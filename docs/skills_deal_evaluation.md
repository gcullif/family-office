# Skill: DealEvaluation (Pre-Investment)

> **Purpose**: Decide whether to invest. This workflow runs BEFORE any capital is deployed. Its output is either a `deal.json` filed in `deals/` (approved) or a record archived in `working/deal-eval/` (rejected/passed).

---

## 1. Overview

| Attribute | Value |
|---|---|
| **Trigger** | New deal sourced: cold intro, LP referral, inbound pitch, proactive outreach |
| **Owner** | Investment decision-maker (Grayson or designated IC member) |
| **Cadence** | Episodic — runs whenever a new deal arrives |
| **Duration** | Fast eval: 1–4 hours. Full eval: 1–4 weeks |
| **Terminal artifacts** | `deals/{slug}/deal.json` (approved) OR `working/deal-eval/{slug}/` archived (rejected) |
| **Risks** | Investing without sufficient diligence; missing red flags; FOMO-driven shortcuts |

---

## 2. Barbell Layer Pre-Check

Before beginning diligence, classify the deal into a barbell layer. This determines which checklist items are mandatory vs. optional.

| Layer | Criteria | Minimum eval required |
|---|---|---|
| `liquidity-runway` | Money market, T-Bills, cash equivalents | Near-zero eval; rate check only |
| `defensive-compounding` | Low-cost index funds, rental RE with FCF, investment-grade bonds | Lightweight: fee check, cashflow confirm |
| `power-law-bet` | VC, PE, operating business, early-stage real estate | Full evaluation mandatory |

---

## 3. Step-by-Step Checklist

### Phase 1: Triage (30 minutes — all deals)

- [ ] **1.1** Record deal in `working/deal-eval/{slug}/notes.md` with: date received, source/referrer, one-sentence description.
- [ ] **1.2** Classify barbell layer. If `liquidity-runway`: skip to Phase 5 (file immediately). If `defensive-compounding`: skip to Phase 3.
- [ ] **1.3** Check for conflicts: does family office or any family member have a conflict of interest?
- [ ] **1.4** Confirm deal is within investment policy statement (IPS) parameters: geography, sector, check size.
- [ ] **1.5** Assign deal slug: `{company-name}-{round-or-type}` in kebab-case. Example: `acme-corp-series-b`.

**Required inputs**: Deal name, source, check size requested, asset type.

### Phase 2: Desk Research (2–4 hours — power-law-bet deals)

- [ ] **2.1** Review pitch deck or PPM. Summarize in `notes.md`: market size claim, business model, revenue/traction, team background, ask.
- [ ] **2.2** Crunchbase / PitchBook: prior rounds, investors, comparable exits.
- [ ] **2.3** LinkedIn: confirm founder backgrounds. Red flags: unexplained gaps, conflicting claims.
- [ ] **2.4** News search: any litigation, regulatory issues, negative press.
- [ ] **2.5** Reference check: does the referrer have financial interest in us investing? Note in `notes.md`.
- [ ] **2.6** Fill in `deal.json` stub (status=`prospect`) in `working/deal-eval/{slug}/deal.json`.

**Required inputs**: Pitch deck or PPM, founder LinkedIn, Crunchbase profile.

### Phase 3: Thesis Development (2–8 hours — power-law-bet and defensive-compounding)

- [ ] **3.1** Write thesis paragraph in plain language (minimum 3 sentences). Will go in `deal.json` `thesis_summary` field.
- [ ] **3.2** Identify 3–5 key risks. Write in `risk_matrix.md`.
- [ ] **3.3** For real estate: confirm positive FCF at current debt terms. Run numbers: NOI − debt service − capex reserve = FCF. FCF must be > $0 to proceed.
- [ ] **3.4** For VC/PE: estimate realistic return scenarios (base case, bull case, bear case). Document assumptions.
- [ ] **3.5** Identify exit path: IPO, acquisition, secondary, hold forever?

**Required inputs**: Financial statements or model, cap table, debt terms (real estate).

### Phase 4: IC Memo (4–16 hours — power-law-bet deals requiring full IC approval)

- [ ] **4.1** Draft `working/deal-eval/{slug}/ic_memo.md` using the template in Section 6 below.
- [ ] **4.2** Complete all mandatory sections (Executive Summary, Barbell Layer, Thesis, Market, Team, Financials, Risk, Decision).
- [ ] **4.3** IC review: present memo to investment committee (even if committee = 1 person). Document decision in memo.
- [ ] **4.4** If approved: set `deal.json` status = `active`, move to `deals/{slug}/`, git tag `deal-eval/{slug}/approved-v1`.
- [ ] **4.5** If rejected/passed: move `working/deal-eval/{slug}/` to `working/deal-eval/_archived/`, add `decision: rejected` and `decision_reason` to `notes.md`.

**Required inputs**: Completed ic_memo.md, IC participants, final check size.

### Phase 5: Filing (15 minutes — all approved deals)

- [ ] **5.1** Validate `deal.json` against `schemas/deal.schema.json` (`python -m jsonschema -i deal.json schemas/deal.schema.json`).
- [ ] **5.2** Create `deals/{slug}/` directory. Copy `deal.json` and `ic_memo.md` into it.
- [ ] **5.3** Upload signed subscription agreement / term sheet to S3. Add pointer to `deal_doc_pointers` in `deal.json`.
- [ ] **5.4** Append to CHANGELOG.md: `DEAL FILED: deals/{slug}/deal.json (status=active, $X invested, barbell={layer})`.
- [ ] **5.5** Git commit and push. Tag: `deal-eval/{slug}/approved-v1`.
- [ ] **5.6** Brief DealUpdatesOps setup: add deal to any relevant email filter rules; confirm ingestion pipeline can match by domain or ticker.

---

## 4. Example 1: Fast $100K Investment (Lightweight Eval)

**Scenario**: Existing LP calls and says "We have a small $100K allocation left in our current fund, are you in?" Company is one you've tracked for 2 years. Deadline: 48 hours.

**What gets skipped**:
- Phase 2 full desk research (you know the company)
- Phase 4 full IC memo (time constraint, known deal)
- Reference check (existing relationship)

**Minimum required**:
- [ ] Triage notes in `working/deal-eval/known-co-fund-iii/notes.md`
- [ ] Confirm check size fits IPS ($100K within limit)
- [ ] 1-paragraph thesis + 3 risk factors in notes
- [ ] `deal.json` stub validated and filed
- [ ] Signed docs pointer uploaded to S3
- [ ] CHANGELOG entry

**Lightweight IC memo (abbreviated)**:
```markdown
# IC Note: Known Co — Fund III Participation
Date: 2026-06-23
Author: Grayson Culliford
Decision: INVEST $100,000

## Why
We have tracked Known Co for 2 years. Strong growth, founder execution. This is a follow-on
into a fund that already owns them. Power-law bet; asymmetric upside.

## Risks
1. Illiquid 10-year fund life
2. Concentration in one manager
3. Fund III may face tougher exit environment vs. prior vintages

## Terms
$100K commitment. 2% mgmt fee, 20% carry. Existing LP relationship.
```

---

## 5. Example 2: Full Deal Evaluation with IC Memo

**Scenario**: Inbound pitch from `Meridian Logistics Tech` — Series A, $250K ask, logistics SaaS for last-mile delivery. No prior relationship. Full diligence required.

**Timeline**: 2-week process.

**All artifacts produced**:

```
working/deal-eval/meridian-logistics-tech-series-a/
├── notes.md               # Daily research log, key findings
├── deal.json              # Status=prospect, updated to active on approval
├── ic_memo.md             # Full IC memo (see template below)
├── risk_matrix.md         # 8-item risk register
└── model_assumptions.md   # Financial scenario analysis
```

**Checklist completion**: All Phase 1–5 items completed.

**Git tags**:
- `deal-eval/meridian-logistics-tech-series-a/research-complete` (end of week 1)
- `deal-eval/meridian-logistics-tech-series-a/approved-v1` (end of week 2, if approved)

---

## 6. IC Memo Template

File path: `working/deal-eval/{deal-slug}/ic_memo.md`

On approval, this file moves to: `deals/{deal-slug}/ic_memo.md`

```markdown
# IC Memo: {Deal Name}

**Date**: YYYY-MM-DD
**Author**: {name}
**Status**: DRAFT | FINAL
**Decision**: PENDING | INVEST ${amount} | PASS

---

## Executive Summary

One paragraph: what is this company/asset, what are we being asked to do, what is our
recommended decision, and what is the single most important reason for that decision.

## Barbell Layer

**Layer**: power-law-bet | defensive-compounding | liquidity-runway

**Rationale**: Why does this deal belong in this layer? What is our portfolio allocation
to this layer today, and how does this deal affect concentration?

## Thesis

Plain-language explanation (3–5 sentences). Why do we believe this investment will
generate the return we expect? What is the key insight that others may be missing?

## Market

- **TAM**: ${amount} — source: {source}
- **Key competitors**: {list}
- **Competitive moat**: {description}
- **Why now**: {timing rationale}

## Team

| Name | Role | Background |
|---|---|---|
| {name} | {title} | {1-sentence background, prior outcomes} |

**Key-person risk**: {assessment}

## Financials

| Metric | Current | Year 1 Proj | Year 3 Proj |
|---|---|---|---|
| Revenue | ${} | ${} | ${} |
| EBITDA | ${} | ${} | ${} |
| Cash balance | ${} | — | — |
| Runway | {} months | — | — |

**Our investment**: ${amount} for {ownership_pct}% at ${pre_money} pre-money.

**Return scenarios**:
| Scenario | Exit value | Our proceeds | MOIC |
|---|---|---|---|
| Bear | ${} | ${} | {}x |
| Base | ${} | ${} | {}x |
| Bull | ${} | ${} | {}x |

## Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| 1 | {risk} | High/Med/Low | High/Med/Low | {mitigation} |

## Decision

**Recommendation**: INVEST / PASS / DEFER

**Check size**: ${amount}

**Conditions** (if any): {list any conditions precedent to wiring funds}

**IC participants**: {names}
**Decision date**: YYYY-MM-DD
```

---

## 7. Output Files Summary

| File | Location | Purpose |
|---|---|---|
| `notes.md` | `working/deal-eval/{slug}/` | Running research log |
| `deal.json` | `working/deal-eval/{slug}/` → `deals/{slug}/` | Canonical deal record |
| `ic_memo.md` | `working/deal-eval/{slug}/` → `deals/{slug}/` | Investment committee memo |
| `risk_matrix.md` | `working/deal-eval/{slug}/` | Risk register |
| `model_assumptions.md` | `working/deal-eval/{slug}/` | Financial scenario model |

---

## 8. Success Metrics

| Metric | Target |
|---|---|
| Time from triage to decision (power-law-bet) | ≤ 21 days |
| Time from triage to decision (defensive-compounding) | ≤ 3 days |
| Schema validation pass rate | 100% before filing |
| IC memo completion rate (power-law-bet) | 100% |
| CHANGELOG entry on every filed deal | 100% |
| Deals with provenance on deal.json | 100% |
| Rejected deals archived (not deleted) | 100% |
