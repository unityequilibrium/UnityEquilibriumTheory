# Topic 13: conditional Noether-to-He-4 density-map circularity

MAJOR_RESULT_CLOSURE: `T13_HE4_CONDITIONAL_CHARGE_MAP_DENSITY_CIRCULARITY` is `CLOSED_FOR_LANE` as an algebraic **conditional** result. No physical He-II state selection, prediction, or Full Topic 13 closure follows.

WHAT_IS_ACTUALLY_CLOSED: The simplest proposed shortcut would identify the full action pressure with `p_SI=e0 p_nat`, set `mu_SI=mu_offset+k_B theta_T mu_nat`, and identify O(2) Noether charge with helium atom number. These are **three new material-correspondence assumptions**, not consequences of the existing local beta/energy-scale convention. Under them the chain rule gives `n_He4=(e0/(k_B theta_T)) n_O2`. But the existing `e0` itself equals `n_He4 k_B T0` and `T0=theta_T T_nat`, so the required action charge is exactly `n_O2=1/T_nat`, independent of the measured `n_He4`. Selecting `mu` to satisfy this equation and reporting that the same density is reproduced is circular, not independent validation.

WHAT_REMAINS_OPEN: A sourced or action-derived atom-number coupling/current normalization, absolute grand-pressure and chemical-potential correspondence, independently anchored `Phi`, and an external observable **not already consumed by `e0`**. A condensed longitudinal two-fluid operator and source protocol remain additional gates.

DEPENDENCY_UNLOCKED: None. The shortcut only produces an internal state under added assumptions.

STATUS: `PASS_SCOPED_DENSITY_CIRCULARITY_BOUNDARY` for the declared hypothetical map; physical map remains unadmitted.

WHAT_CHANGED: Added an executable chain-rule/circularity audit, three tests, hash-backed JSON and this result note. No Core equation, source row, calibration coefficient or acceptance threshold was changed.

EQUATION_OR_MAPPING: `n_SI=(partial p_SI/partial mu_SI)_T=(e0/E_mu)n_nat` for a *hypothetical full pressure correspondence* with `E_mu=k_B theta_T`; with `e0=n_SI k_B T0`, this becomes `n_nat=E_mu/(k_B T0)=theta_T/T0=1/T_nat`. An additive `mu_offset` does not change the derivative. Neither the physical material charge identity nor the full pressure correspondence is currently admitted. The repo's Noether-coordinate contract explicitly says mass/particle-number interpretations require separate evidence.

VERIFICATION: At `T_nat=0.22`, the conditional target is `n_O2=4.5454545`. Solving the *finite-temperature* action charge equation at fixed `Phi=0.15` yields an internal condensed root `mu_nat=1.85568857`, with positive total entropy/susceptibility; this is not a calibrated helium state. Repeating the algebra with synthetic physical density factors `0.5`, `1`, and `2`, while recomputing `e0` from each density, leaves the required natural charge and root unchanged and reproduces each input density by identity (relative residual about `1.45e-12` from numerical root tolerance). Three focused tests pass. Artifact SHA-256: `977f43f874d9abcedd18579278cf35e5fa0b0cbcdfbc4b797069b4895f292f4a`.

CONTROLLING_BLOCKER: `Noether_charge_to_helium_atom_identity_not_admitted`; the current `e0` record is a normalization convention and cannot act as an independent absolute-pressure or charge-correspondence proof.

NEXT_ACTION: To test this route without circularity, first declare and justify a physical atom-number source coupling, chemical-potential scale, material pressure/ensemble map, and independent `Phi` selection. Treat the existing density row as calibration because it built `e0`; preregister a separate response such as a state-matched density derivative/compressibility or phase-stiffness measurement with its own source, units and uncertainty. Only after that should one ask whether an absolute condensed state is identified. If these correspondences cannot be derived or sourced, publish the scoped non-identifiability result rather than claim a density prediction.

CLAIM_BOUNDARY: The conditional root and its tree Goldstone mode are not He-II predictions or second sound. This result does not reject all possible O(2)-to-helium material maps; it rejects counting the same density twice as calibration and independent confirmation. No Xie 2026 holdout data or target-curve fitting was used.

Evidence: [machine-readable audit](t13_he4_conditional_charge_map_circularity.json), [calculation](../../Code/03_Research/Research_T13_He4_Conditional_Charge_Map_Circularity.py), [tests](../../Code/03_Research/test_t13_he4_conditional_charge_map_circularity.py), and the preceding [state-selection boundary](T13_HE4_CONDENSED_STATE_SELECTION_BOUNDARY_2026-09-27.md).
