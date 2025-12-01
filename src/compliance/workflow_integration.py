"""
Workflow Integration Helpers

Provides easy access to decision viewing and summaries during workflow execution.
Can be used by UI components, APIs, or monitoring systems.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from .decision_viewer import DecisionViewer
from .completion_summary import CompletionSummary
from .decision_audit import DecisionAuditService, get_audit_service


class WorkflowDecisionMonitor:
    """
    Monitor for viewing decisions during workflow execution.
    
    Provides convenient methods for:
    - Getting current step decisions
    - Viewing workflow progress
    - Quick audit summaries
    - Step-by-step views
    """
    
    def __init__(
        self,
        audit_service: Optional[DecisionAuditService] = None,
    ):
        """
        Initialize the workflow decision monitor.
        
        Args:
            audit_service: DecisionAuditService instance (optional)
        """
        self._audit_service = audit_service or get_audit_service()
        self._viewer = DecisionViewer(audit_service=self._audit_service)
        self._summary = CompletionSummary(audit_service=self._audit_service)
    
    def get_current_status(
        self,
        claim_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get current workflow status with decisions made so far.
        
        Quick method to check what's happening with a claim.
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            Dictionary with current status
        """
        progress = self._viewer.get_workflow_progress(claim_id)
        quick_audit = self._viewer.get_quick_audit_summary(claim_id)
        
        return {
            "claim_id": str(claim_id),
            "progress": progress,
            "quick_audit": quick_audit,
            "has_issues": quick_audit.get("requires_human_review", False),
        }
    
    def get_step_decisions(
        self,
        claim_id: UUID,
        step_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get decisions for a specific step or current step.
        
        Args:
            claim_id: ID of the claim
            step_name: Optional step name (if None, gets current step)
            
        Returns:
            Dictionary with step decisions
        """
        if step_name is None:
            progress = self._viewer.get_workflow_progress(claim_id)
            step_name = progress.get("current_step")
        
        decisions = self._viewer.get_current_step_decisions(claim_id, step_name)
        
        return {
            "claim_id": str(claim_id),
            "step": step_name,
            "decisions": decisions,
            "decision_count": len(decisions),
        }
    
    def get_all_steps_view(
        self,
        claim_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get complete step-by-step view of all decisions.
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            Dictionary with all steps and decisions
        """
        return self._viewer.get_step_by_step_view(claim_id)
    
    def get_audit_summary(
        self,
        claim_id: UUID,
    ) -> Dict[str, Any]:
        """
        Get quick audit summary for human review.
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            Dictionary with audit summary, findings, and guidance
        """
        quick_audit = self._viewer.get_quick_audit_summary(claim_id)
        audit_guidance = self._viewer.get_audit_guidance(claim_id)
        
        return {
            "claim_id": str(claim_id),
            "summary": quick_audit,
            "guidance": audit_guidance,
            "requires_review": quick_audit.get("requires_human_review", False) or audit_guidance.get("audit_summary", {}).get("red_flags_count", 0) > 0,
        }
    
    def get_completion_summary(
        self,
        claim_id: UUID,
        include_explanations: bool = True,
    ) -> Dict[str, Any]:
        """
        Get comprehensive completion summary.
        
        Use this after workflow completion to get full summary with findings and recommendations.
        
        Args:
            claim_id: ID of the claim
            include_explanations: Whether to include decision explanations
            
        Returns:
            Dictionary with completion summary
        """
        return self._summary.generate_completion_summary(
            claim_id,
            include_explanations=include_explanations,
        )


# Global instance for easy access
_monitor: Optional[WorkflowDecisionMonitor] = None


def get_decision_monitor() -> WorkflowDecisionMonitor:
    """
    Get the global decision monitor instance.
    
    Returns:
        WorkflowDecisionMonitor instance
    """
    global _monitor
    if _monitor is None:
        _monitor = WorkflowDecisionMonitor()
    return _monitor


def set_decision_monitor(monitor: WorkflowDecisionMonitor) -> None:
    """
    Set the global decision monitor instance.
    
    Useful for testing or dependency injection.
    
    Args:
        monitor: WorkflowDecisionMonitor instance
    """
    global _monitor
    _monitor = monitor


# Convenience functions for quick access
def view_current_decisions(claim_id: UUID) -> Dict[str, Any]:
    """
    Quick function to view current decisions for a claim.
    
    Args:
        claim_id: ID of the claim
        
    Returns:
        Dictionary with current decisions
    """
    monitor = get_decision_monitor()
    return monitor.get_current_status(claim_id)


def get_audit_summary(claim_id: UUID) -> Dict[str, Any]:
    """
    Quick function to get audit summary for a claim.
    
    Args:
        claim_id: ID of the claim
        
    Returns:
        Dictionary with audit summary
    """
    monitor = get_decision_monitor()
    return monitor.get_audit_summary(claim_id)


def get_completion_summary(claim_id: UUID) -> Dict[str, Any]:
    """
    Quick function to get completion summary for a claim.
    
    Args:
        claim_id: ID of the claim
        
    Returns:
        Dictionary with completion summary
    """
    monitor = get_decision_monitor()
    return monitor.get_completion_summary(claim_id)


