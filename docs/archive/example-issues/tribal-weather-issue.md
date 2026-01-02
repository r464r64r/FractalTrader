---
name: 💡 Feature Idea
about: Spark from the free electron (Filip's ideas)
title: '[IDEA] Tribal Weather - Crypto Ecosystem Capital Flow Analysis'
labels: 'idea, needs-analysis, feature/tribal'
assignees: ''
---

## 🌟 The Spark

**Rynek krypto to nie jeden ocean - to archipelag plemion.**

Co jeśli FractalTrader pokazywałby **tribal weather map**:

```
┌─────────────────────────────────────────────┐
│ 🌍 CRYPTO TRIBAL WEATHER                    │
├─────────────────────────────────────────────┤
│ BTC Maxi Camp:     ☀️ Sunny (BTC.D ↑ 54%)  │
│ Ethereum Nation:   ⛅ Partly cloudy         │
│ Solana Gang:       🌧️ Rainy (TVL -12%)     │
│ Meme Degenerates:  ⛈️ Stormy               │
│ DeFi Farmers:      🌤️ Clearing             │
├─────────────────────────────────────────────┤
│ Capital Flow: BTC ← ETH ← Alts              │
│ Regime: Early Bear (risk-off rotation)     │
│ Next rotation: 2-4 weeks (historically)    │
└─────────────────────────────────────────────┘
```

**Plus tribal rotation detection:**
- When BTC.D rises → alt season ending → capital flowing to safety
- When funding rates extreme → liquidation cascade coming → tribe wipeout
- When social volume spikes → retail FOMO → tribe about to get rekt

**Result:** Trade WITH the rotation, not against it.

## 🎯 Why This Matters

**Problem:**
1. CryptoWeather shows single asset predictions (BTC up/down)
2. No context WHY capital is moving
3. No understanding of tribal dynamics
4. Traders fight the rotation (long alts in BTC dominance rise)

**Solution:**
- **Tribal clustering:** Auto-group coins by ecosystem/narrative
- **Flow detection:** Track capital rotation between tribes
- **Weather metaphors:** Intuitive "pressure systems" (funding, leverage)
- **Rotation prediction:** Historical patterns + current signals

**Edge over CryptoWeather:**
- They predict price direction (what)
- We understand capital flow (why)
- They use lagging indicators (RSI, MACD)
- We use tribal positioning (leading indicator)

## 🤔 Initial Thoughts

### Tribal Clustering (bottom-up approach)

**Tribes identified so far:**
1. BTC Maximalists (BTC only)
2. Ethereum Nation (ETH + ERC-20 DeFi)
3. Solana Gang (SOL + SPL ecosystem)
4. Meme Degenerates (DOGE, SHIB, PEPE, WIF)
5. DeFi Yield Farmers (AAVE, UNI, CRV)
6. Privacy Purists (XMR, ZEC)
7. AI/Infrastructure (RENDER, FET, TAO)
8. Gaming/Metaverse (IMX, GALA, SAND)
9. Institutional Bridge (XRP, XLM, LINK)
10. Cosmos/IBC (ATOM, OSMO, INJ, TIA)

**Metrics per tribe:**
```python
class TribeMetrics:
    dominance: float        # % of total market cap
    momentum: float         # 7d/30d return vs market
    social_volume: float    # Twitter mentions, Reddit posts
    new_wallets: int        # Fresh retail interest
    whale_flow: float       # Large holder movements
    funding_avg: float      # Avg funding across tribe
```

### Weather Layers (meteorology analogy)

**Temperature = Volatility**
- Cold: <1% daily ATR (ranging, accumulation)
- Warm: 1-3% (normal activity)
- Hot: >3% (mania, distribution)

**Pressure = Leverage/Funding**
- High: Funding >0.05%, overleveraged (liquidations coming)
- Normal: Funding 0-0.03%
- Low: Funding <0%, shorts squeezed

**Wind = Directional Bias**
- North (bullish): CVD positive, OI growing
- South (bearish): CVD negative, OI shrinking
- Calm: No clear direction (chop)

**Precipitation = Volatility Events**
- Clear: Tight ranges, predictable
- Cloudy: Choppy, fake breakouts
- Rainy: Cascades, stop hunts
- Stormy: Flash crashes, liquidations

### Capital Flow Detection

**Rotation Cycle (empirical):**
```
Phase 1: BTC pumps first (21-30 days)
  → Maxi weather: ☀️ Sunny
  → Alt weather: 🌧️ Rainy
  
Phase 2: ETH follows (14-21 days)
  → ETH weather: ☀️ Sunny
  → BTC weather: ⛅ Cooling
  
Phase 3: Large cap alts (7-14 days)
  → Infrastructure weather: ☀️ Sunny
  → Everything else: ⛅ Warming
  
Phase 4: Small cap mania (3-7 days)
  → Meme weather: ⛈️ FOMO storm
  → Smart money: 🌤️ Exiting
  
Phase 5: Everything dumps
  → BTC weather: ☀️ Back to safety
  → Alt weather: ⛈️ Nuclear winter
```

**Indicators:**
- BTC Dominance (primary)
- ETH/BTC ratio (secondary)
- Funding rates across tribes
- Social volume spikes
- Exchange flows (on-chain)

### Integration with Trading

```python
if tribal_weather.regime == 'BTC_DOMINANCE_RISING':
    strategy.avoid(['ALTS'])
    strategy.focus(['BTC', 'STABLES'])
    
elif tribal_weather.regime == 'ALT_SEASON':
    strategy.increase_exposure(['ETH_ECOSYSTEM', 'SOL_ECOSYSTEM'])
    strategy.watch_for_rotation()  # doesn't last forever
    
elif tribal_weather.regime == 'MEME_MANIA':
    strategy.reduce_size(0.5)  # extreme risk
    strategy.set_tight_stops()
```

## 📎 Context

**Competitor Analysis:**
- **CryptoWeather.xyz:** RNN predictions, single asset focus, no tribal context
- **LunarCrush:** Social sentiment, but no tribal clustering
- **Santiment:** On-chain metrics, complex, expensive
- **Glassnode:** Bitcoin-centric, not tribal

**Our Edge:**
- Open source
- Multi-tribe perspective
- Weather metaphor (intuitive)
- Integrated with SMC (institutional + tribal context)

**Data Sources (free APIs):**
- BTC Dominance: CoinGecko, CoinMarketCap
- Funding rates: Coinglass, Binance
- Social volume: LunarCrush free tier
- Price/volume: CCXT (already integrated)

**Data Sources (premium, later):**
- On-chain flows: Glassnode
- Whale alerts: WhaleAlert
- Exchange flows: CryptoQuant

**From chat:**
> "Tribal dynamics - to jest genialne do crypto weather, 
> bo rynek krypto to nie jeden ocean, to archipelag."

---

**Status:** Needs Opus analysis  
**Next Step:** Strategic breakdown & research tasks

---

## Expected Opus Breakdown

(This will be added by Opus in comments)

**Research tasks:**
- [ ] Tribal clustering methodology (manual vs algo)
- [ ] Capital flow indicators (BTC.D, funding, social)
- [ ] Historical rotation patterns analysis
- [ ] Free vs premium data sources comparison
- [ ] Weather metaphor mapping (which metrics = which weather)

**Implementation tasks:**
- [ ] Tribal definitions & coin mapping
- [ ] Tribe metrics calculation
- [ ] Weather scoring algorithm
- [ ] Rotation detection logic
- [ ] Dashboard widget (simple text first)

**Integration:**
- [ ] Connect to data fetchers (multi-symbol support)
- [ ] Strategy confidence adjustment (weather-aware)
- [ ] Jupyter dashboard (tribal weather panel)

**Phasing:**
- MVP: BTC.D only, simple text output
- V1: 5 main tribes, basic weather
- V2: Full 10 tribes, rotation prediction
- V3: On-chain integration, advanced metrics
