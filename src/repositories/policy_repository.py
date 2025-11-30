"""
Policy Repository - Data access for Policy aggregates

Policy Repository provides access to policies for validation purposes.
This is part of the Policy Management bounded context (Supporting Domain).
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..domain.policy import Policy


class PolicyRepository(ABC):
    """
    Abstract repository interface for Policy aggregates.
    
    DDD Pattern: Repository provides a collection-like interface
    for accessing policies without exposing storage details.
    """
    
    @abstractmethod
    async def save(self, policy: Policy) -> None:
        """
        Save a policy aggregate.
        
        Args:
            policy: The policy to save
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, policy_id: UUID) -> Optional[Policy]:
        """
        Find a policy by its ID.
        
        Args:
            policy_id: The policy's unique identifier
        
        Returns:
            The policy if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_by_policy_number(self, policy_number: str) -> Optional[Policy]:
        """
        Find a policy by its policy number.
        
        Args:
            policy_number: The human-readable policy number
        
        Returns:
            The policy if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_by_customer_id(self, customer_id: UUID) -> List[Policy]:
        """
        Find all policies for a customer.
        
        Args:
            customer_id: The customer's unique identifier
        
        Returns:
            List of policies for the customer
        """
        pass
    
    @abstractmethod
    async def find_active_policies(self) -> List[Policy]:
        """
        Find all active policies.
        
        Returns:
            List of active policies
        """
        pass
    
    @abstractmethod
    async def find_all(self) -> List[Policy]:
        """
        Find all policies.
        
        Returns:
            List of all policies
        """
        pass


class InMemoryPolicyRepository(PolicyRepository):
    """
    In-memory implementation of PolicyRepository.
    
    Useful for testing and development. In production, this would
    be replaced with a database-backed implementation.
    """
    
    def __init__(self):
        """Initialize the in-memory repository"""
        self._policies: dict[UUID, Policy] = {}
        self._by_policy_number: dict[str, UUID] = {}
        self._by_customer: dict[UUID, list[UUID]] = {}
    
    async def save(self, policy: Policy) -> None:
        """Save a policy to the in-memory store"""
        self._policies[policy.policy_id] = policy
        self._by_policy_number[policy.policy_number] = policy.policy_id
        
        if policy.customer_id not in self._by_customer:
            self._by_customer[policy.customer_id] = []
        if policy.policy_id not in self._by_customer[policy.customer_id]:
            self._by_customer[policy.customer_id].append(policy.policy_id)
    
    async def find_by_id(self, policy_id: UUID) -> Optional[Policy]:
        """Find a policy by ID"""
        return self._policies.get(policy_id)
    
    async def find_by_policy_number(self, policy_number: str) -> Optional[Policy]:
        """Find a policy by policy number"""
        policy_id = self._by_policy_number.get(policy_number)
        if policy_id:
            return self._policies.get(policy_id)
        return None
    
    async def find_by_customer_id(self, customer_id: UUID) -> List[Policy]:
        """Find all policies for a customer"""
        policy_ids = self._by_customer.get(customer_id, [])
        return [self._policies[pid] for pid in policy_ids if pid in self._policies]
    
    async def find_active_policies(self) -> List[Policy]:
        """Find all active policies"""
        from ..domain.policy import PolicyStatus
        return [
            policy for policy in self._policies.values()
            if policy.status == PolicyStatus.ACTIVE
        ]
    
    async def find_all(self) -> List[Policy]:
        """Find all policies"""
        return list(self._policies.values())
    
    def clear(self) -> None:
        """Clear all policies (useful for testing)"""
        self._policies.clear()
        self._by_policy_number.clear()
        self._by_customer.clear()

