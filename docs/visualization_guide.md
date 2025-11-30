# Visualization Guide

This guide explains how to visualize the claims processing system.

## Available Visualizations

### 1. Architecture Diagram

The main architecture diagram is in `docs/architecture.md`. It shows:
- Bounded contexts
- Components and their relationships
- Data flow
- Domain events

**View it**: Open `docs/architecture.md` in any Markdown viewer (GitHub, VS Code, etc.)

### 2. Sequence Diagram

The sequence diagram in `docs/sequence_diagram.md` shows:
- Step-by-step workflow
- Interactions between components
- Event flow
- Timing of operations

**View it**: Open `docs/sequence_diagram.md` in a Mermaid-compatible viewer

### 3. Interactive Visualization

Run the interactive visualization tool to see the system in action:

```bash
python visualize.py
```

This will:
- Show real-time status updates
- Display workflow progress
- Show domain event timeline
- Generate Mermaid diagrams

### 4. Programmatic Visualization

Use the `WorkflowVisualizer` class in your code:

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

## Online Viewers

### Mermaid Diagrams

1. **GitHub**: Mermaid diagrams render automatically in `.md` files
2. **Mermaid Live Editor**: https://mermaid.live/
   - Paste Mermaid code
   - See live preview
   - Export as PNG/SVG

3. **VS Code**: Install "Markdown Preview Mermaid Support" extension

### Example: Viewing Architecture Diagram

1. Open `docs/architecture.md`
2. Copy the Mermaid code block
3. Go to https://mermaid.live/
4. Paste the code
5. See the interactive diagram

## Visualization Types

### Status Visualization

Shows the current status of a claim with:
- Current status icon and color
- Claim details
- Workflow progress bar
- Step-by-step progress

### Event Timeline

Shows domain events in chronological order:
- Event types
- Timestamps
- Flow between events

### Workflow Flow

Shows the complete workflow as a flowchart:
- All agents and their roles
- Event triggers
- Decision points
- Final destinations

### Mermaid Diagrams

Generate code for:
- Flowcharts
- Sequence diagrams
- State diagrams
- Architecture diagrams

## Customization

### Adding Custom Visualizations

Extend `WorkflowVisualizer` to add custom visualizations:

```python
class CustomVisualizer(WorkflowVisualizer):
    def visualize_custom(self):
        # Your custom visualization code
        pass
```

### Exporting Visualizations

The visualizer outputs text/ASCII art. To export:

1. **PNG/SVG**: Use Mermaid Live Editor
2. **PDF**: Print to PDF from Mermaid Live Editor
3. **Text**: Save output to file

## Tips

- Run `visualize.py` to see real-time processing
- Use Mermaid Live Editor for interactive diagrams
- GitHub automatically renders Mermaid in markdown files
- VS Code with Mermaid extension provides live preview

## Troubleshooting

### Mermaid not rendering?
- Check syntax in Mermaid Live Editor
- Ensure code block is marked as `mermaid`
- Try copying code directly (without markdown code fences)

### Visualization script errors?
- Ensure all dependencies are installed
- Check that Ollama is running (if using local models)
- Use mock providers for testing without LLM

### Diagrams too complex?
- Break into smaller diagrams
- Focus on one bounded context at a time
- Use subgraphs in Mermaid

