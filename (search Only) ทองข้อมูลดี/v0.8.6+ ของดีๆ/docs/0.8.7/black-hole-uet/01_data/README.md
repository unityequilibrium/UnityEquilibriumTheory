# CCBH Analysis Pipeline
## Cosmologically Coupled Black Holes - Day 3

### Quick Start

```bash
# 1. Install dependencies
pip install numpy scipy matplotlib astropy

# 2. Generate test data
python toy_data_generator.py

# 3. Run analysis (test)
python run_all.py toy_quasar_catalog.fits

# Expected: k ≈ 3.0 (within errors)
```

### Real Data Analysis

```bash
# Download Shen 2011 DR7 catalog from:
# http://quasar.astro.illinois.edu/BH_mass/dr7.htm
# or
# https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/194/45

# Run analysis
python run_all.py DR7_BH_cat_final.fits
```

### Files

| File | Description |
|------|-------------|
| `run_all.py` | Master script - runs everything! |
| `ccbh_analysis.py` | Core fitting: M ∝ a^k |
| `data_loader.py` | Load FITS catalogs |
| `quality_cuts.py` | Clean data |
| `visualize.py` | Make plots |
| `toy_data_generator.py` | Generate test data |

### Output

After running `python run_all.py <catalog>`, you get:

- `raw_data.png` - All quasars plotted
- `ccbh_fit.png` - Main result with fit
- `bootstrap_k.png` - Error distribution
- `comparison_summary.png` - vs Farrah (2023)

### The Key Result

We measure **k** in the scaling relation:

```
M_BH ∝ a^k
```

Where:
- `a = 1/(1+z)` is the cosmic scale factor
- `k ≈ 3` means cosmological coupling (Farrah 2023)
- `k ≈ 0` means no coupling (standard physics)

### Decision Matrix

| Result | Interpretation |
|--------|---------------|
| k ≈ 3.0 ± 0.5 | Supports CCBH! GO! |
| k ≈ 1-2 | Partial coupling, interesting |
| k ≈ 0 | No coupling, standard physics |
| k < 0 | BH mass decreases with time (weird!) |

### Requirements

- Python 3.8+
- numpy
- scipy
- matplotlib
- astropy (for FITS files)
