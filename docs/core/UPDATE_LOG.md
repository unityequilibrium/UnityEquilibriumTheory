# Core update log (Research Standard v2)

Format: docs/STANDARD.md section 9. Earlier Core history stays in `08_history/update_logs/`.

## 2026-11-08 — What is the parent action, and what known theory is it?
ทำ: เขียน Theory Card v1 (THEORY_CARD.md + theory_card.json) จากโค้ดเดิม พร้อม map ไปเป็นตัวแปร canonical
ผล: เป็น DEF-class scalar-tensor (ξ_c ψ² R) + O(2) portal; ε ซ้ำซ้อน; ε→0⁺ คือ strong coupling (λ_ψ→∞) โดย ξ_c และ m_ψ ไม่เปลี่ยน, ε=0 เป็นจุดเสื่อม ไม่ใช่ GR limit; sympy ยืนยัน map ได้ residual 0 (scratch, จะเข้า test ใน W4)
ระดับ: UET-PARENT-* → L0_SPECULATIVE (การ์ด DRAFT รออนุมัติ)
ถัดไป: W4 sympy derivation check ของ EOM สามชุด + test ของ canonical map
commit: (this commit)

## 2026-11-08 — Do the implemented equations follow from the action?
ทำ: sympy Euler–Lagrange ของ action ในการ์ด เทียบกับ residual ในโค้ด (scalar/matter บน metric ไม่เป็นเนื้อเดียวกันที่มีพจน์ off-diagonal; metric equation ผ่าน Bianchi I) พร้อม negative control 3 แบบ
ผล: 28/28 ผ่านที่ tolerance 1e-10 (20 จุดต่อสมการ); negative control จับ ξ ผิดเครื่องหมาย, k ผิด และ portal หายได้ทั้งหมด; พจน์ off-diagonal ของ metric equation ยังไม่ได้ตรวจ
ระดับ: C_PARENT_EOM_DERIVED, C_EPSILON_REDUNDANT → L1_CONSISTENT
ถัดไป: W5 map ξ_c, m_ψ ไปยัง DEF β₀ และ scalarization ของดาวนิวตรอน
commit: 689b56cef (tests) + this commit (records)

## 2026-11-08 — What does the parent action predict for neutron stars?
ทำ: map Jordan→Einstein frame ไปยังพารามิเตอร์ DEF (`uet_scalar_tensor_mapping.py`) + physics test 8 ตัว (Brans–Dicke limit, frame equivalence พร้อม negative control, เทียบ sympy) + รวบรวมแหล่งอ้างอิง binary pulsar
ผล: β₀ = −2ξ_c, α₀ = 0, γ−1 = 0 ที่ ψ₀ = 0; m*² = m_ψ² − 2ξ_cΛ − 4κξ_cερ*; scalarization ต้องการ ξ_c ≳ 2 (m_ψ เบา); ZFKSW22 ตัด scalarization ทิ้งที่ β₀ ∈ [−4.8, −4.0] (|α_A| ≲ 6×10⁻³)
ระดับ: C_UET_DEF_MAPPING → L1_CONSISTENT (ภายใต้สมมติฐานว่า matter ต่อแบบ minimal กับ Jordan metric)
ถัดไป: W6 ร่าง Test Card T001 (CONSTRAINT) + data manifest แล้วรอผู้เขียนอนุมัติ ต้องตัดสินใจเรื่อง mass domain และว่า ξ_c ถูกกำหนดล่วงหน้าหรือไม่
commit: 48ba3f9d4 (module+tests) + this commit

## 2026-11-09 — What exactly will binary pulsars test? (T001 draft)
ทำ: ลงทะเบียนข้อมูล ZFKSW22 (ขอบเขต DEF + P_b และมวลของ 7 ระบบ, sha256 ใน data manifest), เขียนสคริปต์วิธีคำนวณ, ร่าง Test Card T001 (CONSTRAINT) และ claim ระดับ L0; ยังไม่ได้รันการเทียบ
ผล: ยังไม่มีผล (รออนุมัติ) — เกณฑ์ล็อกไว้ว่าช่วง ξ_c ที่ถูกตัด = [−β₀max/2, −β₀min/2] และ domain ของ scalar เบา m_ψc² ≤ ħc/(10 a_max); ผู้เขียนกำหนดให้ ξ_c เป็น free ดังนั้น T001 ทำให้ทฤษฎีตกไม่ได้ ทำได้แค่จำกัดพารามิเตอร์
ระดับ: C_T001_BINARY_PULSAR_XI_C → L0_SPECULATIVE (การ์ด DRAFT)
ถัดไป: ผู้เขียนตรวจตัวเลขเทียบกับฉบับตีพิมพ์ แล้วอนุมัติ T001 จากนั้นรันสคริปต์ใน commit แยก
commit: this commit

## 2026-11-09 — Does binary-pulsar timing allow the parent action? (T001 run)
ทำ: รันวิธีของ T001 หลังผู้เขียนอนุมัติการ์ด (70e5b9d35) กับข้อมูล ZFKSW22 ที่ล็อก hash ไว้
ผล: PASS แบบ CONSTRAINT — ξ_c ∈ [2.0, 2.4] ถูกตัดทิ้งเมื่อ m_ψ ≤ 2.5×10⁻¹⁸ eV (a_max = 7.8×10⁹ m, J2222−0137); ξ_c > 2.4 และ scalar ที่หนักกว่านี้ไม่ถูกจำกัดโดย T001; ใช้ค่าจาก arXiv v2 ยังไม่ได้เทียบกับฉบับวารสาร
ระดับ: C_T001_BINARY_PULSAR_XI_C → L2_CONFRONTED (ผู้เขียนอนุมัติ 2026-11-09)
ถัดไป: หา observable ที่ UET ต่างจาก DEF (ส่วน "differences" ใน Theory Card ยังว่าง) หรือหาสิ่งที่กำหนด ξ_c ได้จาก lane อื่น
commit: this commit

## 2026-11-09 — Does selection follow from free-energy exhaustion alone? (layer 3)
ทำ: เขียน `03_lanes/persistence/uet_persistence_selection.py` ระบบหายไปเมื่อพลังงานอิสระหมด (τ = F/P) ไม่มี payoff ที่ตั้งด้วยมือ + physics test 12 ตัว
ผล: Little's law N* = bτ (ลู่เข้าอันดับ 1), replicator dynamics เป็น identity, ผู้ชนะคือ R* = P/(aF) ต่ำสุด, บิตต่อชีวิต F/(kT ln2) ไม่ขึ้นกับ P; negative control: ไม่มีการหมดทรัพยากร = ไม่มี steady state
ระดับ: C_L3_SELECTION_FORMAL → L1_CONSISTENT
ถัดไป: Test Card เทียบกับประชากรดาวฤกษ์ (สัดส่วนต่อช่วงวิวัฒนาการ ∝ อายุช่วงนั้น)
commit: cbebc3fad (model+tests) + this commit

## 2026-11-09 — Does N = b·F/P match real star counts? (T002 run)
ทำ: รันวิธีของ T002 หลังผู้เขียนอนุมัติการ์ด (50c483c4d) กับข้อมูล AYALA14_GC_R_PARAMETER ที่ล็อก hash ไว้
ผล: R_pred = 1.467 ± 0.023 (Y_HII) เทียบกับ R_obs = 1.39 ± 0.03, z = 2.05 → INCONCLUSIVE ตามเกณฑ์ที่ล็อกไว้ (ใช้ SBBN แทนได้ z = 1.25 แต่ไม่ใช้ตัดสิน) ไม่ได้รวมความคลาดเคลื่อนของแบบจำลองดาว
ระดับ: C_T002_STELLAR_PHASE_ABUNDANCE → L2_CONFRONTED (INCONCLUSIVE; ผู้เขียนอนุมัติ)
ถัดไป: หาค่าความคลาดเคลื่อนของแบบจำลองดาวที่ตีพิมพ์แล้ว หรือหาประชากรอื่นที่เป็นอิสระ ก่อนสรุปเรื่องช่องเผาพลังงานที่ซ่อนอยู่
commit: this commit

## 2026-11-10 — Do the equations say what the author means? (A1 fidelity matrix)
ทำ: จับคู่ตรรกะ 10 ข้อใน AUTHOR_PROPOSITION กับสมการและโค้ด ให้คำตัดสินข้อละหนึ่งค่า (docs/core/FIDELITY_MATRIX.md)
ผล: MATCH 1, PARTIAL 4, ASSUMED 2, MISSING 1, CONTRADICTS 1 (ข้อ 3: vacuum สถิตเป็นคำตอบเมื่อ Λ_eff = 0; test_fidelity_static_vacuum.py 40 ผ่าน) เจอ residual ที่เป็น 0 โดยนิยาม 2 จุด (KMS noise, exchange ledger)
ระดับ: ไม่เปลี่ยน claim ใด (เป็นงานตรวจ ไม่ใช่ข้ออ้างใหม่)
ถัดไป: ผู้เขียนเลือกความหมายของข้อ 3; ต่อด้วย A2+B1 (off-diagonal, reduction, stability, ψ₀ ในสสาร)
commit: this commit
