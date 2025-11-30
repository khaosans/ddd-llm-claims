"""
Process Claim Page - Streamlit

Simplified, guided claim processing interface with inline demo mode.
"""

import streamlit as st
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.services import get_service, run_async
from src.ui.demo_workflow import create_demo_workflow
from src.ui.utils import get_local_model_info, get_available_ollama_model

st.set_page_config(page_title="Process Claim", page_icon="📝", layout="wide")

# Initialize session state
if "last_claim_result" not in st.session_state:
    st.session_state.last_claim_result = None
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = True  # Default to demo mode
if "processing" not in st.session_state:
    st.session_state.processing = False

st.title("📝 Process Claim")
st.markdown("Enter unstructured claim data and watch it process through the system step-by-step.")

# Demo mode toggle
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("**Choose processing mode:**")
with col2:
    demo_mode = st.toggle("🎬 Demo Mode", value=True, help="Show step-by-step progress (recommended for first-time users)")

st.session_state.demo_mode = demo_mode

# Template selection - simplified
try:
    from data_templates import CLAIM_TEMPLATES, get_template
    templates_available = True
except ImportError:
    templates_available = False

# Enhanced template selector with categories
if templates_available:
    # Organize templates by category
    template_categories = {
        "✅ Legitimate Claims": {
            "🚗 Auto Insurance": "auto_insurance_claim",
            "🏠 Property Damage": "property_damage_claim",
            "💰 High Value Claim": "high_value_claim",
            "📝 Simple Claim": "simple_claim",
            "🏥 Health Insurance": "health_insurance_claim",
            "💼 Life Insurance": "life_insurance_claim",
            "🦽 Disability Insurance": "disability_insurance_claim",
            "✈️ Travel Insurance": "travel_insurance_claim",
            "✅ Good Legitimate Claim": "good_legitimate_claim",
            "✅ Good Property Claim": "good_property_claim",
            "✅ Good Health Claim": "good_health_claim",
        },
        "🚨 Fraud/Issues": {
            "🚨 Stolen Vehicle": "fraud_risk_claim",
            "🚨 Stolen Vehicle Fraud": "stolen_vehicle_fraud",
            "🚨 Inflated Damage": "inflated_damage_claim",
            "🚨 Duplicate Claim": "duplicate_claim",
            "🚨 Suspicious Timing": "suspicious_timing",
            "🚨 Multiple Vehicles Stolen": "multiple_vehicles_stolen",
            "🚨 Excessive Medical Claims": "excessive_medical_claims",
            "🚨 Coordinate Fraud": "coordinate_fraud",
        },
        "⚠️ Data Quality Issues": {
            "⚠️ Missing Documentation": "missing_documentation",
            "⚠️ Inconsistent Story": "inconsistent_story",
            "⚠️ Missing Critical Fields": "missing_critical_fields",
            "⚠️ Invalid Date Format": "invalid_date_format",
            "⚠️ Invalid Amount Format": "invalid_amount_format",
            "⚠️ Missing Policy Number": "missing_policy_number",
            "⚠️ Bad Health Claim": "bad_health_claim_missing_docs",
        },
        "❌ Policy Issues": {
            "❌ Expired Policy": "expired_policy_claim",
            "❌ Coverage Mismatch": "coverage_mismatch",
            "❌ Amount Exceeds Coverage": "amount_exceeds_coverage",
            "❌ Policy Lapse": "policy_lapse_claim",
        },
        "🔍 Edge Cases": {
            "🔍 Zero Amount": "edge_case_zero_amount",
            "🔍 Very Old Incident": "edge_case_very_old_incident",
            "🔍 Future Date": "edge_case_future_date",
            "🔍 Multiple Claims": "multiple_claims_short_period",
            "🔍 Claim After Policy Start": "claim_after_policy_start",
        },
        "📞 Other Formats": {
            "📞 Phone Transcript": "phone_transcript",
            "🌐 Web Form": "web_form_submission",
        },
    }
    
    # Create expandable sections for each category
    selected_template = None
    st.markdown("**📋 Select a template by category:**")
    
    for category, templates in template_categories.items():
        with st.expander(category, expanded=(category == "✅ Legitimate Claims")):
            cols = st.columns(2)
            for idx, (display_name, template_key) in enumerate(templates.items()):
                col = cols[idx % 2]
                if col.button(display_name, key=f"template_{category}_{template_key}", use_container_width=True):
                    selected_template = template_key
                    st.success(f"✅ Selected: {display_name}")
    
    if selected_template:
        st.info(f"💡 Template '{selected_template}' selected. Scroll down to see it in the input field.")
else:
    selected_template = None

# Input section
st.subheader("📥 Claim Data")
default_value = ""
if templates_available and selected_template:
    default_value = get_template("claim", selected_template)

claim_input = st.text_area(
    "Unstructured Claim Data",
    value=default_value,
    height=200,
    placeholder="""Example:
Subject: Auto Insurance Claim

I had a car accident on January 15, 2024 at 2:30 PM.
Location: Main Street and Oak Avenue.
Damage: $3,500.00
Policy: POL-2024-001234

John Doe""",
    disabled=st.session_state.processing
)

# Document upload section
st.subheader("📎 Supporting Documents")
st.markdown("Upload supporting documents such as photos, police reports, invoices, etc.")

uploaded_files = st.file_uploader(
    "Upload Documents",
    type=["pdf", "png", "jpg", "jpeg", "gif", "bmp", "tiff", "doc", "docx"],
    accept_multiple_files=True,
    help="Supported formats: PDF, Images (PNG, JPG, JPEG, GIF, BMP, TIFF), Word documents",
    disabled=st.session_state.processing
)

# Document type selection for uploaded files
uploaded_documents = []
if uploaded_files:
    st.markdown("**Document Types:**")
    for i, uploaded_file in enumerate(uploaded_files):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"📄 {uploaded_file.name} ({uploaded_file.size:,} bytes)")
        with col2:
            doc_type = st.selectbox(
                f"Type for {uploaded_file.name[:20]}...",
                ["photo", "police_report", "invoice", "receipt", "medical_record", "appraisal", "estimate", "repair_order", "witness_statement", "insurance_form", "other"],
                key=f"doc_type_{i}",
                label_visibility="collapsed"
            )
        uploaded_documents.append({
            "file": uploaded_file,
            "type": doc_type,
            "name": uploaded_file.name
        })

# Configuration - simplified
with st.expander("⚙️ Advanced Settings", expanded=False):
    col1, col2 = st.columns(2)
    
    with col1:
        # Get available models info
        model_info = get_local_model_info()
        available_model = get_available_ollama_model()
        
        provider_options = ["Mock (Demo)"]
        default_index = 0
        
        if model_info["ollama_available"] and available_model:
            provider_options.insert(0, f"Ollama (Local) - {available_model}")
            default_index = 0
        
        provider_options.extend(["Ollama (Local)", "OpenAI", "Anthropic"])
        
        model_provider = st.selectbox(
            "🤖 Model Provider",
            provider_options,
            index=default_index,
            help=f"Mock mode works without setup. Ollama detected: {available_model if available_model else 'None'}"
        )
    
    with col2:
        source = st.selectbox(
            "📧 Source",
            ["email", "web", "phone", "form"],
            help="Source of the claim"
        )
    
    if demo_mode:
        step_delay = st.slider(
            "Step Delay (seconds)",
            min_value=0.5,
            max_value=3.0,
            value=1.5,
            step=0.5,
            help="Time between workflow steps in demo mode"
        )
    else:
        step_delay = 0.5

# Process button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    process_button = st.button(
        "🚀 Process Claim" if not demo_mode else "🎬 Start Demo",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.processing or not claim_input
    )

# Processing logic
if process_button and claim_input:
    st.session_state.processing = True
    st.session_state.last_claim_result = None
    
    # Map provider selection
    provider_type = "mock"
    selected_model = None
    
    if "Ollama" in model_provider:
        provider_type = "ollama"
        # Extract model name if specified in the option
        if " - " in model_provider:
            selected_model = model_provider.split(" - ")[1]
        else:
            # Use auto-detected model
            selected_model = get_available_ollama_model()
    
    if demo_mode:
        # Demo mode with step-by-step visualization
        progress_container = st.container()
        
        with progress_container:
            st.markdown("---")
            st.subheader("🔄 Processing Workflow")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            step_details = st.empty()
            workflow_steps_display = st.empty()
            
            try:
                service = get_service()
                # Initialize with selected model
                if provider_type == "ollama" and selected_model:
                    run_async(service._ensure_initialized(provider_type, selected_model))
                else:
                    run_async(service._ensure_initialized(provider_type))
                
                demo_workflow = create_demo_workflow(service)
                demo_workflow.set_step_delay(step_delay)
                
                # Decision display container
                decisions_container = st.container()
                
                # Progress callback
                def update_progress(message, step, progress, result):
                    progress_bar.progress(progress / 100)
                    status_text.info(f"**{message}**")
                    
                    # Update workflow steps display
                    completed_steps = result.get("steps_completed", [])
                    current_step = result.get("current_step", "")
                    
                    steps_html = "**Workflow Steps:**\n\n"
                    if "facts_extracted" in completed_steps:
                        steps_html += "- ✅ **Facts Extracted** - Intake Agent extracted structured facts\n"
                    elif current_step == "extracting_facts":
                        steps_html += "- ⏳ **Extracting Facts** - Intake Agent processing...\n"
                    else:
                        steps_html += "- ⏸️ Facts Extracted\n"
                    
                    if "policy_validated" in completed_steps:
                        steps_html += "- ✅ **Policy Validated** - Policy Agent validated coverage\n"
                    elif current_step == "validating_policy":
                        steps_html += "- ⏳ **Validating Policy** - Policy Agent checking...\n"
                    else:
                        steps_html += "- ⏸️ Policy Validated\n"
                    
                    if "fraud_assessed" in completed_steps:
                        steps_html += "- ✅ **Fraud Assessed** - Fraud assessment completed\n"
                    elif current_step == "assessing_fraud":
                        steps_html += "- ⏳ **Assessing Fraud** - Analyzing risk...\n"
                    else:
                        steps_html += "- ⏸️ Fraud Assessed\n"
                    
                    if "triaged" in completed_steps:
                        steps_html += "- ✅ **Routed** - Claim routed to processing\n"
                    elif current_step == "triaging":
                        steps_html += "- ⏳ **Routing** - Triage Agent determining route...\n"
                    else:
                        steps_html += "- ⏸️ Routed\n"
                    
                    workflow_steps_display.markdown(steps_html)
                    
                    # Show decisions if claim_id is available
                    claim_id = result.get("claim_id")
                    if claim_id:
                        try:
                            service = get_service()
                            decision_status = run_async(service.get_decision_status(claim_id))
                            
                            if decision_status and not decision_status.get("error"):
                                with decisions_container:
                                    st.markdown("---")
                                    st.subheader("🔍 Decisions Made So Far")
                                    
                                    progress_data = decision_status.get("progress", {})
                                    decisions_list = progress_data.get("steps", {})
                                    
                                    if decisions_list:
                                        for step_name, step_data in decisions_list.items():
                                            step_decisions = step_data.get("decisions", [])
                                            if step_decisions:
                                                with st.expander(f"📋 {step_name.replace('_', ' ').title()} ({len(step_decisions)} decision(s))", expanded=False):
                                                    for decision in step_decisions:
                                                        col1, col2 = st.columns([3, 1])
                                                        with col1:
                                                            st.write(f"**Agent:** {decision.get('agent', 'N/A')}")
                                                            st.write(f"**Decision:** {decision.get('decision', 'N/A')}")
                                                            st.write(f"**Reasoning:** {decision.get('reasoning', 'N/A')[:200]}...")
                                                        with col2:
                                                            if decision.get('success'):
                                                                st.success("✅ Success")
                                                            else:
                                                                st.error("❌ Failed")
                                    else:
                                        st.info("No decisions recorded yet for this step.")
                        except Exception:
                            pass  # Silently fail if decision viewing not available
                
                # Process with demo workflow
                result = run_async(demo_workflow.process_claim_demo(
                    claim_input,
                    source,
                    provider_type,
                    progress_callback=update_progress
                ))
                
                # Add documents if uploaded
                if uploaded_documents and result.get("claim_id"):
                    try:
                        from uuid import UUID
                        from src.storage.document_storage import DocumentStorageService
                        from src.domain.claim.document import DocumentType
                        
                        claim_id = UUID(result["claim_id"])
                        storage_service = DocumentStorageService()
                        service = get_service()
                        
                        for doc_info in uploaded_documents:
                            file_content = doc_info["file"].read()
                            doc_type_enum = DocumentType(doc_info["type"])
                            
                            # Store document
                            document = storage_service.store_document(
                                claim_id=claim_id,
                                file_content=file_content,
                                filename=doc_info["name"],
                                document_type=doc_type_enum,
                            )
                            
                            # Add to claim via orchestrator
                            orchestrator = service.orchestrator
                            run_async(orchestrator.add_document_to_claim(
                                claim_id=claim_id,
                                file_content=file_content,
                                filename=doc_info["name"],
                                document_type=doc_info["type"],
                            ))
                        
                        if uploaded_documents:
                            st.success(f"✅ {len(uploaded_documents)} document(s) uploaded and processed")
                    except Exception as e:
                        st.warning(f"⚠️ Document upload failed: {str(e)}")
                
                st.session_state.last_claim_result = result
                st.session_state.processing = False
                
                # Check for human review
                if result.get("requires_review"):
                    st.markdown("---")
                    st.warning("⚠️ **Human Review Required**")
                    st.info(f"**Reason:** {result.get('review_reason', 'N/A')}")
                    
                    # Human review interface
                    st.subheader("👤 Review Decision")
                    review_col1, review_col2, review_col3 = st.columns(3)
                    
                    with review_col1:
                        if st.button("✅ Approve", type="primary", use_container_width=True):
                            st.success("✅ Claim approved! (Demo mode)")
                            st.balloons()
                    
                    with review_col2:
                        if st.button("❌ Reject", use_container_width=True):
                            st.error("❌ Claim rejected! (Demo mode)")
                    
                    with review_col3:
                        if st.button("🔄 Override", use_container_width=True):
                            st.warning("🔄 Decision overridden! (Demo mode)")
                    
                    feedback = st.text_area("Feedback (Optional)", height=100,
                                            placeholder="Enter your review feedback here...")
                    if st.button("💾 Submit Review Decision"):
                        st.success("Review decision submitted! (Demo mode)")
                
            except ValueError as e:
                error_msg = str(e).lower()
                st.error(f"❌ Error processing claim: {str(e)}")
                
                # Provide specific guidance based on error type
                if "json" in error_msg or "parse" in error_msg or "extra data" in error_msg:
                    st.warning("""
                    **JSON Parsing Error Detected**
                    
                    The LLM returned malformed JSON. This can happen with:
                    - Models that add explanations after JSON
                    - Network interruptions
                    - Model limitations
                    
                    **Solutions:**
                    1. Try again (may be transient)
                    2. Switch to Mock mode for reliable testing
                    3. Try a different Ollama model
                    """)
                elif "ollama" in error_msg or "404" in error_msg or "not found" in error_msg:
                    st.warning("""
                    **Ollama Model Issue**
                    
                    The selected model may not be available.
                    
                    **Solutions:**
                    1. Check available models: `ollama list`
                    2. Ensure Ollama is running: `ollama serve`
                    3. Use Mock mode as fallback
                    """)
                else:
                    st.info("💡 Try using Mock mode if you're having issues with Ollama.")
                
                with st.expander("🔧 Technical Details"):
                    import traceback
                    st.code(traceback.format_exc())
                st.session_state.processing = False
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.info("💡 Try using Mock mode or check the Technical Details below.")
                with st.expander("🔧 Technical Details"):
                    import traceback
                    st.code(traceback.format_exc())
                st.session_state.processing = False
    else:
        # Quick mode - no step-by-step
        with st.spinner("🔄 Processing claim..."):
            try:
                service = get_service()
                # Initialize with selected model
                if provider_type == "ollama" and selected_model:
                    run_async(service._ensure_initialized(provider_type, selected_model))
                else:
                    run_async(service._ensure_initialized(provider_type))
                
                result = run_async(service.process_claim(claim_input, source, provider_type))
                
                # Add documents if uploaded
                if uploaded_documents and result.get("claim_id"):
                    try:
                        from uuid import UUID
                        from src.storage.document_storage import DocumentStorageService
                        from src.domain.claim.document import DocumentType
                        
                        claim_id = UUID(result["claim_id"])
                        storage_service = DocumentStorageService()
                        service = get_service()
                        
                        for doc_info in uploaded_documents:
                            file_content = doc_info["file"].read()
                            doc_type_enum = DocumentType(doc_info["type"])
                            
                            # Store document
                            document = storage_service.store_document(
                                claim_id=claim_id,
                                file_content=file_content,
                                filename=doc_info["name"],
                                document_type=doc_type_enum,
                            )
                            
                            # Add to claim via orchestrator
                            orchestrator = service.orchestrator
                            run_async(orchestrator.add_document_to_claim(
                                claim_id=claim_id,
                                file_content=file_content,
                                filename=doc_info["name"],
                                document_type=doc_info["type"],
                            ))
                        
                        if uploaded_documents:
                            st.success(f"✅ {len(uploaded_documents)} document(s) uploaded and processed")
                    except Exception as e:
                        st.warning(f"⚠️ Document upload failed: {str(e)}")
                
                st.session_state.last_claim_result = result
                st.session_state.processing = False
                
                st.success(f"✅ Claim processed successfully!")
                
            except ValueError as e:
                error_msg = str(e).lower()
                st.error(f"❌ Error processing claim: {str(e)}")
                
                # Provide specific guidance based on error type
                if "json" in error_msg or "parse" in error_msg:
                    st.warning("💡 JSON parsing issue detected. Try Mock mode or retry.")
                elif "ollama" in error_msg:
                    st.warning("💡 Ollama issue detected. Check Ollama is running.")
                else:
                    st.info("💡 Try using Mock mode if you're having issues.")
                
                with st.expander("🔧 Technical Details"):
                    import traceback
                    st.code(traceback.format_exc())
                st.session_state.processing = False
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
                st.info("💡 Try using Mock mode or check Technical Details.")
                with st.expander("🔧 Technical Details"):
                    import traceback
                    st.code(traceback.format_exc())
                st.session_state.processing = False

# Display results
if st.session_state.last_claim_result and not st.session_state.processing:
    result = st.session_state.last_claim_result
    
    st.markdown("---")
    st.subheader("📊 Results")
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Claim ID", result.get("claim_id", "N/A")[:8] + "..." if result.get("claim_id") else "N/A")
    with col2:
        st.metric("Status", result.get("status", "N/A"))
    with col3:
        progress = result.get("progress", 100)
        st.metric("Progress", f"{progress}%")
    
    # Decision Summary Tab
    claim_id = result.get("claim_id")
    if claim_id:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Extracted Facts", "🔍 Decisions", "📊 Audit Summary", "📈 Completion Summary", "🖼️ Document Matching"])
        
        with tab1:
            # Extracted facts
            if result.get("summary"):
                st.subheader("📋 Extracted Facts")
                st.json(result["summary"])
            
            # Workflow steps summary
            if result.get("workflow_steps"):
                st.subheader("🔄 Workflow Summary")
                for icon, step, description in result["workflow_steps"]:
                    st.markdown(f"{icon} **{step}** - {description}")
        
        with tab2:
            # Decisions View
            st.subheader("🔍 Decision Details")
            try:
                service = get_service()
                
                # Get step-by-step view
                steps_view = run_async(service.get_all_steps_view(claim_id))
                
                if steps_view and not steps_view.get("error"):
                    from src.ui.components.decision_status import analyze_decision_outcome
                    
                    # Calculate summary statistics
                    steps = steps_view.get("steps", [])
                    total_steps = len(steps)
                    warnings_count = 0
                    errors_count = 0
                    critical_count = 0
                    
                    for step in steps:
                        status_analysis = analyze_decision_outcome(step)
                        if status_analysis["outcome_type"] == "error":
                            errors_count += 1
                            if status_analysis["status_color"] == "red":
                                critical_count += 1
                        elif status_analysis["outcome_type"] == "warning":
                            warnings_count += 1
                    
                    # Display summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Steps", total_steps)
                    with col2:
                        if warnings_count > 0:
                            st.metric("⚠️ Warnings", warnings_count, delta="Needs Attention", delta_color="off")
                        else:
                            st.metric("⚠️ Warnings", 0)
                    with col3:
                        if errors_count > 0:
                            st.metric("❌ Errors", errors_count, delta="Failed", delta_color="inverse")
                        else:
                            st.metric("❌ Errors", 0)
                    with col4:
                        overall_status = "✅ All Good" if warnings_count == 0 and errors_count == 0 else "⚠️ Review Needed" if warnings_count > 0 else "❌ Issues Found"
                        st.metric("Overall Status", overall_status)
                    
                    if warnings_count > 0 or errors_count > 0:
                        st.markdown("---")
                    
                    for step in steps_view.get("steps", []):
                        # Import decision status helper
                        from src.ui.components.decision_status import analyze_decision_outcome, get_status_badge_html
                        
                        # Analyze decision outcome
                        status_analysis = analyze_decision_outcome(step)
                        status_emoji, status_text, status_color = status_analysis["visual_status"]
                        has_warning = status_analysis["has_warning"]
                        
                        # Determine step header
                        step_name = step.get('step_name', 'Unknown').replace('_', ' ').title()
                        
                        # Color indicators
                        color_emoji = {
                            "green": "🟢",
                            "orange": "🟠",
                            "red": "🔴",
                        }.get(status_color, "⚪")
                        
                        # Build header with status
                        header_text = f"{color_emoji} Step {step.get('step_number')}: {step_name} - {status_emoji} {status_text}"
                        
                        with st.expander(
                            header_text,
                            expanded=has_warning  # Auto-expand warnings
                        ):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**Agent:** {step.get('agent', 'N/A')}")
                                st.write(f"**Type:** {step.get('decision_type', 'N/A')}")
                                st.write(f"**Timestamp:** {step.get('timestamp', 'N/A')}")
                            with col2:
                                if step.get("confidence"):
                                    st.write(f"**Confidence:** {step.get('confidence')}")
                                if step.get("has_context"):
                                    st.write("**Has Context:** ✅")
                            
                            st.write("**Decision:**")
                            st.code(str(step.get("decision", "N/A"))[:500], language=None)
                            
                            # Show warning if applicable
                            if has_warning and status_analysis["warning_message"]:
                                if status_color == "red":
                                    st.error(f"🚨 **Critical:** {status_analysis['warning_message']}")
                                else:
                                    st.warning(f"⚠️ **Warning:** {status_analysis['warning_message']}")
                            
                            st.write("**Reasoning:**")
                            # Use different color based on outcome
                            if status_color == "red":
                                st.error(step.get("reasoning", "N/A"))
                            elif status_color == "orange":
                                st.warning(step.get("reasoning", "N/A"))
                            else:
                                st.info(step.get("reasoning", "N/A"))
                            
                            if not step.get("success") and step.get("error"):
                                st.error(f"**Error:** {step.get('error')}")
                            
                            # Show decision value with highlighting
                            decision_value = step.get("decision", "N/A")
                            if decision_value != "N/A":
                                st.write("**Decision:**")
                                # Highlight negative outcomes
                                if any(keyword in str(decision_value).lower() for keyword in ["false", "invalid", "reject", "suspicious", "non-compliant"]):
                                    st.markdown(f'<div style="background-color: #fff3cd; padding: 10px; border-left: 4px solid #ff9800; border-radius: 4px;">{decision_value}</div>', unsafe_allow_html=True)
                                else:
                                    st.code(str(decision_value)[:500], language=None)
                            
                            if step.get("depends_on"):
                                st.write("**Dependencies:**")
                                for dep in step.get("depends_on", []):
                                    st.caption(f"- Depends on decision: {dep.get('decision_id', 'N/A')[:8]}...")
                else:
                    st.info("No decision details available yet.")
            except Exception as e:
                st.warning(f"Could not load decision details: {str(e)}")
        
        with tab3:
            # Audit Summary
            st.subheader("📊 Quick Audit Summary")
            try:
                service = get_service()
                audit = run_async(service.get_audit_summary(claim_id))
                
                if audit and not audit.get("error"):
                    summary = audit.get("summary", {})
                    guidance = audit.get("guidance", {})
                    
                    # Overview
                    overview = summary.get("overview", {})
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Decisions", overview.get("total_decisions", 0))
                    with col2:
                        st.metric("Successful", overview.get("successful", 0))
                    with col3:
                        st.metric("Failed", overview.get("failed", 0))
                    with col4:
                        status = overview.get("status", "unknown")
                        status_emoji = {"healthy": "✅", "needs_review": "⚠️", "critical": "🔴"}.get(status, "❓")
                        st.metric("Status", f"{status_emoji} {status.replace('_', ' ').title()}")
                    
                    # Key Decisions
                    if summary.get("key_decisions"):
                        st.subheader("🎯 Key Decisions")
                        for decision in summary.get("key_decisions", []):
                            with st.expander(f"📋 {decision.get('step', 'Unknown').replace('_', ' ').title()}"):
                                st.write(f"**Agent:** {decision.get('agent', 'N/A')}")
                                st.write(f"**Decision:** {decision.get('decision', 'N/A')}")
                                st.write(f"**Reasoning:** {decision.get('reasoning', 'N/A')}")
                                st.write(f"**Timestamp:** {decision.get('timestamp', 'N/A')}")
                    
                    # Issues
                    if summary.get("issues"):
                        st.subheader("⚠️ Issues Found")
                        for issue in summary.get("issues", []):
                            st.error(f"**{issue.get('step', 'Unknown')}:** {issue.get('error', 'N/A')}")
                    
                    # Recommendations
                    if summary.get("recommendations"):
                        st.subheader("💡 Recommendations")
                        for rec in summary.get("recommendations", []):
                            st.info(f"**{rec.get('message', 'N/A')}**")
                    
                    # Audit Guidance
                    if guidance:
                        st.subheader("📋 Audit Guidance")
                        if guidance.get("red_flags"):
                            st.warning("**Red Flags Detected:**")
                            for flag in guidance.get("red_flags", []):
                                st.write(f"- {flag.get('issue', 'N/A')}")
                                st.caption(f"  Action: {flag.get('action_required', 'N/A')}")
                        
                        if guidance.get("checklist"):
                            st.write("**Review Checklist:**")
                            for item in guidance.get("checklist", []):
                                status_icon = "✅" if item.get("status") == "completed" else "⏳"
                                st.write(f"{status_icon} {item.get('item', 'N/A')}")
                else:
                    st.info("No audit summary available yet.")
            except Exception as e:
                st.warning(f"Could not load audit summary: {str(e)}")
        
        with tab4:
            # Completion Summary
            st.subheader("📈 Completion Summary")
            try:
                service = get_service()
                completion = run_async(service.get_completion_summary(claim_id))
                
                if completion and not completion.get("error"):
                    # Executive Summary
                    exec_summary = completion.get("executive_summary", {})
                    st.subheader("📊 Executive Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Decisions", exec_summary.get("total_decisions", 0))
                    with col2:
                        st.metric("Success Rate", exec_summary.get("success_rate", "0%"))
                    with col3:
                        overall_status = exec_summary.get("overall_status", "unknown")
                        status_emoji = "✅" if overall_status == "completed" else "⚠️"
                        st.metric("Status", f"{status_emoji} {overall_status.replace('_', ' ').title()}")
                    
                    # Findings
                    if completion.get("findings"):
                        st.subheader("🔍 Findings")
                        for finding in completion.get("findings", []):
                            severity = finding.get("severity", "medium")
                            severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(severity, "⚪")
                            with st.expander(f"{severity_emoji} {finding.get('type', 'Unknown').replace('_', ' ').title()} - {finding.get('severity', 'medium').upper()}"):
                                st.write(f"**Finding:** {finding.get('finding', 'N/A')}")
                                st.write(f"**Impact:** {finding.get('impact', 'N/A')}")
                    
                    # Recommendations
                    if completion.get("recommendations"):
                        st.subheader("💡 Recommendations")
                        for rec in completion.get("recommendations", []):
                            priority = rec.get("priority", "medium")
                            priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
                            with st.expander(f"{priority_emoji} {priority.upper()}: {rec.get('recommendation', 'N/A')}"):
                                st.write(f"**Category:** {rec.get('category', 'N/A').replace('_', ' ').title()}")
                                if rec.get("action_items"):
                                    st.write("**Action Items:**")
                                    for action in rec.get("action_items", []):
                                        st.write(f"- {action}")
                else:
                    st.info("No completion summary available yet.")
            except Exception as e:
                st.warning(f"Could not load completion summary: {str(e)}")
        
        with tab5:
            # Document Matching Results
            st.subheader("🖼️ Document Matching Results")
            try:
                from src.compliance.decision_audit import get_audit_service
                from src.compliance.models import DecisionType
                from uuid import UUID
                
                audit_service = get_audit_service()
                decisions = audit_service.get_decisions_for_claim(UUID(claim_id))
                
                # Find document matching decisions
                matching_decisions = [
                    d for d in decisions 
                    if d.decision_type == DecisionType.DOCUMENT_MATCHING
                ]
                
                if matching_decisions:
                    # Get latest matching decision
                    latest_match = matching_decisions[-1]
                    match_data = latest_match.decision_value
                    
                    if isinstance(match_data, dict):
                        # Display match score
                        match_score = match_data.get("match_score", 0.0)
                        score_color = "🟢" if match_score >= 0.7 else "🟡" if match_score >= 0.5 else "🔴"
                        st.metric("Match Score", f"{match_score:.2%}", delta=f"{score_color} {'High' if match_score >= 0.7 else 'Medium' if match_score >= 0.5 else 'Low'} Match")
                        
                        # Missing documents
                        missing_docs = match_data.get("missing_documents", [])
                        if missing_docs:
                            st.warning(f"⚠️ **Missing Required Documents:** {', '.join(missing_docs)}")
                            st.info("Please upload these required documents to proceed with the claim.")
                        
                        # Matched elements
                        matched = match_data.get("matched_elements", [])
                        if matched:
                            st.success(f"✅ **Matched Elements:** {', '.join(matched)}")
                        
                        # Mismatches
                        mismatches = match_data.get("mismatches", [])
                        if mismatches:
                            st.warning(f"⚠️ **Found {len(mismatches)} Mismatch(es):**")
                            for mismatch in mismatches[:5]:  # Show top 5
                                st.write(f"- {mismatch}")
                        
                        # Recommendations
                        recommendations = match_data.get("recommendations", [])
                        if recommendations:
                            st.subheader("💡 Recommendations")
                            for rec in recommendations[:5]:  # Show top 5
                                st.info(f"• {rec}")
                        
                        # Cost summary (if available)
                        try:
                            from src.agents.cost_tracker import get_cost_tracker
                            cost_tracker = get_cost_tracker()
                            cost_summary = cost_tracker.get_summary()
                            
                            with st.expander("💰 Cost Summary"):
                                st.metric("Total Cost", f"${cost_summary.get('total_cost', 0):.4f}")
                                st.metric("Total Calls", cost_summary.get('total_calls', 0))
                                st.metric("Vision Calls", cost_summary.get('vision_calls', 0))
                                
                                if cost_summary.get('provider_breakdown'):
                                    st.subheader("Provider Breakdown")
                                    for provider, stats in cost_summary['provider_breakdown'].items():
                                        st.write(f"**{provider.title()}:**")
                                        st.write(f"- Cost: ${stats.get('total_cost', 0):.4f}")
                                        st.write(f"- Calls: {stats.get('total_calls', 0)}")
                                        st.write(f"- Vision Calls: {stats.get('vision_calls', 0)}")
                        except Exception:
                            pass  # Cost tracking not critical for UI
                    else:
                        st.info("Document matching data not available in expected format.")
                else:
                    st.info("📋 Document matching not yet completed. Matching runs after document validation.")
                    
                    # Show provider status
                    try:
                        from src.agents.api_config import get_api_config_manager
                        config_manager = get_api_config_manager()
                        available = config_manager.get_available_providers()
                        
                        st.subheader("🔧 Model Provider Status")
                        for provider, is_available in available.items():
                            status = "✅ Available" if is_available else "❌ Not Available"
                            st.write(f"**{provider.title()}:** {status}")
                    except Exception:
                        pass
                        
            except Exception as e:
                st.warning(f"Could not load document matching results: {str(e)}")
    else:
        # Fallback to old display if no claim_id
        # Extracted facts
        if result.get("summary"):
            st.subheader("📋 Extracted Facts")
            st.json(result["summary"])
        
        # Workflow steps summary
        if result.get("workflow_steps"):
            st.subheader("🔄 Workflow Summary")
            for icon, step, description in result["workflow_steps"]:
                st.markdown(f"{icon} **{step}** - {description}")
    
    # Full details (collapsible)
    with st.expander("📋 Full Details", expanded=False):
        st.json(result)

# Instructions
if not st.session_state.last_claim_result and not st.session_state.processing:
    st.info("""
    **How to use:**
    1. Select a template or enter your own claim data
    2. Choose Demo Mode (recommended) to see step-by-step processing
    3. Click "Start Demo" or "Process Claim" to begin
    4. Watch the workflow progress and review results
    """)
