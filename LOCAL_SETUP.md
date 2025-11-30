# Local Setup Guide - Open Source Models

This guide ensures you can run the system completely locally using open-source models.

## Quick Start (Local Only)

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### 2. Start Ollama

```bash
ollama serve
```

### 3. Download a Model

```bash
# Recommended for this demo
ollama pull llama3.2

# Or try other models
ollama pull mistral:7b
ollama pull phi3:mini
```

### 4. Run Streamlit Dashboard

```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run dashboard
streamlit run streamlit_app.py
```

The dashboard will automatically detect Ollama and use it by default!

## Local-First Configuration

The system is configured to prioritize local options:

1. **Ollama** (default) - Local, open-source models
2. **Mock** (fallback) - Works without any models
3. **OpenAI/Anthropic** (optional) - Cloud providers

## No API Keys Required

For local demo, you don't need any API keys:
- ✅ Ollama runs locally
- ✅ No internet required (after model download)
- ✅ No API costs
- ✅ Complete privacy

## Recommended Models

### For Fact Extraction (Intake Agent)
- `llama3.2` - Good balance of quality and speed
- `mistral:7b` - Fast and efficient
- `phi3:mini` - Very fast, smaller model

### For Policy Validation (Policy Agent)
- `llama3.2` - Good reasoning capabilities
- `mistral:7b` - Fast validation

### For Triage (Routing Agent)
- `llama3.2` - Good decision making
- `phi3:mini` - Fast routing decisions

## Model Selection in UI

The Streamlit dashboard will:
1. Auto-detect if Ollama is running
2. Show available models
3. Default to Ollama if available
4. Fall back to Mock mode if Ollama unavailable

## Troubleshooting

### Ollama Not Detected

1. **Check Ollama is running:**
   ```bash
   ollama serve
   ```

2. **Verify models are installed:**
   ```bash
   ollama list
   ```

3. **Test Ollama connection:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Model Not Found

If a model isn't found, download it:
```bash
ollama pull llama3.2
```

### Performance Issues

- Use smaller models for faster processing (`phi3:mini`, `mistral:7b`)
- Reduce temperature for faster responses
- Process claims one at a time

## Environment Variables

Set these for automatic configuration:

```bash
export MODEL_PROVIDER=ollama
export OLLAMA_MODEL=llama3.2
export OLLAMA_BASE_URL=http://localhost:11434
```

## Database Location

All data is stored locally:
- **SQLite**: `data/claims.db`
- **ChromaDB**: `data/chroma_db/`

No cloud services required!

## Complete Local Stack

- ✅ **Ollama** - Local LLM inference
- ✅ **SQLite** - Local database
- ✅ **ChromaDB** - Local vector database
- ✅ **Streamlit** - Local web UI
- ✅ **Python** - All processing local

Everything runs on your machine - perfect for demos and education!

