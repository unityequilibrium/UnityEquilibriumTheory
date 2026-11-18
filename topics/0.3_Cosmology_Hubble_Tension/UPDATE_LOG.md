# Topic 0.3 update log

## 2026-11-17 - Late-time G variation in the EMG branch

- Question: does the Lambda term that separates UET from EMG give a measurable G change today?
- Correction: the extra term is a positive mass +2 xi_c Lambda (about 0.83 H0^2), not tachyonic; UET drives psi less than EMG at late times.
- Estimate (xi = 0.2, psi_i = 0.4 M_pl, lambda ~ eV^4/M_pl^4): psi oscillates with period ~2.9 Gyr, delta G/G ~2.5e-9, Gdot/G ~5e-18 per yr, about 1,800 times below the LLR uncertainty. No UET-only signal here.

## 2026-11-17 - Parent action contains Early Modified Gravity

- Question: can the parent action change gravity before recombination enough to matter for the Hubble tension? Note: `Doc/ANALYSIS_PARENT_ACTION_EMG_2026-11-17.md`.
- Finding (sympy check in scratch: the Lagrangians differ only by -xi Lambda sigma^2, a stabilising mass +2 xi_c Lambda; first draft had the sign wrong): with m_psi ~ 0 and g_c ~ 0 the canonical action is the published EMG model (F = M_pl^2 + xi sigma^2, V = lambda sigma^4/4) with xi = xi_c.
- Numbers from Franco Abellan et al. 2023: xi sigma_i^2 = 0.033 +- 0.014, H0 = 68.9 (71.55 with SH0ES), tension 6 sigma to about 3 sigma; implied xi ~0.1-0.25, outside the T001-excluded 2.0-2.4.
- Not a UET prediction (fit values) and not UET-distinct. Next: sympy check of the mapping; constraint card for compatibility with T001 and Cassini.

## 2026-11-17 - Starlight trace versus expansion (H0)

- Question: can the trace written into existing light and heat (author items 7-8) change H0 or explain the Hubble tension? Note: `Doc/ANALYSIS_TRACE_AND_EXPANSION_2026-11-17.md`.
- New numbers: all starlight ever (COB 24.45 nW/m2/sr, Tompkins et al. 2025, plus CIB ~27 assumed) is 5.2 percent of CMB energy, Omega 2.8e-6, and 0.26 percent of CMB entropy; its effect on H0 is ~1.4e-6 against a tension of 8.4 percent.
- Result: the radiation trace cannot explain the Hubble tension (about 6e4 times too small). Not a UET failure; removes one candidate route.
- Next: bound how much the parent action (psi, xi_c) can change G at recombination.

## 2026-10-19 - W8 published-product scope adoption

- Changed: existing coverage contract now describes offline scalar-product analysis,
  identifies unchanged source-lock/Planck/SH0ES/CODATA input records, and pins the
  scientific code evidence to f7ba82307 rather than unrelated dirty producer work.
- Result: no raw HST reduction or spacecraft correction is claimed. Embedded scalar
  parity, covariance/likelihood adequacy and the physical beta-law justification
  remain open; existing internal benchmark thresholds/results are not changed.
- Verification: 58 contract/observer tests and workflow-YAML parse PASS; read-only
  contract/identity and changed-path checks. No source download, numeric run or fit.
- Next: review the source/uncertainty/model prerequisites before stronger cosmology
  claims; apply standards 30/32, not another blanket raw-instrument simulation.

## 2026-10-17 - Calculation/observation coverage review

- Changed: added the published-H0 calculation contract under calculation_contracts.
- Verified: shared schema/identity/component audit and synthetic observer controls.
- Result: INCOMPLETE; published Planck/SH0ES scalars remain summary inputs, not raw HST exposures. Upstream frame/time/correction lineage needs review.
- Claim boundary: no raw-data replication, new spacecraft correction or physical status promotion; no scientific result regenerated.
- Next: inspect source-product processing and error budget before stronger physical claims. Shared standard: ../For Work/30_Calculation_and_Observation_Completeness_Standard.md.
