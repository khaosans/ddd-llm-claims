"""
Decision Status Helper

Provides visual status indicators for decisions based on both
technical success and business outcome.
"""

from typing import Dict, Any, Tuple


def get_decision_status(step: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Determine visual status for a decision step.
    
    Returns status based on:
    - Technical success (did the step execute without errors?)
    - Business outcome (was the decision positive or negative?)
    
    Args:
        step: Step dictionary with decision information
    
    Returns:
        Tuple of (status_emoji, status_text, status_color)
        - status_emoji: Emoji indicator (✅, ⚠️, ❌, etc.)
        - status_text: Human-readable status text
        - status_color: Color indicator (green, yellow, red)
    """
    success = step.get("success", False)
    decision_type = step.get("decision_type", "")
    decision_value = step.get("decision", "")
    decision_raw = step.get("decision_value")  # Raw value if available
    
    # If step failed technically, it's an error
    if not success:
        return ("❌", "Failed", "red")
    
    # Check decision outcome based on decision type and value
    # Policy Validation
    if decision_type == "policy_validation":
        if isinstance(decision_raw, dict):
            is_valid = decision_raw.get("is_valid", True)
            if not is_valid:
                return ("⚠️", "Policy Invalid", "orange")
        elif "Policy valid: False" in str(decision_value) or "invalid" in str(decision_value).lower():
            return ("⚠️", "Policy Invalid", "orange")
        return ("✅", "Policy Valid", "green")
    
    # Fraud Assessment
    if decision_type == "fraud_assessment":
        if isinstance(decision_raw, dict):
            fraud_score = decision_raw.get("fraud_score", 0.0)
            is_suspicious = decision_raw.get("is_suspicious", False)
            risk_level = decision_raw.get("risk_level", "low")
            
            if fraud_score >= 0.7 or risk_level in ["high", "critical"] or is_suspicious:
                return ("🚩", "High Fraud Risk", "red")
            elif fraud_score >= 0.4 or risk_level == "medium":
                return ("⚠️", "Medium Fraud Risk", "orange")
        elif any(keyword in str(decision_value).lower() for keyword in ["high", "suspicious", "fraud"]):
            return ("⚠️", "Fraud Risk Detected", "orange")
        return ("✅", "Low Fraud Risk", "green")
    
    # Document Validation
    if decision_type == "document_validation":
        if isinstance(decision_raw, dict):
            is_compliant = decision_raw.get("is_compliant", True)
            if not is_compliant:
                return ("⚠️", "Non-Compliant", "orange")
        elif "non-compliant" in str(decision_value).lower() or "missing" in str(decision_value).lower():
            return ("⚠️", "Non-Compliant", "orange")
        return ("✅", "Compliant", "green")
    
    # Document Authenticity
    if decision_type == "document_authenticity_check":
        if isinstance(decision_raw, dict):
            is_suspicious = decision_raw.get("is_suspicious", False)
            authenticity_score = decision_raw.get("authenticity_score", 1.0)
            if is_suspicious or authenticity_score < 0.7:
                return ("⚠️", "Suspicious Document", "orange")
        elif "suspicious" in str(decision_value).lower():
            return ("⚠️", "Suspicious Document", "orange")
        return ("✅", "Authentic", "green")
    
    # Triage/Routing
    if decision_type == "triage_routing":
        if isinstance(decision_raw, dict):
            routing = decision_raw.get("routing_decision", "")
            if routing in ["fraud_investigation", "rejection", "rejected"]:
                return ("⚠️", "Routed to Investigation", "orange")
        elif any(keyword in str(decision_value).lower() for keyword in ["fraud", "reject", "investigation"]):
            return ("⚠️", "Requires Review", "orange")
        return ("✅", "Routed", "green")
    
    # Workflow Step
    if decision_type == "workflow_step":
        if isinstance(decision_raw, dict):
            action = decision_raw.get("action", "")
            if action in ["rejection", "rejected", "error"]:
                return ("⚠️", "Workflow Issue", "orange")
        return ("✅", "Completed", "green")
    
    # Default: step succeeded technically
    return ("✅", "Success", "green")


def get_status_badge_html(status_emoji: str, status_text: str, status_color: str) -> str:
    """
    Generate HTML for a status badge.
    
    Args:
        status_emoji: Emoji indicator
        status_text: Status text
        status_color: Color (green, orange, red)
    
    Returns:
        HTML string for badge
    """
    color_map = {
        "green": "#28a745",
        "orange": "#ff9800",
        "red": "#dc3545",
    }
    
    bg_color = color_map.get(status_color, "#6c757d")
    
    return f"""
    <span style="
        background-color: {bg_color};
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.85em;
        font-weight: bold;
        margin-left: 8px;
    ">{status_emoji} {status_text}</span>
    """


def analyze_decision_outcome(step: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze decision outcome and return detailed status information.
    
    Args:
        step: Step dictionary
    
    Returns:
        Dict with status analysis including:
        - visual_status: Tuple of (emoji, text, color)
        - has_warning: Boolean indicating if warning should be shown
        - warning_message: Optional warning message
        - outcome_type: Type of outcome (success, warning, error)
    """
    success = step.get("success", False)
    decision_type = step.get("decision_type", "")
    decision_value = step.get("decision", "")
    decision_raw = step.get("decision_value")
    
    visual_status = get_decision_status(step)
    status_emoji, status_text, status_color = visual_status
    
    has_warning = False
    warning_message = None
    outcome_type = "success"
    
    # Determine if there's a warning condition
    if not success:
        outcome_type = "error"
        warning_message = step.get("error", "Step failed to execute")
    elif status_color == "orange":
        outcome_type = "warning"
        has_warning = True
        # Generate specific warning message
        if decision_type == "policy_validation":
            warning_message = "Policy validation failed - claim may be rejected"
        elif decision_type == "fraud_assessment":
            warning_message = "Fraud risk detected - requires review"
        elif decision_type == "document_validation":
            warning_message = "Document compliance issues - missing required documents"
        elif decision_type == "document_authenticity_check":
            warning_message = "Document authenticity concerns - possible tampering"
        else:
            warning_message = f"{status_text} - requires attention"
    elif status_color == "red":
        outcome_type = "error"
        has_warning = True
        warning_message = "Critical issue detected - immediate review required"
    
    return {
        "visual_status": visual_status,
        "has_warning": has_warning,
        "warning_message": warning_message,
        "outcome_type": outcome_type,
        "status_emoji": status_emoji,
        "status_text": status_text,
        "status_color": status_color,
    }

