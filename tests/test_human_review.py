"""
Human Review Tests

Tests for human-in-the-loop functionality including:
- Review queue operations
- Human override scenarios
- Feedback capture
- Review workflow
"""

import pytest
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from src.domain.claim import Claim, ClaimStatus
from src.domain.fraud import FraudCheckResult, FraudRiskLevel
from src.human_review import (
    ReviewQueue,
    ReviewItem,
    ReviewStatus,
    ReviewPriority,
    HumanReviewAgent,
    FeedbackHandler,
    ReviewInterface,
)
from src.repositories import InMemoryClaimRepository


def test_review_queue_add_and_retrieve():
    """Test adding and retrieving items from review queue"""
    queue = ReviewQueue()
    
    claim = Claim(raw_input="Test", source="test")
    
    # Add item
    item = queue.add_for_review(
        claim=claim,
        reason="Test reason",
        ai_decision="Test decision",
        priority=ReviewPriority.HIGH,
    )
    
    assert item is not None
    assert item.status == ReviewStatus.PENDING
    assert item.priority == ReviewPriority.HIGH
    
    # Retrieve
    retrieved = queue.get_by_claim_id(claim.claim_id)
    assert retrieved == item
    
    # Get next pending
    next_item = queue.get_next_pending()
    assert next_item == item


def test_review_queue_priority_ordering():
    """Test that review queue orders by priority"""
    queue = ReviewQueue()
    
    claim1 = Claim(raw_input="Test 1", source="test")
    claim2 = Claim(raw_input="Test 2", source="test")
    claim3 = Claim(raw_input="Test 3", source="test")
    
    # Add items with different priorities
    queue.add_for_review(claim1, "Reason 1", "Decision 1", ReviewPriority.LOW)
    queue.add_for_review(claim2, "Reason 2", "Decision 2", ReviewPriority.URGENT)
    queue.add_for_review(claim3, "Reason 3", "Decision 3", ReviewPriority.MEDIUM)
    
    # Get next should return URGENT first
    next_item = queue.get_next_pending()
    assert next_item.priority == ReviewPriority.URGENT


def test_review_queue_assignment():
    """Test assigning review items to reviewers"""
    queue = ReviewQueue()
    
    claim = Claim(raw_input="Test", source="test")
    item = queue.add_for_review(claim, "Reason", "Decision")
    
    # Assign
    queue.assign(item, "reviewer1")
    
    assert item.assigned_to == "reviewer1"
    assert item.status == ReviewStatus.IN_REVIEW


def test_review_queue_completion():
    """Test completing a review"""
    queue = ReviewQueue()
    
    claim = Claim(raw_input="Test", source="test")
    item = queue.add_for_review(claim, "Reason", "Decision")
    
    # Complete review
    queue.complete_review(item, "approved", "Looks good")
    
    assert item.status == ReviewStatus.APPROVED
    assert item.human_decision == "approved"
    assert item.human_feedback == "Looks good"
    assert item.reviewed_at is not None


def test_human_review_agent_should_review_after_extraction():
    """Test human review agent decision logic for fact extraction"""
    queue = ReviewQueue()
    agent = HumanReviewAgent(queue)
    
    # Claim with large amount should need review
    claim = Claim(raw_input="Test", source="test")
    from src.domain.claim.claim_summary import ClaimSummary
    claim.summary = ClaimSummary(
        claim_type="auto",
        incident_date=datetime(2024, 1, 15, 14, 30),
        claimed_amount=Decimal("150000"),  # Large amount
        currency="USD",
        incident_location="Test",
        description="Test",
        claimant_name="Test",
    )
    
    assert agent.should_review_after_extraction(claim) is True
    
    # Claim with normal amount should not need review
    claim.summary.claimed_amount = Decimal("5000")
    assert agent.should_review_after_extraction(claim) is False


def test_human_review_agent_should_review_after_policy_validation():
    """Test human review agent decision logic for policy validation"""
    queue = ReviewQueue()
    agent = HumanReviewAgent(queue)
    
    claim = Claim(raw_input="Test", source="test")
    
    # Invalid policy should need review
    assert agent.should_review_after_policy_validation(claim, False) is True
    
    # Valid policy might not need review
    assert agent.should_review_after_policy_validation(claim, True) is False


def test_human_review_agent_should_review_after_fraud_assessment():
    """Test human review agent decision logic for fraud assessment"""
    queue = ReviewQueue()
    agent = HumanReviewAgent(queue)
    
    claim = Claim(raw_input="Test", source="test")
    from src.domain.claim.claim_summary import ClaimSummary
    claim.summary = ClaimSummary(
        claim_type="auto",
        incident_date=datetime(2024, 1, 15, 14, 30),
        claimed_amount=Decimal("10000"),
        currency="USD",
        incident_location="Test",
        description="Test",
        claimant_name="Test",
    )
    
    # High fraud score should need review
    high_fraud = FraudCheckResult(
        fraud_score=Decimal("0.8"),
        risk_level=FraudRiskLevel.HIGH,
        is_suspicious=True,
        risk_factors=["High amount"],
        assessment_method="test",
    )
    assert agent.should_review_after_fraud_assessment(claim, high_fraud) is True
    
    # Low fraud score should not need review
    low_fraud = FraudCheckResult(
        fraud_score=Decimal("0.2"),
        risk_level=FraudRiskLevel.LOW,
        is_suspicious=False,
        risk_factors=[],
        assessment_method="test",
    )
    assert agent.should_review_after_fraud_assessment(claim, low_fraud) is False


def test_feedback_handler_record_feedback():
    """Test recording feedback"""
    handler = FeedbackHandler()
    queue = ReviewQueue()
    
    claim = Claim(raw_input="Test", source="test")
    item = queue.add_for_review(claim, "Reason", "AI Decision")
    queue.complete_review(item, "approved", "Good decision")
    
    # Record feedback
    record = handler.record_feedback(item)
    
    assert record is not None
    assert record.ai_decision == "AI Decision"
    assert record.human_decision == "approved"
    assert record.human_feedback == "Good decision"


def test_feedback_handler_analytics():
    """Test feedback analytics"""
    handler = FeedbackHandler()
    queue = ReviewQueue()
    
    # Create multiple review items
    for i in range(5):
        claim = Claim(raw_input=f"Test {i}", source="test")
        item = queue.add_for_review(claim, f"Reason {i}", f"Decision {i}")
        decision = "approved" if i < 3 else "rejected"
        queue.complete_review(item, decision, f"Feedback {i}")
        handler.record_feedback(item)
    
    # Get analytics
    patterns = handler.get_override_patterns()
    
    assert patterns["total_reviews"] == 5
    assert patterns["approvals"] == 3
    assert patterns["rejections"] == 2


def test_human_review_agent_process_decision():
    """Test processing human decisions"""
    queue = ReviewQueue()
    handler = FeedbackHandler()
    agent = HumanReviewAgent(queue, handler)
    
    claim = Claim(raw_input="Test", source="test")
    item = queue.add_for_review(claim, "Reason", "AI Decision")
    
    # Process human decision
    agent.process_human_decision(item, "rejected", "Invalid claim")
    
    # Verify claim status updated
    assert claim.status == ClaimStatus.REJECTED
    
    # Verify feedback recorded
    feedback = handler.get_feedback_for_claim(claim.claim_id)
    assert len(feedback) > 0
    assert feedback[0].human_decision == "rejected"


def test_review_interface_display():
    """Test review interface can display items"""
    queue = ReviewQueue()
    interface = ReviewInterface(queue)
    
    claim = Claim(raw_input="Test", source="test")
    item = queue.add_for_review(claim, "Test reason", "Test decision")
    
    # Interface should be able to display
    # (In real test, we'd capture stdout)
    assert interface is not None
    assert interface.review_queue == queue

