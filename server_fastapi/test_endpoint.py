import urllib.request
import json
import time

def test():
    import sqlite3
    conn = sqlite3.connect("data/faiss_index/metadata.db")
    c = conn.cursor()
    c.execute("SELECT mock_id FROM chunks WHERE source_file LIKE 'administrator%' LIMIT 1")
    doc_id = c.fetchone()[0]

    print(f"Fetching document {doc_id} to test Structurer and LLM deduplication...")
    start = time.time()
    try:
        req = urllib.request.urlopen(f"http://localhost:5000/api/judgments/{doc_id}")
        data = json.loads(req.read())
        print(f"Finished in {time.time()-start:.2f}s")
        print("\n\n--- LLM STRUCTURED OUTPUT ---\n")
        print(data['content'][:2500])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test()