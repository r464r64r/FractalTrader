"""Tests for data fetchers."""

import pytest
import pandas as pd
from datetime import datetime, timedelta

from data.hyperliquid_fetcher import HyperliquidFetcher
from data.ccxt_fetcher import CCXTFetcher
from data.fetcher import BaseFetcher


class TestBaseFetcher:
    """Tests for base fetcher interface."""

    def test_base_fetcher_is_abstract(self):
        """Test that BaseFetcher cannot be instantiated."""
        with pytest.raises(TypeError):
            BaseFetcher()

    def test_validate_dataframe_with_correct_format(self):
        """Test validation passes with correct format."""
        df = pd.DataFrame({
            'open': [100.0, 101.0],
            'high': [102.0, 103.0],
            'low': [99.0, 100.0],
            'close': [101.0, 102.0],
            'volume': [1000.0, 2000.0]
        })
        df.index = pd.DatetimeIndex(['2024-01-01', '2024-01-02'])

        fetcher = HyperliquidFetcher(network='testnet')
        assert fetcher.validate_dataframe(df) is True

    def test_validate_dataframe_missing_columns(self):
        """Test validation fails with missing columns."""
        df = pd.DataFrame({
            'open': [100.0],
            'high': [102.0],
            'low': [99.0],
            # missing 'close' and 'volume'
        })
        df.index = pd.DatetimeIndex(['2024-01-01'])

        fetcher = HyperliquidFetcher(network='testnet')
        with pytest.raises(ValueError, match="Missing required columns"):
            fetcher.validate_dataframe(df)

    def test_validate_dataframe_invalid_index(self):
        """Test validation fails without DatetimeIndex."""
        df = pd.DataFrame({
            'open': [100.0],
            'high': [102.0],
            'low': [99.0],
            'close': [101.0],
            'volume': [1000.0]
        })
        # No DatetimeIndex

        fetcher = HyperliquidFetcher(network='testnet')
        with pytest.raises(ValueError, match="Index must be DatetimeIndex"):
            fetcher.validate_dataframe(df)

    def test_validate_dataframe_empty(self):
        """Test validation fails with empty DataFrame."""
        df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        df.index = pd.DatetimeIndex([])

        fetcher = HyperliquidFetcher(network='testnet')
        with pytest.raises(ValueError, match="DataFrame is empty"):
            fetcher.validate_dataframe(df)


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
        assert fetcher.timeout == 30

    def test_initialization_mainnet(self):
        """Test mainnet initialization."""
        fetcher = HyperliquidFetcher(network='mainnet')
        assert fetcher.network == 'mainnet'

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
            assert isinstance(df, pd.DataFrame)

    def test_invalid_timeframe_raises_error(self, fetcher):
        """Test invalid timeframe raises ValueError."""
        with pytest.raises(ValueError, match="Invalid timeframe"):
            fetcher.fetch_ohlcv('BTC', '3h')

    def test_limit_exceeds_max_capped(self, fetcher):
        """Test limit exceeding max is capped at 5000."""
        df = fetcher.fetch_ohlcv('BTC', '1h', limit=10000)
        assert len(df) <= 5000

    def test_empty_dataframe_has_correct_format(self, fetcher):
        """Test empty DataFrame maintains correct structure."""
        df = fetcher._empty_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_parse_since_iso_format(self, fetcher):
        """Test parsing ISO date string."""
        ts = fetcher._parse_since('2024-01-01')
        expected = int(pd.to_datetime('2024-01-01').timestamp() * 1000)
        assert ts == expected

    def test_parse_since_unix_timestamp_seconds(self, fetcher):
        """Test parsing Unix timestamp in seconds."""
        ts = fetcher._parse_since('1704067200')  # 2024-01-01 in seconds
        assert ts == 1704067200000  # Should convert to ms

    def test_parse_since_invalid_format(self, fetcher):
        """Test parsing invalid format raises error."""
        with pytest.raises(ValueError, match="Invalid 'since' format"):
            fetcher._parse_since('invalid_date')

    def test_calculate_start_time(self, fetcher):
        """Test start time calculation."""
        end_time = int(pd.to_datetime('2024-12-20').timestamp() * 1000)
        start = fetcher._calculate_start_time(end_time, '1h', 100)

        # 100 hours = 100 * 60 * 60 * 1000 ms
        expected = end_time - (100 * 60 * 60 * 1000)
        assert start == expected

    def test_get_available_symbols(self, fetcher):
        """Test fetching available symbols."""
        symbols = fetcher.get_available_symbols()
        assert isinstance(symbols, list)
        # Should have some symbols
        assert len(symbols) > 0

    def test_get_current_price(self, fetcher):
        """Test fetching current price."""
        price = fetcher.get_current_price('BTC')
        assert isinstance(price, float)
        # Price should be positive (or 0 if API fails)
        assert price >= 0


class TestCCXTFetcher:
    """Tests for CCXT data fetcher."""

    @pytest.fixture
    def fetcher(self):
        """Create fetcher instance (Binance)."""
        return CCXTFetcher('binance')

    def test_initialization(self, fetcher):
        """Test fetcher initializes correctly."""
        assert fetcher.exchange_id == 'binance'
        assert fetcher.exchange is not None

    def test_initialization_different_exchange(self):
        """Test initialization with different exchange."""
        fetcher = CCXTFetcher('bybit')
        assert fetcher.exchange_id == 'bybit'

    def test_invalid_exchange_raises_error(self):
        """Test invalid exchange name raises error."""
        with pytest.raises(ValueError, match="not supported"):
            CCXTFetcher('invalid_exchange_name')

    def test_fetch_ohlcv_basic(self, fetcher):
        """Test basic OHLCV fetch."""
        df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=100)

        assert isinstance(df, pd.DataFrame)
        assert len(df) <= 100
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_fetch_ohlcv_with_since(self, fetcher):
        """Test fetching from specific date."""
        df = fetcher.fetch_ohlcv('BTC/USDT', '1d', since='2024-12-01', limit=30)

        assert len(df) <= 30
        assert df.index[0] >= pd.to_datetime('2024-12-01', utc=True)

    def test_different_exchanges(self):
        """Test multiple exchanges work."""
        for exchange in ['binance', 'bybit']:
            fetcher = CCXTFetcher(exchange)
            df = fetcher.fetch_ohlcv('BTC/USDT', '1h', limit=10)
            assert len(df) > 0

    def test_get_available_symbols(self, fetcher):
        """Test fetching available symbols."""
        symbols = fetcher.get_available_symbols()
        assert isinstance(symbols, list)
        assert 'BTC/USDT' in symbols

    def test_get_current_price(self, fetcher):
        """Test fetching current price."""
        price = fetcher.get_current_price('BTC/USDT')
        assert isinstance(price, float)
        assert price > 0  # BTC price should be positive

    def test_empty_dataframe_has_correct_format(self, fetcher):
        """Test empty DataFrame maintains correct structure."""
        df = fetcher._empty_dataframe()
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
        assert isinstance(df.index, pd.DatetimeIndex)

    def test_parse_since_iso_format(self, fetcher):
        """Test parsing ISO date string."""
        ts = fetcher._parse_since('2024-01-01')
        expected = int(pd.to_datetime('2024-01-01').timestamp() * 1000)
        assert ts == expected

    def test_parse_since_unix_timestamp(self, fetcher):
        """Test parsing Unix timestamp."""
        ts = fetcher._parse_since('1704067200')
        assert ts == 1704067200000


class TestFetcherCompatibility:
    """Test that both fetchers return compatible DataFrames."""

    def test_both_fetchers_same_format(self):
        """Test Hyperliquid and CCXT return same format."""
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
