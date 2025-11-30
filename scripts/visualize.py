#!/usr/bin/env python3
"""
Interactive Visualization Tool

Run this script to visualize the claims processing system in action.
Shows real-time status, events, and workflow progress.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agents import IntakeAgent, PolicyAgent, TriageAgent
from src.agents.model_provider import create_model_provider
from src.domain.policy import Policy, PolicyStatus
from src.repositories import InMemoryClaimRepository, InMemoryPolicyRepository
from src.orchestrator import WorkflowOrchestrator
from src.visualization.workflow_visualizer import WorkflowVisualizer
from datetime import datetime
from decimal import Decimal
from uuid import uuid4


class VisualizingOrchestrator(WorkflowOrchestrator):
    """Orchestrator with visualization capabilities"""
    
    def __init__(self, visualizer: WorkflowVisualizer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visualizer = visualizer
    
    async def process_claim(self, raw_input: str, source: str = "email"):
        """Process claim with visualization"""
        print("\n" + "="*60)
        print("🚀 STARTING CLAIM PROCESSING")
        print("="*60)
        
        # Show workflow flow
        print(self.visualizer.visualize_workflow_flow())
        
        # Process claim
        claim = await super().process_claim(raw_input, source)
        self.visualizer.record_claim(claim)
        
        # Show initial status
        print("\n📊 INITIAL STATUS:")
        print(self.visualizer.visualize_status(claim.claim_id))
        
        # Wait for events to process
        await asyncio.sleep(2)
        
        # Show updated status
        updated_claim = await self.claim_repository.find_by_id(claim.claim_id)
        if updated_claim:
            print("\n📊 UPDATED STATUS:")
            print(self.visualizer.visualize_status(updated_claim.claim_id))
        
        # Show event timeline
        print("\n📅 EVENT TIMELINE:")
        print(self.visualizer.visualize_event_timeline(claim.claim_id))
        
        return claim


async def main():
    """Main visualization function"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     DDD Claims Processing System - Visualization Tool        ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Initialize visualizer
    visualizer = WorkflowVisualizer()
    
    # Subscribe visualizer to events
    from src.domain.events import event_bus
    
    class EventRecorder:
        async def handle(self, event):
            visualizer.record_event(event)
    
    recorder = EventRecorder()
    event_bus.subscribe("ClaimFactsExtracted", recorder)
    event_bus.subscribe("PolicyValidated", recorder)
    event_bus.subscribe("FraudScoreCalculated", recorder)
    
    # Setup model providers
    print("\n📦 Setting up model providers...")
    try:
        intake_provider = create_model_provider("ollama", "llama3.2")
        policy_provider = create_model_provider("ollama", "llama3.2")
        triage_provider = create_model_provider("ollama", "llama3.2")
        print("✅ Using Ollama (local models)")
    except Exception as e:
        print(f"⚠️  Ollama not available: {e}")
        print("   Using mock providers for demonstration")
        # Create mock providers for demo
        from unittest.mock import MagicMock, AsyncMock
        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value='{"claim_type":"auto","incident_date":"2024-01-15T14:30:00","claimed_amount":"3500.00","currency":"USD","incident_location":"Main St","description":"Test","claimant_name":"John Doe"}')
        intake_provider = policy_provider = triage_provider = mock_provider
    
    # Create agents
    print("🤖 Creating agents...")
    intake_agent = IntakeAgent(intake_provider, temperature=0.3)
    policy_agent = PolicyAgent(policy_provider, temperature=0.2)
    triage_agent = TriageAgent(triage_provider, temperature=0.5)
    
    # Create repositories
    print("💾 Setting up repositories...")
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
    
    # Create orchestrator with visualization
    orchestrator = VisualizingOrchestrator(
        visualizer=visualizer,
        intake_agent=intake_agent,
        policy_agent=policy_agent,
        triage_agent=triage_agent,
        claim_repository=claim_repository,
        policy_repository=policy_repository,
    )
    
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
    
    # Process with visualization
    try:
        claim = await orchestrator.process_claim(sample_email, source="email")
        
        print("\n" + "="*60)
        print("✅ PROCESSING COMPLETE")
        print("="*60)
        print(f"\nFinal Claim ID: {claim.claim_id}")
        print(f"Final Status: {claim.status.value}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Generate Mermaid diagram
    print("\n" + "="*60)
    print("📊 MERMAID DIAGRAM CODE")
    print("="*60)
    print("\nCopy this into a Mermaid-compatible viewer (GitHub, Mermaid Live Editor):")
    print("\n```mermaid")
    print(visualizer.generate_mermaid_diagram())
    print("```")


if __name__ == "__main__":
    asyncio.run(main())

