# Verification Contract

Every topic-level verification workflow should be able to answer the following questions
without relying on institutional memory.

## Minimum inputs

- Which dataset or reference values were used?
- Which local path or citation identifies that input?
- Which config values were fixed before running?
- Which parameters, if any, were calibrated?

## Minimum outputs

- Saved artifact file in JSON form
- Dataset hash or reference identifier
- Explicit metrics
- Explicit thresholds
- Timestamp
- Environment summary
- Repository or package version

## Required distinctions

- `Theoretical derivation`
- `Calibration or fitting`
- `Retrospective fit`
- `Out-of-sample prediction`
- `Qualitative interpretation`

These categories may co-exist in one topic, but they must not be conflated.

## Artifact schema

The standard artifact generated via `docs.scripts.core.audit.reproducibility.generate_artifact()` must
contain:

- `timestamp_utc`
- `topic`
- `uet_version`
- `seed`
- `dataset_hash`
- `results`
- `config`
- `metrics`
- `thresholds`
- `notes`
- `environment`
