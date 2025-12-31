#!/bin/bash
# FractalTrader - AWS EC2 Setup Script
# Optimized for t3.micro (1GB RAM, 2 vCPU, x86_64)
# Recommended region: ap-northeast-1 (Tokyo) for low latency to Hyperliquid
#
# Run this script on your AWS EC2 instance after SSH login:
# curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/aws-setup.sh | bash

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
   ___  _      ______    ____             __
  / _ \| | /| / / __/   / __/___  ___ __ / /___ _____
 / __ | |/ |/ /\ \    _\ \/ -_)/ _ / // / __/ // / _ \
/_/ |_|__/|__/___/   /___/\__/ \_,_\_,_/\__/\_,_/ .__/
                                                /_/
EOF
echo -e "${NC}"
echo -e "${GREEN}FractalTrader AWS EC2 Setup${NC}"
echo -e "${GREEN}=============================${NC}"
echo ""

# Check if running on x86_64
ARCH=$(uname -m)
if [[ "$ARCH" != "x86_64" ]]; then
    echo -e "${RED}✗ Error: Expected x86_64, got: $ARCH${NC}"
    echo -e "${RED}  This script is for AWS EC2 (x86_64)${NC}"
    exit 1
fi

# Check available memory
TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
echo -e "${BLUE}Detected RAM: ${TOTAL_MEM}MB${NC}"

if (( TOTAL_MEM < 900 )); then
    echo -e "${RED}✗ Error: Insufficient memory (${TOTAL_MEM}MB < 900MB)${NC}"
    echo -e "${RED}  t3.micro should have ~950MB available RAM${NC}"
    exit 1
fi

if (( TOTAL_MEM < 1500 )); then
    echo -e "${YELLOW}⚠️  Low memory instance detected (${TOTAL_MEM}MB)${NC}"
    echo -e "${YELLOW}   Will configure 2GB swap for stability${NC}"
fi

# Step 1: Update system
echo -e "\n${GREEN}[1/9] Updating system...${NC}"
sudo apt-get update -qq
sudo apt-get upgrade -y -qq

# Step 2: Install Docker
echo -e "\n${GREEN}[2/9] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${YELLOW}✓ Docker already installed ($(docker --version))${NC}"
fi

# Step 3: Install Docker Compose
echo -e "\n${GREEN}[3/9] Installing Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    sudo apt-get install -y docker-compose-plugin -qq
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${YELLOW}✓ Docker Compose already installed${NC}"
fi

# Step 4: Configure swap (CRITICAL for 1GB RAM)
echo -e "\n${GREEN}[4/9] Configuring swap (2GB)...${NC}"
if [ ! -f /swapfile ]; then
    echo -e "${YELLOW}Creating swap file (this may take a minute)...${NC}"
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

    # Optimize swap settings for trading bot
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
    echo 'vm.vfs_cache_pressure=50' | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p

    echo -e "${GREEN}✓ Swap configured (2GB)${NC}"
else
    echo -e "${YELLOW}✓ Swap already exists${NC}"
fi

# Verify swap
SWAP_SIZE=$(free -h | awk 'NR==3{print $2}')
echo -e "${BLUE}  Total Swap: ${SWAP_SIZE}${NC}"

# Step 5: Configure firewall (UFW)
echo -e "\n${GREEN}[5/9] Configuring firewall...${NC}"
if ! command -v ufw &> /dev/null; then
    sudo apt-get install -y ufw -qq
fi

sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 9000/tcp  # Portainer (optional)
sudo ufw allow 8000/tcp  # Portainer edge
sudo ufw --force enable

echo -e "${GREEN}✓ Firewall configured${NC}"
echo -e "${YELLOW}  Note: AWS Security Groups should also be configured${NC}"

# Step 6: Optimize Docker for low memory
echo -e "\n${GREEN}[6/9] Optimizing Docker daemon...${NC}"
sudo mkdir -p /etc/docker

cat << 'DOCKERCONFIG' | sudo tee /etc/docker/daemon.json > /dev/null
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "5m",
    "max-file": "2"
  },
  "storage-driver": "overlay2",
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 64000,
      "Soft": 64000
    }
  }
}
DOCKERCONFIG

sudo systemctl restart docker || true
echo -e "${GREEN}✓ Docker optimized${NC}"

# Step 7: Clone repository
echo -e "\n${GREEN}[7/9] Setting up project...${NC}"
PROJECT_DIR="$HOME/FractalTrader"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  FractalTrader directory exists${NC}"
    read -p "Remove and re-clone? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
    else
        echo -e "${YELLOW}Skipping clone, using existing directory${NC}"
    fi
fi

if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Please provide your repository URL:${NC}"
    read -p "Git URL (or press Enter to skip): " GIT_URL

    if [ -n "$GIT_URL" ]; then
        git clone "$GIT_URL" "$PROJECT_DIR"
        echo -e "${GREEN}✓ Repository cloned${NC}"
    else
        echo -e "${RED}✗ Repository URL required${NC}"
        echo -e "${YELLOW}  Clone manually: git clone YOUR_URL ~/FractalTrader${NC}"
        exit 1
    fi
fi

# Step 8: Configure environment
cd "$PROJECT_DIR"

echo -e "\n${GREEN}[8/9] Configuring environment...${NC}"

if [ ! -f ".env" ]; then
    if [ -f ".env.cloud.example" ]; then
        cp .env.cloud.example .env
    else
        echo -e "${RED}✗ .env.cloud.example not found${NC}"
        exit 1
    fi

    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}Configure your bot credentials:${NC}"
    echo -e "${BLUE}========================================${NC}"

    # Interactive configuration
    echo -e "\n${BLUE}1. Trading Strategy${NC}"
    echo "   Available: liquidity_sweep, fvg_fill, bos_orderblock"
    read -p "   Strategy [liquidity_sweep]: " STRATEGY
    STRATEGY=${STRATEGY:-liquidity_sweep}
    sed -i "s/STRATEGY=.*/STRATEGY=$STRATEGY/" .env

    echo -e "\n${BLUE}2. Network${NC}"
    read -p "   Use testnet? (RECOMMENDED) [Y/n]: " USE_TESTNET
    if [[ ! $USE_TESTNET =~ ^[Nn]$ ]]; then
        sed -i "s/NETWORK=.*/NETWORK=testnet/" .env
        echo -e "   ${GREEN}✓ Using testnet${NC}"
    else
        sed -i "s/NETWORK=.*/NETWORK=mainnet/" .env
        echo -e "   ${RED}⚠️  Using MAINNET (real money!)${NC}"
    fi

    echo -e "\n${BLUE}3. Hyperliquid Private Key${NC}"
    echo "   Get testnet key from: https://app.hyperliquid-testnet.xyz"
    read -p "   Private Key: " HL_KEY
    if [ -n "$HL_KEY" ]; then
        sed -i "s|HYPERLIQUID_PRIVATE_KEY=.*|HYPERLIQUID_PRIVATE_KEY=$HL_KEY|" .env
        echo -e "   ${GREEN}✓ Key configured${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Skipped - add later: nano .env${NC}"
    fi

    echo -e "\n${BLUE}4. Telegram Notifications (optional)${NC}"
    read -p "   Configure Telegram? [y/N]: " SETUP_TELEGRAM
    if [[ $SETUP_TELEGRAM =~ ^[Yy]$ ]]; then
        echo "   Get bot token from: https://t.me/BotFather"
        read -p "   Bot Token: " TG_TOKEN
        echo "   Get chat ID from: https://t.me/userinfobot"
        read -p "   Chat ID: " TG_CHAT

        if [ -n "$TG_TOKEN" ] && [ -n "$TG_CHAT" ]; then
            sed -i "s/TELEGRAM_BOT_TOKEN=.*/TELEGRAM_BOT_TOKEN=$TG_TOKEN/" .env
            sed -i "s/TELEGRAM_CHAT_ID=.*/TELEGRAM_CHAT_ID=$TG_CHAT/" .env
            echo -e "   ${GREEN}✓ Telegram configured${NC}"
        fi
    fi

    echo -e "\n${GREEN}✓ Configuration complete${NC}"
else
    echo -e "${YELLOW}✓ .env file already exists${NC}"
fi

# Step 9: Build Docker image
echo -e "\n${GREEN}[9/9] Building Docker image...${NC}"
echo -e "${YELLOW}This may take 5-8 minutes on t3.micro...${NC}"

# Build with AWS-optimized Dockerfile
docker build -f Dockerfile.aws -t fractal-trader:aws .

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ AWS Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${BLUE}System Info:${NC}"
echo -e "  RAM: $(free -h | awk 'NR==2{print $2}')"
echo -e "  Swap: $(free -h | awk 'NR==3{print $2}')"
echo -e "  Docker: $(docker --version)"
echo -e "  Region: $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null || echo 'Unknown')"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. ${BLUE}Edit configuration (if needed):${NC}"
echo -e "   nano .env"

echo -e "\n2. ${BLUE}Start bot:${NC}"
echo -e "   docker compose -f docker-compose.aws.yml up -d"

echo -e "\n3. ${BLUE}View logs:${NC}"
echo -e "   docker compose -f docker-compose.aws.yml logs -f"

echo -e "\n4. ${BLUE}Check status:${NC}"
echo -e "   docker exec -it fractal-trader-aws python -m live.cli status"

echo -e "\n5. ${BLUE}Monitor resources:${NC}"
echo -e "   docker stats fractal-trader-aws"

echo -e "\n${YELLOW}Optional: Start Portainer (web UI)${NC}"
echo -e "  docker compose -f docker-compose.aws.yml --profile management up -d"
echo -e "  Access: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR_IP'):9000"

echo -e "\n${GREEN}Happy Trading! 🚀${NC}"
echo -e "${BLUE}AWS Tokyo + Hyperliquid = <5ms latency!${NC}"

# Remind about logout for docker group
if groups | grep -q docker; then
    :
else
    echo -e "\n${YELLOW}⚠️  IMPORTANT: Log out and log back in for Docker group changes to take effect${NC}"
    echo -e "   Then run: cd ~/FractalTrader && docker compose -f docker-compose.aws.yml up -d"
fi
