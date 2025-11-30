# Demo Workflow Guide

## 🎬 Interactive Demo Mode

The Demo Mode provides an educational, step-by-step workflow that processes claims slowly so you can see each stage of the system.

## Features

### ✅ Step-by-Step Processing
- **Visual Progress**: Real-time progress bar showing workflow completion
- **Step Details**: Each step is clearly labeled and explained
- **Status Updates**: Live status messages for each workflow stage
- **Configurable Speed**: Adjust step delay from 0.5 to 5 seconds

### ✅ Human-in-the-Loop Prompts
- **Automatic Detection**: System detects when human review is needed
- **Clear Prompts**: Review requirements are clearly explained
- **Decision Options**: Approve, Reject, or Override buttons
- **Feedback Collection**: Optional feedback field for review decisions

### ✅ Educational Visualization
- **Workflow Steps**: See all completed steps in real-time
- **Current Step**: Highlighted current processing step
- **Progress Tracking**: Visual progress bar (0-100%)
- **Result Summary**: Complete results after processing

## How to Use

### 1. Access Demo Mode
- Open the Streamlit dashboard
- Click "🎬 Demo Mode" in the sidebar

### 2. Select Template
Choose from available templates:
- 🚗 **Auto Insurance** - Standard car accident claim
- 💰 **High Value** - Large claim (triggers review)
- 📝 **Simple Claim** - Quick low-value claim
- 🏠 **Property** - Property damage claim

Or enter your own claim data.

### 3. Configure Settings
- **Step Delay**: Control how fast steps process (slower = more educational)
- **Auto-advance**: Automatically proceed through steps

### 4. Start Demo
- Click "🎬 Start Demo" button
- Watch the workflow progress step-by-step
- See each agent's work in real-time

### 5. Review Decisions
When human review is required:
- Review the claim details
- Make a decision (Approve/Reject/Override)
- Add optional feedback
- Submit your decision

## Workflow Steps

The demo shows these steps:

1. **Initialization** (0-5%)
   - System setup and preparation

2. **Fact Extraction** (5-35%)
   - 🤖 Intake Agent extracts structured facts
   - Converts unstructured input to structured data
   - Validates against domain model

3. **Policy Validation** (35-65%)
   - 🔍 Policy Agent validates coverage
   - Checks policy status and limits
   - Verifies claim eligibility

4. **Fraud Assessment** (65-85%)
   - 🚩 Fraud assessment analyzes patterns
   - Calculates risk score
   - Identifies suspicious indicators

5. **Triage & Routing** (85-100%)
   - 🎯 Triage Agent determines routing
   - Decides next steps
   - Routes to appropriate queue

6. **Human Review** (if needed)
   - ⚠️ Prompts for human decision
   - Shows review reason
   - Collects decision and feedback

## Demo Scenarios

### Quick Demo (2-3 minutes)
1. Select "Simple Claim" template
2. Set step delay to 1 second
3. Start demo
4. Watch complete workflow

### Full Demo (5-7 minutes)
1. Select "High Value" template
2. Set step delay to 1.5-2 seconds
3. Start demo
4. Watch workflow + human review prompt
5. Make review decision

### Educational Demo (10+ minutes)
1. Select any template
2. Set step delay to 3-5 seconds
3. Read each step carefully
4. Understand each agent's role
5. Make informed review decisions

## Best Practices

### For Presentations
- Use "High Value" template to show review workflow
- Set delay to 2-3 seconds for audience comprehension
- Pause at review step to explain human-in-the-loop

### For Training
- Use different templates to show variety
- Set delay to 3-5 seconds for learning
- Explain each step as it processes
- Discuss review decisions

### For Quick Tests
- Use "Simple Claim" template
- Set delay to 0.5-1 second
- Fast iteration for testing

## Tips

1. **Start Slow**: Begin with longer delays to understand workflow
2. **Watch Progress**: Pay attention to progress bar and status messages
3. **Read Steps**: Each step explains what's happening
4. **Review Carefully**: When prompted, review all claim details
5. **Try Different Templates**: See how different claims are processed

## Troubleshooting

### Demo Not Starting
- Ensure claim data is entered
- Check that template is loaded
- Verify model provider is selected

### Steps Too Fast/Slow
- Adjust "Step Delay" slider in settings
- Recommended: 1.5-2 seconds for demos

### Review Not Prompting
- Use "High Value" template (guaranteed to trigger review)
- Check claim amount is above threshold
- Verify review queue is working

## Technical Details

### Processing Flow
1. Demo mode calls service layer
2. Service initializes orchestrator
3. Orchestrator processes claim through agents
4. Demo mode shows progress at each step
5. Review prompts appear when needed

### Step Delays
- Configurable per demo
- Applied between workflow steps
- Allows users to read and understand
- Makes workflow educational

### Review Detection
- System checks review queue after triage
- If claim requires review, prompts user
- User makes decision
- Decision is recorded (demo mode)

## Next Steps

After completing a demo:
1. View results in "Claims List"
2. Check "Review Queue" for pending items
3. View "Analytics" for statistics
4. Try different templates
5. Experiment with different settings

## See Also

- `DATA_TEMPLATES.md` - All available templates
- `TEMPLATES_QUICK_REFERENCE.md` - Quick template guide
- `UI_INTEGRATION.md` - UI integration details

