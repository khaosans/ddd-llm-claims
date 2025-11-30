"""
Tests for Intake Agent

These tests demonstrate how the Intake Agent acts as an Anti-Corruption Layer,
translating unstructured input into domain models.
"""

import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.intake_agent import IntakeAgent
from src.agents.model_provider import OllamaProvider
from src.domain.claim import ClaimSummary


@pytest.fixture
def mock_model_provider():
    """Create a mock model provider for testing"""
    provider = MagicMock(spec=OllamaProvider)
    provider.generate = AsyncMock()
    return provider


@pytest.fixture
def intake_agent(mock_model_provider):
    """Create an Intake Agent with mocked model provider"""
    return IntakeAgent(model_provider=mock_model_provider, temperature=0.3)


@pytest.fixture
def sample_email():
    """Sample unstructured email"""
    return """Subject: Auto Insurance Claim

Dear Insurance Company,

I am filing a claim for a car accident on January 15, 2024 at 2:30 PM.
The incident occurred at Main Street and Oak Avenue in Anytown, State 12345.
Another driver rear-ended my vehicle. Repair costs are $3,500.00.

My policy number is POL-2024-001234.
Contact: john.doe@email.com, +1-555-0123

John Doe"""


@pytest.fixture
def expected_json_output():
    """Expected JSON output from LLM"""
    return json.dumps({
        "claim_type": "auto",
        "incident_date": "2024-01-15T14:30:00",
        "reported_date": "2024-01-16T09:00:00",
        "claimed_amount": "3500.00",
        "currency": "USD",
        "incident_location": "Main Street and Oak Avenue, Anytown, State 12345",
        "description": "Rear-end collision. Other driver hit claimant's vehicle from behind.",
        "claimant_name": "John Doe",
        "claimant_email": "john.doe@email.com",
        "claimant_phone": "+1-555-0123",
        "policy_number": "POL-2024-001234",
        "tags": ["auto", "collision", "rear-end"]
    })


@pytest.mark.asyncio
async def test_intake_agent_extracts_facts(intake_agent, mock_model_provider, sample_email, expected_json_output):
    """
    Test that Intake Agent correctly extracts facts from unstructured input.
    
    This test verifies the Anti-Corruption Layer pattern:
    - Unstructured input → LLM → Structured domain model
    """
    # Mock LLM response
    mock_model_provider.generate.return_value = expected_json_output
    
    # Process the email
    claim_summary, event = await intake_agent.process(sample_email)
    
    # Verify the result is a valid ClaimSummary (Value Object)
    assert isinstance(claim_summary, ClaimSummary)
    assert claim_summary.claim_type == "auto"
    assert claim_summary.claimed_amount == Decimal("3500.00")
    assert claim_summary.claimant_name == "John Doe"
    assert claim_summary.policy_number == "POL-2024-001234"
    
    # Verify domain event was created
    assert event is not None
    assert event.summary == claim_summary


@pytest.mark.asyncio
async def test_intake_agent_validates_domain_invariants(intake_agent, mock_model_provider):
    """
    Test that Intake Agent enforces domain invariants.
    
    Domain Invariants are business rules that must always be true.
    This test verifies that invalid data is rejected.
    """
    # Mock LLM response with invalid data (negative amount)
    invalid_json = json.dumps({
        "claim_type": "auto",
        "incident_date": "2024-01-15T14:30:00",
        "reported_date": "2024-01-16T09:00:00",
        "claimed_amount": "-1000.00",  # Invalid: negative amount
        "currency": "USD",
        "incident_location": "Test Location",
        "description": "Test description",
        "claimant_name": "Test User",
        "claimant_email": None,
        "claimant_phone": None,
        "policy_number": None,
        "tags": []
    })
    
    mock_model_provider.generate.return_value = invalid_json
    
    # Processing should fail due to domain invariant violation
    with pytest.raises(ValueError, match="cannot be negative"):
        await intake_agent.process("test input")


@pytest.mark.asyncio
async def test_intake_agent_handles_markdown_wrapped_json(intake_agent, mock_model_provider):
    """
    Test that Intake Agent handles JSON wrapped in markdown code blocks.
    
    LLMs sometimes wrap JSON in markdown, so the ACL must handle this.
    """
    # Mock LLM response with markdown-wrapped JSON
    wrapped_json = "```json\n" + json.dumps({
        "claim_type": "property",
        "incident_date": "2024-01-15T10:00:00",
        "reported_date": "2024-01-16T09:00:00",
        "claimed_amount": "5000.00",
        "currency": "USD",
        "incident_location": "123 Test St",
        "description": "Water damage",
        "claimant_name": "Jane Smith",
        "claimant_email": None,
        "claimant_phone": None,
        "policy_number": None,
        "tags": ["property", "water-damage"]
    }) + "\n```"
    
    mock_model_provider.generate.return_value = wrapped_json
    
    # Should successfully parse despite markdown wrapping
    claim_summary, _ = await intake_agent.process("test input")
    assert isinstance(claim_summary, ClaimSummary)
    assert claim_summary.claim_type == "property"


@pytest.mark.asyncio
async def test_intake_agent_system_prompt(intake_agent):
    """
    Test that system prompt is properly configured.
    
    The system prompt is crucial for Prompt Engineering - it defines
    how the LLM behaves as a Claims Analyst.
    """
    prompt = intake_agent.get_system_prompt()
    
    # Verify prompt contains key instructions
    assert "Claims Analyst" in prompt
    assert "JSON" in prompt
    assert "claim_type" in prompt
    assert "incident_date" in prompt
    assert "claimed_amount" in prompt


@pytest.mark.asyncio
async def test_intake_agent_extract_facts_for_claim(intake_agent, mock_model_provider, sample_email, expected_json_output):
    """
    Test the full workflow: extract facts and update claim aggregate.
    
    This tests the integration between the agent and the domain model.
    """
    from src.domain.claim import Claim
    
    # Create a claim
    claim = Claim(raw_input=sample_email, source="email")
    
    # Mock LLM response
    mock_model_provider.generate.return_value = expected_json_output
    
    # Extract facts
    event = await intake_agent.extract_facts_for_claim(claim)
    
    # Verify claim was updated
    assert claim.summary is not None
    assert claim.status.value == "facts_extracted"
    assert event.claim_id == claim.claim_id
    assert event.summary == claim.summary

