# FractalTrader Sprint Framework

## Philosophy: Ship or Die 🚢

**Old way:**
```
"Phase 2 in progress... needs more testing... almost there... 2-3 weeks..."
```

**New way:**
```
Sprint 1 (Dec 24 - Jan 6): Ship Jupyter MVP
Sprint 2 (Jan 7 - Jan 20): Ship Paper Trading
Sprint 3 (Jan 21 - Feb 3): Ship Live Trading (testnet)
```

**Each sprint = 2 weeks = 1 clickable deliverable**

No exceptions. No "almost done". Either shipped or failed.

---

## Sprint Structure

### Duration
- **2 weeks fixed** (10 working days)
- Monday start, Sunday end
- No extensions (cut scope instead)

### Deliverable Types

**Type A: User-facing** (Filip can click)
- Jupyter dashboard
- CLI tool
- Web UI
- Trading bot running

**Type B: Developer-facing** (enables Type A)
- Data pipeline
- Testing framework
- API integration
- Monitoring system

**Every sprint must have at least one Type A or enable next sprint's Type A.**

### Sprint Phases

**Week 1: Build**
- Days 1-3: Design & spike (Opus + Haiku)
- Days 4-7: Implementation (Haiku/Sonnet)

**Week 2: Ship**
- Days 8-9: Integration & testing (Sonnet)
- Day 10: Deploy & document
- **End of day 10: Demo or die**

---

## Sprint Roles

### Product Owner (Filip)
- Defines "what" (desired outcome)
- Validates deliverable end of sprint
- Can cut scope mid-sprint
- **Cannot extend sprint**

### Tech Lead (Opus)
- Defines "how" (technical approach)
- Breaks down to tasks (Day 1)
- Unblocks team
- **Accountable for delivery**

### Developers (Haiku/Sonnet)
- Implement tasks
- Communicate blockers daily
- No scope creep
- **Ship on time or explain why**

---

## Sprint Planning (Day 0)

### Input
- Product backlog (GitHub issues)
- Previous sprint retro
- Team capacity (realistic)

### Output
- **Sprint Goal** (one sentence)
- **Deliverable** (specific, demoable)
- **Tasks** (GitHub issues, labeled `sprint-N`)
- **Success criteria** (checkbox list)
- **Risk mitigation** (what could fail?)

### Template

```markdown
# Sprint N: [Name]

**Duration:** Dec 24 - Jan 6, 2025  
**Goal:** [One sentence describing outcome]

## Deliverable

[Specific thing Filip can interact with]

Example: "Jupyter notebook that loads BTC data, runs liquidity sweep strategy, 
shows multi-timeframe chart with SMC overlay, displays confidence breakdown."

## Success Criteria

- [ ] Criterion 1 (must have)
- [ ] Criterion 2 (must have)
- [ ] Criterion 3 (must have)
- [ ] Criterion 4 (nice to have)

## Tasks

- [ ] #123 Task 1 (Haiku, 2d)
- [ ] #124 Task 2 (Sonnet, 3d)
- [ ] #125 Task 3 (Haiku, 2d)

## Risks

- **Risk 1:** Plotly performance with live data
  - Mitigation: Use cached data for MVP
  
- **Risk 2:** SMC overlay rendering complexity
  - Mitigation: Start with order blocks only

## Out of Scope

(Explicitly list what we're NOT doing this sprint)

- Real-time updates (next sprint)
- Multiple pairs (next sprint)
- Advanced confidence tuning (future)
```

---

## Sprint Execution

### Daily Sync (Async, GitHub)

Each agent comments on sprint issue:

```
Day N update:
- Completed: #123 ✅
- In progress: #124 (60% done)
- Blocked: None
- ETA: On track / At risk / Delayed
```

**No meetings.** Just GitHub comments. 5 min max.

### Mid-Sprint Check (Day 5)

**Question:** "Will we ship on time?"

**If NO:**
1. **Cut scope** (move nice-to-haves to next sprint)
2. **Reallocate** (Sonnet helps Haiku if needed)
3. **Escalate** (Filip decides: ship partial or abort)

**DO NOT extend sprint.**

### End of Sprint (Day 10)

**Morning:** Final integration, docs, deploy  
**Evening:** Demo + Retrospective

#### Demo

Filip tests deliverable:
- ✅ Works as expected → Sprint success
- ⚠️ Works partially → Partial success (note gaps)
- ❌ Doesn't work → Sprint failure

**Record outcome in sprint issue.**

#### Retrospective

```markdown
## Sprint N Retrospective

### What went well?
- 
- 

### What went wrong?
- 
- 

### What to improve next sprint?
- 
- 

### Metrics
- Planned tasks: X
- Completed tasks: Y
- Sprint goal achieved: Yes/Partial/No
- Deliverable shipped: Yes/No
```

**10 minutes. No blame. Just learn.**

---

## Sprint Backlog Management

### Backlog Grooming (Continuous)

Opus maintains backlog:
- Breaks down epics into sprint-sized chunks
- Estimates effort (S/M/L)
- Prioritizes by value + dependencies
- Keeps top 3 sprints planned ahead

### Sprint Commitment

**Only commit what team can finish in 2 weeks.**

**Better:** Ship small feature fully  
**Worse:** Half-finish large feature

### Velocity Tracking

After 3 sprints, we know our velocity:
- Sprint 1: Completed 5 tasks (15 points)
- Sprint 2: Completed 4 tasks (12 points)
- Sprint 3: Completed 6 tasks (18 points)
- **Average velocity:** 15 points/sprint

**Use this to plan future sprints realistically.**

---

## Release Cadence

### Sprint Release (Every 2 weeks)

- Tag: `vX.Y.0-sprint-N`
- Branch: `release/sprint-N`
- Changelog: What shipped this sprint
- **Always releasable** (even if small)

### Production Release (Every 4-6 weeks)

- Tag: `vX.Y.0`
- Branch: `release/vX.Y`
- Combines 2-3 sprint releases
- Full QA, migration guide
- **Ready for real usage**

### Hotfix (As needed)

- Branch: `hotfix/issue-description`
- Fix critical bugs in production
- Cherry-pick to main + release branch

---

## Branch Strategy

### Main Branches

```
main            - Stable, always deployable
develop         - Integration branch for current sprint
release/vX.Y    - Production releases
```

### Sprint Branches

```
sprint/N-sprint-name     - Sprint integration branch
feature/issue-123-desc   - Individual features
hotfix/critical-bug      - Emergency fixes
```

### Workflow

```
1. Sprint starts → create sprint/N branch from develop
2. Features → branch from sprint/N
3. Features done → PR to sprint/N
4. Sprint ends → PR sprint/N to develop
5. Release → merge develop to main, tag
```

**Main branch = only working code, always.**

---

## Anti-Patterns to Avoid

❌ **"Almost done"** - Either done or not, no middle  
❌ **Scope creep** - Lock scope after Day 1  
❌ **Extending sprint** - Cut scope instead  
❌ **Working on multiple sprints** - Finish current first  
❌ **Skipping demo** - No demo = didn't happen  
❌ **Ignoring retrospective** - How will you improve?  

---

## Success Metrics

**Sprint Level:**
- Goal achieved: Yes/Partial/No
- Deliverable shipped: Yes/No
- Tasks completed: X/Y (%)
- On-time delivery: Yes/No

**Project Level:**
- Sprints on-time: X/Y (target >80%)
- Features shipped: X total
- User satisfaction: Filip's rating 1-10
- Velocity trend: Stable/Growing/Declining

---

## Example: First Sprint

```markdown
# Sprint 1: Jupyter Fractal Viewer

**Duration:** Dec 24, 2024 - Jan 6, 2025  
**Goal:** Filip can analyze BTC trades in Jupyter with SMC overlay

## Deliverable

Jupyter notebook that:
1. Loads 90d BTC/USDT 1h data
2. Shows 3-panel view (H4/H1/M15)
3. Overlays order blocks on charts
4. Displays confidence breakdown for one example trade

## Success Criteria

- [ ] Notebook runs without errors
- [ ] Charts are interactive (zoom, pan)
- [ ] Order blocks visible and labeled
- [ ] Confidence panel shows breakdown
- [ ] Documentation: README with screenshots

## Tasks

- [ ] #150 Research: Plotly multi-subplot sync (Haiku, 1d)
- [ ] #151 Implement: FractalDashboard class (Haiku, 2d)
- [ ] #152 Implement: Order block overlay (Sonnet, 2d)
- [ ] #153 Implement: Confidence panel (Haiku, 1d)
- [ ] #154 Integration: Example notebook (Sonnet, 2d)
- [ ] #155 Documentation: Usage guide (Haiku, 1d)

## Risks

- Plotly performance → Mitigation: Static data, no live updates
- Complexity → Mitigation: OB only, skip FVG/sweeps for MVP

## Out of Scope

- Live data updates (Sprint 2)
- Multiple pairs (Sprint 2)
- FVG/sweep overlays (Sprint 3)
- Confidence tuning (Sprint 4)
```

---

## Why This Works

### For Filip
- **Predictable:** New toy every 2 weeks
- **Transparent:** Know exactly what's coming
- **Empowering:** Can cut scope, prioritize

### For Team
- **Focused:** 2-week horizon, clear goal
- **Sustainable:** No crunch, realistic planning
- **Learning:** Retro every sprint improves process

### For Project
- **Momentum:** Ship regularly, build confidence
- **Flexibility:** Pivot every 2 weeks if needed
- **Quality:** Always releasable, always tested

---

## Transition Plan

### Current State → Sprint 1

**This week (Dec 24-29):**
1. ✅ Setup GitHub workflow (done!)
2. 🔨 Create Sprint 1 plan (Opus, Day 0)
3. 🔨 Break down to tasks (Opus, Day 1)
4. 🚀 Start Sprint 1 (Haiku/Sonnet, Day 2)

**Sprint 1 Goal:** Jupyter Fractal Viewer  
**Sprint 1 End:** Jan 6, 2025  
**Demo:** Filip plays with notebook, rates experience

---

**No more "soon". No more "almost". No more "2-3 weeks".**

**Ship. Learn. Iterate. Repeat.**

🚢 or 💀
