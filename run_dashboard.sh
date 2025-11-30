#!/bin/bash
# Run Streamlit Dashboard - Local Demo

echo "🚀 Starting DDD Claims Processing System Dashboard"
echo ""
echo "📋 Prerequisites Check:"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python found: $(python3 --version)"
else
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi

# Check Ollama
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is running"
        MODELS=$(ollama list 2>/dev/null | grep -v "^NAME" | awk '{print $1}' | head -3)
        if [ ! -z "$MODELS" ]; then
            echo "✅ Models available: $(echo $MODELS | tr '\n' ' ')"
        else
            echo "⚠️  No models installed. Run: ollama pull llama3.2"
        fi
    else
        echo "⚠️  Ollama not running. Start with: ollama serve"
        echo "   Dashboard will use Mock mode (works without Ollama)"
    fi
else
    echo "⚠️  Ollama not found. Install from https://ollama.com"
    echo "   Dashboard will use Mock mode (works without Ollama)"
fi

# Check dependencies
echo ""
echo "📦 Checking dependencies..."
if python3 -c "import streamlit" 2>/dev/null; then
    echo "✅ Streamlit installed"
else
    echo "⚠️  Streamlit not found. Installing..."
    pip3 install streamlit
fi

# Ensure data directories
mkdir -p data/chroma_db

echo ""
echo "🌐 Starting dashboard..."
echo "   Dashboard will open in your browser"
echo "   Press Ctrl+C to stop"
echo ""

streamlit run streamlit_app.py

