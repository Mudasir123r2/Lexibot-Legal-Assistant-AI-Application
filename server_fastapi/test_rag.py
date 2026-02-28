"""
Test RAG Pipeline
Quick test to verify all services are working.

Run this after:
1. Starting the server (python main.py)
2. Ingesting judgments (python scripts/ingest_judgments.py)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

def test_services():
    """Test all AI services individually."""
    print("=" * 60)
    print("TESTING RAG PIPELINE COMPONENTS")
    print("=" * 60)
    
    # Test 1: Embedding Service
    print("\n1️⃣  Testing Embedding Service...")
    try:
        from services.embeddings import get_embedding_service
        
        embedding_service = get_embedding_service()
        test_text = "This is a test legal document about divorce"
        
        embedding = embedding_service.embed_text(test_text)
        dim = embedding_service.get_dimension()
        
        print(f"   ✅ Embedding service loaded")
        print(f"   ✅ Embedding dimension: {dim}")
        print(f"   ✅ Test embedding shape: {embedding.shape}")
        
    except Exception as e:
        print(f"   ❌ Embedding service failed: {e}")
        return False
    
    # Test 2: Vector Store
    print("\n2️⃣  Testing Vector Store...")
    try:
        from services.vector_store import get_vector_store
        
        vector_store = get_vector_store()
        stats = vector_store.get_stats()
        
        print(f"   ✅ Vector store loaded")
        print(f"   ✅ Total documents: {stats['total_documents']}")
        print(f"   ✅ Index type: {stats['index_type']}")
        
        if stats['total_documents'] == 0:
            print("   ⚠️  WARNING: No documents indexed!")
            print("   💡 Run: python scripts/ingest_judgments.py")
        
    except Exception as e:
        print(f"   ❌ Vector store failed: {e}")
        return False
    
    # Test 3: LLM Service
    print("\n3️⃣  Testing LLM Service...")
    try:
        from services.llm_service import get_llm_service
        
        llm_service = get_llm_service()
        
        if llm_service.client:
            print(f"   ✅ LLM service initialized")
            print(f"   ✅ Model: {llm_service.model}")
            
            # Try a simple generation
            response = llm_service.generate_response(
                "Say 'Hello from LexiBot' in one sentence.",
                max_tokens=50
            )
            print(f"   ✅ Test generation: {response[:50]}...")
        else:
            print(f"   ⚠️  LLM service in fallback mode")
            print(f"   💡 Add GROQ_API_KEY to .env file")
        
    except Exception as e:
        print(f"   ❌ LLM service failed: {e}")
        return False
    
    # Test 4: RAG Pipeline
    print("\n4️⃣  Testing RAG Pipeline...")
    try:
        from services.rag_pipeline import get_rag_pipeline
        
        rag = get_rag_pipeline()
        pipeline_stats = rag.get_stats()
        
        print(f"   ✅ RAG pipeline initialized")
        print(f"   ✅ Pipeline stats:")
        for key, value in pipeline_stats.items():
            print(f"      - {key}: {value}")
        
    except Exception as e:
        print(f"   ❌ RAG pipeline failed: {e}")
        return False
    
    return True


def test_search():
    """Test semantic search."""
    print("\n" + "=" * 60)
    print("TESTING SEMANTIC SEARCH")
    print("=" * 60)
    
    try:
        from services.rag_pipeline import get_rag_pipeline
        
        rag = get_rag_pipeline()
        
        test_query = "divorce grounds Pakistan"
        print(f"\n🔍 Query: '{test_query}'")
        
        results = rag.search_judgments(test_query, top_k=3)
        
        if results:
            print(f"\n✅ Found {len(results)} results:")
            for i, result in enumerate(results):
                print(f"\n   [{i+1}] {result.get('title', 'Untitled')}")
                print(f"       Similarity: {result.get('similarity', 0):.3f}")
                print(f"       Case Type: {result.get('case_type', 'N/A')}")
                print(f"       Excerpt: {result.get('excerpt', '')[:100]}...")
        else:
            print("   ⚠️  No results found")
            print("   💡 Make sure judgments are ingested")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Search failed: {e}")
        return False


def test_rag_query():
    """Test complete RAG query."""
    print("\n" + "=" * 60)
    print("TESTING RAG QUERY (Retrieval + Generation)")
    print("=" * 60)
    
    try:
        from services.rag_pipeline import get_rag_pipeline
        
        rag = get_rag_pipeline()
        
        test_question = "What are the legal grounds for divorce in Pakistan?"
        print(f"\n❓ Question: '{test_question}'")
        
        result = rag.query(test_question, top_k=3, include_sources=True)
        
        print(f"\n📝 Answer:")
        print(f"   {result['answer']}")
        print(f"\n📊 Confidence: {result['confidence']:.3f}")
        print(f"📚 Sources used: {len(result.get('sources', []))}")
        
        if result.get('sources'):
            print(f"\n📖 Source Documents:")
            for i, source in enumerate(result['sources'][:3]):
                print(f"   [{i+1}] {source.get('title', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ RAG query failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🧪 LexiBot RAG Pipeline Test Suite\n")
    
    # Test services
    if not test_services():
        print("\n❌ Service tests failed. Fix errors and try again.")
        return
    
    print("\n✅ All services initialized successfully!")
    
    # Test search
    if not test_search():
        print("\n⚠️  Search test failed or no data indexed.")
        print("💡 Run: python scripts/ingest_judgments.py --source database")
        return
    
    print("\n✅ Search test passed!")
    
    # Test RAG query
    if not test_rag_query():
        print("\n⚠️  RAG query test failed.")
        print("💡 Check if GROQ_API_KEY is set in .env")
        return
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print("\n✅ Your RAG pipeline is fully operational!")
    print("💡 Next: Start server and test via http://localhost:5000/docs")
    print()


if __name__ == "__main__":
    main()
