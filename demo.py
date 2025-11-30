#!/usr/bin/env python3
"""
Live Demo - Interactive demonstration of the DDD Claims Processing System

This script provides a live, interactive demo that can be watched and
explained in real-time. It demonstrates the complete workflow including
human-in-the-loop review.

DISCLAIMER: This is a DEMONSTRATION system for educational purposes only.
NOT for production use.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import IntakeAgent, PolicyAgent, TriageAgent, FraudAgent
from src.agents.model_provider import create_model_provider
from src.domain.policy import Policy, PolicyStatus
from src.human_review import ReviewQueue, HumanReviewAgent, FeedbackHandler, ReviewInterface
from src.orchestrator import WorkflowOrchestrator
from src.repositories import InMemoryClaimRepository, InMemoryPolicyRepository
from src.visualization import WorkflowVisualizer


class LiveDemo:
    """
    Live demonstration of the claims processing system.
    
    Provides step-by-step visualization and explanation of the workflow.
    """
    
    def __init__(self):
        """Initialize the demo"""
        self.visualizer = WorkflowVisualizer()
        self.setup_complete = False
    
    def print_header(self, title: str):
        """Print a section header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    
    def print_step(self, step_num: int, description: str):
        """Print a workflow step"""
        print(f"Step {step_num}: {description}")
        print("-" * 70)
    
    def wait_for_continue(self, message: str = "Press Enter to continue..."):
        """Wait for user to continue"""
        input(f"\n{message}")
    
    async def setup_system(self):
        """Setup the system for demo"""
        self.print_header("SYSTEM SETUP")
        
        print("Setting up model providers...")
        try:
            # Try Ollama first
            intake_provider = create_model_provider("ollama", "llama3.2")
            policy_provider = create_model_provider("ollama", "llama3.2")
            triage_provider = create_model_provider("ollama", "llama3.2")
            print("✓ Using Ollama (local models)")
            model_type = "Ollama (local)"
        except Exception:
            # Fallback to mock
            from unittest.mock import MagicMock, AsyncMock
            mock_provider = MagicMock()
            mock_provider.generate = AsyncMock(return_value='{"claim_type":"auto","incident_date":"2024-01-15T14:30:00","claimed_amount":"3500.00","currency":"USD","incident_location":"Main St","description":"Test","claimant_name":"John Doe"}')
            intake_provider = policy_provider = triage_provider = mock_provider
            print("✓ Using mock providers (for demo without Ollama)")
            model_type = "Mock (demo mode)"
        
        print("\nCreating agents...")
        self.intake_agent = IntakeAgent(intake_provider, temperature=0.3)
        self.policy_agent = PolicyAgent(policy_provider, temperature=0.2)
        self.triage_agent = TriageAgent(triage_provider, temperature=0.5)
        self.fraud_agent = FraudAgent(intake_provider, temperature=0.2)
        print("✓ Intake Agent")
        print("✓ Policy Agent")
        print("✓ Triage Agent")
        print("✓ Fraud Agent")
        
        print("\nSetting up repositories...")
        self.claim_repository = InMemoryClaimRepository()
        self.policy_repository = InMemoryPolicyRepository()
        
        # Add sample policy
        self.sample_policy = Policy(
            policy_id=uuid4(),
            policy_number="POL-2024-001234",
            customer_id=uuid4(),
            status=PolicyStatus.ACTIVE,
            policy_type="auto",
            coverage_start=datetime(2024, 1, 1),
            coverage_end=datetime(2024, 12, 31),
            max_coverage_amount=Decimal("50000.00"),
        )
        await self.policy_repository.save(self.sample_policy)
        print(f"✓ Policy Repository (Policy: {self.sample_policy.policy_number})")
        
        print("\nSetting up human review...")
        self.review_queue = ReviewQueue()
        self.feedback_handler = FeedbackHandler()
        self.human_review_agent = HumanReviewAgent(self.review_queue, self.feedback_handler)
        self.review_interface = ReviewInterface(self.review_queue)
        print("✓ Review Queue")
        print("✓ Feedback Handler")
        print("✓ Human Review Agent")
        
        print("\nCreating workflow orchestrator...")
        self.orchestrator = WorkflowOrchestrator(
            intake_agent=self.intake_agent,
            policy_agent=self.policy_agent,
            triage_agent=self.triage_agent,
            fraud_agent=self.fraud_agent,
            claim_repository=self.claim_repository,
            policy_repository=self.policy_repository,
            human_review_agent=self.human_review_agent,
        )
        print("✓ Workflow Orchestrator")
        
        self.setup_complete = True
        print(f"\n✅ System ready! (Using {model_type})")
    
    async def demonstrate_workflow(self):
        """Demonstrate the complete workflow"""
        self.print_header("DEMONSTRATION: Complete Claim Processing Workflow")
        
        # Load sample email
        sample_email_path = Path(__file__).parent / "examples" / "sample_claim_email.txt"
        if sample_email_path.exists():
            with open(sample_email_path, "r") as f:
                sample_email = f.read()
        else:
            sample_email = """Subject: Auto Insurance Claim

Dear Insurance Company,

I am filing a claim for a car accident on January 15, 2024 at 2:30 PM.
The incident occurred at Main Street and Oak Avenue.
Another driver rear-ended my vehicle. Repair costs are $3,500.00.

My policy number is POL-2024-001234.

John Doe"""
        
        self.print_step(1, "Receiving Unstructured Input")
        print("Input: Customer email")
        print(f"\n{sample_email[:200]}...")
        self.wait_for_continue()
        
        self.print_step(2, "Intake Agent Extracts Facts")
        print("🤖 Intake Agent (LLM) processing unstructured email...")
        print("   - Analyzing text")
        print("   - Extracting structured facts")
        print("   - Validating against domain model")
        
        claim = await self.orchestrator.process_claim(sample_email, source="email")
        print(f"\n✓ Claim created: {claim.claim_id}")
        print(f"✓ Status: {claim.status.value}")
        
        # Wait for async processing
        await asyncio.sleep(1)
        
        updated_claim = await self.claim_repository.find_by_id(claim.claim_id)
        if updated_claim and updated_claim.summary:
            print(f"\n📋 Extracted Facts:")
            print(f"   Type: {updated_claim.summary.claim_type}")
            print(f"   Amount: ${updated_claim.summary.claimed_amount}")
            print(f"   Location: {updated_claim.summary.incident_location}")
            print(f"   Claimant: {updated_claim.summary.claimant_name}")
        
        self.wait_for_continue()
        
        self.print_step(3, "Policy Validation")
        print("🔍 Policy Agent validating claim against policy...")
        await asyncio.sleep(0.5)
        
        if updated_claim:
            print(f"✓ Policy validation complete")
            print(f"✓ Status: {updated_claim.status.value}")
        
        self.wait_for_continue()
        
        self.print_step(4, "Fraud Assessment")
        print("🚩 Fraud Agent analyzing claim for fraud indicators...")
        await asyncio.sleep(1)
        
        # Get fraud result if available
        if updated_claim:
            try:
                fraud_result = await self.fraud_agent.process(updated_claim, claim_id=updated_claim.claim_id)
                print(f"✓ Fraud score: {fraud_result.fraud_score:.2f}")
                print(f"✓ Risk level: {fraud_result.risk_level.value}")
                if fraud_result.risk_factors:
                    print(f"✓ Risk factors detected: {len(fraud_result.risk_factors)}")
                    for factor in fraud_result.risk_factors[:3]:
                        print(f"   - {factor}")
            except Exception:
                print("✓ Fraud assessment completed")
        
        self.wait_for_continue()
        
        self.print_step(5, "Triage & Routing")
        print("🎯 Triage Agent determining routing...")
        await asyncio.sleep(0.5)
        
        final_claim = await self.claim_repository.find_by_id(claim.claim_id)
        if final_claim:
            print(f"✓ Routing decision made")
            print(f"✓ Final status: {final_claim.status.value}")
        
        self.wait_for_continue()
        
        # Check for human review
        review_item = self.review_queue.get_by_claim_id(claim.claim_id)
        if review_item:
            self.print_step(6, "Human Review Required")
            print(f"⚠️  Claim requires human review")
            print(f"   Reason: {review_item.reason}")
            print(f"   Priority: {review_item.priority.value}")
            print(f"\n   This demonstrates human-in-the-loop capability")
            print(f"   Human reviewer can approve, reject, or override AI decision")
            self.wait_for_continue()
        
        self.print_header("WORKFLOW COMPLETE")
        print("✅ Claim processing workflow completed successfully!")
        print(f"\nFinal Claim Status: {final_claim.status.value if final_claim else 'Unknown'}")
        
        # Show statistics
        if self.human_review_agent:
            stats = self.human_review_agent.get_review_statistics()
            if stats["pending_reviews"] > 0:
                print(f"\n📊 Review Statistics:")
                print(f"   Pending Reviews: {stats['pending_reviews']}")
    
    async def demonstrate_human_review(self):
        """Demonstrate human review workflow"""
        self.print_header("DEMONSTRATION: Human-in-the-Loop Review")
        
        # Process a claim that will trigger review
        print("Processing claim with high amount ($150,000)...")
        high_amount_email = """Subject: Major Accident Claim

I had a major car accident. The damage is approximately $150,000.
Policy: POL-2024-001234

John Doe"""
        
        claim = await self.orchestrator.process_claim(high_amount_email)
        await asyncio.sleep(1)
        
        review_item = self.review_queue.get_by_claim_id(claim.claim_id)
        if review_item:
            print(f"\n✓ Claim added to review queue")
            print(f"   Reason: {review_item.reason}")
            print(f"   Priority: {review_item.priority.value}")
            
            self.wait_for_continue("Press Enter to simulate human review...")
            
            print("\n👤 Human Reviewer reviewing claim...")
            print("   - Reviewing claim details")
            print("   - Verifying AI decision")
            print("   - Making decision...")
            
            # Simulate human approval
            self.human_review_agent.process_human_decision(
                review_item,
                decision="approved",
                feedback="Verified amount and policy, proceeding with claim"
            )
            
            print("\n✓ Human decision: APPROVED")
            print(f"✓ Feedback recorded")
            
            # Show statistics
            stats = self.human_review_agent.get_review_statistics()
            print(f"\n📊 Review Statistics:")
            print(f"   Total Reviews: {stats['override_patterns']['total_reviews']}")
            print(f"   Approval Rate: {stats['override_patterns']['approval_rate']:.1%}")
    
    async def run(self):
        """Run the complete demo"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     DDD Claims Processing System - LIVE DEMONSTRATION       ║
║                                                              ║
║     ⚠️  DEMO SYSTEM - NOT FOR PRODUCTION USE                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
        
        print("\nThis is an EDUCATIONAL DEMONSTRATION system.")
        print("It demonstrates Domain-Driven Design principles with LLM agents.")
        print("\n⚠️  DISCLAIMER: This is NOT production-ready software.")
        print("   See DISCLAIMERS.md for complete information.\n")
        
        self.wait_for_continue("Press Enter to start the demonstration...")
        
        # Setup
        await self.setup_system()
        self.wait_for_continue()
        
        # Demonstrate workflow
        await self.demonstrate_workflow()
        
        # Demonstrate human review
        print("\n" + "="*70)
        choice = input("\nWould you like to see human review demonstration? (y/n): ")
        if choice.lower() == 'y':
            await self.demonstrate_human_review()
        
        self.print_header("DEMONSTRATION COMPLETE")
        print("Thank you for watching!")
        print("\nFor more information:")
        print("  - See README.md for overview")
        print("  - See docs/TECHNICAL.md for architecture")
        print("  - See docs/REFERENCES.md for research citations")
        print("  - See DISCLAIMERS.md for important disclaimers")


async def main():
    """Main entry point"""
    demo = LiveDemo()
    try:
        await demo.run()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

