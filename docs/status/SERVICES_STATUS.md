# Services Status & Management

## ✅ Current Status

All services are **RUNNING** and ready to use!

### Service URLs

- **Streamlit Dashboard**: http://localhost:8501 ✅
- **Ollama API**: http://localhost:11434 ✅

### Available Models

- `mistral:latest` (4.4 GB)
- `llama3.2:3b` (2.0 GB)
- `nomic-embed-text:latest` (274 MB)

## Quick Commands

### Check Service Status
```bash
./check_services.sh
```

### Start All Services
```bash
./start_services.sh
```

### Start Streamlit Only
```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

### Start Ollama (if not running)
```bash
ollama serve
# Or on macOS:
open -a Ollama
```

## Service Management

### Streamlit Dashboard

**Status**: ✅ Running at http://localhost:8501

**Start**:
```bash
source venv/bin/activate
streamlit run streamlit_app.py
```

**Stop**: Press `Ctrl+C` in the terminal running Streamlit

**Restart**: Stop and start again

### Ollama Service

**Status**: ✅ Running at http://localhost:11434

**Start**:
```bash
ollama serve
# Or on macOS:
open -a Ollama
```

**Stop**:
```bash
pkill ollama
# Or quit from Ollama app
```

**Check Models**:
```bash
ollama list
```

**Download Model**:
```bash
ollama pull llama3.2
```

## Verification

Run the status check:
```bash
./check_services.sh
```

Or test manually:
```bash
# Check Streamlit
curl http://localhost:8501

# Check Ollama
curl http://localhost:11434/api/tags
```

## Troubleshooting

### Streamlit Not Starting

1. Check if port 8501 is in use:
   ```bash
   lsof -i :8501
   ```

2. Use a different port:
   ```bash
   streamlit run streamlit_app.py --server.port 8502
   ```

3. Check virtual environment:
   ```bash
   source venv/bin/activate
   pip list | grep streamlit
   ```

### Ollama Not Starting

1. Check if Ollama is installed:
   ```bash
   which ollama
   ```

2. Check if port 11434 is in use:
   ```bash
   lsof -i :11434
   ```

3. Install Ollama:
   - macOS: `brew install ollama`
   - Linux: `curl -fsSL https://ollama.com/install.sh | sh`
   - Windows: Download from https://ollama.com

### Services Not Working Together

1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate
   ```

2. Verify dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Check Python path:
   ```bash
   python3 -c "import sys; print(sys.path)"
   ```

## Next Steps

1. **Open Dashboard**: http://localhost:8501
2. **Process a Claim**: Go to "Process Claim" page
3. **View Results**: Check "Claims List" page
4. **Review Queue**: Check "Human Review" page

## Notes

- **Mock Mode**: System works without Ollama using mock providers
- **Data Persistence**: Claims and policies stored in SQLite database (`data/claims.db`) - **persists across sessions**
- **Vector Stores**: ChromaDB vector stores initialized for semantic search (`data/chroma_db/`)
- **Port Conflicts**: Use different ports if needed
- **Virtual Environment**: Always activate before running commands

