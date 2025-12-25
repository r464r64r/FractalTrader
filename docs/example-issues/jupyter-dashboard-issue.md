---
name: 💡 Feature Idea
about: Spark from the free electron (Filip's ideas)
title: '[IDEA] Jupyter Fractal Dashboard - Interactive Multi-Timeframe SMC Visualization'
labels: 'idea, needs-analysis, feature/ui'
assignees: ''
---

## 🌟 The Spark

Co jeśli mielibyśmy **synchronized 3-panel view** w Jupyter, gdzie:
- H4 pokazuje macro context (whale movements, BOS/CHoCH)
- H1 pokazuje meso structure (pullbacks, order blocks)
- M15 pokazuje micro execution (entry zones, sweeps)

**All synchronized.** Scrollujesz H4 → H1 i M15 follow. Klikasz na order block → details panel.

Plus **live SMC overlay**:
- Order blocks (auto-detected, z % fill probability)
- FVG zones (colored by age/strength)
- Liquidity levels (+ estimated $ volume)
- Sweep zones (danger/opportunity)

Plus **confidence explainer panel**:
```
Setup: BOS + OB retest
Confidence: 78/100 ✓ ENTRY

Breakdown:
  HTF alignment:  +15 ✓
  Pattern clean:  +10 ✓
  Volume spike:   +10 ✓
  OB retest:      +15 ✓
  Time of day:    +5  ✓
  Recent streak:  -10 ⚠
```

To byłoby **TradingView killer** dla SMC traders.

## 🎯 Why This Matters

**Problem:**
1. TradingView: trzeba ręcznie rysować OB, FVG, levels
2. Multi-timeframe = 3 osobne okna, brak synchronizacji
3. Zero confidence scoring (dlaczego bot wszedł?)
4. Zero tribal context

**Solution:**
- Auto-detection SMC patterns (mamy już w core/)
- Fractal synchronized view (natura naszego projektu)
- Transparent AI reasoning (przewaga nad CryptoWeather)
- Educational (learn from every setup)

**Edge:**
- Nikt inny tego nie ma w open source
- Perfect showcase dla FractalTrader capabilities
- Bridge między backtesting a live trading (same interface)

## 🤔 Initial Thoughts

**Tech stack hunches:**
- `plotly` dla interactive charts (pan, zoom, hover)
- `ipywidgets` dla controls (timeframe selector, pair switcher)
- `jupyter-dash` dla real-time updates bez refresh?
- `vectorbt` już mamy, perfect integration

**Struktura (rough):**
```python
class FractalDashboard:
    def __init__(self, strategy, data_source):
        self.strategy = strategy
        self.data = data_source
        
    def show(self):
        # Main 3-panel synchronized view
        # SMC overlay layer
        # Confidence panel
        # Controls
```

**Concerns:**
- Performance z live data updates?
- Jak synchronizować 3 timeframes smooth?
- State management (which setup user is analyzing?)

## 📎 Context

**Related:**
- CryptoWeather (competitor): https://cryptoweather.xyz - mają mobile UI, brak fractal view
- vectorbt plotting capabilities: już używamy, można extend
- Existing code: `core/` ma wszystkie SMC detectors gotowe

**Similar projects:**
- Jesse AI (trading framework) - ma dashboard ale prosty
- FreqUI (freqtrade) - pokazuje trades, ale nie SMC analysis

**Inspiration:**
- TradingView multi-chart layout
- Matrix "code rain" aesthetic (data overlay)
- Weather apps (clear visual hierarchy)

**From chat:**
> "Jupyter to game changer dla FractalTrader. Nie tylko przebijemy TradingView 
> - stworzymy coś czego oni nie mogą: transparent AI reasoning."

---

**Status:** Needs Opus analysis  
**Next Step:** Strategic breakdown & research tasks

---

## Expected Opus Breakdown

(This will be added by Opus in comments)

**Research tasks:**
- [ ] Plotly vs Dash vs jupyter-dash comparison
- [ ] vectorbt real-time plotting patterns
- [ ] Multi-timeframe synchronization approaches
- [ ] State management for interactive dashboards

**Implementation tasks:**
- [ ] Core FractalDashboard class
- [ ] 3-panel synchronized view
- [ ] SMC overlay rendering
- [ ] Confidence explainer panel
- [ ] Controls & interactivity

**Integration:**
- [ ] Connect to existing SMC detectors (core/)
- [ ] Connect to strategy confidence scoring (risk/)
- [ ] Connect to data fetchers (data/)
