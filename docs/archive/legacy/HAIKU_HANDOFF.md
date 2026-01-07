# FractalTrader — Handoff Document for Haiku

**Date:** December 2024
**From:** Opus + Sonnet (initial development)
**To:** Haiku (MVP completion)
**Branch:** `alt` (safe experimental branch)

---

## Executive Summary

You are taking over a **well-tested, production-ready algorithmic trading system** based on Smart Money Concepts (SMC). The core detection algorithms, strategies, and risk management are **complete and tested** (134 tests passing, 76% coverage).

**Your mission:** Implement the final 2 components to reach MVP:
1. **Data Layer** — Hyperliquid SDK + CCXT fetchers
2. **Live Trading** — Hyperliquid testnet + mainnet integration

**Timeline:** 3-5 days
**Risk:** LOW (you're NOT modifying existing tested code)
**Safety:** Branch `alt` is isolated from `main`

---

## What You're Inheriting

### ✅ COMPLETE (DO NOT MODIFY without tests)

| Component | Status | Files | Tests |
|-----------|--------|-------|-------|
| **Core Detection** | 100% Done | `core/*.py` | 37 tests |
| **Risk Management** | 100% Done | `risk/*.py` | 28 tests |
| **Strategies** | 100% Done | `strategies/*.py` | 31 tests |
| **Backtesting** | 100% Done | `backtesting/runner.py` | 19 tests |
| **MCP Server** | 100% Done | `fractal_mcp/` | Working |
| **Docker** | 100% Done | `Dockerfile`, scripts | Working |

**Coverage:** 76% overall, 95-100% on core modules

### 🔧 YOUR TASKS (NEW CODE)

| Priority | Task | Files to Create | Estimated Time |
|----------|------|----------------|----------------|
| 1 | Data Layer | `data/hyperliquid_fetcher.py`<br>`data/ccxt_fetcher.py`<br>`tests/test_data_fetchers.py` | 1-2 days |
| 2 | Live Trading | `live/hyperliquid/trader.py`<br>`live/hyperliquid/testnet.py`<br>`tests/test_live_trading.py` | 2-3 days |
| 3 | Integration | End-to-end test, docs update | 0.5 day |

---

## Critical Information

### Project Structure (Where Everything Is)

```
FractalTrader/
├── core/                    ✅ COMPLETE - market structure, liquidity, FVG, OB
├── strategies/              ✅ COMPLETE - 3 strategies (sweep, FVG, BOS+OB)
├── risk/                    ✅ COMPLETE - confidence + position sizing
├── backtesting/             ✅ COMPLETE - vectorbt integration
├── data/                    🔧 YOUR TASK 1 - add fetchers
│   ├── __init__.py          ✅ exists
│   ├── fetcher.py           ✅ exists (basic)
│   ├── hyperliquid_fetcher.py  ← YOU CREATE
│   └── ccxt_fetcher.py         ← YOU CREATE
├── live/                    🔧 YOUR TASK 2 - add trading
│   ├── __init__.py          ✅ exists
│   └── hyperliquid/            ← YOU CREATE DIR
│       ├── __init__.py         ← YOU CREATE
│       ├── trader.py           ← YOU CREATE
│       └── testnet.py          ← YOU CREATE
├── tests/                   🔧 ADD YOUR TESTS
│   ├── test_data_fetchers.py   ← YOU CREATE
│   └── test_live_trading.py    ← YOU CREATE
└── docs/
    ├── HAIKU_TASK_1_DATA_LAYER.md       ← YOUR GUIDE
    └── HAIKU_TASK_2_LIVE_TRADING.md     ← YOUR GUIDE
```

### How to Work Safely

**1. ALWAYS use Docker for tests:**
```bash
# Run all tests (includes vectorbt backtesting tests)
./docker-start.sh test

# Interactive shell
./docker-start.sh

# Inside shell
python -m pytest tests/ -v --tb=short
```

**2. NEVER modify these without breaking tests:**
- `core/market_structure.py`
- `core/liquidity.py`
- `core/imbalance.py`
- `core/order_blocks.py`
- `strategies/*.py`
- `risk/*.py`
- `backtesting/runner.py`

**3. ALWAYS write tests for new code:**
- Minimum 80% coverage for new modules
- Follow existing test patterns (see `tests/test_risk.py`)
- Run tests BEFORE committing

**4. Git workflow:**
```bash
# You're on alt branch (safe)
git status
# Should show: On branch alt

# Make small commits
git add <file>
git commit -m "Add Hyperliquid data fetcher with tests"

# Push regularly
git push origin alt
```

---

## Quick Start (First 30 Minutes)

### Step 1: Verify Environment

```bash
# Navigate to project
cd /Users/nvrl/projects/fractaltrader/FractalTrader

# Check branch
git branch
# Should show: * alt

# Verify tests pass
./docker-start.sh test

# Expected output: 134 tests passed
```

### Step 2: Read These Documents IN ORDER

1. **This file** (HAIKU_HANDOFF.md) — Overview
2. [HAIKU_TASK_1_DATA_LAYER.md](HAIKU_TASK_1_DATA_LAYER.md) — First task details
3. [HAIKU_CODE_EXAMPLES.md](HAIKU_CODE_EXAMPLES.md) — Copy-paste patterns
4. [DEVELOPMENT.md](DEVELOPMENT.md) — Current project status
5. [REFACTORING_PLAN.md](REFACTORING_PLAN.md) — Why Hyperliquid

### Step 3: Start Task 1

```bash
# Open your editor
# Create: data/hyperliquid_fetcher.py

# Follow HAIKU_TASK_1_DATA_LAYER.md step-by-step
# Copy patterns from HAIKU_CODE_EXAMPLES.md
# Write tests as you go
```

---

## Understanding the Codebase

### How to Read Existing Code

**Example: How strategies use core detection**

```python
# File: strategies/liquidity_sweep.py (COMPLETE - for reference)

from core.market_structure import find_swing_points
from core.liquidity import detect_liquidity_sweep

def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
    # 1. Find swing points (core function)
    swing_highs, swing_lows = find_swing_points(
        data['high'], data['low'], n=5
    )

    # 2. Detect sweeps (core function)
    bullish_sweeps = detect_liquidity_sweep(
        data['high'], data['low'], data['close'],
        liquidity_levels=swing_lows,
        reversal_bars=3
    )

    # 3. Generate signals from sweeps
    signals = []
    for idx in data.index[bullish_sweeps]:
        signal = Signal(
            timestamp=idx,
            direction=1,  # long
            entry_price=data.loc[idx, 'close'],
            stop_loss=data.loc[idx, 'low'] * 0.999,
            confidence=self.calculate_confidence(data, idx),
            # ...
        )
        signals.append(signal)

    return signals
```

**Key patterns you'll use:**

1. **Input format:** All functions expect `pd.DataFrame` with `['open', 'high', 'low', 'close', 'volume']`
2. **Output format:** Core functions return `pd.Series` or `pd.DataFrame`
3. **Type hints:** ALWAYS used (see existing code)
4. **Docstrings:** Google style (see existing code)

### How to Use Existing Components in Your Code

```python
# In your data/hyperliquid_fetcher.py

import pandas as pd
from typing import Optional

def fetch_ohlcv(symbol: str, timeframe: str = '1h') -> pd.DataFrame:
    """
    Fetch OHLCV data from Hyperliquid.

    Returns:
        DataFrame with columns [open, high, low, close, volume]
        and DatetimeIndex (THIS FORMAT IS REQUIRED)
    """
    # Your implementation...

    df = pd.DataFrame({
        'open': ...,
        'high': ...,
        'low': ...,
        'close': ...,
        'volume': ...
    })
    df.index = pd.DatetimeIndex(timestamps)

    return df
```

**This format is critical** because strategies expect it:
```python
# Strategies will call your fetcher like this:
from data.hyperliquid_fetcher import HyperliquidFetcher

fetcher = HyperliquidFetcher()
data = fetcher.fetch_ohlcv('BTC', '1h')  # Must return standard format

strategy = LiquiditySweepStrategy()
signals = strategy.generate_signals(data)  # ← expects standard format
```

---

## Testing Requirements

### What Tests Must Do

**Every new function needs:**

1. **Happy path test** — Normal usage works
2. **Edge case test** — Empty data, invalid inputs, etc.
3. **Integration test** — Works with existing components

**Example from existing tests:**

```python
# File: tests/test_risk.py (COMPLETE - for reference)

def test_position_size_respects_max(sample_portfolio):
    """Test that position size never exceeds max_position_percent."""

    params = RiskParameters(max_position_percent=0.05)

    size = calculate_position_size(
        portfolio_value=10000,
        entry_price=100,
        stop_loss_price=95,
        confidence_score=100,
        current_atr=5,
        baseline_atr=5,
        consecutive_wins=0,
        consecutive_losses=0,
        params=params
    )

    position_value = size * 100
    assert position_value <= 10000 * 0.05  # ← Clear assertion
```

### Your Test Coverage Goals

| Module | Minimum Tests | Target Coverage |
|--------|---------------|-----------------|
| `data/hyperliquid_fetcher.py` | 8 tests | 85% |
| `data/ccxt_fetcher.py` | 7 tests | 85% |
| `live/hyperliquid/trader.py` | 10 tests | 70% |
| `live/hyperliquid/testnet.py` | 5 tests | 70% |

**Total new tests:** ~30 tests

**How to run:**
```bash
# All tests
python -m pytest tests/ -v

# Your tests only
python -m pytest tests/test_data_fetchers.py -v
python -m pytest tests/test_live_trading.py -v

# With coverage
python -m pytest tests/test_data_fetchers.py --cov=data --cov-report=term-missing
```

---

## Development Workflow

### Daily Routine

**Morning (Planning):**
1. Read task document (HAIKU_TASK_1 or HAIKU_TASK_2)
2. Check which step you're on
3. Review code examples for that step

**During Work:**
1. Write function
2. Write test immediately
3. Run test: `python -m pytest tests/test_<module>.py -v`
4. Iterate until passing
5. Commit: `git commit -m "Add <feature> with tests"`

**End of Day (Review):**
1. Run full test suite: `./docker-start.sh test`
2. Check coverage: `pytest --cov=data --cov=live`
3. Push code: `git push origin alt`
4. Update progress (comment or message)

### Code Quality Checklist

Before committing ANY code, verify:

- [ ] **Type hints** on all function parameters and returns
- [ ] **Docstring** with Args, Returns, and brief description
- [ ] **Tests** written and passing
- [ ] **Edge cases** handled (None, empty, invalid inputs)
- [ ] **Error messages** are clear
- [ ] **No print statements** (use logging if needed)
- [ ] **Follows existing patterns** (check similar files)

### Example Commit Flow

```bash
# 1. Create new file
touch data/hyperliquid_fetcher.py

# 2. Implement basic version
# ... edit file ...

# 3. Create test file
touch tests/test_data_fetchers.py

# 4. Write first test
# ... edit test file ...

# 5. Run test
python -m pytest tests/test_data_fetchers.py::test_fetch_ohlcv_basic -v

# 6. Fix until passing
# ... iterate ...

# 7. Commit when test passes
git add data/hyperliquid_fetcher.py tests/test_data_fetchers.py
git commit -m "Add Hyperliquid fetcher with basic OHLCV test"

# 8. Continue with next test
# Repeat steps 4-7 for each function/test
```

---

## Communication & Help

### When to Ask for Help

**ASK if:**
- Tests fail and you don't understand why
- Hyperliquid SDK documentation is unclear
- You need to modify core files (rare, needs approval)
- Integration test fails (might be architecture issue)

**DON'T ASK if:**
- You can find answer in existing code (grep for similar patterns)
- Documentation explains it (HAIKU_TASK_*.md)
- Error message is clear (fix the bug)
- Test just needs more work (iterate)

### How to Report Progress

**Daily update format:**

```
Progress Update - Day N

COMPLETED:
- ✅ hyperliquid_fetcher.py basic implementation
- ✅ 5/8 tests passing for Hyperliquid fetcher
- ✅ CCXT fetcher started

IN PROGRESS:
- 🔧 Debugging WebSocket reconnection test
- 🔧 Writing integration test for both fetchers

BLOCKED:
- None

NEXT:
- Finish remaining Hyperliquid tests
- Complete CCXT fetcher tests
- Move to Task 2 (live trading)

TESTS: 139/142 passing (3 new tests in progress)
```

### Where to Find Answers

**Question:** How to structure a DataFrame?
**Answer:** Look at `tests/fixtures/sample_data.py` or existing `data/fetcher.py`

**Question:** How to write a test?
**Answer:** Copy pattern from `tests/test_risk.py` or `tests/test_imbalance.py`

**Question:** How does Hyperliquid SDK work?
**Answer:** See HAIKU_TASK_1_DATA_LAYER.md section "Hyperliquid SDK Reference"

**Question:** What's the error handling pattern?
**Answer:** See HAIKU_CODE_EXAMPLES.md section "Error Handling"

**Question:** How to calculate ATR/indicators?
**Answer:** We DON'T use ta-lib. See existing code in `strategies/base.py::_calculate_atr()`

---

## Success Criteria (Definition of Done)

### Task 1: Data Layer

**DONE when:**
- [ ] `data/hyperliquid_fetcher.py` created with:
  - `fetch_ohlcv()` — returns DataFrame (last 5000 candles)
  - `fetch_live()` — WebSocket for real-time data
  - Error handling for network issues
- [ ] `data/ccxt_fetcher.py` created with:
  - `fetch_ohlcv()` — returns DataFrame (historical data)
  - Pagination for large date ranges
  - Binance integration working
- [ ] `tests/test_data_fetchers.py` has 15+ tests, all passing
- [ ] Both fetchers return **identical DataFrame format**
- [ ] Documentation updated in DEVELOPMENT.md

### Task 2: Live Trading

**DONE when:**
- [ ] `live/hyperliquid/trader.py` created with:
  - Order placement (market + limit)
  - Position monitoring
  - Risk checks integration (uses `risk/position_sizing.py`)
- [ ] `live/hyperliquid/testnet.py` created with:
  - Paper trading mode
  - Testnet configuration
  - Basic performance tracking
- [ ] `tests/test_live_trading.py` has 15+ tests, all passing
- [ ] Successfully places order on testnet
- [ ] 24-hour testnet run without crashes

### Final Integration

**DONE when:**
- [ ] All 164+ tests passing (134 existing + 30 new)
- [ ] Coverage remains >75%
- [ ] End-to-end test: fetch data → generate signals → place order (testnet)
- [ ] DEVELOPMENT.md updated with new components
- [ ] README.md updated with usage examples
- [ ] Branch `alt` ready for merge review

---

## Common Pitfalls (Learn from Others' Mistakes)

### ❌ Mistake 1: Modifying Core Without Tests

**DON'T:**
```python
# Editing core/market_structure.py
def find_swing_points(...):
    # "I'll just add this one line..."
    pass
```

**WHY:** You'll break 37 existing tests. Core is tested and working.

**DO:** Use core functions as-is. If you think they're wrong, ask first.

### ❌ Mistake 2: Skipping Type Hints

**DON'T:**
```python
def fetch_data(symbol, timeframe):  # ← No types
    return data  # ← What type?
```

**DO:**
```python
def fetch_data(symbol: str, timeframe: str) -> pd.DataFrame:
    return data
```

**WHY:** Type hints prevent bugs and match existing codebase standards.

### ❌ Mistake 3: Testing in Production

**DON'T:**
```python
# live/hyperliquid/trader.py
exchange = Exchange(wallet, constants.MAINNET_API_URL)  # ← Real money!
```

**DO:**
```python
# live/hyperliquid/testnet.py
exchange = Exchange(wallet, constants.TESTNET_API_URL)  # ← Fake money
```

**WHY:** Always test on testnet first. Mainnet = real money.

### ❌ Mistake 4: Not Handling Edge Cases

**DON'T:**
```python
def fetch_ohlcv(symbol: str) -> pd.DataFrame:
    data = api.fetch(symbol)
    return pd.DataFrame(data)  # ← What if API fails?
```

**DO:**
```python
def fetch_ohlcv(symbol: str) -> pd.DataFrame:
    try:
        data = api.fetch(symbol)
        if not data:
            raise ValueError(f"No data for {symbol}")
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        raise
```

**WHY:** Trading code must be robust. Network issues happen.

### ❌ Mistake 5: Inconsistent DataFrame Format

**DON'T:**
```python
# Returns different columns
df1 = pd.DataFrame({'Open': ..., 'High': ...})  # ← Capital O
df2 = pd.DataFrame({'open': ..., 'high': ...})  # ← lowercase
```

**DO:**
```python
# ALWAYS use this exact format
df = pd.DataFrame({
    'open': open_prices,
    'high': high_prices,
    'low': low_prices,
    'close': close_prices,
    'volume': volumes
})
df.index = pd.DatetimeIndex(timestamps)
```

**WHY:** Strategies expect lowercase columns. Breaking this breaks everything.

---

## FAQs

### Q: Can I refactor existing code?
**A:** No. Core is tested and working. If you find a bug, report it. Don't "improve" working code.

### Q: What if tests fail after my changes?
**A:** If you only added new files, old tests shouldn't fail. If they do:
1. Run `git status` — did you accidentally edit core files?
2. Run `git diff` — what changed?
3. Revert: `git checkout <file>`
4. Ask for help if still stuck

### Q: Can I use different libraries?
**A:** Stick to existing dependencies (pandas, numpy, scipy, ccxt, hyperliquid-python-sdk). Don't add new ones without asking.

### Q: What if Hyperliquid API changes?
**A:** Pin the SDK version in `requirements.txt`. Don't upgrade mid-development.

### Q: How do I test WebSocket connections?
**A:** See HAIKU_TASK_1_DATA_LAYER.md section on WebSocket testing. Use mocks for unit tests, real connection for integration test.

### Q: What's the difference between testnet and mainnet?
**A:**
- Testnet: Fake money, safe to experiment, URL: `app.hyperliquid-testnet.xyz`
- Mainnet: Real money, only after testnet validation, URL: `app.hyperliquid.xyz`

### Q: How long should tests take to run?
**A:**
- Unit tests (yours): <5 seconds
- Full test suite: <30 seconds
- Backtesting tests (Docker): ~60 seconds

### Q: What if I'm stuck?
**A:**
1. Read the task document again (HAIKU_TASK_*.md)
2. Look at code examples (HAIKU_CODE_EXAMPLES.md)
3. Search existing tests for similar patterns
4. Check existing code (grep for similar functions)
5. Ask for help with specific error message

---

## Next Steps

**RIGHT NOW:**

1. ✅ Read this document (you just did!)
2. ⏭️ Open [HAIKU_TASK_1_DATA_LAYER.md](HAIKU_TASK_1_DATA_LAYER.md)
3. ⏭️ Verify tests pass: `./docker-start.sh test`
4. ⏭️ Create your first file: `data/hyperliquid_fetcher.py`
5. ⏭️ Follow Task 1 step-by-step

**TOMORROW:**

- Complete Task 1 (data layer)
- All tests passing
- Commit and push progress

**THIS WEEK:**

- Complete Task 2 (live trading)
- End-to-end integration test
- Documentation update
- MVP ready for review

---

## You've Got This! 🚀

**Remember:**
- Core is solid (134 tests passing)
- You're building on a strong foundation
- Tasks are well-defined
- Tests guide your implementation
- Ask when stuck

**Your goal:** Add 2 components (data + live trading) to complete MVP.

**Timeline:** 3-5 days

**Risk:** LOW (isolated branch, no core modifications)

**Support:** Full documentation + code examples + existing test patterns

---

**Start here:** [HAIKU_TASK_1_DATA_LAYER.md](HAIKU_TASK_1_DATA_LAYER.md)

**Good luck! Powodzenia! 🇵🇱**
