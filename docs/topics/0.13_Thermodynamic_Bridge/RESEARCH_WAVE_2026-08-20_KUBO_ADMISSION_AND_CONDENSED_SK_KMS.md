# Research Wave 2026-08-20: Kubo Admission and Condensed SK/KMS Match

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_CONDENSED_RELATIVE_FLOW_KUBO_ADMISSION_LANE` and `T13_UET_O2_CONDENSED_SK_KMS_KUBO_MATCH_LANE`.

WHAT_IS_ACTUALLY_CLOSED: A machine-readable state-matched Kubo coefficient record now contains coefficient name, value, natural-unit declaration, hydrodynamic frame, `(T,mu,Phi)` state, correlator formula id, source path/hash, evidence status `KUBO_MATCHED`, and numerical uncertainty. The same state is lifted to a relative-projector SK/KMS/FDT interface with a lower-half-plane retarded pole, positive spectral matrix, KMS ratio, FDT noise identity, zero-frequency Kubo match, and nonnegative entropy witness.

WHAT_REMAINS_OPEN: This admission is for one declared condensed relative-flow contact channel. It is not a complete finite-temperature retarded 1PI self-energy, all-channel renormalization, complete condensed two-fluid tensor, SI transport coefficient, independent physical vertex anchor, dimensional `Phi` map, independent `alpha_Phi_K`, Ding-compatible `C_src`, or Full Topic 13 closure.

DEPENDENCY_UNLOCKED: Declared-channel Kubo admission and declared-channel SK/KMS/FDT interface only. `full_core_unlock=false`; the global physical-coefficient gate remains `BLOCKED_NOT_PROVIDED`.

STATUS: `PASS_KUBO_MATCHED_DECLARED_CONDENSED_RELATIVE_FLOW_CHANNEL` and `PASS_ACTION_DERIVED_CONDENSED_SK_KMS_KUBO_MATCH_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.

WHAT_CHANGED: Added the state-matched coefficient-record builder, Kubo admission audit/regression, condensed SK/KMS/Kubo response module, audit/regression, full-gate mappings, closure-register entries, dependency projections, and this wave record. Both audits use the same Phi-coupled condensed configuration as T13-114; no target residual, fitting, synthetic replacement data, or Xie 2026 holdout was used.

EQUATION_OR_MAPPING:

```text
K_rel^natural=lim_(omega->0) Re G_R^rel(omega)=D_rel/Gamma_rel
P_rel=((1,-1),(-1,1))
G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)*P_rel
rho=2*Im(G_R^rel)
G^>=rho*(1+n_B); G^<=rho*n_B
G^K=G^>+G^<=rho*coth(omega/(2*T))
```

VERIFICATION: Kubo admission audit has zero failed checks; coefficient `K_rel^natural=2.713283847206443e-05`; units are explicitly natural and not SI; numerical uncertainty is `3.500054507989025e-06`; evidence status is `KUBO_MATCHED`; source hash matches the loop module. SK/KMS audit has zero failed checks: KMS residual `0`, FDT residual `2.1815250606323664e-16`, retarded-reality residual `0`, spectral PSD minimum `0`, zero-frequency match residual `0`; focused tests for both new lanes are `4 passed`.

CONTROLLING_BLOCKER: `full_finite_temperature_retarded_1PI_self_energy_missing` and `independent_physical_condensed_vertex_anchor_missing`; at the full-bridge level, dimensional `Phi` energy anchor/independent calibration, non-circular bridge/beta, Ding `C_src`, and EOS/transport/KMS/entropy completion remain open.

NEXT_ACTION: Derive the finite-temperature condensed retarded self-energy and all-channel SK/KMS influence kernel, or source-lock an independent physical condensed vertex anchor. Keep the admitted coefficient scoped to the natural-unit channel and do not promote it to SI or Full Topic 13.

CLAIM_BOUNDARY: These are action-derived declared-channel Kubo/SK/KMS results. They are not external measurements, a complete interacting 1PI theory, SI thermal transport, `alpha_Phi_K` calibration, TTG prediction, external validation, or global UET closure.

EVIDENCE_HASHES:

- Kubo module `docs/core/uet_o2_condensed_relative_flow_kubo_admission.py`: `92dea65cf85d2fc2054e4f5c0b293712d2ea0b8b0df65ffa5e4b95de9dd2df67`
- Kubo audit `docs/core/07_artifacts/topic13/t13_uet_o2_condensed_relative_flow_kubo_admission_audit.json`: `5e909ff97aa0476619235460c012313f36b6065e642bbe4f7fba63f36bd8c7f6`
- SK/KMS module `docs/core/uet_o2_condensed_sk_kms_kubo_match.py`: `ab6fabaca6d2a19f8185535928638ecf4f1581cd2ad89ada78ed89e5341aff72`
- SK/KMS audit `docs/core/07_artifacts/topic13/t13_uet_o2_condensed_sk_kms_kubo_match_audit.json`: `d13d59760f9ebe0a3d2471ad984ec95c6729846d08b2b9ce011e2e8eb2fcaf1c`
- equation registry `docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json`: `ae143f9bd06738ae777415b46d39752c8fbb4a96b17f31de94eac3e563a7be44`
- full gate `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`: `4b69d2f13ef9827f11898edc63b254dd837943b3ccdf4b88f7fe52b2ea0d2415`
- closure register `docs/core/07_artifacts/gates/uet_major_result_closure_register.json`: `6d41189d970ba4b17bb889176412fc66ed4b9cbcd02a8520d014ddc61800ddb0`
- dependency gate `docs/core/07_artifacts/gates/uet_major_result_dependency_unlock_gate.json`: `83f6351dc2ccee0f3ba80a593c2081ca82e04d0b0b9d5b69ec9ad91754bfff1d`
