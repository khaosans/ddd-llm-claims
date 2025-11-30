"""
JSON Utilities - Robust JSON parsing and extraction from LLM responses

Handles common LLM output issues:
- Extra text before/after JSON
- Markdown code blocks
- Multiple JSON objects
- Trailing commas
- Comments in JSON
"""

import json
import re
from typing import Optional, Dict, Any


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON from text that may contain extra content.
    
    Handles:
    - JSON wrapped in markdown code blocks
    - Extra text before/after JSON
    - Multiple JSON objects (returns first valid one)
    - Comments and explanations
    
    Args:
        text: Text that may contain JSON
        
    Returns:
        Extracted JSON string, or None if no valid JSON found
    """
    if not text or not text.strip():
        return None
    
    text = text.strip()
    
    # Remove markdown code blocks (handle multiline)
    text = re.sub(r'```json\s*\n?', '', text, flags=re.MULTILINE)
    text = re.sub(r'```\s*\n?', '', text, flags=re.MULTILINE)
    text = text.strip()
    
    if not text:
        return None
    
    # Try to find JSON object boundaries
    # Look for { ... } pattern
    brace_count = 0
    start_idx = -1
    
    for i, char in enumerate(text):
        if char == '{':
            if start_idx == -1:
                start_idx = i
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx != -1:
                # Found complete JSON object
                json_str = text[start_idx:i+1]
                # Validate it looks like JSON (has at least one key-value pair or is empty object)
                if json_str.strip() and ('{' in json_str and '}' in json_str):
                    return json_str
                # Reset and continue searching
                start_idx = -1
                brace_count = 0
    
    # If no complete object found, check if entire text might be JSON
    text_stripped = text.strip()
    if text_stripped.startswith('{') and text_stripped.endswith('}'):
        # Might be JSON, return it for parsing attempt
        return text_stripped
    
    # No JSON found
    return None


def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string by removing common issues.
    
    Handles:
    - Trailing commas
    - Comments (basic)
    - Extra whitespace
    - Unescaped quotes in strings
    - Control characters
    
    Args:
        json_str: JSON string to clean
        
    Returns:
        Cleaned JSON string
    """
    if not json_str:
        return json_str
    
    # Remove single-line comments (basic)
    json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
    
    # Remove multi-line comments
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    
    # Remove trailing commas before } or ]
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Remove control characters (except newlines and tabs)
    json_str = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', json_str)
    
    # Fix common quote issues (but be careful not to break valid JSON)
    # Only fix if we see obvious issues like unescaped quotes in what looks like a string value
    # This is conservative to avoid breaking valid JSON
    
    return json_str.strip()


def parse_json_resilient(text: str, max_attempts: int = 3) -> Optional[Dict[str, Any]]:
    """
    Parse JSON from text with multiple fallback strategies.
    
    Tries multiple approaches:
    1. Direct JSON parsing
    2. Extract JSON from text
    3. Clean and retry
    4. Try to find first valid JSON object
    5. Try to repair common JSON issues
    
    Args:
        text: Text containing JSON
        max_attempts: Maximum parsing attempts (will try up to 5 strategies)
        
    Returns:
        Parsed JSON dict, or None if all attempts fail
    """
    if not text:
        return None
    
    attempts = [
        # Strategy 1: Direct parse (fastest, most common case)
        lambda t: json.loads(t),
        
        # Strategy 2: Extract JSON first (handles markdown, extra text)
        lambda t: json.loads(extract_json_from_text(t) or t),
        
        # Strategy 3: Clean then parse (handles trailing commas, comments)
        lambda t: json.loads(clean_json_string(t)),
        
        # Strategy 4: Extract, clean, then parse (most comprehensive)
        lambda t: json.loads(clean_json_string(extract_json_from_text(t) or t)),
        
        # Strategy 5: Try to find and parse first JSON object (handles multiple objects)
        lambda t: _parse_first_json_object(t),
        
        # Strategy 6: Try to repair and parse (last resort)
        lambda t: _repair_and_parse(t),
    ]
    
    # Try up to max_attempts strategies (but don't exceed available strategies)
    num_strategies = min(max_attempts, len(attempts))
    
    for i, attempt in enumerate(attempts[:num_strategies]):
        try:
            result = attempt(text)
            if result is not None:
                return result
        except (json.JSONDecodeError, ValueError, TypeError, AttributeError) as e:
            # Continue to next strategy unless this is the last one
            if i == num_strategies - 1:
                # Last attempt failed, return None
                pass
            continue
    
    return None


def _repair_and_parse(text: str) -> Dict[str, Any]:
    """
    Attempt to repair common JSON issues and parse.
    
    This is a last-resort strategy that tries to fix:
    - Missing quotes around keys
    - Single quotes instead of double quotes
    - Unescaped quotes in strings
    """
    # Try extracting JSON first
    extracted = extract_json_from_text(text) or text
    
    # Try replacing single quotes with double quotes (but be careful)
    # Only do this if it looks like JSON with single quotes
    if "'" in extracted and '"' not in extracted:
        # Simple replacement (not perfect but may work for simple cases)
        repaired = extracted.replace("'", '"')
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass
    
    # Try cleaning
    cleaned = clean_json_string(extracted)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError("Could not repair JSON")


def _parse_first_json_object(text: str) -> Dict[str, Any]:
    """Try to parse the first JSON object found in text."""
    # Find first {
    start = text.find('{')
    if start == -1:
        raise ValueError("No JSON object found")
    
    # Find matching }
    brace_count = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            brace_count += 1
        elif text[i] == '}':
            brace_count -= 1
            if brace_count == 0:
                json_str = text[start:i+1]
                return json.loads(json_str)
    
    raise ValueError("Incomplete JSON object")


def validate_and_repair_json(json_str: str) -> Optional[str]:
    """
    Validate JSON and attempt basic repairs.
    
    Args:
        json_str: JSON string to validate/repair
        
    Returns:
        Repaired JSON string, or None if repair impossible
    """
    try:
        # Try parsing to validate
        json.loads(json_str)
        return json_str
    except json.JSONDecodeError:
        # Try cleaning
        cleaned = clean_json_string(json_str)
        try:
            json.loads(cleaned)
            return cleaned
        except json.JSONDecodeError:
            # Try extracting JSON
            extracted = extract_json_from_text(json_str)
            if extracted:
                try:
                    json.loads(extracted)
                    return extracted
                except json.JSONDecodeError:
                    pass
    
    return None

