"""Tests for live trading implementation."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from live.hyperliquid.config import HyperliquidConfig
from live.hyperliquid.testnet import HyperliquidTestnetTrader
from live.hyperliquid.trader import HyperliquidTrader
from strategies.liquidity_sweep import LiquiditySweepStrategy


class TestHyperliquidConfig:
    """Tests for configuration."""

    def test_config_initialization(self):
        """Test config initializes with defaults."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64
        )
        assert config.network == 'testnet'
        assert config.default_symbol == 'BTC'
        assert config.max_open_positions == 3

    def test_config_validation_success(self):
        """Test valid config passes validation."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64
        )
        config.validate()  # Should not raise

    def test_config_validation_missing_key(self):
        """Test validation fails without private key."""
        config = HyperliquidConfig(network='testnet', private_key=None)
        with pytest.raises(ValueError, match="private_key is required"):
            config.validate()

    def test_config_validation_invalid_key_format(self):
        """Test validation fails with invalid key format."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='invalid_key'
        )
        with pytest.raises(ValueError, match="must start with '0x'"):
            config.validate()

    def test_config_validation_max_position_too_high(self):
        """Test validation fails if max position % too high."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64,
            max_position_percent=0.15  # 15% is too high
        )
        with pytest.raises(ValueError, match="max_position_percent too high"):
            config.validate()

    def test_config_validation_max_risk_too_high(self):
        """Test validation fails if max risk % too high."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64,
            base_risk_percent=0.1  # 10% is too high
        )
        with pytest.raises(ValueError, match="base_risk_percent too high"):
            config.validate()

    def test_config_validation_confidence_bounds(self):
        """Test validation fails if confidence out of bounds."""
        # Test too low
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64,
            min_confidence=-1
        )
        with pytest.raises(ValueError, match="min_confidence must be 0-100"):
            config.validate()

        # Test too high
        config.min_confidence = 101
        with pytest.raises(ValueError, match="min_confidence must be 0-100"):
            config.validate()

    def test_config_from_env_missing_key(self):
        """Test from_env fails when key not in environment."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="HYPERLIQUID_PRIVATE_KEY not found"):
                HyperliquidConfig.from_env()

    def test_config_from_env_with_overrides(self):
        """Test from_env loads from environment variables."""
        env_vars = {
            'HYPERLIQUID_PRIVATE_KEY': '0x' + '1' * 64,
            'HYPERLIQUID_MAX_POSITIONS': '5',
            'HYPERLIQUID_MAX_RISK': '0.03'
        }
        with patch.dict('os.environ', env_vars):
            config = HyperliquidConfig.from_env('testnet')
            assert config.private_key == '0x' + '1' * 64
            assert config.max_open_positions == 5
            assert config.base_risk_percent == 0.03


class TestTestnetTrader:
    """Tests for testnet trader."""

    @pytest.fixture
    def mock_config(self):
        """Create mock config."""
        return HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64,
            check_interval_seconds=1  # Fast for tests
        )

    @pytest.fixture
    def mock_strategy(self):
        """Create mock strategy."""
        strategy = Mock(spec=LiquiditySweepStrategy)
        strategy.name = 'LiquiditySweep'
        strategy.generate_signals = Mock(return_value=[])
        return strategy

    @pytest.fixture
    def testnet_trader(self, mock_config, mock_strategy):
        """Create testnet trader with mocks."""
        with patch('live.hyperliquid.testnet.Account'):
            with patch('live.hyperliquid.testnet.Info'):
                with patch('live.hyperliquid.testnet.Exchange'):
                    with patch('live.hyperliquid.testnet.HyperliquidFetcher'):
                        trader = HyperliquidTestnetTrader(mock_config, mock_strategy)
                        # Mock the wallet
                        trader.wallet = Mock()
                        trader.wallet.address = '0xtest'
                        return trader

    def test_testnet_trader_initialization(self, mock_config, mock_strategy):
        """Test testnet trader initializes correctly."""
        with patch('live.hyperliquid.testnet.Account'):
            with patch('live.hyperliquid.testnet.Info'):
                with patch('live.hyperliquid.testnet.Exchange'):
                    with patch('live.hyperliquid.testnet.HyperliquidFetcher'):
                        trader = HyperliquidTestnetTrader(mock_config, mock_strategy)
                        assert trader.config == mock_config
                        assert trader.strategy == mock_strategy
                        assert not trader.is_running

    def test_testnet_trader_requires_testnet_network(self):
        """Test testnet trader rejects mainnet config."""
        config = HyperliquidConfig(
            network='mainnet',
            private_key='0x' + '0' * 64
        )
        strategy = Mock()

        with pytest.raises(ValueError, match="requires network='testnet'"):
            with patch('live.hyperliquid.testnet.Account'):
                HyperliquidTestnetTrader(config, strategy)

    def test_testnet_trader_validates_config(self, mock_strategy):
        """Test testnet trader validates config on init."""
        config = HyperliquidConfig(
            network='testnet',
            private_key=None  # Invalid
        )
        strategy = mock_strategy

        with pytest.raises(ValueError, match="private_key is required"):
            with patch('live.hyperliquid.testnet.Account'):
                HyperliquidTestnetTrader(config, strategy)

    def test_testnet_trader_position_limit(self, testnet_trader):
        """Test trader respects max open positions."""
        # Fill positions
        testnet_trader.open_positions = {'BTC': {}, 'ETH': {}, 'SOL': {}}

        # Try to add another
        signal = Mock()
        signal.confidence = 100
        signal.entry_price = 50000

        # Should return early due to position limit
        testnet_trader.strategy.generate_signals = Mock(
            return_value=[signal]
        )
        testnet_trader.fetcher.get_current_price = Mock(return_value=50000)

        # Mock portfolio
        testnet_trader._get_portfolio_value = Mock(return_value=100000)
        testnet_trader._calculate_atr = Mock(return_value=100)
        testnet_trader._calculate_baseline_atr = Mock(return_value=100)

        # This should not place an order due to position limit
        testnet_trader._trading_iteration()

        # open_positions should still be 3
        assert len(testnet_trader.open_positions) == 3

    def test_testnet_trader_respects_min_confidence(self, testnet_trader):
        """Test trader respects minimum confidence."""
        testnet_trader.config.min_confidence = 70

        signal = Mock()
        signal.confidence = 50  # Below minimum
        signal.entry_price = 50000

        testnet_trader.strategy.generate_signals = Mock(return_value=[signal])
        testnet_trader.fetcher.get_current_price = Mock(return_value=50000)
        testnet_trader._get_portfolio_value = Mock(return_value=100000)
        testnet_trader._calculate_atr = Mock(return_value=100)
        testnet_trader._calculate_baseline_atr = Mock(return_value=100)

        testnet_trader._trading_iteration()

        # No position should be opened
        assert len(testnet_trader.open_positions) == 0

    def test_testnet_trader_empty_signals(self, testnet_trader):
        """Test trader handles empty signals gracefully."""
        testnet_trader.strategy.generate_signals = Mock(return_value=[])
        testnet_trader.fetcher.fetch_ohlcv = Mock(return_value=Mock())

        # Should not raise
        testnet_trader._trading_iteration()


class TestHyperliquidTrader:
    """Tests for mainnet trader."""

    @pytest.fixture
    def mainnet_config(self):
        """Create mainnet config."""
        return HyperliquidConfig(
            network='mainnet',
            private_key='0x' + '0' * 64
        )

    @pytest.fixture
    def mock_strategy(self):
        """Create mock strategy."""
        strategy = Mock(spec=LiquiditySweepStrategy)
        strategy.name = 'LiquiditySweep'
        return strategy

    def test_mainnet_trader_requires_confirmation(self, mainnet_config, mock_strategy):
        """Test mainnet trader requires confirmation."""
        # Mock confirm=False and provide 'CANCEL' instead of 'CONFIRM'
        with patch('eth_account.Account'):
            with patch('hyperliquid.info.Info'):
                with patch('hyperliquid.exchange.Exchange'):
                    with patch('data.hyperliquid_fetcher.HyperliquidFetcher'):
                        with patch('builtins.input', return_value='CANCEL'):
                            with pytest.raises(RuntimeError, match="not confirmed"):
                                HyperliquidTrader(mainnet_config, mock_strategy)

    def test_mainnet_trader_accepts_confirm_flag(self, mainnet_config, mock_strategy):
        """Test mainnet trader initializes with confirm=True flag."""
        with patch('eth_account.Account'):
            with patch('hyperliquid.info.Info'):
                with patch('hyperliquid.exchange.Exchange'):
                    with patch('data.hyperliquid_fetcher.HyperliquidFetcher'):
                        # Should not raise
                        trader = HyperliquidTrader(
                            mainnet_config,
                            mock_strategy,
                            confirm=True
                        )
                        assert trader.config.network == 'mainnet'

    def test_mainnet_trader_requires_mainnet_network(self, mock_strategy):
        """Test mainnet trader rejects testnet config."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64
        )

        with pytest.raises(ValueError, match="requires network='mainnet'"):
            with patch('builtins.input', return_value='CONFIRM'):
                HyperliquidTrader(config, mock_strategy)

    def test_mainnet_trader_circuit_breaker(self, mainnet_config, mock_strategy):
        """Test mainnet trader circuit breaker stops trading on drawdown."""
        with patch('eth_account.Account'):
            with patch('hyperliquid.info.Info'):
                with patch('hyperliquid.exchange.Exchange'):
                    with patch('data.hyperliquid_fetcher.HyperliquidFetcher'):
                        trader = HyperliquidTrader(
                            mainnet_config,
                            mock_strategy,
                            confirm=True
                        )
                        trader.wallet = Mock()
                        trader.wallet.address = '0xtest'

                        # Set starting balance
                        trader.starting_balance = 100000

                        # Mock portfolio to return 80% loss
                        trader._get_portfolio_value = Mock(return_value=20000)
                        trader.is_running = True

                        # Call trading iteration
                        trader._trading_iteration()

                        # Should have stopped due to circuit breaker
                        assert not trader.is_running


class TestLiveTradeIntegration:
    """Integration tests for live trading components."""

    def test_config_strategy_trader_compatibility(self):
        """Test config, strategy, and trader work together."""
        config = HyperliquidConfig(
            network='testnet',
            private_key='0x' + '0' * 64
        )
        config.validate()

        strategy = LiquiditySweepStrategy()
        assert strategy.name == 'liquidity_sweep'

        # Config should be compatible with TestnetTrader
        assert config.network == 'testnet'
        assert config.private_key.startswith('0x')

    def test_mainnet_trader_inheritance(self):
        """Test mainnet trader properly inherits testnet functionality."""
        # Both should have same interface
        assert hasattr(HyperliquidTrader, 'run')
        assert hasattr(HyperliquidTrader, 'stop')
        assert hasattr(HyperliquidTrader, '_trading_iteration')
        assert hasattr(HyperliquidTrader, '_place_order')
