"""
API Configuration Manager

Manages quick model switching, auto-detection of available providers,
and fast configuration loading from config.yaml or environment variables.
"""

import os
import yaml
from typing import Dict, Optional, Any
from pathlib import Path

try:
    import ollama
except ImportError:
    ollama = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import anthropic
except ImportError:
    anthropic = None


class APIConfigManager:
    """
    Manages API configuration for quick model switching.
    
    Features:
    - Load configs from config.yaml or env vars
    - Auto-detect available providers (Ollama health, API keys)
    - Fast provider switching without restart
    - Per-agent model selection
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize API config manager.
        
        Args:
            config_path: Path to config.yaml (default: ./config.yaml)
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._available_providers: Dict[str, bool] = {}
        self._load_config()
        self._detect_providers()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = {}
    
    def _detect_providers(self):
        """Auto-detect available providers"""
        # Check Ollama
        self._available_providers["ollama"] = self._check_ollama()
        
        # Check OpenAI
        self._available_providers["openai"] = self._check_openai()
        
        # Check Anthropic
        self._available_providers["anthropic"] = self._check_anthropic()
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        if ollama is None:
            return False
        
        try:
            base_url = self._config.get("model_provider", {}).get("ollama", {}).get("base_url", "http://localhost:11434")
            client = ollama.Client(host=base_url)
            # Try to list models (lightweight check)
            client.list()
            return True
        except Exception:
            return False
    
    def _check_openai(self) -> bool:
        """Check if OpenAI API key is available"""
        api_key = os.getenv("OPENAI_API_KEY") or self._config.get("model_provider", {}).get("openai", {}).get("api_key", "")
        if api_key and api_key.startswith("${"):
            # Environment variable reference
            api_key = os.getenv(api_key[2:-1], "")
        return bool(api_key and OpenAI is not None)
    
    def _check_anthropic(self) -> bool:
        """Check if Anthropic API key is available"""
        api_key = os.getenv("ANTHROPIC_API_KEY") or self._config.get("model_provider", {}).get("anthropic", {}).get("api_key", "")
        if api_key and api_key.startswith("${"):
            # Environment variable reference
            api_key = os.getenv(api_key[2:-1], "")
        return bool(api_key and anthropic is not None)
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider: Provider name (ollama, openai, anthropic)
        
        Returns:
            Provider configuration dictionary
        """
        provider_config = self._config.get("model_provider", {}).get(provider, {})
        
        # Resolve environment variables
        if "api_key" in provider_config:
            api_key = provider_config["api_key"]
            if api_key.startswith("${") and api_key.endswith("}"):
                env_var = api_key[2:-1]
                provider_config["api_key"] = os.getenv(env_var, "")
        
        return provider_config
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name: Agent name (intake, policy, triage, fraud, document_analysis, document_matching)
        
        Returns:
            Agent configuration dictionary
        """
        agent_config = self._config.get("agents", {}).get(agent_name, {})
        
        # Defaults from primary provider
        if not agent_config:
            primary_provider = self._config.get("model_provider", {}).get("provider", "ollama")
            provider_config = self.get_provider_config(primary_provider)
            agent_config = {
                "provider": primary_provider,
                "model": provider_config.get("default_model", "llama3.2:3b"),
                "temperature": 0.3,
            }
        
        return agent_config
    
    def is_provider_available(self, provider: str) -> bool:
        """
        Check if a provider is available.
        
        Args:
            provider: Provider name
        
        Returns:
            True if provider is available
        """
        return self._available_providers.get(provider, False)
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Get all available providers"""
        return self._available_providers.copy()
    
    def get_preferred_provider(self, agent_name: Optional[str] = None) -> str:
        """
        Get preferred provider (local-first).
        
        Args:
            agent_name: Optional agent name for agent-specific config
        
        Returns:
            Provider name (ollama if available, else first available cloud provider)
        """
        # Check agent-specific config
        if agent_name:
            agent_config = self.get_agent_config(agent_name)
            preferred = agent_config.get("provider")
            if preferred and self.is_provider_available(preferred):
                return preferred
        
        # Local-first: prefer Ollama
        if self.is_provider_available("ollama"):
            return "ollama"
        
        # Fallback to cloud providers
        if self.is_provider_available("openai"):
            return "openai"
        
        if self.is_provider_available("anthropic"):
            return "anthropic"
        
        # Default to ollama (will fail if not available, but that's expected)
        return "ollama"
    
    def get_model_for_agent(self, agent_name: str) -> tuple[str, str]:
        """
        Get provider and model for an agent.
        
        Args:
            agent_name: Agent name
        
        Returns:
            Tuple of (provider, model)
        """
        agent_config = self.get_agent_config(agent_name)
        provider = agent_config.get("provider", self.get_preferred_provider(agent_name))
        model = agent_config.get("model")
        
        # If model not specified, get default for provider
        if not model:
            provider_config = self.get_provider_config(provider)
            model = provider_config.get("default_model", "llama3.2:3b")
        
        return provider, model
    
    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()
        self._detect_providers()
    
    def update_agent_config(self, agent_name: str, provider: Optional[str] = None, model: Optional[str] = None, temperature: Optional[float] = None):
        """
        Update agent configuration (in-memory only, doesn't persist to file).
        
        Args:
            agent_name: Agent name
            provider: Optional provider to set
            model: Optional model to set
            temperature: Optional temperature to set
        """
        if "agents" not in self._config:
            self._config["agents"] = {}
        
        if agent_name not in self._config["agents"]:
            self._config["agents"][agent_name] = {}
        
        if provider is not None:
            self._config["agents"][agent_name]["provider"] = provider
        if model is not None:
            self._config["agents"][agent_name]["model"] = model
        if temperature is not None:
            self._config["agents"][agent_name]["temperature"] = temperature


# Global instance
_config_manager: Optional[APIConfigManager] = None


def get_api_config_manager(config_path: Optional[str] = None) -> APIConfigManager:
    """
    Get or create global API config manager instance.
    
    Args:
        config_path: Optional path to config.yaml
    
    Returns:
        APIConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = APIConfigManager(config_path)
    return _config_manager


def reset_api_config_manager():
    """Reset the global API config manager"""
    global _config_manager
    _config_manager = None

