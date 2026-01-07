# 🗺️ Legacy Data Map (UET v0.8.7)

**Purpose:** Bridge the user's legacy `research` folder with the new `research_v3` analysis layer.
**Status:** Audited 2025-12-30.

---

## 1. Validated Data Sources

### 🌌 Astronomy & Physics
**Source:** `research/(เอ๋อ)01-physics`
- **Galaxies:** `black-hole-uet/01_data/kormendy_ho_data/kormendy_ho_ellipticals_sample.csv` (Real Kormendy-Ho Relation data).
- **Gravity:** `01-gravity-uet/01_data` (Folder exists, check for `SPARC` or other rotation curve data).

### 📉 Interdisciplinary (Econ/Bio/Social)
**Source:** `research/(เอ๋อ)02-interdisciplinary`
- **Markets:** `econophysics/market_data/*.csv`
    - Contains: `AAPL.csv`, `SP500.csv`, `NASDAQ.csv`, `VIX.csv`, etc. (13 Files).
- **Networks:** `02-network-science/01_data/*.txt`
    - Contains: `facebook_combined.txt` (Social), `ca_grqc.txt` (Collaboration), `email_enron.txt` (Communication).
- **Biology:** `03-biophysics/01_data/`
    - Status: ⚠️ **MISSING DATA**. Only `chemotaxis_analysis.py` found.
    - *Action:* We will skip Bio validation in `real_massive_test.py` or search strictly for `.csv` if hidden elsewhere.

---

## 2. Integration Strategy
The script `universal_legacy_test.py` will load these files **in place** (using relative paths).
It will NOT move, rename, or copy them.

### Data Path Constants
```python
LEGACY_MARKET_DIR = r"../../research/(เอ๋อ)02-interdisciplinary/econophysics/market_data"
LEGACY_GALAXY_FILE = r"../../research/(เอ๋อ)01-physics/black-hole-uet/01_data/kormendy_ho_data/kormendy_ho_ellipticals_sample.csv"
LEGACY_NETWORK_DIR = r"../../research/(เอ๋อ)02-interdisciplinary/02-network-science/01_data"
```
