"""
Document Storage Service

Handles file system storage and metadata management for supporting documents.
Documents are stored in a structured directory hierarchy and metadata is
tracked for retrieval and integrity verification.
"""

import hashlib
import mimetypes
import shutil
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import UUID, uuid4

from ..domain.claim.document import Document, DocumentMetadata, DocumentStatus, DocumentType


class DocumentStorageService:
    """
    Service for storing and retrieving supporting documents.
    
    Documents are stored in a directory structure:
    data/documents/{claim_id}/{document_id}_{filename}
    
    This service handles:
    - File storage and retrieval
    - Hash calculation for integrity verification
    - Metadata extraction
    - File type detection
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the document storage service.
        
        Args:
            base_path: Base directory for document storage (default: data/documents)
        """
        if base_path is None:
            base_path = Path("data/documents")
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def store_document(
        self,
        claim_id: UUID,
        file_content: bytes,
        filename: str,
        document_type: DocumentType,
    ) -> Document:
        """
        Store a document file and create a Document Value Object.
        
        Args:
            claim_id: ID of the claim this document belongs to
            file_content: Binary content of the file
            filename: Original filename
            document_type: Type of document
        
        Returns:
            Document Value Object with storage information
        """
        # Generate unique document ID
        document_id = uuid4()
        
        # Create claim-specific directory
        claim_dir = self.base_path / str(claim_id)
        claim_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate safe filename (preserve extension)
        file_extension = Path(filename).suffix
        safe_filename = f"{document_id}{file_extension}"
        file_path = claim_dir / safe_filename
        
        # Write file to disk
        file_path.write_bytes(file_content)
        
        # Calculate file hash (SHA-256)
        file_hash = self._calculate_hash(file_content)
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type is None:
            mime_type = "application/octet-stream"
        
        # Extract basic metadata
        metadata = self._extract_metadata(file_content, filename, mime_type)
        
        # Create Document Value Object
        document = Document(
            document_id=document_id,
            document_type=document_type,
            filename=filename,
            file_path=str(file_path),
            file_hash=file_hash,
            status=DocumentStatus.PENDING,
            metadata=metadata,
        )
        
        return document
    
    def retrieve_document(self, document: Document) -> bytes:
        """
        Retrieve document file content.
        
        Args:
            document: Document Value Object
        
        Returns:
            Binary content of the file
        
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        file_path = Path(document.file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")
        
        content = file_path.read_bytes()
        
        # Verify hash integrity
        calculated_hash = self._calculate_hash(content)
        if calculated_hash != document.file_hash:
            raise ValueError(f"Document hash mismatch: file may have been tampered with")
        
        return content
    
    def delete_document(self, document: Document) -> None:
        """
        Delete a document file from storage.
        
        Args:
            document: Document Value Object to delete
        """
        file_path = Path(document.file_path)
        if file_path.exists():
            file_path.unlink()
        
        # Clean up claim directory if empty
        claim_dir = file_path.parent
        if claim_dir.exists() and not any(claim_dir.iterdir()):
            claim_dir.rmdir()
    
    def verify_integrity(self, document: Document) -> bool:
        """
        Verify document file integrity by checking hash.
        
        Args:
            document: Document Value Object to verify
        
        Returns:
            True if integrity check passes, False otherwise
        """
        try:
            file_path = Path(document.file_path)
            if not file_path.exists():
                return False
            
            content = file_path.read_bytes()
            calculated_hash = self._calculate_hash(content)
            return calculated_hash == document.file_hash
        except Exception:
            return False
    
    def _calculate_hash(self, content: bytes) -> str:
        """
        Calculate SHA-256 hash of file content.
        
        Args:
            content: Binary file content
        
        Returns:
            Hexadecimal hash string (64 characters)
        """
        return hashlib.sha256(content).hexdigest()
    
    def _extract_metadata(
        self,
        content: bytes,
        filename: str,
        mime_type: str,
    ) -> Optional[DocumentMetadata]:
        """
        Extract metadata from document file.
        
        This is a basic implementation. In production, you would use
        specialized libraries for EXIF data, PDF metadata, etc.
        
        Args:
            content: Binary file content
            filename: Original filename
            mime_type: MIME type of the file
        
        Returns:
            DocumentMetadata Value Object or None if extraction fails
        """
        try:
            file_size = len(content)
            
            # Try to extract image metadata if it's an image
            width = None
            height = None
            exif_data = None
            
            if mime_type.startswith("image/"):
                try:
                    from PIL import Image
                    import io
                    
                    img = Image.open(io.BytesIO(content))
                    width, height = img.size
                    
                    # Extract EXIF data if available
                    if hasattr(img, "_getexif") and img._getexif():
                        exif_data = {}
                        for tag_id, value in img._getexif().items():
                            tag_name = img._getexif().tag_names.get(tag_id, tag_id)
                            exif_data[str(tag_name)] = str(value)
                except ImportError:
                    # PIL not available, skip image metadata
                    pass
                except Exception:
                    # Image processing failed, continue without metadata
                    pass
            
            # Try to extract PDF metadata if it's a PDF
            pdf_metadata = None
            if mime_type == "application/pdf":
                try:
                    import PyPDF2
                    import io
                    
                    pdf_file = io.BytesIO(content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    if pdf_reader.metadata:
                        pdf_metadata = {}
                        for key, value in pdf_reader.metadata.items():
                            pdf_metadata[str(key)] = str(value)
                except ImportError:
                    # PyPDF2 not available, skip PDF metadata
                    pass
                except Exception:
                    # PDF processing failed, continue without metadata
                    pass
            
            return DocumentMetadata(
                file_size=file_size,
                mime_type=mime_type,
                width=width,
                height=height,
                exif_data=exif_data,
                pdf_metadata=pdf_metadata,
            )
        except Exception:
            # If metadata extraction fails, return None
            # The document can still be stored without metadata
            return None


