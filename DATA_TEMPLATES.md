# Data Templates Guide

This guide provides ready-to-use templates for all input fields in the application, perfect for demos and testing.

## 📊 Template Overview

The system now includes **30+ claim templates** organized by category:

- **✅ Legitimate Claims** (11 templates) - Good, well-documented claims
- **🚨 Fraud/Issues** (8 templates) - Various fraud indicators and suspicious patterns
- **⚠️ Data Quality Issues** (7 templates) - Missing fields, invalid formats, inconsistencies
- **❌ Policy Issues** (4 templates) - Expired policies, coverage mismatches, etc.
- **🔍 Edge Cases** (5 templates) - Unusual scenarios and boundary conditions
- **📞 Other Formats** (2 templates) - Phone transcripts, web forms

## ✅ Legitimate Claims

### 1. Auto Insurance Claim (Standard)
**Template Name**: `auto_insurance_claim`
**Use Case**: Standard car accident claim with complete information

### 2. Property Damage Claim
**Template Name**: `property_damage_claim`
**Use Case**: Water damage, fire damage, etc.

### 3. High Value Claim
**Template Name**: `high_value_claim`
**Use Case**: Large claims requiring human review ($57,500)

### 4. Simple Claim
**Template Name**: `simple_claim`
**Use Case**: Quick low-value claim for fast demos

### 5. Health Insurance Claim
**Template Name**: `health_insurance_claim`
**Use Case**: Medical expenses claim with proper documentation

### 6. Life Insurance Claim
**Template Name**: `life_insurance_claim`
**Use Case**: Death benefit claim

### 7. Disability Insurance Claim
**Template Name**: `disability_insurance_claim`
**Use Case**: Work injury disability claim

### 8. Travel Insurance Claim
**Template Name**: `travel_insurance_claim`
**Use Case**: Trip cancellation due to emergency

### 9. Good Legitimate Claim
**Template Name**: `good_legitimate_claim`
**Use Case**: Well-documented auto claim with all required information

### 10. Good Property Claim
**Template Name**: `good_property_claim`
**Use Case**: Complete property damage claim with fire department report

### 11. Good Health Claim
**Template Name**: `good_health_claim`
**Use Case**: Medical claim with complete documentation

## 🚨 Fraud/Issues Templates

### 1. Fraud Risk Claim (Stolen Vehicle)
**Template Name**: `fraud_risk_claim`
**Use Case**: Stolen vehicle claim - may be legitimate but requires review

### 2. Stolen Vehicle Fraud
**Template Name**: `stolen_vehicle_fraud`
**Use Case**: Suspicious timing - car stolen immediately after policy start

### 3. Inflated Damage Claim
**Template Name**: `inflated_damage_claim`
**Use Case**: Minor accident with unreasonably high repair costs ($85,000 for fender bender)

### 4. Duplicate Claim
**Template Name**: `duplicate_claim`
**Use Case**: Same incident filed multiple times

### 5. Suspicious Timing
**Template Name**: `suspicious_timing`
**Use Case**: Claim filed immediately after policy start (1 day later)

### 6. Multiple Vehicles Stolen
**Template Name**: `multiple_vehicles_stolen`
**Use Case**: Multiple stolen vehicle claims in short period

### 7. Excessive Medical Claims
**Template Name**: `excessive_medical_claims`
**Use Case**: Multiple doctors for same condition on same day

### 8. Coordinate Fraud
**Template Name**: `coordinate_fraud`
**Use Case**: Friends coordinating to file claims and split money

## ⚠️ Data Quality Issues

### 1. Missing Documentation
**Template Name**: `missing_documentation`
**Use Case**: Claim with no photos, reports, or evidence

### 2. Inconsistent Story
**Template Name**: `inconsistent_story`
**Use Case**: Contradictory details about incident

### 3. Missing Critical Fields
**Template Name**: `missing_critical_fields`
**Use Case**: Minimal information provided

### 4. Invalid Date Format
**Template Name**: `invalid_date_format`
**Use Case**: Vague dates like "yesterday" or "afternoon"

### 5. Invalid Amount Format
**Template Name**: `invalid_amount_format`
**Use Case**: Amount written in words, unclear values

### 6. Missing Policy Number
**Template Name**: `missing_policy_number`
**Use Case**: Claimant doesn't remember policy number

### 7. Bad Health Claim Missing Docs
**Template Name**: `bad_health_claim_missing_docs`
**Use Case**: Medical claim with no receipts or documentation

## ❌ Policy Issues

### 1. Expired Policy Claim
**Template Name**: `expired_policy_claim`
**Use Case**: Claim filed after policy expiration

### 2. Coverage Mismatch
**Template Name**: `coverage_mismatch`
**Use Case**: Property damage claim on auto insurance policy

### 3. Amount Exceeds Coverage
**Template Name**: `amount_exceeds_coverage`
**Use Case**: Claim amount ($150,000) exceeds policy limit ($50,000)

### 4. Policy Lapse
**Template Name**: `policy_lapse_claim`
**Use Case**: Claim filed one day after policy lapsed

## 🔍 Edge Cases

### 1. Zero Amount
**Template Name**: `edge_case_zero_amount`
**Use Case**: Claim with $0.00 damage

### 2. Very Old Incident
**Template Name**: `edge_case_very_old_incident`
**Use Case**: Claim filed 2 years after incident

### 3. Future Date
**Template Name**: `edge_case_future_date`
**Use Case**: Claim for accident that "will happen tomorrow"

### 4. Multiple Claims Short Period
**Template Name**: `multiple_claims_short_period`
**Use Case**: Third claim in same month

### 5. Claim After Policy Start
**Template Name**: `claim_after_policy_start`
**Use Case**: Accident one hour after policy started

## 📞 Other Formats

### 1. Phone Transcript
**Template Name**: `phone_transcript`
**Use Case**: Claim submitted via phone call transcript

### 2. Web Form Submission
**Template Name**: `web_form_submission`
**Use Case**: Structured form submission format

## 🎯 Testing Scenarios

### Testing Fraud Detection
Use these templates to test fraud detection:
- `stolen_vehicle_fraud` - Suspicious timing
- `inflated_damage_claim` - Unreasonable amounts
- `duplicate_claim` - Duplicate submissions
- `suspicious_timing` - Immediate claims after policy start
- `coordinate_fraud` - Coordinated fraud attempts

### Testing Data Quality
Use these templates to test data extraction:
- `missing_critical_fields` - Minimal information
- `invalid_date_format` - Vague dates
- `invalid_amount_format` - Unclear amounts
- `inconsistent_story` - Contradictory details

### Testing Policy Validation
Use these templates to test policy checks:
- `expired_policy_claim` - Expired coverage
- `coverage_mismatch` - Wrong policy type
- `amount_exceeds_coverage` - Over limits
- `policy_lapse_claim` - Lapsed policy

### Testing Edge Cases
Use these templates to test boundary conditions:
- `edge_case_zero_amount` - Zero damage
- `edge_case_very_old_incident` - Old incidents
- `edge_case_future_date` - Invalid dates
- `multiple_claims_short_period` - Frequency patterns

### Testing Different Claim Types
Use these templates to test various insurance types:
- `health_insurance_claim` - Medical claims
- `life_insurance_claim` - Death benefits
- `disability_insurance_claim` - Work injuries
- `travel_insurance_claim` - Trip cancellations

## 📋 Feedback Templates

### Approve
**Template Name**: `approve`
Standard approval message

### Approve with Notes
**Template Name**: `approve_with_notes`
Approval with detailed notes

### Reject
**Template Name**: `reject`
Standard rejection message

### Reject with Reason
**Template Name**: `reject_with_reason`
Rejection with specific reasons

### Override
**Template Name**: `override`
Human override of AI decision

### Request Info
**Template Name**: `request_info`
Request for additional documentation

## 🔍 Search Templates

- `by_name` - Search by claimant name
- `by_policy` - Search by policy number
- `by_amount` - Search by claim amount
- `by_date` - Search by incident date
- `by_type` - Search by claim type

## 🚀 Quick Start for Demos

### Recommended Demo Flow

1. **Start Simple**: Use `simple_claim` for quick results
2. **Show Legitimate**: Use `good_legitimate_claim` to show complete documentation
3. **Show Fraud Detection**: Use `stolen_vehicle_fraud` to demonstrate fraud detection
4. **Show Data Quality**: Use `missing_critical_fields` to show data extraction challenges
5. **Show Policy Issues**: Use `expired_policy_claim` to show policy validation
6. **Show Edge Cases**: Use `edge_case_future_date` to show boundary handling

### Testing Workflow

1. **Good Claims**: Test with `good_legitimate_claim`, `good_property_claim`, `good_health_claim`
2. **Fraud Detection**: Test with fraud templates to verify detection
3. **Data Quality**: Test with data quality templates to verify extraction
4. **Policy Validation**: Test with policy issue templates to verify validation
5. **Edge Cases**: Test with edge case templates to verify robustness

## 💡 Tips for Testing

1. **Start with Good Claims**: Test legitimate claims first to establish baseline
2. **Test Each Category**: Try templates from each category to test different aspects
3. **Compare Results**: Compare how system handles good vs. bad claims
4. **Check Fraud Scores**: Review fraud scores for suspicious claims
5. **Verify Extraction**: Check if all fields are extracted correctly
6. **Test Policy Validation**: Verify policy checks work correctly
7. **Test Edge Cases**: Ensure system handles unusual scenarios gracefully

## 🔧 Programmatic Access

```python
from data_templates import get_template, list_templates

# Get a specific template
claim_data = get_template("claim", "auto_insurance_claim")

# List all available templates
all_claim_templates = list_templates("claim")
all_feedback_templates = list_templates("feedback")
all_search_templates = list_templates("search")

# Get all templates by category
legitimate = ["auto_insurance_claim", "property_damage_claim", "good_legitimate_claim"]
fraud = ["stolen_vehicle_fraud", "inflated_damage_claim", "duplicate_claim"]
data_quality = ["missing_critical_fields", "invalid_date_format", "inconsistent_story"]
policy_issues = ["expired_policy_claim", "coverage_mismatch", "amount_exceeds_coverage"]
edge_cases = ["edge_case_zero_amount", "edge_case_very_old_incident", "edge_case_future_date"]
```

## 📝 Notes

- All templates use policy number `POL-2024-001234` (matches sample policy in system)
- Dates are set to recent dates for realistic demos
- Amounts vary to show different processing scenarios
- Templates are designed to trigger different workflow paths
- Good templates have complete documentation
- Fraud templates have suspicious patterns
- Data quality templates have missing or invalid information
- Policy issue templates have coverage problems
- Edge case templates test boundary conditions

## 🎯 Template Categories Summary

| Category | Count | Purpose |
|----------|-------|---------|
| ✅ Legitimate | 11 | Well-documented, valid claims |
| 🚨 Fraud/Issues | 8 | Suspicious patterns and fraud indicators |
| ⚠️ Data Quality | 7 | Missing fields, invalid formats |
| ❌ Policy Issues | 4 | Coverage problems, expired policies |
| 🔍 Edge Cases | 5 | Unusual scenarios, boundary conditions |
| 📞 Other Formats | 2 | Different input formats |
| **Total** | **37** | Comprehensive test coverage |

## 📚 Additional Resources

- See `TEMPLATES_QUICK_REFERENCE.md` for quick access guide
- See `scripts/generate_test_documents.py` for document generation
- See `scripts/random_template_generator.py` for random template generation
- See `tests/test_fraud_detection.py` for automated testing examples
