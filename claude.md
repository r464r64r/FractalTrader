# Fractal Trader — Claude Code Project Context

## Project Overview

**Fractal Trader** is an algorithmic trading system based on **Smart Money Concepts (SMC)** — detecting institutional order flow patterns for cryptocurrency trading.

**Philosophy:** Trade what institutions trade. Detect liquidity sweeps, fair value gaps, and order blocks — the footprints of smart money.

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Backtesting | vectorbt |
| Live Trading | Freqtrade (planned) |
| Data | CCXT + pandas |
| Testing | pytest |

## Project Structure

```
fractal-trader/
├── core/                 # Core detection algorithms (SMC patterns)
│   ├── market_structure.py   # Swing points, BOS, CHoCH, trend
│   ├── liquidity.py          # Equal levels, liquidity sweeps
│   ├── imbalance.py          # Fair Value Gaps (FVG)
│   └── order_blocks.py       # Order Block detection
│
├── strategies/           # Trading strategies
│   ├── base.py              # BaseStrategy ABC + Signal dataclass
│   ├── liquidity_sweep.py   # Reversal after stop hunts
│   ├── fvg_fill.py          # Trade FVG fills
│   └── bos_orderblock.py    # Trend following with OB entries
│
├── risk/                 # Risk management
│   ├── confidence.py        # Entry scoring (0-100)
│   └── position_sizing.py   # Dynamic position sizing
│
├── backtesting/          # Research & testing
│   └── runner.py            # vectorbt integration
│
├── fractal_mcp/          # MCP Server for Claude Code ✅
│   ├── server.py            # Main server (stdio transport)
│   └── tools/               # run_tests, run_backtest, generate_signals
│
├── tests/                # Test suite
│   ├── test_market_structure.py  # 21 tests ✅
│   ├── test_liquidity.py         # 16 tests ✅
│   └── TODO_TESTS.md             # 116 tests documented
│
└── live/                 # Production (planned)
    └── freqtrade_strategy.py
```

## Code Conventions

### Type Hints Required
```python
def find_swing_points(
    high: pd.Series,
    low: pd.Series,
    n: int = 5
) -> tuple[pd.Series, pd.Series]:
```

### Docstrings Required
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
        low: Low prices
        ...

    Returns:
        Boolean series marking sweep completion bars
    """
```

### Test Requirements Format
Each module ends with:
```python
# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_function_does_x
# [ ] test_edge_case_y
# =============================================================================
```

## Key Domain Concepts (SMC)

| Term | Definition |
|------|------------|
| **Swing High** | Bar where high > N bars on both sides |
| **Swing Low** | Bar where low < N bars on both sides |
| **BOS** | Break of Structure — trend continuation signal |
| **CHoCH** | Change of Character — trend reversal signal |
| **EQH/EQL** | Equal Highs/Lows — liquidity pools |
| **FVG** | Fair Value Gap — 3-candle imbalance pattern |
| **OB** | Order Block — last opposite candle before impulse |
| **Sweep** | Price breaks level then reverses (stop hunt) |

## Current Status

- ✅ Core detection: 4/4 modules complete
- ✅ Strategies: 3/3 strategies complete
- ✅ Risk management: 2/2 modules complete
- ✅ Backtesting: vectorbt integrated
- ✅ MCP Server: Claude Code integration ready
- ✅ Docker: Development environment ready
- ✅ Tests: 37 passing, 116 documented
- 🔧 Live trading: Not started

## MCP Server (Claude Code Integration)

The MCP server allows Claude Code to interact with FractalTrader:

**Tools available:**
- `run_tests` — Execute pytest suite
- `run_backtest` — Run strategy backtests
- `generate_signals` — Generate trading signals

**Start server:** `python -m fractal_mcp.server`

**Configure Claude Code** (`claude_desktop_config.json`):
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

## Running the Project

```bash
# Docker (recommended)
./docker-start.sh          # Interactive shell
./docker-start.sh test     # Run tests
./docker-start.sh backtest # Example backtest

# Or with Python directly
python -m pytest tests/ -v
```

## Key Files to Understand

1. `core/market_structure.py` — Foundation (swing points, trend)
2. `strategies/base.py` — Signal dataclass, BaseStrategy ABC
3. `risk/position_sizing.py` — How position sizes are calculated
4. `backtesting/runner.py` — How backtests work
5. `tests/TODO_TESTS.md` — What tests need implementation

## Development Guidelines

1. **Never skip input validation** — Trading code must handle edge cases
2. **Document changes** — Use `# Modified from DEVELOPMENT.md: [reason]`
3. **Test requirements** — Add TEST REQUIREMENTS section to new modules
4. **Type hints everywhere** — No exceptions
5. **Keep functions pure** — No hidden state, clear inputs/outputs

## Contact / Attribution

- **Opus** (Claude Opus 4): Foundation architecture, core detection, base strategy
- **Sonnet** (Claude Sonnet): Risk management, backtesting, additional strategies
- **Context**: See `fractal-trader-context.md` for full specification
