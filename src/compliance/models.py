"""
Domain Models for Compliance and Explainability

These models represent decision records, context, and explanations
for compliance audit trails and explainability.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DecisionType(str, Enum):
    """Types of decisions made by agents in the system"""
    
    FACT_EXTRACTION = "fact_extraction"  # Intake agent extracting facts
    POLICY_VALIDATION = "policy_validation"  # Policy agent validating claim
    FRAUD_ASSESSMENT = "fraud_assessment"  # Fraud assessment decision
    TRIAGE_ROUTING = "triage_routing"  # Triage agent routing decision
    WORKFLOW_STEP = "workflow_step"  # Workflow orchestrator step
    HUMAN_REVIEW = "human_review"  # Human reviewer decision
    CLAIM_STATUS_CHANGE = "claim_status_change"  # Claim status transition
    DOCUMENT_VALIDATION = "document_validation"  # Document validation decision
    DOCUMENT_AUTHENTICITY_CHECK = "document_authenticity_check"  # Document authenticity check
    DOCUMENT_MATCHING = "document_matching"  # Document-claim matching decision
    COMPLIANCE_CHECK = "compliance_check"  # Compliance check decision


class ExplanationLevel(str, Enum):
    """Levels of detail for explanations"""
    
    SUMMARY = "summary"  # High-level explanation
    DETAILED = "detailed"  # Full reasoning with evidence
    REGULATORY = "regulatory"  # Formatted for compliance reports
    DEBUG = "debug"  # Technical details for developers


class DecisionDependency(BaseModel):
    """Represents a dependency on another decision"""
    
    decision_id: UUID = Field(description="ID of the decision this depends on")
    dependency_type: str = Field(description="Type of dependency (e.g., 'required_for', 'influenced_by')")
    description: Optional[str] = Field(default=None, description="Description of the dependency")


class DecisionContext(BaseModel):
    """Context and evidence for a decision"""
    
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input data used for the decision")
    prompts: Optional[str] = Field(default=None, description="LLM prompt used (if applicable)")
    llm_response: Optional[str] = Field(default=None, description="Raw LLM response (if applicable)")
    intermediate_steps: List[Dict[str, Any]] = Field(
        default_factory=list, description="Intermediate processing steps"
    )
    evidence: List[Dict[str, Any]] = Field(
        default_factory=list, description="Supporting evidence for the decision"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class DecisionRecord(BaseModel):
    """
    Record of a decision made by an agent or component.
    
    This is the core model for the decision audit trail.
    Each decision captures who made it, what was decided, why,
    and all supporting context.
    """
    
    decision_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this decision")
    claim_id: UUID = Field(description="ID of the claim this decision relates to")
    agent_component: str = Field(description="Name of the agent/component that made the decision")
    decision_type: DecisionType = Field(description="Type of decision")
    decision_value: Any = Field(description="The actual decision made (varies by type)")
    reasoning: str = Field(description="Detailed explanation of why this decision was made")
    confidence: Optional[float] = Field(
        default=None, description="Confidence score (0.0-1.0) if applicable"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the decision was made")
    context: DecisionContext = Field(default_factory=DecisionContext, description="Full context and evidence")
    dependencies: List[DecisionDependency] = Field(
        default_factory=list, description="Other decisions this depends on"
    )
    workflow_step: Optional[str] = Field(
        default=None, description="Workflow step this decision belongs to"
    )
    success: bool = Field(default=True, description="Whether the decision was successful")
    error_message: Optional[str] = Field(
        default=None, description="Error message if decision failed"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class Explanation(BaseModel):
    """Generated explanation for a decision"""
    
    explanation_id: UUID = Field(default_factory=uuid4, description="Unique identifier for this explanation")
    decision_id: UUID = Field(description="ID of the decision being explained")
    level: ExplanationLevel = Field(description="Level of detail")
    content: str = Field(description="The explanation text")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="When explanation was generated")
    format: str = Field(default="text", description="Format of explanation (text, json, html, etc.)")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }

