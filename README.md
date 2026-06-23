# Family Office Platform — Start Here

**Collaborators:** Grayson · JP   ·   **Started:** June 2026   ·   **Updated:** June 18, 2026

This is the front door. If you're new to the project, read this page, then open whichever
folder you need. Every folder also has its own `_README.md` explaining what belongs in it.

---

## What we're building

A **single ecosystem** where everything a family needs to manage, understand, and pass on their
wealth lives in one organized place — eliminating the constant link-hopping between custodian
portals, PDF downloads, advisor emails, and scattered logins.

Today a family steward bounces between Fidelity, Schwab, a trust company portal, a property
manager, and a dozen PDFs in their inbox. This platform replaces all of that with one hub:
external accounts and apps (Fidelity, Schwab, etc.) are linked *in*, PDF statements and
documents arrive and are sorted automatically by a document routing agent, and every
record — whether pulled from a live account or filed from a statement — is organized by domain
and linked back to the family members it belongs to.

It's not a wealth dashboard. It's a living archive that captures what a family owns, *who* built
it, *why* decisions were made, and what it means for future generations. It's a **template
platform**: no real family's data lives here yet. The records in `archive/` are example/template
records used to build and test the format, and will be swapped for a real family's data once the
platform is complete.

It serves three readers at once: **the steward today** (precise ledgers and valuations), **the
next generation** (plain-language story beside the numbers), and **a future successor** (durable
records with the reasoning behind decisions). Every record links back to a family member or
generation — the genealogy is the index through which the whole archive is read.

**Five principles** every feature obeys: (1) provenance over data, (2) narrative beside numbers,
(3) time depth not just current state, (4) plain language, (5) permission by role and readiness.
Full detail lives in `CLAUDE.md`.

---

## Where everything lives

```
Family Office Platform/
│
├── README.md              ← you are here: the map
├── CLAUDE.md              ← the framework + the rules for how records get filed
├── PROJECT-STRUCTURE.md   ← auto-generated live record counts (do not edit by hand)
│
├── archive/               ← THE SOURCE OF TRUTH. Family records, split into 8 domains.
│   ├── general-research/      market & macro research, memos, due diligence
│   ├── investments/           holdings, valuations, performance, rationale
│   ├── real-assets/           property, land, physical holdings
│   ├── trusts-governance/     trusts, entities, governance, fiduciary records
│   ├── philanthropy/          giving history, DAFs, foundations, grants
│   ├── family/                family members, lineage, founding narratives
│   ├── tax/                   tax strategy, filings, planning memos, cost basis
│   └── strategy/              IPS, allocation targets, long-term planning
│
├── schema/                ← canonical record templates (the shape every record follows)
│                             AAPL_holding_record.json is the master holding template
│
├── skills/                ← the automation that files records (.skill source bundles)
│
├── evals/                 ← quality testing: eval reviews + the skills tracker spreadsheet
│
├── working/               ← in-progress: STATUS.md (live roadmap) + research/design drafts
│
├── scripts/               ← utility scripts (update_project_structure.py regenerates PROJECT-STRUCTURE.md)
│
├── ops-dashboard-demo/    ← Next.js source code for the dashboard UI (dev only)
│
└── dashboard-dist/        ← compiled dashboard — what START HERE.bat actually serves
```

**The one rule that makes this simple:** everything the family *owns or is* goes in `archive/`,
sorted into one of eight domains. Everything else is *supporting machinery* —
templates (`schema/`), automation (`skills/`), testing (`evals/`), work-in-progress
(`working/`), and the UI (`ops-dashboard-demo/` → builds into `dashboard-dist/`).

---

## Two layers — know the difference

| Layer | What it is | Who it's for |
|---|---|---|
| **Notion** ([link](https://app.notion.com/p/37b673a9e1f6814098dad5ab0bb7b096)) | Section-by-section research + reasoning that backs up the platform | Future collaborators and contributors |
| **Dashboard** (`ops-dashboard-demo/` → `dashboard-dist/`) | Live web app: prototype PDFs, statements, organized documents, Parallel routing agent | The family and stewards |

Notion explains *why* things are structured the way they are. The dashboard is the thing the family actually uses — it holds documents and surfaces records, and includes a routing agent that uses Parallel research to classify incoming PDFs and file them into the right section automatically.

---

## Quick links

- **🖥️ Open the dashboard** → double-click `START HERE — Open Dashboard.bat` (serves on localhost:8765)
- **📖 Notion collaborator layer** → https://app.notion.com/p/37b673a9e1f6814098dad5ab0bb7b096
- **📊 Live record counts** → `PROJECT-STRUCTURE.md`
- **Current status & roadmap** → `working/STATUS.md`
- **How records are structured & filed** → `CLAUDE.md`
- **The records themselves** → `archive/`
- **The master record template** → `schema/AAPL_holding_record.json`
- **Production architecture** → `working/production-system-architecture.md`
