# SD04 result: finite-density matrix tadpole and auxiliary-state handoff

Date: 2026-10-13. Owner Topic10 shared Core/Topic13 secondary derivation.
Status: COMPLETED_SCOPED_DERIVATION_ONLY; no physical or full 2PI admission.
[Preregistered card](CORE_O2_MATRIX_TADPOLE_CONTRACT.md),
[contract](Data/03_Research/fluid_core_o2_matrix_tadpole_contract.json),
[registry](Data/03_Research/fluid_core_o2_matrix_tadpole_registry.json),
[verifier](Code/03_Research/Research_Fluid_Core_O2_Matrix_Tadpole.py),
[58-check result](Result/artifacts/fluid_core_o2_matrix_tadpole.json).

## New evidence and its limits

The finite-mu inverse matrix has antisymmetric frequency mixing 2mu*omega.
Its determinant is (omega^2+A)(omega^2+B)+4mu^2*omega^2 and both poles and
residues change if this mixing is dropped. The zero-flow coincident off-diagonal
sum vanishes by frequency reflection, not because the propagator/vertex is
identically diagonal. The same regulated trace log supplies I_plus=2L_Y and
I_minus=2L_D; the conserved-source derivative includes the mixing variation.
A normal scalar mass, its vacuum source shortcut or its collision resolvent is
therefore not automatically the new condensed-state propagator/vertex.

For gapless Y=mu^2+D,D>0 the small-k internal slope squared is D/(D+2mu^2).
The lower-pole thermal Q22 radial integrand tends to T and Q11's tends to zero,
before 1/(2pi^2). The 3D coincident tadpoles are locally IR integrable under
these conditions. This says nothing about differentiated response/transport
integrals, critical D=0, finite superflow or a material sound-speed prediction.
For positive poles, nB(e)/e has derivative -nB/e^2-nB*(1+nB)/(T*e)<0;
hence the unsubtracted thermal I_minus is negative for D>0. Subtracted vacuum
pieces can change the total renormalized sign; no state is inferred from it.

The zero-point integrand's expansion is

    ell=k+Y/(2k)-(Y^2+D^2)/(8k^3)
        +(Y^3+3Y*D^2-2mu^2*D^2)/(16k^5)+O(k^-7).

There is no explicit mu in the divergent coefficients at zero superflow, while
finite-mu vacuum dependence remains at k^-5. A fixed positive reference Y0
with common derivative subtraction yields

    ell_R=ell-E0-(Y-Y0)/(2E0)+((Y-Y0)^2+D^2)/(8E0^3)
    ell_R=[(Y-Y0)^3+3(Y-Y0)D^2-2mu^2*D^2]/(16k^5)+O(k^-7).

Omitting D^2 leaves -D^2/(8k^3), a logarithmic radial divergence. A moving Y0
adds source derivatives. The derived finite one-loop subtraction is a candidate;
it does not prove counterterm closure or regulator/renormalization-scale
independence of the full modified 2PI theory. The original normal-branch and
paper Hartree counterterms stay in their own scope. No physical Y0 is assigned.

## Actual conditional state equations

At a finite common regulator, or conditionally for an admitted consistent finite
functional, SD01's trace/traceless self-energy is represented by

    Omega_g=U+L-AY^2/(8lambda)+AD^2/(4lambda)
    AY=Y-m_squared-2lambda*x; AD=D-lambda*x.

Unrestricted gradients give AY=2lambda*I_plus and AD=-lambda*I_minus.
The mean-field gradient is (Y-D-mu^2)/2. Thus the changed traceless sign is
required; the old Hartree square sign changes the equation.
After these variations, restriction to Y=mu^2+D gives the scalar rest-state
obligation and condensate recovery

    D=mu^2-m_squared-2lambda*(I_plus+I_minus)=mu^2-m_squared-4lambda*Q11
    x=D/lambda+I_minus.

Imposing Ward before varying eliminates x. Recovering it is essential: an
arbitrary x does not solve the unrestricted state. Auxiliary stationarity is
not convex stability; Omega_xx=0 does not admit a physical minimum or positive
external Hessian. D>0/x>0, root existence/uniqueness, branch comparison and
regulator/reference/approximation control still need actual integral evidence.
No root or thermal momentum integral is solved in SD04.

At fixed Y,D,x the source derivative is Omega_mu=L_mu-mu*x. The stationary
charge is n=mu*x-L_mu, retaining the finite-mu vacuum contribution. Restricted
and unrestricted source derivatives agree only after the trace gap and x
recovery. This is the actual conditional state chain feeding SD02's implicit
Hessian and SD03's fixed-pressure/material conversion; neither their full
source response nor a signed-charge-to-atom map is supplied here.

## Executions, first failures and independent verification

Startup stopped before algebra because repository-root discovery used
parents[4] instead of parents[5]. The [startup source](Result/previews/core_o2_matrix_tadpole_startup_verifier.py.txt)
is retained. The [first complete source](Result/previews/core_o2_matrix_tadpole_first_verifier.py.txt)
and [first complete result](Result/previews/fluid_core_o2_matrix_tadpole_first_execution.json)
remain byte-identical:53/55, with divergent_coefficients_no_explicit_mu and
finite_vacuum_mu_derivative failing. The full Laurent identity already passed;
coefficient extraction was applied to an unexpanded expression divided by u.
Expanding that expression before coefficient lookup fixes its interpretation,
without changing the series, equations, fixtures, source identities or tolerances.
Three archive/root-repair guards give the current58/58. No failure is discarded.

Four independent focused regressions pass (18.33s): direct inverse-matrix
frequency integration and finite-T Matsubara sum at one momentum; source/mass
finite differences against direct frequency derivatives;60-digit UV/IR checks;
and repeatable source/archive/scope rejection. These numerical controls do not
integrate momentum to construct a thermal tadpole, solve a state, compare a
material row, fit a scale or validate a physical response.
All118 preregistered and123 current input identities are fresh.

## Shared handoff and remaining controller

| Shared obligation | Evidence supplied by SD04 | Still required |
| --- | --- | --- |
| Finite-mu matrix Dyson/tadpole state | Full rest kernel, residue weights, finite-T equal-time chain and scalar conditional root equation | Actual self-consistent integrals, positive condensate, existence/branch/stability and refinement |
| Renormalization and same-source pressure | Both trace/traceless divergences and compatible one-loop subtraction candidate | Full modified 2PI counterterms/source proof, physical reference/scale decision and regulator/approximation control |
| Condensed source response | Unrestricted/restricted charge chain and prohibition on early-Ward arbitrary-x state | Full admissible state/pair Hessian, dynamic source vertices, causal response and SD02 obligations |
| Topic13 EOS/heat/material | A declared state equation and derivative interface to SD03 | Same-state atomic/current/chemical-potential/action-measure map, fixed-pressure EOS/covariance, independent protocol and remainder |

The [published Core same-state handoff](../../core/03_lanes/topic13_support/CORE_HE4_SAME_STATE_HANDOFF_2026-10-04.md)
is unchanged and remains SPECIFIC_ADDITIONAL_INPUTS_REQUIRED under
same_state_atomic_current_action_measure_and_low_T_remainder_not_admitted.
Its 1.7K calibration and low-T response domains are not interchangeable.
SD04 does not supply independent length/time/action or atomic normalization.
No calibration/readout gains or previously viewed material rows are rematched.

The existing Topic10 method controller remains
finite_density_gHF_integral_state_renormalization_and_external_source_vertex_not_admitted.
All ten physical method gates are NOT_STARTED; sixteen admissions false;
physical scales/material covariance null; physical J04/J05/J06 remain unexecuted.
Next shared decision: complete the modified functional's counterterm/source
contract before admitting an integral-state solver or source-response numerics.
The full J00-J09 program and overall vector-origin/material-frame controller
remain open. Topic10 stays secondary; benchmark expansion stays deferred.

## Provenance and publication

All SD04 scientific files belong to the existing Topic10 namespaces. Its three
candidate formulas record ontology, units, assumptions, failure modes and
NOT_ADMITTED observables in the local registry; no primary Core equation or
central registry is added/edited. PR34's three published Core source/artifact/
audit files were incorporated byte-identically from main, with both October5
ledger histories preserved. SD01-SD03 remain draft dependencies; inherited
foundation FAIL/BLOCKED and scientific-link DRIFT are not repaired or called green.
No fresh central audit pass is claimed, no raw/private or material inputs published.

[Alford et al.](https://arxiv.org/pdf/1310.5953), selected rest kernel and appendix
A/Table I, is the matrix/vacuum comparator. [Gapless HF](https://arxiv.org/pdf/hep-ph/0506157),
selected functional/renormalization passages, motivates the phenomenological
approximation. SD04 derives its own conditional auxiliary algebra; it does not
replicate full papers or transfer their original counterterms to this scheme.
