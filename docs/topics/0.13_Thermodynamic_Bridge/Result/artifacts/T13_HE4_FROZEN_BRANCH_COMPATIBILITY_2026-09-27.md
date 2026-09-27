# Topic 13: frozen He-4/O(2) branch compatibility

MAJOR_RESULT_CLOSURE: `T13_HE4_FROZEN_STATE_BRANCH_COMPATIBILITY_BOUNDARY` is `CLOSED_FOR_LANE` for the **frozen reference state**. The planned predictive-content result and Full Topic 13 are not closed.

WHAT_IS_ACTUALLY_CLOSED: The natural action state used by the local `Phi` thermal bridge is `T_nat=0.22`, `mu=0.35`, `Phi=0.15` on the **normal** O(2) branch. Re-evaluating the declared action-coupled configuration gives `m_eff^2=0.994` and `q=Z mu^2-m_eff^2=-0.8715` with `Z=1`. The He-4 calibration anchor is 1.7 K at SVP in the **He II** phase, with source-derived superfluid fraction `0.771413...`. Consequently the frozen natural state cannot itself be the condensed background for a He-II two-fluid/second-sound linearization. This is a branch-admissibility result, not a failure of the local effective-response fit.

WHAT_REMAINS_OPEN: An independently selected *condensed* natural action background that can be mapped to the physical He-II thermodynamic state, a rederived local response/uncertainty map at that background, and a longitudinal two-fluid evolution/observable operator. The existing static two-sector thermodynamics and a natural-unit relative-flow collision kernel are partial inputs, not that complete operator. Do not use the older static no-go wording to imply that no collision lane exists now.

DEPENDENCY_UNLOCKED: None; no second-sound prediction or Full Topic 13 promotion.

STATUS: `PASS_SCOPED_FROZEN_STATE_BRANCH_MISMATCH` for the declared tree/quasiparticle branch only.

WHAT_CHANGED: Added an executable Topic 13 branch-admission audit, three focused tests, a source-hashed JSON artifact and this handoff note. Frozen calibration constants, source roles and Core equations were not changed.

EQUATION_OR_MAPPING: `q=Z mu^2-[m^2-epsilon_nc h (Phi-Phi_*)]`. At fixed `Phi=0.15`, the tree boundary is `mu_c=sqrt(m_eff^2/Z)=0.996995...`, about `0.646995` above the frozen `mu`. At fixed `mu=0.35`, the algebraic boundary is `Phi_c=21.9375`, about `21.7875` above the frozen `Phi`. The tree amplitude is zero for `q<=0` and satisfies `A^2=q/lambda` for `q>0`, so the derivative of `A^2` changes across the branch surface; a normal-branch local derivative cannot simply be carried over. These values only locate the **tree-branch surface of the declared natural-unit model**; they are not candidate He-4 fit values, not within a validated local linear-response interval, and not a finite-temperature physical phase boundary. `DeltaPhi_norm=Z_Phi DeltaPhi_nat` is a local response-coordinate map, not an identification of the entire action phase with He-II.

VERIFICATION: Three branch tests pass: frozen branch recomputation, exact tree-boundary substitution and a `Phi +/-0.001` local probe that stays normal. Together with the prior pole-design and He-4 matching tests, the focused suite is 9/9. The JSON records SHA-256 of the current composition, calibration, physical source package, natural bridge and partial-lane source files. Artifact SHA-256: `6ca734bd4aaceea177ef96609dc1c3063d5bc5dfdeb697d14f9dc506a794cad9`. No target-curve fit or Xie 2026 access was performed in this wave.

CONTROLLING_BLOCKER: `state_matched_condensed_action_background_and_independent_transfer_map`. Even after that, `admitted_condensed_two_fluid_longitudinal_response_operator` and physical inertia/transport provenance remain separate gates.

NEXT_ACTION: Keep the frozen normal-branch local bridge as a bounded effective-response result. Before using He-II second sound, preregister an action parameter/state-selection rule independent of the target sound curve; verify `q>0`, thermodynamic stability, finite-temperature background and source-matched SI map; rederive `alpha` and uncertainty at that point rather than carrying the normal-branch derivative over; then build the coupled longitudinal mode and compare source/detector protocols. If no independent state-selection rule is available, report scoped non-identifiability rather than tune `mu` or `Phi` to the measured sound speed.

CLAIM_BOUNDARY: This audit does not invalidate the prior local calibration or the separately bounded Core composition result. It rules out only the proposed *direct* second-sound inference from its frozen normal natural state. It does not prove that UET cannot admit a future condensed He-II extension or that its tree boundary is the observed lambda transition.

Evidence: [machine-readable audit](t13_he4_frozen_branch_compatibility.json), [audit source](../../Code/03_Research/Research_T13_He4_Frozen_Branch_Compatibility.py), [tests](../../Code/03_Research/test_t13_he4_frozen_branch_compatibility.py), and the frozen [Core composition](../../../../core/07_artifacts/topic13/t13_he4_core_thermodynamic_bridge_composition_audit.json).
