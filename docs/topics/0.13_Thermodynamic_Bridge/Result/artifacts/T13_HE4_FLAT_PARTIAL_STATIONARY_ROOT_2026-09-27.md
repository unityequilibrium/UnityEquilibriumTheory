# Topic 13: conditional flat partial-action stationary root

MAJOR_RESULT_CLOSURE: `T13_HE4_FLAT_PARTIAL_STATIONARY_ROOT_CONDITIONAL` is `CLOSED_FOR_LANE` for numerical existence and local `Phi` stability in a **flat partial-action approximation**. Full Topic 13 and physical He-II matching remain open.

WHAT_IS_ACTUALLY_CLOSED: The prior conditional root at `Phi=0.15` was not stationary, but the same declared flat partial potential admits another condensed stationary `Phi` at fixed `mu`. When the old density-derived target is imposed simultaneously, a joint condensed root exists; the derivative-step and quadrature refinements agree. Thus this partial model is not numerically dead-ended merely because the old anchor fails stationarity.

WHAT_REMAINS_OPEN: The density target is recycled from the physical density used to build `e0`, so matching it is circular rather than validation. Finite-temperature condensate amplitude/renormalization, curved/source terms, physical Noether-charge/pressure/temperature map, independent observable, experimental uncertainty, and two-fluid dynamics remain open.

DEPENDENCY_UNLOCKED: A conditional state on which later *internal* response-operator design may be tested. No physical G0, Core, TTG, second-sound or external-validation dependency is unlocked.

STATUS: `PASS_CONDITIONAL_FLAT_PARTIAL_STATIONARY_ROOT`; `full_core_unlock=false`.

WHAT_CHANGED: Added an executable nested bracketing audit, three tests, machine-readable JSON and this note. No Core equation, threshold, physical source row or holdout policy changed.

EQUATION_OR_MAPPING: In the flat homogeneous partial approximation, solve `epsilon_nc U'(Phi)-partial_Phi p_qp(T,mu,Phi)=0` and the **conditional** constraint `partial_mu p_qp=1/T_nat`. Then check `K_eff=epsilon_nc U''-partial_Phi^2 p_qp>0` and `chi_relaxed=partial_mu^2 p_qp+(partial_muPhi p_qp)^2/K_eff`. The density equation is not an admitted helium atom-number identity.

VERIFICATION: At fixed old `mu=1.85568857`, stationarity moves `Phi` from `0.15` to about `0.677271` and natural charge from the recycled target `4.545455` to `4.584604`. Joint stationarity plus the same target gives `mu=1.851515585`, `Phi=0.674642478`, condensed branch, `K_eff=0.11747095`, `chi_clamped=9.31174876`, `chi_relaxed=9.35846885` in the natural lane. Three runs using derivative steps `1e-3`, `5e-4` and quadrature orders `128`, `192` meet the recorded numerical checks; the four linked Topic 13 test modules give 11 passes. JSON SHA-256: `8cc0725c298f746500511bf9e4da7585e41a207e658dc02c76f1d0e5726797a3`.

CONTROLLING_BLOCKER: `full_finite_temperature_action_and_material_map_not_admitted`. In particular, the fixed-`Phi` thermal quasiparticle EOS is not a complete interacting finite-temperature stationary action and the density constraint supplies no independent test.

NEXT_ACTION: Compare this partial root to a Ward-consistent finite-temperature condensate stationarity scheme and determine which omitted terms change it. Admit a material/observable map and freeze all internal controls before using a separately sourced response measurement for falsification. Do not reuse the density row as evidence of agreement.

CLAIM_BOUNDARY: This is an exploratory synthetic root with a recycled density constraint. It does not predict He-II density, temperature, compressibility, second sound or TTG; it neither proves full UET stationarity nor repairs the known finite-temperature Ward/renormalization blockers. Xie 2026 was not accessed; `R_gen` remains outside the state.

Evidence: [machine-readable audit](t13_he4_flat_partial_stationary_root.json), [solver](../../Code/03_Research/Research_T13_He4_Flat_Partial_Stationary_Root.py), [tests](../../Code/03_Research/test_t13_he4_flat_partial_stationary_root.py), and the preceding [nonstationary-anchor result](T13_HE4_RELAXED_PHI_RESPONSE_BOUNDARY_2026-09-27.md).
