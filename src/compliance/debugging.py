"""
Debugging Tools

Provides tools for debugging decisions including:
- Decision trace viewer
- Failure analysis
- Decision comparison
- Workflow execution traces
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from .decision_audit import DecisionAuditService
from .explainability import ExplainabilityService, ExplanationLevel
from .models import DecisionRecord


class DebuggingTools:
    """
    Tools for debugging and analyzing decisions.
    
    Provides various utilities for understanding decision flow,
    identifying failures, and comparing decisions.
    """
    
    def __init__(
        self,
        audit_service: Optional[DecisionAuditService] = None,
        explainability_service: Optional[ExplainabilityService] = None,
    ):
        """
        Initialize debugging tools.
        
        Args:
            audit_service: DecisionAuditService instance (optional)
            explainability_service: ExplainabilityService instance (optional)
        """
        self._audit_service = audit_service
        self._explainability_service = explainability_service
    
    def trace_decision_flow(
        self,
        claim_id: UUID,
        include_context: bool = True,
    ) -> Dict[str, Any]:
        """
        Trace the complete decision flow for a claim.
        
        Shows the sequence of decisions, their dependencies,
        and the flow of information through the system.
        
        Args:
            claim_id: ID of the claim to trace
            include_context: Whether to include decision context
            
        Returns:
            Dictionary containing trace information
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decisions = service.get_decisions_for_claim(claim_id)
        decisions_by_id = {d.decision_id: d for d in decisions}
        
        # Build dependency graph
        graph = {}
        for decision in decisions:
            graph[str(decision.decision_id)] = {
                "decision": decision,
                "dependencies": [str(dep.decision_id) for dep in decision.dependencies],
                "dependents": [],
            }
        
        # Find dependents
        for decision_id, node in graph.items():
            for dep_id in node["dependencies"]:
                if dep_id in graph:
                    graph[dep_id]["dependents"].append(decision_id)
        
        # Build timeline
        timeline = []
        for decision in sorted(decisions, key=lambda d: d.timestamp):
            timeline_entry = {
                "timestamp": decision.timestamp.isoformat(),
                "decision_id": str(decision.decision_id),
                "agent": decision.agent_component,
                "type": decision.decision_type.value,
                "value": str(decision.decision_value),
                "success": decision.success,
            }
            
            if include_context:
                timeline_entry["context"] = {
                    "has_prompt": decision.context.prompts is not None,
                    "has_llm_response": decision.context.llm_response is not None,
                    "evidence_count": len(decision.context.evidence),
                    "intermediate_steps": len(decision.context.intermediate_steps),
                }
            
            timeline.append(timeline_entry)
        
        return {
            "claim_id": str(claim_id),
            "total_decisions": len(decisions),
            "timeline": timeline,
            "dependency_graph": graph,
            "root_decisions": [
                str(d.decision_id)
                for d in decisions
                if not d.dependencies
            ],
            "leaf_decisions": [
                str(d_id)
                for d_id, node in graph.items()
                if not node["dependents"]
            ],
        }
    
    def analyze_failures(
        self,
        claim_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Analyze failed decisions to identify patterns and root causes.
        
        Args:
            claim_id: Optional filter by claim ID
            
        Returns:
            Dictionary containing failure analysis
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        if claim_id:
            failed = service.get_failed_decisions(claim_id=claim_id)
        else:
            failed = service.get_failed_decisions()
        
        if not failed:
            return {
                "total_failures": 0,
                "message": "No failed decisions found",
            }
        
        # Analyze failure patterns
        by_agent = {}
        by_type = {}
        error_messages = {}
        
        for decision in failed:
            # By agent
            agent = decision.agent_component
            by_agent[agent] = by_agent.get(agent, 0) + 1
            
            # By type
            dt = decision.decision_type.value
            by_type[dt] = by_type.get(dt, 0) + 1
            
            # Error messages
            if decision.error_message:
                error_msg = decision.error_message[:100]  # Truncate
                error_messages[error_msg] = error_messages.get(error_msg, 0) + 1
        
        # Get detailed explanations for failures
        failure_details = []
        explain_service = self._explainability_service
        if not explain_service:
            explain_service = ExplainabilityService(audit_service=service)
        
        for decision in failed[:10]:  # Limit to first 10 for performance
            try:
                explanation = explain_service.explain_decision(
                    decision.decision_id,
                    level=ExplanationLevel.DEBUG,
                    audit_service=service,
                )
                failure_details.append({
                    "decision_id": str(decision.decision_id),
                    "agent": decision.agent_component,
                    "type": decision.decision_type.value,
                    "error": decision.error_message,
                    "explanation": explanation.content[:500],  # Truncate
                })
            except Exception:
                failure_details.append({
                    "decision_id": str(decision.decision_id),
                    "agent": decision.agent_component,
                    "type": decision.decision_type.value,
                    "error": decision.error_message,
                    "explanation": "Unable to generate explanation",
                })
        
        return {
            "total_failures": len(failed),
            "failures_by_agent": by_agent,
            "failures_by_type": by_type,
            "common_errors": dict(sorted(error_messages.items(), key=lambda x: x[1], reverse=True)[:5]),
            "failure_details": failure_details,
        }
    
    def compare_decisions(
        self,
        decision_id_1: UUID,
        decision_id_2: UUID,
    ) -> Dict[str, Any]:
        """
        Compare two decisions to identify similarities and differences.
        
        Useful for understanding why similar inputs led to different outcomes.
        
        Args:
            decision_id_1: ID of first decision
            decision_id_2: ID of second decision
            
        Returns:
            Dictionary containing comparison results
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decision1 = service.get_decision_by_id(decision_id_1)
        decision2 = service.get_decision_by_id(decision_id_2)
        
        if not decision1 or not decision2:
            raise ValueError("One or both decisions not found")
        
        comparison = {
            "decision_1": {
                "id": str(decision1.decision_id),
                "claim_id": str(decision1.claim_id),
                "agent": decision1.agent_component,
                "type": decision1.decision_type.value,
                "value": decision1.decision_value,
                "success": decision1.success,
                "reasoning": decision1.reasoning,
            },
            "decision_2": {
                "id": str(decision2.decision_id),
                "claim_id": str(decision2.claim_id),
                "agent": decision2.agent_component,
                "type": decision2.decision_type.value,
                "value": decision2.decision_value,
                "success": decision2.success,
                "reasoning": decision2.reasoning,
            },
            "similarities": [],
            "differences": [],
        }
        
        # Compare basic attributes
        if decision1.agent_component == decision2.agent_component:
            comparison["similarities"].append("Same agent/component")
        else:
            comparison["differences"].append(
                f"Different agents: {decision1.agent_component} vs {decision2.agent_component}"
            )
        
        if decision1.decision_type == decision2.decision_type:
            comparison["similarities"].append("Same decision type")
        else:
            comparison["differences"].append(
                f"Different types: {decision1.decision_type.value} vs {decision2.decision_type.value}"
            )
        
        if decision1.success == decision2.success:
            comparison["similarities"].append(f"Both {'succeeded' if decision1.success else 'failed'}")
        else:
            comparison["differences"].append(
                f"Different outcomes: {'Success' if decision1.success else 'Failure'} vs {'Success' if decision2.success else 'Failure'}"
            )
        
        # Compare inputs
        inputs1 = set(decision1.context.inputs.keys())
        inputs2 = set(decision2.context.inputs.keys())
        
        common_inputs = inputs1 & inputs2
        if common_inputs:
            comparison["similarities"].append(f"Common inputs: {', '.join(common_inputs)}")
        
        unique_inputs_1 = inputs1 - inputs2
        unique_inputs_2 = inputs2 - inputs1
        if unique_inputs_1:
            comparison["differences"].append(f"Decision 1 unique inputs: {', '.join(unique_inputs_1)}")
        if unique_inputs_2:
            comparison["differences"].append(f"Decision 2 unique inputs: {', '.join(unique_inputs_2)}")
        
        return comparison
    
    def visualize_workflow(
        self,
        claim_id: UUID,
    ) -> Dict[str, Any]:
        """
        Generate a visualization-friendly representation of the workflow.
        
        Returns data structure suitable for rendering workflow diagrams.
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            Dictionary containing workflow visualization data
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decisions = service.get_decisions_for_claim(claim_id)
        
        # Build nodes and edges
        nodes = []
        edges = []
        
        for decision in decisions:
            nodes.append({
                "id": str(decision.decision_id),
                "label": f"{decision.agent_component}\n{decision.decision_type.value}",
                "type": decision.decision_type.value,
                "agent": decision.agent_component,
                "success": decision.success,
                "timestamp": decision.timestamp.isoformat(),
            })
            
            # Add edges for dependencies
            for dep in decision.dependencies:
                edges.append({
                    "from": str(dep.decision_id),
                    "to": str(decision.decision_id),
                    "type": dep.dependency_type,
                })
        
        # Sort nodes by timestamp
        nodes.sort(key=lambda n: n["timestamp"])
        
        return {
            "claim_id": str(claim_id),
            "nodes": nodes,
            "edges": edges,
            "total_steps": len(nodes),
            "successful_steps": sum(1 for n in nodes if n["success"]),
            "failed_steps": sum(1 for n in nodes if not n["success"]),
        }
    
    def find_decision_path(
        self,
        from_decision_id: UUID,
        to_decision_id: UUID,
    ) -> Optional[List[DecisionRecord]]:
        """
        Find the path between two decisions.
        
        Useful for understanding how one decision led to another.
        
        Args:
            from_decision_id: Starting decision ID
            to_decision_id: Target decision ID
            
        Returns:
            List of decisions in the path, or None if no path exists
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        # Use BFS to find path
        from collections import deque
        
        visited = set()
        queue = deque([(from_decision_id, [])])
        
        while queue:
            current_id, path = queue.popleft()
            
            if current_id == to_decision_id:
                # Found path, get decisions
                path.append(current_id)
                decisions = []
                for d_id in path:
                    decision = service.get_decision_by_id(d_id)
                    if decision:
                        decisions.append(decision)
                return decisions
            
            if current_id in visited:
                continue
            
            visited.add(current_id)
            
            # Find decisions that depend on current
            all_decisions = service.get_all_decisions()
            for decision in all_decisions:
                for dep in decision.dependencies:
                    if dep.decision_id == current_id:
                        new_path = path + [current_id]
                        queue.append((decision.decision_id, new_path))
        
        return None
    
    def get_decision_statistics(
        self,
        claim_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get statistics about decisions.
        
        Args:
            claim_id: Optional filter by claim ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary containing statistics
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        if claim_id:
            decisions = service.get_decisions_for_claim(claim_id)
        else:
            decisions = service.get_all_decisions(
                start_date=start_date,
                end_date=end_date,
            )
        
        if not decisions:
            return {
                "total": 0,
                "message": "No decisions found",
            }
        
        total = len(decisions)
        successful = sum(1 for d in decisions if d.success)
        failed = total - successful
        
        # By type
        by_type = {}
        for decision in decisions:
            dt = decision.decision_type.value
            by_type[dt] = by_type.get(dt, 0) + 1
        
        # By agent
        by_agent = {}
        for decision in decisions:
            agent = decision.agent_component
            by_agent[agent] = by_agent.get(agent, 0) + 1
        
        # Confidence statistics
        confidences = [d.confidence for d in decisions if d.confidence is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None
        
        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "by_type": by_type,
            "by_agent": by_agent,
            "average_confidence": avg_confidence,
            "min_confidence": min(confidences) if confidences else None,
            "max_confidence": max(confidences) if confidences else None,
        }

