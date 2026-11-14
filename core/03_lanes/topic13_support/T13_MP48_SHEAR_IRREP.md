# Source Gamma doublet: crystal symmetry identification

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for the MP48 Gamma material irrep.

WHAT_IS_ACTUALLY_CLOSED: The shape-selected pair has E2g characters under all 24 source structure operations. Atom permutation, fractional translation and Cartesian rotation are retained. The unchanged source dynamical matrix commutes with these operations to numerical precision.

WHAT_REMAINS_OPEN: Phi representation, full O(2) correspondence, coupling and kinetic normalization, material frequency mismatch, independent strain response, thermal occupation and bath mapping.

DEPENDENCY_UNLOCKED: The previously conditional E2g selection-rule diagnostic now has a checked material-side Gamma irrep. It still assumes a scalar material representation for Phi and unbroken symmetry; no physical downstream gate opens.

STATUS: PASS_SOURCE_E2G; full_core_unlock=false.

WHAT_CHANGED: Added source crystal action/character audit and four tests. No force constants, structure, source frequencies or existing full-topic artifact changed.

EQUATION_OR_MAPPING: For fractional operation (r,t), map each atom i to j by r*x_i+t modulo the lattice. The Cartesian action is A^T*r*A^(-T), acting in the corresponding atom permutation block. At Gamma all lattice-translation Bloch phases are one. Equal mapped masses are required, so this action also acts in mass-weighted coordinates. The pair representation is E^dagger*U_g*E; characters are independent of eigenvector gauge.

VERIFICATION: Eleven combined tests pass (four new crystal-action tests and seven selection-rule tests). Source hashes verified. Space group 194 and 24 operations found at symprec=1e-6 angstrom. Maximum pair-subspace leakage is 1.965e-12; maximum character error is 3.553e-15. The acceptance tolerance is 1e-8 for these new representation checks, not a changed causal or TTG threshold. Inversion character is +2 and the 60-degree screw character is -1, distinguishing this pair from an ordinary polar in-plane vector. All operations are compared, not only these two examples.

CONTROLLING_BLOCKER: physical_response_source_and_thermal_mode_mapping_missing.

NEXT_ACTION: Carry this verified material-side symmetry into the scalar quadratic occupation/energy route. Derive how an independently defined response source changes the mode energy and how occupations relax. A mode's crystal symmetry cannot determine that coupling coefficient. The independent-strain/material-state mismatch remains open in parallel.

CLAIM_BOUNDARY: Gamma-only harmonic source identification. The matrix test does not identify Phi with the phonon, establish its finite-q irrep, equate continuous internal O(2) with discrete crystal symmetry, repair Raman disagreement or supply alpha_Phi_K. Separate He-4/full-topic status is unchanged.

## Character construction

For proper axial rotations through theta, E2 has character 2*cos(2*theta).
Proper twofold rotations about basal axes have character zero. Inversion is even.
This constructs the D6h E2g character for each operation in the declared frame.
The fractional half-cell translation in the screw operation must still be used
to find the atom permutation, even though its Gamma Bloch phase is one.
Omitting that permutation incorrectly treats the pair as an ordinary vector.

Evidence: `artifacts/t13_mp48_shear_irrep_audit.json` contains each operation,
permutation, character, subspace leakage, force commutator and consumed source hashes.
The earlier shape/residue and conditional selection-rule artifacts remain historical
evidence; their then-open material-irrep item is superseded only by this scoped result.
