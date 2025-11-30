"""
Decision Audit Service

Core service for capturing and storing all agent decisions with full context.
Provides immutable audit trail for compliance and debugging.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from .models import (
    DecisionRecord,
    DecisionType,
    DecisionContext,
    DecisionDependency,
)
from .decision_context import DecisionContextTracker


class DecisionAuditService:
    """
    Service for auditing decisions made by agents and components.
    
    This service provides an immutable audit trail of all decisions,
    capturing who made what decision, when, why, and with what context.
    """
    
    def __init__(self, enable_persistence: bool = True):
        """
        Initialize the decision audit service.
        
        Args:
            enable_persistence: Whether to persist decisions (default: True)
        """
        self._decisions: List[DecisionRecord] = []
        self._enable_persistence = enable_persistence
        # In production, this would connect to a database
        # For now, we use in-memory storage
    
    def capture_decision(
        self,
        claim_id: UUID,
        agent_component: str,
        decision_type: DecisionType,
        decision_value: Any,
        reasoning: str,
        context: Optional[DecisionContext] = None,
        confidence: Optional[float] = None,
        dependencies: Optional[List[DecisionDependency]] = None,
        workflow_step: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> DecisionRecord:
        """
        Capture a decision made by an agent or component.
        
        Args:
            claim_id: ID of the claim this decision relates to
            agent_component: Name of the agent/component making the decision
            decision_type: Type of decision
            decision_value: The actual decision value
            reasoning: Explanation of why this decision was made
            context: Full context and evidence (optional)
            confidence: Confidence score 0.0-1.0 (optional)
            dependencies: List of decision dependencies (optional)
            workflow_step: Workflow step this belongs to (optional)
            success: Whether decision was successful (default: True)
            error_message: Error message if failed (optional)
            
        Returns:
            DecisionRecord that was created
        """
        decision = DecisionRecord(
            claim_id=claim_id,
            agent_component=agent_component,
            decision_type=decision_type,
            decision_value=self._serialize_decision_value(decision_value),
            reasoning=reasoning,
            confidence=confidence,
            context=context or DecisionContext(),
            dependencies=dependencies or [],
            workflow_step=workflow_step,
            success=success,
            error_message=error_message,
        )
        
        self._decisions.append(decision)
        
        if self._enable_persistence:
            # In production, persist to database here
            self._persist_decision(decision)
        
        return decision
    
    def get_decisions_for_claim(
        self,
        claim_id: UUID,
        decision_type: Optional[DecisionType] = None,
    ) -> List[DecisionRecord]:
        """
        Get all decisions for a specific claim.
        
        Args:
            claim_id: ID of the claim
            decision_type: Optional filter by decision type
            
        Returns:
            List of DecisionRecord objects
        """
        decisions = [d for d in self._decisions if d.claim_id == claim_id]
        
        if decision_type:
            decisions = [d for d in decisions if d.decision_type == decision_type]
        
        return sorted(decisions, key=lambda d: d.timestamp)
    
    def get_decision_by_id(self, decision_id: UUID) -> Optional[DecisionRecord]:
        """
        Get a specific decision by ID.
        
        Args:
            decision_id: ID of the decision
            
        Returns:
            DecisionRecord or None if not found
        """
        for decision in self._decisions:
            if decision.decision_id == decision_id:
                return decision
        return None
    
    def get_decisions_by_agent(
        self,
        agent_component: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[DecisionRecord]:
        """
        Get all decisions made by a specific agent.
        
        Args:
            agent_component: Name of the agent/component
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of DecisionRecord objects
        """
        decisions = [d for d in self._decisions if d.agent_component == agent_component]
        
        if start_date:
            decisions = [d for d in decisions if d.timestamp >= start_date]
        
        if end_date:
            decisions = [d for d in decisions if d.timestamp <= end_date]
        
        return sorted(decisions, key=lambda d: d.timestamp)
    
    def get_failed_decisions(
        self,
        claim_id: Optional[UUID] = None,
    ) -> List[DecisionRecord]:
        """
        Get all failed decisions.
        
        Args:
            claim_id: Optional filter by claim ID
            
        Returns:
            List of failed DecisionRecord objects
        """
        decisions = [d for d in self._decisions if not d.success]
        
        if claim_id:
            decisions = [d for d in decisions if d.claim_id == claim_id]
        
        return sorted(decisions, key=lambda d: d.timestamp)
    
    def get_decision_chain(
        self,
        decision_id: UUID,
    ) -> List[DecisionRecord]:
        """
        Get the full chain of decisions leading to and from a decision.
        
        This includes dependencies and decisions that depend on this one.
        
        Args:
            decision_id: ID of the decision to trace
            
        Returns:
            List of DecisionRecord objects in chronological order
        """
        decision = self.get_decision_by_id(decision_id)
        if not decision:
            return []
        
        # Get all related decisions
        related_ids = {decision_id}
        
        # Add dependencies
        for dep in decision.dependencies:
            related_ids.add(dep.decision_id)
        
        # Find decisions that depend on this one
        for d in self._decisions:
            for dep in d.dependencies:
                if dep.decision_id == decision_id:
                    related_ids.add(d.decision_id)
        
        # Get all related decisions
        related = [d for d in self._decisions if d.decision_id in related_ids]
        
        return sorted(related, key=lambda d: d.timestamp)
    
    def get_all_decisions(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[DecisionRecord]:
        """
        Get all decisions with optional date filtering.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of all DecisionRecord objects
        """
        decisions = self._decisions.copy()
        
        if start_date:
            decisions = [d for d in decisions if d.timestamp >= start_date]
        
        if end_date:
            decisions = [d for d in decisions if d.timestamp <= end_date]
        
        return sorted(decisions, key=lambda d: d.timestamp)
    
    def _serialize_decision_value(self, value: Any) -> Any:
        """
        Serialize decision value for storage.
        
        Args:
            value: Decision value to serialize
            
        Returns:
            Serialized value
        """
        # Handle common types
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        
        # Handle UUID
        if isinstance(value, UUID):
            return str(value)
        
        # Handle Pydantic models
        if hasattr(value, "model_dump"):
            return value.model_dump()
        
        # Handle dict
        if isinstance(value, dict):
            return {k: self._serialize_decision_value(v) for k, v in value.items()}
        
        # Handle list
        if isinstance(value, list):
            return [self._serialize_decision_value(item) for item in value]
        
        # Handle objects with __dict__
        if hasattr(value, "__dict__"):
            return {
                k: self._serialize_decision_value(v)
                for k, v in value.__dict__.items()
            }
        
        # Fallback to string
        return str(value)
    
    def _persist_decision(self, decision: DecisionRecord) -> None:
        """
        Persist a decision to storage.
        
        In production, this would write to a database.
        For now, it's a no-op (decisions are stored in memory).
        
        Args:
            decision: DecisionRecord to persist
        """
        # TODO: Implement database persistence
        pass


# Global instance (in production, use dependency injection)
_audit_service: Optional[DecisionAuditService] = None


def get_audit_service() -> DecisionAuditService:
    """
    Get the global audit service instance.
    
    Returns:
        DecisionAuditService instance
    """
    global _audit_service
    if _audit_service is None:
        _audit_service = DecisionAuditService()
    return _audit_service


def set_audit_service(service: DecisionAuditService) -> None:
    """
    Set the global audit service instance.
    
    Useful for testing or dependency injection.
    
    Args:
        service: DecisionAuditService instance
    """
    global _audit_service
    _audit_service = service

