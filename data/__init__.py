"""Data management utilities.

Provides both live trading (Hyperliquid) and backtesting (CCXT) data fetchers.
Both return standardized DataFrames compatible with trading strategies.
"""

from .ccxt_fetcher import CCXTFetcher
from .fetcher import BaseFetcher, fetch_ohlcv
from .hyperliquid_fetcher import HyperliquidFetcher

__all__ = [
    "BaseFetcher",
    "fetch_ohlcv",
    "HyperliquidFetcher",
    "CCXTFetcher",
]
