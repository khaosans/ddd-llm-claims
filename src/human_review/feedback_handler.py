"""
Feedback Handler - Captures and processes human feedback

This module handles human feedback, stores it for analysis,
and can be used to improve the system over time.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .review_queue import ReviewItem


@dataclass
class FeedbackRecord:
    """
    Record of human feedback for analysis.
    
    This can be used to:
    - Identify patterns in human overrides
    - Improve AI prompts
    - Train models on human corrections
    - Generate analytics
    """
    claim_id: UUID
    review_item_id: UUID
    ai_decision: str
    human_decision: str
    human_feedback: Optional[str]
    review_reason: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    reviewer_id: Optional[str] = None


class FeedbackHandler:
    """
    Handles human feedback collection and analysis.
    
    Stores feedback records and provides analytics on
    human vs AI decision patterns.
    """
    
    def __init__(self):
        """Initialize the feedback handler"""
        self._feedback_records: List[FeedbackRecord] = []
    
    def record_feedback(self, review_item: ReviewItem) -> FeedbackRecord:
        """
        Record feedback from a completed review.
        
        Args:
            review_item: The completed review item
        
        Returns:
            The created feedback record
        """
        record = FeedbackRecord(
            claim_id=review_item.claim_id,
            review_item_id=review_item.claim_id,  # Using claim_id as item ID
            ai_decision=review_item.ai_decision,
            human_decision=review_item.human_decision or "",
            human_feedback=review_item.human_feedback,
            review_reason=review_item.reason,
            reviewer_id=review_item.assigned_to,
        )
        
        self._feedback_records.append(record)
        return record
    
    def get_feedback_for_claim(self, claim_id: UUID) -> List[FeedbackRecord]:
        """
        Get all feedback records for a specific claim.
        
        Args:
            claim_id: The claim ID
        
        Returns:
            List of feedback records
        """
        return [r for r in self._feedback_records if r.claim_id == claim_id]
    
    def get_override_patterns(self) -> dict:
        """
        Analyze patterns in human overrides.
        
        Returns:
            Dictionary with analytics on override patterns
        """
        total = len(self._feedback_records)
        if total == 0:
            return {
                "total_reviews": 0,
                "approval_rate": 0,
                "rejection_rate": 0,
                "override_rate": 0,
            }
        
        approved = sum(1 for r in self._feedback_records if r.human_decision == "approved")
        rejected = sum(1 for r in self._feedback_records if r.human_decision == "rejected")
        overridden = sum(1 for r in self._feedback_records if r.human_decision == "overridden")
        
        return {
            "total_reviews": total,
            "approval_rate": approved / total if total > 0 else 0,
            "rejection_rate": rejected / total if total > 0 else 0,
            "override_rate": overridden / total if total > 0 else 0,
            "approvals": approved,
            "rejections": rejected,
            "overrides": overridden,
        }
    
    def get_feedback_by_reason(self) -> dict:
        """
        Group feedback by review reason.
        
        Returns:
            Dictionary mapping reasons to feedback counts
        """
        reason_counts = {}
        for record in self._feedback_records:
            reason = record.review_reason
            if reason not in reason_counts:
                reason_counts[reason] = {"total": 0, "overrides": 0}
            reason_counts[reason]["total"] += 1
            if record.human_decision == "overridden":
                reason_counts[reason]["overrides"] += 1
        
        return reason_counts
    
    def get_all_feedback(self) -> List[FeedbackRecord]:
        """Get all feedback records"""
        return self._feedback_records.copy()
    
    def clear(self) -> None:
        """Clear all feedback (useful for testing)"""
        self._feedback_records.clear()

