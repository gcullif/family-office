# GitHub Setup Guide — Family Office Platform

This is the system of record for all family office operations. GitHub provides:
- **Version control** for every record, schema, and script
- **Pull requests** as the approval mechanism for consequential changes
- **CI** to validate schemas and scripts on every push
- **GitHub Secrets** for API keys (never committed)
- **Claude Code** integration so the AI can read and commit to the repo directly

---

## 1. Initialize the local repo

From the project folder, run:

```bash
git init
git add .
git commit -m "init: family office platform baseline"
```

---

## 2. Create a GitHub repository

1. Go to https://github.com/new
2. Name it something like `family-office` or `hive-fo-platform`
3. Set it to **Private**
4. Do NOT initialize with a README (you already have one)

Then push:

```bash
git remote add origin https://github.com/YOUR_ORG/family-office.git
git branch -M main
git push -u origin main
```

---

## 3. Configure GitHub Secrets

In the repo → Settings → Secrets and variables → Actions, add:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (`sk-ant-...`) |
| `ALPHA_VANTAGE_KEY` | For scheduled price updates (optional) |

The server reads `ANTHROPIC_API_KEY` from a local `.env` file. For CI/CD, use the GitHub Secret.

---

## 4. Configure Claude Code

Install Claude Code CLI if not installed:
```bash
npm install -g @anthropic-ai/claude-code
```

From the project root:
```bash
claude
```

Claude Code will read `CLAUDE.md` automatically and have full context on the project structure, filing conventions, and skills.

### Configure Claude Code to commit changes

Add to your `.claude/settings.json` (or run `claude config`):
```json
{
  "git": {
    "autoCommit": false,
    "defaultBranch": "main"
  }
}
```

With `autoCommit: false`, Claude Code will stage changes and show you a diff before committing — recommended for consequential records.

---

## 5. Branch and PR workflow

| Action | Branch convention | Who merges |
|---|---|---|
| File a new deal | `feat/deals/deal-slug` | Steward review → merge |
| Ingest deal updates | `ops/deal-updates/YYYY-MM-DD` | Auto-merge after CI green |
| Valuation refresh | `ops/valuation/deal-slug-YYYY-MM` | Human approval required |
| Schema changes | `schema/field-name-change` | Architecture review |
| Dashboard changes | `ui/feature-name` | Visual review |

**Protect `main`:** In repo Settings → Branches → Add rule for `main`:
- Require PR before merging
- Require CI to pass
- Do not allow force push

---

## 6. Recommended Claude Code workflows

### Ingest a deal update
```bash
# In Claude Code terminal (or your shell):
python scripts/ingest_deal_update.py quarterly-update.pdf
git add deal-updates/
git commit -m "ops: ingest Q2 2026 update for [deal-name]"
git push origin ops/deal-updates/2026-Q2
# Open PR → review → merge
```

### Create a new deal
```bash
python scripts/ingest_deal_update.py --new-deal
git add deals/
git commit -m "deals: add [deal-name]"
```

### Run schema validation locally
```bash
pip install jsonschema
python -c "import json,jsonschema; jsonschema.Draft7Validator.check_schema(json.load(open('schemas/deal.schema.json'))); print('OK')"
```

---

## 7. What never gets committed

See `.gitignore`. Key exclusions:
- `.env` files with real API keys
- `uploads/` — raw uploaded PDFs (too large, may contain PII)
- `demo-statements/*.pdf` — use pointer files instead
- Any document with SSN, account numbers, or legal signatures

Use **pointer files** for sensitive docs:
```json
{
  "pointer_type": "s3",
  "bucket": "family-office-docs",
  "key": "tax/2024-return.pdf",
  "sha256": "abc123...",
  "description": "2024 Federal + State Tax Return",
  "access": ["steward", "accountant"]
}
```

---

## 8. Keeping Claude Code in sync

Every time you open Claude Code in this project, it reads:
- `CLAUDE.md` — project rules and filing conventions
- `PROJECT-STRUCTURE.md` — live record counts
- `schemas/` — canonical data shapes

Run after major filing sessions:
```bash
python scripts/update_project_structure.py .
git add PROJECT-STRUCTURE.md && git commit -m "chore: update project structure"
```
