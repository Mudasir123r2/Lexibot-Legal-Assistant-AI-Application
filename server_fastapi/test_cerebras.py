"""
Quick test script to verify Cerebras API integration.
Tests both direct API calls and RAG pipeline.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from services.llm_service import get_llm_service
from services.embeddings import get_embedding_service
from services.vector_store import get_vector_store
from services.rag_pipeline import get_rag_pipeline
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_llm_service():
    """Test direct LLM API call."""
    logger.info("=" * 60)
    logger.info("TEST 1: Direct LLM Service (Cerebras API)")
    logger.info("=" * 60)
    
    try:
        llm = get_llm_service()
        
        query = "What is the legal definition of divorce in Pakistani law?"
        logger.info(f"Query: {query}")
        
        response = llm.generate_response(
            prompt=query,
            max_tokens=200,
            temperature=0.7
        )
        
        logger.info(f"✅ Response received ({len(response)} chars):")
        logger.info(f"{response[:500]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ LLM Service test failed: {str(e)}")
        return False


async def test_embeddings():
    """Test embedding generation."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Embedding Service")
    logger.info("=" * 60)
    
    try:
        embedding_service = get_embedding_service()
        
        text = "This is a test legal judgment about custody rights."
        logger.info(f"Text: {text}")
        
        embedding = embedding_service.embed_text(text)
        
        logger.info(f"✅ Embedding generated:")
        logger.info(f"  - Dimensions: {len(embedding)}")
        logger.info(f"  - First 5 values: {embedding[:5]}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Embedding test failed: {str(e)}")
        return False


async def test_vector_store():
    """Test vector store operations."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Vector Store")
    logger.info("=" * 60)
    
    try:
        vector_store = get_vector_store()
        stats = vector_store.get_stats()
        
        logger.info(f"✅ Vector Store Stats:")
        logger.info(f"  - Total documents: {stats['total_documents']}")
        logger.info(f"  - Index initialized: {stats['index_initialized']}")
        
        if stats['total_documents'] > 0:
            logger.info(f"  ✅ Vector store has indexed documents!")
        else:
            logger.warning(f"  ⚠️ No documents in vector store yet. Run ingestion first.")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Vector store test failed: {str(e)}")
        return False


async def test_rag_pipeline():
    """Test complete RAG pipeline."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: RAG Pipeline (End-to-End)")
    logger.info("=" * 60)
    
    try:
        rag = get_rag_pipeline()
        
        # Check if we have documents
        vector_store = get_vector_store()
        stats = vector_store.get_stats()
        
        if stats['total_documents'] == 0:
            logger.warning("⚠️ Skipping RAG test - no documents in vector store")
            logger.info("Run ingestion first: python scripts/ingest_judgments.py --source files --directory 'D:\\fyp\\lexibot-judgment\\Datacollectiom' --recursive")
            return True
        
        query = "What are the grounds for divorce in Pakistani law?"
        logger.info(f"Query: {query}")
        
        result = await rag.query(
            query=query,
            top_k=3,
            max_tokens=200
        )
        
        logger.info(f"✅ RAG Pipeline Results:")
        logger.info(f"  - Response length: {len(result['answer'])} chars")
        logger.info(f"  - Retrieved documents: {len(result['sources'])}")
        logger.info(f"\nAnswer preview:")
        logger.info(f"{result['answer'][:500]}...")
        
        if result['sources']:
            logger.info(f"\nTop source:")
            source = result['sources'][0]
            logger.info(f"  - Title: {source.get('title', 'N/A')}")
            logger.info(f"  - Category: {source.get('category', 'N/A')}")
            logger.info(f"  - Similarity: {source.get('similarity', 0):.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ RAG Pipeline test failed: {str(e)}")
        logger.error(f"Error details:", exc_info=True)
        return False


async def main():
    """Run all tests."""
    logger.info("\n" + "=" * 60)
    logger.info("CEREBRAS API + RAG INTEGRATION TEST SUITE")
    logger.info("=" * 60 + "\n")
    
    results = {
        "LLM Service": await test_llm_service(),
        "Embeddings": await test_embeddings(),
        "Vector Store": await test_vector_store(),
        "RAG Pipeline": await test_rag_pipeline()
    }
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    logger.info("\n" + "=" * 60)
    if all_passed:
        logger.info("🎉 ALL TESTS PASSED! System is ready.")
        logger.info("\nNext steps:")
        logger.info("1. If vector store is empty, run ingestion:")
        logger.info("   python scripts/ingest_judgments.py --source files --directory 'D:\\fyp\\lexibot-judgment\\Datacollectiom' --recursive --clear")
        logger.info("\n2. Start the server:")
        logger.info("   uvicorn app:app --reload --host 0.0.0.0 --port 8000")
        logger.info("\n3. Test via API:")
        logger.info("   curl -X POST http://localhost:8000/ai/chat -H 'Content-Type: application/json' -d '{\"message\":\"What are divorce grounds?\"}'")
    else:
        logger.error("❌ SOME TESTS FAILED. Check errors above.")
    logger.info("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
