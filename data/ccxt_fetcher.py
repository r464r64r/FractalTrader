"""CCXT data fetcher for multi-exchange support."""

import logging
import time

import ccxt
import pandas as pd
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from data.fetcher import BaseFetcher

logger = logging.getLogger(__name__)


class CCXTFetcher(BaseFetcher):
    """
    Fetch data using CCXT library (multi-exchange support).

    Primary use: Deep backtesting with unlimited historical data.
    Recommended exchange: Binance (most liquid, longest history).

    Advantages:
    - Unlimited historical data (years)
    - Multiple exchanges supported
    - Well-tested library

    Disadvantages:
    - Slower than native SDKs
    - Requires pagination for large datasets
    """

    # CCXT-supported timeframes
    TIMEFRAME_MAP = {
        "1m": "1m",
        "5m": "5m",
        "15m": "15m",
        "1h": "1h",
        "4h": "4h",
        "1d": "1d",
    }

    def __init__(self, exchange_id: str = "binance", config: dict | None = None):
        """
        Initialize CCXT fetcher.

        Args:
            exchange_id: Exchange name ('binance', 'bybit', 'okx', etc.)
            config: Optional CCXT config (API keys, etc.)

        Raises:
            ValueError: If exchange not supported
        """
        self.exchange_id = exchange_id

        # Initialize exchange
        try:
            exchange_class = getattr(ccxt, exchange_id)
            self.exchange = exchange_class(config or {})
        except AttributeError:
            raise ValueError(f"Exchange '{exchange_id}' not supported by CCXT")

        logger.info(f"CCXTFetcher initialized ({exchange_id})")

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int | None = None,
        since: str | None = None,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from exchange.

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT', 'ETH/USDT')
            timeframe: Candle timeframe
            limit: Max candles (if None and 'since' provided, fetches all)
            since: Start date (ISO format or Unix timestamp)

        Returns:
            DataFrame with standard format

        Example:
            >>> fetcher = CCXTFetcher('binance')
            >>> df = fetcher.fetch_ohlcv('BTC/USDT', '1h', since='2023-01-01')
            >>> len(df)
            8760  # Full year of hourly data
        """
        # Validate timeframe
        if timeframe not in self.TIMEFRAME_MAP:
            raise ValueError(
                f"Invalid timeframe: {timeframe}. "
                f"Valid options: {list(self.TIMEFRAME_MAP.keys())}"
            )

        # Parse 'since' parameter
        since_ms = self._parse_since(since) if since else None

        # Fetch data (with pagination if needed)
        if since_ms and limit is None:
            # Fetch all data from 'since' to now (pagination required)
            all_candles = self._fetch_all_since(symbol, timeframe, since_ms)
        else:
            # Single request (with retry logic)
            all_candles = self._fetch_ohlcv_with_retry(
                symbol=symbol, timeframe=timeframe, since_ms=since_ms, limit=limit or 1000
            )

        if not all_candles:
            logger.warning(f"No data returned for {symbol} {timeframe}")
            return self._empty_dataframe()

        # Convert to DataFrame
        df = self._ohlcv_to_dataframe(all_candles)

        # Validate format
        self.validate_dataframe(df)

        logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
        return df

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ccxt.NetworkError, ccxt.RequestTimeout)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _fetch_ohlcv_with_retry(
        self, symbol: str, timeframe: str, since_ms: int | None, limit: int
    ) -> list:
        """
        Fetch OHLCV with automatic retry on network errors.

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            since_ms: Start timestamp (ms) or None
            limit: Number of candles

        Returns:
            List of OHLCV arrays

        Raises:
            ConnectionError: After 3 failed attempts
        """
        try:
            return self.exchange.fetch_ohlcv(symbol, timeframe, since=since_ms, limit=limit)
        except (ccxt.NetworkError, ccxt.RequestTimeout) as e:
            logger.warning(f"Network error: {e}")
            raise  # Let tenacity handle retry
        except Exception as e:
            logger.error(f"CCXT fetch error: {e}")
            raise ConnectionError(f"CCXT fetch error: {e}")

    def _fetch_all_since(
        self, symbol: str, timeframe: str, since_ms: int, batch_size: int = 1000
    ) -> list:
        """
        Fetch all candles from 'since' to now using pagination.

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            since_ms: Start timestamp (ms)
            batch_size: Candles per request

        Returns:
            List of OHLCV arrays
        """
        all_candles = []
        current_since = since_ms
        now_ms = int(time.time() * 1000)

        while current_since < now_ms:
            try:
                # Use retry logic for each batch
                batch = self._fetch_ohlcv_with_retry(
                    symbol=symbol, timeframe=timeframe, since_ms=current_since, limit=batch_size
                )
            except Exception as e:
                logger.error(f"Pagination error after retries: {e}")
                break

            if not batch:
                break

            all_candles.extend(batch)

            # Update since to last candle timestamp + 1ms
            current_since = batch[-1][0] + 1

            # Rate limit protection
            time.sleep(self.exchange.rateLimit / 1000)

            logger.debug(f"Fetched batch: {len(batch)} candles")

        logger.info(f"Pagination complete: {len(all_candles)} total candles")
        return all_candles

    def _parse_since(self, since: str) -> int:
        """Parse 'since' parameter to Unix timestamp (ms)."""
        try:
            # Try ISO date
            dt = pd.to_datetime(since)
            return int(dt.timestamp() * 1000)
        except:
            pass

        try:
            # Try Unix timestamp
            ts = int(since)
            if ts < 10000000000:  # Assume seconds
                ts *= 1000
            return ts
        except:
            raise ValueError(f"Invalid 'since' format: {since}")

    def _ohlcv_to_dataframe(self, ohlcv: list) -> pd.DataFrame:
        """
        Convert CCXT OHLCV to DataFrame.

        Args:
            ohlcv: List of [timestamp, open, high, low, close, volume]

        Returns:
            DataFrame with standard format
        """
        if not ohlcv:
            return self._empty_dataframe()

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])

        # Convert timestamp to datetime index
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)

        # Sort by time
        df.sort_index(inplace=True)

        # Remove duplicates (can happen with pagination)
        df = df[~df.index.duplicated(keep="first")]

        return df

    def _empty_dataframe(self) -> pd.DataFrame:
        """Return empty DataFrame with correct format."""
        df = pd.DataFrame(columns=["open", "high", "low", "close", "volume"])
        df.index = pd.DatetimeIndex([], name="timestamp")
        return df

    def get_available_symbols(self) -> list[str]:
        """
        Get list of available trading symbols.

        Returns:
            List of trading pairs (e.g., ['BTC/USDT', 'ETH/USDT'])
        """
        try:
            markets = self.exchange.load_markets()
            return list(markets.keys())
        except Exception as e:
            logger.error(f"Failed to fetch symbols: {e}")
            return []

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ccxt.NetworkError, ccxt.RequestTimeout)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol (with retry logic).

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Current price as float

        Raises:
            ConnectionError: After 3 failed attempts
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker["last"])
        except (ccxt.NetworkError, ccxt.RequestTimeout) as e:
            logger.warning(f"Network error fetching price: {e}")
            raise  # Let tenacity retry
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            raise ConnectionError(f"Price fetch error: {e}")
