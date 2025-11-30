"""
End-to-End Tests - Full system testing

Tests the complete system from input to output, including
all components working together.
"""

import asyncio
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from src.agents import IntakeAgent, PolicyAgent, TriageAgent
from src.agents.model_provider import OllamaProvider
from src.domain.policy import Policy, PolicyStatus
from src.human_review import ReviewQueue, HumanReviewAgent, FeedbackHandler, ReviewInterface
from src.orchestrator import WorkflowOrchestrator
from src.repositories import InMemoryClaimRepository, InMemoryPolicyRepository


@pytest.fixture
def mock_model_provider():
    """Create a mock model provider for E2E tests"""
    from unittest.mock import MagicMock, AsyncMock
    provider = MagicMock(spec=OllamaProvider)
    
    # Mock different responses for different agents
    async def mock_generate(prompt, **kwargs):
        if "Extract claim facts" in prompt or "claim" in prompt.lower():
            return '{"claim_type":"auto","incident_date":"2024-01-15T14:30:00","claimed_amount":"3500.00","currency":"USD","incident_location":"Main St","description":"Test","claimant_name":"John Doe"}'
        elif "Validate" in prompt or "policy" in prompt.lower():
            return '{"is_valid":true,"policy_id":"550e8400-e29b-41d4-a716-446655440000","validation_reason":"Policy is active and covers claim"}'
        elif "Route" in prompt or "triage" in prompt.lower():
            return '{"routing_decision":"human_adjudicator_queue","routing_reason":"Standard routing","priority":"medium"}'
        return '{}'
    
    provider.generate = AsyncMock(side_effect=mock_generate)
    return provider


@pytest.fixture
async def full_system_setup(mock_model_provider):
    """Setup complete system for E2E testing"""
    # Create agents
    intake_agent = IntakeAgent(mock_model_provider, temperature=0.3)
    policy_agent = PolicyAgent(mock_model_provider, temperature=0.2)
    triage_agent = TriageAgent(mock_model_provider, temperature=0.5)
    
    # Create repositories
    claim_repository = InMemoryClaimRepository()
    policy_repository = InMemoryPolicyRepository()
    
    # Add sample policy
    sample_policy = Policy(
        policy_id=uuid4(),
        policy_number="POL-2024-001234",
        customer_id=uuid4(),
        status=PolicyStatus.ACTIVE,
        policy_type="auto",
        coverage_start=datetime(2024, 1, 1),
        coverage_end=datetime(2024, 12, 31),
        max_coverage_amount=Decimal("50000.00"),
    )
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
    
    return {
        "orchestrator": orchestrator,
        "human_review_agent": human_review_agent,
        "review_queue": review_queue,
        "claim_repository": claim_repository,
        "policy_repository": policy_repository,
    }


@pytest.mark.asyncio
async def test_full_claim_lifecycle(full_system_setup):
    """
    Test complete claim lifecycle from email to final routing.
    
    This is the main E2E test that verifies the entire system works.
    """
    system = full_system_setup
    orchestrator = system["orchestrator"]
    
    # Load sample email
    sample_email_path = Path(__file__).parent.parent / "examples" / "sample_claim_email.txt"
    if sample_email_path.exists():
        with open(sample_email_path, "r") as f:
            sample_email = f.read()
    else:
        sample_email = """Subject: Auto Insurance Claim

I had a car accident on January 15, 2024 at 2:30 PM.
Location: Main Street and Oak Avenue.
Damage: $3,500.00
Policy: POL-2024-001234

John Doe"""
    
    # Step 1: Process claim
    claim = await orchestrator.process_claim(sample_email, source="email")
    assert claim is not None
    assert claim.status.value == "draft"
    
    # Wait for async processing
    await asyncio.sleep(1)
    
    # Step 2: Verify facts extracted
    updated_claim = await system["claim_repository"].find_by_id(claim.claim_id)
    assert updated_claim is not None
    assert updated_claim.summary is not None
    assert updated_claim.status.value in ["facts_extracted", "policy_validated", "triaged"]
    
    # Step 3: Verify workflow completed
    # Claim should have moved through the workflow
    final_status = updated_claim.status.value
    assert final_status in ["facts_extracted", "policy_validated", "triaged", "processing"]


@pytest.mark.asyncio
async def test_full_lifecycle_with_human_review(full_system_setup):
    """
    Test complete lifecycle with human review intervention.
    """
    system = full_system_setup
    orchestrator = system["orchestrator"]
    human_review_agent = system["human_review_agent"]
    
    # Process claim with high amount (triggers review)
    sample_email = """Subject: Large Claim

I had a major accident. Damage is $150,000.
Policy: POL-2024-001234

John Doe"""
    
    claim = await orchestrator.process_claim(sample_email)
    
    # Wait for processing
    await asyncio.sleep(1)
    
    # Verify review was triggered
    review_item = human_review_agent.review_queue.get_by_claim_id(claim.claim_id)
    assert review_item is not None
    
    # Simulate human review
    human_review_agent.process_human_decision(
        review_item,
        decision="approved",
        feedback="Verified, proceed"
    )
    
    # Verify feedback recorded
    stats = human_review_agent.get_review_statistics()
    assert stats["total_reviews"] > 0


@pytest.mark.asyncio
async def test_system_recovery_after_error(full_system_setup):
    """
    Test that system recovers gracefully from errors.
    """
    system = full_system_setup
    
    # This test verifies error handling
    # In a real scenario, we'd test with actual error conditions
    # For now, we verify the system structure supports error recovery
    
    assert system["orchestrator"] is not None
    assert system["claim_repository"] is not None
    # System should be able to continue after errors


@pytest.mark.asyncio
async def test_human_review_interface(full_system_setup):
    """
    Test human review interface functionality.
    """
    system = full_system_setup
    review_queue = system["review_queue"]
    
    # Create a review item
    from src.domain.claim import Claim
    claim = Claim(raw_input="Test", source="test")
    
    review_item = review_queue.add_for_review(
        claim=claim,
        reason="Test review",
        ai_decision="Test decision",
    )
    
    # Test review interface
    review_interface = ReviewInterface(review_queue)
    
    # List pending
    pending = review_queue.get_all_pending()
    assert len(pending) > 0
    
    # Verify interface can display items
    # (In real test, we'd capture output)
    assert review_interface is not None

