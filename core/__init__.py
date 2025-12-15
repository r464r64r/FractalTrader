"""Core detection algorithms for Smart Money Concepts."""

from .market_structure import find_swing_points, determine_trend, detect_structure_breaks

__all__ = [
    "find_swing_points",
    "determine_trend",
    "detect_structure_breaks",
]

# Lazy imports for modules not yet implemented
try:
    from .liquidity import find_equal_levels, detect_liquidity_sweep
    __all__.extend(["find_equal_levels", "detect_liquidity_sweep"])
except ImportError:
    pass
