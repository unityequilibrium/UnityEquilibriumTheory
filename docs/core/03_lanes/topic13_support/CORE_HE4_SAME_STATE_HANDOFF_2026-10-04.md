# Core He-4 same-state correspondence handoff

MAJOR_RESULT_CLOSURE: No new physical closure. One input/mapping gap is made explicit.

WHAT_IS_ACTUALLY_CLOSED: Reconstructable comparison of the existing 1.7 K calibration and the separate low-temperature response branch, with input hashes and a conditional charge/measure conversion. [Machine-readable handoff](../../07_artifacts/topic13/core_he4_same_state_correspondence_2026_10_04.json).

WHAT_REMAINS_OPEN: Same-state atomic current, chemical-potential convention, spacetime/action normalization, thermodynamic path correspondence and controlled interaction/finite-T remainder.

DEPENDENCY_UNLOCKED: Input acquisition and a Core correspondence decision only. Physical transfer, full Topic13, GR and foundation gates stay open.

STATUS: `SPECIFIC_ADDITIONAL_INPUTS_REQUIRED`; organization registration `REVIEW_REQUIRED`; internal correspondence audit, no physical promotion.

WHAT_CHANGED: Added an opt-in audit generator and this handoff. Existing Core calibration/artifacts/equations and Topic13 files are not edited.

EQUATION_OR_MAPPING:

| Contract | Existing Core anchor | Low-temperature source/response |
| --- | --- | --- |
| Material/state | He II at 1.7 K SVP externally; natural action anchor is normal at T=.22, mu=.35, Phi=.15 | Condensed tree states mu=1.05/1.2, xi=h=0; their Phi is stationary and branch-specific; primary low-T source documents T<100 mK, hybrid rows require component-specific temperature/ancestry |
| Pressure/density | SVP path, rho=145.268639453 kg/m3, n_atom=2.185648035e28 /m3; absolute pressure not locked here | Seven source pressures; SVP hybrid has mixed ancestry; same-state density not admitted |
| Source | Donnelly-Barenghi DOI10.1063/1.556028 and declared evaluated-property snapshot | Godfrin arXiv2012.09067v1 author archive; journal-version parity not established |
| Response map | DeltaPhi_norm=Delta(rho_s/rho)/(rho_s/rho)_0; alpha=-1.022379879 K; theta_T=7.727272727 K/natural T; Z_Phi=-.01748842186 | No same-state atomic/readout gain or Kelvin map supplied by dispersion |
| Energy map | e0=n_atom*k_B*T0=512994.17165 J/m3 is a declared scale convention | No admitted transfer of e0 or 1.7K constants |
| Ensemble | External equilibrium derivative along SVP; action derivative at fixed(mu,Phi) | New tree/phase approximation; finite-T/interaction remainder still open |

The response reconstruction theta_T*alpha_natural/Z_Phi=alpha_external follows from how Z_Phi was constructed. It is not a further independent response observation. The external input is independent of UET target fitting; its measurement ancestry and use for calibration still constrain independence claims.

Chemical potential requires an explicit convention: viscosity's delta_mu=0 is relative to an SVP reference, whereas action mu controls its charged phase. Under the **conditional** linear maps mu_phys=E_unit*mu_nat+constant and p_phys=e0*p_nat+constant, differentiation gives n_Q_phys=(e0/E_unit)*n_Q_nat. With E_unit=k_B*theta_T this is 4.808425678e27 /m3 per natural charge unit. The normal anchor would correspond to approximately .00010717 of the external atomic density. This diagnoses an unproved identification; a normal-component effective description remains possible. State-dependent offsets or scale choices need their own chain rule.

The radial natural momentum measure is k^2 dk/(2*pi^2). For a declared speed scale c_star and energy unit E_unit, ell=hbar*c_star/E_unit, and an action coefficient A gives e0=A*E_unit/ell^3. Neither c_star/ell nor A is fixed by a scalar Phi rescaling. Thus converting source meV and inverse angstrom to the natural dispersion needs independent spacetime/current normalization.

VERIFICATION: Generator checks current input identity and reconstructs the matching identity; no old model solve, source fit or Xie numeric access. Run `py -3.14 docs/scripts/core/audit/audit_he4_same_state_correspondence.py --topic13-root <declared checkout> --check` from repo root. Exact command/input identities and results are in the Core ledger entry; saved JSON is the result source.

CONTROLLING_BLOCKER: `same_state_atomic_current_action_measure_and_low_T_remainder_not_admitted`.

NEXT_ACTION: Choose one material state, then obtain (1) its T/P/density with covariance, (2) atomic charge/current assignment and mu reference, (3) independent energy/length/time/action scale, (4) SVP-to-fixed-variable path Jacobian, and (5) a same-state pressure/compressibility/current observable not used to construct matching plus a remainder bound. Core supplies this correspondence; Topic13 supplies data sufficiency/omitted-term/covariance. A source-backed absence of these inputs is a valid acquisition-gap result. Do not transfer T<100mK rows to 1.7K or select an exposed curve for target agreement.

CLAIM_BOUNDARY: Outcome is a specific additional-input requirement. Existing bounded CLOSED_FOR_CORE composition is preserved; this audit does not establish a microscopic He-II bridge, global no-go or independent empirical validation. Scientific statuses and old failures are unchanged. ORG must register the new audit/handoff as opt-in source support.
