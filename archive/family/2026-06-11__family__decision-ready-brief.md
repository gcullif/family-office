# Family — Decision-Ready Brief (2026-06-11)

Run: `trun_b7d17f0e99f7490f9f5c731a90a328ae` | Scope: family master data, genealogical relationship logic, sensitive-data governance for minors, document workflows, family records.

## Findings
- [FACT] "GEDCOM 7.0 was released in 2021 as the latest version of the GEDCOM format for the transmission and storage of genealogical information." (S1) — the genealogy index of the archive can interoperate with the prevailing open standard.
- [FACT] "ISO 15489 establishes the fundamental concepts and principles for creating, capturing, and managing records." (S2) — the records-management backbone (versioning, capture, retention) has an international standard to anchor on.
- [FACT] GDPR Article 4(11) defines consent as "any freely given, specific, informed and unambiguous indication of the data subject's wishes by which he or she, by a statement or by a clear affirmative action, signifies agreement to the processing of personal data relating to him or her." (S3, verified against the EDPB PDF 2026-06-11)
- [FACT] "When providing information society services to children on the basis of consent, controllers will be expected to make reasonable efforts to verify that the user is over the age of digital consent, and these measures should be proportionate to the nature and risks of the processing activities." (S3) — directly relevant to the platform's permission-by-readiness principle for younger generations.
- [INFERENCE] The ICO Age Appropriate Design Code reportedly contains 15 standards for protecting children's data online; the run asserted this but the citation carried no excerpt and the page could not be fetched (unsupported_claim).
- [INFERENCE] NARA's definition of vital records ("essential to the continued functioning of an organization...") appears in the run content but is not backed by a verbatim excerpt (unsupported_claim).
- [INFERENCE] For the platform: model family members per GEDCOM-compatible person/event/relationship structures; treat consent for minors as a first-class workflow (parental authorisation, age verification, proportionate checks); apply ISO 15489-style capture/audit/versioning to every family record.

## QA & Gaps
- **Missing Excerpts**: S3 (EDPB) — repaired via gap research with two verified verbatim excerpts. S4 (ICO) and S5 (NARA) — fetches returned empty; remain without excerpts.
- **Weak Sources**: None flagged (all five are standards bodies, regulators, or national archives).
- **Unsupported Claims**: ICO "15 standards" claim; NARA vital-records definition. Both kept as [INFERENCE].
- **Gap Research Performed**: EDPB PDF fetched and quotes verified verbatim (2026-06-11). ICO and NARA pages attempted; both returned empty content and were not retried via other means.
- **Confidence**: medium — core consent and records-standard anchors verified; two supporting sources unverified.
- **Dedup Actions**: None (run_id unique across batch).
