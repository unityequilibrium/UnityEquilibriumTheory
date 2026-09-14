# Topic 13 dynamic material response and initial entropy

Status: CANDIDATE standard-material comparator with a prescribed Phi port.
This is not an accepted UET action or a material calibration.

## Correspondence and source boundary

This follows the compatible-strain construction in
[the spatial derivation](T13_THERMOELASTIC_SPATIAL_COMPATIBILITY.md).
The standard components are elastic inertia, reciprocal thermoelastic
stress/entropy coupling, and Fourier or Maxwell-Cattaneo conduction.
The [FEniCS coupled thermoelastic demonstration](https://comet-fenics.readthedocs.io/en/latest/demo/thermoelasticity/thermoelasticity_transient.html)
states the stress/entropy and heat-balance ingredients. For coupled mechanical
and thermal energy accounting see
[Brugnoli et al., port-Hamiltonian thermoelasticity](https://doi.org/10.1080/01495739.2021.1917322).
The [wave-hierarchy study](https://arxiv.org/abs/2005.03761) distinguishes
classical thermoelasticity from relaxation-based generalized thermoelasticity.
These sources do not supply our Phi interaction, a graphite coefficient, or
the physical value of a relaxation time.

## F1-F4: variables, units, assumptions and derivation

For bulk nonzero wavevector q*n, use u=v(t)*sin(q*n.x)/q,
strain=B(n)*v*cos(q*n.x), temperature theta*cos(q*n.x), and longitudinal
heat-flux amplitude J*sin(q*n.x). Let w=dot(v), K_el be the six-component
Mandel isothermal stiffness, beta=K_el*alpha, A=B^T*K_el*B,
b=B^T*beta, h=B^T*G. The conduction coefficient k=n^T*k_tensor*n is supplied
externally. A scalar heat-flux relaxation time tau is assumed. Unforced
transverse flux components are excluded; this is a single bulk mode.

Natural energy dimensions: K_el and inertial density rho E^4; v 1; w E;
q E; time E^-1; theta, T and phi_r E; alpha E^-1; G,b,c E^3;
k E^2; tau E^-1; J E^4; heat-source Q E^5; entropy density ds E^3.
rho is a material inertial input, not UET C. phi_r is a prescribed response
amplitude, not a new state or temperature. R_gen and R_obs are excluded.
The missing physical map remains phi_r=Z_Phi*Delta_Phi_base.

Momentum conservation and heat balance give

```text
dot(v) = w
dot(w) = -(q^2/rho)*(A*v-b*theta+h*phi_r)
c*dot(theta) = -T*b^T*w-q*J+Q
tau*dot(J)+J = k*q*theta                    [tau>0: Cattaneo comparator]
J = k*q*theta                              [tau=0: Fourier comparator]
ds = b^T*v+c*theta/T; dot(ds)=(Q-q*J)/T
```

Initial laser deposition is a distinct input. For an impulsive heat energy
density E_dep with initially fixed v, theta jumps by E_dep/c and ds by
E_dep/T. The implementation instead accepts ds0 explicitly and sets
theta0=T*(ds0-b^T*v0)/c. It does not infer ds0 from Phi or an experimental
trace. Mechanical equilibrium before excitation and instantaneous deposition
at fixed strain are different preparations.

Define the positive quadratic modal availability (twice the spatially
averaged quadratic density for these sine/cosine amplitudes)

```text
W = rho*|w|^2/(2*q^2)+v^T*A*v/2+c*theta^2/(2*T)
    +tau*J^2/(2*T*k)                       [last term only if tau>0]
dot(W) = -phi_r*h^T*w + theta*Q/T - J^2/(T*k)
```

For Fourier replace the last dissipation by k*q^2*theta^2/T. W is a
linearized availability, not total SI energy. External mechanical Phi power
and thermal-source power are exposed, not hidden as failure of conservation.
This identity supplies passivity for the unforced constant-coefficient mode;
undamped shear modes are allowed. It is not microscopic KMS matching.

The ds equation is the first-order entropy perturbation balance. Quadratic
entropy production is represented by the nonnegative availability loss/T;
its mean/second-harmonic fields are outside this single linear mode. The
first-order ds equation alone is not a claim of zero entropy production.

For positive tau,k,c,rho and positive definite stiffness, the principal modal
generator in variables (v,w/q,theta,J) is skew-adjoint under the positive
availability metric after removing flux relaxation. This is a check of the
declared linear control's characteristic structure, not a numerical
pre-arrival test or a full UET continuum/domain-of-dependence proof. Fourier
remains parabolic; the original locked leakage threshold is untouched.

## Independent Laplace response

For zero initial conditions let D(s)=A+rho*s^2*I/q^2 and
F(s)=c*s+k*q^2/(1+tau*s). Elimination yields

```text
H_Phi(s) = T*s*b^T*D(s)^-1*h / (F(s)+T*s*b^T*D(s)^-1*b)
H_Q(s) = 1 / (F(s)+T*s*b^T*D(s)^-1*b)
theta(t) = [exp(M*t)*x0]_theta
           + convolution(H_Phi,phi_r) + convolution(H_Q,Q)
```

For tau=0 use the Fourier denominator, not a small hidden relaxation time.
At removable singularities of D(s), the full state resolvent rather than
this elimination must be used. No threshold adjustment or pole clipping is
permitted.

With k>0, fixed q>0 and static Phi, the long-time thermal response has zero
DC gain. The previous isentropic gain emerges only in an intermediate window
where acoustic inertia and thermal exchange are both negligible compared
with the forcing time scale. The limits k->0 and s->0 do not generally
commute. With k=0 in Fourier, the s->0 forced transfer recovers the spatial
isentropic formula, not a claim that undamped acoustic transients disappear.

## Observable consequence and test design

An initial heat perturbation with phi_r=0 can produce theta(t) through this
material comparator. Thus a sole theta=constant*phi_r output relation cannot
describe arbitrary preparations of this interface. This does not refute an
explicitly coupled UET model whose initial states are constrained by another
equation. That coupling/initialization equation is still required.

Compare the state resolvent with the independent Laplace elimination,
matrix exponential with adaptive time integration, and Fourier/telegraph
limits with analytic curves. Check pointwise source/availability balance,
positive metric, modal stability, unit rescaling, full tensor rotations and
explicit initial entropy. Synthetic constants/windows are fixed in tests
before running. No TTG numeric source, calibration, fitting or holdout is read.

Next controller: identify a physical pump-to-(Phi,entropy,displacement)
initialization and source-matched G/Z/material transport inputs, then test the
coupled response against permitted training/comparison data. Detector transfer,
finite geometry and uncertainty remain open. Do not use this standard-material
response alone to close physical alpha, Kubo, SK/KMS or Full Topic 13.
