"""
Human Review Queue Page - Streamlit

Interface for human reviewers to review AI decisions.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.services import get_service, run_async

st.set_page_config(page_title="Human Review", page_icon="👤", layout="wide")

st.title("👤 Review Queue")
st.markdown("Review and approve/reject AI decisions for claims requiring human oversight.")

# Link to enhanced view
st.info("💡 **New!** Try the [Enhanced Review Interface](review_queue_enhanced) for detailed fraud assessment and comprehensive decision explanations.")

# Refresh button
if st.button("🔄 Refresh"):
    st.rerun()

# Simplified filters
col1, col2 = st.columns(2)

with col1:
    priority_filter = st.selectbox("Priority Filter", ["All", "Urgent", "High", "Medium", "Low"])

with col2:
    status_filter = st.selectbox("Status Filter", ["All", "Pending", "In Review", "Approved", "Rejected"])

# Load review queue
try:
    service = get_service()
    all_reviews = run_async(service.get_review_queue())
    
    # Apply filters
    filtered_reviews = all_reviews
    
    if priority_filter != "All":
        filtered_reviews = [
            r for r in filtered_reviews
            if r.get("priority", "").lower() == priority_filter.lower()
        ]
    
    if status_filter != "All":
        filtered_reviews = [
            r for r in filtered_reviews
            if r.get("status", "").lower() == status_filter.lower().replace(" ", "_")
        ]
    
    # Review queue table
    st.subheader(f"📋 Review Queue ({len(filtered_reviews)} pending)")
    
    if filtered_reviews:
        # Display reviews in a table
        import pandas as pd
        
        df = pd.DataFrame([
            {
                "Claim ID": str(r.get("claim_id", ""))[:8] + "...",
                "Priority": r.get("priority", ""),
                "Reason": r.get("reason", "")[:50] + "..." if len(r.get("reason", "")) > 50 else r.get("reason", ""),
                "Status": r.get("status", ""),
                "AI Decision": r.get("ai_decision", "")[:50] + "..." if len(r.get("ai_decision", "")) > 50 else r.get("ai_decision", ""),
            }
            for r in filtered_reviews
        ])
        
        st.dataframe(df, use_container_width=True)
        
        # Review detail section
        st.subheader("🔍 Review Details")
        
        selected_claim_id = st.selectbox(
            "Select Review",
            [r.get("claim_id", "") for r in filtered_reviews]
        )
        
        if selected_claim_id:
            # Get claim details
            claim_detail = run_async(service.get_claim_by_id(selected_claim_id))
            
            if claim_detail:
                # Display claim information
                st.markdown("### Claim Information")
                claim_info = {
                    "Claim ID": claim_detail.get("claim_id", "")[:8] + "...",
                    "Status": claim_detail.get("status", ""),
                    "Source": claim_detail.get("source", ""),
                }
                
                if claim_detail.get("summary"):
                    summary = claim_detail["summary"]
                    claim_info.update({
                        "Type": summary.get("claim_type", "N/A"),
                        "Amount": summary.get("claimed_amount", "N/A"),
                        "Claimant": summary.get("claimant_name", "N/A"),
                        "Incident Date": summary.get("incident_date", "N/A"),
                    })
                
                st.json(claim_info)
                
                # Find the review item
                review_item = next((r for r in filtered_reviews if r.get("claim_id") == selected_claim_id), None)
                
                if review_item:
                    # Get comprehensive review summary
                    review_summary = run_async(service.get_review_summary(selected_claim_id))
                    
                    if review_summary:
                        fraud_assessment = review_summary.get("fraud_assessment", {})
                        
                        # Display fraud assessment prominently
                        if fraud_assessment:
                            fraud_score = fraud_assessment.get("fraud_score", 0.0)
                            risk_level = fraud_assessment.get("risk_level", "unknown")
                            risk_factors = fraud_assessment.get("risk_factors", [])
                            
                            st.markdown("### 🚩 Fraud Assessment")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Fraud Score", f"{fraud_score:.2f}", 
                                         delta=f"{risk_level.upper()} RISK" if risk_level else None,
                                         delta_color="inverse" if fraud_score >= 0.7 else "off" if fraud_score >= 0.4 else "normal")
                            
                            with col2:
                                st.metric("Risk Level", risk_level.upper() if risk_level else "UNKNOWN")
                            
                            if risk_factors:
                                st.markdown("**Risk Factors Identified:**")
                                for factor in risk_factors:
                                    st.markdown(f"- {factor}")
                            
                            st.markdown("**Assessment Reasoning:**")
                            st.info(fraud_assessment.get("reasoning", "No reasoning provided"))
                    
                    st.markdown("### AI Decision")
                    st.info(f"AI Decision: {review_item.get('ai_decision', 'N/A')}")
                    
                    st.markdown("### Review Reason")
                    st.warning(f"Reason: {review_item.get('reason', 'N/A')}")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ Approve", type="primary", use_container_width=True):
                            st.success("Review approved! (Note: This is a demo - action not persisted)")
                    
                    with col2:
                        if st.button("❌ Reject", use_container_width=True):
                            st.error("Review rejected! (Note: This is a demo - action not persisted)")
                    
                    with col3:
                        if st.button("🔄 Override", use_container_width=True):
                            st.warning("Override option selected. (Note: This is a demo - action not persisted)")
                    
    # Feedback with templates
    st.markdown("### Feedback")
    
    # Feedback templates
    try:
        from data_templates import FEEDBACK_TEMPLATES, get_template
        feedback_templates_available = True
    except ImportError:
        feedback_templates_available = False
    
    if feedback_templates_available:
        feedback_col1, feedback_col2, feedback_col3 = st.columns(3)
        selected_feedback_template = None
        
        with feedback_col1:
            if st.button("✅ Approve Template", use_container_width=True):
                selected_feedback_template = "approve"
        with feedback_col2:
            if st.button("❌ Reject Template", use_container_width=True):
                selected_feedback_template = "reject"
        with feedback_col3:
            if st.button("🔄 Override Template", use_container_width=True):
                selected_feedback_template = "override"
        
        feedback_default = ""
        if selected_feedback_template:
            feedback_default = get_template("feedback", selected_feedback_template)
        
        feedback = st.text_area("Feedback (Optional)", value=feedback_default, height=100, 
                                help="Enter feedback about your review decision. Use template buttons above for quick options.")
    else:
        feedback = st.text_area("Feedback (Optional)", height=100)
    
    if st.button("💾 Submit Review"):
        st.success("Review submitted successfully! (Note: This is a demo - action not persisted)")
    
    if not filtered_reviews:
        st.info("📭 No pending reviews. Claims requiring review will appear here.")
        st.markdown("""
        **Note:** Claims are automatically added to the review queue when they:
        - Have a high claim amount (> $10,000)
        - Have high fraud risk
        - Have policy validation issues
        - Require special handling
        """)
        
except Exception as e:
    st.error(f"Error loading review queue: {str(e)}")
    st.info("💡 Try processing a high-value claim to see the review queue in action.")

