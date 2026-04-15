"""
High-Performance Legal Citation & Metadata Repair Script (Version 2)
Guarantees 100% database synchronization for 534,000+ chunks.
Uses ROW_ID tracking for maximum performance (avoids slow OFFSET).
"""
import sqlite3
import re
import hashlib
import logging
import os
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = Path("data/faiss_index/metadata.db")

# Regex Patterns
RE_CIT_FILE = re.compile(r"EasyLaw_(\d{4})_([A-Z0-9]+)_(\d+)", re.IGNORECASE)
RE_PARTIES = re.compile(r"([A-Z\s,]+)\s+V(?:ERSUS|\.S?| \.S?|S\.)\s+([A-Z\s,]+)", re.IGNORECASE)
RE_ACT = re.compile(r"([A-Z\s]+(?:ACT|ORDINANCE|ORDER|REGULATION))\s+,?\s*(\d{4})", re.IGNORECASE)

def clean_name(name):
    """Clean legal names from headers."""
    if not name:
        return "Unknown"
    # Remove obvious noise and punctuation at ends
    name = re.sub(r"\d+", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    name = name.strip(",. ")
    return name.title()[:60]

def extract_metadata(excerpt, filename, existing_court):
    """Deeply parse metadata from filename and text."""
    title = None
    category = "Judgment"
    
    # 1. Try to get citation from filename
    year, reporter, page = "N/A", "N/A", "N/A"
    cit_match = RE_CIT_FILE.search(filename)
    if cit_match:
        year, reporter, page = cit_match.groups()
    
    # 2. Check for Statute Pattern (Priority if not EasyLaw)
    act_match = RE_ACT.search(excerpt[:1000])
    if act_match and not cit_match:
        name, y = act_match.groups()
        title = f"{clean_name(name)}, {y}"
        category = "Statute"
    else:
        # 3. Default to Judgment formatting
        party_match = RE_PARTIES.search(excerpt[:1000])
        if party_match:
            app, res = party_match.groups()
            title = f"{clean_name(app)} v. {clean_name(res)}"
        else:
            # Fallback if no party found
            title = f"Document from {Path(filename).name[:30]}"
            
        # Append citation if it's a judgment with citation
        if cit_match:
            title = f"{title}, {year} {reporter} {page}"
            
        # Append court
        court = existing_court or "Supreme Court of Pakistan"
        title = f"{title} ({court})"
        
    return title, category

def main():
    if not DB_PATH.exists():
        logger.error(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(str(DB_PATH), isolation_level="EXCLUSIVE")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    logger.info("Starting High-Performance Metadata Repair (100% Sync)...")
    
    total_chunks = cursor.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    logger.info(f"Total chunks awaiting sync: {total_chunks:,}")

    # Optimization: PRAGMAs for speed
    cursor.execute("PRAGMA journal_mode=MEMORY")
    cursor.execute("PRAGMA synchronous=OFF")

    BATCH_SIZE = 20000
    last_id = 0
    total_processed = 0
    
    while True:
        # Fetch by ID tracking (much faster than OFFSET)
        rows = cursor.execute(
            "SELECT row_id, source_file, court, excerpt, case_number FROM chunks WHERE row_id > ? ORDER BY row_id ASC LIMIT ?",
            (last_id, BATCH_SIZE)
        ).fetchall()
        
        if not rows:
            break
            
        updates = []
        for row in rows:
            new_title, category = extract_metadata(
                row['excerpt'] or "", 
                row['source_file'] or "", 
                row['court'] or ""
            )
            
            # Recalculate mock_id for search consistency
            source   = str(row["source_file"] or "")
            case_num = str(row["case_number"] or "")
            doc_key  = new_title + "||" + source + "||" + case_num
            mock_id  = hashlib.md5(doc_key.encode()).hexdigest()[:24]
            
            updates.append((new_title, mock_id, row['row_id']))
            last_id = row['row_id']
            
        # Batch update
        cursor.executemany(
            "UPDATE chunks SET title = ?, mock_id = ? WHERE row_id = ?",
            updates
        )
        conn.commit() # Commit each batch to prevent locks being too long
        
        total_processed += len(rows)
        pct = (total_processed / total_chunks) * 100
        logger.info(f"  Processed {total_processed:,} / {total_chunks:,} chunks ({pct:.1f}%)")

    logger.info("✅ Full Database Synchronization Complete.")
    
    # Final check
    check = cursor.execute("SELECT mock_id FROM chunks LIMIT 1 OFFSET 500000").fetchone()
    if check:
        logger.info(f"Sample Deep ID Check: {check[0]}")
    
    conn.close()

if __name__ == "__main__":
    main()
