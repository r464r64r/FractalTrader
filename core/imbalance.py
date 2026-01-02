"""
Fair Value Gap (FVG) detection for Smart Money Concepts.

This module identifies imbalances in price action - areas where price
moved so aggressively that it left "gaps" between candles. These gaps
often get filled as price returns to fair value.
"""

from typing import Literal

import pandas as pd


def find_fair_value_gaps(
    high: pd.Series, low: pd.Series, min_gap_percent: float = 0.001  # Minimum 0.1% gap
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Identify Fair Value Gaps (imbalances).

    A Fair Value Gap is a 3-candle pattern where:
    - Bullish FVG: Gap between candle[i-2].high and candle[i].low
      (candle[i-1] is the impulse candle)
    - Bearish FVG: Gap between candle[i-2].low and candle[i].high
      (candle[i-1] is the impulse candle)

    The gap represents aggressive institutional buying/selling.

    Args:
        high: Series of high prices
        low: Series of low prices
        min_gap_percent: Minimum gap size as percentage (0.001 = 0.1%)

    Returns:
        bullish_fvg: DataFrame with columns [gap_high, gap_low, filled, fill_idx]
        bearish_fvg: DataFrame with columns [gap_high, gap_low, filled, fill_idx]

    Example:
        >>> bullish_fvg, bearish_fvg = find_fair_value_gaps(
        ...     data['high'], data['low'], min_gap_percent=0.002
        ... )
        >>> active_fvg = bullish_fvg[~bullish_fvg['filled']]
    """
    if len(high) < 3:
        empty_df = pd.DataFrame(columns=["gap_high", "gap_low", "filled", "fill_idx"])
        return empty_df, empty_df

    bullish_fvgs = []
    bearish_fvgs = []

    high_values = high.values
    low_values = low.values
    index = high.index

    # Scan for 3-candle patterns
    for i in range(2, len(high)):
        # Bullish FVG: gap between candle[i-2].high and candle[i].low
        # This means candle[i-1] moved up so fast it left a gap
        gap_low_bull = high_values[i - 2]  # Top of candle 2 bars ago
        gap_high_bull = low_values[i]  # Bottom of current candle

        if gap_high_bull > gap_low_bull:
            # There's a gap (current low > old high)
            gap_size = (gap_high_bull - gap_low_bull) / gap_low_bull

            if gap_size >= min_gap_percent:
                bullish_fvgs.append(
                    {
                        "timestamp": index[i],
                        "gap_high": gap_high_bull,
                        "gap_low": gap_low_bull,
                        "filled": False,
                        "fill_idx": None,
                    }
                )

        # Bearish FVG: gap between candle[i-2].low and candle[i].high
        # This means candle[i-1] moved down so fast it left a gap
        gap_high_bear = low_values[i - 2]  # Bottom of candle 2 bars ago
        gap_low_bear = high_values[i]  # Top of current candle

        if gap_high_bear > gap_low_bear:
            # There's a gap (old low > current high)
            gap_size = (gap_high_bear - gap_low_bear) / gap_low_bear

            if gap_size >= min_gap_percent:
                bearish_fvgs.append(
                    {
                        "timestamp": index[i],
                        "gap_high": gap_high_bear,
                        "gap_low": gap_low_bear,
                        "filled": False,
                        "fill_idx": None,
                    }
                )

    # Convert to DataFrames
    if bullish_fvgs:
        bullish_df = pd.DataFrame(bullish_fvgs).set_index("timestamp")
    else:
        bullish_df = pd.DataFrame(columns=["gap_high", "gap_low", "filled", "fill_idx"])

    if bearish_fvgs:
        bearish_df = pd.DataFrame(bearish_fvgs).set_index("timestamp")
    else:
        bearish_df = pd.DataFrame(columns=["gap_high", "gap_low", "filled", "fill_idx"])

    return bullish_df, bearish_df


def check_fvg_fill(
    high: pd.Series,
    low: pd.Series,
    fvg_zones: pd.DataFrame,
    fill_type: Literal["full", "partial"] = "partial",
    partial_percent: float = 0.5,
) -> pd.Series:
    """
    Check if price has returned to fill FVG zones.

    Args:
        high: Series of high prices
        low: Series of low prices
        fvg_zones: DataFrame from find_fair_value_gaps (one direction)
        fill_type: 'full' (price must fill entire gap) or 'partial' (50% fill)
        partial_percent: Percentage of gap that must be filled (0.5 = 50%)

    Returns:
        Boolean series marking bars where price enters unfilled FVG

    Example:
        >>> bullish_fvg, _ = find_fair_value_gaps(data['high'], data['low'])
        >>> fills = check_fvg_fill(data['high'], data['low'], bullish_fvg)
        >>> entry_signals = fills[fills == True]
    """
    fills = pd.Series(False, index=high.index)

    if len(fvg_zones) == 0:
        return fills

    # For each bar, check if it enters any unfilled FVG
    for idx in high.index:
        current_high = high.loc[idx]
        current_low = low.loc[idx]

        # Check all FVGs that were created before this bar
        prior_fvgs = fvg_zones[fvg_zones.index < idx]

        for fvg_idx, fvg in prior_fvgs.iterrows():
            # Skip if already filled
            if fvg["filled"]:
                continue

            gap_high = fvg["gap_high"]
            gap_low = fvg["gap_low"]

            # Calculate fill threshold
            if fill_type == "full":
                # For bullish FVG, price must reach gap_low (bottom)
                # For bearish FVG, price must reach gap_high (top)
                # We detect this by checking if price enters the zone
                fill_threshold_low = gap_low
                fill_threshold_high = gap_high
            else:  # partial
                gap_size = gap_high - gap_low
                gap_mid = gap_low + (gap_size * partial_percent)
                fill_threshold_low = gap_low
                fill_threshold_high = gap_mid

            # Check if current bar enters the FVG zone
            if current_low <= fill_threshold_high and current_high >= fill_threshold_low:
                fills.loc[idx] = True
                # Mark this FVG as filled in the original dataframe
                # Note: This modifies the input dataframe
                fvg_zones.loc[fvg_idx, "filled"] = True
                fvg_zones.loc[fvg_idx, "fill_idx"] = idx

    return fills


def get_active_fvgs(
    fvg_zones: pd.DataFrame, current_idx: pd.Timestamp, max_age_bars: int = 50
) -> pd.DataFrame:
    """
    Get active (unfilled) FVGs within age limit.

    Args:
        fvg_zones: DataFrame from find_fair_value_gaps
        current_idx: Current timestamp
        max_age_bars: Maximum age in bars (ignore older FVGs)

    Returns:
        DataFrame with active FVGs only

    Example:
        >>> bullish_fvg, _ = find_fair_value_gaps(data['high'], data['low'])
        >>> active = get_active_fvgs(bullish_fvg, data.index[-1], max_age_bars=30)
    """
    if len(fvg_zones) == 0:
        return fvg_zones

    # Filter unfilled FVGs
    active = fvg_zones[fvg_zones["filled"] == False].copy()

    # Filter by age
    if max_age_bars is not None and len(active) > 0:
        # Get position of current_idx in the original index
        if current_idx in fvg_zones.index:
            current_pos = list(fvg_zones.index).index(current_idx)
        else:
            # If current_idx not in FVG index, use the full index from high/low
            return active

        # Keep only FVGs within max_age_bars
        valid_fvgs = []
        for fvg_idx in active.index:
            fvg_pos = list(fvg_zones.index).index(fvg_idx)
            age = current_pos - fvg_pos
            if age <= max_age_bars:
                valid_fvgs.append(fvg_idx)

        active = active.loc[valid_fvgs] if valid_fvgs else pd.DataFrame(columns=active.columns)

    return active


def calculate_fvg_size(fvg_zones: pd.DataFrame) -> pd.Series:
    """
    Calculate the size of each FVG as percentage.

    Args:
        fvg_zones: DataFrame from find_fair_value_gaps

    Returns:
        Series with gap sizes as percentages

    Example:
        >>> bullish_fvg, _ = find_fair_value_gaps(data['high'], data['low'])
        >>> sizes = calculate_fvg_size(bullish_fvg)
        >>> large_gaps = bullish_fvg[sizes > 0.01]  # > 1% gaps
    """
    if len(fvg_zones) == 0:
        return pd.Series(dtype=float)

    gap_sizes = (fvg_zones["gap_high"] - fvg_zones["gap_low"]) / fvg_zones["gap_low"]
    return gap_sizes


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_find_fair_value_gaps_detects_bullish_fvg
# [ ] test_find_fair_value_gaps_detects_bearish_fvg
# [ ] test_bullish_fvg_requires_gap_between_high_and_low
# [ ] test_bearish_fvg_requires_gap_between_low_and_high
# [ ] test_min_gap_percent_filters_small_gaps
# [ ] test_returns_empty_dataframe_when_no_gaps
# [ ] test_returns_empty_for_insufficient_data
# [ ] test_fvg_dataframe_has_required_columns
# [ ] test_check_fvg_fill_detects_full_fill
# [ ] test_check_fvg_fill_detects_partial_fill
# [ ] test_partial_fill_respects_percent_threshold
# [ ] test_fvg_marked_as_filled_after_fill
# [ ] test_fill_idx_recorded_correctly
# [ ] test_get_active_fvgs_returns_unfilled_only
# [ ] test_get_active_fvgs_respects_max_age
# [ ] test_calculate_fvg_size_returns_percentages
# [ ] test_calculate_fvg_size_handles_empty_input
# =============================================================================
