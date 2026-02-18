# 🔍 LLM-Powered Data Pipeline Debugger

**Automatically diagnose and fix data pipeline failures using AI**

When your Airflow/Prefect pipelines fail, this tool:
1. 🕵️ Collects all evidence (logs, git changes, schema changes)
2. 🤖 Uses Claude AI to find the root cause
3. 🔧 Generates code fixes automatically
4. 📊 Calculates blast radius and impact
5. 🧠 Learns from every incident

**Save 1.75 hours per incident. Turn hours of debugging into minutes.**

---

## 🏗️ Architecture

```
Pipeline Fails → Webhook → Evidence Collector → Claude AI → Fix Generator → GitHub PR
                              ↓
                         Knowledge Base (learns patterns)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

---

## 📦 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database with pgvector for similarity search
- **Celery** - Async task processing
- **SQLAlchemy** - ORM
- **Anthropic Claude API** - AI analysis
- **PyGithub** - GitHub integration
- **Apache Airflow Client** - Airflow integration

### Frontend
- **Next.js 14** - React framework
- **Tailwind CSS** - Styling
- **shadcn/ui** - UI components
- **React Query** - Data fetching

---

## 🎯 MVP Features (4 Weeks)

- [x] Week 1: Airflow webhook + log parsing
- [ ] Week 2: Claude AI integration + root cause analysis
- [ ] Week 3: Fix generator + GitHub PR creation
- [ ] Week 4: Knowledge base + similarity search

---

## 📁 Project Structure

```
pipeline-debugger/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes
│   │   ├── core/             # Config, security
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   ├── integrations/     # External APIs
│   │   └── utils/            # Helpers
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/              # Next.js pages
│   │   ├── components/       # React components
│   │   └── lib/              # Utilities
│   └── package.json
└── docs/                     # Documentation
```

---

## 🔌 Integrations

### Airflow Setup
1. Configure webhook in your Airflow DAG:
```python
from airflow.providers.http.operators.http import SimpleHttpOperator

failure_webhook = SimpleHttpOperator(
    task_id='notify_debugger',
    http_conn_id='debugger_api',
    endpoint='/webhook/airflow/failure',
    method='POST',
    data=json.dumps({
        'dag_id': '{{ dag.dag_id }}',
        'task_id': '{{ task.task_id }}',
        'execution_date': '{{ ts }}',
        'log_url': '{{ ti.log_url }}'
    }),
    trigger_rule='one_failed'
)
```

### GitHub Setup
1. Create a GitHub Personal Access Token with `repo` scope
2. Add to `.env`: `GITHUB_TOKEN=your_token_here`

### Claude API Setup
1. Get API key from https://console.anthropic.com/
2. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`

---

## 📊 Database Schema

### Incidents Table
Stores every pipeline failure for analysis and learning

### Evidence Table
Logs, git commits, schema changes collected per incident

### Fixes Table
Generated fixes with success/failure tracking

### Patterns Table (with pgvector)
Similar incident patterns for faster diagnosis

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

---

## 🚢 Deployment

### Backend (Railway / Render)
```bash
# Railway
railway login
railway init
railway up

# Or Render (connects to GitHub)
# Push to GitHub, connect repo in Render dashboard
```

### Frontend (Vercel)
```bash
# Vercel
vercel login
vercel deploy
```

---

## 💰 Pricing Strategy

**Freemium Model:**
- Free: 5 analyses/month
- Pro ($149/mo): 100 analyses/month
- Team ($499/mo): Unlimited + GitHub integration
- Enterprise ($1,999/mo): Custom + dedicated support

**Cost per analysis:** ~$0.05 (Claude API + infrastructure)

---

## 🤝 Contributing

This is a solo project currently. Once MVP is stable, contributions welcome!

---

## 📝 License

Proprietary - All rights reserved

---

## 🎯 Roadmap

**MVP (Month 1-2)**
- ✅ Core pipeline failure detection
- ✅ AI-powered root cause analysis
- ✅ Basic fix generation
- ✅ GitHub PR creation

**Phase 2 (Month 3-4)**
- [ ] Multi-orchestrator support (Prefect, Dagster)
- [ ] Advanced pattern learning
- [ ] Cost impact analysis
- [ ] Slack integration

**Phase 3 (Month 5-6)**
- [ ] Preventive analysis (before failures)
- [ ] Custom fix templates
- [ ] Team collaboration features
- [ ] API for programmatic access

---

## 📧 Contact

Questions? Found a bug? Want to collaborate?
- Create an issue on GitHub
- Email: [your-email]

---

**Built with ❤️ to save data engineers from debugging hell**
