"""
Document Repository - Data access for Document Value Objects

Provides CRUD operations for documents and querying by various criteria.
"""

import json
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..domain.claim.document import Document, DocumentStatus, DocumentType


class DocumentRepository(ABC):
    """
    Abstract repository interface for Document Value Objects.
    """
    
    @abstractmethod
    async def save(self, document: Document, claim_id: UUID) -> None:
        """
        Save a document.
        
        Args:
            document: Document to save
            claim_id: ID of the claim this document belongs to
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, document_id: UUID) -> Optional[Document]:
        """
        Find a document by ID.
        
        Args:
            document_id: Document ID
        
        Returns:
            Document if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def find_by_claim_id(self, claim_id: UUID) -> List[Document]:
        """
        Find all documents for a claim.
        
        Args:
            claim_id: Claim ID
        
        Returns:
            List of documents
        """
        pass
    
    @abstractmethod
    async def find_by_type(
        self,
        claim_id: UUID,
        document_type: DocumentType,
    ) -> List[Document]:
        """
        Find documents by type for a claim.
        
        Args:
            claim_id: Claim ID
            document_type: Type of document to find
        
        Returns:
            List of documents
        """
        pass
    
    @abstractmethod
    async def find_by_status(
        self,
        claim_id: UUID,
        status: DocumentStatus,
    ) -> List[Document]:
        """
        Find documents by status for a claim.
        
        Args:
            claim_id: Claim ID
            status: Status to filter by
        
        Returns:
            List of documents
        """
        pass
    
    @abstractmethod
    async def delete(self, document_id: UUID) -> None:
        """
        Delete a document.
        
        Args:
            document_id: Document ID to delete
        """
        pass


class InMemoryDocumentRepository(DocumentRepository):
    """
    In-memory implementation of DocumentRepository.
    
    Useful for testing and development.
    """
    
    def __init__(self):
        """Initialize the in-memory repository"""
        self._documents: dict[UUID, tuple[Document, UUID]] = {}  # document_id -> (document, claim_id)
    
    async def save(self, document: Document, claim_id: UUID) -> None:
        """Save a document"""
        self._documents[document.document_id] = (document, claim_id)
    
    async def find_by_id(self, document_id: UUID) -> Optional[Document]:
        """Find a document by ID"""
        if document_id in self._documents:
            return self._documents[document_id][0]
        return None
    
    async def find_by_claim_id(self, claim_id: UUID) -> List[Document]:
        """Find all documents for a claim"""
        return [
            doc
            for doc, cid in self._documents.values()
            if cid == claim_id
        ]
    
    async def find_by_type(
        self,
        claim_id: UUID,
        document_type: DocumentType,
    ) -> List[Document]:
        """Find documents by type"""
        return [
            doc
            for doc, cid in self._documents.values()
            if cid == claim_id and doc.document_type == document_type
        ]
    
    async def find_by_status(
        self,
        claim_id: UUID,
        status: DocumentStatus,
    ) -> List[Document]:
        """Find documents by status"""
        return [
            doc
            for doc, cid in self._documents.values()
            if cid == claim_id and doc.status == status
        ]
    
    async def delete(self, document_id: UUID) -> None:
        """Delete a document"""
        if document_id in self._documents:
            del self._documents[document_id]
    
    def clear(self) -> None:
        """Clear all documents (useful for testing)"""
        self._documents.clear()


