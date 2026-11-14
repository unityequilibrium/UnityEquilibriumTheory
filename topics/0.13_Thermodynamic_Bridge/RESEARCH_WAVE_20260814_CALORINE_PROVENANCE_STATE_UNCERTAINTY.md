### 2026-08-14 - Calorine provenance and state-uncertainty decomposition

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_CALORINE_ISOTOPE_MASS_SENSITIVITY and T13_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION.
WHAT_IS_ACTUALLY_CLOSED: Zenodo is recorded as the local byte source, GPUMD as the upstream NEP model origin, and record 7811021 as related but not the input source. NIST natural-carbon bounds were propagated through the mass-only C_src lane; the mesh numerical envelope and mass-only state envelope are reported separately.
WHAT_REMAINS_OPEN: Ding natural-graphite material/state equivalence, defect/morphology and isotope-scattering state, source-grade uncertainty, Ding C_src acceptance, alpha_Phi_K, UET bridge/beta, EOS/transport/KMS/entropy, and dimensional Phi mapping.
DEPENDENCY_UNLOCKED: Provenance and Calorine state-sensitivity lanes only; no full Topic 13 or downstream unlock.
STATUS: PASS_SCOPED_CALORINE_STATE_UNCERTAINTY_DECOMPOSITION; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE.
WHAT_CHANGED: Corrected NEP provenance metadata, regenerated the source package and candidate boundary, added mass-only isotope sensitivity and uncertainty decomposition audits, and synchronized the acceptance/full-gate/registry artifacts.
EQUATION_OR_MAPPING: epsilon_mesh = 0.0023908135; natural-composition mass envelope = 0.0000511973; pure-isotope values are stress bounds only. No Phi, alpha_Phi_K, or holdout mapping is inferred.
VERIFICATION: No fit, target tuning, alpha_Phi_K calibration, threshold adjustment, clipping, padding, or Xie 2026 holdout access occurred. Acceptance remains false.
CONTROLLING_BLOCKER: material_regime_mapping_to_TTG_not_closed; source-grade uncertainty is not inferred from the reported envelopes.
NEXT_ACTION: Source-lock defect/morphology state and response contract, or retain Calorine as a non-Ding comparator; then reassess independent C_src acceptance.
CLAIM_BOUNDARY: Candidate provenance and sensitivity decomposition only; not Ding validation, source-grade uncertainty closure, UET Phi calibration, TTG prediction, or Full Topic 13 closure.
EVIDENCE_HASHES: candidate 5e4e0d42d6e70612eabce988b86ab10b628dea14d4270bf2364ad58f572d014b; isotope 5db4a9487f728e5275906a1d4514c154b02cee4854fadcc0ea45f3ac6d5a0221; uncertainty 06eebd1f40afad38740fc490d89d1f9d631688595d59eeabbd70f49af61cdeff; acceptance 4caacfe498092bc98295e73d24de99fc9ca59133a895336ec623a8d6f4be3f17; full gate 720f26e7487508bb34777bc2c1d9fa4c8d8f40d9517ba174a9cf587befef35bf.
