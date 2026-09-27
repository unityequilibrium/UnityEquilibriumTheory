# He-4 independent-measurement source route screen

MAJOR_RESULT_CLOSURE: `T13_HE4_INDEPENDENT_MEASUREMENT_ROUTE_SCREEN` is `PARTIAL`; source-family triage only.

WHAT_IS_ACTUALLY_CLOSED: J02 recommended Table 4.3, Heiserman key 1 and Tam-Ahlers key 3 cannot be treated as clean independent tests of the present sound-derived calibration. The compilation identifies Wang-Wagner-Donnelly key 5 as a separately named response study, while Dash-Taylor offers a non-sound normal-density method. Both are acquisition routes, not admitted datasets.

WHAT_REMAINS_OPEN: Wang primary protocol/rows/row-level uncertainty/covariance and scale, Dash numeric calibration rows/uncertainty and temperature conversion, source permissions, and an admitted UET two-fluid response operator.

DEPENDENCY_UNLOCKED: None; G0 and Full Topic 13 remain blocked.

STATUS: `PASS_SOURCE_FAMILY_ROUTE_TRIAGE_ONLY`; `numeric_response_rows_admitted=0`.

WHAT_CHANGED: Replaced a vague instruction to find an independent source with two named routes and explicit rejection reasons for the overlapping studies. No measurement, fit, Core equation or physical threshold changed.

EQUATION_OR_MAPPING: The present `alpha_Phi_K` depends on the slope of the superfluid fraction near 1.7 K; measuring second-sound velocity in m/s is a different observable requiring a two-fluid state/operator. A different study key alone is insufficient to prove independence.

VERIFICATION: [NIST Donnelly-Barenghi Section 2 Table 2.1](https://srd.nist.gov/jpcrdreprint/1.556028.pdf) marks calibration-window rows with Maynard/Tam-Ahlers keys 2/3; Section 4 Table 4.1 identifies second-sound key 1 (Heiserman), key 3 (Tam-Ahlers), and key 5 (Wang-Wagner-Donnelly). The [Heiserman primary abstract](https://link.aps.org/doi/10.1103/PhysRevB.14.3862) reports simultaneous sound measurements and lists Maynard as a coauthor; the [Maynard companion abstract](https://link.aps.org/doi/10.1103/PhysRevB.14.3868) says sound data were converted to thermodynamic quantities. The [Dash-Taylor primary abstract](https://journals.aps.org/pr/abstract/10.1103/PhysRev.105.7) describes oscillating-disk normal-density measurements from 1.2 K to the lambda point. Wang's primary full text was not verified; Table 4.1 prints study-level uncertainty as 0.07%, not row-level covariance. Local source hashes are in the [machine screen](t13_he4_independent_measurement_route_screen.json). No Xie 2026 data were read.

CONTROLLING_BLOCKER: `primary_Wang_protocol_row_uncertainty_and_ancestry_not_verified` for a separate response source. The UET operator and G0 are separate blockers.

NEXT_ACTION: Acquire/inspect Wang's primary measurement protocol and permissible numeric rows, verify shared calibration/temperature standards and uncertainties; in parallel check whether Dash-Taylor supplies usable numeric normal-density rows and modern temperature-scale conversion. If neither route clears admission, keep the two-week output as identifiability and measurement design, not independent validation.

CLAIM_BOUNDARY: This narrows the search; it does not prove that Wang data are statistically independent, that Dash values can replace the present calibration, or that UET predicts second sound. No result is fitted or promoted.
