import re
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'faiss_index', 'metadata.db')

def clean_easylaw_text(text):
    if not text: return text
    
    original = text
    
    # 1. Clean Title prefix if it says "Document from Easy Law..."
    text = re.sub(r'Document\s+from\s+Easy\s+Law.*?,\s*', '', text, flags=re.IGNORECASE)

    # 2. Strip useless footers
    text = re.sub(r'COPYRIGHT 20\d{2}\s*easylaw.*?All Rights Reserved\.?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'DISCLAIMER\s*\(?https?://.*?easylaw\.ai.*?\)?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'CASE\s*NO\.\s*\d+[\s\n]*DOWNLOAD\s*CASE', '', text, flags=re.IGNORECASE)
    
    # 3. Fix specific capitalized spaced words & typos
    text = text.replace('F AMIL Y', 'FAMILY')
    text = text.replace('COUR T', 'COURT')
    text = text.replace('LA W', 'LAW')
    text = text.replace('LA TIF', 'LATIF')
    text = text.replace('VVVERSUS', 'VERSUS')
    text = text.replace('VVERSUS', 'VERSUS')
    text = text.replace('v. VERSUS', 'VERSUS')
    
    # Merged versus
    text = re.sub(r'(VERSUS)([A-Z]{2,})', r'\1 \2', text)
    # Merged spaces between numbers and IN THE
    text = re.sub(r'(\d{4})IN THE', r'\1 IN THE', text)

    # 4. Extract and fix merged headers if they exist in a single line without newlines
    # e.g. "Court LAHORE HIGH COURT Date 2003-07-09 Appeal No." -> "Court: ...\nDate: ..."
    if 'Court' in text and 'Judge' in text and 'Parties' in text:
        text = re.sub(r'(?<!\n)\b(Court|Date|Appeal No\.|Judge|Parties|Lawyers|Statutes|Judgment|Issue|Facts|Held|Decision|Arguments)(:?)\s', r'\n\1: ', text)

    # Clean up double newlines and spaces
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

def fix_easylaw_chunks():
    print(f"Connecting to database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("Fetching chunks for EasyLaw footer & header cleanup...")
    cur.execute("SELECT row_id, excerpt, title FROM chunks")
    rows = cur.fetchall()
    
    updates = []
    for row_id, excerpt, title in rows:
        
        new_excerpt = clean_easylaw_text(excerpt) if excerpt else excerpt
        new_title = clean_easylaw_text(title) if title else title
        
        if new_excerpt != excerpt or new_title != title:
            updates.append((new_excerpt, new_title, row_id))

    if updates:
        # Commit in batches of 10000
        print(f"Applying advanced OCR spatial fixes to {len(updates)} chunks. Updating...")
        batch_size = 10000
        for i in range(0, len(updates), batch_size):
            cur.executemany("UPDATE chunks SET excerpt = ?, title = ? WHERE row_id = ?", updates[i:i+batch_size])
            conn.commit()
            print(f"Processed batch {i} to {i+batch_size}...")
        print("Update complete!")
    else:
        print("No EasyLaw advanced fixes needed.")

    conn.close()

if __name__ == "__main__":
    fix_easylaw_chunks()