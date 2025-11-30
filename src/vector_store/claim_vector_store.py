"""
Claim Vector Store - Semantic search for claims using ChromaDB

Provides semantic search capabilities to find similar claims
based on embeddings.
"""

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    Settings = None
from typing import List, Optional
from uuid import UUID


class ClaimVectorStore:
    """
    Vector store for claim embeddings and semantic search.
    
    Uses ChromaDB for local vector storage and similarity search.
    """
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        """
        Initialize the claim vector store.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB not installed. Install with: pip install chromadb")
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="claims",
            metadata={"description": "Claim embeddings for semantic search"}
        )
    
    def add_claim(
        self,
        claim_id: str,
        claim_text: str,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Add a claim to the vector store.
        
        Args:
            claim_id: Unique claim identifier
            claim_text: Text content of the claim (for embedding)
            metadata: Optional metadata (status, amount, type, etc.)
        """
        # For now, we'll use the text directly
        # In production, you'd generate embeddings using a model
        # and store them: embeddings = embedding_model.embed(claim_text)
        
        metadata = metadata or {}
        metadata["claim_id"] = claim_id
        
        self.collection.add(
            ids=[claim_id],
            documents=[claim_text],
            metadatas=[metadata]
        )
    
    def search_similar(
        self,
        query_text: str,
        n_results: int = 5,
        filter_metadata: Optional[dict] = None
    ) -> List[dict]:
        """
        Search for similar claims.
        
        Args:
            query_text: Search query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
        
        Returns:
            List of similar claims with scores
        """
        where = filter_metadata if filter_metadata else None
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
        
        # Format results
        similar_claims = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i, claim_id in enumerate(results["ids"][0]):
                similar_claims.append({
                    "claim_id": claim_id,
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0,
                })
        
        return similar_claims
    
    def delete_claim(self, claim_id: str) -> None:
        """Delete a claim from the vector store"""
        self.collection.delete(ids=[claim_id])
    
    def get_all_claim_ids(self) -> List[str]:
        """Get all claim IDs in the vector store"""
        return self.collection.get()["ids"]

