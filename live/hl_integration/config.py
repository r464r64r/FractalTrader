"""Configuration for Hyperliquid trading."""

from dataclasses import dataclass, field
from typing import Literal, Optional
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class HyperliquidConfig:
    """Hyperliquid trading configuration."""

    # Network
    network: Literal['testnet', 'mainnet'] = 'testnet'
    private_key: Optional[str] = None  # Ethereum private key

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
