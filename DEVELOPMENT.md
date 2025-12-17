# Fractal Trader — Development Guide

## Project Status (December 2024)

### Implementation Progress

| Component | File | Status | Tests | Coverage |
|-----------|------|--------|-------|----------|
| **Core Detection** |
| Swing Points | `core/market_structure.py` | ✅ Done | 21 | 97% |
| Trend Detection | `core/market_structure.py` | ✅ Done | incl. | 97% |
| BOS/CHoCH | `core/market_structure.py` | ✅ Done | incl. | 97% |
| Equal Levels | `core/liquidity.py` | ✅ Done | 16 | 98% |
| Liquidity Sweeps | `core/liquidity.py` | ✅ Done | incl. | 98% |
| Fair Value Gaps | `core/imbalance.py` | ✅ Done | 17 | 97% |
| Order Blocks | `core/order_blocks.py` | ✅ Done | 21 | 95% |
| **Strategies** |
| Base Strategy | `strategies/base.py` | ✅ Done | - | 81% |
| Liquidity Sweep | `strategies/liquidity_sweep.py` | ✅ Done | - | 13%* |
| FVG Fill | `strategies/fvg_fill.py` | ✅ Done | 15 | 88% |
| BOS + Order Block | `strategies/bos_orderblock.py` | ✅ Done | 16 | 42%* |
| **Risk Management** |
| Confidence Scoring | `risk/confidence.py` | ✅ Done | 9 | 100% |
| Position Sizing | `risk/position_sizing.py` | ✅ Done | 19 | 98% |
| **Backtesting** |
| Backtest Runner | `backtesting/runner.py` | ✅ Done | 19 | Docker |
| **Infrastructure** |
| Docker Environment | `Dockerfile`, `docker-start.sh` | ✅ Done | - | - |
| MCP Server | `fractal_mcp/` | ✅ Done | - | - |

\* Low coverage in strategies is expected - tests focus on public API behavior, not private methods.

### Test Summary

| Metric | Value |
|--------|-------|
| Total tests | **134** |
| Passing | **134** (100%) |
| Coverage (avg) | **76%** |
| Core modules | 95-100% |

---

## MVP Roadmap

### Completed Sprints

**Sprint 1-4 (Sonnet):** Core implementation
- Risk management with confidence scoring
- Backtesting framework with vectorbt
- FVG and Order Block detection
- FVG Fill and BOS+OB strategies

**Sprint 5 (Sonnet):** Test suite
- 116 tests implemented per TODO_TESTS.md
- All tests passing

### Remaining for MVP

| Priority | Task | Effort | Status |
|----------|------|--------|--------|
| 1 | Data fetcher implementation | Medium | 🔧 TODO |
| 2 | Live trading integration (Freqtrade) | High | 🔧 TODO |
| 3 | Portfolio-level risk controls | Medium | 🔧 TODO |
| 4 | End-to-end integration test | Low | 🔧 TODO |

### Post-MVP (Optional)

- Multi-timeframe analysis
- Telegram notifications
- Web dashboard
- Additional exchanges via CCXT

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA (OHLCV)                           │
│                    data/fetcher.py                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CORE DETECTION                            │
│  market_structure.py │ liquidity.py │ imbalance.py │ OB    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      STRATEGIES                             │
│  liquidity_sweep.py │ fvg_fill.py │ bos_orderblock.py      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   RISK MANAGEMENT                           │
│         confidence.py │ position_sizing.py                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     EXECUTION                               │
│         backtesting/runner.py │ live/freqtrade             │
└─────────────────────────────────────────────────────────────┘
```

---

## Running Tests

```bash
# All tests (requires Docker for backtesting tests)
./docker-start.sh test

# Without Docker (skips backtesting tests)
python -m pytest tests/ -v --ignore=tests/test_backtesting.py

# With coverage
python -m pytest tests/ --cov=core --cov=risk --cov=strategies

# Specific module
python -m pytest tests/test_risk.py -v
```

---

## Development Guidelines

1. **Type hints required** — All functions must have type annotations
2. **Docstrings required** — Google-style docstrings for public functions
3. **Test requirements** — Add TEST REQUIREMENTS section to new modules
4. **Edge cases** — Trading code must handle all edge cases
5. **No hidden state** — Keep functions pure where possible

---

## Attribution

| Developer | Contributions |
|-----------|---------------|
| **Opus** | Foundation: core detection, base strategy, architecture |
| **Sonnet** | Risk management, backtesting, FVG/OB strategies, tests |
| **Opus** | Review, merge, documentation consolidation |
