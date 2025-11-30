"""
UI Services - Backend integration for Streamlit UI

Provides services to connect the UI to the orchestrator and repositories.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents import IntakeAgent, PolicyAgent, TriageAgent, FraudAgent
from src.agents.model_provider import create_model_provider
from src.agents.document_analysis_agent import DocumentAnalysisAgent
from src.agents.document_matching_agent import DocumentMatchingAgent
from src.agents.document_validation_agent import DocumentValidationAgent
from src.agents.api_config import get_api_config_manager
from src.domain.policy import Policy, PolicyStatus
from src.repositories.db_claim_repository import DatabaseClaimRepository
from src.repositories.db_policy_repository import DatabasePolicyRepository
from src.orchestrator import WorkflowOrchestrator
from src.human_review import ReviewQueue, HumanReviewAgent, FeedbackHandler
from src.compliance.workflow_integration import get_decision_monitor
from src.vector_store import ClaimVectorStore, PolicyVectorStore, FraudPatternStore


class UIService:
    """Service layer for UI operations"""
    
    def __init__(self, db_path: str = "data/claims.db", chroma_db_path: str = "data/chroma_db"):
        """
        Initialize the UI service.
        
        Args:
            db_path: Path to SQLite database file
            chroma_db_path: Path to ChromaDB persistence directory
        """
        self._orchestrator: Optional[WorkflowOrchestrator] = None
        self._claim_repo: Optional[DatabaseClaimRepository] = None
        self._policy_repo: Optional[DatabasePolicyRepository] = None
        self._review_queue: Optional[ReviewQueue] = None
        self._claim_vector_store: Optional[ClaimVectorStore] = None
        self._policy_vector_store: Optional[PolicyVectorStore] = None
        self._fraud_pattern_store: Optional[FraudPatternStore] = None
        self._db_path = db_path
        self._chroma_db_path = chroma_db_path
        self._initialized = False
    
    async def _ensure_initialized(self, provider_type: str = "ollama", model: str = None):
        """Initialize the orchestrator and repositories if not already done"""
        if self._initialized:
            return
        
        # Create model providers
        try:
            if provider_type.lower() == "mock" or provider_type.lower() == "mock (demo)":
                from unittest.mock import MagicMock, AsyncMock
                mock_provider = MagicMock()
                
                async def mock_generate(prompt, **kwargs):
                    # Handle vision/image analysis prompts
                    if "image" in prompt.lower() or "damage" in prompt.lower() or kwargs.get("images"):
                        return '{"damage_type":"collision","severity":"moderate","location_visible":"Main Street","date_indicators":"2024-01-15","matches_claim":true,"match_reasoning":"Image shows collision damage matching claim description","details":"Rear-end collision with visible damage to rear bumper"}'
                    if "fraud" in prompt.lower() or "analyze" in prompt.lower():
                        return '{"fraud_score":0.15,"risk_level":"low","is_suspicious":false,"risk_factors":[],"confidence":0.90}'
                    return '{"claim_type":"auto","incident_date":"2024-01-15T14:30:00","claimed_amount":"3500.00","currency":"USD","incident_location":"Main St","description":"Test","claimant_name":"John Doe"}'
                
                mock_provider.generate = AsyncMock(side_effect=mock_generate)
                mock_provider.supports_vision = lambda: True  # Mock supports vision
                mock_provider.model = "mock-vision-model"
                intake_provider = policy_provider = triage_provider = fraud_provider = mock_provider
            else:
                # Auto-detect model if not provided
                if not model or provider_type.lower() == "ollama":
                    from src.ui.utils import get_available_ollama_model
                    detected_model = get_available_ollama_model()
                    if detected_model:
                        model = detected_model
                    else:
                        # Fallback to default if detection fails
                        model = model or "llama3.2:3b"
                
                intake_provider = create_model_provider("ollama", model)
                policy_provider = create_model_provider("ollama", model)
                triage_provider = create_model_provider("ollama", model)
                fraud_provider = create_model_provider("ollama", model)
        except Exception as e:
            # Fallback to mock with informative error
            import warnings
            error_msg = str(e).lower()
            
            # Check if it's a model not found error
            if "404" in error_msg or "not found" in error_msg or "model" in error_msg:
                warnings.warn(
                    f"Ollama model not found or unavailable: {e}. "
                    f"Falling back to Mock mode. "
                    f"To use Ollama: 1) Check available models (ollama list), "
                    f"2) Ensure model is installed, 3) Restart Ollama if needed."
                )
            else:
                warnings.warn(
                    f"Failed to initialize Ollama provider: {e}. "
                    f"Falling back to Mock mode. "
                    f"Check Ollama is running: ollama serve"
                )
            
            from unittest.mock import MagicMock, AsyncMock
            mock_provider = MagicMock()
            
            async def mock_generate(prompt, **kwargs):
                # Handle vision/image analysis prompts
                if "image" in prompt.lower() or "damage" in prompt.lower() or kwargs.get("images"):
                    return '{"damage_type":"collision","severity":"moderate","location_visible":"Main Street","date_indicators":"2024-01-15","matches_claim":true,"match_reasoning":"Image shows collision damage matching claim description","details":"Rear-end collision with visible damage to rear bumper"}'
                if "fraud" in prompt.lower() or "analyze" in prompt.lower():
                    return '{"fraud_score":0.15,"risk_level":"low","is_suspicious":false,"risk_factors":[],"confidence":0.90}'
                return '{"claim_type":"auto","incident_date":"2024-01-15T14:30:00","claimed_amount":"3500.00","currency":"USD","incident_location":"Main St","description":"Test","claimant_name":"John Doe"}'
            
            mock_provider.generate = AsyncMock(side_effect=mock_generate)
            mock_provider.supports_vision = lambda: True  # Mock supports vision
            mock_provider.model = "mock-vision-model"
            intake_provider = policy_provider = triage_provider = fraud_provider = mock_provider
        
        # Initialize vector stores (with graceful fallback)
        try:
            self._claim_vector_store = ClaimVectorStore(persist_directory=self._chroma_db_path)
            self._policy_vector_store = PolicyVectorStore(persist_directory=self._chroma_db_path)
            self._fraud_pattern_store = FraudPatternStore(persist_directory=self._chroma_db_path)
        except ImportError:
            # ChromaDB not available, continue without vector stores
            import warnings
            warnings.warn("ChromaDB not available. Vector stores will not be initialized. Install with: pip install chromadb")
            self._claim_vector_store = None
            self._policy_vector_store = None
            self._fraud_pattern_store = None
        except Exception as e:
            # Other errors initializing vector stores
            import warnings
            warnings.warn(f"Failed to initialize vector stores: {e}. Continuing without vector stores.")
            self._claim_vector_store = None
            self._policy_vector_store = None
            self._fraud_pattern_store = None
        
        # Create repositories (database-backed) with error handling
        try:
            self._claim_repo = DatabaseClaimRepository(db_path=self._db_path)
            self._policy_repo = DatabasePolicyRepository(db_path=self._db_path)
        except Exception as e:
            # If database initialization fails, log warning but continue
            # This allows the system to work even if SQLAlchemy has issues
            import warnings
            warnings.warn(f"Database initialization warning: {e}. System will continue but data may not persist.")
            # Try to continue with in-memory repositories as fallback
            from src.repositories import InMemoryClaimRepository, InMemoryPolicyRepository
            self._claim_repo = InMemoryClaimRepository()
            self._policy_repo = InMemoryPolicyRepository()
        
        # Add sample policy if it doesn't exist
        from uuid import uuid4
        existing_policy = await self._policy_repo.find_by_policy_number("POL-2024-001234")
        if not existing_policy:
            sample_policy = Policy(
                policy_id=uuid4(),
                policy_number="POL-2024-001234",
                customer_id=uuid4(),
                status=PolicyStatus.ACTIVE,
                policy_type="auto",
                coverage_start=datetime(2024, 1, 1),
                coverage_end=datetime(2024, 12, 31),
                max_coverage_amount=Decimal("50000.00"),
            )
            await self._policy_repo.save(sample_policy)
        
        # Create agents
        intake_agent = IntakeAgent(intake_provider, temperature=0.3)
        policy_agent = PolicyAgent(policy_provider, temperature=0.2)
        triage_agent = TriageAgent(triage_provider, temperature=0.5)
        # Pass FraudPatternStore to FraudAgent if available
        fraud_agent = FraudAgent(
            fraud_provider, 
            temperature=0.2,
            fraud_pattern_store=self._fraud_pattern_store
        )
        
        # Create review queue
        self._review_queue = ReviewQueue()
        feedback_handler = FeedbackHandler()
        human_review_agent = HumanReviewAgent(self._review_queue, feedback_handler)
        
        # Create document agents (with auto-detection)
        try:
            # Use API config manager for document agents
            config_manager = get_api_config_manager()
            
            # Document Analysis Agent (for image analysis)
            document_analysis_agent = DocumentAnalysisAgent(
                model_provider=None,  # Will auto-detect
                temperature=0.3
            )
            
            # Document Matching Agent
            document_matching_agent = DocumentMatchingAgent(
                model_provider=None,  # Will auto-detect
                temperature=0.3
            )
            
            # Document Validation Agent (if available)
            try:
                document_validation_agent = DocumentValidationAgent(
                    model_provider=intake_provider,  # Can reuse intake provider
                    temperature=0.2
                )
            except Exception:
                document_validation_agent = None
        except Exception as e:
            # Fallback: create without auto-detection
            document_analysis_agent = DocumentAnalysisAgent(
                model_provider=intake_provider,
                temperature=0.3
            )
            document_matching_agent = DocumentMatchingAgent(
                model_provider=intake_provider,
                temperature=0.3
            )
            document_validation_agent = None
        
        # Create orchestrator
        self._orchestrator = WorkflowOrchestrator(
            intake_agent=intake_agent,
            policy_agent=policy_agent,
            triage_agent=triage_agent,
            fraud_agent=fraud_agent,
            claim_repository=self._claim_repo,
            policy_repository=self._policy_repo,
            human_review_agent=human_review_agent,
            document_validation_agent=document_validation_agent,
            document_analysis_agent=document_analysis_agent,
            document_matching_agent=document_matching_agent,
        )
        
        self._initialized = True
    
    @property
    def orchestrator(self) -> Optional[WorkflowOrchestrator]:
        """Get the workflow orchestrator"""
        return self._orchestrator
    
    async def process_claim(self, raw_input: str, source: str = "email", provider_type: str = "ollama", model: str = None) -> Dict[str, Any]:
        """Process a claim and return results"""
        try:
            await self._ensure_initialized(provider_type, model)
            
            if not raw_input or not raw_input.strip():
                raise ValueError("Claim input cannot be empty")
            
            claim = await self._orchestrator.process_claim(raw_input, source)
            
            # Wait a bit for async processing
            await asyncio.sleep(1)
            
            # Get updated claim
            updated_claim = await self._claim_repo.find_by_id(claim.claim_id)
            
            result = {
                "claim_id": str(claim.claim_id),
                "status": claim.status.value,
                "summary": None,
                "workflow_steps": []
            }
            
            if updated_claim:
                result["status"] = updated_claim.status.value
                if updated_claim.summary:
                    result["summary"] = {
                        "claim_type": updated_claim.summary.claim_type,
                        "incident_date": str(updated_claim.summary.incident_date) if updated_claim.summary.incident_date else None,
                        "claimed_amount": str(updated_claim.summary.claimed_amount) if updated_claim.summary.claimed_amount else None,
                        "currency": updated_claim.summary.currency,
                        "incident_location": updated_claim.summary.incident_location,
                        "claimant_name": updated_claim.summary.claimant_name,
                        "policy_number": updated_claim.summary.policy_number,
                    }
                
                # Build workflow steps
                if updated_claim.summary:
                    result["workflow_steps"].append(("✅", "Facts Extracted", "Intake Agent extracted structured facts"))
                if updated_claim.status.value in ["policy_validated", "triaged"]:
                    result["workflow_steps"].append(("✅", "Policy Validated", "Policy Agent validated coverage"))
                if updated_claim.status.value == "triaged":
                    result["workflow_steps"].append(("✅", "Fraud Assessed", "Fraud assessment completed"))
                    result["workflow_steps"].append(("✅", "Routed", f"Claim routed to {updated_claim.status.value}"))
            
            return result
        except ValueError as e:
            # Check if it's a JSON parsing error - suggest fallback
            error_msg = str(e).lower()
            if "json" in error_msg or "parse" in error_msg or "extra data" in error_msg:
                raise ValueError(
                    f"Failed to parse LLM response: {e}. "
                    f"The model may have returned malformed JSON. "
                    f"Try using Mock mode or a different model."
                )
            raise  # Re-raise other validation errors
        except Exception as e:
            # Check if it's an Ollama connection error
            error_msg = str(e).lower()
            if "ollama" in error_msg or "connection" in error_msg or "404" in error_msg:
                raise ValueError(
                    f"Ollama connection error: {e}. "
                    f"Please check: 1) Ollama is running (ollama serve), "
                    f"2) Model is installed (ollama list), "
                    f"3) Try Mock mode as fallback."
                )
            
            # Wrap other errors with user-friendly message
            raise Exception(
                f"Failed to process claim: {str(e)}. "
                f"Try using Mock mode if you're having issues with Ollama."
            )
    
    async def get_all_claims(self) -> List[Dict[str, Any]]:
        """Get all claims"""
        try:
            await self._ensure_initialized()
            
            claims = await self._claim_repo.find_all()
            
            result = []
            for claim in claims:
                claim_data = {
                    "claim_id": str(claim.claim_id),
                    "status": claim.status.value,
                    "source": claim.source,
                    "created_at": str(claim.created_at),
                    "claim_type": None,
                    "amount": None,
                    "claimant_name": None,
                }
                
                if claim.summary:
                    claim_data["claim_type"] = claim.summary.claim_type
                    claim_data["amount"] = str(claim.summary.claimed_amount) if claim.summary.claimed_amount else None
                    claim_data["claimant_name"] = claim.summary.claimant_name
                
                result.append(claim_data)
            
            return result
        except Exception as e:
            # Return empty list on error rather than crashing
            return []
    
    async def get_review_queue(self) -> List[Dict[str, Any]]:
        """Get review queue items"""
        try:
            await self._ensure_initialized()
            
            if not self._review_queue:
                return []
            
            reviews = self._review_queue.get_all_pending()
            
            result = []
            for review in reviews:
                result.append({
                    "claim_id": str(review.claim_id),
                    "priority": review.priority.value,
                    "reason": review.reason,
                    "status": review.status.value,
                    "ai_decision": review.ai_decision[:100] if review.ai_decision else "",
                })
            
            return result
        except Exception:
            # Return empty list on error
            return []
    
    async def get_claim_by_id(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get a claim by ID"""
        await self._ensure_initialized()
        
        try:
            claim = await self._claim_repo.find_by_id(UUID(claim_id))
            if not claim:
                return None
            
            result = {
                "claim_id": str(claim.claim_id),
                "status": claim.status.value,
                "source": claim.source,
                "raw_input": claim.raw_input,
                "created_at": str(claim.created_at),
                "summary": None,
            }
            
            if claim.summary:
                result["summary"] = {
                    "claim_type": claim.summary.claim_type,
                    "incident_date": str(claim.summary.incident_date) if claim.summary.incident_date else None,
                    "claimed_amount": str(claim.summary.claimed_amount) if claim.summary.claimed_amount else None,
                    "currency": claim.summary.currency,
                    "incident_location": claim.summary.incident_location,
                    "description": claim.summary.description,
                    "claimant_name": claim.summary.claimant_name,
                    "policy_number": claim.summary.policy_number,
                }
            
            return result
        except Exception:
            return None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            await self._ensure_initialized()
            
            claims = await self._claim_repo.find_all()
            
            total_claims = len(claims)
            processed_today = len([c for c in claims if c.created_at.date() == datetime.now().date()])
            
            reviews = []
            if self._review_queue:
                reviews = self._review_queue.get_all_pending()
            
            pending_reviews = len(reviews)
            
            return {
                "total_claims": total_claims,
                "processed_today": processed_today,
                "pending_reviews": pending_reviews,
            }
        except Exception:
            # Return default stats on error
            return {
                "total_claims": 0,
                "processed_today": 0,
                "pending_reviews": 0,
            }
    
    async def get_decision_status(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current decision status for a claim.
        
        Shows decisions made so far and current workflow progress.
        
        Args:
            claim_id: Claim ID as string
            
        Returns:
            Dictionary with decision status and progress
        """
        try:
            monitor = get_decision_monitor()
            return monitor.get_current_status(UUID(claim_id))
        except Exception as e:
            return {
                "error": str(e),
                "claim_id": claim_id,
            }
    
    async def get_step_decisions(self, claim_id: str, step_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get decisions for a specific workflow step.
        
        Args:
            claim_id: Claim ID as string
            step_name: Optional step name (if None, gets current step)
            
        Returns:
            Dictionary with step decisions
        """
        try:
            monitor = get_decision_monitor()
            return monitor.get_step_decisions(UUID(claim_id), step_name)
        except Exception as e:
            return {
                "error": str(e),
                "claim_id": claim_id,
            }
    
    async def get_all_steps_view(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete step-by-step view of all decisions.
        
        Args:
            claim_id: Claim ID as string
            
        Returns:
            Dictionary with all steps and decisions
        """
        try:
            monitor = get_decision_monitor()
            return monitor.get_all_steps_view(UUID(claim_id))
        except Exception as e:
            return {
                "error": str(e),
                "claim_id": claim_id,
            }
    
    async def get_audit_summary(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audit summary with findings and guidance.
        
        Useful for quick human review and auditing.
        
        Args:
            claim_id: Claim ID as string
            
        Returns:
            Dictionary with audit summary, findings, and guidance
        """
        try:
            monitor = get_decision_monitor()
            return monitor.get_audit_summary(UUID(claim_id))
        except Exception as e:
            return {
                "error": str(e),
                "claim_id": claim_id,
            }
    
    async def get_fraud_assessment_details(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed fraud assessment information for a claim"""
        try:
            await self._ensure_initialized()
            from src.compliance.decision_audit import get_audit_service
            from src.compliance.models import DecisionType
            from uuid import UUID
            
            audit_service = get_audit_service()
            decisions = audit_service.get_decisions_for_claim(UUID(claim_id), DecisionType.FRAUD_ASSESSMENT)
            
            if not decisions:
                return None
            
            # Get most recent fraud assessment
            fraud_decision = decisions[-1] if decisions else None
            if not fraud_decision:
                return None
            
            decision_value = fraud_decision.decision_value or {}
            
            return {
                "fraud_score": decision_value.get("fraud_score", 0.0),
                "risk_level": decision_value.get("risk_level", "unknown"),
                "is_suspicious": decision_value.get("is_suspicious", False),
                "risk_factors": decision_value.get("risk_factors", []),
                "reasoning": fraud_decision.reasoning,
                "confidence": fraud_decision.confidence,
                "timestamp": fraud_decision.timestamp.isoformat(),
                "assessment_method": decision_value.get("assessment_method", "unknown"),
            }
        except Exception:
            return None
    
    async def get_review_summary(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive review summary with all decision details"""
        try:
            await self._ensure_initialized()
            from src.compliance.workflow_integration import get_decision_monitor
            from uuid import UUID
            
            monitor = get_decision_monitor()
            audit_summary = monitor.get_audit_summary(UUID(claim_id))
            
            # Get fraud assessment details
            fraud_details = await self.get_fraud_assessment_details(claim_id)
            
            # Get claim details
            claim_details = await self.get_claim_by_id(claim_id)
            
            return {
                "claim": claim_details,
                "fraud_assessment": fraud_details,
                "audit_summary": audit_summary.get("summary", {}),
                "guidance": audit_summary.get("guidance", {}),
                "requires_review": audit_summary.get("requires_review", False),
            }
        except Exception:
            return None
    
    async def get_completion_summary(self, claim_id: str, include_explanations: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive completion summary.
        
        Use this after workflow completion to get full summary with findings and recommendations.
        
        Args:
            claim_id: Claim ID as string
            include_explanations: Whether to include decision explanations
            
        Returns:
            Dictionary with completion summary
        """
        try:
            monitor = get_decision_monitor()
            return monitor.get_completion_summary(UUID(claim_id), include_explanations=include_explanations)
        except Exception as e:
            return {
                "error": str(e),
                "claim_id": claim_id,
            }


# Global service instance
_service: Optional[UIService] = None


def get_service() -> UIService:
    """Get the global UI service instance"""
    global _service
    if _service is None:
        _service = UIService()
    return _service


def run_async(coro):
    """Run async function synchronously"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

