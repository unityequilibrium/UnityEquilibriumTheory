# Verification Spec

## Primary Command

```powershell
python docs/topics/0.16_Heavy_Nuclei/Code/03_Research/Research_Fission.py
```

## Inputs

| Input | Role | Required identity |
| :-- | :-- | :-- |
| `Data/03_Research/ame2020_heavy_nuclei.json` | AME2020 heavy-nuclei working copy for U-235 checkpoint | SHA256 recorded in artifact |
| `Code/01_Engine/Engine_Heavy_Nuclei.py` | SEMF / UET bridge implementation | Formula IDs `HN16-SEMF-BINDING`, `HN16-UET-SEMF-BRIDGE` |

## Metrics

- Bridge binding energy for U-235.
- AME2020 working-copy binding energy for U-235.
- U-235 relative binding-energy error.
- Bridge-estimated Ba-141 + Kr-92 product binding energy.
- Fission energy sanity value, `Q_bridge = BE_products - BE_parent`.
- Fragment AME provenance flag.

## Current Acceptance Boundary

| Status | Meaning |
| :-- | :-- |
| `WARN` | U-235 checkpoint and exothermic fission sanity range pass, but fragment masses are bridge-derived rather than source-locked. This is the expected current honest status. |
| `FAIL` | Energy release is outside `[100, 250] MeV` or U-235 bridge binding error exceeds `2%`. |
| `PASS` | Reserved for a future verifier that uses source-locked Ba-141/Kr-92 fragment masses and an evaluated fission-energy baseline. |

## Artifact Target

- `Result/artifacts/0_16_heavy_nuclei_verification.json`

The artifact must record:

- status, claim class, command, and timestamp
- dataset path, DOI, and SHA256
- formula IDs
- U-235 binding checkpoint, fragment bridge estimates, energy release, gates, and limitations

## Interpretation

The current artifact supports only an internal fission sanity-check claim. It does not validate the evaluated U-235 fission Q-value, the island of stability, or a first-principles UET nuclear binding theory.
