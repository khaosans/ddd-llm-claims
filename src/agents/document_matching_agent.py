"""
Document Matching Agent

Orchestrates document-claim matching:
- Checks required documents exist
- Analyzes images using vision models
- Matches image content to claim summary
- Generates recommendations
"""

from typing import Dict, List, Optional
from uuid import UUID

from ..compliance.decision_audit import get_audit_service
from ..compliance.decision_context import DecisionContextTracker
from ..compliance.models import DecisionType
from ..domain.claim import Claim
from ..domain.claim.document import Document, DocumentType
from ..domain.claim.document_matching import (
    DocumentClaimMatcher,
    DocumentMatchResult,
)
from .base_agent import BaseAgent
from .document_analysis_agent import DocumentAnalysisAgent
from .api_config import get_api_config_manager
from .model_provider import create_model_provider


class DocumentMatchingAgent(BaseAgent):
    """
    Agent for matching documents to claims.
    
    Orchestrates:
    1. Required document validation
    2. Image content analysis
    3. Content-to-claim matching
    4. Recommendation generation
    """
    
    def __init__(self, model_provider=None, temperature: float = 0.3):
        """
        Initialize document matching agent.
        
        Args:
            model_provider: Model provider (optional, will auto-detect)
            temperature: Temperature for LLM
        """
        # Auto-detect provider if not provided
        if model_provider is None:
            config_manager = get_api_config_manager()
            provider, model = config_manager.get_model_for_agent("document_matching")
            provider_config = config_manager.get_provider_config(provider)
            
            if provider == "ollama":
                model_provider = create_model_provider(
                    "ollama",
                    model,
                    base_url=provider_config.get("base_url", "http://localhost:11434")
                )
            elif provider == "openai":
                model_provider = create_model_provider(
                    "openai",
                    model,
                    api_key=provider_config.get("api_key")
                )
            elif provider == "anthropic":
                model_provider = create_model_provider(
                    "anthropic",
                    model,
                    api_key=provider_config.get("api_key")
                )
        
        super().__init__(model_provider, temperature)
        self.matcher = DocumentClaimMatcher()
        # Use the same model provider for document analysis (or None to auto-detect)
        self.document_analysis_agent = DocumentAnalysisAgent(
            model_provider=model_provider if model_provider else None,
            temperature=temperature
        )
        self.audit_service = get_audit_service()
    
    def get_system_prompt(self) -> str:
        """System prompt for document matching"""
        return """You are a Document-Claim Matching Specialist for an insurance claims system.
Your job is to match document content (especially images) to claim details and identify
inconsistencies, missing information, and provide recommendations."""
    
    async def match_documents_to_claim(
        self,
        claim: Claim,
    ) -> DocumentMatchResult:
        """
        Match documents to a claim.
        
        Args:
            claim: Claim to match documents for
        
        Returns:
            DocumentMatchResult with matching scores and recommendations
        """
        # Initialize decision context tracker
        tracker = DecisionContextTracker()
        tracker.add_input("claim_id", str(claim.claim_id))
        tracker.add_input("claim_type", claim.summary.claim_type if claim.summary else "unknown")
        tracker.add_input("document_count", len(claim.documents))
        
        try:
            # 1. Validate required documents
            claim_type = claim.summary.claim_type if claim.summary else "other"
            missing_required = self.matcher.validate_required_documents(
                claim_type,
                claim.documents
            )
            tracker.add_evidence("missing_required", [dt.value for dt in missing_required])
            
            # 2. Analyze images and match to claim
            image_analyses = {}
            matched_elements = []
            mismatches = []
            
            for doc in claim.documents:
                if doc.document_type == DocumentType.PHOTO:
                    # Analyze image
                    analysis = await self.document_analysis_agent.analyze_image_content(
                        doc,
                        claim
                    )
                    image_analyses[str(doc.document_id)] = analysis
                    
                    # Match to claim
                    match_result = await self._match_image_to_claim(
                        doc,
                        claim,
                        analysis
                    )
                    
                    if match_result:
                        matched_elements.extend(match_result.get("matched", []))
                        mismatches.extend(match_result.get("mismatches", []))
            
            # 3. Calculate overall match score
            match_score = self._calculate_match_score(
                matched_elements,
                mismatches,
                len(claim.documents),
                len(missing_required)
            )
            
            # 4. Generate recommendations
            recommendations = self.matcher.generate_recommendations(
                claim_type,
                claim.documents,
                None  # Will create match result first
            )
            
            # Create match result
            match_result = DocumentMatchResult(
                match_score=match_score,
                matched_elements=matched_elements,
                mismatches=mismatches,
                missing_documents=missing_required,
                recommendations=recommendations,
                image_analysis_results=image_analyses,
            )
            
            # Update recommendations with match result
            match_result.recommendations = self.matcher.generate_recommendations(
                claim_type,
                claim.documents,
                match_result
            )
            
            tracker.add_evidence("match_result", {
                "match_score": match_score,
                "matched_count": len(matched_elements),
                "mismatch_count": len(mismatches),
                "missing_count": len(missing_required),
            })
            
            # Capture decision
            reasoning = (
                f"Document matching completed. "
                f"Match score: {match_score:.2f}. "
                f"Found {len(matched_elements)} matched elements, "
                f"{len(mismatches)} mismatches, "
                f"{len(missing_required)} missing required documents."
            )
            
            self.audit_service.capture_decision(
                claim_id=claim.claim_id,
                agent_component="DocumentMatchingAgent",
                decision_type=DecisionType.DOCUMENT_MATCHING,
                decision_value={
                    "match_score": match_score,
                    "matched_elements": matched_elements,
                    "mismatches": mismatches,
                    "missing_documents": [dt.value for dt in missing_required],
                    "recommendations": recommendations,
                },
                reasoning=reasoning,
                context=tracker.build_context(),
                success=True,
            )
            
            return match_result
            
        except Exception as e:
            # Capture error
            self.audit_service.capture_decision(
                claim_id=claim.claim_id,
                agent_component="DocumentMatchingAgent",
                decision_type=DecisionType.DOCUMENT_MATCHING,
                decision_value={"error": str(e)},
                reasoning=f"Document matching failed: {str(e)}",
                context=tracker.build_context(),
                success=False,
                error_message=str(e),
            )
            raise
    
    async def _match_image_to_claim(
        self,
        document: Document,
        claim: Claim,
        image_analysis: Dict,
    ) -> Optional[Dict]:
        """
        Match image analysis to claim details.
        
        Args:
            document: Image document
            claim: Claim
            image_analysis: Image analysis result
        
        Returns:
            Dictionary with matched elements and mismatches
        """
        if "error" in image_analysis or not claim.summary:
            return None
        
        matched = []
        mismatches = []
        
        # Match damage type
        damage_type = image_analysis.get("damage_type", "").lower()
        claim_desc = claim.summary.description.lower()
        if damage_type and any(word in claim_desc for word in damage_type.split()):
            matched.append("damage_type")
        elif damage_type:
            mismatches.append(f"Damage type mismatch: image shows {damage_type}, claim describes different damage")
        
        # Match location
        location_visible = image_analysis.get("location_visible", "")
        if location_visible and location_visible.lower() in claim.summary.incident_location.lower():
            matched.append("location")
        elif location_visible:
            mismatches.append(f"Location mismatch: image shows {location_visible}, claim location is {claim.summary.incident_location}")
        
        # Match date (if visible in image)
        date_indicators = image_analysis.get("date_indicators", "")
        if date_indicators:
            # Simple check - in production would parse dates properly
            matched.append("date_indicators")
        
        # Overall match
        matches_claim = image_analysis.get("matches_claim", False)
        if matches_claim:
            matched.append("overall_match")
        else:
            match_reasoning = image_analysis.get("match_reasoning", "")
            if match_reasoning:
                mismatches.append(f"Image does not match claim: {match_reasoning}")
        
        return {
            "matched": matched,
            "mismatches": mismatches,
        }
    
    def _calculate_match_score(
        self,
        matched_elements: List[str],
        mismatches: List[str],
        total_documents: int,
        missing_required: int,
    ) -> float:
        """
        Calculate overall match score.
        
        Args:
            matched_elements: List of matched aspects
            mismatches: List of mismatches
            total_documents: Total number of documents
            missing_required: Number of missing required documents
        
        Returns:
            Match score (0.0-1.0)
        """
        # Base score from matches
        base_score = min(len(matched_elements) / max(len(matched_elements) + len(mismatches), 1), 1.0)
        
        # Penalty for mismatches
        mismatch_penalty = len(mismatches) * 0.1
        
        # Penalty for missing required documents
        missing_penalty = missing_required * 0.2
        
        # Final score
        score = max(0.0, base_score - mismatch_penalty - missing_penalty)
        
        return min(1.0, score)
    
    async def process(self, input_data: Claim) -> tuple[DocumentMatchResult, None]:
        """
        Process document matching.
        
        Args:
            input_data: Claim to match documents for
        
        Returns:
            Tuple of (match_result, None)
        """
        result = await self.match_documents_to_claim(input_data)
        return result, None

