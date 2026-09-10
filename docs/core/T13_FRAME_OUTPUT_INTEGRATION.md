# Frame-current output integration

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE; explicit charged-frame current decomposition is now emitted by the existing production state builder.
WHAT_IS_ACTUALLY_CLOSED: Output separates raw energy flux Q, charge diffusion V, invariant heat Q-hV and canonical S_L=s*u+(Q-muV)/T. Linear Eckart-transformed entropy current is also reported and agrees. Existing legacy heat/entropy fields are retained but their noncanonical roles are explicit.
WHAT_REMAINS_OPEN: Full historical composition/registry integration, finite-cutoff convergence, material-charge and protocol mapping, nonlinear and two-fluid completion.
DEPENDENCY_UNLOCKED: No physical/Core readiness promotion.
STATUS: FRAME_OUTPUT_INTEGRATED.
WHAT_CHANGED: Added optional frame_current_decomposition to the existing dataclass, with explicit roles and validity boundary; no new public callable API. Added production-output audit/test/artifact. Did not overwrite historical gates or recalibrate any source.
EQUATION_OR_MAPPING: The previous linear frame derivation is now used on raw moment currents in the production path. Canonical output is frame_current_decomposition.landau_entropy_current_contravariant. Legacy entropy_current_contravariant remains formal s*u+q_heat/T and must not be treated as the canonical Landau current.
VERIFICATION:16 related tests pass. Current/heat identities checked for unit and1e-9 driving, with prior entropy Hessian/streaming/conservation tests retained. F0 inventory369/no duplicates. Search within core Python found no other production consumer of the legacy entropy field; this is not a repository-wide consumer certification.
CONTROLLING_BLOCKER: finite_cutoff_convergence and physical_material_charge_protocol_mapping; historical downstream consumers require explicit integration review.
NEXT_ACTION: Check collocation/resolution dependence of the shared-action heat/charge response before assigning material meaning or updating historical readiness. Keep coefficient convergence separate from the frame identities, which can hold on an unconverged grid.
CLAIM_BOUNDARY: Linear coefficient/probe outputs, not a finite hydrodynamic solution. Unit-force V/n norm is298349.67646; small-probe norm is.00029834967646. Neither is marked as a validated finite-velocity state. O(2) charge remains distinct from material mass, and no physical conductivity or global theory closure is asserted.

## Compatibility boundary

New fields are additive and the existing callable signature is unchanged. The generic projector helper still supplies the legacy formal lift; canonical charged-frame interpretation is attached only where the state builder has the required EOS and moment currents. The linear Eckart velocity shift is not normalized or promoted to an exact velocity. A very large formal unit-response coefficient is not by itself superluminal propagation: the unit probe has not been established as a realizable perturbation in the linear regime.
