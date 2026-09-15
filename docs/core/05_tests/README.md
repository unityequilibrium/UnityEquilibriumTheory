# Tests

Tests are organized by behavior: equation/formal, numerical, artifact/schema
and regression/compatibility. Tests are not evidence of a physical claim until
their inputs, thresholds and claim boundary are recorded.

Owner: EVIDENCE

## Current migration checkpoint

- 500 legacy test/support records are physically migrated into this area; the
  canonical tree currently contains 525 Python files including pre-existing
  canonical tests.
- The collection audit records 2,169 collected tests with no collection error;
  collection status is separate from physics evidence.
- The `docs/core/test/` boundary contains no Python test implementation.
  Its remaining non-Python assets are handled by a separate provenance-aware
  migration wave.
- Do not add old-path Python wrappers for moved tests. The migration manifest
  and collection audit are the sources of truth for this wave.