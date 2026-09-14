# Regression and compatibility tests

Owner: `EVIDENCE`

This area contains public-API, legacy-boundary, topic-contract, and
compatibility regressions. The old `docs/core/test/` tree remains only for
quarantined or not-yet-migrated tests; moved Python tests must not be wrapped at
the old path because that would create duplicate pytest collection.
