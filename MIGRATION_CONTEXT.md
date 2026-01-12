# FractalTrader → Frakt/FraktAl: Decision Context

**Companion to:** `MIGRATION_PLAN.md`
**Purpose:** WHY we made decisions, not just WHAT to do
**Created:** 2026-01-11 (22-hour marathon session)
**Status:** Context preservation for future sessions

---

## Executive Summary: The Conversation

This migration wasn't just code reorganization. It was **philosophical alignment**:

> "Manifest-first development. KISS for AUDHD. Fractal structure at every scale. Ship or die."

The MIGRATION_PLAN.md tells you **what** to execute.
This document tells you **why** we designed it this way.

---

## Key Design Philosophy

### 1. **Fraktalna Architektura** (Fractal Structure)

**Manifest says:**
> "H4 → H1 → M15: the same pattern on every timeframe"

**We applied this to infrastructure:**

```
Trading Strategy (code level):
├─ Entry signal (BOS detection)
├─ Position size (risk calc)
└─ Exit signal (retest confirmation)

Development Workflow (process level):
├─ Entry (git commit)
├─ Position size (which milestone)
└─ Exit (merge to main)

Node Architecture (infrastructure level):
├─ Entry (pull code/data)
├─ Compute (backtest/live/dev)
└─ Exit (publish results)
```

**Key insight:** If the pattern works at one scale, it should work at ALL scales.

**Implication:** When designing new features, ask: "Is this fractal? Does it repeat across layers?"

---

### 2. **Warsztat vs Samochód** (Workshop vs Car)

**Problem:** Original FractalTrader mixed **engine** (trading core) with **tools** (dev infrastructure).

**Decision:**
- **Frakt** = Engine (MIT, public) — the car
- **FraktAl** = Workshop (proprietary, private) — the tools to build/maintain the car

**Boundary rule:**
```python
# Frakt (public): Algorithms, no execution
def generate_signal(ohlcv) -> Signal:
    """Returns signal with confidence. No API calls, no secrets."""
    pass

# FraktAl (private): Execution, infrastructure
from frakt import generate_signal
signal = generate_signal(data)
if signal.confidence > 0.8:
    exchange.place_order(...)  # Business logic, secrets
```

**Why this matters:**
- Community can improve Frakt (engine) without accessing your IP (FraktAl platform)
- You can swap engines (Frakt v2) without rewriting infrastructure
- Clear licensing (MIT vs proprietary)

**Analogy:** Tesla open-sources battery patents (Frakt), but keeps factory automation (FraktAl) proprietary.

---

### 3. **Manifest as Executable Constitution**

**Initial idea:**
> "Let's translate manifesto to English and put it in Frakt."

**Evolution:**
> "What if manifesto had EMBEDDED TESTS? CI would enforce philosophy!"

**Result:**
```markdown
## Principle: No Lagging Indicators

We do NOT use RSI, MACD, Bollinger Bands.

<!-- TEST:
import inspect
from frakt.strategies import *

forbidden = ['rsi', 'macd', 'bollinger']
for strategy in [LiquiditySweep, FVG, Breakout]:
    source = inspect.getsource(strategy).lower()
    for term in forbidden:
        assert term not in source, f"{strategy} violates manifesto!"
-->
```

**Why brilliant:**
1. **Philosophy becomes enforceable** (not just aspirational)
2. **CI blocks PRs** that violate principles
3. **Contributors can't accidentally add lagging indicators**
4. **Integrates with Jupyter** (notebooks can validate compliance too)

**Future extension:**
- Manifesto tests for fractal structure (same logic across timeframes)
- Manifesto tests for liquidity-first approach (order flow validation)
- Auto-generate compliance reports (weekly: "Are we living the manifesto?")

---

### 4. **KISS for AUDHD** (Simplicity as Design Constraint)

**Your context:**
> "Mam AUDHD i KISS to wybawienie. Chaos jest twórczy a strukturyzacja mierzalna."

**Design implications:**

#### **Chaos → Structure Pipeline**
```
Ideas (chaotic)
    ↓
GitHub Issues (semi-structured)
    ↓
TodoWrite (structured tasks)
    ↓
MIGRATION_PLAN.md (executable)
    ↓
Code (measured results)
```

**Each step adds structure, never removes creativity.**

#### **Mierzalność** (Measurability)
Every milestone has **Success Criteria:**
```
- [ ] Tests pass
- [ ] Coverage > 70%
- [ ] API responds < 100ms
```

**NOT:**
```
- [ ] Code is good
- [ ] System works well
```

Vague = unmeasurable = ADHD hell.
Specific = checkable = KISS heaven.

#### **Single Source of Truth**
- Manifest = philosophy
- ISSUES.md = current status
- MIGRATION_PLAN.md = execution plan

**NOT:** 9 docs that might contradict each other.

---

### 5. **Nodes ≠ Hosts** (Portability First)

**Original assumption:**
> "Laptop is dev, EC2 is production."

**Correction:**
> "Nodes are containers + repos. Hosts are just where they run."

**Why this matters:**

```
Today:
├─ Laptop (dev + backtest)
├─ EC2 Tokyo (live testnet)

Tomorrow:
├─ Laptop (backtest only)
├─ Homelab strychu (dev + staging)
├─ EC2 Tokyo (live testnet)
├─ EC2 Oregon (historical backtest node)

Next year:
├─ Laptop (offline)
├─ Kubernetes cluster (all nodes, auto-scaling)
```

**Same containers. Different hosts. Zero rewrite.**

**Implementation:**
- `docker-compose.yml` — portable
- `fractal` CLI — auto-detects node
- Shared volumes — data flows between nodes

**Anti-pattern:** Hardcoding IPs, hostnames, "if on EC2 then..."

---

### 6. **Public Data Strategy** (Trust Through Transparency)

**Question:** What do we show on public dashboard?

**Decision: BOTH link + stats**

**Link (external verification):**
```markdown
**Wallet:** [0xf7ab...5403](https://app.hyperliquid-testnet.xyz/account/0xf7ab...)

Users can verify trades independently (trustless).
```

**Stats (UX convenience):**
```json
{
  "uptime": "4d 18h",
  "trades": 52,
  "equity": 10234.56,
  "win_rate": 0.58
}
```

Users see overview without leaving dashboard (UX).

**What we DON'T show:**
- Strategy parameters (entry thresholds, stop loss %)
- Failed signal attempts (only successful trades)
- Internal metrics (CPU, memory, error rates)
- API keys, secrets (obviously)

**Principle:** Transparency for verification, opacity for IP protection.

---

### 7. **Ship or Die** (Time-Boxing as Forcing Function)

**Your observation:**
> "Takie precyzyjne plany przelatują 3× szybciej niż się wydaje. Najbardziej czasochłonne jest samo planowanie."

**Our agreement:**
> "Days" = token-units (relative effort), not calendar time.

**Why this works:**

| Traditional | Our Approach |
|-------------|--------------|
| "This will take 2 weeks" | "This is 3 day-tokens of effort" |
| Deadline slips → guilt | Faster execution → celebration |
| Planning = overhead | Planning = artifact (reusable) |

**Forcing function:**
> "If we don't ship Phase 1 by [arbitrary date], we'll lose momentum."

This creates urgency without stress (because "days" are flexible).

**Result:** 22 "days" executed in ~4 hours AI-assisted.

---

## What Wasn't in MIGRATION_PLAN.md

### 1. **Multi-Language Documentation Roadmap**

**Long-term vision:**
```
frakt.al (main site)
├─ en.frakt.al (English)
├─ pl.frakt.al (Polish)
├─ jp.frakt.al (Japanese)
├─ cn.frakt.al (Chinese)
├─ in.frakt.al (Hindi/Indian English)
├─ uk.frakt.al, au.frakt.al (localized English)
```

**Why:** Crypto is global. SMC principles are universal. Manifest should be accessible.

**Implementation (future):**
- Manifesto translations (community-contributed)
- Localized dashboards (number formats, timezones)
- Regional node selection (JP for Asia, US for Americas)

---

### 2. **Homelab Strychu Node**

**Context:**
> "Za tydzień na homelab na strychu... na razie nie mamy kosztów, jedziemy na odpadkach i scavenging."

**Planned role:**
- Dev environment (staging before EC2)
- Backtest node (offload from laptop)
- Redundancy (if EC2 fails)

**Setup:**
```bash
# On homelab hardware:
docker-compose up -d
fractal deploy --node homelab

# Auto-registers with FraktAl network
# Same containers as laptop/EC2
```

**Node discovery:**
```yaml
# nodes/registry.yml
nodes:
  - name: laptop-dev
    role: development
    ip: local
  - name: ec2-tokyo
    role: production-testnet
    ip: 54.199.8.26
  - name: homelab-strychu
    role: staging-backtest
    ip: 192.168.1.100  # local network
```

---

### 3. **Kubernetes Migration Path**

**Current:** docker-compose (sufficient for 2-3 nodes)

**Future (SaaS scale):**
```
Kubernetes cluster (frakt.al):
├─ Frakt engine pods (stateless, scalable)
├─ FraktAl API pods (stateful, auto-scaling)
├─ Dashboard ingress (load balanced)
└─ Backtest workers (batch jobs, spot instances)
```

**Migration strategy:**
1. Convert `docker-compose.yml` → Kubernetes manifests
2. Helm chart for FraktAl (easy deployment)
3. Horizontal scaling (more users → more pods)

**Bridge:** docker-compose is Kubernetes-compatible (same concepts: services, volumes, networks).

---

### 4. **Community Engagement Plan**

**Frakt is opensource, but how do we GET contributors?**

**Phase 1: Seed Community** (Months 1-3)
- Write "CONTRIBUTING.md" (how to add strategies)
- Create "good first issue" labels
- Discord/Telegram for real-time help
- Bounties for new features (e.g., "$100 for Binance exchange wrapper")

**Phase 2: Showcase** (Months 3-6)
- Publish weekly backtest reports (Jupyter → HTML)
- Tweet "Frakt beat [retail strategy] by 40% this week"
- Case study: "How we built SMC bot in Python"

**Phase 3: Ecosystem** (Months 6-12)
- Plugin marketplace (community strategies)
- Paper competitions (best strategy wins prize)
- Conferences (present at Python/trading meetups)

**Goal:** Self-sustaining community improving Frakt engine.

---

### 5. **Zbiór Julii vs Mandelbrota** (Fractal Metaphor)

**Your beautiful analogy:**
> "Pomału wyodrębniamy zbiór Julii (MIT) i nasz zbiór Mandelbrota."

**Meaning:**
- **Julia set (Frakt):** Simpler, self-contained, beautiful on its own. Open to everyone.
- **Mandelbrot set (FraktAl):** Complex, contains all Julias, our private masterpiece.

**Design principle:**
Every feature in FraktAl should ask:
> "Is this Julia (belongs in public engine) or Mandelbrot (stays in private platform)?"

Examples:
- BOS detection algorithm → Julia (Frakt)
- Position sizing → Julia (Frakt)
- Hyperliquid API wrapper → Julia (Frakt)
- Live bot orchestration → Mandelbrot (FraktAl)
- Dashboard authentication → Mandelbrot (FraktAl)
- Internal analytics → Mandelbrot (FraktAl)

**Rule of thumb:** If a solo dev could use it independently → Julia. If it needs our infrastructure → Mandelbrot.

---

### 6. **What NOT to Do** (iPhone Chapter Lessons)

**Context:**
> "iPhone development chapter — wstyd wspominać, na razie zamknijmy ten rozdział."

**Lesson (implied):** Something didn't work on iPhone. What was it?

**Guesses:**
- Mobile development too constrained? (small screen, limited tools)
- SSH from iPhone to EC2 fragile? (network issues)
- Termux/iSH not production-ready? (unstable environments)

**Principle to preserve:**
> "Don't force tools into contexts where they fail. iPhone = monitoring OK, development NO."

**Applied to future:**
- Mobile dashboard (view-only) → YES
- Mobile code editing → NO (use laptop/homelab)
- Mobile emergency stop (via API) → MAYBE (with safeguards)

---

### 7. **Branch Naming Convention** (CI Optimization)

**Discussed but not in plan:**

```
Branch naming → CI behavior:
├─ claude/exp-*        → Skip CI, auto-delete after 7d
├─ claude/prod-*       → Full CI, require review
├─ feature/*           → Full tests, auto-merge if green
├─ fix/*               → Tests + hotfix deploy
```

**Why:**
- Experiments are throwaway (don't waste CI minutes)
- Production changes need scrutiny
- Clear signal in branch name (not just commit message)

**Implementation:**
```yaml
# .github/workflows/ci.yml
on:
  push:
    branches-ignore:
      - 'claude/exp-*'  # Skip experimental branches
```

---

### 8. **Token-Based Metrics** (Why "Days" Aren't Time)

**Your insight:**
> "Days jako umowną miarę skali wyzwania jako zamiennik tokenów."

**Meaning:**
- 1 "day" ≈ complexity/effort, not 8 hours of work
- 22 "days" in plan = 22 units of effort, could be 4 hours or 4 weeks

**Why this is profound:**

Traditional estimation:
> "This will take 2 weeks."
> (Feels like a deadline, creates pressure)

Token-based:
> "This is 10 day-tokens."
> (Feels like a score, creates game-like motivation)

**Application:**
- Estimate features in tokens (not hours)
- Track velocity (tokens completed per session)
- No guilt if tokens take longer (focus on completion, not speed)

---

## Decision Rationale: The 5 Locked Choices

### Decision 1: Exchange Integration Split

**Options:**
- A: Generic wrapper in Frakt (extensible)
- B: All execution in FraktAl (simpler)
- C: Split (wrapper in Frakt, credentials in FraktAl)

**Chose: A (Generic wrapper in Frakt)**

**Why:**
1. **Community can add exchanges** (Binance, Coinbase, dYdX)
2. **Frakt stays exchange-agnostic** (not tied to Hyperliquid)
3. **Testing easier** (mock exchange in Frakt, no real API needed)

**Trade-off:** More abstraction (learning curve for contributors).

**Future-proofing:** When mainnet launches, we swap credentials (FraktAl) but keep wrapper (Frakt).

---

### Decision 2: Executable Manifesto

**Options:**
- YES: Embedded tests in `manifesto.md`
- NO: Manifesto is philosophy only

**Chose: YES (Brilliant!)**

**Why:**
1. **Philosophy becomes enforceable** (CI blocks violators)
2. **Living document** (tests evolve with codebase)
3. **Educational** (new contributors see tests, understand principles)
4. **Jupyter integration** (notebooks validate compliance)

**Trade-off:** Manifesto is now code (requires maintenance).

**Payoff:** Zero drift between philosophy and implementation.

---

### Decision 3: Public Data Display

**Options:**
- Link only (external verification)
- Embed only (inline stats)
- Both (link + stats)

**Chose: Both**

**Why:**
1. **Trust:** Link to Hyperliquid (users verify trades independently)
2. **UX:** Stats in dashboard (don't force users to leave site)
3. **Marketing:** Good stats attract users, link proves legitimacy

**Implementation:**
```javascript
// Dashboard
<a href="https://hyperliquid.xyz/account/0xf7ab...">
  Wallet: 0xf7ab...5403
</a>
<div>
  Trades: {stats.trades} | P&L: +{stats.pnl}%
</div>
```

---

### Decision 4: Issue Migration

**Options:**
- A: Transfer to new repos (GitHub transfer feature)
- B: Close with comment ("Migrated to Frakt#123")
- C: Archive (leave in FractalTrader read-only)

**Chose: A (Transfer)**

**Why:**
1. **Preserves history** (issue discussions valuable)
2. **Maintains links** (external references still work)
3. **Clean separation** (core issues → Frakt, live issues → FraktAl)

**Process:**
```bash
gh issue transfer 42 --repo r464r64r/Frakt
# OR
gh issue close 42 --comment "Migrated to Frakt#15"
```

---

### Decision 5: Container Layering

**Options:**
- A: Multi-stage Dockerfile (Frakt base layer)
- B: docker-compose (separate images)
- C: Monorepo (everything in one image)

**Chose: B (docker-compose)**

**Why:**
1. **Clean separation** (Frakt testable independently)
2. **Caching** (Frakt layer rebuilds rarely, FraktAl often)
3. **Kubernetes-ready** (docker-compose translates easily)

**Setup:**
```yaml
services:
  frakt:
    image: ghcr.io/r464r64r/frakt:latest
  fraktal:
    build: .
    depends_on: [frakt]
```

**Trade-off:** Two images to maintain (vs one monolith).

**Payoff:** Frakt updates don't require FraktAl rebuild.

---

## Missing Pieces: What to Add Next

### 1. **ADR for Each Decision**

Create `docs/decisions/`:
```
0001-exchange-wrapper-in-frakt.md
0002-executable-manifesto-tests.md
0003-public-data-both-link-and-stats.md
0004-github-issue-transfer-strategy.md
0005-docker-compose-over-monorepo.md
```

Each ADR:
- Context (what problem)
- Options considered
- Decision + rationale
- Consequences (trade-offs)

---

### 2. **SessionStart Hook Expansion**

Current hook shows:
- Git status
- Bot status
- Current sprint

**Add:**
- Recent issues (last 3 opened)
- CI status (last workflow run)
- Manifesto compliance score (% tests passing)

---

### 3. **Fractal CLI Shortcuts**

```bash
fractal status           # Already exists
fractal test             # Run pytest
fractal manifest         # Check compliance
fractal deploy           # Deploy to current node
fractal backtest <strat> # Run backtest
fractal compare <s1> <s2> # Compare strategies
```

Each command: same interface, different backends (local/EC2/homelab).

---

### 4. **Community Onboarding Guide**

**File:** `CONTRIBUTING.md` in Frakt

```markdown
# Contributing to Frakt

## Quick Start
1. Fork repo
2. Add your strategy in `strategies/my_strategy.py`
3. Tests in `tests/test_my_strategy.py`
4. Run: `pytest tests/` (must pass)
5. Run: `pytest tests/test_manifesto.py` (compliance check)
6. Open PR

## What We Accept
✅ New SMC strategies (BOS, FVG, liquidity sweeps)
✅ Exchange wrappers (Binance, Coinbase, etc.)
✅ Backtesting improvements
❌ Lagging indicators (violates manifesto)
❌ Execution logic (belongs in FraktAl, private)

## Bounties
Check Issues labeled "bounty" for paid tasks.
```

---

### 5. **Kubernetes Helm Chart** (Future)

```bash
# fraktal-helm/
├── Chart.yaml
├── values.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    └── ingress.yaml

# Deploy:
helm install fraktal ./fraktal-helm
```

Enables one-command SaaS deployment.

---

## Philosophical Continuity

### How to Keep Manifest Alive

**Anti-pattern:**
> "We wrote manifesto, now let's forget it and build."

**Correct pattern:**
> "Every feature asks: Is this aligned with manifesto?"

**Weekly ritual:**
1. Run `pytest tests/test_manifesto.py`
2. Review failures: "Why did this violate principles?"
3. Either fix code OR update manifesto (philosophy evolves)

**Monthly ritual:**
1. Read manifesto aloud (seriously)
2. Discuss: "Are we living these principles?"
3. Update if needed (living document)

---

### KISS as North Star

**Every new feature:**
> "Can this be simpler? What's the KISS version?"

**Examples:**

| Complex | KISS |
|---------|------|
| Microservices (5 services) | Monolith (1 service, multiple processes) |
| Custom protocol | HTTP + JSON |
| Database (PostgreSQL) | JSON files + filelock |
| Message queue (RabbitMQ) | Shared volume |

**Rule:** Only add complexity when KISS breaks (measured, not assumed).

---

### Ship or Die Rhythm

**Weekly shipments:**
- Week 1: Feature X → merge to main
- Week 2: Feature Y → deploy to EC2
- Week 3: Feature Z → public demo

**No multi-month epics.** Every week: something ships.

**How:**
- Break features into 1-week chunks
- Use feature flags (ship incomplete, enable later)
- Parallel work (2 features at once)

---

## Export Instructions

### How to Load This Context in New Session

**Option 1: Read File**
```
I'm continuing work on FraktAl (migrated from FractalTrader).

Read ~/projects/fraktal/FraktAl/MIGRATION_CONTEXT.md for philosophical context and decision rationale.

Then show me current project status and what's next.
```

**Option 2: Inline Context**
Paste key sections (this file) directly into prompt.

**Option 3: ADRs**
Convert sections to individual ADRs:
```bash
cp MIGRATION_CONTEXT.md docs/decisions/context-from-migration.md
```

---

## Quick Reference

### Core Principles (Memorize These)

1. **Fractal:** Same pattern at every scale
2. **KISS:** Simplicity beats cleverness
3. **Manifest-first:** Philosophy before features
4. **Ship or die:** Weekly shipments, no epics
5. **Julia/Mandelbrot:** Public engine, private platform
6. **Nodes ≠ Hosts:** Portability über alles
7. **Measurable:** Vague is chaos, specific is structure

### Questions to Ask

**Before adding feature:**
- Is this Julia (Frakt) or Mandelbrot (FraktAl)?
- Does it violate manifesto?
- What's the KISS version?
- Can we ship this in <1 week?

**During development:**
- Are success criteria clear?
- Is this fractal (repeats across layers)?
- Would AUDHD-me understand this in 3 months?

**Before merge:**
- Do manifesto tests pass?
- Is documentation updated?
- Can community reproduce this?

---

## Final Wisdom

**From the 22-hour marathon:**

> "Plany przelatują 3× szybciej niż się wydaje. Najbardziej czasochłonne jest samo planowanie."

**Translation:**
> "Execution is fast. Planning is slow. But good plans make execution trivial."

**Application:**
Spend 20% time planning (this doc, MIGRATION_PLAN.md).
Spend 80% time executing (copy-paste commands, iterate).

**Result:**
22 "days" of work in 4 hours real time.

---

**END OF CONTEXT**

This document is your **memory** of the conversation.
MIGRATION_PLAN.md is your **action list**.
Together: complete picture.

🌀 Ship or die. 🚀
