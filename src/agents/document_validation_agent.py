"""
Document Validation Agent - Validates document compliance

This agent validates that claims have the required supporting documents
based on compliance rules (claim type, amount, etc.). It integrates
with the compliance rules engine and audit system.
"""

from typing import Optional
from uuid import UUID

from ..compliance.decision_audit import get_audit_service
from ..compliance.decision_context import DecisionContextTracker
from ..compliance.document_compliance_rules import (
    ComplianceResult,
    get_compliance_engine,
)
from ..compliance.models import DecisionType
from ..domain.claim import Claim
from ..domain.claim.events import DocumentsValidated
from .base_agent import BaseAgent


class DocumentValidationAgent(BaseAgent):
    """
    Agent for validating document compliance requirements.
    
    This agent checks claims against compliance rules to ensure they
    have the required supporting documents before processing continues.
    
    DDD Role: Application Service that coordinates compliance checking
    """
    
    def __init__(self, model_provider=None, temperature: float = 0.7):
        """
        Initialize the document validation agent.
        
        Args:
            model_provider: Model provider (optional, not used for rule-based validation)
            temperature: Temperature (not used for rule-based validation)
        """
        super().__init__(model_provider or type('MockProvider', (), {'generate': lambda *args, **kwargs: ''})(), temperature)
        self.compliance_engine = get_compliance_engine()
        self.audit_service = get_audit_service()
    
    def get_system_prompt(self) -> str:
        """
        System prompt for document validation agent.
        
        Note: This agent primarily uses rule-based validation, but the
        prompt can be used for generating human-readable reports.
        """
        return """You are a Document Compliance Validator for an insurance claims processing system.
Your job is to validate that claims have the required supporting documents based on
compliance rules and regulations.

You check:
1. Required documents based on claim type (auto, property, health, etc.)
2. Required documents based on claim amount
3. Document completeness and validity
4. Compliance with insurance regulations

Generate clear, professional compliance reports."""
    
    async def validate_claim_documents(self, claim: Claim) -> DocumentsValidated:
        """
        Validate documents for a claim against compliance rules.
        
        Args:
            claim: The claim to validate
        
        Returns:
            DocumentsValidated domain event
        """
        # Initialize decision context tracker
        tracker = DecisionContextTracker()
        tracker.add_input("claim_id", str(claim.claim_id))
        tracker.add_input("claim_type", claim.summary.claim_type if claim.summary else "unknown")
        tracker.add_input("claim_amount", str(claim.summary.claimed_amount) if claim.summary else "0")
        tracker.add_input("document_count", len(claim.documents))
        
        # Evaluate compliance using rules engine
        compliance_result = self.compliance_engine.evaluate_compliance(claim)
        
        # Extract document IDs
        validated_document_ids = [
            doc.document_id
            for doc in claim.documents
            if doc.status.value in ["validated", "pending"]
        ]
        
        rejected_document_ids = [
            doc.document_id
            for doc in claim.documents
            if doc.status.value == "rejected"
        ]
        
        # Add evidence to tracker
        tracker.add_evidence("compliance_result", {
            "is_compliant": compliance_result.is_compliant,
            "violations_count": len(compliance_result.violations),
            "missing_document_types": [
                dt.value for dt in compliance_result.get_missing_document_types()
            ],
        })
        
        # Capture decision in audit trail
        reasoning = self._generate_reasoning(compliance_result)
        self.audit_service.capture_decision(
            claim_id=claim.claim_id,
            agent_component="DocumentValidationAgent",
            decision_type=DecisionType.DOCUMENT_VALIDATION,
            decision_value={
                "is_compliant": compliance_result.is_compliant,
                "violations": [
                    {
                        "rule_name": v.rule_name,
                        "missing_types": [dt.value for dt in v.missing_document_types],
                    }
                    for v in compliance_result.violations
                ],
                "missing_document_types": [
                    dt.value for dt in compliance_result.get_missing_document_types()
                ],
            },
            reasoning=reasoning,
            context=tracker.build_context(),
            success=True,
        )
        
        # Create domain event
        event = DocumentsValidated(
            claim_id=claim.claim_id,
            validated_documents=validated_document_ids,
            rejected_documents=rejected_document_ids,
            missing_document_types=compliance_result.get_missing_document_types(),
            is_compliant=compliance_result.is_compliant,
        )
        
        return event
    
    def _generate_reasoning(self, compliance_result: ComplianceResult) -> str:
        """
        Generate human-readable reasoning for compliance result.
        
        Args:
            compliance_result: Compliance evaluation result
        
        Returns:
            Reasoning string
        """
        if compliance_result.is_compliant:
            return "All document compliance requirements met. Claim has required supporting documents."
        
        violations_text = []
        for violation in compliance_result.violations:
            missing_types = [dt.value for dt in violation.missing_document_types]
            violations_text.append(
                f"{violation.rule_description}: Missing {', '.join(missing_types)}"
            )
        
        return (
            f"Document compliance violations detected: "
            f"{'; '.join(violations_text)}. "
            f"Claim requires additional documentation before processing."
        )
    
    async def process(self, input_data: Claim) -> tuple[DocumentsValidated, DocumentsValidated]:
        """
        Process a claim for document validation.
        
        This method implements the BaseAgent interface.
        
        Args:
            input_data: Claim to validate
        
        Returns:
            Tuple of (domain_event, domain_event) - same event twice for compatibility
        """
        event = await self.validate_claim_documents(input_data)
        return event, event



