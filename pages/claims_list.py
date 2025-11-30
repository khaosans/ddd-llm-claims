"""
Claims List Page - Streamlit

View and search all claims.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.services import get_service, run_async

st.set_page_config(page_title="Claims List", page_icon="📋", layout="wide")

st.title("📋 Claims List")
st.markdown("View and search all processed claims.")

# Refresh button
if st.button("🔄 Refresh"):
    st.rerun()

# Search templates
try:
    from data_templates import SEARCH_TEMPLATES, get_template
    search_templates_available = True
except ImportError:
    search_templates_available = False

if search_templates_available:
    st.caption("💡 Quick search examples:")
    search_col1, search_col2, search_col3, search_col4 = st.columns(4)
    selected_search_template = None
    
    with search_col1:
        if st.button("🔍 By Name", use_container_width=True, key="search_name"):
            selected_search_template = "by_name"
    with search_col2:
        if st.button("🔍 By Policy", use_container_width=True, key="search_policy"):
            selected_search_template = "by_policy"
    with search_col3:
        if st.button("🔍 By Amount", use_container_width=True, key="search_amount"):
            selected_search_template = "by_amount"
    with search_col4:
        if st.button("🔍 By Date", use_container_width=True, key="search_date"):
            selected_search_template = "by_date"

# Search and filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    search_default = ""
    if search_templates_available and selected_search_template:
        search_default = get_template("search", selected_search_template)
    search_query = st.text_input("🔍 Search", value=search_default, placeholder="Search claims...")

with col2:
    status_filter = st.selectbox("Status", ["All", "Draft", "Facts Extracted", "Policy Validated", "Triaged", "Rejected"])

with col3:
    date_filter = st.date_input("Date Range", value=None)

with col4:
    amount_filter = st.selectbox("Amount", ["All", "< $1,000", "$1,000 - $10,000", "> $10,000"])

# Load claims
try:
    service = get_service()
    all_claims = run_async(service.get_all_claims())
    
    # Apply filters
    filtered_claims = all_claims
    
    if search_query:
        filtered_claims = [
            c for c in filtered_claims
            if search_query.lower() in str(c.get("claimant_name", "")).lower()
            or search_query.lower() in str(c.get("claim_id", "")).lower()
        ]
    
    if status_filter != "All":
        filtered_claims = [
            c for c in filtered_claims
            if c.get("status", "").lower() == status_filter.lower().replace(" ", "_")
        ]
    
    # Claims table
    st.subheader(f"Claims ({len(filtered_claims)} found)")
    
    if filtered_claims:
        # Prepare data for display
        display_data = []
        for claim in filtered_claims:
            display_data.append({
                "Claim ID": claim["claim_id"][:8] + "...",
                "Status": claim["status"],
                "Type": claim.get("claim_type", "N/A"),
                "Amount": claim.get("amount", "N/A"),
                "Claimant": claim.get("claimant_name", "N/A"),
                "Source": claim.get("source", "N/A"),
                "Created": claim.get("created_at", "N/A")[:10] if claim.get("created_at") else "N/A",
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Export button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"claims_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        # Claim detail view
        st.subheader("🔍 Claim Details")
        selected_id = st.selectbox(
            "Select a claim to view details",
            [c["claim_id"] for c in filtered_claims]
        )
        
        if selected_id:
            claim_detail = run_async(service.get_claim_by_id(selected_id))
            if claim_detail:
                # Display claim details with tabs
                tab1, tab2, tab3 = st.tabs(["📋 Claim Details", "🔍 Decisions", "📊 Audit"])
                
                with tab1:
                    st.json(claim_detail)
                
                with tab2:
                    st.subheader("🔍 Decision Details")
                    try:
                        steps_view = run_async(service.get_all_steps_view(selected_id))
                        if steps_view and not steps_view.get("error"):
                            st.write(f"**Total Steps:** {steps_view.get('total_steps', 0)}")
                            
                            for step in steps_view.get("steps", []):
                                # Import decision status helper
                                from src.ui.components.decision_status import analyze_decision_outcome
                                
                                # Analyze decision outcome
                                status_analysis = analyze_decision_outcome(step)
                                status_emoji, status_text, status_color = status_analysis["visual_status"]
                                has_warning = status_analysis["has_warning"]
                                
                                step_name = step.get('step_name', 'Unknown').replace('_', ' ').title()
                                
                                # Color indicators
                                color_emoji = {
                                    "green": "🟢",
                                    "orange": "🟠",
                                    "red": "🔴",
                                }.get(status_color, "⚪")
                                
                                header_text = f"{color_emoji} Step {step.get('step_number')}: {step_name} - {status_emoji} {status_text}"
                                
                                with st.expander(
                                    header_text,
                                    expanded=has_warning
                                ):
                                    # Show warning if applicable
                                    if has_warning and status_analysis["warning_message"]:
                                        if status_color == "red":
                                            st.error(f"🚨 **Critical:** {status_analysis['warning_message']}")
                                        else:
                                            st.warning(f"⚠️ **Warning:** {status_analysis['warning_message']}")
                                    
                                    st.write(f"**Agent:** {step.get('agent', 'N/A')}")
                                    
                                    # Show decision with highlighting
                                    decision_value = step.get("decision", "N/A")
                                    st.write("**Decision:**")
                                    if any(keyword in str(decision_value).lower() for keyword in ["false", "invalid", "reject", "suspicious"]):
                                        st.markdown(f'<div style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ff9800; border-radius: 4px;">{decision_value}</div>', unsafe_allow_html=True)
                                    else:
                                        st.write(decision_value)
                                    
                                    st.write("**Reasoning:**")
                                    if status_color == "red":
                                        st.error(step.get("reasoning", "N/A"))
                                    elif status_color == "orange":
                                        st.warning(step.get("reasoning", "N/A"))
                                    else:
                                        st.info(step.get("reasoning", "N/A"))
                                    
                                    if not step.get("success"):
                                        st.error(f"**Error:** {step.get('error', 'N/A')}")
                        else:
                            st.info("No decision details available.")
                    except Exception as e:
                        st.warning(f"Could not load decisions: {str(e)}")
                
                with tab3:
                    st.subheader("📊 Quick Audit Summary")
                    try:
                        audit = run_async(service.get_audit_summary(selected_id))
                        if audit and not audit.get("error"):
                            summary = audit.get("summary", {})
                            overview = summary.get("overview", {})
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Decisions", overview.get("total_decisions", 0))
                            with col2:
                                st.metric("Success Rate", overview.get("success_rate", "0%"))
                            with col3:
                                status = overview.get("status", "unknown")
                                st.metric("Status", status.replace("_", " ").title())
                            
                            if summary.get("issues"):
                                st.warning("**Issues Found:**")
                                for issue in summary.get("issues", []):
                                    st.write(f"- {issue.get('step', 'Unknown')}: {issue.get('error', 'N/A')}")
                            
                            if summary.get("recommendations"):
                                st.info("**Recommendations:**")
                                for rec in summary.get("recommendations", []):
                                    st.write(f"- {rec.get('message', 'N/A')}")
                        else:
                            st.info("No audit summary available.")
                    except Exception as e:
                        st.warning(f"Could not load audit summary: {str(e)}")
            else:
                st.warning("Could not load claim details.")
    else:
        st.info("📭 No claims found. Process a claim to see it here.")
        
        # Example claim display
        with st.expander("📝 Example Claim Format", expanded=False):
            st.json({
                "claim_id": "example-123",
                "status": "triaged",
                "claim_type": "auto",
                "amount": "$3,500.00",
                "claimant": "John Doe",
                "created_at": "2024-01-16T10:00:00"
            })
            
except Exception as e:
    st.error(f"Error loading claims: {str(e)}")
    st.info("📭 No claims found. Process a claim to see it here.")

