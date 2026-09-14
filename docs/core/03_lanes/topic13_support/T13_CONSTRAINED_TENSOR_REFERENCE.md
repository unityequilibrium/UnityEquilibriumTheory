# Three-source constrained thermal tensor reference

MAJOR_RESULT_CLOSURE: PARTIAL; fixed-grid tensor response, reciprocity and factorized balance evaluated through the existing covariant heat lift.
WHAT_IS_ACTUALLY_CLOSED: The previous x-only reference now includes three independent forces and all nine response entries. Both direction rules at120/180 digits give positive symmetric-part eigenvalues, reciprocal cross responses and factorized dissipation matching the response matrix. Sixteen force/lift cases meet unchanged entropy1e-7, boost1e-10 and isotropy1e-8 criteria.
WHAT_REMAINS_OPEN: Input-rounding sensitivity, interpolation consistency, resolution convergence, complete charged-frame state integration, production replacement and physical material mapping.
DEPENDENCY_UNLOCKED: Internal tensor reference available for subsequent checks; no physical/Core unlock.
STATUS: TENSOR_REFERENCE_MEASURED_NOT_PHYSICAL_CLOSURE.
WHAT_CHANGED: Multi-source reference solver, independent tests, four-case tensor artifact, separate covariant-lift audit and registry proposal. Production defaults and prior failure/x-only artifacts unchanged.
EQUATION_OR_MAPPING: H Psi+C Lambda=W G; C.T Psi=0; K=G.T W Psi. Compare all entries with D=Psi.T diag(w*gamma) Psi+(J Psi).T R (J Psi), then q=K X and sigma=X.T K X/T.
VERIFICATION: Nine tests PASS including pivoted multi-RHS comparison, known off-diagonal response, x-only reference regression and original tensor-lift tests. Four tensor cases and sixteen lift cases complete with exit0. F0 inventory369/no duplicates, PASS_WITH_DISCLOSED_GAPS; foundation and compatibility audit PASS with physical gates BLOCKED. Source hashes verified.
CONTROLLING_BLOCKER: input_interpolation_and_resolution_consistency; full charged-frame production integration remains separate.
NEXT_ACTION: Test deterministic input perturbations and interpolation-support dependence without selecting a best-fit setting. Retain the full tensor reference and then connect the charged-frame state outputs only after matching their response coordinates.
CLAIM_BOUNDARY: Fixed binary64 model inputs solved accurately, not high-accuracy physical data. These are coarse-grid natural coefficients, not SI conductivity, full finite-temperature transport, material validation or Full Topic13 closure.

## Full response results

Controls remain T=.22,mu=.35,Phi=.15,radial8,collision24,angular24,cutoff48,transition24,64 channels,interpolation40. One LU decomposition is reused for three source columns; no rcond, clipping, symmetrization of the reported K or parameter fit is used.

| Quantity | Axis6 | Axis/cube14 |
| --- | ---: | ---: |
| trace(K)/3 |254.82471925625518525|254.82471925625526431|
| Largest isotropy relative residual |2.224e-74|8.238e-31|
| Largest reciprocity relative residual |5.386e-113|5.480e-115|
| Largest matrix balance relative residual |1.529e-112|1.376e-114|
|120/180 reported-matrix relative difference |6.577e-113|0 at50 reported digits|

The symmetric-part eigenvalues are positive in both cases. Symmetric-part eigenvalues are a diagnostic, not a replacement for the unsymmetrized response, whose reciprocity residual is reported separately. Agreement at reported precision does not establish physical accuracy to that precision.

The covariant lift consumes binary64 conversions of the reference tensors. For x,y,z and mixed force(1,-.5,.25), it compares the factorized dissipation contraction with sigma and applies the existing x-boost0.37 check. Maximum boost residual is6.822e-13; the two entropy contractions agree at the reported binary64 precision. This does not validate the complete charged Landau/Eckart state builder, which is not replaced here.

The earlier legacy fourteen-direction isotropy failure and failed float64 weighted-pullback artifacts remain historical. The present result changes both coordinate handling and solve representation relative to the legacy route; it does not attribute every old discrepancy solely to precision.

## Evidence

- artifacts/t13_constrained_tensor_audit.json: four full tensor cases and input hashes.
- artifacts/t13_constrained_tensor_lift_audit.json: sixteen force/lift checks, reported precision differences and source hashes.
- artifacts/t13_constrained_tensor_registry_addendum.json: unmerged reference-only mapping, with no physical unlock.
