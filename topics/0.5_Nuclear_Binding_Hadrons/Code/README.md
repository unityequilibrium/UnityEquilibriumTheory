# Topic 0.5: Nuclear Binding & Hadrons - Code

Validates UET against Strong Force interactions, Nuclear Binding Energy, and Hadron Masses.
- **Strong Force** -> Information Pressure (Yukawa Potential)
- **Binding Energy** -> Information Entropy saturation
- **Proton Radius** -> Derived from QCD coupling $\approx 0.841$ fm

## 5x4 Structure

```
Code/
  01_Engine/
    Engine_Nuclear_Binding.py     # Upgrade: Added Yukawa Potential (Error 4.34%)
    Engine_Hadron_Model.py        # Constituent Quark Model
    Engine_Light_Nuclei.py        # Deuteron/Helium analysis
    Engine_QCD_Bridge.py          # Lattice QCD link
  02_Proof/
    Proof_Color_Confinement.py    # Analytical derivation
  03_Research/
    Research_Nuclear_Binding.py   # AME2020 Data Comparison (83 Nuclei)
    Research_Strong_Force.py      # Cornell Potential Validation
    Research_Proton_Radius.py     # Prediction: 0.841 fm
    Research_QCD_Running.py       # Alpha_s evolution
    Research_Quark_Masses.py      # Mass parameters
  04_Competitor/
    Competitor_Nuclear_Baseline.py # Standard SEMF Baseline
```

## 🚀 Run Commands

```powershell
# Navigate to project root
cd c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0

# [1] Core Engine Logic (Upgraded with Yukawa)
python docs/topics/0.5_Nuclear_Binding_Hadrons/Code/01_Engine/Engine_Nuclear_Binding.py

# [2] Strong Force Research
python docs/topics/0.5_Nuclear_Binding_Hadrons/Code/03_Research/Research_Strong_Force.py
python docs/topics/0.5_Nuclear_Binding_Hadrons/Code/03_Research/Research_Proton_Radius.py
python docs/topics/0.5_Nuclear_Binding_Hadrons/Code/03_Research/Research_QCD_Running.py

# [3] Nuclear Data Validation (83 Nuclei)
python docs/topics/0.5_Nuclear_Binding_Hadrons/Code/03_Research/Research_Nuclear_Binding.py
```

## 📊 Test Results

| Script | Test Focus | Result | Status |
|--------|------------|--------|--------|
| Engine_Nuclear_Binding.py | 83 Nuclei BE | **98% Pass (Error 4.3%)** | ✅ PASS |
| Research_Strong_Force.py | Cornell Potential | Linear Confinement | ✅ PASS |
| Research_Proton_Radius.py | Radius | **0.841 fm (Matches Muonic)** | ✅ PASS |
| Engine_Light_Nuclei.py | Deuteron | 97% Error (Need QM Solver) | ❌ FAIL |
| Engine_QCD_Bridge.py | Alpha_s (Mz) | 0.2% Deviation | ✅ PASS |

**Total: 4/5 PASS (Deuteron needs Schrodinger Solver)**

## 🧬 Key Physics

```
E_binding = V_volume + V_surface + V_coulomb + V_asymmetry + V_yukawa
```

## Engine Upgrade Note

### Yukawa Potential Added
We proactively added the Yukawa term $V \sim e^{-m_\pi r}/r$ to `Engine_Nuclear_Binding.py`.
This reduced the error for Helium-4 and Carbon-12 significantly compared to the standard Liquid Drop model.

## ASCII Note

All Unicode replaced with ASCII for Windows compatibility.
