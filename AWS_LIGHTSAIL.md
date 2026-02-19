# 🚀 AWS Lightsail Setup Guide (Easiest AWS Option)

AWS Lightsail is AWS's simplified service - perfect for getting started!

## Why Lightsail?
- ✅ **$5/month** flat rate (first month often free)
- ✅ **One-click setup** (vs complex EC2)
- ✅ **Includes everything:** Server + Database + Networking
- ✅ **SSH access** for development
- ✅ **Static IP included**
- ✅ **Easy to upgrade** to EC2 later if needed

---

## 🎯 Quick Setup (15 minutes)

### Step 1: Create AWS Account

1. Go to https://aws.amazon.com
2. Click "Create an AWS Account"
3. Enter email and password
4. Add payment method (required, but we'll use cheap options)
5. Verify identity

**Note:** AWS may charge $1 for verification, refunded immediately.

---

### Step 2: Launch Lightsail Instance

1. **Go to Lightsail Console:**
   - https://lightsail.aws.amazon.com/

2. **Click "Create Instance"**

3. **Choose Instance Location:**
   - Pick closest to you (e.g., "US East (N. Virginia)")

4. **Pick Your Instance Image:**
   - Select "OS Only"
   - Choose **"Ubuntu 22.04 LTS"**

5. **Choose Instance Plan:**
   - **$5/month plan** (512MB RAM, 20GB SSD)
   - Perfect for development!
   
   Specs:
   ```
   - 512 MB Memory
   - 1 vCPU
   - 20 GB SSD
   - 1 TB Transfer
   ```

6. **Name Your Instance:**
   - Name: `pipeline-debugger-dev`

7. **Click "Create Instance"**

**Wait 2 minutes** - Your server is starting! ☕

---

### Step 3: Connect to Your Server

Once instance shows "Running":

#### **Option A: Browser SSH (Easiest)**

1. Click on your instance name
2. Click "Connect using SSH" button
3. **A terminal opens in your browser!** ✨

#### **Option B: Local Terminal (Better)**

1. Click your instance → "Account" tab
2. Download SSH key
3. In your Mac terminal:

```bash
# Move the key
mv ~/Downloads/LightsailDefaultKey-us-east-1.pem ~/.ssh/
chmod 400 ~/.ssh/LightsailDefaultKey-us-east-1.pem

# Connect (get IP from Lightsail console)
ssh -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ubuntu@YOUR_INSTANCE_IP
```

---

### Step 4: Setup Your Server (10 minutes)

Once connected via SSH:

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip

# 3. Install PostgreSQL with pgvector
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 4. Install Git
sudo apt install -y git

# 5. Create database
sudo -u postgres psql << EOF
CREATE DATABASE pipeline_debugger;
CREATE USER dbuser WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE pipeline_debugger TO dbuser;
\c pipeline_debugger
CREATE EXTENSION vector;
EOF

# 6. Install Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

---

### Step 5: Deploy Your Code

```bash
# 1. Clone your repo (or upload via SCP)
git clone https://github.com/YOUR_USERNAME/pipeline-debugger.git
cd pipeline-debugger/backend

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cat > .env << 'EOF'
DATABASE_URL=postgresql://dbuser:your_secure_password_here@localhost:5432/pipeline_debugger
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-your-key-here
GITHUB_TOKEN=your-github-token
SECRET_KEY=your-super-secret-key-change-this
DEBUG=false
LOG_LEVEL=INFO
BACKEND_CORS_ORIGINS=["*"]
EOF

# 5. Run database migrations
alembic upgrade head

# 6. Test it works
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### Step 6: Open Port 8000

**In Lightsail Console:**

1. Click your instance
2. Go to "Networking" tab
3. Click "Add rule" under Firewall
4. Add:
   - **Application:** Custom
   - **Protocol:** TCP
   - **Port:** 8000
5. Click "Create"

---

### Step 7: Access Your API!

**Open in browser:**
```
http://YOUR_INSTANCE_IP:8000/docs
```

Replace `YOUR_INSTANCE_IP` with the IP shown in Lightsail console.

**Test it:**
```bash
curl http://YOUR_INSTANCE_IP:8000/api/v1/health
```

🎉 **You're live on AWS!**

---

## 🔧 Development Workflow

### **Develop Locally, Deploy to AWS:**

```bash
# On your Mac:
# 1. Make changes to code
# 2. Test locally (optional)
# 3. Commit to GitHub
git add .
git commit -m "Added feature X"
git push

# On AWS Lightsail (via SSH):
# 4. Pull latest code
cd ~/pipeline-debugger
git pull

# 5. Restart server
sudo systemctl restart pipeline-debugger  # (we'll set this up)
```

### **Or Develop Directly on AWS:**

```bash
# Use VS Code Remote SSH:
# 1. Install "Remote - SSH" extension in VS Code
# 2. Connect to your Lightsail instance
# 3. Edit code directly on server
# 4. Changes are live!
```

---

## 🚀 Production Setup (Keep Server Running)

Right now, server stops when you close SSH. Let's fix that:

```bash
# Create systemd service
sudo nano /etc/systemd/system/pipeline-debugger.service
```

Paste this:
```ini
[Unit]
Description=Pipeline Debugger API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/pipeline-debugger/backend
Environment="PATH=/home/ubuntu/pipeline-debugger/backend/venv/bin"
ExecStart=/home/ubuntu/pipeline-debugger/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Enable it:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable pipeline-debugger
sudo systemctl start pipeline-debugger

# Check status
sudo systemctl status pipeline-debugger

# View logs
sudo journalctl -u pipeline-debugger -f
```

**Now your server runs 24/7!** ✅

---

## 💰 Cost Breakdown

### **Lightsail:**
- **$5/month** for the instance
- **Includes:** 1TB bandwidth, static IP
- **Total: ~$5/month**

### **Add Managed Database (Optional):**
- Lightsail PostgreSQL: $15/month
- **Total: $20/month**

**For now, use PostgreSQL on same instance = $5/month total!**

---

## 🎯 Get a Domain Name (Optional)

**Make it accessible via custom domain:**

1. **In Lightsail:**
   - Go to "Networking" tab
   - Click "Create static IP"
   - Attach to your instance

2. **Buy domain:**
   - AWS Route 53: ~$12/year
   - Or Namecheap: ~$10/year

3. **Point domain to Lightsail:**
   - In Route 53 or your registrar
   - Create A record: `api.yourdomain.com` → `YOUR_STATIC_IP`

4. **Access via:**
   ```
   http://api.yourdomain.com:8000/docs
   ```

---

## 🔒 Add HTTPS (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get free SSL certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renews every 90 days!
```

---

## 📊 Monitor Your Instance

**In Lightsail Console:**
- Click your instance
- View "Metrics" tab
- See CPU, network, etc.

**Set up Alarms:**
- High CPU usage
- High bandwidth
- Instance down

---

## 🔧 Useful Commands

```bash
# SSH into server
ssh -i ~/.ssh/LightsailDefaultKey-us-east-1.pem ubuntu@YOUR_IP

# Check server status
sudo systemctl status pipeline-debugger

# View logs
sudo journalctl -u pipeline-debugger -f

# Restart server
sudo systemctl restart pipeline-debugger

# Update code
cd ~/pipeline-debugger
git pull
sudo systemctl restart pipeline-debugger

# Check disk space
df -h

# Check memory
free -h

# Check running processes
htop  # (install with: sudo apt install htop)
```

---

## 🆙 Upgrade Path

**When you outgrow $5/month instance:**

1. **Upgrade Lightsail Plan:**
   - $10/month: 1GB RAM
   - $20/month: 2GB RAM
   - Just click "Change plan"

2. **Or Migrate to EC2:**
   - Lightsail → Create snapshot
   - Export to EC2
   - More power, more features

---

## 🐛 Troubleshooting

### **"Can't connect to instance"**
- Check Firewall rules (port 8000 open?)
- Try browser SSH first
- Verify instance is "Running"

### **"Database connection failed"**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U dbuser -d pipeline_debugger -h localhost
```

### **"Server won't start"**
```bash
# Check logs
sudo journalctl -u pipeline-debugger -n 50

# Common issues:
# - Missing ANTHROPIC_API_KEY in .env
# - Database not created
# - Port already in use
```

### **"Out of disk space"**
```bash
# Check usage
df -h

# Clean up
sudo apt autoremove -y
sudo apt clean
```

---

## 🎓 What You're Learning

By using AWS Lightsail, you're learning:
- ✅ Linux server management
- ✅ SSH and remote development
- ✅ Database administration
- ✅ Systemd services
- ✅ AWS cloud infrastructure
- ✅ Production deployment

**These are valuable skills!** 🎯

---

## 📚 Next Steps

1. **Deploy your code** (follow steps above)
2. **Test all endpoints** (use /docs)
3. **Set up monitoring** (Lightsail metrics)
4. **Add domain name** (optional but nice)
5. **Enable HTTPS** (for production)
6. **Start building features!**

---

## 💡 Pro Tips

- **Snapshots:** Create snapshots before major changes
- **Monitoring:** Set up CPU/memory alarms
- **Backups:** Use Lightsail automatic snapshots ($1/month)
- **Security:** Change default passwords immediately
- **Updates:** Run `sudo apt update && sudo apt upgrade` weekly

---

**You're all set!** 🚀

Your API will be running 24/7 on AWS, accessible from anywhere, for just $5/month!
