"""
Review Queue - Manages claims requiring human review

The review queue determines which claims need human review based on
business rules (high fraud scores, large amounts, policy issues, etc.)
and manages the review workflow.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from ..domain.claim import Claim


class ReviewStatus(str, Enum):
    """Status of a review item"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    OVERRIDDEN = "overridden"


class ReviewPriority(str, Enum):
    """Priority level for review"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class ReviewItem:
    """
    Represents a claim that requires human review.
    
    This is a Value Object that captures all information needed
    for a human reviewer to make a decision.
    """
    claim_id: UUID
    claim: Claim
    priority: ReviewPriority
    reason: str  # Why this claim needs review
    ai_decision: str  # What the AI decided
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: ReviewStatus = ReviewStatus.PENDING
    assigned_to: Optional[str] = None  # Reviewer ID/name
    reviewed_at: Optional[datetime] = None
    human_decision: Optional[str] = None
    human_feedback: Optional[str] = None


class ReviewQueue:
    """
    Manages the queue of claims requiring human review.
    
    This follows the Queue pattern and determines which claims
    need human intervention based on business rules.
    """
    
    def __init__(self):
        """Initialize the review queue"""
        self._queue: List[ReviewItem] = []
        self._by_claim_id: dict[UUID, ReviewItem] = {}
    
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
            claim: The claim requiring review
            reason: Why this claim needs review
            ai_decision: What the AI decided
            priority: Priority level for review
        
        Returns:
            The created ReviewItem
        """
        # Check if already in queue
        if claim.claim_id in self._by_claim_id:
            return self._by_claim_id[claim.claim_id]
        
        review_item = ReviewItem(
            claim_id=claim.claim_id,
            claim=claim,
            priority=priority,
            reason=reason,
            ai_decision=ai_decision,
        )
        
        self._queue.append(review_item)
        self._by_claim_id[claim.claim_id] = review_item
        
        # Sort by priority (urgent first)
        priority_order = {
            ReviewPriority.URGENT: 0,
            ReviewPriority.HIGH: 1,
            ReviewPriority.MEDIUM: 2,
            ReviewPriority.LOW: 3,
        }
        self._queue.sort(key=lambda x: priority_order[x.priority])
        
        return review_item
    
    def get_next_pending(self, reviewer_id: Optional[str] = None) -> Optional[ReviewItem]:
        """
        Get the next pending review item.
        
        Args:
            reviewer_id: Optional reviewer ID to filter by assignment
        
        Returns:
            Next ReviewItem or None if queue is empty
        """
        for item in self._queue:
            if item.status == ReviewStatus.PENDING:
                if reviewer_id is None or item.assigned_to == reviewer_id:
                    return item
        return None
    
    def assign(self, review_item: ReviewItem, reviewer_id: str) -> None:
        """
        Assign a review item to a reviewer.
        
        Args:
            review_item: The review item to assign
            reviewer_id: ID of the reviewer
        """
        review_item.assigned_to = reviewer_id
        review_item.status = ReviewStatus.IN_REVIEW
    
    def complete_review(
        self,
        review_item: ReviewItem,
        decision: str,
        feedback: Optional[str] = None
    ) -> None:
        """
        Complete a review with human decision.
        
        Args:
            review_item: The review item being completed
            decision: Human decision (approved, rejected, overridden)
            feedback: Optional feedback from reviewer
        """
        review_item.status = ReviewStatus(decision.lower())
        review_item.human_decision = decision
        review_item.human_feedback = feedback
        review_item.reviewed_at = datetime.utcnow()
    
    def get_by_claim_id(self, claim_id: UUID) -> Optional[ReviewItem]:
        """Get review item by claim ID"""
        return self._by_claim_id.get(claim_id)
    
    def get_all_pending(self) -> List[ReviewItem]:
        """Get all pending review items"""
        return [item for item in self._queue if item.status == ReviewStatus.PENDING]
    
    def get_all(self) -> List[ReviewItem]:
        """Get all review items"""
        return self._queue.copy()
    
    def clear(self) -> None:
        """Clear the queue (useful for testing)"""
        self._queue.clear()
        self._by_claim_id.clear()

