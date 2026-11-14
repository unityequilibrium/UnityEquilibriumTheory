# Persistence and resource-selection lane

This package is the canonical home for the normalized persistence-energy
diagnostic and the resource-selection thermal/physical bridge contracts.

The lane formalizes a declared ledger and interaction-cost comparator.  It does
not establish an intent, a universal optimization law, or a physical joule
scale from `C`.  The persistence principle remains a candidate selection
hypothesis, while SI mapping requires an independent source, uncertainty, and
measurement operator.

## Members

- `persistence_energy_diagnostic.py` — normalized path-cost and available-energy
  ledger diagnostic.
- `resource_selection_physical_cost_map.py` — fail-closed dimensional cost-map
  contract with explicit provenance requirements.
- `resource_selection_thermal_bridge.py` — normalized dissipated-work and bath
  entropy proxy bridge for resource-selection trajectories.

The former root modules remain compatibility shims while consumers migrate to
this package.  Organization migration does not promote the persistence
principle to a physical law, identify `C` with energy, or close a thermal/data
lane.
