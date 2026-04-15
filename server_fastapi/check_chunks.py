import sqlite3
import os

db_path = "data/faiss_index/metadata.db"
target_id = "eaed14fde18f4a83e19f30e7"

if not os.path.exists(db_path):
    print(f"DATABASE NOT FOUND at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT excerpt FROM chunks WHERE mock_id = ?", (target_id,)).fetchall()
print(f"FOUND {len(rows)} CHUNKS")
for i, row in enumerate(rows):
    e = row["excerpt"]
    print(f"CHUNK {i}: Length {len(e) if e else 'NULL'}")
    if e:
        print(f"SAMPLE: {e[:100]}...")
conn.close()
