# Local Qwen Coder with Aider CLI on Ubuntu 24.04

Fast local AI coding assistant using quantized GGUF models via `llama.cpp`. Optimized for
4GB VRAM (RTX A500) + 32GB RAM. Runs entirely offline on port **8001**.

> **Use this workflow when:** You need fast, interactive code completions (3–15 tokens/sec).

---

## 1. Install llama.cpp

```bash
sudo apt-get update
sudo apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev git-all -y

git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build build --config Release -j --clean-first --target llama-server
```

---

## 2. Download the Models

**Option A: Qwen2.5-Coder-3B — Speed (fits 100% in 4GB GPU)**
```bash
mkdir -p ~/Documents/unsloth/Qwen-3B && cd ~/Documents/unsloth/Qwen-3B
curl -L -o Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf \
  "https://huggingface.co/bartowski/Qwen2.5-Coder-3B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf"
```

**Option B: Qwen2.5-Coder-7B — Intelligence (CPU/GPU split, slower)**
```bash
mkdir -p ~/Documents/unsloth/Qwen-7B && cd ~/Documents/unsloth/Qwen-7B
curl -L -o Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf \
  "https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"
```

---

## 3. Start the Server

Use the provided scripts. Leave this terminal open while coding.

```bash
cd ~/Desktop/Local_LLM/

./qwen3B_server_setup.sh   # 3B model — fast
./qwen7B_server_setup.sh   # 7B model — smarter
```

Wait until the terminal prints:
```
HTTP server listening on 127.0.0.1:8001
```

---

## 4. Connect Aider

Open a new terminal, navigate to your workspace, and run:

```bash
export OPENAI_API_BASE="http://127.0.0.1:8001/v1"
export OPENAI_API_KEY="sk-dummy-key"

aider --model openai/unsloth/Qwen-3B --architect --no-auto-commits
# or
aider --model openai/unsloth/Qwen-7B --architect --no-auto-commits
```