"""
Base Agent - Abstract base class for all agents

⚠️ DEMONSTRATION SYSTEM - NOT FOR PRODUCTION USE
This is an educational demonstration system. See DISCLAIMERS.md for details.

Agents in this system act as Anti-Corruption Layers (ACL) (Evans, 2003) that:
1. Translate unstructured external data into domain models
2. Protect the domain from external API changes
3. Enforce domain rules and invariants
4. Handle errors and validation

Each agent specializes in a specific domain task and uses LLMs (Brown et al., 2020)
to perform that task intelligently.

DDD Pattern: Anti-Corruption Layer - Agents protect the domain from messy
external data and API changes, translating them into clean domain models.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..domain.events import DomainEvent
from .model_provider import ModelProvider


class BaseAgent(ABC):
    """
    Abstract base class for all domain agents.
    
    DDD Pattern: Agents act as Anti-Corruption Layers (ACL).
    They translate between external systems (LLMs, APIs) and
    our domain model, protecting the domain from external changes.
    
    Each agent:
    1. Has a specific domain responsibility
    2. Uses an LLM to perform its task
    3. Validates output against domain models
    4. Publishes domain events when work is complete
    """
    
    def __init__(self, model_provider: ModelProvider, temperature: float = 0.7):
        """
        Initialize the agent.
        
        Args:
            model_provider: The LLM provider to use
            temperature: Sampling temperature for the model
        """
        self.model_provider = model_provider
        self.temperature = temperature
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        
        The system prompt defines the agent's role and behavior.
        It's part of "Prompt Engineering" - crafting instructions
        that make the LLM act as a domain expert.
        
        Returns:
            System prompt string
        """
        pass
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using the model provider.
        
        Args:
            prompt: User prompt
            **kwargs: Additional parameters for the model
        
        Returns:
            Generated text response
        """
        system_prompt = self.get_system_prompt()
        return await self.model_provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=self.temperature,
            **kwargs
        )
    
    @abstractmethod
    async def process(self, input_data: Any) -> tuple[Any, Optional[DomainEvent]]:
        """
        Process input data and return domain model + event.
        
        This is the main entry point for agents. Each agent
        implements this to perform its specific domain task.
        
        Args:
            input_data: Input to process (varies by agent)
        
        Returns:
            Tuple of (domain_object, domain_event)
            - domain_object: The created/updated domain object
            - domain_event: Domain event to publish (if any)
        """
        pass
    
    def validate_output(self, output: str, expected_schema: type, max_retries: int = 2) -> Any:
        """
        Validate LLM output against a Pydantic schema with resilient parsing.
        
        This enforces that the LLM output matches our domain model,
        ensuring type safety and business rule compliance.
        
        Uses multiple strategies to handle common LLM output issues:
        - Extra text before/after JSON
        - Markdown code blocks
        - Multiple JSON objects
        - Trailing commas and formatting issues
        
        Args:
            output: Raw LLM output (should be JSON)
            expected_schema: Pydantic model class to validate against
            max_retries: Maximum retry attempts with different parsing strategies
        
        Returns:
            Validated domain object
        
        Raises:
            ValueError: If output doesn't match schema after all retries
        """
        from .json_utils import parse_json_resilient, extract_json_from_text
        
        if not output or not output.strip():
            raise ValueError("Empty output from agent")
        
        # Try resilient parsing
        data = parse_json_resilient(output, max_attempts=max_retries + 1)
        
        if data is None:
            # Last resort: try to extract and provide helpful error
            extracted = extract_json_from_text(output)
            if extracted:
                try:
                    data = json.loads(extracted)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid JSON output from agent. "
                        f"Could not parse JSON even after extraction. "
                        f"Error: {e}. "
                        f"Raw output preview: {output[:200]}..."
                    ) from e
            else:
                raise ValueError(
                    f"Invalid JSON output from agent. "
                    f"Could not extract JSON from output. "
                    f"Raw output preview: {output[:200]}..."
                )
        
        # Validate against schema
        try:
            return expected_schema(**data)
        except Exception as e:
            raise ValueError(
                f"Output does not match expected schema {expected_schema.__name__}. "
                f"Error: {e}. "
                f"Parsed data: {data}"
            ) from e

