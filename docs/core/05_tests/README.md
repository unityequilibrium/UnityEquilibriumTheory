# Tests

Tests are organized by behavior: equation/formal, numerical, artifact/schema
and regression/compatibility. Tests are not evidence of a physical claim until
their inputs, thresholds and claim boundary are recorded.

Owner: EVIDENCE

## Current migration checkpoint

- 205 test/support files are canonical under this area.
- 295 legacy files remain quarantined until path, package-import, boundary, or
  sandbox review is complete.
- The collection audit records 2,105 collected tests with no duplicate
  collection; collection status is separate from physics evidence.
- Do not add old-path Python wrappers for moved tests. Use the migration
  manifest and repair the remaining source contracts before the next move.