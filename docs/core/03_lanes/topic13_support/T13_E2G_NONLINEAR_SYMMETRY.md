# Nonlinear E2 versus continuous O(2)

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: The existing conditional E2 representation permits a cubic invariant not permitted by continuous O(2). Quadratic degeneracy alone cannot identify the material doublet with exact UET O(2) dynamics.
WHAT_REMAINS_OPEN: Actual representation including extra material symmetries, measured anisotropy coefficients, dispersion, kinetic residue and material thermal matching.
DEPENDENCY_UNLOCKED: None.
STATUS: CONDITIONAL_NONLINEAR_SYMMETRY_BOUNDARY.
WHAT_CHANGED: Degree1..6 polynomial audit, three tests and artifact; existing group implementation and production action unchanged.
EQUATION_OR_MAPPING: I3=s1^3-3*s1*s2^2=r^3*cos(3theta). Under the existing representation's rotations by2*pi/3 and reflections I3 is invariant, but not under arbitrary rotations. If present, V_aniso=c3*I3 produces internal torque3*c3*r^3*sin(3theta).
VERIFICATION: Three tests PASS. Material invariant dimensions for degrees1..6 are0,1,1,1,1,2; continuous-rotation dimensions0,1,0,1,0,1. Explicit cubic group residual below1.1e-15; a pi/6 rotation changes its value by1 at the unit-axis witness. Derivative test checks the torque sign.
CONTROLLING_BLOCKER: anisotropy_coefficient_or_suppression_bound_and_mode_identity.
NEXT_ACTION: Inspect source-backed anharmonic force constants or an independent nonlinear response bound for the selected shear mode. Only then define a harmonic/emergent-O(2) amplitude and time range. Do not insert arbitrary anisotropy into Core or identify lattice doublet count with conserved O(2) charge.
CLAIM_BOUNDARY: Symmetry-allowed does not mean coefficient nonzero. This is not a material no-go, measured torque, exclusion of emergent O(2), or Full Topic13 closure. No external numeric payload or holdout used.

## Algebra and interpretation

Writing z=s1+i*s2, the representation sends z to exp(2*pi*i/3)*z or its conjugate. Re(z^3) is invariant under both operations; a general phase rotation changes it. The existing group list repeats some representation matrices, which changes constraint multiplicity but not its nullspace.

The finite polynomial tests use more sampling angles than needed to distinguish homogeneous polynomials through degree6. The explicit invariant verifies the key degree3 result independently of singular-value rank classification. For continuous rotations, odd-degree homogeneous scalar invariants vanish and even-degree invariants are powers of r^2; the numerical irrational-angle generator is a check of this algebra, not a continuum dynamics proof.

If an additional exact s->-s symmetry applies to the actual mode, the cubic is forbidden; such an extra symmetry must be established, not assumed from a real two-component coordinate. Conversely, a small allowed coefficient may permit a controlled harmonic approximation. Neither possibility gives a measured alpha or automatically supplies the current operator used in the O(2) transport lane.

Literature context inspected in the preceding attempt: Tan et al., https://arxiv.org/abs/1106.1146, identifies low-frequency interlayer shear in multilayer graphene and graphite. Its abstract supports mode context, not the cubic coefficient or a UET identification. No new physical claim is taken from that abstract.

Evidence: artifacts/t13_e2g_nonlinear_symmetry_audit.json. Earlier failed tool request created no files; this run resumed only after ordinary usage was confirmed available.
