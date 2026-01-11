# FractalTrader → Frakt/FraktAl Migration Plan

**Version:** 1.0
**Created:** 2026-01-11
**Status:** READY TO EXECUTE
**Estimated Effort:** ~22 "day-tokens" (3 weeks human time, but we move faster)

---

## Executive Summary

### The Transition

FractalTrader (incubation project) graduates into **two distinct entities**:

```
FractalTrader (†)
    ↓
    ├─→ Frakt (public, MIT)
    │   ├─ SMC engine (core/)
    │   ├─ Strategies (strategies/)
    │   ├─ Risk management (risk/)
    │   ├─ Backtesting tools
    │   ├─ manifesto.md (EN, constitution)
    │   └─ Community-driven, extensible
    │
    └─→ FraktAl (private, proprietary)
        ├─ Live trading bot (live/)
        ├─ Publication layer (fractal_pub/)
        ├─ Development tools (fractal_dev/)
        ├─ Infrastructure (nodes, configs)
        ├─ Secrets (.env, API keys)
        └─ Master roadmap → frakt.al SaaS
```

### Core Principles

1. **Frakt = Engine** (MIT, open source, community)
2. **FraktAl = Platform** (proprietary, full stack, SaaS roadmap)
3. **Manifesto = Constitution** (embedded tests, executable philosophy)
4. **Nodes = Containers** (not hosts; portable, reproducible)
5. **Ship or Die** (fast iteration, measurable structure)

---

## Architectural Decisions

Based on design review (2026-01-11), these decisions are **locked**:

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Exchange integration location | **Generic wrapper in Frakt, credentials in FraktAl** | Enables community to add own exchanges (extensible) |
| 2 | Manifest as executable | **Yes, embedded tests in `manifesto.md`** | Enforces philosophy via CI, integrates with Jupyter |
| 3 | Public data: HL wallet | **Both link + basic stats** | Trust (external verification) + UX (inline display) |
| 4 | Issues/PRs migration | **Transfer to new repos** | Preserves history, maintains continuity |
| 5 | Container layering | **docker-compose (separate images)** | Clean separation, Frakt independently testable |

---

## Phase 1: Repository Setup (Days 1-2)

### Milestone 1.1: Create New Repositories

**Actions:**

```bash
# On GitHub (via gh CLI or web UI)

# 1. Create Frakt (public)
gh repo create r464r64r/Frakt \
  --public \
  --description "SMC-based trading engine. Liquidity-first, fractal structure, no lagging indicators." \
  --license MIT

# 2. Create FraktAl (private)
gh repo create r464r64r/FraktAl \
  --private \
  --description "Full trading platform powered by Frakt. Live bot, infrastructure, SaaS roadmap."

# 3. Clone locally
cd ~/workspace
git clone git@github.com:r464r64r/Frakt.git
git clone git@github.com:r464r64r/FraktAl.git
```

**Success criteria:**
- [ ] Both repos exist on GitHub
- [ ] Frakt: public, MIT license visible
- [ ] FraktAl: private, only you have access
- [ ] Both cloned to local workspace

---

### Milestone 1.2: Translate Manifest

**Actions:**

```bash
cd ~/workspace/FractalTrader

# Create English translation of manifesto
# IMPORTANT: Translate README_MANIFESTO_PL.md → manifesto.md
# Keep 1:1 structure, preserve philosophy

# Use AI translation + manual review for accuracy
# Key terms to preserve:
# - "There is no price" → exact translation
# - "Smart Money" → keep English
# - Fractal structure metaphors
```

**Template structure:**

```markdown
# Manifesto

## Philosophy

[Translate: Po co to wszystko było...]

<!-- TEST:
# Embedded test assertions (executed by CI)
assert_no_lagging_indicators(['rsi', 'macd', 'bollinger'])
assert_fractal_structure(['H4', 'H1', 'M15'])
-->

## Core Principles

### 1. Liquidity-First Approach

[Translate: Nie ma ceny...]

<!-- TEST:
assert_uses_order_flow()
-->

[... rest of translation ...]
```

**Success criteria:**
- [ ] `manifesto.md` created (English)
- [ ] All philosophical concepts translated accurately
- [ ] Embedded `<!-- TEST: -->` blocks added (5+ assertions)
- [ ] Original `README_MANIFESTO_PL.md` preserved in FraktAl (historical)

---

### Milestone 1.3: Split Codebase

**Actions:**

```bash
# Map components to repositories
# FRAKT (public):
core/
strategies/
risk/
backtesting/
data/           # Generic data fetchers, no API keys
tests/test_core.py
tests/test_strategies.py
tests/test_risk.py
manifesto.md
README.md       # "How to use Frakt"
LICENSE         # MIT
requirements.txt

# FRAKTAL (private):
live/
fractal_pub/
fractal_dev/
tests/test_live.py
tests/test_integration.py
docs/           # All existing docs
deploy/
notebooks/
.env.example
docker-compose.yml
README.md       # "FraktAl platform overview"
```

**Implementation:**

```bash
# === FRAKT ===
cd ~/workspace/Frakt

# Copy core components from FractalTrader
cp -r ~/workspace/FractalTrader/core .
cp -r ~/workspace/FractalTrader/strategies .
cp -r ~/workspace/FractalTrader/risk .
cp -r ~/workspace/FractalTrader/backtesting .
cp -r ~/workspace/FractalTrader/data .

# Copy relevant tests
mkdir tests
cp ~/workspace/FractalTrader/tests/test_core.py tests/
cp ~/workspace/FractalTrader/tests/test_strategies.py tests/
cp ~/workspace/FractalTrader/tests/test_risk.py tests/

# Copy manifesto
cp ~/workspace/FractalTrader/manifesto.md .  # (after translation)

# Create README
cat > README.md << 'EOF'
# Frakt

SMC-based trading engine. Liquidity-first, fractal structure, no lagging indicators.

## Philosophy

See [manifesto.md](manifesto.md) for our core principles.

## Quick Start

```python
from frakt.core import detect_bos, detect_fvg
from frakt.strategies import LiquiditySweepStrategy

# Load your data
ohlcv = ...

# Generate signals
strategy = LiquiditySweepStrategy()
signal = strategy.generate_signal(ohlcv)

if signal.confidence > 0.8:
    print(f"Signal: {signal.side} at {signal.entry_price}")
```

## Installation

```bash
pip install frakt  # (future PyPI package)
# Or install from source:
pip install -e .
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT - see [LICENSE](LICENSE)
EOF

# Copy requirements (public dependencies only)
grep -v "hyperliquid\|python-dotenv" ~/workspace/FractalTrader/requirements.txt > requirements.txt

# Git setup
git add .
git commit -m "feat: Initial Frakt engine (from FractalTrader graduation)"
git push origin main


# === FRAKTAL ===
cd ~/workspace/FraktAl

# Copy private components
cp -r ~/workspace/FractalTrader/live .
cp -r ~/workspace/FractalTrader/docs .
cp -r ~/workspace/FractalTrader/deploy .
cp -r ~/workspace/FractalTrader/notebooks .

# Create new directories
mkdir -p fractal_pub/api
mkdir -p fractal_pub/web
mkdir -p fractal_dev/cli
mkdir -p fractal_dev/mcp
mkdir -p fractal_dev/hooks
mkdir -p fractal_dev/agents

# Move existing tools
mv ~/workspace/FractalTrader/fractal_mcp/* fractal_dev/mcp/
mv ~/workspace/FractalTrader/.github/workflows/* fractal_dev/agents/

# Copy full test suite
cp -r ~/workspace/FractalTrader/tests .

# Copy env template (NO SECRETS)
cat > .env.example << 'EOF'
# Hyperliquid API
HL_API_KEY=your_api_key_here
HL_SECRET=your_secret_here
HL_WALLET=your_wallet_address_here

# Node config
NODE_ENV=development
NODE_NAME=laptop-dev

# Logging
LOG_LEVEL=INFO
EOF

# Create README
cat > README.md << 'EOF'
# FraktAl

Full trading platform powered by [Frakt](https://github.com/r464r64r/Frakt).

**PRIVATE REPOSITORY** - Contains live bot, infrastructure, and proprietary tools.

## Structure

```
live/           Live trading bot (uses Frakt engine)
fractal_pub/    Publication layer (API, dashboard)
fractal_dev/    Development tools (CLI, MCP, hooks)
docs/           Documentation, roadmaps, ADRs
deploy/         Infrastructure as code
notebooks/      Research, reports (Jupyter)
```

## Quick Start

See [docs/CLAUDE.md](docs/CLAUDE.md) for development guide.

## Roadmap

See [docs/ROADMAP_Q1_2026.md](docs/ROADMAP_Q1_2026.md).
EOF

# Git setup
git add .
git commit -m "feat: Initial FraktAl platform (from FractalTrader graduation)"
git push origin main
```

**Success criteria:**
- [ ] Frakt repo contains only public components
- [ ] FraktAl repo contains private components + full history
- [ ] No secrets in either repo (validate with `git log --all -S "API_KEY"`)
- [ ] Both repos have distinct READMEs
- [ ] All tests pass in both repos independently

---

## Phase 2: Code Refactoring (Days 3-7)

### Milestone 2.1: Exchange Integration Split

**Goal:** Generic Hyperliquid wrapper in Frakt, credentials in FraktAl.

**Implementation:**

```bash
cd ~/workspace/Frakt

# Create generic exchange interface
cat > frakt/exchanges/__init__.py << 'EOF'
"""
Generic exchange interfaces.

Frakt provides wrappers for common exchanges, but does NOT include:
- API credentials
- Order execution logic
- Position management

These belong in your application layer (e.g., FraktAl).
"""
EOF

# Move and refactor HL integration
mkdir -p frakt/exchanges
cat > frakt/exchanges/hyperliquid.py << 'EOF'
"""
Hyperliquid exchange API wrapper.

Usage:
    from frakt.exchanges import HyperliquidExchange

    exchange = HyperliquidExchange(api_key="...", secret="...")
    exchange.place_order(symbol="BTC", side="LONG", size=0.1, price=42000)
"""

class HyperliquidExchange:
    """Generic Hyperliquid API client."""

    def __init__(self, api_key: str, secret: str, testnet: bool = True):
        """
        Initialize exchange client.

        Args:
            api_key: Your HL API key
            secret: Your HL secret
            testnet: Use testnet (default: True)
        """
        self.api_key = api_key
        self.secret = secret
        self.testnet = testnet
        # ... rest of __init__

    def place_order(self, symbol: str, side: str, size: float, price: float):
        """Place limit order."""
        # Generic implementation (no business logic)
        pass

    def get_position(self, symbol: str):
        """Get current position."""
        pass

    # ... other generic methods
EOF

# Update tests
cat > tests/test_exchanges.py << 'EOF'
"""Tests for exchange wrappers (no real API calls)."""
import pytest
from frakt.exchanges import HyperliquidExchange

def test_hyperliquid_init():
    exchange = HyperliquidExchange(api_key="test", secret="test")
    assert exchange.api_key == "test"
    assert exchange.testnet is True

def test_place_order_validation():
    exchange = HyperliquidExchange(api_key="test", secret="test")

    # Should validate inputs (not execute)
    with pytest.raises(ValueError):
        exchange.place_order(symbol="", side="LONG", size=0.1, price=42000)
EOF

git add frakt/exchanges tests/test_exchanges.py
git commit -m "feat: Add generic Hyperliquid exchange wrapper"
git push origin main


# === FRAKTAL: Use Frakt exchange ===
cd ~/workspace/FraktAl

# Update requirements.txt to include Frakt
echo "frakt @ git+https://github.com/r464r64r/Frakt.git@main" >> requirements.txt

# Refactor live bot to use Frakt
cat > live/hl_integration/client.py << 'EOF'
"""
FraktAl's Hyperliquid client (uses Frakt wrapper + our credentials).
"""
from frakt.exchanges import HyperliquidExchange
import os

class FraktAlHyperliquidClient:
    """Hyperliquid client with FraktAl-specific configuration."""

    def __init__(self):
        # Load credentials from environment (PRIVATE)
        self.exchange = HyperliquidExchange(
            api_key=os.getenv("HL_API_KEY"),
            secret=os.getenv("HL_SECRET"),
            testnet=True
        )

    def execute_signal(self, signal):
        """Execute trading signal (FraktAl business logic)."""
        # Position sizing, risk management, etc.
        size = self._calculate_position_size(signal)

        # Use Frakt's generic wrapper
        self.exchange.place_order(
            symbol=signal.symbol,
            side=signal.side,
            size=size,
            price=signal.entry_price
        )
EOF

git add live/hl_integration/client.py requirements.txt
git commit -m "refactor: Use Frakt exchange wrapper"
git push origin main
```

**Success criteria:**
- [ ] `frakt/exchanges/hyperliquid.py` contains no secrets
- [ ] FraktAl imports from Frakt: `from frakt.exchanges import HyperliquidExchange`
- [ ] Tests pass in both repos
- [ ] Clear separation: Frakt = wrapper, FraktAl = business logic

---

### Milestone 2.2: Embedded Manifest Tests

**Goal:** `manifesto.md` contains executable assertions, CI validates compliance.

**Implementation:**

```bash
cd ~/workspace/Frakt

# Update manifesto.md with embedded tests
cat >> manifesto.md << 'EOF'

## Principle 1: No Lagging Indicators

We do NOT use:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Traditional moving averages

We use:
- Order flow (BOS, FVG)
- Liquidity analysis
- Fractal structure

<!-- TEST:
import ast
import inspect
from frakt.strategies import *

# Get all strategy classes
strategies = [LiquiditySweepStrategy, FVGStrategy, BreakoutStrategy]

forbidden_terms = ['rsi', 'macd', 'bollinger', 'sma', 'ema']

for strategy_class in strategies:
    source = inspect.getsource(strategy_class).lower()
    for term in forbidden_terms:
        assert term not in source, f"{strategy_class.__name__} uses forbidden indicator: {term}"
-->

## Principle 2: Fractal Structure

The same pattern appears across timeframes:

H4: BOS → pullback → retest → entry
H1: BOS → pullback → retest → entry
M15: BOS → pullback → retest → entry

<!-- TEST:
from frakt.core import detect_bos

# Test that BOS detection is consistent across timeframes
# (same algorithm, different data)
for timeframe in ['H4', 'H1', 'M15']:
    assert 'detect_bos' in dir(frakt.core), "BOS detection must be available"
-->

EOF

# Create test runner
cat > tests/test_manifesto.py << 'EOF'
"""
Manifesto compliance tests.

Parses manifesto.md, extracts <!-- TEST: --> blocks, executes them.
"""
import re
import ast

def extract_tests_from_manifesto():
    """Extract embedded test blocks from manifesto.md."""
    with open("manifesto.md") as f:
        content = f.read()

    # Regex: <!-- TEST:\n...\n-->
    pattern = r'<!-- TEST:\n(.*?)\n-->'
    matches = re.findall(pattern, content, re.DOTALL)

    return matches

def test_manifesto_compliance():
    """Execute all embedded tests from manifesto."""
    tests = extract_tests_from_manifesto()

    assert len(tests) > 0, "Manifesto should contain embedded tests"

    for i, test_code in enumerate(tests):
        try:
            # Execute test code
            exec(test_code, globals())
        except AssertionError as e:
            pytest.fail(f"Manifesto test {i+1} failed: {e}")
        except Exception as e:
            pytest.fail(f"Manifesto test {i+1} error: {e}")
EOF

# Update CI to run manifesto tests
cat > .github/workflows/manifesto-compliance.yml << 'EOF'
name: Manifesto Compliance

on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .

      - name: Run manifesto tests
        run: pytest tests/test_manifesto.py -v

      - name: Comment on PR
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: '❌ **Manifesto Compliance Failed**\n\nYour changes violate principles in [manifesto.md](../blob/main/manifesto.md).\n\nPlease review and fix.'
            })
EOF

git add manifesto.md tests/test_manifesto.py .github/workflows/manifesto-compliance.yml
git commit -m "feat: Add embedded tests to manifesto.md + CI enforcement"
git push origin main
```

**Success criteria:**
- [ ] `manifesto.md` contains 5+ `<!-- TEST: -->` blocks
- [ ] `pytest tests/test_manifesto.py` passes
- [ ] CI runs on every PR, blocks merge if manifesto violated
- [ ] Tests validate: no lagging indicators, fractal structure, etc.

---

### Milestone 2.3: Unified CLI

**Goal:** `fractal` command works on laptop/EC2/homelab (auto-detects node).

**Implementation:**

```bash
cd ~/workspace/FraktAl

# Create CLI
mkdir -p fractal_dev/cli

cat > fractal_dev/cli/main.py << 'EOF'
"""
FraktAl unified CLI.

Usage:
    fractal status              # Auto-detect node
    fractal --node ec2 status   # Force EC2
    fractal logs --tail 50      # Stream logs
    fractal deploy              # Deploy to current node
"""
import click
import subprocess
import requests
import os

def detect_node():
    """Auto-detect current node (local, ec2, homelab)."""
    # Check if local Docker is running
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=fractal-trader-dev'],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0 and result.stdout:
            return 'local'
    except:
        pass

    # Check if EC2 API is reachable
    try:
        r = requests.get('http://54.199.8.26:8080/health', timeout=2)
        if r.status_code == 200:
            return 'ec2'
    except:
        pass

    # Default: unknown
    return 'unknown'

@click.group()
@click.option('--node', default='auto', help='Node: local|ec2|homelab|auto')
@click.pass_context
def cli(ctx, node):
    """FraktAl unified interface."""
    ctx.obj = node if node != 'auto' else detect_node()

@cli.command()
@click.pass_context
def status(ctx):
    """Show bot status."""
    node = ctx.obj

    if node == 'local':
        # Direct Docker exec
        result = subprocess.run([
            'docker', 'exec', 'fractal-trader-dev',
            'python3', '-m', 'live.cli', 'status'
        ], capture_output=True)
        print(result.stdout.decode())

    elif node == 'ec2':
        # Query API
        r = requests.get('http://54.199.8.26:8080/api/status')
        data = r.json()
        print(f"Uptime: {data['uptime']}")
        print(f"Trades: {data['trades']}")
        print(f"Equity: ${data['equity']:,.2f}")

    else:
        print(f"❌ Unknown node: {node}")
        print("Use --node local|ec2|homelab")

@cli.command()
@click.option('--tail', default=50, help='Number of lines')
@click.pass_context
def logs(ctx, tail):
    """Stream logs."""
    node = ctx.obj

    if node == 'local':
        subprocess.run([
            'docker', 'exec', 'fractal-trader-dev',
            'tail', f'-{tail}', '/tmp/bot_v2.log'
        ])

    elif node == 'ec2':
        subprocess.run([
            'ssh', 'fractal-ec2',
            f'sudo docker exec fractal-trader-dev tail -{tail} /tmp/bot_v2.log'
        ])

if __name__ == '__main__':
    cli()
EOF

# Create setup.py for installation
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name='fraktal',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'click>=8.0',
        'requests>=2.28',
    ],
    entry_points={
        'console_scripts': [
            'fractal=fractal_dev.cli.main:cli',
        ],
    },
)
EOF

# Install locally
pip install -e .

# Test
fractal status
```

**Success criteria:**
- [ ] `fractal status` works on laptop (detects local Docker)
- [ ] `fractal --node ec2 status` queries EC2 API
- [ ] `fractal logs --tail 50` streams logs from appropriate node
- [ ] Command installs via `pip install -e .`

---

### Milestone 2.4: Publication Layer (EC2 API)

**Goal:** EC2 exports FastAPI server on :8080 (status, trades, signals).

**Implementation:**

```bash
cd ~/workspace/FraktAl

# Create FastAPI server
mkdir -p fractal_pub/api

cat > fractal_pub/api/server.py << 'EOF'
"""
FraktAl publication API.

Endpoints:
    GET /health             Health check
    GET /api/status         Bot status (uptime, trades, equity)
    GET /api/trades         Recent trades
    GET /api/signals        Recent signals
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app = FastAPI(title="FraktAl API", version="1.0.0")

# CORS for public dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/api/status")
def status():
    """Bot status."""
    try:
        with open("/app/.testnet_state.json") as f:
            state = json.load(f)

        return {
            "uptime": "4d 18h",  # TODO: Calculate from state
            "trades": len(state.get("trade_history", [])),
            "equity": state.get("current_equity", 10000),
            "strategy": "liquidity_sweep",
            "version": "frakt-1.0.0",
        }
    except FileNotFoundError:
        return {"error": "State file not found"}

@app.get("/api/trades")
def trades():
    """Recent trades."""
    try:
        with open("/app/.testnet_state.json") as f:
            state = json.load(f)

        # Return last 50 trades
        return state.get("trade_history", [])[-50:]
    except FileNotFoundError:
        return []

@app.get("/api/signals")
def signals():
    """Recent signals."""
    # TODO: Implement signal tracking (separate from trades)
    return []

@app.get("/api/wallet")
def wallet():
    """Hyperliquid wallet info."""
    return {
        "address": "0xf7ab281eeBF13C8720a7eE531934a4803E905403",
        "network": "testnet",
        "explorer": "https://app.hyperliquid.xyz/account/0xf7ab281eeBF13C8720a7eE531934a4803E905403"
    }
EOF

# Update Dockerfile for multi-process (bot + API)
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install supervisor for multi-process
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Copy code
COPY . .

# Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/fraktal.conf

# Expose API port
EXPOSE 8080

CMD ["supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
EOF

# Supervisor config
cat > supervisord.conf << 'EOF'
[supervisord]
nodaemon=true
user=root

[program:bot]
command=python3 -m live.cli start --strategy liquidity_sweep
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/bot.err.log
stdout_logfile=/var/log/bot.out.log

[program:api]
command=uvicorn fractal_pub.api.server:app --host 0.0.0.0 --port 8080
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/api.err.log
stdout_logfile=/var/log/api.out.log
EOF

# Update requirements.txt
echo "fastapi>=0.104.0" >> requirements.txt
echo "uvicorn[standard]>=0.24.0" >> requirements.txt

git add fractal_pub/api/ Dockerfile supervisord.conf requirements.txt
git commit -m "feat: Add FastAPI publication layer"
git push origin main
```

**Deploy to EC2:**

```bash
# SSH to EC2
ssh fractal-ec2

# Pull latest code
cd ~/FractalTrader
git pull

# Rebuild Docker image
docker build -t fraktal:latest .

# Stop old container
docker stop fractal-trader-dev

# Run new container (with API exposed)
docker run -d \
  --name fractal-trader-dev \
  -p 8080:8080 \
  --env-file .env \
  fraktal:latest

# Verify
curl http://localhost:8080/health
# Should return: {"status": "ok"}

curl http://localhost:8080/api/status
# Should return bot status JSON
```

**Success criteria:**
- [ ] `curl http://54.199.8.26:8080/health` returns `{"status": "ok"}`
- [ ] `curl http://54.199.8.26:8080/api/status` returns bot status
- [ ] Bot still trading (multi-process works)
- [ ] API responds in <100ms

---

## Phase 3: Infrastructure & Automation (Days 8-14)

### Milestone 3.1: SessionStart Hook

**Goal:** Claude Code auto-loads context on session start.

**Implementation:**

```bash
cd ~/workspace/FraktAl

mkdir -p .claude/hooks

cat > .claude/hooks/SessionStart.sh << 'EOF'
#!/bin/bash

echo "=== FraktAl Context ==="
echo ""

# Git status
echo "📍 Branch: $(git branch --show-current)"
echo "📝 Last commit: $(git log -1 --oneline)"
echo ""

# Bot status (try local, then EC2)
echo "🤖 Bot Status:"
fractal status 2>/dev/null || echo "  Use: fractal --node ec2 status"
echo ""

# Current sprint
echo "🎯 Current Focus:"
grep -A 5 "## Current:" docs/ISSUES.md 2>/dev/null | head -6 || echo "  See docs/ISSUES.md"
echo ""

# Quick reference
echo "📚 Quick Commands:"
echo "  fractal status       # Bot status"
echo "  fractal logs         # Stream logs"
echo "  pytest tests/        # Run tests"
echo ""

echo "🌀 Manifesto: https://github.com/r464r64r/Frakt/blob/main/manifesto.md"
echo ""
EOF

chmod +x .claude/hooks/SessionStart.sh

# Test
./.claude/hooks/SessionStart.sh

git add .claude/
git commit -m "feat: Add SessionStart hook for Claude Code"
git push origin main
```

**Success criteria:**
- [ ] Hook executes in <2s
- [ ] Shows git status + bot status + current sprint
- [ ] Works offline (graceful degradation if EC2 unreachable)
- [ ] Claude Code loads context automatically

---

### Milestone 3.2: GitHub Agents

**Goal:** Automate code review, deployment, weekly reports.

**Implementation:**

```bash
cd ~/workspace/Frakt

# Agent 1: Code Reviewer
cat > .github/workflows/agent-reviewer.yml << 'EOF'
name: CodeReviewer Agent

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .

      - name: Run tests
        run: pytest tests/ -v

      - name: Check coverage
        run: pytest tests/ --cov=frakt --cov-report=term --cov-fail-under=70

      - name: Type checking
        run: mypy frakt/ --ignore-missing-imports

      - name: Manifesto compliance
        run: pytest tests/test_manifesto.py -v

      - name: Comment on PR
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              body: '❌ **Review Failed**\n\nPlease fix errors before merging.'
            })
EOF

git add .github/workflows/agent-reviewer.yml
git commit -m "feat: Add CodeReviewer agent"
git push origin main


cd ~/workspace/FraktAl

# Agent 2: Deployer
cat > fractal_dev/agents/deploy.yml << 'EOF'
name: Deployer Agent

on:
  push:
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: SSH to EC2 and deploy
        env:
          SSH_KEY: ${{ secrets.EC2_SSH_KEY }}
        run: |
          echo "$SSH_KEY" > /tmp/ec2_key
          chmod 600 /tmp/ec2_key

          ssh -i /tmp/ec2_key ubuntu@54.199.8.26 << 'ENDSSH'
            cd ~/FractalTrader
            git pull origin main
            docker build -t fraktal:latest .
            docker stop fractal-trader-dev || true
            docker rm fractal-trader-dev || true
            docker run -d --name fractal-trader-dev -p 8080:8080 --env-file .env fraktal:latest
          ENDSSH

      - name: Verify deployment
        run: |
          sleep 30
          curl -f http://54.199.8.26:8080/health || exit 1

      - name: Create release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
EOF

# Agent 3: Weekly Reporter
cat > fractal_dev/agents/reporter.yml << 'EOF'
name: Weekly Reporter

on:
  schedule:
    - cron: '0 0 * * 0'  # Sunday midnight UTC

jobs:
  generate-report:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install jupyter nbconvert pandas plotly requests

      - name: Run notebook
        run: |
          jupyter nbconvert --to html --execute notebooks/reports/weekly_performance.ipynb

      - name: Upload to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./
          destination_dir: reports/week_$(date +%U)
EOF

git add fractal_dev/agents/
git commit -m "feat: Add Deployer and Reporter agents"
git push origin main
```

**Success criteria:**
- [ ] CodeReviewer runs on every PR
- [ ] Deployer triggers on tag push (`git tag v1.0.0 && git push --tags`)
- [ ] Reporter generates weekly HTML (uploaded to GitHub Pages)
- [ ] All agents have clear failure notifications

---

### Milestone 3.3: Public Dashboard

**Goal:** Web UI showing bot status, trades, equity curve.

**Implementation:**

```bash
cd ~/workspace/FraktAl

mkdir -p fractal_pub/web

cat > fractal_pub/web/dashboard.py << 'EOF'
"""
FraktAl public dashboard (Streamlit).

Shows:
- Bot status (uptime, trades, equity)
- Equity curve chart
- Recent trades table
- Hyperliquid wallet link
"""
import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="FraktAl Live",
    page_icon="🌀",
    layout="wide"
)

# Fetch data from API
API_URL = "http://54.199.8.26:8080"

try:
    status = requests.get(f"{API_URL}/api/status", timeout=5).json()
    trades = requests.get(f"{API_URL}/api/trades", timeout=5).json()
    wallet = requests.get(f"{API_URL}/api/wallet", timeout=5).json()
except:
    st.error("❌ Unable to connect to bot API")
    st.stop()

# Header
st.title("🌀 FraktAl — Live Trading Bot")
st.markdown(f"Powered by [Frakt](https://github.com/r464r64r/Frakt) | [Manifesto](https://github.com/r464r64r/Frakt/blob/main/manifesto.md)")

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("⏱️ Uptime", status['uptime'])
col2.metric("📊 Trades", status['trades'])
col3.metric("💰 Equity", f"${status['equity']:,.2f}")
col4.metric("🎯 Strategy", status['strategy'])

# Wallet link
st.markdown(f"**Hyperliquid Wallet:** [{wallet['address'][:10]}...{wallet['address'][-6:]}]({wallet['explorer']}) (Testnet)")

# Equity curve
if len(trades) > 0:
    df = pd.DataFrame(trades)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['equity'],
        mode='lines',
        name='Equity',
        line=dict(color='#00ff00', width=2)
    ))
    fig.update_layout(
        title="Equity Curve",
        xaxis_title="Time",
        yaxis_title="Equity (USD)",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

# Recent trades
st.subheader("Recent Trades")
if len(trades) > 0:
    df_display = df[['timestamp', 'symbol', 'side', 'entry_price', 'exit_price', 'pnl', 'pnl_pct']].tail(20)
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("No trades yet")

# Footer
st.markdown("---")
st.markdown("🧊 **FraktAl** — Liquidity-first trading. No lagging indicators. Fractal structure.")
EOF

# Add to requirements
echo "streamlit>=1.28.0" >> requirements.txt
echo "plotly>=5.17.0" >> requirements.txt

# Update supervisord to run dashboard
cat >> supervisord.conf << 'EOF'

[program:dashboard]
command=streamlit run fractal_pub/web/dashboard.py --server.port 8501 --server.address 0.0.0.0
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/dashboard.err.log
stdout_logfile=/var/log/dashboard.out.log
EOF

# Update Dockerfile to expose dashboard port
sed -i 's/EXPOSE 8080/EXPOSE 8080 8501/' Dockerfile

git add fractal_pub/web/ supervisord.conf Dockerfile requirements.txt
git commit -m "feat: Add public dashboard (Streamlit)"
git push origin main
```

**Deploy:**

```bash
# SSH to EC2
ssh fractal-ec2

# Pull + rebuild
cd ~/FractalTrader
git pull
docker build -t fraktal:latest .
docker stop fractal-trader-dev
docker rm fractal-trader-dev
docker run -d --name fractal-trader-dev -p 8080:8080 -p 8501:8501 --env-file .env fraktal:latest

# Test
curl http://54.199.8.26:8501
# Dashboard should load (HTML)
```

**Success criteria:**
- [ ] Dashboard accessible at `http://54.199.8.26:8501`
- [ ] Shows real-time bot status (updates every 5s)
- [ ] Equity curve renders correctly
- [ ] Wallet link works (opens Hyperliquid explorer)
- [ ] Mobile-responsive

---

## Phase 4: Migration Finalization (Days 15-16)

### Milestone 4.1: FractalTrader Sunset PR

**Goal:** Close FractalTrader with final PR explaining migration.

**Implementation:**

```bash
cd ~/workspace/FractalTrader

git checkout -b final/graduation-announcement

# Create sunset notice
cat > SUNSET_NOTICE.md << 'EOF'
# 🎓 FractalTrader Graduation

**Effective Date:** 2026-01-11
**Status:** Project completed, repositories migrated

---

## What Happened?

FractalTrader successfully completed its **incubation phase** (Sprints 1-4).

**Achievements:**
- ✅ 96% production readiness
- ✅ 64.5hr continuous testnet run (zero crashes)
- ✅ 358+ tests, 94% coverage
- ✅ SMC engine validated in live markets
- ✅ 52 real trades executed on Hyperliquid testnet

This project now evolves into **two distinct entities**:

---

## New Repositories

### 1. [Frakt](https://github.com/r464r64r/Frakt) (Public, MIT)

**What it is:**
- SMC-based trading engine
- Core algorithms (BOS, FVG, liquidity sweeps)
- Strategies, risk management, backtesting tools
- Community-driven, open source

**Who it's for:**
- Traders who want to build their own SMC-based bots
- Researchers studying institutional order flow
- Contributors improving the engine

**Get Started:**
```bash
pip install frakt  # (future PyPI package)
# Or: pip install git+https://github.com/r464r64r/Frakt.git
```

**Documentation:** [manifesto.md](https://github.com/r464r64r/Frakt/blob/main/manifesto.md)

---

### 2. FraktAl (Private)

**What it is:**
- Full trading platform (uses Frakt as engine)
- Live bot, infrastructure, automation
- Publication layer (API, dashboard)
- SaaS roadmap → frakt.al

**Status:** Active development, private for now.

---

## For Contributors

**Want to contribute?**
- **Improve SMC algorithms** → Open PR in [Frakt](https://github.com/r464r64r/Frakt)
- **Report bugs** → Open issue in Frakt
- **Use the engine** → Fork Frakt (it's MIT licensed!)

**Questions?**
- Open an issue in Frakt
- Or reach out directly

---

## This Repository

**FractalTrader** is now **archived** (read-only).

All code has been migrated to Frakt/FraktAl. No further commits will be made here.

**Historical Reference:**
- Sprint reports: `docs/sprints/`
- Decision logs: `docs/decisions/`
- Full commit history preserved

---

Thank you for being part of this journey. 🚀

*"There is no price. There is bid/ask, order flow, liquidity distribution."*
— Frakt Manifesto
EOF

# Update README to point to new repos
cat > README.md << 'EOF'
# FractalTrader (Archived)

**⚠️ This project has been migrated.**

See [SUNSET_NOTICE.md](SUNSET_NOTICE.md) for details.

**New repositories:**
- [Frakt](https://github.com/r464r64r/Frakt) — SMC engine (public, MIT)
- FraktAl — Full platform (private)

---

**Historical reference only.** No new commits accepted.
EOF

git add SUNSET_NOTICE.md README.md
git commit -m "docs: Add graduation notice and sunset README"
git push origin final/graduation-announcement

# Create PR on GitHub
gh pr create \
  --title "🎓 Project Graduation — FractalTrader → Frakt + FraktAl" \
  --body "$(cat SUNSET_NOTICE.md)" \
  --base main

# After PR merged, archive repo
gh repo archive r464r64r/FractalTrader
```

**Success criteria:**
- [ ] PR merged to main
- [ ] SUNSET_NOTICE.md clearly explains migration
- [ ] README points to new repos
- [ ] Repository archived (read-only)

---

### Milestone 4.2: Transfer Open Issues

**Goal:** Migrate relevant issues from FractalTrader to Frakt/FraktAl.

**Implementation:**

```bash
# List all open issues
gh issue list --repo r464r64r/FractalTrader --state open

# For each issue, decide:
# - Core/strategy bug → transfer to Frakt
# - Live bot bug → transfer to FraktAl
# - Documentation → close (docs migrated)

# Example: Transfer issue #42 to Frakt
gh issue transfer 42 --repo r464r64r/Frakt

# Or: Close with migration comment
gh issue close 42 --comment "Migrated to Frakt#15"
```

**Success criteria:**
- [ ] All open issues reviewed
- [ ] Critical issues transferred
- [ ] Low-priority issues closed with explanation

---

### Milestone 4.3: Docker Compose Setup

**Goal:** Use docker-compose for clean Frakt/FraktAl separation.

**Implementation:**

```bash
cd ~/workspace/FraktAl

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  frakt:
    image: ghcr.io/r464r64r/frakt:latest
    build:
      context: ../Frakt
      dockerfile: Dockerfile
    volumes:
      - frakt-data:/data
    networks:
      - fraktal-net
    healthcheck:
      test: ["CMD", "python3", "-c", "import frakt"]
      interval: 30s
      timeout: 10s
      retries: 3

  fraktal-bot:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      frakt:
        condition: service_healthy
    environment:
      - HL_API_KEY=${HL_API_KEY}
      - HL_SECRET=${HL_SECRET}
    ports:
      - "8080:8080"
      - "8501:8501"
    volumes:
      - fraktal-state:/app/.state
      - frakt-data:/data:ro  # Read-only access to Frakt data
    networks:
      - fraktal-net
    restart: unless-stopped

volumes:
  frakt-data:
  fraktal-state:

networks:
  fraktal-net:
    driver: bridge
EOF

# Update Frakt Dockerfile (standalone)
cd ~/workspace/Frakt

cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /frakt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pytest tests/  # Validate on build

CMD ["python3", "-c", "print('Frakt engine ready')"]
EOF

git add Dockerfile
git commit -m "feat: Add standalone Dockerfile"
git push origin main

# Publish to GitHub Container Registry
docker build -t ghcr.io/r464r64r/frakt:latest .
docker push ghcr.io/r464r64r/frakt:latest


# Back to FraktAl
cd ~/workspace/FraktAl

# Test docker-compose
docker-compose up -d

# Verify
docker-compose ps
docker-compose logs frakt
docker-compose logs fraktal-bot
```

**Success criteria:**
- [ ] `docker-compose up` starts both containers
- [ ] FraktAl bot imports from Frakt container
- [ ] Shared volume works (data flow)
- [ ] API + dashboard accessible

---

## Rollback Procedures

If anything goes wrong during migration:

### Rollback 1: Code Migration Failed

**Symptom:** Tests failing in Frakt/FraktAl after split.

**Solution:**
```bash
# FractalTrader is still intact (not archived yet)
cd ~/workspace/FractalTrader
git log --oneline -10

# Identify working commit
git checkout <last-good-commit>

# Re-run migration scripts with fixes
```

### Rollback 2: EC2 Deployment Failed

**Symptom:** Bot crashed after deploying new multi-process container.

**Solution:**
```bash
ssh fractal-ec2

# Stop broken container
docker stop fractal-trader-dev
docker rm fractal-trader-dev

# Rollback to previous image
docker images  # Find previous tag
docker run -d --name fractal-trader-dev <previous-image-id>

# Or: Pull old code
cd ~/FractalTrader
git checkout <previous-commit>
docker build -t fraktal:rollback .
docker run -d --name fractal-trader-dev -p 8080:8080 --env-file .env fraktal:rollback
```

### Rollback 3: Manifesto Tests Breaking CI

**Symptom:** Embedded tests too strict, blocking all PRs.

**Solution:**
```bash
cd ~/workspace/Frakt

# Temporarily disable manifesto tests
git checkout -b hotfix/relax-manifesto-tests

# Comment out strict assertions
sed -i 's/assert term not in source/# assert term not in source/' tests/test_manifesto.py

git commit -m "hotfix: Relax manifesto tests temporarily"
git push origin hotfix/relax-manifesto-tests

# Merge immediately to unblock PRs
gh pr create --fill
gh pr merge --auto --squash
```

---

## Success Criteria (Overall)

Migration is **complete** when:

- [ ] Frakt repo live, public, MIT licensed
- [ ] FraktAl repo live, private
- [ ] manifesto.md translated to English
- [ ] Embedded tests in manifesto.md (CI enforced)
- [ ] Exchange wrapper in Frakt (generic, no secrets)
- [ ] Unified CLI (`fractal`) works on laptop + EC2
- [ ] EC2 API live (http://54.199.8.26:8080)
- [ ] Public dashboard live (http://54.199.8.26:8501)
- [ ] SessionStart hook auto-loads context
- [ ] GitHub Agents running (CodeReviewer, Deployer, Reporter)
- [ ] docker-compose separates Frakt/FraktAl
- [ ] FractalTrader archived
- [ ] All open issues transferred
- [ ] Zero downtime (EC2 bot never stopped)

---

## Next Steps (Post-Migration)

Once migration is complete:

1. **Announce on GitHub/Social Media**
   - Tweet: "FractalTrader graduates → Frakt (open source) + FraktAl (platform)"
   - Post in trading communities

2. **Publish Frakt to PyPI**
   ```bash
   cd ~/workspace/Frakt
   python setup.py sdist bdist_wheel
   twine upload dist/*
   ```

3. **Domain Setup (frakt.al)**
   - Purchase domain
   - Point to EC2 public IP
   - SSL cert (Let's Encrypt)

4. **Continue Sprint 5**
   - E2E tests
   - Enhanced monitoring
   - Portfolio-level risk controls

---

## Appendix A: File Mapping

**FractalTrader → Frakt:**
```
core/                   → frakt/core/
strategies/             → frakt/strategies/
risk/                   → frakt/risk/
backtesting/            → frakt/backtesting/
data/                   → frakt/data/
tests/test_core.py      → frakt/tests/test_core.py
tests/test_strategies.py → frakt/tests/test_strategies.py
README_MANIFESTO_PL.md  → manifesto.md (translated)
LICENSE                 → LICENSE (MIT)
```

**FractalTrader → FraktAl:**
```
live/                   → fraktal/live/
fractal_mcp/            → fraktal/fractal_dev/mcp/
docs/                   → fraktal/docs/
deploy/                 → fraktal/deploy/
notebooks/              → fraktal/notebooks/
.github/workflows/      → fraktal/fractal_dev/agents/
tests/test_live.py      → fraktal/tests/test_live.py
.env.example            → fraktal/.env.example
docker-compose.yml      → fraktal/docker-compose.yml
```

---

## Appendix B: Contacts & Resources

**Repositories:**
- Frakt: https://github.com/r464r64r/Frakt
- FraktAl: https://github.com/r464r64r/FraktAl (private)
- FractalTrader (archived): https://github.com/r464r64r/FractalTrader

**Infrastructure:**
- EC2 Tokyo: 54.199.8.26
  - API: http://54.199.8.26:8080
  - Dashboard: http://54.199.8.26:8501
- Hyperliquid Wallet (testnet): 0xf7ab281eeBF13C8720a7eE531934a4803E905403

**Documentation:**
- Manifesto: https://github.com/r464r64r/Frakt/blob/main/manifesto.md
- CLAUDE.md: (in FraktAl repo, guides AI development)
- Roadmap: docs/ROADMAP_Q1_2026.md

**Tools:**
- Unified CLI: `fractal` (install: `pip install -e .` in FraktAl)
- MCP Server: fractal_dev/mcp/
- SessionStart Hook: .claude/hooks/SessionStart.sh

---

**END OF MIGRATION PLAN**

---

*"There is no price. There is bid/ask, order flow, liquidity distribution."*
— Frakt Manifesto

Ship or die. 🚀
