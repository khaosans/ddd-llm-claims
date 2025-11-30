# Visualization Guide

> **⚠️ IMPORTANT**: This is a **DEMONSTRATION SYSTEM** for **EDUCATIONAL PURPOSES ONLY**.  
> **NOT for production use**. See [DISCLAIMERS.md](../DISCLAIMERS.md) for complete information.

## Why Visualizations Matter

Visual representations complement textual documentation by illustrating system structure, data flow, and component relationships. While written descriptions convey concepts, visualizations provide spatial and relational context that enhances comprehension.

In this claims processing system, visualizations facilitate understanding of:

- **System Architecture**: How components are organized and interact across bounded contexts
- **Processing Workflow**: How claims progress from initial submission through final routing
- **Data Flow**: The transformation and movement of data through processing stages
- **Component Relationships**: Communication patterns and dependencies between system elements

These visualizations serve as analytical tools that make complex software architecture accessible to diverse audiences, from students learning Domain-Driven Design (Evans, 2003) to business stakeholders evaluating system capabilities.

---

## System Overview: A Guide for General Audiences

Before examining specific visualizations, it is helpful to understand the overall system structure and processing flow:

1. **Claim Submission**: Customers submit claims through various input channels
2. **Specialized Processing**: Bounded contexts handle domain-specific processing tasks
3. **Event-Driven Communication**: Components communicate through domain events
4. **Decision Points**: Routing and validation decisions occur at multiple stages
5. **Final Routing**: Claims are dispatched to appropriate downstream systems

Each visualization presents different aspects of the system. Architecture diagrams illustrate organizational structure, sequence diagrams document temporal workflows, and interactive visualizations provide real-time exploration capabilities.

---

## Available Visualizations

### 1. Architecture Diagram: System Organization

**Architecture Overview**: The system is organized into three bounded contexts: Claim Intake (Core Domain), Policy Management (Supporting Domain), and Fraud Assessment (Subdomain). The architecture diagram illustrates how these bounded contexts are structured, their internal components, and their communication patterns.

**What You'll See**:
- **Bounded Contexts**: Separate "departments" with clear boundaries (Evans, 2003). Each context has its own rules and responsibilities.
- **Components**: The "employees" and "tools" within each department—agents that process information, repositories that store data, and services that perform work.
- **Data Flow**: How information moves between departments, like memos passed between offices.
- **Domain Events**: Important notifications that trigger actions, like "Facts Extracted" or "Policy Validated" (Vernon, 2013).

**Reading the Diagram**: Start by identifying the three main bounded contexts (colored boxes). Notice how the Claim Intake (Core Domain) is central—this is where the main business value is created. The other contexts support this core work. Follow the arrows to see how information flows, and notice the domain events (purple triangles) that trigger workflow steps.

**Why This Matters**: Understanding the architecture helps you see how the system is organized. Just like understanding a company's org chart helps you know who to contact, understanding the architecture helps you know where functionality lives and how components interact.

**View it**: Open `docs/architecture.md` in any Markdown viewer (GitHub, VS Code, etc.)

---

### 2. Sequence Diagram: Processing Workflow

**Workflow Documentation**: Sequence diagrams document the complete claim processing workflow, illustrating component interactions from initial submission through final routing. They show temporal ordering, message passing, and event-driven coordination.

**What You'll See**:
- **Step-by-step workflow**: Each action in chronological order, from top to bottom
- **Interactions between components**: How agents, repositories, and services communicate
- **Event flow**: When domain events are published and who listens to them
- **Timing of operations**: What happens in sequence and what can happen in parallel

**Reading the Diagram**: Read from top to bottom, following message flow. Each horizontal line (lifeline) represents a component (agent or repository), and vertical arrows indicate messages or actions. The sequence documents the complete workflow: intake → validation → assessment → routing → completion.

**Understanding the Flow**: Notice how domain events trigger the next steps. When the Intake Agent finishes extracting facts, it publishes a `ClaimFactsExtracted` event. This event wakes up the Policy Agent, which then validates the claim. This event-driven approach keeps components loosely coupled (Hohpe & Woolf, 2003)—each component does its job and notifies others when done, rather than directly calling them.

**Why This Matters**: The sequence diagram shows the complete lifecycle of a claim. Understanding this flow helps you see dependencies, identify bottlenecks, and understand what happens when something goes wrong.

**View it**: Open `docs/sequence_diagram.md` in a Mermaid-compatible viewer

---

### 3. Interactive Visualization: See It in Action

**The Story This Visualization Tells**: Watch the system come alive as it processes a real claim. This is like having a live demonstration where you can see each step happen in real-time, with visual feedback showing progress, status changes, and decision points.

**What You'll Experience**:
- **Real-time status updates**: See claims move through workflow stages
- **Workflow progress**: Visual progress bars and step indicators
- **Domain event timeline**: See events as they happen, in chronological order
- **Generated Mermaid diagrams**: Automatically created diagrams showing the current state

**How to Use It**: Run the interactive visualization tool to see the system in action:

```bash
python scripts/visualize.py
```

This will guide you through processing a claim step-by-step, showing you exactly what happens at each stage. You'll see:
- When agents are called
- What data they receive and return
- When domain events are published
- How the workflow progresses

**Interactive Capabilities**: Unlike static diagrams, interactive visualizations enable real-time observation of system behavior. They illustrate timing relationships, reveal processing dependencies, and demonstrate system responses to varying inputs.

**Why It Matters**: Interactive visualizations help bridge the gap between understanding the architecture (the "what") and understanding the behavior (the "how"). They're especially valuable for learning because you can experiment, see cause and effect, and develop intuition about system behavior.

---

### 4. Programmatic Visualization: Custom Views

**Programmatic Visualization**: Programmatic visualization enables creation of custom views tailored to specific analytical needs, such as filtering claims by status or tracking events for specific claims.

**What You Can Do**: Use the `WorkflowVisualizer` class to create custom visualizations:

```python
from src.visualization import WorkflowVisualizer

visualizer = WorkflowVisualizer()

# Record events and claims
visualizer.record_event(event)
visualizer.record_claim(claim)

# Generate visualizations
print(visualizer.visualize_status(claim_id))
print(visualizer.visualize_event_timeline(claim_id))
print(visualizer.visualize_workflow_flow())
```

**Use Cases**:
- **Debugging**: Visualize what happened to a specific claim
- **Learning**: Create custom views to understand specific aspects
- **Documentation**: Generate diagrams for presentations or reports
- **Analysis**: Track patterns across multiple claims

**Why This Matters**: Not every question can be answered with a standard diagram. Programmatic visualization gives you the flexibility to create exactly the view you need, when you need it.

---

## Visualization Types Explained

### Status Visualization: Where Are We Now?

**Status Visualization**: Status visualizations indicate the current processing stage of a claim, providing real-time visibility into workflow progress.

**What It Shows**:
- **Current status**: The claim's current stage (Draft, Facts Extracted, Policy Validated, etc.)
- **Status icon and color**: Visual indicators for quick recognition
- **Claim details**: Key information about the claim
- **Workflow progress bar**: How far through the process we are
- **Step-by-step progress**: Which steps are complete, which are active, which are pending

**Reading It**: Look for the active step (usually highlighted or animated). Completed steps are typically grayed out, and pending steps are shown but not highlighted. The progress bar gives you a quick sense of overall completion.

---

### Event Timeline: Processing History

**Event Timeline**: Event timelines document the chronological sequence of domain events for a claim, providing a complete processing history.

**What It Shows**:
- **Event types**: What happened (ClaimFactsExtracted, PolicyValidated, etc.)
- **Timestamps**: When it happened
- **Flow between events**: How events connect and trigger each other
- **Chronological order**: Events listed from first to last

**Reading Event Timelines**: Read chronologically (top to bottom or left to right, depending on layout). Each event represents a processing milestone. Event dependencies illustrate the event-driven architecture (Hohpe & Woolf, 2003).

**Operational Value**: Event timelines function as audit logs, providing complete processing history. This supports understanding system behavior, debugging issues, and analyzing processing patterns.

---

### Workflow Flow: The Complete Picture

**Workflow Flow Diagrams**: Workflow flow diagrams illustrate all possible processing paths a claim may follow, from initial submission through final routing.

**What It Shows**:
- **All agents and their roles**: Every component that processes the claim
- **Event triggers**: What events cause which actions
- **Decision points**: Where the system makes choices (high risk vs. low risk, valid vs. invalid)
- **Final destinations**: Where claims end up (human review, automated processing, fraud investigation, rejection)

**Reading It**: Follow the arrows from start to finish. Notice the decision points (diamonds or conditional shapes) where the path branches. These represent business logic—the system's decision-making process.

**Understanding Paths**: A claim might take different paths depending on:
- Policy validation results
- Fraud risk scores
- Claim complexity
- Business rules

The workflow flow diagram shows all these possibilities, helping you understand the complete system behavior.

---

### Mermaid Diagrams: The Language of Visualizations

**Mermaid Diagramming**: Mermaid is a text-based diagramming language that enables programmatic visualization creation. It uses declarative syntax to describe system structure and behavior, which Mermaid renders as visual diagrams.

**What You Can Create**:
- **Flowcharts**: Show processes and decision flows
- **Sequence diagrams**: Show interactions over time
- **State diagrams**: Show how states change
- **Architecture diagrams**: Show system structure

**Why Mermaid**: Mermaid diagrams are:
- **Version-controllable**: Stored as text, so they can be tracked in Git
- **Editable**: Easy to modify and update
- **Renderable**: Automatically render on GitHub and many other platforms
- **Accessible**: Can be converted to various formats (PNG, SVG, PDF)

---

## Online Viewers and Tools

### Mermaid Diagrams

Visualizations in this project use Mermaid syntax, which can be viewed in several ways:

1. **GitHub**: Mermaid diagrams render automatically in `.md` files. Just view the file on GitHub and the diagrams appear as interactive visuals.

2. **Mermaid Live Editor**: https://mermaid.live/
   - Paste Mermaid code directly
   - See live preview as you edit
   - Export as PNG or SVG
   - Share diagrams via URL

3. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
   - View diagrams directly in your editor
   - Live preview as you edit
   - Integrated development experience

### Example: Viewing an Architecture Diagram

To view and interact with an architecture diagram:

1. Open `docs/architecture.md` in your preferred viewer
2. Locate the Mermaid code block (starts with ` ```mermaid`)
3. Copy the code between the backticks
4. Go to https://mermaid.live/
5. Paste the code into the editor
6. See the interactive diagram with zoom, pan, and export options

---

## Accessibility and Inclusivity

We've designed our visualizations to be accessible to as many people as possible. Here's what we've considered:

### Visual Accessibility

- **Color Contrast**: Diagrams use high-contrast colors that meet WCAG guidelines
- **Color Independence**: Information isn't conveyed by color alone—shapes and labels also carry meaning
- **Text Alternatives**: All diagrams have descriptive text explanations
- **Scalability**: Diagrams can be zoomed for better visibility

### Navigation

- **Keyboard Navigation**: Interactive visualizations support keyboard navigation
- **Screen Reader Support**: Text descriptions make diagrams accessible to screen readers
- **Clear Structure**: Logical heading hierarchy helps with navigation
- **Table of Contents**: Easy navigation to different sections

### Comprehension

- **Plain Language**: Technical terms are explained when first introduced
- **Analogies**: Real-world comparisons help understand abstract concepts
- **Multiple Formats**: Information available in text, diagrams, and interactive formats
- **Progressive Disclosure**: Start simple, add detail as needed

### Getting Help

If you encounter accessibility barriers:
- Use the text descriptions provided with each diagram
- Request alternative formats if needed
- Check if your viewer supports accessibility features
- Consider using screen reader-friendly text descriptions

---

## Customization

### Adding Custom Visualizations

You can extend the visualization system to create custom views. Here's how:

```python
from src.visualization import WorkflowVisualizer

class CustomVisualizer(WorkflowVisualizer):
    def visualize_custom(self):
        # Your custom visualization code
        # Access self.events and self.claims for data
        pass
```

**When to Customize**: Create custom visualizations when you need:
- Specific views for presentations
- Debugging visualizations
- Learning exercises
- Documentation generation

### Exporting Visualizations

The visualizer outputs text/ASCII art by default. To export in other formats:

1. **PNG/SVG**: Use Mermaid Live Editor to export diagrams
2. **PDF**: Print to PDF from Mermaid Live Editor or browser
3. **Text**: Save output directly to a file
4. **Interactive HTML**: Use the interactive dashboard (`docs/visualization.html`)

---

## Tips for Effective Visualization Use

### For Learning

- **Start with the big picture**: Understand the architecture before diving into details
- **Trace processing workflows**: Use sequence diagrams to analyze complete processing flows
- **Use interactive tools**: See the system in action to develop intuition
- **Compare views**: Look at the same information in different visualizations

### For Understanding

- **Read the narrative**: Don't just look at diagrams—read the explanations
- **Analyze scenarios**: What does this diagram illustrate? What would happen if...?
- **Trace connections**: Follow arrows and relationships to understand dependencies
- **Identify patterns**: Notice recurring structures and understand why they exist

### For Presentation

- **Use the right visualization**: Match the visualization type to your audience
- **Provide context**: Always explain what the diagram shows and why it matters
- **Provide context**: Use visualizations to support documentation, not replace it
- **Make it interactive**: Let your audience explore interactive visualizations

---

## Troubleshooting

### Mermaid Diagrams Not Rendering?

**Problem**: Diagrams appear as code blocks instead of visuals.

**Solutions**:
- Check that the code block is marked as `mermaid` (not `python` or `text`)
- Try viewing on GitHub, which has built-in Mermaid support
- Use Mermaid Live Editor to verify the syntax
- Try copying code directly (without markdown code fences) into Mermaid Live Editor

### Visualization Script Errors?

**Problem**: The `visualize.py` script doesn't run or shows errors.

**Solutions**:
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that Ollama is running (if using local models): `ollama serve`
- Use mock providers for testing without LLM (the script should detect this automatically)
- Verify Python version is 3.10 or higher: `python --version`

### Diagrams Too Complex?

**Problem**: Diagrams are overwhelming or hard to understand.

**Solutions**:
- **Break into smaller diagrams**: Focus on one bounded context at a time
- **Use subgraphs**: Mermaid subgraphs help organize complex diagrams
- **Read the narrative**: Text explanations help make sense of complex visuals
- **Start simple**: Begin with high-level architecture, then dive into details
- **Use interactive tools**: Interactive visualizations let you explore complexity gradually

### Need Help Understanding a Diagram?

**Problem**: You can see the diagram but don't understand what it means.

**Solutions**:
- Read the narrative sections in this guide
- Check the "Reading the Diagram" sections for step-by-step guidance
- Review the architecture documentation for detailed explanations
- Use the interactive dashboard for guided exploration
- Consult the REFERENCES.md for background on DDD concepts

---

## Key Takeaways

1. **Visualizations tell stories**: Each diagram tells part of the system's story—understand the narrative to understand the system.

2. **Start with the big picture**: Architecture diagrams show organization; sequence diagrams show flow; interactive tools show behavior.

3. **Multiple views reveal different insights**: The same system looks different in different visualizations—use multiple views to build complete understanding.

4. **Accessibility matters**: We've designed visualizations to be accessible—use text descriptions, keyboard navigation, and multiple formats.

5. **Visualizations are learning tools**: Don't just look—explore, question, and experiment to develop deep understanding.

---

## References

All concepts and patterns referenced in this guide are grounded in established research:

- **Domain-Driven Design**: Evans, E. (2003). *Domain-driven design: Tackling complexity in the heart of software*. Addison-Wesley Professional.
- **Domain Events**: Vernon, V. (2013). *Implementing domain-driven design*. Addison-Wesley Professional.
- **Event-Driven Architecture**: Hohpe, G., & Woolf, B. (2003). *Enterprise integration patterns: Designing, building, and deploying messaging solutions*. Addison-Wesley Professional.

For complete citations and references, see [docs/REFERENCES.md](REFERENCES.md).

---

**Remember**: This is an **educational demonstration system**. Visualizations help us understand and learn, but the real system would require production-grade features. See [DISCLAIMERS.md](../DISCLAIMERS.md) for important limitations.
