"""
Vector Store Module - ChromaDB integration for semantic search

This module provides vector database capabilities for:
- Semantic claim search
- Policy document matching
- Fraud pattern detection
"""

from .claim_vector_store import ClaimVectorStore
from .policy_vector_store import PolicyVectorStore
from .fraud_pattern_store import FraudPatternStore

__all__ = [
    "ClaimVectorStore",
    "PolicyVectorStore",
    "FraudPatternStore",
]

