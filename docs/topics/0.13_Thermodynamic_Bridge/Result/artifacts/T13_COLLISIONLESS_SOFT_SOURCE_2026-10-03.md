# The Gaussian soft ray retains exact collisionless streaming channels

MAJOR_RESULT_CLOSURE: `T13_GAUSSIAN_COLLISIONLESS_SOFT_RAY_SOURCE_RESPONSE`, `CLOSED_FOR_LANE`. Same named acoustic thermal-insertion branch, not a new physical lane or Full Topic13/R1/Goal closure.

WHAT_IS_ACTUALLY_CLOSED: Phase-local covariance, momentum jet, six zero-channel streaming equations, fixed-centre finite-q convergence and the full-domain static pressure endpoint. Numerical closure is controlled by [artifact](t13_collisionless_soft_source.json), not this derivation alone.

WHAT_REMAINS_OPEN: Full interacting/vacuum/thermal matching and approximation control; actual heat-source/readout and independent material scale; collision operator, second-order work, entropy production, physical Kubo and SK/KMS transport. The original finite-cutoff tail test is not made to pass by the full-domain calculation.

DEPENDENCY_UNLOCKED: No physical/Core/Gravity unlock. Source-work/heat-readout research may proceed when the scoped numerical checks pass.

STATUS: `PASS_SCOPED_COLLISIONLESS_SOFT_SOURCE`; artifact SHA-256 `be7cb2e3bb5ba749e91876e56005ea63269f5b93b0d317eedf7ee8adebfc65a3`. The [first failure](t13_collisionless_soft_source_first_failure.json), SHA-256 `95890c85298ca95524abd13316d0f997c329015aae51f0af081920fad3d60bdb`, is retained: moving-centre monotonicity and truncated thermal-tail checks failed. Thresholds, point parameters and original branch remain unchanged.

WHAT_CHANGED: Separate [calculation](../../Code/03_Research/Research_T13_Collisionless_Soft_Source.py), [tests](../../Code/03_Research/test_t13_collisionless_soft_source.py) and [registry](../../Data/03_Research/t13_collisionless_soft_source_registry.json). The [Noether predecessor](T13_THERMAL_NOETHER_RESPONSE_2026-10-03.md) and protected action are not edited.

EQUATION_OR_MAPPING:

## 1. Tree source on a non-real ray

Set z=w*q in the rest frame, h0=0. Write v=sqrt(s), where s is the
declared matter amplitude squared, not C. The active radial/Phi potential
block gives

```text
x_h = V_active^-1 (0,1)
x_mu = V_active^-1 (2*mu*v,0)
chi_n = s+2*mu*v*x_mu_sigma
n_h = 2*mu*v*x_h_sigma
delta_mu = w^2*n_h/(s-w^2*chi_n)
delta_xi = -w*n_h/(s-w^2*chi_n)
mean_active = x_h+x_mu*delta_mu
q*theta = -i*delta_xi, theta=d_pi/v
```

The static w=0 and large-|w| tree endpoints differ by n_h^2/chi_n.
This is fixed-chemical versus fixed-charge response, not a parameter
adjustment. h has natural dimension E^3, Phi dimension E, and integrated
susceptibility dimension E^-2. It is not an admitted Kelvin calibration.
pi_phase is not UET Pi; neither R_gen nor R_obs enters the covariance state.

## 2. Remove the divergent phase coordinate, not physical modes

For the rotation R_sigma,pi=-1, R_pi,sigma=1, define

```text
G=theta [[R,0],[-iz*R,R]]
X_cartesian = X_local+G*Cov_p+Cov_r*G^T
(-iz-L_Ar,Ap) X_local = delta_A_L*Cov_p+Cov_r*delta_A_R^T
common=-K^-1*(T_sigma*d_sigma+T_Phi*d_Phi)+2*mu*delta_mu*P_matter
delta_A_L lowerleft=common+theta*(z^2-r^2+p^2)*R
delta_A_R lowerleft=common+theta*(z^2+r^2-p^2)*R
both lower-right=2iz*theta*R
```

The finite-q radial equation implies common_pi,pi=(q^2-z^2)d_sigma/v;
its soft limit is exactly zero. The original binary64 cancellation is
reported, not concealed by a mass repair. The source projection uses the
same stationary seagull/background contact as the predecessor, plus the
derived density and gauge-current terms. Coarse Cartesian covariance and
source projection provide an independent check. Direct tiny-q Cartesian
subtractions can be ill-conditioned; they are not called a reliable
finite-precision identity test at every arbitrarily small q.

## 3. Resolve the zero channels by singular perturbation

In the six-column symplectic tree basis, generator frequencies are
(-i*E_i,+i*E_i). Exactly six opposite-frequency pairs have zero sum.
At nonzero p, the remaining channels are nondegenerate in the declared
candidate. No singular-value threshold selects or discards these channels.

Expand A_r=A_p+q*t*A_p'+..., Cov_r=Cov_p+q*t*Cov_p'+...,
where t is the physical momentum cosine. At leading order the zero-channel
source vanishes. First order fixes their finite response:

```text
X_off(t)=X_off0+t*X_off1
H=W^-1*A_p'*W
X_zero_ij(t)=(N0_ij+t*N1_ij+t^2*N2_ij)/(-i*w-t*H_ii)
```

The denominators are w plus or minus group_velocity*t. They are streaming
denominators, not collision rates. The momentum jet includes the derivative
of the symplectic mode normalization and Bose population, and is checked
against a central momentum difference. All three tree virtual poles remain;
only the acoustic mode carries the declared thermal population.

## 4. Analytic angular and static endpoints

For a=-i*w, b=-H_ii, J_k=(1/2)integral_-1^1 t^k/(a+b*t)dt:

```text
J0=[log(1+b/a)-log(1-b/a)]/(2*b)
Jk=(average(t^(k-1))-a*J(k-1))/b
```

The small-b/a binary64 implementation uses a fixed convergent 64-term
series, not a filter. At w=0 the numerator is exactly t*N1: the removable
channel is N1/b, including t=0 by its limit. Real angular poles are rejected
instead of assigning a width. Independent angular quadrature and static
same-action pressure Hessian test these formulas. The static Bose population
factor does not create homogeneous rethermalization or hydrodynamic transport.

## 5. The failed tests determine the corrected protocol

The first point sequence held the left momentum fixed and compared each
pair with a different centre. Its one nonmonotone susceptibility row remains
in the raw record. A convergence sequence must instead hold vector k fixed:
p_vector=k_vector-q_vector/2, r_vector=k_vector+q_vector/2.
The same q/k ratios and thresholds are used; no momentum is fitted.

Increasing precision alone reproduces both initial failures. In particular,
the 32-to-40 truncated Bose integral difference is genuine near a response
cancellation. The Noether prescription requires a full momentum domain,
not an arbitrary finite cutoff. The corrected calculation therefore includes
the tail complement x=split+t/(1-t), t in (0,1), with its exact Jacobian.
32 and 40 are compared as split locations for the same [0,infinity) domain.
The original truncated result still fails and is reported separately.
This is not cone padding, a source-support change or a finite-cutoff certificate.

The equivalent calculation at 50 digits and a 35-digit control retains the
same recorded action inputs; it does not increase physical input accuracy.
An attempted corrected audit stopped before writing a new artifact because
the predecessor's low-p curvature fixed point did not converge in the
infinite-domain quadrature. The replacement refines all three roots of the
same exact characteristic polynomial; it does not extrapolate that low-p
iteration, discard tail nodes or impose a finite physical cutoff.
Known Bose moments independently test the infinite-domain quadrature.
Finite refinements are numerical evidence, not a uniform error bound on
all complex rays or on interacting continuum dynamics.

VERIFICATION: Ten corrected artifact checks over54 point rays and16 thermal cases. Final24-file linked run440 passed in500.32 seconds, including48 new tests. Finest fixed-centre chi error8.765e-5 and covariance1.637e-3, both below the original1e-2 point gate. Raw fixed-left chi/covariance errors remain7.962e-2/2.120e-2. Full-domain split error1.262e-14; truncated32/40 error4.262e-7 still fails1e-8. Static pressure error3.245e-13, radial refinement4.045e-11, angular5.048e-14, coarse Cartesian projection/covariance6.368e-11 and jet FD4.551e-8. The35/50-digit control agrees at recorded binary64 output precision, not certified physical input precision. Hash/registry and audit-time Path allowlist pass, not whole-program security or pristine blindness. Original leakage threshold1e-6 is unchanged and not rerun here.

CONTROLLING_BLOCKER: `full_interacting_work_entropy_and_physical_heat_source_transport_open`.

NEXT_ACTION: Actual second-order source work/heat-readout mapping and independent material scale, then interacting/collision/entropy completion. Preserve 7/11 October and full Goal/R1-R5 acceptance.

CLAIM_BOUNDARY: Gaussian complex-frequency soft-ray response only. No heavy quantum/vacuum admission, fitted rate/contact/alpha, thermalization proof, physical heat coefficient, conserved-C repair, Core-owner edit or Full Topic13/global closure. No numeric Xie access; prior exposure remains REVIEW_REQUIRED. [Morgan](https://arxiv.org/abs/cond-mat/0307246) separates collisionless finite-T response and thermal-component drive; [Hiyane-Watabe-Nikuni](https://arxiv.org/abs/2310.01988) studies hydrodynamic/collisionless crossover with a kinetic equation. Their abstracts are method context, not physical coefficient provenance, validation or novelty of this candidate.
