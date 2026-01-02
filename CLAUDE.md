# FractalTrader — AI Context

**Compact reference for AI assistants. Updated: 2026-01-02**

## Status
- **Sprints 1-4:** ✅ COMPLETE
- **Sprint 5-6:** E2E Testing + 7-Day Validation (pending)
- **AWS:** Configured (`deploy/AWS_*.md`)
- **Production Readiness:** ~92%
- **Test Coverage:** ~94% (350+ tests)

## Project Structure
```
core/           # SMC detection (95%+ coverage) - stable
strategies/     # Trading strategies (70%+ coverage)
risk/           # Position sizing, confidence (98%)
live/           # Paper trading bot + CLI
  hl_integration/  # Hyperliquid exchange
data/           # Market data fetchers (rate limited)
backtesting/    # vectorbt runner
notebooks/      # Jupyter dashboards
tests/          # pytest suite (350+)
deploy/         # AWS/cloud scripts
```

## Key Files
- `live/state_manager.py` - Position persistence (file locking)
- `live/cli.py` - Bot control (start/stop/status)
- `core/*.py` - SMC algorithms (stable)
- `strategies/*.py` - Entry/exit logic (70%+ tested)

## Commands
```bash
# Tests (Docker required for full suite)
./docker-start.sh test

# Paper trading
python -m live.cli start --strategy liquidity_sweep
python -m live.cli status
python -m live.cli stop
```

## Next Steps (Sprint 5-6)
1. E2E integration tests (data → signal → execution)
2. Monitoring dashboard (Streamlit)
3. 7-day testnet validation

## Docs
```
docs/
├── ISSUES.md             # Status & next steps
├── ROADMAP_Q1_2025.md    # 6-sprint roadmap
├── SPRINT_FRAMEWORK.md   # Sprint methodology
├── sprints/              # Sprint reports (1-3)
└── archive/              # Historical docs
deploy/                   # AWS deployment
```

## Rules
- Never push to `main` directly
- Pre-commit hooks run automatically (black, ruff, mypy)
- Core modules: high bar for changes
- Type hints + docstrings required
