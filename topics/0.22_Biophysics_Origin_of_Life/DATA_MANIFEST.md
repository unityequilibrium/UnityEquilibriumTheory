# Data Manifest: 0.22 Biophysics & Origin of Life

Current data reality: source-referenced EEG/omics context, a synthetic primary biomarker verifier, a separate synthetic finite HP model input, and local synthetic_placeholder EEG mechanics files.

The topic package contains provenance context, not an archival biomedical dataset. Source records identify intended upstream datasets; they do not make local summaries or placeholders into measurements.

| Input | Local path | Source identity | Data class | Units / preprocessing | Benchmark role | Status |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Source-lock manifest | data/03_Research/source_lock_manifest.json | Topic manifest bound to three source records | source_referenced_context_plus_synthetic_benchmark | JSON metadata | Binds roles and limitations | Hash in run contract |
| CHB-MIT reference | data/03_Research/chb_mit_reference.json | PhysioNet CHB-MIT, DOI 10.13026/C2K01R | source_referenced_only | Hz/seconds as declared; no raw EDF | Future EEG context | Raw recordings open |
| CHB01 summary | data/03_Research/chb01_summary.txt | CHB-MIT source record | source_referenced_only | Local text summary | Discussion reference | Not raw data |
| Seizure phase data | data/03_Research/seizure_phase_data.json | Derived from CHB-MIT | source_referenced_only | Dimensionless phase summaries | Discussion reference | Raw windows open |
| Bonn Z sample | data/Bonn_EEG/Z.txt | Bonn source target, DOI 10.1103/PhysRevE.64.061907 | synthetic_placeholder | Repeated mechanics-test pattern | Future mechanics input | Not source-locked |
| Bonn S sample | data/Bonn_EEG/S.txt | Bonn source target, DOI 10.1103/PhysRevE.64.061907 | synthetic_placeholder | Repeated mechanics-test pattern | Future mechanics input | Not source-locked |
| CHB-MIT source record | docs/data/external/biophysics/eeg/chb_mit/source_record.json | PhysioNet source record | source_referenced_only | Metadata only | Provenance anchor | Raw data open |
| Bonn source record | docs/data/external/biophysics/eeg/bonn/source_record.json | Bonn source target | source_referenced_only | Metadata only | Provenance anchor | Package/license open |
| TCGA source record | docs/data/external/biophysics/omics/tcga/source_record.json | NCI GDC/TCGA target | source_target_only | No expression matrix | Future omics source | Matrix/cohort open |
| Synthetic biomarker matrix | Generated in active verifier | Seeded local generator | synthetic | Arbitrary expression units | Current internal benchmark | Seed in artifact |
| HP benchmark definition | data/03_Research/protein_folding_hp_benchmark.json | Topic-local historical H/P sequence and finite-model contract | synthetic | Integer 2-D lattice; dimensionless HP model units; no preprocessing | Protein lane internal algorithmic benchmark | SHA-256 in protein artifact |


## Protein-folding dynamics Wave-0 data package

The dynamic lane is source-referenced only. The target source identities and
selection policy live in DYNAMICS_DATA_MANIFEST.json; no external raw file has
been downloaded or frozen in this wave.

| Input/target | Local path | Data class | Unit/provenance contract | Benchmark role | Status |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Dynamic data manifest | DYNAMICS_DATA_MANIFEST.json | source_referenced_only | Source URL/terms, local path, preprocessing, units, and SHA-256 fields are required before use | Cohort and source gate | Present; cohort empty |
| KineticDB | no local copy | source_target_only | Preserve rate units and log-rate transformations | Folding/unfolding kinetics | Not downloaded |
| PFD 2.0 | no local copy | source_target_only | Preserve temperature, denaturant, rate, and free-energy units | Conditions and kinetic cross-check | Not downloaded |
| PFDB standardized | no local copy | source_target_only | Record temperature correction separately | Standardized kinetic cross-check | Not downloaded |
| RCSB PDB | no local copy | source_target_only | Coordinate units and topology preparation must be recorded | Structure endpoint/chain identity | Not downloaded |
| CASP | no local copy | source_target_only | Edition, target set, terms, and evaluation protocol required | Future holdout/reference | Not downloaded |

The first cohort is blocked until 12 protein-level records are source-locked:
8 development and 4 holdout. Synthetic HP data is explicitly excluded from
this cohort.

## Hash and identity rule

The primary verifier artifact and shared runner contract record SHA-256 and byte size for all nine declared context inputs. The protein artifact records the SHA-256 of its one synthetic model-definition input. A future source-backed gate must additionally record original filename, license/terms, exact record or cohort identity, preprocessing, units, and baseline configuration.

## Archived duplicates and helpers

- Exact duplicate data/03_Research/03_Research files are archived under data/legacy/duplicate_03_Research/ with preserved hashes.
- Download helpers that can create convenience or placeholder files are archived under data/legacy/downloaders/ and are not part of the active path.
- Lowercase data/ remains the canonical topic path for this wave; no Data/ path is treated as active.

## Required next evidence

1. Licensed raw CHB-MIT windows with record IDs, preprocessing, hashes, and held-out metrics.
2. Authenticated Bonn package identity, license, subset identity, sampling rate, and raw-file hashes.
3. A real TCGA/GDC matrix with assay units, cohort selection, preprocessing, hashes, and comparator statistics.
4. A source-locked 12-protein dynamics cohort with 8 development and 4 holdout entries.
5. Pinned OpenMM/MDTraj/openmmtools runtime, hashed AMBER ff14SB/TIP3P assets, and passing CPU/trajectory smoke tests.
6. A source-backed protein structure benchmark such as a governed PDB/CASP package if the lane expands beyond the finite HP model; the current deterministic HP artifact does not require external data.
