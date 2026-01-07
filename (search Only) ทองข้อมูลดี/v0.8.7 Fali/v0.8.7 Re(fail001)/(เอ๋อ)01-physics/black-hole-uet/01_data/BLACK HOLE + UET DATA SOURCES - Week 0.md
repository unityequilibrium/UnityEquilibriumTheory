# BLACK HOLE + UET DATA SOURCES - Week 0

## 🎯 PRIMARY DATA SOURCE - FOUND! ✓

### Shen et al. (2011) SDSS DR7 Quasar Catalog

**Status:** PUBLIC, AVAILABLE NOW **Paper:** ApJS, 194, 45 (2011) **ArXiv:** 1006.5178

**Contents:**

- Number of objects: 105,783 quasars
- Redshift range: 0.1 < z < 5.0
- Black hole masses: Virial estimates from Hβ, MgII, CIV
- Luminosities: Continuum measurements
- Emission lines: Hα, Hβ, MgII, CIV
- Additional: Radio properties, BAL flags

**Download Locations:**

1. Primary: http://quasar.astro.illinois.edu/BH_mass/dr7.htm
2. VizieR: https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/194/45
3. SDSS DAS: https://das.sdss.org/va/qso_properties_dr7/

**File Format:** FITS table **Size:** ~50 MB (compressed) **Columns needed:**

- SDSS_NAME: Object identifier
- Z: Redshift
- LOGBH_*: Log black hole mass (solar masses)
- LOGLBOL: Log bolometric luminosity
- FLAGS: Quality flags

**Quality Criteria (for analysis):**

- S/N > 6 per pixel (for line measurements)
- Uniformly selected sample (not all 105k are uniform)
- Error flags checked
- Exclude BAL quasars for virial mass

**Use for:**

- M_BH vs z correlation
- CCBH k parameter fitting
- Statistical power (large N)
- Redshift coverage

---

## 📈 SUPPLEMENTARY DATA SOURCES

### 1. Shen et al. (2022) SDSS DR16 Quasar Catalog UPDATE

**Status:** NEWER VERSION AVAILABLE! **Paper:** ApJS, 261, 15 (2022) **DOI:** 10.3847/1538-4365/ac9ead

**Improvements over DR7:**

- Number: ~750,000 quasars (7× more!)
- Better redshift coverage
- More refined measurements
- Fainter objects included

**Pros:**

- Much larger sample
- Better statistics
- More recent

**Cons:**

- More complex (multiple surveys)
- Selection function more complicated
- Need to understand biases

**Decision:**

- Week 0: Use DR7 (simpler, well-understood)
- Full project: Can upgrade to DR16

---

### 2. EHT M87* and Sgr A* Parameters

**Status:** PUBLIC (multiple papers)

__M87_ (2019):_*

- Mass: (6.5 ± 0.7) × 10^9 M_solar
- Distance: 16.8 ± 0.8 Mpc
- Shadow diameter: 42 ± 3 μas
- Source: ApJL 875, L1 (2019)

__Sgr A_ (2022):_*

- Mass: (4.0 ± 0.2) × 10^6 M_solar
- Distance: 8.3 kpc
- Shadow diameter: 52 ± 3 μas
- Source: ApJL 930, L12 (2022)

**Use for:**

- Direct mass measurements (no virial uncertainties)
- GR tests (shadow size)
- Nearby SMBH constraints
- Precision benchmarks

---

### 3. GWTC-3 Gravitational Wave Catalog

**Status:** PUBLIC **Source:** https://www.gw-openscience.org/GWTC-3/ **Paper:** PRX, 13, 011048 (2023)

**Contents:**

- Stellar-mass black hole mergers
- Masses of component BHs
- Redshifts (cosmological)
- 90 confident events (as of GWTC-3)

**Use for:**

- Stellar-mass BH population
- Test CCBH at low masses
- Merger rates
- Area theorem verification

**Download:**

- FITS tables at gw-openscience.org
- Individual event data
- Posterior samples available

---

### 4. High-z JWST AGN (Lei et al. 2024 data)

**Status:** FROM PAPER (not separate catalog yet) **Source:** 2305.03408 (ArXiv)

**Contents:**

- 3 AGN at z ~ 4.5-7
- Early-type host galaxies
- M_BH and M_star estimates
- Crucial for high-z CCBH test

**Data extraction:**

- Must read from paper tables
- Limited sample (N=3)
- But extreme redshift!

**Use for:**

- High-z CCBH constraint
- k=3 tension check
- Future predictions

---

## 🔧 COMPUTATIONAL TOOLS NEEDED

### Python Libraries (all FREE)

```python
# Data handling
import numpy as np
import pandas as pd
from astropy.io import fits  # For FITS files
from astropy.table import Table
from astropy import units as u
from astropy.cosmology import FlatLambdaCDM

# Statistical analysis
import scipy.stats as stats
from scipy.optimize import curve_fit
import emcee  # For MCMC if needed

# Plotting
import matplotlib.pyplot as plt
import seaborn as sns
import corner  # For posteriors

# Optional but useful
import astroquery  # To query VizieR directly
```

### Analysis Workflow

```python
# 1. Load data
data = fits.open('Shen2011_DR7.fits')[1].data

# 2. Quality cuts
good = (data['LOGBH_HB_VP06'] > 0) & \
       (data['ERR_LOGBH_HB_VP06'] < 0.5) & \
       (data['Z'] > 0.1) & (data['Z'] < 5.0)
       
clean_data = data[good]

# 3. Bin by redshift
z_bins = np.linspace(0.1, 5.0, 20)
M_BH_median = []
for i in range(len(z_bins)-1):
    in_bin = (clean_data['Z'] >= z_bins[i]) & \
             (clean_data['Z'] < z_bins[i+1])
    M_BH_median.append(np.median(clean_data['LOGBH_HB_VP06'][in_bin]))

# 4. Convert to physical masses
z_center = (z_bins[:-1] + z_bins[1:]) / 2
a = 1 / (1 + z_center)  # Scale factor

# 5. Fit CCBH model
def ccbh_model(a, M0, k):
    return np.log10(M0 * a**k)

popt, pcov = curve_fit(ccbh_model, a, M_BH_median)
k_fit, k_err = popt[1], np.sqrt(pcov[1,1])

# 6. Compare
print(f"k_fit = {k_fit:.2f} ± {k_err:.2f}")
print(f"Farrah: k = 3.0 ± 0.5")
print(f"Match? {abs(k_fit - 3.0) < k_err}")
```

---

## 📋 WEEK 0 DATA CHECKLIST

### Day 3: Data Collection ✓

- [✓] Identified Shen 2011 catalog
- [✓] Located download sources (3 mirrors)
- [ ] Downloaded FITS file (need network or manual)
- [ ] Verified file integrity
- [ ] Explored data structure

### Day 4: Data Exploration

- [ ] Load data into Python
- [ ] Check column names and units
- [ ] Apply quality cuts
- [ ] Create summary statistics
- [ ] Make initial plots

### Day 5: Preliminary Analysis

- [ ] Bin data by redshift
- [ ] Calculate medians and errors
- [ ] Fit CCBH model (simple)
- [ ] Extract k parameter
- [ ] Compare with Farrah

### Day 6: Validation

- [ ] Bootstrap error estimates
- [ ] Test different binning
- [ ] Check systematics
- [ ] Compare with EHT masses
- [ ] Cross-check calculations

### Day 7: Decision

- [ ] Summarize findings
- [ ] Assess feasibility
- [ ] Identify challenges
- [ ] Make GO/NO-GO call
- [ ] Plan next steps

---

## 🎯 CRITICAL SUCCESS FACTORS

### For Week 0 to succeed, we need:

1. **Data Access** ✓
    
    - Location: Known
    - Format: FITS (standard)
    - Size: Manageable (~50 MB)
    - Access: PUBLIC
2. **Tools Ready**
    
    - Python: Installed?
    - Libraries: Available?
    - Computing: Sufficient?
    - Time: ~5 hours analysis
3. **Understanding**
    
    - CCBH model: Clear
    - Analysis method: Defined
    - Expected result: Known
    - Interpretation: Prepared
4. **Comparison Data**
    
    - Farrah: k = 3.0 ± 0.5
    - EHT: M87* mass
    - Literature: Values ready
    - Criteria: Established

---

## 🚨 POTENTIAL ROADBLOCKS

### Network Download Issues

**Problem:** Can't download from Claude's computer **Solution:** Download manually on user's computer **Impact:** Delays by 15 minutes (minor)

### Data Format Issues

**Problem:** FITS files unfamiliar **Solution:** Astropy.io.fits handles it **Impact:** Learning curve 30 min (minor)

### Analysis Complexity

**Problem:** Binning/fitting tricky **Solution:** Use standard scipy tools **Impact:** Implementation 2 hours (moderate)

### Selection Effects

**Problem:** Catalog has biases **Solution:** Use uniformly selected subset **Impact:** Reduces N but manageable

### Interpretation

**Problem:** k ≠ 3 ambiguous **Solution:** Calculate confidence intervals **Impact:** Need careful statistics

---

## 💡 ALTERNATIVE IF SHEN FAILS

### Backup: Individual Studies

If Shen catalog inaccessible:

1. Farrah (2023) paper has data tables
2. Extract M_BH vs z by hand
3. Smaller N but sufficient for Week 0
4. Time: +2 hours for extraction

### Backup: Literature Compilation

1. Search ADS for "SMBH mass" papers
2. Compile from multiple sources
3. More work but doable
4. Time: +5 hours for compilation

**Verdict:** Shen catalog strongly preferred!

---

## 📊 EXPECTED WEEK 0 OUTCOME

### If Analysis Works:

```
Result: k_fit = 2.8 ± 0.6 (example)

Interpretation:
- Consistent with Farrah (k=3.0±0.5)
- Within 1σ
- CCBH plausible
- → GO for full project!

Next steps:
- Month 1: Derive k from UET
- Month 2: Make predictions
- Month 3: Compare theory vs data
```

### If Analysis Unclear:

```
Result: k_fit = 1.5 ± 0.9 (example)

Interpretation:
- Not consistent with k=3
- BUT large error bars
- Need better analysis
- → Maybe GO with caution

Next steps:
- Improve statistics
- Check systematics
- Compare with DR16
- Reassess after Month 1
```

### If Analysis Fails:

```
Result: Can't fit / Bad data / Technical issues

Interpretation:
- Data quality problem?
- Analysis method problem?
- Or CCBH wrong?
- → Investigate before decision

Next steps:
- Debug analysis
- Try alternative data
- Consult experts
- Re-evaluate Week 2
```

---

## 🎯 FINAL WEEK 0 DATA STRATEGY

**Day 3 (TODAY):**

- Document Shen catalog ✓
- Create download guide ✓
- List alternative sources ✓

**Day 3 (continued if time):**

- Attempt manual download
- Or: Plan Day 4 analysis
- Or: Move to Day 4 setup

**Day 4:**

- Load data (if downloaded)
- Or: Work with toy data
- Setup analysis pipeline
- Test on small sample

**Day 5:**

- Run full analysis
- Calculate k_fit
- Make plots
- Compare with Farrah

**Day 6:**

- Validate results
- Check errors
- Test robustness
- Document findings

**Day 7:**

- Make decision
- Write summary
- Plan Week 1 (if GO)

---

**STATUS: DATA LOCATED! Week 0 FEASIBLE!** ✓

Next action: Download Shen catalog Time required: 15 min (manual) or 2 min (automated if network available) Priority: HIGH (blocks Day 4-7)