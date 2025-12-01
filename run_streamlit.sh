#!/bin/bash
# Run Streamlit Dashboard - Activates venv and runs streamlit

cd "$(dirname "$0")"

# Check if venv exists
if [ -d "venv" ]; then
    echo "✅ Using virtual environment"
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found"
    echo "   Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    echo "   Or run: python3 scripts/setup.py"
    echo ""
    echo "Continuing with system Python..."
fi

# Run streamlit
streamlit run streamlit_app.py


