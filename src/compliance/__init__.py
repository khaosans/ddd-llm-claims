"""
Compliance and Explainability Framework

This module provides comprehensive decision audit trails, explainability,
and debugging capabilities for regulatory compliance and system transparency.

Key Components:
- DecisionAuditService: Captures all agent decisions with full context
- ExplainabilityService: Generates human-readable explanations
- DecisionContextTracker: Tracks decision context and evidence
- ComplianceReporter: Generates regulatory reports
- DebuggingTools: Provides debugging and analysis capabilities
"""

from .decision_audit import DecisionAuditService
from .explainability import ExplainabilityService, ExplanationLevel
from .decision_context import DecisionContextTracker
from .reporter import ComplianceReporter
from .debugging import DebuggingTools
from .decision_viewer import DecisionViewer
from .completion_summary import CompletionSummary
from .models import (
    DecisionRecord,
    DecisionType,
    DecisionContext,
    Explanation,
    DecisionDependency,
)

__all__ = [
    "DecisionAuditService",
    "ExplainabilityService",
    "ExplanationLevel",
    "DecisionContextTracker",
    "ComplianceReporter",
    "DebuggingTools",
    "DecisionViewer",
    "CompletionSummary",
    "DecisionRecord",
    "DecisionType",
    "DecisionContext",
    "Explanation",
    "DecisionDependency",
]

