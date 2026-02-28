"""
Vector Store Service
Manages FAISS index for efficient similarity search of legal documents.
Stores and retrieves document embeddings with metadata.
"""

import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector store for semantic search of legal judgments.
    
    Features:
    - Fast similarity search using FAISS IndexFlatL2
    - Metadata storage for retrieved documents
    - Persistent storage (save/load index)
    """
    
    def __init__(self, dimension: int = 384, index_path: str = "data/faiss_index"):
        """
        Initialize vector store.
        
        Args:
            dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
            index_path: Directory to save/load index files
        """
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        # FAISS index - using IndexFlatL2 for exact L2 distance search
        self.index = faiss.IndexFlatL2(dimension)
        
        # Metadata storage: list of dicts containing document info
        self.metadata: List[Dict[str, Any]] = []
        
        # Try to load existing index
        self._load_index()
    
    def add_documents(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict[str, Any]]
    ) -> None:
        """
        Add document embeddings to the index.
        
        Args:
            embeddings: numpy array of shape (num_docs, dimension)
            metadata: List of metadata dicts (one per document)
        """
        try:
            if len(embeddings) != len(metadata):
                raise ValueError("Number of embeddings must match metadata count")
            
            # Ensure embeddings are float32 (required by FAISS)
            embeddings = embeddings.astype('float32')
            
            # Add to FAISS index
            self.index.add(embeddings)
            
            # Store metadata
            self.metadata.extend(metadata)
            
            logger.info(f"✅ Added {len(embeddings)} documents to index. Total: {self.index.ntotal}")
            
        except Exception as e:
            logger.error(f"Error adding documents to index: {str(e)}")
            raise
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query vector of shape (dimension,)
            k: Number of results to return
            
        Returns:
            List of dicts containing document metadata and similarity scores
        """
        try:
            if self.index.ntotal == 0:
                logger.warning("Vector store is empty")
                return []
            
            # Reshape query to (1, dimension) and ensure float32
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            # Search
            distances, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
            
            # Prepare results
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx != -1 and idx < len(self.metadata):  # Valid index
                    result = self.metadata[idx].copy()
                    result['score'] = float(distance)
                    result['similarity'] = float(1 / (1 + distance))  # Convert distance to similarity
                    results.append(result)
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error searching index: {str(e)}")
            raise
    
    def get_document_count(self) -> int:
        """Get total number of documents in the index."""
        return self.index.ntotal
    
    def clear(self) -> None:
        """Clear all documents from the index."""
        self.index.reset()
        self.metadata = []
        logger.info("✅ Vector store cleared")
    
    def save_index(self) -> None:
        """Save FAISS index and metadata to disk."""
        try:
            # Save FAISS index
            index_file = self.index_path / "faiss.index"
            faiss.write_index(self.index, str(index_file))
            
            # Save metadata
            metadata_file = self.index_path / "metadata.pkl"
            with open(metadata_file, 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"✅ Saved index with {self.index.ntotal} documents to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
            raise
    
    def _load_index(self) -> None:
        """Load FAISS index and metadata from disk if exists."""
        try:
            index_file = self.index_path / "faiss.index"
            metadata_file = self.index_path / "metadata.pkl"
            
            if index_file.exists() and metadata_file.exists():
                # Load FAISS index
                self.index = faiss.read_index(str(index_file))
                
                # Load metadata
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                
                logger.info(f"✅ Loaded existing index with {self.index.ntotal} documents")
            else:
                logger.info("No existing index found. Starting fresh.")
                
        except Exception as e:
            logger.warning(f"Could not load existing index: {str(e)}. Starting fresh.")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_documents": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": "IndexFlatL2",
            "metadata_count": len(self.metadata),
            "index_initialized": self.index is not None
        }


# Singleton instance
_vector_store = None

def get_vector_store(dimension: int = 384) -> VectorStore:
    """
    Get or create singleton vector store instance.
    
    Args:
        dimension: Embedding dimension
        
    Returns:
        VectorStore instance
    """
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(dimension=dimension)
    return _vector_store
