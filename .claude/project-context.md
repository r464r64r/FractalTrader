# FractalTrader — Claude Code Context

**For full AI context:** See [CLAUDE.md](../CLAUDE.md) in root.

## Quick Status
| Sprint | Status |
|--------|--------|
| 1-3 | ✅ COMPLETE (Dec 2025) |
| 4 | 📋 NEXT (Feb 4-17, 2026) |

**AWS:** Deployed. See `deploy/AWS_*.md`

## Sprint 4 Priorities
1. Strategy test coverage: 13-42% → 70%+
2. File locking in `live/state_manager.py`
3. API rate limiting (Hyperliquid)
4. Error classification in circuit breaker

## Structure
```
core/           # SMC detection (stable, 95%+ coverage)
strategies/     # Trading logic (needs tests)
risk/           # Position sizing (98%)
live/           # Paper trading bot
  hl_integration/  # Hyperliquid connector
data/           # Market data fetchers
deploy/         # AWS deployment
docs/
  sprints/      # Sprint 1-3 reports
  archive/      # Historical docs
```

## Key Commands
```bash
./docker-start.sh test        # Run tests
python -m live.cli status     # Bot status
```

## Docs
- [README.md](../README.md) - Project overview
- [CLAUDE.md](../CLAUDE.md) - AI context
- [docs/ROADMAP_Q1_2025.md](../docs/ROADMAP_Q1_2025.md) - Roadmap
- [docs/sprints/](../docs/sprints/) - Sprint reports
