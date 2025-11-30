"""
Tests for Compliance and Explainability Framework

Tests decision capture, explanation generation, and debugging tools.
"""

import pytest
from datetime import datetime
from uuid import UUID, uuid4

from src.compliance.decision_audit import DecisionAuditService, get_audit_service, set_audit_service
from src.compliance.decision_context import DecisionContextTracker
from src.compliance.explainability import ExplainabilityService, ExplanationLevel
from src.compliance.reporter import ComplianceReporter
from src.compliance.debugging import DebuggingTools
from src.compliance.models import (
    DecisionRecord,
    DecisionType,
    DecisionContext,
    DecisionDependency,
)


@pytest.fixture
def audit_service():
    """Create a fresh audit service for each test"""
    service = DecisionAuditService(enable_persistence=False)
    set_audit_service(service)
    return service


@pytest.fixture
def sample_claim_id():
    """Sample claim ID for testing"""
    return uuid4()


@pytest.fixture
def sample_decision(audit_service, sample_claim_id):
    """Create a sample decision for testing"""
    return audit_service.capture_decision(
        claim_id=sample_claim_id,
        agent_component="TestAgent",
        decision_type=DecisionType.FACT_EXTRACTION,
        decision_value={"claim_type": "auto", "amount": "5000.00"},
        reasoning="Test decision for unit testing",
        confidence=0.95,
        success=True,
    )


class TestDecisionAuditService:
    """Tests for DecisionAuditService"""
    
    def test_capture_decision(self, audit_service, sample_claim_id):
        """Test capturing a decision"""
        decision = audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="TestAgent",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="test_value",
            reasoning="Test reasoning",
        )
        
        assert decision.claim_id == sample_claim_id
        assert decision.agent_component == "TestAgent"
        assert decision.decision_type == DecisionType.FACT_EXTRACTION
        assert decision.decision_value == "test_value"
        assert decision.reasoning == "Test reasoning"
        assert decision.success is True
    
    def test_get_decisions_for_claim(self, audit_service, sample_claim_id):
        """Test retrieving decisions for a claim"""
        # Create multiple decisions
        decision1 = audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="reason1",
        )
        
        decision2 = audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent2",
            decision_type=DecisionType.POLICY_VALIDATION,
            decision_value="value2",
            reasoning="reason2",
        )
        
        # Get all decisions for claim
        decisions = audit_service.get_decisions_for_claim(sample_claim_id)
        assert len(decisions) == 2
        
        # Filter by type
        extraction_decisions = audit_service.get_decisions_for_claim(
            sample_claim_id,
            decision_type=DecisionType.FACT_EXTRACTION,
        )
        assert len(extraction_decisions) == 1
        assert extraction_decisions[0].decision_id == decision1.decision_id
    
    def test_get_failed_decisions(self, audit_service, sample_claim_id):
        """Test retrieving failed decisions"""
        # Create successful and failed decisions
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="success",
            success=True,
        )
        
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent2",
            decision_type=DecisionType.POLICY_VALIDATION,
            decision_value=None,
            reasoning="failed",
            success=False,
            error_message="Test error",
        )
        
        failed = audit_service.get_failed_decisions(sample_claim_id)
        assert len(failed) == 1
        assert failed[0].success is False
        assert failed[0].error_message == "Test error"
    
    def test_get_decision_chain(self, audit_service, sample_claim_id):
        """Test retrieving decision chain"""
        # Create dependent decisions
        decision1 = audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="reason1",
        )
        
        decision2 = audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent2",
            decision_type=DecisionType.POLICY_VALIDATION,
            decision_value="value2",
            reasoning="reason2",
            dependencies=[
                DecisionDependency(
                    decision_id=decision1.decision_id,
                    dependency_type="required_for",
                )
            ],
        )
        
        chain = audit_service.get_decision_chain(decision2.decision_id)
        assert len(chain) == 2
        assert chain[0].decision_id == decision1.decision_id
        assert chain[1].decision_id == decision2.decision_id


class TestDecisionContextTracker:
    """Tests for DecisionContextTracker"""
    
    def test_add_inputs(self):
        """Test adding inputs to context"""
        tracker = DecisionContextTracker()
        tracker.add_input("key1", "value1")
        tracker.add_inputs({"key2": "value2", "key3": 123})
        
        context = tracker.build_context()
        assert context.inputs["key1"] == "value1"
        assert context.inputs["key2"] == "value2"
        assert context.inputs["key3"] == 123
    
    def test_set_prompt_and_response(self):
        """Test setting prompt and LLM response"""
        tracker = DecisionContextTracker()
        tracker.set_prompt("Test prompt")
        tracker.set_llm_response("Test response")
        
        context = tracker.build_context()
        assert context.prompts == "Test prompt"
        assert context.llm_response == "Test response"
    
    def test_add_evidence(self):
        """Test adding evidence"""
        tracker = DecisionContextTracker()
        tracker.add_evidence("policy_check", {"is_valid": True})
        
        context = tracker.build_context()
        assert len(context.evidence) == 1
        assert context.evidence[0]["type"] == "policy_check"
        assert context.evidence[0]["data"]["is_valid"] is True


class TestExplainabilityService:
    """Tests for ExplainabilityService"""
    
    def test_explain_decision_summary(self, audit_service, sample_decision):
        """Test generating summary explanation"""
        service = ExplainabilityService(audit_service=audit_service)
        explanation = service.explain_decision(
            sample_decision.decision_id,
            level=ExplanationLevel.SUMMARY,
        )
        
        assert explanation.decision_id == sample_decision.decision_id
        assert explanation.level == ExplanationLevel.SUMMARY
        assert "Decision" in explanation.content
        assert "TestAgent" in explanation.content
    
    def test_explain_decision_detailed(self, audit_service, sample_decision):
        """Test generating detailed explanation"""
        service = ExplainabilityService(audit_service=audit_service)
        explanation = service.explain_decision(
            sample_decision.decision_id,
            level=ExplanationLevel.DETAILED,
        )
        
        assert explanation.level == ExplanationLevel.DETAILED
        assert "DECISION EXPLANATION" in explanation.content
        assert "REASONING" in explanation.content
    
    def test_explain_decision_regulatory(self, audit_service, sample_decision):
        """Test generating regulatory explanation"""
        service = ExplainabilityService(audit_service=audit_service)
        explanation = service.explain_decision(
            sample_decision.decision_id,
            level=ExplanationLevel.REGULATORY,
        )
        
        assert explanation.level == ExplanationLevel.REGULATORY
        assert "REGULATORY DECISION REPORT" in explanation.content
    
    def test_explain_claim_decisions(self, audit_service, sample_claim_id):
        """Test explaining all decisions for a claim"""
        # Create multiple decisions
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="reason1",
        )
        
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent2",
            decision_type=DecisionType.POLICY_VALIDATION,
            decision_value="value2",
            reasoning="reason2",
        )
        
        service = ExplainabilityService(audit_service=audit_service)
        explanations = service.explain_claim_decisions(
            sample_claim_id,
            level=ExplanationLevel.SUMMARY,
        )
        
        assert len(explanations) == 2


class TestComplianceReporter:
    """Tests for ComplianceReporter"""
    
    def test_generate_claim_report(self, audit_service, sample_claim_id):
        """Test generating claim report"""
        # Create decisions
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="reason1",
        )
        
        reporter = ComplianceReporter(audit_service=audit_service)
        report = reporter.generate_claim_report(sample_claim_id)
        
        assert report["claim_id"] == str(sample_claim_id)
        assert report["report_type"] == "claim_compliance_report"
        assert len(report["decisions"]) == 1
        assert report["summary"]["total_decisions"] == 1
    
    def test_export_audit_trail_json(self, audit_service, sample_claim_id):
        """Test exporting audit trail as JSON"""
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="reason1",
        )
        
        reporter = ComplianceReporter(audit_service=audit_service)
        export = reporter.export_audit_trail(
            claim_id=sample_claim_id,
            format="json",
        )
        
        import json
        data = json.loads(export)
        assert data["export_type"] == "decision_audit_trail"
        assert len(data["decisions"]) == 1
    
    def test_generate_regulatory_submission(self, audit_service, sample_claim_id):
        """Test generating regulatory submission"""
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="reason1",
        )
        
        reporter = ComplianceReporter(
            audit_service=audit_service,
            explainability_service=ExplainabilityService(audit_service=audit_service),
        )
        submission = reporter.generate_regulatory_submission(sample_claim_id)
        
        assert submission["submission_type"] == "regulatory_decision_report"
        assert submission["claim_id"] == str(sample_claim_id)
        assert "executive_summary" in submission
        assert len(submission["decision_timeline"]) == 1


class TestDebuggingTools:
    """Tests for DebuggingTools"""
    
    def test_trace_decision_flow(self, audit_service, sample_claim_id):
        """Test tracing decision flow"""
        # Create decisions with dependencies
        decision1 = audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="reason1",
        )
        
        decision2 = audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent2",
            decision_type=DecisionType.POLICY_VALIDATION,
            decision_value="value2",
            reasoning="reason2",
            dependencies=[
                DecisionDependency(
                    decision_id=decision1.decision_id,
                    dependency_type="required_for",
                )
            ],
        )
        
        tools = DebuggingTools(audit_service=audit_service)
        trace = tools.trace_decision_flow(sample_claim_id)
        
        assert trace["claim_id"] == str(sample_claim_id)
        assert trace["total_decisions"] == 2
        assert len(trace["timeline"]) == 2
        assert len(trace["dependency_graph"]) == 2
    
    def test_analyze_failures(self, audit_service, sample_claim_id):
        """Test analyzing failures"""
        # Create successful and failed decisions
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="success",
            success=True,
        )
        
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent2",
            decision_type=DecisionType.POLICY_VALIDATION,
            decision_value=None,
            reasoning="failed",
            success=False,
            error_message="Test error",
        )
        
        tools = DebuggingTools(
            audit_service=audit_service,
            explainability_service=ExplainabilityService(audit_service=audit_service),
        )
        analysis = tools.analyze_failures(sample_claim_id)
        
        assert analysis["total_failures"] == 1
        assert "Agent2" in analysis["failures_by_agent"]
        assert len(analysis["failure_details"]) > 0
    
    def test_get_decision_statistics(self, audit_service, sample_claim_id):
        """Test getting decision statistics"""
        # Create multiple decisions
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent1",
            decision_type=DecisionType.FACT_EXTRACTION,
            decision_value="value1",
            reasoning="reason1",
            confidence=0.9,
            success=True,
        )
        
        audit_service.capture_decision(
            claim_id=sample_claim_id,
            agent_component="Agent2",
            decision_type=DecisionType.POLICY_VALIDATION,
            decision_value="value2",
            reasoning="reason2",
            confidence=0.8,
            success=True,
        )
        
        tools = DebuggingTools(audit_service=audit_service)
        stats = tools.get_decision_statistics(claim_id=sample_claim_id)
        
        assert stats["total"] == 2
        assert stats["successful"] == 2
        assert stats["failed"] == 0
        assert stats["success_rate"] == 1.0
        assert DecisionType.FACT_EXTRACTION.value in stats["by_type"]
        assert DecisionType.POLICY_VALIDATION.value in stats["by_type"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

