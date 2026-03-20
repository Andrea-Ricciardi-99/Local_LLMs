# AirLLM Server for Large Model Inference on Low VRAM

AirLLM enables running large HuggingFace models (14B, 32B, 70B+) on a single 4GB GPU by streaming
model layers from disk to VRAM one at a time during inference. This trades generation speed for
dramatically higher model intelligence, ideal for complex architectural tasks.

> **Use this workflow when:** You need the smartest possible answer and can afford to wait (~1–3 tokens/sec).

---

## 1. Setup

### Create the Virtual Environment
Ubuntu 24.04 enforces PEP 668, so all dependencies must be installed inside a venv.
Navigate to the `airllm_workflow/` folder and run:

```bash
python3 -m venv airllm_env
source airllm_env/bin/activate
```

### Install Dependencies
Pin the `transformers` and `optimum` versions to avoid a known `BetterTransformer` breakage
introduced in `transformers>=4.49`:

```bash
pip install \
  "transformers==4.48.3" \
  "optimum==1.23.3" \
  "torch==2.3.0" \
  "accelerate>=0.20.3" \
  airllm fastapi uvicorn \
  sentencepiece bitsandbytes scipy \
  einops tiktoken transformers_stream_generator
```

---

## 2. Model Download & Sharding

On the **first run**, AirLLM will automatically:
1. Download the full HuggingFace model to `~/.cache/huggingface/` (~28GB for 14B).
2. Split it into individual layer shard files (~28GB additional).

> ⚠️ **Disk space:** The 14B model requires ~56GB total on first run.
> Add `delete_original=True` in `airllm_server.py` to halve this by deleting the original
> after sharding. All subsequent runs load from shards only.

To redirect where shards are saved (e.g., to keep models organized):
```python
model = AutoModel.from_pretrained(
    "Qwen/Qwen2.5-Coder-14B-Instruct",
    compression="4bit",
    layer_shards_saving_path="/home/andrea/Documents/unsloth/AirLLM-14B",
    delete_original=True
)
```

---

## 3. Starting the Server

Use the provided launch script. It automatically activates the local venv and starts the
FastAPI server on port **8002** (intentionally different from llama.cpp's port 8001 to avoid
conflicts):

```bash
./airllm_server_setup.sh
```

Wait until you see:
```
INFO: Uvicorn running on http://127.0.0.1:8002 (Press CTRL+C to quit)
```

> **Note:** The first run takes 15–30 minutes to download and shard the model.
> Subsequent runs start in under 60 seconds as layers are already on disk.

---

## 4. Connect Aider

Once the server is running, open a **new terminal**, navigate to your ROS2 workspace, and
export the API variables to point to the AirLLM server on port 8002:

```bash
export OPENAI_API_BASE="http://127.0.0.1:8002/v1"
export OPENAI_API_KEY="sk-dummy-key"

aider --model openai/Qwen2.5-Coder-14B --architect --no-auto-commits
```