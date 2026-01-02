"""Tests for liquidity detection."""

import numpy as np
import pandas as pd

from core.liquidity import (
    detect_liquidity_sweep,
    find_equal_levels,
    find_liquidity_zones,
    get_nearest_liquidity,
)
from core.market_structure import find_swing_points

# Import fixtures


class TestFindEqualLevels:
    """Test equal high/low detection."""

    def test_detects_equal_highs(self):
        """Should detect clustered swing highs."""
        # Create data with clear equal highs around 100
        dates = pd.date_range("2024-01-01", periods=30, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        # Place swing highs at similar levels
        highs.iloc[5] = 100.0
        highs.iloc[10] = 100.05  # Within 0.1% tolerance
        highs.iloc[15] = 99.95  # Within 0.1% tolerance

        equal_highs, equal_lows = find_equal_levels(highs, lows, tolerance=0.001)

        # Should find the equal high cluster
        assert equal_highs.dropna().count() >= 1

    def test_detects_equal_lows(self):
        """Should detect clustered swing lows."""
        dates = pd.date_range("2024-01-01", periods=30, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        # Place swing lows at similar levels
        lows.iloc[5] = 95.0
        lows.iloc[12] = 95.02  # Within 0.1% tolerance
        lows.iloc[20] = 94.98  # Within 0.1% tolerance

        equal_highs, equal_lows = find_equal_levels(highs, lows, tolerance=0.001)

        # Should find the equal low cluster
        assert equal_lows.dropna().count() >= 1

    def test_tolerance_affects_clustering(self):
        """Tighter tolerance should find fewer clusters."""
        dates = pd.date_range("2024-01-01", periods=30, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        # Place swing highs
        highs.iloc[5] = 100.0
        highs.iloc[10] = 100.3  # 0.3% difference
        highs.iloc[15] = 100.1  # 0.1% difference

        # Loose tolerance should cluster all
        eq_h_loose, _ = find_equal_levels(highs, lows, tolerance=0.005)

        # Tight tolerance might not cluster
        eq_h_tight, _ = find_equal_levels(highs, lows, tolerance=0.0005)

        # Loose should find equal or more
        assert eq_h_loose.dropna().count() >= eq_h_tight.dropna().count()

    def test_requires_min_touches(self):
        """Should require minimum number of touches."""
        dates = pd.date_range("2024-01-01", periods=30, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        # Only 2 swing highs
        highs.iloc[5] = 100.0
        highs.iloc[15] = 100.05

        # With min_touches=2, should find cluster
        eq_h_2, _ = find_equal_levels(highs, lows, min_touches=2)

        # With min_touches=3, should not find cluster
        eq_h_3, _ = find_equal_levels(highs, lows, min_touches=3)

        assert eq_h_2.dropna().count() > 0
        assert eq_h_3.dropna().count() == 0

    def test_returns_same_index(self, sample_ohlcv):
        """Return series should have same index as input."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        equal_highs, equal_lows = find_equal_levels(swing_highs, swing_lows)

        assert equal_highs.index.equals(sample_ohlcv.index)
        assert equal_lows.index.equals(sample_ohlcv.index)


class TestDetectLiquiditySweep:
    """Test liquidity sweep detection."""

    def test_detects_bullish_sweep(self, liquidity_sweep_data):
        """Should detect bullish sweep (break below then reversal)."""
        # Setup: data has support around 98, breaks to 95, then reverses
        dates = liquidity_sweep_data.index
        liquidity_levels = pd.Series(np.nan, index=dates)
        liquidity_levels.iloc[3] = 98.0  # Support level

        sweeps = detect_liquidity_sweep(
            liquidity_sweep_data["high"],
            liquidity_sweep_data["low"],
            liquidity_sweep_data["close"],
            liquidity_levels,
            reversal_bars=3,
            direction="bullish",
        )

        # Should detect the sweep when price closes back above 98
        assert sweeps.sum() >= 1

    def test_detects_bearish_sweep(self):
        """Should detect bearish sweep (break above then reversal)."""
        dates = pd.date_range("2024-01-01", periods=15, freq="1h")

        # Create bearish sweep pattern: resistance at 100, break above, then reject
        data = pd.DataFrame(
            {
                "high": [99, 99, 99, 99, 102, 98, 97, 96, 95, 94, 93, 92, 91, 90, 89],
                "low": [97, 97, 97, 97, 99, 96, 95, 94, 93, 92, 91, 90, 89, 88, 87],
                "close": [98, 98, 98, 98, 100, 97, 96, 95, 94, 93, 92, 91, 90, 89, 88],
            },
            index=dates,
        )

        liquidity_levels = pd.Series(np.nan, index=dates)
        liquidity_levels.iloc[2] = 99.0  # Resistance level

        sweeps = detect_liquidity_sweep(
            data["high"],
            data["low"],
            data["close"],
            liquidity_levels,
            reversal_bars=3,
            direction="bearish",
        )

        # Should detect the sweep when price closes back below 99
        assert sweeps.sum() >= 1

    def test_reversal_bars_limit(self):
        """Should not detect sweep if reversal takes too long."""
        dates = pd.date_range("2024-01-01", periods=20, freq="1h")

        # Slow reversal (takes 5+ bars) - bullish sweep only
        # Highs stay below the level to avoid triggering bearish sweep
        data = pd.DataFrame(
            {
                "high": [97] * 5
                + [97, 97, 97, 97, 97, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
                "low": [95] * 5
                + [92, 93, 93, 93, 94, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
                "close": [96] * 5
                + [93, 93, 94, 94, 95, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            },
            index=dates,
        )

        liquidity_levels = pd.Series(np.nan, index=dates)
        liquidity_levels.iloc[3] = 98.0

        # With tight reversal window - bullish direction only
        sweeps_tight = detect_liquidity_sweep(
            data["high"],
            data["low"],
            data["close"],
            liquidity_levels,
            reversal_bars=2,
            direction="bullish",
        )

        # Should not detect sweep with tight reversal bars
        # Sweep starts at bar 5 (low=92 < 98), but reversal (close > 98) doesn't happen until bar 10
        assert sweeps_tight.sum() == 0

    def test_direction_filter(self):
        """Direction parameter should filter sweep type."""
        dates = pd.date_range("2024-01-01", periods=10, freq="1h")

        # Bullish sweep pattern - keep highs below level to avoid bearish trigger
        data = pd.DataFrame(
            {
                "high": [97, 97, 97, 96, 103, 105, 106, 107, 108, 109],
                "low": [95, 95, 95, 92, 99, 101, 102, 103, 104, 105],
                "close": [96, 96, 96, 93, 102, 104, 105, 106, 107, 108],
            },
            index=dates,
        )

        liquidity_levels = pd.Series(np.nan, index=dates)
        liquidity_levels.iloc[1] = 98.0  # Level at 98

        bullish = detect_liquidity_sweep(
            data["high"], data["low"], data["close"], liquidity_levels, direction="bullish"
        )

        bearish = detect_liquidity_sweep(
            data["high"], data["low"], data["close"], liquidity_levels, direction="bearish"
        )

        # Bullish sweep should be detected (low[3]=92 < 98, then close[4]=102 > 98)
        assert bullish.sum() >= 1
        # Since highs never break above 98 until after reversal, bearish should not trigger
        assert bearish.sum() == 0

    def test_returns_boolean_series(self, sample_ohlcv):
        """Should return boolean series."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        sweeps = detect_liquidity_sweep(
            sample_ohlcv["high"], sample_ohlcv["low"], sample_ohlcv["close"], swing_lows
        )

        assert sweeps.dtype == bool


class TestFindLiquidityZones:
    """Test liquidity zone detection."""

    def test_returns_dataframes(self):
        """Should return DataFrames with correct columns."""
        # Create data with clear clustered levels
        dates = pd.date_range("2024-01-01", periods=30, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        # Create clusters
        highs.iloc[5] = 100.0
        highs.iloc[10] = 100.05
        highs.iloc[15] = 99.95

        high_zones, low_zones = find_liquidity_zones(highs, lows, tolerance=0.001)

        assert isinstance(high_zones, pd.DataFrame)
        assert isinstance(low_zones, pd.DataFrame)

        expected_cols = ["level_price", "first_touch", "last_touch", "touch_count"]
        for col in expected_cols:
            assert col in high_zones.columns
            assert col in low_zones.columns

    def test_touch_count_accurate(self):
        """Touch count should reflect actual cluster size."""
        dates = pd.date_range("2024-01-01", periods=30, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        # Create cluster of 3 highs
        highs.iloc[5] = 100.0
        highs.iloc[10] = 100.05
        highs.iloc[15] = 99.95

        high_zones, _ = find_liquidity_zones(highs, lows, tolerance=0.001)

        if len(high_zones) > 0:
            assert high_zones.iloc[0]["touch_count"] == 3


class TestGetNearestLiquidity:
    """Test nearest liquidity level finder."""

    def test_finds_nearest_above(self):
        """Should find nearest level above current price."""
        dates = pd.date_range("2024-01-01", periods=20, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        highs.iloc[5] = 105.0
        highs.iloc[10] = 110.0

        result = get_nearest_liquidity(
            price=100.0,
            swing_highs=highs,
            swing_lows=lows,
            current_idx=dates[15],
            direction="above",
        )

        assert result is not None
        assert result["price"] == 105.0  # Nearest above
        assert result["type"] == "swing_high"

    def test_finds_nearest_below(self):
        """Should find nearest level below current price."""
        dates = pd.date_range("2024-01-01", periods=20, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        lows.iloc[5] = 90.0
        lows.iloc[10] = 95.0

        result = get_nearest_liquidity(
            price=100.0,
            swing_highs=highs,
            swing_lows=lows,
            current_idx=dates[15],
            direction="below",
        )

        assert result is not None
        assert result["price"] == 95.0  # Nearest below
        assert result["type"] == "swing_low"

    def test_returns_none_if_no_levels(self):
        """Should return None if no levels found."""
        dates = pd.date_range("2024-01-01", periods=20, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        result = get_nearest_liquidity(
            price=100.0, swing_highs=highs, swing_lows=lows, current_idx=dates[15]
        )

        assert result is None

    def test_only_considers_prior_levels(self):
        """Should only consider levels before current index."""
        dates = pd.date_range("2024-01-01", periods=20, freq="1h")
        highs = pd.Series(np.nan, index=dates)
        lows = pd.Series(np.nan, index=dates)

        # Level after current_idx
        highs.iloc[15] = 105.0

        result = get_nearest_liquidity(
            price=100.0,
            swing_highs=highs,
            swing_lows=lows,
            current_idx=dates[10],  # Before the high
            direction="above",
        )

        assert result is None  # Future level should not be found
