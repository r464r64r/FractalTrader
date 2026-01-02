"""Tests for risk management modules."""

import pytest

from risk.confidence import ConfidenceFactors
from risk.position_sizing import (
    RiskParameters,
    calculate_position_size,
    calculate_position_value,
    calculate_risk_percent,
)


class TestConfidenceFactors:
    """Tests for ConfidenceFactors scoring."""

    def test_confidence_score_zero_by_default(self):
        """Default ConfidenceFactors should score 0."""
        factors = ConfidenceFactors()
        assert factors.calculate_score() == 0

    def test_confidence_score_max_100(self):
        """Confidence score should be capped at 100."""
        # Try to exceed 100 with excessive confluences
        factors = ConfidenceFactors(
            htf_trend_aligned=True,
            htf_structure_clean=True,
            pattern_clean=True,
            multiple_confluences=100,  # Way more than needed
            volume_spike=True,
            volume_divergence=True,
            trending_market=True,
            low_volatility=True,
        )
        assert factors.calculate_score() == 100

    def test_htf_alignment_adds_30_points(self):
        """HTF alignment factors should add exactly 30 points."""
        factors = ConfidenceFactors(htf_trend_aligned=True, htf_structure_clean=True)  # +15  # +15
        assert factors.calculate_score() == 30

    def test_pattern_strength_adds_30_points(self):
        """Pattern strength factors should add exactly 30 points."""
        factors = ConfidenceFactors(
            pattern_clean=True, multiple_confluences=4  # +10  # +20 (4 × 5, capped)
        )
        assert factors.calculate_score() == 30

    def test_volume_confirmation_adds_20_points(self):
        """Volume confirmation factors should add exactly 20 points."""
        factors = ConfidenceFactors(volume_spike=True, volume_divergence=True)  # +10  # +10
        assert factors.calculate_score() == 20

    def test_market_regime_adds_20_points(self):
        """Market regime factors should add exactly 20 points."""
        factors = ConfidenceFactors(trending_market=True, low_volatility=True)  # +10  # +10
        assert factors.calculate_score() == 20

    def test_multiple_confluences_capped_at_20(self):
        """Multiple confluences should cap at 20 points (4 confluences × 5)."""
        # 3 confluences = 15 points
        factors_3 = ConfidenceFactors(multiple_confluences=3)
        assert factors_3.calculate_score() == 15

        # 4 confluences = 20 points
        factors_4 = ConfidenceFactors(multiple_confluences=4)
        assert factors_4.calculate_score() == 20

        # 10 confluences should still cap at 20 points
        factors_10 = ConfidenceFactors(multiple_confluences=10)
        assert factors_10.calculate_score() == 20

    def test_total_score_capped_at_100(self):
        """Total score should never exceed 100."""
        # Maximum possible score
        factors = ConfidenceFactors(
            htf_trend_aligned=True,
            htf_structure_clean=True,
            pattern_clean=True,
            multiple_confluences=4,
            volume_spike=True,
            volume_divergence=True,
            trending_market=True,
            low_volatility=True,
        )
        # 15 + 15 + 10 + 20 + 10 + 10 + 10 + 10 = 100
        assert factors.calculate_score() == 100

    def test_all_factors_true_equals_100(self):
        """All factors enabled (with max confluences) should equal 100."""
        factors = ConfidenceFactors(
            htf_trend_aligned=True,
            htf_structure_clean=True,
            pattern_clean=True,
            multiple_confluences=4,
            volume_spike=True,
            volume_divergence=True,
            trending_market=True,
            low_volatility=True,
        )
        assert factors.calculate_score() == 100


class TestPositionSizing:
    """Tests for position sizing calculations."""

    def test_position_size_respects_max_percent(self):
        """Position size should not exceed max_position_percent."""
        params = RiskParameters(max_position_percent=0.05)  # 5% max
        size = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=100,  # Max confidence to try to exceed limit
            current_atr=2,
            baseline_atr=2,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        position_value = size * 100
        assert position_value <= 10000 * 0.05  # Should be ≤ $500

    def test_low_confidence_returns_zero(self):
        """Confidence below min_confidence should return zero position."""
        params = RiskParameters(min_confidence=50)
        size = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=30,  # Below minimum
            current_atr=2,
            baseline_atr=2,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size == 0.0

    def test_below_min_confidence_returns_zero(self):
        """Confidence exactly at min_confidence-1 should return zero."""
        params = RiskParameters(min_confidence=40)
        size = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=39,  # Just below minimum
            current_atr=2,
            baseline_atr=2,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size == 0.0

    def test_volatility_adjustment_scales_correctly(self):
        """Position size should scale inversely with volatility."""
        params = RiskParameters(max_position_percent=0.5)  # Large cap to avoid hitting it

        # Normal volatility
        size_normal = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,  # Normal = baseline
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )

        # High volatility (2x baseline) - should reduce size
        size_high_vol = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=10,  # 2x baseline
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )

        assert size_high_vol < size_normal

    def test_high_volatility_reduces_size(self):
        """High volatility should reduce position size."""
        params = RiskParameters(max_position_percent=0.5)  # Large cap to avoid hitting it

        # Baseline
        size_baseline = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )

        # 3x volatility (should be capped at 0.5x multiplier)
        size_high = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=15,  # 3x baseline
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )

        # High vol should be ~0.5x of baseline (capped)
        assert size_high < size_baseline
        assert size_high == pytest.approx(size_baseline * 0.5, rel=0.01)

    def test_low_volatility_increases_size(self):
        """Low volatility should increase size (capped at 1.5x)."""
        params = RiskParameters(max_position_percent=0.5)  # Large cap to avoid hitting it

        # Baseline
        size_baseline = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=10,
            baseline_atr=10,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )

        # Very low volatility (should be capped at 1.5x multiplier)
        size_low = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=2,  # 0.2x baseline
            baseline_atr=10,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )

        # Low vol should be ~1.5x of baseline (capped)
        assert size_low > size_baseline
        assert size_low == pytest.approx(size_baseline * 1.5, rel=0.01)

    def test_consecutive_wins_reduces_size(self):
        """Consecutive wins should reduce position size."""
        params = RiskParameters(
            consecutive_wins_reduce=3,
            win_reduction_factor=0.8,
            max_position_percent=0.5,  # Large cap to avoid hitting it
        )

        # No streak
        size_no_streak = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )

        # Win streak
        size_win_streak = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=3,  # Trigger reduction
            consecutive_losses=0,
            params=params,
        )

        assert size_win_streak < size_no_streak
        assert size_win_streak == pytest.approx(size_no_streak * 0.8, rel=0.01)

    def test_consecutive_losses_reduces_size(self):
        """Consecutive losses should reduce position size."""
        params = RiskParameters(
            consecutive_losses_reduce=2,
            loss_reduction_factor=0.7,
            max_position_percent=0.5,  # Large cap to avoid hitting it
        )

        # No streak
        size_no_streak = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )

        # Loss streak
        size_loss_streak = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=2,  # Trigger reduction
            params=params,
        )

        assert size_loss_streak < size_no_streak
        assert size_loss_streak == pytest.approx(size_no_streak * 0.7, rel=0.01)

    def test_zero_risk_per_unit_returns_zero(self):
        """Zero risk per unit (stop == entry) should return zero."""
        params = RiskParameters()
        size = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=100,  # Same as entry
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size == 0.0

    def test_stop_equals_entry_returns_zero(self):
        """Stop loss equal to entry should return zero."""
        params = RiskParameters()
        size = calculate_position_size(
            portfolio_value=10000,
            entry_price=50.0,
            stop_loss_price=50.0,
            confidence_score=80,
            current_atr=2,
            baseline_atr=2,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size == 0.0

    def test_negative_portfolio_value_returns_zero(self):
        """Negative portfolio value should return zero."""
        params = RiskParameters()
        size = calculate_position_size(
            portfolio_value=-1000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size == 0.0

    def test_negative_entry_price_returns_zero(self):
        """Negative entry price should return zero."""
        params = RiskParameters()
        size = calculate_position_size(
            portfolio_value=10000,
            entry_price=-100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size == 0.0

    def test_negative_stop_loss_returns_zero(self):
        """Negative stop loss price should return zero."""
        params = RiskParameters()
        size = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=-95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size == 0.0

    def test_invalid_confidence_returns_zero(self):
        """Invalid confidence scores should return zero."""
        params = RiskParameters()

        # Confidence > 100
        size_high = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=150,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size_high == 0.0

        # Confidence < 0
        size_low = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=-50,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size_low == 0.0

    def test_negative_atr_returns_zero(self):
        """Negative ATR values should return zero."""
        params = RiskParameters()

        # Negative current_atr
        size_curr = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=-5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size_curr == 0.0

        # Negative baseline_atr
        size_base = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=-5,
            consecutive_wins=0,
            consecutive_losses=0,
            params=params,
        )
        assert size_base == 0.0

    def test_negative_streaks_return_zero(self):
        """Negative win/loss streaks should return zero."""
        params = RiskParameters()

        # Negative consecutive wins
        size_wins = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=-3,
            consecutive_losses=0,
            params=params,
        )
        assert size_wins == 0.0

        # Negative consecutive losses
        size_losses = calculate_position_size(
            portfolio_value=10000,
            entry_price=100,
            stop_loss_price=95,
            confidence_score=80,
            current_atr=5,
            baseline_atr=5,
            consecutive_wins=0,
            consecutive_losses=-2,
            params=params,
        )
        assert size_losses == 0.0

    def test_position_value_calculation(self):
        """Position value should be size × price."""
        size = 10.5
        price = 100.0
        value = calculate_position_value(size, price)
        assert value == 1050.0

        # Test with different values
        value2 = calculate_position_value(2.5, 50.0)
        assert value2 == 125.0

    def test_risk_percent_calculation(self):
        """Risk percent should be calculated correctly."""
        # Position: 40 units @ $100, stop @ $98
        # Risk: 40 × ($100 - $98) = $80
        # Portfolio: $10000
        # Risk%: $80 / $10000 = 0.008 = 0.8%
        risk_pct = calculate_risk_percent(
            position_size=40, entry_price=100, stop_loss_price=98, portfolio_value=10000
        )
        assert risk_pct == pytest.approx(0.008, rel=0.001)

    def test_zero_portfolio_value_in_risk_percent(self):
        """Zero portfolio value should return 0% risk."""
        risk_pct = calculate_risk_percent(
            position_size=40, entry_price=100, stop_loss_price=98, portfolio_value=0
        )
        assert risk_pct == 0.0

        # Negative portfolio value
        risk_pct_neg = calculate_risk_percent(
            position_size=40, entry_price=100, stop_loss_price=98, portfolio_value=-1000
        )
        assert risk_pct_neg == 0.0
