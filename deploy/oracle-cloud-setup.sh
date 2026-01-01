#!/bin/bash
# FractalTrader - Oracle Cloud Always Free Setup Script
# Optimized for VM.Standard.A1.Flex (ARM64, 4 OCPU, 24GB RAM)
#
# Run this script on your Oracle Cloud instance after SSH login
# curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/oracle-cloud-setup.sh | bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}FractalTrader Oracle Cloud Setup${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running on ARM64
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Expected ARM64 (aarch64), got: $ARCH${NC}"
    echo -e "${YELLOW}   This script is optimized for Oracle Cloud Always Free (ARM64)${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Update system
echo -e "\n${GREEN}[1/8] Updating system...${NC}"
sudo apt-get update && sudo apt-get upgrade -y

# Step 2: Install Docker
echo -e "\n${GREEN}[2/8] Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${YELLOW}✓ Docker already installed${NC}"
fi

# Step 3: Install Docker Compose
echo -e "\n${GREEN}[3/8] Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo apt-get install -y docker-compose-plugin
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${YELLOW}✓ Docker Compose already installed${NC}"
fi

# Step 4: Configure swap (important for 1GB RAM instances)
echo -e "\n${GREEN}[4/8] Configuring swap (2GB)...${NC}"
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo -e "${GREEN}✓ Swap configured${NC}"
else
    echo -e "${YELLOW}✓ Swap already exists${NC}"
fi

# Step 5: Configure firewall (open ports for Portainer)
echo -e "\n${GREEN}[5/8] Configuring firewall...${NC}"
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 9000/tcp  # Portainer web UI
sudo ufw allow 8000/tcp  # Portainer edge agent
sudo ufw --force enable
echo -e "${GREEN}✓ Firewall configured${NC}"

# Step 6: Clone repository
echo -e "\n${GREEN}[6/8] Setting up project...${NC}"
if [ -d "FractalTrader" ]; then
    echo -e "${YELLOW}⚠️  FractalTrader directory exists${NC}"
    read -p "Remove and re-clone? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf FractalTrader
        git clone https://github.com/YOUR_USERNAME/FractalTrader.git
    fi
else
    echo -e "${YELLOW}Please clone your repository manually:${NC}"
    echo -e "  git clone https://github.com/YOUR_USERNAME/FractalTrader.git"
    echo -e "\nOr provide the git URL:"
    read -p "Git URL (or press Enter to skip): " GIT_URL
    if [ -n "$GIT_URL" ]; then
        git clone "$GIT_URL" FractalTrader
    fi
fi

# Step 7: Configure environment
if [ -d "FractalTrader" ]; then
    cd FractalTrader
    echo -e "\n${GREEN}[7/8] Configuring environment...${NC}"

    if [ ! -f ".env" ]; then
        cp .env.cloud.example .env
        echo -e "${YELLOW}⚠️  Please edit .env file with your credentials:${NC}"
        echo -e "  nano .env"
        echo -e "\nRequired fields:"
        echo -e "  - HYPERLIQUID_PRIVATE_KEY (get from Hyperliquid testnet)"
        echo -e "  - TELEGRAM_BOT_TOKEN (optional, from @BotFather)"
        echo -e "  - TELEGRAM_CHAT_ID (optional, from @userinfobot)"
    else
        echo -e "${YELLOW}✓ .env file already exists${NC}"
    fi
fi

# Step 8: Build and start
echo -e "\n${GREEN}[8/8] Building Docker image...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes on ARM64...${NC}"

# Build multi-arch image
docker build -f Dockerfile.cloud -t fractal-trader:latest .

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. Edit configuration:"
echo -e "   nano .env"
echo -e "\n2. Start bot:"
echo -e "   docker compose -f docker-compose.cloud.yml up -d"
echo -e "\n3. View logs:"
echo -e "   docker compose -f docker-compose.cloud.yml logs -f"
echo -e "\n4. Check status:"
echo -e "   docker exec -it fractal-trader-production python -m live.cli status"
echo -e "\n5. (Optional) Start Portainer for web management:"
echo -e "   docker compose -f docker-compose.cloud.yml --profile management up -d"
echo -e "   Access at: http://YOUR_IP:9000"

echo -e "\n${GREEN}Happy Trading! 🚀${NC}"
