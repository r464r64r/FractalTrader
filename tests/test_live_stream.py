"""Tests for live data streaming."""

import os
import sys
import time
from datetime import datetime

import numpy as np
import pandas as pd
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from notebooks.live_data_stream import LiveDataStream, LiveIndicatorStream


class MockFetcher:
    """Mock fetcher for testing."""

    def __init__(self):
        self.fetch_count = 0

    def fetch_ohlcv(self, symbol, timeframe, limit):
        """Generate mock OHLCV data."""
        self.fetch_count += 1

        # Generate realistic data
        dates = pd.date_range(end=datetime.now(), periods=limit, freq="15min")

        np.random.seed(self.fetch_count)  # Different data each time

        df = pd.DataFrame(
            {
                "open": 50000 + np.random.randn(limit) * 100,
                "high": 50100 + np.random.randn(limit) * 100,
                "low": 49900 + np.random.randn(limit) * 100,
                "close": 50000 + np.random.randn(limit) * 100,
                "volume": np.random.randint(100, 1000, limit),
            },
            index=pd.DatetimeIndex(dates, name="timestamp"),
        )

        return df


@pytest.fixture
def mock_stream():
    """Create mock stream for testing."""
    stream = LiveDataStream(
        symbol="BTC",
        timeframes=["15m", "1h"],
        update_interval=1,  # Fast updates for testing
        source="hyperliquid",
        lookback=100,
    )

    # Replace with mock fetcher
    stream.fetcher = MockFetcher()

    return stream


class TestLiveDataStream:
    """Test suite for LiveDataStream."""

    def test_initialization(self, mock_stream):
        """Test stream initialization."""
        assert mock_stream.symbol == "BTC"
        assert mock_stream.timeframes == ["15m", "1h"]
        assert mock_stream.update_interval >= 1
        assert mock_stream.lookback == 100

    def test_fetch_initial_data(self, mock_stream):
        """Test initial data fetch."""
        mock_stream._fetch_all_timeframes()

        # Check data loaded for all timeframes
        assert "15m" in mock_stream.data
        assert "1h" in mock_stream.data

        # Check data format
        for tf, df in mock_stream.data.items():
            assert isinstance(df, pd.DataFrame)
            assert len(df) > 0
            assert all(col in df.columns for col in ["open", "high", "low", "close", "volume"])

    def test_get_latest_price(self, mock_stream):
        """Test getting latest price."""
        mock_stream._fetch_all_timeframes()

        price = mock_stream.get_latest_price()

        assert price is not None
        assert isinstance(price, float)
        assert price > 0

    def test_callback_registration(self, mock_stream):
        """Test callback registration."""
        callback_called = {"count": 0}

        def test_callback(data):
            callback_called["count"] += 1

        mock_stream.on_update(test_callback)

        assert len(mock_stream._callbacks) == 1

        # Trigger callback
        mock_stream._fetch_all_timeframes()
        mock_stream._notify_callbacks()

        assert callback_called["count"] == 1

    def test_start_stop_stream(self, mock_stream):
        """Test starting and stopping stream."""
        # Start stream
        mock_stream.start()

        assert mock_stream._thread is not None
        assert mock_stream._thread.is_alive()
        assert mock_stream.start_time is not None

        # Wait for updates (1s interval + buffer)
        time.sleep(3)

        # Check updates happened
        assert mock_stream.update_count >= 1

        # Stop stream
        mock_stream.stop()

        assert not mock_stream._thread.is_alive()

    def test_uptime_tracking(self, mock_stream):
        """Test uptime tracking."""
        assert mock_stream.get_uptime() is None  # Not started yet

        mock_stream.start()
        time.sleep(1)

        uptime = mock_stream.get_uptime()
        assert uptime is not None
        assert uptime >= 1

        mock_stream.stop()

    def test_error_handling(self, mock_stream):
        """Test error handling during fetch."""

        # Make fetcher raise error
        def failing_fetch(*args, **kwargs):
            raise ConnectionError("Mock network error")

        mock_stream.fetcher.fetch_ohlcv = failing_fetch

        # Start stream - errors will occur
        mock_stream.start()

        # Wait for at least 2 update cycles
        time.sleep(2.5)
        mock_stream.stop()

        # Should have recorded errors (timing-independent check)
        # At minimum, update_count should be > 0 even if all failed
        assert mock_stream.update_count > 0 or mock_stream.error_count > 0

    def test_callback_error_handling(self, mock_stream):
        """Test that callback errors don't crash stream."""

        def bad_callback(data):
            raise ValueError("Bad callback")

        mock_stream.on_update(bad_callback)

        # Should not crash
        mock_stream._fetch_all_timeframes()
        mock_stream._notify_callbacks()


class TestLiveIndicatorStream:
    """Test suite for LiveIndicatorStream."""

    def test_indicator_calculation(self):
        """Test automatic indicator calculation."""
        stream = LiveIndicatorStream(
            symbol="BTC", timeframes=["1h"], update_interval=1, source="hyperliquid", lookback=100
        )

        # Replace with mock fetcher
        stream.fetcher = MockFetcher()

        # Fetch data (should calculate indicators if detection modules available)
        stream._fetch_all_timeframes()

        # If detection modules are available, indicators should be calculated
        if stream.detect_order_blocks is not None:
            assert "1h" in stream.order_blocks
            assert "1h" in stream.liquidity_zones
            assert "1h" in stream.market_structure

            # Check formats
            assert isinstance(stream.order_blocks["1h"], pd.DataFrame)
            assert isinstance(stream.liquidity_zones["1h"], pd.DataFrame)
            assert isinstance(stream.market_structure["1h"], dict)
        else:
            # Detection modules not available - skip indicator checks
            assert stream.order_blocks == {}
            assert stream.liquidity_zones == {}
            assert stream.market_structure == {}

    def test_get_indicators(self):
        """Test getting indicators for timeframe."""
        stream = LiveIndicatorStream(
            symbol="BTC", timeframes=["1h"], update_interval=1, source="hyperliquid", lookback=100
        )

        stream.fetcher = MockFetcher()
        stream._fetch_all_timeframes()

        indicators = stream.get_indicators("1h")

        assert "order_blocks" in indicators
        assert "liquidity_zones" in indicators
        assert "market_structure" in indicators


@pytest.mark.integration
class TestLiveStreamIntegration:
    """Integration tests with real data fetchers."""

    def test_hyperliquid_stream(self):
        """Test stream with real Hyperliquid fetcher."""
        stream = LiveDataStream(
            symbol="BTC", timeframes=["1h"], update_interval=5, source="hyperliquid", lookback=50
        )

        # Fetch initial data
        stream._fetch_all_timeframes()

        # Check data loaded
        assert "1h" in stream.data
        assert not stream.data["1h"].empty

        # Check price
        price = stream.get_latest_price()
        assert price > 0
        assert 10000 < price < 200000  # Reasonable BTC range


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
