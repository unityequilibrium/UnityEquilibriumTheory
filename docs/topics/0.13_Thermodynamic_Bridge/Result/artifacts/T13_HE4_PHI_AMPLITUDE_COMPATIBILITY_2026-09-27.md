# Topic 13: Phi-only root versus condensate-amplitude stationarity

MAJOR_RESULT_CLOSURE: `T13_HE4_PHI_ONLY_ROOT_THERMAL_GAUSSIAN_AMPLITUDE_NO_GO` is `CLOSED_AS_NO_GO` for **simultaneous stationarity in the tree plus stable thermal-Gaussian class at the conditional Phi-only root**. This applies an existing scoped Core theorem; it is not a universal no-go for UET.

WHAT_IS_ACTUALLY_CLOSED: The new conditional Phi-only point satisfies the analytic no-go domain (`T>0`, `q>0`, positive quartic/kinetic coefficients, `x=A^2>=q/lambda`, stable modes). At its tree amplitude `x=q/lambda`, the tree derivative is zero and the thermal Gaussian amplitude derivative is positive. Thus solving the Phi equation did not close finite-temperature condensate-amplitude stationarity in that same approximation.

WHAT_REMAINS_OPEN: Vacuum renormalization, finite-temperature interacting self-energy, a microscopic Ward-preserving 2PI or controlled 1/N scheme, simultaneous amplitude/Phi solution in that named scheme, material map, and independent response data. The formal Ward-constrained lane is not a physical scheme selection.

DEPENDENCY_UNLOCKED: The research route is narrowed: do not repeat a thermal-only Gaussian parameter search expecting a stationary condensed root. No physical Core, TTG, second-sound or external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_PHI_ROOT_AMPLITUDE_NO_GO`; `full_core_unlock=false`.

WHAT_CHANGED: Added an executable parameter-domain/one-sided-derivative audit, two tests, JSON evidence and this note. Core equations, source rows, thresholds and holdout policy were not changed.

EQUATION_OR_MAPPING: At the conditional Phi-only point, `q=Z mu^2-m_eff(Phi)^2>0` and `x0=q/lambda`. For the declared stable thermal-only Gaussian domain `x>=x0`, the existing proof gives `partial_x(Omega_tree+Omega_G)>0` for `T>0`. The independent equation `epsilon_nc U'(Phi)-partial_Phi p_qp=0` does not imply `partial_x Omega=0`.

VERIFICATION: `T_nat=0.22`, `mu_nat=1.851515585`, `Phi_nat=0.674642478`, `q=x0=2.455095661` for the current unit coefficients. Representative positive mode-root and derivative margins pass for `k=0.01,0.1,1.0`. One-sided total-potential secants stay positive for relative `x` steps `0.01,0.005,0.0025` at quadrature orders `128` and `192` (about `0.00960` down to `0.00536`); these are witnesses, not a continuum limit estimate. Twenty-three Topic 13 He-4 tests and eight related Core tests pass. JSON SHA-256: `6bc82feda38344a3e9183b3c5d762952b7b0526e49368d486e3dfbe1ab13c716`.

CONTROLLING_BLOCKER: `ward_preserving_condensed_2PI_or_1N_microscopic_completion_missing`. The existing formal Ward lane closes symmetry compatibility only, not physical finite-temperature renormalization.

NEXT_ACTION: Select and specify one Ward-preserving interacting/renormalized finite-temperature approximation with its counterterms, state variables, units, conservation and stability conditions. Test simultaneous amplitude and Phi stationarity there before transferring any response coefficient to a He-II comparison; keep the thermal-only Gaussian no-go as a frozen baseline.

CLAIM_BOUNDARY: This is a scoped incompatibility of the conditional Phi-only root with condensate-amplitude stationarity in one thermal-only Gaussian class. It does not rule out other named completions or predict He-II properties. No Xie 2026 data was read; `C`, `Phi` and `R_gen` retain their established meanings.

Evidence: [machine-readable audit](t13_he4_phi_amplitude_compatibility.json), [calculation](../../Code/03_Research/Research_T13_He4_Phi_Amplitude_Compatibility.py), [tests](../../Code/03_Research/test_t13_he4_phi_amplitude_compatibility.py), [conditional Phi-only point](T13_HE4_FLAT_PARTIAL_STATIONARY_ROOT_2026-09-27.md), and the existing [Core no-go](../../../../core/07_artifacts/topic13/t13_uet_o2_gaussian_thermal_stationarity_no_go.json).
