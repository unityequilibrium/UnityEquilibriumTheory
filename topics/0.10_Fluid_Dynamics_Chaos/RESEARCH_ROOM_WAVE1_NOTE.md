# Topic 0.10 Research Room Wave 1 Note

STATUS: INTERNAL_SIMPLIFIED_COMPARATOR_ONLY

WHAT_CHANGED: Wave 1 keeps Topic 0.10 on the standard-fluid comparator and formula-audit lane. Full UET constitutive transport is deferred behind the post-Gravity dependency gate.

EQUATION_OR_MAPPING: The comparator uses the embedded simplified finite-difference Navier-Stokes baseline in benchmark units. It is not a dimensional UET constitutive equation.

VERIFICATION: The latest fluid benchmark artifact is read as an internal implementation comparison under its declared grid, timing, and stability contract.

CONTROLLING_BLOCKER: External CFD accuracy, full constitutive transport, and any physical observable mapping are outside this Wave 1 lane.

NEXT_ACTION: Preserve the comparator/formula audit and wait for the Core/Gravity dependency gate before expanding transport scope.

CLAIM_BOUNDARY: A comparator `PASS` is an internal simplified benchmark only; it is not external CFD validation, a Navier-Stokes theorem result, or proof of UET transport.
