# Data Manifest

Current data reality status: `real source referenced`

The current primary verifier uses the topic-local EHT working-copy package. This is
source-referenced and hash-tracked, but it is not yet a fully normalized upstream archive.

| Item | Local path | Source | Provenance status |
|:--|:--|:--|:--|
| EHT shadow working copy | `Data/03_Research/black_hole_data.json` | Event Horizon Telescope Collaboration M87* 2019 and Sgr A* 2022 values, transcribed working copy | sha256 `5a785571d04ce4c09758ca5d8ef925423c472e62c5e9487db4575f6bf50af85b`; primary benchmark input |
| EHT metadata working copy | `Data/03_Research/black_hole_metadata.json` | Topic-local metadata for EHT working copy | sha256 `26adc5c3ed778a65a92218f6d5e4bd0389920f9e6b1205a2a03e4ccc1fb484cb`; context input |
| plasma records | `Data/03_Research/plasma_records.json` | Topic-local diagnostic input | sha256 `f1a00b3a1d2e5b8774096b5dc224e73943fadabe8a8615230c9610f75d3f619b`; not primary EHT gate |
| Black-hole catalog | `Data/BlackHole_Catalog.csv` | Black-hole observation working copy | sha256 `14be7b52ed4376613f7bf6a162c602f07ed35fe7d3292ff0394e6c3fb7600573`; secondary catalog context |

## Unit and benchmark roles

| Dataset | Unit convention | Benchmark role |
| :-- | :-- | :-- |
| `black_hole_data.json` | mass in solar masses; M87* distance in Mpc; Sgr A* distance in kpc; shadow in microarcseconds | Primary EHT shadow-size benchmark |
| `BlackHole_Catalog.csv` | mass in solar masses; distance in Mpc; spin dimensionless | Secondary context only |
| CCBH Shen/Kormendy sources | not present in repo external cache | Blocked secondary path until archived under `docs/data/external/...` |

Repository note:

- This manifest was created during the repo standards pass and should be tightened further in a later provenance-normalization wave.
- Until upstream URLs, DOIs, preprocessing notes, and hashes are frozen, treat the dataset package as an internal working copy rather than an archival release.
- The CCBH verifier path must not be treated as source-backed until its raw upstream FITS/CSV sources are stored in the shared external cache and linked here.
