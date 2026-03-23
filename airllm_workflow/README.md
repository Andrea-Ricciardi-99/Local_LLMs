# AirLLM Offline Batch Processing Workflow

AirLLM enables running massive HuggingFace models (14B, 32B, 70B+) on a single 4GB GPU by streaming model layers from your SSD to VRAM one at a time during inference. 

Because this layer-swapping technique is slow (~4 to 12 seconds per token depending on model size), **AirLLM is not suitable for interactive chat or AI pair-programming tools like Aider.** 

> Instead, this repository provides an **Offline Batch Processing Workflow**. It is designed for asynchronous, unattended tasks where you need flagship-level intelligence (like a 70B model) to analyze large amounts of data, and you can afford to let the script run in the background for several hours or overnight.

***

## 1. Setup & Installation

### Create the Virtual Environment
Ubuntu 24.04 enforces PEP 668, so all dependencies must be installed inside a venv.
Navigate to the `airllm_workflow/` folder and run:

```bash
python3 -m venv airllm_env
source airllm_env/bin/activate
```

### Install Dependencies
Pin the `transformers` and `optimum` versions to avoid a known `BetterTransformer` breakage introduced in `transformers>=4.49`:

```bash
pip install \
  "transformers==4.42.4" \
  "optimum==1.23.3" \
  "torch==2.3.0" \
  "accelerate>=0.20.3" \
  airllm sentencepiece bitsandbytes \
  einops tiktoken transformers_stream_generator
```

***

## 2. Directory Structure

This workflow uses a simple input/output directory structure:

```text
airllm_workflow/
├── airllm_env/             # Python virtual environment
├── input_data/             # 📥 Drop all files to be analyzed here
├── output_data/            # 📤 AirLLM will save the AI responses here
├── process_batch.py        # Script 1: Analyzes files one by one
├── process_all.py          # Script 2: Analyzes all files together as one context
└── README.md
```

*Note: The `input_data` and `output_data` folders contain `.gitignore` files to ensure they are tracked by Git without uploading your private datasets.*

***

## 3. Model Download & Sharding

Before running any scripts, note that AirLLM requires heavy disk usage. On the **first run**, AirLLM will automatically:
1. Download the full HuggingFace model to `~/.cache/huggingface/`.
2. Split the model into individual layer shard files.

> ⚠️ **Disk Space Warning:** A 70B model requires roughly **140GB** of SSD space. A 7B model requires ~15GB. 

To save space, both scripts include `delete_original=True`, which automatically deletes the original un-sharded weights after the sharding process finishes. The sharding process can take 15–45 minutes depending on the model size and your CPU speed.

***

## 4. How to Use

Place the text, code, or log files you want to analyze inside the `input_data/` folder. Choose one of the two execution scripts below based on your needs.

### Option A: Process Files Individually (`process_batch.py`)
Use this script when you want a separate analysis for every file in the folder. The script will read `file1.py`, generate a summary, save it to `output_data/processed_file1.py.txt`, and then move on to the next file.

**Default execution:**
```bash
python process_batch.py
```

**Custom instruction:**
Pass a specific task using the `--prompt` argument:
```bash
python process_batch.py --prompt "Translate the docstrings in this code to Italian."
```

### Option B: Process All Files as One Context (`process_all.py`)
Use this script when you need the model to understand the relationship between multiple files. It concatenates all files in `input_data/` into one massive text block, sends it to the model, and generates a single `project_analysis.txt` output.

```bash
python process_all.py --prompt "Analyze how these files interact and identify any architectural flaws."
```

***

## 5. ⚠️ Critical Limitations & Warnings

To use this workflow successfully, you must understand the physical limitations of your 4GB GPU:

### 1. The Context Window VRAM Limit (OOM Errors)
While AirLLM dynamically swaps the *model weights* to keep VRAM low, **the Context Window (your input files) stays permanently inside the VRAM.**
* If you use `process_all.py` and merge 50 large files, you will exceed the 8,192 token limit set in the script.
* If you increase the `max_seq_len` to something massive (e.g., 32,000), the context window itself will consume more than 4GB of VRAM and **your GPU will crash** with a Tensor Size Mismatch or CUDA Out of Memory error.
* **Best Practice:** Keep input contexts under 8,000 tokens per run.

### 2. Extreme Generation Times
AirLLM operates at approximately **1 to 4 seconds per token** depending on the model.
* A 500-word response from a 70B model will take **nearly an hour** to generate.
* The script features an auto-resume function. If you stop the script, it will skip already-completed files in the `output_data/` folder when you restart it. 

### 3. Do Not Use Aider
Because of the generation times mentioned above, API-based chat servers and interactive tools like Aider will experience severe timeouts and formatting failures. **Stick to the offline batch scripts.** If you need interactive coding, use `Ollama` with a quantized 7B model instead.