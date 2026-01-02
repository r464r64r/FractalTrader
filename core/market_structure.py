"""
Market structure detection for Smart Money Concepts.

This module provides functions for detecting:
- Swing highs and swing lows (local extrema)
- Break of Structure (BOS) - trend continuation
- Change of Character (CHoCH) - trend reversal
- Market trend based on swing point sequences
"""

from typing import Literal

import numpy as np
import pandas as pd


def find_swing_points(high: pd.Series, low: pd.Series, n: int = 5) -> tuple[pd.Series, pd.Series]:
    """
    Identify swing highs and swing lows.

    A swing high is a bar where the high is higher than N bars on both sides.
    A swing low is a bar where the low is lower than N bars on both sides.

    Args:
        high: Series of high prices
        low: Series of low prices
        n: Number of bars on each side to compare (default 5)

    Returns:
        swing_highs: Series with swing high prices at swing points (NaN elsewhere)
        swing_lows: Series with swing low prices at swing points (NaN elsewhere)

    Example:
        >>> swing_h, swing_l = find_swing_points(data['high'], data['low'], n=5)
        >>> print(f"Found {swing_h.dropna().count()} swing highs")
    """
    if len(high) < 2 * n + 1:
        return pd.Series(np.nan, index=high.index), pd.Series(np.nan, index=low.index)

    swing_highs = pd.Series(np.nan, index=high.index)
    swing_lows = pd.Series(np.nan, index=low.index)

    high_values = high.values
    low_values = low.values

    for i in range(n, len(high) - n):
        # Check swing high: current high > all highs in window on both sides
        left_highs = high_values[i - n : i]
        right_highs = high_values[i + 1 : i + n + 1]

        if high_values[i] > left_highs.max() and high_values[i] > right_highs.max():
            swing_highs.iloc[i] = high_values[i]

        # Check swing low: current low < all lows in window on both sides
        left_lows = low_values[i - n : i]
        right_lows = low_values[i + 1 : i + n + 1]

        if low_values[i] < left_lows.min() and low_values[i] < right_lows.min():
            swing_lows.iloc[i] = low_values[i]

    return swing_highs, swing_lows


def determine_trend(swing_highs: pd.Series, swing_lows: pd.Series) -> pd.Series:
    """
    Determine market trend based on swing point sequence.

    - Uptrend (1): Higher highs AND higher lows
    - Downtrend (-1): Lower highs AND lower lows
    - Ranging (0): Mixed structure

    Args:
        swing_highs: Series with swing high prices (NaN elsewhere)
        swing_lows: Series with swing low prices (NaN elsewhere)

    Returns:
        Series with values: 1 (uptrend), -1 (downtrend), 0 (ranging)
        The trend value is forward-filled to cover all bars.

    Example:
        >>> trend = determine_trend(swing_highs, swing_lows)
        >>> current_trend = trend.iloc[-1]  # 1, -1, or 0
    """
    trend = pd.Series(0, index=swing_highs.index)

    # Get valid swing points
    valid_highs = swing_highs.dropna()
    valid_lows = swing_lows.dropna()

    if len(valid_highs) < 2 or len(valid_lows) < 2:
        return trend

    # Create lists of swing points in chronological order
    swing_points = []

    for idx, val in valid_highs.items():
        swing_points.append({"idx": idx, "type": "high", "value": val})

    for idx, val in valid_lows.items():
        swing_points.append({"idx": idx, "type": "low", "value": val})

    swing_points.sort(key=lambda x: x["idx"])

    # Track last two highs and lows for trend determination
    last_highs: list[float] = []
    last_lows: list[float] = []
    current_trend = 0

    for point in swing_points:
        if point["type"] == "high":
            last_highs.append(point["value"])
            if len(last_highs) > 2:
                last_highs.pop(0)
        else:
            last_lows.append(point["value"])
            if len(last_lows) > 2:
                last_lows.pop(0)

        # Determine trend when we have at least 2 highs and 2 lows
        if len(last_highs) >= 2 and len(last_lows) >= 2:
            higher_high = last_highs[-1] > last_highs[-2]
            lower_high = last_highs[-1] < last_highs[-2]
            higher_low = last_lows[-1] > last_lows[-2]
            lower_low = last_lows[-1] < last_lows[-2]

            if higher_high and higher_low:
                current_trend = 1  # Uptrend
            elif lower_high and lower_low:
                current_trend = -1  # Downtrend
            else:
                current_trend = 0  # Ranging

        trend.loc[point["idx"]] = current_trend

    # Forward fill trend values
    trend = trend.replace(0, np.nan).ffill().fillna(0).astype(int)

    # Fix: only replace zeros after first swing point
    first_swing_idx = min(
        swing_points[0]["idx"] if swing_points else trend.index[0], trend.index[0]
    )
    trend.loc[:first_swing_idx] = 0

    return trend


def detect_structure_breaks(
    close: pd.Series, swing_highs: pd.Series, swing_lows: pd.Series
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Detect Break of Structure (BOS) and Change of Character (CHoCH) events.

    BOS (Break of Structure):
    - Bullish BOS: Price breaks above previous swing high during uptrend (continuation)
    - Bearish BOS: Price breaks below previous swing low during downtrend (continuation)

    CHoCH (Change of Character):
    - Bullish CHoCH: In downtrend, price breaks above previous swing high (reversal)
    - Bearish CHoCH: In uptrend, price breaks below previous swing low (reversal)

    Args:
        close: Series of close prices
        swing_highs: Series with swing high prices (NaN elsewhere)
        swing_lows: Series with swing low prices (NaN elsewhere)

    Returns:
        bos_bullish: Boolean series marking bullish BOS events
        bos_bearish: Boolean series marking bearish BOS events
        choch: Boolean series marking CHoCH events (both directions)

    Example:
        >>> bos_bull, bos_bear, choch = detect_structure_breaks(
        ...     data['close'], swing_highs, swing_lows
        ... )
        >>> breakout_bars = bos_bull | bos_bear | choch
    """
    bos_bullish = pd.Series(False, index=close.index)
    bos_bearish = pd.Series(False, index=close.index)
    choch = pd.Series(False, index=close.index)

    # Get trend
    trend = determine_trend(swing_highs, swing_lows)

    # Track the most recent unbroken swing levels
    last_swing_high: float | None = None
    last_swing_high_idx = None
    last_swing_low: float | None = None
    last_swing_low_idx = None

    valid_highs = swing_highs.dropna()
    valid_lows = swing_lows.dropna()

    for idx in close.index:
        current_close = close.loc[idx]
        current_trend = trend.loc[idx]

        # Update last swing high if we passed one
        if idx in valid_highs.index:
            last_swing_high = valid_highs.loc[idx]
            last_swing_high_idx = idx

        # Update last swing low if we passed one
        if idx in valid_lows.index:
            last_swing_low = valid_lows.loc[idx]
            last_swing_low_idx = idx

        # Check for breaks
        if last_swing_high is not None and idx != last_swing_high_idx:
            if current_close > last_swing_high:
                if current_trend == 1:
                    # Uptrend break of swing high = Bullish BOS (continuation)
                    bos_bullish.loc[idx] = True
                elif current_trend == -1:
                    # Downtrend break of swing high = Bullish CHoCH (reversal)
                    choch.loc[idx] = True
                else:
                    # Ranging break = BOS
                    bos_bullish.loc[idx] = True

                # Reset the broken level
                last_swing_high = None
                last_swing_high_idx = None

        if last_swing_low is not None and idx != last_swing_low_idx:
            if current_close < last_swing_low:
                if current_trend == -1:
                    # Downtrend break of swing low = Bearish BOS (continuation)
                    bos_bearish.loc[idx] = True
                elif current_trend == 1:
                    # Uptrend break of swing low = Bearish CHoCH (reversal)
                    choch.loc[idx] = True
                else:
                    # Ranging break = BOS
                    bos_bearish.loc[idx] = True

                # Reset the broken level
                last_swing_low = None
                last_swing_low_idx = None

    return bos_bullish, bos_bearish, choch


def get_swing_sequence(
    swing_highs: pd.Series, swing_lows: pd.Series, lookback: int | None = None
) -> pd.DataFrame:
    """
    Get a chronological sequence of swing points.

    Args:
        swing_highs: Series with swing high prices (NaN elsewhere)
        swing_lows: Series with swing low prices (NaN elsewhere)
        lookback: Optional limit on number of recent swings to return

    Returns:
        DataFrame with columns [timestamp, type, price] sorted by timestamp
        type is 'high' or 'low'
    """
    swings = []

    for idx, val in swing_highs.dropna().items():
        swings.append({"timestamp": idx, "type": "high", "price": val})

    for idx, val in swing_lows.dropna().items():
        swings.append({"timestamp": idx, "type": "low", "price": val})

    df = pd.DataFrame(swings)
    if len(df) == 0:
        return pd.DataFrame(columns=["timestamp", "type", "price"])

    df = df.sort_values("timestamp").reset_index(drop=True)

    if lookback is not None:
        df = df.tail(lookback)

    return df


def find_recent_swing_level(
    swing_series: pd.Series,
    current_idx: pd.Timestamp,
    direction: Literal["above", "below"] = "above",
) -> float | None:
    """
    Find the most recent swing level before current index.

    Args:
        swing_series: Series with swing prices (NaN elsewhere)
        current_idx: Current timestamp to look before
        direction: 'above' for swing highs, 'below' for swing lows

    Returns:
        Most recent swing price or None if not found
    """
    valid = swing_series.dropna()
    prior = valid[valid.index < current_idx]

    if len(prior) == 0:
        return None

    return prior.iloc[-1]
