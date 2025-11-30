"""
Review Interface Component - Streamlit

Reusable component for human review interface.
"""

import streamlit as st
from typing import List, Dict, Optional, Callable


def render_review_queue(
    reviews: List[Dict],
    on_review: Optional[Callable] = None
) -> None:
    """
    Render review queue interface.
    
    Args:
        reviews: List of review items
        on_review: Callback when review is submitted
    """
    st.subheader("📋 Review Queue")
    
    if not reviews:
        st.info("No pending reviews.")
        return
    
    # Display reviews
    import pandas as pd
    
    df = pd.DataFrame([
        {
            "Claim ID": str(r.get("claim_id", ""))[:8],
            "Priority": r.get("priority", ""),
            "Reason": r.get("reason", "")[:50],
            "Status": r.get("status", ""),
        }
        for r in reviews
    ])
    
    st.dataframe(df, use_container_width=True)
    
    # Review detail
    if reviews:
        selected_idx = st.selectbox("Select Review", range(len(reviews)), format_func=lambda x: f"Review {x+1}")
        selected_review = reviews[selected_idx]
        
        render_review_detail(selected_review, on_review)


def render_review_detail(
    review: Dict,
    on_submit: Optional[Callable] = None
) -> None:
    """
    Render review detail interface.
    
    Args:
        review: Review item dictionary
        on_submit: Callback when review is submitted
    """
    st.subheader("🔍 Review Details")
    
    # Claim info
    st.markdown("### Claim Information")
    st.json(review.get("claim", {}))
    
    # AI decision
    st.markdown("### AI Decision")
    st.info(review.get("ai_decision", ""))
    
    # Review reason
    st.markdown("### Review Reason")
    st.warning(review.get("reason", ""))
    
    # Actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        approve = st.button("✅ Approve", type="primary", use_container_width=True)
    
    with col2:
        reject = st.button("❌ Reject", use_container_width=True)
    
    with col3:
        override = st.button("🔄 Override", use_container_width=True)
    
    # Feedback
    feedback = st.text_area("Feedback (Optional)", height=100)
    
    # Submit
    if approve or reject or override:
        decision = "approved" if approve else ("rejected" if reject else "overridden")
        
        if on_submit:
            on_submit(review, decision, feedback)
        else:
            st.success(f"Review {decision}!")

