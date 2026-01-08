"""Hyperliquid testnet paper trading."""

import logging
import time
from datetime import datetime

from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants
from ratelimit import limits, sleep_and_retry

from data.hyperliquid_fetcher import HyperliquidFetcher
from live.hl_integration.config import HyperliquidConfig
from live.state_manager import StateManager
from risk.position_sizing import RiskParameters, calculate_position_size
from strategies.base import BaseStrategy, Signal

logger = logging.getLogger(__name__)


class TransientError(Exception):
    """
    Transient error that should be retried.

    Examples: network timeout, temporary API unavailability, rate limit hit
    """

    pass


class CriticalError(Exception):
    """
    Critical error that should stop trading.

    Examples: invalid credentials, account locked, insufficient funds
    """

    pass


class HyperliquidTestnetTrader:
    """
    Paper trading on Hyperliquid testnet.

    Features:
    - Uses fake money (zero risk)
    - Real market data
    - Full order placement testing
    - Performance tracking

    Testnet URL: https://app.hyperliquid-testnet.xyz
    """

    def __init__(
        self,
        config: HyperliquidConfig,
        strategy: BaseStrategy,
        state_file: str = ".testnet_state.json",
    ):
        """
        Initialize testnet trader.

        Args:
            config: HyperliquidConfig with network='testnet'
            strategy: Strategy instance to trade
            state_file: Path to state file for persistence

        Raises:
            ValueError: If config.network != 'testnet'
        """
        if config.network != "testnet":
            raise ValueError("TestnetTrader requires network='testnet'")

        config.validate()

        self.config = config
        self.strategy = strategy

        # Setup wallet
        self.wallet = Account.from_key(config.private_key)
        logger.info(f"Wallet address: {self.wallet.address}")

        # Initialize Hyperliquid clients
        self.info = Info(constants.TESTNET_API_URL, skip_ws=True)
        self.exchange = Exchange(self.wallet, constants.TESTNET_API_URL)

        # Initialize data fetcher
        self.fetcher = HyperliquidFetcher(network="testnet")

        # Risk parameters
        self.risk_params = RiskParameters(
            base_risk_percent=config.base_risk_percent,
            max_position_percent=config.max_position_percent,
            min_confidence=config.min_confidence,
        )

        # Initialize state manager (with persistence)
        self.state_manager = StateManager(state_file=state_file, auto_save=True, backup_count=5)

        # Load state from previous session (if exists)
        self.open_positions: dict = self.state_manager.load_positions()
        self.trade_history: list[dict] = self.state_manager.load_trade_history()
        self.is_running = False

        # Set starting balance if not set
        if self.state_manager.get_starting_balance() == 0:
            portfolio_value = self._get_portfolio_value()

            # If testnet account is unfunded, use simulated balance
            if portfolio_value == 0:
                portfolio_value = 10000.0  # $10k simulated balance for paper trading
                self.simulation_mode = True
                logger.warning(
                    "Testnet account has $0 balance. Using simulated balance: $10,000"
                )
                logger.warning(
                    "To fund testnet account, visit: https://app.hyperliquid-testnet.xyz/drip"
                )
                logger.info("Running in SIMULATION MODE - tracking positions in memory only")
            else:
                self.simulation_mode = False

            self.state_manager.set_starting_balance(portfolio_value)
            self.starting_balance = portfolio_value
            logger.info(f"Set starting balance: ${portfolio_value:,.2f}")
        else:
            self.starting_balance = self.state_manager.get_starting_balance()
            # Check if we're still in simulation mode
            actual_balance = self._get_actual_portfolio_value()
            self.simulation_mode = actual_balance == 0
            logger.info(f"Resumed session with starting balance: " f"${self.starting_balance:,.2f}")

        # Circuit breakers (testnet-specific safeguards)
        self.max_daily_drawdown = 0.20  # Stop if down 20% (more lenient than mainnet)
        self.max_daily_trades = 50  # Limit number of trades per day
        self.circuit_breaker_triggered = False
        self._circuit_breaker_date = datetime.now().date()  # Track daily reset

        # Sync positions with exchange on startup (critical for recovery)
        self._sync_positions_with_exchange()

        logger.info("TestnetTrader initialized")
        logger.info(
            f"Circuit breakers: max_drawdown={self.max_daily_drawdown:.1%}, max_trades={self.max_daily_trades}"
        )
        if self.open_positions:
            logger.info(f"Loaded {len(self.open_positions)} open positions from previous session")
        if self.trade_history:
            logger.info(f"Loaded {len(self.trade_history)} trades from history")

    def run(self, duration_seconds: int | None = None):
        """
        Run trading loop.

        Args:
            duration_seconds: How long to run (None = indefinite)

        Example:
            >>> trader = TestnetTrader(config, strategy)
            >>> trader.run(duration_seconds=3600)  # Run for 1 hour
        """
        self.is_running = True
        start_time = time.time()

        logger.info("Starting testnet trading loop")
        logger.info(f"Strategy: {self.strategy.name}")
        logger.info(f"Symbol: {self.config.default_symbol}")
        logger.info(f"Timeframe: {self.config.default_timeframe}")

        try:
            while self.is_running:
                # Check if duration exceeded
                if duration_seconds:
                    elapsed = time.time() - start_time
                    if elapsed > duration_seconds:
                        logger.info("Duration exceeded, stopping")
                        break

                # Main trading loop
                self._trading_iteration()

                # Sleep until next check
                time.sleep(self.config.check_interval_seconds)

        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        except Exception as e:
            logger.error(f"Trading loop error: {e}", exc_info=True)
        finally:
            self.stop()

    def _trading_iteration(self):
        """Single iteration of trading loop with circuit breakers."""
        try:
            # Check circuit breakers first
            if not self._check_circuit_breakers():
                return

            # 0. Monitor and manage existing positions (SL/TP)
            self._monitor_positions()

            # 1. Fetch latest data
            data = self.fetcher.fetch_ohlcv(
                self.config.default_symbol,
                self.config.default_timeframe,
                limit=500,  # Enough for strategy calculations
            )

            # 2. Generate signals
            signals = self.strategy.generate_signals(data)

            if not signals:
                logger.debug("No signals generated")
                return

            # 3. Process latest signal
            latest_signal = signals[-1]

            # Check minimum confidence
            if latest_signal.confidence < self.config.min_confidence:
                logger.info(
                    f"Signal confidence {latest_signal.confidence} < "
                    f"min_confidence {self.config.min_confidence}, skipping"
                )
                return

            logger.info(f"Signal: {latest_signal.direction} @ " f"{latest_signal.entry_price:.2f}")

            # 4. Check if we can open position
            # First check if position already exists for this symbol
            symbol = self.config.default_symbol
            if symbol in self.open_positions:
                logger.warning(f"Position already exists for {symbol}, skipping signal")
                return

            if len(self.open_positions) >= self.config.max_open_positions:
                logger.warning("Max positions reached, skipping signal")
                return

            # 5. Calculate position size
            portfolio_value = self._get_portfolio_value()
            position_size = calculate_position_size(
                portfolio_value=portfolio_value,
                entry_price=latest_signal.entry_price,
                stop_loss_price=latest_signal.stop_loss,
                confidence_score=latest_signal.confidence,
                current_atr=self._calculate_atr(data),
                baseline_atr=self._calculate_baseline_atr(data),
                consecutive_wins=self._count_consecutive_wins(),
                consecutive_losses=self._count_consecutive_losses(),
                params=self.risk_params,
            )

            if position_size == 0:
                logger.info("Position size = 0 (confidence too low or risk limits)")
                return

            # 6. Place order
            self._place_order(latest_signal, position_size)

        except TransientError as e:
            # Transient errors: network issues, API timeouts
            logger.warning(f"Transient error, will retry on next iteration: {e}")
            time.sleep(5)  # Brief pause before continuing

        except CriticalError as e:
            # Critical errors: stop trading immediately
            logger.critical(f"🛑 CRITICAL ERROR - Stopping trading: {e}")
            self.circuit_breaker_triggered = True
            self.stop()

        except Exception as e:
            # Unknown errors: log and categorize conservatively
            error_msg = str(e).lower()

            # Check if it's likely a transient error
            transient_keywords = ["timeout", "connection", "network", "temporary", "rate limit"]
            if any(keyword in error_msg for keyword in transient_keywords):
                logger.warning(f"Likely transient error (retrying): {e}")
                time.sleep(5)
            else:
                # Unknown error - log extensively but continue cautiously
                logger.error(f"Iteration error (unknown type): {e}", exc_info=True)
                time.sleep(10)  # Longer pause for unknown errors

    def _monitor_positions(self):
        """
        Monitor open positions and close them if SL/TP is hit.

        This is critical for risk management - positions must be closed
        when stop loss or take profit levels are reached.
        """
        if not self.open_positions:
            return

        for symbol, position in list(self.open_positions.items()):
            try:
                # Get current price
                current_price = self.fetcher.get_current_price(symbol)
                if current_price <= 0:
                    logger.warning(f"Could not get price for {symbol}, skipping position check")
                    continue

                entry_price = position.get("entry_price", 0)
                stop_loss = position.get("stop_loss")
                take_profit = position.get("take_profit")
                size = position.get("size", 0)

                # Determine position direction (from signal or entry data)
                signal = position.get("signal")
                if signal and hasattr(signal, "direction"):
                    is_long = signal.direction == 1
                else:
                    # Fallback: assume long if no signal data
                    is_long = True

                # Check stop loss
                if stop_loss:
                    sl_hit = (is_long and current_price <= stop_loss) or \
                             (not is_long and current_price >= stop_loss)
                    if sl_hit:
                        logger.warning(
                            f"🛑 STOP LOSS HIT for {symbol}! "
                            f"Price: ${current_price:,.2f}, SL: ${stop_loss:,.2f}"
                        )
                        self._close_position(symbol, current_price, "STOP_LOSS")
                        continue

                # Check take profit
                if take_profit:
                    tp_hit = (is_long and current_price >= take_profit) or \
                             (not is_long and current_price <= take_profit)
                    if tp_hit:
                        logger.info(
                            f"🎯 TAKE PROFIT HIT for {symbol}! "
                            f"Price: ${current_price:,.2f}, TP: ${take_profit:,.2f}"
                        )
                        self._close_position(symbol, current_price, "TAKE_PROFIT")
                        continue

                # Update unrealized P&L for simulation mode
                if hasattr(self, "simulation_mode") and self.simulation_mode:
                    if is_long:
                        unrealized_pnl = (current_price - entry_price) * size
                    else:
                        unrealized_pnl = (entry_price - current_price) * size
                    position["unrealized_pnl"] = unrealized_pnl

            except Exception as e:
                logger.error(f"Error monitoring position {symbol}: {e}")

    def _close_position(self, symbol: str, exit_price: float, reason: str):
        """
        Close a position and record the trade.

        Args:
            symbol: Symbol to close
            exit_price: Price at which position is closed
            reason: Why position was closed (STOP_LOSS, TAKE_PROFIT, MANUAL)
        """
        if symbol not in self.open_positions:
            logger.warning(f"Cannot close position {symbol}: not found")
            return

        position = self.open_positions[symbol]
        entry_price = position.get("entry_price", 0)
        size = position.get("size", 0)

        # Determine direction
        signal = position.get("signal")
        if signal and hasattr(signal, "direction"):
            is_long = signal.direction == 1
        else:
            is_long = True

        # Calculate P&L
        if is_long:
            pnl = (exit_price - entry_price) * size
        else:
            pnl = (entry_price - exit_price) * size

        logger.info(
            f"📊 Closing {symbol}: "
            f"{'LONG' if is_long else 'SHORT'} "
            f"Entry: ${entry_price:,.2f}, Exit: ${exit_price:,.2f}, "
            f"P&L: ${pnl:+,.2f} ({reason})"
        )

        # Place close order (unless in simulation mode)
        if not (hasattr(self, "simulation_mode") and self.simulation_mode):
            try:
                # For long positions, we sell; for short, we buy
                close_order = self.exchange.order(
                    symbol,
                    not is_long,  # Opposite direction to close
                    size,
                    self._round_to_tick_size(symbol, exit_price),
                    {"limit": {"tif": "Gtc"}}
                )
                logger.info(f"Close order placed: {close_order}")
            except Exception as e:
                logger.error(f"Failed to place close order for {symbol}: {e}")

        # Update trade in history
        for trade in reversed(self.trade_history):
            if trade.get("symbol") == symbol and trade.get("status") == "OPEN":
                trade["exit_price"] = exit_price
                trade["pnl"] = pnl
                trade["status"] = "CLOSED"
                trade["close_reason"] = reason
                trade["close_timestamp"] = datetime.now()
                break

        # Remove from open positions
        del self.open_positions[symbol]
        self.state_manager.remove_position(symbol)

        # Save updated state
        self.state_manager.force_save()

        logger.info(f"✅ Position {symbol} closed successfully")

    def _check_circuit_breakers(self) -> bool:
        """
        Check if circuit breakers should trigger.

        Returns:
            True if trading can continue, False if breakers triggered
        """
        # Reset circuit breakers at midnight (new trading day)
        today = datetime.now().date()
        if today != self._circuit_breaker_date:
            logger.info(f"📅 New trading day ({today}): Resetting circuit breakers")
            self._circuit_breaker_date = today
            self.circuit_breaker_triggered = False
            # Note: We don't reset starting_balance - that's session-based

        # Skip if already triggered today
        if self.circuit_breaker_triggered:
            return False

        # 1. Check drawdown limit
        current_balance = self._get_portfolio_value()

        # Prevent division by zero
        if self.starting_balance > 0:
            drawdown = (self.starting_balance - current_balance) / self.starting_balance
        else:
            drawdown = 0.0

        if drawdown > self.max_daily_drawdown:
            logger.critical(
                f"🛑 CIRCUIT BREAKER TRIGGERED! Drawdown {drawdown:.2%} > "
                f"{self.max_daily_drawdown:.2%}"
            )
            logger.critical(
                f"Starting balance: ${self.starting_balance:,.2f}, "
                f"Current balance: ${current_balance:,.2f}"
            )
            self.circuit_breaker_triggered = True
            self.stop()
            return False

        # 2. Check trade count limit (TODAY only, not all history)
        today_trades = self._count_today_trades()
        if today_trades > self.max_daily_trades:
            logger.critical(
                f"🛑 CIRCUIT BREAKER TRIGGERED! Today's trade count {today_trades} > "
                f"{self.max_daily_trades}"
            )
            self.circuit_breaker_triggered = True
            self.stop()
            return False

        return True

    def _count_today_trades(self) -> int:
        """Count trades executed today only."""
        today = datetime.now().date()
        count = 0
        for trade in self.trade_history:
            trade_time = trade.get("timestamp")
            if trade_time:
                # Handle both datetime and string timestamps
                if isinstance(trade_time, str):
                    try:
                        trade_date = datetime.fromisoformat(trade_time).date()
                    except ValueError:
                        continue
                elif hasattr(trade_time, 'date'):
                    trade_date = trade_time.date()
                else:
                    continue

                if trade_date == today:
                    count += 1
        return count

    def _round_to_tick_size(self, symbol: str, price: float) -> float:
        """
        Round price to appropriate tick size for the asset.

        Different assets have different price precision requirements on Hyperliquid.

        Args:
            symbol: Asset symbol (e.g., 'BTC', 'ETH', 'SOL')
            price: Raw price to round

        Returns:
            Price rounded to valid tick size
        """
        # Tick sizes based on Hyperliquid requirements (as of 2026-01)
        # See: https://hyperliquid.gitbook.io/hyperliquid-docs
        tick_sizes = {
            "BTC": 1,        # BTC: integer prices only
            "ETH": 0.1,      # ETH: 0.1 precision
            "SOL": 0.01,     # SOL: 0.01 precision
            "AVAX": 0.01,
            "DOGE": 0.00001,
            "XRP": 0.0001,
            "MATIC": 0.0001,
            "LINK": 0.01,
            "ARB": 0.0001,
            "OP": 0.001,
        }

        tick_size = tick_sizes.get(symbol, 0.01)  # Default to 0.01

        if tick_size >= 1:
            return round(price)
        else:
            # Round to tick size precision
            precision = len(str(tick_size).split('.')[-1])
            return round(price, precision)

    @sleep_and_retry
    @limits(calls=5, period=1)  # Max 5 order placements per second
    def _place_order(self, signal: Signal, size: float):
        """
        Place order on Hyperliquid.

        Args:
            signal: Trading signal
            size: Position size in base currency
        """
        try:
            symbol = self.config.default_symbol
            is_buy = signal.direction == 1

            # Get current market price for limit order
            current_price = self.fetcher.get_current_price(symbol)
            if current_price <= 0:
                logger.error(f"Invalid price for {symbol}")
                return

            # Calculate limit price (slightly better than market)
            offset = self.config.limit_price_offset_percent
            if is_buy:
                limit_price = current_price * (1 - offset)  # Buy lower
            else:
                limit_price = current_price * (1 + offset)  # Sell higher

            # Round price to appropriate precision based on asset
            limit_price = self._round_to_tick_size(symbol, limit_price)

            # Round size to avoid float_to_wire rounding errors
            # Hyperliquid typically accepts up to 5 decimal places for size
            size = round(size, 5)

            logger.info(
                f"Placing order: {symbol} {'BUY' if is_buy else 'SELL'} "
                f"{size:.4f} @ {limit_price:.2f}"
            )

            # Place order
            order = self.exchange.order(
                symbol, is_buy, size, limit_price, {"limit": {"tif": "Gtc"}}  # Good-til-canceled
            )

            logger.info(f"Order placed: {order}")

            # Only track position and record trade if order was successful
            if order.get('status') == 'ok':
                # Track position
                position_data = {
                    "signal": signal,
                    "size": size,
                    "entry_price": limit_price,
                    "stop_loss": signal.stop_loss,
                    "take_profit": signal.take_profit,
                    "timestamp": datetime.now(),
                    "order": order,
                }
                self.open_positions[symbol] = position_data

                # Save position to state manager (persists to disk)
                self.state_manager.save_position(symbol, position_data)

                # Record trade
                trade_data = {
                    "timestamp": datetime.now(),
                    "symbol": symbol,
                    "direction": "LONG" if is_buy else "SHORT",
                    "size": size,
                    "entry_price": limit_price,
                    "stop_loss": signal.stop_loss,
                    "confidence": signal.confidence,
                    "status": "OPEN",
                }
                self.trade_history.append(trade_data)

                # Save trade to state manager (persists to disk)
                self.state_manager.save_trade(trade_data)
            else:
                logger.debug(f"Order failed, not tracking position: {order.get('response', 'Unknown error')}")

        except Exception as e:
            error_msg = str(e).lower()

            # Categorize the error
            critical_keywords = ["invalid", "unauthorized", "forbidden", "insufficient", "locked"]
            transient_keywords = [
                "timeout",
                "connection",
                "network",
                "temporary",
                "rate limit",
                "unavailable",
            ]

            if any(keyword in error_msg for keyword in critical_keywords):
                raise CriticalError(f"Order placement failed (critical): {e}")
            elif any(keyword in error_msg for keyword in transient_keywords):
                raise TransientError(f"Order placement failed (transient): {e}")
            else:
                # Unknown error - log but don't stop trading
                logger.error(f"Order placement failed (unknown): {e}", exc_info=True)

    @sleep_and_retry
    @limits(calls=10, period=1)  # Max 10 portfolio value checks per second
    def _get_actual_portfolio_value(self) -> float:
        """
        Get current portfolio value from Hyperliquid account.

        Returns:
            Portfolio value in USD
        """
        try:
            # Get account state from Hyperliquid
            user_state = self.info.user_state(self.wallet.address)

            # Extract account value
            # Testnet starts with 100,000 USDT
            margin_summary = user_state.get("marginSummary", {})
            account_value = float(margin_summary.get("accountValue", 100000))

            return account_value

        except Exception as e:
            error_msg = str(e).lower()

            # Categorize the error
            transient_keywords = ["timeout", "connection", "network", "temporary", "unavailable"]

            if any(keyword in error_msg for keyword in transient_keywords):
                # Transient error - use cached value or default
                logger.warning(f"Transient error fetching portfolio value: {e}")
                return 100000  # Default testnet starting balance
            else:
                # Unknown error - log and use default
                logger.error(f"Failed to get portfolio value: {e}")
                return 100000  # Default testnet starting balance

    def _get_simulated_portfolio_value(self) -> float:
        """
        Calculate simulated portfolio value from tracked positions and cash.

        Returns:
            Simulated portfolio value in USD
        """
        # Start with the starting balance
        value = self.starting_balance

        # Add/subtract P&L from open positions
        for position in self.open_positions.values():
            # Each position tracks unrealized P&L
            value += position.get("unrealized_pnl", 0.0)

        # Add realized P&L from closed trades
        for trade in self.trade_history:
            if trade.get("status") == "closed":
                value += trade.get("pnl", 0.0)

        return max(0.0, value)

    def _get_portfolio_value(self) -> float:
        """
        Get current portfolio value.
        Returns simulated value if in simulation mode, actual value otherwise.

        Returns:
            Portfolio value in USD
        """
        if hasattr(self, "simulation_mode") and self.simulation_mode:
            return self._get_simulated_portfolio_value()
        else:
            return self._get_actual_portfolio_value()

    def _calculate_atr(self, data) -> float:
        """Calculate current ATR (Average True Range)."""
        # Use the strategy instance we already have
        atr = self.strategy._calculate_atr(data, period=14)
        if atr.empty:
            return 0.0
        return float(atr.iloc[-1])

    def _calculate_baseline_atr(self, data) -> float:
        """Calculate baseline ATR (50-period average)."""
        return self._calculate_atr(data)  # Simplified for now

    def _count_consecutive_wins(self) -> int:
        """Count consecutive winning trades."""
        count = 0
        for trade in reversed(self.trade_history):
            if trade.get("pnl", 0) > 0:
                count += 1
            else:
                break
        return count

    def _count_consecutive_losses(self) -> int:
        """Count consecutive losing trades."""
        count = 0
        for trade in reversed(self.trade_history):
            if trade.get("pnl", 0) < 0:
                count += 1
            else:
                break
        return count

    def stop(self):
        """Stop trading loop."""
        self.is_running = False
        logger.info("Testnet trader stopped")

        # Force save state before stopping
        self.state_manager.force_save()
        logger.info("State saved to disk")

        # Print summary
        self._print_summary()

    def _print_summary(self):
        """Print trading session summary."""
        logger.info("=" * 50)
        logger.info("TRADING SESSION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total trades: {len(self.trade_history)}")
        logger.info(f"Open positions: {len(self.open_positions)}")
        logger.info(f"Final portfolio value: ${self._get_portfolio_value():,.2f}")
        logger.info("=" * 50)

    def _sync_positions_with_exchange(self):
        """
        Synchronize local state with exchange positions on startup.

        Critical for recovery after crashes, restarts, or state file corruption.
        Exchange is source of truth - local state must match reality.

        This prevents the bug where bot restarts with clean state but exchange
        has open positions, leading to unintended position accumulation.
        """
        try:
            # Skip sync in simulation mode (no real positions on exchange)
            if self.simulation_mode:
                logger.info("Simulation mode - skipping exchange position sync")
                return

            logger.info("Syncing positions with exchange...")

            # Get current positions from exchange
            user_state = self.info.user_state(self.wallet.address)
            exchange_positions = user_state.get('assetPositions', [])

            # Build lookup of exchange positions by symbol
            exchange_pos_map = {}
            for asset_pos in exchange_positions:
                pos = asset_pos.get('position', {})
                coin = pos.get('coin')
                size = float(pos.get('szi', 0))

                if coin and size != 0:
                    exchange_pos_map[coin] = {
                        'size': size,
                        'entry_price': float(pos.get('entryPx', 0)),
                        'unrealized_pnl': float(pos.get('unrealizedPnl', 0)),
                        'position_value': float(pos.get('positionValue', 0)),
                        'margin_used': float(pos.get('marginUsed', 0)),
                        'leverage': pos.get('leverage', {}),
                    }

            # Get local positions
            local_symbols = set(self.open_positions.keys())
            exchange_symbols = set(exchange_pos_map.keys())

            # Detect discrepancies
            missing_in_state = exchange_symbols - local_symbols
            extra_in_state = local_symbols - exchange_symbols

            # Log discrepancies
            if missing_in_state or extra_in_state:
                logger.warning("⚠️  POSITION SYNC DISCREPANCY DETECTED")
                logger.warning("=" * 60)

                if missing_in_state:
                    logger.warning(f"❌ Exchange has positions NOT in local state:")
                    for symbol in missing_in_state:
                        pos = exchange_pos_map[symbol]
                        logger.warning(
                            f"   {symbol}: {pos['size']:+.5f} @ ${pos['entry_price']:,.2f} "
                            f"(P&L: ${pos['unrealized_pnl']:+.2f})"
                        )

                if extra_in_state:
                    logger.warning(f"❌ Local state has positions NOT on exchange:")
                    for symbol in extra_in_state:
                        pos = self.open_positions[symbol]
                        logger.warning(
                            f"   {symbol}: {pos.get('size', 0):+.5f} @ "
                            f"${pos.get('entry_price', 0):,.2f}"
                        )

                logger.warning("=" * 60)
                logger.warning("🔧 Syncing local state to match exchange (source of truth)...")

            # Remove positions that don't exist on exchange
            for symbol in extra_in_state:
                logger.info(f"Removing {symbol} from local state (not on exchange)")
                del self.open_positions[symbol]
                self.state_manager.remove_position(symbol)

            # Add positions that exist on exchange but not in state
            for symbol in missing_in_state:
                exchange_pos = exchange_pos_map[symbol]
                logger.warning(
                    f"⚠️  Adding {symbol} to local state from exchange: "
                    f"{exchange_pos['size']:+.5f} @ ${exchange_pos['entry_price']:,.2f}"
                )

                # Create position data matching our internal structure
                # Note: We don't have the original signal, so create minimal data
                position_data = {
                    "signal": None,  # Unknown - position predates this session
                    "size": abs(exchange_pos['size']),  # Store as positive, track direction separately
                    "entry_price": exchange_pos['entry_price'],
                    "stop_loss": None,  # User set manually
                    "take_profit": None,  # User set manually
                    "timestamp": datetime.now(),  # Current time (actual entry time unknown)
                    "synced_from_exchange": True,  # Flag to indicate this was synced
                    "exchange_data": exchange_pos,  # Store full exchange data for reference
                }

                self.open_positions[symbol] = position_data
                self.state_manager.save_position(symbol, position_data)

                logger.info(
                    f"✅ Synced {symbol}: size={exchange_pos['size']:+.5f}, "
                    f"entry=${exchange_pos['entry_price']:,.2f}, "
                    f"pnl=${exchange_pos['unrealized_pnl']:+.2f}"
                )

            # Compare sizes for positions that exist in both
            common_symbols = local_symbols & exchange_symbols
            for symbol in common_symbols:
                local_size = self.open_positions[symbol].get('size', 0)
                exchange_size = abs(exchange_pos_map[symbol]['size'])

                if abs(local_size - exchange_size) > 0.0001:  # Allow for rounding
                    logger.warning(
                        f"⚠️  Size mismatch for {symbol}: "
                        f"local={local_size:.5f}, exchange={exchange_size:.5f}"
                    )
                    logger.warning(f"   Updating local state to match exchange")

                    # Update position size to match exchange
                    self.open_positions[symbol]['size'] = exchange_size
                    self.state_manager.save_position(symbol, self.open_positions[symbol])

            # Summary
            if exchange_positions:
                logger.info(f"✅ Position sync complete: {len(exchange_pos_map)} positions tracked")
            else:
                logger.info("✅ Position sync complete: No open positions on exchange")

        except Exception as e:
            # Don't fail initialization if sync fails - log and continue
            logger.error(f"Failed to sync positions with exchange: {e}", exc_info=True)
            logger.warning("Continuing with local state (may be out of sync with exchange)")
