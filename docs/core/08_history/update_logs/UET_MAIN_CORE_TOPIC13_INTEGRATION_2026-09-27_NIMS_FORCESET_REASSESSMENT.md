# Main Core Integration: Topic 13 NIMS Force-Set Reassessment (2026-09-27)

MAJOR_RESULT_CLOSURE: `T13_NIMS_MP990448_FORCE_DISPLACEMENT_REANALYSIS` is `CLOSED_FOR_LANE` for a conditional harmonic graphite comparator only. It is not a Core closure result.

WHAT_IS_ACTUALLY_CLOSED: The hash-locked NIMS archive contains two displacement-force records; the declared Phonopy workflows reconstruct finite harmonic force constants and produce unit-bearing `Cv`/volumetric candidates over three reciprocal-space meshes. This corrects the prior inference that lack of precomputed force constants prevented numeric harmonic reanalysis.

WHAT_REMAINS_OPEN: A negative-frequency branch remains near Gamma-A and is omitted by the explicit zero cutoff. Source-grade uncertainty, stable-phase acceptance, mapping to Ding's natural-graphite/TTG regime, an SI `Phi` anchor, independent `alpha_Phi_K`, and transport/KMS/entropy closure remain open.

DEPENDENCY_UNLOCKED: NIMS harmonic comparator lane only. No dependency gate, Core foundation result, Topic 13 full-bridge result, Gravity, Galaxy, or constitutive transport is unlocked.

STATUS: `WARN_SCOPED_NIMS_HARMONIC_CV_REANALYSIS_UNSTABLE_MODES_AND_UNCERTAINTY_OPEN`. The Topic 13 full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE`; `claim_promotion=false`.

WHAT_CHANGED: Added an integration note and Core README links to the Topic 13 report and machine-readable artifact. No equation registry, ontology, dependency edge, Core parent gate, or physical claim was changed. This lane-level result is documented and discoverable, but the central major-result register and MP-990448 source-priority projection have not yet been regenerated/hash-synchronized.

EQUATION_OR_MAPPING: `Cv_J_kg_K=Cv_J_mol_primitive_cell_K/M_mol,primitive` and `C_src_J_m3_K=Cv_J_mol_primitive_cell_K/V_mol,primitive` are standard harmonic comparator conversions. `Delta_Tq=alpha_Phi_K*Delta_Phi` remains uninstantiated; `C` and `Phi` ontology is unchanged.

VERIFICATION: Artifact `docs/core/07_artifacts/topic13/t13_nims_mp990448_force_displacement_reanalysis.json`, SHA-256 `7f9bcc88e1f32919392b7221836ebe2c8c90d008f3757b06cbe8bff3636e7ba8`; script SHA-256 `53d271a458e3cba425d13d315a8f1836285305e56403d5b6929bb75233db1171`. Archive/member SHA-256 values match their locked identities. Ten scoped checks and the focused regression suite pass 3/3. At 295.15 K and 12x12x6, the two calculators give `Cv=707.192/707.993 J kg^-1 K^-1` and `C_src=1.425779e6/1.427394e6 J m^-3 K^-1`; these are not measurement uncertainty bounds. Xie 2026 was not accessed.

CONTROLLING_BLOCKER: `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing` remains the Topic 13 full-gate blocker. Separately, central Core metadata still needs a controlled register/source-priority regeneration to include this new lane without treating it as Ding acceptance.

NEXT_ACTION: Regenerate the source-route priority projection, central major-result register, and dependent hashes in a separate scoped pass; keep the Full Topic 13 gate closed until Ding-compatible `C_src`, independent `alpha_Phi_K`, and physical bridge contracts are evidenced.

CLAIM_BOUNDARY: A reproducible external harmonic comparator only. No claim of stable graphite, Ding/TTG validation, UET thermal mechanism, Core closure, external validation, or global UET closure.
