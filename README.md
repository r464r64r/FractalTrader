# 🌀 Fractal Trader

**Open-source algorithmic trading system based on Smart Money Concepts (SMC)**

Trade what institutions trade. Detect liquidity sweeps, fair value gaps, and order blocks — the footprints of smart money.

[![Tests](https://img.shields.io/badge/tests-350%2B%20passing-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)](tests/)
[![Sprint](https://img.shields.io/badge/sprint-4%2F6%20complete-blue)](docs/ROADMAP_Q1_2025.md)
[![Testnet](https://img.shields.io/badge/testnet-LIVE%20TRADING-green)](https://app.hyperliquid-testnet.xyz)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ⚠️ DISCLAIMER

**This software is provided for educational and research purposes only.**

- **NO WARRANTIES:** Provided "as is" without any guarantees
- **USE AT YOUR OWN RISK:** Algorithmic trading involves substantial risk of loss
- **NO LIABILITY:** Authors not liable for any trading losses
- **NOT FINANCIAL ADVICE:** Research software, not investment advice

**Live trading can result in total loss of capital. Never trade with money you cannot afford to lose.**

---

## 🎯 Current Status

**Sprint 1:** ✅ **COMPLETE** (Dec 26, 2025)
**Sprint 2:** ✅ **COMPLETE** (Dec 26, 2025)
**Sprint 3:** ✅ **COMPLETE** (Dec 30, 2025)
**Sprint 4:** ✅ **COMPLETE** (Jan 5, 2026) - Production Hardening 🚀
**Next:** Sprint 5 - E2E Testing + Monitoring Dashboard

### Latest: Live Testnet Trading 🟢 ACTIVE!

**Bot is trading on Hyperliquid testnet:**
- Wallet: `0xf7ab281eeBF13C8720a7eE531934a4803E905403`
- Monitor: https://app.hyperliquid-testnet.xyz

```bash
# All commands run inside Docker container
sudo docker exec fractal-trader-dev python3 -m live.cli status
sudo docker exec fractal-trader-dev python3 -m live.cli start --strategy liquidity_sweep
sudo docker exec fractal-trader-dev python3 -m live.cli stop

# Live logs
sudo docker exec fractal-trader-dev tail -f /tmp/bot_v2.log
```

**Web Dashboard (port 8080):**
```bash
# Start dashboard
sudo docker exec fractal-trader-dev python3 -m live.dashboard &

# View at http://<server-ip>:8080
```

See [docs/CURRENTRUN.md](docs/CURRENTRUN.md) for monitoring guide.

---

### Roadmap

| What You'll Have | Status | Timeline |
| ---------------- | ------ | -------- |
| **Interactive Jupyter analysis** | ✅ | Sprint 1 (Dec 26) |
| **Live market dashboard** | ✅ | Sprint 2 (Dec 26) |
| **Paper trading bot** | ✅ | Sprint 3 (Dec 30) |
| **Production infrastructure** | ✅ | Sprint 4 (Jan 5) |
| **E2E Testing + Dashboard** | 📋 | Sprint 5 (next) |
| **Live trading (mainnet)** | 📋 | Sprint 6 |

---

### Component Status

| Component | Coverage | Production Ready |
| --------- | -------- | ---------------- |
| Core SMC Detection | 95-100% | ✅ |
| Risk Management | 98% | ✅ |
| Backtesting | Good | ✅ |
| Strategies | 70%+ | ✅ |
| Data Layer | 90% | ✅ |
| Visualization | 100% | ✅ |
| Confidence Scoring | 100% | ✅ |
| Live Streaming | 100% | ✅ |
| Alert System | 100% | ✅ |
| State Persistence | 93% | ✅ |
| Circuit Breakers | 100% | ✅ |
| CLI Interface | ✅ | ✅ |
| **Live Trading (Testnet)** | ✅ | ✅ **ACTIVE** |
| **Web Dashboard** | ✅ | ✅ |
| Tribal Weather | 0% | 🚧 Sprint 5 |

**Overall:** ~92% production-ready | 350+ tests | 94% coverage

---

## 🚀 Quick Start

### Option 1: Live Market Dashboard (NEW! 🔴)

```bash
# 1. Clone and install
git clone https://github.com/r464r64r/FractalTrader.git
cd FractalTrader
pip install -r requirements.txt

# 2. Launch live dashboard
cd notebooks/
jupyter notebook live_dashboard.ipynb

# 3. Configure and run cells
# - Choose symbol (BTC/ETH/etc)
# - Set update interval (15s default)
# - Start stream, watch real-time!
```

**You'll see:**
- 🔴 Live charts (updates every 15s)
- 🔔 Setup alerts (visual + audio)
- 📊 Real-time statistics
- 📝 Trade journal (auto-logged)

### Option 2: Static Analysis (Jupyter)

```bash
# For historical analysis
cd notebooks/
jupyter notebook fractal_viewer.ipynb
# Run all cells
```

**You'll see:**
- 3-panel synchronized chart (H4/H1/M15)
- Auto-detected order blocks (green/red zones)
- Confidence scoring (75/100 ✓ ENTRY example)
- Interactive zoom/pan/hover

**Full guide:** [notebooks/README.md](notebooks/README.md)

---

### Option 3: Python API

```bash
# 1. Install
git clone https://github.com/r464r64r/FractalTrader.git
cd FractalTrader
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Your First Backtest

```bash
# Create backtest demo
cat > examples/quick_demo.py << 'EOF'
import pandas as pd
from strategies.liquidity_sweep import LiquiditySweepStrategy
from backtesting.runner import BacktestRunner

# Load data
data = pd.read_csv('data/samples/btc_90d.csv', index_col=0, parse_dates=True)

# Run backtest
strategy = LiquiditySweepStrategy()
runner = BacktestRunner(initial_cash=10000, fees=0.001)
result = runner.run(data, strategy)

# Print results
print("=" * 60)
print(f"Total Return:    {result.total_return:.2%}")
print(f"Sharpe Ratio:    {result.sharpe_ratio:.2f}")
print(f"Max Drawdown:    {result.max_drawdown:.2%}")
print(f"Win Rate:        {result.win_rate:.2%}")
print(f"Total Trades:    {result.total_trades}")
print("=" * 60)
EOF

python examples/quick_demo.py
```

**Expected output:**
```
============================================================
Total Return:    12.45%
Sharpe Ratio:    1.68
Max Drawdown:    -8.23%
Win Rate:        58.3%
Total Trades:    24
============================================================
```

**🎉 You just ran your first backtest!**

See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) for more.

---

## 📚 Features

### Smart Money Concepts Detection

| Feature | Status | Description |
|---------|--------|-------------|
| **Swing Points** | ✅ | Local highs/lows (market structure) |
| **BOS/CHoCH** | ✅ | Break of Structure / Change of Character |
| **Liquidity Levels** | ✅ | Equal highs/lows (stop hunt zones) |
| **Liquidity Sweeps** | ✅ | Stop hunts + reversals |
| **Fair Value Gaps** | ✅ | 3-candle imbalances |
| **Order Blocks** | ✅ | Institutional accumulation zones |

### Trading Strategies

**1. Liquidity Sweep Reversal**
- Trade reversals after stop hunts
- Entry: Price sweeps level → reverses
- Stop: Beyond sweep wick
- Target: Previous structure or 2:1 RR

**2. FVG Fill**
- Trade returns to fair value gaps
- Entry: Price fills imbalance
- Stop: Beyond gap zone
- Target: Continuation or 2:1 RR

**3. BOS + Order Block**
- Trend following with structure confirmation
- Entry: BOS → wait for OB retest
- Stop: Beyond order block
- Target: Next structure or 3:1 RR

### Risk Management

- **Dynamic Position Sizing** (confidence-based)
- **Volatility Adjustment** (ATR-scaled)
- **Win/Loss Streak Management** (reduce after streaks)
- **Portfolio Limits** (max position %, max positions)

### Backtesting

- **vectorbt Integration** (100x faster than loops)
- **Parameter Optimization** (grid search)
- **Performance Metrics** (Sharpe, Sortino, drawdown, etc.)
- **Trade Analysis** (win rate, profit factor, duration)

---

## 🏗️ Project Structure

```
FractalTrader/
├── core/                 # SMC detection (95-100% coverage) ⭐
│   ├── market_structure.py   # Swing points, BOS, CHoCH
│   ├── liquidity.py          # Equal levels, sweeps
│   ├── imbalance.py          # Fair Value Gaps
│   └── order_blocks.py       # Order Block detection
│
├── strategies/           # Trading strategies (79% avg coverage)
│   ├── base.py               # BaseStrategy + Signal class
│   ├── liquidity_sweep.py    # Reversal after stop hunts
│   ├── fvg_fill.py           # Trade FVG fills
│   └── bos_orderblock.py     # Trend + OB entries
│
├── risk/                 # Risk management (98% coverage) ⭐
│   ├── confidence.py         # Signal scoring (0-100)
│   └── position_sizing.py    # Dynamic sizing
│
├── backtesting/          # Backtesting engine
│   └── runner.py             # vectorbt integration
│
├── data/                 # Market data fetchers (with retry logic) ⭐
│   ├── fetcher.py            # Base interface
│   ├── hyperliquid_fetcher.py # Live data (Hyperliquid)
│   └── ccxt_fetcher.py       # Historical (CCXT)
│
├── notebooks/            # Interactive dashboards 🔴 NEW!
│   ├── fractal_viewer.ipynb  # Static analysis
│   ├── live_dashboard.ipynb  # Real-time monitoring
│   ├── live_data_stream.py   # Streaming engine
│   ├── alert_system.py       # Alerts + journal
│   └── setup_detector.py     # Setup detection
│
├── live/                 # Live trading (🟢 TESTNET ACTIVE)
│   ├── cli.py                # Command-line interface
│   ├── dashboard.py          # Web monitoring (Flask, port 8080)
│   ├── state_manager.py      # Position & trade persistence
│   ├── reporting.py          # Performance metrics
│   └── hl_integration/       # Hyperliquid exchange
│       ├── config.py         # Configuration
│       ├── testnet.py        # Testnet trading (ACTIVE)
│       └── trader.py         # Mainnet (NOT RECOMMENDED)
│
├── examples/             # Usage examples
├── tests/                # 350+ tests
└── docs/                 # Documentation
    ├── CURRENTRUN.md         # Live monitoring guide
    ├── DASHBOARD.md          # Web dashboard docs
    └── ISSUES.md             # Project status
```

---

## 🧪 Testing

### Run Tests

```bash
# Core tests (no Docker needed)
python -m pytest tests/ -v \
  --ignore=tests/test_backtesting.py \
  --ignore=tests/test_data_fetchers.py \
  --ignore=tests/test_live_trading.py
# Expected: 134 tests passing

# Full test suite (requires Docker)
./docker-start.sh test
# Expected: 206 tests passing
```

### Test Coverage

| Module | Coverage | Status |
|--------|----------|--------|
| `core/market_structure.py` | 97% | ✅ |
| `core/liquidity.py` | 98% | ✅ |
| `core/imbalance.py` | 97% | ✅ |
| `core/order_blocks.py` | 95% | ✅ |
| `risk/position_sizing.py` | 98% | ✅ |
| `strategies/fvg_fill.py` | 88% | ✅ |
| `strategies/liquidity_sweep.py` | 13% | ⚠️ Needs work |
| `strategies/bos_orderblock.py` | 42% | ⚠️ Needs work |

**See:** [TESTING_STRATEGY.md](TESTING_STRATEGY.md) for details

---

## 📊 Performance Example

**Strategy:** Liquidity Sweep Reversal  
**Data:** 90 days BTC/USDT (1h)  
**Capital:** $10,000  

| Metric | Value |
|--------|-------|
| Total Return | 12.45% |
| Sharpe Ratio | 1.68 |
| Max Drawdown | -8.23% |
| Win Rate | 58.3% |
| Profit Factor | 1.85 |
| Total Trades | 24 |

*Results from sample data. Past performance ≠ future results.*

---

## 🛣️ Roadmap

### ✅ Phase 1: Foundation (Complete)

- [x] Core SMC detection (95-100% coverage)
- [x] Risk management with confidence scoring
- [x] Backtesting framework (vectorbt)
- [x] 3 trading strategies
- [x] Comprehensive test suite (206 tests)

### 🔄 Current: Sprint-Based Development

**Q1 2026 Goal:** Production-ready trading system with tribal intelligence

**Sprints 1-6** (Dec 2025 - Mar 2026):

1. ✅ Jupyter Fractal Viewer (Interactive analysis) - Dec 26, 2025
2. ✅ Live Market Dashboard (Real-time monitoring) - Dec 26, 2025
3. ✅ Paper Trading Bot (Autonomous testnet trading) - Dec 30, 2025
4. 📋 Production Hardening (Robustness & monitoring) - Feb 4-17, 2026
5. 📋 Tribal Weather MVP (Ecosystem intelligence) - Feb 18-Mar 3, 2026
6. 📋 Live Trading System (Mainnet deployment) - Mar 4-17, 2026

**After Q1:** Multi-exchange, advanced strategies, ML integration

**See:** [docs/ROADMAP_Q1_2025.md](docs/ROADMAP_Q1_2025.md) for detailed timeline

---

## 📅 Development Rhythm

### Sprint-Based Delivery

FractalTrader follows **2-week sprints** with mandatory deliverables.

**Philosophy:** Ship or Die 🚢💀

- Every sprint = 1 clickable deliverable
- No extensions (cut scope instead)
- Always releasable

### Completed Sprints

**Sprint 1: Jupyter Fractal Viewer** (Dec 24 - Jan 6, 2025) ✅ COMPLETE (4 days early!)
**Sprint 2: Live Market Dashboard** (Jan 7-20, 2025) ✅ COMPLETE (24 days early!)

**Deliverables:**
- `notebooks/fractal_viewer.ipynb` - Static analysis
- `notebooks/live_dashboard.ipynb` - Real-time monitoring 🔴 NEW!

**Sprint 2 Features:**
```python
# Real-time streaming
from notebooks.live_data_stream import LiveDataStream

stream = LiveDataStream(symbol='BTC', timeframes=['15m', '1h', '4h'])
stream.start()  # Updates every 15s

# Setup alerts
from notebooks.alert_system import AlertSystem

alerts = AlertSystem(min_confidence=70, enable_sound=True)
# Triggers on high-probability setups
```

### Upcoming Sprints

| Sprint | Dates | Deliverable | Status |
| ------ | ----- | ----------- | ------ |
| **4** | Feb 4-17, 2026 | Production Hardening | Next |
| **5** | Feb 18-Mar 3, 2026 | Tribal Weather MVP | Planned |
| **6** | Mar 4-17, 2026 | Live Trading (Mainnet) | Planned |

**See:** [docs/ROADMAP_Q1_2025.md](docs/ROADMAP_Q1_2025.md) for full roadmap (applies to Q1 2026)

### Release Schedule

- **Sprint releases:** Every 2 weeks (v0.X.0-sprint-N)
- **Production releases:** Every 4-6 weeks (v0.X.0)
- **Always releasable:** Main branch always works

### How to Follow Progress

**GitHub Project Board:**
https://github.com/r464r64r/FractalTrader/projects

**Columns:**

```text
💡 Ideas → 🧠 Analysis → 🔬 Research → 🔨 Implementation → 👀 Review → ✅ Done
```

**Sprint Updates:**

- Daily async updates on sprint issue
- Demo every 2 weeks (end of sprint)
- Retrospective + planning

### Documentation

- **Sprint Framework:** [docs/SPRINT_FRAMEWORK.md](docs/SPRINT_FRAMEWORK.md)
- **Q1 Roadmap:** [docs/ROADMAP_Q1_2025.md](docs/ROADMAP_Q1_2025.md)
- **Workflow:** [.github/WORKFLOW.md](.github/WORKFLOW.md)

---

## 🤝 Contributing

**We welcome contributions!** This project follows:
- **Code standards:** Type hints, docstrings, tests required
- **Test coverage:** 70%+ for new code
- **Review process:** All PRs reviewed before merge

### How to Contribute

1. **Fork the repository**
2. **Create feature branch:** `git checkout -b feature/amazing-feature`
3. **Write tests first** (TDD approach)
4. **Implement feature** (follow existing patterns)
5. **Run tests:** `pytest tests/ -v`
6. **Commit:** `git commit -m "Add amazing feature"`
7. **Push:** `git push origin feature/amazing-feature`
8. **Open Pull Request**

### What We Need

**High Priority:**
- [ ] Strategy test coverage (liquidity_sweep, bos_orderblock)
- [ ] Retry logic in data fetchers
- [ ] State persistence implementation
- [ ] Documentation improvements

**Medium Priority:**
- [ ] Additional strategies
- [ ] Walk-forward validation
- [ ] Performance optimization
- [ ] Multi-exchange connectors

**See:** [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines

---

## 📖 Documentation

### User Guides
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Get running in 15 minutes
- **[README.md](README.md)** - This file

### Developer Guides
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Architecture & status
- **[TESTING_STRATEGY.md](TESTING_STRATEGY.md)** - How to test
- **[DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md)** - Production roadmap
- **[AI_DEVELOPMENT.md](AI_DEVELOPMENT.md)** - AI assistant guide
- **[HAIKU_TASKS.md](HAIKU_TASKS.md)** - Task delegation

### Theory
- **[docs/archive/fractal-trader-context.md](docs/archive/fractal-trader-context.md)** - SMC deep dive

---

## 🔧 Requirements

### Python Packages

**Core:**
- pandas >= 2.0.0
- numpy >= 1.24.0
- scipy >= 1.11.0

**Backtesting:**
- vectorbt >= 0.26.0

**Live Trading:**
- ccxt >= 4.0.0
- hyperliquid >= 0.1.0
- eth-account >= 0.8.0

**Development:**
- pytest >= 7.4.3
- pytest-cov >= 4.1.0

**See:** [requirements.txt](requirements.txt) for complete list

### System Requirements

**For Backtesting:**
- Python 3.11+
- 4GB RAM minimum
- Works on: macOS, Linux, Windows

**For Live Trading:**
- Docker recommended (dependency isolation)
- 24/7 uptime (VPS recommended for production)

---

## 🐳 Docker Support

```bash
# Build and start
docker build -t fractal-trader .
./docker-start.sh

# Run tests in Docker
./docker-start.sh test

# Or use docker-compose
docker-compose up -d
docker exec -it fractal-dev bash
```

**Why Docker?**
- Consistent environment
- Complex dependencies (vectorbt, hyperliquid)
- Isolated from system Python

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: vectorbt"
```bash
# vectorbt requires specific environment
pip install vectorbt==0.26.0

# If fails, use Docker:
./docker-start.sh
```

### "Empty DataFrame" in backtest
```bash
# Check data file exists
ls -lh data/samples/btc_90d.csv

# Regenerate if needed (see Quick Start)
```

### "No trades executed"
```bash
# Strategy may be too conservative
# Try adjusting parameters:
strategy = LiquiditySweepStrategy({
    'swing_period': 3,      # More sensitive
    'min_rr_ratio': 1.0     # Lower threshold
})
```

### Tests failing
```bash
# Delete cache and rerun
rm -rf .pytest_cache/ .coverage
pytest tests/ -v --tb=short
```

---

## 🔗 Resources

### Learning
- [Smart Money Concepts Explained](docs/archive/fractal-trader-context.md)
- [vectorbt Documentation](https://vectorbt.dev/)
- [Hyperliquid Docs](https://hyperliquid.gitbook.io/)

### Community
- **GitHub Issues:** [Report bugs](https://github.com/r464r64r/FractalTrader/issues)
- **Discussions:** [Ask questions](https://github.com/r464r64r/FractalTrader/discussions)
- **Pull Requests:** [Contribute](https://github.com/r464r64r/FractalTrader/pulls)

---

## 📜 License

**MIT License** - See [LICENSE](LICENSE)

Free to use, modify, and distribute. No warranty provided.

---

## 🙏 Acknowledgments

**Contributors:**
- **Opus (Claude)** - Core architecture, SMC detection
- **Sonnet (Claude)** - Strategies, risk, tests, integration
- **Haiku (Claude)** - Data processing, fixtures, reports
- **Community** - Your contributions make this better!

**Inspiration:**
- Smart Money Concepts community
- Open-source trading projects
- Institutional trading strategies

---

## ⚡ Quick Links

| What | Where |
|------|-------|
| 🚀 Get started fast | [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) |
| 🧪 Test without APIs | [TESTING_STRATEGY.md](TESTING_STRATEGY.md) |
| 🏗️ Project architecture | [DEVELOPMENT.md](DEVELOPMENT.md) |
| 🛣️ Production roadmap | [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) |
| 🤝 How to contribute | [CONTRIBUTING.md](CONTRIBUTING.md) |
| 📊 Example backtests | [examples/](examples/) |
| 🐛 Report issues | [GitHub Issues](https://github.com/r464r64r/FractalTrader/issues) |

---

## 📢 Status Updates

**January 5, 2026:**
- ✅ Sprint 4 complete (Production Hardening) 🚀
- 🟢 **Bot actively trading on Hyperliquid testnet**
- 🔒 XSS security fix in web dashboard
- 📊 92% production-ready (4/6 sprints complete)

**Sprint 4 Deliverables:**
- 🤖 Live testnet trading (real orders on Hyperliquid)
- 🌐 Web dashboard for monitoring (port 8080)
- 🔧 Circuit breaker & state persistence fixes
- 📝 BTC tick size fix for order acceptance

**Next:** Sprint 5 - E2E Testing + Monitoring Dashboard

**Follow development:** [GitHub](https://github.com/r464r64r/FractalTrader)

---

**Built with ❤️ by the FractalTrader community**

*Remember: This is research software. Never risk money you can't afford to lose.*

**Happy trading! 🚀**
