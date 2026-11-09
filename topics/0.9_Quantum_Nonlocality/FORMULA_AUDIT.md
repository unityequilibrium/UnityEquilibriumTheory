# Formula Audit: 0.9_Quantum_Nonlocality

Review status: reviewed first-pass registry for the Bell/CHSH benchmark lane.
The UET topological-filament explanation remains a model bridge until a separate
derivation/proof artifact maps the bridge to the standard quantum correlations.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `QN09-CHSH-PARAMETER` | `S = |E(a,b) - E(a,b')| + |E(a',b) + E(a',b')|` | `Research_CHSH_Verification.py`; `Research_Bell_Inequality.py`; `bell_test_2015.json` | `E` correlation coefficients, dimensionless; `S` dimensionless | Hensen et al. 2015 working copy, DOI `10.1038/nature15759` | source-referenced benchmark | primary verifier metric | If `S` is copied incorrectly, Bell-violation claim is invalid | Add raw event-count reconstruction from the published experiment. |
| `QN09-LOCAL-REALIST-BOUND` | `S <= 2` | `bell_test_2015.json`; `Research_CHSH_Verification.py` | dimensionless CHSH bound | standard Bell/CHSH theorem | benchmark anchor | primary pass/fail gate | Mislabeling the bound changes violation interpretation | Cite exact CHSH convention and sign/order in METHOD. |
| `QN09-TSIRELSON-BOUND` | `S_QM <= 2*sqrt(2)` | `bell_test_2015.json`; `Research_CHSH_Verification.py`; comparator scripts | dimensionless quantum bound | standard quantum-mechanics theorem | benchmark anchor, not UET-derived in this topic | consistency gate | Treating the benchmark anchor as a UET derivation overclaims the result | Add a derivation note that separates standard QM theorem from UET bridge. |
| `QN09-PVALUE-GATE` | `p < 0.05` | `bell_test_2015.json`; `Research_CHSH_Verification.py` | p-value dimensionless | Hensen et al. working copy | source-referenced statistical diagnostic | primary significance check | p-value alone does not reproduce raw trial analysis | Add raw counts/analysis workflow if available. |
| `QN09-SINGLET-CORRELATION` | `E(theta) = -cos(theta)` or script-specific angle convention | `Research_Bell_Test.py`; `Competitor_QM_Baseline.py` | angle in radians/degrees as declared; correlation dimensionless | standard singlet-state QM relation | benchmark model | secondary visualization/comparator | Angle convention drift can produce false agreement | Standardize angle convention and tie to CHSH settings. |
| `QN09-TOPOLOGICAL-FILAMENT` | zero information-distance/topological-link explanation | README/METHOD; analysis docs | conceptual relation; no physical unit closure yet | UET model proposal | heuristic bridge/open | explanatory model only | Can sound like proof without a derivation linking it to CHSH correlations | Write a derivation artifact with assumptions, variables, and falsifiable predictions. |
| `QN09-QUBIT-T1` | exponential relaxation or topic-specific qubit decay proxy | `Research_Qubit_Mechanics.py`; qubit data files | time in source units; probability/fidelity dimensionless | local qubit working copies | exploratory | excluded from primary verifier | T1 data does not validate nonlocality mechanism | Create a separate qubit benchmark artifact. |
| `QN09-DOUBLE-SLIT` | interference intensity relation from local C60 data | `Research_Double_Slit.py`; `double_slit_c60.json` | length/angle units as source declares; intensity dimensionless | local working copy | exploratory | excluded from primary verifier | Double-slit claims can be conflated with Bell nonlocality | Separate interference benchmark from CHSH benchmark. |

## Claim Boundary

- Current accepted evidence supports Claim Class C: a source-referenced internal
  CHSH benchmark that checks Bell violation and consistency with the Tsirelson
  bound.
- It does not prove the UET topological-filament mechanism or resolve quantum
  nonlocality from first principles.
- Qubit, double-slit, tunneling, and LC-unity scripts are secondary lanes until
  each has its own formula audit rows, source-locked data, and verifier artifact.

## Audit Link

- Core audit report: `docs/meta/core_research_hardening_audit.md`
