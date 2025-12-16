# FractalTrader MCP Server

Model Context Protocol (MCP) server for Claude Code integration with the FractalTrader algorithmic trading system.

## Overview

This MCP server enables Claude Code to interact with FractalTrader by providing three core tools:

1. **run_tests** - Execute pytest test suite
2. **run_backtest** - Run strategy backtests with performance metrics
3. **generate_signals** - Generate trading signals for analysis

## Installation

### Prerequisites

- Python 3.11+
- Docker (for containerized execution)
- FractalTrader project installed

### Setup

1. Install MCP dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Docker container is running:
```bash
docker ps | grep fractal-dev
```

If not running, start it:
```bash
./docker-start.sh shell
```

## Usage

### Starting the Server

Run the MCP server directly:
```bash
python -m fractal_mcp.server
```

The server uses stdio transport for communication with Claude Code.

### Claude Code Integration

Add to your Claude Code MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "fractal-trader": {
      "command": "python",
      "args": ["-m", "mcp.server"],
      "cwd": "/path/to/FractalTrader"
    }
  }
}
```

Replace `/path/to/FractalTrader` with your actual project path.

## Available Tools

### 1. run_tests

Execute the pytest test suite.

**Parameters:**
- `test_path` (string, optional): Path to tests (default: "tests/")

**Returns:**
```json
{
  "passed": true,
  "total": 37,
  "failed": 0,
  "output": "pytest output..."
}
```

**Example Usage:**
```
Run all tests
> Use run_tests tool with test_path="tests/"

Run specific test module
> Use run_tests tool with test_path="tests/test_liquidity.py"
```

### 2. run_backtest

Run a backtest for a FractalTrader strategy.

**Parameters:**
- `strategy` (string): One of "liquidity_sweep", "fvg_fill", "bos_orderblock"
- `bars` (integer, optional): Number of bars for synthetic data (default: 500, range: 100-10000)

**Returns:**
```json
{
  "total_return": 0.1523,
  "sharpe_ratio": 1.87,
  "max_drawdown": -0.0842,
  "total_trades": 23,
  "win_rate": 0.6087
}
```

**Example Usage:**
```
Backtest liquidity sweep strategy
> Use run_backtest tool with strategy="liquidity_sweep", bars=500

Backtest FVG fill strategy with more data
> Use run_backtest tool with strategy="fvg_fill", bars=1000
```

### 3. generate_signals

Generate trading signals for a strategy.

**Parameters:**
- `strategy` (string): One of "liquidity_sweep", "fvg_fill", "bos_orderblock"
- `bars` (integer, optional): Number of bars for synthetic data (default: 500, range: 100-10000)

**Returns:**
```json
{
  "signals": [
    {
      "timestamp": "2024-01-15T10:00:00",
      "direction": "long",
      "entry": 125.34,
      "stop_loss": 123.12,
      "take_profit": 129.78,
      "confidence": 85
    }
  ]
}
```

**Example Usage:**
```
Generate signals for liquidity sweep
> Use generate_signals tool with strategy="liquidity_sweep"

Generate signals for order block strategy
> Use generate_signals tool with strategy="bos_orderblock", bars=1000
```

## Configuration

### Environment Variables

- `USE_DOCKER` (default: "true"): Set to "false" to run commands locally instead of in Docker
- `DOCKER_CONTAINER_NAME` (default: "fractal-dev"): Name of Docker container to execute commands in

### Docker vs Local Execution

By default, the MCP server executes commands inside the `fractal-dev` Docker container. To run locally:

```bash
export USE_DOCKER=false
python -m fractal_mcp.server
```

## Architecture

```
mcp/
├── __init__.py          # Package initialization
├── server.py            # Main MCP server (stdio transport)
├── config.py            # Configuration settings
├── tools/
│   ├── __init__.py
│   ├── test_runner.py   # pytest execution tool
│   ├── backtest.py      # Backtest execution tool
│   └── signals.py       # Signal generation tool
└── README.md            # This file
```

## Error Handling

All tools return errors in a consistent format:

```json
{
  "error": "Error message here",
  ...other fields (may be empty/zero)
}
```

Common errors:
- **Invalid strategy**: Strategy name not in ["liquidity_sweep", "fvg_fill", "bos_orderblock"]
- **Timeout**: Command execution exceeded time limit (120-180s)
- **Docker not running**: Container "fractal-dev" not found
- **Parse error**: Failed to parse tool output

## Development

### Adding New Tools

1. Create tool function in `mcp/tools/`
2. Register tool in `mcp/server.py`:
   - Add to `list_tools()`
   - Add handler in `call_tool()`

### Testing Tools Locally

Test tools without MCP:

```python
from mcp.tools.test_runner import run_tests
from mcp.tools.backtest import run_backtest
from mcp.tools.signals import generate_signals

# Run tests
result = run_tests("tests/")
print(result)

# Run backtest
result = run_backtest("liquidity_sweep", 500)
print(result)

# Generate signals
result = generate_signals("fvg_fill", 500)
print(result)
```

## Troubleshooting

### Server won't start

Check dependencies:
```bash
pip list | grep mcp
```

Verify Python version:
```bash
python --version  # Should be 3.11+
```

### Docker commands fail

Verify container is running:
```bash
docker ps | grep fractal-dev
```

Start container if needed:
```bash
./docker-start.sh shell
```

### Commands timeout

Increase timeout in tool files:
- `test_runner.py`: `timeout=120`
- `backtest.py`: `timeout=180`
- `signals.py`: `timeout=120`

## License

Same as FractalTrader project.

## Support

For issues related to:
- **MCP server**: Check logs in console where server is running
- **FractalTrader**: See main project README and CLAUDE.md
- **Claude Code integration**: Refer to Claude Code documentation
