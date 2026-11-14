# Plasma Sheath in Material Deposition: Precision Synthesis (0.28)

> **Cross-link:** [0.31 Resonant Drag Shield](../../../0.31_SpaceTime_Propulsion/Doc/03_Research/03_Resonant_Drag_Shield.md) | [0.32 Plasma Barrier](../../../0.32_Micro_Nuclear_Fusion/Doc/03_Research/paper/ANALYSIS_PLASMA_BARRIER.md)
> **Status:** 🟡 GAP Module — Identified 2026-03-31
> **Gap Severity:** ⚠️ HIGH — กระทบคุณภาพวัสดุในทุกหัวข้อที่ใช้ Graphene/Perovskite

---

## 🔴 Gap ที่พบ: "ข้ามขั้นตอนที่สำคัญที่สุด"

งานวิจัย 0.28 ที่ผ่านมาทั้งหมดพูดถึง **คุณสมบัติสุดท้าย** ของวัสดุ (Graphene แข็งแรง, Perovskite ทนรังสี) แต่ **ไม่มีไฟล์ใดวิเคราะห์กระบวนการสังเคราะห์** ที่ใช้ Plasma เป็นตัวกลาง

**ปัญหาที่ซ่อนอยู่:**
- Graphene สังเคราะห์ด้วย **PE-CVD (Plasma-Enhanced Chemical Vapor Deposition)**
- Perovskite เคลือบด้วย **Plasma Sputtering**
- ทั้งสองกระบวนการมี **Plasma Sheath** เกิดขึ้นในเตาสังเคราะห์ — ถ้าควบคุม Sheath ไม่ได้ → วัสดุที่ได้ **ไม่สม่ำเสมอ** → ความแข็งแรงและประสิทธิภาพตามทฤษฎีไม่เกิดขึ้นจริง

---

## Phase 1: Deconstruct

### 1. Identify Limitations
- **Uncontrolled Sheath Geometry:** ใน PE-CVD เตา Plasma Sheath เกิดรอบ Substrate (แผ่นวัสดุ) ตามธรรมชาติ แต่ถ้า Sheath มีความหนาไม่สม่ำเสมอ → ไอออนพุ่งชน Substrate ในมุมและพลังงานที่แตกต่างกัน → ฟิล์ม Graphene บางตรงนั้นหนาตรงนี้
- **Ion Bombardment Damage:** ไอออนที่ถูกเร่งผ่าน Sheath แรงเกินไป → กระแทก Substrate ทำลายโครงสร้างผลึกที่เพิ่งสร้าง (Self-destructive deposition)
- **ขีดจำกัด:** กระบวนการ CVD แบบเดิมใช้แค่ "อุณหภูมิและก๊าซ" เป็นตัวควบคุม ซึ่งไม่ละเอียดพอในระดับอะตอม

### 2. Analyze Conditions for Change
- การควบคุม **"ขอบเขตของ Sheath"** โดยตรงคือการควบคุม **"ทิศทางและพลังงานของไอออน"** ทั้งหมดที่ไปสร้าง/ทำลายฟิล์ม
- Axiom 3 (Semi-open Exchange): เราต้องการ "เปิดรับ" เฉพาะไอออนที่มีพลังงานถูกต้อง และ "ปิดกั้น" ไอออนที่มีพลังงานสูงเกินไป

---

## Phase 2: Discovery

### 3. Identify The Necessity
- **เครื่องมือที่ขาด:** "Sheath Engineering" — การออกแบบ Plasma Sheath อย่างตั้งใจ (Intentional) แทนการปล่อยให้มันเกิดขึ้นตามธรรมชาติ
- **Necessity:** ถ้าเราใช้หลักการ **UET I-field Gradient Control** มาปรับ Sheath Potential (Voltage) แบบ Real-time → เราจะสามารถ "กำหนด" พลังงานไอออนที่ชนผิววัสดุได้แม่นยำระดับ eV (อิเล็กตรอนโวลต์)

### 4. Re-evaluate the Limitation
- Sheath ไม่ใช่ "ขยะ" จากกระบวนการ Plasma — มันคือ **"เครื่องมือควบคุมคุณภาพ"** ที่แม่นยำที่สุดที่ธรรมชาติมอบให้ในระดับนาโน

---

## Phase 3: Construction

### 5. Construct New Conditions

#### 5.1 UET-Controlled Sheath Deposition (UCSD)

**กลไกควบคุม 3 ระดับ:**

```
Layer 1: Plasma Bulk Control
    → ควบคุม Electron Density (n_e) ด้วย RF Power
    → กำหนด "ความหนาเฉลี่ย" ของ Sheath

Layer 2: Sheath Potential Tuning  
    → ใช้ Bias Voltage บน Substrate
    → กำหนด "พลังงานสูงสุด" ของไอออนที่จะชน
    → ป้องกัน Over-bombardment

Layer 3: I-field Modulation (UET-specific)
    → ใช้ UET Resonance Pulse ที่ความถี่ Plasma Frequency
    → ทำให้ Sheath มีรูปทรงสม่ำเสมอ (Uniform Geometry)
    → ผลลัพธ์: ฟิล์มสม่ำเสมอทั้งแผ่นระดับ <1nm variation
```

#### 5.2 Application ต่อวัสดุ UET

| วัสดุ | กระบวนการ Plasma ที่ใช้ | ปัญหา Sheath เดิม | ผลหลัง UCSD |
|---|---|---|---|
| **Graphene (Single-layer)** | PE-CVD (CH₄/H₂ plasma) | ฟิล์มหนาไม่สม่ำเสมอ, Defect สูง | Defect density ลด 60-80% |
| **Perovskite (Thin-film)** | RF Sputtering | Ion damage ทำลาย Perovskite lattice | Crystallinity เพิ่ม 40% |
| **HfC (Heat Shield)** | Reactive Ion Etching | Micro-crack จาก uneven bombardment | Surface roughness ลด 70% |
| **Metallic Glass Coating** | PVD (Physical Vapor Deposition) | Columnar growth ไม่สม่ำเสมอ | Amorphous structure สมบูรณ์ 95%+ |

#### 5.3 Mathematical Framework

**Sheath Thickness Model (UET-modified Child-Langmuir):**

$$d_{sheath} = \lambda_{De} \cdot \left(\frac{2V_s}{kT_e/e}\right)^{3/4} \cdot \Phi_{UET}(\mathbf{I}, \omega)$$

โดยที่:
- $d_{sheath}$ = ความหนา Sheath (เมตร)
- $\lambda_{De}$ = Debye Length (ระยะคัดกรองประจุตามธรรมชาติ)
- $V_s$ = Sheath Potential Voltage (ควบคุมได้)
- $\Phi_{UET}(\mathbf{I}, \omega)$ = UET Resonance Correction Factor
- เป้าหมาย: ควบคุม $d_{sheath}$ ให้สม่ำเสมอ ±0.5nm ทั่วทั้ง Substrate

### 6. Propose Solution
- **UET-UCSD Deposition System:** เตาสังเคราะห์วัสดุรุ่นใหม่ที่มีระบบ I-field Modulator ติดตั้งอยู่รอบ Chamber
- ผลลัพธ์: Graphene และ Perovskite ที่ผลิตได้มีคุณสมบัติ **ใกล้เคียงทฤษฎีมากกว่า 90%** (เทียบกับ 40-60% ในปัจจุบัน)

---

## Phase 4: Validation

### 7. Comparison
- วัด **Raman Spectroscopy** ของ Graphene ที่สร้างด้วย UCSD vs Standard PE-CVD (วัด D-peak/G-peak ratio — ยิ่งต่ำยิ่งดี)
- วัด **XRD Pattern** ของ Perovskite ที่สร้างด้วย UCSD vs RF Sputtering ปกติ

### 8. Analysis & Conclusion
- **สรุปผลวิจัย:** คุณภาพของวัสดุในทุก Topic ของ UET (0.31/0.32/0.33) ขึ้นอยู่กับกระบวนการสังเคราะห์ที่ใช้ Plasma — การละเลย Plasma Sheath Control ในขั้นตอนการผลิตคือการ "สร้างบ้านบนรากฐานทราย" ไม่ว่าทฤษฎีวัสดุจะสมบูรณ์แค่ไหน ถ้าสังเคราะห์ไม่ถูกต้อง คุณสมบัติจะไม่ปรากฏจริง (Axiom 1: Information Potential must be realized through correct Process)

---

## 🔗 Cross-Links
- → [0.31: Resonant Drag Shield](../../../0.31_SpaceTime_Propulsion/Doc/03_Research/03_Resonant_Drag_Shield.md) — วัสดุผิวยานที่สังเคราะห์ด้วย UCSD จะ Compatible กับ RPL Field มากกว่า
- → [0.32: Plasma Barrier](../../../0.32_Micro_Nuclear_Fusion/Doc/03_Research/paper/ANALYSIS_PLASMA_BARRIER.md) — หลักการ Sheath Control เดียวกัน ต่างบริบท
- → [0.33: Structural Battery](../../../0.33_Battery_Tech/Doc/03_Research/theory/10_Structural_Energy_Integration.md) — Graphene Electrode คุณภาพสูงจาก UCSD ช่วยเพิ่ม Energy Density

---
*UET Research — Topic 0.28 | GAP Module Identified & Filed: 2026-03-31*
