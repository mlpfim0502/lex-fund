# Volatility Decay Disclosure Template
## For Private Placement Memorandum - Leveraged ETF Section

---

## IMPORTANT DISCLOSURE: LEVERAGED ETF RISKS

### What is Volatility Decay?

The Fund may invest in leveraged exchange-traded funds ("Leveraged ETFs"), including the ProShares UltraPro QQQ (ticker: TQQQ), which seeks daily investment results that correspond to **three times (3x)** the daily performance of the NASDAQ-100 Index.

> **⚠️ CRITICAL WARNING**
> 
> Leveraged ETFs are designed to achieve their stated objective on a **DAILY** basis only. Due to the effects of compounding, performance over periods longer than one day will likely differ—sometimes significantly—from the stated multiple of the index return.

---

### How Volatility Decay Works

When an index experiences volatility (up and down movements), a leveraged ETF will lose value even if the index returns to its starting point. This effect is called **volatility decay** or **beta slippage**.

#### Numerical Example

| Day | QQQ (Index) | TQQQ (3x Leveraged) |
|-----|-------------|---------------------|
| Start | $100.00 | $100.00 |
| Day 1: +5% | $105.00 | $115.00 (+15%) |
| Day 2: -5% | $99.75 | $97.75 (-15%) |
| **Net Change** | **-0.25%** | **-2.25%** |

**Expected**: If QQQ lost 0.25%, TQQQ should lose 0.75% (3 × 0.25%)  
**Actual**: TQQQ lost 2.25% — **3x worse than expected**

This occurs because:
- Day 1: $100 × 1.15 = $115.00
- Day 2: $115 × 0.85 = $97.75
- The leverage compounds against itself on down days

---

### Extended Volatility Scenarios

| 20-Day Scenario | QQQ Return | Expected TQQQ (3x) | Actual TQQQ | Decay |
|----------------|------------|-------------------|-------------|-------|
| Quiet uptrend (+0.5%/day) | +10.5% | +31.5% | +33.1% | +1.6% ✅ |
| Volatile flat (±2%/day) | -0.4% | -1.2% | -11.3% | -10.1% ❌ |
| Sharp decline (-3%/day) | -45.6% | -136.8% | -99.5% | +37.3% (less loss due to math) |
| High volatility (+5%, -5% alternating) | -4.9% | -14.7% | -40.1% | -25.4% ❌ |

---

### FINRA Regulatory Notice 09-31 Summary

In June 2009, FINRA issued Regulatory Notice 09-31 regarding leveraged and inverse ETFs:

> "Inverse and leveraged ETFs that are reset daily typically are unsuitable for retail investors who plan to hold them for longer than one trading session, particularly in volatile markets."

**Key Points from FINRA 09-31:**

1. Daily rebalancing can cause returns to deviate significantly from the underlying index over time
2. In volatile markets, these deviations can be substantial
3. Investors should understand the products and monitor them frequently
4. These products are generally designed for short-term trading, not buy-and-hold

**Full Notice**: [FINRA Notice 09-31](https://www.finra.org/rules-guidance/notices/09-31)

---

### Fund's Risk Mitigation Measures

To mitigate the risks associated with leveraged ETF volatility decay, the Fund implements the following strategy:

**200-Day Moving Average Rotation Strategy:**

The Fund uses a simple, rules-based approach to manage TQQQ volatility decay risk:

| Condition | Action |
|-----------|--------|
| TQQQ > 200-day SMA | 100% TQQQ |
| TQQQ ≤ 200-day SMA | 100% IAUM (gold) |

**Why This Helps:**

1. **Trend Filter**: The 200-day MA keeps the Fund in TQQQ only during confirmed uptrends, when volatility decay is typically lower or works in favor of the strategy.

2. **Crisis Exit**: Breaking below the 200MA typically signals a trend change, triggering rotation to gold before the worst volatility decay occurs.

3. **Gold as Safe Haven**: IAUM (iShares Gold Trust Micro) provides protection during market stress with 0.09% expense ratio.

4. **Historical Benefit**: Backtests suggest this approach captures much of TQQQ's upside while avoiding extended bear market decay.

---

### Investor Acknowledgment

By investing in the Fund, you acknowledge that:

- [ ] I understand that leveraged ETFs like TQQQ are designed for daily returns only
- [ ] I understand that volatility decay can cause significant losses even when the underlying index is flat or positive
- [ ] I have read and understand FINRA Regulatory Notice 09-31
- [ ] I understand that the Fund may hold leveraged ETFs for periods longer than one day
- [ ] I accept the risks associated with leveraged ETF investing

---

*This disclosure is provided pursuant to investor protection requirements and should be read in conjunction with the full Private Placement Memorandum risk factors section.*
