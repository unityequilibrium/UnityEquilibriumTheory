# UET GR Closed-Limit and Non-Closed Response Research Specification

> **Status:** `CURVED 3+1 PERIODIC SPATIAL GEOMETRY OPERATOR VERIFIED / PROGRAM BLOCKED`
> **Current claim class:** `B`
> **Current controlling blocker:** `curved_3p1_gauge_evolution_hyperbolicity_and_constraint_propagation_missing`
> **Program rule:** General relativity is the null/closed-response model. A
> non-zero UET response is an empirical alternative, not a conclusion assumed
> from the existence of the model.

## Current curved 3+1 boundary (2026-08-28, geometry-operator wave)

The curved parent now evaluates the standard ADM Hamiltonian and momentum
constraints and computes their spatial differential-geometry inputs on a
uniform periodic Cartesian chart. The implementation constructs the
Levi-Civita connection, spatial Ricci tensor/scalar, and
`D_j(K^j_i-delta^j_i K)` directly from declared `gamma_ij`, `K_ij`, and grid
spacing. It is source-linked to Gourgoulhon's
[3+1 formalism notes](https://arxiv.org/abs/gr-qc/0703035).

Cartesian-flat exact-zero controls, a conformally-flat analytic Ricci control,
and a manufactured off-diagonal-`K` divergence control pass. The two
nontrivial operators show second-order spatial convergence over three locked
resolutions. Invalid spacing/metrics are rejected; no clipping, fitting, or
holdout data are used.

This closes `CORE_CURVED_3P1_ADM_CONSTRAINT_INTERFACE_READY` and
`CORE_CURVED_3P1_GEOMETRY_OPERATOR_READY` for their individual lanes only.
The parent result remains `PARTIAL`: lapse/shift gauge, metric and
extrinsic-curvature evolution, strong hyperbolicity, constraint propagation,
temporal convergence, non-periodic boundary treatment, Topic 13 stress-energy
projection, and dimensional observable mapping remain open. Gravity is not
unlocked.

## 1. Research question

Can UET be written as a generally covariant, causal, history-dependent
effective theory in which:

1. Einstein gravity is recovered exactly when exchange, dissipation, memory,
   and the additional space-response sector are switched off;
2. a non-closed effective matter-spacetime sector obeys an explicit covariant
   balance law;
3. matter amount can remain conserved even when matter stress-energy exchanges
   with the effective space-response sector;
4. the derived trace remains an observable of past dissipation and never acts
   as an independent source; and
5. data can distinguish a non-zero UET response from the exact GR null model
   without fitting and testing on the same evidence.

The program does **not** assume that the complete universe is thermodynamically
open to an exterior. Global closure remains unresolved until a boundary,
environment, or operational global balance definition exists.

## 2. Nested theory contract

The intended hierarchy is

```text
causal non-closed UET
    -- exchange, dissipation, and memory -> 0 -->
conservative covariant response theory
    -- epsilon_nc -> 0 and Phi -> Phi_* -->
Einstein general relativity
```

This reduction must be a continuous parameter limit. Deleting equations by
hand, cancelling unrelated fitted parameters, or taking a coefficient to
infinity does not count as GR recovery.

The nested hypotheses are

```text
H0: epsilon_nc = 0       -> Einstein GR
H1: epsilon_nc != 0      -> UET non-closed response candidate
```

The existence of `H1` does not establish that nature selects it. A physical
non-closed claim requires independent evidence that rejects or materially
outperforms `H0` after parameter penalties and holdout testing.

## 3. Closure taxonomy

| Closure level | Mathematical condition | Locked interpretation |
| --- | --- | --- |
| Matter amount | `nabla_mu N^mu = 0` | No creation or destruction of the declared matter-number current. |
| Matter stress-energy | `nabla_mu T_m^(mu nu) = Q^nu` | `Q = 0` means separately closed matter stress-energy; `Q != 0` means exchange with another modeled sector. |
| Total modeled balance | `nabla_mu (T_m + T_UET)^(mu nu) = 0` | Required by the covariant parent unless a separate global-nonconservation branch is explicitly opened. |
| GR closed-response limit | `epsilon_nc = 0` with open kernels disabled | The UET correction vanishes and the Einstein field equation remains. |
| Complete-universe closure | unresolved | No current artifact establishes an exterior, global reservoir, or global nonconservation law. |

Einstein's equations provide a local covariant balance through the contracted
Bianchi identity. That identity is not, by itself, a statement that arbitrary
curved spacetimes possess one globally conserved thermodynamic energy.

## 4. Ontology

| Symbol | Role | Independent physical state? | Claim boundary |
| --- | --- | --- | --- |
| `g_mu_nu` | spacetime metric | yes in the future gravity solver | Standard geometric variable. |
| `Psi_m` | relativistic matter variables | yes | Must be a scalar, spinor, gauge field, or fluid current with declared transformation law. |
| `N^mu` | matter-number current | derived from matter state | Used only in lanes where matter amount is meaningful. |
| `Phi` | effective space-response variable | yes in the candidate parent | A collective response degree of freedom; not information, antimatter, or a particle identification. |
| `Pi` | response rate in a 3+1 reduction | yes in reduced dynamics | Must be derived from the covariant state rather than inserted as a second ontology. |
| `Q^nu` | covariant exchange current | no; derived from coupled equations | Records transfer between modeled sectors, not missing energy. |
| `R` | derived trace observable | no | Retarded functional of a physical production source; no feedback edge is allowed. |
| `epsilon_nc` | nesting coupling | model parameter | `0` is exact GR. It is not a percentage of how open the universe is. |

`Phi = Phi_*` denotes an ordered reference, not empty or nonexistent space. The
word `ordered` becomes claim-bearing only after the parent theory demonstrates
a stable stationary point and defines an entropy current or equivalent
measurable ordering criterion.

## 5. Conservative covariant parent target

The first implementation uses a scalar response pilot because it is the
smallest covariant representation. It is not assumed to be the final dynamic
frame ontology.

In natural units (`c = hbar = 1`), use the candidate action

```text
S = integral sqrt(-g) [
      F_epsilon(Phi)/(2 kappa_E) (R_scalar - 2 Lambda)
      - epsilon_nc Z_Phi/2 (nabla Phi)^2
      - epsilon_nc U(Phi)
    ] d^4x
    + S_m[g, Psi_m]
```

with

```text
delta_Phi = Phi - Phi_*
F_epsilon = 1 + epsilon_nc xi_Phi delta_Phi^2
U(Phi) = rho_* + m_Phi^2/2 delta_Phi^2
                 + lambda_Phi/4 delta_Phi^4
```

Required coefficient policy:

- `epsilon_nc >= 0` and dimensionless;
- `Z_Phi > 0`;
- `m_Phi^2 >= 0`;
- `lambda_Phi > 0`;
- `xi_Phi` has mass dimension `-2`;
- `kappa_E` has mass dimension `-2`;
- `rho_*` has mass dimension `4`.

The equilibrium conditions

```text
F_epsilon(Phi_*) = 1
dF_epsilon/dPhi at Phi_* = 0
dU/dPhi at Phi_* = 0
```

prevent a hidden first-order curvature or fifth-force source at the ordered
reference. If `rho_* != 0`, the constant response is reported as

```text
Lambda_eff = Lambda + kappa_E epsilon_nc rho_*
```

rather than being described as missing energy.

The metric equation target is

```text
F G_mu_nu + Lambda F g_mu_nu
  + (g_mu_nu box - nabla_mu nabla_nu) F
  = kappa_E [T_m_mu_nu + epsilon_nc T_Phi_mu_nu]
```

where

```text
T_Phi_mu_nu = Z_Phi nabla_mu Phi nabla_nu Phi
              - g_mu_nu [Z_Phi/2 (nabla Phi)^2 + U(Phi)]
```

The first code wave is a tensor-formula evaluator and exact-limit verifier. It
is not a metric PDE solver, a curved-spacetime simulation, or a Bianchi proof.

### 5.1 Covariant matter-action pilot

The first matter representation is an O(2) scalar doublet
`chi_A = (chi_1, chi_2)`, equivalent to one complex scalar. Define

```text
C_amp^2 = chi_1^2 + chi_2^2
W(C_amp) = m_C^2 C_amp^2/2 + lambda_C C_amp^4/4
```

and add the nested interaction

```text
L_m,coupled = -Z_C/2 sum_A (nabla chi_A)^2
              - W(C_amp)
              + epsilon_nc h/2 delta_Phi C_amp^2
```

with `Z_C > 0`, `lambda_C > 0`, and `h >= 0`. The same action term gives
both coupling directions:

```text
E_chi_A = Z_C box chi_A
          - [m_C^2 + lambda_C C_amp^2
             - epsilon_nc h delta_Phi] chi_A

E_Phi,coupling = +epsilon_nc h C_amp^2/2
```

The mixed derivatives of the interaction energy agree exactly, so the
matter and response forces are reciprocal at the conservative action level.
At `epsilon_nc = 0`, the interaction and response equation vanish while the
ordinary scalar matter action remains in the Einstein equation.

The global O(2) rotation has the candidate current

```text
N^mu = Z_C [chi_1 nabla^mu chi_2 - chi_2 nabla^mu chi_1]
```

and its local identity is

```text
nabla_mu N^mu = chi_1 E_chi_2 - chi_2 E_chi_1
```

so the current is conserved on the conservative matter shell. This does not
yet identify `C_amp` with the normalized density/order variable `C`:

- a conserved Noether charge is not automatically a locally diffusing
  amplitude;
- the Cahn-Hilliard/Model-B law requires a constitutive or closed-time-path
  dissipative reduction;
- the current normalized operator is a fixed `epsilon_nc > 0` chart and does
  not yet expose a regular nested epsilon limit; and
- the scalar pilot is not a Dirac field, antiparticle identification,
  positron, neutrino, or established microscopic matter ontology.

### 5.2 Conserved-current and diffusive-matter bridge

The matter action supplies an on-shell O(2) Noether current, but its scalar
amplitude is not a conserved density. After choosing a unit timelike local
frame `u^mu`, decompose the current kinematically as

```text
N^mu = n u^mu + j^mu
n = -u_mu N^mu
u_mu j^mu = 0
```

The normalized matter variable is now declared to be a coarse-grained charge
density, not the scalar amplitude:

```text
C = n / n_0
J = T j^x / (n_0 L)
```

This identification is a constitutive coarse-graining assumption. It does not
derive `n_0`, `L`, `T`, or the transport coefficients from the scalar action.
On a one-dimensional local-rest-frame slice, use exact continuity and a
finite-relaxation current:

```text
partial_t C + partial_x J = 0
tau_J partial_t J + J = -M_C partial_x mu_C

mu_C = a_C C + b_C C^3 - kappa_C partial_x^2 C
       - epsilon_nc g_0 C Phi
```

The nesting is regular because `g_effective = epsilon_nc g_0`; there is no
division by `epsilon_nc`. At the GR null branch, the matter-space coupling
vanishes while the closed matter-current equation remains available. For
periodic or zero-flux boundaries, the matter-conditioned extended energy is

```text
E_C = F_C[C | Phi] + tau_J/(2 M_C) integral J^2 dx
dE_C/dt = -integral J^2/M_C dx <= 0
```

when `Phi` is held fixed for the matter-sector reduction. In the adiabatic
limit,

```text
J -> -M_C partial_x mu_C
partial_t C -> M_C partial_x^2 mu_C
```

which is exactly the discrete conserved matter equation in
`matter_space_coupled_v1`. This closes the algebraic Model-B limit and the
regular epsilon-nested matter coupling, but not a microscopic dissipative
derivation.

The causal boundary is deliberately split:

- for `kappa_C = 0` and positive local curvature
  `A = partial mu_C/partial C > 0`, the principal system is Maxwell-Cattaneo
  with characteristic speed `v_C = sqrt(M_C A/tau_J)` and must satisfy
  `v_C <= c_hat`;
- for `kappa_C > 0`, the linear dispersion contains
  `M_C kappa_C k^4`, so the high-wavenumber phase speed grows as
  `sqrt(M_C kappa_C/tau_J) k`; finite current relaxation alone is not a proof
  of a relativistic causal cone; and
- in the spinodal lane where the local curvature is negative, the simple
  local hyperbolicity condition also fails.

Accordingly, the current bridge is a partial constitutive result. A genuinely
first-order augmented hyperbolic phase-field closure, closed-time-path/KMS
matching of transport coefficients, dissipative Bianchi accounting, curved
3+1 transport, SI mapping, and physical validation remain open. The derived
history trace is absent from this reduction and has no backreaction.

### 5.3 Sourced first-order hyperbolic phase-field comparator

The ultraviolet obstruction in the simple finite-current bridge is now
compared against Dhaouadi, Dumbser, and Gavrilyuk, *A first-order hyperbolic
reformulation of the Cahn-Hilliard equation* (2025),
[DOI 10.1098/rspa.2024.0606](https://doi.org/10.1098/rspa.2024.0606) and
[arXiv:2408.03862](https://arxiv.org/abs/2408.03862). This is a sourced
external comparator, not a derivation from the UET covariant action.

The source introduces four auxiliary quantities in addition to its physical
order parameter. In the repository transcription:

```text
C                 = source c, used only inside the isolated comparator
flux_impulse      = source q; physical mass flux is q/tau
auxiliary_phase   = source varphi
auxiliary_rate    = source w = beta partial_t varphi
gradient_proxy    = source p = grad varphi when the constraint is prepared
```

The source `varphi` is an auxiliary phase/order-parameter regularization. It
is **not** the UET effective space response `Phi`, information, a history
trace, an ether, or a new particle. Identifying the comparator's `C` with the
coarse-grained Noether-charge density in section 5.2 also remains an open map.

In normalized one-dimensional notation, the transcribed system is

```text
partial_t C + partial_x(q/tau) = 0
partial_t q + partial_x[g'(C) + alpha(C-varphi)] = -q/tau
partial_t w - gamma partial_x p = alpha(C-varphi)
partial_t p - partial_x w/beta = 0
partial_t varphi = w/beta

g(C) = (C^2-1)^2/4
```

with augmented Lyapunov functional

```text
E_hyp = integral [
  g(C) + gamma p^2/2 + alpha(C-varphi)^2/2
  + w^2/(2 beta) + q^2/(2 tau)
] dx

dE_hyp/dt = -integral (q/tau)^2 dx <= 0
```

The v1 formula evaluator uses a periodic skew-adjoint central derivative. It
therefore conserves the discrete integral of `C`, closes the semi-discrete
energy identity, and preserves the prepared constraint
`p - partial_x varphi = 0` at roundoff. It is not yet a validated time
integrator or an external numerical replication of the paper's benchmarks.

For the symmetric double well, the one-dimensional characteristic speeds are

```text
lambda_C = +/-sqrt([alpha + g''(C)]/tau)
lambda_aux = +/-sqrt(gamma/beta)
lambda_0 = 0
```

Strict hyperbolicity requires `alpha > 1`; `alpha = 1` only reaches the
degenerate boundary at `C = 0`. Mathematical hyperbolicity and a UET
relativistic light-cone condition are separate gates. At fixed parameters,
both speed families can be finite and can be constrained by
`max(abs(lambda)) <= c_hat`. Hyperbolicity alone does not enforce that bound.

The source's formal Cahn-Hilliard scaling is

```text
alpha = gamma^-1
tau = gamma^2
beta = gamma^2
```

so as `gamma -> 0` the two speed scales behave as

```text
abs(lambda_C) = O(gamma^-3/2)
abs(lambda_aux) = O(gamma^-1/2)
```

and diverge. The comparator therefore supplies a fixed-parameter finite-cone
regularization, while recovery of the parabolic Cahn-Hilliard equation is a
singular limit that is not uniformly subluminal. The quasistatic augmented
chemical potential converges to the repository's discrete Cahn-Hilliard
chemical potential with approximately first order in `1/alpha`, but this
spatial formula limit is not a covariant UET matter map.

This wave narrows the blocker from “no first-order phase-field comparator” to
the absence of a UET-native covariant derivation and a parameter policy that
keeps the physical approximation useful while all characteristics remain
uniformly inside the declared light cone. Closed-time-path/KMS transport
matching, dissipative Bianchi closure, curved 3+1 evolution, SI mapping,
external numerical replication, and physical validation remain blocked.
Topic 0.11 and Topic 0.19 status do not change, and complete-universe closure
remains unresolved.

### 5.4 Fixed-light-cone feasibility and covariant mapping readiness

The comparator's finite characteristic speeds can now be turned into exact
parameter inequalities, provided the amplitude domain is declared. For the
symmetric interval `|C| <= C_max`,

```text
g''(C) = 3 C^2 - 1
min[alpha + g''(C)] = alpha - 1
max[alpha + g''(C)] = alpha + 3 C_max^2 - 1
```

Thus strict hyperbolicity over the whole interval still requires
`alpha > 1`. Keeping both characteristic families inside a fixed normalized
cone `c_hat` is equivalent to

```text
tau >= (alpha + 3 C_max^2 - 1) / c_hat^2
beta >= gamma / c_hat^2
```

These are necessary and sufficient inequalities for the two speed formulas of
this normalized external comparator on the declared interval. They are not a
physical SI calibration and do not establish a covariant UET completion.

The inequalities also expose an exact incompatibility between two simultaneous
limits. Exact parabolic Cahn-Hilliard recovery asks for

```text
alpha -> infinity
tau -> 0
```

whereas the fixed-cone inequality forces

```text
tau_min >= (alpha + 3 C_max^2 - 1) / c_hat^2 -> infinity.
```

No common parameter sequence can satisfy both exact limits at fixed finite
`c_hat`. This is a normalized no-common-limit result for the declared
comparator, not a theorem that all causal phase-field completions are
impossible. The scientifically allowed choices are therefore to retain finite
relaxation and auxiliary dynamics, or to treat parabolic Cahn-Hilliard as a
late-time, low-wavenumber approximation rather than an exact all-scale law.

The external flux variable does admit one exact local algebraic map. With
constant positive `tau`, define

```text
J = q / tau.
```

Then the source equations

```text
partial_t C + partial_x(q/tau) = 0
partial_t q + partial_x(mu_aug) = -q/tau
```

become

```text
partial_t C + partial_x J = 0
tau partial_t J + J = -partial_x(mu_aug).
```

This matches the mobility-one local Maxwell-Cattaneo form in the conserved
current bridge. It does **not** yet match the physical state variables:

```text
external comparator C          != established UET Noether density
external auxiliary varphi      != UET Phi
external auxiliary varphi      != information or derived trace
local q/tau current-law map    != covariant UET derivation
```

At Wave 8 the remaining map was split into two evidence lanes. The classical
covariant lane had to:

1. declare whether the conserved variable is charge, mass, or another Noether
   density;
2. factor the coarse-graining/state map, identify every many-to-one layer, and
   derive the exact invertible hydrodynamic coordinate layer;
3. write the current law with a four-velocity and spatial projector;
4. exhibit non-negative entropy-current divergence; and
5. close stress-energy exchange with the dissipative Bianchi ledger in curved
   spacetime.

Section 5.5 closes item 1 as signed O(2) charge and closes only the affine
hydrodynamic part of item 2. It proves by counterexample that microscopic and
non-trivial coarse-graining layers are many-to-one. Items 3--5 remain open.

Only after that lane closes does a thermal stochastic claim additionally need
a closed-time-path action, dynamical KMS symmetry, and fluctuation-dissipation
matching. These requirements are source-audited against Jain and Kovtun,
*Schwinger-Keldysh effective field theory for stable and causal relativistic
hydrodynamics* ([DOI 10.1007/JHEP01(2024)162](https://doi.org/10.1007/JHEP01(2024)162),
[arXiv:2309.00511](https://arxiv.org/abs/2309.00511)), and Crossley,
Glorioso, and Liu, *Effective field theory of dissipative fluids*
([DOI 10.1007/JHEP09(2017)095](https://doi.org/10.1007/JHEP09(2017)095),
[arXiv:1511.03646](https://arxiv.org/abs/1511.03646)). The former supplies a
relativistic conserved-current/Maxwell-Cattaneo/entropy/SK-KMS comparator; the
latter supplies the broader CTP/local-KMS dissipative-EFT architecture. Neither
paper derives UET or identifies its variables.

The Wave 8 controller was therefore narrowed to
`noether_density_to_phase_field_order_parameter_map_missing`. The exact
coordinate result in section 5.5 supersedes that controller without turning
the compatibility declaration into a microscopic derivation. The exact
`epsilon_nc = 0` GR response-null branch remains unchanged, but this does not
decide whether the complete universe is open or closed. Global-universe
closure remains `UNRESOLVED`; Topic 0.11 and Topic 0.19 receive no status
promotion.

### 5.5 Factorized Noether-charge to phase-field state map

The state-map blocker is not one invertible microscopic transformation. It is
a chain of maps with different mathematical status:

```text
microscopic O(2) fields
    -> Noether current N^mu
    -> frame density n=-u_mu N^mu and spatial current j^mu
    -> declared coarse variables n_bar, j_bar
    <-> normalized hydrodynamic coordinates C, J
```

For polar matter variables

```text
chi = (A cos(theta), A sin(theta)),
N^mu = Z A^2 partial^mu(theta).
```

The microscopic map is many-to-one. A constant phase shift changes the
microscopic field but not the current, and different amplitude/phase-gradient
pairs can preserve the product `A^2 partial^mu(theta)`. A non-trivial cell
average is also many-to-one because distinct sub-cell profiles can have the
same average. Requiring `C` to reconstruct those discarded microscopic degrees
of freedom is therefore a category error, not a missing invertible formula.

The exact invertible layer begins only after a frame, coarse-graining rule,
reference density, and positive scales are declared:

```text
C = (n_bar - n_ref) / n_scale
J = j_bar / (n_scale L/T)

n_bar = n_ref + n_scale C
j_bar = (n_scale L/T) J.
```

At fixed scales, continuity is preserved exactly. With `t=T t_hat` and
`x=L x_hat`, the residuals satisfy

```text
R_hat = partial_t_hat C + partial_x_hat J
      = (T/n_scale) (partial_t n_bar + partial_x j_bar).
```

This closes a hydrodynamic state-coordinate map. It does not derive the
coarse-graining kernel, select the local rest frame dynamically, or identify
the signed O(2) charge with mass or particle number. Those interpretations
remain forbidden shortcuts in this wave.

The external hyperbolic phase-field comparator can now be connected at the
same coordinate level if, and only if, its `C` is explicitly declared to be a
normalized signed-charge coordinate and its local flux is declared by
`J=q/tau`. This is a compatibility declaration, not a microscopic derivation.
The external auxiliary `varphi` remains distinct from UET `Phi`, information,
and derived trace.

The symmetric double well also has an exact thermodynamic coordinate map. For

```text
g(C) = (C^2 - 1)^2 / 4
f(n_bar) = n_scale mu_scale g(C),
```

the conjugate chemical potential is

```text
df/dn_bar = mu_scale (C^3 - C),
```

so the local normalized coefficients are `a_matter=-1` and `b_matter=+1`.
This is a constitutive free-energy choice. The O(2) matter action has not yet
derived this equation of state, its equilibrium susceptibility, the gradient
coefficient, or the transport coefficients.

The distinction follows the standard external roles used here: Cahn and
Hilliard support a nonuniform composition/density free-energy functional
([DOI 10.1063/1.1744102](https://doi.org/10.1063/1.1744102)), while Hohenberg
and Halperin classify Model B as conserved-order-parameter dynamics
([DOI 10.1103/RevModPhys.49.435](https://doi.org/10.1103/RevModPhys.49.435)).
Neither source equates every conserved order parameter with a microscopic
Noether charge or derives the UET matter action.

The completed and open layers are therefore:

```text
signed O(2) conserved-variable declaration       PASS
fixed-scale n_bar,j_bar <-> C,J affine map       PASS
continuity/current scale map                     PASS
microscopic reconstruction from C               NO-GO (many-to-one)
external C as signed-charge coordinate           PASS only as declared role
equation of state from covariant O(2) action     BLOCKED (controlling)
covariant coarse-graining/hydrodynamic matching  BLOCKED
susceptibility and transport matching            BLOCKED
entropy-current/dissipative-Bianchi completion   BLOCKED
```

The controller is narrowed to
`noether_charge_equation_of_state_and_covariant_transport_matching_missing`.
Derived trace remains downstream-only and cannot alter this state map or the
physical evolution. The exact `epsilon_nc=0` GR response-null branch is
unchanged. Global-universe closure remains `UNRESOLVED`, and this coordinate
result does not promote Topic 0.11 or Topic 0.19.

### 5.6 Finite-density O(2) EOS and T=0 superfluid constitutive layer

Wave 10 fixes the homogeneous finite-density branch of the existing O(2)
matter action without replacing the normalized phase-field potential. With
`chi=A exp(i theta)`, `theta=-mu*t`, and

```text
m_eff^2(Phi)=m^2-epsilon_nc*h*(Phi-Phi_*)
q=Z*mu^2-m_eff^2,
```

the stable condensed branch `q>0` gives

```text
A_*^2=q/lambda
p=q^2/(4*lambda)
n=Z*mu*q/lambda
epsilon=mu*n-p
chi=Z*(3*Z*mu^2-m_eff^2)/lambda
c_s^2=q/(3*Z*mu^2-m_eff^2).
```

The canonical free energy is obtained from `f=mu*n-p` by selecting the unique
stable root of

```text
Z^2*mu^3-Z*m_eff^2*mu-lambda*n=0
```

with the sign of `mu` fixed by the signed O(2) charge. The `q=0` phase edge is
reported separately because its derivatives are one-sided. The reciprocal
response derivatives from the same action are

```text
(partial p/partial Phi)_mu=+epsilon_nc*h*A_*^2/2
(partial f/partial Phi)_n=-epsilon_nc*h*A_*^2/2.
```

On the preregistered normalized comparison domain `-1<=C<=1`, the exact
canonical EOS and the existing symmetric double well have relative residual
`1.0`, above the acceptance threshold `1e-3`. The double well therefore
remains a constitutive comparator; no fit or silent replacement is allowed.
The homogeneous calculation also does not derive `kappa_C`.

For `xi_mu=nabla_mu theta+A_mu` and `X=-xi_mu*xi^mu`, the T=0 action-derived
ideal sector is

```text
f_s=Z*(Z*X-m_eff^2)/lambda
N^mu=f_s*xi^mu
T^{mu nu}=f_s*xi^mu*xi^nu+p*g^{mu nu}.
```

This is a pure-superfluid constitutive layer. It does not supply a
finite-temperature normal component. The dissipative longitudinal control
requires explicit Kubo records and checks a positive-semidefinite Onsager
matrix together with `D=sigma_reg/chi` and `D/tau<=1`. Verifier coefficient
values are opt-in synthetic controls only; physical runs have no defaults.

The completed and open Wave 10 layers are:

```text
tree-level finite-density O(2) EOS              PASS
stable signed canonical inversion               PASS
response reciprocity                            PASS
T=0 covariant pure-superfluid current/stress    PASS
local longitudinal entropy/causal control       PASS (simulation-only)
symmetric double-well reduction                 REJECTED as derived EOS
physical Kubo coefficient evidence              BLOCKED (controlling)
finite-temperature normal component             BLOCKED
full superfluid transport and SK/KMS closure    BLOCKED
covariant coarse graining and curved 3+1 solver BLOCKED
```

The controller is narrowed to
`physical_kubo_coefficient_evidence_and_curved_3p1_solver_missing`. This does
not promote Topic 0.11, Topic 0.19, physical GR validation, or the unresolved
global-universe closure question.

## 6. GR closed-limit contract

The exact null limit is

```text
epsilon_nc -> 0
Q^nu -> 0
open influence kernel -> 0
Phi -> Phi_*
nabla Phi -> 0
Pi -> 0
```

and must yield

```text
G_mu_nu + Lambda g_mu_nu = kappa_E T_m_mu_nu
```

Required implementation properties:

- no division by `epsilon_nc`;
- arbitrary response inputs make no contribution when `epsilon_nc = 0`;
- the GR residual is identical component by component, not merely close after
  fitting;
- a constant equilibrium density is either zero or mapped explicitly to
  `Lambda_eff`;
- the GR limit remains valid before and after the later nonrelativistic
  reduction.

## 7. Non-closed causal extension target

Ordinary single-copy conservative variation is not sufficient for generic
retarded dissipation. The next parent layer will therefore use a causal
influence-functional or closed-time-path contract:

```text
S_eff[+, -] = S_cons[+] - S_cons[-] + S_IF[+, -]
```

The physical balance must take one of two explicit branches:

1. **Exchange-completed branch (primary):**
   `nabla T_m = Q`, `nabla T_UET = -Q`; the observed sector is non-closed while
   the modeled total remains Bianchi-consistent.
2. **Global-nonconservation branch (deferred/high risk):** requires an explicit
   boundary, external sector, broken diffeomorphism contract, or alternative
   geometry. It may not be inferred from branch 1.

The derived trace target is

```text
R(x) = integral G_ret(x, x') [nabla_mu s^mu](x') d^4x'
```

and remains outside the physical equation graph.

## 8. Reduction to the existing matter-space model

After the covariant and open-sector gates pass, a documented 3+1, weak-field,
slow-motion, and near-equilibrium reduction must recover the normalized
`matter_space_coupled_v1` structure or identify exactly why it does not.

The present variables cannot be promoted directly:

- frame-dependent density `C` must map to a covariant matter scalar or current,
  such as a scalar pilot field or `n = sqrt(-N_mu N^mu)`;
- `Phi` and `Pi` must arise from the covariant response state;
- normalized coefficients require an explicit natural-unit and later SI map;
- the existing causal-leakage failure remains a blocker for physical
  propagation language.

## 9. Verification program

### Core gates

- symbolic GR closed-limit residual: exactly zero;
- deterministic numeric closed-limit residual: `<= 1e-12`;
- stable ordered reference and positive local Hessian;
- symmetric response stress tensor;
- action-density mass dimension: `4` in the natural-unit lane;
- metric-equation residual mass dimension: `2`;
- no hidden division by `epsilon_nc`;
- Bianchi/exchange balance: open until the causal sector exists;
- characteristic and ghost gates: open until PDE principal symbols exist;
- derived trace backreaction: forbidden.

### Gravity gates

After the parent passes: Minkowski, Schwarzschild/de Sitter/FLRW closed
solutions, Newtonian/PPN reduction, light bending, perihelion, Shapiro delay,
redshift, gravitational-wave propagation, equivalence principle, and
short-range constraints.

### Empirical model comparison

Every application compares the nested pair `epsilon_nc = 0` and
`epsilon_nc != 0`. Parameter policy and holdout rows are locked before the
claim-bearing run. A fit on the same rows used for evaluation is diagnostic
only.

## 10. Falsification rules

The program is reduced or rejected in a lane if:

- GR appears only after manual term deletion or singular parameter tuning;
- the metric equation violates its covariant balance identity;
- a propagating response has ghosts, gradient instability, or superluminal
  characteristics outside its declared EFT domain;
- the entropy or exchange ledger cannot close;
- the response works only when derived trace `R` is fed back;
- external constraints force `epsilon_nc = 0` in all independent lanes;
- a claimed effect disappears on holdout or under resolution refinement; or
- the formulation is observationally identical to an existing theory while
  retaining an unsupported novelty claim.

## 11. Topic dependency order

1. `docs/core` and topic `0.19`: covariant parent and GR closed limit.
2. Topics `0.10` and `0.13`: causal constitutive and thermodynamic controls.
3. Topic `0.11`: nonrelativistic internal diagnostic only.
4. Topics `0.12` and `0.23`: equilibrium-density, units, and cross-scale policy.
5. Topics `0.1` and `0.26`: galaxy and dynamic-frame tests after gravity gates.
6. Particle/Dirac topics: deferred until local Lorentz, spinor, current, and
   CPT contracts exist.

## 12. Claim boundary

Allowed now:

- `GR correspondence hypothesis`
- `candidate non-closed effective matter-spacetime sector`
- `implemented one-dimensional nonrelativistic prototype`
- `derived trace with no backreaction`

Blocked now:

- `the universe is proved open`
- `Einstein equations derived from UET`
- `UET is Lorentz invariant`
- `UET validates GR`
- `space response is antimatter, ether, or a particle`
- `dark matter replaced`

## 13. Primary comparison literature

- T. Jacobson, *Thermodynamics of Spacetime: The Einstein Equation of State*,
  <https://arxiv.org/abs/gr-qc/9504004>.
- C. Eling, R. Guedens, and T. Jacobson, *Non-equilibrium Thermodynamics of
  Spacetime*, <https://arxiv.org/abs/gr-qc/0602001>.
- C. R. Galley, *The Classical Mechanics of Non-conservative Systems*,
  <https://arxiv.org/abs/1210.2745>.
- M. Crossley, P. Glorioso, and H. Liu, *Effective Field Theory of Dissipative
  Fluids*, <https://arxiv.org/abs/1511.03646>.
- T. Harko et al., *f(R,T) gravity*, <https://arxiv.org/abs/1104.2669>.
- T. Jacobson and D. Mattingly, *Gravity with a Dynamical Preferred Frame*,
  <https://arxiv.org/abs/gr-qc/0007031>.

These are comparison frameworks and constraints on method choice. They are not
evidence that UET is correct.
