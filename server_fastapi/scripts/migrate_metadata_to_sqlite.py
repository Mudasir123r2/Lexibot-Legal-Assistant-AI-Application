"""
Memory-safe chunked migration: metadata.pkl → SQLite
Uses a subprocess trick to process in chunks and avoid OOM.
"""
import sys, os, sqlite3, json, subprocess, pickle
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INDEX_DIR = Path("data/faiss_index")
PKL_PATH  = INDEX_DIR / "metadata.pkl"
DB_PATH   = INDEX_DIR / "metadata.db"

KNOWN_COLS = {"title", "source_file", "court", "judge", "date",
              "case_number", "case_type", "category", "excerpt", "content"}

def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            row_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT,
            source_file TEXT,
            court       TEXT,
            judge       TEXT,
            date        TEXT,
            case_number TEXT,
            case_type   TEXT,
            category    TEXT,
            excerpt     TEXT,
            content     TEXT,
            extra_json  TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_title ON chunks(title)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_court ON chunks(court)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_source ON chunks(source_file)")
    conn.commit()

def dict_to_row(d: dict) -> tuple:
    extra = {k: v for k, v in d.items() if k not in KNOWN_COLS and k != "row_id"}
    return (
        str(d.get("title") or "")[:500],
        str(d.get("source_file") or "")[:300],
        str(d.get("court") or "")[:200],
        str(d.get("judge") or "")[:300],
        str(d.get("date") or "")[:50],
        str(d.get("case_number") or "")[:200],
        str(d.get("case_type") or "")[:100],
        str(d.get("category") or "")[:100],
        str(d.get("excerpt") or d.get("content") or "")[:500],
        str(d.get("content") or ""),
        json.dumps(extra, default=str) if extra else None,
    )

def insert_batch(conn, batch):
    conn.executemany("""
        INSERT INTO chunks
        (title, source_file, court, judge, date, case_number,
         case_type, category, excerpt, content, extra_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, batch)
    conn.commit()

def main():
    if not PKL_PATH.exists():
        logger.error(f"metadata.pkl not found at {PKL_PATH}")
        sys.exit(1)

    file_size_mb = PKL_PATH.stat().st_size / (1024 * 1024)
    logger.info(f"metadata.pkl size: {file_size_mb:.1f} MB")

    conn = sqlite3.connect(str(DB_PATH))
    init_db(conn)

    # Check existing row count
    existing = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    if existing > 0:
        logger.info(f"SQLite already has {existing:,} rows. Nothing to migrate.")
        conn.close()
        return

    logger.info("Attempting to load metadata.pkl...")
    logger.info("This may take a few minutes for a large file. Please be patient.")

    BATCH_SIZE = 3000
    batch = []
    total = 0

    try:
        with open(PKL_PATH, "rb") as f:
            all_data = pickle.load(f)

        total_items = len(all_data)
        logger.info(f"Loaded {total_items:,} chunks from pickle. Writing to SQLite...")

        for i, item in enumerate(all_data):
            if not isinstance(item, dict):
                continue
            batch.append(dict_to_row(item))
            if len(batch) >= BATCH_SIZE:
                insert_batch(conn, batch)
                total += len(batch)
                batch = []
                pct = (i / total_items) * 100
                logger.info(f"  Progress: {pct:.1f}% — {total:,} chunks written")

        if batch:
            insert_batch(conn, batch)
            total += len(batch)

        conn.close()
        logger.info(f"\n✅ Migration complete: {total:,} chunks written to SQLite")
        logger.info(f"SQLite DB size: {DB_PATH.stat().st_size / (1024*1024):.1f} MB")

        # Rename pickle to mark as migrated (keep it as backup)
        backup = str(PKL_PATH) + ".migrated"
        PKL_PATH.rename(backup)
        logger.info(f"Original pickle preserved as: {backup}")

    except MemoryError:
        conn.close()
        logger.error("=" * 60)
        logger.error("MemoryError: Not enough RAM to load the 2.2GB pickle file.")
        logger.error("")
        logger.error("YOUR OPTIONS:")
        logger.error("")
        logger.error("OPTION A (keep existing data, no re-ingestion needed):")
        logger.error("  Increase virtual memory on Windows:")
        logger.error("  Control Panel → System → Advanced → Virtual Memory")
        logger.error("  Set to at least 8GB (8192 MB)")
        logger.error("  Then run this script again.")
        logger.error("")
        logger.error("OPTION B (re-ingest from scratch, takes hours):")
        logger.error("  del data\\faiss_index\\faiss.index")
        logger.error("  del data\\faiss_index\\metadata.pkl")
        logger.error("  Then re-run your ingestion scripts.")
        logger.error("  The new ingestion writes directly to SQLite — this won't happen again.")
        logger.error("=" * 60)
        sys.exit(2)

    except Exception as e:
        conn.close()
        logger.error(f"Migration failed: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
