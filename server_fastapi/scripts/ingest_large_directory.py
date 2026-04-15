import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List

# Add parent directory to path to import services and utils
sys.path.append(str(Path(__file__).parent.parent))

from services.embeddings import get_embedding_service
from services.vector_store import get_vector_store
from utils.document_processor import get_document_processor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ingest_large_directory(directory: str, save_interval: int = 50):
    """
    Safely ingest a large directory of documents with resume capabilities.
    """
    try:
        doc_dir = Path(directory)
        if not doc_dir.exists():
            logger.error(f"Directory not found: {directory}")
            return
            
        logger.info(f"Scanning directory: {directory} for PDF, DOCX, and TXT files...")
        
        # Only grab specific file types (this ignores your json file automatically)
        files = list(doc_dir.rglob("*.pdf")) + \
                list(doc_dir.rglob("*.docx")) + \
                list(doc_dir.rglob("*.txt"))
                
        if not files:
            logger.warning("No valid documents found.")
            return
            
        logger.info(f"Target file count: {len(files)}")

        # Initialize Services
        logger.info("Initializing vector store and embedding service...")
        vector_store = get_vector_store()
        embedding_service = get_embedding_service()
        doc_processor = get_document_processor()
        
        # Figure out which files we've already processed to support resuming!
        processed_files = set()
        for meta in vector_store.metadata:
            source_file = meta.get("source_file")
            if source_file:
                processed_files.add(source_file)
                
        logger.info(f"Found {len(processed_files)} files already registered in the FAISS index.")
        
        # Filter files
        files_to_process = [f for f in files if f.name not in processed_files]
        
        if not files_to_process:
            logger.info("🎉 All files in the directory have already been ingested! Nothing to do.")
            return
            
        logger.info(f"Remaining files to process: {len(files_to_process)}")
        
        current_batch_texts = []
        current_batch_metadata = []
        files_processed_since_save = 0
        total_successfully_processed = 0

        for i, file_path in enumerate(files_to_process):
            try:
                # Extract category from folder structure
                category = "General"
                if file_path.parent != doc_dir:
                    category = file_path.parent.name
                    
                logger.info(f"[{i+1}/{len(files_to_process)}] Processing: {file_path.name} | Category: {category}")
                
                # Base Metadata
                metadata = {
                    "source_file": file_path.name,
                    "title": file_path.stem,
                    "category": category,
                    "source_type": "directory_ingestion"
                }

                # Use the document processor (handles OCR, Chunking)
                chunks = doc_processor.process_judgment_document(
                    file_path=str(file_path),
                    metadata=metadata
                )
                
                if not chunks:
                    logger.warning(f"No text extracted from {file_path.name}")
                    continue

                for chunk in chunks:
                    current_batch_texts.append(chunk["content"])
                    current_batch_metadata.append(chunk)

                files_processed_since_save += 1
                total_successfully_processed += 1
                
                # SAVE INTERVAL Logic: If we hit our threshold, vectorize and save!
                if files_processed_since_save >= save_interval:
                    logger.info("=========================================================")
                    logger.info(f"Threshold reached! Embedding & Saving batch of {len(current_batch_texts)} chunks...")
                    
                    if current_batch_texts:
                        # Generate Embeddings
                        embeddings = embedding_service.embed_texts(current_batch_texts, batch_size=32)
                        
                        # Add to Store
                        vector_store.add_documents(embeddings, current_batch_metadata)
                        
                        # Physically save to disk
                        vector_store.save_index()
                        logger.info(f"✅ SAVE COMPLETE. Progress secured. Total Index Size: {vector_store.get_document_count()}")
                    
                    # Reset batch accumulators
                    current_batch_texts = []
                    current_batch_metadata = []
                    files_processed_since_save = 0
                    logger.info("=========================================================")

            except Exception as e:
                logger.error(f"❌ Error processing {file_path.name}: {str(e)}")
                # Continue gracefully to the next file
                continue

        # Final cleanup save for the remaining files in the queue
        if current_batch_texts:
            logger.info("Processing final remaining documents...")
            embeddings = embedding_service.embed_texts(current_batch_texts, batch_size=32)
            vector_store.add_documents(embeddings, current_batch_metadata)
            vector_store.save_index()
            
        logger.info(f"🎉 Fully completed directory ingestion. Processed {total_successfully_processed} files.")

    except Exception as e:
        logger.error(f"Critical Ingestion Error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely ingest large legal datasets with automatic checkpoint saving.")
    parser.add_argument(
        "--directory", 
        default="new datasets",
        help="Path to the large dataset directory"
    )
    parser.add_argument(
        "--save-interval", 
        type=int, 
        default=50,
        help="How many files to process before permanently saving the FAISS index to disk (default: 50)"
    )
    
    args = parser.parse_args()
    
    ingest_large_directory(args.directory, save_interval=args.save_interval)
