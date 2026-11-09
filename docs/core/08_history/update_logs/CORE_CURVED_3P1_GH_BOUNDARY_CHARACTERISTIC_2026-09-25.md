# Core Curved 3+1 GH Boundary-Characteristic Preflight

MAJOR_RESULT_CLOSURE: `CORE_CURVED_3P1_GH_BOUNDARY_CHARACTERISTIC_CLASSIFICATION / CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: Incoming, outgoing, and glancing mode classification plus a frozen-principal outward-flux sign check for the local five-field GH principal block. The audit covers four face normals and seven normal-shift ratios, including `|beta_n| = alpha`.

WHAT_REMAINS_OPEN: Constraint-preserving boundary conditions; physical incoming-radiation and gauge conditions; a non-periodic initial-boundary evolution; discrete constraint propagation, boundary stability, and convergence; self-consistent matter conservation; dimensional observable mapping.

DEPENDENCY_UNLOCKED: Boundary-design preflight only. The curved 3+1 parent remains `PARTIAL`; Gravity, constitutive transport, and Galaxy remain blocked.

STATUS: `PASS_GH_BOUNDARY_CHARACTERISTIC_CLASSIFICATION`; `claim_promotion=false`.

WHAT_CHANGED: Added a deterministic, source-hashed audit of the GH characteristic incidence and energy-flux sign. The result is now in the major-result closure register and curved-parent progress projection. The Topic 13 aggregate action now points to the already-unlocked curved-parent work rather than requesting the completed O(2)/He-4 integration again.

EQUATION_OR_MAPPING:

- `u0=psi`, `u1pm=Pi +/- Phi_n - gamma2*psi`, `u2_A=Phi_A`.
- Speeds: `0`, `-beta_n +/- alpha`, `-beta_n`.
- Frozen-principal flux: `F_n = 0.5 * U^T * S * A_n * U`.
- The GH field `Phi_iab` is a spatial derivative variable and is distinct from UET effective-response `Phi`. `C`, `R_gen`, and `R_obs` are not GH state variables.

VERIFICATION: 28 direction/shift cases passed; all characteristic bases have rank 5; characteristic and symmetrizer residuals are below `1e-12`; 12 subluminal cases passed with 64 deterministic flux samples each. Focused regression suite: 29 passed. Evidence artifact: `docs/core/07_artifacts/verification/curved_3p1_gh_boundary_characteristic_audit.json`, SHA-256 `45D2A7BE8B72F9586993CCEC0215C1C7DF053C9399E4A80B403C2832F28E5A88`.

CONTROLLING_BLOCKER: `curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing`.

NEXT_ACTION: Implement a non-periodic CPBC interface with separately specified constraint, physical, and gauge conditions; then test constraint propagation and boundary convergence. Keep dimensional observable mapping as an independent parent gate.

CLAIM_BOUNDARY: This result is a local frozen-principal characteristic/flux classification only. It does not impose a boundary operator, establish a well-posed nonlinear IBVP, validate a non-periodic solver, derive Einstein equations, or unlock Gravity.

## Literature Boundary

Rinne's GH boundary analysis treats constraint-preserving, physical-radiation, and gauge conditions separately and proves frozen-coefficient high-frequency boundary stability under the declared subluminal-normal-shift assumptions; this local audit does not inherit that proof for its own discretization ([Rinne 2006](https://arxiv.org/abs/gr-qc/0606053)). Calabrese and Sarbach show that simply nulling incoming constraint fields is not sufficient for arbitrary formulation parameters ([Calabrese & Sarbach 2003](https://arxiv.org/abs/gr-qc/0303040)).
