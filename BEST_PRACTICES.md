# Best Practices Guide

This guide outlines best practices for using, extending, and learning from this educational system.

## Using This System

### ✅ Do's

1. **Read Documentation First**
   - Start with README.md
   - Review DISCLAIMERS.md
   - Study TECHNICAL.md for architecture
   - Check REFERENCES.md for research

2. **Understand Before Modifying**
   - Study the domain models
   - Understand DDD patterns used
   - Review event flow
   - Examine test cases

3. **Use Demo Mode**
   - Run `python demo.py` for live demonstration
   - Use mock providers for testing
   - Start with examples before customizing

4. **Follow DDD Principles**
   - Keep domain logic in domain layer (Evans, 2003)
   - Use aggregates correctly (Evans, 2003; Vernon, 2013)
   - Maintain bounded context boundaries (Evans, 2003)
   - Preserve domain invariants (Evans, 2003)

5. **Test Your Changes**
   - Write tests for new features
   - Run existing tests
   - Verify domain invariants
   - Test integration points

### ❌ Don'ts

1. **Don't Use for Production**
   - This is demonstration code
   - Not production-ready
   - Missing critical features
   - See DISCLAIMERS.md

2. **Don't Skip Documentation**
   - Read before coding
   - Understand patterns first
   - Review examples
   - Check citations

3. **Don't Break Domain Invariants**
   - Maintain business rules
   - Preserve immutability
   - Keep aggregates consistent
   - Validate inputs

4. **Don't Mix Concerns**
   - Keep domain pure
   - Separate infrastructure
   - Maintain boundaries
   - Use proper layers

5. **Don't Ignore Tests**
   - Run tests before changes
   - Add tests for new code
   - Verify correctness
   - Check coverage

## Extending the System

### Adding New Features

1. **Follow DDD Structure**
   ```python
   # Domain layer: Business logic
   src/domain/your_domain/
   
   # Application layer: Orchestration
   src/orchestrator/
   
   # Infrastructure: External systems
   src/agents/your_agent.py
   ```

2. **Maintain Patterns**
   - Use aggregates for entities (Evans, 2003; Vernon, 2013)
   - Use value objects for data (Evans, 2003)
   - Publish domain events (Vernon, 2013)
   - Use repositories for data access (Evans, 2003; Fowler, 2002)

3. **Add Tests**
   - Unit tests for domain logic
   - Integration tests for workflows
   - Tests for domain invariants

4. **Update Documentation**
   - Document new features
   - Update architecture diagrams
   - Add examples
   - Update citations if needed

### Adding New Agents

1. **Inherit from BaseAgent**
   ```python
   from src.agents.base_agent import BaseAgent
   
   class YourAgent(BaseAgent):
       def get_system_prompt(self) -> str:
           # Define agent's role
           pass
       
       async def process(self, input_data):
           # Process and return domain object + event
           pass
   ```

2. **Act as Anti-Corruption Layer**
   - Validate LLM output
   - Translate to domain models (Evans, 2003, pp. 365-380)
   - Enforce domain rules
   - Handle errors gracefully

3. **Use Appropriate Model**
   - Choose model for task
   - Configure temperature
   - Set appropriate prompts
   - Validate outputs

### Adding New Bounded Contexts

1. **Define Domain Models**
   - Create aggregates
   - Define value objects
   - Specify domain events
   - Document invariants

2. **Create Repository**
   - Abstract data access
   - Implement interface
   - Keep domain pure

3. **Integrate with Orchestrator**
   - Subscribe to events
   - Publish events
   - Maintain boundaries

## Learning from This System

### Study Path

1. **Start Broad**
   - Read README.md
   - Watch demo (`python demo.py`)
   - Explore visualizations

2. **Go Deep**
   - Study domain models
   - Understand aggregates
   - Review event flow
   - Examine agents

3. **Practice**
   - Run examples
   - Modify code
   - Add features
   - Write tests

4. **Extend**
   - Add new agents
   - Create new contexts
   - Integrate new models
   - Build features

### Key Learning Points

1. **DDD Patterns**
   - How aggregates maintain consistency (Evans, 2003; Vernon, 2013)
   - How value objects enforce invariants (Evans, 2003)
   - How events enable loose coupling (Vernon, 2013; Hohpe & Woolf, 2003)
   - How repositories abstract persistence (Evans, 2003; Fowler, 2002)

2. **LLM Integration**
   - Prompt engineering techniques
   - Output validation strategies
   - Error handling approaches
   - Model selection criteria

3. **Architecture**
   - Event-driven design (Hohpe & Woolf, 2003)
   - Bounded context boundaries (Evans, 2003)
   - Anti-corruption layers (Evans, 2003)
   - Workflow orchestration (Hohpe & Woolf, 2003)

## Code Quality

### Writing Good Code

1. **Follow DDD Principles**
   - Domain logic in domain layer (Evans, 2003)
   - Infrastructure separate (Evans, 2003; Martin, 2017)
   - Clear boundaries (Evans, 2003)
   - Proper abstractions (Fowler, 2002)

2. **Write Clear Code**
   - Descriptive names
   - Comments explaining DDD concepts
   - Type hints
   - Docstrings

3. **Maintain Invariants**
   - Validate at boundaries
   - Enforce in domain models
   - Test invariants
   - Document rules

4. **Handle Errors**
   - Validate inputs
   - Handle LLM errors
   - Graceful degradation
   - Clear error messages

5. **Leverage Resilience Features**
   - Trust automatic normalization (comma-separated numbers, date formats)
   - Use progressive retry strategies
   - Monitor normalization success rates
   - Test with various data formats
   - See docs/RESILIENCE.md for details

### Testing Best Practices

Testing LLM-based systems requires specialized strategies beyond traditional unit testing:

1. **Test Domain Logic**
   - Test invariants
   - Test state transitions
   - Test business rules
   - Test edge cases

2. **Test Agents**
   - Mock LLM providers
   - Test validation
   - Test error handling
   - Test output parsing
   - Test data normalization (comma-separated numbers, date formats, enum values)
   - Test progressive retry strategies
   - Behavioral testing beyond accuracy (Ribeiro et al., 2020)
   - Property-based testing for ML systems (Godefroid et al., 2020)

3. **Test Integration**
   - Test workflows
   - Test event flow
   - Test human review
   - Test error recovery
   - Adversarial testing for robustness (Zhang et al., 2020; Helbling & Schlobach, 2023)

**Research Foundations**:
- **Ribeiro et al. (2020)**: Behavioral testing of NLP models with CheckList
- **Godefroid et al. (2020)**: Property-based testing for machine learning
- **Helbling & Schlobach (2023)**: Comprehensive survey of testing LLM applications

See: docs/REFERENCES.md#testing-llm-based-systems

## Documentation Best Practices

### Writing Documentation

1. **Be Clear**
   - Use simple language
   - Explain concepts
   - Provide examples
   - Include diagrams

2. **Cite Sources**
   - Reference research
   - Link to papers
   - Credit authors
   - Use APA format

3. **Keep Updated**
   - Update when code changes
   - Maintain examples
   - Keep citations current
   - Review regularly

### Code Comments

1. **Explain Why**
   - Why this pattern?
   - Why this design?
   - Why this approach?
   - Why this invariant?

2. **Reference DDD**
   - Which pattern?
   - Which principle?
   - Which concept?
   - Which reference?

3. **Document Invariants**
   - What must be true?
   - When is it enforced?
   - How is it verified?
   - What happens if violated?

## Common Pitfalls

### Avoid These Mistakes

1. **Mixing Layers**
   - Don't put domain logic in infrastructure
   - Don't put infrastructure in domain
   - Maintain clear boundaries
   - Use proper abstractions

2. **Breaking Invariants**
   - Don't bypass validation
   - Don't modify value objects
   - Don't skip state checks
   - Don't ignore business rules

3. **Tight Coupling**
   - Don't couple bounded contexts
   - Use events for communication
   - Abstract external systems
   - Maintain independence

4. **Ignoring Tests**
   - Don't skip test writing
   - Don't ignore test failures
   - Don't test only happy paths
   - Don't forget edge cases

## Production Considerations

If adapting concepts for production:

1. **Security**
   - Add authentication
   - Implement authorization
   - Encrypt sensitive data
   - Audit access

2. **Persistence**
   - Use real database
   - Implement transactions
   - Add backup/recovery
   - Plan for scale

3. **Monitoring**
   - Add logging
   - Implement metrics
   - Set up alerts
   - Track performance

4. **Compliance**
   - Review regulations
   - Implement compliance
   - Add audit trails
   - Ensure privacy

5. **Testing**
   - Comprehensive test suite
   - Load testing
   - Security testing
   - Compliance testing

## Resources

### Learning Resources

- **DDD**: See REFERENCES.md for DDD books and papers
- **LLMs**: See REFERENCES.md for LLM research
- **Architecture**: See REFERENCES.md for architecture patterns
- **Events**: See REFERENCES.md for event-driven architecture

### Code Resources

- **Examples**: See `examples/` directory
- **Tests**: See `tests/` directory
- **Docs**: See `docs/` directory
- **Visualizations**: See `docs/visualization.html`

## Questions?

- Check documentation first
- Review examples
- Study test cases
- Explore code
- Read citations

---

**Remember**: This is an educational system. Follow best practices, but understand this is demonstration code, not production software.

