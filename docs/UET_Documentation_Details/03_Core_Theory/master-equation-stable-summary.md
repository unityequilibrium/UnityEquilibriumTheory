---
title: "Master Equation Stable Summary"
description: "A conservative reading of the historical seven-term candidate template."
---

# Master Equation Stable Summary

This note promotes the most stable parts of the legacy master-equation material into the
current documentation layer.

It is intentionally conservative.

Its job is to state what the project is trying to use as its core equation structure,
without importing the strongest historical wording unchanged.

## Current ontology correction

The symbol `C` must now be read first as an **abstract relational variable for interaction
and system behaviour**. It is not universally mass, density, energy, information, or a
substance. A mass-density, charge, order-parameter, heat, or observer lane may define an
explicit mapping from `C` to a standard physical quantity, but that mapping is not supplied by
the symbol itself.

See [C as a Relational Interaction Variable](./relational-C-and-physical-mapping.md) for the
current ontology, condition/constraint/necessity distinction, and physical-observable gates.

## Historical seven-term candidate template

The following functional records the historical template, not a closed or validated
universal equation. For active lane contracts and blockers, see the
[Foundation Status Aggregate](../../core/01_contracts/UET_FOUNDATION_STATUS_AGGREGATE.md).

$$
\Omega[C,I,J] =
\int d^3x \left[
V(C)
+ \frac{\kappa}{2}|\nabla C|^2
+ \beta C \cdot I
+ \gamma_J (J_{in} - J_{out}) \cdot C
+ W_N |\nabla \Omega|
+ \beta_U V_{game}
+ \lambda \sum (C_i - C_j)^2
\right]
$$

## Intended interpretation

The project uses this functional as a candidate "single framework" for describing:

- equilibrium and disequilibrium
- spatial variation and smoothing cost
- information-energy coupling
- exchange with surroundings
- persistence or action-like drive
- multi-agent or game-like interaction
- multi-layer coherence across subsystems

This does **not** automatically mean every term is already first-principles closed in the
current repository.

It means this is the stable legacy form that motivated many later topic-specific
implementations.

## The seven historical terms

| Term | Symbol | Intended role | Legacy source language |
| :-- | :-- | :-- | :-- |
| Potential | `V(C)` | cost or preference over relational interaction structure | Landau-Ginzburg-style comparator; units depend on lane |
| Gradient | `(\kappa / 2)|\nabla C|^2` | penalty for sharp variation of the relational coordinate | gradient penalty; not automatically kinetic energy |
| Coupling | `\beta C · I` | coupling between two declared model sectors | information interpretation is lane-specific; not a conversion law |
| Exchange | `\gamma_J (J_in - J_out) · C` | semi-open system exchange | thermodynamic exchange |
| Natural will | `W_N |\nabla \Omega|` | persistence / descent / action-like drive | action-principle-inspired term |
| Game | `\beta_U V_game` | competition or coordination in multi-agent systems | Nash/game layer |
| Coherence | `\lambda \sum (C_i - C_j)^2` | cross-layer synchrony | layer coupling / multi-scale unity |

## What should be considered stable

These points are stable enough to carry forward from legacy:

- the theory was organized around a multi-term functional rather than a single isolated
  algebraic trick
- the project explicitly tried to combine thermodynamic, informational, geometric, and
  interaction terms in one structure
- the 7-term view shaped the way later topic work was interpreted
- the core variable was intended to describe system-level relations, even though older notes
  used inconsistent capacity/mass/information labels

## What should still be treated cautiously

These points should **not** be overpromoted yet:

- that every term has already been fully derived from first principles
- that all parameter values in legacy notes remain canonical today
- that every topic in the repo implements the full 7-term form directly
- that `C` has one universal physical realization across all topics
- that `\beta C I` means matter or interaction is converted into information

The stable claim is weaker and safer:

**The 7-term functional is the main legacy template for the intended UET core structure.**

## Related promoted notes

- [the-master-equation.md](./the-master-equation.md)
- [term-by-term-stable-summary.md](./term-by-term-stable-summary.md)
- [relational-C-and-physical-mapping.md](./relational-C-and-physical-mapping.md)
- [parameter-registry-stable-summary.md](./parameter-registry-stable-summary.md)
- [correspondence-and-reduction.md](./correspondence-and-reduction.md)

## Legacy sources behind this note

- `LEGACY_REPORTS/01_Core_Theory/MASTER_EQUATION.md`
- `LEGACY_REPORTS/01_Core_Theory/Term-by-Term.md`
