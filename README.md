# Fractal Trader

An algorithmic trading system based on **Smart Money Concepts (SMC)** — detecting institutional order flow patterns for cryptocurrency trading.

## Core Philosophy

Trade what institutions trade. Detect liquidity sweeps, fair value gaps, and order blocks — the footprints of smart money.

## Features

| Category | Features |
|----------|----------|
| **Detection** | Swing points, BOS/CHoCH, Equal highs/lows, FVG, Order Blocks |
| **Strategies** | Liquidity Sweep Reversal, FVG Fill, BOS + Order Block |
| **Risk** | Confidence scoring (0-100), Dynamic position sizing |
| **Backtesting** | Vectorized backtesting with vectorbt, Parameter optimization |
| **Infrastructure** | Docker environment, MCP server for Claude Code |

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
├── tests/                # Test suite (134 tests)
│   ├── test_market_structure.py
│   ├── test_liquidity.py
│   ├── test_imbalance.py
│   ├── test_order_blocks.py
│   ├── test_risk.py
│   ├── test_strategies.py
│   └── test_backtesting.py   # Requires Docker/vectorbt
│
└── live/                 # Production (planned)
    └── freqtrade_strategy.py
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

**Test status:** 134 tests, 100% passing, 76% coverage

## Dependencies

| Package | Purpose |
|---------|---------|
| pandas, numpy, scipy | Data manipulation |
| vectorbt | Backtesting engine |
| pytest, pytest-cov | Testing |
| freqtrade (planned) | Live trading |

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
