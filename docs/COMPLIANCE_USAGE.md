# Compliance and Decision Viewing Usage Guide

This guide explains how to use the compliance framework to view decisions, get summaries, and perform audits.

## Quick Start

### View Current Decisions During Processing

```python
from src.compliance.workflow_integration import view_current_decisions
from uuid import UUID

# Get current status and decisions for a claim
claim_id = UUID("your-claim-id")
status = view_current_decisions(claim_id)

print(f"Current step: {status['progress']['current_step']}")
print(f"Decisions made: {status['progress']['total_decisions']}")
print(f"Has issues: {status['has_issues']}")
```

### Get Quick Audit Summary

```python
from src.compliance.workflow_integration import get_audit_summary

# Get audit summary with findings and guidance
audit = get_audit_summary(claim_id)

print(f"Requires review: {audit['requires_review']}")
print(f"Key decisions: {len(audit['summary']['key_decisions'])}")
print(f"Issues found: {len(audit['summary']['issues'])}")
print(f"Recommendations: {len(audit['summary']['recommendations'])}")
```

### Get Completion Summary

```python
from src.compliance.workflow_integration import get_completion_summary

# Get comprehensive completion summary
summary = get_completion_summary(claim_id)

print(f"Executive Summary: {summary['executive_summary']}")
print(f"Findings: {summary['findings']}")
print(f"Recommendations: {summary['recommendations']}")
print(f"Audit Guidance: {summary['audit_guidance']}")
```

## Using the Decision Monitor

### Get Workflow Progress

```python
from src.compliance.workflow_integration import get_decision_monitor

monitor = get_decision_monitor()

# Get current status
status = monitor.get_current_status(claim_id)
print(f"Status: {status['progress']['status']}")
print(f"Current step: {status['progress']['current_step']}")
print(f"Next steps: {status['progress']['next_steps']}")
```

### View Step-by-Step Decisions

```python
# Get all steps view
steps_view = monitor.get_all_steps_view(claim_id)

for step in steps_view['steps']:
    print(f"Step {step['step_number']}: {step['step_name']}")
    print(f"  Agent: {step['agent']}")
    print(f"  Decision: {step['decision']}")
    print(f"  Status: {'Success' if step['success'] else 'Failed'}")
    print(f"  Reasoning: {step['reasoning']}")
```

### Get Decisions for Specific Step

```python
# Get decisions for a specific step
step_decisions = monitor.get_step_decisions(claim_id, step_name="policy_validation")

for decision in step_decisions['decisions']:
    print(f"Decision: {decision['decision']}")
    print(f"Reasoning: {decision['reasoning']}")
```

## Using in UI (Streamlit)

### Display Decision Status

```python
import streamlit as st
from src.ui.services import get_service

service = get_service()

# Get decision status
claim_id = st.session_state.get('current_claim_id')
if claim_id:
    status = await service.get_decision_status(claim_id)
    
    st.subheader("Current Workflow Status")
    st.write(f"Status: {status['progress']['status']}")
    st.write(f"Current Step: {status['progress']['current_step']}")
    st.write(f"Total Decisions: {status['progress']['total_decisions']}")
    
    if status['has_issues']:
        st.warning("⚠️ Issues detected - review required")
```

### Display Audit Summary

```python
# Get audit summary
audit = await service.get_audit_summary(claim_id)

st.subheader("Quick Audit Summary")
st.write(f"Requires Review: {audit['requires_review']}")

if audit['summary']['issues']:
    st.error("Issues Found:")
    for issue in audit['summary']['issues']:
        st.write(f"- {issue['step']}: {issue['error']}")

if audit['summary']['recommendations']:
    st.info("Recommendations:")
    for rec in audit['summary']['recommendations']:
        st.write(f"- {rec['message']}")
```

### Display Completion Summary

```python
# Get completion summary
summary = await service.get_completion_summary(claim_id)

st.subheader("Completion Summary")

# Executive Summary
st.write("**Executive Summary**")
st.json(summary['executive_summary'])

# Findings
if summary['findings']:
    st.write("**Findings**")
    for finding in summary['findings']:
        severity_color = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
        }.get(finding['severity'], "⚪")
        st.write(f"{severity_color} {finding['finding']}")

# Recommendations
if summary['recommendations']:
    st.write("**Recommendations**")
    for rec in summary['recommendations']:
        st.write(f"**{rec['priority'].upper()}**: {rec['recommendation']}")
        for action in rec.get('action_items', []):
            st.write(f"  - {action}")
```

## Using Decision Viewer Directly

### Get Workflow Progress

```python
from src.compliance.decision_viewer import DecisionViewer

viewer = DecisionViewer()

# Get workflow progress
progress = viewer.get_workflow_progress(claim_id)

print(f"Status: {progress['status']}")
print(f"Steps completed: {progress['steps_completed']}")
print(f"Next steps: {progress['next_steps']}")
```

### Get Audit Guidance

```python
# Get audit guidance
guidance = viewer.get_audit_guidance(claim_id)

print(f"Review required: {guidance['audit_summary']['review_required']}")
print(f"Red flags: {guidance['audit_summary']['red_flags_count']}")

if guidance['red_flags']:
    print("Red Flags:")
    for flag in guidance['red_flags']:
        print(f"  - {flag['issue']}")
        print(f"    Action: {flag['action_required']}")
```

## Integration Examples

### During Workflow Execution

```python
from src.compliance.workflow_integration import get_decision_monitor

# In your workflow code, after each step:
monitor = get_decision_monitor()

# Check current status
status = monitor.get_current_status(claim_id)

# If issues detected, log or alert
if status['has_issues']:
    audit = monitor.get_audit_summary(claim_id)
    logger.warning(f"Issues detected: {audit['summary']['issues']}")
```

### After Workflow Completion

```python
# After workflow completes
summary = monitor.get_completion_summary(claim_id)

# Log completion summary
logger.info(f"Workflow completed: {summary['executive_summary']['overall_status']}")

# Check if review needed
if summary['executive_summary']['requires_review']:
    logger.warning("Human review required")
    # Send notification or add to review queue
```

## Key Features

### Real-time Decision Viewing
- View decisions as they're made during workflow execution
- Monitor workflow progress step-by-step
- Get current step decisions

### Quick Audit Capabilities
- Quick audit summaries for human reviewers
- Findings and issues identification
- Recommendations and guidance
- Red flags detection

### Completion Summaries
- Executive summaries
- Detailed findings
- Actionable recommendations
- Audit guidance
- Decision explanations

### Human-Friendly Formatting
- Step-by-step views
- Timeline visualization
- Clear status indicators
- Guidance and recommendations
- Review checklists

## Best Practices

1. **During Processing**: Use `get_current_status()` to monitor progress
2. **For Quick Review**: Use `get_audit_summary()` for fast human review
3. **After Completion**: Use `get_completion_summary()` for comprehensive analysis
4. **For Debugging**: Use `get_all_steps_view()` to see complete decision flow
5. **For Auditing**: Use `get_audit_guidance()` for structured audit review

## API Reference

See the module docstrings for detailed API documentation:
- `src.compliance.workflow_integration`
- `src.compliance.decision_viewer`
- `src.compliance.completion_summary`
- `src.compliance.decision_audit`


