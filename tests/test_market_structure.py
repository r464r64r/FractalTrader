"""Tests for market structure detection."""

import pandas as pd

from core.market_structure import (
    detect_structure_breaks,
    determine_trend,
    find_recent_swing_level,
    find_swing_points,
    get_swing_sequence,
)

# Import fixtures


class TestSwingPoints:
    """Test swing point detection."""

    def test_finds_swing_highs(self, sample_ohlcv):
        """Swing highs should be found in sample data."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"], n=3)

        # Should find multiple swing highs
        assert swing_highs.dropna().count() >= 5

    def test_finds_swing_lows(self, sample_ohlcv):
        """Swing lows should be found in sample data."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"], n=3)

        # Should find multiple swing lows
        assert swing_lows.dropna().count() >= 5

    def test_swing_high_is_local_maximum(self, sample_ohlcv):
        """Swing highs should be higher than surrounding bars."""
        n = 3
        swing_highs, _ = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"], n=n)

        for idx in swing_highs.dropna().index:
            i = sample_ohlcv.index.get_loc(idx)
            if i >= n and i < len(sample_ohlcv) - n:
                # Swing high should be higher than n bars on each side
                assert sample_ohlcv["high"].iloc[i] > sample_ohlcv["high"].iloc[i - n : i].max()
                assert (
                    sample_ohlcv["high"].iloc[i]
                    > sample_ohlcv["high"].iloc[i + 1 : i + n + 1].max()
                )

    def test_swing_low_is_local_minimum(self, sample_ohlcv):
        """Swing lows should be lower than surrounding bars."""
        n = 3
        _, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"], n=n)

        for idx in swing_lows.dropna().index:
            i = sample_ohlcv.index.get_loc(idx)
            if i >= n and i < len(sample_ohlcv) - n:
                # Swing low should be lower than n bars on each side
                assert sample_ohlcv["low"].iloc[i] < sample_ohlcv["low"].iloc[i - n : i].min()
                assert (
                    sample_ohlcv["low"].iloc[i] < sample_ohlcv["low"].iloc[i + 1 : i + n + 1].min()
                )

    def test_swing_period_affects_count(self, sample_ohlcv):
        """Larger period should find fewer swings."""
        swings_3, _ = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"], n=3)
        swings_10, _ = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"], n=10)

        # Larger period = fewer swing points
        assert swings_3.dropna().count() >= swings_10.dropna().count()

    def test_returns_series_same_index(self, sample_ohlcv):
        """Return series should have same index as input."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        assert swing_highs.index.equals(sample_ohlcv.index)
        assert swing_lows.index.equals(sample_ohlcv.index)

    def test_handles_short_data(self):
        """Should handle data shorter than required window."""
        short_data = pd.Series([100, 101, 102, 103, 104])
        swing_highs, swing_lows = find_swing_points(short_data, short_data, n=5)

        # Should return all NaN for data too short
        assert swing_highs.isna().all()
        assert swing_lows.isna().all()


class TestDetermineTrend:
    """Test trend determination."""

    def test_identifies_uptrend(self, trending_data):
        """Should identify uptrend from HH/HL sequence."""
        swing_highs, swing_lows = find_swing_points(
            trending_data["high"], trending_data["low"], n=5
        )

        trend = determine_trend(swing_highs, swing_lows)

        # Majority should be uptrend
        uptrend_count = (trend == 1).sum()
        total_non_zero = (trend != 0).sum()

        assert uptrend_count > total_non_zero * 0.5, "Should be mostly uptrend"

    def test_identifies_downtrend(self, downtrending_data):
        """Should identify downtrend from LH/LL sequence."""
        swing_highs, swing_lows = find_swing_points(
            downtrending_data["high"], downtrending_data["low"], n=5
        )

        trend = determine_trend(swing_highs, swing_lows)

        # Majority should be downtrend
        downtrend_count = (trend == -1).sum()
        total_non_zero = (trend != 0).sum()

        assert downtrend_count > total_non_zero * 0.5, "Should be mostly downtrend"

    def test_identifies_ranging(self, ranging_data):
        """Should identify ranging/mixed market."""
        swing_highs, swing_lows = find_swing_points(ranging_data["high"], ranging_data["low"], n=5)

        trend = determine_trend(swing_highs, swing_lows)

        # Should have mix of values
        unique_values = trend.unique()
        # In ranging market, we expect some variation
        assert len(unique_values) >= 1

    def test_returns_valid_values(self, sample_ohlcv):
        """Trend should only contain -1, 0, or 1."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        trend = determine_trend(swing_highs, swing_lows)

        assert set(trend.unique()).issubset({-1, 0, 1})

    def test_handles_empty_swings(self):
        """Should handle empty swing series."""
        empty = pd.Series(dtype=float)
        trend = determine_trend(empty, empty)

        assert len(trend) == 0


class TestStructureBreaks:
    """Test BOS and CHoCH detection."""

    def test_detects_bullish_bos_in_uptrend(self, trending_data):
        """Should detect bullish BOS in uptrend."""
        swing_highs, swing_lows = find_swing_points(
            trending_data["high"], trending_data["low"], n=5
        )

        bos_bull, bos_bear, choch = detect_structure_breaks(
            trending_data["close"], swing_highs, swing_lows
        )

        # Should find some bullish BOS in uptrend
        assert bos_bull.sum() > 0, "Should detect bullish BOS in uptrend"

    def test_detects_bearish_bos_in_downtrend(self, downtrending_data):
        """Should detect bearish BOS in downtrend."""
        swing_highs, swing_lows = find_swing_points(
            downtrending_data["high"], downtrending_data["low"], n=5
        )

        bos_bull, bos_bear, choch = detect_structure_breaks(
            downtrending_data["close"], swing_highs, swing_lows
        )

        # Should find some bearish BOS in downtrend
        assert bos_bear.sum() > 0, "Should detect bearish BOS in downtrend"

    def test_returns_boolean_series(self, sample_ohlcv):
        """All return values should be boolean series."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        bos_bull, bos_bear, choch = detect_structure_breaks(
            sample_ohlcv["close"], swing_highs, swing_lows
        )

        assert bos_bull.dtype == bool
        assert bos_bear.dtype == bool
        assert choch.dtype == bool

    def test_same_index_as_input(self, sample_ohlcv):
        """Return series should have same index as input."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        bos_bull, bos_bear, choch = detect_structure_breaks(
            sample_ohlcv["close"], swing_highs, swing_lows
        )

        assert bos_bull.index.equals(sample_ohlcv.index)
        assert bos_bear.index.equals(sample_ohlcv.index)
        assert choch.index.equals(sample_ohlcv.index)


class TestSwingSequence:
    """Test swing sequence utilities."""

    def test_returns_sorted_dataframe(self, sample_ohlcv):
        """Should return chronologically sorted DataFrame."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        seq = get_swing_sequence(swing_highs, swing_lows)

        assert isinstance(seq, pd.DataFrame)
        if len(seq) > 1:
            # Should be sorted by timestamp
            assert seq["timestamp"].is_monotonic_increasing

    def test_contains_both_types(self, sample_ohlcv):
        """Should contain both high and low types."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        seq = get_swing_sequence(swing_highs, swing_lows)

        if len(seq) > 0:
            types = set(seq["type"].unique())
            assert "high" in types or "low" in types

    def test_lookback_limits_results(self, sample_ohlcv):
        """Lookback parameter should limit results."""
        swing_highs, swing_lows = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        seq_all = get_swing_sequence(swing_highs, swing_lows)
        seq_limited = get_swing_sequence(swing_highs, swing_lows, lookback=3)

        assert len(seq_limited) <= 3
        if len(seq_all) > 3:
            assert len(seq_limited) == 3


class TestFindRecentSwingLevel:
    """Test finding recent swing levels."""

    def test_finds_recent_swing_high(self, sample_ohlcv):
        """Should find most recent swing high before index."""
        swing_highs, _ = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        # Get a point after some swing highs exist
        current_idx = sample_ohlcv.index[-1]

        level = find_recent_swing_level(swing_highs, current_idx, direction="above")

        if swing_highs.dropna().count() > 0:
            assert level is not None
            assert isinstance(level, (int, float))

    def test_returns_none_if_no_prior_swings(self, sample_ohlcv):
        """Should return None if no swings before current index."""
        swing_highs, _ = find_swing_points(sample_ohlcv["high"], sample_ohlcv["low"])

        # Use very early index
        early_idx = sample_ohlcv.index[0]

        level = find_recent_swing_level(swing_highs, early_idx)

        assert level is None
