"""
Document Authenticity Service

Performs authenticity checks on documents to detect tampering, fraud,
or inconsistencies. Includes image analysis, PDF verification, OCR,
and metadata validation.
"""

import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

from ..domain.claim.document import Document, DocumentMetadata
from ..storage.document_storage import DocumentStorageService


class AuthenticityCheckResult:
    """
    Result of an authenticity check on a document.
    """
    
    def __init__(
        self,
        document_id: UUID,
        authenticity_score: float,
        is_suspicious: bool,
        findings: List[str],
        checks_performed: List[str],
    ):
        """
        Initialize authenticity check result.
        
        Args:
            document_id: ID of the document checked
            authenticity_score: Score from 0.0-1.0 (higher is more authentic)
            is_suspicious: Whether document shows signs of tampering
            findings: List of findings from the check
            checks_performed: List of check types that were performed
        """
        self.document_id = document_id
        self.authenticity_score = authenticity_score
        self.is_suspicious = is_suspicious
        self.findings = findings
        self.checks_performed = checks_performed


class DocumentAuthenticityService:
    """
    Service for checking document authenticity.
    
    Performs various checks including:
    - File hash verification
    - Image EXIF metadata analysis
    - PDF metadata extraction
    - Timestamp validation
    - Basic tampering detection
    """
    
    def __init__(self, storage_service: Optional[DocumentStorageService] = None):
        """
        Initialize the authenticity service.
        
        Args:
            storage_service: Document storage service for file access
        """
        self.storage_service = storage_service or DocumentStorageService()
    
    def check_authenticity(self, document: Document) -> AuthenticityCheckResult:
        """
        Perform authenticity checks on a document.
        
        Args:
            document: Document Value Object to check
        
        Returns:
            AuthenticityCheckResult with score and findings
        """
        findings: List[str] = []
        checks_performed: List[str] = []
        score = 1.0  # Start with perfect score, deduct for issues
        
        # Check 1: File integrity (hash verification)
        checks_performed.append("hash_verification")
        if not self.storage_service.verify_integrity(document):
            findings.append("File hash mismatch - file may have been tampered with")
            score -= 0.5
        else:
            findings.append("File hash verified - integrity intact")
        
        # Check 2: Metadata analysis
        if document.metadata:
            checks_performed.append("metadata_analysis")
            metadata_checks = self._check_metadata(document.metadata, document)
            findings.extend(metadata_checks["findings"])
            score += metadata_checks["score_adjustment"]
        
        # Check 3: File type validation
        checks_performed.append("file_type_validation")
        file_type_check = self._validate_file_type(document)
        findings.extend(file_type_check["findings"])
        score += file_type_check["score_adjustment"]
        
        # Check 4: Timestamp validation
        checks_performed.append("timestamp_validation")
        timestamp_check = self._validate_timestamps(document)
        findings.extend(timestamp_check["findings"])
        score += timestamp_check["score_adjustment"]
        
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        # Determine if suspicious (score < 0.7 or critical findings)
        is_suspicious = score < 0.7 or any(
            "tampered" in f.lower() or "mismatch" in f.lower() or "invalid" in f.lower()
            for f in findings
        )
        
        return AuthenticityCheckResult(
            document_id=document.document_id,
            authenticity_score=score,
            is_suspicious=is_suspicious,
            findings=findings,
            checks_performed=checks_performed,
        )
    
    def _check_metadata(
        self,
        metadata: DocumentMetadata,
        document: Document,
    ) -> Dict[str, Any]:
        """
        Check document metadata for authenticity indicators.
        
        Args:
            metadata: DocumentMetadata Value Object
            document: Document Value Object
        
        Returns:
            Dict with findings and score adjustment
        """
        findings: List[str] = []
        score_adjustment = 0.0
        
        # Check EXIF data for images
        if metadata.exif_data:
            exif_checks = self._check_exif_data(metadata.exif_data)
            findings.extend(exif_checks["findings"])
            score_adjustment += exif_checks["score_adjustment"]
        else:
            if document.document_type.value in ["photo", "image"]:
                findings.append("No EXIF data found - may indicate image manipulation")
                score_adjustment -= 0.1
        
        # Check PDF metadata
        if metadata.pdf_metadata:
            pdf_checks = self._check_pdf_metadata(metadata.pdf_metadata)
            findings.extend(pdf_checks["findings"])
            score_adjustment += pdf_checks["score_adjustment"]
        
        # Check image dimensions
        if metadata.width and metadata.height:
            if metadata.width < 100 or metadata.height < 100:
                findings.append("Image dimensions unusually small - may be low quality or cropped")
                score_adjustment -= 0.05
        
        return {
            "findings": findings,
            "score_adjustment": score_adjustment,
        }
    
    def _check_exif_data(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check EXIF metadata for authenticity indicators.
        
        Args:
            exif_data: Dictionary of EXIF data
        
        Returns:
            Dict with findings and score adjustment
        """
        findings: List[str] = []
        score_adjustment = 0.0
        
        # Check for common EXIF fields
        if "DateTime" in exif_data or "DateTimeOriginal" in exif_data:
            findings.append("EXIF timestamp found - helps verify authenticity")
            score_adjustment += 0.1
        else:
            findings.append("No EXIF timestamp found")
            score_adjustment -= 0.05
        
        # Check for camera make/model (indicates real photo)
        if "Make" in exif_data or "Model" in exif_data:
            findings.append("Camera information found in EXIF - indicates real photograph")
            score_adjustment += 0.1
        
        # Check for software tags (may indicate editing)
        if "Software" in exif_data:
            software = str(exif_data["Software"]).lower()
            if any(editor in software for editor in ["photoshop", "gimp", "paint", "editor"]):
                findings.append(f"Image editing software detected: {exif_data['Software']}")
                score_adjustment -= 0.1
        
        return {
            "findings": findings,
            "score_adjustment": score_adjustment,
        }
    
    def _check_pdf_metadata(self, pdf_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check PDF metadata for authenticity indicators.
        
        Args:
            pdf_metadata: Dictionary of PDF metadata
        
        Returns:
            Dict with findings and score adjustment
        """
        findings: List[str] = []
        score_adjustment = 0.0
        
        # Check for creation date
        if "/CreationDate" in pdf_metadata or "CreationDate" in pdf_metadata:
            findings.append("PDF creation date found")
            score_adjustment += 0.05
        
        # Check for author/producer (may indicate source)
        if "/Author" in pdf_metadata or "Author" in pdf_metadata:
            findings.append("PDF author information found")
            score_adjustment += 0.05
        
        # Check for modification date
        if "/ModDate" in pdf_metadata or "ModDate" in pdf_metadata:
            mod_date = pdf_metadata.get("/ModDate") or pdf_metadata.get("ModDate")
            creation_date = pdf_metadata.get("/CreationDate") or pdf_metadata.get("CreationDate")
            if mod_date != creation_date:
                findings.append("PDF has been modified after creation")
                score_adjustment -= 0.05
        
        return {
            "findings": findings,
            "score_adjustment": score_adjustment,
        }
    
    def _validate_file_type(self, document: Document) -> Dict[str, Any]:
        """
        Validate that file type matches document type.
        
        Args:
            document: Document Value Object
        
        Returns:
            Dict with findings and score adjustment
        """
        findings: List[str] = []
        score_adjustment = 0.0
        
        if not document.metadata:
            return {"findings": findings, "score_adjustment": score_adjustment}
        
        mime_type = document.metadata.mime_type
        
        # Check if file type matches document type
        type_mismatches = {
            DocumentType.PHOTO: ["image/"],
            DocumentType.POLICE_REPORT: ["application/pdf", "image/"],
            DocumentType.MEDICAL_RECORD: ["application/pdf", "image/"],
            DocumentType.INVOICE: ["application/pdf", "image/"],
            DocumentType.RECEIPT: ["application/pdf", "image/"],
        }
        
        expected_prefixes = type_mismatches.get(document.document_type, [])
        if expected_prefixes:
            matches = any(mime_type.startswith(prefix) for prefix in expected_prefixes)
            if not matches:
                findings.append(
                    f"File type ({mime_type}) doesn't match expected type for {document.document_type.value}"
                )
                score_adjustment -= 0.1
            else:
                findings.append(f"File type matches document type: {mime_type}")
        
        return {
            "findings": findings,
            "score_adjustment": score_adjustment,
        }
    
    def _validate_timestamps(self, document: Document) -> Dict[str, Any]:
        """
        Validate document timestamps for consistency.
        
        Args:
            document: Document Value Object
        
        Returns:
            Dict with findings and score adjustment
        """
        findings: List[str] = []
        score_adjustment = 0.0
        
        if not document.metadata:
            return {"findings": findings, "score_adjustment": score_adjustment}
        
        # Check if creation timestamp is reasonable (not in future)
        if document.metadata.created_timestamp:
            if document.metadata.created_timestamp > datetime.utcnow():
                findings.append("Document creation timestamp is in the future - suspicious")
                score_adjustment -= 0.2
            else:
                findings.append("Document creation timestamp is valid")
        
        # Check if upload timestamp is after creation timestamp
        if document.metadata.created_timestamp and document.uploaded_at:
            if document.metadata.created_timestamp > document.uploaded_at:
                findings.append("Document created after upload - timestamp inconsistency")
                score_adjustment -= 0.15
        
        return {
            "findings": findings,
            "score_adjustment": score_adjustment,
        }


# Global instance
_authenticity_service: DocumentAuthenticityService = None


def get_authenticity_service() -> DocumentAuthenticityService:
    """
    Get the global document authenticity service instance.
    
    Returns:
        DocumentAuthenticityService instance
    """
    global _authenticity_service
    if _authenticity_service is None:
        _authenticity_service = DocumentAuthenticityService()
    return _authenticity_service

