# Topic 0.3 update log

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
