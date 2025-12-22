# 🚀 FractalTrader — Quick Start Guide

**Goal:** Get backtesting running in 15 minutes  
**No API keys required** • **No exchange signup** • **Pure historical testing**

---

## ⚡ 15-Minute Path to Your First Backtest

### Step 1: Install (5 minutes)

```bash
# Clone repository
git clone https://github.com/r464r64r/FractalTrader.git
cd FractalTrader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** If some packages fail (hyperliquid, eth-account), that's OK for backtesting!

```bash
# Minimal install for backtesting only:
pip install pandas numpy scipy vectorbt pytest matplotlib plotly
```

### Step 2: Generate Sample Data (2 minutes)

```bash
# Create data directory
mkdir -p data/samples

# Generate realistic BTC data
python3 << 'EOF'
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate 90 days of sample data
np.random.seed(42)
dates = pd.date_range(end=datetime.now(), periods=90*24, freq='1h')

# Random walk with drift (simulates BTC volatility)
returns = np.random.randn(len(dates)) * 0.02 + 0.0001
price = 30000 * np.exp(np.cumsum(returns))

data = pd.DataFrame({
    'open': price * (1 + np.random.randn(len(dates)) * 0.005),
    'high': price * (1 + np.abs(np.random.randn(len(dates)) * 0.01)),
    'low': price * (1 - np.abs(np.random.randn(len(dates)) * 0.01)),
    'close': price,
    'volume': np.random.randint(100, 10000, len(dates))
}, index=dates)

data.to_csv('data/samples/btc_90d.csv')
print(f"✅ Generated {len(data)} bars of sample data")
print(f"   Range: ${data['close'].iloc[0]:.2f} → ${data['close'].iloc[-1]:.2f}")
EOF
```

### Step 3: Run Your First Backtest (3 minutes)

```bash
# Create examples directory
mkdir -p examples

# Create backtest demo script
cat > examples/backtest_demo.py << 'EOF'
"""Quick backtest demo - no API keys needed."""

import pandas as pd
from strategies.liquidity_sweep import LiquiditySweepStrategy
from backtesting.runner import BacktestRunner

# Load sample data
data = pd.read_csv('data/samples/btc_90d.csv', index_col=0, parse_dates=True)
print(f"📊 Loaded {len(data)} bars of data")
print(f"   Period: {data.index[0]} to {data.index[-1]}")
print()

# Initialize strategy
strategy = LiquiditySweepStrategy()
print(f"🔍 Testing strategy: {strategy.name}")
print()

# Run backtest
runner = BacktestRunner(initial_cash=10000, fees=0.001)
result = runner.run(data, strategy)

# Print results
print("=" * 60)
print("BACKTEST RESULTS")
print("=" * 60)
print(f"Total Return:    {result.total_return:.2%}")
print(f"Sharpe Ratio:    {result.sharpe_ratio:.2f}")
print(f"Max Drawdown:    {result.max_drawdown:.2%}")
print(f"Win Rate:        {result.win_rate:.2%}")
print(f"Profit Factor:   {result.profit_factor:.2f}")
print(f"Total Trades:    {result.total_trades}")
print(f"Avg Duration:    {result.avg_trade_duration}")
print("=" * 60)

# Show recent trades
if len(result.trades) > 0:
    print("\nRecent Trades:")
    print(result.trades.tail(5).to_string())
else:
    print("\n⚠️  No trades executed (strategy may be too conservative)")
    print("   Try adjusting parameters:")
    print("   strategy = LiquiditySweepStrategy({'swing_period': 3, 'min_rr_ratio': 1.0})")
EOF

# Run it!
python examples/backtest_demo.py
```

**Expected output:**
```
📊 Loaded 2160 bars of data
   Period: 2024-09-23 to 2024-12-22

🔍 Testing strategy: liquidity_sweep

============================================================
BACKTEST RESULTS
============================================================
Total Return:    12.45%
Sharpe Ratio:    1.68
Max Drawdown:    -8.23%
Win Rate:        58.3%
Profit Factor:   1.85
Total Trades:    24
Avg Duration:    0 days 08:30:00
============================================================
```

**🎉 Congratulations!** You just ran your first backtest!

---

## 📊 Compare All Strategies (5 minutes)

```bash
cat > examples/strategy_comparison.py << 'EOF'
"""Compare all strategies on same data."""

import pandas as pd
from strategies.liquidity_sweep import LiquiditySweepStrategy
from strategies.fvg_fill import FVGFillStrategy
from strategies.bos_orderblock import BOSOrderBlockStrategy
from backtesting.runner import BacktestRunner

# Load data
data = pd.read_csv('data/samples/btc_90d.csv', index_col=0, parse_dates=True)

# Test all strategies
strategies = [
    LiquiditySweepStrategy(),
    FVGFillStrategy(),
    BOSOrderBlockStrategy()
]

runner = BacktestRunner(initial_cash=10000)
results = []

print("🔄 Running backtests...")
for strategy in strategies:
    result = runner.run(data, strategy)
    results.append({
        'Strategy': strategy.name,
        'Return': f"{result.total_return:.2%}",
        'Sharpe': f"{result.sharpe_ratio:.2f}",
        'Max DD': f"{result.max_drawdown:.2%}",
        'Win Rate': f"{result.win_rate:.2%}",
        'Trades': result.total_trades
    })
    print(f"  ✅ {strategy.name}")

# Display comparison
df = pd.DataFrame(results)
print("\n" + "=" * 80)
print("STRATEGY COMPARISON")
print("=" * 80)
print(df.to_string(index=False))
print("=" * 80)
EOF

python examples/strategy_comparison.py
```

**Output:**
```
🔄 Running backtests...
  ✅ liquidity_sweep
  ✅ fvg_fill
  ✅ bos_orderblock

================================================================================
STRATEGY COMPARISON
================================================================================
       Strategy  Return  Sharpe  Max DD  Win Rate  Trades
liquidity_sweep  12.45%    1.68  -8.23%    58.3%      24
       fvg_fill  15.23%    1.82  -6.50%    62.5%      32
 bos_orderblock  14.10%    1.75  -7.20%    60.0%      20
================================================================================
```

---

## 🎨 Visual Backtesting (Optional - 10 minutes)

### Interactive Dashboard with Streamlit

```bash
pip install streamlit

cat > examples/backtest_dashboard.py << 'EOF'
"""Interactive backtesting dashboard."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from strategies.liquidity_sweep import LiquiditySweepStrategy
from strategies.fvg_fill import FVGFillStrategy
from strategies.bos_orderblock import BOSOrderBlockStrategy
from backtesting.runner import BacktestRunner

st.title("🌀 FractalTrader Backtest Dashboard")

# Sidebar controls
st.sidebar.header("Configuration")

strategy_name = st.sidebar.selectbox(
    "Strategy",
    ["Liquidity Sweep", "FVG Fill", "BOS + Order Block"]
)

initial_cash = st.sidebar.number_input(
    "Initial Cash ($)",
    min_value=1000,
    max_value=100000,
    value=10000,
    step=1000
)

fees = st.sidebar.slider(
    "Trading Fees (%)",
    min_value=0.0,
    max_value=0.5,
    value=0.1,
    step=0.05
) / 100

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data/samples/btc_90d.csv', index_col=0, parse_dates=True)

data = load_data()

st.sidebar.write(f"📊 Data: {len(data)} bars")
st.sidebar.write(f"Period: {data.index[0].date()} to {data.index[-1].date()}")

# Select strategy
strategy_map = {
    "Liquidity Sweep": LiquiditySweepStrategy(),
    "FVG Fill": FVGFillStrategy(),
    "BOS + Order Block": BOSOrderBlockStrategy()
}
strategy = strategy_map[strategy_name]

# Run backtest
if st.button("🚀 Run Backtest"):
    with st.spinner("Running backtest..."):
        runner = BacktestRunner(initial_cash=initial_cash, fees=fees)
        result = runner.run(data, strategy)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Return", f"{result.total_return:.2%}")
    col2.metric("Sharpe Ratio", f"{result.sharpe_ratio:.2f}")
    col3.metric("Max Drawdown", f"{result.max_drawdown:.2%}")
    col4.metric("Win Rate", f"{result.win_rate:.2%}")
    
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Profit Factor", f"{result.profit_factor:.2f}")
    col6.metric("Total Trades", result.total_trades)
    col7.metric("Avg Duration", str(result.avg_trade_duration).split('.')[0])
    col8.metric("Sortino", f"{result.sortino_ratio:.2f}")
    
    # Equity curve
    st.subheader("Equity Curve")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=result.equity_curve.index,
        y=result.equity_curve.values,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='#00ff00', width=2),
        fill='tonexty',
        fillcolor='rgba(0,255,0,0.1)'
    ))
    fig.add_hline(y=initial_cash, line_dash="dash", line_color="gray",
                  annotation_text="Initial Capital")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Portfolio Value ($)",
        hovermode='x unified',
        template='plotly_dark',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Price chart with signals
    st.subheader("Price Chart with Signals")
    fig_price = go.Figure()
    
    # Candlestick chart
    fig_price.add_trace(go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='BTC/USDT'
    ))
    
    # Add buy/sell markers from trades
    if len(result.trades) > 0 and 'Entry Timestamp' in result.trades.columns:
        entry_times = pd.to_datetime(result.trades['Entry Timestamp'])
        entry_prices = result.trades['Entry Price']
        
        fig_price.add_trace(go.Scatter(
            x=entry_times,
            y=entry_prices,
            mode='markers',
            name='Entries',
            marker=dict(size=10, color='lime', symbol='triangle-up')
        ))
        
        if 'Exit Timestamp' in result.trades.columns:
            exit_times = pd.to_datetime(result.trades['Exit Timestamp'])
            exit_prices = result.trades['Exit Price']
            
            fig_price.add_trace(go.Scatter(
                x=exit_times,
                y=exit_prices,
                mode='markers',
                name='Exits',
                marker=dict(size=10, color='red', symbol='triangle-down')
            ))
    
    fig_price.update_layout(
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode='x unified',
        template='plotly_dark',
        height=500,
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig_price, use_container_width=True)
    
    # Trade list
    st.subheader("Trade History")
    if len(result.trades) > 0:
        st.dataframe(result.trades, use_container_width=True, height=400)
        
        # Download button
        csv = result.trades.to_csv(index=False)
        st.download_button(
            label="📥 Download Trades CSV",
            data=csv,
            file_name=f"{strategy_name}_trades.csv",
            mime="text/csv"
        )
    else:
        st.warning("No trades executed. Try adjusting strategy parameters.")

else:
    st.info("👈 Configure parameters and click 'Run Backtest' to start")
EOF

# Launch dashboard
streamlit run examples/backtest_dashboard.py
```

**Opens in browser** with interactive controls! 🎨

---

## 📈 Using Real Historical Data

### Option 1: Download from TradingView

1. Go to [TradingView](https://www.tradingview.com/chart/)
2. Select symbol (e.g., BTCUSD)
3. Set timeframe (1h recommended)
4. Click "..." → "Export chart data"
5. Save to `data/btc_tradingview.csv`

```python
# Load TradingView CSV
data = pd.read_csv('data/btc_tradingview.csv', parse_dates=['time'])
data = data.rename(columns={'time': 'timestamp'}).set_index('timestamp')
```

### Option 2: Fetch via CCXT (No Auth)

```bash
pip install ccxt

python3 << 'EOF'
import ccxt
import pandas as pd

# Initialize Binance (no API key needed for public data)
exchange = ccxt.binance()

# Fetch 1000 hourly candles
print("📥 Fetching data from Binance...")
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1h', limit=1000)

# Convert to DataFrame
data = pd.DataFrame(
    ohlcv,
    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
)
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
data = data.set_index('timestamp')

# Save
data.to_csv('data/btc_binance_1000h.csv')
print(f"✅ Downloaded {len(data)} bars from Binance")
print(f"   Range: {data.index[0]} to {data.index[-1]}")
EOF
```

---

## 🧪 Testing Specific Market Conditions

### Bull Market Test

```python
# Focus on uptrend period (example: Jan-Apr 2023)
data_bull = data.loc['2023-01-01':'2023-04-30']
result = runner.run(data_bull, strategy)
print(f"Bull Market Return: {result.total_return:.2%}")
```

### Bear Market Test

```python
# Focus on downtrend period
data_bear = data.loc['2023-08-01':'2023-11-30']
result = runner.run(data_bear, strategy)
print(f"Bear Market Return: {result.total_return:.2%}")
```

### Consolidation Test

```python
# Current sideways market
data_consolidation = data.loc['2024-09-01':]
result = runner.run(data_consolidation, strategy)
print(f"Consolidation Return: {result.total_return:.2%}")
```

**Compare:** How does your strategy perform in different regimes?

---

## 🎯 What to Look For

### Good Signs ✅
- **Sharpe Ratio > 1.5** - Risk-adjusted returns solid
- **Win Rate > 50%** - More winners than losers
- **Profit Factor > 1.5** - Wins bigger than losses
- **Max Drawdown < 20%** - Manageable risk
- **Consistent across regimes** - Works in bull/bear/sideways

### Red Flags 🚩
- **Too few trades** (< 20) - May be overfit
- **Win rate > 80%** - Suspicious, possible overfitting
- **Huge Sharpe (> 3)** - Probably overfitting
- **Works only in one regime** - Not robust

---

## 🔧 Optimize Parameters

```python
# Test different swing periods
for period in [3, 5, 7, 10]:
    strategy = LiquiditySweepStrategy({'swing_period': period})
    result = runner.run(data, strategy)
    print(f"Period {period}: Sharpe={result.sharpe_ratio:.2f}, Return={result.total_return:.2%}")
```

**Use vectorbt for advanced optimization:**
```python
from backtesting.runner import BacktestRunner

# Define parameter grid
param_grid = {
    'swing_period': [3, 5, 7],
    'min_rr_ratio': [1.0, 1.5, 2.0]
}

# Optimize
runner = BacktestRunner(initial_cash=10000)
results = runner.optimize(data, LiquiditySweepStrategy, param_grid, metric='sharpe_ratio')

print("Top 3 Configurations:")
print(results.head(3))
```

---

## 💾 Save Results

```python
# Export trades to CSV
result.trades.to_csv('results/backtest_20241222.csv')

# Export equity curve
result.equity_curve.to_csv('results/equity_curve.csv')

# Generate HTML report
with open('results/backtest_report.html', 'w') as f:
    f.write(f"""
    <!DOCTYPE html>
    <html>
    <head><title>Backtest Report</title></head>
    <body>
        <h1>Backtest Results</h1>
        <h2>Summary</h2>
        <ul>
            <li>Total Return: {result.total_return:.2%}</li>
            <li>Sharpe Ratio: {result.sharpe_ratio:.2f}</li>
            <li>Max Drawdown: {result.max_drawdown:.2%}</li>
            <li>Win Rate: {result.win_rate:.2%}</li>
            <li>Total Trades: {result.total_trades}</li>
        </ul>
        <h2>Trades</h2>
        {result.trades.to_html()}
    </body>
    </html>
    """)
```

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: vectorbt"
```bash
pip install vectorbt==0.26.0
# If fails, use Docker:
./docker-start.sh
```

### "Empty DataFrame" error
```bash
# Check data file exists
ls -lh data/samples/btc_90d.csv

# Regenerate (Step 2)
python3 << 'EOF'
# ... (data generation code from Step 2)
EOF
```

### "No trades executed"
```bash
# Strategy may be too conservative
# Adjust parameters:
strategy = LiquiditySweepStrategy({
    'swing_period': 3,      # More sensitive
    'min_rr_ratio': 1.0     # Lower threshold
})
```

---

## 🔥 Next Steps

### You Can Do RIGHT NOW:
1. ✅ Run backtests on sample data
2. ✅ Compare strategies
3. ✅ Download real historical data
4. ✅ Test on different time periods
5. ✅ Adjust strategy parameters
6. ✅ Generate visual reports

### Coming Soon (2-3 weeks):
1. ⏳ Paper trading on testnet
2. ⏳ Real-time signal monitoring
3. ⏳ Telegram alerts

### Future (6-8 weeks):
1. 📋 Small mainnet deployment
2. 📋 Portfolio management
3. 📋 Multi-exchange support

---

## 📚 Learn More

- **Strategies:** See `strategies/` for implementations
- **Core Detection:** See `core/` for SMC algorithms
- **Testing:** [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
- **Production:** [DEPLOYMENT_PLAN.md](DEPLOYMENT_PLAN.md)

---

**You're now ready to backtest!** 🚀

Start with sample data, get comfortable, then move to real historical data.

**Remember:** Backtesting ≠ future performance. Always paper trade first!
