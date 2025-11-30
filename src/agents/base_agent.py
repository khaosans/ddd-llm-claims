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
to perform that task intelligently through prompt engineering techniques.

DDD Pattern: Anti-Corruption Layer - Agents protect the domain from messy
external data and API changes, translating them into clean domain models.

Prompt Engineering Research:
- Brown et al. (2020): Few-shot learning with language models
- Wei et al. (2022): Chain-of-thought prompting
- Ouyang et al. (2022): Instruction following (InstructGPT)
- Kojima et al. (2022): Zero-shot reasoning
- Zhou et al. (2022): Least-to-most prompting
- White et al. (2023): Prompt patterns catalog

See: docs/REFERENCES.md#llmai-agents--prompt-engineering
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
        that make the LLM act as a domain expert (Brown et al., 2020;
        Ouyang et al., 2022).
        
        This implements instruction-following patterns (Ouyang et al., 2022)
        and can incorporate chain-of-thought reasoning (Wei et al., 2022)
        or least-to-most prompting strategies (Zhou et al., 2022) as needed.
        
        References:
        - Brown et al. (2020): Few-shot learning
        - Ouyang et al. (2022): Instruction following
        - Wei et al. (2022): Chain-of-thought prompting
        - White et al. (2023): Prompt patterns
        
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
    
    def validate_output(self, output: str, expected_schema: type, max_retries: int = 3) -> Any:
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
        
        # Progressive normalization and validation with retries
        return self._validate_with_auto_fix(data, expected_schema, max_retries)
    
    def _validate_with_auto_fix(self, data: Dict[str, Any], schema: type, max_retries: int) -> Any:
        """
        Validate data with progressive auto-fixing strategies.
        
        Tries multiple normalization strategies in order of aggressiveness:
        1. Basic numeric cleaning
        2. Full data normalization
        3. Aggressive auto-fix
        4. Final attempt with all fixes
        
        Args:
            data: Parsed JSON data
            schema: Pydantic model class
            max_retries: Maximum retry attempts
            
        Returns:
            Validated domain object
            
        Raises:
            ValueError: If validation fails after all attempts
        """
        from .data_normalizer import DataNormalizer
        
        last_error = None
        strategies = [
            # Strategy 1: Basic numeric cleaning (least aggressive)
            lambda d: self._clean_numeric_strings(d, schema),
            
            # Strategy 2: Full normalization (moderate)
            lambda d: DataNormalizer.normalize_data(d, schema),
            
            # Strategy 3: Auto-fix common issues (more aggressive)
            lambda d: DataNormalizer.auto_fix_common_issues(d, schema),
            
            # Strategy 4: Combined approach (most aggressive)
            lambda d: DataNormalizer.normalize_data(
                DataNormalizer.auto_fix_common_issues(d, schema), 
                schema
            ),
        ]
        
        for attempt_num, normalize_strategy in enumerate(strategies[:max_retries + 1]):
            try:
                # Apply normalization strategy
                normalized_data = normalize_strategy(data)
                
                # Try validation
                return schema(**normalized_data)
                
            except Exception as e:
                last_error = e
                # If this is the last attempt, don't continue
                if attempt_num >= max_retries:
                    break
                # Otherwise, continue to next strategy
                continue
        
        # All strategies failed - provide detailed error
        raise ValueError(
            f"Output does not match expected schema {schema.__name__} after {max_retries + 1} normalization attempts. "
            f"Last error: {last_error}. "
            f"Parsed data: {data}"
        ) from last_error
    
    def _clean_numeric_strings(self, data: Dict[str, Any], schema: type) -> Dict[str, Any]:
        """
        Clean numeric string fields by removing commas and other formatting.
        
        This handles cases where LLMs return formatted numbers like '57,500.00'
        which Pydantic Decimal fields can't parse directly.
        
        Args:
            data: Dictionary of parsed JSON data
            schema: Pydantic model class to check field types
        
        Returns:
            Cleaned data dictionary
        """
        from decimal import Decimal
        from pydantic import BaseModel
        import typing
        
        if not isinstance(data, dict) or not issubclass(schema, BaseModel):
            return data
        
        cleaned_data = data.copy()
        
        # Get schema fields (Pydantic v2)
        schema_fields = schema.model_fields if hasattr(schema, 'model_fields') else {}
        
        # Known numeric field names (fallback if type checking fails)
        numeric_field_names = {'amount', 'cost', 'price', 'value', 'score', 'confidence', 
                              'fraud_score', 'claimed_amount', 'coverage_amount', 'limit'}
        
        for field_name, field_info in schema_fields.items():
            if field_name in cleaned_data:
                value = cleaned_data[field_name]
                
                if not isinstance(value, str):
                    continue
                
                # Check if this looks like a numeric string
                is_numeric_string = False
                
                # Check field type annotation
                field_type = getattr(field_info, 'annotation', None)
                if field_type:
                    # Handle direct Decimal type
                    if field_type == Decimal:
                        is_numeric_string = True
                    # Handle Optional[Decimal] or Union types
                    elif hasattr(typing, 'get_origin') and typing.get_origin(field_type):
                        origin = typing.get_origin(field_type)
                        args = typing.get_args(field_type)
                        if Decimal in args:
                            is_numeric_string = True
                    # Handle old-style Union (Python < 3.10)
                    elif hasattr(field_type, '__origin__'):
                        if Decimal in getattr(field_type, '__args__', []):
                            is_numeric_string = True
                
                # Fallback: check field name
                if not is_numeric_string:
                    is_numeric_string = any(numeric_name in field_name.lower() 
                                           for numeric_name in numeric_field_names)
                
                # Clean the string if it's numeric
                if is_numeric_string:
                    # Remove commas, whitespace, keep decimal point and minus sign
                    cleaned_value = value.replace(',', '').strip()
                    # Validate it's a valid number format
                    try:
                        # Try to convert to float to validate format
                        float(cleaned_value)
                        cleaned_data[field_name] = cleaned_value
                    except (ValueError, TypeError):
                        # If conversion fails, leave as is (will be caught by Pydantic)
                        pass
        
        return cleaned_data

