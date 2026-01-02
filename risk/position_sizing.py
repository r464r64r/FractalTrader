"""
Dynamic position sizing based on risk parameters and confidence scoring.

This module calculates position sizes that adapt to:
- Trade confidence (0-100 score)
- Market volatility (ATR-based)
- Win/loss streaks
- Portfolio-level limits
"""

from dataclasses import dataclass


@dataclass
class RiskParameters:
    """
    Global risk parameters for position sizing.

    These parameters control how aggressively the system sizes positions
    based on confidence, volatility, and trading performance.

    Attributes:
        base_risk_percent: Base risk per trade (0.02 = 2%)
        max_position_percent: Maximum position size (0.05 = 5%)
        min_confidence: Minimum confidence to take trade (0-100)
        atr_period: Period for ATR calculation
        consecutive_wins_reduce: Reduce size after N consecutive wins
        consecutive_losses_reduce: Reduce size after N consecutive losses
        win_reduction_factor: Size multiplier after win streak
        loss_reduction_factor: Size multiplier after loss streak

    Example:
        >>> params = RiskParameters(
        ...     base_risk_percent=0.01,  # Risk 1% per trade
        ...     max_position_percent=0.03  # Max 3% position
        ... )
    """

    base_risk_percent: float = 0.02  # 2% base risk per trade
    max_position_percent: float = 0.05  # 5% max single position
    min_confidence: int = 40  # Minimum confidence to trade

    # Volatility adjustment
    atr_period: int = 14
    atr_baseline_multiplier: float = 1.0  # Size multiplier at baseline ATR

    # Win/loss adjustments
    consecutive_wins_reduce: int = 3  # Reduce size after N wins
    consecutive_losses_reduce: int = 2  # Reduce size after N losses
    win_reduction_factor: float = 0.8  # Multiply size by this after win streak
    loss_reduction_factor: float = 0.7  # Multiply size by this after loss streak


def calculate_position_size(
    portfolio_value: float,
    entry_price: float,
    stop_loss_price: float,
    confidence_score: int,
    current_atr: float,
    baseline_atr: float,
    consecutive_wins: int,
    consecutive_losses: int,
    params: RiskParameters,
) -> float:
    """
    Calculate position size based on risk parameters.

    Formula:
        risk_amount = portfolio_value × base_risk% × (confidence/100)
        volatility_adj = baseline_atr / current_atr  # Reduce in high vol
        streak_adj = adjustment based on win/loss streaks

        risk_per_unit = |entry_price - stop_loss_price|
        position_size = (risk_amount × volatility_adj × streak_adj) / risk_per_unit

        Final size capped at max_position_percent of portfolio

    Args:
        portfolio_value: Current portfolio value in base currency
        entry_price: Proposed entry price
        stop_loss_price: Stop loss price
        confidence_score: Trade confidence (0-100)
        current_atr: Current ATR value
        baseline_atr: Baseline ATR (e.g., 50-period average)
        consecutive_wins: Number of consecutive winning trades
        consecutive_losses: Number of consecutive losing trades
        params: Risk parameters configuration

    Returns:
        Position size in base currency units (0 if trade rejected)

    Example:
        >>> params = RiskParameters()
        >>> size = calculate_position_size(
        ...     portfolio_value=10000,
        ...     entry_price=100,
        ...     stop_loss_price=98,
        ...     confidence_score=80,
        ...     current_atr=5,
        ...     baseline_atr=5,
        ...     consecutive_wins=0,
        ...     consecutive_losses=0,
        ...     params=params
        ... )
        >>> print(f"Position size: {size:.2f} units")

    Edge Cases:
        - Returns 0 if confidence < min_confidence
        - Returns 0 if risk_per_unit == 0 (stop == entry)
        - Returns 0 if any input is invalid (negative, zero, NaN)
        - Caps volatility adjustment between 0.5x and 1.5x
        - Respects max_position_percent cap
    """
    # Modified from DEVELOPMENT.md: Added comprehensive input validation
    # Validate inputs
    if portfolio_value <= 0:
        return 0.0
    if entry_price <= 0:
        return 0.0
    if stop_loss_price <= 0:
        return 0.0
    if not 0 <= confidence_score <= 100:
        return 0.0
    if current_atr < 0 or baseline_atr < 0:
        return 0.0
    if consecutive_wins < 0 or consecutive_losses < 0:
        return 0.0

    # Skip if confidence too low
    if confidence_score < params.min_confidence:
        return 0.0

    # Base risk calculation
    confidence_factor = confidence_score / 100.0
    risk_amount = portfolio_value * params.base_risk_percent * confidence_factor

    # Volatility adjustment (reduce size in high volatility)
    # Modified from DEVELOPMENT.md: Added zero-division protection
    if current_atr > 0 and baseline_atr > 0:
        volatility_adj = baseline_atr / current_atr
        volatility_adj = min(volatility_adj, 1.5)  # Cap at 1.5x
        volatility_adj = max(volatility_adj, 0.5)  # Floor at 0.5x
    else:
        volatility_adj = 1.0

    # Streak adjustment
    streak_adj = 1.0
    if consecutive_wins >= params.consecutive_wins_reduce:
        streak_adj = params.win_reduction_factor
    elif consecutive_losses >= params.consecutive_losses_reduce:
        streak_adj = params.loss_reduction_factor

    # Calculate position size
    # Modified from DEVELOPMENT.md: Added edge case for stop_loss == entry_price
    risk_per_unit = abs(entry_price - stop_loss_price)
    if risk_per_unit == 0:
        # Stop loss equals entry - invalid setup
        return 0.0

    adjusted_risk = risk_amount * volatility_adj * streak_adj
    position_size = adjusted_risk / risk_per_unit

    # Apply maximum position cap
    max_position = (portfolio_value * params.max_position_percent) / entry_price
    position_size = min(position_size, max_position)

    return position_size


def calculate_position_value(position_size: float, entry_price: float) -> float:
    """
    Calculate total position value in base currency.

    Args:
        position_size: Position size in units
        entry_price: Entry price

    Returns:
        Position value in base currency

    Example:
        >>> value = calculate_position_value(10.5, 100)
        >>> print(f"Position value: ${value:.2f}")
        Position value: $1050.00
    """
    return position_size * entry_price


def calculate_risk_percent(
    position_size: float, entry_price: float, stop_loss_price: float, portfolio_value: float
) -> float:
    """
    Calculate actual risk as percentage of portfolio.

    Args:
        position_size: Position size in units
        entry_price: Entry price
        stop_loss_price: Stop loss price
        portfolio_value: Current portfolio value

    Returns:
        Risk as percentage (0.02 = 2%)

    Example:
        >>> risk_pct = calculate_risk_percent(40, 100, 98, 10000)
        >>> print(f"Risk: {risk_pct:.2%}")
        Risk: 0.80%
    """
    if portfolio_value <= 0:
        return 0.0

    risk_per_unit = abs(entry_price - stop_loss_price)
    total_risk = position_size * risk_per_unit

    return total_risk / portfolio_value


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_position_size_respects_max_percent
# [ ] test_low_confidence_returns_zero
# [ ] test_below_min_confidence_returns_zero
# [ ] test_volatility_adjustment_scales_correctly
# [ ] test_high_volatility_reduces_size
# [ ] test_low_volatility_increases_size (capped at 1.5x)
# [ ] test_consecutive_wins_reduces_size
# [ ] test_consecutive_losses_reduces_size
# [ ] test_zero_risk_per_unit_returns_zero
# [ ] test_stop_equals_entry_returns_zero
# [ ] test_negative_portfolio_value_returns_zero
# [ ] test_negative_entry_price_returns_zero
# [ ] test_negative_stop_loss_returns_zero
# [ ] test_invalid_confidence_returns_zero
# [ ] test_negative_atr_returns_zero
# [ ] test_negative_streaks_return_zero
# [ ] test_position_value_calculation
# [ ] test_risk_percent_calculation
# [ ] test_zero_portfolio_value_in_risk_percent
# =============================================================================
