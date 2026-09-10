# Transition coordinate correspondence audit

MAJOR_RESULT_CLOSURE: PARTIAL; a weighted-coordinate interpolation mismatch is established and its coordinate-covariant pullback derived.
WHAT_IS_ACTUALLY_CLOSED: A manufactured same-node weight change gives transition amplitude -10.333333 instead of -9 under the current map. The pullback gives -9 and preserves the quadratic transition form. Actual six- and fourteen-direction interpolation also fails constant-psi reproduction when applied directly to z.
WHAT_REMAINS_OPEN: Production repair, full-path response comparison, interpolation approximation, angular/transition convergence and material mapping.
DEPENDENCY_UNLOCKED: None; full_core_unlock=false.
STATUS: WEIGHTED_COORDINATE_MISMATCH_IDENTIFIED.
WHAT_CHANGED: Read-only audit of the existing mapping, four tests, frozen counterexample artifact, this note and a registry proposal. Production mapping and prior artifacts remain unchanged.
EQUATION_OR_MAPPING: z=sqrt(W)*psi. If psi_e=S.T*psi_b, then z_e=sqrt(W_e)*S.T*inv_sqrt(W_b)*z_b. Therefore transition rows U_b=V_e*sqrt(W_e)*S.T*inv_sqrt(W_b), not V_e*S.T.
VERIFICATION: Four tests PASS: manufactured amplitude, rectangular-map quadratic identity, exact-weight reparameterization cancellation and invalid-weight rejection. Actual base and channel states evaluated for both direction rules at the previous coarse pilot controls. F0 PASS_WITH_DISCLOSED_GAPS,369 formula rows,0 duplicates.
CONTROLLING_BLOCKER: production_coordinate_map_repair. Existing interpolation was applied directly between weighted z coordinates without the susceptibility factors required for interpolation of psi.
NEXT_ACTION: Preserve this counterexample; implement the explicit coordinate map as a named revised path, then rerun full tensor response and report all changes without retuning. Check rate-weighted quadratic forms and interpolation convergence separately.
CLAIM_BOUNDARY: This is a coordinate-consistency result conditional on interpreting normalized interpolation as a map of psi. A direct interpolation of z could instead be declared as a different numerical ansatz, but it is not the same scalar interpolation and requires independent consistency justification. No physical conductivity, viscosity, full Topic13 or global closure follows.

## Why existing checks missed it

The existing S columns sum to one and preserve a constant unweighted function. The exact channel rows, however, contain incidence coefficients divided by sqrt(w_exact). The basis solver uses z_basis=sqrt(w_basis)*psi_basis. Passing z directly through S.T does not preserve psi when weights differ.

Projection can enforce selected invariant columns after an incorrect mapping. A positive sum of outer products can also remain positive. Thus conservation, positivity and a small post-projection residual alone do not establish coordinate correspondence.

For an arbitrary positive diagonal rate matrix D, the corrected pullback obeys z_b.T U_b.T D U_b z_b = z_e.T V_e.T D V_e z_e. This does not prove that the chosen interpolation approximates the physical continuum or that channel rates are a converged collision integral.

## Numerical evidence and limits

For the manufactured example, exact weights are (1,4,9,16), basis weights (4,9,16,25), S=identity and psi=(1,2,4,8). The incidence row is (+1,+1,-1,-1). The expected amplitude is -9. Legacy mapping gives -10.333333 and a constant defect0.916667; the coordinate pullback gives -9 and zero constant defect.

The actual grids give maximum constant-channel errors approximately1.96e65 (axis6) and2.28e56 (axis_cube14) with the legacy map, versus3.68e-16 and5.31e-16 with the coordinate map. These very large unweighted maxima include exponentially tiny tail susceptibility weights. They are NOT material error estimates or conductivity changes: rates must be included before interpreting physical importance. The finite manufactured counterexample establishes the mismatch without relying on these tail extremes.

Evidence: artifacts/t13_transition_coordinate_map_audit.json. Previous weighted-direction pilot remains a historical measurement of the old transition mapping, not evidence that its small kappa change validates that mapping.
