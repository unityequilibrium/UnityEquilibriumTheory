# Topic 13: thermal matter-to-strain susceptibility matching

Status: CANDIDATE external-source extension, thermal Gaussian/one-loop increment
only. No accepted action, material identity, vacuum renormalization or physical
alpha is promoted.

## Why this route is different from relabeling h as G

The implemented O(2) interaction in `uet_covariant_matter.py` is
`V_int=-epsilon_nc*h*delta_phi*(chi_1^2+chi_2^2)/2`. It contains no material
strain. The earlier operator-substitution no-go remains correct. Introduce an
explicit external mass-source deformation `D_raw:eps*chi^2/2`, not a new UET
state. Its physical value and its association with graphite are OPEN.

For matter kinetic coefficient A_chi, canonical matter has

```text
x = m_eff^2 = (m_raw^2-epsilon_nc*h*delta_phi+D_raw:eps)/A_chi
eta = epsilon_nc*h/A_chi; D=D_raw/A_chi
x = x0-eta*delta_phi+D:eps
```

The missing two powers of energy are supplied by a deformation potential D,
not by an arbitrary scale or fit. The full operator is recorded before use.
Strain remains an external material variable. C is not mass, Phi is not
temperature, and R_gen/R_obs are excluded from states and feedback.

## Thermal determinant and derivative origin

Use the normal branch chi=0, chemical potential mu=0, T>0, x>0, flat fixed
volume, constant kinetic coefficient and fixed integration measure. The two
real components give degeneracy two. The matter quartic does not enter this
Gaussian Hessian; interaction loops and thermal-mass resummation are excluded.
The standard thermal determinant is described in
[Laine and Vuorinen, Basics of thermal field theory](https://arxiv.org/abs/1701.01554).
The following source derivatives are derived here, not supplied by that source
as a UET or graphite correspondence:

```text
F_th(T,x) = 2*T*integral_p log(1-exp(-E_p/T)); E_p=sqrt(p^2+x)
integral_p = integral_0^infinity dp*p^2/(2*pi^2)
n=1/(exp(E_p/T)-1); w=n*(1+n)
F_x = integral_p n/E_p
F_xx = -integral_p [n/E_p^3+w/(T*E_p^2)]/2
F_xT = integral_p w/T^2
c_chi = -T*F_TT = 2*integral_p E_p^2*w/T^2
```

The integrals have exponential UV convergence for positive T,x. We use a
semi-infinite quadrature, not a fitted momentum cutoff or clipped distribution.
No zero-point term is included. All outputs are thermal increments; allowed
vacuum local terms are not determined by these finite thermal integrals.

Natural dimensions: T, phi and eta E; x,D E^2; strain 1; F E^4;
F_x E^2; F_xx 1; F_xT E; c_chi E^3; G E^3; r E^2.

## Matching the whole Hessian, not just G

The chain rule gives all matching terms together:

```text
G_i = partial_phi partial_eps_i F = -eta*D_i*F_xx
delta_K_ij = D_i*D_j*F_xx
delta_a_phi = eta^2*F_xx
delta_beta_i = -partial_T partial_eps_i F = -D_i*F_xT
r = -partial_T partial_phi F = eta*F_xT
delta_c = c_chi
```

The phi/strain thermal Hessian is the rank-one matrix
`F_xx*(-eta,D)*(-eta,D)^T`. F_xx is negative, so these terms soften the
static Hessian. Positive bare stiffness/response curvature and the resulting
total Schur condition must be checked; a loop result alone is not a stable
material model. Mixed response/stress derivatives are reciprocal.

Most importantly, the same calculation produces a direct Phi--temperature
term `-r*delta_phi*dT`. Retaining G while silently discarding r is not the
full matching of this mass-source route. At D=0, G vanishes but r generally
does not. This does not identify Phi with temperature.

For declared total coefficients, the local constitutive expansion becomes

```text
df = eps:K:eps/2-dT*beta:eps-c*dT^2/(2*T)
     +delta_phi*G:eps+a*delta_phi^2/2-r*delta_phi*dT
ds = beta:eps+c*dT/T+r*delta_phi
f_phi = G:eps+a*delta_phi-r*dT
```

For compatible nonzero-q strain with b=B^T*beta, h=B^T*G and A=B^T*K*B,
zero mechanical force and ds=0 give

```text
dT/delta_phi = T*(b^T*A^-1*h-r)/(c+T*b^T*A^-1*b)
```

The earlier strain-only formula is the r=0 comparator, not automatically the
matched limit of the current matter action. This is an isentropic relation;
it is not the fixed-energy or fixed-mu energy derivative from another lane.

## Source, ensemble and interpretation limits

The existing Ding heating package and
[Ding et al., Methods](https://www.nature.com/articles/s41467-021-27907-z)
report incident setup and a temperature bound. They do not supply D, canonical
Phi normalization, or a pump-to-Phi source. Incident fluence is not substituted
for absorbed energy or Phi. No Ding or holdout curve enters this calculation.

This is a fixed-measure scalar mass-source probe, not a deformation of the
full spacetime metric, Brillouin zone, dispersion tensor or material volume.
It neither identifies chi with graphite phonons nor determines physical D.
At nonzero chemical potential, fixed-density thermodynamics requires an
additional ensemble transformation not performed here.

If experimental K, beta and c already include these same matter modes, adding
their loop increments again double counts. A physical matching prescription
must specify bare/reference coefficients, subtraction and sample state. Finite
vacuum counterterms, higher loops and Z_Phi remain open. The finite thermal
increment does not remove these uncertainties.

## Verification and next handoff

Check the mass source against the actual action curvature including the
matter kinetic normalization. Compare analytic thermal derivatives to central
finite differences of the independently evaluated free energy. Test mixed
reciprocity, Hessian rank/sign, quadrature refinement, natural-unit scaling,
matter-field reparameterization, zero couplings, and unstable-mass rejection.
An explicit synthetic total-coefficient example may compare the complete
isentropic map to the r=0 truncation, but is not physical calibration.

Next: identify a material excitation/strain source that can supply D and a
normalization/subtraction prescription, then carry G and r together into a
reciprocal dynamic interface and the pump/initial-entropy map. The pre-existing
prescribed-Phi dynamic comparator remains unchanged pending that handoff.
