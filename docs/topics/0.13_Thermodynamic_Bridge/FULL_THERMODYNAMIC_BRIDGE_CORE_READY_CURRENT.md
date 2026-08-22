# Topic 0.13 Current Full-Bridge State

Machine-readable authority: `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`.

MAJOR_RESULT_CLOSURE: `PARTIAL`

WHAT_IS_ACTUALLY_CLOSED: Evidence-producing lanes remain closed only at their declared scope. The current wave closes the full-gate projection of `density_uncertainty_not_source_locked` through the source-locked IG-210 density rows and their k=2 bounds. The existing IG-210 volumetric `C_p` comparator remains lane-closed, while the causal no-go/named branch, Ding source boundaries, formal O(2)/SK/KMS/entropy interfaces, and graphite comparator/source boundaries remain lane-level results. This is not Full Topic 13 closure.

WHAT_REMAINS_OPEN: The current full-gate blockers are:
`ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`,
`alpha_Phi_K_independent_calibration_missing`,
`normalized_beta_and_SI_scale_correspondence_missing`,
`eos_transport_kms_entropy_completion_missing`,
`dimensional_phi_to_thermal_observable_map_missing`,
`physical_Kubo_coefficient_record_missing`,
`same_grade_alpha_V_and_K_T_missing`,
`material_regime_mapping_to_TTG_not_closed`, and
`c_v_source_uncertainty_not_closed`.

DEPENDENCY_UNLOCKED: The density uncertainty projection and IG-210 volumetric `C_p` comparator are lane-level only. No Core-ready, curved 3+1, Gravity/GR, full constitutive transport, Galaxy, external-validation, or global UET dependency is unlocked.

STATUS: `BLOCKED_OPEN_T13_FULL_BRIDGE`

WHAT_CHANGED: The full gate now records a machine-readable resolved-blocker entry linking `density_uncertainty_not_source_locked` to `T13_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE`, with three source rows and coverage factor k=2. The gate, register, and dependency projections were regenerated. No `C_v`, Ding `C_src`, `alpha_Phi_K`, fit, threshold change, or holdout access was introduced.

EQUATION_OR_MAPPING:
y_TTG = Delta_Tq(t) / Delta_Tq(0)
y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)
Delta_Tq = alpha_Phi_K * Delta_Phi
C_p^V = rho * C_p
C_v^V = C_p^V - T*alpha_V^2*K_T

VERIFICATION: The IG-210 source audit reports `density_uncertainty_locked=true` for the archived 500/700/1000 C rows with source-expanded relative density bounds of 0.003 at k=2. The volumetric `C_p` audit passed 14/14 checks; Topic 13 closure/regression checks passed 11 tests. Full gate summary is 180 closed lanes, 16 scoped no-go lanes, and 9 open blockers. `holdout_consumed=false` and `claim_promotion=false`.

CONTROLLING_BLOCKER: The nearest source controller remains Ding-compatible numeric `C_src` or an accepted independent reproduction, followed independently by the paired base-`Phi`/SI record for `alpha_Phi_K`. The IG-210 `C_p`-to-`C_v` route remains blocked by missing same-state `K_T` and material-regime mapping.

NEXT_ACTION: Acquire a permitted Ding numeric package or accepted same-regime PBTE reproduction with material/state, units, uncertainty, convergence, and hash. In parallel, seek an independent paired base-`Phi`/SI record; do not infer alpha from `C_p`, Landauer, normalized TTG, or the locked holdout. Then continue EOS, covariant transport, SK/KMS, entropy production, and dissipative-balance closure.

CLAIM_BOUNDARY: UET remains a candidate effective theory. `C` remains a collective coordinate, `Phi` an effective response, `R_gen` a derived history trace, and `R_obs` an observer record. No `C_v`, Ding `C_src`, numeric `alpha_Phi_K`, Kelvin prediction, physical transport coefficient, external validation, Full Topic 13 closure, or downstream unlock is claimed.

EVIDENCE: `docs/core/artifacts/t13_farooqui_ig210_thermophysical_source_audit.json` SHA-256 `1bf871b436166ba44243d6600fdfc06e9bbbf65a8fc23e2f99a728ff6402fb7e`; resolved full gate `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json` SHA-256 `f2f67384475fc8680476dee1b893dc1b32c9a90d8a1e348580789426536899d4`; register SHA-256 `7093fccfbb6e027df11429e51515dc3ddbabde3ecd27cbdce70a51fddf76bd69`; dependency SHA-256 `41303c1d38bc86c8c1f5008aafb515e05990f32acd74af1605ed371616f1ccd1`.
## 2026-08-22 - QH-15 Graphite Comparator Boundary (T13-152)

MAJOR_RESULT_CLOSURE: `T13_QH15_GRAPHITE_CV_COMPARATOR_BOUNDARY` is `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL` / `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_IS_ACTUALLY_CLOSED: The Materials Cloud QH-15 archive identity, selected raw entries, local hashes, source-notebook unit witness, natural-graphite `SpecificC` rows, explicit SI conversion, and a two-temperature equilibrium-scale cross-check against the independent Calorine candidate are machine-readable. The natural and isopure control rows remain separate.

WHAT_REMAINS_OPEN: QH-15 does not provide Ding mode-resolved `C_src`, a Ding TTG response-contract match, source-grade uncertainty, a material-regime equivalence proof, or an independent `alpha_Phi_K` calibration. The full gate still has 10 open blockers.

DEPENDENCY_UNLOCKED: Comparator/source classification only. No Full Topic 13, Core, curved 3+1, Gravity, constitutive transport, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_QH15_CV_COMPARATOR_BOUNDARY`.

WHAT_CHANGED: Added the QH-15 source package, archived selected raw entries, unit-conversion verifier, focused regression, full-gate lane integration, and major-result/dependency synchronization. No fit, calibration, threshold change, synthetic replacement, or Xie 2026 holdout access occurred.

EQUATION_OR_MAPPING:

```text
C_v^QH15[J m^-3 K^-1] = SpecificC[pg/(um ns^2 K)] * 1.0e9
r_T = (C_v^QH15 - C_src^Calorine) / C_src^Calorine
```

VERIFICATION: QH-15 natural rows and isopure-control rows match the archived hashes and 20-column schema. At 200 K the relative difference to the Calorine latest mesh is `-0.682889%`; at 300 K it is `+0.014257%`. The comparison is source-separated and non-fitting; it is not a Ding acceptance test. The full gate is `176` closed lanes, `16` scoped no-go lanes, `10` open blockers, and downstream unlock `false`; the new coupling no-go remains lane-only.

CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`; `alpha_Phi_K_independent_calibration_missing` remains independently open.

NEXT_ACTION: Keep QH-15 as comparator evidence while obtaining an authorized Ding numeric package or accepted same-regime PBTE reproduction with uncertainty and response mapping; separately obtain an independent base-Phi/SI record for `alpha_Phi_K`.

CLAIM_BOUNDARY: QH-15 is not Ding `C_src`, not a Phi-to-temperature prediction, not an `alpha_Phi_K` calibration, not external validation, and not Full Topic 13 closure. `C`, `Phi`, `R_gen`, and `R_obs` meanings are unchanged.

EVIDENCE: `docs/core/artifacts/t13_qh15_graphite_transport_boundary_audit.json`; `docs/scripts/audit/audit_topic13_qh15_graphite_transport_boundary.py`; `docs/core/test/test_topic13_qh15_graphite_transport_boundary.py`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`.

## 2026-08-11 Causal Branch Selection Update

MAJOR_RESULT_CLOSURE: `T13_CAUSAL_THERMAL_BRANCH_SELECTION` is `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The original conserved-gradient baseline is a scoped high-k no-go, while the named coupled conserved-flux/C-Phi branch passes the locked compact-support, arrival, ledger, convergence, and anti-manipulation gates.

WHAT_REMAINS_OPEN: The selected causal branch is normalized; the SI `Phi` scale, source package, `alpha_Phi_K`, bridge, EOS, transport, SK/KMS, entropy, and balance requirements remain open.

DEPENDENCY_UNLOCKED: Normalized causal input only; no full Topic 13 or downstream Core dependency.

STATUS: `PASS_CLOSED_AS_NO_GO_WITH_NAMED_COUPLED_BRANCH` for branch selection; Full Topic 13 remains `PARTIAL/BLOCKED`.

WHAT_CHANGED: Linked the baseline no-go and the passing named branches as one major-result record and removed the obsolete standalone-flux note that said coupled integration was still pending.

EQUATION_OR_MAPPING: `C_t + partial_x J_C = 0`; `tau_C J_C_t + J_C = -M_C partial_x(mu_C)`; `tau_Phi Phi_tt + Phi_t + M_Phi mu_Phi = 0` in the named normalized branch.

VERIFICATION: The original baseline remains above `1e-6`; the selected coupled lane has zero measured pre-arrival leakage, nonzero arrivals, energy residual below `1e-6`, no clipping, no cone padding, no parameter fit, and no Xie 2026 access.

CONTROLLING_BLOCKER: `selected_causal_branch_is_normalized_and_dimensional_thermal_bridge_remains_open`.

NEXT_ACTION: Independently close the dimensional and thermodynamic bridge without relabeling the failed baseline.

CLAIM_BOUNDARY: No SI thermal mapping, external validation, covariant completion, or global closure follows from the named branch.

## Base-Phi Calibration Controller

MAJOR_RESULT_CLOSURE: `OPEN`

WHAT_IS_ACTUALLY_CLOSED: The admissible independent calibration route is now a
machine-readable acceptance contract with required provenance, units,
uncertainty, row identity, and holdout restrictions.

WHAT_REMAINS_OPEN: No paired base-`Phi` amplitude and SI observable record is
available. The named `Phi_E` reference lane remains separate from base `Phi`.

DEPENDENCY_UNLOCKED: None. Full Topic 13, Core curved 3+1, and Gravity remain
blocked by this and the remaining thermodynamic closure gates.

STATUS: `OPEN_INDEPENDENT_BASE_PHI_CALIBRATION_REQUIRED`

WHAT_CHANGED: `docs/core/artifacts/t13_base_phi_independent_calibration_requirement.json` is linked into the full gate, major-result
register, dependency gate, and formula audit.

EQUATION_OR_MAPPING:

```text
Phi_E = Delta_u / e0
Phi_E = s_material * Phi_base
alpha_Phi_K = (e0 / c_v) * s_material
Delta_Tq = alpha_Phi_K * Delta_Phi
rho_model = N_C M_C / (N_A V_primitive)
c_v,implied = C_src / rho_model_base
```

VERIFICATION: The contract audit passes its required-field and forbidden-input
checks. No source rows, TTG residuals, numeric target curve, parameter fit, or
Xie 2026 holdout was consumed.

CONTROLLING_BLOCKER: `independent_paired_base_Phi_amplitude_and_SI_observable_record_missing`

NEXT_ACTION: Obtain a permitted independent paired base-`Phi`/SI record or a
derived base-`Phi` to `Phi_E` map, then run the preregistered calibration without
post-inspection tuning.

CLAIM_BOUNDARY: This is a protocol result, not a calibration result. It emits
no numerical `alpha_Phi_K`, prediction, external validation, or full Topic 13
closure.

## Formal SK/KMS and Entropy Interface

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: Topic 13 now has a named local SK response/noise
interface, KMS relation, entropy-current form, Onsager positivity witness, and
exchange-current balance that does not give `R_gen` backreaction.

WHAT_REMAINS_OPEN: Physical Kubo coefficient provenance, finite-temperature
normal component, curved 3+1 transport, base-Phi SI normalization, and external
transport validation remain open.

DEPENDENCY_UNLOCKED: Formal lane only. No full transport, Full Topic 13, Core,
Gravity, or external-claim dependency is unlocked.

STATUS: `PASS_NAMED_SK_KMS_ENTROPY_INTERFACE_CONTRACT`

WHAT_CHANGED: `docs/core/artifacts/t13_sk_kms_entropy_contract_audit.json` and `docs/core/thermal_sk_kms_entropy_contract.py` were added and linked into the
full gate, major-result register, dependency gate, formula audit, and update log.

EQUATION_OR_MAPPING:

```text
S_SK = integral [Phi_a D_R Phi_r + i Phi_a N Phi_a/2]
N(omega) = coth(beta_th omega/2) * 2 Im D_R(omega)
J_S^mu = s u^mu + q^mu/T
nabla_mu T_matter^(mu nu) = Q^nu
nabla_mu T_UET^(mu nu) = -Q^nu
```

VERIFICATION: The KMS noise witness is nonnegative for a positive retarded
spectral term, and the declared Onsager witness is symmetric positive
semidefinite. No source rows, fit, target, Xie 2026 holdout, or numeric physical
transport coefficient was used.

CONTROLLING_BLOCKER: `physical_Kubo_coefficient_provenance_missing`

NEXT_ACTION: Source-lock or microscopically match state-specific Kubo
coefficients, complete finite-temperature and curved transport, and keep this
formal witness separate from physical validation.

CLAIM_BOUNDARY: This is a formal candidate interface, not microscopic SK/KMS
matching, physical entropy-production validation, SI Phi calibration, or global
UET closure.

## Ding PBTE Author-Request Controller

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A bounded corresponding-author request package now
lists the missing Ding PBTE payload, units, row identity, provenance,
uncertainty/convergence, hashes, permission terms, and acceptance tests.

WHAT_REMAINS_OPEN: The request is `REQUEST_PACKAGE_READY_NOT_SENT`. No author
payload, numeric `C_src(T)`, mode-resolved `c_mu(T)`, `e0`, base-`Phi` energy
map, or `alpha_Phi_K` has been received or emitted.

DEPENDENCY_UNLOCKED: Source-acquisition readiness only. Full Topic 13, Core
curved 3+1, Gravity, and transport remain blocked.

STATUS: `PASS_REQUEST_SCHEMA_OPEN_EXTERNAL_RESPONSE`

WHAT_CHANGED: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/ding_2022_pbte_author_request_manifest.json` and `docs/core/artifacts/t13_ding_pbte_author_request_audit.json` are linked to the full gate,
energy bridge, register, dependency gate, formula audit, and update log.

EQUATION_OR_MAPPING:

```text
C_src(T) = sum_mu c_mu(T)
Delta_Tq = Delta_u_ph / C_src
Phi_E = Delta_u_ph / e0
```

VERIFICATION: The local OA package remains a scoped no-go for numeric Ding
inputs. The request audit passes all schema, provenance, unit, and holdout
checks; `sent=false`, `response_received=false`, and no target curve was used.

CONTROLLING_BLOCKER: `author_data_or_independent_reproduction_payload_not_received`

NEXT_ACTION: If the project owner authorizes external contact, send the prepared
request and record the sent-message hash. On response, hash and audit every
file before accepting any numeric `C_src` row.

CLAIM_BOUNDARY: This is a request specification, not a sent request, source
package, calibration, fit, prediction, external validation, or Full Topic 13
closure.

## Physical Kubo Coefficient Provenance Controller

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The required state-matched Kubo coefficient record
fields and evidence statuses are now machine-readable, and all existing
external transport records are classified as readiness/structure sources only.

WHAT_REMAINS_OPEN: No accepted physical coefficient record is present. The
transport verifier remains `physical_coefficient_evidence=BLOCKED_NOT_PROVIDED`;
finite-temperature normal response and curved 3+1 transport remain open.

DEPENDENCY_UNLOCKED: Kubo coefficient acceptance gate only. Full Topic 13 and
downstream Core/Gravity dependencies remain blocked.

STATUS: `PASS_KUBO_PROVENANCE_GATE_OPEN_PHYSICAL_COEFFICIENT`

WHAT_CHANGED: `docs/core/artifacts/t13_physical_kubo_coefficient_provenance_audit.json` is linked into the Topic 13 transport gate,
major-result register, dependency gate, formula audit, report, and update log.

EQUATION_OR_MAPPING:

```text
KuboCoefficientRecord -> constitutive coefficient
```

VERIFICATION: Required value/unit/state/correlator/hash fields are checked;
synthetic controls are not promoted; no numeric coefficient, target curve, or
Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.

CONTROLLING_BLOCKER: `physical_Kubo_coefficient_record_missing`

NEXT_ACTION: Acquire or microscopically derive one accepted state-matched
coefficient record, then rerun the transport verifier.

CLAIM_BOUNDARY: This closes a provenance gate only. It is not a physical
transport result, Kubo match, finite-temperature completion, alpha calibration,
or Full Topic 13 closure.

## Standard Graphite Transport Comparator

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A conditional, source-backed graphite comparator at
`573.15 K` is reproducible from the archived row. The reconstructed
`k = 74.0939625200673 W m^-1 K^-1`; source-reported and first-order propagated
uncertainty envelopes are both retained and explicitly separated.

WHAT_REMAINS_OPEN: Density uncertainty, the `c_p` to `c_v` regime correction,
UET `Phi` transport, Ding `C_src`, and the base-Phi SI anchor remain open.

DEPENDENCY_UNLOCKED: Standard-material comparator lane only. No Full Topic 13,
Core curved 3+1, Gravity, or constitutive transport dependency is unlocked.

STATUS: `PASS_STANDARD_GRAPHITE_TRANSPORT_COMPARATOR_CONDITIONAL`

WHAT_CHANGED: `docs/core/artifacts/t13_gatech_standard_transport_comparator_audit.json` and its source/hash evidence are linked into the
Topic 13 full gate, major-result register, dependency gate, formula audit, and
current-state report.

EQUATION_OR_MAPPING:

```text
c_p^vol = c_p^mass * rho_assumed
k = D * c_p^vol
sigma_k(source-reported) != forced_equal_to sigma_k(first-order propagated)
```

VERIFICATION: Source row identity, unit conversions, raw hash, reconstructed
conductivity, finite uncertainty envelopes, synthetic-control separation, and
no-holdout/no-alpha-fit policy all pass.

CONTROLLING_BLOCKER: `standard_comparator_is_not_a_UET_Phi_transport_coefficient_or_Ding_C_src`

NEXT_ACTION: Acquire a state-matched physical Kubo coefficient and an
independent base-Phi SI anchor; do not relabel this standard comparator as UET
transport evidence.

CLAIM_BOUNDARY: This is a conditional standard-material comparator only. It is
not Ding PBTE `C_src`, not UET constitutive transport, not `alpha_Phi_K`, not a
TTG prediction, and not external validation.

## Covariant Transport Implementation Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The current implementation is explicitly bounded to a
natural-unit Landau-frame `T=0` pure-superfluid ideal sector plus a minimal
longitudinal Kubo interface. Ideal covariance, entropy positivity, causal
control, and missing-provenance blocking are verified.

WHAT_REMAINS_OPEN: No physical Kubo coefficient is supplied. The finite-
temperature normal component, full transport tensor, SI lane, and curved 3+1
solver are not implemented.

DEPENDENCY_UNLOCKED: Implementation-boundary result only. No physical transport,
Full Topic 13, Core curved 3+1, or Gravity dependency is unlocked.

STATUS: `PASS_CLOSED_TRANSPORT_IMPLEMENTATION_BOUNDARY`

WHAT_CHANGED: `docs/core/artifacts/t13_covariant_transport_implementation_boundary_audit.json` hashes the transport implementation, contract,
verification artifact, and tests, then links the boundary into the full gate,
register, dependency gate, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
P = P(X, Phi)
N^mu = (Z*q/lambda) xi^mu
T^mu_nu = f_s xi^mu xi^nu + p g^mu_nu
KuboCoefficientRecord -> coefficient only when matched evidence passes
sigma = X_A L^(AB) X_B >= 0
```

VERIFICATION: Source markers and tests confirm T=0 rejection, no-default
coefficient admission, natural-unit/SI boundary, synthetic-control opt-in,
trace isolation, ideal covariance, entropy sign, causal speed, and blocked
physical provenance.

CONTROLLING_BLOCKER: `physical_Kubo_coefficient_record_missing`

NEXT_ACTION: Acquire one state-matched physical Kubo coefficient and derive the
finite-temperature normal sector and SI Phi observable map independently.

CLAIM_BOUNDARY: This is an implementation-scope result only. It is not a
microscopic Kubo match, finite-temperature two-fluid derivation, SI transport
result, external validation, or Full Topic 13 closure.

## Standard Finite-Temperature O(2) Normal Comparator

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A deterministic standard finite-temperature complex-
scalar normal-branch comparator is implemented using the declared UET
`m_eff(Phi)` as an input. Pressure, charge density, entropy density, energy
density, susceptibility, charge symmetry, and pressure-derivative identities
pass in the natural-unit comparator domain.

WHAT_REMAINS_OPEN: This does not derive a finite-temperature UET effective
action, condensate/normal two-fluid sector, physical Kubo coefficient, SI
`Phi` map, or `alpha_Phi_K`.

DEPENDENCY_UNLOCKED: Standard thermodynamic comparator lane only. Full Topic 13,
Core, Gravity, and physical constitutive transport remain blocked.

STATUS: `PASS_STANDARD_O2_FINITE_T_NORMAL_COMPARATOR`

WHAT_CHANGED: `docs/core/artifacts/t13_standard_o2_finite_temperature_comparator_audit.json` and its module/EOS hashes are linked into the full
Topic 13 gate, major-result register, dependency gate, formula audit, report,
update log, and work ledger.

EQUATION_OR_MAPPING:

```text
E_k = sqrt(k^2 + m_eff(Phi)^2)
p_T = T integral [L(E_k-mu) + L(E_k+mu)] d^3k/(2 pi)^3
n_T = partial p_T / partial mu
s_T = partial p_T / partial T
epsilon_T = -p_T + T*s_T + mu*n_T
```

VERIFICATION: Normal-branch domain, positivity, even/odd charge symmetry,
finite-difference pressure derivatives, and separation from `C`, `R_gen`,
`R_obs`, `alpha_Phi_K`, Kubo, and SI lanes pass. No target, holdout, or fit is
used.

CONTROLLING_BLOCKER: `finite_temperature_UET_effective_action_and_normal_two_fluid_sector_not_derived`

NEXT_ACTION: Derive or source-lock the finite-temperature UET action and normal
sector, then match physical Kubo coefficients and the SI Phi observable map.

CLAIM_BOUNDARY: Standard QFT comparator only. Not a finite-temperature UET EOS,
not a two-fluid derivation, not physical transport, not `alpha_Phi_K`, and not
external validation.

## Action-Derived O(2) One-Loop Normal Branch

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The thermal one-loop determinant on the homogeneous
normal background `A=0` is derived from the declared action mass map
`m_eff(Phi)`. The response derivative, charge/temperature derivatives,
positivity, and energy identity pass in natural units.

WHAT_REMAINS_OPEN: Vacuum counterterm/renormalization and interacting thermal
self-energy are not closed. The condensate/Goldstone/normal two-fluid sector,
physical Kubo coefficient, SK/KMS matching, SI Phi map, and `alpha_Phi_K` remain
open.

DEPENDENCY_UNLOCKED: Action-derived normal-background lane only. No full finite-
temperature UET EOS, physical transport, Full Topic 13, Core, or Gravity unlock.

STATUS: `PASS_ACTION_DERIVED_ONE_LOOP_NORMAL_LANE`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_one_loop_normal_branch_audit.json` and hashes of the action, mass map, and one-loop
implementation are linked into the full gate, register, dependency gate,
formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
E_k = sqrt(k^2 + m_eff(Phi)^2)
Omega_N^(1,T) = T integral log[(1-exp(-(E_k-mu)/T))(1-exp(-(E_k+mu)/T))] d^3k/(2 pi)^3
partial p_N/partial Phi = -(partial m_eff^2/partial Phi) * 1/2 integral[(n_-+n_+)/E_k] d^3k/(2 pi)^3
```

VERIFICATION: Action mass derivative, pressure derivatives with respect to Phi,
mu, and T, positivity, energy identity, normal-domain condition, and explicit
vacuum/condensate/two-fluid exclusion all pass. No fit, target, holdout,
physical Kubo value, or SI alpha is used.

CONTROLLING_BLOCKER: `vacuum_counterterm_and_interacting_finite_temperature_UET_completion_not_closed`

NEXT_ACTION: Close or explicitly bound the vacuum/renormalization layer, then
derive the condensate/two-fluid sector and match physical Kubo/SI Phi
observables.

CLAIM_BOUNDARY: This is an action-derived thermal normal-background lane only.
It is not a renormalized full finite-temperature UET action, two-fluid
derivation, physical transport, SI calibration, external validation, or Full
Topic 13 closure.

## One-Loop Normal Branch Convergence

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The action-derived thermal-only one-loop normal branch
has a reproducible numerical plateau. The locked reference is
`cutoff_factor=70`, `quadrature_order=256`; the maximum plateau drift across
cutoffs `30,40,50,70,100` and orders `96,128,192,256` is below `1e-8` for all
declared outputs.

WHAT_REMAINS_OPEN: The convergence result does not close vacuum counterterms,
renormalization, interacting thermal self-energy, condensate/two-fluid physics,
Kubo transport, SK/KMS matching, SI Phi mapping, or `alpha_Phi_K`.

DEPENDENCY_UNLOCKED: Numerical stability of the action-derived normal branch
only. No physical thermal, transport, Full Topic 13, Core, or Gravity unlock.

STATUS: `PASS_ACTION_DERIVED_ONE_LOOP_CONVERGENCE`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_one_loop_convergence_audit.json` adds explicit cutoff/order sweeps and is linked into
the full gate, register, dependency gate, formula audit, report, update log,
and ledger.

EQUATION_OR_MAPPING:

```text
cutoff = 70 * max(T, m_eff, |mu|)
quadrature_order = 256
max relative plateau drift <= 1e-8
```

VERIFICATION: Plateau max drift is `7.634e-11`;
cutoff-tail drift is `5.930e-14`;
order drift is `4.942e-14`.
Low-order high-cutoff cases are excluded from the reference. No target,
holdout, alpha fit, or synthetic replacement is used.

CONTROLLING_BLOCKER: `vacuum_counterterm_and_renormalized_one_loop_response_not_closed`

NEXT_ACTION: Close or explicitly bound the one-loop vacuum/renormalization
layer, then derive the interacting finite-temperature and condensate/two-fluid
sectors before physical transport matching.

CLAIM_BOUNDARY: Numerical convergence of the declared thermal-only integral
only. Not a renormalization proof, physical transport result, SI calibration,
external validation, or Full Topic 13 closure.

## One-Loop Thermal UV Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The thermal-only one-loop normal branch has an explicit
UV scope boundary. Its Bose-log and occupation tails are analytically bounded
above on the declared normal branch, and the omitted vacuum/zero-point term is
separately recorded as a divergent, not-yet-renormalized contribution.

WHAT_REMAINS_OPEN: No vacuum counterterm, renormalized one-loop response,
interacting finite-temperature self-energy, condensate/two-fluid completion,
physical Kubo coefficient, SI Phi map, or `alpha_Phi_K` is supplied.

DEPENDENCY_UNLOCKED: Thermal-only UV scope control and a machine-readable
renormalization blocker. No physical transport, Full Topic 13, Core, or Gravity
dependency is unlocked.

STATUS: `PASS_THERMAL_UV_BOUNDARY`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_one_loop_uv_boundary_audit.json` records the thermal tail bounds, vacuum cutoff-growth
boundary, source hashes, explicit exclusion policy, and holdout contract; this
sync links it into the full gate, register, dependency gate, formula audit,
update log, and ledger.

EQUATION_OR_MAPPING:

```text
-log(1-exp(-x)) <= exp(-x)/(1-exp(-x))
n_B(x) <= exp(-x)/(1-exp(-x))
I_0(Lambda) >= Lambda^4/(8 pi^2)
I_1(Lambda) >= (Lambda^2 - m_eff^2)/(4 sqrt(2) pi^2)
```

VERIFICATION: The maximum thermal-tail bound relative to the declared
reference outputs is `9.031e-56`;
the convergence, branch, ontology, and holdout checks pass. The vacuum term is
not included and no renormalized action is claimed.

CONTROLLING_BLOCKER: `vacuum_counterterm_and_renormalized_one_loop_response_not_closed`; the independent base-Phi SI anchor and
`alpha_Phi_K` remain the Full Topic 13 controller.

NEXT_ACTION: Acquire or derive a source-backed vacuum renormalization contract
without inventing counterterms, while separately pursuing physical Kubo and
independent base-Phi calibration evidence.

CLAIM_BOUNDARY: This closes only the thermal-only UV scope and blocker boundary.
It is not a renormalization proof, physical transport result, SI calibration,
external validation, or Full Topic 13 closure.

## T=0 Condensate and Goldstone Ideal Lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The declared natural-unit O(2) action closes a
tree-level condensed branch at `T=0`: stationarity, amplitude, pressure, signed
Noether charge, susceptibility, sound speed, canonical Legendre relation,
Josephson phase relation, covariant ideal current/stress, and the tree-level
Goldstone frequency relation are verified together.

WHAT_REMAINS_OPEN: The finite-temperature normal component, interacting
self-energy, two-fluid completion, physical Kubo coefficient, SK/KMS physical
matching, SI `Phi` map, `alpha_Phi_K`, vacuum renormalization, and curved 3+1
remain open. Synthetic Kubo values were used only as a simulation control.

DEPENDENCY_UNLOCKED: T=0 tree-level condensate/Goldstone ideal lane only. No
physical transport, Full Topic 13, Core, or Gravity dependency is unlocked.

STATUS: `PASS_T0_CONDENSATE_GOLDSTONE_IDEAL_LANE`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_condensate_goldstone_ideal_lane_audit.json` verifies and records the existing EOS, covariant
Noether current, ideal stress, Josephson, and Goldstone interfaces, then this
sync links the result into the full gate, register, dependency gate, formula
audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
q = Z*mu^2 - m_eff(Phi)^2 > 0
A^2 = q/lambda
p = q^2/(4*lambda)
N^mu = (Z*q/lambda)*xi^mu
T^mu nu = f_s*xi^mu*xi^nu + p*g^mu nu
omega_G = +-c_s*k
```

VERIFICATION: The condensed branch, stationarity, thermodynamic derivatives,
Noether conservation, Josephson relation, current/stress mapping, Goldstone
frequency, finite-temperature rejection boundary, ontology separation, and
holdout policy all pass. No physical coefficient, target fit, or Xie 2026
numeric data is used.

CONTROLLING_BLOCKER: `finite_temperature_normal_component_and_physical_Kubo_coefficient_missing` for this lane; the Full Topic 13 controller
remains the independent dimensional `Phi`/SI anchor or `alpha_Phi_K`.

NEXT_ACTION: Derive or source-lock the finite-temperature normal sector and
state-matched physical Kubo coefficients without turning the synthetic control
into data; keep the SI Phi and renormalization blockers explicit.

CLAIM_BOUNDARY: This is a natural-unit tree-level T=0 ideal lane. It is not a
finite-temperature two-fluid derivation, physical transport validation,
renormalized one-loop theory, SI calibration, external validation, or Full
Topic 13 closure.

## T=0 Condensate Fluctuation Spectrum

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: At fixed `Phi`, the declared O(2) action gives a
tree-level quadratic radial/phase determinant around the condensed background.
Both roots are non-negative over the declared wavenumber sweep, the
zero-momentum low root is Goldstone, the determinant residual is at most
`7.105e-15`, and the low-k slope agrees with
the independent EOS sound speed.

WHAT_REMAINS_OPEN: Finite-temperature self-energy, normal component, dissipative
transport, physical Kubo coefficients, vacuum renormalization, SI `Phi` map,
`alpha_Phi_K`, and external validation remain open.

DEPENDENCY_UNLOCKED: Fixed-Phi natural-unit T=0 spectrum only. No finite-
temperature normal, physical transport, Full Topic 13, Core, or Gravity unlock.

STATUS: `PASS_T0_QUADRATIC_FLUCTUATION_SPECTRUM`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_condensate_fluctuation_spectrum_audit.json` and `docs/core/uet_o2_condensate_fluctuations.py` add and verify the fixed-Phi
quadratic determinant; this sync links the result into the full gate, register,
dependency gate, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
det M = (omega^2-k^2)(omega^2-k^2-2q/Z) - 4*mu^2*omega^2
omega_+-^2 = k^2 + q/Z + 2*mu^2
               +- sqrt((q/Z + 2*mu^2)^2 + 4*mu^2*k^2)
lim(k->0) omega_-^2/k^2 = c_s^2
```

VERIFICATION: Determinant residual max is `7.105e-15`;
low-k Goldstone slope is `0.274560` versus
EOS `c_s^2=0.274419`. `Phi` is held fixed;
no target, holdout, alpha fit, or physical Kubo value is used.

CONTROLLING_BLOCKER: `finite_temperature_normal_component_and_interacting_self_energy_not_derived`; Full Topic 13 still controls on the independent
dimensional `Phi`/SI anchor or `alpha_Phi_K`.

NEXT_ACTION: Match this boundary to a declared finite-temperature effective
action without inventing self-energy terms, then acquire state-matched physical
Kubo evidence and independent base-Phi calibration.

CLAIM_BOUNDARY: This is a fixed-Phi natural-unit T=0 tree-level spectrum. It is
not a finite-temperature two-fluid theory, renormalized loop result, physical
transport validation, SI calibration, external validation, or Full Topic 13
closure.

## O(2) Normal-Lane Thermodynamic Consistency

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The action-derived one-loop normal branch is internally
consistent across a deterministic grid: pressure derivatives recover charge,
entropy, and the Phi response derivative; cross-derivative reciprocity and
Gibbs-Duhem identities pass; positivity and the normal-domain condition pass.

WHAT_REMAINS_OPEN: Vacuum renormalization, interacting finite-temperature
self-energy, condensate/Goldstone/normal two-fluid completion, physical Kubo
coefficients, SK/KMS microscopic matching, the SI Phi map, and `alpha_Phi_K`
remain open.

DEPENDENCY_UNLOCKED: Normal-lane thermodynamic consistency only. No physical
EOS, transport, SI, Full Topic 13, Core, or Gravity dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_NORMAL_THERMODYNAMIC_CONSISTENCY`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_normal_thermodynamic_consistency_audit.json` evaluates the declared normal determinant over
8 state points with fixed quadrature/cutoff policy,
finite-difference derivative checks, Maxwell reciprocity, positivity, and
Gibbs-Duhem identities. The result is linked into the full gate, register,
dependency gate, formula audit, update log, and ledger.

EQUATION_OR_MAPPING:

```text
n = partial_mu p
s = partial_T p
epsilon = -p + T*s + mu*n
partial_Phi n = partial_mu(partial_Phi p)
partial_Phi s = partial_T(partial_Phi p)
```

VERIFICATION: Maximum derivative error is `3.632e-09`;
maximum Maxwell error is `1.589e-11`;
and all declared positivity, branch, ontology, and holdout checks pass. No
parameter fitting, target curve, Xie 2026 data, alpha, or SI coefficient was
used.

CONTROLLING_BLOCKER: `vacuum_counterterm_and_renormalized_one_loop_response_not_closed` for this derived lane;
the Full Topic 13 controller remains `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`.

NEXT_ACTION: Keep this lane fixed as an internal consistency baseline; close
the vacuum/interaction and condensate/two-fluid sectors, then obtain physical
Kubo evidence and an independent base-Phi SI anchor.

CLAIM_BOUNDARY: This is not a renormalized finite-temperature UET theory, a
physical transport result, an SI calibration, external validation, or Full
Topic 13 closure.

## Berut Source Package Availability Boundary (2026-08-12)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The Berut working copies in the current checkout are
classified as topic-derived summaries, not raw experimental rows. The captured
publisher surface is recorded as a Figure 3/PPT acquisition route, while the
absence of a local raw or separately exposed source-data package is explicit.

WHAT_REMAINS_OPEN: The official Figure 3 binary/hash, selected panel and axis
mapping, numeric transcription, row identity, preprocessing, and uncertainty
package remain open. No Berut numeric row is eligible for calibration.

DEPENDENCY_UNLOCKED: Berut source-acquisition decision only. No Full Topic 13,
Core, Gravity, or constitutive-transport dependency is unlocked.

STATUS: `PASS_SCOPED_BERUT_SOURCE_PACKAGE_BOUNDARY`

WHAT_CHANGED: `docs/core/artifacts/t13_berut_source_package_availability_boundary.json` records the source identity, publisher locator,
current local inventory, source-surface scope, and non-calibration policy.

EQUATION_OR_MAPPING: `E_min = k_B T ln(2)` remains an imported standard
constraint. No numeric `Delta_Tq = alpha_Phi_K * Delta_Phi
rho_model = N_C M_C / (N_A V_primitive)
c_v,implied = C_src / rho_model` mapping is emitted.

VERIFICATION: All source identity, summary-role, no-raw-file, surface-scope,
holdout, no-fit, and no-calibration checks pass; accepted numeric rows emitted:
`0`.

CONTROLLING_BLOCKER: `berut_local_raw_or_permissioned_numeric_package_missing`

NEXT_ACTION: Archive the official Figure 3 PPT or an explicitly permitted numeric/supplement package, then select one panel and record axis ticks, selected points/curve, row identity, uncertainty, preprocessing, and SHA-256 before any source-normalized use.

CLAIM_BOUNDARY: This is a provenance and acquisition boundary, not a closed
Berut numeric row, uncertainty result, `alpha_Phi_K`, UET bridge, or external
validation.

## Berut Figure 3 Remote Binary Identity

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE

WHAT_IS_ACTUALLY_CLOSED: The official publisher Figure 3 route was
download-tested. Its remote binary identity is pinned by SHA-256, byte size,
OLE signature, retrieval date, and an explicit four-asset raster inventory.

WHAT_REMAINS_OPEN: No raster is accepted as a numeric row yet. Selected panel,
axis ticks and units, point or curve selection, digitization uncertainty,
preprocessing, and row identity remain open.

DEPENDENCY_UNLOCKED: Berut figure-acquisition route only. No numeric source,
alpha_Phi_K, Full Topic 13, Core, Gravity, or transport dependency is unlocked.

STATUS: PASS_REMOTE_FIGURE3_BINARY_IDENTITY

WHAT_CHANGED: docs/core/artifacts/t13_berut_figure3_remote_binary_identity.json records the official article/download locators,
binary hash e4bab6be849a093b7578bc52ce6df9be95dc25d83d51ecb718b4f798a37d50fa, size
479744 bytes, and embedded raster inventory.
The binary itself remains outside the repository.

EQUATION_OR_MAPPING: Figure 3 is a source-surface asset for the Berut
heat-versus-erasure-duration observable; no numeric Delta_Tq or alpha_Phi_K
mapping is emitted.

VERIFICATION: Binary identity and asset inventory checks pass; accepted numeric
rows emitted: 0; no fit, target data, calibration, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.

CONTROLLING_BLOCKER: berut_selected_panel_and_axis_tick_mapping_missing

NEXT_ACTION: Select one quantitative panel, record axis ticks and units, map selected points or curve with declared digitization uncertainty, and archive row identity and preprocessing before source-normalized use.

CLAIM_BOUNDARY: Remote binary identity only. This is not a source-normalized
numeric row, uncertainty result, calibration, prediction, or external validation.

## Fixed-Background Gaussian Finite-Temperature O(2) Lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The declared O(2) quadratic radial/Goldstone roots
were used to derive a natural-unit Gaussian Bose determinant on a fixed
tree-level condensed background. Pressure, entropy, generalized chemical
potential response, Phi response derivative, energy identity, mode positivity,
and quadrature/cutoff convergence pass.

WHAT_REMAINS_OPEN: The thermal background is not re-minimized, so the
self-consistent finite-temperature phase boundary and thermal backreaction are
open. Vacuum renormalization, interacting self-energy, normal two-fluid
current, physical Kubo coefficient, microscopic SK/KMS, entropy production,
SI Phi mapping, and `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: Fixed-background Gaussian finite-temperature quasiparticle
lane only. No physical two-fluid, Full Topic 13, Core, Gravity, or external
validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_LANE`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_condensate_gaussian_thermal_audit.json` records the action-derived mode-root, thermal
determinant, finite-difference, convergence, units, ontology, and exclusion
checks; this sync links it into the full gate, register, dependency graph,
formula audit, current report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
q = Z*mu^2 - m_eff(Phi)^2 > 0
omega_+-^2 = k^2 + q/Z + 2*mu^2
               +- sqrt((q/Z + 2*mu^2)^2 + 4*mu^2*k^2)
Omega_G = T integral sum_a log(1-exp(-omega_a/T)) d^3k/(2*pi)^3
p_G = -Omega_G
epsilon_G = -p_G + T*s_G + mu*n_G
```

VERIFICATION: `PASS_ACTION_DERIVED_FIXED_BACKGROUND_GAUSSIAN_FINITE_T_LANE`; pressure, entropy, charge-response,
Phi-response and energy identity checks pass; mode roots are non-negative;
reference quadrature/cutoff convergence is within the declared tolerance. No
source row, target curve, fit, physical Kubo coefficient, or Xie 2026 holdout
is used.

CONTROLLING_BLOCKER: `thermal_background_backreaction_and_self_consistent_phase_boundary_not_closed`. The full Topic 13 controller remains the
independent dimensional Phi/SI anchor or `alpha_Phi_K`.

NEXT_ACTION: Derive or source-lock a self-consistent finite-temperature
background/effective potential, then close the normal Kubo/SK/KMS and entropy
sectors while independently obtaining the base-Phi SI anchor.

CLAIM_BOUNDARY: This is an action-derived fixed-background Gaussian
finite-temperature lane in natural units. It is not a self-consistent UET EOS,
finite-temperature two-fluid theory, renormalized loop action, physical
transport result, microscopic SK/KMS match, SI calibration, external
validation, or Full Topic 13 closure.

## Off-Shell Gaussian O(2) Thermal Background Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The off-shell homogeneous O(2) Hessian was derived at
fixed `Phi`, and at `A^2=q/lambda` it recovers the existing radial/Goldstone
determinant. The thermal-only Gaussian potential is evaluated only where both
quadratic roots are positive. At the reference tree-level amplitude, the
one-sided stable-direction thermal slope is `0.0103167102961`, above the declared threshold `0.001`.

WHAT_REMAINS_OPEN: The fixed tree-level amplitude is therefore not a
finite-temperature stationary point of the thermal-only Gaussian potential,
while the lower-amplitude side is unstable at the reference point. A valid
finite-temperature phase boundary requires a declared thermal self-energy or
renormalized effective action. Vacuum counterterms, normal two-fluid/Kubo,
SK/KMS, entropy production, SI Phi mapping, and `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: Off-shell Gaussian thermal background boundary diagnostic
only. No Full Topic 13, Core, Gravity, constitutive transport, or external
validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_OFFSHELL_THERMAL_BACKREACTION_BOUNDARY`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_gaussian_offshell_background_audit.json` and `docs/core/uet_o2_gaussian_offshell_background.py` add the off-shell curvatures,
mode roots, stable-domain audit, stationary determinant recovery, one-sided
thermal tadpole witness, and convergence record; this sync links them into the
full gate, closure register, dependency graph, formula audit, current report,
update log, and ledger.

EQUATION_OR_MAPPING:

```text
Omega_tree(A) = 0.5*(m_eff(Phi)^2 - Z*mu^2)*A^2 + 0.25*lambda*A^4
r_sigma = -q + 3*lambda*A^2
r_pi = -q + lambda*A^2
det(y) = (y-k^2-r_sigma/Z)*(y-k^2-r_pi/Z) - 4*mu^2*y
Omega_G(A,T) = T integral sum_a log(1-exp(-omega_a(A)/T)) d^3k/(2*pi)^3
```

VERIFICATION: `PASS_ACTION_DERIVED_OFFSHELL_THERMAL_BACKREACTION_BOUNDARY`; stationary roots recover the existing
determinant, the thermal-only stable-domain and quadrature checks pass, the
one-sided tadpole is nonzero, and the lower-amplitude witness is rejected as
unstable. No fit, source row, physical Kubo coefficient, or Xie 2026 holdout
is used.

CONTROLLING_BLOCKER: `thermal_background_backreaction_requires_self_consistent_renormalized_phase_boundary`. The full Topic 13 controller remains the
independent dimensional Phi/SI anchor or `alpha_Phi_K`; this lane additionally
makes the finite-temperature self-consistency requirement explicit.

NEXT_ACTION: Derive or explicitly source-lock the thermal self-energy and
vacuum renormalization needed for a self-consistent finite-temperature phase
boundary, then close normal Kubo/SK/KMS, entropy balance, and the independent
base-Phi SI anchor.

CLAIM_BOUNDARY: This is an action-derived off-shell Gaussian thermal boundary
diagnostic in natural units. It is not a renormalized finite-temperature UET
EOS, physical transport result, microscopic SK/KMS match, SI calibration,
external validation, or Full Topic 13 closure.

## Conservative-Action Kubo Identifiability Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO`

WHAT_IS_ACTUALLY_CLOSED: The current single-copy conservative O(2) action
determines the ideal pressure/current/stress sector but does not determine a
unique dissipative Onsager/Kubo sector. Two distinct positive-semidefinite
matrices with positive relaxation times satisfy the formal entropy interface
while producing different dissipative responses. The result is a scoped
no-go for the current action, not a rejection of a future open-system UET
extension.

WHAT_REMAINS_OPEN: A physical coefficient still requires a state-matched
retarded correlator or a microscopic SK/open-system collision-noise derivation,
with units, temperature, chemical potential, Phi state, locator, source
identity, hash, and evidence status. Finite-temperature normal response, SI
transport, curved 3+1 transport, the Phi SI anchor, and `alpha_Phi_K` remain
open.

DEPENDENCY_UNLOCKED: Structural Kubo identifiability boundary only. No
physical transport, Full Topic 13, Core, Gravity, constitutive transport, or
external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_NO_GO_CONSERVATIVE_ACTION_KUBO_IDENTIFIABILITY`

WHAT_CHANGED: `docs/core/artifacts/t13_transport_coefficient_identifiability_no_go.json` and `docs/core/uet_transport_coefficient_identifiability.py` add two explicit PSD transport
witnesses and an action-level identifiability audit; this sync links them into
the full gate, closure register, dependency graph, formula audit, current
report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
S_cons[Phi,chi] -> ideal P(X,Phi), N_ideal^mu, T_ideal^munu
J_diss^A = -L^(AB) X_B, tau_A > 0
nabla_mu J_S^mu = X_A L^(AB) X_B >= 0
```

VERIFICATION: `PASS_SCOPED_NO_GO_CONSERVATIVE_ACTION_KUBO_IDENTIFIABILITY`; the two witnesses are distinct, positive
semidefinite, and have positive relaxation times. The transport implementation
requires external or microscopic matching and emits no default physical
coefficient. Formal SK/KMS/entropy positivity is kept separate from physical
transport evidence. No fit, source row, or Xie 2026 holdout is used.

CONTROLLING_BLOCKER: `physical_Kubo_coefficient_record_missing` for the transport lane. The full Topic 13
controller remains `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`.

NEXT_ACTION: Acquire one state-matched physical Kubo record or derive a
microscopic open-system/SK collision-noise kernel. In parallel, obtain the
independent base-Phi SI anchor and `alpha_Phi_K` route; do not substitute the
internal witnesses as physical values.

CLAIM_BOUNDARY: This is a scoped structural identifiability no-go for the
current conservative action. It is not a physical transport measurement,
microscopic Kubo match, finite-temperature two-fluid closure, SI calibration,
external validation, or Full Topic 13 closure.

## Action-Derived Normal Thermal Response Curvature

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The declared normal O(2) one-loop thermal determinant
was differentiated through the declared `m_eff(Phi)` action map. The natural-
unit Phi response curvature, its temperature derivative, the bare response
potential Hessian contribution, finite differences, and quadrature convergence
are recorded. This closes a derivation lane, not the physical thermal bridge.

WHAT_REMAINS_OPEN: The result has natural-unit field normalization and has no
vacuum counterterm, condensate contribution, finite-temperature two-fluid
completion, physical Kubo coefficient, normalized `beta_T13` correspondence,
SI Phi map, or independent `alpha_Phi_K`.

DEPENDENCY_UNLOCKED: Action-derived natural-unit normal response curvature
only. No normalized beta, SI observable, physical transport, Full Topic 13,
Core, Gravity, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_normal_response_curvature_audit.json` and `docs/core/uet_o2_normal_response_curvature.py` add the action-derived response
curvature, temperature slope, finite-difference checks, convergence records,
units, and explicit non-identification rules; this sync links them into the
full gate, closure register, dependency graph, formula audit, current report,
update log, and ledger.

EQUATION_OR_MAPPING:

```text
m_eff(Phi)^2 = m^2 - epsilon_nc*h*(Phi-Phi_*)
kappa_Phi^T = (partial_Phi m_eff^2)^2 * partial_(m_eff^2) s_M
beta_action_natural = T * partial_T kappa_Phi^T
kappa_Phi = epsilon_nc*U''(Phi) + kappa_Phi^T
```

VERIFICATION: `PASS_ACTION_DERIVED_NORMAL_THERMAL_RESPONSE_CURVATURE`; analytic curvature, temperature slope,
total curvature, finite-difference agreement, and convergence checks pass.
The contract confirms natural units and confirms that physical beta, SI map,
vacuum renormalization, condensate, and Kubo sectors are not emitted. No fit,
source row, or Xie 2026 holdout is used.

CONTROLLING_BLOCKER: `beta_T13_normalized_correspondence_and_source_provenance_missing` for this lane. The Full Topic 13 controller
remains the independent dimensional Phi/SI anchor or `alpha_Phi_K` route.

NEXT_ACTION: Match the action-derived natural-unit curvature to a separately
declared normalized finite-temperature functional or independent source-backed
coefficient without renaming it `beta_T13`; then close renormalization,
normal/two-fluid transport, KMS/entropy, SI Phi mapping, and alpha.

CLAIM_BOUNDARY: This is an action-derived natural-unit normal response
curvature and temperature-slope lane. It is not `beta_T13`, a physical thermal
observable, a renormalized finite-temperature action, a physical transport
coefficient, an SI calibration, external validation, or Full Topic 13 closure.

## Action-Beta to Normalized beta_T13 Correspondence Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO`

WHAT_IS_ACTUALLY_CLOSED: The natural-unit normal-branch action slope and the
named normalized `beta_T13` contract are not numerically identifiable from
the current records. They have different units and derivation origins. Two
distinct positive field/free-energy/temperature scale completions preserve the
current normalized beta witness while leaving the physical correspondence
undefined. The no-go closes the structural question only.

WHAT_REMAINS_OPEN: A declared field normalization, free-energy density scale,
natural-to-Kelvin map, and source-backed `beta_T13` coefficient are missing.
The independent Phi/SI anchor, `alpha_Phi_K`, renormalized finite-temperature
action, transport, SK/KMS, and entropy closure are also open.

DEPENDENCY_UNLOCKED: Correspondence no-go only. No beta value, SI map,
physical transport, Full Topic 13, Core, Gravity, or external-validation
dependency is unlocked.

STATUS: `PASS_SCOPED_NO_GO_ACTION_BETA_T13_CORRESPONDENCE`

WHAT_CHANGED: `docs/core/artifacts/t13_beta_action_normalized_correspondence_no_go.json` and `docs/core/uet_o2_beta_correspondence.py` add explicit scale witnesses
and a unit/derivation comparison between the action-derived curvature and the
normalized beta contract; this sync links them into the bridge gate, register,
dependency graph, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
beta_action_natural = T * partial_T(partial_Phi^2 Omega_T)
beta_T13 = T0 * (da_Phi/dT)|T0
beta_T13 = F(field_normalization, free_energy_scale,
             temperature_unit, beta_action_natural)
```

VERIFICATION: `PASS_SCOPED_NO_GO_ACTION_BETA_T13_CORRESPONDENCE`; the action lane, normalized contract,
Phi-anchor no-go, distinct scale witnesses, and no-holdout checks pass. No
numeric beta, alpha, e0, Kelvin prediction, or target fit is emitted.

CONTROLLING_BLOCKER: `declared_field_normalization_free_energy_scale_and_natural_to_kelvin_beta_correspondence_missing`. The Full Topic 13 controller remains the
independent dimensional Phi/SI anchor or `alpha_Phi_K` route.

NEXT_ACTION: Derive or source-lock the missing scale map and beta coefficient
from an independent finite-temperature action or source, then test EOS,
transport, KMS, entropy, and dissipation without using Xie 2026.

CLAIM_BOUNDARY: This is a scoped structural correspondence no-go. It is not a
physical beta measurement, SI calibration, transport coefficient, external
validation, or Full Topic 13 closure.

## Renormalized Normal One-Loop Scheme Lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: A declared mass-squared Taylor-subtraction scheme through second order at `Phi_*` now produces a finite natural-unit normal-branch vacuum plus thermal one-loop state. Reference conditions, response curvature, cutoff convergence, and pressure/entropy/charge/energy identities are recorded.

WHAT_REMAINS_OPEN: This is not a unique microscopic renormalization, interacting finite-temperature self-energy, condensate/two-fluid EOS, physical Kubo coefficient, microscopic SK/KMS match, entropy-production closure, SI Phi map, or independent `alpha_Phi_K` calibration.

DEPENDENCY_UNLOCKED: Renormalized normal one-loop scheme lane only. No Full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_RENORMALIZED_NORMAL_ONE_LOOP_SCHEME`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_renormalized_normal_branch_audit.json` and `docs/core/uet_o2_renormalized_normal_branch.py` add the declared subtraction scheme, mass-derivative and response checks, convergence record, and thermodynamic identity audit; this sync links them to the full gate, closure register, dependency evidence, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
x = m_eff(Phi)^2
V_vac^R(x) = integral [E(x)-E(x0)-(x-x0)E'(x0)-1/2*(x-x0)^2 E''(x0)] d^3k/(2*pi)^3
Omega_R = V_vac^R + Omega_N^(1,T)
kappa_Phi^R = epsilon_nc U''(Phi) + kappa_Phi^T + (partial_Phi m_eff^2)^2 partial_x^2 V_vac^R
```

VERIFICATION: `PASS_ACTION_DERIVED_RENORMALIZED_NORMAL_ONE_LOOP_SCHEME`; reference renormalization conditions, mass-derivative finite difference, response curvature, convergence, thermodynamic derivatives, natural units, ontology, and holdout exclusion pass. Numerical cancellation sensitivity is explicitly recorded rather than hidden.

CONTROLLING_BLOCKER: `interacting_finite_temperature_self_energy_and_unique_microscopic_scheme_matching_missing` for this lane. Full Topic 13 remains controlled by the independent dimensional Phi/SI anchor, source package, beta bridge, EOS/transport/KMS/entropy completion, and `alpha_Phi_K` calibration.

NEXT_ACTION: Match the finite-temperature action beyond the declared free normal determinant, then close physical Kubo/SK/KMS/entropy and the independent Phi-to-thermal observable map without using Xie 2026 or fitting `alpha_Phi_K`.

CLAIM_BOUNDARY: This is an action-derived natural-unit subtraction scheme for one normal O(2) lane. It is not a unique physical renormalization, external validation, SI calibration, transport coefficient, or Full Topic 13 closure.

## Thermal-Only Quadratic Condensed Stability Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The declared O(2) Hessian gives an analytic lower boundary `A_boundary^2=q/lambda` where `r_pi=0` and `r_sigma=2q`. The quadratic mode witness is nonnegative at and above this boundary and becomes negative below it. The thermal-only grand potential and one-sided slope at the boundary are finite and converged.

WHAT_REMAINS_OPEN: This is a quadratic stability boundary, not a self-consistent finite-temperature stationary phase boundary. Thermal self-energy, vacuum renormalization, condensate/two-fluid EOS, physical Kubo, microscopic SK/KMS/entropy, SI Phi mapping, and `alpha_Phi_K` remain open.

DEPENDENCY_UNLOCKED: Thermal-only quadratic stability boundary lane only. No finite-temperature phase-transition, Full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation dependency is unlocked.

STATUS: `PASS_ACTION_DERIVED_THERMAL_QUADRATIC_STABILITY_BOUNDARY`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_thermal_stability_boundary_audit.json` and `docs/core/uet_o2_thermal_stability_boundary.py` add the analytic boundary, mode-sign witnesses, one-sided thermal diagnostic, convergence record, and explicit non-promotion boundary; this sync links them into the full gate, closure register, dependency evidence, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
q = Z*mu^2 - m_eff(Phi)^2 > 0
r_pi(A) = -q + lambda*A^2
A_boundary^2 = q/lambda
r_sigma(A_boundary) = 2*q
```

VERIFICATION: `PASS_ACTION_DERIVED_THERMAL_QUADRATIC_STABILITY_BOUNDARY`; `r_pi=0`, `r_sigma=2q`, mode roots are nonnegative at/above the boundary and negative below it, thermal one-sided slope is resolved, and cutoff convergence passes. No clipping, fit, source row, or Xie 2026 holdout is used.

CONTROLLING_BLOCKER: `thermal_background_backreaction_requires_self_consistent_renormalized_phase_boundary`. The boundary is not a finite-temperature stationary solution because the declared thermal determinant supplies a nonzero one-sided slope; closing that requires thermal self-energy or a renormalized effective action.

NEXT_ACTION: Derive or source-lock the finite-temperature self-energy needed for an interior stationary boundary, then close the condensate/normal two-fluid EOS and physical transport without promoting this stability boundary to a phase transition.

CLAIM_BOUNDARY: This is an action-derived natural-unit quadratic stability boundary and thermal-only diagnostic. It is not a self-consistent finite-temperature phase transition, EOS closure, transport result, SI calibration, external validation, or Full Topic 13 closure.

## Thermal Gaussian Condensate Stationarity No-Go

MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO`

WHAT_IS_ACTUALLY_CLOSED: In the declared tree plus stable thermal Gaussian branch, let `x=A^2`. The stable domain is `x>=q/lambda`; the tree derivative is nonnegative, both quadratic mode roots increase with `x`, and each stable Bose determinant term increases with `x`. Therefore the combined thermal-only potential has no stationary condensate in that domain. Analytic margins, finite-difference derivative signs, and cutoff convergence are recorded.

WHAT_REMAINS_OPEN: This no-go is scoped. Vacuum counterterms, interacting finite-temperature self-energy, and a renormalized effective action may define a different branch and are not ruled out. EOS/two-fluid, physical Kubo, SK/KMS/entropy, SI Phi mapping, alpha, source package, and Full Topic 13 remain open.

DEPENDENCY_UNLOCKED: No-go for the current thermal-only Gaussian branch only. A named renormalized/interacting branch is required; no Full Topic 13, Core, Gravity, transport, SI, alpha, or external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_NO_GO_THERMAL_GAUSSIAN_CONDENSATE_STATIONARITY`

WHAT_CHANGED: `docs/core/artifacts/t13_uet_o2_gaussian_thermal_stationarity_no_go.json` and `docs/core/uet_o2_gaussian_thermal_stationarity_no_go.py` add the algebraic no-go, analytic mode-root derivatives, finite-difference sign witnesses, and convergence record; this sync links them into the full gate, closure register, dependency evidence, formula audit, report, update log, and ledger.

EQUATION_OR_MAPPING:

```text
x = A^2
x >= q/lambda
partial_x Omega_tree = 0.5*(-q + lambda*x) >= 0
partial_x omega_+^2 > 0, partial_x omega_-^2 > 0
partial_x [T log(1-exp(-omega/T))] > 0
=> partial_x Omega_tree+Omega_G > 0
```

VERIFICATION: `PASS_SCOPED_NO_GO_THERMAL_GAUSSIAN_CONDENSATE_STATIONARITY`; analytic discriminant margin is positive, mode-root derivatives are positive over the declared witness, thermal and combined finite-difference derivatives are positive, and potential convergence passes. No clipping, fit, source row, or Xie 2026 holdout is used.

CONTROLLING_BLOCKER: `thermal_gaussian_stationarity_no_go_requires_named_renormalized_interacting_branch_for_any_finite_temperature_stationary_solution`. The no-go excludes only a stationary point of the current thermal-only Gaussian domain; any finite-temperature stationary phase claim now requires the named renormalized/interacting branch.

NEXT_ACTION: Derive or source-lock the finite-temperature self-energy and renormalized effective action for the named branch, then test whether a stationary solution exists before discussing phase transition or two-fluid closure.

CLAIM_BOUNDARY: This is a scoped structural no-go for the current tree plus stable thermal Gaussian branch. It is not a no-go for interacting finite-temperature UET, a physical phase-transition proof, EOS closure, transport result, SI calibration, external validation, or Full Topic 13 closure.

## Ding Public Supplementary Payload Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The official 11-object Ding PMC inventory and all three MOESM PDFs are locally hash-pinned. The public machine-readable route contains no raw numeric `C_src` or PBTE input payload object.

WHAT_REMAINS_OPEN: Ding mode-resolved numeric `C_src`, an accepted same-regime PBTE reproduction, independent `alpha_Phi_K`, the non-circular bridge/beta, EOS/transport/KMS/entropy, and the dimensional `Phi` to thermal-observable map.

DEPENDENCY_UNLOCKED: Public Ding supplementary provenance boundary only. No full-source, alpha, Core, Gravity, or constitutive-transport dependency is unlocked.

STATUS: `PASS_PUBLIC_SUPPLEMENTARY_PAYLOAD_BOUNDARY_NO_NUMERIC_C_SRC`

WHAT_CHANGED: Added `docs/core/artifacts/t13_ding_public_supplementary_payload_boundary_audit.json`, integrated it into the Topic 13 full gate under `verification_status.source_package`, and recorded the MOESM1-3 hashes in `DATA_MANIFEST.md`.

EQUATION_OR_MAPPING: `C_src(T) = sum_mu c_mu(T)` and `Delta_Tq = Delta_u_ph / C_src` remain Ding source definitions; the audited PDFs and figures are not relabeled as numeric `C_src` rows. The measurement layer remains `y_TTG = Delta_Tq(t) / Delta_Tq(0)`.

VERIFICATION: Public inventory count, object-key set, PDF sizes, local hashes, no machine-readable numeric payload extension, holdout exclusion, and no alpha fitting pass. Focused Topic 13 suite: `16 passed`. Full gate hash: `0bf92c90042368d9edb2d62efddc0ab669c2490e82108c3fe8d1341c324db23d`. Major-result register hash: `bd2df440394afac3e678ba34af93b8cec4b8aacbe9d9be36d95b1b3760972333`.

CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.

NEXT_ACTION: Use the recorded corresponding-author request route if authorized, or build an accepted Ding-regime PBTE reproduction with mode-resolved `C_src(T)`, convergence, uncertainty, and unit contracts. Do not relabel MP48, figures, or PDFs as `C_src`.

CLAIM_BOUNDARY: This closes only the public supplementary payload-availability boundary. Full Topic 13 remains `PARTIAL / BLOCKED`; no external validation, independent `alpha_Phi_K`, or global UET closure is claimed.

### 2026-08-13 - MP48 harmonic spectral C_src-like cross-file lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_MP48_SPECTRAL_C_SRC_REPRODUCTION`.
WHAT_IS_ACTUALLY_CLOSED: The archived MP48 total DOS and deposited harmonic thermal-properties file reproduce a C_src-like spectral heat-capacity row at 200, 250, and 300 K with explicit quadrature and source hashes.
WHAT_REMAINS_OPEN: This is not Ding PBTE `C_src`, does not establish Ding material-regime equivalence, does not provide PBTE mode-resolved uncertainty/convergence, and does not supply the base-Phi energy anchor or `alpha_Phi_K`.
DEPENDENCY_UNLOCKED: MP48 harmonic spectral consistency lane only; no source, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_HARMONIC_DOS_CROSS_FILE_REPRODUCTION`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/artifacts/t13_mp48_spectral_csrc_reproduction_audit.json` (SHA-256 `5b2c6332fb70c6ae98749d96051cc4dbbffa04d37eed8f90e09168d35c61c091`) and linked it into the Topic 13 full gate (SHA-256 `af317db05b87a694502b5852ee14f6a90e3b094ead9bb521c88c6820efb03ad2`).
EQUATION_OR_MAPPING: `c_mu(T) = k_B x_mu^2 exp(x_mu)/(exp(x_mu)-1)^2`, `C_src^DOS = N_A integral[g(nu)c(nu,T)dnu]`; this is the harmonic MP48 comparator and is not relabeled as Ding `C_src`.
VERIFICATION: 201-row uniform DOS grid, deposited rows at 200/250/300 K, finite kernel values, trapezoid/Simpson/every-second-bin envelope, source hashes, no target fit, no alpha fit, and no holdout access. Maximum trapezoid residual is `0.009992863239339345`; maximum coarse-grid difference is `0.014787789991730582`.
CONTROLLING_BLOCKER: `Ding_material_regime_and_mode_resolved_C_src_acceptance_missing` for this lane; the full gate remains controlled by the existing Ding source, dimensional alpha, bridge/beta, EOS/transport/KMS/entropy, and SI-map blockers.
NEXT_ACTION: Obtain Ding-compatible mode-resolved `C_src(T)` or an accepted same-regime PBTE reproduction with volume, convergence, uncertainty, and material-state contracts; separately obtain a declared base-Phi SI anchor or independent paired calibration.
CLAIM_BOUNDARY: Internal/cross-file harmonic MP48 reproduction only. It is not Ding PBTE reproduction, UET transport validation, a temperature prediction, an `alpha_Phi_K` calibration, or Full Topic 13 closure.

### 2026-08-13 - MP48 named Phi_E dimensional comparator

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_MP48_PHI_E_DIMENSIONAL_ANCHOR_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: A standard harmonic energy-to-temperature comparator is source-locked at MP48 reference temperature `T0=300 K`; `Phi_E := Delta_u_ph/e0(T0)` and `alpha_Phi_E_K := e0(T0)/c_v(T0)` are numerically evaluated without target fitting.
WHAT_REMAINS_OPEN: The mapping from base UET `Phi` to named `Phi_E` is not derived, so this does not close base `alpha_Phi_K`; Ding PBTE material matching, physical transport, SK/KMS, entropy, and dissipative balance remain open.
DEPENDENCY_UNLOCKED: Named `Phi_E` standard dimensional comparator only; no base-Phi, Full Topic 13, Core, Gravity, or transport unlock.
STATUS: `PASS_SCOPED_PHI_E_DIMENSIONAL_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/core/artifacts/t13_mp48_phi_e_dimensional_comparator_audit.json` (SHA-256 `46fad518feb670e7e3fe4faac47582f7a5e93b88985c53225d4da4e6fc7cde44`), integrated it under the dimensional-observable map, and refreshed the register (`9890c4464268d7ae043b445f62b400198b3479f8358bad9d2e4db27044bf7be7`) and full gate (`2e1c8ff8f845b24a10abff390a2fd8ef762021203155ccdbc65afb7c3e1d2871`).
EQUATION_OR_MAPPING: `u_th(T)=N_A integral[g(nu) h nu/(exp(h nu/(k_B T))-1)dnu]`; `Phi_E=Delta_u_ph/e0(T0)`; `Delta_Tq=(e0(T0)/c_v(T0))*Phi_E`; at `300 K`, conditional `alpha_Phi_E_K=126.72529975005031 K`.
VERIFICATION: DOS source identity, zero negative-frequency weight, uniform grid, source volume, finite energy/capacity rows at `200/250/300 K`, volume cancellation in `e0/c_v`, no base-alpha emission, no target fit, and no Xie 2026 access. Focused Phi_E/spectral tests: `4 passed`.
CONTROLLING_BLOCKER: `base_Phi_to_Phi_E_mapping_and_independent_alpha_Phi_K_missing` for this lane; full gate retains the existing dimensional and source/transport blockers.
NEXT_ACTION: Derive or source-lock a physical base-Phi-to-Phi_E amplitude map, or obtain a paired base-Phi/SI record. Do not relabel `alpha_Phi_E_K` as `alpha_Phi_K`.
CLAIM_BOUNDARY: Standard harmonic comparator only. It is not a base-Phi calibration, not Ding PBTE validation, not a UET temperature prediction, and not Full Topic 13 closure.

### 2026-08-13 - MP48 force-constant harmonic reconstruction lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_MP48_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION`.
WHAT_IS_ACTUALLY_CLOSED: The archived 200x200 MP48 force-constant matrix parses with every pair present once; its primitive-to-supercell mapping reconstructs a 12-mode dynamical matrix, satisfies acoustic/Hermitian roundoff checks, and reaches the deposited frequency envelope on a declared 5x5x2 q-grid.
WHAT_REMAINS_OPEN: This does not reproduce Ding PBTE `C_src`, third-order PBTE transport, the Ding material regime, the base-Phi energy anchor, or independent `alpha_Phi_K`.
DEPENDENCY_UNLOCKED: MP48 harmonic force-constant source lane only; no Ding source, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_FORCE_CONSTANT_HARMONIC_RECONSTRUCTION`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/artifacts/t13_mp48_force_constant_harmonic_reconstruction_audit.json` (SHA-256 `3903fbbbc22476e1394305edd2c9ad3c948802d31a9a9c36c572b8eb395cedd1`) and linked it into the Topic 13 full gate (SHA-256 `f6005cb6225975168eaf9fdf41ff280a6a6c096c16b55129cc9a92fda01671fd`).
EQUATION_OR_MAPPING: `D_ij(q) = sum_R Phi_ij(R) exp(2*pi*i*q.R)/sqrt(m_i*m_j)` and
u_mu = sign(lambda_mu)*sqrt(abs(lambda_mu))*conversion_factor`; mapping is from supercell Cartesian coordinates to primitive atom plus integer translation.
VERIFICATION: Force-constant shape `200x200x3x3`, pair symmetry residual `1.1e-14`, acoustic-sum residual `9.5e-14`, Gamma acoustic maximum `8.17e-7 THz`, no q-grid negative eigenvalue beyond roundoff, and q-grid maximum `48.41862978666018 THz` versus deposited summary `48.4370817598 THz` (relative gap `-0.0003809472509372913`). No fit, target access, holdout access, or alpha emission.
CONTROLLING_BLOCKER: `Ding_material_regime_and_mode_resolved_C_src_acceptance_missing` for this lane; the full gate remains controlled by the existing Ding source, dimensional alpha, bridge/beta, EOS/transport/KMS/entropy, and SI-map blockers.
NEXT_ACTION: Obtain Ding-compatible mode-resolved `C_src(T)` or an accepted same-regime PBTE reproduction with volume, convergence, uncertainty, and material-state contracts; separately obtain a declared base-Phi SI anchor or independent paired calibration.
CLAIM_BOUNDARY: Internal/source-traceable MP48 harmonic reconstruction only. It is not Ding PBTE reproduction, UET transport validation, a temperature prediction, an `alpha_Phi_K` calibration, or Full Topic 13 closure.

### 2026-08-13 - NIST graphite alpha_V source boundary lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NIST_GRAPHITE_ALPHA_V_SOURCE_BOUNDARY`.
WHAT_IS_ACTUALLY_CLOSED: Official NIST SP 260-89 AXM-5Q1 graphite source is archived with SHA-256 `fbcde491cadf6b8105d8b22bd15145e48709926aaf1d4a24335af2a8984c71b2`; its declared length-expansion polynomial is evaluated at 200, 225, 250, and 300 K and converted explicitly to an isotropic `alpha_V` comparator.
WHAT_REMAINS_OPEN: `K_T` is not source-locked, the AXM-5Q1 comparator is not established as Ding/HOPG material equivalence, row-level statistical uncertainty is absent, and `Cp -> Cv`, Ding `C_src`, base-Phi mapping, and `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: NIST alpha_V source-comparator lane only; no `K_T`, volumetric `c_v`, Ding source, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_NIST_ALPHA_V_SOURCE_BOUNDARY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/artifacts/t13_nist_graphite_alpha_v_source_boundary_audit.json` (SHA-256 `392bf8c98de925ea806a86392cbf440029a47e4e32173c2839cd04ff2cb553d5`) and linked it into the Topic 13 full gate (SHA-256 `4cc6d5b68e7ee84710da6fb357ec7b4c640ca30182835200b84b2be41507e2a8`).
EQUATION_OR_MAPPING: `Delta_L/L[%] = -0.201 + 6.595e-4*T + 9.593e-8*T^2 - 3.427e-12*T^3`, `alpha_L = d(Delta_L/L)/dT/(1+Delta_L/L)`, and comparator `alpha_V=3 alpha_L`.
VERIFICATION: PDF presence and hash, source locators, explicit percent-to-strain conversion, finite rows, NIST program accuracy boundary, no invented `K_T`, no target fit, no alpha fit, and no Xie 2026 access. At 300 K the comparator gives `alpha_V = 2.1482823124269745e-5 K^-1`.
CONTROLLING_BLOCKER: `isothermal_bulk_modulus_K_T_and_Ding_material_regime_mapping_missing` for this lane; full Topic 13 remains controlled by the existing Ding source, alpha, bridge/beta, EOS/transport/KMS/entropy, and SI-map blockers.
NEXT_ACTION: Obtain source-locked `K_T` with uncertainty for a declared material state and explicit mapping to the TTG sample; do not combine this comparator with Ding `C_src` or use it as a base-Phi calibration.
CLAIM_BOUNDARY: Internal/source-traceable AXM-5Q1 alpha_V comparator only. It is not a Ding/HOPG material match, complete `Cp -> Cv` closure, UET transport validation, `alpha_Phi_K`, or Full Topic 13 closure.

### 2026-08-13 - Bosak graphite elastic bulk comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_GRAPHITE_ELASTIC_BULK_MODULUS_SOURCE`.
WHAT_IS_ACTUALLY_CLOSED: The Bosak et al. IXS primary PDF is archived with SHA-256 `5db6247c3dbf48dcbed70d749da96ca61816fe6fed480f32d80a947ead649d7d`; its room-temperature single-crystal graphite elastic tensor and reported `B=36.4 +/- 1.1 GPa` are transcribed, and the hexagonal compliance inversion reproduces `B_elastic=36.44001810774106 GPa`.
WHAT_REMAINS_OPEN: The IXS result is an elastic/dynamic comparator rather than a source-locked isothermal `K_T`; same-state `Cp/Cv`, Ding TTG material mapping, `Cp -> Cv`, base-Phi mapping, and `alpha_Phi_K` remain open.

## Fixed-Reference Ward Coefficient State-Dependence Boundary (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_AS_NO_GO for T13_UET_O2_WARD_CONSTRAINED_COEFFICIENT_STATE_DEPENDENCE_NO_GO; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: With one fixed reference point and scale, the algebraically Ward-derived local coefficient varies across the declared finite-temperature and response state grid. Each state can be made Ward-stationary separately, but the residual-tolerance coefficient intervals have no common intersection.
WHAT_REMAINS_OPEN: A state-independent physical finite-temperature renormalization scheme, Ward-preserving condensed 2PI or controlled 1/N completion, complete condensed/two-fluid EOS, retarded physical Kubo, microscopic SK/KMS, entropy/heat-flux balance, dimensional Phi mapping, independent alpha_Phi_K, and Ding-compatible C_src remain open.
DEPENDENCY_UNLOCKED: Scoped state-independence boundary only; no physical renormalization, condensed EOS, transport, Core, Gravity, SI, alpha, or external-validation dependency is unlocked.
STATUS: PASS_SCOPED_WARD_COEFFICIENT_STATE_DEPENDENCE_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Added a fixed-reference state-grid audit, regression test, full-gate projection, and major-result register synchronization. The state grid is diagnostic rather than a fit set and does not read Xie 2026.
EQUATION_OR_MAPPING: x_W=q/lambda; a_W(state)=-D_0(x_W;state)*Lambda_*^2/[3*(x_W-x_*)^2]; admission requires D_a(x_W;state)=0 with one common a. The declared coefficient range is -0.004429003695465447 to -0.003457384113108128, with an empty common residual-tolerance interval.
VERIFICATION: Audit passed with zero failed checks; all six state records are finite and condensed, each is Ward-stationary to 1e-10, coefficient spread is 0.0009716195823573194, and the common interval is empty. Regression test passed (3 passed); major-result closure has 99 entries; downstream dependency audit remains blocked; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: state_independent_physical_finite_temperature_renormalization_scheme_missing.
NEXT_ACTION: Construct a state-independent microscopic or symmetry-improved finite-temperature scheme, then rerun the condensed EOS and retarded Kubo/SK-KMS gates across the state domain.
CLAIM_BOUNDARY: This closes only the state-independence boundary of the present one-counterterm Ward construction under the declared fixed reference and state grid. It is not a no-go for every higher-order or microscopic scheme and does not close physical finite-temperature theory or Full Topic 13.
EVIDENCE_HASHES: audit fec9203a71d10330c63e415b2e8e264a39c392f14002a86ccbe583d79d0a4a8e; verifier b31bd59cbe63020635bb155c67d26796a70d6246a72cb0a8581caaea2556781d; regression 390d02fee6f56489efab63b50602e3785190cc3adf9385b4c82322cc7357f807; full gate dcf92c2f78a83fc6b8f9bdbc634f43c6b2cc583c2bf741d59a22013aaf39429b; register a91c91682f1959158568bdfa71f019c4a4114549441d6298794430c10d60fc05; dependency 352bd07ec29792fe032a6cfbebcba111949f909b323a7411fde2cfcaffe46575.
DEPENDENCY_UNLOCKED: Source-locked graphite elastic bulk comparator only; no `K_T`, volumetric `c_v`, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_GRAPHITE_ELASTIC_BULK_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/artifacts/t13_graphite_elastic_bulk_modulus_source_audit.json` (SHA-256 `65238edbfb66b57c6b3c0a06f95d8b3d28d6dc613df7b83d825332aff4a996af`), the Bosak source package, and the archived primary PDF; current full-gate hash is `60bb65b47f33dcd08f2f01a40d200d78d01eaf79236c6ca02ae91a17572f57f1`.
EQUATION_OR_MAPPING: `S=C_normal^-1`; `B_elastic=1/(2*S11+2*S12+4*S13+S33)`; no `C33 -> K_T` relabeling.
VERIFICATION: Source hash, page locators, tensor positivity, compliance inversion, central-value agreement, uncertainty declaration, no `K_T` emission, no target fit, no alpha fit, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `isothermal_K_T_material_regime_and_dynamic_to_thermal_conversion_missing` for this lane; the full gate remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Obtain a same-state isothermal `K_T` or a permitted dynamic-to-thermal conversion with matched `Cp/Cv` and material-state uncertainty; do not use the elastic comparator as `alpha_Phi_K`.
CLAIM_BOUNDARY: Internal/source-traceable single-crystal graphite elastic bulk comparator only. It is not `K_T`, not a Ding/HOPG material match, not UET transport, not an alpha calibration, and not Full Topic 13 closure.

### 2026-08-13 - Hanfland graphite isothermal K_T source lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_GRAPHITE_ISOTHERMAL_KT_SOURCE`.
WHAT_IS_ACTUALLY_CLOSED: The Hanfland et al. primary XRD equation-of-state PDF is archived with SHA-256 `300a6b03af667f71a27fc7c269e7a928af57d4b846bded25feaefa0e37b1089e`; its fixed-temperature `T=300 K` ambient-pressure graphite EOS row is source-locked as `K_T=33.8 +/- 3.0 GPa` with the reported reference volume and pressure derivative.
WHAT_REMAINS_OPEN: Same-grade alpha_V and density uncertainty, mapping from natural graphite powder to the Ding TTG material, temperature-resolved K_T, matched Cp/Cv, base-Phi mapping, and independent `alpha_Phi_K` remain open. No local pressure-volume refit was performed.
DEPENDENCY_UNLOCKED: Declared 300 K natural-graphite isothermal K_T source lane only; no same-grade Cp-to-Cv, alpha, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_ISOTHERMAL_GRAPHITE_K_T_SOURCE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/artifacts/t13_graphite_isothermal_kt_source_audit.json` (SHA-256 `63f0518c78febda473f89f8a0c3927d14b9d98a102dc560277bcd2a9daf8c0c4`), the Hanfland source package, and the archived primary PDF; current full-gate hash is `236f82bdb7a810e587255fb1368d97e7e84f66167bb9f638d81f7dfbc0077c34`.
EQUATION_OR_MAPPING: `K_T=-V*(partial P/partial V)_T=dP/d(-ln V)`; source Murnaghan fit at `T=300 K`, `P=0` gives `33.8 +/- 3.0 GPa`; this is not inferred from `C33`.
VERIFICATION: Source hash, page locators, fixed-temperature XRD method, isothermal derivative definition, scalar row identity, uncertainty, no figure refit, no target fit, no alpha fit, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `same_grade_alpha_V_K_T_and_Ding_material_regime_mapping_missing` for this lane; the full gate still requires Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Match this `K_T` to the Ding TTG material and acquire same-state alpha_V/density/Cp/Cv uncertainty; do not combine it with NIST AXM-5Q1 alpha_V without a material-state map.
CLAIM_BOUNDARY: Source-traceable 300 K natural-graphite K_T input only. It is not a Ding/HOPG match, not complete Cp-to-Cv closure, not UET transport, not an alpha calibration, and not Full Topic 13 closure.

### 2026-08-13 - IHEP TPG anisotropic alpha_V comparator lane

## Action-Derived Dilute-Gas Kinetic Collision Lane (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_KINETIC_COLLISION_KERNEL_LANE; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: A declared constant-amplitude 2-to-2 phase-space kernel produces a positive normal-branch collision width and a finite dilute-gas kinetic response in natural units. Quadrature and cutoff refinement are bounded on the declared state.
WHAT_REMAINS_OPEN: Final-state Bose enhancement, ladder/vertex matching, condensed scattering, microscopic SK/KMS and retarded Kubo matching, heat-flux/entropy balance, dimensional Phi mapping, independent alpha_Phi_K, and Ding-compatible C_src.
DEPENDENCY_UNLOCKED: Action-derived dilute-gas kinetic comparator only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation dependency is unlocked.
STATUS: PASS_ACTION_DERIVED_DILUTE_KINETIC_COLLISION_LANE; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Added the collision-kernel module, audit artifact, focused regression, full-gate projection, and major-result synchronization. The fixed reference momentum is k_ref=max(T,m_eff,sqrt(Z)*abs(mu)); no source rows, fit, target curve, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: E_s(k)=sqrt(k^2+m_eff^2)-s*sqrt(Z)*abs(mu); sigma_22(s)=lambda^2/(16*pi*s); Gamma_s(k)=sum_r integral[d^3p/(2*pi)^3] f_r(E_p)v_rel sigma_22(s); D_s=(1/3)integral[d^3k/(2*pi)^3]k^2[-partial_E f_s]; K_kin=sum_s D_s/Gamma_s(k_ref).
VERIFICATION: Audit passed with zero failed checks; reference collision widths are 1.3919336977353308e-06 for both species; reference K_kin=608.3842369966399; refined-vs-reference width and response changes are both about 2.55e-06; focused regression passed (3 passed); the current major-result register has 104 entries; downstream dependency audit remains blocked.
CONTROLLING_BLOCKER: microscopic_ladder_vertex_and_SK_KMS_matching_missing.
NEXT_ACTION: Use the separate quantum and conserving-response lanes to match a momentum-dependent microscopic ladder and SK/KMS response, without promoting the comparator coefficient.
CLAIM_BOUNDARY: This closes only an action-derived dilute-gas kinetic comparator lane. It is not a physical Kubo coefficient, complete finite-temperature transport theory, SI observable, alpha_Phi_K calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module 411314a28d67bbce457f96ad6f147b183a7580fb983e88af7ba9ce0ce7c149be; verifier 9547fe1d29b2df7538af18142d22756af52295b523d741e8fab056fb5ca1e3eb; regression 8fab8d414e268c97cbaff2982ff807da14c76061bf2a3861707256ba334329f5; artifact 1f56e114e69e7c238d55921a3a3c2265b3e26e1655e7d69948072680499747a8; full gate 79c44f158589e2a1f4bcd20da4f307505fef63ae9cbd193326d26d4105bbbaa3; register f9eae6d0ea9c7e6b41876c7d2f6a5ba68f4929d249260b7f4c1700bda1d7ccdf; dependency fb5497504fbf50875dbf60a1f78a14e313e1aceb51df6054d608bb52927ce75e.

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The IHEP 2001-32 report is archived with SHA-256 `e9527b8dba9d3944a1a9298e9d516e501279b500586cf0179ec076b94fdd6f2e`; its ATOMGRAPH TPG in-plane row `alpha_a=-1.04 +/- 0.11e-6 K^-1` and averaged TPG out-of-plane row `alpha_c=26.84 +/- 0.4e-6 K^-1` are source-locked over the reported near-room-temperature range. The explicit family comparator is `alpha_V=24.76e-6 K^-1` with propagated comparator uncertainty `0.4565085979e-6 K^-1`.
WHAT_REMAINS_OPEN: The two axes are not a same-specimen, same-point pair; same-state density/Cp/Cv, Ding TTG material mapping, base-Phi SI mapping, and `alpha_Phi_K` remain open. This comparator does not close the Hanfland `K_T` lane.
DEPENDENCY_UNLOCKED: Source-locked TPG family-level `alpha_V` comparator only; no same-grade `K_T`, Ding `C_src`, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_TPG_ANISOTROPIC_ALPHA_V_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/artifacts/t13_tpg_anisotropic_alpha_v_source_audit.json` (SHA-256 `f8ed02677b5ef1aede683cc2b191538722bda56b520d1d6ba5af024638504c68`), the IHEP source package, and the archived primary report; current full-gate hash is `1a35429f68456f46aa6e0f4ae75c822fba0ef2f88042774a80c34020cbdc70bc`.
EQUATION_OR_MAPPING: `alpha_V=2*alpha_a+alpha_c`; uncertainty is propagated only as a zero-covariance comparator assumption. The source scope is approximately 25-60 deg C, not an exact 300 K point.
VERIFICATION: Source hash, report locators, units, sign and range checks, anisotropic reconstruction, uncertainty boundary, mixed-row boundary, no `K_T`, no target fit, no alpha fit, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `same_specimen_alpha_V_K_T_and_Ding_material_regime_mapping_missing`; full Topic 13 is still controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Acquire a same-state/same-specimen `alpha_V` and `K_T` pair or a permitted direct volumetric heat-capacity route; keep this family comparator out of calibration and holdout paths.
CLAIM_BOUNDARY: Internal/source-traceable TPG family-level expansion comparator only. It is not a same-specimen volumetric measurement, not a Ding/HOPG material match, not UET transport, not an alpha calibration, and not Full Topic 13 closure.

### 2026-08-13 - official Nelson-Riley natural graphite alpha_V comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NATURAL_GRAPHITE_NELSON_RILEY_ALPHA_V_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The official OSTI/Argonne ANL-5524 report is archived with SHA-256 `7e334a4c380c130773f6c34a6238f25a9c28e15c3a9c0e1f9aa3769647e98561`; Table XIX gives `alpha_a=-1.5e-6 K^-1` over 0-150 deg C and `alpha_c=27.00e-6+3.05e-9*T_C K^-1`. At the declared approximate 27 deg C point, the deterministic family comparator is `alpha_V=24.08235e-6 K^-1`.
WHAT_REMAINS_OPEN: The source provides no row-level statistical uncertainty, does not identify the Hanfland specimen as the same state, and does not establish the Ding TTG material regime. Base-Phi mapping and `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: Official natural/crystalline graphite family alpha_V comparator only; no same-specimen `K_T`, Ding `C_src`, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_NATURAL_GRAPHITE_ALPHA_V_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated `docs/core/artifacts/t13_natural_graphite_nelson_riley_alpha_v_source_audit.json` (SHA-256 `c20b42f64b9107459b555dfaddc5150028c39b5254e4791782161b2b9861b861`), the ANL-5524 source package, and the archived official report; current full-gate hash is `03fc499a284a43a0f15e314ed7efc3e8d683e16ed05adc2b9f331f2b1b8f8ea6`.
EQUATION_OR_MAPPING: `alpha_a=-1.5e-6 K^-1`; `alpha_c=27.00e-6+3.05e-9*T_C K^-1`; `alpha_V=2*alpha_a+alpha_c`. No uncertainty was invented where Table XIX gives none.
VERIFICATION: Source hash, Table XIX locator, Celsius/Kelvin scope, formula reconstruction, no-uncertainty boundary, no `K_T`, no target fit, no alpha fit, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `same_specimen_alpha_V_K_T_uncertainty_and_Ding_material_regime_mapping_missing`; full Topic 13 remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Find a same-state/same-specimen alpha_V and K_T source with uncertainty, or a permitted direct volumetric heat-capacity route; do not use this table as calibration.
CLAIM_BOUNDARY: Official natural/crystalline graphite family comparator only. It is not a same-specimen measurement, not a matched Hanfland state, not a Ding TTG material match, not UET transport, not an alpha calibration, and not Full Topic 13 closure.

## Latest Source-Route Boundary: MP48 C_src Mesh Convergence (2026-08-13)

The latest independent MP48 force-constant route is machine-readable in
`docs/core/artifacts/t13_mp48_force_constant_csrc_mesh_convergence_audit.json`.
It passes source-integrity and stability checks but fails the declared mesh
convergence criterion: the maximum adjacent-mesh change is `0.513481935500736`
against `0.01`. The route is therefore `CLOSED_FOR_LANE` as a no-go boundary,
while full Topic 13 remains `PARTIAL/BLOCKED` and the Ding `C_src` blocker is
not removed.

## Huang 2023 Graphite Supplementary Boundary (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_HUANG_2023_SUPPLEMENTARY_PAYLOAD_BOUNDARY`.
WHAT_IS_ACTUALLY_CLOSED: The NIMS/publisher supplementary PDF is source-locked at 2726877 bytes with SHA-256 `aaf2f325ddc797e7c309132e65d69379e4223e049e7411e6c3dc04cba9e09b90`. Review of all 9 pages found figures, methods, and narrative but no row-level PBTE or force-constant payload; curves were not digitized.
WHAT_REMAINS_OPEN: This independent isotopically purified graphite-ribbon comparator is not declared equivalent to Ding's HOPG TTG/PBTE regime. Numeric Ding `C_src`, base-Phi SI mapping, and independent `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: Huang comparator provenance only; no source, alpha, bridge, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_HUANG_PUBLIC_SUPPLEMENTARY_BOUNDARY_NO_NUMERIC_PBTE_PAYLOAD`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added the source-boundary artifact and integrated it into full gate SHA-256 `888e2ff3cd23a2e4b1b4454b53039c76fd7b3a8083cb8dd6cf2427e7d25beaeb` and register SHA-256 `730cd7ab782e51e5b29ddc4bb8d5f017724f34413ae34d5059d3863767e4db72`.
EQUATION_OR_MAPPING: Comparator layer only: `y_TTG = Delta_Tq(t) / Delta_Tq(0)`; no `C_src`, `Delta_Tq = alpha_Phi_K * Delta_Phi
rho_model = N_C M_C / (N_A V_primitive)
c_v,implied = C_src / rho_model`, or temperature prediction is emitted.
VERIFICATION: Hash, size, PDF/page boundary, no numeric payload, no digitization, no fit, no alpha fit, and no Xie 2026 holdout access pass.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing` plus the existing alpha, bridge/beta, EOS/transport/KMS/entropy, dimensional-map, and material-regime blockers.
NEXT_ACTION: Obtain an authorized numeric Ding payload or accepted same-regime PBTE reproduction with convergence, uncertainty, and units.
CLAIM_BOUNDARY: Independent public comparator provenance only; not Ding validation, UET transport validation, alpha calibration, or Full Topic 13 closure.

## MP48 Finest-Pair Convergence Refinement (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` refinement for the finest-pair diagnostic; MP48 complete route remains blocked.
WHAT_IS_ACTUALLY_CLOSED: The `20x20x8 -> 25x25x10` pair is below the unchanged 1% numerical criterion at `0.006531457496264048`.
WHAT_REMAINS_OPEN: `15x15x6 -> 20x20x8` still changes by `0.020163733436403874` at 100 K, and the overall five-mesh maximum remains `0.513481935500736`. MP48 is not Ding `C_src`.
DEPENDENCY_UNLOCKED: Finest-pair diagnostic only; no downstream dependency unlock.
STATUS: `BLOCKED_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Canonical artifact now records all five meshes and distinguishes route-wide, fine-tail, and finest-pair convergence. Full gate SHA-256 `f0cb644215f356b0b2e6b925bbc8bfa0e9fa364a0c33275133fbe70fd0624c1e`.
EQUATION_OR_MAPPING: `C_src^mesh(T) = N_A/N_q * sum_(q,mu) c_mu(q,T)`; no `Delta_Tq = alpha_Phi_K * Delta_Phi
rho_model = N_C M_C / (N_A V_primitive)
c_v,implied = C_src / rho_model` calibration is emitted.
VERIFICATION: Five-mesh source audit, focused `3 passed`, and full Topic 13 `176 passed, 625 deselected`; no fit or holdout access.
CONTROLLING_BLOCKER: `mp48_force_constant_C_src_mesh_convergence_missing` plus Ding source/material mapping and full thermal bridge blockers.
NEXT_ACTION: Seek an accepted Ding-compatible numeric PBTE payload/reproduction rather than treating the finest pair as sufficient.
CLAIM_BOUNDARY: Internal convergence diagnostic only; not Ding validation, alpha calibration, or Full Topic 13 closure.

## NIST AXM-5Q1 Same-Grade Density Boundary (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY`.
WHAT_IS_ACTUALLY_CLOSED: A same-grade AXM-5Q1 density row is source-locked at `1721 kg m^-3` (approximately 20 C, hydrostatic weighing), and its `+/-0.1%` source precision is explicitly kept separate from standard uncertainty.
WHAT_REMAINS_OPEN: Density uncertainty, direct volumetric `c_v`, same-state `C_p/C_v`, alpha_V/K_T pairing, Ding material mapping, base-Phi, and independent alpha remain open.
DEPENDENCY_UNLOCKED: Same-grade density availability only; no downstream dependency unlock.
STATUS: `PASS_SCOPED_NIST_AXM5Q1_DENSITY_SOURCE_BOUNDARY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added and integrated the NIST density package/audit; full gate SHA-256 `2030316aacac4f654b4ead1b1b59d4c034e9cd38596bb3243f16e66f10c1b4f7`.
EQUATION_OR_MAPPING: `c_p^V=rho*c_p`; density is an input boundary, not `c_v`, `C_src`, or alpha.
VERIFICATION: Focused tests `2 passed`; source/hash/precision boundary pass; no fit or Xie 2026 access.
CONTROLLING_BLOCKER: `density_uncertainty_not_source_locked` and the remaining `c_v`, Ding, alpha, bridge, transport, and mapping blockers.
NEXT_ACTION: Obtain uncertainty-grade density or direct volumetric `c_v`/same-state `C_p` evidence.
CLAIM_BOUNDARY: Same-grade density source availability only; not calibration, prediction, external validation, or Full Topic 13 closure.

## Latest Source-Route Boundary: MP48 Deep Fine-Tail Convergence (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` refinement for `T13_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; complete route remains blocked.
WHAT_IS_ACTUALLY_CLOSED: Seven source-traceable MP48 meshes are now evaluated. The fine-tail `20x20x8 -> 25x25x10 -> 30x30x12 -> 35x35x14` passes the unchanged `0.01` criterion at maximum `0.00653145749584183`; the finest pair passes at `0.0007133166616816178`.
WHAT_REMAINS_OPEN: Route-wide adjacent-mesh convergence still fails at `0.5134819354919335`, so the independent route is not accepted as Ding PBTE `C_src`. Material mapping, uncertainty, base-Phi SI anchor, independent `alpha_Phi_K`, bridge/beta, EOS/transport/KMS/entropy, and dimensional observable closure remain open.
DEPENDENCY_UNLOCKED: Fine-tail diagnostic only; no downstream dependency unlock.
STATUS: `BLOCKED_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Canonical artifact SHA-256 `3b7832a7c7562de91be77cba0291b8dd0fdf40819a90b46d75e95f0d9a56a133`; full gate SHA-256 `09ad63424a483a338346c43c2f2de1d0713ddabff15e1f80f586b9973e48e764`; major-result register SHA-256 `63b877fdf0014bcf75f03c0476fef1edfa9858e3ea2986392e34cbd1aa997d00`; dependency gate SHA-256 `566566bd47547190572b9bcdc3906e3aabce08f54cf3646cb26f8f8ebf5c9662`.
EQUATION_OR_MAPPING: `C_src^mesh(T) = N_A/N_q * sum_(q,mu) c_mu(q,T)`; no UET base-Phi calibration is emitted.
VERIFICATION: Seven-mesh source audit and zero-negative-mode checks pass; route-wide convergence remains false. Focused tests `2 passed`; Topic 13 regression `177 passed, 625 deselected`; no fit, target, holdout, or alpha access.
CONTROLLING_BLOCKER: `mp48_force_constant_C_src_mesh_convergence_missing` for the complete route, plus the full bridge blockers.
NEXT_ACTION: Keep the fine-tail result as a comparator and obtain a Ding-compatible PBTE payload or accepted same-regime reproduction with uncertainty.
CLAIM_BOUNDARY: Internal harmonic convergence diagnostic only; not Ding validation, UET transport, alpha calibration, external validation, or Full Topic 13 closure.

### 2026-08-13 - BIPM graphite specific-heat comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_BIPM_SPECIFIC_HEAT_CP_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: BIPM-2006/01 is archived from the OSTI mirror with raw PDF SHA-256 `2c491c94adb3f70f4b1ba915259f0a1d2f4788e072e99c8d34a87f964f69ce42`. The report's sample-H relation gives `c_p=710.6 +/- 0.7 J kg^-1 K^-1` at 22 deg C, and the same report gives bulk density `1780 +/- 2 kg m^-3`; the source-locked volumetric comparator is `c_p^V=1264868 +/- 1890.0596392706766 J m^-3 K^-1` under independent first-order propagation.
WHAT_REMAINS_OPEN: This is `c_p^V`, not `c_v^V`; the `T*alpha_V^2*K_T` correction, Ding TTG material-regime mapping, numeric Ding `C_src`, base-Phi SI anchor, and independent `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: Source-locked ultra-pure graphite volumetric `c_p` comparator only; no `c_v`, Ding, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_BIPM_CP_COMPARATOR_CV_OPEN`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added the BIPM source package `ab120653076ac3d44e45235705ca505e923096be78078c1ee261dbe72bdea2c7`, audit artifact `6d71952c1ab294d3e391ca257abd49cde10c534f2265612561efacd4e2cc8a4d`, full-gate integration `0dc0e1b1508dbd94fdc9db80d00c6f2cb8237e1447294c4a1d7361e65a672216`, and register/dependency synchronization `2cf90fa93ed3f5339cf897c31905122149108e24404a71c187e0d8d9af7453d6` / `55914eda90af1c18f56619ea4ac4ba3af2b6ffb57cbe99c3b6ae32cbf039fbcb`.
EQUATION_OR_MAPPING: `c_p^V=rho*c_p`; `c_v^V=c_p^V-T*alpha_V^2*K_T`. No `c_v`, `C_src`, `Delta_Tq=alpha_Phi_K*Delta_Phi`, or alpha calibration is emitted from this comparator.
VERIFICATION: Raw hash, source locators, units, 22 deg C scope, density and `c_p` uncertainty, volumetric conversion, holdout non-access, no target fit, and no alpha fit pass.
CONTROLLING_BLOCKER: `alpha_V_K_T_c_v_and_Ding_material_regime_mapping_missing`; the full gate also remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Acquire same-regime `alpha_V` and `K_T` or a direct volumetric `c_v` source with uncertainty; keep this comparator out of calibration and holdout paths.
CLAIM_BOUNDARY: Source-traceable BIPM ultra-pure graphite `c_p^V` comparator only. It is not `c_v`, not Ding/HOPG validation, not UET transport, not an alpha calibration, and not Full Topic 13 closure.

### 2026-08-13 - IAEA manufactured-graphite table-derived c_v comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_IAEA_GRAPHITE_TABLE_CV_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The IAEA-hosted Graphite Engineering Handbook is archived with raw PDF SHA-256 `91e9d84e5d1828ab1028bf0e5fec0743fe1fb49e416b9e6305edf2f71a30a28a`. Table 4.11 at 300 K gives `c_p=0.1723`, `Delta c_p=0.0017`, `c_w=0.00069`, and `c_e=0.00009 cal g^-1 K^-1`; the declared table relation `c_v=c_p-c_w-c_e` gives `c_v=0.17152 cal g^-1 K^-1 = 717.63968 J kg^-1 K^-1`.
WHAT_REMAINS_OPEN: The handbook's `Delta c_p` is a probable-error envelope, not a standard uncertainty for `c_v`; `c_w` depends on density, expansion, and compressibility; no same-grade density/volumetric conversion or Ding material match is established.
DEPENDENCY_UNLOCKED: Source-traceable manufactured-graphite mass-specific lattice `c_v` comparator only; no volumetric `c_v`, Ding `C_src`, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_IAEA_TABLE_CV_COMPARATOR_UNCERTAINTY_OPEN`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added IAEA source package `568853f10f4ef1fc75b4ebed5851240ac8a94f05a5d72cf10af1a2d94bb62e09`, audit `1af3c1c9e81a44b6837cad8d47651f92e167f613743a667e8d3c823cdaaf213c`, full-gate integration `5c0b34226599fe39537da1afc6325d047048c7db479b308c19d4d8e8e10f399d`, and registry/dependency synchronization `21432d3fb5e0cfb1ef4566f04fdac039ac86ede0acf8c1ff17133bad121e5526` / `5b7421c9ad0d09ffbd5c2bba255b07358a803a4908a190578f672b405e4339d9`.
EQUATION_OR_MAPPING: `c_p=c_v+c_w+c_e`; `c_v=c_p-c_w-c_e`. No volumetric `c_v`, `C_src`, `Delta_Tq=alpha_Phi_K*Delta_Phi`, or alpha calibration is emitted.
VERIFICATION: Raw hash, Table 4.11 locator, 300 K row, formula reconstruction, calorie conversion, uncertainty boundary, material mismatch, holdout non-access, no target fit, and no alpha fit pass.
CONTROLLING_BLOCKER: `cv_uncertainty_density_volumetric_conversion_and_Ding_material_regime_mapping_missing`; the full gate also remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Acquire source-grade `c_v` uncertainty plus same-grade density or direct volumetric `c_v`; keep the table-derived comparator out of calibration and holdout paths.
CLAIM_BOUNDARY: Source-traceable IAEA table-derived manufactured-graphite mass-specific lattice `c_v` comparator only. It is not volumetric `c_v`, not Ding/HOPG validation, not UET transport, not an alpha calibration, and not Full Topic 13 closure.

### 2026-08-13 - Ding/comparator material-regime boundary lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_DING_MATERIAL_REGIME_BOUNDARY`.
WHAT_IS_ACTUALLY_CLOSED: Ding's supplementary source locks a natural graphite crystal TTG specimen and reports grain characterization at p. 11 (`382 +/- 270 um^2` average grain area; typical grain size greater than 20 um). The lane compares this target with MP48 ideal AB graphite, NIST AXM-5Q1, BIPM Carbone Lorraine graphite, IAEA manufactured graphite, and Huang isotopically purified ribbons; none is declared equivalent without an explicit material/state/PBTE mapping.
WHAT_REMAINS_OPEN: Numeric Ding `C_src`, same-grade volumetric heat-capacity uncertainty, and an accepted material/state/PBTE equivalence mapping remain open. Comparator `c_v`/`c_p` values remain comparison-only.
DEPENDENCY_UNLOCKED: Material-equivalence no-go only; no Ding `C_src`, alpha calibration, bridge, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_DING_MATERIAL_REGIME_BOUNDARY_NO_GO`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added material-boundary source package `c379002e67b4ee3f27e784999bf65f6becb4094f9f101be2360b528c0bfb6fc8`, audit `64742790afda02aae657ceed146c6a88c235185066ff283f067ed52c376d14e0`, full-gate integration `cff87f9e0341944943504cb099f5099b104b564aeec34ef13e0939990f900b52`, and registry/dependency synchronization `381df20de9d3d987330a25da6d0a0f10bd80186b092a8def8ca5319d0ab16801` / `9b8bf946bc2c85453194dc946cc6aa09148505cb4edb8d59d81a68400926390a`.
EQUATION_OR_MAPPING: `C_src(T)=sum_mu c_mu(T)` remains Ding's source PBTE quantity; `material_regime_equivalent_to_Ding` is explicitly `false` for all archived comparator lanes.
VERIFICATION: Ding raw hash and p. 11 locator, comparator package identity, explicit equivalence rule, no silent relabeling, no fit, no alpha calibration, and no Xie 2026 access pass.
CONTROLLING_BLOCKER: `material_regime_mapping_to_TTG_not_closed` is now a named no-go boundary; numeric Ding `C_src`, source-grade volumetric uncertainty, independent `alpha_Phi_K`, bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping remain controlling.
NEXT_ACTION: Obtain an authorized Ding mode-resolved PBTE payload or a genuinely matched same-material/state reproduction; do not substitute MP48 or graphite-grade comparators.
CLAIM_BOUNDARY: This closes only the evidence boundary against silent material substitution. It is not a claim that the comparator physics is false, not Ding validation, and not Full Topic 13 closure.

### 2026-08-13 - IAEA c_v uncertainty and volumetric boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_IAEA_CV_UNCERTAINTY_BOUNDARY`.
WHAT_IS_ACTUALLY_CLOSED: The IAEA Table 4.11 comparator remains source-traceable, but its `Delta c_p` is a probable-error envelope rather than a standard uncertainty for derived `c_v`; the thermoelastic correction and volumetric conversion have no source-locked same-row uncertainty contract.
WHAT_REMAINS_OPEN: Uncertainty-grade volumetric `c_v` or Ding `C_src` is still missing; the comparator cannot be used as a Ding material substitution or alpha calibration.
DEPENDENCY_UNLOCKED: The IAEA uncertainty route is closed as a scoped no-go; no Core, Gravity, transport, or alpha dependency is unlocked.
STATUS: `PASS_SCOPED_IAEA_CV_UNCERTAINTY_BOUNDARY_NO_GO`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added source package `43c28e1bb5f33e7c10261e2d3a84a31c54b55fa8d2413f44c5c9e5461c3e6fd5`, boundary audit `a51c4318a72603c521fd9c9aaa48f759a95054a9da00707427c59cd3abe34b3e`, full-gate projection `435accef32d016f951cf16873d68c1ad34a0cb83e8fccd31eba5055900b37864`, and registry/dependency synchronization `cface8245d94f3158abaae493c9611d71fde8be3a237c1609aac476b8f4c86bf` / `ffedbac3779a8c952d90c91a95e3fcd20da2deec7f10f486a15a84a29bd8fe4e`.
EQUATION_OR_MAPPING: `c_p=c_v+c_w+c_e`; `c_v^V=rho*c_v` requires same-regime density and uncertainty. No uncertainty is inferred from `Delta c_p`.
VERIFICATION: Raw hash, source locators, uncertainty boundary, no volumetric emission, Ding non-substitution, holdout non-access, and no fitting pass.
CONTROLLING_BLOCKER: `iaea_table_derived_cv_uncertainty_and_volumetric_conversion_not_source_locked`.
NEXT_ACTION: Acquire direct uncertainty-grade same-regime volumetric `c_v` or a same-state `Cp`/density/thermoelastic package; keep this comparator out of calibration and Ding `C_src` paths.
CLAIM_BOUNDARY: Scoped source no-go only; this does not close `alpha_Phi_K`, the UET bridge, EOS/transport/KMS/entropy, or Full Topic 13.

### 2026-08-13 - Phonix mp-47 graphite harmonic comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_PHONIX_MP47_GRAPHITE_HARMONIC_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The Phonix `mp-47` row is archived with immutable dataset revision `284bddebbd144ae3e3f93474dc05e4658417d09f`, exact row identity, primitive volume, graphite space group, frequency/DOS arrays, q-mesh, and source hashes. Identity, shape, grid, sign, provenance, and holdout-isolation checks pass.
WHAT_REMAINS_OPEN: Phonix reports `phdos` in source arbitrary units and supplies no standard uncertainty for a unitful `c_v`; it is not a Ding natural-graphite TTG/PBTE material match and does not provide Ding mode-resolved `C_src` or an independent `alpha_Phi_K`.
DEPENDENCY_UNLOCKED: Source-locked graphite harmonic comparator only; no Ding source, volumetric `c_v`, alpha, transport, Core, Gravity, or Galaxy dependency unlock.
STATUS: `PASS_SCOPED_PHONIX_GRAPHITE_HARMONIC_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added raw snapshot `cea9711b09f455375a5f9182c295588b98d498fb09af4660af6fb7dce4fdaff1`, source package `f08bc1d0ac5142abb4f1916c0caaf79c89d3ef414979edfeef9365f4690c1b76`, comparator audit `57550435f987dff1a38601f20dfd94c3a43b1aca0af2aea8216320c2b0443130`, full-gate projection `b6216d47149435624c84c3370e522d571e3356ba305eeb1748acb41cc83d0578`, and register/dependency synchronization `e98e16cd6e968845b8ef196271c3aecd5c2bd8dfe810b2a08ac9890dea2600e4` / `5502ca70042021c1038887dab8a23341cb75d093d4314366e3a71f2b436cdf8f`.
EQUATION_OR_MAPPING: Harmonic kernel boundary `c_mu(T)=k_B*x_mu^2*exp(x_mu)/(exp(x_mu)-1)^2`; only `I_DOS=integral[phdos_source(nu)dnu]` in source units is reported. No volumetric `c_v`, Ding `C_src`, `Delta_Tq=alpha_Phi_K*Delta_Phi`, or alpha value is emitted.
VERIFICATION: Immutable revision, exact `mp-47` locator, raw/package hash, P6_3/mmc identity, 51-bin shape/grid, nonnegative DOS, arbitrary-unit boundary, no invented uncertainty, no target/alpha fit, and Xie 2026 holdout isolation pass.
CONTROLLING_BLOCKER: `phonix_summary_dos_units_and_uncertainty_not_sufficient_for_volumetric_cv`; full gate also remains controlled by Ding `C_src`, independent `alpha_Phi_K`, non-circular bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Obtain a unitful uncertainty-grade same-regime `c_v` or authorized Ding PBTE payload/accepted reproduction with material-state mapping; retain Phonix as comparison only.
CLAIM_BOUNDARY: Source-provenance and harmonic-comparator lane only. This is not Ding validation, UET transport validation, alpha calibration, external validation, or global UET closure.

### 2026-08-13 - Oxford TGS Figure 1 numeric-row comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_OXFORD_TGS_NUMERIC_ROWS_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The archived MATLAB v7.3 Figure 1 source is extracted at the source-selected map point (`ph=39.0`, `pv=3.95`) as 10 trace identities with 2002 samples per trace. The source time/intensity labels and `yy1 - yy` operation are preserved without fitting.
WHAT_REMAINS_OPEN: The source does not declare the selected material and temperature, gives intensity rather than a unitful thermal observable, and does not provide Ding PBTE `C_src`, volumetric `c_v`, or a base-Phi amplitude.
DEPENDENCY_UNLOCKED: Oxford numeric comparator lane only; no Ding source, `c_v`, `alpha_Phi_K`, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_OXFORD_TGS_NUMERIC_ROWS_SOURCE_LOCKED_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added compressed numeric rows `6e67be5794ed10ebb81ca1ca5b513ee1232b64f6040d7413c81332cf61250454`, extraction manifest `25c0d7110843f26383433cf995ff2a2aad743fd1badccff4d0501e0010fd9817`, numeric-row audit `80020df66e0c03ceaf02a9e112f56308f4bf0ea753fe28a421e90dd4b487c8df`, full-gate projection `42163939230b11f13d07a135dd99e15ac9488c8a0579bd576f46cc9d9c8d9dbd`, and register/dependency synchronization `5deb4611a49ebabea6897d297edd913be81d672b257b968f057e0366f315bc0c` / `48a16f52964923bb499de187f5ef3710e1d6f5d61708db59069abe68af34d025`.
EQUATION_OR_MAPPING: `y_source(t) = yy1(t) - yy(t)`; source fit remains outside this artifact. No `c_v`, Ding `C_src`, `Delta_Tq=alpha_Phi_K*Delta_Phi`, or alpha value is emitted.
VERIFICATION: HDF5 shape/transpose contract, raw source hash, 20,020 row count, unique trace/sample identity, finite values, monotone time, exact subtraction, no fit, no target access, and Xie 2026 holdout isolation pass.
CONTROLLING_BLOCKER: `material_temperature_and_physical_thermal_mapping_missing`; full gate remains controlled by Ding `C_src`, independent `alpha_Phi_K`, dimensional Phi anchor, bridge/beta, EOS/transport/KMS/entropy, and source-grade `c_v` requirements.
NEXT_ACTION: Retain the extracted rows as a comparator and continue with a permitted source that supplies physical heat capacity or an independent base-Phi/SI anchor; do not relabel Oxford intensity as temperature.
CLAIM_BOUNDARY: Source-locked Oxford TGS numeric-row comparator only. It is not Ding validation, UET transport validation, alpha calibration, external validation, or Full Topic 13 closure.

### 2026-08-13 - DeSorbo Ceylon graphite numeric Cp comparator lane

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_DESORBO_1955_CEYLON_GRAPHITE_CP_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: The official NIST SRD 69 graphite table is archived with raw HTML SHA-256 `2e9955e1a176adc93ee152aceb390da67f561bf5ba0a4c741e9936a552f1dc1b`. The row attributed to DeSorbo 1955 records Ceylon natural graphite `Cp=7.841 J mol^-1 K^-1` at `298.15 K`; the primary paper identity, locator, and reported accuracy boundary are preserved.
WHAT_REMAINS_OPEN: The reported accuracy is not promoted to standard uncertainty; no source-locked density, volumetric `c_v`, `C_src`, or Ding TTG material equivalence is available from this lane.
DEPENDENCY_UNLOCKED: Ceylon natural-graphite numeric `Cp` comparator only; no `c_v`, Ding, alpha calibration, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_DESORBO_CEYLON_GRAPHITE_CP_SOURCE_LOCKED_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added source package `3bf9cebd1b3129f9b0f1cd66b49e16c2d7743059a207ed203048894abb6a746b`, audit artifact `bccbb8f7d2895c8f4e5c86c53a39690ac739e8d621673ba109d1dc3ca795f399`, full-gate projection `87284e7d5ca90d134926aa77be4b1188a19a422e96f4865a53c6e12441af77a1`, and register/dependency synchronization `d039c81ecc170a5667d1328b1cd820371ff67c7d335186b7996165ff24c76186` / `be5fcf16fcbb4aa82984af9b705b3777eebadb7ce691b5184077e381975bf35b`.
EQUATION_OR_MAPPING: `Cp,solid^m(298.15 K)=7.841 J mol^-1 K^-1`; downstream `c_v^V` conversion remains open. No `Delta_Tq=alpha_Phi_K*Delta_Phi` calibration is emitted.
VERIFICATION: Raw hash, NIST row identity, source locator, units, no-fit/no-target policy, no-Xie policy, no-alpha policy, and non-promotion of accuracy to standard uncertainty pass.
CONTROLLING_BLOCKER: `standard_uncertainty_density_and_Ding_material_mapping_missing`; full Topic 13 is still controlled additionally by Ding `C_src`, independent `alpha_Phi_K`, physical bridge/beta, EOS/transport/KMS/entropy, and base-Phi SI mapping.
NEXT_ACTION: Acquire source-grade density and standard uncertainty for a material regime demonstrably compatible with Ding TTG, or retain this row as comparison-only evidence.
CLAIM_BOUNDARY: Source-traceable natural-graphite molar `Cp` comparator only. It is not volumetric `c_v`, not Ding/PBTE validation, not UET calibration, not external validation, and not Full Topic 13 closure.

### 2026-08-13 - Xie 2026 holdout access-semantics correction

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_XIE_2026_HOLDOUT_ACCESS_CONTROL`.
WHAT_IS_ACTUALLY_CLOSED: The current audit now distinguishes metadata-only observation from source-data consumption. No numeric holdout payload, source rows, curves, or source bytes were consumed by Topic 13 research paths, and no holdout-derived fit, tuning, calibration, threshold adjustment, or claim promotion occurred.
WHAT_REMAINS_OPEN: Xie 2026 remains a locked holdout and must not be used for calibration, tuning, fitting, or threshold adjustment.
DEPENDENCY_UNLOCKED: Holdout-integrity reporting may proceed from the canonical access audit; no thermal-bridge, alpha, prediction, or external-validation dependency is unlocked.
STATUS: `PASS_HOLDOUT_DATA_UNCONSUMED_METADATA_ONLY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/core/artifacts/t13_xie_2026_holdout_access_audit.json` (SHA-256 `c3185da0a233894d7f338138bbe6acee287194e1852a80e40b0b5f6f2134e21b`), wired it into the active full-gate and Ding source-mapping verifiers, and synchronized the major-result register/dependency gate.
EQUATION_OR_MAPPING: Access contract is `metadata_only_observed != numeric_payload_consumed`; the locked rule is
umeric_payload_consumed = used_for_fit = used_for_tuning = used_for_calibration = used_for_threshold_adjustment = false`.
VERIFICATION: Canonical holdout audit and full-gate evidence hash agree; full-gate holdout integrity is `PASS` with metadata-only observation recorded and all numeric-consumption controls false. Focused holdout/acceptance/KMS tests pass (`7 passed`).
CONTROLLING_BLOCKER: No blocker remains in the access-control lane. Full Topic 13 remains controlled by Ding-regime `C_src`, independent `alpha_Phi_K`, dimensional/base-Phi anchor, bridge/beta, EOS/transport/KMS/entropy, and source uncertainty blockers.
NEXT_ACTION: Keep Xie 2026 locked and continue only with an authorized Ding numeric package or an accepted independent same-regime PBTE reproduction, plus an independent base-Phi SI anchor/calibration.
CLAIM_BOUNDARY: This closes an access-control audit only. It is not evidence for `C_src`, `alpha_Phi_K`, temperature prediction, external validation, or global UET closure.

### 2026-08-13 - NIMS graphite LTC source-route no-go

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_NIMS_GRAPHITE_LTC_ROUTE_NO_GO`.
WHAT_IS_ACTUALLY_CLOSED: The public NIMS lattice-thermal-conductivity collection was searched with exact `C`, `Graphite`, `Carbon`, `graphite`, and `specimen:graphite` terms. Exact graphite/carbon searches returned zero records; the 349-row carbon full-text result was scanned across 35 pages with zero elemental-carbon formula `C` material records. The two public API `specimen:"graphite"` records belong to `MDR XAFS DB`, not the LTC collection.
WHAT_REMAINS_OPEN: Ding numeric `C_src` or a permitted same-regime PBTE reproduction with mode-resolved rows, SI units, uncertainty, convergence, and material-state mapping remains open. The independent `alpha_Phi_K` calibration remains open. :codex-annotation{index="1"}
DEPENDENCY_UNLOCKED: NIMS graphite-source route exclusion only; no `C_src`, alpha, bridge, transport, Core, Gravity, or Galaxy unlock.
STATUS: `PASS_SCOPED_NIMS_GRAPHITE_ROUTE_NO_GO`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/core/artifacts/t13_nims_graphite_ltc_route_no_go.json` (SHA-256 `47814c603057bd8dede2cbebcf069e820ff389566612402f23997bd3acc529ff`), integrated it into the full-gate source-package lane, and added a focused test. The regenerated full gate is `1a6704861fc01734641f7af14eb0ae2663fae4d1a271d69eb326242d286f0f42`.
EQUATION_OR_MAPPING: Required source quantity remains `C_src(T)=sum_mu c_mu(T)` with `C_src` in `J m^-3 K^-1`; `Delta_Tq=Delta_u_ph/C_src`. This route emits no numeric `C_src` and no `Delta_Tq=alpha_Phi_K*Delta_Phi` calibration.
VERIFICATION: Public NIMS collection/API metadata was source-located, query outcomes and response hashes were recorded, no numeric research payload was consumed, no fit/tuning/alpha emission occurred, Xie 2026 was not accessed, and focused source-route tests passed (`6 passed`).
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`; full Topic 13 remains additionally controlled by the dimensional Phi anchor/independent alpha, bridge/beta, EOS/transport/KMS/entropy, and uncertainty blockers.
NEXT_ACTION: Pursue the Ding author route or another permitted same-regime PBTE source. Do not reopen the NIMS route unless its collection metadata changes, and do not substitute XAFS, harmonic DOS, graphene, or unrelated graphite comparators.
CLAIM_BOUNDARY: This closes only the NIMS source-route no-go. It is not `C_src` evidence, an independent alpha calibration, TTG prediction, external validation, Core closure, or global UET closure.

## Latest MP48 Fine-Tail Acceptance Policy (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`; independent MP48 fine-tail convergence is closed, while full Topic 13 remains blocked.
WHAT_IS_ACTUALLY_CLOSED: The three-pair fine tail passes at `0.00653145749584183` under unchanged tolerance `0.01`; coarse route-wide sensitivity `0.5134819354919335` remains visible as a diagnostic.
WHAT_REMAINS_OPEN: Ding material/mode-resolved `C_src`, uncertainty, base-Phi SI anchor, `alpha_Phi_K`, bridge/beta, and physical EOS/transport/KMS/entropy.
STATUS: `PASS_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Fine-tail acceptance is now explicit and machine-readable. Artifact `585ebc548e5354c2c4905af9b3efca5f9c9d1365527046d4103751ce7869b45d`; full gate `e04bed7abbc38801fcab7d302f31f207c4f85685fe72a12f82127e29b96f0f56`.
EQUATION_OR_MAPPING: `C_src^mesh(T)=N_A/N_q*sum_(q,mu)c_mu(q,T)`; no UET dimensional calibration is emitted.
VERIFICATION: Fine-tail audit and gate regeneration pass without fit or holdout access.
CONTROLLING_BLOCKER: `Ding_material_regime_and_mode_resolved_C_src_acceptance_missing`.
NEXT_ACTION: Obtain accepted Ding-compatible PBTE evidence.
CLAIM_BOUNDARY: Comparator-only; not Ding validation, alpha calibration, or Full Topic 13 closure.

## Latest MP48 Acceptance Controller Synchronization (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for MP48 fine-tail convergence; `PARTIAL` for Full Topic 13.
WHAT_IS_ACTUALLY_CLOSED: The acceptance contract records a passing fine-tail mesh controller.
WHAT_REMAINS_OPEN: Ding material/PBTE equivalence, numeric `C_src`, base-Phi SI anchor, `alpha_Phi_K`, and full bridge closure.
STATUS: `PASS_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; Full Topic 13 `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Acceptance, full gate, register, and dependency hashes are synchronized.
EQUATION_OR_MAPPING: Harmonic mesh sum only; no Ding relabeling and no UET dimensional calibration.
VERIFICATION: Contract guards pass; Xie 2026 numeric holdout remains excluded.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.
NEXT_ACTION: Obtain permitted same-regime PBTE evidence.
CLAIM_BOUNDARY: Comparator-only; not Ding validation, alpha calibration, or Full Topic 13 closure. Full gate `c189beba37a32ebcc06f15eb4ea39558dcadb36c74e3a469e7f4bdd640f62427`.

## Latest MP48 Full-Gate Narrative Drift Repair (2026-08-13)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for MP48 convergence; `PARTIAL` for Full Topic 13.
WHAT_IS_ACTUALLY_CLOSED: MP48 is described as a convergence pass, not a mesh no-go.
WHAT_REMAINS_OPEN: Ding source acceptance, alpha, dimensional map, bridge/beta, and physical transport.
STATUS: `PASS_MP48_FORCE_CONSTANT_C_SRC_MESH_CONVERGENCE`; Full Topic 13 `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Full-gate narrative and generated register were synchronized.
EQUATION_OR_MAPPING: Harmonic mesh sum only; no Ding relabeling.
VERIFICATION: Obsolete phrase scan clean; holdout and fit guards unchanged.
CONTROLLING_BLOCKER: `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`.
NEXT_ACTION: Obtain permitted same-regime PBTE evidence.
CLAIM_BOUNDARY: Comparator-only; not Ding validation or Full Topic 13 closure. Full gate `284664c485e308f6311d2f85443c83c0937dac7518c891854216244e0d05c8c2`.

## Formal Finite-Temperature Two-Sector Thermodynamic Split

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FORMAL_TWO_SECTOR_THERMODYNAMIC_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The declared natural-unit O(2) finite-temperature EOS now has an explicit tree-condensate plus thermal-quasiparticle pressure split, with sector-wise charge, entropy, energy, and susceptibility identities verified on normal and condensed branches. The normal-sector charge derivative is explicitly not a Landau normal mass density.
WHAT_REMAINS_OPEN: Transverse normal-current response, interacting finite-temperature self-energy/renormalization, physical Kubo provenance, microscopic SK/KMS matching, heat-flux and entropy-production closure, dimensional Phi mapping, independent `alpha_Phi_K`, and Ding-compatible `C_src` remain open.
DEPENDENCY_UNLOCKED: Formal thermodynamic two-sector lane only; no physical two-fluid transport, SI, alpha, Full Topic 13, Core, Gravity, or external-validation unlock.
STATUS: `PASS_FORMAL_TWO_SECTOR_THERMODYNAMIC_CONSISTENCY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`.
WHAT_CHANGED: Added `docs/core/uet_o2_formal_two_sector_thermodynamics.py`, its audit artifact and focused tests, then linked the result into the full gate and major-result registry.
EQUATION_OR_MAPPING: `p_2sector = p_condensate + p_normal`;
_i = partial_mu p_i`; `s_condensate = partial_T p_condensate = 0`; `epsilon_i = -p_i + T*s_i + mu*n_i`; `chi_i = partial_mu n_i`. No transverse current or transport coefficient is inferred.
VERIFICATION: Formal audit passed with zero failed checks; focused tests passed (`2 passed`); full gate retains the existing 10 blockers; Xie 2026 remains unconsumed. A broader EOS test still has a pre-existing assertion-shape failure in `test_topic13_finite_temperature_quasiparticle_eos.py`.
CONTROLLING_BLOCKER: `transverse_normal_current_response_or_Landau_normal_density_missing`.
NEXT_ACTION: Derive or source-lock a state-matched transverse normal-current response from a declared interacting finite-temperature action, while keeping this thermodynamic split separate from physical Kubo and SI calibration.
CLAIM_BOUNDARY: Formal natural-unit thermodynamic consistency only. This is not a complete finite-temperature two-fluid transport theory, not `alpha_Phi_K` calibration, not TTG prediction, not external validation, and not global UET closure.
EVIDENCE_HASHES: module `a260f9c50a8685a6c5506f6e5ff1602cfcd2c2bcf1b5f79d3faf81803a4915c9`; audit `0e1bd35153563af720b6a27badf8ebbbb4ab37fd0301c8b764f7935d36f18efa`; full gate `07c066e0427729d562218fd81f82bea4b1d6cfb4c59ee71c8974baecb8c8f22f`.

## Formal Static Transverse Quasiparticle Response

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FORMAL_TRANSVERSE_RESPONSE_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The declared normal and condensed O(2) quasiparticle branches now have a positive static Doppler-response integral and a tree condensate phase-stiffness witness in natural units. Low-temperature response decreases on both representative branches, and the result is explicitly bounded away from retarded Kubo and Landau normal-density claims.
WHAT_REMAINS_OPEN: Retarded physical Kubo matching, interacting finite-temperature self-energy/renormalization, microscopic SK/KMS matching, heat-flux and entropy-production closure, dimensional Phi mapping, independent `alpha_Phi_K`, and Ding-compatible `C_src` remain open.
DEPENDENCY_UNLOCKED: Formal static transverse response lane only; no physical Kubo, SI, alpha, Full Topic 13, Core, Gravity, transport, or external-validation unlock.
STATUS: `PASS_FORMAL_STATIC_TRANSVERSE_QUASIPARTICLE_RESPONSE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`.
WHAT_CHANGED: Added `docs/core/uet_o2_formal_transverse_response.py`, its audit artifact and focused tests, then linked the result into the full gate and major-result registry.
EQUATION_OR_MAPPING: `E_a(k;v)=E_a(k)+k.v+O(v^2)`; `chi_perp_qp=(1/3) sum_a integral[d^3k/(2*pi)^3] k^2[-partial_E n_B(E_a)]`; `f_s_tree=Z*q/lambda` for `q>0`. No retarded Kubo coefficient is emitted.
VERIFICATION: Formal audit passed with zero failed checks; focused transverse/two-sector tests passed (`4 passed`); full gate retains the existing 10 blockers; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: `retarded_physical_Kubo_match_missing`.
NEXT_ACTION: Match the formal transverse response to a state-matched retarded microscopic Kubo record; retain this result as a natural-unit static witness until that match exists.
CLAIM_BOUNDARY: Formal static response witness only. This is not a physical Kubo match, Landau normal density, complete two-fluid transport theory, SI calibration, TTG prediction, external validation, or global UET closure.
EVIDENCE_HASHES: module `bb30501e3486323dc56e814b5855a66383949a71029b4683cd4bc9931c6bbd58`; audit `84111a21c71ed9d1c033117a552e925cc40db535ada9f1385eee3236df56d675`; full gate `94152d772dd103d419f44d9715631d01128d2a6c1155344154968c76b03865fd`.

## Hartree Normal-Branch One-Sided Stability Boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_HARTREE_NORMAL_STABILITY_BOUNDARY_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The existing natural-unit Hartree gap equation now yields a one-sided normal-branch stability boundary from `r_T = M^2 - Z*mu^2 = 0`, with a critical root, regular Bose domain, stable-side and unstable-side residual signs, and quadrature/cutoff convergence.
WHAT_REMAINS_OPEN: The condensed finite-temperature branch, vacuum/microscopic renormalization matching, full two-fluid EOS, retarded physical Kubo, microscopic SK/KMS, entropy-current and heat-flux closure, dimensional Phi mapping, independent `alpha_Phi_K`, and Ding-compatible `C_src` remain open.
DEPENDENCY_UNLOCKED: Hartree normal-branch one-sided stability-boundary lane only; no renormalized phase transition, physical transport, SI, alpha, Full Topic 13, Core, Gravity, or external-validation unlock.
STATUS: `PASS_ACTION_DERIVED_HARTREE_NORMAL_ONE_SIDED_STABILITY_BOUNDARY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL` with the existing 10 blockers.
WHAT_CHANGED: Added the named stability-boundary module, audit artifact, focused regression tests, full-gate projection, major-result registry entry, dependency-gate synchronization, and this report section.
EQUATION_OR_MAPPING: `M^2=m_eff(Phi)^2+(N+2)*lambda*I_T`; `r_T=M^2-Z*mu^2`; `F(mu_c)=Z*mu_c^2-m_eff(Phi)^2-(N+2)*lambda*I_T(Z*mu_c^2;T,mu_c)=0`. The current determinant convention requires `Z>1` for the regular one-sided witness. No condensed solution or physical coefficient is inferred.
VERIFICATION: Audit passed with zero failed checks; critical `mu_c=0.659465499827425`, residual `1.9709581189353287e-13`, Bose-domain margin `0.08697894909252707`; focused stability/formal-lane tests passed (`7 passed`); full gate and downstream dependency audit remain blocked; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: `condensed_branch_and_renormalized_finite_temperature_phase_transition_missing`.
NEXT_ACTION: Derive or source-lock the renormalized condensed finite-temperature branch and match its retarded Kubo/SK/KMS coefficients; retain this result as a one-sided Hartree diagnostic rather than a phase-transition claim.
CLAIM_BOUNDARY: Natural-unit Hartree normal-branch stability boundary only. This is not a renormalized finite-temperature phase transition, complete two-fluid transport theory, `alpha_Phi_K` calibration, TTG prediction, external validation, or global UET closure.
EVIDENCE_HASHES: module `b3073220c311dd3e68b1925b51d86a1a7aa8aad65d35c931ac34a0340a7991e7`; audit `d2b82c4f8b1429a091d2efeec21c450b5a1af595bf4be660c8ab4f94a1550d85`; full gate `debd78fdeec330f04daf7d3f51bbded829e6a4faf7a47ac90ba6c56e3b09aa75`; register `b87aea00be7f2913f7112a2c661303db34808c74b75999a4c6407bd158ee0b4d`; dependency `f2b4bd7efed8fb8ba92075d1aa1344475e70131434eb353aa36462f60bb541aa`.

## Finite-Temperature Condensed Stationarity Scheme Boundary (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_AS_NO_GO for T13_UET_O2_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE.
WHAT_IS_ACTUALLY_CLOSED: The current value/first-derivative/second-derivative reference anchors do not select a unique finite-temperature condensed stationarity outcome. Scheme A (a=0) has no stationary witness on the declared grid, while anchored scheme B (a=-0.05) has an interior stationary witness with positive mode squares.
WHAT_REMAINS_OPEN: A physical finite-temperature renormalization prescription, a complete condensed/two-fluid EOS, retarded Kubo, microscopic SK/KMS, entropy/heat-flux balance, dimensional Phi mapping, independent alpha_Phi_K, and Ding-compatible C_src remain open. Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
DEPENDENCY_UNLOCKED: Scoped finite-temperature scheme-identifiability no-go only; no physical phase-transition, transport, Core, Gravity, SI, alpha, or external-validation dependency is unlocked.
STATUS: PASS_SCOPED_RENORMALIZED_CONDENSATE_STATIONARITY_SCHEME_DEPENDENCE.
WHAT_CHANGED: Added the scheme-dependence module, audit artifact, focused tests, full-gate projection, closure-register/dependency sync, formula-audit entry, and this report section.
EQUATION_OR_MAPPING: x=A^2; V_vac^R(x)=integral[S(x)-S(x_*)-(x-x_*)S'(x_*)-1/2*(x-x_*)^2*S''(x_*)]; Delta V_a(x)=a*(x-x_*)^3/Lambda_*^2; partial_x Omega=0. Both schemes enforce zero value/first/second derivative of Delta V_a at x_*; Phi remains a natural-unit action response input.
VERIFICATION: Audit passed with zero failed checks; scheme-A boundary derivative=0.011741494171722888, scheme-B stationary x=2.169974254196495, residual=-5.118322432551281e-12, and low/high mode floors=0.0518577599066905/9.9381035857585. Focused suite passed (14 passed); Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: physical_finite_temperature_renormalization_scheme_missing.
NEXT_ACTION: Select the physical finite-temperature scheme by independent microscopic matching or source-backed input; until then retain this as a scoped no-go and do not call the stationary witness a phase transition.
CLAIM_BOUNDARY: This closes only structural non-identifiability under two declared finite local completions. It is not a physical renormalization choice, phase-transition result, two-fluid transport closure, alpha_Phi_K calibration, TTG prediction, external validation, or global UET closure.
EVIDENCE_HASHES: module cc7d69c74fbb1725ca5710b7a8b50d50e6739f977d92a044646fefb7fefa879f; identifiability 26d7a8f2dc54ce8f16771ffac86c5414f71963db2ea5cdd1d026716833598358; audit 884076c8400adc3611bd3a6daa2ef0f35e6721efd0a9506c3acd082049b4ac90; full gate d098e9e7b123a282dfa97f7759e5461e553993dbf436b6fd8b91c418485ab723; register c7f03f1b94935ae2e1091f68687ff192e329d790f176de36a816adccf74669a1; dependency 95747c26cbc189f52817657370c38faf7179a12a60c563c4dd0adead7c3be92b.

## O(2) Renormalized Hartree Normal Functional (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_RENORMALIZED_HARTREE_NORMAL_LANE; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: A declared natural-unit vacuum Taylor-subtracted one-loop term and thermal tadpole now enter one renormalized Hartree normal gap equation. The same stationary functional produces pressure, charge, entropy, energy, susceptibility, and heat-capacity diagnostics.
WHAT_REMAINS_OPEN: Physical finite-temperature scheme selection, the condensed/two-fluid EOS, retarded physical Kubo, microscopic SK/KMS matching, entropy-current and heat-flux balance, dimensional Phi-to-thermal mapping, independent alpha_Phi_K calibration, and Ding-compatible C_src remain open.
DEPENDENCY_UNLOCKED: Renormalized interacting normal Hartree lane only; no condensed/two-fluid, physical Kubo, SI, alpha, Full Topic 13, Core, Gravity, or external-validation unlock.
STATUS: PASS_ACTION_DERIVED_RENORMALIZED_HARTREE_NORMAL_SCHEME; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Added the renormalized Hartree normal module, machine-readable audit artifact, regression test, full-gate projection, and major-result registry sync.
EQUATION_OR_MAPPING: V_vac^R is Taylor-subtracted through second order in mass squared; I_R = partial_M2(V_vac^R + Omega_1^T); M^2 = m_eff(Phi)^2 + (N+2)*lambda*I_R; p_H^R = p_1^T - V_vac^R + (N+2)*lambda*I_R^2/2; n = partial_mu p_H^R; s = partial_T p_H^R; epsilon = -p + T*s + mu*n. Natural units only.
VERIFICATION: Audit passed with zero failed checks. Reference gap residual is -3.750688995496354e-12; functional stationarity residual is 1.439807342311346e-14; charge and entropy finite-difference errors are 1.4726962956415623e-08 and 1.2786594883601454e-08. The combined focused regression suite passed with 24 tests; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: condensate_and_finite_temperature_normal_two_fluid_eos_completion_missing.
NEXT_ACTION: Extend the renormalized functional to a self-consistent condensed branch, then match a state-matched retarded Kubo and microscopic SK/KMS interface without promoting this formal normal lane to physical transport.
CLAIM_BOUNDARY: This closes one declared natural-unit renormalized Hartree normal-branch functional and its stationary identities. It is not a physical finite-temperature renormalization choice, complete two-fluid transport theory, SI Phi map, alpha_Phi_K calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module b90fdb7f3263ad37be366bd624f242d715fbfeef196dafb58fb2a4c38db527cb; audit c8edc3ee3c9c9e29472c07d81271e7087c20c1c4b5281c21e2500cbc5eede5ed; regression aa8cf0ed8b1abb6400089713e393c850ebe52befe0469f8e39436ce0f9b51b3a; full gate 850360b0b0a1b7d3e9e9dcb400914f57efdedea572c88f263c2904c1f29a2c31; register 06c70ea7dfd65474884adde132b8fab52b332e4f0d6988f2e02097a1d7b6be70; dependency 72f77dbe21ae31e5ae01e9f50fc29927ff10d644c050476996ee3112bdab6ad1.

## Condensed Goldstone/Ward Boundary (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_AS_NO_GO for T13_UET_O2_CONDENSED_GOLDSTONE_WARD_NO_GO; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The tree stationary boundary is gapless at zero momentum, but the declared finite-temperature scheme-B stationary witness has a resolved nonzero low-mode gap; its stationarity derivative at the Ward point is also -0.13207100582827716 rather than zero. The current witness therefore cannot be accepted as a symmetry-consistent broken O(2) phase.
WHAT_REMAINS_OPEN: A Ward-preserving condensed construction, physical finite-temperature scheme selection, complete two-fluid EOS, retarded Kubo, microscopic SK/KMS, entropy/heat-flux balance, dimensional Phi map, independent alpha_Phi_K, and Ding-compatible C_src remain open.
DEPENDENCY_UNLOCKED: Goldstone/Ward rejection of the current witness only; no condensed phase, phase transition, two-fluid, transport, Core, Gravity, SI, alpha, or external-validation unlock.
STATUS: PASS_SCOPED_CONDENSED_GOLDSTONE_WARD_BOUNDARY; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Added a machine-readable Ward audit using the existing stationarity and off-shell determinant lanes, linked it to the full gate and major-result registry, and recorded the primary-literature context at https://arxiv.org/abs/0810.5510.
EQUATION_OR_MAPPING: x_boundary=q/lambda and omega_G^2(k=0;x_boundary)=0; the broken-phase Ward requirement is omega_G^2(k=0;x_stationary)=0. The scheme-B witness instead gives omega_G^2(k=0)=0.05185301641084461, while partial_x Omega_scheme_B(x_boundary)=-0.13207100582827716.
VERIFICATION: Audit passed with zero failed checks; tree-boundary low-mode square is 0.0, Ward-point stationarity derivative is -0.13207100582827716, stationary-point residual is -5.118322432551281e-12, and the nonzero gap remains converged across quadrature and cutoff sweeps. Ward suite and integration tests passed (17 passed); Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: ward_preserving_condensed_2PI_or_1N_completion_missing.
NEXT_ACTION: Replace the current stationarity witness with a Ward-preserving symmetry-improved 2PI or controlled 1/N condensed construction, then rerun the finite-temperature EOS and state-matched Kubo/SK-KMS gates.
CLAIM_BOUNDARY: This is a scoped Ward-consistency no-go for the current witness, not a no-go for every future symmetry-improved construction. It is not a phase-transition result, two-fluid closure, alpha_Phi_K calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: audit 968b073d053be004bcf2521ab649fddeee26ccc265dd4d4c9a5aee2b219acd06; verifier ee5e60f82f754ce56563c3f3bf0dd0a7457d062037fff1a3c4d2beaf40e25942; regression a97ce7d7b569ef065208bd1ab3e46072f220b3a3b8339cc8632e88a44198a002; full gate 36907cb3711574f665be58ac172737e2c06d7e3ec8cf107af7eb8515ba8e35bb; register 7a5885400bd1d486aad4eb033835c9373eb1e8854fc98814f8e7aad0e87bbf1; dependency f327449420f564eefb2d34edf4eaebb7ce14aa66b6021575accd038b38b735ce.

## Formal Ward-Constrained Condensed Stationarity (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_WARD_CONSTRAINED_CONDENSED_LANE; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: A finite local counterterm coefficient is derived algebraically from the Goldstone/Ward condition at the tree condensate boundary. The same coefficient makes that boundary stationary to tolerance, leaves the zero mode gapless, leaves the high mode positive, and gives a positive one-sided derivative into the stable domain.
WHAT_REMAINS_OPEN: This is not a microscopic finite-temperature renormalization or 2PI/1/N completion. The full condensed EOS, normal/two-fluid sector, retarded Kubo, microscopic SK/KMS, entropy/heat-flux balance, dimensional Phi map, independent alpha_Phi_K, and Ding-compatible C_src remain open.
DEPENDENCY_UNLOCKED: Formal Ward-constrained condensed stationarity lane only; no physical renormalization, full condensed EOS, two-fluid, transport, Core, Gravity, SI, alpha, or external-validation unlock.
STATUS: PASS_FORMAL_WARD_CONSTRAINED_CONDENSED_STATIONARITY; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Added the formal Ward-constrained condensed module, audit artifact, regression test, full-gate projection, and major-result registry sync.
EQUATION_OR_MAPPING: x_W=q/lambda; a_W=-D_0(x_W)*Lambda_*^2/[3*(x_W-x_*)^2]; D_{a_W}(x_W)=0; omega_G^2(k=0;x_W)=0. The reference result is a_W=-0.004082223093167454, D_W=-1.734723475976807e-18, and the one-sided derivative is 0.007018833356261021.
VERIFICATION: Audit passed with zero failed checks; coefficient convergence, cutoff convergence, zero-mode, high-mode, one-sided stability, reference anchors, ontology, and no-fit checks pass. Formal Ward/integration suite passed (20 passed); Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: ward_preserving_condensed_2PI_or_1N_microscopic_completion_missing.
NEXT_ACTION: Replace the formal local completion with a source-backed or microscopically renormalized symmetry-improved 2PI/controlled 1/N branch, then close physical condensed EOS and retarded Kubo/SK-KMS interfaces.
CLAIM_BOUNDARY: This closes only a formal symmetry-constrained stationarity lane. The coefficient is derived from Ward compatibility, not fitted, but it is not a microscopic thermal scheme, complete condensed/two-fluid EOS, physical transport, SI calibration, alpha_Phi_K, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module 361da29567144649f248d85ea961d035bd427d8645d0af991d464f97fe50afa3; audit 9e1c3c8994059529da650a2c80285a1ab13a88e2850531fa586883abd5524911; regression 3476b5d32f60c46761309843080b57304832a94f0392109058cc37a682cbd94e; full gate 50f3060a24bf96ba514941ea6f9c3aaf9d0a95e043ecbcd692daaeb6a7c18c73; register b8b329edd4d0eb80c0b4da8d4073bc27a613b6ba52f516a5f58909bb4fcf776e; dependency 454225b29a60be707bbcf55977f9c9cc4c66d63c9c1c5c517c6060d1b3b72638.

## Evidence-Chain Resynchronization (2026-08-14)

MAJOR_RESULT_CLOSURE: Existing lane closures remain unchanged; evidence hashes are synchronized after a semantics-preserving implementation cleanup.
WHAT_IS_ACTUALLY_CLOSED: The renormalized Hartree normal lane, condensed Ward no-go, and formal Ward-constrained lane each point to their current audit artifacts and the same full gate/register/dependency snapshot.
WHAT_REMAINS_OPEN: Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL with the existing source, alpha, bridge/beta, EOS/transport/KMS/entropy, and dimensional-map blockers.
DEPENDENCY_UNLOCKED: No new dependency; only evidence-chain consistency.
STATUS: PASS_SCOPED_EVIDENCE_CHAIN_RESYNCHRONIZATION.
WHAT_CHANGED: Reran the renormalized Hartree audit after eliminating a duplicated vacuum-term evaluation, reran the Ward audit and full gate, and refreshed registry/dependency projections.
EQUATION_OR_MAPPING: No equation or threshold changed; all Ward and Hartree equations remain as previously declared.
VERIFICATION: Hartree audit, Ward audit, full gate, major-result closure, downstream dependency audit, and focused regressions remain passing within their declared scopes; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: ward_preserving_condensed_2PI_or_1N_microscopic_completion_missing and physical finite-temperature/source/Kubo closure.
NEXT_ACTION: Continue with a source-backed or microscopic Ward-preserving condensed construction; do not promote formal lanes to physical closure.
CLAIM_BOUNDARY: Hash synchronization is not physical renormalization, external validation, alpha calibration, full EOS/transport closure, or Full Topic 13 closure.
EVIDENCE_HASHES: Hartree module 833517333209bd9b2e6f0deb42f0a792454769ee35400626deb18369396ce725; Hartree audit 2d63daeb2252fbb63b1f051a53d6da2c8fdd941a82aadf94141db111000e8f38; Ward-constrained audit 9e1c3c8994059529da650a2c80285a1ab13a88e2850531fa586883abd5524911; full gate 6ac87401d38b3c6bce7c060bd911b3cc0e00794c9d380d57c1b2daf2d53cc480; register 2ea577e83ce3d4b520b1f7faebd4d4f2f1795bb105bb3786c6af6c465ebbe842; dependency a14ba456f53f8626e6bff944006ca1601a2abbbc564fadabcea8b49f760d154b.

## Fixed-Prescription Ward-Preserving Auxiliary-Field Condensed Lane (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_AUXILIARY_FIELD_WARD_PRESERVING_CONDENSED_LANE; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: A single fixed mass-squared Taylor-subtraction prescription now defines a finite-temperature condensed auxiliary-field lane across the declared state grid. Joint stationarity enforces M^2=Z*mu^2, so the resummed phase Ward gap is zero without a state-dependent counterterm.
WHAT_REMAINS_OPEN: Microscopic 2PI or controlled 1/N matching, physical finite-temperature renormalization, complete condensed/two-fluid EOS, retarded physical Kubo, microscopic SK/KMS, entropy/heat-flux balance, dimensional Phi mapping, independent alpha_Phi_K, and Ding-compatible C_src remain open.
DEPENDENCY_UNLOCKED: Formal Ward-preserving auxiliary-field condensed lane only; no physical EOS, Kubo/SK-KMS, SI, alpha, TTG, Core, Gravity, or external-validation dependency is unlocked.
STATUS: PASS_FORMAL_WARD_PRESERVING_AUXILIARY_FIELD_CONDENSED_LANE; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Added the auxiliary-field functional, audit artifact, regression test, full-gate projection, and major-result registry synchronization. No source rows, target curve, fit, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: Omega=(m_eff^2-Z*mu^2)*rho/2+lambda*rho^2/4+Omega_1^R(M^2)-(M^2-m_eff^2-lambda*rho)^2/(4*lambda); partial_rho Omega=(M^2-Z*mu^2)/2; partial_M2 Omega=I_R-(M^2-m_eff^2-lambda*rho)/(2*lambda); therefore M^2=Z*mu^2 and rho=(Z*mu^2-m_eff^2-2*lambda*I_R)/lambda.
VERIFICATION: Audit passed with zero failed checks; six states are condensed and Ward-gapless, auxiliary gap residuals close to 1e-10, thermodynamic charge/entropy envelope checks pass, maximum quadrature relative error is 5.4062289645398915e-12, and maximum cutoff relative error is 5.588546748373999e-07. Regression test passed (3 passed); major-result closure has 100 entries; downstream dependency audit remains blocked; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: microscopic_2pi_or_controlled_1N_matching_missing.
NEXT_ACTION: Match this formal auxiliary-field equation set to a microscopic symmetry-preserving 2PI or controlled 1/N construction, then rerun condensed EOS and retarded Kubo/SK-KMS gates across the state domain.
CLAIM_BOUNDARY: This closes only a fixed-prescription Ward-preserving auxiliary-field condensed lane. It is not a microscopic 2PI or controlled 1/N completion, a physical finite-temperature renormalization, a complete two-fluid EOS, a retarded Kubo/SK-KMS match, an SI Phi map, an alpha_Phi_K calibration, TTG validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module 588e676a0097fa06393b0b9542af846c4156ff869247521856b753b9d4fa9c1d; verifier ffbe68dc7b99ce4923617cdcbbc4fa2167645e45b95cc9b74982f80dabcb5aae3; artifact 523b6b1e9202450f6d5b555657a72f3967b393e079dc8925fb179d795267d50f; regression e35fb9938dfd519add947f4a74a7b910b9be7022c430aa59c77a5e80c7f69270; full gate f9555b729dca96a97e37a7c82506e00f74179b9f91a8218130ad7b29560a1e67; register d0c07f864073563bcbca73f4156f144cbf98415f9293594f0046aa8cca734699; dependency ec2d13394f0d81bf4b467f6a58e1fcdbabb8335f2e086f8f28c91d01cea0f05e.

## Collisionless O(2) Kubo Boundary (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_AS_NO_GO for T13_UET_O2_COLLISIONLESS_KUBO_NO_GO; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The declared normal collisionless response has a positive Drude weight, but the DC Kubo limit is not finite when the width tends to zero.
WHAT_REMAINS_OPEN: An interaction collision kernel or microscopic self-energy/width, a matched retarded correlator, physical heat transport, dimensional Phi mapping, independent alpha_Phi_K, and Ding-compatible C_src remain open.
DEPENDENCY_UNLOCKED: Collisionless Kubo structural boundary only; no physical transport, SI, alpha, Core, Gravity, or external-validation dependency is unlocked.
STATUS: PASS_COLLISIONLESS_KUBO_DC_NO_GO; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Added the action-derived collisionless Drude boundary, verifier, regression test, full-gate projection, and major-result synchronization. No source rows, fit, target curve, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: sigma(omega;gamma)=D/(gamma-i*omega); rho_JJ=2*D*omega*gamma/(gamma^2+omega^2); K_DC=(1/2)lim rho_JJ/omega=D/gamma; gamma->0+ gives no finite DC coefficient.
VERIFICATION: Audit passed with zero failed checks. D=0.0008468305206465916; regulated coefficients for gamma=(0.1,0.01,0.001) are (0.008468305206465916, 0.08468305206465916, 0.8468305206465916); focused regression passed (3 passed); major-result register has 101 entries; downstream dependency audit remains blocked.
CONTROLLING_BLOCKER: interaction_collision_kernel_or_microscopic_width_missing.
NEXT_ACTION: Derive a state-matched interaction collision kernel or obtain a microscopic retarded correlator with a declared width, then rerun the transport and SK/KMS gates without promoting the diagnostic regulator.
CLAIM_BOUNDARY: This closes only a collisionless Kubo structural no-go. It does not supply a physical transport coefficient, SI observable, alpha_Phi_K calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module ca2013138f968ab01272d4df54404ed1bf103b6ff6bb45a373ac75b34170096c; verifier b13c60c53490c3b73b609037016856b4f0823e036773b58b297c77cf46565e69; artifact 122307d4c4549bc303fff9415d9c40c1f0217a6558922d6f60111cfb13ad82fb; full gate 6f9924d2087db0c502f46c04444e851166347e46f8ade0f21d8da732d16c4a1c; register 466da190249635edbede5b3477b69052c3a8709a19719ee941996f5c0970166c; dependency 90271fcc45df99a2979b571294ca08f0d7bbcb9c0787275108fae7ef17e567d.

## Action-Derived Dilute-Gas Kinetic Collision Kernel (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_KINETIC_COLLISION_KERNEL_LANE; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The declared constant-amplitude normal-branch 2-to-2 phase-space kernel produces a positive collision width and finite action-derived kinetic comparator in natural units. The baseline lane keeps final-state Bose enhancement disabled.
WHAT_REMAINS_OPEN: The separately named elastic quantum enhancement lane is not a retarded or ladder-matched transport result; condensed scattering, microscopic SK/KMS, heat-flux and entropy balance, dimensional Phi mapping, independent alpha_Phi_K, Ding C_src, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Named dilute-gas kinetic comparator only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock.
STATUS: PASS_ACTION_DERIVED_DILUTE_KINETIC_COLLISION_LANE; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Repaired the optional outgoing-state parameter integration without changing the baseline default, reran the baseline artifact, and preserved the explicit no-fit/no-holdout contract.
EQUATION_OR_MAPPING: Gamma_s(k)=sum_r integral[d^3p/(2*pi)^3] f_r(E_p) v_rel sigma_22(s); sigma_22(s)=lambda^2/(16*pi*s); K_kin=sum_s D_s/Gamma_s(k_ref). Natural units only; Phi is not temperature.
VERIFICATION: Baseline audit passed with zero failed checks; reference widths are (1.3919336977353308e-06, 1.3919336977353308e-06), K_kin=608.3842369966399, refinement changes are about 2.554e-06, and focused regression passed (3 passed). Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: ladder_vertex_resummation_missing.
NEXT_ACTION: Derive a matched retarded response and ladder/vertex closure, then compare it to this action-derived comparator without promoting the comparator to a physical Kubo coefficient.
CLAIM_BOUNDARY: Lane-level natural-unit kinetic comparator only; not full quantum transport, physical Kubo, SI observable, alpha_Phi_K calibration, TTG prediction, external validation, or global UET closure.
EVIDENCE_HASHES: module 411314a28d67bbce457f96ad6f147b183a7580fb983e88af7ba9ce0ce7c149be; verifier 9547fe1d29b2df7538af18142d22756af52295b523d741e8fab056fb5ca1e3eb; regression 8fab8d414e268c97cbaff2982ff807da14c76061bf2a3861707256ba334329f5; artifact 1f56e114e69e7c238d55921a3a3c2265b3e26e1655e7d69948072680499747a8; full gate 79c44f158589e2a1f4bcd20da4f307505fef63ae9cbd193326d26d4105bbbaa3; register f9eae6d0ea9c7e6b41876c7d2f6a5ba68f4929d249260b7f4c1700bda1d7ccdf; dependency fb5497504fbf50875dbf60a1f78a14e313e1aceb51df6054d608bb52927ce75e.

## Explicit Elastic Final-State Bose Enhancement (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_QUANTUM_COLLISION_ENHANCEMENT_LANE; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: An explicit elastic outgoing-state factor B_34=(1+f_3)(1+f_4) is averaged over the final-state center-of-mass angle and increases the declared collision width relative to the baseline at the same state point.
WHAT_REMAINS_OPEN: Ladder/vertex resummation, condensed collision processes, microscopic SK/KMS and retarded Kubo matching, heat-flux and entropy balance, dimensional Phi mapping, independent alpha_Phi_K, Ding C_src, and external validation remain open.
DEPENDENCY_UNLOCKED: Quantum-enhanced dilute-gas comparator only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock.
STATUS: PASS_ACTION_DERIVED_QUANTUM_COLLISION_ENHANCEMENT_LANE; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL.
WHAT_CHANGED: Added a separately named explicit Bose-enhancement lane, verifier artifact, focused tests, full-gate projection, and major-result register entry. No source rows, target curve, fit, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: Gamma_s^Q(k)=sum_r integral[d^3p/(2*pi)^3] f_r v_rel sigma_22 B_34; B_34=(1+f_3)(1+f_4) for the declared elastic outgoing-state comparator. This is not a ladder-resummed retarded response.
VERIFICATION: Audit passed with zero failed checks; width ratios versus baseline are (1.0141056743182757, 1.027717187674908), quantum refinement changes are about 2.54e-06, response refinement is about 2.53e-06, and focused regression passed (3 passed). The lane emits no physical Kubo coefficient or alpha_Phi_K and leaves Xie 2026 unconsumed.
CONTROLLING_BLOCKER: ladder_vertex_resummation_missing.
NEXT_ACTION: Build the matched retarded/ladder response and test its SK/KMS relation before using any quantum-enhanced coefficient as physical transport.
CLAIM_BOUNDARY: This closes only a named action-derived quantum-enhanced collision comparator. It is not full quantum transport, a physical Kubo coefficient, an SI observable, alpha_Phi_K calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module 411314a28d67bbce457f96ad6f147b183a7580fb983e88af7ba9ce0ce7c149be; verifier ced57134341ecfc74b2323154e8022417f48b386f2c24c7a47a0d16486a30d82; artifact 5a74176a196435b7dcc4c8d670e2eb4b6d667b9eb611d2852cf9cd422c887760; focused test 5d1214c0f3acdc9812edf177f89aa2194bbca977c2bcd64987b9120c61453f87; full gate 79c44f158589e2a1f4bcd20da4f307505fef63ae9cbd193326d26d4105bbbaa3; register f9eae6d0ea9c7e6b41876c7d2f6a5ba68f4929d249260b7f4c1700bda1d7ccdf; dependency fb5497504fbf50875dbf60a1f78a14e313e1aceb51df6054d608bb52927ce75e.

## Conserving Two-Channel Retarded Response (2026-08-14)
MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_UET_O2_CHARGE_CONSERVING_LADDER_RESPONSE_LANE; Full Topic 13 remains PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The corrected quantum collision width now feeds an explicit two-channel conserving response operator. The conserved sum mode is an exact zero mode, the relative mode is positive dissipative, and the finite-frequency retarded response is resolved by a declared matrix resolvent.
WHAT_REMAINS_OPEN: A momentum-dependent microscopic Bethe-Salpeter ladder, SK/KMS matching, condensed scattering, physical Kubo, entropy-current/heat-flux balance, dimensional Phi mapping, independent alpha_Phi_K, Ding-compatible C_src, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Named conserving response lane only; no physical Kubo, SI, alpha, thermal bridge, Core, Gravity, constitutive transport, or external-validation dependency is unlocked.
STATUS: PASS_ACTION_DERIVED_CONSERVING_LADDER_RESPONSE_LANE; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE at PARTIAL with the same 10 controlling blockers.
WHAT_CHANGED: Added the conserving response module, machine-readable audit artifact, focused regression tests, full-gate projection, major-result register synchronization, formula-audit entry T13-059, and this major-result report section. The duplicate angular collision-kernel accumulation was removed before the response rerun; no threshold, holdout, or ontology changed.
EQUATION_OR_MAPPING: P_perp=I-n*n^T/(n^T*n), n=(1,1); Gamma_rel=(Gamma_+ + Gamma_-)/2; L=Gamma_rel*P_perp; b_perp=P_perp*q*sqrt(D), q=(-1,+1); K_R(omega)=b_perp^T*(L-i*omega*I)^(-1)*b_perp. Natural units only; Phi is not temperature and the response is not an SI Kubo coefficient.
VERIFICATION: Response audit passed with zero failed checks; eigenvalues are (0, 1.4210409948530135e-06), DC response is 413.8909140423845 and matches the closed form, real-response refinement change is 2.5334741779713136e-06, focused collision/quantum/response suite passed (9 tests), full gate remains blocked, downstream dependency audit remains blocked, and Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: microscopic_ladder_vertex_and_SK_KMS_matching_missing.
NEXT_ACTION: Replace the finite-dimensional comparator with a momentum-dependent microscopic ladder/vertex construction and match it to SK/KMS and entropy/heat-flux identities; keep physical Kubo and alpha_Phi_K closed until the independent SI/source contracts exist.
CLAIM_BOUNDARY: This closes only a named action-derived conserving two-channel response lane. It is not a microscopic transport proof, physical Kubo coefficient, SI observable, alpha_Phi_K calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module d01d7d04bbdb2e86ac660c0e7fb18052e33b0efd75ccb6b8bc61c8649d452eea; verifier 5b9f59bd7cee55daebd21584c25c2d9f4f1f14d16b338d1fc04b703577c3c345; regression f6d5e4356b49cf62695edd411696a1fa365e870c395dc543ae727175d52c3919; quantum artifact 5a74176a196435b7dcc4c8d670e2eb4b6d667b9eb611d2852cf9cd422c887760; corrected collision artifact 1f56e114e69e7c238d55921a3a3c2265b3e26e1655e7d69948072680499747a8; full gate 79c44f158589e2a1f4bcd20da4f307505fef63ae9cbd193326d26d4105bbbaa3; register f9eae6d0ea9c7e6b41876c7d2f6a5ba68f4929d249260b7f4c1700bda1d7ccdf; dependency fb5497504fbf50875dbf60a1f78a14e313e1aceb51df6054d608bb52927ce75e.

## Momentum-Grid Action-Derived SK/KMS Interface (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for `T13_UET_O2_MOMENTUM_LADDER_SK_KMS_INTERFACE_LANE`; Full Topic 13 remains `PARTIAL` and `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: A momentum-grid response construction now uses action-derived quantum collision widths, a weighted charge-conserving projector, a positive semidefinite projected collision operator, a finite-frequency retarded resolvent, and an explicit algebraic KMS/FDT interface. The formal entropy-production witness is nonnegative on the declared lane.
WHAT_REMAINS_OPEN: The finite-cutoff limit, full energy-momentum conserving collision operator, microscopic Bethe-Salpeter vertex, microscopic SK/KMS action matching, physical Kubo coefficient, entropy-current/heat-flux balance, dimensional Phi-to-thermal map, independent alpha_Phi_K, Ding-compatible numeric C_src, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Named momentum-dependent response and algebraic KMS/FDT interface only. No physical Kubo, SI, alpha, TTG, Core, Gravity, constitutive-transport, or external-validation dependency is unlocked.
STATUS: PASS_ACTION_DERIVED_MOMENTUM_LADDER_SK_KMS_INTERFACE_LANE; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`.
WHAT_CHANGED: Added the momentum-grid module, machine-readable audit artifact, regression tests, full-gate map, major-result sync tuple, formula-audit entry T13-060, and this report section. The lane declares a finite momentum cutoff and does not consume source rows, fit parameters, target data, or Xie 2026.
EQUATION_OR_MAPPING: `w_s(k)=k^2/(2*pi^2*T)*f_s(E_k)*(1+f_s(E_k))*dk`; `c_(s,k)=q_s*sqrt(w_s(k))`; `P=I-c*c^T/(c^T*c)`; `L=P*diag(Gamma_s(k))*P`; `b_perp=P*b`; `K_R(omega)=b_perp^T*(L-i*omega*I)^(-1)*b_perp`; `rho=2*Im(K_R)`; `G^>=rho*(1+n_B)`; `G^<=rho*n_B`;
=rho*coth(beta_th*omega/2)`; `sigma_formal=b_perp^T*L*b_perp/T`. Natural units only; Phi is not temperature, C is not mass or charge, R_gen is a derived history trace, and R_obs is separate.
VERIFICATION: Audit completed with zero failed checks. The reference lane has 64 states across two species, width spread `3.572274811684194`, positive-mode rate `3.845182613400187e-07`, entropy witness `4.662265988145945e-10`, and fixed-cutoff reference/refined response change `0.008022779716558905`. Charge conservation, positive semidefiniteness, retarded sign/monotonicity, algebraic KMS/FDT identities, finite-grid refinement, ontology, no-fitting, and no-holdout checks pass. Full gate and downstream dependency audit remain blocked.
CONTROLLING_BLOCKER: `microscopic_bethe_salpeter_and_SK_KMS_matching_missing`.
NEXT_ACTION: Derive the full energy-momentum conserving collision operator and microscopic vertex, then match its retarded response to a microscopic Bethe-Salpeter/SK construction. Keep the finite-cutoff boundary, physical Kubo, dimensional map, source package, and alpha_Phi_K independently gated.
CLAIM_BOUNDARY: This closes only a named action-derived momentum-grid response and algebraic KMS/FDT interface at a declared finite cutoff. It is not a microscopic Bethe-Salpeter or SK/KMS proof, physical transport coefficient, SI observable, alpha_Phi_K calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module c47aae04eca1e703919de6de9050e81d76dd036053bec9ef47c4cc0bbd648dbb; verifier e0fbe5e38c139f662e665f23e339143e8844c5ff7ef8c6e2467e0cbe47f4d047; regression a22dbe3291ea8b65183cac401ee978cd6f5fb06313df63e40de942892596da15; artifact ecab85f83097a47104abeea8d25a289cb35f137e2c618757232b0c470b7dbffc; full gate e03dbc30463696c0f8568550e93725167365d3eb7007cc7969ebe423721acac6; register 2d35357ecf179ccb84756d63966d7bc010a90f05de39ea60e8415fac08da2318; dependency f0d6c5c97b322b2af1049891b42a52161f0e161c2ea1fb1ad17c7cce4acf6d11.

## Finite-Grid Charge and Four-Momentum Conserving Bethe-Salpeter Interface (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for `T13_UET_O2_ENERGY_MOMENTUM_CONSERVING_BS_INTERFACE_LANE`; Full Topic 13 remains `PARTIAL` and `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The six-direction finite momentum grid has independent charge, energy, and three spatial-momentum invariant columns. A positive semidefinite projected collision operator preserves all five moments, its momentum-current retarded response is refined at fixed cutoff, and an algebraic Bethe-Salpeter resolvent identity is verified and paired with algebraic KMS/FDT and entropy checks.
WHAT_REMAINS_OPEN: The microscopic two-to-two transition kernel, detailed-balance collision matrix, microscopic Bethe-Salpeter vertex, microscopic SK action/KMS matching, finite-cutoff limit, entropy-current/heat-flux balance, dimensional Phi-to-thermal map, independent alpha_Phi_K, Ding-compatible numeric C_src, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Named finite-grid charge and four-momentum conserving response plus algebraic Bethe-Salpeter/KMS interface only. No microscopic transport, physical Kubo, SI, alpha, TTG, Core, Gravity, constitutive-transport, or external-validation dependency is unlocked.
STATUS: PASS_ACTION_DERIVED_FULL_MOMENT_CONSERVING_BS_INTERFACE_LANE; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`.
WHAT_CHANGED: Added the full-moment conserving module, machine-readable audit artifact, regression tests, full-gate map, major-result sync tuple, formula-audit entry T13-061, and this report section. The construction uses no source rows, fitting, target data, or Xie 2026.
EQUATION_OR_MAPPING: `w_(s,k,n)=k^2/(2*pi^2*T)*f_s(E_k)*(1+f_s(E_k))*dk*dOmega/(4*pi)`; `I_A=(q_s,E_k,p_x,p_y,p_z)*sqrt(w)`; `Q=orth(I_A)`; `P=I-Q*Q^T`; `L=P*diag(Gamma_s(k))*P`; `G_R=(L-i*omega*I)^(-1)`; `G_0=(gamma_ref*I-i*omega*I)^(-1)`; `K_BS=gamma_ref*I-L`; `G_R=G_0+G_0*K_BS*G_R`. Natural units only; Phi is not temperature, C is not mass or charge, R_gen is a derived history trace, and R_obs is separate.
VERIFICATION: Audit completed with zero failed checks. Reference state count is 336 and refined count 384; invariant rank is 5 with exactly 5 zero modes; width spread is `3.5807734053859255`; fixed-cutoff radial response change is `0.011432789900851996`; angular response change is `4.286281547630234e-07`; maximum algebraic BS residual is `2.838675109392314e-16`; entropy witness is `3.94107226021442e-10`. Focused regression passed 3 tests; full gate and downstream dependency audit remain blocked.
CONTROLLING_BLOCKER: `microscopic_transition_kernel_and_vertex_SK_match_missing`.
NEXT_ACTION: Derive an action-derived two-to-two transition kernel with detailed balance, then match its ladder vertex to the SK/KMS response. Keep finite-cutoff, entropy-current, dimensional mapping, independent alpha_Phi_K, and source contracts separate.
CLAIM_BOUNDARY: This closes only a finite-grid action-derived charge and four-momentum conserving response plus algebraic Bethe-Salpeter/KMS interface. It is not a microscopic transition kernel, Bethe-Salpeter vertex, SK action match, physical Kubo coefficient, SI observable, alpha_Phi_K calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module eb69cc8ab6c35d782fbc687bc6fa503a22ae76c78e28d65c466eaf0e7e4719a9; verifier 7eda9d921a5741d909040ff97dacc3be2f60b0665967bc59e051798ee27e5abc; regression ca90dc837bfadfce294308d70da119485b212a92084af0cf9f10b64dca926d7c; artifact a680c01bd50e8596a2ccc43d86e06f69c24b9785a40117f4ebe424ef5c34815b; full gate d5ab4df23ad9c3c2475baae9b3e71a4d842f2897ce594478f40c128240e9d59c; register 78c7399d136bbc4796589f677a995827b6ef1f5bc94430aeafdea04f7f1f6b17; dependency 3c2460992d0496b88d6242fff68dba4d39d2994c19c876a20679e85c817f4e98.

## Exact-Kinematic Action-Derived Two-to-Two Transition Kernel (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for `T13_UET_O2_EXACT_KINEMATIC_2TO2_TRANSITION_KERNEL_LANE`; Full Topic 13 remains `PARTIAL` and `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: Twelve finite elastic two-to-two channels are generated by exact center-of-mass kinematics and boosts. The action-derived constant-amplitude cross section and Bose factors produce forward/reverse detailed balance, and their channel outer-product operator is positive semidefinite, charge/four-momentum conserving, and connected to the active response/KMS interface.
WHAT_REMAINS_OPEN: The connected continuum collision operator, finite-channel limit, microscopic Bethe-Salpeter vertex, microscopic SK action/KMS matching, entropy-current/heat-flux balance, dimensional Phi-to-thermal map, independent alpha_Phi_K, Ding-compatible numeric C_src, and Full Topic 13 remain open. The 44 finite-channel null modes are declared, not promoted away.
DEPENDENCY_UNLOCKED: Named exact-kinematic transition-kernel and detailed-balance response interface only. No microscopic vertex, physical Kubo, SI, alpha, TTG, Core, Gravity, constitutive-transport, or external-validation dependency is unlocked.
STATUS: PASS_ACTION_DERIVED_EXACT_KINEMATIC_2TO2_TRANSITION_KERNEL_LANE; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`.
WHAT_CHANGED: Added the exact-kinematic transition module, machine-readable audit artifact, regression tests, full-gate map, major-result sync tuple, formula-audit entry T13-062, and this report section. No source rows, fitting, target data, or Xie 2026 were used.
EQUATION_OR_MAPPING: `p1+p2=p3+p4`; `E1+E2=E3+E4`; `sigma_22=lambda^2/(16*pi*s)`; `W_f=f1*f2*(1+f3)*(1+f4)*v_rel*sigma_22*dmu`; `W_r=f3*f4*(1+f1)*(1+f2)*v_rel*sigma_22*dmu`; `L=sum_c W_c*v_c*v_c^T`; `G_R=(L-i*omega*I)^(-1)`. Natural units only; Phi is not temperature, C is not mass or charge, R_gen is a derived history trace, and R_obs is separate.
VERIFICATION: Audit completed with zero failed checks. Reference has 12 channels and 48 leg states; invariant rank 5; 44 finite-channel null modes; maximum kinematic residual `1.3322676295501878e-14`; maximum detailed-balance residual `5.691997389781759e-14`; maximum algebraic BS residual `1.7446272552401067e-16`; entropy witness `5.802817311393105e-55`. Focused regression passed 3 tests; full gate and downstream dependency audit remain blocked.
CONTROLLING_BLOCKER: `connected_continuum_collision_operator_and_microscopic_vertex_missing`.
NEXT_ACTION: Connect the exact channels into a continuum collision operator and match its vertex to the microscopic Bethe-Salpeter/SK construction. Preserve the finite-channel boundary and keep entropy, dimensional, source, and alpha gates independent.
CLAIM_BOUNDARY: This closes only a finite exact-kinematic action-derived two-to-two transition kernel and detailed-balance response interface. It is not a connected continuum collision operator, microscopic Bethe-Salpeter vertex, SK action match, physical Kubo coefficient, SI observable, alpha_Phi_K calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module d1cae79dbbcd289c33b04c209ad4d0140ab3c22ce16bb568c267f041d2b3ece7; verifier c13264532ac27ffd0d1f60491f520c5dcf46ecc6d75743c36b86f988737bd201; regression eaf172360dd2a4013743e2013449b146fe74fbf9f5aa6941edf8824895dfcdd2; artifact 03b74b8ec35685decfa8ddc2e4b518453f68b70b2547413ffde7997508dd7ded; full gate a669e8ecb96ba077edfa3b8d385c50ca0315ab4dd1381951e1aa34a5207c8b4c; register dd5f847a37b1e7a357e1cb3a5e2695cb58862c5105633821ce33f4eb8c2beae8; dependency bd94ed176a122c8144be97e22d824fe5ddb9e4d5b9159f6be436374d07f58b27.

## Conservative Continuum-Collocation Collision Operator (2026-08-14)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for `T13_UET_O2_CONSERVATIVE_CONTINUUM_COLLOCATION_LANE`; Full Topic 13 remains `PARTIAL` and `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: A shared finite-temperature momentum basis is connected by one structural transition-support component with complete basis coverage. Exact action-derived two-to-two samples are mapped by an explicit normalized interpolation matrix; Gram projection removes mapped charge and four-momentum residuals; the action-width operator plus projected transition vertex has five physical zero modes and passes the formal response, algebraic Bethe-Salpeter, KMS/FDT, and entropy checks.
WHAT_REMAINS_OPEN: Continuum limit, microscopic Bethe-Salpeter vertex, microscopic SK/KMS action matching, entropy-current/heat-flux/dissipative balance, dimensional `Phi` to thermal map, independent `alpha_Phi_K`, Ding-compatible numeric `C_src`, physical Kubo, and Full Topic 13 remain open. The raw interpolation invariant residual is retained as a measured correction, not hidden.
DEPENDENCY_UNLOCKED: Named finite-cutoff conservative continuum-collocation operator and algebraic vertex/KMS interface only; no continuum-limit, microscopic, physical Kubo, SI, alpha, Core, Gravity, transport, or external-validation unlock.
STATUS: PASS_ACTION_DERIVED_CONSERVATIVE_CONTINUUM_COLLOCATION_LANE; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`; downstream dependency remains `BLOCKED_DOWNSTREAM_MAJOR_RESULTS`.
WHAT_CHANGED: Added a shared momentum-basis collocation lane, explicit interpolation and conservation projection, action-derived transition-vertex correction, machine-readable audit artifact, focused regression tests, full-gate/register mappings, and this report section. No source rows, fitting, target data, or Xie 2026 were used.
EQUATION_OR_MAPPING: `u_c=B*v_c`; `u_c^P=P*u_c`; `L_width=P*diag(Gamma_action_s(k))*P`; `K_transition=sum_c W_c*u_c^P*(u_c^P)^T`; `L_cont=L_width+K_transition`; `G_R=(L_cont-i*omega*I)^(-1)`; `K_BS=gamma_ref*I-L_cont`; `G_R=G_0+G_0*K_BS*G_R`. Natural units only; `Phi` is not temperature, `C` is not mass or charge, `R_gen` is a derived history trace, and `R_obs` is separate.
VERIFICATION: Audit passed with zero failed checks. Reference has 96 basis states, 64 exact channel samples, one transition-support component, complete basis coverage, invariant rank 5, and 5 zero modes. Projected mapped-invariant residual is `2.5325958237978373e-17`, raw residual is `0.05126807072913043`, vertex trace ratio is `1.5806302954625802e-06`, maximum BS residual is `4.513280234121269e-16`, entropy witness is `7.653163030092222e-10`, and fixed-cutoff refinement response change is `0.47541462972440046`; refinement is recorded, not called continuum convergence. Focused regression passed `3` tests; combined transition/full-moment/continuum regression passed `9` tests; syntax check passed; dependency audit keeps Core curved 3+1, GR, transport, and Galaxy blocked.
CONTROLLING_BLOCKER: `microscopic_bethe_salpeter_vertex_and_SK_action_match_missing`.
NEXT_ACTION: Derive the microscopic vertex and SK/KMS action match on top of this connected finite-cutoff operator, then test a declared continuum-limit sequence. Keep entropy-current/heat-flux, dimensional mapping, independent `alpha_Phi_K`, Ding source, and Xie holdout gates independent.
CLAIM_BOUNDARY: This closes only a finite-cutoff action-derived conservative continuum-collocation and algebraic vertex/KMS interface. It is not a continuum-limit proof, microscopic Bethe-Salpeter vertex, microscopic SK action match, physical Kubo coefficient, SI observable, `alpha_Phi_K` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module 010c1322063b806a1d87d3708cf5509e696f7370170dc2b859f61fd8f884e9e; verifier adf50437fbd42ddcb772c3ca2ff5f4ddc7e7d5adec551a0067b5258f929070b5; regression 86ec301973854c8f39d03e4f3ed42142da711118d258b1eabac56d883da125a4; artifact c51318e5a912bb12622fbbab53a52796aec257a46593717687f6af2df5e2bf63; full gate d7f7730f9baf1473553d69de3fe3b191db5abbb0848df9f59fa65bccee0ca3b0; register 9d8f80ba59d5fdfca6deac252af3f14f6ab15d7207b63118eb056af1f3f1f239; dependency d6c7ca22a7fbeccabf7628b1f2a8b22ccb3859350f00ae8507018765c241147e.

## Tree-Level Action Vertex and Formal SK/KMS/Bethe-Salpeter Interface (2026-08-14)
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_TREE_LEVEL_BS_SK_MATCH_INTERFACE_LANE`; Full Topic 13 remains `PARTIAL` and `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The declared tree-level charged-sector action vertex normalization is explicit and matched to exact elastic kinematics. The finite-cutoff conservative operator, algebraic Bethe-Salpeter identity, and formal SK retarded/noise KMS/FDT interface pass machine checks with a positive formal entropy witness.
WHAT_REMAINS_OPEN: The loop-renormalized microscopic vertex, full interacting SK influence functional, continuum limit, physical Kubo coefficient, entropy-current/heat-flux/dissipative balance, dimensional `Phi` to thermal map, independent `alpha_Phi_K`, Ding-compatible numeric `C_src`, and Full Topic 13 remain open. The recorded continuum sequence is visibly nonconverged.
DEPENDENCY_UNLOCKED: Named tree-level action vertex normalization and formal finite-cutoff SK/KMS/Bethe-Salpeter interface only. Core curved 3+1, Gravity, full constitutive transport, Galaxy, SI, alpha, source, and external-validation dependencies remain blocked.
STATUS: `PASS_ACTION_DERIVED_TREE_LEVEL_BS_SK_MATCH_INTERFACE_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`; downstream dependency remains `BLOCKED_DOWNSTREAM_MAJOR_RESULTS`.
WHAT_CHANGED: Added the tree-level action vertex/SK matching state, machine-readable verifier/artifact, regression tests, full-gate/register mappings, formula-audit entry `T13-064`, and this report section. No source rows, fitting, target data, Landauer-derived alpha, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: `M_tree=lambda`; `sigma_22=|M_tree|^2/(16*pi*s)`; `L_cont=L_width+K_transition`; `K_BS=gamma_ref*I-L_cont`; `G_R=G_0+G_0*K_BS*G_R`; `S_SK=integral[Phi_a D_R Phi_r+i Phi_a N Phi_a/2]`;
=coth(beta_th*omega/2)*rho`. Natural units only; `Phi` is not temperature, `C` is not mass or charge, `R_gen` is a derived history trace, and `R_obs` is separate.
VERIFICATION: Zero failed checks. Action cross-section residual `1.1102230246251565e-16`; kinematic residual `1.4210854715202004e-14`; detailed-balance residual `8.543090354715029e-14`; decomposition residual `2.4147484638442308e-22`; BS residual `4.513280234121269e-16`; formal SK/KMS residual `1.729285121923951e-16`; FDT residual `2.0024586688771869e-16`; entropy witness `7.653163030092222e-10`; maximum recorded continuum-sequence change `0.47541462972440046`. New regression passed `3` tests. Full gate and dependency audit keep downstream promotion blocked.
CONTROLLING_BLOCKER: `loop_renormalized_microscopic_vertex_and_full_interacting_SK_action_match_missing`; independent `alpha_Phi_K` calibration remains separately open.
NEXT_ACTION: Derive the loop-renormalized microscopic vertex and full interacting SK/KMS action match on top of the declared tree-level interface, then rerun the continuum-limit controller. Keep entropy-current/heat-flux, dimensional mapping, independent alpha, Ding source, and Xie holdout gates independent.
CLAIM_BOUNDARY: This closes only the declared tree-level action vertex normalization and formal finite-cutoff SK/KMS/Bethe-Salpeter interface. It is not a loop-renormalized microscopic vertex, full interacting SK action, continuum-limit proof, physical Kubo coefficient, SI observable, `alpha_Phi_K` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module `ef3522ec6e925eee3fd937035829c801325f9e1ec39d5a809d42246f6c5e90c5`; verifier `24d5c3910f6dad9c79eb7c59bdbb3d0948b95523e5ff92688534d23d37ca2046`; regression `d4c7db2b9a1307dfc029d01de03710724bf513e33b243f3ea2b10f19f1619e20`; artifact `0861c4dc1b453685ea479054919d2f42b59a2c088284c81d40a0a25244302506`; full gate `b2f958fe8a965d44fd97194deb186803b19afd1f037b474b2633c700594853e9`; register `7bd723b6984f280458a195afa550a71e69b4eb3323da7a529d736012cdfe0d66`; dependency `dba0e24175476033394e4f974e667df4f5a1a61d137a5986e8399c7430594266`.

## O(2) One-Loop Vertex and UV Boundary (2026-08-14)
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_ONE_LOOP_VERTEX_UV_BOUNDARY`; Full Topic 13 remains `PARTIAL` and `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The O(2)-invariant bare four-point tensor, its rotation/permutation identities, the tree-level Keldysh contour interaction expansion, and the zero-external-momentum one-loop bubble separation are explicit. The thermal bubble is cutoff-stable; the vacuum bubble and loop correction expose the renormalization boundary.
WHAT_REMAINS_OPEN: Vacuum counterterm, renormalized microscopic vertex, finite-density charged propagator/vertex, full interacting SK/KMS action, continuum limit, physical Kubo, entropy-current/heat-flux balance, dimensional `Phi` map, independent `alpha_Phi_K`, Ding-compatible `C_src`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Named O(2) bare tensor and one-loop UV-boundary result only. No renormalized microscopic, finite-density, physical Kubo, SI, alpha, source, Core, Gravity, transport, or external-validation dependency is unlocked.
STATUS: `PASS_ACTION_DERIVED_O2_ONE_LOOP_VERTEX_UV_BOUNDARY`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`; downstream dependency remains `BLOCKED_DOWNSTREAM_MAJOR_RESULTS`.
WHAT_CHANGED: Added the O(2) tensor/bubble module, machine-readable verifier/artifact, regression tests, full-gate/register mappings, formula-audit entry `T13-065`, and this report section. The lane uses `mu=0` explicitly and consumes no source rows, fitting, target data, Landauer shortcut, or Xie 2026 holdout.
EQUATION_OR_MAPPING: `V_abcd=lambda*(delta_ab*delta_cd+delta_ac*delta_bd+delta_ad*delta_bc)`; `B_E^Lambda(0)=integral[(1+2*n_B)/(4*E^3)+n_B*(1+n_B)/(2*T*E^2)]`; `Gamma_1PI=V-(B_s*(V.V)+B_t*(V.V)+B_u*(V.V))/2`; `V_+-V_-=lambda*(phi_r^2)*(phi_r.phi_a)+(lambda/4)*(phi_a^2)*(phi_r.phi_a)`. Natural units only.
VERIFICATION: Zero failed checks. Tensor symmetry residual `0`; O(2) rotation residual `8.881784197001252e-16`; contour residual `3.4670477549072174e-16`; thermal cutoff relative change `2.9661695791593287e-14`; vacuum growth ratio `2.1590771346418225`; loop-correction growth ratio `2.151163286423315`; KMS ratio residual `0`; FDT residual `2.1737996091473846e-16`. New regression passed `3` tests. Full gate and dependency audit keep downstream promotion blocked.
CONTROLLING_BLOCKER: `vacuum_counterterm_and_renormalized_microscopic_vertex_missing`; finite-density charged propagator and full interacting SK/KMS match remain open separately.
NEXT_ACTION: Derive a declared vacuum counterterm and finite-density charged propagator/vertex, then match the renormalized result to the full interacting SK/KMS action without consuming Xie 2026. Keep alpha, source, continuum, entropy, and physical Kubo gates independent.
CLAIM_BOUNDARY: This closes only the O(2) bare tensor/contour identity and finite-cutoff one-loop UV boundary at `mu=0`. It is not a renormalized microscopic vertex, finite-density charged SK/KMS match, continuum-limit proof, physical Kubo coefficient, SI observable, `alpha_Phi_K` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module `fb47090eed90d4e37bab34516cc0ad0d60300981de91f9322d1513746e11e8e1`; verifier `2bccbbdb21d89569c54133c1382f1284a888010be59cdf056ed0ed84222b7a69`; regression `6a7f53dd9c079972048a449a0abd765b95576280834094e8ac1280b83dc11c28`; artifact `951ba2138f42674076ba573d15411ac4f2f662396e9f2d5644e73f932a82e155`; full gate `95f88e948ee0009ef6ba385cf488a3d6c0900c2c03f32d25972c0cc551d5703c`; register `b6d76ecf6af3a4a39f2ac58ce58e6cb0e0c7ac2dc03b2f04ab4738c27d75cdd8`; dependency `7fcc363577d66f449097a1446a17231aa49921f0a3212a90103883f1d3822c3e`.

## Finite-Density Charged Propagator and Vertex Scheme (2026-08-14)
MAJOR_RESULT_CLOSURE: \`CLOSED_FOR_LANE\` for \`T13_UET_O2_FINITE_DENSITY_CHARGED_VERTEX_SCHEME\`; Full Topic 13 remains \`PARTIAL\` and \`BLOCKED_OPEN_T13_FULL_BRIDGE\`.
WHAT_IS_ACTUALLY_CLOSED: The stable normal-branch Euclidean charged propagator, particle/antiparticle thermal weights, finite-density reference-subtracted one-loop vertex scheme, charged mode KMS/FDT witnesses, charge-conjugation/odd-charge checks, and exact compatibility with the preceding \`mu=0\` lane.
WHAT_REMAINS_OPEN: Unique physical renormalization, condensed/two-fluid charged completion, full interacting SK/KMS action, continuum limit, physical Kubo coefficient, entropy-current/heat-flux/dissipative balance, dimensional \`Phi\` map, independent \`alpha_Phi_K\`, Ding-compatible numeric \`C_src\`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Named finite-density charged normal-branch scheme only. Core curved 3+1, Gravity, full constitutive transport, Galaxy, SI, alpha, source, and external-validation dependencies remain blocked.
STATUS: \`PASS_ACTION_DERIVED_FINITE_DENSITY_CHARGED_O2_VERTEX_SCHEME\`; full gate remains \`BLOCKED_OPEN_T13_FULL_BRIDGE\` at \`PARTIAL\`; downstream dependency remains \`BLOCKED_DOWNSTREAM_MAJOR_RESULTS\`.
WHAT_CHANGED: Added the finite-density charged propagator/vertex module, machine-readable verifier/artifact, regression tests, full-gate/register mappings, and formula-audit entry \`T13-066\`. The lane uses only declared natural-unit action inputs; no source rows, fitting, target data, Landauer shortcut, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: \`D_E^{-1}(omega_n,k)=(omega_n+i*mu_eff)^2+k^2+m_eff(Phi)^2\`; \`E_particle=E-mu_eff\`; \`E_antiparticle=E+mu_eff\`; \`B_ch^R=B_vac(m)-B_vac(m_ref)+B_thermal(m,mu_eff)\`; \
_ch=sqrt(Z)*integral[(n_-(E)-n_+(E))d^3k/(2*pi)^3]\`. Natural units only; \`Phi\` is not temperature, \`C\` is not mass or charge, \`R_gen\` is a derived history trace, and \`R_obs\` is separate.
VERIFICATION: Zero failed checks. Static propagator residual \`1.2820127305140375e-16\`; factorization residual \`0\`; charged thermal cutoff change \`3.1691751332771736e-14\`; renormalized bubble/vertex changes \`1.1413950082964835e-05\` and \`3.137451738838419e-08\`; particle/antiparticle KMS, charge-conjugation, odd-charge, and neutral-limit residuals are all \`0\`. New regression passed \`3\` tests; Topic 13 suite passed \`289\` tests. Full gate and dependency audit keep downstream promotion blocked.
CONTROLLING_BLOCKER: \`unique_physical_renormalization_and_full_interacting_sk_kms_match_missing\`; condensed/two-fluid, continuum, entropy-current, physical Kubo, dimensional, independent \`alpha_Phi_K\`, Ding source, and holdout boundaries remain independent.
NEXT_ACTION: Match the finite-density charged scheme to a full interacting SK/KMS construction and a declared physical renormalization, then test the condensed/two-fluid interface. Keep \`alpha_Phi_K\`, TTG source, Xie holdout, entropy-current, heat-flux, and physical Kubo gates independent.
CLAIM_BOUNDARY: This closes only one declared natural-unit finite-density charged normal-branch vertex scheme. It is not a unique physical renormalization, condensed/two-fluid closure, full interacting SK/KMS action, continuum-limit proof, physical Kubo coefficient, SI observable, \`alpha_Phi_K\` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module \`188edb08ef56bf0a3908d1cab843632faf0580525fee527112cf41e6fcf4777f\`; verifier \`96b5303ec171a126cb1a702eaff98c5162580a1358564cc1491268afc99cfa04\`; regression \`cd0400d22fe2dc2bb0a746ce55c31a5037a3a2dfff4446ffa16cbaa9de746748\`; artifact \`5a1afa505dde3840923f67e9bded5acdbb05c01fde755396a218525b4701384d\`; full gate \`967e8c63388e4d6faff1918948797c74decdb712745905f4e4f1f9138627252d\`; register \`4ce4599047edaf0843ac3aefa3968fd2838c4a6f3c955d184007e1d373a721b3\`; dependency \`524f8381e90d0e4eaf1d6f8c34e007852ede0699eab2dca065da83f429eac4a5\`.

## Local Interacting SK/KMS Action Interface (2026-08-14)
MAJOR_RESULT_CLOSURE: \`CLOSED_FOR_LANE\` for \`T13_UET_O2_INTERACTING_SK_KMS_ACTION_INTERFACE\`; Full Topic 13 remains \`PARTIAL\` and \`BLOCKED_OPEN_T13_FULL_BRIDGE\`.
WHAT_IS_ACTUALLY_CLOSED: The exact local O(2) contour action difference in r/a variables, unitarity and reality identities, absence of pure-r interactions, explicit r^3a and ra^3 vertices, charged particle/antiparticle KMS-FDT, action-derived charged detailed balance, and a formal nonnegative entropy witness.
WHAT_REMAINS_OPEN: Nonlocal interacting SK influence functional, microscopic retarded self-energy and physical dissipation, unique physical renormalization, condensed/two-fluid completion, physical Kubo coefficient, entropy-current/heat-flux/dissipative balance, dimensional \`Phi\` map, independent \`alpha_Phi_K\`, Ding-compatible numeric \`C_src\`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Local interacting SK contour and charged equilibrium KMS/detailed-balance interface only. Core curved 3+1, Gravity, full constitutive transport, Galaxy, SI, alpha, source, and external-validation dependencies remain blocked.
STATUS: \`PASS_ACTION_DERIVED_INTERACTING_SK_KMS_LOCAL_ACTION_INTERFACE\`; full gate remains \`BLOCKED_OPEN_T13_FULL_BRIDGE\` at \`PARTIAL\`; downstream dependency remains \`BLOCKED_DOWNSTREAM_MAJOR_RESULTS\`.
WHAT_CHANGED: Added the exact local interacting contour module, machine-readable verifier/artifact, regression tests, full-gate/register mappings, and formula-audit entry \`T13-067\`. The lane uses declared natural-unit action inputs and existing action-derived transition channels; no source rows, fitting, target data, Landauer shortcut, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: \`S_SK=S_E[Phi_r+Phi_a/2]-S_E[Phi_r-Phi_a/2]\`; \`D_tau Phi=partial_tau Phi+mu_eff*J*Phi\`; \`V(r+a/2)-V(r-a/2)=lambda*(r.r)*(r.a)+(lambda/4)*(a.a)*(r.a)\`; charged KMS and detailed balance as recorded in \`T13-067\`. Natural units only; \`Phi\` is not temperature, \`C\` is not mass or charge, \`R_gen\` is a derived history trace, and \`R_obs\` is separate.
VERIFICATION: Zero failed checks. Contour expansion, unitarity, reality, and no-pure-r residuals are \`0\`; r^3a/ra^3 weights are \`0.0009339120000000001\` and \`6.6780000000000008e-05\`; charged collision detailed-balance residual \`2.8463221008786541e-14\`; collision KMS/FDT residuals \`1.7292851219239511e-16\` and \`1.5019325358485805e-16\`; formal entropy witness \`1.3611620264866121e-27\`. New regression passed \`3\` tests; Topic 13 suite passed \`292\` tests. Full gate and dependency audit keep downstream promotion blocked.
CONTROLLING_BLOCKER: \
onlocal_interacting_sk_influence_functional_and_physical_retarded_kernel_missing\`; unique physical renormalization, condensed/two-fluid, entropy-current, physical Kubo, dimensional, independent \`alpha_Phi_K\`, Ding source, and holdout boundaries remain independent.
NEXT_ACTION: Derive the nonlocal interacting SK influence functional and physical retarded/dissipative kernel from the charged action without importing a fitted coefficient. Then rerun entropy-current/heat-flux and Kubo gates while keeping \`alpha_Phi_K\`, TTG source, and Xie holdout independent.
CLAIM_BOUNDARY: This closes only the local action-level interacting SK contour and charged equilibrium KMS/detailed-balance interface. It is not a nonlocal influence-functional derivation, physical retarded self-energy, dissipative transport closure, unique physical renormalization, condensed/two-fluid closure, physical Kubo coefficient, SI observable, \`alpha_Phi_K\` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module \`91b432c04e11aebf4aa1c293a05ae611be4eca3243daa91546d671f63fd68da5\`; verifier \`2b3c09d45b386dda36fd38592fc18cdeb44d91987e7d52c9242c03bdecbc1c55\`; regression \`7a184da2a1710e59c10690952757917fbb87d74821a4b66257f1fcf6ee95236c\`; artifact \`6131d8ffba0e365d172c52c8e97cc58fa5f3eae75432aa8875aee9bb54b6c4e2\`; full gate \`6d8bd2d071ef01110416c887f85c594796ba925e96ef955de9f8b5da6a626069\`; register \`fede0159caa349bb3295f2ff1025f57cb37a1d231172f5d8d810c484421ec2e1\`; dependency \`fdffaa7ede862db19c306d15153e55edbd35c0c13b7e97cb3cab37de2ae384fa\`.

## Nonlocal SK/KMS Memory-Kernel Control (2026-08-14)
MAJOR_RESULT_CLOSURE: \`CLOSED_FOR_LANE\` for \`T13_UET_O2_NONLOCAL_SK_KMS_MEMORY_KERNEL_LANE\`; Full Topic 13 remains \`PARTIAL\` and \`BLOCKED_OPEN_T13_FULL_BRIDGE\`.
WHAT_IS_ACTUALLY_CLOSED: The explicit causal exponential memory kernel, action-derived collision-width source, retarded transfer function, lower-half-plane memory pole, positive spectral density, KMS/FDT noise, and formal nonnegative entropy witness.
WHAT_REMAINS_OPEN: Physical retarded self-energy/dissipative kernel, unique physical renormalization, condensed/two-fluid completion, physical Kubo coefficient, entropy-current/heat-flux/dissipative balance, dimensional \`Phi\` map, independent \`alpha_Phi_K\`, Ding-compatible numeric \`C_src\`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Formal action-derived nonlocal SK/KMS memory control only. Core curved 3+1, Gravity, full constitutive transport, Galaxy, SI, alpha, source, and external-validation dependencies remain blocked.
STATUS: \`PASS_ACTION_DERIVED_NONLOCAL_SK_KMS_MEMORY_KERNEL_LANE\`; full gate remains \`BLOCKED_OPEN_T13_FULL_BRIDGE\` at \`PARTIAL\`; downstream dependency remains \`BLOCKED_DOWNSTREAM_MAJOR_RESULTS\`.
WHAT_CHANGED: Added the nonlocal memory-kernel module, machine-readable verifier/artifact, regression tests, full-gate/register mappings, and formula-audit entry \`T13-068\`. The damping rate is inherited from the action-derived normal collision-width comparator; no target rows, fitting, Landauer shortcut, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: \`S_IF=integral dt dt' [Phi_a(t) K_R(t-t') Phi_r(t')+i Phi_a(t) N(t-t') Phi_a(t')/2]\`; \`g_R(t)=gamma_memory/memory_time*exp(-t/memory_time)*Theta(t)\`; \`rho(omega)=2 gamma_memory omega/(1+omega^2 memory_time^2)\`; \
=rho*coth(beta_th*omega/2)\`. Natural units only; \`Phi\` is not temperature, \`C\` is not mass or charge, \`R_gen\` is a derived history trace, and \`R_obs\` is separate.
VERIFICATION: Zero failed checks. Negative-time support \`0\`; memory pole imaginary part \`-0.7039206634854508\`; spectral minimum \`3.0393357701529953e-07\`; maximum causal-transform residual \`5.357171079777344e-14\`; maximum KMS residual \`7.488546547861213e-16\`; maximum FDT residual \`4.2351647362715017e-22\`; kernel-reality residuals \`0\`; formal entropy witness \`2.4883064269456041e-05\`. New regression passed \`3\` tests; Topic 13 suite passed \`295\` tests. Full gate and dependency audit keep downstream promotion blocked.
CONTROLLING_BLOCKER: \`physical_retarded_self_energy_and_dissipative_kernel_missing\`; unique physical renormalization, condensed/two-fluid, entropy-current, physical Kubo, dimensional, independent \`alpha_Phi_K\`, Ding source, and holdout boundaries remain independent.
NEXT_ACTION: Replace the formal collision-width memory control with a state-matched microscopic retarded self-energy and entropy-current/dissipative kernel. Keep physical Kubo, \`alpha_Phi_K\`, TTG source, and Xie holdout access independent.
CLAIM_BOUNDARY: This closes only a formal action-derived nonlocal SK/KMS memory-kernel control. It is not a physical retarded self-energy, unique renormalization, condensed/two-fluid closure, physical Kubo coefficient, entropy-current closure, SI observable, \`alpha_Phi_K\` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module \`9a80cbb16f227c102da432e461c8648c86f07a4ad8cea269f848b4f172efcb93\`; verifier \`45650c47511442673c364d03ad08a465228b49c6b1b466b116639f204c06705d\`; regression \`61c0182afe1853712a4ce930d7d7b955971b05b7ee82c6d378c4799c0d50d6c8\`; artifact \`84081e77a4900f970a5306da97d6b24e430ff895e061dab14d6f9c278de7b74f\`; full gate \`c5f9dacc36eb7531d456d08bf7f374ad14101ab1326b56a3bb4fa11deb65b7d4\`; register \`e34194a6369c5423ef5b66e4fdc4bf4c280789b5df919d92594bf4f1765d0590\`; dependency \`84b35561345d3140e92c403701f31e528fd7d00aa6f34760d84bbadaea0f1fe8\`.

## One-Loop Retarded Self-Energy Dissipation No-Go (2026-08-14)
MAJOR_RESULT_CLOSURE: \`CLOSED_AS_NO_GO\` for \`T13_UET_O2_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO\`; Full Topic 13 remains \`PARTIAL\` and \`BLOCKED_OPEN_T13_FULL_BRIDGE\`.
WHAT_IS_ACTUALLY_CLOSED: The local quartic one-loop retarded correction is a real, external-frequency-independent tadpole with exactly zero imaginary part and zero dissipative spectral density. The one-loop route cannot close physical dissipation.
WHAT_REMAINS_OPEN: Two-loop sunset or microscopic retarded self-energy, physical dissipative kernel, unique physical renormalization, condensed/two-fluid completion, physical Kubo coefficient, entropy-current/heat-flux/dissipative balance, dimensional \`Phi\` map, independent \`alpha_Phi_K\`, Ding-compatible numeric \`C_src\`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: One-loop dissipation no-go only. It does not unlock physical transport, Core curved 3+1, Gravity, Galaxy, SI, alpha, source, or external validation.
STATUS: \`PASS_ACTION_DERIVED_ONE_LOOP_RETARDED_SELF_ENERGY_NO_GO\`; closure level is \`CLOSED_AS_NO_GO\`; full gate remains \`BLOCKED_OPEN_T13_FULL_BRIDGE\` at \`PARTIAL\`; downstream dependency remains \`BLOCKED_DOWNSTREAM_MAJOR_RESULTS\`.
WHAT_CHANGED: Added the one-loop tadpole/self-energy no-go module, machine-readable verifier/artifact, regression tests, full-gate/register mappings, and formula-audit entry \`T13-069\`. No source rows, fitting, target data, Landauer shortcut, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: \`Sigma_R^(1)(omega,k)=3 lambda [I_vac^R+I_thermal]\`; \`I_thermal=integral[(n_-(E)+n_+(E))/(4E)]d^3k/(2*pi)^3\`; \`Im Sigma_R^(1)=0\`; \`rho_Sigma^(1)=0\`. Natural units only; \`Phi\` is not temperature, \`C\` is not mass or charge, \`R_gen\` is a derived history trace, and \`R_obs\` is separate.
VERIFICATION: Zero failed checks. Thermal tadpole \`0.00022235021208668495\`; real self-energy \`0.000533640509008044\`; imaginary and spectral maxima \`0\`; frequency-independence residual \`0\`; stable normal branch and no-go requirement pass. New regression passed \`3\` tests; Topic 13 suite passed \`298\` tests. Full gate and dependency audit keep downstream promotion blocked.
CONTROLLING_BLOCKER: \`two_loop_sunset_or_microscopic_retarded_self_energy_missing\`; physical Kubo, entropy-current, dimensional, independent \`alpha_Phi_K\`, Ding source, and holdout boundaries remain independent.
NEXT_ACTION: Derive the two-loop sunset self-energy or obtain a state-matched microscopic retarded correlator with units and uncertainty. Do not promote the one-loop zero spectral part or the formal memory rate to physical transport.
CLAIM_BOUNDARY: This closes only a structural one-loop dissipation no-go. It is not a two-loop/microscopic retarded self-energy, physical dissipative transport closure, physical Kubo coefficient, entropy-current closure, SI observable, \`alpha_Phi_K\` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module \`a0e04de5efe2c23d93ef91a56766c38cc359c4787b5f51f2c7f97fa839a5f84e\`; verifier \`a288483701b491f7fff758041cbb5a1d00c95b798ad4f8ab7ec90df618cd2c9d\`; regression \`1ca5e1b87a894b97ccf39afe350baf49ca6dd3d4562831782eb1b26a177208f2\`; artifact \`f240e594ea1c167cd7aeed88028b636b9ee25cfe1a2925087b4e05ae2bf7189f\`; full gate \`35d8dd76f66430a229b3962561beb1ef4c78cfd43ab88f4c9773d04e2b997580\`; register \`92dc131cb735c788cffa6e9145aeb8142e12830c456d67710458718f72acfc4d\`; dependency \`9cf5089af1e6f6a278c0ba5ab16a6b519ef91c4428d46bb1121704d0f2d7a9e6\`.

## Finite-Channel Two-Loop Sunset Cut
MAJOR_RESULT_CLOSURE: \`CLOSED_FOR_LANE\` for \`T13_UET_O2_TWO_LOOP_SUNSET_CUT_LANE\`; Full Topic 13 remains \`PARTIAL\` and \`BLOCKED_OPEN_T13_FULL_BRIDGE\`.
WHAT_IS_ACTUALLY_CLOSED: The first nonzero action-derived order-lambda^2 finite-channel elastic phase-space cut is explicit. Forward and reverse Bose-weighted rates are evaluated separately; every active channel has positive symmetric cut weight and detailed balance passes.
WHAT_REMAINS_OPEN: The continuum 1PI sunset integral, regulator/subtraction matching, full retarded self-energy, physical Kubo/transport, entropy-current/heat-flux balance, dimensional \`Phi\` map, independent \`alpha_Phi_K\`, Ding-compatible \`C_src\`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Finite-channel two-loop phase-space cut interface only. No physical self-energy, Kubo, SI, alpha, Core, Gravity, Galaxy, or external-validation dependency is unlocked.
STATUS: \`PASS_ACTION_DERIVED_TWO_LOOP_SUNSET_CUT_LANE\`; closure level \`CLOSED_FOR_LANE\`; full gate remains \`BLOCKED_OPEN_T13_FULL_BRIDGE\` at \`PARTIAL\`; downstream dependency remains \`BLOCKED_DOWNSTREAM_MAJOR_RESULTS\`.
WHAT_CHANGED: Added the two-loop sunset-cut module, refreshed the transition-kernel reverse-rate field and artifact, verifier, regression tests, full-gate/register integration, and formula-audit entry \`T13-070\`. No source rows, fitting, target data, Landauer shortcut, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: \`W_>^(2)=integral dPi_1...dPi_4 delta^4(P_in-P_out)|M_22|^2 f1*f2*(1+f3)*(1+f4)\`; \`W_<^(2)=integral ... f3*f4*(1+f1)*(1+f2)\`; \`W_cut^(2)=0.5*(W_>^(2)+W_<^(2))\`. Natural units only; \`Phi\` is not temperature, \`C\` is not mass or charge, \`R_gen\` is a derived history trace, and \`R_obs\` is separate.
VERIFICATION: Zero failed checks. Reference 12-channel forward/reverse/symmetric cut totals are \`2.133294206254412e-18\`, \`2.1332942062544197e-18\`, and \`2.1332942062544158e-18\`; maximum detailed-balance residual \`1.755777910152043e-14\`; conservation residual \`6.75000790405693e-29\`; KMS/FDT residuals \`1.3467686071081029e-16\` and \`1.5206645789855688e-16\`; formal entropy witness \`2.2494043957344814e-18\`. Focused sunset plus transition regression: \`6\` passed.
CONTROLLING_BLOCKER: \`continuum_sunset_integral_and_full_retarded_self_energy_missing\`; independent \`alpha_Phi_K\` calibration remains open with zero eligible paired records.
NEXT_ACTION: Derive and verify the continuum 1PI sunset retarded self-energy with explicit regulator/subtraction, then match its KMS/entropy kernel. Keep the finite-channel result as a non-promoted lane and keep source/calibration/holdout gates independent.
CLAIM_BOUNDARY: This closes only a finite-channel action-derived two-loop phase-space cut interface. It is not a continuum 1PI self-energy, physical dissipative transport or Kubo coefficient, entropy-current closure, SI observable, \`alpha_Phi_K\` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module \`9c4e4c569a6df5a92017dde3be656060197f34a7eb7ece390269cc006b5e7add\`; verifier \`7a24a05a45286627be600e73666c446dd2a694e5cd3d02feebc23791ed256dc0\`; regression \`0388f78bd6aa18de51aafba404e0bbbc509a1f9a04a9acf1ddea88cb152ad4d6\`; sunset artifact \`23f01a422f3b217e3065bf531a29182496083cfabb1bc145ce8cb25fe8f5d73c\`; transition artifact \`44b950f76b99138395150372501c9a2714d2d132adc26daa6894c1d933f6a9d1\`; full gate \`c70f03cdb1e1c4eee0deb4dd7e8707b745ccfc0eb303dd6804f406560d714e10\`; register \`7a453b9bcc91124559e75ac5504fd4f8a6718be512f092a32b33082f6b2afd5a\`; dependency \`78dadd6eed2c8e5580e7238c0d4ab8c98cff1df0290d8d3aa58aa1ea8911c3d9\`.

## Continuum Neutral On-Shell Sunset Cut (2026-08-14)
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_CONTINUUM_SUNSET_CUT_LANE`; Full Topic 13 remains `PARTIAL` and `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The neutral p=0 continuum on-shell elastic 2-to-2 sunset-cut phase-space integral is evaluated in the declared natural-unit convention. Greater/lesser weights, the spectral/noise cut, KMS ratio, and independent radial, CM-angle, and cutoff convergence controls are explicit.
WHAT_REMAINS_OPEN: Full 1PI retarded self-energy, real-part subtraction, off-shell matching, regulator-scheme matching, physical Kubo/transport, covariant entropy-current/heat-flux balance, dimensional `Phi` map, independent `alpha_Phi_K`, Ding-compatible numeric `C_src`, and Full Topic 13 closure remain open.
DEPENDENCY_UNLOCKED: Neutral continuum on-shell sunset-cut lane only. No full retarded self-energy, physical Kubo, entropy-current, SI, alpha, source, Core, Gravity, Galaxy, or external-validation dependency is unlocked.
STATUS: `PASS_ACTION_DERIVED_CONTINUUM_SUNSET_CUT_LANE`; closure level `CLOSED_FOR_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` at `PARTIAL`; downstream dependency remains `BLOCKED_DOWNSTREAM_MAJOR_RESULTS`.
WHAT_CHANGED: Added the continuum sunset-cut module, verifier, artifact, regression test, full-gate lane mapping, continuum major-result registry/dependency sync extension, and formula-audit entry `T13-072`. Reference uses `48/40` quadrature and cutoff factor `24`; no source rows, fitting, Landauer shortcut, target data, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: `p=(E_p,0,0,0)`, `E_p=m_eff`; `Gamma_>^cut=integral d^3k/(2*pi)^3 n_k v_rel sigma_22 <(1+n_3)(1+n_4)>_CM`; `Gamma_<^cut=integral d^3k/(2*pi)^3 (1+n_k) v_rel sigma_22 <n_3 n_4>_CM`; `rho_cut=2*E_p*(Gamma_>-Gamma_<)`;
_cut=2*E_p*(Gamma_>+Gamma_<)`; `Gamma_>/Gamma_<=exp(beta*E_p)`. Natural units only; `Phi` is not temperature, `C` is not mass or charge, `R_gen` is a derived history trace, and `R_obs` is separate.
VERIFICATION: Continuum verifier has zero failed checks. Greater/lesser cut weights are `9.52491443174392e-07` and `3.8840193632612374e-08`; spectral/noise cuts are `1.2862704057367969e-06` and `1.3956315906479364e-06`; KMS residual is `2.8974136869086344e-16`; radial, angular, and cutoff residuals are `1.2354253257923907e-10`, `0`, and `1.7723202010929002e-09`, below threshold `1e-8`. Continuum regression and two inherited Topic 13 lanes: `9` passed. Full gate remains blocked.
CONTROLLING_BLOCKER: `full_1PI_retarded_self_energy_real_part_subtraction_and_off_shell_match_missing`; independent `alpha_Phi_K` calibration remains open with zero eligible paired records.
NEXT_ACTION: Derive the real and imaginary parts of the full 1PI retarded self-energy with an explicit regulator/subtraction and off-shell matching, then connect the matched KMS kernel to covariant entropy/heat-flux balance while keeping source, alpha, and holdout gates independent.
CLAIM_BOUNDARY: This closes only the declared neutral p=0 continuum on-shell sunset-cut lane. It is not a full 1PI retarded self-energy, real-part renormalization, off-shell prediction, physical Kubo coefficient, entropy-current closure, SI observable, `alpha_Phi_K` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module `d5f597c2669775cd49e8a1f20014c1acc458b79c4224906bc362c75ada6f2972`; verifier `598eaa97ba5dd19e55b5e6722c0f78ddd045b0c168ea9b4927043c4e996f7d8e`; regression `59abc7c819719e6a38078c3e7cfe3e1bc7f6a8695dad1a856de63435f42444d0`; artifact `5944a7a18f8d657671a7c06f11fde6d7fa1c6d79cd94bc21dbf9c57d70bac663`; full gate `74873b6734cfbd12f99bb34065100feb72f4324a298d4947f32bb8c1b1984d60`; register `bffcb1b2ca690b22f4cf3e99b3a1c63d053e0324f1c3ce0f854a4f219bac940e`; dependency `2c766a1587de4fd93447997b28b6e1418bbbcf05f64965b558fc7391703acd82`.


LATEST_METADATA_HASHES: After the generated full-entry sync and continuum lane extension, canonical full gate is `74873b6734cfbd12f99bb34065100feb72f4324a298d4947f32bb8c1b1984d60`, register is `a0fcf7baa146c4a4c3fc07c2096f75135fd05c8b4c6e83bb35b68286c662a196`, and dependency gate is `af42da13534cd9ed36b1f11da082b64700573eb6474959058603c79255ee35ad`.


## Finite-Channel Entropy Balance and H-Theorem
MAJOR_RESULT_CLOSURE: \`CLOSED_FOR_LANE\` for \`T13_UET_O2_FINITE_CHANNEL_ENTROPY_BALANCE_LANE\`; Full Topic 13 remains \`PARTIAL\` and \`BLOCKED_OPEN_T13_FULL_BRIDGE\`.
WHAT_IS_ACTUALLY_CLOSED: The formal finite-channel entropy affinity and H-theorem identity is explicit. A declared positive internal affinity produces nonnegative channel entropy production, and the discrete entropy-balance divergence matches the summed production.
WHAT_REMAINS_OPEN: Covariant continuum entropy current, physical heat-flux/dissipative balance, physical Kubo/transport, dimensional \`Phi\` map, independent \`alpha_Phi_K\`, Ding-compatible \`C_src\`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Finite-channel formal entropy balance only. No covariant entropy current, physical heat flux, Kubo, SI, alpha, Core, Gravity, Galaxy, or external-validation dependency is unlocked.
STATUS: \`PASS_ACTION_DERIVED_FINITE_CHANNEL_ENTROPY_BALANCE_LANE\`; closure level \`CLOSED_FOR_LANE\`; full gate remains \`BLOCKED_OPEN_T13_FULL_BRIDGE\` at \`PARTIAL\`; downstream dependency remains \`BLOCKED_DOWNSTREAM_MAJOR_RESULTS\`.
WHAT_CHANGED: Added the finite-channel entropy-balance module, verifier, artifact, regression tests, full-gate/register integration, and formula-audit entry \`T13-071\`. The affinity is an internal declared witness; no source rows, fitting, target data, Landauer shortcut, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: \`A_c=log(W_f,c/W_r,c)\`; \`sigma_c=(W_f,c-W_r,c)*A_c/T>=0\`; \`partial_mu S^mu_discrete=sum_c sigma_c\`. Natural units only; \`Phi\` is not temperature, \`C\` is not mass or charge, \`R_gen\` is a derived history trace, and \`R_obs\` is separate.
VERIFICATION: Zero failed checks. Reference equilibrium entropy production \`3.5592569872372884e-52\`; positive-affinity production \`2.272374294421268e-27\`; balance divergence \`2.2723742944212683e-27\`; balance residual \`3.5873240686715317e-43\`; minimum channel production \`7.6677620444810345e-67\`; detailed-balance/conservation/KMS/FDT residuals pass. Focused entropy regression: \`3\` passed.
CONTROLLING_BLOCKER: \`covariant_continuum_entropy_current_and_heat_flux_balance_missing\`; independent \`alpha_Phi_K\` calibration remains open with zero eligible paired records.
NEXT_ACTION: Derive the covariant entropy current and heat-flux balance from the continuum retarded/KMS kernel; retain this finite-channel H-theorem as a formal lane and keep physical Kubo, dimensional, source, and holdout gates independent.
CLAIM_BOUNDARY: This closes only a finite-channel formal entropy-production identity with a declared internal affinity. It is not a covariant entropy current, physical heat-flux balance, physical Kubo coefficient, SI observable, \`alpha_Phi_K\` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module \`418247b1b61d23bdf0ee5212b5b4969216d1ced539636b741b04edd35e876f92\`; verifier \`821ae8f6b24f0f5b3dddbfa10aef92623461e1464c054033f666ddb8305aaeeb\`; regression \`fe703b73071d47668e18b8c619257409219fd91dd6bf521b79a9faa2dd1b374c\`; artifact \`7a21a03c87c0b39d619cb23bc459643a8c41b7ae792beed88425e0129996968d\`; full gate \`ecb6153b8e66dd7f8fed4f5c7f7898b3ff3a7bccbeb736fb389b9bf96c883fa7\`; register \`3f1e9b5550bc8a56b5d100126687c39c1f25314a81cef6a1416c8e879d55fb70\`; dependency \`3384957f4f439de2e22d213e76a6c6f332e25107d03941343b5beb06cd2b20f5\`.

## Condensed Loop-Renormalized Contact Vertex (T13-114)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The condensed relative-flow contact channel now has a finite thermal derivative-channel loop bubble, explicit reference subtraction, positive effective coupling, and a state-matched natural-unit retarded response. Radial, angular, compactification-scale, positivity, conservation, KMS/FDT, and entropy checks pass.
WHAT_REMAINS_OPEN: Complete condensed 1PI vertex and scattering channels, independent physical Kubo/vertex anchor and accepted provenance, complete two-fluid tensor, dimensional `Phi` map, independent calibration, Ding-compatible `C_src`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Loop-renormalized condensed contact-channel and state-matched natural retarded lane only; no physical Kubo, SI, alpha, Core, Gravity, or external-validation unlock.
STATUS: `PASS_ACTION_DERIVED_CONDENSED_LOOP_RENORMALIZED_CONTACT_VERTEX_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.
WHAT_CHANGED: Added the action-derived condensed thermal loop/contact implementation, audit, focused regression, equation addendum, full-gate projection, major-result register entry, dependency evidence, and wave record. No external numeric source, target data, fit, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: `B_ab^R=B_ab^th(T,mu,Phi)-B_ab^th(T,mu,Phi_ref)`; `lambda_ab^R=lambda/(1+lambda*B_ab^R)`; `sigma_ab^R=(lambda_ab^R)^2/[16*pi*(s_med+2*lambda*A_*^2)]`; `L_rel=Gamma_rel*((1,-1),(-1,1))`; `G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)`.
VERIFICATION: Zero failed checks; numerical uncertainty bound `3.500054507989025e-06`; loop-bubble relative change `9.321205929180344e-13`; loop-coupling relative change `3.261235996489399e-14`; focused regression `2 passed`; KMS/FDT, entropy, positivity, and common-flow conservation pass.
CONTROLLING_BLOCKER: `physical_Kubo_coefficient_record_missing`, with `independent_physical_condensed_vertex_anchor_missing` and `complete_condensed_1PI_vertex_and_scattering_channels_missing`.
NEXT_ACTION: Source-lock or microscopically match one state-matched physical condensed Kubo/retarded record with units, locator, hash, evidence status, and uncertainty; then test full interacting SK/KMS and complete scattering-channel admission.
CLAIM_BOUNDARY: Natural-unit loop-renormalized contact-channel lane only; not a full 1PI renormalization, physical Kubo coefficient, SI observable, `alpha_Phi_K` calibration, TTG prediction, external validation, or Full Topic 13 closure.
EVIDENCE_HASHES: module `6384e8bc5553b696c17a079b93fd97df95b8f545475732b2a23f7133f03fe0dc`; audit `6a3b581978b4020648c5f2c9b9d38fef4aed501267190e5a8c5c2178e666737b`; registry `ae143f9bd06738ae777415b46d39752c8fbb4a96b17f31de94eac3e563a7be44`; full gate `3336e8e0ee0fa3e0d4f455f39010a3c9426af8583074d830c8143518dbc94c09`; register `fd0db3bd2358b0e66c480464ddf088e13fa37ccb8b0b1df0a542ec383740078d`; dependency `ec6199d171b0aea536c0f072e498c0bfd9988ae66612bedfac94d422b5462637`.

## 2026-08-20 - State-matched Kubo admission and condensed SK/KMS match (T13-115/T13-116)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_CONDENSED_RELATIVE_FLOW_KUBO_ADMISSION_LANE` and `T13_UET_O2_CONDENSED_SK_KMS_KUBO_MATCH_LANE`.
WHAT_IS_ACTUALLY_CLOSED: One declared condensed relative-flow contact channel now has a machine-readable state-matched natural-unit Kubo record, plus a matched retarded lower-half-plane pole, positive spectral matrix, KMS ratio, FDT identity, zero-frequency Kubo match, and nonnegative entropy witness.
WHAT_REMAINS_OPEN: Full finite-temperature retarded 1PI self-energy, all-channel renormalization, complete two-fluid transport, SI conversion, independent physical vertex anchor, dimensional Phi map, independent alpha_Phi_K, Ding-compatible C_src, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Declared-channel Kubo and SK/KMS/FDT lanes only; `full_core_unlock=false`; no physical global coefficient, Core, Gravity, Galaxy, SI, or external-validation dependency is unlocked.
STATUS: `PASS_KUBO_MATCHED_DECLARED_CONDENSED_RELATIVE_FLOW_CHANNEL` and `PASS_ACTION_DERIVED_CONDENSED_SK_KMS_KUBO_MATCH_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_CHANGED: Added the state-matched Kubo admission builder/audit and the condensed SK/KMS/Kubo response audit, then synchronized full-gate mappings, closure register, dependency projection, and update records. No fit, synthetic replacement, target residual, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: `K_rel^natural=lim_(omega->0) Re G_R^rel(omega)=D_rel/Gamma_rel`; `G_R^rel(omega)=2*D_rel/(2*Gamma_rel-i*omega)*P_rel`; `G^K=rho*coth(omega/(2*T))`.
VERIFICATION: Both audits have zero failed checks. Kubo coefficient `2.713283847206443e-05` with quadrature uncertainty `3.500054507989025e-06` is `KUBO_MATCHED` in natural units only. SK/KMS residuals are KMS `0`, FDT `2.1815250606323664e-16`, retarded reality `0`, spectral PSD minimum `0`, and zero-frequency match `0`; focused tests `4 passed`. Wave 1 integrity is `PASS_WITH_BLOCKED_LANES` with no hash errors and holdout access clean.
CONTROLLING_BLOCKER: `full_finite_temperature_retarded_1PI_self_energy_missing`, `independent_physical_condensed_vertex_anchor_missing`, and the full-bridge dimensional/alpha, Ding C_src, EOS/transport/KMS/entropy closure groups.
NEXT_ACTION: Derive the full finite-temperature condensed retarded self-energy and all-channel SK/KMS kernel, or source-lock an independent physical condensed vertex anchor. Keep this coefficient scoped to the declared natural-unit lane and do not promote it to SI or Full Topic 13.
CLAIM_BOUNDARY: Action-derived declared-channel result only; not an external measurement, complete interacting 1PI theory, SI thermal transport, alpha_Phi_K calibration, TTG prediction, external validation, or global UET closure.
DATA_ROLE: `DERIVED_INTERNAL_NATURAL_UNIT`; the admitted coefficient is not a calibration, training, comparison, or holdout record. No external numeric source was consumed by these two lanes.
EVIDENCE_PATHS: `docs/core/uet_o2_condensed_relative_flow_kubo_admission.py`; `docs/core/artifacts/t13_uet_o2_condensed_relative_flow_kubo_admission_audit.json`; `docs/core/uet_o2_condensed_sk_kms_kubo_match.py`; `docs/core/artifacts/t13_uet_o2_condensed_sk_kms_kubo_match_audit.json`.
EVIDENCE_HASHES: Kubo module `92dea65cf85d2fc2054e4f5c0b293712d2ea0b8b0df65ffa5e4b95de9dd2df67`; Kubo audit `5e909ff97aa0476619235460c012313f36b6065e642bbe4f7fba63f36bd8c7f6`; SK/KMS module `ab6fabaca6d2a19f8185535928638ecf4f1581cd2ad89ada78ed89e5341aff72`; SK/KMS audit `d13d59760f9ebe0a3d2471ad984ec95c6729846d08b2b9ce011e2e8eb2fcaf1c`; registry `ae143f9bd06738ae777415b46d39752c8fbb4a96b17f31de94eac3e563a7be44`; full gate `4b69d2f13ef9827f11898edc63b254dd837943b3ccdf4b88f7fe52b2ea0d2415`; register `6d41189d970ba4b17bb889176412fc66ed4b9cbcd02a8520d014ddc61800ddb0`; dependency `83f6351dc2ccee0f3ba80a593c2081ca82e04d0b0b9d5b69ec9ad91754bfff1d`.
## 2026-08-20 - Declared finite-temperature retarded 1PI response grid (T13-117)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The audited action-derived 1<->3 and labeled 2<->2 finite-temperature sunset channels are evaluated on one matched timelike invariant grid. The assembled pole-subtracted retarded response has a positive spectral grid, lower-half-plane imaginary part, grid-level KMS/FDT checks, retarded i0 consistency, and PV convergence.
WHAT_REMAINS_OPEN: Complete finite-temperature retarded 1PI self-energy, all sunset cuts, unique physical renormalization, physical Kubo transport, covariant entropy/heat-flux closure, dimensional Phi mapping, independent alpha_Phi_K, Ding C_src, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Declared retarded response-grid lane only; `full_core_unlock=false`; no physical Kubo, SI, alpha, Core, Gravity, Galaxy, or external-validation dependency is unlocked.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.
WHAT_CHANGED: Added the multi-invariant state-matched retarded response builder, focused regression, audit artifact, full-gate mapping, closure-register entry, dependency projection, and wave record. No target data, fit, synthetic replacement data, Landauer shortcut, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: `Sigma_R,T^declared(s+i0)=Re Sigma_R,T^declared,sub(s)-i*pi*rho_T^declared(s)`; `rho_T^declared=rho_>,13+rho_>,22-rho_<,13-rho_<,22`; `log(rho_>/rho_<)=sqrt(s)/T`;
_T=rho_T*coth(sqrt(s)/(2*T))`.
VERIFICATION: Audit has zero failed checks on `s={4.75,5.0,5.5}` with threshold `4.5`. Maximum KMS residual `8.881784197001252e-16`; maximum FDT residual `0.003942955405912313`; maximum PV inner/outer residuals `0.0004183177470783957` / `0.00028892386785935357`; retarded i0 residual `6.776263578034403e-21`; focused regression `3 passed`. Wave 1 integrity remains `PASS_WITH_BLOCKED_LANES`, with no hash errors and no holdout consumption.
CONTROLLING_BLOCKER: `complete_finite_temperature_1pi_self_energy_and_all_channel_physical_renormalization_missing`; independent physical vertex/Kubo provenance, dimensional Phi anchor, alpha_Phi_K, Ding C_src, and EOS/transport/KMS/entropy completion remain full-bridge blockers.
NEXT_ACTION: Derive the remaining finite-temperature interacting 1PI channels and an independent physical renormalization/vertex anchor. Keep this grid as a declared natural-unit lane and do not promote it to physical SI transport.
CLAIM_BOUNDARY: Action-derived internal evidence for the declared two-channel response grid only; not a complete interacting 1PI theory, physical Kubo coefficient, SI thermal transport, alpha_Phi_K calibration, TTG prediction, external validation, or global UET closure.
DATA_ROLE: `ACTION_DERIVED_FINITE_T_DECLARED_RETARDED_1PI_RESPONSE_GRID_NO_HOLDOUT`.
EVIDENCE_HASHES: module `f635e131e00c295cb90bf51607a8c41b392fef4af610682d9c4d3bc99e504885`; audit script `c2c379f776a48d0c4daad099696042e3c205ded0f51dcc7893a959ebe9d2c281`; audit artifact `f22d74b88c82e62bb0dc984bc96b1171bc2b7579d563d693fa3559ac199e3861`; full gate `53f40cd31b9cba7d608aeb5e8a3d48d3dc204302c478c16d4bb165a96f66a9ee`; register `8561401dec879ebc1b3c98f438e0ea774e8a8bacaf9cbe6cacae0ab1b25b985c`; dependency `cc3ef8f07c4e16037d9d232f40487f5de6cd841f9b12ddc8f163541bc7f820fd`.
## Signed-Cut Kinematic Taxonomy (2026-08-20, T13-118)
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE`.
WHAT_IS_ACTUALLY_CLOSED: All eight positive-external-energy equal-mass sign assignments are enumerated. One `1<->3` assignment and three `2<->2` permutations are kinematically allowed; the remaining assignments are forbidden. The current scattering module covers one labeled `2<->2` pattern, so the two-pattern multiplicity gap is now explicit.
WHAT_REMAINS_OPEN: Action-level cut multiplicity, complete finite-temperature 1PI self-energy, physical renormalization, physical Kubo, entropy/heat-flux closure, dimensional `Phi` map, independent `alpha_Phi_K`, Ding `C_src`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Signed-cut taxonomy only; `full_core_unlock=false`.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_SIGNED_CUT_KINEMATIC_TAXONOMY_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_CHANGED: Added the signed-cut classifier, audit, regression, gate/register projection, and corrected the composition state so `all_finite_temperature_sunset_channels_completed=false` remains honest.
EQUATION_OR_MAPPING: `P0=sigma_1 E_1+sigma_2 E_2+sigma_3 E_3`; `+++` is `1<->3`; `-++`, `+-+`, and `++-` are the three `2<->2` permutations; current labeled coverage is `++-`; missing permutations are `2`.
VERIFICATION: Signed-cut audit zero failed checks; 8 assignments, 4 allowed, 1 `1<->3`, 3 `2<->2`, and 2 missing labeled permutations. Focused regression `3 passed`; full sunset regression `3 passed`; Wave 1 integrity `PASS_WITH_BLOCKED_LANES`; holdout not consumed.
CONTROLLING_BLOCKER: `action_level_signed_cut_multiplicity_and_complete_finite_temperature_1pi_missing`, alongside the full-gate dimensional/alpha, source, and EOS/transport/KMS/entropy blockers.
NEXT_ACTION: Derive the action-level multiplicity and identical-state symmetry factor, then connect it to the complete retarded/advanced/Keldysh 1PI object and physical renormalization.
CLAIM_BOUNDARY: This is a natural-unit kinematic taxonomy lane only; it is not full 1PI closure, physical transport, SI mapping, `alpha_Phi_K` calibration, TTG validation, or global UET closure.
## Sunset Cut Multiplicity (2026-08-20, T13-119)
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE`.
WHAT_IS_ACTUALLY_CLOSED: From `S_sunset=1/6`, one `1<->3` pattern has weight `1/6` and three equal-mass `2<->2` sign permutations have graph weight `3/6=1/2`. The existing representative factor `0.5` matches this graph-summed weight. The species-resolved physical final-state factor `1/(1+delta_cd)` remains separate.
WHAT_REMAINS_OPEN: Physical scattering normalization identity, complete finite-temperature 1PI, physical renormalization, Kubo, entropy/heat-flux, dimensional `Phi`, independent `alpha_Phi_K`, Ding `C_src`, and Full Topic 13.
DEPENDENCY_UNLOCKED: Action-level cut multiplicity only; `full_core_unlock=false`.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_SUNSET_CUT_MULTIPLICITY_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_CHANGED: Added multiplicity derivation/audit/test and clarified the existing scattering factor semantics without changing its numeric value.
EQUATION_OR_MAPPING: `w_13=1*(1/6)=1/6`; `w_22=3*(1/6)=1/2`; `w_final(c,d)=1/(1+delta_cd)` is comparator-only.
VERIFICATION: Audit zero failed checks; `w_13=0.16666666666666666`, `w_22=0.5`, ratio `3`; physical final-state weights `{0.5,1.0}`; focused tests `6 passed`; holdout not consumed.
CONTROLLING_BLOCKER: `physical_scattering_normalization_identity_and_complete_finite_temperature_1pi_missing` plus the 11 full-bridge blockers.
NEXT_ACTION: Evaluate complete retarded/advanced/Keldysh 1PI with this graph weight and establish a physical renormalization anchor.
CLAIM_BOUNDARY: Natural-unit action-level multiplicity only; not physical transport, SI mapping, `alpha_Phi_K`, TTG validation, or Full Topic 13 closure.
## All Positive-Energy On-Shell Cut Response (2026-08-20, T13-120)
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The `1<->3` plus all three equal-mass `2<->2` positive-energy cuts are represented on `s={4.75,5.0,5.5}` with graph weight `w_22=1/2`. The combined spectral response passes positivity, retarded sign, KMS/FDT, i0, and PV convergence checks.
WHAT_REMAINS_OPEN: Complete off-shell finite-temperature 1PI, physical renormalization, physical scattering/Kubo normalization, entropy/heat-flux, dimensional `Phi`, independent `alpha_Phi_K`, Ding `C_src`, and Full Topic 13.
DEPENDENCY_UNLOCKED: All-positive-energy on-shell spectral response only; `full_core_unlock=false`.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_ALL_ONSHELL_CUT_SPECTRAL_RESPONSE_LANE`; full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_CHANGED: Integrated signed-cut taxonomy, action multiplicity, and matched retarded response into one evidence-producing lane.
EQUATION_OR_MAPPING: `rho_all=rho_(+++)+rho_(-++)+rho_(+-+)+rho_(++-)`; `rho_(2<->2,all)=(3/6)rho_(++-)`; `Sigma_R=Re Sigma_sub-i*pi*rho_all`.
VERIFICATION: Zero failed checks; maximum KMS `8.881784197001252e-16`, FDT `0.003942955405912313`, PV inner/outer `0.0004183177470783957` / `0.00028892386785935357`, i0 `6.776263578034403e-21`; focused all-onshell tests `3 passed`; holdout not consumed.
CONTROLLING_BLOCKER: `complete_off_shell_finite_temperature_1pi_and_physical_renormalization_missing` plus 11 full-bridge blockers.
NEXT_ACTION: Evaluate the complete off-shell retarded/advanced/Keldysh 1PI object and prove its physical subtraction anchor.
CLAIM_BOUNDARY: Natural-unit all-onshell spectral response only; not complete 1PI, physical transport, SI mapping, `alpha_Phi_K`, TTG validation, or Full Topic 13 closure.

## Declared-Channel Retarded/Advanced/Keldysh 1PI (T13-121)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_DECLARED_CHANNEL_RETARDED_ADVANCED_KELDYSH_1PI_LANE`; Full Topic 13 remains `PARTIAL` and `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The declared action-derived 1<->3 and representative 2<->2 thermal channels now emit a matched numerical retarded, advanced, and Keldysh component triplet. Retarded/advanced conjugacy, the spectral discontinuity, Keldysh component convention, FDT, and the existing BPHZ subtraction interface are checked on `s={4.75,5.0,5.5}`.
WHAT_REMAINS_OPEN: Complete off-shell all-channel finite-temperature 1PI, physical renormalization anchor, physical Kubo, covariant entropy/heat-flux balance, dimensional `Phi` map, independent `alpha_Phi_K`, Ding `C_src`, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Declared-channel real-time component interface only; `full_core_unlock=false`; no physical coefficient, SI, Core, Gravity, Galaxy, or external-validation dependency is unlocked.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_DECLARED_CHANNEL_RETARDED_ADVANCED_KELDYSH_1PI_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.
WHAT_CHANGED: Added a numerical component builder, audit artifact, focused tests, full-gate projection, major-result register entry, and dependency projection. No fit, target data, synthetic replacement, Landauer shortcut, or Xie 2026 holdout was used. The Calorine 300 K cross-check residual is 0.1756%; the IAEA comparator uncertainty remains explicitly unpromoted.
EQUATION_OR_MAPPING: `rho=rho_>-rho_<`;
=rho_>+rho_<`; `Sigma_R=Re Sigma_sub-i*pi*rho`; `Sigma_A=Re Sigma_sub+i*pi*rho=Sigma_R^*`; `Sigma_K=-2*i*pi*N`;
/rho=coth(sqrt(s)/(2*T))`.
VERIFICATION: Audit has zero failed checks; maximum retarded/advanced conjugacy, discontinuity, and Keldysh-convention residuals are `0`; maximum Keldysh FDT residual is `1.1620995061153706e-16`; focused regression `3 passed`; full gate remains blocked with 11 blockers.
CONTROLLING_BLOCKER: `complete_off_shell_all_channel_1pi_and_physical_renormalization_anchor_missing`; dimensional, alpha, source, EOS, transport, KMS, and entropy blockers remain independent.
NEXT_ACTION: Complete the off-shell all-channel finite-temperature 1PI evaluation and source-lock an independent physical renormalization anchor without using TTG target residuals or Xie 2026.
CLAIM_BOUNDARY: This closes only the declared-channel natural-unit real-time component interface. It is not a complete interacting 1PI theory, physical renormalization, physical Kubo coefficient, SI observable, `alpha_Phi_K` calibration, TTG prediction, external validation, or Full Topic 13 closure.
DATA_ROLE: `ACTION_DERIVED_FINITE_T_DECLARED_CHANNEL_RETA_KELDYSH_1PI_NO_HOLDOUT`.
EVIDENCE_PATHS: `docs/core/uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi.py`; `docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi.py`; `docs/core/test/test_topic13_uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi.py`; `docs/core/artifacts/t13_uet_o2_finite_temperature_declared_channel_retarded_advanced_keldysh_1pi_audit.json`.
EVIDENCE_HASHES: module `48ac15b10b64c81aa4c85dd7941ce8004022e61dc08acc655c9ab2ef4f25f013`; audit `6fb21ef9accc84f9af43197c22225d62b88d4a9670f482804be98d7be23bc5e4`; test `f5a6c71cc0dce44249a45803ff728544dcef69a704882e07dd797126e53f805e`; artifact `ff5a8ea3972f02189f7f4ff3413855946526faeb7b8c5317adc6c09ba3ebea2f`; full gate `ed5ec6babcca07b09925c33ffc3ec0389bfd2ed80eac49b23f2d1440577d38eb`; register `68a8b651ace97ae6dd99e7a64609203f381fb520d6a66ed56d7d9a433e455251`; dependency `6a8ba736e60b18c28bab998a09308d81a1cccfdef52bc88ec863ef56d5377b0a`.

## Off-Shell Threshold-Crossing Declared 1PI Lane (2026-08-20, T13-122)
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_OFFSHELL_THRESHOLD_CROSSING_1PI_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The declared natural-unit real-time response is now evaluated across a below/above three-body threshold grid. The `1<->3` spectral support is zero below `s_th=9*m^2` and nonzero above it, while the graph-summed `2<->2` channel remains nonzero at selected points below the three-body threshold. The combined retarded, advanced, and Keldysh component identities are checked on the same grid.
WHAT_REMAINS_OPEN: Complete off-shell all-channel finite-temperature 1PI closure, unique physical renormalization, physical Kubo provenance, covariant entropy and heat-flux balance, dimensional `Phi` to thermal observable mapping, independent `alpha_Phi_K`, Ding `C_src`, EOS and constitutive transport, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: The below/above-threshold declared response lane only; `full_core_unlock=false`. No Core, Gravity, Galaxy, physical transport, SI, or external-validation dependency is unlocked.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_OFFSHELL_THRESHOLD_CROSSING_1PI_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.
WHAT_CHANGED: Added the threshold-crossing response builder, audit artifact, focused regression, major-result register projection, full-gate projection, and dependency evidence. The PV quadrature resolution was increased from `16->24` to `48->64` only to resolve the low-`s` subtraction kernel; the threshold, acceptance gate, ontology, and data role were unchanged.
EQUATION_OR_MAPPING: `s_th=9*m^2`; `rho_13(s)=0` for `s<=s_th` and `rho_13(s)>0` for `s>s_th`; `rho_22(s)>0` on selected `s<s_th`; `rho=rho_13+rho_22`; `Sigma_R=Re Sigma_sub-i*pi*rho`; `Sigma_A=Sigma_R^*`; `Sigma_K=-2*i*pi*N`;
/rho=coth(sqrt(s)/(2*T))`.
VERIFICATION: Grid `s={0.25,1.0,4.0,4.75,5.0,5.5,7.0}` with `m^2=0.5`, `s_th=4.5`; focused regression `3 passed`; audit zero failed checks; maximum `1<->3` PV residual `6.103811254557431e-05`; maximum `2<->2` PV residual `0.014920561773350124`; maximum Keldysh FDT residual `2.6926011101365283e-16`; below-threshold zero/nonzero support witnesses all true; Xie 2026 not accessed.
CONTROLLING_BLOCKER: `complete_off_shell_all_channel_1pi_and_physical_renormalization_anchor_missing`, together with the 11 full-bridge blockers for source/calibration, dimensional mapping, EOS, transport, KMS/entropy, and heat-flux closure.
NEXT_ACTION: Continue from this crossing lane to the complete off-shell all-channel 1PI object and an independent physical renormalization anchor. Keep the action-derived natural-unit lane separate from physical TTG transport and do not use holdout data for calibration.
CLAIM_BOUNDARY: This is a declared action-derived natural-unit threshold-crossing response lane only. It is not complete interacting 1PI closure, physical renormalization, a physical Kubo coefficient, an SI observable, an `alpha_Phi_K` calibration, a TTG prediction, external validation, or global UET closure.
DATA_ROLE: `ACTION_DERIVED_FINITE_T_OFFSHELL_THRESHOLD_CROSSING_NO_HOLDOUT`.
EVIDENCE_PATHS: `docs/core/uet_o2_finite_temperature_offshell_threshold_crossing_1pi.py`; `docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_offshell_threshold_crossing_1pi.py`; `docs/core/test/test_topic13_uet_o2_finite_temperature_offshell_threshold_crossing_1pi.py`; `docs/core/artifacts/t13_uet_o2_finite_temperature_offshell_threshold_crossing_1pi_audit.json`; `docs/core/artifacts/uet_major_result_closure_register.json`; `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`.
EVIDENCE_HASHES: module `1b481136ba677b79d441f9ec253d1a4bb167c576463ee677f799d912ebfe549f`; audit script `0ebe3a880d6fe66759349233abb5dba21c1cfe0e63c240eee2df0b0ed8782123`; test `db17e230f12020634e107422705a1aab5844108c12204928f52db986f32d2c7a`; audit artifact `b0d449ecdc994e150d0157ba450515ea617d462a46b3a8d8f1607f60a2953920`; full gate `0df1a55ddcb131d328935c53c0aea2793dce28e07274cb1d6763d9c64002c5c0`; register `e4478953864f311d9eb0b8b4a06f6dccb2aba7b56186f2d2627c2bf2334e4983`; dependency gate `f73572847b21611be4c8dd658680f9e3f8960468285335d903c373732056f364`.
## All 2-to-2 Permutation Identity (2026-08-20, T13-123)
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_UET_O2_FINITE_T_ALL_22_PERMUTATION_IDENTITY_LANE`.
WHAT_IS_ACTUALLY_CLOSED: The three allowed equal-mass `2<->2` signed-cut patterns `++-`, `+-+`, and `-++` are now represented by explicit dummy-line relabeling maps to the reference kernel. Each map has unit Jacobian, the action-level single-cut weight remains `1/6`, and the aggregate graph weight is `3*(1/6)=1/2`. The matched response diagnostics are identical under the declared equal-mass relabeling.
WHAT_REMAINS_OPEN: Complete off-shell all-channel finite-temperature 1PI, unique physical renormalization, physical Kubo provenance, covariant entropy and heat-flux balance, dimensional `Phi` mapping, independent `alpha_Phi_K`, Ding `C_src`, EOS and constitutive transport, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Equal-mass `2<->2` permutation identity and action-level coverage only; `full_core_unlock=false`. No physical transport, SI, Core, Gravity, Galaxy, or external-validation dependency is unlocked.
STATUS: `PASS_ACTION_DERIVED_O2_FINITE_T_ALL_22_PERMUTATION_IDENTITY_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.
WHAT_CHANGED: Added an explicit all-three-permutation identity state, audit artifact, focused regression, full-gate projection, major-result register entry, and dependency projection. No new data, fit, holdout, clipping, padding, threshold change, or physical coefficient was introduced.
EQUATION_OR_MAPPING: `P+k_minus=k_plus,1+k_plus,2`; `k_ref=(k_plus,1,k_plus,2,k_minus)`; `|det J|=1`; `w_single=1/6`; `w_22=3*(1/6)=1/2`; `I_22^(++-)=I_22^(+-+)=I_22^(-++)` for equal masses and common temperature/couplings.
VERIFICATION: Three permutations and maps `(-++):(2,3,1)`, `(+-+):(1,3,2)`, `(++-):(1,2,3)`; response identity residual `0`; maximum PV inner residual `0.014920561773350124`; maximum PV outer residual `0.005424851497988344`; focused regression `3 passed`; audit zero failed checks; no Xie 2026 access.
CONTROLLING_BLOCKER: `complete_off_shell_all_channel_1pi_and_physical_renormalization_anchor_missing`; dimensional, source/calibration, EOS, transport, KMS, and entropy blockers remain independent.
NEXT_ACTION: Use the now-explicit three-permutation coverage as input to the complete off-shell all-channel 1PI construction and then test a physical renormalization anchor. Keep the response as action-derived natural-unit evidence only.
CLAIM_BOUNDARY: This closes the equal-mass `2<->2` permutation identity and action-level coverage lane only. It is not complete interacting 1PI closure, physical renormalization, a physical Kubo coefficient, an SI observable, an `alpha_Phi_K` calibration, a TTG prediction, external validation, or global UET closure.
DATA_ROLE: `ACTION_DERIVED_FINITE_T_ALL_22_PERMUTATION_IDENTITY_NO_HOLDOUT`.
EVIDENCE_PATHS: `docs/core/uet_o2_finite_temperature_all_22_permutation_identity.py`; `docs/scripts/audit/audit_topic13_uet_o2_finite_temperature_all_22_permutation_identity.py`; `docs/core/test/test_topic13_uet_o2_finite_temperature_all_22_permutation_identity.py`; `docs/core/artifacts/t13_uet_o2_finite_temperature_all_22_permutation_identity_audit.json`; `docs/core/artifacts/uet_major_result_closure_register.json`; `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`.
EVIDENCE_HASHES: module `4e4609b56b9fc230ff70cca5c87bf2ccc809ed09b4f14e8b7906551c7b10d250`; audit script `a3ab76cb78c6c1b12e6ddba533b9d66506b3e9d9d59a8cd6a17c4e7a756b9bb3`; test `495d4f3fbe938f48860023ea8bb9e9de3227d83e5f85bf86fb6d507cd727c1f6`; audit artifact `d8a70695cb21d4530dc1073bfcf5a1cf0bf2d80f9f075e225aeee5f50323f84c`; full gate `af09632cc717526649df82a6c4245f96a6d14c26cb0e02ccc3444104484109c1`; register `c52b1c556c04fc4a76e264e866aea379d3cf2747207b40e58aa5ba08246fa0c3`; dependency gate `6d465f940bbc3d6d0892d83a3b7b8222161434b3afce399f76eaf364dc5b9e51`.
## IAEA GR-280 Same-State Cp Availability Comparator (2026-08-20, T13-124)
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_IAEA_GR280_SAME_STATE_CP_COMPARATOR`; Full Topic 13 remains `PARTIAL` and `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: The official IAEA-THPH source is archived with locator and hash. Its GR-280 tables provide a same-temperature 300 C Cp row and a 300 C density row, so the availability sub-blocker for a same-state Cp source is now closed. The result is a comparison lane only.
WHAT_REMAINS_OPEN: Full-gate blockers remain `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`, `alpha_Phi_K_independent_calibration_missing`,
on_circular_uet_bridge_and_beta_derivation_missing`, `eos_transport_kms_entropy_completion_missing`, `dimensional_phi_to_thermal_observable_map_missing`, `physical_Kubo_coefficient_record_missing`, `same_grade_alpha_V_and_K_T_missing`, `material_regime_mapping_to_TTG_not_closed`, `density_uncertainty_not_source_locked`, and `c_v_source_uncertainty_not_closed`.
DEPENDENCY_UNLOCKED: Same-state Cp availability sub-blocker only; no Ding C_src, c_v uncertainty, alpha calibration, transport, Core, Gravity, Galaxy, or external-validation dependency is unlocked.
STATUS: `PASS_SCOPED_IAEA_GR280_SAME_STATE_CP_COMPARATOR`; full gate is `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; `claim_promotion=false`.
WHAT_CHANGED: Added the source package, raw PDF archive, audit, focused regression, full-gate projection, and major-result register/dependency projection. The gate now removes only `direct_volumetric_c_v_or_same_state_Cp_source_missing` when the same-state row check passes.
EQUATION_OR_MAPPING: `C_p^V = rho*C_p`; `u(C_p^V | rho fixed) = rho*u(C_p)`; `c_v^V = C_p^V - T*alpha_V^2*K_T`. The comparator is `C_p^V = 2386800 J m^-3 K^-1` with Cp-only uncertainty `209640.6 J m^-3 K^-1`; this is not a standard total uncertainty because density uncertainty is not reported.
VERIFICATION: Source audit passed with zero failed checks; raw SHA-256 is `bdb8454d8ebdadf83ecdb1794621180651bcf00108f1214f8f3a82193c05976b`; focused source/gate regression `10 passed`; full gate hash is `e64c34834dcb1ec36c9606b641601a8381430ae2ec02904986d6c25647be80e5`; Wave 1 integrity is `PASS_WITH_BLOCKED_LANES`; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: The source lane is now controlled by missing standard density uncertainty, c_v correction inputs, and the non-equivalence of GR-280 to Ding HOPG/TTG. Full Topic 13 remains controlled by the ten blockers above plus the independent dimensional and thermodynamic closure groups.
NEXT_ACTION: Acquire a source-grade density uncertainty or direct same-state volumetric c_v record, then match alpha_V and K_T to the same specimen/regime. Keep this comparator out of calibration and holdout paths while continuing the independent physical 1PI/renormalization wave.
CLAIM_BOUNDARY: This closes only a source-traceable same-state reactor-graphite Cp and density comparator lane. It is not c_v, Ding TTG C_src, an alpha_Phi_K calibration, physical SI transport, external validation, or Full Topic 13 closure.
DATA_ROLE: `EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_DING_TTG_GRADE`; no fit, target tuning, Landauer shortcut, or holdout access.
EVIDENCE_PATHS: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/iaea_gr280_same_state_cp_source_package.json`; `docs/core/artifacts/t13_iaea_gr280_same_state_cp_source_audit.json`; `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/iaea_thermophysical_properties_web.pdf`.
EVIDENCE_HASHES: package `d090b066a8d3e6ea405a553700a1c15b33b28d652636cf6aff1cc054e2ab9d73`; audit `c0091ce3d6624e5fd1b5e814f2bd3822459a5d84426cd861d31a9a0052710213`; full gate `e64c34834dcb1ec36c9606b641601a8381430ae2ec02904986d6c25647be80e5`; register `9b1c2e395af59976dd9f9c3e249fb85ee56fa9c6f81e9176eb0db586182b2217`; dependency `a8b1411c0a993a08a86d7c2fcd5a095f807fc15e76e9829a1fa1035bb8958e8a`.
## T13-125 Zenodo Hi-Trace high-temperature Cp comparator

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: A Zenodo-recorded Hi-Trace workbook is now source-locked with MD5/SHA-256, sheet/cell row identity, 27 populated Cp rows from three laboratories on same-block isotropic graphite, and explicit uncertainty handling: 16 rows with expanded uncertainty and 11 VINCA rows with uncertainty not reported.
WHAT_REMAINS_OPEN: `c_v`, source-grade density uncertainty, same-grade `alpha_V`/`K_T`, Ding/TTG material-regime mapping, Ding numeric `C_src`, dimensional `Phi` map, independent `alpha_Phi_K`, EOS/transport/KMS/entropy closure, and Full Topic 13 remain open.
DEPENDENCY_UNLOCKED: Comparator source lane only; `full_core_unlock=false`; no calibration, holdout, Core, Gravity, transport, Galaxy, or external-validation dependency is unlocked.
STATUS: `PASS_SCOPED_ZENODO_HITRACE_ISOTROPIC_GRAPHITE_CP_COMPARATOR`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL` with 10 controlling blockers.
WHAT_CHANGED: Added the raw XLSX archive, machine-readable source package, source audit, focused regression, full-gate projection, closure-register entry, and dependency projection. No synthetic replacement, fit, threshold change, Landauer inference, or Xie 2026 holdout access was used.
EQUATION_OR_MAPPING: `C_p(T)` is retained as mass-specific source data in `J kg^-1 K^-1`; `c_v^V = rho*(C_p - T*alpha_V^2*K_T)` is not evaluated because density, `alpha_V`, and `K_T` are not source-locked for this package.
VERIFICATION: Source audit passed with all checks true; raw MD5 `6b9e617fb0266da9a5724d04eccb18b8`, raw SHA-256 `c38e74d22c8b409b347b5d65384f0c172d4a43162ffffe7c2eba231f48d57020`; focused regression `10 passed`; major-result sync passed; downstream dependency audit remains blocked by the partial Topic 13 result.
CONTROLLING_BLOCKER: `c_v_source_uncertainty_not_closed`, `density_uncertainty_not_source_locked`, `same_grade_alpha_V_and_K_T_missing`, `material_regime_mapping_to_TTG_not_closed`, `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`, and `alpha_Phi_K_independent_calibration_missing` remain controlling.
NEXT_ACTION: Acquire direct volumetric `c_v` or a same-state source-grade density/`alpha_V`/`K_T` package for the relevant material regime, while continuing the independent Ding `C_src` and `alpha_Phi_K` routes without entering calibration or holdout paths.
CLAIM_BOUNDARY: This lane is a source-traceable high-temperature Cp comparator only. It is not `c_v`, not volumetric, not Ding/HOPG/TTG `C_src`, not an `alpha_Phi_K` calibration, not a temperature prediction, and not Full Topic 13 closure.
DATA_ROLE: `EXTERNAL_INPUT_STANDARD_COMPARATOR_NOT_DING_TTG_GRADE`; no calibration, training, or holdout role.
EVIDENCE_PATHS: `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/raw/zenodo_6091274_isotropic_graphite_specific_heat.xlsx`; `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/zenodo_hitrace_isotropic_graphite_cp_source_package.json`; `docs/scripts/audit/audit_topic13_zenodo_hitrace_isotropic_graphite_cp_source.py`; `docs/core/artifacts/t13_zenodo_hitrace_isotropic_graphite_cp_source_audit.json`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`; `docs/core/artifacts/uet_major_result_closure_register.json`; `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`.
EVIDENCE_HASHES: package `5d3cbbbf1eeab24c7f66f1cc01b16e80005aa80dfc9918edf62d82e6473dc8e3`; source audit `067238d11f9f426117cd29e757a8391f9089e97acfbeb0ab2b33c50d0eeb026a`; full gate `0b66d65364143b7f37fe1f58675b36da6ade7fd28e39caca09d6eeda2b8eeba0`; register `b04e38cc8b05b607314cc46f84d5a06473f04a30d5fc9e14d50de3486a9b2ced`; dependency `2e621c93e40aca38e3e4727a4f9cc7d5b570a1432120ee22aa84fcc4a46f1248`.

## Latest Hardening Lane: T13-126
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_ZENODO_HITRACE_IG210_ALPHA_L_COMPARATOR`.
WHAT_IS_ACTUALLY_CLOSED: Open Zenodo source package with 15 IG210 mean linear-expansion rows, row-level provenance, source replicate/model columns, and the paper-reported expanded uncertainty boundary.
WHAT_REMAINS_OPEN: `alpha_V` is conditional `3*alpha_l`; same-state `K_T`, density, `Cp/Cv`, Ding material mapping, Ding `C_src`, dimensional `Phi` anchor, and independent `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: IG210 alpha comparator lane only; `full_core_unlock=false`.
STATUS: Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; claim promotion remains false.
WHAT_CHANGED: Added source archive/package/audit/test and full-gate/register/dependency projections.
EQUATION_OR_MAPPING: `alpha_l[K^-1]=alpha_l[10^-6 K^-1]*10^-6`; `alpha_V=3*alpha_l` conditionally; `c_p^V-c_v^V=T*alpha_V^2*K_T` remains open.
VERIFICATION: Audit `17/17`; focused test `2 passed`; full gate and major-result sync passed; holdout access clean.
CONTROLLING_BLOCKER: Dimensional `Phi` energy anchor / independent `alpha_Phi_K`, Ding numeric `C_src`, and full EOS/transport/KMS/entropy remain the global controllers.
NEXT_ACTION: Continue source-grade paired thermodynamic inputs and the independent `Phi` anchor; do not use this comparator for fit or holdout tuning.
CLAIM_BOUNDARY: Comparator lane only, not Full Topic 13 closure.
## Latest Hardening Lane: T13-128
MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for `T13_FAROOQUI_IG210_THERMOPHYSICAL_SOURCE`.
WHAT_IS_ACTUALLY_CLOSED: Published NPL/Hi-Trace IG-210 Table 1 rows are source-locked for density, `C_p`, diffusivity, `alpha_l`, conductivity, and expanded uncertainty at `k=2`.
WHAT_REMAINS_OPEN: `K_T`, `C_v`, Ding material mapping, Ding `C_src`, dimensional `Phi`, and independent `alpha_Phi_K` remain open.
DEPENDENCY_UNLOCKED: IG-210 source comparator lane only; `full_core_unlock=false`.
STATUS: Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`; claim promotion remains false.
WHAT_CHANGED: Added the PDF archive, package, audit, focused test, full-gate projection, material-regime entry, and register/dependency projections.
EQUATION_OR_MAPPING: `c_v^V=rho*(C_p-T*alpha_V^2*K_T)` remains open; `alpha_V=3*alpha_l` is conditional.
VERIFICATION: Source audit `15/15`; focused regression `3 passed`; material audit comparator count `8`; full gate remains at 10 blockers; holdout access clean.
CONTROLLING_BLOCKER: Same-state `K_T` and independent dimensional `Phi` calibration, plus Ding `C_src` and full EOS/transport closure.
NEXT_ACTION: Search for same-state IG-210 `K_T`; keep `C_p` separate from `C_v` and continue independent `alpha_Phi_K` work.
CLAIM_BOUNDARY: Comparator lane only, not Full Topic 13 closure.

## Latest Hardening Lane: T13-129
MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for T13_GRAPHITE_ALPHA_V_K_T_MATCHED_SOURCE_BOUNDARY.
WHAT_IS_ACTUALLY_CLOSED: IG210 is now present in the matched-source inventory with three source-locked thermophysical rows and explicit absence of same-state K_T/C_v.
WHAT_REMAINS_OPEN: same_state_IG210_K_T_missing, Ding C_src/material mapping, dimensional Phi, independent alpha_Phi_K, and full EOS/transport/KMS/entropy remain open.
DEPENDENCY_UNLOCKED: IG210 source-boundary lane only; full_core_unlock=false.
STATUS: Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL; claim promotion remains false.
WHAT_CHANGED: Extended the matched-source audit and regression, then regenerated full-gate/register/dependency hashes.
EQUATION_OR_MAPPING: c_v^V=rho*(C_p-T*alpha_V^2*K_T) remains open; alpha_V=3*alpha_l remains conditional.
VERIFICATION: Boundary audit passed; focused regression 2 passed; full gate remains at 10 blockers; Xie 2026 not accessed.
CONTROLLING_BLOCKER: Same-state IG210 K_T and the independent Phi calibration route.
NEXT_ACTION: Search permitted same-state IG210 K_T, while continuing independent alpha_Phi_K and Ding C_src work without target/holdout fitting.
CLAIM_BOUNDARY: Source-boundary lane only, not C_v, not alpha_Phi_K, and not Full Topic 13 closure.
## T13-130 - Current major-result status
MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the symbolic covariant-action SI conversion contract; not CLOSED_FOR_CORE.
WHAT_IS_ACTUALLY_CLOSED: Natural-unit dimensional conversion formulas are available as a machine-readable, exact-constant-backed contract when E_ref and Phi_scale are declared.
WHAT_REMAINS_OPEN: Full Topic 13 still lacks physical E_ref provenance, covariant/base-Phi normalization, independent alpha_Phi_K, Ding C_src, non-circular bridge/beta, EOS, transport/Kubo, KMS, entropy, and heat-flux closure.
DEPENDENCY_UNLOCKED: Symbolic formula lane only; full_core_unlock=false.
STATUS: Full gate BLOCKED_OPEN_T13_FULL_BRIDGE; closure PARTIAL; 10 blockers remain.
WHAT_CHANGED: Registered and synchronized T13-130 module, audit, test, full gate, closure register, and dependency gate.
EQUATION_OR_MAPPING: u_SI=u_nat*E_ref^4/(hbar*c)^3; C_SI=C_nat*k_B*E_ref^3/(hbar*c)^3; Delta_Tq=(E_ref/k_B)*Delta_theta; alpha_Phi_K=(E_ref/k_B)*alpha_Phi_theta.
VERIFICATION: Symbolic audit passed; regression 4 passed; room integrity PASS_WITH_BLOCKED_LANES; Xie 2026 not consumed.
CONTROLLING_BLOCKER: energy_reference_and_base_Phi_normalization_provenance_missing.
NEXT_ACTION: Produce an independent, provenance-backed E_ref/Phi_scale record; only then attempt a numeric dimensional anchor.
CLAIM_BOUNDARY: This result is not a measured calibration, prediction, proof, external validation, or global UET closure.

## T13-133 - Current major-result status
MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the existing action-derived beta/no-go correspondence result; not CLOSED_FOR_CORE.
WHAT_IS_ACTUALLY_CLOSED: Reporting now records that the natural-unit beta derivation exists and that its conversion to normalized beta_T13 is non-identifiable without field, free-energy, and temperature scale inputs.
WHAT_REMAINS_OPEN: nnormalized_beta_and_SI_scale_correspondence_missing, independent alpha_Phi_K, accepted Ding C_src(T), the dimensional Phi map, physical Kubo provenance, and EOS/transport/KMS/entropy closure.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: Full gate BLOCKED_OPEN_T13_FULL_BRIDGE; closure PARTIAL; claim promotion false.
WHAT_CHANGED: The full-gate blocker projection was narrowed without changing the underlying equations or evidence class.
EQUATION_OR_MAPPING: beta_Phi^nat=T*partial_T a_Phi^nat; normalized beta_T13 requires an independent scale correspondence.
VERIFICATION: Full gate SHA-256 c4cb035a55ecd6d1dbbdf4f663a0f05b3d57cf71181f542bfb30590492852cbf; room integrity PASS_WITH_BLOCKED_LANES; focused regression 31 passed; holdout clean.
CONTROLLING_BLOCKER: nnormalized_beta_and_SI_scale_correspondence_missing.
NEXT_ACTION: Acquire an independent scale map or paired base-Phi/SI record; preserve the no-fit and locked-holdout policy.
CLAIM_BOUNDARY: This is blocker-classification closure only, not a physical beta value, SI calibration, prediction, or Full Topic 13 closure.

## Regularized Continuum Heat-Current Lane (T13-142)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`
WHAT_IS_ACTUALLY_CLOSED: A named normal-branch compactified radial heat-current scheme is closed for lane. It uses the existing action-derived normal dispersion and constant-amplitude collision width, projects charge/energy/three-momentum invariants, and passes the unchanged `1e-2` radial/angular/scale controller.
WHAT_REMAINS_OPEN: Loop-renormalized off-shell self-energy, physical Kubo provenance, condensed finite-temperature two-fluid completion, full SK/KMS matching, dimensional `Phi` to thermal observable mapping, independent `alpha_Phi_K`, and Ding `C_src` remain open.
DEPENDENCY_UNLOCKED: This unlocks only the named natural-unit normal-branch lane; it does not unlock physical transport, SI mapping, TTG, Core, Gravity, or Full Topic 13.
STATUS: `PASS_ACTION_DERIVED_REGULARIZED_CONTINUUM_HEAT_CURRENT_LANE`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_CHANGED: Added `docs/core/artifacts/t13_uet_o2_regularized_continuum_heat_current_audit.json` and synchronized the full gate and research-room reporting surfaces.
EQUATION_OR_MAPPING: `k=Lambda*u/(1-u)`; `b_q=(E-h*q)*(p_x/E)*sqrt(w)`; `L_reg=P*diag(Gamma_s(k))*P`; `kappa=Re[b_q^T(L_reg-i*omega*I)^(-1)b_q]`.
VERIFICATION: `kappa_natural=153.316802`; radial maximum change `1.04244e-06`, angular change `7.28033e-07`, scale change `1.10828e-08`; conservation residual `8.47823e-23`; source residual `1.92646e-18`; entropy `1.21146e-09`; KMS residual `1.72929e-16`. No fit, target, physical coefficient, numeric alpha, or Xie 2026 holdout was used.
CONTROLLING_BLOCKER: `loop_renormalized_off_shell_self_energy_missing` for this lane; full Topic 13 still retains the source, dimensional, alpha, EOS/transport/KMS/entropy, and material-regime blockers.
NEXT_ACTION: Keep this branch as scoped natural-unit evidence and close physical Kubo/source provenance and the remaining independent dimensional bridge before promotion.
CLAIM_BOUNDARY: `CLOSED_FOR_LANE` only. The branch does not replace the failed finite-cutoff baseline, prove a physical transport coefficient, or close Full Topic 13.

## Berut Figure 3 Local Archive (2026-08-20)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE

WHAT_IS_ACTUALLY_CLOSED: The official publisher Figure 3 route was
download-tested. Its remote binary identity is pinned by SHA-256, byte size,
OLE signature, retrieval date, and an explicit four-asset raster inventory.

WHAT_REMAINS_OPEN: No raster is accepted as a numeric row yet. Selected panel,
axis ticks and units, point or curve selection, digitization uncertainty,
preprocessing, and row identity remain open.

DEPENDENCY_UNLOCKED: Berut figure-acquisition route only. No numeric source,
alpha_Phi_K, Full Topic 13, Core, Gravity, or transport dependency is unlocked.

STATUS: PASS_REMOTE_FIGURE3_BINARY_IDENTITY

WHAT_CHANGED: docs/core/artifacts/t13_berut_figure3_remote_binary_identity.json records the official article/download locators,
binary hash e4bab6be849a093b7578bc52ce6df9be95dc25d83d51ecb718b4f798a37d50fa, size
479744 bytes, and embedded raster inventory.
The binary is archived locally at the hash-linked raw path; no raw measurement table is implied.

EQUATION_OR_MAPPING: Figure 3 is a source-surface asset for the Berut
heat-versus-erasure-duration observable; no numeric Delta_Tq or alpha_Phi_K
mapping is emitted.

VERIFICATION: Binary identity and asset inventory checks pass; accepted numeric
rows emitted: 0; no fit, target data, calibration, or Xie 2026 holdout was used.

CONTROLLING_BLOCKER: berut_selected_panel_and_axis_tick_mapping_missing

NEXT_ACTION: Select one quantitative panel, record axis ticks and units, map selected points or curve with declared digitization uncertainty, and archive row identity and preprocessing before source-normalized use.

CLAIM_BOUNDARY: Remote binary identity only. This is not a source-normalized
numeric row, uncertainty result, calibration, prediction, or external validation.

## Berut Source Package Availability Boundary (2026-08-20)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The Berut working copies in the current checkout are
classified as topic-derived summaries, not raw experimental rows. The captured
publisher surface is recorded as a Figure 3/PPT acquisition route, while the
absence of a local raw or separately exposed source-data package is explicit.

WHAT_REMAINS_OPEN: The official Figure 3 binary/hash, selected panel and axis
mapping, numeric transcription, row identity, preprocessing, and uncertainty
package remain open. No Berut numeric row is eligible for calibration.

DEPENDENCY_UNLOCKED: Berut source-acquisition decision only. No Full Topic 13,
Core, Gravity, or constitutive-transport dependency is unlocked.

STATUS: `PASS_SCOPED_BERUT_SOURCE_PACKAGE_BOUNDARY`

WHAT_CHANGED: `docs/core/artifacts/t13_berut_source_package_availability_boundary.json` records the source identity, publisher locator,
current local inventory, source-surface scope, and non-calibration policy.

EQUATION_OR_MAPPING: `E_min = k_B T ln(2)` remains an imported standard
constraint. No numeric `Delta_Tq = alpha_Phi_K * Delta_Phi` mapping is emitted.

VERIFICATION: All source identity, summary-role, no-raw-file, surface-scope,
holdout, no-fit, and no-calibration checks pass; accepted numeric rows emitted:
`0`.

CONTROLLING_BLOCKER: `berut_permissioned_raw_numeric_package_missing`

NEXT_ACTION: Obtain a permissioned raw numeric table or numeric measurement uncertainty for the Berut rows; keep the archived Figure 3c transcription as comparison-only and outside alpha calibration.

CLAIM_BOUNDARY: This is a provenance and acquisition boundary, not a closed
Berut numeric row, uncertainty result, `alpha_Phi_K`, UET bridge, or external
validation.

## T13-145 - Semantic alpha-calibration admission gate

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the calibration-admission contract; the numeric alpha_Phi_K result remains open.

WHAT_IS_ACTUALLY_CLOSED: Candidate eligibility is evaluated from substantive values within one paired record rather than from field-name presence across an arbitrary JSON tree. The gate requires source identity and locator, matched material/state/geometry, finite base-Phi and SI response amplitudes, units, numeric uncertainty, preprocessing, row identity, a valid source hash, and an independence statement.

WHAT_REMAINS_OPEN: All 11 current candidate packages remain ineligible. No independent paired base-Phi/SI record, numeric alpha_Phi_K, or base-Phi to Phi_E scale was produced.

DEPENDENCY_UNLOCKED: Calibration-admission contract only; no alpha, dimensional map, Full Topic 13, Core, Gravity, or transport dependency is unlocked.

STATUS: PASS_SCOPED_NO_ELIGIBLE_PAIRED_ALPHA_RECORD; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL.

WHAT_CHANGED: The candidate audit now validates semantic paired records and keeps key-presence diagnostics separate. The full gate, closure register, and dependency projection consume the regenerated candidate artifact.

EQUATION_OR_MAPPING: y_TTG^UET = Delta_Phi(t) / Delta_Phi(0); Delta_Tq = alpha_Phi_K * Delta_Phi; no coefficient is emitted from normalized data, Landauer, or a comparator package.

VERIFICATION: Candidate count is 11 and eligible count is 0; numeric_alpha_Phi_K_emitted=false, holdout_accessed=false, and target_fit_performed=false. The focused regression passed with 10 tests.

CONTROLLING_BLOCKER: independent_paired_base_Phi_amplitude_and_SI_observable_record_missing.

NEXT_ACTION: Obtain a permitted paired base-Phi/SI record or derive a coefficient-provenance-backed dimensional map without reading Xie 2026, then rerun the semantic admission gate before any calibration or prediction.

CLAIM_BOUNDARY: This closes the admission and provenance boundary only. It is not a numeric calibration, temperature prediction, external validation, or Full Topic 13 closure.
## T13-147 - Joint thermal-bridge scale-dependency no-go

MAJOR_RESULT_CLOSURE: `CLOSED_AS_NO_GO` for the current normalized/action scale question; Full Topic 13 remains `PARTIAL` / `BLOCKED`.

WHAT_IS_ACTUALLY_CLOSED: The declared scalar action and normalized TTG lane admit an explicit continuous field-rescaling family. A field-only alpha compensation preserves the dimensional response form while changing the unanchored Phi amplitude, and a joint field/energy-density rescaling changes the absolute Kelvin response and normalized beta correspondence.

WHAT_REMAINS_OPEN: An independent field-energy-temperature scale map, an independent paired base-Phi/SI observable record, physical beta provenance, and the base-Phi-to-Delta_u_ph map remain open. No numeric alpha_Phi_K or e0 was emitted.

DEPENDENCY_UNLOCKED: None. This closes a structural no-go lane only; it does not unlock Full Topic 13, Core, Gravity, constitutive transport, or Galaxy.

STATUS: `PASS_SCOPED_THERMAL_BRIDGE_SCALE_DEPENDENCY_NO_GO`; canonical full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL` with 10 blockers.

WHAT_CHANGED: Added `docs/core/t13_thermal_bridge_scale_dependency.py` and its verifier/artifact. The full gate now registers `T13_THERMAL_BRIDGE_SCALE_DEPENDENCY_NO_GO` under the dimensional observable map and records the no-go in lane closures.

EQUATION_OR_MAPPING: `y_TTG = Delta_Tq(t) / Delta_Tq(0)`; `y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)`; `Delta_Tq = alpha_Phi_K * Delta_Phi`; `delta_phi_prime = s_phi delta_phi`; `beta_T13 = (Phi_scale^2 / e0_scale) beta_Phi^nat`.

VERIFICATION: The structural witness passed action-term, normalized-response, field-compensation, absolute-scale, beta-scale, ontology, no-fit, no-Landauer, no-target, and no-holdout checks. Full closure summary is `closed_lane_count=170`, `closed_as_no_go_count=15`, `open_blocker_count=10`, `downstream_dependency_unlocked=false`. Xie 2026 remained unconsumed.

CONTROLLING_BLOCKER: `independent_field_energy_and_temperature_scale_map_missing`, together with the existing independent alpha, Ding C_src, physical Kubo, EOS/transport/KMS/entropy, material-regime, and uncertainty blockers.

NEXT_ACTION: Obtain a permitted source-locked field residue or paired base-Phi/SI observable anchor, or derive the map from a declared dimensionful action/free-energy origin. Do not infer it from normalized TTG, Landauer, or Xie 2026.

CLAIM_BOUNDARY: Scoped structural no-go only. It is not numeric calibration, Kelvin prediction, external validation, `CLOSED_FOR_CORE`, or global UET closure.

## T13-148 - AIST graphite source-route public-reproducibility boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for the screened AIST public source route; Full Topic 13 remains `PARTIAL` / `BLOCKED`.
WHAT_IS_ACTUALLY_CLOSED: The public AIST TPDS graphite search surface was source-located. It exposes graphite material names and property categories relevant to density, c_v, volumetric heat capacity, and volumetric thermal expansion, but the displayed terms restrict publishing or providing the contents to third parties. The audit therefore closes this route as a public-reproducibility boundary without opening a material detail record or consuming numeric rows.
WHAT_REMAINS_OPEN: A permitted redistributable numeric c_v or volumetric-heat-capacity row with material identity, units, preprocessing, row-level uncertainty, and hash remains open. Ding-compatible C_src, material-regime mapping, density uncertainty, and independent alpha_Phi_K remain open.
DEPENDENCY_UNLOCKED: AIST route boundary only. No c_v source closure, Ding C_src, alpha_Phi_K, Full Topic 13, Core, Gravity, constitutive transport, or Galaxy dependency is unlocked.
STATUS: `PASS_SCOPED_AIST_GRAPHITE_SOURCE_ROUTE_BOUNDARY`; canonical full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL` with 10 blockers.
WHAT_CHANGED: Added the machine-readable AIST route-boundary artifact and verifier, recorded source metadata and terms without numeric payload, integrated the lane into the full-gate source-package section, and added focused regression coverage.
EQUATION_OR_MAPPING: Candidate source quantity `c_v(T, material)` has units `J kg^-1 K^-1`; candidate volumetric map `c_v^V = rho c_v` has units `J m^-3 K^-1`. `numeric_mapping_emitted=false`; no `Delta_Tq = alpha_Phi_K * Delta_Phi` coefficient is emitted.
VERIFICATION: Artifact records `numeric_payload_accessed=false`, `numeric_payload_stored=false`, `material_state_verified=false`, `accepted_for_full_topic13=false`, and `holdout_accessed=false`. Focused regression passed (`6 passed`). Full gate remains blocked; downstream dependency audit remains blocked; Xie 2026 was not accessed.
CONTROLLING_BLOCKER: `aist_numeric_payload_not_publicly_redistributable` for this route; globally the Ding-compatible `C_src`, independent alpha/dimensional map, physical Kubo, EOS/transport/KMS/entropy, material-regime, and uncertainty blockers remain controlling.
NEXT_ACTION: Acquire a permitted redistributable numeric graphite c_v or volumetric-heat-capacity source with provenance and uncertainty, or obtain a permissioned private source package without treating it as publicly reproducible. Do not substitute AIST metadata for Ding or calibration.
CLAIM_BOUNDARY: This closes only a source-route boundary. It is not numeric c_v or C_src evidence, independent alpha_Phi_K calibration, TTG prediction, external validation, `CLOSED_FOR_CORE`, or global UET closure.
EVIDENCE_PATHS: `docs/scripts/audit/audit_topic13_aist_graphite_source_route_boundary.py`; `docs/core/test/test_topic13_aist_graphite_source_route_boundary.py`; `docs/core/artifacts/t13_aist_graphite_source_route_boundary_audit.json`; `docs/scripts/audit/audit_topic13_full_bridge_gate.py`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`; `docs/core/artifacts/uet_major_result_closure_register.json`; `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`.
EVIDENCE_HASHES: verifier `96024a0bbabb09218681870804109eff417dfe0597a873c5a898cacefd5669ac`; regression `feaa4ef9b94d3dd32bf1b87a9c5da9f2781fa543e0b6403b6fcd4982e962e261`; AIST artifact `3a37c2cd5a37dccaa7f0a5aa7f4704c54ed73a11e04d5e7168d00682de2ff3de`; full-gate builder `7b87f0476f4d49f37993cc405e2c14b13ecfdc8044daaf2279a1729a030a3857`; full gate `7b156617b44d30367464e0d69ff5e13f82509d848c4c5bf320acfd43749ed663`; register `11f33ef3d80d5fe222b0b60d96b65c7bfb1b6d87c38f6218bca55f42680eaf0a`; dependency `6078156e584cd84b7ab75cf1598f1ca90c9cea2098e5c02d6046d9f514f94d78`.
## T13-149 - NIST SRM 3600 heat-capacity comparator boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for the NIST SRM 3600 heat-capacity comparator boundary; Full Topic 13 remains `PARTIAL` / `BLOCKED`.
WHAT_IS_ACTUALLY_CLOSED: The official NIST SRM 3600 paper is archived locally with a source hash and page locators. Its 20-295 K heat-capacity range, approximately +/-2 percent uncertainty boundary at 90 percent confidence, and separate systematic-discrepancy warning are recorded without relabeling them as row-level standard uncertainty. The material boundary between low-hydrogen glassy carbon/graphite powder and Ding's HOPG PBTE state is explicit.
WHAT_REMAINS_OPEN: No machine-readable numeric rows were emitted from Figure 3; this is not Ding `C_src`, not a same-state HOPG source, and it does not close `c_v` uncertainty, material-regime mapping, `alpha_Phi_K`, dimensional mapping, physical Kubo, EOS/transport/KMS/entropy, or Full Topic 13.
DEPENDENCY_UNLOCKED: NIST SRM 3600 comparator boundary only. No Core, Gravity, constitutive transport, Galaxy, calibration, or external-validation dependency is unlocked.
STATUS: `PASS_SCOPED_NIST_SRM_3600_HEAT_CAPACITY_COMPARATOR_BOUNDARY`; canonical full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL` with 10 blockers.
WHAT_CHANGED: Added the hash-locked source-boundary verifier and artifact, integrated the lane under the full-gate source-package section, synchronized the major-result register/dependency gate, and added focused regression coverage. The raw PDF remains ignored and local-only under the repository raw-source policy.
EQUATION_OR_MAPPING: Candidate `c_v^V(T, material) = rho(T, material) * c_v^m(T, material)` is recorded as a mapping contract only; `numeric_rows_emitted=false`, no `C_src`, `alpha_Phi_K`, or TTG temperature mapping is emitted.
VERIFICATION: SRM 3600 boundary verifier passed; focused Topic 13/register/dependency regressions passed (`10 passed` after synchronization). Raw PDF SHA-256 is `5bbbd0e3949a1e38cbb7ec00bbfc1a75a9d4708f6a0656e5e49c8d44d32ba5da`; source artifact records zero numeric rows, no fit, no calibration, and no holdout access. Full closure summary is `closed_lane_count=172`, `closed_as_no_go_count=15`, `open_blocker_count=10`, `downstream_dependency_unlocked=false`.
CONTROLLING_BLOCKER: `figure_only_numeric_payload_and_Ding_material_mapping_missing` for this comparator; globally `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing` remains primary, with Ding `C_src` and physical thermodynamic/transport evidence also open.
NEXT_ACTION: Obtain a permitted same-state machine-readable heat-capacity/PBTE source with row locators, units, uncertainty, preprocessing, convergence, material identity, and hash, or obtain a permissioned Ding-compatible `C_src` package. Do not digitize Figure 3 into calibration without a declared digitization uncertainty contract.
CLAIM_BOUNDARY: Comparator source boundary only; not numeric `C_src`, not independent `alpha_Phi_K`, not a Kelvin prediction, not external validation, not `CLOSED_FOR_CORE`, and not global UET closure.
EVIDENCE_PATHS: `docs/core/artifacts/t13_nist_srm_3600_heat_capacity_boundary_audit.json`; `docs/scripts/audit/audit_topic13_nist_srm_3600_heat_capacity_boundary.py`; `docs/core/test/test_topic13_nist_srm_3600_heat_capacity_boundary.py`; `docs/scripts/audit/audit_topic13_full_bridge_gate.py`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`; `docs/core/artifacts/uet_major_result_closure_register.json`; `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`.
EVIDENCE_HASHES: source `5bbbd0e3949a1e38cbb7ec00bbfc1a75a9d4708f6a0656e5e49c8d44d32ba5da`; source artifact `7317cadd672abd7eaacdda3eb5b4e5fdfc6bbe9fe6085a916ab93418ce6678b3`; full gate `17f9a8f09f17dacaaea987a086b1ad905bb206cc16dd8c6949538ff5167fe55c`; register `8037569bca69757892be6c7b216218fc7c437ad0413a1877dcdf723f75a40253`; dependency `3fcfbdbe603db366b0dc848df5da7602ac1ce649d07d86379e5fc3bf346b6016`.
## T13-150 - Perez-Castaneda HOPG specific-heat source boundary

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for a source-traceable HOPG specific-heat comparator boundary; not CLOSED_FOR_CORE.

WHAT_IS_ACTUALLY_CLOSED: The author-posted paper is archived with a reproducible PDF hash, DOI/arXiv locators, specimen details, and page-level source locators. Its below-3-percent method-comparison statement is preserved as a method/error boundary, not row-level standard uncertainty. The figure-only route is explicitly rejected for silent C_src or alpha promotion.

WHAT_REMAINS_OPEN: Numeric rows, source-grade c_v uncertainty, Ding natural-graphite TTG/PBTE material and response mapping, Ding C_src, independent alpha_Phi_K, dimensional Phi map, physical Kubo coefficient, and EOS/transport/KMS/entropy closure remain open.

DEPENDENCY_UNLOCKED: HOPG comparator/source-boundary lane only; no downstream dependency is unlocked.

STATUS: PASS_SCOPED_HOPG_SPECIFIC_HEAT_SOURCE_BOUNDARY; Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL with 10 blockers.

WHAT_CHANGED: Added the HOPG source-boundary verifier, artifact, focused test, full-gate projection, closure-register/dependency sync, manifest, formula-audit entry, and update-log entry. The local raw PDF remains ignored and is not included in the public commit.

EQUATION_OR_MAPPING: Candidate c_p^m(T, material) and c_v^V(T, material) = rho(T, material) * c_p^m(T, material) - Cp-to-Cv correction are recorded as standard-physics mapping contracts only. No numeric mapping is evaluated. The UET measurement equations remain y_TTG = Delta_Tq(t) / Delta_Tq(0), y_TTG^UET = Delta_Phi(t) / Delta_Phi(0), and Delta_Tq = alpha_Phi_K * Delta_Phi.

VERIFICATION: Source hash f5056e3804275336deca634da84a47fec1e91876ff65ab62a84596a5ad3ebd4a; 1141942 bytes; 21 pages; zero numeric rows; figure-only payload; 3 percent method-comparison boundary; no Ding match; focused regression 13 passed; full gate remains blocked; claim promotion=false; Xie 2026 remains untouched.

CONTROLLING_BLOCKER: figure_only_numeric_payload_and_Ding_PBTE_response_mapping_missing for this source route; globally the missing independent Phi/SI dimensional anchor and alpha_Phi_K remain controlling.

NEXT_ACTION: Acquire a permitted machine-readable same-state heat-capacity or Ding PBTE C_src package with provenance, row uncertainty, convergence, material identity, and hash; keep this HOPG route outside calibration and holdout paths.

CLAIM_BOUNDARY: Source comparator boundary only; not numeric C_src, not alpha calibration, not prediction, not external validation, and not Full Topic 13 closure.

EVIDENCE_PATHS: docs/core/artifacts/t13_perez_castaneda_hopg_source_boundary_audit.json; docs/scripts/audit/audit_topic13_perez_castaneda_hopg_boundary.py; docs/core/test/test_topic13_perez_castaneda_hopg_boundary.py; docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json; docs/core/artifacts/uet_major_result_closure_register.json; docs/core/artifacts/uet_major_result_dependency_unlock_gate.json.
## T13-151 - Calorine full-LBTE numerical stability boundary

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for the source-locked full-LBTE numerical-stability boundary; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL`.
WHAT_IS_ACTUALLY_CLOSED: A fixed Calorine 4x4x2 force-constant state was rerun with explicit natural-isotope control. The archived `pinv_method=0` and `pinv_method=1` outputs show that the high-mesh collision spectrum is sign-indefinite; the positive method-1 response is therefore recorded as a numerical boundary, not physical transport closure.
WHAT_REMAINS_OPEN: Collision-spectrum positivity, full-LBTE mesh convergence, source-grade uncertainty, Calorine-to-Ding material/state mapping, independent `alpha_Phi_K`, dimensional `Phi` mapping, physical Kubo provenance, and EOS/transport/KMS/entropy closure remain open.
DEPENDENCY_UNLOCKED: Full-LBTE numerical-boundary evidence lane only. No physical transport, dimensional calibration, Full Topic 13, Core, Gravity, constitutive transport, or Galaxy dependency is unlocked.
STATUS: `WARN_FULL_LBTE_NUMERICAL_STABILITY_OPEN`; canonical full gate remains `BLOCKED_OPEN_T13_FULL_BRIDGE` with 10 blockers.
WHAT_CHANGED: Added the archived full-LBTE stability audit, method-sensitivity control, collision-eigenvalue diagnostics, focused regression, full-gate source-package projection, and major-result register/dependency synchronization. No source, ontology, thermal leakage threshold, fit, calibration, or holdout policy changed.
EQUATION_OR_MAPPING: `C_src(T) = [sum_q w_q sum_mu c_qmu(T)] / [sum_q w_q V_primitive]`; candidate `Delta_Tq = Delta_u_ph / C_src(T)`; full-LBTE observable `kappa` is in `W m^-1 K^-1`. `pinv_method=1` treats eigenvalue `< 1e-8` as zero and ignores negative eigenvalues; it is not a proof of positive entropy/transport response.
VERIFICATION: Latest method-1 mesh pair `0.129379135193` relative change (8x8x4 to 10x10x5), method-0 in-plane `kappa` at 300 K is negative (`True`), and the high-mesh method-1 collision spectrum has negative-mode counts `[280, 296, 285]`. Fit, target-curve use, `alpha_Phi_K` fit, and holdout access are false.
CONTROLLING_BLOCKER: `full_lbte_numerical_well_posedness_not_closed`, alongside the existing independent dimensional/`alpha_Phi_K`, Ding `C_src`, material, uncertainty, and thermodynamic-transport blockers.
NEXT_ACTION: Resolve the sign-indefinite collision spectrum and obtain a declared source-supported convergence/uncertainty contract before treating full-LBTE output as a physical comparator; do not use it for `alpha_Phi_K` or holdout prediction.
CLAIM_BOUNDARY: This is a numerical-stability boundary for one external candidate route, not a physical UET transport coefficient, Ding TTG validation, `Phi`-to-temperature prediction, Core closure, or global UET closure.
EVIDENCE_PATHS: `docs/core/artifacts/t13_calorine_full_lbte_stability_boundary_audit.json`; `docs/scripts/audit/audit_topic13_calorine_full_lbte_stability.py`; `docs/core/test/test_topic13_calorine_full_lbte_stability.py`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`; `docs/core/artifacts/uet_major_result_closure_register.json`; `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`.
EVIDENCE_HASHES: artifact `8b5de32a8c33b0a646c8e26faf263585d98bcb939df8adb78b1b16f9d832859d`; full gate `6505ad8b6b1aac6da67d8ba7a3c10ae77f2c6047def0502a47377f44bdd8f14a`; register `a0207ee94c1cdc4e5d5a86f33763a7bbe3267716d3ce5bd7290a7f806b424344`; dependency `62195d85fbf71e31b98448215aa25e991a55b01f6d6dbca80b93cac1f561b91d`.

### 2026-08-22 - Ding publisher provenance locator wave (T13-151)

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE
WHAT_IS_ACTUALLY_CLOSED: The Ding 2022 source package records the primary Nature Communications locator and publisher-level data-availability statement; the captured official PMC OA inventory remains a verified no-go for machine-readable PBTE reproduction inputs.
WHAT_REMAINS_OPEN: Numeric Ding C_src(T), uncertainty/convergence, accepted same-regime independent reproduction, independent alpha_Phi_K calibration, dimensional Phi anchor, and full beta/EOS/transport/KMS/entropy closure.
DEPENDENCY_UNLOCKED: Source-provenance lane only; no Full Topic 13, Core, Gravity, constitutive-transport, or Galaxy dependency is unlocked.
STATUS: PASS_SCOPED_OA_NUMERIC_INPUT_AVAILABILITY_NO_GO
WHAT_CHANGED: Added publisher locator fields and verifier checks distinguishing the publisher route from the archived PMC OA inventory.
EQUATION_OR_MAPPING: C_src(T) = sum_mu c_mu(T); no numeric c_mu or C_src value was emitted.
VERIFICATION: Source audit passed; archived records and supplementary hashes match; no reproduction payload candidate was found; focused regressions passed 8 tests; Xie 2026 remained unread and unconsumed.
CONTROLLING_BLOCKER: ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing and independent_alpha_Phi_K_calibration_missing.
NEXT_ACTION: Execute an authorized corresponding-author request or build an accepted same-regime PBTE reproduction with units, uncertainty, convergence, material/state mapping, and hash; keep calibration independent and do not read the locked holdout.
CLAIM_BOUNDARY: Source-provenance/availability classification only; not numeric C_src, alpha_Phi_K calibration, temperature prediction, external validation, CLOSED_FOR_CORE, or global UET closure.
EVIDENCE_HASHES: package b87680866ebed7ca25f27008f01e37dd47f0e6da54c3c1e27eb404e20fe600ad; source audit 1828db74760ac53c73345d0e4a8adc8fc00fc16bb25e84809a73aaa3cd9b3d9a; full gate fcd703b29b69e2e32ebc9d9572eca5fc33ffc9a9ad2893336c3f5ca81644c231.

## T13-155 - Ding C_src fixed-volume thermodynamic identity

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`; Full Topic 13 remains `PARTIAL` / `BLOCKED_OPEN_T13_FULL_BRIDGE`.
WHAT_IS_ACTUALLY_CLOSED: A conditional fixed-volume standard-phonon identity now connects the Ding denominator to `C_src(T,V)=(partial u_ph/partial T)_V=(1/V) sum_mu c_mu(T,V)`. The source formula, unit contract, Bose kernel, and UET ontology separation are audited without a numeric source row.
WHAT_REMAINS_OPEN: Numeric Ding `C_src(T)`, accepted PBTE reproduction, material/state/volume match, source-grade uncertainty/convergence, base-Phi-to-energy map, independent `alpha_Phi_K`, and full EOS/transport/KMS/entropy closure.
DEPENDENCY_UNLOCKED: Conditional identity lane only; no downstream dependency is unlocked.
STATUS: `PASS_SCOPED_C_SRC_FIXED_VOLUME_IDENTITY`.
WHAT_CHANGED: Added the verifier, artifact, focused regression, and machine-readable gate/register/dependency projections. Existing comparator lanes remain comparison-only.
EQUATION_OR_MAPPING: `C_src(T,V)=(partial u_ph/partial T)_V`; `Delta_Tq=Delta_u_ph/C_src`; `C_p^vol-C_v^vol=T*alpha_V^2*K_T` remains separate and is not used to create Ding `C_src`.
VERIFICATION: Analytic/finite-difference identity relative error `7.995153125698355e-11`; focused regression `19 passed`; full gate remains at `10` blockers; `claim_promotion=false`; Xie 2026 remains unconsumed.
CONTROLLING_BLOCKER: `ding_pbte_numeric_C_src_or_accepted_independent_reproduction_missing` plus the independent dimensional/alpha and thermodynamic-transport blockers.
NEXT_ACTION: Acquire the permitted Ding-compatible numeric mode/C_src or fixed-volume c_v source package with material/state, volume, uncertainty, convergence, and hash.
CLAIM_BOUNDARY: Conditional identity only; no numeric C_src, alpha, temperature prediction, external validation, or Full Topic 13 closure.
EVIDENCE: `docs/core/artifacts/t13_csrc_fixed_volume_identity_audit.json` (SHA-256 `155b15ac1184f0309e10db8466925d6ad6483d4321a7703d82ecfb09a086cdd5`); full gate `f0cddb266247c0454ed2f89775a7eefc033d3ce1ef8d84cde574a9e4bfc8df50`; closure register `eb044c3083382b61855baa8ee26ea847a85005c148f5e0b85612a74bfb7b3c0b`; dependency gate `985a9727e59db875b6446096942b07b70375da9ba59cb06cc456e9cd25ef93e2`.
## 2026-08-22 - IG-210 density-uncertainty blocker closure (T13-157)

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE` for the resolved blocker projection `density_uncertainty_not_source_locked`; Full Topic 13 remains `PARTIAL` / `BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_IS_ACTUALLY_CLOSED: The source-locked IG-210 thermophysical audit exposes three density rows at 500/700/1000 C with source-expanded relative density bounds of 0.003 at coverage factor k=2. The full gate now consumes that field and removes only the density-uncertainty blocker.

WHAT_REMAINS_OPEN: Same-state IG-210 `K_T`, the `C_p`-to-`C_v` correction, Ding material/response mapping, Ding-compatible `C_src`, independent `alpha_Phi_K`, dimensional `Phi` mapping, physical Kubo evidence, and EOS/transport/KMS/entropy closure remain open.

DEPENDENCY_UNLOCKED: Density uncertainty projection and IG-210 volumetric `C_p` comparator only. No `C_v`, Ding `C_src`, alpha calibration, Core, Gravity, constitutive transport, Galaxy, or external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_SOURCE_LOCKED_DENSITY_UNCERTAINTY`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE` / `PARTIAL` with 9 open blockers.

WHAT_CHANGED: Added the machine-readable `major_result.resolved_blockers` record, propagated it into the major-result register, updated the full-gate regression, and synchronized the current report, update log, and data manifest. No source rows were invented; no fit, threshold change, calibration, or holdout access occurred.

EQUATION_OR_MAPPING: `C_p^V = rho*C_p` with conservative source-expanded interval propagation; `C_v^V = C_p^V - T*alpha_V^2*K_T` remains uninstantiated for IG-210.

VERIFICATION: IG-210 volumetric audit passed 14/14; focused Topic 13/closure regressions passed 11 tests; full gate reports 180 closed lanes, 16 scoped no-go lanes, 9 open blockers, `holdout_consumed=false`, and `claim_promotion=false`.

CONTROLLING_BLOCKER: `same_state_IG210_isothermal_K_T_missing` controls this source route; globally Ding-compatible `C_src`, independent alpha/dimensional mapping, and EOS/transport/KMS/entropy remain controlling.

NEXT_ACTION: Source-lock a permitted same-state IG-210 `K_T` only if it carries material/state, units, uncertainty, locator, and hash; otherwise retain this correction boundary and prioritize Ding-compatible `C_src` plus an independent paired base-`Phi`/SI record.

CLAIM_BOUNDARY: This closes only the density-uncertainty gate projection and the source-traceable IG-210 volumetric `C_p` comparator. It is not `C_v`, Ding `C_src`, numeric `alpha_Phi_K`, a temperature prediction, physical transport, external validation, Full Topic 13 closure, or global UET closure.

EVIDENCE_PATHS: `docs/core/artifacts/t13_farooqui_ig210_thermophysical_source_audit.json`; `docs/core/artifacts/t13_farooqui_ig210_volumetric_cp_uncertainty_audit.json`; `docs/scripts/audit/audit_topic13_full_bridge_gate.py`; `docs/scripts/audit/audit_major_result_closure.py`; `docs/core/test/test_topic13_gatech_volumetric_cp_independence.py`; `docs/core/test/test_major_result_closure.py`; `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`; `docs/core/artifacts/uet_major_result_closure_register.json`; `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`.

EVIDENCE_HASHES: source audit `1bf871b436166ba44243d6600fdfc06e9bbbf65a8fc23e2f99a728ff6402fb7e`; volumetric audit `8714a13530c99cba457b86d529928747f26b8536befe782843387f3f2a362add`; full gate `f2f67384475fc8680476dee1b893dc1b32c9a90d8a1e348580789426536899d4`; register `7093fccfbb6e027df11429e51515dc3ddbabde3ecd27cbdce70a51fddf76bd69`; dependency `41303c1d38bc86c8c1f5008aafb515e05990f32acd74af1605ed371616f1ccd1`.