# Data Manifest

Current data reality status: `embedded local only`

The primary Bell-test working copy includes a DOI, but the topic still lacks a
full raw upstream event-count package. Treat current data as source-referenced
repository working copies until raw-source provenance is added.

## Primary Inputs

| Dataset | Local path | Source | Unit convention | Benchmark role | Provenance status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Hensen 2015 Bell test | `Data/03_Research/bell_test_2015.json` | Hensen et al. 2015, DOI `10.1038/nature15759` | dimensionless CHSH `S`, error, p-value | primary CHSH verifier input | DOI recorded; raw counts not included |
| Bell inequality summary | `Data/03_Research/bell_inequality_data.json` | Hensen et al. 2015 / local summary | dimensionless CHSH values and p-value | secondary consistency input | source text recorded; DOI absent in this file |

## Secondary Inputs

| Dataset | Local path | Role | Limitation |
| :-- | :-- | :-- | :-- |
| Bell test data module | `Data/03_Research/bell_test_data.py` | legacy local data helper | not used by primary verifier |
| Double-slit C60 | `Data/03_Research/double_slit_c60.json` | interference lane | not evidence for CHSH nonlocality |
| Qubit/tunneling files | `Data/03_Research/*qubit*`, `*tunnel*` | future lanes | require separate manifests and verifiers |

## Hash Policy

The primary verifier records SHA-256 hashes for the primary input files in
`Result/artifacts/0_9_quantum_nonlocality_verification.json`.

## Next Provenance Work

- Add raw event counts or source tables from the Hensen et al. analysis if
  licensing allows.
- Add DOI/URL/retrieval notes to every local Bell and qubit working copy.
- Keep raw external sources under `docs/data/external/quantum_nonlocality/...`
  when fetched; keep topic-derived normalized inputs under this topic's `Data/`.
