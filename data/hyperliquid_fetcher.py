"""Hyperliquid data fetcher using native SDK."""

import pandas as pd
from typing import Optional, Literal
from datetime import datetime, timezone
import time
import logging

from hyperliquid.info import Info
from hyperliquid.utils import constants

from data.fetcher import BaseFetcher


logger = logging.getLogger(__name__)


class HyperliquidFetcher(BaseFetcher):
    """
    Fetch data from Hyperliquid DEX using native SDK.

    Hyperliquid provides:
    - Last 5000 candles per request (FREE)
    - Real-time WebSocket data
    - Low latency (<200ms)

    Limitations:
    - Historical data limited to 5000 candles
    - Use CCXT/Binance for deep backtesting (>5000 candles)
    """

    MAINNET_URL = constants.MAINNET_API_URL
    TESTNET_URL = constants.TESTNET_API_URL

    # Hyperliquid timeframe mapping
    TIMEFRAME_MAP = {
        '1m': '1m',
        '5m': '5m',
        '15m': '15m',
        '1h': '1h',
        '4h': '4h',
        '1d': '1d',
    }

    MAX_CANDLES = 5000  # Hyperliquid API limit

    def __init__(
        self,
        network: Literal['mainnet', 'testnet'] = 'mainnet',
        timeout: int = 30
    ):
        """
        Initialize Hyperliquid fetcher.

        Args:
            network: 'mainnet' or 'testnet'
            timeout: Request timeout in seconds
        """
        self.network = network
        api_url = self.MAINNET_URL if network == 'mainnet' else self.TESTNET_URL

        self.info = Info(api_url, skip_ws=True)  # No WebSocket for now
        self.timeout = timeout

        logger.info(f"HyperliquidFetcher initialized ({network})")

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: Optional[int] = None,
        since: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from Hyperliquid.

        Args:
            symbol: Coin name (e.g., 'BTC', 'ETH') - no /USDT suffix
            timeframe: Candle timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: Number of candles (max 5000, default 1000)
            since: Start timestamp (ISO format or Unix timestamp)

        Returns:
            DataFrame with standard format

        Raises:
            ValueError: Invalid symbol or timeframe
            ConnectionError: API request failed

        Example:
            >>> fetcher = HyperliquidFetcher()
            >>> df = fetcher.fetch_ohlcv('BTC', '1h', limit=100)
            >>> df.head()
                                open    high     low   close    volume
            2024-12-01 00:00:00  42000  42100  41900  42050  1234.56
        """
        # Validate inputs
        if timeframe not in self.TIMEFRAME_MAP:
            raise ValueError(
                f"Invalid timeframe: {timeframe}. "
                f"Valid options: {list(self.TIMEFRAME_MAP.keys())}"
            )

        if limit is None:
            limit = 1000  # Default
        elif limit > self.MAX_CANDLES:
            logger.warning(f"Limit {limit} exceeds max {self.MAX_CANDLES}, capping")
            limit = self.MAX_CANDLES

        # Convert timeframe
        hl_timeframe = self.TIMEFRAME_MAP[timeframe]

        # Calculate time range
        end_time = int(time.time() * 1000)  # Current time in ms

        if since is not None:
            start_time = self._parse_since(since)
        else:
            # Calculate start time based on limit and timeframe
            start_time = self._calculate_start_time(end_time, timeframe, limit)

        # Fetch data from Hyperliquid
        try:
            candles = self.info.candles_snapshot(
                name=symbol,
                interval=hl_timeframe,
                startTime=start_time,
                endTime=end_time
            )
        except Exception as e:
            raise ConnectionError(f"Hyperliquid API error: {e}")

        if not candles:
            logger.warning(f"No data returned for {symbol} {timeframe}")
            return self._empty_dataframe()

        # Convert to DataFrame
        df = self._candles_to_dataframe(candles)

        # Apply limit
        if limit and len(df) > limit:
            df = df.tail(limit)

        # Validate format
        self.validate_dataframe(df)

        logger.info(f"Fetched {len(df)} candles for {symbol} {timeframe}")
        return df

    def _parse_since(self, since: str) -> int:
        """
        Parse 'since' parameter to Unix timestamp (ms).

        Args:
            since: ISO date string or Unix timestamp

        Returns:
            Unix timestamp in milliseconds
        """
        # Try parsing as ISO date
        try:
            dt = pd.to_datetime(since)
            return int(dt.timestamp() * 1000)
        except:
            pass

        # Try as Unix timestamp (seconds)
        try:
            ts = int(since)
            # If less than year 2000, assume it's in seconds
            if ts < 946684800:
                raise ValueError("Timestamp too old")
            # If less than typical ms timestamp, convert to ms
            if ts < 10000000000:
                ts *= 1000
            return ts
        except:
            raise ValueError(f"Invalid 'since' format: {since}")

    def _calculate_start_time(self, end_time: int, timeframe: str, limit: int) -> int:
        """
        Calculate start time based on end time, timeframe, and limit.

        Args:
            end_time: End timestamp (ms)
            timeframe: Candle timeframe
            limit: Number of candles

        Returns:
            Start timestamp (ms)
        """
        # Timeframe to milliseconds
        tf_to_ms = {
            '1m': 60 * 1000,
            '5m': 5 * 60 * 1000,
            '15m': 15 * 60 * 1000,
            '1h': 60 * 60 * 1000,
            '4h': 4 * 60 * 60 * 1000,
            '1d': 24 * 60 * 60 * 1000,
        }

        interval_ms = tf_to_ms[timeframe]
        start_time = end_time - (limit * interval_ms)

        return start_time

    def _candles_to_dataframe(self, candles: list) -> pd.DataFrame:
        """
        Convert Hyperliquid candles to standard DataFrame format.

        Args:
            candles: List of candle dicts from Hyperliquid API

        Returns:
            DataFrame with standard format
        """
        if not candles:
            return self._empty_dataframe()

        # Hyperliquid candle format:
        # [
        #   {
        #     't': 1638316800000,  # timestamp (ms)
        #     'T': 1638320399999,  # close time
        #     'o': '57000.0',      # open
        #     'h': '57100.0',      # high
        #     'l': '56900.0',      # low
        #     'c': '57050.0',      # close
        #     'v': '123.45',       # volume
        #     'n': 1234            # number of trades
        #   },
        #   ...
        # ]

        data = []
        for candle in candles:
            data.append({
                'timestamp': candle['t'],
                'open': float(candle['o']),
                'high': float(candle['h']),
                'low': float(candle['l']),
                'close': float(candle['c']),
                'volume': float(candle['v']),
            })

        df = pd.DataFrame(data)

        # Convert timestamp to datetime index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df.set_index('timestamp', inplace=True)

        # Sort by time
        df.sort_index(inplace=True)

        return df

    def _empty_dataframe(self) -> pd.DataFrame:
        """Return empty DataFrame with correct format."""
        df = pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume'])
        df.index = pd.DatetimeIndex([], name='timestamp')
        return df

    def get_available_symbols(self) -> list[str]:
        """
        Get list of available trading symbols on Hyperliquid.

        Returns:
            List of coin names (e.g., ['BTC', 'ETH', 'SOL'])
        """
        try:
            meta = self.info.meta()
            universe = meta.get('universe', [])
            return [coin['name'] for coin in universe]
        except Exception as e:
            logger.error(f"Failed to fetch symbols: {e}")
            return []

    def get_current_price(self, symbol: str) -> float:
        """
        Get current price for a symbol.

        Args:
            symbol: Coin name (e.g., 'BTC')

        Returns:
            Current price as float
        """
        try:
            all_mids = self.info.all_mids()
            return float(all_mids.get(symbol, 0))
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            return 0.0
