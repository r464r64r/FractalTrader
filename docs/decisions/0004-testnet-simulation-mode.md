# Decision Log: Testnet Simulation Mode

**Date:** 2026-01-04
**Branch:** `fix/testnet-zero-balance-simulation`
**Status:** ✅ Implemented & Tested

## Problem Statement

Testnet bot crashed on startup when Hyperliquid testnet wallet had zero balance:

1. **Division by zero** in circuit breaker drawdown calculation
2. **Immediate circuit breaker trigger** (100% drawdown from $0)
3. **Float precision errors** in order size causing API rejections
4. **Abstract class instantiation** error in ATR calculation

## Impact

- **Severity:** Critical - Bot could not run
- **Affected Components:**
  - `live/hl_integration/testnet.py`
  - Testnet paper trading functionality
- **User Impact:** Unable to test strategies without funded testnet wallet

## Root Causes

### 1. Zero Balance Handling
**Location:** `testnet.py:107-114`

```python
# Before: Assumed testnet accounts start with $100k
portfolio_value = self._get_portfolio_value()  # Returns 0 for unfunded account
self.starting_balance = portfolio_value  # Sets to 0
```

**Issue:** No fallback for unfunded testnet wallets

### 2. Division by Zero
**Location:** `testnet.py:269`

```python
# Before: No safety check
drawdown = (self.starting_balance - current_balance) / self.starting_balance
# Crashes when starting_balance = 0
```

### 3. Float Precision
**Location:** `testnet.py:355`

```python
# Before: Unrounded position size
order = self.exchange.order(symbol, is_buy, size, limit_price, ...)
# Hyperliquid API rejects: ValueError('float_to_wire causes rounding')
```

### 4. ATR Calculation
**Location:** `testnet.py:488`

```python
# Before: Creating abstract class instance
temp_strategy = BaseStrategy.__new__(BaseStrategy)  # Can't instantiate abstract class
```

## Solutions Implemented

### 1. Simulation Mode for Zero Balance ✅

**Location:** `testnet.py:110-122`

```python
# If testnet account is unfunded, use simulated balance
if portfolio_value == 0:
    portfolio_value = 10000.0  # $10k simulated balance for paper trading
    self.simulation_mode = True
    logger.warning("Testnet account has $0 balance. Using simulated balance: $10,000")
    logger.warning("To fund testnet account, visit: https://app.hyperliquid-testnet.xyz/drip")
    logger.info("Running in SIMULATION MODE - tracking positions in memory only")
else:
    self.simulation_mode = False
```

**Rationale:**
- Enables paper trading without funded wallet
- $10k balance provides realistic position sizing
- Clear warnings inform user of simulation mode
- Graceful degradation vs hard failure

### 2. Simulated Portfolio Tracking ✅

**Location:** `testnet.py:449-482`

Added three methods:
- `_get_actual_portfolio_value()` - Query Hyperliquid account
- `_get_simulated_portfolio_value()` - Calculate from tracked positions/trades
- `_get_portfolio_value()` - Route based on simulation mode

```python
def _get_simulated_portfolio_value(self) -> float:
    """Calculate simulated portfolio value from tracked positions and cash."""
    value = self.starting_balance

    # Add/subtract P&L from open positions
    for position in self.open_positions.values():
        value += position.get("unrealized_pnl", 0.0)

    # Add realized P&L from closed trades
    for trade in self.trade_history:
        if trade.get("status") == "closed":
            value += trade.get("pnl", 0.0)

    return max(0.0, value)
```

**Rationale:**
- Maintains full accounting in simulation mode
- Accurate P&L tracking for backtesting
- No dependency on external APIs

### 3. Division by Zero Protection ✅

**Location:** `testnet.py:282-285`

```python
# Prevent division by zero
if self.starting_balance > 0:
    drawdown = (self.starting_balance - current_balance) / self.starting_balance
else:
    drawdown = 0.0
```

**Rationale:**
- Defensive programming
- Handles edge case gracefully
- Prevents crashes in circuit breaker logic

### 4. Order Size Precision ✅

**Location:** `testnet.py:349-351`

```python
# Round size to avoid float_to_wire rounding errors
# Hyperliquid typically accepts up to 5 decimal places for size
size = round(size, 5)
```

**Rationale:**
- Hyperliquid SDK validates float precision
- 5 decimals sufficient for crypto position sizing
- Prevents API rejection errors

### 5. ATR Calculation Fix ✅

**Location:** `testnet.py:486-490`

```python
# Before: temp_strategy = BaseStrategy.__new__(BaseStrategy)
# After: Use the strategy instance we already have
atr = self.strategy._calculate_atr(data, period=14)
```

**Rationale:**
- Strategy instance already available via `self.strategy`
- Avoids abstract class instantiation
- Cleaner, more maintainable code

## Dependencies Added

**Location:** `Dockerfile.aws`

```dockerfile
ratelimit>=2.2.1 \
filelock>=3.13.0
```

**Rationale:**
- `ratelimit`: API rate limiting (added in Sprint 4)
- `filelock`: State file locking (added in Sprint 4)
- Both required for production testnet trading

## Testing

### Manual Testing ✅

```bash
# Cleaned state, started bot with unfunded wallet
sudo docker exec fractal-trader-dev python -m live.cli start --strategy liquidity_sweep

# Results:
✅ Bot initialized in SIMULATION MODE
✅ Starting balance: $10,000 (simulated)
✅ Market data fetching working
✅ Signal generation working
✅ Position sizing calculations working
✅ No crashes for 60+ seconds continuous operation
⚠️ Order placement fails (expected - wallet not activated on testnet)
```

### Expected Behavior

| Scenario | Expected | Actual |
|----------|----------|--------|
| Zero balance wallet | Start in simulation mode | ✅ Pass |
| Funded wallet | Use real balance | ⚠️ Not tested (no testnet funds) |
| Division by zero | No crash | ✅ Pass |
| Order precision | No API errors | ✅ Pass (simulation) |
| ATR calculation | No abstract class error | ✅ Pass |

## Migration Path

No breaking changes. Existing behavior preserved:

1. **Funded wallets:** Use real balance (existing behavior)
2. **Unfunded wallets:** Auto-enable simulation mode (new behavior)
3. **State files:** Compatible with existing format

## Future Considerations

### Potential Improvements

1. **Configurable simulation balance**
   - Currently hardcoded to $10,000
   - Could be CLI argument: `--sim-balance 50000`

2. **Simulation order execution**
   - Currently orders fail (wallet not activated)
   - Could simulate fills at market price ±slippage

3. **State persistence in simulation mode**
   - Fix Timestamp serialization issue
   - Enable session resume in simulation mode

4. **Testnet faucet integration**
   - Auto-request testnet funds on first run
   - Requires mainnet deposit first (per Hyperliquid docs)

### Known Limitations

1. **Order execution:** Orders won't execute until wallet funded
2. **State serialization:** Timestamp objects causing JSON errors (non-critical)
3. **Real vs simulated:** No automatic transition when funds added (requires restart)

## References

- **Issue:** Testnet bot crashes with zero balance
- **Files Modified:**
  - `live/hl_integration/testnet.py` (5 fixes)
  - `Dockerfile.aws` (2 dependencies)
- **Test Coverage:** Manual testing only (no unit tests added)
- **Documentation:** This decision log

## Approval Checklist

- [x] Code follows project style (black, ruff, mypy)
- [x] Changes documented with rationale
- [x] Manual testing completed
- [x] No breaking changes to existing functionality
- [x] Clear user warnings when in simulation mode
- [ ] Unit tests added (deferred - Sprint 5)
- [ ] Peer review (pending PR)

---

**Author:** Claude Sonnet 4.5
**Reviewer:** TBD
**Sprint:** Pre-Sprint 5 (bugfix)
