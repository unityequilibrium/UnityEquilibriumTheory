# Topic 0.6: Electroweak Physics - Code

This code layer supports a provenance-aware electroweak benchmark workflow.

## Current posture

- Core benchmark: PDG-linked comparison for `sin2(theta_W)`, `m_W`, `m_H`, and `G_F`
- Expanded benchmark: adds a checked-local neutron-lifetime gate
- Diagnostic layer: running-angle compiled points remain useful for inspection, but are not
  primary benchmark gates

## 5x4 Structure

```text
Code/
  01_Engine/
    Engine_Electroweak.py
  02_Proof/
    Proof_WZ_Ratio.py
  03_Research/
    Research_Electroweak_PDG_Comparison.py
    Research_Electroweak_Expanded_Benchmark.py
    Research_Neutron_Decay.py
    Research_Sin2_Theta_W_Running.py
    Research_Higgs_Mechanism.py
    Research_W_Mass_Anomaly_Exp.py
    Research_Alpha_Decay.py
    Research_Beta_Minus.py
    Research_Beta_Plus.py
  04_Competitor/
    Competitor_Electroweak_Baseline.py
    electroweak_solver.py
```

## Recommended commands

```powershell
python docs/topics/0.6_Electroweak_Physics/Code/03_Research/Research_Electroweak_PDG_Comparison.py
python docs/topics/0.6_Electroweak_Physics/Code/03_Research/Research_Electroweak_Expanded_Benchmark.py
```

## Supporting commands

```powershell
python docs/topics/0.6_Electroweak_Physics/Code/01_Engine/Engine_Electroweak.py
python docs/topics/0.6_Electroweak_Physics/Code/02_Proof/Proof_WZ_Ratio.py
python docs/topics/0.6_Electroweak_Physics/Code/03_Research/Research_Neutron_Decay.py
python docs/topics/0.6_Electroweak_Physics/Code/03_Research/Research_Sin2_Theta_W_Running.py
```

## Interpretation

- `Research_Electroweak_PDG_Comparison.py` is the core PDG-linked verifier
- `Research_Electroweak_Expanded_Benchmark.py` is the current best summary of the topic's
  benchmark package
- `Research_Sin2_Theta_W_Running.py` remains diagnostic-only until its benchmark layer is
  improved
- Older research scripts remain useful for exploration, but they should not override the
  standards package defined at the topic root

## Formula registry

- Topic-level formula audit: `docs/topics/0.6_Electroweak_Physics/FORMULA_AUDIT.md`
- Review this file together with `METHOD.md` before promoting any electroweak derivation
  language
