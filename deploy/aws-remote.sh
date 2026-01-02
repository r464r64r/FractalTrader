#!/bin/bash
# FractalTrader - AWS Remote Command Wrapper
# Allows running commands on your AWS EC2 instance from Claude Code
#
# Usage:
#   ./aws-remote.sh status         # Bot status
#   ./aws-remote.sh logs           # View logs
#   ./aws-remote.sh exec "cmd"     # Run any command
#   ./aws-remote.sh deploy         # Pull latest & restart
#   ./aws-remote.sh ssh            # Interactive SSH session

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
CONFIG_FILE="${FRACTAL_AWS_CONFIG:-$HOME/.fractal-aws.env}"

# Load config
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo -e "${RED}Config not found: $CONFIG_FILE${NC}"
    echo -e "${YELLOW}Create from template:${NC}"
    echo "  cp deploy/aws-remote.env.example ~/.fractal-aws.env"
    echo "  nano ~/.fractal-aws.env"
    exit 1
fi

# Validate required vars
if [ -z "$AWS_HOST" ] || [ -z "$AWS_USER" ] || [ -z "$AWS_KEY_PATH" ]; then
    echo -e "${RED}Missing required config: AWS_HOST, AWS_USER, AWS_KEY_PATH${NC}"
    exit 1
fi

# Expand key path
AWS_KEY_PATH="${AWS_KEY_PATH/#\~/$HOME}"

# SSH command base
SSH_CMD="ssh -i $AWS_KEY_PATH -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10"
REMOTE="$AWS_USER@$AWS_HOST"
PROJECT="${REMOTE_PROJECT_PATH:-/home/ubuntu/FractalTrader}"
COMPOSE="docker compose -f ${REMOTE_COMPOSE_FILE:-docker-compose.aws.yml}"

# Helper function
remote_exec() {
    $SSH_CMD $REMOTE "$@"
}

# Commands
case "${1:-help}" in
    status)
        echo -e "${BLUE}Checking bot status on $AWS_HOST...${NC}"
        remote_exec "cd $PROJECT && docker exec -it fractal-trader-aws python -m live.cli status 2>/dev/null || echo 'Container not running'"
        ;;

    logs)
        LINES="${2:-50}"
        echo -e "${BLUE}Last $LINES log lines from $AWS_HOST...${NC}"
        remote_exec "cd $PROJECT && $COMPOSE logs --tail=$LINES"
        ;;

    logs-follow)
        echo -e "${BLUE}Following logs from $AWS_HOST (Ctrl+C to stop)...${NC}"
        remote_exec "cd $PROJECT && $COMPOSE logs -f"
        ;;

    ps)
        echo -e "${BLUE}Container status on $AWS_HOST...${NC}"
        remote_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
        ;;

    start)
        echo -e "${GREEN}Starting bot on $AWS_HOST...${NC}"
        remote_exec "cd $PROJECT && $COMPOSE up -d"
        ;;

    stop)
        echo -e "${YELLOW}Stopping bot on $AWS_HOST...${NC}"
        remote_exec "cd $PROJECT && $COMPOSE down"
        ;;

    restart)
        echo -e "${YELLOW}Restarting bot on $AWS_HOST...${NC}"
        remote_exec "cd $PROJECT && $COMPOSE restart"
        ;;

    deploy)
        echo -e "${GREEN}Deploying latest code to $AWS_HOST...${NC}"
        remote_exec "cd $PROJECT && git pull && $COMPOSE up -d --build"
        ;;

    pull)
        echo -e "${BLUE}Pulling latest code on $AWS_HOST...${NC}"
        remote_exec "cd $PROJECT && git pull"
        ;;

    report)
        echo -e "${BLUE}Performance report from $AWS_HOST...${NC}"
        remote_exec "cd $PROJECT && docker exec -it fractal-trader-aws python -m live.cli report 2>/dev/null || echo 'Container not running'"
        ;;

    resources)
        echo -e "${BLUE}System resources on $AWS_HOST...${NC}"
        remote_exec "echo '=== Memory ===' && free -h && echo -e '\n=== Disk ===' && df -h / && echo -e '\n=== Docker Stats ===' && docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}' 2>/dev/null || echo 'No containers'"
        ;;

    exec)
        shift
        echo -e "${BLUE}Executing on $AWS_HOST: $*${NC}"
        remote_exec "cd $PROJECT && $*"
        ;;

    ssh)
        echo -e "${BLUE}Connecting to $AWS_HOST...${NC}"
        $SSH_CMD $REMOTE
        ;;

    test)
        echo -e "${BLUE}Testing connection to $AWS_HOST...${NC}"
        if remote_exec "echo 'Connected to $(hostname) - $(date)'" 2>/dev/null; then
            echo -e "${GREEN}Connection successful!${NC}"
        else
            echo -e "${RED}Connection failed!${NC}"
            exit 1
        fi
        ;;

    info)
        echo -e "${BLUE}Remote Server Info:${NC}"
        echo -e "  Host: $AWS_HOST"
        echo -e "  User: $AWS_USER"
        echo -e "  Key:  $AWS_KEY_PATH"
        echo -e "  Path: $PROJECT"
        ;;

    help|*)
        echo -e "${BLUE}FractalTrader AWS Remote Control${NC}"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  status       - Show bot trading status"
        echo "  logs [n]     - Show last n log lines (default: 50)"
        echo "  logs-follow  - Follow logs in real-time"
        echo "  ps           - Show container status"
        echo "  start        - Start the bot"
        echo "  stop         - Stop the bot"
        echo "  restart      - Restart the bot"
        echo "  deploy       - Pull latest code and restart"
        echo "  pull         - Pull latest code (no restart)"
        echo "  report       - Show performance report"
        echo "  resources    - Show system resources (RAM, disk, docker)"
        echo "  exec \"cmd\"   - Execute arbitrary command"
        echo "  ssh          - Open interactive SSH session"
        echo "  test         - Test SSH connection"
        echo "  info         - Show connection info"
        echo ""
        echo "Config: $CONFIG_FILE"
        ;;
esac
