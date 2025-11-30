"""
Decision Viewer - Real-time decision viewing and monitoring

Provides real-time access to decisions as they're being made,
enabling monitoring and quick auditing during workflow execution.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from .decision_audit import DecisionAuditService
from .models import DecisionRecord, DecisionType


class DecisionViewer:
    """
    Service for viewing decisions in real-time and providing quick audit capabilities.
    
    Enables:
    - Real-time decision monitoring
    - Quick audit summaries
    - Step-by-step decision viewing
    - Guidance and findings
    """
    
    def __init__(self, audit_service: Optional[DecisionAuditService] = None):
        """
        Initialize the decision viewer.
        
        Args:
            audit_service: DecisionAuditService instance (optional)
        """
        self._audit_service = audit_service
    
    def get_current_step_decisions(
        self,
        claim_id: UUID,
        workflow_step: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get decisions for the current workflow step.
        
        Args:
            claim_id: ID of the claim
            workflow_step: Optional workflow step name
            
        Returns:
            List of decision summaries for current step
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decisions = service.get_decisions_for_claim(claim_id)
        
        # Filter by workflow step if provided
        if workflow_step:
            decisions = [d for d in decisions if d.workflow_step == workflow_step]
        
        # Return most recent decisions first
        decisions = sorted(decisions, key=lambda d: d.timestamp, reverse=True)
        
        return [self._format_decision_summary(d) for d in decisions]
    
    def get_workflow_progress(
        self,
        claim_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get workflow progress with current step and decisions made so far.
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            Dictionary with workflow progress information
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decisions = service.get_decisions_for_claim(claim_id)
        
        if not decisions:
            return {
                "claim_id": str(claim_id),
                "status": "not_started",
                "current_step": None,
                "steps_completed": [],
                "next_steps": ["claim_creation", "fact_extraction"],
                "total_decisions": 0,
            }
        
        # Sort by timestamp
        decisions = sorted(decisions, key=lambda d: d.timestamp)
        
        # Identify workflow steps
        steps = {}
        for decision in decisions:
            step = decision.workflow_step or decision.decision_type.value
            if step not in steps:
                steps[step] = {
                    "step_name": step,
                    "decisions": [],
                    "status": "completed" if decision.success else "failed",
                    "completed_at": decision.timestamp.isoformat(),
                }
            steps[step]["decisions"].append(self._format_decision_summary(decision))
        
        steps_completed = list(steps.keys())
        current_step = steps_completed[-1] if steps_completed else None
        
        # Determine next steps based on current state
        next_steps = self._determine_next_steps(decisions)
        
        return {
            "claim_id": str(claim_id),
            "status": "in_progress" if any(not d.success for d in decisions) else "completed",
            "current_step": current_step,
            "steps_completed": steps_completed,
            "next_steps": next_steps,
            "total_decisions": len(decisions),
            "steps": steps,
            "has_failures": any(not d.success for d in decisions),
        }
    
    def get_quick_audit_summary(
        self,
        claim_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get a quick audit summary for human review.
        
        Provides:
        - Key decisions made
        - Issues/findings
        - Recommendations
        - Quick status overview
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            Dictionary with quick audit summary
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
        
        # Analyze decisions
        key_decisions = []
        issues = []
        recommendations = []
        
        for decision in sorted(decisions, key=lambda d: d.timestamp):
            # Identify key decisions
            if decision.decision_type in [
                DecisionType.FACT_EXTRACTION,
                DecisionType.POLICY_VALIDATION,
                DecisionType.TRIAGE_ROUTING,
            ]:
                key_decisions.append({
                    "step": decision.workflow_step or decision.decision_type.value,
                    "agent": decision.agent_component,
                    "decision": str(decision.decision_value)[:100],
                    "reasoning": decision.reasoning[:200],
                    "timestamp": decision.timestamp.isoformat(),
                    "success": decision.success,
                })
            
            # Identify issues
            if not decision.success:
                issues.append({
                    "step": decision.workflow_step or decision.decision_type.value,
                    "agent": decision.agent_component,
                    "error": decision.error_message,
                    "severity": "high" if decision.decision_type == DecisionType.POLICY_VALIDATION else "medium",
                })
            
            # Generate recommendations based on decision patterns
            if decision.decision_type == DecisionType.POLICY_VALIDATION:
                if not decision.success or (isinstance(decision.decision_value, dict) and not decision.decision_value.get("is_valid", True)):
                    recommendations.append({
                        "type": "review_required",
                        "message": "Policy validation failed or invalid - manual review recommended",
                        "priority": "high",
                    })
            
            if decision.decision_type == DecisionType.TRIAGE_ROUTING:
                if isinstance(decision.decision_value, dict):
                    routing = decision.decision_value.get("routing_decision", "")
                    if routing == "fraud_investigation":
                        recommendations.append({
                            "type": "investigation",
                            "message": "Claim routed to fraud investigation - requires specialist review",
                            "priority": "high",
                        })
        
        # Overall status
        failed_count = sum(1 for d in decisions if not d.success)
        success_rate = (len(decisions) - failed_count) / len(decisions) if decisions else 0
        
        return {
            "claim_id": str(claim_id),
            "overview": {
                "total_decisions": len(decisions),
                "successful": len(decisions) - failed_count,
                "failed": failed_count,
                "success_rate": f"{success_rate:.1%}",
                "status": "healthy" if success_rate >= 0.9 else "needs_review" if success_rate >= 0.7 else "critical",
            },
            "key_decisions": key_decisions,
            "issues": issues,
            "recommendations": recommendations,
            "requires_human_review": len(issues) > 0 or len(recommendations) > 0,
        }
    
    def get_step_by_step_view(
        self,
        claim_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get a step-by-step view of all decisions made.
        
        Provides chronological view with context for each step.
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            Dictionary with step-by-step decision view
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decisions = service.get_decisions_for_claim(claim_id)
        decisions = sorted(decisions, key=lambda d: d.timestamp)
        
        steps = []
        for i, decision in enumerate(decisions):
            step_info = {
                "step_number": i + 1,
                "step_name": decision.workflow_step or decision.decision_type.value,
                "timestamp": decision.timestamp.isoformat(),
                "agent": decision.agent_component,
                "decision_type": decision.decision_type.value,
                "decision": self._format_decision_value(decision.decision_value),
                "decision_value": decision.decision_value,  # Include raw value for analysis
                "reasoning": decision.reasoning,
                "success": decision.success,
                "has_context": bool(decision.context.inputs or decision.context.evidence),
            }
            
            if not decision.success:
                step_info["error"] = decision.error_message
            
            if decision.confidence is not None:
                step_info["confidence"] = f"{decision.confidence:.1%}"
            
            if decision.dependencies:
                step_info["depends_on"] = [
                    {
                        "decision_id": str(dep.decision_id),
                        "type": dep.dependency_type,
                    }
                    for dep in decision.dependencies
                ]
            
            steps.append(step_info)
        
        return {
            "claim_id": str(claim_id),
            "total_steps": len(steps),
            "steps": steps,
            "timeline": [
                {
                    "time": step["timestamp"],
                    "step": step["step_name"],
                    "status": "success" if step["success"] else "failed",
                }
                for step in steps
            ],
        }
    
    def get_audit_guidance(
        self,
        claim_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get audit guidance and findings for human reviewers.
        
        Provides:
        - What to look for
        - Key findings
        - Red flags
        - Review checklist
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            Dictionary with audit guidance
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decisions = service.get_decisions_for_claim(claim_id)
        
        findings = []
        red_flags = []
        checklist = []
        
        # Analyze decisions for findings
        for decision in decisions:
            # Check for failures
            if not decision.success:
                red_flags.append({
                    "type": "decision_failure",
                    "step": decision.workflow_step or decision.decision_type.value,
                    "agent": decision.agent_component,
                    "issue": decision.error_message,
                    "action_required": "Review decision failure and determine if retry is needed",
                })
            
            # Check policy validation
            if decision.decision_type == DecisionType.POLICY_VALIDATION:
                checklist.append({
                    "item": "Policy validation completed",
                    "status": "completed" if decision.success else "failed",
                    "details": decision.reasoning,
                })
                
                if isinstance(decision.decision_value, dict):
                    is_valid = decision.decision_value.get("is_valid", False)
                    if not is_valid:
                        findings.append({
                            "type": "policy_issue",
                            "severity": "high",
                            "message": f"Policy validation failed: {decision.reasoning}",
                            "recommendation": "Review policy details and claim eligibility",
                        })
            
            # Check fraud assessment
            if decision.decision_type == DecisionType.FRAUD_ASSESSMENT:
                checklist.append({
                    "item": "Fraud assessment completed",
                    "status": "completed" if decision.success else "failed",
                    "details": decision.reasoning,
                })
                
                if isinstance(decision.decision_value, dict):
                    fraud_score = decision.decision_value.get("fraud_score", 0)
                    if fraud_score > 0.7:
                        red_flags.append({
                            "type": "high_fraud_risk",
                            "step": "fraud_assessment",
                            "issue": f"High fraud score: {fraud_score}",
                            "action_required": "Immediate fraud investigation required",
                        })
            
            # Check routing decisions
            if decision.decision_type == DecisionType.TRIAGE_ROUTING:
                checklist.append({
                    "item": "Claim routing determined",
                    "status": "completed" if decision.success else "failed",
                    "details": decision.reasoning,
                })
                
                if isinstance(decision.decision_value, dict):
                    routing = decision.decision_value.get("routing_decision", "")
                    if routing == "fraud_investigation":
                        findings.append({
                            "type": "routing_alert",
                            "severity": "high",
                            "message": "Claim routed to fraud investigation",
                            "recommendation": "Ensure proper fraud investigation procedures are followed",
                        })
        
        # Generate review checklist
        review_checklist = [
            {
                "item": "All workflow steps completed",
                "status": "completed" if len(decisions) >= 3 else "pending",
            },
            {
                "item": "No decision failures",
                "status": "completed" if all(d.success for d in decisions) else "failed",
            },
            {
                "item": "Policy validation passed",
                "status": "check_required",
            },
            {
                "item": "Fraud assessment completed",
                "status": "check_required",
            },
            {
                "item": "Routing decision appropriate",
                "status": "check_required",
            },
        ]
        
        return {
            "claim_id": str(claim_id),
            "audit_summary": {
                "total_decisions": len(decisions),
                "decisions_requiring_review": len([d for d in decisions if not d.success or d.decision_type == DecisionType.TRIAGE_ROUTING]),
                "red_flags_count": len(red_flags),
            },
            "findings": findings,
            "red_flags": red_flags,
            "checklist": review_checklist,
            "guidance": {
                "focus_areas": [
                    "Policy validation results",
                    "Fraud assessment scores",
                    "Routing decisions",
                    "Any decision failures",
                ],
                "review_priority": "high" if red_flags else "normal",
            },
        }
    
    def _format_decision_summary(self, decision: DecisionRecord) -> Dict[str, Any]:
        """Format a decision for summary view"""
        return {
            "decision_id": str(decision.decision_id),
            "step": decision.workflow_step or decision.decision_type.value,
            "agent": decision.agent_component,
            "type": decision.decision_type.value,
            "decision": self._format_decision_value(decision.decision_value),
            "reasoning": decision.reasoning[:150] + "..." if len(decision.reasoning) > 150 else decision.reasoning,
            "success": decision.success,
            "timestamp": decision.timestamp.isoformat(),
            "has_error": decision.error_message is not None,
        }
    
    def _format_decision_value(self, value: Any) -> str:
        """Format decision value for display"""
        if isinstance(value, dict):
            # Extract key information
            if "routing_decision" in value:
                return f"Routed to: {value['routing_decision']}"
            if "is_valid" in value:
                return f"Policy valid: {value['is_valid']}"
            if "fraud_score" in value:
                return f"Fraud score: {value['fraud_score']}"
            return str(value)[:100]
        return str(value)[:100]
    
    def _determine_next_steps(self, decisions: List[DecisionRecord]) -> List[str]:
        """Determine next steps based on current decisions"""
        completed_types = {d.decision_type for d in decisions if d.success}
        
        next_steps = []
        
        if DecisionType.FACT_EXTRACTION not in completed_types:
            next_steps.append("fact_extraction")
        elif DecisionType.POLICY_VALIDATION not in completed_types:
            next_steps.append("policy_validation")
        elif DecisionType.FRAUD_ASSESSMENT not in completed_types:
            next_steps.append("fraud_assessment")
        elif DecisionType.TRIAGE_ROUTING not in completed_types:
            next_steps.append("triage_routing")
        else:
            next_steps.append("workflow_complete")
        
        return next_steps

