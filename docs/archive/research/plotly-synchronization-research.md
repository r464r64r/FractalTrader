# Plotly Multi-Timeframe Synchronization Research

**Issue:** [#15](https://github.com/r464r64r/FractalTrader/issues/15)
**Sprint:** 1 - Jupyter Fractal Viewer
**Date:** Dec 26, 2024
**Researcher:** AI Assistant (Claude)

---

## 🎯 Research Goal

Determine the best approach for creating synchronized 3-panel charts (H4/H1/M15) in Plotly for the FractalDashboard, where:
- X-axis (time) synchronizes across all panels (zoom/pan together)
- Y-axis (price) remains independent per panel
- Interactive features work smoothly (hover, zoom, pan)
- Order block overlays render correctly on each timeframe

---

## ✅ Recommended Solution

**Use `plotly.subplots.make_subplots()` with `shared_xaxes=True`**

### Key Implementation Pattern

```python
from plotly.subplots import make_subplots
import plotly.graph_objects as go

fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,           # Synchronize zoom/pan on time axis
    vertical_spacing=0.02,        # Minimal gap between panels
    subplot_titles=['4H', '1H', '15M'],
    row_heights=[0.4, 0.3, 0.3]  # H4 gets more space (macro view)
)

# Add candlestick traces
fig.add_trace(go.Candlestick(...), row=1, col=1)  # H4
fig.add_trace(go.Candlestick(...), row=2, col=1)  # H1
fig.add_trace(go.Candlestick(...), row=3, col=1)  # M15

# Add order block overlays as shapes
fig.add_shape(
    type="rect",
    x0=ob_start, x1=ob_end,
    y0=ob_low, y1=ob_high,
    fillcolor="rgba(0,255,0,0.2)",
    line=dict(color="green"),
    row=1, col=1  # Specify which subplot
)
```

### Why This Works

1. **Native Plotly Feature**: `shared_xaxes=True` provides built-in synchronization
2. **Independent Y-Scales**: Each timeframe can have its own price range
3. **Performance**: No custom JS callbacks needed
4. **Compatibility**: Works in Jupyter notebooks out-of-the-box
5. **Shapes Support**: Order blocks can be added as layered shapes per subplot

---

## 📊 Technical Details

### Plotly Version
- **Installed**: 5.24.1 (confirmed)
- **Required**: 5.0+ for optimal subplot features

### Core API: `make_subplots()`

**Parameters:**
```python
make_subplots(
    rows: int,                    # Number of rows (3 for H4/H1/M15)
    cols: int,                    # Number of columns (1 for vertical stack)
    shared_xaxes: bool | str,     # True = sync all x-axes
    shared_yaxes: bool | str,     # False = independent price scales
    vertical_spacing: float,      # Gap between subplots (0.02 = tight)
    row_heights: list[float],     # Relative heights [0.4, 0.3, 0.3]
    subplot_titles: list[str],    # Panel labels ['4H', '1H', '15M']
    specs: list[list[dict]]       # Advanced config (optional)
)
```

**Returns:** `plotly.graph_objs.Figure` with multiple subplots

---

## 🔬 Alternative Approaches Considered

### ❌ Option 1: Separate Figures with Custom JS
**Idea:** Three independent Plotly figures + JavaScript event listeners

**Pros:**
- Maximum flexibility
- Custom behavior possible

**Cons:**
- Complex implementation (100+ lines of JS)
- Hard to maintain
- May not work in all Jupyter environments
- Overkill for our use case

**Verdict:** Too complex for Sprint 1 MVP

---

### ❌ Option 2: Single Figure with Manual Timeframe Switching
**Idea:** One chart with dropdown to switch between H4/H1/M15

**Pros:**
- Simplest implementation
- Single figure to manage

**Cons:**
- **Breaks core requirement**: No fractal multi-timeframe view
- User can't see H4 context while analyzing M15
- Defeats purpose of "synchronized" visualization

**Verdict:** Doesn't meet Sprint 1 goals

---

### ⚠️ Option 3: Dash + Callbacks
**Idea:** Use Dash framework with synchronized callbacks

**Pros:**
- Powerful interactivity
- Production-grade for web apps

**Cons:**
- Requires Dash server (not pure Jupyter)
- More dependencies
- Complexity not needed for static analysis (Sprint 1 scope)
- **Sprint 2 consideration** (live dashboard)

**Verdict:** Save for Sprint 2 when adding real-time updates

---

## 🎨 Design Recommendations

### Layout Structure

```
┌─────────────────────────────────────┐
│  4H (Macro) - 40% height            │
│  [Candlesticks + Order Blocks]      │
├─────────────────────────────────────┤
│  1H (Meso) - 30% height             │
│  [Candlesticks + Order Blocks]      │
├─────────────────────────────────────┤
│  15M (Micro) - 30% height           │
│  [Candlesticks + Order Blocks]      │
└─────────────────────────────────────┘
        Shared X-Axis (Time) →
```

**Rationale:**
- H4 gets most space (macro context is critical for SMC)
- Tight spacing (`vertical_spacing=0.02`) for fractal continuity
- Shared time axis enables "zoom into execution" workflow

### Visual Hierarchy

1. **Primary**: Candlestick patterns (high contrast)
2. **Secondary**: Order blocks (semi-transparent fills)
3. **Tertiary**: Grid lines, labels (subtle)

**Color Scheme:**
- Bullish OB: `rgba(0, 255, 0, 0.2)` (green, 20% opacity)
- Bearish OB: `rgba(255, 0, 0, 0.2)` (red, 20% opacity)
- Border: Solid line matching fill color

---

## 🧪 Proof of Concept

### Minimal Working Example

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_fractal_view(data_h4, data_h1, data_m15):
    """Create 3-panel synchronized chart."""

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=['4H (Macro)', '1H (Meso)', '15M (Micro)'],
        row_heights=[0.4, 0.3, 0.3]
    )

    # Add candlesticks
    for i, (data, name) in enumerate([
        (data_h4, '4H'),
        (data_h1, '1H'),
        (data_m15, '15M')
    ], 1):
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name=name
            ),
            row=i, col=1
        )

    # Layout
    fig.update_layout(
        height=800,
        showlegend=False,
        xaxis3_rangeslider_visible=False  # Hide rangeslider on bottom
    )

    return fig

# Usage
fig = create_fractal_view(df_4h, df_1h, df_15m)
fig.show()
```

**Expected Behavior:**
- ✅ Zooming on any panel zooms all panels
- ✅ Panning on any panel pans all panels
- ✅ Each panel maintains independent price scale
- ✅ Hover works independently per panel

---

## 🚀 Integration with FractalDashboard

### Architecture Plan

```python
# visualization/fractal_dashboard.py

class FractalDashboard:
    def __init__(self, pair: str, timeframes: list[str]):
        self.pair = pair
        self.timeframes = timeframes  # ['4h', '1h', '15m']
        self.data = {}  # Cached OHLCV per timeframe
        self.order_blocks = {}  # Detected OBs per timeframe

    def load_data(self):
        """Load historical data from data/samples/."""
        # Use existing data fetchers (CCXT for historical)
        pass

    def detect_patterns(self):
        """Run SMC detection on all timeframes."""
        # Use core/order_blocks.py
        # Use core/imbalance.py (for FVG - future sprint)
        pass

    def render(self) -> go.Figure:
        """Create synchronized 3-panel chart."""
        # Use make_subplots() pattern from POC
        # Add candlesticks
        # Add order block shapes
        # Add confidence panel (annotations)
        pass

    def show(self):
        """Display in Jupyter."""
        fig = self.render()
        fig.show()
```

### Data Flow

```
1. FractalDashboard.__init__()
   ↓
2. load_data() → data/samples/btc_90d.csv
   ↓
3. detect_patterns() → core/order_blocks.py
   ↓
4. render() → make_subplots() + add traces/shapes
   ↓
5. show() → Display in Jupyter
```

---

## 📋 Implementation Checklist

### Phase 1: Basic Structure (Task #16)
- [ ] Create `visualization/fractal_dashboard.py`
- [ ] Implement `FractalDashboard` class skeleton
- [ ] Add `load_data()` method (read CSV)
- [ ] Add `render()` method (3-panel candlesticks only)
- [ ] Test in Jupyter notebook

### Phase 2: SMC Integration
- [ ] Add `detect_patterns()` using `core/order_blocks.py`
- [ ] Render order blocks as shapes
- [ ] Add labels to order blocks
- [ ] Test with real BTC data

### Phase 3: Confidence Panel
- [ ] Use `risk/confidence.py` for scoring
- [ ] Add annotations showing breakdown
- [ ] Position panel (top-right overlay or 4th subplot?)

### Phase 4: Polish
- [ ] Color scheme refinement
- [ ] Hover tooltips for OBs
- [ ] Layout responsiveness
- [ ] Performance testing (90 days data)

---

## ⚠️ Known Limitations

### 1. Rangeslider Conflicts
**Issue:** Bottom subplot shows rangeslider by default (clutters view)

**Solution:**
```python
fig.update_layout(xaxis3_rangeslider_visible=False)
```

### 2. Different Data Lengths
**Issue:** H4 has ~500 candles, M15 has ~8640 candles for same period

**Solution:**
- Use shared x-axis with datetime (Plotly handles alignment)
- May need to downsample M15 for performance (Sprint 2 optimization)

### 3. Shape Layer Limits
**Issue:** Too many order blocks (>100) may slow rendering

**Solution:**
- Filter to top N strongest OBs (strength threshold)
- Hide invalidated OBs by default (toggle option)

---

## 📚 References

1. **Plotly Subplots Docs**: https://plotly.com/python/subplots/
2. **Candlestick Charts**: https://plotly.com/python/candlestick-charts/
3. **Shapes & Annotations**: https://plotly.com/python/shapes/
4. **Community Thread**: https://community.plotly.com/t/synchronized-x-and-y-axes-for-zoom-pan-for-subplots/8467

---

## 🎯 Decision

**Use `make_subplots(shared_xaxes=True)` for Sprint 1.**

**Rationale:**
- ✅ Meets all requirements
- ✅ Simple, maintainable
- ✅ No external dependencies beyond Plotly
- ✅ Proven pattern for financial charts
- ✅ Enables fast iteration

**Next Step:** Implement `FractalDashboard` core class (Task #16)

---

**Research Status:** ✅ Complete
**Confidence:** High (validated with Plotly 5.24.1 docs + community patterns)
**Estimated Implementation:** 2-3 days (per sprint plan)
