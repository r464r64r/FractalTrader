# 🧪 FractalTrader — Testing Strategy

**Goal:** Comprehensive testing without API keys or exchange accounts  
**Philosophy:** Test early, test often, test everything

---

## 📋 Testing Pyramid

```
                    /\
                   /  \
                  / E2E \          ← 5% (Full system)
                 /--------\
                /          \
               / Integration\      ← 15% (Components together)
              /--------------\
             /                \
            /   Unit Tests     \   ← 80% (Individual functions)
           /____________________\
```

**Our approach:**
- 80% unit tests (fast, isolated, no dependencies)
- 15% integration tests (Docker-based)
- 5% end-to-end tests (testnet validation)

---

## 🎯 Test Categories

### 1. Unit Tests (No Dependencies)

**What:** Test individual functions in isolation  
**Speed:** Fast (<1s per test)  
**Coverage Target:** 95%+ for core modules

**Run:**
```bash
# Fast tests only (no Docker)
python -m pytest tests/ -v \
  --ignore=tests/test_backtesting.py \
  --ignore=tests/test_data_fetchers.py \
  --ignore=tests/test_live_trading.py

# Expected: 134 tests passing in <10s
```

### 2. Integration Tests (Docker Required)

**What:** Test components working together  
**Speed:** Medium (10-30s per test)

**Run:**
```bash
./docker-start.sh test
# Expected: 280+ tests passing (with Docker, Sprints 1-3)
```

### 3. End-to-End Tests (Testnet)

**What:** Full system test with real exchange  
**Speed:** Slow (hours/days)

---

## 🏗️ Test Fixtures

### Reusable Test Data

```python
# tests/conftest.py
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_ohlcv():
    """Generate realistic OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200, freq='1h')
    close = 100 + np.cumsum(np.random.randn(200) * 0.5)
    
    return pd.DataFrame({
        'open': close + np.random.randn(200) * 0.2,
        'high': close + np.abs(np.random.randn(200) * 0.5),
        'low': close - np.abs(np.random.randn(200) * 0.5),
        'close': close,
        'volume': np.random.randint(1000, 10000, 200)
    }, index=dates)
```

---

## 🔍 Testing Without API Keys

### Mock Exchange Responses

```python
from unittest.mock import Mock, patch

@patch('hyperliquid.info.Info')
def test_retry_logic(mock_info):
    """Test retry on network failure."""
    mock_info.return_value.candles_snapshot.side_effect = [
        ConnectionError("Timeout"),  # Fails
        ConnectionError("Timeout"),  # Fails
        [{'time': 1000, 'open': 100}]  # Succeeds
    ]
    
    fetcher = HyperliquidFetcher()
    data = fetcher.fetch_ohlcv('BTC', '1h', 100)
    
    assert len(data) > 0
    assert mock_info.return_value.candles_snapshot.call_count == 3
```

---

## 🎭 Edge Cases to Test

### Empty Data
```python
def test_handles_empty_data():
    strategy = LiquiditySweepStrategy()
    signals = strategy.generate_signals(pd.DataFrame())
    assert signals == []
```

### Extreme Volatility
```python
def test_position_sizing_high_vol():
    size_normal = calculate_position_size(..., current_atr=100, ...)
    size_extreme = calculate_position_size(..., current_atr=500, ...)
    
    assert size_extreme < size_normal
    assert size_extreme >= size_normal * 0.5  # Floor at 0.5x
```

---

## 📊 Coverage Goals

| Module | Current | Target | Status |
|--------|---------|--------|--------|
| `core/market_structure.py` | 97% | 95% | ✅ |
| `core/liquidity.py` | 98% | 95% | ✅ |
| `strategies/liquidity_sweep.py` | 13% | 70% | ❌ |
| `strategies/bos_orderblock.py` | 42% | 70% | ❌ |

### Check Coverage

```bash
python -m pytest tests/ --cov=strategies --cov-report=html
open htmlcov/index.html
```

---

## ✅ Testing Checklist

### Before Committing
- [ ] All unit tests pass
- [ ] No decrease in coverage
- [ ] Edge cases tested
- [ ] No debug statements

### Before Testnet
- [ ] All tests pass for 7 days
- [ ] State persistence tested
- [ ] Circuit breaker tested

---

**See full guide:** [tests/](tests/) directory

Testing = Confidence. Test thoroughly, deploy safely. 🧪
