# Valuation Policy Template
## NAV Calculation & Asset Pricing Procedures

---

## VALUATION POLICY

**Fund Name:** [FUND NAME] LP  
**Effective Date:** [Date]  
**Valuation Committee:** [Names]

---

## 1. OVERVIEW

### 1.1 Purpose
This policy establishes procedures for the fair and accurate valuation of Fund assets and calculation of Net Asset Value (NAV).

### 1.2 Regulatory Framework
| Requirement | Reference |
|-------------|-----------|
| Fair valuation | Investment Company Act §2(a)(41) |
| Valuation policies | SEC Rule 2a-5 |
| Custody/NAV | Advisers Act Rule 206(4)-2 |

---

## 2. NAV CALCULATION

### 2.1 Frequency
- [x] **Daily** (market close)
- [ ] Weekly
- [ ] Monthly

### 2.2 Valuation Time
**4:00 PM Eastern Time** (US market close)

### 2.3 NAV Formula
```
NAV = (Total Assets - Total Liabilities) / Total Units Outstanding

Per-Unit NAV = NAV / Number of Outstanding Units
```

### 2.4 Components

**Assets:**
- Cash and cash equivalents
- Securities at fair value
- Accrued interest/dividends
- Receivables

**Liabilities:**
- Accrued management fee
- Accrued performance fee (if applicable)
- Accounts payable
- Redemptions payable

---

## 3. SECURITY VALUATION

### 3.1 Exchange-Traded Securities (Including TQQQ)

| Security Type | Valuation Method | Pricing Source |
|---------------|------------------|----------------|
| Listed ETFs (TQQQ, GLD, etc.) | Last trade price | Bloomberg/Reuters |
| Listed stocks | Last trade price | Primary exchange |
| Options | Mid-point bid/ask | Exchange data |

**TQQQ Specific:**
- Use official 4:00 PM closing price from NYSE Arca
- If trading halted: Use last available trade price + disclosure
- If market disruption: See Section 5

### 3.2 Pricing Hierarchy
1. **Level 1**: Quoted prices in active markets (preferred)
2. **Level 2**: Observable inputs (comparable securities)
3. **Level 3**: Unobservable inputs (model-based)

For a TQQQ strategy, nearly all positions should be Level 1.

### 3.3 Pricing Sources
| Priority | Source |
|----------|--------|
| Primary | Prime broker (Interactive Brokers) |
| Secondary | Bloomberg |
| Tertiary | Reuters/Refinitiv |

---

## 4. CASH & EQUIVALENTS

| Asset | Valuation |
|-------|-----------|
| Bank deposits | Face value |
| Money market funds | NAV per share |
| T-Bills < 90 days | Amortized cost |
| T-Bills > 90 days | Market value |

---

## 5. MARKET DISRUPTION EVENTS

### 5.1 Definition
A market disruption event includes:
- Exchange closure (unscheduled)
- Trading halt in key securities
- Extreme volatility (circuit breakers triggered)
- Natural disaster affecting markets
- Cyber attack on exchange systems

### 5.2 TQQQ Trading Halt Procedures
If TQQQ trading is halted:
1. Use last available trade price
2. Estimate NAV using QQQ (underlying) × 3 as proxy
3. Document reasoning and methodology
4. Disclose to investors if material

### 5.3 Stale Pricing
If closing price is more than 24 hours old:
- Flag as stale
- Consider fair value adjustment
- Document rationale

---

## 6. FAIR VALUE ADJUSTMENTS

### 6.1 When Required
Fair value adjustments may be needed when:
- Market closes before Fund's valuation time
- Security is thinly traded
- Significant event occurs after market close
- Quoted price doesn't reflect fair value

### 6.2 Adjustment Process
1. Identify triggering event
2. Gather relevant information
3. Make adjustment with documented rationale
4. Valuation Committee approval
5. Retain documentation

---

## 7. VALUATION COMMITTEE

### 7.1 Composition
- Portfolio Manager
- Chief Compliance Officer
- CFO/Controller (if applicable)

### 7.2 Responsibilities
- Approve valuation policies
- Review Level 3 valuations
- Assess fair value adjustments
- Annual policy review

### 7.3 Meeting Frequency
- Quarterly (minimum)
- Ad-hoc for material events

---

## 8. ERROR CORRECTION

### 8.1 Materiality Threshold
| Error Size | Action |
|------------|--------|
| < 0.25% of NAV | Correct prospectively; no restatement |
| 0.25% - 0.50% | Correct; notify impacted investors |
| > 0.50% | Restate NAV; make investors whole |

### 8.2 Correction Process
1. Identify error
2. Calculate impact
3. Determine materiality
4. Notify CCO
5. Document correction
6. Notify investors (if material)

---

## 9. RECORD RETENTION

| Record | Retention |
|--------|-----------|
| Daily NAV calculations | 5 years |
| Pricing source data | 5 years |
| Fair value adjustments | 5 years |
| Valuation Committee minutes | 5 years |

---

## 10. LEVERAGED ETF SPECIFIC CONSIDERATIONS

### 10.1 Daily Rebalancing Impact
TQQQ rebalances daily to maintain 3x exposure. This affects valuation in that:
- End-of-day price reflects post-rebalance value
- Intraday NAV estimates may differ from close

### 10.2 Volatility Decay in NAV
When calculating performance:
- Use actual TQQQ prices (which include decay)
- Do NOT calculate hypothetical 3x returns
- Document any performance attribution separately

### 10.3 Creation/Redemption NAV
TQQQ has its own NAV (published by ProShares). The Fund's TQQQ position should be valued at:
- [ ] TQQQ market price (standard)
- [ ] TQQQ NAV (less common)

---

## APPENDIX: SAMPLE NAV CALCULATION

**Date:** [Date]  
**Valuation Time:** 4:00 PM ET

| Asset | Quantity | Price | Value |
|-------|----------|-------|-------|
| TQQQ | 10,000 | $50.00 | $500,000 |
| GLD | 5,000 | $180.00 | $900,000 |
| Cash | - | - | $100,000 |
| **Total Assets** | | | **$1,500,000** |

| Liability | Amount |
|-----------|--------|
| Accrued Mgmt Fee | $7,500 |
| Accrued Expenses | $2,500 |
| **Total Liabilities** | **$10,000** |

**NAV = $1,500,000 - $10,000 = $1,490,000**

---

*This template should be reviewed by legal and accounting professionals.*
