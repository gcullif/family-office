# System Architecture: Family Office Passive Investment Operations

> **Philosophy**: GitHub is the system of record. Every financial fact is a file. Every change is a commit. Every decision has provenance.

---

## 1. Repo Folder Structure

```
family-office/
├── deals/                          # One subfolder per deal — static deal records
│   └── {deal-slug}/
│       ├── deal.json               # Canonical deal record (schemas/deal.schema.json)
│       ├── ic_memo.md              # Investment committee memo (pre-investment)
│       └── deal_doc_pointers.json  # Pointers to PDFs/signed docs in S3 or Drive
│
├── deal-updates/                   # Immutable ingested updates (POST-investment ops)
│   └── YYYY/MM/DD/
│       └── {deal-slug}--{update-type}--{source}--{hash8}.json
│
├── valuations/                     # Valuation records triggered by deal updates
│   └── {deal-slug}/
│       └── valuation_{YYYY-MM-DD}_{hash8}.json
│
├── cashflow/                       # CFO/Liquidity module
│   ├── cashflow.json               # Rolling cashflow record
│   ├── runway_snapshots/
│   │   └── runway_{YYYY-MM-DD}.json
│   └── summaries/
│       └── cashflow_summary_{YYYY-MM}.md
│
├── public-marks/                   # Daily/weekly public equity price snapshots
│   └── YYYY/MM/
│       ├── price_snapshot_{YYYY-MM-DD}.csv
│       └── portfolio_marks_{YYYY-MM-DD}.json
│
├── docs/                           # Architecture, workflow, and decision docs
│   ├── architecture.md             # This file
│   ├── workflows_ingestion.md
│   ├── skills_deal_evaluation.md
│   ├── skills_deal_updates_ops.md
│   ├── cashflow_module.md
│   ├── scheduled_price_updates.md
│   ├── testing_and_evals.md
│   ├── cli_vs_web_memo.md
│   └── phase2_hr_cfo.md
│
├── schemas/                        # JSON Schema definitions (draft-07)
│   ├── deal.schema.json
│   ├── deal_update.schema.json
│   ├── valuation.schema.json
│   └── cashflow.schema.json
│
├── scripts/                        # CLI automation scripts
│   ├── ingest_deal_update.py       # Main ingestion pipeline
│   ├── fetch_public_marks.py       # Scheduled price fetcher
│   ├── run_valuation.py            # Valuation calculation runner
│   ├── cashflow_snapshot.py        # CFO runway snapshot generator
│   ├── match_deal.py               # Deal matching logic
│   ├── changelog_writer.py         # CHANGELOG.md auto-appender
│   └── update_project_structure.py
│
├── tests/                          # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/                   # Golden dataset JSON files
│
├── evals/                          # LLM eval harness
│   ├── golden_dataset.json         # 20 synthetic deal updates
│   ├── eval_runner.py
│   └── results/
│
├── working/                        # In-progress research, drafts, IC memos
│   └── deal-eval/
│       └── {deal-slug}/
│           ├── ic_memo.md
│           └── notes.md
│
├── .env.example                    # Placeholder secrets (never real values)
├── .gitignore
├── CHANGELOG.md                    # Auto-updated on every commit touching records
├── CLAUDE.md                       # Instructions for Claude agents working in this repo
└── README.md                       # Human onboarding guide
```

---

## 2. Branching Model

### Branch Naming

| Branch type | Pattern | Example |
|---|---|---|
| Main (protected) | `main` | `main` |
| Feature / filing | `feature/{description}` | `feature/ingest-acme-q2-update` |
| Hotfix | `hotfix/{description}` | `hotfix/fix-valuation-schema` |
| Eval run | `eval/{date}` | `eval/2026-06-23` |

### Rules

- All changes flow through PRs to `main`. Direct pushes to `main` are blocked except for automated scripts.
- Automated scripts (scheduled jobs, ingestion pipeline) commit directly to `main` via a dedicated `ci-bot` GitHub user — only for additive file writes (new records, new snapshots). Modifications to existing records require a PR.
- Tags follow `v{major}.{minor}.{patch}-{YYYY-MM-DD}` (e.g., `v1.0.0-2026-06-23`). Tags are created at milestone releases.

### CHANGELOG.md Auto-Update

Every script that writes a new record appends a line to `CHANGELOG.md` before committing:

```
## [2026-06-23]
- FILED: deal-updates/2026/06/23/acme-corp--earnings--email--a3f9b1c2.json
- VALUATION: valuations/acme-corp/valuation_2026-06-23_b7d2e4f1.json (triggered by earnings update)
- MARKS: public-marks/2026/06/price_snapshot_2026-06-23.csv
```

Format: `scripts/changelog_writer.py` handles all appends. Never hand-edit CHANGELOG.md.

---

## 3. Secrets Policy

### .env.example (committed to repo)

```env
# --- API Keys (store in 1Password vault: "Family Office Ops") ---
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# --- Email Ingestion ---
IMAP_HOST=imap.gmail.com
IMAP_USER=deals@familyoffice.com
IMAP_PASSWORD=your_app_password_here

# --- Storage ---
S3_BUCKET=family-office-documents
S3_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_here
GDRIVE_FOLDER_ID=your_gdrive_folder_id_here

# --- Notifications ---
SLACK_WEBHOOK_URL=your_slack_webhook_here
```

### What is NEVER committed to the repo

| Forbidden item | Alternative |
|---|---|
| Real API keys | Store in 1Password, export to GitHub Secrets |
| PDFs with PII | Store in S3/GDrive, commit a `.pointer.json` file |
| Signed legal documents | Same as PDFs |
| Tax returns | `docs/tax/2024-return.pointer.json` pointing to S3 |
| Bank statements | Pointer file + S3 |
| SSNs, EINs in raw files | Reference entity slug only in repo |

### Pointer File Pattern

Instead of committing sensitive documents, commit a pointer:

```json
{
  "document": "2024 Federal Tax Return — Smith Family Office LLC",
  "storage": "s3",
  "bucket": "family-office-documents",
  "key": "tax/2024/smith-family-office-2024-federal-return.pdf",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "uploaded_at": "2025-04-15T10:22:00Z",
  "uploaded_by": "grayson.culliford@hivefs.com",
  "access": "1Password vault: Family Office Ops > S3 credentials"
}
```

Stored at: `docs/tax/2024-return.pointer.json`

---

## 4. Barbell Investment Philosophy Structure

Inspired by Tony Robbins' *Money: Master the Game* and Scott Kupor's *Secrets of Sand Hill Road*.

```
┌─────────────────────────────────────────────────────────────┐
│                    BARBELL STRUCTURE                        │
│                                                             │
│  Layer 1: LIQUIDITY RUNWAY / CFO                            │
│  ─────────────────────────────────────────────────────      │
│  • 6–24 months of operating expenses in liquid assets       │
│  • Money market, T-Bills, HYSA                              │
│  • Zero illiquidity risk; instant access                    │
│  • Managed by: cashflow/ module                             │
│                                                             │
│  Layer 2: DEFENSIVE COMPOUNDING                             │
│  ─────────────────────────────────────────────────────      │
│  • Low-cost index funds (VTSAX, VTI, BND)                   │
│  • Rental real estate with positive FCF                     │
│  • Investment-grade credit / bonds                          │
│  • Goal: match/beat inflation, preserve purchasing power    │
│  • Managed by: deals/ (type=public-equity, real-estate)     │
│                                                             │
│  Layer 3: POWER-LAW BETS                                    │
│  ─────────────────────────────────────────────────────      │
│  • Venture capital (direct + fund-of-funds)                 │
│  • PE buyouts, growth equity                                │
│  • Operating businesses (direct ownership)                  │
│  • Asymmetric upside; 10x+ or zero                          │
│  • Managed by: deals/ (type=VC, PE, operating-business)     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Repo Mapping

| Barbell Layer | `barbell_layer` field value | Primary repo locations |
|---|---|---|
| Liquidity Runway | `liquidity-runway` | `cashflow/`, `deals/` (money market) |
| Defensive Compounding | `defensive-compounding` | `deals/`, `public-marks/` |
| Power-Law Bets | `power-law-bet` | `deals/`, `valuations/`, `deal-updates/` |

---

## 5. DealEvaluation vs. DealUpdatesOps

These are **two separate processes** with different triggers, artifacts, and ownership.

### DealEvaluation (Pre-Investment)

```
Trigger: New deal sourced / intro received
Owner: Investment team
Artifacts written to: working/deal-eval/{deal-slug}/
                       deals/{deal-slug}/   (on approval)
Purpose: Should we invest?
State: prospect → (approved) → active
       prospect → (rejected) → archived in working/deal-eval/
```

Key artifacts:
- `ic_memo.md` — investment committee memo
- `deal.json` stub — schema-compliant, status=`prospect`
- `risk_matrix.md` — deal-specific risk register
- Git tag on approval: `deal-eval/{deal-slug}/approved-v1`

### DealUpdatesOps (Post-Investment)

```
Trigger: Incoming update (email, PDF, web article, manual note)
Owner: Ops / automation pipeline
Artifacts written to: deal-updates/YYYY/MM/DD/
                       valuations/{deal-slug}/  (if triggered)
Purpose: What happened to something we already own?
State: RECEIVED → PARSED → MATCHED → FILED → PROCESSED
```

Key artifacts:
- `{deal-slug}--{update-type}--{source}--{hash8}.json` — immutable update record
- `valuation_{YYYY-MM-DD}_{hash8}.json` — if update triggers valuation refresh
- CHANGELOG.md append — automated
- Alert if `confidence_score < 0.7` or `needs_review = true`

### Side-by-Side Comparison

| Dimension | DealEvaluation | DealUpdatesOps |
|---|---|---|
| Trigger | New deal sourced | Incoming update on existing deal |
| Human involvement | High (IC approval required) | Low (automated; human only on flags) |
| Primary folder | `working/deal-eval/` then `deals/` | `deal-updates/` then `valuations/` |
| Schema | `deal.schema.json` | `deal_update.schema.json` + `valuation.schema.json` |
| Frequency | Episodic | Continuous / scheduled |
| Reversible? | Approval creates permanent deal record | Updates are immutable; corrections add new record |
| Downstream effect | Portfolio goes live | Valuation refresh, cashflow update, alerts |

---

## 6. Key Design Principles

1. **Immutability**: Filed records are never edited. Corrections create a new record with `corrects_ref` pointing to the original.
2. **Provenance everywhere**: Every JSON record has a `provenance` object with `source`, `timestamp_utc`, `author`, `file_hash`.
3. **Human-in-the-loop**: Automated pipelines halt and queue to `NEEDS_REVIEW` when `confidence_score < 0.7`.
4. **Schema-first**: Nothing is written to disk without passing `jsonschema` validation against the relevant schema.
5. **Grep-friendly**: All records are plain JSON/Markdown. `grep -r "acme-corp" deals/` finds everything instantly.
6. **No database required**: Git IS the database. Queryable via `jq`, `grep`, `find`. Frontend-agnostic by design.
