"""
Domain Events for Policy Management Bounded Context
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from ..events import DomainEvent


class PolicyValidated(DomainEvent):
    """
    Domain Event: Policy validation completed.
    
    This event is published by the Policy Validation Agent after checking
    if a claim is covered by an active policy. It triggers the triage process.
    """
    
    claim_id: UUID = Field(description="ID of the claim that was validated")
    policy_id: Optional[UUID] = Field(default=None, description="ID of the policy if found")
    is_valid: bool = Field(description="Whether the claim is covered by a valid policy")
    validated_at: datetime = Field(default_factory=datetime.utcnow, description="When validation occurred")
    validation_reason: Optional[str] = Field(default=None, description="Reason for validation result")

