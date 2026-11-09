# Formula Audit: 0.16_Heavy_Nuclei

Review status: reviewed registry for the current heavy-nuclei binding engine, fission diagnostic, and AME2020 working-copy comparisons.

This topic currently uses a UET interpretation of liquid-drop / SEMF-like terms. The current primary verifier supports only an internal fission sanity check and an AME2020 U-235 binding checkpoint. It does not yet validate fragment Q-values, island-of-stability predictions, or a first-principles nuclear theory.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `HN16-SEMF-BINDING` | `BE = a_V A - a_S A^(2/3) - a_C Z(Z-1)/A^(1/3) - a_A(N-Z)^2/A + delta` | `Code/01_Engine/Engine_Heavy_Nuclei.py::binding_energy_semf`; `Code/01_Engine/Engine_Fission_Solver.py::semf_binding_energy` | `Z`, `N`, `A` dimensionless counts; coefficients in MeV; output MeV or converted to keV depending on code path | standard SEMF coefficient set encoded locally; not derived inside this topic | checked local baseline / benchmark bridge | primary formula path for current fission sanity artifact | Treating SEMF coefficients as UET-derived would overstate the result. | Add explicit coefficient provenance and compare against a source-locked SEMF baseline table. |
| `HN16-UET-SEMF-BRIDGE` | `uet_bridge_be(Z,A) = binding_energy_semf(Z,A)` | `Code/01_Engine/Engine_Heavy_Nuclei.py::uet_bridge_be` | same as `HN16-SEMF-BINDING` | topic interpretation bridge over SEMF coefficients | heuristic bridge | primary artifact formula path | Bridge currently equals SEMF, so it is not an independent UET prediction. | Replace equality bridge with a documented derivation or keep claims at interpretation/benchmark level. |
| `HN16-FISSION-Q-SANITY` | `Q_bridge = BE(Ba-141) + BE(Kr-92) - BE(U-235)` | `Code/03_Research/Research_Fission.py` | binding energies in MeV; output energy release in MeV | fragment values are engine-derived SEMF/UET bridge outputs; U-235 has AME2020 checkpoint | internal sanity check | primary verifier artifact, status currently `WARN` | Without AME fragment masses, the fission Q-value is not source-locked. | Load Ba-141 and Kr-92 from AME/NUBASE and compare against evaluated fission energy. |
| `HN16-U235-AME-CHECK` | `error = |BE_bridge(U-235) - BE_AME(U-235)| / BE_AME(U-235)` | `Code/03_Research/Research_Fission.py`; `Data/03_Research/ame2020_heavy_nuclei.json` | MeV and percent | AME2020 working copy with DOI in data file | source-labeled checkpoint | primary artifact checkpoint | Single isotope agreement does not validate the heavy-nuclei model. | Expand to multiple heavy isotope rows with fixed thresholds. |
| `HN16-UET-LD-HEAVY-BINDING` | `BE_uet_ld = engine.uet_bridge_be(Z,A)` compared with AME heavy-nuclei rows | `Code/03_Research/Research_Heavy_Binding.py` | `BE_exp` and `BE_uet_ld` in MeV; errors in percent | AME2020 heavy working copy; SEMF coefficients in engine | internal benchmark, not primary artifact yet | secondary research lane | Current script prints pass rate and visualizes, but does not write the primary artifact. | Convert heavy-binding comparison into artifact rows and define pass thresholds. |
| `HN16-SOLITON-LEGACY` | `BE = 8.5 A - 0.5 Z(Z-1)/A^(1/3)` | `Code/03_Research/Research_Heavy_Binding.py::uet_soliton_be` | `A`, `Z` counts; output MeV-like model units | local legacy heuristic constants | heuristic baseline | diagnostic comparator only | May be mistaken for current theory if cited without context. | Keep as legacy comparator or remove from README-facing claims. |
| `HN16-STABILITY-VALLEY` | stability-valley / magic-number checks | `Code/02_Proof/Proof_Stability_Valley.py` | nuclear counts and stability labels; unit audit incomplete | mixed local model terms and source labels | open | excluded from primary artifact | Cannot support Island of Stability claims until artifact-backed. | Create a stability artifact with source-locked isotope half-lives/shell labels. |

## Claim Boundary

- Supported now: internal fission sanity check that records U-235 AME binding identity and flags missing fragment provenance.
- Partially supported: heavy-nuclei binding comparison as a secondary script, pending artifact rows and thresholds.
- Not supported now: prediction of U-235 evaluated fission energy, proof of the island of stability, or a first-principles nuclear binding derivation.
- Downstream use: `0.5`, `0.17`, `0.21`, `0.23`, and `0.0` may cite this topic only with the SEMF-bridge and fragment-provenance limitations.

## Audit Link

- Primary artifact: `Result/artifacts/0_16_heavy_nuclei_verification.json`
- Core audit report: `docs/meta/core_research_hardening_audit.md`
