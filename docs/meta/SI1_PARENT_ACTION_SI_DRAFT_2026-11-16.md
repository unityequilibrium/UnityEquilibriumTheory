# SI-1: ชั้นหน่วย SI ของสมการแกน (ร่างให้ผู้เขียนตรวจ, 2026-11-16)

สถานะ: ส่วน derivation ทำแล้ว (L1, `R_SI1_PARENT_ACTION_SI`) ส่วนการเทียบข้อมูลยังเป็น**ร่าง**
ยังไม่มี Test Card ที่อนุมัติ และยังไม่ได้รันเทียบกับข้อมูลใด ๆ ทุกอย่างที่เขียนว่า "AI เลือก" ไม่ใช่ข้อกำหนดของทฤษฎี

## 1. ทำไม topic 13 ติด

- Topic 13 ใช้ Φ แบบ normalized (ไม่มีหน่วย) แล้วต้องหาค่า scale มาแปลงเป็น SI (`Z_Φ`, `κ_E`, `e0`)
- ใน lane He-4 ค่าเหล่านี้ได้จากการ**calibrate และตั้ง convention** (`e0 = n k_B T0`, `Z_Φ = −0.0175` จากข้อมูล
  superfluid fraction) ไม่ได้มาจากสมการ (`t13_he4_o2_si_beta_mapping_audit.json` เขียนไว้เองว่า "not a first-principles prediction")
- ใน lane graphite ต้องใช้ข้อมูล Ding ที่ไม่เปิดเผย จึงติดถาวร
- สมการแกนใน standard v2 (`core/THEORY_CARD.md` §3) ไม่ได้ใช้ Φ ตัวนั้น แต่ใช้ ψ และ χ ที่มีหน่วยจริงอยู่แล้ว
  ไม่มีใครเขียนสะพานระหว่างสองอย่างนี้ นี่คือจุดที่ไม่ sync กัน

## 2. สิ่งที่ SI-1 derive ได้แล้ว (L1)

โค้ด: `core/03_lanes/open_system/uet_si_bose_fluid.py` ทดสอบ: `core/05_tests/physics/test_si_bose_fluid.py` (3 physics tests ผ่าน)

1. **ไม่มี energy reference ที่เลือกได้อิสระ** parameter ของ action มีหน่วย mass (m, m_ψ, g_c เป็น eV) เมื่อกำหนดว่า χ คืออนุภาคอะไร
   การแปลงเป็น SI ใช้แค่ ħ, c (และ k_B ถ้ามีอุณหภูมิ) ปัญหา "เลือก E_ref" ของ topic 13 เกิดจาก Φ แบบ normalized เท่านั้น
2. **ภาค χ คือ Bose fluid แบบ O(2)** ใน non-relativistic limit มันคือ Gross–Pitaevskii โดย `λ = 8π a m`
   (a = scattering length) ความเร็วเสียงแบบ relativistic `c_s² = (μ²−m²)/(3μ²−m²)` ลดลงเป็น Bogoliubov `√(gn/m)` (ทดสอบแล้ว error ลดลงตาม gn/m)
3. **ψ เพิ่มอะไร** การแลก ψ ระหว่าง nucleon คือ Yukawa ของ T005 ในของไหลมันเลื่อน scattering length ไป
   `δa = −α G M³ / m_ψ²`
   ที่ขอบ T005 (α ≈ 1, m_ψ = 5.1e-3 eV): Rb-87 `δa/a = −5e-18`, He-4 `δa = −2.6e-30 m` วัดไม่ได้
4. **He II อยู่นอกขอบเขตของ action ที่ tree level** แม้ใช้ hard core 2.6 Å ก็ได้ `n a³ = 0.38` (ด้วย scattering length จริงราว 100 Å ได้ราว 10⁴)
   GP ให้ความเร็วเสียง 134 m/s ขณะที่ first sound ที่วัดได้ที่ 1.70 K คือ 233.1 m/s (Donnelly & Barenghi 1998; เดิมเขียนราว 238 จากความจำ แก้แล้ว) ดังนั้น**action ไม่ได้ให้การจับคู่ Φ = superfluid fraction ของ lane He-4 เดิม**
   ของไหล He II เป็นระบบ strongly correlated ต้องใช้ closure แยก (Landau two-fluid) ซึ่งไม่ได้มาจาก action

ข้อสังเกตเรื่อง lane (AI inference): T005 ใช้ χ = nucleon ถ้าให้ χ = อะตอมทั้งตัวแทน แรงจาก ψ จะไม่แปรตามมวล
และจะชนกับการทดสอบ equivalence principle ทันที ดังนั้น lane ที่สอดคล้องคือ χ = nucleon และ order parameter ของ He II เป็น O(2) ตัวใหม่ที่เกิดขึ้นทีหลัง (emergent) ไม่ใช่ χ เอง
ตรงกับที่ Theory Card §7 เขียนไว้ว่า "charge-to-atom identity ยังเปิดอยู่"

## 3. ความหมายต่อ topic 13 (ข้อเสนอของ AI ให้ผู้เขียนตัดสิน)

- ช่องทาง "declared dimensionful action origin" ที่ topic 13 รออยู่ **ตอบได้แล้ว แต่คำตอบไม่ช่วยปลดล็อก**:
  action ให้ SI ได้เต็มที่ แต่สิ่งที่มันทำนายใน He-4 หรือ graphite คือผลของ ψ ที่เล็กกว่า 10⁻¹⁷ ส่วน Φ ของ topic 13 เป็นตัวแปร phenomenological คนละตัว
- ทางเลือก:
  - **(ก)** บันทึก lane Φ ของ topic 13 ว่าเป็น phenomenological closure (ไม่ใช่ตัวแปรของ action) แล้วหยุดไล่ data package ของ graphite
  - **(ข)** ถ้าผู้เขียนตั้งใจให้ Φ ของ topic 13 คือ "response ของ space" จริง ต้องมีเทอมใหม่ใน action ที่ต่อ ψ กับ entropy หรืออุณหภูมิของสสาร (ชั้น 2) ซึ่งยังไม่มี
    นี่คือคำถามเดียวกับ dissipative sector ที่ Theory Card §4 บอกว่ายังเปิดอยู่
- สิ่งที่ SI-1 ไม่ได้แตะ: ไฟล์ของ topic 13, gate และ status เดิม (Codex กำลังซ่อม path อยู่ใน checkout หลัก)

## 4. ร่าง Test Card สำหรับคุยกัน (ยังไม่สร้างไฟล์, ยังไม่รัน)

| ตัวเลือก | สิ่งที่เทียบ | ข้อมูล (AI เสนอ, ยังไม่ได้ดึง) | ทดสอบอะไรจริง ๆ |
|---|---|---|---|
| **S1** ชั้น SI ของ χ end-to-end | ความเร็วเสียง Bogoliubov ใน BEC ที่ใช้ a จากการวัดอิสระ | Andrews et al. 1997 (Na, PRL 79, 553) หรือชุดที่ใหม่กว่า | การแปลงหน่วยและ λ = 8πam ทำงานกับข้อมูลจริง ไม่ใช่ UET-distinct ฟิสิกส์มาตรฐานก็ผ่านแบบเดียวกัน |
| **S2** ขอบเขต He II | n a³ และความเร็วเสียง tree level เทียบกับที่วัดได้ | Donnelly & Barenghi 1998 (topic 13 ใช้อยู่แล้ว) และ He-He scattering length จาก Grisenti et al. 2000 | ยืนยันว่า He II อยู่นอกขอบเขตของ action ผลที่คาดคือ FAILED สำหรับ lane นี้ ต้องบันทึกตรง ๆ |
| **S3** ψ ในของไหล | ขอบบน δa จากความแม่นยำของ scattering length หรือ Feshbach | ข้อมูล precision spectroscopy ของ Rb/Cs | ได้ขอบเขตของ g_c ที่อ่อนกว่า T005 มาก จึงไม่น่าทำ |

ข้อเสนอ: S2 ตรงกับปัญหา topic 13 ที่สุด ส่วน S1 เป็น sanity check ของชั้น SI
ก่อนอนุมัติต้องตกลงกันว่าจะใช้ค่าตัวเลขไหนและตัวเลขเกณฑ์ pass/fail เท่าไร และผู้เขียนเป็นคนอนุมัติ

## 5. ผู้เขียนเลือก S2 (2026-11-16)

ร่าง Test Card อยู่ที่ `docs/standard/tests/T015.json` (DRAFT ยังไม่ได้รัน) ข้อมูลอยู่ที่ `docs/data/external/condensed_matter/helium4/he_ii_tree_level_inputs.csv`
