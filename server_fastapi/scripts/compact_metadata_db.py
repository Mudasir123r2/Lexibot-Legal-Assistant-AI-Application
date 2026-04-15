"""
Compacts the 60GB metadata.db by rebuilding it without full document content.
For search, we only need title, court, date, case_number, excerpt (500 chars).
Full text is reconstructed from FAISS chunks when a judgment is opened.
"""
import sys, sqlite3, logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INDEX_DIR   = Path("data/faiss_index")
OLD_DB      = INDEX_DIR / "metadata.db"
NEW_DB      = INDEX_DIR / "metadata_compact.db"


def main():
    if not OLD_DB.exists():
        logger.error(f"metadata.db not found at {OLD_DB}")
        sys.exit(1)

    old_size_gb = OLD_DB.stat().st_size / (1024**3)
    logger.info(f"Source DB size: {old_size_gb:.1f} GB")

    # --- Build compact DB ---
    new_conn = sqlite3.connect(str(NEW_DB))
    new_conn.execute("PRAGMA journal_mode=WAL")
    new_conn.execute("PRAGMA synchronous=NORMAL")
    new_conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            row_id      INTEGER PRIMARY KEY,
            title       TEXT,
            source_file TEXT,
            court       TEXT,
            judge       TEXT,
            date        TEXT,
            case_number TEXT,
            case_type   TEXT,
            category    TEXT,
            excerpt     TEXT
        )
    """)
    new_conn.execute("CREATE INDEX IF NOT EXISTS idx_title   ON chunks(title)")
    new_conn.execute("CREATE INDEX IF NOT EXISTS idx_court   ON chunks(court)")
    new_conn.execute("CREATE INDEX IF NOT EXISTS idx_source  ON chunks(source_file)")
    new_conn.commit()

    # --- Stream from old DB ---
    old_conn = sqlite3.connect(str(OLD_DB), check_same_thread=False)
    old_conn.row_factory = sqlite3.Row

    total_rows = old_conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    logger.info(f"Total rows to compact: {total_rows:,}")

    BATCH = 10_000
    offset = 0
    written = 0

    while True:
        rows = old_conn.execute(
            """SELECT row_id, title, source_file, court, judge, date,
                      case_number, case_type, category,
                      SUBSTR(COALESCE(excerpt, content, ''), 1, 500) AS excerpt
               FROM chunks
               ORDER BY row_id
               LIMIT ? OFFSET ?""",
            (BATCH, offset)
        ).fetchall()

        if not rows:
            break

        new_conn.executemany(
            """INSERT OR IGNORE INTO chunks
               (row_id, title, source_file, court, judge, date,
                case_number, case_type, category, excerpt)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            [
                (r["row_id"], r["title"], r["source_file"], r["court"],
                 r["judge"], r["date"], r["case_number"],
                 r["case_type"], r["category"], r["excerpt"])
                for r in rows
            ]
        )
        new_conn.commit()
        written += len(rows)
        offset  += BATCH

        pct = (written / total_rows) * 100
        logger.info(f"  {pct:.1f}%  —  {written:,} / {total_rows:,} rows")

    old_conn.close()

    # VACUUM to reclaim space
    logger.info("Running VACUUM on compact DB...")
    new_conn.execute("VACUUM")
    new_conn.close()

    new_size_mb = NEW_DB.stat().st_size / (1024**2)
    logger.info(f"\n✅ Compact DB ready: {new_size_mb:.0f} MB  (was {old_size_gb*1024:.0f} MB)")

    # Swap files
    backup = INDEX_DIR / "metadata_full.db"
    OLD_DB.rename(backup)
    NEW_DB.rename(OLD_DB)
    logger.info(f"Full DB preserved at: {backup}")
    logger.info(f"Compact DB now live at: {OLD_DB}")
    logger.info("Done. Restart python main.py to use the new compact index.")


if __name__ == "__main__":
    main()
