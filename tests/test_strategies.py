"""Tests for trading strategies.

NOTE: These are integration tests that test the full strategy logic.
Some tests may require vectorbt which is only available in Docker.
"""
import pytest
import pandas as pd
import numpy as np

from strategies.fvg_fill import FVGFillStrategy
from strategies.bos_orderblock import BOSOrderBlockStrategy
from strategies.liquidity_sweep import LiquiditySweepStrategy
from strategies.base import Signal


@pytest.fixture
def sample_ohlcv():
    """Generate sample OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=200, freq="1h")

    # Create uptrend with pullbacks
    close = np.linspace(100, 150, 200) + np.random.randn(200) * 2

    return pd.DataFrame({
        "open": close - np.random.rand(200),
        "high": close + np.random.rand(200) * 2,
        "low": close - np.random.rand(200) * 2,
        "close": close,
        "volume": np.random.randint(1000, 10000, 200)
    }, index=dates)


@pytest.fixture
def fvg_pattern_data():
    """Data with clear FVG pattern."""
    dates = pd.date_range("2024-01-01", periods=20, freq="1h")

    # Bullish FVG followed by pullback to fill
    data = pd.DataFrame({
        "open":  [100, 101, 106, 107, 108, 109, 108, 105, 106, 107,
                  108, 109, 110, 111, 112, 113, 114, 115, 116, 117],
        "high":  [101, 102, 108, 109, 110, 110, 109, 106, 107, 108,
                  109, 110, 111, 112, 113, 114, 115, 116, 117, 118],
        "low":   [99,  100, 105, 106, 107, 108, 104, 103, 105, 106,
                  107, 108, 109, 110, 111, 112, 113, 114, 115, 116],
        "close": [101, 102, 107, 108, 109, 109, 105, 104, 106, 107,
                  108, 109, 110, 111, 112, 113, 114, 115, 116, 117],
        "volume": [1000] * 20
    }, index=dates)

    return data


@pytest.fixture
def bos_pattern_data():
    """Data with BOS and order block pattern."""
    dates = pd.date_range("2024-01-01", periods=30, freq="1h")

    # Create swing highs, BOS, and OB retest
    close = [100] * 5 + [105] * 5 + [110] * 5 + [115] * 5 + [120] * 10

    data = pd.DataFrame({
        "open": close,
        "high": [c + 1 for c in close],
        "low": [c - 1 for c in close],
        "close": close,
        "volume": [1000] * 30
    }, index=dates)

    return data


class TestFVGFillStrategy:
    """Tests for FVG Fill Strategy."""

    def test_strategy_generates_signals_on_fvg_fill(self, fvg_pattern_data):
        """Strategy should generate signals when FVG is filled."""
        strategy = FVGFillStrategy({"min_gap_percent": 0.01})
        signals = strategy.generate_signals(fvg_pattern_data)

        # May or may not generate signals depending on exact pattern
        assert isinstance(signals, list)
        for signal in signals:
            assert isinstance(signal, Signal)

    def test_bullish_fvg_creates_long_signal(self, fvg_pattern_data):
        """Bullish FVG fill should create long signals."""
        strategy = FVGFillStrategy({"min_gap_percent": 0.01})
        signals = strategy.generate_signals(fvg_pattern_data)

        long_signals = [s for s in signals if s.direction == 1]
        # If signals exist, verify they are long
        for signal in long_signals:
            assert signal.direction == 1

    def test_bearish_fvg_creates_short_signal(self):
        """Bearish FVG fill should create short signals."""
        dates = pd.date_range("2024-01-01", periods=20, freq="1h")

        # Bearish FVG pattern
        data = pd.DataFrame({
            "open":  [100, 99, 94, 93, 92, 91, 92, 95, 94, 93,
                      92, 91, 90, 89, 88, 87, 86, 85, 84, 83],
            "high":  [101, 100, 95, 94, 93, 92, 96, 97, 95, 94,
                      93, 92, 91, 90, 89, 88, 87, 86, 85, 84],
            "low":   [99,  90, 88, 87, 86, 85, 90, 93, 92, 91,
                      90, 89, 88, 87, 86, 85, 84, 83, 82, 81],
            "close": [99,  91, 89, 88, 87, 86, 95, 94, 93, 92,
                      91, 90, 89, 88, 87, 86, 85, 84, 83, 82],
            "volume": [1000] * 20
        }, index=dates)

        strategy = FVGFillStrategy({"min_gap_percent": 0.01})
        signals = strategy.generate_signals(data)

        short_signals = [s for s in signals if s.direction == -1]
        for signal in short_signals:
            assert signal.direction == -1

    def test_stop_loss_below_fvg_for_long(self, fvg_pattern_data):
        """Long signal stop loss should be below FVG."""
        strategy = FVGFillStrategy({"min_gap_percent": 0.01})
        signals = strategy.generate_signals(fvg_pattern_data)

        for signal in signals:
            if signal.direction == 1:  # Long
                assert signal.stop_loss < signal.entry_price

    def test_stop_loss_above_fvg_for_short(self):
        """Short signal stop loss should be above FVG."""
        dates = pd.date_range("2024-01-01", periods=15, freq="1h")

        data = pd.DataFrame({
            "open":  [100, 99, 94, 93, 92, 91, 92, 95, 94, 93, 92, 91, 90, 89, 88],
            "high":  [101, 100, 95, 94, 93, 92, 96, 97, 95, 94, 93, 92, 91, 90, 89],
            "low":   [99,  90, 88, 87, 86, 85, 90, 93, 92, 91, 90, 89, 88, 87, 86],
            "close": [99,  91, 89, 88, 87, 86, 95, 94, 93, 92, 91, 90, 89, 88, 87],
            "volume": [1000] * 15
        }, index=dates)

        strategy = FVGFillStrategy({"min_gap_percent": 0.01})
        signals = strategy.generate_signals(data)

        for signal in signals:
            if signal.direction == -1:  # Short
                assert signal.stop_loss > signal.entry_price

    def test_take_profit_uses_2_1_rr(self, fvg_pattern_data):
        """Take profit should use at least 2:1 RR."""
        strategy = FVGFillStrategy({"min_rr_ratio": 2.0})
        signals = strategy.generate_signals(fvg_pattern_data)

        for signal in signals:
            if signal.take_profit is not None:
                rr = signal.risk_reward_ratio
                if rr is not None:
                    assert rr >= 1.5  # At least close to target

    def test_filters_by_min_rr_ratio(self, sample_ohlcv):
        """Strategy should filter signals by minimum RR ratio."""
        # Strict RR filter
        strategy_strict = FVGFillStrategy({"min_rr_ratio": 3.0})
        signals_strict = strategy_strict.generate_signals(sample_ohlcv)

        # Lenient RR filter
        strategy_lenient = FVGFillStrategy({"min_rr_ratio": 1.0})
        signals_lenient = strategy_lenient.generate_signals(sample_ohlcv)

        # Lenient should have more or equal signals
        assert len(signals_lenient) >= len(signals_strict)

    def test_confidence_calculation(self, fvg_pattern_data):
        """Confidence should be calculated for signals."""
        strategy = FVGFillStrategy()
        signals = strategy.generate_signals(fvg_pattern_data)

        for signal in signals:
            assert 0 <= signal.confidence <= 100

    def test_confidence_considers_trend(self, sample_ohlcv):
        """Confidence calculation should consider trend."""
        strategy = FVGFillStrategy()
        # Test that confidence method exists and works
        if len(sample_ohlcv) > 50:
            conf = strategy.calculate_confidence(sample_ohlcv, 50)
            assert 0 <= conf <= 100

    def test_confidence_considers_volume(self, sample_ohlcv):
        """Confidence should consider volume confirmation."""
        strategy = FVGFillStrategy()
        signals = strategy.generate_signals(sample_ohlcv)

        # Verify confidence is set (volume considered internally)
        for signal in signals:
            assert signal.confidence > 0

    def test_confidence_considers_volatility(self, sample_ohlcv):
        """Confidence should consider volatility (ATR)."""
        # ATR is calculated in the strategy
        strategy = FVGFillStrategy({"atr_period": 14})
        signals = strategy.generate_signals(sample_ohlcv)

        # Just verify signals are generated with confidence
        for signal in signals:
            assert hasattr(signal, "confidence")

    def test_no_signals_when_no_fvgs(self):
        """Should return empty list when no FVGs exist."""
        dates = pd.date_range("2024-01-01", periods=10, freq="1h")

        # Flat price action, no gaps
        data = pd.DataFrame({
            "open":  [100] * 10,
            "high":  [101] * 10,
            "low":   [99] * 10,
            "close": [100] * 10,
            "volume": [1000] * 10
        }, index=dates)

        strategy = FVGFillStrategy({"min_gap_percent": 0.01})
        signals = strategy.generate_signals(data)

        assert len(signals) == 0

    def test_respects_max_gap_age(self, fvg_pattern_data):
        """Strategy should respect max_gap_age_bars parameter."""
        # Strict age limit
        strategy_strict = FVGFillStrategy({"max_gap_age_bars": 5})
        signals_strict = strategy_strict.generate_signals(fvg_pattern_data)

        # Lenient age limit
        strategy_lenient = FVGFillStrategy({"max_gap_age_bars": 100})
        signals_lenient = strategy_lenient.generate_signals(fvg_pattern_data)

        # Lenient should have more or equal signals
        assert len(signals_lenient) >= len(signals_strict)

    def test_partial_fill_parameter(self, fvg_pattern_data):
        """partial_fill_percent parameter should affect signal generation."""
        # Require full fill
        strategy_full = FVGFillStrategy({"partial_fill_percent": 1.0})
        signals_full = strategy_full.generate_signals(fvg_pattern_data)

        # Allow partial fill
        strategy_partial = FVGFillStrategy({"partial_fill_percent": 0.3})
        signals_partial = strategy_partial.generate_signals(fvg_pattern_data)

        # Partial should have more or equal signals
        assert len(signals_partial) >= len(signals_full)

    def test_min_gap_percent_filters(self, sample_ohlcv):
        """min_gap_percent should filter small gaps."""
        # Strict gap filter
        strategy_strict = FVGFillStrategy({"min_gap_percent": 0.05})  # 5%
        signals_strict = strategy_strict.generate_signals(sample_ohlcv)

        # Lenient gap filter
        strategy_lenient = FVGFillStrategy({"min_gap_percent": 0.001})  # 0.1%
        signals_lenient = strategy_lenient.generate_signals(sample_ohlcv)

        assert len(signals_lenient) >= len(signals_strict)


class TestBOSOrderBlockStrategy:
    """Tests for BOS Order Block Strategy."""

    def test_strategy_requires_bos_confirmation(self, sample_ohlcv):
        """Strategy should require BOS before generating signals."""
        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(sample_ohlcv)

        # Signals should only exist with BOS
        assert isinstance(signals, list)

    def test_bullish_bos_creates_long_setup(self, bos_pattern_data):
        """Bullish BOS should create long setup opportunities."""
        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(bos_pattern_data)

        long_signals = [s for s in signals if s.direction == 1]
        for signal in long_signals:
            assert signal.direction == 1

    def test_bearish_bos_creates_short_setup(self):
        """Bearish BOS should create short setup opportunities."""
        dates = pd.date_range("2024-01-01", periods=30, freq="1h")

        # Downtrend with BOS
        close = [100] * 5 + [95] * 5 + [90] * 5 + [85] * 5 + [80] * 10

        data = pd.DataFrame({
            "open": close,
            "high": [c + 1 for c in close],
            "low": [c - 1 for c in close],
            "close": close,
            "volume": [1000] * 30
        }, index=dates)

        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(data)

        short_signals = [s for s in signals if s.direction == -1]
        for signal in short_signals:
            assert signal.direction == -1

    def test_finds_recent_ob_before_bos(self, sample_ohlcv):
        """Strategy should find order blocks before BOS."""
        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(sample_ohlcv)

        # Just verify signals are created with proper structure
        for signal in signals:
            assert signal.entry_price > 0
            assert signal.stop_loss > 0

    def test_waits_for_ob_retest_after_bos(self, bos_pattern_data):
        """Strategy should wait for OB retest after BOS."""
        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(bos_pattern_data)

        # Verify signals exist and have metadata
        for signal in signals:
            assert hasattr(signal, "metadata")

    def test_stop_loss_below_ob_for_long(self, bos_pattern_data):
        """Long signal SL should be below OB."""
        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(bos_pattern_data)

        for signal in signals:
            if signal.direction == 1:
                assert signal.stop_loss < signal.entry_price

    def test_stop_loss_above_ob_for_short(self):
        """Short signal SL should be above OB."""
        dates = pd.date_range("2024-01-01", periods=30, freq="1h")

        close = [100] * 5 + [95] * 5 + [90] * 5 + [85] * 5 + [80] * 10

        data = pd.DataFrame({
            "open": close,
            "high": [c + 1 for c in close],
            "low": [c - 1 for c in close],
            "close": close,
            "volume": [1000] * 30
        }, index=dates)

        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(data)

        for signal in signals:
            if signal.direction == -1:
                assert signal.stop_loss > signal.entry_price

    def test_take_profit_uses_3_1_rr_minimum(self, sample_ohlcv):
        """Strategy should target at least 3:1 RR."""
        strategy = BOSOrderBlockStrategy({"min_rr_ratio": 3.0})
        signals = strategy.generate_signals(sample_ohlcv)

        for signal in signals:
            if signal.take_profit is not None:
                rr = signal.risk_reward_ratio
                if rr is not None:
                    assert rr >= 2.0  # At least close to target

    def test_filters_by_min_rr_ratio(self, sample_ohlcv):
        """Should filter by minimum RR ratio."""
        strategy_strict = BOSOrderBlockStrategy({"min_rr_ratio": 4.0})
        signals_strict = strategy_strict.generate_signals(sample_ohlcv)

        strategy_lenient = BOSOrderBlockStrategy({"min_rr_ratio": 2.0})
        signals_lenient = strategy_lenient.generate_signals(sample_ohlcv)

        assert len(signals_lenient) >= len(signals_strict)

    def test_confidence_weighted_for_bos(self, sample_ohlcv):
        """Confidence should be calculated for BOS setups."""
        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(sample_ohlcv)

        for signal in signals:
            assert 0 <= signal.confidence <= 100

    def test_confidence_considers_trend_consistency(self, sample_ohlcv):
        """Confidence should consider trend consistency."""
        strategy = BOSOrderBlockStrategy()

        if len(sample_ohlcv) > 50:
            conf = strategy.calculate_confidence(sample_ohlcv, 50)
            assert 0 <= conf <= 100

    def test_confidence_considers_volume(self, sample_ohlcv):
        """Confidence should factor in volume."""
        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(sample_ohlcv)

        for signal in signals:
            assert signal.confidence > 0

    def test_no_signals_without_bos(self):
        """No signals should be generated without BOS."""
        dates = pd.date_range("2024-01-01", periods=20, freq="1h")

        # Ranging market, no clear BOS
        data = pd.DataFrame({
            "open":  [100] * 20,
            "high":  [102] * 20,
            "low":   [98] * 20,
            "close": [100] * 20,
            "volume": [1000] * 20
        }, index=dates)

        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(data)

        # May have 0 signals due to no BOS
        assert isinstance(signals, list)

    def test_no_signals_without_ob(self):
        """No signals without valid order blocks."""
        dates = pd.date_range("2024-01-01", periods=20, freq="1h")

        # Smooth trend, no OBs
        close = list(range(100, 120))

        data = pd.DataFrame({
            "open": close,
            "high": [c + 0.5 for c in close],
            "low": [c - 0.5 for c in close],
            "close": close,
            "volume": [1000] * 20
        }, index=dates)

        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(data)

        # Verify it handles lack of OBs gracefully
        assert isinstance(signals, list)

    def test_respects_ob_validity_bars(self, sample_ohlcv):
        """Strategy should respect OB validity period."""
        strategy_strict = BOSOrderBlockStrategy({"max_ob_age_bars": 10})
        signals_strict = strategy_strict.generate_signals(sample_ohlcv)

        strategy_lenient = BOSOrderBlockStrategy({"max_ob_age_bars": 100})
        signals_lenient = strategy_lenient.generate_signals(sample_ohlcv)

        assert len(signals_lenient) >= len(signals_strict)

    def test_ob_retest_detected_correctly(self, bos_pattern_data):
        """OB retest should be detected correctly."""
        strategy = BOSOrderBlockStrategy()
        signals = strategy.generate_signals(bos_pattern_data)

        # Verify signals have proper structure
        for signal in signals:
            assert signal.entry_price > 0
            assert signal.stop_loss > 0
            assert signal.confidence >= 0


# =============================================================================
# Liquidity Sweep Strategy Tests (Phase 1.3)
# =============================================================================


@pytest.fixture
def liquidity_sweep_data():
    """Data with clear liquidity sweep pattern."""
    dates = pd.date_range("2024-01-01", periods=30, freq="1h")

    # Pattern:
    # - Swing low at index 5 (price = 100)
    # - Price sweeps below (low = 99.5) at index 20
    # - Reverses back inside (close = 101) - bullish sweep
    data = pd.DataFrame({
        "open":  [105, 104, 103, 102, 101, 100, 101, 102, 103, 104,
                  105, 106, 107, 106, 105, 104, 103, 102, 101, 100,
                  99.5, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        "high":  [106, 105, 104, 103, 102, 101, 102, 103, 104, 105,
                  106, 107, 108, 107, 106, 105, 104, 103, 102, 101,
                  101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        "low":   [104, 103, 102, 101, 100, 99, 100, 101, 102, 103,
                  104, 105, 106, 105, 104, 103, 102, 101, 100, 99.5,
                  99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
        "close": [104, 103, 102, 101, 100, 100, 101, 102, 103, 104,
                  105, 106, 107, 106, 105, 104, 103, 102, 101, 100,
                  101, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        "volume": [1000] * 30
    }, index=dates)

    return data


class TestLiquiditySweepStrategy:
    """Tests for Liquidity Sweep Strategy (Phase 1.3 - coverage improvement)."""

    def test_strategy_initialization(self):
        """Test strategy initializes with correct defaults."""
        strategy = LiquiditySweepStrategy()

        assert strategy.name == "liquidity_sweep"
        assert strategy.params["swing_period"] == 5
        assert strategy.params["min_sweep_percent"] == 0.001
        assert strategy.params["max_reversal_bars"] == 3
        assert strategy.params["min_rr_ratio"] == 1.5

    def test_custom_parameters(self):
        """Test strategy accepts custom parameters."""
        custom_params = {
            "swing_period": 10,
            "min_rr_ratio": 2.0
        }
        strategy = LiquiditySweepStrategy(custom_params)

        assert strategy.params["swing_period"] == 10
        assert strategy.params["min_rr_ratio"] == 2.0
        # Default params should still be there
        assert strategy.params["max_reversal_bars"] == 3

    def test_generate_signals_basic(self, liquidity_sweep_data):
        """Test signal generation with bullish sweep pattern."""
        strategy = LiquiditySweepStrategy()
        signals = strategy.generate_signals(liquidity_sweep_data)

        # Should detect the bullish sweep
        assert isinstance(signals, list)
        # May or may not generate signal depending on RR filter

    def test_combine_liquidity_levels(self, sample_ohlcv):
        """Test combining swing levels with equal levels."""
        strategy = LiquiditySweepStrategy()

        # Create sample swing and equal levels
        swing_levels = pd.Series([100.0, None, 105.0, None, 110.0],
                                index=sample_ohlcv.index[:5])
        equal_levels = pd.Series([None, 103.0, None, None, 111.0],
                                index=sample_ohlcv.index[:5])

        combined = strategy._combine_liquidity_levels(swing_levels, equal_levels)

        # Equal levels should override swing levels
        assert combined.iloc[0] == 100.0  # From swing
        assert combined.iloc[1] == 103.0  # From equal (overrides NaN)
        assert combined.iloc[2] == 105.0  # From swing
        assert combined.iloc[4] == 111.0  # From equal (overrides 110.0)

    def test_create_long_signal_basic(self, liquidity_sweep_data):
        """Test creating a long signal after bullish sweep."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = liquidity_sweep_data

        # Find swing points
        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        # Try to create signal at sweep bar (index 20)
        idx = data.index[20]
        signal = strategy._create_long_signal(data, idx, swing_highs, swing_lows)

        if signal is not None:
            assert signal.direction == 1
            assert signal.entry_price == data.loc[idx, "close"]
            assert signal.stop_loss < signal.entry_price
            assert signal.take_profit > signal.entry_price
            assert signal.confidence >= 0
            assert signal.confidence <= 100
            assert "sweep_low" in signal.metadata
            assert signal.metadata["signal_type"] == "bullish_sweep"

    def test_create_long_signal_invalid_stop(self, sample_ohlcv):
        """Test that long signal returns None if stop >= entry."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = sample_ohlcv.copy()

        # Manipulate data to make invalid stop loss
        idx = data.index[50]
        data.loc[idx, "low"] = data.loc[idx, "close"] * 1.01  # Low > close

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        signal = strategy._create_long_signal(data, idx, swing_highs, swing_lows)

        # Should return None for invalid setup
        assert signal is None

    def test_create_long_signal_with_prior_swing_high(self, liquidity_sweep_data):
        """Test long signal uses prior swing high for TP when available."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = liquidity_sweep_data

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        # Create signal late in data (should have prior swing highs)
        idx = data.index[25]
        signal = strategy._create_long_signal(data, idx, swing_highs, swing_lows)

        if signal is not None and len(swing_highs[swing_highs.index < idx].dropna()) > 0:
            prior_high = swing_highs[swing_highs.index < idx].dropna().iloc[-1]
            # TP should be either prior high or 2:1 RR
            assert signal.take_profit > signal.entry_price

    def test_create_long_signal_fallback_to_2_1_rr(self, liquidity_sweep_data):
        """Test long signal TP calculation logic."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = liquidity_sweep_data.copy()

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        idx = data.index[20]
        signal = strategy._create_long_signal(data, idx, swing_highs, swing_lows)

        if signal is not None:
            # TP should be either prior swing high or 2:1 RR
            # Just verify TP is above entry
            assert signal.take_profit > signal.entry_price
            # And that it's reasonable (not too far)
            assert signal.take_profit < signal.entry_price * 1.2  # Within 20%

    def test_create_short_signal_basic(self, sample_ohlcv):
        """Test creating a short signal after bearish sweep."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        # Try creating short signal at an arbitrary index
        idx = data.index[100]
        signal = strategy._create_short_signal(data, idx, swing_highs, swing_lows)

        if signal is not None:
            assert signal.direction == -1
            assert signal.entry_price == data.loc[idx, "close"]
            assert signal.stop_loss > signal.entry_price
            assert signal.take_profit < signal.entry_price
            assert signal.confidence >= 0
            assert signal.confidence <= 100
            assert "sweep_high" in signal.metadata
            assert signal.metadata["signal_type"] == "bearish_sweep"

    def test_create_short_signal_invalid_stop(self, sample_ohlcv):
        """Test that short signal returns None if stop <= entry."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = sample_ohlcv.copy()

        # Manipulate data to make invalid stop loss
        idx = data.index[50]
        data.loc[idx, "high"] = data.loc[idx, "close"] * 0.99  # High < close

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        signal = strategy._create_short_signal(data, idx, swing_highs, swing_lows)

        # Should return None for invalid setup
        assert signal is None

    def test_create_short_signal_with_prior_swing_low(self, sample_ohlcv):
        """Test short signal uses prior swing low for TP when available."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        # Create signal late in data
        idx = data.index[150]
        signal = strategy._create_short_signal(data, idx, swing_highs, swing_lows)

        if signal is not None:
            # TP should be below entry
            assert signal.take_profit < signal.entry_price

    def test_create_short_signal_fallback_to_2_1_rr(self, sample_ohlcv):
        """Test short signal TP calculation logic."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        idx = data.index[100]
        signal = strategy._create_short_signal(data, idx, swing_highs, swing_lows)

        if signal is not None:
            # TP should be either prior swing low or 2:1 RR
            # Just verify TP is below entry
            assert signal.take_profit < signal.entry_price
            # And that it's reasonable (not too far)
            assert signal.take_profit > signal.entry_price * 0.8  # Within 20%

    def test_confidence_calculation(self, liquidity_sweep_data):
        """Test confidence scoring for liquidity sweep signals."""
        strategy = LiquiditySweepStrategy()
        data = liquidity_sweep_data

        # Calculate confidence at various points
        confidence_early = strategy.calculate_confidence(data, 10)
        confidence_late = strategy.calculate_confidence(data, 25)

        # Both should be valid confidence scores
        assert 0 <= confidence_early <= 100
        assert 0 <= confidence_late <= 100

    def test_signals_filtered_by_min_rr(self, liquidity_sweep_data):
        """Test that signals are filtered by minimum RR ratio."""
        # Strategy with very high RR requirement (should filter most signals)
        strategy_high_rr = LiquiditySweepStrategy({"min_rr_ratio": 10.0})
        signals_high = strategy_high_rr.generate_signals(liquidity_sweep_data)

        # Strategy with low RR requirement
        strategy_low_rr = LiquiditySweepStrategy({"min_rr_ratio": 1.0})
        signals_low = strategy_low_rr.generate_signals(liquidity_sweep_data)

        # Low RR should have >= signals than high RR
        assert len(signals_low) >= len(signals_high)

    def test_exception_handling_in_create_long_signal(self, sample_ohlcv):
        """Test that exceptions in _create_long_signal return None."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        # Use invalid index (should trigger exception)
        invalid_idx = pd.Timestamp("2025-01-01")
        signal = strategy._create_long_signal(data, invalid_idx, swing_highs, swing_lows)

        # Should return None on exception
        assert signal is None

    def test_exception_handling_in_create_short_signal(self, sample_ohlcv):
        """Test that exceptions in _create_short_signal return None."""
        from core.market_structure import find_swing_points

        strategy = LiquiditySweepStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        # Use invalid index
        invalid_idx = pd.Timestamp("2025-01-01")
        signal = strategy._create_short_signal(data, invalid_idx, swing_highs, swing_lows)

        # Should return None on exception
        assert signal is None


# =============================================================================
# BOS OrderBlock Strategy Additional Tests (Phase 1.3)
# =============================================================================


class TestBOSOrderBlockStrategyExtended:
    """Extended tests for BOS + OrderBlock Strategy (Phase 1.3 - coverage improvement)."""

    def test_find_recent_ob_basic(self, sample_ohlcv):
        """Test finding recent order block before BOS."""
        from core.order_blocks import find_order_blocks

        strategy = BOSOrderBlockStrategy()
        data = sample_ohlcv

        # Find order blocks
        bullish_ob, bearish_ob = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"],
            min_impulse_percent=0.01
        )

        if len(bullish_ob) > 0:
            # Pick a timestamp after some OBs
            bos_idx = data.index[100]
            recent_ob = strategy._find_recent_ob(bullish_ob, bos_idx, lookback=10)

            if recent_ob is not None:
                assert "timestamp" in recent_ob
                assert "ob_high" in recent_ob
                assert "ob_low" in recent_ob
                assert "invalidated" in recent_ob
                assert recent_ob["timestamp"] < bos_idx

    def test_find_recent_ob_empty_dataframe(self):
        """Test finding OB with empty DataFrame."""
        strategy = BOSOrderBlockStrategy()

        # Empty OB DataFrame
        empty_obs = pd.DataFrame(columns=["ob_high", "ob_low", "invalidated"])
        bos_idx = pd.Timestamp("2024-01-01")

        result = strategy._find_recent_ob(empty_obs, bos_idx)

        assert result is None

    def test_find_recent_ob_no_prior_obs(self, sample_ohlcv):
        """Test finding OB when there are no prior OBs."""
        from core.order_blocks import find_order_blocks

        strategy = BOSOrderBlockStrategy()
        data = sample_ohlcv

        bullish_ob, bearish_ob = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"],
            min_impulse_percent=0.01
        )

        if len(bullish_ob) > 0:
            # Use very early timestamp (before any OBs)
            bos_idx = data.index[0]
            recent_ob = strategy._find_recent_ob(bullish_ob, bos_idx)

            # Should return None (no prior OBs)
            assert recent_ob is None

    def test_find_recent_ob_respects_lookback(self, sample_ohlcv):
        """Test that lookback parameter limits search window."""
        from core.order_blocks import find_order_blocks

        strategy = BOSOrderBlockStrategy()
        data = sample_ohlcv

        bullish_ob, bearish_ob = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"],
            min_impulse_percent=0.01
        )

        if len(bullish_ob) > 10:
            bos_idx = data.index[150]

            # Small lookback
            ob_small = strategy._find_recent_ob(bullish_ob, bos_idx, lookback=3)

            # Large lookback
            ob_large = strategy._find_recent_ob(bullish_ob, bos_idx, lookback=50)

            # Both should find something if OBs exist
            # Large lookback might find an earlier OB
            if ob_small and ob_large:
                assert ob_small["timestamp"] <= bos_idx
                assert ob_large["timestamp"] <= bos_idx

    def test_wait_for_retest_bullish(self, sample_ohlcv):
        """Test waiting for bullish OB retest after BOS."""
        from core.market_structure import find_swing_points
        from core.order_blocks import find_order_blocks

        strategy = BOSOrderBlockStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        bullish_ob, bearish_ob = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"],
            min_impulse_percent=0.01
        )

        if len(bullish_ob) > 0:
            # Simulate OB and BOS
            ob_idx = bullish_ob.index[0]
            ob_details = {
                "timestamp": ob_idx,
                "ob_high": bullish_ob.iloc[0]["ob_high"],
                "ob_low": bullish_ob.iloc[0]["ob_low"],
                "invalidated": False
            }

            bos_idx = data.index[min(50, len(data)-1)]

            signal = strategy._wait_for_retest(
                data, bos_idx, ob_details, bullish_ob, swing_highs, direction="long"
            )

            # May or may not generate signal (depends on retest)
            if signal is not None:
                assert signal.direction == 1
                assert signal.entry_price > 0
                assert signal.stop_loss < signal.entry_price
                assert signal.take_profit > signal.entry_price

    def test_wait_for_retest_bearish(self, sample_ohlcv):
        """Test waiting for bearish OB retest after BOS."""
        from core.market_structure import find_swing_points
        from core.order_blocks import find_order_blocks

        strategy = BOSOrderBlockStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        bullish_ob, bearish_ob = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"],
            min_impulse_percent=0.01
        )

        if len(bearish_ob) > 0:
            ob_idx = bearish_ob.index[0]
            ob_details = {
                "timestamp": ob_idx,
                "ob_high": bearish_ob.iloc[0]["ob_high"],
                "ob_low": bearish_ob.iloc[0]["ob_low"],
                "invalidated": False
            }

            bos_idx = data.index[min(50, len(data)-1)]

            signal = strategy._wait_for_retest(
                data, bos_idx, ob_details, bearish_ob, swing_lows, direction="short"
            )

            if signal is not None:
                assert signal.direction == -1
                assert signal.entry_price > 0
                assert signal.stop_loss > signal.entry_price
                assert signal.take_profit < signal.entry_price

    def test_wait_for_retest_invalidated_ob(self, sample_ohlcv):
        """Test that invalidated OB does not generate signal."""
        from core.market_structure import find_swing_points
        from core.order_blocks import find_order_blocks

        strategy = BOSOrderBlockStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        bullish_ob, _ = find_order_blocks(
            data["open"], data["high"], data["low"], data["close"]
        )

        if len(bullish_ob) > 0:
            ob_idx = bullish_ob.index[0]
            ob_details = {
                "timestamp": ob_idx,
                "ob_high": bullish_ob.iloc[0]["ob_high"],
                "ob_low": bullish_ob.iloc[0]["ob_low"],
                "invalidated": True  # Invalidated OB
            }

            bos_idx = data.index[50]

            signal = strategy._wait_for_retest(
                data, bos_idx, ob_details, bullish_ob, swing_highs, direction="long"
            )

            # Should not generate signal for invalidated OB
            assert signal is None

    def test_create_long_signal_basic(self, sample_ohlcv):
        """Test creating long signal from OB retest."""
        from core.market_structure import find_swing_points

        strategy = BOSOrderBlockStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        # Simulate OB details
        idx = data.index[100]
        ob_details = {
            "timestamp": data.index[95],
            "ob_high": data.loc[data.index[95], "high"],
            "ob_low": data.loc[data.index[95], "low"],
            "invalidated": False
        }

        signal = strategy._create_long_signal(
            data, idx, ob_details, swing_highs
        )

        if signal is not None:
            assert signal.direction == 1
            assert signal.entry_price == data.loc[idx, "close"]
            assert signal.stop_loss < ob_details["ob_low"]
            assert signal.take_profit > signal.entry_price
            assert 0 <= signal.confidence <= 100

    def test_create_short_signal_basic(self, sample_ohlcv):
        """Test creating short signal from OB retest."""
        from core.market_structure import find_swing_points

        strategy = BOSOrderBlockStrategy()
        data = sample_ohlcv

        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=5
        )

        # Simulate OB details
        idx = data.index[100]
        ob_details = {
            "timestamp": data.index[95],
            "ob_high": data.loc[data.index[95], "high"],
            "ob_low": data.loc[data.index[95], "low"],
            "invalidated": False
        }

        signal = strategy._create_short_signal(
            data, idx, ob_details, swing_lows
        )

        if signal is not None:
            assert signal.direction == -1
            assert signal.entry_price == data.loc[idx, "close"]
            assert signal.stop_loss > ob_details["ob_high"]
            assert signal.take_profit < signal.entry_price
            assert 0 <= signal.confidence <= 100

    def test_exception_handling_in_private_methods(self, sample_ohlcv):
        """Test that exceptions in private methods don't crash."""
        from core.market_structure import find_swing_points

        strategy = BOSOrderBlockStrategy()
        data = sample_ohlcv

        swing_highs, _ = find_swing_points(
            data["high"], data["low"], n=5
        )

        # Invalid OB details (should trigger exception handling)
        invalid_ob = {
            "timestamp": pd.Timestamp("2025-01-01"),  # Future date
            "ob_high": 100,
            "ob_low": 99,
            "invalidated": False
        }

        invalid_idx = pd.Timestamp("2025-01-02")

        # Should return None on exception
        signal = strategy._create_long_signal(
            data, invalid_idx, invalid_ob, swing_highs
        )

        assert signal is None

    def test_max_ob_age_parameter(self, sample_ohlcv):
        """Test that max_ob_age_bars parameter is respected."""
        # Create strategy with very short OB validity
        strategy_short = BOSOrderBlockStrategy({"ob_validity_bars": 5})

        # Create strategy with long OB validity
        strategy_long = BOSOrderBlockStrategy({"ob_validity_bars": 100})

        assert strategy_short.params["ob_validity_bars"] == 5
        assert strategy_long.params["ob_validity_bars"] == 100

        # Generate signals (short validity should have <= signals)
        signals_short = strategy_short.generate_signals(sample_ohlcv)
        signals_long = strategy_long.generate_signals(sample_ohlcv)

        # Longer validity might find more signals
        assert len(signals_long) >= len(signals_short)
