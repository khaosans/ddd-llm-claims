"""
Fraud Pattern Store - Vector store for fraud pattern detection

Stores fraud patterns and suspicious claim patterns for
semantic similarity matching.
"""

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    Settings = None
from typing import List, Optional


class FraudPatternStore:
    """
    Vector store for fraud patterns and suspicious claim patterns.
    
    Used to detect similar fraud patterns in new claims.
    """
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        """
        Initialize the fraud pattern store.
        
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
            name="fraud_patterns",
            metadata={"description": "Fraud pattern embeddings"}
        )
    
    def add_pattern(
        self,
        pattern_id: str,
        pattern_text: str,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Add a fraud pattern to the store.
        
        Args:
            pattern_id: Unique pattern identifier
            pattern_text: Description of the fraud pattern
            metadata: Optional metadata (risk_level, category, etc.)
        """
        metadata = metadata or {}
        metadata["pattern_id"] = pattern_id
        
        self.collection.add(
            ids=[pattern_id],
            documents=[pattern_text],
            metadatas=[metadata]
        )
    
    def detect_similar_patterns(
        self,
        claim_text: str,
        n_results: int = 5
    ) -> List[dict]:
        """
        Detect similar fraud patterns in a claim.
        
        Args:
            claim_text: Claim description/text
            n_results: Number of similar patterns to return
        
        Returns:
            List of similar fraud patterns with scores
        """
        results = self.collection.query(
            query_texts=[claim_text],
            n_results=n_results
        )
        
        similar_patterns = []
        if results["ids"] and len(results["ids"][0]) > 0:
            for i, pattern_id in enumerate(results["ids"][0]):
                similar_patterns.append({
                    "pattern_id": pattern_id,
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0,
                })
        
        return similar_patterns

