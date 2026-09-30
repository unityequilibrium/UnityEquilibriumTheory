# Topic 13: thermal-pole measurement design control (2026-09-27)

MAJOR_RESULT_CLOSURE: `T13_CATTANEO_POLE_MEASUREMENT_DESIGN_CONTROL` is `CLOSED_FOR_LANE` as a standard comparator only. The planned `T13_HE4_PREDICTIVE_CONTENT_AND_MEASUREMENT_DESIGN` is not closed.

WHAT_IS_ACTUALLY_CLOSED: In the declared linear Cattaneo class, a single oscillation frequency does not identify the relaxation time and conductivity, even with a known heat capacity and wave number. An underdamped pole pair's oscillation frequency **and** decay rate identify both locally when the wave number and volumetric heat capacity are independent inputs. Two positive, stable synthetic coefficient pairs explicitly witness the frequency-only ambiguity. This is a measurement-design calculation, not a new He-II result.

WHAT_REMAINS_OPEN: A UET He-II two-fluid/finite-temperature response operator, matched source and detector protocols, independently measured heat capacity and mode geometry, physical coefficient provenance and joint covariance. Existing conservative-action transport underdetermination is not removed.

DEPENDENCY_UNLOCKED: None. Neither Full Topic 13 nor Core/Gravity is unlocked.

STATUS: `ANALYTIC_AND_SYNTHETIC_CONTROL_PASS`; physical response remains `BLOCKED`.

WHAT_CHANGED: Added a topic-owned reproducible inversion audit and four focused tests. No Core equation or existing calibration was modified; no Xie 2026 data were accessed.

EQUATION_OR_MAPPING: For `c d_t(theta)+d_x(j)=0` and `tau d_t(j)+j=-kappa d_x(theta)`, a Fourier mode has `tau s^2+s+(kappa/c)q^2=0`. In the underdamped regime `s=-gamma +/- i omega`, so `tau=1/(2 gamma)`, `D=tau(omega^2+gamma^2)/q^2`, `kappa=c D`. Holding `omega,q,c` fixed while varying positive `tau` gives a continuous family of distinct positive `kappa`; decay rate distinguishes them. The periodic/no-flux quadratic stability functional `V=integral[c theta^2/2+tau j^2/(2 kappa)]dx` obeys `dV/dt=-integral j^2/kappa dx`. Its density is `J K/m^3`, **not** physical SI energy density; this is not the UET energy ledger or entropy current.

VERIFICATION: Four focused tests pass, including pole inversion, two distinct stable witnesses at the same frequency, mode-wise quadratic balance, and first-order independent-input uncertainty checked against central finite differences. Synthetic witnesses use `omega=100 s^-1`, `q=1000 m^-1`, `c=1000 J/(m^3 K)`; `tau=0.01 s` gives `kappa=0.125 W/(m K)`, `gamma=50 s^-1`, whereas `tau=0.04 s` gives `kappa=0.40625 W/(m K)`, `gamma=12.5 s^-1`. Assumed independent 5% frequency, 5% decay, 1% wave-number and 5% heat-capacity standard uncertainties give about 10.10% first-order conductivity uncertainty for the first witness; this is an illustrative error budget, not a source uncertainty. Clean-base machine-readable artifact SHA-256: `cbaaae67cf8c0ca12ced5ca44f2a4521cc3c6105e772133d19886311db1da369`.

CONTROLLING_BLOCKER: `admitted_UET_HeII_two_fluid_response_operator`. The comparator's poles cannot be identified with second-sound poles without a derived physical operator and matching input/readout map.

NEXT_ACTION: Freeze the He-4 calibration/protocol and classify the accepted UET linearized state and observable operator. Either derive the two-fluid pole and its coefficient origins or record a scoped proof that the current admitted state cannot generate it. Then design a same-state measurement of mode frequency, attenuation, geometry and independent calorimetry with covariance. If only speed is available, do not report a unique transport coefficient.

CLAIM_BOUNDARY: This result extends the existing conservative-action transport non-identifiability audit with an explicit standard-comparator inverse measurement design. It does not demonstrate UET predictive content, He-II second sound, physical transport, TTG validation, or Full Topic 13 closure. The result applies only to one underdamped linear Cattaneo mode with a correctly separated source/detector response; it is not a continuum theorem about all UET extensions.

Evidence: [machine-readable artifact](t13_thermal_pole_measurement_design_control.json), [audit source](../../Code/03_Research/Research_T13_Thermal_Pole_Measurement_Design.py), [regression tests](../../Code/03_Research/test_t13_thermal_pole_measurement_design.py), and the pre-existing [transport underdetermination module](../../../../core/03_lanes/thermal/uet_transport_coefficient_identifiability.py).
