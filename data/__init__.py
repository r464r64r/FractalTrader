"""Data management utilities.

Provides both live trading (Hyperliquid) and backtesting (CCXT) data fetchers.
Both return standardized DataFrames compatible with trading strategies.
"""

from .fetcher import BaseFetcher, fetch_ohlcv
from .hyperliquid_fetcher import HyperliquidFetcher
from .ccxt_fetcher import CCXTFetcher

__all__ = [
    'BaseFetcher',
    'fetch_ohlcv',
    'HyperliquidFetcher',
    'CCXTFetcher',
]
