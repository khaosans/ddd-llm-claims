# Technical Documentation

> **⚠️ IMPORTANT**: This is a **DEMONSTRATION SYSTEM** for **EDUCATIONAL PURPOSES ONLY**.  
> **NOT for production use**. See [DISCLAIMERS.md](../DISCLAIMERS.md) for complete information.

## Architecture Decisions

### Domain-Driven Design (DDD) Implementation

This system follows DDD principles (Evans, 2003) to structure the codebase around business domains rather than technical layers.

#### Bounded Contexts

1. **Claim Intake (Core Domain)**
   - The heart of the business
   - Contains Claim aggregate, ClaimSummary value object
   - Handles fact extraction from unstructured data

2. **Policy Management (Supporting Domain)**
   - Provides services to the Core Domain
   - Contains Policy aggregate
   - Handles policy validation

3. **Fraud Assessment (Subdomain)**
   - Important but not core
   - Contains FraudCheckResult value object
   - Provides fraud detection capabilities

#### Domain Patterns

- **Aggregates**: `Claim` and `Policy` are aggregate roots with unique identities (Evans, 2003; Vernon, 2013)
- **Value Objects**: `ClaimSummary`, `FraudCheckResult` are immutable value objects (Evans, 2003)
- **Domain Events**: `ClaimFactsExtracted`, `PolicyValidated`, `FraudScoreCalculated` (Vernon, 2013)
- **Repositories**: Abstract data access, enabling easy testing and swapping implementations (Evans, 2003; Fowler, 2002)
- **Anti-Corruption Layer**: Agents translate external data into domain models (Evans, 2003)

### Model Provider Architecture

The system supports multiple LLM backends through a provider abstraction:

#### Supported Providers

1. **Ollama** (Local Models)
   - Best for: Privacy, cost reduction, offline operation
   - Supports SLMs: Llama 3.2, Mistral 7B, Phi-3 Mini
   - Configuration: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`

2. **OpenAI** (Cloud)
   - Best for: High quality, production use
   - Models: GPT-4o-mini, GPT-4, GPT-3.5
   - Configuration: `OPENAI_API_KEY`, `OPENAI_MODEL`

3. **Anthropic** (Cloud)
   - Best for: High quality, safety-focused
   - Models: Claude 3.5 Sonnet, Claude 3 Opus
   - Configuration: `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`

#### Per-Agent Model Selection

Each agent can use a different model, allowing optimization per task:

```yaml
agents:
  intake:
    model: "llama3.2"
    temperature: 0.3  # Lower for consistent extraction
  policy:
    model: "llama3.2"
    temperature: 0.2  # Very low for validation
  triage:
    model: "mistral:7b"
    temperature: 0.5  # Higher for routing decisions
```

### Agent Patterns

#### Base Agent

All agents inherit from `BaseAgent`, which provides:
- Model provider abstraction
- System prompt management
- Output validation against Pydantic schemas
- Error handling

#### Specialized Agents

1. **Intake Agent**
   - Role: Extract structured facts from unstructured input
   - Input: Unstructured text (email, form, note)
   - Output: `ClaimSummary` value object
   - Event: `ClaimFactsExtracted`

2. **Policy Agent**
   - Role: Validate claims against policies
   - Input: `ClaimSummary`, list of `Policy` objects
   - Output: Validation result
   - Event: `PolicyValidated`

3. **Triage Agent**
   - Role: Route claims to downstream systems
   - Input: `Claim`, `FraudCheckResult`, `PolicyValidated`
   - Output: Routing decision
   - Updates: Claim status

### Event-Driven Architecture

The workflow is orchestrated through domain events (Hohpe & Woolf, 2003):

1. **ClaimFactsExtracted** → Triggers policy validation and fraud assessment
2. **PolicyValidated** → Indicates policy check complete
3. **FraudScoreCalculated** → Triggers triage and routing

#### Event Bus

- Simple in-memory implementation for MVP
- Production: Replace with Redis Streams, RabbitMQ, or Kafka
- Handlers subscribe to event types
- Events are immutable and timestamped

### Repository Pattern

Repositories abstract data access:

- **ClaimRepository**: Manages Claim aggregates
- **PolicyRepository**: Manages Policy aggregates
- **InMemory Implementation**: For testing and development
- **Production**: Replace with database-backed implementations

### Prompt Engineering

System prompts are carefully crafted to make LLMs act as domain experts:

#### Intake Agent Prompt
- Defines role: "Claims Analyst"
- Specifies output format: JSON matching `ClaimSummary` schema
- Enforces domain rules: dates, amounts, validation
- Provides examples

#### Policy Agent Prompt
- Defines role: "Policy Validation Specialist"
- Specifies validation criteria
- Outputs structured validation result

#### Triage Agent Prompt
- Defines role: "Claims Triage Specialist"
- Specifies routing options
- Considers fraud score, policy status, claim complexity

## Model Configuration

### Ollama Setup

1. **Install Ollama**
   ```bash
   # macOS
   brew install ollama
   
   # Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```

2. **Start Ollama Service**
   ```bash
   ollama serve
   ```

3. **Download Models**
   ```bash
   ollama pull llama3.2      # Recommended for quality
   ollama pull llama3.2:3b  # Faster, smaller (SLM)
   ollama pull mistral:7b   # Alternative SLM
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env:
   MODEL_PROVIDER=ollama
   OLLAMA_MODEL=llama3.2
   ```

### SLM Selection Guide

- **Llama 3.2 (8B)**: Best quality, moderate speed
- **Llama 3.2 (3B)**: Good quality, fast (recommended for development)
- **Mistral 7B**: Alternative option, good balance
- **Phi-3 Mini**: Very fast, smaller model

### Model Selection by Task

- **Fact Extraction**: Use larger models (llama3.2) for accuracy
- **Policy Validation**: Can use smaller models (llama3.2:3b) for speed
- **Triage**: Medium models work well (mistral:7b)

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run specific test file
pytest tests/test_intake_agent.py

# Run with coverage
pytest --cov=src tests/
```

### Test Structure

- **Unit Tests**: Test individual components (agents, domain models)
- **Integration Tests**: Test workflow orchestrator end-to-end
- **Mocking**: Use mock model providers to avoid LLM API calls in tests

### Example Test

```python
@pytest.mark.asyncio
async def test_intake_agent_extracts_facts():
    # Mock LLM response
    mock_provider.generate.return_value = expected_json
    
    # Process input
    summary, event = await agent.process(unstructured_input)
    
    # Verify domain model
    assert isinstance(summary, ClaimSummary)
    assert summary.claim_type == "auto"
```

## Development Workflow

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Setup Ollama
./scripts/setup_ollama.sh
```

### 2. Configure Models

Edit `.env` or `config.yaml` to set:
- Model provider (ollama, openai, anthropic)
- Model names
- Agent-specific settings

### 3. Run Application

```python
from src.orchestrator import WorkflowOrchestrator
from src.agents import IntakeAgent, PolicyAgent, TriageAgent
from src.repositories import InMemoryClaimRepository, InMemoryPolicyRepository
from src.agents.model_provider import create_model_provider

# Create model providers
intake_provider = create_model_provider("ollama", "llama3.2")
policy_provider = create_model_provider("ollama", "llama3.2:3b")

# Create agents
intake_agent = IntakeAgent(intake_provider)
policy_agent = PolicyAgent(policy_provider)
triage_agent = TriageAgent(intake_provider)

# Create repositories
claim_repo = InMemoryClaimRepository()
policy_repo = InMemoryPolicyRepository()

# Create orchestrator
orchestrator = WorkflowOrchestrator(
    intake_agent=intake_agent,
    policy_agent=policy_agent,
    triage_agent=triage_agent,
    claim_repository=claim_repo,
    policy_repository=policy_repo,
)

# Process a claim
claim = await orchestrator.process_claim(raw_email_text)
```

## Production Considerations

### Database Integration

Replace in-memory repositories with database-backed implementations:

```python
class PostgreSQLClaimRepository(ClaimRepository):
    async def save(self, claim: Claim):
        # Serialize to database
        # Publish domain events
        pass
```

### Event Bus

Replace in-memory event bus with:
- **Redis Streams**: For distributed systems
- **RabbitMQ**: For reliable messaging
- **Kafka**: For high-throughput event streaming

### Error Handling

- Add retry logic for LLM API calls
- Implement circuit breakers
- Add comprehensive logging
- Monitor model performance

### Security

- Secure API keys (use secrets management)
- Validate all inputs
- Rate limit LLM API calls
- Audit domain events

## Performance Optimization

### Model Selection

- Use smaller models (SLMs) for simple tasks
- Use larger models only when needed
- Cache common policy validations

### Batch Processing

- Process multiple claims in parallel
- Batch LLM API calls when possible

### Caching

- Cache policy data
- Cache fraud assessment results for similar claims
- Use Redis for distributed caching

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve
```

### Model Not Found

```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3.2
```

### JSON Parsing Errors

- Check LLM output format
- Verify system prompt includes JSON schema
- Add retry logic with different temperature

### Domain Invariant Violations

- Review domain model validation rules
- Check input data quality
- Verify LLM output matches schema

## Future Work

> **Note**: This section outlines potential improvements and extensions for educational purposes. This is a demonstration system and these enhancements would require significant additional development.

### Architecture Enhancements

1. **Event Sourcing**
   - Implement full event sourcing for complete audit trail
   - Store all domain events for replay and debugging
   - Enable time-travel debugging and state reconstruction

2. **CQRS (Command Query Responsibility Segregation)**
   - Separate read and write models for better scalability
   - Optimize read models for different query patterns
   - Implement eventual consistency patterns

3. **Distributed Event Bus**
   - Replace in-memory event bus with distributed messaging (Redis, RabbitMQ, Kafka)
   - Enable horizontal scaling of event handlers
   - Support multiple service instances

### Agent Improvements

1. **Multi-Agent Collaboration**
   - Implement agent-to-agent communication
   - Support agent negotiation and consensus
   - Add agent specialization and delegation

2. **Advanced Prompt Engineering**
   - Implement few-shot learning with examples
   - Add chain-of-thought prompting (Wei et al., 2022)
   - Support prompt templates and versioning
   - A/B testing for prompt effectiveness

3. **Agent Monitoring & Observability**
   - Track agent performance metrics
   - Monitor LLM token usage and costs
   - Implement agent health checks
   - Add agent decision logging

### Infrastructure Enhancements

1. **Persistence Layer**
   - Replace in-memory storage with PostgreSQL or MongoDB
   - Implement database migrations
   - Add connection pooling and transaction management
   - Support database replication

2. **Caching Layer**
   - Add Redis for caching frequently accessed data
   - Cache policy lookups and fraud patterns
   - Implement cache invalidation strategies

3. **Search & Indexing**
   - Enhance vector store with full-text search
   - Add Elasticsearch for advanced search capabilities
   - Implement semantic search across claims

### Security & Compliance

1. **Authentication & Authorization**
   - Implement OAuth2/JWT authentication
   - Add role-based access control (RBAC)
   - Support multi-factor authentication

2. **Data Protection**
   - Encrypt sensitive data at rest and in transit
   - Implement data masking for PII
   - Add audit logging for compliance

3. **Compliance Features**
   - HIPAA compliance for health insurance claims
   - GDPR compliance for EU customers
   - SOC 2 compliance for enterprise use
   - Regulatory reporting capabilities

### Testing & Quality

1. **Test Coverage**
   - Increase unit test coverage to >90%
   - Add integration tests for all workflows
   - Implement property-based testing
   - Add performance and load testing

2. **Quality Assurance**
   - Implement continuous integration (CI/CD)
   - Add code quality gates (SonarQube, CodeClimate)
   - Automated security scanning
   - Dependency vulnerability scanning

### Monitoring & Observability

1. **Application Monitoring**
   - Add distributed tracing (Jaeger, Zipkin)
   - Implement structured logging
   - Add metrics collection (Prometheus)
   - Create dashboards (Grafana)

2. **Business Metrics**
   - Track claim processing times
   - Monitor fraud detection accuracy
   - Measure agent performance
   - Track human review patterns

For more detailed future work items, see [docs/architecture.md](architecture.md#future-work).

---

**Note**: These future enhancements are suggestions for educational exploration. For production use, a complete rewrite would be necessary with proper security, compliance, and production-grade infrastructure. See [DISCLAIMERS.md](../DISCLAIMERS.md) for more information.

