# Method

## Problem target

This topic studies whether current UET-style neutrino structure can reproduce selected mixing-angle and mass-splitting benchmarks when checked against official NuFIT 6.0 ranges, and whether the absolute neutrino-mass engine path remains compatible with the official KATRIN 2025 direct mass limit.

## Core components

### Engine components
- `Code/01_Engine/Engine_Mixing_Neutrino.py`
- `Code/01_Engine/Engine_Neutrino.py`

### Proof-oriented components
- `Code/02_Proof/Proof_PMNS_Angles.py`

### Research and comparison components
- `Code/03_Research/Research_Ft_Values.py`
- `Code/03_Research/Research_Neutrino.py`
- `Code/03_Research/Research_Neutrino_Extended.py`
- `Code/03_Research/Research_NuFit_6_0_Comparison.py`

## Variable framing

- Primary modeled quantities: mixing angles, mass-squared differences, PMNS-style parameters, and selected decay observables.
- Formula registry: see `FORMULA_AUDIT.md` for the current distinction between geometric angle outputs, benchmark-fed mass splittings, PMNS matrix construction, oscillation formulas, and the see-saw-style absolute-mass branch.

## Assumptions

- The primary benchmark for oscillation parameters should now come from the official NuFIT 6.0 parameter table.
- The direct absolute-mass benchmark should come from the official KATRIN 2025 latest-results page.
- Geometric angle outputs are treated separately from runtime benchmark-fed mass splittings.
- The absolute-mass branch uses a see-saw-style relation `m_nu = v^2 / M_I`, so the electroweak scale `v` and the heavy information scale `M_I` must be expressed in the same unit system before converting the final result to eV.

## Domain of validity

- Selected three-flavor oscillation parameters under normal ordering, benchmarked against official NuFIT 6.0 ranges.

## Excluded cases

- A complete neutrino-sector theory across all matter effects, sterile sectors, or cosmological constraints.

## Parameter sensitivity note

- The current angle checks now use live `Engine_Neutrino.py` outputs rather than a separate benchmark-compatible angle snapshot.
- The runtime mass splittings still come from benchmark-fed parameters inside the engine, so they should not yet be described as fully first-principles derivations.
- Any mismatch between live engine angles and NuFIT ranges is a model-hardening blocker, not a documentation-only issue.
- The direct absolute-mass engine path is distinct from the oscillation benchmark path and therefore must be audited separately against KATRIN rather than inferred from the NuFIT pass alone.
- The major blocker found in the previous KATRIN fail was a dimensional inconsistency: the earlier engine mixed SI-kilogram Planck mass with an electroweak scale written in GeV and inserted an extra `1e-6` bridge factor. The current branch repairs that unit mismatch by keeping the see-saw relation in GeV and converting to eV only at the end.

## Cross-topic dependency policy

- `0.17_Mass_Generation` can use the KATRIN-compatible mass-scale branch only as a bounded model component until the angle gate is repaired.
- `0.23_Unity_Scale_Link` can use the `0.7` verifier as a constraint on cross-domain linking, not as positive evidence for a unity-scale proof.
- `0.0_Grand_Unification` should index the current FAIL artifact and inherit the neutrino-angle limitation in any integration claim.
