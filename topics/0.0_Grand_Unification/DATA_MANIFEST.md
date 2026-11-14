# Data Manifest

Current data reality status: "integration artifact dependency manifest"

| Item | Local path | Source | Provenance status |
|:--|:--|:--|:--|
| integration dependency manifest | `Data/03_Research/integration_dependency_manifest.json` | Topic-local integration manifest over subordinate artifacts | Defines delegated artifact paths, roles, metric bridges, and claim boundary for the primary `0.0` verifier. |

## Delegated Data Dependencies

`0.0` does not own a raw scientific dataset. It owns a delegated artifact manifest. The primary verifier reads subordinate artifact identity, status, and hashes from `Data/03_Research/integration_dependency_manifest.json`.

| Dependency | Role in `0.0` | Data responsibility |
| :-- | :-- | :-- |
| `0.1_Galaxy_Rotation_Problem` | galaxy/halo metric | Must be checked in the subordinate topic manifest and verifier artifact. |
| `0.6_Electroweak_Physics` | Weinberg-angle metric | Must be checked in the subordinate topic manifest and verifier artifact. |
| `0.10_Fluid_Dynamics_Chaos` | critical Reynolds metric | Must be checked in the subordinate topic manifest and verifier artifact. |
| `0.17_Mass_Generation` | tau-mass metric | Must be checked in the subordinate topic manifest and verifier artifact. |
| `0.18_Mathnicry` | quantum entropy metric | Must be checked in the subordinate topic manifest and verifier artifact. |
| `0.20_Atomic_Physics` | H-alpha error metric | Must be checked in the subordinate topic manifest and verifier artifact. |
| `0.24_Artificial_Intelligence` | initial loss metric | Must be checked in the subordinate topic manifest and verifier artifact. |
| `0.25_Strategy_Power_Economics` | economic omega metric | Must be checked in the subordinate topic manifest and verifier artifact. |

## Integration Artifact Inputs

| Dependency | Artifact path | Role |
| :-- | :-- | :-- |
| `0.1_Galaxy_Rotation_Problem` | `docs/topics/0.1_Galaxy_Rotation_Problem/Result/artifacts/galaxy_rotation_validation.json` | Galaxy/halo metric dependency. |
| `0.6_Electroweak_Physics` | `docs/topics/0.6_Electroweak_Physics/Result/artifacts/0_6_electroweak_physics_verification.json` | Weinberg-angle metric dependency. |
| `0.10_Fluid_Dynamics_Chaos` | `docs/topics/0.10_Fluid_Dynamics_Chaos/Result/artifacts/fluid_benchmark_validation.json` | Critical Reynolds metric dependency. |
| `0.17_Mass_Generation` | `docs/topics/0.17_Mass_Generation/Result/artifacts/0_17_mass_generation_verification.json` | Tau-mass metric dependency. |
| `0.18_Mathnicry` | `docs/topics/0.18_Mathnicry/Result/artifacts/0_18_mathnicry_verification.json` | Quantum entropy metric dependency. |
| `0.20_Atomic_Physics` | `docs/topics/0.20_Atomic_Physics/Result/artifacts/0_20_atomic_physics_verification.json` | Atomic H-alpha/Rydberg metric dependency. |
| `0.24_Artificial_Intelligence` | `docs/topics/0.24_Artificial_Intelligence/Result/artifacts/0_24_artificial_intelligence_verification.json` | AI scaling/sparsity metric dependency. |
| `0.25_Strategy_Power_Economics` | `docs/topics/0.25_Strategy_Power_Economics/Result/artifacts/0_25_strategy_power_economics_verification.json` | Economic omega metric dependency. |

Repository note:

- This topic should not copy subordinate datasets into its own `Data/` folder.
- The correct hardening path is to record dependency artifact IDs/statuses/hashes and inherit their limitations.
- A `WARN` or `FAIL` subordinate artifact blocks theory-level closure even if the `0.0` engine run completes.
