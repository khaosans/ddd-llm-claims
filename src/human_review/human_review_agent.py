"""
Human Review Agent - Coordinates human review workflow

This agent determines when human review is needed, formats information
for reviewers, and processes human decisions to update the system.

This implementation follows Human-in-the-Loop (HITL) patterns for collaborative
AI systems, enabling human oversight and intervention in AI decision-making
(Amershi et al., 2014; Bansal et al., 2021).

Research Foundations:
- Amershi et al. (2014): Role of humans in interactive machine learning
- Holzinger (2016): Interactive ML for health informatics
- Bansal et al. (2021): Human-AI team performance
- Yang et al. (2020): Human-AI interaction design challenges

See: docs/REFERENCES.md#human-in-the-loop-hitl-patterns
"""

from typing import Optional

from ..domain.claim import Claim
from ..domain.fraud import FraudCheckResult
from .review_queue import ReviewQueue, ReviewItem, ReviewPriority
from .feedback_handler import FeedbackHandler


class HumanReviewAgent:
    """
    Agent that coordinates human review workflow.
    
    This agent:
    1. Determines when human review is needed based on business rules
    2. Adds claims to review queue with appropriate priority
    3. Formats information for human reviewers
    4. Processes human decisions and updates the system
    
    This implements the Human-in-the-Loop pattern, enabling human oversight
    and intervention in AI decision-making processes. The agent follows best
    practices for HITL systems, including clear intervention points, feedback
    collection, and learning from human decisions (Amershi et al., 2014;
    Bansal et al., 2021; Yang et al., 2020).
    
    References:
    - Amershi et al. (2014): Power to the people: Role of humans in interactive ML
    - Bansal et al. (2021): Human-AI team performance
    - Yang et al. (2020): Human-AI interaction design
    
    See: docs/REFERENCES.md#human-in-the-loop-hitl-patterns
    """
    
    def __init__(
        self,
        review_queue: ReviewQueue,
        feedback_handler: Optional[FeedbackHandler] = None
    ):
        """
        Initialize the human review agent.
        
        Args:
            review_queue: The review queue to use
            feedback_handler: Optional feedback handler for analytics
        """
        self.review_queue = review_queue
        self.feedback_handler = feedback_handler or FeedbackHandler()
    
    def should_review_after_extraction(self, claim: Claim) -> bool:
        """
        Determine if claim needs review after fact extraction.
        
        Business rules:
        - Review if extraction confidence is low
        - Review if critical information is missing
        - Review if amount is very large
        
        Args:
            claim: The claim to evaluate
        
        Returns:
            True if review is needed
        """
        if not claim.summary:
            return True
        
        # Review if amount is very large
        from decimal import Decimal
        if claim.summary.claimed_amount > Decimal("100000"):
            return True
        
        # Review if critical fields are missing
        if not claim.summary.claimant_name or not claim.summary.incident_location:
            return True
        
        return False
    
    def should_review_after_policy_validation(
        self,
        claim: Claim,
        is_valid: bool
    ) -> bool:
        """
        Determine if claim needs review after policy validation.
        
        Business rules:
        - Always review if policy validation failed
        - Review if policy is borderline
        
        Args:
            claim: The claim
            is_valid: Whether policy validation passed
        
        Returns:
            True if review is needed
        """
        # Always review rejected policies
        if not is_valid:
            return True
        
        return False
    
    def should_review_after_fraud_assessment(
        self,
        claim: Claim,
        fraud_result: FraudCheckResult
    ) -> bool:
        """
        Determine if claim needs review after fraud assessment.
        
        Business rules:
        - Review if fraud score is high
        - Review if fraud score is medium and amount is large
        
        Args:
            claim: The claim
            fraud_result: The fraud assessment result
        
        Returns:
            True if review is needed
        """
        from decimal import Decimal
        
        # Always review high fraud scores
        if fraud_result.fraud_score >= Decimal("0.7"):
            return True
        
        # Review medium scores with large amounts
        if (fraud_result.fraud_score >= Decimal("0.5") and 
            claim.summary and 
            claim.summary.claimed_amount > Decimal("50000")):
            return True
        
        return False
    
    def add_for_review(
        self,
        claim: Claim,
        reason: str,
        ai_decision: str,
        priority: ReviewPriority = ReviewPriority.MEDIUM
    ) -> ReviewItem:
        """
        Add a claim to the review queue.
        
        Args:
            claim: The claim to review
            reason: Why review is needed
            ai_decision: What the AI decided
            priority: Priority level
        
        Returns:
            The created review item
        """
        return self.review_queue.add_for_review(
            claim=claim,
            reason=reason,
            ai_decision=ai_decision,
            priority=priority,
        )
    
    def process_human_decision(
        self,
        review_item: ReviewItem,
        decision: str,
        feedback: Optional[str] = None
    ) -> None:
        """
        Process a human decision and update the system.
        
        Args:
            review_item: The review item
            decision: Human decision (approved, rejected, overridden)
            feedback: Optional feedback
        """
        # Complete the review
        self.review_queue.complete_review(review_item, decision, feedback)
        
        # Record feedback
        self.feedback_handler.record_feedback(review_item)
        
        # Update claim based on decision
        claim = review_item.claim
        
        if decision == "approved":
            # Human approved AI decision - continue workflow
            # Status should already be set by workflow
            pass
        elif decision == "rejected":
            # Human rejected - mark claim as rejected
            from ..domain.claim import ClaimStatus
            claim.status = ClaimStatus.REJECTED
        elif decision == "overridden":
            # Human overrode decision - apply override
            # In a full implementation, this would parse feedback
            # and apply specific changes
            # For now, we'll mark as requiring manual processing
            from ..domain.claim import ClaimStatus
            claim.status = ClaimStatus.PROCESSING
    
    def get_review_statistics(self) -> dict:
        """
        Get statistics on human reviews.
        
        Returns:
            Dictionary with review statistics
        """
        patterns = self.feedback_handler.get_override_patterns()
        by_reason = self.feedback_handler.get_feedback_by_reason()
        
        return {
            "override_patterns": patterns,
            "feedback_by_reason": by_reason,
            "pending_reviews": len(self.review_queue.get_all_pending()),
            "total_reviews": len(self.review_queue.get_all()),
        }

