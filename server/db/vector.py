"""
Vector database for semantic search
For MVP: Uses in-memory numpy-based similarity search
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from config import get_settings


class InMemoryVectorDB:
    """
    In-memory vector database for MVP.
    Uses numpy for similarity calculations.
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectors: Dict[str, np.ndarray] = {}
        self.metadata: Dict[str, dict] = {}
        self._mock_embeddings = True  # Use random embeddings for MVP
    
    def _generate_mock_embedding(self, text: str) -> np.ndarray:
        """Generate a deterministic mock embedding based on text hash"""
        # Use hash for reproducibility
        seed = hash(text) % (2**32)
        rng = np.random.RandomState(seed)
        embedding = rng.randn(self.dimension)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    def add_document(self, doc_id: str, text: str, metadata: dict = None):
        """Add a document with its embedding"""
        embedding = self._generate_mock_embedding(text)
        self.vectors[doc_id] = embedding
        self.metadata[doc_id] = metadata or {}
    
    def add_documents_batch(self, documents: List[dict]):
        """Add multiple documents at once"""
        for doc in documents:
            self.add_document(
                doc["id"],
                doc.get("text", doc.get("full_text", "")),
                {"title": doc.get("title", ""), "citation": doc.get("citation", "")}
            )
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, dict]]:
        """
        Search for similar documents.
        Returns list of (doc_id, similarity_score, metadata)
        """
        if not self.vectors:
            return []
        
        query_embedding = self._generate_mock_embedding(query)
        
        # Calculate cosine similarities
        similarities = []
        for doc_id, doc_embedding in self.vectors.items():
            similarity = np.dot(query_embedding, doc_embedding)
            similarities.append((doc_id, float(similarity), self.metadata.get(doc_id, {})))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def get_document(self, doc_id: str) -> Optional[dict]:
        """Get a document's metadata"""
        return self.metadata.get(doc_id)
    
    def delete_document(self, doc_id: str):
        """Remove a document"""
        if doc_id in self.vectors:
            del self.vectors[doc_id]
            del self.metadata[doc_id]
    
    def count(self) -> int:
        """Get total document count"""
        return len(self.vectors)


# Global vector DB instance
_vector_db = InMemoryVectorDB()


def get_vector_db() -> InMemoryVectorDB:
    """Get vector database instance"""
    return _vector_db


def initialize_vector_db(db) -> InMemoryVectorDB:
    """Initialize vector DB from database cases"""
    vector_db = get_vector_db()
    cases = db.get_all_cases()
    vector_db.add_documents_batch(cases)
    return vector_db
