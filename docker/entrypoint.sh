#!/bin/bash
set -e

echo "🚀 Starting Luymas AI..."

# Start Ollama in the background
echo "📦 Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
for i in $(seq 1 30); do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️ Ollama startup timeout, continuing anyway..."
    fi
    sleep 2
done

# Check for required models
echo "🔍 Checking models..."
REQUIRED_MODELS=("qwen2.5-coder:7b" "deepseek-r1:8b")
for model in "${REQUIRED_MODELS[@]}"; do
    if ! ollama list 2>/dev/null | grep -q "$model"; then
        echo "📥 Pulling model: $model (this may take a while)..."
        ollama pull "$model" &
    fi
done

# Start the main application
echo "🎯 Starting Luymas AI application..."
exec "$@"
