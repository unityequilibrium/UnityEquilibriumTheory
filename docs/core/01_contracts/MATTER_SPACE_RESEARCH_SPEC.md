# UET Matter-Space Response Research Specification

**Status:** implemented normalized prototype / physical interpretation blocked

This specification separates physical evolution from a derived record of past
change. It is an opt-in research lane and does not alter the legacy UET
potential or default operator.

## 1. Ontology contract

| Symbol | Role | Independent state? | Meaning in v1 |
| --- | --- | --- | --- |
| `C` | matter/structure state | yes | Density-like conserved variable or non-conserved order parameter, selected per lane. |
| `Phi` | effective space response | yes | Signed departure from the ordered reference `Phi = 0`; not information or a metric tensor. |
| `Pi = partial_t Phi` | space-response rate | yes | Inertial/memory state paired with `Phi`. |
| `sigma` | dissipation source | no | Non-negative quantity derived from the physical equations. |
| `R = I_trace` | causal record | no | Retarded functional of `sigma`; it never feeds back into v1 dynamics. |
| `J_C` | matter drive | external input | Must integrate to zero in the closed conserved-matter lane. |
| `J_Phi` | space-subsystem drive | external input | Open-system drive whose work is reported in the ledger. |

`Phi = 0` means the maximally ordered reference used by this effective model.
It does not mean empty space. Positive or negative `Phi` is a signed response;
neither sign is identified with matter, antimatter, positrons, neutrinos, or
any particle species.

## 2. Candidate functional

```text
Omega[C,Phi] = integral [
    a_C/2 C^2 + b_C/4 C^4 + kappa_C/2 |grad C|^2
  + a_Phi/2 Phi^2 + b_Phi/4 Phi^4 + kappa_Phi/2 |grad Phi|^2
  - g/2 C^2 Phi
] dx
```

The positive quartic coefficients make the candidate polynomial bounded from
below. The coupling sign convention makes matter/structure source a response
of `Phi`; it is a constitutive choice, not a first-principles spacetime
derivation.

```text
mu_C   = a_C C + b_C C^3 - kappa_C laplacian(C) - g C Phi
mu_Phi = a_Phi Phi + b_Phi Phi^3 - kappa_Phi laplacian(Phi) - g/2 C^2
```

These functions must be implemented as one exact variational pair. The legacy
`potential_V()` and `potential_derivative()` remain unchanged and are recorded
as a separate alignment warning.

## 3. Dynamics

Closed conserved-matter lane:

```text
partial_t C = M_C laplacian(mu_C) + J_C
integral J_C dx = 0
```

Non-conserved control lane:

```text
partial_t C = -M_C mu_C + J_C
```

Effective space response:

```text
partial_t Phi = Pi
tau_Phi partial_t Pi + Pi = -M_Phi mu_Phi + J_Phi
```

The first implementation is normalized and one-dimensional. `periodic` and
finite-volume `zero_flux` boundaries are allowed. Unsupported dimensions,
unit lanes, or ambiguous legacy state inputs must fail explicitly.

## 4. Energy and dissipation ledger

```text
E = Omega + tau_Phi/(2 M_Phi) integral Pi^2 dx
```

For periodic or zero-flux boundaries without external drive:

```text
dE/dt = -integral (sigma_C + sigma_Phi) dx <= 0
```

where

```text
sigma_C = M_C |grad mu_C|^2       # conserved lane
sigma_C = M_C mu_C^2              # non-conserved lane
sigma_Phi = Pi^2 / M_Phi
```

With additive sources, the normalized open ledger also reports

```text
P_C   = integral mu_C J_C dx
P_Phi = integral Pi J_Phi / M_Phi dx
```

No term may be called joules, heat, entropy, or curvature until a lane-specific
SI contract closes.

## 5. Derived trace rule

```text
R(x,t) = G_ret * (sigma_C + sigma_Phi)
```

The trace may be enabled or disabled as a diagnostic. Given the same complete
physical state and inputs, enabling trace calculation must not change `C`,
`Phi`, or `Pi`. A different trace history with the same complete state must
also leave the future physical evolution unchanged.

History dependence enters through the physical `Phi, Pi` state. The history
buffer used for `R` is a computational cache only.

## 6. Public interface target

```text
MatterSpaceConfig:
  a_matter, b_matter, kappa_matter, mobility_matter
  a_space, b_space, kappa_space, mobility_space, tau_space
  coupling_g
  matter_dynamics = conserved | nonconserved
  boundary_condition = periodic | zero_flux
  unit_lane = normalized
  stability_safety
  ledger_tolerance

MatterSpaceState:
  C
  space_response
  space_rate
```

`UETStepResult` retains its existing first five positional fields and appends
optional `space_response` and `space_rate` fields. The new operator is named
`matter_space_coupled_v1` and remains opt-in.

## 7. Numerical contract

- 1D finite-volume gradient/Laplacian operators preserve the discrete integral.
- Heun/RK2 is used with a preflight stability bound; field clipping is forbidden.
- The preflight includes the conserved fourth-order stiffness, damping time,
  and `v_Phi = sqrt(M_Phi kappa_Phi / tau_Phi)`.
- Non-finite state, unsupported shape, invalid coefficient, or non-zero net
  conserved source raises an explicit error.
- `unit_lane = si` is rejected in v1.
- Adiabatic reduction requires `tau_Phi`, the relaxation time, and the spatial
  response length to vanish together; `tau_Phi -> 0` alone is insufficient.

## 8. Falsification and claim boundary

The lane fails if its effect is below discretization error, the energy ledger
cannot close, the response precedes its declared causal control, numerical
stability needs clipping, or the model only works when `R` is fed back as a
new mass/energy state.

Allowed wording:

- candidate normalized effective model
- effective space-response variable
- derived causal trace observable
- internal diagnostic or simulation-only control

Blocked wording:

- derived spacetime geometry
- information as a new substance
- ether identification
- antimatter/positron/neutrino derivation
- external validation from synthetic controls
- galaxy or dark-matter replacement

## 9. GR correspondence handoff

This one-dimensional model is not the covariant gravity parent. Its role in the
new GR correspondence program is a possible nonrelativistic constitutive limit
that must be derived later rather than assumed.

The repository now separates four statements that were previously easy to
conflate:

- conserved matter amount means the declared integral/current is preserved;
- matter stress-energy exchange requires a future covariant current `Q^nu`;
- the GR closed-response limit means all additional UET response terms vanish;
- whether the complete universe is globally open or closed remains unresolved.

The controlling specification is
[`UET_GR_NONCLOSED_RESEARCH_SPEC.md`](UET_GR_NONCLOSED_RESEARCH_SPEC.md).
Until its covariant parent and exact-limit verifier exist, this implementation
supports no Einstein-equation, Lorentz, global-open-universe, or spacetime
