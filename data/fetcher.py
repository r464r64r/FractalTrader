"""Data fetching base interface."""

from abc import ABC, abstractmethod

import pandas as pd


class BaseFetcher(ABC):
    """
    Abstract base class for data fetchers.

    All fetchers must implement this interface to ensure
    strategies work with any data source.
    """

    @abstractmethod
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int | None = None,
        since: str | None = None,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data.

        Args:
            symbol: Trading pair (format depends on exchange)
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: Maximum number of candles to fetch
            since: Start date (ISO format: '2023-01-01' or timestamp)

        Returns:
            DataFrame with:
                - Index: DatetimeIndex (timezone-aware UTC)
                - Columns: ['open', 'high', 'low', 'close', 'volume']
                - All prices as float64
                - Volume as float64

        Raises:
            ValueError: Invalid symbol or timeframe
            ConnectionError: Network/API issues
        """
        pass

    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        """
        Validate DataFrame matches required format.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid

        Raises:
            ValueError: If format is incorrect
        """
        required_columns = ["open", "high", "low", "close", "volume"]

        if not all(col in df.columns for col in required_columns):
            missing = [c for c in required_columns if c not in df.columns]
            raise ValueError(f"Missing required columns: {missing}")

        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("Index must be DatetimeIndex")

        if df.empty:
            raise ValueError("DataFrame is empty")

        return True


# Keep the old function for backward compatibility
def fetch_ohlcv(
    symbol: str = "BTC/USDT", timeframe: str = "1h", limit: int = 1000, exchange_id: str = "binance"
) -> pd.DataFrame:
    """
    Legacy function for backward compatibility.

    Use CCXTFetcher class instead.
    """
    from data.ccxt_fetcher import CCXTFetcher

    fetcher = CCXTFetcher(exchange_id)
    return fetcher.fetch_ohlcv(symbol, timeframe, limit)
