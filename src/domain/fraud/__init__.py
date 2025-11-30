"""
Fraud Assessment Domain - Subdomain (Bounded Context: Fraud Assessment)

This is a Subdomain - it's important but not core to the business.
It provides fraud detection capabilities to support the Core Domain.
"""

from .fraud import FraudCheckResult, FraudRiskLevel
from .events import FraudScoreCalculated

__all__ = ["FraudCheckResult", "FraudRiskLevel", "FraudScoreCalculated"]

