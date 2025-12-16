"""
Signal Generation Tool for MCP Server.

Generates trading signals for FractalTrader strategies.
"""

import subprocess
from typing import Any

from mcp.config import (
    DEFAULT_BACKTEST_BARS,
    AVAILABLE_STRATEGIES,
    USE_DOCKER,
    DOCKER_CONTAINER_NAME
)


def generate_signals(
    strategy: str = "liquidity_sweep",
    bars: int = DEFAULT_BACKTEST_BARS
) -> dict[str, Any]:
    """
    Generate trading signals for a given strategy.

    Args:
        strategy: Strategy name ("liquidity_sweep", "fvg_fill", "bos_orderblock")
        bars: Number of bars for synthetic data (default: 500)

    Returns:
        Dictionary containing:
            - signals: list of signal dictionaries with:
                - timestamp: str - ISO format timestamp
                - direction: str - "long" or "short"
                - entry: float - Entry price
                - stop_loss: float - Stop loss price
                - take_profit: float - Take profit price
                - confidence: int - Confidence score (0-100)
            - error: str - Error message if failed (optional)
    """
    if strategy not in AVAILABLE_STRATEGIES:
        return {
            "signals": [],
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

    # Python code to generate signals
    signal_code = f"""
from {strategy_module} import {strategy_class}
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

    # Generate signals
    strategy = {strategy_class}()
    signals_series = strategy.generate_signals(
        high=data['high'],
        low=data['low'],
        close=data['close']
    )

    # Extract signals
    signal_list = []
    for idx, signal in signals_series.items():
        if signal is not None and hasattr(signal, 'direction'):
            signal_dict = {{
                'timestamp': idx.isoformat(),
                'direction': signal.direction,
                'entry': float(signal.entry),
                'stop_loss': float(signal.stop_loss),
                'take_profit': float(signal.take_profit),
                'confidence': int(signal.confidence)
            }}
            signal_list.append(signal_dict)

    output = {{'signals': signal_list}}
    print('__MCP_RESULT__')
    print(json.dumps(output))

except Exception as e:
    output = {{
        'signals': [],
        'error': str(e)
    }}
    print('__MCP_RESULT__')
    print(json.dumps(output))
"""

    try:
        if USE_DOCKER:
            cmd = [
                "docker", "exec", DOCKER_CONTAINER_NAME,
                "python", "-c", signal_code
            ]
        else:
            cmd = ["python", "-c", signal_code]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        output = result.stdout + result.stderr

        # Extract JSON result
        if "__MCP_RESULT__" in output:
            json_str = output.split("__MCP_RESULT__")[1].strip()
            import json
            return json.loads(json_str)
        else:
            return {
                "signals": [],
                "error": f"Failed to parse signal output:\n{output}"
            }

    except subprocess.TimeoutExpired:
        return {
            "signals": [],
            "error": "Signal generation timed out after 120 seconds"
        }
    except Exception as e:
        return {
            "signals": [],
            "error": f"Error generating signals: {str(e)}"
        }


# =============================================================================
# TEST REQUIREMENTS
# =============================================================================
# [ ] test_generate_signals_liquidity_sweep
# [ ] test_generate_signals_fvg_fill
# [ ] test_generate_signals_bos_orderblock
# [ ] test_generate_signals_invalid_strategy
# [ ] test_generate_signals_timeout
# [ ] test_generate_signals_empty_result
# =============================================================================
