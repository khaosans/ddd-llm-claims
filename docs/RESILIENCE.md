# System Resilience Guide

This document describes the resilience features built into the system to handle errors gracefully and autonomously.

The resilience patterns implemented here are based on established research and best practices:
- **Circuit Breaker Pattern**: Hohpe & Woolf (2003), Nygard (2007), Fowler (2014)
- **Retry Logic**: Exponential backoff strategies (Nygard, 2007)
- **Graceful Degradation**: Fault tolerance patterns (Netflix Tech Blog, 2011)

See: docs/REFERENCES.md#resilience-patterns--circuit-breakers

## JSON Parsing Resilience

### Problem
LLMs sometimes return:
- Extra text before/after JSON
- Markdown code blocks wrapping JSON
- Multiple JSON objects
- Malformed JSON with trailing commas
- Explanations mixed with JSON

### Solution
The system uses **multi-strategy JSON parsing**:

1. **Direct Parsing** - Try parsing JSON directly
2. **Extraction** - Extract JSON from mixed content
3. **Cleaning** - Remove trailing commas, comments
4. **Object Detection** - Find first complete JSON object
5. **Retry Logic** - Retry with improved prompts

### Implementation
- `src/agents/json_utils.py` - Robust JSON utilities
- `src/agents/base_agent.py` - Enhanced `validate_output()` method
- Automatic retry with exponential backoff

## Automatic Error Handling

### Error Types Handled

#### 1. JSON Parsing Errors
- **Detection**: "json", "parse", "extra data" in error message
- **Action**: 
  - Retry with stricter prompt
  - Suggest Mock mode
  - Provide helpful error message

#### 2. Ollama Connection Errors
- **Detection**: "ollama", "404", "not found" in error message
- **Action**:
  - Check Ollama service status
  - Verify model availability
  - Suggest Mock mode fallback

#### 3. Model Unavailable Errors
- **Detection**: Model not found (404)
- **Action**:
  - Auto-detect available models
  - Fallback to Mock mode
  - Provide setup instructions

### Error Messages
All errors provide:
- Clear description of the problem
- Specific solutions
- Fallback options
- Technical details (in expandable section)

## Automatic Fallbacks

### 1. Model Detection Fallback
```python
# Auto-detects available models
detected_model = get_available_ollama_model()
if detected_model:
    model = detected_model
else:
    # Falls back to Mock mode
    model = "mock"
```

### 2. Service Initialization Fallback
```python
try:
    # Try Ollama
    provider = create_model_provider("ollama", model)
except Exception:
    # Fallback to Mock
    provider = create_mock_provider()
```

### 3. JSON Parsing Fallback
```python
# Multiple parsing strategies
data = parse_json_resilient(output, max_attempts=3)
if data is None:
    # Try extraction
    extracted = extract_json_from_text(output)
    data = json.loads(extracted)
```

## Retry Logic

### Intake Agent Retries
- **Max Retries**: 2 (3 total attempts)
- **Backoff**: Exponential (0.5s, 1s)
- **Improved Prompts**: Stricter JSON-only instructions on retry

### JSON Parsing Retries
- **Max Attempts**: 3 strategies
- **Strategies**: Direct → Extract → Clean → Extract+Clean

## User-Friendly Error Messages

### In Streamlit UI
- **Specific Guidance**: Based on error type
- **Actionable Solutions**: Step-by-step fixes
- **Fallback Options**: Mock mode suggestion
- **Technical Details**: Collapsible for debugging

### Error Categories

1. **JSON Parsing Errors**
   - Shows what went wrong
   - Suggests retry or Mock mode
   - Explains common causes

2. **Ollama Errors**
   - Checks service status
   - Verifies model availability
   - Provides setup instructions

3. **General Errors**
   - Generic fallback message
   - Mock mode suggestion
   - Technical details available

## Best Practices

### For Development
1. **Use Mock Mode** for testing
2. **Check Ollama** before using local models
3. **Monitor Errors** in technical details

### For Production (Future)
1. **Log All Errors** for analysis
2. **Metrics** on error rates
3. **Automatic Alerts** for repeated failures
4. **Circuit Breaker** pattern for failing services (Hohpe & Woolf, 2003; Nygard, 2007; Fowler, 2014)
5. **Distributed Tracing** for error correlation (Sigelman et al., 2010)
6. **Observability** for production monitoring (Charity & Swaminathan, 2021)

## Testing Resilience

Test error handling:
```bash
# Test JSON extraction
python3 -c "from src.agents.json_utils import parse_json_resilient; print(parse_json_resilient('{\"test\":\"value\"} extra'))"

# Test model detection
python3 scripts/check_ollama_setup.py

# Test service initialization
python3 -c "from src.ui.services import UIService; import asyncio; service = UIService(); asyncio.run(service._ensure_initialized('ollama'))"
```

## Summary

✅ **Robust JSON Parsing** - Handles malformed LLM output
✅ **Automatic Retries** - Retries with improved prompts
✅ **Graceful Fallbacks** - Falls back to Mock mode
✅ **Clear Error Messages** - User-friendly guidance
✅ **Auto-Detection** - Finds available models automatically
✅ **Resilient Architecture** - Handles errors at every layer

The system is now much more resilient and handles errors autonomously!

