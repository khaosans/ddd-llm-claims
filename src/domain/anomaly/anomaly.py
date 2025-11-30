"""
Anomaly Detection - Subdomain

In DDD, a Subdomain is important but not core to the business.
Anomaly Detection is a Subdomain because it supports the Core Domain
but isn't the primary business value.

AnomalyResult is a Value Object representing anomaly detection results.
"""

from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected"""
    FRAUD = "fraud"  # Intentional deception
    DATA_QUALITY = "data_quality"  # Missing/invalid data
    POLICY_MISMATCH = "policy_mismatch"  # Coverage/eligibility issues
    TEMPORAL_PATTERN = "temporal_pattern"  # Suspicious timing patterns
    AMOUNT_ANOMALY = "amount_anomaly"  # Unusual claim amounts
    BEHAVIORAL_PATTERN = "behavioral_pattern"  # Unusual claimant behavior


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AnomalyResult(BaseModel):
    """
    Value Object: Result of anomaly detection.
    
    This represents the output of anomaly detection (whether from an LLM agent
    or an ML model). It's a Value Object because it's defined by its attributes
    and has no identity of its own.
    """
    
    anomaly_type: AnomalyType = Field(description="Type of anomaly detected")
    severity: AnomalySeverity = Field(description="Severity level of the anomaly")
    confidence: Decimal = Field(
        description="Confidence in the detection (0.0 to 1.0)",
        ge=0,
        le=1
    )
    indicators: List[str] = Field(
        default_factory=list,
        description="List of indicators that led to this detection"
    )
    recommendation: str = Field(
        description="Recommended action based on the anomaly"
    )
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: Decimal) -> Decimal:
        """Ensure confidence is within valid range"""
        if v < 0 or v > 1:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v
    
    @field_validator('indicators')
    @classmethod
    def validate_indicators(cls, v: List[str]) -> List[str]:
        """Ensure at least one indicator is provided"""
        if not v:
            raise ValueError("At least one indicator must be provided")
        return v
    
    class Config:
        frozen = True  # Value Objects are immutable
        json_encoders = {
            Decimal: lambda v: str(v),
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return self.model_dump()

