# Natural fixed-charge response

MAJOR_RESULT_CLOSURE: PARTIAL; ensemble dependence of the existing natural response quantified.

WHAT_IS_ACTUALLY_CLOSED: At the same normal-branch action state T=0.22,mu=0.35,Phi=0.15, fixed-mu and fixed-charge energy derivatives were compared without changing the model. At step0.00025, the fixed-mu thermal susceptibility is0.017682719 versus0.004339685 at fixed charge. Natural quasi-temperature coefficients are +0.002313926 and -0.000562622 respectively. The sign difference persists across steps0.001,0.0005,0.00025.

WHAT_REMAINS_OPEN: Which natural constraint corresponds to the physical He-4 experiment. O(2) charge density has not become atom/mass density by performing this calculation. Neither path is automatically the SVP equilibrium path used for fraction calibration.

DEPENDENCY_UNLOCKED: Natural ensemble-specific comparison only; no physical unlock.

STATUS: ENSEMBLE_COMPARISON_NOT_PHYSICAL_CALIBRATION.

WHAT_CHANGED: Fixed-charge audit/tests, [numerical evidence](../../07_artifacts/topic13/t13_fixed_charge_response_audit.json), and an unmerged equation-registry addendum. Existing alpha,Z,e0 and composition gates remain unchanged.

EQUATION_OR_MAPPING: At fixed n, dmu/dx=-n_x/n_mu and d epsilon/dx=epsilon_x-epsilon_mu*n_x/n_mu. Apply independently to x=T and x=Phi; their ratio defines a different natural quasi-temperature response. The auxiliary charge constraint is not a new physical state or ontology.

VERIFICATION: Two tests PASS for chain rule and singular/unstable susceptibility rejection. Direct root solutions keeping charge fixed agree with the derivative construction: temperature-derivative discrepancy decreases from5.26e-7 to3.29e-8 under fourfold step refinement; Phi-derivative discrepancy is below1.1e-12 in the inspected runs. Maximum charge residual is about2.1e-16. All evaluations stayed on the original branch. F0 inventory369/no duplicates; foundation/compatibility audits PASS with physical states BLOCKED.

CONTROLLING_BLOCKER: Physical perturbation protocol and material-charge correspondence. The sign difference is evidence that the constraint matters, not proof that either physical experiment has the predicted sign. Numerical refinement does not cover source uncertainty or EOS approximation error.

NEXT_ACTION: Specify exchange constraints and material-variable mapping before using a frozen-scale coefficient for independent comparison. If a physical protocol conserves a quantity, map that quantity explicitly and follow its constrained path; do not silently reuse fixed-mu alpha. No need to retune calibration to make these different derivatives agree.

CLAIM_BOUNDARY: Internal natural-unit result, not a new Kelvin alpha, He-4 heat-capacity prediction, external validation or reversal of existing bounded composition. No holdout access or physical parameter change.
