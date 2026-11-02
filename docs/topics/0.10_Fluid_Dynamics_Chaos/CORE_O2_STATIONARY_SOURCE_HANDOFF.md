# SD02 result and handoff: stationary source response

Date: 2026-10-05. Owner: Topic10 shared Core/Topic13 derivation.
Status: COMPLETED_SCOPED_DERIVATION_ONLY; physical admissions remain open.
[Preregistered derivation](CORE_O2_STATIONARY_SOURCE_RESPONSE.md),
[locked contract](Data/03_Research/fluid_core_o2_stationary_source_response_contract.json),
[local candidate registry](Data/03_Research/fluid_core_o2_stationary_source_response_registry.json),
[verifier](Code/03_Research/Research_Fluid_Core_O2_Stationary_Source_Response.py),
[current result](Result/artifacts/fluid_core_o2_stationary_source_response.json).

## New result relative to SD01

The derivative of the declared gHF coincident self-energy is
T_g,abcd=lambda*(3delta_ab delta_cd-delta_ac delta_bd-delta_ad delta_bc),
contracted over the full symmetric pair indices. Its O(2) trace eigenvalue
4lambda agrees with Hartree, but its two traceless eigenvalues -2lambda
have the opposite sign to Hartree's +2lambda. Independent symmetric variations
and the expanded V2 coordinate Hessian check this exact result. Therefore an
original Hartree response kernel cannot be reused unchanged for this candidate.
No full pair-space loop, counterterm, contour or external vertex is calculated.
The negative bare eigenvalue is not a physical stability verdict.

The conditional source chain derivation fixes which state is eliminated. At
full F_y=0, y_s=-F_yy^-1 F_ys; first stationary derivatives are F_s, while
second derivatives contain -F_sy F_yy^-1 F_ys. For p=-Omega_star the correction
has the opposite sign. Current/stress defined through a source-varied generating
functional follow the same envelope/response rule, with explicit source contacts,
metric measure and convention factors. W and Omega are not silently equated.
SD02 derives those obligations; it does not compute gHF pressure, current or stress.

## Discriminating exact evidence

One prelocked synthetic quadratic fixture gives

    B^T A^-1 B = [[7,2],[2,7]]/5
    frozen pressure Hessian = [[4,1],[1,3]]
    relaxed pressure Hessian = [[27,7],[7,22]]/5.

Direct stationary substitution and exact first/mixed second finite differences
agree at both locked steps. Keeping only the frozen term or only the relaxation
term fails this fixture. These numbers are algebra controls, not material data.
State coordinate changes leave pressure and source Hessian unchanged; a source
coordinate/gain change instead transforms its Hessian by R^T chi R. This is not
a material gain calibration. Scale-2 E1/E2/E4 dimensional controls pass.

A decoupled null phase can be removed only when the source has no excluded
component. The strengthened quotient solver checks the full linear response
residual and rejects a phase-source obstruction, a removed massive direction
and a singular retained block. Invertibility alone does not imply positivity:
an indefinite state Hessian gives an explicit negative relaxation correction.
Nonstationary paths require F_y y_s, and a source-dependent integration endpoint
requires its boundary term. Both omissions are detected. Smooth cross derivatives
cannot be extended through a branch switch or critical zero mode by assumption.

## First execution, refinement and regression correction

The first diagnostic passed 147/147. Its [source](Result/previews/core_o2_stationary_source_first_verifier.py.txt)
and [result](Result/previews/fluid_core_o2_stationary_source_first_execution.json)
remain byte-identical. The current 149/149 adds two archive guards and replaces
two weak phase-domain checks with actual quotient-solving and rejection.
No fixture, formula, state, coefficient or threshold changed. The current artifact
records 95 input identities: 91 preregistered inputs, two immutable archives,
the locked contract and current verifier.

Four independent tests pass (pytest 2.53s): explicit stationary pressure/cofactor
solution and mixed Hessian, expanded V2 tensor and pair-index symmetry, quotient
source/null-domain rejection, and repeatable provenance/false or stale scope
rejection. The first test run had one handwritten expected cross entry 1/5
instead of 2/5; three other tests passed. Expanding
2(a+2b)^2-2(a+2b)(-a+b)+3(-a+b)^2=7a^2+4ab+7b^2 fixes its mixed derivative.
The [original test](Result/previews/core_o2_stationary_source_first_test.py.txt)
is retained. Only test arithmetic was corrected; verifier, contract and generated
149-check result remained unchanged. No failed result was renamed as a pass.

## Connection with existing Topic13 research

[Existing thermal source curvature](../0.13_Thermodynamic_Bridge/Result/artifacts/T13_THERMAL_SOURCE_CURVATURE_2026-10-03.md)
and [pair-source interface](../0.13_Thermodynamic_Bridge/Result/artifacts/T13_ACOUSTIC_SOURCE_PAIR_2026-10-03.md)
already retain stationary background, energy and polarization derivatives for
their own tree/acoustic parent. SD02 pins those reports, artifacts and relevant
source/registry identities without rerunning or borrowing their numerical result.
Their static matching target requires dynamic contact/virtual/full-thermal
completion. A damping/pole fit cannot replace that pressure obligation.

Topic13's +h Phi source h:E^3 and susceptibility E^-2 differ from charge mu:E
and the synthetic dimension-E source. Parent state, source normalization,
regulator, counterterms, mode admission and order of approximation must agree
before composition. Neither current kernel nor an existing collision resolvent
supplies that compatibility. These records guide tests of a future physical
calculation; they do not admit an interacting gHF/He-II response.

## Controlling boundary and SD03 handoff

All sixteen admissions remain false and all ten method gates remain NOT_STARTED.
No thermal integral, interacting state, full external vertex, physical current/
stress, material benchmark, fit, threshold relaxation or dependency unlock.
No original Core/Topic13 file is scientifically modified. F0-F8 and the inherited
central foundation audit failures/scientific-link DRIFT remain controlling.
No central gate rerun/promotion is claimed; the relevant central inputs did not
change during this Topic10-local derivation.

Method controller remains
finite_density_gHF_integral_state_renormalization_and_external_source_vertex_not_admitted.
Selected and overall physical controllers retain their SD01 values. The full
J00-J09 program remains open; J04/J05/J06 stay NOT_STARTED. SD02 completion means
the conditional derivation handoff is finished, not the physical pressure/vertex
method gate. Topic10 remains secondary and benchmark expansion deferred.

SD03 remains PLANNED. Its deliverable is the material heat/enthalpy and mass/charge
frame plus Legendre/SI and Topic13 fixed-constraint EOS/entropy/covariance/independent
protocol handoff. Before a physical numerical response, the existing method
controller requires the regulated finite-density same-functional state and its
source/contour/vertex contract. Source/ensemble and frame assumptions above must
be carried into that admission rather than replaced by the synthetic fixture.

## Provenance and ownership

All new files are owned by the Topic10 shared-response package in its existing
Code/Data/Result/topic-document namespaces. The two formula candidates are
registered locally with ontology, units, assumptions, derivation class, failure
mode, source/verifier/artifact and NOT_ADMITTED observable mapping. The central
Core registry is unchanged. Topic13 source files were restored to committed
bytes only after verifying a CRLF-to-LF-only checkout difference; no source or
artifact hash was refreshed to hide drift.

[Gapless HF](https://arxiv.org/pdf/hep-ph/0506157), v2 selected section II, supplies
the phenomenological approximation normalized in SD01. [External vertices](https://arxiv.org/pdf/hep-ph/0203008),
v3 selected section III/equations 28-31, establishes why a scheme-specific
external construction is separate from internal propagators. The exact tensor
and chain calculations here are conditional derivations, not paper replication.
