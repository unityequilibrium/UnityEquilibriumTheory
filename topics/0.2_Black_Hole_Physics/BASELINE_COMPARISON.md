# Baseline Comparison

## Baseline target

- Topic-local black-hole catalog files and cited observational comparison targets.

## Current comparator package

- Comparator or reference scripts should be taken from topic-local Code/04_Competitor/ when present.
- If no dedicated competitor script exists, the baseline is the cited source dataset or reference model listed in DATA_MANIFEST.md.

## Comparison metrics

- relative error on mass-radius style observables and residual mismatch against selected references

## Acceptance boundary

- This file does not certify a final pass/fail result.
- Until the benchmark is rerun with a saved artifact, comparison language must remain internal benchmark comparison.
- A future hardening pass must record the exact numeric threshold, generated artifact, timestamp, environment, and dataset hash.

## Claim boundary

- This baseline comparison can support only conservative wording such as matched selected benchmarks or internal comparison workflow.
- It does not support wording such as solved, verified, exact, unified, or production grade.
