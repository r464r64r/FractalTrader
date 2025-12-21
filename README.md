# Fractal Trader

An algorithmic trading system based on **Smart Money Concepts (SMC)** — detecting institutional order flow patterns for cryptocurrency trading.

## ⚠️ DISCLAIMER

**This software is provided for educational and research purposes only.**

- **NO WARRANTIES:** This software is provided "as is" without any guarantees
- **USE AT YOUR OWN RISK:** Algorithmic trading involves substantial risk of loss
- **NO LIABILITY:** Authors and contributors are not liable for any trading losses
- **TESTNET FIRST:** Always validate on testnet for 24+ hours before considering mainnet
- **NOT FINANCIAL ADVICE:** This is research software, not investment advice

**Live trading can result in total loss of capital. Never trade with money you cannot afford to lose.**

---

## Core Philosophy

Trade what institutions trade. Detect liquidity sweeps, fair value gaps, and order blocks — the footprints of smart money.

## Features

| Category | Features |
|----------|----------|
| **Detection** | Swing points, BOS/CHoCH, Equal highs/lows, FVG, Order Blocks |
| **Strategies** | Liquidity Sweep Reversal, FVG Fill, BOS + Order Block |
| **Risk** | Confidence scoring (0-100), Dynamic position sizing |
| **Backtesting** | Vectorized backtesting with vectorbt, Parameter optimization |
| **Data Sources** | Hyperliquid (live), CCXT (backtesting) |
| **Live Trading** | Hyperliquid testnet/mainnet integration |
| **Infrastructure** | Docker environment, MCP server for Claude Code |

## 🚧 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| **Core SMC Logic** | ✅ **Production-ready** | 134 tests, 95-100% coverage |
| **Backtesting** | ✅ **Production-ready** | vectorbt integration, Docker-based |
| **Data Layer** | ⚠️ **Beta** | Works in Docker, needs local testing |
| **Testnet Trading** | 🔴 **Alpha** | Requires 24h+ validation |
| **Mainnet Trading** | 🔴 **Not Recommended** | High risk, incomplete validation |

### Known Limitations

1. **Testing Environment:**
   - 72 tests require Docker (missing `hyperliquid`/`eth-account` dependencies locally)
   - Full test suite: 206 tests (134 run without Docker)

2. **Strategy Coverage:**
   - Strategy modules: 13-42% test coverage (private methods not tested)
   - Core detection: 95-100% coverage ✅

3. **Production Gaps:**
   - ⚠️ No retry logic in data fetchers (network failures will crash bot)
   - ⚠️ No portfolio-level risk controls (only per-trade limits)
   - ⚠️ No state persistence (restart loses position tracking)
   - ⚠️ No end-to-end integration tests

4. **Recommended Path:**
   - ✅ Use for backtesting and research
   - ⚠️ Testnet only with close monitoring
   - 🔴 Mainnet not advised until post-v1.0 validation

See [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) for production readiness roadmap.

## Quick Start

### Using Docker (Recommended)

```bash
# Start interactive development shell
./docker-start.sh

# Run tests
./docker-start.sh test

# Run example backtest
./docker-start.sh backtest
```

### Using Python directly

```bash
# Install dependencies
pip install -e .

# Run tests (backtesting tests require Docker)
python -m pytest tests/ -v --ignore=tests/test_backtesting.py
```

### Basic Usage

```python
from core.market_structure import find_swing_points, determine_trend
from strategies.liquidity_sweep import LiquiditySweepStrategy
from backtesting.runner import BacktestRunner

# Load OHLCV data (pandas DataFrame with open, high, low, close, volume)
data = load_your_data()

# Analyze market structure
swing_highs, swing_lows = find_swing_points(data['high'], data['low'], n=5)
trend = determine_trend(swing_highs, swing_lows)

# Run backtest
runner = BacktestRunner(initial_cash=10000)
strategy = LiquiditySweepStrategy()
result = runner.run(data, strategy)

print(f"Return: {result.total_return:.1%}")
print(f"Sharpe: {result.sharpe_ratio:.2f}")
print(f"Win Rate: {result.win_rate:.1%}")
```

## Project Structure

```
fractal-trader/
├── core/                 # Core detection algorithms
│   ├── market_structure.py   # Swing points, BOS, CHoCH, trend
│   ├── liquidity.py          # Equal levels, liquidity sweeps
│   ├── imbalance.py          # Fair Value Gaps (FVG)
│   └── order_blocks.py       # Order Block detection
│
├── strategies/           # Trading strategies
│   ├── base.py               # BaseStrategy ABC + Signal dataclass
│   ├── liquidity_sweep.py    # Reversal after stop hunts
│   ├── fvg_fill.py           # Trade FVG fills
│   └── bos_orderblock.py     # Trend following with OB entries
│
├── risk/                 # Risk management
│   ├── confidence.py         # Entry scoring (0-100)
│   └── position_sizing.py    # Dynamic position sizing
│
├── backtesting/          # Research & testing
│   └── runner.py             # vectorbt integration
│
├── fractal_mcp/          # MCP Server for Claude Code
│   └── server.py             # Tools: run_tests, run_backtest
│
├── data/                 # Data fetching
│   ├── fetcher.py            # Base interface
│   ├── hyperliquid_fetcher.py # Live data (5000 candles)
│   └── ccxt_fetcher.py       # Historical data (unlimited)
│
├── live/                 # Live trading
│   └── hyperliquid/
│       ├── config.py         # Trading configuration
│       ├── testnet.py        # Testnet paper trading
│       └── trader.py         # Mainnet trader
│
└── tests/                # Test suite (206 total)
    ├── test_market_structure.py (21 tests)
    ├── test_liquidity.py (16 tests)
    ├── test_imbalance.py (17 tests)
    ├── test_order_blocks.py (21 tests)
    ├── test_risk.py (28 tests)
    ├── test_strategies.py (31 tests)
    ├── test_backtesting.py (19 tests - Docker only)
    ├── test_data_fetchers.py (32 tests - Docker only)
    └── test_live_trading.py (22 tests - Docker only)
```

## Strategies

### 1. Liquidity Sweep Reversal
Trade reversals after institutional stop hunts. Entry on sweep completion, stop below sweep wick.

### 2. FVG Fill
Trade returns to Fair Value Gaps (3-candle imbalances). Entry when price fills the gap, stop beyond gap zone.

### 3. BOS + Order Block
Trend following with structure confirmation. Wait for BOS, then enter on Order Block retest.

## Smart Money Concepts (SMC)

| Term | Definition |
|------|------------|
| **Swing High/Low** | Local price extremes (higher than N bars on both sides) |
| **BOS** | Break of Structure — trend continuation signal |
| **CHoCH** | Change of Character — trend reversal signal |
| **FVG** | Fair Value Gap — 3-candle imbalance pattern |
| **Order Block** | Last opposite candle before impulse move |
| **Sweep** | Price breaks level then reverses (stop hunt) |

## Docker Environment

The project includes a Docker environment with all dependencies pre-installed:

```bash
# Build and start
docker build -t fractal-trader .
./docker-start.sh

# Or use docker-compose
docker-compose up -d
docker exec -it fractal-dev bash
```

**Why Docker?**
- vectorbt has complex dependencies (numba, etc.)
- Consistent environment across machines
- Isolated from system Python

## MCP Server (Claude Code Integration)

The MCP server allows Claude Code to interact with FractalTrader:

```bash
# Start server
python -m fractal_mcp.server
```

**Available tools:**
- `run_tests` — Execute pytest suite
- `run_backtest` — Run strategy backtests
- `generate_signals` — Generate trading signals

**Configure Claude Code** (see `fractal_mcp/README.md`).

## Testing

```bash
# All tests (Docker)
./docker-start.sh test

# Without Docker
python -m pytest tests/ -v --ignore=tests/test_backtesting.py

# With coverage
python -m pytest tests/ --cov=core --cov=risk --cov=strategies
```

**Test status:**
- **Core tests:** 134 passing (run without Docker)
- **Full suite:** 206 tests (requires Docker for data/live trading tests)
- **Coverage:** 76% average, core modules 95-100%

## Dependencies

| Package | Purpose | Docker Only? |
|---------|---------|--------------|
| pandas, numpy, scipy | Data manipulation | No |
| vectorbt | Backtesting engine | Yes |
| pytest, pytest-cov | Testing | No |
| ccxt | Multi-exchange data | No |
| hyperliquid | Hyperliquid DEX SDK | Yes* |
| eth-account | Wallet management | Yes* |

\* Available in Docker, may have issues locally (see [requirements.txt](requirements.txt))

See `requirements.txt` for full list.

## Development

See `DEVELOPMENT.md` for:
- Current project status
- MVP roadmap
- Architecture overview
- Development guidelines

See `claude.md` for Claude Code specific instructions.

## License

MIT License
