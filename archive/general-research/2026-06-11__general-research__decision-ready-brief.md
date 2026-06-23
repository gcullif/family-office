# General Research — Decision-Ready Brief (2026-06-11)

Run: `trun_b7d17f0e99f7490fad08720fc0a90678` | Scope: research operating model, source credibility rubric, evidence capture, KB taxonomy, monitoring, brief templates, collaboration, KPIs (NOTES 1–8).

## Findings
- [FACT] "MoSCoW prioritization... is a popular prioritization technique for managing requirements. The acronym MoSCoW represents four categories of initiatives: must-have, should-have, could-have, and won’t-have, or will not have right now." (S1, repaired 2026-06-11; weak_source_tier_3) — usable as the triage/prioritization vocabulary for research intake.
- [FACT] Stanford CoreNLP's quote annotator "Deterministically picks out quotes from a text." (S5) — automated verbatim-quote extraction is technically feasible for the evidence-capture pipeline.
- [FACT] A research project intake form template exists with sections including "PROJECT DESCRIPTION" and "REQUIRED RESOURCES" (S2; fragmentary excerpts; weak_source_tier_3).
- [INFERENCE] The full operating model in NOTES 1–8 (intake→triage→assign→publish→archive, three-tier credibility rubric, evidence objects with checksums, entity/tag taxonomy, watchlists, brief templates, collaboration lifecycle, KPI set) is synthesized design guidance from the run, not supported by verbatim excerpts (unsupported_claim).
- [INFERENCE] Digital-provenance capture standards (TrueScreen, S3) and source red-flag criteria (LibGuides, S4) and verified-capture tooling (OpenOrigins, S6) were cited without excerpts; the claims attributed to them remain unverified (unsupported_claim).
- [INFERENCE] For the platform: the three-tier source rubric and evidence-per-claim linkage in NOTE 2–3 map directly onto the project's "provenance over data" principle and should become the schema for every archive record's source_ref.

## QA & Gaps
- **Missing Excerpts**: S3 (TrueScreen), S4 (LibGuides), S6 (OpenOrigins) — empty excerpts[]; gap research not attempted for these (low-value tier-3 sources; cap budget prioritized elsewhere). S1 repaired via gap research.
- **Weak Sources**: S1 (vendor glossary), S2 (vendor template PDF), S3 (vendor article), S4 (school libguide), S6 (vendor marketing) — all weak_source_tier_3.
- **Unsupported Claims**: All NOTE 1–8 framework content; all claims attributed to S3/S4/S6.
- **Gap Research Performed**: Fetched ProductPlan (S1) and captured verbatim definition. Did not attempt S3/S4/S6 (deliberate cap allocation). Nothing fetched failed for this domain.
- **Confidence**: low — frameworks are reasonable but rest almost entirely on synthesis and tier-3 sources; only two narrow facts verified.
- **Dedup Actions**: None (run_id unique across batch).
