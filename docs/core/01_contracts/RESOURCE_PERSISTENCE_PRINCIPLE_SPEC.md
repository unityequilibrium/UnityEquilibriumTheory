# UET Resource Persistence Principle

Status: CANDIDATE_PRINCIPLE / HEURISTIC_BRIDGE / SIMULATION_ONLY

## Canonical name

Thai: หลักการจัดสรรพลังงานร่วมเพื่อการดำรงอยู่ของระบบ
English: Cooperative Energy Allocation for System Persistence Principle
Identifier: UET-PRINCIPLE-001

The canonical name uses "persistence capacity" rather than "potential energy" at
the universal level. Potential energy has a specific meaning in physics, and UET
does not yet have one mapping from its abstract coordinate to potential energy in
all lanes. A lane may use potential-energy terminology only after it derives the
mapping and units.

## Principle statement

The system does not intend to survive and does not choose an energy strategy as a
conscious player. The principle is a result-based explanation:

> Patterns that allocate resources associated with behaviour and interaction in a
> mutually compatible way lose persistence capacity more slowly and therefore
> remain observable for longer. Patterns that exhaust the resources needed to
> maintain their organization change phase, degrade, or cease to exist as the
> same system.

Optimization here means emergent persistence or dynamical selection, not a goal
held by matter.

## Causal chain

matter and interaction
-> behaviour
-> resource use and allocation
-> transition or failure probability
-> filtering of persistent patterns
-> collective behaviour C
-> system persistence capacity

C is a relational collective-behaviour coordinate. It is not automatically mass,
energy, force, or a substance.

## First operationalization

The current diagnostic prescribes a relational/organizational trajectory C(t) and
keeps its resource ledger separate:

P_C = eta_C |dC/dt|^2 >= 0

dE_available/dt = J_in - J_out - P_C

t_persist = inf{t : E_available(t) <= E_sustain}

The formula statuses are:

| Relation | Status |
|---|---|
| P_C | Rayleigh-type constitutive ansatz / heuristic bridge |
| resource ledger | checked local bookkeeping identity in the normalized lane |
| persistence threshold | benchmark criterion / open interpretation |

This does not derive the physical origin of C and is not a total-universe energy
conservation law.

## Current research result

The existing diagnostic compares C paths with equal endpoints but different activity.
Under the declared path-cost ansatz, the high-activity path has a larger cost and
reaches the sustain threshold first, while the normalized ledger closes within
numerical tolerance.

The supported statement is limited to:

> Under the Rayleigh-type path-cost ansatz, a more rapidly changing behaviour path
> can consume a normalized resource ledger faster even when its endpoints match.

This is not a derivation of thermodynamics, Darwinian selection, or a universal law
of persistence.

## Next physical research step

Move from prescribed C(t) to one declared physical lane containing:

1. an explicit interaction or state-transition mechanism;
2. a work, heat, flux, or entropy-production observable;
3. units and boundary conditions;
4. transition/failure rates with no intentionality;
5. a coarse-graining map from lower-level dynamics to C; and
6. a baseline and holdout policy that does not fit the principle back to the result.

If the path cost does not map to a measured physical quantity, this principle remains
a mathematical or constitutive comparator.

## Claim boundary

Allowed:

- candidate resource-constrained collective dynamics
- candidate emergent persistence principle
- simulation-only path-cost diagnostic
- candidate collective-behaviour coordinate C

Not allowed:

- matter has an intention or goal to survive;
- C is universal mass or energy;
- potential-energy preservation is a universal UET law;
- the principle is derived from first principles;
- the simulation is external validation or proof.

## Controlling blocker

map_behavior_path_cost_to_measured_work_heat_or_entropy_in_one_declared_physical_lane

Current controlling artifacts:

- docs/core/artifacts/resource_persistence_principle_contract.json
- docs/core/artifacts/persistence_energy_diagnostic_verification.json

## Dynamic-selection control result ? 2026-08-08

The interaction-selection realization now has a confounding control. The
original cooperative/conflict pair changed both interaction structure and
resource-cost inputs, so its persistence contrast could not be attributed to
`C` alone.

With the same interaction matrix and `cost_weight=0`, changing behavior and
maintenance costs leaves the full interaction-derived `C` trajectory
unchanged while changing the available-resource ledger. With the same cost
vectors and `cost_weight=0`, changing the interaction matrix changes `C` while
leaving the resource ledger unchanged. A zero-cost, zero-input control keeps
the ledger constant.

This supports the narrower statement:

> The comparator contains two separable mechanisms: interaction-derived
> collective compatibility and declared resource depletion. The current
> evidence does not identify them as one physical quantity.

The result strengthens falsifiability and prevents the principle from being
used as an explanation of persistence merely because a cooperative example
lasts longer. The next physical step is to source-lock one material lane in
which behavior/maintenance costs can be measured as work, heat, entropy
production, transition rate, or failure rate. Until that map exists, the
principle remains a normalized, non-agentic, simulation-only comparator.
