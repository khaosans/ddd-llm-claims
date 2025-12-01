#!/bin/bash
# Check status of all services

cd "$(dirname "$0")"

echo "🔍 DDD Claims Processing System - Service Status"
echo "================================================"
echo ""

# Check Python
echo "🐍 Python:"
if command -v python3 &> /dev/null; then
    echo "   ✅ $(python3 --version)"
else
    echo "   ❌ Not found"
fi

# Check Virtual Environment
echo ""
echo "📦 Virtual Environment:"
if [ -d "venv" ]; then
    echo "   ✅ Found at: $(pwd)/venv"
    if [ -f "venv/bin/activate" ]; then
        echo "   ✅ Activation script exists"
    fi
else
    echo "   ⚠️  Not found (optional, but recommended)"
fi

# Check Dependencies
echo ""
echo "📚 Dependencies:"
if [ -d "venv" ]; then
    source venv/bin/activate
    if python3 -c "import streamlit" 2>/dev/null; then
        echo "   ✅ Streamlit installed"
    else
        echo "   ❌ Streamlit not installed"
    fi
    if python3 -c "import ollama" 2>/dev/null; then
        echo "   ✅ Ollama client installed"
    else
        echo "   ⚠️  Ollama client not installed (optional)"
    fi
else
    echo "   ⚠️  Cannot check (venv not found)"
fi

# Check Ollama Service
echo ""
echo "🤖 Ollama Service:"
if command -v ollama &> /dev/null; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "   ✅ Running at http://localhost:11434"
        MODELS=$(ollama list 2>/dev/null | grep -v "^NAME" | awk '{print $1}' | head -5)
        if [ ! -z "$MODELS" ]; then
            echo "   ✅ Available models:"
            echo "$MODELS" | while read model; do
                echo "      - $model"
            done
        else
            echo "   ⚠️  No models installed"
        fi
    else
        echo "   ⚠️  Not running (but installed)"
        echo "      Start with: ollama serve"
    fi
else
    echo "   ⚠️  Not installed (optional - system uses Mock mode)"
fi

# Check Streamlit
echo ""
echo "🌐 Streamlit Dashboard:"
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "   ✅ Running at http://localhost:8501"
    echo "   ✅ Accessible"
else
    echo "   ⚠️  Not running"
    echo "      Start with: streamlit run streamlit_app.py"
fi

# Check Data Directories
echo ""
echo "💾 Data Directories:"
if [ -d "data" ]; then
    echo "   ✅ data/ exists"
    if [ -d "data/chroma_db" ]; then
        echo "   ✅ data/chroma_db/ exists"
    else
        echo "   ⚠️  data/chroma_db/ missing (will be created automatically)"
    fi
else
    echo "   ⚠️  data/ missing (will be created automatically)"
fi

# Check UI Service
echo ""
echo "🔧 UI Service:"
if [ -d "venv" ]; then
    source venv/bin/activate
    if python3 -c "from src.ui.services import get_service; print('OK')" 2>/dev/null | grep -q "OK"; then
        echo "   ✅ UI Service can be imported"
    else
        echo "   ❌ UI Service import failed"
    fi
else
    echo "   ⚠️  Cannot check (venv not found)"
fi

echo ""
echo "================================================"
echo "📋 Summary:"
echo ""
if curl -s http://localhost:8501 > /dev/null 2>&1 && curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ All services are running!"
    echo ""
    echo "🌐 Access the dashboard at: http://localhost:8501"
elif curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Streamlit is running (Ollama optional)"
    echo ""
    echo "🌐 Access the dashboard at: http://localhost:8501"
    echo "⚠️  Ollama not running - using Mock mode"
else
    echo "⚠️  Some services need to be started"
    echo ""
    echo "🚀 To start everything:"
    echo "   ./start_services.sh"
    echo ""
    echo "   Or manually:"
    echo "   source venv/bin/activate"
    echo "   streamlit run streamlit_app.py"
fi


