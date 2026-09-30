# Topic 13: formal auxiliary Phi/condensate joint root

MAJOR_RESULT_CLOSURE: `T13_FORMAL_AUXILIARY_PHI_CONDENSATE_JOINT_STATIONARITY` is `CLOSED_FOR_LANE` only for Core's fixed-prescription **formal** auxiliary-field configuration (`Z=1.2`). It is not a microscopic, material-matched or SI thermal result.

WHAT_IS_ACTUALLY_CLOSED: At fixed natural-unit `mu=1.3`, the flat homogeneous composition of the declared auxiliary functional plus `epsilon_nc U(Phi)` has a positive-condensate point satisfying its auxiliary gap, condensate-amplitude, Ward-gap and Phi equations. The analytic Phi envelope derivative agrees with finite differences both at and away from the root. This demonstrates a formal route around the *thermal-only Gaussian* amplitude no-go without reusing a density target.

WHAT_REMAINS_OPEN: A controlled microscopic 2PI/1/N or equivalent derivation, physical finite-temperature renormalization, admitted material correspondence, thermal transport/Kubo/SK-KMS, SI mapping, independent `alpha_Phi_K`, and external response data. The prior normalized `Z=1` configuration is outside this auxiliary implementation's `Z>1` domain.

DEPENDENCY_UNLOCKED: Formal feasibility and a precise model-selection boundary only. No physical Topic 13, Core, TTG, He-II or external-validation dependency is unlocked.

STATUS: `PASS_FORMAL_AUXILIARY_PHI_JOINT_ROOT`; `full_core_unlock=false`.

WHAT_CHANGED: Added a Topic 13 audit and two tests using Core's published auxiliary reference configuration and fixed momentum cutoff. No Core equation, source row, threshold or holdout policy changed.

EQUATION_OR_MAPPING: With `M^2=Z mu^2` and `rho=(M^2-m_eff^2(Phi)-2 lambda I_R)/lambda`, the stationary envelope gives `partial_Phi Omega_total=epsilon_nc*[U'(Phi)-h_coupling*(Z mu^2-m_eff^2(Phi))/(2 lambda)]`. Its local curvature is `epsilon_nc U''(Phi)-epsilon_nc^2 h_coupling^2/(2 lambda)>0`. This formal Phi equation has no explicit `T` at fixed `mu`, although `rho`, charge and entropy vary with `T`.

VERIFICATION: At `T=0.20,0.25,0.28`, `mu=1.3`, `Z=1.2`, the root is `Phi=0.268626816335582`, with profiled Phi curvature `0.121085609936377`. Across quadrature orders `128/192`, the condensate amplitude squared is positive (about `1.899`, `1.895`, `1.893` by increasing temperature); numerical Phi derivatives at the root are about `2.7e-10`, and the off-root derivative at `Phi=0.2` agrees with the analytic `-0.0079625`. Twenty-five Topic 13 He-4 and three Core auxiliary tests pass. The old normalized `Z=1` action is rejected by the auxiliary function's declared domain. JSON SHA-256: `eafd283cc7cde049c4217a3462ea1f13103bbcaeee5185240797f43527eaf662`.

CONTROLLING_BLOCKER: `microscopic_2pi_or_controlled_1N_matching_missing`. The formal Ward condition and joint stationary point do not select a physical finite-temperature scheme.

NEXT_ACTION: Derive or source-lock one controlled interacting condensed approximation with a fixed renormalization prescription and check its Phi/amplitude stationarity at the *same declared action parameters*. Do not transplant this `Z=1.2` root to `Z=1` or compare its response to He-II/TTG before a material map and independent observable are admitted.

CLAIM_BOUNDARY: This is a synthetic, natural-unit, flat homogeneous formal auxiliary-field point, not a full Hessian or curved-action stability result. The temperature-independent Phi equation at fixed chemical potential is a structural limitation of this approximation, not an experimental prediction. `C`, `Phi` and `R_gen` keep their established ontology; Xie 2026 was not read.

Evidence: [machine-readable audit](t13_he4_formal_auxiliary_phi_joint_root.json), [calculation](../../Code/03_Research/Research_T13_He4_Formal_Auxiliary_Phi_Joint_Root.py), [tests](../../Code/03_Research/test_t13_he4_formal_auxiliary_phi_joint_root.py), [Core formal auxiliary lane](../../../../core/07_artifacts/topic13/t13_uet_o2_auxiliary_field_condensed_audit.json), and [Gaussian boundary](T13_HE4_PHI_AMPLITUDE_COMPATIBILITY_2026-09-27.md).
