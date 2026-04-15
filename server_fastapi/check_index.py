import pickle, os, sys

path = 'data/faiss_index/metadata.pkl'
if not os.path.exists(path):
    print("ERROR: metadata.pkl not found!")
    sys.exit(1)

size_mb = os.path.getsize(path) / (1024*1024)
print(f"File size: {size_mb:.1f} MB")

with open(path, 'rb') as f:
    meta = pickle.load(f)

print(f"Total chunks in metadata: {len(meta)}")

if meta:
    sample = meta[0]
    print(f"Sample keys: {list(sample.keys())}")
    print(f"Sample title: {sample.get('title', 'N/A')}")
    print(f"Sample court: {sample.get('court', 'N/A')}")
    print(f"Sample source_file: {sample.get('source_file', 'N/A')}")
    print(f"Sample year: {sample.get('year', 'N/A')}")
    
    # Count unique titles
    titles = set(c.get('title','') for c in meta)
    print(f"\nUnique document titles: {len(titles)}")
    print("First 5 titles:")
    for t in list(titles)[:5]:
        print(f"  - {t}")
