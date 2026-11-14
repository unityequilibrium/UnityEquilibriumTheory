# Limitations

## Current benchmark status

- This topic now uses a source-locked 2025 experimental result and a source-locked 2025 Standard-Model comparator.
- Under that stricter benchmark package, the current engine-linked verifier passes, but only after replacing the stale hardcoded comparator in the research script with the actual `Engine_Muon_G2.py` output.

## Scientific boundary

- The present workflow tests numerical compatibility with the current experiment-minus-theory gap.
- It does not prove that the UET anomaly mechanism is the unique explanation of the muon magnetic-moment discrepancy.

## Known gaps

- The previous passing result depended on a legacy local comparator package rather than the 2025 theory benchmark.
- A stale hardcoded anomaly constant can still create an artificial failure against the 2025 package, so workflow discipline matters here: the benchmark must read the live engine, not a disconnected topic-local reference number.
- The current UET anomaly term remains a compact closed-form engine output and is not yet re-derived from a fuller hadronic or electroweak coupling package.
- The current sensitivity layer now separates `legacy_2023`, published/derived `2025`, and `null-gap` baselines, and the baseline package adds historical local theory packages, but it still does not cover the full space of external alternate theory packages or downstream consistency with related particle topics.

## Interpretation rule

- Any future failure against the stricter 2025 source-locked package should be treated as a real theory-data mismatch, not hidden by documentation changes.
- Any future recovery must come from a stronger derivation or a scientifically justified benchmark revision, not from swapping back to a weaker comparator or reintroducing stale hardcoded anomaly numbers.
