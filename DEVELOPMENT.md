# Fractal Trader — Development Guide

**Last Updated:** 2026-01-02
**Status:** Sprints 1-3 Complete (Dec 24, 2025 - Dec 30, 2025) ✅
**Overall Production Readiness:** 85% → Next: Sprint 4 (Feb 4-17, 2026)

---

## 📊 Honest Project Status

### Component Breakdown

| Component | Status | Tests | Coverage | Production Ready? |
|-----------|--------|-------|----------|-------------------|
| **Core Detection** | ✅ Complete | 75 | 95-100% | **YES** ✅ |
| Market Structure | ✅ Done | 21 | 97% | ✅ |
| Liquidity | ✅ Done | 16 | 98% | ✅ |
| Imbalance (FVG) | ✅ Done | 17 | 97% | ✅ |
| Order Blocks | ✅ Done | 21 | 95% | ✅ |
| **Risk Management** | ✅ Complete | 28 | 98% | **YES** ✅ |
| Position Sizing | ✅ Done | 19 | 98% | ✅ |
| Confidence Scoring | ✅ Done | 9 | 100% | ✅ |
| **Strategies** | ⚠️ Partial | 31 | 13-88% | **NO** ⚠️ |
| Liquidity Sweep | ⚠️ Logic OK | - | 13% | ❌ Tests needed |
| FVG Fill | ✅ Done | 15 | 88% | ✅ |
| BOS + Order Block | ⚠️ Logic OK | 16 | 42% | ❌ Tests needed |
| **Backtesting** | ✅ Complete | 19 | Docker | **YES** ✅ |
| VectorBT Runner | ✅ Done | 19 | N/A | ✅ |
| **Data Layer** | ⚠️ Beta | 32 | 85-90% | **NO** 🚨 |
| Hyperliquid | ⚠️ Works | 15 | 90% | ❌ No retry logic |
| CCXT | ⚠️ Works | 11 | 85% | ❌ No retry logic |
| **Live Trading** | 🚨 Alpha | 22 | 80% | **NO** 🚨 |
| Testnet | 🚨 Skeleton | 7 | 80% | ❌ Missing safeguards |
| Mainnet | 🚨 Skeleton | 4 | 85% | ❌ Not validated |

### Overall Readiness Assessment

| Phase | Readiness | Notes |
|-------|-----------|-------|
| **Research & Backtesting** | 85% | ✅ Ready for use |
| **Paper Trading (Testnet)** | 40% | ⚠️ Needs 2-3 weeks work |
| **Live Trading (Mainnet)** | 20% | 🚨 Needs 6-8 weeks work |

**Previous estimate (85% ready) was based on core completion only.**
**Revised estimate (65% ready) accounts for integration gaps and production requirements.**

---

## 🚨 Critical Gaps (Blocking Production)

### Priority 1: MUST FIX (Before ANY Live Trading)

| # | Issue | Impact | Effort | Status |
|---|-------|--------|--------|--------|
| 1 | **No Retry Logic in Data Fetchers** | Network timeout = crash | 2-4h | ✅ **DONE** (Sprint 3) |
| 2 | **No State Persistence** | Restart = lost positions | 4-6h | ✅ **DONE** (Sprint 3) |
| 3 | **Strategy Test Coverage 13-42%** | Untested edge cases | 8-12h | ⚠️ IN PROGRESS |
| 4 | **Circuit Breaker Only in Mainnet** | Can't test fail-safes | 2h | ✅ **DONE** (Sprint 3) |

### Priority 2: HIGH (Before Mainnet)

| # | Issue | Impact | Effort | Status |
|---|-------|--------|--------|--------|
| 5 | **No Portfolio-Level Risk** | Over-exposure risk | 6-8h | ❌ TODO |
| 6 | **No End-to-End Integration Test** | Unknown system behavior | 4-6h | ❌ TODO |
| 7 | **No Walk-Forward Validation** | Overfitting risk | 6-8h | ❌ TODO |

### Priority 3: MEDIUM (Nice to Have)

| # | Issue | Impact | Effort | Status |
|---|-------|--------|--------|--------|
| 8 | **Unused ConfidenceFactors Class** | Code inconsistency | 4-6h | ❌ TODO |
| 9 | **No Monte Carlo Simulation** | Can't assess luck vs skill | 4-6h | ❌ TODO |
| 10 | **No Architecture Decision Records** | Lost context | 2-4h | ❌ TODO |

---

## 🎯 Realistic Timeline

### Current Position
- ✅ **Core Detection:** Production-ready
- ✅ **Risk Management:** Production-ready
- ✅ **Backtesting:** Works well
- ⚠️ **Strategies:** Logic OK, tests insufficient
- 🚨 **Live Trading:** Critical gaps

### Path to Production

**Sprint 3 Completed (Dec 30, 2025)** ✅
```
✅ Retry logic in data fetchers (with exponential backoff)
✅ State persistence (432 lines, 93% coverage)
✅ Circuit breakers in testnet (20% drawdown, 50 trade limit)
✅ CLI interface (start/stop/status/report)
✅ Performance reporting system

Deliverable: ✅ Paper Trading Bot Ready!
```

**Week 3-4: Production Hardening (Sprint 4)**
```
Strategy test coverage (13% → 70%+)
End-to-end integration tests
Portfolio-level risk controls
7-day validation run
```

**Week 3-4: Integration & Validation**
```
Day 15-18: End-to-end integration test
Day 19-21: Portfolio-level risk controls
Day 22-28: 7-day testnet run (zero crashes)

Deliverable: Validated testnet system
```

**Week 5-6: Polish & Monitoring**
```
Week 5:  Monitoring dashboard + alerts
Week 6:  Documentation + disaster recovery

Deliverable: Mainnet-ready system (small capital)
```

**Total Timeline:** 6-8 weeks to safe mainnet with $50-100

---

## 📚 Documentation Status

### Up-to-Date Documentation ✅
- `README.md` - Project overview
- `CONTRIBUTING.md` - Contribution guidelines
- `AI_DEVELOPMENT.md` - AI assistant guide
- `DEPLOYMENT_PLAN.md` - Production roadmap

### New Documentation (This Update) 🆕
- `QUICK_START_GUIDE.md` - Get backtesting running in 15 minutes
- `TESTING_STRATEGY.md` - How to test without API keys
- `HAIKU_TASKS.md` - Task delegation guide

### Archive Candidates 📦
**Move to `docs/archive/`:**
- `docs/fractal-trader-context.md` - Historical context (keep for reference)
- Any prototype documents from initial sprints
- Old TODO lists (if completed)

**Keep in `docs/`:**
- Current architectural diagrams
- API documentation
- User guides

---

## 🏗️ Architecture

### What's Working Well ✅

**1. Separation of Concerns**
```
core/          → Pure SMC logic (95-100% coverage) ⭐
strategies/    → Trading decisions (uses core)
risk/          → Position sizing (98% coverage) ⭐
data/          → Market data (90% coverage)
live/          → Execution layer
```

**Why this works:** Each layer is independently testable and reusable.

**2. Test-Driven Approach**
```python
# Every module has TEST REQUIREMENTS section
# [ ] test_function_does_x
# [ ] test_edge_case_y
```

**Why this works:** Clear testing checklist prevents gaps.

**3. Type Hints & Docstrings**
```python
def calculate_position_size(
    portfolio_value: float,
    entry_price: float,
    stop_loss_price: float,
    confidence_score: int
) -> float:
    """Calculate position size based on risk."""
```

**Why this works:** Self-documenting code, IDE support, fewer bugs.

### What Needs Improvement ⚠️

**1. Strategy Test Coverage**
```
Current:  13-42% coverage
Target:   70%+ coverage
Reason:   Strategies contain actual trading logic
```

**2. Data Fetcher Reliability**
```
Current:  No retry on network failure
Target:   3 retries with exponential backoff
Reason:   Network blips shouldn't crash bot
```

**3. State Management**
```
Current:  In-memory only (lost on restart)
Target:   Persistent state (JSON file)
Reason:   Track positions across restarts
```

---

## 🔧 Development Workflow

### Quick Start

```bash
# Clone and setup
git clone https://github.com/r464r64r/FractalTrader.git
cd FractalTrader
pip install -r requirements.txt

# Run core tests (no Docker needed)
python -m pytest tests/ -v \
  --ignore=tests/test_backtesting.py \
  --ignore=tests/test_data_fetchers.py \
  --ignore=tests/test_live_trading.py
# Expected: 134 tests passing

# Run backtest demo (see QUICK_START_GUIDE.md)
python examples/backtest_demo.py --symbol BTC --days 90
```

### Full Test Suite

```bash
# Requires Docker (for vectorbt, hyperliquid dependencies)
./docker-start.sh test
# Expected: 280+ tests passing (Sprints 1-3)
```

### Before Committing

```bash
# 1. Run tests
python -m pytest tests/ -v

# 2. Check coverage (for modified modules)
python -m pytest tests/ --cov=strategies --cov-report=term-missing

# 3. Verify no debug statements
grep -r "print(" *.py | grep -v test_
grep -r "breakpoint()" *.py

# 4. Type check (optional)
mypy strategies/ --ignore-missing-imports
```

---

## 📝 Code Standards

### Type Hints (REQUIRED)
```python
def calculate_position_size(
    portfolio_value: float,
    entry_price: float,
    stop_loss: float,
    confidence: int
) -> float:
    """Calculate position size."""
    # Implementation...
```

### Docstrings (REQUIRED)
```python
def detect_liquidity_sweep(
    high: pd.Series,
    low: pd.Series,
    liquidity_levels: pd.Series,
    reversal_bars: int = 3
) -> pd.Series:
    """
    Detect liquidity sweeps (stop hunts).

    A sweep occurs when:
    1. Price exceeds liquidity level
    2. Price reverses within reversal_bars
    3. Close returns inside the level

    Args:
        high: High prices
        low: Low prices
        liquidity_levels: Series of liquidity levels
        reversal_bars: Max bars for reversal (default: 3)

    Returns:
        Boolean series marking sweep completion bars

    Example:
        >>> sweeps = detect_liquidity_sweep(
        ...     data['high'], data['low'], swing_lows
        ... )
    """
```

### Testing (REQUIRED)

**Minimum coverage targets:**
- `core/` modules: 95%+
- `strategies/`: 70%+
- `risk/`: 90%+
- New features: 80%+

**Test structure:**
```python
class TestYourFunction:
    """Tests for your_function."""

    def test_basic_functionality(self):
        """Test happy path."""
        result = your_function(valid_input)
        assert result == expected

    def test_edge_case_empty_data(self):
        """Test with empty input."""
        result = your_function(pd.Series([]))
        assert result.empty

    def test_invalid_input_raises_error(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            your_function(invalid_input)
```

---

## 🚫 Critical Rules

### DO NOT
- ❌ Modify `core/` without tests
- ❌ Skip type hints or docstrings
- ❌ Commit failing tests
- ❌ Use global state
- ❌ Test on mainnet without approval
- ❌ Decrease test coverage
- ❌ Leave debug statements (`print()`, `breakpoint()`)

### DO
- ✅ Run tests before committing
- ✅ Write tests for new code (TDD approach)
- ✅ Handle edge cases explicitly
- ✅ Update documentation
- ✅ Use Docker for backtesting
- ✅ Follow existing patterns
- ✅ Ask before major changes

---

## 🎯 Next Sprint: User Experience

**Goal:** Get backtesting working in 15 minutes for new users

**Deliverables:**
1. `examples/backtest_demo.py` - One-click backtest
2. `examples/strategy_comparison.py` - Compare all strategies
3. `examples/backtest_dashboard.py` - Interactive Streamlit UI

**Timeline:** 2-3 days

**See:** `QUICK_START_GUIDE.md` for details

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style guide
- Pull request process
- Testing requirements

---

## 📜 License & Attribution

**License:** MIT (open-source)

**Contributors:**
- Opus — Core architecture, SMC detection
- Sonnet — Strategies, risk, tests, integration
- Haiku — Data processing, reports, test fixtures
- Community — (your contributions here!)

---

## 🔗 Resources

### Documentation
- [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) - Get started fast
- [TESTING_STRATEGY.md](TESTING_STRATEGY.md) - Testing without API keys
- [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) - Production roadmap
- [HAIKU_TASKS.md](HAIKU_TASKS.md) - Task delegation guide

### External
- [Smart Money Concepts](docs/archive/fractal-trader-context.md) - SMC theory
- [vectorbt Documentation](https://vectorbt.dev/)
- [Hyperliquid Docs](https://hyperliquid.gitbook.io/)

---

**Remember:** This is research software. Never risk money you can't afford to lose.

Production readiness is a journey, not a destination. We're at 65% - let's get to 95% together. 🚀
