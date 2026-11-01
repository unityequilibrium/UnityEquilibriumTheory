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

- [Equation inventory](01_contracts/UET_FOUNDATION_EQUATION_INVENTORY.md)
- [Correspondence matrix](01_contracts/UET_FOUNDATION_CORRESPONDENCE_MATRIX.md)
- [Compatibility audit](08_history/research_notes/UET_FOUNDATION_COMPATIBILITY_AUDIT.md)
- [Foundation compatibility decision](01_contracts/UET_FOUNDATION_COMPATIBILITY_DECISION.md)
- [Legacy variational closure audit](07_artifacts/gates/uet_legacy_variational_closure.json)
- [Matter-space causal discretization diagnostic](07_artifacts/archive/matter_space_causal_discretization_diagnostic.json)
- [Causal discretization repair artifact](07_artifacts/archive/causal_discretization_repair_artifact.json)
- [Causal reference energy verification](07_artifacts/verification/matter_space_causal_reference_energy_verification.json)
- [Causal Phi/Pi discrete-gradient verification](07_artifacts/verification/matter_space_causal_discrete_gradient_verification.json)
- [Changing-C shared-ledger split verification](07_artifacts/verification/matter_space_causal_split_verification.json)
- [Changing-C causal-cone compatibility audit](07_artifacts/archive/matter_space_causal_cone_compatibility.json)
- [Finite-cone C candidate specification](01_contracts/MATTER_SPACE_FINITE_CONE_C_SPEC.md)
- [Finite-cone C lane comparison artifact](07_artifacts/archive/matter_space_causal_lane_comparison.json)
- [Foundation status aggregate](01_contracts/UET_FOUNDATION_STATUS_AGGREGATE.md)
- [Machine-readable inventory gate](07_artifacts/gates/uet_foundation_equation_inventory.json)
- [Machine-readable correspondence matrix](07_artifacts/gates/uet_foundation_correspondence_matrix.json)
- [Machine-readable aggregate status](07_artifacts/gates/uet_foundation_status_aggregate.json)
- [Thought experiment: observation as past behavior](08_history/research_notes/THOUGHT_EXPERIMENT_OBSERVATION_PAST_BEHAVIOR.md)
- [Canonical C ontology and physical mapping](../UET_Documentation_Details/03_Core_Theory/relational-C-and-physical-mapping.md)
- [Relational two-body baseline specification](01_contracts/RELATIONAL_TWO_BODY_BASELINE_SPEC.md)
- [Relational two-body baseline artifact](07_artifacts/verification/relational_two_body_baseline_verification.json)
- [Mass-density correspondence specification](01_contracts/MASS_DENSITY_CORRESPONDENCE_SPEC.md)
- [Mass-density correspondence artifact](07_artifacts/correspondence/mass_density_correspondence_verification.json)
- [Matter-to-interaction forward mapping specification](01_contracts/MATTER_INTERACTION_FORWARD_SPEC.md)
- [Matter-to-interaction forward mapping artifact](./07_artifacts/verification/matter_interaction_forward_verification.json)
- [Persistence-energy diagnostic specification](01_contracts/PERSISTENCE_ENERGY_DIAGNOSTIC_SPEC.md)
- [Persistence-energy diagnostic artifact](07_artifacts/verification/persistence_energy_diagnostic_verification.json)
- [Thermal observable bridge specification](01_contracts/THERMAL_OBSERVABLE_BRIDGE_SPEC.md)
- [Thermal observable bridge artifact](07_artifacts/topic13/thermal_observable_bridge_verification.json)
- [Curved 3+1 ADM constraint interface](02_equations/covariant/uet_curved_3p1_constraints.py)
- [Curved 3+1 ADM constraint verification](07_artifacts/verification/curved_3p1_adm_constraint_interface_audit.json)
- [Curved 3+1 parent dependency gate](07_artifacts/gates/core_curved_3p1_parent_gate.json)
- [Curved 3+1 periodic geometry operator](02_equations/covariant/uet_curved_3p1_geometry.py)
- [Curved 3+1 geometry verification](07_artifacts/verification/curved_3p1_geometry_operator_verification.json)
- [Curved 3+1 ADM evolution RHS](02_equations/covariant/uet_curved_3p1_adm_evolution.py)
- [Curved 3+1 ADM evolution verification](07_artifacts/verification/curved_3p1_adm_evolution_operator_verification.json)
- [Fixed-gauge ADM hyperbolicity no-go](07_artifacts/archive/curved_3p1_fixed_gauge_adm_hyperbolicity_no_go.json)
- [Curved 3+1 evolution branch specification](01_contracts/CORE_CURVED_3P1_EVOLUTION_BRANCH_SPEC.md)
- [Curved 3+1 generalized-harmonic principal system](02_equations/covariant/uet_curved_3p1_generalized_harmonic.py)
- [Generalized-harmonic principal-system verification](07_artifacts/verification/curved_3p1_gh_principal_system_verification.json)
- [Generalized-harmonic branch gate](07_artifacts/gates/curved_3p1_gh_branch_gate.json)

<a id="current-response-realization"></a>
### Current response realization — ตรวจถึง 23 ตุลาคม 2026

> **ขอบเขตชุดเผยแพร่:** รอบนี้เผยแพร่เฉพาะสาม README และ WORK_LEDGER ไม่รวมงานวิจัย/PR ค้าง การตรวจ availability อ้าง main `d0210c00b63398f70e1f8f285a6daf5169645933` ชื่อแหล่งที่กำกับ **working-only** เป็นหลักฐานใน workspace ไม่ใช่ลิงก์ที่เปิดได้จาก public main จึงแสดงเป็นชื่อแทน hyperlink; ไม่ได้ลบผลหรือยกระดับข้ออ้าง
>
> แหล่งที่ยังไม่รวม: `docs/meta/UET_THEORY_ARGUMENT.md` (§§23–25), `docs/topics/0.13_Thermodynamic_Bridge/calculation_contracts/energy_memory_cycle.json` และ `docs/meta/UET_RESEARCH_RETROSPECTIVE.md` ชุด source/verifier ที่รายงานอ้างยังต้องมี publication review แยก ส่วน pending curved 3+1 narrative/artifacts คงไว้ใน workspace เดิม ไม่ถูกพามาในชุดนี้

แหล่งสรุปคือ Theory Argument §§25.2–5 (working-only) ใน **local source commit `1346edfc07c2d2f9eb2adbd5257e820fa186a37b`** บน `codex/research/source-backaction-discrimination` ไม่ใช่ release ใหม่หรือหลักฐานว่า public main ตรงกับ working copy แล้ว ส่วนนี้อธิบาย realization ล่าสุด ไม่ได้แทนที่ controller ของทุก Core family

**Functional ไม่ใช่ kinetic law:** Omega ระบุ cost/availability landscape ที่เลือก; variational derivatives ระบุ mu ของ landscape นั้น แต่ยังต้องเลือกกฎวิวัฒน์ mobility, conservation, sources, initial/boundary data และ measurement/readout แยก การหาอนุพันธ์ได้ถูกไม่พิสูจน์ว่าธรรมชาติเลือก functional หรือ coefficients เหล่านั้น

#### สมการที่ใช้จริงและสถานะ opt-in

`matter_space_coupled_v1` ใช้ state `(C,Phi,Pi)` ใน normalized 1D prototype ตาม [MATTER_SPACE_RESEARCH_SPEC](01_contracts/MATTER_SPACE_RESEARCH_SPEC.md) และ [implementation](02_equations/matter_space/uet_matter_space.py):

```text
Omega[C,Phi] = integral [
    a_C*C^2/2 + b_C*C^4/4 + kappa_C*|grad C|^2/2
  + a_Phi*Phi^2/2 + b_Phi*Phi^4/4 + kappa_Phi*|grad Phi|^2/2
  - g*C^2*Phi/2
] dx
mu_C   = a_C*C + b_C*C^3 - kappa_C*lap(C) - g*C*Phi
mu_Phi = a_Phi*Phi + b_Phi*Phi^3 - kappa_Phi*lap(Phi) - g*C^2/2

C_t = -M_C*mu_C + J_C           # nonconserved control
   or M_C*lap(mu_C) + J_C       # conserved branch, separate kinetic law
Phi_t = Pi
tau_Phi*Pi_t + Pi = -M_Phi*mu_Phi + J_Phi

E = Omega + tau_Phi/(2*M_Phi)*integral Pi^2 dx
R = G_ret * (sigma_C + sigma_Phi)  # derived trace, no feedback in v1
```

สูตรนี้ใช้ periodic/zero-flux boundaries ตาม spec และ coefficient domain ที่ประกาศ ไม่ใช่ SI energy/entropy/curvature contract ใน closed conserved lane ต้องมี `integral J_C dx=0`; ใน undriven case extended ledger มี `dE/dt=-integral(sigma_C+sigma_Phi)dx` ไม่ใช่อ้างว่า Omega ลดทุก step ในทุก driven/inertial model Source work ใช้ `P_C=integral mu_C*J_C dx` และ `P_Phi=integral Pi*J_Phi/M_Phi dx` ตาม additive-source convention นี้ ไม่ย้ายไปใช้กับ force/traction ports โดยไม่แปลงบัญชี

โหมดนี้และ `legacy_variational_v1` เป็น **opt-in** ค่า default ใน [parameter source](01_contracts/units/uet_parameters.py) ยังเป็น **`legacy_local`**; รอบนี้ไม่เปลี่ยนค่าใด การเปิดไฟล์ชื่อ master จึงไม่ระบุ model จนกว่าจะล็อก mode/config/source identity

| วัตถุ | บทบาทที่ต้องรักษา |
| --- | --- |
| Legacy I | independent initialized/evolving field ที่มี coupling กลับสู่ C ใน C/I mode ไม่ใช่ derived I_trace หรือ entropy สากล |
| Phi | effective response coordinate ที่มี dynamics; ไม่ใช่ metric, particle หรือ information substance |
| Pi=Phi_t | rate/initial datum คู่กับ Phi; ไม่ใช่สารอีกชนิด การเขียน first-order pair ไม่เพิ่มกลไกใหม่ |
| E, sigma | extended normalized availability กับ dissipation; ไม่ใช่ physical energy/heat/entropy จนมี dimensional correspondence |
| R / I_trace | derived history output จาก sigma; ไม่มี feedback ไป C/Phi/Pi ใน v1 และไม่แทน complete state |
| Observer record | ผลจาก detector state + admitted input + measurement/processing operator; ไม่ใช่ R ทุกชนิดหรือ source state ทั้งหมด |

ระบบผู้วัดเป็น subsystem ได้เช่นกัน แต่ต้องประกาศ boundary/coupling: internal impact, signal transport, receiver effect และ source backaction เป็นคนละคำถาม การตรวจพบไม่แปลว่ามี reciprocal influence ที่สำคัญหรือสังเกต hidden state ได้ครบ การเปลี่ยน metadata การอ่านอย่างเดียวไม่เปลี่ยน source dynamics

#### ความสัมพันธ์ของรูปสมการและเงื่อนไขใช้แทนกัน

| รูปที่เทียบ | ความสัมพันธ์ / หลักที่ใช้ | ขอบเขตที่ไม่ตามมา |
| --- | --- | --- |
| Omega → mu_C,mu_Phi | exact variational differentiation เมื่อใช้ functional/boundary/discrete operator เดิม | ไม่เลือก kinetics หรือพิสูจน์ physical interpretation ให้เอง |
| Phi/Pi pair ↔ second-order Phi | exact rewrite เมื่อเก็บ Phi(t0),Pi(t0) และ sources เดิม | ไม่อนุญาตให้ทิ้ง independent initial rate |
| Smooth invertible coordinate map | exact หาก push forward generator, mobility, sources และ readout ครบ | C^2 สูญ sign ข้าม branches; nonlinear map ไม่รักษา constant mobility เอง |
| tau_Phi→0 / stationary Phi_*(C) | คนละ conditional reduction: overdamped evolution กับ static/adiabatic elimination | tau=0 ยังได้ Phi_t=-M_Phi*mu_Phi+J_Phi ไม่ใช่ mu_Phi=0; ต้องตรวจ time scales/initial layer/history |
| Legacy C/I ↔ C/Phi/Pi | alternative models; unresolved full bridge ไม่ใช่ constant rename | beta*C*I กับ -g*C^2*Phi/2 ต่าง parity/state dependence; สอง initial fields ไม่เท่ากับสาม |
| Conserved ↔ nonconserved C | คนละ kinetic law แม้ใช้ Omega เดียว | conserved integral/equilibrium constraint ต่าง ไม่ใช่แค่ numerical precision |
| State → R → observer record | derived output และ measurement mapping ไม่ใช่ invertible state transform | kernel/readout ไม่รับรอง complete observability หรือ feedback |
| Response → rod comparator → first mode | declared linear comparator และ projection/approximation | §23 รับเฉพาะ steady narrow-band protocol; §24 ปฏิเสธ projected-state sufficiency สำหรับ prepared-history class ที่ระบุ |

อ่าน §25.4 (working-only) สำหรับข้อโต้แย้ง/อนุมานและ §25.5 (working-only) สำหรับ relation domains เช่น stationary I elimination ให้ quadratic C correction เมื่อ kappa_I>0 ส่วน Phi sector ให้ leading quartic correction ใกล้ C=0 เมื่อ a_Phi>0,b_Phi>0 ไม่ใช่การลบ dynamic memory และไม่พิสูจน์ว่าไม่มี nonlinear representation อื่นใดเชื่อมได้

#### ที่มาของ coefficients และสิ่งที่ยังไม่ derive

| ชั้นที่มา | ตัวอย่างในขอบเขตนี้ | สิ่งที่หลักฐานรองรับ |
| --- | --- | --- |
| Definition / identity | Pi=Phi_t; นิยาม mu เป็น variational derivatives | บทบาท/การเปลี่ยนรูปภายใน model ไม่กำหนด parameter กายภาพ |
| Imported result | โครง variational/gradient flow, relaxation และ conservation จากกรอบมาตรฐาน; Landauer bound ใน SI เมื่อเงื่อนไขตรง | นำผลพร้อมเงื่อนไข ไม่ทำให้ coefficient ของ UET derive จากชื่อทฤษฎี |
| Constitutive choice | a,b,kappa,g; การเลือก M,tau, sources และ conserved/nonconserved law | normalized model/control inputs ที่ต้องประกาศ origin/units แยก ไม่ใช่ universal constants |
| Conditional derivation | mu_C,mu_Phi และ extended ledger หลังเลือก functional/kinetics | exact ภายใน assumptions; ไม่ย้อนพิสูจน์ที่มาของ functional |
| Calibration / open physical anchor | physical scale, material correspondence และ dimensional coefficients | ต้องมี independent source/calibration กับ uncertainty; ยังไม่ปิดโดย symbolic audit หรือ fit เป้าหมาย |

normalized beta ของ C/I **ไม่ใช่** inverse temperature และไม่เท่ากับ k_B*T*ln(2) ซึ่งมีหน่วย joules ส่วนหลังเป็น Landauer process bound ในบริบทที่ใช้ได้ ไม่ derive g/beta/tau หรือมวลข้อมูลสากลให้เอง ดู [scoped compatibility audit](08_history/research_notes/UET_FOUNDATION_COMPATIBILITY_AUDIT.md)

**ผลและ controller:** §23.3 (working-only) ให้ error bound <0.9%<1% ของ complex p/F_b และ x/F_b **เทียบ full normalized reference** ใน F_b-only steady band [0.99,1.01] ของ omega/omega_0 ไม่ใช่ physical accuracy; §24.6 (working-only) แสดง prepared-history ที่ projection นี้เก็บไม่ครบโดยใช้ smooth write/controlled wait/released read ไม่ได้เปลี่ยนผล steady เดิมหรือยืนยัน learning

[Compatibility decision](07_artifacts/gates/uet_foundation_compatibility_decision.json) ยัง `FOUNDATION_NOT_CLOSED`; cycle contract (working-only) ยัง review `INCOMPLETE` / physical correspondence `UNKNOWN` เฉพาะ declared path ไม่ครอบทุก family ช่อง physical map/หน่วย/source/preparation/detector uncertainty และข้อจำกัดใหม่เหนือ comparator ยังเปิดอยู่ Thermal helper bug ที่รายงานไว้ไม่ได้ซ่อมในรอบนี้และต้องทบทวนเฉพาะ claims ที่พึ่งมัน

รายงาน §§23–25 อยู่ใน local source commit ที่ระบุ แต่ retrospective และ source/verifier สามไฟล์ที่รายงานชี้ยังไม่อยู่ใน tree ของ commit นั้น จึงไม่ใช่ complete public reproduction packet; ไม่อนุมานสถานะ remote หรือทำให้ลิงก์ที่เปิดได้ในเครื่องเท่ากับเผยแพร่แล้ว บันทึกงานที่ [Topic 13 UPDATE_LOG](../topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md) / [WORK_LEDGER](../../WORK_LEDGER/2026/2026-10-23.md) ผลสายนี้ไม่เปลี่ยนสถานะเส้นทาง curved 3+1 ที่แยกทำอยู่

> **Historical engine layer for candidate UET equation families**
> **Version 0.9.0** | Last Updated: 2026-01-13

![Engine](https://img.shields.io/badge/Engine-UET_Master_Eq-blue)
![Coverage](https://img.shields.io/badge/Axioms-12%2F12-brightgreen)
![Status](https://img.shields.io/badge/Status-Legacy-Claim-Controlled-yellow)
![Tests](https://img.shields.io/badge/Tests-126_(98.4%25)-green)

---

## 🎯 Purpose

This directory contains the **computational core** of the Unity Equilibrium Theory: candidate equation families, scoped comparators and solver implementations, not one closed physical engine for all 20 historically listed domains (from Galaxies to Quantum Mechanics).

**Historical proposal:** Nature is described here through a constrained-optimization interpretation, not an established universal law.
> *The system state evolves to minimize the generalized energy functional $\Omega$.*

**The Value Equation:**
> $$\mathcal{V} = -\Delta\Omega$$
> *When disequilibrium decreases, the system gains Value.*

> ข้อความและ Value equation เดิมคงไว้เป็น interpretation ของ selected functional ไม่ใช่ข้อพิสูจน์ว่า driven/inertial systems ต้องลด Omega ทุกขณะ หรือว่า improvement/learning/persistence ตามจากค่าลดลงนี้เสมอ Extended availability, physical energy conservation, heat และ entropy เป็นคนละบัญชี

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
| [`uet_master_equation.py`](02_equations/matter_space/uet_master_equation.py) | **Legacy engine entry point** | Defines candidate Ω functionals and solver paths; not a universal physical law or single source of truth. |
| [`uet_matrix_engine.py`](../scripts/core/runners/uet_matrix_engine.py) | **The Solver** | Fast Tensor-based implementation for large-scale grids (3D Galaxies). |
| [`uet_matrix_toolkit.py`](../scripts/core/runners/uet_matrix_engine.py) | **The Tools** | Helper functions for visualization and matrix algebra. |
| [`uet_4d_engine.py`](01_contracts/correspondence/uet_gr_correspondence.py) | **Relativity** | Extension for 4D spacetime metrics and tensor operations. |

---

## 📚 Documentation
| [`../UET_Documentation_Details/LEGACY_REPORTS/03_Evidence/DOMAIN_MAPPING.md`](../UET_Documentation_Details/LEGACY_REPORTS/03_Evidence/DOMAIN_MAPPING.md) | C/I ในแต่ละสาขา (6 domains) |
| [`../UET_Documentation_Details/LEGACY_REPORTS/03_Evidence/VALUE_EQUATION.md`](../UET_Documentation_Details/LEGACY_REPORTS/03_Evidence/VALUE_EQUATION.md) | 𝒱 = -ΔΩ — สมการ Value |

---

## 🌐 Multi-Domain Interpretation

C และ I ในตารางเดิมเป็น lane-specific interpretations ของ shared template; ยังไม่มีหลักฐานว่าทุก domain เป็นสมการกายภาพเดียวกัน:

| Domain | C = | I = |
|:-------|:----|:----|
| **Physics** | relational interaction coordinate; lane mapping required | lane-declared second sector; no universal dark-matter identity |
| **Neuroscience** | lane-specific mapping from interaction structure | lane-specific second sector |
| **Economics** | lane-specific mapping from interaction structure | lane-specific second sector |
| **Biology** | lane-specific mapping from interaction structure | lane-specific second sector |
| **Machine Learning** | lane-specific mapping from interaction structure | lane-specific second sector |

> 📖 **Full domain mapping**: See [`../UET_Documentation_Details/LEGACY_REPORTS/03_Evidence/DOMAIN_MAPPING.md`](../UET_Documentation_Details/LEGACY_REPORTS/03_Evidence/DOMAIN_MAPPING.md)

---

## ✅ Validator Scripts

These scripts check declared internal conditions (historically grouped under Axiom 11); they do not establish complete physical validation or override the foundation gates:

| Script | Purpose |
|:-------|:--------|
| [`05_tests/`](./05_tests/) | Unit tests for core functions |
| [`validation/`](./05_tests/) | Physics validation scripts |

---

## 🔗 Navigation

- **🔙 [Research Root](../README.md)**
- **🧪 [Topics (Applications)](../topics/)**
- **📊 [Data Sources](../UET_Documentation_Details/LEGACY_REPORTS/03_Evidence/DATA_SOURCE_MAP.md)**
- **📖 [Documentation Index](../UET_Documentation_Details/LEGACY_REPORTS/99_Legacy/DOC_INDEX.md)**

---

*Unity Equilibrium Theory — Core Engine v0.9.0*
*"𝒱 = -ΔΩ — ระบบที่ลดความไม่สมดุล = ระบบที่สร้าง Value"*

---

<a id="wording-history-2026-10-23"></a>
## ภาคผนวก: ถ้อยคำที่ปรับในรอบนี้

ตรวจ 23 ตุลาคม 2026 — เก็บถ้อยคำที่แทนจาก public-main baseline ไม่ใช่รับรองข้ออ้างเก่า ตารางแสดงเฉพาะ cell ที่เปลี่ยนเมื่อเนื้อหาแถวอื่นคงเดิม สูตร/ตัวอย่าง/แผนภาพเดิมไม่ถูกเขียนใหม่

| ตำแหน่ง | ข้อความเดิม | ข้อความใหม่ | เหตุผล | หลักฐาน/ขอบเขต |
| --- | --- | --- | --- | --- |
| Purpose / scope | <code>This directory contains the &#42;&#42;computational core&#42;&#42; of the Unity Equilibrium Theory. It is the "Engine" that solves the fundamental energy functional for all 20 physics domains &#40;from Galaxies to Quantum Mechanics&#41;.</code> | <code>This directory contains the &#42;&#42;computational core&#42;&#42; of the Unity Equilibrium Theory: candidate equation families, scoped comparators and solver implementations, not one closed physical engine for all 20 historically listed domains &#40;from Galaxies to Quantum Mechanics&#41;.</code> | ไม่ใช้ engine family หนึ่งแทน physical closure ทุก domain; คงจำนวน 20 และขอบเขตประวัติ | §25.2–5 (working-only) / [foundation decision](07_artifacts/gates/uet_foundation_compatibility_decision.json) |
| Purpose / optimization interpretation | <code>&#42;&#42;The Rule:&#42;&#42; Nature is constrained optimization.</code> | <code>&#42;&#42;Historical proposal:&#42;&#42; Nature is described here through a constrained-optimization interpretation, not an established universal law.</code> | กฎ driven/inertial และ extended availability ไม่เท่ากับ universal Omega minimization; คง Value formula เดิม | §25.2–5 (working-only) / [foundation decision](07_artifacts/gates/uet_foundation_compatibility_decision.json) |
| Multi-Domain Interpretation introduction | <code>C และ I มีความหมายต่างกันในแต่ละ domain — แต่สมการเดียวกัน:</code> | <code>C และ I ในตารางเดิมเป็น lane-specific interpretations ของ shared template; ยังไม่มีหลักฐานว่าทุก domain เป็นสมการกายภาพเดียวกัน:</code> | shared template ไม่ทำให้ unit/ontology/kinetics/observable ทุก domain เท่ากัน | §25.2–5 (working-only) / [foundation decision](07_artifacts/gates/uet_foundation_compatibility_decision.json) |
| Validator Scripts introduction | <code>These scripts ensure the engine adheres to fundamental physics limits &#40;Axiom 11&#41;:</code> | <code>These scripts check declared internal conditions &#40;historically grouped under Axiom 11&#41;; they do not establish complete physical validation or override the foundation gates:</code> | internal checks ไม่แทน F0–F8 หรือ override parent blocker | §25.2–5 (working-only) / [foundation decision](07_artifacts/gates/uet_foundation_compatibility_decision.json) |
