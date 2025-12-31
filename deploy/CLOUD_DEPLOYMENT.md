# ☁️ FractalTrader - Cloud Deployment Guide

Kompletny przewodnik deployment bota FractalTrader na platformach cloud.

## 🎯 Quick Start (Oracle Cloud - Rekomendowane)

**Koszt: $0/miesiąc (Always Free)**

```bash
# 1. SSH do Oracle Cloud instance
ssh ubuntu@YOUR_IP

# 2. Uruchom setup script
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/oracle-cloud-setup.sh | bash

# 3. Skonfiguruj .env
cd FractalTrader
nano .env

# 4. Uruchom bota
docker compose -f docker-compose.cloud.yml up -d

# 5. Sprawdź logi
docker compose -f docker-compose.cloud.yml logs -f
```

**Czas setup: ~10-15 minut**

---

## 📊 Porównanie Platform Cloud

| Platforma | Koszt (1 rok) | RAM | CPU | Latencja do HL | Setup Complexity |
|-----------|---------------|-----|-----|----------------|------------------|
| **Oracle Cloud** | **$0** | 24 GB | 4 OCPU (ARM) | ~50ms | Medium |
| AWS Tokyo | $0 → $120 | 1 GB | 2 vCPU (x86) | <5ms | Easy |
| DigitalOcean | $72 | 1 GB | 1 vCPU (x86) | ~30ms | Easy |
| Linode | $60 | 1 GB | 1 vCPU (x86) | ~30ms | Easy |

### Rekomendacja:

**🏆 Oracle Cloud** (dla testnet/development):
- ✅ Najwięcej RAM (24GB) = bezpieczny zapas
- ✅ $0 na zawsze
- ✅ Idealny do testów i developmentu
- ⚠️ ARM64 architektura (wymaga multi-arch Docker)

**⚡ AWS Tokyo** (dla produkcji mainnet):
- ✅ Najniższa latencja do Hyperliquid (<5ms)
- ✅ x86_64 (standardowa architektura)
- ✅ Enterprise-grade reliability
- ❌ $10-15/miesiąc po free tier

---

## 🚀 Deployment Workflows

### Workflow 1: Oracle Cloud (ARM64)

**Architektura:** ARM64 (Ampere)
**Docker Image:** Multi-arch (linux/arm64)

```bash
# Clone repo
git clone https://github.com/YOUR_REPO/FractalTrader.git
cd FractalTrader

# Setup .env
cp .env.cloud.example .env
nano .env

# Build i deploy
docker build -f Dockerfile.cloud -t fractal-trader:latest .
docker compose -f docker-compose.cloud.yml up -d

# Monitor
docker compose -f docker-compose.cloud.yml logs -f
```

### Workflow 2: AWS / DigitalOcean (x86_64)

**Architektura:** x86_64 (AMD/Intel)
**Docker Image:** Standard linux/amd64

```bash
# Ten sam proces co Oracle, Docker automatycznie wykryje architekturę
git clone https://github.com/YOUR_REPO/FractalTrader.git
cd FractalTrader

cp .env.cloud.example .env
nano .env

docker compose -f docker-compose.cloud.yml up -d
docker compose -f docker-compose.cloud.yml logs -f
```

### Workflow 3: Multi-Architecture Build (Local)

Jeśli budujesz lokalnie na Mac M1/M2/M3 dla deployment na x86_64:

```bash
# Setup buildx
docker buildx create --use

# Build dla obu architektur
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f Dockerfile.cloud \
  -t fractal-trader:latest \
  --push \
  .

# Deploy na serwerze (pull pre-built image)
docker pull fractal-trader:latest
docker compose -f docker-compose.cloud.yml up -d
```

---

## 🔧 Konfiguracja po deployment

### 1. Environment Variables (.env)

```bash
# Minimalna konfiguracja (testnet)
STRATEGY=liquidity_sweep
NETWORK=testnet
HYPERLIQUID_PRIVATE_KEY=0x...
LOG_LEVEL=INFO

# Opcjonalnie: Telegram notifications
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Risk management
BASE_RISK_PERCENT=0.02
MAX_POSITION_PERCENT=0.05
MIN_CONFIDENCE=40
```

### 2. Resource Limits

Dostosuj w `docker-compose.cloud.yml`:

```yaml
# Dla Oracle Cloud (24GB RAM available)
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G

# Dla AWS t3.micro (1GB RAM)
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 768M
```

### 3. Logging

```yaml
# Dostosuj retention w docker-compose.cloud.yml
logging:
  options:
    max-size: "10m"   # Max rozmiar pojedynczego log file
    max-file: "3"     # Ilość rotowanych plików
```

---

## 📊 Monitoring i Management

### CLI Commands

```bash
# Status bota
docker exec -it fractal-trader-production python -m live.cli status

# Performance report
docker exec -it fractal-trader-production python -m live.cli report

# Restart bota (graceful)
docker compose -f docker-compose.cloud.yml restart

# Stop bota
docker exec -it fractal-trader-production python -m live.cli stop

# View logs (live)
docker compose -f docker-compose.cloud.yml logs -f

# Last 100 lines
docker compose -f docker-compose.cloud.yml logs --tail=100
```

### Portainer Web UI (Rekomendowane!)

```bash
# Start Portainer
docker compose -f docker-compose.cloud.yml --profile management up -d

# Access: http://YOUR_IP:9000
# Username: admin
# Password: (set on first login)
```

Features:
- ✅ Container management (start/stop/restart)
- ✅ Live logs viewer
- ✅ Resource monitoring (CPU, RAM, Network)
- ✅ Console access (exec into container)
- ✅ Volume management

---

## 🛡️ Security Checklist

### Firewall (UFW)

```bash
# Setup firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 9000/tcp  # Portainer (opcjonalnie)
sudo ufw enable

# Sprawdź status
sudo ufw status
```

### Cloud Provider Security Groups

**Oracle Cloud:**
- VCN → Security Lists → Add Ingress Rules
  - Port 22 (SSH)
  - Port 9000 (Portainer, opcjonalnie)

**AWS:**
- EC2 → Security Groups → Inbound Rules
  - Port 22 (SSH)
  - Port 9000 (Portainer, opcjonalnie)

### Best Practices

- ✅ **Nie commituj .env do git**
- ✅ **Używaj strong passwords** (Portainer, SSH keys)
- ✅ **Enable 2FA** na cloud provider
- ✅ **Regularnie aktualizuj system:**
  ```bash
  sudo apt update && sudo apt upgrade -y
  docker compose -f docker-compose.cloud.yml pull
  docker compose -f docker-compose.cloud.yml up -d
  ```
- ✅ **Backup state files:**
  ```bash
  # Cron job (daily backup)
  0 0 * * * tar -czf ~/backups/fractal-$(date +\%Y\%m\%d).tar.gz ~/FractalTrader/.testnet_state.json ~/FractalTrader/data
  ```

---

## 🐛 Troubleshooting

### Bot nie startuje

```bash
# Sprawdź logi
docker compose -f docker-compose.cloud.yml logs

# Sprawdź .env
cat .env | grep -v "^#" | grep -v "^$"

# Test połączenia Hyperliquid
docker exec -it fractal-trader-production python -c "
from hyperliquid.info import Info
info = Info('testnet')
print('Connection OK!')
"

# Restart z czystym stanem
docker compose -f docker-compose.cloud.yml down
rm .testnet_state.json
docker compose -f docker-compose.cloud.yml up -d
```

### Out of Memory (OOM)

```bash
# Sprawdź memory usage
docker stats fractal-trader-production

# Dodaj/zwiększ swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Zmniejsz resource limits
nano docker-compose.cloud.yml
# memory: 512M
docker compose -f docker-compose.cloud.yml up -d
```

### WebSocket disconnect issues

```bash
# Sprawdź network stability
ping -c 10 api.hyperliquid.xyz

# Zwiększ reconnect attempts w kodzie
# (już zaimplementowane w hyperliquid_fetcher.py)

# Check logs for connection errors
docker compose -f docker-compose.cloud.yml logs | grep -i "websocket\|connect"
```

### Image build failures (ARM64)

```bash
# ARM64 build może zajmować długo (especially vectorbt)
# Solution: Use timeout i retry

docker build -f Dockerfile.cloud -t fractal-trader:latest . --no-cache

# Alternatywnie: Build na x86 machine i push do registry
# Następnie pull na ARM64 instance
```

---

## 📈 Performance Optimization

### 1. Resource Allocation

**Oracle Cloud (24GB RAM):**
```yaml
cpus: '2.0'
memory: 4G
```

**AWS t3.micro (1GB RAM):**
```yaml
cpus: '1.0'
memory: 768M
```

### 2. Network Optimization

```bash
# Dla najniższej latencji, deploy w regionie najbliższym Hyperliquid
# Hyperliquid validators: mainly Tokyo, Singapore

# AWS: ap-northeast-1 (Tokyo)
# Oracle Cloud: ap-tokyo-1
# DigitalOcean: sgp1 (Singapore)
```

### 3. Python Optimization

```bash
# W docker-compose.cloud.yml, dodaj:
environment:
  - PYTHONOPTIMIZE=1  # Enable Python optimizations
  - PYTHONDONTWRITEBYTECODE=1  # Nie twórz .pyc files
```

---

## 🔄 Updates i Maintenance

### Weekly Maintenance

```bash
#!/bin/bash
# weekly-maintenance.sh

# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Pull latest code
cd FractalTrader
git pull

# 3. Rebuild i restart
docker compose -f docker-compose.cloud.yml build
docker compose -f docker-compose.cloud.yml up -d

# 4. Clean old images
docker image prune -f

# 5. Backup
tar -czf ~/backups/fractal-$(date +%Y%m%d).tar.gz .testnet_state.json data/
```

Dodaj do cron:
```bash
crontab -e

# Weekly maintenance (Sunday 2 AM)
0 2 * * 0 /home/ubuntu/FractalTrader/deploy/weekly-maintenance.sh
```

---

## 📱 Mobile Management

**Zobacz:** [iphone-deployment-guide.md](./iphone-deployment-guide.md)

Zarządzaj botem z iPhone przez:
- **Termius/Blink** (SSH)
- **Portainer** (web UI)
- **Telegram** (notifications)

---

## 🆘 Support

**Dokumentacja:**
- Main README: `/README.md`
- iPhone Guide: `/deploy/iphone-deployment-guide.md`
- Strategy Docs: `/strategies/README.md`

**Community:**
- GitHub Issues: https://github.com/YOUR_REPO/issues
- Discord: (jeśli masz community)

**Cloud Provider Docs:**
- Oracle Cloud: https://docs.oracle.com/cloud
- AWS: https://docs.aws.amazon.com
- DigitalOcean: https://docs.digitalocean.com

---

**Happy Trading! 🚀**
