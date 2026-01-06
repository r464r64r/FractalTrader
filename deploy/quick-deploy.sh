#!/bin/bash
# FractalTrader - Quick Deploy Script
# One-command deployment for any cloud platform
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/deploy/quick-deploy.sh | bash
#   Or:
#   ./quick-deploy.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
  ______               _        _ _______             _
 |  ____|             | |      | |__   __|           | |
 | |__ _ __ __ _  ___| |_ __ _| |  | |_ __ __ _  __| | ___ _ __
 |  __| '__/ _` |/ __| __/ _` | |  | | '__/ _` |/ _` |/ _ \ '__|
 | |  | | | (_| | (__| || (_| | |  | | | | (_| | (_| |  __/ |
 |_|  |_|  \__,_|\___|\__\__,_|_|  |_|_|  \__,_|\__,_|\___|_|

EOF
echo -e "${NC}"
echo -e "${GREEN}Cloud Deployment - Quick Start${NC}"
echo ""

# Detect architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64|amd64)
        PLATFORM="linux/amd64"
        echo -e "Architecture: ${GREEN}x86_64${NC} (AWS, DigitalOcean, Linode)"
        ;;
    aarch64|arm64)
        PLATFORM="linux/arm64"
        echo -e "Architecture: ${GREEN}ARM64${NC} (Oracle Cloud, AWS Graviton)"
        ;;
    *)
        echo -e "${RED}Unsupported architecture: $ARCH${NC}"
        exit 1
        ;;
esac

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
    echo -e "${YELLOW}⚠️  Please log out and log back in for group changes to take effect${NC}"
    echo -e "${YELLOW}   Then re-run this script${NC}"
    exit 0
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${YELLOW}Docker Compose not found. Installing...${NC}"
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
fi

# Clone or update repository
REPO_URL="${REPO_URL:-https://github.com/YOUR_USERNAME/FractalTrader.git}"
PROJECT_DIR="$HOME/FractalTrader"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Repository exists. Updating...${NC}"
    cd "$PROJECT_DIR"
    git pull
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    echo -e "Repository URL: $REPO_URL"
    read -p "Press Enter to continue or Ctrl+C to abort..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

# Setup .env if not exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.cloud.example .env

    echo -e "${BLUE}========================================${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Configure your credentials${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "Please provide the following information:"
    echo ""

    # Strategy
    echo "1. Trading Strategy"
    echo "   Available: liquidity_sweep, fvg_fill, bos_orderblock"
    read -p "   Strategy [liquidity_sweep]: " STRATEGY
    STRATEGY=${STRATEGY:-liquidity_sweep}
    sed -i "s/STRATEGY=.*/STRATEGY=$STRATEGY/" .env

    # Network
    echo ""
    echo "2. Network"
    read -p "   Use testnet? (recommended) [Y/n]: " USE_TESTNET
    if [[ ! $USE_TESTNET =~ ^[Nn]$ ]]; then
        sed -i "s/NETWORK=.*/NETWORK=testnet/" .env
        echo -e "   ${GREEN}✓ Using testnet${NC}"
    else
        sed -i "s/NETWORK=.*/NETWORK=mainnet/" .env
        echo -e "   ${RED}⚠️  Using MAINNET (real money!)${NC}"
    fi

    # Hyperliquid Key
    echo ""
    echo "3. Hyperliquid Private Key"
    echo "   Get testnet key from: https://app.hyperliquid-testnet.xyz"
    read -p "   Private Key: " HL_KEY
    if [ -n "$HL_KEY" ]; then
        sed -i "s|HYPERLIQUID_PRIVATE_KEY=.*|HYPERLIQUID_PRIVATE_KEY=$HL_KEY|" .env
        echo -e "   ${GREEN}✓ Key configured${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Skipped - you can add this later in .env${NC}"
    fi

    # Telegram (optional)
    echo ""
    echo "4. Telegram Notifications (optional)"
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

    echo ""
    echo -e "${GREEN}✓ Configuration complete${NC}"
    echo -e "${YELLOW}You can edit .env later: nano .env${NC}"
fi

# Build Docker image
echo ""
echo -e "${YELLOW}Building Docker image (this may take 5-10 minutes)...${NC}"
docker build -f Dockerfile.cloud -t fractal-trader:latest .

# Start bot
echo ""
echo -e "${YELLOW}Starting FractalTrader bot...${NC}"
docker compose -f docker-compose.cloud.yml up -d

# Wait a bit for startup
sleep 5

# Check if running
if docker ps --format '{{.Names}}' | grep -q "fractal-trader-production"; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Deployment Successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "Bot is running! 🚀"
    echo ""
    echo "Useful commands:"
    echo -e "  ${BLUE}View logs:${NC}      docker compose -f docker-compose.cloud.yml logs -f"
    echo -e "  ${BLUE}Bot status:${NC}     docker exec -it fractal-trader-production python3 -m live.cli status"
    echo -e "  ${BLUE}Performance:${NC}    docker exec -it fractal-trader-production python3 -m live.cli report"
    echo -e "  ${BLUE}Restart bot:${NC}    docker compose -f docker-compose.cloud.yml restart"
    echo -e "  ${BLUE}Stop bot:${NC}       docker compose -f docker-compose.cloud.yml down"
    echo ""
    echo "Or use Makefile shortcuts:"
    echo -e "  ${BLUE}make logs${NC}       - View logs"
    echo -e "  ${BLUE}make status${NC}     - Bot status"
    echo -e "  ${BLUE}make restart${NC}    - Restart bot"
    echo ""
    echo -e "${YELLOW}Optional: Start Portainer for web UI${NC}"
    echo -e "  make portainer"
    echo -e "  Access at: http://$(curl -s ifconfig.me):9000"
    echo ""
    echo -e "${GREEN}Happy Trading! 📈${NC}"
else
    echo ""
    echo -e "${RED}✗ Deployment failed${NC}"
    echo "Check logs:"
    echo "  docker compose -f docker-compose.cloud.yml logs"
    exit 1
fi
