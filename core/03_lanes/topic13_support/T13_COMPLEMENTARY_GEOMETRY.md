# A concrete complementary-information route

MAJOR_RESULT_CLOSURE: PARTIAL; an ideal added-geometry design removes the sampled model's energy null space.

WHAT_IS_ACTUALLY_CLOSED: Adding reciprocal planes l=-2,-1,0,1,2 to the same six reduced q points yields rank 12 and energy null projection below 1.2e-15. Basal-only and l=0,+1 designs remain energy-ambiguous. The earlier ambiguity is therefore not unavoidable within the source model.

WHAT_REMAINS_OPEN: Experimental access, matched preparation/orientation, actual atomic factors and detector covariance, conditioning, full-zone energy integration and independent Phi coupling.

DEPENDENCY_UNLOCKED: Complementary measurement/source targeting only; no physical gate.

STATUS: COMPLEMENTARY_DESIGNS_EVALUATED; full_core_unlock=false.

WHAT_CHANGED: Added nested reciprocal-plane designs using the existing finite-q amplitude and energy-null test, three tests and a source-model artifact. No new physical equation or external dataset.

EQUATION_OR_MAPPING: Same A=S/f and c=f at each fixed q. Only reciprocal vectors G are added. The largest design includes 124 ideal G vectors with h,k in -2..2 and l in -2..2 excluding the origin. Populations must be the same across observations of that q.

VERIFICATION: Three tests check nested/unique rows, complementary versus duplicate observations and row-scale invariance. Basal source matrices reproduced; all source frequencies checked. Rank and energy conclusion stable over 1e-9 to 1e-11 relative singular thresholds. No negative gap clipped.

CONTROLLING_BLOCKER: experimentally_accessible_energy_sensitive_geometry_and_noise_contract.

NEXT_ACTION: Establish whether matched tilted/orientation-resolved measurements exist or can access a useful subset of these reciprocal planes. Use detector-specific covariance and energy-estimator variance to choose rows; full algebraic rank is not sufficient. In parallel, seek independent thermometry/energy balance rather than treating this design as the only route.

CLAIM_BOUNDARY: Ideal source-model measurement design, not acquired data, a validated experiment, unique minimum design, temperature, alpha or full Topic 13 closure. No fit or holdout. No claim that existing [001] images contain the added planes.

## Findings

| q | Rank with l=0 | Rank with l=0,+1 | Rank with l=-2..2 | Raw condition number of largest design |
| --- | ---: | ---: | ---: | ---: |
| (0.005,0,0) | 6 | 11 | 12 | 14688 |
| (0.02,0,0) | 6 | 11 | 12 | 3594 |
| (0.1,0,0) | 6 | 11 | 12 | 511 |
| (0.005,0.005,0) | 5 | 10 | 12 | 9263 |
| (0.02,0.02,0) | 5 | 10 | 12 | 2229 |
| (0.1,0.1,0) | 5 | 10 | 12 | 399 |

Adding l=-1 to l=0,+1 does not restore the remaining rank. The l=+-2 design
does, for these samples. This is not proof that those planes are necessary:
other directions, observables or justified constraints may suffice.

Condition numbers are for the unwhitened ideal response with omitted common
site factors. They warn of potentially strong noise sensitivity, especially
near Gamma; they are not measured uncertainty or the variance of an energy
estimator. Actual row factors and covariance must be included before comparing
experimental designs. The number of independent model equations is not the
number of independent measured pixels after symmetry averaging.

This result supplies a constructive route rather than another unexplained
blocker: complementary geometric information can remove this model's ambiguity.
Whether that route is practical is now a specific experimental/source question.

Evidence: `artifacts/t13_complementary_geometry_audit.json`, including complete
design grids, singular values, tolerance sweeps and source hashes.
