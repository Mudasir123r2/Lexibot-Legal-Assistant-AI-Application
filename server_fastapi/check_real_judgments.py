import sqlite3

db_path = r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\data\faiss_index\metadata.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT source_file, title, court, case_number, excerpt FROM chunks WHERE excerpt LIKE "% Versus %" LIMIT 5')
rows = cursor.fetchall()
for row in rows:
    print(f"FILE: {row['source_file']}")
    print(f"TITLE: {row['title']}")
    print(f"COURT: {row['court']}")
    print(f"CASE_NUM: {row['case_number']}")
    print(f"EXCERPT: {repr(row['excerpt'][:400])}")
    print("-" * 50)

conn.close()
