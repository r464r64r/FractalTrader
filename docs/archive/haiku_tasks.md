# 🌿 Haiku Tasks — Carbon-Efficient Delegation

**Goal:** Minimize AI carbon footprint by using appropriate model  
**Philosophy:** Haiku for simple/repetitive, Sonnet for complex

---

## 🎯 Model Selection Guide

### Use **Haiku 3.5** For:
✅ Data processing & transformation  
✅ Running tests & reporting results  
✅ Generating fixtures & sample data  
✅ CSV/JSON parsing & export  
✅ Simple code generation (templates)  
✅ Batch operations  

### Use **Sonnet 4** For:
🧠 Strategy logic implementation  
🧠 Complex algorithms  
🧠 Debugging tricky issues  
🧠 Code review & refactoring  

### Use **Opus 3** For:
💎 Critical architecture decisions  
💎 Security review  
💎 Production deployment planning  

---

## 📋 Haiku-Ready Tasks

### Data Generation
```python
# HAIKU CAN DO THIS
"""
Generate 100 bars of uptrend OHLCV data:
- Linear uptrend: 100 → 150
- Random noise: ±2%
- Save to tests/fixtures/uptrend.csv
"""
```

### Test Execution
```bash
# HAIKU CAN DO THIS
"""
Run pytest, generate markdown report:
- Total tests run
- Pass/fail counts
- Coverage %
Save to reports/test_report_YYYYMMDD.md
"""
```

### Batch Processing
```python
# HAIKU CAN DO THIS
"""
Run backtest for all strategies on same data.
Generate comparison CSV:
- Strategy name, return, sharpe, max_dd, win_rate
"""
```

---

## 🔄 Workflow Examples

### Workflow: Add Test Fixtures

**Step 1 (Haiku):** Generate data
```bash
"Generate bull/bear/sideways market CSV files"
```

**Step 2 (Sonnet):** Write tests
```bash
"Implement tests that verify strategy behavior"
```

---

## 📊 Cost & Carbon Savings

| Approach | Cost | Carbon |
|----------|------|--------|
| All Sonnet | ~$50 | High |
| Haiku for data | ~$15 | Low |

**Savings:** 70% cost, 60% carbon reduction

---

## ✅ Delegation Checklist

**Haiku Tasks:**
- [ ] Generate bull market data (200 bars)
- [ ] Generate bear market data (200 bars)
- [ ] Run all unit tests, generate report
- [ ] Batch backtest all strategies
- [ ] Generate HTML trade report

---

## 🌱 Best Practices

1. **Batch operations** (one Haiku call for 100 tasks)
2. **Reuse generated code** (save scripts)
3. **Cache results** (don't regenerate)

---

**Remember:** Haiku for 80% of tasks. Save Sonnet/Opus for when you need them. 🌿
