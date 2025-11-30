"""
Workflow Orchestrator - Event-driven workflow coordination

⚠️ DEMONSTRATION SYSTEM - NOT FOR PRODUCTION USE
This is an educational demonstration system. See DISCLAIMERS.md for details.

The orchestrator is the central coordinator that:
1. Listens to domain events
2. Invokes appropriate agents based on events
3. Manages workflow state
4. Publishes new events to continue the workflow

This follows Event-Driven Architecture (EDA) principles (Hohpe & Woolf, 2003):
- Loose coupling between components
- Event-driven communication
- Workflow orchestration through events

DDD Pattern: The orchestrator acts as an Application Service that coordinates
domain objects and agents without containing business logic (Evans, 2003).
"""

from typing import Optional
from uuid import UUID

from ..domain.claim import Claim
from ..domain.claim.document import Document, DocumentStatus
from ..domain.claim.events import (
    ClaimFactsExtracted,
    DocumentAdded,
    DocumentsValidated,
    DocumentAuthenticityChecked,
)
from ..domain.events import DomainEvent, EventBus, EventHandler
from ..domain.fraud import FraudCheckResult
from ..domain.fraud.events import FraudScoreCalculated
from ..domain.policy.events import PolicyValidated
from ..agents.intake_agent import IntakeAgent
from ..agents.policy_agent import PolicyAgent
from ..agents.triage_agent import TriageAgent
from ..agents.fraud_agent import FraudAgent
from ..agents.document_validation_agent import DocumentValidationAgent
from ..agents.document_analysis_agent import DocumentAnalysisAgent
from ..repositories import ClaimRepository, PolicyRepository
from ..human_review import HumanReviewAgent, ReviewPriority
from ..compliance.decision_audit import get_audit_service
from ..compliance.document_authenticity import get_authenticity_service
from ..compliance.models import DecisionType
from ..storage.document_storage import DocumentStorageService


class WorkflowOrchestrator:
    """
    Event-Driven Workflow Orchestrator.
    
    This orchestrator coordinates the entire claims processing workflow:
    1. Receives unstructured input
    2. Triggers Intake Agent to extract facts
    3. Listens for ClaimFactsExtracted event
    4. Triggers Policy Validation Agent
    5. Listens for PolicyValidated event
    6. Triggers Fraud Assessment (simplified)
    7. Triggers Triage & Routing Agent
    8. Routes to downstream systems
    
    DDD Pattern: The orchestrator acts as an Application Service that
    coordinates domain objects and agents without containing business logic.
    """
    
    def __init__(
        self,
        intake_agent: IntakeAgent,
        policy_agent: PolicyAgent,
        triage_agent: TriageAgent,
        fraud_agent: Optional[FraudAgent] = None,
        claim_repository: ClaimRepository = None,
        policy_repository: PolicyRepository = None,
        event_bus: Optional[EventBus] = None,
        human_review_agent: Optional[HumanReviewAgent] = None,
        document_validation_agent: Optional[DocumentValidationAgent] = None,
        document_analysis_agent: Optional[DocumentAnalysisAgent] = None,
        document_storage_service: Optional[DocumentStorageService] = None,
    ):
        """
        Initialize the workflow orchestrator.
        
        Args:
            intake_agent: Agent for extracting claim facts
            policy_agent: Agent for validating policies
            triage_agent: Agent for routing claims
            fraud_agent: Agent for fraud detection (optional, will use simple heuristic if not provided)
            claim_repository: Repository for claims
            policy_repository: Repository for policies
            event_bus: Event bus for publishing/subscribing (optional)
            human_review_agent: Optional human review agent for human-in-the-loop
            document_validation_agent: Optional agent for document validation
            document_analysis_agent: Optional agent for document analysis
            document_storage_service: Optional service for document storage
        """
        self.intake_agent = intake_agent
        self.policy_agent = policy_agent
        self.triage_agent = triage_agent
        self.fraud_agent = fraud_agent
        self.claim_repository = claim_repository
        self.policy_repository = policy_repository
        self.event_bus = event_bus or EventBus()
        self.human_review_agent = human_review_agent
        self.document_validation_agent = document_validation_agent
        self.document_analysis_agent = document_analysis_agent
        self.document_storage_service = document_storage_service or DocumentStorageService()
        self.authenticity_service = get_authenticity_service()
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register event handlers for domain events"""
        self.event_bus.subscribe("ClaimFactsExtracted", ClaimFactsExtractedHandler(self))
        self.event_bus.subscribe("PolicyValidated", PolicyValidatedHandler(self))
        self.event_bus.subscribe("FraudScoreCalculated", FraudScoreCalculatedHandler(self))
        self.event_bus.subscribe("DocumentAdded", DocumentAddedHandler(self))
        self.event_bus.subscribe("DocumentsValidated", DocumentsValidatedHandler(self))
    
    async def process_claim(self, raw_input: str, source: str = "email") -> Claim:
        """
        Main entry point: Process a new claim from unstructured input.
        
        This method:
        1. Creates a new Claim aggregate
        2. Triggers the Intake Agent to extract facts
        3. Publishes ClaimFactsExtracted event
        4. The event handlers continue the workflow
        
        Args:
            raw_input: Unstructured customer data (email, form, etc.)
            source: Source of the claim (email, web, phone, etc.)
        
        Returns:
            The created Claim aggregate
        """
        # Create new claim aggregate
        claim = Claim(raw_input=raw_input, source=source)
        
        # Save claim
        await self.claim_repository.save(claim)
        
        # Capture workflow start decision
        audit_service = get_audit_service()
        audit_service.capture_decision(
            claim_id=claim.claim_id,
            agent_component="WorkflowOrchestrator",
            decision_type=DecisionType.WORKFLOW_STEP,
            decision_value={
                "action": "workflow_started",
                "source": source,
            },
            reasoning=f"Workflow started for claim from {source}",
            workflow_step="claim_creation",
            success=True,
        )
        
        # Extract facts using Intake Agent
        # This acts as an Anti-Corruption Layer, translating unstructured
        # data into our domain model
        await self.intake_agent.extract_facts_for_claim(claim)
        
        # Get the domain event from the claim
        # The extract_facts_for_claim method updates the claim and creates the event
        domain_events = claim.get_domain_events()
        if not domain_events:
            raise RuntimeError("No domain event created after fact extraction")
        domain_event = domain_events[0]
        
        # Save updated claim
        await self.claim_repository.save(claim)
        
        # Human-in-the-Loop: Check if review needed after fact extraction
        if self.human_review_agent:
            if self.human_review_agent.should_review_after_extraction(claim):
                self.human_review_agent.add_for_review(
                    claim=claim,
                    reason="Fact extraction review needed (large amount or missing data)",
                    ai_decision=f"Facts extracted: {claim.summary.claim_type if claim.summary else 'unknown'}",
                    priority=ReviewPriority.HIGH if claim.summary and claim.summary.claimed_amount > 100000 else ReviewPriority.MEDIUM,
                )
                print(f"⚠️  Claim {claim.claim_id} added to review queue for fact extraction review")
        
        # Publish domain event to trigger next steps
        await self.event_bus.publish(domain_event)
        
        # Validate documents if any are present
        if claim.documents:
            await self._validate_claim_documents(claim)
        
        return claim
    
    async def add_document_to_claim(
        self,
        claim_id: UUID,
        file_content: bytes,
        filename: str,
        document_type: str,
    ) -> Document:
        """
        Add a document to a claim.
        
        Args:
            claim_id: ID of the claim
            file_content: Binary content of the file
            filename: Original filename
            document_type: Type of document (string value)
        
        Returns:
            Document Value Object
        """
        from ..domain.claim.document import DocumentType
        
        # Load claim
        claim = await self.claim_repository.find_by_id(claim_id)
        if not claim:
            raise ValueError(f"Claim not found: {claim_id}")
        
        # Convert document_type string to enum
        try:
            doc_type_enum = DocumentType(document_type)
        except ValueError:
            doc_type_enum = DocumentType.OTHER
        
        # Store document
        document = self.document_storage_service.store_document(
            claim_id=claim_id,
            file_content=file_content,
            filename=filename,
            document_type=doc_type_enum,
        )
        
        # Add document to claim aggregate
        event = claim.add_document(document)
        
        # Save claim
        await self.claim_repository.save(claim)
        
        # Publish domain event
        await self.event_bus.publish(event)
        
        # Perform authenticity check
        await self._check_document_authenticity(claim, document)
        
        return document
    
    async def _validate_claim_documents(self, claim: Claim) -> None:
        """
        Validate documents for a claim.
        
        Args:
            claim: Claim to validate documents for
        """
        if not self.document_validation_agent:
            return
        
        try:
            # Validate compliance
            validation_event = await self.document_validation_agent.validate_claim_documents(claim)
            
            # Update document statuses based on validation
            for doc in claim.documents:
                if doc.document_id in validation_event.validated_documents:
                    doc = doc.mark_validated()
                elif doc.document_id in validation_event.rejected_documents:
                    doc = doc.mark_rejected()
            
            # Save claim
            await self.claim_repository.save(claim)
            
            # Publish validation event
            await self.event_bus.publish(validation_event)
            
            # Route to human review if not compliant
            if not validation_event.is_compliant and self.human_review_agent:
                self.human_review_agent.add_for_review(
                    claim=claim,
                    reason=f"Document compliance violations: Missing {', '.join([dt.value for dt in validation_event.missing_document_types])}",
                    ai_decision=f"Document validation: {'Compliant' if validation_event.is_compliant else 'Non-compliant'}",
                    priority=ReviewPriority.HIGH,
                )
        except Exception as e:
            # Log error but don't fail the workflow
            print(f"Warning: Document validation failed: {e}")
    
    async def _check_document_authenticity(self, claim: Claim, document: Document) -> None:
        """
        Check document authenticity.
        
        Args:
            claim: Claim the document belongs to
            document: Document to check
        """
        try:
            # Perform authenticity check
            result = self.authenticity_service.check_authenticity(document)
            
            # Update document with authenticity score
            if result.is_suspicious:
                document = document.mark_suspicious(result.authenticity_score)
            else:
                document = document.mark_validated()
            
            # Update document in claim
            for i, doc in enumerate(claim.documents):
                if doc.document_id == document.document_id:
                    claim.documents[i] = document
                    break
            
            # Save claim
            await self.claim_repository.save(claim)
            
            # Create and publish authenticity event
            authenticity_event = DocumentAuthenticityChecked(
                claim_id=claim.claim_id,
                document_id=document.document_id,
                authenticity_score=result.authenticity_score,
                is_suspicious=result.is_suspicious,
                findings=result.findings,
            )
            await self.event_bus.publish(authenticity_event)
            
            # Route to human review if suspicious
            if result.is_suspicious and self.human_review_agent:
                self.human_review_agent.add_for_review(
                    claim=claim,
                    reason=f"Document authenticity concerns: {', '.join(result.findings[:3])}",
                    ai_decision=f"Authenticity score: {result.authenticity_score:.2f} - Suspicious",
                    priority=ReviewPriority.URGENT,
                )
        except Exception as e:
            # Log error but don't fail the workflow
            print(f"Warning: Document authenticity check failed: {e}")
    
    async def _handle_claim_facts_extracted(self, event: ClaimFactsExtracted) -> None:
        """
        Handle ClaimFactsExtracted event.
        
        This triggers:
        1. Policy validation
        2. Fraud assessment (simplified)
        """
        # Load claim
        claim = await self.claim_repository.find_by_id(event.claim_id)
        if not claim:
            return
        
        # Find relevant policies
        # In a real system, this would use policy_number from claim summary
        # For now, we'll check all active policies
        policies = await self.policy_repository.find_active_policies()
        
        # Validate policy
        policy_event = await self.policy_agent.validate_claim(claim, policies)
        
        # Save claim
        await self.claim_repository.save(claim)
        
        # Human-in-the-Loop: Check if review needed after policy validation
        if self.human_review_agent:
            if self.human_review_agent.should_review_after_policy_validation(claim, policy_event.is_valid):
                self.human_review_agent.add_for_review(
                    claim=claim,
                    reason=f"Policy validation review needed (validation result: {policy_event.is_valid})",
                    ai_decision=f"Policy validation: {'Valid' if policy_event.is_valid else 'Invalid'}",
                    priority=ReviewPriority.HIGH if not policy_event.is_valid else ReviewPriority.MEDIUM,
                )
                print(f"⚠️  Claim {claim.claim_id} added to review queue for policy validation review")
        
        # Publish policy validation event
        await self.event_bus.publish(policy_event)
        
        # Fraud assessment using FraudAgent (if available) or fallback to simple heuristic
        if claim.summary:
            if self.fraud_agent:
                # Use FraudAgent for LLM-based fraud detection
                fraud_event = await self.fraud_agent.assess_claim(claim)
                fraud_result = fraud_event.fraud_result
            else:
                # Fallback to simple heuristic if FraudAgent not available
                from ..domain.fraud import FraudRiskLevel
                from decimal import Decimal
                
                fraud_score = Decimal("0.1")  # Low risk by default
                risk_level = FraudRiskLevel.LOW
                
                # Simple heuristic: high amounts = higher risk
                if claim.summary.claimed_amount > Decimal("50000"):
                    fraud_score = Decimal("0.5")
                    risk_level = FraudRiskLevel.MEDIUM
                
                fraud_result = FraudCheckResult(
                    fraud_score=fraud_score,
                    risk_level=risk_level,
                    is_suspicious=False,
                    risk_factors=[],
                    assessment_method="simple_heuristic",
                )
                
                # Capture fraud assessment decision
                audit_service = get_audit_service()
                audit_service.capture_decision(
                    claim_id=claim.claim_id,
                    agent_component="WorkflowOrchestrator",
                    decision_type=DecisionType.FRAUD_ASSESSMENT,
                    decision_value={
                        "fraud_score": float(fraud_score),
                        "risk_level": risk_level.value,
                        "is_suspicious": fraud_result.is_suspicious,
                    },
                    reasoning=f"Fraud assessment: score {fraud_score}, risk level {risk_level.value} (simple heuristic based on claim amount)",
                    workflow_step="fraud_assessment",
                    success=True,
                )
                
                fraud_event = FraudScoreCalculated(
                    claim_id=claim.claim_id,
                    fraud_result=fraud_result,
                )
            
            # Human-in-the-Loop: Check if review needed after fraud assessment
            if self.human_review_agent:
                if self.human_review_agent.should_review_after_fraud_assessment(claim, fraud_result):
                    self.human_review_agent.add_for_review(
                        claim=claim,
                        reason=f"Fraud assessment review needed (fraud score: {fraud_result.fraud_score}, risk: {fraud_result.risk_level.value})",
                        ai_decision=f"Fraud score: {fraud_result.fraud_score}, Risk level: {fraud_result.risk_level.value}",
                        priority=ReviewPriority.URGENT if fraud_result.fraud_score >= 0.7 else ReviewPriority.HIGH,
                    )
                    print(f"⚠️  Claim {claim.claim_id} added to review queue for fraud assessment review")
            
            # Publish fraud assessment event
            await self.event_bus.publish(fraud_event)
    
    async def _handle_policy_validated(self, event: PolicyValidated) -> None:
        """
        Handle PolicyValidated event.
        
        This event indicates policy validation is complete.
        The triage agent will be triggered by FraudScoreCalculated event.
        """
        # Policy validation is complete
        # Triage will happen after fraud assessment
        pass
    
    async def _handle_fraud_score_calculated(self, event: FraudScoreCalculated) -> None:
        """
        Handle FraudScoreCalculated event.
        
        This triggers the triage and routing process.
        """
        # Load claim
        claim = await self.claim_repository.find_by_id(event.claim_id)
        if not claim:
            return
        
        # Load policy validation result
        # In a real system, we'd store this or retrieve from event store
        # For now, we'll check claim status
        policy_validated = None
        if claim.status.value == "policy_validated":
            policy_validated = PolicyValidated(
                claim_id=claim.claim_id,
                is_valid=True,
            )
        
        # Human-in-the-Loop: Check if review needed before final routing
        # If claim is in review queue, wait for human decision
        if self.human_review_agent:
            review_item = self.human_review_agent.review_queue.get_by_claim_id(claim.claim_id)
            if review_item and review_item.status.value in ["pending", "in_review"]:
                print(f"⏸️  Claim {claim.claim_id} awaiting human review before routing")
                return  # Wait for human review
        
        # Triage and route the claim
        routing_decision = await self.triage_agent.triage_claim(
            claim,
            fraud_result=event.fraud_result,
            policy_validated=policy_validated,
        )
        
        # Capture workflow-level routing decision
        audit_service = get_audit_service()
        audit_service.capture_decision(
            claim_id=claim.claim_id,
            agent_component="WorkflowOrchestrator",
            decision_type=DecisionType.WORKFLOW_STEP,
            decision_value={
                "routing_decision": routing_decision,
                "workflow_complete": True,
            },
            reasoning=f"Workflow completed: claim routed to {routing_decision}",
            workflow_step="final_routing",
            success=True,
        )
        
        # Save claim
        await self.claim_repository.save(claim)
        
        # Human-in-the-Loop: Optional review before final dispatch
        if self.human_review_agent:
            # Check if routing decision needs review (e.g., routing to fraud investigation)
            if routing_decision == "fraud_investigation":
                self.human_review_agent.add_for_review(
                    claim=claim,
                    reason="Routing review needed (routed to fraud investigation)",
                    ai_decision=f"Routing decision: {routing_decision}",
                    priority=ReviewPriority.HIGH,
                )
        
        # In a production system, this would dispatch to downstream systems
        # For now, we'll just log the routing decision
        print(f"Claim {claim.claim_id} routed to: {routing_decision}")
    
    async def _handle_document_added(self, event: DocumentAdded) -> None:
        """
        Handle DocumentAdded event.
        
        This triggers document authenticity checking and analysis.
        """
        # Load claim
        claim = await self.claim_repository.find_by_id(event.claim_id)
        if not claim:
            return
        
        # Find the document
        document = None
        for doc in claim.documents:
            if doc.document_id == event.document_id:
                document = doc
                break
        
        if not document:
            return
        
        # Perform authenticity check
        await self._check_document_authenticity(claim, document)
        
        # Perform document analysis if analysis agent is available
        if self.document_analysis_agent:
            try:
                await self.document_analysis_agent.analyze_document(claim, document)
            except Exception as e:
                print(f"Warning: Document analysis failed: {e}")
    
    async def _handle_documents_validated(self, event: DocumentsValidated) -> None:
        """
        Handle DocumentsValidated event.
        
        This event indicates document compliance validation is complete.
        The workflow can proceed or route to human review if non-compliant.
        """
        # Document validation is complete
        # The workflow continues based on compliance status
        # Non-compliant claims are already routed to human review
        pass


# Event Handlers

class ClaimFactsExtractedHandler(EventHandler):
    """Handler for ClaimFactsExtracted domain event"""
    
    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle ClaimFactsExtracted event"""
        if isinstance(event, ClaimFactsExtracted):
            await self.orchestrator._handle_claim_facts_extracted(event)


class PolicyValidatedHandler(EventHandler):
    """Handler for PolicyValidated domain event"""
    
    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle PolicyValidated event"""
        if isinstance(event, PolicyValidated):
            await self.orchestrator._handle_policy_validated(event)


class FraudScoreCalculatedHandler(EventHandler):
    """Handler for FraudScoreCalculated domain event"""
    
    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle FraudScoreCalculated event"""
        if isinstance(event, FraudScoreCalculated):
            await self.orchestrator._handle_fraud_score_calculated(event)


class DocumentAddedHandler(EventHandler):
    """Handler for DocumentAdded domain event"""
    
    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle DocumentAdded event"""
        if isinstance(event, DocumentAdded):
            await self.orchestrator._handle_document_added(event)


class DocumentsValidatedHandler(EventHandler):
    """Handler for DocumentsValidated domain event"""
    
    def __init__(self, orchestrator: WorkflowOrchestrator):
        self.orchestrator = orchestrator
    
    async def handle(self, event: DomainEvent) -> None:
        """Handle DocumentsValidated event"""
        if isinstance(event, DocumentsValidated):
            await self.orchestrator._handle_documents_validated(event)

