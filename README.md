# 🏛️ LexiBot - Legal Assistant AI Application

> **An Intelligent Legal Research and Case Management System powered by Advanced AI and RAG (Retrieval-Augmented Generation)**

LexiBot is a comprehensive legal assistant platform designed to help legal professionals and clients manage cases efficiently, research legal documents, and get intelligent legal insights powered by cutting-edge AI technology.

## 🌟 Features

### Core Functionalities
- 📋 **Case Management**: Create, track, and manage legal cases with detailed information
- 🔍 **Intelligent Search**: Semantic search across a database of legal judgments using AI
- 💬 **AI-Powered Chat**: Get instant legal insights and case analysis through conversational AI
- 📊 **Case Analysis**: Automated prediction of case outcomes based on historical data
- 🔔 **Smart Reminders**: Never miss important case deadlines with intelligent reminder system
- 👤 **User Roles**: Support for clients, advocates, and administrators
- 📄 **Document Processing**: Extract and analyze PDF and DOCX legal documents with OCR support
- ⚡ **RAG Pipeline**: Retrieval-Augmented Generation for accurate, grounded legal responses

## 📸 Project Screenshots

### Home Page
![Home Page 1](project_photos/home_page%201.png)

### Home Page (Additional View)
![Home Page 2](project_photos/home_page%202.png)

### My Cases
![My Cases](project_photos/my%20cases%20.png)

### Judgment Workspace
![Judgment Workspace](project_photos/judgment%20workspace%20.png)

### AI Chat Interface
![LexiBot Chat](project_photos/lexibot_chat%20.png)

### Client Guidance
![Client Guidance](project_photos/client%20guidance.png)

## 🛠️ Tech Stack

### **Frontend**
- **React** 19.1.1 - Modern UI library
- **Vite** 7.1.7 - Fast build tool and dev server
- **React Router DOM** 7.9.5 - Client-side routing
- **Tailwind CSS** 4.1.16 - Utility-first CSS framework
- **Axios** 1.13.1 - HTTP client for API calls
- **Formik & Yup** - Form management and validation
- **React Icons** - Icon library

### **Backend**
- **FastAPI** 0.115.0 - Modern Python web framework
- **Uvicorn** 0.32.0 - ASGI server
- **MongoDB** - NoSQL database for flexible data storage
- **Motor** 3.6.0 - Async MongoDB driver
- **Pydantic** - Data validation using Python type hints
- **Python-Jose** - JWT authentication
- **Passlib & Bcrypt** - Secure password hashing

### **AI & Machine Learning**
- **Groq API** - Fast LLM inference for legal analysis
- **LangChain** 0.1.0 - Framework for building LLM applications
- **FAISS** 1.7.4 - Vector search and similarity matching
- **Sentence Transformers** 2.3.1 - Text embeddings generation
- **OpenAI** - GPT models for advanced NLP tasks

### **Document Processing**
- **PyPDF2** - PDF parsing and extraction
- **PDF2Image & Pytesseract** - OCR for scanned documents
- **Python-DOCX** - Word document processing
- **Pillow** - Image processing

### **Other Tools**
- **Environment Management**: Python-dotenv
- **Email Validation**: Email-validator
- **API Documentation**: Swagger UI (built-in with FastAPI)

## 📊 Languages & Frameworks

| Component | Language | Framework |
|-----------|----------|-----------|
| Frontend | JavaScript/JSX | React + Vite |
| Backend | Python | FastAPI |
| Database | N/A | MongoDB |
| AI/ML | Python | LangChain, FAISS, Sentence Transformers |
| Styling | CSS | Tailwind CSS |

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ and npm
- Python 3.10+
- MongoDB 4.4+
- Git

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Lexibot-Legal-Assistant-AI-Application.git
cd Lexibot-Legal-Assistant-AI-Application
```

#### 2. Frontend Setup
```bash
cd client
npm install
npm run dev
```
Frontend will be available at `http://localhost:5173`

#### 3. Backend Setup
```bash
cd server_fastapi

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # On Windows
# or
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Create a `.env` file in the `server_fastapi` directory:
```env
GROQ_API_KEY=your_groq_api_key_here
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=lexibot
JWT_SECRET_KEY=your_secret_key_here
```

#### 5. Start the Backend Server
```bash
python main.py
```
Backend API will be available at `http://localhost:5000`
API Documentation: `http://localhost:5000/docs`

## 📁 Project Structure

```
Lexibot-Legal-Assistant-AI-Application/
├── client/                          # React Frontend
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   ├── context/                # React context for state management
│   │   ├── api/                    # API integration
│   │   └── utils/                  # Utility functions
│   └── package.json
│
├── server_fastapi/                 # FastAPI Backend
│   ├── main.py                     # Application entry point
│   ├── config/                     # Configuration and DB setup
│   ├── models/                     # Pydantic data models
│   ├── routes/                     # API endpoints
│   │   ├── auth.py                # Authentication routes
│   │   ├── cases.py               # Case management
│   │   ├── judgments.py           # Judgment search and retrieval
│   │   ├── ai.py                  # AI and RAG endpoints
│   │   └── reminders.py           # Reminder management
│   ├── services/                   # Business logic
│   │   ├── embeddings.py          # Text embeddings
│   │   ├── vector_store.py        # FAISS vector database
│   │   ├── llm_service.py         # LLM integration (Groq)
│   │   └── rag_pipeline.py        # RAG orchestration
│   ├── utils/                      # Utility functions
│   │   ├── document_processor.py  # PDF/DOCX processing
│   │   └── formatters.py          # Response formatting
│   ├── scripts/                    # Utility scripts
│   │   ├── ingest_judgments.py    # Index builder
│   │   └── create_admin.py        # Admin creation
│   └── requirements.txt
│
├── data/                           # Data storage
│   └── faiss_index/               # Vector search index
│
└── project_photos/                 # Project screenshots
    ├── home_page 1.png
    ├── home_page 2.png
    ├── my cases .png
    ├── judgment workspace .png
    ├── lexibot_chat .png
    └── client guidance.png
```

## 🔑 Key API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Cases
- `GET /api/cases` - Retrieve user's cases
- `POST /api/cases` - Create new case
- `GET /api/cases/{id}` - Get case details
- `PUT /api/cases/{id}` - Update case
- `DELETE /api/cases/{id}` - Delete case

### Judgments
- `GET /api/judgments/search` - Search judgments
- `GET /api/judgments/{id}` - Get judgment details

### AI Services
- `POST /api/ai/chat` - Chat with LexiBot
- `POST /api/ai/summarize` - Summarize legal documents
- `POST /api/ai/extract` - Extract key information
- `POST /api/ai/predict` - Predict case outcomes

### Reminders
- `GET /api/reminders` - Get user reminders
- `POST /api/reminders` - Create reminder
- `PUT /api/reminders/{id}` - Update reminder

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact & Support

For questions, suggestions, or support, please reach out or open an issue on the GitHub repository.

---

**Built with ❤️ for the legal tech community**