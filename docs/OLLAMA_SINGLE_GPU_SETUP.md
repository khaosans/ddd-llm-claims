# Ollama Single GPU Setup Guide

This guide ensures the system works optimally with Ollama on a single GPU setup.

## Quick Verification

Run the setup check script:
```bash
python3 scripts/check_ollama_setup.py
```

This will verify:
- ✅ Ollama service is running
- ✅ Models are available
- ✅ Best model for single GPU is recommended

## Automatic Model Detection

The system now **automatically detects** available Ollama models and selects the best one for single GPU:

1. **Priority Order** (smallest first):
   - `llama3.2:3b` (2GB) - **Recommended for single GPU**
   - `mistral:latest` (4.4GB) - Good balance
   - `phi3:mini` - Very small
   - `mistral:7b` - Alternative
   - `llama3.2` - Larger but better quality

2. **Auto-Selection**: The system automatically uses the first available model in priority order

3. **Fallback**: If no preferred model is found, uses the first available model

## Current Setup

Based on your system, the following models are detected:
- ✅ `llama3.2:3b` (2GB) - **Automatically selected**
- ✅ `mistral:latest` (4.4GB) - Available as alternative
- ✅ `nomic-embed-text:latest` - For embeddings (not used for claims processing)

## Configuration

### Default Configuration (`config.yaml`)
```yaml
ollama:
  default_model: "llama3.2:3b"  # Optimized for single GPU

agents:
  intake:
    model: "llama3.2:3b"
  policy:
    model: "llama3.2:3b"
  triage:
    model: "llama3.2:3b"
```

### Streamlit UI
The UI now:
- ✅ Auto-detects available models
- ✅ Shows recommended model in dropdown
- ✅ Uses detected model automatically
- ✅ Falls back to Mock mode if Ollama unavailable

## How It Works

1. **On Startup**: System checks Ollama availability
2. **Model Detection**: Scans for available models
3. **Auto-Selection**: Chooses best model for single GPU (smallest first)
4. **Initialization**: Uses detected model for all agents
5. **Error Handling**: Falls back to Mock mode if model unavailable

## Single GPU Optimization

### Why `llama3.2:3b`?
- **Size**: Only 2GB (fits easily in GPU memory)
- **Speed**: Fast inference on single GPU
- **Quality**: Good enough for claims processing
- **Memory**: Leaves room for other processes

### GPU Memory Usage
- `llama3.2:3b`: ~2-3GB GPU memory
- `mistral:latest`: ~4-5GB GPU memory
- `llama3.2`: ~6-8GB GPU memory

## Troubleshooting

### Model Not Found Error
If you see: `model 'llama3.2' not found`

**Solution**: The system now auto-detects and uses available models. If you still see errors:

1. Check available models:
   ```bash
   ollama list
   ```

2. Run setup check:
   ```bash
   python3 scripts/check_ollama_setup.py
   ```

3. The system will automatically use `llama3.2:3b` if available

### Ollama Not Running
If Ollama service is not running:

```bash
# Start Ollama
ollama serve

# In another terminal, verify
ollama list
```

### Using Different Model
To use a different model (e.g., `mistral:latest`):

1. **In Streamlit UI**: Select "Ollama (Local) - mistral:latest" from dropdown
2. **In Code**: The system will auto-detect and use it
3. **Manual Override**: Update `config.yaml` if needed

## Verification

Test that everything works:

```bash
# 1. Check Ollama setup
python3 scripts/check_ollama_setup.py

# 2. Test model detection
python3 -c "from src.ui.utils import get_available_ollama_model; print(get_available_ollama_model())"

# 3. Test service initialization
python3 -c "from src.ui.services import UIService; import asyncio; service = UIService(); asyncio.run(service._ensure_initialized('ollama')); print('✓ OK')"

# 4. Run Streamlit
streamlit run streamlit_app.py
```

## Summary

✅ **Automatic Model Detection** - No manual configuration needed
✅ **Single GPU Optimized** - Uses smallest available model (`llama3.2:3b`)
✅ **Error Handling** - Falls back gracefully if model unavailable
✅ **UI Integration** - Shows available models in dropdown
✅ **Works Out of Box** - Detects and uses your installed models automatically

The system is now fully configured for single GPU operation with Ollama!

