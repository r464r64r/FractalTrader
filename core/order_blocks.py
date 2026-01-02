"""
Order Block detection for Smart Money Concepts.

This module identifies Order Blocks - areas where institutions accumulated
or distributed positions before making significant moves. These zones often
act as strong support/resistance on retest.
"""

from typing import Literal

import pandas as pd


def find_order_blocks(
    open_price: pd.Series,
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    min_impulse_percent: float = 0.01,  # Minimum 1% impulse move
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identify Order Blocks.

    An Order Block is the last opposite-colored candle before an impulse move:
    - Bullish OB: Last down candle before bullish impulse (accumulation zone)
    - Bearish OB: Last up candle before bearish impulse (distribution zone)

    Args:
        open_price: Series of open prices
        high: Series of high prices
        low: Series of low prices
        close: Series of close prices
        min_impulse_percent: Minimum impulse move size (0.01 = 1%)

    Returns:
        bullish_ob: DataFrame with columns [ob_high, ob_low, invalidated, retest_count]
        bearish_ob: DataFrame with columns [ob_high, ob_low, invalidated, retest_count]

    Example:
        >>> bullish_ob, bearish_ob = find_order_blocks(
        ...     data['open'], data['high'], data['low'], data['close']
        ... )
        >>> valid_obs = bullish_ob[~bullish_ob['invalidated']]
    """
    if len(close) < 3:
        empty_df = pd.DataFrame(columns=["ob_high", "ob_low", "invalidated", "retest_count"])
        return empty_df, empty_df

    bullish_obs = []
    bearish_obs = []

    open_vals = open_price.values
    high_vals = high.values
    low_vals = low.values
    close_vals = close.values
    index = close.index

    # Scan for impulse moves
    for i in range(1, len(close) - 1):
        # Check for bullish impulse (strong up move)
        current_close = close_vals[i + 1]
        prev_close = close_vals[i]

        # Bullish impulse: next candle closes significantly higher
        if current_close > prev_close * (1 + min_impulse_percent):
            # Look for the last down candle before this impulse
            # The down candle is the order block
            if close_vals[i] < open_vals[i]:  # Current candle is down
                bullish_obs.append(
                    {
                        "timestamp": index[i],
                        "ob_high": high_vals[i],
                        "ob_low": low_vals[i],
                        "invalidated": False,
                        "retest_count": 0,
                    }
                )

        # Bearish impulse: next candle closes significantly lower
        if current_close < prev_close * (1 - min_impulse_percent):
            # Look for the last up candle before this impulse
            if close_vals[i] > open_vals[i]:  # Current candle is up
                bearish_obs.append(
                    {
                        "timestamp": index[i],
                        "ob_high": high_vals[i],
                        "ob_low": low_vals[i],
                        "invalidated": False,
                        "retest_count": 0,
                    }
                )

    # Convert to DataFrames
    if bullish_obs:
        bullish_df = pd.DataFrame(bullish_obs).set_index("timestamp")
    else:
        bullish_df = pd.DataFrame(columns=["ob_high", "ob_low", "invalidated", "retest_count"])

    if bearish_obs:
        bearish_df = pd.DataFrame(bearish_obs).set_index("timestamp")
    else:
        bearish_df = pd.DataFrame(columns=["ob_high", "ob_low", "invalidated", "retest_count"])

    return bullish_df, bearish_df


def check_ob_retest(
    high: pd.Series,
    low: pd.Series,
    order_blocks: pd.DataFrame,
    direction: Literal["bullish", "bearish"] = "bullish",
) -> pd.Series:
    """
    Check if price is retesting a valid order block.

    A retest occurs when price returns to the OB zone without invalidating it.

    Args:
        high: Series of high prices
        low: Series of low prices
        order_blocks: DataFrame from find_order_blocks (one direction)
        direction: 'bullish' or 'bearish'

    Returns:
        Boolean series marking bars where price retests valid OB

    Example:
        >>> bullish_ob, _ = find_order_blocks(data['open'], data['high'],
        ...                                    data['low'], data['close'])
        >>> retests = check_ob_retest(data['high'], data['low'],
        ...                           bullish_ob, direction='bullish')
    """
    retests = pd.Series(False, index=high.index)

    if len(order_blocks) == 0:
        return retests

    for idx in high.index:
        current_high = high.loc[idx]
        current_low = low.loc[idx]

        # Check all OBs created before this bar
        prior_obs = order_blocks[order_blocks.index < idx]

        for ob_idx, ob in prior_obs.iterrows():
            # Skip invalidated OBs
            if ob["invalidated"]:
                continue

            ob_high = ob["ob_high"]
            ob_low = ob["ob_low"]

            # Check for retest (price enters OB zone)
            if current_low <= ob_high and current_high >= ob_low:
                retests.loc[idx] = True

                # Increment retest count
                order_blocks.loc[ob_idx, "retest_count"] += 1

                # Check for invalidation
                if direction == "bullish":
                    # Bullish OB invalidated if price closes below OB low
                    if current_low < ob_low:
                        order_blocks.loc[ob_idx, "invalidated"] = True
                else:  # bearish
                    # Bearish OB invalidated if price closes above OB high
                    if current_high > ob_high:
                        order_blocks.loc[ob_idx, "invalidated"] = True

    return retests


def get_valid_order_blocks(
    order_blocks: pd.DataFrame, current_idx: pd.Timestamp, max_age_bars: int = 50
) -> pd.DataFrame:
    """
    Get valid (non-invalidated) order blocks within age limit.

    Args:
        order_blocks: DataFrame from find_order_blocks
        current_idx: Current timestamp
        max_age_bars: Maximum age in bars

    Returns:
        DataFrame with valid OBs only

    Example:
        >>> bullish_ob, _ = find_order_blocks(data['open'], data['high'],
        ...                                    data['low'], data['close'])
        >>> valid = get_valid_order_blocks(bullish_ob, data.index[-1])
    """
    if len(order_blocks) == 0:
        return order_blocks

    # Filter non-invalidated
    valid = order_blocks[order_blocks["invalidated"] == False].copy()

    # Filter by age (implementation simplified - would need full index for precise age)
    if max_age_bars is not None and len(valid) > 0:
        # Keep recent ones
        valid = valid.tail(max_age_bars)

    return valid


def get_nearest_order_block(
    price: float,
    order_blocks: pd.DataFrame,
    current_idx: pd.Timestamp,
    direction: Literal["above", "below"] = "below",
) -> dict | None:
    """
    Find the nearest valid order block to current price.

    Args:
        price: Current price
        order_blocks: DataFrame from find_order_blocks
        current_idx: Current timestamp
        direction: 'above' (look for OBs above price) or 'below'

    Returns:
        Dictionary with OB details or None if not found

    Example:
        >>> bullish_ob, _ = find_order_blocks(data['open'], data['high'],
        ...                                    data['low'], data['close'])
        >>> nearest = get_nearest_order_block(100, bullish_ob,
        ...                                   data.index[-1], 'below')
    """
    valid_obs = get_valid_order_blocks(order_blocks, current_idx)

    if len(valid_obs) == 0:
        return None

    # Filter by direction
    candidates = []
    for ob_idx, ob in valid_obs.iterrows():
        ob_mid = (ob["ob_high"] + ob["ob_low"]) / 2

        if direction == "below" and ob_mid < price:
            candidates.append(
                {
                    "timestamp": ob_idx,
                    "ob_high": ob["ob_high"],
                    "ob_low": ob["ob_low"],
                    "distance": price - ob_mid,
                    "retest_count": ob["retest_count"],
                }
            )
        elif direction == "above" and ob_mid > price:
            candidates.append(
                {
                    "timestamp": ob_idx,
                    "ob_high": ob["ob_high"],
                    "ob_low": ob["ob_low"],
                    "distance": ob_mid - price,
                    "retest_count": ob["retest_count"],
                }
            )

    if not candidates:
        return None

    # Return nearest
    return min(candidates, key=lambda x: x["distance"])


def calculate_ob_strength(order_blocks: pd.DataFrame, volume: pd.Series | None = None) -> pd.Series:
    """
    Calculate strength score for each order block.

    Strength factors:
    - Retest count (more retests = stronger)
    - Volume at OB formation (if provided)
    - OB size (larger = stronger institutional presence)

    Args:
        order_blocks: DataFrame from find_order_blocks
        volume: Optional volume series

    Returns:
        Series with strength scores (0-100)

    Example:
        >>> bullish_ob, _ = find_order_blocks(data['open'], data['high'],
        ...                                    data['low'], data['close'])
        >>> strength = calculate_ob_strength(bullish_ob, data['volume'])
        >>> strong_obs = bullish_ob[strength > 70]
    """
    if len(order_blocks) == 0:
        return pd.Series(dtype=float)

    strength = pd.Series(0.0, index=order_blocks.index)

    # Factor 1: Retest count (0-50 points)
    max_retests = order_blocks["retest_count"].max()
    if max_retests > 0:
        retest_score = (order_blocks["retest_count"] / max_retests) * 50
    else:
        retest_score = 0

    strength += retest_score

    # Factor 2: OB size (0-25 points)
    ob_size = order_blocks["ob_high"] - order_blocks["ob_low"]
    ob_size_pct = ob_size / order_blocks["ob_low"]
    max_size = ob_size_pct.max()
    if max_size > 0:
        size_score = (ob_size_pct / max_size) * 25
    else:
        size_score = 0

    strength += size_score

    # Factor 3: Base score (25 points for being identified)
    strength += 25

    return strength.clip(0, 100)


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_find_order_blocks_detects_bullish_ob
# [ ] test_find_order_blocks_detects_bearish_ob
# [ ] test_bullish_ob_is_down_candle_before_impulse
# [ ] test_bearish_ob_is_up_candle_before_impulse
# [ ] test_min_impulse_percent_filters_small_moves
# [ ] test_returns_empty_dataframe_when_no_obs
# [ ] test_returns_empty_for_insufficient_data
# [ ] test_ob_dataframe_has_required_columns
# [ ] test_check_ob_retest_detects_price_entering_zone
# [ ] test_ob_invalidated_when_price_breaks_zone
# [ ] test_bullish_ob_invalidated_below_low
# [ ] test_bearish_ob_invalidated_above_high
# [ ] test_retest_count_increments
# [ ] test_get_valid_order_blocks_filters_invalidated
# [ ] test_get_valid_order_blocks_respects_max_age
# [ ] test_get_nearest_order_block_finds_below
# [ ] test_get_nearest_order_block_finds_above
# [ ] test_get_nearest_returns_none_when_no_valid
# [ ] test_calculate_ob_strength_considers_retests
# [ ] test_calculate_ob_strength_considers_size
# [ ] test_ob_strength_capped_at_100
# =============================================================================
