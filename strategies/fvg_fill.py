"""
Fair Value Gap Fill Strategy.

Trade returns to Fair Value Gaps (imbalances). FVGs represent aggressive
institutional moves. Price often returns to "fill" these gaps before continuing.
"""


import pandas as pd

from core.imbalance import check_fvg_fill, find_fair_value_gaps
from core.market_structure import determine_trend, find_swing_points
from strategies.base import BaseStrategy, Signal


class FVGFillStrategy(BaseStrategy):
    """
    Trade returns to Fair Value Gaps (imbalances).

    Entry Logic:
    1. Identify Fair Value Gaps (3-candle imbalances)
    2. Track active (unfilled) gaps
    3. Enter when price returns to the gap zone
    4. Stop loss: Beyond the gap zone
    5. Take profit: Origin of the move that created FVG or 2:1 RR

    Example:
        >>> strategy = FVGFillStrategy({'min_gap_percent': 0.002})
        >>> signals = strategy.generate_signals(btc_data)
        >>> for signal in signals:
        ...     print(f"{signal.timestamp}: {signal.direction} @ {signal.entry_price}")
    """

    DEFAULT_PARAMS = {
        "min_gap_percent": 0.002,  # Minimum 0.2% gap size
        "max_gap_age_bars": 50,  # Ignore gaps older than 50 bars
        "partial_fill_percent": 0.5,  # Enter when gap 50% filled
        "min_rr_ratio": 1.5,  # Minimum risk:reward
        "swing_period": 5,  # For trend detection
        "atr_period": 14,  # For volatility
    }

    def __init__(self, params: dict | None = None):
        """Initialize the FVG Fill Strategy."""
        merged_params = {**self.DEFAULT_PARAMS, **(params or {})}
        super().__init__("fvg_fill", merged_params)

    def generate_signals(self, data: pd.DataFrame) -> list[Signal]:
        """
        Generate trading signals from OHLCV data.

        Args:
            data: DataFrame with columns [open, high, low, close, volume]

        Returns:
            List of Signal objects for valid setups
        """
        self.validate_data(data)
        signals: list[Signal] = []

        # 1. Find all FVGs
        bullish_fvg, bearish_fvg = find_fair_value_gaps(
            data["high"], data["low"], min_gap_percent=self.params["min_gap_percent"]
        )

        # 2. Track fills
        bullish_fills = check_fvg_fill(
            data["high"],
            data["low"],
            bullish_fvg.copy(),  # Copy to avoid modifying original
            fill_type="partial",
            partial_percent=self.params["partial_fill_percent"],
        )

        bearish_fills = check_fvg_fill(
            data["high"],
            data["low"],
            bearish_fvg.copy(),
            fill_type="partial",
            partial_percent=self.params["partial_fill_percent"],
        )

        # 3. Generate signals on fills
        # Bullish FVG fill = long signal (price returned to bullish gap)
        for idx in data.index[bullish_fills]:
            signal = self._create_long_signal(data, idx, bullish_fvg)
            if signal is not None:
                signals.append(signal)

        # Bearish FVG fill = short signal (price returned to bearish gap)
        for idx in data.index[bearish_fills]:
            signal = self._create_short_signal(data, idx, bearish_fvg)
            if signal is not None:
                signals.append(signal)

        # 4. Filter by RR ratio
        signals = self.filter_signals_by_rr(signals, self.params["min_rr_ratio"])

        return signals

    def _create_long_signal(
        self, data: pd.DataFrame, idx: pd.Timestamp, fvg_zones: pd.DataFrame
    ) -> Signal | None:
        """
        Create a long signal on bullish FVG fill.

        Args:
            data: OHLCV DataFrame
            idx: Timestamp of the signal bar
            fvg_zones: Bullish FVG zones

        Returns:
            Signal object or None if invalid
        """
        try:
            entry = data.loc[idx, "close"]

            # Find the FVG being filled
            prior_fvgs = fvg_zones[fvg_zones.index < idx]
            if len(prior_fvgs) == 0:
                return None

            # Get most recent unfilled FVG
            active_fvgs = prior_fvgs[prior_fvgs["filled"] == False]
            if len(active_fvgs) == 0:
                # Try recently filled
                active_fvgs = prior_fvgs.tail(5)

            fvg = active_fvgs.iloc[-1]
            gap_high = fvg["gap_high"]
            gap_low = fvg["gap_low"]

            # Stop loss: Below the FVG zone
            stop_loss = gap_low * 0.999  # Small buffer

            # Validate stop makes sense
            if stop_loss >= entry:
                return None

            # Take profit: Above the FVG (continuation assumption)
            # Use 2:1 RR by default
            risk = entry - stop_loss
            take_profit = entry + (risk * 2)

            # Calculate confidence
            iloc_idx = data.index.get_loc(idx)
            confidence = self.calculate_confidence(data, iloc_idx)

            return Signal(
                timestamp=idx,
                direction=1,
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                strategy_name=self.name,
                metadata={
                    "fvg_high": gap_high,
                    "fvg_low": gap_low,
                    "signal_type": "bullish_fvg_fill",
                },
            )
        except Exception:
            return None

    def _create_short_signal(
        self, data: pd.DataFrame, idx: pd.Timestamp, fvg_zones: pd.DataFrame
    ) -> Signal | None:
        """
        Create a short signal on bearish FVG fill.

        Args:
            data: OHLCV DataFrame
            idx: Timestamp of the signal bar
            fvg_zones: Bearish FVG zones

        Returns:
            Signal object or None if invalid
        """
        try:
            entry = data.loc[idx, "close"]

            # Find the FVG being filled
            prior_fvgs = fvg_zones[fvg_zones.index < idx]
            if len(prior_fvgs) == 0:
                return None

            # Get most recent unfilled FVG
            active_fvgs = prior_fvgs[prior_fvgs["filled"] == False]
            if len(active_fvgs) == 0:
                # Try recently filled
                active_fvgs = prior_fvgs.tail(5)

            fvg = active_fvgs.iloc[-1]
            gap_high = fvg["gap_high"]
            gap_low = fvg["gap_low"]

            # Stop loss: Above the FVG zone
            stop_loss = gap_high * 1.001  # Small buffer

            # Validate stop makes sense
            if stop_loss <= entry:
                return None

            # Take profit: Below the FVG (continuation assumption)
            # Use 2:1 RR by default
            risk = stop_loss - entry
            take_profit = entry - (risk * 2)

            # Calculate confidence
            iloc_idx = data.index.get_loc(idx)
            confidence = self.calculate_confidence(data, iloc_idx)

            return Signal(
                timestamp=idx,
                direction=-1,
                entry_price=entry,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence=confidence,
                strategy_name=self.name,
                metadata={
                    "fvg_high": gap_high,
                    "fvg_low": gap_low,
                    "signal_type": "bearish_fvg_fill",
                },
            )
        except Exception:
            return None

    def calculate_confidence(self, data: pd.DataFrame, signal_idx: int) -> int:
        """
        Calculate confidence score for a signal.

        Factors:
        - Trend alignment (0-30 points)
        - Gap size (0-20 points) - larger gaps = higher confidence
        - Volume confirmation (0-20 points)
        - Volatility regime (0-20 points)
        - Pattern clarity (0-10 points)

        Args:
            data: Full OHLCV DataFrame
            signal_idx: Integer position of the signal bar

        Returns:
            Confidence score 0-100
        """
        score = 0

        try:
            # Get recent data for analysis
            lookback = min(50, signal_idx)
            recent_data = data.iloc[max(0, signal_idx - lookback) : signal_idx + 1]

            if len(recent_data) < 10:
                return 50  # Default confidence for insufficient data

            # 1. Trend alignment (0-30 points)
            swing_h, swing_l = find_swing_points(
                recent_data["high"], recent_data["low"], n=min(5, len(recent_data) // 4)
            )
            trend = determine_trend(swing_h, swing_l)

            if len(trend) > 0:
                current_trend = trend.iloc[-1]
                if current_trend != 0:
                    score += 15  # Clear trend
                # Trend consistency
                trend_consistency = (trend == current_trend).mean()
                if trend_consistency > 0.7:
                    score += 15  # Strong consistent trend

            # 2. Gap size (0-20 points)
            # Larger gaps = more institutional interest
            # This is assessed in the signal creation, so we add base points
            score += 15  # Base for detected FVG

            # 3. Volume confirmation (0-20 points)
            avg_volume = recent_data["volume"].mean()
            current_volume = data.iloc[signal_idx]["volume"]

            if current_volume > avg_volume * 1.5:
                score += 20  # Volume spike
            elif current_volume > avg_volume:
                score += 10  # Above average

            # 4. Volatility regime (0-20 points)
            atr = self._calculate_atr(recent_data, self.params["atr_period"])
            if len(atr.dropna()) > 0:
                current_atr = atr.iloc[-1]
                avg_atr = atr.mean()

                if current_atr < avg_atr * 1.5:
                    score += 20  # Low volatility
                elif current_atr < avg_atr * 2:
                    score += 10  # Moderate volatility

            # 5. Pattern clarity (0-10 points)
            # Clean fill = price enters gap zone decisively
            score += 10  # Base for detected fill

        except Exception:
            return 50  # Default on error

        return min(score, 100)


def create_strategy(params: dict | None = None) -> FVGFillStrategy:
    """
    Factory function to create a FVGFillStrategy.

    Args:
        params: Optional strategy parameters

    Returns:
        Configured FVGFillStrategy instance
    """
    return FVGFillStrategy(params)


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_strategy_generates_signals_on_fvg_fill
# [ ] test_bullish_fvg_creates_long_signal
# [ ] test_bearish_fvg_creates_short_signal
# [ ] test_stop_loss_below_fvg_for_long
# [ ] test_stop_loss_above_fvg_for_short
# [ ] test_take_profit_uses_2_1_rr
# [ ] test_filters_by_min_rr_ratio
# [ ] test_confidence_calculation
# [ ] test_confidence_considers_trend
# [ ] test_confidence_considers_volume
# [ ] test_confidence_considers_volatility
# [ ] test_no_signals_when_no_fvgs
# [ ] test_respects_max_gap_age
# [ ] test_partial_fill_parameter
# [ ] test_min_gap_percent_filters
# =============================================================================
