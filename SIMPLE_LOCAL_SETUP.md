# 🚀 Simple Local Setup (No Docker Needed!)

This guide gets you running on your Mac WITHOUT Docker Desktop.

## What You Need
- Python 3.11+ (probably already have it)
- That's it! We'll skip PostgreSQL for now.

---

## Quick Start (10 minutes)

### Step 1: Check Python
```bash
python3 --version
# Should show 3.11 or higher
# If not, install from python.org
```

### Step 2: Setup Project
```bash
cd pipeline-debugger/backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Your prompt will change

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Use SQLite (Lighter Database)

Instead of PostgreSQL, let's use SQLite for development:

```bash
# Edit backend/app/core/config.py
# Find the DATABASE_URL line and change it to:
# DATABASE_URL: str = "sqlite:///./pipeline_debugger.db"
```

Or just create a simple `.env` file:
```bash
cat > .env << 'EOF'
# Database (using SQLite - easier for old Mac)
DATABASE_URL=sqlite:///./pipeline_debugger.db

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Redis (we'll skip for now)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=dev-secret-key-change-later
DEBUG=true
EOF
```

### Step 4: Create Database
```bash
# Create tables (without migrations for now)
python3 -c "
from app.core.database import engine, Base
from app.models.incident import Incident, Evidence, Fix, Pattern, User
Base.metadata.create_all(bind=engine)
print('✅ Database created!')
"
```

### Step 5: Start Server
```bash
uvicorn app.main:app --reload --port 8000
```

### Step 6: Test It!
Open browser: http://localhost:8000/docs

---

## ✅ This Works Because:
- SQLite = built into Python (no installation)
- No Docker needed
- No PostgreSQL setup
- Just Python!

---

## When You're Ready for Production:
- Switch back to PostgreSQL
- Use cloud hosting (Railway, Render)
- But for development, SQLite works fine!

---

## Quick Commands

```bash
# Start development
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Stop server
Ctrl + C

# Deactivate venv
deactivate
```

---

## Limitations of SQLite Version:
- ❌ No pgvector (pattern matching won't work)
- ❌ No concurrent writes (fine for solo dev)
- ✅ Everything else works perfectly!

---

## Troubleshooting

**"command not found: python3"**
```bash
# Install Python from python.org
# Or use Homebrew
brew install python@3.11
```

**"pip: command not found"**
```bash
python3 -m ensurepip
```

**"Module not found"**
```bash
# Make sure venv is activated
source venv/bin/activate
# See (venv) in prompt

# Reinstall
pip install -r requirements.txt
```

---

This is the simplest way to get started on an old Mac! 🎉
