import asyncio
import os
import sys

# Setup environment before importing app code
os.environ["CEREBRAS_API_KEY"] = "mock_key_to_avoid_requests"

from services.vector_store import get_vector_store
from services.embeddings import get_embedding_service
from services.llm_service import get_llm_service

def test_rag_length():
    emb = get_embedding_service()
    vs = get_vector_store()
    llm = get_llm_service()
    
    query = "how can you help me"
    query_emb = emb.embed_query(query)
    
    # Bypass faiss error by just taking top 5 metadata docs manually
    docs = vs.metadata[:5]
    
    # Simulate generate_with_context length calculation
    context_parts = []
    for i, doc in enumerate(docs):
        category = doc.get('category', 'judgment')
        title = doc.get('title', 'Untitled')
        citation = doc.get('citation', '')
        court = doc.get('court', '')
        date = doc.get('date', '')
        parties = doc.get('parties', '')
        
        is_law = category.lower() in ['laws', 'legal provisions', 'statute', 'legislation']
        doc_type = "Legal Provision" if is_law else "Case Judgment"
        
        case_name = title
        if parties and (str(title).isdigit() or len(str(title)) < 10 or 'WP-No' in str(title)):
            case_name = f"{parties} [{title}]" if title != 'Untitled' else parties
        
        header = f"[{doc_type}] {case_name}"
        if citation and citation not in case_name:
            header += f" (Citation: {citation})"
        if court:
            header += f" | Court: {court}"
        if date:
            header += f" | Date: {date}"
        
        content = str(doc.get('content', ''))
        if len(content) > 1500:
            content = content[:1500] + "... [Content truncated for length]"
            
        context_parts.append(f"{header}\n\nContent:\n{content}")
        # Print lengths to diagnose
        print(f"Doc {i} - title_len: {len(str(title))}, parties_len: {len(str(parties))}, content_len: {len(content)}, header_len: {len(header)}")

    separator = "\n\n" + "=" * 80 + "\n\n"
    context_text = separator.join(context_parts)
    print("TOTAL CONTEXT LENGTH (CHARACTERS):", len(context_text))
    
    system_prompt = "You are LexiBot, an AI legal assistant specializing in Pakistani law for legal professionals..."
    
    prompt = f"Context from Legal Database:\n{context_text}\n\nUser Question: {query}\n\nCritical Instructions:..."
    print("TOTAL PROMPT LENGTH (CHARACTERS):", len(prompt))
    print("Prompt:", repr(prompt)[:100])

if __name__ == "__main__":
    test_rag_length()
