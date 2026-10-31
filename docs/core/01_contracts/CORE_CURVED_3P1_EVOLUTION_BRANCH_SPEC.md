# Core Curved 3+1 Evolution Branch Specification

MAJOR_RESULT_CLOSURE: `GH_PERIODIC_PRESCRIBED_TOPIC13_MATTER_READY / PARENT_PARTIAL`

WHAT_IS_ACTUALLY_CLOSED: The fixed-geodesic ADM branch remains closed as a branch-local hyperbolicity no-go. The selected generalized-harmonic branch closes its principal/characteristic system, complete nonlinear vacuum Eqs. (35)-(40) RHS, periodic RK4 evolution with a fixed characteristic CFL contract, and separate local boundary-classification lanes. The prescribed Topic 13 He-4/O(2) stress tensor, Eulerian projections, trace-reversed GH source, vacuum-null control, and natural-to-SI multiplicative scaling also pass. A source-matched ideal interferometer response for one linear TT plane-wave mode and a separate evolved pure-gauge TT-null negative control are closed as bounded diagnostic lanes.

WHAT_REMAINS_OPEN: Constraint-preserving non-periodic boundaries, self-consistent matter evolution/conservation, multi-chart/strong-field controls, physical SI Einstein-coupling provenance, and the general curved/nonlinear detector-observable mapping remain open. The closed single-mode response does not provide GH wave-zone extraction or detector calibration.

DEPENDENCY_UNLOCKED: The bounded linear TT-mode detector-response and evolved GH gauge-false-positive diagnostic lanes are recorded only; neither unlocks a downstream topic. CPBC and the general dimensional-observable mapping remain active Core work. Gravity/GR remains blocked.

STATUS: `PARTIAL_CURVED_3P1_GH_PERIODIC_PRESCRIBED_MATTER_READY`

WHAT_CHANGED: Added a separate periodic vacuum evolution module using classical RK4 and `dt <= cfl min(dx_i)/max(alpha+||beta||_2)`. The stepper evaluates the verified nonlinear RHS at all stages and records unprojected gauge, reduction, and curl constraints without filtering, artificial dissipation, clipping, or fitting.

EQUATION_OR_MAPPING:

- Evolve the spacetime metric `psi_ab`, its normal derivative `Pi_ab`, and spatial derivatives `Phi_iab`.
- Enforce the reduction constraint `C_iab = partial_i psi_ab - Phi_iab`.
- Enforce the gauge constraint `C_a = H_a + Gamma_a` with a declared gauge source `H_a`.
- Keep `psi_ab` as geometry, not `Phi`; keep the stress-energy projection lane-specific, not universal `C`; exclude `R_gen` and `R_obs` from the dynamical state.

VERIFICATION:

- Match the analytic GH principal symbol and obtain a complete characteristic basis in every preregistered direction.
- Classify incoming, outgoing, and glancing modes across 28 direction/normal-shift cases, including the sonic edges `|beta_n| = alpha`; verify nonnegative outward principal flux on 12 subluminal controls.
- Keep the boundary-characteristic result lane-local: it neither imposes CPBC nor verifies a non-periodic initial-boundary evolution.
- Demonstrate symmetric or strong hyperbolicity and causal declared characteristic speeds.
- Pass Minkowski, gauge-wave, robust-stability, and constraint-violation controls.
- Pass temporal and spatial convergence without clipping, fitted damping, or hidden filtering.
- Verify constraint damping and propagation separately from solution accuracy.
- Add constraint-preserving boundary tests before any non-periodic or black-hole claim.
- Periodic gauge-wave spatial order is at least `1.9845`; RK4 temporal self-convergence order is `3.9266`.
- The constant off-diagonal reduction violation follows `exp(-gamma2 t)` within the locked relative-error threshold.
- The separate ideal interferometer measurement lane passes 10 analytic/source-matched controls and 13 focused regression tests; no detector data are consumed.
- The evolved periodic harmonic gauge-wave negative control has nonzero raw metric perturbation (`0.0496236`) but zero TT projection and detector strain; no time-series waveform is emitted.
- Keep the parent partial until non-periodic boundary, self-consistent matter, and observable gates pass.

CONTROLLING_BLOCKER: `curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing`

NEXT_ACTION: Apply CPBC in a non-periodic evolution scheme; independently connect verified GH wave-zone extraction and temporal Fourier mapping to the bounded detector-response operator. Treat self-consistent matter evolution as a separate conservation-compatible wave.

CLAIM_BOUNDARY: This closes bounded periodic vacuum evolution, a prescribed Topic 13 matter-source lane, a separate standard-GR ideal measurement operator for one linear TT mode, and a pure-gauge false-positive control. Neither GW lane is a physical waveform extraction, UET prediction, or external validation. These results do not establish a production numerical-relativity solver, self-consistent matter-coupled curved UET solution, Einstein-equation derivation, or Gravity compatibility.

## Stop Rules

The branch closes `CLOSED_FOR_LANE` only when every verification item above passes with source-locked equations and fixed thresholds. A reproducible principal-symbol or constraint-propagation failure closes the attempted formulation as `CLOSED_AS_NO_GO` and requires a new named branch. More runtime alone cannot promote either result.

## Linearized GW Detector-Response Measurement Lane (2026-09-25)

MAJOR_RESULT_CLOSURE: `CORE_CURVED_3P1_GW_DETECTOR_RESPONSE_LANE / CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: For one linearized spatial metric Fourier mode in an asymptotically flat wave zone, the metric perturbation can be TT-projected and mapped through the source-matched finite-frequency equal-arm, single-round-trip interferometer response without optical cavities. The lane has explicit SI units for frequency, arm length, exact `c`, dimensionless strain, and equivalent length. It is a standard-GR measurement operator, not a new UET dynamic equation.

WHAT_REMAINS_OPEN: GH wave-zone extraction, time-series Fourier mapping, optical cavities/control loops, detector calibration/noise/uncertainty, non-periodic CPBC evolution, and nonlinear or strong-field observables.

DEPENDENCY_UNLOCKED: This bounded measurement-operator lane only. The parent remains `PARTIAL`; general observable mapping and CPBC remain open; Gravity remains blocked.

STATUS: `PASS_GH_LINEAR_GW_INTERFEROMETER_RESPONSE`; `claim_promotion=false`.

WHAT_CHANGED: Added a deterministic response module, source metadata record, audit artifact, focused tests, and Core parent/registry/dependency-progress integration. No UET state variables or periodic evolution equations changed.

EQUATION_OR_MAPPING:

- `h_ij = gamma_ij - delta_ij`, with `h_TT = P h P - (1/2) P tr(P h P)` and `P_ij = delta_ij - n_i n_j`.
- For `q = pi*f*L/c`, the arm transfer is `T(f,mu) = (1/2)[sinc(q(1-mu)) exp(-i q(3+mu)) + sinc(q(1+mu)) exp(-i q(1+mu))]`.
- `D_ij(f) = (1/2)(u_i u_j T_u - v_i v_j T_v)`, `h_D(f)=D_ij h_TT_ij`, and `DeltaL_equiv=L h_D`.

VERIFICATION: 10/10 analytic controls pass, including low-frequency and finite-frequency plus response, cross polarization, TT transversality/trace, pure-gauge rejection, rotational covariance, negative-frequency conjugacy, SI length scaling, and source/hash availability. Focused tests: 13 passed. The formula follows [Liang et al. (2019)](https://arxiv.org/abs/1901.09624), Eqs. (2)-(6), Sec. II.3; no detector data or holdout rows were consumed.

CONTROLLING_BLOCKER: `curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing`.

NEXT_ACTION: Verify GH wave-zone extraction and time/Fourier normalization as a separate lane, then assess calibration/noise only from permitted source-backed detector inputs; continue CPBC independently.

CLAIM_BOUNDARY: Ideal standard-GR single-mode detector response only; no data validation, calibrated detector pipeline, GH evolution-to-observable result, nonlinear/strong-field map, UET prediction, parent closure, or Gravity unlock.

## Evolved GH Harmonic Gauge-Wave TT Null Control (2026-09-25)

MAJOR_RESULT_CLOSURE: `CORE_CURVED_3P1_GH_GAUGE_WAVE_TT_NULL_CONTROL / CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: The existing periodic GH harmonic gauge-wave control is evolved and passed through the metric-to-TT projection and ideal detector measurement operator. The raw metric perturbation is nonzero, but its only spatial component is longitudinal to the declared propagation direction, so the TT projection and detector strain are zero across the grid. This guards against classifying the existing coordinate/gauge control as gravitational radiation.

WHAT_REMAINS_OPEN: The evolution result contains no metric snapshots or worldtube time series. No physical outgoing radiative solution, non-periodic CPBC evolution, extraction sphere, retarded-time map, waveform extraction, or detector calibration is present.

DEPENDENCY_UNLOCKED: None. The result is only a false-positive exclusion control; the parent remains `PARTIAL` and Gravity remains blocked.

STATUS: `PASS_GH_HARMONIC_GAUGE_WAVE_TT_NULL_CONTROL`; `claim_promotion=false`.

WHAT_CHANGED: Added a source-screen record, deterministic audit, regression tests, and parent/dependency-progress integration. The GH evolution equations and solver were not changed.

EQUATION_OR_MAPPING:

- For the exact control, `h_ij = gamma_ij - delta_ij = diag(h_xx,0,0)` and `n_i=(1,0,0)`.
- `P_ij=delta_ij-n_i n_j=diag(0,1,1)`, hence `P h P=0`, `h_TT=0`, and `h_D=D_ij h_TT_ij=0`.

VERIFICATION: On a `12x5x5` periodic GH grid with input gauge-wave amplitude `0.05`, the integration reaches coordinate time `0.02` in 4 RK4 steps. The raw metric perturbation maximum is `0.049623581088992896`; maximum TT residual and detector strain are exactly `0.0`. Projection, filtering, clipping, and fitting are disabled. The solver exposes only a final state and scalar constraint diagnostics, not a metric history.

CONTROLLING_BLOCKER: `curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing`.

NEXT_ACTION: Build a non-periodic CPBC evolution that exports a declared fixed-radius/worldtube metric time series with lapse/shift and constraint diagnostics. Then select an extraction route based on the available background: gauge-invariant metric RWZ multipoles require a spherical background and extraction-sphere data ([Fontbuté et al.](https://arxiv.org/abs/2508.03799)); finite-radius `Psi_4` corrections require curvature data and radius/background controls ([Nakano et al.](https://arxiv.org/abs/1503.00718)); Cauchy-characteristic extraction requires worldtube data plus characteristic evolution to null infinity ([Reisswig et al.](https://arxiv.org/abs/0912.1285)). None is implemented by this control.

CLAIM_BOUNDARY: Zero response is established only for the existing periodic harmonic gauge-wave negative control. It is not a physical radiative-wave extraction, detector prediction, UET validation, parent closure, or Gravity unlock.

## Boundary Characteristic Preflight (2026-09-25)

The result `CORE_CURVED_3P1_GH_BOUNDARY_CHARACTERISTIC_CLASSIFICATION` is
`CLOSED_FOR_LANE` for the implemented five-field, one-metric-component,
local-orthonormal frozen principal block only. It checks
`u0=psi`, `u1pm=Pi +/- Phi_n - gamma2*psi`, and `u2_A=Phi_A` with speeds
`0`, `-beta_n +/- alpha`, and `-beta_n`. The additional `u2_A` fields are
incoming when the outward normal shift is positive; at zero shift they are
glancing. The exact sonic cases are classified as outside the strict
`|beta_n| < alpha` reference domain.

For the 12 subluminal controls, the audit zeroes incoming characteristic
amplitudes and checks the sign of `F_n = 0.5 U^T S A_n U`. This is a
frozen-principal energy-flux check, not a boundary operator. Constraint,
physical incoming-radiation, and gauge conditions remain unimplemented, as
do non-periodic SBP/SAT evolution, discrete stability, boundary convergence,
and dimensional observables. In this GH notation `Phi_iab` is a spatial
derivative variable and is not UET's effective-response `Phi`; UET `C`,
`R_gen`, and `R_obs` are not added to the GH state.

The literature basis is intentionally bounded: Rinne analyzes the GH
constraint/physical/gauge boundary decomposition and frozen-coefficient
Fourier-Laplace boundary stability in the subluminal normal-shift regime;
this audit does not claim that result for its own discretization or as a
fully nonlinear well-posedness proof. Calabrese and Sarbach show why
constraint-consistent or zero-incoming-constraint prescriptions alone do not
ensure well-posedness for arbitrary formulation parameters.

## Sources

- C. Gundlach and J. M. Martin-Garcia, *Well-posedness of formulations of the Einstein equations with dynamical lapse and shift conditions*, arXiv:gr-qc/0604035, DOI: 10.1103/PhysRevD.74.024016.
- L. Lindblom et al., *A New Generalized Harmonic Evolution System*, arXiv:gr-qc/0512093, DOI: 10.1088/0264-9381/23/16/S09.
- O. Rinne, *Stable radiation-controlling boundary conditions for the generalized harmonic Einstein equations*, arXiv:gr-qc/0606053, DOI: 10.1088/0264-9381/23/22/013.
- G. Calabrese and O. Sarbach, *Detecting ill posed boundary conditions in General Relativity*, arXiv:gr-qc/0303040, DOI: 10.1063/1.1599056.

## Linear TT SBP-SAT Boundary Pilot (2026-09-25)

CORE_CURVED_3P1_GH_LINEAR_TT_SBP_SAT_BOUNDARY_PILOT is CLOSED_FOR_LANE for the two physical transverse-traceless polarizations of standard linearized GR on a finite, non-periodic one-dimensional slab. The Legendre-Gauss-Lobatto diagonal-norm SBP operator and a weak SAT penalty enforce homogeneous no-incoming characteristic data at both faces. This is a bounded physical-sector pilot, not the first-order ten-component GH system and not the full differential constraint-preserving boundary condition (CPBC) construction of [Rinne 2006](https://arxiv.org/abs/gr-qc/0606053).

For each polarization A, the evolved state is Pi_A=-partial_t h_A and G_A=partial_x h_A, with partial_t h_A=-Pi_A, partial_t Pi_A=-D G_A-H^-1 e_L(Pi_A+G_A)_L-H^-1 e_R(Pi_A-G_A)_R, and partial_t G_A=-D Pi_A. The semidiscrete energy E=1/2 sum_A(Pi_A^T H Pi_A+G_A^T H G_A) obeys dE/dt=-sum_A(Pi_A,L^2+Pi_A,R^2)<=0; the reduction constraint D h_A-G_A=0 is invariant under the semidiscrete evolution. The state contains no UET C, Phi, Pi, R_gen, or R_obs; no UET equation or ontology was changed.

The independent left/right packet controls both leave only roundoff-scale energy: final-to-initial ratios 9.51e-31 and 8.11e-31. The maximum SBP residual is 1.43e-12, maximum semidiscrete energy-identity residual is 5.38e-12, the final reduction-constraint residuals are below 4.26e-12, and the RK4 temporal refinement ratio is 15.71 (fourth-order target interval [10,22]). The source-hashed evidence is docs/core/07_artifacts/verification/curved_3p1_gh_tt_sbp_sat_boundary_pilot.json (SHA-256 9827276BE2A1BA34E6A16D391291FF988B1941925003850B89FFBACAFC384012).

The Core parent gate registers this only as PASS_DIAGNOSTIC_ONLY and preserves the controlling blocker curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing. The parent remains PARTIAL; no dependency is unlocked and Gravity remains blocked. Full ten-component GH constraint/physical/gauge boundary conditions, positive-shift incoming u2_A, discrete subsidiary-constraint propagation, variable coefficients, nonlinear evolution, corners, matter boundaries, and dimensional observables remain open. The related SBP-SAT GH construction of [Dailey et al.](https://arxiv.org/abs/2409.17970) changes the evolved formulation and boundary contract, so it is treated as a method comparator, not a drop-in implementation of Rinne's differential CPBC for this branch.

The next bounded result has been attempted as a frozen-background, full ten-component incoming `u1_minus` slab pilot. Its 4+2+4 algebra and Rinne-residual cross-check pass, but the pointwise implementation fails the declared pulse-energy and reduction-constraint limits, while the constraint-compatible lift is spectrally unstable. A separate second-order algebraic reduced-wave comparator preserves `Phi_x=D(psi)` but remains partial because absorption and high-resolution spectral screens are unresolved. See the [full-u1 pilot](../07_artifacts/verification/curved_3p1_gh_full_u1_cpbc_slab_pilot.json) and [reduced-wave comparator](../07_artifacts/verification/curved_3p1_gh_reduced_wave_boundary_comparator.json).

## Reduced-TT SBP-SAT Energy Comparator (2026-09-25)

`CORE_CURVED_3P1_GH_REDUCED_TT_SBP_SAT_COMPARATOR` is `CLOSED_FOR_LANE` for a separate standard-linearized-GR TT-sector control. It evolves `(h_A, Pi_A)` and reconstructs `G_A=D(h_A)` algebraically, with

```text
h_dot_A = -Pi_A
Pi_dot_A = -D G_A - H^-1 e_L (Pi_A+G_A)_L - H^-1 e_R (Pi_A-G_A)_R
E = 1/2 sum_A (Pi_A^T H Pi_A + G_A^T H G_A)
dE/dt = -sum_A (Pi_A,L^2 + Pi_A,R^2) <= 0
```

The derived second-order RHS matches the existing first-order TT SBP-SAT RHS exactly on `G_A=D(h_A)` (residual `0`). At degree 72 the LGL-SBP identity residual is `1.4243e-12`; the measured energy-rate difference is accounted for by the independently computed floating-point SBP defect, leaving decomposition residual `6.4790e-13` under the unchanged `2e-11` tolerance. The maximum normalized SAT energy growth screen is `3.0166e-10`; right/left packet final-to-initial energy ratios are `1.223e-29` and `1.568e-29`; the RK4 temporal refinement ratio is `13.96`.

This provides a concrete energy-stable TT comparator and shows that the tested pointwise strong differentiated-target replacement has positive energy-growth directions on both LGL-SBP and Chebyshev/Clenshaw-Curtis norms. It does **not** close the full first-order GH CPBC: constraint and gauge sectors, positive-shift `u2_A`, tangential derivatives, corners, variable coefficients, nonlinear evolution, and spatial/continuum convergence remain open. No UET symbol, ontology, parent requirement, downstream dependency, or claim promotion changes. See the [source-hashed comparator artifact](../07_artifacts/verification/curved_3p1_gh_reduced_wave_sbp_sat_comparator.json).

## Full U1 Boundary Pilot and Reduced-Wave Comparator (2026-09-25)

MAJOR_RESULT_CLOSURE: `CORE_CURVED_3P1_GH_FULL_U1_CHEBYSHEV_SLAB_PILOT / PARTIAL`; separate `CORE_CURVED_3P1_GH_REDUCED_WAVE_BOUNDARY_COMPARATOR / PARTIAL`.

WHAT_IS_ACTUALLY_CLOSED: The full ten-component incoming `u1_minus` tensor maps into the source-defined 4+2+4 constraint/physical/gauge sectors, and the normal-incidence RHS target agrees with the independent Rinne residual evaluator to `4.27e-14`. In the separate reduced formulation, `Phi_x=D(psi)` is enforced algebraically, the pulse reduction residual is `1.53e-14`, and the degree-8 spectrum and random-perturbation screens pass.

WHAT_REMAINS_OPEN: The full first-order pointwise scheme has a Clenshaw-Curtis TT energy ratio `0.2131 > 0.05` and reduction residual `3.55e-3 > 2e-6`. The cubic compatible lift preserves reduction (`9.60e-10`) but has 59 resolved growing modes and perturbation growth `2.72e6`. The reduced-wave comparator's degree-12 integrated-energy remainder is `0.155 > 0.05`; exploratory degrees 8, 12, 14, 16, 18, and 20 are non-monotone, and degree 20 has one eigenvalue `1.3873e-6` above the unchanged `1e-6` tolerance. Spatial convergence and a semidiscrete energy estimate remain unestablished.

DEPENDENCY_UNLOCKED: None. The curved 3+1 parent remains `PARTIAL`; Gravity remains blocked.

STATUS: `FAIL_GH_FULL_U1_CHEBYSHEV_SLAB_PILOT`; reduced-wave comparator `PARTIAL_REDUCED_WAVE_BOUNDARY_COMPARATOR`; `claim_promotion=false`.

WHAT_CHANGED: Added the full-u1 slab audit, source-hashed pilot artifact, a separate reduced-wave comparator artifact, Clenshaw-Curtis integrated-energy reporting, and a fixed-threshold resolution sensitivity sweep. No UET ontology, periodic GH evolution, or parent dependency was changed.

EQUATION_OR_MAPPING: `q_ab=Pi_ab-n*Phi_xab-gamma2*psi_ab`; the projected incoming RHS is split by ranks 4+2+4. Comparator-only reduction sets `Phi_xab=D(psi_ab)` and evolves `(psi_ab,Pi_ab)`; it is not the independent-variable first-order GH system.

VERIFICATION: Projector ranks and algebra pass with maximum residual `2.78e-16`; target and Rinne cross-check maxima are `1.80e-14` and `4.27e-14`. The pointwise scheme has no resolved positive eigenvalue above `1e-6`, its random-noise growth is `4.14`, but the pulse and reduction gates fail. The compatible lift fails spectrum/noise gates. Reduced comparator degree-12 noise growth is `1.0046`, reduction residual `1.53e-14`, and weighted pulse remainder `0.155`; at degrees 18/20 the remainders are `0.0337/0.0199`, but degree 20 has one mode above the locked eigenvalue tolerance. RK4 refinement ratio is `10.86`. Thresholds were not changed.

CONTROLLING_BLOCKER: `full_first_order_gh_boundary_evolution_stability_and_reduction_constraint_closure`.

NEXT_ACTION: Derive a discrete energy estimate for the algebraic reduced-wave boundary condition and independently resolve the near-zero high-order eigenvalue behavior without relaxing the `1e-6` screen. Require spatial convergence of the integrated pulse energy before classifying that comparator beyond `PARTIAL`; keep full first-order GH, positive-shift `u2_A`, corners, and subsidiary-constraint evolution as separate blockers.

CLAIM_BOUNDARY: Standard-GR frozen-background numerical diagnostics only. The reduced-wave comparator is not full GH CPBC, a continuum/IBVP proof, a UET prediction, Gravity compatibility, Core-parent closure, or global UET closure.

## Constraint/Physical/Gauge Projector Decomposition (2026-09-25)

MAJOR_RESULT_CLOSURE: `CORE_CURVED_3P1_GH_BOUNDARY_PROJECTOR_DECOMPOSITION / CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: In the local orthonormal GH frame, the incoming symmetric tensor `u1^-_{ab}` is split by the source-defined constraint, physical-radiation, and gauge projectors. The verified ranks are 4, 2, and 4, respectively; the maps are idempotent, complete, and pairwise annihilating. The physical component is transverse to the time/face normals and trace-free on the two-surface.

WHAT_REMAINS_OPEN: Source-matched linearized/frozen-background differential residual evaluators now exist, but they are not applied to an evolution scheme. Nonlinear variable-coefficient boundary conditions, SBP/SAT enforcement, discrete boundary stability/convergence, corner compatibility, self-consistent matter-boundary behavior, and dimensional observables remain open. The `u2_A` definition-curl residual is implemented for positive normal shift, but its full subsidiary-constraint propagation has not been established.

DEPENDENCY_UNLOCKED: Projector/decomposition design only. The curved 3+1 parent stays `PARTIAL`; Gravity remains blocked.

STATUS: `PASS_GH_BOUNDARY_PROJECTOR_DECOMPOSITION`; `claim_promotion=false`.

WHAT_CHANGED: Added and audited the finite-dimensional GH projector maps on symmetric spacetime two-tensors. The existing periodic solver was not modified.

EQUATION_OR_MAPPING:

- `P_G = I - P_C - P_P`.
- For `-alpha < beta_n <= 0`, the incoming evolution tensor `u1^-` splits as `u1^- = P_C u1^- + P_P u1^- + P_G u1^-` with dimensions `4 + 2 + 4 = 10`.
- `P_C u1^-` and `P_P u1^-` are fixed through differential constraint and Weyl/`Psi_0` conditions; `P_G u1^-` receives gauge data.
- If `beta_n > 0`, additional `u2_A` fields are incoming and require their own constraint-compatible boundary treatment.

VERIFICATION: 26 normalized cube directions; 8 deterministic symmetric-tensor inputs per direction; ranks 4/2/4; maximum projector residual `3.3306690738754696e-16`; reconstruction, pairwise annihilation, physical transversality, and physical trace checks passed. Focused tests: 28 passed. Evidence: `docs/core/07_artifacts/verification/curved_3p1_gh_boundary_projector_audit.json`, SHA-256 `1648BC84C8D47FB8701D7573B0B5E13A953643FA2B64F72B3297D54726C27C29`.

CONTROLLING_BLOCKER: `curved_3p1_constraint_preserving_boundaries_and_dimensional_observable_mapping_missing`.

NEXT_ACTION: Build a non-periodic SBP/SAT or equivalently justified initial-boundary discretization that applies the source-matched residuals. Verify the discrete subsidiary-constraint energy estimate, incoming-radiation control, stability, spatial/temporal convergence, and edge/corner compatibility before linking this module to nonlinear GH time evolution.

CLAIM_BOUNDARY: This verifies projector algebra only. Rinne's boundary-stability analysis is formulation- and assumption-specific, and the repo does not inherit it without its own boundary operator, constraint subsystem, and discrete stability tests ([Rinne 2006](https://arxiv.org/abs/gr-qc/0606053)). Constraint-consistent simplifications can still be ill-posed for unsuitable formulation parameters ([Calabrese & Sarbach 2003](https://arxiv.org/abs/gr-qc/0303040)).

## Linear Differential Boundary Residuals (2026-09-25)

`CORE_CURVED_3P1_GH_LINEAR_DIFFERENTIAL_BOUNDARY_RESIDUALS` is
`CLOSED_FOR_LANE` for source-matched residual evaluation on linear perturbations
about a Minkowski local orthonormal frame. The implementation evaluates the
incoming subsidiary-constraint condition, Weyl/`Psi_0` condition, algebraic
gauge data, and the incoming `u2_A` definition-curl condition for positive
normal shift. The four- and two-component normal-derivative maps annihilate the
complementary source-defined projectors.

The audit checks 26 face normals, prescribed physical/gauge data, a symmetric
mixed-derivative control, and the source equations by a separate literal-index
reference test. Units are geometric: `delta_psi` is dimensionless, `Pi` and
`Phi_iab` are `L^-1`, and the differential residuals are `L^-2`.

The incoming-condition count closes at the symbol level: for
`-alpha < beta_n <= 0`, ten `u1_minus` modes match four constraint and two
physical differential conditions plus four gauge data. For
`0 < beta_n < alpha`, the additional twenty `u2_A` modes are controlled by a
rank-20 normal-derivative map from the Eq. (29) definition-curl residual.

This result does not impose boundary conditions on the periodic solver. There is
no nonlinear variable-coefficient boundary operator, non-periodic SBP/SAT
evolution, boundary energy estimate, stability/convergence result, or
edge/corner analysis. Therefore the parent remains `PARTIAL` and Gravity remains
blocked. See `docs/core/07_artifacts/verification/curved_3p1_gh_linear_boundary_residual_audit.json`.

## Full-U1 Maximally Dissipative SAT Control (2026-09-25)

`CORE_CURVED_3P1_GH_MAX_DISSIPATIVE_SAT_CONTROL` is `CLOSED_FOR_LANE` for a
separate, full ten-component, zero-shift GH control using direct homogeneous
incoming-characteristic data. With the positive packed-tensor Frobenius metric
(`1` on diagonal tensor entries and `2` on off-diagonal entries), the 4+2+4
constraint/physical/gauge projectors are self-adjoint and mutually orthogonal
on the audited 26 face normals.

The weak penalty acts only on the `Pi_ab` RHS:
`Pi_dot=-D(Phi)-H^-1 e_L q_L-H^-1 e_R q_R`, where
`q=Pi-n*Phi_n-gamma2*psi`. The SBP energy balance is not falsely required to be
monotone: its exact form includes the GH lower-order contribution
`R_lower=sum_j w_j[-lambda^2<psi,Pi>+gamma2||Pi||^2-gamma2||Phi||^2]`
and endpoint dissipation `-sum_faces||Pi-gamma2*psi||^2`. For the declared
`gamma2=0.7`, `lambda=2`, the independently bounded growth constant is
`dE/dt <= 2.1351 E - boundary_dissipation`, independent of the tested LGL
order. The definition constraint obeys `C_dot=-gamma2*C` exactly.

The audit passes LGL orders 4, 8, and 12: maximum SBP residual
`4.69e-14`, energy-identity residual `2.07e-13`, reduction-identity residual
`1.43e-14`, and no eigenvalue above the unchanged `1e-6` growth tolerance.
The frozen strong-Rinne method comparison also fails on the tested LGL orders
8/12/16: pulse-energy ratios are `3.529/1.267/1.833`, reduction-constraint
residuals are `0.249/0.384/0.00404`, and orders 12/16 have eight resolved
positive modes. This finite-grid result shows that changing the grid alone did
not rescue the tested strong replacement; it is not a continuum no-go. The SAT
control does not impose the differential constraint or Weyl/`Psi_0` conditions
and adds no dependency-unlock edge. Existing parent-work authorization is
unchanged; the actual curved 3+1 parent remains `PARTIAL`, and Gravity remains
blocked. See `docs/core/07_artifacts/verification/curved_3p1_gh_full_u1_max_diss_sat_control.json`.
