# Sprint 4: Production Hardening - Implementation Plan

**Sprint Duration:** Feb 4 - Feb 17, 2025 (14 days)
**Status:** 📋 Planning → Ready for Implementation
**Goal:** Maximize production readiness (85% → 95%+) before Sprint 6 (Live Trading)
**Philosophy:** Quality over speed. No live trading pressure. Build bulletproof foundations.

---

## 🎯 Executive Summary

Sprint 4 is the **critical hardening phase** before we consider live trading. With the stacja robocza offline and no pressure for immediate mainnet deployment, we have the perfect opportunity to:

1. **Fix all critical gaps** (strategy tests, E2E validation, portfolio risk)
2. **Build production-grade monitoring** (observability, alerts, health checks)
3. **Validate system resilience** (7-day testnet run, disaster recovery)
4. **Document everything** (incident response, operational playbooks)

**Success Metric:** System ready for small-scale live trading validation ($100-500) with **zero known critical bugs**.

---

## 🎯 Sprint Goals

### Primary Objectives (Must Have):
1. ✅ **Strategy test coverage:** 13-42% → **70%+**
2. ✅ **E2E integration tests:** Full trading loop validated
3. ✅ **Portfolio-level risk controls:** Prevent over-concentration
4. ✅ **7-day testnet validation:** Zero crashes, 99.9% uptime
5. ✅ **Monitoring dashboard:** Real-time system observability

### Secondary Objectives (Should Have):
6. ✅ **Disaster recovery procedures:** Documented playbooks
7. ✅ **Walk-forward validation:** Strategy robustness testing
8. ✅ **Documentation cleanup:** Archive old docs, update current

### Stretch Goals (Nice to Have):
9. 📊 Performance profiling & optimization
10. 🔒 Security audit (API key handling, state file permissions)
11. 📱 Alert system enhancements (SMS/Telegram integration)

---

## 🚨 Critical Tasks (Priority 1)

### Task 1: Strategy Test Coverage (70%+)
**Current State:**
- `strategies/liquidity_sweep.py`: **13% coverage** ❌
- `strategies/bos_orderblock.py`: **42% coverage** ❌
- `strategies/fvg_fill.py`: **~40% coverage** ⚠️

**Target:** All strategies **70%+ coverage** ✅

**Time Estimate:** 10-14 hours

**Subtasks:**
1. **Liquidity Sweep Strategy Tests** (4-6h)
   - Test entry logic (sweep detection + reversal)
   - Test exit logic (TP/SL placement)
   - Test edge cases:
     - No liquidity levels detected
     - Multiple sweeps in succession
     - Sweep during low volatility
     - Concurrent signals across timeframes
   - Test risk integration (position sizing, stop loss)
   - Mock exchange responses (no API keys needed)

2. **BOS Order Block Strategy Tests** (4-6h)
   - Test BOS detection (Break of Structure)
   - Test order block identification
   - Test entry timing (pullback to OB)
   - Test edge cases:
     - Weak order blocks (low volume)
     - Failed retest (price breaks through OB)
     - Multiple OBs in same zone
     - HTF/LTF alignment
   - Test risk integration

3. **FVG Fill Strategy Tests** (2-3h)
   - Test FVG detection (3-candle gaps)
   - Test mean reversion logic
   - Test edge cases:
     - Gaps filled immediately
     - Partial fills
     - Gaps that never fill
   - Test risk integration

**Implementation Notes:**
```python
# Example test structure (tests/test_strategies.py)

class TestLiquiditySweepStrategy:
    """Comprehensive tests for liquidity sweep strategy."""

    def test_sweep_detection_with_reversal(self):
        """Test entry when sweep is followed by reversal."""
        # Setup: Create price data with liquidity sweep
        # Execute: Run strategy
        # Assert: Signal generated with correct direction

    def test_no_signal_without_reversal(self):
        """Test no entry when sweep doesn't reverse."""
        # Edge case: sweep continues in same direction

    def test_position_sizing_scales_with_confidence(self):
        """Test dynamic position sizing based on confidence."""
        # Verify: Higher confidence → larger position

    @patch('hyperliquid.info.Info')
    def test_handles_exchange_disconnect(self, mock_info):
        """Test graceful handling of exchange errors."""
        mock_info.side_effect = ConnectionError("API Timeout")
        # Verify: No crash, error logged, retry attempted
```

**Success Criteria:**
- [ ] All 3 strategies ≥70% coverage
- [ ] All edge cases documented and tested
- [ ] No failing tests
- [ ] Mock-based (works without API keys)

**Risks & Mitigation:**
- **Risk:** Edge cases hard to identify
- **Mitigation:** Review historical backtest failures, study market regime changes

---

### Task 2: End-to-End Integration Tests
**Current State:** No E2E tests ❌

**Target:** Full trading loop validated ✅

**Time Estimate:** 6-8 hours

**Subtasks:**
1. **E2E Test Framework Setup** (2-3h)
   - Create `tests/test_e2e_integration.py`
   - Mock exchange environment (simulated order fills)
   - Test data pipeline (data fetch → strategy → execution → state)

2. **Happy Path E2E Test** (2-3h)
   - Test: Fetch data → Detect signal → Place order → Update state
   - Verify: State persistence, position tracking, PnL calculation
   - Validate: All components communicate correctly

3. **Failure Mode E2E Tests** (2-3h)
   - Test: Exchange disconnect during order placement
   - Test: State file corruption recovery
   - Test: Circuit breaker triggers (drawdown limit)
   - Test: Partial order fills
   - Test: Order rejection (insufficient margin)

**Implementation Notes:**
```python
class TestE2EIntegration:
    """End-to-end system integration tests."""

    @patch('data.fetchers.HyperliquidFetcher')
    @patch('hyperliquid.exchange.Exchange')
    def test_full_trading_loop(self, mock_exchange, mock_fetcher):
        """Test complete flow: data → signal → execution → state."""

        # 1. Setup: Mock exchange with fake balances
        mock_exchange.get_account.return_value = {'equity': 10000}

        # 2. Mock data fetch (simulated BTC price data)
        mock_fetcher.fetch_ohlcv.return_value = create_sweep_setup()

        # 3. Execute: Run bot for 1 iteration
        bot = LiveTradingBot(strategy='liquidity_sweep')
        bot.run_iteration()

        # 4. Verify: Signal detected, order placed, state saved
        assert mock_exchange.place_order.called
        assert bot.state_manager.get_open_positions() == 1
        assert os.path.exists('state/bot_state.json')

    def test_circuit_breaker_stops_trading(self):
        """Test bot auto-shutdown on 20% drawdown."""
        # Simulate losses → verify auto-stop
```

**Success Criteria:**
- [ ] Happy path E2E test passing
- [ ] All failure modes handled gracefully
- [ ] State persistence verified across scenarios
- [ ] Circuit breakers tested

**Risks & Mitigation:**
- **Risk:** Hard to mock complex exchange behavior
- **Mitigation:** Start simple (happy path), add complexity incrementally

---

### Task 3: Portfolio-Level Risk Controls
**Current State:** Only per-trade risk limits ⚠️

**Target:** Portfolio-wide exposure management ✅

**Time Estimate:** 6-8 hours

**Subtasks:**
1. **Design Portfolio Risk System** (2h)
   - Max total exposure (e.g., 20% of portfolio in all positions)
   - Max correlated exposure (e.g., 30% in BTC-correlated assets)
   - Max positions per symbol (e.g., 1 position per asset)
   - Max concurrent positions (e.g., 3 total positions)

2. **Implement Portfolio Risk Manager** (3-4h)
   - Create `risk/portfolio_risk.py`
   - Add methods:
     - `check_portfolio_exposure() → bool`
     - `check_correlation_limits() → bool`
     - `get_available_risk() → float`
   - Integrate with `live/bot.py` (pre-trade validation)

3. **Add Tests** (2-3h)
   - Test: Reject trade if portfolio exposure exceeds limit
   - Test: Allow trade if within limits
   - Test: Correlation calculation (BTC vs ETH vs SOL)
   - Test: Edge case - all capital in existing positions

**Implementation Notes:**
```python
# risk/portfolio_risk.py

from typing import Dict, List
import pandas as pd

class PortfolioRiskManager:
    """Manages portfolio-level risk constraints."""

    def __init__(
        self,
        max_portfolio_exposure: float = 0.20,  # 20% max
        max_correlated_exposure: float = 0.30,  # 30% max
        max_positions: int = 3
    ):
        self.max_portfolio_exposure = max_portfolio_exposure
        self.max_correlated_exposure = max_correlated_exposure
        self.max_positions = max_positions

    def check_new_trade(
        self,
        symbol: str,
        position_size: float,
        current_positions: List[Dict],
        portfolio_value: float
    ) -> Dict[str, any]:
        """Validate if new trade meets portfolio risk limits.

        Returns:
            {
                'allowed': bool,
                'reason': str,
                'current_exposure': float,
                'new_exposure': float
            }
        """
        # Calculate current exposure
        current_exposure = sum(p['size'] for p in current_positions)
        new_exposure = current_exposure + position_size
        exposure_pct = new_exposure / portfolio_value

        # Check limits
        if len(current_positions) >= self.max_positions:
            return {
                'allowed': False,
                'reason': f'Max positions ({self.max_positions}) reached'
            }

        if exposure_pct > self.max_portfolio_exposure:
            return {
                'allowed': False,
                'reason': f'Portfolio exposure ({exposure_pct:.1%}) exceeds limit ({self.max_portfolio_exposure:.1%})'
            }

        # Check correlation (if BTC position exists, limit other crypto)
        btc_positions = [p for p in current_positions if 'BTC' in p['symbol']]
        if btc_positions and 'BTC' not in symbol:
            # Simplified correlation check (assume all crypto 70% correlated to BTC)
            correlated_exposure = sum(p['size'] for p in btc_positions) + position_size
            if correlated_exposure / portfolio_value > self.max_correlated_exposure:
                return {
                    'allowed': False,
                    'reason': f'Correlated exposure exceeds {self.max_correlated_exposure:.1%}'
                }

        return {
            'allowed': True,
            'reason': 'Within risk limits',
            'current_exposure': current_exposure,
            'new_exposure': new_exposure
        }
```

**Success Criteria:**
- [ ] Portfolio risk manager implemented
- [ ] Integrated with live bot (pre-trade checks)
- [ ] Tests ≥80% coverage
- [ ] Prevents over-concentration in backtests

**Risks & Mitigation:**
- **Risk:** Correlation calculation too simplistic
- **Mitigation:** Start with basic rules, refine in Sprint 5 based on testnet data

---

### Task 4: 7-Day Testnet Validation
**Current State:** Short manual tests only ⚠️

**Target:** Continuous 7-day run with zero crashes ✅

**Time Estimate:** 1 hour setup + 7 days monitoring (15 min/day)

**Subtasks:**
1. **Setup Validation Environment** (1h)
   - Configure bot for 7-day run
   - Setup automated logging
   - Configure alerts (email/log on critical errors)
   - Document start conditions (capital, strategy, params)

2. **Daily Monitoring** (15 min/day × 7 days)
   - Check logs for errors/warnings
   - Verify state persistence (no corruption)
   - Monitor performance metrics:
     - Uptime %
     - Trades executed
     - Circuit breaker triggers (if any)
     - API errors (count, types)
   - Document any issues

3. **End-of-Run Analysis** (2h)
   - Generate final report
   - Analyze failure modes (if any)
   - Calculate uptime % (target: 99.9%)
   - Review trade quality (PnL, win rate, risk metrics)

**Implementation Notes:**
```bash
# Start 7-day validation (Week 1, Day 3)
cd /home/user/FractalTrader
python -m live.cli start \
  --strategy liquidity_sweep \
  --capital 10000 \
  --risk-per-trade 0.02 \
  --log-level INFO

# Daily check (run each morning)
python -m live.cli status --detailed
python -m live.cli report --last 24h

# Monitor logs
tail -f logs/bot_$(date +%Y%m%d).log | grep -i "error\|warning\|critical"
```

**Success Criteria:**
- [ ] 7 consecutive days running
- [ ] Uptime ≥99.9% (max 10 min downtime)
- [ ] Zero unhandled crashes
- [ ] All trades logged correctly
- [ ] State persistence verified (no corruption)
- [ ] Circuit breakers tested (simulate drawdown)

**Risks & Mitigation:**
- **Risk:** Exchange API downtime (beyond our control)
- **Mitigation:** Implement graceful degradation (pause trading, don't crash)

---

### Task 5: Monitoring Dashboard
**Current State:** CLI-only monitoring ⚠️

**Target:** Real-time web dashboard with health checks ✅

**Time Estimate:** 8-10 hours

**Subtasks:**
1. **Choose Tech Stack** (1h)
   - Option A: Simple Flask + Plotly (lightweight, fast to build)
   - Option B: Streamlit (interactive, minimal code)
   - **Decision:** Streamlit (faster iteration, built-in refresh)

2. **Build Core Dashboard** (4-5h)
   - Create `monitoring/dashboard.py`
   - Panels:
     1. **System Health** (uptime, last update, bot status)
     2. **Performance Metrics** (PnL, win rate, Sharpe ratio)
     3. **Active Positions** (symbol, size, entry price, unrealized PnL)
     4. **Recent Trades** (last 20 trades with outcomes)
     5. **Risk Metrics** (current exposure, drawdown, circuit breaker status)
     6. **Error Log** (last 50 errors/warnings)

3. **Add Health Checks** (2-3h)
   - Heartbeat monitoring (bot alive?)
   - State file integrity check
   - Exchange connectivity check
   - Data freshness check (last candle < 5 min old)
   - Alert if any check fails

4. **Add Tests** (1-2h)
   - Test: Dashboard loads without errors
   - Test: Displays metrics correctly
   - Test: Health checks detect failures

**Implementation Notes:**
```python
# monitoring/dashboard.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from live.state_manager import StateManager

st.set_page_config(page_title="FractalTrader Monitor", layout="wide")

# Header
st.title("🤖 FractalTrader Live Monitor")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Load state
state_mgr = StateManager()
state = state_mgr.get_state()

# === SYSTEM HEALTH ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    status = "🟢 Running" if state['running'] else "🔴 Stopped"
    st.metric("Status", status)

with col2:
    uptime_hours = (datetime.now() - datetime.fromisoformat(state['start_time'])).total_seconds() / 3600
    st.metric("Uptime", f"{uptime_hours:.1f}h")

with col3:
    total_trades = len(state['trade_history'])
    st.metric("Total Trades", total_trades)

with col4:
    equity = state['equity']
    st.metric("Equity", f"${equity:,.2f}")

# === PERFORMANCE ===
st.subheader("📊 Performance")

perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)

trades_df = pd.DataFrame(state['trade_history'])
if not trades_df.empty:
    winning_trades = len(trades_df[trades_df['pnl'] > 0])
    win_rate = winning_trades / len(trades_df) * 100
    total_pnl = trades_df['pnl'].sum()
    avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
    avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if len(trades_df) > winning_trades else 0

    perf_col1.metric("Win Rate", f"{win_rate:.1f}%")
    perf_col2.metric("Total PnL", f"${total_pnl:,.2f}")
    perf_col3.metric("Avg Win", f"${avg_win:.2f}")
    perf_col4.metric("Avg Loss", f"${avg_loss:.2f}")

# === ACTIVE POSITIONS ===
st.subheader("📍 Active Positions")
positions_df = pd.DataFrame(state['open_positions'])
if not positions_df.empty:
    st.dataframe(positions_df, use_container_width=True)
else:
    st.info("No open positions")

# === RECENT TRADES ===
st.subheader("📜 Recent Trades (Last 20)")
if not trades_df.empty:
    recent = trades_df.tail(20).sort_values('exit_time', ascending=False)
    st.dataframe(recent, use_container_width=True)

# === HEALTH CHECKS ===
st.subheader("🏥 Health Checks")

health_col1, health_col2, health_col3 = st.columns(3)

# Check 1: Heartbeat (last update < 5 min ago)
last_update = datetime.fromisoformat(state.get('last_update', datetime.now().isoformat()))
heartbeat_ok = (datetime.now() - last_update).total_seconds() < 300
health_col1.metric("Heartbeat", "✅ OK" if heartbeat_ok else "❌ STALE")

# Check 2: State file integrity
state_file_ok = state_mgr.validate_state()
health_col2.metric("State File", "✅ OK" if state_file_ok else "❌ CORRUPT")

# Check 3: Circuit breakers
circuit_breaker_triggered = state.get('circuit_breaker_triggered', False)
health_col3.metric("Circuit Breaker", "🔴 TRIGGERED" if circuit_breaker_triggered else "✅ OK")

# Auto-refresh every 30s
st.button("Refresh Now")
```

**Usage:**
```bash
# Run dashboard
cd monitoring/
streamlit run dashboard.py --server.port 8501

# Access: http://localhost:8501
```

**Success Criteria:**
- [ ] Dashboard displays all key metrics
- [ ] Auto-refresh (30s intervals)
- [ ] Health checks functional
- [ ] Works with live bot state
- [ ] Mobile-friendly (responsive design)

**Risks & Mitigation:**
- **Risk:** Dashboard overhead slows down bot
- **Mitigation:** Read-only access to state (no writes), separate process

---

## 🔥 High Priority Tasks (Priority 2)

### Task 6: Disaster Recovery Procedures
**Time Estimate:** 3-4 hours

**Deliverables:**
1. **Incident Response Playbook** (`docs/INCIDENT_RESPONSE.md`)
   - Exchange disconnect recovery
   - State file corruption recovery
   - Emergency shutdown procedure
   - Lost internet connection handling
   - API key compromise response

2. **Automated Recovery Scripts**
   - `scripts/emergency_shutdown.sh` - Kill bot, close all positions
   - `scripts/recover_state.sh` - Restore from backup
   - `scripts/health_check.sh` - Validate system integrity

3. **Tests for Recovery Procedures**
   - Test: State recovery from backup
   - Test: Emergency shutdown closes positions
   - Test: Corruption detection works

**Implementation:**
```markdown
# docs/INCIDENT_RESPONSE.md

## Emergency Shutdown

**When:** Critical error, loss of control, unexpected behavior

**Steps:**
1. Run emergency shutdown:
   ```bash
   ./scripts/emergency_shutdown.sh
   ```
2. Verify all positions closed (check exchange UI)
3. Stop bot process: `python -m live.cli stop`
4. Investigate logs: `tail -100 logs/bot_latest.log`
5. Document incident in `incidents/YYYYMMDD_description.md`

## State File Corruption

**Symptoms:** Bot crashes on startup, JSON parse errors

**Recovery:**
1. Stop bot (if running)
2. List backups: `ls -lh state/backups/`
3. Restore latest backup:
   ```bash
   ./scripts/recover_state.sh
   ```
4. Verify state integrity:
   ```bash
   python -c "from live.state_manager import StateManager; StateManager().validate_state()"
   ```
5. Restart bot: `python -m live.cli start`

## Exchange API Disconnect

**Symptoms:** ConnectionError, Timeout errors in logs

**Auto-Recovery:**
- Bot retries 3x with exponential backoff (2s, 4s, 8s)
- If all retries fail → pause trading, log error, continue monitoring

**Manual Intervention:**
1. Check exchange status (Twitter, status page)
2. If exchange down >30 min → emergency shutdown
3. Wait for exchange recovery
4. Restart bot when confirmed operational
```

**Success Criteria:**
- [ ] Playbook documented
- [ ] Recovery scripts tested
- [ ] Team can execute without bot creator

---

### Task 7: Walk-Forward Validation
**Time Estimate:** 6-8 hours

**Goal:** Test strategy robustness, prevent overfitting

**Methodology:**
1. Split historical data into 6 periods (2 months each)
2. Train on Period 1 → Test on Period 2
3. Train on Periods 1-2 → Test on Period 3
4. Continue rolling forward
5. Verify: Strategy performance remains consistent

**Implementation:**
```python
# tests/test_walk_forward.py

def test_liquidity_sweep_walk_forward():
    """Test strategy stability across time periods."""

    periods = [
        ('2024-01-01', '2024-02-28'),  # Train 1
        ('2024-03-01', '2024-04-30'),  # Test 1
        ('2024-05-01', '2024-06-30'),  # Test 2
        ('2024-07-01', '2024-08-31'),  # Test 3
    ]

    results = []

    for i in range(1, len(periods)):
        # Train on all periods up to i
        train_data = fetch_data(periods[0][0], periods[i-1][1])

        # Test on period i
        test_data = fetch_data(periods[i][0], periods[i][1])

        # Run backtest
        strategy = LiquiditySweepStrategy()
        perf = run_backtest(strategy, test_data)

        results.append({
            'period': periods[i],
            'sharpe': perf.sharpe_ratio,
            'win_rate': perf.win_rate,
            'total_return': perf.total_return
        })

    # Verify: Performance doesn't degrade significantly
    sharpe_ratios = [r['sharpe'] for r in results]
    assert min(sharpe_ratios) > 0.5  # No period falls below 0.5 Sharpe
    assert max(sharpe_ratios) / min(sharpe_ratios) < 3  # Variance within 3x
```

**Success Criteria:**
- [ ] Walk-forward tests implemented for all strategies
- [ ] Performance stable across periods (Sharpe variance <3x)
- [ ] Overfitting risk assessed

---

## 📅 Week-by-Week Plan

### **Week 1: Testing & Validation Foundation** (Feb 4-10)

**Day 1-2 (Feb 4-5): Strategy Tests**
- [ ] Implement Liquidity Sweep tests (70%+ coverage)
- [ ] Implement BOS Order Block tests (70%+ coverage)
- [ ] Run full test suite → verify all passing

**Day 3-4 (Feb 6-7): Integration & Risk**
- [ ] Build E2E integration test framework
- [ ] Implement portfolio risk manager
- [ ] Integrate portfolio risk with live bot
- [ ] **START 7-day testnet validation** (runs through Feb 13)

**Day 5 (Feb 8): Monitoring Foundation**
- [ ] Setup Streamlit dashboard (core panels)
- [ ] Implement health checks
- [ ] Test dashboard with live bot

**Weekend (Feb 9-10): Monitoring & Docs**
- [ ] Enhance dashboard (error logs, alerts)
- [ ] Write incident response playbook
- [ ] Daily testnet monitoring (15 min/day)

---

### **Week 2: Hardening & Validation** (Feb 11-17)

**Day 6-7 (Feb 11-12): Walk-Forward & Recovery**
- [ ] Implement walk-forward validation tests
- [ ] Run walk-forward analysis for all strategies
- [ ] Build disaster recovery scripts
- [ ] Test recovery procedures

**Day 8-9 (Feb 13-14): Testnet Analysis**
- [ ] Complete 7-day testnet validation
- [ ] Analyze results (uptime, trades, errors)
- [ ] Fix any issues discovered
- [ ] Re-run critical scenarios if needed

**Day 10 (Feb 15): Documentation & Cleanup**
- [ ] Archive old docs to `docs-archive/`
- [ ] Update `DEVELOPMENT.md` with Sprint 4 results
- [ ] Update `deployment.md` production readiness %
- [ ] Write Sprint 4 final report

**Day 11-12 (Feb 16-17): Final Validation & Retrospective**
- [ ] Run full test suite (311+ tests)
- [ ] Verify all success criteria met
- [ ] Generate coverage report (target: 95%+)
- [ ] Sprint retrospective
- [ ] Plan Sprint 5 (Tribal Weather MVP)

---

## ✅ Success Criteria

### Must Have (Critical):
- [ ] **Strategy coverage:** All strategies ≥70% (currently 13-42%)
- [ ] **E2E tests:** Full trading loop validated, all failure modes handled
- [ ] **Portfolio risk:** Implemented and tested (prevents over-concentration)
- [ ] **7-day testnet:** Completed with ≥99.9% uptime, zero crashes
- [ ] **Monitoring:** Dashboard functional with health checks

### Should Have (Important):
- [ ] **Disaster recovery:** Playbook documented, scripts tested
- [ ] **Walk-forward:** Strategy robustness validated
- [ ] **Documentation:** Up-to-date, old docs archived

### Metrics:
- [ ] **Overall coverage:** ≥95% (currently 92%)
- [ ] **Production readiness:** ≥95% (currently 85%)
- [ ] **Test count:** ≥350 tests (currently 311)
- [ ] **Open critical bugs:** 0

---

## ⚠️ Risk Management

### Technical Risks:

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Strategy tests reveal critical bugs | High | Medium | Fix immediately, re-validate |
| 7-day testnet run crashes | Medium | Low | Auto-restart, daily monitoring |
| E2E tests hard to implement | Low | Medium | Start simple, iterate |
| Walk-forward shows overfitting | High | Medium | Simplify strategy, add robustness checks |

### Timeline Risks:

| Risk | Impact | Mitigation |
|------|--------|------------|
| Strategy tests take longer than estimated | Medium | Priority 1, allocate extra time |
| 7-day validation delayed | Low | Can extend into Week 2 |
| Scope creep (too many nice-to-haves) | Medium | Strict priority enforcement |

**Contingency:**
- If behind schedule by Day 5 → Cut Priority 3 tasks
- If critical bug found → Pause new features, fix immediately
- If testnet validation fails → Extend sprint by 3 days (acceptable)

---

## 📊 Testing Strategy

### Unit Tests (80% of effort):
- Fast (<10s total)
- No Docker required
- Mock all external dependencies
- Target: ≥350 tests

### Integration Tests (15% of effort):
- Docker-based (Docker Compose)
- Real database, mocked exchange
- Target: Full trading loop validated

### E2E Tests (5% of effort):
- 7-day testnet validation
- Real exchange (testnet)
- Manual monitoring + automated logging

**Test Execution:**
```bash
# Fast unit tests (no Docker)
python -m pytest tests/ -v --tb=short \
  --ignore=tests/test_backtesting.py \
  --ignore=tests/test_data_fetchers.py \
  --ignore=tests/test_live_trading.py

# Full integration tests (Docker required)
./docker-start.sh test

# Coverage report
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term
```

---

## 📦 Deliverables

### Code:
1. ✅ `tests/test_strategies.py` - Strategy tests (70%+ coverage)
2. ✅ `tests/test_e2e_integration.py` - End-to-end tests
3. ✅ `risk/portfolio_risk.py` - Portfolio risk manager
4. ✅ `monitoring/dashboard.py` - Streamlit monitoring dashboard
5. ✅ `scripts/emergency_shutdown.sh` - Emergency procedures
6. ✅ `scripts/recover_state.sh` - State recovery automation

### Documentation:
1. ✅ `docs/INCIDENT_RESPONSE.md` - Disaster recovery playbook
2. ✅ `docs/SPRINT_4_REPORT.md` - Final sprint report
3. ✅ Updated `DEVELOPMENT.md` - New coverage metrics
4. ✅ Updated `deployment.md` - Production readiness %
5. ✅ `docs/WALK_FORWARD_ANALYSIS.md` - Robustness results

### Reports:
1. ✅ 7-day testnet validation report
2. ✅ Test coverage report (HTML)
3. ✅ Walk-forward validation results
4. ✅ Sprint retrospective

---

## 🎯 Post-Sprint State

**By Feb 17, 2025, FractalTrader will be:**

✅ **Production-hardened** (95%+ readiness)
✅ **Fully tested** (350+ tests, 95%+ coverage)
✅ **Battle-tested** (7-day validation completed)
✅ **Observable** (monitoring dashboard deployed)
✅ **Resilient** (disaster recovery procedures documented)
✅ **Robust** (walk-forward validation passed)

**Ready for:** Sprint 5 (Tribal Weather MVP) and eventual Sprint 6 (Live Trading)

---

## 📝 Notes for Implementation

### Philosophy:
- **Quality > Speed** - No live trading pressure, focus on excellence
- **Test Everything** - If it's not tested, it's broken
- **Document Decisions** - Future you will thank present you
- **Automate Recovery** - Assume failures will happen, prepare responses

### Daily Routine:
1. Morning: Check testnet status (15 min)
2. Work: Focus on Priority 1 tasks first
3. Evening: Run test suite, commit progress
4. Document: Update sprint progress in GitHub issues

### When Blocked:
1. Document the blocker
2. Move to next task
3. Ask for help if blocked >2 hours
4. Don't let blockers stop sprint progress

---

**Sprint 4 Motto:** *"Build it bulletproof, because bullets are coming."* 🛡️

**Let's ship production-grade code.** 🚢
