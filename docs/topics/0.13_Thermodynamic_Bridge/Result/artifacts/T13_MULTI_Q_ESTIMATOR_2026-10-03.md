# Three-Node Estimator, Covariance And Conditional Error Budget

MAJOR_RESULT_CLOSURE: T13_MULTI_Q_ESTIMATOR_COVARIANCE_AND_TREE_BIAS_BUDGET; CLOSED_FOR_LANE for the declared tree witnesses, not physical measurement design or Full Topic13.

WHAT_IS_ACTUALLY_CLOSED: Explicit three-node dispersion coefficient estimation, exact common-axis invariance, the joint energy/momentum/native-input differential, and a replayable sufficient rational tree-bias plus bounded-energy-error requirement. All ten preregistered windows remain, including an invalid inverse and six noncertified budgets.

WHAT_REMAINS_OPEN: Permitted same-state physical peak data, detector resolution and joint covariance, Noether-to-particle/current/action mapping, native-state and interaction/finite-temperature error, independent thermal gain/alpha, heat/entropy/Kubo/SK-KMS and nonlinear parent. A coefficient estimator is not a complete experiment.

DEPENDENCY_UNLOCKED: Instrument-input and alternative independent-scale feasibility research only. G2-G4/R1-R5/Goal, Core-owner composition and physical/global unlock remain unchanged.

STATUS: PASS_SCOPED_MULTI_Q_ESTIMATOR, seven method checks. Artifact [t13_multi_q_estimator.json](t13_multi_q_estimator.json), SHA256 `56c9aa7ef469c51a30337bea9ea958c8d2459ed7e2316fbbe49644ad192c57b1`.

WHAT_CHANGED: New topic-local estimator, tests, registry and artifact. The pinned q5 predecessor, original source-work FAIL/first failure, old conserved-C branch and Core actions are not edited. No acquired physical inputs or external parameter fitting; linear coefficient interpolation is explicitly an estimator, not physical calibration.

EQUATION_OR_MAPPING: For positive distinct momenta, x_i=q_i^2 and f_i=E_i/q_i. Let beta=(c,eta,zeta) for E=cq+eta*q^3+zeta*q^5+O(q^7). For the other two indices j,l:

```text
W_2i = 1/[(x_i-x_j)(x_i-x_l)]
W_1i = -(x_j+x_l) W_2i
W_0i = x_j x_l W_2i
beta_hat_k = sum_i W_ki f_i
sum_i W_ki x_i^j = delta_kj
```

The identity is exact for the truncated polynomial, not for the full tree curve. An independently implemented Newton divided difference checks the same estimator at 70/100 digits. Natural-lane units: c dimensionless, eta:E^-2, zeta:E^-4, I:E^-2. Native Phi:E is not normalized Phi/Kelvin. The quintic coefficient is not collective C.

## Joint Differential And Correlation

At the observed three-node interpolant, differentiating W(x)f gives:

```text
J_beta,logE_i = W_i f_i
J_beta,logq_i = W_i [-f_i-2*x_i*(beta_hat_1+2*beta_hat_2*x_i)]
Sigma_beta = J_beta Sigma_log(E,q) J_beta^T
r = beta_hat_0 beta_hat_2 / beta_hat_1^2
grad_beta r = (beta_hat_2/beta_hat_1^2,
               -2*beta_hat_0*beta_hat_2/beta_hat_1^3,
               beta_hat_0/beta_hat_1^2)
```

If all energies change by a common multiplicative factor, beta scales uniformly. If all q change by a common factor a at fixed energies, beta_k scales as a^(-1-2k). Thus r is exactly invariant under either axis scaling, not just to first order. The coefficient covariance is not zero. Rank-one common-axis covariance controls cancel in r; decorrelated shape errors do not. Resolution distortions, state error and calibration ancestry are not common-axis symmetries.

For the predecessor's known-native, strict positive kinetic class:

```text
r = r0-D*[I/(1+sI)]^2, f=1+sI
dI/dr = -f^3/(2*D*I)
g_data = (dI/dr) grad_log(E,q) r
g_native = (-(dI/dr)*r0, -I*f/2, s*I^2)
Var(I) = g_full^T Sigma_full g_full
```

Native input order is log(-r0), log(D), log(s), following the six log(E,q) inputs. These three functions of native parameters need not be statistically independent. Sigma_full must include their correlations with each other and with data. The covariance formula is a local first-order propagation; nonlinear/systematic bounds remain a separate obligation. No diagonal or measured covariance is assumed. Outside the strict inverse domain, I and its propagated gradient are undefined, not clipped to zero.

## Exact Sufficient Energy-Only Bound

The q5 predecessor supplies exact rational coefficient witnesses and B_i >= |E_tree_i-E5_i|/(c*q_i). Set P_i=1+h*x_i+j*x_i^2, u=(1,h,j). For exact q, fixed native inputs and relative energy errors |delta E_i/E_tree_i|<=epsilon:

```text
T_k = sum_i |W_ki| B_i
N_k = sum_i |W_ki| (P_i+B_i)
|beta_hat_k/c-u_k| <= T_k+epsilon*N_k
```

This follows by the triangle inequality and |E_tree_i/(c*q_i)|<=P_i+B_i in the declared positive-energy domain. Let L=u-radius and U=u+radius. If L0>0, L1>0, U2<0, the independent component box implies:

```text
r_lower = U0*L2/L1^2
r_upper = L0*U2/U1^2
r(I_true*(1+rho)) <= r_lower <= r_upper <= r(I_true*(1-rho))
```

The outer inequalities certify |I_hat/I_true-1|<=rho. Here rho=0.01 is an illustrative design target locked before the audit, not an empirical gate. Rational arithmetic decides the certificate; float displays do not. Ninety-six dyadic steps give a certified lower epsilon and noncertified upper separated by 2^-96 where zero-noise certification exists. The box is conservative, ignores correlations between coefficient errors and is not the optimal measurement budget. If zero noise is not certified, the displayed zero budget means no positive budget is certified by this box, not that the true instrument must have zero noise or that inference is physically impossible.

The exact certificate is for rationalized tree coefficients, not a proof of the physical EOS, continuum theory or full-action approximation error. Rounded 80-digit roots are numerical controls against the analytic box, not exact experimental energies.

VERIFICATION: Seven artifact checks pass. Exact interpolation/common-axis identities, independent Newton recovery, tree-box containment, central log finite differences for all six data and three native inputs, exact correlated null controls, rational endpoint replay and eight energy corners per positive budget checked. Maximum ratio-gradient relative disagreement 2.347e-35; native-gradient disagreement 1.999e-43. Frozen two mu/five q maxima/three ratios/80-digit roots/70-100-digit estimators/FD1e-24/96 steps retained. Estimator tolerance1e-45 and Jacobian1e-8 unchanged; original causal1e-6 not rerun or promoted. Runtime Path-read allowlist checks the declared audit path only, not pristine historical blindness. Exact decimal encoding is size-bounded without changing Python's global integer limit. Linked test count is recorded in UPDATE_LOG after the final integration run.

CONTROLLING_BLOCKER: physical_peak_resolution_joint_covariance_native_state_and_interaction_error_not_admitted. The original source-work aggregate remains PARTIAL/FAIL and broad thermal closure remains open.

NEXT_ACTION: Before the existing 7 October freeze, compare the q5 extraction route with the conditional independent-scale/q3 route using documented resolution and native inputs. Produce a feasibility or exact-input-gap decision, not another unchanged grid. If resolution is unavailable, retain a conditional requirement in the portfolio and make the acquisition an explicit funded aim.

CLAIM_BOUNDARY: Restricted derived estimator/error requirement only. No physical noise assigned, q5 measured, material/temperature calibration, gain identification, interaction/heat/transport/KMS or Full Topic13/Core/global/Goal acceptance. No source replacement, fitting of physical parameters, clipping, padding, threshold/ontology/owner changes or numeric Xie read. Prior Xie context exposure remains REVIEW_REQUIRED. C is not charge/mass, pi_phase is not UET Pi, and R_gen/R_obs are excluded from dynamical state. Model trial remains NOT_RUN/settings unchanged; funder/PI/budget/deadline unknown and next funding round is a scenario.
