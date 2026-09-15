# Research Wave: Finite-Temperature EOS Stability Boundary

MAJOR_RESULT_CLOSURE:
T13_UET_O2_FINITE_T_TWO_FLUID_STATIC_RESPONSE_LANE remains CLOSED_FOR_LANE.
This wave closes a narrower stability/sign-policy boundary inside that lane;
Full Topic 13 remains BLOCKED_OPEN_T13_FULL_BRIDGE/PARTIAL.

WHAT_IS_ACTUALLY_CLOSED:
The finite-temperature two-sector verifier now checks the total-state entropy
and charge susceptibility on the declared reference grid. It also makes the
sector sign convention explicit: condensate and normal charge/energy entries
are derivatives of their declared grand-pressure sectors, so a signed residual
entry is not silently treated as a negative physical normal density.

The condensed reference states deliberately retain their negative residual
normal charge/energy entries. This is a non-clipping witness that the lane is
using the declared derivative decomposition rather than manufacturing positive
sector data. The nonnegative quantities used for the stability boundary are the
total entropy, total susceptibility, and static transverse response.

WHAT_REMAINS_OPEN:
The physical retarded Kubo coefficient, microscopic collision/self-energy
input, complete dissipative two-fluid constitutive tensor, physical SK/KMS
matching, dimensional Phi-to-SI map, independent alpha calibration, and
source-backed TTG C_src remain open.

DEPENDENCY_UNLOCKED:
Only the total-state natural-unit EOS stability/sign-policy boundary inside the
finite-temperature static lane is unlocked. No physical transport, SI, alpha,
TTG, Core, Gravity, or external-validation dependency is unlocked.

STATUS:
PASS_ACTION_DERIVED_FINITE_T_TWO_FLUID_STATIC_RESPONSE_LANE

WHAT_CHANGED:
The lane contract declares an equilibrium stability boundary and a residual
sector sign policy. The verifier adds total entropy, total susceptibility, sign
boundary, and non-clipping checks. The artifact, major-result register, and
dependency metadata were regenerated with the new evidence hashes.

EQUATION_OR_MAPPING:
pressure split: p = p_condensate + p_normal

sector derivatives:
n_i = partial_mu p_i
epsilon_i = -p_i + T*s_i + mu*n_i

stability boundary on the declared reference grid:
s_total >= 0, chi_total >= 0

The residual sector derivatives are not a Landau normal mass density and are
not a replacement for a retarded Kubo response.

VERIFICATION:
The lane verifier passed with no failed checks. Focused regression passed 11
tests. No source rows, fitting, target data, holdout access, SI coefficient,
or numeric alpha value was used.

CONTROLLING_BLOCKER:
eos_transport_kms_entropy_completion_missing

NEXT_ACTION:
Advance the state-matched retarded transport/collision record and complete the
finite-temperature SK/KMS and entropy-production matching. Keep the natural
unit and static-response boundary until those inputs are independently
available.

CLAIM_BOUNDARY:
This is an action-derived natural-unit stability/sign-policy result. It is not
a physical charge EOS, Kubo coefficient, SI Phi-to-temperature map, alpha
calibration, TTG prediction, external validation, or Full Topic 13 closure.

Evidence artifact:
docs/core/07_artifacts/topic13/t13_uet_o2_finite_temperature_two_fluid_response_audit.json
