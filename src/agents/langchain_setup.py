"""
LangChain Setup - Local-first configuration

Provides LangChain setup that prioritizes local/open-source models.
"""

from typing import Optional
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel


def create_langchain_llm(
    provider: str = "ollama",
    model: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> BaseChatModel:
    """
    Create a LangChain LLM, prioritizing local/open-source options.
    
    Args:
        provider: Provider name ("ollama", "openai", "anthropic", "mock")
        model: Model name (defaults based on provider)
        temperature: Sampling temperature
        **kwargs: Additional provider-specific arguments
    
    Returns:
        LangChain chat model
    """
    provider = provider.lower()
    
    if provider == "ollama" or provider == "ollama (local)":
        if not LANGCHAIN_COMMUNITY_AVAILABLE:
            raise ImportError("langchain-community not installed. Install with: pip install langchain-community")
        
        model = model or kwargs.get("model", "llama3.2")
        base_url = kwargs.get("base_url", "http://localhost:11434")
        
        try:
            return Ollama(
                model=model,
                base_url=base_url,
                temperature=temperature,
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to Ollama at {base_url}. "
                f"Make sure Ollama is running: ollama serve"
            ) from e
    
    elif provider == "openai":
        if not LANGCHAIN_OPENAI_AVAILABLE:
            raise ImportError("langchain-openai not installed. Install with: pip install langchain-openai")
        
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        model = model or kwargs.get("model", "gpt-4o-mini")
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
        )
    
    elif provider == "anthropic":
        if not LANGCHAIN_ANTHROPIC_AVAILABLE:
            raise ImportError("langchain-anthropic not installed. Install with: pip install langchain-anthropic")
        
        api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")
        
        model = model or kwargs.get("model", "claude-3-5-sonnet-20241022")
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=api_key,
        )
    
    elif provider == "mock" or provider == "mock (demo)":
        # Return a mock LLM for demo purposes
        from unittest.mock import MagicMock
        from langchain_core.language_models import BaseChatModel
        from langchain_core.messages import AIMessage
        
        class MockLLM(BaseChatModel):
            async def ainvoke(self, input, config=None, **kwargs):
                # Return mock response
                return AIMessage(content='{"claim_type":"auto","incident_date":"2024-01-15T14:30:00","claimed_amount":"3500.00","currency":"USD","incident_location":"Main St","description":"Test","claimant_name":"John Doe"}')
        
        return MockLLM()
    
    else:
        raise ValueError(f"Unknown provider: {provider}. Use 'ollama', 'openai', 'anthropic', or 'mock'")

