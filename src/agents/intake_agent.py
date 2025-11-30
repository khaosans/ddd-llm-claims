"""
Intake Agent - Extracts claim facts from unstructured data

This agent acts as an Anti-Corruption Layer (ACL) that:
1. Takes unstructured customer data (emails, forms, notes)
2. Uses an LLM to extract structured facts
3. Validates output against ClaimSummary (Value Object)
4. Publishes ClaimFactsExtracted domain event

This is the Core Domain agent - it's the heart of the business.
"""

import json
from typing import Optional
from uuid import UUID

from ..domain.claim import Claim, ClaimSummary
from ..domain.claim.events import ClaimFactsExtracted
from ..domain.events import DomainEvent
from .base_agent import BaseAgent
from ..compliance.decision_audit import get_audit_service
from ..compliance.decision_context import DecisionContextTracker
from ..compliance.models import DecisionType


class IntakeAgent(BaseAgent):
    """
    Intake Agent - Extracts structured claim facts from unstructured input.
    
    DDD Role: Anti-Corruption Layer (ACL)
    - Protects domain from unstructured external data
    - Translates customer language into domain model
    - Enforces domain invariants through validation
    
    This agent embodies "Prompt Engineering" - it uses carefully crafted
    prompts to make the LLM act as a Claims Analyst, extracting facts
    according to our domain model.
    """
    
    def get_system_prompt(self) -> str:
        """
        System prompt that makes the LLM act as a Claims Analyst.
        
        This is Prompt Engineering - we're programming the LLM's behavior
        through instructions, not code. The prompt:
        1. Defines the agent's role (Claims Analyst)
        2. Specifies the output format (JSON matching ClaimSummary)
        3. Provides examples and guidelines
        4. Enforces domain rules (e.g., dates, amounts)
        """
        return """You are an expert Claims Analyst working for an insurance company.
Your job is to extract structured facts from unstructured customer communications
(emails, forms, notes) and create a comprehensive claim summary.

IMPORTANT: You must output ONLY valid JSON that matches this exact schema:
{
    "claim_type": "string (e.g., 'auto', 'property', 'health')",
    "incident_date": "ISO 8601 datetime string (e.g., '2024-01-15T10:30:00')",
    "reported_date": "ISO 8601 datetime string (current date/time)",
    "claimed_amount": "decimal number as string (e.g., '5000.00')",
    "currency": "string (default: 'USD')",
    "incident_location": "string (full address or location description)",
    "description": "string (detailed description of the incident)",
    "claimant_name": "string (full name)",
    "claimant_email": "string or null (email address if provided)",
    "claimant_phone": "string or null (phone number if provided)",
    "policy_number": "string or null (policy number if mentioned)",
    "tags": ["array", "of", "relevant", "tags"]
}

RULES:
1. Extract ALL available information from the input
2. If information is missing, use null (not empty strings)
3. Dates must be valid ISO 8601 format
4. Amounts must be non-negative numbers
5. Incident date cannot be in the future
6. Be precise and factual - don't infer information not present
7. Output ONLY the JSON object, no additional text or explanation

Example output:
{
    "claim_type": "auto",
    "incident_date": "2024-01-15T14:30:00",
    "reported_date": "2024-01-16T09:00:00",
    "claimed_amount": "3500.00",
    "currency": "USD",
    "incident_location": "123 Main St, Anytown, ST 12345",
    "description": "Rear-end collision at intersection. Other driver ran red light.",
    "claimant_name": "John Doe",
    "claimant_email": "john.doe@email.com",
    "claimant_phone": "+1-555-0123",
    "policy_number": "POL-2024-001234",
    "tags": ["auto", "collision", "rear-end"]
}"""
    
    async def process(self, input_data: str, max_retries: int = 2, claim_id: Optional[UUID] = None) -> ClaimSummary:
        """
        Extract claim facts from unstructured input with automatic retry.
        
        This is the main processing method. It:
        1. Sends unstructured data to the LLM
        2. Validates the LLM output against ClaimSummary schema
        3. Retries with improved prompts if validation fails
        4. Returns the Value Object
        
        Args:
            input_data: Unstructured customer data (email, form, note, etc.)
            max_retries: Maximum retry attempts if parsing fails
            claim_id: Optional claim ID for decision tracking
        
        Returns:
            ClaimSummary Value Object
        
        Raises:
            ValueError: If LLM output doesn't match domain model after retries
        """
        import asyncio
        
        # Initialize decision context tracker
        tracker = DecisionContextTracker()
        tracker.add_input("input_data", input_data)
        tracker.add_input("max_retries", max_retries)
        tracker.set_prompt(self.get_system_prompt())
        
        # Create the prompt for the LLM
        base_prompt = f"""Extract claim facts from the following customer communication:

{input_data}

Output the extracted facts as JSON matching the schema provided in your instructions."""
        
        # Try with retries
        last_error = None
        success = False
        claim_summary = None
        
        for attempt in range(max_retries + 1):
            try:
                # Add retry instruction if not first attempt
                if attempt > 0:
                    prompt = f"""{base_prompt}

IMPORTANT: Output ONLY valid JSON. No additional text, explanations, or markdown formatting. Just the JSON object."""
                    tracker.add_intermediate_step(f"retry_attempt_{attempt}", {"attempt": attempt})
                else:
                    prompt = base_prompt
                
                # Generate response from LLM
                raw_output = await self.generate(prompt)
                tracker.set_llm_response(raw_output)
                
                # Validate output against domain model (ClaimSummary Value Object)
                # This is the Anti-Corruption Layer in action - we're ensuring
                # external LLM output conforms to our strict domain model
                claim_summary = self.validate_output(raw_output, ClaimSummary, max_retries=2)
                
                # Success - add evidence
                tracker.add_evidence("extraction_success", {
                    "attempt": attempt + 1,
                    "summary": claim_summary.model_dump() if hasattr(claim_summary, 'model_dump') else str(claim_summary),
                })
                success = True
                break
                
            except ValueError as e:
                last_error = e
                tracker.add_intermediate_step(f"validation_error_attempt_{attempt}", {
                    "attempt": attempt + 1,
                    "error": str(e),
                })
                if attempt < max_retries:
                    # Wait before retry (exponential backoff)
                    await asyncio.sleep(0.5 * (attempt + 1))
                    continue
                else:
                    # All retries exhausted
                    error_msg = (
                        f"Failed to extract claim facts after {max_retries + 1} attempts. "
                        f"Last error: {last_error}. "
                        f"This may indicate the LLM is not responding correctly. "
                        f"Try using Mock mode or check your Ollama setup."
                    )
                    raise ValueError(error_msg) from last_error
        
        # Capture decision
        if claim_id:
            audit_service = get_audit_service()
            reasoning = f"Extracted claim facts: {claim_summary.claim_type if claim_summary else 'unknown'} claim"
            if claim_summary and hasattr(claim_summary, 'description'):
                reasoning += f" - {claim_summary.description[:100]}"
            
            audit_service.capture_decision(
                claim_id=claim_id,
                agent_component="IntakeAgent",
                decision_type=DecisionType.FACT_EXTRACTION,
                decision_value=claim_summary.model_dump() if claim_summary and hasattr(claim_summary, 'model_dump') else str(claim_summary),
                reasoning=reasoning,
                context=tracker.build_context(),
                success=success,
                error_message=str(last_error) if not success else None,
            )
        
        # Should not reach here if successful, but handle edge case
        if not success:
            raise ValueError(f"Unexpected error in process method: {last_error}")
        
        return claim_summary
    
    async def extract_facts_for_claim(self, claim: Claim) -> ClaimFactsExtracted:
        """
        Extract facts for an existing claim.
        
        This method processes the claim's raw input and updates the claim
        with extracted facts. It's called by the workflow orchestrator.
        
        Args:
            claim: The claim to process
        
        Returns:
            ClaimFactsExtracted domain event
        """
        claim_summary = await self.process(claim.raw_input, claim_id=claim.claim_id)
        
        # Update the claim aggregate
        # This enforces domain invariants (e.g., can only extract once)
        # The extract_facts method creates the domain event with the claim_id
        domain_event = claim.extract_facts(claim_summary)
        
        return domain_event

