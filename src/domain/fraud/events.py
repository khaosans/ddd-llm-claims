"""
Domain Events for Fraud Assessment Bounded Context
"""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from ..events import DomainEvent
from .fraud import FraudCheckResult


class FraudScoreCalculated(DomainEvent):
    """
    Domain Event: Fraud score has been calculated.
    
    This event is published when fraud assessment is complete.
    It triggers the triage and routing process, which may route
    high-risk claims to special handling queues.
    """
    
    claim_id: UUID = Field(description="ID of the claim that was assessed")
    fraud_result: FraudCheckResult = Field(description="The fraud assessment result (Value Object)")
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="When calculation occurred")

