"""
LangChain-based Intake Agent

Uses LangChain framework for fact extraction from unstructured claims.
"""

from typing import Optional

from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

from ..domain.claim import ClaimSummary
from ..domain.claim.events import ClaimFactsExtracted


class LangChainIntakeAgent:
    """
    LangChain-based Intake Agent for extracting claim facts.
    
    Uses LangChain's structured output capabilities and agent framework.
    """
    
    def __init__(
        self,
        llm: BaseChatModel,
        temperature: float = 0.3,
        tools: Optional[list] = None
    ):
        """
        Initialize the LangChain intake agent.
        
        Args:
            llm: LangChain chat model (ChatOpenAI, ChatOllama, etc.)
            temperature: Sampling temperature
            tools: Optional LangChain tools for the agent
        """
        self.llm = llm
        self.temperature = temperature
        self.tools = tools or []
        
        # Create system prompt
        self.system_prompt = """You are an expert Claims Analyst working for an insurance company.
Your job is to extract structured facts from unstructured customer communications
(emails, forms, notes) and create a comprehensive claim summary.

You must output structured JSON matching this exact schema:
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
6. Be precise and factual - don't infer information not present"""
    
    async def extract_facts(self, input_data: str) -> ClaimSummary:
        """
        Extract claim facts from unstructured input using LangChain.
        
        Args:
            input_data: Unstructured customer data
        
        Returns:
            ClaimSummary Value Object
        """
        from langchain.output_parsers import PydanticOutputParser
        from langchain_core.output_parsers import JsonOutputParser
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "Extract claim facts from the following customer communication:\n\n{input}\n\nOutput the extracted facts as JSON matching the schema provided in your instructions."),
        ])
        
        # Use structured output if supported, otherwise JSON parser
        try:
            # Try structured output (for models that support it)
            chain = prompt | self.llm.with_structured_output(ClaimSummary)
            result = await chain.ainvoke({"input": input_data})
            return result
        except Exception:
            # Fallback to JSON parsing
            parser = JsonOutputParser(pydantic_object=ClaimSummary)
            chain = prompt | self.llm | parser
            result = await chain.ainvoke({"input": input_data})
            
            # Validate and create ClaimSummary
            return ClaimSummary(**result)
    
    async def extract_facts_for_claim(self, claim) -> ClaimFactsExtracted:
        """
        Extract facts for an existing claim.
        
        Args:
            claim: The claim to process
        
        Returns:
            ClaimFactsExtracted domain event
        """
        claim_summary = await self.extract_facts(claim.raw_input)
        domain_event = claim.extract_facts(claim_summary)
        return domain_event

