import os
import glob
import argparse
from airllm import AutoModel

# Default prompt if the user doesn't provide one
DEFAULT_SYSTEM_PROMPT = """You are a senior developer. 
Read the following file and provide a summary of the core logic, 
followed by a list of any functions defined within it. 
Keep it concise."""

def load_model():
    print("Loading model into AirLLM...")
    model = AutoModel.from_pretrained(
        "Qwen/Qwen2.5-Coder-7B-Instruct",  # Swap to meta-llama/Meta-Llama-3-70B-Instruct later
        compression="4bit",
        delete_original=True,
        max_seq_len=8192
    )
    return model

def process_file(model, filepath, system_prompt):
    # Read the file content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Format the prompt using the chat template
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the file content:\n\n{content}"}
    ]
    prompt_text = model.tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    # Tokenize
    inputs = model.tokenizer(
        prompt_text, return_tensors="pt", truncation=True, max_length=8192, padding=False
    )
    
    input_ids = inputs["input_ids"].cuda()
    attention_mask = inputs.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.cuda()

    # Generate the result
    output = model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_new_tokens=512,  # Adjust if you expect longer outputs
        use_cache=True,
        return_dict_in_generate=True,
        eos_token_id=model.tokenizer.eos_token_id,
        pad_token_id=model.tokenizer.eos_token_id
    )

    # Decode and remove prompt tokens
    input_length = input_ids.shape[1]
    generated_tokens = output.sequences[0][input_length:]
    return model.tokenizer.decode(generated_tokens, skip_special_tokens=True)


if __name__ == "__main__":
    # Setup command line arguments
    parser = argparse.ArgumentParser(description="Run batch processing with AirLLM")
    parser.add_argument(
        "--prompt", 
        type=str, 
        help="The system prompt/instructions to apply to all files.", 
        default=DEFAULT_SYSTEM_PROMPT
    )
    args = parser.parse_args()

    # Ensure directories exist
    os.makedirs("input_data", exist_ok=True)
    os.makedirs("output_data", exist_ok=True)

    # Get all files in the input directory
    input_files = glob.glob("input_data/*")
    
    if not input_files:
        print("No files found in input_data/. Please add some files and try again.")
        exit()

    print(f"Found {len(input_files)} files to process.")
    print(f"Using System Prompt:\n\"{args.prompt}\"\n")

    # Load the model only once
    model = load_model()

    for filepath in input_files:
        # Ignore subdirectories, process files only
        if not os.path.isfile(filepath):
            continue
            
        filename = os.path.basename(filepath)
        output_filepath = os.path.join("output_data", f"processed_{filename}.txt")
        
        # Skip if already processed (allows you to pause and resume)
        if os.path.exists(output_filepath):
            print(f"Skipping {filename}, already processed.")
            continue
            
        print(f"\nProcessing {filename}...")
        
        # Process the file
        result = process_file(model, filepath, args.prompt)
        
        # Save the result
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(result)
            
        print(f"Saved result to {output_filepath}")

    print("\nBatch processing complete!")
