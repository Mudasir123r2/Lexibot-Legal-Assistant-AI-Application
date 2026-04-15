import sqlite3
import re
from pathlib import Path
import sys

# Ensure utils can be imported
sys.path.append(str(Path(__file__).parent))
from utils.formatters import extract_full_metadata, format_judgment_title, extract_court

def fix_easylaw_titles():
    db_path = Path("data/faiss_index/metadata.db")
    if not db_path.exists():
        print(f"DB not found at {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Select all unique mock_ids that belong to Easy Law
    c.execute("SELECT mock_id FROM chunks WHERE source_file LIKE 'administrator%' OR source_file LIKE 'EasyLaw_%' OR excerpt LIKE '%Journal %' OR excerpt LIKE '%\nAppeal No.%' GROUP BY mock_id")
    mock_ids = [row["mock_id"] for row in c.fetchall()]

    print(f"Found {len(mock_ids)} Easy Law judgments to process.")

    updates = []
    for count, mock_id in enumerate(mock_ids, 1):
        c.execute("SELECT row_id, title, court, case_number, excerpt, source_file FROM chunks WHERE mock_id = ? ORDER BY row_id ASC", (mock_id,))
        rows = c.fetchall()
        if not rows: continue

        # The first chunk usually has the header
        first_row = rows[0]
        excerpt = str(first_row["excerpt"] or "")
        old_title = str(first_row["title"] or "")
        
        # 1. Very dirty title cleanup
        # Clean up v. ERSUS and (IN CA) artifacts from the old title
        clean_old_title = re.sub(r'v\.\s*[Ee][rR][sS][uU][sS]', 'v.', old_title)
        clean_old_title = re.sub(r'\bVERSUS\b', 'v.', clean_old_title, flags=re.IGNORECASE)
        clean_old_title = re.sub(r'ANW\s+AR', 'ANWAR', clean_old_title)
        clean_old_title = re.sub(r'MUKHT\s+AR', 'MUKHTAR', clean_old_title)
        clean_old_title = re.sub(r'REHABILIT\s+ATION', 'REHABILITATION', clean_old_title)
        clean_old_title = re.sub(r'P\s+AKIST\s+AN', 'PAKISTAN', clean_old_title)
        clean_old_title = re.sub(r'\s*\([iI][nN]\s+C[A-Z\.]*[\s\.,]*.*?\)', '', clean_old_title)
        clean_old_title = re.sub(r'\bIN\s+CA\b\s*\)\.?', '', clean_old_title)
        clean_old_title = re.sub(r'\s+', ' ', clean_old_title).strip('. ,-')

        # 2. Extract structured metadata cleanly using our new fixed regexes
        court = extract_court(first_row["court"], excerpt)
        # 3. Format title properly
        new_title = format_judgment_title(
            citation="", 
            court=court, 
            original_title=clean_old_title, 
            excerpt=excerpt, 
            source_file=first_row["source_file"]
        )

        # In case the new title still has some artifacts (like stray 'v. ERSUS' if it slipped)
        new_title = re.sub(r'v\.\s*[Ee][rR][sS][uU][sS]', 'v.', new_title)
        new_title = re.sub(r'\bVERSUS\b', 'v.', new_title, flags=re.IGNORECASE)
        new_title = re.sub(r'ANW\s+AR', 'ANWAR', new_title)
        new_title = re.sub(r'REHABILIT\s+ATION', 'REHABILITATION', new_title)
        new_title = re.sub(r'P\s+AKIST\s+AN', 'PAKISTAN', new_title)
        new_title = re.sub(r'\s*\([iI][nN]\s+C[A-Z\.]*[\s\.,]*.*?\)', '', new_title)
        new_title = re.sub(r'\bIN\s+CA\b\s*\)\.?', '', new_title)
        new_title = re.sub(r'\s+', ' ', new_title).strip('. ,-')

        # If it's different, we push it to update queue
        if old_title != new_title:
            updates.append((new_title, mock_id))

        if count % 1000 == 0:
            print(f"Processed {count}/{len(mock_ids)}")

    print(f"Found {len(updates)} titles to fix. Updating database...")
    for chunk in [updates[i:i+1000] for i in range(0, len(updates), 1000)]:
        c.executemany("UPDATE chunks SET title = ? WHERE mock_id = ?", chunk)
        conn.commit()

    conn.close()
    print("Done! Easy Law titles have been perfectly cleaned.")

if __name__ == "__main__":
    fix_easylaw_titles()
