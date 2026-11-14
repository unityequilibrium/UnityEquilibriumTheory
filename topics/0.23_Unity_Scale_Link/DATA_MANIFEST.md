# Data Manifest

Current data reality status: "manifested real dataset with local snapshots and explicit source-lock limitations"

| Item | Local path | Source | Unit convention | Benchmark role | Provenance status |
|:--|:--|:--|:--|:--|:--|
| create_unified_data.py | `data/03_Research/create_unified_data.py` | Topic-local data builder | n/a | Rebuilds unified local benchmark files | Local script; generation inputs need source-lock. |
| source_lock_manifest.json | `data/03_Research/source_lock_manifest.json` | Topic-derived source-lock package | n/a | Binds verifier inputs to finance source metadata and inherited core-topic artifacts | Present; SHA-256 `c909161011c3cef45433542753e50bf6e6c216c914e9a07fd41122310e29fe4c`; retains WARN until external query logs and held-out datasets exist. |
| Yahoo finance source manifest | `docs/data/external/finance/yahoo_snapshots/0_23_unity_scale_link/source_manifest.json` | Yahoo Finance style OHLCV source metadata for local snapshots | Date in ISO format; OHLC prices in source quote units; volume in source-reported units | External provenance record for finance inputs | Present; SHA-256 `84adb0cc8471f6e96119ea09fd30b42383f8f6c8504371df47803850d7f6c908`; original query logs still missing. |
| Bitcoin_yahoo_real.csv | `data/03_Research/economy/Bitcoin_yahoo_real.csv` | Yahoo-style local market snapshot | Date/time series with price columns | Finance scale/noise comparison | Retrieval date/query metadata missing. |
| DowJones_yahoo_real.csv | `data/03_Research/economy/DowJones_yahoo_real.csv` | Yahoo-style local market snapshot | Date/time series with price columns | Finance scale/noise comparison | Retrieval date/query metadata missing. |
| EUR_USD_yahoo_real.csv | `data/03_Research/economy/EUR_USD_yahoo_real.csv` | Yahoo-style local FX snapshot | Date/time series with price columns | Finance scale/noise comparison | Retrieval date/query metadata missing. |
| SP500_yahoo_real.csv | `data/03_Research/economy/SP500_yahoo_real.csv` | Yahoo-style local market snapshot | Date/time series with close/adjusted-close column | Primary verifier economy volatility input | Retrieval date/query metadata missing. |
| scale_mapping.json | `data/03_Research/scale_mapping.json` | Topic-local scale mapping | mixed scale units; requires audit | Kappa/running hypothesis map | Source chain and uncertainty open. |
| unified_system_data.json | `data/03_Research/unified_system_data.json` | Topic-local combined benchmark | mixed normalized fields | Cross-domain exploratory benchmark | Must not be treated as raw external data. |
| Research_Cross_Domain.py | `Code/03_Research/Research_Cross_Domain.py` | Primary verifier script | normalized fields, log-return volatility, dimensionless Omega | Writes structured artifact and warning state | SHA-256 `217cde3b27842e3cabbc0b40841eeb46c9abaef588978f473e51fccb8c8b4813`; code artifact, not an external source. |

## External Source Targets

| Source target | Required storage path | Current status |
|:--|:--|:--|
| Yahoo/finance raw query metadata and snapshots | `docs/data/external/finance/yahoo_snapshots/0_23_unity_scale_link/` | Source metadata manifest stored; original query logs/retrieval timestamp/upstream response hashes still open. |
| Real neural/EEG data for seizure/normal comparison | `docs/data/external/biophysics/eeg/` | Not present; current neural fields are synthetic. |
| Scale calibration sources from `0.5`, `0.6`, `0.13` | respective topic `Data/` plus `docs/data/external/...` | Dependency links identified; source-locked propagation open. |
| Cosmology/high-redshift source files | `docs/data/external/cosmology/...` | Topic-local summaries exist; raw provenance open. |

Repository note:

- This manifest was created during the repo standards pass and should be tightened further in a later provenance-normalization wave.
- Until upstream query logs, retrieval timestamps, preprocessing scripts, and upstream response hashes are frozen, treat the dataset package as source-referenced local snapshots rather than an archival release.
