/home/andrea/Documents/GitHub/llama.cpp/llama-server \
    --model /home/andrea/Documents/unsloth/Qwen-7B/Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf \
    --alias "unsloth/Qwen-7B" \
    --n-gpu-layers 10 \
    --temp 0.6 \
    --top-p 0.95 \
    --top-k 20 \
    --port 8001 \
    --kv-unified \
    --cache-type-k q8_0 --cache-type-v q8_0 \
    --flash-attn on --fit on \
    --ctx-size 32768 \
    --batch-size 512 \
    --ubatch-size 256 \
    -t 16

