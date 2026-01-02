"""
Tests for visualization/fractal_dashboard.py
"""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from visualization.fractal_dashboard import FractalDashboard


@pytest.fixture
def sample_ohlcv_data():
    """Generate sample OHLCV data for testing."""
    dates = pd.date_range("2024-01-01", periods=1000, freq="15min")
    np.random.seed(42)

    # Generate realistic price movement
    close_prices = 50000 + np.cumsum(np.random.randn(1000) * 100)

    df = pd.DataFrame(
        {
            "timestamp": dates,
            "open": close_prices + np.random.randn(1000) * 50,
            "high": close_prices + np.abs(np.random.randn(1000) * 100),
            "low": close_prices - np.abs(np.random.randn(1000) * 100),
            "close": close_prices,
            "volume": np.random.randint(100, 1000, 1000),
        }
    )

    return df


@pytest.fixture
def sample_csv(sample_ohlcv_data):
    """Create temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        sample_ohlcv_data.to_csv(f.name, index=False)
        yield f.name
    Path(f.name).unlink()


class TestFractalDashboardInit:
    """Test FractalDashboard initialization."""

    def test_init_valid_params(self):
        """Test initialization with valid parameters."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["4h", "1h", "15m"])
        assert dashboard.pair == "BTC/USDT"
        assert dashboard.timeframes == ["4h", "1h", "15m"]
        assert dashboard.min_impulse_percent == 0.01
        assert dashboard.data == {}
        assert dashboard.order_blocks == {}

    def test_init_empty_timeframes(self):
        """Test initialization fails with empty timeframes."""
        with pytest.raises(ValueError, match="Timeframes must contain 1-3 entries"):
            FractalDashboard(pair="BTC/USDT", timeframes=[])

    def test_init_too_many_timeframes(self):
        """Test initialization fails with >3 timeframes."""
        with pytest.raises(ValueError, match="Timeframes must contain 1-3 entries"):
            FractalDashboard(pair="BTC/USDT", timeframes=["1m", "5m", "15m", "1h"])

    def test_init_custom_impulse_percent(self):
        """Test initialization with custom impulse percent."""
        dashboard = FractalDashboard(pair="ETH/USDT", timeframes=["1h"], min_impulse_percent=0.02)
        assert dashboard.min_impulse_percent == 0.02


class TestFractalDashboardLoadData:
    """Test data loading functionality."""

    def test_load_data_success(self, sample_csv):
        """Test successful data loading from CSV."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["4h", "1h"])
        dashboard.load_data(sample_csv)

        assert "4h" in dashboard.data
        assert "1h" in dashboard.data
        assert isinstance(dashboard.data["4h"], pd.DataFrame)
        assert len(dashboard.data["4h"]) > 0

    def test_load_data_missing_file(self):
        """Test error handling for missing file."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        with pytest.raises(FileNotFoundError):
            dashboard.load_data("/nonexistent/path.csv")

    def test_load_data_invalid_csv(self):
        """Test error handling for CSV with missing columns."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            # Write CSV with missing required columns
            f.write("timestamp,open,high\n")
            f.write("2024-01-01,100,105\n")
            temp_path = f.name

        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])

        with pytest.raises(ValueError, match="missing columns"):
            dashboard.load_data(temp_path)

        Path(temp_path).unlink()

    def test_load_data_unsupported_timeframe(self, sample_csv):
        """Test error handling for unsupported timeframe."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["2h"])  # Not in timeframe_map
        with pytest.raises(ValueError, match="Unsupported timeframe"):
            dashboard.load_data(sample_csv)

    def test_load_data_resampling(self, sample_csv):
        """Test data is correctly resampled to different timeframes."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h", "4h"])
        dashboard.load_data(sample_csv)

        # 4h should have fewer candles than 1h
        assert len(dashboard.data["4h"]) < len(dashboard.data["1h"])

        # All required columns should exist
        for tf in ["1h", "4h"]:
            assert all(
                col in dashboard.data[tf].columns
                for col in ["open", "high", "low", "close", "volume"]
            )


class TestFractalDashboardDetectPatterns:
    """Test pattern detection functionality."""

    def test_detect_patterns_success(self, sample_csv):
        """Test successful pattern detection."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()

        assert "1h" in dashboard.order_blocks
        bullish_ob, bearish_ob = dashboard.order_blocks["1h"]
        assert isinstance(bullish_ob, pd.DataFrame)
        assert isinstance(bearish_ob, pd.DataFrame)

    def test_detect_patterns_before_load_data(self):
        """Test error when calling detect_patterns before load_data."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        with pytest.raises(RuntimeError, match="Must call load_data"):
            dashboard.detect_patterns()

    def test_detect_patterns_all_timeframes(self, sample_csv):
        """Test patterns detected for all loaded timeframes."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["4h", "1h", "15m"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()

        assert len(dashboard.order_blocks) == 3
        for tf in ["4h", "1h", "15m"]:
            assert tf in dashboard.order_blocks


class TestFractalDashboardRender:
    """Test chart rendering functionality."""

    def test_render_success(self, sample_csv):
        """Test successful chart rendering."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()
        fig = dashboard.render()

        assert fig is not None
        assert len(fig.data) > 0  # Has traces

    def test_render_before_detect_patterns(self, sample_csv):
        """Test error when calling render before detect_patterns."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        dashboard.load_data(sample_csv)

        with pytest.raises(RuntimeError, match="Must call detect_patterns"):
            dashboard.render()

    def test_render_custom_height(self, sample_csv):
        """Test rendering with custom height."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()
        fig = dashboard.render(height=1000)

        assert fig.layout.height == 1000

    def test_render_multiple_timeframes(self, sample_csv):
        """Test rendering with 3 timeframes creates 3 subplots."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["4h", "1h", "15m"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()
        fig = dashboard.render()

        # Should have 3 candlestick traces (one per timeframe)
        candlestick_traces = [t for t in fig.data if t.type == "candlestick"]
        assert len(candlestick_traces) == 3


class TestFractalDashboardRowHeights:
    """Test row height calculation."""

    def test_row_heights_single_panel(self):
        """Test row heights for single timeframe."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        heights = dashboard._calculate_row_heights()
        assert heights == [1.0]

    def test_row_heights_two_panels(self):
        """Test row heights for two timeframes."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["4h", "1h"])
        heights = dashboard._calculate_row_heights()
        assert heights == [0.6, 0.4]
        assert sum(heights) == pytest.approx(1.0)

    def test_row_heights_three_panels(self):
        """Test row heights for three timeframes."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["4h", "1h", "15m"])
        heights = dashboard._calculate_row_heights()
        assert heights == [0.4, 0.3, 0.3]
        assert sum(heights) == pytest.approx(1.0)


class TestFractalDashboardConfidence:
    """Test confidence calculation functionality."""

    def test_calculate_confidence_success(self, sample_csv):
        """Test successful confidence calculation."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["4h", "1h"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()

        # Get first bullish OB on 1h
        bullish_ob, _ = dashboard.order_blocks["1h"]
        if len(bullish_ob) > 0:
            ob_index = bullish_ob.index[0]
            score, factors = dashboard.calculate_confidence("1h", ob_index, "bullish")

            assert isinstance(score, int)
            assert 0 <= score <= 100
            assert hasattr(factors, "calculate_score")

    def test_calculate_confidence_before_detect_patterns(self, sample_csv):
        """Test error when calling before detect_patterns."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        dashboard.load_data(sample_csv)

        with pytest.raises(RuntimeError, match="Must call detect_patterns"):
            dashboard.calculate_confidence("1h", pd.Timestamp("2024-01-01"), "bullish")

    def test_calculate_confidence_invalid_timeframe(self, sample_csv):
        """Test error with invalid timeframe."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()

        with pytest.raises(ValueError, match="Timeframe"):
            dashboard.calculate_confidence("4h", pd.Timestamp("2024-01-01"), "bullish")

    def test_calculate_confidence_invalid_ob_index(self, sample_csv):
        """Test error with non-existent OB."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()

        # Use a timestamp that definitely doesn't exist
        with pytest.raises(ValueError, match="Order block"):
            dashboard.calculate_confidence("1h", pd.Timestamp("2020-01-01"), "bullish")

    def test_render_with_confidence_panel(self, sample_csv):
        """Test rendering with confidence panel."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()

        bullish_ob, _ = dashboard.order_blocks["1h"]
        if len(bullish_ob) > 0:
            ob_index = bullish_ob.index[0]
            fig = dashboard.render(show_confidence_for=("1h", ob_index, "bullish"))

            assert fig is not None
            # Should have confidence annotation
            assert len(fig.layout.annotations) > 0


class TestFractalDashboardIntegration:
    """Integration tests for full workflow."""

    def test_full_workflow(self, sample_csv):
        """Test complete dashboard creation workflow."""
        # Initialize
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["4h", "1h"])

        # Load data
        dashboard.load_data(sample_csv)
        assert len(dashboard.data) == 2

        # Detect patterns
        dashboard.detect_patterns()
        assert len(dashboard.order_blocks) == 2

        # Render
        fig = dashboard.render(height=800)
        assert fig is not None
        assert fig.layout.height == 800

    def test_show_method_runs(self, sample_csv):
        """Test show() method doesn't raise errors."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["1h"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()

        # show() calls render() internally - should not raise
        # (Won't actually display in test environment)
        try:
            dashboard.show()
        except Exception as e:
            # Allow errors related to display (no browser in CI)
            if "display" not in str(e).lower():
                raise

    def test_full_workflow_with_confidence(self, sample_csv):
        """Test complete workflow including confidence panel."""
        dashboard = FractalDashboard(pair="BTC/USDT", timeframes=["4h", "1h", "15m"])
        dashboard.load_data(sample_csv)
        dashboard.detect_patterns()

        # Get strongest bullish OB
        bullish_4h, _ = dashboard.order_blocks["4h"]
        if len(bullish_4h) > 0:
            strongest = bullish_4h.nlargest(1, "retest_count").index[0]

            # Calculate confidence
            score, factors = dashboard.calculate_confidence("4h", strongest, "bullish")
            assert isinstance(score, int)

            # Render with confidence panel
            fig = dashboard.render(show_confidence_for=("4h", strongest, "bullish"))
            assert fig is not None
            assert len(fig.layout.annotations) > 0
