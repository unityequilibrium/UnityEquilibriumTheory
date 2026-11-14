# Baseline Comparison

## Baseline target

- AME2020, PDG-derived topic files, proton-radius references, and topic-local competitor scripts.

## Current comparator package

- Comparator or reference scripts should be taken from topic-local Code/04_Competitor/ when present.
- If no dedicated competitor script exists, the baseline is the cited source dataset or reference model listed in DATA_MANIFEST.md.

## Comparison metrics

- strict-subset binding-energy residuals
- table-wide AME2020 diagnostic residuals
- selected radius residuals
- mismatch against competitor baselines

## Acceptance boundary

- This file does not certify a final pass/fail result.
- Until the benchmark is rerun with a saved artifact, comparison language must remain internal benchmark comparison.
- The strict selected-subset artifact and the table-wide diagnostic artifact should be described separately.
- A future hardening pass must record the exact numeric threshold, generated artifact, timestamp, environment, and dataset hash.

## Claim boundary

- This baseline comparison can support only conservative wording such as matched selected benchmarks or internal comparison workflow.
- It does not support wording such as solved, verified, exact, unified, or production grade.
