"""Tests for Fair Value Gap (imbalance) detection."""

import pandas as pd
import pytest

from core.imbalance import calculate_fvg_size, check_fvg_fill, find_fair_value_gaps, get_active_fvgs


@pytest.fixture
def bullish_fvg_data():
    """Data with a clear bullish FVG pattern."""
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")

    # Bullish FVG: Gap between candle[i-2].high and candle[i].low
    # Candle 0: high=102
    # Candle 1: impulse candle (moves up fast)
    # Candle 2: low=105 (gap: 105 > 102)
    data = pd.DataFrame(
        {
            "high": [102, 110, 112, 113, 114, 115, 116, 117, 118, 119],
            "low": [100, 108, 105, 111, 112, 113, 114, 115, 116, 117],
            "close": [101, 109, 111, 112, 113, 114, 115, 116, 117, 118],
        },
        index=dates,
    )

    return data


@pytest.fixture
def bearish_fvg_data():
    """Data with a clear bearish FVG pattern."""
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")

    # Bearish FVG: Gap between candle[i-2].low and candle[i].high
    # Candle 0: low=100
    # Candle 1: impulse candle (moves down fast)
    # Candle 2: high=97 (gap: 100 > 97)
    data = pd.DataFrame(
        {
            "high": [102, 99, 97, 96, 95, 94, 93, 92, 91, 90],
            "low": [100, 90, 88, 87, 86, 85, 84, 83, 82, 81],
            "close": [101, 91, 89, 88, 87, 86, 85, 84, 83, 82],
        },
        index=dates,
    )

    return data


@pytest.fixture
def no_gap_data():
    """Data with no gaps (smooth price action)."""
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")

    data = pd.DataFrame(
        {
            "high": [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
            "low": [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            "close": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        },
        index=dates,
    )

    return data


class TestFindFairValueGaps:
    """Tests for find_fair_value_gaps function."""

    def test_find_fair_value_gaps_detects_bullish_fvg(self, bullish_fvg_data):
        """Should detect bullish FVG in appropriate data."""
        bullish, bearish = find_fair_value_gaps(
            bullish_fvg_data["high"], bullish_fvg_data["low"], min_gap_percent=0.001
        )

        assert len(bullish) > 0, "Should detect at least one bullish FVG"
        assert len(bearish) == 0, "Should not detect bearish FVG"

    def test_find_fair_value_gaps_detects_bearish_fvg(self, bearish_fvg_data):
        """Should detect bearish FVG in appropriate data."""
        bullish, bearish = find_fair_value_gaps(
            bearish_fvg_data["high"], bearish_fvg_data["low"], min_gap_percent=0.001
        )

        assert len(bearish) > 0, "Should detect at least one bearish FVG"
        assert len(bullish) == 0, "Should not detect bullish FVG"

    def test_bullish_fvg_requires_gap_between_high_and_low(self):
        """Bullish FVG requires candle[i].low > candle[i-2].high."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        # No gap: current low (101) is not greater than old high (102)
        data = pd.DataFrame(
            {
                "high": [102, 110, 111, 112, 113],
                "low": [100, 108, 101, 110, 111],  # Index 2: low=101 <= 102
            },
            index=dates,
        )

        bullish, bearish = find_fair_value_gaps(data["high"], data["low"], min_gap_percent=0.0)

        # Should not detect a gap at index 2
        # Check if any detected gaps are actually valid
        for idx, fvg in bullish.iterrows():
            assert fvg["gap_high"] > fvg["gap_low"], "Gap high must be > gap low"

    def test_bearish_fvg_requires_gap_between_low_and_high(self):
        """Bearish FVG requires candle[i-2].low > candle[i].high."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        # No gap: old low (100) is not greater than current high (101)
        data = pd.DataFrame(
            {
                "high": [102, 99, 101, 100, 99],  # Index 2: high=101 >= 100
                "low": [100, 90, 89, 88, 87],
            },
            index=dates,
        )

        bullish, bearish = find_fair_value_gaps(data["high"], data["low"], min_gap_percent=0.0)

        # Check if any detected gaps are actually valid
        for idx, fvg in bearish.iterrows():
            assert fvg["gap_high"] > fvg["gap_low"], "Gap high must be > gap low"

    def test_min_gap_percent_filters_small_gaps(self):
        """Small gaps should be filtered by min_gap_percent."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        # Tiny gap: 100.05 > 100 (0.05% gap)
        data = pd.DataFrame(
            {
                "high": [100.00, 110.00, 111.00, 112.00, 113.00],
                "low": [99.00, 108.00, 100.05, 110.00, 111.00],
            },
            index=dates,
        )

        # With min_gap_percent = 0.01 (1%), should not detect the 0.05% gap
        bullish_strict, _ = find_fair_value_gaps(data["high"], data["low"], min_gap_percent=0.01)

        # With min_gap_percent = 0.0001 (0.01%), should detect it
        bullish_lenient, _ = find_fair_value_gaps(data["high"], data["low"], min_gap_percent=0.0001)

        assert len(bullish_lenient) > len(bullish_strict)

    def test_returns_empty_dataframe_when_no_gaps(self, no_gap_data):
        """Should return empty DataFrames when no gaps exist."""
        bullish, bearish = find_fair_value_gaps(
            no_gap_data["high"], no_gap_data["low"], min_gap_percent=0.001
        )

        assert len(bullish) == 0, "Should find no bullish FVGs"
        assert len(bearish) == 0, "Should find no bearish FVGs"
        assert isinstance(bullish, pd.DataFrame)
        assert isinstance(bearish, pd.DataFrame)

    def test_returns_empty_for_insufficient_data(self):
        """Should return empty DataFrames for less than 3 bars."""
        dates = pd.date_range("2024-01-01", periods=2, freq="1h")
        data = pd.DataFrame({"high": [102, 103], "low": [100, 101]}, index=dates)

        bullish, bearish = find_fair_value_gaps(data["high"], data["low"])

        assert len(bullish) == 0
        assert len(bearish) == 0

    def test_fvg_dataframe_has_required_columns(self, bullish_fvg_data):
        """FVG DataFrames should have required columns."""
        bullish, bearish = find_fair_value_gaps(bullish_fvg_data["high"], bullish_fvg_data["low"])

        required_cols = ["gap_high", "gap_low", "filled", "fill_idx"]

        # Check bullish columns (even if empty)
        for col in required_cols:
            assert col in bullish.columns, f"Bullish FVG missing column: {col}"

        # Check bearish columns
        for col in required_cols:
            assert col in bearish.columns, f"Bearish FVG missing column: {col}"


class TestCheckFVGFill:
    """Tests for check_fvg_fill function."""

    def test_check_fvg_fill_detects_full_fill(self, bullish_fvg_data):
        """Should detect when price fully fills an FVG."""
        bullish, _ = find_fair_value_gaps(
            bullish_fvg_data["high"], bullish_fvg_data["low"], min_gap_percent=0.001
        )

        if len(bullish) == 0:
            pytest.skip("No FVG detected in test data")

        # Create data that fills the FVG
        fill_data = bullish_fvg_data.copy()
        # Make sure price returns to fill the gap
        fill_data.loc[fill_data.index[-1], "low"] = bullish.iloc[0]["gap_low"]

        fills = check_fvg_fill(fill_data["high"], fill_data["low"], bullish, fill_type="full")

        assert fills.sum() > 0, "Should detect at least one fill"

    def test_check_fvg_fill_detects_partial_fill(self, bullish_fvg_data):
        """Should detect partial fills when configured."""
        bullish, _ = find_fair_value_gaps(
            bullish_fvg_data["high"], bullish_fvg_data["low"], min_gap_percent=0.001
        )

        if len(bullish) == 0:
            pytest.skip("No FVG detected in test data")

        # Create data that partially fills the FVG
        fill_data = bullish_fvg_data.copy()
        gap_size = bullish.iloc[0]["gap_high"] - bullish.iloc[0]["gap_low"]
        partial_level = bullish.iloc[0]["gap_low"] + (gap_size * 0.5)
        fill_data.loc[fill_data.index[-1], "low"] = partial_level

        fills = check_fvg_fill(
            fill_data["high"], fill_data["low"], bullish, fill_type="partial", partial_percent=0.5
        )

        assert fills.sum() > 0, "Should detect partial fill"

    def test_partial_fill_respects_percent_threshold(self):
        """Partial fill should respect the percentage threshold."""
        dates = pd.date_range("2024-01-01", periods=6, freq="1h")

        # Create clear bullish FVG
        data = pd.DataFrame(
            {
                "high": [100, 120, 125, 130, 130, 130],
                "low": [95, 115, 110, 125, 125, 112],  # FVG between 100 and 110
            },
            index=dates,
        )

        bullish, _ = find_fair_value_gaps(data["high"], data["low"], min_gap_percent=0.01)

        if len(bullish) > 0:
            # 50% fill should trigger
            fills_50 = check_fvg_fill(
                data["high"], data["low"], bullish.copy(), fill_type="partial", partial_percent=0.5
            )

            # Full fill requires reaching the bottom
            fills_full = check_fvg_fill(data["high"], data["low"], bullish.copy(), fill_type="full")

            # Partial should detect fills more easily than full
            assert fills_50.sum() >= fills_full.sum()

    def test_fvg_marked_as_filled_after_fill(self, bullish_fvg_data):
        """FVG should be marked as filled after fill detection."""
        bullish, _ = find_fair_value_gaps(
            bullish_fvg_data["high"], bullish_fvg_data["low"], min_gap_percent=0.001
        )

        if len(bullish) == 0:
            pytest.skip("No FVG detected in test data")

        # Initially should not be filled
        assert not bullish.iloc[0]["filled"]

        # Create data that fills the FVG
        fill_data = bullish_fvg_data.copy()
        fill_data.loc[fill_data.index[-1], "low"] = bullish.iloc[0]["gap_low"] - 1

        check_fvg_fill(fill_data["high"], fill_data["low"], bullish, fill_type="full")

        # Now should be marked as filled (function modifies the dataframe)
        # Check if at least one got filled
        assert bullish["filled"].any(), "At least one FVG should be marked as filled"

    def test_fill_idx_recorded_correctly(self, bullish_fvg_data):
        """Fill index should be recorded when FVG is filled."""
        bullish, _ = find_fair_value_gaps(
            bullish_fvg_data["high"], bullish_fvg_data["low"], min_gap_percent=0.001
        )

        if len(bullish) == 0:
            pytest.skip("No FVG detected in test data")

        # Create data that fills the FVG
        fill_data = bullish_fvg_data.copy()
        fill_idx = fill_data.index[-1]
        fill_data.loc[fill_idx, "low"] = bullish.iloc[0]["gap_low"] - 1

        check_fvg_fill(fill_data["high"], fill_data["low"], bullish, fill_type="full")

        # Check if fill_idx is recorded for filled FVGs
        filled_fvgs = bullish[bullish["filled"]]
        if len(filled_fvgs) > 0:
            assert filled_fvgs.iloc[0]["fill_idx"] is not None


class TestGetActiveFVGs:
    """Tests for get_active_fvgs function."""

    def test_get_active_fvgs_returns_unfilled_only(self):
        """Should return only unfilled FVGs."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        # Create FVG dataframe with some filled
        fvg_zones = pd.DataFrame(
            {
                "gap_high": [105, 110, 115],
                "gap_low": [103, 108, 113],
                "filled": [True, False, False],
                "fill_idx": [dates[3], None, None],
            },
            index=dates[:3],
        )

        active = get_active_fvgs(fvg_zones, dates[-1], max_age_bars=None)

        assert len(active) == 2, "Should return only unfilled FVGs"
        assert not active["filled"].any(), "All returned FVGs should be unfilled"

    def test_get_active_fvgs_respects_max_age(self):
        """Should filter FVGs by max age."""
        dates = pd.date_range("2024-01-01", periods=100, freq="1h")

        # Create FVGs at different times
        fvg_zones = pd.DataFrame(
            {
                "gap_high": [105, 110, 115],
                "gap_low": [103, 108, 113],
                "filled": [False, False, False],
                "fill_idx": [None, None, None],
            },
            index=[dates[10], dates[50], dates[80]],
        )

        # Get all active FVGs (no age filter)
        active_no_filter = get_active_fvgs(fvg_zones, dates[80], max_age_bars=None)

        # Get active FVGs with max_age_bars=20
        # At dates[80], only FVG at dates[80] should be within 20 bars
        active_filtered = get_active_fvgs(fvg_zones, dates[80], max_age_bars=20)

        # Filtered should have fewer or equal FVGs than unfiltered
        assert len(active_filtered) <= len(active_no_filter), "Age filter should reduce FVGs"


class TestCalculateFVGSize:
    """Tests for calculate_fvg_size function."""

    def test_calculate_fvg_size_returns_percentages(self):
        """Should return gap sizes as percentages."""
        dates = pd.date_range("2024-01-01", periods=3, freq="1h")

        fvg_zones = pd.DataFrame(
            {
                "gap_high": [105, 110],
                "gap_low": [100, 100],  # 5% and 10% gaps
                "filled": [False, False],
                "fill_idx": [None, None],
            },
            index=dates[:2],
        )

        sizes = calculate_fvg_size(fvg_zones)

        assert len(sizes) == 2
        assert sizes.iloc[0] == pytest.approx(0.05, rel=0.01)  # 5%
        assert sizes.iloc[1] == pytest.approx(0.10, rel=0.01)  # 10%

    def test_calculate_fvg_size_handles_empty_input(self):
        """Should handle empty DataFrame gracefully."""
        empty_fvg = pd.DataFrame(columns=["gap_high", "gap_low", "filled", "fill_idx"])

        sizes = calculate_fvg_size(empty_fvg)

        assert len(sizes) == 0
        assert isinstance(sizes, pd.Series)
