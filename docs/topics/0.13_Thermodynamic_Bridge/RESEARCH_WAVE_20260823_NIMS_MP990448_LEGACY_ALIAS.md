# Topic 13 Research Sub-wave: NIMS MP-990448 Legacy Alias

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the legacy-route equivalence check of T13_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY.

WHAT_IS_ACTUALLY_CLOSED: The legacy phononDB mapping for material 990448 (wd3761563) was downloaded and its archive SHA-256 and byte size match the current NIMS MP-990448 archive. The legacy locator therefore does not expose a richer force-constant, frequency-mesh, or thermal-row payload.

WHAT_REMAINS_OPEN: Ding-compatible numeric C_src(T), source-grade uncertainty, material/state equivalence, base-Phi SI anchoring, independent alpha_Phi_K, and physical transport/KMS/entropy closure remain open.

DEPENDENCY_UNLOCKED: Legacy-route equivalence evidence only; no numeric C_src, alpha, transport, Core, Gravity, Galaxy, or external-validation unlock.

STATUS: PASS_SCOPED_NIMS_MP990448_PHONON_PAYLOAD_BOUNDARY; claim_promotion=false; holdout_accessed=false.

WHAT_CHANGED: Added a byte-identity check for the phononDB legacy locator, regenerated the NIMS source package and audit, and refreshed the full gate, major-result register, and dependency projection.

EQUATION_OR_MAPPING: The required source contract remains C_src(T) = sum_mu c_mu(T) in J m^-3 K^-1; the byte-identical legacy route adds no rows. Delta_Tq = alpha_Phi_K * Delta_Phi remains uncalibrated.

VERIFICATION: Current and legacy archives both hash to eea6ca7569c9442754ce5492ddb2f545186f97ad8b82b209d95f1a80b0158767 and are 133375 bytes. Focused NIMS regression passed 1/1; no figure digitization, fit, threshold change, synthetic replacement, or Xie 2026 access occurred.

CONTROLLING_BLOCKER: nims_mp990448_archive_lacks_machine_readable_force_constants_or_frequency_mesh is closed as a route boundary; the full-topic controllers remain ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing, alpha_Phi_K_independent_calibration_missing, and the other six full-gate groups.

NEXT_ACTION: Continue with an authorized Ding numeric package or accepted same-regime PBTE reproduction, plus an independent paired base-Phi/SI calibration record. Do not relabel this alias as numeric C_src.

CLAIM_BOUNDARY: This closes only legacy-route equivalence. It is not numeric C_src, Ding validation, an alpha calibration, a Phi-to-temperature prediction, physical UET transport, external validation, or Full Topic 13 closure.

EVIDENCE_PATHS:
- docs/scripts/audit/audit_topic13_nims_mp990448_phonon_source_boundary.py
- docs/core/test/test_topic13_nims_mp990448_phonon_source_boundary.py
- docs/core/artifacts/t13_nims_mp990448_phonon_source_boundary_audit.json
- docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/nims_mdr_mp990448_phonon_source_package.json
- docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json

EVIDENCE_HASHES: audit 2e9f93be5cf23c429d9d0b77f755efb074a44790483f0b635a62327d5025eda9; source package bbd4aee185a7c5a08b33f2f267e81a8b5274fa43b26eae1167966b4a5ec9a061; full gate 147e0c822d7a693abfce8c008cc87b48cd07eb2e4743288083c56e8b68660a86; register 0d2487bfd12523c2d6d738f06b3b391e0f4ab8dedf20998488231b50f26bb996; dependency fbf124a50ccf00d3a6d99295e69a890a3ef4671afc738c7ab13d94dc716dce19.
