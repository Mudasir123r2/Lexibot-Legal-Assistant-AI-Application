from services.rag_pipeline import get_rag_pipeline
rag = get_rag_pipeline()
docs = rag.search_judgments('divorce cases', top_k=10)
for i, d in enumerate(docs):
    print(f'Doc {i}:')
    print(f'  source_file: {d.get("source_file")}')
    print(f'  journal: {d.get("journal")}')
    print(f'  case_num: {d.get("case_number")}')
    print(f'  title: {d.get("title")}')
    print(f'  category: {d.get("category")}')