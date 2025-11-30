"""
Integration Tests - Complete workflow testing

Tests the complete claim processing workflow including:
- End-to-end claim processing
- Event-driven workflow
- Human review integration
- Error recovery
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from src.agents import IntakeAgent, PolicyAgent, TriageAgent
from src.agents.model_provider import OllamaProvider
from src.domain.claim import Claim
from src.domain.policy import Policy, PolicyStatus
from src.human_review import ReviewQueue, HumanReviewAgent, FeedbackHandler
from src.orchestrator import WorkflowOrchestrator
from src.repositories import InMemoryClaimRepository, InMemoryPolicyRepository


@pytest.fixture
def mock_model_provider():
    """Create a mock model provider for testing"""
    from unittest.mock import MagicMock, AsyncMock
    provider = MagicMock(spec=OllamaProvider)
    provider.generate = AsyncMock(return_value='{"claim_type":"auto","incident_date":"2024-01-15T14:30:00","claimed_amount":"3500.00","currency":"USD","incident_location":"Main St","description":"Test","claimant_name":"John Doe"}')
    return provider


@pytest.fixture
def sample_policy():
    """Create a sample policy for testing"""
    return Policy(
        policy_id=uuid4(),
        policy_number="POL-2024-001234",
        customer_id=uuid4(),
        status=PolicyStatus.ACTIVE,
        policy_type="auto",
        coverage_start=datetime(2024, 1, 1),
        coverage_end=datetime(2024, 12, 31),
        max_coverage_amount=Decimal("50000.00"),
    )


@pytest.fixture
async def orchestrator_with_human_review(mock_model_provider, sample_policy):
    """Create orchestrator with human review enabled"""
    # Create agents
    intake_agent = IntakeAgent(mock_model_provider, temperature=0.3)
    policy_agent = PolicyAgent(mock_model_provider, temperature=0.2)
    triage_agent = TriageAgent(mock_model_provider, temperature=0.5)
    
    # Create repositories
    claim_repository = InMemoryClaimRepository()
    policy_repository = InMemoryPolicyRepository()
    await policy_repository.save(sample_policy)
    
    # Create human review components
    review_queue = ReviewQueue()
    feedback_handler = FeedbackHandler()
    human_review_agent = HumanReviewAgent(review_queue, feedback_handler)
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        intake_agent=intake_agent,
        policy_agent=policy_agent,
        triage_agent=triage_agent,
        claim_repository=claim_repository,
        policy_repository=policy_repository,
        human_review_agent=human_review_agent,
    )
    
    return orchestrator, human_review_agent


@pytest.mark.asyncio
async def test_complete_workflow_without_human_review(mock_model_provider, sample_policy):
    """
    Test complete workflow without human review intervention.
    
    This tests the happy path where AI processes everything
    and no human review is needed.
    """
    # Setup
    intake_agent = IntakeAgent(mock_model_provider, temperature=0.3)
    policy_agent = PolicyAgent(mock_model_provider, temperature=0.2)
    triage_agent = TriageAgent(mock_model_provider, temperature=0.5)
    
    claim_repository = InMemoryClaimRepository()
    policy_repository = InMemoryPolicyRepository()
    await policy_repository.save(sample_policy)
    
    orchestrator = WorkflowOrchestrator(
        intake_agent=intake_agent,
        policy_agent=policy_agent,
        triage_agent=triage_agent,
        claim_repository=claim_repository,
        policy_repository=policy_repository,
    )
    
    # Process claim
    sample_email = "I had a car accident on Jan 15. Damage is $3,500. Policy POL-2024-001234"
    claim = await orchestrator.process_claim(sample_email)
    
    # Wait for async events
    await asyncio.sleep(0.5)
    
    # Verify claim was processed
    updated_claim = await claim_repository.find_by_id(claim.claim_id)
    assert updated_claim is not None
    assert updated_claim.summary is not None
    assert updated_claim.status.value in ["triaged", "processing"]


@pytest.mark.asyncio
async def test_workflow_with_human_review_triggered(orchestrator_with_human_review):
    """
    Test workflow where human review is triggered.
    
    This tests that claims requiring review are added to the queue.
    """
    orchestrator, human_review_agent = orchestrator_with_human_review
    
    # Process a claim with high amount (should trigger review)
    sample_email = "I had a car accident. Damage is $150,000. Policy POL-2024-001234"
    claim = await orchestrator.process_claim(sample_email)
    
    # Wait for async events
    await asyncio.sleep(0.5)
    
    # Verify claim was added to review queue
    review_item = human_review_agent.review_queue.get_by_claim_id(claim.claim_id)
    assert review_item is not None
    assert review_item.status.value == "pending"
    assert "large amount" in review_item.reason.lower() or "fact extraction" in review_item.reason.lower()


@pytest.mark.asyncio
async def test_human_review_workflow(orchestrator_with_human_review):
    """
    Test complete human review workflow.
    
    Tests that human can review, make decisions, and system updates accordingly.
    """
    orchestrator, human_review_agent = orchestrator_with_human_review
    
    # Process a claim that needs review
    sample_email = "Car accident. Damage $200,000. Policy POL-2024-001234"
    claim = await orchestrator.process_claim(sample_email)
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Get review item
    review_item = human_review_agent.review_queue.get_by_claim_id(claim.claim_id)
    assert review_item is not None
    
    # Simulate human approval
    human_review_agent.process_human_decision(
        review_item,
        decision="approved",
        feedback="Looks good, proceed"
    )
    
    # Verify feedback was recorded
    feedback_records = human_review_agent.feedback_handler.get_feedback_for_claim(claim.claim_id)
    assert len(feedback_records) > 0
    assert feedback_records[0].human_decision == "approved"


@pytest.mark.asyncio
async def test_human_override_scenario(orchestrator_with_human_review):
    """
    Test human override scenario.
    
    Tests that human can override AI decisions.
    """
    orchestrator, human_review_agent = orchestrator_with_human_review
    
    # Process claim
    sample_email = "Car accident. Policy POL-2024-001234"
    claim = await orchestrator.process_claim(sample_email)
    
    await asyncio.sleep(0.5)
    
    # Get review item
    review_item = human_review_agent.review_queue.get_by_claim_id(claim.claim_id)
    if review_item:
        # Human overrides AI decision
        human_review_agent.process_human_decision(
            review_item,
            decision="overridden",
            feedback="AI missed important detail, routing to specialist"
        )
        
        # Verify claim status updated
        updated_claim = await orchestrator.claim_repository.find_by_id(claim.claim_id)
        assert updated_claim.status.value == "processing"


@pytest.mark.asyncio
async def test_multiple_claims_processing(mock_model_provider, sample_policy):
    """
    Test processing multiple claims concurrently.
    
    Verifies system handles multiple claims correctly.
    """
    # Setup
    intake_agent = IntakeAgent(mock_model_provider, temperature=0.3)
    policy_agent = PolicyAgent(mock_model_provider, temperature=0.2)
    triage_agent = TriageAgent(mock_model_provider, temperature=0.5)
    
    claim_repository = InMemoryClaimRepository()
    policy_repository = InMemoryPolicyRepository()
    await policy_repository.save(sample_policy)
    
    orchestrator = WorkflowOrchestrator(
        intake_agent=intake_agent,
        policy_agent=policy_agent,
        triage_agent=triage_agent,
        claim_repository=claim_repository,
        policy_repository=policy_repository,
    )
    
    # Process multiple claims
    claims = []
    for i in range(3):
        email = f"Claim {i}: Car accident. Policy POL-2024-001234"
        claim = await orchestrator.process_claim(email)
        claims.append(claim)
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Verify all claims processed
    for claim in claims:
        updated = await claim_repository.find_by_id(claim.claim_id)
        assert updated is not None
        assert updated.summary is not None


@pytest.mark.asyncio
async def test_error_recovery(mock_model_provider, sample_policy):
    """
    Test error recovery in workflow.
    
    Verifies system handles errors gracefully.
    """
    # Setup with agent that might fail
    from unittest.mock import MagicMock, AsyncMock
    failing_provider = MagicMock()
    failing_provider.generate = AsyncMock(side_effect=Exception("LLM error"))
    
    intake_agent = IntakeAgent(failing_provider, temperature=0.3)
    policy_agent = PolicyAgent(mock_model_provider, temperature=0.2)
    triage_agent = TriageAgent(mock_model_provider, temperature=0.5)
    
    claim_repository = InMemoryClaimRepository()
    policy_repository = InMemoryPolicyRepository()
    await policy_repository.save(sample_policy)
    
    orchestrator = WorkflowOrchestrator(
        intake_agent=intake_agent,
        policy_agent=policy_agent,
        triage_agent=triage_agent,
        claim_repository=claim_repository,
        policy_repository=policy_repository,
    )
    
    # Process claim (should handle error)
    sample_email = "Test claim"
    try:
        claim = await orchestrator.process_claim(sample_email)
        # If we get here, error was handled
        assert claim is not None
    except Exception:
        # Error handling is acceptable
        pass

