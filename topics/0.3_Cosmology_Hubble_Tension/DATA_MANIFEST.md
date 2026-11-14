# Data Manifest

| Item | Local path | Source | Provenance status |
|:--|:--|:--|:--|
| Planck 2018 reference values | `docs/data/external/cosmology/hubble_tension/planck_2018/source_record.json` | Planck Collaboration, DOI `10.1051/0004-6361/201833910` | Source-locked scalar H0 value |
| SH0ES 2022 reference values | `docs/data/external/cosmology/hubble_tension/shoes_2022/source_record.json` | Riess et al. 2022, DOI `10.3847/2041-8213/ac5c5b` | Source-locked scalar H0 value |
| Fine-structure constant | `docs/data/external/constants/codata/fine_structure/source_record.json` | NIST/CODATA inverse fine-structure constant | Source-locked constant record; repository value is truncated |
| Hubble source-lock manifest | `Data/03_Research/source_lock_manifest.json` | Topic-derived provenance package | Primary verifier hashes this manifest and source records |
| JWST high-z calibration file | `Data/03_Research/jwst_highz_calibration.csv` | Topic-local working data | Needs a fuller provenance note before external release |

## Unit and benchmark roles

| Dataset / constant | Unit convention | Benchmark role |
| :-- | :-- | :-- |
| Planck H0 | `km s^-1 Mpc^-1` | early/CMB H0 baseline |
| SH0ES H0 | `km s^-1 Mpc^-1` | late/local H0 comparator |
| `alpha_em` | dimensionless | no-fit bridge constant for `beta_frame = sqrt(alpha_em)` |
| JWST high-z calibration | mixed topic-local columns | future high-z diagnostic only |

Repository note:

- The current structured topic pass focuses on explicit citation and local-path tracking.
- Full observational packaging remains future work.
- The current primary verifier uses scalar published H0 values, not full Planck chains,
  SH0ES covariance tables, BAO data, or SN likelihoods.
