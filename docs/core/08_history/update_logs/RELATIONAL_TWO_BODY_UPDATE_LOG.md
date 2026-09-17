# Relational Two-Body Baseline Update Log

## 2026-07-26 — Initial correspondence wave

- Added the normalized Newtonian two-body comparator after the C ontology was locked as a
  relational interaction coordinate.
- Tested `C_AB -> U_AB -> F_A -> a_A` while keeping `m_A` and `m_B` as separate standard
  counterpart parameters.
- Added a finite-signal observer record showing that the received source state belongs to the
  earlier event time, not automatically to the source state at arrival.
- Generated `docs/core/artifacts/relational_two_body_baseline_verification.json` with audit
  status `PASS`, claim status `SIMULATION_ONLY`, and all nine declared local gates passing.
- The mass-scale diagnostic keeps geometry-only `C` unchanged while the interaction amplitude
  scales with mass. This is evidence against silently defining `C` as mass in this lane.
- Controlling blocker: no dimensional lane or empirical observable has been selected. The next
  decision is either a declared `C -> rho` mass-density map or a different constitutive
  interaction map.
