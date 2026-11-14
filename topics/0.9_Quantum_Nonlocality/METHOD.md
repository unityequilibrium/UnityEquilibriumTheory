# Method

## Problem Target

This topic tests the quantum-nonlocality evidence lane through a concrete CHSH
benchmark first. UET explanatory mechanisms are kept separate from the benchmark
until a derivation artifact maps them to standard quantum correlations.

## Evidence Lanes

| Lane | Files | Current role |
| :-- | :-- | :-- |
| CHSH/Bell benchmark | `bell_test_2015.json`, `Research_CHSH_Verification.py` | primary verifier lane |
| Tsirelson bound consistency | `2*sqrt(2)` check in verifier | benchmark anchor |
| Singlet/QM comparator | `Research_Bell_Test.py`, `Competitor_QM_Baseline.py` | secondary comparator/visualization |
| UET topological filament | README, analysis docs, engine concepts | heuristic bridge |
| Qubit mechanics/T1 | `Research_Qubit_Mechanics.py` and data files | future verifier lane |
| Double slit/tunneling | double-slit and tunneling scripts | separate quantum benchmark lanes |

## Variables

| Symbol | Meaning | Unit |
| :-- | :-- | :-- |
| `E(a,b)` | correlation between measurement settings | dimensionless |
| `S` | CHSH parameter | dimensionless |
| `S_error` | reported uncertainty for `S` | dimensionless |
| `p` | p-value for local-realist violation | dimensionless |
| `2*sqrt(2)` | Tsirelson benchmark | dimensionless |
| `theta` | measurement angle in comparator scripts | radians or degrees as declared |

## Procedure

1. Load the Hensen 2015 working copy and summary file.
2. Check that `S > 2` and that the lower 1-sigma bound still clears `2`.
3. Check that p-value is below `0.05`.
4. Check that the recorded quantum maximum is within rounding tolerance of
   `2*sqrt(2)`.
5. Record input hashes, DOI/source identity, metrics, checks, blockers, and
   limitations in the artifact.

## Domain of Validity

The current method validates a source-referenced CHSH benchmark. It does not
derive UET's topological explanation or reproduce raw experimental event-count
analysis.

## Dependency Policy

Any topic that uses `0.9` as evidence may cite only the CHSH benchmark unless it
also cites a future derivation artifact for the UET topological bridge.
