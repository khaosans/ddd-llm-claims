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

    # Additional Claim Types - Legitimate
    "health_insurance_claim": """Subject: Medical Claim Submission

Dear Insurance Provider,

I am submitting a claim for medical expenses incurred on February 5, 2024.

PATIENT INFORMATION:
- Name: Maria Rodriguez
- Date of Birth: March 15, 1985
- Policy Number: POL-2024-001234

MEDICAL SERVICES:
- Date of Service: February 5, 2024
- Provider: City Medical Center
- Diagnosis: Sprained ankle from fall
- Treatment: X-ray, examination, pain medication
- Total Charges: $1,850.00

INCIDENT DETAILS:
I slipped on ice in a parking lot and injured my ankle. I was seen at the emergency room and received treatment.

I have attached the medical bills and receipts.

Thank you,
Maria Rodriguez
maria.rodriguez@email.com
(555) 567-8901""",

    "life_insurance_claim": """Subject: Life Insurance Claim - Death Benefit

Dear Insurance Company,

I am filing a claim for the death benefit under policy POL-2024-001234.

DECEDENT INFORMATION:
- Name: James Wilson
- Date of Birth: June 10, 1950
- Date of Death: January 20, 2024
- Cause of Death: Natural causes (heart failure)

BENEFICIARY INFORMATION:
- Name: Sarah Wilson (spouse)
- Relationship: Wife
- Contact: sarah.wilson@email.com, (555) 678-9012

POLICY DETAILS:
- Policy Number: POL-2024-001234
- Coverage Amount: $250,000.00
- Policy Type: Term Life Insurance

I have attached the death certificate and required documentation.

Sincerely,
Sarah Wilson""",

    "disability_insurance_claim": """Subject: Disability Claim - Unable to Work

Hello,

I need to file a disability claim. I was injured at work on January 25, 2024 and cannot perform my job duties.

CLAIMANT: Michael Chen
POLICY: POL-2024-001234
DATE OF INJURY: January 25, 2024

INJURY DETAILS:
I injured my back while lifting heavy equipment at my construction job. My doctor has placed me on medical leave for 6-8 weeks.

MEDICAL INFORMATION:
- Treating Physician: Dr. Emily Johnson
- Diagnosis: Herniated disc, L4-L5
- Treatment: Physical therapy, medication, rest
- Expected Recovery: 6-8 weeks

I have attached medical documentation and work restrictions.

Thank you,
Michael Chen
michael.chen@email.com
(555) 789-0123""",

    "travel_insurance_claim": """Subject: Travel Insurance Claim - Trip Cancellation

Dear Travel Insurance,

I need to file a claim for trip cancellation due to medical emergency.

POLICY: POL-2024-001234
TRIP DATES: February 15-22, 2024
CANCELLATION DATE: February 10, 2024

REASON FOR CANCELLATION:
My mother was hospitalized on February 8, 2024 with a serious medical condition. I had to cancel my trip to care for her.

TRIP DETAILS:
- Destination: Paris, France
- Total Trip Cost: $4,200.00
- Non-refundable Amount: $3,800.00

I have attached medical documentation from the hospital and cancellation receipts from the travel agency.

Best regards,
Jennifer Martinez
jennifer.martinez@email.com
(555) 890-1234""",

    # Additional Fraud/Issue Scenarios
    "multiple_vehicles_stolen": """Subject: Another Stolen Vehicle Claim

Hi Insurance,

This is my second stolen vehicle claim this year. My car was stolen again on February 1, 2024. I parked it at the grocery store at 2 PM and when I came out at 3 PM it was gone.

VEHICLE: 2022 Ford F-150
VALUE: $42,000.00
POLICY: POL-2024-001234

(I already filed a claim for a stolen 2021 Toyota Camry in January)

Please process quickly. I need the money.

Thanks,
Chris Anderson
chris.anderson@email.com""",

    "excessive_medical_claims": """Subject: Medical Claim - Third This Month

Hello,

I'm filing another medical claim. This is my third one this month.

PATIENT: Robert Smith
POLICY: POL-2024-001234
DATE: February 15, 2024

I went to three different doctors today:
1. Dr. Johnson - $1,200
2. Dr. Williams - $950
3. Dr. Brown - $1,350
Total: $3,500.00

All for the same back pain. Each doctor gave me different treatments.

Please pay all three claims.

Thanks,
Robert Smith
robert.smith@email.com""",

    "policy_lapse_claim": """Subject: Claim for Lapsed Policy

Dear Insurance,

I need to file a claim for an accident that happened on February 1, 2024. I know my policy lapsed on January 31, 2024 because I forgot to pay, but I think you should still cover it since it was only one day.

INCIDENT: Car accident
DATE: February 1, 2024
DAMAGE: $5,500.00
POLICY: POL-2024-001234 (lapsed Jan 31)

I'm going to pay my premium now, so please process the claim.

Thanks,
Lisa Johnson
lisa.johnson@email.com""",

    "coordinate_fraud": """Subject: Accident Claim

Hi,

I had an accident on February 5, 2024. My friend was driving my car and hit another car. The other driver was also my friend. We all agreed to file claims and split the money.

INCIDENT: Collision
DATE: February 5, 2024
DAMAGE: $8,000.00
POLICY: POL-2024-001234

My friend's insurance is also filing a claim for the same accident.

Please process.

Thanks,
David Kim
david.kim@email.com""",

    "good_legitimate_claim": """Subject: Auto Insurance Claim - Complete Documentation

Dear Insurance Company,

I am filing a claim for a car accident that occurred on February 10, 2024 at 3:45 PM.

INCIDENT DETAILS:
- Date: February 10, 2024
- Time: 3:45 PM
- Location: 1234 Main Street, Springfield, IL 62701
- Weather: Clear, dry conditions
- Traffic: Light

ACCIDENT DESCRIPTION:
I was stopped at a red light when another vehicle rear-ended my car. The other driver admitted fault and provided their insurance information. Police were called and a report was filed (Report #PR-2024-2345).

VEHICLE INFORMATION:
- Year/Make/Model: 2021 Toyota Camry
- VIN: 4T1B11HK5MU123456
- License Plate: IL-ABC-1234
- Current Mileage: 28,450

DAMAGE ASSESSMENT:
- Repair Estimate: $3,200.00 (from authorized Toyota dealer)
- Photos: Attached (6 photos showing damage)
- Police Report: PR-2024-2345

POLICY INFORMATION:
- Policy Number: POL-2024-001234
- Policyholder: Emily Davis
- Coverage: Comprehensive and Collision

CONTACT INFORMATION:
- Email: emily.davis@email.com
- Phone: (555) 123-4567
- Address: 567 Oak Avenue, Springfield, IL 62702

I have attached all required documentation including photos, police report, and repair estimate.

Thank you for your prompt attention to this matter.

Sincerely,
Emily Davis""",

    "good_property_claim": """Subject: Property Damage Claim - Fire Damage

Dear Insurance Provider,

I am filing a claim for fire damage to my home that occurred on February 8, 2024.

INCIDENT DETAILS:
- Date: February 8, 2024
- Time: 11:30 PM
- Location: 789 Elm Street, Springfield, IL 62703
- Cause: Electrical fire in kitchen (determined by fire department)

DAMAGE ASSESSMENT:
- Kitchen: Complete loss, $15,000
- Adjacent rooms: Smoke damage, $8,500
- Personal property: $12,300
- Total: $35,800.00

FIRE DEPARTMENT:
- Responded: Springfield Fire Department
- Report Number: FD-2024-0567
- Cause: Electrical malfunction in kitchen outlet
- No injuries reported

POLICY INFORMATION:
- Policy Number: POL-2024-001234
- Policyholder: Thomas Anderson
- Coverage Type: Homeowners Insurance

DOCUMENTATION:
- Fire department report: FD-2024-0567
- Photos: Attached (15 photos)
- Contractor estimate: $35,800.00
- Inventory of damaged items: Attached

I have been staying with family while repairs are being made. The fire department has cleared the property for assessment.

Please contact me to schedule an inspection.

Thank you,
Thomas Anderson
thomas.anderson@email.com
(555) 234-5678""",

    "edge_case_zero_amount": """Subject: Claim Submission

Hi,

I had an accident but there's no damage. I'm filing a claim just in case something comes up later.

INCIDENT: Minor fender bender
DATE: February 12, 2024
DAMAGE: $0.00
POLICY: POL-2024-001234

Thanks,
Alex Brown
alex.brown@email.com""",

    "edge_case_very_old_incident": """Subject: Claim for Old Accident

Hello,

I'm filing a claim for an accident that happened 2 years ago on January 15, 2022. I just realized I never filed a claim for it.

INCIDENT: Car accident
DATE: January 15, 2022
DAMAGE: $4,500.00
POLICY: POL-2024-001234

Please process this old claim.

Thanks,
Patricia White
patricia.white@email.com""",

    "edge_case_future_date": """Subject: Accident Claim

Hi Insurance,

I'm filing a claim for an accident that will happen tomorrow, February 20, 2024. I know it's going to happen because I saw it in a dream.

INCIDENT: Car accident
DATE: February 20, 2024 (tomorrow)
DAMAGE: $6,000.00
POLICY: POL-2024-001234

Please approve the claim now so I'm ready.

Thanks,
Daniel Garcia
daniel.garcia@email.com""",

    "good_health_claim": """Subject: Medical Claim - Complete Documentation

Dear Insurance,

I am submitting a medical claim with complete documentation.

PATIENT: Susan Lee
POLICY: POL-2024-001234
DATE OF SERVICE: February 10, 2024

MEDICAL SERVICES:
- Provider: Springfield Medical Center
- Diagnosis: Broken wrist from fall
- Treatment: X-ray, cast application, follow-up care
- Total Charges: $2,450.00

INCIDENT:
I fell on ice in a parking lot on February 10, 2024 at 2:30 PM. I was taken to the emergency room where X-rays confirmed a broken wrist. A cast was applied and I was given pain medication.

DOCUMENTATION:
- Medical bills: Attached
- X-ray results: Attached
- Doctor's notes: Attached
- Receipts: Attached

Thank you,
Susan Lee
susan.lee@email.com
(555) 345-6789""",

    "bad_health_claim_missing_docs": """Subject: Medical Claim

Hi,

I need money for medical bills. I went to the doctor but I don't have any receipts or bills. Just trust me, it cost $5,000.

PATIENT: Mark Thompson
POLICY: POL-2024-001234
AMOUNT: $5,000.00

Please send payment.

Thanks,
Mark Thompson
mark.thompson@email.com""",
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

