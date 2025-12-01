#!/bin/bash
# Start all services for DDD Claims Processing System

cd "$(dirname "$0")"

echo "🚀 Starting DDD Claims Processing System Services"
echo "=================================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.10+"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Using system Python."
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
fi

# Check Ollama
echo ""
echo "📦 Checking Ollama..."
if command -v ollama &> /dev/null; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama is running"
        MODELS=$(ollama list 2>/dev/null | grep -v "^NAME" | awk '{print $1}' | head -3)
        if [ ! -z "$MODELS" ]; then
            echo "   Available models: $(echo $MODELS | tr '\n' ' ')"
        else
            echo "⚠️  No models installed. Run: ollama pull llama3.2"
        fi
    else
        echo "⚠️  Ollama not running. Starting Ollama..."
        # Try to start Ollama in background (macOS)
        if [ -d "/Applications/Ollama.app" ]; then
            open -a Ollama 2>/dev/null || ollama serve &
            sleep 2
            if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
                echo "✅ Ollama started"
            else
                echo "⚠️  Could not start Ollama. Please start manually: ollama serve"
            fi
        else
            echo "⚠️  Ollama not found. Install from https://ollama.com"
            echo "   System will use Mock mode (works without Ollama)"
        fi
    fi
else
    echo "⚠️  Ollama not installed. Install from https://ollama.com"
    echo "   System will use Mock mode (works without Ollama)"
fi

# Check Streamlit
echo ""
echo "🌐 Checking Streamlit..."
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Streamlit is already running at http://localhost:8501"
    echo "   Open in browser: http://localhost:8501"
else
    echo "🚀 Starting Streamlit..."
    echo "   Dashboard will open in your browser"
    echo "   Press Ctrl+C to stop"
    echo ""
    
    # Ensure data directories exist
    mkdir -p data/chroma_db
    
    # Start Streamlit
    streamlit run streamlit_app.py
fi

echo ""
echo "=================================================="
echo "✅ All services ready!"
echo ""
echo "📋 Service Status:"
echo "   - Streamlit: http://localhost:8501"
echo "   - Ollama: http://localhost:11434"
echo ""
echo "💡 To stop services:"
echo "   - Streamlit: Press Ctrl+C or close terminal"
echo "   - Ollama: Stop from Ollama app or: pkill ollama"


