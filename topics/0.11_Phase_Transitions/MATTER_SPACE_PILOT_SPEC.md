# Matter-Space Coupling Pilot Specification

## Purpose

This pilot tests whether the exact normalized matter-space functional produces a numerically distinguishable, conservative, history-dependent physical response without allowing the derived trace to feed back into the dynamics.

It is an isolated internal diagnostic. It does not replace the current structure-factor workstream, change Topic 0.11 readiness, or support universality, critical-exponent, RG, or material claims.

## Locked ontology and equations

- `C`: conserved normalized matter/order parameter.
- `Phi`: normalized effective space-response variable.
- `Pi = dPhi/dt`: normalized space-response rate.
- `R`: derived dissipation-history observable only.

The physical chain is

`(C, Phi, Pi) -> (mu_C, mu_Phi) -> dynamics -> energy/dissipation ledger -> R`.

No arrow from `R` to `C`, `Phi`, or `Pi` is permitted.

The coupled lane uses `matter_space_coupled_v1` with periodic one-dimensional finite-volume operators and conserved matter dynamics. The canonical baseline uses the same discretization with `g = 0`. The adiabatic reduction solves the local root

`a_Phi Phi_* + b_Phi Phi_*^3 - (g/2) C^2 = 0`

before advancing conserved `C`.

## Comparator matrix

1. Legacy instantaneous UET: descriptive comparator only; not conservative and not a variational reference.
2. Canonical `C`-only conserved gradient flow: `g = 0`, no trace.
3. Canonical `C` plus derived trace: same physical lane as comparator 2, trace enabled with no feedback.
4. Coupled `(C, Phi, Pi)`: exact normalized functional and extended ledger.
5. Adiabatic reduced model: local `Phi_*[C]` constitutive reduction.

## Locked initial-condition suite

- uniform coupled equilibrium
- localized matter pulse
- periodic two-domain interface
- random spinodal fields from seeds `1101`, `1102`, and `1103`
- same `C` with different `(Phi, Pi)`
- same complete physical state with different trace histories

All numeric values, time-step fractions, grid sizes, seeds, and gates are stored in `Data/03_Research/matter_space_coupled_preregistration.json` before the evidence run.

## Measurements

- matter-integral drift
- maximum relative extended-energy increase
- maximum ledger-closure residual
- non-negative dissipation source
- coupled-versus-canonical RMS effect
- temporal-refinement error and multi-resolution effect persistence
- same-`C` state sensitivity
- trace-history physical invariance
- adiabatic-limit error sequence
- interface-width proxy
- finite-k structure-factor peak
- spectral correlation-length proxy

The last three are morphology diagnostics only. They are not accepted Topic 0.11 estimators and cannot feed the existing structure-factor or exponent gates.

## Gates

- conserved matter relative drift `<= 1e-10`
- minimum dissipation density `>= -1e-12`
- closed-system relative energy increase `<= 1e-9`
- relative ledger closure `<= 1e-6`
- trace-history physical difference `<= 1e-12`
- trace switch physical difference `<= 1e-12`
- coupled effect `> 10 *` temporal-refinement error and `> 1e-6`
- multi-resolution minimum/maximum effect ratio `>= 0.5`
- same-`C`, different-`(Phi,Pi)` response `> 10 *` temporal-refinement error
- adiabatic errors decrease across the locked sequence and the finest relative error is `<= 5%`
- no NaN, field clipping, parameter fitting, or external numeric data

## Falsification and claim boundary

The candidate is reduced or rejected in this lane if the coupling effect is numerical-only, conservation/ledger gates fail, trace history changes future physical state, the adiabatic limit does not converge, or stable execution requires clipping.

Allowed label: `internal normalized matter-space diagnostic`.

Not allowed: accepted structure-factor estimator, critical universality, RG closure, material validation, spacetime proof, or full phase-transition theory.
