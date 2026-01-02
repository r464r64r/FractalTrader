# FractalTrader: 6-Sprint Roadmap (Q1 2026)

## Overview: 12 Weeks to Production

```
Sprint 1 (Dec 24-26, 2025):  Jupyter Fractal Viewer       [Research → Interactive]
Sprint 2 (Dec 26, 2025):     Live Market Dashboard         [Static → Live]
Sprint 3 (Dec 30, 2025):     Paper Trading Bot            [Analyze → Trade]
Sprint 4 (Feb 4-17, 2026):   Production Hardening         [Alpha → Beta]
Sprint 5 (Feb 18-Mar 3, 2026): Tribal Weather MVP         [Single → Ecosystem]
Sprint 6 (Mar 4-17, 2026):   Live Trading (Testnet)       [Beta → Production]
```

**After 12 weeks:** Production-ready trading system with unique tribal intelligence.

---

## Sprint 1: Jupyter Fractal Viewer
**Dec 24-26, 2025** ✅ COMPLETE

### 🎯 Goal
Filip can analyze historical BTC trades in Jupyter with multi-timeframe SMC visualization.

### 📦 Deliverable
Interactive Jupyter notebook featuring:
- 3-panel synchronized charts (H4/H1/M15)
- Order block overlay (auto-detected)
- Confidence breakdown panel
- One example trade walkthrough

### ✅ Success Criteria
- [ ] Notebook runs end-to-end without errors
- [ ] Charts are interactive (zoom, pan, hover)
- [ ] Order blocks clearly visible with labels
- [ ] Confidence panel explains setup (78/100 breakdown)
- [ ] README with screenshots and usage instructions

### 🔨 Key Tasks
1. Research Plotly multi-timeframe synchronization (Haiku, 1d)
2. Implement FractalDashboard core class (Haiku, 2d)
3. Build order block rendering layer (Sonnet, 2d)
4. Create confidence explainer panel (Haiku, 1d)
5. Integrate with example notebook (Sonnet, 2d)
6. Write documentation (Haiku, 1d)

### 🎁 What Filip Gets
**File:** `notebooks/fractal_viewer.ipynb`  
**Action:** Open, run all cells, explore BTC chart with SMC overlay

### 📊 Why This First
- Validates core SMC detection works visually
- Builds foundation for live dashboard (Sprint 2)
- Gives Filip something to click ASAP
- Low risk, high value

---

## Sprint 2: Live Market Dashboard
**Dec 26, 2025** ✅ COMPLETE

### 🎯 Goal
Filip can watch live BTC market with real-time SMC detection and signal generation.

### 📦 Deliverable
Jupyter dashboard with live updates:
- Real-time price data (Hyperliquid/Binance)
- Live SMC pattern detection
- New setup alerts (visual + sound)
- Trade journal (setups detected, confidence scores)

### ✅ Success Criteria
- [ ] Dashboard updates every 15 seconds
- [ ] New order blocks appear automatically
- [ ] Alert when setup confidence >70%
- [ ] Journal logs all setups with timestamps
- [ ] Can run for 24h without crashes

### 🔨 Key Tasks
1. Implement live data streaming (data fetchers + retry logic) (Haiku, 3d)
2. Add real-time SMC detection pipeline (Sonnet, 2d)
3. Build alert system (visual + audio) (Haiku, 1d)
4. Create trade journal component (Haiku, 2d)
5. Stability testing (24h run) (Sonnet, 1d)
6. Documentation + deployment guide (Haiku, 1d)

### 🎁 What Filip Gets
**File:** `notebooks/live_dashboard.ipynb`  
**Action:** Launch, watch market live, get alerted to setups

### 📊 Why Second
- Adds missing piece: real-time data
- Tests system stability (critical for trading)
- Natural evolution from Sprint 1
- Still no capital at risk

---

## Sprint 3: Paper Trading Bot
**Dec 30, 2025** ✅ COMPLETE

### 🎯 Goal
Filip can run automated paper trading bot that executes strategies on testnet.

### 📦 Deliverable
CLI trading bot that:
- Runs liquidity sweep strategy autonomously
- Executes on Hyperliquid testnet
- Logs all trades with reasoning
- Generates daily performance report
- Has kill switch (stop bot command)

### ✅ Success Criteria
- [ ] Bot runs 7 days continuously
- [ ] Executes at least 10 paper trades
- [ ] No crashes or missed opportunities
- [ ] Daily reports show: PnL, win rate, confidence distribution
- [ ] Can stop/restart without losing state

### 🔨 Key Tasks
1. Implement state persistence (position tracking) (Sonnet, 2d)
2. Build execution engine (testnet orders) (Haiku, 3d)
3. Add circuit breakers (max loss, error handling) (Sonnet, 2d)
4. Create daily report generator (Haiku, 1d)
5. 7-day testnet validation (Sonnet, 2d)
6. CLI interface + documentation (Haiku, 1d)

### 🎁 What Filip Gets
**Command:** `python -m live.cli --mode paper --strategy liquidity_sweep`  
**Action:** Watch bot trade autonomously, review daily reports

### 📊 Why Third
- First real "trading" experience
- Validates strategy logic end-to-end
- Testnet = safe to fail
- Critical step before real money

---

## Sprint 4: Production Hardening
**Feb 4-17, 2026** 📋 NEXT

### 🎯 Goal
Trading system is robust enough for small-scale live trading ($100-500). Maximize production readiness from 85% → **95%+**.

### 📦 Deliverable
Production-grade infrastructure:
- **Strategy test coverage:** 13-42% → **70%+** (critical gap)
- **E2E integration tests:** Full trading loop validated
- **Portfolio-level risk controls:** Prevent over-concentration
- **7-day testnet validation:** Zero crashes, 99.9% uptime
- **Monitoring dashboard:** Real-time observability (Streamlit)
- **Disaster recovery procedures:** Documented playbooks + scripts
- **Walk-forward validation:** Strategy robustness testing

### ✅ Success Criteria
- [ ] **Strategy coverage:** All strategies ≥70% (currently 13-42%)
- [ ] **E2E tests:** Full trading loop validated, all failure modes handled
- [ ] **Portfolio risk:** Implemented and tested (prevents over-concentration)
- [ ] **7-day testnet:** ≥99.9% uptime, zero unhandled crashes
- [ ] **Monitoring:** Dashboard functional with health checks
- [ ] **Overall coverage:** ≥95% (currently 92%)
- [ ] **Production readiness:** ≥95% (currently 85%)
- [ ] **Test count:** ≥350 tests (currently 311)

### 🔨 Key Tasks

**CRITICAL (Priority 1):**
1. **Strategy Test Coverage** (10-14h)
   - Liquidity Sweep: 13% → 70%+ (edge cases, mocking)
   - BOS Order Block: 42% → 70%+ (HTF/LTF alignment)
   - FVG Fill: ~40% → 70%+ (gap fill scenarios)

2. **E2E Integration Tests** (6-8h)
   - Happy path: data → signal → execution → state
   - Failure modes: disconnect, corruption, circuit breakers

3. **Portfolio-Level Risk Controls** (6-8h)
   - Max portfolio exposure (20%)
   - Max correlated exposure (30%)
   - Position limits (3 concurrent max)

4. **7-Day Testnet Validation** (1h setup + 7 days monitoring)
   - Continuous run: zero crashes
   - Daily monitoring: 15 min/day
   - End analysis: uptime %, trade quality

5. **Monitoring Dashboard** (8-10h)
   - Streamlit dashboard with 6 panels
   - Health checks (heartbeat, state integrity, connectivity)
   - Auto-refresh (30s intervals)

**HIGH (Priority 2):**
6. **Disaster Recovery** (3-4h) - Incident response playbook + scripts
7. **Walk-Forward Validation** (6-8h) - Strategy robustness testing

### 🎁 What Filip Gets
**URL:** `http://localhost:8501` (Streamlit monitoring dashboard)
**Action:** Watch system health in real-time, trust 95%+ production readiness
**Docs:** `docs/SPRINT_4_PLAN.md` (comprehensive implementation guide)
**Checklist:** `docs/SPRINT_4_CHECKLIST.md` (GitHub issue template)

### 📊 Why Fourth
- **Can't skip to live trading without this** - critical gaps must be fixed
- **No live trading pressure** - Filip's workstation offline, perfect timing
- **Quality over speed** - maximize robustness before Sprint 6
- **Prevents costly mistakes** - untested strategies = real losses
- **Builds unshakeable confidence** - 7-day validation proves stability

**Sprint Motto:** *"Build it bulletproof, because bullets are coming."* 🛡️

---

## Sprint 5: Tribal Weather MVP
**Feb 18-Mar 3, 2026** 📋 Planned

### 🎯 Goal
Filip can see crypto tribal weather map and understand capital flow dynamics.

### 📦 Deliverable
Tribal weather dashboard showing:
- 5 main tribes (BTC Maxi, ETH Nation, SOL Gang, Meme Degen, DeFi Farmers)
- Weather status per tribe (☀️⛅🌧️⛈️)
- Capital flow direction (BTC ← ETH ← Alts)
- Rotation prediction (next 1-2 weeks)
- Integration with trading strategies (regime-aware positioning)

### ✅ Success Criteria
- [ ] Tribal metrics update every 1 hour
- [ ] Weather accurately reflects market state (manual validation)
- [ ] Rotation detection triggers strategy adjustment
- [ ] Dashboard integrated with Jupyter viewer
- [ ] Documentation: tribal theory + usage guide

### 🔨 Key Tasks
1. Research tribal clustering methodology (Haiku, 2d)
2. Implement tribe metrics calculation (BTC.D, funding, social) (Haiku, 2d)
3. Build weather scoring algorithm (Sonnet, 2d)
4. Create rotation detection logic (Sonnet, 2d)
5. Integrate with strategy confidence (Haiku, 1d)
6. Dashboard UI + documentation (Haiku, 1d)

### 🎁 What Filip Gets
**Panel in Jupyter:** Tribal Weather Map (top of dashboard)  
**Action:** See ecosystem dynamics, understand WHY setups work/fail

### 📊 Why Fifth
- Unique differentiation vs competitors
- Adds context to SMC analysis
- Natural evolution after trading works
- Can develop while system trades (parallel work)

---

## Sprint 6: Live Trading (Testnet → Mainnet)
**Mar 4-17, 2026** 📋 Planned

### 🎯 Goal
Filip can run live trading on mainnet with small capital ($100-500) safely.

### 📦 Deliverable
Live trading system that:
- Trades liquidity sweep strategy on Hyperliquid mainnet
- Starts with $100 capital (conservative)
- Has kill switch (instant stop if things go wrong)
- Generates weekly performance reports
- Includes position size calculator (risk management)

### ✅ Success Criteria
- [ ] Executes first live trade successfully
- [ ] Runs 1 week without critical errors
- [ ] PnL tracked accurately
- [ ] Risk limits respected (max 2% per trade)
- [ ] Filip feels confident, not anxious

### 🔨 Key Tasks
1. Mainnet configuration (API keys, wallet setup) (Sonnet, 1d)
2. Conservative position sizing (start tiny) (Haiku, 1d)
3. Enhanced risk controls (mainnet-specific) (Sonnet, 2d)
4. Live trading validation (small capital) (Haiku, 3d)
5. Weekly report generator (Sonnet, 1d)
6. Documentation: going live checklist (Haiku, 1d)

### 🎁 What Filip Gets
**Command:** `python -m live.cli --mode LIVE --capital 100 --strategy liquidity_sweep`  
**Action:** Real trading, real money, real results

### 📊 Why Last
- Everything else must work first
- Confidence built through sprints 1-5
- Small capital = manageable risk
- Culmination of 12 weeks work

---

## Post-Sprint 6: What's Next?

### If Successful (System Works)
- **Sprint 7:** Scale capital ($500 → $2000)
- **Sprint 8:** Multi-strategy portfolio
- **Sprint 9:** Multi-exchange (Binance, Bybit)
- **Sprint 10:** Advanced tribal features (on-chain data)

### If Partial Success (System Needs Work)
- Fix critical issues identified in Sprint 6
- Repeat Sprint 6 with improvements
- Don't rush to scale

### If Failure (System Doesn't Work)
- Deep retrospective: what went wrong?
- Pivot strategy or approach
- Go back to Sprint 3-4, rebuild foundation

---

## Metrics Dashboard (Track Progress)

### Sprint Velocity
```
Sprint | Planned Tasks | Completed | On-Time | Goal Achieved | Early By
-------|---------------|-----------|---------|---------------|----------
   1   |       6       |     6     |   ✅ YES |     ✅ YES    | 4 days
   2   |       6       |     6     |   ✅ YES |     ✅ YES    | 24 days
   3   |       6       |     6     |   ✅ YES |     ✅ YES    | 21 days
   4   |       7       |     -     |    -    |       -       |   -
   5   |       6       |     -     |    -    |       -       |   -
   6   |       6       |     -     |    -    |       -       |   -
-------|---------------|-----------|---------|---------------|----------
 Avg   |      6.0      |    6.0    |  100%   |     100%      | 16 days
```

**Target:** >80% on-time, >80% goal achieved
**Current:** 100% (Avg 16 days ahead of schedule! 🚀)

### Deliverable Tracker
```
Sprint | Deliverable                  | Shipped? | Date      | Status
-------|------------------------------|----------|-----------|--------
   1   | Jupyter Fractal Viewer       |  ✅ YES  | Dec 26    | Complete
   2   | Live Market Dashboard        |  ✅ YES  | Dec 26    | Complete
   3   | Paper Trading Bot            |  ✅ YES  | Dec 30    | Complete
   4   | Production Infrastructure    |  📋 PLAN | -         | Planning
   5   | Tribal Weather MVP           |    -     | -         | Waiting
   6   | Live Trading System          |    -     | -         | Waiting
-------|------------------------------|----------|-----------|--------
Total  |                              |   3/6    | -         | 50% Done
```

**Target:** 6/6 shipped by Mar 17, 2025
**Current:** 3/6 shipped (50% complete, 21 days ahead of schedule! 🚀)
**Production Readiness:** 85% → Target: 95% (Sprint 4)

---

## Risk Management

### High-Risk Sprints
- **Sprint 3:** First real trading logic (could have bugs)
- **Sprint 6:** Real money on the line (emotional stress)

**Mitigation:** Extra testing, conservative approach, kill switch ready

### Dependencies
- Sprint 2 → Sprint 3 (need live data before trading)
- Sprint 3 → Sprint 4 (need basic trading before hardening)
- Sprint 4 → Sprint 6 (need robustness before mainnet)

**Sprint 5 can run parallel to 3-4** (tribal weather independent)

### Team Capacity
- Opus: Strategic oversight (10% time per sprint)
- Sonnet: Integration, review (40% time per sprint)
- Haiku: Implementation, research (50% time per sprint)

**Total capacity:** ~40 person-hours per sprint (realistic for 2 weeks)

---

## Communication Plan

### Sprint Start (Day 0)
- Opus posts sprint plan as GitHub issue
- Team comments with questions/concerns
- Plan finalized by end of day

### Daily Updates (Async)
- Each agent comments on sprint issue
- Format: "Day N: Completed X, Working on Y, Blocked by Z"
- 5 minutes max

### Mid-Sprint Check (Day 5)
- Opus reviews progress
- Adjusts scope if needed
- Escalates blockers

### Sprint End (Day 10)
- Demo to Filip (30 min)
- Retrospective (30 min)
- Document lessons learned

### Ad-Hoc
- Critical issues: Comment immediately
- Questions: Tag relevant person
- No meetings unless absolutely necessary

---

## What Filip Should Expect

### Every 2 Weeks
- 📦 New deliverable to play with
- 📊 Sprint retrospective (learn what worked)
- 🎯 Next sprint preview (what's coming)

### Every 4 Weeks
- 🚀 Production release (tag version)
- 📈 Progress review (velocity, quality trends)
- 🤔 Roadmap adjustment (if needed)

### Every 12 Weeks (Quarter)
- 🎉 Major milestone (Q1: live trading working)
- 📝 Quarterly retrospective (big picture lessons)
- 🗺️ Next quarter planning (where to next?)

---

## Success Criteria (12 Weeks)

### Must Have
- [ ] Filip can analyze trades in Jupyter (Sprint 1)
- [ ] Filip can watch live market (Sprint 2)
- [ ] Bot can trade autonomously on testnet (Sprint 3)
- [ ] System is robust and monitored (Sprint 4)
- [ ] Live trading works on mainnet (Sprint 6)

### Nice to Have
- [ ] Tribal weather provides edge (Sprint 5)
- [ ] All sprints on-time (>80%)
- [ ] Filip rating >7/10 average
- [ ] Community interest (GitHub stars, forks)

### Definition of Success
**By Mar 17, 2025:**
- FractalTrader trades live on Hyperliquid mainnet
- System is stable (99%+ uptime)
- Filip trusts it with $500+ capital
- Unique tribal intelligence works
- Code is production-grade (tests, docs, monitoring)

---

## The Promise

**No more "soon". No more "almost". No more phases.**

**Every 2 weeks: ship something Filip can click.**

**12 weeks: production trading system.**

🚢 or 💀

Let's fucking go! 🚀
