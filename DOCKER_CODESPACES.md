# 🐳 Docker & GitHub Codespaces Guide

This project supports **three ways** to run it:

1. **Local Python** (manual setup)
2. **Docker** (containerized)
3. **GitHub Codespaces** (cloud development)

---

## 🚀 Option 1: Docker (Recommended for Local Development)

### Why Docker?
- ✅ **Zero config** - Everything just works
- ✅ **Consistent** - Same environment everywhere
- ✅ **Isolated** - Won't mess with your system
- ✅ **Complete** - Includes PostgreSQL + Redis + Backend

### Quick Start (5 minutes)

#### Prerequisites
- Docker Desktop installed ([download here](https://www.docker.com/products/docker-desktop/))
- That's it! 🎉

#### Step 1: Configure Environment
```bash
# Create .env file with your API keys
cat > .env << EOF
ANTHROPIC_API_KEY=your-api-key-here
GITHUB_TOKEN=your-github-token
SECRET_KEY=your-secret-key
EOF
```

#### Step 2: Start Everything
```bash
# Start all services (PostgreSQL + Redis + Backend)
docker-compose up -d

# View logs
docker-compose logs -f backend
```

#### Step 3: Initialize Database
```bash
# Run database migrations
docker-compose exec backend alembic upgrade head
```

#### Step 4: Test It!
```bash
# Check health
curl http://localhost:8000/api/v1/health

# Or open in browser
open http://localhost:8000/docs
```

### Common Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f backend

# Restart backend only
docker-compose restart backend

# Access backend shell
docker-compose exec backend bash

# Access PostgreSQL
docker-compose exec db psql -U postgres -d pipeline_debugger

# Access Redis CLI
docker-compose exec redis redis-cli

# Rebuild after code changes
docker-compose build backend
docker-compose up -d backend

# View running containers
docker-compose ps

# Clean everything (⚠️ deletes data)
docker-compose down -v
```

### Development Workflow with Docker

```bash
# 1. Make code changes in backend/app/
# Code is mounted, so changes are live!

# 2. Backend auto-reloads (thanks to --reload flag)
# Just refresh your browser or re-run curl

# 3. View logs to debug
docker-compose logs -f backend

# 4. Add new dependencies
# Edit backend/requirements.txt, then:
docker-compose build backend
docker-compose up -d backend
```

### Troubleshooting Docker

**"Port already in use" error:**
```bash
# Check what's using the port
lsof -i :8000  # or 5432, 6379

# Kill the process or change ports in docker-compose.yml
```

**"Database connection refused":**
```bash
# Check if PostgreSQL is healthy
docker-compose ps

# Wait for it to be healthy
docker-compose logs db

# Recreate if needed
docker-compose down
docker-compose up -d
```

**Backend not starting:**
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing ANTHROPIC_API_KEY in .env
# - Database not ready yet (wait 10 seconds)
```

---

## ☁️ Option 2: GitHub Codespaces (Cloud Development)

### Why Codespaces?
- ✅ **Instant** - Ready in 60 seconds
- ✅ **Cloud-based** - Work from anywhere
- ✅ **Powerful** - 4-32 core machines
- ✅ **Free** - 60 hours/month on free plan

### Quick Start (1 minute)

#### Step 1: Open in Codespaces

**From GitHub:**
1. Go to your repository on GitHub
2. Click the green **"Code"** button
3. Select **"Codespaces"** tab
4. Click **"Create codespace on main"**

**Direct URL:**
```
https://github.com/your-username/pipeline-debugger
→ Click "Code" → "Codespaces" → "Create"
```

#### Step 2: Wait for Setup
Codespaces automatically:
- ✅ Starts PostgreSQL + Redis
- ✅ Installs Python dependencies
- ✅ Sets up VS Code
- ✅ Forwards ports (8000, 5432, 6379)

This takes ~60 seconds.

#### Step 3: Configure Environment
```bash
# In the Codespaces terminal:
cd backend
cp .env.example .env
nano .env  # Add your ANTHROPIC_API_KEY
```

#### Step 4: Run Database Migrations
```bash
alembic upgrade head
```

#### Step 5: Start the Server
```bash
uvicorn app.main:app --reload
```

#### Step 6: Open the App
VS Code will show a notification: **"Your application running on port 8000 is available"**

Click **"Open in Browser"** or visit the forwarded port URL.

### Codespaces Features

**Auto-installed VS Code Extensions:**
- Python + Pylance (language support)
- Black (code formatting)
- Ruff (linting)
- Docker tools
- GitHub Copilot (if you have it)
- GitLens (git visualization)

**Keyboard Shortcuts:**
- `Ctrl + ~` - Toggle terminal
- `Ctrl + Shift + P` - Command palette
- `F5` - Start debugging

**Development Workflow:**
1. Edit code in VS Code
2. Save (auto-formats with Black)
3. Backend auto-reloads
4. Test in browser or with curl

### Codespaces Configuration

Located in `.devcontainer/devcontainer.json`:

```json
{
  "name": "Pipeline Debugger",
  "dockerComposeFile": "../docker-compose.yml",
  "forwardPorts": [8000, 5432, 6379],
  "postCreateCommand": "pip install -r requirements.txt"
}
```

**Customize it:**
- Add more VS Code extensions
- Change Python version
- Add other services

### Cost & Limits

**Free Tier:**
- 60 hours/month
- 2-core machines
- 32GB storage

**Pro Tier ($4/month):**
- 90 hours/month
- Up to 8-core machines
- 20GB storage per codespace

**Best Practices:**
- Stop codespace when not using (saves hours)
- Delete old codespaces (saves storage)
- Use 2-core for development (4-core for production testing)

### Codespaces Commands

```bash
# In your local terminal:

# Create codespace
gh codespace create --repo your-username/pipeline-debugger

# List codespaces
gh codespace list

# SSH into codespace
gh codespace ssh

# Stop codespace
gh codespace stop

# Delete codespace
gh codespace delete
```

---

## 🔄 Option 3: Local Python (Manual Setup)

See `GETTING_STARTED.md` for detailed instructions.

**When to use:**
- You don't have Docker
- You want full control
- You already have PostgreSQL + Redis installed

---

## 📊 Comparison Table

| Feature | Docker | Codespaces | Local Python |
|---------|--------|------------|--------------|
| **Setup Time** | 5 min | 1 min | 30 min |
| **Prerequisites** | Docker only | GitHub account | Python + PostgreSQL + Redis |
| **Isolation** | ✅ Complete | ✅ Complete | ❌ Shares system |
| **Cost** | Free | Free (60h/mo) | Free |
| **Works Offline** | ✅ Yes | ❌ No | ✅ Yes |
| **Team Consistency** | ✅ Perfect | ✅ Perfect | ⚠️ Varies |
| **Performance** | ✅ Native | ⚠️ Network latency | ✅ Native |

---

## 🎯 Recommended Setup

**For Development:**
→ **Docker** (consistent, isolated, easy)

**For Quick Testing:**
→ **Codespaces** (instant, no setup)

**For Production:**
→ **Docker** (deployed with docker-compose or Kubernetes)

**For Contributing:**
→ **Codespaces** (everyone has same environment)

---

## 🐛 Troubleshooting

### Docker Issues

**"Cannot connect to Docker daemon":**
```bash
# Make sure Docker Desktop is running
# Restart Docker Desktop if needed
```

**"Port 8000 already in use":**
```bash
# Check what's using it
lsof -i :8000

# Kill it or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Codespaces Issues

**"Ports not forwarding":**
- Check bottom panel "Ports" tab
- Click "Forward a Port" manually
- Add: 8000, 5432, 6379

**"Container failed to start":**
- Check `.devcontainer/devcontainer.json` syntax
- View creation logs in Codespaces dashboard
- Try rebuilding: Cmd+Shift+P → "Rebuild Container"

**"Out of space":**
- Delete old codespaces
- Clean docker: `docker system prune -a`

---

## 🚢 Deployment

### Deploy with Docker

**Railway:**
```bash
railway login
railway init
railway up
```

**Render:**
- Connect GitHub repo
- Render auto-detects docker-compose.yml
- Add environment variables
- Deploy!

**AWS ECS / GCP Cloud Run:**
- Build image: `docker build -t pipeline-debugger ./backend`
- Push to registry: `docker push your-registry/pipeline-debugger`
- Deploy with service

---

## 📚 Additional Resources

**Docker:**
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

**Codespaces:**
- [Codespaces Docs](https://docs.github.com/en/codespaces)
- [devcontainer.json Reference](https://containers.dev/implementors/json_reference/)

**Production:**
- [12-Factor App](https://12factor.net/)
- [Docker Production Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## ✅ Quick Decision Tree

```
Do you have Docker installed?
├─ Yes → Use Docker (docker-compose up -d)
└─ No
    ├─ Have GitHub account? → Use Codespaces
    └─ No GitHub? → Local Python setup
```

---

**You're all set!** 🎉

Choose your favorite method and start building! Each option gives you a fully functional development environment.
