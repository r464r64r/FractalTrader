# Task 2: Live Trading Implementation

**Estimated Time:** 2-3 days
**Difficulty:** Medium-High
**Dependencies:** Task 1 (Data Layer) must be complete
**Goal:** Implement Hyperliquid live trading with testnet validation

---

## Overview

You will create **live trading infrastructure** for Hyperliquid DEX:

1. **Testnet Trader** — Paper trading with fake money (SAFE)
2. **Mainnet Trader** — Real trading with real money (after testnet validation)
3. **Risk Integration** — Connect existing risk management
4. **Monitoring** — Track performance and errors

**Critical:** ALWAYS start with testnet. Never touch mainnet until testnet proves stable.

---

## Implementation Plan (12 Steps)

### Phase 1: Setup & Testnet Configuration (1-2 hours)

#### Step 1: Create Directory Structure

```bash
mkdir -p live/hyperliquid
touch live/hyperliquid/__init__.py
touch live/hyperliquid/testnet.py
touch live/hyperliquid/trader.py
touch live/hyperliquid/config.py
```

#### Step 2: Create Configuration Module

**File:** `live/hyperliquid/config.py` (NEW)

```python
"""Configuration for Hyperliquid trading."""

from dataclasses import dataclass
from typing import Literal
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class HyperliquidConfig:
    """Hyperliquid trading configuration."""

    # Network
    network: Literal['testnet', 'mainnet'] = 'testnet'
    private_key: str = None  # Ethereum private key

    # Trading parameters
    default_symbol: str = 'BTC'
    default_timeframe: str = '1h'
    max_open_positions: int = 3

    # Risk limits (from risk/position_sizing.py)
    max_position_percent: float = 0.05  # 5% max per position
    base_risk_percent: float = 0.02     # 2% base risk
    min_confidence: int = 50             # Minimum confidence to trade

    # Execution
    order_type: Literal['market', 'limit'] = 'limit'
    limit_price_offset_percent: float = 0.001  # 0.1% better than market

    # Monitoring
    check_interval_seconds: int = 60  # How often to check for signals
    log_level: str = 'INFO'

    @classmethod
    def from_env(cls, network: str = 'testnet') -> 'HyperliquidConfig':
        """
        Load config from environment variables.

        Required env vars:
            HYPERLIQUID_PRIVATE_KEY - Ethereum private key (0x...)

        Optional env vars:
            HYPERLIQUID_MAX_POSITIONS - Max open positions (default: 3)
            HYPERLIQUID_MAX_RISK - Max risk per trade (default: 0.02)

        Example .env file:
            HYPERLIQUID_PRIVATE_KEY=0x1234...
            HYPERLIQUID_MAX_POSITIONS=5
            HYPERLIQUID_MAX_RISK=0.015
        """
        private_key = os.getenv('HYPERLIQUID_PRIVATE_KEY')
        if not private_key:
            raise ValueError(
                "HYPERLIQUID_PRIVATE_KEY not found in environment. "
                "Add to .env file or set environment variable."
            )

        config = cls(
            network=network,
            private_key=private_key
        )

        # Override with env vars if present
        if max_pos := os.getenv('HYPERLIQUID_MAX_POSITIONS'):
            config.max_open_positions = int(max_pos)

        if max_risk := os.getenv('HYPERLIQUID_MAX_RISK'):
            config.base_risk_percent = float(max_risk)

        return config

    def validate(self) -> None:
        """
        Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.private_key:
            raise ValueError("private_key is required")

        if not self.private_key.startswith('0x'):
            raise ValueError("private_key must start with '0x'")

        if self.max_position_percent > 0.1:
            raise ValueError("max_position_percent too high (>10%)")

        if self.base_risk_percent > 0.05:
            raise ValueError("base_risk_percent too high (>5%)")

        if self.min_confidence < 0 or self.min_confidence > 100:
            raise ValueError("min_confidence must be 0-100")
```

#### Step 3: Create `.env.example` Template

**File:** `.env.example` (NEW)

```bash
# Hyperliquid Configuration
# Copy this to .env and fill in your values

# REQUIRED: Your Ethereum private key (for signing transactions)
# ⚠️ NEVER commit your actual private key to git!
# Get testnet wallet: https://app.hyperliquid-testnet.xyz
HYPERLIQUID_PRIVATE_KEY=0x0000000000000000000000000000000000000000000000000000000000000000

# OPTIONAL: Trading parameters
HYPERLIQUID_MAX_POSITIONS=3
HYPERLIQUID_MAX_RISK=0.02
```

**Important:** Add `.env` to `.gitignore` if not already there.

---

### Phase 2: Testnet Trader (3-4 hours)

#### Step 4: Implement Testnet Paper Trading

**File:** `live/hyperliquid/testnet.py` (NEW)

```python
"""Hyperliquid testnet paper trading."""

import logging
import time
from typing import Optional
from datetime import datetime

from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

from data.hyperliquid_fetcher import HyperliquidFetcher
from strategies.base import BaseStrategy, Signal
from risk.position_sizing import calculate_position_size, RiskParameters
from live.hyperliquid.config import HyperliquidConfig


logger = logging.getLogger(__name__)


class TestnetTrader:
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
        strategy: BaseStrategy
    ):
        """
        Initialize testnet trader.

        Args:
            config: HyperliquidConfig with network='testnet'
            strategy: Strategy instance to trade

        Raises:
            ValueError: If config.network != 'testnet'
        """
        if config.network != 'testnet':
            raise ValueError("TestnetTrader requires network='testnet'")

        config.validate()

        self.config = config
        self.strategy = strategy

        # Setup wallet
        self.wallet = Account.from_key(config.private_key)
        logger.info(f"Wallet address: {self.wallet.address}")

        # Initialize Hyperliquid clients
        self.info = Info(constants.TESTNET_API_URL)
        self.exchange = Exchange(self.wallet, constants.TESTNET_API_URL)

        # Initialize data fetcher
        self.fetcher = HyperliquidFetcher(network='testnet')

        # Risk parameters
        self.risk_params = RiskParameters(
            base_risk_percent=config.base_risk_percent,
            max_position_percent=config.max_position_percent,
            min_confidence=config.min_confidence
        )

        # State tracking
        self.open_positions = {}  # symbol -> position info
        self.trade_history = []
        self.is_running = False

        logger.info("TestnetTrader initialized")

    def run(self, duration_seconds: Optional[int] = None):
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
        """Single iteration of trading loop."""
        try:
            # 1. Fetch latest data
            data = self.fetcher.fetch_ohlcv(
                self.config.default_symbol,
                self.config.default_timeframe,
                limit=500  # Enough for strategy calculations
            )

            # 2. Generate signals
            signals = self.strategy.generate_signals(data)

            if not signals:
                logger.debug("No signals generated")
                return

            # 3. Process latest signal
            latest_signal = signals[-1]
            logger.info(f"Signal: {latest_signal.direction} @ {latest_signal.entry_price}")

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
                params=self.risk_params
            )

            if position_size == 0:
                logger.info("Position size = 0 (confidence too low or risk limits)")
                return

            # 6. Place order
            self._place_order(latest_signal, position_size)

        except Exception as e:
            logger.error(f"Iteration error: {e}", exc_info=True)

    def _place_order(self, signal: Signal, size: float):
        """
        Place order on Hyperliquid.

        Args:
            signal: Trading signal
            size: Position size in base currency

        Example order:
            Direction: LONG
            Size: 0.1 BTC
            Entry: $42000
            Stop: $41500
        """
        try:
            symbol = self.config.default_symbol
            is_buy = signal.direction == 1

            # Get current market price for limit order
            current_price = self.fetcher.get_current_price(symbol)

            # Calculate limit price (slightly better than market)
            offset = self.config.limit_price_offset_percent
            if is_buy:
                limit_price = current_price * (1 - offset)  # Buy lower
            else:
                limit_price = current_price * (1 + offset)  # Sell higher

            # Round price to appropriate precision
            limit_price = round(limit_price, 2)

            # Place order
            logger.info(f"Placing order: {symbol} {'BUY' if is_buy else 'SELL'} {size} @ {limit_price}")

            order = self.exchange.order(
                symbol,
                is_buy,
                size,
                limit_price,
                {"limit": {"tif": "Gtc"}}  # Good-til-canceled
            )

            logger.info(f"Order placed: {order}")

            # Track position
            self.open_positions[symbol] = {
                'signal': signal,
                'size': size,
                'entry_price': limit_price,
                'stop_loss': signal.stop_loss,
                'take_profit': signal.take_profit,
                'timestamp': datetime.now(),
                'order': order
            }

            # Record trade
            self.trade_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'direction': 'LONG' if is_buy else 'SHORT',
                'size': size,
                'entry_price': limit_price,
                'stop_loss': signal.stop_loss,
                'confidence': signal.confidence,
                'status': 'OPEN'
            })

        except Exception as e:
            logger.error(f"Order placement failed: {e}", exc_info=True)

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
            margin_summary = user_state.get('marginSummary', {})
            account_value = float(margin_summary.get('accountValue', 100000))

            return account_value

        except Exception as e:
            logger.error(f"Failed to get portfolio value: {e}")
            return 100000  # Default testnet starting balance

    def _calculate_atr(self, data) -> float:
        """Calculate current ATR (Average True Range)."""
        # Use existing implementation from strategies
        from strategies.base import BaseStrategy
        temp_strategy = BaseStrategy.__new__(BaseStrategy)
        return temp_strategy._calculate_atr(data, period=14).iloc[-1]

    def _calculate_baseline_atr(self, data) -> float:
        """Calculate baseline ATR (50-period average)."""
        atr = self._calculate_atr(data)
        return atr  # Simplified for now

    def _count_consecutive_wins(self) -> int:
        """Count consecutive winning trades."""
        count = 0
        for trade in reversed(self.trade_history):
            if trade.get('pnl', 0) > 0:
                count += 1
            else:
                break
        return count

    def _count_consecutive_losses(self) -> int:
        """Count consecutive losing trades."""
        count = 0
        for trade in reversed(self.trade_history):
            if trade.get('pnl', 0) < 0:
                count += 1
            else:
                break
        return count

    def stop(self):
        """Stop trading loop."""
        self.is_running = False
        logger.info("Testnet trader stopped")

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
```

#### Step 5: Create Testnet Example Script

**File:** `examples/testnet_trading_example.py` (NEW)

```python
"""Example: Paper trading on Hyperliquid testnet."""

import logging
from live.hyperliquid.config import HyperliquidConfig
from live.hyperliquid.testnet import TestnetTrader
from strategies.liquidity_sweep import LiquiditySweepStrategy

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    """Run testnet paper trading."""

    # Load configuration
    config = HyperliquidConfig.from_env(network='testnet')

    # Choose strategy
    strategy = LiquiditySweepStrategy()

    # Create trader
    trader = TestnetTrader(config, strategy)

    # Run for 1 hour (testing)
    # For production: trader.run()  # Runs indefinitely
    trader.run(duration_seconds=3600)


if __name__ == '__main__':
    main()
```

**Usage:**
```bash
# Set up .env file first
cp .env.example .env
# Edit .env and add your testnet private key

# Run testnet trading
python examples/testnet_trading_example.py
```

---

### Phase 3: Mainnet Trader (2-3 hours)

#### Step 6: Implement Mainnet Trading

**File:** `live/hyperliquid/trader.py` (NEW)

**⚠️ WARNING:** This trades REAL money. Only use after testnet validation.

```python
"""Hyperliquid mainnet live trading."""

import logging
from typing import Optional
from live.hyperliquid.testnet import TestnetTrader
from hyperliquid.utils import constants
from live.hyperliquid.config import HyperliquidConfig


logger = logging.getLogger(__name__)


class HyperliquidTrader(TestnetTrader):
    """
    Live trading on Hyperliquid mainnet.

    ⚠️ WARNING: Uses REAL money!

    Only use after:
    1. Testnet validation (24+ hours stable)
    2. Small position sizes
    3. Manual monitoring

    Inherits from TestnetTrader (same logic, different network).
    """

    def __init__(self, config: HyperliquidConfig, strategy):
        """
        Initialize mainnet trader.

        Args:
            config: HyperliquidConfig with network='mainnet'
            strategy: Strategy instance

        Raises:
            ValueError: If config.network != 'mainnet'
            RuntimeError: If testnet validation not confirmed
        """
        if config.network != 'mainnet':
            raise ValueError("HyperliquidTrader requires network='mainnet'")

        # Safety check: require explicit confirmation
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
        # Override network-specific parts
        self.config = config
        self.strategy = strategy

        # ... rest of initialization identical to TestnetTrader
        # but uses constants.MAINNET_API_URL

        super().__init__(config, strategy)

        # Override API URLs to mainnet
        from hyperliquid.info import Info
        from hyperliquid.exchange import Exchange
        from eth_account import Account

        self.wallet = Account.from_key(config.private_key)
        self.info = Info(constants.MAINNET_API_URL)
        self.exchange = Exchange(self.wallet, constants.MAINNET_API_URL)

        # Use mainnet data fetcher
        from data.hyperliquid_fetcher import HyperliquidFetcher
        self.fetcher = HyperliquidFetcher(network='mainnet')

        logger.warning("🚨 MAINNET TRADER INITIALIZED - REAL MONEY 🚨")

    def run(self, duration_seconds: Optional[int] = None):
        """
        Run mainnet trading loop.

        Safety features:
        - Logs all trades
        - Monitors portfolio value
        - Stops on large drawdown
        """
        # Additional safety: max drawdown stop
        initial_value = self._get_portfolio_value()
        max_drawdown_percent = 0.10  # Stop if down 10%

        def check_drawdown():
            current_value = self._get_portfolio_value()
            drawdown = (initial_value - current_value) / initial_value
            if drawdown > max_drawdown_percent:
                logger.error(f"Max drawdown exceeded: {drawdown:.2%}")
                self.stop()
                raise RuntimeError("Max drawdown exceeded - trading stopped")

        # Override iteration to include drawdown check
        original_iteration = self._trading_iteration

        def safe_iteration():
            check_drawdown()
            original_iteration()

        self._trading_iteration = safe_iteration

        # Run parent class trading loop
        super().run(duration_seconds)
```

#### Step 7: Create Mainnet Example (with safety warnings)

**File:** `examples/mainnet_trading_example.py` (NEW)

```python
"""
Example: Live trading on Hyperliquid mainnet.

⚠️ WARNING: This uses REAL money!

Prerequisites:
1. Testnet validation (24+ hours stable)
2. Small starting capital ($100-$1000)
3. Manual monitoring for first week
4. Stop-loss discipline

DO NOT RUN unless you understand the risks!
"""

import logging
from live.hyperliquid.config import HyperliquidConfig
from live.hyperliquid.trader import HyperliquidTrader
from strategies.liquidity_sweep import LiquiditySweepStrategy

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mainnet_trading.log'),  # Log to file
        logging.StreamHandler()  # Also print to console
    ]
)


def main():
    """Run mainnet live trading."""

    print("\n⚠️  READ THIS BEFORE PROCEEDING ⚠️\n")
    print("This script trades REAL money on Hyperliquid mainnet.")
    print("You can lose your entire capital.")
    print("\nRecommended steps:")
    print("1. Validate on testnet for 24+ hours")
    print("2. Start with small capital ($100-$1000)")
    print("3. Monitor manually for first week")
    print("4. Use strict risk limits")
    print("\nType 'I UNDERSTAND THE RISKS' to continue")

    user_input = input("\n> ")
    if user_input != "I UNDERSTAND THE RISKS":
        print("Exiting. Run testnet instead: python examples/testnet_trading_example.py")
        return

    # Load configuration
    config = HyperliquidConfig.from_env(network='mainnet')

    # Use conservative settings for mainnet
    config.base_risk_percent = 0.01  # 1% risk per trade (conservative)
    config.max_position_percent = 0.03  # 3% max position (conservative)
    config.min_confidence = 60  # Higher confidence threshold

    # Choose strategy
    strategy = LiquiditySweepStrategy()

    # Create trader (will require CONFIRM input)
    trader = HyperliquidTrader(config, strategy)

    # Run indefinitely (production mode)
    # Use Ctrl+C to stop gracefully
    trader.run()


if __name__ == '__main__':
    main()
```

---

### Phase 4: Testing & Validation (2-3 hours)

#### Step 8: Write Tests

**File:** `tests/test_live_trading.py` (NEW)

```python
"""Tests for live trading components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

from live.hyperliquid.config import HyperliquidConfig
from live.hyperliquid.testnet import TestnetTrader
from strategies.liquidity_sweep import LiquiditySweepStrategy


class TestHyperliquidConfig:
    """Tests for configuration."""

    def test_config_initialization(self):
        """Test basic config creation."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64
        )

        assert config.network == 'testnet'
        assert config.private_key.startswith('0x')

    def test_config_validation_rejects_invalid_key(self):
        """Test validation catches bad private key."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='invalid_key'  # Missing 0x
        )

        with pytest.raises(ValueError, match="must start with '0x'"):
            config.validate()

    def test_config_validation_rejects_high_risk(self):
        """Test validation catches excessive risk."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64,
            base_risk_percent=0.10  # 10% too high
        )

        with pytest.raises(ValueError, match="too high"):
            config.validate()

    def test_config_from_env(self, monkeypatch):
        """Test loading config from environment."""
        monkeypatch.setenv('HYPERLIQUID_PRIVATE_KEY', '0x' + '1' * 64)
        monkeypatch.setenv('HYPERLIQUID_MAX_POSITIONS', '5')

        config = HyperliquidConfig.from_env('testnet')

        assert config.private_key == '0x' + '1' * 64
        assert config.max_open_positions == 5

    def test_config_from_env_missing_key_raises_error(self, monkeypatch):
        """Test error when private key not in env."""
        monkeypatch.delenv('HYPERLIQUID_PRIVATE_KEY', raising=False)

        with pytest.raises(ValueError, match="not found in environment"):
            HyperliquidConfig.from_env()


class TestTestnetTrader:
    """Tests for testnet trading."""

    @pytest.fixture
    def config(self):
        """Create test config."""
        return HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64,  # Dummy key for testing
            check_interval_seconds=1  # Fast for tests
        )

    @pytest.fixture
    def strategy(self):
        """Create test strategy."""
        return LiquiditySweepStrategy()

    @pytest.fixture
    def trader(self, config, strategy):
        """Create trader instance (mocked)."""
        with patch('live.hyperliquid.testnet.Info'), \
             patch('live.hyperliquid.testnet.Exchange'), \
             patch('live.hyperliquid.testnet.HyperliquidFetcher'):
            trader = TestnetTrader(config, strategy)
            return trader

    def test_trader_initialization(self, trader, config, strategy):
        """Test trader initializes correctly."""
        assert trader.config == config
        assert trader.strategy == strategy
        assert trader.is_running is False
        assert len(trader.open_positions) == 0

    def test_trader_rejects_mainnet_config(self, strategy):
        """Test TestnetTrader rejects mainnet config."""
        config = HyperliquidConfig(
            network='mainnet',  # Wrong network
            private_key='0x' + '0' * 64
        )

        with pytest.raises(ValueError, match="requires network='testnet'"):
            TestnetTrader(config, strategy)

    @patch('live.hyperliquid.testnet.TestnetTrader._trading_iteration')
    def test_run_stops_after_duration(self, mock_iteration, trader):
        """Test run() stops after specified duration."""
        trader.run(duration_seconds=2)

        # Should have run at least once
        assert mock_iteration.call_count >= 1
        assert trader.is_running is False

    def test_portfolio_value_defaults_to_100k(self, trader):
        """Test portfolio value defaults to testnet starting balance."""
        # Mock API failure
        trader.info.user_state = Mock(side_effect=Exception("API error"))

        value = trader._get_portfolio_value()
        assert value == 100000  # Testnet default

    def test_consecutive_wins_counted_correctly(self, trader):
        """Test counting consecutive wins."""
        trader.trade_history = [
            {'pnl': 100},
            {'pnl': 50},
            {'pnl': 75},
            {'pnl': -20},  # Loss breaks streak
        ]

        assert trader._count_consecutive_wins() == 3

    def test_consecutive_losses_counted_correctly(self, trader):
        """Test counting consecutive losses."""
        trader.trade_history = [
            {'pnl': -100},
            {'pnl': -50},
            {'pnl': 100},  # Win breaks streak
        ]

        assert trader._count_consecutive_losses() == 2

    @patch('live.hyperliquid.testnet.TestnetTrader._get_portfolio_value')
    @patch('live.hyperliquid.testnet.calculate_position_size')
    def test_trading_iteration_skips_low_confidence(
        self,
        mock_calc_size,
        mock_portfolio,
        trader
    ):
        """Test iteration skips when position size = 0."""
        mock_portfolio.return_value = 100000
        mock_calc_size.return_value = 0  # Position size too small

        # Mock data fetch
        trader.fetcher.fetch_ohlcv = Mock(return_value=pd.DataFrame({
            'open': [100],
            'high': [101],
            'low': [99],
            'close': [100],
            'volume': [1000]
        }, index=pd.DatetimeIndex(['2024-01-01'])))

        # Mock signal generation
        from strategies.base import Signal
        trader.strategy.generate_signals = Mock(return_value=[
            Signal(
                timestamp=pd.Timestamp('2024-01-01'),
                direction=1,
                entry_price=100,
                stop_loss=95,
                take_profit=110,
                confidence=30,  # Low confidence
                strategy_name='test',
                metadata={}
            )
        ])

        trader._trading_iteration()

        # Should not place order (size = 0)
        assert len(trader.open_positions) == 0

    def test_stop_sets_running_false(self, trader):
        """Test stop() sets is_running to False."""
        trader.is_running = True
        trader.stop()
        assert trader.is_running is False


class TestIntegration:
    """Integration tests (require network access)."""

    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="Integration tests disabled (use --run-integration)"
    )
    def test_testnet_connection(self):
        """Test actual connection to testnet."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64  # Dummy key
        )

        from hyperliquid.info import Info
        from hyperliquid.utils import constants

        info = Info(constants.TESTNET_API_URL)
        symbols = info.meta()

        assert 'universe' in symbols
        assert len(symbols['universe']) > 0

    @pytest.mark.skipif(
        not pytest.config.getoption("--run-integration"),
        reason="Integration tests disabled"
    )
    def test_fetch_testnet_data(self):
        """Test fetching data from testnet."""
        from data.hyperliquid_fetcher import HyperliquidFetcher

        fetcher = HyperliquidFetcher(network='testnet')
        df = fetcher.fetch_ohlcv('BTC', '1h', limit=10)

        assert len(df) == 10
        assert list(df.columns) == ['open', 'high', 'low', 'close', 'volume']
```

**Add pytest config for integration tests:**

**File:** `pytest.ini` (update)

```ini
[pytest]
markers =
    integration: Integration tests (require network access)

addopts = --tb=short
```

**Run tests:**
```bash
# Unit tests only
python -m pytest tests/test_live_trading.py -v

# Include integration tests (requires network)
python -m pytest tests/test_live_trading.py -v --run-integration
```

---

### Phase 5: Monitoring & Documentation (1 hour)

#### Step 9: Add Logging Configuration

**File:** `live/hyperliquid/logger.py` (NEW)

```python
"""Logging configuration for live trading."""

import logging
import sys
from pathlib import Path


def setup_logging(log_level: str = 'INFO', log_file: str = None):
    """
    Setup logging for live trading.

    Args:
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_file: Optional log file path

    Example:
        >>> setup_logging('INFO', 'logs/trading.log')
    """
    # Create logs directory if needed
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Configure logging
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    # Reduce noise from external libraries
    logging.getLogger('hyperliquid').setLevel(logging.WARNING)
    logging.getLogger('ccxt').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
```

#### Step 10: Update `live/__init__.py`

```python
"""Live trading module."""

from live.hyperliquid.config import HyperliquidConfig
from live.hyperliquid.testnet import TestnetTrader
from live.hyperliquid.trader import HyperliquidTrader
from live.hyperliquid.logger import setup_logging

__all__ = [
    'HyperliquidConfig',
    'TestnetTrader',
    'HyperliquidTrader',
    'setup_logging',
]
```

#### Step 11: Update Documentation

**Update:** `DEVELOPMENT.md`

**Add after Data Layer section:**

```markdown
### Live Trading (NEW - Sprint 7)

| Component | File | Status | Tests | Coverage |
|-----------|------|--------|-------|----------|
| Config | `live/hyperliquid/config.py` | ✅ Done | 5 | 100% |
| Testnet Trader | `live/hyperliquid/testnet.py` | ✅ Done | 8 | 75% |
| Mainnet Trader | `live/hyperliquid/trader.py` | ✅ Done | 2 | 70% |

**Total Tests:** 15 new tests (172 total)

**Usage:**

**Testnet (Paper Trading):**
```python
from live.hyperliquid.config import HyperliquidConfig
from live.hyperliquid.testnet import TestnetTrader
from strategies.liquidity_sweep import LiquiditySweepStrategy

config = HyperliquidConfig.from_env(network='testnet')
strategy = LiquiditySweepStrategy()
trader = TestnetTrader(config, strategy)
trader.run(duration_seconds=3600)  # Run for 1 hour
```

**Mainnet (Real Trading - after testnet validation):**
```python
# ⚠️ WARNING: Uses REAL money!
config = HyperliquidConfig.from_env(network='mainnet')
trader = HyperliquidTrader(config, strategy)
trader.run()  # Requires manual confirmation
```

**Testnet URL:** https://app.hyperliquid-testnet.xyz/trade
```

**Update:** `README.md`

**Add section after "Basic Usage":**

```markdown
### Live Trading

**⚠️ Always test on testnet first!**

1. **Setup Configuration:**
   ```bash
   cp .env.example .env
   # Edit .env and add your private key
   ```

2. **Run Testnet (Paper Trading):**
   ```bash
   python examples/testnet_trading_example.py
   ```

3. **Monitor Testnet Performance:**
   - Let run for 24+ hours
   - Check logs: `logs/trading.log`
   - Verify no crashes
   - Confirm profitable trades

4. **Deploy to Mainnet (after validation):**
   ```bash
   # Only after testnet validation!
   python examples/mainnet_trading_example.py
   ```
```

---

## Checklist (Definition of Done)

### Code Quality
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] Error handling for API failures
- [ ] Comprehensive logging
- [ ] Safety checks (confirmations, drawdown limits)

### Testing
- [ ] 5+ tests for HyperliquidConfig
- [ ] 8+ tests for TestnetTrader
- [ ] 2+ tests for HyperliquidTrader
- [ ] Integration tests (optional, with --run-integration flag)
- [ ] All tests passing: `python -m pytest tests/test_live_trading.py -v`

### Functionality
- [ ] Testnet trader runs without crashes
- [ ] Orders successfully placed on testnet
- [ ] Position tracking works
- [ ] Risk limits enforced
- [ ] Drawdown protection works
- [ ] Logging captures all events

### Safety
- [ ] Mainnet requires manual confirmation
- [ ] Max drawdown stop implemented
- [ ] All trades logged to file
- [ ] Conservative defaults (low risk%)
- [ ] Clear warnings in code and docs

### Documentation
- [ ] DEVELOPMENT.md updated
- [ ] README.md updated with live trading section
- [ ] Example scripts created
- [ ] .env.example template provided
- [ ] Safety warnings prominent

---

## Deployment Checklist

Before running on testnet:
- [ ] `.env` file configured with testnet key
- [ ] Wallet has testnet funds
- [ ] Strategy validated in backtests (Sharpe >1.0)
- [ ] Risk limits conservative (1-2% per trade)

Before deploying to mainnet:
- [ ] Testnet ran successfully for 24+ hours
- [ ] No crashes or errors in logs
- [ ] Profitable on testnet (positive P&L)
- [ ] Small starting capital ($100-$1000)
- [ ] Manual monitoring plan in place
- [ ] Emergency stop procedure documented

---

## Troubleshooting

### Issue: "HYPERLIQUID_PRIVATE_KEY not found"

**Solution:**
```bash
cp .env.example .env
# Edit .env and add your private key
# Testnet: Get wallet at https://app.hyperliquid-testnet.xyz
```

### Issue: Order placement fails

**Symptoms:** `Order placement failed: insufficient margin`

**Solution:**
- Check testnet wallet has funds
- Reduce position size
- Check `max_position_percent` in config

### Issue: No signals generated

**Symptoms:** "No signals generated" in logs

**Solution:**
- Check market conditions (may not have setups)
- Review strategy parameters
- Verify data fetch is working: `df.tail()`

### Issue: Testnet connection timeout

**Solution:**
```python
fetcher = HyperliquidFetcher(network='testnet', timeout=60)
```

---

## Next Steps

After completing Task 2:

1. ✅ Run testnet for 24+ hours
2. ✅ Verify all tests pass
3. ✅ Commit code
4. ✅ Update documentation
5. ⏭️ Create end-to-end integration test
6. ⏭️ Prepare for mainnet deployment

---

**Estimated completion time:** 2-3 days

**When done, you'll have:**
- Fully functional testnet paper trading
- Mainnet trading (ready after validation)
- 15 new passing tests
- 172 total tests (157 + 15)
- Production-ready MVP

**WARNING:** Never skip testnet validation. Always test thoroughly before risking real money.

Good luck! 🚀
