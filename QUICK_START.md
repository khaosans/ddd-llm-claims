# Quick Start Guide

Get up and running with the DDD Claims Processing System in minutes.

## ⚠️ Important: Read First

- **This is a DEMO system** - See [DISCLAIMERS.md](DISCLAIMERS.md)
- **Educational purposes only** - Not for production
- **Use demo data only** - Never use real customer data

## Fastest Start (3 minutes)

### Streamlit Dashboard (Recommended)

```bash
# Set up virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run streamlit_app.py

# Or use convenience script:
./run_streamlit.sh
```

**Opens interactive web UI** - works immediately with Mock mode (no setup needed)!

The dashboard provides:
- **Simple navigation** - Just 4 pages: Dashboard, Process Claim, Claims List, Review Queue
- **Demo mode** - Step-by-step processing with visual progress
- **Quick mode** - Fast processing without step-by-step display
- **Template selection** - Pre-built examples to get started quickly
- **Human review** - Inline review prompts when needed

**No Ollama required** - Mock mode works out of the box!

## With Local Models (Ollama - Recommended!)

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com
```

### 2. Start Ollama

```bash
ollama serve
```

### 3. Download a Model

```bash
ollama pull llama3.2
```

### 4. Run Dashboard

```bash
streamlit run streamlit_app.py
```

**That's it!** The dashboard auto-detects Ollama and uses it automatically.

No configuration needed - completely local and open-source!

See [LOCAL_SETUP.md](LOCAL_SETUP.md) for more details.

## Interactive Examples

### Basic Example

```bash
python examples/run_example.py
```

### Human Review Example

```bash
python examples/human_review_example.py
```

### Visualization

```bash
python visualize.py
```

Or open in browser:
```bash
open docs/visualization.html
```

## What to Explore

1. **Start with Dashboard**: Run `streamlit run streamlit_app.py` and click "Start Processing Claims"
2. **Try Demo Mode**: Enable "Demo Mode" toggle to see step-by-step processing
3. **Use Templates**: Select from pre-built templates (Auto Insurance, High Value, etc.)
4. **View Visualizations**: Open `docs/visualization.html` for interactive architecture diagrams
5. **Read Documentation**: Start with README.md for full overview
6. **Study Code**: Explore `src/domain/` for DDD patterns

## Next Steps

- Read [PREFACE.md](PREFACE.md) for project overview
- Review [BEST_PRACTICES.md](BEST_PRACTICES.md) for guidelines
- Check [DISCLAIMERS.md](DISCLAIMERS.md) for limitations
- Explore [docs/TECHNICAL.md](docs/TECHNICAL.md) for architecture

## Troubleshooting

### Ollama Not Working?

Use demo mode - it works without Ollama:
```bash
python demo.py
```

### Import Errors?

Make sure you're in the project root:
```bash
cd /path/to/ddd-llm
python demo.py
```

### Need Help?

- Check [docs/TECHNICAL.md](docs/TECHNICAL.md)
- Review [BEST_PRACTICES.md](BEST_PRACTICES.md)
- See examples in `examples/` directory

---

**Remember**: This is a demonstration system for learning. Enjoy exploring!

