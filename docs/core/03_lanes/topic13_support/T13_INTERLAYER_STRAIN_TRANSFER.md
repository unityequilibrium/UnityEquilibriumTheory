# Independent axial-strain source: transfer boundary

MAJOR_RESULT_CLOSURE: PARTIAL, not physical material closure.

WHAT_IS_ACTUALLY_CLOSED: A fixed-plane axial-strain source route is identified and source-locked. The MP48 geometry lies beyond that source's compressive reference, so a direct correction is inadmissible.

WHAT_REMAINS_OPEN: Same-state strained force constants, model uncertainty and UET mode normalization. Finding a published derivative does not supply these.

DEPENDENCY_UNLOCKED: None; a candidate research input is available, not an accepted calibration.

STATUS: SOURCE_JOIN_CHECKED_TRANSFER_BLOCKED.

WHAT_CHANGED: Added a source package, derivative/transfer audit and independent tests. Original spectra remain untouched.

EQUATION_OR_MAPPING: Differentiating a power-law frequency fit gives d ln(nu^2)/d epsilon_zz=-6*gamma at its own reference. The source-only value is -10.0374 with fit-only error 0.0012. This is not an experimental error budget or a UET parameter.

VERIFICATION: Thirteen combined tests pass, including central differentiation and refusal of cross-state calibration. PDF and consumed MP48 evidence hashes are checked. The precursor's positive intracell phase agrees with the displacement convention in [Phonopy formulation, dynamical matrix and displacement equations](https://phonopy.github.io/phonopy/formulation.html#dynamical-matrix); this textual check is not a second finite-q reconstruction.

CONTROLLING_BLOCKER: MP48 spacing is 3.53937 angstrom; the independent fit references 3.20 angstrom. The 10.6% difference is between two models, not an experimental strain or evidence of a unique error mechanism.

NEXT_ACTION: Acquire a common-functional strained-structure/force-constant series or a same-state experimental axial response. Separate geometry, electronic-interaction approximation and finite-temperature effects before deciding which explains the frequency mismatch. Do not rescale force constants, import a fit error as model uncertainty, or identify a phonon with Phi.

CLAIM_BOUNDARY: No corrected MP48 frequency, full deformation tensor, alpha_Phi_K, transport or full-topic unlock is produced. Separate He-4 status is unchanged; holdout not read.

## Source assessment

[Sun et al., arXiv:1704.04202v1](https://arxiv.org/abs/1704.04202v1), pages 1-3, use PBE with Grimme vdW. Their fixed-plane compression fit has gamma=1.6729(2), with uncertainty explicitly from fitting. The optimized spacing is 3.20 angstrom and shear frequency 48.70 cm^-1. MP48 instead uses its deposited PBEsol structure. These are independent calculations, not interchangeable material states. No graph has been digitized or published sample data synthesized.

[Lebedeva et al.](https://arxiv.org/abs/1708.01504) compare vdW-corrected functionals and show sensitivity of interlayer properties to functional and geometry. This supports testing those explanations, not declaring that either explains the MP48 mismatch quantitatively.

Evidence: `artifacts/t13_interlayer_strain_transfer_audit.json`; source rows and PDF hash are in the Topic 13 `sun_2017_interlayer_strain_source_package.json`. Raw PDF remains local-only. This note records a research input and exclusion boundary, not a new accepted core equation.
