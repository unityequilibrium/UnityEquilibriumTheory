# Method

## Problem target

This topic studies whether a UET-style correction term can numerically track the muon magnetic-moment anomaly when both the experimental and theory sides are anchored to source-locked 2025 references.

## Core components

### Engine components
- `Code/01_Engine/Engine_Muon_G2.py`

### Proof-oriented components
- `Code/02_Proof/Proof_Muon_Anomaly.py`

### Research and comparison components
- `Code/03_Research/Research_Muon_Anomaly.py`
- `Code/03_Research/Research_Muon_Anomaly_2025.py`

## Variable framing

- Primary modeled quantities: measured `a_mu`, total Standard-Model `a_mu`, derived `delta_a_mu`, and UET anomaly correction.

## Assumptions

- The primary benchmark package should now come from the source-locked 2025 experimental result and the source-locked Muon g-2 Theory Initiative 2025 total Standard-Model comparator.

## Domain of validity

- Direct anomaly-gap comparison against the current 2025 benchmark package.

## Excluded cases

- A definitive resolution of the full theory disagreement behind hadronic contributions or an exclusion of all competing explanations.

## Parameter sensitivity note

- The 2025 verifier should use the current `Engine_Muon_G2.py` output directly rather than a topic-local hardcoded anomaly constant.
- The old hardcoded reference value `2.51e-9` is still useful as a legacy comparison point, but it should not be treated as the canonical theory output once the engine is available.
- Because the official 2025 theory benchmark has shifted the experiment-theory gap downward, old fixed-reference numbers can fail even when the live engine output remains compatible.

## Formula audit link

- See `FORMULA_AUDIT.md` for the current registry of calculation paths, units, constant
  origins, proof status, and benchmark roles.
