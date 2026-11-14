# Verification Spec

## Primary Command

```powershell
python docs/topics/0.19_Gravity_GR/Code/03_Research/Research_G_Constant.py
```

## Inputs

| Input | Role | Required identity |
| :-- | :-- | :-- |
| `Data/03_Research/codata_2018_gravity.json` | CODATA 2018 constants working copy | SHA256 and DOI recorded in artifact |
| `Code/01_Engine/Engine_Gravity_GR.py` | Engine constant package and Planck-unit definitions | Formula IDs `GR19-CONSTANT-PACKAGE`, `GR19-PLANCK-UNITS` |

## Metrics

- `G_engine`
- `G_codata`
- relative error percent
- threshold percent, based on CODATA relative uncertainty with a minimum numerical tolerance
- Planck length/time/mass values derived from the engine constants

## Fixed Threshold

| Metric | PASS threshold |
| :-- | :-- |
| Relative error between `G_engine` and `G_codata` | `<= max(CODATA relative uncertainty percent, 0.0001%)` |

## Artifact Target

- `Result/artifacts/0_19_gravity_gr_verification.json`

The artifact must record:

- PASS/FAIL status and claim class
- command and timestamp
- dataset path, SHA256, source, and DOI
- formula IDs
- threshold and metrics
- limitations

## Interpretation

A PASS supports only a Claim Class C internal source-constant checkpoint. It does not derive `G`, validate general relativity, prove the equivalence principle, predict light bending/perihelion precession, or resolve singularities.
Topic-level source-evidence and branch-claim gates further limit this topic to constants and derived-unit checkpoint usage unless dedicated GR artifacts are added.
`gravity_claim_scope_gate.controller_status == WARN` is expected when the CODATA checkpoint passes while G derivation, weak-field validation, MICROSCOPE eta comparison, Eot-Wash comparison, Einstein-equation, singularity, and quantum-gravity branches remain open.

## Core GR Program Dependency Gate

### Command

```powershell
.venv\Scripts\python.exe docs\topics\0.19_Gravity_GR\Code\03_Research\Research_Core_GR_Program_Dependency_Gate.py
.venv\Scripts\python.exe -m pytest docs\core\test\test_core_gr_topic_0_19_dependency.py -q
```

### Artifact

- `Result/artifacts/0_19_core_gr_program_dependency_gate.json`

### Required gates

- `core_program_stage_gate == PASS`
- `exact_gr_response_null_gate == PASS`
- `local_covariant_balance_gate == PASS`
- `causal_constitutive_scope_gate == PASS`
- `partial_response_reduction_gate == PASS`
- `noether_state_map_scope_gate == PASS`
- `topic_constant_checkpoint_preservation_gate == PASS`
- `physical_gr_benchmark_gate == BLOCKED` until dedicated classical and experimental comparisons exist
- `covariant_completion_gate == BLOCKED` until curved 3+1, EOS, coarse-graining, transport/KMS, entropy-current, and dissipative-Bianchi requirements close
- `topic_promotion_gate == BLOCKED`

### Current interpretation

The dependency artifact is expected to report
`BLOCKED / CORE_CANDIDATE_GR_PARENT_AVAILABLE_TOPIC_PHYSICAL_VALIDATION_OPEN`.
It may record an exact implemented `epsilon_nc = 0` response-null, local
covariant balance, flat local 1+1 causal support, and a partial response-sector
reduction. It must preserve the Topic 0.19 CODATA/Planck checkpoint, its `WARN`
export controller, `Draft / Tier B` status, and the physical benchmark blockers.
Global universe closure must remain `UNRESOLVED`.
