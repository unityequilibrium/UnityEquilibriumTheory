# Core Curved 3+1 GH Boundary Projectors - 2026-09-25

MAJOR_RESULT_CLOSURE: `CORE_CURVED_3P1_GH_BOUNDARY_PROJECTOR_DECOMPOSITION / CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: Local generalized-harmonic incoming-tensor projector algebra on the ten-dimensional symmetric spacetime-tensor space. Constraint, physical-radiation, and gauge projectors have ranks 4/2/4 and pass idempotence, completeness, mutual-annihilation, and physical transverse/trace-free checks over 26 face normals.

WHAT_REMAINS_OPEN: Differential constraint and Weyl boundary residuals are not implemented; gauge data are not applied. Positive-normal-shift incoming `u2_A`, non-periodic SBP/SAT evolution, boundary stability and convergence, edge/corner compatibility, self-consistent matter-boundary behavior, and dimensional gravitational observables remain open.

DEPENDENCY_UNLOCKED: Projector/decomposition design only. The curved 3+1 parent remains `PARTIAL`; `GR_CLASSICAL_COMPATIBILITY_LANE` and downstream Gravity remain blocked.

STATUS: `PASS_GH_BOUNDARY_PROJECTOR_DECOMPOSITION`; `claim_promotion=false`.

WHAT_CHANGED: Added a source-matched projector module and deterministic audit. Existing periodic GH evolution and UET ontology were not modified. Registered the result as lane-level progress, not as a CPBC pass.

EQUATION_OR_MAPPING:

- `u1_minus = P_C u1_minus + P_P u1_minus + P_G u1_minus`, with ranks `4 + 2 + 4 = 10` for `-alpha < beta_n <= 0`.
- `P_G = I - P_C - P_P`; `P_C` and `P_P` identify differential constraint and physical/Weyl condition classes, while `P_G` receives algebraic gauge data.
- For `beta_n > 0`, incoming `u2_A` modes require a separate constraint-compatible boundary treatment.

VERIFICATION: 26 normalized face normals and 8 deterministic symmetric-tensor controls per normal; maximum algebraic residual `3.3306690738754696e-16`; focused regression suite: 28 passed. Artifact: `docs/core/07_artifacts/verification/curved_3p1_gh_boundary_projector_audit.json`; SHA-256 `1648BC84C8D47FB8701D7573B0B5E13A953643FA2B64F72B3297D54726C27C29`.

CONTROLLING_BLOCKER: `curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing`.

NEXT_ACTION: Implement the constraint and physical differential residuals plus gauge-data map as a separate non-periodic boundary module. First test its constraint subsystem and boundary energy behavior; then test convergence and box edges/corners. Handle positive-normal-shift `u2_A` separately. Do not change the parent gate until these tests and the dimensional observable map are addressed.

CLAIM_BOUNDARY: This closes projector algebra only, not an implemented constraint-preserving boundary condition or a well-posed initial-boundary value problem. Rinne's frozen-coefficient analysis is not inherited by the repository discretization; formulation-specific boundary stability must be established independently ([Rinne 2006](https://arxiv.org/abs/gr-qc/0606053)). Constraint consistency alone does not guarantee well-posedness for arbitrary formulation parameters ([Calabrese and Sarbach 2003](https://arxiv.org/abs/gr-qc/0303040)).
