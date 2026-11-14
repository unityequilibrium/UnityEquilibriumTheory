# Limitations

- The PDG-linked verifier now passes the current four-observable package: `sin2(theta_W)`, `m_W`, `m_H`, and `G_F`.
- The expanded benchmark also passes the current neutron-lifetime gate, but that neutron layer is still a checked local benchmark rather than a newly source-locked external package.
- The Higgs branch is now internally more consistent because it follows the electroweak-running angle branch, but that is still a model-design choice that should be defended with a fuller derivation if this topic is pushed toward manuscript-level claims.
- The effective weak-mixing-angle and Fermi-constant layer now sit inside a structured electroweak reference package, but the weak-mixing-angle observable is still not mapped directly from the current PDG SQLite workflow.
- The running-angle layer is useful as a diagnostic, but with the current compiled-point workflow it still sits around a few-percent average error and should not be promoted to a primary benchmark gate.
- The source-lock manifest improves reproducibility, but checked-local layers still need direct upstream mappings before manuscript-grade promotion.
- Internal script execution does not by itself establish external replication, theorem-level proof, or broad physical closure.
