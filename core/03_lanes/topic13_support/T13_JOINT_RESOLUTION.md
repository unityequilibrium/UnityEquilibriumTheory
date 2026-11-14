# Joint radial, cutoff and inverse resolution

MAJOR_RESULT_CLOSURE: PARTIAL; observed radial/cutoff/inverse sensitivity narrowed on the fixed-action reference, not continuum certification.
WHAT_IS_ACTUALLY_CLOSED: All six locked cases completed. At cutoff48, radial48-to64 changes kappa by0.0042119%. At radial48, cutoff36/48/60 gives an observed spread0.0025656% relative to cutoff48. Spectral and production SVD inverses agree within8.89e-16 relative in these runs. Diagnostic rcond1e-10/1e-12/1e-14 retains the same rank in each case; no negative eigenmode is retained.
WHAT_REMAINS_OPEN: Transition quadrature, channel sample and interpolation dependence; fixed six-direction moment basis; isotropy; simultaneous wider limits; physical material/charge/protocol and SI transport mapping.
DEPENDENCY_UNLOCKED: No physical/Core unlock.
STATUS: JOINT_RESOLUTION_MEASURED_NOT_CERTIFIED.
WHAT_CHANGED: Locked joint plan, runner, complete artifact, two inverse tests and this review. Production action, cutoff policy, source calibration and historical results unchanged. The live job was followed rather than restarted; after its session handle disappeared, completed=true and all six result rows were verified, with no matching process remaining.
EQUATION_OR_MAPPING: Existing full tensor response; a separate symmetric spectral pseudoinverse diagnostic preserves signed eigenmodes above its absolute-relative threshold. No best cutoff selected and production rcond remains1e-12.
VERIFICATION: Two tests pass, including signed-mode agreement with numpy pinv and nonmutation under diagnostic cutoff changes. All artifact input hashes match current files. All six entropy gates meet the original1e-7 threshold. The final job exit code was not available after session expiration; completion is supported by the completed artifact, all six EVALUATED rows and process inspection, not a claimed recovered exit code.
CONTROLLING_BLOCKER: transition_and_directional_basis plus physical_material_mapping. Overall joint_transport_convergence remains open; this pass narrows rather than removes it.
NEXT_ACTION: Lock a transition quadrature/channel/interpolation study on a fixed resolved radial reference, and independently inspect the moment-direction quadrature. Retain these resolution results instead of rerunning coarse radial cases without a changed question.
CLAIM_BOUNDARY: Observed local numerical differences, not rigorous error bounds, material uncertainty or universal convergence. Some isotropy residuals still exceed the existing isotropy criterion. No physical conductivity, full Topic13 or global UET promotion.

## Complete results

| Radial order | Cutoff factor | Kappa, natural |
| ---: | ---: | ---: |
|24|48|147.1939712522|
|32|48|150.1942946966|
|48|48|149.7563525383|
|64|48|149.7500451891|
|48|36|149.7525103283|
|48|60|149.7541047913|

Collision integration order48 and angular integration order32 were held fixed, alongside transition order24,64 channels and interpolation order40. The angular integration parameter does not refine the six-direction moment basis. This is why a stable radial reference does not certify the entire collision model.

The four-point radial sequence is not monotonic. The latest small difference is useful evidence of stabilization, but no extrapolated limit or post-hoc acceptance threshold is introduced. All retained spectral ranks equal state_count minus the five declared invariant modes in this sample; this is not a continuum spectral theorem.
