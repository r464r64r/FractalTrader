# Opus Recommendation: Critical Hardening Sprint

**Date:** Dec 31, 2024
**Sprint:** Sprint 4 - Production Hardening
**Recommendation:** Critical Hardening Sprint (8-10h)

---

## Executive Summary

Before the 7-day testnet validation, I recommend focusing on **eliminating systemic risks** rather than adding new features. Three critical issues could cause test failure:

1. **Race condition in StateManager** - concurrent bot + CLI access can corrupt JSON state
2. **No API rate limiting** - Hyperliquid can ban on high activity
3. **Circuit breaker treats all errors equally** - network hiccup = false stop

---

## Proposed Tasks

### 1. Fix Race Condition in StateManager (2-3h)

**Location:** `live/state_manager.py:281-294`

**Problem:** `_save_state()` uses `open()` without file locking. If bot and CLI run simultaneously, they can corrupt the JSON file.

**Solution:**
```python
from filelock import FileLock

def _save_state(self) -> None:
    lock = FileLock(f"{self.state_file}.lock")
    with lock:
        # existing save logic
```

**Risk:** Low - isolated change, easy to test
**Test:** Concurrent access test, stress test with multiple processes

---

### 2. Add API Rate Limiting (2-3h)

**Location:** `data/hyperliquid_fetcher.py`, `live/hyperliquid/testnet.py`

**Problem:** No rate limiting on API calls. Hyperliquid has limits (undocumented but exist). Ban = end of test.

**Solution:**
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=10, period=1)  # 10 calls/sec
def fetch_ohlcv(self, ...):
    ...
```

**Risk:** Low - decorator on existing methods
**Test:** Mock API, verify timing between calls

---

### 3. Improve Circuit Breaker Error Handling (2h)

**Location:** `live/hyperliquid/testnet.py:220-221`

**Problem:** All exceptions are treated equally. Transient network error = bot stops unnecessarily.

**Solution:**
```python
class TransientError(Exception): pass  # retry
class CriticalError(Exception): pass   # stop

# In circuit breaker:
except TransientError:
    logger.warning("Transient error, retrying...")
    time.sleep(5)
except CriticalError:
    self.circuit_breaker_triggered = True
```

**Risk:** Low-Medium - requires defining error types
**Test:** Simulate different exception types

---

### 4. Add Pre-commit Hooks + Basic CI (1-2h)

**What:** `black`, `ruff`, `mypy --strict`, `pytest` (fast tests only)

**Why:** Prevents regression, automatic validation on every commit

**Deliverables:**
- `.pre-commit-config.yaml`
- `.github/workflows/ci.yml`

**Risk:** Very Low - configuration only

---

## Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Production readiness | 85% | 90-92% |
| 7-day testnet confidence | Medium | High |
| Critical failure points | 3 | 0 |

---

## Why NOT Other Options

### Option B (Performance Sprint)
- Premature optimization
- 10-100x faster backtests won't help 7-day live test
- Better after testnet validates basic operation

### Option C (Feature Sprint)
- MTF confidence adds ~400 lines of new code
- New edge cases = new bugs
- Higher risk before testnet
- Save for Sprint 5

### Option D (Balanced Sprint)
- Too spread out
- Better to focus on eliminating risks completely

---

## Additional Observations (Post-Testnet)

**Code Duplication:**
- `calculate_confidence()` is ~80% identical across strategies
- `_create_long_signal()` / `_create_short_signal()` - similar structure
- Proposal: `ConfidenceCalculator` mixin, `SignalFactory` helper

**Missing Parameter Validation:**
- `min_rr_ratio: -5` would pass without error
- Solution: Pydantic models for strategy params

---

## Bottom Line

> "If you had 10-16 hours before 7-day testnet, what would you focus on?"

**File locking + Rate limiting + Error handling + CI**

This minimizes the risk of infrastructure failures. Features can wait - a working bot that survives 7 days is more valuable than a bot with better signals that crashes after 2 days.

---

**Status:** Ready for implementation
**Estimated time:** 8-10 hours
**Questions?** Ready to start any of these tasks.
