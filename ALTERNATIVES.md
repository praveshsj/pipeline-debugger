# 🎯 Codespaces Alternatives for Old Mac

Since Codespaces isn't working, here are **3 better options** ranked by ease:

---

## Option 1: Gitpod (Best Cloud Alternative) ⭐⭐⭐

**Why Gitpod > Codespaces:**
- ✅ More stable and reliable
- ✅ 50 hours/month FREE
- ✅ Faster startup (30 seconds vs 60)
- ✅ Better for old browsers
- ✅ Works on Safari (Codespaces sometimes doesn't)

### How to Use Gitpod:

#### Method A: From GitHub (Easiest)
1. Push your code to GitHub (if not already)
2. Go to your repo URL
3. **Add "gitpod.io/#" before the URL**

Example:
```
https://github.com/yourname/pipeline-debugger
becomes
https://gitpod.io/#https://github.com/yourname/pipeline-debugger
```

That's it! Gitpod opens automatically.

#### Method B: Gitpod Dashboard
1. Go to https://gitpod.io
2. Sign in with GitHub
3. Click "New Workspace"
4. Paste your GitHub repo URL
5. Click "Continue"

### What Happens Next:
- Gitpod reads `.gitpod.yml` (I created this)
- Automatically starts PostgreSQL + Redis
- Installs Python dependencies
- Opens VS Code in browser
- Takes ~30 seconds

### After Gitpod Opens:
```bash
# 1. Add your API key
cd backend
nano .env  # Add: ANTHROPIC_API_KEY=sk-ant-...

# 2. Create database tables
alembic upgrade head

# 3. Start server
uvicorn app.main:app --reload --host 0.0.0.0
```

**Click the "Open Preview" when port 8000 notification appears!**

### Gitpod Free Tier:
- 50 hours/month
- 4 concurrent workspaces
- Public repos only (private = paid)

---

## Option 2: Simple Local (No Cloud, No Docker) ⭐⭐⭐

**Best if:** You want to work offline on your Mac

**Advantages:**
- ✅ Works on ANY Mac (even 10 years old)
- ✅ No Docker needed
- ✅ No cloud needed
- ✅ Uses SQLite (built into Python)
- ✅ 100% free

### Quick Setup:
```bash
# 1. Go to project
cd pipeline-debugger/backend

# 2. Create Python environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create simple .env
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./pipeline_debugger.db
ANTHROPIC_API_KEY=sk-ant-your-key-here
SECRET_KEY=dev-secret-key
DEBUG=true
EOF

# 5. Create database
python3 -c "
from app.core.database import engine, Base
from app.models.incident import *
Base.metadata.create_all(bind=engine)
print('✅ Database ready!')
"

# 6. Start server
uvicorn app.main:app --reload
```

**Open:** http://localhost:8000/docs

**See full guide:** `SIMPLE_LOCAL_SETUP.md`

### Limitations:
- No pgvector (pattern matching disabled)
- Can't test concurrent access
- **But everything else works!**

### When to Use:
- Quick testing
- Learning the codebase
- Development without internet
- Later switch to PostgreSQL for production

---

## Option 3: Replit (Simplest Cloud) ⭐⭐

**Best if:** You want zero configuration

**Advantages:**
- ✅ Super simple (3 clicks)
- ✅ Built-in database
- ✅ Works on iPad even
- ✅ Free tier available

### How to Use Replit:

1. **Go to https://replit.com**
2. **Click "Create Repl"**
3. **Choose "Import from GitHub"**
4. **Paste your repo URL**
5. **Click "Import"**

Replit automatically:
- Detects Python
- Installs dependencies
- Sets up database
- Gives you a URL

### Configure:
1. Click "Secrets" tab (lock icon)
2. Add: `ANTHROPIC_API_KEY` = `sk-ant-...`
3. Click "Run"

**Done!** Replit gives you a public URL.

### Replit Free Tier:
- Unlimited public repls
- 1GB storage
- Always-on with bounties/pay

### Limitations:
- Slower than Gitpod
- Public by default
- Goes to sleep when inactive

---

## Option 4: Railway (Deploy & Develop) ⭐

**Best if:** You want a production environment

**Advantages:**
- ✅ Real PostgreSQL
- ✅ Can develop directly on it
- ✅ $5/month credit FREE
- ✅ Production-ready

### Quick Setup:

```bash
# 1. Install Railway CLI
brew install railway

# 2. Login
railway login

# 3. Initialize
cd pipeline-debugger
railway init

# 4. Add PostgreSQL
railway add --database postgres

# 5. Deploy
railway up
```

**Railway gives you:**
- Real PostgreSQL with pgvector
- Live URL (e.g., yourapp.up.railway.app)
- Environment variables UI
- Logs & monitoring

### Cost:
- $5 free credit/month
- After that: ~$10-20/month
- Can pause when not using

---

## 🎯 My Recommendation for You

Based on "old MacBook" + "Codespaces not working":

### **Start with: Gitpod** (Option 1)
Why:
- Most similar to Codespaces
- Very reliable
- Full Docker environment
- 50 hours/month free

**If Gitpod also doesn't work:**

### **Use: Simple Local Setup** (Option 2)
Why:
- Works on any Mac
- No cloud dependencies
- Instant startup
- Learn the code locally

**Then later deploy to Railway for production.**

---

## 🆘 Troubleshooting Codespaces

**Before giving up, try:**

### Issue: "Codespace won't start"
```bash
# Try from VS Code desktop instead of browser
# Download VS Code
brew install --cask visual-studio-code

# Install GitHub CLI
brew install gh
gh auth login

# Try creating from CLI
gh codespace create --repo yourname/pipeline-debugger
```

### Issue: "Browser hangs"
- Try different browser (Chrome vs Safari)
- Clear browser cache
- Try incognito/private mode
- Check internet connection

### Issue: "Container failed to build"
- Check `.devcontainer/devcontainer.json` syntax
- Try "Rebuild Container" option
- Delete and recreate codespace

---

## Quick Comparison Table

| Option | Setup Time | Cost | Old Mac OK? | Offline? |
|--------|-----------|------|-------------|----------|
| **Gitpod** | 2 min | Free (50h) | ✅ Yes | ❌ No |
| **Local SQLite** | 5 min | Free | ✅ Yes | ✅ Yes |
| **Replit** | 1 min | Free | ✅ Yes | ❌ No |
| **Railway** | 5 min | $5/mo free | ✅ Yes | ❌ No |
| **Codespaces** | 2 min | Free (60h) | ⚠️ Issues | ❌ No |

---

## 🎬 What I Recommend You Do NOW

**Try this order:**

1. **First: Try Gitpod** (5 minutes)
   - Go to: `https://gitpod.io/#YOUR_GITHUB_REPO_URL`
   - If it works → you're done! ✅

2. **If Gitpod also fails: Local Setup** (10 minutes)
   - Follow `SIMPLE_LOCAL_SETUP.md`
   - Works 100% guaranteed
   - No cloud needed

3. **Working? Great!** Start building features
   - Evidence collector
   - Claude integration
   - GitHub PRs

---

## Need Help?

Tell me:
1. **Which option you want to try?**
2. **What error are you seeing with Codespaces?** (might be fixable)
3. **Does your Mac have Python installed?** (`python3 --version`)

I'll help you get unblocked! 🚀
