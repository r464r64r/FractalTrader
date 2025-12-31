# ⚡ AWS Quick Start - FractalTrader

**Najszybszy sposób na deployment na AWS. 15 minut od zera do działającego bota!**

---

## 🎯 Wariant 1: Complete Beginner (Step-by-Step)

### Krok 1: Utwórz AWS Account (5 min)

1. https://aws.amazon.com → **Create an AWS Account**
2. Podaj email, password
3. Podaj dane karty (nie zostanie obciążona przez 12 miesięcy!)
4. Verify phone number
5. Choose **Basic Support (Free)**

### Krok 2: Launch EC2 Instance (5 min)

1. **Login**: https://console.aws.amazon.com
2. **Region** (góra prawa): Wybierz **Tokyo** (ap-northeast-1)
3. Search bar: wpisz "EC2" → Enter
4. **Launch Instance** (pomarańczowy button)

**Konfiguracja:**
```
Name:          fractal-trader
Image:         Ubuntu Server 22.04 LTS
Instance type: t3.micro (✅ Free tier eligible)
Key pair:      Create new → "fractal-key" → Download .pem
Network:       ✅ Allow SSH from My IP
               ✅ Add rule: Custom TCP, Port 9000, My IP
Storage:       20 GB gp3
```

5. **Launch Instance** 🚀
6. **Zapisz Public IPv4 address** (np. 13.231.123.45)

### Krok 3: SSH Connect (3 min)

**Mac/Linux:**
```bash
# 1. Set permissions
chmod 400 ~/Downloads/fractal-key.pem

# 2. Connect
ssh -i ~/Downloads/fractal-key.pem ubuntu@YOUR_PUBLIC_IP
```

**Windows:**
- Download **PuTTY**
- Use **PuTTYgen** to convert .pem to .ppk
- Connect z PuTTY

**iPhone:**
- Download **Termius** z App Store
- Import .pem key
- Add host (YOUR_PUBLIC_IP, user: ubuntu)
- Connect

### Krok 4: Deploy Bot (5 min)

```bash
# One command - setup wszystko!
curl -sSL https://raw.githubusercontent.com/r464r64r/FractalTrader/main/deploy/aws-setup.sh | bash
```

Script zapyta o:
1. **Git URL** (Twoje repo lub fork)
2. **Strategy**: `liquidity_sweep` (recommended)
3. **Network**: testnet (ZAWSZE zacznij od testnet!)
4. **Hyperliquid Key**: Get from https://app.hyperliquid-testnet.xyz
5. **Telegram** (optional): Bot token i chat ID

**Wait ~5-8 minut** (Docker build)

### Krok 5: Start! (1 min)

```bash
cd FractalTrader
docker compose -f docker-compose.aws.yml up -d

# View logs
docker compose -f docker-compose.aws.yml logs -f
```

✅ **DONE! Bot is trading!** 🎉

---

## 🚀 Wariant 2: Experienced User (One-Liner)

Jeśli znasz AWS i masz już EC2 instance:

```bash
# SSH to instance, then:
curl -sSL https://raw.githubusercontent.com/r464r64r/FractalTrader/main/deploy/aws-setup.sh | bash && \
cd FractalTrader && \
docker compose -f docker-compose.aws.yml up -d
```

**Total time: ~10 minut**

---

## 📱 Wariant 3: iPhone Only

1. **Setup EC2 przez Safari:**
   - Login: https://console.aws.amazon.com
   - Launch instance (jak wyżej)
   - Download .pem key do Files app

2. **Termius App:**
   - Import key
   - Add host
   - Connect

3. **Deploy:**
   ```bash
   curl -sSL https://raw.githubusercontent.com/r464r64r/FractalTrader/main/deploy/aws-setup.sh | bash
   cd FractalTrader
   docker compose -f docker-compose.aws.yml up -d
   ```

4. **Portainer (Web UI):**
   ```bash
   docker compose -f docker-compose.aws.yml --profile management up -d
   ```
   Access: `http://YOUR_IP:9000` w Safari 📱

---

## ⚙️ Post-Deployment

### Check Status

```bash
# Bot status
docker exec -it fractal-trader-aws python -m live.cli status

# Live logs
docker compose -f docker-compose.aws.yml logs -f

# Performance report
docker exec -it fractal-trader-aws python -m live.cli report
```

### Common Operations

```bash
# Restart bot
docker compose -f docker-compose.aws.yml restart

# Stop bot
docker compose -f docker-compose.aws.yml down

# Update code
cd FractalTrader && git pull
docker compose -f docker-compose.aws.yml up -d --build

# Check resources
docker stats fractal-trader-aws
free -h
```

---

## 💰 Cost

**Year 1 (Free Tier):** $0/month

**After Year 1:**
- t3.micro Tokyo: ~$7.50/month
- Storage (20GB): ~$2/month
- Data transfer: ~$1/month
- **Total: ~$10.50/month**

---

## 🆘 Troubleshooting

### Bot keeps getting killed (OOM)

```bash
# Check swap
free -h | grep Swap

# If no swap, setup script should have created it
# If missing, run:
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Can't connect to Portainer (port 9000)

```bash
# 1. Check AWS Security Group
# EC2 Console → Security Groups
# Inbound: Port 9000 should be open

# 2. Check UFW
sudo ufw allow 9000/tcp

# 3. Restart Portainer
docker compose -f docker-compose.aws.yml --profile management restart
```

### Bot not trading

```bash
# Check logs for errors
docker logs fractal-trader-aws | tail -50

# Verify Hyperliquid connection
docker exec -it fractal-trader-aws python -c "
from hyperliquid.info import Info
info = Info('testnet')
print('Connection OK!')
"

# Check .env
cat .env | grep HYPERLIQUID_PRIVATE_KEY
```

**Full troubleshooting:** [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md#8-troubleshooting)

---

## 📚 Next Steps

### 1. Setup Monitoring

```bash
# Install health check cron
cp deploy/health-check.sh ~/
chmod +x ~/health-check.sh

# Edit paths
nano ~/health-check.sh
# Change: /path/to/docker-compose.aws.yml → ~/FractalTrader/docker-compose.aws.yml

# Add to cron (check every 5 min)
crontab -e
# Add: */5 * * * * ~/health-check.sh
```

### 2. Enable Telegram Notifications

```bash
# Edit .env
nano .env

# Add:
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id

# Restart
docker compose -f docker-compose.aws.yml restart
```

### 3. Portainer Web UI

```bash
# Start Portainer
docker compose -f docker-compose.aws.yml --profile management up -d

# Access: http://YOUR_IP:9000
# Set admin password
# Manage containers from browser! 🌐
```

### 4. iPhone Management

- **Termius:** Full terminal access
- **Portainer:** Web UI (Safari)
- **Telegram:** Notifications

Full guide: [iphone-deployment-guide.md](./iphone-deployment-guide.md)

---

## 🎓 Tips

### Aliases (Save Time)

```bash
# Add to ~/.bashrc
echo 'alias dca="docker compose -f ~/FractalTrader/docker-compose.aws.yml"' >> ~/.bashrc
echo 'alias ftlogs="docker compose -f ~/FractalTrader/docker-compose.aws.yml logs -f"' >> ~/.bashrc
echo 'alias ftstatus="docker exec -it fractal-trader-aws python -m live.cli status"' >> ~/.bashrc
source ~/.bashrc

# Now:
dca up -d           # Start
ftlogs              # Logs
ftstatus            # Status
dca restart         # Restart
```

### Auto-Start on Reboot

```bash
# Already configured in docker-compose.aws.yml
restart: unless-stopped

# Verify:
docker ps
# Should show: STATUS: Up ... (restart: unless-stopped)
```

### Backup State

```bash
# Backup trading state (daily)
crontab -e
# Add:
0 3 * * * tar -czf ~/backups/fractal-$(date +\%Y\%m\%d).tar.gz -C ~/FractalTrader .testnet_state.json data/

# Create backup dir
mkdir -p ~/backups
```

---

## ✅ Checklist

- [ ] AWS account created
- [ ] EC2 instance running (Tokyo, t3.micro)
- [ ] SSH connection working
- [ ] Setup script completed
- [ ] Bot started
- [ ] Logs showing activity
- [ ] Status command works
- [ ] (Optional) Portainer accessible
- [ ] (Optional) Telegram working

---

## 📖 Full Documentation

- **AWS Complete Guide:** [AWS_DEPLOYMENT.md](./AWS_DEPLOYMENT.md)
- **iPhone Management:** [iphone-deployment-guide.md](./iphone-deployment-guide.md)
- **General Cloud:** [CLOUD_DEPLOYMENT.md](./CLOUD_DEPLOYMENT.md)

---

**AWS Tokyo + FractalTrader = <5ms latency! ⚡**

**Quick. Reliable. Free for 12 months. 🚀**
