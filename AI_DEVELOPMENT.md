# FractalTrader — AI Development Guide

Guidelines for AI assistants (Claude, GPT, Copilot, etc.) working on FractalTrader.

---

## 🎯 Project Overview

**FractalTrader** is an open-source algorithmic trading system based on **Smart Money Concepts (SMC)** for cryptocurrency markets.

**Current Status:** Phase 1 Complete (85% production-ready)

| Component | Status | Coverage |
|-----------|--------|----------|
| Core SMC Detection | ✅ Production | 95-100% |
| Trading Strategies | ✅ Production | 79% |
| Risk Management | ✅ Production | 98% |
| Data Layer | ✅ Complete | 90% |
| Live Trading | ⚠️ Testnet Only | 80% |

**Next Phase:** Testnet validation (24h run + monitoring)

---

## 📚 Essential Documentation

**Read these FIRST:**

| Document | Purpose | When to Read |
|----------|---------|--------------|
| [README.md](README.md) | Project overview, quick start | Always first |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Architecture, roadmap | For all changes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Code standards, PR process | Before contributing |
| [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) | Production roadmap | For deployment tasks |

**Reference:**
- `strategies/base.py` — Strategy framework
- `risk/position_sizing.py` — Risk logic
- `core/` modules — SMC detection algorithms
- `docs/archive/` — Historical context only

---

## 🏗️ Project Structure

```
FractalTrader/
├── core/           # SMC detection (95-100% coverage) ⚠️ CRITICAL
│   ├── market_structure.py
│   ├── liquidity.py
│   ├── imbalance.py
│   └── order_blocks.py
│
├── strategies/     # Trading strategies (79% coverage)
│   ├── base.py
│   ├── liquidity_sweep.py
│   ├── fvg_fill.py
│   └── bos_orderblock.py
│
├── risk/           # Risk management (98% coverage)
│   ├── confidence.py
│   └── position_sizing.py
│
├── data/           # Data fetchers (90% coverage)
│   ├── fetcher.py            # Base interface
│   ├── hyperliquid_fetcher.py # Live data
│   └── ccxt_fetcher.py       # Historical data
│
├── live/           # Live trading (80% coverage) ⚠️ TESTNET ONLY
│   └── hyperliquid/
│       ├── config.py
│       ├── testnet.py
│       └── trader.py
│
├── backtesting/    # Backtesting (Docker only)
│   └── runner.py
│
└── tests/          # 222 tests (161 without Docker)
    ├── test_market_structure.py (21 tests)
    ├── test_strategies.py (58 tests)
    └── ...
```

---

## 🔑 Key Concepts (SMC)

| Term | Definition | Where Used |
|------|------------|------------|
| **Swing High/Low** | Local price extremes | `core/market_structure.py` |
| **BOS** | Break of Structure (trend continuation) | `core/market_structure.py` |
| **CHoCH** | Change of Character (reversal) | `core/market_structure.py` |
| **FVG** | Fair Value Gap (imbalance) | `core/imbalance.py` |
| **Order Block** | Institutional accumulation zone | `core/order_blocks.py` |
| **Liquidity Sweep** | Stop hunt reversal | `core/liquidity.py` |

For detailed SMC theory, see [docs/archive/fractal-trader-context.md](docs/archive/fractal-trader-context.md).

---

## 💻 Development Workflow

### Quick Start

```bash
# Clone and setup
git clone https://github.com/r464r64r/FractalTrader.git
cd FractalTrader
pip install -r requirements.txt

# Run tests (core)
python -m pytest tests/ -v --ignore=tests/test_backtesting.py \
  --ignore=tests/test_data_fetchers.py --ignore=tests/test_live_trading.py
# Expected: 161 tests passing

# Run all tests (requires Docker)
./docker-start.sh test
# Expected: 222 tests passing
```

### Before Making Changes

1. ✅ **Read CONTRIBUTING.md** — Code standards
2. ✅ **Create feature branch** — `git checkout -b feature/name`
3. ✅ **Run existing tests** — Ensure nothing breaks
4. ✅ **Understand the module** — Read existing code + tests

### Making Changes

1. ✅ **Follow existing patterns** — Match surrounding code style
2. ✅ **Add type hints** — Required on all functions
3. ✅ **Write docstrings** — Google style, all public functions
4. ✅ **Write tests FIRST** — TDD approach preferred
5. ✅ **Handle edge cases** — Trading code must be bulletproof

### Before Committing

```bash
# Run tests
python -m pytest tests/ -v

# Check coverage (if modified strategies/core/risk)
python -m pytest tests/ --cov=strategies --cov=core --cov=risk

# Verify no debug/print statements left
grep -r "print(" *.py | grep -v test_
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

    A sweep occurs when price exceeds a level then reverses
    back inside within reversal_bars.

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

- ❌ **Modify `core/` without tests** — Foundation modules
- ❌ **Skip type hints or docstrings** — Required for all functions
- ❌ **Commit failing tests** — Fix before committing
- ❌ **Use global state** — Keep functions pure
- ❌ **Test on mainnet without approval** — Testnet first, 24h+ validation
- ❌ **Decrease test coverage** — PRs must maintain/improve coverage
- ❌ **Leave debug statements** — Remove `print()`, `breakpoint()`, etc.

### DO

- ✅ **Run tests before committing** — Every time
- ✅ **Write tests for new code** — TDD approach
- ✅ **Handle edge cases explicitly** — No silent failures
- ✅ **Update documentation** — Keep docs in sync
- ✅ **Use Docker for backtesting** — vectorbt requires it
- ✅ **Follow existing patterns** — Consistency matters
- ✅ **Ask before major changes** — Discuss architecture changes

---

## 🔧 Common Tasks

### Adding a New Strategy

1. Create `strategies/your_strategy.py` extending `BaseStrategy`
2. Implement `generate_signals(data) -> list[Signal]`
3. Add tests in `tests/test_strategies.py` (target: 70%+ coverage)
4. Add example in `examples/`
5. Update README.md strategy list

**Reference:** `strategies/liquidity_sweep.py` (82% coverage)

### Adding Tests

1. Place in `tests/test_<module>.py`
2. Use `pytest` fixtures for sample data
3. Test: happy path, edge cases, errors
4. Target coverage: >70% (strategies), >90% (risk/core)

**Reference:** `tests/test_strategies.py` (58 tests)

### Modifying Core Detection

⚠️ **CRITICAL:** Core modules are production-tested.

1. **Open an issue first** — Discuss the change
2. Read existing tests thoroughly
3. Add new tests BEFORE modifying
4. Ensure 95%+ coverage maintained
5. Get review before merging

---

## 🧪 Testing

### Test Suites

```bash
# Core tests (no Docker, 161 tests)
python -m pytest tests/test_market_structure.py \
                 tests/test_liquidity.py \
                 tests/test_strategies.py -v

# Specific module with coverage
python -m pytest tests/test_strategies.py --cov=strategies --cov-report=term-missing

# All tests (Docker, 222 tests)
./docker-start.sh test
```

### Coverage Thresholds

| Module | Current | Target | Status |
|--------|---------|--------|--------|
| `core/market_structure.py` | 97% | 95% | ✅ |
| `core/liquidity.py` | 98% | 95% | ✅ |
| `strategies/liquidity_sweep.py` | 82% | 70% | ✅ |
| `risk/position_sizing.py` | 98% | 90% | ✅ |

---

## 🎯 Current Priorities

See [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) for full roadmap.

**Phase 2 (Current):** Testnet Validation
1. End-to-end integration test
2. 24-hour testnet run (zero crashes)
3. Monitoring dashboard
4. Alert system (Telegram)

**Phase 3:** Portfolio risk controls
**Phase 4:** Mainnet readiness validation

---

## 🐛 Troubleshooting

### Import Errors

```bash
# Missing dependencies
pip install -r requirements.txt

# Hyperliquid/eth-account errors (use Docker)
./docker-start.sh
```

### Test Failures

```bash
# See full traceback
python -m pytest tests/test_file.py -v --tb=short

# Run specific test
python -m pytest tests/test_file.py::TestClass::test_method -v
```

### Docker Issues

```bash
# Rebuild container
docker build -t fractal-trader .
./docker-start.sh
```

---

## 📦 Git Workflow

### Branches

- `main` — Stable, production-ready
- `feature/*` — New features
- `fix/*` — Bug fixes
- `phase-*` — Major milestones

### Commit Messages

```
Add liquidity sweep detection tests (16 tests)

- Test private methods (_create_long_signal, _create_short_signal)
- Test edge cases (invalid stops, missing data)
- Coverage: 13% → 82%

Fixes #123
```

**Format:**
- Present tense ("Add" not "Added")
- Concise first line (<50 chars)
- Detailed explanation in body
- Reference issues ("Fixes #123")

---

## 🤝 Getting Help

- **Code questions:** See [CONTRIBUTING.md](CONTRIBUTING.md)
- **Bug reports:** [GitHub Issues](https://github.com/r464r64r/FractalTrader/issues)
- **Discussions:** [GitHub Discussions](https://github.com/r464r64r/FractalTrader/discussions)
- **SMC theory:** [docs/archive/fractal-trader-context.md](docs/archive/fractal-trader-context.md)

---

## 📜 License & Attribution

**License:** MIT (open-source)

**Contributors:**
- Opus — Core architecture, SMC detection
- Sonnet — Strategies, risk, tests, Phase 1
- Community — (your contributions here!)

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

**Last Updated:** 2025-12-21
**Version:** Phase 1 Complete (v0.9)
