# Finite-cutoff current metric identity

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: Integration-by-parts surface terms reconcile the existing Bose momentum metric with thermodynamic charge and enthalpy densities on five finite cutoffs.
WHAT_REMAINS_OPEN: Complete basis, physical current matching, self-energy and material calibration.
DEPENDENCY_UNLOCKED: None.
STATUS: FINITE_CUTOFF_CURRENT_IDENTITY_CHECKED.
WHAT_CHANGED: Standalone surface-term audit and five tests; production current projection unchanged.
EQUATION_OR_MAPPING: T*G00=w-Bw and G01=n-Bn, where the existing first basis vector is p/T. Bw=P^3 sum_q E_q(P)f_q(P)/(6*pi^2); Bn=P^3 sum_q q*f_q(P)/(6*pi^2).
VERIFICATION: Five tests PASS, including charge conjugation and zero-charge state. Corrected identities agree below4e-15 in the evaluated rows. Bw/w at cutoffs2/4/8/12/24 is0.1021/6.929e-4/1.504e-9/9.162e-16/2.239e-35. F0 inventory369 rows, no duplicates, PASS_WITH_DISCLOSED_GAPS; foundation/compatibility audits PASS with physical gates BLOCKED.
CONTROLLING_BLOCKER: basis_completeness_and_physical_collision_current_matching, not the metric surface term at the tested production cutoff24.
NEXT_ACTION: Keep the existing metric projection. Investigate missing physical current/material matching rather than adjusting projection to compensate for negligible surface terms. Repeat boundary audit if state, masses or cutoff change.
CLAIM_BOUNDARY: Synthetic normal mixture T=.25, mu=.2 and existing action inputs only; no full thermodynamic/transport closure, no external or holdout input and no parameter fitting.

## Derivation and interpretation

For each species df/dp=-(p/(E*T))*f*(1+f). Integration by parts of p^3*E*f gives the enthalpy identity; integration by parts of p^3*f gives the charge identity. The lower boundary vanishes and the upper boundary is retained, not clipped. G00 has units energy^2, G01 energy^3, w and Bw energy^4, n and Bn energy^3.

Consequently the finite-cutoff projection ratio is T*(n-Bn)/(w-Bw), not exactly T*n/w. The production code already uses the metric ratio; this audit does not justify replacing it. At its tested cutoff24 the surface correction is negligible, while the corrected numerical identity residual is limited by quadrature/floating-point error. The1e-35 boundary fraction is an analytic tail estimate evaluated numerically, not a1e-35 precision claim for the metric.

Evidence: artifacts/t13_current_metric_surface_audit.json (runner, test and coupled-source hashes).
