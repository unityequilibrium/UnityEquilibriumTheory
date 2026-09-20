# Independent phase-space measure pilot

MAJOR_RESULT_CLOSURE: PARTIAL.
WHAT_IS_ACTUALLY_CLOSED: Positive independent radial-pair and angular product weights reproduce manufactured scalar moments. Incoming radial pairs grow as n^2 rather than repeating the previous21 pairs.
WHAT_REMAINS_OPEN: Differential cross-section normalization, species and identical-particle factors, boosted outgoing occupations, collision response and physical calibration.
DEPENDENCY_UNLOCKED: None.
STATUS: MANUFACTURED_MEASURE_ONLY.
WHAT_CHANGED: Standalone audit, three tests and hashed artifact; production collision kernels remain unchanged.
EQUATION_OR_MAPPING: x1^2 dx1 x2^2 dx2 du/2 dv/2 dphi/(2*pi), with x=p/P, u=incoming relative cosine and v=outgoing center-of-mass polar cosine.
VERIFICATION: Three tests PASS. Radial4/8/16/32 gives16/64/256/1024 independent pairs. The manufactured exp(-12*(x1+x2)) integral has relative errors0.1111/1.61e-5/7.91e-16/2.22e-15. The last difference is floating-point scale, not monotonic physical convergence. Polynomial and angular moments are checked separately.
CONTROLLING_BLOCKER: differential_cross_section_and_species_symmetry_contract.
NEXT_ACTION: Inspect the declared scattering convention and derive which angular and identical-particle factors belong in the collision integral. Then use exact boosted channels and Bose occupations on these product nodes, independently refining radial and angular orders.
CLAIM_BOUNDARY: Analytic manufactured controls are not thermal data. Fixed incoming orientation is valid only for rotational scalars; tensor response requires global orientation integration. No physical transport coefficient or full Topic13 closure is emitted.

## Scope of the measure

Both radial integrations retain their own Gauss-Legendre nodes and weights. Angular factors are normalized averages, not a derivation of a differential cross section. The physical radial factor P^6/(2*pi^2)^2 is deliberately excluded from this dimensionless pilot. It must be restored consistently with the declared collision convention, without double counting solid angle or total cross section.

The exponential test is manufactured and fixed before running; it is not a Bose distribution or fitted reference. The four resolution rows share cosine order6 and azimuth order16; this does not demonstrate angular convergence of a physical integrand. No old result, threshold, production rate or holdout was altered.

Evidence: artifacts/t13_phase_space_measure_audit.json.
