# Matter-Space Phase Coupling Pilot

## Status

`INTERNAL_DIAGNOSTIC / SIMULATION_ONLY / CORE_DEPENDENCY_BLOCKED`

This lane tests the normalized one-dimensional `matter_space_coupled_v1`
operator as a phase/collective-behaviour diagnostic. It is separate from the
Topic 0.11 structure-factor controller and cannot promote a critical exponent,
universality, material claim, particle identity, or cosmological law.

## Comparator set

1. standard conserved gradient flow (`g = 0`),
2. legacy instantaneous UET descriptive comparator,
3. `C` plus derived trace with no trace feedback,
4. coupled `(C, Phi, Pi)` candidate,
5. coupled receiver-effect record with explicit receiver feedback,
6. adiabatic reduced candidate.

All physical fields use the existing normalized preregistered lane. The
receiver effect is recorded after the physical step and never feeds back into
`C`, `Phi`, or `Pi` in this pilot.

## Initial conditions and observables

The runner uses uniform, localized pulse, two-domain interface, and locked
spinodal seeds. It reports interface-width and spectral-peak diagnostics only.
`C_phase` is defined for this pilot as

```text
C_phase = exp(-[RMS(C_final - C_initial)/max(RMS(C_initial),1)
                + RMS(Phi_final) + RMS(Pi_final)])
```

It is a normalized persistence/compatibility proxy, not a universal physical
quantity and not mass, charge, temperature, or critical order-parameter proof.

The pilot also checks:

- mass drift and normalized energy/ledger behaviour,
- same `C` with different `Phi,Pi`,
- same complete physical state with different trace history,
- explicit receiver response,
- temporal/spatial resolution sensitivity,
- the inherited causal-support controller.

## Falsification and boundary

The lane is reduced or rejected if coupling disappears at refinement, trace
history changes physical state without an explicit receiver operator, energy
or conservation gates fail, or the run needs clipping/fitted parameters. The
existing core pre-arrival leakage failure remains controlling and is not
hidden by this diagnostic.

The result cannot change the current Topic 0.11 Wave 55 replicate/temporal
acquisition controller.
