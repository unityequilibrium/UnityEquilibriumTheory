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

## 2026-11-10 — Is layer 1 complete, and can it break from inside? (A2 + B1)
ทำ: derive metric equation ส่วน off-diagonal (13 test), derive การแลกเปลี่ยนสสาร ⇄ φ (10 test), โจมตี vacuum/ghost/ขอบล่าง (32 test), mutation test 8 ตัว
ผล: Q = ½εh|χ|²∇φ ผ่าน portal เท่านั้น; vacuum เลื่อนไปที่ ψ₀ ≈ g_c X_c/(2m_ψ²) ≠ 0 ได้เมื่อ χ condense หรือเมื่อ λ_χ เล็ก ทำให้ γ ≠ 1; จับ mutant จริงได้ 7/7; ผู้เขียนเลือกความหมายข้อ 3 = Λ_eff > 0
ระดับ: C_PARENT_EOM_DERIVED ครอบคลุม off-diagonal แล้ว (L1); claim ใหม่ C_EXCHANGE_DERIVED, C_VACUUM_SHIFT_ROUTE (L1)
ถัดไป: ผู้เขียนตอบว่า χ คือสสารธรรมดาหรือไม่; A3 สมการชั้น 2
commit: this commit + records commit

## 2026-11-10 — If χ is ordinary matter, what force does the portal make? (B1b)
ทำ: ผู้เขียนตัดสินว่า χ = สสารธรรมดา จึง derive แรงที่ portal สร้างระหว่างมวล (5 physics test: NR limit, sphere ODE ลู่เข้าอันดับ 2, อัตราส่วนต่อแรงโน้มถ่วง)
ผล: Yukawa α = g_c²/(2κm_χ⁴), λ = 1/m_ψ ไม่ขึ้นกับชนิดสาร; α = 1 ต้องการแค่ g_c ≈ 5×10⁻¹⁰ eV; ทาง χ condense ถูกตัด; T001 ใช้ได้เมื่อ portal α ≪ 1 เท่านั้น
ระดับ: claim ใหม่ C_PORTAL_FIFTH_FORCE (L1)
ถัดไป: ร่าง Test Card T005 (inverse-square law, LLR, ดาวเคราะห์) ให้ผู้เขียนอนุมัติก่อนรัน
commit: this commit + records commit

## 2026-11-10 — How strongly do fifth-force data limit the portal? (T005 draft)
ทำ: ร่าง Test Card T005 (CONSTRAINT) พร้อมข้อมูลสองจุดที่ล็อก hash แล้ว (Lee et al. 2020: |α| = 1 ถูกตัดที่ λ ≥ 38.6 μm; Merkowitz 2010 LLR: α < 5.9×10⁻¹¹ ที่ λ = a/2) และสคริปต์แปลงเป็น g_c_max
ผล: ยังไม่รัน; เปิดเผยแล้วว่าผลประมาณรู้ล่วงหน้า (g_c ≲ 5×10⁻¹⁰ eV ระยะสั้น, ≲ 4×10⁻¹⁵ eV ที่ระยะดวงจันทร์)
ระดับ: claim C_T005_PORTAL_G_C ที่ L0 (DRAFT)
ถัดไป: ผู้เขียนอนุมัติ หรือกำหนด g_min เพื่อให้ T005 ฆ่าทฤษฎีได้จริง; ตรวจตัวเลขกับฉบับวารสาร
commit: this commit

## 2026-11-10 — T005 run: portal coupling versus fifth-force data
ทำ: รันวิธีของ T005 หลังผู้เขียนอนุมัติการ์ด (2b4985485) กับข้อมูล T005_YUKAWA_BOUNDS ที่ล็อก hash ไว้
ผล: PASS แบบ CONSTRAINT: g_c < 5.1×10⁻¹⁰ eV (m_ψ ≤ 5.1×10⁻³ eV), g_c < 3.9×10⁻¹⁵ eV (m_ψ ≈ 1.0×10⁻¹⁵ eV); ช่องแลกเปลี่ยนของข้อ 2 แรงได้เฉพาะเมื่อ ψ หนัก
ระดับ: C_T005_PORTAL_G_C → L2_CONFRONTED (CONSTRAINT; ผู้เขียนอนุมัติ)
ถัดไป: A3 สมการชั้น 2; ตรวจตัวเลข T001/T002/T005 กับฉบับวารสาร
commit: this commit

## 2026-11-10 — Does an open system emerge from a closed one? (A3 layer 2)
ทำ: mode + สิ่งแวดล้อม 150–600 oscillator เป็นระบบปิดทั้งก้อน (Caldeira–Leggett) แล้วดูเฉพาะ mode (8 physics test)
ผล: แรงเสียดทาน ลู่เข้าอันดับ 1; พลังงานที่เสีย/∫P dt = 1.0002; noise+KMS เกิดเอง ⟨v²⟩/T = 0.97; ความร้อนไหลร้อน→เย็น; F ลดแบบ exponential (P ∝ F) ซึ่งขัดกับ P คงที่ของชั้น 3
ระดับ: claim ใหม่ C_LAYER2_OPEN_FROM_CLOSED (L1)
ถัดไป: A4 แก้ τ = F/P ให้ครอบคลุมทั้งแบบคุมอัตราเผาและแบบ passive; ระบุว่าสิ่งแวดล้อมคือสนามไหนใน parent action
commit: this commit + records commit

## 2026-11-10 — Does selection survive the real burn law, and is there a Nash equilibrium? (A4)
ทำ: แทน τ = F/P ด้วย τ = ∫dF/P(F) จากชั้น 2; จำลองการแข่งขันด้วยอายุคงที่จริงข้ามกฎการเผา 3 แบบ; ทรัพยากรสองชนิด + ผู้บุกรุก 4 แบบ (13 physics test)
ผล: R* ต่ำสุดยังชนะ (R = 0.2674 เทียบ 0.2670) แต่กฎ F₀/P₀ เดิมทำนายผู้ชนะผิดเมื่อมีระบบ passive; สองทรัพยากรให้ดุลยภาพผสม R* = (0.4375, 0.3125) ที่เป็น Nash (4/4); บิต ∝ F·P^(−1/4) สำหรับวัตถุดำ
ระดับ: claim ใหม่ C_L3_BURN_LAW_SELECTION (L1)
ถัดไป: B4 หาข้อทำนายที่ต่างจากฟิสิกส์มาตรฐาน; B5 red-team
commit: this commit + records commit

## 2026-11-10 — Does UET predict anything standard physics does not? (B4)
ทำ: เทียบทุกชั้นกับทฤษฎีที่มีอยู่ (ชั้น 3 = chemostat consumer–resource ของ Tilman ตรงตัว, sympy) แล้ว derive ผลที่เกิดเฉพาะเมื่อรวมชั้น 1+2 (6 physics test)
ผล: แต่ละชั้นลดรูปเป็นทฤษฎีมาตรฐาน; ผลข้ามชั้นเดียวที่หาได้คือ portal drag F = Γvq²/(12πR) เทียบกับ frame พิเศษ แต่มีพารามิเตอร์อิสระ 3 ตัว จึงยังไม่มีการทำนายเชิงตัวเลขที่ต่าง
ระดับ: claim ใหม่ C_B4_DISTINCTNESS_AUDIT (L1)
ถัดไป: ผู้เขียนผูกค่าต่ำสุดของ g_c หรือ Γ จากตรรกะ หรือระบุระบบ autocatalytic; B5 red-team
commit: this commit + records commit

## 2026-11-10 — How strongly does energy use write onto space? (R1 + T006 draft)
ทำ: คำนวณสองช่องที่ฟิสิกส์มาตรฐานมีอยู่แล้ว: แรงโน้มถ่วง (มวลที่เผาไปทำให้ GM ลดและวงโคจรขยาย) และ entropy ของรังสี (4L/3T); 5 physics test (Planck → s/u = 4/3T, วงโคจรขยายแบบ 1/GM); ร่าง Test Card T006 เทียบกับการวัด d(GM☉)/dt จาก MESSENGER
ผล: ดวงอาทิตย์เขียนบิตผ่านรังสีราว 9×10⁴⁵ บิต/วินาทีที่ผิว; T006 ยังไม่รัน เปิดเผยแล้วว่าประมาณการด้วยมือได้ z ราว 1.5
ระดับ: claim C_T006_ENERGY_USE_GRAVITY_TRACE ที่ L0 (DRAFT)
ถัดไป: ผู้เขียนอนุมัติ T006; ทำ R2
commit: this commit

## 2026-11-10 — Is there a non-living physical system that layer 3 governs? (R2)
ทำ: เทียบสมการอัตราของเลเซอร์หลาย mode กับชั้น 3 (sympy) และจำลองแบบโฟตอนรั่วออกแบบ exponential (3 physics test)
ผล: ตรงทุกเทอม (a = B, τ = อายุโฟตอน, F = 1, R = inversion); R* = threshold inversion; inversion ก้อนเดียว → mode threshold ต่ำสุดชนะและ gain clamping; สองบริเวณ → สอง mode อยู่ร่วมกัน
ระดับ: claim ใหม่ C_R2_LASER_LAYER3 (L1)
ถัดไป: ผู้เขียนอนุมัติ T006; B5 red-team
commit: this commit + records commit

## 2026-11-10 — T006 run: the Sun's energy use in its gravity
ทำ: รันวิธีของ T006 หลังผู้เขียนอนุมัติการ์ด (72d072c86) กับข้อมูล T006_SOLAR_MASS_LOSS ที่ล็อก hash ไว้
ผล: คำนวณ −8.76×10⁻¹⁴/ปี เทียบวัด −6.13×10⁻¹⁴/ปี, z = 1.48 → PASS; "ไม่ทิ้งร่องรอยทางแรงโน้มถ่วง" ถูกปฏิเสธที่ 4.2σ
ระดับ: C_T006_ENERGY_USE_GRAVITY_TRACE → L2_CONFRONTED (PASS; ผู้เขียนอนุมัติ)
ถัดไป: B5 red-team; ตรวจตัวเลข T001/T002/T005/T006 กับฉบับวารสาร
commit: this commit

## 2026-11-10 — Do the registered numbers match the published papers? (journal cross-check)
ทำ: เทียบตัวเลขภายนอกทุกตัวของ T001, T002, T005, T006 กับฉบับวารสาร/ฉบับ arXiv สุดท้ายก่อนตีพิมพ์ และตรวจการอ้างอิงงานคลาสสิก (docs/core/01_contracts/JOURNAL_CROSSCHECK_2026-11-10.md)
ผล: ไม่พบตัวเลขผิดแม้แต่ตัวเดียว ผลของ Test Card ทั้งสี่ไม่เปลี่ยน; ข้อจำกัด: CQG/PRL ฉบับเต็มติด paywall (ใช้ arXiv ฉบับก่อนตีพิมพ์), ค่าลมสุริยะเป็นค่าจากบทความทบทวนช่วง solar minimum, Statz–deMars ยังไม่ได้ตรวจ
ระดับ: ไม่เปลี่ยน claim ใด
ถัดไป: หาค่าลมสุริยะช่วง 2011–2015 ที่ตีพิมพ์แล้ว; B5 red-team; owner ตัดสินเรื่อง push
commit: this commit
