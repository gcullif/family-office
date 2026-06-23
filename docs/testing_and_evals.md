# Testing and Evaluation Strategy

> **Goal**: Every record filed by this system is correct, complete, and provenance-bearing. Tests catch regressions before they hit production. Evals measure LLM-assisted pipeline quality on a repeatable golden dataset.

---

## 1. Test Matrix

### Unit Tests (`tests/unit/`)

| Test | What it validates | Input | Pass condition |
|---|---|---|---|
| `test_schema_deal.py` | `deal.schema.json` validates valid deal | Valid `deal.json` | `jsonschema` raises no error |
| `test_schema_deal_invalid.py` | Schema rejects invalid deal | Missing `provenance` field | `jsonschema.ValidationError` raised |
| `test_schema_deal_update.py` | `deal_update.schema.json` validates | Valid update JSON | No error |
| `test_schema_valuation.py` | `valuation.schema.json` validates | Valid valuation JSON | No error |
| `test_schema_cashflow.py` | `cashflow.schema.json` validates | Valid cashflow JSON | No error |
| `test_path_generation.py` | Deal update path is deterministic | `(slug, update_type, source, hash8)` → correct path string | Path matches expected |
| `test_matching_deterministic.py` | Ticker match yields score 1.0 | Input with `ticker=AAPL`, deal with `ticker=AAPL` | `confidence_score == 1.0` |
| `test_matching_fuzzy.py` | Fuzzy match scores correct | Input company name "Acme Corporation", deal name "Acme Corp" | Score >= 0.85 |
| `test_matching_below_threshold.py` | Low-confidence match triggers NEEDS_REVIEW | Input company "TechCo" vs no similar deal | `needs_review == True`, state == `NEEDS_REVIEW` |
| `test_duplicate_detection.py` | Same hash rejected | File existing `hash8` in index, submit same | State == `REJECTED` |
| `test_holiday_skip.py` | Market holiday returns False | `is_market_open("2026-07-04")` | `False` |
| `test_outlier_filter.py` | >20% daily move sets flag | Prior close $100, current close $125 | `outlier_flag == True` |
| `test_dscr_calculation.py` | DSCR computed correctly | NOI=$165300, annual debt service=$153600 | `dscr == 1.07` |
| `test_runway_calculation.py` | Runway months correct | total_liquid=$487000, monthly_burn=$42000 | `runway_months == 11.6` |

### Integration Tests (`tests/integration/`)

| Test | What it validates | Steps |
|---|---|---|
| `test_ingest_pipeline_email.py` | Full email → filed record | Run `ingest_deal_update.py` on fixture email; assert file written at correct path, schema valid, CHANGELOG updated |
| `test_ingest_pipeline_pdf.py` | Full PDF → filed record | Run on fixture PDF; assert path, schema, CHANGELOG |
| `test_valuation_trigger.py` | Earnings update → valuation written | Ingest earnings update; assert `valuations/{slug}/` has new record, `deal.json` updated |
| `test_needs_review_queue.py` | Low-confidence match → NEEDS_REVIEW file | Ingest ambiguous update; assert `needs-review/` has file, no `deal-updates/` record |
| `test_quarterly_review.py` | All active deals get valuations | Run `run_quarterly_review.py` on fixture portfolio; assert N valuation files created |
| `test_cashflow_snapshot.py` | Snapshot writes correct runway | Run `cashflow_snapshot.py` on fixture data; assert `runway_months` correct and alert fires if < 3 |

### End-to-End Tests (`tests/e2e/`)

| Test | What it validates |
|---|---|
| `test_e2e_email_to_record.py` | Raw email → MATCHED → FILED → PROCESSED → CHANGELOG entry → git commit |
| `test_e2e_quarterly_cycle.py` | Full quarterly review: 12 deals → 12 valuations → cashflow summary → CHANGELOG |
| `test_e2e_needs_review_resolution.py` | NEEDS_REVIEW → human resolve → re-run → FILED |
| `test_e2e_deal_eval_to_active.py` | IC memo created → deal.json validated → filed in deals/ → git tag |

---

## 2. Golden Dataset — 20 Synthetic Deal Updates

Location: `evals/golden_dataset.json`

Each entry has: `id`, `description`, `input_file` (path to fixture), `expected_deal_match`, `expected_path`, `expected_update_type`, `expected_valuation_triggered`, `notes`.

```json
[
  {
    "id": "gd_001",
    "description": "Standard quarterly earnings email from known company",
    "input_file": "tests/fixtures/emails/acme-corp-q2-earnings.eml",
    "expected_deal_match": "acme-corp-series-b",
    "expected_match_confidence_min": 1.0,
    "expected_path": "deal-updates/2026/07/15/acme-corp-series-b--earnings--email--{hash}.json",
    "expected_update_type": "earnings",
    "expected_valuation_triggered": true,
    "expected_state": "PROCESSED",
    "notes": "Happy path — deterministic domain match"
  },
  {
    "id": "gd_002",
    "description": "VC fund closing memo PDF with known fund manager",
    "input_file": "tests/fixtures/pdfs/horizon-fund-ii-closing-memo.pdf",
    "expected_deal_match": "horizon-vc-fund-ii",
    "expected_match_confidence_min": 0.85,
    "expected_path": "deal-updates/2026/06/15/horizon-vc-fund-ii--financing-round--pdf--{hash}.json",
    "expected_update_type": "financing-round",
    "expected_valuation_triggered": true,
    "expected_state": "PROCESSED",
    "notes": "Fuzzy match via contact email domain"
  },
  {
    "id": "gd_003",
    "description": "Distribution notice with explicit deal ID in email body",
    "input_file": "tests/fixtures/emails/acme-distribution-notice.eml",
    "expected_deal_match": "acme-corp-series-b",
    "expected_match_confidence_min": 1.0,
    "expected_path": "deal-updates/2026/06/01/acme-corp-series-b--distribution--email--{hash}.json",
    "expected_update_type": "distribution",
    "expected_valuation_triggered": false,
    "expected_state": "PROCESSED",
    "notes": "Distribution does not trigger valuation by default"
  },
  {
    "id": "gd_004",
    "description": "Real estate appraisal Excel from property manager",
    "input_file": "tests/fixtures/excel/downtown-loft-appraisal-q2-2026.xlsx",
    "expected_deal_match": "downtown-loft-portfolio",
    "expected_match_confidence_min": 0.85,
    "expected_path": "deal-updates/2026/06/10/downtown-loft-portfolio--valuation-mark--excel--{hash}.json",
    "expected_update_type": "valuation-mark",
    "expected_valuation_triggered": true,
    "expected_state": "PROCESSED",
    "notes": "Name fuzzy match on filename"
  },
  {
    "id": "gd_005",
    "description": "Management change: CEO departure announcement from company IR",
    "input_file": "tests/fixtures/emails/acme-ceo-departure.eml",
    "expected_deal_match": "acme-corp-series-b",
    "expected_match_confidence_min": 1.0,
    "expected_path": "deal-updates/2026/05/15/acme-corp-series-b--management-change--email--{hash}.json",
    "expected_update_type": "management-change",
    "expected_valuation_triggered": false,
    "expected_state": "PROCESSED",
    "notes": "Management change triggers Slack alert but not valuation"
  },
  {
    "id": "gd_006",
    "description": "TechCrunch article — company not in portfolio",
    "input_file": "tests/fixtures/web/techcrunch-apex-biosciences.html",
    "expected_deal_match": null,
    "expected_match_confidence_min": null,
    "expected_path": "needs-review/2026/05/28/{hash}.json",
    "expected_update_type": "company-news",
    "expected_valuation_triggered": false,
    "expected_state": "NEEDS_REVIEW",
    "notes": "Ambiguous — no portfolio match. Should land in NEEDS_REVIEW."
  },
  {
    "id": "gd_007",
    "description": "Duplicate: same earnings email submitted twice",
    "input_file": "tests/fixtures/emails/acme-corp-q2-earnings.eml",
    "expected_deal_match": "acme-corp-series-b",
    "expected_match_confidence_min": null,
    "expected_path": null,
    "expected_update_type": "earnings",
    "expected_valuation_triggered": false,
    "expected_state": "REJECTED",
    "notes": "Exact duplicate — file_hash already exists. Must be REJECTED, not filed twice."
  },
  {
    "id": "gd_008",
    "description": "Malformed PDF: corrupted file, cannot parse",
    "input_file": "tests/fixtures/pdfs/corrupted-file.pdf",
    "expected_deal_match": null,
    "expected_match_confidence_min": null,
    "expected_path": null,
    "expected_update_type": null,
    "expected_valuation_triggered": false,
    "expected_state": "REJECTED",
    "notes": "pdfplumber raises exception. Pipeline must catch gracefully and REJECT."
  },
  {
    "id": "gd_009",
    "description": "Macro event email: Fed rate decision, no specific portfolio company",
    "input_file": "tests/fixtures/emails/fed-rate-decision-june-2026.eml",
    "expected_deal_match": null,
    "expected_match_confidence_min": null,
    "expected_path": "needs-review/2026/06/12/{hash}.json",
    "expected_update_type": "macro-event",
    "expected_valuation_triggered": false,
    "expected_state": "NEEDS_REVIEW",
    "notes": "Macro event with no specific deal. Human decides if any deal is affected."
  },
  {
    "id": "gd_010",
    "description": "Exit notice: acquisition announcement from company CEO",
    "input_file": "tests/fixtures/emails/acme-corp-acquisition-close.eml",
    "expected_deal_match": "acme-corp-series-b",
    "expected_match_confidence_min": 1.0,
    "expected_path": "deal-updates/2026/09/01/acme-corp-series-b--exit--email--{hash}.json",
    "expected_update_type": "exit",
    "expected_valuation_triggered": true,
    "expected_state": "PROCESSED",
    "notes": "Exit — triggers valuation, Slack alert to #deals-exits, human confirms status change to realized"
  },
  {
    "id": "gd_011",
    "description": "Similar company names: 'Apex Capital' email — portfolio has 'Apex Financial Services'",
    "input_file": "tests/fixtures/emails/apex-capital-update.eml",
    "expected_deal_match": "apex-financial-services",
    "expected_match_confidence_min": 0.70,
    "expected_path": "needs-review/2026/06/20/{hash}.json",
    "expected_update_type": "company-news",
    "expected_valuation_triggered": false,
    "expected_state": "NEEDS_REVIEW",
    "notes": "Ambiguous name similarity 0.72 — above NEEDS_REVIEW floor but below 0.85 auto-match threshold"
  },
  {
    "id": "gd_012",
    "description": "Manual note: LP meeting verbal update on Horizon VC Fund II",
    "input_file": null,
    "input_cli_args": "--source manual --deal-slug horizon-vc-fund-ii --update-type company-news --note 'GP confirmed Fund II is 60% deployed as of June 2026. Next capital call expected Q4.'",
    "expected_deal_match": "horizon-vc-fund-ii",
    "expected_match_confidence_min": 1.0,
    "expected_path": "deal-updates/2026/06/23/horizon-vc-fund-ii--company-news--manual--{hash}.json",
    "expected_update_type": "company-news",
    "expected_valuation_triggered": false,
    "expected_state": "PROCESSED",
    "notes": "Manual notes always confidence=1.0"
  },
  {
    "id": "gd_013",
    "description": "Public market public price snapshot — VTSAX outlier: >20% single-day move",
    "input_file": "tests/fixtures/prices/vtsax-outlier-day.json",
    "expected_deal_match": "vtsax-index-fund",
    "expected_match_confidence_min": 1.0,
    "expected_path": "public-marks/2026/06/price_snapshot_2026-06-19.csv",
    "expected_update_type": "valuation-mark",
    "expected_valuation_triggered": true,
    "expected_state": "NEEDS_REVIEW",
    "notes": "Outlier flag set. Should not auto-commit. Human confirms before filing."
  },
  {
    "id": "gd_014",
    "description": "Operating business quarterly FCF update via Excel model",
    "input_file": "tests/fixtures/excel/smithco-operating-q2-2026.xlsx",
    "expected_deal_match": "smithco-operating-business",
    "expected_match_confidence_min": 0.88,
    "expected_path": "deal-updates/2026/07/05/smithco-operating-business--earnings--excel--{hash}.json",
    "expected_update_type": "earnings",
    "expected_valuation_triggered": true,
    "expected_state": "PROCESSED",
    "notes": "Fuzzy match on filename. Excel extraction should capture EBITDA, capex, debt service rows."
  },
  {
    "id": "gd_015",
    "description": "LP capital call notice: requires wire transfer",
    "input_file": "tests/fixtures/pdfs/horizon-fund-ii-capital-call-q3.pdf",
    "expected_deal_match": "horizon-vc-fund-ii",
    "expected_match_confidence_min": 0.91,
    "expected_path": "deal-updates/2026/07/01/horizon-vc-fund-ii--other--pdf--{hash}.json",
    "expected_update_type": "other",
    "expected_valuation_triggered": false,
    "expected_state": "PROCESSED",
    "notes": "Capital call classified as 'other'. Action required flag should be set in extracted_data."
  },
  {
    "id": "gd_016",
    "description": "Bond fund quarterly NAV statement (BND equivalent)",
    "input_file": "tests/fixtures/pdfs/bnd-q2-nav-statement.pdf",
    "expected_deal_match": "bnd-bond-position",
    "expected_match_confidence_min": 0.95,
    "expected_path": "deal-updates/2026/07/02/bnd-bond-position--valuation-mark--pdf--{hash}.json",
    "expected_update_type": "valuation-mark",
    "expected_valuation_triggered": true,
    "expected_state": "PROCESSED",
    "notes": "Fixed income NAV update triggers valuation using nav method"
  },
  {
    "id": "gd_017",
    "description": "Email with no company name, no attachments, only generic 'investor update'",
    "input_file": "tests/fixtures/emails/generic-investor-update-no-context.eml",
    "expected_deal_match": null,
    "expected_match_confidence_min": null,
    "expected_path": "needs-review/2026/06/25/{hash}.json",
    "expected_update_type": null,
    "expected_valuation_triggered": false,
    "expected_state": "NEEDS_REVIEW",
    "notes": "Zero extractable fields. Empty parse → NEEDS_REVIEW."
  },
  {
    "id": "gd_018",
    "description": "Two updates for same deal on same day — different content",
    "input_file": "tests/fixtures/emails/acme-corp-two-updates-same-day.eml",
    "expected_deal_match": "acme-corp-series-b",
    "expected_match_confidence_min": 1.0,
    "expected_path": "deal-updates/2026/07/15/acme-corp-series-b--company-news--email--{hash}.json",
    "expected_update_type": "company-news",
    "expected_valuation_triggered": false,
    "expected_state": "PROCESSED",
    "notes": "Different content = different hash = not a duplicate. Both should be filed. This tests idempotency on distinct inputs."
  },
  {
    "id": "gd_019",
    "description": "Correction record: fixes a previously mis-filed update_type",
    "input_file": null,
    "input_cli_args": "--source manual --deal-slug acme-corp-series-b --corrects-ref deal-updates/2026/07/14/acme-corp-series-b--other--email--a1b2c3d4.json --update-type earnings --note 'Reclassified from other to earnings. Original parse missed revenue figures.'",
    "expected_deal_match": "acme-corp-series-b",
    "expected_match_confidence_min": 1.0,
    "expected_path": "deal-updates/2026/07/16/acme-corp-series-b--earnings--manual--{hash}.json",
    "expected_update_type": "earnings",
    "expected_valuation_triggered": true,
    "expected_state": "PROCESSED",
    "notes": "Correction creates NEW record with corrects_ref. Original is never deleted or modified."
  },
  {
    "id": "gd_020",
    "description": "Valuation with low confidence requires human approval before use",
    "input_file": "tests/fixtures/valuations/early-stage-vc-cost-basis.json",
    "expected_deal_match": "seedstage-startup-seed",
    "expected_match_confidence_min": 1.0,
    "expected_path": "valuations/seedstage-startup-seed/valuation_{date}_{hash}.json",
    "expected_update_type": "valuation-mark",
    "expected_valuation_triggered": true,
    "expected_state": "PROCESSED",
    "notes": "Cost-basis valuation on 18-month-old seed investment → confidence=low → human_approved must be false until manually set. Verify guardrail blocks LP report generation."
  }
]
```

---

## 3. Regression Checks

Run on every PR and nightly.

| Check | Command | Pass condition |
|---|---|---|
| Schema validation — all deals | `python tests/unit/test_all_schemas.py` | 0 errors across all `deals/*/deal.json` |
| Schema validation — all updates | `python tests/unit/test_all_deal_updates.py` | 0 errors |
| Deterministic paths | `python tests/unit/test_path_generation.py` | Same inputs always produce same path |
| Idempotency | Run ingestion twice on same input | Second run → REJECTED (duplicate), no new file written |
| Audit completeness | `python tests/unit/test_provenance_completeness.py` | Every JSON record in `deal-updates/` and `valuations/` has `provenance` object with all required fields |
| CHANGELOG currency | `python tests/unit/test_changelog_currency.py` | Every file in `deal-updates/` has a corresponding CHANGELOG entry |

---

## 4. LLM Scoring Rubric

Used by `evals/eval_runner.py` to score pipeline outputs against golden dataset.

### Dimensions

| Dimension | Scale | Definition |
|---|---|---|
| Groundedness | 0–3 | Do all extracted facts in `extracted_data` appear verbatim or clearly implied in the source? 0=fabrications present, 1=mostly grounded, 2=minor issues, 3=fully grounded |
| Completeness | 0–3 | Are all key facts from the source captured? 0=<50% captured, 1=50–75%, 2=75–95%, 3=95–100% |
| Correct routing | pass/fail | Does `update_type` match `expected_update_type`? |
| Correct artifacts written | pass/fail | Are all expected output files present at correct paths? |
| Provenance present | pass/fail | Does the filed record have a complete `provenance` object? |

### Thresholds

| Overall score | Decision |
|---|---|
| Groundedness ≥ 2 AND Completeness ≥ 2 AND all 3 pass/fail = pass | **PASS** |
| Groundedness ≥ 1 AND Completeness ≥ 1 AND ≥ 2/3 pass/fail | **NEEDS_REVIEW** (flag for human inspection) |
| Any other combination | **FAIL** |

### Eval Runner Command

```bash
python evals/eval_runner.py --dataset evals/golden_dataset.json --output evals/results/run_{date}.json
```

Output format: JSON with per-case scores + aggregate pass rate.

---

## 5. CI Plan

### Per-PR (must complete in < 2 minutes)

```yaml
# .github/workflows/pr-checks.yml
jobs:
  unit-tests:
    - pytest tests/unit/ -v --tb=short
  schema-validation:
    - python tests/unit/test_all_schemas.py
  deterministic-paths:
    - python tests/unit/test_path_generation.py
  provenance-check:
    - python tests/unit/test_provenance_completeness.py
```

### Nightly (runs at 02:00 ET)

```yaml
# .github/workflows/nightly.yml
jobs:
  integration-tests:
    - pytest tests/integration/ -v
  e2e-tests:
    - pytest tests/e2e/ -v
  llm-evals:
    - python evals/eval_runner.py --dataset evals/golden_dataset.json
    - python evals/eval_runner.py --assert-pass-rate 0.85  # Fail if < 85% pass
```

---

## 6. Evals Folder Structure

```
evals/
├── golden_dataset.json          # 20 synthetic test cases (this file)
├── eval_runner.py               # Runs pipeline on each case, scores with LLM rubric
├── scoring_rubric.md            # Detailed rubric definitions
├── results/
│   ├── run_2026-06-23.json      # Output of each eval run
│   └── run_2026-06-16.json
└── fixtures/                    # Symlinked to tests/fixtures/ or duplicated
```
