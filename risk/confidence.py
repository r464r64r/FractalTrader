"""
Confidence scoring system for trading signals.

Confidence scores (0-100) determine position sizing - higher confidence = larger size.
This module provides a structured way to evaluate trade quality.
"""

from dataclasses import dataclass


@dataclass
class ConfidenceFactors:
    """
    Factors that determine entry confidence.

    The confidence score is calculated by summing points from various factors:
    - Timeframe alignment: 0-30 points
    - Pattern strength: 0-30 points
    - Volume confirmation: 0-20 points
    - Market regime: 0-20 points

    Total score is capped at 100.

    Example:
        >>> factors = ConfidenceFactors(
        ...     htf_trend_aligned=True,
        ...     pattern_clean=True,
        ...     volume_spike=True
        ... )
        >>> score = factors.calculate_score()
        >>> print(f"Confidence: {score}/100")
    """

    # Timeframe alignment (0-30 points)
    htf_trend_aligned: bool = False  # +15 if higher TF confirms direction
    htf_structure_clean: bool = False  # +15 if HTF structure is clear

    # Pattern strength (0-30 points)
    pattern_clean: bool = False  # +10 if pattern is textbook
    multiple_confluences: int = 0  # +5 per additional confluence (max 20)

    # Volume confirmation (0-20 points)
    volume_spike: bool = False  # +10 if volume confirms
    volume_divergence: bool = False  # +10 if volume divergence present

    # Market regime (0-20 points)
    trending_market: bool = False  # +10 if clear trend
    low_volatility: bool = False  # +10 if ATR is manageable

    def calculate_score(self) -> int:
        """
        Calculate total confidence score.

        Returns:
            Confidence score 0-100

        Example:
            >>> factors = ConfidenceFactors(
            ...     htf_trend_aligned=True,
            ...     htf_structure_clean=True,
            ...     pattern_clean=True,
            ...     multiple_confluences=3,
            ...     volume_spike=True,
            ...     trending_market=True,
            ...     low_volatility=True
            ... )
            >>> factors.calculate_score()
            100
        """
        score = 0

        # Timeframe alignment (0-30 points)
        if self.htf_trend_aligned:
            score += 15
        if self.htf_structure_clean:
            score += 15

        # Pattern strength (0-30 points)
        if self.pattern_clean:
            score += 10
        # Cap confluences at 4 (= 20 points)
        score += min(self.multiple_confluences * 5, 20)

        # Volume confirmation (0-20 points)
        if self.volume_spike:
            score += 10
        if self.volume_divergence:
            score += 10

        # Market regime (0-20 points)
        if self.trending_market:
            score += 10
        if self.low_volatility:
            score += 10

        return min(score, 100)


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_confidence_score_zero_by_default
# [ ] test_confidence_score_max_100
# [ ] test_htf_alignment_adds_30_points
# [ ] test_pattern_strength_adds_30_points
# [ ] test_volume_confirmation_adds_20_points
# [ ] test_market_regime_adds_20_points
# [ ] test_multiple_confluences_capped_at_20
# [ ] test_total_score_capped_at_100
# [ ] test_all_factors_true_equals_100
# =============================================================================
