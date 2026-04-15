import sqlite3
import re
from pathlib import Path

DB_PATH = Path("data/faiss_index/metadata.db")

def main():
    if not DB_PATH.exists():
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Find rows with missing titles but promising filenames
    logger_query = """
    SELECT row_id, source_file, excerpt 
    FROM chunks 
    WHERE (title IS NULL OR title = '' OR title = 'Untitled') 
    AND (source_file LIKE '%PLD%' OR source_file LIKE '%SCMR%' OR source_file LIKE '%CLC%')
    LIMIT 10
    """
    
    rows = cursor.execute(logger_query).fetchall()
    print(f"Found {len(rows)} samples for research.\n")

    for i, row in enumerate(rows):
        print(f"--- SAMPLE {i+1} ---")
        print(f"ID: {row['row_id']}")
        print(f"FILE: {row['source_file']}")
        print(f"EXCERPT HEAD:\n{row['excerpt'][:500]}")
        print("-" * 50)

    conn.close()

if __name__ == "__main__":
    main()
