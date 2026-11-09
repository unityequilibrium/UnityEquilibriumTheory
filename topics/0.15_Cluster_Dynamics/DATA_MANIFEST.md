# Data Manifest

Current data reality status: real source referenced, topic-local working copies.

## Primary Diagnostic Dataset

| Item | Local path | Source label | Units | Benchmark role | Provenance status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Bullet Cluster coordinate/offset working copy | `Data/Bullet_Cluster_Coordinates.json` | `Clowe et al. 2006 (ApJ 648:L109-L113)` | offset `kpc`; scale `1 arcsec = 4.415 kpc`; RA/Dec labels | primary input for qualitative separation-sign artifact | Real source label present; DOI/URL and transcription audit still need to be frozen. |

The primary verifier records the SHA256 hash of this file in `Result/artifacts/0_15_cluster_dynamics_verification.json`.

## Secondary Cluster Working Copies

| Item | Local path | Source label | Units | Role | Use policy |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Chandra relaxed cluster sample | `Data/03_Research/chandra_clusters_2006.json` | Vikhlinin et al. 2006, ApJ 640, DOI `10.1086/500288` | `T_keV`, `M500_Msun`, `r500_Mpc` | secondary mass-temperature benchmark | Not part of current primary verifier. |
| Optical virial mass estimates | `Data/03_Research/cluster_virial_1998.json` | Girardi et al. 1998, ApJ 505, DOI `10.1086/306157` | velocity `km/s`, mass `Msun`, radius `Mpc` | secondary virial comparator | Needs artifact rows before claim promotion. |
| Simplified virial sample | `Data/03_Research/cluster_virial_data.json` | topic-local simplified working copy | mass in local scale units; radius `Mpc` | legacy diagnostic | Do not cite as source-backed without normalization. |
| Data helper | `Data/03_Research/download_data.py` | topic-local script | n/a | source-label/data-writing helper | Not an upstream source. |
| JWST early galaxies | `Data/03_Research/jwst_early_galaxies.json` | topic-local working copy | redshift/mass fields | separate formation-rate lane | Excluded from current cluster-offset verifier. |
| Planck SZ sample | `Data/03_Research/planck_sz_2016.json` | topic-local working copy | SZ/mass fields | future cluster benchmark | Excluded until a dedicated verifier is added. |

## Preprocessing

- The current primary verifier does not transform RA/Dec into physical offsets; it uses the already recorded `offset_kpc` fields.
- The toy model output is dimensionless model units and is not converted to kpc.
- This mismatch is intentionally recorded as a `WARN` limitation.

## Data Policy

- Raw external archival files should be stored under `docs/data/external/...` when captured.
- Topic-normalized or derived working copies remain under `docs/topics/0.15_Cluster_Dynamics/Data/...`.
- No downstream topic may treat the toy offset diagnostic as a calibrated cluster-lensing dataset.
