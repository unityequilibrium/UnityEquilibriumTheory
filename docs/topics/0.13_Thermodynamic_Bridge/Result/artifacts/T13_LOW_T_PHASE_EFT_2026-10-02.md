# Tree-matched low-temperature phase thermal prescription

MAJOR_RESULT_CLOSURE: `T13_TREE_MATCHED_LOW_T_PHASE_THERMODYNAMIC_PRESCRIPTION`, `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED: A separately declared phase-only one-loop thermal prescription from joint tree elimination of the original radial/classical-Phi action. Gapless parent dispersion, T4/T6 thermal pressure, entropy, leading source/Phi response and relative-flow partition function agree with independent checks. Tree EOS and leading T4 do not identify a subleading kinetic response combination; a conditional dispersion measurement adds information.

WHAT_REMAINS_OPEN: Vacuum Wilson matching/interaction remainder, full finite-T normal-component dynamics, physical heat/collision/Kubo/SK-KMS/entropy transport, independent material/source/readout/temperature scale and original causal/Core admission. Full Topic13/R1-R5/funding science acceptance and novelty remain open.

DEPENDENCY_UNLOCKED: New-EFT remainder and independent-input research only. No physical/Core/Gravity unlock or overwrite of the Core-owner composition; old Hartree remains excluded in its original low-T scope.

STATUS: `PASS_SCOPED_TREE_MATCHED_LOW_T_EFT`. [Artifact](t13_low_T_phase_eft.json) SHA-256 `050aceb4f94f3534929d8c59c75da4dda8efe16ce7aec250a34f6f8b5868dcb7`.

WHAT_CHANGED: New topic-local branch/verifier/tests, tree/source/phase matching and actual thermal integrations. No old Hartree masses, potential, counterterms or poles reused as new answers. All main action trial inputs unchanged; kinetic-family probes are declared separately, not fitted.

EQUATION_OR_MAPPING:

## 1. Definition, ontology and loop order

Branch: `t13.candidate.tree_matched_classical_phi_low_T_phase_EFT_v1`.
Natural units only: mu, xi, T, Phi, gamma have E; s, X, V'', chi/rho have E2;
external h and entropy/charge have E3; pressure has E4; eta/B6 have E^-2.
O(2) radial amplitude squared s is not collective C. Phi is the existing
effective response, not a metric or 2PI functional. R_gen/R_obs do not enter
state or feedback. h is an external conjugate source, not an added state.

For X=mu^2-xi^2, and r=X-m0^2+gamma*(Phi-Phi_ref),

```text
Omega0(s,Phi;X,h)=-r*s/2+u*s^2/4+V_R(Phi)-h*Phi
s=r/u, V_R'(Phi)-gamma*s/2-h=0
P0(X,h)=r^2/(4u)-V_R(Phi)+h*Phi
V_R=epsilon*(m_Phi^2*x^2/2+lambda_Phi*x^4/4), x=Phi-Phi_ref
U=u-gamma^2/(2*V_R'')>0
P0_X=s/2, P0_XX=1/(2U), P0_h=Phi0
```

The restricted inputs satisfy epsilon*m_Phi^2>gamma^2/(2u).
The reduced cubic source equation is globally monotone; the condensed
solution is unique in this class and has positive radial/Phi Hessian.
This is a classical/tree statement, not a quantum vacuum stability proof.

The prescription quantizes the IR phase, not classical Phi. Treat P0 as
tree Wilson input and compute the finite thermal difference of its phase
determinant at one loop. A heavy mean-field shift is order hbar; its
contribution to stationary pressure begins at hbar^2 because tree first
derivatives vanish. Differentiating the tree-eliminated P1 includes that
chain at first order. This is order bookkeeping, not a computation of the
full shifted microscopic Hessian/finite-T two-fluid response.

Full one-loop pressure would also require matched vacuum terms and their
renormalization; those are not computed. No old Hartree trace-log or
double-bubble is present. The finite thermal difference below is not an
extra phonon term inserted into old Hartree Omega.

## 2. Independent conservative parent and dispersion

At relative rest let ell=q^2-omega^2, a=2us and K_Phi=epsilon*Z_Phi.

```text
Gamma = [[ell+a, 2i*mu*omega, -gamma*sqrt(s)],
         [-2i*mu*omega, ell, 0],
         [-gamma*sqrt(s), 0, V_R''+K_Phi*ell]]
Gamma_phase=ell-4mu^2*omega^2/(ell+a-gamma^2*s/(V_R''+K_Phi*ell))
rho=s, chi=s+2mu^2/U, c^2=rho/chi
A0=2sU, H=1+gamma^2*s*K_Phi/(V_R'')^2
omega=c*q+eta*q^3+O(q^5)
eta=H*(1-c^2)^2/[2c*(A0+4mu^2)]
```

No old Hartree phase mass is set to zero; tree stationarity creates this
new branch's zero mode. The Schur root agrees with an uneliminated
polynomial and an independently assembled six-state first-order parent.
Its kinetic metric is diag(1,1,K_Phi); the potential is the positive heavy
Hessian plus positive q^2 gradients. Antisymmetric gyroscopic mixing drops
out of E2=(dot_x^T K dot_x+x^T V(q)x)/2. The direct operator check satisfies
L^T Q+Q L=0 and all six eigenvalues are nongrowing at the sampled q.
The local tree wave principal part is not a repair or leakage test of the
original conserved-C dynamics.

| mu (E) | Phi0 (E) | s (E2) | c | eta (E^-2) |
| --- | --- | --- | --- | --- |
| 1.05 | .041593538865 | .104163741555 | .210767027723 | .470930156682 |
| 1.20 | .173549574617 | .446941982985 | .364184456194 | .157409949338 |

These are tree states, not predecessor Hartree states or measured He-II.

## 3. Thermal pressure, entropy and Phi response

```text
Delta_T P = -T*integral d^3q/(2pi)^3 ln(1-exp(-omega(q)/T))
Delta_T P = A4*T^4+B6*T^6+O(T^8) within the tree dispersion expansion
A4=pi^2/(90c^3), B6=-4pi^4*eta/(63c^6)
s_th=4A4*T^3+6B6*T^5+...
Delta_T <Phi>=partial_h A4*T^4+... at phase one-loop
Delta_T n=partial_mu A4*T^4+...
C_V,fixed_charge=12A4*T^3+... (leading only)
```

The T6 coefficient follows from the independent Bose moment
integral x^5/(exp(x)-1) dx=120*zeta(6), not a curve fit.
Its error against the full parent **acoustic-mode** integral decreases:
at the finest two T values pressure disagreements are 8.430e-6/6.272e-6;
independent Bose entropy disagreements are 1.683e-5/1.252e-5.
The entropy integral also agrees with numerical differentiation of parent
acoustic pressure. The other parent modes and their exponentially small
thermal terms are not included in this phase-only definition; their
omission is not a certified full microscopic error bound.

At the two tree states partial_h A4=-131.709768548/-5.703351337 E^-3.
Thus a noncircular natural-unit forward thermal Phi response is defined in
this prescription, with a state-dependent T4 law. It is not normalized TTG
Phi or independent alpha_Phi_K. It does not turn k_B*T*ln(2) into a beta/EOS
derivation. Numerical convergence does not bound UV matching, Wilson
coefficient errors or phonon interactions at trial u=1.

## 4. Leading relative-flow consistency

For the declared phase background theta=-mu*t+xi*z,

```text
A=s+2mu^2/U, B=2mu*xi/U, D=s-2xi^2/U, rho=s
L2=A*dot_pi^2/2+B*dot_pi*partial_z pi-D*(partial_z pi)^2/2
   -rho*|grad_perp pi|^2/2
A4_flow=(pi^2/90)*(A*D+B^2)^(3/2)/(rho*D^2), D>0
```

An angular positive-frequency integral checks this coefficient separately.
Charge/spatial current are derivatives of the same pressure, with
n=partial_mu P and j_z=-partial_xi P in this phase/source convention.
This supplies leading **equilibrium** relative-flow response, not a new
normal hydrodynamic state, two-sound eigenproblem or dissipative tensor.
T6 matching is declared at relative rest only.

The phase-EFT method context is [Son](https://arxiv.org/abs/hep-ph/0204199).
The low-T partition/current and frame dependence are treated in
[Kourkoulou, Nicolis and Parmentier, Eqs. 1.1-1.3 and 2.4-2.16](https://arxiv.org/html/2212.12555v2).
Their result is a standard-method comparator; it is not UET calibration or
a novelty claim. Pi used for phase perturbations in other conventions is
not the existing UET Pi=dot_Phi.

## 5. Physical ambiguity versus coordinate redundancy

Vary Z_Phi=.5,1,2 holding other declared coefficients fixed. P0, c and A4
remain identical while eta and B6 differ. Positive energy metrics and
independent parent frequencies remain admissible at the tested states/q.
This constructs a physical response ambiguity in this restricted class.

Separately rescale Phi'=a*Phi, h'=h/a, gamma'=gamma/a,
V''{}'=V''/a^2, Z_Phi'=Z_Phi/a^2 with the quartic/ref transformed too.
Pressure/A4/eta are invariant. Thus coordinate normalization is not the
kinetic-family ambiguity. Dispersion identifies the invariant combination
I_kinetic=gamma^2*epsilon*Z_Phi/(V'')^2; it identifies Z_Phi alone only when
the other coefficients and Phi normalization are independently fixed.
At gamma=0 it cannot identify Z_Phi, as the negative control confirms.

The [conditional measurement card](T13_LOW_T_PHASE_EFT_MEASUREMENT_CARD_2026-10-02.md)
gives the additional observable, information gain and uncertainty relation.
It is not lab feasibility or physical input admission.

VERIFICATION: Fourteen artifact checks; focused and linked regression results recorded in UPDATE_LOG. Two mu, q=.008/.004/.002, T=c*dispersion_scale/(32,64,128), derivative steps .0004/.0002/.0001, xi=0/.02/.04, adaptive tolerances 1e-8/1e-10. Grids/gates declared before first audit, no external-data preregistration. Full parent polynomial/first-order energy, pressure/source derivatives, entropy/moment, relative-flow and coordinate/decoupling negative controls; source/protected hashes and units/claim review. No full quantum or transport audit claimed.

CONTROLLING_BLOCKER: `low_T_EFT_vacuum_Wilson_and_interaction_remainder_not_matched`. The predecessor's blocker still applies to predecessor Hartree; it is not erased.

NEXT_ACTION: Quantify the interaction/derivative expansion and vacuum Wilson input obligations in this new branch; independently establish material/state/source/readout/scale for its measurement card. Full finite-T normal/heat transport needs its own derivation. Preserve 7 October freeze and 11 October portfolio review; don't restart dates or rerun unchanged Hartree.

CLAIM_BOUNDARY: Scoped tree-matched phase-only low-T prescription, thermal differences and conditional kinetic-information result, not a controlled full quantum EOS, He-II/TTG prediction, SI alpha, external validation or Full Topic13/Core. No fit, old-mass/phonon repair, clipping/filter/padding/threshold change, new numeric Xie read or Core-owner edit. Conserved-C failure stays BLOCKED at 1e-6; prior Xie exposure REVIEW_REQUIRED. Global claim promotion and physical/full-Core unlock false.
