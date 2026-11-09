# Conditional Multi-Q Window And Route Decision Card

MAJOR_RESULT_CLOSURE: T13_MULTI_Q_ESTIMATOR_COVARIANCE_AND_TREE_BIAS_BUDGET; CLOSED_FOR_LANE method requirement, not a completed physical measurement design.

WHAT_IS_ACTUALLY_CLOSED: The finite-q bias versus decorrelated energy-shape sensitivity tradeoff is explicit for ten locked tree windows. Four admit a conservative energy-only sufficient budget for the illustrative 1% I target, six do not. One full-tree interpolant lies outside the positive inverse domain and is retained.

WHAT_REMAINS_OPEN: Physical q range, material/Noether current and action units, same-state native inputs, permissions/row identities, resolution kernel/peak estimator/ancestry, full joint covariance and theory remainder. Neither instrument feasibility nor a lower bound on necessary instrument precision has been established.

DEPENDENCY_UNLOCKED: Comparison of candidate acquisition routes and instrument feasibility research only, not G4/Goal/R1-R5/Core or physical Topic13.

STATUS: Derived conditional requirement. Source [artifact](t13_multi_q_estimator.json), SHA256 `56c9aa7ef469c51a30337bea9ea958c8d2459ed7e2316fbbe49644ad192c57b1`; [derivation](T13_MULTI_Q_ESTIMATOR_2026-10-03.md). No experimental rows or noise admitted.

WHAT_CHANGED: Replaces a vague request for better precision with a reproducible sufficient-bound calculation and a correlation-aware local sensitivity. It does not replace the prior measurement/source/alpha controllers or erase their failure.

EQUATION_OR_MAPPING: Estimate (c,eta,zeta) from q=(q_max,q_max/2,q_max/4), form r=c*zeta/eta^2, invert only within r0-D/s^2<r<r0 with known native inputs. Covariance uses the full nine-input gradient and Sigma_full; common multiplicative energy/q axes cancel exactly, decorrelated shape errors do not. q and energies below are natural-action controls, not physical metre/Joule measurement windows.

| mu | q_max | Tree-only I bias | Sufficient relative energy bound | Unit independent-energy L2 gain |
| --- | --- | --- | --- | --- |
| 1.05 | .04 | Outside inverse domain | Not certified | Undefined |
| 1.05 | .02 | 37.84% | Not certified | 1.066e10 |
| 1.05 | .01 | 8.011% | Not certified | 7.815e10 |
| 1.05 | .005 | 1.942% | Not certified | 1.101e12 |
| 1.05 | .0025 | .4821% | 1.654e-16 | 1.711e13 |
| 1.2 | .04 | 3.572% | Not certified | 4.780e8 |
| 1.2 | .02 | .8825% | Not certified | 7.255e9 |
| 1.2 | .01 | .2200% | 4.192e-14 | 1.146e11 |
| 1.2 | .005 | .05495% | 3.304e-15 | 1.828e12 |
| 1.2 | .0025 | .01374% | 2.172e-16 | 2.922e13 |

The gain is sqrt(sum of squared log-energy derivatives)/I_hat, a unit-covariance sensitivity control, not actual instrument variance. The bound is sufficient, worst-case and energy-only: exact q/fixed native inputs/tree approximation. The 1% target is illustrative, not a physical pass rule. The mu1.2/.02 case shows why an uncertified conservative box is not a no-go: its numerical tree bias is already below 1% while the bound cannot certify that window.

At small q the omitted O(q^7) term typically biases the estimated quintic coefficient by O(q_max^2), but differencing energies to extract it amplifies shape errors approximately as q_max^-4 at fixed node ratios. Thus simply reducing q is not a free path to physical accuracy. The observed tiny sufficient bounds warrant a route comparison, not a claim that every apparatus is impossible. No optimum over node placement, correlated fitting, other estimators or all native parameters was proved.

## Input Packet Required For A Decisive Route Comparison

1. Same-state particle-current and action normalization with native r0/D/s and joint uncertainty, not the existing 1.7K calibration silently transferred to a low-T branch.
2. Permitted low-q energy rows with source locator, units, state/temperature/pressure, row identity, preprocessing and hash. No Xie 2026 acquisition/calibration.
3. Detector-to-peak response with resolution kernel, wavelength/momentum calibration, peak bias and covariance across the three observations. Raw detector noise is not automatically an unbiased energy error.
4. Independent scale U/current/EOS input for the alternative q3 route, its provenance and sensitivity. The earlier conditional inverse does not itself supply physical U.
5. Controlled interaction/finite-T/native-state remainder and how it enters bias/covariance, separately from numerical convergence.

VERIFICATION: Every locked window is retained; rational certificates and independent estimator/differential controls are in the linked artifact/tests. No acquired resolution, Gaussian error bar, diagonal independence, thermal width or external comparison is substituted. Source/protected hashes preserve the predecessor and old failure identities; original causal gate unchanged. Full linked test result belongs in UPDATE_LOG, not an invented physical success percentage.

CONTROLLING_BLOCKER: physical_peak_resolution_joint_covariance_native_state_and_interaction_error_not_admitted.

NEXT_ACTION: By the existing 5 October decision window, compare q5 extraction versus independent-scale/q3 using only documented input. Prefer the route whose information/uncertainty is actually supported, not the one with more PASS checks. If neither can be admitted, freeze the conditional structural/methods result on 7 October and make a review-ready preliminary portfolio by 11 October; this does not satisfy G2-G4 automatically. By 8 November R2/R3, obtain an input-backed feasibility decision or name the exact acquisition to fund. Continue the original 25 October/22 November/6 December/20 December reviews; do not invent a confirmed next call. No external contact, purchase or submission is authorized by this card.

CLAIM_BOUNDARY: Non-empirical acquisition requirement, not actual detector precision, optimal design, physical no-go, alpha_Phi_K, Kubo/SK-KMS, complete thermal bridge or Full Topic13/Core/Goal closure. New evidence does not promote source-work FAIL or Core-owner composition. Holdout remains prohibited; prior exposure REVIEW_REQUIRED; ontology and model trial/settings unchanged. Funder, PI/institution, cash budget and actual deadline remain unknown, so review-ready is not submission-ready.
