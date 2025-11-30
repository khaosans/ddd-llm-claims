# Sequence Diagram - Claim Processing Workflow

> **⚠️ IMPORTANT**: This is a **DEMONSTRATION SYSTEM** for **EDUCATIONAL PURPOSES ONLY**.  
> **NOT for production use**. See [DISCLAIMERS.md](../DISCLAIMERS.md) for complete information.

## Claim Processing Workflow: Complete Lifecycle

This sequence diagram documents the complete claim processing lifecycle, from initial submission through final routing. It illustrates the temporal ordering of component interactions and the transformation of unstructured input into processed, routed claims.

**Processing Overview**: Claims originate as unstructured input (emails, forms, notes) containing necessary information in formats requiring transformation. Through coordinated processing stages, specialized AI agents transform this input into structured, validated domain models. Each processing stage adds value and advances the claim toward resolution.

**Workflow Significance**: Understanding this sequence enables analysis of processing dependencies (precedence constraints), temporal relationships (sequential vs. parallel execution), and decision points (routing logic). This knowledge supports debugging, performance optimization, and system extension.

---

## Understanding the Flow

### How to Read This Diagram

Sequence diagrams represent temporal ordering of interactions. Each horizontal line (lifeline) represents a component or actor. Time flows downward, with earlier interactions appearing above later ones.

**The Components**:
- **User**: The person submitting the claim
- **Orchestrator**: Coordinates the entire workflow
- **Agents**: Specialized AI workers (Intake, Policy, Fraud, Triage)
- **Repositories**: Store and retrieve data (Claim, Policy)
- **LLM**: The AI model that processes requests
- **Downstream Systems**: Final destinations for processed claims

**The Arrows**: 
- Solid arrows (→) show messages or actions
- Dashed arrows (-->>) show returns or responses
- The direction shows who initiates the action

**The Flow**: Read from top to bottom, following the arrows. Notice how each step triggers the next, creating a coordinated workflow.

---

## The Complete Journey: Step by Step

### Phase 1: Claim Creation and Intake

**Processing Overview**: A customer submits a claim through various channels (email, form, note). The system receives this unstructured input and initiates the transformation process.

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant IntakeAgent
    participant LLM as LLM (Ollama/OpenAI)
    participant ClaimRepo as Claim Repository
    participant PolicyAgent
    participant PolicyRepo as Policy Repository
    participant FraudAgent as Fraud Assessment
    participant TriageAgent
    participant Downstream as Downstream Systems

    User->>Orchestrator: Submit Unstructured Claim (Email)
    Orchestrator->>ClaimRepo: Create New Claim
    ClaimRepo-->>Orchestrator: Claim Created
    
    Orchestrator->>IntakeAgent: Extract Facts
    IntakeAgent->>LLM: Send Email + System Prompt
    LLM-->>IntakeAgent: Return JSON (ClaimSummary)
    IntakeAgent->>IntakeAgent: Validate Against Domain Model
    IntakeAgent->>ClaimRepo: Update Claim with Summary
    IntakeAgent->>Orchestrator: Publish ClaimFactsExtracted Event
    
    Orchestrator->>PolicyAgent: Validate Policy
    PolicyAgent->>PolicyRepo: Find Active Policies
    PolicyRepo-->>PolicyAgent: Return Policies
    PolicyAgent->>LLM: Send Claim + Policies
    LLM-->>PolicyAgent: Return Validation Result
    PolicyAgent->>ClaimRepo: Update Claim Status
    PolicyAgent->>Orchestrator: Publish PolicyValidated Event
    
    Orchestrator->>FraudAgent: Assess Fraud Risk
    FraudAgent->>LLM: Analyze Claim for Fraud
    LLM-->>FraudAgent: Return Fraud Score
    FraudAgent->>Orchestrator: Publish FraudScoreCalculated Event
    
    Orchestrator->>TriageAgent: Route Claim
    TriageAgent->>LLM: Determine Routing Decision
    LLM-->>TriageAgent: Return Routing Decision
    TriageAgent->>ClaimRepo: Update Claim Status
    TriageAgent->>Downstream: Dispatch to Queue
    
    Downstream-->>User: Claim Processed
```

**What Happens**:

1. **User Submits Claim**: Processing begins when a user submits unstructured input (email, form, or note) to the system.

2. **Orchestrator Creates Claim**: The Workflow Orchestrator receives the input and creates a new Claim aggregate in the repository. The claim is initialized in DRAFT status.

3. **Intake Agent Extracts Facts**: The Orchestrator invokes the Intake Agent to extract structured facts from the unstructured input. The agent applies prompt engineering techniques to identify and extract key information.

4. **LLM Processing**: The Intake Agent sends the unstructured input plus a carefully crafted system prompt to the LLM. The prompt tells the LLM how to behave—like giving detailed instructions to a new employee.

5. **Structured Output**: The LLM returns structured JSON containing the extracted facts (claim type, date, location, amount, description). This is like the analyst writing a clean summary report.

6. **Validation**: The Intake Agent validates the LLM output against the domain model schema, ensuring compliance with business rules and domain invariants.

7. **Claim Updated**: The validated ClaimSummary is stored in the repository, updating the claim with structured information.

8. **Domain Event Published**: The Intake Agent publishes a `ClaimFactsExtracted` domain event. This is like sending a memo to notify other departments that the first step is complete.

**Why This Matters**: This phase transforms chaos into order. Unstructured input becomes structured data that the system can process. The event-driven approach means the next phase can start as soon as facts are extracted, without the Intake Agent needing to know what happens next.

---

### Phase 2: Policy Validation

**Policy Validation Phase**: With structured claim facts extracted, the system verifies that the claim is covered by an active insurance policy. This validation ensures policy coverage before claim processing proceeds.

**What Happens**:

1. **Event Triggers Validation**: The `ClaimFactsExtracted` event wakes up the Orchestrator, which tells the Policy Agent to start validation.

2. **Policy Lookup**: The Policy Agent queries the Policy Repository to find active policies for the claimant. This is like looking up someone's insurance in a database.

3. **Policies Retrieved**: The repository returns relevant policies, including coverage details, effective dates, and terms.

4. **LLM Validation**: The Policy Agent sends claim details and policy information to the LLM, requesting coverage determination. The LLM applies policy validation logic to compare claim details against policy terms.

5. **Validation Result**: The LLM returns a validation result—covered, not covered, or needs review. This decision is based on policy terms, coverage dates, and claim details.

6. **Claim Status Updated**: The Policy Agent updates the claim status in the repository based on the validation result.

7. **Domain Event Published**: The Policy Agent publishes a `PolicyValidated` event, notifying the system that policy validation is complete.

**Why This Matters**: Policy validation ensures that only valid claims proceed. Invalid claims can be rejected early, saving processing time and resources. The event-driven approach means fraud assessment can start as soon as validation completes.

---

### Phase 3: Fraud Assessment

**Fraud Assessment Phase**: Following policy validation, the system assesses fraud risk. This analysis identifies suspicious patterns and anomalies before claim processing proceeds.

**What Happens**:

1. **Event Triggers Assessment**: The `PolicyValidated` event (or the original `ClaimFactsExtracted` event) triggers fraud assessment. The Orchestrator tells the Fraud Agent to assess risk.

2. **LLM Analysis**: The Fraud Agent sends claim details to the LLM, requesting pattern analysis, anomaly detection, and risk indicator evaluation. The LLM applies fraud detection algorithms to identify suspicious patterns.

3. **Fraud Score**: The LLM returns a fraud score and risk level (low, medium, high), along with reasons for the assessment. This might include patterns like unusual claim amounts, suspicious timing, or inconsistent details.

4. **Domain Event Published**: The Fraud Agent publishes a `FraudScoreCalculated` event with the assessment results.

**Why This Matters**: Fraud assessment helps route claims appropriately. High-risk claims go to fraud investigation, medium-risk claims get extra review, and low-risk claims can proceed more quickly. This protects the business while maintaining efficiency.

---

### Phase 4: Triage and Routing

**Triage and Routing Phase**: With complete information (structured facts, policy validation results, fraud assessment), the system makes routing decisions. The Triage Agent evaluates all available data to determine appropriate downstream processing.

**What Happens**:

1. **Event Triggers Triage**: The `FraudScoreCalculated` event (and potentially `PolicyValidated`) triggers the Triage Agent to make a routing decision.

2. **LLM Decision**: The Triage Agent sends all available information (claim facts, policy status, fraud score) to the LLM, asking it to determine the best routing destination.

3. **Routing Decision**: The LLM returns a routing decision based on:
   - Policy validation status (valid, invalid, needs review)
   - Fraud risk level (low, medium, high)
   - Claim complexity (simple, complex)
   - Business rules

4. **Claim Status Updated**: The Triage Agent updates the claim status in the repository with the routing decision.

5. **Dispatch**: The claim is dispatched to the appropriate downstream system:
   - **Human Adjudicator Queue**: For complex, high-risk, or ambiguous claims requiring human judgment
   - **Automated Processing System**: For simple, low-risk, valid claims that can be processed automatically
   - **Fraud Investigation System**: For suspicious or high-risk claims requiring specialized investigation
   - **Specialist Review Queue**: For claims requiring domain expertise (medical, legal, engineering)
   - **Rejection Handler**: For invalid, ineligible, or non-covered claims

**Integration Patterns**: Downstream systems are integrated using various patterns:
- **Message Queue Pattern** (Hohpe & Woolf, 2003, pp. 102-115): For asynchronous dispatch to human review and fraud investigation queues
- **REST API** (Newman, 2021): For synchronous integration with automated processing systems
- **Event-Driven Architecture** (Hohpe & Woolf, 2003, pp. 516-530): Domain events trigger downstream system integration
- **Message Router Pattern** (Hohpe & Woolf, 2003, pp. 230-237): The Triage Agent acts as a message router, directing claims to appropriate destinations

**What Happens After Dispatch**: Once a claim reaches a downstream system:
- **Human Adjudicator Queue**: Claims are queued with priority, human reviewers pull claims, make decisions, and update claim status
- **Automated Processing**: System validates final rules, calculates settlement, triggers payment, and sends notifications
- **Fraud Investigation**: Specialized investigators receive prioritized alerts, perform deep analysis, and make decisions
- **Rejection Handler**: Claims are immediately rejected, customer notifications are sent, and audit logs are created

**Why This Matters**: Intelligent routing ensures claims go to the right place. Simple claims get fast, automated processing. Complex claims get human attention. Suspicious claims get investigation. This balances efficiency, accuracy, and risk management. The integration patterns demonstrate how to maintain bounded context boundaries (Evans, 2003) while enabling system integration.

**⚠️ Note**: This demonstration system simulates dispatch but doesn't actually integrate with real downstream systems. In production, this would require message queue infrastructure (RabbitMQ, Kafka), API gateways, service discovery, and monitoring. See [Architecture Documentation](architecture.md#downstream-systems-integration-and-routing) for complete details on what's included and what's missing.

---

## Understanding the Flow: Key Patterns

### Event-Driven Architecture

Notice how components don't directly call each other—they communicate through domain events. When the Intake Agent finishes, it publishes `ClaimFactsExtracted`, and the Orchestrator listens for this event to trigger the next step. This event-driven approach (Hohpe & Woolf, 2003) keeps components loosely coupled—they don't need to know about each other directly.

**Benefits**:
- **Loose Coupling**: Components are independent and can be modified without affecting others
- **Flexibility**: New components can listen to events without modifying existing code
- **Scalability**: Events can be processed asynchronously and in parallel
- **Testability**: Components can be tested independently by publishing test events

### Domain Events as Coordination Mechanism

Domain events (Vernon, 2013) serve as the coordination mechanism between components. Each event represents something important that happened in the domain:
- `ClaimFactsExtracted`: Facts were successfully extracted
- `PolicyValidated`: Policy validation completed
- `FraudScoreCalculated`: Fraud assessment finished

These events enable the workflow to progress without components needing direct knowledge of each other.

### Agent Pattern: AI as Domain Expert

Each agent uses LLMs to act as a domain expert:
- **Intake Agent**: Extracts structured facts from unstructured input using LLM-based processing
- **Policy Agent**: Validates claim coverage against active policies
- **Fraud Agent**: Assesses fraud risk through pattern analysis and anomaly detection
- **Triage Agent**: Makes routing decisions based on policy status, fraud score, and claim complexity

This pattern (Brown et al., 2020) enables the system to handle unstructured input intelligently while maintaining clean domain models.

### Anti-Corruption Layer

The agents act as Anti-Corruption Layers (Evans, 2003), protecting the clean domain model from messy external data. They translate unstructured input into structured domain objects, validate the results, and ensure data quality before it enters the domain.

---

## What Happens When: Decision Points and Alternatives

The sequence diagram shows the main "happy path," but the system handles many scenarios:

### Alternative Paths

**Invalid Policy**:
- If policy validation fails, the claim might be rejected immediately
- Or it might go to a review queue for human verification

**High Fraud Risk**:
- High-risk claims go to fraud investigation
- They don't proceed to normal processing

**Complex Claims**:
- Complex claims (large amounts, unusual circumstances) go to human review
- Simple claims can be processed automatically

**Policy Ambiguity**:
- If policy terms are unclear, the claim goes to human review
- A human expert makes the final decision

### Error Handling

If any step fails:
- Errors are logged and the claim status is updated
- The claim might go to an error queue for manual review
- Retry logic can attempt to reprocess failed steps
- Human reviewers can intervene when automation fails

---

## Key Takeaways

1. **Event-Driven Architecture**: Each processing stage publishes domain events that trigger subsequent stages, maintaining loose coupling between components (Hohpe & Woolf, 2003).

2. **Agents Transform Data**: AI agents act as domain experts, transforming unstructured input into structured, validated information (Brown et al., 2020).

3. **Validation Happens at Each Step**: Facts are validated, policies are checked, and fraud is assessed before routing decisions are made.

4. **Intelligent Routing**: The system makes intelligent routing decisions based on all available information, balancing efficiency and risk.

5. **Human-in-the-Loop**: Complex, high-risk, or ambiguous claims go to human review, combining AI speed with human judgment.

---

## References

All concepts and patterns referenced in this document are grounded in established research:

- **Domain-Driven Design**: Evans, E. (2003). *Domain-driven design: Tackling complexity in the heart of software*. Addison-Wesley Professional.
- **Domain Events**: Vernon, V. (2013). *Implementing domain-driven design*. Addison-Wesley Professional.
- **Event-Driven Architecture**: Hohpe, G., & Woolf, B. (2003). *Enterprise integration patterns: Designing, building, and deploying messaging solutions*. Addison-Wesley Professional.
- **Large Language Models**: Brown, T., et al. (2020). Language models are few-shot learners. *Advances in neural information processing systems*, 33, 1877-1901.

For complete citations and references, see [docs/REFERENCES.md](REFERENCES.md).

---

**Remember**: This is an **educational demonstration system**. The sequence shows how claims would be processed, but a production system would require additional features like persistence, monitoring, security, and compliance. See [DISCLAIMERS.md](../DISCLAIMERS.md) for important limitations.
