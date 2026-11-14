# Formula Audit: 0.0_Grand_Unification

Review status: first reviewed integration registry.

This topic is the integration/index layer for core research, not a master proof layer. Its formulas and metrics must cite subordinate topics and inherit their limitations. A pass in this topic means selected engines can be orchestrated and recorded; it does not promote unresolved claims in subordinate topics.

## Formula Registry

| formula_id | relation | code surface | variables and units | constant_origin | proof_status | verification_role | failure_mode | next_hardening_step |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| `T00-OMEGA-001` | Master action density sketch: `Omega_density = (kappa/2)*(dC/dx)^2 + V(C) + beta*C*I`; Euler-Lagrange sketch: `kappa*C'' - V'(C) - beta*I = 0`. | `Code/02_Proof/Proof_Grand_Unification.py` | `C`: information/configuration field; `x`: coordinate; `kappa`, `beta`: dimensionless or topic-dependent coupling parameters; `I`: information/intensity term; `V(C)`: potential term. Units are not closed in this topic. | Core UET symbolic relation; not source-locked to an external derivation here. | Symbolic model sketch/open derivation. | Explanatory only; not current primary verifier gate. | Treating the sketch as a derivation of GR/QM/mass generation hides unresolved units and subordinate proof gaps. | Link each term to core `docs/core` formula registry and subordinate topic formula IDs with unit conventions. |
| `T00-OMNI-002` | Integration run at beta values: component engines are called with `get_params(topic, beta=beta)` and metrics are collected into `UniverseState`; dependency status is read from `Data/03_Research/integration_dependency_manifest.json`. | `Code/01_Engine/Engine_Omni.py`, `Code/03_Research/Verify_Omni.py`, `Data/03_Research/integration_dependency_manifest.json` | `beta`: dimensionless global parameter; component metrics retain subordinate-topic units, e.g. Weinberg angle dimensionless, tau mass MeV, Reynolds number dimensionless, H-alpha error percent. | Component formulas and constants originate in subordinate topics; artifact status originates in subordinate verifier outputs. | Integration/run-contract with dependency-status gate. | Primary verifier role. | If subordinate topics use benchmark-fed or heuristic outputs, or if subordinate artifacts are WARN/FAIL/missing, the integration artifact inherits those limitations. | Expand the manifest to all core topics and map each metric to subordinate formula IDs. |
| `T00-GALAXY-003` | Galaxy branch metric: derived halo ratio from `v_tot`, `r_probe`, `G_GALACTIC`, and baryonic mass model. | `Code/01_Engine/Engine_Omni.py`, topic `0.1`. | `v_tot`: km/s-like velocity; `r_probe`: kpc; `G_GALACTIC`: galaxy-unit gravitational constant; mass terms in solar-mass-like units. | Subordinate topic `0.1` and core parameter constants. | Delegated checked/local status depends on `0.1`. | Integration metric only. | Unit or benchmark changes in `0.1` silently change `0.0` dashboard meaning. | Link to `0.1` artifact and formula IDs. |
| `T00-EW-004` | Electroweak branch metric: `weinberg_angle_geometric()` returns corrected `sin^2(theta_W)`. | `Code/01_Engine/Engine_Omni.py`, topic `0.6`. | Weinberg angle metric dimensionless. | Subordinate topic `0.6`; benchmark target in verifier is `0.2312`. | Delegated benchmark check. | Primary verifier threshold checks absolute error <= `0.001`. | A local benchmark match is not a unified-force proof. | Link to `0.6` verification artifact and constants. |
| `T00-MASS-005` | Mass branch metric: tau mass from Koide-constrained `UETMassEngine.predict_tau_mass(0.511, 105.66)`. | `Code/01_Engine/Engine_Omni.py`, topic `0.17`. | Electron/muon/tau masses in MeV. | Subordinate topic `0.17`; Koide target is benchmark anchor. | Delegated diagnostic/integration metric. | Primary verifier threshold checks tau mass within 1 MeV of `1776.9`. | Can look like independent prediction while it is Koide-constrained and benchmark-framed. | Inherit `0.17` formula audit limitations and use source-locked masses. |
| `T00-QUANTUM-006` | Quantum branch metric: Bell-like state entropy after Hadamard + CNOT, target entropy near `1.0`. | `Code/01_Engine/Engine_Omni.py`, topic `0.18`. | Entropy in bits; state vector dimensionless complex amplitudes. | Standard quantum-circuit formulas via subordinate `0.18` engine. | Delegated model check. | Primary verifier threshold checks abs entropy error <= `0.001`. | Does not prove mathematical branches in `0.18`; only checks a small quantum circuit state. | Split quantum-engine validation from Mathnicry theorem attempts. |
| `T00-COMPONENTS-007` | Other dashboard metrics: fluid critical Reynolds, AI initial loss, economy omega, atomic H-alpha percent error. | `Code/01_Engine/Engine_Omni.py`, topics `0.10`, `0.20`, `0.24`, `0.25`. | Mixed units; each metric inherits subordinate topic conventions. | Subordinate topics. | Delegated integration metrics. | Recorded in artifact; not all are hard gates. | Mixed metrics can be misread as a single proof score. | Add dependency map with artifact status and threshold role for each component. |

## Current Verifier Boundary

- Primary verifier: `Code/03_Research/Verify_Omni.py`.
- Current artifact target: `Result/artifacts/0_0_grand_unification_verification.json`.
- Supported claim class: internal integration/run-contract check for selected component engines.
- Unsupported by current artifact: Theory of Everything, derivation of all constants, proof of GR/QM unification, or proof transfer from any subordinate topic.

## Dependency Policy

- `0.0` must inherit limitations from every dependency it calls.
- If a dependency has `FAIL` or `WARN` artifact status, `0.0` cannot claim theory-level closure.
- If a dependency is benchmark-fed or heuristic, `0.0` must label the dashboard metric as delegated/diagnostic.

## Required Follow-Up

- Expand component artifact-status reads to all core dependencies, not only the selected Omni-engine scope.
- Map every dashboard metric to subordinate `FORMULA_AUDIT.md` IDs.
- Keep README language as index/governance/integration, not master proof.

## Audit Link

- Core audit report: `docs/meta/core_research_hardening_audit.md`
