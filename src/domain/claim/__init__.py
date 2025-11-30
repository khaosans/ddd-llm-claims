"""
Claim Domain - Core Domain (Bounded Context: Claim Intake)

This is the Core Domain - the heart of the business.
It handles the extraction and structuring of claim information
from unstructured customer data.
"""

from .claim import Claim, ClaimStatus
from .claim_summary import ClaimSummary
from .events import ClaimFactsExtracted

__all__ = ["Claim", "ClaimStatus", "ClaimSummary", "ClaimFactsExtracted"]

