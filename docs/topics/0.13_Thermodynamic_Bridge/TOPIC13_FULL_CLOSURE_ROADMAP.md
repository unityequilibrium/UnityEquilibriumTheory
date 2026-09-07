# Topic 13 Full Closure Roadmap

## MAJOR_RESULT_CLOSURE

The current Topic 13 state is `PARTIAL`. The canonical gate remains
`BLOCKED_OPEN_T13_FULL_BRIDGE`.

The target is:

```text
T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY
```

This target means that the thermal bridge is integrated and ready for Core
handoff. It does not mean that global UET, external validation, or all
downstream topics are closed.

## WHAT_IS_ACTUALLY_CLOSED

The closure matrix contains 10 major result areas and 36 evidence-producing
subresults.

| Current level | Count | Meaning |
| --- | ---: | --- |
| `CLOSED_FOR_LANE` | 21 | Formal, comparator, or named internal lane is bounded and verified |
| `CLOSED_AS_NO_GO` | 5 | A scoped impossibility or source-route boundary is recorded |
| `OPEN` | 10 | Core-level evidence is still missing |

The causal structural question is already a scoped no-go for the declared
conserved-C local-gradient class. The named coupled flux-Phi branch has a
separate bounded Core handoff record,
`T13_CAUSAL_FLUX_PHI_COUPLED_CORE_COMPATIBILITY`, at `CLOSED_FOR_CORE`.
That is a causal exception only: it does not convert any of the 36 Full Topic
13 subresults to `CLOSED_FOR_CORE`, replace the original blocked baseline, or
unlock SI thermal mapping, physical transport, curved 3+1, or Gravity.

The latest Lowitzer source wave also closed the same-study, same-sample
`alpha_V`/`K_T` pair as a source-locked lane. This reduced the canonical full
gate from eight to seven blocker groups. It does not establish Ding TTG
material equivalence and it does not provide `alpha_Phi_K`.

## WHAT_REMAINS_OPEN

Every item below must reach `CLOSED_FOR_CORE`.

| Major result | Open subresult | Required evidence |
| --- | --- | --- |
| Dimensional Phi-to-thermal map | `base_phi_si_anchor` | A dimensionful action/free-energy origin or an independent paired base-Phi/SI response record |
| Independent alpha | `independent_alpha_record` | One eligible non-holdout paired record, or a derivation with an independently fixed SI scale, including uncertainty |
| Beta/SI correspondence | `normalized_beta_si_map` | Independently fixed Phi normalization and dimensionful free-energy scale propagated into beta; Landauer is not the derivation |
| Charge-density EOS | `physical_source_backed_eos` | Finite-temperature coefficients, declared material regime, source-grade `c_v` uncertainty, and SI Phi normalization |
| Covariant thermal transport | `physical_uet_kubo_record` | One source-backed or microscopic state-matched physical coefficient with units, frame, state, correlator provenance, and uncertainty |
| SK/KMS matching | `physical_sk_transport_match` | Microscopic response linked to the physical coefficient and uncertainty; no synthetic substitute |
| Entropy/dissipative balance | `physical_entropy_production_mapping` | Physical coefficient, SI heat flux, source uncertainty, entropy-production uncertainty, and same-state balance |
| TTG source/uncertainty | `accepted_numeric_csrc` | Authorized Ding package or accepted same-regime reproduction with mode-resolved `C_src(T)` and source-grade uncertainty |
| Material/uncertainty closure | `material_and_uncertainty_closure` | Material, morphology, isotope/defect state, TTG/PBTE response contract, same-state thermodynamic correction, and uncertainty |
| Heat-flux/entropy map | `physical_heat_flux_entropy_map` | SI Phi anchor, physical coefficient, accepted `C_src`, and one propagated uncertainty chain on the same state |

The canonical gate currently reports these seven blocker groups:

1. `ding_pbte_C_src_numeric_or_accepted_independent_reproduction_missing`
2. `alpha_Phi_K_independent_calibration_missing`
3. `normalized_beta_and_SI_scale_correspondence_missing`
4. `physical_Kubo_coefficient_record_missing`
5. `dimensional_phi_to_thermal_observable_map_missing`
6. `material_regime_mapping_to_TTG_not_closed`
7. `c_v_source_uncertainty_not_closed`

## DEPENDENCY_UNLOCKED

No downstream dependency is currently unlocked. The three grouped input
packages are acquisition and derivation gates, not readiness promotions.

### Ding TTG source package

Required minimum records:

- Mode-resolved `C_src(T)` rows in `J m^-3 K^-1` with temperature and state identity.
- Material, morphology, isotope/defect state, TTG response contract, and PBTE convergence.
- Locator, permission, preprocessing, row identity, uncertainty, and SHA-256.
- Same-grade `alpha_V` and `K_T`, or a justified `c_v` conversion with propagated uncertainty.

Current state: numeric Calorine candidate rows and mesh preflight exist, but
the candidate is not Ding-equivalent and has no source-grade uncertainty.
The Lowitzer pair is source-locked for its own synthetic-graphite lane only;
it is not a Ding-compatible `C_src` or TTG material closure.

### Base-Phi SI, alpha, and beta package

Required minimum records:

- Dimensionful action/free-energy coefficient provenance, or an independent paired base-Phi/SI response.
- Phi amplitude, reference state, field normalization, and `e0` in declared units.
- Paired `Delta_Phi` with `Delta_Tq` or `Delta_u_ph`, uncertainty, locator, preprocessing, row identity, and hash.
- A beta derivation independent of Landauer, target residuals, and holdout data.

Current state: no eligible paired alpha record and no independently fixed SI
Phi scale are present.

### Physical transport package

Required minimum records:

- Coefficient name, value, units, frame, temperature, chemical potential, and spatial response state.
- Retarded-correlator formula identifier, source locator, source hash, evidence status, and uncertainty.
- Finite-temperature normal/condensed matching and KMS/FDT residuals.
- Heat-flux and entropy-production propagation on the same state.

Current state: the natural-unit Kubo lane and formal SK/KMS lane are available,
but no physical state-matched coefficient record is admitted.

## EQUATION_OR_MAPPING

The bridge remains split into normalized measurement, dimensional response, and
source thermodynamics:

```text
y_TTG     = Delta_Tq(t) / Delta_Tq(0)
y_TTG^UET = Delta_Phi(t) / Delta_Phi(0)
Delta_Tq  = alpha_Phi_K * Delta_Phi
C_src(T)  = sum_mu c_mu(T)
Delta_Tq  = Delta_u_ph / C_src(T)
```

`C` remains a lane-specific collective system-behaviour coordinate, `Phi`
remains an effective response variable, `R_gen` remains a derived history
trace, and `R_obs` remains separate from physical dynamics.

## VERIFICATION

Full closure is allowed only when all of the following are true:

- All 10 major results satisfy `CLOSED_FOR_CORE`; the causal no-go exception is used only with a separately Core-closed named causal branch.
- All 10 currently open subresults have accepted evidence records and no unresolved controlling blocker.
- The three grouped input packages are accepted or their declared derivations are independently closed.
- Units, uncertainty propagation, source hashes, row identity, and provenance pass their gates.
- `Xie 2026` remains unread by calibration, fitting, tuning, and threshold paths.
- No normalized curve, comparator, Landauer identity, or synthetic control is relabeled as physical UET calibration or transport.
- The canonical gate changes to `T13_FULL_THERMODYNAMIC_BRIDGE_CORE_READY` with `claim_promotion=false`.

## CONTROLLING_BLOCKER

The nearest dimensional controller is
`dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`.
The Ding-compatible `C_src` package and the physical Kubo coefficient remain
independent blockers. Re-running the existing comparator cannot remove these
external-input blockers.

## NEXT_ACTION

Work in finite evidence-producing waves:

1. Acquire or derive the independent base-Phi SI anchor and `alpha_Phi_K` record.
2. Acquire an authorized Ding package or an explicitly accepted same-regime PBTE reproduction, including material and uncertainty closure.
3. Admit one physical state-matched Kubo coefficient and connect it to SK/KMS, entropy, and heat-flux records.
4. Promote the named causal branch to Core after its unchanged leakage, arrival, convergence, ledger, and no-manipulation checks are rerun.
5. Regenerate the full gate, closure matrix, dependency projection, and update log together.

If an external package is unavailable, close the route boundary as a measured
no-go and keep the affected Core result open. Do not manufacture rows, fit
`alpha_Phi_K`, read the holdout, or substitute a comparator.

## CLAIM_BOUNDARY

This roadmap is a closure controller, not a claim that Topic 13 is already
Core-ready. `CLOSED_FOR_CORE` means an internally integrated thermal bridge
ready for Core handoff; it is not external-ready and does not close global UET.

## Canonical Evidence

- `docs/core/artifacts/t13_topic13_closure_matrix.json`
- `docs/core/artifacts/t13_closure_input_package_audit.json`
- `docs/core/artifacts/uet_major_result_closure_register.json`
- `docs/core/artifacts/uet_major_result_dependency_unlock_gate.json`
- `docs/topics/0.13_Thermodynamic_Bridge/Result/artifacts/topic13_full_thermodynamic_bridge_core_ready_gate.json`

## Latest Source, Calibration, and Transport Triage (2026-08-24)

The source routes were checked against the three Core input packages without
accepting any new payload. Lowitzer and BIPM are source-locked thermodynamic
comparators, Kim 2018 is an external Green-Kubo comparator, and the existing
Calorine full-LBTE run is a numerical-stability boundary. They do not supply
the missing Ding-equivalent `C_src`, base-Phi/SI response pair, or physical UET
Kubo record.

The canonical matrix remains 21 `CLOSED_FOR_LANE`, 5 `CLOSED_AS_NO_GO`, 0
`CLOSED_FOR_CORE`, and 10 `OPEN` subresults. No dependency is unlocked and no
`alpha_Phi_K` value is emitted.

The next admissible state change requires one of the three missing packages:
an authorized or accepted same-regime Ding-compatible PBTE source, an
independent base-Phi/SI anchor, or a state-matched physical Kubo/SK/KMS record.
Existing comparators must not be rerun as substitutes.
