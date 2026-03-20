#!/bin/bash

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate the venv that lives in the same folder as this script
source "$SCRIPT_DIR/airllm_env/bin/activate"

echo "Downloading and sharding Qwen2.5-Coder-14B on first run..."
echo "Server will be available at http://127.0.0.1:8002"

python3 "$SCRIPT_DIR/airllm_server.py"