# LexiBot Backend - FastAPI with RAG Pipeline

This is the FastAPI backend for the LexiBot legal research and case management system, featuring a complete **RAG (Retrieval-Augmented Generation)** pipeline for intelligent legal assistance.

## 🌟 Key Features

- **RAG Pipeline**: Retrieval-Augmented Generation for accurate, grounded legal answers
- **Vector Search**: Semantic search using FAISS for finding relevant judgments
- **LLM Integration**: Groq API (FREE) for fast, intelligent response generation
- **Document Processing**: Extract and process legal documents (PDF, DOCX, TXT)
- **Complete API**: Authentication, case management, judgments, reminders, and AI endpoints

## 📋 Requirements

- Python 3.10+
- MongoDB 4.4+
- ~500MB free disk space for AI models
- Internet connection (for Groq API)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install all packages (including AI/ML dependencies)
pip install -r requirements.txt
```

### 2. Get Groq API Key (FREE)

1. Visit https://console.groq.com
2. Sign up (free account)
3. Create API key

### 3. Configure Environment

Edit `.env` file and add your Groq API key:

```bash
GROQ_API_KEY=gsk_your_actual_key_here
```

### 4. Start the Server

```bash
python main.py
```

Server will be available at: http://localhost:5000

### 5. Ingest Judgments (Create Vector Index)

```bash
# In a new terminal
.\venv\Scripts\activate

# Process judgments from MongoDB
python scripts/ingest_judgments.py --source database
```

### 6. Test the RAG System

Visit http://localhost:5000/docs and try the `/api/ai/chat` endpoint!

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Step-by-step getting started guide
- **[RAG_IMPLEMENTATION_GUIDE.md](RAG_IMPLEMENTATION_GUIDE.md)** - Complete RAG pipeline documentation
- **[API Documentation](http://localhost:5000/docs)** - Interactive Swagger UI

## 🏗️ Project Structure

```
server_fastapi/
├── main.py              # FastAPI application entry point
├── config/              # Configuration and database
│   ├── database.py
│   └── settings.py
├── models/              # Pydantic models
├── routes/              # API endpoints
│   ├── auth.py
│   ├── ai.py           # ✨ RAG-powered AI endpoints
│   └── ...
├── services/            # ✨ AI/ML Services
│   ├── embeddings.py    # Text to vector conversion
│   ├── vector_store.py  # FAISS index management
│   ├── llm_service.py   # Groq LLM integration
│   └── rag_pipeline.py  # Complete RAG orchestration
├── utils/
│   ├── document_processor.py  # ✨ PDF/DOCX processing
│   └── ...
├── scripts/
│   ├── ingest_judgments.py    # ✨ Index builder
│   ├── create_admin.py
│   └── seed_judgments.py
└── data/
    ├── faiss_index/     # ✨ Vector index storage
    └── raw_documents/   # Place PDF files here
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
MONGO_URI=mongodb://localhost:27017/lexibot_db

# Authentication
JWT_SECRET=your_jwt_secret_here
JWT_ALGORITHM=HS256

# AI/ML (NEW)
GROQ_API_KEY=gsk_your_key_here
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=llama-3.1-70b-versatile

# Email (for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASS=your_password

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure_password
ADMIN_NAME=Admin User
```

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password
- `GET /api/auth/verify-email` - Verify email

### AI & RAG (NEW) ✨
- `POST /api/ai/chat` - RAG-powered chat
- `POST /api/ai/search` - Semantic judgment search
- `POST /api/ai/summarize` - Summarize judgment
- `POST /api/ai/predict` - Predict case outcome
- `POST /api/ai/guidance` - Get client guidance
- `GET /api/ai/health` - Check AI services status
- `GET /api/ai/stats` - Get pipeline statistics

### Cases
- `GET /api/cases` - List user's cases
- `POST /api/cases` - Create new case
- `GET /api/cases/{id}` - Get case details
- `PUT /api/cases/{id}` - Update case
- `DELETE /api/cases/{id}` - Delete case

### Judgments
- `GET /api/judgments` - List judgments (paginated, filtered)
- `GET /api/judgments/{id}` - Get judgment details
- `POST /api/judgments` - Create judgment (admin only)
- `PUT /api/judgments/{id}` - Update judgment (admin only)
- `DELETE /api/judgments/{id}` - Delete judgment (admin only)

### Reminders
- `GET /api/reminders` - List user's reminders
- `POST /api/reminders` - Create reminder
- `PUT /api/reminders/{id}` - Update reminder
- `DELETE /api/reminders/{id}` - Delete reminder

### Admin
- `GET /api/admin/users` - List all users
- `PUT /api/admin/users/{id}` - Update user
- `DELETE /api/admin/users/{id}` - Delete user
- `GET /api/admin/stats` - System statistics

## 💡 Understanding RAG

### What is RAG?

RAG = **Retrieval-Augmented Generation**

**Traditional LLM** (what most chatbots do):
```
User: "What are grounds for divorce?"
LLM: [Makes up answer from training data]
```

**LexiBot with RAG** (what we do):
```
User: "What are grounds for divorce?"
System: 
  1. Search 1000s of judgments
  2. Find 5 most relevant divorce cases
  3. LLM reads those cases
  4. Generates answer citing actual cases
```

### Benefits

✅ **Accurate** - Answers based on real judgments  
✅ **Citable** - References specific cases  
✅ **Up-to-date** - Add new judgments anytime  
✅ **Trustworthy** - Not hallucinated  
✅ **Fast** - Groq provides fastest LLM inference  

## 📊 RAG Pipeline Flow

```
User Question
     ↓
Convert to Embedding (384-dim vector)
     ↓
Search FAISS Index (milliseconds)
     ↓
Retrieve Top-5 Similar Judgments
     ↓
Send to LLM with Context
     ↓
Generate Grounded Answer
     ↓
Response with Citations
```

## 🗄️ Database Setup

### Create Admin User

```bash
python scripts/create_admin.py
```

This will create an admin user using the credentials from your `.env` file:
- ADMIN_EMAIL
- ADMIN_PASSWORD
- ADMIN_NAME

### Seed Sample Judgments

```bash
python scripts/seed_judgments.py
```

This will populate the database with sample legal judgments for testing.

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## API Endpoints

### Authentication
- POST `/api/auth/register` - Register new user
- POST `/api/auth/login` - Login user
- POST `/api/auth/forgot-password` - Request password reset
- POST `/api/auth/reset-password` - Reset password with token
- GET `/api/auth/verify-email` - Verify email address

### Profile
- GET `/api/profile` - Get user profile
- PUT `/api/profile` - Update user profile

### Cases
- GET `/api/cases` - Get all user cases
- GET `/api/cases/{id}` - Get specific case
- POST `/api/cases` - Create new case
- PUT `/api/cases/{id}` - Update case
- DELETE `/api/cases/{id}` - Delete case

### Judgments
- GET `/api/judgments/search` - Search judgments
- GET `/api/judgments/{id}` - Get specific judgment
- POST `/api/judgments` - Create new judgment

### AI
- POST `/api/ai/chat` - AI chat (mock responses)
- POST `/api/ai/summarize` - Summarize judgment
- POST `/api/ai/extract-details` - Extract key details
- POST `/api/ai/predict-outcome` - Predict case outcome

### Reminders
- GET `/api/reminders` - Get all reminders
- POST `/api/reminders` - Create reminder
- PUT `/api/reminders/{id}` - Update reminder
- PATCH `/api/reminders/{id}/complete` - Mark as complete
- DELETE `/api/reminders/{id}` - Delete reminder

### Admin
- GET `/api/admin/users` - Get all users (admin only)
- PATCH `/api/admin/users/{id}/activate` - Activate user
- PATCH `/api/admin/users/{id}/deactivate` - Deactivate user
- DELETE `/api/admin/users/{id}` - Delete user

## Differences from Node.js Version

1. **Database Driver**: Using Motor (async MongoDB driver) instead of Mongoose
2. **Validation**: Using Pydantic models instead of Mongoose schemas
3. **Authentication**: Using python-jose for JWT instead of jsonwebtoken
4. **Password Hashing**: Using passlib with bcrypt instead of bcryptjs
5. **Email**: Using smtplib instead of nodemailer
6. **Async**: All database operations are async using asyncio

## Project Structure

```
server_fastapi/
├── config/
│   ├── database.py       # MongoDB connection
│   └── settings.py       # Environment configuration
├── middlewares/
│   └── auth.py           # Authentication dependencies
├── models/
│   ├── user.py          # User models
│   ├── case.py          # Case models
│   ├── judgment.py      # Judgment models
│   ├── reminder.py      # Reminder models
│   └── chatlog.py       # Chat log models
├── routes/
│   ├── auth.py          # Authentication routes
│   ├── profile.py       # Profile routes
│   ├── cases.py         # Case routes
│   ├── judgments.py     # Judgment routes
│   ├── ai.py            # AI routes
│   ├── reminders.py     # Reminder routes
│   └── admin.py         # Admin routes
├── scripts/
│   ├── create_admin.py  # Create admin user
│   └── seed_judgments.py # Seed sample data
├── utils/
│   ├── auth.py          # Auth utilities
│   └── mailer.py        # Email utilities
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
```

## Testing

You can test the API using:
- The Swagger UI at http://localhost:5000/docs
- Postman or similar tools
- curl commands

## Notes

- All endpoints (except authentication) require JWT token in Authorization header: `Bearer <token>`
- The AI endpoints currently return mock responses - integrate actual AI models as needed
- MongoDB indexes should be created for better performance in production
- CORS is configured for localhost:5173 and localhost:5174 (frontend dev servers)
