import os
import sqlite3

db_path = 'data/faiss_index/metadata.db'
pkl_path = 'data/faiss_index/metadata.pkl'

print('DB exists:', os.path.exists(db_path))
print('PKL exists:', os.path.exists(pkl_path))

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print('Tables:', [t[0] for t in tables])
    
    table_name = tables[0][0] if tables else None
    if table_name:
        rows = cur.execute(f'SELECT * FROM {table_name} LIMIT 5').fetchall()
        if rows:
            keys = list(rows[0].keys())
            print('Columns:', keys)
            for i, r in enumerate(rows):
                print(f'\n--- ROW {i+1} ---')
                for k in keys:
                    val = r[k]
                    if isinstance(val, str) and len(val) > 200:
                        val = val[:200] + '...'
                    print(f'  {k}: {val}')
    
    # Count total rows
    total = cur.execute(f'SELECT COUNT(*) FROM {table_name}').fetchone()[0]
    print(f'\nTotal rows: {total}')
    
    # Count bad titles
    bad = cur.execute(
        "SELECT COUNT(*) FROM chunks WHERE title IS NULL OR title = '' OR title LIKE 'Untitled%' OR title LIKE 'judgment-%'"
    ).fetchone()[0]
    print(f'Bad/missing titles: {bad}')
    
    conn.close()
