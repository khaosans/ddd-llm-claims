# Fraud Detection Demo Guide

This guide explains how to run fraud detection demos and generate test templates.

## Quick Start

### Run Fraud Detection Demo

```bash
python scripts/demo_fraud_detection.py
```

This interactive demo allows you to:
- Test various fraud and anomaly templates
- See fraud detection results in real-time
- Compare normal vs. suspicious claims
- Explore risk factors and fraud scores

### Generate New Templates Using LLM

```bash
python scripts/generate_fraud_templates.py
```

This interactive tool uses LLM to generate new fraud templates:
- Generate completely new fraud scenarios
- Create variations of existing templates
- Generate random templates for testing
- Batch generate multiple templates

### Generate Random Template Variations

```bash
python scripts/random_template_generator.py <template_name> -n 10 -l moderate
```

Generate random variations of existing templates:
- `-n, --count`: Number of variations (default: 5)
- `-l, --level`: Variation level - minor/moderate/major (default: moderate)
- `-o, --output`: Output directory (default: generated_templates)

Example:
```bash
# Generate 10 moderate variations of stolen_vehicle_fraud template
python scripts/random_template_generator.py stolen_vehicle_fraud -n 10 -l moderate
```

## Demo Modes

### 1. Interactive Fraud Detection Demo

Run `scripts/demo_fraud_detection.py` for an interactive demo:

**Features:**
- Select from available fraud/anomaly templates
- See fraud detection results with scores and risk factors
- Compare normal vs. suspicious claims
- Run all fraud templates in sequence

**Usage:**
```bash
python scripts/demo_fraud_detection.py
```

**What You'll See:**
- Fraud score (0.0 - 1.0)
- Risk level (low/medium/high/critical)
- Risk factors identified
- Assessment confidence
- Human review requirements

### 2. Template Generation Demo

Run `scripts/generate_fraud_templates.py` to generate new templates:

**Options:**
1. **Generate new fraud template** - Create a completely new fraud scenario
2. **Generate variation** - Create variations of existing templates
3. **Generate random template** - Random fraud scenario
4. **Batch generate** - Generate multiple templates at once

**Example Workflow:**
```bash
python scripts/generate_fraud_templates.py

# Select option 1: Generate new fraud template
# Enter template type: stolen_vehicle
# Enter description: Car stolen immediately after policy purchase
# Enter fraud indicators: Suspicious timing, Quick reporting, Location inconsistencies
# Enter severity: high
```

### 3. Random Variation Generator

Use `scripts/random_template_generator.py` for quick variations:

**Use Cases:**
- Generate test datasets
- Create diverse training data
- Test system robustness
- Performance testing

**Examples:**
```bash
# Generate 5 moderate variations
python scripts/random_template_generator.py inflated_damage_claim -n 5

# Generate 20 minor variations for testing
python scripts/random_template_generator.py auto_insurance_claim -n 20 -l minor

# Generate major variations
python scripts/random_template_generator.py suspicious_timing -n 10 -l major
```

## Integration with Main Demo

The main demo (`demo.py`) now includes fraud detection:

```bash
python demo.py
```

The workflow now shows:
1. Fact extraction
2. Policy validation
3. **Fraud assessment** (with fraud score and risk factors)
4. Triage & routing

## Template Types

### Fraud Templates
- `stolen_vehicle_fraud` - Suspicious theft claims
- `inflated_damage_claim` - Unusually high repair costs
- `duplicate_claim` - Same incident claimed multiple times
- `suspicious_timing` - Claims filed immediately after policy start
- `missing_documentation` - Insufficient evidence
- `inconsistent_story` - Contradictory details

### Anomaly Templates
- `missing_critical_fields` - Incomplete information
- `invalid_date_format` - Date inconsistencies
- `invalid_amount_format` - Amount formatting issues
- `missing_policy_number` - Policy information missing
- `expired_policy_claim` - Claims on expired policies
- `coverage_mismatch` - Coverage type mismatches
- `amount_exceeds_coverage` - Claims exceeding policy limits
- `multiple_claims_short_period` - Multiple claims in short timeframe
- `claim_after_policy_start` - Suspicious timing patterns

## Demo Scenarios

### Scenario 1: Quick Fraud Detection Test
```bash
python scripts/demo_fraud_detection.py
# Select template: stolen_vehicle_fraud
# Review fraud detection results
```

### Scenario 2: Generate Custom Fraud Template
```bash
python scripts/generate_fraud_templates.py
# Option 1: Generate new fraud template
# Enter details for custom scenario
# Save template for future use
```

### Scenario 3: Batch Testing
```bash
# Generate 50 random variations
python scripts/random_template_generator.py auto_insurance_claim -n 50

# Test all variations
python scripts/demo_fraud_detection.py
# Select: Run all fraud templates
```

### Scenario 4: Full Workflow Demo
```bash
python demo.py
# Complete workflow including fraud detection
# See fraud assessment in step 4
```

## Expected Results

### Low Risk Claims (Score: 0.0 - 0.3)
- Normal auto insurance claims
- Standard property damage claims
- Well-documented incidents

### Medium Risk Claims (Score: 0.3 - 0.6)
- Missing documentation
- Data quality issues
- Policy mismatches
- Expired policies

### High Risk Claims (Score: 0.6 - 0.8)
- Suspicious timing
- Inflated damage amounts
- Duplicate claims
- Inconsistent stories

### Critical Risk Claims (Score: 0.8 - 1.0)
- Multiple fraud indicators
- Clear fraud patterns
- Stolen vehicle with timing issues
- Major inconsistencies

## Tips

1. **Start with Templates**: Use existing templates to understand the system
2. **Generate Variations**: Create variations to test robustness
3. **Compare Results**: Test normal vs. fraud templates side-by-side
4. **Review Risk Factors**: Pay attention to specific risk factors identified
5. **Test Edge Cases**: Generate extreme variations to test limits

## Troubleshooting

### LLM Not Available
- Scripts will use mock providers automatically
- Results will be simulated but functional
- Install Ollama for real LLM generation

### Templates Not Found
- Check template name spelling
- Use `list_templates()` to see available templates
- Generate new templates if needed

### Generation Errors
- Check LLM provider connection
- Verify template format
- Try simpler variations first

## Next Steps

1. **Run Demo**: `python scripts/demo_fraud_detection.py`
2. **Generate Templates**: `python scripts/generate_fraud_templates.py`
3. **Create Variations**: `python scripts/random_template_generator.py <template> -n 10`
4. **Run Tests**: `python scripts/run_fraud_tests.py`

For more information, see:
- `tests/test_fraud_detection.py` - Test suite
- `tests/expected_fraud_results.json` - Expected results
- `DATA_TEMPLATES.md` - Template documentation



