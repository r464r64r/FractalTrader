"""Example: Live trading on Hyperliquid testnet."""

import logging

from live.hl_integration.config import HyperliquidConfig
from live.hl_integration.testnet import HyperliquidTestnetTrader
from strategies.liquidity_sweep import LiquiditySweepStrategy

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    """Run testnet paper trading example."""

    # Load configuration from .env file
    config = HyperliquidConfig.from_env(network="testnet")

    # Choose strategy
    strategy = LiquiditySweepStrategy()

    # Create testnet trader
    trader = HyperliquidTestnetTrader(config, strategy)

    # Run for 1 hour (testing)
    # For production: trader.run()  # Runs indefinitely
    print("Starting testnet paper trading for 1 hour...")
    trader.run(duration_seconds=3600)


if __name__ == "__main__":
    main()
