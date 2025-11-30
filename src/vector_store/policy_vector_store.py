"""
Policy Vector Store - Semantic search for policies using ChromaDB

Provides semantic search to match claims to policies based on
policy document content.
"""

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    Settings = None
from typing import List, Optional


class PolicyVectorStore:
    """
    Vector store for policy document embeddings.
    
    Stores policy documents for semantic matching with claims.
    """
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        """
        Initialize the policy vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB not installed. Install with: pip install chromadb")
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        self.collection = self.client.get_or_create_collection(
            name="policies",
            metadata={"description": "Policy document embeddings"}
        )
    
    def add_policy(
        self,
        policy_id: str,
        policy_text: str,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Add a policy to the vector store.
        
        Args:
            policy_id: Unique policy identifier
            policy_text: Policy document text
            metadata: Optional metadata (policy_number, type, etc.)
        """
        metadata = metadata or {}
        metadata["policy_id"] = policy_id
        
        self.collection.add(
            ids=[policy_id],
            documents=[policy_text],
            metadatas=[metadata]
        )
    
    def find_matching_policies(
        self,
        claim_text: str,
        n_results: int = 3
    ) -> List[dict]:
        """
        Find policies that match a claim semantically.
        
        Args:
            claim_text: Claim description/text
            n_results: Number of matching policies to return
        
        Returns:
            List of matching policies with scores
        """
        results = self.collection.query(
            query_texts=[claim_text],
            n_results=n_results
        )
        
        matching_policies = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i, policy_id in enumerate(results["ids"][0]):
                matching_policies.append({
                    "policy_id": policy_id,
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0,
                })
        
        return matching_policies

