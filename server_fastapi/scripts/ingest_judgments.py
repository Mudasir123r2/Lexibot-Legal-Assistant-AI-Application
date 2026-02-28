"""
Judgment Ingestion Script
Processes legal judgments from MongoDB and creates FAISS vector index.

Usage:
    python scripts/ingest_judgments.py

This script:
1. Connects to MongoDB
2. Fetches all judgments
3. Processes and chunks the text
4. Generates embeddings
5. Stores in FAISS index
6. Saves index to disk
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from services.embeddings import get_embedding_service
from services.vector_store import get_vector_store
from utils.document_processor import get_document_processor
from config.settings import get_settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


async def ingest_judgments_from_db():
    """
    Ingest judgments from MongoDB into FAISS vector store.
    """
    client = None
    
    try:
        # Connect to MongoDB
        logger.info("Connecting to MongoDB...")
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client.get_database()
        
        # Test connection
        await client.admin.command('ping')
        logger.info("✅ Connected to MongoDB")
        
        # Get services
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()
        doc_processor = get_document_processor()
        
        # Fetch all judgments from database
        logger.info("Fetching judgments from database...")
        judgments_cursor = db.judgments.find({})
        judgments = await judgments_cursor.to_list(length=None)
        
        if not judgments:
            logger.warning("⚠️  No judgments found in database")
            logger.info("💡 Add judgments using: python scripts/seed_judgments.py")
            return
        
        logger.info(f"Found {len(judgments)} judgments to process")
        
        # Process each judgment
        all_texts = []
        all_metadata = []
        
        for i, judgment in enumerate(judgments):
            try:
                judgment_id = str(judgment.get("_id", ""))
                title = judgment.get("title", "Untitled")
                content = judgment.get("content") or judgment.get("summary", "")
                
                if not content:
                    logger.warning(f"Skipping judgment {judgment_id}: No content")
                    continue
                
                logger.info(f"Processing [{i+1}/{len(judgments)}]: {title}")
                
                # Process document into chunks
                chunks = doc_processor.process_judgment_document(
                    text=content,
                    metadata={
                        "_id": judgment_id,
                        "title": title,
                        "case_type": judgment.get("caseType", "Unknown"),
                        "court": judgment.get("court", "Unknown"),
                        "date": judgment.get("date", "Unknown"),
                        "parties": judgment.get("parties", ""),
                        "outcome": judgment.get("outcome", "Unknown"),
                        "citation": judgment.get("citation", "")
                    }
                )
                
                # Add each chunk
                for chunk in chunks:
                    all_texts.append(chunk["content"])
                    all_metadata.append(chunk)
                
            except Exception as e:
                logger.error(f"Error processing judgment {i+1}: {str(e)}")
                continue
        
        if not all_texts:
            logger.error("❌ No valid judgment text extracted")
            return
        
        logger.info(f"Processed {len(all_texts)} text chunks from {len(judgments)} judgments")
        
        # Generate embeddings
        logger.info("Generating embeddings... (this may take a few minutes)")
        embeddings = embedding_service.embed_texts(all_texts, batch_size=32)
        
        # Add to vector store
        logger.info("Adding documents to vector store...")
        vector_store.add_documents(embeddings, all_metadata)
        
        # Save index to disk
        logger.info("Saving index to disk...")
        vector_store.save_index()
        
        logger.info(f"""
╔══════════════════════════════════════════════════════════╗
║           ✅ INGESTION COMPLETED SUCCESSFULLY            ║
╠══════════════════════════════════════════════════════════╣
║  Judgments processed:  {len(judgments):>5}                         ║
║  Text chunks created:  {len(all_texts):>5}                         ║
║  Embeddings generated: {len(embeddings):>5}                         ║
║  Index saved to:       data/faiss_index/                ║
╚══════════════════════════════════════════════════════════╝
""")
        
        # Display some stats
        stats = vector_store.get_stats()
        logger.info(f"Vector Store Stats: {stats}")
        
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {str(e)}", exc_info=True)
        
    finally:
        if client:
            client.close()
            logger.info("MongoDB connection closed")


async def ingest_from_files(directory: str = "data/raw_documents", recursive: bool = False):
    """
    Ingest judgments from files (PDF, DOCX, TXT) in a directory.
    
    Args:
        directory: Path to directory containing judgment files
        recursive: If True, recursively process subdirectories (useful for categorized folders)
    """
    try:
        doc_dir = Path(directory)
        
        if not doc_dir.exists():
            logger.error(f"Directory not found: {directory}")
            logger.info(f"Create it with: mkdir -p {directory}")
            return
        
        # Get all files (recursively if requested)
        if recursive:
            files = list(doc_dir.rglob("*.pdf")) + \
                    list(doc_dir.rglob("*.docx")) + \
                    list(doc_dir.rglob("*.txt"))
        else:
            files = list(doc_dir.glob("*.pdf")) + \
                    list(doc_dir.glob("*.docx")) + \
                    list(doc_dir.glob("*.txt"))
        
        if not files:
            logger.warning(f"No documents found in {directory}")
            logger.info("Add PDF, DOCX, or TXT files to this directory")
            return
        
        logger.info(f"Found {len(files)} files to process")
        
        # Get services
        embedding_service = get_embedding_service()
        vector_store = get_vector_store()
        doc_processor = get_document_processor()
        
        all_texts = []
        all_metadata = []
        
        for i, file_path in enumerate(files):
            try:
                logger.info(f"Processing [{i+1}/{len(files)}]: {file_path.name}")
                
                # Extract category from folder structure (if subdirectory)
                category = None
                if file_path.parent != doc_dir:
                    # Get immediate parent folder name as category
                    category = file_path.parent.name
                
                # Process document
                metadata = {
                    "source_file": file_path.name,
                    "title": file_path.stem
                }
                
                # Add category if found
                if category:
                    metadata["category"] = category
                    logger.info(f"  Category: {category}")
                
                chunks = doc_processor.process_judgment_document(
                    file_path=str(file_path),
                    metadata=metadata
                )
                
                for chunk in chunks:
                    all_texts.append(chunk["content"])
                    all_metadata.append(chunk)
                
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {str(e)}")
                continue
        
        if not all_texts:
            logger.error("No valid text extracted from files")
            return
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(all_texts)} chunks...")
        embeddings = embedding_service.embed_texts(all_texts, batch_size=32)
        
        # Add to vector store
        vector_store.add_documents(embeddings, all_metadata)
        
        # Save index
        vector_store.save_index()
        
        logger.info(f"✅ Ingestion complete! Processed {len(files)} files into {len(all_texts)} chunks")
        
    except Exception as e:
        logger.error(f"File ingestion failed: {str(e)}", exc_info=True)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest legal judgments into FAISS vector store")
    parser.add_argument(
        "--source",
        choices=["database", "files"],
        default="database",
        help="Source of judgments (default: database)"
    )
    parser.add_argument(
        "--directory",
        default="data/raw_documents",
        help="Directory for file ingestion (default: data/raw_documents)"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively process subdirectories (useful for categorized folders)"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing index before ingestion"
    )
    
    args = parser.parse_args()
    
    # Clear index if requested
    if args.clear:
        logger.info("Clearing existing vector store...")
        vector_store = get_vector_store()
        vector_store.clear()
        logger.info("✅ Vector store cleared")
    
    # Run ingestion
    if args.source == "database":
        asyncio.run(ingest_judgments_from_db())
    else:
        asyncio.run(ingest_from_files(args.directory, recursive=args.recursive))


if __name__ == "__main__":
    main()
