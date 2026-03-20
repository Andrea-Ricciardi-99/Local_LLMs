from fastapi import FastAPI
from pydantic import BaseModel
from airllm import AutoModel
import uvicorn, torch

app = FastAPI()
model = AutoModel.from_pretrained(
    "Qwen/Qwen2.5-Coder-14B-Instruct",
    compression="4bit"   # remove for full precision, uses more disk I/O
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[Message]
    max_tokens: int = 512

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest):
    # Extract the last user message
    prompt = next(
        (m.content for m in reversed(req.messages) if m.role == "user"),
        ""
    )
    input_tokens = model.tokenizer(
        [prompt],
        return_tensors="pt",
        truncation=True,
        max_length=2048,
        padding=False
    )
    output = model.generate(
        input_tokens["input_ids"].cuda(),
        max_new_tokens=req.max_tokens,
        use_cache=True,
        return_dict_in_generate=True
    )
    text = model.tokenizer.decode(
        output.sequences[0],
        skip_special_tokens=True
    )
    return {
        "choices": [{
            "message": {"role": "assistant", "content": text},
            "finish_reason": "stop"
        }],
        "model": req.model
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8002)

