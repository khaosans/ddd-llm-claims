# Technical Documentation

> **⚠️ IMPORTANT**: This is a **DEMONSTRATION SYSTEM** for **EDUCATIONAL PURPOSES ONLY**.  
> **NOT for production use**. See [DISCLAIMERS.md](../DISCLAIMERS.md) for complete information.

## Architecture Decisions

### Domain-Driven Design (DDD) Implementation

**Why DDD?** This system follows DDD principles (Evans, 2003) to structure the codebase around business domains rather than technical layers. We chose DDD because:

1. **Business Alignment**: Insurance claims processing is a complex business domain with many rules and relationships. DDD helps organize code to match how the business actually works, making it easier for both developers and domain experts to understand (Evans, 2003).

2. **Maintainability**: As requirements change (new claim types, policy rules, fraud patterns), code organized by domain is easier to locate and modify. Changes to fraud detection don't affect policy validation code.

3. **Testability**: Domain logic separated from infrastructure makes it easier to test business rules without mocking databases or external services.

4. **Scalability**: Bounded contexts can evolve independently, allowing different parts of the system to scale or change at different rates.

This approach organizes code around business concepts, making the system more maintainable and aligned with business needs (Evans, 2003; Vernon, 2013).

#### Bounded Contexts

**Why Separate Bounded Contexts?** We separated the system into three bounded contexts because each has different rules, responsibilities, and rates of change. This separation prevents one context's changes from breaking another (Evans, 2003, pp. 335-365).

1. **Claim Intake (Core Domain)**
   - **Why it's Core**: This is the heart of the business—processing claims is what the system exists to do
   - **Why Separate**: Claim processing rules change frequently (new claim types, extraction requirements)
   - Contains Claim aggregate, ClaimSummary value object
   - Handles fact extraction from unstructured data

2. **Policy Management (Supporting Domain)**
   - **Why it's Supporting**: Policies support claim processing but aren't the core business
   - **Why Separate**: Policy rules are relatively stable and can be maintained independently
   - Provides services to the Core Domain
   - Contains Policy aggregate
   - Handles policy validation

3. **Fraud Assessment (Subdomain)**
   - **Why it's a Subdomain**: Important for business but not the core value proposition
   - **Why Separate**: Fraud detection algorithms evolve independently and may be replaced with different ML models
   - Important but not core
   - Contains FraudCheckResult value object
   - Provides fraud detection capabilities

#### Domain Patterns

**Why These Patterns?** Each pattern solves a specific problem in managing complex business logic:

- **Aggregates**: `Claim` and `Policy` are aggregate roots with unique identities (Evans, 2003; Vernon, 2013)
  - **Why**: Aggregates define consistency boundaries. All changes to a Claim must go through the Claim aggregate, ensuring business rules are always enforced. This prevents invalid states (e.g., a claim with extracted facts but no summary).

- **Value Objects**: `ClaimSummary`, `FraudCheckResult` are immutable value objects (Evans, 2003)
  - **Why**: Immutability prevents accidental modification and ensures data integrity. Once a ClaimSummary is created, it can't be changed—you create a new one. This eliminates entire classes of bugs and makes the code easier to reason about (Evans, 2003, pp. 97-124).

- **Domain Events**: `ClaimFactsExtracted`, `PolicyValidated`, `FraudScoreCalculated` (Vernon, 2013)
  - **Why**: Events enable loose coupling between components. The Intake Agent doesn't need to know about Policy validation—it just publishes an event. This makes the system flexible: we can add new event handlers without modifying existing code (Vernon, 2013, pp. 381-420).

- **Repositories**: Abstract data access, enabling easy testing and swapping implementations (Evans, 2003; Fowler, 2002)
  - **Why**: Repositories keep domain logic independent of persistence. We can test with in-memory repositories, then swap to PostgreSQL in production without changing domain code. This separation of concerns makes the system more testable and maintainable (Evans, 2003, pp. 151-170).

- **Anti-Corruption Layer**: Agents translate external data into domain models (Evans, 2003)
  - **Why**: LLM outputs are unpredictable and may not match our domain model. Agents validate and transform this external data before it enters our clean domain, protecting business logic from bad data. This is especially important with AI systems where outputs can vary (Evans, 2003, pp. 365-380).

### Model Provider Architecture

**Why Provider Abstraction?** The system supports multiple LLM backends through a provider abstraction because:

1. **Flexibility**: Different use cases need different models. Local development might use Ollama for cost/privacy, while production might use OpenAI for quality.

2. **Vendor Independence**: We're not locked into one LLM provider. If a better model or pricing becomes available, we can switch without rewriting agent code.

3. **Testing**: Mock providers allow testing without making expensive API calls or requiring internet connectivity.

4. **Cost Optimization**: We can use smaller, cheaper models for simple tasks and larger models only when needed.

The abstraction layer isolates agent code from provider-specific details, making the system more maintainable and flexible.

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

**Why Per-Agent Models?** Each agent can use a different model, allowing optimization per task. This design decision was made because:

1. **Task-Specific Optimization**: Different tasks have different requirements:
   - **Fact Extraction** (Intake Agent): Needs accuracy, so we use larger models (llama3.2)
   - **Policy Validation** (Policy Agent): Needs consistency, so we use smaller models with low temperature (llama3.2:3b, temp=0.2)
   - **Triage** (Triage Agent): Needs reasoning, so we use medium models with higher temperature (mistral:7b, temp=0.5)

2. **Cost Efficiency**: Using smaller models for simple tasks reduces costs. A 3B model is sufficient for policy validation but not for complex fact extraction.

3. **Performance**: Smaller models are faster, improving response times for high-frequency operations like policy validation.

4. **Flexibility**: Teams can experiment with different models per agent to find optimal configurations.

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

**Why Event-Driven?** The workflow is orchestrated through domain events (Hohpe & Woolf, 2003) because:

1. **Loose Coupling**: Components don't directly depend on each other. The Intake Agent doesn't know about Policy validation—it just publishes an event. This makes the system easier to modify and test (Hohpe & Woolf, 2003, pp. 516-530).

2. **Scalability**: Events can be processed asynchronously. Multiple claims can be processed in parallel without blocking each other.

3. **Extensibility**: New features can listen to existing events without modifying existing code. Want to send an email when facts are extracted? Just add an event handler.

4. **Auditability**: Events provide a complete history of what happened, making debugging and compliance easier.

5. **Resilience**: If one component fails, others can continue processing. Failed events can be retried without affecting the entire workflow.

The workflow progression:

1. **ClaimFactsExtracted** → Triggers policy validation and fraud assessment
2. **PolicyValidated** → Indicates policy check complete
3. **FraudScoreCalculated** → Triggers triage and routing

#### Event Bus

**Why In-Memory for MVP?** We chose a simple in-memory implementation for the MVP because:

1. **Simplicity**: No infrastructure setup required—works immediately for demos and education
2. **Sufficient for Learning**: Demonstrates event-driven concepts without complexity
3. **Easy Testing**: In-memory events are easier to test and reason about

**Why Replace for Production?** Production systems need:
- **Persistence**: In-memory events are lost on restart. Production needs Redis Streams, RabbitMQ, or Kafka for durability
- **Distributed Processing**: Multiple service instances need shared event bus
- **Reliability**: Message brokers provide delivery guarantees, retries, and dead-letter queues
- **Ordering**: Some events must be processed in order (message brokers provide ordering guarantees)

- Handlers subscribe to event types
- Events are immutable and timestamped

### Repository Pattern

**Why Repositories?** Repositories abstract data access because:

1. **Domain Independence**: Domain models don't know about databases, SQL, or persistence details. This keeps business logic pure and testable (Evans, 2003, pp. 151-170).

2. **Testability**: In-memory repositories make testing fast and simple. We can test business logic without setting up databases or mocking complex ORMs.

3. **Flexibility**: We can swap implementations (in-memory → PostgreSQL → MongoDB) without changing domain code. This is especially useful when requirements change.

4. **Abstraction**: Repository interfaces define what operations are needed, not how they're implemented. This makes the domain's data needs explicit.

Repositories abstract data access:

- **ClaimRepository**: Manages Claim aggregates
- **PolicyRepository**: Manages Policy aggregates
- **InMemory Implementation**: For testing and development
- **Production**: Replace with database-backed implementations

### Prompt Engineering

**Why Structured Prompts?** System prompts are carefully crafted to make LLMs act as domain experts (Brown et al., 2020). This follows prompt engineering best practices where structured prompts guide LLM behavior. We use structured prompts because:

1. **Consistency**: Well-defined prompts produce more consistent outputs, reducing the need for retries and error handling.

2. **Role Definition**: Prompts define the agent's role (e.g., "Claims Analyst"), helping the LLM understand context and expectations.

3. **Output Format**: Specifying JSON schemas in prompts helps ensure outputs match our domain models, reducing validation failures.

4. **Domain Rules**: Prompts can encode business rules (e.g., "amounts must be non-negative"), providing guardrails for LLM behavior.

5. **Few-Shot Learning**: Including examples in prompts teaches the LLM the desired format and behavior without fine-tuning (Brown et al., 2020).

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
- Implement circuit breakers (Hohpe & Woolf, 2003, pp. 420-430)
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
   - Implement full event sourcing for complete audit trail (Young, 2016)
   - Store all domain events for replay and debugging
   - Enable time-travel debugging and state reconstruction

2. **CQRS (Command Query Responsibility Segregation)**
   - Separate read and write models for better scalability (Fowler, 2011)
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
   - Implement few-shot learning with examples (Brown et al., 2020)
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

