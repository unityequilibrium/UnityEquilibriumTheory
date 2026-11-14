# Formula Audit: Nuclear Binding Hadrons

## Scope

This registry covers the calculation paths that currently support topic `0.5`.
It separates source-backed benchmark gates from heuristic bridge terms and diagnostic-only
hadron/QCD scripts.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T05-SEMF-001` | `B = a_vol*A - a_surf*A^(2/3) - a_coul*Z*(Z-1)/A^(1/3) - a_asym*(N-Z)^2/A + delta + beta*ln(A) + yukawa*A` | `Code/01_Engine/Engine_Nuclear_Binding.py` | `A`, `Z`, `N` dimensionless counts; `B` MeV; coefficients in MeV; `delta` MeV; final `B/A` MeV per nucleon | `checked_local_reference` for SEMF coefficients; `heuristic_bridge` for UET entropy correction; `heuristic_bridge` for Yukawa add-on | `checked local` for selected heavy-nucleus benchmark; not first-principles | primary gate in `Research_Nuclear_Binding_SourceLocked.py` | Light nuclei can fail badly; additive correction may hide fitted/heuristic behavior if described too strongly. | Source-lock coefficient provenance and split SEMF baseline from UET correction in artifact metrics. |
| `T05-YUKAWA-002` | `correction = 10.0 * exp(-mu*R) / R`, `mu = m_pion / hbar_c`, `R = r0*A^(1/3)` | `Code/01_Engine/Engine_Nuclear_Binding.py` | `m_pion` MeV; `hbar_c` MeV*fm; `R` fm; `mu` 1/fm; correction MeV-like before multiplication by `A` | `source_locked_physics_constant` for pion mass convention; `heuristic_bridge` for coefficient `10.0` and additive use | `heuristic bridge` | part of primary binding engine | The coefficient and additive placement can create apparent heavy-nucleus success while failing outside domain. | Record sensitivity of heavy-nucleus pass rate to the Yukawa coefficient and justify or demote the term. |
| `T05-PAIR-003` | `delta = +/- a_pair/sqrt(A)` for even-even / odd-odd nuclei | `Code/01_Engine/Engine_Nuclear_Binding.py` | `A` dimensionless; `delta` MeV; parity of `Z` and `N` dimensionless | `checked_local_reference` from SEMF convention | `checked local` | primary binding engine | Pairing convention affects small/light nuclei strongly and must not be treated as UET-specific derivation. | Document coefficient source and compare against SEMF-only baseline. |
| `T05-PROTON-RADIUS-004` | `r_p = 0.841 fm` | `Code/01_Engine/Engine_Nuclear_Binding.py` | `r_p` fm | `source_locked_benchmark_input` / benchmark anchor from muonic-hydrogen-style value | `benchmark anchor` | primary gate against `Data_Proton_Radius.json` | The engine returns the target-like value directly, so this is not an independent prediction. | Replace with derived relation or keep it labeled as benchmark-anchor compatibility only. |
| `T05-AME-GATE-005` | `relative_error = abs(predicted_BE/A - observed_BE/A) / observed_BE/A * 100` | `Code/03_Research/Research_Nuclear_Binding_SourceLocked.py` | `predicted_BE/A`, `observed_BE/A` MeV per nucleon; error percent | `source_locked_benchmark_input` from AME2020 raw-derived subset | `identity` for metric; source-backed benchmark gate for data | primary verifier threshold: heavy nuclei `A >= 16` under `15%`, proton radius under `5%` | Passing selected heavy nuclei does not imply full AME table pass. | Keep strict subset gate separate from full-table diagnostic in README and paper drafts. |
| `T05-FULLTABLE-006` | table-wide residual distribution over parsed AME2020 rows | `Code/03_Research/Research_Nuclear_Binding_FullTable_Diagnostic.py` | AME2020 parsed `A`, `Z`, `BE_keV`; derived `BE/A` MeV per nucleon; error percent | `source_locked_benchmark_input` from `docs/data/external/particle_physics/ame2020/mass_1.mas20` | `checked local` diagnostic | diagnostic-only artifact | Light nuclei show very weak behavior; using only selected subset can overstate robustness. | Use diagnostic artifact in limitations and decide whether a separate light-nuclei engine should own `A < 16`. |
| `T05-LIGHT-007` | deuteron: `(hbar_c*kappa)^2/(2*mu)`; triton/He3/He4 use overlap, Coulomb, and saturation factors | `Code/01_Engine/Engine_Light_Nuclei.py` | `hbar_c` MeV*fm; `kappa` 1/fm; `mu` MeV; binding MeV; factors dimensionless | `checked_local_reference` for constants; `heuristic_bridge` for overlap/saturation terms | `heuristic bridge` | diagnostic-only for light nuclei | Uses empirical-looking constants (`0.232`, `0.95`, `0.762`, `1.3`, `1.16`) and should not be merged into heavy-nucleus pass claims. | Source-lock constants or classify as fitted/heuristic; connect to separate verifier if retained. |
| `T05-HADRON-008` | meson/baryon mass as sum of constituent masses with constituent shift `DELTA_M_UET = 330*beta` | `Code/01_Engine/Engine_Hadron_Model.py` | quark masses MeV; hadron mass MeV; `beta` dimensionless | `source_locked_benchmark_input` for PDG current masses; `heuristic_bridge` for constituent shift and strangeness factor | `heuristic bridge` | diagnostic-only | Constituent shift can act as hidden benchmark anchor; embedded PDG snapshots are not a source-locked data layer. | Move PDG/FLAG inputs to external/source-backed data package or demote to legacy diagnostic. |
| `T05-GMOR-009` | `m_pi = sqrt(abs(-(m_u+m_d)*condensate/F_pi^2))` | `Code/01_Engine/Engine_Hadron_Model.py` | `m_u`, `m_d`, `F_pi`, `sigma_qq` MeV; condensate MeV^3; result MeV | `checked_local_reference` from PDG/lattice-QCD-style constants | `checked local` | diagnostic-only | Constants are embedded and not yet tied to local source files/hashes. | Source-lock PDG/FLAG values or move this row to checked external benchmark status. |
| `T05-QCD-010` | `alpha_s(Q) = 1/(b0*ln(Q^2/Lambda^2))`; UET variants multiply or alter `Lambda` | `Code/01_Engine/Engine_QCD_Bridge.py` | `Q`, `Lambda` GeV; `alpha_s` dimensionless; `n_f` active flavors | `source_locked_benchmark_input` for PDG-like data; `heuristic_bridge` for UET corrections | `open` | diagnostic-only | `alpha_s_uet_v2` currently treats a float as a dict (`QCD_PARAMS[...]["value"]`), so that branch is not reliable. | Fix the data shape bug, source-lock PDG alpha_s inputs, and define whether this is baseline QCD or a UET correction. |
| `T05-CONF-011` | proof script checks `0.9 < proton_mass_gev < 1.01` after hadron engine step | `Code/02_Proof/Proof_Color_Confinement.py` | proton mass GeV from diagnostic hadron model | `heuristic_bridge` | `open` | diagnostic-only | Script returns `True` regardless of pass/fail print path, so it cannot certify confinement. | Make proof command return real pass/fail and label as diagnostic until derivation exists. |

## Unit and Data Discipline

- AME2020 binding inputs are source-backed through `docs/data/external/particle_physics/ame2020/mass_1.mas20`.
- Strict pass/fail applies only to selected heavy nuclei (`A >= 16`) plus proton radius.
- Full-table AME2020 behavior is diagnostic; it is not a pass/fail proof of general nuclear binding.
- Hadron/QCD constants remain partly embedded snapshots and should not be reused as source-locked UET constants.

## Current Formula Status

- Primary nuclear-binding gate: `checked local` for selected heavy nuclei.
- Light nuclei: `heuristic bridge` / diagnostic.
- Proton radius: benchmark anchor, not independent prediction.
- Hadron and QCD bridge: diagnostic/open until source-backed data and verifier contracts are added.
- Confinement proof script: open; current return behavior is not a proof gate.

## Next Hardening Steps

1. Split SEMF baseline and UET correction metrics in the primary artifact.
2. Source-lock SEMF coefficients and hadron/QCD constants or label them as legacy snapshots.
3. Fix `Engine_QCD_Bridge.alpha_s_uet_v2` data-shape bug before using it in any verifier.
4. Change `Proof_Color_Confinement.py` to return a real pass/fail status.
5. Add a dedicated light-nuclei verifier or keep `A < 16` explicitly outside the heavy-nucleus claim.
