"""
Triage & Routing Agent - Routes claims to appropriate downstream systems

This agent determines where a claim should be routed based on:
- Policy validation status
- Fraud score
- Claim complexity
- Business rules

It acts as an Anti-Corruption Layer between the workflow orchestrator
and downstream systems (human adjudicator queues, automated processing, etc.)
"""

import json
from typing import Optional
from uuid import UUID

from ..domain.claim import Claim
from ..domain.fraud import FraudCheckResult
from ..domain.policy.events import PolicyValidated
from .base_agent import BaseAgent
from .json_utils import parse_json_resilient, extract_json_from_text
from ..compliance.decision_audit import get_audit_service
from ..compliance.decision_context import DecisionContextTracker
from ..compliance.models import DecisionType, DecisionDependency


class TriageAgent(BaseAgent):
    """
    Triage & Routing Agent - Routes claims to appropriate handlers.
    
    DDD Role: Anti-Corruption Layer (ACL) for routing decisions.
    
    This agent:
    1. Analyzes claim status, fraud score, and complexity
    2. Uses an LLM to make intelligent routing decisions
    3. Determines the appropriate downstream system
    4. Updates claim status
    """
    
    def get_system_prompt(self) -> str:
        """System prompt for triage and routing"""
        return """You are a Claims Triage Specialist for an insurance company.
Your job is to route claims to the appropriate downstream system based on:
1. Policy validation status
2. Fraud risk score
3. Claim complexity and amount
4. Business rules

Available routing options:
- "human_adjudicator_queue": For complex claims, high fraud risk, or large amounts
- "automated_processing": For simple, low-risk claims
- "fraud_investigation": For high fraud risk claims
- "specialist_review": For claims requiring domain expertise
- "rejected": For invalid or ineligible claims

Output ONLY valid JSON:
{
    "routing_decision": "string (one of the options above)",
    "routing_reason": "string explaining why this route was chosen",
    "priority": "high" | "medium" | "low"
}

Consider:
- High fraud scores (>0.7) should go to fraud_investigation
- Large amounts (>$50,000) should go to human_adjudicator_queue
- Invalid policies should be rejected
- Simple, low-risk claims can be automated"""
    
    async def process(
        self,
        claim: Claim,
        fraud_result: Optional[FraudCheckResult] = None,
        policy_validated: Optional[PolicyValidated] = None,
    ) -> tuple[str, str, str]:
        """
        Determine routing for a claim.
        
        Args:
            claim: The claim to route
            fraud_result: Fraud assessment result (if available)
            policy_validated: Policy validation result (if available)
        
        Returns:
            Tuple of (routing_decision, routing_reason, priority)
        """
        # Initialize decision context tracker
        tracker = DecisionContextTracker()
        tracker.set_prompt(self.get_system_prompt())
        
        # Build context for the LLM
        claim_data = {
            "claim_id": str(claim.claim_id),
            "status": claim.status.value,
            "claim_type": claim.summary.claim_type if claim.summary else "unknown",
            "claimed_amount": str(claim.summary.claimed_amount) if claim.summary else "0",
        }
        tracker.add_input("claim_data", claim_data)
        
        fraud_data = None
        if fraud_result:
            fraud_data = {
                "fraud_score": str(fraud_result.fraud_score),
                "risk_level": fraud_result.risk_level.value,
                "is_suspicious": fraud_result.is_suspicious,
                "risk_factors": fraud_result.risk_factors,
            }
            tracker.add_input("fraud_result", fraud_data)
            tracker.add_evidence("fraud_assessment", fraud_data)
        
        policy_data = None
        if policy_validated:
            policy_data = {
                "is_valid": policy_validated.is_valid,
                "validation_reason": policy_validated.validation_reason,
            }
            tracker.add_input("policy_validation", policy_data)
            tracker.add_evidence("policy_validation", policy_data)
        
        prompt = f"""Route this claim to the appropriate downstream system:

CLAIM INFORMATION:
{json.dumps(claim_data, indent=2)}

FRAUD ASSESSMENT:
{json.dumps(fraud_data, indent=2) if fraud_data else "Not yet assessed"}

POLICY VALIDATION:
{json.dumps(policy_data, indent=2) if policy_data else "Not yet validated"}

Determine the best routing decision. Output JSON with your decision."""
        
        raw_output = await self.generate(prompt)
        tracker.set_llm_response(raw_output)
        
        # Parse and validate output using resilient JSON parsing
        # This handles cases where LLM returns JSON with extra text, markdown, empty responses, etc.
        result = parse_json_resilient(raw_output, max_attempts=3)
        
        if result is None:
            # Last resort: try to extract and provide helpful error
            extracted = extract_json_from_text(raw_output)
            if extracted:
                try:
                    result = json.loads(extracted)
                except json.JSONDecodeError as e:
                    error_msg = (
                        f"Failed to parse triage routing response. "
                        f"Could not parse JSON even after extraction. "
                        f"Error: {e}. "
                        f"Raw output preview: {raw_output[:200]}..."
                    )
                    audit_service = get_audit_service()
                    audit_service.capture_decision(
                        claim_id=claim.claim_id,
                        agent_component="TriageAgent",
                        decision_type=DecisionType.TRIAGE_ROUTING,
                        decision_value=None,
                        reasoning=f"Triage routing failed: {error_msg}",
                        context=tracker.build_context(),
                        success=False,
                        error_message=error_msg,
                    )
                    raise ValueError(error_msg) from e
            else:
                error_msg = (
                    f"Failed to parse triage routing response. "
                    f"Could not extract JSON from output. "
                    f"The LLM may have returned an empty or invalid response. "
                    f"Raw output preview: {raw_output[:200]}..."
                )
                audit_service = get_audit_service()
                audit_service.capture_decision(
                    claim_id=claim.claim_id,
                    agent_component="TriageAgent",
                    decision_type=DecisionType.TRIAGE_ROUTING,
                    decision_value=None,
                    reasoning=f"Triage routing failed: {error_msg}",
                    context=tracker.build_context(),
                    success=False,
                    error_message=error_msg,
                )
                raise ValueError(error_msg)
        
        routing_decision = result.get("routing_decision", "human_adjudicator_queue")
        routing_reason = result.get("routing_reason", "No reason provided")
        priority = result.get("priority", "medium")
        
        # Build dependencies
        dependencies = []
        # Note: In a full implementation, we'd look up decision IDs for fraud_result and policy_validated
        # For now, we'll just capture the reasoning
        
        # Capture decision
        audit_service = get_audit_service()
        audit_service.capture_decision(
            claim_id=claim.claim_id,
            agent_component="TriageAgent",
            decision_type=DecisionType.TRIAGE_ROUTING,
            decision_value={
                "routing_decision": routing_decision,
                "routing_reason": routing_reason,
                "priority": priority,
            },
            reasoning=routing_reason,
            context=tracker.build_context(),
            dependencies=dependencies,
            success=True,
        )
        
        return routing_decision, routing_reason, priority
    
    async def triage_claim(
        self,
        claim: Claim,
        fraud_result: Optional[FraudCheckResult] = None,
        policy_validated: Optional[PolicyValidated] = None,
    ) -> str:
        """
        Triage a claim and update its status.
        
        Args:
            claim: The claim to triage
            fraud_result: Fraud assessment result
            policy_validated: Policy validation result
        
        Returns:
            Routing decision string
        """
        routing_decision, routing_reason, priority = await self.process(
            claim, fraud_result, policy_validated
        )
        
        # Update claim status
        claim.triage(routing_decision)
        
        return routing_decision

