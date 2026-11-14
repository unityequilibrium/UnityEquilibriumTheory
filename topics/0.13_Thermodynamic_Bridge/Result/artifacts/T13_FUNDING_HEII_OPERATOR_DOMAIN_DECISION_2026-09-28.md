# Frozen He-4 bridge: He-II operator-domain decision

MAJOR_RESULT_CLOSURE: `T13_FROZEN_HEII_OPERATOR_DOMAIN_BOUNDARY` is `CLOSED_FOR_LANE` for the current frozen bundle; the planned predictive-content result remains open.

WHAT_IS_ACTUALLY_CLOSED: The frozen action reference has `q=-0.8715` and zero condensate amplitude, whereas the He-II anchor has positive superfluid fraction. It cannot itself be used as an admitted condensed He-II second-sound linearization. Two alternative tree-condensed points are not material-admitted; the thermal-only Gaussian Phi root fails simultaneous amplitude stationarity in its declared class; the formal auxiliary joint root uses `Z=1.2` rather than the previous `Z=1` prescription and has no physical transfer.

WHAT_REMAINS_OPEN: A named Ward-consistent finite-temperature condensed completion, an independent charge/stiffness-to-He-II density map, a source-to-detector longitudinal two-fluid operator, response-source admission, and clean Core baseline revalidation.

DEPENDENCY_UNLOCKED: Structural route selection only; no physical G1, G2, G0 or Full Topic 13 unlock.

STATUS: `PASS_SCOPED_OPERATOR_DOMAIN_BOUNDARY`; physical G1=`BLOCKED_NO_ADMITTED_CONDENSED_STATE_AND_LONGITUDINAL_OPERATOR`; G2=`UNRESOLVED_OPERATOR_COMPLETION_BOUNDARY_NOT_NONIDENTIFIABILITY_PROOF`.

WHAT_CHANGED: Composed the existing frozen-branch, state-selection, Gaussian no-go, formal auxiliary and source-route results into a hash-backed model-domain decision. No Core equation, calibration value, fit, holdout or threshold changed.

EQUATION_OR_MAPPING: `q=Z*mu^2-m_eff(Phi)^2`. At the frozen point, `q=0.35^2-0.994=-0.8715`. The local calibration map `g` exists, but the physical response map `h(p; protocol)=u2_UET` is not currently defined on this frozen model domain. An SVD of `Dg,Dh` is therefore not a legitimate structural nonidentifiability proof yet.

VERIFICATION: The [machine decision](t13_funding_heii_operator_domain_decision.json) recomputes `q`, checks each scoped result, and stores exact input hashes. Twelve linked Topic 13 tests pass, including two new decision tests. Decision artifact SHA-256: `3e93e42c98af6944747d248b6f5f4f2a997fa538eeed3e1c62c48d22acc9ae01`. Xie 2026 was not read.

CONTROLLING_BLOCKER: `named_admissible_condensed_model_to_observable_operator_missing`. The source package and G0 are separate blockers, not substitutes for the operator.

NEXT_ACTION: Freeze one Ward-consistent condensed approximation and independently justified material state map. Derive its longitudinal excitation/readout operator, or construct a same-calibration/different-response family *inside that named admissible class*. Until then, use the two-week portfolio to state the operator-completion question rather than invent a second-sound score.

CLAIM_BOUNDARY: This is not a theorem against future UET completions, a proof of nonidentifiability of all UET, a physical He-II prediction, external validation, or Full Topic 13 closure. Existing internal tree Goldstone velocities are not relabeled second sound.
