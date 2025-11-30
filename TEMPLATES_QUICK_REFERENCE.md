# Templates Quick Reference

## 🚀 Quick Start for Demos

### Process Claim Page Templates

Templates are now organized by category with expandable sections:

#### ✅ Legitimate Claims (11 templates)
- 🚗 **Auto Insurance** - Standard car accident
- 🏠 **Property Damage** - Water/fire damage
- 💰 **High Value** - $57,500 claim (triggers review)
- 📝 **Simple Claim** - Quick low-value
- 🏥 **Health Insurance** - Medical expenses
- 💼 **Life Insurance** - Death benefit
- 🦽 **Disability Insurance** - Work injury
- ✈️ **Travel Insurance** - Trip cancellation
- ✅ **Good Legitimate Claim** - Well-documented auto
- ✅ **Good Property Claim** - Complete property claim
- ✅ **Good Health Claim** - Complete medical claim

#### 🚨 Fraud/Issues (8 templates)
- 🚨 **Stolen Vehicle** - Theft claim
- 🚨 **Stolen Vehicle Fraud** - Suspicious timing
- 🚨 **Inflated Damage** - Unreasonable costs
- 🚨 **Duplicate Claim** - Same incident twice
- 🚨 **Suspicious Timing** - Immediate after policy start
- 🚨 **Multiple Vehicles Stolen** - Pattern of thefts
- 🚨 **Excessive Medical Claims** - Multiple doctors
- 🚨 **Coordinate Fraud** - Friends coordinating

#### ⚠️ Data Quality Issues (7 templates)
- ⚠️ **Missing Documentation** - No evidence
- ⚠️ **Inconsistent Story** - Contradictory details
- ⚠️ **Missing Critical Fields** - Minimal info
- ⚠️ **Invalid Date Format** - Vague dates
- ⚠️ **Invalid Amount Format** - Unclear amounts
- ⚠️ **Missing Policy Number** - No policy info
- ⚠️ **Bad Health Claim** - Missing medical docs

#### ❌ Policy Issues (4 templates)
- ❌ **Expired Policy** - Coverage expired
- ❌ **Coverage Mismatch** - Wrong policy type
- ❌ **Amount Exceeds Coverage** - Over limits
- ❌ **Policy Lapse** - Recently lapsed

#### 🔍 Edge Cases (5 templates)
- 🔍 **Zero Amount** - $0.00 damage
- 🔍 **Very Old Incident** - 2 years old
- 🔍 **Future Date** - Invalid date
- 🔍 **Multiple Claims** - Frequent claims
- 🔍 **Claim After Policy Start** - Immediate claim

#### 📞 Other Formats (2 templates)
- 📞 **Phone Transcript** - Phone call format
- 🌐 **Web Form** - Online submission

### Review Queue Feedback Templates

| Button | Template | Use Case |
|--------|----------|----------|
| ✅ **Approve Template** | Standard approval | Quick approval |
| ✅ **Approve with Notes** | Detailed approval | Approval with notes |
| ❌ **Reject Template** | Standard rejection | Quick rejection |
| ❌ **Reject with Reason** | Detailed rejection | Rejection with reasons |
| 🔄 **Override Template** | Override AI decision | Show human override |
| 📋 **Request Info** | Request documentation | Ask for more info |

### Search Templates

| Button | Search By | Example |
|--------|-----------|---------|
| 🔍 **By Name** | Claimant name | John Doe |
| 🔍 **By Policy** | Policy number | POL-2024-001234 |
| 🔍 **By Amount** | Claim amount | $3,500 |
| 🔍 **By Date** | Incident date | 2024-01-15 |
| 🔍 **By Type** | Claim type | auto |

## 📋 Recommended Demo Flow

1. **Start**: Go to Process Claim page
2. **Load Template**: Click a template from any category
3. **Process**: Click "🚀 Process Claim"
4. **View Results**: See extracted facts and workflow
5. **Check Queue**: Go to Claims List to see the claim
6. **Review**: Go to Human Review if claim needs review
7. **Use Feedback**: Click feedback template buttons

## 💡 Demo Tips

### First Demo
- Use **"Simple Claim"** for quick results
- Shows basic workflow without complexity

### Full Demo
- Use **"Good Legitimate Claim"** to show complete workflow
- Shows all features with proper documentation

### Fraud Detection Demo
- Use **"Stolen Vehicle Fraud"** to show fraud detection
- Shows suspicious timing patterns

### Data Quality Demo
- Use **"Missing Critical Fields"** to show extraction challenges
- Shows how system handles incomplete data

### Policy Validation Demo
- Use **"Expired Policy Claim"** to show policy checks
- Shows coverage validation

### Edge Cases Demo
- Use **"Future Date"** to show boundary handling
- Shows system robustness

## 🎯 Testing Scenarios

### Test Good Claims
1. `good_legitimate_claim` - Complete auto claim
2. `good_property_claim` - Complete property claim
3. `good_health_claim` - Complete medical claim

### Test Fraud Detection
1. `stolen_vehicle_fraud` - Suspicious timing
2. `inflated_damage_claim` - Unreasonable amounts
3. `duplicate_claim` - Duplicate submissions
4. `coordinate_fraud` - Coordinated fraud

### Test Data Quality
1. `missing_critical_fields` - Minimal information
2. `invalid_date_format` - Vague dates
3. `inconsistent_story` - Contradictory details

### Test Policy Validation
1. `expired_policy_claim` - Expired coverage
2. `coverage_mismatch` - Wrong policy type
3. `amount_exceeds_coverage` - Over limits

### Test Edge Cases
1. `edge_case_zero_amount` - Zero damage
2. `edge_case_very_old_incident` - Old incidents
3. `edge_case_future_date` - Invalid dates

## 🔧 All Templates Available

- **37 Claim Templates**: Comprehensive coverage
- **6 Feedback Templates**: Review actions
- **5 Search Templates**: Quick searches

## 📚 See Also

- `DATA_TEMPLATES.md` - Complete template documentation
- `docs/TECHNICAL.md` - Technical details
- `README.md` - System overview
