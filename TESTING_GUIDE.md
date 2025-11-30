# Testing Guide

This guide provides comprehensive testing scenarios using the diverse claim templates available in the system.

## 🎯 Testing Overview

The system includes **37 claim templates** organized into categories to test different aspects:

- **Legitimate Claims** - Well-documented, valid claims
- **Fraud/Issues** - Suspicious patterns and fraud indicators
- **Data Quality Issues** - Missing fields, invalid formats
- **Policy Issues** - Coverage problems, expired policies
- **Edge Cases** - Unusual scenarios, boundary conditions
- **Other Formats** - Different input formats

## ✅ Testing Legitimate Claims

### Purpose
Test that the system correctly processes well-documented, valid claims.

### Templates to Use
1. `good_legitimate_claim` - Complete auto claim with all documentation
2. `good_property_claim` - Complete property claim with fire report
3. `good_health_claim` - Complete medical claim with documentation
4. `auto_insurance_claim` - Standard auto claim
5. `property_damage_claim` - Standard property claim
6. `health_insurance_claim` - Standard health claim

### Expected Results
- ✅ All fields extracted correctly
- ✅ Policy validation passes
- ✅ Fraud score is low (< 0.3)
- ✅ Claim proceeds through workflow
- ✅ No human review required (unless high value)

### What to Verify
- [ ] All claim facts extracted (date, amount, location, etc.)
- [ ] Policy number validated
- [ ] Claim amount within policy limits
- [ ] Workflow completes successfully
- [ ] Decision audit trail created

## 🚨 Testing Fraud Detection

### Purpose
Test that the system detects various fraud indicators and suspicious patterns.

### Templates to Use

#### Suspicious Timing
- `stolen_vehicle_fraud` - Car stolen immediately after policy start
- `suspicious_timing` - Claim filed 1 day after policy start
- `claim_after_policy_start` - Accident 1 hour after policy start

#### Unreasonable Amounts
- `inflated_damage_claim` - $85,000 for minor fender bender

#### Duplicate Claims
- `duplicate_claim` - Same incident filed twice

#### Pattern Analysis
- `multiple_vehicles_stolen` - Multiple thefts in short period
- `excessive_medical_claims` - Multiple doctors same day
- `multiple_claims_short_period` - Third claim in one month

#### Coordinated Fraud
- `coordinate_fraud` - Friends coordinating claims

### Expected Results
- ⚠️ Fraud score elevated (> 0.3, often > 0.6)
- ⚠️ Risk level: Medium to High
- ⚠️ Claim routed to human review
- ⚠️ Risk factors identified

### What to Verify
- [ ] Fraud score reflects suspicious patterns
- [ ] Risk factors are identified correctly
- [ ] Claim flagged for review
- [ ] Risk level appropriate
- [ ] Decision audit captures fraud assessment

## ⚠️ Testing Data Quality Issues

### Purpose
Test that the system handles incomplete or invalid data gracefully.

### Templates to Use
- `missing_critical_fields` - Minimal information
- `missing_documentation` - No evidence provided
- `invalid_date_format` - Vague dates ("yesterday", "afternoon")
- `invalid_amount_format` - Amount in words, unclear
- `missing_policy_number` - No policy information
- `inconsistent_story` - Contradictory details
- `bad_health_claim_missing_docs` - Medical claim without receipts

### Expected Results
- ⚠️ Some fields may not be extracted
- ⚠️ Data quality warnings generated
- ⚠️ May require human review for clarification
- ⚠️ System continues processing with available data

### What to Verify
- [ ] System handles missing fields gracefully
- [ ] Warnings generated for data quality issues
- [ ] Partial extraction works correctly
- [ ] System doesn't crash on invalid formats
- [ ] Human review triggered when needed

## ❌ Testing Policy Validation

### Purpose
Test that the system correctly validates policy coverage and limits.

### Templates to Use
- `expired_policy_claim` - Policy expired before incident
- `policy_lapse_claim` - Policy lapsed one day before
- `coverage_mismatch` - Property claim on auto policy
- `amount_exceeds_coverage` - Claim exceeds policy limit

### Expected Results
- ❌ Policy validation fails
- ❌ Claim rejected or flagged
- ❌ Clear error messages
- ❌ Human review required

### What to Verify
- [ ] Expired policies detected
- [ ] Coverage type validated
- [ ] Policy limits checked
- [ ] Appropriate error messages
- [ ] Claims routed correctly

## 🔍 Testing Edge Cases

### Purpose
Test that the system handles unusual scenarios and boundary conditions.

### Templates to Use
- `edge_case_zero_amount` - $0.00 damage claim
- `edge_case_very_old_incident` - Claim filed 2 years after incident
- `edge_case_future_date` - Claim for "tomorrow's" accident
- `multiple_claims_short_period` - Frequent claims pattern

### Expected Results
- ⚠️ System handles edge cases gracefully
- ⚠️ Appropriate warnings or errors
- ⚠️ Doesn't crash on invalid data
- ⚠️ May require human review

### What to Verify
- [ ] Zero amounts handled correctly
- [ ] Old incidents validated
- [ ] Invalid dates rejected
- [ ] Frequency patterns detected
- [ ] System remains stable

## 📞 Testing Different Formats

### Purpose
Test that the system handles various input formats.

### Templates to Use
- `phone_transcript` - Phone call format
- `web_form_submission` - Structured form format
- `auto_insurance_claim` - Email format (standard)

### Expected Results
- ✅ All formats processed correctly
- ✅ Same extraction quality regardless of format
- ✅ Workflow proceeds normally

### What to Verify
- [ ] Phone transcripts parsed correctly
- [ ] Form submissions handled
- [ ] Email format works
- [ ] Extraction quality consistent

## 🎯 Comprehensive Testing Workflow

### Step 1: Baseline Testing
1. Start with `good_legitimate_claim`
2. Verify all features work correctly
3. Establish baseline metrics

### Step 2: Category Testing
1. Test 2-3 templates from each category
2. Verify category-specific behavior
3. Check fraud scores and routing

### Step 3: Edge Case Testing
1. Test all edge case templates
2. Verify system stability
3. Check error handling

### Step 4: Integration Testing
1. Process multiple claims in sequence
2. Test with different claim types
3. Verify system handles variety

### Step 5: Review Testing
1. Process claims that require review
2. Test review queue functionality
3. Verify human review workflow

## 📊 Expected Fraud Scores by Category

| Category | Expected Fraud Score | Risk Level |
|----------|---------------------|------------|
| ✅ Legitimate | 0.0 - 0.3 | Low |
| 🚨 Fraud/Issues | 0.4 - 0.9 | Medium to High |
| ⚠️ Data Quality | 0.2 - 0.5 | Low to Medium |
| ❌ Policy Issues | N/A (Policy validation fails) | N/A |
| 🔍 Edge Cases | 0.1 - 0.6 | Varies |

## 🔍 What to Check in Results

### For Each Claim, Verify:

1. **Extraction Quality**
   - [ ] All available fields extracted
   - [ ] Dates parsed correctly
   - [ ] Amounts extracted accurately
   - [ ] Policy number found

2. **Fraud Assessment**
   - [ ] Fraud score appropriate for claim type
   - [ ] Risk factors identified
   - [ ] Risk level matches score

3. **Policy Validation**
   - [ ] Policy found and validated
   - [ ] Coverage checked
   - [ ] Limits verified

4. **Workflow Progression**
   - [ ] Workflow steps completed
   - [ ] Events published correctly
   - [ ] Routing decision made

5. **Decision Audit**
   - [ ] Decisions captured
   - [ ] Context stored
   - [ ] Audit trail complete

## 💡 Testing Tips

1. **Start Simple**: Begin with legitimate claims
2. **Test Categories**: Cover all template categories
3. **Compare Results**: Compare good vs. bad claims
4. **Check Scores**: Verify fraud scores make sense
5. **Review Routing**: Ensure claims routed correctly
6. **Test Edge Cases**: Don't skip unusual scenarios
7. **Verify Persistence**: Check data saved to database
8. **Test Vector Search**: Try semantic search features

## 📚 Additional Resources

- `DATA_TEMPLATES.md` - Complete template documentation
- `TEMPLATES_QUICK_REFERENCE.md` - Quick access guide
- `docs/TECHNICAL.md` - Technical implementation details
- `README.md` - System overview

## 🎯 Quick Test Checklist

- [ ] Test at least 1 legitimate claim
- [ ] Test at least 1 fraud indicator
- [ ] Test at least 1 data quality issue
- [ ] Test at least 1 policy issue
- [ ] Test at least 1 edge case
- [ ] Verify fraud scores
- [ ] Verify policy validation
- [ ] Verify human review routing
- [ ] Verify data persistence
- [ ] Verify decision audit trail

