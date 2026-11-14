# Conditional Density-Spectroscopy Measurement Card

MAJOR_RESULT_CLOSURE: Derived information-gap component CLOSED_FOR_LANE;
the physical measurement design and material prediction remain OPEN.

WHAT_IS_ACTUALLY_CLOSED: Same-action tree density operator and restricted
gain/unit information analysis identify specific independent inputs that
would remove two constructive ambiguities. Not a full measurement theorem.

WHAT_REMAINS_OPEN: Noether-to-atomic-current map, matched state/action
normalization, permitted numeric rows, independent instrument inputs,
joint covariance, practical feasibility and theoretical remainder.

DEPENDENCY_UNLOCKED: One conditional low-temperature He4 density-spectrum
protocol investigation only; not thermal transport or physical/Core gates.

STATUS: CONDITIONAL_DENSITY_SPECTROSCOPY_ROUTE_NOT_ADMITTED.

WHAT_CHANGED: Operator-derived requirements replace treating raw Phi
poles or instrumental peak width as directly measured thermal dynamics.

EQUATION_OR_MAPPING: Conditional I=G_inst*Z_N^2*(R convolve S_Noether),
after independently declaring kinematics, state and units. Tree chi_nn
is fixed by the [derivation](T13_NOETHER_DENSITY_READOUT_2026-10-03.md).

VERIFICATION: Linked artifact has ten passing internal scientific checks;
zero experimental rows admitted. Independent-scale constructive inverse
and central log-gradient differences checked, not a real calibration.

CONTROLLING_BLOCKER: Noether_to_atomic_density_SI_state_resolution_and_independent_gain_not_admitted.

NEXT_ACTION: Verify one same-state particle-current/unit map and primary
low-q data ancestry/rights; acquire independent resolution/gain covariance
before any comparison. Also derive/check whether an independent q5
coefficient could lift the restricted q3 unit family, with approximation
control; that calculation is not completed here. No external contact or
purchase authorized here.

CLAIM_BOUNDARY: Neither acquired data nor physical prediction; no TTG,
second-sound, Phi-to-Kelvin, physical linewidth/Kubo or full KMS claim.
Existing1.7K calibration cannot silently be transferred to this low-T route.
Prior Xie context exposure remains REVIEW_REQUIRED; no numeric holdout read.

## Candidate Protocol And Source Boundaries

[Beauvois et al.](https://arxiv.org/html/1802.08120v3), DOI
10.1103/PhysRevB.97.184520, Sections II-III/IV.2 and Figure5, documents
IN5 time-of-flight density spectra below100mK, including SVP, with cell and
multiple-scattering corrections. Resolution depends on energy and wavevector;
SVP spectra reuse earlier-study data. Thus a separate paper is not evidence
of independent source ancestry, and observed width is not intrinsic damping.

[NIST Copley](https://www.ncnr.nist.gov/summerschool/ss13/pdf/SS2013_Lecture_Copley.pdf),
slides27-30/41, supplies standard cross-section/structure-factor and
coherent-channel guidance, not a UET coefficient or temperature calibration.
The [screen](../../Data/03_Research/t13_density_spectroscopy_protocol_screen.json)
records locators, roles, unknown rights/covariance and zero numeric rows.
No digitized curve, raw-data hash, instrument budget or lab access invented.

## Inputs That Must Be Kept Separate

| Input | What it identifies | Current admission |
| --- | --- | --- |
| Noether-to-He4 number current, state and unit map | Which physical density the derived operator could describe | OPEN; C is not charge/mass |
| Independent flux/efficiency/sample normalization and gain covariance | Removes restricted G_inst/Z_N amplitude ambiguity | NOT ACQUIRED |
| Joint R(Q,E;Q',E') and background/multiple-scattering covariance | Relates theoretical response to observed spectrum | NOT ACQUIRED; no width assignment |
| Independent volumetric action scale U with action normalization | Removes retained-q^3 kinetic/unit family when other native inputs are known | NOT ADMITTED |
| Primary low-q numeric rows, rights, row identity, uncertainty and ancestry | Permits calibration/comparison separation | ZERO ROWS; independence and validity overlap unknown |
| Controlled q^5 and interaction/finite-T remainder | Determines a trustworthy low-q inference window | OPEN; no fit-selected window |
| Independent thermal observable/map | Relates this response to requested temperature/heat question | OPEN; density measurement alone does not provide alpha_Phi_K |

## Information And Uncertainty Contract

With all other input/convolution conventions fixed and a nonzero known
S_N, intensity alone has log Jacobian (1,2) for (G_inst,Z_N): rank1.
An independent gain row (1,0) raises it to2. Conditional positive inverse
Z_N=sqrt(I/(G_inst*S_N)); background and source covariance still matter.
A normalized peak position carries no absolute gain or Phi/Kelvin scale.

For physical dispersion E(Q)=A_Q Q+B_Q Q^3+..., natural sound c,
eta=eta_base*(1+s I), and declared U=E_unit*Q_unit^3:

```text
eta = B_Q*c^(3/2)*U^(1/2)*A_Q^(-3/2)
I = (eta/eta_base-1)/s
r = eta/eta_base
log-input order = (A_Q,B_Q,U,c,eta_base,s)
g = (-1.5*r/s, r/s, .5*r/s, 1.5*r/s, -r/s, -I)
Var(I) = g^T*Sigma_log*g + separately controlled theory remainder
```

Logs denote ratios to declared references. Full covariance must be used;
do not assume independent errors or invent laboratory precision. The
fixed constructive ratios1.01/1.02 are not experimental unit calibration.
Independent U could come from an admitted nonzero thermodynamic difference
only after the same-state action/pressure normalization is demonstrated;
zero SVP pressure or an arbitrary additive vacuum pressure cannot anchor it.
No scale from another Core-owner lane is imported without that mapping.

The formula identifies one retained invariant under its restricted input
class, not all thermal transport. Acceptable next outcomes are a genuine
independent input package, a documented infeasible protocol or an explicit
unresolved requirement. Missing access alone is not a physical no-go.

## Evidence And Delivery

Artifact SHA-256:
`2b6688dab3cb55c623fa5c1a43320ef28d65fe82e95b27d6ea1731f9c632ac12`.
This card extends, rather than replaces, the earlier
[native-input phase-EFT card](T13_LOW_T_PHASE_EFT_MEASUREMENT_CARD_2026-10-02.md).
The demonstrated sufficient U route is not the only possible input route:
higher-order dispersion might add information, but its rank/conditioning
and trustworthy physical inference window must be calculated first.
The original7 October scientific freeze/11 October portfolio review and
R1-R5/full Goal requirements remain. A conditional card is not G4 acceptance,
external validation, funding eligibility or full measurement-design closure.
