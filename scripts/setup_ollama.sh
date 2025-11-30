#!/bin/bash

# Setup script for Ollama and local models
# This script helps set up Ollama for running local LLMs/SLMs

set -e

echo "🚀 Setting up Ollama for DDD Claims Processing System"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed."
    echo ""
    echo "Please install Ollama first:"
    echo "  macOS:   brew install ollama"
    echo "  Linux:   curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Windows: Download from https://ollama.com/download"
    echo ""
    exit 1
fi

echo "✅ Ollama is installed"
echo ""

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "⚠️  Ollama service is not running. Starting it..."
    ollama serve &
    sleep 3
fi

echo "✅ Ollama service is running"
echo ""

# Recommended models for this system
MODELS=(
    "llama3.2"      # Good balance of quality and speed
    "llama3.2:3b"    # Smaller, faster model (SLM)
    "mistral:7b"     # Alternative SLM option
    "phi3:mini"      # Very small, fast model (SLM)
)

echo "📥 Downloading recommended models..."
echo ""

for model in "${MODELS[@]}"; do
    echo "Downloading $model..."
    ollama pull "$model" || echo "⚠️  Failed to download $model (this is okay)"
    echo ""
done

echo "✅ Model setup complete!"
echo ""
echo "📋 Available models:"
ollama list
echo ""
echo "🎯 Next steps:"
echo "  1. Copy .env.example to .env"
echo "  2. Update MODEL_PROVIDER=ollama in .env"
echo "  3. Set OLLAMA_MODEL to one of the downloaded models"
echo "  4. Run the application!"
echo ""
echo "💡 Tip: Start with 'llama3.2:3b' for faster testing,"
echo "   then switch to 'llama3.2' for better quality."

