# Real Assets — Decision-Ready Brief (2026-06-11)

Run: `trun_b7d17f0e99f7490fb9dbd0ec0d6a3484` | Scope: real-estate module — operating model, master data, leasing, rent roll, opex, maintenance, CapEx, vendor/COI, performance reporting, risk & controls (NOTES 1–10).

## Findings
- [FACT] "Create detailed property profiles – address, acquisition date, legal structure, square footage, and market valuation. Map ownership to trusts, family" (S2, Masttro; truncated; weak_source_tier_3) — the property master record should link directly to trusts and family members, matching the project's family-as-index principle.
- [FACT] "Optiml's Real Estate Decision Intelligence software empowers asset managers, investors & consultancies to optimize Capex planning." (S1; weak_source_tier_3) — vendor tooling exists for CapEx optimization (vendor self-description).
- [FACT] "The best leasing automation software centralizes the entire leasing process into one connected workflow." (S3; truncated; weak_source_tier_3)
- [FACT] "Property Listings: The database should store detailed information about properties, including location, type ( residential , commercial, industrial), size..." (S4; truncated; weak_source_tier_3)
- [INFERENCE] NOTES 1, 4–10 (operating model, rent roll controls, opex budgeting, maintenance workflow, CapEx governance with draw schedules, COI tracking, NOI/occupancy KPIs, fraud/safety controls) are logical extensions acknowledged by the run itself as "consistent with the cited material but not directly quoted" (unsupported_claim).
- [INFERENCE] For the platform: each property record should carry acquisition provenance (when, from whom, by whose decision), ownership mapping to entities/trusts, and a stewardship history — extending S2's profile concept to the archive's time-depth principle.

## QA & Gaps
- **Missing Excerpts**: None (all four sources carry excerpts), though three are truncated mid-sentence.
- **Weak Sources**: S1, S2, S3, S4 — all weak_source_tier_3 (vendor marketing/blogs/sample-schema site).
- **Unsupported Claims**: NOTES 1, 4–10 content; the content's closing claim that "All statements are supported by publicly available professional sources" overstates support.
- **Gap Research Performed**: None for this domain — no empty excerpts to repair; cap budget allocated to domains with missing evidence. Truncated excerpts not re-retrieved.
- **Confidence**: low-medium — design direction is plausible but rests entirely on tier-3 sources.
- **Dedup Actions**: None (run_id unique across batch).
