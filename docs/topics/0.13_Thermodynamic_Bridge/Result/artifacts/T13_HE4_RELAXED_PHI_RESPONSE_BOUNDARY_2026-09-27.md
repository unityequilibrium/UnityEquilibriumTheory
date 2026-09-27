# Topic 13: local relaxed-Phi response boundary

MAJOR_RESULT_CLOSURE: `T13_HE4_RELAXED_PHI_RESPONSE_NONIDENTIFIABILITY_BOUNDARY` is `CLOSED_FOR_LANE` only for a conditional local class result. It does not close a physical He-II response or Full Topic 13.

WHAT_IS_ACTUALLY_CLOSED: The current fixed-`Phi` quasiparticle EOS does not by itself select an ordinary relaxed-`Phi` susceptibility. Two explicit positive-curvature local conservative completions share the same anchor pressure, charge density, and clamped susceptibility but give different relaxed susceptibilities. Under this class and nonzero mixed derivative, stable local relaxation increases susceptibility relative to clamping. A separate probe finds that the same conditional root is **not stationary** for the declared flat, homogeneous partial combination `Omega=-p_qp+epsilon_nc U(Phi)`.

WHAT_REMAINS_OPEN: The displayed `U_K` is not an admitted UET action or a helium material response law. The repo does declare a candidate `U(Phi)`, but its finite-temperature, curved/renormalized completion is not established by this probe. Its stationary physical state, effective curvature, the Noether-charge-to-atom and pressure maps, an independent same-state isothermal response row, and dynamical transport remain open.

DEPENDENCY_UNLOCKED: None. This narrows the measurement/derivation requirement; it does not open G0, Core, TTG validation or second sound.

STATUS: `PASS_SCOPED_RELAXED_RESPONSE_NONIDENTIFIABILITY`; `full_core_unlock=false`.

WHAT_CHANGED: Added an executable mixed-derivative and local-completion audit, two tests, this note and a hash-backed JSON artifact. No Core equation, coefficient, source row or holdout policy changed.

EQUATION_OR_MAPPING: With `delta=Phi-Phi0`, set `Omega_K=-p_qp+U_K` and `U_K=p_Phi|0 delta+(p_PhiPhi|0+K)delta^2/2+lambda delta^4/4`, where `K,lambda>0`. Then `Omega_Phi|0=0`, `Omega_PhiPhi|0=K`, `dPhi/dmu=p_muPhi/K`, and `chi_relaxed=p_mumu+p_muPhi^2/K > chi_clamped=p_mumu` when `p_muPhi != 0`. For the *declared flat partial* potential instead, `Omega_Phi=epsilon_nc U'(Phi)-p_Phi`. Neither equation is a helium SI map.

VERIFICATION: At the prior **conditional** condensed root, `p_mumu=9.33719371`, `p_muPhi=0.074250014` in natural units. Synthetic `K=1` and `K=2` give `chi_relaxed=9.34270678` and `9.33995024`, respectively, versus the same clamped `9.33719371`. For the declared flat partial potential with `epsilon_nc=0.05`, `epsilon_nc U'=0.00766875` while `p_Phi=0.04897460`, giving `Omega_Phi=-0.04130585`, not zero; local curvature is positive `0.05257457`. Coarse/fine derivative stencils agree within recorded spreads and match the prior clamped EOS state. The three linked Topic 13 test modules gave eight passes. JSON SHA-256: `73d5cfc943187d345992b330514830a31529d2dd9af07d995d94a2f9d3d8fd09`.

CONTROLLING_BLOCKER: `declared_flat_partial_action_not_stationary_at_conditional_root`. A source row for ordinary compressibility alone cannot rescue a nonstationary anchor or select a prediction when effective `K` is still free.

NEXT_ACTION: First derive/register a self-consistent finite-temperature stationary `Phi` background from the declared action, with explicit curvature/vacuum/source terms and stability checks, or state why this flat partial composition is inapplicable. Then fix the effective response curvature independently and admit the charge/pressure map before reserving an isothermal source row as a test; do not choose `K` from that row and call it prediction.

CLAIM_BOUNDARY: The synthetic family is local and conditional; the declared-action check is only a flat partial-action probe. Nonstationarity here is not a no-go for a curved, renormalized or otherwise completed UET action. The result does not prove two physical UET completions exist, define a laboratory `Phi` clamp, establish He-II compressibility, give a TTG prediction, consume Xie 2026, or validate UET externally. `R_gen` is absent from the state.

Evidence: [machine-readable audit](t13_he4_relaxed_phi_response_boundary.json), [calculation](../../Code/03_Research/Research_T13_He4_Relaxed_Phi_Response_Boundary.py), [tests](../../Code/03_Research/test_t13_he4_relaxed_phi_response_boundary.py), and the prior [clamped response design](T13_HE4_CONDITIONAL_COMPRESSIBILITY_DESIGN_2026-09-27.md).
