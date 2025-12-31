# 🚀 FractalTrader Cloud Deployment

Wszystkie pliki i instrukcje potrzebne do deploymentu FractalTrader w chmurze.

## 📁 Struktura

```
deploy/
├── README.md                      # Ten plik
├── CLOUD_DEPLOYMENT.md           # Pełny przewodnik deployment
├── iphone-deployment-guide.md    # Przewodnik deployment z iPhone
├── oracle-cloud-setup.sh         # Setup script dla Oracle Cloud
├── quick-deploy.sh               # Szybki deployment (one-liner)
└── health-check.sh               # Health monitoring script
```

## ⚡ Quick Start

### Metoda 1: Quick Deploy (Rekomendowane)

Najprostszy sposób - jeden command:

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/quick-deploy.sh | bash
```

Ten script:
- ✅ Wykrywa architekturę (ARM64/x86_64)
- ✅ Instaluje Docker (jeśli potrzeba)
- ✅ Klonuje repo
- ✅ Konfiguruje .env (interaktywnie)
- ✅ Builduje i startuje bota

**Czas: ~10-15 minut**

### Metoda 2: Manual Setup

Dla większej kontroli:

```bash
# 1. Sklonuj repo
git clone https://github.com/YOUR_REPO/FractalTrader.git
cd FractalTrader

# 2. Skonfiguruj .env
cp .env.cloud.example .env
nano .env  # Wypełnij credentials

# 3. Użyj Makefile
make setup   # Setup environment
make build   # Build Docker image
make start   # Start bot

# 4. Monitor
make logs    # View logs
make status  # Bot status
```

### Metoda 3: Oracle Cloud Specific

Dla Oracle Cloud Always Free (ARM64):

```bash
curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/oracle-cloud-setup.sh | bash
```

Ten script dodatkowo:
- ✅ Konfiguruje swap (2GB)
- ✅ Setupuje firewall (UFW)
- ✅ Otwiera porty dla Portainer

## 📚 Dokumentacja

### Podstawy

- **[CLOUD_DEPLOYMENT.md](./CLOUD_DEPLOYMENT.md)** - Pełny przewodnik deployment
  - Porównanie platform cloud
  - Deployment workflows
  - Monitoring i troubleshooting
  - Performance optimization

- **[iphone-deployment-guide.md](./iphone-deployment-guide.md)** - Deploy z iPhone
  - SSH przez Termius/Blink
  - Portainer web UI
  - GitHub Actions CI/CD
  - Mobile workflow tips

### Narzędzia

- **oracle-cloud-setup.sh** - Setup dla Oracle Cloud
  - Auto-install Docker
  - Configure swap i firewall
  - Clone i setup projektu

- **quick-deploy.sh** - Universal quick deploy
  - Działa na wszystkich platformach
  - Interaktywna konfiguracja
  - Auto-detect architektury

- **health-check.sh** - Monitoring script
  - Container health check
  - Memory/disk monitoring
  - Auto-restart on failure
  - Telegram/email alerts

## 🎯 Wybór Platformy Cloud

| Platforma | RAM | CPU | Koszt (rok 1) | Koszt (długo) | Best For |
|-----------|-----|-----|---------------|---------------|----------|
| **Oracle Cloud** | 24GB | 4 ARM | $0 | $0 | **Testnet, Development** |
| AWS Tokyo | 1GB | 2 x86 | $0 | $120 | **Mainnet, Low Latency** |
| DigitalOcean | 1-2GB | 1 x86 | $72 | $72 | **Simple Setup** |
| Linode | 1-2GB | 1 x86 | $60 | $60 | **Simple Setup** |

### Rekomendacje

**Testnet / Development:**
```
Platform: Oracle Cloud Always Free
Cost: $0/miesiąc
RAM: 24GB (overkill, ale za darmo!)
```

**Mainnet / Production:**
```
Platform: AWS Tokyo (ap-northeast-1)
Cost: ~$12/miesiąc
Latency: <5ms do Hyperliquid
```

## 🛠️ Common Commands

### Makefile Shortcuts

```bash
# Setup
make setup          # First time setup
make build          # Build Docker image

# Operations
make start          # Start bot
make stop           # Stop bot
make restart        # Restart bot

# Monitoring
make logs           # View logs (follow)
make logs-tail      # Last 100 lines
make status         # Bot status
make report         # Performance report

# Management
make portainer      # Start Portainer (port 9000)
make shell          # Shell into container
make clean          # Cleanup Docker resources
```

### Docker Compose

```bash
# Full commands (if not using Makefile)
docker compose -f docker-compose.cloud.yml up -d      # Start
docker compose -f docker-compose.cloud.yml down       # Stop
docker compose -f docker-compose.cloud.yml logs -f    # Logs
docker compose -f docker-compose.cloud.yml restart    # Restart
```

### Bot CLI

```bash
# Inside container
docker exec -it fractal-trader-production python -m live.cli status
docker exec -it fractal-trader-production python -m live.cli report
docker exec -it fractal-trader-production python -m live.cli stop
```

## 📱 iPhone Management

Zarządzaj botem z iPhone:

1. **SSH Apps** (Termius, Blink)
   - Pełna kontrola terminala
   - Run all commands

2. **Portainer** (Web UI)
   - http://YOUR_IP:9000
   - Container management
   - Logs viewer
   - Resource monitoring

3. **Telegram** (Notifications)
   - Trade alerts
   - Error notifications
   - Daily reports

Zobacz: [iphone-deployment-guide.md](./iphone-deployment-guide.md)

## 🔍 Health Monitoring

### Automated Health Checks

```bash
# Copy health check script
cp deploy/health-check.sh ~/health-check.sh
chmod +x ~/health-check.sh

# Add to cron (check every 5 minutes)
crontab -e
# Add: */5 * * * * /home/ubuntu/health-check.sh

# Configure alerts
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

Script checks:
- ✅ Container running
- ✅ Bot process active
- ✅ Memory usage (<90%)
- ✅ Disk space (<90%)
- ✅ Recent errors

Auto-restarts on failure + sends alerts!

## 🆘 Troubleshooting

### Bot nie startuje

```bash
# Check logs
make logs

# Check environment
cat .env | grep -v "^#"

# Test Hyperliquid connection
docker exec -it fractal-trader-production python -c "
from hyperliquid.info import Info
info = Info('testnet')
print('Connection OK!')
"
```

### Out of Memory

```bash
# Add swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Port conflicts

```bash
# Check what's using port
sudo netstat -tulpn | grep 9000

# Kill process
sudo kill -9 PID

# Or change port in docker-compose.cloud.yml
```

Więcej: [CLOUD_DEPLOYMENT.md - Troubleshooting](./CLOUD_DEPLOYMENT.md#-troubleshooting)

## 🔐 Security

### Checklist

- [ ] `.env` nie jest w git (sprawdź .gitignore)
- [ ] Strong password dla Portainer
- [ ] SSH keys zamiast passwords
- [ ] Firewall enabled (UFW)
- [ ] Tylko potrzebne porty otwarte (22, 9000)
- [ ] 2FA enabled na cloud provider
- [ ] Regularnie update system
- [ ] Backup `.testnet_state.json`

### Firewall Setup

```bash
# Basic firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 9000/tcp  # Portainer (optional)
sudo ufw enable
```

## 📈 Performance Tips

### Resource Optimization

```yaml
# docker-compose.cloud.yml

# Dla Oracle Cloud (24GB RAM)
memory: 4G
cpus: 2.0

# Dla AWS t3.micro (1GB RAM)
memory: 768M
cpus: 1.0
```

### Network Optimization

Deploy w regionie najbliższym Hyperliquid:
- **AWS:** ap-northeast-1 (Tokyo)
- **Oracle Cloud:** ap-tokyo-1
- **DigitalOcean:** sgp1 (Singapore)

### Python Optimization

```yaml
environment:
  - PYTHONOPTIMIZE=1
  - PYTHONDONTWRITEBYTECODE=1
```

## 🔄 Updates

### Weekly Maintenance

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Pull latest code
cd FractalTrader && git pull

# Rebuild and restart
make build
make restart

# Clean old images
docker image prune -f
```

Lub użyj automated cron job w [CLOUD_DEPLOYMENT.md](./CLOUD_DEPLOYMENT.md)

## 📞 Support

**Dokumentacja:**
- Cloud Deployment: [CLOUD_DEPLOYMENT.md](./CLOUD_DEPLOYMENT.md)
- iPhone Guide: [iphone-deployment-guide.md](./iphone-deployment-guide.md)
- Main README: [/README.md](../README.md)

**Resources:**
- Oracle Cloud Docs: https://docs.oracle.com/cloud
- Docker Docs: https://docs.docker.com
- Hyperliquid Docs: https://hyperliquid.gitbook.io

**Community:**
- GitHub Issues: https://github.com/YOUR_REPO/issues

---

**Powodzenia w deploymencie! 🚀**

Oracle Cloud Always Free + FractalTrader = 24/7 trading za $0! 💪
