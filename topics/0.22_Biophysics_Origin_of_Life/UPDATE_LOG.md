# UPDATE LOG: 0.22 Biophysics & Origin of Life

> **Scope:** `docs/topics/0.22_Biophysics_Origin_of_Life/`
> **Owner:** `UET research hardening wave`
> **Purpose:** Preserve the completed lane-level evidence and blocker history without promoting the umbrella topic.


## [2026-08-10] - Protein-folding dynamics Wave-0 source/runtime gate

- Scope: protein_folding_dynamics lane; existing HP and umbrella lanes remain separate.
- Wave type: source pass + gate pass + formula/claim-boundary sync.
- Added or changed: DYNAMICS_RESEARCH_SPEC.md, DYNAMICS_DATA_MANIFEST.json, DYNAMICS_RUNTIME_MANIFEST.json, the protein dynamics preflight, registry/gate entries, T22-013 through T22-018 candidate formula records, source-target references, and synchronized topic docs.
- Files touched: dynamic spec/manifests, Code/03_Research/Research_Protein_Folding_Dynamics_Gate.py, Result/artifacts/0_22_protein_folding_dynamics_gate.json, RESEARCH_REGISTRY.json, claim gate, FORMULA_AUDIT.md, DATA_MANIFEST.md, METHOD.md, README.md, BASELINE_COMPARISON.md, LIMITATIONS.md, VERIFICATION_SPEC.md, Code/README.md, and data/03_Research/README.md.
- Verified with: .venv\Scripts\python.exe docs\topics\0.22_Biophysics_Origin_of_Life\Code\03_Research\Research_Protein_Folding_Dynamics_Gate.py; .venv\Scripts\python.exe -m pytest docs\core\test\test_protein_folding_dynamics_gate.py docs\core\test\test_protein_folding_hp_benchmark.py docs\core\test\test_run_core_verifications_input_resolution.py -q; primary biomarker verifier; HP verifier; shared runner for 0.22 with input_resolution_status=PASS and exit_code=0; git diff --check.
- Result: umbrella remains Draft / Tier B / WARN; dynamic lane gate is BLOCKED; primary verifier exit code 0; regression tests 9 passed.
- Blocker narrowed: broad protein physical-correspondence uncertainty is now separated into a machine-readable source_locked_cohort_and_atomistic_runtime_missing gate with a 12-protein selection contract and no-download policy.
- Still open: source-backed cohort, pinned OpenMM/MDTraj/openmmtools runtime, hashed AMBER ff14SB/TIP3P assets, CPU smoke test, trajectory round-trip test, atomistic baseline, and later cellular data.
- Next controller: close the source/runtime gate before generating any atomistic result; HP remains a synthetic reduced control.
- Claim impact: no upgrade; dynamic lane remains Claim Class B design/preflight and source_referenced_only; no Claim Class D, real protein folding, AlphaFold replication, PDB/CASP validation, or cellular mechanism claim.
- Workflow linkage: pilot for the shared hardening sequence source package -> gate -> formula audit -> docs -> verifier -> update log.

## [2026-08-10] - Protein folding finite-HP hardening

- Scope: `protein_folding` lane only; umbrella status remains `Draft / Tier B / WARN`.
- Wave type: `artifact pass` with formula and claim-boundary sync.
- Added or changed: deterministic 2-D HP verifier, synthetic input contract, exact finite-model oracle, seeded comparison artifact, T22-010 audit, lane registry, claim gate, and reproducibility docs.
- Files touched: `Code/03_Research/Research_Protein_Folding_HP_Benchmark.py`, `data/03_Research/protein_folding_hp_benchmark.json`, `Result/artifacts/0_22_protein_folding_hp_benchmark.json`, and synchronized topic docs/gates.
- Executed with: `.venv\Scripts\python.exe docs\topics\0.22_Biophysics_Origin_of_Life\Code\03_Research\Research_Protein_Folding_HP_Benchmark.py`.
- Result: `PASS` for the finite HP mechanics contract; `claim_class=C`, `data_class=synthetic`; no topic-level status change.
- Blocker narrowed: `known_benchmark_optimum_seed_and_reproducible_artifact_missing` became a completed finite-model artifact with exact oracle, fixed seeds, input hash, thresholds, and replay check.
- Still open: physical protein correspondence, source-backed structure benchmark, biological free-energy mapping, PDB/CASP comparison, experimental validation, and independent replication.
- Next controller: `physical_protein_correspondence_source_backed_structure_benchmark_and_independent_replication_missing`.
- Claim impact: wording is narrowed to `finite 2-D HP model benchmark`, `exact optimum within the declared lattice model`, and `seeded algorithmic comparison`; no real protein, AlphaFold, PDB/CASP, clinical, or external-validation wording is permitted.
- Workflow linkage: follows the shared hardening sequence of artifact -> gate -> documentation -> update log.
- Notes: the exhaustive canonical search evaluated `11,025` configurations and found `E_HP=-4` for the declared topic-local sequence `HHPPHHPHHPH`; both stochastic comparators reached zero optimum gap in the internal run.
- Regression evidence: HP tests lock the exact configuration count, optimum energy, optimum-fold count, non-bonded contact rule, and deterministic replay; shared-runner tests cover topic-relative, repo-relative, missing, and ambiguous path cases.
