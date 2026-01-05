# FractalTrader Public Dashboard

Minimalist live monitoring dashboard for public viewing.

## Quick Start

**URL:** http://54.199.8.26:8080

### Start Dashboard

```bash
# Inside Docker container
sudo docker exec fractal-trader-dev nohup python3 -m live.dashboard > /tmp/dashboard.log 2>&1 &

# Check if running
sudo docker exec fractal-trader-dev curl http://localhost:8080/api/status
```

### Stop Dashboard

```bash
sudo docker exec fractal-trader-dev pkill -f "live.dashboard"
```

## Features

- **Auto-refresh:** Updates every 5 seconds
- **Session Info:** Uptime, balance, positions, trades
- **Live Logs:** Last 50 log lines with syntax highlighting
- **Mobile Responsive:** Works on all devices
- **Dark Terminal Theme:** Hacker-style green-on-black

## Endpoints

- `/` - Main HTML dashboard (auto-refreshes)
- `/api/status` - JSON status endpoint

## Security Group Setup

If dashboard is not accessible from public internet, configure AWS Security Group:

1. Go to EC2 → Security Groups
2. Find security group for this instance
3. Add inbound rule:
   - Type: Custom TCP
   - Port: 8080
   - Source: 0.0.0.0/0 (public) or your IP
   - Description: FractalTrader Dashboard

## Architecture

- **Framework:** Flask (minimal, KISS)
- **Data Sources:**
  - State: `/app/.testnet_state.json`
  - Logs: `/tmp/bot_v2.log`
- **Port:** 8080 (mapped in docker-compose)
- **Mode:** Read-only (no control actions)

## Sample JSON Response

```json
{
  "status": "RUNNING",
  "status_class": "running",
  "uptime": "3.1h",
  "session_start": "2026-01-05T00:20:03.158960",
  "starting_balance": "10000.00",
  "open_positions": 0,
  "total_trades": 0
}
```

## Monitoring

```bash
# Dashboard logs
sudo docker exec fractal-trader-dev tail -f /tmp/dashboard.log

# Test API
curl http://localhost:8080/api/status

# Test HTML
curl http://localhost:8080/ | head -20
```

## Notes

- Dashboard runs independently of trading bot
- Simulation mode only (no real trades)
- Branch shown in footer
- No authentication (read-only public data)
