# Quick Commands Reference 🚀

## Setup & Installation

```bash
# Navigate to server directory
cd D:\fyp\lexibot-judgment\server_fastapi

# Activate virtual environment
venv\Scripts\activate

# Install/Update dependencies
pip install openai==1.12.0
pip uninstall groq langchain-groq -y
```

## Testing

```bash
# Run Cerebras integration test
python test_cerebras.py

# Expected: All tests should PASS ✅
```

## Data Ingestion

### Ingest All Categories (Recommended)
```bash
# Clear existing index and ingest all judgments recursively
python scripts\ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom" --recursive --clear
```

### Ingest Specific Category
```bash
# Only divorce cases
python scripts\ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\divorce"

# Only bail cases
python scripts\ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\bail"

# Only laws
python scripts\ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\Laws"
```

### Add New Documents (Without Clearing)
```bash
# Add without --clear flag to append to existing index
python scripts\ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\new_cases" --recursive
```

## Start Server

```bash
# Development mode (with auto-reload)
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Testing (PowerShell)

### Chat Endpoint
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/ai/chat" `
  -ContentType "application/json" `
  -Body '{"message": "What are the grounds for divorce in Pakistani law?"}'
```

### Search Judgments
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/ai/search" `
  -ContentType "application/json" `
  -Body '{"query": "child custody", "limit": 5}'
```

### Summarize Judgment
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/ai/summarize" `
  -ContentType "application/json" `
  -Body '{"judgment_id": "your-judgment-id-here"}'
```

### Predict Outcome
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/ai/predict" `
  -ContentType "application/json" `
  -Body '{"case_details": "Divorce case with child custody dispute"}'
```

### Get Client Guidance
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/ai/guidance" `
  -ContentType "application/json" `
  -Body '{"case_type": "divorce", "situation": "Wife wants divorce due to abuse"}'
```

### Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ai/health"
```

### Get Stats
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/ai/stats"
```

## API Testing (cURL)

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"What are the grounds for divorce in Pakistani law?\"}"
```

### Search Judgments
```bash
curl -X POST http://localhost:8000/ai/search \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"child custody\", \"limit\": 5}"
```

### Health Check
```bash
curl http://localhost:8000/ai/health
```

## Troubleshooting

### Check Python Environment
```bash
# Which Python?
python --version

# Where is Python?
where python

# List installed packages
pip list | Select-String -Pattern "openai|sentence|faiss|fastapi"
```

### Check Server Status
```bash
# Test if server is running
Test-NetConnection -ComputerName localhost -Port 8000

# Check API health
Invoke-RestMethod -Uri "http://localhost:8000/ai/health"
```

### View Logs
```bash
# Server logs (if running in terminal)
# Look for ERROR or WARNING messages

# Check ingestion results
ls data\faiss_index  # Should show index files
```

### Reset Everything
```bash
# Clear vector store
python scripts\ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom" --recursive --clear

# Restart server
# Ctrl+C to stop, then restart with uvicorn command
```

## File Locations

### Configuration
- `.env` - Environment variables (API keys)
- `config\settings.py` - Application settings

### Data
- `data\faiss_index\` - Vector store (FAISS index)
- `data\raw_documents\` - Optional document storage
- `D:\fyp\lexibot-judgment\Datacollectiom\` - Your judgments

### Logs
- Terminal output during server run
- Check for ERROR or WARNING messages

## Common Issues

### "Module not found"
```bash
# Solution: Activate venv and install
venv\Scripts\activate
pip install -r requirements.txt
```

### "API key not configured"
```bash
# Solution: Check .env file
type .env | Select-String -Pattern "CEREBRAS"

# Should show:
# CEREBRAS_API_KEY=csk-6ckrkdjre8d2wc5432t33ntjxtc92wmhfprd2n38x3kx6xrc
```

### "No documents in vector store"
```bash
# Solution: Run ingestion
python scripts\ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom" --recursive --clear
```

### "Port already in use"
```bash
# Solution: Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
uvicorn app:app --reload --port 8001
```

## Performance Tips

### Faster Ingestion
- Process categories separately instead of all at once
- Use SSD for vector store storage
- Increase batch_size for embeddings (default: 32)

### Faster API Responses
- Reduce top_k in search (fewer documents retrieved)
- Reduce max_tokens for shorter responses
- Use caching for frequently asked questions

### Monitor Usage
- Check Cerebras dashboard: https://cloud.cerebras.ai/
- Watch token usage in logs
- Set up rate limiting if needed

## Development Workflow

1. **Start Development**
   ```bash
   cd D:\fyp\lexibot-judgment\server_fastapi
   venv\Scripts\activate
   ```

2. **Run Tests**
   ```bash
   python test_cerebras.py
   ```

3. **Start Server**
   ```bash
   uvicorn app:app --reload
   ```

4. **Test Changes**
   - Use Postman, cURL, or PowerShell
   - Check terminal logs for errors
   - Test frontend integration

5. **Deploy**
   ```bash
   # Without reload for production
   uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
   ```

## Documentation

- [CEREBRAS_MIGRATION.md](CEREBRAS_MIGRATION.md) - Migration guide
- [DATACOLLECTION_SETUP.md](DATACOLLECTION_SETUP.md) - Data ingestion guide
- [QUICK_START.md](QUICK_START.md) - Complete setup guide
- [RAG_IMPLEMENTATION_GUIDE.md](RAG_IMPLEMENTATION_GUIDE.md) - Technical details
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

---

**Quick Start**: Run `python test_cerebras.py`, then ingest data, then start server! 🚀
