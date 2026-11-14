# Method

## Problem target

This topic studies whether current UET-inspired nuclear binding and hadron-scale heuristics can reproduce selected binding-energy and proton-radius benchmarks, and how the same engine behaves across the wider AME2020 parsed table.

## Core components

### Engine components
- `Code/01_Engine/Engine_Hadron_Model.py`
- `Code/01_Engine/Engine_Light_Nuclei.py`
- `Code/01_Engine/Engine_Nuclear_Binding.py`

### Proof-oriented components
- `Code/02_Proof/Proof_Color_Confinement.py`

### Research and comparison components
- `Code/03_Research/Research_Nuclear_Binding.py`
- `Code/03_Research/Research_Nuclear_Binding_SourceLocked.py`
- `Code/03_Research/Research_Proton_Radius.py`
- `Code/03_Research/Research_QCD_Running.py`

## Variable framing

- Primary modeled quantities: binding energy per nucleon, hadron mass, confinement-scale terms, overlap parameters, and proton-radius observables.
- Formula registry: see `FORMULA_AUDIT.md` for the current distinction between source-backed heavy-nucleus binding gates, diagnostic light-nuclei formulas, benchmark-anchor proton-radius behavior, and open hadron/QCD bridge paths.

## Assumptions

- The primary strict verifier now uses a source-backed AME2020 extracted subset and a source-backed proton-radius benchmark.
- The topic now also maintains a separate full-table diagnostic layer for the parsed AME2020 coverage; that layer is descriptive and does not replace the strict subset gate.
- Heavy nuclei and light nuclei should be interpreted differently because the liquid-drop-style branch is intended mainly for larger nuclei.

## Domain of validity

- Selected isotopes from the AME2020 strict validation subset, table-wide AME2020 diagnostics, proton-radius checks, and strong-force benchmark tests.

## Excluded cases

- A full derivation of QCD from first principles or a general confinement proof.

## Parameter sensitivity note

- The current engine still uses fixed semi-empirical coefficients and an additive UET correction, so the topic should not be described as fully parameter-free.
- The stricter verifier is now less dependent on embedded lists, but it still uses a curated subset rather than a full-table pass/fail gate.
- The full-table diagnostic layer is useful for scientific honesty because it exposes where the engine degrades outside the curated validation subset, especially for lighter nuclei.
- Hadron-mass, QCD-running, and confinement-proof scripts are diagnostic/open until their embedded constants are source-locked and their pass/fail behavior is made artifact-backed.
