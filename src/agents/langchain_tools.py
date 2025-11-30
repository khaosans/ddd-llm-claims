"""
LangChain Tools for Agents

Provides LangChain tools that agents can use to interact with
the system (policy lookup, claim search, etc.).
"""

from typing import Optional
from langchain.tools import tool
from langchain_core.tools import ToolException

from ..repositories import PolicyRepository
from ..vector_store import ClaimVectorStore, PolicyVectorStore


@tool
def lookup_policy(policy_number: str, repository: PolicyRepository) -> str:
    """
    Lookup a policy by policy number.
    
    Args:
        policy_number: The policy number to lookup
        repository: Policy repository instance
    
    Returns:
        Policy information as JSON string
    """
    import asyncio
    import json
    
    try:
        policy = asyncio.run(repository.find_by_policy_number(policy_number))
        if policy:
            return json.dumps({
                "policy_id": str(policy.policy_id),
                "policy_number": policy.policy_number,
                "status": policy.status.value,
                "policy_type": policy.policy_type,
                "max_coverage_amount": str(policy.max_coverage_amount),
            }, default=str)
        return f"Policy {policy_number} not found"
    except Exception as e:
        raise ToolException(f"Error looking up policy: {e}")


@tool
def search_similar_claims(
    query: str,
    vector_store: ClaimVectorStore,
    n_results: int = 5
) -> str:
    """
    Search for similar claims using semantic search.
    
    Args:
        query: Search query text
        vector_store: Claim vector store instance
        n_results: Number of results to return
    
    Returns:
        JSON string with similar claims
    """
    import json
    
    try:
        results = vector_store.search_similar(query, n_results=n_results)
        return json.dumps(results, default=str)
    except Exception as e:
        raise ToolException(f"Error searching claims: {e}")


@tool
def find_matching_policies(
    claim_description: str,
    vector_store: PolicyVectorStore,
    n_results: int = 3
) -> str:
    """
    Find policies that match a claim description semantically.
    
    Args:
        claim_description: Description of the claim
        vector_store: Policy vector store instance
        n_results: Number of matching policies to return
    
    Returns:
        JSON string with matching policies
    """
    import json
    
    try:
        results = vector_store.find_matching_policies(claim_description, n_results=n_results)
        return json.dumps(results, default=str)
    except Exception as e:
        raise ToolException(f"Error finding matching policies: {e}")


def get_agent_tools(
    policy_repository: Optional[PolicyRepository] = None,
    claim_vector_store: Optional[ClaimVectorStore] = None,
    policy_vector_store: Optional[PolicyVectorStore] = None,
) -> list:
    """
    Get list of LangChain tools for agents.
    
    Args:
        policy_repository: Policy repository (for lookup_policy tool)
        claim_vector_store: Claim vector store (for search_similar_claims tool)
        policy_vector_store: Policy vector store (for find_matching_policies tool)
    
    Returns:
        List of LangChain tools
    """
    tools = []
    
    if policy_repository:
        # Create tool with repository bound
        def lookup_policy_bound(policy_number: str) -> str:
            return lookup_policy(policy_number, policy_repository)
        
        lookup_policy_bound.__name__ = "lookup_policy"
        lookup_policy_bound.__doc__ = lookup_policy.__doc__
        tools.append(lookup_policy_bound)
    
    if claim_vector_store:
        def search_claims_bound(query: str, n_results: int = 5) -> str:
            return search_similar_claims(query, claim_vector_store, n_results)
        
        search_claims_bound.__name__ = "search_similar_claims"
        search_claims_bound.__doc__ = search_similar_claims.__doc__
        tools.append(search_claims_bound)
    
    if policy_vector_store:
        def find_policies_bound(claim_description: str, n_results: int = 3) -> str:
            return find_matching_policies(claim_description, policy_vector_store, n_results)
        
        find_policies_bound.__name__ = "find_matching_policies"
        find_policies_bound.__doc__ = find_matching_policies.__doc__
        tools.append(find_policies_bound)
    
    return tools

