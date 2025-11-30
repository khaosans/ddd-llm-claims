"""
Fraud Detection Agent - Detects fraud and anomalies in claims

This agent acts as an Anti-Corruption Layer (ACL) that:
1. Analyzes claims for fraud indicators using LLM
2. Integrates with FraudPatternStore for pattern matching
3. Returns FraudCheckResult value object
4. Publishes domain events for audit trail

This is a Subdomain agent - it supports the Core Domain but isn't core itself.
"""

import json
import re
from decimal import Decimal
from typing import Optional
from uuid import UUID

from ..domain.claim import Claim
from ..domain.fraud import FraudCheckResult, FraudRiskLevel
from ..domain.fraud.events import FraudScoreCalculated
from ..domain.events import DomainEvent
from .base_agent import BaseAgent
from .json_utils import parse_json_resilient, extract_json_from_text, clean_json_string
from ..compliance.decision_audit import get_audit_service
from ..compliance.decision_context import DecisionContextTracker
from ..compliance.models import DecisionType
from ..vector_store.fraud_pattern_store import FraudPatternStore


class FraudAgent(BaseAgent):
    """
    Fraud Detection Agent - Detects fraud and anomalies in claims.
    
    DDD Role: Anti-Corruption Layer (ACL) for fraud detection.
    
    This agent:
    1. Analyzes claims for fraud indicators using LLM
    2. Uses FraudPatternStore for pattern matching
    3. Applies rule-based checks (amount thresholds, frequency, etc.)
    4. Returns FraudCheckResult value object
    5. Publishes FraudScoreCalculated domain event
    """
    
    def __init__(self, model_provider, temperature: float = 0.2, fraud_pattern_store: Optional[FraudPatternStore] = None):
        """
        Initialize the fraud agent.
        
        Args:
            model_provider: The LLM provider to use
            temperature: Sampling temperature (low for consistent fraud detection)
            fraud_pattern_store: Optional fraud pattern store for pattern matching
        """
        super().__init__(model_provider, temperature)
        self.fraud_pattern_store = fraud_pattern_store
    
    def get_system_prompt(self) -> str:
        """System prompt for fraud detection"""
        return """You are a Fraud Detection Specialist for an insurance company.
Your job is to analyze claims for fraud indicators and suspicious patterns.

Analyze claims for:
1. FRAUD INDICATORS:
   - Suspicious timing (claim filed immediately after policy start)
   - Inflated damage amounts (unusually high repair costs)
   - Inconsistent stories (contradictory details)
   - Missing documentation (insufficient evidence)
   - Duplicate claims (same incident claimed multiple times)
   - Stolen vehicle patterns (suspicious theft claims)

2. DATA QUALITY ISSUES:
   - Missing critical fields (incomplete information)
   - Invalid date formats or inconsistencies
   - Invalid amount formats
   - Missing policy information

3. POLICY ANOMALIES:
   - Claims on expired policies
   - Coverage mismatches (claim type not covered)
   - Amount exceeds coverage limits

4. TEMPORAL PATTERNS:
   - Multiple claims in short timeframe
   - Suspicious timing patterns

5. BEHAVIORAL PATTERNS:
   - Unusual claimant behavior
   - Patterns matching known fraud cases

Output ONLY valid JSON:
{
    "fraud_score": 0.0-1.0 (decimal number, higher = more suspicious),
    "risk_level": "low" | "medium" | "high" | "critical",
    "is_suspicious": true or false,
    "risk_factors": ["array", "of", "identified", "risk", "factors"],
    "confidence": 0.0-1.0 (optional, confidence in assessment)
}

Scoring Guidelines:
- 0.0-0.3: LOW risk (normal claim, minor data quality issues)
- 0.3-0.6: MEDIUM risk (some concerns, needs review)
- 0.6-0.8: HIGH risk (multiple red flags, likely fraud)
- 0.8-1.0: CRITICAL risk (clear fraud indicators)

Be thorough and precise. Consider all available information."""
    
    async def process(
        self,
        claim: Claim,
        claim_id: Optional[UUID] = None,
    ) -> FraudCheckResult:
        """
        Analyze claim for fraud and anomalies.
        
        Args:
            claim: The claim to analyze
            claim_id: Optional claim ID for decision tracking
        
        Returns:
            FraudCheckResult value object
        """
        # Initialize decision context tracker
        tracker = DecisionContextTracker()
        tracker.set_prompt(self.get_system_prompt())
        
        # Build claim context
        claim_data = {
            "claim_id": str(claim.claim_id),
            "status": claim.status.value,
            "source": claim.source,
            "raw_input": claim.raw_input[:500],  # First 500 chars for context
        }
        
        if claim.summary:
            claim_data.update({
                "claim_type": claim.summary.claim_type,
                "incident_date": claim.summary.incident_date.isoformat() if claim.summary.incident_date else None,
                "reported_date": claim.summary.reported_date.isoformat() if claim.summary.reported_date else None,
                "claimed_amount": str(claim.summary.claimed_amount),
                "currency": claim.summary.currency,
                "incident_location": claim.summary.incident_location,
                "description": claim.summary.description,
                "claimant_name": claim.summary.claimant_name,
                "policy_number": claim.summary.policy_number,
            })
        
        tracker.add_input("claim_data", claim_data)
        
        # Check fraud pattern store for similar patterns
        pattern_matches = []
        if self.fraud_pattern_store and claim.summary:
            try:
                claim_text = claim.summary.description or claim.raw_input
                pattern_matches = self.fraud_pattern_store.detect_similar_patterns(
                    claim_text,
                    n_results=3
                )
                if pattern_matches:
                    tracker.add_evidence("pattern_matches", [
                        {
                            "pattern_id": p.get("pattern_id"),
                            "distance": p.get("distance", 0.0),
                            "metadata": p.get("metadata", {}),
                        }
                        for p in pattern_matches
                    ])
            except Exception as e:
                # Pattern store errors shouldn't block fraud detection
                tracker.add_intermediate_step("pattern_store_error", {"error": str(e)})
        
        # Apply rule-based checks
        rule_based_checks = self._apply_rule_based_checks(claim)
        tracker.add_evidence("rule_based_checks", rule_based_checks)
        
        # Build prompt for LLM
        prompt = f"""Analyze this claim for fraud indicators and anomalies:

CLAIM INFORMATION:
{json.dumps(claim_data, indent=2)}

RULE-BASED CHECKS:
{json.dumps(rule_based_checks, indent=2)}

{f'PATTERN MATCHES: {json.dumps([p.get("pattern_id") for p in pattern_matches], indent=2)}' if pattern_matches else ''}

Analyze this claim comprehensively. Consider:
- Fraud indicators (suspicious timing, inflated amounts, inconsistencies)
- Data quality issues (missing fields, invalid formats)
- Policy anomalies (coverage mismatches, expired policies)
- Temporal patterns (multiple claims, suspicious timing)
- Behavioral patterns (unusual claimant behavior)

Output JSON with your fraud assessment."""
        
        raw_output = await self.generate(prompt)
        tracker.set_llm_response(raw_output)
        
        # Parse and validate output with multiple strategies
        result = None
        
        # Strategy 1: Try resilient parsing
        result = parse_json_resilient(raw_output, max_attempts=5)
        
        # Strategy 2: Try extracting JSON and parsing
        if result is None:
            extracted = extract_json_from_text(raw_output)
            if extracted and extracted.strip():
                try:
                    # Clean the extracted JSON
                    cleaned = clean_json_string(extracted)
                    result = json.loads(cleaned)
                except json.JSONDecodeError:
                    # Try parsing without cleaning
                    try:
                        result = json.loads(extracted)
                    except json.JSONDecodeError:
                        pass
        
        # Strategy 3: Try to infer fraud score from text if no JSON found
        if result is None:
            result = self._infer_fraud_from_text(raw_output, rule_based_checks)
        
        # Strategy 4: Fallback to rule-based assessment only
        if result is None:
            # Use rule-based checks as fallback
            result = self._create_fallback_result(rule_based_checks, raw_output)
            
            # Log fallback usage
            if claim_id:
                audit_service = get_audit_service()
                audit_service.capture_decision(
                    claim_id=claim_id,
                    agent_component="FraudAgent",
                    decision_type=DecisionType.FRAUD_ASSESSMENT,
                    decision_value=result,
                    reasoning=f"Fraud detection: Used fallback rule-based assessment (LLM JSON parsing failed). Raw output preview: {raw_output[:200]}...",
                    context=tracker.build_context(),
                    success=True,  # Still successful, just using fallback
                    error_message=f"LLM returned non-JSON response, using rule-based fallback",
                )
        
        # Extract fraud assessment data
        fraud_score = Decimal(str(result.get("fraud_score", 0.1)))
        risk_level_str = result.get("risk_level", "low").lower()
        is_suspicious = result.get("is_suspicious", False)
        risk_factors = result.get("risk_factors", [])
        confidence = result.get("confidence")
        
        # Map risk level string to enum
        risk_level_map = {
            "low": FraudRiskLevel.LOW,
            "medium": FraudRiskLevel.MEDIUM,
            "high": FraudRiskLevel.HIGH,
            "critical": FraudRiskLevel.CRITICAL,
        }
        risk_level = risk_level_map.get(risk_level_str, FraudRiskLevel.LOW)
        
        # Combine rule-based checks with LLM analysis
        # If rule-based checks flag high risk, increase score
        if rule_based_checks.get("high_risk_flags", 0) > 0:
            fraud_score = max(fraud_score, Decimal("0.6"))
            if risk_level == FraudRiskLevel.LOW:
                risk_level = FraudRiskLevel.MEDIUM
        
        # Add rule-based risk factors
        rule_factors = rule_based_checks.get("risk_factors", [])
        if rule_factors:
            risk_factors.extend(rule_factors)
        
        # Create FraudCheckResult value object
        fraud_result = FraudCheckResult(
            fraud_score=fraud_score,
            risk_level=risk_level,
            is_suspicious=is_suspicious or risk_level in [FraudRiskLevel.HIGH, FraudRiskLevel.CRITICAL],
            risk_factors=risk_factors,
            assessment_method="llm_agent",
            confidence=Decimal(str(confidence)) if confidence is not None else None,
        )
        
        # Add evidence
        tracker.add_evidence("fraud_assessment", {
            "fraud_score": float(fraud_score),
            "risk_level": risk_level.value,
            "is_suspicious": fraud_result.is_suspicious,
            "risk_factors_count": len(risk_factors),
        })
        
        # Capture decision
        if claim_id:
            audit_service = get_audit_service()
            audit_service.capture_decision(
                claim_id=claim_id,
                agent_component="FraudAgent",
                decision_type=DecisionType.FRAUD_ASSESSMENT,
                decision_value={
                    "fraud_score": float(fraud_score),
                    "risk_level": risk_level.value,
                    "is_suspicious": fraud_result.is_suspicious,
                    "risk_factors": risk_factors,
                },
                reasoning=f"Fraud assessment: score {fraud_score}, risk level {risk_level.value}. Risk factors: {', '.join(risk_factors[:3]) if risk_factors else 'none'}",
                context=tracker.build_context(),
                success=True,
            )
        
        return fraud_result
    
    def _apply_rule_based_checks(self, claim: Claim) -> dict:
        """
        Apply rule-based fraud checks.
        
        These are deterministic checks that don't require LLM analysis.
        
        Args:
            claim: The claim to check
        
        Returns:
            Dictionary with rule-based check results
        """
        checks = {
            "high_risk_flags": 0,
            "risk_factors": [],
            "warnings": [],
        }
        
        if not claim.summary:
            checks["warnings"].append("No claim summary available for rule-based checks")
            return checks
        
        # Check for unusually high amounts
        if claim.summary.claimed_amount > Decimal("100000"):
            checks["high_risk_flags"] += 1
            checks["risk_factors"].append("Unusually high claim amount (>$100,000)")
        
        # Check for suspicious timing (claim filed very quickly after policy start)
        if claim.summary.incident_date and claim.summary.reported_date:
            from datetime import timedelta
            time_diff = claim.summary.reported_date - claim.summary.incident_date
            if time_diff.days < 1:
                checks["high_risk_flags"] += 1
                checks["risk_factors"].append("Claim reported very quickly after incident (< 1 day)")
        
        # Check for missing critical fields
        missing_fields = []
        if not claim.summary.claimant_name:
            missing_fields.append("claimant_name")
        if not claim.summary.incident_location:
            missing_fields.append("incident_location")
        if not claim.summary.description:
            missing_fields.append("description")
        
        if missing_fields:
            checks["risk_factors"].append(f"Missing critical fields: {', '.join(missing_fields)}")
        
        # Check for negative or zero amounts
        if claim.summary.claimed_amount <= 0:
            checks["warnings"].append("Claim amount is zero or negative")
        
        return checks
    
    def _infer_fraud_from_text(self, text: str, rule_based_checks: dict) -> Optional[dict]:
        """
        Try to infer fraud assessment from text when JSON parsing fails.
        
        Looks for keywords and patterns in the text to estimate fraud score.
        
        Args:
            text: LLM response text
            rule_based_checks: Rule-based check results
        
        Returns:
            Dict with fraud assessment, or None if inference fails
        """
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Look for fraud score mentions
        score_patterns = [
            r'fraud[_\s]*score[:\s]*([0-9.]+)',
            r'score[:\s]*([0-9.]+)',
            r'risk[_\s]*score[:\s]*([0-9.]+)',
        ]
        
        fraud_score = None
        for pattern in score_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    fraud_score = float(match.group(1))
                    # Normalize to 0-1 range if needed
                    if fraud_score > 1.0:
                        fraud_score = fraud_score / 100.0
                    break
                except ValueError:
                    continue
        
        # Look for risk level mentions
        risk_level = None
        if any(word in text_lower for word in ['critical', 'very high', 'extremely high']):
            risk_level = 'critical'
        elif any(word in text_lower for word in ['high risk', 'high']):
            risk_level = 'high'
        elif any(word in text_lower for word in ['medium', 'moderate']):
            risk_level = 'medium'
        elif any(word in text_lower for word in ['low risk', 'low']):
            risk_level = 'low'
        
        # Look for suspicious indicators
        is_suspicious = any(word in text_lower for word in [
            'suspicious', 'fraud', 'anomaly', 'unusual', 'concerning',
            'red flag', 'warning', 'investigate'
        ])
        
        # Extract risk factors
        risk_factors = []
        risk_factor_keywords = [
            'suspicious timing', 'inflated', 'inconsistent', 'missing documentation',
            'duplicate', 'stolen', 'expired policy', 'coverage mismatch'
        ]
        for keyword in risk_factor_keywords:
            if keyword in text_lower:
                risk_factors.append(keyword.replace('_', ' ').title())
        
        # Use rule-based checks if available
        if rule_based_checks.get("risk_factors"):
            risk_factors.extend(rule_based_checks["risk_factors"])
        
        # Determine default values if not found
        if fraud_score is None:
            if is_suspicious or risk_level in ['high', 'critical']:
                fraud_score = 0.6
            elif risk_level == 'medium':
                fraud_score = 0.4
            else:
                fraud_score = 0.2
        
        if risk_level is None:
            if fraud_score >= 0.7:
                risk_level = 'critical'
            elif fraud_score >= 0.5:
                risk_level = 'high'
            elif fraud_score >= 0.3:
                risk_level = 'medium'
            else:
                risk_level = 'low'
        
        return {
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "is_suspicious": is_suspicious or fraud_score >= 0.5,
            "risk_factors": risk_factors[:10],  # Limit to 10 factors
            "confidence": 0.5,  # Lower confidence for inferred results
        }
    
    def _create_fallback_result(self, rule_based_checks: dict, raw_output: str) -> dict:
        """
        Create a fallback fraud assessment result using only rule-based checks.
        
        Args:
            rule_based_checks: Rule-based check results
            raw_output: Raw LLM output (for logging)
        
        Returns:
            Dict with fraud assessment
        """
        # Base score on rule-based checks
        high_risk_flags = rule_based_checks.get("high_risk_flags", 0)
        risk_factors = rule_based_checks.get("risk_factors", [])
        
        if high_risk_flags >= 2:
            fraud_score = 0.7
            risk_level = "high"
            is_suspicious = True
        elif high_risk_flags >= 1:
            fraud_score = 0.5
            risk_level = "medium"
            is_suspicious = True
        elif risk_factors:
            fraud_score = 0.3
            risk_level = "medium"
            is_suspicious = False
        else:
            fraud_score = 0.1
            risk_level = "low"
            is_suspicious = False
        
        return {
            "fraud_score": fraud_score,
            "risk_level": risk_level,
            "is_suspicious": is_suspicious,
            "risk_factors": risk_factors,
            "confidence": 0.6,  # Moderate confidence for rule-based only
        }
    
    async def assess_claim(self, claim: Claim) -> FraudScoreCalculated:
        """
        Assess a claim for fraud and return domain event.
        
        Args:
            claim: The claim to assess
        
        Returns:
            FraudScoreCalculated domain event
        """
        fraud_result = await self.process(claim, claim_id=claim.claim_id)
        
        # Create domain event
        event = FraudScoreCalculated(
            claim_id=claim.claim_id,
            fraud_result=fraud_result,
        )
        
        return event

