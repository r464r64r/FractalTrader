# Fractal Trader — Claude Code Instructions

## Project Overview

**Fractal Trader** is an algorithmic trading system based on **Smart Money Concepts (SMC)** — detecting institutional order flow patterns for cryptocurrency trading.

**Status:** Core implementation complete, test suite complete, awaiting live trading integration.

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
├── live/                 # Freqtrade integration (TODO)
└── data/                 # Data fetching (TODO)
```

### Key Files

| File | Purpose | Read First |
|------|---------|------------|
| `DEVELOPMENT.md` | Project status, MVP roadmap | Yes |
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
| 1 | `data/fetcher.py` | Implement CCXT data fetching |
| 2 | `live/freqtrade_strategy.py` | Complete Freqtrade wrapper |
| 3 | `risk/portfolio.py` | Portfolio-level risk controls |
| 4 | Integration test | End-to-end backtest validation |

See `DEVELOPMENT.md` for full roadmap.

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

## Attribution

| Model | Contributions |
|-------|---------------|
| **Opus** | Architecture, core detection, base strategy |
| **Sonnet** | Risk management, backtesting, strategies, tests |
| **Opus** | Review, documentation, merge coordination |
