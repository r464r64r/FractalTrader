# FractalTrader — AI Context

**Compact reference for AI assistants. Updated: 2026-01-10**

---

## 🚀 Quick Start (Read This First!)

### Docker Workflow — CRITICAL
**ALL commands run inside Docker container `fractal-trader-dev`**

```bash
# Check container status
sudo docker ps

# Execute commands in container
sudo docker exec fractal-trader-dev <command>

# Bot commands (always use python3, not python)
sudo docker exec fractal-trader-dev python3 -m live.cli status
sudo docker exec fractal-trader-dev tail -f /tmp/bot_v2.log
```

### Current Bot Status — Quick Check
```bash
# Status
sudo docker exec fractal-trader-dev python3 -m live.cli status

# Recent logs
sudo docker exec fractal-trader-dev tail -50 /tmp/bot_v2.log

# Errors
sudo docker exec fractal-trader-dev grep "CRITICAL\|ERROR" /tmp/bot_v2.log
```

**Full monitoring guide:** `docs/CURRENTRUN.md`

---

## 📚 Docs Quick Index (Where to Find What)

### Active/Critical (Check These First)
- **`docs/CURRENTRUN.md`** → Real-time bot status, monitoring commands, validation timeline
- **`docs/ISSUES.md`** → Project status, latest fixes, current sprint, what's next
- **`CHANGELOG.md`** → Version history, migration guides (keepachangelog.com format)
- **`SECURITY.md`** → Security policy, vulnerability reporting, best practices

### Planning/Roadmap
- **`docs/ROADMAP_Q1_2026.md`** → 6-sprint plan (Dec 2025 - Mar 2026)
- **`docs/SPRINT_FRAMEWORK.md`** → Sprint methodology, how we work

### Decision Records (ADRs)
- **`docs/decisions/`** → Architecture decision records
- **`docs/decisions/0001-*.md`** → Circuit breaker false triggers fix
- **`docs/decisions/0004-*.md`** → Testnet simulation mode design

### Historical/Reference
- **`docs/sprints/*.md`** → Sprint 1-4 reports (completed)
- **`docs/archive/`** → Deprecated docs (Jan 2 cleanup)
- **`docs/archive/legacy/`** → Pre-sprint era docs

### Deploy
- **`deploy/AWS_*.md`** → AWS deployment guides (configured but not active)

---

## Status
- **Sprints 1-4:** ✅ COMPLETE (Sprint 4: Jan 2-6, 2026)
- **Current:** Sprint 5 - E2E Testing + Monitoring (Feb 9-22, 2026)
- **Next:** Sprint 6 - 7-Day Validation (Feb 23 - Mar 8, 2026)
- **Production Readiness:** 96% (verified on EC2, Jan 10)
- **Test Coverage:** 94% (358+ tests)
- **Live Trading:** 🟢 Active on Hyperliquid testnet (EC2 Tokyo, 4d 15h uptime)

---

## Project Structure
```
core/           # SMC detection (95%+ coverage) - stable, don't change
strategies/     # Trading strategies (70%+ coverage) - active development
risk/           # Position sizing, confidence (98%)
live/           # Paper trading bot + CLI ⭐ ACTIVE
  hl_integration/  # Hyperliquid exchange integration
  state_manager.py # Position persistence (filelock)
  cli.py           # Bot control (start/stop/status)
data/           # Market data fetchers (rate limited)
backtesting/    # vectorbt runner
notebooks/      # Jupyter dashboards
tests/          # pytest suite (350+)
deploy/         # AWS/cloud scripts
docs/           # Documentation ⭐ UPDATE FREQUENTLY
```

---

## Key Files (Hot Paths)

### Bot Operations
- `live/cli.py` → Bot control (start/stop/status)
- `live/hl_integration/testnet.py` → Trading loop, circuit breakers
- `live/state_manager.py` → Position persistence (JSON + filelock)

### Core Logic (Stable — High Bar for Changes)
- `core/*.py` → SMC algorithms (95%+ coverage) - avoid changes
- `strategies/*.py` → Entry/exit logic (70%+ tested)
- `risk/position_sizing.py` → Position sizing calculator

### Monitoring
- `/tmp/bot_v2.log` → Current bot logs (inside container)
- `.testnet_state.json` → State file (auto-saved, gitignored)
- `docs/CURRENTRUN.md` → Monitoring guide

---

## Common Tasks

### Bot Control (Always in Docker)
```bash
# Start bot (simulation mode)
sudo docker exec fractal-trader-dev python3 -m live.cli start --strategy liquidity_sweep

# Check status
sudo docker exec fractal-trader-dev python3 -m live.cli status

# Stop bot
sudo docker exec fractal-trader-dev python3 -m live.cli stop

# Monitor live
sudo docker exec fractal-trader-dev tail -f /tmp/bot_v2.log
```

### Tests
```bash
# All tests (in Docker)
sudo docker exec fractal-trader-dev python3 -m pytest tests/ -v

# Specific test file
sudo docker exec fractal-trader-dev python3 -m pytest tests/test_strategies.py -v

# Coverage
sudo docker exec fractal-trader-dev python3 -m pytest tests/ --cov=strategies --cov-report=term-missing
```

### State Management
```bash
# View state file
sudo docker exec fractal-trader-dev cat /app/.testnet_state.json

# Clean state (bot must be stopped)
sudo docker exec fractal-trader-dev rm -f .testnet_state.json .testnet_state.json.* .trading_bot.pid
```

---

## Current Work (as of 2026-01-07)

**Sprint 4:** ✅ COMPLETE (Jan 2-6, 2026)
- Testnet deployment successful
- 7 critical bugs fixed (position sync, circuit breaker, state persistence, tick size)
- 24h+ continuous operation achieved
- See: `docs/sprints/sprint-4.md`

**Sprint 5:** 🔄 CURRENT (Feb 9-22, 2026)
- E2E integration tests (data → signal → execution)
- Enhanced monitoring dashboard (Streamlit)
- Portfolio-level risk controls
- Signal statistics tracking

**Recent Updates (Phase 1-2):**
- Centralized logging system with file rotation
- Standard project files (CHANGELOG.md, SECURITY.md, LICENSE)
- Documentation reorganization (ADRs, Sprint 4 report)
- All fixes merged to main

**Next:** Sprint 6 - 7-Day Testnet Validation (Feb 23 - Mar 8, 2026)

---

## 🔄 Development Protocol (How to Work)

### Session Startup Checklist
1. **Read foundation:** `README_MANIFESTO_PL.md` - "po co to wszystko było"
2. **Check current status:** `docs/ISSUES.md` - co naprawione, co następne
3. **Verify infrastructure:**
   - Local: `sudo docker ps` - czy container działa
   - EC2: `ssh fractal-ec2 "uptime"` - bot status
4. **Review context:** `CLAUDE.md` (this file) - quick reference
5. **Check sprint:** `docs/sprints/sprint-*.md` - gdzie jesteśmy

### Work Flow (The FractalTrader Way)

**1. Understand Context (Nitka)**
- Start with WHY (Manifesto) → WHAT (ISSUES.md) → HOW (code)
- Check recent commits: `git log --oneline -10`
- Read relevant sprint report if mid-sprint

**2. Navigate to Goal (Indeks)**
- Use `docs/` structure - everything indexed in `CLAUDE.md`
- Current work: always in `docs/ISSUES.md` "Current" section
- Technical decisions: `docs/decisions/*.md` (ADRs)

**3. Execute with Purpose (Cel → Wyzwanie)**
- **Plan first:** Use TodoWrite tool for multi-step tasks
- **Test-driven:** Write/update tests BEFORE implementation
- **Document as you go:** Update ISSUES.md when fixing bugs
- **Verify on EC2:** Check production logs after local changes

**4. Close Culturally (Zamknięcie)**
- **Update docs:** ISSUES.md, CURRENTRUN.md if relevant
- **Clean commit:** Descriptive message, reference issues
- **PR if needed:** Never push to main directly (unless trivial)
- **Verify sync:** Local ↔ EC2 alignment

### When to Document What

| Event | Document Where | Format |
|-------|----------------|--------|
| Bug discovered | `docs/ISSUES.md` | Add to "Latest Fixes" section |
| Bug fixed + verified | Comment on GitHub issue | Link commit, show verification |
| Sprint complete | `docs/sprints/sprint-N.md` | Full report with metrics |
| Architecture decision | `docs/decisions/NNNN-*.md` | ADR format |
| Production change | `CHANGELOG.md` | keepachangelog.com format |
| Status change | `docs/ISSUES.md` "Current Metrics" | Update percentage, counts |
| New feature planning | GitHub issue | Use templates in `.github/` |

### Infrastructure Maintenance

**Daily checks (if bot running):**
- EC2 uptime: `ssh fractal-ec2 "uptime"`
- Bot status: `ssh fractal-ec2 "sudo docker exec fractal-trader-dev python3 -m live.cli status"`
- Recent errors: `ssh fractal-ec2 "sudo docker exec fractal-trader-dev grep -i error /tmp/bot_v2.log | tail -10"`

**After code changes:**
1. Test locally: `sudo docker exec fractal-trader-dev python3 -m pytest tests/`
2. Push to GitHub: `git push origin <branch>`
3. SSH to EC2: `ssh fractal-ec2`
4. Pull changes: `cd FractalTrader && git pull`
5. Restart if needed: `sudo docker restart fractal-trader-dev`
6. Verify: Check logs for 5-10 minutes

**Weekly cleanup:**
- Review open issues: Close or update stale ones
- Check branch status: Delete merged branches
- Archive old logs: EC2 `/tmp/bot_v2.log` rotation
- Update ISSUES.md: Refresh "Current Metrics"

### Questions to Ask Yourself

**Before starting work:**
- [ ] Did I read the Manifesto recently? (stay aligned with vision)
- [ ] Is ISSUES.md current? (am I working on the right thing?)
- [ ] Is EC2 bot stable? (check before making changes)
- [ ] Do I understand the goal? (not just the task)

**During work:**
- [ ] Am I updating docs as I go? (not leaving it for later)
- [ ] Are tests passing? (local + on changes)
- [ ] Is this aligned with sprint goals? (focus vs distraction)

**After completing:**
- [ ] Did I verify on production (EC2)? (not just local)
- [ ] Did I update all relevant docs? (ISSUES, CHANGELOG, etc.)
- [ ] Is the commit message clear? (future-me will thank me)
- [ ] Can I explain WHY not just WHAT? (architectural thinking)

---

## EC2 Infrastructure (Production Testnet)

### SSH Access
```bash
# Primary key
ssh -i ~/.ssh/fractal_ec2 ubuntu@54.199.8.26

# Alias (add to ~/.ssh/config)
Host fractal-ec2
    HostName 54.199.8.26
    User ubuntu
    IdentityFile ~/.ssh/fractal_ec2
    ServerAliveInterval 60

# Then: ssh fractal-ec2
```

### EC2 Bot Commands
```bash
# Status
ssh fractal-ec2 "sudo docker exec fractal-trader-dev python3 -m live.cli status"

# Logs (last 100 lines)
ssh fractal-ec2 "sudo docker exec fractal-trader-dev tail -100 /tmp/bot_v2.log"

# Check for errors
ssh fractal-ec2 "sudo docker exec fractal-trader-dev grep -i 'error\|critical' /tmp/bot_v2.log | tail -20"

# Download logs for analysis
scp fractal-ec2:/tmp/bot_v2.log /tmp/ec2_logs.txt
```

### EC2 Monitoring
- **Location:** Tokyo (ap-northeast-1) - <5ms to Hyperliquid
- **Instance:** t3.micro (1GB RAM, 2 vCPU)
- **Uptime check:** `ssh fractal-ec2 "uptime"`
- **Docker status:** `ssh fractal-ec2 "sudo docker ps"`

---

## Rules
- **Never push to `main` directly** - always use PRs
- **Pre-commit hooks** run automatically (black, ruff, mypy)
- **Core modules** (`core/`, `risk/`) - high bar for changes (95%+ coverage)
- **Type hints + docstrings** required for all new code
- **Docker first** - all commands in container unless explicitly host-side
- **Update docs** - CURRENTRUN.md, ISSUES.md when making changes
