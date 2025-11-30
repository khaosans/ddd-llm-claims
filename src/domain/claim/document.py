"""
Document - Value Object for Supporting Documents

In DDD, a Value Object is an immutable object defined by its attributes
rather than its identity. Document represents a supporting document
attached to a claim (e.g., police report, photo, invoice).

Documents are Value Objects because:
1. They have no identity of their own (they're part of a Claim)
2. They're immutable (once created, they don't change)
3. They're defined by their attributes (all fields together define what it is)
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class DocumentType(str, Enum):
    """
    Enumeration for document types.
    
    In DDD, enumerations represent a fixed set of domain concepts.
    This is part of the Ubiquitous Language - terms that domain experts
    and developers both understand and use consistently.
    """
    POLICE_REPORT = "police_report"
    PHOTO = "photo"
    INVOICE = "invoice"
    RECEIPT = "receipt"
    MEDICAL_RECORD = "medical_record"
    APPRAISAL = "appraisal"
    ESTIMATE = "estimate"
    REPAIR_ORDER = "repair_order"
    WITNESS_STATEMENT = "witness_statement"
    INSURANCE_FORM = "insurance_form"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """
    Enumeration for document validation status.
    """
    PENDING = "pending"  # Uploaded but not yet validated
    VALIDATED = "validated"  # Passed validation checks
    REJECTED = "rejected"  # Failed validation
    SUSPICIOUS = "suspicious"  # Authenticity concerns detected


class DocumentMetadata(BaseModel):
    """
    Value Object: Metadata extracted from a document.
    
    Contains technical metadata about the document such as EXIF data,
    PDF properties, file properties, etc.
    """
    file_size: int = Field(description="File size in bytes", ge=0)
    mime_type: str = Field(description="MIME type of the file")
    width: Optional[int] = Field(default=None, description="Image width in pixels (if image)")
    height: Optional[int] = Field(default=None, description="Image height in pixels (if image)")
    exif_data: Optional[Dict[str, Any]] = Field(default=None, description="EXIF metadata (if image)")
    pdf_metadata: Optional[Dict[str, Any]] = Field(default=None, description="PDF metadata (if PDF)")
    created_timestamp: Optional[datetime] = Field(default=None, description="Document creation timestamp from metadata")
    modified_timestamp: Optional[datetime] = Field(default=None, description="Document modification timestamp from metadata")
    
    class Config:
        frozen = True  # Immutability: Value Objects cannot be modified after creation
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class Document(BaseModel):
    """
    Value Object: Represents a supporting document attached to a claim.
    
    Documents are immutable Value Objects that contain metadata about
    supporting files (photos, police reports, invoices, etc.) that are
    part of a claim submission.
    
    DDD Principle: Value Objects are immutable and validated at creation.
    """
    
    document_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this document")
    document_type: DocumentType = Field(description="Type of document")
    filename: str = Field(description="Original filename")
    file_path: str = Field(description="Path where the file is stored")
    file_hash: str = Field(description="SHA-256 hash of the file for integrity verification")
    status: DocumentStatus = Field(default=DocumentStatus.PENDING, description="Validation status")
    authenticity_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Authenticity score (0.0-1.0), higher is more authentic"
    )
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, description="When the document was uploaded")
    validated_at: Optional[datetime] = Field(default=None, description="When the document was validated")
    metadata: Optional[DocumentMetadata] = Field(default=None, description="Technical metadata extracted from the document")
    
    @field_validator('filename')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """
        Domain Invariant: Filename must not be empty.
        """
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()
    
    @field_validator('file_hash')
    @classmethod
    def validate_hash(cls, v: str) -> str:
        """
        Domain Invariant: File hash must be a valid SHA-256 hash (64 hex characters).
        """
        if not v or len(v) != 64:
            raise ValueError("File hash must be a valid SHA-256 hash (64 hex characters)")
        # Validate hex characters
        try:
            int(v, 16)
        except ValueError:
            raise ValueError("File hash must contain only hexadecimal characters")
        return v.lower()
    
    def mark_validated(self) -> 'Document':
        """
        Create a new Document instance with validated status.
        
        Since Document is immutable, this returns a new instance.
        """
        return Document(
            document_id=self.document_id,
            document_type=self.document_type,
            filename=self.filename,
            file_path=self.file_path,
            file_hash=self.file_hash,
            status=DocumentStatus.VALIDATED,
            authenticity_score=self.authenticity_score,
            uploaded_at=self.uploaded_at,
            validated_at=datetime.utcnow(),
            metadata=self.metadata,
        )
    
    def mark_rejected(self) -> 'Document':
        """
        Create a new Document instance with rejected status.
        """
        return Document(
            document_id=self.document_id,
            document_type=self.document_type,
            filename=self.filename,
            file_path=self.file_path,
            file_hash=self.file_hash,
            status=DocumentStatus.REJECTED,
            authenticity_score=self.authenticity_score,
            uploaded_at=self.uploaded_at,
            validated_at=datetime.utcnow(),
            metadata=self.metadata,
        )
    
    def mark_suspicious(self, authenticity_score: float) -> 'Document':
        """
        Create a new Document instance with suspicious status and authenticity score.
        """
        return Document(
            document_id=self.document_id,
            document_type=self.document_type,
            filename=self.filename,
            file_path=self.file_path,
            file_hash=self.file_hash,
            status=DocumentStatus.SUSPICIOUS,
            authenticity_score=authenticity_score,
            uploaded_at=self.uploaded_at,
            validated_at=self.validated_at,
            metadata=self.metadata,
        )
    
    class Config:
        frozen = True  # Immutability: Value Objects cannot be modified after creation
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return self.model_dump()

