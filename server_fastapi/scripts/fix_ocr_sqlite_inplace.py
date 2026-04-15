import sqlite3
import re
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'faiss_index', 'metadata.db')

def apply_ocr_fixes(text):
    if not text:
        return text
    
    # Common OCR merge errors in legal headers
    text = text.replace("ERSUS", "VERSUS")
    text = re.sub(r'([A-Z]+)FOR THE', r'\1 FOR THE', text)  # ADVOCATEFOR -> ADVOCATE FOR
    text = re.sub(r'([A-Z]+)COURT', r'\1 COURT', text)      # SUPREMECOURT -> SUPREME COURT
    
    # Section numbers getting merged
    text = re.sub(r'SECTION([0-9])', r'SECTION \1', text, flags=re.IGNORECASE)
    
    # Basic missing boundaries between lower and uppercase (indicates missing space) 
    # e.g., "dismissedThe appeal"
    # Be careful not to break camelCase variables, but mostly legal text is not camelCase
    text = re.sub(r'([a-z])([A-Z][a-z])', r'\1 \2', text)
    
    return text

def fix_metadata_db():
    print(f"Connecting to database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Fetching chunks...")
    cur.execute("SELECT row_id, excerpt, title FROM chunks")
    rows = cur.fetchall()
    
    print(f"Applying OCR fixes to {len(rows)} chunks. This might take a minute...")
    
    updates = []
    for row_id, excerpt, title in rows:
        needs_update = False
        
        # Protect against None values
        new_excerpt = apply_ocr_fixes(excerpt) if excerpt else excerpt
        new_title = apply_ocr_fixes(title) if title else title
        
        if new_excerpt != excerpt or new_title != title:
            updates.append((new_excerpt, new_title, row_id))
            
    if updates:
        print(f"Identified {len(updates)} chunks that require fixes. Updating...")
        cur.executemany("UPDATE chunks SET excerpt = ?, title = ? WHERE row_id = ?", updates)
        conn.commit()
        print("Update complete!")
    else:
        print("No OCR fixes were needed.")

    conn.close()

if __name__ == "__main__":
    fix_metadata_db()
