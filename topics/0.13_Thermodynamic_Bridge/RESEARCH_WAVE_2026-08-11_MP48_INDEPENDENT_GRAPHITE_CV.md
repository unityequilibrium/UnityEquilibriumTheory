# Topic 13 Research Wave: Independent Graphite Heat Capacity

MAJOR_RESULT_CLOSURE:
`T13_MP48_INDEPENDENT_GRAPHITE_CV_REPRODUCTION` is `CLOSED_FOR_LANE` after the deterministic source audit passes.

WHAT_IS_ACTUALLY_CLOSED:
- An authorized numeric harmonic phonon route for Materials Project `mp-48` graphite is archived with exact Zenodo archive/member locators.
- The extracted `FORCE_CONSTANTS`, structure, summary, DOS, and thermal-properties members have local byte counts and SHA-256 identities.
- Phonopy heat-capacity rows are treated as `J K^-1 mol^-1` of the primitive cell and converted with an independently sourced graphite volume anchor to representative volumetric `c_v` rows.
- `125 K` and `225 K` are explicitly linear interpolation rows; they are not additional source measurements.
- NIST-JANAF is comparison-only. Its `C_p` versus the harmonic source `C_v` supplies a conservative epistemic discrepancy envelope, not a statistical uncertainty and not a `C_p-C_v` correction.

WHAT_REMAINS_OPEN:
- This is not Ding 2022's mode-resolved PBTE `C_src(T)` and does not close Ding-specific convergence or uncertainty.
- The dimensional anchor `e0`, base `Phi -> Delta_u_ph` mapping, and independent `alpha_Phi_K` remain open.
- Temperature-resolved volume, material-grade/isotope matching to the TTG experiment, EOS, covariant transport, SK/KMS, entropy current, and dissipative balance remain open.

DEPENDENCY_UNLOCKED:
The independent harmonic `c_v` comparator route is available to Core as evidence. It does not unlock Gravity, full Topic 13, or holdout use.

STATUS:
`PASS_INDEPENDENT_NUMERIC_CV_WITH_EPISTEMIC_ENVELOPE` for this lane; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_CHANGED:
Added `mp48_independent_graphite_cv_source_package.json`, archived the exact extracted source members, and added `audit_topic13_mp48_independent_graphite_cv.py` with deterministic hash, schema, unit, conversion, interpolation, comparator, and holdout checks.

EQUATION_OR_MAPPING:
`C_v^vol(T) = C_v^mol,cell(T) / V_mol,cell`

`Delta_Tq = Delta_u / C_v^vol`

This remains a standard-material mapping. It does not assert `Phi = Delta_u` and does not infer `alpha_Phi_K`.

VERIFICATION:
Run `audit_topic13_mp48_independent_graphite_cv.py`. The audit must confirm all seven gzip member hashes, `mp-48` identity, the 10 K source grid, derived `c_v` rows, the JANAF comparison envelope, and that Xie 2026 was not accessed or consumed.

CONTROLLING_BLOCKER:
`base_Phi_to_Delta_u_ph_energy_anchor_and_independent_alpha_Phi_K_missing`

NEXT_ACTION:
Derive or source-lock `e0` and the base `Phi -> Delta_u_ph` correspondence independently of the TTG residual and locked Xie 2026 holdout. Then construct an uncertainty-bearing `alpha_Phi_K` record; if that cannot be derived or independently calibrated, retain `OPEN_CALIBRATION`.

CLAIM_BOUNDARY:
This wave closes only an independent harmonic graphite heat-capacity comparator lane. It is not a temperature prediction, not an `alpha_Phi_K` calibration, not external validation, and not global UET closure.
