# Thermal Matter-Space Pilot Specification

## Status and purpose

This is a diagnostic-only, normalized control lane for `matter_space_coupled_v1`.
It compares response shapes and numerical accounting; it does not identify
`space_response` with temperature, heat flux, entropy, or an SI observable.

Current dependency state: `BLOCKED` by
`docs/core/07_artifacts/gates/matter_space_dependency_gate.json`, whose controlling
blocker is pre-arrival leakage in the physical-response discretization.
Diagnostic execution is allowed, but physical interpretation and claim
promotion are not.

## Pre-registered comparison set

1. Fourier instantaneous control: `q_F = k F(t)`.
2. Cattaneo control: `tau_q dq/dt + q = k F(t)`.
3. Trace-only observable: `R = G_ret * sigma`, with no backreaction.
4. Linearized space-response control:
   `tau_Phi d2Phi/dt2 + dPhi/dt + M_Phi a_Phi Phi = J_Phi(t)`.
5. Nonlinear coupled candidate using the declared matter-space functional and
   explicit `(C, Phi, Pi)` state.

The locked machine-readable configuration is
`Data/03_Research/matter_space_thermal_preregistration.json`. The selected
primary parameter row is fixed before execution; the remaining grid is a
sensitivity diagnostic and is not selected by agreement with data.

## Observable boundary

All simulated variables are normalized. In particular:

- `F(t)` is a normalized thermal-force control, not a declared `K/m` gradient.
- `q`, `Phi`, and `R` are plotted on separate normalized-response axes.
- `R` is generated from non-negative dissipation and never feeds back.
- no curve from an external paper is digitized, fitted, or used as a target.
- Landauer `k_B T ln 2` remains an external lower-bound constraint and is not
  used to derive a core `beta` or any matter-space coefficient.

## Metrics and gates

The pilot records phase lag, phase error, hysteresis area, physical arrival
speed, pre-arrival leakage, minimum dissipation source, open-system ledger
closure, time-step convergence, and input/artifact hashes.

The Cattaneo control must satisfy:

- complex analytical residual `<= 1e-10`;
- phase, lag, and hysteresis relative error `<= 5%`;
- time-step convergence error `<= 5e-4`.

The physical causal and source-sign gates inherit the core thresholds:

- pre-arrival leakage `<= 1e-6` of peak;
- source minimum `>= -1e-12`.

A failed inherited core gate keeps this pilot `SIMULATION_ONLY` with blocked
physical interpretation even when the analytical control passes.

## External source package

The source registry is
`Data/03_Research/matter_space_second_sound_source_package.json`.

- Ding et al. (2022), graphite over 200 K, is the primary external source
  candidate: https://doi.org/10.1038/s41467-021-27907-z
- Huberman et al. (2019) is a graphite comparator:
  https://arxiv.org/abs/1901.09160 and
  https://doi.org/10.1126/science.aav3548
- McNelly et al. (1970), NaF, is a separate material-family comparator:
  https://doi.org/10.1103/PhysRevLett.24.100
- Xie et al. (2026) is locked as an untouched holdout for this development
  pass: https://doi.org/10.1038/s41467-026-70807-3

The source package remains `BLOCKED` until a dimensional observable map from
`Phi` to a measured temperature/TTG signal is declared and an allowed local
numeric source with units, locators, preprocessing, uncertainty, and hash is
archived.

## Claim boundary

Allowed wording: `synthetic control`, `simulation-only`, `normalized internal
diagnostic`, and `candidate effective model`.

Not allowed: `external validation`, `second sound derived by UET`, `Phi is
measured temperature`, `Landauer derives beta`, or any material-level fit.
