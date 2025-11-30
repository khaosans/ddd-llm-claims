"""
Example: Running the Claims Processing System

This script demonstrates how to use the system to process a claim
from unstructured input through the complete workflow.
"""

import asyncio
from pathlib import Path

from src.agents import IntakeAgent, PolicyAgent, TriageAgent
from src.agents.model_provider import create_model_provider
from src.domain.policy import Policy, PolicyStatus
from src.repositories import InMemoryClaimRepository, InMemoryPolicyRepository
from src.orchestrator import WorkflowOrchestrator
from datetime import datetime
from decimal import Decimal
from uuid import uuid4


async def main():
    """Main example function"""
    print("🚀 DDD Claims Processing System - Example")
    print("=" * 50)
    
    # Configuration
    # For this example, we'll use Ollama (local models)
    # Make sure Ollama is running: ollama serve
    # And you have a model: ollama pull llama3.2
    
    try:
        # Create model providers
        print("\n📦 Setting up model providers...")
        intake_provider = create_model_provider(
            "ollama",
            "llama3.2",
            base_url="http://localhost:11434"
        )
        policy_provider = create_model_provider(
            "ollama",
            "llama3.2",
            base_url="http://localhost:11434"
        )
        triage_provider = create_model_provider(
            "ollama",
            "llama3.2",
            base_url="http://localhost:11434"
        )
        print("✅ Model providers configured")
    except Exception as e:
        print(f"❌ Error setting up model providers: {e}")
        print("\n💡 Make sure Ollama is running:")
        print("   1. Start Ollama: ollama serve")
        print("   2. Download a model: ollama pull llama3.2")
        return
    
    # Create agents
    print("\n🤖 Creating agents...")
    intake_agent = IntakeAgent(intake_provider, temperature=0.3)
    policy_agent = PolicyAgent(policy_provider, temperature=0.2)
    triage_agent = TriageAgent(triage_provider, temperature=0.5)
    print("✅ Agents created")
    
    # Create repositories
    print("\n💾 Setting up repositories...")
    claim_repository = InMemoryClaimRepository()
    policy_repository = InMemoryPolicyRepository()
    
    # Add a sample policy
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
    print("✅ Repositories configured with sample policy")
    
    # Create orchestrator
    print("\n🎼 Creating workflow orchestrator...")
    orchestrator = WorkflowOrchestrator(
        intake_agent=intake_agent,
        policy_agent=policy_agent,
        triage_agent=triage_agent,
        claim_repository=claim_repository,
        policy_repository=policy_repository,
    )
    print("✅ Orchestrator created")
    
    # Load sample email
    print("\n📧 Loading sample claim email...")
    sample_email_path = Path(__file__).parent / "sample_claim_email.txt"
    if sample_email_path.exists():
        with open(sample_email_path, "r") as f:
            sample_email = f.read()
        print("✅ Sample email loaded")
    else:
        # Fallback sample
        sample_email = """Subject: Auto Insurance Claim

Dear Insurance Company,

I am filing a claim for a car accident on January 15, 2024 at 2:30 PM.
The incident occurred at Main Street and Oak Avenue in Anytown, State 12345.
Another driver rear-ended my vehicle. Repair costs are $3,500.00.

My policy number is POL-2024-001234.
Contact: john.doe@email.com, +1-555-0123

John Doe"""
        print("⚠️  Using fallback sample email")
    
    # Process the claim
    print("\n🔄 Processing claim...")
    print("-" * 50)
    try:
        claim = await orchestrator.process_claim(sample_email, source="email")
        
        print("\n✅ Claim processed successfully!")
        print(f"   Claim ID: {claim.claim_id}")
        print(f"   Status: {claim.status.value}")
        
        if claim.summary:
            print(f"\n📋 Extracted Facts:")
            print(f"   Type: {claim.summary.claim_type}")
            print(f"   Amount: ${claim.summary.claimed_amount}")
            print(f"   Location: {claim.summary.incident_location}")
            print(f"   Claimant: {claim.summary.claimant_name}")
        
        # Wait a moment for async events to process
        await asyncio.sleep(1)
        
        # Check final status
        updated_claim = await claim_repository.find_by_id(claim.claim_id)
        if updated_claim:
            print(f"\n🎯 Final Status: {updated_claim.status.value}")
        
    except Exception as e:
        print(f"\n❌ Error processing claim: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✨ Example complete!")


if __name__ == "__main__":
    asyncio.run(main())

