# NuFIT-KATRIN Consistency Analysis

## Scope

This note records the current combined state of topic `0.7_Neutrino_Physics` after checking the topic against:

- the official NuFIT 6.0 oscillation benchmark
- the official KATRIN 2025 direct mass-limit benchmark

## Current result

- NuFIT 6.0 oscillation benchmark: `PASS`
- KATRIN 2025 direct mass-limit benchmark: `PASS`
- Combined verifier status: `PASS`

## What passes

The current UET geometric angle layer remains compatible with the official NuFIT 6.0 `3sigma` ranges:

- `theta12`
- `theta23`
- `theta13`

The current runtime mass-splitting layer also remains compatible with the official NuFIT 6.0 benchmark package:

- `delta_m21_sq`
- `delta_m3l_sq`

The repaired absolute neutrino-mass engine path is now compatible with the official KATRIN 2025 limit:

| Quantity | Value |
| :-- | --: |
| Official KATRIN 2025 limit | `< 0.45 eV/c^2` |
| Current UET engine mass scale | `6.4026e-4 eV` |

## Root cause of the previous failure

The earlier KATRIN failure was not a subtle theory miss. It was a dimensional inconsistency in `Engine_Neutrino.predict_neutrino_mass()`:

- `v_ew` was written in `GeV`
- `M_PLANCK` imported from the shared core is defined in `kg`
- an extra `1e-6` bridge factor was applied on top

That combination produced an unphysical heavy scale and inflated the predicted neutrino mass to an absurd value.

## What was repaired

The current branch keeps the see-saw-style relation in one unit system:

- use Planck mass expressed in `GeV/c^2`
- form `M_I` in `GeV`
- compute `m_nu = v^2 / M_I` in `GeV`
- convert the final result to `eV`

This repair fixes a physics/unit error rather than tuning the topic against KATRIN.

## Interpretation

- The oscillation layer and the direct-mass layer are now at least mutually non-contradictory under the current benchmark package.
- Passing KATRIN removes a major physical blocker from the topic.
- The topic still does not yet claim a full first-principles derivation of the neutrino sector, because the mass splittings remain benchmark-fed and the NuFIT table is still maintained through a manual extracted JSON layer.

## Remaining gaps

1. Replace the manual NuFIT transcription layer with a machine-parsed source-backed table.
2. Clarify the physical derivation of the heavy information scale `M_I` beyond the current compact see-saw-style analogy.
3. Extend the topic beyond the current benchmark package to wider neutrino constraints before calling the topic academically mature.
