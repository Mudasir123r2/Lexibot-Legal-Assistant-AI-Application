import re
import sqlite3
import os

def check_court(citation):
    if not citation: return None
    cit = citation.upper()
    if 'SCMR' in cit or 'PLD SC' in cit or ' SC ' in cit:
        return "Supreme Court of Pakistan"
    if 'YLR' in cit or 'PLD' in cit or 'CLC' in cit or 'MLD' in cit or 'PCrLJ' in cit:
        if 'SC' not in cit:  # PLD 1971 Lahore High Court
            return "High Court"
    return None

def clean_text(text):
    if not text: return text
    text = str(text)
    
    # Extreme Versus Anomalies
    text = re.sub(r'(?i)\bv\.\s*v+ersus\b', 'VERSUS', text)
    text = re.sub(r'(?i)\bV+ERSUS\b', 'VERSUS', text)
    text = re.sub(r'(?i)V+ERSUS([A-Za-z])', r'VERSUS \1', text) 
    text = re.sub(r'(?i)([A-Za-z]+)V+ERSUS', r'\1 VERSUS', text) 
    
    # Merged roles (e.g. SHERRIFFPETITIONER)
    roles = ['PETITIONER', 'RESPONDENT', 'APPELLANT', 'DEFENDANT', 'PLAINTIFF']
    for role in roles:
        text = re.sub(r'([A-Z])(' + role + r'S?)\b', r'\1 \2', text)
        text = re.sub(r'([a-z])(' + role + r's?)\b', r'\1 \2', text, flags=re.IGNORECASE)

    # Specific known OCR typos 
    text = re.sub(r'(?i)\bTHROUGH1?\s*LEGD\b', 'THROUGH LEGAL', text)
    
    # Dots and spaces
    text = re.sub(r'\.\s*\.\s*\.*', ' ', text)
    text = text.replace("v. VERSUS", "VERSUS")
    text = text.replace("VVERSUS", "VERSUS")

    # Spaced letters in F ATIMA and RIT A type names
    text = re.sub(r'\b([A-Z])\s([A-Z][a-z]+)\b', r'\1\2', text)
    text = re.sub(r'\b([A-Z]{3,})\s([A-Z])\b', r'\1\2', text)
    
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'faiss_index', 'metadata.db')

def update_metadata_and_titles():
    print(f"Connecting to database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("Fetching chunks for comprehensive metadata pass...")
    cur.execute("SELECT row_id, title, court, case_number FROM chunks")
    rows = cur.fetchall()
    
    updates = []
    
    for row in rows:
        row_id, title, court, citation = row['row_id'], row['title'], row['court'], row['case_number']
        
        new_title = clean_text(title)
        
        # Determine actual court from citation if title has contradiction
        actual_court = check_court(new_title)
        new_court = court
        
        # If the citation says SCMR, it is the Supreme Court regardless of what OCR says
        if actual_court and 'High Court' in str(new_court) and actual_court == 'Supreme Court of Pakistan':
            new_court = actual_court
            new_title = new_title.replace('High Court', 'Supreme Court of Pakistan')
            
        if actual_court and 'Supreme Court' in str(new_court) and actual_court == 'High Court':
            new_court = actual_court
            new_title = new_title.replace('Supreme Court', 'High Court')

        if new_title != title or new_court != court:
            updates.append((new_title, new_court, row_id))

    if updates:
        print(f"Applying metadata fixes to {len(updates)} titles and courts...")
        cur.executemany("UPDATE chunks SET title = ?, court = ? WHERE row_id = ?", updates)
        conn.commit()
        print("Done!")
    else:
        print("No metadata title fixes needed.")

    conn.close()

if __name__ == "__main__":
    update_metadata_and_titles()