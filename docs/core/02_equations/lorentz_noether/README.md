# Lorentz and Noether equation family

This directory is the canonical organization area for the legacy Lorentz
diagnostics and the Noether/phase-field mapping support.

The current migration starts with `uet_lorentz.py`.  Its Lorentz matrices and
diagnostics are compatibility utilities, not a proof that every UET operator
is Lorentz invariant.  The Noether sources are migrated separately after
their shared legacy dependencies and mapping tests are checked.

The root imports under `docs.core.02_equations.lorentz_noether.uet_lorentz` remain compatibility shims.
Organization status is independent of physics evidence status; the current
family contract still limits claims to support utilities and mapping layers.

## Included sources

- `uet_lorentz.py` — legacy Lorentz transform and metric diagnostics.
- `uet_noether.py` — legacy spatial Noether/conservation diagnostics.
- `uet_noether_phase_field_map.py` — declared hydrodynamic coordinate map from
  coarse-grained O(2) Noether charge/current to normalized `C`/`J` coordinates.

These sources retain their existing evidence boundaries.  The package layout
is an organization change; it does not turn the diagnostics into a covariance
or conservation proof and does not make `C` a universal physical quantity.