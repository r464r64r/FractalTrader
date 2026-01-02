"""Live data streaming for real-time market analysis."""

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from threading import Event, Thread

import pandas as pd

from data.ccxt_fetcher import CCXTFetcher
from data.hyperliquid_fetcher import HyperliquidFetcher

logger = logging.getLogger(__name__)


class LiveDataStream:
    """
    Real-time market data streaming with automatic updates.

    Features:
    - Configurable update interval (default: 15 seconds)
    - Multi-timeframe support
    - Automatic error recovery
    - Callback system for new data
    - Thread-safe operation

    Example:
        >>> stream = LiveDataStream(
        ...     symbol='BTC',
        ...     timeframes=['15m', '1h', '4h'],
        ...     update_interval=15
        ... )
        >>> stream.on_update(lambda data: print(f"New data: {len(data['1h'])} candles"))
        >>> stream.start()
        >>> # ... dashboard runs ...
        >>> stream.stop()
    """

    def __init__(
        self,
        symbol: str,
        timeframes: list[str] = ["15m", "1h", "4h"],
        update_interval: int = 15,
        source: str = "hyperliquid",
        lookback: int = 500,
    ):
        """
        Initialize live data stream.

        Args:
            symbol: Trading symbol (e.g., 'BTC' for Hyperliquid, 'BTC/USDT' for CCXT)
            timeframes: List of timeframes to track
            update_interval: Update frequency in seconds (min: 5)
            source: Data source ('hyperliquid' or 'binance')
            lookback: Number of historical candles to maintain
        """
        self.symbol = symbol
        self.timeframes = timeframes
        self.update_interval = max(5, update_interval)  # Min 5 seconds
        self.lookback = lookback
        self.source = source

        # Initialize data fetcher
        if source == "hyperliquid":
            self.fetcher = HyperliquidFetcher(network="mainnet")
        elif source == "binance":
            self.fetcher = CCXTFetcher(exchange_id="binance")
        else:
            raise ValueError(f"Unknown source: {source}")

        # Data storage
        self.data: dict[str, pd.DataFrame] = {}
        self.last_update: dict[str, datetime] = {}

        # Threading
        self._thread: Thread | None = None
        self._stop_event = Event()
        self._callbacks: list[Callable] = []

        # Metrics
        self.update_count = 0
        self.error_count = 0
        self.start_time: datetime | None = None

        logger.info(
            f"LiveDataStream initialized: {symbol} on {source}, "
            f"timeframes={timeframes}, interval={update_interval}s"
        )

    def on_update(self, callback: Callable[[dict[str, pd.DataFrame]], None]):
        """
        Register callback for data updates.

        Args:
            callback: Function to call when new data arrives
                     Receives dict of {timeframe: DataFrame}
        """
        self._callbacks.append(callback)
        logger.debug(f"Registered callback: {callback.__name__}")

    def start(self):
        """Start live data streaming in background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Stream already running")
            return

        # Initial data fetch
        logger.info("Fetching initial data...")
        self._fetch_all_timeframes()

        # Start update thread
        self._stop_event.clear()
        self._thread = Thread(target=self._update_loop, daemon=True)
        self._thread.start()

        self.start_time = datetime.now(UTC)
        logger.info("Live stream started")

    def stop(self):
        """Stop live data streaming."""
        if not self._thread or not self._thread.is_alive():
            logger.warning("Stream not running")
            return

        logger.info("Stopping live stream...")
        self._stop_event.set()
        self._thread.join(timeout=5)

        logger.info(f"Stream stopped. Updates: {self.update_count}, " f"Errors: {self.error_count}")

    def get_data(self, timeframe: str | None = None) -> dict[str, pd.DataFrame]:
        """
        Get current data.

        Args:
            timeframe: Specific timeframe (or None for all)

        Returns:
            Dict of {timeframe: DataFrame} or single DataFrame
        """
        if timeframe:
            return self.data.get(timeframe)
        return self.data.copy()

    def get_latest_price(self) -> float | None:
        """Get most recent close price from fastest timeframe."""
        if not self.data:
            return None

        # Use fastest timeframe (first in list)
        fastest_tf = self.timeframes[0]
        df = self.data.get(fastest_tf)

        if df is None or df.empty:
            return None

        return float(df["close"].iloc[-1])

    def get_uptime(self) -> float | None:
        """Get stream uptime in seconds."""
        if not self.start_time:
            return None
        return (datetime.now(UTC) - self.start_time).total_seconds()

    def _update_loop(self):
        """Background thread: periodically fetch new data."""
        while not self._stop_event.is_set():
            try:
                # Fetch updates
                self._fetch_all_timeframes()

                # Notify callbacks
                self._notify_callbacks()

                self.update_count += 1

            except Exception as e:
                self.error_count += 1
                logger.error(f"Update error: {e}", exc_info=True)

            # Wait for next interval
            self._stop_event.wait(self.update_interval)

    def _fetch_all_timeframes(self):
        """Fetch data for all timeframes."""
        for tf in self.timeframes:
            try:
                df = self.fetcher.fetch_ohlcv(symbol=self.symbol, timeframe=tf, limit=self.lookback)

                self.data[tf] = df
                self.last_update[tf] = datetime.now(UTC)

                logger.debug(f"Updated {tf}: {len(df)} candles")

            except Exception as e:
                logger.error(f"Failed to fetch {tf}: {e}")
                # Keep old data if fetch fails

    def _notify_callbacks(self):
        """Call all registered callbacks with new data."""
        for callback in self._callbacks:
            try:
                callback(self.data)
            except Exception as e:
                logger.error(f"Callback error in {callback.__name__}: {e}")


class LiveIndicatorStream(LiveDataStream):
    """
    Extended stream that calculates indicators in real-time.

    Automatically computes order blocks, liquidity zones, etc.
    on each update.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Import detection modules (lazy import to avoid circular dependencies)
        try:
            from detection.liquidity import detect_liquidity_zones
            from detection.market_structure import detect_market_structure
            from detection.order_blocks import detect_order_blocks

            self.detect_order_blocks = detect_order_blocks
            self.detect_liquidity_zones = detect_liquidity_zones
            self.detect_market_structure = detect_market_structure
        except ImportError:
            logger.warning("Detection modules not available - indicators disabled")
            self.detect_order_blocks = None
            self.detect_liquidity_zones = None
            self.detect_market_structure = None

        # Indicator storage
        self.order_blocks: dict[str, pd.DataFrame] = {}
        self.liquidity_zones: dict[str, pd.DataFrame] = {}
        self.market_structure: dict[str, dict] = {}

    def _fetch_all_timeframes(self):
        """Fetch data and compute indicators."""
        super()._fetch_all_timeframes()

        # Skip indicators if detection modules not available
        if self.detect_order_blocks is None:
            return

        # Compute indicators for each timeframe
        for tf in self.timeframes:
            if tf not in self.data or self.data[tf].empty:
                continue

            try:
                df = self.data[tf]

                # Detect order blocks
                ob_df = self.detect_order_blocks(df)
                self.order_blocks[tf] = ob_df

                # Detect liquidity zones
                liq_df = self.detect_liquidity_zones(df)
                self.liquidity_zones[tf] = liq_df

                # Detect market structure
                structure = self.detect_market_structure(df)
                self.market_structure[tf] = structure

                logger.debug(
                    f"Indicators updated for {tf}: "
                    f"{len(ob_df)} OBs, {len(liq_df)} liquidity zones"
                )

            except Exception as e:
                logger.error(f"Indicator calculation error for {tf}: {e}")

    def get_indicators(self, timeframe: str) -> dict:
        """
        Get all indicators for a timeframe.

        Args:
            timeframe: Timeframe to get indicators for

        Returns:
            Dict with 'order_blocks', 'liquidity_zones', 'market_structure'
        """
        return {
            "order_blocks": self.order_blocks.get(timeframe),
            "liquidity_zones": self.liquidity_zones.get(timeframe),
            "market_structure": self.market_structure.get(timeframe, {}),
        }
