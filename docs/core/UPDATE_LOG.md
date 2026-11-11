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

## 2026-11-10 — What is the trace that energy use leaves? (R3)
ทำ: ผู้เขียนอธิบายว่าร่องรอยอาจเป็นแค่ตัวเลข/ความต่างศักย์; คำนวณแม่นตรงในระบบปิดของ A3 ว่า Σ = I(S:R) + D(R‖eq) (Esposito et al. 2010) (5 physics test)
ผล: เอกลักษณ์ถูกต้องถึง 10⁻¹⁰; ระยะยาว D (ความต่างศักย์ในสิ่งแวดล้อม) > 90% ของ Σ; สสารที่เย็นกว่าให้ Q < 0 แต่ I > 0 จึงต้องใช้ บิต = Σ/ln2 แทน Q/(kT ln2); ลู่เข้าสูตร x − 1 − ln x แบบอันดับ 1
ระดับ: claim ใหม่ C_R3_TRACE_RECORD_PLUS_POTENTIAL (L1); ข้อ 8 และ 9 → MATCH
ถัดไป: B5 red-team; owner ตัดสินเรื่อง push/merge
commit: this commit + records commit

## 2026-11-10 — Are the borrowed principles used correctly, and do they compose? (synthesis audit)
ทำ: ตรวจหลักการ 9 ข้อที่ UET ยืมมา เทียบเงื่อนไขของต้นฉบับกับวิธีที่ UET ใช้ และตรวจการต่อกัน 4 คู่ (docs/core/SYNTHESIS_AUDIT.md)
ผล: ใช้ถูก 4, ต้องแก้ 2 (กฎข้อ 2 ของข้อ 1; สูตร Landauer กลับด้าน), จำกัดขอบเขต 3 (τ = F/P, R*, Nash); ขัดกันหนึ่งคู่: ระบบที่มีแรงโน้มถ่วงสร้างโครงสร้างเพิ่มในระบบปิด (Lynden-Bell & Wood 1968)
ระดับ: ไม่เปลี่ยน claim (เป็นงานตรวจตรรกะ)
ถัดไป: ทาง ก — Test Card ต่อสาขา (เลเซอร์, เคมี, chemostat, ดาวแคระขาว) ให้ผู้เขียนอนุมัติทีละใบ
commit: this commit

## 2026-11-10 — Author accepts the point-1 fix
ทำ: ผู้เขียนรับการแก้ข้อ 1 ตาม SYNTHESIS_AUDIT C1
ผล: ข้อ 1 กลายเป็น "โครงสร้างที่ต้องเผาพลังงานเพื่อคงอยู่ต้องเปิด" (แรงโน้มถ่วงสร้างโครงสร้างในระบบปิดได้เอง) บันทึกใน AUTHOR_PROPOSITION ข้อ 1
ระดับ: ไม่เปลี่ยน claim
ถัดไป: Test Card แรกของทาง ก
commit: this commit

## 2026-11-10 — Does layer 3 predict real two-resource competition? (T007 draft, path ก)
ทำ: ร่าง Test Card T007 เทียบการคัดสรรของชั้น 3 กับการทดลอง chemostat ของ Tilman (1977): ทำนายจากสรีรวิทยาตอนเลี้ยงเดี่ยวเท่านั้น (Table 1) ล็อก hash ข้อมูลแล้ว
ผล: ยังไม่รัน; เปิดเผยแล้วว่าเลขขอบเขตที่คำนวณด้วยมือ (86.9 และ 6.2 เทียบกับที่วัดได้ราว 80 และ 6) ทำให้รู้ผลล่วงหน้า; กลุ่ม Si/P = 38 ตรงไม่หมด
ระดับ: claim C_T007_RESOURCE_SELECTION_CHEMOSTAT ที่ L0 (DRAFT)
ถัดไป: ผู้เขียนอนุมัติ T007; Test Card สาขาถัดไป (เลเซอร์, เคมี, ดาวแคระขาว)
commit: this commit

## 2026-11-10 — T007 run: layer 3 predicts Tilman's chemostat regions
ทำ: รันวิธีของ T007 หลังผู้เขียนอนุมัติการ์ด (5d23822e4) กับข้อมูล TILMAN1977_CHEMOSTAT ที่ล็อก hash ไว้
ผล: มี trade-off (Asterionella เก่งฟอสเฟต, Cyclotella เก่งซิลิกา); ขอบที่ทำนาย 86.9 และ 6.2 เทียบที่วัดได้ราว 80 และ 6 (|log10| 0.036, 0.012) → PASS; ตรงเต็มที่ 2 ใน 3 กลุ่ม, Si/P = 38 ตรงบางส่วน
ระดับ: C_T007_RESOURCE_SELECTION_CHEMOSTAT → L2_CONFRONTED (PASS; ผู้เขียนอนุมัติ)
ถัดไป: Test Card สาขาถัดไปของทาง ก (เลเซอร์จริง, เคมี, ดาวแคระขาว)
commit: this commit

## 2026-11-10 — Path-ก batch: feasibility of all planned systems; T008 and T009 drafted
ทำ: ค้นข้อมูลระบบ T008–T018 ตามแผน; เขียนโมเดล uet_path_a_models.py (Mestel cooling เป็น passive burner n = 7/2, secular equilibrium, negative control ปฏิกิริยาขนานไม่ autocatalytic) พร้อม 3 physics test; ร่าง T008 (ดาวแคระขาว) และ T009 (U-234) พร้อมข้อมูลล็อก hash
ผล: ยังไม่รัน; T013/T014 (เลเซอร์ clamping, chemostat ขาเข้า) ยังหาข้อมูลตัวเลขเปิดไม่ได้; negative control ส่วนเคมีผ่านระดับ L1 (ไม่มีผู้ชนะเมื่อไม่ autocatalytic)
ระดับ: claim ใหม่ C_T008_*, C_T009_* ที่ L0 (DRAFT)
ถัดไป: ผู้เขียนอนุมัติ T008/T009 พร้อมกัน; หาข้อมูล T013/T014/T016 ต่อ
commit: this commit

## 2026-11-10 — T008 and T009 run: abundance law in astronomy and nuclear physics
ทำ: รัน T008 และ T009 หลังผู้เขียนอนุมัติการ์ด (8eefb40c1) กับข้อมูลที่ล็อก hash ไว้
ผล: T008 ความชันที่ทำนาย 0.286 เทียบ 0.320 (|log10| 0.049) → PASS; T009 ครึ่งชีวิต 245,670 เทียบ 244,900 ปี z = 0.56 → PASS
ระดับ: C_T008_*, C_T009_* → L2_CONFRONTED (PASS; ผู้เขียนอนุมัติ); ตารางรวมผลทาง ก อยู่ใน SYNTHESIS_AUDIT ส่วนที่ 5
ถัดไป: หาข้อมูล T013/T014/T016; push ครั้งเดียวเมื่อผู้เขียนสั่ง
commit: this commit

## 2026-11-10 — T016 dropped (star-mass negative control)
ทำ: หาข้อมูล PDMF (Bovy 2017: ความชัน 4.7 สำหรับ M > 1 M☉) และ IMF จากกระจุกอายุน้อย (Kroupa 2001)
ผล: ตัด T016 ก่อนร่างการ์ด เพราะผลแกว่งตามเลขชี้กำลัง mass–luminosity (4.8–5.9) และความไม่แน่นอนของ IMF กว้างจนการทดสอบไม่ไม่ผ่านเลย; ผู้เขียนเห็นชอบ
ระดับ: ไม่เปลี่ยน claim
ถัดไป: negative control ที่คมกว่า; หาข้อมูล T013/T014
commit: this commit

## 2026-11-10 — One map of where the core equations live (CORE_MAP)
ทำ: เขียน docs/core/CORE_MAP.md ไฟล์เดียว บอกว่าสมการหลักแต่ละชั้น โค้ด test ข้อมูล และของเก่าอยู่ที่ไหน ตรวจพาธทุกตัวแล้ว
ผล: ชี้ชัดว่าสมการหลักชั้น 1 อยู่ใน THEORY_CARD + 02_equations/covariant, ชั้น 2–3 อยู่ใน 03_lanes และยังไม่ได้ derive จากชั้น 1; Master Equation 7 เทอมและ For Work เป็นของเก่า
ระดับ: ไม่เปลี่ยน claim
ถัดไป: merge PR #57
commit: this commit

## 2026-11-11 — Thought experiment rewritten (v3): no "being", no eternity claim
ทำ: ผู้เขียนอธิบายใหม่ว่า "เกิดขึ้นแล้ว" ไม่เท่ากับ "เป็นนิรันดร์"; เขียน docs/core/THOUGHT_EXPERIMENT.md v3 (ฉบับเดิมไม่แก้เพราะ manifest ล็อก hash) ตัดคำว่า being, การคำนวณเปลี่ยนอดีต, ภาพลวงตา
ผล: หลักการที่ยืนโดยไม่ต้องพึ่งนิยาม: P1 วัดได้สถานะในอดีต, P2 ช่องว่าง ≈ อัตราเปลี่ยน × อายุบันทึก, P3 ความพร้อมกันของที่ไกลไม่เป็นสากล, P4 บันทึกร่วม = สัมผัสเชิงเหตุผล + I(A:B) > 0; R3 แสดงว่าบันทึกที่อ่านได้ I จางลงทั้งที่ข้อมูลรวมไม่หาย
ระดับ: ไม่เปลี่ยน claim (เป็นงานเขียนเจตนา); P2 และ P4 ยังไม่มี physics test
ถัดไป: test P2 (light-time) และ P4 (light cone); ต่อชั้นสังเกตเข้าสมการหลัก
commit: this commit

## 2026-11-11 — Is the gap between record and present equal to rate x record age? (O1)
ทำ: หา retarded time ด้วย root search แล้วตรวจกับคำตอบปิดของการเคลื่อนที่สม่ำเสมอใน 3-D; ตรวจ Delta ≈ Xdot(t_e)·a ว่าลู่เข้าอันดับ 1; negative control ไม่คิดเวลาหน่วง (16 physics test)
ผล: root search ตรงคำตอบปิดที่ 1e-10 (10/10); อัตราส่วน error ของการประมาณอันดับ 1 ระหว่างการลดอายุลงครึ่งหนึ่ง 2.42, 2.17, 2.08 → 2; ไม่คิดเวลาหน่วงผิดพอดี rate × age
ระดับ: P2 ของ thought experiment v3 → L1 (บันทึกผลตอนท้าย)
ถัดไป: O2 บันทึกร่วมเกิดภายใน light cone เท่านั้น
commit: this commit

## 2026-11-11 — Do two systems share a record only after causal contact? (O2)
ทำ: โซ่ oscillator 121 ตัว เริ่มจาก product state (I = 0) แล้ววัด mutual information ของสองตำแหน่งตามเวลาและระยะ d; ตรวจ group velocity ≤ c = √κ; negative control สมมติความเร็วสัญญาณผิด (5 physics test)
ผล: ก่อนสัมผัส (0.6·d/2c) I = 1.5e-7, 2.7e-13, 0 ที่ d = 10, 20, 30 (ลดแบบ super-exponential); หลังสัมผัส (1.2·d/2c) I = 6.5e-3, 2.6e-3, 1.4e-3; ที่ t = 0.75 d/c ซึ่งสัญญาณตรงยังมาไม่ถึง I = 1.4e-2 แล้ว → สัมผัสเกิดผ่าน common past ที่ d/2c ไม่ใช่เฉพาะสัญญาณตรง ที่ d/c
ระดับ: P4 → L1 และ **ต้องแก้ถ้อยคำ P4**: contact = past cone ซ้อนกัน ไม่ใช่เฉพาะอยู่ใน cone ของกันและกัน
ถัดไป: O3 Markov กับ history-dependent
commit: this commit
