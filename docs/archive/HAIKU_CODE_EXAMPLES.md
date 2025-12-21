# Code Examples & Patterns for Haiku

**Purpose:** Copy-paste ready code snippets following project conventions

---

## Table of Contents

1. [Type Hints & Docstrings](#type-hints--docstrings)
2. [Error Handling](#error-handling)
3. [DataFrame Operations](#dataframe-operations)
4. [Testing Patterns](#testing-patterns)
5. [Using Existing Core Functions](#using-existing-core-functions)
6. [Configuration Management](#configuration-management)
7. [Logging](#logging)
8. [Common Patterns](#common-patterns)

---

## Type Hints & Docstrings

### Function Template

```python
from typing import Optional, Literal
import pandas as pd


def fetch_data(
    symbol: str,
    timeframe: Literal['1m', '5m', '15m', '1h', '4h', '1d'] = '1h',
    limit: Optional[int] = None,
    since: Optional[str] = None
) -> pd.DataFrame:
    """
    Fetch OHLCV data from exchange.

    This function retrieves candlestick data and formats it
    for use with trading strategies.

    Args:
        symbol: Trading pair (e.g., 'BTC/USDT')
        timeframe: Candle timeframe (default: '1h')
        limit: Maximum number of candles to fetch
        since: Start date in ISO format or Unix timestamp

    Returns:
        DataFrame with columns ['open', 'high', 'low', 'close', 'volume']
        and DatetimeIndex (timezone-aware UTC)

    Raises:
        ValueError: If symbol format is invalid
        ConnectionError: If API request fails

    Example:
        >>> df = fetch_data('BTC/USDT', '1h', limit=100)
        >>> df.head()
                            open    high     low   close    volume
        2024-01-01 00:00:00  42000  42100  41900  42050  1234.56

    Note:
        All timestamps are in UTC timezone.
    """
    # Implementation
    pass
```

### Class Template

```python
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Config:
    """
    Configuration for data fetcher.

    Attributes:
        api_url: API endpoint URL
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    """
    api_url: str
    timeout: int = 30
    max_retries: int = 3


class BaseFetcher(ABC):
    """
    Abstract base class for data fetchers.

    All fetchers must implement this interface to ensure
    strategies work with any data source.
    """

    @abstractmethod
    def fetch_ohlcv(self, symbol: str) -> pd.DataFrame:
        """
        Fetch OHLCV data.

        Args:
            symbol: Trading pair

        Returns:
            DataFrame with standard format
        """
        pass
```

---

## Error Handling

### Pattern 1: Try-Except with Logging

```python
import logging

logger = logging.getLogger(__name__)


def fetch_with_retry(url: str, max_retries: int = 3) -> dict:
    """Fetch data with retry logic."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
            if attempt == max_retries - 1:
                raise ConnectionError(f"Failed after {max_retries} attempts")
            time.sleep(2 ** attempt)  # Exponential backoff

        except requests.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise ConnectionError(f"API request failed: {e}")

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
```

### Pattern 2: Input Validation

```python
def calculate_position_size(
    portfolio_value: float,
    entry_price: float,
    stop_loss_price: float
) -> float:
    """Calculate position size with validation."""

    # Validate inputs
    if portfolio_value <= 0:
        raise ValueError(f"Invalid portfolio_value: {portfolio_value} (must be > 0)")

    if entry_price <= 0:
        raise ValueError(f"Invalid entry_price: {entry_price} (must be > 0)")

    if stop_loss_price <= 0:
        raise ValueError(f"Invalid stop_loss_price: {stop_loss_price} (must be > 0)")

    if entry_price == stop_loss_price:
        raise ValueError("Entry price cannot equal stop loss price")

    # Calculation
    risk_per_unit = abs(entry_price - stop_loss_price)
    position_size = portfolio_value * 0.02 / risk_per_unit

    return position_size
```

### Pattern 3: Graceful Degradation

```python
def get_portfolio_value(self) -> float:
    """Get portfolio value with fallback."""
    try:
        # Try to get from API
        user_state = self.api.get_user_state()
        return float(user_state['account_value'])

    except Exception as e:
        logger.error(f"Failed to fetch portfolio value: {e}")

        # Fallback to cached value or default
        if hasattr(self, '_cached_portfolio_value'):
            logger.warning("Using cached portfolio value")
            return self._cached_portfolio_value

        logger.warning("Using default portfolio value")
        return 100000.0  # Default testnet value
```

---

## DataFrame Operations

### Pattern 1: Creating Standard OHLCV DataFrame

```python
import pandas as pd
from typing import List


def create_ohlcv_dataframe(
    timestamps: List[int],
    open_prices: List[float],
    high_prices: List[float],
    low_prices: List[float],
    close_prices: List[float],
    volumes: List[float]
) -> pd.DataFrame:
    """
    Create standard OHLCV DataFrame.

    This is the REQUIRED format for all strategies.
    """
    df = pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })

    # Convert timestamps to DatetimeIndex
    df.index = pd.to_datetime(timestamps, unit='ms', utc=True)
    df.index.name = 'timestamp'

    # Sort by time (required)
    df.sort_index(inplace=True)

    # Remove duplicates (can happen with API pagination)
    df = df[~df.index.duplicated(keep='first')]

    return df
```

### Pattern 2: Validating DataFrame Format

```python
def validate_ohlcv_dataframe(df: pd.DataFrame) -> bool:
    """
    Validate DataFrame matches required format.

    Raises:
        ValueError: If format is incorrect
    """
    # Check columns
    required_columns = ['open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_columns):
        missing = [c for c in required_columns if c not in df.columns]
        raise ValueError(f"Missing required columns: {missing}")

    # Check index type
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(
            f"Index must be DatetimeIndex, got {type(df.index).__name__}"
        )

    # Check not empty
    if df.empty:
        raise ValueError("DataFrame is empty")

    # Check data types
    for col in required_columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise ValueError(f"Column '{col}' must be numeric")

    # Check for NaN values
    if df[required_columns].isnull().any().any():
        raise ValueError("DataFrame contains NaN values")

    return True
```

### Pattern 3: Empty DataFrame (for error cases)

```python
def empty_ohlcv_dataframe() -> pd.DataFrame:
    """Return empty DataFrame with correct format."""
    df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
    df.index = pd.DatetimeIndex([], name='timestamp')
    return df
```

---

## Testing Patterns

### Pattern 1: Basic Test Structure

```python
import pytest
import pandas as pd
import numpy as np


class TestDataFetcher:
    """Tests for DataFetcher class."""

    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance for testing."""
        from data.my_fetcher import MyFetcher
        return MyFetcher()

    def test_fetch_returns_dataframe(self, fetcher):
        """Test fetch_ohlcv returns a DataFrame."""
        df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=10)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_fetch_has_correct_columns(self, fetcher):
        """Test DataFrame has required columns."""
        df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=10)

        expected_columns = ['open', 'high', 'low', 'close', 'volume']
        assert list(df.columns) == expected_columns

    def test_fetch_respects_limit(self, fetcher):
        """Test limit parameter works correctly."""
        df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=50)

        assert len(df) <= 50

    def test_invalid_symbol_raises_error(self, fetcher):
        """Test invalid symbol raises ValueError."""
        with pytest.raises(ValueError, match="Invalid symbol"):
            fetcher.fetch_ohlcv('INVALID', '1h')

    def test_dataframe_index_is_datetime(self, fetcher):
        """Test DataFrame index is DatetimeIndex."""
        df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=10)

        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.is_monotonic_increasing
```

### Pattern 2: Mocking External APIs

```python
from unittest.mock import Mock, patch, MagicMock


class TestWithMocks:
    """Tests using mocks for external dependencies."""

    @patch('data.my_fetcher.ExternalAPI')
    def test_fetch_with_mocked_api(self, mock_api_class):
        """Test fetcher with mocked API."""
        # Setup mock
        mock_api = Mock()
        mock_api_class.return_value = mock_api

        # Mock API response
        mock_api.fetch_ohlcv.return_value = [
            [1609459200000, 29000, 29100, 28900, 29050, 1234.5],
            [1609462800000, 29050, 29200, 29000, 29150, 2345.6],
        ]

        # Create fetcher (will use mocked API)
        from data.my_fetcher import MyFetcher
        fetcher = MyFetcher()

        # Test
        df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=2)

        assert len(df) == 2
        assert df['close'].iloc[0] == 29050
        assert df['close'].iloc[1] == 29150

        # Verify API was called correctly
        mock_api.fetch_ohlcv.assert_called_once_with(
            'BTC/USDT', '1h', limit=2
        )
```

### Pattern 3: Parameterized Tests

```python
@pytest.mark.parametrize('timeframe,expected_candles', [
    ('1m', 60),   # 1 hour of 1m candles
    ('5m', 12),   # 1 hour of 5m candles
    ('15m', 4),   # 1 hour of 15m candles
    ('1h', 1),    # 1 hour of 1h candles
])
def test_different_timeframes(fetcher, timeframe, expected_candles):
    """Test fetching different timeframes."""
    # Fetch 1 hour of data
    df = fetcher.fetch_ohlcv(
        'BTC/USDT',
        timeframe,
        since='2024-01-01 00:00:00',
        limit=expected_candles
    )

    assert len(df) <= expected_candles
```

### Pattern 4: Test Fixtures with Sample Data

```python
@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data for testing."""
    dates = pd.date_range('2024-01-01', periods=100, freq='1h')

    # Create realistic price movement
    np.random.seed(42)
    close = 100 * (1 + np.random.randn(100).cumsum() * 0.01)
    high = close * (1 + np.random.rand(100) * 0.01)
    low = close * (1 - np.random.rand(100) * 0.01)
    open_prices = close * (1 + np.random.randn(100) * 0.005)
    volume = np.random.randint(1000, 10000, 100)

    df = pd.DataFrame({
        'open': open_prices,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)

    return df


def test_strategy_with_sample_data(sample_ohlcv_data):
    """Test strategy using fixture data."""
    from strategies.liquidity_sweep import LiquiditySweepStrategy

    strategy = LiquiditySweepStrategy()
    signals = strategy.generate_signals(sample_ohlcv_data)

    assert isinstance(signals, list)
```

---

## Using Existing Core Functions

### Pattern 1: Using Market Structure Detection

```python
from core.market_structure import find_swing_points, determine_trend
import pandas as pd


def analyze_market_structure(data: pd.DataFrame) -> dict:
    """Analyze market structure using core functions."""

    # Find swing points
    swing_highs, swing_lows = find_swing_points(
        data['high'],
        data['low'],
        n=5  # Look 5 bars on each side
    )

    # Determine trend
    trend = determine_trend(swing_highs, swing_lows)

    # Latest trend value
    current_trend = trend.iloc[-1]  # 1 = uptrend, -1 = downtrend, 0 = ranging

    return {
        'swing_highs': swing_highs.dropna(),
        'swing_lows': swing_lows.dropna(),
        'current_trend': current_trend,
        'is_uptrend': current_trend == 1,
        'is_downtrend': current_trend == -1,
        'is_ranging': current_trend == 0
    }
```

### Pattern 2: Using Liquidity Detection

```python
from core.liquidity import detect_liquidity_sweep, find_equal_levels


def find_sweep_opportunities(data: pd.DataFrame) -> pd.DataFrame:
    """Find liquidity sweep opportunities."""

    # Get swing points first
    from core.market_structure import find_swing_points
    swing_highs, swing_lows = find_swing_points(
        data['high'], data['low'], n=5
    )

    # Find equal lows (liquidity pools)
    equal_highs, equal_lows = find_equal_levels(
        swing_highs.dropna(),
        swing_lows.dropna(),
        tolerance=0.001  # 0.1% tolerance
    )

    # Detect sweeps of equal lows (bullish setup)
    bullish_sweeps = detect_liquidity_sweep(
        data['high'],
        data['low'],
        data['close'],
        liquidity_levels=equal_lows,
        reversal_bars=3
    )

    # Return sweep timestamps and prices
    sweep_data = data.loc[bullish_sweeps]
    return sweep_data
```

### Pattern 3: Using Risk Management

```python
from risk.position_sizing import calculate_position_size, RiskParameters
from risk.confidence import ConfidenceFactors


def size_position(
    signal: 'Signal',
    portfolio_value: float,
    market_data: pd.DataFrame
) -> float:
    """Calculate position size for a signal."""

    # Calculate confidence score
    factors = ConfidenceFactors()
    factors.pattern_clean = True  # Signal passed filters
    factors.volume_spike = market_data['volume'].iloc[-1] > market_data['volume'].mean() * 1.5
    # ... set other factors ...

    confidence = factors.calculate_score()

    # Setup risk parameters
    risk_params = RiskParameters(
        base_risk_percent=0.02,  # 2% base risk
        max_position_percent=0.05,  # 5% max position
        min_confidence=50  # Minimum confidence threshold
    )

    # Calculate ATR for volatility adjustment
    atr_current = calculate_atr(market_data, period=14).iloc[-1]
    atr_baseline = calculate_atr(market_data, period=14).rolling(50).mean().iloc[-1]

    # Calculate position size
    position_size = calculate_position_size(
        portfolio_value=portfolio_value,
        entry_price=signal.entry_price,
        stop_loss_price=signal.stop_loss,
        confidence_score=confidence,
        current_atr=atr_current,
        baseline_atr=atr_baseline,
        consecutive_wins=0,  # Track from trade history
        consecutive_losses=0,
        params=risk_params
    )

    return position_size


def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate ATR (helper function)."""
    high = data['high']
    low = data['low']
    close = data['close']

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())

    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    return atr
```

---

## Configuration Management

### Pattern 1: Dataclass Configuration

```python
from dataclasses import dataclass, field
from typing import Literal, Optional
import os


@dataclass
class TradingConfig:
    """Trading configuration with defaults."""

    # Network
    network: Literal['testnet', 'mainnet'] = 'testnet'

    # Trading parameters
    symbols: list[str] = field(default_factory=lambda: ['BTC', 'ETH'])
    timeframe: str = '1h'
    check_interval_seconds: int = 60

    # Risk management
    max_risk_percent: float = 0.02
    max_position_percent: float = 0.05
    min_confidence: int = 50

    # API credentials (loaded from env)
    api_key: Optional[str] = None
    api_secret: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        self.validate()

    def validate(self):
        """Validate configuration values."""
        if self.max_risk_percent > 0.05:
            raise ValueError("max_risk_percent too high (>5%)")

        if self.min_confidence < 0 or self.min_confidence > 100:
            raise ValueError("min_confidence must be 0-100")

        if self.check_interval_seconds < 1:
            raise ValueError("check_interval_seconds must be >= 1")

    @classmethod
    def from_env(cls) -> 'TradingConfig':
        """Load configuration from environment variables."""
        return cls(
            network=os.getenv('TRADING_NETWORK', 'testnet'),
            api_key=os.getenv('API_KEY'),
            api_secret=os.getenv('API_SECRET'),
            max_risk_percent=float(os.getenv('MAX_RISK', '0.02')),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary (for serialization)."""
        return {
            'network': self.network,
            'symbols': self.symbols,
            'timeframe': self.timeframe,
            'max_risk_percent': self.max_risk_percent,
            # Exclude sensitive data
        }
```

---

## Logging

### Pattern 1: Module-Level Logger

```python
import logging

# Create logger for this module
logger = logging.getLogger(__name__)


class MyClass:
    """Example class with logging."""

    def __init__(self):
        logger.info("MyClass initialized")

    def fetch_data(self, symbol: str) -> pd.DataFrame:
        """Fetch data with logging."""
        logger.debug(f"Fetching data for {symbol}")

        try:
            data = self._api_call(symbol)
            logger.info(f"Successfully fetched {len(data)} candles for {symbol}")
            return data

        except Exception as e:
            logger.error(f"Failed to fetch {symbol}: {e}", exc_info=True)
            raise
```

### Pattern 2: Setup Logging

```python
import logging
import sys
from pathlib import Path


def setup_logging(level: str = 'INFO', log_file: str = None):
    """
    Configure logging for the application.

    Args:
        level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_file: Optional file path for logs

    Example:
        >>> setup_logging('INFO', 'logs/trading.log')
    """
    # Create logs directory
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Setup handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    # Reduce noise from external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

    logging.info("Logging configured")
```

---

## Common Patterns

### Pattern 1: Pagination for Large Datasets

```python
import time


def fetch_all_data(
    symbol: str,
    timeframe: str,
    since_ms: int,
    batch_size: int = 1000
) -> list:
    """Fetch all data using pagination."""
    all_data = []
    current_since = since_ms
    now_ms = int(time.time() * 1000)

    while current_since < now_ms:
        # Fetch batch
        batch = api.fetch_ohlcv(
            symbol,
            timeframe,
            since=current_since,
            limit=batch_size
        )

        if not batch:
            break

        all_data.extend(batch)

        # Update since to last candle timestamp + 1ms
        current_since = batch[-1][0] + 1

        # Rate limit protection
        time.sleep(0.1)

        logger.debug(f"Fetched batch: {len(batch)} candles")

    logger.info(f"Pagination complete: {len(all_data)} total candles")
    return all_data
```

### Pattern 2: Retry with Exponential Backoff

```python
import time


def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """Retry function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()

        except Exception as e:
            if attempt == max_retries - 1:
                # Last attempt failed
                raise

            # Calculate delay: 1s, 2s, 4s, ...
            delay = base_delay * (2 ** attempt)
            logger.warning(
                f"Attempt {attempt + 1} failed: {e}. "
                f"Retrying in {delay}s..."
            )
            time.sleep(delay)
```

### Pattern 3: Converting API Response to DataFrame

```python
def api_response_to_dataframe(response: list) -> pd.DataFrame:
    """
    Convert API response to standard OHLCV DataFrame.

    Args:
        response: List of [timestamp, open, high, low, close, volume]

    Returns:
        DataFrame with standard format
    """
    if not response:
        return empty_ohlcv_dataframe()

    df = pd.DataFrame(
        response,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
    )

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df.set_index('timestamp', inplace=True)

    # Ensure numeric types
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Remove any NaN rows
    df.dropna(inplace=True)

    # Sort and deduplicate
    df.sort_index(inplace=True)
    df = df[~df.index.duplicated(keep='first')]

    return df
```

---

## Quick Reference

### Import Statements

```python
# Standard library
import logging
import time
from typing import Optional, Literal, List, Dict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Third-party
import pandas as pd
import numpy as np
import pytest
from unittest.mock import Mock, patch

# Project imports
from core.market_structure import find_swing_points, determine_trend
from core.liquidity import detect_liquidity_sweep, find_equal_levels
from core.imbalance import find_fair_value_gaps
from core.order_blocks import find_order_blocks
from strategies.base import BaseStrategy, Signal
from risk.position_sizing import calculate_position_size, RiskParameters
from risk.confidence import ConfidenceFactors
from data.fetcher import BaseFetcher
```

### Common Variable Names

```python
# DataFrame column names (ALWAYS lowercase)
df['open']
df['high']
df['low']
df['close']
df['volume']

# Time-related
timestamp: pd.Timestamp
timeframe: str  # '1m', '5m', '15m', '1h', '4h', '1d'
since: str  # ISO date or Unix timestamp
limit: int  # Number of candles

# Trading
symbol: str  # 'BTC/USDT' or 'BTC' (depends on exchange)
signal: Signal
direction: int  # 1 = long, -1 = short
entry_price: float
stop_loss: float
take_profit: float
confidence: int  # 0-100

# Risk
portfolio_value: float
position_size: float
risk_percent: float
max_position_percent: float
```

---

**Use these patterns as templates for your implementation. Copy-paste and modify as needed!**
