# FractalTrader Development Workflow

## The KISS Process

### Step 1: Filip Sparks 💡

**Where:** Create GitHub Issue using "Feature Idea" template  
**What:** Raw idea, no structure needed  
**Labels:** `idea`, `needs-analysis`

**Example:**
```
Title: [IDEA] Jupyter fractal dashboard
Body: "What if we had synchronized 3-panel view (H4/H1/M15) 
       with live SMC overlay? Like TradingView but fractal..."
```

### Step 2: Opus Analyzes 🧠

**Trigger:** Issue labeled `needs-analysis`  
**What:** Strategic breakdown

**Opus creates:**

1. **Comment on original issue** with:
   - Strategic value assessment
   - Technical approach options
   - Integration points with existing code
   - Risk/complexity analysis

2. **Child issues:**
   - Research tasks (for Haiku) - labeled `research`, `haiku-task`
   - Implementation tasks - labeled `implementation`
   - Each linked to parent issue

3. **Updates parent issue:**
   - Removes `needs-analysis`
   - Adds feature area label (e.g., `feature/ui`)
   - Adds priority & effort estimates
   - Adds to milestone (if applicable)

**Example Breakdown:**
```
Parent: #42 [IDEA] Jupyter fractal dashboard

Created child issues:
  #43 [RESEARCH] Plotly vs Dash for multi-timeframe sync
  #44 [RESEARCH] vectorbt integration patterns for live updates
  #45 [IMPL] Core FractalDashboard class structure
  #46 [IMPL] SMC overlay rendering layer
```

### Step 3: Haiku Researches 🔬

**Trigger:** Assigned `haiku-task` issues  
**What:** Technical research, prototyping, data analysis

**Haiku delivers:**
- Markdown research reports in `docs/research/`
- Code prototypes in `experiments/`
- Data analysis notebooks
- Updates issue with findings

**Example:**
```
Issue: #43 [RESEARCH] Plotly vs Dash for multi-timeframe sync

Haiku creates:
  docs/research/jupyter-frameworks-comparison.md
  experiments/plotly-multi-timeframe-poc.ipynb
  
Findings: "Plotly + ipywidgets wins for our use case because..."
```

### Step 4: Haiku or Sonnet Implements 🔨

**Trigger:** Research complete, implementation issue ready  
**What:** Write production code

**Developer:**
- Creates feature branch: `feature/issue-45-fractal-dashboard`
- Implements according to research findings
- Writes tests (coverage >70%)
- Updates documentation
- Opens Pull Request

**PR Requirements:**
- Links to original issue: "Closes #45"
- Passes all tests
- Meets acceptance criteria from issue

### Step 5: Sonnet Reviews 👀

**Trigger:** PR opened  
**What:** Code review, integration check

**Sonnet checks:**
- Code quality & consistency
- Test coverage
- Documentation completeness
- Integration with existing features
- No breaking changes (or justified)

**Actions:**
- Request changes, or
- Approve + merge

### Step 6: Done ✅

**After merge:**
- GitHub auto-closes linked issues
- Update parent issue progress
- If all child issues done → close parent issue
- Celebrate! 🎉

## Quick Reference

| Stage | Who | Label | Output |
|-------|-----|-------|--------|
| Idea | Filip | `idea`, `needs-analysis` | GitHub issue |
| Analysis | Opus | `opus-task` | Breakdown + child issues |
| Research | Haiku | `research`, `haiku-task` | Reports, prototypes |
| Code | Haiku/Sonnet | `implementation` | PR with tests |
| Review | Sonnet | `review` | Merge or feedback |
| Done | Auto | `done` | Closed issue |

## Communication Channels

- **GitHub Issues:** All features, bugs, tasks
- **PR Comments:** Code-specific discussion
- **Commit Messages:** Why this change (not what - code shows that)
- **This Chat:** Brainstorming only (then → GitHub issue)

## Example: End-to-End Flow

```
1. Filip (chat): "Jupyter dashboard would be cool!"
   → Filip (GitHub): Creates issue #42

2. Opus (GitHub): Comments analysis, creates issues #43-46
   → Updates #42 with labels, milestone

3. Haiku (GitHub): Works on #43, #44 (research)
   → Delivers reports in docs/research/

4. Haiku (GitHub): Works on #45 (implementation)
   → Creates PR #47, links to #45

5. Sonnet (GitHub): Reviews PR #47
   → Approves, merges
   → Issue #45 auto-closes

6. Repeat for #46...

7. All child issues done
   → Close parent #42
   → Feature shipped! 🚀
```

## Anti-Patterns to Avoid

❌ **Long chat discussions** → Convert to issues  
❌ **"I'll remember this"** → Write it down in issue  
❌ **Direct to code** → Research first (for unknowns)  
❌ **Mega-issues** → Break down into child tasks  
❌ **No tests** → Not done until tested  

## Benefits

✅ **Context preserved** in issues, not lost in chat  
✅ **Clear ownership** via agent labels  
✅ **Progress visible** via GitHub project board  
✅ **Community friendly** - others can contribute  
✅ **AI-native** - designed for Claude collaboration  
✅ **KISS** - simple, repeatable process  

---

**Remember:** This workflow serves the code, not the other way around.  
If process gets in the way → simplify. But preserve context.
