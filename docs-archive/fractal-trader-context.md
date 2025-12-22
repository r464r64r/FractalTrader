# Fractal Trader — Complete Project Context for Claude Code

**Version:** 1.0.0  
**Date:** December 2024  
**Purpose:** One-shot context for autonomous code generation  
**Target:** Claude Code on GitHub repository

---

## Executive Summary

Build an algorithmic trading system focused on **Smart Money Concepts (SMC)** — detecting institutional order flow patterns rather than relying on lagging indicators. The system must support backtesting, paper trading, and live execution with robust risk management.

**Core Philosophy:** Trade what institutions trade. Detect liquidity sweeps, fair value gaps, and order blocks — the footprints of smart money.

---

## Part 1: Project Architecture

### Directory Structure

```
fractal-trader/
├── README.md
├── requirements.txt
├── setup.py
├── .env.example
│
├── core/                          # Core detection algorithms
│   ├── __init__.py
│   ├── market_structure.py        # Swing points, BOS, CHoCH
│   ├── liquidity.py               # Sweep detection, equal H/L
│   ├── imbalance.py               # FVG detection
│   └── order_blocks.py            # OB identification
│
├── risk/                          # Risk management engine
│   ├── __init__.py
│   ├── position_sizing.py         # Dynamic size calculation
│   ├── portfolio.py               # Portfolio-level controls
│   └── confidence.py              # Entry scoring system
│
├── strategies/                    # Trading strategies
│   ├── __init__.py
│   ├── base.py                    # Abstract strategy class
│   ├── liquidity_sweep.py         # Strategy 1
│   ├── fvg_fill.py                # Strategy 2
│   └── bos_orderblock.py          # Strategy 3
│
├── backtesting/                   # Research & testing
│   ├── __init__.py
│   ├── runner.py                  # vectorbt integration
│   ├── optimizer.py               # Parameter optimization
│   └── reports.py                 # Performance analysis
│
├── live/                          # Production execution
│   ├── __init__.py
│   ├── freqtrade_strategy.py      # Freqtrade IStrategy wrapper
│   └── config/
│       ├── config.json            # Freqtrade config
│       └── pairlists.json         # Trading pairs
│
├── data/                          # Data management
│   ├── __init__.py
│   ├── fetcher.py                 # CCXT data fetching
│   └── cache/                     # Local data cache
│
├── utils/                         # Shared utilities
│   ├── __init__.py
│   ├── logger.py                  # Structured logging
│   └── config.py                  # Configuration management
│
└── tests/                         # Test suite
    ├── __init__.py
    ├── test_market_structure.py
    ├── test_strategies.py
    ├── test_risk.py
    └── fixtures/
        └── sample_data.py
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Language | Python 3.11+ | Core development |
| Backtesting | vectorbt | Fast vectorized backtesting (100x speed) |
| Live Trading | freqtrade | Production execution, exchange connectivity |
| Data | CCXT + pandas | Multi-exchange data fetching |
| Indicators | pandas + numpy | Custom SMC calculations (no ta-lib dependency for core) |
| Testing | pytest | Unit and integration tests |
| Visualization | plotly | Interactive charts |

### Dependencies (requirements.txt)

```
# Core
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0

# Backtesting
vectorbt>=0.26.0

# Live Trading
freqtrade>=2024.1
ccxt>=4.0.0

# Visualization
plotly>=5.17.0
matplotlib>=3.8.0

# Development
pytest>=7.4.3
pytest-cov>=4.1.0
python-dotenv>=1.0.0
loguru>=0.7.0

# Optional Performance
numba>=0.58.0
bottleneck>=1.3.7
```

---

## Part 2: Core Detection Algorithms

### 2.1 Market Structure (`core/market_structure.py`)

Market structure is the foundation of SMC trading. We need to detect:

**Swing Points:**
- Swing High: Bar where high is higher than N bars on both sides
- Swing Low: Bar where low is lower than N bars on both sides
- Typical N = 3-5 for intraday, 5-10 for higher timeframes

```python
def find_swing_points(high: pd.Series, low: pd.Series, n: int = 5) -> tuple[pd.Series, pd.Series]:
    """
    Identify swing highs and swing lows.
    
    Returns:
        swing_highs: Series with swing high prices (NaN elsewhere)
        swing_lows: Series with swing low prices (NaN elsewhere)
    """
    # Swing high: high[i] > high[i-n:i] and high[i] > high[i+1:i+n+1]
    # Swing low: low[i] < low[i-n:i] and low[i] < low[i+1:i+n+1]
    pass
```

**Break of Structure (BOS):**
- Bullish BOS: Price breaks above previous swing high (trend continuation)
- Bearish BOS: Price breaks below previous swing low (trend continuation)

**Change of Character (CHoCH):**
- Bullish CHoCH: In downtrend, price breaks above previous swing high (reversal signal)
- Bearish CHoCH: In uptrend, price breaks below previous swing low (reversal signal)

```python
def detect_structure_breaks(
    close: pd.Series,
    swing_highs: pd.Series,
    swing_lows: pd.Series
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Detect BOS and CHoCH events.
    
    Returns:
        bos_bullish: Boolean series for bullish BOS
        bos_bearish: Boolean series for bearish BOS  
        choch: Boolean series for change of character
    """
    pass
```

**Trend Determination:**
- Uptrend: Higher highs AND higher lows
- Downtrend: Lower highs AND lower lows
- Ranging: Mixed structure

```python
def determine_trend(swing_highs: pd.Series, swing_lows: pd.Series) -> pd.Series:
    """
    Determine market trend based on swing point sequence.
    
    Returns:
        Series with values: 1 (uptrend), -1 (downtrend), 0 (ranging)
    """
    pass
```

### 2.2 Liquidity Detection (`core/liquidity.py`)

**Equal Highs/Lows (EQH/EQL):**
- Detect areas where price made similar highs/lows (within tolerance)
- These are liquidity pools — stop losses accumulate here

```python
def find_equal_levels(
    highs: pd.Series, 
    lows: pd.Series,
    tolerance: float = 0.001  # 0.1% price tolerance
) -> tuple[pd.Series, pd.Series]:
    """
    Find equal highs and equal lows (liquidity pools).
    
    Returns:
        equal_highs: Price levels where multiple swing highs cluster
        equal_lows: Price levels where multiple swing lows cluster
    """
    pass
```

**Liquidity Sweep Detection:**
- Price breaks beyond a liquidity level (EQH/EQL or swing point)
- Then reverses back within N bars
- This is the "liquidity candle" pattern — institutional stop hunt

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
    1. Price exceeds liquidity level (break)
    2. Price reverses back within reversal_bars
    3. Close is back inside the level
    
    Returns:
        Boolean series marking sweep completion bars
    """
    pass
```

### 2.3 Imbalance Detection (`core/imbalance.py`)

**Fair Value Gap (FVG):**
- Bullish FVG: Gap between candle 1 high and candle 3 low (3-candle pattern)
- Bearish FVG: Gap between candle 1 low and candle 3 high
- Represents aggressive institutional buying/selling

```python
def find_fair_value_gaps(
    high: pd.Series,
    low: pd.Series,
    min_gap_percent: float = 0.001  # Minimum 0.1% gap
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identify Fair Value Gaps (imbalances).
    
    Returns:
        bullish_fvg: DataFrame with columns [start_idx, gap_high, gap_low, filled]
        bearish_fvg: DataFrame with columns [start_idx, gap_high, gap_low, filled]
    """
    pass

def check_fvg_fill(
    high: pd.Series,
    low: pd.Series,
    fvg_zones: pd.DataFrame
) -> pd.Series:
    """
    Check if price has returned to fill FVG zones.
    
    Returns:
        Boolean series marking bars where price enters unfilled FVG
    """
    pass
```

### 2.4 Order Block Detection (`core/order_blocks.py`)

**Order Block (OB):**
- Bullish OB: Last down candle before bullish impulse move
- Bearish OB: Last up candle before bearish impulse move
- Represents institutional accumulation/distribution zone

```python
def find_order_blocks(
    open: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    min_impulse_percent: float = 0.01  # Minimum 1% impulse move
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identify Order Blocks.
    
    Returns:
        bullish_ob: DataFrame with columns [idx, ob_high, ob_low, invalidated]
        bearish_ob: DataFrame with columns [idx, ob_high, ob_low, invalidated]
    """
    pass

def check_ob_retest(
    high: pd.Series,
    low: pd.Series,
    order_blocks: pd.DataFrame
) -> pd.Series:
    """
    Check if price is retesting a valid order block.
    
    Returns:
        Boolean series marking bars where price enters valid OB zone
    """
    pass
```

---

## Part 3: Risk Management System

### 3.1 Confidence Scoring (`risk/confidence.py`)

Every trade setup receives a confidence score (0-100) that determines position size.

```python
@dataclass
class ConfidenceFactors:
    """Factors that determine entry confidence."""
    
    # Timeframe alignment (0-30 points)
    htf_trend_aligned: bool = False      # +15 if higher TF confirms direction
    htf_structure_clean: bool = False    # +15 if HTF structure is clear
    
    # Pattern strength (0-30 points)
    pattern_clean: bool = False          # +10 if pattern is textbook
    multiple_confluences: int = 0        # +5 per additional confluence (max 20)
    
    # Volume confirmation (0-20 points)  
    volume_spike: bool = False           # +10 if volume confirms
    volume_divergence: bool = False      # +10 if volume divergence present
    
    # Market regime (0-20 points)
    trending_market: bool = False        # +10 if clear trend
    low_volatility: bool = False         # +10 if ATR is manageable
    
    def calculate_score(self) -> int:
        """Calculate total confidence score."""
        score = 0
        
        # Timeframe alignment
        if self.htf_trend_aligned:
            score += 15
        if self.htf_structure_clean:
            score += 15
            
        # Pattern strength
        if self.pattern_clean:
            score += 10
        score += min(self.multiple_confluences * 5, 20)
        
        # Volume
        if self.volume_spike:
            score += 10
        if self.volume_divergence:
            score += 10
            
        # Market regime
        if self.trending_market:
            score += 10
        if self.low_volatility:
            score += 10
            
        return min(score, 100)
```

### 3.2 Position Sizing (`risk/position_sizing.py`)

```python
@dataclass
class RiskParameters:
    """Global risk parameters."""
    
    base_risk_percent: float = 0.02      # 2% base risk per trade
    max_position_percent: float = 0.05   # 5% max single position
    min_confidence: int = 40             # Minimum confidence to take trade
    
    # Volatility adjustment
    atr_period: int = 14
    atr_baseline_multiplier: float = 1.0  # Size multiplier at baseline ATR
    
    # Win/loss adjustments
    consecutive_wins_reduce: int = 3      # Reduce size after N wins
    consecutive_losses_reduce: int = 2    # Reduce size after N losses
    win_reduction_factor: float = 0.8     # Multiply size by this after win streak
    loss_reduction_factor: float = 0.7    # Multiply size by this after loss streak


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
    """
    Calculate position size based on risk parameters.
    
    Formula:
        risk_amount = portfolio_value × base_risk% × (confidence/100)
        volatility_adj = baseline_atr / current_atr  # Reduce in high vol
        streak_adj = adjustment based on win/loss streaks
        
        risk_per_unit = |entry_price - stop_loss_price|
        position_size = (risk_amount × volatility_adj × streak_adj) / risk_per_unit
        
        Final size capped at max_position_percent of portfolio
    
    Returns:
        Position size in base currency units
    """
    # Skip if confidence too low
    if confidence_score < params.min_confidence:
        return 0.0
    
    # Base risk calculation
    confidence_factor = confidence_score / 100
    risk_amount = portfolio_value * params.base_risk_percent * confidence_factor
    
    # Volatility adjustment (reduce size in high volatility)
    if current_atr > 0:
        volatility_adj = min(baseline_atr / current_atr, 1.5)  # Cap at 1.5x
        volatility_adj = max(volatility_adj, 0.5)  # Floor at 0.5x
    else:
        volatility_adj = 1.0
    
    # Streak adjustment
    streak_adj = 1.0
    if consecutive_wins >= params.consecutive_wins_reduce:
        streak_adj = params.win_reduction_factor
    elif consecutive_losses >= params.consecutive_losses_reduce:
        streak_adj = params.loss_reduction_factor
    
    # Calculate position size
    risk_per_unit = abs(entry_price - stop_loss_price)
    if risk_per_unit == 0:
        return 0.0
    
    adjusted_risk = risk_amount * volatility_adj * streak_adj
    position_size = adjusted_risk / risk_per_unit
    
    # Apply maximum position cap
    max_position = (portfolio_value * params.max_position_percent) / entry_price
    position_size = min(position_size, max_position)
    
    return position_size
```

### 3.3 Portfolio Controls (`risk/portfolio.py`)

```python
@dataclass 
class PortfolioLimits:
    """Portfolio-level risk limits."""
    
    max_open_positions: int = 5
    max_correlated_exposure: float = 0.15  # 15% max in correlated assets
    daily_loss_limit: float = 0.03         # 3% daily loss = stop trading
    weekly_loss_limit: float = 0.07        # 7% weekly = reduce size 50%
    max_drawdown: float = 0.15             # 15% = full stop, manual review
    
    # Correlation groups (positions in same group are "correlated")
    correlation_groups: dict = field(default_factory=lambda: {
        'btc_ecosystem': ['BTC/USDT', 'BTC/USDC'],
        'eth_ecosystem': ['ETH/USDT', 'ETH/USDC'],
        'alt_large': ['BNB/USDT', 'SOL/USDT', 'XRP/USDT'],
        'alt_mid': ['AVAX/USDT', 'DOGE/USDT', 'ADA/USDT'],
    })


class PortfolioManager:
    """Manage portfolio-level risk."""
    
    def __init__(self, limits: PortfolioLimits, initial_balance: float):
        self.limits = limits
        self.initial_balance = initial_balance
        self.peak_balance = initial_balance
        self.daily_start_balance = initial_balance
        self.weekly_start_balance = initial_balance
        
        self.open_positions: dict[str, Position] = {}
        self.trade_history: list[Trade] = []
        
    def can_open_position(self, symbol: str, position_value: float) -> tuple[bool, str]:
        """
        Check if new position is allowed.
        
        Returns:
            (allowed: bool, reason: str)
        """
        # Check max positions
        if len(self.open_positions) >= self.limits.max_open_positions:
            return False, f"Max positions ({self.limits.max_open_positions}) reached"
        
        # Check correlated exposure
        correlated_exposure = self._get_correlated_exposure(symbol)
        if correlated_exposure + position_value > self.current_balance * self.limits.max_correlated_exposure:
            return False, f"Correlated exposure would exceed {self.limits.max_correlated_exposure:.0%}"
        
        # Check daily loss limit
        daily_pnl = self._get_daily_pnl()
        if daily_pnl < -self.limits.daily_loss_limit * self.daily_start_balance:
            return False, f"Daily loss limit ({self.limits.daily_loss_limit:.0%}) reached"
        
        # Check drawdown
        current_dd = (self.peak_balance - self.current_balance) / self.peak_balance
        if current_dd > self.limits.max_drawdown:
            return False, f"Max drawdown ({self.limits.max_drawdown:.0%}) exceeded"
        
        return True, "OK"
    
    def get_size_multiplier(self) -> float:
        """
        Get position size multiplier based on portfolio state.
        
        Returns:
            Multiplier (0.5-1.0) to apply to calculated position size
        """
        # Check weekly loss
        weekly_pnl = self._get_weekly_pnl()
        if weekly_pnl < -self.limits.weekly_loss_limit * self.weekly_start_balance:
            return 0.5  # Reduce all positions by 50%
        
        return 1.0
```

---

## Part 4: Trading Strategies

### 4.1 Base Strategy Class (`strategies/base.py`)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import pandas as pd

@dataclass
class Signal:
    """Trading signal with all necessary information."""
    
    timestamp: pd.Timestamp
    direction: int  # 1 = long, -1 = short
    entry_price: float
    stop_loss: float
    take_profit: Optional[float]
    confidence: int  # 0-100
    strategy_name: str
    metadata: dict  # Strategy-specific data


class BaseStrategy(ABC):
    """Abstract base class for all strategies."""
    
    def __init__(self, name: str, params: dict = None):
        self.name = name
        self.params = params or {}
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
        """
        Generate trading signals from OHLCV data.
        
        Args:
            data: DataFrame with columns [open, high, low, close, volume]
                  Index should be DatetimeIndex
        
        Returns:
            List of Signal objects
        """
        pass
    
    @abstractmethod
    def calculate_confidence(self, data: pd.DataFrame, signal_idx: int) -> int:
        """
        Calculate confidence score for a specific signal.
        
        Args:
            data: Full OHLCV DataFrame
            signal_idx: Index of the signal bar
            
        Returns:
            Confidence score 0-100
        """
        pass
    
    def backtest(
        self, 
        data: pd.DataFrame,
        initial_cash: float = 10000,
        risk_params: RiskParameters = None
    ) -> BacktestResult:
        """
        Run backtest using vectorbt.
        
        Returns:
            BacktestResult with performance metrics
        """
        # Implementation uses vectorbt.Portfolio.from_signals()
        pass
```

### 4.2 Liquidity Sweep Reversal (`strategies/liquidity_sweep.py`)

**Logic:**
1. Identify liquidity levels (swing highs/lows, equal levels)
2. Wait for price to sweep the level (break beyond it)
3. Enter on reversal candle (close back inside)
4. Stop loss: Beyond the sweep wick
5. Take profit: Previous structure level or 2:1 RR

```python
class LiquiditySweepStrategy(BaseStrategy):
    """
    Trade reversals after liquidity sweeps.
    
    This is the "liquidity candle" pattern - institutional stop hunts
    followed by reversals.
    """
    
    DEFAULT_PARAMS = {
        'swing_period': 5,           # Bars for swing detection
        'min_sweep_percent': 0.001,  # Minimum sweep beyond level (0.1%)
        'max_reversal_bars': 3,      # Must reverse within N bars
        'min_rr_ratio': 1.5,         # Minimum risk:reward
    }
    
    def __init__(self, params: dict = None):
        merged_params = {**self.DEFAULT_PARAMS, **(params or {})}
        super().__init__("liquidity_sweep", merged_params)
        
    def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
        signals = []
        
        # 1. Find swing points
        swing_highs, swing_lows = find_swing_points(
            data['high'], data['low'], 
            n=self.params['swing_period']
        )
        
        # 2. Find equal levels (additional liquidity)
        equal_highs, equal_lows = find_equal_levels(
            swing_highs.dropna(), 
            swing_lows.dropna()
        )
        
        # 3. Detect sweeps
        # Combine swing points and equal levels as liquidity
        bullish_sweeps = detect_liquidity_sweep(
            data['high'], data['low'], data['close'],
            liquidity_levels=equal_lows,  # Sweep below lows = bullish
            reversal_bars=self.params['max_reversal_bars']
        )
        
        bearish_sweeps = detect_liquidity_sweep(
            data['high'], data['low'], data['close'],
            liquidity_levels=equal_highs,  # Sweep above highs = bearish
            reversal_bars=self.params['max_reversal_bars']
        )
        
        # 4. Generate signals
        for idx in data.index[bullish_sweeps]:
            signal = self._create_long_signal(data, idx, swing_lows)
            if signal and self._validate_rr(signal):
                signals.append(signal)
                
        for idx in data.index[bearish_sweeps]:
            signal = self._create_short_signal(data, idx, swing_highs)
            if signal and self._validate_rr(signal):
                signals.append(signal)
        
        return signals
    
    def _create_long_signal(self, data, idx, swing_lows) -> Optional[Signal]:
        """Create long signal after bullish liquidity sweep."""
        entry = data.loc[idx, 'close']
        
        # Stop loss: Below the sweep low (the wick)
        sweep_low = data.loc[idx, 'low']
        stop_loss = sweep_low * 0.999  # Small buffer
        
        # Take profit: Previous swing high
        prev_swing_high = swing_highs[swing_highs.index < idx].iloc[-1] if len(swing_highs[swing_highs.index < idx]) > 0 else None
        take_profit = prev_swing_high if prev_swing_high else entry * 1.02
        
        confidence = self.calculate_confidence(data, idx)
        
        return Signal(
            timestamp=idx,
            direction=1,
            entry_price=entry,
            stop_loss=stop_loss,
            take_profit=take_profit,
            confidence=confidence,
            strategy_name=self.name,
            metadata={'sweep_low': sweep_low}
        )
    
    def calculate_confidence(self, data: pd.DataFrame, signal_idx: int) -> int:
        """Calculate confidence based on multiple factors."""
        factors = ConfidenceFactors()
        
        # Check trend alignment (simplified - would use HTF in production)
        recent_data = data.loc[:signal_idx].tail(50)
        trend = determine_trend(
            find_swing_points(recent_data['high'], recent_data['low'])[0],
            find_swing_points(recent_data['high'], recent_data['low'])[1]
        )
        factors.htf_trend_aligned = trend.iloc[-1] == 1  # For long signal
        
        # Pattern strength
        factors.pattern_clean = True  # Already filtered by sweep detection
        
        # Volume confirmation
        avg_volume = data['volume'].rolling(20).mean()
        factors.volume_spike = data.loc[signal_idx, 'volume'] > avg_volume.loc[signal_idx] * 1.5
        
        # Market regime (ATR-based)
        atr = self._calculate_atr(data, 14)
        avg_atr = atr.rolling(50).mean()
        factors.low_volatility = atr.loc[signal_idx] < avg_atr.loc[signal_idx] * 1.5
        
        return factors.calculate_score()
```

### 4.3 FVG Fill Strategy (`strategies/fvg_fill.py`)

**Logic:**
1. Identify Fair Value Gaps (3-candle imbalances)
2. Wait for price to return to the gap zone
3. Enter when price enters the gap
4. Stop loss: Beyond the gap zone
5. Take profit: Origin of the move that created FVG

```python
class FVGFillStrategy(BaseStrategy):
    """
    Trade returns to Fair Value Gaps (imbalances).
    
    FVGs represent aggressive institutional moves. Price often
    returns to "fill" these gaps before continuing.
    """
    
    DEFAULT_PARAMS = {
        'min_gap_percent': 0.002,    # Minimum 0.2% gap size
        'max_gap_age_bars': 50,      # Ignore gaps older than 50 bars
        'partial_fill_percent': 0.5, # Enter when gap 50% filled
        'min_rr_ratio': 1.5,
    }
    
    def __init__(self, params: dict = None):
        merged_params = {**self.DEFAULT_PARAMS, **(params or {})}
        super().__init__("fvg_fill", merged_params)
    
    def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
        signals = []
        
        # Find FVGs
        bullish_fvg, bearish_fvg = find_fair_value_gaps(
            data['high'], data['low'],
            min_gap_percent=self.params['min_gap_percent']
        )
        
        # Track active (unfilled) FVGs
        active_bullish = []
        active_bearish = []
        
        for idx in data.index:
            # Add new FVGs
            if idx in bullish_fvg.index:
                active_bullish.append(bullish_fvg.loc[idx])
            if idx in bearish_fvg.index:
                active_bearish.append(bearish_fvg.loc[idx])
            
            # Remove old FVGs
            active_bullish = [f for f in active_bullish 
                           if (idx - f['start_idx']).total_seconds() / 3600 < self.params['max_gap_age_bars']]
            active_bearish = [f for f in active_bearish
                           if (idx - f['start_idx']).total_seconds() / 3600 < self.params['max_gap_age_bars']]
            
            # Check for fills
            current_low = data.loc[idx, 'low']
            current_high = data.loc[idx, 'high']
            
            for fvg in active_bullish:
                if current_low <= fvg['gap_high']:  # Price entered bullish FVG
                    signal = self._create_long_signal(data, idx, fvg)
                    if signal:
                        signals.append(signal)
                        active_bullish.remove(fvg)
                        
            for fvg in active_bearish:
                if current_high >= fvg['gap_low']:  # Price entered bearish FVG
                    signal = self._create_short_signal(data, idx, fvg)
                    if signal:
                        signals.append(signal)
                        active_bearish.remove(fvg)
        
        return signals
```

### 4.4 Break of Structure + Order Block (`strategies/bos_orderblock.py`)

**Logic:**
1. Detect Break of Structure (BOS) confirming trend
2. Identify Order Block before the BOS impulse
3. Wait for price to retest the Order Block
4. Enter on retest with trend direction
5. Stop loss: Beyond the Order Block
6. Take profit: Next structure level or measured move

```python
class BOSOrderBlockStrategy(BaseStrategy):
    """
    Trend following with Break of Structure and Order Block entries.
    
    Most conservative of the three strategies - trades with
    confirmed trend on pullbacks to institutional zones.
    """
    
    DEFAULT_PARAMS = {
        'swing_period': 5,
        'min_impulse_percent': 0.01,  # 1% minimum impulse for OB
        'ob_validity_bars': 30,        # OB valid for 30 bars
        'min_rr_ratio': 2.0,           # Higher RR for trend following
    }
    
    def __init__(self, params: dict = None):
        merged_params = {**self.DEFAULT_PARAMS, **(params or {})}
        super().__init__("bos_orderblock", merged_params)
    
    def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
        signals = []
        
        # Find structure
        swing_highs, swing_lows = find_swing_points(
            data['high'], data['low'],
            n=self.params['swing_period']
        )
        
        # Detect BOS
        bos_bullish, bos_bearish, choch = detect_structure_breaks(
            data['close'], swing_highs, swing_lows
        )
        
        # Find order blocks
        bullish_ob, bearish_ob = find_order_blocks(
            data['open'], data['high'], data['low'], data['close'],
            min_impulse_percent=self.params['min_impulse_percent']
        )
        
        # Track active setups
        active_long_setups = []  # (BOS timestamp, OB zone)
        active_short_setups = []
        
        for idx in data.index:
            # New BOS creates setup
            if bos_bullish.loc[idx]:
                # Find the order block that preceded this BOS
                recent_ob = self._find_recent_ob(bullish_ob, idx)
                if recent_ob is not None:
                    active_long_setups.append((idx, recent_ob))
                    
            if bos_bearish.loc[idx]:
                recent_ob = self._find_recent_ob(bearish_ob, idx)
                if recent_ob is not None:
                    active_short_setups.append((idx, recent_ob))
            
            # Check for OB retests
            for bos_time, ob in active_long_setups[:]:  # Copy to allow removal
                if self._is_ob_retest(data, idx, ob, direction=1):
                    signal = self._create_long_signal(data, idx, ob, swing_highs)
                    if signal:
                        signals.append(signal)
                    active_long_setups.remove((bos_time, ob))
                elif self._is_ob_invalidated(data, idx, ob, direction=1):
                    active_long_setups.remove((bos_time, ob))
                    
            for bos_time, ob in active_short_setups[:]:
                if self._is_ob_retest(data, idx, ob, direction=-1):
                    signal = self._create_short_signal(data, idx, ob, swing_lows)
                    if signal:
                        signals.append(signal)
                    active_short_setups.remove((bos_time, ob))
                elif self._is_ob_invalidated(data, idx, ob, direction=-1):
                    active_short_setups.remove((bos_time, ob))
        
        return signals
```

---

## Part 5: Backtesting Framework

### 5.1 vectorbt Runner (`backtesting/runner.py`)

```python
import vectorbt as vbt
import pandas as pd
from dataclasses import dataclass
from typing import Optional

@dataclass
class BacktestResult:
    """Results from a backtest run."""
    
    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_duration: pd.Timedelta
    
    # Detailed data
    equity_curve: pd.Series
    trades: pd.DataFrame
    signals: list[Signal]


class BacktestRunner:
    """Run backtests using vectorbt."""
    
    def __init__(
        self,
        initial_cash: float = 10000,
        fees: float = 0.001,      # 0.1% per trade
        slippage: float = 0.0005  # 0.05% slippage
    ):
        self.initial_cash = initial_cash
        self.fees = fees
        self.slippage = slippage
        
    def run(
        self,
        data: pd.DataFrame,
        strategy: BaseStrategy,
        risk_params: RiskParameters = None
    ) -> BacktestResult:
        """
        Run backtest for a strategy.
        
        Args:
            data: OHLCV DataFrame
            strategy: Strategy instance
            risk_params: Risk parameters (uses defaults if None)
            
        Returns:
            BacktestResult with performance metrics
        """
        risk_params = risk_params or RiskParameters()
        
        # Generate signals
        signals = strategy.generate_signals(data)
        
        if not signals:
            return self._empty_result()
        
        # Convert to vectorbt format
        entries, exits, sizes = self._signals_to_arrays(
            data, signals, risk_params
        )
        
        # Run vectorbt backtest
        portfolio = vbt.Portfolio.from_signals(
            close=data['close'],
            entries=entries,
            exits=exits,
            size=sizes,
            size_type='value',
            init_cash=self.initial_cash,
            fees=self.fees,
            slippage=self.slippage,
            freq='1h'  # Adjust based on data timeframe
        )
        
        return self._extract_results(portfolio, signals)
    
    def optimize(
        self,
        data: pd.DataFrame,
        strategy_class: type,
        param_grid: dict,
        metric: str = 'sharpe_ratio'
    ) -> pd.DataFrame:
        """
        Optimize strategy parameters.
        
        Args:
            data: OHLCV DataFrame
            strategy_class: Strategy class to optimize
            param_grid: Dict of param_name -> list of values
            metric: Metric to optimize ('sharpe_ratio', 'total_return', etc.)
            
        Returns:
            DataFrame with results for all parameter combinations
        """
        from itertools import product
        
        results = []
        
        # Generate all combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        for values in product(*param_values):
            params = dict(zip(param_names, values))
            
            strategy = strategy_class(params)
            result = self.run(data, strategy)
            
            results.append({
                **params,
                'total_return': result.total_return,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown,
                'win_rate': result.win_rate,
                'total_trades': result.total_trades
            })
        
        df = pd.DataFrame(results)
        return df.sort_values(metric, ascending=False)
```

---

## Part 6: Live Trading Integration

### 6.1 Freqtrade Strategy (`live/freqtrade_strategy.py`)

```python
from freqtrade.strategy import IStrategy, merge_informative_pair
from freqtrade.persistence import Trade
import pandas as pd
from typing import Optional
from datetime import datetime

# Import our strategy components
from core.market_structure import find_swing_points, detect_structure_breaks
from core.liquidity import detect_liquidity_sweep
from strategies.liquidity_sweep import LiquiditySweepStrategy
from risk.position_sizing import calculate_position_size, RiskParameters


class FractalTraderStrategy(IStrategy):
    """
    Freqtrade wrapper for Fractal Trader strategies.
    
    This bridges our backtested strategies to live execution.
    """
    
    # Freqtrade settings
    INTERFACE_VERSION = 3
    
    minimal_roi = {
        "0": 0.1,    # 10% ROI target
        "30": 0.05,  # 5% after 30 minutes
        "60": 0.02,  # 2% after 60 minutes
    }
    
    stoploss = -0.05  # 5% stop loss (fallback - strategy calculates dynamic SL)
    
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    
    timeframe = '1h'
    
    # Custom parameters
    swing_period = 5
    active_strategy = 'liquidity_sweep'  # or 'fvg_fill', 'bos_orderblock'
    
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        
        # Initialize our strategy
        self.smc_strategy = LiquiditySweepStrategy({
            'swing_period': self.swing_period
        })
        
        self.risk_params = RiskParameters()
        
    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """Calculate indicators needed for strategy."""
        
        # Swing points
        swing_highs, swing_lows = find_swing_points(
            dataframe['high'], 
            dataframe['low'],
            n=self.swing_period
        )
        dataframe['swing_high'] = swing_highs
        dataframe['swing_low'] = swing_lows
        
        # Structure breaks
        bos_bull, bos_bear, choch = detect_structure_breaks(
            dataframe['close'],
            swing_highs,
            swing_lows
        )
        dataframe['bos_bullish'] = bos_bull
        dataframe['bos_bearish'] = bos_bear
        
        # Liquidity sweeps
        dataframe['liq_sweep_bull'] = detect_liquidity_sweep(
            dataframe['high'],
            dataframe['low'],
            dataframe['close'],
            swing_lows
        )
        dataframe['liq_sweep_bear'] = detect_liquidity_sweep(
            dataframe['high'],
            dataframe['low'],
            dataframe['close'],
            swing_highs
        )
        
        # ATR for volatility adjustment
        dataframe['atr'] = self._calculate_atr(dataframe, 14)
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """Define entry conditions."""
        
        # Long entries
        dataframe.loc[
            (dataframe['liq_sweep_bull'] == True),
            'enter_long'
        ] = 1
        
        # Short entries
        dataframe.loc[
            (dataframe['liq_sweep_bear'] == True),
            'enter_short'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """Define exit conditions."""
        
        # Exit long on bearish structure break
        dataframe.loc[
            (dataframe['bos_bearish'] == True),
            'exit_long'
        ] = 1
        
        # Exit short on bullish structure break
        dataframe.loc[
            (dataframe['bos_bullish'] == True),
            'exit_short'
        ] = 1
        
        return dataframe
    
    def custom_stake_amount(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_stake: float,
        min_stake: Optional[float],
        max_stake: float,
        leverage: float,
        entry_tag: Optional[str],
        side: str,
        **kwargs
    ) -> float:
        """Calculate position size using our risk management."""
        
        # Get wallet balance
        wallet_balance = self.wallets.get_total_stake_amount()
        
        # Get current ATR (from last populated candle)
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        current_atr = dataframe['atr'].iloc[-1]
        baseline_atr = dataframe['atr'].rolling(50).mean().iloc[-1]
        
        # Calculate stop loss distance (simplified - use swing low for longs)
        if side == 'long':
            recent_swing_low = dataframe['swing_low'].dropna().iloc[-1]
            stop_loss = recent_swing_low * 0.999
        else:
            recent_swing_high = dataframe['swing_high'].dropna().iloc[-1]
            stop_loss = recent_swing_high * 1.001
        
        # Get trade history for streak calculation
        trades = Trade.get_trades([Trade.is_open.is_(False)]).all()
        consecutive_wins, consecutive_losses = self._calculate_streaks(trades)
        
        # Calculate confidence (simplified - would use full factors in production)
        confidence = 60  # Base confidence for validated setup
        
        # Calculate position size
        position_size = calculate_position_size(
            portfolio_value=wallet_balance,
            entry_price=current_rate,
            stop_loss_price=stop_loss,
            confidence_score=confidence,
            current_atr=current_atr,
            baseline_atr=baseline_atr,
            consecutive_wins=consecutive_wins,
            consecutive_losses=consecutive_losses,
            params=self.risk_params
        )
        
        # Convert to stake
        stake = position_size * current_rate
        
        # Apply freqtrade limits
        stake = max(stake, min_stake or 0)
        stake = min(stake, max_stake)
        
        return stake
```

### 6.2 Freqtrade Config (`live/config/config.json`)

```json
{
    "trading_mode": "futures",
    "margin_mode": "isolated",
    
    "max_open_trades": 5,
    "stake_currency": "USDT",
    "stake_amount": "unlimited",
    
    "tradable_balance_ratio": 0.95,
    "fiat_display_currency": "USD",
    
    "dry_run": true,
    "dry_run_wallet": 1000,
    
    "exchange": {
        "name": "binance",
        "key": "",
        "secret": "",
        "ccxt_config": {},
        "ccxt_async_config": {}
    },
    
    "pairlists": [
        {
            "method": "StaticPairList",
            "pairs": [
                "BTC/USDT:USDT",
                "ETH/USDT:USDT",
                "SOL/USDT:USDT"
            ]
        }
    ],
    
    "entry_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1
    },
    
    "exit_pricing": {
        "price_side": "same",
        "use_order_book": true,
        "order_book_top": 1
    },
    
    "telegram": {
        "enabled": false,
        "token": "",
        "chat_id": ""
    },
    
    "api_server": {
        "enabled": true,
        "listen_ip_address": "127.0.0.1",
        "listen_port": 8080,
        "verbosity": "info"
    }
}
```

---

## Part 7: Testing Requirements

### 7.1 Test Structure

```python
# tests/test_market_structure.py

import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_ohlcv():
    """Generate sample OHLCV data with known structure."""
    # Create data with clear swing points
    dates = pd.date_range('2024-01-01', periods=100, freq='1h')
    
    # Uptrend with pullbacks
    close = [100]
    for i in range(1, 100):
        if i % 10 < 5:  # Rally phase
            close.append(close[-1] * 1.005)
        else:  # Pullback phase
            close.append(close[-1] * 0.997)
    
    close = np.array(close)
    
    return pd.DataFrame({
        'open': close * 0.999,
        'high': close * 1.005,
        'low': close * 0.995,
        'close': close,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)


class TestSwingPoints:
    """Test swing point detection."""
    
    def test_finds_swing_highs(self, sample_ohlcv):
        from core.market_structure import find_swing_points
        
        swing_highs, swing_lows = find_swing_points(
            sample_ohlcv['high'],
            sample_ohlcv['low'],
            n=3
        )
        
        # Should find multiple swing highs in our data
        assert swing_highs.dropna().count() >= 5
        
    def test_swing_high_is_local_maximum(self, sample_ohlcv):
        from core.market_structure import find_swing_points
        
        swing_highs, _ = find_swing_points(
            sample_ohlcv['high'],
            sample_ohlcv['low'],
            n=3
        )
        
        for idx in swing_highs.dropna().index:
            # Swing high should be higher than surrounding bars
            i = sample_ohlcv.index.get_loc(idx)
            if i >= 3 and i < len(sample_ohlcv) - 3:
                assert sample_ohlcv['high'].iloc[i] >= sample_ohlcv['high'].iloc[i-3:i].max()
                assert sample_ohlcv['high'].iloc[i] >= sample_ohlcv['high'].iloc[i+1:i+4].max()


class TestLiquiditySweep:
    """Test liquidity sweep detection."""
    
    def test_detects_sweep_and_reversal(self):
        from core.liquidity import detect_liquidity_sweep
        
        # Create data with clear sweep pattern
        dates = pd.date_range('2024-01-01', periods=10, freq='1h')
        
        # Price dips below support then recovers
        data = pd.DataFrame({
            'high': [100, 100, 100, 100, 99, 102, 103, 104, 105, 106],
            'low':  [98, 98, 98, 98, 95, 99, 101, 102, 103, 104],
            'close': [99, 99, 99, 99, 96, 101, 102, 103, 104, 105],
        }, index=dates)
        
        liquidity_level = pd.Series([98] * 10, index=dates)  # Support at 98
        
        sweeps = detect_liquidity_sweep(
            data['high'], data['low'], data['close'],
            liquidity_levels=liquidity_level,
            reversal_bars=2
        )
        
        # Should detect sweep at bar 5 (price went to 95, below 98)
        assert sweeps.sum() >= 1


class TestRiskManagement:
    """Test risk management calculations."""
    
    def test_position_size_respects_max(self):
        from risk.position_sizing import calculate_position_size, RiskParameters
        
        params = RiskParameters(
            base_risk_percent=0.02,
            max_position_percent=0.05
        )
        
        size = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,  # 5% stop
            confidence_score=100,  # Max confidence
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params
        )
        
        # Position value should not exceed 5% of portfolio
        position_value = size * 100
        assert position_value <= 10000 * 0.05
    
    def test_low_confidence_reduces_size(self):
        from risk.position_sizing import calculate_position_size, RiskParameters
        
        params = RiskParameters()
        
        high_conf_size = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=98,
            confidence_score=80,
            current_atr=2,
            baseline_atr=2,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params
        )
        
        low_conf_size = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=98,
            confidence_score=40,
            current_atr=2,
            baseline_atr=2,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params
        )
        
        assert low_conf_size < high_conf_size
```

---

## Part 8: Development Workflow

### 8.1 Sprint 1: Foundation (Week 1-2)

**Goals:**
- [ ] Project setup with proper structure
- [ ] Core market structure detection (swing points, BOS)
- [ ] Basic liquidity sweep detection
- [ ] Unit tests for core components

**Key Files to Create:**
1. `core/market_structure.py` - Complete implementation
2. `core/liquidity.py` - Basic implementation
3. `tests/test_market_structure.py` - Tests
4. `requirements.txt` - Dependencies
5. `setup.py` - Package setup

### 8.2 Sprint 2: Strategies (Week 3-4)

**Goals:**
- [ ] Complete all 3 strategies
- [ ] Backtesting framework with vectorbt
- [ ] Parameter optimization
- [ ] Risk management integration

**Key Files:**
1. `strategies/liquidity_sweep.py`
2. `strategies/fvg_fill.py`
3. `strategies/bos_orderblock.py`
4. `risk/position_sizing.py`
5. `backtesting/runner.py`

### 8.3 Sprint 3: Production (Week 5-6)

**Goals:**
- [ ] Freqtrade integration
- [ ] Paper trading setup
- [ ] Performance monitoring
- [ ] Documentation

**Key Files:**
1. `live/freqtrade_strategy.py`
2. `live/config/config.json`
3. `README.md` - User documentation
4. Docker configuration

---

## Part 9: Validation Criteria

### Performance Targets

| Metric | Minimum | Target |
|--------|---------|--------|
| Sharpe Ratio | > 1.0 | > 1.5 |
| Win Rate | > 45% | > 55% |
| Profit Factor | > 1.3 | > 1.8 |
| Max Drawdown | < 20% | < 15% |
| Avg Trade R:R | > 1.5 | > 2.0 |

### Code Quality

- [ ] All core functions have docstrings
- [ ] Type hints throughout
- [ ] Test coverage > 80%
- [ ] No circular imports
- [ ] Logging integrated

### Backtest Validation

- [ ] Strategy profitable on BTC/USDT (2023-2024)
- [ ] Strategy profitable on ETH/USDT (2023-2024)
- [ ] Results stable across different time periods
- [ ] No look-ahead bias in signals

---

## Part 10: Instructions for Claude Code

### Your Task

You are building the Fractal Trader system from scratch. Follow these guidelines:

1. **Start with Core:**
   - Implement `core/market_structure.py` first
   - Then `core/liquidity.py`
   - Then `core/imbalance.py` and `core/order_blocks.py`
   - Write tests as you go

2. **Build Strategies:**
   - Use the `BaseStrategy` pattern
   - Implement Liquidity Sweep first (simplest)
   - Then FVG Fill, then BOS+OB

3. **Integrate Risk Management:**
   - Position sizing should be dynamic
   - Respect portfolio limits
   - Log all risk decisions

4. **Test Thoroughly:**
   - Unit tests for each function
   - Integration tests for strategies
   - Backtest on real historical data

5. **Code Style:**
   - Use type hints everywhere
   - Follow PEP 8
   - Document complex logic
   - Keep functions small and focused

### What NOT To Do

- Don't use Pine Script or PyneCore (unnecessary complexity)
- Don't implement indicators we won't use (MACD, RSI, etc.)
- Don't over-engineer before validating basic functionality
- Don't skip tests to move faster

### Communication

After each significant milestone, provide:
1. What was completed
2. Test results
3. Any issues encountered
4. Next steps

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| BOS | Break of Structure - price breaks previous swing high/low |
| CHoCH | Change of Character - first BOS against prevailing trend |
| FVG | Fair Value Gap - price imbalance, 3-candle pattern |
| OB | Order Block - last opposite candle before impulse |
| Sweep | Price breaks level then reverses (stop hunt) |
| SMC | Smart Money Concepts - institutional trading patterns |
| HTF | Higher Time Frame - used for confluence |
| LTF | Lower Time Frame - used for entries |

---

## Appendix B: Reference Trades

### Example 1: Liquidity Sweep Long

```
Scenario:
- Price in uptrend (HH, HL pattern)
- Equal lows form at 100.00
- Price sweeps to 99.50, wick below EQL
- Reversal candle closes back above 100.00

Entry: 100.50 (confirmation close)
Stop: 99.30 (below sweep low)
Target: 102.50 (previous swing high)
R:R = 1.67
```

### Example 2: FVG Fill Short

```
Scenario:
- Bearish impulse creates FVG between 105-107
- Price rallies back into gap
- Entry when price reaches 106 (50% fill)

Entry: 106.00
Stop: 107.50 (above gap)
Target: 103.00 (origin of move)
R:R = 2.0
```

### Example 3: BOS + Order Block Long

```
Scenario:
- Downtrend reverses with CHoCH
- Bullish BOS confirms new uptrend
- Order Block identified at 98-99
- Price retests OB zone

Entry: 98.50 (OB retest)
Stop: 97.50 (below OB)
Target: 102.00 (structure target)
R:R = 3.5
```

---

**End of Context Document**

*This document contains everything needed to build the Fractal Trader system. No additional context should be required. If clarification is needed on any section, ask before proceeding.*
