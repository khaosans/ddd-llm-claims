"""
Domain Events for Anomaly Detection Bounded Context
"""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from ..events import DomainEvent
from .anomaly import AnomalyResult


class AnomalyDetected(DomainEvent):
    """
    Domain Event: An anomaly has been detected.
    
    This event is published when anomaly detection identifies issues
    beyond fraud (data quality, policy mismatches, temporal patterns, etc.).
    It may trigger additional review or routing decisions.
    """
    
    claim_id: UUID = Field(description="ID of the claim with the anomaly")
    anomaly_result: AnomalyResult = Field(description="The anomaly detection result (Value Object)")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="When detection occurred")


