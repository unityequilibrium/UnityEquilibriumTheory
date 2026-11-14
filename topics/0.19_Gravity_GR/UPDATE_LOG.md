# Update Log: 0.19 Gravity & General Relativity

## 2026-07-22 - Core GR Program Dependency Gate

**What changed:**
- Added `CORE_GR_PROGRAM_DEPENDENCY_SPEC.md`, a deterministic dependency verifier, generated dependency artifact, and twelve regression tests.
- Connected Topic 0.19 to the current core GR program without rewriting the topic's CODATA primary artifact or branch claim gate.
- Separated the exact implemented `epsilon_nc = 0` response-null from metric-PDE derivation, physical GR validation, and global universe closure.

**Which verifier was run:**
- `.\.venv\Scripts\python.exe docs/topics/0.19_Gravity_GR/Code/03_Research/Research_Core_GR_Program_Dependency_Gate.py`
- `.\.venv\Scripts\python.exe -m pytest docs/core/test/test_core_gr_topic_0_19_dependency.py -q`

**Which blocker narrowed:**
- The topic can now reference a machine-readable core candidate chain: exact response-null, local covariant balance, flat local 1+1 causal kernel, partial response reduction, and bounded Noether coordinate layer.
- These layers remain candidate mathematics and do not replace the topic's physical benchmarks.
- The dependency controller is narrowed to `topic_0_19_classical_gr_tests_and_covariant_completion_missing`.

**Next controlling blocker:**
- Add source-backed light-bending, perihelion, MICROSCOPE eta, and Eot-Wash artifacts, then close curved 3+1, equation-of-state, coarse-graining, transport/KMS, entropy-current, and dissipative-Bianchi requirements.
- Compare `epsilon_nc != 0` against the exact `epsilon_nc = 0` GR null on independent holdout evidence.

**Current topic-level status after wave:**
- Topic 0.19 remains `Draft / Tier B`; the CODATA checkpoint remains the independent primary artifact and its export controller remains `WARN`.
- Global universe closure remains `UNRESOLVED`; no GR-validation, global-open/closed, singularity, quantum-gravity, external-validation, or solved-theory claim is upgraded.

## 2026-08-08 - Repair 0.19 dependency input and artifact drift

**What changed:**
- Restored the previously tracked `Data/03_Research/branch_claim_gate.json` input from commit `5a853349c`; the dependency generator already required this file and the persisted artifact still recorded it as a scientific input.
- Regenerated `Result/artifacts/0_19_core_gr_program_dependency_gate.json` from the existing generator without changing the topic claim boundary.

**Which verifier was run:**
- `Research_Core_GR_Program_Dependency_Gate.py` returned `BLOCKED` with the same controller: `topic_0_19_classical_gr_tests_and_covariant_completion_missing`.
- `pytest docs/core/test/test_core_gr_topic_0_19_dependency.py docs/core/test/test_particle_dirac_program_gate.py docs/core/test/test_uet_wave3_wave10_program.py docs/core/test/test_uet_wave3_wave10_artifact_coverage.py -q` passed `18/18`.

**Which blocker narrowed:**
- The repository consistency blocker (missing branch input and stale scientific-input hash) is closed. The physical GR validation blocker is unchanged.

**Next controlling blocker:**
- Source-backed classical GR tests, curved 3+1 completion, transport/KMS, and independent holdout comparison remain required before any GR or global-universe claim can advance.

**Claim impact:**
- No promotion. Topic 0.19 remains `Draft / Tier B`; this is an artifact/provenance repair wave only.
