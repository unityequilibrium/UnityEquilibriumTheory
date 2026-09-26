# He-4 second-sound response protocol card (J02)

**Status:** response-source candidate identified; primary frequency-specific protocol and UET operator remain open. This card is a research protocol, not a new Core gate or physical claim.

## Question and purpose

With the existing He-4 normalization constants held fixed, can a separately measured dynamic response be derived from an admitted UET state and reproduce the second-sound phase velocity of liquid He-II? This is a useful bridge to Topic 10 because the observable is a propagating thermal/entropy wave, while Topic 10 currently has no admitted two-fluid dynamic state.

## Frozen reference interface

| Quantity | Frozen value | Existing record |
| --- | ---: | --- |
| alpha_Phi_K | -1.02237987858849 K per normalized base Phi | Topic 13 response-calibration audit |
| theta_T | 7.727272727272727 K per natural temperature | Topic 13 response-calibration audit |
| Z_Phi | -0.017488421860832278 ± 0.0009712263618290997 | Topic 13 response-calibration audit |
| e0 | 512994.17164886114 ± 60.608920908635206 J m^-3 | Topic 13 SI beta audit |
| eta_normal | (1.29 ± 0.05) × 10^-6 Pa s | external normal-component shear input; not a UET prediction |

These values may not be recalibrated or rematched on second-sound rows. Their source bounds remain conservative bounds, not standard deviations; covariance is unavailable.

## Source candidate and measurement

Donnelly and Barenghi’s 1998 reference review reports recommended second-sound phase speeds along the saturated-vapor-pressure line in Table 4.3. It gives u2 = 20.33 m s^-1 at T90 = 1.700 K, with local recommended values 20.37 m s^-1 at 1.650 K and 20.18 m s^-1 at 1.750 K. The finite difference across the outer rows is -1.9 m s^-1 K^-1. It is derived from rounded recommended values and has no row-level covariance or uncertainty attached, so it is a protocol diagnostic only.

The table summarizes resonance measurements. The recommended rows do not identify a specific drive frequency, mode geometry, row-wise uncertainty or response covariance. Table 4.1 lists a 0.07–0.75% range across contributing studies, but that range cannot be assigned to each Table 4.3 value. No numeric pass threshold is set.

Lane, Fairbank and Fairbank’s 1947 resonance paper reports a maximum of 20.46 m s^-1 near 1.7 K and accuracy of at least ±0.5%. Its abstract does not establish pressure-path and temperature-scale correspondence to the 1998 T90/SVP recommendation, so it is retained as a protocol cross-check rather than combined or scored against the table.

The source values were inspected while designing this protocol. They were not used to construct alpha, Z, theta_T or e0 and have not been used for fitting, but this is no longer a blind holdout. Use a separately selected source or future experiment for any claim of blind validation.

## State and comparison contract

The reference state is liquid He-4, He-II, on the T90 saturated-vapour-pressure path around 1.70 K. A temperature derivative along that path is not the fixed-(T, mu) action derivative used by the existing natural response construction. The recommended table does not settle the wave’s local perturbation constraints, exact resonance frequency, geometry or mean-flow condition; those must be obtained from the selected primary record before comparison.

The target is the real phase speed u2 = omega/k of a full-He-II collective thermal/entropy-wave mode. It is not normal-component velocity, first sound, shear viscosity, bulk heat conductivity or a generic incompressible Navier–Stokes velocity. Attenuation should remain a separate observable because multiple two-fluid dissipative processes can contribute; the source-locked normal shear coefficient alone does not specify it.

A future candidate must derive the complex mode frequency by linearizing an admitted two-fluid state around the matched equilibrium state, then compare the real phase speed without fitting. The state must expose the required mass/entropy/temperature and relative normal–superfluid motion, with its ontology, units, source terms and boundaries admitted through Core F0–F8. A reference two-fluid comparator must use the same state and thermodynamic inputs. Propagate source, parameter and numerical bounds without assuming independence. Do not run or score a UET prediction until the exact primary measurement protocol and row uncertainty are source-locked.

## Topic 10 and OpenAI relationship

The current Topic 10 scalar C/I evolution and scalar-gradient velocity mapping cannot predict this two-fluid eigenmode. The J01 no-go applies only to nonzero periodic incompressible vortical targets under that legacy map; it does not imply a second-sound no-go for all UET models. OpenAI’s Navier–Stokes result helps formalize theorem scope, norms and residual obligations for a later incompressible normal-flow subproblem. It supplies no He-II mode equation, transport coefficient, source data or direct validation for second sound.

## Current blockers

- No admitted UET two-fluid second-sound operator or coupled relative-velocity/entropy state.
- No primary source row with matched pressure path, temperature scale, frequency/mode protocol and row-level uncertainty.
- The response candidate has been viewed during protocol design and cannot be described as a blind holdout.

**Claim boundary:** source/protocol candidate only. No UET prediction, independent action-to-material validation, blind holdout result, Core admission, or dependency unlock is recorded.

## Source records

- Donnelly and Barenghi, *The Observed Properties of Liquid Helium at the Saturated Vapor Pressure*, DOI 10.1063/1.556028, Tables 4.1 and 4.3: https://srd.nist.gov/jpcrdreprint/1.556028.pdf
- Lane, Fairbank and Fairbank, *Second Sound in Liquid Helium II*, DOI 10.1103/PhysRev.71.600: https://journals.aps.org/pr/abstract/10.1103/PhysRev.71.600
- Machine-readable source package: Data/03_Research/he4_svp_second_sound_response_source_package.json