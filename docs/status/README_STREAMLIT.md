# Streamlit Dashboard Guide

## Quick Start

Run the Streamlit dashboard:

```bash
streamlit run streamlit_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Features

### Main Dashboard
- System overview
- Quick statistics
- Navigation to all pages

### Process Claim
- Interactive claim processing
- Model selection
- Real-time workflow visualization

### Human Review
- Review queue interface
- Approve/Reject/Override decisions
- Feedback capture

### Claims List
- Searchable claims table
- Filtering and sorting
- Export functionality

### Analytics
- Processing metrics
- Performance charts
- Review statistics

### Visualizations
- Architecture diagrams
- Workflow visualization

### Settings
- Model configuration
- API key management
- System preferences

## Database Setup

The dashboard uses SQLite for persistence. The database is automatically created at `data/claims.db` on first run.

## Vector Database

ChromaDB is used for semantic search. Data is stored in `data/chroma_db/`.

## Configuration

Configure models and settings in the Settings page, or set environment variables:

- `MODEL_PROVIDER`: ollama, openai, or anthropic
- `OLLAMA_MODEL`: Model name for Ollama
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key

## Troubleshooting

### Database Errors
- Ensure `data/` directory exists
- Check file permissions

### Vector DB Errors
- Ensure `data/chroma_db/` directory exists
- Check ChromaDB installation

### Model Provider Errors
- Verify API keys are set correctly
- Check model provider is running (for Ollama)

