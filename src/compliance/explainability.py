"""
Explainability Service

Generates human-readable explanations for decisions at different detail levels:
- Summary: High-level explanation
- Detailed: Full reasoning with evidence
- Regulatory: Formatted for compliance reports
- Debug: Technical details for developers
"""

import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from .models import (
    DecisionRecord,
    Explanation,
    ExplanationLevel,
    DecisionType,
)
from .decision_audit import DecisionAuditService


class ExplainabilityService:
    """
    Service for generating explanations of decisions.
    
    Provides multiple explanation formats suitable for different audiences:
    - Business users (summary)
    - Compliance officers (detailed, regulatory)
    - Developers (debug)
    """
    
    def __init__(self, audit_service: Optional[DecisionAuditService] = None):
        """
        Initialize the explainability service.
        
        Args:
            audit_service: DecisionAuditService instance (optional)
        """
        self._audit_service = audit_service
        self._explanations: List[Explanation] = []
    
    def explain_decision(
        self,
        decision_id: UUID,
        level: ExplanationLevel = ExplanationLevel.DETAILED,
        audit_service: Optional[DecisionAuditService] = None,
    ) -> Explanation:
        """
        Generate an explanation for a decision.
        
        Args:
            decision_id: ID of the decision to explain
            level: Level of detail for the explanation
            audit_service: Optional audit service (uses instance default if not provided)
            
        Returns:
            Explanation object
        """
        service = audit_service or self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decision = service.get_decision_by_id(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        # Generate explanation based on level
        if level == ExplanationLevel.SUMMARY:
            content = self._generate_summary(decision, service)
        elif level == ExplanationLevel.DETAILED:
            content = self._generate_detailed(decision, service)
        elif level == ExplanationLevel.REGULATORY:
            content = self._generate_regulatory(decision, service)
        elif level == ExplanationLevel.DEBUG:
            content = self._generate_debug(decision, service)
        else:
            content = self._generate_detailed(decision, service)
        
        explanation = Explanation(
            decision_id=decision_id,
            level=level,
            content=content,
            format="text",
        )
        
        self._explanations.append(explanation)
        return explanation
    
    def explain_claim_decisions(
        self,
        claim_id: UUID,
        level: ExplanationLevel = ExplanationLevel.DETAILED,
        audit_service: Optional[DecisionAuditService] = None,
    ) -> Dict[str, Explanation]:
        """
        Generate explanations for all decisions related to a claim.
        
        Args:
            claim_id: ID of the claim
            level: Level of detail for explanations
            audit_service: Optional audit service
            
        Returns:
            Dictionary mapping decision IDs to explanations
        """
        service = audit_service or self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decisions = service.get_decisions_for_claim(claim_id)
        explanations = {}
        
        for decision in decisions:
            explanation = self.explain_decision(
                decision.decision_id,
                level=level,
                audit_service=service,
            )
            explanations[str(decision.decision_id)] = explanation
        
        return explanations
    
    def _generate_summary(self, decision: DecisionRecord, service: DecisionAuditService) -> str:
        """Generate a high-level summary explanation"""
        lines = [
            f"Decision: {decision.decision_type.value}",
            f"Agent: {decision.agent_component}",
            f"Result: {self._format_decision_value(decision.decision_value)}",
        ]
        
        if decision.reasoning:
            lines.append(f"Reason: {decision.reasoning}")
        
        if decision.confidence is not None:
            lines.append(f"Confidence: {decision.confidence:.2%}")
        
        if not decision.success:
            lines.append(f"Status: Failed - {decision.error_message}")
        
        return "\n".join(lines)
    
    def _generate_detailed(self, decision: DecisionRecord, service: DecisionAuditService) -> str:
        """Generate a detailed explanation with evidence"""
        lines = [
            "=" * 60,
            "DECISION EXPLANATION",
            "=" * 60,
            "",
            f"Decision ID: {decision.decision_id}",
            f"Type: {decision.decision_type.value}",
            f"Agent/Component: {decision.agent_component}",
            f"Timestamp: {decision.timestamp.isoformat()}",
            f"Claim ID: {decision.claim_id}",
            "",
            "DECISION:",
            f"  {self._format_decision_value(decision.decision_value)}",
            "",
            "REASONING:",
            f"  {decision.reasoning}",
            "",
        ]
        
        if decision.confidence is not None:
            lines.append(f"CONFIDENCE: {decision.confidence:.2%}")
            lines.append("")
        
        # Add context information
        if decision.context.inputs:
            lines.append("INPUTS:")
            for key, value in decision.context.inputs.items():
                lines.append(f"  {key}: {self._format_value(value)}")
            lines.append("")
        
        # Add evidence
        if decision.context.evidence:
            lines.append("EVIDENCE:")
            for evidence in decision.context.evidence:
                lines.append(f"  Type: {evidence.get('type', 'unknown')}")
                for key, value in evidence.get('data', {}).items():
                    if key != 'type':
                        lines.append(f"    {key}: {self._format_value(value)}")
            lines.append("")
        
        # Add dependencies
        if decision.dependencies:
            lines.append("DEPENDENCIES:")
            for dep in decision.dependencies:
                dep_decision = service.get_decision_by_id(dep.decision_id)
                if dep_decision:
                    lines.append(
                        f"  - {dep.dependency_type}: {dep_decision.decision_type.value} "
                        f"(ID: {dep.decision_id})"
                    )
                else:
                    lines.append(f"  - {dep.dependency_type}: Decision {dep.decision_id}")
            lines.append("")
        
        if decision.workflow_step:
            lines.append(f"WORKFLOW STEP: {decision.workflow_step}")
            lines.append("")
        
        if not decision.success:
            lines.append(f"STATUS: FAILED")
            lines.append(f"ERROR: {decision.error_message}")
            lines.append("")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _generate_regulatory(self, decision: DecisionRecord, service: DecisionAuditService) -> str:
        """Generate a regulatory-compliant explanation"""
        lines = [
            "REGULATORY DECISION REPORT",
            "",
            f"Report Date: {decision.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Claim ID: {decision.claim_id}",
            f"Decision ID: {decision.decision_id}",
            "",
            "DECISION DETAILS:",
            f"  Decision Type: {decision.decision_type.value}",
            f"  Decision Maker: {decision.agent_component}",
            f"  Decision: {self._format_decision_value(decision.decision_value)}",
            "",
            "DECISION RATIONALE:",
            f"  {decision.reasoning}",
            "",
        ]
        
        # Regulatory requirements: show evidence
        if decision.context.evidence:
            lines.append("SUPPORTING EVIDENCE:")
            for evidence in decision.context.evidence:
                lines.append(f"  - {evidence.get('type', 'unknown')}: {self._format_evidence(evidence)}")
            lines.append("")
        
        # Show decision chain
        if decision.dependencies:
            lines.append("DECISION DEPENDENCIES:")
            for dep in decision.dependencies:
                dep_decision = service.get_decision_by_id(dep.decision_id)
                if dep_decision:
                    lines.append(
                        f"  - Depends on: {dep_decision.decision_type.value} "
                        f"made by {dep_decision.agent_component} "
                        f"at {dep_decision.timestamp.isoformat()}"
                    )
            lines.append("")
        
        if decision.confidence is not None:
            lines.append(f"CONFIDENCE LEVEL: {decision.confidence:.2%}")
            lines.append("")
        
        lines.append("END OF REPORT")
        
        return "\n".join(lines)
    
    def _generate_debug(self, decision: DecisionRecord, service: DecisionAuditService) -> str:
        """Generate a debug-level explanation with technical details"""
        lines = [
            "DEBUG DECISION TRACE",
            "",
            f"Decision ID: {decision.decision_id}",
            f"Claim ID: {decision.claim_id}",
            f"Type: {decision.decision_type.value}",
            f"Agent: {decision.agent_component}",
            f"Timestamp: {decision.timestamp.isoformat()}",
            f"Success: {decision.success}",
            "",
            "DECISION VALUE:",
            json.dumps(decision.decision_value, indent=2, default=str),
            "",
            "REASONING:",
            decision.reasoning,
            "",
        ]
        
        # Full context dump
        lines.append("FULL CONTEXT:")
        lines.append(json.dumps(decision.context.model_dump(), indent=2, default=str))
        lines.append("")
        
        # LLM details if available
        if decision.context.prompts:
            lines.append("PROMPT:")
            lines.append(decision.context.prompts)
            lines.append("")
        
        if decision.context.llm_response:
            lines.append("LLM RESPONSE:")
            lines.append(decision.context.llm_response)
            lines.append("")
        
        # Intermediate steps
        if decision.context.intermediate_steps:
            lines.append("INTERMEDIATE STEPS:")
            for step in decision.context.intermediate_steps:
                lines.append(f"  Step: {step.get('step', 'unknown')}")
                lines.append(f"  Data: {json.dumps(step.get('data', {}), indent=4, default=str)}")
            lines.append("")
        
        # Dependencies
        if decision.dependencies:
            lines.append("DEPENDENCIES:")
            for dep in decision.dependencies:
                lines.append(f"  - {dep.dependency_type}: {dep.decision_id}")
                if dep.description:
                    lines.append(f"    Description: {dep.description}")
            lines.append("")
        
        # Metadata
        if decision.context.metadata:
            lines.append("METADATA:")
            lines.append(json.dumps(decision.context.metadata, indent=2, default=str))
            lines.append("")
        
        if not decision.success:
            lines.append(f"ERROR: {decision.error_message}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_decision_value(self, value: Any) -> str:
        """Format a decision value for display"""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, dict):
            return json.dumps(value, indent=2, default=str)
        if isinstance(value, list):
            return json.dumps(value, indent=2, default=str)
        return str(value)
    
    def _format_value(self, value: Any) -> str:
        """Format a value for display"""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, dict):
            return json.dumps(value, indent=4, default=str)
        if isinstance(value, list):
            return json.dumps(value, indent=4, default=str)
        return str(value)
    
    def _format_evidence(self, evidence: Dict[str, Any]) -> str:
        """Format evidence for regulatory report"""
        data = evidence.get('data', {})
        if isinstance(data, dict):
            # Extract key information
            key_info = []
            for key, value in data.items():
                if key not in ['type', 'timestamp']:
                    key_info.append(f"{key}={value}")
            return ", ".join(key_info)
        return str(data)


# Re-export ExplanationLevel for convenience
__all__ = ["ExplainabilityService", "ExplanationLevel"]

