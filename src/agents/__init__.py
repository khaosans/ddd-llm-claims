"""
Agents Module - LLM-powered domain agents

Agents act as Anti-Corruption Layers (ACL) that translate between
external systems (LLMs) and our domain model.
"""

from .base_agent import BaseAgent
from .intake_agent import IntakeAgent
from .policy_agent import PolicyAgent
from .triage_agent import TriageAgent
from .fraud_agent import FraudAgent
from .model_provider import ModelProvider, create_model_provider
from .json_utils import parse_json_resilient, extract_json_from_text

__all__ = [
    "BaseAgent",
    "IntakeAgent",
    "PolicyAgent",
    "TriageAgent",
    "FraudAgent",
    "ModelProvider",
    "create_model_provider",
    "parse_json_resilient",
    "extract_json_from_text",
]
