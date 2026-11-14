# Relational Organization and Persistence-Energy Diagnostic

Status: `CANDIDATE_PRINCIPLE` / `INTERNAL_DIAGNOSTIC` / `SIMULATION_ONLY` / `CONSTITUTIVE_ANSATZ`

Canonical principle: UET-PRINCIPLE-001 ? หลักการจัดสรรพลังงานร่วมเพื่อการดำรงอยู่ของระบบ.
See RESOURCE_PERSISTENCE_PRINCIPLE_SPEC.md for the named principle and claim boundary.

## Research question

Can the idea that a system's behaviour consumes an available resource be written
without identifying the relational coordinate `C` with energy itself?

This first diagnostic treats `C(t)` as a prescribed dimensionless relational or
organizational trajectory and keeps the resource in a separate ledger:

\[
P_C=\eta_C\left|\frac{dC}{dt}\right|^2\geq0,
\]

\[
E_{\mathrm{available}}(t+\Delta t)
=E_{\mathrm{available}}(t)
+(J_{\mathrm{in}}-J_{\mathrm{out}}-P_C)\Delta t.
\]

The first relation is a Rayleigh-type dissipative constitutive ansatz. It is a
standard modelling form for a generalized coordinate, not a derivation from the
UET master equation and not a universal law that every physical realization of
`C` must obey.

## Ontology

| Quantity | Role | What it is not |
| --- | --- | --- |
| `C(t)` | prescribed relational/organizational coordinate | energy, force, mass, or substance |
| `P_C` | modelled rate of resource expenditure along the path | a measured universal dissipation law |
| `E_available` | separate normalized resource ledger | `C` or the full physical energy of the universe |
| `t_persist` | first time the ledger reaches the declared sustain threshold | proof of biological survival or natural selection |

The phrase “จัดการพลังงานได้ดี” is therefore represented by a path-level
diagnostic: two trajectories can have the same endpoints but different integrated
costs under the declared ansatz. The result concerns the comparator's cost rule,
not an established UET prediction.

## Synthetic control

The verifier compares two prescribed paths with equal amplitude and equal
endpoints:

1. low-activity path: one oscillation over the horizon;
2. high-activity path: eight oscillations over the same horizon.

With the same initial resource and no external input, the high-activity path has a
larger \(\int P_Cdt\) and reaches the sustain threshold sooner. This is a
diagnostic of path dependence in the declared Rayleigh comparator.

## Claim boundary and next step

- This does not derive `C` from thermodynamics.
- This does not prove that all behaviour has a quadratic energy cost.
- This does not establish a new energy reservoir, force, mass, or field.
- The normalized ledger is not SI energy accounting.
- No external data, fit, galaxy model, or biological claim is used.

The next hardening step is to connect a physical lane's measured work, heat flux,
or entropy production to the path cost, then test whether the mapping survives a
baseline and holdout protocol. Until then, the correct status remains
`CONSTITUTIVE_ANSATZ` and `DIAGNOSTIC_ONLY`.
