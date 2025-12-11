# TQQQ 200MA / IAUM Strategy - Risk Rules
## Position Limits & Risk Management Policy

---

## STRATEGY RISK MANAGEMENT DOCUMENT

**Fund Name:** [FUND NAME] LP  
**Effective Date:** [Date]

---

## 1. STRATEGY OVERVIEW

### 1.1 The Strategy
```
IF TQQQ > 200-day SMA → 100% TQQQ
ELSE                  → 100% IAUM
```

### 1.2 Position Characteristics
| State | TQQQ Allocation | IAUM Allocation |
|-------|-----------------|-----------------|
| **Bullish** (TQQQ > 200MA) | 100% | 0% |
| **Bearish** (TQQQ ≤ 200MA) | 0% | 100% |

---

## 2. POSITION LIMITS

### 2.1 Strategy-Specific Limits

| Parameter | Limit | Rationale |
|-----------|-------|-----------|
| Maximum TQQQ allocation | **100%** | Binary strategy design |
| Minimum IAUM allocation (defensive) | **100%** when signal is bearish |
| Maximum gross exposure | 100% of NAV | Fully funded, no leverage |
| Cash reserve | 0-2% for execution | Minimize cash drag |

### 2.2 Key Principles
- ✅ **Binary allocation** - Always 100% in one position
- ✅ **Fully funded** - No margin borrowing
- ✅ **Single signal** - 200-day SMA only
- ❌ **No partial positions** - Either 100% TQQQ or 100% IAUM

---

## 3. RISK LIMITS

### 3.1 Maximum Drawdown Tolerance
| Threshold | Action |
|-----------|--------|
| -25% NAV from peak | Review strategy parameters |
| -35% NAV from peak | Consider temporary strategy pause |
| -50% NAV from peak | Emergency Investment Committee review |

### 3.2 Whipsaw Protection
When TQQQ price oscillates near the 200MA, multiple trades may occur. 

**Mitigation Options (choose one if needed):**
- [ ] Accept whipsaws as cost of protection
- [ ] Add 1% buffer zone (cross must exceed 1%)
- [ ] Require 3-day confirmation above/below MA
- [ ] Limit trades to [X] per month maximum

**Current Policy**: Accept whipsaws as cost of protection

---

## 4. 200-DAY MOVING AVERAGE CALCULATION

### 4.1 Specification
| Parameter | Value |
|-----------|-------|
| Type | Simple Moving Average (SMA) |
| Period | 200 trading days |
| Applied to | TQQQ closing price |
| Data source | Yahoo Finance / Bloomberg |

### 4.2 Calculation
```
SMA(200) = (P₁ + P₂ + ... + P₂₀₀) / 200

Where P₁ = most recent closing price
      P₂₀₀ = closing price 200 trading days ago
```

### 4.3 Signal Timing
| Event | Time |
|-------|------|
| Price data collection | After 4:00 PM ET market close |
| Signal calculation | 4:00 PM - 5:00 PM ET |
| Trade execution | Next trading day, 9:30 AM - 10:00 AM ET |

---

## 5. TQQQ-SPECIFIC RISKS

### 5.1 Volatility Decay
TQQQ's 3x leverage resets **daily**. This causes "volatility decay" in choppy markets.

| Market Condition | Effect on TQQQ |
|------------------|----------------|
| Strong uptrend | 3x gains (compounding helps) |
| Strong downtrend | 3x losses (compounding hurts less than expected) |
| Sideways/volatile | Decay - cumulative losses even if index unchanged |

**How 200MA Helps**: By exiting TQQQ during downtrends/sideways markets, we aim to avoid the worst decay periods.

### 5.2 Gap Risk
Overnight gaps can cause significant losses before signal changes.

| Scenario | Example |
|----------|---------|
| Weekend gap down | TQQQ closes Friday > 200MA, opens Monday -15% |
| Earnings shock | Major tech earnings after hours |
| Macro event | Fed announcement, geopolitical crisis |

**Mitigation**: Accept as inherent risk; 200MA filter provides medium-term protection but not overnight protection.

### 5.3 Signal Lag
The 200-day SMA is a lagging indicator by design.

| Concern | Reality |
|---------|---------|
| Slow to signal downtrend | May lose 5-15% before exit signal |
| Slow to re-enter uptrend | May miss 5-15% of new rally |
| Overall effect | Portfolio undershoots both extremes |

---

## 6. IAUM (GOLD) CONSIDERATIONS

### 6.1 Why IAUM?
| Factor | IAUM Advantage |
|--------|---------------|
| Expense ratio | 0.09% (lowest gold ETF) |
| Physical backing | 100% physical gold in London vaults |
| Correlation | Low/negative correlation to equities in crises |
| Liquidity | Good (though lower than GLD) |

### 6.2 IAUM Risks
| Risk | Description |
|------|-------------|
| Gold bear market | Gold can decline for extended periods |
| Opportunity cost | May underperform while TQQQ rallies |
| Lower liquidity than GLD | Wider spreads possible in stress |

---

## 7. OPERATIONAL PROCEDURES

### 7.1 Daily Checklist
- [ ] Get TQQQ closing price (after 4 PM ET)
- [ ] Calculate 200-day SMA
- [ ] Compare: Is TQQQ > 200MA?
- [ ] If signal changed: Prepare trade for next day
- [ ] Log signal and any actions

### 7.2 Trade Execution
| Step | Action |
|------|--------|
| 1 | Confirm signal change (close > or < 200MA) |
| 2 | Calculate trade size (100% of portfolio) |
| 3 | Place order: Sell current position, Buy new position |
| 4 | Verify execution |
| 5 | Update records |

---

## 8. PPM DISCLOSURE LANGUAGE

Include in Private Placement Memorandum:

> **Strategy**: The Fund employs a trend-following strategy that maintains 100% allocation to TQQQ (ProShares UltraPro QQQ, a 3x leveraged ETF) when TQQQ's price is above its 200-day simple moving average, and rotates to 100% allocation in IAUM (iShares Gold Trust Micro) when TQQQ's price is at or below its 200-day moving average.
>
> **Concentration Risk**: Due to the binary nature of the strategy, the Fund will always be 100% concentrated in a single ETF at any given time. This concentration increases both upside potential and downside risk.
>
> **Leveraged ETF Risks**: TQQQ is a 3x leveraged ETF that resets daily. Positions held for longer than one day may experience returns that differ significantly from 3× the underlying index return. See "Volatility Decay Disclosure" for detailed explanation.

---

## 9. REGULATORY REFERENCES

| Topic | Reference |
|-------|-----------|
| Leveraged ETF suitability | [FINRA Notice 09-31](https://www.finra.org/rules-guidance/notices/09-31) |
| Suitability obligations | [FINRA Rules 2111, 2090](https://www.finra.org/rules-guidance/rulebooks/finra-rules) |
| Margin requirements | [Regulation T (12 CFR 220)](https://www.ecfr.gov/current/title-12/chapter-II/subchapter-A/part-220) |
| Gold ETF tax treatment | IRS - Collectibles (28% max rate for gains) |

---

*This policy should be reviewed and approved by legal counsel before implementation.*
