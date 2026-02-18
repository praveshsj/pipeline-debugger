# 🚀 Getting Started with Pipeline Debugger

This guide will get you from zero to running the Pipeline Debugger in 30 minutes.

---

## 📋 Prerequisites

Before you start, make sure you have:

- ✅ Python 3.11 or higher
- ✅ PostgreSQL 15+ installed and running
- ✅ Git
- ✅ Anthropic API key ([get one here](https://console.anthropic.com/))
- ✅ (Optional) GitHub Personal Access Token
- ✅ (Optional) Airflow instance to connect to

---

## ⚡ Quick Start (5 minutes)

### 1. Clone and Setup

```bash
# Navigate to the project
cd pipeline-debugger/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your favorite editor
```

**Minimum required settings:**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/pipeline_debugger
ANTHROPIC_API_KEY=sk-ant-...your-key-here...
SECRET_KEY=your-secret-key-change-this
```

### 3. Setup Database

```bash
# Create the database
createdb pipeline_debugger

# Or using psql:
psql -U postgres -c "CREATE DATABASE pipeline_debugger;"

# Install pgvector extension
psql -U postgres -d pipeline_debugger -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Run migrations (creates all tables)
alembic upgrade head
```

### 4. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

**That's it!** 🎉 Your API is running at http://localhost:8000

---

## 🧪 Test It Works

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/api/v1/health
```

You should see:
```json
{
  "status": "healthy",
  "app_name": "Pipeline Debugger",
  "version": "0.1.0",
  "database": "healthy"
}
```

### 2. View API Docs

Open your browser to: http://localhost:8000/docs

You'll see interactive Swagger documentation for all endpoints.

### 3. Send a Test Webhook

```bash
curl -X POST http://localhost:8000/api/v1/webhooks/airflow/failure \
  -H "Content-Type: application/json" \
  -d '{
    "dag_id": "test_pipeline",
    "task_id": "test_task",
    "execution_date": "2024-02-18T10:00:00Z",
    "error_message": "Test error",
    "log_url": "http://airflow:8080/log?dag_id=test_pipeline"
  }'
```

You should get:
```json
{
  "success": true,
  "incident_id": "uuid-here",
  "message": "Incident created, analysis starting"
}
```

### 4. List Incidents

```bash
curl http://localhost:8000/api/v1/incidents
```

---

## 🔗 Connect to Airflow

### Option 1: Webhook (Recommended for MVP)

Add this to your Airflow DAG to send failure notifications:

```python
from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
from datetime import datetime
import json

def my_failing_task():
    # Your task logic that might fail
    raise Exception("Something went wrong!")

with DAG(
    'my_pipeline',
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    catchup=False
) as dag:
    
    task = PythonOperator(
        task_id='my_task',
        python_callable=my_failing_task
    )
    
    # Add webhook notification on failure
    notify_debugger = SimpleHttpOperator(
        task_id='notify_debugger',
        http_conn_id='pipeline_debugger',
        endpoint='/api/v1/webhooks/airflow/failure',
        method='POST',
        data=json.dumps({
            'dag_id': '{{ dag.dag_id }}',
            'task_id': '{{ task.task_id }}',
            'execution_date': '{{ ts }}',
            'log_url': '{{ ti.log_url }}',
            'error_message': '{{ ti.log[-500:] }}'  # Last 500 chars of log
        }),
        headers={'Content-Type': 'application/json'},
        trigger_rule='one_failed'
    )
    
    task >> notify_debugger
```

**Setup HTTP connection in Airflow:**

1. Go to Airflow UI → Admin → Connections
2. Add new connection:
   - Conn Id: `pipeline_debugger`
   - Conn Type: `HTTP`
   - Host: `http://localhost:8000` (or your server URL)

### Option 2: Airflow API Integration

Set these in your `.env`:

```env
AIRFLOW_BASE_URL=http://localhost:8080
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin
```

The debugger will automatically fetch logs from Airflow.

---

## 🎯 Your First Analysis

Let's debug a real failure:

### 1. Create a Test Incident

```bash
curl -X POST http://localhost:8000/api/v1/webhooks/airflow/failure \
  -H "Content-Type: application/json" \
  -d '{
    "dag_id": "daily_etl",
    "task_id": "load_customers",
    "execution_date": "2024-02-18T10:00:00Z",
    "error_message": "SQL compilation error: column user_id does not exist",
    "log_url": "http://airflow:8080/log?dag_id=daily_etl&task_id=load_customers"
  }'
```

Save the `incident_id` from the response.

### 2. Trigger Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "your-incident-id-here"
  }'
```

### 3. View Results

```bash
# Get incident details
curl http://localhost:8000/api/v1/incidents/{incident_id}

# Get generated fixes
curl http://localhost:8000/api/v1/incidents/{incident_id}/fixes
```

---

## 📊 Database Schema

The system uses 5 main tables:

**Incidents** - Pipeline failures
- Stores error details, status, root cause

**Evidence** - Collected context
- Logs, git commits, schema changes

**Fixes** - Generated solutions
- Code patches, SQL fixes, instructions

**Patterns** - Learned patterns (with pgvector)
- Similar incidents for faster diagnosis

**Users** - User accounts
- For multi-tenant support (future)

---

## 🔧 Development Mode

### Enable Debug Logging

```env
DEBUG=true
LOG_LEVEL=DEBUG
```

### Auto-Reload on Code Changes

```bash
uvicorn app.main:app --reload --port 8000
```

### Run Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
# Format code
black app/

# Lint
ruff check app/
```

---

## 🐳 Docker Setup (Optional)

```bash
# Build image
docker build -t pipeline-debugger .

# Run with docker-compose
docker-compose up -d
```

This starts:
- Backend API on port 8000
- PostgreSQL on port 5432
- Redis on port 6379

---

## ❓ Troubleshooting

### "Connection refused" database error

```bash
# Check if PostgreSQL is running
pg_isready

# If not, start it:
# macOS (Homebrew)
brew services start postgresql

# Ubuntu
sudo systemctl start postgresql

# Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15
```

### "Module not found" errors

```bash
# Make sure you're in the venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Claude API errors

```bash
# Check your API key is set
echo $ANTHROPIC_API_KEY

# Test it directly
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Hi"}]
  }'
```

### Database migration issues

```bash
# Reset database (⚠️ deletes all data)
alembic downgrade base
alembic upgrade head

# Or drop and recreate
dropdb pipeline_debugger
createdb pipeline_debugger
psql -d pipeline_debugger -c "CREATE EXTENSION vector;"
alembic upgrade head
```

---

## 📚 Next Steps

1. **Connect your Airflow** - See webhook setup above
2. **Test with real failures** - Let a pipeline fail and watch it get analyzed
3. **Customize prompts** - Edit `app/integrations/claude/analysis.py`
4. **Add GitHub integration** - Set `GITHUB_TOKEN` in `.env`
5. **Deploy to production** - See deployment guide

---

## 💬 Need Help?

- 📖 Check the [full documentation](docs/)
- 🐛 [Report issues](https://github.com/your-repo/issues)
- 💡 [Request features](https://github.com/your-repo/issues/new)

---

**You're ready to go! 🎉**

Every pipeline failure will now automatically trigger:
1. Evidence collection
2. AI analysis
3. Fix generation
4. Impact assessment

Happy debugging! 🔍
