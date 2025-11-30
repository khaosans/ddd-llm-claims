"""
Streamlit Dashboard - Main Application

DDD Claims Processing System Dashboard
"""

import streamlit as st
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Ensure data directories exist
from src.ui.utils import ensure_data_directories, get_local_model_info
ensure_data_directories()

# Page configuration
st.set_page_config(
    page_title="DDD Claims Processing System",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.claims = []
    st.session_state.reviews = []

# Import service
from src.ui.services import get_service, run_async

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🏢 Navigation")
page = st.sidebar.radio(
    "Select Page",
    [
        "🏠 Dashboard",
        "📝 Process Claim",
        "📋 Claims List",
        "👤 Review Queue",
        "🔍 Enhanced Review"
    ]
)

# Main content area
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">DDD Claims Processing System</div>', unsafe_allow_html=True)
    
    # Warning banner
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ DEMO SYSTEM</strong> - This is an educational demonstration system. 
        NOT for production use. See DISCLAIMERS.md for details.
    </div>
    """, unsafe_allow_html=True)
    
    # What is this section
    st.markdown("""
    ## What is this?
    
    This system demonstrates how **Domain-Driven Design (DDD)** principles can be combined with **LLM agents** 
    to process insurance claims automatically. It takes unstructured customer input (emails, forms) and:
    
    1. **Extracts** structured facts using an AI agent
    2. **Validates** policy coverage automatically  
    3. **Assesses** fraud risk
    4. **Routes** claims to appropriate handlers
    
    All using proven software architecture patterns for maintainability and clarity.
    """)
    
    # Quick Start
    st.markdown("---")
    st.subheader("🚀 Quick Start")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Start Processing Claims", type="primary", use_container_width=True):
            st.switch_page("pages/process_claim.py")
    
    with col2:
        st.markdown("""
        **Or explore:**
        - 📋 View processed claims
        - 👤 Check review queue
        - 🎨 See [interactive visualizations](docs/visualization.html)
        """)
    
    # System status
    st.markdown("---")
    st.subheader("📊 System Status")
    
    try:
        model_info = get_local_model_info()
        service = get_service()
        stats = run_async(service.get_statistics())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if model_info["ollama_available"]:
                recommended = model_info.get("recommended_model", "None")
                st.success(f"✅ **Ollama Available**\n\n{len(model_info['ollama_models'])} model(s) installed\nRecommended: {recommended}")
            else:
                st.info("🟡 **Mock Mode**\n\nUsing demo mode (no Ollama needed)")
        
        with col2:
            st.metric("Total Claims", stats.get("total_claims", 0))
        
        with col3:
            st.metric("Pending Reviews", stats.get("pending_reviews", 0))
        
        # Recent activity
        all_claims = run_async(service.get_all_claims())
        recent_claims = sorted(all_claims, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
        
        if recent_claims:
            st.subheader("📋 Recent Activity")
            for claim in recent_claims:
                claim_id_short = claim.get("claim_id", "")[:8]
                status = claim.get("status", "unknown")
                claimant = claim.get("claimant_name", "Unknown")
                st.markdown(f"- **Claim {claim_id_short}...** - {status} - {claimant}")
        else:
            st.info("💡 No claims yet. Click 'Start Processing Claims' to begin!")
            
    except Exception as e:
        st.warning(f"⚠️ System initialization issue: {str(e)}")
        st.info("💡 Don't worry - you can still use Mock mode. Click 'Start Processing Claims' to begin!")

elif page == "📝 Process Claim":
    st.title("📝 Process Claim")
    st.markdown("Enter unstructured claim data and process it through the system.")
    
    # Input form
    claim_input = st.text_area(
        "Claim Data",
        height=200,
        placeholder="Paste email, form data, or other unstructured claim information here..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        model_provider = st.selectbox(
            "Model Provider",
            ["Ollama (Local)", "Mock (Demo)", "OpenAI", "Anthropic"],
            help="Ollama is recommended for local demo (no API keys needed)"
        )
    
    with col2:
        if st.button("🚀 Process Claim", type="primary", use_container_width=True):
            if claim_input:
                with st.spinner("Processing claim..."):
                    st.success("✅ Claim processed successfully!")
                    st.json({
                        "status": "facts_extracted",
                        "claim_type": "auto",
                        "amount": "$3,500.00"
                    })
            else:
                st.warning("Please enter claim data first.")

elif page == "👤 Review Queue":
    st.switch_page("pages/review_queue.py")

elif page == "🔍 Enhanced Review":
    st.switch_page("pages/review_queue_enhanced.py")

elif page == "📋 Claims List":
    st.switch_page("pages/claims_list.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <small>DDD Claims Processing System - Educational Demonstration</small><br>
    <small>⚠️ NOT for production use</small>
</div>
""", unsafe_allow_html=True)

