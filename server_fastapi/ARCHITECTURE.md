# LexiBot RAG Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                               │
│                     React.js Frontend (Port 5173)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Login   │  │   Chat   │  │  Cases   │  │Judgments │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ HTTP/REST + JWT Auth
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       API Gateway Layer                             │
│                    FastAPI (Python 3.10+)                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Routes: /auth, /cases, /judgments, /ai, /admin, /profile   │  │
│  │  Middleware: JWT Verification, CORS, Error Handling          │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────┬─────────────────────────────────┬───────────────────┘
                │                                 │
      ┌─────────▼─────────┐            ┌─────────▼─────────┐
      │  Business Logic   │            │   AI/RAG Pipeline │
      │     Layer         │            │       Layer       │
      └─────────┬─────────┘            └─────────┬─────────┘
                │                                 │
                ▼                                 ▼
┌───────────────────────────────┐  ┌──────────────────────────────────┐
│    Database Layer             │  │    AI Services Layer             │
│                               │  │                                  │
│  ┌─────────────────────────┐ │  │  ┌────────────────────────────┐ │
│  │      MongoDB            │ │  │  │  Embedding Service         │ │
│  │  ┌──────────────────┐  │ │  │  │  (Sentence Transformers)   │ │
│  │  │ Users Collection │  │ │  │  └────────────────────────────┘ │
│  │  ├──────────────────┤  │ │  │                                  │
│  │  │ Cases Collection │  │ │  │  ┌────────────────────────────┐ │
│  │  ├──────────────────┤  │ │  │  │  Vector Store (FAISS)      │ │
│  │  │Judgments Collect │  │ │  │  │  Index: IndexFlatL2        │ │
│  │  ├──────────────────┤  │ │  │  │  Dimension: 384            │ │
│  │  │Reminders Collect │  │ │  │  └────────────────────────────┘ │
│  │  ├──────────────────┤  │ │  │                                  │
│  │  │ChatLogs Collect  │  │ │  │  ┌────────────────────────────┐ │
│  │  └──────────────────┘  │ │  │  │  LLM Service (Groq API)    │ │
│  └─────────────────────────┘ │  │  │  Model: Llama 3.1 70B      │ │
│                               │  │  │  Speed: <1s response       │ │
└───────────────────────────────┘  │  └────────────────────────────┘ │
                                   │                                  │
                                   │  ┌────────────────────────────┐ │
                                   │  │  Document Processor        │ │
                                   │  │  PDF/DOCX extraction       │ │
                                   │  │  Text chunking             │ │
                                   │  └────────────────────────────┘ │
                                   └──────────────────────────────────┘
```

## RAG Pipeline Detailed Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER QUERY PROCESSING                           │
└─────────────────────────────────────────────────────────────────────┘

Step 1: User Input
┌──────────────────────────────────────┐
│ User types:                          │
│ "What are the grounds for divorce    │
│  in Pakistani law?"                  │
└────────────────┬─────────────────────┘
                 │
                 ▼
Step 2: Query Embedding
┌──────────────────────────────────────┐
│ Embedding Service                    │
│ ┌──────────────────────────────────┐ │
│ │ Input: Text query                │ │
│ │ Model: all-MiniLM-L6-v2         │ │
│ │ Output: 384-dim vector           │ │
│ │ [0.123, -0.456, 0.789, ...]     │ │
│ └──────────────────────────────────┘ │
└────────────────┬─────────────────────┘
                 │
                 ▼
Step 3: Vector Similarity Search
┌──────────────────────────────────────┐
│ FAISS Vector Store                   │
│ ┌──────────────────────────────────┐ │
│ │ Query vector                     │ │
│ │      vs                          │ │
│ │ 10,000+ judgment vectors         │ │
│ │                                  │ │
│ │ L2 Distance Calculation          │ │
│ │ Finds top-5 most similar         │ │
│ └──────────────────────────────────┘ │
└────────────────┬─────────────────────┘
                 │
                 ▼
Step 4: Document Retrieval
┌──────────────────────────────────────┐
│ Retrieved Documents (Top 5):        │
│                                      │
│ 1. "Khan vs Khan (Divorce 2023)"    │
│    Similarity: 0.92                  │
│    Content: "Grounds for divorce..." │
│                                      │
│ 2. "Ali vs Ali (Family 2022)"       │
│    Similarity: 0.89                  │
│    Content: "According to law..."    │
│                                      │
│ 3. "Ahmed vs Fatima (2024)"         │
│    Similarity: 0.87                  │
│    ...                               │
└────────────────┬─────────────────────┘
                 │
                 ▼
Step 5: Context Preparation
┌──────────────────────────────────────┐
│ Format for LLM:                      │
│                                      │
│ System Prompt: "You are a legal AI" │
│                                      │
│ Context:                             │
│ """                                  │
│ Document 1: [Case details...]        │
│ Document 2: [Case details...]        │
│ ...                                  │
│ """                                  │
│                                      │
│ User Question: "What are grounds..." │
└────────────────┬─────────────────────┘
                 │
                 ▼
Step 6: LLM Generation (Groq API)
┌──────────────────────────────────────┐
│ Groq LLM Service                     │
│ ┌──────────────────────────────────┐ │
│ │ Model: Llama 3.1 70B            │ │
│ │ Temperature: 0.3 (focused)      │ │
│ │ Max Tokens: 1024                │ │
│ │                                  │ │
│ │ Reads context documents          │ │
│ │ Generates grounded answer        │ │
│ │ Cites specific cases             │ │
│ └──────────────────────────────────┘ │
└────────────────┬─────────────────────┘
                 │
                 ▼
Step 7: Response
┌──────────────────────────────────────┐
│ Generated Answer:                    │
│                                      │
│ "According to Pakistani law, the    │
│  grounds for divorce include:       │
│                                      │
│  1. Khul (Case: Khan vs Khan 2023)  │
│     - Wife can seek divorce...      │
│                                      │
│  2. Talaq (Case: Ali vs Ali 2022)   │
│     - Husband's right...            │
│                                      │
│  [Detailed explanation with         │
│   citations from actual cases]"     │
│                                      │
│ Sources: 5 judgments                │
│ Confidence: 0.89                     │
└──────────────────────────────────────┘
```

## Document Ingestion Pipeline

```
┌────────────────────────────────────────────────────────────────┐
│                    JUDGMENT INGESTION FLOW                     │
└────────────────────────────────────────────────────────────────┘

Source 1: MongoDB                    Source 2: Files
┌──────────────────┐                ┌─────────────────┐
│  Judgments       │                │  PDF/DOCX/TXT   │
│  Collection      │                │  Files          │
└────────┬─────────┘                └────────┬────────┘
         │                                   │
         └──────────────┬────────────────────┘
                        │
                        ▼
         ┌──────────────────────────┐
         │  Document Processor      │
         │  ┌────────────────────┐  │
         │  │ Text Extraction    │  │
         │  │ (PDF/DOCX → text)  │  │
         │  └────────────────────┘  │
         │  ┌────────────────────┐  │
         │  │ Text Cleaning      │  │
         │  │ (normalize, strip) │  │
         │  └────────────────────┘  │
         │  ┌────────────────────┐  │
         │  │ Metadata Extract   │  │
         │  │ (parties, dates)   │  │
         │  └────────────────────┘  │
         │  ┌────────────────────┐  │
         │  │ Text Chunking      │  │
         │  │ (1000 chars/chunk) │  │
         │  │ (200 char overlap) │  │
         │  └────────────────────┘  │
         └──────────┬───────────────┘
                    │
                    ▼
         ┌──────────────────────────┐
         │  Chunks with Metadata    │
         │                          │
         │  Chunk 1:                │
         │  - content: "..."        │
         │  - title: "Case X"       │
         │  - case_type: "Civil"    │
         │  - chunk_index: 0        │
         │                          │
         │  Chunk 2: ...            │
         │  Chunk 3: ...            │
         └──────────┬───────────────┘
                    │
                    ▼
         ┌──────────────────────────┐
         │  Embedding Generation    │
         │  ┌────────────────────┐  │
         │  │ Batch Processing   │  │
         │  │ 32 chunks at a time│  │
         │  │                    │  │
         │  │ Each chunk → 384-  │  │
         │  │ dimensional vector │  │
         │  └────────────────────┘  │
         └──────────┬───────────────┘
                    │
                    ▼
         ┌──────────────────────────┐
         │  FAISS Index Storage     │
         │  ┌────────────────────┐  │
         │  │ faiss.index        │  │
         │  │ (vector index)     │  │
         │  └────────────────────┘  │
         │  ┌────────────────────┐  │
         │  │ metadata.pkl       │  │
         │  │ (document info)    │  │
         │  └────────────────────┘  │
         └──────────────────────────┘
                    │
                    ▼
         ┌──────────────────────────┐
         │  Ready for Search!       │
         │  ✅ Index built          │
         │  ✅ Saved to disk        │
         └──────────────────────────┘
```

## Technology Stack

### Backend Framework
- **FastAPI**: High-performance Python web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and settings

### Database
- **MongoDB**: Document database via Motor (async driver)
- **Collections**: users, cases, judgments, reminders, chatlogs

### AI/ML Stack
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **LLM**: Groq API (Llama 3.1 70B)
- **NLP**: LangChain, tiktoken

### Document Processing
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX parsing
- **Regex**: Metadata extraction

### Authentication
- **JWT**: JSON Web Tokens via python-jose
- **Password Hashing**: bcrypt via passlib

## Deployment Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Production Setup                      │
└────────────────────────────────────────────────────────────┘

Internet
   │
   ▼
┌──────────────┐
│   Nginx      │  ← Reverse proxy, SSL termination
│   (Port 80)  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   FastAPI    │  ← 4 worker processes
│   (Port 5000)│
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐   ┌─────────────┐
│   MongoDB    │   │  FAISS      │
│  (Port 27017)│   │  Index      │
│              │   │  (on disk)  │
└──────────────┘   └─────────────┘
       │
       ▼
┌──────────────┐
│   Groq API   │  ← External service
│   (HTTPS)    │
└──────────────┘
```

## Security Architecture

```
┌────────────────────────────────────────┐
│         Security Layers                │
└────────────────────────────────────────┘

Layer 1: Transport Security
┌────────────────────────────────────┐
│  HTTPS (TLS/SSL)                   │
│  - Encrypts all traffic            │
│  - Prevents MITM attacks           │
└────────────────────────────────────┘

Layer 2: Authentication
┌────────────────────────────────────┐
│  JWT Tokens                        │
│  - Stateless authentication        │
│  - Token expiry: 24 hours          │
│  - Signature verification          │
└────────────────────────────────────┘

Layer 3: Authorization
┌────────────────────────────────────┐
│  Role-Based Access Control (RBAC) │
│  - Admin: Full access              │
│  - Advocate: CRUD on own resources │
│  - Client: Read-only               │
└────────────────────────────────────┘

Layer 4: Data Protection
┌────────────────────────────────────┐
│  - Password hashing (bcrypt)       │
│  - Sensitive data encryption       │
│  - API key protection              │
│  - Input validation (Pydantic)     │
└────────────────────────────────────┘

Layer 5: Rate Limiting
┌────────────────────────────────────┐
│  - Groq: 30 req/min (free tier)    │
│  - API endpoint throttling         │
│  - DDoS protection (Nginx)         │
└────────────────────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
- Multiple FastAPI instances behind load balancer
- Stateless design (JWT tokens)
- MongoDB replica sets

### Caching Strategy
- Redis for session caching (future)
- LLM response caching (future)
- Pre-computed embeddings (current)

### Performance Optimization
- Async I/O throughout
- Batch embedding generation
- FAISS index in memory
- Connection pooling (MongoDB)

## Monitoring & Logging

```
Application Logs
  │
  ├─ INFO: Request/Response logging
  ├─ WARNING: API rate limits
  ├─ ERROR: Exception tracking
  └─ DEBUG: RAG pipeline steps

Performance Metrics
  │
  ├─ Response times
  ├─ Embedding generation time
  ├─ FAISS search latency
  └─ LLM generation time

Health Checks
  │
  ├─ /health (basic)
  ├─ /api/ai/health (AI services)
  └─ MongoDB connectivity
```

---

This architecture provides:
- ✅ **Scalability**: Handle 1000s of users
- ✅ **Performance**: Sub-second response times
- ✅ **Reliability**: Fault tolerance and error handling
- ✅ **Security**: Multi-layer protection
- ✅ **Maintainability**: Clean separation of concerns
