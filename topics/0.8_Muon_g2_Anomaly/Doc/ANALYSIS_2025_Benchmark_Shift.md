# 2025 Benchmark Shift Analysis

## Purpose

This note explains what actually changed in topic `0.8_Muon_g2_Anomaly` once the topic was checked against the stricter 2025 source-locked benchmark package.

## Core finding

There were two different effects mixed together before:

1. the experiment-minus-theory gap became much smaller in the 2025 package
2. the 2025 verifier was still comparing that tighter gap to a stale hardcoded UET reference number instead of the live engine output

## Benchmark comparison

| Quantity | Value | Meaning |
| :-- | --: | :-- |
| Legacy 2023 package gap | `2.49 x 10^-9` | Older local discrepancy package used by earlier scripts |
| Strict 2025 source-locked gap | `0.375 x 10^-9` | Derived from 2025 experimental result minus 2025 theory benchmark |
| Legacy hardcoded UET reference | `2.51 x 10^-9` | Topic-local historical comparison value |
| Current engine-linked UET output | `0.105 x 10^-9` | Live output from `Engine_Muon_G2.py` |

## Interpretation

- Under the stricter 2025 package, the old hardcoded value overshoots the derived gap and produces the earlier `3.35 sigma` miss.
- Once the verifier is re-linked to the live engine, the current UET output is much smaller and lands within about `0.42 sigma` of the 2025 benchmark.
- The important lesson is that benchmark tightening and workflow drift happened at the same time, so the earlier fail was not a clean statement about the engine alone.

## Scientific consequence

- The current 2025 source-locked verifier now passes when it reads the actual engine.
- That pass is more credible than the old hardcoded workflow, because the benchmark is finally attached to the current theory code path.
- The topic still needs deeper derivation work: a passing compact engine term is not yet the same thing as a full anomaly explanation across alternate theory baselines.

## Reproduction

Run:

```powershell
.venv\Scripts\python.exe docs\topics\0.8_Muon_g2_Anomaly\Code\03_Research\Research_Muon_Anomaly_2025.py
```

Artifacts:

- `Result/artifacts/muon_g2_2025_validation.json`
- `Result/artifacts/muon_g2_benchmark_shift.json`
