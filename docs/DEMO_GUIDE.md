# Demo Guide

How to run and present the live demonstration of the DDD Claims Processing System.

## Quick Demo (Recommended)

The easiest way to demonstrate the system:

```bash
python demo.py
```

This interactive script will:
- Guide you through the complete workflow
- Explain each step
- Show human review in action
- Work without Ollama (uses mock providers)

## Demo Scenarios

### Scenario 1: Standard Claim Processing

**Setup**: Run `python demo.py` and follow the prompts.

**What to Highlight**:
- Unstructured email input
- AI agent extracts facts
- Policy validation
- Fraud assessment
- Automatic routing

**Key Points**:
- DDD patterns in action
- Event-driven workflow
- LLM as Anti-Corruption Layer

### Scenario 2: Human Review Required

**Setup**: Process a claim with high amount ($150,000+)

**What to Highlight**:
- System detects need for review
- Claim added to review queue
- Human reviewer makes decision
- Feedback captured

**Key Points**:
- Human-in-the-loop pattern
- Review queue prioritization
- Feedback loop

### Scenario 3: Interactive Visualization

**Setup**: Open `docs/visualization.html` in browser

**What to Highlight**:
- Architecture diagram
- Workflow sequence
- Interactive tooltips
- Guided tour

**Key Points**:
- Visual learning
- Concept exploration
- Research citations

## Presentation Tips

### For Technical Audiences

1. **Start with Architecture**
   - Show bounded contexts
   - Explain DDD patterns
   - Highlight event-driven design

2. **Demonstrate Code**
   - Show domain models
   - Explain aggregates
   - Review agents

3. **Run Live Demo**
   - Process a claim
   - Show human review
   - Explain workflow

### For Business Audiences

1. **Start with Problem**
   - Unstructured data challenge
   - Manual processing costs
   - Need for automation

2. **Show Solution**
   - AI extracts facts
   - Automatic validation
   - Smart routing

3. **Highlight Benefits**
   - Faster processing
   - Consistent quality
   - Human oversight

### For Educational Audiences

1. **Explain Concepts**
   - What is DDD?
   - How do agents work?
   - Why events?

2. **Show Examples**
   - Run demo
   - Explore code
   - Review tests

3. **Discuss Patterns**
   - Aggregate pattern
   - Repository pattern
   - Anti-Corruption Layer

## Demo Script

### Introduction (1 minute)

"Today I'll demonstrate a Domain-Driven Design system that processes insurance claims using LLM agents. This is an educational demonstration showing how modern AI can be integrated with proven software architecture patterns."

### Setup (30 seconds)

"Let me start the system. It's using mock providers for this demo, so it works immediately without needing Ollama running."

```bash
python demo.py
```

### Workflow Demonstration (3-5 minutes)

1. **Input**: "Here's an unstructured email from a customer..."
2. **Extraction**: "The Intake Agent extracts structured facts..."
3. **Validation**: "Policy Agent validates coverage..."
4. **Assessment**: "Fraud assessment calculates risk..."
5. **Routing**: "Triage Agent routes to appropriate handler..."

### Human Review (2 minutes)

"If the claim needs review, it goes to a human reviewer..."

### Key Takeaways (1 minute)

- DDD structures complex domains
- LLM agents act as translators
- Events enable loose coupling
- Human review provides oversight

## Common Questions

### "Is this production-ready?"

**Answer**: No, this is a demonstration system for educational purposes. See DISCLAIMERS.md for limitations.

### "Can I use this for real claims?"

**Answer**: No, this is not for production use. It's missing security, compliance, persistence, and many other production features.

### "How accurate is the AI?"

**Answer**: This demo uses simplified scenarios. Real LLMs have accuracy limitations and may hallucinate. Always validate AI output.

### "What about security?"

**Answer**: This demo has no security features. Production systems need authentication, authorization, encryption, and compliance.

### "Can I extend this?"

**Answer**: Yes! See BEST_PRACTICES.md for guidelines. But remember this is educational code, not a production foundation.

## Troubleshooting

### Demo Won't Start

- Check Python version (3.10+)
- Install dependencies: `pip install -r requirements.txt`
- Run from project root directory

### Ollama Issues

- Use demo mode (works without Ollama)
- Or check Ollama is running: `ollama serve`
- Verify model downloaded: `ollama list`

### Import Errors

- Make sure you're in project root
- Check Python path includes project
- Verify all dependencies installed

## Best Practices for Demos

1. **Read DISCLAIMERS.md First**
   - Understand limitations
   - Set proper expectations
   - Avoid misleading claims

2. **Use Demo Data Only**
   - Never use real customer data
   - Use provided examples
   - Create synthetic data

3. **Explain It's Educational**
   - Emphasize learning purpose
   - Highlight it's a demo
   - Mention limitations

4. **Show Code When Possible**
   - Explain DDD patterns
   - Show domain models
   - Review architecture

5. **Answer Questions Honestly**
   - Admit limitations
   - Explain trade-offs
   - Suggest improvements

---

**Remember**: This is a demonstration system. Always emphasize it's for education, not production.

