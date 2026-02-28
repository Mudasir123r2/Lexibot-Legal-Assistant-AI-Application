"""
Embedding Service
Generates vector embeddings for text using sentence-transformers.
Uses 'all-MiniLM-L6-v2' model for efficient and accurate embeddings.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using sentence-transformers.
    
    The model 'all-MiniLM-L6-v2' produces 384-dimensional embeddings and is:
    - Fast (can process 1000s of sentences quickly)
    - Accurate for semantic similarity tasks
    - Lightweight (only 80MB)
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding service.
        
        Args:
            model_name: HuggingFace model name (default: all-MiniLM-L6-v2)
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"✅ Embedding model loaded successfully. Dimension: {self.get_dimension()}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def get_dimension(self) -> int:
        """
        Get the dimension of the embeddings.
        
        Returns:
            int: Embedding dimension (384 for all-MiniLM-L6-v2)
        """
        return self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            numpy array of shape (embedding_dim,)
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for multiple texts in batches.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
            
        Returns:
            numpy array of shape (num_texts, embedding_dim)
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts...")
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {str(e)}")
            raise
    
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query.
        Same as embed_text but named for clarity in RAG pipeline.
        
        Args:
            query: Search query text
            
        Returns:
            numpy array of shape (embedding_dim,)
        """
        return self.embed_text(query)


# Singleton instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """
    Get or create singleton embedding service instance.
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
