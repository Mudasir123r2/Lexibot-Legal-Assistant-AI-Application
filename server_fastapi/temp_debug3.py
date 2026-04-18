from services.rag_pipeline import get_rag_pipeline
rag = get_rag_pipeline()
docs = rag.search_judgments('divorce cases', top_k=19)
print(f'Initial docs: {len(docs)}')
for i, doc in enumerate(docs):
    src = str(doc.get('source_file') or '')
    title = str(doc.get('title') or '').lower()
    cat = str(doc.get('category') or doc.get('case_type') or doc.get('caseType') or '').lower()
    print(f'Doc {i}: src={src}, title={title[:30]}, cat={cat}')
    if 'easylaw' not in src.lower() and not src.lower().startswith('administrator'):
        print('  -> Failed easylaw/admin check')
        continue
    if cat in ('statute', 'law', 'act') or 'laws/' in src.lower() or 'ordinance' in title or (('act,' in title or 'act 19' in title or 'act 20' in title) and ' vs ' not in title and ' v ' not in title and ' v. ' not in title):
        print('  -> Failed statute check')
        continue
    journal = str(doc.get('journal') or '')
    case_num = str(doc.get('case_number') or doc.get('caseNumber') or '')
    if journal or 'Appeal No' in case_num or src.startswith('administrator'):
        print('  -> PASSED!')
    else:
        print('  -> Failed final inclusion check')
