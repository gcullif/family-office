# Skill: DealUpdatesOps (Post-Investment)

> **Purpose**: Monitor and process everything that happens AFTER capital is deployed. Keeps deal records current, triggers valuation refreshes, and surfaces flags requiring human attention — without requiring manual intervention on routine updates.

---

## 1. Overview

| Attribute | Value |
|---|---|
| **Trigger** | Any incoming update on an active deal: email, PDF, article, scheduled check, manual note |
| **Owner** | Automation pipeline (scripts/ingest_deal_update.py); human intervention only on NEEDS_REVIEW flags |
| **Cadence** | Continuous (email/PDF ingestion); daily (news scan); quarterly (scheduled valuation review) |
| **Terminal artifacts** | `deal-updates/YYYY/MM/DD/{slug}--{type}--{source}--{hash8}.json` + optional valuation record |
| **Risks** | Stale valuations; missed material events; filing errors on ambiguous matches |

---

## 2. Triggers and Cadence

| Trigger type | Frequency | Automation level |
|---|---|---|
| Email forwarded to ingest inbox | Real-time (15-min polling) | Fully automated |
| PDF attachment from email | Real-time (attached to email trigger) | Automated + S3 upload |
| Manual note by ops team | Ad-hoc | Human-initiated, then automated |
| Excel file drop | Ad-hoc | Automated on file drop to watched folder |
| Scheduled web news scan | Daily at 06:00 ET | Automated |
| Quarterly valuation review | Every quarter (Jan, Apr, Jul, Oct) | Automated trigger, human approval of result |

---

## 3. Step-by-Step Ingestion + Filing Checklist

### Step 1: Receive

- [ ] Raw input arrives (email polling, file drop, manual CLI command).
- [ ] `scripts/ingest_deal_update.py` begins processing.
- [ ] Compute SHA-256 of raw bytes → check against `deal-updates/` index for duplicate. If duplicate: log and stop (`REJECTED`).
- [ ] Set `processing_state = RECEIVED`.

### Step 2: Parse

- [ ] Extract structured data from raw input using LLM extraction or rule-based parser:
  - Email: sender, subject, body, attachment names, dates mentioned.
  - PDF: run `pdfplumber` → send text + tables to extraction prompt.
  - Excel: read sheets with `openpyxl` → extract numeric fields + labels.
  - Web article: fetch URL → strip HTML → extract headline, company name, key facts.
  - Manual note: use CLI-provided structured fields directly.
- [ ] Infer `update_type` from content (if not provided explicitly).
- [ ] Set `processing_state = PARSED`.

### Step 3: Match

- [ ] Run `scripts/match_deal.py` with extracted entity name, sender domain, any tickers/IDs.
- [ ] Tier 1 (deterministic): check ticker, domain, explicit deal ID. Score = 1.0.
- [ ] Tier 2 (fuzzy): name similarity, contact match, keyword overlap. Score = weighted sum.
- [ ] If score ≥ 0.85: proceed to file. Set `confidence_score = score`.
- [ ] If 0.70 ≤ score < 0.85: proceed to file but set `needs_review = true`. Queue Slack alert.
- [ ] If score < 0.70: write to `needs-review/YYYY/MM/DD/{hash8}.json`. Set state = `NEEDS_REVIEW`. Halt.
- [ ] Set `processing_state = MATCHED` (or `NEEDS_REVIEW`).

### Step 4: Validate + File

- [ ] Build complete `DealUpdate` JSON object.
- [ ] Validate against `schemas/deal_update.schema.json` using `jsonschema`. Fail → `REJECTED`.
- [ ] Upload raw file to S3 (or local `raw-updates/` mirror). Write `raw_content_pointer`.
- [ ] Write JSON record to `deal-updates/YYYY/MM/DD/{slug}--{type}--{source}--{hash8}.json`.
- [ ] Set `processing_state = FILED`.

### Step 5: Downstream Effects

- [ ] If `valuation_refresh_triggered = true`: invoke `scripts/run_valuation.py --deal-slug {slug} --trigger-ref {update_path}`.
  - Valuation auto-triggers on: `earnings`, `financing-round`, `valuation-mark`, `exit`.
  - Valuation does NOT auto-trigger on: `company-news`, `macro-event`, `management-change`.
- [ ] If valuation completed: update `deal.json` field `latest_valuation_ref`. Append valuation to CHANGELOG.
- [ ] If `update_type = exit` and `extracted_data.exit_type` is set: update `deal.json` status to `realized` (requires human confirmation).
- [ ] Update `deal.json` field `last_updated_at` with current UTC timestamp.
- [ ] Append to CHANGELOG.md.
- [ ] Git commit all new files with message: `ops: file deal update {slug} {update_type} {hash8}`.
- [ ] Set `processing_state = PROCESSED`.

### Step 6: Alerts

- [ ] If `needs_review = true`: send Slack message to `#deals-ops` with file path and top match candidate.
- [ ] If `update_type = exit`: send Slack alert to `#deals-exits`.
- [ ] If valuation delta > 25% (up or down): send Slack alert to `#deals-valuations`.
- [ ] If `update_type = management-change`: send Slack alert to `#deals-ops` (management changes can be material).

---

## 4. Output Files

| File | Location | Created by |
|---|---|---|
| Deal update record | `deal-updates/YYYY/MM/DD/{slug}--{type}--{source}--{hash8}.json` | Step 4 |
| Raw input (pointer) | `raw-updates/YYYY/MM/DD/{hash8}-{filename}` (S3) | Step 4 |
| Valuation record | `valuations/{slug}/valuation_{YYYY-MM-DD}_{hash8}.json` | Step 5 (if triggered) |
| NEEDS_REVIEW record | `needs-review/YYYY/MM/DD/{hash8}.json` | Step 3 (if NEEDS_REVIEW) |
| CHANGELOG entry | `CHANGELOG.md` | Step 5 |

---

## 5. Example 3: Quarterly Post-Investment Update Cycle

**Scenario**: It is October 1, 2026. The quarterly review cycle runs for all 12 active deals.

### What gets triggered automatically

```
1. scripts/run_quarterly_review.py
   ├── Scans deals/ for all deal.json with status=active
   ├── Checks last valuation date for each deal
   ├── If last valuation > 90 days ago → triggers run_valuation.py with trigger_type=scheduled-quarterly
   └── Writes valuation records for each deal
```

### What gets filed

For each of 12 active deals:
```
valuations/
├── acme-corp-series-b/valuation_2026-10-01_a1b2c3d4.json
├── horizon-vc-fund-ii/valuation_2026-10-01_b2c3d4e5.json
├── downtown-loft-portfolio/valuation_2026-10-01_c3d4e5f6.json
... (9 more)
```

### What requires human attention

- All valuations with `confidence = low` → `human_approved` must be set before quarterly report is generated.
- Any valuation with `value_delta_usd` > ±25%: Slack alert sent, human reviews before CHANGELOG is finalized.
- `run_quarterly_review.py` outputs a summary: `cashflow/summaries/cashflow_summary_2026-10.md` with all current marks.

### What gets committed

```
git commit -m "ops: quarterly valuation review 2026-Q4 — 12 deals updated"
git tag v1.3.0-2026-10-01
```

---

## 6. Connection to ValuationRefresh Pipeline

```
DealUpdate filed (update_type = earnings | financing-round | valuation-mark | exit)
        │
        ▼
scripts/run_valuation.py --deal-slug {slug} --trigger-ref {update_json_path}
        │
        ├── Reads deal.json: asset_type, ownership_pct, cost_basis
        ├── Reads trigger update: extracted_data fields (revenue, ARR, appraised_value, etc.)
        ├── Selects valuation method based on asset_type + available data
        ├── Computes value_low, value_mid, value_high
        ├── Checks confidence level
        │     └── If confidence = low OR value_mid > $500K: sets human_approved = false (manual review required)
        ├── Writes valuation record to valuations/{slug}/
        ├── Updates deal.json: latest_valuation_ref, current_value_usd (= value_mid)
        └── Returns valuation_ref path to calling script
```

---

## 7. Monitoring: Alerts vs. Routine

### Always alert (Slack to #deals-ops)

| Condition | Alert text |
|---|---|
| `needs_review = true` | "NEEDS REVIEW: {slug} — match confidence {score}. Path: {path}" |
| `update_type = exit` | "EXIT EVENT: {slug}. Please confirm deal status update." |
| Valuation delta > ±25% | "VALUATION CHANGE: {slug} changed from ${prior} to ${current} ({delta}%)" |
| `update_type = management-change` | "MGMT CHANGE: {slug}. Review for material impact." |
| Schema validation failure | "FILING ERROR: {slug} — schema validation failed. Check logs." |
| Duplicate detected | "DUPLICATE: {hash8} already filed at {original_path}. Skipped." |

### Routine (no alert, just CHANGELOG)

| Condition | Action |
|---|---|
| Earnings update, normal range | File, trigger valuation, CHANGELOG |
| Distribution notice | File, update cashflow record, CHANGELOG |
| Company news, sentiment=neutral | File, no valuation trigger, CHANGELOG |
| Scheduled quarterly valuation (confidence=high) | File, CHANGELOG |
| Public market price snapshot | File in public-marks/, CHANGELOG |

---

## 8. Success Metrics

| Metric | Target |
|---|---|
| Time from email received to FILED | < 15 minutes (automated) |
| NEEDS_REVIEW rate | < 10% of all updates |
| Schema validation pass rate | 100% |
| Valuation triggered within 24h of triggering update | 100% |
| Human approval completed within 48h of low-confidence valuation | 100% |
| Zero filed records without provenance | 100% |
| Duplicate detection rate | 100% (no double-files) |
| Quarterly review completion (all 12 deals valued) | 100% by day 3 of each quarter |
