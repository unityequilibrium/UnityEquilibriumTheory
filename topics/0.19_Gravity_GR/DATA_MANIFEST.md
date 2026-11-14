# Data Manifest

Current data reality status: manifested real dataset for the primary CODATA working copy; secondary gravity datasets are source-labeled but need normalization.

## Primary Verifier Input

| Item | Local path | Source | DOI / stable ID | Units | Benchmark role | Provenance status |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| CODATA 2018 gravity constants | `Data/03_Research/codata_2018_gravity.json` | NIST/CODATA recommended values | `10.1103/RevModPhys.93.025010` | `G` m^3 kg^-1 s^-2; `c` m/s; `hbar` J s; Planck units SI | primary verifier input for source-constant checkpoint | Source label and DOI present; verifier records local SHA256. |

## Secondary Inputs

| Item | Local path | Source | Units | Role | Use policy |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Eot-Wash short-range gravity curve | `Data/03_Research/eotwash_2007_data.json` | Kapner et al. 2007 PRL 98, 021101 | `lambda_m`; `alpha_strength` dimensionless | secondary Yukawa comparator | Not primary until a short-range artifact is added. |
| Eot-Wash 2008 local package | `Data/03_Research/eotwash_2008.json` | topic-local Eot-Wash working copy | short-range gravity fields | secondary comparator | Needs source/DOI normalization before claim use. |
| MICROSCOPE 2022 equivalence dataset | `Data/03_Research/microscope_2022.json` | MICROSCOPE Collaboration, PRL 129, 121102 | `eta` dimensionless | secondary equivalence-principle comparator | Not primary until eta verifier compares against uncertainty. |
| Data helper scripts | `Data/03_Research/download_data.py`, `Data/03_Research/download_references.py` | topic-local helpers | n/a | data/source helper scripts | Not upstream sources. |

## Preprocessing

- Primary verifier reads CODATA values directly from JSON and compares `G` to the engine package.
- Planck-unit outputs are derived from engine constants and recorded as metrics.
- No light-bending, perihelion, or singularity dataset is used in the primary artifact.

## Data Policy

- Shared raw constants may later move to `docs/data/external/constants/...`, but this topic must still record exact shared paths and hashes.
- Secondary Eot-Wash and MICROSCOPE data cannot support README claims until they have dedicated artifacts.
