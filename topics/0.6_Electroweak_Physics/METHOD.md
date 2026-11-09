# Method

## Problem target

This topic studies whether UET-inspired electroweak relationships can reproduce selected decay, ratio, and coupling benchmarks.

## Core components

### Engine components
- `Code/01_Engine/Engine_Electroweak.py`

### Proof-oriented components
- `Code/02_Proof/Proof_WZ_Ratio.py`

### Research and comparison components
- `Code/03_Research/Research_Alpha_Decay.py`
- `Code/03_Research/Research_Beta_Minus.py`
- `Code/03_Research/Research_Beta_Plus.py`
- `Code/03_Research/Research_Electroweak_PDG_Comparison.py`

## Variable framing

- Primary modeled quantities: W/Z-related ratios, electroweak couplings, decay observables, and correction terms.

## Assumptions

- The topic uses effective comparison scripts against selected electroweak tables rather than a full gauge-theory derivation.
- The primary real-data verification now compares engine outputs against source-locked PDG 2025 summary-table values from the local PDG SQLite database.
- The current effective weak-mixing-angle reference is still taken from the topic electroweak snapshot, with an explicit note in the verification artifact, until a direct PDG table mapping is added for that observable.
- The topic now has a source-lock manifest that both primary verifier artifacts hash, so provenance changes become visible in reruns.

## Domain of validity

- Selected electroweak observables and decay-style benchmark datasets.

## Excluded cases

- A complete replacement of the Standard Model electroweak sector or a full derivation of all gauge couplings.

## Parameter sensitivity note

- Some coefficients and normalization choices remain calibration-sensitive.
- In particular, `V_EW`, `ALPHA_EM_MZ`, and the geometric correction path inside `Engine_Electroweak.py` materially control `G_F`, `sin2(theta_W)`, `m_W`, and Higgs-scale outputs.
- The runtime engine now keeps the Higgs branch on the same electroweak-running path as the successful mixing-angle branch by using `sin2_theta_W_running` rather than the raw symmetry-limit seed `0.25`.
- This improves internal consistency and closes the current PDG Higgs mismatch without changing the runtime `kappa`, but it still does not amount to a full gauge-theory derivation.

## Formula audit link

- See `FORMULA_AUDIT.md` for the current registry of relations, units, constant origins,
  proof status, and hardening targets.
