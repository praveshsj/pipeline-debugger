# ☁️ AWS Deployment Guide - Complete

Everything you need to deploy Pipeline Debugger on AWS.

---

## 🎯 Which AWS Service to Use?

### **Quick Decision Tree:**

```
Do you want the simplest option?
├─ Yes → Lightsail ($5/month) ⭐⭐⭐
└─ No
    ├─ Want FREE for 12 months? → EC2 Free Tier ⭐⭐
    ├─ Want zero server management? → Elastic Beanstalk ⭐
    └─ Want containers? → ECS/Fargate
```

---

## 📊 Service Comparison

| Service | Cost | Setup Time | Complexity | Best For |
|---------|------|------------|------------|----------|
| **Lightsail** | $5/mo | 10 min | ⭐ Easy | Getting started, small apps |
| **EC2 Free Tier** | Free (1yr) | 15 min | ⭐⭐ Medium | Learning AWS, development |
| **EC2 Paid** | $8-30/mo | 15 min | ⭐⭐ Medium | Production apps |
| **Elastic Beanstalk** | $15/mo+ | 20 min | ⭐⭐⭐ Hard | Hands-off deployment |
| **ECS Fargate** | $20/mo+ | 30 min | ⭐⭐⭐⭐ Very Hard | Microservices, containers |

---

## 🚀 Recommended Path

### **For You (Learning + Building):**

**Start:** AWS Lightsail ($5/month)
- Simplest setup
- Fixed cost (no surprises)
- Learn basics

**Then:** Migrate to EC2
- When you need more power
- When you're comfortable with AWS
- Easy to export from Lightsail

**Finally:** Production with ECS/RDS
- When you're scaling
- When you need high availability
- When you have users

---

## 💰 Complete Cost Breakdown

### **Option 1: Lightsail (Recommended)**

```
Lightsail Instance ($5/mo)
  ├─ 512MB RAM, 1 vCPU
  ├─ 20GB SSD
  ├─ 1TB Transfer
  └─ Includes: PostgreSQL, Redis, App

Optional Additions:
  ├─ Static IP: FREE
  ├─ Snapshots: $1/snapshot/mo
  ├─ Managed DB: +$15/mo
  └─ Domain: $12/year

TOTAL: $5-7/month
```

### **Option 2: EC2 Free Tier**

```
First Year (FREE):
  ├─ t2.micro: 750 hours/mo
  ├─ 30GB Storage: FREE
  ├─ 15GB Transfer: FREE
  └─ TOTAL: $0/month!

After Year 1:
  ├─ t2.micro: $8/mo
  ├─ OR t3.small: $15/mo
  └─ Storage: $2/mo
  
TOTAL: $0 → $10-17/month
```

### **Option 3: Full Production Stack**

```
EC2 t3.medium ($30/mo)
RDS PostgreSQL ($15/mo)
ElastiCache Redis ($15/mo)
Load Balancer ($16/mo)
Route 53 ($0.50/mo)
CloudWatch ($5/mo)

TOTAL: ~$80/month
```

---

## 📖 Setup Guides

I've created detailed guides for each option:

### 1. **AWS Lightsail** (START HERE!) ⭐
- **File:** `AWS_LIGHTSAIL.md`
- **Time:** 10-15 minutes
- **Cost:** $5/month
- **Difficulty:** Easy

### 2. **AWS EC2**
- **File:** `AWS_EC2.md`
- **Time:** 15-20 minutes
- **Cost:** Free (12 months) then $8-15/month
- **Difficulty:** Medium

---

## 🎓 What You'll Learn

### **Using AWS Lightsail:**
- ✅ Basic cloud deployment
- ✅ SSH and remote servers
- ✅ Linux system administration
- ✅ Database management
- ✅ Networking basics

### **Using AWS EC2:**
- ✅ Everything above, plus:
- ✅ Security groups
- ✅ Elastic IPs
- ✅ EBS volumes
- ✅ CloudWatch monitoring
- ✅ IAM roles

### **Production Deployment:**
- ✅ Everything above, plus:
- ✅ Load balancing
- ✅ Auto-scaling
- ✅ CI/CD pipelines
- ✅ High availability
- ✅ Disaster recovery

---

## 🔧 Development Workflow

### **Method 1: Local → AWS** (Recommended)

```
Your Mac:
  ├─ Write code
  ├─ Test locally (optional)
  ├─ Commit to GitHub
  └─ Push

AWS Server:
  ├─ SSH in
  ├─ Git pull
  └─ Restart service
```

### **Method 2: Direct AWS Development**

```
Your Mac:
  └─ VS Code with Remote SSH
      ├─ Connect to AWS
      ├─ Edit files directly
      └─ Auto-sync
```

**Setup VS Code Remote SSH:**

1. Install "Remote - SSH" extension
2. Click green icon (bottom left)
3. "Connect to Host"
4. Enter: `ubuntu@YOUR_AWS_IP`
5. Select your SSH key
6. **Edit code directly on AWS!** ✨

---

## 🚀 Deployment Automation

### **Simple Deployment Script:**

Create `deploy.sh` on your Mac:

```bash
#!/bin/bash

echo "🚀 Deploying to AWS..."

# Push to GitHub
git add .
git commit -m "Deploy: $(date)"
git push

# Deploy to AWS
ssh -i ~/.ssh/your-key.pem ubuntu@YOUR_IP << 'EOF'
  cd ~/pipeline-debugger
  git pull
  source backend/venv/bin/activate
  pip install -r backend/requirements.txt
  alembic upgrade head
  sudo systemctl restart pipeline-debugger
EOF

echo "✅ Deployment complete!"
echo "🌐 https://YOUR_IP:8000/docs"
```

**Use it:**
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## 🔒 Security Best Practices

### **Must Do:**

1. **Change Default Passwords**
   ```bash
   sudo passwd ubuntu
   ```

2. **Setup Firewall**
   ```bash
   sudo ufw enable
   sudo ufw allow 22    # SSH
   sudo ufw allow 8000  # API
   ```

3. **Disable Password Auth (use keys only)**
   ```bash
   sudo nano /etc/ssh/sshd_config
   # Set: PasswordAuthentication no
   sudo systemctl restart sshd
   ```

4. **Use Environment Variables**
   - Never commit .env to git
   - Never hardcode API keys

5. **Keep System Updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### **Should Do:**

6. **Setup HTTPS** (with Let's Encrypt)
7. **Enable CloudWatch Logging**
8. **Setup Automated Backups**
9. **Use IAM Roles** (not root)
10. **Enable MFA** on AWS account

---

## 📊 Monitoring Your App

### **Basic Monitoring:**

```bash
# SSH into server
ssh ubuntu@YOUR_IP

# Check app status
sudo systemctl status pipeline-debugger

# View logs
sudo journalctl -u pipeline-debugger -f

# Check resources
htop                    # CPU, memory
df -h                   # Disk space
netstat -tuln          # Network connections
```

### **AWS CloudWatch:**

1. Go to CloudWatch console
2. View metrics:
   - CPU Usage
   - Network Traffic
   - Disk I/O

3. Set up alarms:
   - CPU > 80% → email alert
   - Disk > 90% → email alert

---

## 💾 Backup Strategy

### **Database Backups:**

```bash
# Daily backup script
cat > ~/backup-db.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump -U dbuser pipeline_debugger > ~/backups/db-$DATE.sql
# Keep only last 7 days
find ~/backups -name "db-*.sql" -mtime +7 -delete
EOF

chmod +x ~/backup-db.sh

# Schedule daily at 2 AM
echo "0 2 * * * ~/backup-db.sh" | crontab -
```

### **Full Server Snapshots:**

**Lightsail:**
- Console → Snapshots → Create snapshot
- $1/snapshot/month

**EC2:**
- Console → Volumes → Create snapshot
- $0.05/GB/month

---

## 🆙 Scaling Your App

### **When to Scale:**

**Scale UP (Vertical)** when:
- CPU constantly > 80%
- Memory constantly > 90%
- Response times slow

**Scale OUT (Horizontal)** when:
- Traffic spikes unpredictably
- Need high availability
- Want zero-downtime deploys

### **How to Scale:**

**Lightsail → EC2:**
1. Create snapshot
2. Export to EC2
3. Launch larger instance type

**Single EC2 → Multiple EC2:**
1. Create AMI
2. Setup Load Balancer
3. Launch Auto Scaling Group

---

## 🌐 Adding a Domain

### **Buy Domain:**
- **AWS Route 53:** $12/year
- **Namecheap:** $10/year
- **Google Domains:** $12/year

### **Point to AWS:**

**For Lightsail:**
1. Create static IP (free)
2. Add DNS record: `api.yourdomain.com` → Static IP

**For EC2:**
1. Allocate Elastic IP (free when attached)
2. Add DNS record: `api.yourdomain.com` → Elastic IP

### **Enable HTTPS:**

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get free SSL
sudo certbot --nginx -d api.yourdomain.com

# Auto-renews every 90 days!
```

---

## 🐛 Common Issues

### **"Can't connect to AWS instance"**
✅ Check security group (port 22 open?)
✅ Use correct key file
✅ Use correct username (`ubuntu` not `ec2-user`)

### **"Server stops when I close terminal"**
✅ Use systemd service (see guides)
✅ Or use `screen` or `tmux`

### **"Running out of disk space"**
```bash
# Check space
df -h

# Clean up
sudo apt autoremove -y
sudo apt clean

# Or resize volume (EC2):
# 1. Stop instance
# 2. Modify volume size
# 3. Extend filesystem
```

### **"High costs unexpectedly"**
✅ Check CloudWatch metrics
✅ Look for data transfer charges
✅ Set up billing alerts
✅ Use cost explorer

---

## 📚 Helpful AWS Resources

**Documentation:**
- Lightsail Docs: https://lightsail.aws.amazon.com/ls/docs
- EC2 User Guide: https://docs.aws.amazon.com/ec2/
- AWS CLI Reference: https://docs.aws.amazon.com/cli/

**Tutorials:**
- AWS Getting Started: https://aws.amazon.com/getting-started/
- AWS Free Tier: https://aws.amazon.com/free/

**Cost Management:**
- Cost Explorer: https://console.aws.amazon.com/cost-management/
- Pricing Calculator: https://calculator.aws/

---

## 🎯 Your Next Steps

### **Right Now (15 minutes):**

1. **Choose your AWS service** (I recommend Lightsail)
2. **Create AWS account** (if you don't have one)
3. **Follow setup guide**:
   - Lightsail: See `AWS_LIGHTSAIL.md`
   - EC2: See `AWS_EC2.md`

### **This Week:**

4. **Deploy your app**
5. **Test all endpoints**
6. **Set up domain** (optional)
7. **Enable HTTPS** (recommended)

### **This Month:**

8. **Build new features**
9. **Set up monitoring**
10. **Configure backups**
11. **Optimize costs**

---

## ✅ Pre-Launch Checklist

Before going live:

- [ ] Environment variables set correctly
- [ ] Database migrations run
- [ ] HTTPS enabled (if using domain)
- [ ] Firewall configured
- [ ] Backups automated
- [ ] Monitoring enabled
- [ ] Logs accessible
- [ ] Health checks working
- [ ] Documentation updated
- [ ] Cost alerts set

---

## 💬 Need Help?

**Tell me:**
1. Which AWS service you chose
2. Where you're stuck
3. Any error messages

I'll help you debug! 🚀

---

**Ready to deploy?** Pick Lightsail or EC2 and follow the guide! 🎉
