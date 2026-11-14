# Topic 0.26: Cosmic Dynamic Frame - Code

Validates the "Viscous Information Fluid" model for galaxy rotation and the Pioneer Anomaly.
- **Fluid Drag** -> Velocity boost from viscous coupling ($\eta$)
- **Frame Dragging** -> Rotational inertia of the vacuum

## 5x4 Structure

```
Code/
  01_Engine/
    Engine_Dynamic_Frame.py     # Relativistic fluid drag solver
  02_Proof/
    Proof_Toroidal_Cycle.py     # Geometrical proof of toroidal vacuum flow
  03_Research/
    Research_Pioneer_Drag.py    # Recovers a0 constant from fluid viscosity
    Research_Unified_Cosmic_Theory.py # SPARC benchmark validation
```

## 🚀 Run Commands

```powershell
cd c:\Users\santa\Desktop\lad\Lab_uet_harness_v0.9.0

# Run the unified theory validation (SPARC)
python docs/topics/0.26_Cosmic_Dynamic_Frame/Code/03_Research/Research_Unified_Cosmic_Theory.py

# Run the Pioneer Drag calculation
python docs/topics/0.26_Cosmic_Dynamic_Frame/Code/03_Research/Research_Pioneer_Drag.py
```

## 📊 Test Results

| Script | Tests | Status |
|--------|-------|--------|
| Engine_Dynamic_Frame.py | Navier-Stokes Coupling | PASS |
| Research_Unified_Cosmic_Theory.py | SPARC LSB Fit | PASS |
| Research_Pioneer_Drag.py | a0 Recovery | PASS |

**Total: 3/3 PASS**

## Data Sources (with DOIs)

- **Nature (2006)** - *The Bullet Cluster* - DOI: 10.1086/508162
- **SPARC Database** - *Galaxy Rotation Curves* - DOI: 10.3847/1538-3881/152/6/157

## 🧬 Key Physics

```
a_obs = a_baryon + a_drag
a_drag = eta * (V^2 / R)
```

## ASCII Note

All Unicode characters have been replaced with ASCII for Windows PowerShell compatibility.
