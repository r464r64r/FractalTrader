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
            self.state_manager.set_starting_balance(portfolio_value)
            self.starting_balance = portfolio_value
            logger.info(f"Set starting balance: ${portfolio_value:,.2f}")
        else:
            self.starting_balance = self.state_manager.get_starting_balance()
            logger.info(f"Resumed session with starting balance: " f"${self.starting_balance:,.2f}")

        # Circuit breakers (testnet-specific safeguards)
        self.max_daily_drawdown = 0.20  # Stop if down 20% (more lenient than mainnet)
        self.max_daily_trades = 50  # Limit number of trades per day
        self.circuit_breaker_triggered = False

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

    def _check_circuit_breakers(self) -> bool:
        """
        Check if circuit breakers should trigger.

        Returns:
            True if trading can continue, False if breakers triggered
        """
        # Skip if already triggered
        if self.circuit_breaker_triggered:
            return False

        # 1. Check drawdown limit
        current_balance = self._get_portfolio_value()
        drawdown = (self.starting_balance - current_balance) / self.starting_balance

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

        # 2. Check trade count limit
        if len(self.trade_history) > self.max_daily_trades:
            logger.critical(
                f"🛑 CIRCUIT BREAKER TRIGGERED! Trade count {len(self.trade_history)} > "
                f"{self.max_daily_trades}"
            )
            self.circuit_breaker_triggered = True
            self.stop()
            return False

        return True

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

            # Round price to appropriate precision
            limit_price = round(limit_price, 2)

            logger.info(
                f"Placing order: {symbol} {'BUY' if is_buy else 'SELL'} "
                f"{size:.4f} @ {limit_price:.2f}"
            )

            # Place order
            order = self.exchange.order(
                symbol, is_buy, size, limit_price, {"limit": {"tif": "Gtc"}}  # Good-til-canceled
            )

            logger.info(f"Order placed: {order}")

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
    def _get_portfolio_value(self) -> float:
        """
        Get current portfolio value.

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

    def _calculate_atr(self, data) -> float:
        """Calculate current ATR (Average True Range)."""
        from strategies.base import BaseStrategy

        temp_strategy = BaseStrategy.__new__(BaseStrategy)
        atr = temp_strategy._calculate_atr(data, period=14)
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
