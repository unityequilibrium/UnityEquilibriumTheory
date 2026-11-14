# Data Manifest

Current data reality status: "manual or placeholder"

The current primary verifier is a surrogate mathematical demonstration and does not consume a real external theorem dataset. This manifest therefore records the current helper file honestly as a local script dependency rather than as scientific source data.

## Current Declared Input

| Item | Local path | Bytes | SHA256 | Source | Provenance status | Unit convention | Benchmark role |
| :-- | :-- | --: | :-- | :-- | :-- | :-- | :-- |
| `Download_Quantum_Data.py` | `Data/Download_Quantum_Data.py` | 3759 | `e4b82c0ea5093ff2d0042f3cada4f4074ade15399a01b5d6241b0b6f6108e07a` | Topic-local quantum/math helper script | Manual/placeholder; not an upstream dataset and not loaded by the current BSD verifier. | Not applicable; script/helper file. | Declared placeholder input in the current verification spec. |

## Missing Provenance for Theorem Branches

- BSD branch: no source-backed elliptic-curve rank table or L-function values are present.
- Riemann branch: known zeros are supplied dynamically by `mpmath.zetazero`; no local zero table, precision manifest, or source version is recorded.
- P-vs-NP/Grover branch: no NP-complete benchmark suite or formal reduction dataset is present.
- Collatz branch: no bounded search manifest, seed/range declaration, or counterexample policy is present.
- Quantum-logic branch: no deterministic gate-test fixture package is present.

## Repository Note

- Future raw/source datasets or benchmark tables should be stored under `docs/data/external/math/...` or `docs/data/external/quantum/...` when shared across topics.
- Topic-specific generated tables or bounded-search outputs should stay under `docs/topics/0.18_Mathnicry/Data/...`.
- A theorem branch cannot be promoted by adding data alone; it also needs a formal theorem target, assumptions, proof status, and artifact with failure modes.
