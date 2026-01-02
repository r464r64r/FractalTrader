# Sprint 4 Implementation Guide (For Sonnet)

**From:** Opus
**Date:** Dec 31, 2024
**Priority:** Critical (before 7-day testnet)
**Estimated time:** 8-10h total

---

## Overview

Implement these 4 tasks in order. Each has exact code examples - adapt to codebase style.

---

## Task 1: Fix Race Condition in StateManager (2-3h)

### Problem
`live/state_manager.py:281-294` - `_save_state()` uses `open()` without locking. Concurrent bot + CLI = corrupted JSON.

### Solution

**Step 1:** Add dependency
```bash
pip install filelock
# Add to requirements.txt: filelock>=3.12.0
```

**Step 2:** Modify `StateManager.__init__()` (line ~67):
```python
from filelock import FileLock

def __init__(self, ...):
    # ... existing code ...
    self.state_file = Path(state_file)
    self._lock = FileLock(f"{self.state_file}.lock", timeout=10)
    # ... rest of init ...
```

**Step 3:** Modify `_save_state()` (line ~281):
```python
def _save_state(self) -> None:
    """Save current state to file with file locking."""
    try:
        with self._lock:
            # Create backup before saving
            if self.state_file.exists():
                self._create_backup()

            # Write state to file
            with open(self.state_file, 'w') as f:
                json.dump(self.state.to_dict(), f, indent=2)

        logger.debug(f"State saved to {self.state_file}")
    except Timeout:
        logger.error("Could not acquire file lock - another process is writing")
    except Exception as e:
        logger.error(f"Failed to save state: {e}")
```

**Step 4:** Modify `_load_or_create_state()` (line ~261):
```python
def _load_or_create_state(self) -> TradingState:
    """Load existing state or create new one."""
    if self.state_file.exists():
        try:
            with self._lock:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
            logger.info(f"Loaded state from {self.state_file}")
            return TradingState.from_dict(data)
        except Exception as e:
            # ... existing error handling ...
```

### Tests to Add (`tests/test_state_manager.py`)

```python
import threading
import time

def test_concurrent_write_safety():
    """Test that concurrent writes don't corrupt state."""
    manager = StateManager(state_file='.test_concurrent.json')
    errors = []

    def writer(n):
        try:
            for i in range(10):
                manager.save_trade({'id': f'{n}-{i}', 'symbol': 'BTC'})
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=writer, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0
    # Verify state is valid JSON
    manager2 = StateManager(state_file='.test_concurrent.json')
    assert len(manager2.load_trade_history()) == 50

def test_lock_timeout():
    """Test that lock timeout is handled gracefully."""
    # This tests the Timeout exception path
    pass  # Implement based on your mocking approach
```

---

## Task 2: Add API Rate Limiting (2-3h)

### Problem
`data/hyperliquid_fetcher.py` - No rate limiting. High activity = potential ban.

### Solution

**Step 1:** Add dependency
```bash
pip install ratelimit
# Add to requirements.txt: ratelimit>=2.2.1
```

**Step 2:** Create `utils/rate_limit.py`:
```python
"""Rate limiting utilities for API calls."""

from functools import wraps
from ratelimit import limits, sleep_and_retry
import logging

logger = logging.getLogger(__name__)

# Hyperliquid limits (conservative estimates)
CALLS_PER_SECOND = 5
CALLS_PER_MINUTE = 100


def rate_limited(calls: int = CALLS_PER_SECOND, period: int = 1):
    """
    Decorator for rate-limited API calls.

    Args:
        calls: Max calls per period
        period: Period in seconds

    Example:
        @rate_limited(calls=5, period=1)
        def fetch_data():
            ...
    """
    def decorator(func):
        @sleep_and_retry
        @limits(calls=calls, period=period)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator


def rate_limited_minute(calls: int = CALLS_PER_MINUTE):
    """Rate limit per minute (for heavier endpoints)."""
    return rate_limited(calls=calls, period=60)
```

**Step 3:** Apply to `data/hyperliquid_fetcher.py`:
```python
from utils.rate_limit import rate_limited

class HyperliquidFetcher(BaseFetcher):

    @rate_limited(calls=5, period=1)
    def fetch_ohlcv(self, symbol: str, timeframe: str = '1h', ...):
        # ... existing implementation ...

    @rate_limited(calls=10, period=1)
    def get_current_price(self, symbol: str) -> float:
        # ... existing implementation ...
```

**Step 4:** Apply to `live/hl_integration/testnet.py` (API calls in trading):
```python
from utils.rate_limit import rate_limited

class HyperliquidTestnetTrader:

    @rate_limited(calls=2, period=1)  # More conservative for trading
    def _place_order(self, signal: Signal, size: float):
        # ... existing implementation ...

    @rate_limited(calls=5, period=1)
    def _get_portfolio_value(self) -> float:
        # ... existing implementation ...
```

### Tests (`tests/test_rate_limit.py`)

```python
import time
from utils.rate_limit import rate_limited

def test_rate_limit_slows_calls():
    """Test that rate limiting actually slows down calls."""
    call_times = []

    @rate_limited(calls=2, period=1)
    def tracked_call():
        call_times.append(time.time())

    # Make 4 calls - should take at least 1 second
    start = time.time()
    for _ in range(4):
        tracked_call()
    elapsed = time.time() - start

    assert elapsed >= 1.0, f"Expected >= 1s, got {elapsed}s"

def test_rate_limit_allows_burst():
    """Test that burst within limit is allowed."""
    @rate_limited(calls=5, period=1)
    def fast_call():
        return True

    start = time.time()
    results = [fast_call() for _ in range(5)]
    elapsed = time.time() - start

    assert all(results)
    assert elapsed < 0.5  # Should be fast (within burst limit)
```

---

## Task 3: Improve Circuit Breaker Error Handling (2h)

### Problem
`live/hl_integration/testnet.py:220-221` - All exceptions trigger same response. Network hiccup = unnecessary stop.

### Solution

**Step 1:** Create `live/exceptions.py`:
```python
"""Custom exceptions for live trading."""


class TradingError(Exception):
    """Base class for trading errors."""
    pass


class TransientError(TradingError):
    """
    Temporary error that should be retried.

    Examples: network timeout, rate limit, temporary API unavailable
    """
    pass


class CriticalError(TradingError):
    """
    Critical error that should stop trading.

    Examples: authentication failed, insufficient funds, invalid order
    """
    pass


def classify_error(error: Exception) -> type:
    """
    Classify an exception as Transient or Critical.

    Args:
        error: The exception to classify

    Returns:
        TransientError or CriticalError class
    """
    transient_patterns = [
        'timeout', 'timed out', 'connection', 'network',
        'rate limit', 'too many requests', '429', '503', '504',
        'temporary', 'retry'
    ]

    error_str = str(error).lower()
    error_type = type(error).__name__.lower()

    for pattern in transient_patterns:
        if pattern in error_str or pattern in error_type:
            return TransientError

    return CriticalError
```

**Step 2:** Modify `live/hl_integration/testnet.py`:

```python
from live.exceptions import TransientError, CriticalError, classify_error

class HyperliquidTestnetTrader:

    def __init__(self, ...):
        # ... existing code ...

        # Error tracking for circuit breaker
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5  # Stop after 5 transient errors in a row
        self.error_backoff_seconds = [5, 10, 30, 60, 120]  # Exponential backoff

    def _trading_iteration(self):
        """Single iteration of trading loop with improved error handling."""
        try:
            # Check circuit breakers first
            if not self._check_circuit_breakers():
                return

            # ... existing trading logic ...

            # Reset error counter on success
            self.consecutive_errors = 0

        except Exception as e:
            self._handle_error(e)

    def _handle_error(self, error: Exception):
        """Handle errors with classification and appropriate response."""
        error_class = classify_error(error)

        if error_class == TransientError:
            self.consecutive_errors += 1

            if self.consecutive_errors >= self.max_consecutive_errors:
                logger.critical(
                    f"🛑 CIRCUIT BREAKER: {self.consecutive_errors} consecutive "
                    f"transient errors. Stopping."
                )
                self.circuit_breaker_triggered = True
                self.stop()
                return

            # Exponential backoff
            backoff_idx = min(self.consecutive_errors - 1, len(self.error_backoff_seconds) - 1)
            wait_time = self.error_backoff_seconds[backoff_idx]

            logger.warning(
                f"Transient error ({self.consecutive_errors}/{self.max_consecutive_errors}): "
                f"{error}. Retrying in {wait_time}s..."
            )
            time.sleep(wait_time)

        else:  # CriticalError
            logger.critical(f"🛑 CRITICAL ERROR: {error}")
            logger.critical("Stopping trading immediately.")
            self.circuit_breaker_triggered = True
            self.stop()
```

### Tests (`tests/test_error_handling.py`)

```python
from live.exceptions import classify_error, TransientError, CriticalError

def test_classify_timeout_as_transient():
    assert classify_error(TimeoutError("Connection timed out")) == TransientError

def test_classify_connection_error_as_transient():
    assert classify_error(ConnectionError("Network unreachable")) == TransientError

def test_classify_rate_limit_as_transient():
    assert classify_error(Exception("429 Too Many Requests")) == TransientError

def test_classify_auth_error_as_critical():
    assert classify_error(Exception("Authentication failed")) == CriticalError

def test_classify_insufficient_funds_as_critical():
    assert classify_error(Exception("Insufficient margin")) == CriticalError

def test_classify_unknown_as_critical():
    """Unknown errors should be treated as critical (safe default)."""
    assert classify_error(Exception("Something weird happened")) == CriticalError
```

---

## Task 4: Add Pre-commit Hooks + CI (1-2h)

### Step 1: Create `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pandas-stubs
          - types-requests
        args: [--ignore-missing-imports]

  - repo: local
    hooks:
      - id: pytest-fast
        name: pytest (fast tests only)
        entry: python -m pytest tests/ -x -q --ignore=tests/test_live_trading.py --ignore=tests/test_data_fetchers.py
        language: system
        pass_filenames: false
        always_run: true
```

### Step 2: Create `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main, 'claude/*']
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov black ruff mypy

      - name: Lint with ruff
        run: ruff check .

      - name: Format check with black
        run: black --check .

      - name: Type check with mypy
        run: mypy --ignore-missing-imports strategies/ core/ risk/

      - name: Run tests
        run: |
          pytest tests/ -v --cov=. --cov-report=xml \
            --ignore=tests/test_live_trading.py \
            --ignore=tests/test_data_fetchers.py

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: false
```

### Step 3: Setup commands

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files (first time)
pre-commit run --all-files
```

---

## Verification Checklist

After implementation, verify:

- [ ] `pytest tests/test_state_manager.py -v` - all pass including new concurrent tests
- [ ] `pytest tests/test_rate_limit.py -v` - all pass
- [ ] `pytest tests/test_error_handling.py -v` - all pass
- [ ] `pytest tests/ --ignore=tests/test_live_trading.py --ignore=tests/test_data_fetchers.py` - all 350+ tests pass
- [ ] `pre-commit run --all-files` - passes
- [ ] Coverage not decreased (currently 92%)

---

## Notes

1. **Order matters:** Do Task 1 first (state safety), then 2-3 (runtime safety), then 4 (DX)
2. **Test each task** before moving to next
3. **Commit after each task** with descriptive message
4. If stuck, check existing patterns in codebase

---

**Questions?** Leave a note in this file or create an issue.

Good luck! 🚀
