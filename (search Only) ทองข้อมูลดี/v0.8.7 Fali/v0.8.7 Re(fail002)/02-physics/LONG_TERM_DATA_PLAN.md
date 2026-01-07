# Long-Term Real Data Acquisition Plan

**Version:** 1.0  
**Date:** 2025-12-29

---

## 🎯 Objective

Replace synthetic CSV data with **real-world experimental data** from authoritative scientific databases to strengthen UET validation claims.

---

## 📅 Timeline (12 Weeks)

```
Week 1-2:   Gravity (NASA JPL Horizons)
Week 3-4:   Thermodynamics (NOAA GSOD)
Week 5-6:   Electromagnetism (NIST Constants)
Week 7-8:   Strong Force (HEPData)
Week 9-10:  Weak Force (NNDC Nuclear Data)
Week 11-12: Integration & Paper Drafts
```

---

## 🌍 Phase 1: Gravity (NASA JPL Horizons)

### Data Source
- **API:** https://ssd.jpl.nasa.gov/horizons/
- **Format:** CSV via web interface or REST API
- **Objects:** Earth-Moon, Mars-Phobos, Jupiter-Europa

### Download Script
```powershell
# Example: Earth-Moon barycenter
$url = "https://ssd.jpl.nasa.gov/api/horizons.api?format=text&COMMAND='301'&OBJ_DATA='YES'&MAKE_EPHEM='YES'&EPHEM_TYPE='VECTORS'&CENTER='500@399'&START_TIME='2020-01-01'&STOP_TIME='2024-12-31'&STEP_SIZE='1 d'"
Invoke-WebRequest -Uri $url -OutFile "nasa_moon_vectors.txt"
```

### Expected Data
| Column | Description |
|--------|-------------|
| `JD` | Julian Date |
| `X, Y, Z` | Position (km) |
| `VX, VY, VZ` | Velocity (km/s) |

### Validation Criteria
- Energy conservation: `|E_final - E_initial| / E_initial < 1%`
- Orbital period match: Within 0.1% of known value

---

## 🌡️ Phase 2: Thermodynamics (NOAA GSOD)

### Data Source
- **Portal:** https://www.ncei.noaa.gov/access/search/data-search/global-summary-of-the-day
- **Stations:** Bangkok (48455), Singapore (48698), Tokyo (47662)
- **Years:** 2020-2024

### Download Steps
1. Go to NOAA portal
2. Select station and date range
3. Export as CSV

### Expected Data
| Column | Description |
|--------|-------------|
| `DATE` | YYYY-MM-DD |
| `TEMP` | Temperature (°F) |
| `STP` | Station pressure (mbar) |
| `DEWP` | Dew point (°F) |

### Validation Criteria
- UET energy correlates with thermodynamic proxy: `corr(Ω, T·P) > 0.7`

---

## ⚡ Phase 3: Electromagnetism (NIST)

### Data Source
- **Portal:** https://physics.nist.gov/cuu/Constants/
- **Specific:** https://physics.nist.gov/cgi-bin/cuu/Value?e

### Key Constants
| Constant | Symbol | Value |
|----------|--------|-------|
| Elementary charge | e | 1.602176634×10⁻¹⁹ C |
| Vacuum permittivity | ε₀ | 8.8541878128×10⁻¹² F/m |
| Coulomb constant | k | 8.9875517923×10⁹ N·m²/C² |

### Lab Data Options
- Millikan oil drop experiment (historical)
- Coulomb torsion balance measurements

### Validation Criteria
- Force-distance relationship: `F ∝ 1/r²` within 1%

---

## 🔴 Phase 4: Strong Force (HEPData)

### Data Source
- **Portal:** https://www.hepdata.net/
- **Search:** "lattice QCD static potential"
- **Papers:** arXiv:1107.1540, arXiv:1503.05652

### Expected Data
| Column | Description |
|--------|-------------|
| `r` | Quark separation (fm) |
| `V(r)` | Potential (GeV) |
| `σ_V` | Uncertainty (GeV) |

### Cornell Potential Fit
```
V(r) = -α/r + σr + c
```
Target: α ≈ 0.3, σ ≈ 0.18 GeV²

### Validation Criteria
- UET with κ = 5 reproduces linear rising potential
- Chi-square fit: χ²/dof < 2

---

## 🟢 Phase 5: Weak Force (NNDC)

### Data Source
- **Portal:** https://www.nndc.bnl.gov/nudat3/
- **Query:** Select isotopes, export CSV

### Target Isotopes
| Isotope | Half-life | Decay Mode |
|---------|-----------|------------|
| ³H | 12.32 y | β⁻ |
| ¹⁴C | 5700 y | β⁻ |
| ⁶⁰Co | 5.27 y | β⁻, γ |
| ¹³⁷Cs | 30.17 y | β⁻ |

### Validation Criteria
- Log-linear relationship: `log(t½) ∝ 1/s` (asymmetry parameter)
- Correlation with Fermi coupling: `s ↔ Gᶠ`

---

## 🔧 Implementation Checklist

### Week 1-2 (Gravity)
- [ ] Register NASA API key
- [ ] Download Earth-Moon data (5 years)
- [ ] Parse and clean CSV
- [ ] Update `orbital_data.csv`
- [ ] Rerun Phase 5 tests
- [ ] Update `paper_gravity.md`

### Week 3-4 (Thermodynamics)
- [ ] Download NOAA GSOD for 3 stations
- [ ] Merge and normalize data
- [ ] Update `climate_data.csv`
- [ ] Rerun Phase 5 tests
- [ ] Update `paper_thermodynamics_mapping.md`

### Week 5-6 (EM)
- [ ] Compile NIST constants
- [ ] Find historical Coulomb data
- [ ] Update `coulomb_data.csv`
- [ ] Rerun Phase 5 tests
- [ ] Update `paper_em.md`

### Week 7-8 (Strong)
- [ ] Search HEPData for lattice QCD
- [ ] Download potential data
- [ ] Update `qcd_potential.csv`
- [ ] Rerun Phase 5 tests
- [ ] Update `paper_strong_force.md`

### Week 9-10 (Weak)
- [ ] Query NNDC for isotope data
- [ ] Export with uncertainties
- [ ] Update `beta_decay.csv`
- [ ] Rerun Phase 5 tests
- [ ] Update `paper_weak_force.md`

### Week 11-12 (Integration)
- [ ] Run full 17-test suite
- [ ] Generate final report
- [ ] Draft arXiv paper outline
- [ ] Prepare submission materials

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Real data coverage | 100% (all 5 forces) |
| Test pass rate | 100% (17/17) |
| Data freshness | < 1 year old |
| Correlation strength | > 0.8 for each domain |
| Documentation | Complete papers for each force |

---

## 🚨 Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| API rate limits | Cache data locally |
| Data format changes | Version control scripts |
| Missing uncertainties | Use conservative estimates |
| Large file sizes | Compress and sample |

---

## 📝 References

1. NASA JPL Horizons: https://ssd.jpl.nasa.gov/horizons/
2. NOAA GSOD: https://www.ncei.noaa.gov/products/land-based-station/global-summary-of-the-day
3. NIST Constants: https://physics.nist.gov/cuu/Constants/
4. HEPData: https://www.hepdata.net/
5. NNDC NuDat3: https://www.nndc.bnl.gov/nudat3/

---

*Plan created: 2025-12-29 | Target completion: 12 weeks*
