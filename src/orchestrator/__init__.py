"""
Workflow Orchestrator - Event-driven workflow coordination

The orchestrator coordinates the workflow by:
1. Listening to domain events
2. Invoking appropriate agents
3. Managing the flow between bounded contexts
4. Publishing new domain events

This follows the Event-Driven Architecture pattern, enabling
loose coupling between bounded contexts.
"""

from .workflow_orchestrator import WorkflowOrchestrator

__all__ = ["WorkflowOrchestrator"]

