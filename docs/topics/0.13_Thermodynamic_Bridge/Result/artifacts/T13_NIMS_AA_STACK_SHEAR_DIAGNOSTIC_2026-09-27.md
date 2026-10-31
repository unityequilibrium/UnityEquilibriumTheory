# NIMS MP-990448 Structural and Harmonic-Mode Diagnostic

MAJOR_RESULT_CLOSURE: T13_NIMS_MP990448_AA_STACK_SHEAR_MODE_DIAGNOSTIC is CLOSED_FOR_LANE for the deposited NIMS structure and declared harmonic calculation only.

WHAT_IS_ACTUALLY_CLOSED: The hash-locked NIMS YAML identifies a two-carbon-atom P6/mmm (No. 191) cell. Both basis atoms have fractional c-coordinate zero, so periodic copies repeat the same in-plane registry, an AA-like structural arrangement. At q=(0,0,1/2), a pair of basal-plane negative harmonic modes persists across five fixed force-constant/symmetrization variants. The negative-frequency spread is 3.0471838e-7 THz. Translation/permutation symmetrization reduces the acoustic sum-rule residual from 7.1092e-8 to 6.3158e-14 eV/angstrom^2 without removing the modes.

WHAT_REMAINS_OPEN: This idealized NIMS simulation is not shown equivalent to Ding's TTG specimen or stable ABAB hexagonal graphite. Electronic-structure, finite-temperature, and anharmonic uncertainties are not quantified. No Ding-compatible mode-resolved C_src, TTG response, SI Phi anchor, independent alpha_Phi_K, or physical transport/KMS/entropy package is produced.

DEPENDENCY_UNLOCKED: This NIMS result changes source-route classification only; it does not itself unlock a dependency. Separately, the registered O(2)/He-4 result T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY permits Core curved 3+1 work to proceed. That curved 3+1 parent remains PARTIAL, so Gravity is still blocked. MP-990448 remains a conditional harmonic comparator and is rejected as a Ding PBTE substitute.

STATUS: WARN_SCOPED_NIMS_AA_STACK_SHEAR_MODE_ROBUST_MATERIAL_MAPPING_OPEN. The aggregate Topic 13 gate remains BLOCKED_OPEN_T13_FULL_BRIDGE with seven open blocker groups.

WHAT_CHANGED: The earlier interpretation treated the negative branch mainly as an unresolved numerical issue. Reanalysis shows it persists after a large reduction of the acoustic sum-rule residual and under distinct force-constant methods. The data also show a structural mismatch: NIMS records C/P6/mmm, whereas IUPAC describes stable hexagonal graphite as ABAB-stacked P6_3/mmc (No. 194). This closes the question of whether MP-990448 should continue to be pursued as direct Ding/natural-graphite evidence: it should not.

EQUATION_OR_MAPPING: The standard harmonic eigenproblem is D(q)e_(q,nu)=omega_(q,nu)^2 e_(q,nu). The q=(0,0,1/2) phase alternates between adjacent c-periodic cells; basal-plane polarization is consistent with alternating-layer shear. This is not a UET equation or a Phi-to-temperature map.

VERIFICATION: The source archive SHA-256 is eea6ca7569c9442754ce5492ddb2f545186f97ad8b82b209d95f1a80b0158767; the nested YAML member SHA-256 is 92bfbcaa4cec51cbdf85c0d5d167bb8a57718e4d5074ac100378250257007a70. All 14 scientific/policy checks pass; non-promotion controls are separately false by design. The five-variant mode spread is below the fixed 1e-4 THz robustness threshold. Focused diagnostic tests pass 4/4; source-route, closure-track, dependency-unlock, and register-sync regressions pass. Xie 2026 was not accessed.

CONTROLLING_BLOCKER: The NIMS structure is not demonstrated equivalent to Ding/natural graphite. The aggregate Topic 13 controller remains dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing; Ding-compatible C_src and source-grade uncertainty remain separate open requirements.

NEXT_ACTION: Stop further unchanged repairs of the MP-990448 route. Prioritize an authorized Ding numeric package or a source-backed PBTE reproduction of the relevant ABAB graphite material/state with provenance, uncertainty, and convergence. If neither is available, keep the claim limited to normalized shape or conditional harmonic simulation.

CLAIM_BOUNDARY: This result does not establish that natural ABAB graphite is unstable, does not validate TTG, does not calibrate alpha_Phi_K, and does not close the physical thermodynamic bridge or global UET.

## Evidence

- Machine-readable artifact: [t13_nims_mp990448_aa_stack_shear_instability.json](../../../../core/07_artifacts/topic13/t13_nims_mp990448_aa_stack_shear_instability.json), SHA-256 6389321FDD634A6A9E36A228921BE1FD4A790B462D143998403454422F65434B.
- Reanalysis implementation: [Research_T13_NIMS_AA_Stack_Shear_Instability.py](../../Code/03_Research/Research_T13_NIMS_AA_Stack_Shear_Instability.py), SHA-256 95FAA276A5DD98351401BCB4B106299990D8AA001ABB87AEBDF4A52EDACADD22.
- Focused regression: [test_topic13_nims_aa_stack_shear_instability.py](../../../../core/05_tests/regression/root/test_topic13_nims_aa_stack_shear_instability.py), SHA-256 1D22F36A2CD763500237AC1CA8394063650D7E00472F650213DE13894D1DD82B.
- NIMS source record: [NIMS Materials Data Repository](https://mdr.nims.go.jp/datasets/5383108b-180d-4eb0-a34f-b28ff9e430d7).
- Symmetrization method: [Phonopy API](https://phonopy.github.io/phonopy/phonopy-module.html).
- Structural comparator: [IUPAC Gold Book, hexagonal graphite](https://goldbook.iupac.org/terms/view/H02818).
- Source-priority artifact: [t13_csrc_source_route_priority_audit.json](../../../../core/07_artifacts/topic13/t13_csrc_source_route_priority_audit.json), SHA-256 0562617FB4745E691543CBB6826CD83A1A82ED73056591C31B751497D70D804D; status PASS_SCOPED_C_SRC_SOURCE_ROUTE_PRIORITY_NO_ACCEPTED_ROUTE.
- Full Topic 13 gate remains BLOCKED_OPEN_T13_FULL_BRIDGE; its current controller is unchanged.
