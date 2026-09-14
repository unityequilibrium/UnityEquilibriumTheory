# Controlled rotation profile comparison

MAJOR_RESULT_CLOSURE: PARTIAL; rotation's effect isolated under unchanged weighting, not physical registration closure.

WHAT_IS_ACTUALLY_CLOSED: The same152 source ROIs were fit with a rotation degree of freedom while retaining uniform residual weighting, constant background and source width bounds. Three angular starts per ROI give456 retained fits. All optimizers terminate successfully; maximum start-dependent center difference is2.51e-8px. Primary fits start from the previous unrotated parameters at angle pi; other starts pi+/-0.2 remain visible rather than being selected by best cost.

WHAT_REMAINS_OPEN: Residual structure, detector covariance and actual registration accuracy. Relative residual norm drops from about11.3% to9.00-9.22%, a residual-norm ratio of0.7963-0.8071 versus the unrotated comparator. Rotation explains part, not all, of the mismatch. No measured noise floor permits accepting the remaining residual as noise or rejecting it statistically.

DEPENDENCY_UNLOCKED: Instrument-model comparison only; no physical unlock.

STATUS: ROTATION_COMPARISON_PHYSICAL_ACCURACY_OPEN.

WHAT_CHANGED: Controlled rotated-profile solver/tests and [all fits and summary](artifacts/t13_ued_rotated_position_audit.json). The frozen unrotated artifact remains unchanged.

EQUATION_OR_MAPPING: Separable Voigt profiles in rotated centered pixel coordinates plus constant offset. Source rotated helper also changes weights to1/sqrt(1+raw intensity); this comparator deliberately does not, so the rotation effect is not confounded with weighting. No source lmfit replication or uncertainty model is claimed.

VERIFICATION: Two tests PASS for the nested unrotated limit and known rotated synthetic center. All456 real fits retained; source hashes checked. Foundation and compatibility audits PASS while physical states remain BLOCKED. Maximum center change relative to unrotated primary fits is0.00408846px. Between-cut fitted-center differences remain0.0467351px ON and0.0466842px OFF.

CONTROLLING_BLOCKER: Profile/background/detector model adequacy, not the tested angular starts. A nested model's lower in-sample residual is expected and is not external validation. An optimized profile angle is not a physical sample orientation without reciprocal-space mapping.

NEXT_ACTION: Inspect residual structure/background and detector response before any registration correction; avoid indefinitely adding fit parameters. Keep this instrument work separate from the three physical input packages in t13_full_closure_minimal_input_contract.json: accepted thermal numeric source, independent Phi SI anchor, and physical Kubo/SK/KMS/entropy inputs. This wave accepts none of them.

CLAIM_BOUNDARY: No image transformation, physical calibration, covariance, heat/temperature inference, alpha, holdout or full-topic promotion. Synthetic tests establish implementation behavior only; solver stopping criteria are not physical precision.
