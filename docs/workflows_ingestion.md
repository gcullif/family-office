# Workflows: Deal Update Ingestion

> **Purpose**: Define the end-to-end pipeline for receiving, parsing, matching, and filing any incoming deal update — email, PDF, spreadsheet, or manual note.

---

## 1. State Machine

Every update passes through these states. States are stored in the filed JSON record under `processing_state`.

```
                    ┌──────────────────────────────────────────┐
                    │                                          │
  Incoming update   │                                          ▼
  ─────────────►  RECEIVED ──► PARSED ──► MATCHED ──► FILED ──► PROCESSED
                                  │           │
                                  │           │  confidence < 0.7
                                  │           │  or ambiguous match
                                  ▼           ▼
                              REJECTED   NEEDS_REVIEW ──► (human resolves) ──► MATCHED
                          (malformed,    (queued in
                           duplicate)    needs-review/)
```

### State Definitions

| State | Meaning | Next action |
|---|---|---|
| `RECEIVED` | Raw input accepted by pipeline | Begin parsing |
| `PARSED` | Structured data extracted from raw input | Attempt deal match |
| `MATCHED` | Linked to a specific `deal.json` in `deals/` | Write to `deal-updates/` |
| `FILED` | Record written to disk, schema-validated | Trigger downstream (valuation, cashflow) |
| `PROCESSED` | Downstream effects complete, CHANGELOG updated | Terminal state |
| `NEEDS_REVIEW` | Confidence too low or match ambiguous | Human resolves via checklist |
| `REJECTED` | Malformed input or confirmed duplicate | Logged but not filed |

### Error Handling Rules

- If `confidence_score < 0.7` after matching: set `needs_review = true`, write to `needs-review/{YYYY-MM-DD}/{hash8}.json`, send Slack alert.
- If schema validation fails: state = `REJECTED`, log error to `logs/rejected_{YYYY-MM-DD}.log`.
- If exact duplicate detected (same `file_hash` already in `deal-updates/`): state = `REJECTED`, log "duplicate: {original_path}".
- If parsing yields zero extractable fields: state = `REJECTED`, log "empty parse: {source_type}".

---

## 2. Folder Naming Convention

All filed updates follow this exact path pattern:

```
deal-updates/YYYY/MM/DD/{deal-slug}--{update-type}--{source}--{hash8}.json
```

### Component Definitions

| Component | Values | Example |
|---|---|---|
| `YYYY/MM/DD` | UTC date filed | `2026/06/23` |
| `{deal-slug}` | Slug from `deal.json` | `acme-corp-series-b` |
| `{update-type}` | See enum below | `earnings` |
| `{source}` | `email`, `pdf`, `web`, `excel`, `manual` | `email` |
| `{hash8}` | First 8 chars of SHA-256 of raw content | `a3f9b1c2` |

### Update Type Enum

`earnings` / `financing-round` / `valuation-mark` / `distribution` / `company-news` / `macro-event` / `management-change` / `exit` / `other`

### Example Paths for 5 Update Types

```
deal-updates/2026/06/23/acme-corp-series-b--earnings--email--a3f9b1c2.json
deal-updates/2026/06/15/horizon-vc-fund-ii--financing-round--pdf--b7d2e4f1.json
deal-updates/2026/06/10/downtown-loft-portfolio--valuation-mark--excel--c9e1a7b3.json
deal-updates/2026/06/01/acme-corp-series-b--distribution--email--d4f8c2e5.json
deal-updates/2026/05/28/acme-corp-series-b--management-change--web--e6a3d9f7.json
```

---

## 3. Deal Matching Strategy

Executed by `scripts/match_deal.py`. Three tiers, attempted in order.

### Tier 1: Deterministic Match

Check for exact match on any of:
- Ticker symbol (e.g., `AAPL` in content matches `deal.json` field `ticker: "AAPL"`)
- Domain/URL (e.g., `acme.com` in sender domain matches `deal.json` field `domain: "acme.com"`)
- Deal ID (e.g., explicit `deal_id` field in structured input)
- CUSIP / ISIN (for public securities)

If deterministic match found: `confidence_score = 1.0`, proceed to MATCHED.

### Tier 2: Fuzzy Match

If no deterministic match, score candidates using:

```python
score = (
    0.40 * name_similarity(update_company, deal.name)   # rapidfuzz ratio
  + 0.25 * contact_match(update_sender, deal.contacts)  # email domain match
  + 0.20 * keyword_overlap(update_text, deal.tags)      # Jaccard on keyword sets
  + 0.15 * sector_match(update_sector, deal.sector)     # exact string match
)
```

- If top candidate `score >= 0.85`: `confidence_score = score`, proceed to MATCHED.
- If top candidate `score >= 0.70` and `score < 0.85`: `confidence_score = score`, set `needs_review = true`, proceed to NEEDS_REVIEW.
- If top candidate `score < 0.70`: set `needs_review = true`, state = NEEDS_REVIEW.

### Tier 3: NEEDS_REVIEW Queue

Human checklist (stored as comment in `needs-review/{hash8}.json`):

```
NEEDS_REVIEW Checklist
──────────────────────
[ ] 1. Does the company name in the update match any deal in deals/?
[ ] 2. Does the sender email domain match any deal contact?
[ ] 3. Does the content reference a known ticker, CUSIP, or deal ID?
[ ] 4. Is this a new company we don't have a deal record for yet?
[ ] 5. Is this spam / irrelevant / macro noise with no specific deal?

Resolution options:
  A) Manually set deal_id and rerun pipeline with --force-match
  B) Create new deal.json stub and rerun
  C) Mark as REJECTED (no deal match, not relevant)
```

---

## 4. Five Worked Examples

### Example 1: Quarterly Earnings Email (High Confidence)

**Input**: Email from `ir@acmecorp.com`, subject "Acme Corp Q2 2026 Investor Update"

**Match**: Domain `acmecorp.com` matches `deal.json` field `domain: "acmecorp.com"` — deterministic match.

**Filed record**:
```json
{
  "id": "upd_7f3a9b2c-1d4e-5f6a-8b9c-0d1e2f3a4b5c",
  "deal_id": "deal_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "deal_slug": "acme-corp-series-b",
  "update_type": "earnings",
  "processing_state": "PROCESSED",
  "received_at": "2026-07-15T09:14:22Z",
  "filed_at": "2026-07-15T09:14:45Z",
  "source_type": "email",
  "raw_content_pointer": {
    "storage": "s3",
    "key": "raw-updates/2026/07/15/a3f9b1c2-acme-q2-email.eml",
    "sha256_full": "a3f9b1c2d5e8f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6"
  },
  "extracted_data": {
    "period": "Q2 2026",
    "revenue_usd": 4200000,
    "revenue_growth_yoy_pct": 18.5,
    "ebitda_usd": 840000,
    "ebitda_margin_pct": 20.0,
    "cash_balance_usd": 3100000,
    "headcount": 47,
    "key_highlights": [
      "Launched enterprise tier in April",
      "ARR crossed $4M milestone",
      "Net revenue retention: 118%"
    ],
    "next_milestone": "Series C targeting Q4 2026"
  },
  "provenance": {
    "source_url": null,
    "email_from": "ir@acmecorp.com",
    "author": "Acme Corp IR Team",
    "timestamp_utc": "2026-07-15T09:14:22Z",
    "file_hash": "a3f9b1c2",
    "ingest_script_version": "1.2.0"
  },
  "confidence_score": 1.0,
  "needs_review": false,
  "review_notes": null,
  "valuation_refresh_triggered": true,
  "valuation_ref": "valuations/acme-corp-series-b/valuation_2026-07-15_b8e2f1a3.json",
  "tags": ["earnings", "q2-2026", "arr-milestone", "series-c-prep"]
}
```

**File path**: `deal-updates/2026/07/15/acme-corp-series-b--earnings--email--a3f9b1c2.json`

---

### Example 2: New Financing Round PDF

**Input**: PDF attachment from `legal@horizonvc.com`, filename `Horizon_Fund_II_Closing_Memo_2026.pdf`

**Match**: Contact email domain `horizonvc.com` matches `deal.json` contacts field — fuzzy match score 0.91.

**Filed record**:
```json
{
  "id": "upd_2c4e6a8b-0d2f-4e6a-8c0e-2a4c6e8a0c2e",
  "deal_id": "deal_b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "deal_slug": "horizon-vc-fund-ii",
  "update_type": "financing-round",
  "processing_state": "PROCESSED",
  "received_at": "2026-06-15T14:30:00Z",
  "filed_at": "2026-06-15T14:31:12Z",
  "source_type": "pdf",
  "raw_content_pointer": {
    "storage": "s3",
    "key": "raw-updates/2026/06/15/b7d2e4f1-horizon-closing-memo.pdf",
    "sha256_full": "b7d2e4f1a3c5e7b9d1f3a5c7e9b1d3f5a7c9e1b3d5f7a9c1e3b5d7f9a1c3e5b7"
  },
  "extracted_data": {
    "round_type": "Fund II Final Close",
    "total_fund_size_usd": 85000000,
    "family_office_commitment_usd": 500000,
    "close_date": "2026-06-10",
    "management_fee_pct": 2.0,
    "carry_pct": 20.0,
    "investment_period_years": 4,
    "fund_life_years": 10
  },
  "provenance": {
    "source_url": null,
    "email_from": "legal@horizonvc.com",
    "author": "Horizon Ventures Legal",
    "timestamp_utc": "2026-06-15T14:30:00Z",
    "file_hash": "b7d2e4f1",
    "ingest_script_version": "1.2.0"
  },
  "confidence_score": 0.91,
  "needs_review": false,
  "valuation_refresh_triggered": true,
  "valuation_ref": "valuations/horizon-vc-fund-ii/valuation_2026-06-15_c9f3a7b5.json",
  "tags": ["fund-close", "vc", "power-law-bet"]
}
```

**File path**: `deal-updates/2026/06/15/horizon-vc-fund-ii--financing-round--pdf--b7d2e4f1.json`

---

### Example 3: Rental Property Valuation Mark (Excel)

**Input**: Excel file `Downtown_Loft_Portfolio_Appraisal_Q2_2026.xlsx` from property manager.

**Match**: Filename keyword `Downtown Loft Portfolio` matches deal `name` field — fuzzy name similarity 0.93.

**Filed record**:
```json
{
  "id": "upd_4e8a2c6f-1b3d-5e7a-9c1e-3a5c7e9a1c3e",
  "deal_id": "deal_c3d4e5f6-a7b8-9012-cdef-123456789012",
  "deal_slug": "downtown-loft-portfolio",
  "update_type": "valuation-mark",
  "processing_state": "PROCESSED",
  "received_at": "2026-06-10T11:00:00Z",
  "filed_at": "2026-06-10T11:02:33Z",
  "source_type": "excel",
  "raw_content_pointer": {
    "storage": "s3",
    "key": "raw-updates/2026/06/10/c9e1a7b3-downtown-loft-appraisal.xlsx",
    "sha256_full": "c9e1a7b3d5f7a9c1e3b5d7f9a1c3e5b7d9f1a3c5e7b9d1f3a5c7e9b1d3f5a7c9"
  },
  "extracted_data": {
    "appraisal_value_usd": 2850000,
    "appraiser": "Metro Commercial Appraisal Group",
    "effective_date": "2026-05-31",
    "cap_rate_pct": 5.8,
    "gross_rent_annual_usd": 198000,
    "vacancy_rate_pct": 4.2,
    "noi_annual_usd": 165300
  },
  "provenance": {
    "source_url": null,
    "email_from": "mgmt@loftproperty.com",
    "author": "Metro Commercial Appraisal Group",
    "timestamp_utc": "2026-06-10T11:00:00Z",
    "file_hash": "c9e1a7b3",
    "ingest_script_version": "1.2.0"
  },
  "confidence_score": 0.93,
  "needs_review": false,
  "valuation_refresh_triggered": true,
  "valuation_ref": "valuations/downtown-loft-portfolio/valuation_2026-06-10_d0a4b8c2.json",
  "tags": ["appraisal", "real-estate", "defensive-compounding"]
}
```

**File path**: `deal-updates/2026/06/10/downtown-loft-portfolio--valuation-mark--excel--c9e1a7b3.json`

---

### Example 4: Distribution Notice (Email)

**Input**: Email from `distributions@acmecorp.com`, subject "Acme Corp — Series B Distribution Notice"

**Match**: Deterministic — domain `acmecorp.com`.

**File path**: `deal-updates/2026/06/01/acme-corp-series-b--distribution--email--d4f8c2e5.json`

Key `extracted_data` fields:
```json
{
  "distribution_amount_usd": 75000,
  "distribution_type": "return_of_capital",
  "record_date": "2026-05-31",
  "payment_date": "2026-06-15",
  "per_unit_usd": null,
  "tax_character": "return_of_capital"
}
```

---

### Example 5: Ambiguous Case — NEEDS_REVIEW

**Input**: Email from `newsletter@techcrunch.com`, subject "Apex Biosciences raises $40M Series C"

**Match attempt**:
- No domain match (techcrunch.com is not a deal contact)
- Name fuzzy match: "Apex Biosciences" vs deals in portfolio:
  - `apex-financial-services`: name similarity 0.51 — too low
  - `biotech-index-fund`: keyword overlap 0.20 — too low
- Top score: 0.51 — below NEEDS_REVIEW threshold

**Action**: Written to `needs-review/2026/05/28/e6a3d9f7.json` with state `NEEDS_REVIEW`.

**Needs-review record**:
```json
{
  "id": "nr_5f9b3d7a-2e4c-6f8a-0b2d-4f6a8b0d2f4a",
  "processing_state": "NEEDS_REVIEW",
  "received_at": "2026-05-28T08:45:00Z",
  "source_type": "email",
  "email_from": "newsletter@techcrunch.com",
  "subject": "Apex Biosciences raises $40M Series C",
  "top_match_candidate": "apex-financial-services",
  "top_match_score": 0.51,
  "confidence_score": 0.51,
  "raw_content_pointer": {
    "storage": "local",
    "key": "needs-review/2026/05/28/e6a3d9f7-raw.eml"
  },
  "human_checklist": {
    "question_1_company_match": null,
    "question_2_sender_match": null,
    "question_3_known_id": null,
    "question_4_new_company": null,
    "question_5_spam_or_noise": null
  },
  "resolution": null,
  "resolved_by": null,
  "resolved_at": null,
  "file_hash": "e6a3d9f7"
}
```

Human resolves: "This is a TechCrunch newsletter item about a company not in our portfolio. Mark REJECTED — macro news, no deal match."

---

## 5. Ingestion Methods

### 5a. Email Forward Ingestion

```
1. Ops team forwards update email to: ingest@familyoffice.com (or auto-forwarded)
2. scripts/ingest_deal_update.py --source email --input-file /path/to/email.eml
   OR
   Pipeline polls IMAP inbox every 15 minutes (cron job)
3. Script extracts: sender, subject, body, attachments
4. Attachments (PDF/Excel) are extracted and processed separately (see 5b)
5. Body text is parsed via LLM extraction prompt → structured extracted_data
6. File hash computed on raw .eml bytes
7. Match logic runs (Tier 1 → Tier 2 → Tier 3)
8. Record written to deal-updates/ or needs-review/
9. CHANGELOG.md updated, git commit
```

### 5b. PDF / Excel Ingestion

```
1. scripts/ingest_deal_update.py --source pdf --input-file /path/to/document.pdf
2. PDF: pdfplumber extracts text + tables → LLM extraction prompt
   Excel: openpyxl reads all sheets → LLM extraction prompt with sheet names + values
3. File hash computed on raw bytes → check for duplicates
4. Extracted data structured against update_type sub-schema
5. Match logic runs
6. Raw file uploaded to S3, pointer written to raw_content_pointer
7. Record written, CHANGELOG updated, git commit
```

### 5c. Manual Note Ingestion

```
1. Human runs: scripts/ingest_deal_update.py --source manual --deal-slug acme-corp-series-b
2. Script prompts for: update_type, key facts (free text), date
3. Script creates minimal extracted_data from free text
4. confidence_score set to 1.0 (human-authored)
5. Record written to deal-updates/ with source_type=manual
6. CHANGELOG updated, git commit
```

**Manual note example command**:
```bash
python scripts/ingest_deal_update.py \
  --source manual \
  --deal-slug acme-corp-series-b \
  --update-type company-news \
  --note "CEO confirmed verbally at LP meeting that Series C process begins Q4 2026. Targeting $20M at $120M pre-money." \
  --author "grayson.culliford@hivefs.com"
```
