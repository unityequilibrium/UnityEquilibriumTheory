# Verification Spec

## Primary Command

```powershell
python docs/topics/0.12_Vacuum_Energy_Casimir/Code/03_Research/Research_Casimir.py
```

## Inputs

| Input | Role | Required identity |
| :-- | :-- | :-- |
| `Data/03_Research/mohideen_1998_casimir.json` | Primary sphere-plate Casimir benchmark working copy | SHA256 recorded in the artifact |
| `Code/01_Engine/Engine_Vacuum.py` | Formula implementation | Formula IDs `VAC-SPHERE-PFA`, `VAC-FINITE-CONDUCTIVITY` |

## Metrics

- Average relative force error across all benchmark separations.
- Maximum relative force error across all benchmark separations.
- Per-point residual table with separation, experimental force, model force, and relative error.

## Fixed Thresholds

| Metric | PASS threshold |
| :-- | :-- |
| Average relative error | `<= 10%` |
| Maximum relative error | `<= 15%` |

## Artifact Target

- `Result/artifacts/0_12_vacuum_energy_casimir_verification.json`

The artifact must record:

- PASS/FAIL status.
- command string and generation timestamp.
- dataset path and SHA256 hash.
- source label, geometry, material, dataset radius, and model radius.
- formula IDs used by the verifier.
- thresholds, metrics, per-point rows, and limitations.

## Interpretation

A PASS supports a Claim Class C internal benchmark for the sphere-plate Casimir force only. It does not validate `VAC-DARK-ENERGY-ANCHOR`, solve the cosmological-constant problem, or prove a Planck-scale vacuum cutoff.
