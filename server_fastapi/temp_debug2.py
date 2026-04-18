from services.rag_pipeline import get_rag_pipeline
rag = get_rag_pipeline()
docs = rag.search_judgments('divorce cases', top_k=50)
print(f'Total docs: {len(docs)}')
easylaw = [d for d in docs if 'easylaw' in str(d.get('source_file', '')).lower()]
print(f'EasyLaw docs: {len(easylaw)}')
for d in easylaw[:5]:
  print(d.get('source_file'))