# Strategy — Decision-Ready Brief (2026-06-11)

Run: `trun_b7d17f0e99f7490fa1ac571174e10bff` | Scope: strategy operating model, objectives hierarchy, risk appetite, liquidity planning, scenario planning, policy library, decision log, reporting pack (NOTES 1–8).

## Findings
- [FACT] An "effective governance model is the cornerstone of a successful family office operating within a business" (S1, Plante Moran; excerpt truncated at start/end in source data).
- [FACT] "The four key components of a family office investment strategy are values-based customization, strategic asset allocation, risk management, and liquidity" (S2, Aleta; weak_source_tier_3, truncated).
- [FACT] "Building a family office requires careful planning, a clear vision, and a strong governance structure to ensure long-term wealth sustainability." (S3; weak_source_tier_3)
- [FACT] Family office governance "defines who has authority over wealth management, how family members communicate about financial matters, and what processes guide everything" (S4, Sage; weak_source_tier_3, truncated).
- [FACT] "Detailed meeting minutes should capture major decisions, action items, and the reasoning behind them." (S5, Phoenix Strategy Group; weak_source_tier_3, truncated) — directly supports the platform's decision-log-with-reasoning design.
- [INFERENCE] The NOTE 1–8 structure (mission → objectives hierarchy → policies → cadence; risk limits with breach protocols; liquidity buffers and drawdown procedures; scenario narratives; version-controlled policy library; attestations; KPI dashboards with narratives) is a synthesis; individual elements are not verbatim-supported (unsupported_claim).
- [INFERENCE] For the platform: the decision log (NOTE 7) is the strategy module's provenance backbone — every policy and allocation should link to a logged decision with reasoning, satisfying principles 1–3 of the project framework.

## QA & Gaps
- **Missing Excerpts**: None (all six sources carry excerpts).
- **Weak Sources**: S2, S3, S4, S5, S6 — vendor blogs, law-firm marketing, LinkedIn page (weak_source_tier_3). S6 is low-relevance (company self-description). S1 (Plante Moran) treated as tier-2 professional-services insight.
- **Unsupported Claims**: The full NOTE 1–8 framework content beyond the five quoted statements.
- **Gap Research Performed**: None for this domain — all sources already had excerpts; cap budget allocated to domains with missing evidence. Several excerpts are truncated mid-sentence (truncated_excerpt flags); full-quote re-retrieval not attempted.
- **Confidence**: medium-low — direction is consistent across sources, but source quality is predominantly tier-3.
- **Dedup Actions**: None (run_id unique across batch).
