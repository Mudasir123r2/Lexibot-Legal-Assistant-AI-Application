import sqlite3
import re
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'faiss_index', 'metadata.db')

def fix_title_artifacts(text):
    if not text: return text
    
    # 1. Fix weird spaced-out country/region names and common words
    text = text.replace('FEDERA TION', 'FEDERATION')
    text = text.replace('P AKIST AN', 'PAKISTAN')
    text = text.replace('MUKHT AR', 'MUKHTAR')
    text = text.replace('P AK', 'PAK')
    
    # 2. Fix the "arties: " or "Parties: " prefix that leaked into the title
    text = re.sub(r'^(?:[Pp]arty|[Pp]arties|[Aa]rties|PARTIES)[\s:]*', '', text).strip()
    
    # Strip any leading dashes or dots
    text = re.sub(r'^[\.\-\s]+', '', text)
    
    # Clean up "By High Court" / "by High Court"
    text = text.replace('By High Court', 'High Court')
    text = text.replace('by High Court', 'High Court')
    
    # Supreme Court "of pakistan" instead of name (if any weird artifact exists)
    # The user noted that some say "Supreme Court of pakistan instead of name". 
    # This might mean the party names are missing entirely and it just says 19XX SCMR 123 - Supreme Court.
    # We can't hallucinate the names if they are lost in extraction unless we fetch the excerpt, but we can capitalize "pakistan".
    text = text.replace('of pakistan', 'of Pakistan')

    return text.strip()

def run_phase3():
    print(f"Connecting to database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Fetching titles for Phase 3 cleanup...")
    cur.execute("SELECT row_id, title FROM chunks")
    rows = cur.fetchall()
    
    updates = []
    for row_id, title in rows:
        new_title = fix_title_artifacts(title)
        
        if new_title != title:
            updates.append((new_title, row_id))

    if updates:
        print(f"Applying Phase 3 title fixes to {len(updates)} chunks. Updating...")
        batch_size = 10000
        for i in range(0, len(updates), batch_size):
            cur.executemany("UPDATE chunks SET title = ? WHERE row_id = ?", updates[i:i+batch_size])
            conn.commit()
            print(f"Processed batch {i} to {i+batch_size}...")
        print("Update complete!")
    else:
        print("No Phase 3 fixes needed.")

    conn.close()

if __name__ == "__main__":
    run_phase3()