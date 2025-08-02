# backend/vector_service.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import json
import logging
from rag_error_handler import (
    handle_vector_service_errors, 
    IndexLoadError, 
    SearchError, 
    log_error
)

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
MODEL_NAME = 'all-MiniLM-L6-v2'
INDEX_FILE = 'learning_kb.index'
METADATA_FILE = 'learning_kb_meta.json'
DATA_DIR = 'data'

class VectorService:
    """
    Service for managing vector embeddings and similarity search for the RAG system.
    
    This service handles:
    - Loading and initializing sentence transformer models
    - Loading FAISS vector indices from disk
    - Performing similarity searches on the knowledge base
    """
    
    def __init__(self):
        """Initialize the VectorService with sentence transformer model."""
        try:
            logger.info(f"Initializing VectorService with model: {MODEL_NAME}")
            self.model = SentenceTransformer(MODEL_NAME)
            self.index = None
            self.metadata = []
            logger.info("VectorService initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize VectorService: {e}")
            raise
    
    @handle_vector_service_errors
    def load_index(self):
        """
        Loads the FAISS index and metadata from disk.
        
        Returns:
            bool: True if index loaded successfully, False otherwise
        """
        try:
            index_path = os.path.join(DATA_DIR, INDEX_FILE)
            metadata_path = os.path.join(DATA_DIR, METADATA_FILE)
            
            # Store paths for error handling
            self._last_index_path = index_path
            self._last_metadata_path = metadata_path
            
            # Check if both files exist
            if not os.path.exists(index_path):
                logger.warning(f"Vector index file not found: {index_path}")
                return False
                
            if not os.path.exists(metadata_path):
                logger.warning(f"Metadata file not found: {metadata_path}")
                return False
            
            # Load FAISS index
            logger.info(f"Loading FAISS index from: {index_path}")
            self.index = faiss.read_index(index_path)
            
            # Load metadata
            logger.info(f"Loading metadata from: {metadata_path}")
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            # Validate that index and metadata are consistent
            if self.index.ntotal != len(self.metadata):
                logger.error(f"Index/metadata mismatch: index has {self.index.ntotal} vectors, metadata has {len(self.metadata)} entries")
                self.index = None
                self.metadata = []
                return False
            
            logger.info(f"✅ Vector index with {self.index.ntotal} entries loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load vector index: {e}")
            self.index = None
            self.metadata = []
            return False
    
    @handle_vector_service_errors
    def search(self, query_text: str, k: int = 5):
        """
        Searches the index for the most similar documents.
        
        Args:
            query_text (str): The text to search for
            k (int): Number of similar documents to return (default: 5)
            
        Returns:
            list: List of similar documents with metadata, empty list if no index loaded
        """
        try:
            # Check if index is loaded
            if self.index is None:
                logger.warning("No vector index loaded, attempting to load...")
                if not self.load_index():
                    logger.warning("Vector index not available, returning empty results")
                    return []
            
            # Validate input
            if not query_text or not query_text.strip():
                logger.warning("Empty query text provided")
                return []
            
            # Ensure k doesn't exceed available documents
            k = min(k, len(self.metadata))
            if k <= 0:
                logger.warning("No documents available for search")
                return []
            
            logger.debug(f"Searching for: '{query_text}' (k={k})")
            
            # Encode query text
            query_vector = self.model.encode([query_text.strip()]).astype('float32')
            
            # Normalize for cosine similarity
            faiss.normalize_L2(query_vector)
            
            # Perform search
            distances, indices = self.index.search(query_vector, k)
            
            # Build results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                # Skip invalid indices
                if idx < 0 or idx >= len(self.metadata):
                    logger.warning(f"Invalid index returned by FAISS: {idx}")
                    continue
                
                # Get document metadata
                doc = self.metadata[idx].copy()
                doc['similarity_score'] = float(distance)  # Inner product score
                doc['rank'] = i + 1
                results.append(doc)
            
            logger.debug(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Error during vector search: {e}")
            return []
    
    def is_ready(self):
        """
        Check if the vector service is ready for searches.
        
        Returns:
            bool: True if index is loaded and ready, False otherwise
        """
        return self.index is not None and len(self.metadata) > 0
    
    def get_stats(self):
        """
        Get statistics about the loaded index.
        
        Returns:
            dict: Statistics about the vector service
        """
        stats = {
            'model_name': MODEL_NAME,
            'index_loaded': self.index is not None,
            'total_documents': len(self.metadata),
            'index_size': self.index.ntotal if self.index else 0,
            'embedding_dimension': 384,  # all-MiniLM-L6-v2 dimension
        }
        
        if self.index:
            stats['index_type'] = type(self.index).__name__
        
        return stats

# Singleton instance for application-wide usage
vector_service = VectorService()