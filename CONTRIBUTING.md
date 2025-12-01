# Contributing to DDD-LLM Claims Processing System

> **⚠️ IMPORTANT**: This is a **DEMONSTRATION SYSTEM** for **EDUCATIONAL PURPOSES ONLY**.  
> **NOT for production use**. See [DISCLAIMERS.md](DISCLAIMERS.md) for complete information.

Thank you for your interest in contributing to this educational demonstration project! This document provides guidelines for contributing.

## Purpose of This Project

This project is designed for **educational purposes** to demonstrate:
- Domain-Driven Design (DDD) principles
- LLM agent integration patterns
- Event-driven architecture
- Human-in-the-loop workflows

Contributions should maintain this educational focus.

## How to Contribute

### Types of Contributions We Welcome

1. **Documentation Improvements**
   - Clarifying explanations
   - Fixing typos or errors
   - Adding examples
   - Improving diagrams

2. **Code Examples**
   - Additional use cases
   - Better examples
   - Test cases

3. **Educational Enhancements**
   - Better visualizations
   - Tutorial content
   - Learning resources

4. **Code Quality**
   - Bug fixes
   - Code clarity improvements
   - Test coverage

### What We Don't Accept

- Production-ready features (this is a demo system)
- Security hardening (not needed for educational demo)
- Performance optimizations (not the focus)
- Enterprise features (beyond educational scope)

## Development Guidelines

### Before Contributing

1. **Read the Documentation**
   - [README.md](README.md) - Project overview
   - [DISCLAIMERS.md](DISCLAIMERS.md) - Important limitations
   - [BEST_PRACTICES.md](BEST_PRACTICES.md) - Development guidelines
   - [docs/TECHNICAL.md](docs/TECHNICAL.md) - Architecture details

2. **Understand the Purpose**
   - This is an educational demonstration
   - Focus on learning value, not production features
   - Maintain DDD principles

### Code Standards

1. **Follow DDD Principles**
   - Keep domain logic in domain layer
   - Use aggregates correctly
   - Maintain bounded context boundaries
   - Preserve domain invariants

2. **Code Quality**
   - Follow existing code style
   - Add type hints
   - Write clear docstrings
   - Include demo disclaimers in module docstrings

3. **Testing**
   - Add tests for new features
   - Run existing tests
   - Verify domain invariants

### Documentation Standards

1. **Always Include Demo Disclaimers**
   - Mark as educational/demo system
   - Reference DISCLAIMERS.md
   - Don't suggest production use

2. **Cite Sources**
   - Use APA format for citations
   - Link to REFERENCES.md
   - Include DOI links where available

3. **Use Mermaid for Diagrams**
   - All diagrams should use Mermaid syntax
   - Ensure GitHub compatibility
   - Keep diagrams clear and readable

## Contribution Process

### 1. Fork and Clone

```bash
git clone <your-fork-url>
cd ddd-llm
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes

- Follow development guidelines
- Add tests if applicable
- Update documentation
- Include demo disclaimers

### 4. Test Your Changes

```bash
# Run tests
pytest tests/

# Check code quality
ruff check src/
black --check src/
```

### 5. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git commit -m "docs: Add future work section to architecture.md"
```

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Pull Request Guidelines

### PR Description Should Include

1. **Purpose**: What does this PR do?
2. **Educational Value**: How does this help learning?
3. **Changes**: What was changed?
4. **Testing**: How was it tested?
5. **Documentation**: What docs were updated?

### PR Checklist

- [ ] Code follows DDD principles
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Demo disclaimers included
- [ ] Citations added (if applicable)
- [ ] No production-focused features

## Code Review Process

1. **Maintainer reviews** for:
   - Educational value
   - DDD compliance
   - Code quality
   - Documentation completeness

2. **Feedback provided** within reasonable time

3. **Changes requested** if needed

4. **PR merged** when approved

## Questions?

- Check [BEST_PRACTICES.md](BEST_PRACTICES.md) for guidelines
- Review [docs/TECHNICAL.md](docs/TECHNICAL.md) for architecture
- See [docs/README.md](docs/README.md) for documentation structure

## Future Work

If you're interested in exploring future enhancements, see:
- [docs/architecture.md](docs/architecture.md#future-work) - Future work items
- [docs/REFERENCES.md](docs/REFERENCES.md#future-research-directions) - Research directions

---

**Remember**: This is an **educational demonstration system**. Focus on learning value and maintaining the educational purpose of the project.

Thank you for contributing! 🎓


