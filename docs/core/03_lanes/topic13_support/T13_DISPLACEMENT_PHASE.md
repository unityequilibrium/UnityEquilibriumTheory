# Local displacement phase and readout identity

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the declared same-cell harmonic readout identity only.
WHAT_IS_ACTUALLY_CLOSED: The positive intracell phase used in the local centroid readout agrees with the standard displacement convention, explicit atom-by-atom centroid calculation and a separate commensurate force-matrix construction.
WHAT_REMAINS_OPEN: Off-commensurate interpolation checks, continuum covariance accuracy, whole-layer/coherent-slip mapping, anharmonicity and material-to-UET normalization.
DEPENDENCY_UNLOCKED: None; no physical dependency or full_core_unlock.
STATUS: LOCAL_READOUT_IDENTITY_CLOSED_NOT_MATERIAL_CALIBRATION.
WHAT_CHANGED: Independent phase/readout audit, two tests and hashed artifact. Existing covariance formulas and production dynamics remain unchanged.
EQUATION_OR_MAPPING: P=diag(exp(2*pi*i*q.r_j)); D_cell=P D_phonopy P^dagger; local s=B^dagger P e/sqrt(mu). The explicit atomic readout is the difference of the two mass-weighted same-cell layer centroids.
VERIFICATION: Two tests PASS, including unequal masses, rigid translation and origin shift. Four supercell-commensurate matrix checks give relative differences below9.93e-16; explicit atomic readout differences below2.07e-16. Foundation audit must be reported separately from this lane identity.
CONTROLLING_BLOCKER: continuum_covariance_and_material_to_UET_mapping.
NEXT_ACTION: Retain the existing phase. Specify the desired physical spatial averaging/readout and independently verify off-commensurate interpolation before treating further quadrature refinement as calibration progress.
CLAIM_BOUNDARY: Closing a Fourier/readout identity does not identify a phonon with Phi, give alpha, prove physical dimensional reduction or close Full Topic13. No holdout used.

## Derivation and independent check

The [Phonopy formulation](https://phonopy.github.io/phonopy/formulation.html#dynamical-matrix) includes atomic positions in both the dynamical-matrix phase and displacement expansion. Writing atomic position as cell translation plus basis position gives D_phonopy=P^dagger D_cell P and cell-gauge eigenvectors P e. Thus the positive basis-position phase is required when summing physical displacements inside a single cell.

For each layer a, its centroid displacement is sum_j_in_a m_j u_j/M_a. Substituting the mode displacement gives coefficients sum_j_in_a sqrt(m_j) exp(2*pi*i*q.r_j)e_j/M_a. Their difference equals B^dagger P e/sqrt(mu) for the declared tangent axes. B is the existing mass-normalized relative-layer basis and mu the two layer masses' reduced mass. This is algebraic, not fitted.

The raw-force construction uses integer cell translations independently of Phonopy's phase. It matches after the declared unitary transformation at q=(.2,0,0),(.2,.2,.5),(.4,.2,.5),(.4,.4,0), which are commensurate with the source supercell. This does not establish correctness of the raw wrapped-translation interpolation at arbitrary q; no such claim is made.

Omitting the phase changes the300K covariance matrix by relative Frobenius norms10.017%,18.952%,13.108%,31.211% at these four points. These are pointwise negative controls, not Brillouin-zone integrated errors. No previous covariance artifact omitted the phase, so these numbers are not corrections to the earlier RMS values.

## Physical boundary

The declared observable averages the atoms belonging to one chosen primitive cell within each layer. It is not the centroid of an entire macroscopic layer. Regrouping atoms into neighboring cells can change a local observable unless its measurement weights and translations are transformed consistently. Origin translation only gives a common mode phase and leaves covariance unchanged; the tests check that simpler invariance.

Consequently this result closes a genuine ambiguity in the implementation without closing the desired experimental mapping. A uniform coherent slip, finite measurement footprint and same-cell thermal fluctuation are distinct readouts. The next decision is which observable a permitted calibration actually measures, not whether the existing positive phase should be discarded.

Evidence: `artifacts/t13_displacement_phase.json`, with source/implementation hashes. Source prose above is paraphrased; no source payload or holdout was acquired.
