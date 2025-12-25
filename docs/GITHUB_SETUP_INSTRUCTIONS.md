# GitHub Workflow Setup Instructions

## What We Created

A complete GitHub workflow system for AI-native development:

```
.github/
├── ISSUE_TEMPLATE/
│   ├── feature-idea.md           # For Filip's sparks
│   ├── research-task.md           # For Haiku's research
│   └── implementation-task.md     # For Haiku/Sonnet code work
├── WORKFLOW.md                    # Complete process documentation
├── PROJECT_BOARD.md               # GitHub Projects setup guide
└── labels.md                      # Label system reference

docs/
├── FILIP_QUICKSTART.md            # Quick start for Filip
└── example-issues/
    ├── jupyter-dashboard-issue.md # Ready to submit
    └── tribal-weather-issue.md    # Ready to submit
```

## Installation (5 minutes)

### Step 1: Copy Files to Your Repo

```bash
# From your FractalTrader repo root:
cd /path/to/FractalTrader

# Copy .github directory
mkdir -p .github/ISSUE_TEMPLATE
cp /path/to/these/files/.github/ISSUE_TEMPLATE/* .github/ISSUE_TEMPLATE/
cp /path/to/these/files/.github/*.md .github/

# Copy docs
mkdir -p docs/example-issues
cp /path/to/these/files/docs/FILIP_QUICKSTART.md docs/
cp /path/to/these/files/docs/example-issues/* docs/example-issues/
```

### Step 2: Commit to Repo

```bash
git add .github/ docs/
git commit -m "Add GitHub workflow system for AI-native development

- Issue templates for ideas, research, and implementation
- Workflow documentation (KISS process)
- Project board setup guide
- Label system
- Quick start guide for Filip
- Example issues (Jupyter dashboard, Tribal weather)
"
git push origin main
```

### Step 3: Set Up GitHub Labels

**On GitHub website:**

1. Go to: https://github.com/r464r64r/FractalTrader/labels
2. Create labels from `.github/labels.md`:

```
Lifecycle:
- idea (purple #7B68EE)
- needs-analysis (yellow #FFD700)
- research (blue #4169E1)
- implementation (green #32CD32)
- review (orange #FF8C00)
- done (gray #696969)

Agents:
- opus-task (red #DC143C)
- sonnet-task (cyan #00CED1)
- haiku-task (pink #FF69B4)

Features:
- feature/smc (blue)
- feature/strategies (blue)
- feature/risk (blue)
- feature/backtest (blue)
- feature/live (blue)
- feature/data (blue)
- feature/ui (blue)
- feature/tribal (blue)
- feature/mcp (blue)

Priority:
- priority/critical (red)
- priority/high (orange)
- priority/medium (yellow)
- priority/low (gray)

Effort:
- effort/S (green)
- effort/M (yellow)
- effort/L (red)
```

**Tip:** Use GitHub CLI for batch creation:
```bash
# Install gh CLI if needed: https://cli.github.com/

gh label create "idea" --color "7B68EE" --description "Raw idea, needs analysis"
gh label create "needs-analysis" --color "FFD700" --description "Waiting for Opus breakdown"
# ... (repeat for all labels)
```

### Step 4: Create GitHub Project Board

**On GitHub website:**

1. Go to: https://github.com/r464r64r/FractalTrader/projects
2. Click "New project"
3. Choose "Board" template
4. Name: "FractalTrader Development"
5. Add columns:
   - 💡 Ideas
   - 🧠 Analysis
   - 🔬 Research
   - 🔨 Implementation
   - 👀 Review
   - ✅ Done

6. Set up automations (Settings > Workflows):
   - When issue labeled `needs-analysis` → Move to Analysis
   - When issue labeled `research` → Move to Research
   - When issue labeled `implementation` → Move to Implementation
   - When PR opened → Move to Review
   - When PR merged → Move to Done

### Step 5: Create First Issues

**Option A: Use Example Files**

1. Go to: https://github.com/r464r64r/FractalTrader/issues/new/choose
2. Choose "💡 Feature Idea"
3. Copy content from:
   - `docs/example-issues/jupyter-dashboard-issue.md`, or
   - `docs/example-issues/tribal-weather-issue.md`
4. Submit!

**Option B: Fresh Idea**

1. Read: `docs/FILIP_QUICKSTART.md`
2. Create issue using template
3. Let Opus analyze

## Usage

### For Filip (Idea Creator)

1. **Have idea** → Create GitHub issue (template: Feature Idea)
2. **Submit** → Opus takes over
3. **Watch it flow** through project board
4. **Test/feedback** when ready

**Read:** `docs/FILIP_QUICKSTART.md`

### For Opus (Strategic Analyst)

1. **Check** "Ideas" column in project board
2. **Analyze** issue strategically
3. **Comment** breakdown on original issue
4. **Create** child issues (research, implementation)
5. **Label** appropriately, add to milestone
6. **Move** to Analysis column

**Read:** `.github/WORKFLOW.md`

### For Haiku (Researcher/Coder)

1. **Pick** task from Research or Implementation column
2. **Deliver** according to issue requirements
3. **Update** issue with progress
4. **Create PR** when ready (for code tasks)

**Read:** `.github/WORKFLOW.md` (Step 3-4)

### For Sonnet (Reviewer/Integrator)

1. **Review** PRs in Review column
2. **Check** tests, docs, integration
3. **Approve + Merge** or request changes
4. **Help** with integration tasks

**Read:** `.github/WORKFLOW.md` (Step 5)

## What Changes

**Before:**
```
Chat → Great idea! → ... → Forgotten
```

**After:**
```
Chat → GitHub Issue → Opus Breakdown → Research/Code → PR → Merge → Done
```

**Benefits:**
- ✅ Context preserved in issues
- ✅ Clear ownership (agent labels)
- ✅ Progress visible (project board)
- ✅ Community friendly
- ✅ AI-native workflow

## Verification

After setup, you should see:

1. ✅ Issue templates available when creating new issue
2. ✅ Labels created (check /labels page)
3. ✅ Project board created (check /projects)
4. ✅ Example issues submitted (optional)

## Next Steps

1. **Submit example issues** (Jupyter, Tribal) to test workflow
2. **Wait for Opus** to analyze and break down
3. **Watch** the system work
4. **Iterate** - adjust process as needed

## Questions?

- Read: `.github/WORKFLOW.md` (full process)
- Read: `docs/FILIP_QUICKSTART.md` (Filip's guide)
- Read: `.github/PROJECT_BOARD.md` (board usage)

---

**Welcome to organized chaos!** 🌀

The workflow serves the code, not the other way around.  
Keep it simple, keep context, ship features.
