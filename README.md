# Local AI Coding Assistant - Offline Setup for Ubuntu 24.04

Private, fully offline AI coding assistant powered by local Qwen models. No API keys, no cloud,
no data leaving your machine. Uses Aider + llama.cpp for fast, interactive terminal-based pair programming, and AirLLM for offline, large-scale batch processing when maximum model intelligence is required.

---

## Which Workflow Should I Use?

| | llama.cpp (Interactive) | AirLLM (Batch Processing) |
|---|---|---|
| **Model size** | 3B or 7B (GGUF quantized) | 70B+ (full HuggingFace) |
| **Generation speed** | 15–20 tokens/sec | ~4–12 seconds per token |
| **Use Case** | Real-time pair programming via Aider | Offline file analysis & code translation |
| **Best for** | Fast iteration, writing and editing code | Massive architectural summaries, overnight tasks |
| **Interface** | Aider Terminal | Python Batch Scripts |
| **Setup guide** | `llama_cpp_workflow/README.md` | `airllm_workflow/README.md` |

---

## Repository Structure

```
Local_LLM/
├── llama_cpp_workflow/
│   ├── README.md                  ← llama.cpp setup and launch guide
│   ├── qwen3B_server_setup.sh     ← starts llama-server with Qwen-3B on port 8001
│   └── qwen7B_server_setup.sh     ← starts llama-server with Qwen-7B on port 8001
│
├── airllm_workflow/
│   ├── README.md                  ← AirLLM setup and batch execution guide
│   ├── input_data/                ← Place files to be analyzed here
│   ├── output_data/               ← AirLLM saves analysis results here
│   ├── process_batch.py           ← Script: Analyzes files one by one
│   └── process_all.py             ← Script: Analyzes all files as a single context
│
└── README.md                      ← this file
```

---

## Install Aider (One-Time)

Aider is the shared terminal frontend used by the `llama.cpp` workflow. Install it once system-wide:

```bash
curl -LsSf https://aider.chat/install.sh | sh
```

---

## Running Aider

### Step 1 — Start the inference server
Follow the `llama_cpp_workflow/README.md` to start the inference server. Once running on port 8001, **leave that terminal open.**

### Step 2 — Navigate to your project
```bash
cd ~/your/ros2/workspace
```

### Step 3 — Export the API variables
Point Aider at the correct local server port:

```bash
# Point Aider at the local llama.cpp server:
export OPENAI_API_BASE="http://127.0.0.1:8001/v1"
export OPENAI_API_KEY="sk-dummy-key"
```

### Step 4 — Launch Aider
```bash
# llama.cpp 3B (fast):
aider --model openai/unsloth/Qwen-3B --architect --no-auto-commits

# llama.cpp 7B (balanced):
aider --model openai/unsloth/Qwen-7B --architect --no-auto-commits
```

---

## Aider Workflow

### Context Management
Aider only reads files you explicitly add to its context. Always add a file before asking
the AI to read or edit it.

```
/add src/my_node.cpp        → load a file into AI memory
/drop src/my_node.cpp       → remove it to free up context tokens
/clear                      → wipe the entire conversation history
```

### "Ask First, Edit Later" (Recommended)
This is the safest way to work. The AI proposes changes for your review before touching any file.

```
/chat-mode ask    → AI enters read-only mode. It will plan and propose code but never write files.
                    Ask your question or describe the feature you want.

/chat-mode code   → AI gets write access. Type "apply this" or "do it" to authorize the edit.
```

### Flags Explained

| Flag | Effect |
|---|---|
| `--architect` | Splits reasoning and file-editing into two separate AI calls. Prevents format errors on smaller local models. |
| `--no-auto-commits` | Stops Aider from committing every AI edit to Git automatically. You commit manually when ready. |

### Undoing Changes
Because `--no-auto-commits` is enabled, `/undo` inside Aider will not work. To revert an
unwanted AI edit, use Git directly in a separate terminal:

```bash
git restore src/my_node.cpp     # discard changes to a specific file
git diff                        # review all pending AI changes before committing
```

---

## Persistent Environment Variables (Optional)

To avoid exporting the API variables every time you open a new terminal, add your preferred
server's export lines to your `~/.bashrc`:

```bash
echo 'export OPENAI_API_BASE="http://127.0.0.1:8001/v1"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="sk-dummy-key"' >> ~/.bashrc
source ~/.bashrc
```

*(This ensures Aider always connects to your local llama.cpp instance automatically).*

## Acknowledgements

This setup is built entirely on the shoulders of three outstanding open-source projects.
All credit for the underlying inference, tooling, and frontend goes to their respective authors.

### 🦙 llama.cpp
High-performance inference engine for running quantized GGUF models locally on CPU and GPU.
Enables the fast 3B/7B workflow in this repo with full CUDA support and KV cache optimization.

- **Repository:** [https://github.com/ggml-org/llama.cpp](https://github.com/ggml-org/llama.cpp)
- **License:** MIT

### 🌬️ AirLLM
Enables running 70B+ parameter models on a single 4GB GPU without quantization, powering the offline batch-processing and deep architectural analysis workflows in this repo.

- **Repository:** [https://github.com/lyogavin/airllm](https://github.com/lyogavin/airllm)
- **Author:** Gavin Li
- **License:** Apache 2.0
- **Citation:**
```bibtex
@software{airllm2023,
  author  = {Gavin Li},
  title   = {AirLLM: scaling large language models on low-end commodity computers},
  url     = {https://github.com/lyogavin/airllm/},
  version = {0.0},
  year    = {2023},
}
```

### 🤖 Aider
Open-source AI pair programmer that runs in the terminal. Handles Git-aware file editing,
repo mapping, and the Architect/Editor workflow that makes local models reliable for
real-world coding tasks.

- **Repository:** [https://github.com/Aider-AI/aider](https://github.com/Aider-AI/aider)
- **Author:** Paul Gauthier and contributors
- **License:** Apache 2.0
- **Website:** [https://aider.chat](https://aider.chat)
