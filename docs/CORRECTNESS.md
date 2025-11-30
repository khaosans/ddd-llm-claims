# Correctness Verification

This document describes the critical domain invariants, correctness guarantees, and verification approaches used in this system.

## Domain Invariants

Domain invariants are business rules that must always be true (Evans, 2003). These are enforced at the domain model level to ensure correctness. Invariants are a core concept in Domain-Driven Design, representing constraints that must hold true for the domain model to be valid (Evans, 2003, pp. 125-150).

### 1. Claim Amount Invariant

**Invariant**: Claim amount must be non-negative.

**Location**: `src/domain/claim/claim_summary.py`

**Enforcement**:
```python
@field_validator('claimed_amount')
@classmethod
def validate_amount(cls, v: Decimal) -> Decimal:
    if v < 0:
        raise ValueError("Claim amount cannot be negative")
    return v
```

**Verification**: Tested in `tests/test_domain_models.py::test_claim_summary_value_object`

**Proof**: By construction - the validator rejects any negative amount at Value Object creation time.

### 2. Incident Date Invariant

**Invariant**: Incident date cannot be in the future.

**Location**: `src/domain/claim/claim_summary.py`

**Enforcement**:
```python
@field_validator('incident_date')
@classmethod
def validate_incident_date(cls, v: datetime) -> datetime:
    if v > datetime.utcnow():
        raise ValueError("Incident date cannot be in the future")
    return v
```

**Verification**: Tested in `tests/test_domain_models.py::test_claim_summary_value_object`

**Proof**: Temporal validation ensures business rule compliance.

### 3. Claim Status Transition Invariant

**Invariant**: Claims can only transition through valid states.

**Location**: `src/domain/claim/claim.py`

**Enforcement**:
- Facts can only be extracted when status is DRAFT
- Policy can only be validated when status is FACTS_EXTRACTED
- Triage can only occur when status is POLICY_VALIDATED

**Verification**: Tested in `tests/test_domain_models.py::test_claim_status_transitions`

**Proof**: State machine logic enforces valid transitions only.

### 4. Value Object Immutability

**Invariant**: Value Objects (ClaimSummary, FraudCheckResult) are immutable (Evans, 2003, pp. 97-124).

**Location**: All Value Object classes

**Enforcement**:
```python
class Config:
    frozen = True  # Pydantic frozen=True enforces immutability
```

**Verification**: Pydantic's frozen=True prevents modification after creation.

**Proof**: By construction - frozen objects cannot be modified.

### 5. Aggregate Consistency

**Invariant**: Aggregate roots maintain consistency within their boundaries (Evans, 2003, pp. 125-150; Vernon, 2013, pp. 345-380).

**Location**: `src/domain/claim/claim.py`, `src/domain/policy/policy.py`

**Enforcement**:
- Claim aggregate controls access to ClaimSummary
- Only Claim aggregate can modify its own state
- Domain events are published when state changes

**Verification**: Tested through integration tests and domain logic tests.

**Proof**: Encapsulation ensures all modifications go through aggregate root methods.

## Pattern Correctness

### Repository Pattern

**Correctness**: Repository abstraction maintains domain model independence from persistence (Evans, 2003, pp. 151-170; Fowler, 2002, pp. 322-334).

**Verification**: 
- In-memory implementation for testing
- Interface allows swapping implementations
- Domain model has no persistence dependencies

**Proof**: Repository interface (`ClaimRepository`, `PolicyRepository`) abstracts data access, keeping domain model clean.

### Anti-Corruption Layer

**Correctness**: Agents properly translate external data into domain models (Evans, 2003, pp. 365-380). This pattern protects the domain model from external system changes and ensures data quality.

**Verification**:
- Intake Agent validates LLM output against ClaimSummary schema
- Invalid output is rejected
- Domain invariants are enforced

**Proof**: Validation in `BaseAgent.validate_output()` ensures external data conforms to domain model.

### Event-Driven Architecture

**Correctness**: Domain events enable loose coupling without data loss (Vernon, 2013, pp. 381-420; Hohpe & Woolf, 2003, pp. 516-530). Events represent immutable facts about domain occurrences and enable asynchronous processing.

**Verification**:
- Events are immutable
- Event handlers are registered correctly
- Event ordering is preserved

**Proof**: Event bus implementation ensures events are published and handled correctly.

## Runtime Assertions

Critical paths include runtime assertions for additional safety:

### Claim Fact Extraction

```python
def extract_facts(self, summary: ClaimSummary) -> ClaimFactsExtracted:
    # Domain Invariant: Can only extract facts if in DRAFT status
    if self.status != ClaimStatus.DRAFT:
        raise ValueError(f"Cannot extract facts: claim is in {self.status} status")
    # ... rest of method
```

### Policy Validation

```python
def validate_policy(self, is_valid: bool) -> None:
    if self.status != ClaimStatus.FACTS_EXTRACTED:
        raise ValueError(f"Cannot validate policy: claim is in {self.status} status")
    # ... rest of method
```

## Test Coverage

### Unit Tests

- Domain model validation tests
- Invariant preservation tests
- State transition tests
- Value object immutability tests

**Location**: `tests/test_domain_models.py`, `tests/test_intake_agent.py`

### Integration Tests

- End-to-end workflow tests
- Event handling tests
- Repository pattern tests

**Location**: `tests/` directory

## Verification Checklist

- [x] Domain invariants documented
- [x] Invariants enforced in code
- [x] Runtime assertions added
- [x] Tests verify invariants
- [x] Pattern correctness verified
- [x] Value object immutability enforced
- [x] Aggregate consistency maintained
- [x] Event-driven correctness verified

## Known Limitations

1. **Formal Proofs**: This document provides practical verification, not formal mathematical proofs. For academic use, formal verification could be added.

2. **Concurrency**: Current implementation assumes single-threaded execution. For production, additional concurrency controls would be needed.

3. **Event Ordering**: In-memory event bus doesn't guarantee ordering across distributed systems. Production would need message broker with ordering guarantees.

4. **Persistence**: In-memory repositories don't persist data. Production would need database-backed implementations.

## References

- Evans, E. (2003). *Domain-driven design: Tackling complexity in the heart of software*. Addison-Wesley Professional.
- Vernon, V. (2013). *Implementing domain-driven design*. Addison-Wesley Professional.

For complete references, see [REFERENCES.md](REFERENCES.md).

