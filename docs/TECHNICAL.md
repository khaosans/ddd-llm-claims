# Technical Documentation

> **⚠️ IMPORTANT**: This is a **DEMONSTRATION SYSTEM** for **EDUCATIONAL PURPOSES ONLY**.  
> **NOT for production use**. See [DISCLAIMERS.md](../DISCLAIMERS.md) for complete information.

## Architecture Decisions

### Domain-Driven Design (DDD) Implementation

**Why DDD?** This system follows DDD principles (Evans, 2003) to structure code around business domains rather than technical layers. DDD provides:

1. **Business Alignment**: Organizes code to match how the business works—easier for developers and domain experts to understand (Evans, 2003)
2. **Maintainability**: Domain-organized code is easier to locate and modify—changes to fraud detection don't affect policy validation
3. **Testability**: Domain logic separated from infrastructure—test business rules without mocking databases
4. **Scalability**: Bounded contexts evolve independently—different parts scale at different rates

This approach makes the system more maintainable and aligned with business needs (Evans, 2003; Vernon, 2013).

#### Bounded Contexts

**Why Separate Bounded Contexts?** Each context has different rules, responsibilities, and change rates. Separation prevents one context's changes from breaking another (Evans, 2003, pp. 335-365).

1. **Claim Intake (Core Domain)**
   - **Core**: The heart of the business—processing claims
   - **Separate**: Rules change frequently (new claim types, extraction requirements)
   - Contains: Claim aggregate, ClaimSummary value object
   - Handles: Fact extraction from unstructured data

2. **Policy Management (Supporting Domain)**
   - **Supporting**: Enables claim processing but isn't core business
   - **Separate**: Rules are relatively stable, maintained independently
   - Contains: Policy aggregate
   - Handles: Policy validation

3. **Fraud Assessment (Subdomain)**
   - **Subdomain**: Important but not core value proposition
   - **Separate**: Algorithms evolve independently, may be replaced with different ML models
   - Contains: FraudCheckResult value object
   - Handles: Fraud detection

#### Domain Patterns

**Why These Patterns?** Each pattern solves a specific problem in managing complex business logic:

- **Aggregates**: `Claim` and `Policy` are aggregate roots with unique identities (Evans, 2003; Vernon, 2013)
  - **Why**: Define consistency boundaries—all changes go through the aggregate root, ensuring business rules are enforced. Prevents invalid states (e.g., claim with extracted facts but no summary).

- **Value Objects**: `ClaimSummary`, `FraudCheckResult` are immutable value objects (Evans, 2003)
  - **Why**: Immutability prevents accidental modification and ensures data integrity. Once created, can't be changed—create a new one instead. Eliminates entire classes of bugs (Evans, 2003, pp. 97-124).

- **Domain Events**: `ClaimFactsExtracted`, `PolicyValidated`, `FraudScoreCalculated` (Vernon, 2013)
  - **Why**: Enable loose coupling—Intake Agent doesn't know about Policy validation, just publishes events. System is flexible: add new handlers without modifying existing code (Vernon, 2013, pp. 381-420).

- **Repositories**: Abstract data access, enabling easy testing and swapping implementations (Evans, 2003; Fowler, 2002)
  - **Why**: Keep domain logic independent of persistence. Test with in-memory repositories, swap to PostgreSQL in production without domain changes. Separation improves testability and maintainability (Evans, 2003, pp. 151-170).

- **Anti-Corruption Layer**: Agents translate external data into domain models (Evans, 2003)
  - **Why**: LLM outputs are unpredictable. Agents validate and transform data before domain entry, protecting business logic. Critical for AI systems where outputs vary (Evans, 2003, pp. 365-380).

### Model Provider Architecture

**Why Provider Abstraction?** Multiple LLM backends through abstraction enable:
- **Flexibility**: Different models for different use cases (Ollama for dev, OpenAI for production)
- **Vendor Independence**: Switch providers without rewriting agent code
- **Testing**: Mock providers enable testing without API calls or internet
- **Cost Optimization**: Use smaller models for simple tasks, larger models when needed

The abstraction isolates agent code from provider details, improving maintainability and flexibility.

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

**Why Per-Agent Models?** Each agent uses a different model for task-specific optimization:
- **Fact Extraction** (Intake): Needs accuracy → larger models (llama3.2)
- **Policy Validation** (Policy): Needs consistency → smaller models, low temperature (llama3.2:3b, temp=0.2)
- **Triage** (Routing): Needs reasoning → medium models, higher temperature (mistral:7b, temp=0.5)

**Benefits**: Cost efficiency (smaller models for simple tasks), performance (faster responses), flexibility (experiment with configurations).

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

**Why Event-Driven?** Domain events (Hohpe & Woolf, 2003) orchestrate the workflow because they enable:
- **Loose Coupling**: Components don't directly depend on each other—Intake Agent doesn't know about Policy validation (Hohpe & Woolf, 2003, pp. 516-530)
- **Scalability**: Asynchronous processing enables parallel claim processing
- **Extensibility**: New features listen to existing events without code changes
- **Auditability**: Complete history for debugging and compliance
- **Resilience**: Component failures don't cascade—failed events can be retried

The workflow progression:

1. **ClaimFactsExtracted** → Triggers policy validation and fraud assessment
2. **PolicyValidated** → Indicates policy check complete
3. **FraudScoreCalculated** → Triggers triage and routing

#### Event Bus

**Why In-Memory for MVP?** Simple in-memory implementation chosen because:
- **Simplicity**: No infrastructure setup—works immediately for demos
- **Sufficient for Learning**: Demonstrates event-driven concepts without complexity
- **Easy Testing**: In-memory events are easier to test and reason about

**Why Replace for Production?** Production needs:
- **Persistence**: Redis Streams, RabbitMQ, or Kafka for durability (in-memory lost on restart)
- **Distributed Processing**: Shared event bus for multiple service instances
- **Reliability**: Delivery guarantees, retries, dead-letter queues
- **Ordering**: Message brokers provide ordering guarantees for sequential events

- Handlers subscribe to event types
- Events are immutable and timestamped

### Repository Pattern

**Why Repositories?** Repositories abstract data access because they provide:
- **Domain Independence**: Domain models don't know about databases—business logic stays pure and testable (Evans, 2003, pp. 151-170)
- **Testability**: In-memory repositories make testing fast—no database setup or ORM mocking
- **Flexibility**: Swap implementations (in-memory → PostgreSQL → MongoDB) without domain changes
- **Abstraction**: Interfaces define what's needed, not how—makes domain data needs explicit

Repositories abstract data access:

- **ClaimRepository**: Manages Claim aggregates
- **PolicyRepository**: Manages Policy aggregates
- **InMemory Implementation**: For testing and development
- **Production**: Replace with database-backed implementations

### Prompt Engineering

**Why Structured Prompts?** Carefully crafted prompts make LLMs act as domain experts (Brown et al., 2020). Structured prompts provide:
- **Consistency**: Well-defined prompts produce consistent outputs—reduces retries and errors
- **Role Definition**: Define agent roles (e.g., "Claims Analyst") for context and expectations
- **Output Format**: JSON schemas in prompts ensure outputs match domain models
- **Domain Rules**: Encode business rules (e.g., "amounts must be non-negative") as guardrails
- **Few-Shot Learning**: Examples teach desired format without fine-tuning (Brown et al., 2020)

**Advanced Prompt Engineering Techniques**: The system can incorporate advanced prompting strategies:
- **Instruction Following**: Training models to follow instructions (Ouyang et al., 2022)
- **Chain-of-Thought**: Eliciting reasoning through step-by-step prompts (Wei et al., 2022)
- **Zero-Shot Reasoning**: Enabling complex reasoning without examples (Kojima et al., 2022)
- **Least-to-Most Prompting**: Breaking complex problems into simpler subproblems (Zhou et al., 2022)
- **Prompt Patterns**: Reusable patterns for common LLM tasks (White et al., 2023)

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

- Add retry logic for LLM API calls with exponential backoff
- Implement circuit breakers (Hohpe & Woolf, 2003, pp. 420-430; Nygard, 2007; Fowler, 2014)
- Add comprehensive logging
- Monitor model performance
- Graceful degradation patterns (Nygard, 2007)

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
   - Implement full event sourcing for complete audit trail (Young, 2016; Fowler, 2005)
   - Store all domain events for replay and debugging
   - Enable time-travel debugging and state reconstruction
   - Event sourcing patterns for data-intensive applications (Kleppmann, 2017)

2. **CQRS (Command Query Responsibility Segregation)**
   - Separate read and write models for better scalability (Fowler, 2011; Vernon, 2013)
   - Optimize read models for different query patterns
   - Implement eventual consistency patterns
   - CQRS Journey patterns and practices (Young & Betts, 2010; Betts et al., 2013)

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
   - Implement few-shot learning with examples (Brown et al., 2020)
   - Add chain-of-thought prompting (Wei et al., 2022)
   - Support instruction following patterns (Ouyang et al., 2022)
   - Implement zero-shot reasoning (Kojima et al., 2022)
   - Apply least-to-most prompting for complex tasks (Zhou et al., 2022)
   - Use prompt patterns catalog (White et al., 2023)
   - Support prompt templates and versioning
   - A/B testing for prompt effectiveness

3. **Agent Monitoring & Observability**
   - Track agent performance metrics
   - Monitor LLM token usage and costs
   - Implement agent health checks
   - Add agent decision logging
   - Distributed tracing for agent workflows (Sigelman et al., 2010; OpenTelemetry Project, n.d.)
   - Observability engineering practices (Charity & Swaminathan, 2021)

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

