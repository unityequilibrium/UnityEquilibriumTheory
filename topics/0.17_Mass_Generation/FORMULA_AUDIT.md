# Formula Audit: 0.17_Mass_Generation

Review status: first reviewed registry.

This topic currently contains two separate evidence branches: a Higgs-coupling consistency check and a charged-lepton/Koide mass-hierarchy check. These branches must not be merged into a single "mass generation proved" claim unless their data, constants, and verification artifacts are aligned.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T17-KOIDE-001` | `K = (sqrt(m_e)+sqrt(m_mu)+sqrt(m_tau))^2 / (m_e + m_mu + m_tau)`; engine target is `K = 1.5`. Equivalent conventional form is `Q = sum(m)/(sum(sqrt(m))^2) ~= 2/3`. | `Code/01_Engine/Engine_Mass_Higgs.py`, `Code/03_Research/Research_Mass_Mechanism.py` | `m_e`, `m_mu`, `m_tau`: charged-lepton masses in MeV; `sqrt(m)`: sqrt(MeV); `K`, `Q`: dimensionless ratios. | Lepton masses are PDG/CODATA-style benchmark inputs; exact `1.5`/`2/3` target is a Koide relation benchmark anchor. | Empirical relation/benchmark anchor, not derived first-principles proof. | Diagnostic branch; not the current primary verifier in `VERIFICATION_SPEC.md`. | Treating the Koide match as a derivation of mass generation hides that tau is benchmark-fed or algebraically constrained by the selected relation. | Source-lock the PDG values used, decide whether `K=1.5` or `Q=2/3` is the canonical registry form, and create a dedicated Koide verifier artifact. |
| `T17-TAU-002` | Tau prediction from electron and muon by solving `(sqrt(m_e)+sqrt(m_mu)+x)^2 = 1.5*(m_e+m_mu+x^2)` for `x=sqrt(m_tau)` and selecting the heavier root. | `Code/01_Engine/Engine_Mass_Higgs.py`, `Code/03_Research/Verify_Mass_Generation.py` | Inputs `m_e`, `m_mu`, output `m_tau`: MeV; quadratic coefficients have mixed sqrt(MeV)/MeV algebra through `x=sqrt(m_tau)`; error: percent or sigma against observed tau. | Electron/muon/tau benchmark values are local PDG/CODATA inputs; target `1.5` is Koide anchor. | Algebraic consequence of assuming Koide target; not an independent mass-generation derivation. | Diagnostic-only until a primary artifact records the prediction, tau benchmark, uncertainty, and pass/fail threshold. | The branch can look predictive while the relation is imposed as an exact constraint; sigma threshold uses hardcoded tau uncertainty. | Add artifact output for predicted tau, observed tau, uncertainty source, percent error, and sigma; label as Koide-constrained inference. |
| `T17-HIGGSKAPPA-003` | Coupling-modifier residual: `avg_dev = mean(abs(kappa_observed - 1.0))`; current gate treats `avg_dev < 0.2` as pass. | `Code/03_Research/Research_Higgs_Coupling.py` | `kappa_observed`: dimensionless observed/SM coupling modifier; `uncertainty`: dimensionless; `mass_GeV`: GeV; `avg_dev`: dimensionless. | `kappa` and uncertainties are topic-local values attributed to CMS Nature 2022; `1.0` is the Standard Model normalized baseline; `0.2` threshold is local working threshold. | Internal benchmark consistency check. | Current primary verifier branch. | Average absolute residual ignores uncertainty weighting, correlations, and source-table provenance; it can pass because the input is already normalized to the SM. | Write artifact directly from the script with dataset hashes and upgrade to uncertainty-aware residual such as pull or chi-square when provenance is normalized. |
| `T17-HIGGSVEV-004` | Standard Model coupling context: fermion `y_f ~= sqrt(2)*m_f/v`; data records `v = 246.22 GeV`, but the primary script plots normalized `kappa` rather than recomputing all couplings. | `Code/03_Research/Research_Higgs_Coupling.py`, `Data/03_Research/higgs_coupling_data.json` | `m_f`: GeV; `v`: GeV; `y_f`, `kappa`: dimensionless. | Higgs vacuum expectation value and CMS/ATLAS coupling narrative are source-referenced but not raw-source locked in this topic. | Context formula, not an independent UET derivation. | Explanatory role for current verifier. | README may overread an SM consistency plot as evidence for a UET-specific mechanism. | Store exact upstream table/source citation and clarify whether verifier checks SM consistency, UET correction, or both. |
| `T17-PLANCKEXP-005` | UET mass ansatz: `m = M_P * exp(-kappa_eff * scale_factor)`; inverse action `S = ln(M_P/m)`. | `Code/03_Research/Research_Mass_Mechanism.py` | `M_P`: MeV; `m`: MeV; `kappa_eff`, `scale_factor`, `S`: dimensionless. | `M_P_MeV = 1.2209e22` is hardcoded; source not machine-linked in this topic. | Heuristic bridge/open physical mechanism. | Exploratory, not primary verifier. | Planck mass unit comments conflict with code history; no fitted or predicted `kappa_eff` is verified. | Source-lock Planck mass convention, derive or fit `kappa_eff` with declared uncertainty, and add failure cases. |
| `T17-RATIO-006` | Mass hierarchy ratios such as `m_mu/m_e`, `m_tau/m_e`, `m_tau/m_mu` from PDG-style local data. | `Data/03_Research/pdg_2024_leptons.json`, `Code/03_Research/Research_Mass_Mechanism.py` | Masses: MeV; ratios: dimensionless. | PDG 2024 local JSON is source-referenced with DOI/URL but not raw external cache verified. | Checked local reference once hashes are recorded; currently topic-local source-referenced data. | Baseline/diagnostic for lepton hierarchy claims. | Silent mismatch between `lepton_data.json` (CODATA/PDG 2020) and `pdg_2024_leptons.json` can create inconsistent benchmarks. | Choose normative lepton dataset for each verifier and record source year, DOI/URL, local hash, and preprocessing. |

## Current Verifier Boundary

- Primary verifier: `Code/03_Research/Research_Higgs_Coupling.py`.
- Current artifact target: `Result/artifacts/0_17_mass_generation_verification.json`.
- Supported claim class: internal benchmark/run-contract consistency check for topic-local Higgs coupling modifiers relative to the SM-normalized baseline `kappa = 1`.
- Unsupported by current artifact: first-principles mass generation, replacement of the Higgs mechanism, full Standard Model mass hierarchy, and formal proof of the Koide relation.

## Unit and Data Discipline

- Lepton mass branches use MeV.
- Higgs coupling branch uses GeV for masses and dimensionless `kappa`.
- Do not mix `lepton_data.json`, `pdg_2024_leptons.json`, and `PDG_Leptons.csv` without stating which file is normative for the verifier.
- A normalized `kappa` dataset already divides by the SM expectation, so passing `kappa ~= 1` is primarily an SM-consistency benchmark unless a UET-specific correction is separately defined.

## Required Follow-Up

- Make `Research_Higgs_Coupling.py` write the primary artifact directly with input hashes, average residual, threshold, and interpretation.
- Create a separate Koide/tau verifier artifact if the lepton branch is used in claims.
- Upgrade data provenance: upstream DOI/URL, license/terms, raw source path or declared local working copy, preprocessing, units, and benchmark role for each important file.
- Remove or constrain language that implies a definitive new mass-generation law before the above gates exist.

## Audit Link

- Core audit report: `docs/meta/core_research_hardening_audit.md`
