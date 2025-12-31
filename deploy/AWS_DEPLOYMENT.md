# ☁️ FractalTrader - AWS Deployment Guide

Kompletny przewodnik deployment bota FractalTrader na **Amazon Web Services (AWS)**.

**Dlaczego AWS?**
- ✅ **Najniższa latencja** do Hyperliquid (<5ms z Tokyo)
- ✅ **Enterprise reliability** (99.99% SLA)
- ✅ **Free tier** (12 miesięcy, t3.micro)
- ✅ **Łatwy setup** (prostszy niż Oracle Cloud)
- ✅ **Standardowa architektura** (x86_64)

---

## 🎯 Quick Start

**Czas setup: ~15 minut**

```bash
# 1. SSH do EC2 instance
ssh -i your-key.pem ubuntu@YOUR_IP

# 2. Run setup script
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/aws-setup.sh | bash

# 3. Start bot
cd FractalTrader
docker compose -f docker-compose.aws.yml up -d

# 4. View logs
docker compose -f docker-compose.aws.yml logs -f
```

---

## 📋 Spis Treści

1. [Utworzenie EC2 Instance](#1-utworzenie-ec2-instance)
2. [SSH Setup](#2-ssh-setup)
3. [Instalacja Bota](#3-instalacja-bota)
4. [Konfiguracja](#4-konfiguracja)
5. [Monitoring](#5-monitoring)
6. [Optymalizacja](#6-optymalizacja-dla-1gb-ram)
7. [Cost Breakdown](#7-cost-breakdown)
8. [Troubleshooting](#8-troubleshooting)
9. [iPhone Management](#9-iphone-management)

---

## 1. Utworzenie EC2 Instance

### Krok 1: Zaloguj się do AWS Console

1. Otwórz: https://console.aws.amazon.com
2. Region: **ap-northeast-1 (Tokyo)** ⚡ (najważniejsze dla low latency!)
   - Górny prawy róg → Wybierz: **Asia Pacific (Tokyo) ap-northeast-1**

### Krok 2: Launch EC2 Instance

1. **EC2 Dashboard** → **Launch Instance**

2. **Name:** `fractal-trader-production`

3. **Application and OS Images:**
   - **Ubuntu Server 22.04 LTS**
   - Architecture: **64-bit (x86_64)**
   - ✅ Free tier eligible

4. **Instance Type:**
   - **t3.micro** (1 GB RAM, 2 vCPU)
   - ✅ Free tier eligible (750 hours/month for 12 months)

   **Alternatywnie (jeśli budget pozwala):**
   - **t3.small** ($0.0208/hr = ~$15/month)
     - 2 GB RAM = więcej komfortu
     - Nie wymaga tak agresywnej optymalizacji

5. **Key Pair:**
   - Create new key pair
   - Name: `fractal-trader-key`
   - Type: **RSA**
   - Format: **.pem** (dla Mac/Linux) lub **.ppk** (dla PuTTY)
   - **Download i zapisz bezpiecznie!**

6. **Network Settings:**
   - ✅ **Allow SSH** from: **My IP** (lub Anywhere - mniej bezpieczne)
   - ✅ **Allow HTTP** (optional, dla future dashboard)
   - ✅ **Add Rule:** Custom TCP, Port **9000**, Source: My IP (dla Portainer)

7. **Configure Storage:**
   - **20 GB** gp3 (wystarczy)
   - Free tier: do 30GB

8. **Advanced Details (Optional ale WAŻNE!):**
   - **User data** (auto-run script na first boot):

   ```bash
   #!/bin/bash
   # Auto-install setup script
   apt-get update
   curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/aws-setup.sh -o /home/ubuntu/setup.sh
   chmod +x /home/ubuntu/setup.sh
   chown ubuntu:ubuntu /home/ubuntu/setup.sh
   ```

9. **Launch Instance** 🚀

### Krok 3: Zapisz Instance Details

Po utworzeniu, zapisz:
- **Public IPv4 address:** (np. 13.231.xxx.xxx)
- **Instance ID:** (np. i-0abcd1234efgh5678)

---

## 2. SSH Setup

### Mac / Linux

```bash
# 1. Set key permissions
chmod 400 ~/Downloads/fractal-trader-key.pem

# 2. SSH to instance
ssh -i ~/Downloads/fractal-trader-key.pem ubuntu@YOUR_PUBLIC_IP

# 3. (Optional) Add to ~/.ssh/config for easy access
cat >> ~/.ssh/config << EOF
Host fractal-aws
    HostName YOUR_PUBLIC_IP
    User ubuntu
    IdentityFile ~/Downloads/fractal-trader-key.pem
EOF

# Now you can just: ssh fractal-aws
```

### iPhone (Termius App)

1. **Download Termius** z App Store
2. **Import SSH Key:**
   - Keys → `+` → Import from Files
   - Wybierz `.pem` file
3. **Add Host:**
   - Hosts → `+`
   - Label: `Fractal AWS`
   - Address: `YOUR_PUBLIC_IP`
   - Username: `ubuntu`
   - Key: (wybierz imported key)
4. **Connect!** 🎉

---

## 3. Instalacja Bota

### Metoda A: Automated Setup (Recommended)

```bash
# Po SSH do instance:
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/aws-setup.sh | bash
```

Script automatycznie:
- ✅ Instaluje Docker + Docker Compose
- ✅ Konfiguruje **2GB swap** (critical dla 1GB RAM!)
- ✅ Setupuje firewall (UFW)
- ✅ Klonuje repo
- ✅ Konfiguruje `.env` (interaktywnie)
- ✅ Builduje obraz Docker (AWS-optimized)

**Czas: ~10-15 minut** (build zajmuje ~5-8 min)

### Metoda B: Manual Setup

```bash
# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Install Docker Compose
sudo apt-get install -y docker-compose-plugin

# 4. Configure swap (CRITICAL!)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 5. Optimize swap for trading bot
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# 6. Log out and back in (for docker group)
exit
# (reconnect)

# 7. Clone repo
git clone https://github.com/YOUR_REPO/FractalTrader.git
cd FractalTrader

# 8. Configure .env
cp .env.cloud.example .env
nano .env
# Fill: HYPERLIQUID_PRIVATE_KEY, STRATEGY, etc.

# 9. Build and start
docker build -f Dockerfile.aws -t fractal-trader:aws .
docker compose -f docker-compose.aws.yml up -d
```

---

## 4. Konfiguracja

### Environment Variables (.env)

```bash
# Edit .env file
nano .env
```

**Minimalna konfiguracja:**

```bash
# Strategy
STRATEGY=liquidity_sweep

# Network (ALWAYS test on testnet first!)
NETWORK=testnet

# Hyperliquid Private Key
# Get from: https://app.hyperliquid-testnet.xyz
HYPERLIQUID_PRIVATE_KEY=0x1234567890abcdef...

# Logging
LOG_LEVEL=INFO

# Risk Management
BASE_RISK_PERCENT=0.02
MAX_POSITION_PERCENT=0.05
MIN_CONFIDENCE=40
```

**Opcjonalnie: Telegram Notifications**

```bash
# Create bot: https://t.me/BotFather
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHI...

# Get chat ID: https://t.me/userinfobot
TELEGRAM_CHAT_ID=123456789
```

### Start Bot

```bash
# Start (detached)
docker compose -f docker-compose.aws.yml up -d

# View logs (live)
docker compose -f docker-compose.aws.yml logs -f

# Stop (graceful)
docker compose -f docker-compose.aws.yml down
```

### Using Makefile (Optional)

```bash
# Add alias to .bashrc for convenience
echo 'alias dca="docker compose -f docker-compose.aws.yml"' >> ~/.bashrc
source ~/.bashrc

# Now you can:
dca up -d        # Start
dca logs -f      # Logs
dca down         # Stop
dca restart      # Restart
```

---

## 5. Monitoring

### CLI Commands

```bash
# Bot status
docker exec -it fractal-trader-aws python -m live.cli status

# Performance report
docker exec -it fractal-trader-aws python -m live.cli report

# Live logs
docker compose -f docker-compose.aws.yml logs -f

# Resource usage
docker stats fractal-trader-aws

# System resources
free -h           # Memory
df -h             # Disk
htop              # CPU (install: sudo apt install htop)
```

### Portainer Web UI (Recommended!)

```bash
# Start Portainer
docker compose -f docker-compose.aws.yml --profile management up -d

# Access: http://YOUR_PUBLIC_IP:9000
# First login: set admin password
```

**Portainer Features:**
- ✅ Container management (start/stop/restart)
- ✅ Live logs viewer
- ✅ Resource graphs (CPU, RAM, Network)
- ✅ Shell access (exec into container)
- ✅ **iPhone-friendly!** 📱

### CloudWatch Monitoring (AWS Native)

AWS automatycznie monitoruje:
- CPU utilization
- Network traffic
- Disk I/O

**Setup CloudWatch Alarms:**

1. EC2 Console → Instances → Your instance
2. **Monitoring** tab
3. **Create Alarm**
   - Metric: **CPU Utilization**
   - Threshold: > 80% for 5 minutes
   - Action: SNS → Email notification

---

## 6. Optymalizacja dla 1GB RAM

### ⚠️ t3.micro ma tylko 1GB RAM!

**Problemy które możesz napotkać:**
- Container killed (OOM - Out of Memory)
- Swap thrashing (slow performance)
- Docker build failures

### ✅ Rozwiązania (już zaimplementowane)

#### 1. **Swap File (2GB)** - CRITICAL!

Setup script automatycznie konfiguruje. Verify:

```bash
# Check swap
free -h
#               total        used        free
# Mem:           950Mi       650Mi       100Mi
# Swap:          2.0Gi       200Mi       1.8Gi  ← Should see this
```

#### 2. **Docker Resource Limits**

`docker-compose.aws.yml` ma aggressive limits:

```yaml
resources:
  limits:
    memory: 768M      # Leave 256M for system
    cpus: '1.5'
```

#### 3. **Lightweight Dockerfile**

`Dockerfile.aws` skips heavy dependencies:
- ❌ matplotlib (heavy plotting)
- ❌ numba (JIT compiler)
- ❌ bottleneck (optimization library)
- ✅ Only essential trading libs

#### 4. **Python Memory Optimizations**

```bash
# Already set in Dockerfile.aws
PYTHONMALLOC=malloc
MALLOC_TRIM_THRESHOLD_=100000
```

#### 5. **Log Rotation**

```yaml
logging:
  options:
    max-size: "5m"      # Small log files
    max-file: "2"       # Keep only 2
```

### Performance Tips

```bash
# 1. Monitor memory usage
watch -n 5 free -h

# 2. Check swap usage (should be < 500MB ideally)
free -h | grep Swap

# 3. If high swap usage, restart bot periodically
crontab -e
# Add: 0 3 * * * cd ~/FractalTrader && docker compose -f docker-compose.aws.yml restart
```

### When to Upgrade to t3.small?

Consider **t3.small** (2GB RAM, ~$15/month) if:
- ❌ Bot gets OOM killed frequently
- ❌ Swap usage constantly > 1GB
- ❌ Want to enable Portainer permanently
- ❌ Planning to run multiple strategies

---

## 7. Cost Breakdown

### Free Tier (First 12 Months)

| Resource | Free Tier | Włączone? |
|----------|-----------|-----------|
| **EC2 t3.micro** | 750 hrs/month | ✅ Yes (24/7 = 720 hrs) |
| **EBS Storage** | 30 GB | ✅ Yes (using 20 GB) |
| **Data Transfer** | 100 GB/month out | ✅ Yes (bot uses ~5-10 GB) |

**Cost Year 1: $0/month** 🎉

### After Free Tier (Month 13+)

**Tokyo Region Pricing:**

| Item | Price | Monthly Cost |
|------|-------|--------------|
| **t3.micro** | $0.0104/hr | **$7.49** |
| **EBS (20GB gp3)** | $0.096/GB | **$1.92** |
| **Data Transfer** | $0.114/GB (first 10TB) | **~$1.00** |
| **Total** | | **~$10.50/month** |

**Annual cost (after year 1): ~$126/year**

### Cost Optimization

```bash
# 1. Use t3.micro (not t3.small) if possible
# Savings: $7.50/month

# 2. Reduce EBS to 10GB (if you don't need space)
# Savings: $0.96/month

# 3. Use Reserved Instance (1 year commit)
# Savings: ~30% on EC2 (~$2.50/month)

# Total optimized: ~$6/month after free tier
```

### Comparison: AWS vs Oracle Cloud

| | AWS Tokyo | Oracle Cloud |
|---|-----------|--------------|
| **Year 1** | $0 | $0 |
| **Year 2+** | ~$126/year | $0 (always!) |
| **Latency** | <5ms ⚡ | ~50ms |
| **RAM** | 1 GB | 24 GB |
| **Reliability** | 99.99% | 99.95% |
| **Setup** | Easy | Medium |

**Verdict:**
- **Testnet:** Oracle (free forever, more RAM)
- **Mainnet:** AWS Tokyo (best latency)

---

## 8. Troubleshooting

### Problem: Container keeps getting killed (OOM)

**Symptom:**
```bash
docker ps  # Container not running
docker logs fractal-trader-aws  # Shows "Killed"
```

**Solution:**

```bash
# 1. Check memory
free -h

# 2. Check if swap is active
sudo swapon --show

# 3. If no swap, create it
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 4. Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 5. Restart container
docker compose -f docker-compose.aws.yml restart

# 6. If still issues, reduce memory limit
nano docker-compose.aws.yml
# Change: memory: 512M (from 768M)
```

### Problem: Docker build fails (out of memory)

**Symptom:**
```
ERROR: failed to solve: ...
g++: fatal error: Killed signal terminated program cc1plus
```

**Solution:**

```bash
# 1. Build with swap active (ensure 2GB swap)
free -h | grep Swap

# 2. Build with reduced parallelism
docker build -f Dockerfile.aws -t fractal-trader:aws . --build-arg JOBS=1

# 3. Or use pre-built image (if available)
docker pull YOUR_REGISTRY/fractal-trader:aws
```

### Problem: High swap usage (slow performance)

**Symptom:**
```bash
free -h
# Swap: 2.0Gi   1.8Gi   200Mi  ← Most swap used
```

**Solution:**

```bash
# 1. Restart container (clear memory)
docker compose -f docker-compose.aws.yml restart

# 2. Reduce container memory if needed
nano docker-compose.aws.yml
# memory: 512M

# 3. Check for memory leaks in logs
docker logs fractal-trader-aws | grep -i "memory\|oom"

# 4. Consider upgrading to t3.small ($15/month, 2GB RAM)
```

### Problem: Cannot connect to Portainer (port 9000)

**Symptom:**
```
http://YOUR_IP:9000  # Connection refused
```

**Solution:**

```bash
# 1. Check if Portainer is running
docker ps | grep portainer

# 2. If not running, start it
docker compose -f docker-compose.aws.yml --profile management up -d

# 3. Check AWS Security Group
# EC2 Console → Security Groups → Your SG
# Inbound Rules → Should have:
#   - Type: Custom TCP
#   - Port: 9000
#   - Source: 0.0.0.0/0 (or Your IP)

# 4. Check UFW firewall
sudo ufw status
# Should show: 9000 ALLOW Anywhere

# 5. If not, allow it
sudo ufw allow 9000/tcp
```

### Problem: Bot not placing trades

**Symptom:**
```bash
docker logs fractal-trader-aws
# No trades, no errors
```

**Solution:**

```bash
# 1. Check bot status
docker exec -it fractal-trader-aws python -m live.cli status

# 2. Verify Hyperliquid connection
docker exec -it fractal-trader-aws python -c "
from hyperliquid.info import Info
info = Info('testnet')
print(info.user_state('0x0000000000000000000000000000000000000000'))
"

# 3. Check .env configuration
docker exec -it fractal-trader-aws cat .env | grep -v "^#"

# 4. Verify strategy is loaded
docker logs fractal-trader-aws | grep -i strategy

# 5. Check if testnet is active (testnet sometimes has low activity)
# Consider switching to different timeframe or strategy
```

### Problem: SSH connection timeout

**Symptom:**
```
ssh: connect to host YOUR_IP port 22: Connection timed out
```

**Solution:**

```bash
# 1. Check instance is running
# AWS Console → EC2 → Instances → Should be "running"

# 2. Check Security Group
# Should allow SSH (port 22) from Your IP

# 3. Get current public IP changed?
# AWS Console → Instance → Networking → Public IPv4

# 4. If IP changed (after stop/start), update:
ssh -i your-key.pem ubuntu@NEW_IP
```

---

## 9. iPhone Management

Pełny przewodnik: [iphone-deployment-guide.md](./iphone-deployment-guide.md)

### Quick Setup (iPhone)

1. **Install Termius** (App Store)

2. **Add AWS Host:**
   - Import `.pem` key
   - Host: `YOUR_PUBLIC_IP`
   - User: `ubuntu`

3. **Connect & Deploy:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/aws-setup.sh | bash
   ```

4. **Portainer Web UI:**
   ```bash
   docker compose -f docker-compose.aws.yml --profile management up -d
   ```
   Access: `http://YOUR_IP:9000` w Safari

5. **Telegram Notifications:**
   Configure in `.env` → Receive alerts on iPhone! 🔔

---

## 🎯 Quick Reference

### Common Commands

```bash
# Status check
docker compose -f docker-compose.aws.yml ps
docker exec -it fractal-trader-aws python -m live.cli status

# Logs
docker compose -f docker-compose.aws.yml logs -f
docker compose -f docker-compose.aws.yml logs --tail=100

# Restart
docker compose -f docker-compose.aws.yml restart

# Stop
docker compose -f docker-compose.aws.yml down

# Update code
cd ~/FractalTrader && git pull
docker compose -f docker-compose.aws.yml up -d --build

# Performance report
docker exec -it fractal-trader-aws python -m live.cli report

# Resource monitoring
docker stats fractal-trader-aws
free -h
df -h
```

### File Locations

```
/home/ubuntu/FractalTrader/         # Project root
├── .env                            # Configuration
├── logs/                           # Bot logs
├── data/                           # Data cache
├── .testnet_state.json             # Trading state
└── docker-compose.aws.yml          # Deploy config
```

---

## 🆘 Support

**Documentation:**
- AWS Guide: This file
- iPhone Guide: [iphone-deployment-guide.md](./iphone-deployment-guide.md)
- General Cloud: [CLOUD_DEPLOYMENT.md](./CLOUD_DEPLOYMENT.md)

**AWS Resources:**
- EC2 Console: https://console.aws.amazon.com/ec2
- Free Tier: https://aws.amazon.com/free
- Pricing Calculator: https://calculator.aws

**Community:**
- GitHub Issues: https://github.com/YOUR_REPO/issues

---

## ✅ Setup Checklist

- [ ] EC2 instance created (t3.micro, Tokyo region)
- [ ] SSH key downloaded and secured
- [ ] Security Group configured (ports 22, 9000)
- [ ] SSH connection successful
- [ ] Setup script executed
- [ ] Swap configured (2GB)
- [ ] .env file configured
- [ ] Docker image built
- [ ] Bot started successfully
- [ ] Logs showing activity
- [ ] (Optional) Portainer accessible
- [ ] (Optional) Telegram notifications working
- [ ] (Optional) iPhone Termius setup

---

**AWS Tokyo + Hyperliquid = <5ms latency! ⚡**

**Cost: $0 (year 1), ~$10/month (after)**

**Happy Trading! 🚀📈**
