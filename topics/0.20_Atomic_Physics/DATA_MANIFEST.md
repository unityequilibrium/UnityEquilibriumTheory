# Data Manifest

Current data reality status: manifested real dataset for NIST/CODATA working copies used by the primary hydrogen-spectrum verifier.

## Primary Verifier Inputs

| Item | Local path | Source | DOI / URL | Units | Benchmark role | Provenance status |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| NIST hydrogen spectrum working copy | `Data/03_Research/nist_hydrogen_spectrum.json` | NIST Atomic Spectra Database v5.11 | DOI `10.18434/T4W30F`; URL `https://physics.nist.gov/asd` | vacuum/air wavelength `nm`; frequency `THz`; energy `eV` | primary spectral-line benchmark | Source label and DOI/URL present; verifier records local SHA256. |
| CODATA atomic constants working copy | `Data/03_Research/codata_2018_atomic.json` | CODATA recommended values | DOI `10.1063/5.0064853` | `R_H`, `R_infinity` in m^-1; `a_0` m; energies/constants SI | primary constant benchmark | Source label and DOI present; verifier records local SHA256. |

## Secondary Inputs

| Item | Local path | Source | Units | Role | Use policy |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Hydrogen level working copy | `Data/03_Research/hydrogen_spectra_data.json` | topic-local source-labeled level package | energy `eV` | secondary level-energy lane | Not primary until a level-energy artifact is added. |
| NIST hydrogen visible CSV | `Data/NIST_Hydrogen_Visible.csv` | NIST local visible-line copy | wavelength fields in CSV | engine demo input | Not used by the primary artifact. |
| NIST helium visible CSV | `Data/NIST_Helium_Visible.csv` | NIST local visible-line copy | wavelength fields in CSV | future helium/many-electron lane | Excluded from current claim scope. |
| Data helper scripts | `Data/Download_NIST.py`, `Data/03_Research/download_data.py`, `Data/03_Research/download_references.py` | topic-local helpers | n/a | data/source helper scripts | Not upstream sources. |

## Preprocessing

- Primary verifier uses vacuum wavelengths from the NIST hydrogen working copy.
- It computes the Rydberg geometric term from parsed transitions.
- It compares predicted vacuum wavelengths from CODATA `R_H` against NIST vacuum wavelengths.
- Air wavelengths are preserved in the data but not used in the primary metric.

## Data Policy

- Raw external spectral source captures may later move to `docs/data/external/...`; this topic must still record exact local paths and hashes.
- Hydrogen benchmark results cannot be used as evidence for helium, fine-structure, Lamb-shift, or many-electron claims.
