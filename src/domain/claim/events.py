"""
Domain Events for Claim Intake Bounded Context

Domain Events represent something important that happened in the domain.
They are immutable facts that occurred at a specific point in time.
"""

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import Field

from ..events import DomainEvent
from .claim_summary import ClaimSummary
from .document import Document, DocumentType


class ClaimFactsExtracted(DomainEvent):
    """
    Domain Event: Claim facts have been successfully extracted.
    
    This event is published when the Intake Agent successfully extracts
    structured facts from unstructured customer data. It triggers the
    workflow orchestrator to proceed with policy validation and fraud assessment.
    
    DDD Pattern: Domain Events enable loose coupling between bounded contexts.
    The Claim Intake context publishes this event, and other contexts
    (Policy Management, Fraud Assessment) can react to it without
    direct dependencies.
    """
    
    claim_id: UUID = Field(description="ID of the claim for which facts were extracted")
    summary: ClaimSummary = Field(description="The extracted claim summary (Value Object)")
    extracted_at: datetime = Field(default_factory=datetime.utcnow, description="When facts were extracted")


class DocumentAdded(DomainEvent):
    """
    Domain Event: A supporting document has been added to a claim.
    
    This event is published when a document is attached to a claim.
    It triggers document validation and authenticity checks.
    
    DDD Pattern: Domain Events enable loose coupling between bounded contexts.
    The Claim Intake context publishes this event, and the Document Validation
    context can react to it.
    """
    
    claim_id: UUID = Field(description="ID of the claim the document was added to")
    document_id: UUID = Field(description="ID of the document that was added")
    document_type: DocumentType = Field(description="Type of document that was added")
    added_at: datetime = Field(default_factory=datetime.utcnow, description="When the document was added")


class DocumentsValidated(DomainEvent):
    """
    Domain Event: Document validation has been completed for a claim.
    
    This event is published when document compliance validation completes.
    It indicates which documents passed validation and which are missing or rejected.
    
    DDD Pattern: Domain Events enable loose coupling between bounded contexts.
    The Document Validation context publishes this event, and the workflow
    orchestrator can react to it.
    """
    
    claim_id: UUID = Field(description="ID of the claim for which documents were validated")
    validated_documents: List[UUID] = Field(default_factory=list, description="IDs of documents that passed validation")
    rejected_documents: List[UUID] = Field(default_factory=list, description="IDs of documents that failed validation")
    missing_document_types: List[DocumentType] = Field(default_factory=list, description="Types of documents that are required but missing")
    is_compliant: bool = Field(description="Whether the claim meets all document compliance requirements")
    validated_at: datetime = Field(default_factory=datetime.utcnow, description="When validation was completed")


class DocumentAuthenticityChecked(DomainEvent):
    """
    Domain Event: Document authenticity check has been completed.
    
    This event is published when authenticity checking completes for a document.
    It includes authenticity scores and any suspicious findings.
    
    DDD Pattern: Domain Events enable loose coupling between bounded contexts.
    The Document Authenticity context publishes this event, and the fraud
    assessment context can react to it.
    """
    
    claim_id: UUID = Field(description="ID of the claim the document belongs to")
    document_id: UUID = Field(description="ID of the document that was checked")
    authenticity_score: float = Field(ge=0.0, le=1.0, description="Authenticity score (0.0-1.0)")
    is_suspicious: bool = Field(description="Whether the document shows signs of tampering or fraud")
    findings: List[str] = Field(default_factory=list, description="List of findings from authenticity check")
    checked_at: datetime = Field(default_factory=datetime.utcnow, description="When the check was completed")


class DocumentMatched(DomainEvent):
    """
    Domain Event: Document-claim matching has been completed.
    
    This event is published when document matching completes for a claim.
    It includes match scores, mismatches, missing documents, and recommendations.
    
    DDD Pattern: Domain Events enable loose coupling between bounded contexts.
    The Document Matching context publishes this event, and the workflow
    orchestrator can react to it.
    """
    
    claim_id: UUID = Field(description="ID of the claim for which documents were matched")
    match_score: float = Field(ge=0.0, le=1.0, description="Overall match score (0.0-1.0)")
    matched_elements: List[str] = Field(default_factory=list, description="List of matched aspects")
    mismatches: List[str] = Field(default_factory=list, description="List of inconsistencies found")
    missing_documents: List[DocumentType] = Field(default_factory=list, description="List of required document types not present")
    recommendations: List[str] = Field(default_factory=list, description="List of actionable recommendations")
    matched_at: datetime = Field(default_factory=datetime.utcnow, description="When matching was completed")

