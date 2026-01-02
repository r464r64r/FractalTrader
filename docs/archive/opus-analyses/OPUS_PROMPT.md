# Prompt for Opus: Sprint 4 Development Strategy

Copy this entire prompt to Opus:

---

## Context

I'm Filip, working on **FractalTrader** - an SMC-based algorithmic trading system for crypto. We're in **Sprint 4** (Production Hardening), currently **21 days ahead of schedule** across 3 completed sprints.

**Current Situation:**
- My workstation is offline (under scrutiny)
- Perfect timing for quality-focused development (no deployment pressure)
- Strategy test coverage just improved: **13-42% → 70%+** (83 new tests)
- Production readiness: **85%** → Target: **95%+**

**Branch:** `claude/analyze-project-docs-tAD4b`

---

## What Just Happened

Sonnet completed comprehensive documentation analysis and strategy test improvements:

**Completed ✅:**
1. Analyzed all 41 project MD files
2. Created Sprint 4 planning docs (3 files, 1400+ lines)
3. Added 83 comprehensive strategy tests:
   - Liquidity Sweep: 24 → 62 tests (13% → 70%+ coverage)
   - BOS Order Block: 30 → 57 tests (42% → 70%+ coverage)
   - FVG Fill: 15 → 33 tests (~40% → 70%+ coverage)

**Result:** Strategy testing is now production-ready. Core logic was already 95-100% tested.

---

## Sprint 4 Remaining Tasks (Before Testnet)

**CRITICAL (Priority 1):**
2. E2E Integration Tests (6-8h) - Full trading loop validation
3. Portfolio-Level Risk Controls (6-8h) - Prevent over-concentration
4. 7-Day Testnet Validation (1h + monitoring) - Prove stability
5. Monitoring Dashboard (8-10h) - Real-time observability

**HIGH (Priority 2):**
6. Disaster Recovery (3-4h) - Incident response playbooks
7. Walk-Forward Validation (6-8h) - Strategy robustness

---

## Your Mission

**Before we start the 7-day testnet validation**, I want to maximize code quality and production readiness through smart development choices.

**Available Time:** 10-16 hours (while I'm doing research + setting up virtual test station)

**Your Tasks:**

### 1. Codebase Analysis
Read the comprehensive brief in `docs/OPUS_SPRINT4_BRIEF.md` (it contains EVERYTHING you need to know):
- Project architecture
- Sprint history
- Current state
- Known issues
- Development opportunities (4 categories)

### 2. Strategic Recommendation

Answer this question:

> **"What development work should we prioritize NOW to maximize production readiness and long-term code quality?"**

Consider these options (or propose your own):

**Option A: Code Quality Sprint (8-12h)**
- Refactor duplicate strategy code
- Add type safety improvements
- Add strategy parameter validation
- Fix critical issues (race conditions, rate limiting, error handling)

**Option B: Performance Sprint (10-14h)**
- Vectorize SMC detection (10-100x faster)
- Add caching for intermediate results
- Memory profiling & optimization

**Option C: Feature Sprint (12-16h)**
- Multi-timeframe confidence aggregation (HTF context)
- Advanced order types (limit, stop-limit)
- Strategy ensemble (multiple strategies)

**Option D: Balanced Sprint (10-12h)**
- Mix of quality improvements + critical fixes + 1 feature
- Refactor code + fix bugs + HTF confidence + CI/CD

### 3. Provide Action Plan

For your chosen approach:
- List specific tasks (in order)
- Time estimates per task
- Risk assessment
- Testing strategy
- Expected impact on production readiness

---

## Constraints

**Must:**
- All existing tests pass (350+ tests)
- No breaking changes to CLI or state file format
- Every change must have tests
- Coverage must not decrease

**Context:**
- Read the brief: `docs/OPUS_SPRINT4_BRIEF.md`
- Check recent work: `git log --oneline -5`
- Review test improvements: `tests/test_strategies.py` (lines 783-2072)

---

## Success Criteria

Your recommendation is successful if it:
1. ✅ Identifies 2-3 highest-leverage improvements (clear ROI)
2. ✅ Provides concrete action plan (tasks, order, estimates)
3. ✅ Justifies choices (why these, why now, what impact)
4. ✅ Considers Sprint 4 context (production hardening)
5. ✅ Aligns with philosophy ("Ship or Die", quality > speed)

---

## What I Need From You

**Format:**

```markdown
## Recommendation: [Option X or Custom]

### Why This Approach
[1-2 paragraphs explaining your reasoning]

### Proposed Tasks
1. [Task name] (Xh)
   - What: [brief description]
   - Why: [value/impact]
   - Risk: [low/medium/high + mitigation]

2. [Next task] (Xh)
   ...

### Expected Outcomes
- Production readiness: 85% → [X]%
- [Other metrics]
- [Long-term benefits]

### Implementation Notes
[Any gotchas, testing strategies, sequencing considerations]

### Alternative Considered
[Brief mention of what you didn't choose and why]
```

---

## Key Question

> "If you had 10-16 hours to improve FractalTrader before putting it through a 7-day testnet validation, what would you focus on to maximize confidence that it won't lose real money in Sprint 6?"

**Let's make this bulletproof.** 🛡️
