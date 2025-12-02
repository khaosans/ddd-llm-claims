"""
Document-Claim Matching Domain Models

Value Objects and services for matching documents to claims,
validating required documents exist, and generating recommendations.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .document import DocumentType


@dataclass
class DocumentRequirement:
    """
    Value Object: Defines required documents for a claim type.
    
    Specifies which document types are required, optional, or recommended
    for different claim types.
    """
    claim_type: str
    required: List[DocumentType]  # Must have these
    recommended: List[DocumentType]  # Should have these
    optional: List[DocumentType]  # Nice to have
    
    def is_required(self, doc_type: DocumentType) -> bool:
        """Check if a document type is required"""
        return doc_type in self.required
    
    def is_recommended(self, doc_type: DocumentType) -> bool:
        """Check if a document type is recommended"""
        return doc_type in self.recommended


class DocumentMatchResult(BaseModel):
    """
    Value Object: Result of matching documents to a claim.
    
    Contains matching scores, mismatches, missing documents,
    and recommendations.
    """
    match_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall match score (0.0-1.0) - confidence that images match claim"
    )
    matched_elements: List[str] = Field(
        default_factory=list,
        description="List of matched aspects (e.g., 'damage_type', 'location', 'date')"
    )
    mismatches: List[str] = Field(
        default_factory=list,
        description="List of inconsistencies found between documents and claim"
    )
    missing_documents: List[DocumentType] = Field(
        default_factory=list,
        description="List of required document types not present"
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="List of actionable recommendations"
    )
    image_analysis_results: Dict[str, Dict] = Field(
        default_factory=dict,
        description="Per-image analysis results (keyed by document_id)"
    )


class DocumentClaimMatcher:
    """
    Service for matching documents to claims.
    
    Validates required documents exist and matches image content
    to claim details.
    """
    
    # Define document requirements per claim type
    REQUIREMENTS: Dict[str, DocumentRequirement] = {
        "auto": DocumentRequirement(
            claim_type="auto",
            required=[DocumentType.PHOTO],
            recommended=[DocumentType.POLICE_REPORT, DocumentType.ESTIMATE, DocumentType.REPAIR_ORDER],
            optional=[DocumentType.WITNESS_STATEMENT, DocumentType.INSURANCE_FORM],
        ),
        "property": DocumentRequirement(
            claim_type="property",
            required=[DocumentType.PHOTO],
            recommended=[DocumentType.APPRAISAL, DocumentType.ESTIMATE],
            optional=[DocumentType.POLICE_REPORT, DocumentType.INVOICE, DocumentType.RECEIPT],
        ),
        "health": DocumentRequirement(
            claim_type="health",
            required=[DocumentType.MEDICAL_RECORD],
            recommended=[DocumentType.INVOICE, DocumentType.RECEIPT],
            optional=[DocumentType.INSURANCE_FORM],
        ),
        "other": DocumentRequirement(
            claim_type="other",
            required=[],
            recommended=[DocumentType.PHOTO, DocumentType.INVOICE],
            optional=[],
        ),
    }
    
    def get_requirements(self, claim_type: str) -> DocumentRequirement:
        """
        Get document requirements for a claim type.
        
        Args:
            claim_type: Type of claim (auto, property, health, etc.)
        
        Returns:
            DocumentRequirement for the claim type
        """
        return self.REQUIREMENTS.get(claim_type.lower(), self.REQUIREMENTS["other"])
    
    def validate_required_documents(
        self,
        claim_type: str,
        documents: List,
    ) -> List[DocumentType]:
        """
        Validate that required documents exist.
        
        Args:
            claim_type: Type of claim
            documents: List of Document objects
        
        Returns:
            List of missing required document types
        """
        requirements = self.get_requirements(claim_type)
        present_types = {doc.document_type for doc in documents}
        missing = [req for req in requirements.required if req not in present_types]
        return missing
    
    def check_recommended_documents(
        self,
        claim_type: str,
        documents: List,
    ) -> List[DocumentType]:
        """
        Check which recommended documents are missing.
        
        Args:
            claim_type: Type of claim
            documents: List of Document objects
        
        Returns:
            List of missing recommended document types
        """
        requirements = self.get_requirements(claim_type)
        present_types = {doc.document_type for doc in documents}
        missing = [rec for rec in requirements.recommended if rec not in present_types]
        return missing
    
    def generate_recommendations(
        self,
        claim_type: str,
        documents: List,
        match_result: Optional[DocumentMatchResult] = None,
    ) -> List[str]:
        """
        Generate recommendations based on document validation and matching.
        
        Args:
            claim_type: Type of claim
            documents: List of Document objects
            match_result: Optional DocumentMatchResult from content matching
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Check required documents
        missing_required = self.validate_required_documents(claim_type, documents)
        if missing_required:
            doc_names = ", ".join([dt.value.replace("_", " ").title() for dt in missing_required])
            recommendations.append(
                f"Missing required documents: {doc_names}. Please upload these documents to proceed."
            )
        
        # Check recommended documents
        missing_recommended = self.check_recommended_documents(claim_type, documents)
        if missing_recommended:
            doc_names = ", ".join([dt.value.replace("_", " ").title() for dt in missing_recommended])
            recommendations.append(
                f"Recommended documents not provided: {doc_names}. These may help expedite processing."
            )
        
        # Add matching result recommendations
        if match_result:
            if match_result.mismatches:
                recommendations.append(
                    f"Found {len(match_result.mismatches)} inconsistency(ies) between documents and claim details. Please review."
                )
            
            if match_result.match_score < 0.5:
                recommendations.append(
                    "Low match score between images and claim description. Please verify images match the claim."
                )
        
        return recommendations



