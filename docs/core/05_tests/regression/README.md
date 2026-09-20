# Regression and compatibility tests

Owner: `EVIDENCE`

This area contains public-API, legacy-boundary, topic-contract, and
compatibility regressions. The old `docs/core/test/` tree is now a non-Python
legacy boundary; moved Python tests must not be wrapped at the old path because
that would create duplicate pytest collection.
