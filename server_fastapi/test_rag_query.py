import asyncio
from services.rag_pipeline import RAGPipeline

def run_test():
    rag = RAGPipeline()
    print("Running a difficult legal query to test retrieval logic...")
    query = "What is the limitation period for an appeal under section 25 of the Anti-Terrorism Act, and why would an appeal be dismissed if it's over 7 days?"
    
    # Run the query
    result = rag.query(query, top_k=3)
    
    print("\n" + "="*50)
    print("AI RESPONSE:")
    print("="*50)
    print(result.get("answer", "No answer generated."))
    
    print("\n" + "="*50)
    print("RETRIEVED CONTEXT (Ghost Chunking in Action):")
    print("="*50)
    context_chunks = result.get("context", [])
    for i, ctx in enumerate(context_chunks):
        title = ctx.get("title", 'Unknown Title')
        score = ctx.get('similarity', 0)
        excerpt = ctx.get("excerpt", "")
        # Highlight if we see the context markers
        has_expanded_context = "(Previous Context)" in excerpt or "(Next Context)" in excerpt
        
        print(f"CHUNK {i+1} | Title: {title} | Expanded Context: {has_expanded_context}")
        # Print first 200 chars and last 100 to show the appended context
        safe_preview = excerpt.replace('\n', ' ')
        if len(safe_preview) > 300:
            print(f"Preview: {safe_preview[:200]} ... {safe_preview[-100:]}")
        else:
            print(f"Preview: {safe_preview}")
        print("-" * 30)

if __name__ == "__main__":
    run_test()
