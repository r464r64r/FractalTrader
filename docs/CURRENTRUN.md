# Current Testnet Run - Monitoring Guide

**Created:** 2026-01-04 17:14 UTC
**Branch:** `fix/testnet-zero-balance-simulation`
**PR:** #30 (pending approval)

---

## Current Status

```
🟢 RUNNING in SIMULATION MODE
Started: 2026-01-04 16:52:18 UTC
Mode: Paper trading with $10k virtual balance
Strategy: liquidity_sweep
Symbol: BTC
Timeframe: 1h
Network: Hyperliquid Testnet

✅ Market data fetching: Every 60 seconds
✅ Signal generation: Working (bearish -1 detected)
✅ Position sizing: Working (0.0055 BTC ~$500)
⚠️ Orders: Failing (expected - wallet not activated)
⚠️ State persistence: JSON error (non-critical in simulation)
```

### Wallet Information

- **Address:** `0xEA28Cb42efE3e90831a583Ee1d376c9e64bc4A02`
- **Balance:** $0.00 (unfunded)
- **Mode:** SIMULATION (not executing real orders)
- **Fund at:** https://app.hyperliquid-testnet.xyz/drip

---

## How to Check Results

### 1. Quick Status Check

```bash
sudo docker exec fractal-trader-dev python -m live.cli status
```

**Expected Output:**
```
Status: 🟢 RUNNING
Starting Balance: $10,000.00
Open Positions: 0
Total Trades: 0
```

### 2. Recent Activity (Last 10 iterations)

```bash
sudo docker exec fractal-trader-dev tail -50 /tmp/bot_v2.log | grep -E "Signal:|Placing order:|ERROR|CRITICAL"
```

**What to Look For:**
- `Signal: -1 @ <price>` = Bearish signal detected
- `Signal: 1 @ <price>` = Bullish signal detected
- `Signal: 0 @ <price>` = No signal (wait)
- `ERROR` = Non-critical issues (expected: order failures)
- `CRITICAL` = Circuit breaker or fatal errors (should be 0)

### 3. Full Bot Logs

```bash
sudo docker exec fractal-trader-dev cat /tmp/bot_v2.log
```

### 4. Check Uptime & Crash Status

```bash
# Check if bot process is running
sudo docker exec fractal-trader-dev ps aux | grep "python.*live.cli" | grep -v grep

# Check PID file timestamp (bot start time)
sudo docker exec fractal-trader-dev stat .trading_bot.pid
```

**If no process found:** Bot crashed - check logs for CRITICAL errors

### 5. Monitor Live Activity (Real-time)

```bash
sudo docker exec fractal-trader-dev tail -f /tmp/bot_v2.log
```

Press `Ctrl+C` to exit

### 6. Signal History Analysis

```bash
# Count total signals generated
sudo docker exec fractal-trader-dev grep -c "Signal:" /tmp/bot_v2.log

# View signal distribution
sudo docker exec fractal-trader-dev grep "Signal:" /tmp/bot_v2.log | awk '{print $NF}' | sort | uniq -c

# Last 20 signals with timestamps
sudo docker exec fractal-trader-dev grep "Signal:" /tmp/bot_v2.log | tail -20
```

---

## Monitoring Schedule

### Immediate Checkpoints

#### Every 1 Hour
```bash
# Quick health check
sudo docker exec fractal-trader-dev python -m live.cli status
```

**Success Criteria:**
- Status shows 🟢 RUNNING
- No CRITICAL errors in logs

#### Every 6 Hours
```bash
# Review signal patterns
sudo docker exec fractal-trader-dev grep "Signal:" /tmp/bot_v2.log | tail -30

# Check for errors
sudo docker exec fractal-trader-dev grep -c "ERROR\|CRITICAL" /tmp/bot_v2.log
```

**Success Criteria:**
- Signals being generated regularly (1 per minute expected)
- No CRITICAL errors
- ERROR count stable (only order placement failures expected)

#### Every 24 Hours (Full Health Check)
```bash
# 1. Check uptime
sudo docker exec fractal-trader-dev stat .trading_bot.pid

# 2. Count total signals
sudo docker exec fractal-trader-dev grep -c "Signal:" /tmp/bot_v2.log

# 3. Check for CRITICAL errors
sudo docker exec fractal-trader-dev grep "CRITICAL" /tmp/bot_v2.log

# 4. Verify no circuit breakers
sudo docker exec fractal-trader-dev grep "CIRCUIT BREAKER" /tmp/bot_v2.log

# 5. Check for division by zero
sudo docker exec fractal-trader-dev grep "ZeroDivisionError" /tmp/bot_v2.log
```

---

## Success Metrics for PR Approval

**Minimum Validation Period:** 24 hours continuous operation

| Metric | Target | How to Check | Status |
|--------|--------|--------------|--------|
| No crashes | 0 | `ps aux \| grep live.cli` | ⏳ Pending |
| Data fetching | Every 60s | `grep "Fetched.*candles" /tmp/bot_v2.log \| tail -5` | ✅ Pass |
| Signal generation | Consistent | `grep "Signal:" /tmp/bot_v2.log \| wc -l` | ✅ Pass |
| No circuit breakers | 0 triggers | `grep "CIRCUIT BREAKER" /tmp/bot_v2.log` | ✅ Pass |
| No division by zero | 0 errors | `grep "ZeroDivisionError" /tmp/bot_v2.log` | ✅ Pass |
| Simulation mode active | Yes | `grep "SIMULATION MODE" /tmp/bot_v2.log` | ✅ Pass |

---

## Current Known Issues (Non-Critical)

### 1. State Persistence Error
```
ERROR - Failed to save state: Object of type Timestamp is not JSON serializable
```

**Impact:** State not saved between restarts
**Workaround:** In simulation mode, state tracked in memory only
**Fix:** Future improvement (serialize datetime to ISO string)
**Criticality:** Low - doesn't affect simulation mode operation

### 2. Order Execution Failures
```
Order placed: {'status': 'err', 'response': 'User or API Wallet ... does not exist.'}
```

**Impact:** Orders don't execute on exchange
**Expected:** Normal behavior for unfunded testnet wallet
**Fix:** Fund wallet at https://app.hyperliquid-testnet.xyz/drip
**Criticality:** N/A - expected in simulation mode

---

## Validation Timeline

```
NOW (17:14 UTC)         → Bot running 22 min ✅
+1 hour (18:14 UTC)     → Check: still running?
+6 hours (23:14 UTC)    → Check: signal patterns
+24 hours (17:14 UTC)   → Full review → READY FOR MERGE
```

**After 24 hours continuous operation with no crashes → Safe to merge PR #30**

---

## How to Run Real Testnet (with Funded Wallet)

### Prerequisites

1. **Hyperliquid mainnet deposit** (required for testnet access)
   - Must have deposited on Hyperliquid mainnet with same wallet address
   - See: https://hyperliquid.gitbook.io/hyperliquid-docs/onboarding/testnet-faucet

2. **Fund testnet wallet**
   - Visit: https://app.hyperliquid-testnet.xyz/drip
   - Login with wallet `0xEA28Cb42efE3e90831a583Ee1d376c9e64bc4A02`
   - Claim 1,000 mock USDC (available every 4 hours)

3. **Alternative faucets** (if mainnet requirement is an issue)
   - QuickNode: https://faucet.quicknode.com/hyperliquid/testnet (requires 0.05 HYPE on mainnet)
   - Chainstack: https://faucet.chainstack.com/hyperliquid-testnet-faucet (requires 0.08 ETH on Ethereum)

### Steps to Transition from Simulation to Real Testnet

#### 1. Stop Current Bot
```bash
sudo docker exec fractal-trader-dev python -m live.cli stop
```

#### 2. Verify Wallet is Funded
```bash
sudo docker exec fractal-trader-dev python -c "
from live.hl_integration.config import HyperliquidConfig
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.utils import constants

config = HyperliquidConfig.from_env(network='testnet')
wallet = Account.from_key(config.private_key)
info = Info(constants.TESTNET_API_URL, skip_ws=True)
state = info.user_state(wallet.address)

balance = float(state['marginSummary']['accountValue'])
print(f'Wallet: {wallet.address}')
print(f'Balance: \${balance:,.2f}')
print(f'Mode: {'REAL TESTNET' if balance > 0 else 'SIMULATION'}')
"
```

**Expected Output (after funding):**
```
Wallet: 0xEA28Cb42efE3e90831a583Ee1d376c9e64bc4A02
Balance: $1,000.00
Mode: REAL TESTNET
```

#### 3. Clean State Files
```bash
sudo docker exec fractal-trader-dev bash -c "rm -f .testnet_state.json .testnet_state.json.* .trading_bot.pid"
```

#### 4. Restart Bot (will auto-detect funded wallet)
```bash
sudo docker exec fractal-trader-dev bash -c "cd /app && nohup python -m live.cli start --strategy liquidity_sweep > /tmp/bot_real.log 2>&1 &"
```

#### 5. Verify Real Mode Activated
```bash
# Wait 10 seconds for initialization
sleep 10

# Check logs for mode
sudo docker exec fractal-trader-dev grep -E "SIMULATION MODE|Set starting balance" /tmp/bot_real.log
```

**Expected Output (real mode):**
```
Set starting balance: $1,000.00
```

**NOT expected (simulation mode):**
```
WARNING - Testnet account has $0 balance. Using simulated balance: $10,000
INFO - Running in SIMULATION MODE
```

#### 6. Monitor Real Trading Activity
```bash
# Check status
sudo docker exec fractal-trader-dev python -m live.cli status

# Monitor live
sudo docker exec fractal-trader-dev tail -f /tmp/bot_real.log
```

**Expected Behavior (real mode):**
- Orders execute successfully: `{'status': 'ok', 'response': ...}`
- Positions tracked in state file
- Trades recorded in history
- Real P&L calculated from executed orders

---

## Real Testnet Monitoring

### Key Differences from Simulation

| Aspect | Simulation Mode | Real Testnet Mode |
|--------|-----------------|-------------------|
| Starting Balance | $10,000 (virtual) | Actual wallet balance |
| Orders | Fail (wallet not activated) | Execute on exchange |
| Positions | Tracked in memory | Tracked on exchange + state file |
| P&L | Calculated from simulated fills | Real fills from exchange |
| State Persistence | Not critical | Required for recovery |

### Additional Commands for Real Mode

#### Check Open Orders on Exchange
```bash
sudo docker exec fractal-trader-dev python -c "
from live.hl_integration.config import HyperliquidConfig
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.utils import constants

config = HyperliquidConfig.from_env(network='testnet')
wallet = Account.from_key(config.private_key)
info = Info(constants.TESTNET_API_URL, skip_ws=True)

orders = info.open_orders(wallet.address)
print('Open Orders:', orders)
"
```

#### Check Exchange Positions
```bash
sudo docker exec fractal-trader-dev python -c "
from live.hl_integration.config import HyperliquidConfig
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.utils import constants

config = HyperliquidConfig.from_env(network='testnet')
wallet = Account.from_key(config.private_key)
info = Info(constants.TESTNET_API_URL, skip_ws=True)

state = info.user_state(wallet.address)
positions = state.get('assetPositions', [])
print('Exchange Positions:', positions)
"
```

#### View Trading Dashboard
Open in browser: https://app.hyperliquid-testnet.xyz/

Login with wallet to see:
- Open positions
- Order history
- Portfolio value
- P&L charts

---

## Circuit Breakers (Real Mode)

When running with real testnet funds, these safety limits apply:

| Circuit Breaker | Threshold | Action |
|-----------------|-----------|--------|
| Max Drawdown | 20% | Stop trading, save state |
| Max Daily Trades | 50 | Stop trading for safety |

**To modify circuit breakers:**

Edit `live/hl_integration/testnet.py` lines 127-129:
```python
self.max_daily_drawdown = 0.20  # 20% default
self.max_daily_trades = 50      # 50 trades default
```

---

## Troubleshooting

### Bot Won't Start
```bash
# Check for PID file conflict
sudo docker exec fractal-trader-dev ls -la .trading_bot.pid

# Remove if exists
sudo docker exec fractal-trader-dev rm .trading_bot.pid

# Try again
sudo docker exec fractal-trader-dev python -m live.cli start --strategy liquidity_sweep
```

### Bot Crashed
```bash
# Check logs for CRITICAL errors
sudo docker exec fractal-trader-dev grep "CRITICAL\|Traceback" /tmp/bot_v2.log | tail -50

# Check system resources
sudo docker stats fractal-trader-dev --no-stream
```

### Orders Not Executing (Real Mode)
```bash
# Verify wallet balance
sudo docker exec fractal-trader-dev python -c "
from live.hl_integration.config import HyperliquidConfig
from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.utils import constants

config = HyperliquidConfig.from_env(network='testnet')
wallet = Account.from_key(config.private_key)
info = Info(constants.TESTNET_API_URL, skip_ws=True)
state = info.user_state(wallet.address)
print('Balance:', state['marginSummary']['accountValue'])
"

# Check for API errors
sudo docker exec fractal-trader-dev grep "Order placed:" /tmp/bot_real.log | tail -10
```

---

## Files & Locations

| File | Location | Purpose |
|------|----------|---------|
| Bot logs | `/tmp/bot_v2.log` | Current run activity |
| State file | `.testnet_state.json` | Position/trade persistence |
| PID file | `.trading_bot.pid` | Process tracking |
| State backups | `.testnet_state.json.bak[1-5]` | Auto-backups (5 rotations) |

---

## Next Steps

1. **Monitor for 24 hours** - Verify no crashes in simulation mode
2. **Merge PR #30** - After successful validation
3. **Fund testnet wallet** - Transition to real testnet trading
4. **Sprint 5** - Add E2E tests and monitoring dashboard

---

**Last Updated:** 2026-01-04 17:14 UTC
**Maintained by:** Development Team
**Related Docs:**
- `docs/DECISION_LOG_TESTNET_SIMULATION.md` - Technical decision rationale
- `docs/ISSUES.md` - Project status tracker
- `docs/ROADMAP_Q1_2025.md` - Sprint planning
