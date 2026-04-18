from services.rag_pipeline import get_rag_pipeline
rag = get_rag_pipeline()
docs = rag.search_judgments('divorce cases', top_k=19)
filtered = []
for doc in docs:
    src = str(doc.get('source_file') or '')
    cat = str(doc.get('category') or doc.get('case_type') or doc.get('caseType') or '')
    title = str(doc.get('title') or '')
    if 'easylaw' not in src.lower():
        print(f'SKIP (no easylaw): {src}')
        continue
    cat_l = cat.lower()
    title_l = title.lower()
    if cat_l in ('statute', 'law', 'act') or 'laws/' in src.lower() or 'ordinance' in title_l or (('act,' in title_l or 'act 19' in title_l) and ' vs ' not in title_l and ' v ' not in title_l):
        print(f'SKIP (statute): {title}')
        continue
    filtered.append(doc)
print(f'FINAL COUNT: {len(filtered)}')
