# Working in this project

This file tells Claude (and any collaborator) how this repository is organized and how new
material should be filed. Read `README.md` first for the map; this file covers the *rules*.

## The thesis

This is a generational archive that happens to track wealth. A descendant opening it decades
from now should learn, from the same screen, both what the family owns and who built it, why,
and what it cost to steward. Numbers are the surface; provenance and narrative are the substance.

## The five principles (every record obeys all five)

1. **Provenance over data** — every meaningful record carries a *why*: who decided, when, the
   reasoning, the source. A figure without provenance is incomplete.
2. **Narrative beside numbers** — each record has a plain-language story alongside the ledger.
3. **Time depth** — show lineage and history (when acquired, prior values, who stewarded it),
   not just current state.
4. **Plain language** — any record must be legible to a family member with no finance background.
5. **Permission by role and readiness** — family, trustees, staff, and advisors see different
   layers; younger generations may see narrative before full figures.

Family is the center, not a section: every record links back to a family member or generation.

## Where things go

| If it is... | It goes in... |
|---|---|
| A record of something the family owns or is | `archive/<domain>/` |
| The template/shape a record should follow | `schema/` |
| Automation that creates or files records | `skills/` |
| A quality test or eval of the skills | `evals/` |
| In-progress research, drafts, or the roadmap | `working/` |

The eight archive domains: `general-research`, `investments`, `real-assets`,
`trusts-governance`, `philanthropy`, `family`, `tax`, `strategy`.

## How records are filed

The live skills file records automatically into `archive/` — do not rename the domain folders
or auto-filing will break. They map content as follows:

- **fo-archive-ingest** — files any record into the right `archive/` domain.
- **parallel-fo-ingest** — files Parallel.ai research output.
- **research-auto-ingest** — auto-classifies any pasted research into a domain.

Records are markdown files named `slug-YYYY-MM-DD.md` (e.g.
`vtsax-vanguard-total-stock-market-2026-06-09.md`). Structured holding records follow the JSON
shape in `schema/AAPL_holding_record.json` — the canonical template: every field carries a
`value`, a `plain_language` explanation, and a `source_ref` for provenance.

## Two distinct layers — understand both

**Notion** and the **dashboard** are separate things and serve different purposes. Never conflate them.

### Notion — collaborator research layer
https://app.notion.com/p/37b673a9e1f6814098dad5ab0bb7b096

Notion is for *future collaborators*, not for the family. It is organized section by section to give any new contributor the research and reasoning behind each domain — the *why* that backs up what shows up on the dashboard. Think of it as the annotated bibliography for the platform: each section explains what belongs in that domain, links to key archive records, and surfaces the Parallel research that informed the design.

Notion does **not** hold raw documents or PDF statements. It holds explanations, research summaries, and links.

### Dashboard — the live family-facing product
The dashboard is a **separate web app** (Next.js source in `ops-dashboard-demo/`, compiled output in `dashboard-dist/`, served by `START HERE — Open Dashboard.bat` on localhost:8765).

This is what the family actually uses. It holds:
- **Prototype PDF statements** and financial documents, organized by domain
- **All live records** surfaced in a navigable UI
- **A document routing agent** that reads incoming documents and classifies them into the right section automatically

When a new PDF or statement arrives, the routing agent reads it, identifies the asset class, entity, or family member it belongs to, and drops it into the correct dashboard section. Collaborators configure which documents feed into which domain; the agent does the sorting.

### Maintenance — always refresh the structure index after filing

After any record is filed (by any skill or manually), run:

```bash
python "<project_path>/scripts/update_project_structure.py" "<project_path>"
```

This regenerates `PROJECT-STRUCTURE.md` with live record counts for every archive domain. The filing skills (`research-auto-ingest`, `parallel-fo-ingest`) do this automatically as their final step. If you file a record manually, run the script yourself before finishing.

`PROJECT-STRUCTURE.md` is the always-current quick-reference for collaborators. It is auto-generated — do not edit it by hand.

## Naming conventions

- Archive records: `descriptive-slug-YYYY-MM-DD.md`
- Folder docs: `_README.md` (the underscore sorts it to the top)
- Superseded files move to an `_archived-old-versions/` subfolder rather than being deleted.
