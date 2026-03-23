import os
import glob
import argparse
from airllm import AutoModel

DEFAULT_SYSTEM_PROMPT = """You are a senior software architect. 
I am providing you with the source code for several files from my project.
Please analyze how these files interact, identify any architectural flaws, 
and provide a single summary of the entire system."""

def load_model():
    print("Loading model into AirLLM...")
    model = AutoModel.from_pretrained(
        "Qwen/Qwen2.5-Coder-7B-Instruct", 
        compression="4bit",
        delete_original=True,
        # If your combined files are huge, you can increase this up to the model's limit
        # (e.g., Qwen supports up to 32k or 128k depending on the specific version)
        max_seq_len=8192 
    )
    return model

def process_all_files_together(model, input_files, system_prompt):
    combined_content = "Here is the codebase:\n\n"
    
    # 1. Merge all files into one string
    for filepath in input_files:
        if not os.path.isfile(filepath):
            continue
        filename = os.path.basename(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            file_text = f.read()
        
        # Add clear separators so the model knows where files begin and end
        combined_content += f"=== FILE: {filename} ===\n"
        combined_content += file_text + "\n\n"

    # 2. Format the prompt
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": combined_content}
    ]
    prompt_text = model.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    # 3. Tokenize (with truncation in case it's too big)
    inputs = model.tokenizer(
        prompt_text, return_tensors="pt", truncation=True, max_length=8192, padding=False
    )
    
    input_ids = inputs["input_ids"].cuda()
    attention_mask = inputs.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.cuda()

    print(f"Total input size: {input_ids.shape[1]} tokens. Generating response...")

    # 4. Generate the result
    output = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_new_tokens=1024,  # Give it a larger output window for a full project summary
        use_cache=True,
        return_dict_in_generate=True,
        eos_token_id=model.tokenizer.eos_token_id,
        pad_token_id=model.tokenizer.eos_token_id
    )

    # 5. Decode
    input_length = input_ids.shape[1]
    generated_tokens = output.sequences[0][input_length:]
    return model.tokenizer.decode(generated_tokens, skip_special_tokens=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process all files as one context in AirLLM")
    parser.add_argument("--prompt", type=str, default=DEFAULT_SYSTEM_PROMPT)
    args = parser.parse_args()

    os.makedirs("input_data", exist_ok=True)
    os.makedirs("output_data", exist_ok=True)

    input_files = glob.glob("input_data/*")
    
    # Filter out directories and hidden files (like .gitignore)
    valid_files = [f for f in input_files if os.path.isfile(f) and not os.path.basename(f).startswith('.')]

    if not valid_files:
        print("No valid files found in input_data/")
        exit()

    print(f"Found {len(valid_files)} files. Merging them into a single context...")

    # Load model
    model = load_model()

    # Process everything at once
    result = process_all_files_together(model, valid_files, args.prompt)
    
    # Save the single output
    output_filepath = os.path.join("output_data", "project_analysis.txt")
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(result)
        
    print(f"\nSuccess! Saved full project analysis to {output_filepath}")
