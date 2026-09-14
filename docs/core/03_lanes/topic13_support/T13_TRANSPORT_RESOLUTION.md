# Shared-action transport resolution

MAJOR_RESULT_CLOSURE: PARTIAL; numerical sensitivity and the scalar entropy-lift discrepancy are isolated. Transport convergence is not closed.
WHAT_IS_ACTUALLY_CLOSED: Ten locked one-factor cases were evaluated without changing the action or physical state. Radial/cutoff sensitivity dominates the examined controls. The scalar-lift entropy residual is accounted for by abs(K_xx-tr(K)/3)/T; using the full matrix contraction agrees with collision entropy to at most2.274e-12 in these cases.
WHAT_REMAINS_OPEN: Converged radial/cutoff response, simultaneous controls, fixed-direction angular basis, transition discretization, pseudoinverse sensitivity and physical material/protocol mapping.
DEPENDENCY_UNLOCKED: None.
STATUS: RESOLUTION_MEASURED_CONVERGENCE_NOT_CERTIFIED.
WHAT_CHANGED: Locked resolution plan, runner, complete results, integrity tests and this note. Added a disclosed post-hoc scalar-versus-tensor diagnostic after the first pass; reran the unchanged plan. No failing original gate was relabeled or threshold changed.
EQUATION_OR_MAPPING: Existing K_ab=b_a^T L^+ b_b. Kappa=tr(K)/3 is an isotropic approximation. For the declared x-force, tensor entropy is K_xx/T whereas the scalar lift uses kappa/T. No new material law is inferred.
VERIFICATION: All10 cases completed; three integrity tests passed, including source hashes and retention of failed original entropy gates. Four cases fail the original1e-7 scalar entropy gate. Matrix/kinetic agreement is an algebraic consistency result, not evidence of grid convergence or physical precision.
CONTROLLING_BLOCKER: radial_cutoff_transport_underresolution plus scalar_lift_of_nonisotropic_finite_grid_response.
NEXT_ACTION: Implement a named full-response-tensor lift preserving matrix/kinetic entropy balance without clipping or changing thresholds. Separately test jointly refined radial/cutoff controls and inverse sensitivity; do not interpret a tensor-consistency pass as converged conductivity.
CLAIM_BOUNDARY: Internal finite-cutoff moment response, not physical conductivity, external validation or full Topic13 closure. Existing same-action and frame identities remain narrow results; they never certified converged transport.

## Measured response

| Control | Kappa | Original scalar entropy gate |
| --- | ---: | --- |
| radial8, cutoff48 baseline |254.82472|PASS|
| radial12 |101.54920|FAIL|
| radial16 |132.25903|FAIL|
| radial24 |147.17901|FAIL|
| collision integral32 |255.14097|PASS|
| collision integral48 |255.12315|PASS|
| collision angle32 |254.82472|PASS|
| collision angle48 |254.82472|PASS|
| cutoff36 |160.11762|FAIL|
| cutoff60 |278.98538|PASS|

The fixed-cutoff radial sequence is not stable over the tested orders. Cutoff changes also relocate coarse quadrature nodes and change collision/transition integration support, so their effect is not isolated ultraviolet physics. The collision-angle result does not refine the six-direction moment basis. No continuum extrapolation or material uncertainty is reported.

At radial24 the scalar entropy residual is1.27691e-4, while the full matrix contraction differs from kinetic entropy by2.274e-13. This narrows the cause of that failed gate without deleting it. The matrix itself remains numerically underresolved as a transport coefficient.
