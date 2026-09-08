# Topic 13: distinguish coherent shear from the thermal scalar channel

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE for conditional representation algebra, not physical graphite/UET identification.

WHAT_IS_ACTUALLY_CLOSED: Under an invariant scalar Phi, an unbroken material point group and a Gamma E2g doublet, no nonzero invariant linear force coefficient exists. A scalar quadratic invariant exists. These are different experimental channels, not different names for the same observable.

WHAT_REMAINS_OPEN: The material representation of Phi, identification of the source eigenvectors with the full E2g representation, kinetic normalization, eta, pump tensor, occupancy/bath evolution and same-state material data.

DEPENDENCY_UNLOCKED: Choice of experimental channel only; no physical downstream unlock.

STATUS: CONDITIONAL_ALGEBRA_ONLY. Do not turn the conditional exclusion into a universal no-go.

WHAT_CHANGED: Added representation constraints, independent tests and a source-free audit. No existing action or source coefficient is altered.

EQUATION_OR_MAPPING: Use the E2 representation D(R_theta)=R_(2theta) and reflection diag(1,-1). For V_linear=Phi*l^T*s, invariance requires D^T*l=l, whose solution is l=0. For V_quadratic=Phi*s^T*H*s/2, the symmetric invariant is H=h*I. Group averaging gives the same result independently of a chosen doublet basis. Inversion acts trivially in E2g; the rotation/reflection subgroup already excludes the linear invariant.

VERIFICATION: Seven new algebra/channel tests and thirteen previous mode/transfer tests pass. Linear invariant dimension is zero; symmetric quadratic invariant dimension is one. The group-average residual is 1.434e-16. Source data and holdout are not computational inputs.

CONTROLLING_BLOCKER: physical_scalar_mass_source_and_pump_channel_identification_missing.

NEXT_ACTION: For the thermal route, study scalar occupation/variance and the derivative of mode energy with respect to an independently defined response source. For coherent shear, require polarization, crystal orientation, directional force and detector mapping. Do not use coherent displacement-force residue alone as Phi-to-temperature calibration.

CLAIM_BOUNDARY: Neither an invariant coupling nor a positive variance supplies a numerical coupling constant, temperature, thermalization mechanism or heat flux. Finite-q, strain-broken symmetry, boundaries, higher-order couplings and nonequilibrium preparations require separate analysis. The existing quadratic mass-source route remains allowed, not physically established. Full-topic and separate He-4 status remain unchanged.

## Why the previous matter route is not rejected

The existing candidate interaction is `-epsilon_nc*h*delta_phi*(chi_1^2+chi_2^2)/2`.
It changes a mass/curvature, not a force independent of displacement. A symmetry-preserving
thermal state can have zero mean displacement and nonzero mean-square displacement.
Therefore the absence of a scalar linear force is not an absence of a thermal response.
The continuous internal O(2) of that action is also not automatically the material's
discrete E2g symmetry; agreement at quadratic order does not establish full equivalence.

## Pump information cannot be reduced to intensity alone

In an abstract real in-plane polarization basis, the traceless optical bilinear
`p=(E_x^2-E_y^2,2*E_x*E_y)` transforms as an E2 doublet. A pairing `-p^T*s`
can be invariant when both transform; its actual Raman/absorptive coefficient and
the basis mapping remain unspecified. Orthogonal unit polarizations have identical
intensity but opposite p. An intensity-only record therefore cannot determine this
coherent force. This kinematic example does not assume a purely virtual Raman mechanism.

[Gerbig et al., New Journal of Physics 27 (2025) 053004](https://doi.org/10.1088/1367-2630/adcfbc)
observe polarized coherent shear in few-layer graphite and discuss an impulsive drive
associated with anisotropic carriers. This supports retaining pump-direction information;
it is not a numeric calibration or a same-state TTG dataset. No fitted force lifetime
from that paper is imported.

Evidence: `artifacts/t13_shear_symmetry_audit.json`. Representation matrices are declared
assumptions; the earlier shape-only MP48 audit does not yet test screw/atom-permutation
operations to establish its full irrep. This distinction remains an explicit blocker.
