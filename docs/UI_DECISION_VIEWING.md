# UI Decision Viewing Features

This document describes how decision viewing is integrated into the Streamlit UI.

## Overview

The UI now provides comprehensive decision viewing capabilities:
- **Real-time decision viewing** during processing
- **Step-by-step decision details** in final output
- **Quick audit summaries** for human review
- **Completion summaries** with findings and recommendations

## Features by Page

### Process Claim Page (`pages/process_claim.py`)

#### During Processing (Demo Mode)
- **Real-time Decision Display**: Shows decisions as they're made during workflow execution
- **Step-by-step Updates**: Decisions appear in expandable sections as each step completes
- **Decision Details**: Each decision shows:
  - Agent/component that made it
  - Decision value
  - Reasoning
  - Success/failure status

#### Final Output (Results Section)
Four tabs provide comprehensive decision viewing:

1. **📋 Extracted Facts Tab**
   - Shows extracted claim facts
   - Workflow steps summary

2. **🔍 Decisions Tab**
   - Complete step-by-step view of all decisions
   - Each step shows:
     - Step number and name
     - Agent/component
     - Decision type
     - Decision value
     - Reasoning
     - Success/failure status
     - Error messages (if failed)
     - Dependencies
   - Expandable sections for easy navigation

3. **📊 Audit Summary Tab**
   - Quick audit overview with metrics:
     - Total decisions
     - Successful vs failed
     - Success rate
     - Overall status
   - Key decisions summary
   - Issues found (if any)
   - Recommendations
   - Audit guidance with:
     - Red flags
     - Review checklist

4. **📈 Completion Summary Tab**
   - Executive summary with key metrics
   - Detailed findings with severity levels
   - Prioritized recommendations with action items
   - Audit guidance

### Claims List Page (`pages/claims_list.py`)

When viewing claim details, three tabs are available:

1. **📋 Claim Details Tab**
   - Standard claim information

2. **🔍 Decisions Tab**
   - Step-by-step decision view
   - Same format as Process Claim page

3. **📊 Audit Tab**
   - Quick audit summary
   - Issues and recommendations

## Visual Features

### Status Indicators
- ✅ Success indicators (green)
- ❌ Failure indicators (red)
- ⏳ In-progress indicators
- ⚠️ Warning indicators

### Color Coding
- **Healthy**: Green (✅)
- **Needs Review**: Yellow (⚠️)
- **Critical**: Red (🔴)

### Expandable Sections
- Decisions organized in expandable sections
- Easy to navigate through many decisions
- Collapsed by default to reduce clutter

## Usage Examples

### Viewing Decisions During Processing

1. Start processing a claim in Demo Mode
2. Watch the "Decisions Made So Far" section update in real-time
3. Expand any step to see decision details

### Viewing Final Decision Summary

1. After processing completes, navigate to the Results section
2. Click on the "🔍 Decisions" tab
3. Expand any step to see full decision details
4. Review reasoning, context, and dependencies

### Quick Audit Review

1. After processing, go to "📊 Audit Summary" tab
2. Review the overview metrics
3. Check for issues and recommendations
4. Use the review checklist for systematic review

### Completion Analysis

1. Go to "📈 Completion Summary" tab
2. Review executive summary
3. Check findings (sorted by severity)
4. Review recommendations with action items

## Integration Points

### Service Layer (`src/ui/services.py`)

New methods added:
- `get_decision_status()` - Current decision status
- `get_step_decisions()` - Decisions for specific step
- `get_all_steps_view()` - Complete step-by-step view
- `get_audit_summary()` - Quick audit summary
- `get_completion_summary()` - Full completion summary

### Demo Workflow (`src/ui/demo_workflow.py`)

Enhanced to include:
- Decision status in result dictionary
- Real-time decision updates during processing

## Technical Details

### Error Handling
- Graceful degradation if decision viewing unavailable
- Error messages shown to user
- Fallback to basic display if needed

### Performance
- Decisions loaded on-demand
- Lazy loading for large decision sets
- Efficient querying of decision data

### Data Flow
1. Agents make decisions → Captured by DecisionAuditService
2. UI requests decision data → Via UIService methods
3. DecisionMonitor provides formatted views
4. UI displays in user-friendly format

## Future Enhancements

Potential improvements:
- Real-time WebSocket updates for live decision viewing
- Decision comparison tools
- Decision filtering and search
- Export decision reports
- Decision visualization graphs
- Timeline visualization



