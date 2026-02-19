# 🚀 AWS EC2 Setup Guide (More Control)

Use this if you want more power and flexibility than Lightsail.

## Why EC2?
- ✅ **Free Tier:** 750 hours/month for 12 months (basically free for 1 year!)
- ✅ **More powerful:** Choose exact specs you need
- ✅ **Scalable:** Easy to upgrade
- ✅ **Industry standard:** Most companies use EC2
- ⚠️ **More complex:** More settings to configure

---

## 🎯 Quick Setup (20 minutes)

### Step 1: Launch EC2 Instance

1. **Go to EC2 Console:**
   - https://console.aws.amazon.com/ec2/

2. **Click "Launch Instance"**

3. **Configure Instance:**

   **Name:**
   ```
   pipeline-debugger-dev
   ```

   **Application and OS Images:**
   - **AMI:** Ubuntu Server 22.04 LTS
   - **Architecture:** 64-bit (x86)

   **Instance Type:**
   - **Free Tier:** t2.micro (1 vCPU, 1GB RAM) ✅
   - **Better:** t3.small (2 vCPU, 2GB RAM) - $15/month
   - **Recommended for dev:** t3.small

   **Key Pair:**
   - Click "Create new key pair"
   - Name: `pipeline-debugger-key`
   - Type: RSA
   - Format: .pem (for Mac/Linux)
   - Click "Create key pair"
   - **SAVE THIS FILE!** You'll need it to connect

   **Network Settings:**
   - ✅ Allow SSH traffic from: Anywhere (or My IP)
   - ✅ Allow HTTP traffic
   - ✅ Allow HTTPS traffic
   - Click "Edit" → Add Rule:
     - Type: Custom TCP
     - Port: 8000
     - Source: Anywhere (0.0.0.0/0)

   **Storage:**
   - 20 GB gp3 (Free tier: up to 30 GB)

4. **Click "Launch Instance"**

**Wait 2 minutes** - Instance is starting! ☕

---

### Step 2: Connect to Your Instance

#### Get Your Instance IP:
1. Go to EC2 Console
2. Click "Instances"
3. Select your instance
4. Copy "Public IPv4 address"

#### Connect via SSH:

```bash
# Move your key file
mv ~/Downloads/pipeline-debugger-key.pem ~/.ssh/
chmod 400 ~/.ssh/pipeline-debugger-key.pem

# Connect (replace YOUR_IP)
ssh -i ~/.ssh/pipeline-debugger-key.pem ubuntu@YOUR_IP
```

---

### Step 3: Setup Server (Same as Lightsail)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3-pip git

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database
sudo -u postgres psql << EOF
CREATE DATABASE pipeline_debugger;
CREATE USER dbuser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE pipeline_debugger TO dbuser;
\c pipeline_debugger
CREATE EXTENSION vector;
EOF

# Install Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Clone your code
git clone https://github.com/YOUR_USERNAME/pipeline-debugger.git
cd pipeline-debugger/backend

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env
cat > .env << 'EOF'
DATABASE_URL=postgresql://dbuser:secure_password@localhost:5432/pipeline_debugger
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=sk-ant-your-key-here
SECRET_KEY=change-this-secret
DEBUG=false
EOF

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### Step 4: Test It!

**In browser:**
```
http://YOUR_INSTANCE_IP:8000/docs
```

---

## 💰 Cost Comparison

### **Free Tier (12 months):**
- **t2.micro:** 750 hours/month FREE
- **Storage:** 30 GB FREE
- **Data transfer:** 15 GB/month FREE
- **Total: $0/month** (first year!)

### **After Free Tier:**
- **t2.micro:** ~$8/month
- **t3.small:** ~$15/month
- **t3.medium:** ~$30/month

### **Additional Costs:**
- Storage: $0.10/GB/month (20GB = $2/month)
- Data transfer: $0.09/GB (after 1GB free)
- Elastic IP: Free if attached, $3.65/month if not

---

## 🎯 Production Setup

### **Make Server Run 24/7:**

```bash
# Create systemd service
sudo nano /etc/systemd/system/pipeline-debugger.service
```

Paste:
```ini
[Unit]
Description=Pipeline Debugger API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/pipeline-debugger/backend
Environment="PATH=/home/ubuntu/pipeline-debugger/backend/venv/bin"
ExecStart=/home/ubuntu/pipeline-debugger/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable pipeline-debugger
sudo systemctl start pipeline-debugger
sudo systemctl status pipeline-debugger
```

---

## 🔒 Security Hardening

### **1. Setup Firewall:**

```bash
# Install UFW
sudo apt install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow API
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

### **2. Disable Password Auth:**

```bash
sudo nano /etc/ssh/sshd_config
```

Set:
```
PasswordAuthentication no
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### **3. Auto Updates:**

```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📊 Monitoring with CloudWatch

AWS automatically monitors your EC2 instance!

**View Metrics:**
1. Go to EC2 Console
2. Select your instance
3. Click "Monitoring" tab
4. See: CPU, Network, Disk

**Set Up Alarms:**
1. Click "Create Alarm"
2. Choose metric (e.g., CPU > 80%)
3. Add email notification

---

## 🔄 Auto Scaling (Advanced)

**When you're ready for production:**

1. Create AMI (image) of your instance
2. Create Launch Template
3. Create Auto Scaling Group
4. Add Load Balancer
5. Scale automatically based on traffic!

---

## 💾 Backups

### **1. Automated Snapshots:**

```bash
# Install AWS CLI
sudo apt install -y awscli

# Create snapshot script
cat > ~/backup.sh << 'EOF'
#!/bin/bash
INSTANCE_ID=$(ec2-metadata --instance-id | cut -d " " -f 2)
DATE=$(date +%Y-%m-%d)
aws ec2 create-snapshot \
  --volume-id YOUR_VOLUME_ID \
  --description "Backup-$DATE"
EOF

chmod +x ~/backup.sh

# Add to cron (daily backup at 2 AM)
echo "0 2 * * * /home/ubuntu/backup.sh" | crontab -
```

### **2. Manual Snapshots:**

1. Go to EC2 Console
2. Click "Volumes"
3. Select your volume
4. Actions → Create Snapshot

---

## 🌐 Add Domain Name

### **1. Allocate Elastic IP:**

1. EC2 Console → "Elastic IPs"
2. Click "Allocate Elastic IP address"
3. Click "Allocate"
4. Select the IP → Actions → Associate
5. Choose your instance

**Now your IP won't change when you restart!**

### **2. Configure DNS:**

1. **Buy domain** (Route 53, Namecheap, etc.)
2. **Create A record:**
   ```
   api.yourdomain.com → YOUR_ELASTIC_IP
   ```

### **3. Setup NGINX + SSL:**

```bash
# Install NGINX
sudo apt install -y nginx

# Configure
sudo nano /etc/nginx/sites-available/pipeline-debugger
```

Paste:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/pipeline-debugger /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

**Now accessible via:** `https://api.yourdomain.com`

---

## 🚀 Deployment Strategies

### **Option 1: Git Pull (Simple)**
```bash
ssh ubuntu@YOUR_IP
cd ~/pipeline-debugger
git pull
sudo systemctl restart pipeline-debugger
```

### **Option 2: CI/CD with GitHub Actions**

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS EC2

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to EC2
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_KEY }}
          script: |
            cd ~/pipeline-debugger
            git pull
            source backend/venv/bin/activate
            pip install -r backend/requirements.txt
            sudo systemctl restart pipeline-debugger
```

**Now every push to main auto-deploys!** 🚀

---

## 📈 Upgrade Instance Type

**As your app grows:**

1. Stop instance
2. Actions → Instance Settings → Change Instance Type
3. Choose bigger type (e.g., t3.medium)
4. Start instance

**Data is preserved!**

---

## 🐛 Troubleshooting

### **"Connection timeout"**
- Check Security Group (port 8000 open?)
- Check instance is "Running"
- Check UFW firewall: `sudo ufw status`

### **"Permission denied"**
- Check key file permissions: `chmod 400 ~/.ssh/pipeline-debugger-key.pem`
- Use correct username: `ubuntu` (not `ec2-user`)

### **"Out of memory"**
```bash
# Check memory
free -h

# Add swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📚 Useful Resources

- **EC2 Pricing:** https://aws.amazon.com/ec2/pricing/
- **Free Tier:** https://aws.amazon.com/free/
- **EC2 User Guide:** https://docs.aws.amazon.com/ec2/

---

**You're running on AWS EC2!** 🎉

More powerful and flexible than Lightsail, with room to grow!
