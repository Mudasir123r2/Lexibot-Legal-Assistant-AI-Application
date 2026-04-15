"""
Updates the existing metadata.db to include the mock_id (MD5 hash) column and index.
This allows the 'get_judgment' route to find FAISS documents instantly by ID.
"""
import sqlite3
import hashlib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = Path("data/faiss_index/metadata.db")

def main():
    if not DB_PATH.exists():
        logger.error(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    logger.info("Checking database schema...")
    
    # 1. Add mock_id column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE chunks ADD COLUMN mock_id TEXT")
        logger.info("Added 'mock_id' column.")
    except sqlite3.OperationalError:
        logger.info("'mock_id' column already exists.")

    # 2. Check for missing hashes
    rows_to_update = cursor.execute("SELECT COUNT(*) FROM chunks WHERE mock_id IS NULL").fetchone()[0]
    
    if rows_to_update > 0:
        logger.info(f"Generating hashes for {rows_to_update:,} rows...")
        
        # We'll batch this to avoid memory issues
        BATCH_SIZE = 10000
        offset = 0
        total_updated = 0
        
        while True:
            # Fetch rows that need an ID
            rows = cursor.execute(
                "SELECT row_id, title, source_file, case_number FROM chunks WHERE mock_id IS NULL LIMIT ?",
                (BATCH_SIZE,)
            ).fetchall()
            
            if not rows:
                break
                
            updates = []
            for row in rows:
                title = row["title"] or "Untitled"
                source = str(row["source_file"] or "")
                case_num = str(row["case_number"] or "")
                doc_key = title + "||" + source + "||" + case_num
                mock_id = hashlib.md5(doc_key.encode()).hexdigest()[:24]
                updates.append((mock_id, row["row_id"]))
            
            cursor.executemany("UPDATE chunks SET mock_id = ? WHERE row_id = ?", updates)
            conn.commit()
            
            total_updated += len(rows)
            logger.info(f"  Updated {total_updated:,} / {rows_to_update:,} rows...")

    # 3. Create index for fast lookups
    logger.info("Creating index on mock_id...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mock ON chunks(mock_id)")
    conn.commit()
    
    logger.info("✅ Database successfully updated with indexed judgment IDs.")
    conn.close()

if __name__ == "__main__":
    main()
