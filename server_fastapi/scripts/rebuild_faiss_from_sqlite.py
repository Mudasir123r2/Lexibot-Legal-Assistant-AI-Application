import sqlite3
import faiss
import math
import time
from sentence_transformers import SentenceTransformer

db_path = 'data/faiss_index/metadata.db'
index_path = 'data/faiss_index/faiss.index'
batch_size = 512
dimension = 384

print('Loading embedding model...')
model = SentenceTransformer('all-MiniLM-L6-v2')

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

total_rows = conn.execute('SELECT COUNT(*) FROM chunks').fetchone()[0]
print(f'Total text chunks to process: {total_rows}')

# Create a brand new FAISS index
index = faiss.IndexFlatL2(dimension)

print('Starting AI Embedding logic (This is heavy math, please be patient!)...')
start_time = time.time()

cursor = conn.execute('SELECT row_id, excerpt FROM chunks ORDER BY row_id ASC')

batch_texts = []
current_batch = 0
total_added = 0

for row in cursor:
    batch_texts.append(row['excerpt'])
    if len(batch_texts) >= batch_size:
        start_batch_time = time.time()
        embs = model.encode(batch_texts, batch_size=128, show_progress_bar=False)
        index.add(embs)
        total_added += len(batch_texts)
        batch_texts = []
        current_batch += 1
        
        # Print progress EVERY SINGLE BATCH so you know it's working
        elapsed = time.time() - start_time
        rate = total_added / elapsed
        remain = (total_rows - total_added) / rate if rate > 0 else 0
        print(f'âœ… Processed {total_added}/{total_rows} text chunks... (Batch took {time.time()-start_batch_time:.1f}s) | Est time remaining: {remain/60:.1f} mins')

# finish remainder
if batch_texts:
    embs = model.encode(batch_texts, batch_size=128, show_progress_bar=False)
    index.add(embs)
    total_added += len(batch_texts)

print(f'Finished embedding! Total vectors: {index.ntotal}')
import os
import shutil
if os.path.exists(index_path):
    shutil.copy2(index_path, index_path + '.bak')
faiss.write_index(index, index_path)
print('Saved new index to disk!')
