# Fractal Trader — Claude Code Instructions

## Project Overview

**Fractal Trader** is an algorithmic trading system based on **Smart Money Concepts (SMC)** — detecting institutional order flow patterns for cryptocurrency trading on Hyperliquid DEX.

**Status:** Core implementation complete, test suite complete, awaiting data layer and live trading integration.

---

## Essential Knowledge

### Project Structure

```
fractal-trader/
├── core/                 # SMC detection algorithms (DO NOT MODIFY without tests)
├── strategies/           # Trading strategies
├── risk/                 # Risk management (confidence + position sizing)
├── backtesting/          # vectorbt integration (Docker only)
├── fractal_mcp/          # MCP server for Claude Code
├── tests/                # 134 tests, 76% coverage
├── data/                 # Data fetching (TODO - Hyperliquid SDK + CCXT)
└── live/                 # Hyperliquid live trading (TODO)
    └── hyperliquid/      # Native SDK integration
```

### Key Files

| File | Purpose | Read First |
|------|---------|------------|
| `DEVELOPMENT.md` | Project status, MVP roadmap | Yes |
| `REFACTORING_PLAN.md` | Hyperliquid integration strategy | Yes |
| `strategies/base.py` | Signal dataclass, BaseStrategy ABC | Yes |
| `risk/position_sizing.py` | Position sizing logic | If modifying risk |
| `tests/TODO_TESTS.md` | Test checklist (all complete) | If adding tests |
| `fractal-trader-context.md` | Full SMC specification | For deep context |

### Domain Concepts (SMC)

| Term | Definition |
|------|------------|
| **Swing High/Low** | Local extremes (high/low > N bars on both sides) |
| **BOS** | Break of Structure — trend continuation |
| **CHoCH** | Change of Character — trend reversal |
| **FVG** | Fair Value Gap — 3-candle imbalance |
| **Order Block** | Last opposite candle before impulse |
| **Sweep** | Price breaks level then reverses (stop hunt) |

---

## Development Environment

### Docker (Recommended)

```bash
# Start interactive shell with all dependencies
./docker-start.sh

# Run tests
./docker-start.sh test

# Run backtest example
./docker-start.sh backtest
```

**Why Docker?**
- vectorbt requires numba/LLVM (complex to install)
- Backtesting tests only work in Docker
- Consistent environment

### Without Docker

```bash
# Install (no vectorbt)
pip install pandas numpy scipy pytest

# Run tests (skips backtesting)
python -m pytest tests/ -v --ignore=tests/test_backtesting.py
```

---

## MCP Server

The project includes an MCP server for Claude Code integration.

### Available Tools

| Tool | Description |
|------|-------------|
| `run_tests` | Execute pytest suite |
| `run_backtest` | Run strategy backtest |
| `generate_signals` | Generate trading signals from data |

### Starting the Server

```bash
python -m fractal_mcp.server
```

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fractal-trader": {
      "command": "python",
      "args": ["-m", "fractal_mcp.server"],
      "cwd": "/path/to/FractalTrader"
    }
  }
}
```

---

## Code Conventions

### Type Hints (Required)

```python
def find_swing_points(
    high: pd.Series,
    low: pd.Series,
    n: int = 5
) -> tuple[pd.Series, pd.Series]:
```

### Docstrings (Required)

```python
def detect_liquidity_sweep(...) -> pd.Series:
    """
    Detect liquidity sweeps (stop hunts).

    A sweep occurs when:
    1. Price exceeds liquidity level
    2. Price reverses within reversal_bars
    3. Close returns inside the level

    Args:
        high: High prices
        ...

    Returns:
        Boolean series marking sweep completion bars
    """
```

### Test Requirements

New modules should include TEST REQUIREMENTS section:

```python
# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_function_does_x
# [ ] test_edge_case_y
# =============================================================================
```

---

## Best Practices

### DO

1. **Run tests before commits** — `python -m pytest tests/ -v`
2. **Use type hints everywhere** — No exceptions
3. **Handle edge cases** — Trading code must be robust
4. **Keep functions pure** — Clear inputs/outputs, no hidden state
5. **Document changes** — Update DEVELOPMENT.md for significant work
6. **Use Docker for backtesting** — vectorbt only works there

### DON'T

1. **Modify core/ without tests** — These are foundation modules
2. **Skip input validation** — Trading errors are costly
3. **Use global state** — All state should be explicit
4. **Ignore test failures** — Fix before proceeding
5. **Force push to main** — Use feature branches

---

## Git Workflow

### Branch Strategy

```
main                    # Stable, tested code
├── implement-*         # Feature implementation
├── fix-*               # Bug fixes
└── claude/*            # Claude Code sessions
```

### Commit Messages

```
Add FVG detection tests (17 tests)
Fix position sizing edge case for zero ATR
Update DEVELOPMENT.md with sprint 5 status
```

---

## Current TODO (MVP)

| Priority | Task | Notes |
|----------|------|-------|
| 1 | `data/fetcher.py` | Base interface for data fetching |
| 2 | `data/hyperliquid_fetcher.py` | Native Hyperliquid SDK (live, 5000 candles) |
| 3 | `data/ccxt_fetcher.py` | CCXT/Binance (deep backtesting, unlimited history) |
| 4 | `live/hyperliquid/testnet.py` | Paper trading on testnet |
| 5 | `live/hyperliquid/trader.py` | Live trading implementation |
| 6 | `risk/portfolio.py` | Portfolio-level risk controls |
| 7 | Integration test | End-to-end testnet → mainnet validation |

See `DEVELOPMENT.md` and `REFACTORING_PLAN.md` for full roadmap.

---

## Hyperliquid Integration (NEW)

### Why Hyperliquid?

- 🚀 200,000+ TPS with <0.2s latency
- 🔐 Self-custody DEX security
- 💰 Zero gas fees, ~0.02% trading fees
- 🧪 Full-featured testnet
- 📊 Free real-time and historical data
- ⚡ No KYC required

### Data Architecture

**Dual-fetcher approach:**

```python
# Live trading: Hyperliquid SDK (last 5000 candles)
from data.hyperliquid_fetcher import HyperliquidFetcher
fetcher = HyperliquidFetcher()
data = fetcher.fetch_ohlcv('BTC', '1h', limit=5000)

# Backtesting: CCXT/Binance (unlimited history)
from data.ccxt_fetcher import CCXTFetcher
fetcher = CCXTFetcher('binance')
data = fetcher.fetch_ohlcv('BTC/USDT', '1h', since='2023-01-01')
```

### Testnet vs Mainnet

```python
from hyperliquid.utils import constants
from hyperliquid.exchange import Exchange

# Testnet (paper trading, zero risk)
exchange = Exchange(wallet, constants.TESTNET_API_URL)

# Mainnet (real money)
exchange = Exchange(wallet, constants.MAINNET_API_URL)
```

**Testnet URL:** https://app.hyperliquid-testnet.xyz/trade

---

## Testing

```bash
# Full suite (Docker)
./docker-start.sh test

# Without Docker
python -m pytest tests/ -v --ignore=tests/test_backtesting.py

# Specific file
python -m pytest tests/test_risk.py -v

# With coverage
python -m pytest tests/ --cov=core --cov=risk --cov=strategies
```

**Current status:** 134 tests, 100% passing, 76% coverage

---

## Troubleshooting

### "ModuleNotFoundError: vectorbt"
Use Docker: `./docker-start.sh`

### Tests fail with import errors
Install dependencies: `pip install pandas numpy scipy pytest`

### MCP server won't start
Check Python path and `fractal_mcp/__init__.py` exists

---

## For Haiku Model

**If you're Haiku working on this project:** Start here! 👇

### Quick Start for Haiku

You've been assigned to **complete the MVP** by implementing the final 2 components:

1. **Data Layer** (1-2 days) — Hyperliquid SDK + CCXT fetchers
2. **Live Trading** (2-3 days) — Testnet + Mainnet trader

**Read these documents IN ORDER:**

1. **[HAIKU_HANDOFF.md](HAIKU_HANDOFF.md)** — Overview, safety rules, workflow
2. **[HAIKU_TASK_1_DATA_LAYER.md](HAIKU_TASK_1_DATA_LAYER.md)** — Data layer implementation (step-by-step)
3. **[HAIKU_TASK_2_LIVE_TRADING.md](HAIKU_TASK_2_LIVE_TRADING.md)** — Live trading implementation (step-by-step)
4. **[HAIKU_CODE_EXAMPLES.md](HAIKU_CODE_EXAMPLES.md)** — Copy-paste code patterns

### Critical Rules for Haiku

**RED LINES (DO NOT CROSS):**
- ❌ **NEVER modify** `core/`, `strategies/`, or `risk/` without explicit approval
- ❌ **NEVER commit** without passing tests (`./docker-start.sh test`)
- ❌ **NEVER skip** type hints or docstrings
- ❌ **NEVER test on mainnet** before testnet validation (24+ hours)

**GREEN LIGHTS (YOU MUST DO):**
- ✅ **ALWAYS use Docker** for running tests
- ✅ **ALWAYS write tests** for new code (minimum 80% coverage)
- ✅ **ALWAYS follow** existing code patterns (see HAIKU_CODE_EXAMPLES.md)
- ✅ **ALWAYS commit** small, incremental changes

### Your Starting Checklist

Before writing ANY code:

- [ ] Read [HAIKU_HANDOFF.md](HAIKU_HANDOFF.md) completely
- [ ] Run tests to verify environment: `./docker-start.sh test`
- [ ] Expected: 134 tests passing
- [ ] Verify branch: `git status` (should show `alt` branch)
- [ ] Create `.env` file: `cp .env.example .env`

Once you've verified everything works, proceed to [HAIKU_TASK_1_DATA_LAYER.md](HAIKU_TASK_1_DATA_LAYER.md).

### What You're Inheriting

✅ **COMPLETE (134 tests passing):**
- Core SMC detection (market structure, liquidity, FVG, order blocks)
- 3 trading strategies (liquidity sweep, FVG fill, BOS+OB)
- Risk management (confidence scoring, position sizing)
- Backtesting framework (vectorbt integration)
- Full test suite (76% coverage)

🔧 **YOUR MISSION (30+ new tests):**
- Data fetchers (Hyperliquid + CCXT)
- Live trading (testnet + mainnet)
- Integration tests
- Documentation updates

**Timeline:** 3-5 days to MVP completion

**Risk Level:** LOW (you're adding new code, not modifying tested core)

**Success Criteria:** 164+ tests passing, testnet runs 24h without issues

### Getting Help

**Before asking:**
1. Check [HAIKU_CODE_EXAMPLES.md](HAIKU_CODE_EXAMPLES.md) for code patterns
2. Look at existing tests (`tests/test_risk.py`, etc.) for examples
3. Search codebase with `grep -r "similar_function" .`

**When to ask:**
- Tests fail and you don't understand why
- Need to modify core files (requires approval)
- Hyperliquid SDK documentation unclear
- Integration test fails (might be architecture issue)

**Format for questions:**
```
**Context:** Working on Task 1, Step 3 (Hyperliquid fetcher)
**Issue:** Test failing with "Invalid symbol format"
**What I tried:** [list attempts]
**Error:** [full error message]
**Question:** How should I format Hyperliquid symbols?
```

Good luck! The foundation is solid, you're just adding the final pieces. 🚀

---

## Attribution

| Model | Contributions |
|-------|---------------|
| **Opus** | Architecture, core detection, base strategy |
| **Sonnet** | Risk management, backtesting, strategies, tests, documentation |
| **Haiku** | Data layer, live trading (in progress) |
