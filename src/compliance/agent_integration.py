"""
Agent Integration Helpers

Provides decorators and utilities for integrating decision capture
into agents without modifying their core logic.
"""

import functools
from typing import Any, Callable, Optional
from uuid import UUID

from .decision_audit import DecisionAuditService, get_audit_service
from .decision_context import DecisionContextTracker
from .models import DecisionType, DecisionDependency


def capture_decision(
    decision_type: DecisionType,
    agent_name: str,
    extract_claim_id: Optional[Callable] = None,
    extract_reasoning: Optional[Callable] = None,
    extract_dependencies: Optional[Callable] = None,
    audit_service: Optional[DecisionAuditService] = None,
):
    """
    Decorator to automatically capture decisions made by agents.
    
    Args:
        decision_type: Type of decision being made
        agent_name: Name of the agent making the decision
        extract_claim_id: Function to extract claim_id from function args/kwargs
        extract_reasoning: Function to extract reasoning from return value
        extract_dependencies: Function to extract dependencies from function args/kwargs
        audit_service: Optional audit service (uses global if not provided)
    
    Usage:
        @capture_decision(
            DecisionType.FACT_EXTRACTION,
            "IntakeAgent",
            extract_claim_id=lambda args, kwargs: kwargs.get('claim').claim_id,
            extract_reasoning=lambda result: f"Extracted {len(result)} facts",
        )
        async def process(self, claim: Claim):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracker = DecisionContextTracker()
            success = True
            error_message = None
            result = None
            
            try:
                # Capture inputs
                tracker.add_inputs({
                    "args": str(args),
                    "kwargs_keys": list(kwargs.keys()),
                })
                
                # Extract claim_id if function provided
                claim_id = None
                if extract_claim_id:
                    try:
                        claim_id = extract_claim_id(args, kwargs)
                    except Exception:
                        pass
                
                # Try to extract claim_id from common patterns
                if not claim_id:
                    for arg in args:
                        if hasattr(arg, 'claim_id'):
                            claim_id = arg.claim_id
                            break
                    for value in kwargs.values():
                        if hasattr(value, 'claim_id'):
                            claim_id = value.claim_id
                            break
                
                # Execute the function
                result = await func(*args, **kwargs)
                
                # Extract reasoning
                reasoning = "Decision completed successfully"
                if extract_reasoning:
                    try:
                        reasoning = extract_reasoning(result)
                    except Exception:
                        pass
                
                # Extract dependencies
                dependencies = []
                if extract_dependencies:
                    try:
                        deps = extract_dependencies(args, kwargs)
                        if deps:
                            dependencies = deps
                    except Exception:
                        pass
                
                # Build context
                context = tracker.build_context()
                
                # Capture decision
                if claim_id:
                    service = audit_service or get_audit_service()
                    service.capture_decision(
                        claim_id=claim_id,
                        agent_component=agent_name,
                        decision_type=decision_type,
                        decision_value=result,
                        reasoning=reasoning,
                        context=context,
                        dependencies=dependencies,
                        success=True,
                    )
                
                return result
                
            except Exception as e:
                success = False
                error_message = str(e)
                
                # Capture failed decision
                if claim_id:
                    service = audit_service or get_audit_service()
                    service.capture_decision(
                        claim_id=claim_id,
                        agent_component=agent_name,
                        decision_type=decision_type,
                        decision_value=None,
                        reasoning=f"Decision failed: {error_message}",
                        context=tracker.build_context(),
                        success=False,
                        error_message=error_message,
                    )
                
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For synchronous functions, we can't easily capture async context
            # Just call the function
            return func(*args, **kwargs)
        
        # Return appropriate wrapper based on whether function is async
        if functools.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def with_decision_context(
    agent_name: str,
    audit_service: Optional[DecisionAuditService] = None,
):
    """
    Context manager for capturing decision context.
    
    Usage:
        with with_decision_context("IntakeAgent") as tracker:
            tracker.set_prompt(prompt)
            result = await agent.generate(prompt)
            tracker.set_llm_response(result)
    """
    class DecisionContextManager:
        def __init__(self, agent_name: str, audit_service: Optional[DecisionAuditService]):
            self.tracker = DecisionContextTracker()
            self.agent_name = agent_name
            self.audit_service = audit_service or get_audit_service()
        
        def __enter__(self):
            return self.tracker
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            # Context is captured, but decision is recorded elsewhere
            pass
    
    return DecisionContextManager(agent_name, audit_service)

