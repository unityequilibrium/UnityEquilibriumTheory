# O(2) Finite-Density EOS and Covariant Superfluid Transport Contract

## Status

- Equation of state: `tree-level finite-density O(2) mean-field derivation`
- Ideal current/stress: `covariant T=0 pure-superfluid constitutive derivation`
- Dissipative sector: `longitudinal Kubo-matching interface / synthetic control only`
- Physical coefficients, finite-temperature normal component, full Schwinger-Keldysh completion, SI lane, and curved 3+1 evolution: `BLOCKED`

This package narrows the signed-charge equation-of-state blocker. It does not
promote Topic 0.11, Topic 0.19, global-universe closure, or any validation claim.

## Ontology and conventions

- `chi=A exp(i theta)` is the polar representation of the existing global-O(2) matter doublet.
- `n` is the signed O(2) Noether charge density in a declared timelike frame.
- `C=(n_bar-n_ref)/n_scale` remains a normalized coarse hydrodynamic coordinate.
- `Phi` is the effective response scalar from the conservative parent action; it is not information, a metric tensor, or a particle.
- `theta=-mu*t`, metric signature is `(-,+,+,+)`, and v1 uses natural units.
- A history trace is absent from the state and has no backreaction.

## Tree-level homogeneous equation of state

The response-shifted mass and stationary grand potential are

```text
m_eff^2(Phi) = m^2 - epsilon_nc*h*(Phi-Phi_*)
Omega(A;mu,Phi) = (m_eff^2-Z*mu^2)*A^2/2 + lambda*A^4/4
q = Z*mu^2-m_eff^2.
```

For `q<=0` the vacuum-relative normal branch has `A=0`, `p=0`, and `n=0`.
The `q=0` boundary is reported separately because derivatives are one-sided.
For `q>0`,

```text
A_*^2 = q/lambda
p = q^2/(4*lambda)
n = dp/dmu = Z*mu*q/lambda
epsilon = mu*n-p
chi = dn/dmu = Z*(3*Z*mu^2-m_eff^2)/lambda
c_s^2 = q/(3*Z*mu^2-m_eff^2).
```

The canonical free energy is `f(n,Phi)=mu*n-p`, where the stable signed root
of `Z^2*mu^3-Z*m_eff^2*mu-lambda*n=0` is selected by monotone bracketing.
Reciprocity from the same action requires

```text
(partial p/partial Phi)_mu = epsilon_nc*h*A_*^2/2
(partial f/partial Phi)_n = -epsilon_nc*h*A_*^2/2.
```

The symmetric phase-field double well remains a constitutive comparator. It is
not substituted for this EOS unless a fixed-domain residual is at most `1e-3`.
The homogeneous EOS does not derive `kappa_C`.

## Covariant ideal sector

With `xi_mu=nabla_mu theta+A_mu`, `X=-xi_mu*xi^mu`, and
`Delta^{mu nu}=g^{mu nu}+u^mu*u^nu`, the ideal Josephson condition is
`u^mu*xi_mu=-mu`. The action-derived T=0 constitutive relations are

```text
f_s = Z*(Z*X-m_eff^2)/lambda
N^mu = f_s*xi^mu
T^{mu nu} = f_s*xi^mu*xi^nu + p*g^{mu nu}.
```

At zero counterflow they reduce to the perfect-fluid form and reproduce the
homogeneous EOS. A finite-temperature normal component is not inferred from
this action and remains open.

## Dissipative and causal boundary

The conservative action does not generate dissipation. The v1 longitudinal
interface therefore requires explicit `KuboCoefficientRecord` entries for
regular conductivity, phase relaxation, cross response, and relaxation time.
No numerical defaults are permitted.

For a declared two-force control, the Onsager matrix must be symmetric and
positive semidefinite so `sigma_entropy=X^T L X>=0`. The regular-current causal
control uses

```text
tau_J*d_t J + J = -sigma_reg*grad(mu)
D = sigma_reg/chi
v_transport^2 = D/tau_J <= 1.
```

Synthetic records may be used only by a verifier explicitly marked
`SIMULATION_ONLY`. Physical runs require externally or microscopically matched
records with source identity, state point, units, correlator ID, and hash.

## Verification and claim boundary

The generated verifier must check stationarity, analytic derivatives,
Legendre closure, signed symmetry, response-null behavior, projector and
Lorentz covariance, Noether-current agreement, Goldstone sound speed, entropy
sign, causal speed, missing-provenance blocking, and trace isolation.

Allowed wording is limited to the status labels at the top of this document.
The package does not establish microscopic transport values, full two-fluid
hydrodynamics, GR validation, spacetime geometry, or whether the complete
universe is globally open or closed.
