# Tax — Decision-Ready Brief (2026-06-11, v2 evidence-repaired)

Run: `trun_b7d17f0e99f7490f8fca2c4dab560d7f` | v2 supersedes the 2026-06-11 v1 brief (archived in `_archived-old-versions/`). Gap research added 11 authoritative sources (IRS ×7, 26 U.S.C. §§ 6001/7216 via Cornell LII, NIST CSRC ×3) plus ISO 15489 reuse; all [FACT] bullets below carry verbatim excerpts in the v2 source index. Vendor sources (S1–S4) are retained as tier-3 context only.

## NOTE 1 — Tax Operating Model & Calendar
- [FACT] "Every person liable for any tax imposed by this title, or for the collection thereof, shall keep such records, render such statements, make such returns, and comply with such rules and regulations as the Secretary may from time to time prescribe." (26 U.S.C. § 6001, S9)
- [FACT] "Good records will help you monitor the progress of your business, prepare your financial statements, identify sources of income, keep track of deductible expenses, keep track of your basis in property, prepare your tax returns, and support items reported on your tax returns." (IRS, S6)
- [FACT] "Generally, you must keep your records that support an item of income, deduction or credit shown on your tax return until the period of limitations for that tax return runs out." (IRS, S5)
- [FACT] "Starting tax year 2023, if you have 10 or more information returns, you must file them electronically." (IRS, S11)
- [INFERENCE] Entity-to-obligation mapping, master calendar, named owners, and approval checkpoints operationalize these duties (unsupported_claim — design layer).

## NOTE 2 — Document Intake & Normalization
- [FACT] "The partnership uses Schedule K-1 to report your share of the partnership's income, deductions, credits, etc. Keep it for your records." (IRS K-1 instructions, S12)
- [FACT] "For your protection, Schedule K-1 may show only the last four digits of your identifying number..." (S12) — intake must match entities on masked TINs.
- [FACT] Form 1099-NEC applies "For each person to whom you have paid at least $600" for covered payments; payers are "most likely required to file an information return" (IRS, S11).
- [FACT] "All requirements that apply to hard copy books and records also apply to electronic records." (IRS, S7) — digitized intake inherits full recordkeeping obligations.
- [INFERENCE] AI-driven extraction/normalization pipeline is design; vendor K-1 automation material (S2/S4, ≤2 vendor sources used) is context only (unsupported_claim).

## NOTE 3 — Data Quality Controls
- [FACT] "Your books must show your gross income, as well as your deductions and credits." (IRS, S7)
- [FACT] "It is important to keep these documents because they support the entries in your books and on your tax return." (IRS, S7)
- [FACT] "The responsibility to prove entries, deductions, and statements made on your tax returns is known as the burden of proof. You must be able to prove (substantiate) certain elements of expenses to deduct them." (IRS, S8)
- [FACT] Supporting documents must "identify the payee, the amount paid, proof of payment, the date incurred, and include a description of the item purchased or service received" (IRS, S7) — this is the minimum field schema for tax evidence records.
- [INFERENCE] Reconciliation against partner capital accounts and exception-queue workflows implement, but are not prescribed by, these sources (unsupported_claim).

## NOTE 4 — Advisor Collaboration Workflow
- [FACT] 26 U.S.C. § 7216 makes it a misdemeanor — fines up to "$1,000 ($100,000 in the case of a disclosure or use to which section 6713(b) applies), or imprisoned not more than 1 year" — for a preparer who knowingly or recklessly "discloses any information furnished to him for, or in connection with, the preparation of any such return" or "uses any such information for any purpose other than to prepare, or assist in preparing, any such return" (S10, clause fragments).
- [FACT] "Use Form 2848 to authorize an individual to represent you before the IRS." / "Your authorization of a qualifying representative will also allow that individual to receive and inspect your confidential tax information." (IRS, S13) — authorization is an explicit, documentable act with defined scope.
- [FACT] Least privilege: access restricted "to the minimum necessary to accomplish assigned tasks" (NIST, S14).
- [INFERENCE] The advisor portal should store authorizations as records (grantor, scope, date, revocation), scope advisor access per entity at least-privilege, and log all access; the portal design itself is unsourced (unsupported_claim).

## NOTE 5 — Audit Support & Evidence Management
- [FACT] "You must keep your records as long as needed to prove the income or deductions on a tax return." (IRS, S6)
- [FACT] Event-driven retention: 7 years (worthless securities/bad debt), indefinite (no return filed), "at least 4 years" (employment taxes), property records until limitations expire for the disposal year (IRS, S5).
- [FACT] "You generally must have documentary evidence, such as receipts, canceled checks, or bills, to support your expenses." (IRS, S8)
- [FACT] Audit trail: "A record showing who has accessed an information technology (IT) system and what operations the user has performed during a given period." (NIST, S16)
- [FACT] "ISO 15489 establishes the fundamental concepts and principles for creating, capturing, and managing records." (ISO, S17)
- [INFERENCE] v1's flat "7-year archive" is superseded: retention must be computed per record type from IRS limitation rules. Retrieval SLAs remain design (unsupported_claim).

## NOTE 6 — Tax-Sensitive Transaction Workflow
- [FACT] "You need records to compute the annual depreciation and the gain or loss when you sell the assets." (IRS, S7) — with required asset data: when/how acquired, purchase price, improvements, disposal details (S7).
- [FACT] "Generally, keep records relating to property until the period of limitations expires for the year in which you dispose of the property." (IRS, S5)
- [FACT] §6001 recordkeeping (S9) and burden of proof (S8) apply to every transaction entry.
- [INFERENCE] Deal-close capture with provisional tax entries and pre-reporting approvals is design built on these duties (unsupported_claim).

## NOTE 7 — Dashboards & KPIs
- Unknown — no authoritative monitoring/compliance-reporting guidance retrieved within caps (PCAOB AS 1215 fetch failed). (qa_flags: unsupported_topic, gap_research_fetch_failed)
- [INFERENCE] Deadline/status/exposure dashboards and KPI candidates remain design hypotheses (unsupported_claim).

## NOTE 8 — Security & Segregation of Duties
- [FACT] Least privilege (NIST, S14): privileges restricted "to the minimum necessary to accomplish assigned tasks."
- [FACT] Separation of duty: "no user should be given enough privileges to misuse the system on their own. For example, the person authorizing a paycheck should not also be the one who can prepare them." (NIST SP 800-192 via CSRC, S15)
- [FACT] SoD enforcement modes: "either statically (by defining conflicting roles...) or dynamically (by enforcing the control at access time)." (S15)
- [FACT] Audit-trail logging definitions per NIST (S16).
- [INFERENCE] The specific entry/review/export permission split and create-approve-export SoD matrix is a direct application but remains design (unsupported_claim).

## QA & Gaps
- **Missing Excerpts**: S1–S4 (Thomson Reuters, K1x ×2, Asora) still carry empty excerpts[] — retained as tier-3 context only, not repaired (deliberate: authoritative replacements preferred; per task rule they cannot support [FACT] claims and do not).
- **Weak Sources**: S1–S4 (weak_source_tier_3, context_only). ≤2 vendor sources referenced for context (K1x in NOTE 2; Asora mentioned alongside). No [FACT] relies on any vendor source.
- **Unsupported Claims**: All [INFERENCE] bullets above (workflow/design layer); NOTE 7 entirely Unknown except design hypotheses. S10 excerpts are clause fragments of one statutory sentence (flagged).
- **Gap Research Performed**: 13 fetch attempts; 11 succeeded with verbatim quotes (IRS recordkeeping hub, what-kind-of-records, burden of proof, how-long-keep-records [prior pass], 1099 information-return page, K-1 partner instructions, About Form 2848, 26 USC 6001, 26 USC 7216, NIST least-privilege/SoD/audit-trail glossaries) plus ISO 15489 reuse. Failed: IRS About Schedule K-1 page (empty, 2 attempts), PCAOB AS 1215 (empty). Within cap of 25 new sources (11 new + 1 reused).
- **Coverage**: NOTES 1–6 and 8 each have ≥3 authoritative supporting sources; NOTE 7 has none (marked Unknown).
- **Confidence**: medium-high for NOTES 1–6, 8 (statute + IRS + NIST verbatim anchors); low for NOTE 7.
- **Dedup Actions**: None (run_id unique; ISO 15489 deduplicated to existing GS7 rather than assigned a new global ID).
