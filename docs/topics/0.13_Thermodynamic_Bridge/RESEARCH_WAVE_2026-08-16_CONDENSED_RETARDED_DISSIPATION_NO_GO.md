# Research Wave: Condensed Retarded-Dissipation No-Go

MAJOR_RESULT_CLOSURE: `T13_UET_O2_CONDENSED_RETARDED_DISSIPATION_NO_GO` is `CLOSED_AS_NO_GO`.

WHAT_IS_ACTUALLY_CLOSED: The current conservative O(2) action fixes the condensed phase stiffness and tree Goldstone sector, but it contains no dissipative imaginary retarded kernel, collision/noise kernel, or closed-time-path influence functional. Two causal positive-memory witnesses can share the same zero-frequency value while differing at finite frequency. Therefore the conservative action alone cannot identify a unique condensed dissipative kernel.

WHAT_REMAINS_OPEN: A physical condensed collision kernel, state-matched retarded correlator, microscopic SK/influence-functional matching, complete two-fluid constitutive tensor, SI observable map, `alpha_Phi_K`, TTG source package, and Full Topic 13 remain open.

DEPENDENCY_UNLOCKED: Only the structural boundary for the condensed conservative-action dissipation question. No physical Kubo, SI, alpha, TTG, Core, Gravity, or external-validation dependency is unlocked.

STATUS: `PASS_SCOPED_CONDENSED_RETARDED_DISSIPATION_NO_GO`

WHAT_CHANGED: Added an action-matched condensed phase-stiffness/Goldstone check and a causal-memory identifiability audit. The two memory kernels are normalized mathematical witnesses; they are not fitted values, source data, or physical transport coefficients.

EQUATION_OR_MAPPING: `q=Z*mu^2-m_eff(Phi)^2>0`; `f_s=Z*q/lambda`; `Im K_R^cons=0`; `M_R,j(t)=gamma*Lambda_j*exp(-Lambda_j*t)*H(t)`; `M_R,j(omega)=gamma*Lambda_j/(Lambda_j-i*omega)`; `M_R,A(0)=M_R,B(0)` but `M_R,A(omega_probe)!=M_R,B(omega_probe)`.

VERIFICATION: `docs/scripts/audit/audit_topic13_uet_o2_condensed_retarded_dissipation_no_go.py` passes the condensed branch, Goldstone polynomial, retarded support, non-negative real-part, zero-frequency match, finite-frequency separation, ontology, and no-fit checks. Xie 2026 remains unread.

CONTROLLING_BLOCKER: `condensed_sk_influence_functional_or_physical_retarded_correlator_missing`.

NEXT_ACTION: Obtain an allowed state-matched retarded correlator or derive a microscopic condensed SK/influence functional. Do not promote the normalized memory witnesses to physical transport.

CLAIM_BOUNDARY: This is a scoped structural no-go for the current conservative condensed action. It is not a physical Kubo coefficient, a complete two-fluid transport theory, an SI `Phi` map, an `alpha_Phi_K` calibration, a TTG prediction, or Full Topic 13 closure.

Evidence: `docs/core/07_artifacts/topic13/t13_uet_o2_condensed_retarded_dissipation_no_go_audit.json`.
