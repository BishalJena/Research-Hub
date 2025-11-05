# 🔧 Installation Troubleshooting Guide

Common installation issues and their solutions for Smart Research Hub backend.

---

## ⚠️ Common Issues

### 1. Pydantic Build Error on Python 3.13

**Error:**
```
ERROR: Failed building wheel for pydantic-core
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

**Cause**: Old pydantic versions (< 2.10.0) don't have pre-built wheels for Python 3.13.

**Solution**: ✅ **FIXED in requirements.txt**
```bash
# requirements.txt now uses:
pydantic>=2.10.0  # Has Python 3.13 support
pydantic-settings>=2.7.0
```

**Action**: Just reinstall:
```bash
pip install --upgrade -r requirements.txt
```

---

### 2. Long Cohere Dependency Resolution

**Error:**
```
INFO: pip is still looking at multiple versions of cohere to determine which version is compatible...
This is taking longer than usual.
```

**Cause**: `cohere>=5.0.0` has many versions with complex dependencies.

**Solution**: ✅ **FIXED in requirements.txt**
```bash
# requirements.txt now uses:
cohere==5.6.2  # Pinned version - fast install
```

**Action**: Just reinstall:
```bash
pip install --upgrade -r requirements.txt
```

---

### 3. Email Validator Yanked Warning

**Error:**
```
WARNING: The candidate selected for download or install is a yanked version: 'email-validator' candidate (version 2.1.0)
```

**Cause**: Version 2.1.0 was yanked (removed) from PyPI.

**Solution**: ✅ **FIXED in requirements.txt**
```bash
# requirements.txt now uses:
email-validator>=2.2.0  # Uses non-yanked version
```

**Action**: Just reinstall:
```bash
pip install --upgrade -r requirements.txt
```

---

### 4. psycopg2-binary Compilation Error

**Error:**
```
ERROR: Could not build wheels for psycopg2-binary
```

**Cause**: No pre-built wheels for Python 3.13.

**Solution**: ✅ **ALREADY FIXED in requirements.txt**
```bash
# We use psycopg3 instead:
psycopg[binary]>=3.1.0  # Has Python 3.13 wheels
```

**Database URL Format Change**:
```bash
# OLD (psycopg2):
postgresql://user:pass@host:port/db

# NEW (psycopg3):
postgresql+psycopg://user:pass@host:port/db
```

---

### 5. Virtual Environment Issues

**Error:**
```
bad interpreter: /path/to/old/venv/bin/python3.13: no such file or directory
```

**Cause**: Virtual environment created in different location or with different Python.

**Solution**: Recreate virtual environment:
```bash
# 1. Delete old venv
rm -rf venv

# 2. Create new venv with Python 3.13
python3.13 -m venv venv

# 3. Activate
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 6. Missing Rust Compiler

**Error:**
```
error: failed to run custom build command for `pydantic-core`
Rust not found
```

**Cause**: Trying to build pydantic-core from source (shouldn't happen with pydantic 2.10+).

**Solution**:
1. Verify pydantic version in requirements.txt:
   ```bash
   grep pydantic requirements.txt
   # Should show: pydantic>=2.10.0
   ```

2. Clear pip cache and reinstall:
   ```bash
   pip cache purge
   pip install --upgrade -r requirements.txt
   ```

3. If still failing, install pre-built wheel directly:
   ```bash
   pip install --upgrade pydantic pydantic-settings
   ```

---

### 7. PostgreSQL Connection Error

**Error:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions**:

**Option 1: PostgreSQL not running**
```bash
# Mac (Homebrew):
brew services start postgresql@15

# Linux:
sudo systemctl start postgresql

# Check if running:
pg_isready
```

**Option 2: Wrong database URL format**
```bash
# Check .env file - must use psycopg format:
DATABASE_URL=postgresql+psycopg://bishal@localhost:5432/research_hub
#                         ^^^^^^^^^ Important!
```

**Option 3: Database doesn't exist**
```bash
# Create database:
createdb research_hub

# Or with psql:
psql -c "CREATE DATABASE research_hub;"
```

---

## 🚀 **Clean Installation (Recommended)**

If you have multiple issues, do a clean install:

```bash
# 1. Navigate to backend
cd backend

# 2. Remove old virtual environment
rm -rf venv

# 3. Create fresh venv with Python 3.13
python3.13 -m venv venv

# 4. Activate venv
source venv/bin/activate

# 5. Upgrade pip
pip install --upgrade pip setuptools wheel

# 6. Install dependencies (should be fast now!)
pip install -r requirements.txt

# 7. Verify installation
python -c "import fastapi, sqlalchemy, pydantic; print('✅ All imports work!')"

# 8. Check versions
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
# Should show: Pydantic: 2.10.x or higher

# 9. Setup database
createdb research_hub  # If not exists

# 10. Configure .env
cp .env.example .env
# Edit .env with your settings

# 11. Run server
uvicorn app.main:app --reload
```

**Expected install time**: 2-3 minutes (fast with pre-built wheels!)

---

## ✅ Verification Checklist

After installation, verify everything works:

```bash
# 1. Check Python version
python --version
# Should be: Python 3.13.x

# 2. Check pydantic version (critical!)
python -c "import pydantic; print(pydantic.__version__)"
# Should be: 2.10.x or higher

# 3. Check database connection
python -c "from app.core.database import engine; print('✅ DB connection works')"

# 4. Run tests
pytest tests/test_translation_service.py::TestTranslationService::test_translate_same_language -v
# Should pass

# 5. Start server
uvicorn app.main:app --reload
# Should start without errors
```

---

## 📊 **Dependency Versions (Working Combination)**

These versions are tested and work together on Python 3.13:

```txt
# Core Framework
fastapi>=0.115.0
uvicorn>=0.30.0
pydantic>=2.10.0  ✅ Python 3.13 support
pydantic-settings>=2.7.0

# Database
sqlalchemy>=2.0.36
psycopg[binary]>=3.1.0  ✅ Python 3.13 wheels
alembic>=1.14.0

# AI/ML APIs
openai>=1.54.0  ✅ Python 3.13 support
cohere==5.6.2  ✅ Pinned for fast install
anthropic>=0.49.0

# Data Processing
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Utilities
python-dateutil==2.8.2
pytz==2023.3
email-validator>=2.2.0  ✅ Non-yanked version
```

---

## 🐛 **Still Having Issues?**

### Check Requirements File

Ensure your `requirements.txt` has the latest fixes:

```bash
# Should show updated versions:
grep -E "(pydantic|cohere|email-validator)" requirements.txt

# Expected output:
# pydantic>=2.10.0  # Python 3.13 support with pre-built wheels
# pydantic-settings>=2.7.0  # Compatible with pydantic 2.10+
# email-validator>=2.2.0  # Fixed version (2.1.0 is yanked)
# cohere==5.6.2  # Pinned version - avoids long dependency resolution
```

### Clear Everything

```bash
# Nuclear option - start completely fresh:
cd backend

# 1. Delete venv
rm -rf venv

# 2. Clear pip cache
pip cache purge

# 3. Clear Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 4. Recreate venv
python3.13 -m venv venv
source venv/bin/activate

# 5. Fresh install
pip install --upgrade pip
pip install -r requirements.txt
```

### Get Help

1. Check GitHub issues: https://github.com/[your-repo]/issues
2. Check documentation: `docs/` folder
3. Verify Python version: `python --version` (must be 3.13+)
4. Check system requirements:
   - macOS: 10.14+ (tested on 14+)
   - Linux: Ubuntu 20.04+ / Debian 11+
   - Windows: 10+ with WSL2 recommended

---

## 📝 **Prevention Tips**

1. **Always use Python 3.13+**
   ```bash
   python --version  # Check first!
   ```

2. **Use virtual environments**
   ```bash
   # Never install globally!
   python -m venv venv
   source venv/bin/activate
   ```

3. **Keep pip updated**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

4. **Don't modify requirements.txt versions** unless you know what you're doing

5. **Use the exact DATABASE_URL format**
   ```bash
   postgresql+psycopg://user@host:port/db
   #             ^^^^^^^^ Don't forget this!
   ```

---

## 🎉 **Success!**

If you can run these without errors, you're ready:

```bash
# 1. Import check
python -c "from app.main import app; print('✅ Imports work')"

# 2. Server start
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. Health check
curl http://localhost:8000/health
# Should return: {"status":"healthy","environment":"development"}

# 4. API docs
open http://localhost:8000/api/v1/docs
# Should show Swagger UI

# 5. Run one test
pytest tests/test_translation_service.py -v -k "test_translate_same_language"
# Should pass
```

**You're ready to code!** 🚀

---

**Last Updated**: 2025-11-03
**Python Version**: 3.13.3 (tested)
**Platform**: macOS 14+ (should work on Linux/Windows too)
