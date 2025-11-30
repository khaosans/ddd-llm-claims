"""
Compliance Reporter

Generates regulatory reports and exports decision audit trails
for compliance purposes.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from .decision_audit import DecisionAuditService
from .explainability import ExplainabilityService, ExplanationLevel
from .models import DecisionRecord


class ComplianceReporter:
    """
    Service for generating compliance reports and exporting audit trails.
    
    Provides various report formats suitable for regulatory submissions
    and compliance reviews.
    """
    
    def __init__(
        self,
        audit_service: Optional[DecisionAuditService] = None,
        explainability_service: Optional[ExplainabilityService] = None,
    ):
        """
        Initialize the compliance reporter.
        
        Args:
            audit_service: DecisionAuditService instance (optional)
            explainability_service: ExplainabilityService instance (optional)
        """
        self._audit_service = audit_service
        self._explainability_service = explainability_service
    
    def generate_claim_report(
        self,
        claim_id: UUID,
        include_explanations: bool = True,
        explanation_level: ExplanationLevel = ExplanationLevel.REGULATORY,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive compliance report for a claim.
        
        Args:
            claim_id: ID of the claim
            include_explanations: Whether to include decision explanations
            explanation_level: Level of detail for explanations
            
        Returns:
            Dictionary containing the report data
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        decisions = service.get_decisions_for_claim(claim_id)
        
        report = {
            "report_type": "claim_compliance_report",
            "claim_id": str(claim_id),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": self._generate_summary(decisions),
            "decisions": [],
        }
        
        # Add decision details
        for decision in decisions:
            decision_data = {
                "decision_id": str(decision.decision_id),
                "timestamp": decision.timestamp.isoformat(),
                "agent_component": decision.agent_component,
                "decision_type": decision.decision_type.value,
                "decision_value": decision.decision_value,
                "reasoning": decision.reasoning,
                "success": decision.success,
            }
            
            if decision.confidence is not None:
                decision_data["confidence"] = decision.confidence
            
            if decision.workflow_step:
                decision_data["workflow_step"] = decision.workflow_step
            
            if decision.dependencies:
                decision_data["dependencies"] = [
                    {
                        "decision_id": str(dep.decision_id),
                        "dependency_type": dep.dependency_type,
                        "description": dep.description,
                    }
                    for dep in decision.dependencies
                ]
            
            # Add explanation if requested
            if include_explanations and self._explainability_service:
                try:
                    explanation = self._explainability_service.explain_decision(
                        decision.decision_id,
                        level=explanation_level,
                        audit_service=service,
                    )
                    decision_data["explanation"] = explanation.content
                except Exception as e:
                    decision_data["explanation_error"] = str(e)
            
            report["decisions"].append(decision_data)
        
        return report
    
    def export_audit_trail(
        self,
        claim_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json",
    ) -> str:
        """
        Export decision audit trail in specified format.
        
        Args:
            claim_id: Optional filter by claim ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            format: Export format ("json", "csv", "text")
            
        Returns:
            Exported audit trail as string
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
        
        if format == "json":
            return self._export_json(decisions)
        elif format == "csv":
            return self._export_csv(decisions)
        elif format == "text":
            return self._export_text(decisions)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def generate_regulatory_submission(
        self,
        claim_id: UUID,
    ) -> Dict[str, Any]:
        """
        Generate a formatted report suitable for regulatory submission.
        
        Args:
            claim_id: ID of the claim
            
        Returns:
            Dictionary containing regulatory submission data
        """
        service = self._audit_service
        if not service:
            from .decision_audit import get_audit_service
            service = get_audit_service()
        
        explain_service = self._explainability_service
        if not explain_service:
            explain_service = ExplainabilityService(audit_service=service)
        
        decisions = service.get_decisions_for_claim(claim_id)
        
        submission = {
            "submission_type": "regulatory_decision_report",
            "submission_date": datetime.utcnow().isoformat(),
            "claim_id": str(claim_id),
            "executive_summary": self._generate_executive_summary(decisions),
            "decision_timeline": [],
            "decision_details": [],
        }
        
        # Build timeline
        for decision in sorted(decisions, key=lambda d: d.timestamp):
            timeline_entry = {
                "timestamp": decision.timestamp.isoformat(),
                "agent": decision.agent_component,
                "decision_type": decision.decision_type.value,
                "decision": str(decision.decision_value),
                "status": "success" if decision.success else "failed",
            }
            submission["decision_timeline"].append(timeline_entry)
        
        # Add detailed explanations
        for decision in decisions:
            explanation = explain_service.explain_decision(
                decision.decision_id,
                level=ExplanationLevel.REGULATORY,
                audit_service=service,
            )
            
            detail = {
                "decision_id": str(decision.decision_id),
                "explanation": explanation.content,
                "evidence": self._extract_evidence(decision),
            }
            
            submission["decision_details"].append(detail)
        
        return submission
    
    def _generate_summary(self, decisions: List[DecisionRecord]) -> Dict[str, Any]:
        """Generate summary statistics for decisions"""
        total = len(decisions)
        successful = sum(1 for d in decisions if d.success)
        failed = total - successful
        
        decision_types = {}
        for decision in decisions:
            dt = decision.decision_type.value
            decision_types[dt] = decision_types.get(dt, 0) + 1
        
        agents = {}
        for decision in decisions:
            agent = decision.agent_component
            agents[agent] = agents.get(agent, 0) + 1
        
        return {
            "total_decisions": total,
            "successful_decisions": successful,
            "failed_decisions": failed,
            "decision_types": decision_types,
            "agents": agents,
        }
    
    def _generate_executive_summary(self, decisions: List[DecisionRecord]) -> str:
        """Generate executive summary text"""
        if not decisions:
            return "No decisions recorded for this claim."
        
        successful = sum(1 for d in decisions if d.success)
        failed = len(decisions) - successful
        
        lines = [
            f"This report documents {len(decisions)} decision(s) made during claim processing.",
            f"Successfully completed: {successful}",
            f"Failed: {failed}",
            "",
            "Decision breakdown:",
        ]
        
        decision_types = {}
        for decision in decisions:
            dt = decision.decision_type.value
            decision_types[dt] = decision_types.get(dt, 0) + 1
        
        for dt, count in decision_types.items():
            lines.append(f"  - {dt}: {count}")
        
        return "\n".join(lines)
    
    def _extract_evidence(self, decision: DecisionRecord) -> List[Dict[str, Any]]:
        """Extract evidence from decision context"""
        evidence_list = []
        
        for ev in decision.context.evidence:
            evidence_list.append({
                "type": ev.get("type", "unknown"),
                "data": ev.get("data", {}),
            })
        
        return evidence_list
    
    def _export_json(self, decisions: List[DecisionRecord]) -> str:
        """Export decisions as JSON"""
        data = {
            "export_type": "decision_audit_trail",
            "exported_at": datetime.utcnow().isoformat(),
            "total_decisions": len(decisions),
            "decisions": [self._decision_to_dict(d) for d in decisions],
        }
        return json.dumps(data, indent=2, default=str)
    
    def _export_csv(self, decisions: List[DecisionRecord]) -> str:
        """Export decisions as CSV"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "Decision ID",
            "Claim ID",
            "Timestamp",
            "Agent",
            "Decision Type",
            "Decision Value",
            "Success",
            "Reasoning",
        ])
        
        # Rows
        for decision in decisions:
            writer.writerow([
                str(decision.decision_id),
                str(decision.claim_id),
                decision.timestamp.isoformat(),
                decision.agent_component,
                decision.decision_type.value,
                str(decision.decision_value),
                decision.success,
                decision.reasoning[:100] if decision.reasoning else "",  # Truncate
            ])
        
        return output.getvalue()
    
    def _export_text(self, decisions: List[DecisionRecord]) -> str:
        """Export decisions as formatted text"""
        lines = [
            "DECISION AUDIT TRAIL",
            "=" * 60,
            f"Exported: {datetime.utcnow().isoformat()}",
            f"Total Decisions: {len(decisions)}",
            "",
        ]
        
        for decision in decisions:
            lines.extend([
                f"Decision ID: {decision.decision_id}",
                f"Claim ID: {decision.claim_id}",
                f"Timestamp: {decision.timestamp.isoformat()}",
                f"Agent: {decision.agent_component}",
                f"Type: {decision.decision_type.value}",
                f"Decision: {decision.decision_value}",
                f"Success: {decision.success}",
                f"Reasoning: {decision.reasoning}",
                "",
                "-" * 60,
                "",
            ])
        
        return "\n".join(lines)
    
    def _decision_to_dict(self, decision: DecisionRecord) -> Dict[str, Any]:
        """Convert DecisionRecord to dictionary"""
        return {
            "decision_id": str(decision.decision_id),
            "claim_id": str(decision.claim_id),
            "agent_component": decision.agent_component,
            "decision_type": decision.decision_type.value,
            "decision_value": decision.decision_value,
            "reasoning": decision.reasoning,
            "confidence": decision.confidence,
            "timestamp": decision.timestamp.isoformat(),
            "workflow_step": decision.workflow_step,
            "success": decision.success,
            "error_message": decision.error_message,
            "dependencies": [
                {
                    "decision_id": str(dep.decision_id),
                    "dependency_type": dep.dependency_type,
                    "description": dep.description,
                }
                for dep in decision.dependencies
            ],
        }

