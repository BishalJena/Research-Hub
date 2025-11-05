# Backend Setup Guide

This guide walks you through setting up the Smart Research Hub backend on your local machine.

## Prerequisites

### Required Software
- **Python 3.13+** ([Download](https://www.python.org/downloads/))
- **PostgreSQL 15+** ([Download](https://www.postgresql.org/download/))
- **pip** (comes with Python)

### API Keys (Free Signup)
- **OpenRouter**: https://openrouter.ai/keys (for AI models)
- **Cohere**: https://cohere.com (for embeddings - FREE tier)
- **Bhashini** (optional): https://bhashini.gov.in/ulca (for translation - FREE)

## Step-by-Step Setup

### 1. Navigate to Backend Directory

```bash
cd /path/to/Smart-Research-Hub/backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Installation time**: 2-3 minutes
**Total size**: ~400MB

### 4. Setup PostgreSQL Database

#### Option A: macOS (with Homebrew)

```bash
# If PostgreSQL is not running, start it:
brew services start postgresql@15

# Create database
createdb research_hub
```

#### Option B: Linux

```bash
# Start PostgreSQL service
sudo systemctl start postgresql

# Create database
sudo -u postgres createdb research_hub
```

#### Option C: Windows

```powershell
# Open psql terminal
psql -U postgres

# In psql:
CREATE DATABASE research_hub;
\q
```

### 5. Configure Environment Variables

```bash
# Copy example .env file
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required configuration in `.env`:**

```bash
# Database - Update with your PostgreSQL username
DATABASE_URL=postgresql+psycopg://YOUR_USERNAME@localhost:5432/research_hub

# Example for macOS user 'bishal':
# DATABASE_URL=postgresql+psycopg://bishal@localhost:5432/research_hub

# Example for default PostgreSQL user:
# DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/research_hub

# API Keys
OPENAI_API_KEY=sk-or-v1-YOUR_OPENROUTER_KEY_HERE
COHERE_API_KEY=YOUR_COHERE_KEY_HERE

# Optional
BHASHINI_API_KEY=YOUR_BHASHINI_KEY_HERE  # Can leave empty
```

**How to find your PostgreSQL username:**

```bash
# On macOS/Linux:
whoami

# Or check current PostgreSQL user:
psql -l
```

### 6. Start the Server

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start server
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Will watch for changes in these directories: ['/path/to/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process using WatchFiles
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database initialized
INFO:     Application startup complete.
```

### 7. Verify Installation

Open a new terminal and test the API:

```bash
# Test root endpoint
curl http://127.0.0.1:8000/

# Expected response:
# {"message":"Smart Research Hub API","version":"v1","docs":"/api/v1/docs"}
```

**View API Documentation:**

Open in browser: http://127.0.0.1:8000/api/v1/docs

You should see the Swagger UI with all API endpoints.

## Troubleshooting

### Issue: Database Connection Error

**Error:**
```
psycopg.OperationalError: connection failed: FATAL: role "postgres" does not exist
```

**Solution:**
1. Check your PostgreSQL username: `whoami` or `psql -l`
2. Update `DATABASE_URL` in `.env` to use correct username
3. Restart the server

### Issue: Module Not Found Errors

**Error:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Python Version Too Old

**Error:**
```
ERROR: Could not find a version that satisfies the requirement psycopg[binary]>=3.1.0
```

**Solution:**
- Upgrade to Python 3.13+
- Verify version: `python --version`

### Issue: PostgreSQL Not Running

**Error:**
```
psycopg.OperationalError: could not connect to server: Connection refused
```

**Solution:**

```bash
# macOS (Homebrew):
brew services start postgresql@15

# Linux:
sudo systemctl start postgresql

# Windows:
# Start PostgreSQL from Services or pgAdmin
```

### Issue: Port 8000 Already in Use

**Error:**
```
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

## Development

### Running Tests

```bash
pytest
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Code Formatting

```bash
# Format code
black app/

# Check linting
flake8 app/

# Type checking
mypy app/
```

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Configuration, database
│   ├── models/       # Database models
│   ├── schemas/      # Pydantic schemas
│   ├── services/     # Business logic
│   └── main.py       # Application entry point
├── tests/            # Test files
├── venv/             # Virtual environment
├── .env              # Environment variables (create from .env.example)
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Performance

- **Startup time**: 2-3 seconds
- **API response time**: 200-500ms (depending on API calls)
- **Memory usage**: ~200-300MB
- **Concurrent requests**: 100+ (with default uvicorn workers)

## API Keys Cost Estimate

For a **Proof of Concept** (8 users, 2 months):

- **OpenRouter**: $5-15 (using Gemini 2.5 Flash - very cheap!)
- **Cohere**: FREE (1000 API calls/month on free tier)
- **Bhashini**: FREE (Government of India service)

**Total**: $5-20 for entire PoC period 💰

## Support

For issues or questions:
1. Check [CHANGELOG.md](CHANGELOG.md) for recent changes
2. Review [Troubleshooting](#troubleshooting) section above
3. Check API docs at http://127.0.0.1:8000/api/v1/docs
4. Review logs in console output

## Next Steps

Once the backend is running:
1. Test API endpoints using Swagger UI
2. Setup the frontend (see ../frontend/README.md)
3. Review API documentation for integration
4. Start building features!

---

**Backend Status**: ✅ Ready for development

Server running at: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/api/v1/docs
