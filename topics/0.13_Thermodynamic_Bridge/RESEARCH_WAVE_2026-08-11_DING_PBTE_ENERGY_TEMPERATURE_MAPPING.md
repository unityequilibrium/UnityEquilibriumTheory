# Topic 13 Ding PBTE Energy-Temperature Mapping Wave

MAJOR_RESULT_CLOSURE:
`T13_DING_PBTE_ENERGY_TEMPERATURE_MAPPING` is `CLOSED_FOR_LANE`.

WHAT_IS_ACTUALLY_CLOSED:
The official Ding 2022 Supplementary Information is archived with matching PMC MD5 and local SHA-256. Its PBTE derivation directly source-locks the standard linear-response map from mode-summed deviational phonon energy density to the source temperature response, and its ballistic section locates the TTG peak-to-null temperature-difference observable. The source heat-capacity symbol is renamed `C_src` in UET records so it cannot be confused with the UET collective coordinate `C`.

WHAT_REMAINS_OPEN:
No numeric `C_src(T)` row or uncertainty is supplied by this package. Mode-resolved `c_mu`, unit-cell volume, or a reproducible first-principles input/output package must still be acquired. The UET scale `e0`, base `Phi -> Delta_u_ph`, independent `alpha_Phi_K`, EOS, transport, SK/KMS, entropy current, and dissipative balance remain open.

DEPENDENCY_UNLOCKED:
The standard Ding PBTE formula lane and the correct non-circular route for acquiring `C_src(T)` are unlocked. Core curved 3+1, Gravity, full transport, and external claims remain blocked.

STATUS:
`PASS_SOURCE_FORMULA_MAPPING_NUMERIC_C_OPEN`; Full Topic 13 remains `PARTIAL / BLOCKED_OPEN_T13_FULL_BRIDGE`.

WHAT_CHANGED:
Added a provenance package for the official Supplementary PDF, a deterministic source/formula/unit verifier, energy-branch and full-gate integration, a major-result register entry, and focused regression tests. The Georgia Tech porous-grade property route remains preserved as a scoped no-go and is no longer the preferred numeric `C_src` route for Ding TTG.

EQUATION_OR_MAPPING:
Source PBTE mapping:

```text
Delta_u_ph = sum_mu(g_mu)
Delta_Tq = Delta_u_ph / C_src
y_TTG = Delta_Tq(t) / Delta_Tq(0)
```

Conditional named UET energy-response branch:

```text
Phi_E = Delta_u_ph / e0
Delta_Tq = (e0 / C_src) Phi_E
alpha_Phi_E_K = e0 / C_src
```

`C_src` has units `J m^-3 K^-1` and is not UET `C`. `Phi_E` is not identified with base `Phi`.

VERIFICATION:
The verifier checks PDF size, SHA-256, official metadata MD5, DOI/PMC identity, CC BY license record, Eq. S4 and S10 locators, dimensional closure to kelvin, ontology separation, material non-pooling, absence of fabricated numeric `C_src` or alpha, and non-access of Xie 2026.

CONTROLLING_BLOCKER:
`ding_pbte_numeric_C_src_and_uet_energy_anchor_missing`

NEXT_ACTION:
Package or reproducibly regenerate Ding-compatible `C_src(T)=sum_mu(c_mu)` with unit-cell volume and convergence/uncertainty, then derive `e0` and base `Phi -> Delta_u_ph` independently of TTG target residuals and Xie 2026.

CLAIM_BOUNDARY:
This wave closes a source-backed standard PBTE formula lane only. It is not a numeric heat-capacity calibration, base-`Phi` derivation, TTG prediction, external validation, Full Topic 13 closure, or global UET closure.
