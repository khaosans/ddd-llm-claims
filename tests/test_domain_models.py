"""
Tests for Domain Models

These tests verify DDD patterns: Aggregates, Value Objects, Domain Events, and Invariants.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.claim import Claim, ClaimStatus, ClaimSummary
from src.domain.claim.events import ClaimFactsExtracted
from src.domain.policy import Policy, PolicyStatus
from src.domain.fraud import FraudCheckResult, FraudRiskLevel


def test_claim_summary_value_object():
    """
    Test that ClaimSummary is a proper Value Object.
    
    Value Objects:
    - Are immutable (frozen=True)
    - Are defined by their attributes
    - Enforce domain invariants
    """
    summary = ClaimSummary(
        claim_type="auto",
        incident_date=datetime(2024, 1, 15, 14, 30),
        claimed_amount=Decimal("3500.00"),
        currency="USD",
        incident_location="123 Main St",
        description="Test claim",
        claimant_name="John Doe",
    )
    
    # Verify immutability
    assert summary.frozen is True
    
    # Verify domain invariant: amount cannot be negative
    with pytest.raises(ValueError, match="cannot be negative"):
        ClaimSummary(
            claim_type="auto",
            incident_date=datetime(2024, 1, 15, 14, 30),
            claimed_amount=Decimal("-100.00"),  # Invalid
            currency="USD",
            incident_location="123 Main St",
            description="Test",
            claimant_name="John Doe",
        )
    
    # Verify domain invariant: incident date cannot be in future
    future_date = datetime.utcnow() + timedelta(days=1)
    with pytest.raises(ValueError, match="cannot be in the future"):
        ClaimSummary(
            claim_type="auto",
            incident_date=future_date,  # Invalid
            claimed_amount=Decimal("1000.00"),
            currency="USD",
            incident_location="123 Main St",
            description="Test",
            claimant_name="John Doe",
        )


def test_claim_aggregate_root():
    """
    Test that Claim is a proper Aggregate Root.
    
    Aggregate Roots:
    - Have unique identity
    - Enforce business invariants
    - Control access to related objects
    - Publish domain events
    """
    claim = Claim(
        raw_input="Test input",
        source="email",
    )
    
    # Verify identity
    assert claim.claim_id is not None
    assert claim.status == ClaimStatus.DRAFT
    
    # Create summary
    summary = ClaimSummary(
        claim_type="auto",
        incident_date=datetime(2024, 1, 15, 14, 30),
        claimed_amount=Decimal("3500.00"),
        currency="USD",
        incident_location="123 Main St",
        description="Test claim",
        claimant_name="John Doe",
    )
    
    # Extract facts (this should publish an event)
    event = claim.extract_facts(summary)
    
    # Verify aggregate was updated
    assert claim.summary == summary
    assert claim.status == ClaimStatus.FACTS_EXTRACTED
    
    # Verify domain event was created
    assert isinstance(event, ClaimFactsExtracted)
    assert event.summary == summary
    
    # Verify domain invariant: can only extract facts once
    with pytest.raises(ValueError, match="Cannot extract facts"):
        claim.extract_facts(summary)


def test_claim_status_transitions():
    """
    Test claim status transitions.
    
    This demonstrates state machine behavior in the aggregate.
    """
    claim = Claim(raw_input="Test", source="email")
    assert claim.status == ClaimStatus.DRAFT
    
    summary = ClaimSummary(
        claim_type="auto",
        incident_date=datetime(2024, 1, 15, 14, 30),
        claimed_amount=Decimal("1000.00"),
        currency="USD",
        incident_location="123 Main St",
        description="Test",
        claimant_name="John Doe",
    )
    
    # Extract facts
    claim.extract_facts(summary)
    assert claim.status == ClaimStatus.FACTS_EXTRACTED
    
    # Validate policy
    claim.validate_policy(True)
    assert claim.status == ClaimStatus.POLICY_VALIDATED
    
    # Triage
    claim.triage("human_adjudicator_queue")
    assert claim.status == ClaimStatus.TRIAGED


def test_policy_aggregate():
    """
    Test Policy aggregate domain logic.
    """
    policy = Policy(
        policy_id=uuid4(),
        policy_number="POL-2024-001234",
        customer_id=uuid4(),
        status=PolicyStatus.ACTIVE,
        policy_type="auto",
        coverage_start=datetime(2024, 1, 1),
        coverage_end=datetime(2024, 12, 31),
        max_coverage_amount=Decimal("50000.00"),
    )
    
    # Test domain logic: is_active
    assert policy.is_active() is True
    
    # Test domain logic: covers_claim_type
    assert policy.covers_claim_type("auto") is True
    assert policy.covers_claim_type("property") is False
    
    # Test domain logic: is_amount_covered
    assert policy.is_amount_covered(Decimal("10000.00")) is True
    assert policy.is_amount_covered(Decimal("60000.00")) is False


def test_fraud_check_result_value_object():
    """
    Test FraudCheckResult Value Object with domain invariants.
    """
    # Valid fraud result
    result = FraudCheckResult(
        fraud_score=Decimal("0.3"),
        risk_level=FraudRiskLevel.LOW,
        is_suspicious=False,
        risk_factors=[],
        assessment_method="llm_agent",
    )
    
    assert result.fraud_score == Decimal("0.3")
    assert result.risk_level == FraudRiskLevel.LOW
    
    # Test domain invariant: risk level must match score
    with pytest.raises(ValueError):
        FraudCheckResult(
            fraud_score=Decimal("0.9"),  # High score
            risk_level=FraudRiskLevel.LOW,  # But low risk level - invalid!
            is_suspicious=False,
            risk_factors=[],
            assessment_method="test",
        )
    
    # Test domain invariant: high risk must be suspicious
    with pytest.raises(ValueError):
        FraudCheckResult(
            fraud_score=Decimal("0.9"),
            risk_level=FraudRiskLevel.HIGH,
            is_suspicious=False,  # Should be True for high risk!
            risk_factors=[],
            assessment_method="test",
        )


def test_domain_events():
    """
    Test domain events are immutable and properly structured.
    """
    summary = ClaimSummary(
        claim_type="auto",
        incident_date=datetime(2024, 1, 15, 14, 30),
        claimed_amount=Decimal("1000.00"),
        currency="USD",
        incident_location="123 Main St",
        description="Test",
        claimant_name="John Doe",
    )
    
    event = ClaimFactsExtracted(
        claim_id=uuid4(),
        summary=summary,
    )
    
    # Verify event properties
    assert event.event_id is not None
    assert event.occurred_at is not None
    assert event.event_type == "ClaimFactsExtracted"
    assert event.summary == summary
    
    # Verify immutability
    assert event.frozen is True

