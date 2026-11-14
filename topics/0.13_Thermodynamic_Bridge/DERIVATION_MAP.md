# Derivation Map

## Purpose

This file separates three things that are easy to blur together in `0.13`:

1. standard thermodynamic identities imported as constraints
2. topic-local UET proxies and engine rules
3. the still-open claim that UET *derives* an information-entropy-energy bridge

It is a boundary document, not a proof.

## Current status

`open_boundary_mapped_not_derived`

Current allowed reading:

- `0.13` can use Landauer, Bekenstein, Unruh, and Hawking relations as source-backed constraint formulas.
- `0.13` can use its entropy/contact engine as a structured proxy sandbox.
- `0.13` cannot yet claim that UET first-principles dynamics derive those thermodynamic identities or close the full bridge.

## Layer split

| Layer | What it contains now | Current status | What it does *not* justify |
| :-- | :-- | :-- | :-- |
| Standard identity layer | Landauer lower bound, Bekenstein bound, Unruh temperature, Hawking temperature | usable as constraints | proof of UET |
| UET proxy layer | Stirling entropy proxy, dimensionless temperature proxy, stochastic contact update | heuristic/model component | dimensional bridge closure |
| UET bridge hypothesis layer | proposed information-entropy-energy interpretation and vacuum-sink extension logic | blocked hypothesis lane | solved or exact bridge claims |
| Matter-space diagnostic layer | normalized `(C, Phi, Pi)` dynamics, energy/dissipation ledger, and derived trace `R` | `SIMULATION_ONLY / FAIL` | a temperature map, measured heat-flux prediction, or external validation |

## Formula path

| Formula ID | Role in the map | Why it matters |
| :-- | :-- | :-- |
| `T13-004` | imports the Landauer lower bound | strongest current benchmark-facing anchor |
| `T13-006` | imports an information-density constraint | keeps entropy-capacity language bounded |
| `T13-008` | imports Unruh temperature | thermodynamic-gravity context only |
| `T13-009` | imports Hawking temperature | thermodynamic-gravity context only |
| `T13-001` | defines a topic-local entropy proxy | useful engine sandbox, not physical entropy by default |
| `T13-002` | defines a topic-local temperature proxy | useful engine sandbox, not Kelvin by default |
| `T13-003` | defines a contact/equilibration rule | useful trend model, not closed derivation |
| `T13-011` | holds bridge-extension/vacuum-sink hypothesis logic | keeps the speculative branch visible and contained |

## Matter-space thermal diagnostic boundary

The pilot follows the one-way chain

`(C, Phi, Pi) -> (mu_C, mu_Phi) -> dynamics -> energy/dissipation ledger -> R`.

`R` has no arrow back into `C`, `Phi`, or `Pi`. The nonlinear homogeneous reduction is cross-checked against `matter_space_coupled_v1`, while Fourier and Cattaneo remain standard controls. The current artifact is still `SIMULATION_ONLY / FAIL`: its disclosed refined ledger passes, but the core physical pre-arrival leakage gate and external numeric-source gate fail. No dimensional map from normalized `Phi` to kelvin, heat flux, or a source-normalized TTG signal has been established.

The source review now defines a standard TTG measurement operator without promoting `Phi` to temperature:

`Delta_Tq = Tq_peak - Tq_valley`, `y_TTG = Delta_Tq(t) / Delta_Tq(0)`

and the candidate normalized UET operator:

`y_TTG_UET = Delta_Phi(t) / Delta_Phi(0)`.

This closes the observable definition layer only. The dimensional coefficient `alpha_Phi_K` remains open, and no heat-flux or entropy-production observable is directly available from the TTG signal.

This diagnostic therefore tests internal constitutive behavior only. It does not derive Cattaneo transport, Landauer's lower bound, second sound, or a dimensional thermodynamic bridge from UET.

## Open derivation steps

### 1. Units contract

Open question:
How do UET variables map onto physical entropy, heat, work, temperature, and information units?

Still needed:

- explicit symbol-to-unit contract
- conversion path from proxy variables to observables
- statement of where physical scaling enters and where it does not
- source-normalized TTG rows with locator, preprocessing, uncertainty, and hash
- independent calibration or derivation of `alpha_Phi_K`

### 2. Landauer-to-UET mapping

Open question:
How does UET reproduce or constrain `E_min = k_B T ln 2` without simply borrowing it as an external identity?

Still needed:

- non-circular mapping from UET variables to erasure cost
- parameter-origin statement
- testable distinction between imported lower bound and UET-added structure

### 3. Gravity-identity mapping

Open question:
How do Bekenstein/Unruh/Hawking formulas enter as consequences or nontrivial constraints of UET rather than decorative context?

Still needed:

- explicit derivation path with assumptions
- regime statement
- explanation of what UET adds beyond restating the standard formulas

### 4. Uncertainty and source closure

Open question:
Does the bridge remain credible once source-normalized data and uncertainty-aware evaluation are enforced?

Current partial progress:

- source-evidence intake/readiness exists
- first-pass propagated intervals exist

Still needed:

- raw-row or machine-transcribed Landauer source package
- Jun final-source parity/local archival for the captured Table 1/Figure 4 fit target
- systematic astrophysical uncertainty terms after direct CODATA 2022 G extraction
- gates that stay conservative under those intervals

## Non-allowed shortcuts

- Do not treat lower-bound agreement as full bridge proof.
- Do not treat imported gravity identities as derived UET outputs.
- Do not let synthetic Cattaneo, matter-space, trace, or vacuum-sink behavior act as empirical support.
- Do not treat a post-diagnostic numerical amendment as a blind preregistered confirmation.
- Do not hide unresolved parameter origin behind good-looking benchmark output.

## Artifact link

The machine-readable version of this boundary map is:

- [bridge_derivation_map.json](/C:/Users/santa/Desktop/uet_harness/docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/bridge_derivation_map.json:1)

That file is generated by the primary verifier and should be kept aligned with:

- [FORMULA_AUDIT.md](/C:/Users/santa/Desktop/uet_harness/docs/topics/0.13_Thermodynamic_Bridge/FORMULA_AUDIT.md:1)
- [METHOD.md](/C:/Users/santa/Desktop/uet_harness/docs/topics/0.13_Thermodynamic_Bridge/METHOD.md:1)
- [VERIFICATION_SPEC.md](/C:/Users/santa/Desktop/uet_harness/docs/topics/0.13_Thermodynamic_Bridge/VERIFICATION_SPEC.md:1)
