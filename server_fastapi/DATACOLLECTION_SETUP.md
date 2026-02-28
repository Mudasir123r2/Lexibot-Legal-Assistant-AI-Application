# Datacollection Folder Setup Guide

## Overview
This guide explains how to ingest judgments and laws from your existing `Datacollectiom` folder into the RAG system.

## Folder Structure
```
Datacollectiom/
├── divorce/          # Divorce-related judgments (60+ PDFs)
├── bail/             # Bail cases
├── Criminal Appeal/  # Criminal appeal judgments
├── custody/          # Custody cases
├── Family/           # Family law cases
└── Laws/             # Pakistani legal codes (CPC, CrPC, PPC, etc.)
```

## Ingestion Process

### Step 1: Verify Your Data
Check that the folder exists and contains PDF files:
```bash
# Check folder structure
ls "D:\fyp\lexibot-judgment\Datacollectiom"

# Count PDF files
ls "D:\fyp\lexibot-judgment\Datacollectiom" -Recurse -Filter "*.pdf" | Measure-Object
```

### Step 2: Run Ingestion with Recursive Option
The ingestion script now supports recursive processing of subdirectories:

```bash
# Navigate to server directory
cd D:\fyp\lexibot-judgment\server_fastapi

# Clear existing index and ingest all judgments (recommended for first run)
python scripts/ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom" --recursive --clear

# Without clearing (adds to existing index)
python scripts/ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom" --recursive
```

### Step 3: Monitor Progress
The script will:
1. ✅ Recursively scan all subdirectories
2. ✅ Process each PDF file
3. ✅ Extract category from folder name (divorce, bail, Criminal Appeal, etc.)
4. ✅ Generate embeddings for text chunks
5. ✅ Store in FAISS vector index
6. ✅ Save index to disk

Expected output:
```
INFO - Found 200+ files to process
INFO - Processing [1/200]: 2012_LHC_1234.pdf
INFO -   Category: divorce
INFO - Processing [2/200]: Bail_Application_567.pdf
INFO -   Category: bail
...
INFO - ✅ Ingestion complete! Processed 200+ files into 5000+ chunks
```

### Step 4: Verify Ingestion
```bash
# Check vector store stats
python scripts/ingest_judgments.py --help

# Start server and test search
uvicorn app:app --reload
```

Then test via API:
```bash
# Search for divorce-related judgments
curl -X POST http://localhost:8000/ai/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "divorce cases involving child custody",
    "limit": 5
  }'
```

## Category Mapping
Each judgment is automatically tagged with its category based on the subfolder:

| Folder Name | Category Tag | Description |
|------------|--------------|-------------|
| divorce | `divorce` | Divorce-related cases |
| bail | `bail` | Bail applications and orders |
| Criminal Appeal | `Criminal Appeal` | Criminal appeal judgments |
| custody | `custody` | Child custody cases |
| Family | `Family` | Family law matters |
| Laws | `Laws` | Legal codes and statutes |

## Processing Details

### What Gets Processed
- ✅ **PDF files**: Extracted using PyPDF2
- ✅ **DOCX files**: Extracted using python-docx (if any)
- ✅ **TXT files**: Plain text (if any)

### Chunking Strategy
- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Purpose**: Maintains context across boundaries

### Metadata Extracted
For each chunk:
```json
{
  "source_file": "2012_LHC_1234.pdf",
  "title": "2012_LHC_1234",
  "category": "divorce",
  "chunk_index": 0,
  "total_chunks": 15
}
```

## Troubleshooting

### Issue: "Directory not found"
**Solution**: Check the path spelling. Note: Your folder is named `Datacollectiom` (with typo).
```bash
# Verify exact folder name
ls "D:\fyp\lexibot-judgment" | Select-String -Pattern "Data"
```

### Issue: "No documents found"
**Solution**: Verify PDF files exist:
```bash
ls "D:\fyp\lexibot-judgment\Datacollectiom\divorce" -Filter "*.pdf"
```

### Issue: "PDF extraction failed"
**Solution**: 
- Some PDFs may be scanned images (no extractable text)
- Check PDF file integrity
- View error details in logs

### Issue: "Memory error during embedding generation"
**Solution**: Process in smaller batches by temporarily moving files:
```bash
# Process divorce cases first
python scripts/ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\divorce" --clear

# Then add other categories
python scripts/ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\bail"
```

## Performance Expectations

### Processing Time
- **Small folder** (10 PDFs): ~30 seconds
- **Medium folder** (50 PDFs): ~2-3 minutes
- **Large folder** (200+ PDFs): ~10-15 minutes

Factors affecting speed:
- PDF size and page count
- Number of text chunks generated
- CPU performance for embedding generation

### Storage Requirements
- **Embeddings**: ~1.5 KB per chunk (384 dimensions × 4 bytes)
- **FAISS Index**: Scales linearly with document count
- **Estimated**: 200 PDFs → ~5000 chunks → ~7.5 MB index

## Advanced Usage

### Process Specific Categories
```bash
# Only divorce cases
python scripts/ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\divorce"

# Only legal codes
python scripts/ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\Laws"
```

### Update Existing Index
```bash
# Add new PDFs without clearing existing data
python scripts/ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\new_cases" --recursive
```

### Clear and Rebuild Index
```bash
# Complete rebuild (use when structure changes)
python scripts/ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom" --recursive --clear
```

## Next Steps

1. ✅ Ingest your judgments using the commands above
2. ✅ Test search functionality via API
3. ✅ Integrate with frontend chat interface
4. ✅ Monitor Cerebras API usage and rate limits

## Integration with Cerebras

Your RAG system now uses:
- **LLM**: Llama-3.3-70b via Cerebras API
- **Max Context**: 65,536 tokens
- **Rate Limits**: 30 req/min, 900 req/hour
- **Embeddings**: Sentence Transformers (local, no API calls)
- **Vector Store**: FAISS (local, persistent)

The ingestion process is independent of the LLM provider. Embeddings are generated locally, so there's no API cost for indexing documents.

## Questions?

See also:
- [QUICK_START.md](QUICK_START.md) - Complete setup guide
- [RAG_IMPLEMENTATION_GUIDE.md](RAG_IMPLEMENTATION_GUIDE.md) - Technical details
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
