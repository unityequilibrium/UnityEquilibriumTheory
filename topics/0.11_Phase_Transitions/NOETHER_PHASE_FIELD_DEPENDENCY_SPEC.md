# Topic 0.11 Noether-Phase-Field Dependency Specification

## Purpose

This dependency lane asks one narrow question: can the core Wave 9 Noether
result constrain how Topic 0.11 interprets its conserved phase-field variable
without upgrading the topic's physical or publication claim?

The answer in this wave is conditional.  The final affine coordinate layer is
exact, but the current Topic 0.11 field has not been established as a signed
O(2) Noether charge and the constitutive equation of state and transport map
remain open.

## Factorized map and ontology

The accepted factorization is

\[
(\chi_1,\chi_2)
\longrightarrow N^\mu
\longrightarrow (\bar n,\bar j)
\longrightarrow (C,J).
\]

The microscopic and coarse-graining arrows are many-to-one.  Only the final
fixed-scale coordinate change is bijective:

\[
C=\frac{\bar n-n_{\mathrm{ref}}}{n_{\mathrm{scale}}},
\qquad
J=\frac{\bar j}{n_{\mathrm{scale}}L/T}.
\]

This means:

- the affine map is exact after a physical conserved variable, averaging rule,
  and scales have been declared;
- it does not reconstruct the microscopic O(2) field from `C`;
- it does not establish that the current Topic 0.11 `C` is an O(2) charge;
- it does not derive the double-well equation of state or transport
  coefficients from the covariant action;
- it introduces neither the matter-space response `Phi` nor the derived trace
  `R`.

## Inputs

The verifier reads, but does not rewrite:

- the four core Wave 9 state-map, formula, dependency, and program artifacts;
- the Topic 0.11 Wave 55 next-path gate;
- the isolated matter-space pilot artifact;
- canonical readiness metadata in `docs/meta/topic_readiness.json`.

Input identity uses a canonical scientific-payload hash that removes only
`generated_at`, `timestamp_utc`, and `environment`.  This avoids treating a
timestamp-only local rerun as new scientific evidence.

## Gates

The dependency artifact must record:

1. `core_hydrodynamic_coordinate_gate == PASS` for the exact fixed-scale
   affine coordinate layer;
2. `microscopic_inverse_boundary_gate == PASS` for both many-to-one
   counterexamples;
3. `topic_C_signed_charge_identity_gate == BLOCKED` until a system-specific
   mapping manifest, coarse-graining prescription, equation-of-state match,
   transport match, and source package exist;
4. `equation_of_state_and_transport_gate == BLOCKED` while the core Wave 9
   controller remains open;
5. `trace_and_space_separation_gate == PASS` so neither `R` nor `Phi` enters
   the map or feeds back into the phase-field dynamics;
6. `wave55_controller_preservation_gate == PASS` so estimator acquisition
   remains the topic controller;
7. `topic_promotion_gate == BLOCKED`.

## Status relationship

Canonical metadata currently records Topic 0.11 as `Structured / Tier B`.
This dependency wave has `topic_status_impact = NONE`.  Earlier pilot artifacts
that stored `Draft` are historical run snapshots; they are not rewritten as if
the later metadata existed at run time.

The independent Topic 0.11 controller remains:

```text
ch_finite_k_replicate_temporal_acquisition_plan_defined_execution_open
```

The controller for this dependency lane is:

```text
topic_0_11_signed_noether_charge_eos_transport_matching_missing
```

## Required next evidence

- declare and source a system-specific signed O(2) charge variable, or reject
  that identity explicitly;
- specify the covariant coarse-graining map to the topic field;
- derive or independently calibrate the charge-density equation of state;
- match susceptibility, mobility, relaxation, and gradient coefficients;
- execute Wave 55 replicate/temporal acquisition independently of this map.

## Claim boundary and falsification

Allowed language is limited to a conditional hydrodynamic state-coordinate
compatibility.  The result must be reduced or rejected for Topic 0.11 if a
consistent signed-charge declaration cannot be made, the required EOS or
transport matching fails, or the map works only after importing `Phi`, trace
feedback, or fitted evaluation-set parameters.

This lane does not validate an estimator, critical exponent, universality
class, material model, renormalization-group result, spacetime interpretation,
global universe closure, external benchmark, or solved phase-transition theory.

## Candidate mapping manifest

The repository now contains `Data/03_Research/noether_charge_coordinate_mapping.json`.
It declares a testable `C_phase` lane, not an accepted identity for the current Topic
0.11 field. Its status is `DECLARED_CANDIDATE_BLOCKED`: the affine coordinate form is
available, while the system-specific coarse-graining kernel, equation of state,
transport match, source package, and observable acceptance remain open.