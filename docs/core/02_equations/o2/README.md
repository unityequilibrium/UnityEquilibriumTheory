# O(2) equation family

This package is the canonical implementation home for the UET O(2) equation
family.  Root-level modules remain compatibility shims while downstream
consumers migrate to the canonical path.

## Members

- `uet_o2_finite_density_eos.py` — tree-level finite-density O(2) mean-field
  EOS.  Its declared lane is natural units and its current controller remains
  the missing externally matched dissipative/Kubo transport and entropy
  evidence.
- `standard_o2_finite_temperature_comparator.py` — standard finite-temperature
  normal-branch complex-scalar comparator.  It is not a finite-temperature UET
  derivation and does not emit an SI observable map.
- `uet_o2_*.py` — the extended O(2) response, Kubo, Schwinger–Keldysh,
  renormalization, and identifiability surfaces. These implementations are
  canonical here; their individual scientific evidence and claim boundaries
  remain controlled by the equation registry and foundation gate.

The covariant ideal-superfluid transport bridge is owned by the covariant
family at `../covariant/uet_covariant_superfluid_transport.py`; this package
imports no duplicate implementation for that lane.

## Migration boundary

The old root paths, including `docs/core/uet_o2_*.py`, remain thin shims for
legacy imports. New implementation edits belong in this package and can be
imported through `docs.core.02_equations.o2.<module>`. Organization migration
does not change physics status, parameter provenance, or claim boundaries.
