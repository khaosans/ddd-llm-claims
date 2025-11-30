"""
Enhanced Review Queue Page - Comprehensive review interface for human approvers

Provides detailed, explanatory information to help human reviewers make informed decisions.
"""

import streamlit as st
import sys
from pathlib import Path
from uuid import UUID

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.services import get_service, run_async
from src.ui.components.document_viewer import display_documents_list, display_compliance_status
from src.domain.claim.document import DocumentType

st.set_page_config(page_title="Human Review", page_icon="👤", layout="wide")

st.title("👤 Review Queue - Enhanced")
st.markdown("**Comprehensive review interface with detailed fraud assessment and decision explanations**")

# Refresh button
if st.button("🔄 Refresh"):
    st.rerun()

# Load review queue
try:
    service = get_service()
    all_reviews = run_async(service.get_review_queue())
    
    if not all_reviews:
        st.info("📭 No pending reviews. Claims requiring review will appear here.")
        st.markdown("""
        **Claims are automatically added to the review queue when they:**
        - Have high fraud risk (fraud score > 0.7)
        - Have high claim amounts (> $50,000)
        - Have policy validation issues
        - Require special handling
        """)
        st.stop()
    
    # Display review queue
    st.subheader(f"📋 Review Queue ({len(all_reviews)} pending)")
    
    # Select claim to review
    review_options = {
        f"{r.get('claim_id', '')[:8]}... - {r.get('priority', '').upper()} - {r.get('reason', '')[:40]}": r.get('claim_id')
        for r in all_reviews
    }
    
    selected_review_key = st.selectbox(
        "Select Claim to Review",
        list(review_options.keys()),
        help="Select a claim from the review queue to see detailed information"
    )
    
    selected_claim_id = review_options[selected_review_key]
    
    if selected_claim_id:
        # Get comprehensive review summary
        review_summary = run_async(service.get_review_summary(selected_claim_id))
        
        if review_summary:
            claim = review_summary.get("claim", {})
            fraud_assessment = review_summary.get("fraud_assessment", {})
            audit_summary = review_summary.get("audit_summary", {})
            guidance = review_summary.get("guidance", {})
            
            # Header with key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                fraud_score = fraud_assessment.get("fraud_score", 0.0)
                risk_level = fraud_assessment.get("risk_level", "unknown")
                
                # Color code based on risk
                if fraud_score >= 0.7:
                    st.metric("🚩 Fraud Score", f"{fraud_score:.2f}", delta="HIGH RISK", delta_color="inverse")
                elif fraud_score >= 0.4:
                    st.metric("⚠️ Fraud Score", f"{fraud_score:.2f}", delta="MEDIUM RISK", delta_color="off")
                else:
                    st.metric("✓ Fraud Score", f"{fraud_score:.2f}", delta="LOW RISK", delta_color="normal")
            
            with col2:
                risk_display = risk_level.upper() if risk_level else "UNKNOWN"
                st.metric("Risk Level", risk_display)
            
            with col3:
                if claim.get("summary"):
                    amount = claim["summary"].get("claimed_amount", "N/A")
                    st.metric("Claim Amount", f"${amount}" if amount != "N/A" else "N/A")
            
            with col4:
                status = claim.get("status", "unknown")
                st.metric("Status", status.upper())
            
            st.markdown("---")
            
            # Main content in tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Claim Overview", "🚩 Fraud Assessment", "🔍 Decision Details", "📎 Documents", "✅ Review & Action"])
            
            with tab1:
                st.subheader("Claim Information")
                
                if claim.get("summary"):
                    summary = claim["summary"]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Basic Information**")
                        st.json({
                            "Claim ID": claim.get("claim_id", "")[:8] + "...",
                            "Claim Type": summary.get("claim_type", "N/A"),
                            "Claimant": summary.get("claimant_name", "N/A"),
                            "Policy Number": summary.get("policy_number", "N/A"),
                            "Source": claim.get("source", "N/A"),
                        })
                    
                    with col2:
                        st.markdown("**Incident Details**")
                        st.json({
                            "Incident Date": summary.get("incident_date", "N/A"),
                            "Location": summary.get("incident_location", "N/A"),
                            "Amount": f"${summary.get('claimed_amount', 'N/A')}",
                            "Currency": summary.get("currency", "USD"),
                        })
                    
                    st.markdown("**Description**")
                    st.info(summary.get("description", "No description available"))
                    
                    st.markdown("**Original Input**")
                    with st.expander("View Original Claim Data"):
                        st.text(claim.get("raw_input", "N/A"))
            
            with tab2:
                st.subheader("Fraud Assessment Details")
                
                if fraud_assessment:
                    fraud_score = fraud_assessment.get("fraud_score", 0.0)
                    risk_level = fraud_assessment.get("risk_level", "unknown")
                    is_suspicious = fraud_assessment.get("is_suspicious", False)
                    risk_factors = fraud_assessment.get("risk_factors", [])
                    reasoning = fraud_assessment.get("reasoning", "No reasoning provided")
                    confidence = fraud_assessment.get("confidence")
                    
                    # Visual fraud score indicator
                    st.markdown("### Fraud Score Analysis")
                    
                    # Progress bar for fraud score
                    st.progress(fraud_score, text=f"Fraud Score: {fraud_score:.2%}")
                    
                    # Risk level badge
                    if risk_level == "critical" or fraud_score >= 0.8:
                        st.error(f"🚨 **CRITICAL RISK** - Immediate investigation required")
                    elif risk_level == "high" or fraud_score >= 0.6:
                        st.warning(f"⚠️ **HIGH RISK** - Detailed review recommended")
                    elif risk_level == "medium" or fraud_score >= 0.3:
                        st.info(f"ℹ️ **MEDIUM RISK** - Standard review")
                    else:
                        st.success(f"✓ **LOW RISK** - Minimal concerns")
                    
                    # Risk factors
                    if risk_factors:
                        st.markdown("### 🎯 Risk Factors Identified")
                        for i, factor in enumerate(risk_factors, 1):
                            st.markdown(f"{i}. **{factor}**")
                    else:
                        st.info("No specific risk factors identified")
                    
                    # Assessment reasoning
                    st.markdown("### 📝 Assessment Reasoning")
                    st.info(reasoning)
                    
                    # Confidence and method
                    col1, col2 = st.columns(2)
                    with col1:
                        if confidence:
                            st.metric("Confidence", f"{confidence:.1%}")
                    with col2:
                        method = fraud_assessment.get("assessment_method", "unknown")
                        st.metric("Assessment Method", method.replace("_", " ").title())
                    
                    # Timestamp
                    timestamp = fraud_assessment.get("timestamp", "")
                    if timestamp:
                        st.caption(f"Assessment completed: {timestamp}")
                else:
                    st.warning("Fraud assessment details not available")
            
            with tab3:
                st.subheader("Decision Details & Workflow")
                
                # Key decisions
                key_decisions = audit_summary.get("key_decisions", [])
                if key_decisions:
                    st.markdown("### Key Decisions Made")
                    for decision in key_decisions:
                        # Analyze decision status
                        from src.ui.components.decision_status import analyze_decision_outcome
                        
                        # Create step-like dict for analysis
                        step_dict = {
                            "success": decision.get("success", True),
                            "decision_type": decision.get("decision_type", ""),
                            "decision": decision.get("decision", ""),
                            "decision_value": decision.get("decision_value"),
                        }
                        
                        status_analysis = analyze_decision_outcome(step_dict)
                        status_emoji, status_text, status_color = status_analysis["visual_status"]
                        has_warning = status_analysis["has_warning"]
                        
                        # Color indicators
                        color_emoji = {
                            "green": "🟢",
                            "orange": "🟠",
                            "red": "🔴",
                        }.get(status_color, "⚪")
                        
                        step_name = decision.get('step', 'Unknown').replace('_', ' ').title()
                        agent_name = decision.get('agent', 'Unknown Agent')
                        
                        with st.expander(
                            f"{color_emoji} {step_name} - {agent_name} - {status_emoji} {status_text}",
                            expanded=has_warning
                        ):
                            # Show warning if applicable
                            if has_warning and status_analysis["warning_message"]:
                                if status_color == "red":
                                    st.error(f"🚨 **Critical:** {status_analysis['warning_message']}")
                                else:
                                    st.warning(f"⚠️ **Warning:** {status_analysis['warning_message']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Decision:**")
                                decision_value = decision.get("decision", "N/A")
                                if any(keyword in str(decision_value).lower() for keyword in ["false", "invalid", "reject", "suspicious"]):
                                    st.markdown(f'<div style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ff9800; border-radius: 4px;">{decision_value}</div>', unsafe_allow_html=True)
                                else:
                                    st.write(decision_value)
                                
                                st.write(f"**Timestamp:** {decision.get('timestamp', 'N/A')}")
                            
                            with col2:
                                st.write(f"**Status:** {status_emoji} {status_text}")
                                if decision.get("success"):
                                    st.success("✅ Step Executed Successfully")
                                else:
                                    st.error("❌ Step Failed")
                            
                            st.write("**Reasoning:**")
                            if status_color == "red":
                                st.error(decision.get("reasoning", "N/A"))
                            elif status_color == "orange":
                                st.warning(decision.get("reasoning", "N/A"))
                            else:
                                st.info(decision.get("reasoning", "N/A"))
                else:
                    st.info("No decision details available")
                
                # Issues and recommendations
                issues = audit_summary.get("issues", [])
                if issues:
                    st.markdown("### ⚠️ Issues Identified")
                    for issue in issues:
                        st.warning(f"**{issue.get('step', 'Unknown')}**: {issue.get('error', 'N/A')}")
                
                recommendations = audit_summary.get("recommendations", [])
                if recommendations:
                    st.markdown("### 💡 Recommendations")
                    for rec in recommendations:
                        priority = rec.get("priority", "normal")
                        if priority == "high":
                            st.error(f"🔴 **HIGH PRIORITY**: {rec.get('message', 'N/A')}")
                        else:
                            st.info(f"ℹ️ {rec.get('message', 'N/A')}")
            
            with tab4:
                st.subheader("📎 Supporting Documents")
                
                # Get claim documents
                try:
                    from uuid import UUID
                    from src.domain.claim import Claim
                    from src.repositories.claim_repository import ClaimRepository
                    
                    claim_uuid = UUID(selected_claim_id)
                    service = get_service()
                    claim_obj = run_async(service.claim_repository.find_by_id(claim_uuid))
                    
                    if claim_obj and hasattr(claim_obj, 'documents'):
                        display_documents_list(claim_obj.documents)
                        
                        # Display compliance status if available
                        if hasattr(claim_obj, 'summary') and claim_obj.summary:
                            from src.compliance.document_compliance_rules import get_compliance_engine
                            compliance_engine = get_compliance_engine()
                            compliance_result = compliance_engine.evaluate_compliance(claim_obj)
                            
                            display_compliance_status(
                                claim_uuid,
                                compliance_result.get_missing_document_types(),
                                compliance_result.is_compliant,
                            )
                    else:
                        st.info("No documents attached to this claim.")
                except Exception as e:
                    st.warning(f"Could not load documents: {str(e)}")
                    st.info("Documents feature may not be fully integrated yet.")
            
            with tab5:
                st.subheader("Review Decision")
                
                # Find the review item
                review_item = next((r for r in all_reviews if r.get("claim_id") == selected_claim_id), None)
                
                if review_item:
                    st.markdown("### Why This Claim Needs Review")
                    st.warning(f"**Reason**: {review_item.get('reason', 'N/A')}")
                    st.info(f"**AI Decision**: {review_item.get('ai_decision', 'N/A')}")
                    st.caption(f"**Priority**: {review_item.get('priority', 'N/A').upper()}")
                    
                    # Summary for quick decision
                    st.markdown("---")
                    st.markdown("### 📊 Quick Summary")
                    
                    summary_cols = st.columns(3)
                    with summary_cols[0]:
                        st.markdown(f"**Fraud Score**: {fraud_score:.2f}")
                        st.markdown(f"**Risk Level**: {risk_level.upper()}")
                    with summary_cols[1]:
                        if claim.get("summary"):
                            st.markdown(f"**Amount**: ${claim['summary'].get('claimed_amount', 'N/A')}")
                            st.markdown(f"**Type**: {claim['summary'].get('claim_type', 'N/A')}")
                    with summary_cols[2]:
                        st.markdown(f"**Risk Factors**: {len(risk_factors)}")
                        st.markdown(f"**Suspicious**: {'Yes' if is_suspicious else 'No'}")
                    
                    # Actionable recommendations
                    st.markdown("---")
                    st.markdown("### 💡 Recommended Actions")
                    
                    if fraud_score >= 0.7:
                        st.error("""
                        **🔴 HIGH FRAUD RISK DETECTED**
                        
                        **Recommended Actions:**
                        1. Review all risk factors carefully
                        2. Verify claim documentation
                        3. Check claimant history
                        4. Consider fraud investigation
                        5. Request additional evidence if needed
                        """)
                    elif fraud_score >= 0.4:
                        st.warning("""
                        **⚠️ MEDIUM RISK - REVIEW RECOMMENDED**
                        
                        **Recommended Actions:**
                        1. Review identified risk factors
                        2. Verify key claim details
                        3. Check policy coverage
                        4. Request clarification if needed
                        """)
                    else:
                        st.success("""
                        **✓ LOW RISK - STANDARD REVIEW**
                        
                        **Recommended Actions:**
                        1. Verify claim details match policy
                        2. Confirm amount is reasonable
                        3. Check for any data quality issues
                        """)
                    
                    # Decision buttons
                    st.markdown("---")
                    st.markdown("### Make Your Decision")
                    
                    decision_col1, decision_col2, decision_col3 = st.columns(3)
                    
                    with decision_col1:
                        if st.button("✅ Approve", type="primary", use_container_width=True):
                            st.success("✅ Claim approved!")
                            st.balloons()
                    
                    with decision_col2:
                        if st.button("❌ Reject", use_container_width=True):
                            st.error("❌ Claim rejected!")
                    
                    with decision_col3:
                        if st.button("🔄 Override", use_container_width=True):
                            st.warning("🔄 Decision overridden!")
                    
                    # Feedback
                    st.markdown("---")
                    st.markdown("### 📝 Review Feedback")
                    
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
                        
                        feedback = st.text_area(
                            "Enter your review feedback",
                            value=feedback_default,
                            height=150,
                            help="Provide detailed feedback about your decision. Use template buttons above for quick options.",
                            placeholder="Example: Approved after reviewing fraud assessment. Risk factors were minor and claim details verified."
                        )
                    else:
                        feedback = st.text_area(
                            "Enter your review feedback",
                            height=150,
                            placeholder="Provide detailed feedback about your decision..."
                        )
                    
                    if st.button("💾 Submit Review Decision", type="primary"):
                        if feedback:
                            st.success(f"✅ Review submitted with feedback: {feedback[:100]}...")
                        else:
                            st.success("✅ Review submitted!")
                        st.info("💡 Note: In production, this would persist the review decision and update the claim status.")
        else:
            st.error("Could not load review summary for this claim")
    
except Exception as e:
    st.error(f"Error loading review queue: {str(e)}")
    import traceback
    with st.expander("Error Details"):
        st.code(traceback.format_exc())

