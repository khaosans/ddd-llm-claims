"""
Database-backed Claim Repository

Replaces in-memory repository with SQLite persistence.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

import json

from ..domain.claim import Claim, ClaimStatus
from ..domain.claim.claim_summary import ClaimSummary
from ..domain.claim.document import Document, DocumentMetadata, DocumentStatus, DocumentType
from ..repositories.claim_repository import ClaimRepository
from ..database.models import ClaimModel, DocumentModel
from ..database.session import get_db_session


class DatabaseClaimRepository(ClaimRepository):
    """
    Database-backed implementation of ClaimRepository.
    
    Uses SQLAlchemy to persist claims to SQLite database.
    """
    
    def __init__(self, db_path: str = "data/claims.db"):
        """
        Initialize the database repository.
        
        Args:
            db_path: Path to the database file
        """
        self.db_path = db_path
        from ..database.session import init_db
        init_db(db_path)
    
    def _to_domain(self, db_model: ClaimModel) -> Claim:
        """Convert database model to domain Claim"""
        claim = Claim(
            claim_id=UUID(db_model.claim_id),
            raw_input=db_model.raw_input,
            source=db_model.source,
            status=ClaimStatus(db_model.status),
        )
        
        # Reconstruct ClaimSummary if fields are present
        if db_model.claim_type:
            claim.summary = ClaimSummary(
                claim_type=db_model.claim_type,
                incident_date=db_model.incident_date,
                reported_date=db_model.reported_date or datetime.utcnow(),
                claimed_amount=db_model.claimed_amount,
                currency=db_model.currency or "USD",
                incident_location=db_model.incident_location or "",
                description=db_model.description or "",
                claimant_name=db_model.claimant_name or "",
                claimant_email=db_model.claimant_email,
                claimant_phone=db_model.claimant_phone,
                policy_number=db_model.policy_number,
                tags=[],
            )
        
        # Load documents if available
        if hasattr(db_model, 'documents') and db_model.documents:
            claim.documents = [
                self._document_to_domain(doc_model)
                for doc_model in db_model.documents
            ]
        
        return claim
    
    def _document_to_domain(self, db_model: DocumentModel) -> Document:
        """Convert database DocumentModel to domain Document"""
        metadata = None
        if db_model.metadata_json:
            try:
                metadata_dict = json.loads(db_model.metadata_json)
                metadata = DocumentMetadata(**metadata_dict)
            except Exception:
                pass
        
        return Document(
            document_id=UUID(db_model.document_id),
            document_type=DocumentType(db_model.document_type),
            filename=db_model.filename,
            file_path=db_model.file_path,
            file_hash=db_model.file_hash,
            status=DocumentStatus(db_model.status),
            authenticity_score=db_model.authenticity_score,
            uploaded_at=db_model.uploaded_at,
            validated_at=db_model.validated_at,
            metadata=metadata,
        )
    
    def _to_db_model(self, claim: Claim) -> ClaimModel:
        """Convert domain Claim to database model"""
        db_model = ClaimModel(
            claim_id=str(claim.claim_id),
            raw_input=claim.raw_input,
            source=claim.source,
            status=claim.status.value,
        )
        
        # Flatten ClaimSummary if present
        if claim.summary:
            db_model.claim_type = claim.summary.claim_type
            db_model.incident_date = claim.summary.incident_date
            db_model.reported_date = claim.summary.reported_date
            db_model.claimed_amount = claim.summary.claimed_amount
            db_model.currency = claim.summary.currency
            db_model.incident_location = claim.summary.incident_location
            db_model.description = claim.summary.description
            db_model.claimant_name = claim.summary.claimant_name
            db_model.claimant_email = claim.summary.claimant_email
            db_model.claimant_phone = claim.summary.claimant_phone
            db_model.policy_number = claim.summary.policy_number
        
        return db_model
    
    async def save(self, claim: Claim) -> None:
        """Save a claim to the database"""
        with get_db_session(self.db_path) as session:
            # Check if exists
            existing = session.query(ClaimModel).filter_by(
                claim_id=str(claim.claim_id)
            ).first()
            
            if existing:
                # Update existing
                db_model = self._to_db_model(claim)
                for key, value in db_model.__dict__.items():
                    if key != "claim_id" and not key.startswith("_"):
                        setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
                
                # Save documents
                self._save_documents(session, claim)
            else:
                # Create new
                db_model = self._to_db_model(claim)
                session.add(db_model)
                session.flush()  # Flush to get ID
                
                # Save documents
                self._save_documents(session, claim)
    
    def _save_documents(self, session, claim: Claim) -> None:
        """Save documents for a claim"""
        from ..database.models import DocumentModel
        
        # Get existing documents
        existing_doc_ids = {
            UUID(doc.document_id)
            for doc in session.query(DocumentModel).filter_by(
                claim_id=str(claim.claim_id)
            ).all()
        }
        
        # Save or update documents
        for doc in claim.documents:
            doc_model = session.query(DocumentModel).filter_by(
                document_id=str(doc.document_id)
            ).first()
            
            metadata_json = None
            if doc.metadata:
                metadata_json = json.dumps(doc.metadata.model_dump())
            
            if doc_model:
                # Update existing
                doc_model.document_type = doc.document_type.value
                doc_model.filename = doc.filename
                doc_model.file_path = doc.file_path
                doc_model.file_hash = doc.file_hash
                doc_model.status = doc.status.value
                doc_model.authenticity_score = doc.authenticity_score
                doc_model.validated_at = doc.validated_at
                doc_model.metadata_json = metadata_json
            else:
                # Create new
                doc_model = DocumentModel(
                    document_id=str(doc.document_id),
                    claim_id=str(claim.claim_id),
                    document_type=doc.document_type.value,
                    filename=doc.filename,
                    file_path=doc.file_path,
                    file_hash=doc.file_hash,
                    status=doc.status.value,
                    authenticity_score=doc.authenticity_score,
                    uploaded_at=doc.uploaded_at,
                    validated_at=doc.validated_at,
                    metadata_json=metadata_json,
                )
                session.add(doc_model)
        
        # Remove documents that are no longer in the claim
        current_doc_ids = {doc.document_id for doc in claim.documents}
        to_delete = existing_doc_ids - current_doc_ids
        for doc_id in to_delete:
            session.query(DocumentModel).filter_by(
                document_id=str(doc_id)
            ).delete()
    
    async def find_by_id(self, claim_id: UUID) -> Optional[Claim]:
        """Find a claim by ID"""
        with get_db_session(self.db_path) as session:
            db_model = session.query(ClaimModel).filter_by(
                claim_id=str(claim_id)
            ).first()
            
            if db_model:
                return self._to_domain(db_model)
            return None
    
    async def find_all(self) -> List[Claim]:
        """Find all claims"""
        with get_db_session(self.db_path) as session:
            db_models = session.query(ClaimModel).all()
            return [self._to_domain(model) for model in db_models]
    
    async def find_by_status(self, status: ClaimStatus) -> List[Claim]:
        """Find claims by status"""
        with get_db_session(self.db_path) as session:
            db_models = session.query(ClaimModel).filter_by(
                status=status.value
            ).all()
            return [self._to_domain(model) for model in db_models]

