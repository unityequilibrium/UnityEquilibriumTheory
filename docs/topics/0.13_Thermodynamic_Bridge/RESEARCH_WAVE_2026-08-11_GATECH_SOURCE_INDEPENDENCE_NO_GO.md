# Topic 13 Georgia Tech Source-Independence No-Go Wave

MAJOR_RESULT_CLOSURE: `CLOSED_FOR_LANE`

WHAT_IS_ACTUALLY_CLOSED: The Georgia Tech workbook route cannot independently recover density from `k/(D c_p)` or volumetric heat capacity from `k/D`. The publisher defines conductivity from measured diffusivity, measured/interpolated `c_p`, and an assumed density, so both inverse expressions reproduce the assumed input.

WHAT_REMAINS_OPEN: A permitted direct volumetric `c_v` source or independently measured same-grade density with uncertainty; same-regime `alpha_V` and `K_T`; material correspondence to the TTG lane; `e0`; base `Phi -> Phi_E`; independent `alpha_Phi_K`; and downstream EOS/transport/KMS/entropy closure.

DEPENDENCY_UNLOCKED: The circular same-workbook inversion route is rejected. Topic 13 may proceed to an independent direct-`c_v` or same-grade density/thermoelastic source-acquisition wave. No Core, Gravity, transport, or Galaxy dependency is unlocked.

STATUS: `PASS_SCOPED_SOURCE_INDEPENDENCE_NO_GO`; Full Topic 13 remains `BLOCKED_OPEN_T13_FULL_BRIDGE / PARTIAL`.

WHAT_CHANGED: The source package now distinguishes publisher preprocessing from local preprocessing and classifies each property as measured, source-interpolated, assumed, or derived. A deterministic no-go audit, gate integration, major-result register entry, runner, and focused regression tests were added.

EQUATION_OR_MAPPING:

```text
k_src := D_src * c_p,src * rho_assumed
rho_inverse := k_src / (D_src * c_p,src) = rho_assumed
C_p,V_inverse := k_src / D_src = rho_assumed * c_p,src
```

At the locked `573.15 K` row:

```text
rho_assumed  = 1780 kg m^-3
rho_inverse  = 1780.0000000000002 kg m^-3
C_p,V(k/D)   = 2242474.161628691 J m^-3 K^-1
C_p,V(rho cp)= 2242474.161628691 J m^-3 K^-1
```

VERIFICATION: Source audit `PASS_SOURCE_CP_95CI_CV_OPEN`; scoped no-go audit `PASS_SCOPED_SOURCE_INDEPENDENCE_NO_GO`; Topic 13 focused regression `27 passed`; Wave 1 integrity `PASS_WITH_BLOCKED_LANES`; threshold unchanged; Xie 2026 not accessed or consumed; no fit, clipping, padding, or substitute data.

CONTROLLING_BLOCKER: `dimensional_phi_energy_anchor_or_independent_alpha_calibration_missing`. The immediate source controller is `independent_same_grade_density_or_direct_volumetric_heat_capacity_missing`.

NEXT_ACTION: Source-lock either direct volumetric `c_v` or independently measured EMS-5000/same-specimen density with uncertainty, then same-regime `alpha_V` and `K_T`. Do not use reported Georgia Tech `k`, `D`, and `c_p` to infer an independent density or heat capacity. After that, derive or independently calibrate `e0` and base `Phi -> Phi_E` without TTG target residuals or Xie 2026.

CLAIM_BOUNDARY: This no-go is scoped to the information dependency of the Georgia Tech package. It is not a no-go for all graphite data, not a `c_v` calibration, not an `alpha_Phi_K` derivation, not external validation, and not Full Topic 13 or global UET closure.

## Evidence

- `docs/core/07_artifacts/topic13/t13_gatech_volumetric_cp_independence_audit.json`, SHA-256 `7e9e858548cac1843c6bf5d405aeb192226ea79ef69a7dd5c3dc1e55d3cf8c6e`
- `Data/03_Research/gatech_gen3csp_graphite_source_package.json`, SHA-256 `2635be1d91f35c9be6fd36d14a9e4d04384f158dd90340b59c5d7fa3f277bd51`
- `Data/03_Research/raw/gen3csp_graphite.xlsx`, SHA-256 `baa7f6181fa3d5521fc594cb2c832308927bc77dbac89c43b373bc304eaa6900`
- Georgia Tech graphite method: <https://gen3csp.gatech.edu/graphite/>
- Georgia Tech uncertainty and propagation method: <https://gen3csp.gatech.edu/uncertainty/>
