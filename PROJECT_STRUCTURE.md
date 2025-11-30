# Project Structure

This document describes the organization of the DDD Claims Processing System repository.

## Root Directory

### Core Application Files
- `streamlit_app.py` - Main Streamlit dashboard application
- `demo.py` - Command-line interactive demo script
- `data_templates.py` - Template data for demos
- `config.yaml` - Application configuration
- `requirements.txt` - Python dependencies
- `pyproject.toml` - Project metadata

### Documentation (Root Level - Quick Access)
- `README.md` - Main project overview
- `QUICK_START.md` - Fastest way to get started
- `DISCLAIMERS.md` - ⚠️ **READ FIRST** - Important limitations
- `PREFACE.md` - Project purpose and context
- `BEST_PRACTICES.md` - Development guidelines
- `LOCAL_SETUP.md` - Local development setup
- `DATA_TEMPLATES.md` - Available data templates
- `TEMPLATES_QUICK_REFERENCE.md` - Quick template reference

### Scripts
- `run_streamlit.sh` - Start Streamlit dashboard
- `run_demo.sh` - Run command-line demo
- `run_dashboard.sh` - Alternative dashboard launcher
- `start_services.sh` - Start required services
- `check_services.sh` - Check service status

## Directory Structure

### `/src` - Source Code
```
src/
├── domain/          # Domain-Driven Design models
│   ├── claim/      # Claim aggregate, value objects, events
│   ├── policy/     # Policy aggregate, events
│   └── fraud/      # Fraud value objects, events
├── agents/         # LLM agents (Anti-Corruption Layer)
├── orchestrator/   # Workflow orchestration
├── repositories/   # Data access abstraction
├── human_review/  # Human-in-the-loop review system
├── ui/            # Streamlit UI components and services
├── database/      # Database models and session management
├── vector_store/  # Vector database integration
└── visualization/ # Workflow visualization utilities
```

### `/pages` - Streamlit Pages
- `process_claim.py` - Main claim processing page (with demo mode)
- `claims_list.py` - View and search all claims
- `review_queue.py` - Human review queue interface

### `/docs` - Documentation
- `README.md` - Documentation index
- `TECHNICAL.md` - Technical architecture documentation
- `architecture.md` - Architecture diagrams
- `sequence_diagram.md` - Workflow sequence diagrams
- `REFERENCES.md` - Research citations (APA format)
- `RESEARCH_SUMMARY.md` - Quick reference for research by category
- `CORRECTNESS.md` - System invariants
- `DOA_CHECKLIST.md` - DDD verification checklist
- `DEMO_GUIDE.md` - Demo presentation guide
- `DEMO_WORKFLOW_GUIDE.md` - Demo mode workflow details
- `visualization_guide.md` - Visualization usage guide
- `visualization.html` - Interactive visualization dashboard
- `RESILIENCE.md` - Error handling and resilience patterns
- `COMPLIANCE_USAGE.md` - Compliance and explainability features
- `status/` - Historical implementation status documents

### `/tests` - Test Suite
- `test_domain_models.py` - Domain model tests
- `test_intake_agent.py` - Intake agent tests
- `test_e2e.py` - End-to-end tests
- `test_human_review.py` - Human review tests
- `test_integration_final.py` - Integration tests
- `test_e2e_simple.py` - Simplified E2E tests
- `test_run.py` - Test runner utilities

### `/examples` - Example Code and Data
- `run_example.py` - Basic usage example
- `human_review_example.py` - Human review example
- `sample_claim_email.txt` - Sample claim input
- `sample_policy.json` - Sample policy data
- `expected_output.json` - Expected output example

### `/scripts` - Utility Scripts
- `setup.py` - Project setup script
- `setup_ollama.sh` - Ollama installation script
- `run_tests.py` - Test runner
- `visualize.py` - Visualization generator

### `/data` - Data Storage
- `chroma_db/` - ChromaDB vector database files (gitignored)

## Quick Navigation

**Getting Started:**
1. Read `DISCLAIMERS.md` first
2. Follow `QUICK_START.md`
3. Run `streamlit run streamlit_app.py`

**For Developers:**
1. Read `BEST_PRACTICES.md`
2. Review `docs/TECHNICAL.md`
3. Check `docs/status/` for implementation history

**For Demos:**
1. Read `docs/DEMO_GUIDE.md`
2. Use `demo.py` for command-line demo
3. Use Streamlit dashboard for interactive demo

