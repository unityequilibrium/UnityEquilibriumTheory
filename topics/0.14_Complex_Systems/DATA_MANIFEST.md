# Data Manifest

Current data reality status: "real source referenced with derived RR working files"

This topic contains several local working datasets across HRV, economy, climate, inequality, social networks, ledgers, and validation branches. The current primary verifier uses the HRV package below. The HRV files are now tied to a PhysioNet/MIT-BIH Normal Sinus Rhythm Database source record and record IDs, but remain derived RR working copies until original source files, extraction scripts, and preprocessing logs are archived.

## Primary Verifier Input Package: HRV RR Intervals

| Item | Local path | Bytes | SHA256 | Source | Provenance status | Unit convention | Benchmark role |
| :-- | :-- | --: | :-- | :-- | :-- | :-- | :-- |
| `source_record.json` | `docs/data/external/biophysics/hrv/mit_bih_nsrdb/source_record.json` | 1354 | `740026bd57987bfe3bd5868a16e2ce38c1a2082ea4696f33c10db7a4425adba3` | PhysioNet MIT-BIH Normal Sinus Rhythm Database v1.0.0 | Source record present; original `.dat/.hea/.atr` records and extraction logs not stored. | RR interval target in seconds after extraction/filtering. | External source identity for HRV verifier. |
| `source_lock_manifest.json` | `Data/03_Research/biology_hrv/source_lock_manifest.json` | 2722 | `05aa2c059e520f00d1eb2fd830c3a919876ea67dd5fdce5a3bbc0d49943d7e97` | Topic-derived source-lock package | Maps record IDs to local CSV hashes and runtime preprocessing contract. | RR intervals seconds; runtime filter `0.3 < rr < 2.0`. | Provenance package for primary HRV verifier. |
| `hrv_stress.csv` | `Data/03_Research/biology_hrv/hrv_stress.csv` | 726 | `948606f15b173c039d967ffe5d5aa97c5af85afeeddad43ec314919d9ce7694b` | Topic-local working copy or generated benchmark input | Local copy only; upstream identity not frozen. | Script reads first numeric column as RR-like intervals. | Local stress/control-style working input; not currently loaded by the primary script because it filters `physionet_*_rr.csv`. |
| `physionet_16265_rr.csv` | `Data/03_Research/biology_hrv/physionet_16265_rr.csv` | 2624855 | `5c0ba598b3d98916bd7e7b144748c4a97cd1381f84217d4d728d57d92d6d98ce` | MIT-BIH NSRDB record `16265`, PhysioNet-derived topic-local RR copy | Source-referenced derived RR copy; extraction method not frozen. | RR interval in seconds after numeric coercion; verifier keeps `0.3 < rr < 2.0`. | Primary HRV verifier input. |
| `physionet_16272_rr.csv` | `Data/03_Research/biology_hrv/physionet_16272_rr.csv` | 2525821 | `59550c71f4188854439efa6f7b43b51321302390d82eaa36cacf0671c3e70ecc` | MIT-BIH NSRDB record `16272`, PhysioNet-derived topic-local RR copy | Source-referenced derived RR copy; extraction method not frozen. | RR interval in seconds after numeric coercion; verifier keeps `0.3 < rr < 2.0`. | Primary HRV verifier input. |
| `physionet_16273_rr.csv` | `Data/03_Research/biology_hrv/physionet_16273_rr.csv` | 2342547 | `07387f540056692af7fb203d14e874f56e021de222e77e5cae9ad96d65b11880` | MIT-BIH NSRDB record `16273`, PhysioNet-derived topic-local RR copy | Source-referenced derived RR copy; extraction method not frozen. | RR interval in seconds after numeric coercion; verifier keeps `0.3 < rr < 2.0`. | Primary HRV verifier input. |
| `physionet_16420_rr.csv` | `Data/03_Research/biology_hrv/physionet_16420_rr.csv` | 2663361 | `f3cd3b331afd16451a5237b3f9fe5f0a9e01312a7e4a69e8337db0b1b6589162` | MIT-BIH NSRDB record `16420`, PhysioNet-derived topic-local RR copy | Source-referenced derived RR copy; extraction method not frozen. | RR interval in seconds after numeric coercion; verifier keeps `0.3 < rr < 2.0`. | Primary HRV verifier input. |
| `physionet_16483_rr.csv` | `Data/03_Research/biology_hrv/physionet_16483_rr.csv` | 2718611 | `94c53732e83f41371cdca47cc8e1fecb0e39798fe3a2d042f63ebb4f8f0cbfe4` | MIT-BIH NSRDB record `16483`, PhysioNet-derived topic-local RR copy | Source-referenced derived RR copy; extraction method not frozen. | RR interval in seconds after numeric coercion; verifier keeps `0.3 < rr < 2.0`. | Primary HRV verifier input. |

## Other Topic-Local Working Data

- Economy files under `Data/03_Research/economy/` include Yahoo-style local CSVs and a bubble sample file.
- Climate files under `Data/03_Research/climate/` include NASA/NOAA-labeled local CSVs.
- Inequality files under `Data/03_Research/inequality/` include World Bank-labeled local CSVs.
- Social, ledger, validation, brain, plasma, and black-hole working files are present under `Data/03_Research/`.

These branches are not yet promoted to source-backed verifier inputs. Before they can support claims, each branch needs upstream source identity, raw-source storage or citation, preprocessing notes, hashes, unit convention, baseline role, and an artifact-producing verifier.

## Repository Note

- Until raw PhysioNet files, extraction commands, preprocessing notes, and hashes are frozen for each domain branch, treat this data package as source-referenced derived working copies rather than an archival release.
- Raw external sources, when re-fetched or normalized, must be stored under `docs/data/external/...`.
- Topic-specific derived data must remain under `docs/topics/0.14_Complex_Systems/Data/...`.
