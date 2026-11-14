# UPDATE LOG: 0.25 Strategy Power Economics

> **Scope:** `docs/topics/0.25_Strategy_Power_Economics`
> **Purpose:** Record auditable hardening waves for the economic diagnostic lane.

## Entries

### 2026-08-11 - Book 1 research reset and integrity repair

- Scope: Waves 0–4 containment, ontology/claim-map reset, and verifier-integrity repair; this does not implement the long-horizon evidence program.
- Added or changed: canonical Section/Book research controls, Book 1 eight-part Blueprint, controlled `Y/W/Kp/H/L/E/X/A/C/M/Cr/T/P/F` ontology, 15-wave register, 20 lane-scoped gates, Book–Topic alignment verifier, global-panel integrity gate, and focused regression tests.
- Formula boundary: `R=N+K+I` is `BOOK-HEURISTIC-001 / RETIRED_AS_IDENTITY`; `R/M` is a resource-coverage diagnostic, while purchasing power, FX, payment use, and real returns remain separate.
- Integrity repairs: rolling-origin RMSE is now true RMSE; median absolute error is separately named; coefficient/sign checks fit pre-holdout only; circular moving blocks are sampled with replacement using a recorded seed; producer scripts run before consumers.
- Verified with: Python compilation, 5 focused regression tests, Book/Topic alignment, global-panel rebuild, and the full aggregate verifier. The final run executed 37 commands with zero failures and returned `WARN`.
- Findings: the legacy resource proxy and Stone/resource-coverage proxy do not beat their declared baselines; measurement validity remains `WARN`. The frozen global panel has zero complete rows across GDP, PPP GDP, population, and energy, so six downstream artifacts are `INVALID_SUPERSEDED`.
- Blocker narrowed: version/ontology alignment is `PASS_WITH_BOUNDARY`; false global replication coverage is contained.
- Current controller: `SYSTEMATIC_LITERATURE_REVIEW_INCOMPLETE`; global replication separately remains blocked by `GLOBAL_COMPLETE_CASE_PANEL_UNAVAILABLE`.
- Claim impact: remains Claim Class C / `DESCRIPTIVE_DIAGNOSTIC_ONLY`; no law, fiat-causal, validated-peg, policy-success, or transaction-lineage claim is enabled.

### 2026-08-01 - SEC recipient funding concordance

- Scope: connect the frozen prime/subaward recipient names to public issuer accounting channels while preserving the distinction between firm accounts and award-dollar payment provenance.
- Added: `Research_UET_SEC_Recipient_Funding_Concordance.py`, official SEC company-ticker registry archive, exact-match/no-match concordance, current-vintage CIK Company Facts archives, normalized recipient/funding-channel CSVs, aggregate/readiness/join integration, and synchronized docs.
- Verified with: SEC API/cache run, py_compile, standalone join/readiness, complete aggregate verifier, and cross-artifact SHA-256 checks. Coverage is 1,285 unique names, 17 exact unique matches, 15 CIKs, and 235 annual fact rows; 1,268 names remain explicit no-match and no values are imputed.
- Finding: matched issuers expose annual net income, operating cash flow, capex, debt, dividends, and cash observations. These are descriptive firm-level accounting channels; exact identity does not show whether a government award dollar was paid from profit, borrowing, or cash, so `funding_share_identification` is `NOT_IDENTIFIED`.
- Blocker narrowed: public recipient accounting context is source-locked for the exact-match subset, but the controlling `firm_project_payment_ledger` blocker remains; payer-to-invoice-to-resource provenance is unavailable.
- Claim impact: Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged; no profit-vs-debt attribution, payment causality, money-creation, or resource-conversion claim is enabled.

### 2026-08-01 - Downstream subaward-recipient audit

- Scope: extend public award provenance from prime recipient/account fields to reported downstream subaward recipients and described work, without relabeling award reports as cash settlement.
- Added: `Research_UET_USASpending_Subaward_Downstream_Recipient_Audit.py`, ten count responses, all 32 subaward pages for the one positive-count award, empty-page responses for the other nine, normalized 3,168-row archive, source manifest, aggregate/readiness/join integration, and synchronized docs.
- Verified with: API/cache run, py_compile, standalone join/readiness, complete aggregate verifier, reported-count versus retrieved-row reconciliation, and cross-artifact SHA-256 checks. All ten awards are complete; one reports 3,168 subawards, producing 1,024 unique downstream recipients and 950 derived FY2024 rows.
- Finding: downstream recipient names, action dates, amounts, and descriptions are now observable for the reported subaward chain. They remain award-reporting observations, not bank settlement, invoice, payroll, profit, debt, money-creation, or physical-delivery proof.
- Blocker narrowed: public downstream-recipient visibility is source-locked for this nonrepresentative sample, but the controlling `firm_project_payment_ledger` blocker remains; payer-to-purchase-to-resource provenance is still unavailable.
- Claim impact: Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged; no financing-source, payment-causality, or resource-conversion claim is enabled.

### 2026-08-01 - Federal-account budget-resource audit

- Scope: extend the fixed award/account provenance chain to the federal account's budget authority, appropriations, obligations, outlays, and unobligated balance without treating budget data as a financing or cash-settlement trace.
- Added: `Research_UET_USASpending_Federal_Account_Budget_Resource_Audit.py`, cached profile/snapshot/TAS/program-activity responses, normalized two-account FY2024 panel, source manifest, aggregate/readiness/join integration, and synchronized docs.
- Verified with: official API cache run, py_compile, standalone join/readiness, complete aggregate verifier, and cross-artifact SHA-256 checks. Both observed accounts (`089-0240`, `089-0314`) have FY2024 snapshots; the rounded identity `budget_authority = obligated + unobligated` passes at `$0.01` tolerance.
- Finding: FY2024 budget authority is `$24.318B` for `089-0240` and `$1.886B` for `089-0314`; appropriations and other budgetary resources are separately reported. These are account-budget quantities, not proof of tax/debt/cash funding, profit funding, supplier payment, or physical-resource transformation.
- Blocker narrowed: federal-account budget context is now source-locked for the observed subset, but the controlling `firm_project_payment_ledger` blocker remains; payer-to-purchase-to-resource provenance is still unavailable.
- Claim impact: Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged; no financing-source, money-creation, payer causality, or resource-conversion claim is enabled.

### 2026-08-01 - Award federal-account linkage

- Scope: add a bounded reporting-account/program layer to the fixed public award sample so the audit distinguishes an award's federal account and funding agency from its ultimate financing source.
- Added: `Research_UET_USASpending_Award_Funding_Account_Audit.py`, ten cached `/api/v2/awards/funding/` responses, a normalized FY2024 account panel, source manifest, verifier/join/readiness integration, and synchronized docs.
- Verified with: API/cache rerun, py_compile, complete aggregate verifier, and cross-artifact SHA-256 checks. The source artifact is `WARN`: 4/10 awards return FY2024 funding rows and six awards are explicitly missing; the bounded join component is `PASS_WITH_BOUNDARY`.
- Finding: returned rows identify federal accounts `089-0240`/`089-0314`, the Department of Energy funding agency, and object-class/program fields. They do not identify tax receipts, debt instruments, bank settlement, supplier invoices, profit, or physical-resource transformation.
- Blocker narrowed: account/program provenance is now observable for a bounded subset, but the controlling `firm_project_payment_ledger` blocker remains; payer-to-purchase-to-resource provenance is still unavailable.
- Claim impact: Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged; no financing-source, money-creation, payer causality, or resource-conversion claim is enabled.

### 2026-08-01 - Award-level account outlay audit

- Scope: move one step closer to payment evidence by testing account-level outlay and obligation fields on individual public awards without relabeling them as bank payments.
- Added: `Research_UET_USASpending_Award_Level_Outlay_Audit.py`, ten cached USAspending award-detail responses, normalized award-level panel, source manifest, aggregate/readiness/join integration, and synchronized docs.
- Verified with: ten award-detail API refresh and cached rerun, py_compile, standalone join/readiness, aggregate verifier, and sub-artifact hash checks. Result is `PASS_WITH_BOUNDARY`; aggregate remains `WARN` with no command failures.
- Finding: all 10 fixed awards have account obligation and account outlay fields; the nonrepresentative sample median outlay/obligation ratio is `1.084`, with a large award dominating the total.
- Blocker narrowed: award-accounting fields are now observable, but they remain nonrepresentative and do not identify bank settlement, supplier invoices, financing source, or physical-resource transformation.
- Next controller: approved transaction/invoice settlement evidence and concordant resource allocation; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.
- Claim impact: no profit-vs-debt attribution, money-creation claim, payer causality, or payment-to-resource claim is enabled.


### 2026-08-01 - Award-to-outlay reconciliation

- Scope: test whether a public agency award obligation can be reconciled to a Treasury program outlay without calling the result a cash-payment match.
- Added: `Research_UET_Federal_Award_Outlay_Reconciliation.py`, a cached grouped USAspending DOE FY2024 response, normalized one-row comparison, source manifest, aggregate/readiness/join integration, and synchronized docs.
- Verified with: API refresh and cached rerun, py_compile, standalone join/readiness, aggregate verifier, and sub-artifact hash checks. Result is `PASS_WITH_BOUNDARY` / `NOT_ONE_TO_ONE`; aggregate remains `WARN` with no command failures.
- Finding: USAspending grouped award obligations are `$46.044B`; Treasury DOE FYTD net outlays are `$49.315B`; ratio is approximately `0.934`. The difference is a scope/timing/accounting diagnostic, not unpaid cash or a funding-source share.
- Blocker narrowed: the public evidence now distinguishes obligation scale from program outlay scale, but no award-to-bank settlement, private invoice, or resource transformation is observed.
- Next controller: approved transaction/invoice settlement evidence and concordant resource allocation; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.
- Claim impact: no profit-vs-debt attribution, money-creation claim, payer causality, or payment-to-resource claim is enabled.


### 2026-08-01 - Treasury aggregate funding-source lane

- Scope: distinguish government-wide receipts, outlays, deficit financing, and debt from the source of an individual award payment.
- Added: `Research_UET_Treasury_Funding_Source_Package.py`, six official Fiscal Data endpoint archives at record date `2024-09-30`, a 959-row normalized snapshot, aggregate/readiness/join integration, and synchronized docs.
- Verified with: official API refresh and cached rerun, py_compile, and source/hash checks. Treasury lane is `PASS_WITH_BOUNDARY`; the payer-resource join remains `BLOCKED` only on `firm_project_payment_ledger`.
- Blocker narrowed: aggregate government funding categories are now observable alongside public award obligations, but no tax/debt/cash source can be assigned to a specific award, invoice, or physical transformation.
- Next controller: approved transaction/invoice settlement evidence and concordant resource allocation; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.
- Claim impact: no profit-vs-debt attribution, money-creation claim, payer causality, or payment-to-resource claim is enabled.


### 2026-08-01 - Public federal award ledger lane

- Scope: add a source-locked public payer/recipient observation without treating federal award data as private settlement or financing-source proof.
- Added: `Research_UET_USASpending_Federal_Award_Ledger.py`, five cached USAspending.gov API response wrappers, a normalized 500-row DOE FY2024 contract-award sample, source manifest, and aggregate/join/readiness integration.
- Verified with: API refresh, cached rerun, py_compile, and source/hash checks. The public lane is `PASS_WITH_BOUNDARY`; the join remains `BLOCKED` only on `firm_project_payment_ledger`.
- Blocker narrowed: agency-to-recipient award obligations are now observable for a bounded public sample; cash settlement, private invoices/payroll, and tax/debt/money-creation financing remain unidentified.
- Next controller: obtain an approved project/invoice/payment ledger and concordant resource allocation; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.
- Claim impact: no payer causality, profit-vs-debt attribution, money-creation claim, or payment-to-resource claim is enabled.


### 2026-08-01 - BLS bounded labor coverage refresh

- Scope: narrow the labor-hours component of the payer-resource join without converting partial candidate coverage into a full industry panel.
- Added: targeted official BLS API windows for the 11 series already observed in the frozen archive, archived under retrieval vintage `2026-08-01` without mixing the prior `2026-07-16` directory; the normalized panel now has 418 rows and complete 1987-2024 coverage for those returned series. The join gate now records `candidate_set_complete=false`, `complete_series_count=11`, `no_imputation=true`, and a bounded labor status of `PASS_WITH_BOUNDARY` while the BLS source artifact remains `WARN`.
- Verified with: targeted BLS refresh, cached source-package rebuild, py_compile, and payer-resource join gate. Join result is `BLOCKED` with one controlling component: `firm_project_payment_ledger`.
- Blocker narrowed: labor observations are usable for a bounded returned-series diagnostic; the 202-code candidate universe and the payer/project transaction ledger remain unresolved. No funding-share or payer causality claim is enabled.
- Next controller: acquire the missing candidate-series coverage only through a compliant BLS archive/API route, then obtain approved transaction/project payment evidence; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.
- Claim impact: no upgrade; this wave changes join readiness only, not source grade or economic interpretation.


### 2026-07-16 - Labor, material, and public-firm funding provenance wave

- Scope: add observable inputs for the chain `funding -> industry use -> labor -> physical material`, while keeping payer/project provenance separate.
- Added: official BLS public-API industry-hours package, USGS cement/copper/gold quantity audit, SEC Company Facts proxy and funding-mix audit, and the explicit project payment ledger gate; integrated artifacts into the aggregate/readiness/join contracts.
- Verified with: py_compile, cached-source reruns, standalone BLS/USGS/SEC/project gates, payer-resource join, evidence-readiness, and aggregate verifier.
- Result: BLS `WARN` (11/202 predeclared NAICS4 candidates returned for 1987-2006; later API windows hit the provider daily quota); USGS `PASS_WITH_BOUNDARY` (3 commodities, 1,027 rows); SEC `PASS_WITH_BOUNDARY` (10 firms, 149 rows, 2010-2024); project ledger `BLOCKED`.
- Blocker narrowed: payer-resource join now has two controlling components, `labor_industry_hours` (provider quota-limited) and `firm_project_payment_ledger`; USGS is source-locked as a national quantity lane, not a completed common industry/project join. SEC funding ratios explicitly remain `NOT_IDENTIFIED` as shares.
- Next controller: obtain approved restricted-use or licensed transaction/project ledger and establish concordant industry/material allocation; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.
- Claim impact: no upgrade; no claim that profit, debt, or money paid for a specific resource transformation is permitted.


### 2026-07-16 - BEA 1997 benchmark structural audit

- Scope: close the structural industry/commodity-flow sub-check without pretending that a one-year benchmark supplies annual funding provenance.
- Added: `Research_UET_BEA_1997_IO_Benchmark_Audit.py`, the official BEA 1997 benchmark archives and source manifest, aggregate/readiness integration, and synchronized topic docs.
- Verified with: py_compile, standalone benchmark audit, payer-resource join gate, evidence-readiness artifact, and aggregate verifier; all verifier commands exited zero.
- Result: benchmark artifact `PASS_WITH_BOUNDARY`; 511 code-dictionary rows, 76,809 make/use rows, 73,766 direct-requirements rows, and 241,081 total-requirements rows pass finite-value, table-reference, year, and code-crosswalk checks.
- Blocker narrowed: payer-resource join remains `BLOCKED` with three controlling components: industry labor-hours, physical material quantities, and project payment ledger. The annual BLS/BEA flow lane remains separate and unavailable.
- Next controller: obtain source-locked labor/resource/project joins or explicitly quarantine the payer-level claim; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.
- Claim impact: no upgrade; no profit-vs-debt payer attribution, payment-level resource claim, resource causality, or innovation causality is permitted.

### 2026-07-16 - Payer-resource join readiness gate

- Scope: make the missing link from aggregate funding channels to actual industry, labor, and physical-resource use machine-readable.
- Added: `Research_UET_Payer_Resource_Join_Readiness.py`, aggregate/readiness integration, and synchronized topic docs/manifests/specification.
- Verified with: py_compile, standalone join gate, and aggregate verifier exit zero.
- Result: `BLOCKED` / `PAYER_RESOURCE_JOIN_NOT_IDENTIFIED`; funding flow and aggregate energy throughput are present, and the BEA code concordance now passes with boundary, while industry I-O, industry labor-hours, material quantities, and project payment ledger remain missing or blocked.
- Blocker narrowed: the package now distinguishes an available aggregate channel and a hashed industry crosswalk from a valid transaction-to-resource join; no imputation or hidden GDP substitution is allowed.
- Next controller: approved source-locked I-O archive plus labor/resource/project concordance; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.
- Claim impact: no upgrade; no funding-share, payer-level, resource-causality, or innovation-causality claim is permitted.

### 2026-07-16 - Fed Z.1 signed funding-mix audit

- Scope: distinguish descriptive net saving/debt/equity associations from a true funding-share claim.
- Wave type: artifact pass and claim-boundary pass.
- Added: `Research_UET_Fed_Z1_Funding_Mix_Audit.py`, aggregate/readiness integration, and signed-ratio definitions.
- Verified with: py_compile, standalone audit (66 complete rows, 1959-2024), and aggregate verifier exit zero.
- Result: `WARN` / `FUNDING_MIX_ASSOCIATION_DESCRIPTIVE_ONLY`; same-year and 0-2-year lead correlations plus payment-flow scale are reported.
- Blocker narrowed: the artifact now machine-reads `funding_share_identification.status = NOT_IDENTIFIED`; net debt/equity/saving flows cannot be summed as project funding shares.
- Still open: gross payment ledger, counterparty/project identity, BLS I-O replacement archive, and physical resource/labor concordance.
- Next controller: source-validated industry/commodity flow join; no fiat or profit-causality wording is permitted.
- Claim impact: no upgrade.

### 2026-07-16 - BLS input-output source and quality gate

- Scope: industry/commodity flow source needed to connect payer channels to labor and resource use.
- Wave type: source pass and access/quality gate pass.
- Added: `Research_UET_BLS_IO_Source_Gate.py`, aggregate-verifier/readiness integration, and the BLS source contract.
- Verified with: py_compile, official page metadata review, and aggregate verifier exit zero.
- Result: `BLOCKED` because the official automated endpoint returned Access Denied; the provider page also records a 2026-02-06 removal notice for matrix files with incorrect value-added percentages. No BLS matrix rows enter the primary evidence.
- Blocker narrowed: the required coverage is now explicit (1997-2024; production -> intermediate industry use -> final users), with a named approved-access and quality-validation requirement.
- Still open: obtain an approved official archive, hash it, inspect layout/units, and join it to EIA/USGS/FAOSTAT physical resource and BLS labor measures.
- Next controller: BLS I-O replacement archive and payer/resource concordance; Fed Z.1 remains the usable aggregate accounting lane.
- Claim impact: no upgrade; this gate is source readiness only.

### 2026-07-16 - Fed Z.1 sectoral funding mapping and accounting bridge

- Scope: payer/funding-source visibility for the Book 1 money-flow question.
- Wave type: source pass, artifact pass, and blocker-narrowing gate pass.
- Added: `Research_UET_Fed_Z1_Funding_Mapping_Probe.py`, its source/hash-linked artifact, and aggregate-verifier integration.
- Verified with: py_compile, standalone Fed Z.1 mapping probe, and `Verify_UET_Economics_Hardening.py` (exit zero).
- Result: `WARN` / `FUNDING_FLOW_MAPPING_DESCRIPTIVE_ONLY`; 66 complete annual rows (1959-2024) from `S11.1.i.a`; the capital-account identity residual is at most 1 million dollars from published rounding.
- Blocker narrowed: observed aggregate channels now separate labor payments, taxes, interest, dividends, internal saving, debt, equity transactions, and capital formation.
- Still open: counterparty/project-level payer provenance, historical-as-of revision vintages, and concordant labor/physical natural-resource extraction data.
- Next controller: payer/resource provenance join; energy-density remains the topic's separate concrete sub-lane blocker.
- Claim impact: no upgrade; sectoral accounting mapping is descriptive and does not identify which funding source paid for a particular investment or prove fiat causality.

### 2026-07-16 - Wave 3 cost-of-living and household-welfare lane

- Scope: U.S. household welfare separate from aggregate GDP.
- Added: welfare source package and audit for rent, owners equivalent rent, real median household
  income, and FHFA house-price index; archived source metadata/hashes under the external welfare
  manifest and embedded them into the aggregate artifact.
- Verified with: public source refresh, py_compile, standalone welfare audit, and aggregate
  verifier exit zero.
- Result: welfare lane PASS for 40 complete annual observations, 1985-2024 (requested start
  1984 was unavailable in the common intersection); no imputation was used. Aggregate remains
  WARN and Claim Class C.
- Claim impact: no upgrade; welfare pressure is descriptive and not evidence of policy or fiat
  causality.
- Next controller: expand distributional/regional coverage and keep revision/measurement gates
  explicit before any welfare generalization.


### 2026-07-16 - Wave 2 measurement-validity sensitivity

- Scope: frozen U.S. 1959-2024 R/N/K/I proxy construct.
- Added: Research_UET_Measurement_Validity_Audit.py and
  0_25_uet_measurement_validity_audit.json; compared three R families, three N families,
  two available K families plus an explicit missing patent family, and three I families.
- Verified with: py_compile, standalone measurement audit, and aggregate verifier exit zero.
- Result: WARN. R-family pairwise correlations were 0.8946-0.9864 and exceeded the declared
  0.8 diagnostic threshold, but coefficient signs were not stable across 54 combinations and
  USPTO/PatsView patents-per-capita data are absent. No imputation was used.
- Claim impact: no upgrade; R=N+K+I remains a heuristic proxy diagnostic and Claim Class C.
- Next controller: close WARN_MEASUREMENT with a predeclared third K family, reliability/error
  analysis, and invariance/structural-break checks.


### 2026-07-16 - Evidence Grade A roadmap, preregistration, and 12-gate architecture

- Scope: long-term hardening architecture for the U.S.-first to global economics evidence lane.
- Wave type: research-constitution, gate, claim-boundary, and documentation pass.
- Added: 10-wave research register; source-family and global-panel contract; variable dictionary;
  causal DAG; claim matrix; 12 machine-readable WARN gates; explicit Strategy/Power/Nash/Social
  Stabilization quarantine; roadmap, formula/data/verification documentation links.
- Verified with: JSON parsing for the new contracts; py_compile for the updated common/verifier
  modules; Verify_UET_Economics_Hardening.py (exit zero).
- Result: aggregate artifact remains WARN, controller DESCRIPTIVE_DIAGNOSTIC_ONLY, Claim Class C;
  source/panel/sub-audit execution remains complete, while architecture blockers include open
  measurement, revision, license, causal, external, publication, and related gates.
- Claim impact: no upgrade. Package Tier A is explicitly separated from the Evidence Grade A target.
- Next controller: close WARN_MEASUREMENT/WARN_UNIT and the source/revision/asset/energy lanes
  before attempting causal identification or global replication.


### 2026-07-16 - Optional-source semantics and legacy-claim quarantine

- Scope: source manifest semantics and whole-topic claim-boundary audit.
- Added or changed: optional missing exports now use `OPTIONAL_EXPORT_PENDING` rather than `MISSING_REQUIRED_EXPORT`; each source record now carries coverage and UTC retrieval timestamp; the panel enforces SHA-256 integrity; aggregate verifier now records `legacy_claim_quarantine`, panel/source-transform references, command failures, and a self-contained evidence bundle.
- Verified with: `Verify_UET_Economics_Hardening.py`; source readiness `PASS` (`15/15`), panel `PASS` (`66` rows), all commands exit zero, legacy quarantine `PASS` (`12/12` markdown files).
- Result: aggregate remains `WARN` only because `energy_density: WARN` is intentionally unresolved; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` are unchanged.
- Next controller: source-lock the 1776-1945 energy mix and common heat-content basis; optional LBMA/S&P total-return exports remain separate.

### 2026-07-15 - Source closure, unit correction, and execution-gate hardening

- Scope: U.S. historical Book 1 economics diagnostic lane.
- Wave type: source pass, artifact pass, formula/unit pass, and claim-boundary pass.
- Added or changed: BEA/EIA/EPI transform manifest and normalized subsets; truthful BEA quantity-index labels; median rolling-origin acceptance rule with two resource baselines; aggregate command-failure and panel-status gates; synchronized topic standards docs and code README.
- Files touched: `Code/03_Research/`, `Data/03_Research/`, `Result/artifacts/`, `README.md`, `METHOD.md`, `DATA_MANIFEST.md`, `FORMULA_AUDIT.md`, `BASELINE_COMPARISON.md`, `VERIFICATION_SPEC.md`, `LIMITATIONS.md`.
- Verified with: `.\.venv\Scripts\python.exe -m py_compile` for all hardening scripts; `Research_UET_Economics_External_Source_Transform.py`; `Research_UET_Economics_Source_Package.py --vintage 2026-07-12`; `Verify_UET_Economics_Hardening.py`.
- Result: source readiness `PASS` (`15/15`); panel `PASS` (`66` rows, `1959-2024`); all executed subcommands exit zero; aggregate artifact `WARN`.
- Blocker narrowed: the prior broad missing-source blocker is closed for the primary panel. The remaining machine-readable controller is `energy_density: WARN`; the asset lane is separately `BLOCKED` pending LBMA and licensed S&P total-return inputs.
- Still open: EIA 1776-1945 source-mix export, source-locked common heat-content basis, optional exact asset exports, external replication, and legacy working-copy provenance.
- Next controller: `energy_density_definition_gate` / `energy_density: WARN`.
- Claim impact: wording upgraded only to `Structured / Tier A` package readiness; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged. No economic-law, fiat-causality, policy, asset, or strategy claim was upgraded.
- Workflow linkage: this pilot follows the For_Work hardening sequence of source package, stable artifact, machine-readable blocker, documentation sync, update log, and scoped commit.
- Notes: the primary 3-year resource candidate signal is false; Stone mismatch does not beat the autoregression; EPI and BLS constructions are reported separately.

### 2026-07-12 - Book 1 historical economics source and gate package

- Scope: U.S. historical Book 1 economics diagnostic lane.
- Wave type: source pass and artifact/gate pass.
- Added or changed: source-lock manifest, readiness/parameter/holdout/formula/claim gates, seven research scripts, and aggregate verifier artifact.
- Files touched: `Code/03_Research/`, `Data/03_Research/`, `Result/artifacts/`, and topic standards docs.
- Verified with: `Research_UET_Economics_Source_Package.py --refresh --vintage 2026-07-12`; `Verify_UET_Economics_Hardening.py`.
- Result: `WARN`; 12 public FRED inputs were archived and hashed, while BEA fixed assets, EIA annual energy, and versioned EPI chart data remain missing.
- Blocker narrowed: broad Book 1 economics ambiguity is now a machine-readable three-source primary-panel gate; asset and literal-energy-density lanes have separate explicit gates.
- Still open: acquire and normalize the three required exports without substituting local convenience data.
- Next controller: `uet_us_historical_source_readiness` remains `WARN`.
- Claim impact: no change; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain controlling.
- Workflow linkage: follows the Topic 0.25 source-packaging and formula-audit hardening workflow.

### 2026-07-16 - Wave 4 money-credit-inflation diagnostic

- Scope: extend the Stone-in-the-Balloon lane from M2/resource mismatch to descriptive money, credit, velocity, debt-to-GDP-gap, and inflation diagnostics.
- Added: `Research_UET_Money_Credit_Inflation_Audit.py` and `0_25_money_credit_inflation_audit.json`; integrated both into the aggregate verifier.
- Verified: audit `PASS` with 64 annual observations; aggregate verifier `WARN`; all executed commands exit zero.
- Result: correlations and regressions are descriptive associations only; no monetary, fiat, fiscal, or policy causal claim is supported.
- Controller: energy-density definition remains the controlling blocker; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.

### 2026-07-16 - Wave 8 global replication readiness gate

- Added `Research_UET_Global_Replication_Readiness.py` and `0_25_global_replication_readiness.json`.
- Gate records the required World Bank, OECD, ILOSTAT, IMF, BIS, and WID provider roles plus 30-economy/20-year coverage and PPP-versus-exchange-rate policy.
- Result: `BLOCKED`; no global result is constructed until source vintages, hashes, common coverage, measurement invariance, and leave-one-out artifacts exist.
- Aggregate verifier rerun: `WARN`; Claim Class C and `DESCRIPTIVE_DIAGNOSTIC_ONLY` remain unchanged.

### 2026-07-16 - Wave 8 WDI source and panel pass

- Archived three World Bank WDI API responses (real GDP per capita, population, energy use per capita) with retrieval URL, timestamp, and SHA-256 manifest under the global raw-data cache.
- Normalized 4,699 complete country-year rows; 186 economies have at least 20 complete years across all three indicators. No imputation was used.
- Added `Research_UET_Global_WDI_Panel.py` and the panel artifact; this closes only the WDI sub-lane. OECD/ILOSTAT/IMF/BIS/WID source closure, PPP split, measurement invariance, and external replication remain blocked.
- Aggregate verifier remains `WARN / Claim C / DESCRIPTIVE_DIAGNOSTIC_ONLY`.

### 2026-07-16 - IMF CPI normalization and regional WDI hardening

- Added source-locked IMF DataMapper CPI archive and coverage artifact (228 economies; 222 with 20+ years).
- Added reproducible IMF ISO3 to WDI ISO2 normalization (147 matched economies with 20+ years) and integrated it into the aggregate verifier.
- Repaired WDI regional leave-one-out country join using ISO2 metadata, excluding aggregates; 162 countries joined and the regional script now runs in the aggregate chain.
- Current claim boundary remains descriptive; causal, universal, and Evidence Grade A promotion remain blocked.

### 2026-07-16 - Funding-source and money-flow proxy wave

- Archived FRED CPATAX, GPDI, BUSLOANS, and dividend-income series with a funding-source manifest.
- Added a 67-year no-imputation annual sectoral proxy panel and integrated it into the aggregate verifier.
- The panel distinguishes profit/investment and business-credit ratios but cannot identify individual payer funding provenance; transfers/equity and transaction-level links remain blocked.
- Aggregate remains `WARN / Claim Class C / DESCRIPTIVE_DIAGNOSTIC_ONLY`.

### 2026-07-16 - Funding proxy association audit

- Added a 62-observation complete-case audit of annual log changes in investment against corporate profits, business loans, and dividend income.
- Same-year correlations were approximately `0.549`, `0.086`, and `0.903` respectively; these are descriptive associations only and do not identify funding direction or payment provenance.
- Integrated the association artifact into the aggregate verifier; funding-flow provenance remains blocked.

### 2026-07-16 - Transfer receipts added to funding lane

- Added FRED/BEA Personal Current Transfer Receipts (`PCTR`) to the frozen funding-source proxy panel.
- Same-year transfer-receipt/investment-growth association was `-0.358`; one-year lag was `0.184`; two-year lag was `0.257`.
- These are descriptive co-movements, not evidence that transfers cause or fund investment; transaction-level provenance remains blocked.
