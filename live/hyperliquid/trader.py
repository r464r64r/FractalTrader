"""Hyperliquid mainnet live trading."""

import logging
from typing import Optional
from hyperliquid.utils import constants

from live.hyperliquid.testnet import HyperliquidTestnetTrader
from live.hyperliquid.config import HyperliquidConfig
from strategies.base import BaseStrategy


logger = logging.getLogger(__name__)


class HyperliquidTrader(HyperliquidTestnetTrader):
    """
    Live trading on Hyperliquid mainnet.

    ⚠️ WARNING: Uses REAL money!

    Only use after:
    1. Testnet validation (24+ hours stable)
    2. Small position sizes
    3. Manual monitoring

    Inherits from TestnetTrader (same logic, different network).
    """

    def __init__(
        self,
        config: HyperliquidConfig,
        strategy: BaseStrategy,
        confirm: bool = False
    ):
        """
        Initialize mainnet trader.

        Args:
            config: HyperliquidConfig with network='mainnet'
            strategy: Strategy instance
            confirm: If True, skip interactive confirmation (for testing)

        Raises:
            ValueError: If config.network != 'mainnet'
            RuntimeError: If mainnet trading not confirmed
        """
        if config.network != 'mainnet':
            raise ValueError("HyperliquidTrader requires network='mainnet'")

        # Safety check: require explicit confirmation
        if not confirm:
            print("=" * 60)
            print("⚠️  MAINNET TRADING - REAL MONEY AT RISK ⚠️")
            print("=" * 60)
            print(f"Strategy: {strategy.name}")
            print(f"Max risk per trade: {config.base_risk_percent:.2%}")
            print(f"Max positions: {config.max_open_positions}")
            print("=" * 60)

            confirmation = input("Type 'CONFIRM' to proceed with mainnet trading: ")
            if confirmation != 'CONFIRM':
                raise RuntimeError("Mainnet trading not confirmed")

        # Initialize parent class (TestnetTrader logic)
        config.validate()

        self.config = config
        self.strategy = strategy

        # Setup wallet
        from eth_account import Account
        self.wallet = Account.from_key(config.private_key)
        logger.info(f"Mainnet wallet address: {self.wallet.address}")

        # Initialize Hyperliquid clients (MAINNET!)
        from hyperliquid.info import Info
        from hyperliquid.exchange import Exchange

        self.info = Info(constants.MAINNET_API_URL, skip_ws=True)
        self.exchange = Exchange(self.wallet, constants.MAINNET_API_URL)

        # Initialize data fetcher
        from data.hyperliquid_fetcher import HyperliquidFetcher
        self.fetcher = HyperliquidFetcher(network='mainnet')

        # Risk parameters
        from risk.position_sizing import RiskParameters
        self.risk_params = RiskParameters(
            base_risk_percent=config.base_risk_percent,
            max_position_percent=config.max_position_percent,
            min_confidence=config.min_confidence
        )

        # State tracking
        self.open_positions = {}  # symbol -> position info
        self.trade_history = []
        self.is_running = False

        # Mainnet-specific: Circuit breaker
        self.max_daily_drawdown = 0.10  # Stop if down 10%
        self.starting_balance = self._get_portfolio_value()

        logger.info("HyperliquidTrader initialized (MAINNET)")
        logger.warning(f"Starting balance: ${self.starting_balance:,.2f}")

    def _trading_iteration(self):
        """Single iteration of trading loop with mainnet safeguards."""
        try:
            # Check circuit breaker
            current_balance = self._get_portfolio_value()
            drawdown = (self.starting_balance - current_balance) / self.starting_balance

            if drawdown > self.max_daily_drawdown:
                logger.critical(
                    f"CIRCUIT BREAKER TRIGGERED! Drawdown {drawdown:.2%} > "
                    f"{self.max_daily_drawdown:.2%}"
                )
                self.stop()
                return

            # Call parent trading iteration
            super()._trading_iteration()

        except Exception as e:
            logger.error(f"Mainnet iteration error: {e}", exc_info=True)

    def _print_summary(self):
        """Print trading session summary with mainnet warnings."""
        current_balance = self._get_portfolio_value()
        pnl = current_balance - self.starting_balance
        pnl_pct = (pnl / self.starting_balance * 100) if self.starting_balance > 0 else 0

        logger.info("=" * 50)
        logger.info("MAINNET TRADING SESSION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Starting balance: ${self.starting_balance:,.2f}")
        logger.info(f"Final balance: ${current_balance:,.2f}")
        logger.info(f"P&L: ${pnl:,.2f} ({pnl_pct:.2f}%)")
        logger.info(f"Total trades: {len(self.trade_history)}")
        logger.info(f"Open positions: {len(self.open_positions)}")
        logger.info("=" * 50)
