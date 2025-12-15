# Fractal Trader — Development Continuation Guide

## Current State (December 2024)

### Completed Components ✅

| Component | File | Status | Tests |
|-----------|------|--------|-------|
| Swing Points | `core/market_structure.py` | ✅ Done | 21 tests |
| Trend Detection | `core/market_structure.py` | ✅ Done | Included |
| BOS/CHoCH Detection | `core/market_structure.py` | ✅ Done | Included |
| Equal Levels | `core/liquidity.py` | ✅ Done | 16 tests |
| Liquidity Sweeps | `core/liquidity.py` | ✅ Done | Included |
| Base Strategy | `strategies/base.py` | ✅ Done | - |
| Liquidity Sweep Strategy | `strategies/liquidity_sweep.py` | ✅ Done | - |

**Total: 37 tests passing**

### Remaining Tasks 🔧

#### Priority 1: Risk Management
```
risk/confidence.py      - ConfidenceFactors dataclass (copy from context doc)
risk/position_sizing.py - calculate_position_size() function
```

#### Priority 2: Backtesting
```
backtesting/runner.py   - BacktestRunner class with vectorbt
```

#### Priority 3: Additional Strategies (Optional)
```
core/imbalance.py       - FVG detection
strategies/fvg_fill.py  - FVG fill strategy
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
