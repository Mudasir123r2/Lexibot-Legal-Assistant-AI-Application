import sqlite3
import sys
sys.path.insert(0, '.')
from routes.judgments import format_judgment_title

conn = sqlite3.connect('data/faiss_index/metadata.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute('''
  SELECT mock_id, title, court, case_number, date, source_file, excerpt
  FROM chunks
  GROUP BY mock_id
  LIMIT 20
''').fetchall()

print("Sample of 20 judgment titles (ON-THE-FLY FORMATTING):")
print("="*80)
for r in rows:
    title = r["title"] or ""
    court = r["court"] or ""
    case_num = r["case_number"] or ""
    source = r["source_file"] or ""
    excerpt = r["excerpt"] or ""
    
    formatted_title = format_judgment_title(case_num, court, title, excerpt, source)
    
    print(f"Original: {title[:80]}...")
    print(f"Result:   {formatted_title}")
    # print(f"Source:   {source}")
    print("-" * 60)

conn.close()
