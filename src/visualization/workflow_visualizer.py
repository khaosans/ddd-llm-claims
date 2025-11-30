"""
Workflow Visualizer - Visual representation of claim processing

This module provides visualization capabilities for the claims processing workflow.
It can generate diagrams, show real-time progress, and visualize domain events.
"""

from typing import List, Optional
from datetime import datetime
from uuid import UUID

from ..domain.claim import Claim, ClaimStatus
from ..domain.events import DomainEvent


class WorkflowVisualizer:
    """
    Visualizes the claim processing workflow.
    
    Can generate:
    - Status diagrams
    - Event timelines
    - Process flow charts
    - Real-time progress indicators
    """
    
    def __init__(self):
        self.events: List[DomainEvent] = []
        self.claims: dict[UUID, Claim] = {}
    
    def record_event(self, event: DomainEvent) -> None:
        """Record a domain event for visualization"""
        self.events.append(event)
    
    def record_claim(self, claim: Claim) -> None:
        """Record a claim for visualization"""
        self.claims[claim.claim_id] = claim
    
    def visualize_status(self, claim_id: UUID) -> str:
        """
        Generate a text-based status visualization for a claim.
        
        Returns:
            ASCII art representation of claim status
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return f"Claim {claim_id} not found"
        
        status_icons = {
            ClaimStatus.DRAFT: "📝",
            ClaimStatus.FACTS_EXTRACTED: "✅",
            ClaimStatus.POLICY_VALIDATED: "🔍",
            ClaimStatus.TRIAGED: "🎯",
            ClaimStatus.PROCESSING: "⚙️",
            ClaimStatus.COMPLETED: "✨",
            ClaimStatus.REJECTED: "❌",
        }
        
        status_colors = {
            ClaimStatus.DRAFT: "\033[93m",  # Yellow
            ClaimStatus.FACTS_EXTRACTED: "\033[94m",  # Blue
            ClaimStatus.POLICY_VALIDATED: "\033[96m",  # Cyan
            ClaimStatus.TRIAGED: "\033[92m",  # Green
            ClaimStatus.PROCESSING: "\033[95m",  # Magenta
            ClaimStatus.COMPLETED: "\033[92m",  # Green
            ClaimStatus.REJECTED: "\033[91m",  # Red
        }
        reset = "\033[0m"
        
        icon = status_icons.get(claim.status, "❓")
        color = status_colors.get(claim.status, "")
        
        visualization = f"""
╔══════════════════════════════════════════════════════════╗
║              CLAIM PROCESSING STATUS                     ║
╠══════════════════════════════════════════════════════════╣
║  Claim ID: {str(claim.claim_id)[:50]:<50} ║
║  Status:   {color}{icon} {claim.status.value.upper():<45}{reset} ║
╠══════════════════════════════════════════════════════════╣
"""
        
        if claim.summary:
            visualization += f"""║  Claim Type:     {claim.summary.claim_type:<40} ║
║  Claimed Amount: ${claim.summary.claimed_amount:<39} ║
║  Claimant:       {claim.summary.claimant_name:<40} ║
║  Location:       {claim.summary.incident_location[:40]:<40} ║
╠══════════════════════════════════════════════════════════╣
"""
        
        # Show workflow progress
        workflow_steps = [
            ("📝 Draft", ClaimStatus.DRAFT),
            ("✅ Facts Extracted", ClaimStatus.FACTS_EXTRACTED),
            ("🔍 Policy Validated", ClaimStatus.POLICY_VALIDATED),
            ("🎯 Triaged", ClaimStatus.TRIAGED),
            ("⚙️ Processing", ClaimStatus.PROCESSING),
            ("✨ Completed", ClaimStatus.COMPLETED),
        ]
        
        visualization += "║  Workflow Progress:                                          ║\n"
        visualization += "║  "
        
        current_index = 0
        for i, (label, status) in enumerate(workflow_steps):
            if claim.status == status:
                current_index = i
                break
        
        for i, (label, status) in enumerate(workflow_steps):
            if i <= current_index:
                visualization += f"{color}●{reset} "
            else:
                visualization += "○ "
            if i < len(workflow_steps) - 1:
                visualization += "→ "
        
        visualization += "\n╚══════════════════════════════════════════════════════════╝\n"
        
        return visualization
    
    def visualize_event_timeline(self, claim_id: Optional[UUID] = None) -> str:
        """
        Generate a timeline visualization of domain events.
        
        Args:
            claim_id: Optional claim ID to filter events
        
        Returns:
            ASCII art timeline
        """
        relevant_events = [
            e for e in self.events
            if claim_id is None or (hasattr(e, 'claim_id') and e.claim_id == claim_id)
        ]
        
        if not relevant_events:
            return "No events recorded"
        
        timeline = "\n╔══════════════════════════════════════════════════════════╗\n"
        timeline += "║              DOMAIN EVENT TIMELINE                        ║\n"
        timeline += "╠══════════════════════════════════════════════════════════╣\n"
        
        for i, event in enumerate(relevant_events):
            event_type = event.event_type
            timestamp = event.occurred_at.strftime("%H:%M:%S")
            
            icon = "⚡" if "Event" in event_type else "📌"
            
            timeline += f"║  {icon} {event_type:<35} {timestamp:>10} ║\n"
            
            if i < len(relevant_events) - 1:
                timeline += "║    │                                                      ║\n"
                timeline += "║    ↓                                                      ║\n"
        
        timeline += "╚══════════════════════════════════════════════════════════╝\n"
        
        return timeline
    
    def visualize_workflow_flow(self) -> str:
        """
        Generate a flowchart-style visualization of the workflow.
        
        Returns:
            ASCII art flowchart
        """
        flow = """
╔══════════════════════════════════════════════════════════════════╗
║                    CLAIMS PROCESSING WORKFLOW                    ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📧 Unstructured Input                                           ║
║     │                                                            ║
║     ↓                                                            ║
║  ┌──────────────────────────────────────────────────────────┐   ║
║  │  🤖 Intake Agent                                         │   ║
║  │  Extract facts from unstructured data                   │   ║
║  └──────────────────────────────────────────────────────────┘   ║
║     │                                                            ║
║     ↓                                                            ║
║  ⚡ ClaimFactsExtracted Event                                    ║
║     │                                                            ║
║     ├──────────────────┬──────────────────┐                    ║
║     ↓                  ↓                  ↓                    ║
║  ┌─────────┐    ┌─────────┐    ┌─────────┐                  ║
║  │ 🔍      │    │ 🚩      │    │ 🎯      │                  ║
║  │ Policy  │    │ Fraud   │    │ Triage  │                  ║
║  │ Agent   │    │ Agent   │    │ Agent   │                  ║
║  └─────────┘    └─────────┘    └─────────┘                  ║
║     │                  │                  │                    ║
║     ↓                  ↓                  ↓                    ║
║  ⚡ PolicyValidated  ⚡ FraudScore      Routing Decision        ║
║     │                  │                  │                    ║
║     └──────────────────┴──────────────────┘                    ║
║                          │                                      ║
║                          ↓                                      ║
║                    📦 Downstream Systems                        ║
║                    (Human Queue / Automated)                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        return flow
    
    def generate_mermaid_diagram(self) -> str:
        """
        Generate a Mermaid diagram string for the workflow.
        
        Returns:
            Mermaid diagram code
        """
        return """graph TD
    A[Unstructured Input] --> B[Intake Agent]
    B --> C[ClaimFactsExtracted Event]
    C --> D[Policy Agent]
    C --> E[Fraud Assessment]
    D --> F[PolicyValidated Event]
    E --> G[FraudScoreCalculated Event]
    F --> H[Triage Agent]
    G --> H
    H --> I[Downstream Systems]
    
    style A fill:#e1f5ff
    style B fill:#fff4e1
    style C fill:#e8d5ff
    style D fill:#fff4e1
    style E fill:#fff4e1
    style F fill:#e8d5ff
    style G fill:#e8d5ff
    style H fill:#fff4e1
    style I fill:#d4edda
"""

