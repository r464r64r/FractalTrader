"""
FractalTrader MCP Server.

Model Context Protocol server for Claude Code integration with
FractalTrader algorithmic trading system.
"""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from fractal_mcp.config import AVAILABLE_STRATEGIES, SERVER_NAME, SERVER_VERSION
from fractal_mcp.tools.backtest import run_backtest
from fractal_mcp.tools.signals import generate_signals
from fractal_mcp.tools.test_runner import run_tests

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Initialize MCP server
app = Server(SERVER_NAME)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools for the MCP server.

    Returns:
        List of Tool objects describing available functionality
    """
    return [
        Tool(
            name="run_tests",
            description=(
                "Run pytest tests for FractalTrader. "
                "Returns pass/fail status, test counts, and full output."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "test_path": {
                        "type": "string",
                        "description": "Path to tests (default: 'tests/')",
                        "default": "tests/",
                    }
                },
            },
        ),
        Tool(
            name="run_backtest",
            description=(
                "Run backtest for a FractalTrader strategy. "
                "Returns performance metrics: total return, Sharpe ratio, "
                "max drawdown, and trade count."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "strategy": {
                        "type": "string",
                        "description": f"Strategy name: {', '.join(AVAILABLE_STRATEGIES)}",
                        "enum": AVAILABLE_STRATEGIES,
                        "default": "liquidity_sweep",
                    },
                    "bars": {
                        "type": "integer",
                        "description": "Number of bars for synthetic data (default: 500)",
                        "default": 500,
                        "minimum": 100,
                        "maximum": 10000,
                    },
                },
            },
        ),
        Tool(
            name="generate_signals",
            description=(
                "Generate trading signals for a FractalTrader strategy. "
                "Returns list of signals with entry, stop loss, take profit, "
                "and confidence scores."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "strategy": {
                        "type": "string",
                        "description": f"Strategy name: {', '.join(AVAILABLE_STRATEGIES)}",
                        "enum": AVAILABLE_STRATEGIES,
                        "default": "liquidity_sweep",
                    },
                    "bars": {
                        "type": "integer",
                        "description": "Number of bars for synthetic data (default: 500)",
                        "default": 500,
                        "minimum": 100,
                        "maximum": 10000,
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Execute a tool by name with given arguments.

    Args:
        name: Tool name to execute
        arguments: Dictionary of arguments for the tool

    Returns:
        List containing TextContent with the tool result

    Raises:
        ValueError: If tool name is not recognized
    """
    try:
        if name == "run_tests":
            test_path = arguments.get("test_path", "tests/")
            logger.info(f"Running tests: {test_path}")
            result = run_tests(test_path)

        elif name == "run_backtest":
            strategy = arguments.get("strategy", "liquidity_sweep")
            bars = arguments.get("bars", 500)
            logger.info(f"Running backtest: {strategy} with {bars} bars")
            result = run_backtest(strategy, bars)

        elif name == "generate_signals":
            strategy = arguments.get("strategy", "liquidity_sweep")
            bars = arguments.get("bars", 500)
            logger.info(f"Generating signals: {strategy} with {bars} bars")
            result = generate_signals(strategy, bars)

        else:
            raise ValueError(f"Unknown tool: {name}")

        # Format result as JSON string
        import json

        result_text = json.dumps(result, indent=2)

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        error_result = {"error": str(e), "tool": name}
        import json

        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def main() -> None:
    """
    Main entry point for the MCP server.

    Starts the server using stdio transport for Claude Code integration.
    """
    logger.info(f"Starting {SERVER_NAME} MCP server v{SERVER_VERSION}")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())


# =============================================================================
# USAGE
# =============================================================================
# Start the server:
#   python -m mcp.server
#
# Available tools:
#   - run_tests: Execute pytest tests
#   - run_backtest: Run strategy backtest
#   - generate_signals: Generate trading signals
#
# For Claude Code integration, add to MCP settings:
#   {
#     "mcpServers": {
#       "fractal-trader": {
#         "command": "python",
#         "args": ["-m", "fractal_mcp.server"],
#         "cwd": "/path/to/FractalTrader"
#       }
#     }
#   }
# =============================================================================
