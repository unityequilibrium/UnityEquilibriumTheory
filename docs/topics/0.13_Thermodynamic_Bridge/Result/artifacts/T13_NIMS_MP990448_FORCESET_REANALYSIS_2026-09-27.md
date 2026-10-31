# Topic 13 NIMS MP-990448 Force-Set Reanalysis

MAJOR_RESULT_CLOSURE: `T13_NIMS_MP990448_FORCE_DISPLACEMENT_REANALYSIS` is `CLOSED_FOR_LANE` for reproducible harmonic heat-capacity reanalysis only.

WHAT_IS_ACTUALLY_CLOSED: The hash-locked NIMS payload contains two displacement-force records. Phonopy reconstructs finite harmonic force constants using both its default and traditional calculators, and emits a conditional `Cv`/volumetric heat-capacity candidate over three q meshes. This supersedes only the earlier inference that the absence of precomputed force constants made numeric reanalysis impossible.

WHAT_REMAINS_OPEN: The reconstructed branch has negative frequencies near the Gamma-A direction; those modes are excluded by the declared zero cutoff, not repaired. Source-grade statistical/systematic uncertainty, stability of the declared harmonic structure, equivalence to Ding's natural-graphite/TTG regime, PBTE transport data, the SI scale of `Phi`, and independent `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: NIMS harmonic graphite comparator/reanalysis lane only. No Ding `C_src` acceptance, `alpha_Phi_K` calibration, physical UET transport, Core closure, Gravity, or Galaxy dependency is unlocked.

STATUS: `WARN_SCOPED_NIMS_HARMONIC_CV_REANALYSIS_UNSTABLE_MODES_AND_UNCERTAINTY_OPEN`; scoped source/reanalysis checks pass, while the physical-use boundary remains open.

WHAT_CHANGED: Reconstructed force constants from the deposited displacement-force rows, emitted a unit-bearing harmonic `Cv`/`C_src` candidate at 200, 295.15, and 300 K, compared default and traditional force-constant calculators, and recorded displacement row identities and normalized force-array hashes. No NIMS figure was digitized, no target curve was fitted, and Xie 2026 was not accessed.

EQUATION_OR_MAPPING: `Cv(T)=sum_(q,mu) k_B*x^2*exp(x)/(exp(x)-1)^2`, `x=hbar*omega_(q,mu)/(k_B*T)`; `Cv_J_kg_K=Cv_J_mol_primitive_cell_K/M_mol,primitive`; `C_src_J_m3_K=Cv_J_mol_primitive_cell_K/V_mol,primitive`. The UET relation `Delta_Tq=alpha_Phi_K*Delta_Phi` remains uninstantiated.

VERIFICATION: Reanalysis script SHA-256 `53d271a458e3cba425d13d315a8f1836285305e56403d5b6929bb75233db1171`; archive SHA-256 `eea6ca7569c9442754ce5492ddb2f545186f97ad8b82b209d95f1a80b0158767`; member SHA-256 `92bfbcaa4cec51cbdf85c0d5d167bb8a57718e4d5074ac100378250257007a70`; generated artifact SHA-256 `7f9bcc88e1f32919392b7221836ebe2c8c90d008f3757b06cbe8bff3636e7ba8`. All 10 scoped checks pass and focused status regressions pass 3/3. At 295.15 K and the 12x12x6 mesh, the two methods give `Cv=707.192` and `707.993 J kg^-1 K^-1`, and `C_src=1.425779e6` and `1.427394e6 J m^-3 K^-1`. The 10-to-12 mesh changes are 0.300% and 0.217%, respectively, but were not preregistered as an acceptance threshold. Minimum frequency is about `-0.766 THz`; 12/5184 and 10/5184 weighted modes are negative for the two methods. These values are conditional because the zero cutoff excludes negative frequencies and `pretend_real=false`.

The BIPM comparator reports `c_p=710.6 J kg^-1 K^-1` with `u_c=0.7` for its graphite sample near 22 C. The present result is harmonic `c_v` for an idealized NIMS structure; their numerical proximity is neither validation nor calibration.

CONTROLLING_BLOCKER: A Ding-compatible numeric `C_src` package or accepted same-regime reproduction with material/state mapping and source-grade uncertainty remains missing; independently, the physical `Phi`-to-temperature scale and `alpha_Phi_K` remain missing.

NEXT_ACTION: Keep this as a bounded harmonic comparator. If the lane is retained, resolve the negative-frequency branch and obtain source-grade uncertainty/material-state mapping; then regenerate the NIMS source-route priority projection and central major-result register. Do not use this result to calibrate `Phi` or close TTG transport.

CLAIM_BOUNDARY: Source-backed harmonic comparator only. It is not stable-phase acceptance, Ding-equivalent data, PBTE/TTG response, `alpha_Phi_K`, external validation, Full Topic 13 closure, or a global UET claim.

EVIDENCE_PATHS:
- `docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_NIMS_Force_Displacement_Reanalysis.py`
- `docs/core/05_tests/regression/root/test_topic13_nims_force_displacement_reanalysis.py`
- `docs/core/07_artifacts/topic13/t13_nims_mp990448_force_displacement_reanalysis.json`
- `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/nims_mdr_mp990448_graphite_phonon_dataset.zip`

SOURCE_LOCATORS:
- NIMS dataset: https://mdr.nims.go.jp/datasets/5383108b-180d-4eb0-a34f-b28ff9e430d7
- Phonopy API: https://phonopy.github.io/phonopy/phonopy-module.html
- Phonopy thermal-property settings: https://phonopy.github.io/phonopy/setting-tags.html
- BIPM graphite heat-capacity report: https://www.bipm.org/documents/20126/27085544/bipm%20publication-ID-1661.pdf/ecac54bb-1086-ac6c-46a3-6f986951a033?download=true&t=1598613830576&version=1.4
