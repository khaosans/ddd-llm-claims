# Sequence Diagram - Claim Processing Workflow

This diagram shows the complete flow of processing a claim from unstructured input to final routing.

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

## Flow Explanation

1. **User submits claim** → Unstructured email/form data
2. **Orchestrator creates claim** → New Claim aggregate in DRAFT status
3. **Intake Agent extracts facts** → LLM processes unstructured data → Returns structured ClaimSummary
4. **Policy Agent validates** → Checks against active policies → Updates claim status
5. **Fraud Agent assesses** → Calculates fraud risk score
6. **Triage Agent routes** → Determines final destination → Dispatches to downstream systems

