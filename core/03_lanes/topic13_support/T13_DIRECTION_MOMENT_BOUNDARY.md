# Directional moment coverage boundary

MAJOR_RESULT_CLOSURE: PARTIAL; a structural quadrupole limitation of the six-axis grid is identified and a positive-weight replacement candidate constructed.
WHAT_IS_ACTUALLY_CLOSED: Production directions are the six coordinate axes with equal weights. They integrate second moments correctly but give E[x^4]=1/3 instead of1/5 and E[x^2 y^2]=0 instead of1/15. The five-mode traceless quadrupole Gram matrix has rank2, not5. Off-diagonal shear sources p_x p_y, p_x p_z and p_y p_z vanish at every node; more radial nodes cannot repair that absence.
WHAT_REMAINS_OPEN: Weighted direction-rule plumbing, angular transport convergence, higher moments, transition resolution and physical material correspondence.
DEPENDENCY_UNLOCKED: No physical/Core unlock. A finite-grid repair route is identified, not installed.
STATUS: SIX_AXIS_QUADRUPOLE_DEFICIT_IDENTIFIED.
WHAT_CHANGED: Read-only production-basis audit, three tests, artifact and this note. No transport rerun, production direction change, parameter fit or historical artifact replacement.
EQUATION_OR_MAPPING: Add eight cube-corner directions (+/-1,+/-1,+/-1)/sqrt(3). Per-axis weight1/15 and per-corner weight3/40 follow from normalization and the mixed fourth moment. The resulting14-direction rule has rank5 and exact degree-four isotropic moments, but E[x^6]=7/45 differs from the sphere1/7.
VERIFICATION: Three tests PASS; actual imported production directions checked. Candidate quadrupole Gram error2.22e-16 is arithmetic agreement with the declared angular moments, not a transport error estimate. The new rule is a constructed quadrature candidate, not fitted material data.
CONTROLLING_BLOCKER: production_weighted_direction_interface and directional_transport_convergence.
NEXT_ACTION: Add an explicit weighted numerical direction rule while preserving six-axis baseline identity, then compare full moment responses and conserved projections. The fourteen-node rule cannot use the old uniform1/N weight. Independently continue transition quadrature/channel/interpolation checks.
CLAIM_BOUNDARY: This proves a representation limitation for the declared six-node quadrupole sources, not zero physical viscosity. It does not invalidate imported He4 viscosity measurements or by itself disprove degree-two heat response. Radial convergence around149.75 remains a result within a restricted angular discretization, not a continuum conductivity.

## Independent derivation

Uniform sphere x has marginal density1/2 on[-1,1], giving E[x^(2m)]=1/(2m+1). Symmetry plus (x^2+y^2+z^2)^2=1 then gives mixed fourth moment1/15. For the proposed signed-axis/cube rule, sign symmetry cancels odd monomials. With per-node weights a on6 axes and b on8 corners,6a+8b=1 and8b/9=1/15 yield the positive weights above. This is angular integration logic only; no new physical variable or dynamics is introduced.
