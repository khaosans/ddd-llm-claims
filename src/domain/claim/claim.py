"""
Claim - Aggregate Root

⚠️ DEMONSTRATION SYSTEM - NOT FOR PRODUCTION USE
This is an educational demonstration system. See DISCLAIMERS.md for details.

In DDD, an Aggregate is a cluster of domain objects treated as a single unit
(Evans, 2003; Vernon, 2013). The Aggregate Root is the only entry point for
accessing objects within the aggregate.

Claim is the Aggregate Root for the Claim Intake bounded context because:
1. It has a unique identity (claim_id)
2. It controls access to related objects (ClaimSummary, events)
3. It enforces business invariants
4. It's the only object external code can reference directly

DDD Pattern: Aggregate - Claim maintains consistency boundaries and enforces
business rules within the Claim Intake bounded context.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, PrivateAttr, field_validator

from ..events import DomainEvent
from .claim_summary import ClaimSummary
from .document import Document, DocumentType
from .events import ClaimFactsExtracted, DocumentAdded


class ClaimStatus(str, Enum):
    """
    Enumeration for claim status.
    
    In DDD, enumerations represent a fixed set of domain concepts.
    This is part of the Ubiquitous Language - terms that domain experts
    and developers both understand and use consistently.
    """
    DRAFT = "draft"  # Initial state, facts being extracted
    FACTS_EXTRACTED = "facts_extracted"  # Facts extracted, awaiting validation
    POLICY_VALIDATED = "policy_validated"  # Policy validated, awaiting triage
    TRIAGED = "triaged"  # Routed to appropriate handler
    PROCESSING = "processing"  # Being processed by downstream system
    COMPLETED = "completed"  # Processing complete
    REJECTED = "rejected"  # Claim rejected (invalid policy, fraud, etc.)


class Claim(BaseModel):
    """
    Aggregate Root: Represents a claim in the system.
    
    As an Aggregate Root, Claim:
    1. Has a unique identity (claim_id)
    2. Enforces business invariants
    3. Controls access to related objects
    4. Publishes domain events when state changes
    
    DDD Principle: Only Aggregate Roots can be referenced from outside
    the aggregate. Other objects are accessed through the root.
    """
    
    # Identity (Aggregate Root must have unique identity)
    claim_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this claim")
    
    # Status tracking
    status: ClaimStatus = Field(default=ClaimStatus.DRAFT, description="Current status of the claim")
    
    # Core domain data (Value Object)
    summary: Optional[ClaimSummary] = Field(default=None, description="Structured claim facts")
    
    # Supporting documents
    documents: List[Document] = Field(default_factory=list, description="Supporting documents attached to the claim")
    
    # Source data
    raw_input: str = Field(description="Original unstructured input (email, form, etc.)")
    source: str = Field(default="email", description="Source of the claim (email, web, phone, etc.)")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the claim was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Domain events (stored for event sourcing or debugging)
    # Using PrivateAttr for internal events list (not part of public API)
    _domain_events: List[DomainEvent] = PrivateAttr(default_factory=list)
    
    @field_validator('status')
    @classmethod
    def validate_status_transition(cls, v: ClaimStatus, info) -> ClaimStatus:
        """
        Domain Invariant: Status transitions must be valid.
        
        This is a simplified version. In a full implementation, you'd have
        a state machine that enforces all valid transitions.
        """
        # Basic validation - can be extended with state machine
        return v
    
    def extract_facts(self, summary: ClaimSummary) -> ClaimFactsExtracted:
        """
        Extract facts from unstructured data and update the claim.
        
        This method enforces the business rule that facts can only be
        extracted once (or when in DRAFT status). This is a domain invariant.
        
        Args:
            summary: The extracted claim summary (Value Object)
        
        Returns:
            ClaimFactsExtracted domain event
        
        Raises:
            ValueError: If facts have already been extracted
        """
        # Domain Invariant: Can only extract facts if in DRAFT status
        if self.status != ClaimStatus.DRAFT:
            raise ValueError(f"Cannot extract facts: claim is in {self.status} status")
        
        # Update aggregate state
        self.summary = summary
        self.status = ClaimStatus.FACTS_EXTRACTED
        self.updated_at = datetime.utcnow()
        
        # Create and store domain event
        event = ClaimFactsExtracted(
            claim_id=self.claim_id,
            summary=summary,
            extracted_at=datetime.utcnow(),
        )
        self._domain_events.append(event)
        
        return event
    
    def validate_policy(self, is_valid: bool) -> None:
        """
        Mark policy as validated.
        
        This would typically be called by the Policy Validation Agent
        after checking the claim against the policy repository.
        
        Args:
            is_valid: Whether the policy is valid for this claim
        """
        if self.status != ClaimStatus.FACTS_EXTRACTED:
            raise ValueError(f"Cannot validate policy: claim is in {self.status} status")
        
        if is_valid:
            self.status = ClaimStatus.POLICY_VALIDATED
        else:
            self.status = ClaimStatus.REJECTED
        
        self.updated_at = datetime.utcnow()
    
    def triage(self, routing_decision: str) -> None:
        """
        Triage and route the claim to downstream systems.
        
        Args:
            routing_decision: Where the claim should be routed
        """
        if self.status != ClaimStatus.POLICY_VALIDATED:
            raise ValueError(f"Cannot triage: claim is in {self.status} status")
        
        self.status = ClaimStatus.TRIAGED
        self.updated_at = datetime.utcnow()
        # In a full implementation, routing_decision would be stored
    
    def add_document(self, document: Document) -> DocumentAdded:
        """
        Add a supporting document to the claim.
        
        This method enforces the business rule that documents can be added
        at any stage of the claim lifecycle. This is a domain invariant.
        
        Args:
            document: The document to add (Value Object)
        
        Returns:
            DocumentAdded domain event
        
        Raises:
            ValueError: If document is invalid
        """
        # Domain Invariant: Document must have valid ID
        if not document.document_id:
            raise ValueError("Document must have a valid ID")
        
        # Add document to collection
        self.documents.append(document)
        self.updated_at = datetime.utcnow()
        
        # Create and store domain event
        event = DocumentAdded(
            claim_id=self.claim_id,
            document_id=document.document_id,
            document_type=document.document_type,
            added_at=datetime.utcnow(),
        )
        self._domain_events.append(event)
        
        return event
    
    def get_documents_by_type(self, document_type: DocumentType) -> List[Document]:
        """
        Get all documents of a specific type.
        
        Args:
            document_type: The type of document to filter by
        
        Returns:
            List of documents matching the type
        """
        return [doc for doc in self.documents if doc.document_type == document_type]
    
    def get_domain_events(self) -> List[DomainEvent]:
        """
        Get and clear domain events.
        
        This is used by the repository or event bus to publish events
        after the aggregate is saved.
        
        Returns:
            List of domain events that occurred
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

