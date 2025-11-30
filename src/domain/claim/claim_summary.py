"""
ClaimSummary - Value Object

In DDD, a Value Object is an immutable object defined by its attributes
rather than its identity. Two Value Objects are equal if all their
attributes are equal.

ClaimSummary represents the structured facts extracted from unstructured
customer data. It's a Value Object because:
1. It has no identity of its own (it's part of a Claim)
2. It's immutable (once created, it doesn't change)
3. It's defined by its attributes (all fields together define what it is)
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ClaimSummary(BaseModel):
    """
    Value Object: Structured summary of claim facts extracted from unstructured data.
    
    This is the output of the Intake Agent's fact extraction process.
    It represents the "ubiquitous language" - the shared vocabulary
    between domain experts and developers.
    
    DDD Principle: Value Objects are immutable and validated at creation.
    """
    
    # Core claim information
    claim_type: str = Field(description="Type of claim (e.g., 'auto', 'property', 'health')")
    incident_date: datetime = Field(description="When the incident occurred")
    reported_date: datetime = Field(default_factory=datetime.utcnow, description="When the claim was reported")
    
    # Financial information
    claimed_amount: Decimal = Field(description="Amount claimed by the customer", ge=0)
    currency: str = Field(default="USD", description="Currency code")
    
    # Location information
    incident_location: str = Field(description="Where the incident occurred")
    
    # Description
    description: str = Field(description="Structured description of the incident")
    
    # Parties involved
    claimant_name: str = Field(description="Name of the person filing the claim")
    claimant_email: Optional[str] = Field(default=None, description="Email of the claimant")
    claimant_phone: Optional[str] = Field(default=None, description="Phone number of the claimant")
    
    # Additional details
    policy_number: Optional[str] = Field(default=None, description="Policy number if mentioned")
    tags: List[str] = Field(default_factory=list, description="Tags or categories for the claim")
    
    # Document references
    document_ids: List[UUID] = Field(default_factory=list, description="IDs of supporting documents referenced in the claim")
    
    @field_validator('claimed_amount')
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        """
        Domain Invariant: Claim amount must be positive.
        
        In DDD, invariants are business rules that must always be true.
        Value Objects enforce invariants at creation time.
        """
        if v < 0:
            raise ValueError("Claim amount cannot be negative")
        return v
    
    @field_validator('incident_date')
    @classmethod
    def validate_incident_date(cls, v: datetime) -> datetime:
        """
        Domain Invariant: Incident date cannot be in the future.
        
        This is a business rule enforced by the domain model.
        """
        if v > datetime.utcnow():
            raise ValueError("Incident date cannot be in the future")
        return v
    
    class Config:
        frozen = True  # Immutability: Value Objects cannot be modified after creation
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v),
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return self.model_dump()

