"""
Data Templates for Demo Purposes

Provides ready-to-use templates for all input fields in the application.
"""

# Claim Data Templates
CLAIM_TEMPLATES = {
    "auto_insurance_claim": """Subject: Auto Insurance Claim

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
John Doe""",

    "property_damage_claim": """Subject: Property Damage Claim - Water Damage

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
(555) 987-6543""",

    "high_value_claim": """Subject: Major Auto Accident Claim - Urgent

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
(555) 234-5678""",

    "simple_claim": """Subject: Fender Bender Claim

Hi,

I had a minor accident yesterday (January 20, 2024) around 10 AM. Another car backed into mine in a parking lot. Damage is minor - just a dent and scratch on the rear bumper.

Location: Shopping Center parking lot, 500 Main St
Damage: About $1,200
Policy: POL-2024-001234

Thanks,
Mike Wilson
mike.wilson@email.com""",

    "phone_transcript": """[PHONE CALL TRANSCRIPT]

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

[END OF TRANSCRIPT]""",

    "web_form_submission": """CLAIM SUBMISSION FORM

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

Additional Notes: Police report filed, report number PR-2024-0789""",

    "fraud_risk_claim": """Subject: Stolen Vehicle Claim

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
(555) 456-7890""",

    # Fraud Templates
    "stolen_vehicle_fraud": """Subject: Car Stolen - Need Immediate Payment

Hi,

My car was stolen yesterday. I just got my policy last week and now my car is gone. I parked it at the mall parking lot at 2 PM and when I came back at 3 PM it was stolen. This is very suspicious timing.

VEHICLE: 2023 Mercedes-Benz C-Class
VALUE: $55,000.00
POLICY: POL-2024-001234 (just started last week)

I need the money ASAP. Please process quickly.

Thanks,
Alex Thompson
alex.thompson@email.com""",

    "inflated_damage_claim": """Subject: Major Accident - High Repair Costs

Dear Insurance,

I had a minor fender bender in a parking lot on January 15, 2024. The other car barely touched mine, but the damage is extensive. My mechanic says it will cost $85,000 to repair. The entire front end needs replacement, engine work, transmission rebuild, and full body repaint.

INCIDENT: Parking lot collision at 5 MPH
DATE: January 15, 2024
DAMAGE: $85,000.00
VEHICLE: 2018 Honda Civic
POLICY: POL-2024-001234

Please approve this claim immediately.

Regards,
Michael Chen
michael.chen@email.com""",

    "duplicate_claim": """Subject: Car Accident Claim

Hello,

I'm filing a claim for the accident that happened on January 15, 2024 at Main Street. This is my second time filing for the same incident because I didn't hear back from you.

INCIDENT DATE: January 15, 2024
LOCATION: Main Street and Oak Avenue
DAMAGE: $3,500.00
POLICY: POL-2024-001234

Please process this claim. I already submitted it last week.

Thanks,
John Doe
john.doe@email.com""",

    "suspicious_timing": """Subject: Claim Filed - Policy Started Yesterday

Hi Insurance Company,

I just got my policy yesterday (January 14, 2024) and today (January 15, 2024) I had an accident. My car was hit while parked. The damage is $12,000.

POLICY START: January 14, 2024
INCIDENT DATE: January 15, 2024
DAMAGE: $12,000.00
POLICY: POL-2024-001234

Please process my claim.

Best,
Jennifer Martinez
jennifer.martinez@email.com""",

    "missing_documentation": """Subject: Claim Submission

I need to file a claim. Something happened to my car. I don't have any photos or police reports, but I need money for repairs.

DAMAGE: Around $5,000
POLICY: POL-2024-001234

Please send payment.

Thanks,
Robert Smith
robert.smith@email.com""",

    "inconsistent_story": """Subject: Car Accident Claim

Dear Insurance,

I was driving on Main Street on January 15, 2024 at 2 PM when another car hit me from behind. Actually, wait, it was at 3 PM. And I was stopped at a red light. No wait, I was making a left turn. The other driver ran a red light and hit me. Or maybe I ran the red light? I'm not sure exactly what happened but my car is damaged.

DATE: January 15, 2024 (or maybe January 16?)
TIME: 2 PM or 3 PM
LOCATION: Main Street (or maybe Oak Avenue?)
DAMAGE: $4,500.00
POLICY: POL-2024-001234

Please process my claim.

Sincerely,
Patricia Williams
patricia.williams@email.com""",

    # Data Quality Templates
    "missing_critical_fields": """Subject: Claim

Hi,

I need to file a claim. Something happened.

Thanks""",

    "invalid_date_format": """Subject: Auto Insurance Claim

Dear Insurance Company,

I am filing a claim for a car accident.

INCIDENT DETAILS:
- Date: Yesterday
- Time: Afternoon
- Location: Somewhere downtown
- Damage: $3,500.00

POLICY: POL-2024-001234

Thank you.

John Doe""",

    "invalid_amount_format": """Subject: Claim Submission

Hello,

I had an accident and need to claim money. The damage is about three thousand five hundred dollars, maybe more. Or less. I'm not sure exactly.

POLICY: POL-2024-001234

Thanks,
Mike Wilson""",

    "missing_policy_number": """Subject: Car Accident Claim

Hi Insurance,

I had a car accident on January 15, 2024. My car was damaged and I need to file a claim. I don't remember my policy number right now.

DAMAGE: $3,500.00
DATE: January 15, 2024

Please help.

Thanks,
Sarah Davis""",

    # Policy Anomaly Templates
    "expired_policy_claim": """Subject: Claim for Expired Policy

Dear Insurance,

I need to file a claim for an accident that happened on January 15, 2024. My policy expired on December 31, 2023, but I think you should still cover it.

INCIDENT DATE: January 15, 2024
DAMAGE: $3,500.00
POLICY: POL-2024-001234 (expired Dec 31, 2023)

Please process my claim.

Regards,
Thomas Anderson
thomas.anderson@email.com""",

    "coverage_mismatch": """Subject: Property Damage Claim

Hello,

I have an auto insurance policy (POL-2024-001234) and I need to file a claim for water damage to my apartment. The pipe burst and damaged my furniture.

INCIDENT DATE: January 15, 2024
DAMAGE: $8,500.00
POLICY: POL-2024-001234 (Auto Insurance)

Please process this property damage claim under my auto policy.

Thanks,
Lisa Brown
lisa.brown@email.com""",

    "amount_exceeds_coverage": """Subject: High Value Claim

Dear Insurance Company,

I had a major accident on January 15, 2024. My car was completely totaled and I need $150,000 to replace it. My policy covers up to $50,000 but I think you should pay the full amount.

INCIDENT DATE: January 15, 2024
CLAIMED AMOUNT: $150,000.00
POLICY: POL-2024-001234 (max coverage $50,000)

Please approve the full amount.

Sincerely,
David Miller
david.miller@email.com""",

    # Temporal Pattern Templates
    "multiple_claims_short_period": """Subject: Another Claim

Hi,

This is my third claim this month. I had another accident on January 20, 2024. This time someone hit my car while it was parked. The damage is $4,200.

INCIDENT DATE: January 20, 2024
DAMAGE: $4,200.00
POLICY: POL-2024-001234

(I already filed claims on January 5 and January 12)

Please process.

Thanks,
Chris Johnson
chris.johnson@email.com""",

    "claim_after_policy_start": """Subject: Immediate Claim After Policy Start

Hello Insurance,

I just started my policy on January 14, 2024 at 5 PM. On January 14, 2024 at 6 PM (one hour later), I had an accident. My car was hit while I was driving home from the insurance office.

POLICY START: January 14, 2024, 5:00 PM
INCIDENT DATE: January 14, 2024, 6:00 PM
DAMAGE: $6,500.00
POLICY: POL-2024-001234

Please process my claim.

Best regards,
Amanda Taylor
amanda.taylor@email.com""",
}

# Feedback Templates for Review Queue
FEEDBACK_TEMPLATES = {
    "approve": """Approved - Verified all information matches policy coverage. Claim amount is within policy limits. Proceeding with processing.""",
    
    "approve_with_notes": """Approved with notes:
- Verified policy coverage
- Confirmed incident details match police report
- Amount is reasonable based on damage assessment
- Proceeding with claim processing""",
    
    "reject": """Rejected - Policy does not cover this type of incident. Claimant's policy is for auto insurance, but this is a property damage claim.""",
    
    "reject_with_reason": """Rejected - Reason:
- Policy expired before incident date
- Coverage type mismatch
- Insufficient documentation provided""",
    
    "override": """Override - AI decision was incorrect. After manual review:
- Policy coverage confirmed
- Additional documentation reviewed
- Approving claim despite initial AI assessment""",
    
    "request_info": """Requesting additional information:
- Need police report for verification
- Require repair estimates from authorized shop
- Need photos of damage
- Please provide witness statements if available""",
}

# Search Query Templates
SEARCH_TEMPLATES = {
    "by_name": "John Doe",
    "by_policy": "POL-2024-001234",
    "by_amount": "$3,500",
    "by_date": "2024-01-15",
    "by_type": "auto",
}

def get_template(template_type: str, template_name: str = None) -> str:
    """
    Get a template by type and name.
    
    Args:
        template_type: Type of template ('claim', 'feedback', 'search')
        template_name: Specific template name (optional)
    
    Returns:
        Template string
    """
    if template_type == "claim":
        templates = CLAIM_TEMPLATES
    elif template_type == "feedback":
        templates = FEEDBACK_TEMPLATES
    elif template_type == "search":
        templates = SEARCH_TEMPLATES
    else:
        return ""
    
    if template_name and template_name in templates:
        return templates[template_name]
    
    # Return first template if name not specified
    if templates:
        return list(templates.values())[0]
    
    return ""

def list_templates(template_type: str) -> list:
    """List all available templates of a given type"""
    if template_type == "claim":
        return list(CLAIM_TEMPLATES.keys())
    elif template_type == "feedback":
        return list(FEEDBACK_TEMPLATES.keys())
    elif template_type == "search":
        return list(SEARCH_TEMPLATES.keys())
    return []

