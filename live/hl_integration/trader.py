"""Hyperliquid mainnet live trading."""

import logging
from datetime import datetime

from hyperliquid.utils import constants

from live.hl_integration.config import HyperliquidConfig
from live.hl_integration.testnet import HyperliquidTestnetTrader
from live.state_manager import StateManager
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
        state_file: str = ".mainnet_state.json",
        confirm: bool = False,
    ):
        """
        Initialize mainnet trader.

        Args:
            config: HyperliquidConfig with network='mainnet'
            strategy: Strategy instance
            state_file: Path to state file for persistence
            confirm: If True, skip interactive confirmation (for testing)

        Raises:
            ValueError: If config.network != 'mainnet'
            RuntimeError: If mainnet trading not confirmed
        """
        if config.network != "mainnet":
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
            if confirmation != "CONFIRM":
                raise RuntimeError("Mainnet trading not confirmed")

        # Initialize parent class (TestnetTrader logic)
        config.validate()

        self.config = config
        self.strategy = strategy
        self.simulation_mode = False  # Mainnet is never simulation

        # Setup wallet
        from eth_account import Account

        self.wallet = Account.from_key(config.private_key)
        logger.info(f"Mainnet wallet address: {self.wallet.address}")

        # Initialize Hyperliquid clients (MAINNET!)
        from hyperliquid.exchange import Exchange
        from hyperliquid.info import Info

        self.info = Info(constants.MAINNET_API_URL, skip_ws=True)
        self.exchange = Exchange(self.wallet, constants.MAINNET_API_URL)

        # Initialize data fetcher
        from data.hyperliquid_fetcher import HyperliquidFetcher

        self.fetcher = HyperliquidFetcher(network="mainnet")

        # Risk parameters
        from risk.position_sizing import RiskParameters

        self.risk_params = RiskParameters(
            base_risk_percent=config.base_risk_percent,
            max_position_percent=config.max_position_percent,
            min_confidence=config.min_confidence,
        )

        # Initialize state manager (CRITICAL for mainnet - must persist!)
        self.state_manager = StateManager(state_file=state_file, auto_save=True, backup_count=10)

        # Load state from previous session
        self.open_positions: dict = self.state_manager.load_positions()
        self.trade_history: list[dict] = self.state_manager.load_trade_history()
        self.is_running = False

        # Set starting balance
        if self.state_manager.get_starting_balance() == 0:
            portfolio_value = self._get_actual_portfolio_value()
            self.state_manager.set_starting_balance(portfolio_value)
            self.starting_balance = portfolio_value
            logger.info(f"Set starting balance: ${portfolio_value:,.2f}")
        else:
            self.starting_balance = self.state_manager.get_starting_balance()
            logger.info(f"Resumed session with starting balance: ${self.starting_balance:,.2f}")

        # Mainnet-specific: Tighter circuit breakers
        self.max_daily_drawdown = 0.10  # Stop if down 10% (stricter than testnet)
        self.max_daily_trades = 20  # Fewer trades on mainnet
        self.circuit_breaker_triggered = False
        self._circuit_breaker_date = datetime.now().date()

        # Sync positions with exchange
        self._sync_positions_with_exchange()

        logger.info("HyperliquidTrader initialized (MAINNET)")
        logger.warning(f"Starting balance: ${self.starting_balance:,.2f}")
        if self.open_positions:
            logger.warning(f"Loaded {len(self.open_positions)} open positions from previous session")

    def _trading_iteration(self):
        """Single iteration of trading loop with mainnet safeguards."""
        # Use parent class implementation - it has position monitoring,
        # circuit breakers, and all safety features built in.
        # The only difference is that mainnet has tighter limits (set in __init__).
        super()._trading_iteration()

    def _print_summary(self):
        """Print trading session summary with mainnet warnings."""
        # Force save state before printing summary
        self.state_manager.force_save()

        current_balance = self._get_portfolio_value()
        pnl = current_balance - self.starting_balance
        pnl_pct = (pnl / self.starting_balance * 100) if self.starting_balance > 0 else 0

        logger.info("=" * 50)
        logger.info("⚠️  MAINNET TRADING SESSION SUMMARY ⚠️")
        logger.info("=" * 50)
        logger.info(f"Starting balance: ${self.starting_balance:,.2f}")
        logger.info(f"Final balance: ${current_balance:,.2f}")
        logger.info(f"P&L: ${pnl:,.2f} ({pnl_pct:.2f}%)")
        logger.info(f"Total trades: {len(self.trade_history)}")
        logger.info(f"Open positions: {len(self.open_positions)}")
        if self.open_positions:
            logger.warning("⚠️  OPEN POSITIONS REMAIN - Manual intervention may be needed!")
            for symbol, pos in self.open_positions.items():
                logger.warning(f"   {symbol}: {pos.get('size', 0):.4f} @ ${pos.get('entry_price', 0):,.2f}")
        logger.info("=" * 50)
        logger.info("State saved to disk")
