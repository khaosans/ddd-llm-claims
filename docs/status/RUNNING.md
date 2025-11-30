# Running the Application

This guide helps you verify that the application is set up correctly and can run.

## Quick Verification

Run the test script to verify everything is working:

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Run test
python3 test_run.py
```

This will verify:
- ✅ All imports work correctly
- ✅ Model providers can be created
- ✅ Basic system setup works

## Running the Demo

### Option 1: Interactive Command Line Demo

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Run demo
python3 demo.py

# Or use convenience script
./run_demo.sh
```

The demo will:
- Guide you through the complete workflow
- Show step-by-step processing
- Demonstrate human-in-the-loop review
- Work with Ollama (if available) or Mock mode (if not)

### Option 2: Streamlit Web Dashboard

```bash
# Activate virtual environment (if using one)
source venv/bin/activate

# Run dashboard
streamlit run streamlit_app.py

# Or use convenience script
./run_streamlit.sh
```

The dashboard will:
- Open in your browser (usually http://localhost:8501)
- Provide interactive UI for processing claims
- Show analytics and visualizations
- Work with Ollama (if available) or Mock mode (if not)

## Virtual Environment Setup

If you haven't set up a virtual environment yet:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

Or use the setup script:

```bash
python3 scripts/setup.py
```

## Troubleshooting

### Import Errors

If you get import errors:
1. Make sure you're in the project root directory
2. Activate the virtual environment if using one
3. Verify dependencies are installed: `pip list`

### Ollama Not Available

The application works without Ollama using Mock mode. You'll see:
- "⚠️ Ollama not detected. Using Mock mode."

To use Ollama:
1. Install Ollama: https://ollama.com
2. Start Ollama: `ollama serve`
3. Download a model: `ollama pull llama3.2`

### Port Already in Use

If Streamlit says the port is in use:
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Virtual Environment Issues

If you have issues with the virtual environment:
- Make sure Python 3.10+ is installed
- Try recreating: `rm -rf venv && python3 -m venv venv`
- Or use system Python (not recommended)

## What to Expect

### Demo Mode (Mock Providers)

When running without Ollama, the system uses mock providers:
- ✅ All functionality works
- ✅ Claims are processed
- ✅ Workflow is demonstrated
- ⚠️ Responses are simulated (not real LLM)

### Ollama Mode

When Ollama is available:
- ✅ Real LLM processing
- ✅ More realistic responses
- ✅ Better demonstration of AI capabilities
- ⚠️ Requires Ollama running and models downloaded

## Next Steps

Once the application is running:

1. **Try the Demo**: Run `python3 demo.py` to see the workflow
2. **Explore the Dashboard**: Run `streamlit run streamlit_app.py` for the web UI
3. **Read Documentation**: See README.md for more information
4. **Check Examples**: Look in `examples/` directory for code samples

## Verification Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created (optional but recommended)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test script passes (`python3 test_run.py`)
- [ ] Demo runs (`python3 demo.py`)
- [ ] Streamlit app starts (`streamlit run streamlit_app.py`)
- [ ] (Optional) Ollama installed and running
- [ ] (Optional) Model downloaded (`ollama pull llama3.2`)

## Getting Help

- See `README.md` for overview
- See `QUICK_START.md` for quick setup
- See `LOCAL_SETUP.md` for Ollama setup
- See `docs/TECHNICAL.md` for technical details

