# Cashflow Module: CFO / Liquidity Layer

> **Purpose**: Track all cash inflows, outflows, debt obligations, and liquidity reserves. Produce the runway snapshot that tells the family office how many months of operating capacity they have at any moment.

This module is the operational backbone of **Barbell Layer 1: Liquidity Runway**. It also receives distributions and rental income from Layers 2 and 3.

---

## 1. Data Model

### CashFlowSource

Represents a recurring or one-time source of cash inflow or outflow.

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | UUID | Unique identifier | `csrc_a1b2c3d4...` |
| `name` | string | Human label | `"Downtown Loft — Rental Income"` |
| `type` | enum | `rental`, `dividend`, `operating`, `interest`, `distribution`, `debt-service`, `capex`, `operating-expense` | `rental` |
| `deal_ref` | string or null | Path to `deal.json` for deal-linked sources | `"deals/downtown-loft-portfolio/deal.json"` |
| `active` | bool | Is this source currently active? | `true` |
| `notes` | string | Any context | `"3-unit building, leases expire June 2027"` |

### CashFlowItem

A single cash event in a specific period.

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | UUID | Unique identifier | `cfi_b2c3d4e5...` |
| `source_id` | UUID | FK to CashFlowSource | `csrc_a1b2c3d4...` |
| `period` | string | `YYYY-MM` | `"2026-06"` |
| `amount_usd` | number | Positive = inflow, negative = outflow | `12500` (rental) or `-3200` (mortgage) |
| `category` | enum | `rental-income`, `dividend`, `distribution`, `interest-income`, `operating-revenue`, `debt-service`, `capex`, `operating-expense`, `tax-payment` | `rental-income` |
| `notes` | string | Any variance notes | `"Unit 2 vacancy July — prorated"` |
| `provenance` | object | source, timestamp, author, file_hash | — |

### DebtService

Tracks each loan/mortgage/credit facility.

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | UUID | Unique identifier | — |
| `deal_ref` | string | Path to associated `deal.json` | `"deals/downtown-loft-portfolio/deal.json"` |
| `lender` | string | Lender name | `"First National Bank"` |
| `loan_type` | string | `mortgage`, `LOC`, `term-loan`, `bridge` | `mortgage` |
| `balance_usd` | number | Outstanding principal | `1850000` |
| `rate` | number | Annual interest rate (decimal) | `0.0625` (= 6.25%) |
| `rate_type` | enum | `fixed`, `variable`, `floating` | `fixed` |
| `payment_usd` | number | Monthly P&I payment | `12800` |
| `maturity_date` | date | Loan maturity | `"2032-07-01"` |
| `dscr` | number | Debt Service Coverage Ratio = NOI / Annual Debt Service | `1.07` |
| `ltv_pct` | number | Loan-to-value percentage | `64.9` |

### LiquidityBucket

Tracks balance by bucket (operating, reserve, deployment).

| Field | Type | Description | Example |
|---|---|---|---|
| `name` | enum | `operating`, `reserve`, `deployment` | `operating` |
| `balance_usd` | number | Current balance | `285000` |
| `as_of_date` | date | Balance date | `"2026-06-23"` |
| `institution` | string | Where this cash lives | `"Chase Business Checking"` |
| `notes` | string | Context | `"Main operating account — covers payroll, vendors"` |

### RunwaySnapshot

Point-in-time snapshot of liquidity position.

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | UUID | — | — |
| `as_of_date` | date | Snapshot date | `"2026-06-23"` |
| `monthly_burn_usd` | number | Average monthly cash outflows (6-month rolling avg) | `42000` |
| `total_liquid_usd` | number | Sum of all LiquidityBucket balances | `487000` |
| `runway_months` | number | `total_liquid_usd / monthly_burn_usd` | `11.6` |
| `alert_triggered` | bool | True if runway < 3 months or alert rule fires | `false` |
| `alert_type` | string or null | `cash-crunch`, `forced-sale-risk`, `refi-cliff`, null | `null` |
| `notes` | string | Human commentary | — |

---

## 2. Calculation Specs

### 2a. Rental Property: NOI → FCF

```
Gross Rental Income (annual)         $198,000
- Vacancy allowance (4.2%)           -  $8,316
= Effective Gross Income              $189,684
- Operating expenses (insurance,
  property tax, maintenance, mgmt)   - $24,384
= Net Operating Income (NOI)          $165,300

NOI                                   $165,300
- Annual Debt Service (P&I × 12)    - $153,600   ($12,800/mo × 12)
= Pre-Capex Cash Flow                  $11,700

Pre-Capex Cash Flow                    $11,700
- Capex Reserve (5% of gross rent)   -  $9,900
= Free Cash Flow (FCF)                  $1,800

DSCR = NOI / Annual Debt Service
     = $165,300 / $153,600
     = 1.07   ← ALERT: Below 1.25 threshold; flag for review

Debt Yield = NOI / Loan Balance
           = $165,300 / $1,850,000
           = 8.9%
```

**DSCR guardrail**: If DSCR < 1.25, flag in `DebtService.dscr` and trigger `alert_type = forced-sale-risk` in next RunwaySnapshot.

### 2b. Dividends: Gross → Net Received

```
Gross Dividend (per quarter)          $3,750    (e.g., 1,500 shares × $2.50/share)
- Federal withholding (0% qualified)       $0    (assume qualified dividend)
- State withholding (California 13.3%)   -$499
= Net Cash Received                    $3,251

Annual net dividend income:           $13,004
Monthly contribution to cashflow:      $1,084
```

Filed as `CashFlowItem`:
- `category = dividend`
- `amount_usd = 3251` (net)
- `notes = "Q2 2026 dividend: 1500 shares @ $2.50/sh, CA state withholding applied"`

### 2c. Operating Business: EBITDA → FCF

```
EBITDA (trailing 12 months)           $840,000

+ Working Capital Change (decrease)   + $15,000   (AR collected faster)
= Cash EBITDA                          $855,000

- Capex (maintenance + growth)        -$120,000
= Pre-Debt Cash Flow                   $735,000

- Annual Debt Service                 -$480,000   ($40,000/mo × 12)
= Free Cash Flow (FCF)                 $255,000

FCF Yield = FCF / Invested Capital
          = $255,000 / $2,000,000
          = 12.75%

DSCR = (EBITDA - Capex) / Debt Service
     = ($840,000 - $120,000) / $480,000
     = 1.50   ← Healthy; no alert
```

### 2d. Debt Yield and DSCR Reference

```
Debt Yield = NOI / Loan Balance
           Threshold: > 8% = healthy; 6–8% = watch; < 6% = alert

DSCR = NOI (or EBITDA - Capex) / Annual Debt Service
     Threshold: > 1.35 = healthy; 1.20–1.35 = watch; < 1.20 = alert
```

---

## 3. Output Files

### cashflow.json

Rolling cashflow record. Contains all `CashFlowSource`, `CashFlowItem`, `DebtService`, and `LiquidityBucket` arrays. Validated against `schemas/cashflow.schema.json`. Updated monthly by `scripts/cashflow_snapshot.py`.

Location: `cashflow/cashflow.json`

### cashflow_summary_{YYYY-MM}.md Template

Location: `cashflow/summaries/cashflow_summary_{YYYY-MM}.md`

```markdown
# Cashflow Summary — {Month} {Year}

**Generated**: {YYYY-MM-DD}
**Runway snapshot**: {runway_months} months as of {as_of_date}
**Alert status**: {NONE | alert_type}

---

## Monthly Cashflow Table

| Source | Category | Amount (USD) | Notes |
|---|---|---|---|
| Downtown Loft — Unit 1 | rental-income | +$4,500 | Full month |
| Downtown Loft — Unit 2 | rental-income | +$4,000 | Full month |
| Downtown Loft — Unit 3 | rental-income | +$4,000 | Full month |
| VTSAX Dividends | dividend | +$1,084 | Q2 quarterly, net of state tax |
| Acme Corp Distribution | distribution | +$6,250 | Q2 return of capital |
| First National — Loft Mortgage | debt-service | -$12,800 | P&I |
| Operating Expenses — FO | operating-expense | -$8,500 | Payroll, software, legal |
| **Net Monthly Cashflow** | | **-$1,466** | Negative: deployment month |

---

## Liquidity Buckets

| Bucket | Balance | Institution |
|---|---|---|
| Operating | $285,000 | Chase Business Checking |
| Reserve | $150,000 | Marcus HYSA (4.85% APY) |
| Deployment | $52,000 | Fidelity Money Market |
| **Total Liquid** | **$487,000** | |

**Monthly Burn (6-mo avg)**: $42,000
**Runway**: **11.6 months**

---

## Debt Service Summary

| Property/Asset | Lender | Balance | Rate | Monthly P&I | DSCR | Maturity |
|---|---|---|---|---|---|---|
| Downtown Loft Portfolio | First National | $1,850,000 | 6.25% fixed | $12,800 | 1.07 | 2032-07 |

**ALERT**: Downtown Loft DSCR = 1.07 — below 1.25 threshold. Monitor for rent increase opportunity or capex deferral.

---

## Alert Status

{NONE — all metrics within normal range.}
{OR: ALERT — [cash-crunch | forced-sale-risk | refi-cliff] — [description]}
```

---

## 4. Alert Rules

| Alert Type | Trigger Condition | Action |
|---|---|---|
| `cash-crunch` | `runway_months < 3` | Immediate Slack alert to #fo-cfo; human reviews within 24h |
| `cash-crunch-warning` | `runway_months < 6` | Slack alert to #fo-cfo; include in next weekly review |
| `forced-sale-risk` | Any `DebtService.dscr < 1.10` | Slack alert; flag in cashflow summary; review debt terms |
| `refi-cliff` | Any loan `maturity_date` within 12 months | Quarterly reminder beginning 12 months out; monthly at 6 months |
| `low-dscr-watch` | Any `DebtService.dscr` between 1.10 and 1.25 | Note in summary; no immediate alert |
| `negative-fcf` | Any rental with FCF < $0 | Flag in summary; review at next cashflow meeting |

Alert rules are evaluated each time `scripts/cashflow_snapshot.py` runs (monthly minimum, weekly optional).

---

## 5. Barbell Layer 1 Connection

The cashflow module IS the Layer 1 implementation:

```
Layer 1: Liquidity Runway
├── Operating bucket: 1–3 months burn ($42K × 3 = $126K minimum)
├── Reserve bucket: 3–6 months additional ($42K × 6 = $252K minimum)
└── Deployment bucket: discretionary, for next investment

Healthy configuration (per Tony Robbins / Money: Master the Game):
- Operating: 3 months minimum at all times
- Reserve: 3–6 additional months (total 6–9 months secure)
- Deployment: only funded once Operating + Reserve targets are met

Alert: if total liquid < 6 months burn ($252K), no new power-law-bet investments
       until liquidity is restored
```

Scripts:
- `scripts/cashflow_snapshot.py` — runs monthly, writes `runway_{YYYY-MM-DD}.json`
- `scripts/cashflow_snapshot.py --mode weekly` — lighter update, no full recalculation
