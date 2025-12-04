#!/bin/bash

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

source venv/bin/activate

export HF_TOKEN="$HF_TOKEN"  # From .env if set

echo "Starting Chroma..."
chroma run --host 127.0.0.1 --port 8003 --path ./data/chroma &
CHROMA_PID=$!

echo "Starting vLLM..."
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.2-3B-Instruct \
  --trust-remote-code \
  --dtype half \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.8 \
  --enable-chunked-prefill \
  --tensor-parallel-size 1 \
  --port 8000 &
VLLM_PID=$!

# Health check function
check_vllm_status() {
    curl -s http://localhost:8000/health > /dev/null 2>&1
    return $?
}

echo "Waiting for vLLM server to be ready (this may take 5-6 minutes on first run)..."
server_ready=false
attempts=0
max_attempts=70

while [ "$server_ready" = false ] && [ $attempts -lt $max_attempts ]; do
    if check_vllm_status; then
        echo "✅ vLLM server is ready!"
        server_ready=true
    else
        attempts=$((attempts + 1))
        echo "⏳ vLLM not ready yet... (attempt $attempts/$max_attempts)"
        sleep 5
    fi
done

if [ "$server_ready" = false ]; then
    echo "❌ vLLM server failed to start after 5 minutes. Exiting."
    kill $CHROMA_PID $VLLM_PID
    exit 1
fi

echo "Starting FastAPI..."
uvicorn src.apps:app --host 0.0.0.0 --port 8001 &
FASTAPI_PID=$!

sleep 2

echo "Starting ngrok..."
ngrok config add-authtoken "$NGROK_AUTHTOKEN"
ngrok http 8001

trap "kill $CHROMA_PID $VLLM_PID $FASTAPI_PID" EXIT


echo "Starting ngrok..."
ngrok config add-authtoken $NGROK_AUTHTOKEN
ngrok http 8001

trap "kill $CHROMA_PID $VLLM_PID $FASTAPI_PID" EXIT
