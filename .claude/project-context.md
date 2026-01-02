# FractalTrader — Claude Code Context

**For full AI context:** See [CLAUDE.md](../CLAUDE.md) in root.

## Quick Status
| Sprint | Status |
|--------|--------|
| 1-4 | ✅ COMPLETE |
| 5-6 | 📋 NEXT (E2E + Testnet) |

**Production Readiness:** ~92% | **Tests:** 350+ | **Coverage:** ~94%

## Next Steps
1. E2E integration tests
2. Monitoring dashboard (Streamlit)
3. 7-day testnet validation

## Structure
```
core/           # SMC detection (stable)
strategies/     # Trading logic (70%+ tested)
risk/           # Position sizing (98%)
live/           # Paper trading bot
data/           # Rate-limited fetchers
deploy/         # AWS deployment
docs/sprints/   # Sprint 1-4 reports
```

## Key Commands
```bash
./docker-start.sh test        # Run tests
python -m live.cli status     # Bot status
```

## Docs
- [CLAUDE.md](../CLAUDE.md) - AI context
- [docs/ISSUES.md](../docs/ISSUES.md) - Status & next steps
- [docs/sprints/](../docs/sprints/) - Sprint reports
