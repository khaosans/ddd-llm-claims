"""
Policy Validation Agent - Validates claims against policies

This agent checks if a claim is covered by an active policy.
It acts as an Anti-Corruption Layer between the Policy Management
bounded context and the Claim Intake context.
"""

import json
from typing import Optional
from uuid import UUID

from ..domain.policy import Policy
from ..domain.policy.events import PolicyValidated
from ..domain.claim import Claim, ClaimSummary
from ..domain.events import DomainEvent
from .base_agent import BaseAgent
from .json_utils import parse_json_resilient, extract_json_from_text
from ..compliance.decision_audit import get_audit_service
from ..compliance.decision_context import DecisionContextTracker
from ..compliance.models import DecisionType, DecisionDependency


class PolicyAgent(BaseAgent):
    """
    Policy Validation Agent - Validates claims against policies.
    
    DDD Role: Anti-Corruption Layer (ACL) between Policy Management
    and Claim Intake bounded contexts.
    
    This agent:
    1. Takes a claim summary and available policies
    2. Uses an LLM to determine if the claim is covered
    3. Validates policy status, coverage dates, and amounts
    4. Publishes PolicyValidated domain event
    """
    
    def get_system_prompt(self) -> str:
        """System prompt for policy validation"""
        return """You are a Policy Validation Specialist for an insurance company.
Your job is to determine if a claim is covered by an active policy.

You will receive:
1. A claim summary with claim details
2. One or more policy records

You must check:
1. Is the policy active? (status = "active" and within coverage dates)
2. Does the policy cover this claim type?
3. Is the claim amount within coverage limits?
4. Is the incident date within the coverage period?

Output ONLY valid JSON:
{
    "is_valid": true or false,
    "policy_id": "UUID string or null",
    "validation_reason": "string explaining the decision"
}

Be strict and precise. A claim is only valid if ALL conditions are met."""
    
    async def process(
        self,
        claim_summary: ClaimSummary,
        policies: list[Policy],
        claim_id: Optional[UUID] = None,
    ) -> tuple[bool, Optional[str], str]:
        """
        Validate claim against available policies.
        
        Args:
            claim_summary: The claim summary to validate
            policies: List of policies to check against
            claim_id: Optional claim ID for decision tracking
        
        Returns:
            Tuple of (is_valid, policy_id, validation_reason)
        """
        # Initialize decision context tracker
        tracker = DecisionContextTracker()
        tracker.add_input("claim_summary", claim_summary.model_dump() if hasattr(claim_summary, 'model_dump') else str(claim_summary))
        tracker.add_input("policies_count", len(policies))
        tracker.set_prompt(self.get_system_prompt())
        
        # Format policies for the LLM
        policies_data = []
        for policy in policies:
            policies_data.append({
                "policy_id": str(policy.policy_id),
                "policy_number": policy.policy_number,
                "status": policy.status.value,
                "policy_type": policy.policy_type,
                "coverage_start": policy.coverage_start.isoformat(),
                "coverage_end": policy.coverage_end.isoformat(),
                "max_coverage_amount": str(policy.max_coverage_amount),
            })
        
        # Convert to JSON-serializable dict
        claim_dict = claim_summary.model_dump(mode='json')
        
        prompt = f"""Validate this claim against the available policies:

CLAIM SUMMARY:
{json.dumps(claim_dict, indent=2)}

AVAILABLE POLICIES:
{json.dumps(policies_data, indent=2)}

Determine if the claim is covered by any active policy. Output JSON with your decision."""
        
        raw_output = await self.generate(prompt)
        tracker.set_llm_response(raw_output)
        
        # Parse and validate output using resilient JSON parsing
        # This handles cases where LLM returns JSON with extra text, markdown, etc.
        result = parse_json_resilient(raw_output, max_attempts=3)
        
        if result is None:
            # Last resort: try to extract and provide helpful error
            extracted = extract_json_from_text(raw_output)
            if extracted:
                try:
                    result = json.loads(extracted)
                except json.JSONDecodeError as e:
                    error_msg = (
                        f"Failed to parse policy validation response. "
                        f"Could not parse JSON even after extraction. "
                        f"Error: {e}. "
                        f"Raw output preview: {raw_output[:200]}..."
                    )
                    if claim_id:
                        audit_service = get_audit_service()
                        audit_service.capture_decision(
                            claim_id=claim_id,
                            agent_component="PolicyAgent",
                            decision_type=DecisionType.POLICY_VALIDATION,
                            decision_value=None,
                            reasoning=f"Policy validation failed: {error_msg}",
                            context=tracker.build_context(),
                            success=False,
                            error_message=error_msg,
                        )
                    raise ValueError(error_msg) from e
            else:
                error_msg = (
                    f"Failed to parse policy validation response. "
                    f"Could not extract JSON from output. "
                    f"Raw output preview: {raw_output[:200]}..."
                )
                if claim_id:
                    audit_service = get_audit_service()
                    audit_service.capture_decision(
                        claim_id=claim_id,
                        agent_component="PolicyAgent",
                        decision_type=DecisionType.POLICY_VALIDATION,
                        decision_value=None,
                        reasoning=f"Policy validation failed: {error_msg}",
                        context=tracker.build_context(),
                        success=False,
                        error_message=error_msg,
                    )
                raise ValueError(error_msg)
        
        is_valid = result.get("is_valid", False)
        policy_id = result.get("policy_id")
        validation_reason = result.get("validation_reason", "No reason provided")
        
        # Add evidence
        tracker.add_evidence("policy_validation", {
            "is_valid": is_valid,
            "policy_id": policy_id,
            "policies_checked": len(policies),
        })
        
        # Capture decision
        if claim_id:
            audit_service = get_audit_service()
            audit_service.capture_decision(
                claim_id=claim_id,
                agent_component="PolicyAgent",
                decision_type=DecisionType.POLICY_VALIDATION,
                decision_value={
                    "is_valid": is_valid,
                    "policy_id": policy_id,
                    "validation_reason": validation_reason,
                },
                reasoning=validation_reason,
                context=tracker.build_context(),
                success=True,
            )
        
        return is_valid, policy_id, validation_reason
    
    async def validate_claim(
        self,
        claim: Claim,
        policies: list[Policy]
    ) -> PolicyValidated:
        """
        Validate a claim and return domain event.
        
        Args:
            claim: The claim to validate
            policies: Available policies to check
        
        Returns:
            PolicyValidated domain event
        """
        if not claim.summary:
            raise ValueError("Cannot validate claim: no summary available")
        
        is_valid, policy_id, reason = await self.process(claim.summary, policies, claim_id=claim.claim_id)
        
        # Update claim status
        claim.validate_policy(is_valid)
        
        # Create domain event
        event = PolicyValidated(
            claim_id=claim.claim_id,
            policy_id=policy_id,
            is_valid=is_valid,
            validation_reason=reason,
        )
        
        return event

