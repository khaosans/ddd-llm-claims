"""
Document Analysis Agent - LLM-based document content analysis

This agent extracts text from documents (OCR for images, text extraction for PDFs)
and uses LLM to analyze document content, cross-reference with claim summary,
and detect inconsistencies or fraud indicators.

Now supports vision models for image analysis.
"""

import base64
from typing import Dict, List, Optional
from uuid import UUID

from ..compliance.decision_audit import get_audit_service
from ..compliance.decision_context import DecisionContextTracker
from ..compliance.models import DecisionType
from ..domain.claim import Claim
from ..domain.claim.document import Document
from ..storage.document_storage import DocumentStorageService
from .base_agent import BaseAgent
from .cost_tracker import get_cost_tracker
from .api_config import get_api_config_manager
from .model_provider import create_model_provider


class DocumentAnalysisResult:
    """
    Result of document content analysis.
    """
    
    def __init__(
        self,
        document_id: UUID,
        extracted_text: str,
        analysis_summary: str,
        inconsistencies: List[str],
        fraud_indicators: List[str],
        confidence_score: float,
    ):
        """
        Initialize analysis result.
        
        Args:
            document_id: ID of the analyzed document
            extracted_text: Text extracted from the document
            analysis_summary: LLM-generated summary of document content
            inconsistencies: List of inconsistencies found with claim summary
            fraud_indicators: List of potential fraud indicators
            confidence_score: Confidence score (0.0-1.0)
        """
        self.document_id = document_id
        self.extracted_text = extracted_text
        self.analysis_summary = analysis_summary
        self.inconsistencies = inconsistencies
        self.fraud_indicators = fraud_indicators
        self.confidence_score = confidence_score


class DocumentAnalysisAgent(BaseAgent):
    """
    Agent for analyzing document content using LLM.
    
    This agent:
    1. Extracts text from documents (OCR for images, text extraction for PDFs)
    2. Uses LLM to analyze document content
    3. Cross-references document content with claim summary
    4. Detects inconsistencies or fraud indicators
    
    DDD Role: Application Service that coordinates document analysis
    """
    
    def __init__(self, model_provider=None, temperature: float = 0.3):
        """
        Initialize the document analysis agent.
        
        Args:
            model_provider: Model provider for LLM analysis (optional, will auto-detect if None)
            temperature: Temperature for LLM (lower for more consistent analysis)
        """
        # Auto-detect provider if not provided
        if model_provider is None:
            config_manager = get_api_config_manager()
            provider, model = config_manager.get_model_for_agent("document_analysis")
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
        self.storage_service = DocumentStorageService()
        self.audit_service = get_audit_service()
        self.cost_tracker = get_cost_tracker()
    
    def get_system_prompt(self) -> str:
        """
        System prompt for document analysis agent.
        """
        return """You are a Document Content Analyst for an insurance claims processing system.
Your job is to analyze supporting documents and cross-reference them with claim information
to detect inconsistencies, verify authenticity, and identify potential fraud indicators.

You analyze:
1. Document content and extract key information
2. Consistency between document content and claim summary
3. Potential fraud indicators (dates, amounts, locations, etc.)
4. Document authenticity clues

Be thorough, objective, and provide clear analysis with evidence."""
    
    async def analyze_document(
        self,
        claim: Claim,
        document: Document,
    ) -> DocumentAnalysisResult:
        """
        Analyze a document's content and cross-reference with claim summary.
        
        Args:
            claim: The claim the document belongs to
            document: Document to analyze
        
        Returns:
            DocumentAnalysisResult with analysis findings
        """
        # Initialize decision context tracker
        tracker = DecisionContextTracker()
        tracker.add_input("claim_id", str(claim.claim_id))
        tracker.add_input("document_id", str(document.document_id))
        tracker.add_input("document_type", document.document_type.value)
        
        # Extract text from document
        extracted_text = await self._extract_text(document)
        tracker.add_input("extracted_text_length", len(extracted_text))
        
        # Prepare claim summary context
        claim_context = self._prepare_claim_context(claim)
        
        # Analyze with LLM
        analysis_prompt = self._build_analysis_prompt(
            document,
            extracted_text,
            claim_context,
        )
        
        tracker.set_prompt(analysis_prompt)
        
        try:
            # For images, use vision model if available
            mime_type = document.metadata.mime_type if document.metadata else ""
            if mime_type.startswith("image/"):
                # Analyze image content
                image_analysis = await self.analyze_image_content(document, claim)
                tracker.add_evidence("image_analysis", image_analysis)
                
                # Build enhanced prompt with image analysis
                if "error" not in image_analysis:
                    analysis_prompt = f"""Based on the image analysis and claim information:

Image Analysis:
{str(image_analysis)}

Claim Information:
{claim_context}

Please provide your analysis in JSON format:
{{
    "summary": "Brief summary of document content",
    "inconsistencies": ["list", "of", "inconsistencies"],
    "fraud_indicators": ["list", "of", "fraud", "indicators"],
    "confidence_score": 0.85
}}"""
            
            llm_response = await self.generate(analysis_prompt)
            tracker.set_llm_response(llm_response)
            
            # Track cost
            provider_name = self.model_provider.__class__.__name__.replace("Provider", "").lower()
            model_name = self.model_provider.model
            self.cost_tracker.record_usage(
                provider=provider_name,
                model=model_name,
                input_tokens=len(analysis_prompt) // 4,  # Rough estimate
                output_tokens=len(llm_response) // 4,
                call_type="text"
            )
            
            # Parse analysis result
            analysis_result = self._parse_analysis_result(llm_response, document.document_id)
            tracker.add_evidence("analysis_result", {
                "inconsistencies_count": len(analysis_result.inconsistencies),
                "fraud_indicators_count": len(analysis_result.fraud_indicators),
                "confidence_score": analysis_result.confidence_score,
            })
            
            # Capture decision in audit trail
            reasoning = (
                f"Document analysis completed. "
                f"Found {len(analysis_result.inconsistencies)} inconsistencies, "
                f"{len(analysis_result.fraud_indicators)} fraud indicators. "
                f"Confidence: {analysis_result.confidence_score:.2f}"
            )
            
            self.audit_service.capture_decision(
                claim_id=claim.claim_id,
                agent_component="DocumentAnalysisAgent",
                decision_type=DecisionType.DOCUMENT_VALIDATION,
                decision_value={
                    "document_id": str(document.document_id),
                    "inconsistencies": analysis_result.inconsistencies,
                    "fraud_indicators": analysis_result.fraud_indicators,
                    "confidence_score": analysis_result.confidence_score,
                },
                reasoning=reasoning,
                context=tracker.build_context(),
                success=True,
            )
            
            return analysis_result
            
        except Exception as e:
            # Capture error in audit trail
            self.audit_service.capture_decision(
                claim_id=claim.claim_id,
                agent_component="DocumentAnalysisAgent",
                decision_type=DecisionType.DOCUMENT_VALIDATION,
                decision_value={"error": str(e)},
                reasoning=f"Document analysis failed: {str(e)}",
                context=tracker.build_context(),
                success=False,
                error_message=str(e),
            )
            raise
    
    async def analyze_image_content(
        self,
        document: Document,
        claim: Claim,
    ) -> Dict:
        """
        Analyze image content using vision models.
        
        Args:
            document: Image document to analyze
            claim: Claim the image belongs to
        
        Returns:
            Dictionary with analysis results
        """
        try:
            content = self.storage_service.retrieve_document(document)
            mime_type = document.metadata.mime_type if document.metadata else ""
            
            if not mime_type.startswith("image/"):
                return {"error": "Document is not an image"}
            
            # Check if provider supports vision
            if not self.model_provider.supports_vision():
                # Try to get a vision-capable provider
                config_manager = get_api_config_manager()
                preferred = config_manager.get_preferred_provider("document_analysis")
                
                # Try to find vision-capable provider
                if config_manager.is_provider_available("ollama"):
                    provider_config = config_manager.get_provider_config("ollama")
                    vision_provider = create_model_provider(
                        "ollama",
                        "llava",  # Common Ollama vision model
                        base_url=provider_config.get("base_url", "http://localhost:11434")
                    )
                elif config_manager.is_provider_available("openai"):
                    provider_config = config_manager.get_provider_config("openai")
                    vision_provider = create_model_provider(
                        "openai",
                        "gpt-4o",  # Vision-capable model
                        api_key=provider_config.get("api_key")
                    )
                elif config_manager.is_provider_available("anthropic"):
                    provider_config = config_manager.get_provider_config("anthropic")
                    vision_provider = create_model_provider(
                        "anthropic",
                        "claude-3-5-sonnet-20241022",
                        api_key=provider_config.get("api_key")
                    )
                else:
                    return {"error": "No vision-capable provider available"}
            else:
                vision_provider = self.model_provider
            
            # Prepare prompt for image analysis
            claim_context = self._prepare_claim_context(claim)
            prompt = f"""Analyze this image in the context of an insurance claim.

Claim Information:
{claim_context}

Please analyze the image and provide:
1. What damage or incident is visible in the image?
2. What type of damage (e.g., collision, fire, water, theft)?
3. Severity of damage (if applicable)
4. Location visible in image (if any)
5. Date/time indicators (if any)
6. Does the image match the claim description?

Provide your analysis in JSON format:
{{
    "damage_type": "type of damage observed",
    "severity": "severity level",
    "location_visible": "location if visible",
    "date_indicators": "date/time if visible",
    "matches_claim": true/false,
    "match_reasoning": "explanation of match/mismatch",
    "details": "detailed description of what's in the image"
}}"""
            
            # Analyze with vision model
            response = await vision_provider.generate(
                prompt=prompt,
                images=[content],
                system_prompt="You are an expert insurance claims analyst analyzing damage photos."
            )
            
            # Track cost (approximate - vision models have different pricing)
            provider_name = vision_provider.__class__.__name__.replace("Provider", "").lower()
            model_name = vision_provider.model
            self.cost_tracker.record_usage(
                provider=provider_name,
                model=model_name,
                input_tokens=len(prompt) // 4,  # Rough estimate
                output_tokens=len(response) // 4,
                call_type="vision"
            )
            
            # Parse response
            from .json_utils import parse_json_resilient
            analysis = parse_json_resilient(response, max_attempts=3)
            
            return analysis or {"raw_response": response}
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _extract_text(self, document: Document) -> str:
        """
        Extract text from document (OCR for images using vision models, text extraction for PDFs).
        
        Args:
            document: Document to extract text from
        
        Returns:
            Extracted text content
        """
        try:
            content = self.storage_service.retrieve_document(document)
            mime_type = document.metadata.mime_type if document.metadata else ""
            
            # For PDFs, try to extract text
            if mime_type == "application/pdf":
                try:
                    import PyPDF2
                    import io
                    
                    pdf_file = io.BytesIO(content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    text_parts = []
                    for page in pdf_reader.pages:
                        text_parts.append(page.extract_text())
                    
                    return "\n".join(text_parts)
                except Exception:
                    return "[PDF text extraction failed - document may be image-based PDF]"
            
            # For images, use vision model analysis
            if mime_type.startswith("image/"):
                # Use vision model to extract information from image
                # This is a placeholder - actual implementation would analyze the image
                # For now, return a message indicating vision analysis is available
                return "[Image content - will be analyzed using vision model]"
            
            # For other types, return placeholder
            return f"[Text extraction not available for {mime_type}]"
            
        except Exception as e:
            return f"[Text extraction failed: {str(e)}]"
    
    def _prepare_claim_context(self, claim: Claim) -> str:
        """
        Prepare claim summary context for analysis.
        
        Args:
            claim: Claim to prepare context for
        
        Returns:
            Formatted claim context string
        """
        if not claim.summary:
            return "Claim summary not available"
        
        summary = claim.summary
        context = f"""Claim Information:
- Type: {summary.claim_type}
- Incident Date: {summary.incident_date}
- Claimed Amount: {summary.claimed_amount} {summary.currency}
- Location: {summary.incident_location}
- Description: {summary.description}
- Claimant: {summary.claimant_name}
"""
        return context
    
    def _build_analysis_prompt(
        self,
        document: Document,
        extracted_text: str,
        claim_context: str,
    ) -> str:
        """
        Build LLM prompt for document analysis.
        
        Args:
            document: Document being analyzed
            extracted_text: Extracted text from document
            claim_context: Claim summary context
        
        Returns:
            Analysis prompt string
        """
        return f"""Analyze the following supporting document and cross-reference it with the claim information.

Document Type: {document.document_type.value}
Document Filename: {document.filename}

Extracted Document Content:
{extracted_text[:2000]}  # Limit to avoid token limits

Claim Information:
{claim_context}

Please analyze:
1. What information does this document contain?
2. Does the document content match the claim information (dates, amounts, locations, etc.)?
3. Are there any inconsistencies between the document and the claim?
4. Are there any potential fraud indicators (suspicious dates, amounts, etc.)?

Provide your analysis in the following JSON format:
{{
    "summary": "Brief summary of document content",
    "inconsistencies": ["list", "of", "inconsistencies"],
    "fraud_indicators": ["list", "of", "fraud", "indicators"],
    "confidence_score": 0.85
}}"""
    
    def _parse_analysis_result(
        self,
        llm_response: str,
        document_id: UUID,
    ) -> DocumentAnalysisResult:
        """
        Parse LLM response into DocumentAnalysisResult.
        
        Args:
            llm_response: Raw LLM response
            document_id: Document ID
        
        Returns:
            DocumentAnalysisResult
        """
        try:
            # Try to extract JSON from response
            from .json_utils import parse_json_resilient
            
            data = parse_json_resilient(llm_response, max_attempts=3)
            
            if data:
                return DocumentAnalysisResult(
                    document_id=document_id,
                    extracted_text="",  # Already stored separately
                    analysis_summary=data.get("summary", "Analysis completed"),
                    inconsistencies=data.get("inconsistencies", []),
                    fraud_indicators=data.get("fraud_indicators", []),
                    confidence_score=float(data.get("confidence_score", 0.5)),
                )
        except Exception:
            pass
        
        # Fallback: create result from raw text
        return DocumentAnalysisResult(
            document_id=document_id,
            extracted_text="",
            analysis_summary=llm_response[:500],
            inconsistencies=[],
            fraud_indicators=[],
            confidence_score=0.5,
        )
    
    async def process(self, input_data: tuple[Claim, Document]) -> tuple[DocumentAnalysisResult, None]:
        """
        Process document analysis.
        
        This method implements the BaseAgent interface.
        
        Args:
            input_data: Tuple of (Claim, Document)
        
        Returns:
            Tuple of (analysis_result, None)
        """
        claim, document = input_data
        result = await self.analyze_document(claim, document)
        return result, None

