# 📱 Your Personal iPhone AWS Setup Guide

**FractalTrader on AWS Free Tier - iPhone 12 Only!** ❤️

Total time: ~20 minutes | Cost: $0 for 12 months

---

## 🎯 What You'll Do (3 Steps)

1. **Create AWS EC2** (via Safari) - 5 min
2. **Connect with Termius** (SSH app) - 2 min
3. **Run automated setup** (one command) - 10 min

---

## Step 1: Create AWS Account & EC2 (Safari)

### 1.1 AWS Account (if you don't have one)
1. Open Safari: https://aws.amazon.com
2. **Create an AWS Account**
3. Enter email, password
4. Add payment card (won't be charged - 12 months free!)
5. Verify phone
6. Choose **Basic Support (Free)**

### 1.2 Launch EC2 Instance
1. Login: https://console.aws.amazon.com
2. **Change region** (top-right): **Tokyo** (ap-northeast-1) - best latency!
3. Search bar: type "EC2" → press Go
4. Orange button: **Launch Instance**

**Fill in:**
```
Name:          fractal-trader
Image:         Ubuntu Server 22.04 LTS (select from list)
Instance type: t3.micro ✅ FREE TIER ELIGIBLE
```

**Key pair:**
- Click **Create new key pair**
- Name: `fractal-key`
- Type: RSA
- Format: `.pem`
- **Download → Save to Files app!** 🔑

**Network settings:**
- ✅ Allow SSH traffic from: My IP
- Click "Add security group rule"
  - Type: Custom TCP
  - Port: 9000
  - Source: My IP
  - Description: Portainer

**Storage:**
- 20 GB gp3 (default is fine)

5. **Launch Instance** 🚀
6. Wait 2 minutes
7. **Copy Public IPv4 address** (looks like: 13.231.123.45)
   - Instance → Details → Public IPv4 address
   - Write it down or screenshot!

---

## Step 2: Install Termius & Connect

### 2.1 Install Termius
1. App Store → Search "Termius"
2. Install Termius (free version is fine)
3. Open app

### 2.2 Import SSH Key
1. Termius → **Keychain** tab (bottom)
2. Tap **+** (top right)
3. **Import**
4. Files → Downloads → Select `fractal-key.pem`
5. Label: "AWS Fractal Key" → Save

### 2.3 Add Host
1. Termius → **Hosts** tab
2. Tap **+** → **New Host**

**Fill in:**
```
Label:    AWS FractalTrader
Address:  [YOUR_PUBLIC_IP from Step 1.2]
Port:     22
Username: ubuntu
Key:      AWS Fractal Key (select from dropdown)
```

3. **Save**

### 2.4 Connect!
1. Tap on "AWS FractalTrader" host
2. Tap **Connect**
3. First time: Accept fingerprint → Yes
4. 🎉 **You're in the terminal!**

---

## Step 3: Deploy FractalTrader (Automated!)

### 3.1 Run Setup Script

In Termius terminal, copy-paste this ONE command:

```bash
curl -sSL https://raw.githubusercontent.com/r464r64r/FractalTrader/main/deploy/aws-setup.sh | bash
```

**What happens:**
- Updates system
- Installs Docker
- Creates 2GB swap (for 1GB RAM stability)
- Configures firewall
- Clones YOUR repo
- Builds Docker image (~5 min)

### 3.2 Answer Prompts

Script will ask:

**1. Git URL:**
```
https://github.com/r464r64r/FractalTrader.git
```

**2. Strategy:**
```
liquidity_sweep
```
(or just press Enter for default)

**3. Network:**
```
testnet
```
**⚠️ ALWAYS start with testnet!**

**4. Hyperliquid Private Key:**
- Open Safari: https://app.hyperliquid-testnet.xyz
- Connect wallet → Create testnet account
- Copy private key
- Paste in Termius
(If you don't have it yet, skip - you can add later)

**5. Telegram (optional):**
- Skip for now (type `n`)
- You can set up later

### 3.3 Start Bot!

After setup completes (~10 min total):

```bash
cd FractalTrader
docker compose -f docker-compose.aws.yml up -d
```

**Check it's running:**
```bash
docker compose -f docker-compose.aws.yml logs -f
```

Press `Ctrl+C` to stop watching logs (bot keeps running!)

---

## 🌐 Step 4: Web UI (Portainer)

**Manage bot from Safari!**

### Start Portainer:
In Termius:
```bash
docker compose -f docker-compose.aws.yml --profile management up -d
```

### Access in Safari:
```
http://[YOUR_PUBLIC_IP]:9000
```

**First time:**
1. Create admin password (save in iCloud Keychain!)
2. Select "Docker" environment
3. Connect to local

**Now you can:**
- ✅ View logs (visual!)
- ✅ Restart/Stop containers
- ✅ Monitor CPU/RAM
- ✅ Access terminal

**Pro tip:** Add to Home Screen!
- Safari → Share → Add to Home Screen
- Name: "FractalTrader"
- Now it's like an app! 📱

---

## ✅ Daily Operations (From iPhone!)

### Via Termius SSH:

```bash
# View logs
docker compose -f docker-compose.aws.yml logs -f

# Check bot status
docker exec -it fractal-trader-aws python -m live.cli status

# Performance report
docker exec -it fractal-trader-aws python -m live.cli report

# Restart bot
docker compose -f docker-compose.aws.yml restart

# Stop bot
docker compose -f docker-compose.aws.yml down
```

### Via Portainer (Safari):
1. Open `http://[YOUR_IP]:9000`
2. Containers → fractal-trader-aws
3. Click for: Logs, Stats, Restart, Console

### Via Telegram (if configured):
- Get notifications on your iPhone!
- Trade alerts
- Error warnings
- Daily reports

---

## 💰 Cost Breakdown

### Year 1: **$0/month** (AWS Free Tier)
- t3.micro: FREE (750 hours/month)
- 20GB storage: FREE
- Data transfer: FREE (15GB/month)

### After Year 1: **~$10.50/month**
- t3.micro (Tokyo): $7.50
- Storage (20GB): $2
- Data transfer: $1

**Still cheaper than coffee!** ☕ → 📈

---

## 🆘 Troubleshooting

### Can't connect with Termius?
1. Check Security Group in AWS Console
   - EC2 → Security Groups
   - Inbound rules → Port 22 should allow your IP
2. Check instance is running (green status)
3. Try recreating key pair

### Can't access Portainer (port 9000)?
1. AWS Security Group → Add port 9000
2. In Termius: `sudo ufw allow 9000/tcp`
3. Restart: `docker compose -f docker-compose.aws.yml --profile management restart`

### Bot not trading?
```bash
# Check logs
docker logs fractal-trader-aws | tail -50

# Verify credentials
cat ~/FractalTrader/.env | grep HYPERLIQUID_PRIVATE_KEY
```

### Out of memory?
```bash
# Check swap
free -h

# Should show 2GB swap
# If not, setup script might have failed
```

---

## 🎓 Pro Tips

### Termius Snippets (save common commands):
1. Termius → Snippets → **+**
2. Create shortcuts:
   - `logs` → `docker compose -f ~/FractalTrader/docker-compose.aws.yml logs -f`
   - `status` → `docker exec -it fractal-trader-aws python -m live.cli status`
   - `restart` → `docker compose -f ~/FractalTrader/docker-compose.aws.yml restart`

### Safari Bookmark for Quick Access:
```
http://[YOUR_IP]:9000
```
Add to Favorites → Always one tap away!

### Enable Telegram:
1. Create bot: https://t.me/BotFather
2. Get chat ID: https://t.me/userinfobot
3. Edit .env in Termius:
   ```bash
   nano ~/FractalTrader/.env
   ```
4. Add:
   ```
   TELEGRAM_BOT_TOKEN=your_token
   TELEGRAM_CHAT_ID=your_id
   ```
5. Restart bot

---

## 📚 Full Documentation

- **AWS Complete Guide:** `deploy/AWS_DEPLOYMENT.md`
- **iPhone Guide (Polish):** `deploy/iphone-deployment-guide.md`
- **Quick Start:** `deploy/AWS_QUICK_START.md`
- **Project README:** `README.md`

---

## ✅ Checklist

- [ ] AWS account created
- [ ] EC2 t3.micro launched (Tokyo)
- [ ] SSH key downloaded to Files
- [ ] Termius installed
- [ ] SSH connection working
- [ ] Setup script completed
- [ ] Docker containers running
- [ ] Logs showing activity
- [ ] Portainer accessible (optional)
- [ ] Add to Home Screen (optional)

---

## 🚀 You're Done!

**Bot is now trading 24/7 on AWS!**

- ✅ Free for 12 months
- ✅ <5ms latency (Tokyo → Hyperliquid)
- ✅ Managed from iPhone
- ✅ Auto-restart on crashes

**Monitor via:**
- 📱 Termius (terminal)
- 🌐 Portainer (web)
- 💬 Telegram (notifications)

---

**Happy Trading!** 📈❤️

**Questions?** Check full docs in `/deploy` folder or GitHub issues.

---

**Your URLs:**
- GitHub Repo: https://github.com/r464r64r/FractalTrader
- Setup Script: https://raw.githubusercontent.com/r464r64r/FractalTrader/main/deploy/aws-setup.sh
- AWS Console: https://console.aws.amazon.com
- Hyperliquid Testnet: https://app.hyperliquid-testnet.xyz
