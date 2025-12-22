# Fractal Trader — Deployment Roadmap

**Current:** Phase 1 Complete (Core), Phase 2 at 60%  
**Overall Readiness:** 65% (revised from 85%)  
**Updated:** 2024-12-22

---

## 🎯 "When Can I...?" Milestones

### ✅ RIGHT NOW
- Run backtests
- Compare strategies  
- Test historical periods  
**Time:** 15 minutes  
**See:** [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)

### ⏳ In 2-3 Weeks (Paper Trading)
- Paper trade on testnet
- Real-time signals
- 24/7 bot
**Blockers:** Retry logic (2-4h), state persistence (4-6h), tests (8-12h)

### 📋 In 6-8 Weeks (Small Mainnet)
- Live trading $50-100
- Full monitoring
- Alerts & risk controls
**Blockers:** All Priority 1-2 items + 7-day testnet run

---

## 📊 Honest Status

| Component | Was | Actually | Gap |
|-----------|-----|----------|-----|
| Core Detection | 100% ✅ | 100% ✅ | None |
| Strategies | 79% ✅ | 60% ⚠️ | Test coverage 13-42% |
| Data Layer | 85% ⚠️ | 40% 🚨 | No retry logic |
| Live Trading | 80% ⚠️ | 40% 🚨 | No state persistence |
| **OVERALL** | **85%** | **65%** | **20% gap** |

---

## 🚨 Critical Gaps

### Priority 1 (Before ANY Live Trading)

| Issue | Impact | Effort | Status |
|-------|--------|--------|--------|
| No retry logic | Crash on timeout | 2-4h | ❌ |
| No state persistence | Lost positions | 4-6h | ❌ |
| Strategy tests 13-42% | Untested bugs | 8-12h | ❌ |
| Circuit breaker (testnet) | Can't test fails | 2h | ❌ |

**Total:** 16-24 hours

### Priority 2 (Before Mainnet)

| Issue | Effort | Status |
|-------|--------|--------|
| Portfolio risk controls | 6-8h | ❌ |
| End-to-end test | 4-6h | ❌ |
| Monitoring dashboard | 6-8h | ❌ |

**Total:** 16-22 hours

---

## 🛣️ Timeline

### Week 1-2: Foundation
- Retry logic
- State persistence  
- Strategy tests
- Circuit breakers

**Deliverable:** Testnet-ready

### Week 3-4: Validation
- End-to-end test
- Portfolio risk
- 7-day testnet run

**Deliverable:** Validated system

### Week 5-6: Polish
- Monitoring dashboard
- Telegram alerts
- Disaster recovery

**Deliverable:** Mainnet-ready ($50-100)

---

## 🏠 Hosting Options

### Option 1: Local (Free)
- Zero cost
- Must stay on

### Option 2: VPS (Recommended)
- DigitalOcean: $6/month
- Vultr: $5/month
- 24/7 uptime

### Option 3: Cloud (Scalable)
- AWS EC2: Free tier (1 year)
- Google Cloud: Free tier (90 days)

---

## ✅ Final Checklist

### Before Testnet
- [ ] Priority 1 complete
- [ ] 134 tests passing
- [ ] Strategy coverage >70%

### Before Mainnet
- [ ] Priority 1 & 2 complete
- [ ] 7-day testnet success
- [ ] Monitoring deployed
- [ ] Small capital only

---

**Current:** 65% ready  
**Next:** 85% (testnet) in 2-3 weeks  
**Final:** 95% (mainnet) in 6-8 weeks

You're on track. 🚀
