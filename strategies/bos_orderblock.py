"""
Break of Structure + Order Block Strategy.

Trend following with BOS confirmation and OB entries. This is the most
conservative strategy - trades with confirmed trend on pullbacks to
institutional accumulation/distribution zones.
"""


import pandas as pd

from core.market_structure import detect_structure_breaks, determine_trend, find_swing_points
from core.order_blocks import find_order_blocks
from strategies.base import BaseStrategy, Signal


class BOSOrderBlockStrategy(BaseStrategy):
    """
    Trend following with Break of Structure and Order Block entries.

    Entry Logic:
    1. Detect Break of Structure (BOS) confirming trend
    2. Identify Order Block before the BOS impulse
    3. Wait for price to retest the Order Block
    4. Enter on retest with trend direction
    5. Stop loss: Beyond the Order Block
    6. Take profit: Next structure level or measured move

    Example:
        >>> strategy = BOSOrderBlockStrategy({'swing_period': 5})
        >>> signals = strategy.generate_signals(btc_data)
        >>> for signal in signals:
        ...     print(f"{signal.timestamp}: {signal.direction} @ {signal.entry_price}")
    """

    DEFAULT_PARAMS = {
        "swing_period": 5,
        "min_impulse_percent": 0.01,  # 1% minimum impulse for OB
        "ob_validity_bars": 30,  # OB valid for 30 bars
        "min_rr_ratio": 2.0,  # Higher RR for trend following
        "atr_period": 14,  # For volatility
    }

    def __init__(self, params: dict | None = None):
        """Initialize the BOS + Order Block Strategy."""
        merged_params = {**self.DEFAULT_PARAMS, **(params or {})}
        super().__init__("bos_orderblock", merged_params)

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

        # 1. Find market structure
        swing_highs, swing_lows = find_swing_points(
            data["high"], data["low"], n=self.params["swing_period"]
        )

        # 2. Detect BOS events
        bos_bullish, bos_bearish, choch = detect_structure_breaks(
            data["close"], swing_highs, swing_lows
        )

        # 3. Find order blocks
        bullish_ob, bearish_ob = find_order_blocks(
            data["open"],
            data["high"],
            data["low"],
            data["close"],
            min_impulse_percent=self.params["min_impulse_percent"],
        )

        # 4. Track BOS + OB setups
        # When BOS occurs, look for the OB that preceded it
        # Then wait for retest of that OB

        # Process bullish BOS
        for idx in data.index[bos_bullish]:
            # Find recent bullish OB before this BOS
            recent_ob = self._find_recent_ob(bullish_ob, idx, lookback=10)

            if recent_ob is not None:
                # Wait for retest after BOS
                retest_signal = self._wait_for_retest(
                    data, idx, recent_ob, bullish_ob, swing_highs, direction="long"
                )
                if retest_signal is not None:
                    signals.append(retest_signal)

        # Process bearish BOS
        for idx in data.index[bos_bearish]:
            # Find recent bearish OB before this BOS
            recent_ob = self._find_recent_ob(bearish_ob, idx, lookback=10)

            if recent_ob is not None:
                # Wait for retest after BOS
                retest_signal = self._wait_for_retest(
                    data, idx, recent_ob, bearish_ob, swing_lows, direction="short"
                )
                if retest_signal is not None:
                    signals.append(retest_signal)

        # 5. Filter by RR ratio
        signals = self.filter_signals_by_rr(signals, self.params["min_rr_ratio"])

        return signals

    def _find_recent_ob(
        self, order_blocks: pd.DataFrame, bos_idx: pd.Timestamp, lookback: int = 10
    ) -> dict | None:
        """
        Find the most recent order block before a BOS event.

        Args:
            order_blocks: DataFrame from find_order_blocks
            bos_idx: Timestamp of BOS event
            lookback: Number of bars to look back

        Returns:
            Dictionary with OB details or None
        """
        if len(order_blocks) == 0:
            return None

        # Get OBs before the BOS
        prior_obs = order_blocks[order_blocks.index < bos_idx]

        if len(prior_obs) == 0:
            return None

        # Get the most recent OB
        recent_obs = prior_obs.tail(lookback)
        if len(recent_obs) == 0:
            return None

        ob = recent_obs.iloc[-1]
        ob_idx = recent_obs.index[-1]

        return {
            "timestamp": ob_idx,
            "ob_high": ob["ob_high"],
            "ob_low": ob["ob_low"],
            "invalidated": ob["invalidated"],
        }

    def _wait_for_retest(
        self,
        data: pd.DataFrame,
        bos_idx: pd.Timestamp,
        ob: dict,
        ob_dataframe: pd.DataFrame,
        swing_levels: pd.Series,
        direction: str,
    ) -> Signal | None:
        """
        Wait for price to retest the OB after BOS, generate signal.

        Args:
            data: OHLCV DataFrame
            bos_idx: BOS timestamp
            ob: Order block dictionary
            ob_dataframe: Full OB DataFrame
            swing_levels: Swing highs (for long) or lows (for short)
            direction: 'long' or 'short'

        Returns:
            Signal if retest occurs, None otherwise
        """
        # Get bars after BOS
        bos_pos = data.index.get_loc(bos_idx)
        validity_bars = self.params["ob_validity_bars"]

        for i in range(bos_pos + 1, min(bos_pos + validity_bars + 1, len(data))):
            idx = data.index[i]
            current_high = data.loc[idx, "high"]
            current_low = data.loc[idx, "low"]

            ob_high = ob["ob_high"]
            ob_low = ob["ob_low"]

            # Check if price enters OB zone
            if current_low <= ob_high and current_high >= ob_low:
                # Retest detected!
                if direction == "long":
                    signal = self._create_long_signal(data, idx, ob, swing_levels)
                else:
                    signal = self._create_short_signal(data, idx, ob, swing_levels)

                return signal

        return None

    def _create_long_signal(
        self, data: pd.DataFrame, idx: pd.Timestamp, ob: dict, swing_highs: pd.Series
    ) -> Signal | None:
        """
        Create a long signal on bullish OB retest.

        Args:
            data: OHLCV DataFrame
            idx: Timestamp of the signal bar
            ob: Order block dictionary
            swing_highs: Swing high prices

        Returns:
            Signal object or None if invalid
        """
        try:
            entry = data.loc[idx, "close"]

            # Stop loss: Below the OB
            stop_loss = ob["ob_low"] * 0.999  # Small buffer

            # Validate stop makes sense
            if stop_loss >= entry:
                return None

            # Take profit: Next swing high or 3:1 RR (higher for trend following)
            prior_highs = swing_highs[swing_highs.index < idx].dropna()
            if len(prior_highs) > 0:
                # Look for swing high above entry
                future_targets = prior_highs[prior_highs > entry]
                if len(future_targets) > 0:
                    take_profit = future_targets.iloc[0]
                else:
                    # Use RR-based target
                    risk = entry - stop_loss
                    take_profit = entry + (risk * 3)
            else:
                # Use 3:1 RR
                risk = entry - stop_loss
                take_profit = entry + (risk * 3)

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
                    "ob_high": ob["ob_high"],
                    "ob_low": ob["ob_low"],
                    "signal_type": "bullish_ob_retest",
                },
            )
        except Exception:
            return None

    def _create_short_signal(
        self, data: pd.DataFrame, idx: pd.Timestamp, ob: dict, swing_lows: pd.Series
    ) -> Signal | None:
        """
        Create a short signal on bearish OB retest.

        Args:
            data: OHLCV DataFrame
            idx: Timestamp of the signal bar
            ob: Order block dictionary
            swing_lows: Swing low prices

        Returns:
            Signal object or None if invalid
        """
        try:
            entry = data.loc[idx, "close"]

            # Stop loss: Above the OB
            stop_loss = ob["ob_high"] * 1.001  # Small buffer

            # Validate stop makes sense
            if stop_loss <= entry:
                return None

            # Take profit: Next swing low or 3:1 RR
            prior_lows = swing_lows[swing_lows.index < idx].dropna()
            if len(prior_lows) > 0:
                # Look for swing low below entry
                future_targets = prior_lows[prior_lows < entry]
                if len(future_targets) > 0:
                    take_profit = future_targets.iloc[-1]
                else:
                    # Use RR-based target
                    risk = stop_loss - entry
                    take_profit = entry - (risk * 3)
            else:
                # Use 3:1 RR
                risk = stop_loss - entry
                take_profit = entry - (risk * 3)

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
                    "ob_high": ob["ob_high"],
                    "ob_low": ob["ob_low"],
                    "signal_type": "bearish_ob_retest",
                },
            )
        except Exception:
            return None

    def calculate_confidence(self, data: pd.DataFrame, signal_idx: int) -> int:
        """
        Calculate confidence score for a signal.

        Factors:
        - Trend confirmation via BOS (0-40 points) - highest weight
        - Trend consistency (0-20 points)
        - Volume confirmation (0-20 points)
        - Volatility regime (0-20 points)

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

            # 1. BOS confirmation (0-40 points)
            # This strategy requires BOS, so this is high weight
            score += 40  # BOS already confirmed in signal generation

            # 2. Trend consistency (0-20 points)
            swing_h, swing_l = find_swing_points(
                recent_data["high"], recent_data["low"], n=min(5, len(recent_data) // 4)
            )
            trend = determine_trend(swing_h, swing_l)

            if len(trend) > 0:
                current_trend = trend.iloc[-1]
                if current_trend != 0:
                    # Trend consistency
                    trend_consistency = (trend == current_trend).mean()
                    if trend_consistency > 0.8:
                        score += 20  # Very consistent trend
                    elif trend_consistency > 0.6:
                        score += 10  # Moderately consistent

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

        except Exception:
            return 60  # Default for trend-following strategy

        return min(score, 100)


def create_strategy(params: dict | None = None) -> BOSOrderBlockStrategy:
    """
    Factory function to create a BOSOrderBlockStrategy.

    Args:
        params: Optional strategy parameters

    Returns:
        Configured BOSOrderBlockStrategy instance
    """
    return BOSOrderBlockStrategy(params)


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_strategy_requires_bos_confirmation
# [ ] test_bullish_bos_creates_long_setup
# [ ] test_bearish_bos_creates_short_setup
# [ ] test_finds_recent_ob_before_bos
# [ ] test_waits_for_ob_retest_after_bos
# [ ] test_stop_loss_below_ob_for_long
# [ ] test_stop_loss_above_ob_for_short
# [ ] test_take_profit_uses_3_1_rr_minimum
# [ ] test_filters_by_min_rr_ratio
# [ ] test_confidence_weighted_for_bos
# [ ] test_confidence_considers_trend_consistency
# [ ] test_confidence_considers_volume
# [ ] test_no_signals_without_bos
# [ ] test_no_signals_without_ob
# [ ] test_respects_ob_validity_bars
# [ ] test_ob_retest_detected_correctly
# =============================================================================
