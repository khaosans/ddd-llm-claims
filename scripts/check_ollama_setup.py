#!/usr/bin/env python3
"""
Check Ollama Setup - Verify Ollama is configured correctly for single GPU

This script checks:
1. Ollama service is running
2. Models are available
3. Recommends best model for single GPU setup
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import ollama
except ImportError:
    print("❌ Ollama Python package not installed")
    print("   Install with: pip install ollama")
    sys.exit(1)

def check_ollama_service():
    """Check if Ollama service is running"""
    try:
        client = ollama.Client()
        client.list()
        return True, None
    except Exception as e:
        return False, str(e)

def get_available_models():
    """Get list of available models"""
    try:
        client = ollama.Client()
        models_response = client.list()
        
        # Handle Pydantic response object
        if hasattr(models_response, 'models'):
            models_list = models_response.models
        elif isinstance(models_response, dict) and 'models' in models_response:
            models_list = models_response['models']
        elif isinstance(models_response, list):
            models_list = models_response
        else:
            models_list = []
        
        # Extract model names
        model_names = []
        for m in models_list:
            if isinstance(m, dict):
                name = m.get("name") or m.get("model")
            elif hasattr(m, 'model'):
                name = m.model
            elif hasattr(m, 'name'):
                name = m.name
            else:
                continue
            if name:
                model_names.append(name)
        
        return model_names
    except Exception as e:
        print(f"Error getting models: {e}")
        import traceback
        traceback.print_exc()
        return []

def recommend_model(available_models):
    """Recommend best model for single GPU"""
    if not available_models:
        return None
    
    # Priority order for single GPU (smaller models first)
    priority_order = [
        "llama3.2:3b",      # Smallest, fastest (2GB)
        "mistral:latest",   # Good balance (4.4GB)
        "phi3:mini",        # Very small
        "mistral:7b",       # Alternative
        "llama3.2",         # Larger but good quality
    ]
    
    for model in priority_order:
        if model in available_models:
            return model
    
    return available_models[0]

def main():
    print("🔍 Checking Ollama Setup for Single GPU\n")
    
    # Check service
    print("1. Checking Ollama service...")
    service_ok, error = check_ollama_service()
    if not service_ok:
        print(f"   ❌ Ollama service not running: {error}")
        print("\n   💡 Start Ollama with: ollama serve")
        sys.exit(1)
    print("   ✅ Ollama service is running\n")
    
    # Get models
    print("2. Checking available models...")
    models = get_available_models()
    if not models:
        print("   ⚠️  No models found")
        print("\n   💡 Download a model with: ollama pull llama3.2:3b")
        sys.exit(1)
    
    print(f"   ✅ Found {len(models)} model(s):")
    for model in models:
        print(f"      - {model}")
    print()
    
    # Recommend model
    print("3. Recommending model for single GPU...")
    recommended = recommend_model(models)
    if recommended:
        print(f"   ✅ Recommended: {recommended}")
        print(f"\n   💡 This model is optimized for single GPU setups")
        print(f"   💡 Update your code to use: '{recommended}'")
    else:
        print("   ⚠️  Could not determine recommendation")
    
    print("\n✅ Ollama setup check complete!")
    print(f"\n📝 To use in code:")
    print(f"   model = '{recommended}'")
    print(f"   provider = create_model_provider('ollama', model)")

if __name__ == "__main__":
    main()

