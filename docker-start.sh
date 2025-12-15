#!/bin/bash
# Fractal Trader - Docker Quick Start
# Usage: ./docker-start.sh [command]
#   ./docker-start.sh          - Start interactive shell
#   ./docker-start.sh test     - Run all tests
#   ./docker-start.sh backtest - Run example backtest

set -e

IMAGE_NAME="fractal-trader"
CONTAINER_NAME="fractal-dev"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Fractal Trader Docker Environment${NC}"

# Build if needed
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo -e "${YELLOW}Building image (first time, ~5 min)...${NC}"
    docker build -t $IMAGE_NAME .
fi

case "${1:-shell}" in
    shell)
        echo -e "${GREEN}Starting interactive shell...${NC}"
        docker run -it --rm \
            -v "$(pwd):/app" \
            --name $CONTAINER_NAME \
            $IMAGE_NAME \
            bash
        ;;
    test)
        echo -e "${GREEN}Running tests...${NC}"
        docker run --rm \
            -v "$(pwd):/app" \
            $IMAGE_NAME \
            python -m pytest tests/ -v --tb=short
        ;;
    backtest)
        echo -e "${GREEN}Running example backtest...${NC}"
        docker run --rm \
            -v "$(pwd):/app" \
            $IMAGE_NAME \
            python -c "
from strategies.liquidity_sweep import LiquiditySweepStrategy
from backtesting.runner import BacktestRunner
import pandas as pd
import numpy as np

# Generate test data
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=500, freq='1h')
trend = np.linspace(100, 150, 500)
noise = np.random.randn(500) * 3
close = trend + noise

data = pd.DataFrame({
    'open': close - np.random.rand(500),
    'high': close + np.random.rand(500) * 3,
    'low': close - np.random.rand(500) * 3,
    'close': close,
    'volume': np.random.randint(1000, 10000, 500)
}, index=dates)

# Run backtest
strategy = LiquiditySweepStrategy()
runner = BacktestRunner(initial_cash=10000)
result = runner.run(data, strategy)

print(f'''
=== BACKTEST RESULTS ===
Total Return: {result.total_return:.2%}
Sharpe Ratio: {result.sharpe_ratio:.2f}
Max Drawdown: {result.max_drawdown:.2%}
Win Rate:     {result.win_rate:.2%}
Total Trades: {result.total_trades}
''')
"
        ;;
    *)
        echo "Usage: $0 [shell|test|backtest]"
        exit 1
        ;;
esac
