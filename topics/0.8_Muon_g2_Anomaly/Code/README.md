# Topic 0.8: Muon g-2 Anomaly - Code

This code layer supports a source-locked muon g-2 benchmark workflow.

## Current posture

- Canonical benchmark: source-locked 2025 experiment-theory gap
- Canonical verifier: live output from `Engine_Muon_G2.py`
- Sensitivity layer: compares the canonical 2025 package against historical local baseline
  packages

## 5x4 Structure

```text
Code/
  01_Engine/
    Engine_Muon_G2.py
  02_Proof/
    Proof_Muon_Anomaly.py
  03_Research/
    Research_Muon_Anomaly_2025.py
    Research_Muon_Sensitivity_2025.py
    Research_Muon_Benchmark_Shift.py
    Research_Muon_Anomaly.py
  04_Competitor/
    run_muon_experiment.py
```

## Recommended commands

```powershell
python docs/topics/0.8_Muon_g2_Anomaly/Code/03_Research/Research_Muon_Anomaly_2025.py
python docs/topics/0.8_Muon_g2_Anomaly/Code/03_Research/Research_Muon_Sensitivity_2025.py
```

## Supporting commands

```powershell
python docs/topics/0.8_Muon_g2_Anomaly/Code/01_Engine/Engine_Muon_G2.py
python docs/topics/0.8_Muon_g2_Anomaly/Code/03_Research/Research_Muon_Benchmark_Shift.py
```

## Interpretation

- `Research_Muon_Anomaly_2025.py` is the canonical benchmark verifier
- `Research_Muon_Sensitivity_2025.py` is the current best summary of benchmark stability
- `Research_Muon_Anomaly.py` and older local scripts are historical/internal layers and
  should not override the source-locked standards package
- Historical local theory packages are useful for comparison, not for replacing the
  canonical 2025 benchmark path

## Formula registry

- Topic-level formula audit: `docs/topics/0.8_Muon_g2_Anomaly/FORMULA_AUDIT.md`
- Review this file before upgrading anomaly-mechanism wording or comparator claims
