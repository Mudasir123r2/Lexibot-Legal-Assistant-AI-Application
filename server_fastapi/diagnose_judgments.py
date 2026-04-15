"""
Show sample excerpts that contain vs/versus/appellant patterns 
to understand what real judgment data looks like
"""
import sqlite3

conn = sqlite3.connect('data/faiss_index/metadata.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Find rows with actual judgment patterns
rows = cur.execute("""
    SELECT row_id, title, source_file, court, case_number, date, excerpt
    FROM chunks
    WHERE (
        excerpt LIKE '%versus%' OR 
        excerpt LIKE '%Appellant%' OR 
        excerpt LIKE '%Petitioner%' OR
        excerpt LIKE '%W.P.%' OR
        excerpt LIKE '%W.P No%' OR
        excerpt LIKE '%PLD%' OR
        excerpt LIKE '%SCMR%' OR
        excerpt LIKE '%YLR%' OR
        excerpt LIKE '%CLC%'
    )
    AND title LIKE 'Document from%'
    LIMIT 8
""").fetchall()

print(f"Sample judgment-like rows:\n")

for r in rows:
    print(f"=== row_id={r['row_id']} ===")
    print(f"Title: {r['title']}")
    print(f"Court: {r['court']}")
    print(f"Case#: {r['case_number']}")
    print(f"Source: {r['source_file']}")
    print(f"Excerpt:\n{r['excerpt'][:800]}")
    print()

conn.close()
