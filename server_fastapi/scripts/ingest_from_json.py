import json
import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path to import services and utils
sys.path.append(str(Path(__file__).parent.parent))

from services.embeddings import get_embedding_service
from services.vector_store import get_vector_store
from utils.document_processor import get_document_processor
from config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def categorize_document(file_name: str, text: str) -> str:
    """Categorize document based on filename and content."""
    text_lower = text[:1000].lower()
    fn_lower = file_name.lower()
    
    # Check for Judgments
    judgment_keywords = ['judgment', 'petitioner', 'respondent', 'appellant', 'versus', ' v. ', 'court held', 'honourable']
    if any(kw in text_lower or kw in fn_lower for kw in judgment_keywords):
        return "Judgment"
    
    # Check for Statutes
    statute_keywords = ['ordinance', 'act', 'rules', 'regulation', 'section', 'article', 'amendment', 'gazette']
    if any(kw in text_lower or kw in fn_lower for kw in statute_keywords):
        return "Statute"
    
    return "Legal Document"

def ingest_from_json(json_path: str, limit: int = None, clear: bool = False):
    """
    Ingest all records from a JSON file into the FAISS vector store.
    """
    try:
        json_file = Path(json_path)
        if not json_file.exists():
            logger.error(f"JSON file not found: {json_path}")
            return

        # Load JSON data
        logger.info(f"Loading data from {json_path}...")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            logger.error("JSON data must be a list of records")
            return

        if limit:
            data = data[:limit]
            logger.info(f"Limiting to first {limit} records as requested.")

        logger.info(f"Found {len(data)} records to process.")

        # Get services
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()
        doc_processor = get_document_processor()

        if clear:
            logger.info("Clearing existing vector store...")
            vector_store.clear()

        all_texts = []
        all_metadata = []

        # Process each record
        for i, record in enumerate(data):
            file_name = record.get('file_name', f'record_{i}')
            text_content = record.get('text', '')

            if not text_content:
                logger.warning(f"Skipping record {i} ({file_name}): No content")
                continue

            logger.info(f"Processing [{i+1}/{len(data)}]: {file_name[:50]}...")

            # Categorize the document
            category = categorize_document(file_name, text_content)
            
            # Additional metadata
            base_metadata = {
                "source_file": file_name,
                "category": category,
                "source_type": "json_ingestion",
                "original_json": json_path
            }

            # Process document into chunks
            chunks = doc_processor.process_judgment_document(
                text=text_content,
                metadata=base_metadata
            )

            for chunk in chunks:
                all_texts.append(chunk["content"])
                all_metadata.append(chunk)

        if not all_texts:
            logger.error("No valid text chunks extracted from JSON.")
            return

        logger.info(f"Total chunks created: {len(all_texts)}")

        # Split into batches for embedding to avoid memory issues (though sentence-transformers handles it)
        batch_size = 128
        total_batches = (len(all_texts) + batch_size - 1) // batch_size
        
        logger.info(f"Generating embeddings in {total_batches} batches...")
        
        for b in range(total_batches):
            start_idx = b * batch_size
            end_idx = min((b + 1) * batch_size, len(all_texts))
            
            batch_texts = all_texts[start_idx:end_idx]
            batch_meta = all_metadata[start_idx:end_idx]
            
            logger.info(f"  Batch {b+1}/{total_batches} ({len(batch_texts)} chunks)...")
            batch_embeddings = embedding_service.embed_texts(batch_texts, batch_size=32)
            
            # Add to vector store
            vector_store.add_documents(batch_embeddings, batch_meta)

        # Save the index
        logger.info("Saving FAISS index to disk...")
        vector_store.save_index()

        logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║           ✅ JSON INGESTION COMPLETED                    ║
╠══════════════════════════════════════════════════════════╣
║  Records processed:    {len(data):>5}                         ║
║  Text chunks created:  {len(all_texts):>5}                         ║
║  Index size:           {vector_store.get_document_count():>5}                         ║
╚══════════════════════════════════════════════════════════╝
""")

    except Exception as e:
        logger.error(f"❌ Ingestion failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest legal data from JSON into RAG vector store")
    parser.add_argument(
        "--file", 
        default="new datasets/pdf_data.json",
        help="Path to the JSON file (relative to server_fastapi)"
    )
    parser.add_argument(
        "--limit", 
        type=int, 
        help="Limit the number of records to process (for testing)"
    )
    parser.add_argument(
        "--clear", 
        action="store_true", 
        help="Clear existing index before ingestion"
    )
    
    args = parser.parse_args()
    
    # Execute ingestion
    ingest_from_json(args.file, limit=args.limit, clear=args.clear)
