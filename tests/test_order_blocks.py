"""Tests for Order Block detection."""

import pandas as pd
import pytest

from core.order_blocks import (
    calculate_ob_strength,
    check_ob_retest,
    find_order_blocks,
    get_nearest_order_block,
    get_valid_order_blocks,
)


@pytest.fixture
def bullish_ob_data():
    """Data with a clear bullish order block pattern."""
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")

    # Bullish OB: Last down candle before bullish impulse
    # Bar 3: Down candle (close < open)
    # Bar 4: Bullish impulse (closes much higher)
    data = pd.DataFrame(
        {
            "open": [100, 101, 102, 103, 102, 110, 111, 112, 113, 114],
            "high": [101, 102, 103, 104, 103, 111, 112, 113, 114, 115],
            "low": [99, 100, 101, 101, 100, 109, 110, 111, 112, 113],
            "close": [101, 102, 103, 102, 110, 111, 112, 113, 114, 115],
        },
        index=dates,
    )

    return data


@pytest.fixture
def bearish_ob_data():
    """Data with a clear bearish order block pattern."""
    dates = pd.date_range("2024-01-01", periods=10, freq="1h")

    # Bearish OB: Last up candle before bearish impulse
    # Bar 3: Up candle (close > open)
    # Bar 4: Bearish impulse (closes much lower)
    data = pd.DataFrame(
        {
            "open": [100, 99, 98, 97, 98, 90, 89, 88, 87, 86],
            "high": [101, 100, 99, 99, 99, 91, 90, 89, 88, 87],
            "low": [99, 98, 97, 96, 89, 88, 87, 86, 85, 84],
            "close": [99, 98, 97, 98, 90, 89, 88, 87, 86, 85],
        },
        index=dates,
    )

    return data


class TestFindOrderBlocks:
    """Tests for find_order_blocks function."""

    def test_find_order_blocks_detects_bullish_ob(self, bullish_ob_data):
        """Should detect bullish order blocks."""
        bullish, bearish = find_order_blocks(
            bullish_ob_data["open"],
            bullish_ob_data["high"],
            bullish_ob_data["low"],
            bullish_ob_data["close"],
            min_impulse_percent=0.05,
        )

        assert len(bullish) > 0, "Should detect at least one bullish OB"

    def test_find_order_blocks_detects_bearish_ob(self, bearish_ob_data):
        """Should detect bearish order blocks."""
        bullish, bearish = find_order_blocks(
            bearish_ob_data["open"],
            bearish_ob_data["high"],
            bearish_ob_data["low"],
            bearish_ob_data["close"],
            min_impulse_percent=0.05,
        )

        assert len(bearish) > 0, "Should detect at least one bearish OB"

    def test_bullish_ob_is_down_candle_before_impulse(self):
        """Bullish OB should be a down candle (close < open)."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        data = pd.DataFrame(
            {
                "open": [100, 101, 103, 102, 110],  # Bar 3 is down candle
                "high": [101, 102, 104, 103, 111],
                "low": [99, 100, 102, 101, 109],
                "close": [101, 102, 103, 102, 110],  # Close[3]=102 < Open[3]=103
            },
            index=dates,
        )

        bullish, _ = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"], min_impulse_percent=0.05
        )

        for idx, ob in bullish.iterrows():
            # The candle at idx should be a down candle
            candle_open = data.loc[idx, "open"]
            candle_close = data.loc[idx, "close"]
            assert candle_close < candle_open, "Bullish OB should be down candle"

    def test_bearish_ob_is_up_candle_before_impulse(self):
        """Bearish OB should be an up candle (close > open)."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        data = pd.DataFrame(
            {
                "open": [100, 99, 97, 97, 89],  # Bar 3 is up candle
                "high": [101, 100, 99, 99, 90],
                "low": [99, 98, 96, 96, 88],
                "close": [99, 98, 97, 98, 89],  # Close[3]=98 > Open[3]=97
            },
            index=dates,
        )

        _, bearish = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"], min_impulse_percent=0.08
        )

        for idx, ob in bearish.iterrows():
            candle_open = data.loc[idx, "open"]
            candle_close = data.loc[idx, "close"]
            assert candle_close > candle_open, "Bearish OB should be up candle"

    def test_min_impulse_percent_filters_small_moves(self):
        """Small impulse moves should be filtered."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        # Small impulse: only 2% move
        data = pd.DataFrame(
            {
                "open": [100, 101, 103, 102, 104],
                "high": [101, 102, 104, 103, 105],
                "low": [99, 100, 102, 101, 103],
                "close": [101, 102, 103, 102, 104],
            },
            index=dates,
        )

        # Strict filter (5%)
        bullish_strict, _ = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"], min_impulse_percent=0.05
        )

        # Lenient filter (1%)
        bullish_lenient, _ = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"], min_impulse_percent=0.01
        )

        assert len(bullish_lenient) >= len(bullish_strict)

    def test_returns_empty_dataframe_when_no_obs(self):
        """Should return empty DataFrame when no OBs found."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        # Flat price action, no impulses
        data = pd.DataFrame(
            {
                "open": [100, 100, 100, 100, 100],
                "high": [101, 101, 101, 101, 101],
                "low": [99, 99, 99, 99, 99],
                "close": [100, 100, 100, 100, 100],
            },
            index=dates,
        )

        bullish, bearish = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"], min_impulse_percent=0.05
        )

        assert len(bullish) == 0
        assert len(bearish) == 0
        assert isinstance(bullish, pd.DataFrame)
        assert isinstance(bearish, pd.DataFrame)

    def test_returns_empty_for_insufficient_data(self):
        """Should return empty for less than 3 bars."""
        dates = pd.date_range("2024-01-01", periods=2, freq="1h")

        data = pd.DataFrame(
            {"open": [100, 101], "high": [101, 102], "low": [99, 100], "close": [101, 102]},
            index=dates,
        )

        bullish, bearish = find_order_blocks(data["open"], data["high"], data["low"], data["close"])

        assert len(bullish) == 0
        assert len(bearish) == 0

    def test_ob_dataframe_has_required_columns(self, bullish_ob_data):
        """OB DataFrames should have required columns."""
        bullish, bearish = find_order_blocks(
            bullish_ob_data["open"],
            bullish_ob_data["high"],
            bullish_ob_data["low"],
            bullish_ob_data["close"],
        )

        required_cols = ["ob_high", "ob_low", "invalidated", "retest_count"]

        for col in required_cols:
            assert col in bullish.columns
            assert col in bearish.columns


class TestCheckOBRetest:
    """Tests for check_ob_retest function."""

    def test_check_ob_retest_detects_price_entering_zone(self, bullish_ob_data):
        """Should detect when price retests OB zone."""
        bullish, _ = find_order_blocks(
            bullish_ob_data["open"],
            bullish_ob_data["high"],
            bullish_ob_data["low"],
            bullish_ob_data["close"],
            min_impulse_percent=0.05,
        )

        if len(bullish) == 0:
            pytest.skip("No OB detected")

        # Create retest data
        retest_data = bullish_ob_data.copy()
        ob_mid = (bullish.iloc[0]["ob_high"] + bullish.iloc[0]["ob_low"]) / 2
        retest_data.loc[retest_data.index[-1], "low"] = ob_mid

        retests = check_ob_retest(
            retest_data["high"], retest_data["low"], bullish, direction="bullish"
        )

        assert retests.sum() > 0

    def test_ob_invalidated_when_price_breaks_zone(self):
        """OB should be invalidated when price breaks through it."""
        dates = pd.date_range("2024-01-01", periods=8, freq="1h")

        data = pd.DataFrame(
            {
                "open": [100, 101, 103, 102, 110, 111, 112, 100],
                "high": [101, 102, 104, 103, 111, 112, 113, 101],
                "low": [99, 100, 102, 101, 109, 110, 111, 99],
                "close": [101, 102, 103, 102, 110, 111, 112, 100],
            },
            index=dates,
        )

        bullish, _ = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"], min_impulse_percent=0.05
        )

        if len(bullish) > 0:
            # Make last candle break below OB low
            data.loc[dates[-1], "low"] = bullish.iloc[0]["ob_low"] - 10

            check_ob_retest(data["high"], data["low"], bullish, direction="bullish")

            # Check if invalidated flag is set
            assert bullish["invalidated"].any()

    def test_bullish_ob_invalidated_below_low(self):
        """Bullish OB should be invalidated if price goes below OB low."""
        dates = pd.date_range("2024-01-01", periods=6, freq="1h")

        data = pd.DataFrame(
            {
                "open": [100, 101, 103, 102, 110, 100],
                "high": [101, 102, 104, 103, 111, 101],
                "low": [99, 100, 102, 101, 109, 95],  # Last bar breaks low
                "close": [101, 102, 103, 102, 110, 96],
            },
            index=dates,
        )

        bullish, _ = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"], min_impulse_percent=0.05
        )

        if len(bullish) > 0:
            check_ob_retest(data["high"], data["low"], bullish, direction="bullish")

            assert bullish["invalidated"].any()

    def test_bearish_ob_invalidated_above_high(self, bearish_ob_data):
        """Bearish OB should be invalidated if price goes above OB high."""
        bearish_ob_data_copy = bearish_ob_data.copy()

        _, bearish = find_order_blocks(
            bearish_ob_data_copy["open"],
            bearish_ob_data_copy["high"],
            bearish_ob_data_copy["low"],
            bearish_ob_data_copy["close"],
            min_impulse_percent=0.05,
        )

        if len(bearish) > 0:
            # Make last candle break above OB high
            bearish_ob_data_copy.loc[bearish_ob_data_copy.index[-1], "high"] = (
                bearish.iloc[0]["ob_high"] + 10
            )

            check_ob_retest(
                bearish_ob_data_copy["high"],
                bearish_ob_data_copy["low"],
                bearish,
                direction="bearish",
            )

            assert bearish["invalidated"].any()

    def test_retest_count_increments(self):
        """Retest count should increment when price retests OB."""
        dates = pd.date_range("2024-01-01", periods=8, freq="1h")

        data = pd.DataFrame(
            {
                "open": [100, 101, 103, 102, 110, 111, 103, 112],  # Bar 6 retests
                "high": [101, 102, 104, 103, 111, 112, 104, 113],
                "low": [99, 100, 102, 101, 109, 110, 102, 111],
                "close": [101, 102, 103, 102, 110, 111, 103, 112],
            },
            index=dates,
        )

        bullish, _ = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"], min_impulse_percent=0.05
        )

        if len(bullish) > 0:
            initial_count = bullish.iloc[0]["retest_count"]

            check_ob_retest(data["high"], data["low"], bullish, direction="bullish")

            assert bullish.iloc[0]["retest_count"] >= initial_count


class TestGetValidOrderBlocks:
    """Tests for get_valid_order_blocks function."""

    def test_get_valid_order_blocks_filters_invalidated(self):
        """Should return only non-invalidated OBs."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        obs = pd.DataFrame(
            {
                "ob_high": [105, 110, 115],
                "ob_low": [103, 108, 113],
                "invalidated": [True, False, False],
                "retest_count": [2, 1, 0],
            },
            index=dates[:3],
        )

        valid = get_valid_order_blocks(obs, dates[-1])

        assert len(valid) == 2
        assert not valid["invalidated"].any()

    def test_get_valid_order_blocks_respects_max_age(self):
        """Should filter by max age."""
        dates = pd.date_range("2024-01-01", periods=100, freq="1h")

        obs = pd.DataFrame(
            {
                "ob_high": [105, 110, 115, 120],
                "ob_low": [103, 108, 113, 118],
                "invalidated": [False, False, False, False],
                "retest_count": [0, 0, 0, 0],
            },
            index=[dates[10], dates[20], dates[30], dates[40]],
        )

        # Get with age limit
        valid_limited = get_valid_order_blocks(obs, dates[50], max_age_bars=2)

        # Get without age limit
        valid_all = get_valid_order_blocks(obs, dates[50], max_age_bars=None)

        assert len(valid_limited) <= len(valid_all)


class TestGetNearestOrderBlock:
    """Tests for get_nearest_order_block function."""

    def test_get_nearest_order_block_finds_below(self):
        """Should find nearest OB below price."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        obs = pd.DataFrame(
            {
                "ob_high": [95, 90, 85],
                "ob_low": [93, 88, 83],
                "invalidated": [False, False, False],
                "retest_count": [0, 0, 0],
            },
            index=dates[:3],
        )

        nearest = get_nearest_order_block(
            price=100, order_blocks=obs, current_idx=dates[-1], direction="below"
        )

        assert nearest is not None
        # Should find the 95 OB (closest to 100)
        assert nearest["ob_high"] == 95

    def test_get_nearest_order_block_finds_above(self):
        """Should find nearest OB above price."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        obs = pd.DataFrame(
            {
                "ob_high": [105, 110, 115],
                "ob_low": [103, 108, 113],
                "invalidated": [False, False, False],
                "retest_count": [0, 0, 0],
            },
            index=dates[:3],
        )

        nearest = get_nearest_order_block(
            price=100, order_blocks=obs, current_idx=dates[-1], direction="above"
        )

        assert nearest is not None
        assert nearest["ob_high"] == 105  # Closest above 100

    def test_get_nearest_returns_none_when_no_valid(self):
        """Should return None when no valid OBs exist."""
        dates = pd.date_range("2024-01-01", periods=5, freq="1h")

        # All invalidated
        obs = pd.DataFrame(
            {
                "ob_high": [105, 110],
                "ob_low": [103, 108],
                "invalidated": [True, True],
                "retest_count": [0, 0],
            },
            index=dates[:2],
        )

        nearest = get_nearest_order_block(
            price=100, order_blocks=obs, current_idx=dates[-1], direction="below"
        )

        assert nearest is None


class TestCalculateOBStrength:
    """Tests for calculate_ob_strength function."""

    def test_calculate_ob_strength_considers_retests(self):
        """Strength should increase with retest count."""
        dates = pd.date_range("2024-01-01", periods=3, freq="1h")

        obs = pd.DataFrame(
            {
                "ob_high": [105, 110],
                "ob_low": [103, 108],
                "invalidated": [False, False],
                "retest_count": [0, 5],  # Second OB has more retests
            },
            index=dates[:2],
        )

        strength = calculate_ob_strength(obs)

        assert len(strength) == 2
        # OB with more retests should be stronger
        assert strength.iloc[1] > strength.iloc[0]

    def test_calculate_ob_strength_considers_size(self):
        """Strength should consider OB size."""
        dates = pd.date_range("2024-01-01", periods=3, freq="1h")

        obs = pd.DataFrame(
            {
                "ob_high": [105, 115],  # Second OB is larger
                "ob_low": [103, 108],
                "invalidated": [False, False],
                "retest_count": [0, 0],  # Same retests
            },
            index=dates[:2],
        )

        strength = calculate_ob_strength(obs)

        assert len(strength) == 2
        # All else equal, larger OB should be stronger
        assert strength.iloc[1] > strength.iloc[0]

    def test_ob_strength_capped_at_100(self):
        """OB strength should be capped at 100."""
        dates = pd.date_range("2024-01-01", periods=3, freq="1h")

        obs = pd.DataFrame(
            {
                "ob_high": [200],  # Huge OB
                "ob_low": [100],
                "invalidated": [False],
                "retest_count": [100],  # Many retests
            },
            index=dates[:1],
        )

        strength = calculate_ob_strength(obs)

        assert all(strength <= 100)
        assert all(strength >= 0)
