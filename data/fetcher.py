"""Data fetching utilities using CCXT."""

import pandas as pd


def fetch_ohlcv(
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    limit: int = 1000,
    exchange_id: str = "binance"
) -> pd.DataFrame:
    """
    Fetch OHLCV data from exchange.

    Args:
        symbol: Trading pair (e.g., 'BTC/USDT')
        timeframe: Candle timeframe (e.g., '1h', '4h', '1d')
        limit: Number of candles to fetch
        exchange_id: Exchange to fetch from

    Returns:
        DataFrame with columns [open, high, low, close, volume] and DatetimeIndex
    """
    import ccxt

    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()

    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    df = pd.DataFrame(
        ohlcv,
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    return df
