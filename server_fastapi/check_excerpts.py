import sqlite3

db_path = r'D:\Lexibot-Legal-Assistant-AI-Application\server_fastapi\data\faiss_index\metadata.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT excerpt FROM chunks WHERE excerpt LIKE "% vs %" OR excerpt LIKE "% versus %" OR excerpt LIKE "% v. %" LIMIT 3')
rows = cursor.fetchall()
for row in rows:
    print("EXCERPT:", repr(row['excerpt'][:300]))

conn.close()
