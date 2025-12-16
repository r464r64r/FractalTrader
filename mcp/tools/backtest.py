"""
Backtest Tool for MCP Server.

Executes backtests for FractalTrader strategies.
"""

import subprocess
from typing import Any

from mcp.config import (
    DEFAULT_BACKTEST_BARS,
    AVAILABLE_STRATEGIES,
    USE_DOCKER,
    DOCKER_CONTAINER_NAME
)


def run_backtest(
    strategy: str = "liquidity_sweep",
    bars: int = DEFAULT_BACKTEST_BARS
) -> dict[str, Any]:
    """
    Run backtest for a given strategy.

    Args:
        strategy: Strategy name ("liquidity_sweep", "fvg_fill", "bos_orderblock")
        bars: Number of bars for synthetic data (default: 500)

    Returns:
        Dictionary containing:
            - total_return: float - Total return percentage
            - sharpe_ratio: float - Sharpe ratio
            - max_drawdown: float - Maximum drawdown percentage
            - total_trades: int - Number of trades executed
            - win_rate: float - Win rate percentage (optional)
            - error: str - Error message if failed (optional)
    """
    if strategy not in AVAILABLE_STRATEGIES:
        return {
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "total_trades": 0,
            "error": f"Invalid strategy. Choose from: {', '.join(AVAILABLE_STRATEGIES)}"
        }

    # Map strategy name to class name
    strategy_map = {
        "liquidity_sweep": "LiquiditySweepStrategy",
        "fvg_fill": "FVGFillStrategy",
        "bos_orderblock": "BOSOrderBlockStrategy"
    }

    strategy_class = strategy_map[strategy]
    strategy_module = f"strategies.{strategy}"

    # Python code to execute backtest
    backtest_code = f"""
from {strategy_module} import {strategy_class}
from backtesting.runner import BacktestRunner
import pandas as pd
import numpy as np
import json

try:
    # Generate synthetic data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods={bars}, freq='1h')
    trend = np.linspace(100, 150, {bars})
    noise = np.random.randn({bars}) * 3
    close = trend + noise

    data = pd.DataFrame({{
        'open': close - np.random.rand({bars}),
        'high': close + np.random.rand({bars}) * 3,
        'low': close - np.random.rand({bars}) * 3,
        'close': close,
        'volume': np.random.randint(1000, 10000, {bars})
    }}, index=dates)

    # Run backtest
    strategy = {strategy_class}()
    runner = BacktestRunner(initial_cash=10000)
    result = runner.run(data, strategy)

    # Output as JSON
    output = {{
        'total_return': float(result.total_return),
        'sharpe_ratio': float(result.sharpe_ratio),
        'max_drawdown': float(result.max_drawdown),
        'total_trades': int(result.total_trades),
        'win_rate': float(result.win_rate) if hasattr(result, 'win_rate') else 0.0
    }}
    print('__MCP_RESULT__')
    print(json.dumps(output))

except Exception as e:
    output = {{
        'total_return': 0.0,
        'sharpe_ratio': 0.0,
        'max_drawdown': 0.0,
        'total_trades': 0,
        'error': str(e)
    }}
    print('__MCP_RESULT__')
    print(json.dumps(output))
"""

    try:
        if USE_DOCKER:
            cmd = [
                "docker", "exec", DOCKER_CONTAINER_NAME,
                "python", "-c", backtest_code
            ]
        else:
            cmd = ["python", "-c", backtest_code]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180
        )

        output = result.stdout + result.stderr

        # Extract JSON result
        if "__MCP_RESULT__" in output:
            json_str = output.split("__MCP_RESULT__")[1].strip()
            import json
            return json.loads(json_str)
        else:
            return {
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "total_trades": 0,
                "error": f"Failed to parse backtest output:\n{output}"
            }

    except subprocess.TimeoutExpired:
        return {
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "total_trades": 0,
            "error": "Backtest execution timed out after 180 seconds"
        }
    except Exception as e:
        return {
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "total_trades": 0,
            "error": f"Error running backtest: {str(e)}"
        }


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_run_backtest_liquidity_sweep
# [ ] test_run_backtest_fvg_fill
# [ ] test_run_backtest_bos_orderblock
# [ ] test_run_backtest_invalid_strategy
# [ ] test_run_backtest_timeout
# =============================================================================
