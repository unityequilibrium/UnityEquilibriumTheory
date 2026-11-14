# Topic 10-13: He-II fixed-constraint EOS source candidate

Date: 2026-09-30. Role: SOURCE_CANDIDATE_NOT_ADMITTED_MATERIAL_EOS.
Overall controller: vector_momentum_constitutive_origin_and_material_frame_admission_open.
Source controller: he4_fixed_constraint_EOS_source_found_but_covariance_entropy_anchor_and_independence_open.

## Provenance and scope

[Source package](Data/03_Research/he4_tn1334_fixed_constraint_eos_source_candidate.json)
preserves three liquid-row raw tokens from the September 1998 revised
[NIST TN1334](https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote1334.pdf),
Appendix A printed pages 14-15 (PDF pages 20-21). Full rendered pages and derivative
definitions on printed page 4 were inspected. The following row at each temperature
is vapor and must not be substituted. The source PDF SHA256 is recorded; the temporary
review PDF is not redistributed or an offline-verifier dependency.

The source tables are calculated from a fitted EOS. These equilibrium states lie
on SVP, but the derivative columns have separately specified held variables.
They therefore fill part of the fixed-constraint source gap; they do not turn SVP
path derivatives into a complete independent material EOS.

## F0-F4: quantities, constraints and SI conversions before code

Use material T, rho, specific entropy s, c_p, c_v, alpha_p and kappa_T as
standard thermodynamic quantities. No C=rho, Phi=T/phase, Q=entropy current,
R=independent reservoir or e0=full internal energy is assigned.

- Density is already kg/m^3. Pressure MPa to Pa multiplies by 1e6.
- Entropy and specific heats J/(g K) to J/(kg K) multiply by 1000.
- The expansivity column is alpha_p*T; divide by T for alpha_p in 1/K.
- The compressibility column is P*kappa_T; divide by P in Pa for kappa_T in 1/Pa.
- The source phi denotes the dimensionless Gruneisen coefficient, not UET Phi.
- Blank ordinary transport entries stay null. The nonlinear counterflow
  conductivity of Section 5.3 is not a replacement for linear conductivity.

The selected temperatures 1.650, 1.700 and 1.750 K lie on the He-II EOS branch
below the source overlap boundary T_A. That limited branch check is not a universal
phase classifier. EPT-76/ITS-90 consistency is a source statement with uncertainty,
not an exact temperature-scale identity with Topic 13.

## Locked printing-compatibility diagnostic

Before the first audit, each raw token is assigned a symmetric interval of half
its last printed decimal unit, including T. This is an explicitly assumed
printing diagnostic, not a physical uncertainty, standard deviation or covariance.
Check closed-interval overlap for the three standard identities:

~~~text
c_p-c_v = T alpha_p^2/(rho kappa_T)
c_adiabatic^2 = c_p/(c_v rho kappa_T)
Gamma_Gruneisen = alpha_p/(rho c_v kappa_T)
~~~

Use endpoint extrema with no probabilistic independence assumption. Keep failures
and do not alter tokens or tolerances to force compatibility. Negative controls
must expose pressure conversion, undivided alpha*T, undivided P*kappa, vapor
substitution and blank-as-zero errors. Passing only establishes source transcription
and this declared compatibility diagnostic. No acoustic UET eigenvalue is computed.

## Independence and unresolved material admission

[Arp 1990](https://link.springer.com/article/10.1007/BF00683459) fits sound as well
as thermodynamic data and cites Maynard and Tam-Ahlers. Exact fitted-row overlap
requires full source reconstruction; the bibliography alone does not prove it.
TN1334's superfluid fraction is sound-derived, and its second/fourth sound speeds
are calculated from two-fluid theory. Those values are not independent targets.

[NIST IR8474 (2023)](https://nvlpubs.nist.gov/nistpubs/ir/2023/NIST.IR.8474.pdf)
excludes He-II and is screened out. The older
[NBS1029](https://nvlpubs.nist.gov/nistpubs/Legacy/TN/nbstechnicalnote1029.pdf)
supplies an archive/code lead using fitted Brooks-Donnelly inputs and T58; it is
not a modern independent response dataset. Maynard's official
[abstract](https://journals.aps.org/prb/abstract/10.1103/PhysRevB.14.3868) explicitly
converts measured first/second/fourth sound through two-fluid equations to
thermodynamic quantities. Full Arp coefficients and Maynard experimental protocol
were not acquired.

Per-row uncertainty/covariance, the selected edition's absolute entropy anchor,
exact EOS/response ancestry and a primary frequency/geometry/state-matched response
protocol remain unresolved. The source's global density uncertainty estimate is
not assigned to every derived quantity. Do not import the WebBook/REFPROP entropy
reference into this edition without evidence.

The [original material requirements](Data/03_Research/he4_two_fluid_thermodynamic_input_requirements.json)
remain unassigned and unchanged. A physical Core-to-material Legendre/state/SI map
and superfluid phase/stiffness/response mapping, plus dissipative closure, remain
required. J05/J06, Core/Topic 13 gates and frozen matching constants are unchanged.
