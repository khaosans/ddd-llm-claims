"""
Model Provider Abstraction - Supports multiple LLM backends

This module provides a unified interface for different LLM providers:
- Ollama (local models, SLMs)
- OpenAI (cloud-based)
- Anthropic (cloud-based)

Each agent can use a different model, allowing optimization per task.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import ollama
except ImportError:
    ollama = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class ModelProvider(ABC):
    """
    Abstract base class for LLM model providers.
    
    This abstraction allows agents to work with any LLM backend
    without being coupled to a specific provider. This is the
    Strategy pattern in action.
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion from the model.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (instructions for the model)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters
        
        Returns:
            Generated text response
        """
        pass


class OllamaProvider(ModelProvider):
    """
    Ollama Provider - For local models and SLMs.
    
    Ollama allows running LLMs locally, including Small Language Models (SLMs)
    like Llama 3.2, Mistral 7B, Phi-3, etc. This is ideal for:
    - Privacy-sensitive applications
    - Cost reduction (no API costs)
    - Offline operation
    - Testing and development
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
            model: Model name (e.g., "llama3.2", "mistral:7b", "phi3:mini")
        """
        if ollama is None:
            raise ImportError("ollama package is required. Install with: pip install ollama")
        self.base_url = base_url
        self.model = model
        self.client = ollama.Client(host=base_url)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate using Ollama.
        
        Note: Ollama's async support may vary. This uses the sync client
        but can be wrapped in an executor for true async.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        options = {
            "temperature": temperature,
        }
        if max_tokens:
            options["num_predict"] = max_tokens
        
        # Merge any additional options
        options.update(kwargs)
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options=options,
            )
            return response["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Ollama API error: {e}") from e


class OpenAIProvider(ModelProvider):
    """
    OpenAI Provider - For GPT models.
    
    Supports GPT-4, GPT-3.5, GPT-4o-mini, etc.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., "gpt-4o-mini", "gpt-4")
        """
        if OpenAI is None:
            raise ImportError("openai package is required. Install with: pip install openai")
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate using OpenAI API"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {e}") from e


class AnthropicProvider(ModelProvider):
    """
    Anthropic Provider - For Claude models.
    
    Supports Claude 3.5 Sonnet, Claude 3 Opus, etc.
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key
            model: Model name
        """
        if anthropic is None:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate using Anthropic API"""
        max_tokens = max_tokens or 4096  # Anthropic requires max_tokens
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {e}") from e


def create_model_provider(
    provider_type: str,
    model: str,
    **kwargs
) -> ModelProvider:
    """
    Factory function to create model providers.
    
    Args:
        provider_type: "ollama", "openai", or "anthropic"
        model: Model name
        **kwargs: Provider-specific configuration
    
    Returns:
        Configured ModelProvider instance
    
    Example:
        # Ollama (local)
        provider = create_model_provider("ollama", "llama3.2", base_url="http://localhost:11434")
        
        # OpenAI
        provider = create_model_provider("openai", "gpt-4o-mini", api_key="sk-...")
        
        # Anthropic
        provider = create_model_provider("anthropic", "claude-3-5-sonnet-20241022", api_key="sk-...")
    """
    if provider_type.lower() == "ollama":
        base_url = kwargs.get("base_url", "http://localhost:11434")
        return OllamaProvider(base_url=base_url, model=model)
    
    elif provider_type.lower() == "openai":
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("OpenAI provider requires api_key")
        return OpenAIProvider(api_key=api_key, model=model)
    
    elif provider_type.lower() == "anthropic":
        api_key = kwargs.get("api_key")
        if not api_key:
            raise ValueError("Anthropic provider requires api_key")
        return AnthropicProvider(api_key=api_key, model=model)
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

