# Cyclic source work is computable without supplying a heat or entropy map

MAJOR_RESULT_CLOSURE: `T13_GAUSSIAN_CYCLIC_SOURCE_WORK_AND_ENTROPY_BOUNDARY`, `PARTIAL`. Two subordinate identities are `CLOSED_FOR_LANE`; the preregistered finite-amplitude/binary64 work audit remains FAIL. No Full Topic13/R1/Goal acceptance.

WHAT_IS_ACTUALLY_CLOSED: The zero-amplitude work coefficient from forced time-domain Liouvillian convolution agrees with independent stimulated modal transitions. Finite Hamiltonian flow preserves the Poisson form/volume and a conditional full-rank Gaussian entropy difference. Neither result supplies irreversible heat or primary-state entropy.

WHAT_REMAINS_OPEN: The frozen finite-amplitude work grid does not reach the leading-work limit, and binary64 subtraction does not resolve its small coefficient. Full interacting/vacuum approximation, physical heat/readout/scale, collisions and SK/KMS entropy/transport remain open.

DEPENDENCY_UNLOCKED: None for physical/Core/Gravity/portfolio acceptance. The verified identities are preliminary methods evidence only.

STATUS: `FAIL_SCOPED_GAUSSIAN_SOURCE_WORK`, aggregate `PARTIAL`. [Final artifact](t13_gaussian_source_work.json), SHA-256 `959441d2940f0aa209d72b8f8671d440807dd14ae9a80aff4357606f3bce4c62`, controls the numerical record. [First failure](t13_gaussian_source_work_first_failure.json), SHA-256 `0c8c828f512f0a70653d30c15c4b0f1e7d960fb878712c774ae298dd038f35f4`, is retained, not relabelled by the extended calculation.

WHAT_CHANGED: Separate [calculation](../../Code/03_Research/Research_T13_Gaussian_Source_Work.py), [tests](../../Code/03_Research/test_t13_gaussian_source_work.py) and [registry](../../Data/03_Research/t13_gaussian_source_work_registry.json). The [collisionless predecessor](T13_COLLISIONLESS_SOFT_SOURCE_2026-10-03.md), Noether/FQ modules and Core-owner action are unchanged.

EQUATION_OR_MAPPING:

## 1. A compact pulse with a Phi-only action source

For f=sin^8(pi*t/L)cos(Omega*t) on (0,L), extended by zero, its first
seven endpoint derivatives vanish. This is declared source support, not
clipping a physical trajectory. In the rest h0=0 branch, set U=2u*s,
v=sqrt(s), K_Phi=epsilon*Z_Phi and G=(i*L_tree).real:

```text
b_pi = amplitude*f'
b_sigma = -amplitude*(f''+q^2*f)/(2*mu)
b_Phi = -amplitude*[f''''+(U+2q^2+4mu^2)f''+q^2(U+q^2)f]/(2mu*g*v)
h = K_Phi*b_Phi''+(V_curvature+K_Phi*q^2)b_Phi-g*v*b_sigma
K*bddot+G*bdot+V_q*b = e_Phi*h
```

The radial/phase equations are unsourced. This is not an arbitrary radial
drive or a fitted temperature protocol. Natural b has dimension E, h E^3;
T is a natural-energy population input, not admitted material temperature.
pi_phase is not UET Pi; C/R_gen/R_obs are not covariance states.

## 2. Real-pair Hamiltonian and source reciprocity

Use two real blocks with momenta p,r and their acoustic-only stationary
thermal covariances. Heavy tree modes remain virtual and initially empty.
The quadratic off-diagonal potential is V_b=sum_i T_i*b_i. Cross response:

```text
Xdot=A_r*X+X*A_p^T+delta_A_b*C_p+C_r*delta_A_b^T
delta_A_b lowerleft=-K^-1*V_b
F_i=T_i:X_xx
K*lddot+G*ldot+V_q*l=-F-M_pair_full*b
W2=int bdot*F = int h*ldot_Phi
```

There are two real pair orientations. F=T:X and M_pair_full=2M_predecessor,
not the predecessor single-oriented .5T:X. Integrating the reciprocal
Euler operator by parts gives the source-work identity when compact b and
bdot vanish at both endpoints. Symmetric stationary contact contributes
int bdot*M*b=.5[b^T*M*b]_end=0 analytically, not a dissipative rate. The
binary64 contact-cycle subtraction still fails its tiny relative gate.
Per-internal-pair l is E^-2 and W2 is E; a justified momentum measure E^3
would convert it to an E^4 energy density. No SI measure/map is admitted.
At q0 the two identical-momentum blocks are an orientation-normalization
control, not two additional physical material modes. Finite-amplitude
off-diagonal modulation is the declared quadratic control, not a completed
continuum source-counting or nonlinear parent-action prescription.

## 3. Independent leading coefficient, not an amplitude fit

Write the compact source as exact finite tones, V_b=sum_nu V_nu exp(-i nu t).
In the exact symplectic tree basis, each Liouvillian channel rho obeys
Ydot=rho*Y+R_nu exp(-i nu t). Thus:

```text
Y_nu(t)=R_nu*[exp(-i nu t)-exp(rho*t)]/(-i nu-rho)
J(z)=int_0^L exp(z*t)dt=expm1(z*L)/z; J(0)=L
W2=sum_omega,nu,i,j (-i omega)*B_omega,ij*R_nu,ij
   *[J(-i(omega+nu))-J(rho-i omega)]/(-i nu-rho)
```

Resonance uses the analytic J' limit, not a width. Independently, for
tree modes (E_p,u_p),(E_r,u_r) and acoustic occupations n_p,n_r:

```text
W_pair=sum (E_p+E_r)(n_p+n_r)*|u_p^dagger*Vhat(E_p+E_r)*u_r^*|^2/(4E_pE_r)
W_number=sum (E_r-E_p)(n_p-n_r)*|u_r^dagger*Vhat(E_r-E_p)*u_p|^2/(4E_pE_r)
W2=W_pair+W_number
```

The vacuum +1 is deliberately absent. The zero-T result here is zero
thermal-insertion work, not a theorem that a real quantum system cannot
absorb at zero temperature. Exact tree roots/normalizations at 50 digits
and a 35-digit control avoid cancellation at the same recorded inputs;
they add no physical input precision. The time convolution and modal
sum are different calculation methods, not external replication.

## 4. Energy transfer does not determine irreversible entropy

The finite-amplitude quadratic control evolves C=S*C0*S^T and verifies
Delta_Hrot=int .5 Tr(Vdot*C). Its energy is the rotating Gaussian
Hamiltonian, not the full physical Noether E=Hrot+mu*N ledger. Quartic
background completion, charge exchange and physical heating remain open.
For canonical momentum p_c=K*xdot+G*x/2:

```text
P_velocity=[[0,K^-1],[-K^-1,-K^-1*G*K^-1]]
S*P_velocity*S^T=P_velocity; det(S)=1
conditional full-rank Gaussian Delta_s=.5 Delta_logdet(C)=log|det(S)|=0
```

The primary insertion has rank four in twelve coordinates. It is not a
complete quantum covariance or a full-rank Gaussian distribution, so its
complete-state entropy is undefined, not assigned zero. A separately
labelled positive full-rank covariance tests the conditional identity only;
it does not fill the empty heavy/vacuum populations of the primary branch.
Irreversibility requires an admitted collision, reservoir or coarse-graining
and readout contract. Absorption alone does not supply that contract.

VERIFICATION: Final25-file linked suite477 passed in566.10 seconds, including36 new work tests and30 funding-contract tests; tests validate record integrity and retained FAIL, not physical acceptance. Six locked momentum/state cases. W2 ranges6.823e-15 to4.441e-13 in conditional natural pair units. Extended time/modal relative disagreement is at most1.407e-37;35/50-digit controls agree at stored binary64 precision, not material precision. The original thirteen checks retain six FAILs. Binary64 time/modal error reaches2.681e-3; finite-amplitude halving ratios are near1/16, not the1/4 leading quadratic-work ratio. This is an observed higher-order-dominated grid, not a fitted asymptotic proof. Zero-drive energy drift is3.469e-18 and is not subtracted to force ledger PASS. Audit-time Path read allowlist, evidence/protected/first-failure hashes, six local links and historical calendar/acceptance/model/holdout invariants were checked. No whole-repository, external or full interacting validation.

CONTROLLING_BLOCKER: `finite_amplitude_work_grid_outside_leading_limit_and_binary64_work_cancellation`; physical/interacting inputs are separate, still open.

NEXT_ACTION: Use the verified coefficient and conditional entropy boundary in measurement design. Any finite-amplitude validity study must derive a controlled remainder and declare its protocol before calculation, not tune a pulse/amplitude to observed work. Keep source-to-state-to-detector/independent scale work explicit and the7/11 October deliverables unchanged. These identities alone do not accept G2-G4 or Full R1/Goal.

CLAIM_BOUNDARY: Conditional real-pair Gaussian rotating-energy work only; no full interacting/quantum/SI heat, collision, KMS or irreversible entropy closure. No fitted alpha/rate, threshold/padding/ontology/Core-owner change, numeric Xie access or pristine blindness claim; prior exposure remains REVIEW_REQUIRED. [Brown-Friis-Huber](https://arxiv.org/abs/1608.04977) studies Gaussian passivity and [Serafini-Illuminati-De Siena](https://arxiv.org/abs/quant-ph/0307073) studies complete Gaussian-state entropy through symplectic invariants. Their abstracts are methodological context, not admission of this incomplete covariance as a quantum state. [Kubo](https://www.jstage.jst.go.jp/article/jpsj1946/12/6/12_6_570/_article) supplies response-theory context, not a measured transport coefficient for this branch or a novelty claim.
