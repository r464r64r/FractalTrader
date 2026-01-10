# Archive Directory - Historical Documentation

This directory contains **historical documentation** from earlier phases of FractalTrader development.

---

## 📁 Structure

### `legacy/` - Pre-Sprint Era (Pre-Dec 2025)
Historical documents from before the sprint framework was established.

**Contents:**
- `fractal-trader-context.md` - Original project context
- `HAIKU_TASK_*.md` - AI collaboration handoff documents (Claude Haiku)
- `HAIKU_*.md` - Phase 0-1 development docs
- `DEPLOYMENT_PLAN.md` - Original deployment strategy
- `PHASE_1_PROGRESS.md` - First phase progress report

**Status:** ⚠️ **Historical reference only** - may contain outdated information

**Use case:** Understanding project evolution, architectural decisions from early phases

---

### `opus-analyses/` - Strategic Analysis (Sprint 4 Planning)
Strategic analyses by Claude Opus for Sprint 4 direction.

**Contents:**
- `OPUS_SPRINT4_BRIEF.md` - Strategic brief for production hardening
- `OPUS_RECOMMENDATION.md` - Architectural recommendations
- `OPUS_PROMPT.md` - Analysis prompts used
- `START_HERE_OPUS.md` - Opus context document

**Status:** ✅ **Reference value** - strategic insights still relevant

**Use case:** Understanding high-level architectural decisions, strategic priorities

---

### `research/` - Technical Research
Deep-dive technical research on specific implementation challenges.

**Contents:**
- `plotly-synchronization-research.md` - Multi-timeframe plot sync investigation

**Status:** ✅ **Still relevant** - technical findings applicable to dashboard work

**Use case:** Implementing advanced visualization features

---

### `example-issues/` - Issue Templates
Example GitHub issues demonstrating project workflow.

**Contents:**
- `jupyter-dashboard-issue.md` - Sprint 1 dashboard feature
- `tribal-weather-issue.md` - Future tribal weather feature

**Status:** ✅ **Template reference** - good examples of issue structure

**Use case:** Creating well-structured issues for new features

---

### Other Historical Files

**`CRITICAL_HARDENING_SUMMARY.md`**
- Summary of production hardening work (pre-Sprint 4)
- Status: Historical, superseded by `docs/sprints/sprint-4.md`

**`ORGANIZATIONAL_OVERHAUL_SUMMARY.md`**
- Documentation reorganization (Jan 2, 2026)
- Status: Historical, reflects archive structure creation

**`GITHUB_SETUP_INSTRUCTIONS.md`**
- GitHub workflow setup guide
- Status: Reference (see `.github/WORKFLOW.md` for current)

**`WORKFLOW.md`**
- Original workflow documentation
- Status: Historical (see `.github/WORKFLOW.md` for current)

**`testing_strategy.md`**
- Early testing approach
- Status: Historical (see `CONTRIBUTING.md` for current)

**`QUICK_REFERENCE.md`**
- Quick command reference (outdated)
- Status: Historical (see `CLAUDE.md` for current)

---

## ⚠️ Important Notes

### When to Use Archive

**Use archive docs when:**
- ✅ Understanding project evolution
- ✅ Finding rationale for old architectural decisions
- ✅ Researching technical approaches tried in past
- ✅ Learning from strategic analyses (Opus)

**DO NOT use archive docs for:**
- ❌ Current development guidelines → See `CONTRIBUTING.md`
- ❌ Current project status → See `docs/ISSUES.md`
- ❌ Current deployment → See `deploy/AWS_*.md`
- ❌ Current sprint info → See `docs/sprints/sprint-*.md`

### Archive vs Active Documentation

| Type | Active Location | Archive Location |
|------|----------------|------------------|
| Sprint reports | `docs/sprints/` | N/A (don't archive) |
| Deployment guides | `deploy/` | `archive/legacy/DEPLOYMENT_PLAN.md` |
| AI context | `CLAUDE.md` | `archive/legacy/fractal-trader-context.md` |
| Workflow | `.github/WORKFLOW.md` | `archive/WORKFLOW.md` |
| Testing guide | `CONTRIBUTING.md` | `archive/testing_strategy.md` |

---

## 🗂️ What Was Deleted

As of Jan 10, 2026 cleanup:

**`archive/sprint-planning/`** - DELETED ❌
- Reason: Redundant with `docs/sprints/`
- Files removed: SPRINT_4_PLAN.md, SPRINT_4_CHECKLIST.md, etc.
- Current location: `docs/sprints/sprint-4.md` (consolidated)

---

## 📜 Changelog

**2026-01-10:**
- Deleted redundant `sprint-planning/` (4 files)
- Created this README
- Moved `FraktalnyHandlarz.md` to legacy/ (Polish historical version)

**2026-01-02:**
- Created `archive/` directory structure
- Moved pre-sprint docs to `legacy/`
- Organized by content type

---

*For current project information, always check:*
- **Status:** `docs/ISSUES.md`
- **Roadmap:** `docs/ROADMAP_Q1_2026.md`
- **Current sprint:** `docs/sprints/` (latest)
- **AI context:** `CLAUDE.md`
