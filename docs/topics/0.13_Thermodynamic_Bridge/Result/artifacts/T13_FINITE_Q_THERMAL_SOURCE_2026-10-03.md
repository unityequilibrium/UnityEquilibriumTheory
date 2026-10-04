# Finite-q source response recovers static population without a fitted relaxation time

MAJOR_RESULT_CLOSURE: `T13_FINITE_Q_THERMAL_SOURCE_AND_STATIC_POPULATION_LIMIT`, `CLOSED_FOR_LANE` in the named acoustic thermal-insertion prescription. Not Full Topic13/R1/Goal closure.

WHAT_IS_ACTUALLY_CLOSED: An explicit finite-q thermal action-source kernel, checked with a two-momentum real-time cross-covariance calculation, and the static Bose-population term that connects its equilibrium limit to the same-action pressure target.

WHAT_REMAINS_OPEN: Collisionless low-frequency/long-wavelength limits, full loop-current Ward and energy balance, collision/relaxation physics, full vacuum/interacting thermal matching/approximation control and independent material/source/readout/scale/uncertainty. Physical Kubo/SK-KMS remains open.

DEPENDENCY_UNLOCKED: Collisionless current/energy and thermal-source mapping research only. No physical/Core/Gravity/owner-composition admission.

STATUS: `PASS_SCOPED_FINITE_Q_THERMAL_SOURCE`. [Artifact](t13_finite_q_thermal_source.json), SHA-256 `a1583b3ef2ec12929078800a6c1ee18f10d0fe4243957206febd4098363c0a57`.

WHAT_CHANGED: Separate [finite-q calculation](../../Code/03_Research/Research_T13_Finite_Q_Thermal_Source.py), [exact mode quadrature](../../Code/03_Research/Research_T13_Thermal_Mode_Quadrature.py), tests and [registry](../../Data/03_Research/t13_finite_q_thermal_source_registry.json). The parent action and [virtual/source predecessor](T13_THERMAL_VIRTUAL_RESPONSE_2026-10-03.md) remain unchanged. The branch is still `t13.candidate.acoustic_thermal_insertion_tree_virtual_response_v1`, not a new physical theory or quantum-heavy admission.

EQUATION_OR_MAPPING:

## 1. Two momenta require two initial thermal covariances

For external q, let r=abs(p_vector+q_vector). In the rest frame the
first-order tree generators A_p/A_r and acoustic covariances Cov_p/Cov_r
are those of the predecessor. The perturbation delta_A_j comes from the
same cubic potential derivative T_j, not a new fitted source operator:

```text
(-iz-L_Ar,Ap) delta_Cov_j=delta_A_j Cov_p+Cov_r delta_A_j^T
L_Ar,Ap X=A_r X+X A_p^T
B_ij(z;p,r)=-Tr(T_i delta_Cov_j,xx)/2
```

This 36-component cross-covariance solve is independent of the propagator
method. Both thermal populations are required, even if only one is large.
The physical triangles checked are (p,r,q)=(.005,.011,.008),(.02,.031,.02),
(.04,.037,.02), at T=.004 in each of the two declared mu states.

The equivalent spectral insertion is

```text
I_ij(p,r;z)=[u_p^dag T_i G(E_p+z,r) T_j u_p
            +u_p^dag T_j G(E_p-z,r) T_i u_p]/(2E_p)
B(z;p,r)=[n(E_p) I(p,r;z)+n(E_r) I(r,p;z)]/2
```

Only acoustic modes carry thermal population. All tree poles in G are
virtual propagation, not independently occupied/quantized heavy loops.
After translation of the infinite isotropic integration variable, the
integrated bubble can use one acoustic insertion n(E_p)I(p,r;z). The
implemented finite thermal tails are convergence diagnostics, not a proof
of exact equality of differently truncated domains or an infinite-tail bound.

## 2. External source dressing and contact remain action-derived

```text
d(z,q)=D(z,q)^-1 e_Phi
delta_chi(z,q)=d(-z,q)^T [integral B(z,q)-integral n M(p)] d(z,q)
M=S+T delta_x
```

S and the homogeneous thermal background shift delta_x are the same
quartic/tadpole terms derived in the predecessor. No new local contact,
pole width, relaxation time or amplitude is fitted. Non-real frequency
evaluation is not physical broadening. Source h E3 and susceptibility
E^-2 belong to the declared natural-energy lane, not SI heat or Kelvin.

The phase row of the tree source equation gives

```text
delta_n_tree=2mu d_sigma-iz d_phase
-iz delta_n_tree+q^2 d_phase=0
```

This verifies tree charge continuity, not the full loop-corrected current
operator or dissipative energy ledger. The latter are explicitly false/open
in the artifact. C, UET Pi, R_gen and R_obs are excluded from the covariance
state; velocities here do not redefine the UET state ontology.

## 3. Static spectral resolution produces the population term

At z=0 use the real static source vertex A(q)=T_i d_i(0,q). Between
tree modes define P_ij=u_i(p)^T A(q)u_j(r) and
N_ij=u_i(p)^dag A(q)u_j(r). For n_i=acoustic Bose population and n_i=0
for virtual nonacoustic modes, the source-projected static bubble is

```text
B_static=sum_ij [(n_i(p)+n_j(r)) abs(P_ij)^2/(4E_i E_j(E_i+E_j))
                +(n_i(p)-n_j(r)) abs(N_ij)^2/(4E_i E_j(E_j-E_i))]
```

The acoustic-acoustic number term has a removable diagonal limit:

```text
[n(E_p)-n(E_r)]/(E_r-E_p) -> n(E)(1+n(E))/T
u_a^dag D_h u_a=2E E_h
number_diagonal=n(1+n) E_h^2/T
```

The stable divided difference is evaluated symmetrically with expm1 and
its exact zero-width limit, not a numerical energy floor or clipping.
Thus equilibrium population variance is recovered from finite-q spectral
response without inventing a relaxation coefficient. At precisely q=0 and
nonzero frequency, homogeneous populations remain conserved; substituting
this static variance into that dynamical response would still be wrong.

The static radial equation fixes A_phase,phase=-q^2 d_sigma/sqrt(s).
Using that exact identity avoids subtracting larger source terms to recover
the tiny phase entry. It neither repairs a mass nor changes the action.

## 4. Integrated static limit and numerical boundaries

Let p_T=T/c. At q/p_T=1/16,1/32,1/64, static source response approaches
the independently computed acoustic pressure Hessian. Normalized
target discrepancies at the finest q are:

| mu | T divisor256 | T divisor512 |
| --- | --- | --- |
| 1.05 | 2.40343e-5 | 2.39952e-5 |
| 1.2 | 7.87706e-6 | 7.86327e-6 |

The errors decrease at both preceding q refinements. Direct q=0 static
resolution agrees within4.961e-12. These are finite-q diagnostic fractions,
not physical material errors or a measured temperature accuracy.
The analytic diagonal identity and these integral checks do not establish
the whole z/q collisionless limit, global continuum proof or approximation
remainder. They do establish that the old static population term is not
missing because a fitted collision time was omitted.

## 5. Exact batching, not a smaller verification grid

The initial scalar-only audit was intentionally stopped before producing a
completed artifact, after independently checking a batched replacement.
The process was confirmed live and identified by its script before stopping;
it was not treated as failed/dead merely because an observation timed out.
That interrupted attempt supplies neither a PASS nor a numerical FAIL.

The replacement computes the same Schur acoustic root, companion heavy
poles and symplectic polarizations for multiple angles together. Small
acoustic energies are not taken from an ill-conditioned companion eigenvalue.
Pointwise channels agree with the retained scalar method to1.114e-15 on
the declared comparison momenta. Angular inverses also have a direct-loop
regression check. All original q/T/mu/resolution/tail/gate values remain.

The p=q integration breakpoint isolates an integrable soft-momentum corner;
it is quadrature partitioning of the same domain, not cone padding or a
filter. No singular region is removed or replaced with invented data.
Finite-tail/refinement agreement is not a full analytic/physical error bound.

VERIFICATION: Six artifact checks; mu1.05/1.2, T=c*dispersion_scale/256 and /512, radial orders24/48/96, angular32/64/128, tails32/40. Static q/p_T1/16,1/32,1/64; dynamic q.01/.005/.0025 and z=.02i/.05i/.03+.02i. Cross-covariance matrix error<7.278e-16, source projection<6.261e-16 and tree continuity<3.365e-15; largest joint quadrature difference4.135e-8 and finite-tail4.338e-10. Tests cover batched/scalar modes, angular geometry, exact Bose limit, static source equation, q0 predecessor recovery, zero-T/decoupling/coordinate/invalid domain, protected hashes and audit-time Path reads. Fixed identity1e-9/covariance1e-7/quadrature1e-6/tail1e-8 unchanged; new static soft-limit diagnostic1e-3 declared before the first attempt, not an old physical-gate override. Original conserved-C leakage gate remains1e-6 and is not rerun/passed here. Final linked count is in UPDATE_LOG.

CONTROLLING_BLOCKER: `collisionless_soft_limit_full_interacting_matching_and_physical_transport_open`.

NEXT_ACTION: Derive the loop-current/energy Ward interface and the collisionless soft-frequency limit from this kernel, then connect an actual heat-source/readout operator and independent material scale. Collision/transport inputs must be derived, microscopically matched or explicitly external, not assigned from static variance. Complete interacting/vacuum/approximation obligations. Preserve7/11 October and full Goal/R1-R5 criteria.

CLAIM_BOUNDARY: Named acoustic-populated Gaussian rest-frame response only, not full EOS, collision operator, physical Kubo/SK-KMS/heat conductivity/calibration, original conserved-C repair or Full Topic13/UET/Core promotion. No holdout numeric read; prior exposure REVIEW_REQUIRED. No parameter fit, fabricated data, assigned relaxation/width, clipping/padding/filter, threshold/ontology/owner change. [Morgan's collisionless response study](https://arxiv.org/abs/cond-mat/0307246) explicitly treats external driving of the thermal component; [Hiyane-Watabe-Nikuni](https://arxiv.org/abs/2310.01988) studies the hydrodynamic/collisionless crossover with kinetic equations. They motivate keeping source and collision regimes distinct, not transferring their coefficients/validation to this candidate or claiming this standard response machinery is novel.
