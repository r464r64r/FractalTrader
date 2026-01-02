# FractalTrader — Known Issues & Priorities

**Updated:** 2026-01-02

## Critical (Sprint 4)

### 1. Low Strategy Test Coverage
| Strategy | Coverage | Target |
|----------|----------|--------|
| liquidity_sweep.py | 13% | 70% |
| bos_orderblock.py | 42% | 70% |
| fvg_fill.py | ~40% | 70% |

**Impact:** Cannot safely deploy to production without tests.

### 2. Race Condition in StateManager
**Location:** `live/state_manager.py:281-294`
**Problem:** `_save_state()` uses `open()` without file locking. Concurrent bot + CLI access can corrupt JSON state.
**Solution:** Add `filelock` library.

### 3. No API Rate Limiting
**Location:** `data/hyperliquid_fetcher.py`, `live/hl_integration/testnet.py`
**Problem:** No rate limiting on API calls. Hyperliquid ban = end of test.
**Solution:** Add `ratelimit` decorator (10 calls/sec).

### 4. Circuit Breaker Error Handling
**Location:** `live/hl_integration/testnet.py:220-221`
**Problem:** All exceptions treated equally. Transient network error = bot stops unnecessarily.
**Solution:** Classify errors as TransientError vs CriticalError.

## Medium Priority

### 5. Code Duplication in Strategies
- `calculate_confidence()` is ~80% identical across strategies
- `_create_long_signal()` / `_create_short_signal()` similar structure
**Solution:** `ConfidenceCalculator` mixin, `SignalFactory` helper.

### 6. Missing Parameter Validation
- Strategy params accept invalid values (e.g., `min_rr_ratio: -5`)
**Solution:** Pydantic models for strategy params.

## Low Priority

### 7. Documentation Inconsistencies
- Some files reference 2025, others 2026
- README.md roadmap file references outdated (fixed in this cleanup)

### 8. Pre-commit Hooks
- No automated linting/formatting on commit
**Solution:** Add `.pre-commit-config.yaml` with black, ruff, mypy.

---

## Resolved (This Session)

- [x] Duplicate documentation (quick_start.md removed)
- [x] Chaotic docs structure (reorganized with archive/)
- [x] Outdated .claude/project-context.md (updated)
- [x] No central AI context (CLAUDE.md created)
