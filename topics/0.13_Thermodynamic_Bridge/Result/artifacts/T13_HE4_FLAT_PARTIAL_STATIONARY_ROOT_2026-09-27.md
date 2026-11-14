# Topic 13: conditional flat partial-action stationary root

MAJOR_RESULT_CLOSURE: `T13_HE4_FLAT_PARTIAL_STATIONARY_ROOT_CONDITIONAL` is `CLOSED_FOR_LANE` for numerical existence and local **Phi-direction** stability in a flat partial-action approximation. It is not finite-temperature condensate-amplitude stationarity. Full Topic 13 and physical He-II matching remain open.

WHAT_IS_ACTUALLY_CLOSED: The prior conditional root at `Phi=0.15` was not stationary, but the same declared flat partial potential admits a Phi-stationary point at fixed `mu` on the tree-condensed (`q>0`) background. When the old density-derived target is imposed simultaneously, a joint Phi-stationary tree-condensed point exists; the derivative-step and quadrature refinements agree. Thus this partial model is not numerically dead-ended merely because the old anchor fails Phi stationarity.

WHAT_REMAINS_OPEN: The density target is recycled from the physical density used to build `e0`, so matching it is circular rather than validation. The quasiparticle EOS keeps a tree-level condensate amplitude; this audit does not solve its finite-temperature stationarity or Ward/Goldstone consistency. The existing [Gaussian stationarity no-go](../../../../core/07_artifacts/topic13/t13_uet_o2_gaussian_thermal_stationarity_no_go.json), [Ward boundary](../../../../core/07_artifacts/topic13/t13_uet_o2_condensed_goldstone_ward_audit.json), and [formal Ward-constrained lane](../../../../core/07_artifacts/topic13/t13_uet_o2_ward_constrained_condensed_audit.json) retain their separate scopes. Renormalization, curved/source terms, physical material map, independent observable, uncertainty, and two-fluid dynamics remain open.

DEPENDENCY_UNLOCKED: A conditional state on which later *internal* response-operator design may be tested. No physical G0, Core, TTG, second-sound or external-validation dependency is unlocked.

STATUS: `PASS_CONDITIONAL_FLAT_PARTIAL_STATIONARY_ROOT`; `full_core_unlock=false`.

WHAT_CHANGED: Added an executable nested bracketing audit, three tests, machine-readable JSON and this note. No Core equation, threshold, physical source row or holdout policy changed.

EQUATION_OR_MAPPING: In the flat homogeneous partial approximation, solve `epsilon_nc U'(Phi)-partial_Phi p_qp(T,mu,Phi)=0` and the **conditional** constraint `partial_mu p_qp=1/T_nat`. Then check `K_eff=epsilon_nc U''-partial_Phi^2 p_qp>0` and `chi_relaxed=partial_mu^2 p_qp+(partial_muPhi p_qp)^2/K_eff`. The density equation is not an admitted helium atom-number identity.

VERIFICATION: At fixed old `mu=1.85568857`, Phi stationarity moves `Phi` from `0.15` to about `0.677271` and natural charge from the recycled target `4.545455` to `4.584604`. Joint Phi stationarity plus the same target gives `mu=1.851515585`, `Phi=0.674642478`, tree-condensed branch, `K_eff=0.11747095`, `chi_clamped=9.31174876`, `chi_relaxed=9.35846885` in the natural lane. Three runs using derivative steps `1e-3`, `5e-4` and quadrature orders `128`, `192` meet the recorded numerical checks; the four linked Topic 13 test modules give 11 passes. JSON SHA-256: `007b0b0bf0036248b5fc1487131d4d0e4f23cb42e561d07905f4a94905792a99`.

CONTROLLING_BLOCKER: `finite_T_condensate_amplitude_and_Ward_stationarity_not_verified`. In particular, the fixed-`Phi` thermal quasiparticle EOS is not a complete interacting finite-temperature stationary action and the density constraint supplies no independent test.

NEXT_ACTION: First test whether a Ward-consistent finite-temperature condensate amplitude and Phi background can be stationary together in a declared microscopic/renormalized scheme; do not transplant this Phi-only root into the existing Gaussian or formal Ward lanes. Then admit a material/observable map and freeze all internal controls before a separately sourced response measurement. Do not reuse the density row as evidence of agreement.

CLAIM_BOUNDARY: This is an exploratory synthetic Phi-only stationary point with a tree-condensed background and recycled density constraint. It does not predict He-II density, temperature, compressibility, second sound or TTG; it neither proves finite-temperature condensate-amplitude stationarity nor repairs the known Ward/renormalization blockers. Xie 2026 was not accessed; `R_gen` remains outside the state.

Evidence: [machine-readable audit](t13_he4_flat_partial_stationary_root.json), [solver](../../Code/03_Research/Research_T13_He4_Flat_Partial_Stationary_Root.py), [tests](../../Code/03_Research/test_t13_he4_flat_partial_stationary_root.py), and the preceding [nonstationary-anchor result](T13_HE4_RELAXED_PHI_RESPONSE_BOUNDARY_2026-09-27.md).
