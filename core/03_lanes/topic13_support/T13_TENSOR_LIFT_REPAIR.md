# Full transverse response lift repair

MAJOR_RESULT_CLOSURE: CLOSED_FOR_LANE; scalar-approximation error removed from the finite-grid heat-flux and entropy lift.
WHAT_IS_ACTUALLY_CLOSED: Production state contracts the complete transverse tensor with the thermal force, transforms that tensor under Lorentz boosts, and agrees with the collision quadratic entropy. Kappa remains trace(K)/3 as a summary only. All ten previously locked cases meet unchanged entropy1e-7 and covariance1e-10 thresholds after this repair.
WHAT_REMAINS_OPEN: Radial/cutoff convergence, finite moment-direction basis, transition/inverse sensitivity, material/protocol and physical transport matching. Isotropy is not newly certified.
DEPENDENCY_UNLOCKED: No physical/Core promotion.
STATUS: TENSOR_BALANCE_REPAIRED_TRANSPORT_UNRESOLVED.
WHAT_CHANGED: Private tensor lift and tensor boost check replace the scalar approximation in the state builder. The existing scalar helper remains an explicit scalar control. Added anisotropic/boost/rejection tests, separate ten-case repair artifact and registry addendum. Frozen scalar baseline is unchanged.
EQUATION_OR_MAPPING: q^mu=K^(mu nu)X_nu; sigma=X_mu K^(mu nu)X_nu/T; K'=Lambda K Lambda^T. No parameter fit, clipping or tolerance relaxation.
VERIFICATION:14 tests passed, including anisotropic off-diagonal response, three boosts, invalid-tensor rejection, frame/legacy regressions and frozen baseline integrity. Ten cases completed; maximum entropy residual2.274e-12 and boost residual6.822e-13. Kappa changes from the same pre-repair case are zero. F0 inventory369/no duplicate IDs.
CONTROLLING_BLOCKER: radial_cutoff_transport_underresolution and physical_material_protocol_mapping.
NEXT_ACTION: Jointly refine radial resolution and cutoff, inspect quadrature coverage and inverse sensitivity. Keep convergence evidence separate from tensor entropy consistency.
CLAIM_BOUNDARY: This repairs a finite-grid response implementation, not physical conductivity or full Topic13. The old isotropy criterion remains unsatisfied for some grids; a tensor response can conserve entropy without being isotropic or numerically converged. No historical gate, calibration or holdout was consumed or replaced.

## Historical evidence and compatibility

The scalar diagnostic baseline remains t13_transport_resolution_audit.json with SHA25628bc408cdc624f33c503c38727c85cff14de104d3c4409ed35cd496a8bda666f. Its four scalar entropy failures remain visible. A regression formerly comparing historical code hashes to the current implementation now locks the historical artifact itself and verifies the unchanged plan; the new repair artifact records current code hashes. This does not pretend that historical hashes still describe the repaired runtime.

The callable public signatures are unchanged. State heat-flux outputs now use the full response and declare FULL_TRANSVERSE_TENSOR_V1. Canonical charged-frame entropy remains in frame_current_decomposition; the legacy formal entropy-current field is still labeled noncanonical. The correction is numerical/constitutive bookkeeping within the existing lane, not a new state or substance.

The preceding attempt was interrupted by an approval usage-limit rejection before code edits. A read-only usage check subsequently showed no active rate limit, and ordinary authorized execution resumed. No reset was redeemed or alternate execution path used to bypass the rejection.
