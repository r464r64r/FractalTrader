# FractalTrader - Jupyter Notebooks

Interactive notebooks for analyzing and trading with Smart Money Concepts.

---

## 📓 Available Notebooks

### [fractal_viewer.ipynb](fractal_viewer.ipynb) - Sprint 1 ✅

**Static Analysis** - Multi-timeframe SMC visualization with confidence scoring

### [live_dashboard.ipynb](live_dashboard.ipynb) - Sprint 2 ✅ NEW

**Live Trading** - Real-time market monitoring with automatic setup detection

**What it does:**
- Loads historical BTC data (90 days of 15m candles)
- Detects order blocks across 3 timeframes (H4/H1/M15)
- Displays synchronized interactive charts
- Calculates confidence scores for trade setups
- Exports analysis as HTML

**Quick Start:**

```bash
# 1. Navigate to notebooks directory
cd notebooks/

# 2. Launch Jupyter
jupyter notebook

# 3. Open fractal_viewer.ipynb

# 4. Run all cells (Cell → Run All)
```

**Expected Output:**
- ✅ 3-panel synchronized chart with order blocks
- ✅ Confidence breakdown for strongest setup
- ✅ Interactive zoom/pan controls
- ✅ Exportable HTML chart

---

### [live_dashboard.ipynb](live_dashboard.ipynb)

**Sprint 2** - Live market dashboard with real-time alerts

**What it does:**
- Streams live BTC data (updates every 15s)
- Detects setups in real-time (liquidity sweeps, OB bounces)
- Triggers visual/audio alerts (confidence >70%)
- Logs all setups to trade journal
- Exports journal to CSV

**Quick Start:**

```bash
# 1. Navigate to notebooks directory
cd notebooks/

# 2. Launch Jupyter
jupyter notebook

# 3. Open live_dashboard.ipynb

# 4. Configure settings (symbol, timeframes, etc.)

# 5. Run cells to start live stream
```

**Configuration:**
```python
SYMBOL = 'BTC'              # Trading symbol
DATA_SOURCE = 'hyperliquid' # Data source
UPDATE_INTERVAL = 15        # Update frequency (seconds)
MIN_CONFIDENCE = 70         # Alert threshold (%)
```

**Expected Output:**
- 🔴 Live charts updating every 15 seconds
- 🔔 Visual alerts when setups detected
- 📊 Real-time statistics dashboard
- 📝 Trade journal with all setups logged

---

## 🎯 Features Demonstrated

### 1. Multi-Timeframe Synchronization
- **H4 (Macro):** Overall market structure, whale movements
- **H1 (Meso):** Pullbacks, order block formation
- **M15 (Micro):** Entry zones, precise execution

**All panels share x-axis (time)** → Zoom on one, all zoom together

### 2. Order Block Detection
- Auto-detected using `core/order_blocks.py`
- Color-coded: 🟢 Bullish / 🔴 Bearish
- Labels show retest count (strength indicator)
- Faded = invalidated (price broke through)

### 3. Confidence Scoring ✨ NEW
- **Score:** 0-100 (higher = better setup)
- **Breakdown:** 8 factors analyzed
  - HTF trend alignment (0-30 pts)
  - Pattern quality (0-30 pts)
  - Volume confirmation (0-20 pts)
  - Market regime (0-20 pts)

**Signals:**
- ✓ **ENTRY** (70+): High probability setup
- ⚠ **CAUTION** (50-69): Medium probability
- ✗ **SKIP** (<50): Low probability

### 4. Interactive Controls
- **Zoom:** Click & drag
- **Pan:** Shift + drag
- **Reset:** Double-click
- **Hover:** See OHLC + details

---

## 📊 Sample Output

### Console Output (Section 7)

```
📊 Confidence Analysis for OB at 2024-12-15 08:00:00
==================================================

🎯 Score: 75/100
   Signal: ✓ ENTRY (High confidence)

📋 Factor Breakdown:
   HTF Trend Aligned:    +15 ✓
   HTF Structure Clean:    0 ✗
   Pattern Clean:        +10 ✓
   Confluences:          +20 (4x)
   Volume Spike:         +10 ✓
   Volume Divergence:      0 ✗
   Trending Market:      +10 ✓
   Low Volatility:       +10 ✓
```

### Visual Output (Section 8)

**3-Panel Chart:**
```
┌─────────────────────────────────┐ ← Confidence Panel (top-right)
│  4H (Macro) - 40% height        │   Setup: BULLISH OB Retest
│  [Candlesticks + Green/Red OBs]│   Confidence: 75/100 ✓ ENTRY
├─────────────────────────────────┤
│  1H (Meso) - 30% height         │   Breakdown:
│  [Candlesticks + OBs]           │     HTF alignment:  +15 ✓
├─────────────────────────────────┤     Pattern clean:  +10 ✓
│  15M (Micro) - 30% height       │     ...
│  [Candlesticks + OBs]           │
└─────────────────────────────────┘
```

---

## 🛠️ Requirements

### Python Packages

Already included in `requirements.txt`:

```
pandas
numpy
plotly >= 5.0
jupyter
```

### Installation

```bash
# From project root
pip install -r requirements.txt
```

---

## 📚 Learning Path

**Beginner:**
1. Read [README.md](../README.md) - Project overview
2. Run `fractal_viewer.ipynb` - See SMC in action
3. Experiment with parameters (timeframes, thresholds)

**Intermediate:**
4. Review [core/order_blocks.py](../core/order_blocks.py) - Detection logic
5. Review [risk/confidence.py](../risk/confidence.py) - Scoring system
6. Modify confidence factors (edit `calculate_confidence()`)

**Advanced:**
7. Create custom visualization (extend `FractalDashboard`)
8. Add new SMC patterns (FVG, liquidity sweeps)
9. Build live trading notebook (Sprint 2)

---

## 🔧 Customization

### Change Timeframes

```python
dashboard = FractalDashboard(
    pair='ETH/USDT',  # Different pair
    timeframes=['1d', '4h', '1h'],  # Different TFs
    min_impulse_percent=0.02  # 2% impulse threshold
)
```

### Analyze Different Setups

```python
# Find bearish OBs instead
bearish_1h, _ = dashboard.order_blocks['1h']
strongest_bear = bearish_1h.nlargest(1, 'retest_count').index[0]

# Show confidence for bearish setup
dashboard.show(
    show_confidence_for=('1h', strongest_bear, 'bearish')
)
```

### Export for Later Review

```python
# Save with confidence panel
fig = dashboard.render(
    height=1200,
    show_confidence_for=('4h', ob_index, 'bullish')
)
fig.write_html('my_analysis.html')  # Open in browser anytime
```

---

## ⚠️ Known Limitations (Sprint 1)

### Current

- ✅ Static historical data only
- ✅ Manual execution (no auto-refresh)
- ✅ Order blocks only (no FVG, sweeps)
- ✅ Simple confidence factors (HTF, volume, regime)

### Coming in Sprint 2

- [ ] Live data streaming (Hyperliquid/Binance)
- [ ] Auto-refresh every 15 seconds
- [ ] FVG and liquidity sweep overlays
- [ ] Advanced tribal weather integration
- [ ] Trade journal component

---

## 🐛 Troubleshooting

### "FileNotFoundError: data/samples/btc_90d.csv"

**Solution:** Run Section 1 first (generates sample data)

### "ModuleNotFoundError: No module named 'visualization'"

**Solution:**
```python
import sys
sys.path.append('..')  # Add parent dir to path
```

### Charts not displaying

**Solution:** Ensure Jupyter has Plotly support:
```bash
jupyter labextension install jupyterlab-plotly
```

### Confidence panel not showing

**Solution:** Check parameters:
```python
# Ensure OB exists at specified index
bullish_ob, _ = dashboard.order_blocks['4h']
print(bullish_ob.index)  # See available timestamps

# Use valid timestamp
ob_index = bullish_ob.index[0]
dashboard.show(show_confidence_for=('4h', ob_index, 'bullish'))
```

---

## 💡 Tips & Tricks

### Find Best Setups Programmatically

```python
# Get all bullish OBs across all timeframes
best_setups = []

for tf in dashboard.timeframes:
    bullish_ob, _ = dashboard.order_blocks[tf]

    for ob_index in bullish_ob.index:
        score, _ = dashboard.calculate_confidence(tf, ob_index, 'bullish')

        if score >= 70:  # High confidence only
            best_setups.append((tf, ob_index, score))

# Sort by score
best_setups.sort(key=lambda x: x[2], reverse=True)

print("Top 5 setups:")
for tf, idx, score in best_setups[:5]:
    print(f"  {tf} @ {idx}: {score}/100")
```

### Compare Bullish vs Bearish

```python
bullish_4h, bearish_4h = dashboard.order_blocks['4h']

print(f"4H Bullish: {len(bullish_4h)} OBs")
print(f"4H Bearish: {len(bearish_4h)} OBs")

# Market sentiment
if len(bullish_4h) > len(bearish_4h):
    print("→ Bullish bias (more accumulation zones)")
else:
    print("→ Bearish bias (more distribution zones)")
```

### Batch Export Multiple Analyses

```python
# Analyze top 3 OBs and export each
bullish_4h, _ = dashboard.order_blocks['4h']
top3 = bullish_4h.nlargest(3, 'retest_count')

for i, (ob_index, _) in enumerate(top3.iterrows(), 1):
    fig = dashboard.render(
        show_confidence_for=('4h', ob_index, 'bullish')
    )
    fig.write_html(f'analysis_{i}_{ob_index.strftime("%Y%m%d")}.html')

print("✅ Exported 3 analyses")
```

---

## 📖 API Reference

### FractalDashboard

```python
class FractalDashboard:
    def __init__(self, pair, timeframes, min_impulse_percent=0.01)
    def load_data(self, csv_path)
    def detect_patterns(self)
    def calculate_confidence(self, timeframe, ob_index, ob_type='bullish')
    def render(self, height=800, show_invalidated=False,
               max_order_blocks=50, show_confidence_for=None)
    def show(self, **kwargs)
```

**Full docs:** See docstrings in [visualization/fractal_dashboard.py](../visualization/fractal_dashboard.py)

---

## 🚀 Next Steps

1. **Run the notebook** - Get hands-on experience
2. **Tweak parameters** - Experiment with different settings
3. **Analyze your own data** - Replace sample data with real market data
4. **Build on it** - Extend for your own trading strategies

**Sprint 2 Preview:**
- Live dashboard with auto-refresh
- Paper trading integration
- Real-time signal generation

---

## 📞 Questions?

- **SMC Theory:** [docs/archive/fractal-trader-context.md](../docs/archive/fractal-trader-context.md)
- **Development Guide:** [AI_DEVELOPMENT.md](../AI_DEVELOPMENT.md)
- **Sprint Framework:** [docs/SPRINT_FRAMEWORK.md](../docs/SPRINT_FRAMEWORK.md)
- **GitHub Issues:** https://github.com/r464r64r/FractalTrader/issues

---

**FractalTrader** - Open source SMC trading system
🚢 Sprint 1 Deliverable (Dec 24 - Jan 6, 2025)
