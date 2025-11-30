"""
Repository Layer - Data access abstraction

Repositories provide a way to access domain objects without exposing
the underlying data storage details. This is a key DDD pattern that:
1. Keeps the domain model independent of persistence
2. Provides a clean interface for data access
3. Enables easy testing with in-memory implementations
"""

from .claim_repository import ClaimRepository, InMemoryClaimRepository
from .policy_repository import PolicyRepository, InMemoryPolicyRepository

__all__ = [
    "ClaimRepository",
    "InMemoryClaimRepository",
    "PolicyRepository",
    "InMemoryPolicyRepository",
]

