# Independent soft enrichment and smooth infrared trial controls

Date: 2026-10-01. Selected J01/J02 kinetic reference, not physical admission.
Physical controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Previous measured controller: stable_vector_basis_cross_family_or_cutoff_current_response_not_converged.
This method/contract/registry is locked before the first numerical execution.

## Scientific question and unchanged inputs
Does adding a bounded soft radial seed to the old EVEN space reconcile its
response with SOFT, and can smooth vector trials approach that enriched result?
Retain the same cubic collision form, exact tree kinematics, source momentum
constraint, mu1.28, lambda.01, T=.002/.004 and1% acceptance targets.
Use the prior [stable-vector method](CORE_O2_GOLDSTONE_VECTOR_REFINEMENT.md).
The old EVEN cutoff/basis and EVEN-versus-SOFT FAILs remain immutable.
Agreement of new enriched trial families is not retroactive closure of those FAILs.

## Independently generated HYBRID family
At each shared Gauss bank construct the old EVEN basis by its k^2 recurrence.
Seed list: k, T, EVEN_1,...,EVEN_(N-2).
Use full two-pass weighted Gram orthogonalization on that seed list, keep k first,
and record the seed-to-feature matrix. Evaluate the same EVEN recurrence and
seed transform at every off-grid collision leg. No interpolation, fitted width,
source-dependent basis tuning or collision projection.
The resulting span is {constant,k,k^3,k^5,...,k^(2N-3)}.
HYBRID18 contains EVEN17. SOFT35 contains HYBRID18.
For the SAME finite event form, verify nested/discrete variational response
ordering EVEN17<=HYBRID18<=SOFT35. This is not a continuum upper bound.

## Smooth vector trial and precise domain boundary
For epsilon>0 replace only the constant radial seed by
A_epsilon(k)=T*k/sqrt(k^2+epsilon^2).
Its Cartesian vector is T*k_vector/sqrt(k^2+epsilon^2), smooth at the origin.
All other EVEN seeds, event integration limits and kernel remain unchanged.
epsilon=delta*T/c; delta is dimensionless. This regularizes a TRIAL FEATURE,
not a collision denominator, scattering rate, occupation or momentum cutoff.

For E(k)=c*k+O(k^3), w(k)dk approaches T^2/(6pi^2*c^2)dk as k->0.
|A_epsilon|<=T and A_epsilon->T at every k>0 imply convergence in the
finite-cutoff Bose Hilbert norm by dominated convergence. This establishes
the Gram-norm approximation only. It DOES NOT establish convergence in the
collision quadratic-form domain, a continuum response bound or spectral gap.
Record smooth-trial response refinements numerically without upgrading this lemma.

## Locked execution and targets
Gauss parent/daughter orders96/192/384; cutoffs40/50/60*T/c.
HYBRID features6/10/14/18, fixed SOFT35 and EVEN17 comparison.
Defaultorder384/defaultcutoff60. Smooth HYBRID18 delta=.1/.03/.01/.003.
Separate order refinement for the smallest delta and epsilon refinement;
compare the last smooth response to the unsmoothed HYBRID response.
Keep energy_cut/gap<=.1, event tolerance1e-9, algebra1e-8 and relative
spectral tolerance1e-9. Every finite response/refinement/source target remains1%.

Check the copied make_bank collision function's AST against the immutable
prior implementation, plus order192/cutoff60 matrix/source and response
correspondence for the unchanged EVEN/SOFT families. Then actual Gram, momentum,
source, detailed balance/geometry, spectra, independent frequency/DC resolvents,
nested responses and scale2 for the smooth family. G:E5,Q:E6,b:E5,D:E5,R:E4,
basis-time:E-1. Record k/energy validity separately, no new interaction claims.

A structural PASS is separate from the declared enriched/smooth finite targets.
Any failed target stays OPEN. Even all declared targets passing cannot supply
continuum collision-domain control, an upper error bound, all-channel/interacting
completion, kinetic-to-condensate/charge heat-current or material/SI admission.
Scalar conservation evidence is reused, not rerun. Physical J04/J05/J06 remain
NOT_STARTED. Keep first source/output if numerical repair is needed.
