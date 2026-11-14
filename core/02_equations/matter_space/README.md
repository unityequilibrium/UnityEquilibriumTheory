# Matter-space equation family

This directory is the canonical source area for the bounded matter-space
equation family:

- `uet_spatial.py` — one-dimensional conservative spatial primitives;
- `uet_matter_space.py` — the normalized `matter_space_coupled_v1` operator;
- `uet_trace.py` — the derived, retarded history-trace lane;
- uet_matter_space_flux_telegraph.py — the named conserved flux-relaxation
  comparator;
- uet_matter_space_flux_phi.py — the named coupled flux/response comparator;
- uet_hyperbolic_phase_field.py — an external first-order hyperbolic Cahn–Hilliard comparator;
- uet_hyperbolic_phase_field_bridge.py — analytic fixed-cone and algebraic current-map diagnostics for that comparator;

- `uet_master_equation.py` — the retained legacy master-engine facade and its
  opt-in operator dispatch.

The root paths under `docs/core/` remain compatibility shims. Moving the
implementation changes organization and import provenance only; it does not
promote the physics evidence status. The current causal and dimensional
limitations remain controlled by the equation-family contracts and foundation
gates.
