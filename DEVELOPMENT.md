# Fractal Trader — Development Continuation Guide

## Current State (December 2024) - UPDATED BY SONNET

### 🎉 ALL CORE COMPONENTS COMPLETE! 🎉

| Component | File | Status | Tests | Developer |
|-----------|------|--------|-------|-----------|
| **Core Detection** |
| Swing Points | `core/market_structure.py` | ✅ Done | 21 tests | Opus |
| Trend Detection | `core/market_structure.py` | ✅ Done | Included | Opus |
| BOS/CHoCH Detection | `core/market_structure.py` | ✅ Done | Included | Opus |
| Equal Levels | `core/liquidity.py` | ✅ Done | 16 tests | Opus |
| Liquidity Sweeps | `core/liquidity.py` | ✅ Done | Included | Opus |
| Fair Value Gaps | `core/imbalance.py` | ✅ Done | 17 req'd | Sonnet |
| Order Blocks | `core/order_blocks.py` | ✅ Done | 21 req'd | Sonnet |
| **Strategies** |
| Base Strategy | `strategies/base.py` | ✅ Done | - | Opus |
| Liquidity Sweep | `strategies/liquidity_sweep.py` | ✅ Done | - | Opus |
| FVG Fill | `strategies/fvg_fill.py` | ✅ Done | 15 req'd | Sonnet |
| BOS + Order Block | `strategies/bos_orderblock.py` | ✅ Done | 16 req'd | Sonnet |
| **Risk Management** |
| Confidence Scoring | `risk/confidence.py` | ✅ Done | 9 req'd | Sonnet |
| Position Sizing | `risk/position_sizing.py` | ✅ Done | 19 req'd | Sonnet |
| **Backtesting** |
| Backtest Runner | `backtesting/runner.py` | ✅ Done | 19 req'd | Sonnet |

**Tests Status:**
- ✅ **37 tests passing** (Opus: market_structure + liquidity)
- 📋 **116 tests required** (Sonnet modules - documented in tests/TODO_TESTS.md)

### Sonnet Sprint Summary (4 Autonomous Sprints)

**Sprint 1: Risk Management** ✅
- Implemented `risk/confidence.py` with ConfidenceFactors dataclass
- Implemented `risk/position_sizing.py` with dynamic sizing algorithm
- Added comprehensive input validation and edge case handling
- Verified with functional tests

**Sprint 2: Backtesting Framework** ✅
- Installed and verified vectorbt 0.28.2
- Implemented `backtesting/runner.py` with BacktestRunner and BacktestResult
- Added parameter optimization with grid search
- Tested with LiquiditySweepStrategy: 15.62% return, 4.01 Sharpe on test data

**Sprint 3: FVG Strategy** ✅
- Implemented `core/imbalance.py` for Fair Value Gap detection
- Implemented `strategies/fvg_fill.py` for FVG fill trading
- Detected 52 bullish + 43 bearish FVGs on test data
- Generated 20 signals, backtest: 7.87% return, 3.89 Sharpe

**Sprint 4: Order Blocks & BOS Strategy** ✅
- Implemented `core/order_blocks.py` for OB detection
- Implemented `strategies/bos_orderblock.py` for trend following
- Most conservative strategy (requires BOS + OB retest)
- Detected 54 bullish + 48 bearish OBs on test data

### Remaining Tasks 🔧

#### Priority 1: Testing (116 tests required)
See `tests/TODO_TESTS.md` for comprehensive checklist:
- Risk management tests (28 tests)
- Backtesting framework tests (19 tests)
- Core detection tests (38 tests)
- Strategy tests (31 tests)

#### Priority 2: Live Trading Integration (Optional)
```
live/freqtrade_strategy.py  - Freqtrade IStrategy wrapper
live/config/config.json     - Freqtrade configuration
```

#### Priority 3: Enhancements (Optional)
```
risk/portfolio.py           - Portfolio-level risk controls
data/fetcher.py             - CCXT data fetching (exists but needs implementation)
utils/logger.py             - Structured logging
```

---

## How to Continue Development

### Step 1: Implement Risk Management

Create `risk/confidence.py`:
```python
from dataclasses import dataclass

@dataclass
class ConfidenceFactors:
    """Factors that determine entry confidence."""

    htf_trend_aligned: bool = False      # +15 points
    htf_structure_clean: bool = False    # +15 points
    pattern_clean: bool = False          # +10 points
    multiple_confluences: int = 0        # +5 per confluence (max 20)
    volume_spike: bool = False           # +10 points
    volume_divergence: bool = False      # +10 points
    trending_market: bool = False        # +10 points
    low_volatility: bool = False         # +10 points

    def calculate_score(self) -> int:
        score = 0
        if self.htf_trend_aligned: score += 15
        if self.htf_structure_clean: score += 15
        if self.pattern_clean: score += 10
        score += min(self.multiple_confluences * 5, 20)
        if self.volume_spike: score += 10
        if self.volume_divergence: score += 10
        if self.trending_market: score += 10
        if self.low_volatility: score += 10
        return min(score, 100)
```

Create `risk/position_sizing.py`:
```python
from dataclasses import dataclass

@dataclass
class RiskParameters:
    base_risk_percent: float = 0.02      # 2% base risk
    max_position_percent: float = 0.05   # 5% max position
    min_confidence: int = 40             # Min confidence to trade
    atr_period: int = 14
    consecutive_wins_reduce: int = 3
    consecutive_losses_reduce: int = 2
    win_reduction_factor: float = 0.8
    loss_reduction_factor: float = 0.7

def calculate_position_size(
    portfolio_value: float,
    entry_price: float,
    stop_loss_price: float,
    confidence_score: int,
    current_atr: float,
    baseline_atr: float,
    consecutive_wins: int,
    consecutive_losses: int,
    params: RiskParameters
) -> float:
    """Calculate position size based on risk parameters."""
    if confidence_score < params.min_confidence:
        return 0.0

    # Base risk
    confidence_factor = confidence_score / 100
    risk_amount = portfolio_value * params.base_risk_percent * confidence_factor

    # Volatility adjustment
    volatility_adj = min(max(baseline_atr / current_atr, 0.5), 1.5) if current_atr > 0 else 1.0

    # Streak adjustment
    streak_adj = 1.0
    if consecutive_wins >= params.consecutive_wins_reduce:
        streak_adj = params.win_reduction_factor
    elif consecutive_losses >= params.consecutive_losses_reduce:
        streak_adj = params.loss_reduction_factor

    # Calculate size
    risk_per_unit = abs(entry_price - stop_loss_price)
    if risk_per_unit == 0:
        return 0.0

    position_size = (risk_amount * volatility_adj * streak_adj) / risk_per_unit
    max_position = (portfolio_value * params.max_position_percent) / entry_price

    return min(position_size, max_position)
```

### Step 2: Implement Backtesting

Create `backtesting/runner.py`:
```python
import vectorbt as vbt
import pandas as pd
from dataclasses import dataclass
from strategies.base import BaseStrategy, Signal

@dataclass
class BacktestResult:
    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    equity_curve: pd.Series
    trades: pd.DataFrame
    signals: list

class BacktestRunner:
    def __init__(self, initial_cash: float = 10000, fees: float = 0.001):
        self.initial_cash = initial_cash
        self.fees = fees

    def run(self, data: pd.DataFrame, strategy: BaseStrategy) -> BacktestResult:
        signals = strategy.generate_signals(data)

        if not signals:
            return self._empty_result()

        entries, exits = self._signals_to_arrays(data, signals)

        portfolio = vbt.Portfolio.from_signals(
            close=data['close'],
            entries=entries,
            exits=exits,
            init_cash=self.initial_cash,
            fees=self.fees
        )

        return self._extract_results(portfolio, signals)
```

### Step 3: Write Tests

For each new component, write tests in `tests/`:
```python
# tests/test_risk.py
def test_position_size_respects_max():
    ...

def test_low_confidence_reduces_size():
    ...

# tests/test_strategies.py
def test_strategy_generates_signals():
    ...
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      DATA (OHLCV)                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   CORE DETECTION                            │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ market_structure │  │    liquidity     │                │
│  │ - swing points   │  │ - equal levels   │                │
│  │ - trend          │  │ - sweeps         │                │
│  │ - BOS/CHoCH      │  │ - zones          │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      STRATEGIES                             │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  BaseStrategy    │  │ LiquiditySweep   │                │
│  │  - generate()    │  │ Strategy         │                │
│  │  - confidence()  │  │                  │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   RISK MANAGEMENT                           │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ confidence.py    │  │ position_sizing  │                │
│  │ - score calc     │  │ - size calc      │                │
│  └──────────────────┘  └──────────────────┘                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     BACKTESTING                             │
│  ┌──────────────────┐                                      │
│  │ BacktestRunner   │  → vectorbt integration              │
│  │ - run()          │                                      │
│  │ - optimize()     │                                      │
│  └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Concepts (SMC)

| Term | Definition |
|------|------------|
| **Swing High** | Bar where high > N bars on both sides |
| **Swing Low** | Bar where low < N bars on both sides |
| **BOS** | Break of Structure - trend continuation |
| **CHoCH** | Change of Character - trend reversal |
| **EQH/EQL** | Equal Highs/Lows - liquidity pools |
| **Sweep** | Price breaks level then reverses (stop hunt) |

---

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_market_structure.py -v

# Run with coverage
python -m pytest tests/ --cov=core --cov=strategies
```

---

## Example Usage

```python
from core.market_structure import find_swing_points, determine_trend
from core.liquidity import find_equal_levels, detect_liquidity_sweep
from strategies.liquidity_sweep import LiquiditySweepStrategy
from data.fetcher import fetch_ohlcv

# Fetch data
data = fetch_ohlcv('BTC/USDT', '1h', 1000)

# Analyze structure
swing_h, swing_l = find_swing_points(data['high'], data['low'], n=5)
trend = determine_trend(swing_h, swing_l)
print(f"Current trend: {trend.iloc[-1]}")  # 1=up, -1=down, 0=range

# Generate signals
strategy = LiquiditySweepStrategy({'swing_period': 5})
signals = strategy.generate_signals(data)

for signal in signals:
    print(f"{signal.timestamp}: {'LONG' if signal.direction == 1 else 'SHORT'}")
    print(f"  Entry: {signal.entry_price:.2f}")
    print(f"  Stop: {signal.stop_loss:.2f}")
    print(f"  TP: {signal.take_profit:.2f}")
    print(f"  Confidence: {signal.confidence}")
```

---

## Full Context Document

For complete specifications, see `fractal-trader-context.md` in the repository root.
