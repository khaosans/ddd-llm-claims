"""
Completion Summary - Post-completion summaries with guidance

Provides comprehensive summaries after claim processing completion,
including findings, guidance, and actionable recommendations.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from .decision_audit import DecisionAuditService
from .explainability import ExplainabilityService, ExplanationLevel
from .models import DecisionType


class CompletionSummary:
    """
    Service for generating completion summaries with guidance and findings.
    
    Provides:
    - Executive summary
    - Detailed findings
    - Recommendations
    - Audit guidance
    - Next steps
    """
    
    def __init__(
        self,
        audit_service: Optional[DecisionAuditService] = None,
        explainability_service: Optional[ExplainabilityService] = None,
    ):
        """
        Initialize the completion summary service.
        
        Args:
            audit_service: DecisionAuditService instance (optional)
            explainability_service: ExplainabilityService instance (optional)
        """
        self._audit_service = audit_service
        self._explainability_service = explainability_service
    
    def generate_completion_summary(
        self,
        claim_id: UUID,
        include_explanations: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive completion summary.
        
        Args:
            claim_id: ID of the claim
            include_explanations: Whether to include decision explanations
            
        Returns:
            Dictionary with completion summary
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decisions = service.get_decisions_for_claim(claim_id)
        
        if not decisions:
            return {
                "claim_id": str(claim_id),
                "status": "no_decisions",
                "message": "No decisions recorded for this claim",
            }
        
        # Generate summary sections
        executive_summary = self._generate_executive_summary(decisions)
        findings = self._generate_findings(decisions)
        recommendations = self._generate_recommendations(decisions)
        decision_timeline = self._generate_decision_timeline(decisions)
        audit_guidance = self._generate_audit_guidance(decisions)
        
        # Include explanations if requested
        explanations = {}
        if include_explanations and self._explainability_service:
            explain_service = self._explainability_service
            if not explain_service._audit_service:
                explain_service._audit_service = service
            
            for decision in decisions:
                try:
                    explanation = explain_service.explain_decision(
                        decision.decision_id,
                        level=ExplanationLevel.SUMMARY,
                        audit_service=service,
                    )
                    explanations[str(decision.decision_id)] = explanation.content
                except Exception:
                    pass
        
        return {
            "claim_id": str(claim_id),
            "generated_at": self._get_timestamp(),
            "executive_summary": executive_summary,
            "findings": findings,
            "recommendations": recommendations,
            "decision_timeline": decision_timeline,
            "audit_guidance": audit_guidance,
            "explanations": explanations if explanations else None,
            "quick_stats": self._generate_quick_stats(decisions),
        }
    
    def _generate_executive_summary(self, decisions: List) -> Dict[str, Any]:
        """Generate executive summary"""
        total = len(decisions)
        successful = sum(1 for d in decisions if d.success)
        failed = total - successful
        
        # Identify key outcomes
        key_outcomes = []
        for decision in decisions:
            if decision.decision_type == DecisionType.POLICY_VALIDATION:
                if isinstance(decision.decision_value, dict):
                    is_valid = decision.decision_value.get("is_valid", False)
                    key_outcomes.append({
                        "type": "policy_validation",
                        "outcome": "valid" if is_valid else "invalid",
                        "impact": "high",
                    })
            
            if decision.decision_type == DecisionType.TRIAGE_ROUTING:
                if isinstance(decision.decision_value, dict):
                    routing = decision.decision_value.get("routing_decision", "")
                    key_outcomes.append({
                        "type": "routing",
                        "outcome": routing,
                        "impact": "high",
                    })
        
        return {
            "total_decisions": total,
            "successful_decisions": successful,
            "failed_decisions": failed,
            "success_rate": f"{(successful / total * 100):.1f}%" if total > 0 else "0%",
            "overall_status": "completed" if failed == 0 else "completed_with_issues",
            "key_outcomes": key_outcomes,
            "requires_review": failed > 0 or any(
                isinstance(d.decision_value, dict) and 
                d.decision_value.get("routing_decision") == "fraud_investigation"
                for d in decisions
                if d.decision_type == DecisionType.TRIAGE_ROUTING
            ),
        }
    
    def _generate_findings(self, decisions: List) -> List[Dict[str, Any]]:
        """Generate findings from decisions"""
        findings = []
        
        for decision in decisions:
            # Failure findings
            if not decision.success:
                findings.append({
                    "type": "failure",
                    "severity": "high",
                    "step": decision.workflow_step or decision.decision_type.value,
                    "agent": decision.agent_component,
                    "finding": f"Decision failed: {decision.error_message}",
                    "impact": "Workflow may be blocked or require manual intervention",
                })
            
            # Policy validation findings
            if decision.decision_type == DecisionType.POLICY_VALIDATION:
                if isinstance(decision.decision_value, dict):
                    is_valid = decision.decision_value.get("is_valid", False)
                    if not is_valid:
                        findings.append({
                            "type": "policy_issue",
                            "severity": "high",
                            "step": "policy_validation",
                            "finding": f"Policy validation failed: {decision.reasoning}",
                            "impact": "Claim may be rejected or require policy review",
                        })
            
            # Fraud assessment findings
            if decision.decision_type == DecisionType.FRAUD_ASSESSMENT:
                if isinstance(decision.decision_value, dict):
                    fraud_score = decision.decision_value.get("fraud_score", 0)
                    if fraud_score > 0.7:
                        findings.append({
                            "type": "fraud_risk",
                            "severity": "critical",
                            "step": "fraud_assessment",
                            "finding": f"High fraud risk detected: score {fraud_score}",
                            "impact": "Requires immediate fraud investigation",
                        })
            
            # Low confidence findings
            if decision.confidence is not None and decision.confidence < 0.7:
                findings.append({
                    "type": "low_confidence",
                    "severity": "medium",
                    "step": decision.workflow_step or decision.decision_type.value,
                    "finding": f"Low confidence decision: {decision.confidence:.1%}",
                    "impact": "Decision may benefit from human review",
                })
        
        return findings
    
    def _generate_recommendations(self, decisions: List) -> List[Dict[str, Any]]:
        """Generate recommendations based on decisions"""
        recommendations = []
        
        # Check for failures
        failures = [d for d in decisions if not d.success]
        if failures:
            recommendations.append({
                "priority": "high",
                "category": "error_recovery",
                "recommendation": f"Review and resolve {len(failures)} failed decision(s)",
                "action_items": [
                    f"Investigate failure in {d.workflow_step or d.decision_type.value}"
                    for d in failures
                ],
            })
        
        # Check policy validation
        policy_decisions = [d for d in decisions if d.decision_type == DecisionType.POLICY_VALIDATION]
        for decision in policy_decisions:
            if isinstance(decision.decision_value, dict):
                is_valid = decision.decision_value.get("is_valid", False)
                if not is_valid:
                    recommendations.append({
                        "priority": "high",
                        "category": "policy_review",
                        "recommendation": "Review policy validation failure",
                        "action_items": [
                            "Verify policy details",
                            "Check claim eligibility",
                            "Consider policy exceptions if applicable",
                        ],
                    })
        
        # Check fraud assessment
        fraud_decisions = [d for d in decisions if d.decision_type == DecisionType.FRAUD_ASSESSMENT]
        for decision in fraud_decisions:
            if isinstance(decision.decision_value, dict):
                fraud_score = decision.decision_value.get("fraud_score", 0)
                if fraud_score > 0.7:
                    recommendations.append({
                        "priority": "critical",
                        "category": "fraud_investigation",
                        "recommendation": "Immediate fraud investigation required",
                        "action_items": [
                            "Escalate to fraud investigation team",
                            "Gather additional evidence",
                            "Review claim history",
                        ],
                    })
        
        # Check routing
        routing_decisions = [d for d in decisions if d.decision_type == DecisionType.TRIAGE_ROUTING]
        for decision in routing_decisions:
            if isinstance(decision.decision_value, dict):
                routing = decision.decision_value.get("routing_decision", "")
                if routing == "fraud_investigation":
                    recommendations.append({
                        "priority": "high",
                        "category": "routing_review",
                        "recommendation": "Verify fraud investigation routing",
                        "action_items": [
                            "Confirm routing decision is appropriate",
                            "Ensure proper investigation procedures",
                        ],
                    })
        
        # Check document matching
        matching_decisions = [d for d in decisions if d.decision_type == DecisionType.DOCUMENT_MATCHING]
        for decision in matching_decisions:
            if isinstance(decision.decision_value, dict):
                match_score = decision.decision_value.get("match_score", 1.0)
                missing_docs = decision.decision_value.get("missing_documents", [])
                mismatches = decision.decision_value.get("mismatches", [])
                recs = decision.decision_value.get("recommendations", [])
                
                # Missing required documents
                if missing_docs:
                    recommendations.append({
                        "priority": "high",
                        "category": "document_requirements",
                        "recommendation": f"Missing {len(missing_docs)} required document(s)",
                        "action_items": [
                            f"Upload missing documents: {', '.join(missing_docs)}",
                            "Verify all required documents are provided",
                        ] + recs[:3],  # Include first 3 recommendations
                    })
                
                # Low match score
                if match_score < 0.5:
                    recommendations.append({
                        "priority": "medium",
                        "category": "document_matching",
                        "recommendation": f"Low match score ({match_score:.2f}) between documents and claim",
                        "action_items": [
                            "Review images to ensure they match claim description",
                            "Verify dates, locations, and damage descriptions match",
                        ] + (mismatches[:3] if mismatches else []),
                    })
                
                # Mismatches found
                if mismatches and match_score >= 0.5:
                    recommendations.append({
                        "priority": "medium",
                        "category": "document_consistency",
                        "recommendation": f"Found {len(mismatches)} inconsistency(ies) between documents and claim",
                        "action_items": mismatches[:5],  # Top 5 mismatches
                    })
        
        return recommendations
    
    def _generate_decision_timeline(self, decisions: List) -> List[Dict[str, Any]]:
        """Generate decision timeline"""
        timeline = []
        
        for decision in sorted(decisions, key=lambda d: d.timestamp):
            timeline.append({
                "timestamp": decision.timestamp.isoformat(),
                "step": decision.workflow_step or decision.decision_type.value,
                "agent": decision.agent_component,
                "decision_type": decision.decision_type.value,
                "status": "success" if decision.success else "failed",
                "summary": decision.reasoning[:100] + "..." if len(decision.reasoning) > 100 else decision.reasoning,
            })
        
        return timeline
    
    def _generate_audit_guidance(self, decisions: List) -> Dict[str, Any]:
        """Generate audit guidance"""
        # Identify areas requiring attention
        attention_areas = []
        
        failures = [d for d in decisions if not d.success]
        if failures:
            attention_areas.append({
                "area": "Failed Decisions",
                "count": len(failures),
                "priority": "high",
                "guidance": "Review each failure to understand root cause and determine if retry is appropriate",
            })
        
        policy_issues = [
            d for d in decisions
            if d.decision_type == DecisionType.POLICY_VALIDATION
            and isinstance(d.decision_value, dict)
            and not d.decision_value.get("is_valid", True)
        ]
        if policy_issues:
            attention_areas.append({
                "area": "Policy Validation Issues",
                "count": len(policy_issues),
                "priority": "high",
                "guidance": "Verify policy details and claim eligibility. Consider policy exceptions if applicable.",
            })
        
        high_fraud = [
            d for d in decisions
            if d.decision_type == DecisionType.FRAUD_ASSESSMENT
            and isinstance(d.decision_value, dict)
            and d.decision_value.get("fraud_score", 0) > 0.7
        ]
        if high_fraud:
            attention_areas.append({
                "area": "High Fraud Risk",
                "count": len(high_fraud),
                "priority": "critical",
                "guidance": "Immediate fraud investigation required. Review all evidence and claim history.",
            })
        
        return {
            "review_required": len(attention_areas) > 0,
            "attention_areas": attention_areas,
            "review_checklist": [
                "All decisions completed successfully",
                "Policy validation passed",
                "Fraud assessment within acceptable range",
                "Routing decision appropriate",
                "No critical errors",
            ],
            "review_priority": "critical" if any(a["priority"] == "critical" for a in attention_areas) else "high" if attention_areas else "normal",
        }
    
    def _generate_quick_stats(self, decisions: List) -> Dict[str, Any]:
        """Generate quick statistics"""
        total = len(decisions)
        successful = sum(1 for d in decisions if d.success)
        
        by_type = {}
        for decision in decisions:
            dt = decision.decision_type.value
            by_type[dt] = by_type.get(dt, 0) + 1
        
        by_agent = {}
        for decision in decisions:
            agent = decision.agent_component
            by_agent[agent] = by_agent.get(agent, 0) + 1
        
        confidences = [d.confidence for d in decisions if d.confidence is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None
        
        return {
            "total_decisions": total,
            "success_rate": f"{(successful / total * 100):.1f}%" if total > 0 else "0%",
            "decisions_by_type": by_type,
            "decisions_by_agent": by_agent,
            "average_confidence": f"{avg_confidence:.1%}" if avg_confidence else None,
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as ISO string"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

