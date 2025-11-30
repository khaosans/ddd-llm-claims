"""
Review Interface - CLI interface for human reviewers

Provides a simple command-line interface for human reviewers to
review claims, make decisions, and provide feedback.
"""

from typing import Optional
from uuid import UUID

from ..domain.claim import Claim
from .review_queue import ReviewQueue, ReviewItem, ReviewStatus


class ReviewInterface:
    """
    CLI interface for human reviewers.
    
    Provides a simple, pragmatic interface for reviewing claims.
    In production, this could be replaced with a web interface.
    """
    
    def __init__(self, review_queue: ReviewQueue):
        """
        Initialize the review interface.
        
        Args:
            review_queue: The review queue to work with
        """
        self.review_queue = review_queue
    
    def display_review_item(self, item: ReviewItem) -> None:
        """
        Display a review item for human review.
        
        Args:
            item: The review item to display
        """
        print("\n" + "="*70)
        print("CLAIM REVIEW")
        print("="*70)
        print(f"\nClaim ID: {item.claim_id}")
        print(f"Priority: {item.priority.value.upper()}")
        print(f"Reason for Review: {item.reason}")
        print(f"\nAI Decision: {item.ai_decision}")
        
        if item.claim.summary:
            summary = item.claim.summary
            print(f"\nClaim Summary:")
            print(f"  Type: {summary.claim_type}")
            print(f"  Amount: ${summary.claimed_amount}")
            print(f"  Location: {summary.incident_location}")
            print(f"  Claimant: {summary.claimant_name}")
            print(f"  Incident Date: {summary.incident_date}")
            print(f"  Description: {summary.description}")
        
        print(f"\nCurrent Status: {item.claim.status.value}")
        print(f"Created: {item.created_at}")
        print("="*70)
    
    def get_human_decision(self) -> tuple[str, Optional[str]]:
        """
        Get human decision and feedback.
        
        Returns:
            Tuple of (decision, feedback)
            decision: 'approved', 'rejected', or 'overridden'
            feedback: Optional feedback text
        """
        print("\nReview Options:")
        print("  1. Approve (accept AI decision)")
        print("  2. Reject (reject AI decision)")
        print("  3. Override (change AI decision)")
        print("  0. Skip (review later)")
        
        choice = input("\nEnter your choice (0-3): ").strip()
        
        if choice == "0":
            return ("skip", None)
        elif choice == "1":
            feedback = input("Optional feedback (press Enter to skip): ").strip()
            return ("approved", feedback if feedback else None)
        elif choice == "2":
            feedback = input("Reason for rejection (required): ").strip()
            if not feedback:
                print("Feedback required for rejection")
                return self.get_human_decision()
            return ("rejected", feedback)
        elif choice == "3":
            feedback = input("Override details (required): ").strip()
            if not feedback:
                print("Override details required")
                return self.get_human_decision()
            return ("overridden", feedback)
        else:
            print("Invalid choice. Please try again.")
            return self.get_human_decision()
    
    def review_next(self, reviewer_id: str = "reviewer1") -> Optional[ReviewItem]:
        """
        Review the next pending claim.
        
        Args:
            reviewer_id: ID of the reviewer
        
        Returns:
            The reviewed item, or None if no items pending
        """
        item = self.review_queue.get_next_pending()
        if not item:
            print("\nNo claims pending review.")
            return None
        
        # Assign to reviewer
        self.review_queue.assign(item, reviewer_id)
        
        # Display for review
        self.display_review_item(item)
        
        # Get human decision
        decision, feedback = self.get_human_decision()
        
        if decision == "skip":
            item.status = ReviewStatus.PENDING
            item.assigned_to = None
            print("\nReview skipped. Item returned to queue.")
            return item
        
        # Complete review
        self.review_queue.complete_review(item, decision, feedback)
        
        print(f"\n✓ Review completed: {decision.upper()}")
        if feedback:
            print(f"  Feedback: {feedback}")
        
        return item
    
    def review_claim(self, claim_id: UUID, reviewer_id: str = "reviewer1") -> Optional[ReviewItem]:
        """
        Review a specific claim by ID.
        
        Args:
            claim_id: ID of the claim to review
            reviewer_id: ID of the reviewer
        
        Returns:
            The reviewed item, or None if not found
        """
        item = self.review_queue.get_by_claim_id(claim_id)
        if not item:
            print(f"\nClaim {claim_id} not found in review queue.")
            return None
        
        return self.review_next(reviewer_id)
    
    def list_pending(self) -> None:
        """List all pending review items"""
        pending = self.review_queue.get_all_pending()
        if not pending:
            print("\nNo claims pending review.")
            return
        
        print(f"\nPending Reviews: {len(pending)}")
        print("-"*70)
        for i, item in enumerate(pending, 1):
            print(f"{i}. Claim {item.claim_id}")
            print(f"   Priority: {item.priority.value.upper()}")
            print(f"   Reason: {item.reason}")
            print(f"   AI Decision: {item.ai_decision}")
            if item.assigned_to:
                print(f"   Assigned to: {item.assigned_to}")
            print()

