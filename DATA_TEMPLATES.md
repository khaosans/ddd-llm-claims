# Data Templates Guide

This guide provides ready-to-use templates for all input fields in the application, perfect for demos and testing.

## 📝 Claim Data Templates

### 1. Auto Insurance Claim (Standard)
**Use Case**: Standard car accident claim
**Template Name**: `auto_insurance_claim`

```
Subject: Auto Insurance Claim

Dear Insurance Company,

I am filing a claim for a car accident that occurred on January 15, 2024 at approximately 2:30 PM.

INCIDENT DETAILS:
- Date: January 15, 2024
- Time: 2:30 PM
- Location: Main Street and Oak Avenue, Anytown, State 12345
- Type: Rear-end collision
- Other driver: Another vehicle hit me from behind at a red light

DAMAGE:
- Estimated repair cost: $3,500.00
- Vehicle: 2020 Honda Accord
- License plate: ABC-1234

POLICY INFORMATION:
- Policy Number: POL-2024-001234
- Policyholder: John Doe

CONTACT INFORMATION:
- Email: john.doe@email.com
- Phone: +1-555-0123

Thank you for your assistance.

Sincerely,
John Doe
```

### 2. Property Damage Claim
**Use Case**: Water damage, fire damage, etc.
**Template Name**: `property_damage_claim`

```
Subject: Property Damage Claim - Water Damage

Hello,

I need to file a claim for water damage to my property.

INCIDENT DATE: February 10, 2024
TIME: Approximately 3:00 AM

LOCATION:
123 Oak Street, Apartment 4B
Springfield, IL 62701

DAMAGE DESCRIPTION:
A pipe burst in the apartment above mine, causing significant water damage to my ceiling, walls, and personal belongings. Water leaked through the ceiling for several hours before it was discovered.

ESTIMATED DAMAGE:
- Structural damage: $8,500.00
- Personal property damage: $3,200.00
- Total: $11,700.00

POLICY:
- Policy Number: POL-2024-001234
- Type: Renters Insurance

I have photos and documentation available upon request.

Best regards,
Jane Smith
jane.smith@email.com
(555) 987-6543
```

### 3. High Value Claim
**Use Case**: Large claims requiring human review
**Template Name**: `high_value_claim`

```
Subject: Major Auto Accident Claim - Urgent

URGENT CLAIM SUBMISSION

I was involved in a serious car accident on March 5, 2024 at 4:15 PM.

ACCIDENT DETAILS:
- Date: March 5, 2024
- Time: 4:15 PM
- Location: Highway 101, Mile Marker 45, Northbound
- Weather: Clear, dry conditions
- Traffic: Moderate

INCIDENT DESCRIPTION:
I was driving northbound on Highway 101 when another vehicle crossed the median and collided head-on with my vehicle. The impact was severe, and both vehicles sustained extensive damage. Emergency services were called, and I was transported to the hospital for evaluation.

VEHICLE INFORMATION:
- Year/Make/Model: 2022 Tesla Model 3
- VIN: 5YJ3E1EA8NF123456
- License: XYZ-7890

DAMAGE ESTIMATE:
- Vehicle total loss: $45,000.00
- Medical expenses: $12,500.00
- Total claim: $57,500.00

POLICY:
- Policy Number: POL-2024-001234
- Policyholder: Robert Johnson

I have police report number: PR-2024-0456
Hospital: City General Hospital, Case #789012

Please contact me urgently to process this claim.

Robert Johnson
robert.johnson@email.com
(555) 234-5678
```

### 4. Simple Claim
**Use Case**: Quick, low-value claims
**Template Name**: `simple_claim`

```
Subject: Fender Bender Claim

Hi,

I had a minor accident yesterday (January 20, 2024) around 10 AM. Another car backed into mine in a parking lot. Damage is minor - just a dent and scratch on the rear bumper.

Location: Shopping Center parking lot, 500 Main St
Damage: About $1,200
Policy: POL-2024-001234

Thanks,
Mike Wilson
mike.wilson@email.com
```

### 5. Phone Transcript
**Use Case**: Claims submitted via phone call
**Template Name**: `phone_transcript`

```
[PHONE CALL TRANSCRIPT]

Date: January 18, 2024
Time: 2:45 PM
Call Duration: 8 minutes

AGENT: Thank you for calling. How can I help you?

CUSTOMER: Hi, I need to file a claim. I had an accident yesterday.

AGENT: I'm sorry to hear that. Can you tell me what happened?

CUSTOMER: Yeah, so I was driving on Elm Street yesterday afternoon, around 3 PM. Another car ran a red light and hit the side of my car. It was pretty scary.

AGENT: I understand. Were you or anyone else injured?

CUSTOMER: No, thankfully everyone was okay. Just shaken up.

AGENT: Good to hear. Can you provide the location and damage estimate?

CUSTOMER: It happened at Elm Street and Maple Avenue. The body shop said it'll cost about $4,200 to fix. My policy number is POL-2024-001234.

AGENT: Thank you. I'll start processing your claim. You should receive a claim number within 24 hours.

CUSTOMER: Great, thanks for your help.

[END OF TRANSCRIPT]
```

### 6. Web Form Submission
**Use Case**: Online form submissions
**Template Name**: `web_form_submission`

```
CLAIM SUBMISSION FORM

Policy Number: POL-2024-001234
Claimant Name: Sarah Davis
Date of Incident: January 22, 2024
Time of Incident: 11:30 AM

Incident Type: Auto Accident
Location: Downtown intersection, 1st Street and Main Avenue

Description:
I was stopped at a red light when another vehicle rear-ended my car. The impact caused damage to my rear bumper and trunk. No injuries reported.

Vehicle Information:
- Year: 2019
- Make: Toyota
- Model: Camry
- License Plate: DEF-4567

Damage Estimate: $2,800.00

Contact:
Email: sarah.davis@email.com
Phone: (555) 345-6789

Additional Notes: Police report filed, report number PR-2024-0789
```

### 7. Fraud Risk Claim
**Use Case**: Testing fraud detection
**Template Name**: `fraud_risk_claim`

```
Subject: Stolen Vehicle Claim

URGENT - Vehicle Theft Report

My car was stolen on January 25, 2024. I parked it at 8 PM in front of my house at 789 Pine Street, and when I came out at 7 AM the next morning, it was gone.

VEHICLE DETAILS:
- 2021 BMW 3 Series
- Color: Black
- License: GHI-9012
- VIN: WBA3A5C59EK123456

VALUE: $38,000.00

POLICY: POL-2024-001234

I've filed a police report (PR-2024-1234) and contacted the police department. They're investigating.

Please process my claim as soon as possible.

David Lee
david.lee@email.com
(555) 456-7890
```

## 👤 Review Feedback Templates

### Approve Templates

**Simple Approve** (`approve`):
```
Approved - Verified all information matches policy coverage. Claim amount is within policy limits. Proceeding with processing.
```

**Approve with Notes** (`approve_with_notes`):
```
Approved with notes:
- Verified policy coverage
- Confirmed incident details match police report
- Amount is reasonable based on damage assessment
- Proceeding with claim processing
```

### Reject Templates

**Simple Reject** (`reject`):
```
Rejected - Policy does not cover this type of incident. Claimant's policy is for auto insurance, but this is a property damage claim.
```

**Reject with Reason** (`reject_with_reason`):
```
Rejected - Reason:
- Policy expired before incident date
- Coverage type mismatch
- Insufficient documentation provided
```

### Override Template

**Override** (`override`):
```
Override - AI decision was incorrect. After manual review:
- Policy coverage confirmed
- Additional documentation reviewed
- Approving claim despite initial AI assessment
```

### Request Information Template

**Request Info** (`request_info`):
```
Requesting additional information:
- Need police report for verification
- Require repair estimates from authorized shop
- Need photos of damage
- Please provide witness statements if available
```

## 🔍 Search Templates

- **By Name**: `John Doe`
- **By Policy**: `POL-2024-001234`
- **By Amount**: `$3,500`
- **By Date**: `2024-01-15`
- **By Type**: `auto`

## 🚀 How to Use Templates

### In Process Claim Page

1. Click any template button at the top of the page
2. The template will automatically load into the input field
3. Modify as needed or use as-is
4. Click "Process Claim" to submit

### In Review Queue Page

1. Select a review item from the queue
2. Click a feedback template button (Approve/Reject/Override)
3. The template will load into the feedback field
4. Modify as needed
5. Submit your review

### In Claims List Page

1. Click a search template button
2. The search query will populate automatically
3. Results will filter based on the search

## 💡 Tips for Demos

1. **Start Simple**: Use "Simple Claim" template for quick demos
2. **Show Variety**: Use different templates to show system flexibility
3. **High Value**: Use "High Value Claim" to demonstrate human review workflow
4. **Different Sources**: Show how system handles email, phone, and web form inputs
5. **Search Examples**: Use search templates to demonstrate filtering capabilities

## 📋 Template Customization

All templates are stored in `data_templates.py`. You can:
- Modify existing templates
- Add new templates
- Create templates for specific use cases
- Export templates for documentation

## 🔧 Programmatic Access

You can also use templates programmatically:

```python
from data_templates import get_template, list_templates

# Get a specific template
claim_data = get_template("claim", "auto_insurance_claim")

# List all available templates
all_claim_templates = list_templates("claim")
all_feedback_templates = list_templates("feedback")
```

## 📝 Notes

- All templates use policy number `POL-2024-001234` (matches sample policy in system)
- Dates are set to recent dates for realistic demos
- Amounts vary to show different processing scenarios
- Templates are designed to trigger different workflow paths

