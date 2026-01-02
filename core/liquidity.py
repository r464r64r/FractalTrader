"""
Liquidity detection for Smart Money Concepts.

This module provides functions for detecting:
- Equal highs and equal lows (liquidity pools)
- Liquidity sweeps (stop hunts)

These patterns reveal where institutions hunt retail stop losses
before making significant moves.
"""

from typing import Literal

import numpy as np
import pandas as pd


def find_equal_levels(
    highs: pd.Series, lows: pd.Series, tolerance: float = 0.001, min_touches: int = 2
) -> tuple[pd.Series, pd.Series]:
    """
    Find equal highs and equal lows (liquidity pools).

    Equal levels are areas where price made similar highs or lows within
    a tolerance. These areas accumulate stop losses and become liquidity
    pools that institutions target.

    Args:
        highs: Series with swing high prices (from find_swing_points, NaN elsewhere)
        lows: Series with swing low prices (from find_swing_points, NaN elsewhere)
        tolerance: Price tolerance for considering levels "equal" (0.001 = 0.1%)
        min_touches: Minimum number of touches to form an equal level

    Returns:
        equal_highs: Series with equal high level prices at detection bars (NaN elsewhere)
        equal_lows: Series with equal low level prices at detection bars (NaN elsewhere)

    Example:
        >>> swing_h, swing_l = find_swing_points(data['high'], data['low'])
        >>> eqh, eql = find_equal_levels(swing_h, swing_l, tolerance=0.001)
    """
    equal_highs = pd.Series(np.nan, index=highs.index)
    equal_lows = pd.Series(np.nan, index=lows.index)

    # Process highs
    valid_highs = highs.dropna()
    if len(valid_highs) >= min_touches:
        equal_highs = _find_clustered_levels(valid_highs, tolerance, min_touches, highs.index)

    # Process lows
    valid_lows = lows.dropna()
    if len(valid_lows) >= min_touches:
        equal_lows = _find_clustered_levels(valid_lows, tolerance, min_touches, lows.index)

    return equal_highs, equal_lows


def _find_clustered_levels(
    levels: pd.Series, tolerance: float, min_touches: int, full_index: pd.Index
) -> pd.Series:
    """
    Find clustered price levels within tolerance.

    Args:
        levels: Series of price levels (non-NaN swing points)
        tolerance: Relative tolerance for clustering
        min_touches: Minimum touches to form a cluster
        full_index: Full index for output series

    Returns:
        Series with cluster prices at the last touch of each cluster
    """
    result = pd.Series(np.nan, index=full_index)

    if len(levels) < min_touches:
        return result

    values = levels.values
    indices = levels.index

    # Track which levels have been assigned to a cluster
    assigned = set()

    for i, (idx, price) in enumerate(zip(indices, values)):
        if i in assigned:
            continue

        # Find all levels within tolerance of this price
        cluster_mask = np.abs(values - price) / price <= tolerance
        cluster_indices = np.where(cluster_mask)[0]

        if len(cluster_indices) >= min_touches:
            # Mark all as assigned
            assigned.update(cluster_indices)

            # Calculate the average level price
            cluster_prices = values[cluster_indices]
            avg_price = np.mean(cluster_prices)

            # Mark the cluster at the last touch
            last_touch_iloc = cluster_indices[-1]
            last_touch_idx = indices[last_touch_iloc]
            result.loc[last_touch_idx] = avg_price

    return result


def detect_liquidity_sweep(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    liquidity_levels: pd.Series,
    reversal_bars: int = 3,
    direction: Literal["bullish", "bearish", "both"] = "both",
) -> pd.Series:
    """
    Detect liquidity sweeps (stop hunts).

    A sweep occurs when:
    1. Price exceeds a liquidity level (breaks beyond it)
    2. Price reverses within reversal_bars
    3. Close returns inside the level

    Bullish sweep: Price breaks below liquidity, then closes back above
    Bearish sweep: Price breaks above liquidity, then closes back below

    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of close prices
        liquidity_levels: Series with liquidity level prices
        reversal_bars: Maximum bars for reversal to occur
        direction: 'bullish' (sweep below), 'bearish' (sweep above), or 'both'

    Returns:
        Boolean series marking sweep completion bars

    Example:
        >>> # Detect bullish sweeps of equal lows
        >>> sweeps = detect_liquidity_sweep(
        ...     data['high'], data['low'], data['close'],
        ...     equal_lows, reversal_bars=3, direction='bullish'
        ... )
    """
    sweeps = pd.Series(False, index=high.index)

    # Get valid liquidity levels
    valid_levels = liquidity_levels.dropna()

    if len(valid_levels) == 0:
        return sweeps

    # Convert to list for iteration
    index_list = list(high.index)

    # For each liquidity level, look for sweeps
    for level_idx, level_price in valid_levels.items():
        level_pos = index_list.index(level_idx)

        # Look at bars after the level was established
        for i in range(level_pos + 1, len(index_list)):
            idx = index_list[i]
            current_high = high.iloc[i]
            current_low = low.iloc[i]
            current_close = close.iloc[i]

            # Check for bullish sweep (break below, then close above)
            if direction in ("bullish", "both") and current_low < level_price:
                # Found a break below - look for reversal
                for j in range(i, min(i + reversal_bars + 1, len(index_list))):
                    reversal_idx = index_list[j]
                    reversal_close = close.iloc[j]

                    if reversal_close > level_price:
                        # Reversal complete
                        sweeps.loc[reversal_idx] = True
                        break
                # After finding a sweep attempt, move past this level
                break

            # Check for bearish sweep (break above, then close below)
            if direction in ("bearish", "both") and current_high > level_price:
                # Found a break above - look for reversal
                for j in range(i, min(i + reversal_bars + 1, len(index_list))):
                    reversal_idx = index_list[j]
                    reversal_close = close.iloc[j]

                    if reversal_close < level_price:
                        # Reversal complete
                        sweeps.loc[reversal_idx] = True
                        break
                # After finding a sweep attempt, move past this level
                break

    return sweeps


def find_liquidity_zones(
    swing_highs: pd.Series, swing_lows: pd.Series, tolerance: float = 0.001
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Find all liquidity zones (areas of clustered highs or lows).

    Args:
        swing_highs: Series with swing high prices
        swing_lows: Series with swing low prices
        tolerance: Tolerance for level clustering

    Returns:
        high_zones: DataFrame with columns [level_price, first_touch, last_touch, touch_count]
        low_zones: DataFrame with columns [level_price, first_touch, last_touch, touch_count]
    """
    high_zones = _calculate_zones(swing_highs.dropna(), tolerance)
    low_zones = _calculate_zones(swing_lows.dropna(), tolerance)

    return high_zones, low_zones


def _calculate_zones(levels: pd.Series, tolerance: float) -> pd.DataFrame:
    """Calculate liquidity zones from swing levels."""
    columns = ["level_price", "first_touch", "last_touch", "touch_count"]

    if len(levels) == 0:
        return pd.DataFrame(columns=columns)

    zones = []
    values = levels.values
    indices = levels.index
    assigned = set()

    for i, (idx, price) in enumerate(zip(indices, values)):
        if i in assigned:
            continue

        # Find all levels within tolerance
        cluster_mask = np.abs(values - price) / price <= tolerance
        cluster_indices = np.where(cluster_mask)[0]

        if len(cluster_indices) >= 2:
            assigned.update(cluster_indices)

            cluster_prices = values[cluster_indices]
            cluster_times = [indices[j] for j in cluster_indices]

            zones.append(
                {
                    "level_price": np.mean(cluster_prices),
                    "first_touch": min(cluster_times),
                    "last_touch": max(cluster_times),
                    "touch_count": len(cluster_indices),
                }
            )

    return pd.DataFrame(zones)


def get_nearest_liquidity(
    price: float,
    swing_highs: pd.Series,
    swing_lows: pd.Series,
    current_idx: pd.Timestamp,
    direction: Literal["above", "below", "both"] = "both",
) -> dict | None:
    """
    Find the nearest liquidity level to current price.

    Args:
        price: Current price
        swing_highs: Series with swing high prices
        swing_lows: Series with swing low prices
        current_idx: Current timestamp (only consider levels before this)
        direction: 'above', 'below', or 'both'

    Returns:
        Dictionary with 'price', 'distance', 'type' or None if not found
    """
    candidates = []

    # Get levels before current index
    prior_highs = swing_highs[swing_highs.index < current_idx].dropna()
    prior_lows = swing_lows[swing_lows.index < current_idx].dropna()

    if direction in ("above", "both"):
        for level in prior_highs.values:
            if level > price:
                candidates.append({"price": level, "distance": level - price, "type": "swing_high"})

    if direction in ("below", "both"):
        for level in prior_lows.values:
            if level < price:
                candidates.append({"price": level, "distance": price - level, "type": "swing_low"})

    if not candidates:
        return None

    # Return nearest
    return min(candidates, key=lambda x: x["distance"])
