# Topic 13 Closure Critical Path

MAJOR_RESULT_CLOSURE:
- `T13_CLOSURE_CRITICAL_PATH` is `CLOSED_FOR_LANE`.
- This closes the current research-control boundary, not the physical thermal bridge.

WHAT_IS_ACTUALLY_CLOSED:
- current 37-subresult closure state is reconstructed from canonical progress
- all open subresults are mapped to their complete required root input package sets, including multi-package dependencies
- current input hashes are recorded and rerunning existing gates without new input is explicitly non-progress
- normalized/action scale routes are structurally bounded by no-go evidence, not merely missing scripts

WHAT_REMAINS_OPEN:
- Open subresults: `10` of `37`.
- `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`
- `alpha_Phi_K_independent_calibration_missing`
- `normalized_beta_and_SI_scale_correspondence_missing`
- `physical_Kubo_coefficient_record_missing`
- `dimensional_phi_to_thermal_observable_map_missing`
- `material_regime_mapping_to_TTG_not_closed`
- `c_v_source_uncertainty_not_closed`

DEPENDENCY_UNLOCKED:
- none; reporting and replay guard only

STATUS:
- `PASS_T13_CLOSURE_CRITICAL_PATH_WITH_EXTERNAL_INPUTS`
- Full Topic 13: `BLOCKED_OPEN_T13_FULL_BRIDGE`
- Full Core unlock: `False`
- Claim promotion: `False`

WHAT_CHANGED:
- Reconstructed the canonical 37-subresult state and preserved each open row's complete required root input package set.
- Recorded the current evidence hashes and replay rule so an unchanged rerun is not counted as progress.

EQUATION_OR_MAPPING:
- `y_TTG = Delta_Tq(t)/Delta_Tq(0); y_TTG^UET = Delta_Phi(t)/Delta_Phi(0)`
- `Delta_Tq = alpha_Phi_K * Delta_Phi`
- `C_src(T)=sum_mu c_mu(T); Delta_Tq=Delta_u_ph/C_src(T)`
- `Phi_normalized=Phi_covariant/Phi_scale; u_SI=u_nat*E_ref^4/(hbar*c)^3`

CRITICAL_PATH:
| Root input package | Status | Canonical unlocks | Required by open rows | Accepted for Core |
|---|---|---:|---|
| `T13_INPUT_DING_TTG_SOURCE` | `BLOCKED` | 4 | 4 | `False` |
| `T13_INPUT_BASE_PHI_SI_ALPHA_BETA` | `BLOCKED` | 5 | 5 | `False` |
| `T13_INPUT_PHYSICAL_TRANSPORT_MATCH` | `BLOCKED` | 4 | 4 | `False` |

OPEN_SUBRESULTS:
| Subresult | Required input packages | Primary controller | Closure level | Status |
|---|---|---|---|---|
| `accepted_numeric_csrc` | `T13_INPUT_DING_TTG_SOURCE` | `T13_INPUT_DING_TTG_SOURCE` | `OPEN` | `OPEN` |
| `base_phi_si_anchor` | `T13_INPUT_BASE_PHI_SI_ALPHA_BETA` | `T13_INPUT_BASE_PHI_SI_ALPHA_BETA` | `OPEN` | `OPEN` |
| `independent_alpha_record` | `T13_INPUT_BASE_PHI_SI_ALPHA_BETA` | `T13_INPUT_BASE_PHI_SI_ALPHA_BETA` | `OPEN` | `OPEN` |
| `material_and_uncertainty_closure` | `T13_INPUT_DING_TTG_SOURCE` | `T13_INPUT_DING_TTG_SOURCE` | `OPEN` | `OPEN` |
| `normalized_beta_si_map` | `T13_INPUT_BASE_PHI_SI_ALPHA_BETA` | `T13_INPUT_BASE_PHI_SI_ALPHA_BETA` | `OPEN` | `OPEN` |
| `physical_entropy_production_mapping` | `T13_INPUT_PHYSICAL_TRANSPORT_MATCH` | `T13_INPUT_PHYSICAL_TRANSPORT_MATCH` | `OPEN` | `OPEN` |
| `physical_heat_flux_entropy_map` | `T13_INPUT_DING_TTG_SOURCE`, `T13_INPUT_BASE_PHI_SI_ALPHA_BETA`, `T13_INPUT_PHYSICAL_TRANSPORT_MATCH` | `MULTI_PACKAGE_DEPENDENCY` | `OPEN` | `OPEN` |
| `physical_sk_transport_match` | `T13_INPUT_PHYSICAL_TRANSPORT_MATCH` | `T13_INPUT_PHYSICAL_TRANSPORT_MATCH` | `OPEN` | `OPEN` |
| `physical_source_backed_eos` | `T13_INPUT_DING_TTG_SOURCE`, `T13_INPUT_BASE_PHI_SI_ALPHA_BETA` | `MULTI_PACKAGE_DEPENDENCY` | `OPEN` | `OPEN` |
| `physical_uet_kubo_record` | `T13_INPUT_PHYSICAL_TRANSPORT_MATCH` | `T13_INPUT_PHYSICAL_TRANSPORT_MATCH` | `OPEN` | `OPEN` |

VERIFICATION:
- Checks: `15/15` passed.
- Existing numeric gates must not be rerun as a substitute for changing an input package.
- Xie 2026 remains locked holdout; no target fit or calibration access is recorded.

CONTROLLING_BLOCKER:
- `external_input_package_state_unchanged`

NEXT_ACTION:
- Change one root package state by authorized Ding payload/reproduction, independent base-Phi SI anchor/alpha derivation, or physical Kubo match; then rerun dependent gates.

CLAIM_BOUNDARY:
- Does not close Full Topic 13 or claim physical SI, TTG, or transport validation.

UNBLOCK_ROUTES:
- `DING_AUTHOR_PAYLOAD`: authorized numeric Ding/PBTE payload with provenance, uncertainty, preprocessing, and hash.
- `DING_ACCEPTED_REPRODUCTION`: independent reproduction accepted against the declared Ding material/state and protocol.
- `BASE_PHI_DERIVATION`: dimensionful Phi-to-energy/temperature derivation with explicit SI anchor.
- `INDEPENDENT_ALPHA_RECORD`: independent alpha_Phi_K calibration record, uncertainty, locator, hash, and independence statement.
- `PHYSICAL_KUBO_MATCH`: physical finite-temperature transport/Kubo match with KMS and entropy contracts.
