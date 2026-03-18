# Local Qwen Coder with Aider CLI on Ubuntu 24.04

This guide covers how to set up and run Qwen2.5-Coder models locally using `llama.cpp` as the backend server and `Aider` as the terminal-based AI coding assistant. This setup is specifically optimized for hardware with limited VRAM (e.g., 4GB RTX A500) and ample system RAM (32GB).

## 1. Prerequisites & Installation

### Install llama.cpp (Backend Server)
Compile `llama.cpp` from source to enable strict memory controls and optimizations required for local inference.
```bash
sudo apt-get update
sudo apt-get install pciutils build-essential cmake curl libcurl4-openssl-dev git-all -y

git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DBUILD_SHARED_LIBS=OFF -DGGML_CUDA=ON
cmake --build build --config Release -j --clean-first --target llama-server
```

### Install Aider (Frontend CLI)
Use the official Aider installation script to set up the CLI without conflicting with Ubuntu's PEP 668 restrictions.
```bash
curl -LsSf https://aider.chat/install.sh | sh
```

---

## 2. Download the Models (GGUF Format)

Create a directory to store your models and download the 4-bit quantized versions (Q4_K_M) directly via `curl`. 

**Option A: Qwen2.5-Coder-3B (Recommended for Speed)**
*Use this for fast, instant responses. Fits entirely in a 4GB GPU.*
```bash
mkdir -p ~/Documents/unsloth/Qwen-3B
cd ~/Documents/unsloth/Qwen-3B
curl -L -o Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf "https://huggingface.co/bartowski/Qwen2.5-Coder-3B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-3B-Instruct-Q4_K_M.gguf"
```

**Option B: Qwen2.5-Coder-7B (Recommended for Intelligence)**
*Use this for complex C++/ROS2 logic. Requires CPU offloading and generates slower.*
```bash
mkdir -p ~/Documents/unsloth/Qwen-7B
cd ~/Documents/unsloth/Qwen-7B
curl -L -o Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf "https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf"
```

---

## 3. Starting the Backend Server (Automated)

Instead of manually typing the long server commands, use the provided bash scripts located in `~/Desktop/Local LLM/`. These scripts handle the exact CPU/GPU thread splitting and VRAM management required for your system.

**For the 3B Model (100% GPU Offload):**
```bash
cd ~/Desktop/Local\ LLM/
./qwen3B_server_setup.sh
```

**For the 7B Model (CPU/GPU Split for 4GB VRAM):**
```bash
cd ~/Desktop/Local\ LLM/
./qwen7B_server_setup.sh
```

*(Note: Leave this terminal window open running the server while you code).*

---

## 4. Run Aider using Architect Mode & No Auto-Commits

Once the server is listening on port 8001, open a **new terminal window**, navigate to your ROS2 workspace, and launch Aider. 

First, ensure Aider routes to your local server instead of OpenAI:
```bash
export OPENAI_API_BASE="http://127.0.0.1:8001/v1"
export OPENAI_API_KEY="sk-dummy-key"
```

**Launch Aider with the `--architect` and `--no-auto-commits` flags:**
```bash
# If using the 3B Server:
aider --model openai/unsloth/Qwen-3B --architect --no-auto-commits

# If using the 7B Server:
aider --model openai/unsloth/Qwen-7B --architect --no-auto-commits
```

### Why use `--architect`?
Smaller local models (under 14B parameters) often fail to format file saves correctly while simultaneously trying to solve complex coding logic. Architect Mode splits the task in two:
1. **The Architect:** Converses with you and plans the code logic naturally.
2. **The Editor:** Aider automatically runs a hidden secondary prompt to format the Architect's plan into strict file edits. 
This prevents the "LLM did not conform to edit format" error and ensures files are actually saved to your disk.

---

## 5. Workflow: "Ask First, Edit Later" (Manual Authorization)

Because `--no-auto-commits` stops Aider from touching Git, you maintain full control. To ensure the AI never modifies a file without your explicit authorization, use Aider's chat modes:

1. **Enter Ask Mode (Read-Only)**  
   Type `/chat-mode ask` in the Aider prompt. In this mode, the AI is physically restricted from writing to your files.
2. **Request the Code**  
   Ask the AI to design your new feature or fix a bug. It will print the proposed code into the terminal for you to review.
3. **Switch to Code Mode (Write Access)**  
   Once you approve of the printed code, type `/chat-mode code` to give the AI file-write permissions again.
4. **Authorize the Edit**  
   Simply type "apply this" or "do it". Aider will remember the conversation and immediately inject the proposed changes into your files.

---

## 6. Basic Aider Commands

Inside the Aider terminal (`>` prompt), use these commands to manage your context:

*   `/add src/my_node.cpp` : Adds a specific file to the AI's memory context. **Always do this before asking it to read or edit a file.**
*   `/drop src/my_node.cpp` : Removes the file from memory to speed up processing and save tokens.
*   `/undo` : Instantly reverts the last code change. *(Note: This command relies on Git. If you use `--no-auto-commits`, you must manually undo changes using `git restore` in a separate terminal).*
*   `/clear` : Wipes the chat history so the AI doesn't get confused by past instructions.