# Contributing to FractalTrader

Thank you for your interest in contributing to FractalTrader! This document provides guidelines for contributing to the project.

---

## 🎯 Project Vision

FractalTrader is an open-source algorithmic trading system based on **Smart Money Concepts (SMC)** for cryptocurrency markets. Our goal is to create a production-ready, well-tested trading framework that:

- Detects institutional order flow patterns (liquidity sweeps, order blocks, FVG)
- Provides robust risk management
- Maintains high code quality (>70% test coverage)
- Offers clear, comprehensive documentation

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Git
- Docker (optional, for full test suite)

### Setup

```bash
# Clone the repository
git clone https://github.com/r464r64r/FractalTrader.git
cd FractalTrader

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v
```

### Project Structure

```
fractal-trader/
├── core/           # SMC detection algorithms (95-100% test coverage)
├── strategies/     # Trading strategies (79% test coverage)
├── risk/           # Risk management (98% test coverage)
├── data/           # Data fetchers (Hyperliquid, CCXT)
├── live/           # Live trading (testnet + mainnet)
├── backtesting/    # Backtesting framework (vectorbt)
├── tests/          # 222 tests (161 without Docker)
└── docs/           # Documentation
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed architecture.

---

## 📋 How to Contribute

### 1. Find an Issue

Check our [issue tracker](https://github.com/r464r64r/FractalTrader/issues) for:
- `good first issue` — beginner-friendly tasks
- `help wanted` — areas needing contributors
- `bug` — reported bugs
- `enhancement` — feature requests

### 2. Fork & Branch

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/FractalTrader.git
cd FractalTrader

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 3. Make Changes

Follow our coding standards (see below).

### 4. Test Your Changes

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_strategies.py -v

# Check coverage
python -m pytest tests/ --cov=core --cov=strategies --cov=risk
```

**Required:** All PRs must maintain or improve test coverage.

### 5. Commit

```bash
git add .
git commit -m "Brief description of changes

Detailed explanation if needed.
Fixes #issue_number"
```

**Commit message format:**
- Use present tense ("Add feature" not "Added feature")
- First line: <50 characters
- Reference issues with "Fixes #123" or "Closes #123"

### 6. Push & Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

---

## 🎨 Code Style

### Python Standards

- **PEP 8** compliance
- **Type hints** on all functions (required)
- **Docstrings** (Google style) on all public functions
- **Line length:** 88 characters (Black formatter)

### Example

```python
def calculate_position_size(
    portfolio_value: float,
    entry_price: float,
    stop_loss_price: float,
    confidence_score: int
) -> float:
    """
    Calculate position size based on risk parameters.

    Args:
        portfolio_value: Total portfolio value in USD
        entry_price: Entry price for the trade
        stop_loss_price: Stop loss price
        confidence_score: Signal confidence (0-100)

    Returns:
        Position size in base currency

    Raises:
        ValueError: If inputs are invalid
    """
    # Implementation...
```

### Code Organization

**DO:**
- ✅ Keep functions pure where possible
- ✅ Use dataclasses for structured data
- ✅ Handle edge cases explicitly
- ✅ Add input validation
- ✅ Write self-documenting code

**DON'T:**
- ❌ Use global state
- ❌ Skip type hints
- ❌ Leave TODOs in production code
- ❌ Commit commented-out code
- ❌ Use magic numbers (define constants)

---

## 🧪 Testing Requirements

### Test Coverage Goals

| Module | Target | Current |
|--------|--------|---------|
| `core/` | 95%+ | 95-100% ✅ |
| `strategies/` | 70%+ | 79% ✅ |
| `risk/` | 90%+ | 98% ✅ |
| `data/` | 80%+ | 90% ✅ |
| `live/` | 80%+ | 80% ✅ |

### Writing Tests

**Location:** Place tests in `tests/test_<module>.py`

**Structure:**
```python
import pytest
from your_module import your_function

class TestYourFunction:
    """Tests for your_function."""

    def test_basic_functionality(self):
        """Test basic use case."""
        result = your_function(input_data)
        assert result == expected

    def test_edge_case(self):
        """Test edge case handling."""
        # Test edge cases

    def test_invalid_input(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            your_function(invalid_input)
```

**Required test types:**
- ✅ Happy path (basic functionality)
- ✅ Edge cases (empty data, extreme values)
- ✅ Error handling (invalid inputs)
- ✅ Integration (if applicable)

---

## 📝 Documentation

### When to Update Docs

Update documentation when you:
- Add new features
- Change public APIs
- Fix bugs that affect usage
- Add configuration options

### Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start |
| `DEVELOPMENT.md` | Architecture, roadmap, status |
| `DEPLOYMENT_PLAN.md` | Production deployment roadmap |
| `CONTRIBUTING.md` | This file |
| `AI_DEVELOPMENT.md` | AI assistant guidelines |

### Docstring Example

```python
def detect_liquidity_sweep(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
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
        close: Close prices
        liquidity_levels: Series of liquidity levels
        reversal_bars: Max bars for reversal (default: 3)

    Returns:
        Boolean series marking sweep completion bars

    Example:
        >>> sweeps = detect_liquidity_sweep(
        ...     data['high'], data['low'], data['close'],
        ...     swing_lows, reversal_bars=3
        ... )
        >>> sweep_count = sweeps.sum()
    """
```

---

## 🔍 Pull Request Guidelines

### PR Checklist

Before submitting, ensure:

- [ ] All tests pass (`pytest tests/ -v`)
- [ ] Coverage maintained or improved
- [ ] Code follows style guide (type hints, docstrings)
- [ ] Documentation updated (if applicable)
- [ ] Commit messages are clear
- [ ] No merge conflicts with main
- [ ] Self-reviewed changes
- [ ] No debug/print statements left

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added (if applicable)
- Coverage: X% → Y%

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks** run (tests, linting)
2. **Maintainer review** (1-3 days typical)
3. **Feedback addressed** (if any)
4. **Merge** (squash and merge)

---

## 🚫 What We Don't Accept

- Code without tests
- Undocumented public APIs
- Breaking changes without discussion
- Trading strategies without backtesting
- Code with security vulnerabilities
- GPL-licensed dependencies (MIT only)

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Update to latest version
3. Try to reproduce with minimal example

### Bug Report Template

```markdown
**Describe the bug**
Clear description of what's wrong

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Run command '...'
3. See error

**Expected behavior**
What you expected to happen

**Environment**
- OS: [e.g., macOS 13.0]
- Python version: [e.g., 3.12.1]
- FractalTrader version: [e.g., v1.0.0]

**Additional context**
Any other relevant information
```

---

## 💡 Feature Requests

We welcome feature suggestions! Please:

1. Check if it's already requested
2. Describe the use case clearly
3. Explain why it benefits the project
4. Consider offering to implement it

**Format:**
```markdown
**Feature Description**
What feature you want

**Use Case**
Why this is useful

**Proposed Implementation**
How it could work (optional)
```

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the **MIT License**.

All contributions must be your original work or properly attributed.

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming, inclusive environment for all contributors.

### Standards

**Positive behaviors:**
- ✅ Respectful communication
- ✅ Constructive feedback
- ✅ Focus on what's best for the project
- ✅ Helping newcomers

**Unacceptable:**
- ❌ Harassment or discrimination
- ❌ Trolling or insulting comments
- ❌ Personal attacks
- ❌ Publishing private information

### Enforcement

Violations may result in temporary or permanent ban from the project.

---

## 🎓 Resources

### Documentation
- [README.md](README.md) — Project overview
- [DEVELOPMENT.md](DEVELOPMENT.md) — Architecture details
- [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md) — Production roadmap

### Learning Resources
- [Smart Money Concepts](docs/archive/fractal-trader-context.md) — SMC theory
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)

### Community
- [GitHub Issues](https://github.com/r464r64r/FractalTrader/issues)
- [Discussions](https://github.com/r464r64r/FractalTrader/discussions)

---

## 🏆 Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md`
- Credited in release notes
- Mentioned in commit messages (`Co-Authored-By:`)

---

## ❓ Questions?

- **General questions:** Open a [Discussion](https://github.com/r464r64r/FractalTrader/discussions)
- **Bugs:** Open an [Issue](https://github.com/r464r64r/FractalTrader/issues)
- **Security:** Email [security contact] (add if you have one)

---

**Thank you for contributing to FractalTrader!** 🚀

Every contribution, no matter how small, helps make this project better for everyone.

---

*Last updated: 2025-12-21*
