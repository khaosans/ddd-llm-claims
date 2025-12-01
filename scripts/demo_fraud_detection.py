#!/usr/bin/env python3
"""
Fraud Detection Demo - Interactive demonstration of fraud detection capabilities

This script demonstrates the fraud detection system with various test templates
and allows interactive exploration of fraud detection results.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import IntakeAgent, PolicyAgent, TriageAgent, FraudAgent
from src.agents.model_provider import create_model_provider
from src.domain.policy import Policy, PolicyStatus
from src.human_review import ReviewQueue, HumanReviewAgent, FeedbackHandler
from src.orchestrator import WorkflowOrchestrator
from src.repositories import InMemoryClaimRepository, InMemoryPolicyRepository
from data_templates import get_template, list_templates, CLAIM_TEMPLATES


class FraudDetectionDemo:
    """Interactive fraud detection demonstration"""
    
    def __init__(self):
        """Initialize demo"""
        self.setup_complete = False
    
    def print_header(self, title: str):
        """Print section header"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80 + "\n")
    
    def print_fraud_result(self, fraud_result, claim_id=None):
        """Print fraud detection result"""
        print("\n" + "-"*80)
        print("FRAUD DETECTION RESULT")
        print("-"*80)
        print(f"Fraud Score: {fraud_result.fraud_score:.2f} (0.0 = Low Risk, 1.0 = Critical Risk)")
        print(f"Risk Level: {fraud_result.risk_level.value.upper()}")
        print(f"Suspicious: {'⚠️  YES' if fraud_result.is_suspicious else '✓ No'}")
        print(f"Assessment Method: {fraud_result.assessment_method}")
        
        if fraud_result.confidence:
            print(f"Confidence: {fraud_result.confidence:.2%}")
        
        if fraud_result.risk_factors:
            print(f"\nRisk Factors Detected ({len(fraud_result.risk_factors)}):")
            for i, factor in enumerate(fraud_result.risk_factors, 1):
                print(f"  {i}. {factor}")
        else:
            print("\nNo specific risk factors identified")
        
        print("-"*80)
    
    async def setup_system(self):
        """Setup system for demo"""
        self.print_header("SYSTEM SETUP")
        
        print("Initializing model providers...")
        try:
            provider = create_model_provider("ollama", "llama3.2:3b")
            print("✓ Using Ollama (local models)")
            model_type = "Ollama"
        except Exception as e:
            print(f"⚠️  Ollama not available: {e}")
            print("   Using mock providers for demo")
            from unittest.mock import MagicMock, AsyncMock
            
            async def mock_generate(prompt, **kwargs):
                if "fraud" in prompt.lower() or "analyze" in prompt.lower():
                    if "stolen" in prompt.lower() or "suspicious" in prompt.lower():
                        return '{"fraud_score":0.75,"risk_level":"high","is_suspicious":true,"risk_factors":["Suspicious timing","Unusual claim pattern"],"confidence":0.85}'
                    elif "missing" in prompt.lower() or "invalid" in prompt.lower():
                        return '{"fraud_score":0.45,"risk_level":"medium","is_suspicious":false,"risk_factors":["Missing critical fields"],"confidence":0.70}'
                    else:
                        return '{"fraud_score":0.15,"risk_level":"low","is_suspicious":false,"risk_factors":[],"confidence":0.90}'
                elif "Extract" in prompt or "claim" in prompt.lower():
                    return '{"claim_type":"auto","incident_date":"2024-01-15T14:30:00","reported_date":"2024-01-16T09:00:00","claimed_amount":"3500.00","currency":"USD","incident_location":"Main St","description":"Test claim","claimant_name":"John Doe","policy_number":"POL-2024-001234"}'
                elif "Validate" in prompt or "policy" in prompt.lower():
                    return '{"is_valid":true,"policy_id":"550e8400-e29b-41d4-a716-446655440000","validation_reason":"Policy is active"}'
                elif "Route" in prompt or "triage" in prompt.lower():
                    return '{"routing_decision":"human_adjudicator_queue","routing_reason":"Standard routing","priority":"medium"}'
                return '{}'
            
            mock_provider = MagicMock()
            mock_provider.generate = AsyncMock(side_effect=mock_generate)
            provider = mock_provider
            model_type = "Mock (demo mode)"
        
        print("\nCreating agents...")
        self.intake_agent = IntakeAgent(provider, temperature=0.3)
        self.policy_agent = PolicyAgent(provider, temperature=0.2)
        self.triage_agent = TriageAgent(provider, temperature=0.5)
        self.fraud_agent = FraudAgent(provider, temperature=0.2)
        print("✓ Intake Agent")
        print("✓ Policy Agent")
        print("✓ Triage Agent")
        print("✓ Fraud Agent")
        
        print("\nSetting up repositories...")
        self.claim_repository = InMemoryClaimRepository()
        self.policy_repository = InMemoryPolicyRepository()
        
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
        await self.policy_repository.save(sample_policy)
        print(f"✓ Policy Repository (Policy: {sample_policy.policy_number})")
        
        print("\nSetting up workflow orchestrator...")
        self.review_queue = ReviewQueue()
        self.feedback_handler = FeedbackHandler()
        self.human_review_agent = HumanReviewAgent(self.review_queue, self.feedback_handler)
        
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
    
    async def demo_template(self, template_name: str):
        """Demonstrate fraud detection with a specific template"""
        print(f"\n{'='*80}")
        print(f"Testing Template: {template_name}")
        print("="*80)
        
        template_content = get_template("claim", template_name)
        if not template_content:
            print(f"❌ Template '{template_name}' not found")
            return
        
        print("\nTemplate Content:")
        print("-"*80)
        print(template_content[:500] + ("..." if len(template_content) > 500 else ""))
        print("-"*80)
        
        print("\n🤖 Processing claim through workflow...")
        
        # Process claim
        claim = await self.orchestrator.process_claim(template_content, source="email")
        
        # Wait for async processing
        await asyncio.sleep(2)
        
        # Get updated claim
        updated_claim = await self.claim_repository.find_by_id(claim.claim_id)
        
        if updated_claim and updated_claim.summary:
            print("\n📋 Extracted Facts:")
            print(f"   Type: {updated_claim.summary.claim_type}")
            print(f"   Amount: ${updated_claim.summary.claimed_amount}")
            print(f"   Location: {updated_claim.summary.incident_location}")
            print(f"   Claimant: {updated_claim.summary.claimant_name}")
        
        # Get fraud result (would be in workflow, but for demo we'll assess directly)
        if updated_claim:
            print("\n🚩 Running fraud detection...")
            fraud_result = await self.fraud_agent.process(updated_claim, claim_id=updated_claim.claim_id)
            self.print_fraud_result(fraud_result, updated_claim.claim_id)
            
            # Check routing
            print(f"\n🎯 Final Status: {updated_claim.status.value}")
            
            # Check review queue
            review_item = self.review_queue.get_by_claim_id(updated_claim.claim_id)
            if review_item:
                print(f"\n⚠️  Human Review Required:")
                print(f"   Reason: {review_item.reason}")
                print(f"   Priority: {review_item.priority.value}")
    
    async def interactive_demo(self):
        """Interactive demo mode"""
        self.print_header("FRAUD DETECTION INTERACTIVE DEMO")
        
        # Get fraud templates
        fraud_templates = [
            name for name in CLAIM_TEMPLATES.keys()
            if "fraud" in name.lower() or "suspicious" in name.lower() or
               "missing" in name.lower() or "invalid" in name.lower() or
               "expired" in name.lower() or "mismatch" in name.lower() or
               "multiple" in name.lower()
        ]
        
        normal_templates = [
            name for name in CLAIM_TEMPLATES.keys()
            if name not in fraud_templates
        ]
        
        print("Available Templates:")
        print("\nFraud/Anomaly Templates:")
        for i, name in enumerate(fraud_templates, 1):
            print(f"  {i}. {name}")
        
        print("\nNormal Templates (for comparison):")
        for i, name in enumerate(normal_templates[:5], len(fraud_templates) + 1):
            print(f"  {i}. {name}")
        
        print(f"\n  {len(fraud_templates) + len(normal_templates[:5]) + 1}. Run all fraud templates")
        print(f"  {len(fraud_templates) + len(normal_templates[:5]) + 2}. Exit")
        
        while True:
            try:
                choice = input("\nSelect template number: ").strip()
                choice_num = int(choice)
                
                if choice_num == len(fraud_templates) + len(normal_templates[:5]) + 1:
                    # Run all fraud templates
                    print("\n" + "="*80)
                    print("Running All Fraud Templates")
                    print("="*80)
                    for template_name in fraud_templates:
                        await self.demo_template(template_name)
                        input("\nPress Enter to continue to next template...")
                    break
                
                elif choice_num == len(fraud_templates) + len(normal_templates[:5]) + 2:
                    print("\nExiting demo...")
                    break
                
                elif 1 <= choice_num <= len(fraud_templates):
                    await self.demo_template(fraud_templates[choice_num - 1])
                    continue_demo = input("\nContinue demo? (y/n): ").strip().lower()
                    if continue_demo != 'y':
                        break
                
                elif len(fraud_templates) + 1 <= choice_num <= len(fraud_templates) + len(normal_templates[:5]):
                    idx = choice_num - len(fraud_templates) - 1
                    await self.demo_template(normal_templates[idx])
                    continue_demo = input("\nContinue demo? (y/n): ").strip().lower()
                    if continue_demo != 'y':
                        break
                
                else:
                    print("Invalid selection")
            
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nDemo interrupted")
                break
    
    async def run(self):
        """Run the demo"""
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     Fraud Detection Demo - Interactive Demonstration         ║
║                                                              ║
║     ⚠️  DEMO SYSTEM - NOT FOR PRODUCTION USE                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
        
        print("\nThis demo showcases fraud detection capabilities.")
        print("You can test various fraud and anomaly templates.")
        print("\n⚠️  DISCLAIMER: This is NOT production-ready software.\n")
        
        input("Press Enter to start...")
        
        # Setup
        await self.setup_system()
        input("\nPress Enter to continue...")
        
        # Interactive demo
        await self.interactive_demo()
        
        self.print_header("DEMO COMPLETE")
        print("Thank you for exploring fraud detection!")
        print("\nTo generate new templates, run:")
        print("  python scripts/generate_fraud_templates.py")


async def main():
    """Main entry point"""
    demo = FraudDetectionDemo()
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


