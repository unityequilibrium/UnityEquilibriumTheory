# Topic 13 support lane

This package is the canonical home for Topic 13 thermal-bridge support
contracts, formal integration witnesses, and dimensional scale diagnostics.

The modules here are internal support surfaces.  They do not by themselves
provide a physical SI calibration, a microscopic Kubo match, a TTG prediction,
or full Topic 13 closure.  Their evidence status and controlling blockers
remain governed by the Topic 13 artifacts and the foundation gates.

## Members

- `t13_formal_thermodynamic_bridge_integration.py` — cross-module formal
  thermodynamic bridge witness.
- `t13_thermal_bridge_scale_dependency.py` — structural scale-dependency and
  identifiability no-go witness.
- `topic13_closure_record_contract.py` — fail-closed schemas for the three
  required Topic 13 input packages.

The former root paths remain compatibility shims while consumers migrate to
this package.  Organization migration does not promote a physics claim or
change the normalized/natural-unit boundary.
