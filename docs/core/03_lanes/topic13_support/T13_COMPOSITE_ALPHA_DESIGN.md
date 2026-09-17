# Composite-alpha measurement design

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: In the existing conditional product, identifying every factor separately is sufficient but not necessary for identifying alpha magnitude. A full-numerator measurement and heat capacity suffice algebraically.
WHAT_REMAINS_OPEN: Independent physical numerator measurement, fixed normalized-Phi amplitude convention, material operator, sign, SI conversion and covariance provenance.
DEPENDENCY_UNLOCKED: No physical dependency; an alternative measurement-design route is available.
STATUS: CONDITIONAL_DESIGN_NOT_CALIBRATION.
WHAT_CHANGED: Six hypothetical measurement designs, three tests and hashed artifact; no production coefficient or gate changed.
EQUATION_OR_MAPPING: For x=(log|chi|,log|g|,log|Z|,log|C_src|), log|alpha|=a.x with a=(1,1,1,-1). Measurements y=A.x determine the target iff a lies in rowspace(A), equivalently a annihilates null(A).
VERIFICATION: Three tests PASS. Heat capacity alone and heat capacity plus gZ fail. Heat capacity plus chi*g*Z passes at rank2, even though four individual factors remain unidentified. Heat capacity plus chi plus gZ passes at rank3. Normalized shape alone fails. Correlated covariance propagation tested.
CONTROLLING_BLOCKER: independent_source_backed_numerator_measurement_with_fixed_Phi_convention.
NEXT_ACTION: Search existing source/matching packages for an admissible absolute response-amplitude measurement of the numerator, with same material/state and independent calibration role. Do not collect separate factors solely because a checklist requires them if the target combination is independently measured.
CLAIM_BOUNDARY: This does not supply a source, value, sign or physical coupling. The absent strain operator and full transport closure remain open. No holdout access or fit; original gates unchanged.

## Why the target can be known while factors are not

If C_src and N=chi*g*Z are measured independently of the target curve, alpha=N/C_src. Transformations that redistribute g and Z while keeping N fixed cannot change alpha. This is consistent with the existing interface rescaling witness, not a refutation of the normalized-Phi no-go. N must refer to a fixed base-Phi amplitude convention; otherwise rescaling that base coordinate still changes the claimed coefficient.

Logs refer to absolute factors divided by fixed unit reference values, with nonzero fixed signs. This analysis identifies magnitude only. Unknown sign or zero response needs separate treatment. For measurement log-covariance Sigma and target combination c, Var(log|alpha|)=c^T Sigma c. Do not assume independent errors when the measurements share calibration.

An independently measured product can close an observable calibration requirement only. It cannot be relabeled a derivation of each constituent, supply a missing action term, or close full Topic13. The earlier factor-by-factor route remains valid but is not the only algebraically sufficient calibration design.

Evidence: artifacts/t13_composite_alpha_design_audit.json. All design matrices are hypothetical; no numeric calibration output is emitted.
