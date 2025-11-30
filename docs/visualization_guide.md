# Visualization Guide

> **⚠️ IMPORTANT**: This is a **DEMONSTRATION SYSTEM** for **EDUCATIONAL PURPOSES ONLY**.  
> **NOT for production use**. See [DISCLAIMERS.md](../DISCLAIMERS.md) for complete information.

## Why Visualizations Matter

Imagine trying to understand how a complex organization works by reading only written descriptions. You might grasp the concepts, but seeing how departments connect, how information flows, and how decisions are made would be much clearer with a visual map. That's exactly what visualizations do for software systems.

In this claims processing system, visualizations help us understand:

- **The Big Picture**: How different parts of the system work together, like departments in a company
- **The Journey**: How a claim travels from a customer's email to final processing
- **The Flow**: What happens at each step and why
- **The Relationships**: How components communicate and depend on each other

These visualizations aren't just pretty pictures—they're storytelling tools that make complex software architecture accessible to everyone, from students learning Domain-Driven Design (Evans, 2003) to business stakeholders understanding system capabilities.

---

## Understanding the Story: A Guide for General Audiences

Before diving into specific visualizations, let's understand what story they're telling. Think of this system like a well-organized office:

1. **A customer sends in a claim** (like dropping off paperwork)
2. **Specialized departments process it** (like different office departments)
3. **Information flows between departments** (like inter-office memos)
4. **Decisions are made at each step** (like approvals and routing)
5. **The claim reaches its final destination** (like filing or further processing)

Each visualization tells a different part of this story. Some show the organizational structure (architecture diagrams), others show the step-by-step process (sequence diagrams), and some show real-time progress (interactive visualizations).

---

## Available Visualizations

### 1. Architecture Diagram: The Organizational Map

**The Story This Diagram Tells**: Imagine a company with three main departments—one that handles the core business (Claim Intake), one that provides supporting services (Policy Management), and one that specializes in risk assessment (Fraud Assessment). The architecture diagram shows how these departments are organized, what they contain, and how they communicate.

**What You'll See**:
- **Bounded Contexts**: Separate "departments" with clear boundaries (Evans, 2003). Each context has its own rules and responsibilities.
- **Components**: The "employees" and "tools" within each department—agents that process information, repositories that store data, and services that perform work.
- **Data Flow**: How information moves between departments, like memos passed between offices.
- **Domain Events**: Important notifications that trigger actions, like "Facts Extracted" or "Policy Validated" (Vernon, 2013).

**Reading the Diagram**: Start by identifying the three main bounded contexts (colored boxes). Notice how the Claim Intake (Core Domain) is central—this is where the main business value is created. The other contexts support this core work. Follow the arrows to see how information flows, and notice the domain events (purple triangles) that trigger workflow steps.

**Why This Matters**: Understanding the architecture helps you see how the system is organized. Just like understanding a company's org chart helps you know who to contact, understanding the architecture helps you know where functionality lives and how components interact.

**View it**: Open `docs/architecture.md` in any Markdown viewer (GitHub, VS Code, etc.)

---

### 2. Sequence Diagram: The Step-by-Step Journey

**The Story This Diagram Tells**: Follow a single claim as it travels through the system, from the moment a customer submits it until it reaches its final destination. This is like watching a package move through a shipping facility—you see each stop, each person who handles it, and what happens at each stage.

**What You'll See**:
- **Step-by-step workflow**: Each action in chronological order, from top to bottom
- **Interactions between components**: How agents, repositories, and services communicate
- **Event flow**: When domain events are published and who listens to them
- **Timing of operations**: What happens in sequence and what can happen in parallel

**Reading the Diagram**: Read from top to bottom, following the arrows. Each horizontal line represents a component (like an agent or repository), and vertical arrows show messages or actions. The sequence shows the complete journey: intake → validation → assessment → routing → completion.

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

**The Experience**: Unlike static diagrams, this interactive visualization lets you see the system's behavior. It's the difference between looking at a map and actually taking the journey. You'll see timing, understand dependencies, and get a feel for how the system responds to different inputs.

**Why It Matters**: Interactive visualizations help bridge the gap between understanding the architecture (the "what") and understanding the behavior (the "how"). They're especially valuable for learning because you can experiment, see cause and effect, and develop intuition about system behavior.

---

### 4. Programmatic Visualization: Custom Views

**The Story This Tells**: Sometimes you need a specific view of the system—maybe you want to see all claims in a certain status, or track events for a specific claim. Programmatic visualization lets you create custom views tailored to your needs.

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

**The Story**: Like a progress bar on a download, status visualizations show where a claim is in its journey. They answer the question "What's happening right now?"

**What It Shows**:
- **Current status**: The claim's current stage (Draft, Facts Extracted, Policy Validated, etc.)
- **Status icon and color**: Visual indicators for quick recognition
- **Claim details**: Key information about the claim
- **Workflow progress bar**: How far through the process we are
- **Step-by-step progress**: Which steps are complete, which are active, which are pending

**Reading It**: Look for the active step (usually highlighted or animated). Completed steps are typically grayed out, and pending steps are shown but not highlighted. The progress bar gives you a quick sense of overall completion.

---

### Event Timeline: The Story of What Happened

**The Story**: Like a timeline in a history book, event timelines show what happened and when. They tell the complete story of a claim's journey through the system.

**What It Shows**:
- **Event types**: What happened (ClaimFactsExtracted, PolicyValidated, etc.)
- **Timestamps**: When it happened
- **Flow between events**: How events connect and trigger each other
- **Chronological order**: Events listed from first to last

**Reading It**: Read from top to bottom (or left to right, depending on layout). Each event represents a milestone in the claim's journey. Notice how some events trigger others—this shows the event-driven nature of the system (Hohpe & Woolf, 2003).

**Why It Matters**: Event timelines are like audit logs—they show the complete history. This is valuable for understanding what happened, debugging issues, and learning how the system behaves.

---

### Workflow Flow: The Complete Picture

**The Story**: Like a flowchart showing a business process, workflow flow diagrams show all possible paths a claim can take, from start to finish.

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

**The Story**: Mermaid is a text-based diagramming language that lets us create visualizations using code. Think of it like writing a screenplay—you describe what should happen, and Mermaid creates the visual representation.

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
- **Follow a claim's journey**: Use sequence diagrams to trace a complete flow
- **Use interactive tools**: See the system in action to develop intuition
- **Compare views**: Look at the same information in different visualizations

### For Understanding

- **Read the narrative**: Don't just look at diagrams—read the explanations
- **Ask questions**: What story is this diagram telling? What would happen if...?
- **Trace connections**: Follow arrows and relationships to understand dependencies
- **Identify patterns**: Notice recurring structures and understand why they exist

### For Presentation

- **Use the right visualization**: Match the visualization type to your audience
- **Provide context**: Always explain what the diagram shows and why it matters
- **Tell the story**: Use visualizations to support a narrative, not replace it
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
