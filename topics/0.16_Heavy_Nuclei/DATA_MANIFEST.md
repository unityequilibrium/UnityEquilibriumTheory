# Data Manifest

Current data reality status: manifested real dataset for selected AME2020 working copies; fragment coverage still incomplete for the primary fission Q-value.

## Primary Verifier Input

| Item | Local path | Source | DOI / stable ID | Units | Benchmark role | Provenance status |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| AME2020 heavy-nuclei working copy | `Data/03_Research/ame2020_heavy_nuclei.json` | Wang et al., AME2020 atomic mass evaluation | `10.1088/1674-1137/abddaf` | binding energy `keV`; mass excess `keV` | U-235 binding checkpoint in primary fission artifact | Source label and DOI present; local hash recorded by verifier. |

## Secondary Inputs

| Item | Local path | Source | Units | Role | Use policy |
| :-- | :-- | :-- | :-- | :-- | :-- |
| AME2020 heavy binding subset | `Data/03_Research/ame2020_heavy/ame2020_heavy.json` | AME2020 working copy | total `BE_MeV`, `BE_per_A` MeV | secondary heavy-binding comparison | Not primary until artifact rows and thresholds are frozen. |
| AME2020 raw mass text | `Data/AME2020_mass.txt` | AME2020 local text copy | AME fixed-width text fields | raw/local reference package | Parser currently falls back to curated checkpoints in engine code; do not cite as fully parsed without parser audit. |
| Data helper | `Data/03_Research/download_data.py` | topic-local helper | n/a | provenance/data-writing helper | Not an upstream source. |

## Preprocessing

- Primary verifier converts U-235 AME binding energy from keV to MeV.
- Ba-141 and Kr-92 fragment binding energies are currently computed by the SEMF/UET bridge rather than loaded from AME2020.
- This missing fragment provenance is recorded as the reason for artifact status `WARN`.

## Data Policy

- Raw external AME/NUBASE files should be stored under `docs/data/external/...` when normalized for shared use.
- Topic-specific curated subsets remain under `docs/topics/0.16_Heavy_Nuclei/Data/...`.
- No downstream topic may use `0.16` as fission-energy or island-of-stability evidence until source-locked fragment and stability artifacts exist.
