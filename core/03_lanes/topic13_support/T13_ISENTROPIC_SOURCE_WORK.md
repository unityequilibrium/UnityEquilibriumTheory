# Isentropic source-work check

MAJOR_RESULT_CLOSURE: PARTIAL; current-EOS reversible work accounting checked, not physical thermalization.
WHAT_IS_ACTUALLY_CLOSED: At fixed volume, entropy density and O(2) charge density, the current natural EOS gives dT/dPhi about-0.00125705. Its energy derivative agrees with generalized source work -partial_Phi p, about-7.89678e-6. Reversible heat is zero by the imposed entropy constraint; temperature change alone is not proof of heating.
WHAT_REMAINS_OPEN: Physical state/constraint mapping, finite-rate entropy production, and historical EOS-version reconciliation. Charge is not material mass density.
DEPENDENCY_UNLOCKED: Natural reversible accounting only.
STATUS: CURRENT_EOS_REVERSIBLE_WORK_NOT_HISTORICAL_REPLICATION.
WHAT_CHANGED: Source-work audit, tests and artifact. The interrupted prior attempt had created no files. The first completed run rejected a stale source hash; inspection found the committed EOS repair bd55dc487. This calculation now explicitly uses current code and historical initial coordinates only; both historical and current hashes are recorded, not relabeled as matching.
EQUATION_OR_MAPPING: Solve J_(s,n)/(T,mu)*(T_Phi,mu_Phi)=-(s_Phi,n_Phi); at fixed volume d epsilon=T ds+mu dn-p_Phi dPhi. No new physical coupling is asserted.
VERIFICATION: Two unit tests; direct entropy/charge roots and derivative construction at three steps. At finest step, relative first-law discrepancies are3.46e-6 (chain) and2.23e-7 (direct roots); largest scaled root constraint residual below4.2e-13. The root residual tolerance1e-9 is numerical, not a physical or causal threshold. No claim that residual has converged to zero under all numerical controls.
CONTROLLING_BLOCKER: Mapping the natural reversible path to a physical process; obsolete EOS hashes also prevent calling historical composition recursively source-current without further audit.
NEXT_ACTION: Reconcile EOS-dependent historical evidence in a separate scoped wave. Keep current calculations distinct; do not rebuild calibration or promote/downgrade Core solely from this derivative test.
CLAIM_BOUNDARY: No Kelvin alpha, finite-rate isolation, actual heat flow, holdout or Core gate change. Existing unrelated dirty artifacts remain untouched.
