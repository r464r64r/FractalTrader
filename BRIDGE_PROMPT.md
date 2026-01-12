# Bridge Prompt: Load Migration Context in New Session

**Use this prompt in VSCode (new Claude Code session) to load full context:**

---

## Full Context Prompt

```
I'm working on FraktAl - a trading platform that recently migrated from FractalTrader.

Context files to read:
1. MIGRATION_PLAN.md - Execution plan (22 milestones, 1770 lines)
2. MIGRATION_CONTEXT.md - Decision rationale and philosophy (831 lines)

Key background:
- Frakt (public, MIT) = SMC trading engine
- FraktAl (private) = Full platform with live bot, API, dashboard
- Migration completed in ~4 hours (AI-assisted)
- Philosophy: Manifest-first, KISS for AUDHD, fractal architecture
- Current status: Repos created, code split, tests passing

Read both context files, then:
1. Show me FraktAl project structure
2. Verify SessionStart hook works
3. Summarize what was migrated and what's next

I'm ready to continue development.
```

---

## Quick Context Prompt (if full load too heavy)

```
I'm working on FraktAl (migrated from FractalTrader).

Key facts:
- Frakt = public engine (MIT), FraktAl = private platform
- Migration plan in MIGRATION_PLAN.md (22 milestones)
- Philosophy: Fractal architecture, KISS, manifest-first
- Embedded tests in manifesto.md enforce principles

Show project structure and current status.
```

---

## Selective Context (if you know what you need)

```
Read MIGRATION_CONTEXT.md section: [pick one]

- "Decision Rationale: The 5 Locked Choices"
- "KISS for AUDHD"
- "Nodes ≠ Hosts"
- "Executable Manifesto"
- "Julia/Mandelbrot Metaphor"

Then help me with: [your specific task]
```

---

## Export Method (Alternative)

If you want to SHOW me conversation history instead of files:

1. Go to this conversation in Claude.ai
2. Look for Export option (if available)
3. Copy relevant parts to a new file: `SESSION_EXPORT.md`
4. In new Claude Code session: "Read SESSION_EXPORT.md"

---

## What Context Files Contain

**MIGRATION_PLAN.md:**
- WHAT to do (execution steps)
- 22 milestones across 4 phases
- Copy-paste ready commands
- Success criteria for each step

**MIGRATION_CONTEXT.md:**
- WHY decisions were made
- Philosophical principles
- KISS/AUDHD design patterns
- Community/multi-language roadmap
- Missing pieces from plan
- Questions to ask yourself

**Together:** Complete picture of migration.

---

## Tips for New Session

1. **SessionStart hook loads automatically** in FraktAl repo
2. **Git history has full migration** (check recent commits)
3. **Both Frakt and FraktAl exist** (GitHub confirmed)
4. **EC2 bot still running** (zero downtime during migration)

---

## If Context Too Large

Claude Code has token limits. If both files too big:

**Priority 1 (must read):**
- MIGRATION_CONTEXT.md: "Core Principles" section
- MIGRATION_CONTEXT.md: "Decision Rationale"

**Priority 2 (skim):**
- MIGRATION_PLAN.md: Phase headers + milestones
- MIGRATION_CONTEXT.md: "Missing Pieces"

**Priority 3 (reference):**
- Full MIGRATION_PLAN.md (1770 lines)
- MIGRATION_CONTEXT.md: Examples and analogies

---

## Verification Commands

Once context loaded, verify migration success:

```bash
# Check repos exist
ls ~/projects/frakt/Frakt
ls ~/projects/fraktal/FraktAl

# Check manifesto
cat ~/projects/frakt/Frakt/manifesto.md | head -50

# Check SessionStart hook
cat ~/projects/fraktal/FraktAl/.claude/hooks/SessionStart.sh

# Run tests (if in Frakt)
cd ~/projects/frakt/Frakt
pytest tests/test_manifesto.py -v
```

Expected output:
- ✅ Both repos exist
- ✅ Manifesto in English (789 lines)
- ✅ SessionStart hook present
- ✅ Manifesto tests pass

---

**Ready to bridge!** 🌉
