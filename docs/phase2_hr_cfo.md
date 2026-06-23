# Phase 2: HR + CFO Expansion

> **Context**: Phase 1 establishes the investment operations core (deal evaluation, deal updates, valuations, cashflow, public marks). Phase 2 adds the operational backbone that a real family office or operating entity needs: payroll, benefits, equity compensation, budgeting, tax coordination, entity management, insurance, and vendor management.
>
> Every Phase 2 module follows the same principles as Phase 1: JSON records, git provenance, schema validation, human-in-the-loop on approvals.

---

## Priority Order

| Priority | Module | Unblocks |
|---|---|---|
| 1 | Payroll & Contractors | Operating entity compliance; cash outflows in cashflow module |
| 2 | Operating Budget | Full CFO picture; without budget, runway is approximate |
| 3 | Entity Management | Signing authority, corporate actions — needed before tax prep |
| 4 | Tax Prep Coordination | Annual obligation; needs entity + cashflow data from P1 |
| 5 | Vendor / AP Management | Controls around payments; needed as entity grows |
| 6 | Insurance Register | Risk management; needed before adding significant assets |
| 7 | Benefits & Compliance | Needed once W-2 employees are on payroll |
| 8 | Equity Compensation Tracking | Needed once employees receive equity |

---

## Module 1: Payroll & Contractors

### Purpose
Track all compensation payments — W-2 employees, 1099 contractors, officer distributions. Feed directly into the cashflow module as `operating-expense` line items.

### Workflow Steps

1. **Roster file**: Maintain `hr/roster.json` — one record per person with role, entity, pay type, rate, start date.
2. **Pay cycle**: Each payroll run generates `hr/payroll/payroll_{YYYY-MM-DD}.json` with itemized payments.
3. **Contractor invoices**: Received via email → ingested using `ingest_deal_update.py` variant → filed in `hr/contractors/invoices/`.
4. **Integration with cashflow**: Each payroll run creates `CashFlowItem` entries (category=`operating-expense`) in `cashflow/cashflow.json`.
5. **Year-end**: Generate W-2 summary and 1099 summary for each payee. Pointers to payroll processor docs in S3.

### Key Artifacts

| File | Location | Description |
|---|---|---|
| `roster.json` | `hr/roster.json` | Active + historical employee/contractor list |
| `payroll_{YYYY-MM-DD}.json` | `hr/payroll/` | Per-run payroll record with amounts, deductions, net |
| `contractor_invoice_{hash8}.json` | `hr/contractors/invoices/` | Filed contractor invoices |
| `payroll_summary_{YYYY}.md` | `hr/payroll/summaries/` | Annual payroll summary for tax prep |

### Automation Potential
- **High**: Payroll data import from ADP/Gusto via API → auto-generate cashflow items.
- **Human approval required**: Any new employee add, rate change, or termination requires IC approval before roster update.

### Minimum Controls
- Dual approval for any payment > $10,000 (two authorized signers).
- All rate changes require written approval filed in `hr/approvals/`.
- Quarterly reconciliation: payroll records vs. bank statements.

---

## Module 2: Benefits & Compliance

### Purpose
Track employee benefits (health, dental, 401k), compliance filings (EEO, OSHA, state registrations), and open enrollment cycles.

### Workflow Steps

1. Benefits elections recorded in `hr/benefits/elections_{YYYY}.json` per employee.
2. Carrier invoices ingested monthly → cashflow entries.
3. Compliance calendar: `hr/compliance/calendar.json` tracks filing deadlines (state registrations, form 5500, etc.).
4. Open enrollment: Annual cycle in September–November. Updates elections file. Triggers payroll deduction changes.

### Key Artifacts

| File | Location | Description |
|---|---|---|
| `elections_{YYYY}.json` | `hr/benefits/` | Per-employee benefit elections |
| `compliance_calendar.json` | `hr/compliance/` | Deadline tracker with alert dates |
| `carrier_invoice_{hash8}.json` | `hr/benefits/invoices/` | Health/dental/vision carrier bills |

### Automation Potential
- **Medium**: Carrier invoice ingestion automated. Open enrollment still requires human decision.
- **Human approval required**: All benefits changes; compliance filings (human signs).

### Minimum Controls
- Benefits invoices reconciled quarterly against elections.
- Compliance deadlines trigger Slack alerts 30, 14, and 7 days before due date.

---

## Module 3: Equity Compensation Tracking

### Purpose
Track stock options, warrants, RSUs, or profit interest units issued to employees or advisors. Critical for 409A compliance, tax planning, and cap table accuracy.

### Workflow Steps

1. Grant recorded in `hr/equity/grants.json` at issuance — includes grant date, type, shares, strike price, vesting schedule, cliff.
2. Vesting events tracked monthly via `scripts/equity_vesting_update.py` — adds `vesting_events` to each grant record.
3. Exercise events recorded when employee exercises options — triggers tax event notification.
4. 409A valuation updates (from `valuations/` module) feed into fair market value used for option pricing.
5. Cap table pointer maintained in `deals/{slug}/deal_doc_pointers.json`.

### Key Artifacts

| File | Location | Description |
|---|---|---|
| `grants.json` | `hr/equity/` | All equity grants with vesting schedules |
| `vesting_snapshot_{YYYY-MM}.json` | `hr/equity/vesting/` | Monthly vested/unvested summary |
| `exercise_events.json` | `hr/equity/` | Record of all option exercises |

### Automation Potential
- **High**: Vesting schedule calculations are deterministic — fully automatable.
- **Human approval required**: New grants require IC/board approval; exercise events require legal review.

### Minimum Controls
- Every grant backed by a board/IC approval document (pointer to S3).
- Annual 409A valuation required if issuing options (links to `valuations/` pipeline).
- No grants without `strike_price_usd` and `grant_date` fields.

---

## Module 4: Operating Budget

### Purpose
Establish and track annual operating budget for the family office entity. Provides the `monthly_burn_usd` denominator for runway calculations. Without this, cashflow module uses trailing actuals — budget adds forward-looking discipline.

### Workflow Steps

1. Annual budget set each December for following year: `cashflow/budget/budget_{YYYY}.json`.
2. Budget contains monthly line items by category (payroll, professional services, software, travel, insurance, misc).
3. Monthly: actuals from `cashflow/cashflow.json` compared to budget — variance report generated.
4. Variance > 15% in any category triggers Slack alert and requires explanation in notes.

### Calculation Spec: Budget vs. Actuals

```
Budget (monthly):
  Payroll:               $18,000
  Professional services:  $5,000   (legal, accounting)
  Software/tools:         $1,200
  Insurance:              $1,500
  Travel:                 $2,000
  Misc:                   $1,500
  Total Budget:          $29,200

Actuals (June 2026):
  Payroll:               $18,000   (0% variance — on budget)
  Professional services:  $8,500   (+70% — legal fees for deal close)
  Software/tools:         $1,350   (+12.5% — new tool)
  Insurance:              $1,500   (0%)
  Travel:                 $3,200   (+60% — LP meeting travel)
  Misc:                   $900     (-40%)
  Total Actuals:         $33,450   (+14.6% over budget — below 15% threshold)
```

### Key Artifacts

| File | Location | Description |
|---|---|---|
| `budget_{YYYY}.json` | `cashflow/budget/` | Annual budget by month and category |
| `variance_report_{YYYY-MM}.json` | `cashflow/budget/variance/` | Monthly actuals vs. budget |
| `variance_summary_{YYYY-MM}.md` | `cashflow/summaries/` | Human-readable variance summary |

### Automation Potential
- **High**: Variance calculation is deterministic once actuals are in cashflow.json.
- **Human approval required**: Budget setting (December), any budget amendment > 10%.

---

## Module 5: Tax Prep Coordination

### Purpose
Coordinate annual tax preparation across all entities and family members. Collect K-1s, 1099s, real property schedules, and communicate with CPA. Generate the data package the CPA needs.

### Workflow Steps

1. **December**: Run `scripts/tax_prep_init.py --year {YYYY}` — generates `tax/{YYYY}/checklist.json` from all active deals and entities.
2. **January–March**: As documents arrive (K-1s, 1099s, brokerage statements), ingest and file in `tax/{YYYY}/documents/` as pointer files (S3).
3. **February**: Generate cashflow summary for CPA: `scripts/generate_tax_cashflow_report.py --year {YYYY}`.
4. **March**: CPA review package assembled — all pointers, cashflow report, entity list, equity grants. Filed in `tax/{YYYY}/cpa_package.json`.
5. **April**: Returns filed. Pointer to signed returns stored in S3. `tax/{YYYY}/filed.json` updated.

### Key Artifacts

| File | Location | Description |
|---|---|---|
| `checklist.json` | `tax/{YYYY}/` | Auto-generated list of expected tax documents |
| `cpa_package.json` | `tax/{YYYY}/` | Assembled data package for CPA |
| `filed.json` | `tax/{YYYY}/` | Record of filed returns with pointers |
| `{document}.pointer.json` | `tax/{YYYY}/documents/` | Pointers to K-1s, 1099s, statements in S3 |

### Automation Potential
- **Medium**: Checklist generation and document ingestion automated. CPA communication and review is human.
- **Human approval required**: All returns require human sign-off before filing.

### Minimum Controls
- No return filed without dual approval (owner + CPA signature).
- All original documents stored in S3 minimum 7 years.
- Deadline alerts: estimated taxes (April 15, June 15, Sep 15, Jan 15), returns (April 15 / Oct 15 extension).

---

## Module 6: Entity Management

### Purpose
Track all legal entities (LLCs, LPs, trusts, corporations) — registered agents, state registrations, officers, annual filings, and signing authority.

### Workflow Steps

1. `entities/registry.json` — master list of all entities with type, state, EIN, registered agent, officers.
2. Annual report due dates tracked in `entities/compliance_calendar.json` — alerts 60, 30, 14 days out.
3. Officer changes: `entities/officer_changes/` — immutable record of any officer add/remove.
4. Signing authority matrix: `entities/signing_authority.json` — who can sign what for each entity.
5. Dissolution events: filed as immutable record with effective date.

### Key Artifacts

| File | Location | Description |
|---|---|---|
| `registry.json` | `entities/` | All entities |
| `compliance_calendar.json` | `entities/` | Annual report and renewal deadlines |
| `signing_authority.json` | `entities/` | Authorization matrix |
| `officer_changes/` | `entities/` | Immutable officer change records |

### Automation Potential
- **Low**: Most entity actions require human judgment and legal counsel.
- **Human approval required**: All officer changes; state filings; entity formation or dissolution.

### Minimum Controls
- Every entity has an EIN and registered agent on file.
- Annual reports calendared and completed before deadline.
- Any signing authority change requires written IC approval.

---

## Module 7: Insurance Register

### Purpose
Track all insurance policies — property & casualty, liability, D&O, life, umbrella, errors & omissions. Ensure no coverage gaps.

### Workflow Steps

1. `insurance/policies.json` — one record per policy with insurer, coverage type, limits, premium, effective dates.
2. Renewal alerts: 90, 60, 30 days before expiration — Slack to #fo-insurance.
3. Claims: filed as immutable records in `insurance/claims/`.
4. Annual review: compare coverage to current portfolio value. Flag any properties or entities not covered.

### Key Artifacts

| File | Location | Description |
|---|---|---|
| `policies.json` | `insurance/` | All active and expired policies |
| `claims/` | `insurance/` | Filed claims (pointer files to claim documents in S3) |
| `coverage_gap_report_{YYYY}.md` | `insurance/` | Annual coverage analysis |

### Automation Potential
- **Medium**: Renewal alerts automated. Coverage gap analysis requires human judgment.
- **Human approval required**: All new policy purchases; claims filing.

### Minimum Controls
- Every real estate asset has property insurance on file.
- Umbrella policy covers all entities.
- No policy lapse — renewal process begins 90 days before expiration.

---

## Module 8: Vendor / AP Management

### Purpose
Track all vendors and contractors, approve and record payments, maintain vendor contracts. Prevent unauthorized payments and maintain audit trail.

### Workflow Steps

1. **Vendor onboarding**: New vendor added to `vendors/registry.json` — name, EIN/SSN, payment method, W-9 pointer.
2. **Invoice receipt**: Vendor invoices ingested (email/PDF) → filed in `vendors/invoices/{vendor-slug}/`.
3. **Approval workflow**: Invoices > $5,000 require dual approval. Documented in invoice record.
4. **Payment**: Payment recorded in `vendors/payments/{YYYY-MM-DD}-{vendor-slug}-{hash8}.json`. Feeds cashflow.
5. **1099 prep**: At year-end, `scripts/generate_1099_summary.py` tallies all payments per vendor for CPA.

### Calculation Spec: AP Controls

```
Payment approval thresholds:
  $0    – $1,000:  Single approver (ops manager)
  $1,001 – $5,000: Single approver (Grayson)
  $5,001 – $25,000: Dual approval (Grayson + one trustee)
  $25,001+:        Dual approval + IC documentation required

1099 threshold: Any vendor paid > $600/year receives a 1099-NEC
```

### Key Artifacts

| File | Location | Description |
|---|---|---|
| `registry.json` | `vendors/` | All vendors with W-9 pointers |
| `invoices/{vendor-slug}/` | `vendors/` | Filed invoices per vendor |
| `payments/{date}-{slug}-{hash}.json` | `vendors/` | Payment records feeding cashflow |

### Automation Potential
- **Medium**: Invoice ingestion automated. Approval workflow requires human action.
- **Human approval required**: All payments per thresholds above.

---

## Minimum Viable Controls Checklist

### Who Can Approve What

| Action | Approver(s) |
|---|---|
| New deal investment | IC (investment committee) |
| Deal update filing (automated) | Pipeline (no human unless flagged) |
| Valuation > $500K | Human approval required (GP/IC) |
| New employee hire | IC |
| Payroll change | Operations manager + IC |
| Vendor payment > $5,000 | Dual approval |
| Entity formation/dissolution | IC + legal counsel |
| Tax return filing | Owner + CPA |
| New insurance policy | IC |
| Equity grant | IC + board |

### Dual-Control Thresholds

| Transaction type | Single approver limit | Dual approval required above |
|---|---|---|
| Cash disbursement | $5,000 | $5,001 |
| Wire transfer | $10,000 | $10,001 |
| New vendor onboarding | Always single | N/A |
| Investment commitment | $25,000 | $25,001 |

### Audit Log Requirements

Every approval action creates an immutable record:
```json
{
  "action": "approve_payment",
  "amount_usd": 12500,
  "vendor": "acme-legal-llp",
  "approved_by": ["grayson.culliford@hivefs.com", "trustee@smithfamily.com"],
  "approved_at": "2026-07-01T14:22:00Z",
  "notes": "Q2 legal retainer per engagement letter dated 2026-01-01"
}
```

---

## Integration Points with Phase 1

| Phase 2 Module | Phase 1 Integration |
|---|---|
| Payroll & Contractors | Payroll → `CashFlowItem` (operating-expense) in cashflow module |
| Operating Budget | Budget `monthly_burn_usd` overrides trailing average in `RunwaySnapshot` |
| Tax Prep | Pulls from `cashflow/cashflow.json`, `deals/`, `valuations/`, `hr/payroll/` |
| Entity Management | Entities referenced in `deal.json` `entity` field — must be consistent |
| Vendor / AP | Vendor payments → `CashFlowItem` (operating-expense) |
| Insurance | Insurance premiums → `CashFlowItem` (operating-expense); coverage tracked against `deals/` real estate assets |
| Equity Compensation | 409A valuations use `valuations/` pipeline; cap table linked to `deals/{slug}/deal_doc_pointers` |
