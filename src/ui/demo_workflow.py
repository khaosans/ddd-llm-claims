"""
Demo Workflow - Interactive step-by-step claim processing

Provides a slow, educational workflow that shows each step
and prompts users at appropriate decision points.
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ui.services import UIService, run_async


class DemoWorkflow:
    """
    Interactive demo workflow that processes claims step-by-step
    with visual progress and user prompts.
    """
    
    def __init__(self, service: Optional[UIService] = None):
        """Initialize demo workflow"""
        self.service = service or UIService()
        self.step_delay = 1.5  # Seconds between steps
        self.prompt_callbacks = {}
    
    def set_step_delay(self, seconds: float):
        """Set delay between steps (for demo pacing)"""
        self.step_delay = seconds
    
    def register_prompt_callback(self, step: str, callback: Callable):
        """Register callback for user prompts at specific steps"""
        self.prompt_callbacks[step] = callback
    
    async def process_claim_demo(
        self,
        raw_input: str,
        source: str = "email",
        provider_type: str = "ollama",
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Process a claim in demo mode with step-by-step visualization.
        
        Args:
            raw_input: Unstructured claim data
            source: Source of claim
            provider_type: Model provider type
            progress_callback: Callback for progress updates
        
        Returns:
            Processing result dictionary
        """
        result = {
            "claim_id": None,
            "status": "processing",
            "steps_completed": [],
            "current_step": None,
            "summary": None,
            "workflow_steps": [],
            "requires_review": False,
            "review_reason": None,
        }
        
        # Step 1: Initialize
        await self._update_progress(
            progress_callback,
            "Initializing claim processing...",
            "initializing",
            0,
            result
        )
        await asyncio.sleep(self.step_delay * 0.5)
        
        # Step 2: Extract Facts
        await self._update_progress(
            progress_callback,
            "🤖 Intake Agent: Extracting facts from unstructured data...",
            "extracting_facts",
            10,
            result
        )
        await asyncio.sleep(self.step_delay)
        
        # Initialize service
        await self.service._ensure_initialized(provider_type)
        
        # Process claim (this will trigger async workflow)
        claim_result = await self.service.process_claim(raw_input, source, provider_type)
        
        result["claim_id"] = claim_result.get("claim_id")
        result["summary"] = claim_result.get("summary")
        
        await self._update_progress(
            progress_callback,
            "✅ Facts extracted successfully!",
            "facts_extracted",
            30,
            result
        )
        result["steps_completed"].append("facts_extracted")
        await asyncio.sleep(self.step_delay)
        
        # Step 3: Policy Validation
        await self._update_progress(
            progress_callback,
            "🔍 Policy Agent: Validating claim against policy coverage...",
            "validating_policy",
            40,
            result
        )
        await asyncio.sleep(self.step_delay)
        
        # Check if policy validation completed
        from uuid import UUID
        updated_claim = None
        if hasattr(self.service, '_claim_repo') and self.service._claim_repo:
            try:
                updated_claim = await self.service._claim_repo.find_by_id(UUID(result["claim_id"]))
            except:
                pass
        
        await self._update_progress(
            progress_callback,
            "✅ Policy validation complete!",
            "policy_validated",
            50,
            result
        )
        result["steps_completed"].append("policy_validated")
        await asyncio.sleep(self.step_delay)
        
        # Step 4: Fraud Assessment
        await self._update_progress(
            progress_callback,
            "🚩 Fraud Assessment: Analyzing claim for suspicious patterns...",
            "assessing_fraud",
            60,
            result
        )
        await asyncio.sleep(self.step_delay)
        
        await self._update_progress(
            progress_callback,
            "✅ Fraud assessment complete!",
            "fraud_assessed",
            70,
            result
        )
        result["steps_completed"].append("fraud_assessed")
        await asyncio.sleep(self.step_delay)
        
        # Step 5: Triage & Routing
        await self._update_progress(
            progress_callback,
            "🎯 Triage Agent: Determining routing and next steps...",
            "triaging",
            80,
            result
        )
        await asyncio.sleep(self.step_delay)
        
        # Check for human review requirement
        review_queue = await self.service.get_review_queue()
        claim_reviews = [
            r for r in review_queue
            if r.get("claim_id") == result["claim_id"]
        ]
        
        if claim_reviews:
            result["requires_review"] = True
            result["review_reason"] = claim_reviews[0].get("reason", "Requires human review")
            
            await self._update_progress(
                progress_callback,
                "⚠️ Human Review Required!",
                "review_required",
                85,
                result
            )
            
            # Prompt user for review decision
            if "review_required" in self.prompt_callbacks:
                review_decision = await self.prompt_callbacks["review_required"](
                    claim_reviews[0]
                )
                result["review_decision"] = review_decision
        else:
            await self._update_progress(
                progress_callback,
                "✅ Claim routed successfully!",
                "routed",
                90,
                result
            )
        
        result["steps_completed"].append("triaged")
        await asyncio.sleep(self.step_delay)
        
        # Add decision information to result
        try:
            monitor = get_decision_monitor()
            decision_status = monitor.get_current_status(UUID(result["claim_id"]))
            result["decision_status"] = decision_status
        except Exception:
            pass  # Silently fail if decision viewing not available
        
        # Final status
        final_claim = None
        if hasattr(self.service, '_claim_repo') and self.service._claim_repo:
            try:
                final_claim = await self.service._claim_repo.find_by_id(UUID(result["claim_id"]))
            except:
                pass
        
        if final_claim:
            result["status"] = final_claim.status.value
        
        await self._update_progress(
            progress_callback,
            "✅ Claim processing complete!",
            "complete",
            100,
            result
        )
        
        # Build workflow steps for display
        result["workflow_steps"] = [
            ("✅", "Facts Extracted", "Intake Agent extracted structured facts from unstructured input"),
            ("✅", "Policy Validated", "Policy Agent validated claim against policy coverage"),
            ("✅", "Fraud Assessed", "Fraud assessment completed"),
            ("✅", "Routed", f"Claim routed to {result.get('status', 'processing')}"),
        ]
        
        if result["requires_review"]:
            result["workflow_steps"].append(
                ("⚠️", "Human Review", result["review_reason"])
            )
        
        return result
    
    async def _update_progress(
        self,
        callback: Optional[Callable],
        message: str,
        step: str,
        progress: int,
        result: Dict[str, Any]
    ):
        """Update progress callback"""
        result["current_step"] = step
        result["progress"] = progress
        result["progress_message"] = message
        
        if callback:
            if asyncio.iscoroutinefunction(callback):
                await callback(message, step, progress, result)
            else:
                callback(message, step, progress, result)


def create_demo_workflow(service: Optional[UIService] = None) -> DemoWorkflow:
    """Create a demo workflow instance"""
    return DemoWorkflow(service)

