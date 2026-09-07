# ⚙️ Core — UET Mathematical Engine

> Foundation-first status: This README contains historical/legacy engine wording and is
> not the controlling claim source. Current equation status is controlled by
> [docs/core/AGENTS.md](./AGENTS.md), the equation registry, and the foundation dependency gate.
> The legacy statement that C universally means mass or that I is a universal physical field
> is not accepted by the current research protocol.

## Current foundation contract

The legacy tables below are retained for historical compatibility. For current equation
work, use this contract:

| Symbol | Current status |
| :-- | :-- |
| C | system-state coordinate with lane-specific physical mapping; not universally mass |
| Phi | effective space-response variable; not a metric or substance |
| Pi | time derivative of Phi |
| R / I_trace | derived causal/history observable with no feedback in the new mode |
| mass, density, charge, stress-energy | separate standard-physics quantities or explicit lane mappings |

Current foundation artifacts:

- [Equation inventory](./UET_FOUNDATION_EQUATION_INVENTORY.md)
- [Correspondence matrix](./UET_FOUNDATION_CORRESPONDENCE_MATRIX.md)
- [Compatibility audit](./UET_FOUNDATION_COMPATIBILITY_AUDIT.md)
- [Foundation compatibility decision](./UET_FOUNDATION_COMPATIBILITY_DECISION.md)
- [Legacy variational closure audit](./artifacts/uet_legacy_variational_closure.json)
- [Matter-space causal discretization diagnostic](./artifacts/matter_space_causal_discretization_diagnostic.json)
- [Causal discretization repair artifact](./artifacts/causal_discretization_repair_artifact.json)
- [Causal reference energy verification](./artifacts/matter_space_causal_reference_energy_verification.json)
- [Causal Phi/Pi discrete-gradient verification](./artifacts/matter_space_causal_discrete_gradient_verification.json)
- [Changing-C shared-ledger split verification](./artifacts/matter_space_causal_split_verification.json)
- [Changing-C causal-cone compatibility audit](./artifacts/matter_space_causal_cone_compatibility.json)
- [Finite-cone C candidate specification](./MATTER_SPACE_FINITE_CONE_C_SPEC.md)
- [Finite-cone C lane comparison artifact](./artifacts/matter_space_causal_lane_comparison.json)
- [Foundation status aggregate](./UET_FOUNDATION_STATUS_AGGREGATE.md)
- [Machine-readable inventory gate](./artifacts/uet_foundation_equation_inventory.json)
- [Machine-readable correspondence matrix](./artifacts/uet_foundation_correspondence_matrix.json)
- [Machine-readable aggregate status](./artifacts/uet_foundation_status_aggregate.json)
- [Thought experiment: observation as past behavior](./THOUGHT_EXPERIMENT_OBSERVATION_PAST_BEHAVIOR.md)
- [Canonical C ontology and physical mapping](../UET_Documentation_Details/03_Core_Theory/relational-C-and-physical-mapping.md)
- [Relational two-body baseline specification](./RELATIONAL_TWO_BODY_BASELINE_SPEC.md)
- [Relational two-body baseline artifact](./artifacts/relational_two_body_baseline_verification.json)
- [Mass-density correspondence specification](./MASS_DENSITY_CORRESPONDENCE_SPEC.md)
- [Mass-density correspondence artifact](./artifacts/mass_density_correspondence_verification.json)
- [Matter-to-interaction forward mapping specification](./MATTER_INTERACTION_FORWARD_SPEC.md)
- [Matter-to-interaction forward mapping artifact](./artifacts/matter_interaction_forward_verification.json)
- [Persistence-energy diagnostic specification](./PERSISTENCE_ENERGY_DIAGNOSTIC_SPEC.md)
- [Persistence-energy diagnostic artifact](./artifacts/persistence_energy_diagnostic_verification.json)
- [Thermal observable bridge specification](./THERMAL_OBSERVABLE_BRIDGE_SPEC.md)
- [Thermal observable bridge artifact](./artifacts/thermal_observable_bridge_verification.json)
- [Curved 3+1 ADM constraint interface](./uet_curved_3p1_constraints.py)
- [Curved 3+1 ADM constraint verification](./artifacts/curved_3p1_adm_constraint_interface_audit.json)
- [Curved 3+1 parent dependency gate](./artifacts/core_curved_3p1_parent_gate.json)
- [Curved 3+1 periodic geometry operator](./uet_curved_3p1_geometry.py)
- [Curved 3+1 geometry verification](./artifacts/curved_3p1_geometry_operator_verification.json)
- [Curved 3+1 ADM evolution RHS](./uet_curved_3p1_adm_evolution.py)
- [Curved 3+1 ADM evolution verification](./artifacts/curved_3p1_adm_evolution_operator_verification.json)
- [Fixed-gauge ADM hyperbolicity no-go](./artifacts/curved_3p1_fixed_gauge_adm_hyperbolicity_no_go.json)
- [Curved 3+1 evolution branch specification](./CORE_CURVED_3P1_EVOLUTION_BRANCH_SPEC.md)
- [Curved 3+1 generalized-harmonic principal system](./uet_curved_3p1_generalized_harmonic.py)
- [Generalized-harmonic principal-system verification](./artifacts/curved_3p1_gh_principal_system_verification.json)
- [Generalized-harmonic branch gate](./artifacts/curved_3p1_gh_branch_gate.json)

> **Historical engine layer for candidate UET equation families**
> **Version 0.9.0** | Last Updated: 2026-01-13

![Engine](https://img.shields.io/badge/Engine-UET_Master_Eq-blue)
![Coverage](https://img.shields.io/badge/Axioms-12%2F12-brightgreen)
![Status](https://img.shields.io/badge/Status-Legacy-Claim-Controlled-yellow)
![Tests](https://img.shields.io/badge/Tests-126_(98.4%25)-green)

---

## 🎯 Purpose

This directory contains the **computational core** of the Unity Equilibrium Theory. It is the "Engine" that solves the fundamental energy functional for all 20 physics domains (from Galaxies to Quantum Mechanics).

**The Rule:** Nature is constrained optimization.
> *The system state evolves to minimize the generalized energy functional $\Omega$.*

**The Value Equation:**
> $$\mathcal{V} = -\Delta\Omega$$
> *When disequilibrium decreases, the system gains Value.*

---

## Legacy master equation (historical form)

The following seven-term functional is retained as a legacy candidate implementation; it is not a closed physical derivation:

$$
\Omega[C,I,J] = \int d^3x \left[ 
\underbrace{V(C)}_{\text{A1: Energy}} + 
\underbrace{\frac{\kappa}{2}|\nabla C|^2}_{\text{A3: Space/Memory}} + 
\underbrace{\beta C \cdot I}_{\text{A2: Info Coupling}} + 
\underbrace{\gamma_J (J_{in} - J_{out}) \cdot C}_{\text{A4: Semi-Open Exchange}} + 
\underbrace{W_N |\nabla \Omega|}_{\text{A5: Natural Will}} + 
\underbrace{\beta_U V_{game}}_{\text{A8: Dynamic Game}} + 
\underbrace{\lambda \Sigma (C_i - C_j)^2}_{\text{A10: Coherence}}
\right]
$$

---

## 🔤 Variable Definition

| Symbol | Name | Mathematical Meaning | Physical Interpretation |
|:------:|:-----|:---------------------|:------------------------|
| **C** | Relational interaction coordinate | State coordinate `C(x,t)` | Current ontology; physical realization is lane-specific |
| **I** | Lane-declared second sector | Legacy `I` label or declared field | Must be explicitly defined; `I_trace` is derived when used |
| **J** | Flux Field | J_in - J_out | Open system energy exchange |
| **V(C)** | Potential | legacy or lane-specific functional of `C` | Cost/comparator over relational structure; units are lane-specific |
| **κ** | Gradient coefficient | coefficient of `\|∇C\|²` | Variation penalty; units must be closed per lane |
| **β** | Coupling coefficient | coefficient of `C I` | Not automatically `kT ln 2`; Landauer is an external bound when applicable |
| **Ω** | Equilibrium Functional | ∫[...] dx | Total disequilibrium (minimize this) |
| **𝒱** | Value | -ΔΩ | Improvement per step |

> 📖 **Current C ontology**: See [C as a Relational Interaction Variable](../UET_Documentation_Details/03_Core_Theory/relational-C-and-physical-mapping.md). The nearby legacy table is retained for provenance.

---

## 📄 Engine Components

| File | Role | Description |
|:-----|:-----|:------------|
| [`uet_master_equation.py`](./uet_master_equation.py) | **Legacy engine entry point** | Defines candidate Ω functionals and solver paths; not a universal physical law or single source of truth. |
| [`uet_matrix_engine.py`](./uet_matrix_engine.py) | **The Solver** | Fast Tensor-based implementation for large-scale grids (3D Galaxies). |
| [`uet_matrix_toolkit.py`](./uet_matrix_toolkit.py) | **The Tools** | Helper functions for visualization and matrix algebra. |
| [`uet_4d_engine.py`](./uet_4d_engine.py) | **Relativity** | Extension for 4D spacetime metrics and tensor operations. |

---

## 📚 Documentation
| [`../Doc/DOMAIN_MAPPING.md`](../Doc/DOMAIN_MAPPING.md) | C/I ในแต่ละสาขา (6 domains) |
| [`../Doc/VALUE_EQUATION.md`](../Doc/VALUE_EQUATION.md) | 𝒱 = -ΔΩ — สมการ Value |

---

## 🌐 Multi-Domain Interpretation

C และ I มีความหมายต่างกันในแต่ละ domain — แต่สมการเดียวกัน:

| Domain | C = | I = |
|:-------|:----|:----|
| **Physics** | relational interaction coordinate; lane mapping required | lane-declared second sector; no universal dark-matter identity |
| **Neuroscience** | lane-specific mapping from interaction structure | lane-specific second sector |
| **Economics** | lane-specific mapping from interaction structure | lane-specific second sector |
| **Biology** | lane-specific mapping from interaction structure | lane-specific second sector |
| **Machine Learning** | lane-specific mapping from interaction structure | lane-specific second sector |

> 📖 **Full domain mapping**: See [`../Doc/DOMAIN_MAPPING.md`](../Doc/DOMAIN_MAPPING.md)

---

## ✅ Validator Scripts

These scripts ensure the engine adheres to fundamental physics limits (Axiom 11):

| Script | Purpose |
|:-------|:--------|
| [`test/`](./test/) | Unit tests for core functions |
| [`validation/`](./validation/) | Physics validation scripts |

---

## 🔗 Navigation

- **🔙 [Research Root](../README.md)**
- **🧪 [Topics (Applications)](../topics/)**
- **📊 [Data Sources](../DATA_SOURCE_MAP.md)**
- **📖 [Documentation Index](../Doc/DOC_INDEX.md)**

---

*Unity Equilibrium Theory — Core Engine v0.9.0*
*"𝒱 = -ΔΩ — ระบบที่ลดความไม่สมดุล = ระบบที่สร้าง Value"*
