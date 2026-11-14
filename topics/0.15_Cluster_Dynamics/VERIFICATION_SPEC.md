# Verification Spec

## Primary Command

```powershell
python docs/topics/0.15_Cluster_Dynamics/Code/03_Research/Research_BulletCluster_Offset.py
```

## Inputs

| Input | Role | Required identity |
| :-- | :-- | :-- |
| `Data/Bullet_Cluster_Coordinates.json` | Primary Bullet Cluster offset working copy | SHA256 recorded in artifact |
| `Code/03_Research/Research_BulletCluster_Offset.py` | One-dimensional toy diagnostic verifier | Formula IDs `CL15-DRAG-TOY`, `CL15-OFFSET-SIGN-GATE` |

## Metrics

- Observed lensing/X-ray offsets in kpc for main cluster and sub-cluster components.
- Toy model final gas/halo separation in model units.
- Qualitative sign match: observed offsets positive and model offset positive.
- Dimensional calibration flag.

## Current Acceptance Boundary

| Status | Meaning |
| :-- | :-- |
| `WARN` | Qualitative separation sign matches, but model lacks kpc calibration. This is the expected current honest status. |
| `FAIL` | The toy model fails even the separation-sign diagnostic or the input dataset is missing. |
| `PASS` | Reserved for a future kpc-calibrated model with numeric magnitude thresholds against the observed offsets. |

## Artifact Target

- `Result/artifacts/0_15_cluster_dynamics_verification.json`

The artifact must record:

- status and claim class
- command and timestamp
- dataset path and SHA256
- source label, system name, and unit convention
- formula IDs
- observed kpc offsets, model-unit offset, qualitative sign match, and dimensional calibration flag
- limitations and failure reason

## Interpretation

The current verifier supports only Claim Class D qualitative diagnostic language. It does not support "solved dark matter", "resolves the virial discrepancy", "predicts Bullet Cluster lensing", or a general cluster-scale replacement for dark matter.
