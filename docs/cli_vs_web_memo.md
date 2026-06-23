# Decision Memo: CLI-First vs. Web App / API-First

**Date**: 2026-06-23
**Author**: Grayson Culliford
**Status**: Final
**Decision**: CLI-First — with thin UI layer added in Phase 2

---

## 1. Comparison Table

| Dimension | CLI-First (Git + JSON + Python scripts) | Web App / API-First (Next.js + REST API + DB) |
|---|---|---|
| **Setup time** | 1–3 days (clone repo, install deps, run scripts) | 3–8 weeks (design API, set up DB, build UI, deploy infra) |
| **Cost** | Near-zero — GitHub free tier, no hosting, no DB | $50–$500/mo (hosting, DB, auth service, monitoring) |
| **Security** | Secrets in 1Password + GitHub Secrets; no public surface; no auth layer to exploit | Auth layer adds attack surface; API keys, JWT tokens, session management required |
| **UX** | CLI / terminal; requires basic command line comfort | Browser UI accessible to non-technical family members |
| **Maintainability** | Low — plain files, no framework churn, no migrations | Medium-High — framework updates, DB migrations, dependency rot |
| **Auditability** | Perfect — git log IS the audit trail; every change attributed to author/timestamp | Requires separate audit logging; DB changes harder to audit than file diffs |
| **Queryability** | `grep`, `jq`, `find` — powerful but requires CLI knowledge | SQL + UI search — more accessible but adds infrastructure |
| **Team size required** | 1 person can operate fully; no DevOps required | Requires at minimum 1 full-stack developer to maintain |
| **Onboarding** | README + CLAUDE.md; any developer can understand in 30 minutes | Requires architecture docs, env setup, DB seeding, local dev environment |
| **Frontend flexibility** | Any frontend can read JSON files from git — lock-in zero | Locked into API contract; changing schema requires migrations |
| **Disaster recovery** | `git clone` = full recovery; no backup strategy needed | DB backup strategy required; recovery can take hours |
| **Schema evolution** | Add fields to JSON + schema; old records remain valid | DB migration scripts required; risk of data loss |
| **Offline capability** | Fully offline — no internet required once repo is cloned | Requires API server to be running |
| **Compliance/audit** | Git history satisfies most audit requirements | Requires additional audit log infrastructure |

---

## 2. 30-Day CLI-First Plan

### Week 1: Foundation (Days 1–7)

**Goal**: Repo is set up, schemas validated, one deal filed end-to-end.

| Day | Deliverable |
|---|---|
| 1 | `git init`, create folder structure per `docs/architecture.md`, add `.gitignore`, `.env.example` |
| 2 | Commit all 4 schemas (`deal`, `deal_update`, `valuation`, `cashflow`). Run `jsonschema` validation on sample records. |
| 3 | Create first real `deal.json` for each active deal in portfolio. Validate all against schema. |
| 4 | Write `scripts/ingest_deal_update.py` — email ingestion path only |
| 5 | Test ingest on 3 real recent emails. File 3 deal update records. |
| 6 | Set up `symbol_mapping.json`. Run `fetch_public_marks.py --dry-run` for all symbols. |
| 7 | First successful `git commit` with real data. CHANGELOG updated. End-of-week review. |

**Repo deliverables by Day 7**:
```
deals/           # All active deals filed
schemas/         # 4 schemas committed and tested
scripts/ingest_deal_update.py   # Working email path
scripts/fetch_public_marks.py   # Working dry-run
public-marks/symbol_mapping.json
CHANGELOG.md     # 3+ entries
```

### Week 2: Automation (Days 8–14)

**Goal**: Ingestion pipeline handles email, PDF, Excel. Valuation pipeline works.

| Day | Deliverable |
|---|---|
| 8 | Add PDF ingestion path to `ingest_deal_update.py` (pdfplumber + LLM extraction) |
| 9 | Add Excel ingestion path (openpyxl) |
| 10 | Write `scripts/match_deal.py` with all 3 tiers (deterministic, fuzzy, NEEDS_REVIEW) |
| 11 | Write `scripts/run_valuation.py` for mark-to-market and cost-basis methods |
| 12 | Write `scripts/cashflow_snapshot.py` — runway calculation + alert rules |
| 13 | Run unit tests for all scripts. Fix failures. |
| 14 | End-of-week: all scripts working on real data. 10+ deal updates filed. |

**Repo deliverables by Day 14**:
```
scripts/ingest_deal_update.py   # Email + PDF + Excel paths
scripts/match_deal.py
scripts/run_valuation.py
scripts/cashflow_snapshot.py
tests/unit/                     # Core unit tests passing
deal-updates/                   # 10+ real records
valuations/                     # 5+ real valuation records
```

### Week 3: Scheduling + Testing (Days 15–21)

**Goal**: GitHub Actions running daily. Test suite green.

| Day | Deliverable |
|---|---|
| 15 | Set up `.github/workflows/daily-marks.yml` — cron at 17:30 ET |
| 16 | Set up `.github/workflows/pr-checks.yml` — unit + schema + path tests |
| 17 | Write integration tests for full ingest pipeline |
| 18 | Set up IMAP polling with cron or GitHub Actions schedule |
| 19 | Run golden dataset eval on 10 cases from `evals/golden_dataset.json` |
| 20 | Fix any eval failures. Aim for ≥ 80% pass rate. |
| 21 | End-of-week: CI/CD green. First daily marks snapshot committed automatically. |

**Repo deliverables by Day 21**:
```
.github/workflows/daily-marks.yml
.github/workflows/pr-checks.yml
tests/integration/
evals/golden_dataset.json       # 10 cases minimum
evals/results/run_2026-{date}.json
public-marks/YYYY/MM/           # 5+ days of price snapshots
```

### Week 4: Polish + Documentation (Days 22–30)

**Goal**: System is fully operational and documented for a second contributor.

| Day | Deliverable |
|---|---|
| 22 | Write `README.md` — 15-minute onboarding guide |
| 23 | Update `CLAUDE.md` for this repo |
| 24 | Run `scripts/cashflow_snapshot.py` on real portfolio — file first monthly summary |
| 25 | File first quarterly valuation review (all active deals) |
| 26 | Add remaining 10 golden dataset eval cases |
| 27 | Run full nightly eval — achieve ≥ 85% pass rate |
| 28 | Create v1.0.0 git tag |
| 29 | Dry-run onboarding: can a fresh collaborator follow README to clone + run in 30 min? |
| 30 | System live. All active deals valued. CI green. CHANGELOG current. |

---

## 3. "Thin UI Later" Plan

The CLI-first design deliberately keeps the door open to any future frontend.

### How CLI-first preserves options

| CLI-first design choice | How it enables thin UI later |
|---|---|
| All records are JSON files | Any frontend (React, Vue, static site) reads JSON directly — no API layer needed initially |
| Schemas define every field | Schemas double as API contracts — just wrap with FastAPI or Express |
| Git history = audit log | Any future compliance UI just renders `git log` output |
| Deterministic file paths | `GET /deal-updates/{year}/{month}/{day}/{filename}` maps directly to file path |
| No database | Add SQLite or Postgres later; migrate from JSON files with a one-time import script |
| `jq` queries work today | Same JSON structure works with any query layer |

### Minimal viable thin UI (when needed)

```
Option A: Static site (< 1 day to build)
  - Next.js static export or Astro
  - Reads JSON files from public-marks/, deals/, valuations/
  - Deployed as GitHub Pages — zero hosting cost
  - No auth needed if repo is private and UI is local

Option B: Dashboard shell (1 week to build)
  - ops-dashboard-demo/ already exists in the project
  - Point it at deals/*.json and public-marks/*.json
  - Add read routes for deal-updates/ and valuations/
  - No new backend required
```

---

## 4. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| File sprawl: too many files to navigate | Medium | Low | Strict naming conventions + `grep -r` + `jq` queries cover all use cases |
| No full-text search | Medium | Low | `grep -r "search term" deals/ deal-updates/` works immediately; add `ripgrep` for speed |
| Non-technical family member can't use CLI | High | Medium | Dashboard shell (Option B above) added in Phase 2; CLI is ops-facing only |
| Git conflicts when multiple people file simultaneously | Low | Medium | Scripts use atomic writes + unique filenames (hash-based); conflicts are extremely rare |
| Large binary files bloat repo | Low | High | Policy enforced: no PDFs in git; pointer files only; `.gitignore` blocks common binary extensions |
| Onboarding friction for new contributor | Medium | Medium | README + CLAUDE.md; `make setup` script installs deps; working in 30 min |
| LLM extraction errors (wrong field values) | Medium | Medium | Human-in-the-loop on NEEDS_REVIEW; eval harness catches regressions |
| Cron job fails silently | Low | Medium | GitHub Actions sends email/Slack on workflow failure; nightly health check script |

---

## 5. Recommendation

**Recommendation: CLI-First, with thin UI in Phase 2.**

**Reasoning**:

1. **Speed to value**: A working, schema-valid, fully audited system can be operational in 30 days. A web app would take 2–3 months to reach equivalent functionality.

2. **Auditability is native**: The family office's primary legal and compliance need is an unimpeachable audit trail. Git provides this by default — no additional logging infrastructure required.

3. **Cost**: $0/month vs. $50–$500/month indefinitely. For a single-family office managing its own portfolio, this is meaningful.

4. **Security posture**: No public-facing API = no API attack surface. Secrets never leave 1Password. Risk is dramatically lower.

5. **Team reality**: This is a 1–2 person operation. CLI-first matches actual team capacity. A web app requires ongoing maintenance that diverts attention from investment work.

6. **Future optionality**: Every design decision — JSON files, schemas, deterministic paths, git-as-database — is reversible. Adding a UI layer later requires zero rearchitecting.

The only meaningful cost is UX: non-technical family members cannot use a CLI. That cost is deferred to Phase 2, when the dashboard shell is added on top of the already-working data layer.
