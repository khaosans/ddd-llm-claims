"""
Document Viewer Component for Streamlit

Provides document preview, viewing, and metadata display capabilities.
"""

import streamlit as st
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from ...domain.claim.document import Document, DocumentStatus, DocumentType
from ...storage.document_storage import DocumentStorageService


def display_document(document: Document, storage_service: Optional[DocumentStorageService] = None) -> None:
    """
    Display a document in the Streamlit UI.
    
    Args:
        document: Document Value Object to display
        storage_service: Optional storage service for file retrieval
    """
    if storage_service is None:
        storage_service = DocumentStorageService()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**📄 {document.filename}**")
        st.caption(f"Type: {document.document_type.value.replace('_', ' ').title()}")
    
    with col2:
        status_colors = {
            DocumentStatus.PENDING: "🟡",
            DocumentStatus.VALIDATED: "🟢",
            DocumentStatus.REJECTED: "🔴",
            DocumentStatus.SUSPICIOUS: "🟠",
        }
        status_icon = status_colors.get(document.status, "⚪")
        st.markdown(f"{status_icon} {document.status.value.title()}")
    
    # Display metadata
    if document.metadata:
        with st.expander("📋 Document Metadata", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**File Size:** {document.metadata.file_size:,} bytes")
                st.write(f"**MIME Type:** {document.metadata.mime_type}")
            with col2:
                if document.metadata.width and document.metadata.height:
                    st.write(f"**Dimensions:** {document.metadata.width} x {document.metadata.height}")
                if document.authenticity_score is not None:
                    st.write(f"**Authenticity Score:** {document.authenticity_score:.2f}")
    
    # Display authenticity findings if available
    if document.status == DocumentStatus.SUSPICIOUS and document.authenticity_score is not None:
        st.warning(f"⚠️ Suspicious document detected (score: {document.authenticity_score:.2f})")
    
    # Try to display document preview
    try:
        file_path = Path(document.file_path)
        if file_path.exists():
            mime_type = document.metadata.mime_type if document.metadata else ""
            
            # Display image preview
            if mime_type.startswith("image/"):
                try:
                    from PIL import Image
                    img = Image.open(file_path)
                    st.image(img, caption=document.filename, use_container_width=True)
                except Exception:
                    st.info("Image preview not available")
            
            # Display PDF info
            elif mime_type == "application/pdf":
                st.info(f"📄 PDF Document: {document.filename}")
                st.caption("PDF preview not available in this demo. Download to view.")
                
                # Provide download button
                try:
                    file_content = storage_service.retrieve_document(document)
                    st.download_button(
                        label="📥 Download PDF",
                        data=file_content,
                        file_name=document.filename,
                        mime_type="application/pdf",
                    )
                except Exception:
                    pass
            
            # Display other file types
            else:
                st.info(f"📄 {mime_type} Document: {document.filename}")
                try:
                    file_content = storage_service.retrieve_document(document)
                    st.download_button(
                        label="📥 Download File",
                        data=file_content,
                        file_name=document.filename,
                        mime_type=mime_type,
                    )
                except Exception:
                    pass
        else:
            st.warning("⚠️ Document file not found")
    except Exception as e:
        st.error(f"Error displaying document: {str(e)}")


def display_documents_list(
    documents: List[Document],
    storage_service: Optional[DocumentStorageService] = None,
) -> None:
    """
    Display a list of documents.
    
    Args:
        documents: List of Document Value Objects
        storage_service: Optional storage service for file retrieval
    """
    if not documents:
        st.info("No documents attached to this claim.")
        return
    
    st.subheader(f"📎 Supporting Documents ({len(documents)})")
    
    for i, document in enumerate(documents):
        with st.expander(
            f"📄 {document.filename} - {document.document_type.value.replace('_', ' ').title()}",
            expanded=False
        ):
            display_document(document, storage_service)


def display_compliance_status(
    claim_id: UUID,
    missing_document_types: List[DocumentType],
    is_compliant: bool,
) -> None:
    """
    Display document compliance status.
    
    Args:
        claim_id: Claim ID
        missing_document_types: List of missing document types
        is_compliant: Whether claim is compliant
    """
    if is_compliant:
        st.success("✅ **Document Compliance:** All required documents present")
    else:
        st.warning("⚠️ **Document Compliance:** Missing required documents")
        st.write("**Missing Document Types:**")
        for doc_type in missing_document_types:
            st.write(f"- {doc_type.value.replace('_', ' ').title()}")



