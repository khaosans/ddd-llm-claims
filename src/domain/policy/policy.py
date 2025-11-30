"""
Policy - Aggregate (Supporting Domain)

In DDD, a Supporting Domain provides services to the Core Domain.
Policy Management is a Supporting Domain because it enables the Core
Domain (Claim Intake) to function, but it's not the primary business value.

Policy is an Aggregate Root in its own bounded context.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PolicyStatus(str, Enum):
    """Policy status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Policy(BaseModel):
    """
    Aggregate Root: Represents an insurance policy.
    
    This is part of the Policy Management bounded context (Supporting Domain).
    It's used by the Policy Validation Agent to check if a claim is covered.
    """
    
    policy_id: UUID = Field(description="Unique identifier for the policy")
    policy_number: str = Field(description="Human-readable policy number")
    customer_id: UUID = Field(description="ID of the policyholder")
    
    status: PolicyStatus = Field(description="Current status of the policy")
    policy_type: str = Field(description="Type of policy (auto, property, health, etc.)")
    
    # Coverage details
    coverage_start: datetime = Field(description="When coverage begins")
    coverage_end: datetime = Field(description="When coverage ends")
    max_coverage_amount: Decimal = Field(description="Maximum coverage amount")
    
    # Additional metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_active(self) -> bool:
        """
        Domain Logic: Check if policy is currently active.
        
        This is domain logic - business rules that belong in the domain model,
        not in application services or agents.
        """
        now = datetime.utcnow()
        return (
            self.status == PolicyStatus.ACTIVE
            and self.coverage_start <= now <= self.coverage_end
        )
    
    def covers_claim_type(self, claim_type: str) -> bool:
        """
        Domain Logic: Check if policy covers a specific claim type.
        
        Args:
            claim_type: Type of claim to check
        
        Returns:
            True if policy covers this claim type
        """
        # Simplified logic - in reality, this would be more complex
        return self.policy_type.lower() == claim_type.lower()
    
    def is_amount_covered(self, amount: Decimal) -> bool:
        """
        Domain Logic: Check if claim amount is within coverage limits.
        
        Args:
            amount: Claim amount to check
        
        Returns:
            True if amount is covered
        """
        return amount <= self.max_coverage_amount
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
            UUID: lambda v: str(v),
        }

