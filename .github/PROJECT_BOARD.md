# GitHub Project Board Setup

## Board: FractalTrader Development

### Columns

1. **💡 Ideas**
   - Issues with `idea` label
   - Waiting for Opus analysis

2. **🧠 Analysis**
   - Issues with `needs-analysis` label
   - Opus working on breakdown

3. **🔬 Research**
   - Issues with `research` label
   - Haiku investigating

4. **🔨 Implementation**
   - Issues with `implementation` label
   - Code being written

5. **👀 Review**
   - Open PRs
   - Awaiting code review

6. **✅ Done**
   - Merged PRs
   - Closed issues
   - Auto-archived after 7 days

### Automation Rules

**Ideas → Analysis:**
- Trigger: Issue labeled `needs-analysis`
- Action: Auto-move to Analysis column

**Analysis → Research/Implementation:**
- Trigger: Child issue created with `research` or `implementation`
- Action: Auto-move to respective column

**Implementation → Review:**
- Trigger: PR opened
- Action: Auto-move to Review

**Review → Done:**
- Trigger: PR merged
- Action: Auto-move to Done, close linked issues

### Views

**View 1: By Agent**
- Grouped by: Agent labels (`opus-task`, `sonnet-task`, `haiku-task`)
- Use: See what each agent is working on

**View 2: By Feature Area**
- Grouped by: Feature labels (`feature/smc`, `feature/ui`, etc.)
- Use: Track progress by domain

**View 3: Current Sprint**
- Filter: Current milestone + priority high/critical
- Use: Focus on what matters now

## Creating the Board

```bash
# On GitHub:
# 1. Go to repository
# 2. Click "Projects" tab
# 3. Click "New project"
# 4. Choose "Board" template
# 5. Name: "FractalTrader Development"
# 6. Add columns as defined above
# 7. Set up automation rules
```

## Using the Board

**For Filip:**
- Create issue → appears in "Ideas" column
- Watch it move through pipeline
- Jump in when you want to contribute

**For Opus:**
- Check "Ideas" column
- Analyze, break down, create child issues
- Move to "Analysis" when done

**For Haiku:**
- Pick from "Research" column
- Deliver findings
- Move to next task

**For Sonnet:**
- Review PRs in "Review" column
- Merge or request changes
- Help with integration tasks

**For Everyone:**
- **Daily:** Quick glance at board
- **Weekly:** Review "Done" column (celebrate!)
- **Monthly:** Clean up stale issues

## Milestones

### Current Milestone: Phase 2 - Integration
- Retry logic in data fetchers
- State persistence
- Strategy test coverage
- Circuit breakers

### Future Milestones:
- Phase 3: Production (testnet validation)
- Phase 4: Scale (multi-exchange)
- Feature: Jupyter Dashboard
- Feature: Tribal Weather

## Issue Linking

**Parent-Child Relationship:**
```
#42 [IDEA] Jupyter fractal dashboard
  ├─ #43 [RESEARCH] Plotly vs Dash
  ├─ #44 [RESEARCH] vectorbt integration
  ├─ #45 [IMPL] Core dashboard class
  └─ #46 [IMPL] SMC overlay rendering
```

**In GitHub:**
- Child issues reference parent: "Part of #42"
- Parent issue tracks children: "Subtasks: #43, #44, #45, #46"
- Checkboxes in parent issue description

## Tips

✅ **Keep issues small** - If >16h effort, break it down  
✅ **Link everything** - PRs to issues, issues to parents  
✅ **Update status** - Comment when stuck, blocked, or pivoting  
✅ **Close promptly** - Don't leave done issues open  
✅ **Use drafts** - PR drafts for WIP, prevents accidental merge  

---

**The board is a shared brain.** Keep it current, keep it clean.
