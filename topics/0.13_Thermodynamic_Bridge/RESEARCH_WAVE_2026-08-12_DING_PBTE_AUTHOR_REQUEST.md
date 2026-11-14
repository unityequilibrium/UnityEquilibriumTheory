# Topic 13 Research Wave: Ding PBTE Author Request

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The missing Ding PBTE acquisition route is now a bounded request package with explicit payloads, units, provenance, uncertainty/convergence requirements, acceptance tests, and a response-state machine.

WHAT_REMAINS_OPEN: The request has not been sent and no author payload has been received. Numeric `C_src(T)`, mode-resolved `c_mu(T)`, the `Phi`-to-energy map, `e0`, and independent `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: Source-acquisition readiness only. No numeric thermal input, Full Topic 13, Core curved 3+1, Gravity, or transport dependency is unlocked.

STATUS: `PASS_REQUEST_SCHEMA_OPEN_EXTERNAL_RESPONSE`

WHAT_CHANGED: Added `ding_2022_pbte_author_request_manifest.json`, based on the captured Ding 2022 OA inventory and supplementary formula record. The package requests only source-specific reproducibility inputs and does not request a fitted UET parameter.

EQUATION_OR_MAPPING:

```text
C_src(T) = sum_mu c_mu(T)
Delta_Tq = Delta_u_ph / C_src
Phi_E = Delta_u_ph / e0
```

VERIFICATION: The manifest requires source identity, locator, material state, units, row identity, preprocessing, uncertainty/convergence, hashes, permission terms, and an explicit holdout non-access statement. The current Ding OA inventory remains a scoped no-go for numeric payload; the request status is `NOT_SENT`.

CONTROLLING_BLOCKER: `author_data_or_independent_reproduction_payload_not_received`

NEXT_ACTION: If authorized by the project owner, send the prepared request to the corresponding-author route and record the sent date and message hash. Until a response arrives, continue only with independent derivation and lane-level audits; do not infer `C_src` from the normalized TTG curve.

CLAIM_BOUNDARY: This is not evidence that the request was sent or accepted. It is not a numeric source package, calibration, fit, prediction, external validation, or closure of Topic 13.

See the machine-readable controller at `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_pbte_author_request_manifest.json`.
