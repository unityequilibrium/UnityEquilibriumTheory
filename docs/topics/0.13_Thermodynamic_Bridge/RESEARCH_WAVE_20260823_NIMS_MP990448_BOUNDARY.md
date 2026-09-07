# Topic 13 Research Wave: NIMS MP-990448 Payload Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY`.

WHAT_IS_ACTUALLY_CLOSED: The public NIMS MDR record for elemental C / P6/mmm (191), MP-990448, is source-locked with CC BY provenance, archive identity, and member hashes. The archive contains phonon figures, a compressed phonopy structural/displacement payload, and VASP settings, but no force-constant data, frequency mesh, or machine-readable thermal-property rows. The route is therefore closed as a payload boundary, not as numeric `C_src` evidence.

WHAT_REMAINS_OPEN: A Ding-compatible numeric `C_src(T)` source or accepted same-regime reproduction, source-grade uncertainty, material/state mapping, an independent base-`Phi` SI anchor, and `alpha_Phi_K` remain open. Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with eight blocker groups.

DEPENDENCY_UNLOCKED: NIMS MP-990448 source-payload boundary only. No `C_src`, alpha, thermal bridge, physical transport, Core, Gravity, Galaxy, or external-validation unlock.

STATUS: `PASS_SCOPED_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY`; `closure_level=CLOSED_FOR_LANE`; `claim_promotion=false`; `holdout_accessed=false`.

WHAT_CHANGED: Added the hash-locked NIMS MP-990448 archive and source package, audited nested phonopy/VASP payload members, projected the boundary into the Topic 13 full gate, and synchronized the closure register and dependency gate.

EQUATION_OR_MAPPING: Required source contract remains `C_src(T) = sum_mu c_mu(T)` in `J m^-3 K^-1`; `Delta_Tq = Delta_u_ph / C_src(T)` is not instantiated because the archive lacks machine-readable frequencies/thermal rows. `Delta_Tq = alpha_Phi_K * Delta_Phi` remains uncalibrated.

VERIFICATION: NIMS archive SHA-256 `eea6ca7569c9442754ce5492ddb2f545186f97ad8b82b209d95f1a80b0158767` and six-member inventory pass. Nested payload checks confirm no force constants, frequency mesh, or machine-readable thermal rows; `thermal_properties.png` is figure-only. Focused regression passed `5/5`; Xie 2026 was not accessed.

CONTROLLING_BLOCKER: `nims_mp990448_archive_lacks_machine_readable_force_constants_or_frequency_mesh` for this route; `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing` and `alpha_Phi_K_independent_calibration_missing` remain independent full-topic controllers.

NEXT_ACTION: Obtain an authorized Ding numeric package or permitted same-regime PBTE reproduction with mode-resolved `C_src(T)`, SI units, uncertainty, convergence, and material/state mapping. Do not digitize the NIMS figure or use this route for `alpha_Phi_K`.

CLAIM_BOUNDARY: This result is a source-payload boundary only. It is not a numeric `C_src` value, Ding validation, independent alpha calibration, TTG prediction, physical UET transport, Full Topic 13 closure, or global UET closure.

EVIDENCE_PATHS:
- `docs/scripts/audit/audit_topic13_nims_mp990448_phonon_source_boundary.py`
- `docs/core/test/test_topic13_nims_mp990448_phonon_source_boundary.py`
- `docs/core/artifacts/t13_nims_mp990448_phonon_source_boundary_audit.json`
- `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/nims_mdr_mp990448_phonon_source_package.json`
- `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/nims_mdr_mp990448_graphite_phonon_dataset.zip`
- `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`

EVIDENCE_HASHES: audit `af61412589e0c39fd5ca5f548e7870c718142579a581cc8853e9102de30a4571`; source package `79b6a25119b334a449686c9c5dcb356901390375bba71464c62dda338838b47d`; full gate `d5e6fb8bbd4cd96a2f06426b18be96f06079c846f2036fcfe58b124fc49ba27a`; matrix `74898242e258ad4ebbb8dc0584625ccd47b00336ff80c08fb7012155f7091fc7`; register `520b5b8f5780d526d72bc61364bf4b60cf21d27969baa62422e175ab309d7bf6`; dependency `3bbfc752fbe16ef82ec88d2a5cf552564d264cfd556c2746f893cdc404d01116`.
