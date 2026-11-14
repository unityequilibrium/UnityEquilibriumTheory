# Baseline Comparison

## Baseline target

- Supercon working files, calibrated superconducting datasets, and cited material references.

## Current comparator package

- Comparator or reference scripts should be taken from topic-local Code/04_Competitor/ when present.
- If no dedicated competitor script exists, the baseline is the cited source dataset or reference model listed in DATA_MANIFEST.md.

## Comparison metrics

- relative error on transition-temperature or materials-response benchmarks

## Acceptance boundary

- Current saved artifact: `Result/artifacts/0_4_superconductivity_superfluids_verification.json`.
- Current run status: `PASS`.
- Current raw McMillan model gate: `FAIL`.
- Current average relative error: about `62.4%`.
- Current pass count: `1 / 10` materials within the fixed 20 percent per-material gate.
- The artifact records dataset hash, source-lock manifest hash, source-record hashes, timestamp, environment, thresholds, and failure analysis.

## Claim boundary

- This baseline comparison can support only conservative wording such as matched selected benchmarks or internal comparison workflow.
- It does not support wording such as solved, verified, exact, unified, or production grade.
- The current failure signal should drive the next model-hardening task: source-normalized rows and a separate Allen-Dynes/UET held-out verifier.
