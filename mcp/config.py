"""
MCP Server Configuration.

Configuration settings for the FractalTrader MCP server.
"""

import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_PATH = PROJECT_ROOT / "tests"
STRATEGIES_PATH = PROJECT_ROOT / "strategies"

# Server settings
SERVER_NAME = "fractal-trader"
SERVER_VERSION = "0.1.0"

# Tool defaults
DEFAULT_TEST_PATH = "tests/"
DEFAULT_BACKTEST_BARS = 500
AVAILABLE_STRATEGIES = ["liquidity_sweep", "fvg_fill", "bos_orderblock"]

# Docker settings
DOCKER_CONTAINER_NAME = "fractal-dev"
USE_DOCKER = os.getenv("USE_DOCKER", "true").lower() == "true"
