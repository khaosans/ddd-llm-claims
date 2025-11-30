"""
Decision Context Tracker

Captures and manages context for decisions including:
- Inputs and outputs
- LLM prompts and responses
- Intermediate processing steps
- Supporting evidence
- Decision dependencies
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from .models import DecisionContext, DecisionDependency


class DecisionContextTracker:
    """
    Tracks context and evidence for decisions.
    
    This class builds up context as a decision is being made,
    capturing all relevant information for explainability and debugging.
    """
    
    def __init__(self):
        """Initialize a new context tracker"""
        self._inputs: Dict[str, Any] = {}
        self._prompt: Optional[str] = None
        self._llm_response: Optional[str] = None
        self._intermediate_steps: List[Dict[str, Any]] = []
        self._evidence: List[Dict[str, Any]] = []
        self._metadata: Dict[str, Any] = {}
    
    def add_input(self, key: str, value: Any) -> None:
        """
        Add an input value to the context.
        
        Args:
            key: Name of the input
            value: Input value (will be serialized)
        """
        self._inputs[key] = self._serialize_value(value)
    
    def add_inputs(self, inputs: Dict[str, Any]) -> None:
        """
        Add multiple inputs at once.
        
        Args:
            inputs: Dictionary of input key-value pairs
        """
        for key, value in inputs.items():
            self.add_input(key, value)
    
    def set_prompt(self, prompt: str) -> None:
        """
        Set the LLM prompt used for this decision.
        
        Args:
            prompt: The prompt text
        """
        self._prompt = prompt
    
    def set_llm_response(self, response: str) -> None:
        """
        Set the raw LLM response.
        
        Args:
            response: The raw response text
        """
        self._llm_response = response
    
    def add_intermediate_step(self, step_name: str, step_data: Dict[str, Any]) -> None:
        """
        Add an intermediate processing step.
        
        Args:
            step_name: Name/description of the step
            step_data: Data associated with this step
        """
        self._intermediate_steps.append({
            "step": step_name,
            "data": self._serialize_value(step_data),
            "timestamp": self._get_timestamp(),
        })
    
    def add_evidence(self, evidence_type: str, evidence_data: Dict[str, Any]) -> None:
        """
        Add supporting evidence for the decision.
        
        Args:
            evidence_type: Type of evidence (e.g., "policy_check", "fraud_score")
            evidence_data: Evidence data
        """
        self._evidence.append({
            "type": evidence_type,
            "data": self._serialize_value(evidence_data),
            "timestamp": self._get_timestamp(),
        })
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the context.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata[key] = self._serialize_value(value)
    
    def build_context(self) -> DecisionContext:
        """
        Build the final DecisionContext object.
        
        Returns:
            DecisionContext with all captured information
        """
        return DecisionContext(
            inputs=self._inputs.copy(),
            prompts=self._prompt,
            llm_response=self._llm_response,
            intermediate_steps=self._intermediate_steps.copy(),
            evidence=self._evidence.copy(),
            metadata=self._metadata.copy(),
        )
    
    def reset(self) -> None:
        """Reset the tracker for a new decision"""
        self._inputs.clear()
        self._prompt = None
        self._llm_response = None
        self._intermediate_steps.clear()
        self._evidence.clear()
        self._metadata.clear()
    
    def _serialize_value(self, value: Any) -> Any:
        """
        Serialize a value for storage.
        
        Handles common types that need serialization.
        
        Args:
            value: Value to serialize
            
        Returns:
            Serialized value
        """
        # Handle common serializable types
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        
        # Handle UUID
        if isinstance(value, UUID):
            return str(value)
        
        # Handle dict - recursively serialize
        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        
        # Handle list - recursively serialize
        if isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        
        # Handle objects with model_dump (Pydantic models)
        if hasattr(value, "model_dump"):
            return value.model_dump()
        
        # Handle objects with dict method
        if hasattr(value, "__dict__"):
            return {k: self._serialize_value(v) for k, v in value.__dict__.items()}
        
        # Fallback to string representation
        return str(value)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


def create_dependency(
    decision_id: UUID,
    dependency_type: str = "required_for",
    description: Optional[str] = None,
) -> DecisionDependency:
    """
    Helper function to create a decision dependency.
    
    Args:
        decision_id: ID of the decision this depends on
        dependency_type: Type of dependency
        description: Optional description
        
    Returns:
        DecisionDependency object
    """
    return DecisionDependency(
        decision_id=decision_id,
        dependency_type=dependency_type,
        description=description,
    )

