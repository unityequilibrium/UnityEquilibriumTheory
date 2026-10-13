# SD01 shared derivation handoff: conditional gapless functional

Date: 2026-10-05. Owner: Topic 10, supporting Core O(2) and Topic 13.
Status: COMPLETED_SCOPED_DERIVATION_ONLY. No physical gate admission.
Canonical candidate: [frozen source/derivation card](CORE_O2_GAPLESS_FUNCTIONAL_CANDIDATE.md).
Evidence: [192-check artifact](Result/artifacts/fluid_core_o2_gapless_functional_audit.json),
[locked contract](Data/03_Research/fluid_core_o2_gapless_functional_contract.json),
[verifier](Code/03_Research/Research_Fluid_Core_O2_Gapless_Functional.py).

## What SD01 answers

The declared modified approximation has a mean-field residual and an internal
static inverse block satisfying K_g J phi = J h for arbitrary real symmetric
coincident tadpoles Q. At nonzero h=0 this supplies a static zero mode.
It resolves the conditional algebra question posed by SD01. It does not establish
that a self-consistent finite-density propagator realizes those tadpoles.
The phenomenological correction is explicit; it is not derived from the
unmodified microscopic diagram expansion. Primary Core action files are unchanged.

## Variation from one declared approximation

Use natural units, d=m^2-mu_charge^2, x=phi^T phi, N=2 and
lambda_paper/N=lambda_here=lambda. With Q=[[a,c],[c,b]],

    V2_H = lambda/4 * ((tr Q)^2 + 2 tr(Q^2))
    Delta V2 = -lambda/2 * (2 tr(Q^2) - (tr Q)^2)
    V2_g = lambda/4 * (3 (tr Q)^2 - 2 tr(Q^2))
    delta V2 = (1/2) tr(Sigma delta Q)
    Sigma_H = lambda * ((tr Q) I + 2 Q)
    Sigma_g = lambda * (3 (tr Q) I - 2 Q)

The single symmetric coordinate c varies both Q12 and Q21: Sigma12=partial_c V2,
whereas Sigma11=2 partial_a V2 and Sigma22=2 partial_b V2. Doubling the
c derivative is a detected negative control.

For the fixed-Q homogeneous field part of the declared approximation,

    V_field = d*x/2 + lambda*x^2/4 + lambda*x*tr(Q)/2
              + lambda*phi^T Q phi + V2_g
    h = partial_phi V_field = (d+lambda*x+lambda*tr(Q))*phi + 2lambda*Q phi
    K_g = (d+lambda*x) I + 2lambda*phi phi^T + Sigma_g
    J = [[0,-1],[1,0]]
    K_g J phi = J h

Delta V2 has no explicit phi derivative at fixed Q. V_field records the
field-dependent part; it is not a substitute for the full trace-log, propagator
variation, regulator, counterterms or source-varied 2PI functional.
With Sigma_t=Sigma_H+t*(Sigma_g-Sigma_H), the exact defect is

    K_t J phi - J h = 2lambda*(1-t)*(2Q-tr(Q)I) J phi.

The t=0 and t=1/2 negatives detect missing or misnormalized corrections.
phi has dimension E, Q dimension E^2, V2 dimension E^4, Sigma and K dimension E^2,
and h dimension E^3. These are natural-unit relations, not an SI material map.
Q_ab is unrelated to the material-rate symbol Q=Dt Phi; canonical phi and the
papers' diagram functional Phi are both distinct from UET Phi.

## Old and modified stationary equations remain separate

For phi=(rho,0), I_plus=a+b and I_minus=a-b, conditional mean stationarity gives

    rho^2 = (mu_charge^2-m^2-lambda*(2I_plus+I_minus))/lambda
    Y = m^2+2lambda*rho^2+2lambda*I_plus
    D_g = lambda*rho^2-lambda*I_minus
    D_H = lambda*rho^2+lambda*I_minus
    Y-D_g-mu_charge^2 = 0
    Y-D_H-mu_charge^2 = -2lambda*I_minus.

The prior Hartree residuals evaluated on the modified witness are
[-2lambda I_minus,0,-2lambda I_minus]. Thus the new conditional identity does
not turn the old scheme's failures into passes. Synthetic tadpoles, including
negative I_minus, are algebra controls rather than solved or admitted states.
A positive synthetic radial block is not full spectral or thermodynamic stability.

## Evidence and retained first execution

The first complete verifier passed 186/186 without adjusting a state, coefficient
or threshold. Its [source](Result/previews/core_o2_gapless_functional_first_verifier.py.txt)
and [result](Result/previews/fluid_core_o2_gapless_functional_first_execution.json)
are preserved byte-for-byte. Adding four fixed-Q mean-field variation checks and
two archive-identity checks gives the current 192/192 result, with 81 input hashes.
A path-binding editor attempt stopped on historical Windows separators; only the
current lookup was normalized. The first result retains its original keys.

Four focused regressions pass: independent expanded-coordinate functional
variation at an extra rational point/rotation, original-versus-modified residuals,
repeatable fresh provenance, and rejection of altered scope/normalization or stale
source identity before algebra. The extra points test implementation, not new
material benchmarks. All sixteen admissions stay false and all ten method gates
stay NOT_STARTED. Neither the three Core source inventories nor the symbolic
nonzero cross-Hessian obligation computes a microscopic vertex.

## Handoff to SD02 and Topic 13

SD02 remains PLANNED. For a differentiable stationary branch with a phase-fixed
or quotient domain and an invertible admissible pair/state Hessian, chain
differentiation requires

    H_ext = Gamma_phiphi - Gamma_phiG * Gamma_GG^(-1) * Gamma_Gphi
    p_thetatheta = -Omega_thetatheta
                  + Omega_thetay * Omega_yy^(-1) * Omega_ytheta.

These formulas identify the next obligation; SD01 has not evaluated these
Hessians or derived a source-varied current/stress. Internal inverse propagator,
frozen-state curvature and external response must be compared explicitly using
the same sources, measure, regulator and counterterms. Local/dynamic Ward
identities, causal response and collision/KMS kernels remain separate.
Existing normal-branch ladder and finite-grid collision resolvents cannot be
identified with delta Sigma_g/delta G or reused as condensed material kernels
without an explicit derivation.

Before material use, Core and Topic 13 still need a finite-density integral state,
renormalization, justified approximation/error control, heat/enthalpy and mass/charge
frame, Legendre/SI atom/state mapping, fixed-constraint EOS, entropy reference and
covariance, and an independent dynamic measurement protocol. Physical J04/J05/J06
remain NOT_STARTED. Topic 10 stays secondary; new benchmark expansion is deferred.

## Required repository audit boundary

F0 inventory regeneration used --json --no-write: PASS_WITH_DISCLOSED_GAPS,
inventory_gate_status BLOCKED, controller
topic_formula_audits_not_code_complete_or_correspondence_incomplete.
Equation-foundation audit exits 1 with 222 existing missing-path errors and
foundation_gate_status BLOCKED. Central registry/gate and audit implementations
match committed HEAD after newline normalization; this wave does not repair or
promote that central gate. Scientific-link --check exits 1 with DRIFT against the
existing artifact; its six input files are likewise unchanged from HEAD.
The read-only physical-path build passes all eight checks.
Compatibility --json --no-write passes its audit with compatibility_status BLOCKED
(matter_space_causal_response and o2_to_legacy_double_well). The bundled runtime's
first attempt lacked SciPy; rerunning in the existing repository virtual environment
completed successfully. No generated central audit artifact was overwritten.
These central failures prevent any claim that all repository audits are green.
The candidate addendum stays unmerged and outside Core admission.

Current method controller:
finite_density_gHF_integral_state_renormalization_and_external_source_vertex_not_admitted.
Selected physical controller remains
useful_certified_current_error_and_interacting_Noether_heat_frame_material_correspondence_open;
overall remains vector_momentum_constitutive_origin_and_material_frame_admission_open.

## Source scope and OpenAI relevance

[Gapless HF](https://arxiv.org/pdf/hep-ph/0506157), v2 equations 9-18 and selected
renormalization/limitations passages, motivates the explicit phenomenological
correction. [Stationary external vertices](https://arxiv.org/pdf/hep-ph/0203008),
v3 equations 19-31 and selected discussion, motivates the separate response
obligation. Selected sections were reviewed; full paper results were not replicated.
OpenAI theorem/checker practice contributes frozen assumptions, negative controls,
retained failures and reproducible evidence discipline. It supplies no derivation
of this functional, He-II state, SI map or independent material validation.

## File ownership and path disposition

Topic 10 owns the shared derivation card, locked contract, verifier/tests, local
result and immutable first-execution archives at their linked canonical paths.
The correspondence candidate is owned by this Topic 10 shared package at
`docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry_topic10_o2_gapless_functional_addendum.json`.
It extends the prior interacting-method addendum; its ontology, units, source,
implementation and claim ceiling are recorded there. It is unmerged into the
central registry and has no admitted Core family/operator disposition.
Organization control-plane files are unchanged. This classification does not
repair central scientific-link drift or unlock F0-F8. The local UPDATE_LOG and
repo work ledger are the wave's historical records.
