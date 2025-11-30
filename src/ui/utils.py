"""
UI Utilities - Helper functions for Streamlit UI

Provides utilities for model provider setup, default configurations,
and local-first setup.
"""

import os
from typing import Optional
from pathlib import Path


def get_default_model_provider() -> str:
    """
    Get default model provider, prioritizing local/open-source options.
    
    Returns:
        Default provider name
    """
    # Check environment variable first
    env_provider = os.getenv("MODEL_PROVIDER", "").lower()
    if env_provider in ["ollama", "mock"]:
        return env_provider
    
    # Check if Ollama is available
    try:
        import ollama
        # Try to connect
        client = ollama.Client()
        client.list()  # This will fail if Ollama not running
        return "ollama"
    except Exception:
        pass
    
    # Default to mock for demo
    return "mock"


def setup_local_ollama() -> dict:
    """
    Setup Ollama configuration for local use.
    
    Returns:
        Configuration dictionary
    """
    return {
        "provider": "ollama",
        "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    }


def check_ollama_available() -> bool:
    """
    Check if Ollama is available and running.
    
    Returns:
        True if Ollama is available
    """
    try:
        import ollama
        client = ollama.Client()
        client.list()
        return True
    except Exception:
        return False


def get_local_model_info() -> dict:
    """
    Get information about available local models.
    
    Returns:
        Dictionary with model information
    """
    info = {
        "ollama_available": False,
        "ollama_models": [],
        "recommended_model": None,
    }
    
    if check_ollama_available():
        try:
            import ollama
            client = ollama.Client()
            models_response = client.list()
            
            # Handle different response formats
            if hasattr(models_response, 'models'):
                models_list = models_response.models
            elif isinstance(models_response, dict) and 'models' in models_response:
                models_list = models_response['models']
            elif isinstance(models_response, list):
                models_list = models_response
            else:
                models_list = []
            
            info["ollama_available"] = True
            
            # Extract model names
            model_names = []
            for m in models_list:
                if isinstance(m, dict):
                    name = m.get("name") or m.get("model")
                elif hasattr(m, 'name'):
                    name = m.name
                elif hasattr(m, 'model'):
                    name = m.model
                else:
                    continue
                if name:
                    model_names.append(name)
            
            info["ollama_models"] = model_names
            
            # Recommend a model (prefer smaller for single GPU)
            # Priority: smallest first for single GPU setups
            preferred = ["llama3.2:3b", "mistral:latest", "phi3:mini", "mistral:7b", "llama3.2", "llama3.2:1b"]
            for pref in preferred:
                if pref in info["ollama_models"]:
                    info["recommended_model"] = pref
                    break
            
            if not info["recommended_model"] and info["ollama_models"]:
                info["recommended_model"] = info["ollama_models"][0]
        except Exception as e:
            import warnings
            warnings.warn(f"Error getting Ollama models: {e}")
            pass
    
    return info


def get_available_ollama_model() -> Optional[str]:
    """
    Get the best available Ollama model for single GPU setup.
    
    Returns:
        Model name string, or None if no models available
    """
    if not check_ollama_available():
        return None
    
    try:
        import ollama
        client = ollama.Client()
        models_response = client.list()
        
        # Handle different response formats
        if hasattr(models_response, 'models'):
            models_list = models_response.models
        elif isinstance(models_response, dict) and 'models' in models_response:
            models_list = models_response['models']
        elif isinstance(models_response, list):
            models_list = models_response
        else:
            models_list = []
        
        # Extract model names
        available_models = []
        for m in models_list:
            if isinstance(m, dict):
                name = m.get("name") or m.get("model")
            elif hasattr(m, 'name'):
                name = m.name
            elif hasattr(m, 'model'):
                name = m.model
            else:
                continue
            if name:
                available_models.append(name)
        
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
        
        # Find first available model in priority order
        for model in priority_order:
            if model in available_models:
                return model
        
        # Fallback to first available model
        return available_models[0]
    except Exception as e:
        import warnings
        warnings.warn(f"Error detecting Ollama model: {e}")
        return None


def ensure_data_directories() -> None:
    """Ensure required data directories exist"""
    Path("data").mkdir(exist_ok=True)
    Path("data/chroma_db").mkdir(parents=True, exist_ok=True)

