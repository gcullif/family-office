# Investments — Decision-Ready Brief (2026-06-11)

Run: `trun_b7d17f0e99f7490f85d1c2105549bd39` | Original run contained **no citations and no notes** (placeholder output only). All evidence below was added via bounded gap research (5 sources, retrieved 2026-06-11).

## 12-Topic Coverage

### 1) Investment operating model & governance
- [FACT] SEC-registered investment advisers must "Adopt and implement written policies and procedures reasonably designed to prevent violation, by you and your supervised persons, of the Act and the rules that the Commission has adopted under the Act" (17 CFR 275.206(4)-7, S5).
- [FACT] The same rule requires advisers to "Designate an individual (who is a supervised person) responsible for administering the policies and procedures" — a chief compliance officer (S5).
- [INFERENCE] A family-office investment module should mirror this structure: written policy library, named accountable owner, and periodic review cadence, even where the office is not itself a registered adviser.

### 2) Strategic asset allocation workflow
- [FACT] "Asset allocation involves dividing your investments among different assets, such as stocks, bonds, and cash. The asset allocation decision is a personal one." (SEC Investor.gov, S1)
- [FACT] "To bring your portfolio back to its original asset allocation, you may need to rebalance your portfolio." (S1)
- [INFERENCE] The platform's SAA workflow should capture target weights, drift thresholds, and rebalancing decisions with provenance (who approved, when, why).

### 3) Public markets implementation
- [FACT] "When determining your asset allocation, consider diversification— the practice of spreading money among different investments to reduce risk." (S1)
- [INFERENCE] Public-markets records should link each holding to the allocation target it implements and record diversification rationale in plain language.

### 4) Manager/fund selection pipeline
- [FACT] "The ILPA DDQ and Diversity Metrics Template are intended to standardize the key areas of inquiry posed by investors during their diligence of managers and to provide a framework for ongoing monitoring of progress related to DEI." (ILPA, S2)
- [INFERENCE] The manager pipeline should adopt a standardized questionnaire structure (ILPA DDQ 2.0 as the reference template) with stage gates: sourcing → screening → DDQ → IC decision.

### 5) Due diligence pack design
- [FACT] ILPA publishes the DDQ 2.0 as PDF/DOCX with a user guide and summary of changes (S2).
- [INFERENCE] The due diligence pack should be a versioned document set with every answer linked to a source document and reviewer sign-off.

### 6) Private fund operations
- Unknown. (No authoritative source with verbatim excerpt retrieved within caps; qa_flag: unsupported_topic)

### 7) Private direct deals workflow
- Unknown. (No authoritative source with verbatim excerpt retrieved within caps; qa_flag: unsupported_topic)

### 8) Valuation & pricing governance
- [FACT] "The International Private Equity and Venture Capital Valuation (IPEV) Guidelines set out recommendations, intended to represent current best practice, on the valuation of Private Capital Investments." (IPEV, S3)
- [FACT] "The 2025 edition of the IPEV Guidelines were published on 11 December 2025" (S3).
- [INFERENCE] Private-asset valuations in the platform should reference IPEV fair-value methodology, record the valuation basis per holding, and log valuation approvals.

### 9) Performance measurement & attribution
- [FACT] GIPS (CFA Institute): "we champion standards for calculating and presenting investment performance based on the ethical principles of fair representation and full disclosure." (S4)
- [INFERENCE] Performance reporting should follow GIPS-aligned calculation conventions and disclose methodology beside every figure.

### 10) Risk management & limits
- Unknown (partial). [INFERENCE] Risk-tolerance and time-horizon concepts from S1 imply limits should be set per family objectives, but no dedicated risk-framework source with verbatim excerpt was retrieved within caps. (qa_flag: unsupported_topic_partial)

### 11) Portfolio reporting pack
- Unknown. (No authoritative source with verbatim excerpt retrieved within caps; qa_flag: unsupported_topic)

### 12) Controls, audit trails, and data management
- [FACT] Advisers must "Review, no less frequently than annually, the adequacy of the policies and procedures established pursuant to this section and the effectiveness of their implementation" (17 CFR 275.206(4)-7, S5).
- [INFERENCE] The platform should enforce an annual control-review workflow with immutable audit logs of consequential actions.

## QA & Gaps
- **Missing Excerpts**: None remaining among filed sources (all 5 gap-research sources carry verbatim excerpts). The original run supplied zero citations (`missing_citations`).
- **Weak Sources**: None — all 5 sources are tier-1 (SEC/eCFR, ILPA, IPEV, CFA Institute/GIPS).
- **Unsupported Claims**: Topics 6, 7, 11 fully Unknown; topic 10 partially Unknown. All [INFERENCE] items above are design recommendations not directly quoted from sources (`unsupported_claim` applies to each).
- **Gap Research Performed**: Fetched and quoted 5 sources (Investor.gov, ILPA DDQ, IPEV, GIPS, eCFR 206(4)-7). Failed fetch: SEC "Information for Newly-Registered Investment Advisers" (empty response). Per-domain cap of 5 reached; topics 6/7/10/11 left Unknown rather than using weak sources.
- **Confidence**: low-medium — evidence anchors are authoritative but cover only 8 of 12 topics; original run contributed no usable content.
- **Dedup Actions**: None (run_id unique across batch).
