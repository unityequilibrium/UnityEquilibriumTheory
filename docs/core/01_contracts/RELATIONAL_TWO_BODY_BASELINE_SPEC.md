# Relational Two-Body Baseline

Status: `INTERNAL_CHECKED_COMPARATOR` / `SIMULATION_ONLY`

This package is the next foundation step after locking `C` as a relational interaction
coordinate. It is deliberately a standard Newtonian comparator. It does not claim that UET
has derived Newtonian gravity, mass, or a universal physical law.

## Research question

Can the current ontology express a two-body relation in which:

1. `C` represents relational interaction structure;
2. that structure maps to a standard interaction potential;
3. the potential produces force and acceleration through standard mechanics;
4. mass remains a separate inertial/amplitude parameter; and
5. a finite-signal observer receives a record of an earlier source event?

The key test is not whether a curve can be fit. It is whether the layers remain distinct and
reproduce the declared standard baseline.

## Locked normalized comparator

The code uses two-dimensional normalized units. `G`, masses, distances, time, and signal speed
are code-unit inputs, not SI constants.

For two bodies `A` and `B`, define

$$
\mathbf r = \mathbf x_A-\mathbf x_B,
\qquad r=|\mathbf r|,
\qquad C_{AB}=-\frac{r_0}{r}.
$$

Here `C_AB` is a dimensionless relational coordinate normalized by a reference separation
`r_0`. It is a chosen correspondence map for the comparator, not a first-principles UET
derivation.

The standard counterpart is

$$
U_{AB}=-\frac{Gm_Am_B}{r}
=U_0 C_{AB},
\qquad
U_0=\frac{Gm_Am_B}{r_0}.
$$

The force and acceleration remain standard:

$$
\mathbf F_A=-\nabla_{\mathbf x_A}U_{AB},
\qquad
m_A\mathbf a_A=\mathbf F_A,
\qquad
\mathbf F_B=-\mathbf F_A.
$$

This deliberately places the masses in the standard counterpart and not in the definition of
`C`.

## Observer layer

For a fixed observer at `x_O` and a finite comparator signal speed `u`, a source event at
`t_e` is received at

$$
t_o=t_e+\frac{|\mathbf x_A(t_e)-\mathbf x_O|}{u}.
$$

The received record contains the source state at `t_e`. It must not be silently labelled as the
source state at `t_o`.

The implementation reports both:

- `received_position_a`: the delayed record;
- `source_position_at_arrival`: the later source state at the arrival time.

This is a measurement-layer correspondence, not a claim that all physical traces are merely
observer-relative.

## Verification gates

The deterministic audit checks:

- exact `C -> U` reconstruction in the declared normalized map;
- exact force from the derivative of `U(C)` against the direct Newtonian force;
- bounded energy drift under velocity-Verlet integration;
- equal-and-opposite force and momentum conservation;
- Galilean common-boost invariance of relative `C`;
- positive finite observation delay and a distinct source state at arrival;
- mass-scale separation: the same geometry-only `C` can coexist with a changed potential/force
  amplitude when masses change.

The numerical thresholds are implementation gates for this comparator only. Passing them does
not promote the UET ontology to a physical theory.

## What this establishes

If the audit passes, we have an internally reproducible correspondence package showing that a
relational `C` coordinate can be connected to a standard two-body interaction without redefining
`C` as mass. It also shows where mass enters the standard equation.

It does **not** establish any of the following:

- `C` is baryonic mass density;
- UET derives `G` or Newtonian gravity;
- a galaxy rotation model is ready;
- the observer record is a new physical field;
- the finite-signal comparator is already Lorentz covariant.

## Next dependency

After this comparator, choose one explicit application lane:

1. a mass-density mapping `C -> rho` for galaxy work; or
2. a constitutive interaction mapping `C -> U_int/F_int` for a non-gravitational system.

The mass-density lane must add a dimensional map, a source/measurement operator, uncertainty,
and a holdout protocol before any galaxy fit. The current comparator alone cannot choose between
these lanes.

Implementation: [relational_two_body_baseline.py](./relational_two_body_baseline.py)

Audit: `docs/scripts/audit/audit_relational_two_body_baseline.py`
