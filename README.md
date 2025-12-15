# Fractal Trader

An algorithmic trading system based on **Smart Money Concepts (SMC)** - detecting institutional order flow patterns for cryptocurrency trading.

## Core Philosophy

Trade what institutions trade. Detect liquidity sweeps, fair value gaps, and order blocks - the footprints of smart money.

## Features

- **Market Structure Detection**: Swing points, Break of Structure (BOS), Change of Character (CHoCH)
- **Liquidity Analysis**: Equal highs/lows detection, liquidity sweep identification
- **Imbalance Detection**: Fair Value Gap (FVG) identification and fill tracking
- **Order Block Detection**: Institutional accumulation/distribution zones
- **Risk Management**: Dynamic position sizing based on confidence scoring
- **Backtesting**: Fast vectorized backtesting with vectorbt
- **Live Trading**: Freqtrade integration for production execution

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from core.market_structure import find_swing_points, determine_trend
from strategies.liquidity_sweep import LiquiditySweepStrategy
from backtesting.runner import BacktestRunner

# Load your OHLCV data
# data = load_btc_data()

# Detect market structure
swing_highs, swing_lows = find_swing_points(data['high'], data['low'], n=5)
trend = determine_trend(swing_highs, swing_lows)

# Run backtest
runner = BacktestRunner(initial_cash=10000)
strategy = LiquiditySweepStrategy()
result = runner.run(data, strategy)

print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
print(f"Win Rate: {result.win_rate:.1%}")
```

## Project Structure

```
fractal-trader/
├── core/               # Core detection algorithms
├── risk/               # Risk management engine
├── strategies/         # Trading strategies
├── backtesting/        # Research & testing
├── live/               # Production execution
├── data/               # Data management
├── utils/              # Shared utilities
└── tests/              # Test suite
```

## Strategies

1. **Liquidity Sweep Reversal**: Trade reversals after institutional stop hunts
2. **FVG Fill**: Trade returns to fair value gaps
3. **BOS + Order Block**: Trend following with structure confirmation

## License

MIT License
