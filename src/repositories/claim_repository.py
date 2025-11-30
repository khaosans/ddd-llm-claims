"""
Claim Repository - Data access for Claim aggregates

In DDD, Repositories provide a way to retrieve and persist aggregates
without exposing persistence details. They act as a collection-like
interface for domain objects.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..domain.claim import Claim


class ClaimRepository(ABC):
    """
    Abstract repository interface for Claim aggregates.
    
    DDD Pattern: Repository provides a collection-like interface
    for domain objects, hiding persistence details from the domain.
    
    This abstraction allows:
    1. Easy testing with in-memory implementations
    2. Swapping persistence mechanisms (SQL, NoSQL, etc.)
    3. Keeping domain model independent of infrastructure
    """
    
    @abstractmethod
    async def save(self, claim: Claim) -> None:
        """
        Save a claim aggregate.
        
        Args:
            claim: The claim to save
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, claim_id: UUID) -> Optional[Claim]:
        """
        Find a claim by its ID.
        
        Args:
            claim_id: The claim's unique identifier
        
        Returns:
            The claim if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_all(self) -> List[Claim]:
        """
        Find all claims.
        
        Returns:
            List of all claims
        """
        pass
    
    @abstractmethod
    async def delete(self, claim_id: UUID) -> None:
        """
        Delete a claim.
        
        Args:
            claim_id: The claim's unique identifier
        """
        pass


class InMemoryClaimRepository(ClaimRepository):
    """
    In-memory implementation of ClaimRepository.
    
    This is useful for:
    - Testing
    - Development
    - Demonstrating the repository pattern
    
    In production, this would be replaced with a database-backed
    implementation (e.g., PostgreSQL, MongoDB, etc.)
    """
    
    def __init__(self):
        """Initialize the in-memory repository"""
        self._claims: dict[UUID, Claim] = {}
    
    async def save(self, claim: Claim) -> None:
        """
        Save a claim to the in-memory store.
        
        In a real implementation, this would:
        1. Serialize the aggregate
        2. Save to database
        3. Publish domain events
        4. Handle transactions
        """
        self._claims[claim.claim_id] = claim
    
    async def find_by_id(self, claim_id: UUID) -> Optional[Claim]:
        """Find a claim by ID"""
        return self._claims.get(claim_id)
    
    async def find_all(self) -> List[Claim]:
        """Find all claims"""
        return list(self._claims.values())
    
    async def delete(self, claim_id: UUID) -> None:
        """Delete a claim"""
        if claim_id in self._claims:
            del self._claims[claim_id]
    
    def clear(self) -> None:
        """Clear all claims (useful for testing)"""
        self._claims.clear()

