# 🚀 LexiBot RAG Quick Start Guide

## What You Just Got

I've implemented a complete **RAG (Retrieval-Augmented Generation)** pipeline for your LexiBot project! Here's what's been added:

### ✅ What's Implemented

1. **Embedding Service** - Converts text to vectors for similarity search
2. **Vector Store (FAISS)** - Fast semantic search over legal judgments
3. **LLM Service (Groq)** - FREE, fast AI for generating responses
4. **RAG Pipeline** - Complete orchestration: retrieve → generate
5. **Document Processing** - Extracts text from PDF/DOCX, chunks intelligently
6. **AI Routes** - Chat, search, summarize, predict, guidance endpoints
7. **Ingestion Script** - Process judgments into searchable index

## 🎯 How It Works (Simple Explanation)

**Without RAG** (what you had):
- User asks: "What are grounds for divorce?"
- LLM makes up answer (could be wrong/hallucinated)

**With RAG** (what you have now):
- User asks: "What are grounds for divorce?"
- System finds 5 relevant divorce judgments from your database
- LLM reads those judgments and answers based on them
- Response is **grounded in actual Pakistani cases!**

## 📋 Steps to Get It Running

### Step 1: Get FREE Groq API Key (2 minutes)

1. Go to https://console.groq.com
2. Sign up with email (completely free)
3. Click "API Keys" → "Create API Key"
4. Copy the key (starts with `gsk_...`)

### Step 2: Add API Key to .env

Open `server_fastapi/.env` and replace:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

With your actual key:

```bash
GROQ_API_KEY=gsk_abc123xyz...
```

### Step 3: Start the Server

```bash
cd server_fastapi
.\venv\Scripts\activate
python main.py
```

You should see:
```
✅ Embedding model loaded successfully
✅ MongoDB connected successfully
INFO: Uvicorn running on http://0.0.0.0:5000
```

### Step 4: Ingest Your Judgments

In a new terminal:

```bash
cd server_fastapi
.\venv\Scripts\activate

# This processes judgments from MongoDB and creates vector index
python scripts/ingest_judgments.py --source database
```

Expected output:
```
✅ Connected to MongoDB
Found X judgments to process
Processing [1/X]: Case Title...
Generating embeddings...
✅ INGESTION COMPLETED SUCCESSFULLY
```

### Step 5: Test It!

#### Option A: Swagger UI (Easiest)

1. Open browser: http://localhost:5000/docs
2. Click "Authorize" → Enter your JWT token
3. Try `/api/ai/chat`:
   ```json
   {
     "message": "What are the grounds for divorce in Pakistan?",
     "caseId": null,
     "sessionId": null
   }
   ```
4. See AI response based on your judgments!

#### Option B: Test in Frontend

Your React frontend should work as-is! The API endpoints are compatible.

#### Option C: Python Test

```python
# Create a test file: test_rag.py
from services.rag_pipeline import get_rag_pipeline

rag = get_rag_pipeline()

# Search
results = rag.search_judgments("divorce", top_k=5)
print(f"Found {len(results)} judgments")

# Ask question
answer = rag.query("What are grounds for divorce?")
print(answer['answer'])
print(f"Sources: {len(answer['sources'])}")
```

Run it:
```bash
python test_rag.py
```

## 📊 What Each File Does

```
server_fastapi/
├── services/
│   ├── embeddings.py       → Converts text to 384-dim vectors
│   ├── vector_store.py     → FAISS index for fast search
│   ├── llm_service.py      → Groq API integration
│   └── rag_pipeline.py     → Orchestrates everything
│
├── utils/
│   └── document_processor.py → Extracts text, chunks documents
│
├── routes/
│   └── ai.py               → 6 new endpoints (chat, search, etc.)
│
├── scripts/
│   ├── ingest_judgments.py → Process judgments into FAISS
│   └── seed_judgments.py   → Add sample judgments
│
└── data/
    ├── faiss_index/        → Vector index (auto-created)
    └── raw_documents/      → Place PDF files here (optional)
```

## 🎨 API Endpoints You Can Use

### 1. Chat with AI
```http
POST /api/ai/chat
{
  "message": "Explain breach of contract"
}
```

### 2. Search Judgments
```http
POST /api/ai/search
{
  "query": "divorce custody",
  "limit": 10
}
```

### 3. Summarize Judgment
```http
POST /api/ai/summarize
{
  "judgmentId": "123abc"
}
```

### 4. Predict Outcome
```http
POST /api/ai/predict
{
  "caseDescription": "...",
  "caseType": "Civil"
}
```

### 5. Get Guidance
```http
POST /api/ai/guidance
{
  "caseType": "Divorce",
  "situationDescription": "..."
}
```

### 6. Health Check
```http
GET /api/ai/health
```

## 🐛 Troubleshooting

### "No judgments found in database"

**Solution**: Add sample judgments first:
```bash
python scripts/seed_judgments.py
python scripts/ingest_judgments.py --source database
```

### "Groq API key not configured"

**Solution**: Make sure `.env` has your actual API key, then restart server.

### "Vector store is empty"

**Solution**: Run ingestion:
```bash
python scripts/ingest_judgments.py --source database --clear
```

### Ingestion takes long time

**Normal**: First run downloads embedding model (~80MB). Subsequent runs are fast.

### Low quality responses

**Causes**:
- Not enough judgments indexed
- Groq API key not working
- Judgments don't have good content

**Solutions**:
- Add more judgments with detailed content
- Check API key at https://console.groq.com
- Verify ingestion completed successfully

## 📚 Understanding the Flow

```
┌─────────────────────────────────────────────────────┐
│  1. User Question                                   │
│  "What are the grounds for divorce in Pakistan?"   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  2. Embedding Service                               │
│  Converts question to 384-dimensional vector        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  3. FAISS Vector Store                              │
│  Searches 1000s of judgments in milliseconds        │
│  Returns top-5 most similar cases                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  4. Context Preparation                             │
│  Formats retrieved judgments as context             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  5. LLM Service (Groq)                              │
│  Reads context + question                           │
│  Generates answer based on retrieved cases          │
│  Model: Llama 3.1 70B (very smart!)                │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  6. Response with Citations                         │
│  "According to Case No. 123/2024..."                │
│  + Source documents                                 │
│  + Confidence score                                 │
└─────────────────────────────────────────────────────┘
```

## 🎓 For Your Supervisor Demo

### Key Points to Mention

1. **Not just an LLM** - It's a complete RAG system
2. **Grounded responses** - Answers based on actual judgments, not hallucinated
3. **Vector search** - Semantic similarity, finds relevant cases even with different wording
4. **Fast & Free** - Groq provides fastest inference, completely free
5. **Scalable** - Can handle thousands of judgments
6. **Production-ready** - Proper error handling, logging, API documentation

### Demo Flow

1. **Show Architecture**: Explain RAG flow diagram
2. **Show Data**: Display judgments in MongoDB
3. **Run Ingestion**: Show terminal output of processing
4. **Show Index**: Check `data/faiss_index/` directory
5. **Test Search**: Ask question in Swagger UI
6. **Show Response**: Point out citations from actual cases
7. **Show Stats**: Call `/api/ai/stats` endpoint

### Metrics to Report

```bash
# Get statistics
curl http://localhost:5000/api/ai/stats

# You'll see:
# - Total judgments indexed
# - Embedding dimension: 384
# - LLM model: llama-3.1-70b-versatile
```

## 🔮 Next Steps (Optional Enhancements)

1. **Add More Judgments** - More data = better answers
2. **Fine-tune Model** - Train on Pakistani legal language
3. **Add Feedback** - Let users rate responses
4. **Streaming** - Show response word-by-word
5. **Multi-lingual** - Add Urdu support
6. **Legal Graphs** - Connect related cases

## 📞 Need Help?

Read the detailed guide: `RAG_IMPLEMENTATION_GUIDE.md`

**Common Questions:**

Q: Do I need to train a model?
A: **NO!** We use pre-trained models (embeddings + LLM).

Q: Is Groq really free?
A: **YES!** 30 requests/minute, perfect for FYP.

Q: How many judgments do I need?
A: Minimum 10-20 for demo. More is better.

Q: Can I use OpenAI instead?
A: Yes, but it costs money. Groq is free and faster!

Q: What if I don't have PDF files?
A: Use judgments from MongoDB. The script handles both.

---

## ✅ Checklist

- [ ] Got Groq API key from console.groq.com
- [ ] Added API key to `.env` file
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Started server (`python main.py`)
- [ ] Ran ingestion (`python scripts/ingest_judgments.py`)
- [ ] Tested in Swagger UI (http://localhost:5000/docs)
- [ ] Verified responses use actual case data

---

**You're all set! Your LexiBot now has a production-ready RAG pipeline! 🎉**

For detailed documentation, see: `RAG_IMPLEMENTATION_GUIDE.md`
