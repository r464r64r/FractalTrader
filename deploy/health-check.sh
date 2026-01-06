#!/bin/bash
# FractalTrader - Health Check Script
# Monitor bot health and send alerts if issues detected
#
# Usage:
#   ./health-check.sh
#   Or add to cron: */5 * * * * /path/to/health-check.sh

set -e

# Configuration
CONTAINER_NAME="fractal-trader-production"
ALERT_EMAIL="${ALERT_EMAIL:-}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check functions
check_container_running() {
    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        return 0
    else
        return 1
    fi
}

check_bot_process() {
    docker exec $CONTAINER_NAME test -f .trading_bot.pid 2>/dev/null
    return $?
}

check_memory_usage() {
    local mem_usage=$(docker stats --no-stream --format "{{.MemPerc}}" $CONTAINER_NAME | sed 's/%//')
    if (( $(echo "$mem_usage > 90" | bc -l) )); then
        return 1
    fi
    return 0
}

check_disk_space() {
    local disk_usage=$(df -h /var/lib/docker | awk 'NR==2 {print $5}' | sed 's/%//')
    if (( disk_usage > 90 )); then
        return 1
    fi
    return 0
}

check_recent_logs() {
    # Check for errors in last 5 minutes
    local errors=$(docker logs --since 5m $CONTAINER_NAME 2>&1 | grep -i "error\|exception\|crash" | wc -l)
    if (( errors > 10 )); then
        return 1
    fi
    return 0
}

# Alert functions
send_telegram_alert() {
    local message="$1"
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST \
            "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=🚨 FractalTrader Alert: ${message}" \
            -d "parse_mode=HTML" \
            >/dev/null 2>&1
    fi
}

send_email_alert() {
    local message="$1"
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "FractalTrader Alert" "$ALERT_EMAIL" 2>/dev/null || true
    fi
}

restart_bot() {
    echo -e "${YELLOW}Attempting to restart bot...${NC}"
    docker compose -f /path/to/docker-compose.cloud.yml restart
    sleep 10
    if check_container_running && check_bot_process; then
        echo -e "${GREEN}✓ Bot restarted successfully${NC}"
        send_telegram_alert "Bot was automatically restarted and is now running."
        return 0
    else
        echo -e "${RED}✗ Failed to restart bot${NC}"
        send_telegram_alert "CRITICAL: Failed to restart bot. Manual intervention required!"
        return 1
    fi
}

# Main health check
main() {
    echo "=========================================="
    echo "FractalTrader Health Check"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="

    local has_issues=0

    # Check 1: Container running
    echo -n "Container Status: "
    if check_container_running; then
        echo -e "${GREEN}✓ Running${NC}"
    else
        echo -e "${RED}✗ Not Running${NC}"
        send_telegram_alert "Container is not running!"
        restart_bot
        has_issues=1
        return $has_issues
    fi

    # Check 2: Bot process
    echo -n "Bot Process: "
    if check_bot_process; then
        echo -e "${GREEN}✓ Active${NC}"
    else
        echo -e "${RED}✗ Not Active${NC}"
        send_telegram_alert "Bot process is not active!"
        restart_bot
        has_issues=1
    fi

    # Check 3: Memory usage
    echo -n "Memory Usage: "
    if check_memory_usage; then
        local mem=$(docker stats --no-stream --format "{{.MemPerc}}" $CONTAINER_NAME)
        echo -e "${GREEN}✓ ${mem}${NC}"
    else
        local mem=$(docker stats --no-stream --format "{{.MemPerc}}" $CONTAINER_NAME)
        echo -e "${RED}✗ ${mem} (>90%)${NC}"
        send_telegram_alert "High memory usage: ${mem}"
        has_issues=1
    fi

    # Check 4: Disk space
    echo -n "Disk Space: "
    if check_disk_space; then
        local disk=$(df -h /var/lib/docker | awk 'NR==2 {print $5}')
        echo -e "${GREEN}✓ ${disk}${NC}"
    else
        local disk=$(df -h /var/lib/docker | awk 'NR==2 {print $5}')
        echo -e "${RED}✗ ${disk} (>90%)${NC}"
        send_telegram_alert "Low disk space: ${disk}"
        has_issues=1
    fi

    # Check 5: Recent errors
    echo -n "Recent Errors: "
    if check_recent_logs; then
        echo -e "${GREEN}✓ Normal${NC}"
    else
        echo -e "${YELLOW}⚠ High error rate${NC}"
        send_telegram_alert "High error rate detected in logs (last 5 minutes)"
        has_issues=1
    fi

    # Get bot status
    echo ""
    echo "Bot Status:"
    docker exec $CONTAINER_NAME python3 -m live.cli status 2>/dev/null || echo "Unable to retrieve bot status"

    echo "=========================================="
    if [ $has_issues -eq 0 ]; then
        echo -e "${GREEN}✓ All checks passed${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ Some issues detected${NC}"
        exit 1
    fi
}

# Run main
main
