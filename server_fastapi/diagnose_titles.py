"""
Title extraction diagnostic - see what excerpt data looks like for various rows
"""
import sqlite3, re

conn = sqlite3.connect('data/faiss_index/metadata.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Sample rows where title looks like "Document from..."
rows = cur.execute("""
    SELECT row_id, title, source_file, court, case_number, date, excerpt
    FROM chunks
    WHERE title LIKE 'Document from%'
    LIMIT 10
""").fetchall()

print(f"Rows with 'Document from' title: sampling 10\n")

for r in rows:
    print(f"=== row_id={r['row_id']} ===")
    print(f"Title: {r['title']}")
    print(f"Court: {r['court']}")
    print(f"Case#: {r['case_number']}")
    print(f"Date: {r['date']}")
    print(f"Excerpt (first 600 chars):\n{r['excerpt'][:600]}")
    print()

conn.close()
