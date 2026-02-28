# LexiBot RAG Pipeline - Setup & Usage Guide

## 🎯 Overview

This document explains the complete RAG (Retrieval-Augmented Generation) implementation for LexiBot legal assistant.

## 📁 Project Structure

```
server_fastapi/
├── services/              # AI/ML Services
│   ├── embeddings.py     # Sentence transformer embeddings
│   ├── vector_store.py   # FAISS vector database
│   ├── llm_service.py    # Groq LLM integration
│   └── rag_pipeline.py   # Complete RAG orchestration
├── utils/
│   └── document_processor.py  # Text extraction & chunking
├── routes/
│   └── ai.py             # RAG-powered API endpoints
├── scripts/
│   ├── ingest_judgments.py   # Index judgments
│   └── seed_judgments.py     # Add sample data
├── data/
│   ├── faiss_index/      # FAISS index storage
│   └── raw_documents/    # PDF/DOCX files (optional)
└── config/
    └── settings.py       # Configuration with AI settings
```

## 🚀 Quick Start

### Step 1: Get Groq API Key (FREE)

1. Visit: https://console.groq.com
2. Sign up (free account)
3. Go to API Keys section
4. Create new API key
5. Copy the key

### Step 2: Configure Environment

Add to your `.env` file:

```bash
# Required - Add your Groq API key
GROQ_API_KEY=gsk_your_actual_api_key_here

# Optional - AI Configuration (defaults shown)
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=llama-3.1-70b-versatile
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RETRIEVAL=5
```

### Step 3: Install Dependencies

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install AI/ML packages
pip install -r requirements.txt
```

### Step 4: Ingest Judgments

```bash
# From MongoDB (if you have judgments in DB)
python scripts/ingest_judgments.py --source database

# From PDF/DOCX files
# 1. Place files in data/raw_documents/
# 2. Run:
python scripts/ingest_judgments.py --source files
```

### Step 5: Start Server

```bash
python main.py
```

## 📊 How RAG Works

### The Complete Flow

```
User Question
     ↓
[1] Convert to Embedding (Sentence Transformer)
     ↓
[2] Search FAISS Index (Find Similar Judgments)
     ↓
[3] Retrieve Top-5 Most Relevant Documents
     ↓
[4] Send Documents + Question to LLM (Groq)
     ↓
[5] LLM Reads Documents & Generates Answer
     ↓
Response to User
```

### Example Walkthrough

**User asks:** "What are the grounds for divorce in Pakistan?"

1. **Embedding**: Question converted to 384-dimensional vector
2. **FAISS Search**: Finds 5 most similar divorce case judgments
3. **Context**: Retrieved cases are formatted
4. **LLM Prompt**: 
   ```
   Context: [5 divorce case judgments]
   Question: What are grounds for divorce?
   Answer based ONLY on provided cases.
   ```
5. **Answer**: LLM generates response citing specific cases

## 🔧 API Endpoints

### 1. Chat (RAG-Powered)

```http
POST /api/ai/chat
Authorization: Bearer <token>

{
  "message": "What are the grounds for divorce?",
  "caseId": "optional_case_id",
  "sessionId": "optional_session_id"
}

Response:
{
  "response": "Based on relevant cases...",
  "sessionId": "abc-123",
  "chatLogId": "log_id"
}
```

### 2. Semantic Search

```http
POST /api/ai/search
Authorization: Bearer <token>

{
  "query": "contract breach cases",
  "filters": { "caseType": "Civil" },
  "limit": 10
}

Response:
{
  "results": [
    {
      "id": "judgment_id",
      "title": "Case Title",
      "similarity": 0.89,
      "excerpt": "..."
    }
  ],
  "total": 10
}
```

### 3. Summarize Judgment

```http
POST /api/ai/summarize
Authorization: Bearer <token>

{
  "judgmentId": "123abc",
  "judgmentText": "optional full text"
}

Response:
{
  "summary": "Generated summary...",
  "judgmentId": "123abc"
}
```

### 4. Outcome Prediction

```http
POST /api/ai/predict
Authorization: Bearer <token>

{
  "caseDescription": "Description of the case...",
  "caseType": "Civil"
}

Response:
{
  "prediction": "Favorable",
  "confidence": 0.75,
  "explanation": "Based on similar cases...",
  "similarCases": [...]
}
```

### 5. Client Guidance

```http
POST /api/ai/guidance
Authorization: Bearer <token>

{
  "caseType": "Divorce",
  "situationDescription": "My situation..."
}

Response:
{
  "guidance": "Step-by-step guidance...",
  "caseType": "Divorce",
  "similarCases": [...]
}
```

### 6. Health Check

```http
GET /api/ai/health

Response:
{
  "status": "healthy",
  "services": {
    "vector_store": { "status": "operational", "documents": 150 },
    "embedding_service": { "status": "operational" },
    "llm_service": { "status": "operational" }
  }
}
```

## 🧪 Testing the Pipeline

### 1. Test Without API Key (Fallback Mode)

```bash
# Don't set GROQ_API_KEY
python main.py

# Visit http://localhost:5000/api/ai/health
# Should show status with fallback messages
```

### 2. Test Ingestion

```bash
# Clear and rebuild index
python scripts/ingest_judgments.py --clear --source database

# Check logs for:
# ✅ Loaded embedding model
# ✅ Generated X embeddings
# ✅ Added X documents to index
# ✅ Saved index
```

### 3. Test Search (Python)

```python
from services.rag_pipeline import get_rag_pipeline

rag = get_rag_pipeline()

# Search
results = rag.search_judgments("divorce grounds", top_k=5)
print(f"Found {len(results)} judgments")

# Query
answer = rag.query("What are grounds for divorce?")
print(answer['answer'])
print(f"Confidence: {answer['confidence']}")
```

### 4. Test via Swagger UI

1. Start server: `python main.py`
2. Visit: http://localhost:5000/docs
3. Authorize with JWT token
4. Try `/api/ai/chat` endpoint

## 🔍 Understanding Key Components

### Embeddings (services/embeddings.py)

- **Model**: all-MiniLM-L6-v2
- **Size**: 80MB (lightweight)
- **Speed**: Very fast
- **Dimensions**: 384
- **Purpose**: Convert text to vectors for similarity search

### Vector Store (services/vector_store.py)

- **Technology**: FAISS IndexFlatL2
- **Search**: Exact L2 distance
- **Storage**: Persistent (saved to disk)
- **Features**: Metadata storage, incremental updates

### LLM Service (services/llm_service.py)

- **Provider**: Groq (free tier)
- **Model**: Llama 3.1 70B
- **Speed**: 10-20x faster than OpenAI
- **Features**: Context-aware generation, summarization, extraction

### RAG Pipeline (services/rag_pipeline.py)

- **Orchestration**: Complete RAG workflow
- **Methods**: query(), search(), summarize(), predict(), guidance()
- **Features**: Confidence scoring, source citation, filtering

## 📝 Adding Your Own Judgments

### Option 1: MongoDB

```python
# Add judgment to database
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def add_judgment():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.lexibot_db
    
    judgment = {
        "title": "Smith vs Jones",
        "content": "Full judgment text here...",
        "caseType": "Civil",
        "court": "High Court",
        "date": "2024-01-15",
        "parties": "Smith vs Jones",
        "outcome": "Plaintiff won",
        "citation": "2024 HC 123"
    }
    
    await db.judgments.insert_one(judgment)
    print("✅ Judgment added")

asyncio.run(add_judgment())

# Then run ingestion
# python scripts/ingest_judgments.py --source database
```

### Option 2: PDF Files

```bash
# 1. Create directory
mkdir -p data/raw_documents

# 2. Copy PDF files
cp ~/Downloads/judgment1.pdf data/raw_documents/
cp ~/Downloads/judgment2.pdf data/raw_documents/

# 3. Run ingestion
python scripts/ingest_judgments.py --source files
```

## 🐛 Troubleshooting

### Issue: "Groq API key not configured"

**Solution**: Add `GROQ_API_KEY=gsk_xxx` to `.env` file

### Issue: "No judgments found in database"

**Solution**: 
```bash
# Add sample judgments
python scripts/seed_judgments.py

# Then ingest
python scripts/ingest_judgments.py --source database
```

### Issue: "Vector store is empty"

**Solution**: Run ingestion script
```bash
python scripts/ingest_judgments.py --source database --clear
```

### Issue: "ModuleNotFoundError: No module named 'sentence_transformers'"

**Solution**: 
```bash
pip install -r requirements.txt
```

### Issue: Slow embedding generation

**Explanation**: First run downloads model (~80MB). Subsequent runs are fast.

### Issue: Low confidence scores

**Causes**:
- Not enough judgments indexed
- Query doesn't match document content
- Need better quality judgments

**Solutions**:
- Add more judgments
- Rephrase query
- Improve judgment content quality

## 📊 Performance Tips

### 1. Batch Ingestion

```bash
# Instead of ingesting one at a time
# Add many judgments to DB, then ingest all at once
python scripts/ingest_judgments.py --source database
```

### 2. GPU Acceleration (Optional)

```bash
# If you have NVIDIA GPU
pip uninstall faiss-cpu
pip install faiss-gpu

# Embeddings will be 10x faster
```

### 3. Caching

- Embedding model is cached after first load
- FAISS index is loaded once at startup
- LLM responses can be cached (implement in future)

## 🎓 For Your Supervisor/Demo

### Key Points to Highlight

1. **RAG Implementation**: Not just LLM, but retrieval-augmented
2. **Vector Search**: Semantic similarity, not keyword matching
3. **Grounded Responses**: Answers based on actual cases, not hallucinated
4. **Scalable**: Can handle thousands of judgments
5. **Fast**: Groq provides fastest LLM inference
6. **Cost**: Completely free (Groq free tier)

### Demo Flow

1. Show health endpoint - all services operational
2. Add a test judgment
3. Run ingestion - show progress
4. Ask legal question in chat
5. Show retrieved sources + generated answer
6. Highlight citations from actual cases

### Metrics to Report

- Number of judgments indexed: `curl localhost:5000/api/ai/stats`
- Embedding dimension: 384
- Average query time: <2 seconds
- Confidence scores: 0.0 - 1.0

## 🔮 Future Enhancements

1. **Fine-tuning**: Train custom model on Pakistani law
2. **Hybrid Search**: Combine vector + keyword search
3. **Reranking**: Add cross-encoder for better ranking
4. **Streaming**: Stream LLM responses token-by-token
5. **Feedback Loop**: Learn from user feedback
6. **Multi-lingual**: Support Urdu language
7. **Citation Extraction**: Auto-extract case citations
8. **Legal Graphs**: Connect related cases

## 📚 Additional Resources

- **Groq Console**: https://console.groq.com
- **FAISS Documentation**: https://github.com/facebookresearch/faiss
- **Sentence Transformers**: https://www.sbert.net
- **LangChain Docs**: https://python.langchain.com

## 🆘 Support

If you encounter issues:

1. Check logs for detailed error messages
2. Verify `.env` configuration
3. Ensure MongoDB is running
4. Check FAISS index exists: `ls data/faiss_index/`
5. Test Groq API key: Visit console.groq.com

---

**Good luck with your FYP presentation! 🎓✨**
