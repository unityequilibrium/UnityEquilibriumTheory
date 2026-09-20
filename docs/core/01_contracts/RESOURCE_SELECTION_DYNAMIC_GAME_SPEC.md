# Resource Selection Dynamic-Game Comparator

Status: CANDIDATE_NORMALIZED_DYNAMIC_SELECTION / SIMULATION_ONLY

This lane formalizes the persistence hypothesis as a non-agentic dynamical
selection comparator. It does not assign intention, consciousness, or a goal to
matter.

## State and interaction

Let p_i(t) be the normalized occupancy of interaction states. The interaction
matrix A_ij is an explicit normalized compatibility/payoff comparator. The
collective coordinate is derived from the interaction state:

    C_collective = sum_i,j p_i A_ij p_j

The state evolution is the standard replicator-style relation:

    dp_i/dt = p_i (f_i - sum_j p_j f_j)

with

    f_i = s sum_j A_ij p_j - w c_i

where s and w are declared normalized comparator weights and c_i is the
behavior-related cost of state i.

This relation is a constitutive/evolutionary-game comparator. It is not a
derivation that nature has an objective function.

## Resource ledger

    dE_available/dt =
        J_in - J_out - P_behavior - P_maintenance

    P_behavior = sum_i p_i c_i
    P_maintenance = sum_i p_i m_i

Persistence is defined only as the benchmark event

    t_persist = inf{t : E_available(t) <= E_sustain}

The ledger does not identify E_available with SI energy until a physical lane
maps the costs to work, heat, or entropy production.

## Research question

For identical initial resource and initial state distributions, do interaction
structures with greater collective compatibility and lower resource cost produce
longer persistence without adding an intentional optimizer?

The answer is a falsifiable comparator result. It is not evidence for universal
Darwinian, biological, cosmological, or particle dynamics.

## Required gates

- simplex preservation and non-negative probabilities
- ledger closure without clipping
- deterministic configuration and no fitting
- C is derived from interaction state, not relabelled mass
- persistence ordering survives dt refinement
- physical mapping to work, heat, or entropy remains open

## 2026-08-08 - Control and identifiability result

The original cooperative/conflict comparison changed the interaction matrix and
both cost vectors at the same time. It therefore could show a persistence
ordering in the declared comparator, but it could not identify whether the
ordering came from collective compatibility `C`, declared resource costs, or
both.

The verifier now includes three controls:

1. **Same interaction, different costs, zero selection-cost weight.** The
   probability and `C` histories are identical, while the resource ledger
   changes. The measured `C` residual is `0.0`; the low-cost and high-cost
   final resources are approximately `0.65` and `-2.50`.
2. **Same interaction, zero costs and zero net input.** The resource remains
   constant with a range of `0.0`.
3. **Same costs, different interaction matrices, zero selection-cost weight.**
   `C` changes by `1.15`, while the final resource residual is `0.0`.

All control gates pass in the deterministic normalized audit. The result is a
separation of outputs, not a causal proof that `C` itself consumes energy or
creates persistence. In this lane, `C` is interaction-derived and the ledger
is depleted by explicitly declared behavior/maintenance costs. A physical
interpretation requires a separate map from those costs to measured work,
heat, entropy production, transition rate, or failure rate.

The dynamic-game lane therefore remains `INTERNAL_DIAGNOSTIC` and
`SIMULATION_ONLY`; no intentional optimizer, mass interpretation, SI energy
claim, or universal Darwinian/cosmological law is introduced.

## Physical-cost mapping contract - 2026-08-08

The next lane is now an explicit opt-in interface:

    Q_J = alpha_b*W_behavior + alpha_m*W_maintenance
    Delta_S_bath_J_per_K = Q_J/T_bath_K

`alpha_b` and `alpha_m` have units of joules per normalized work and must be
independently derived or source-locked. The new contract rejects an incomplete
record, a fitted record, or a record without uncertainty, provenance, and a
measurement-operator identifier. Its deterministic fixture is marked
`TEST_ONLY` and is not a material calibration.

The current audit is `PASS_WITH_BLOCKED_INDEPENDENT_CALIBRATION`: the SI
conversion interface and unit algebra are explicit, but no physical heat,
calorimetry, heat-flux, entropy, or persistence prediction is promoted. The
next experiment must supply one material lane and a holdout that was not used
to choose either scale.

## Mapped control result - 2026-08-08

The dynamic-game controls were also passed through the `TEST_ONLY` dimensional
map. With the same interaction and different declared costs, the `C` residual
remains `0.0` and the mapped heat difference has magnitude `7.2 J` under the
fixture scales. With the same costs and different interaction matrices, the
`C` contrast is `1.15` while the mapped heat residual is `0.0`.

This is an algebraic consistency result: the cost map preserves the separation
between interaction-derived `C` and the ledger's declared cost channels. The
fixture values are not material constants, not fitted values, and not external
heat evidence.
