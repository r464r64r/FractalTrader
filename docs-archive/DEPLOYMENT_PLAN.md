# Fractal Trader — Production Deployment Roadmap

**Current Status:** Alpha (Core Complete, Live Trading Untested)
**Target:** Production-ready mainnet deployment
**Timeline:** 4-6 weeks

---

## Executive Summary

FractalTrader has a **solid technical foundation** (134 core tests, 95%+ coverage) but requires additional work before production deployment:

| Component | Status | Risk Level |
|-----------|--------|-----------|
| Core SMC Detection | ✅ Production-ready | LOW |
| Backtesting Framework | ✅ Production-ready | LOW |
| Data Layer | ⚠️ Beta (Docker-only testing) | MEDIUM |
| Live Trading | 🔴 Alpha (no validation) | **HIGH** |
| Portfolio Risk Controls | ❌ Missing | **CRITICAL** |

**Recommendation:** Do not deploy to mainnet until all HIGH/CRITICAL items are addressed.

---

## Phase 1: Stabilization (Priority: CRITICAL)

**Goal:** Make all tests runnable locally, fix critical gaps
**Timeline:** 1 week
**Risk if skipped:** Crashes in production, data loss

### Tasks

#### 1.1 Fix Dependency Issues ✅ DONE
- [x] Add `hyperliquid>=0.1.0` to requirements.txt
- [x] Add `eth-account>=0.8.0` to requirements.txt
- [ ] Test installation on clean Python environment
- [ ] Document platform-specific issues (if any)

**Acceptance Criteria:**
```bash
pip install -r requirements.txt  # No errors
python -m pytest tests/ -v       # All 206 tests pass
```

#### 1.2 Add Retry Logic to Data Fetchers
**Priority:** CRITICAL (prevents crashes)

**Files to modify:**
- `data/hyperliquid_fetcher.py`
- `data/ccxt_fetcher.py`

**Implementation:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int):
    # Existing code...
```

**Tests to add:**
- [ ] `test_retry_on_network_failure`
- [ ] `test_retry_exponential_backoff`
- [ ] `test_max_retries_exceeded`

**Acceptance Criteria:**
- Network timeout doesn't crash bot
- 3 retry attempts with exponential backoff
- Logs all retry attempts

#### 1.3 Increase Strategy Test Coverage
**Priority:** HIGH (production confidence)

**Current coverage:**
- `liquidity_sweep.py`: 13%
- `bos_orderblock.py`: 42%

**Target:** 70%+ for all strategies

**Approach:**
- Add tests for private methods (`_create_long_signal`, `_create_short_signal`)
- Test edge cases (empty data, no signals, extreme volatility)
- Mock dependencies (avoid testing core modules again)

**Acceptance Criteria:**
```bash
pytest tests/test_strategies.py --cov=strategies --cov-report=term-missing
# All strategies >70% coverage
```

---

## Phase 2: Testnet Validation (Priority: HIGH)

**Goal:** 24-hour crash-free testnet run
**Timeline:** 1 week
**Risk if skipped:** Unknown bugs in production

### Tasks

#### 2.1 End-to-End Integration Test
**Priority:** CRITICAL

**Create:** `tests/test_integration.py`

**Test flow:**
```python
def test_full_trading_cycle():
    """Test complete flow: data → signals → orders → fills → P&L"""
    # 1. Fetch data
    # 2. Generate signals
    # 3. Calculate position size
    # 4. Place order (mock exchange)
    # 5. Simulate fill
    # 6. Track P&L
    # 7. Close position
```

**Acceptance Criteria:**
- Tests pass with mocked exchange
- Tests pass on live testnet (mark as `@pytest.mark.testnet`)

#### 2.2 24-Hour Testnet Run
**Priority:** HIGH

**Setup:**
```bash
# Create testnet config
cat > .env.testnet <<EOF
NETWORK=testnet
PRIVATE_KEY=<testnet_key>
DEFAULT_SYMBOL=BTC
DEFAULT_TIMEFRAME=1h
BASE_RISK_PERCENT=0.5
MAX_OPEN_POSITIONS=2
CHECK_INTERVAL_SECONDS=300
EOF

# Run
python examples/live_trading_example.py --config .env.testnet --duration 86400
```

**Monitoring checklist:**
- [ ] No crashes for 24h
- [ ] All signals logged correctly
- [ ] Position sizing within limits
- [ ] Stop losses executed properly
- [ ] P&L tracking accurate

**Success criteria:**
- Zero crashes
- Zero unexpected errors in logs
- All positions closed cleanly

#### 2.3 Monitoring Dashboard
**Priority:** MEDIUM

**Create:** `live/monitoring/dashboard.py`

**Features:**
- Real-time P&L tracking
- Open positions display
- Signal history log
- Performance metrics (Sharpe, win rate, etc.)

**Tech stack:** Streamlit or simple Flask app

**Acceptance Criteria:**
- Dashboard shows live positions
- Updates every 60 seconds
- Shows last 50 signals

#### 2.4 Alert System
**Priority:** MEDIUM

**Create:** `live/alerts/telegram.py`

**Notifications:**
- Trade opened/closed
- Stop loss hit
- Daily P&L summary
- Error alerts (critical only)

**Acceptance Criteria:**
- Telegram bot sends alerts
- Rate limiting (max 10 msgs/hour)
- Configurable alert levels

---

## Phase 3: Portfolio Risk Controls (Priority: HIGH)

**Goal:** Multi-position risk management
**Timeline:** 1 week
**Risk if skipped:** Correlated losses, runaway drawdown

### Tasks

#### 3.1 Position Correlation Tracking
**Priority:** HIGH

**Create:** `risk/portfolio.py`

**Features:**
```python
class PortfolioRiskManager:
    def check_correlation(self, new_symbol: str, open_positions: List[str]) -> bool:
        """
        Prevent opening highly correlated positions.

        Example: If BTC position open, reject ETH signal (>0.8 correlation)
        """

    def calculate_portfolio_var(self) -> float:
        """Value at Risk for entire portfolio"""

    def check_drawdown_limit(self, current_equity: float) -> bool:
        """Emergency stop if drawdown >10%"""
```

**Data needed:**
- Historical correlation matrix (pre-computed)
- Real-time portfolio value
- Starting equity baseline

**Acceptance Criteria:**
- Rejects correlated positions (>0.8 correlation)
- Stops trading if portfolio down >10%

#### 3.2 State Persistence
**Priority:** HIGH (prevents data loss)

**Create:** `live/persistence/state_manager.py`

**Implementation:**
```python
import json
from pathlib import Path

class StateManager:
    def save_state(self, positions: Dict, trades: List):
        """Save to data/state.json"""

    def load_state(self) -> Tuple[Dict, List]:
        """Load from data/state.json on restart"""
```

**Saves:**
- Open positions (entry price, size, SL/TP)
- Trade history (last 100 trades)
- Performance metrics (total P&L, win rate)

**Acceptance Criteria:**
- Bot restarts without losing position data
- `data/state.json` updated every 60s
- Recovery test: kill process, restart, verify positions

#### 3.3 Circuit Breakers
**Priority:** CRITICAL

**Add to:** `live/hyperliquid/testnet.py` and `trader.py`

**Triggers:**
```python
class CircuitBreaker:
    def should_halt_trading(self) -> bool:
        # 1. Portfolio drawdown >10%
        # 2. 5 consecutive losses
        # 3. Unusual volatility (ATR >3x baseline)
        # 4. Exchange connection issues (3+ failures)
```

**Actions:**
- Stop opening new positions
- Close all positions (optional, configurable)
- Send critical alert
- Log incident to `data/circuit_breaker_events.log`

**Acceptance Criteria:**
- Halts trading on 10% drawdown
- Halts on 5 consecutive losses
- Resumes only after manual confirmation

---

## Phase 4: Mainnet Readiness (Priority: MEDIUM)

**Goal:** Safe mainnet deployment checklist
**Timeline:** 2 weeks
**Risk if skipped:** Loss of real capital

### Tasks

#### 4.1 7-Day Testnet Validation
**Priority:** CRITICAL before mainnet

**Requirements:**
- [ ] 7 consecutive days without crashes
- [ ] At least 20 trades executed
- [ ] Circuit breakers tested (trigger manually)
- [ ] State persistence tested (restart 3+ times)
- [ ] Alert system working (receive all notifications)

**Metrics to track:**
- Total P&L (testnet $)
- Win rate
- Max drawdown
- Average trade duration
- Sharpe ratio

**Success criteria:**
- Zero critical errors
- Circuit breaker triggers correctly
- Bot recovers from restarts

#### 4.2 Small Capital Test
**Priority:** CRITICAL

**Mainnet test with minimal capital:**
- Start with $50-100 (amount you can lose)
- Max position size: $10
- Run for 48 hours
- Monitor every 4 hours

**Checklist:**
- [ ] Wallet funded ($50-100)
- [ ] Config updated (max_position_percent=0.2%)
- [ ] Monitoring dashboard running
- [ ] Telegram alerts active
- [ ] Manual override ready (kill switch)

**Success criteria:**
- No unexpected behavior
- All systems work as on testnet
- P&L tracking accurate (verify manually)

#### 4.3 Manual Verification Process
**Priority:** HIGH

**Before each mainnet trade:**
```python
if config.network == 'mainnet' and not config.auto_confirm:
    print(f"MAINNET ORDER CONFIRMATION REQUIRED")
    print(f"Symbol: {symbol}, Direction: {direction}, Size: {size}")
    confirmation = input("Type 'CONFIRM' to proceed: ")
    if confirmation != 'CONFIRM':
        logger.warning("Trade cancelled by user")
        return
```

**Acceptance Criteria:**
- Requires explicit "CONFIRM" for mainnet (already implemented)
- Logs all confirmation requests
- Timeout after 60s (skip trade)

#### 4.4 Disaster Recovery Plan

**Document:** `DISASTER_RECOVERY.md`

**Scenarios:**
1. **Bot crashes with open positions**
   - Action: Manual close on Hyperliquid UI
   - Backup: `data/state.json` has position details

2. **Exchange API down**
   - Action: Wait for restoration (positions safe on DEX)
   - Backup: Use Hyperliquid UI to manage

3. **Unexpected drawdown >20%**
   - Action: Emergency shutdown (`kill -9` + manual close)
   - Prevention: Circuit breakers should prevent this

4. **Data corruption**
   - Action: Restore from `data/state.json.backup`
   - Prevention: Daily backups to `data/backups/`

**Acceptance Criteria:**
- All scenarios documented
- Recovery procedures tested on testnet
- Backup files created automatically

---

## Phase 5: Production Operations (Post-Mainnet)

**Goal:** Ongoing maintenance and improvement
**Timeline:** Continuous

### Tasks

#### 5.1 Multi-Exchange Support
**Priority:** LOW

**Add exchanges:**
- Bybit (via CCXT)
- OKX (via CCXT)
- Binance Futures (via CCXT)

**Implementation:**
- Extend `data/ccxt_fetcher.py` for live trading
- Add exchange-specific configs
- Test on each exchange's testnet

#### 5.2 Performance Dashboard
**Priority:** MEDIUM

**Features:**
- Cumulative P&L chart
- Equity curve
- Drawdown graph
- Trade distribution (win/loss histogram)
- Strategy performance comparison

**Tech:** Plotly + Streamlit

#### 5.3 Automated Reporting
**Priority:** LOW

**Daily reports (email/Telegram):**
- P&L summary
- Top performing strategy
- Worst trade of the day
- System health check

---

## Risk Matrix

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data fetcher crashes | HIGH | MEDIUM | Retry logic (Phase 1.2) |
| Correlated losses | HIGH | HIGH | Portfolio correlation (Phase 3.1) |
| State loss on restart | MEDIUM | LOW | State persistence (Phase 3.2) |
| Runaway drawdown | CRITICAL | LOW | Circuit breakers (Phase 3.3) |
| Exchange API failure | MEDIUM | MEDIUM | Disaster recovery plan (Phase 4.4) |
| Untested edge cases | HIGH | MEDIUM | Integration tests (Phase 2.1) |

---

## Success Metrics

### Pre-Mainnet
- [x] All 206 tests passing
- [ ] 7-day testnet run successful
- [ ] Circuit breakers tested
- [ ] State persistence verified

### Post-Mainnet (Month 1)
- [ ] 30-day uptime >99%
- [ ] Max drawdown <15%
- [ ] No critical errors
- [ ] Positive Sharpe ratio >1.0

### Long-term (Month 3+)
- [ ] Multi-exchange deployment
- [ ] Performance dashboard live
- [ ] Community documentation complete
- [ ] 1000+ backtested strategies

---

## Timeline Overview

```
Week 1-2:  Phase 1 (Stabilization)
Week 2-3:  Phase 2 (Testnet Validation)
Week 3-4:  Phase 3 (Portfolio Risk)
Week 4-6:  Phase 4 (Mainnet Readiness)
Week 6+:   Phase 5 (Operations)
```

**Earliest safe mainnet date:** 6 weeks from now (assuming no major issues)

---

## Approval Checklist

Before deploying to mainnet, verify ALL items:

- [ ] All 206 tests pass locally and in Docker
- [ ] Retry logic implemented and tested
- [ ] Strategy coverage >70%
- [ ] 7-day testnet run completed (zero crashes)
- [ ] Circuit breakers trigger correctly
- [ ] State persistence works (tested with 3+ restarts)
- [ ] Small capital test successful ($50-100 for 48h)
- [ ] Monitoring dashboard deployed
- [ ] Telegram alerts working
- [ ] Disaster recovery plan documented
- [ ] Team review completed
- [ ] Risk assessment signed off

**Only proceed when ALL boxes are checked. Your capital depends on it.**

---

## Contact & Support

**Questions?** Open an issue on GitHub
**Critical bugs?** Tag as `[CRITICAL]` in issue title
**Live trading issues?** Stop bot immediately, assess manually

---

*Last updated: 2025-12-20*
*Status: Phase 1 in progress (dependencies fixed)*
