# Task 1: Data Layer Implementation

**Estimated Time:** 1-2 days
**Difficulty:** Medium
**Dependencies:** None (standalone task)
**Goal:** Create dual data fetchers (Hyperliquid + CCXT) with standardized output

---

## Overview

You will create **two data fetchers** that retrieve OHLCV (Open, High, Low, Close, Volume) data from different sources:

1. **HyperliquidFetcher** — Primary for live trading (last 5000 candles via native SDK)
2. **CCXTFetcher** — Secondary for deep backtesting (unlimited history via Binance)

**Why two fetchers?**
- Hyperliquid: Fast, low-latency, perfect for live trading
- CCXT/Binance: Deep historical data (years) for rigorous backtesting
- Price correlation between exchanges >99%, so backtest on Binance, trade on Hyperliquid

**Critical requirement:** Both must return **identical DataFrame format** so strategies work with either.

---

## Implementation Plan (15 Steps)

### Phase 1: Setup & Base Interface (30 min)

#### Step 1: Update Base Fetcher

**File:** `data/fetcher.py` (already exists, needs enhancement)

**Current state:**
```python
# Simple function, not a class
def fetch_ohlcv(...) -> pd.DataFrame:
    pass
```

**New structure (ABC pattern):**
```python
"""Data fetching base interface."""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Optional, Literal
from datetime import datetime


class BaseFetcher(ABC):
    """
    Abstract base class for data fetchers.

    All fetchers must implement this interface to ensure
    strategies work with any data source.
    """

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: Optional[int] = None,
        since: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data.

        Args:
            symbol: Trading pair (format depends on exchange)
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: Maximum number of candles to fetch
            since: Start date (ISO format: '2023-01-01' or timestamp)

        Returns:
            DataFrame with:
                - Index: DatetimeIndex (timezone-aware UTC)
                - Columns: ['open', 'high', 'low', 'close', 'volume']
                - All prices as float64
                - Volume as float64

        Raises:
            ValueError: Invalid symbol or timeframe
            ConnectionError: Network/API issues
        """
        pass

    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        """
        Validate DataFrame matches required format.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid

        Raises:
            ValueError: If format is incorrect
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']

        if not all(col in df.columns for col in required_columns):
            missing = [c for c in required_columns if c not in df.columns]
            raise ValueError(f"Missing required columns: {missing}")

        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("Index must be DatetimeIndex")

        if df.empty:
            raise ValueError("DataFrame is empty")

        return True


# Keep the old function for backward compatibility
def fetch_ohlcv(
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    limit: int = 1000,
    exchange_id: str = "binance"
) -> pd.DataFrame:
    """
    Legacy function for backward compatibility.

    Use CCXTFetcher class instead.
    """
    from data.ccxt_fetcher import CCXTFetcher

    fetcher = CCXTFetcher(exchange_id)
    return fetcher.fetch_ohlcv(symbol, timeframe, limit)
```

**Test:**
```python
# tests/test_data_fetchers.py
def test_base_fetcher_is_abstract():
    from data.fetcher import BaseFetcher

    with pytest.raises(TypeError):
        BaseFetcher()  # Can't instantiate ABC
```

---

### Phase 2: Hyperliquid Fetcher (3-4 hours)

#### Step 2: Install Hyperliquid SDK

**Command:**
```bash
# Already in requirements.txt, but verify
pip install hyperliquid-python-sdk==0.5.0
```

**Verify installation:**
```python
# In Python shell
from hyperliquid.info import Info
from hyperliquid.utils import constants
print(constants.MAINNET_API_URL)
# Should print: https://api.hyperliquid.xyz
```

#### Step 3: Create Hyperliquid Fetcher Class

**File:** `data/hyperliquid_fetcher.py` (NEW)

**Full implementation:**
```python
"""Hyperliquid data fetcher using native SDK."""

import pandas as pd
from typing import Optional, Literal
from datetime import datetime, timezone
import time
import logging

from hyperliquid.info import Info
from hyperliquid.utils import constants

from data.fetcher import BaseFetcher


logger = logging.getLogger(__name__)


class HyperliquidFetcher(BaseFetcher):
    """
    Fetch data from Hyperliquid DEX using native SDK.

    Hyperliquid provides:
    - Last 5000 candles per request (FREE)
    - Real-time WebSocket data
    - Low latency (<200ms)

    Limitations:
    - Historical data limited to 5000 candles
    - Use CCXT/Binance for deep backtesting (>5000 candles)
    """

    MAINNET_URL = constants.MAINNET_API_URL
    TESTNET_URL = constants.TESTNET_API_URL

    # Hyperliquid timeframe mapping
    TIMEFRAME_MAP = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '1h': '1h',
        '4h': '4h',
        '1d': '1d',
    }

    MAX_CANDLES = 5000  # Hyperliquid API limit

    def __init__(
        self,
        network: Literal['mainnet', 'testnet'] = 'mainnet',
        timeout: int = 30
    ):
        """
        Initialize Hyperliquid fetcher.

        Args:
            network: 'mainnet' or 'testnet'
            timeout: Request timeout in seconds
        """
        self.network = network
        api_url = self.MAINNET_URL if network == 'mainnet' else self.TESTNET_URL

        self.info = Info(api_url, skip_ws=True)  # No WebSocket for now
        self.timeout = timeout

        logger.info(f"HyperliquidFetcher initialized ({network})")

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: Optional[int] = None,
        since: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from Hyperliquid.

        Args:
            symbol: Coin name (e.g., 'BTC', 'ETH') - no /USDT suffix
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: Number of candles (max 5000, default 1000)
            since: Start timestamp (ISO format or Unix timestamp)

        Returns:
            DataFrame with standard format

        Raises:
            ValueError: Invalid symbol or timeframe
            ConnectionError: API request failed

        Example:
            >>> fetcher = HyperliquidFetcher()
            >>> df = fetcher.fetch_ohlcv('BTC', '1h', limit=100)
            >>> df.head()
                                open    high     low   close    volume
            2024-12-01 00:00:00  42000  42100  41900  42050  1234.56
        """
        # Validate inputs
        if timeframe not in self.TIMEFRAME_MAP:
            raise ValueError(
                f"Invalid timeframe: {timeframe}. "
                f"Valid options: {list(self.TIMEFRAME_MAP.keys())}"
            )

        if limit is None:
            limit = 1000  # Default
        elif limit > self.MAX_CANDLES:
            logger.warning(f"Limit {limit} exceeds max {self.MAX_CANDLES}, capping")
            limit = self.MAX_CANDLES

        # Convert timeframe
        hl_timeframe = self.TIMEFRAME_MAP[timeframe]

        # Calculate time range
        end_time = int(time.time() * 1000)  # Current time in ms

        if since is not None:
            start_time = self._parse_since(since)
        else:
            # Calculate start time based on limit and timeframe
            start_time = self._calculate_start_time(end_time, timeframe, limit)

        # Fetch data from Hyperliquid
        try:
            candles = self.info.candles_snapshot(
                coin=symbol,
                interval=hl_timeframe,
                startTime=start_time,
                endTime=end_time
            )
        except Exception as e:
            raise ConnectionError(f"Hyperliquid API error: {e}")

        if not candles:
            logger.warning(f"No data returned for {symbol} {timeframe}")
            return self._empty_dataframe()

        # Convert to DataFrame
        df = self._candles_to_dataframe(candles)

        # Apply limit
        if limit and len(df) > limit:
            df = df.tail(limit)

        # Validate format
        self.validate_dataframe(df)

        logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
        return df

    def _parse_since(self, since: str) -> int:
        """
        Parse 'since' parameter to Unix timestamp (ms).

        Args:
            since: ISO date string or Unix timestamp

        Returns:
            Unix timestamp in milliseconds
        """
        # Try parsing as ISO date
        try:
            dt = pd.to_datetime(since)
            return int(dt.timestamp() * 1000)
        except:
            pass

        # Try as Unix timestamp (seconds)
        try:
            ts = int(since)
            # If less than year 2000, assume it's in seconds
            if ts < 946684800:
                raise ValueError("Timestamp too old")
            # If less than typical ms timestamp, convert to ms
            if ts < 10000000000:
                ts *= 1000
            return ts
        except:
            raise ValueError(f"Invalid 'since' format: {since}")

    def _calculate_start_time(self, end_time: int, timeframe: str, limit: int) -> int:
        """
        Calculate start time based on end time, timeframe, and limit.

        Args:
            end_time: End timestamp (ms)
            timeframe: Candle timeframe
            limit: Number of candles

        Returns:
            Start timestamp (ms)
        """
        # Timeframe to milliseconds
        tf_to_ms = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
        }

        interval_ms = tf_to_ms[timeframe]
        start_time = end_time - (limit * interval_ms)

        return start_time

    def _candles_to_dataframe(self, candles: list) -> pd.DataFrame:
        """
        Convert Hyperliquid candles to standard DataFrame format.

        Args:
            candles: List of candle dicts from Hyperliquid API

        Returns:
            DataFrame with standard format
        """
        if not candles:
            return self._empty_dataframe()

        # Hyperliquid candle format:
        # [
        #   {
        #     't': 1638316800000,  # timestamp (ms)
        #     'T': 1638320399999,  # close time
        #     'o': '57000.0',      # open
        #     'h': '57100.0',      # high
        #     'l': '56900.0',      # low
        #     'c': '57050.0',      # close
        #     'v': '123.45',       # volume
        #     'n': 1234            # number of trades
        #   },
        #   ...
        # ]

        data = []
        for candle in candles:
            data.append({
                'timestamp': candle['t'],
                'open': float(candle['o']),
                'high': float(candle['h']),
                'low': float(candle['l']),
                'close': float(candle['c']),
                'volume': float(candle['v']),
            })

        df = pd.DataFrame(data)

        # Convert timestamp to datetime index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df.set_index('timestamp', inplace=True)

        # Sort by time
        df.sort_index(inplace=True)

        return df

    def _empty_dataframe(self) -> pd.DataFrame:
        """Return empty DataFrame with correct format."""
        df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        df.index = pd.DatetimeIndex([], name='timestamp')
        return df

    def get_available_symbols(self) -> list[str]:
        """
        Get list of available trading symbols on Hyperliquid.

        Returns:
            List of coin names (e.g., ['BTC', 'ETH', 'SOL'])
        """
        try:
            meta = self.info.meta()
            universe = meta.get('universe', [])
            return [coin['name'] for coin in universe]
        except Exception as e:
            logger.error(f"Failed to fetch symbols: {e}")
            return []

    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.

        Args:
            symbol: Coin name (e.g., 'BTC')

        Returns:
            Current price as float
        """
        try:
            all_mids = self.info.all_mids()
            return float(all_mids.get(symbol, 0))
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            return 0.0
```

**Key features:**
- Standard DataFrame output (matches existing code)
- Error handling (network issues, invalid inputs)
- Logging (for debugging)
- Type hints (all parameters and returns)
- Docstrings (Google style)

#### Step 4: Write Tests for Hyperliquid Fetcher

**File:** `tests/test_data_fetchers.py` (NEW)

```python
"""Tests for data fetchers."""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from data.hyperliquid_fetcher import HyperliquidFetcher
from data.fetcher import BaseFetcher


class TestHyperliquidFetcher:
    """Tests for Hyperliquid data fetcher."""

    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance (testnet)."""
        return HyperliquidFetcher(network='testnet')

    def test_initialization(self, fetcher):
        """Test fetcher initializes correctly."""
        assert fetcher.network == 'testnet'
        assert fetcher.info is not None

    def test_fetch_ohlcv_basic(self, fetcher):
        """Test basic OHLCV fetch."""
        df = fetcher.fetch_ohlcv('BTC', '1h', limit=100)

        # Check DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) <= 100
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']

        # Check index
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.is_monotonic_increasing

        # Check data types
        assert df['open'].dtype == float
        assert df['close'].dtype == float

    def test_fetch_ohlcv_respects_limit(self, fetcher):
        """Test that limit parameter works."""
        df = fetcher.fetch_ohlcv('BTC', '1h', limit=50)
        assert len(df) <= 50

    def test_fetch_ohlcv_different_timeframes(self, fetcher):
        """Test fetching different timeframes."""
        for tf in ['1m', '5m', '15m', '1h', '4h', '1d']:
            df = fetcher.fetch_ohlcv('BTC', tf, limit=10)
            assert len(df) > 0

    def test_invalid_timeframe_raises_error(self, fetcher):
        """Test invalid timeframe raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timeframe"):
            fetcher.fetch_ohlcv('BTC', '3h')

    def test_limit_exceeds_max_capped(self, fetcher):
        """Test limit exceeding max is capped at 5000."""
        df = fetcher.fetch_ohlcv('BTC', '1h', limit=10000)
        assert len(df) <= 5000

    def test_empty_symbol_handling(self, fetcher):
        """Test handling of invalid symbol."""
        # Hyperliquid should return empty or raise error
        with pytest.raises((ValueError, ConnectionError)):
            fetcher.fetch_ohlcv('INVALID_SYMBOL_XYZ', '1h')

    def test_dataframe_validation(self, fetcher):
        """Test DataFrame passes validation."""
        df = fetcher.fetch_ohlcv('BTC', '1h', limit=10)
        assert fetcher.validate_dataframe(df) is True

    def test_get_available_symbols(self, fetcher):
        """Test fetching available symbols."""
        symbols = fetcher.get_available_symbols()
        assert isinstance(symbols, list)
        assert 'BTC' in symbols
        assert 'ETH' in symbols

    def test_get_current_price(self, fetcher):
        """Test fetching current price."""
        price = fetcher.get_current_price('BTC')
        assert isinstance(price, float)
        assert price > 0  # BTC price should be positive

    def test_since_parameter(self, fetcher):
        """Test using 'since' parameter."""
        since = '2024-12-01'
        df = fetcher.fetch_ohlcv('BTC', '1h', since=since)

        # First candle should be after 'since' date
        first_date = df.index[0]
        assert first_date >= pd.to_datetime(since, utc=True)

    def test_parse_since_iso_format(self, fetcher):
        """Test parsing ISO date string."""
        ts = fetcher._parse_since('2024-01-01')
        expected = int(pd.to_datetime('2024-01-01').timestamp() * 1000)
        assert ts == expected

    def test_parse_since_unix_timestamp(self, fetcher):
        """Test parsing Unix timestamp."""
        ts = fetcher._parse_since('1704067200')  # 2024-01-01 in seconds
        assert ts == 1704067200000  # Should convert to ms

    def test_empty_dataframe_has_correct_format(self, fetcher):
        """Test empty DataFrame maintains correct structure."""
        df = fetcher._empty_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
        assert isinstance(df.index, pd.DatetimeIndex)
```

**Run tests:**
```bash
python -m pytest tests/test_data_fetchers.py::TestHyperliquidFetcher -v
```

**Expected:** All 15 tests passing

---

### Phase 3: CCXT Fetcher (2-3 hours)

#### Step 5: Create CCXT Fetcher Class

**File:** `data/ccxt_fetcher.py` (NEW)

```python
"""CCXT data fetcher for multi-exchange support."""

import pandas as pd
from typing import Optional, Literal
import time
import logging

import ccxt

from data.fetcher import BaseFetcher


logger = logging.getLogger(__name__)


class CCXTFetcher(BaseFetcher):
    """
    Fetch data using CCXT library (multi-exchange support).

    Primary use: Deep backtesting with unlimited historical data.
    Recommended exchange: Binance (most liquid, longest history).

    Advantages:
    - Unlimited historical data (years)
    - Multiple exchanges supported
    - Well-tested library

    Disadvantages:
    - Slower than native SDKs
    - Requires pagination for large datasets
    """

    # CCXT-supported timeframes
    TIMEFRAME_MAP = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '1h': '1h',
        '4h': '4h',
        '1d': '1d',
    }

    def __init__(
        self,
        exchange_id: str = 'binance',
        config: Optional[dict] = None
    ):
        """
        Initialize CCXT fetcher.

        Args:
            exchange_id: Exchange name ('binance', 'bybit', 'okx', etc.)
            config: Optional CCXT config (API keys, etc.)

        Raises:
            ValueError: If exchange not supported
        """
        self.exchange_id = exchange_id

        # Initialize exchange
        try:
            exchange_class = getattr(ccxt, exchange_id)
            self.exchange = exchange_class(config or {})
        except AttributeError:
            raise ValueError(f"Exchange '{exchange_id}' not supported by CCXT")

        logger.info(f"CCXTFetcher initialized ({exchange_id})")

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: Optional[int] = None,
        since: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from exchange.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT', 'ETH/USDT')
            timeframe: Candle timeframe
            limit: Max candles (if None and 'since' provided, fetches all)
            since: Start date (ISO format or Unix timestamp)

        Returns:
            DataFrame with standard format

        Example:
            >>> fetcher = CCXTFetcher('binance')
            >>> df = fetcher.fetch_ohlcv('BTC/USDT', '1h', since='2023-01-01')
            >>> len(df)
            8760  # Full year of hourly data
        """
        # Validate timeframe
        if timeframe not in self.TIMEFRAME_MAP:
            raise ValueError(
                f"Invalid timeframe: {timeframe}. "
                f"Valid options: {list(self.TIMEFRAME_MAP.keys())}"
            )

        # Parse 'since' parameter
        since_ms = self._parse_since(since) if since else None

        # Fetch data (with pagination if needed)
        if since_ms and limit is None:
            # Fetch all data from 'since' to now (pagination required)
            all_candles = self._fetch_all_since(symbol, timeframe, since_ms)
        else:
            # Single request
            try:
                all_candles = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=since_ms,
                    limit=limit or 1000
                )
            except Exception as e:
                raise ConnectionError(f"CCXT fetch error: {e}")

        if not all_candles:
            logger.warning(f"No data returned for {symbol} {timeframe}")
            return self._empty_dataframe()

        # Convert to DataFrame
        df = self._ohlcv_to_dataframe(all_candles)

        # Validate format
        self.validate_dataframe(df)

        logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
        return df

    def _fetch_all_since(
        self,
        symbol: str,
        timeframe: str,
        since_ms: int,
        batch_size: int = 1000
    ) -> list:
        """
        Fetch all candles from 'since' to now using pagination.

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            since_ms: Start timestamp (ms)
            batch_size: Candles per request

        Returns:
            List of OHLCV arrays
        """
        all_candles = []
        current_since = since_ms
        now_ms = int(time.time() * 1000)

        while current_since < now_ms:
            try:
                batch = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=current_since,
                    limit=batch_size
                )
            except Exception as e:
                logger.error(f"Pagination error: {e}")
                break

            if not batch:
                break

            all_candles.extend(batch)

            # Update since to last candle timestamp + 1ms
            current_since = batch[-1][0] + 1

            # Rate limit protection
            time.sleep(self.exchange.rateLimit / 1000)

            logger.debug(f"Fetched batch: {len(batch)} candles")

        logger.info(f"Pagination complete: {len(all_candles)} total candles")
        return all_candles

    def _parse_since(self, since: str) -> int:
        """Parse 'since' parameter to Unix timestamp (ms)."""
        try:
            # Try ISO date
            dt = pd.to_datetime(since)
            return int(dt.timestamp() * 1000)
        except:
            pass

        try:
            # Try Unix timestamp
            ts = int(since)
            if ts < 10000000000:  # Assume seconds
                ts *= 1000
            return ts
        except:
            raise ValueError(f"Invalid 'since' format: {since}")

    def _ohlcv_to_dataframe(self, ohlcv: list) -> pd.DataFrame:
        """
        Convert CCXT OHLCV to DataFrame.

        Args:
            ohlcv: List of [timestamp, open, high, low, close, volume]

        Returns:
            DataFrame with standard format
        """
        if not ohlcv:
            return self._empty_dataframe()

        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )

        # Convert timestamp to datetime index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df.set_index('timestamp', inplace=True)

        # Sort by time
        df.sort_index(inplace=True)

        # Remove duplicates (can happen with pagination)
        df = df[~df.index.duplicated(keep='first')]

        return df

    def _empty_dataframe(self) -> pd.DataFrame:
        """Return empty DataFrame with correct format."""
        df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        df.index = pd.DatetimeIndex([], name='timestamp')
        return df

    def get_available_symbols(self) -> list[str]:
        """
        Get list of available trading symbols.

        Returns:
            List of trading pairs (e.g., ['BTC/USDT', 'ETH/USDT'])
        """
        try:
            markets = self.exchange.load_markets()
            return list(markets.keys())
        except Exception as e:
            logger.error(f"Failed to fetch symbols: {e}")
            return []

    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Current price as float
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            return 0.0
```

#### Step 6: Write Tests for CCXT Fetcher

**Add to:** `tests/test_data_fetchers.py`

```python
class TestCCXTFetcher:
    """Tests for CCXT data fetcher."""

    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance (Binance)."""
        from data.ccxt_fetcher import CCXTFetcher
        return CCXTFetcher('binance')

    def test_initialization(self, fetcher):
        """Test fetcher initializes correctly."""
        assert fetcher.exchange_id == 'binance'
        assert fetcher.exchange is not None

    def test_fetch_ohlcv_basic(self, fetcher):
        """Test basic OHLCV fetch."""
        df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=100)

        assert isinstance(df, pd.DataFrame)
        assert len(df) <= 100
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_fetch_ohlcv_with_since(self, fetcher):
        """Test fetching from specific date."""
        df = fetcher.fetch_ohlcv('BTC/USDT', '1d', since='2024-01-01', limit=30)

        assert len(df) <= 30
        assert df.index[0] >= pd.to_datetime('2024-01-01', utc=True)

    def test_pagination_for_large_dataset(self, fetcher):
        """Test pagination works for large date ranges."""
        # Fetch 1 week of 1h data (168 candles)
        df = fetcher.fetch_ohlcv('BTC/USDT', '1h', since='2024-12-01', limit=None)

        # Should have multiple batches
        assert len(df) > 100

    def test_different_exchanges(self):
        """Test multiple exchanges work."""
        from data.ccxt_fetcher import CCXTFetcher

        for exchange in ['binance', 'bybit']:
            fetcher = CCXTFetcher(exchange)
            df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=10)
            assert len(df) > 0

    def test_invalid_exchange_raises_error(self):
        """Test invalid exchange name raises error."""
        from data.ccxt_fetcher import CCXTFetcher

        with pytest.raises(ValueError, match="not supported"):
            CCXTFetcher('invalid_exchange_name')

    def test_get_available_symbols(self, fetcher):
        """Test fetching available symbols."""
        symbols = fetcher.get_available_symbols()
        assert isinstance(symbols, list)
        assert 'BTC/USDT' in symbols

    def test_get_current_price(self, fetcher):
        """Test fetching current price."""
        price = fetcher.get_current_price('BTC/USDT')
        assert isinstance(price, float)
        assert price > 0


class TestFetcherCompatibility:
    """Test that both fetchers return compatible DataFrames."""

    def test_both_fetchers_same_format(self):
        """Test Hyperliquid and CCXT return same format."""
        from data.hyperliquid_fetcher import HyperliquidFetcher
        from data.ccxt_fetcher import CCXTFetcher

        hl_fetcher = HyperliquidFetcher(network='testnet')
        ccxt_fetcher = CCXTFetcher('binance')

        # Fetch same timeframe
        df_hl = hl_fetcher.fetch_ohlcv('BTC', '1h', limit=10)
        df_ccxt = ccxt_fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=10)

        # Check same columns
        assert list(df_hl.columns) == list(df_ccxt.columns)

        # Check same index type
        assert type(df_hl.index) == type(df_ccxt.index)

        # Check same dtypes
        assert df_hl.dtypes.to_dict() == df_ccxt.dtypes.to_dict()

    def test_strategies_work_with_both_fetchers(self):
        """Test that strategies can use either fetcher."""
        from data.hyperliquid_fetcher import HyperliquidFetcher
        from data.ccxt_fetcher import CCXTFetcher
        from strategies.liquidity_sweep import LiquiditySweepStrategy

        strategy = LiquiditySweepStrategy()

        # Test with Hyperliquid data
        hl_fetcher = HyperliquidFetcher(network='testnet')
        df_hl = hl_fetcher.fetch_ohlcv('BTC', '1h', limit=100)
        signals_hl = strategy.generate_signals(df_hl)
        # Should not raise error

        # Test with CCXT data
        ccxt_fetcher = CCXTFetcher('binance')
        df_ccxt = ccxt_fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=100)
        signals_ccxt = strategy.generate_signals(df_ccxt)
        # Should not raise error

        assert isinstance(signals_hl, list)
        assert isinstance(signals_ccxt, list)
```

**Run tests:**
```bash
python -m pytest tests/test_data_fetchers.py -v
```

**Expected:** 22+ tests passing

---

### Phase 4: Integration & Documentation (1 hour)

#### Step 7: Update `data/__init__.py`

```python
"""Data fetching utilities."""

from data.fetcher import BaseFetcher, fetch_ohlcv
from data.hyperliquid_fetcher import HyperliquidFetcher
from data.ccxt_fetcher import CCXTFetcher

__all__ = [
    'BaseFetcher',
    'fetch_ohlcv',
    'HyperliquidFetcher',
    'CCXTFetcher',
]
```

#### Step 8: Create Usage Examples

**File:** `examples/data_fetching_example.py` (NEW)

```python
"""Examples of using data fetchers."""

from data.hyperliquid_fetcher import HyperliquidFetcher
from data.ccxt_fetcher import CCXTFetcher


def example_hyperliquid():
    """Example: Fetch data from Hyperliquid."""
    print("=== Hyperliquid Fetcher ===")

    fetcher = HyperliquidFetcher(network='testnet')

    # Fetch recent data
    df = fetcher.fetch_ohlcv('BTC', '1h', limit=100)
    print(f"Fetched {len(df)} candles")
    print(df.head())
    print()

    # Get current price
    price = fetcher.get_current_price('BTC')
    print(f"Current BTC price: ${price:,.2f}")
    print()


def example_ccxt():
    """Example: Fetch data from Binance via CCXT."""
    print("=== CCXT Fetcher (Binance) ===")

    fetcher = CCXTFetcher('binance')

    # Fetch historical data
    df = fetcher.fetch_ohlcv('BTC/USDT', '1d', since='2024-01-01', limit=30)
    print(f"Fetched {len(df)} daily candles from 2024")
    print(df.head())
    print()

    # Get current price
    price = fetcher.get_current_price('BTC/USDT')
    print(f"Current BTC/USDT price: ${price:,.2f}")
    print()


def example_strategy_usage():
    """Example: Using fetchers with strategies."""
    print("=== Strategy with Data Fetcher ===")

    from strategies.liquidity_sweep import LiquiditySweepStrategy

    # Use Hyperliquid for live trading
    fetcher = HyperliquidFetcher(network='testnet')
    data = fetcher.fetch_ohlcv('BTC', '1h', limit=500)

    strategy = LiquiditySweepStrategy()
    signals = strategy.generate_signals(data)

    print(f"Generated {len(signals)} signals")
    if signals:
        print("Latest signal:")
        latest = signals[-1]
        print(f"  Direction: {'LONG' if latest.direction == 1 else 'SHORT'}")
        print(f"  Entry: ${latest.entry_price:,.2f}")
        print(f"  Stop: ${latest.stop_loss:,.2f}")
        print(f"  Confidence: {latest.confidence}/100")
    print()


if __name__ == '__main__':
    example_hyperliquid()
    example_ccxt()
    example_strategy_usage()
```

**Run example:**
```bash
python examples/data_fetching_example.py
```

#### Step 9: Update Documentation

**Update:** `DEVELOPMENT.md`

**Add section after "Test Summary":**

```markdown
### Data Layer (NEW - Sprint 6)

| Component | File | Status | Tests | Coverage |
|-----------|------|--------|-------|----------|
| Base Fetcher | `data/fetcher.py` | ✅ Done | 1 | 100% |
| Hyperliquid Fetcher | `data/hyperliquid_fetcher.py` | ✅ Done | 15 | 90% |
| CCXT Fetcher | `data/ccxt_fetcher.py` | ✅ Done | 7 | 85% |

**Total Tests:** 23 new tests (157 total)

**Usage:**
```python
# Live trading: Hyperliquid (last 5000 candles)
from data.hyperliquid_fetcher import HyperliquidFetcher
fetcher = HyperliquidFetcher()
data = fetcher.fetch_ohlcv('BTC', '1h', limit=1000)

# Backtesting: CCXT/Binance (unlimited history)
from data.ccxt_fetcher import CCXTFetcher
fetcher = CCXTFetcher('binance')
data = fetcher.fetch_ohlcv('BTC/USDT', '1h', since='2023-01-01')
```
```

---

## Checklist (Definition of Done)

### Code Quality
- [ ] All functions have type hints
- [ ] All functions have docstrings (Google style)
- [ ] Error handling for network issues
- [ ] Logging for debugging
- [ ] No print statements (use logger)

### Testing
- [ ] 15+ tests for HyperliquidFetcher
- [ ] 7+ tests for CCXTFetcher
- [ ] Integration tests (both fetchers work with strategies)
- [ ] All tests passing: `python -m pytest tests/test_data_fetchers.py -v`
- [ ] Coverage >85% for new code

### Functionality
- [ ] HyperliquidFetcher works on testnet
- [ ] CCXTFetcher works with Binance
- [ ] Both return identical DataFrame format
- [ ] Strategies work with both fetchers
- [ ] Pagination works for large datasets (CCXT)
- [ ] Error messages are clear

### Documentation
- [ ] DEVELOPMENT.md updated with new components
- [ ] Code examples created
- [ ] Inline comments for complex logic

---

## Troubleshooting

### Issue: Hyperliquid API timeout

**Symptoms:** `ConnectionError: Hyperliquid API error`

**Solution:**
```python
# Increase timeout
fetcher = HyperliquidFetcher(network='testnet', timeout=60)
```

### Issue: CCXT rate limit exceeded

**Symptoms:** `Exchange rate limit exceeded`

**Solution:**
```python
# Pagination includes rate limit protection
# But you can add manual delay:
time.sleep(1)  # 1 second between requests
```

### Issue: DataFrame format mismatch

**Symptoms:** Strategy raises `KeyError: 'open'`

**Solution:**
```python
# Verify format
print(df.columns)
# Should be: Index(['open', 'high', 'low', 'close', 'volume'])

# Use validation
fetcher.validate_dataframe(df)  # Raises error if wrong format
```

### Issue: Tests fail with "No data returned"

**Symptoms:** Empty DataFrame in tests

**Solution:**
- Check network connection
- Verify symbol exists (use `get_available_symbols()`)
- Try different date range

---

## Next Steps

After completing Task 1:

1. ✅ Verify all tests pass
2. ✅ Commit code: `git add data/ tests/test_data_fetchers.py`
3. ✅ `git commit -m "Add Hyperliquid and CCXT data fetchers with tests"`
4. ✅ Push: `git push origin alt`
5. ⏭️ Move to [HAIKU_TASK_2_LIVE_TRADING.md](HAIKU_TASK_2_LIVE_TRADING.md)

---

**Estimated completion time:** 1-2 days

**When done, you'll have:**
- 2 fully tested data fetchers
- 23 new passing tests
- 157 total tests (134 + 23)
- Foundation for live trading (Task 2)

Good luck! 🚀
