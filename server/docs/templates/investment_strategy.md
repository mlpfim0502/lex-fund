# Investment Strategy & Thesis
## TQQQ 200MA / IAUM Rotation Strategy

---

## FUND INVESTMENT STRATEGY DOCUMENT

**Fund Name:** [FUND NAME] LP  
**Prepared By:** [Manager Name]  
**Date:** [Date]  
**Version:** 1.0

---

## 1. EXECUTIVE SUMMARY

### 1.1 Strategy Name
**TQQQ 200MA Trend-Following Rotation Strategy**

### 1.2 One-Sentence Description
The Fund seeks to generate superior risk-adjusted returns by maintaining 100% allocation to TQQQ (3x leveraged NASDAQ-100) when TQQQ trades above its 200-day moving average, and rotating to 100% IAUM (iShares Gold Trust) when TQQQ trades below its 200-day moving average.

### 1.3 Key Features
- **Simple, rules-based approach** - No discretion, mechanical execution
- **Binary allocation** - Always 100% in one of two positions
- **Trend-following** - Uses 200-day moving average as primary signal
- **Defensive rotation** - Gold (IAUM) as safe haven during downtrends

---

## 2. STRATEGY RULES

### 2.1 Primary Signal Logic

```
IF TQQQ price > TQQQ 200-day Simple Moving Average:
    → 100% TQQQ

ELSE (TQQQ price ≤ TQQQ 200-day SMA):
    → 100% IAUM
```

### 2.2 Signal Details

| Parameter | Value |
|-----------|-------|
| **Indicator** | 200-day Simple Moving Average (SMA) |
| **Applied To** | TQQQ closing prices |
| **Signal Check** | Daily at market close |
| **Execution** | Next trading day open |

### 2.3 Instruments

| Ticker | Name | Role | Expense Ratio |
|--------|------|------|---------------|
| **TQQQ** | ProShares UltraPro QQQ | 3x Long NASDAQ-100 | 0.86% |
| **IAUM** | iShares Gold Trust Micro | Gold exposure (safe haven) | 0.09% |

---

## 3. INVESTMENT THESIS

### 3.1 Why This Works

1. **Trend Persistence**: Markets tend to trend. The 200-day MA captures major market regimes (bull vs bear).

2. **Crash Protection**: By exiting TQQQ when it breaks below the 200-day MA, we aim to avoid the worst of bear market drawdowns.

3. **Gold as Safe Haven**: IAUM provides:
   - Low/negative correlation to equities during crises
   - Inflation hedge
   - Store of value during uncertainty

4. **Leverage with Protection**: TQQQ's 3x leverage amplifies gains during confirmed uptrends, while the rotation mechanism limits exposure during downtrends.

### 3.2 Why 200-Day Moving Average?

- **Widely followed**: Institutional and retail investors use 200MA as bull/bear market indicator
- **Self-fulfilling**: High awareness creates actual support/resistance
- **Historically validated**: Backtests show strong risk-adjusted returns
- **Low turnover**: Fewer signals = lower transaction costs

### 3.3 Why IAUM Over Other Defensive Assets?

| Alternative | Why IAUM is Preferred |
|-------------|----------------------|
| Cash/Money Market | Zero/low yield, no crisis alpha |
| TLT (Long-term Treasuries) | High interest rate sensitivity |
| GLD | Higher expense ratio (0.40% vs 0.09%) |
| SHY (Short-term Treasuries) | Low yield, minimal crisis protection |

---

## 4. RISK MANAGEMENT

### 4.1 Key Risks

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Volatility Decay** | TQQQ 3x leverage resets daily, causing decay in volatile/sideways markets | Trend filter (200MA) avoids choppy periods |
| **Whipsaw** | False signals when price oscillates around 200MA | Accept as cost of protection |
| **Gap Risk** | Overnight moves can cause large losses | Diversified signal timing |
| **Gold Correlation** | IAUM may not always provide protection | Historical low/negative correlation |

### 4.2 TQQQ-Specific Risks
- **Daily 3x Reset**: Returns over periods >1 day may differ significantly from 3x index return
- **Compounding Effect**: Works in favor during trending markets, against during volatile markets
- **Counterparty Risk**: TQQQ uses swaps; check prospectus for counterparty details

### 4.3 Drawdown Expectations

| Scenario | Expected Max Drawdown |
|----------|----------------------|
| Bull market correction | 15-25% |
| Bear market (protected) | 20-35% |
| Flash crash | Up to 30% intraday |

---

## 5. OPERATIONAL DETAILS

### 5.1 Signal Calculation
- **Data Source**: Yahoo Finance / Bloomberg / Broker API
- **Calculation Time**: After 4:00 PM ET close
- **200-day SMA**: Simple arithmetic mean of last 200 closing prices

### 5.2 Trade Execution
- **Signal Day**: Day 0 (market close)
- **Execution Day**: Day 1 (market open or VWAP)
- **Order Type**: Market or Limit (within 0.1% of open)
- **Broker**: Interactive Brokers (recommended for low margin rates)

### 5.3 Rebalancing
- **Only on signal change**: No rebalancing when position matches signal
- **Expected annual trades**: 4-8 round-trips historically
- **Tax efficiency**: Long-term holds possible during extended trends

---

## 6. HISTORICAL PERFORMANCE (BACKTEST)

> ⚠️ **DISCLAIMER**: Past performance does not guarantee future results. Backtests are hypothetical and do not account for all real-world conditions.

| Metric | Strategy | Buy-Hold QQQ | Buy-Hold TQQQ |
|--------|----------|--------------|---------------|
| CAGR | [X]% | [X]% | [X]% |
| Max Drawdown | [X]% | [X]% | [X]% |
| Sharpe Ratio | [X] | [X] | [X] |
| # of Trades/Year | [X] | 0 | 0 |

---

## 7. FEE STRUCTURE

| Fee Type | Amount |
|----------|--------|
| Management Fee | [2]% of NAV annually |
| Performance Fee | [20]% of profits above high-water mark |
| Hurdle Rate | [0]% (or risk-free rate) |

---

## 8. REGULATORY CONSIDERATIONS

### 8.1 Required Disclosures
- FINRA Notice 09-31: Leveraged ETF suitability
- Volatility decay explanation (see separate document)
- Position limits and concentration risk

### 8.2 Investor Suitability
- Accredited investors only
- Suitable for investors with high risk tolerance
- Not suitable for short-term investors

---

## APPENDIX A: SIGNAL PSEUDOCODE

```python
def calculate_signal(tqqq_prices):
    """
    Calculate trading signal based on 200-day SMA
    
    Args:
        tqqq_prices: List of TQQQ closing prices (most recent last)
    
    Returns:
        'TQQQ' or 'IAUM'
    """
    if len(tqqq_prices) < 200:
        return 'IAUM'  # Insufficient data, stay defensive
    
    sma_200 = sum(tqqq_prices[-200:]) / 200
    current_price = tqqq_prices[-1]
    
    if current_price > sma_200:
        return 'TQQQ'
    else:
        return 'IAUM'
```

---

## APPENDIX B: IAUM vs GLD COMPARISON

| Feature | IAUM | GLD |
|---------|------|-----|
| Expense Ratio | 0.09% | 0.40% |
| AUM | $1B+ | $50B+ |
| Liquidity | Good | Excellent |
| Structure | Grantor Trust | Grantor Trust |
| Physical Gold | Yes | Yes |

**Recommendation**: IAUM for lower costs; GLD if liquidity is critical.

---

*This document is for internal use only and should be reviewed by legal counsel before incorporation into offering documents.*
