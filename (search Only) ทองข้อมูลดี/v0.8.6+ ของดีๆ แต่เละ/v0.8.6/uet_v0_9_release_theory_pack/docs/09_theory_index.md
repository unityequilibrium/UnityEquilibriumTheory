# UET Theory Index (for Public Repo) — Draft v0.1
Date: 2025-12-19

> จุดประสงค์: ทำ “ดัชนีทางทฤษฎี” ให้คนรีวิว/อ้างอิงได้  
> โดยไม่บังคับให้เริ่มจากสมการลึกทันที  
> โครงนี้จัดตาม “Iceberg Layers” (A→D)

---

## 0) How to use this index
- ถ้าคุณเป็น “ผู้ใช้ harness”: อ่าน **Layer A** ก่อน
- ถ้าคุณต้องการเชื่อมกับหน่วย/ข้อมูลจริง: ไป **Layer B**
- ถ้าคุณรีวิวความสอดคล้องเชิงคณิต: ไป **Layer C**
- ถ้าคุณสนใจ bridge program (Thermo/Info/Quantum/Einstein): ดู **Layer D** เป็น test plan

---

## Layer A — Simulation-first (สิ่งที่รันได้)
### A1) Harness pipeline & artifacts
- Matrix → run_suite → validators → aggregate → phase maps
- Artifacts: UET_final_summary.csv, phase_prob.csv, Strength heatmaps

**เอกสารที่ควรอยู่ใน repo:**
- `docs/01_quickstart.md`
- `docs/03_matrices_and_sweeps.md`
- `docs/04_validators.md`
- `docs/05_outputs_and_interpretation.md`

### A2) Reference model (field + RHS + constraints)
- นิยาม state fields (C,S,I) บน grid
- RHS มี drive/linear/cubic/laplacian และมี constraint projection (เช่น S ≥ 0, 0 ≤ I ≤ S)

**ไฟล์อ้างอิง (แนะนำวางใน `theory/`):**
- `theory/UET_Merged_2025-12-16_0.8.3.md` (reference equations/implementation notes)

---

## Layer B — Units & Calibration (ต้องทำเมื่อจะ claim เชิงหน่วย)
### B1) Units table + normalization map
- ประกาศ units ของตัวแปร/พารามิเตอร์
- ประกาศ normalization เพื่อ map data → dimensionless fields (Layer A)

**ไฟล์อ้างอิง:**
- `theory/UET_Merged_2025-11-26_Framework.md` (Dimensional map / consistency notes)

---

## Layer C — Formal Ω, Dynamics, Stability (รีวิวเชิงคณิต)
### C1) Ω-functional & boundedness conditions
- เงื่อนไขพารามิเตอร์ที่ทำให้ Ω “ไม่ระเบิด” และใช้เป็น Lyapunov ได้ (ตัวอย่าง: δ>0, κ>0)
- นิยาม decomposition ของ Ω (local + gradient + coupling)

**ไฟล์อ้างอิง:**
- `theory/UET_Merged_2025-12-08_0.7.md` (boundedness / parameter conditions)

### C2) Projected gradient flow (classical)
- Dynamics แบบ projected gradient flow บน manifold/constraints
**ไฟล์อ้างอิง:**
- `theory/UET_Merged_2025-12-16_0.8.3.md`

### C3) Lyapunov proof report
- รายงานพิสูจน์ monotonicity ของ Ω_tot ภายใต้เงื่อนไขที่กำหนด
**ไฟล์อ้างอิง:**
- `theory/UET_Merged_2025-12-10_0.8.2_B5_Lyapunov_proof_report.md`

---

## Layer D — Bridge Program (Thermo → Info → Quantum → Einstein)
> หมวดนี้ “ยังไม่ควร claim ว่าเสร็จ” ให้เขียนเป็น test plan:
- limiting cases
- measurable predictions
- falsifiable signatures

**ไฟล์อ้างอิง (roadmap):**
- `theory/UET_Merged_2025-11-26_Framework.md` (Ω-equation/tensor sketch)
- `theory/UET_Merged_2025-11-26_Physics_Objective_Raw.md`
- `theory/UET_Merged_2025-11-26_Chat_Physics_Objective_Raw.md`

---

## 1) Recommended repo placement
แนะนำให้วางไฟล์ทฤษฎีไว้ที่:
- `theory/`  (ไฟล์ merged และรายงาน proof)
แล้วทำ links จาก docs มา

---

## 2) Theory files detected in your workspace
รายการไฟล์ที่พบใน environment ตอนนี้ (คุณสามารถคัดเข้า `theory/`):

- UET_0_8_2_repo_scaffold.zip
- UET_Merged_2025-11-26_Before_Equation.md
- UET_Merged_2025-11-26_Chat_Physics_Objective_Raw.md
- UET_Merged_2025-11-26_Framework.md
- UET_Merged_2025-11-26_Physics_Objective_Raw.md
- UET_Merged_2025-12-08_0.3.md
- UET_Merged_2025-12-08_0.4.md
- UET_Merged_2025-12-08_0.5.md
- UET_Merged_2025-12-08_0.6.md
- UET_Merged_2025-12-08_0.7.md
- UET_Merged_2025-12-08_0.8.0.md
- UET_Merged_2025-12-08_0.8.1.md
- UET_Merged_2025-12-10_0.8.2_B5_Lyapunov_proof_report.md
- UET_Merged_2025-12-16_0.8.3.md
- UET_Merged_2025-12-16_0.8.4.md
- UET_Merged_2025-12-16_0.8.5.md
- 0.8.5+.md
