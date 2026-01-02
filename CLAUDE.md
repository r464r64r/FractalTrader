# FractalTrader — AI Context

**Compact reference for AI assistants. Updated: 2026-01-02**

## Status
- **Sprints 1-3:** COMPLETE (Dec 2025)
- **Sprint 4:** Production Hardening (Feb 4-17, 2026) - NEXT
- **AWS:** Configured (`deploy/AWS_*.md`)
- **Test coverage:** Core 95%+, Strategies 13-42% (needs work)

## Project Structure
```
core/           # SMC detection (95%+ coverage) - DO NOT BREAK
strategies/     # Trading strategies (needs test coverage)
risk/           # Position sizing, confidence (98%)
live/           # Paper trading bot + CLI
  hl_integration/  # Hyperliquid exchange
data/           # Market data fetchers
backtesting/    # vectorbt runner
notebooks/      # Jupyter dashboards
tests/          # pytest suite
deploy/         # AWS/cloud scripts
```

## Critical Files
- `live/state_manager.py` - Position/trade persistence
- `live/cli.py` - Bot control (start/stop/status)
- `core/*.py` - SMC algorithms (high coverage, stable)
- `strategies/*.py` - Entry/exit logic (low coverage, active dev)

## Known Issues (Sprint 4 priorities)
1. **Strategy test coverage:** liquidity_sweep 13%, bos_orderblock 42%
2. **Race condition:** StateManager concurrent access (needs file locking)
3. **No rate limiting:** API calls to Hyperliquid
4. **Error handling:** Circuit breaker treats all errors equally

## Commands
```bash
# Tests (Docker required for full suite)
./docker-start.sh test

# Paper trading
python -m live.cli start --strategy liquidity_sweep
python -m live.cli status
python -m live.cli stop
```

## Docs Structure
```
docs/
├── ROADMAP_Q1_2025.md    # 6-sprint roadmap (Q1 2026)
├── SPRINT_FRAMEWORK.md   # Sprint methodology
├── sprints/              # Sprint reports (1-3)
└── archive/              # Historical docs
deploy/                   # AWS deployment guides
```

## Rules
- Never push to `main` directly
- Run tests before commit
- Core modules: high bar for changes
- Type hints + docstrings required
