# Matter-to-Interaction Forward Mapping Update Log

## 2026-07-26 — Forward source correspondence wave

- Added a normalized forward comparator that accepts an independent matter source
  and returns density, relational `C`, standard pair potential, force, and
  acceleration as separate layers.
- The source-to-density amplitude and source-to-interaction amplitude remain
  distinct from the geometry-only `C` coordinate.
- Added a constructive mass-rescaling verifier: common source rescaling leaves
  `C` unchanged, doubles the density integral, quadruples pair-potential/force
  amplitude, and doubles body-A acceleration.
- Kept the extra UET response explicitly blocked because no constitutive law has
  been derived or declared in this wave.
- Controlling blocker: define and audit a non-Newtonian constitutive response and
  its dimensional observable map before any galaxy or real-data application.
