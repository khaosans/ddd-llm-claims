"""
Document Compliance Rules Engine

Defines and evaluates compliance rules for required supporting documents
based on claim type, amount, and other factors. Ensures claims have
appropriate documentation before processing.
"""

from decimal import Decimal
from typing import List, Set
from uuid import UUID

from ..domain.claim import Claim
from ..domain.claim.document import Document, DocumentType


class ComplianceRule:
    """
    Represents a single compliance rule for document requirements.
    """
    
    def __init__(
        self,
        name: str,
        required_document_types: List[DocumentType],
        condition: callable = None,
        description: str = "",
    ):
        """
        Initialize a compliance rule.
        
        Args:
            name: Name of the rule
            required_document_types: List of document types required by this rule
            condition: Optional callable that takes a Claim and returns True if rule applies
            description: Human-readable description of the rule
        """
        self.name = name
        self.required_document_types = required_document_types
        self.condition = condition or (lambda claim: True)  # Default: always applies
        self.description = description
    
    def applies_to(self, claim: Claim) -> bool:
        """
        Check if this rule applies to the given claim.
        
        Args:
            claim: The claim to check
        
        Returns:
            True if rule applies, False otherwise
        """
        return self.condition(claim)
    
    def get_missing_documents(self, claim: Claim) -> List[DocumentType]:
        """
        Get list of required document types that are missing from the claim.
        
        Args:
            claim: The claim to check
        
        Returns:
            List of missing document types
        """
        if not self.applies_to(claim):
            return []
        
        existing_types = {doc.document_type for doc in claim.documents}
        missing = [
            doc_type
            for doc_type in self.required_document_types
            if doc_type not in existing_types
        ]
        return missing


class DocumentComplianceRulesEngine:
    """
    Engine for evaluating document compliance rules.
    
    This engine checks claims against a set of compliance rules to ensure
    they have the required supporting documents before processing.
    """
    
    def __init__(self):
        """Initialize the compliance rules engine with default rules."""
        self.rules: List[ComplianceRule] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize default compliance rules."""
        
        # Rule 1: Auto claims require police report if accident involved another vehicle
        self.rules.append(ComplianceRule(
            name="auto_police_report",
            required_document_types=[DocumentType.POLICE_REPORT],
            condition=lambda claim: (
                claim.summary is not None
                and claim.summary.claim_type == "auto"
                # In a real system, we'd check if accident involved another vehicle
                # For now, we'll require it for all auto claims
            ),
            description="Auto insurance claims require a police report",
        ))
        
        # Rule 2: Property claims require photos
        self.rules.append(ComplianceRule(
            name="property_photos",
            required_document_types=[DocumentType.PHOTO],
            condition=lambda claim: (
                claim.summary is not None
                and claim.summary.claim_type == "property"
            ),
            description="Property insurance claims require photos of damage",
        ))
        
        # Rule 3: Health claims require medical records
        self.rules.append(ComplianceRule(
            name="health_medical_records",
            required_document_types=[DocumentType.MEDICAL_RECORD],
            condition=lambda claim: (
                claim.summary is not None
                and claim.summary.claim_type == "health"
            ),
            description="Health insurance claims require medical records",
        ))
        
        # Rule 4: High-value claims (>$50K) require additional documentation
        self.rules.append(ComplianceRule(
            name="high_value_documentation",
            required_document_types=[
                DocumentType.INVOICE,
                DocumentType.RECEIPT,
                DocumentType.APPRAISAL,
            ],
            condition=lambda claim: (
                claim.summary is not None
                and claim.summary.claimed_amount > Decimal("50000")
            ),
            description="Claims over $50,000 require invoices, receipts, or appraisals",
        ))
        
        # Rule 5: All claims require at least one supporting document
        self.rules.append(ComplianceRule(
            name="minimum_documentation",
            required_document_types=[DocumentType.OTHER],  # Any document type
            condition=lambda claim: True,  # Applies to all claims
            description="All claims require at least one supporting document",
            # Special handling: check if any document exists
        ))
    
    def add_rule(self, rule: ComplianceRule) -> None:
        """
        Add a custom compliance rule.
        
        Args:
            rule: ComplianceRule to add
        """
        self.rules.append(rule)
    
    def evaluate_compliance(self, claim: Claim) -> "ComplianceResult":
        """
        Evaluate a claim against all compliance rules.
        
        Args:
            claim: The claim to evaluate
        
        Returns:
            ComplianceResult with compliance status and details
        """
        violations: List["ComplianceViolation"] = []
        applied_rules: List[str] = []
        
        for rule in self.rules:
            if not rule.applies_to(claim):
                continue
            
            applied_rules.append(rule.name)
            
            # Special handling for minimum_documentation rule
            if rule.name == "minimum_documentation":
                if len(claim.documents) == 0:
                    violations.append(ComplianceViolation(
                        rule_name=rule.name,
                        rule_description=rule.description,
                        missing_document_types=[DocumentType.OTHER],
                        severity="error",
                    ))
            else:
                missing_docs = rule.get_missing_documents(claim)
                if missing_docs:
                    violations.append(ComplianceViolation(
                        rule_name=rule.name,
                        rule_description=rule.description,
                        missing_document_types=missing_docs,
                        severity="error",
                    ))
        
        is_compliant = len(violations) == 0
        
        return ComplianceResult(
            claim_id=claim.claim_id,
            is_compliant=is_compliant,
            violations=violations,
            applied_rules=applied_rules,
        )
    
    def get_required_document_types(self, claim: Claim) -> Set[DocumentType]:
        """
        Get all document types required for a claim based on applicable rules.
        
        Args:
            claim: The claim to check
        
        Returns:
            Set of required document types
        """
        required_types: Set[DocumentType] = set()
        
        for rule in self.rules:
            if rule.applies_to(claim):
                required_types.update(rule.required_document_types)
        
        return required_types


class ComplianceViolation:
    """
    Represents a compliance violation (missing required documents).
    """
    
    def __init__(
        self,
        rule_name: str,
        rule_description: str,
        missing_document_types: List[DocumentType],
        severity: str = "error",
    ):
        """
        Initialize a compliance violation.
        
        Args:
            rule_name: Name of the rule that was violated
            rule_description: Description of the rule
            missing_document_types: List of missing document types
            severity: Severity level ("error", "warning")
        """
        self.rule_name = rule_name
        self.rule_description = rule_description
        self.missing_document_types = missing_document_types
        self.severity = severity


class ComplianceResult:
    """
    Result of compliance evaluation for a claim.
    """
    
    def __init__(
        self,
        claim_id: UUID,
        is_compliant: bool,
        violations: List[ComplianceViolation],
        applied_rules: List[str],
    ):
        """
        Initialize compliance result.
        
        Args:
            claim_id: ID of the claim evaluated
            is_compliant: Whether the claim is compliant
            violations: List of compliance violations
            applied_rules: List of rule names that were applied
        """
        self.claim_id = claim_id
        self.is_compliant = is_compliant
        self.violations = violations
        self.applied_rules = applied_rules
    
    def get_missing_document_types(self) -> List[DocumentType]:
        """
        Get all missing document types from violations.
        
        Returns:
            List of missing document types (deduplicated)
        """
        missing_types: Set[DocumentType] = set()
        for violation in self.violations:
            missing_types.update(violation.missing_document_types)
        return list(missing_types)


# Global instance
_compliance_engine: DocumentComplianceRulesEngine = None


def get_compliance_engine() -> DocumentComplianceRulesEngine:
    """
    Get the global compliance rules engine instance.
    
    Returns:
        DocumentComplianceRulesEngine instance
    """
    global _compliance_engine
    if _compliance_engine is None:
        _compliance_engine = DocumentComplianceRulesEngine()
    return _compliance_engine

