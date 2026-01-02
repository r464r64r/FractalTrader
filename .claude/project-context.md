# FractalTrader — Claude Code Project Context

**Quick reference for AI assistants working on FractalTrader**

---

## 🎯 Current Status (Auto-Updated)

**Sprint:** Sprint 3 - Paper Trading Bot
**Status:** ✅ **COMPLETE** (Dec 30, 2025 - 21 days early!)
**Previous Sprints:**
- ✅ Sprint 1 Complete (Dec 26, 2025 - 4 days ahead!)
- ✅ Sprint 2 Complete (Dec 26, 2025 - 24 days ahead!)

**Sprint 3 Results:**

- ✅ All 5 success criteria met
- ✅ State persistence (position & trade tracking)
- ✅ Execution engine (Hyperliquid testnet)
- ✅ Circuit breakers (max loss, position limits)
- ✅ Daily performance reports + CLI interface
- ✅ 31 new tests passing (280+ total)
- ✅ Deliverable: Automated Trading Bot with CLI
- ✅ Completed: Dec 30, 2025 (21 days early!)

**Next Sprint:** Sprint 4 - Production Hardening (Feb 4-17, 2026)

---

## 📚 Essential Reading (Start Here)

**Before doing ANY work:**

1. [README.md](../README.md) - Project overview & quick start
2. [docs/SPRINT_FRAMEWORK.md](../docs/SPRINT_FRAMEWORK.md) - Sprint methodology
3. [.github/WORKFLOW.md](../.github/WORKFLOW.md) - GitHub workflow
4. [AI_DEVELOPMENT.md](../AI_DEVELOPMENT.md) - AI assistant guidelines

**When working on specific tasks:**

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Code standards & PR process
- [DEVELOPMENT.md](../DEVELOPMENT.md) - Architecture & status
- [docs/ROADMAP_Q1_2025.md](../docs/ROADMAP_Q1_2025.md) - 6-sprint roadmap

---

## 🚢 Sprint Workflow (Ship or Die)

### Philosophy

- **2-week sprints** (fixed, no extensions)
- **1 clickable deliverable** per sprint
- **Cut scope, don't extend time**
- **Always releasable** (main branch always works)

### Workflow

```text
1. Pick task from sprint issues
   ↓
2. Comment "Working on this"
   ↓
3. Create branch (feature/issue-N-description)
   ↓
4. Implement + tests (TDD preferred)
   ↓
5. Daily updates on issue
   ↓
6. Open PR when ready
   ↓
7. Address review feedback
   ↓
8. Merge → Close issue
```

### Issue Labels

- `sprint-1` - Current sprint tasks (HIGH PRIORITY)
- `research` - Investigation work
- `implementation` - Coding tasks
- `needs-analysis` - Waiting for strategic breakdown
- `blocked` - Waiting on dependency

**Find tasks:** https://github.com/r464r64r/FractalTrader/issues?q=is%3Aissue+is%3Aopen+label%3Asprint-1

---

## 🏗️ Project Structure (Quick Reference)

```
FractalTrader/
├── core/              # SMC detection (95-100% coverage) ⭐ CRITICAL
│   ├── market_structure.py   # BOS/CHoCH
│   ├── liquidity.py          # Sweeps, levels
│   ├── imbalance.py          # Fair Value Gaps
│   └── order_blocks.py       # Order blocks
│
├── strategies/        # Trading strategies (79% coverage)
│   ├── base.py               # Strategy framework
│   ├── liquidity_sweep.py    # Reversal after stop hunts
│   ├── fvg_fill.py           # Trade FVG fills
│   └── bos_orderblock.py     # Trend + OB entries
│
├── risk/              # Risk management (98% coverage) ⭐
│   ├── confidence.py         # Signal scoring (0-100)
│   └── position_sizing.py    # Dynamic sizing
│
├── data/              # Market data (90% coverage)
│   ├── fetcher.py            # Base interface
│   ├── hyperliquid_fetcher.py # Live data
│   └── ccxt_fetcher.py       # Historical
│
├── live/              # Live trading (⚠️ TESTNET ONLY)
│   └── hyperliquid/          # Hyperliquid exchange
│
├── backtesting/       # Backtesting (vectorbt)
│   └── runner.py
│
├── visualization/     # ✅ Sprint 1 (COMPLETE)
│   └── fractal_dashboard.py  # Jupyter UI
│
├── notebooks/         # 🔴 Sprint 2 (COMPLETE - NEW!)
│   ├── fractal_viewer.ipynb  # Static analysis
│   ├── live_dashboard.ipynb  # Real-time monitoring
│   ├── live_data_stream.py   # Streaming engine
│   ├── alert_system.py       # Alerts + journal
│   └── setup_detector.py     # Setup detection
│
├── tests/             # 280 tests (30 new in Sprint 2!)
├── docs/              # Sprint reports & roadmap
│   ├── SPRINT_1_REPORT.md
│   └── SPRINT_2_REPORT.md ⭐ NEW!
└── .github/           # Issue templates & workflow
```

---

## ⚡ Quick Commands

```bash
# Run core tests (no Docker)
python -m pytest tests/ -v \
  --ignore=tests/test_backtesting.py \
  --ignore=tests/test_data_fetchers.py \
  --ignore=tests/test_live_trading.py

# Run all tests (Docker)
./docker-start.sh test

# Check GitHub issues
gh issue list --label sprint-1

# Create new issue
gh issue create --title "Title" --label sprint-1,implementation
```

---

## 🎯 Sprint 1 Goals (Dec 24 - Jan 6)

**Deliverable:** Interactive Jupyter notebook with multi-timeframe SMC visualization

**Success Criteria:**
- [ ] Notebook runs end-to-end without errors
- [ ] Charts are interactive (zoom, pan, hover)
- [ ] Order blocks clearly visible with labels
- [ ] Confidence panel explains setup (78/100 breakdown)
- [ ] README with screenshots and usage instructions

**Key Tasks:**
1. Research Plotly synchronization (#15)
2. Implement FractalDashboard core (#16)
3. Build order block rendering layer
4. Create confidence explainer panel
5. Integrate with example notebook
6. Write documentation

**What Filip Gets:**

```python
# notebooks/fractal_viewer.ipynb
from fractal_trader import FractalDashboard

dashboard = FractalDashboard(
    pair='BTC/USDT',
    timeframes=['4h', '1h', '15m']
)
dashboard.show()  # Interactive 3-panel chart with order blocks
```

---

## 💡 Key Concepts (SMC)

| Term | Definition | Where Used |
| ---- | ---------- | ---------- |
| **Swing High/Low** | Local price extremes | `core/market_structure.py` |
| **BOS** | Break of Structure (trend continuation) | `core/market_structure.py` |
| **CHoCH** | Change of Character (reversal) | `core/market_structure.py` |
| **FVG** | Fair Value Gap (imbalance) | `core/imbalance.py` |
| **Order Block** | Institutional accumulation zone | `core/order_blocks.py` |
| **Liquidity Sweep** | Stop hunt reversal | `core/liquidity.py` |

For deep dive: [docs/archive/fractal-trader-context.md](../docs/archive/fractal-trader-context.md)

---

## ✅ Code Standards (MUST FOLLOW)

### Required for All Code

```python
from typing import List, Dict, Optional
import pandas as pd

def detect_order_blocks(
    data: pd.DataFrame,
    min_strength: float = 0.7
) -> List[Dict]:
    """Detect order blocks in price data.

    Args:
        data: OHLCV DataFrame with datetime index
        min_strength: Minimum block strength (0-1)

    Returns:
        List of order blocks with zones and confidence

    Raises:
        ValueError: If data is empty or missing columns
    """
    # Implementation
    pass
```

**Must have:**
- ✅ Type hints on ALL functions
- ✅ Google-style docstrings (public functions)
- ✅ Tests (70%+ coverage for new code)
- ✅ Edge case handling

### Testing

```python
def test_order_blocks_empty_data():
    """Test order block detection with empty data."""
    with pytest.raises(ValueError, match="empty"):
        detect_order_blocks(pd.DataFrame())
```

**TDD approach preferred:**
1. Write test first
2. Implement feature
3. Verify test passes

---

## 🚨 Critical Rules

**NEVER:**
- ❌ Push directly to `main` branch
- ❌ Commit without running tests
- ❌ Break existing tests
- ❌ Touch `core/` without deep understanding
- ❌ Skip type hints or docstrings
- ❌ Create issues without checking sprint

**ALWAYS:**
- ✅ Work from sprint issues first
- ✅ Comment on issue before starting
- ✅ Run tests before committing
- ✅ Update issue with daily progress
- ✅ Follow existing code patterns
- ✅ Ask for help if blocked

---

## 🔗 Quick Links

| What | Where |
| ---- | ----- |
| Sprint planning | [#13](https://github.com/r464r64r/FractalTrader/issues/13) |
| Active sprint tasks | [Sprint 1 filter](https://github.com/r464r64r/FractalTrader/issues?q=is%3Aissue+is%3Aopen+label%3Asprint-1) |
| Sprint framework | [docs/SPRINT_FRAMEWORK.md](../docs/SPRINT_FRAMEWORK.md) |
| Q1 roadmap | [docs/ROADMAP_Q1_2025.md](../docs/ROADMAP_Q1_2025.md) |
| GitHub workflow | [.github/WORKFLOW.md](../.github/WORKFLOW.md) |
| Project board | https://github.com/r464r64r/FractalTrader/projects |
| AI guidelines | [AI_DEVELOPMENT.md](../AI_DEVELOPMENT.md) |

---

## 📅 Q1 2026 Roadmap (Quick View)

| Sprint | Dates | Deliverable | Status |
| ------ | ----- | ----------- | ------ |
| **1** | Dec 24-26, 2025 | Jupyter Fractal Viewer | ✅ COMPLETE |
| **2** | Dec 26, 2025 | Live Market Dashboard | ✅ COMPLETE |
| **3** | Dec 30, 2025 | Paper Trading Bot | ✅ COMPLETE |
| **4** | Feb 4-17, 2026 | Production Hardening | 📋 NEXT |
| **5** | Feb 18-Mar 3, 2026 | Tribal Weather MVP | 📋 Planned |
| **6** | Mar 4-17, 2026 | Live Trading (Mainnet) | 📋 Planned |

**End State (Mar 17, 2026):** Production-ready trading system with tribal intelligence

---

## 🤖 For AI Assistants

**When user says "work on the project":**
1. Check [active sprint issues](https://github.com/r464r64r/FractalTrader/issues?q=is%3Aissue+is%3Aopen+label%3Asprint-1)
2. Ask which task to work on (if not specified)
3. Read the issue completely
4. Comment on issue: "AI assistant starting work"
5. Create branch, implement, test, PR

**When user asks "what should I work on?":**
1. Show Sprint 1 tasks from GitHub
2. Suggest starting with research tasks (#15)
3. Point to [docs/SPRINT_FRAMEWORK.md](../docs/SPRINT_FRAMEWORK.md) for context

**When stuck:**
- Comment on issue with specific question
- Tag maintainer if blocked >1 day
- Check [.github/WORKFLOW.md](../.github/WORKFLOW.md) for escalation process

---

**Last Updated:** 2026-01-02 (Sprints 1-3 Complete)
**Auto-update:** Update this file at start of each sprint
