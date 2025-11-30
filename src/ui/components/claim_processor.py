"""
Claim Processor Component - Streamlit

Reusable component for processing claims in the UI.
"""

import streamlit as st
from typing import Optional, Dict, Any


def render_claim_processor(
    on_process: Optional[callable] = None,
    default_input: str = ""
) -> Dict[str, Any]:
    """
    Render claim processing interface.
    
    Args:
        on_process: Callback function when claim is processed
        default_input: Default input text
    
    Returns:
        Dictionary with processing results
    """
    st.subheader("📝 Process Claim")
    
    # Input
    claim_input = st.text_area(
        "Unstructured Claim Data",
        value=default_input,
        height=200,
        placeholder="Enter claim data here..."
    )
    
    # Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        model_provider = st.selectbox("Model Provider", ["Mock", "Ollama", "OpenAI", "Anthropic"])
    
    with col2:
        source = st.selectbox("Source", ["email", "web", "phone", "form"])
    
    # Process button
    if st.button("🚀 Process Claim", type="primary", use_container_width=True):
        if not claim_input:
            st.warning("Please enter claim data.")
            return {}
        
        if on_process:
            return on_process(claim_input, model_provider, source)
        else:
            # Default processing
            with st.spinner("Processing..."):
                st.success("Claim processed!")
                return {
                    "status": "success",
                    "claim_id": "example-123",
                    "summary": {
                        "claim_type": "auto",
                        "amount": "$3,500.00"
                    }
                }
    
    return {}

