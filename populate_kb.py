#!/usr/bin/env python3
"""
Knowledge Base Population Script for RAG-based Language Learning Tutor

This script processes existing database content (WordOfDay and CommonPhrase entries)
into vector embeddings and builds a FAISS index for similarity search.

Usage:
    python populate_kb.py

The script will:
1. Read data from WordOfDay and CommonPhrase tables
2. Extract and format text content for embedding
3. Generate embeddings using sentence transformers
4. Create and populate FAISS index with cosine similarity
5. Save index and metadata to disk
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import faiss
import numpy as np
from tqdm import tqdm

# Import database models and vector service
from models import create_tables, get_db_session, WordOfDay, CommonPhrase
from vector_service import VectorService, INDEX_FILE, METADATA_FILE, DATA_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('populate_kb.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def extract_word_of_day_documents(db_session):
    """
    Extract documents from WordOfDay table.
    
    Args:
        db_session: Database session
        
    Returns:
        list: List of document dictionaries
    """
    documents = []
    
    try:
        logger.info("Extracting documents from WordOfDay table...")
        words = db_session.query(WordOfDay).all()
        logger.info(f"Found {len(words)} WordOfDay entries")
        
        for word in words:
            # Extract example sentences
            if word.example_sentence and word.example_sentence.strip():
                doc = {
                    "source": "Word of Day Example",
                    "language": word.language,
                    "text": f"An example of using '{word.word}' ({word.translation}) is: \"{word.example_sentence}\"",
                    "metadata": {
                        "word_id": word.id,
                        "word": word.word,
                        "translation": word.translation,
                        "part_of_speech": word.part_of_speech,
                        "difficulty": word.difficulty,
                        "example_translation": word.example_translation
                    }
                }
                documents.append(doc)
            
            # Extract cultural notes
            if word.cultural_note and word.cultural_note.strip():
                doc = {
                    "source": "Cultural Note",
                    "language": word.language,
                    "text": f"A cultural note about '{word.word}': {word.cultural_note}",
                    "metadata": {
                        "word_id": word.id,
                        "word": word.word,
                        "translation": word.translation,
                        "part_of_speech": word.part_of_speech,
                        "difficulty": word.difficulty
                    }
                }
                documents.append(doc)
            
            # Extract etymology information
            if word.etymology and word.etymology.strip():
                doc = {
                    "source": "Etymology",
                    "language": word.language,
                    "text": f"The etymology of '{word.word}': {word.etymology}",
                    "metadata": {
                        "word_id": word.id,
                        "word": word.word,
                        "translation": word.translation,
                        "part_of_speech": word.part_of_speech,
                        "difficulty": word.difficulty
                    }
                }
                documents.append(doc)
        
        logger.info(f"Extracted {len(documents)} documents from WordOfDay table")
        return documents
        
    except Exception as e:
        logger.error(f"Error extracting WordOfDay documents: {e}")
        return []

def extract_common_phrase_documents(db_session):
    """
    Extract documents from CommonPhrase table.
    
    Args:
        db_session: Database session
        
    Returns:
        list: List of document dictionaries
    """
    documents = []
    
    try:
        logger.info("Extracting documents from CommonPhrase table...")
        phrases = db_session.query(CommonPhrase).all()
        logger.info(f"Found {len(phrases)} CommonPhrase entries")
        
        for phrase in phrases:
            # Main phrase document
            doc = {
                "source": "Common Phrase",
                "language": phrase.language,
                "text": f"The common phrase '{phrase.phrase}' translates to '{phrase.translation}' and is often used for {phrase.category}.",
                "metadata": {
                    "phrase_id": phrase.id,
                    "phrase": phrase.phrase,
                    "translation": phrase.translation,
                    "category": phrase.category,
                    "difficulty": phrase.difficulty,
                    "pronunciation": phrase.pronunciation
                }
            }
            documents.append(doc)
            
            # Usage context document (if available)
            if phrase.usage_context and phrase.usage_context.strip():
                context_doc = {
                    "source": "Usage Context",
                    "language": phrase.language,
                    "text": f"Usage context for '{phrase.phrase}': {phrase.usage_context}",
                    "metadata": {
                        "phrase_id": phrase.id,
                        "phrase": phrase.phrase,
                        "translation": phrase.translation,
                        "category": phrase.category,
                        "difficulty": phrase.difficulty
                    }
                }
                documents.append(context_doc)
        
        logger.info(f"Extracted {len(documents)} documents from CommonPhrase table")
        return documents
        
    except Exception as e:
        logger.error(f"Error extracting CommonPhrase documents: {e}")
        return []

def generate_embeddings(documents, vector_service):
    """
    Generate embeddings for all documents.
    
    Args:
        documents (list): List of document dictionaries
        vector_service (VectorService): Vector service instance
        
    Returns:
        numpy.ndarray: Array of embeddings
    """
    try:
        logger.info(f"Generating embeddings for {len(documents)} documents...")
        
        # Extract text content
        texts = [doc['text'] for doc in documents]
        
        # Generate embeddings with progress bar
        logger.info("This may take a while depending on the number of documents...")
        embeddings = vector_service.model.encode(
            texts, 
            show_progress_bar=True,
            batch_size=32,  # Process in batches for memory efficiency
            convert_to_numpy=True
        )
        
        # Convert to float32 for FAISS
        embeddings = embeddings.astype('float32')
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise

def create_faiss_index(embeddings):
    """
    Create and populate FAISS index.
    
    Args:
        embeddings (numpy.ndarray): Array of embeddings
        
    Returns:
        faiss.Index: Populated FAISS index
    """
    try:
        logger.info("Creating FAISS index...")
        
        # Get embedding dimension
        dimension = embeddings.shape[1]
        logger.info(f"Embedding dimension: {dimension}")
        
        # Create index for inner product (cosine similarity with normalized vectors)
        index = faiss.IndexFlatIP(dimension)
        
        # Add embeddings to index
        logger.info("Adding embeddings to index...")
        index.add(embeddings)
        
        logger.info(f"Created FAISS index with {index.ntotal} vectors")
        return index
        
    except Exception as e:
        logger.error(f"Error creating FAISS index: {e}")
        raise

def save_index_and_metadata(index, documents):
    """
    Save FAISS index and metadata to disk.
    
    Args:
        index (faiss.Index): FAISS index
        documents (list): List of document dictionaries
    """
    try:
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        logger.info(f"Data directory: {DATA_DIR}")
        
        # Save FAISS index
        index_path = os.path.join(DATA_DIR, INDEX_FILE)
        logger.info(f"Saving FAISS index to: {index_path}")
        faiss.write_index(index, index_path)
        
        # Prepare metadata (remove numpy types for JSON serialization)
        metadata = []
        for doc in documents:
            clean_doc = {
                "source": doc["source"],
                "language": doc["language"],
                "text": doc["text"],
                "metadata": doc["metadata"]
            }
            metadata.append(clean_doc)
        
        # Save metadata
        metadata_path = os.path.join(DATA_DIR, METADATA_FILE)
        logger.info(f"Saving metadata to: {metadata_path}")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info("✅ Index and metadata saved successfully")
        
        # Log statistics
        logger.info(f"📊 Knowledge Base Statistics:")
        logger.info(f"   Total documents: {len(documents)}")
        logger.info(f"   Index size: {index.ntotal} vectors")
        logger.info(f"   Embedding dimension: {index.d}")
        
        # Language breakdown
        lang_counts = {}
        source_counts = {}
        for doc in documents:
            lang = doc["language"]
            source = doc["source"]
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
        
        logger.info(f"   Languages: {dict(sorted(lang_counts.items()))}")
        logger.info(f"   Sources: {dict(sorted(source_counts.items()))}")
        
    except Exception as e:
        logger.error(f"Error saving index and metadata: {e}")
        raise

def populate_knowledge_base():
    """
    Main function to populate the knowledge base.
    
    This function orchestrates the entire process:
    1. Initialize database and vector service
    2. Extract documents from database
    3. Generate embeddings
    4. Create FAISS index
    5. Save to disk
    """
    start_time = datetime.now()
    logger.info("🚀 Starting knowledge base population...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        create_tables()
        db_session = get_db_session()
        
        # Initialize vector service
        logger.info("Initializing vector service...")
        vector_service = VectorService()
        
        # Extract documents from database
        logger.info("📚 Extracting documents from database...")
        word_documents = extract_word_of_day_documents(db_session)
        phrase_documents = extract_common_phrase_documents(db_session)
        
        # Combine all documents
        all_documents = word_documents + phrase_documents
        
        if not all_documents:
            logger.warning("❌ No documents found in the database.")
            logger.warning("Please ensure the database contains WordOfDay and CommonPhrase entries.")
            logger.warning("You may need to run database migration or populate sample data first.")
            return False
        
        logger.info(f"📄 Total documents to process: {len(all_documents)}")
        
        # Generate embeddings
        logger.info("🧠 Generating embeddings...")
        embeddings = generate_embeddings(all_documents, vector_service)
        
        # Create FAISS index
        logger.info("🔍 Creating FAISS index...")
        index = create_faiss_index(embeddings)
        
        # Save to disk
        logger.info("💾 Saving index and metadata...")
        save_index_and_metadata(index, all_documents)
        
        # Close database session
        db_session.close()
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = end_time - start_time
        
        logger.info("🎉 Knowledge base population completed successfully!")
        logger.info(f"⏱️  Total processing time: {processing_time}")
        logger.info(f"📁 Files created:")
        logger.info(f"   - {os.path.join(DATA_DIR, INDEX_FILE)}")
        logger.info(f"   - {os.path.join(DATA_DIR, METADATA_FILE)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Knowledge base population failed: {e}")
        logger.exception("Full error traceback:")
        return False

def main():
    """Main entry point."""
    print("=" * 60)
    print("RAG Knowledge Base Population Script")
    print("=" * 60)
    
    success = populate_knowledge_base()
    
    if success:
        print("\n✅ Knowledge base population completed successfully!")
        print("The RAG system is now ready to provide enhanced explanations.")
        return 0
    else:
        print("\n❌ Knowledge base population failed!")
        print("Please check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())