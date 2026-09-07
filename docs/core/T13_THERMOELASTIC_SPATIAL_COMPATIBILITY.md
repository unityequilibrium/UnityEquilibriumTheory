# Topic 13: finite-wavevector thermoelastic compatibility

Status: CANDIDATE conditional material interface, not an accepted UET action.

## Question and physical correspondence

The previous scalar and normal-strain tensor bridges eliminate strain by
setting every stress component to zero. That is a homogeneous free-expansion
boundary condition. A bulk nonzero-wavevector grating instead requires a
compatible displacement and mechanical equilibrium. This note derives that
distinct response; it does not replace or invalidate the homogeneous result.

Standard ingredients are symmetric displacement gradients, thermoelastic
stress/entropy, and elastic plane-wave equilibrium. See the original
[FEniCS thermoelasticity demonstration](https://comet-fenics.readthedocs.io/en/latest/demo/thermoelasticity/thermoelasticity_transient.html)
and [Bower, elastic plane waves, section 4.4.4](https://solidmechanics.org/text/Chapter4_4/Chapter4_4.htm).
The Phi--strain interaction is our conditional ansatz, not derived by these
sources and not an independently established UET/material identification.

## Ontology and units

Use full symmetric Mandel vectors ordered xx, yy, zz, sqrt(2) yz,
sqrt(2) xz, sqrt(2) xy. Euclidean vector products then equal tensor contractions.
K_el is the isothermal material stiffness, NOT UET C. The response phi_r is
the previous candidate Phi_E amplitude; phi_r=Z_Phi*Delta_Phi_base still needs
independent material normalization. R_gen and R_obs are not state variables.

Natural energy powers: T and phi_r: 1; K_el: 4; strain and unit direction n: 0;
thermal expansion alpha: -1; beta=K_el*alpha: 3; coupling G: 3;
fixed-strain volumetric heat capacity c_eps: 3; curvature a_phi: 2;
free-energy density: 4; compliance R_n: -4. A physical SI coefficient is OPEN.
All numerical examples are dimensionally assigned synthetic inputs, not data.

## Derivation before implementation

Linearize about a fixed reference T>0, using constant local coefficients:

```text
df = eps.K_el.eps/2 - dT*beta.eps - c_eps*dT^2/(2*T)
     + phi_r*G.eps + a_phi*phi_r^2/2
sigma = K_el*eps - beta*dT + G*phi_r
ds = beta.eps + c_eps*dT/T
```

For a nonzero grating wavevector q*n, take displacement
u(x)=v*sin(q*n.x)/q; eps(x)=sym(n tensor v)*cos(q*n.x).
Define its Mandel matrix B(n) by eps=B*v. Mechanical equilibrium is
B^T*sigma=0, equivalently sigma*n=0, not sigma=0. Set
A=B^T*K_el*B, b=B^T*beta, h=B^T*G. A is positive definite for positive
definite K_el and nonzero n. For a locally fixed entropy perturbation ds=0:

```text
[ A   -b     ] [v ] = [-h*phi_r]
[ b^T c_eps/T] [dT]   [    0   ]
R_n = B * A^-1 * B^T
dT/phi_r = T * beta^T*R_n*G / (c_eps + T*beta^T*R_n*beta)
```

An independent elimination uses the fixed-entropy elastic operator
K_ad=K_el+(T/c_eps)*beta*beta^T and solves
(B^T*K_ad*B)*v=-h*phi_r, then dT=-T*beta^T*B*v/c_eps.
At fixed T the strain/response Schur bound for this direction is
a_phi-G^T*R_n*G>0. This is not a dynamic well-posedness proof.
The temperature coordinate of free energy is concave; do not require its
full temperature-extended Hessian to be positive definite.

Homogeneous zero-stress elimination uses R_0=K_el^-1 instead. It gives the
previous formula T*(alpha^T*G)/(c_eps+T*alpha^T*K_el*alpha).
In general R_n is rank three, not the full compliance. One cannot obtain
homogeneous unconstrained strain by inserting q=0 in the nonzero-q problem.

For isotropic bulk modulus K, shear modulus mu, alpha=(alpha_V/3)*I,
and G=g*I, let L=K+4*mu/3. Independent longitudinal elasticity gives

```text
(dT/phi_r)_grating = T*K*alpha_V*g / (L*c_eps+T*K^2*alpha_V^2)
(dT/phi_r)_uniform = T*alpha_V*g / (c_eps+T*K*alpha_V^2)
```

For positive shear modulus these differ even in an isotropic solid.
The shear-free limit recovers the uniform expression as mu tends to zero
from above; exactly zero shear makes the full stiffness singular.

## Scope and verification design

This is a mechanically quasistatic, locally isentropic, infinite/periodic
bulk response. It assumes no imposed entropy perturbation. A laser-heated
TTG can have a nonzero initial entropy perturbation, so it is not automatically
described by ds=0. No acoustic dynamics, surfaces, diffusion, KMS noise, or
coupled Phi dynamics are implemented. A physical use would require a scale
window where mechanical equilibration precedes heat exchange, or a full
dynamic replacement. Nonzero q alone does not establish causal propagation.

Verify the block solve against fixed-entropy elimination and isotropic
longitudinal elasticity. Check full rotations including shear, direct
sigma*n equilibrium, real-space strain convergence, the homogeneous
incompatibility witness, energy-unit rescaling, and unstable-input rejection.
No experimental numeric data or holdout is an input. Existing full-closure
gates and the old causal threshold must remain unchanged.

Next physical question: derive the finite-frequency thermoelastic/heat
response with explicit initial entropy and acoustic time scales, then identify
G, Z_Phi and same-state material coefficients independently. Static compatibility
alone cannot close alpha_Phi_K or Full Topic 13.
