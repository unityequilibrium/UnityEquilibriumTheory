# 🔥 UET PREDICTION TEST - COMPLETE GUIDE

## 🎯 What We're Testing

**UET Prediction:** k ≈ 2.7-2.9 (from thermodynamic derivation)
**Farrah Claim:** k = 3.0 ± 1.19
**Null Hypothesis:** k = 0 (no cosmological coupling)

This script compares all three and tells you which one the data supports!

---

## 📋 Prerequisites

### Python Packages Required:
```bash
numpy
scipy
matplotlib
astropy
```

### Check if you have them:
```python
python -c "import numpy, scipy, matplotlib, astropy; print('✓ All packages installed!')"
```

### If not, install:
```bash
pip install numpy scipy matplotlib astropy --break-system-packages
```

---

## 🚀 How to Run

### Method 1: Full Shen 2011 Catalog (Recommended)

```bash
cd C:\Users\santa\Desktop\lad\uet_harness_v0_1_hangfix_v5_3_dtladderfix\uet_harness_v0_1\research\01-physics\black-hole-uet\01_data

python test_uet_prediction.py shen2011.fits
```

### Method 2: Sample Data (Faster for testing)

```bash
python test_uet_prediction.py shen2011_sample.fits
```

### Method 3: Default (looks for shen2011.fits in current directory)

```bash
python test_uet_prediction.py
```

---

## 📊 What You'll Get

### Output Files:
1. **uet_prediction_test.png** - Comprehensive 4-panel plot:
   - Panel 1: Data + all 3 models (Free fit, UET k=2.8, Farrah k=3.0)
   - Panel 2: Residuals comparison
   - Panel 3: Chi-squared comparison bars

### Terminal Output:
```
STEP 1: Load & clean data → N objects after quality cuts
STEP 2: Apply V/Vmax correction → Bias-corrected bins
STEP 3: Fit free k → k_fit ± error
STEP 4: Test k = 2.8 → chi-squared
STEP 5: Test k = 3.0 → chi-squared
STEP 6: Statistical tests → F-test, AIC
STEP 7: VERDICT → Which model wins!
```

---

## 🔬 What the Script Does

### Step-by-Step:

1. **Load Shen 2011 catalog** (105,783 quasars)
   - Read FITS file
   - Show summary

2. **Apply quality cuts**
   - Valid M_BH measurements
   - Error < 0.5 dex
   - S/N > 3
   - Not BAL quasars
   - Result: ~30,000-50,000 good objects

3. **Apply V/Vmax correction** (CRITICAL!)
   - Fix Malmquist bias
   - Weight by detection probability
   - Bin by redshift (20 bins)
   - Get bias-corrected M_BH per bin

4. **Fit CCBH model with FREE k**
   ```
   M_BH ∝ a^k
   log(M_BH) = log(M_0) + k × log(a)
   
   Linear regression → k_fit ± k_err
   ```

5. **Test UET prediction (k = 2.8 fixed)**
   - Fit only M_0 (k forced to 2.8)
   - Calculate chi-squared
   - Compare with free fit

6. **Test Farrah prediction (k = 3.0 fixed)**
   - Fit only M_0 (k forced to 3.0)
   - Calculate chi-squared
   - Compare with free fit

7. **Statistical comparison**
   - **F-test:** Is fixed k significantly worse than free k?
   - **AIC:** Which model is preferred?
   - **Sigma test:** How many σ from prediction?

8. **Generate verdict**
   - Which k is closer to data?
   - Which model is statistically better?
   - Final interpretation

---

## 📈 Interpreting Results

### Possible Outcomes:

#### Outcome A: k_fit ≈ 2.8 ± 0.3
```
✓ UET PREDICTION CONFIRMED!
✓ k ≈ 2.8 matches UET thermodynamic derivation
✓ Farrah's k = 3 is too high
→ BHs couple to vacuum energy but k ≠ 3
→ This is ORIGINAL CONTRIBUTION!
```

#### Outcome B: k_fit ≈ 3.0 ± 0.5
```
✓ Farrah CONFIRMED!
✗ UET needs refinement
→ w = -1 exactly (pure vacuum)
→ Need to explain why w doesn't evolve
```

#### Outcome C: k_fit ≈ 1.5-2.0
```
⚠ Between UET and observations
✓ Coupling exists (k > 0)
✗ But weaker than UET predicts
→ Maybe β parameter needs adjustment
→ Or multiple coupling mechanisms
```

#### Outcome D: k_fit ≈ 0 or negative
```
✗ Still biased!
→ V/Vmax correction not enough
→ Need M_BH/M_galaxy ratio method
→ Or elliptical galaxy sample
```

---

## 🔧 If Something Goes Wrong

### Error: "No module named 'astropy'"
```bash
pip install astropy --break-system-packages
```

### Error: "File not found: shen2011.fits"
```bash
# Check you're in the right directory
cd C:\Users\santa\Desktop\lad\uet_harness_v0_1_hangfix_v5_3_dtladderfix\uet_harness_v0_1\research\01-physics\black-hole-uet\01_data

# Or use full path
python test_uet_prediction.py C:\path\to\shen2011.fits
```

### Error: "Cannot find column 'LOGBH_HB_VP06'"
```
Catalog format different!
→ Check data_loader.py
→ May need to adjust column names
```

### Warning: "k_fit = -2.03" (like before)
```
V/Vmax correction didn't work well enough
→ Try M_BH/M_galaxy method instead
→ Or use elliptical galaxy sample
```

---

## 🎯 Next Steps After Running

### If UET wins (k_fit ≈ 2.8):
1. ✓ Write paper: "UET Prediction of CCBH Parameter k"
2. ✓ Calculate observable predictions (ISCO shifts)
3. ✓ Compare with future data (XRISM, EHT)

### If Farrah wins (k_fit ≈ 3.0):
1. ⚠ Refine UET derivation
2. ⚠ Understand why w = -1 exactly
3. ⚠ Look for time evolution effects

### If inconclusive:
1. → Try M_BH/M_galaxy ratio method
2. → Download MPA-JHU catalog
3. → Cross-match and re-analyze

---

## 📚 Technical Details

### V/Vmax Correction Method:

For each object at redshift z_i:
```
1. Calculate z_max (max z where detectable)
2. Compute V_max = comoving volume to z_max
3. Weight = 1/V_max
4. Weighted mean removes bias
```

### CCBH Model:
```
M_BH(z) = M_0 × a^k = M_0 × (1+z)^(-k)

Taking log:
log(M_BH) = log(M_0) - k × log(1+z)
         = log(M_0) + k × log(a)

Linear regression in log space!
```

### Statistical Tests:

**F-test:**
```
F = [(SS_res_fixed - SS_res_free) / df_diff] / [SS_res_free / df_free]

If p > 0.05: Fixed k NOT significantly worse → Use simpler model
If p < 0.05: Free k significantly better → Fixed k rejected
```

**AIC:**
```
AIC = 2k + n × ln(SS_res / n)

Where k = number of parameters

ΔAIC < 2: Models equivalent
ΔAIC 2-10: Weak preference
ΔAIC > 10: Strong preference
```

---

## 🎉 Expected Runtime

- Sample data (shen2011_sample.fits): **~10 seconds**
- Full data (shen2011.fits): **~30-60 seconds**

Fast enough to run multiple times with different parameters!

---

## 💡 Pro Tips

1. **Start with sample data first** to verify pipeline works
2. **Check plots before accepting results** - visual inspection matters!
3. **If k_fit is weird (negative, huge), suspect bias** not fully corrected
4. **Compare chi-squared values** - should be ~1 for good fit
5. **Look at residuals** - should be random, not systematic

---

## 🚀 Ready to Run?

```bash
# Navigate to directory
cd C:\Users\santa\Desktop\lad\uet_harness_v0_1_hangfix_v5_3_dtladderfix\uet_harness_v0_1\research\01-physics\black-hole-uet\01_data

# Run the test!
python test_uet_prediction.py shen2011.fits

# Wait ~1 minute...

# Check results!
# → Terminal: Statistical verdict
# → File: uet_prediction_test.png
```

**LET'S FUCKING GO!** 🔥
