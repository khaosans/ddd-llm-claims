"""
Example: Human Review Workflow

This script demonstrates the human-in-the-loop review process.
"""

import asyncio
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import IntakeAgent, PolicyAgent, TriageAgent
from src.agents.model_provider import create_model_provider
from src.domain.policy import Policy, PolicyStatus
from src.human_review import ReviewQueue, HumanReviewAgent, FeedbackHandler, ReviewInterface
from src.orchestrator import WorkflowOrchestrator
from src.repositories import InMemoryClaimRepository, InMemoryPolicyRepository
from datetime import datetime
from decimal import Decimal
from uuid import uuid4


async def main():
    """Demonstrate human review workflow"""
    print("="*70)
    print("Human-in-the-Loop Review Example")
    print("="*70)
    
    # Setup (using mock providers for demo)
    from unittest.mock import MagicMock, AsyncMock
    mock_provider = MagicMock()
    mock_provider.generate = AsyncMock(return_value='{"claim_type":"auto","incident_date":"2024-01-15T14:30:00","claimed_amount":"150000.00","currency":"USD","incident_location":"Main St","description":"Major accident","claimant_name":"John Doe"}')
    
    intake_agent = IntakeAgent(mock_provider, temperature=0.3)
    policy_agent = PolicyAgent(mock_provider, temperature=0.2)
    triage_agent = TriageAgent(mock_provider, temperature=0.5)
    
    claim_repository = InMemoryClaimRepository()
    policy_repository = InMemoryPolicyRepository()
    
    # Add policy
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
    
    # Create orchestrator with human review
    orchestrator = WorkflowOrchestrator(
        intake_agent=intake_agent,
        policy_agent=policy_agent,
        triage_agent=triage_agent,
        claim_repository=claim_repository,
        policy_repository=policy_repository,
        human_review_agent=human_review_agent,
    )
    
    # Process a claim with high amount (triggers review)
    print("\n1. Processing claim with high amount ($150,000)...")
    sample_email = """Subject: Major Accident Claim

I had a major car accident. The damage is approximately $150,000.
Policy number: POL-2024-001234

John Doe"""
    
    claim = await orchestrator.process_claim(sample_email)
    print(f"   Claim ID: {claim.claim_id}")
    
    # Wait for processing
    await asyncio.sleep(0.5)
    
    # Check review queue
    print("\n2. Checking review queue...")
    review_item = review_queue.get_by_claim_id(claim.claim_id)
    if review_item:
        print(f"   ✓ Claim added to review queue")
        print(f"   Reason: {review_item.reason}")
        print(f"   Priority: {review_item.priority.value}")
        print(f"   AI Decision: {review_item.ai_decision}")
    else:
        print("   No review needed")
    
    # Simulate human review
    print("\n3. Simulating human review...")
    if review_item:
        # Human approves
        human_review_agent.process_human_decision(
            review_item,
            decision="approved",
            feedback="Verified amount, policy covers claim, proceed"
        )
        print("   ✓ Human approved AI decision")
        print(f"   Feedback: {review_item.human_feedback}")
    
    # Show statistics
    print("\n4. Review Statistics:")
    stats = human_review_agent.get_review_statistics()
    print(f"   Total Reviews: {stats['override_patterns']['total_reviews']}")
    print(f"   Approval Rate: {stats['override_patterns']['approval_rate']:.1%}")
    
    print("\n" + "="*70)
    print("Example complete!")
    print("\nTo use the interactive review interface:")
    print("  from src.human_review import ReviewInterface")
    print("  interface = ReviewInterface(review_queue)")
    print("  interface.review_next('reviewer1')")


if __name__ == "__main__":
    asyncio.run(main())

