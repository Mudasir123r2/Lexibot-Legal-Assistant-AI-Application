import sqlite3
import re

def test_overlap():
    conn = sqlite3.connect('data/faiss_index/metadata.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT mock_id FROM chunks GROUP BY mock_id HAVING COUNT(*) > 5 LIMIT 1")
    doc_id = c.fetchone()[0]

    c.execute("SELECT excerpt FROM chunks WHERE mock_id = ? ORDER BY row_id ASC", (doc_id,))
    excerpts = [r["excerpt"] for r in c.fetchall()]

    e1 = excerpts[0]
    e2 = excerpts[1]

    # Let's find longest overlap
    e1_tail = e1[-100:]
    if e1_tail in e2:
        idx = e2.find(e1_tail)
        print(f"OVERLAP FOUND! At index {idx} in chunk 2")
    else:
        # Check shorter suffixes
        for i in range(10, min(200, len(e1)), 10):
            if e1[-i:] in e2:
                print(f"Overlap found for length {i}: {repr(e1[-i:])}")
                break
        else:
            print("NO STRICT OVERLAP FOUND")

if __name__ == '__main__':
    test_overlap()