"""
Fraud Assessment - Subdomain

In DDD, a Subdomain is important but not core to the business.
Fraud Assessment is a Subdomain because it supports the Core Domain
but isn't the primary business value.

FraudCheckResult is a Value Object representing fraud assessment results.
"""

from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class FraudRiskLevel(str, Enum):
    """Fraud risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FraudCheckResult(BaseModel):
    """
    Value Object: Result of fraud assessment.
    
    This represents the output of fraud detection (whether from an LLM agent
    or an ML model). It's a Value Object because it's defined by its attributes
    and has no identity of its own.
    """
    
    fraud_score: Decimal = Field(
        description="Fraud score from 0.0 to 1.0 (higher = more suspicious)",
        ge=0,
        le=1
    )
    risk_level: FraudRiskLevel = Field(description="Categorized risk level")
    is_suspicious: bool = Field(description="Whether the claim is flagged as suspicious")
    
    # Details
    risk_factors: List[str] = Field(default_factory=list, description="List of risk factors identified")
    assessment_method: str = Field(default="llm_agent", description="Method used (llm_agent, ml_model, etc.)")
    confidence: Optional[Decimal] = Field(default=None, description="Confidence in the assessment", ge=0, le=1)
    
    @field_validator('risk_level')
    @classmethod
    def validate_risk_level(cls, v: FraudRiskLevel, info) -> FraudRiskLevel:
        """
        Domain Logic: Risk level should match fraud score.
        
        This enforces consistency between the numeric score and categorical level.
        """
        if 'fraud_score' in info.data:
            score = info.data['fraud_score']
            if score < 0.3 and v != FraudRiskLevel.LOW:
                raise ValueError("Risk level should be LOW for scores < 0.3")
            elif 0.3 <= score < 0.6 and v not in [FraudRiskLevel.LOW, FraudRiskLevel.MEDIUM]:
                raise ValueError("Risk level should be LOW or MEDIUM for scores 0.3-0.6")
            elif 0.6 <= score < 0.8 and v not in [FraudRiskLevel.MEDIUM, FraudRiskLevel.HIGH]:
                raise ValueError("Risk level should be MEDIUM or HIGH for scores 0.6-0.8")
            elif score >= 0.8 and v != FraudRiskLevel.HIGH:
                raise ValueError("Risk level should be HIGH for scores >= 0.8")
        return v
    
    @field_validator('is_suspicious')
    @classmethod
    def validate_suspicious_flag(cls, v: bool, info) -> bool:
        """
        Domain Logic: Suspicious flag should align with risk level.
        
        This is a business rule: high or critical risk should be flagged as suspicious.
        """
        if 'risk_level' in info.data:
            risk_level = info.data['risk_level']
            if risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL] and not v:
                raise ValueError("High or critical risk must be flagged as suspicious")
        return v
    
    class Config:
        frozen = True  # Value Objects are immutable
        json_encoders = {
            Decimal: lambda v: str(v),
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return self.model_dump()

