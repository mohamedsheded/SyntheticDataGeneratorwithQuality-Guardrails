"""Embedding utilities for semantic similarity"""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """Wrapper for sentence transformer model with caching"""
    
    _model: Optional[SentenceTransformer] = None
    _model_name: str = "all-MiniLM-L6-v2"
    
    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Get or initialize the embedding model"""
        if cls._model is None:
            cls._model = SentenceTransformer(cls._model_name)
        return cls._model
    
    @classmethod
    def encode(cls, texts: List[str]) -> np.ndarray:
        """
        Encode texts into embeddings.
        
        Args:
            texts: List of text strings
            
        Returns:
            numpy array of embeddings (n_texts, embedding_dim)
        """
        model = cls.get_model()
        return model.encode(texts, convert_to_numpy=True)
    
    @classmethod
    def cosine_similarity(cls, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))
    
    @classmethod
    def batch_similarity(
        cls, 
        query_embedding: np.ndarray, 
        candidate_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between query and multiple candidates.
        
        Args:
            query_embedding: Single embedding vector
            candidate_embeddings: Array of candidate embeddings (n_candidates, dim)
            
        Returns:
            Array of similarity scores
        """
        # Normalize query
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return np.zeros(len(candidate_embeddings))
        
        # Normalize candidates
        candidate_norms = np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
        candidate_norms = np.where(candidate_norms == 0, 1, candidate_norms)
        
        # Compute similarities
        similarities = np.dot(candidate_embeddings, query_embedding) / (
            candidate_norms.flatten() * query_norm
        )
        
        return similarities

