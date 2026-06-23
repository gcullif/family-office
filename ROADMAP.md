# Roadmap

**Family Office Platform** — generational archive + wealth management dashboard  
_Started: June 2026 · Last updated: June 23, 2026_

---

## What we're building

A single ecosystem where everything a family needs to manage, understand, and pass on their wealth lives in one organized place. External accounts (Fidelity, Schwab, etc.) link in, PDF statements are sorted automatically by a document routing agent, and every record is organized by domain and linked back to the family members it belongs to.

It serves three readers at once: the steward today (precise ledgers), the next generation (plain-language story beside the numbers), and a future successor (durable records with the reasoning behind decisions).

**Five principles every feature obeys:**
1. Provenance over data — every record carries a *why*
2. Narrative beside numbers — plain-language story alongside the ledger
3. Time depth — lineage and history, not just current state
4. Plain language — legible to a family member with no finance background
5. Permission by role and readiness — family, trustees, staff, and advisors see different layers

---

## ✅ Completed

### Archive — Example Records
- [x] Family & Genealogy — founding generation record
- [x] Investments — example index fund holding (VTSAX)
- [x] Real Assets — example vacation property record

### Schema
- [x] Canonical holding record schema (`schema/AAPL_holding_record.json`) — master template with provenance, valuation history, income, tax treatment, liquidity, and values alignment fields

### Skills (Automation)
- [x] `fo-archive-ingest` — file any record into the correct archive domain
- [x] `parallel-fo-ingest` — ingest Parallel.ai research output into archive
- [x] `research-auto-ingest` — auto-classify and file any pasted research content

### Evaluation & QA
- [x] Skill eval iteration 1
- [x] FO record update eval
- [x] Skills tracker spreadsheet (v2)

### Dashboard
- [x] Next.js dashboard UI (`ops-dashboard-demo/` → compiled to `dashboard-dist/`)
- [x] Prototype PDF statements organized by domain
- [x] Local server + launcher (`START HERE — Open Dashboard.bat`, serves on localhost:8765)

---

## 🔄 In Progress

### Archive — Incomplete Domains

| Domain | What's Done | What's Needed |
|---|---|---|
| **Family & Genealogy** | 1 founding-generation record | Stewardship transition record; generational timeline template |
| **Investments** | VTSAX fund record; AAPL JSON schema | Translate AAPL JSON → `archive/investments/` markdown record |
| **Real Assets** | 1 property record | Cross-reference link to a Trusts & Governance record |

---

## ⬜ Not Yet Started

### Archive — Empty Domains

| Domain | What Belongs Here |
|---|---|
| **Trusts & Governance** | Example trust record (referenced by real-assets example but not yet created); example LLC or governance doc |
| **Philanthropy** | Example charitable giving record, donor-advised fund, or foundation entry |
| **Tax** | Example tax planning memo, annual filing summary, or entity-level tax note |
| **Strategy** | Example investment policy statement, allocation framework, or long-term planning document |
| **General Research** | Example market research memo, due diligence note, or investment thesis |

### Platform — Core Features

| Feature | Description |
|---|---|
| **Document routing agent** | Reads incoming PDFs/statements → classifies by domain, entity, or family member → files into correct dashboard section automatically |
| **Permissions layer** | Role-based access control: family, trustees, staff, and advisors see different data layers; younger generations may see narrative before full figures |
| **Plain-language narrative views** | Human-readable story displayed beside every ledger record; teaches as it reports |
| **Generational timeline** | Time-depth view showing lineage, historical values, and the stewardship chain for every asset |
| **Genealogy index** | Family member as the primary navigation index — every record in every domain links back to a person or generation |

### Onboarding

| Item | Description |
|---|---|
| **Real family onboarding** | Replace all example/template records in `archive/` with a real family's data once all platform sections are complete and tested |

---

## 📌 Open Questions

1. Which archive domain gets fully fleshed out next — Trusts & Governance or Tax?
2. What skills should be built after the current three — a holdings-update skill? a research-fetch skill?
3. When does front-end / UX design work begin in earnest?
4. What's the rollout plan for the permissions layer — who are the first named roles?

---

## Repo structure

```
archive/          ← source of truth: all family records (8 domains)
schema/           ← canonical record templates
skills/           ← automation that classifies and files records
evals/            ← QA: skill eval reports + tracker spreadsheet
working/          ← STATUS.md (detailed roadmap) + in-progress drafts
scripts/          ← utility scripts (structure updater, etc.)
ops-dashboard-demo/  ← Next.js dashboard source
dashboard-dist/   ← compiled dashboard (what the launcher serves)
```

Full details: `README.md` (architecture) · `CLAUDE.md` (filing rules + five principles) · `working/STATUS.md` (granular task tracking)
