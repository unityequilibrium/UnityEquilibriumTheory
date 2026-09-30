# Topic 13: conditional compressibility measurement independence

MAJOR_RESULT_CLOSURE: `T13_HE4_CONDITIONAL_COMPRESSIBILITY_INDEPENDENCE_DESIGN` is `CLOSED_FOR_LANE` for a conditional measurement-design result. No physical He-II map or Full Topic 13 closure follows.

WHAT_IS_ACTUALLY_CLOSED: Under the three unadmitted full-pressure, chemical-potential and atom-number identifications in the preceding circularity audit, a **clamped-`Phi`** isothermal response is algebraically distinct from the density used to define `e0`. The calculation specifies exactly when it would be a test versus another parameter-selection row. It does not obtain a physical response datum.

WHAT_REMAINS_OPEN: The Noether-charge-to-atom and material-pressure maps, independently fixed chemical-potential energy scale, a physical `Phi` clamp or relaxed-`Phi` response law, same-state isothermal response source with covariance, and the two-fluid dynamical operator. Ordinary sound-speed or adiabatic compressibility data cannot silently replace the clamped isothermal derivative.

DEPENDENCY_UNLOCKED: A preregistration design for a separate response measurement only. No Core or Full Topic 13 physical dependency is unlocked.

STATUS: `PASS_SCOPED_CONDITIONAL_COMPRESSIBILITY_DESIGN`; `full_core_unlock=false`.

WHAT_CHANGED: Added an executable chain-rule/local-rank audit, three focused tests, a hash-backed JSON and this note. No accepted action, physical source row, fitted coefficient or threshold changed.

EQUATION_OR_MAPPING: Conditional `n_SI=e0 n_nat/E_mu` and `chi_SI|Phi=e0 chi_nat|Phi/E_mu^2` imply `kappa_T|Phi=chi_SI|Phi/n_SI^2` and `n_SI E_mu kappa_T|Phi=chi_nat|Phi/n_nat`. If `Phi` relaxes, `chi_nat,total=(partial_mu n_nat)|Phi+(partial_Phi n_nat)(dPhi/dmu)|T`; the second term is not provided by the frozen-`Phi` EOS. The equation is not admitted as a helium identity.

VERIFICATION: At the preceding conditional root `T_nat=0.22`, `mu_nat=1.85568857`, `Phi=0.15`, the natural susceptibility is `9.33719` and the dimensionless ratio is `2.05418`. The implied clamped response `8.81e-7 Pa^-1` is **not** a physical prediction. Synthetic density/e0 rescaling leaves the ratio invariant. The local two-output Jacobian for `(mu,Phi)` has determinant about `-0.099789` at the root under two finite-difference steps; this is a local numerical witness, not global identifiability. Three focused tests pass. Artifact SHA-256: `dee8a9fa124e7316fedeefed312fb31fa84fc82ed4da25ab40b671a7a13b4538`.

CONTROLLING_BLOCKER: `Noether_charge_to_helium_atom_identity_not_admitted`; additionally, a physical `Phi` clamp or relaxation law is needed before comparing ordinary compressibility.

NEXT_ACTION: First justify the charge/pressure/chemical-potential map and choose a physical `Phi` protocol. If `Phi` and `E_mu` are independently fixed, reserve a source-locked clamped isothermal response as a non-reused test. If `Phi` is fitted from that response, reserve a third independent observable and lock roles before reading it. If the physical clamp is impossible, derive the relaxed-response correction before claiming a comparison.

CLAIM_BOUNDARY: This is a conditional analytic/numerical design result, not a He-II fit, second-sound prediction, measured compressibility agreement, or external validation. The Xie 2026 TTG holdout was not read or used for tuning.

Evidence: [machine-readable audit](t13_he4_conditional_compressibility_design.json), [calculation](../../Code/03_Research/Research_T13_He4_Conditional_Compressibility_Design.py), [tests](../../Code/03_Research/test_t13_he4_conditional_compressibility_design.py), and the preceding [density circularity result](T13_HE4_CONDITIONAL_CHARGE_MAP_CIRCULARITY_2026-09-27.md).
