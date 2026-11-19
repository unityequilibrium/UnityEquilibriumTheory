# CORE_MAP: สมการหลักของ UET อยู่ไหน อะไรคือของจริง อะไรคือของเก่า

> เขียนเมื่อ 2026-11-10 ตามที่ผู้เขียนสั่ง ทุกพาธในไฟล์นี้ตรวจแล้วว่ามีอยู่จริงในรีโพ ณ วันที่เขียน · อัปเดตตารางผลทดสอบให้ครบ T001–T020 เมื่อ 2026-11-17 · เพิ่ม T021–T023, ชั้น 3 = Lotka–Volterra และผลการจัด core เมื่อ 2026-11-18
> ไฟล์นี้เป็น**แผนที่** ไม่ใช่หลักฐาน ระดับหลักฐานของแต่ละข้ออ้างดูที่ [`docs/standard/claims.json`](../docs/standard/claims.json) เท่านั้น
> **โค้ดและเทสต์ของสมการหลักอยู่ใน `core/` ทั้งหมด** ส่วน `docs/standard/` เป็นสมุดบันทึกกลาง (Test Card ที่ล็อกเกณฑ์ไว้ก่อนรัน, ผลลัพธ์, ระดับหลักฐาน) ตามที่ Standard v2 กำหนด สรุปผลทุกตัวอยู่ในหัวข้อ 3 ของไฟล์นี้
> ถ้าไฟล์นี้ขัดกับ `docs/STANDARD.md` ให้ถือ `docs/STANDARD.md`

## 1. อ่านตามลำดับนี้

| ลำดับ | ไฟล์ | บอกอะไร |
|---|---|---|
| 1 | [`AUTHOR_PROPOSITION.md`](AUTHOR_PROPOSITION.md) | เจตนาและตรรกะ 10 ข้อของผู้เขียน (แหล่งเดียวของเจตนา) |
| 1b | [`THOUGHT_EXPERIMENT.md`](THOUGHT_EXPERIMENT.md) | thought experiment "สิ่งที่เห็นคือบันทึกของอดีต" เวอร์ชัน 3 (ฉบับเดิมอยู่ `08_history/research_notes/` เก็บเป็นประวัติ) |
| 2 | [`THEORY_CARD.md`](THEORY_CARD.md) | **สมการหลักของชั้น 1** (parent action) พร้อมสถานะและพารามิเตอร์ที่ซ้ำซ้อน |
| 3 | [`FIDELITY_MATRIX.md`](FIDELITY_MATRIX.md) | ตรรกะแต่ละข้อของผู้เขียนตรงกับสมการไหม (ตรง 8 ข้อ) |
| 4 | [`SYNTHESIS_AUDIT.md`](SYNTHESIS_AUDIT.md) | หลักการที่ยืมจากทฤษฎีอื่นใช้ถูกเงื่อนไขไหม และขอบเขตของกฎรวม |
| 5 | [`../docs/STANDARD.md`](../docs/STANDARD.md) | มาตรฐานวิจัย (ระดับหลักฐาน, Test Card) |
| 6 | [`CORE_ALIGNMENT_REGISTER.md`](CORE_ALIGNMENT_REGISTER.md) | ป้ายของทุกไฟล์ใน core: A ใช้ต่อ, B พัฒนาต่อ, C เก็บเป็นประวัติ, D โครงสร้าง |

## 2. สมการหลักอยู่ที่ไหน (แยกตามชั้น)

**สำคัญ: สมการหลักยังไม่ใช่สมการเดียว** ชั้น 1 เป็น action ที่ derive แล้ว ชั้น 2 derive จาก action ได้แล้วหนึ่งช่องทาง (χ เป็นแหล่งความร้อนให้ φ, 2026-11-18) ส่วนชั้น 3 derive ได้แค่อัตราการจับทรัพยากรกับอัตราการตาย (2026-11-19) อัตราการรั่ว δ derive ได้ (2026-11-19) **อัตราการเติม S ไม่ได้มาจาก action เป็นค่าที่ขอบเขตกำหนด ส่วนชุดโหมดยังไม่ได้ derive**

### ชั้น 1: สสารแลกเปลี่ยนกับโครงสร้างของ space (parent action)

| อะไร | ไฟล์ |
|---|---|
| สมการ (action + สมการเคลื่อนที่ 3 ชุด) | [`THEORY_CARD.md`](THEORY_CARD.md) |
| โค้ดสมการ | `02_equations/covariant/uet_covariant_matter.py`, `uet_covariant_response.py`, `uet_covariant_parent.py`, `uet_covariant_balance.py` |
| แปลงเป็นทฤษฎี scalar-tensor (DEF) | `02_equations/covariant/uet_scalar_tensor_mapping.py` |
| ตัวตรวจว่าสมการถูก (sympy) | `05_tests/physics/test_parent_derivation.py`, `test_parent_offdiagonal.py`, `test_exchange_identity.py`, `test_def_mapping.py` |
| symmetry และกฎอนุรักษ์ (Noether, 2026-11-19) | `03_lanes/symmetry/uet_noether.py`: ประจุ O(2) อนุรักษ์แม้มี portal, generalized Bianchi identity ของ diffeomorphism ถือใน metric ที่ไม่สม่ำเสมอและมีพจน์นอกแนวทแยง จึงอนุรักษ์พลังงาน-โมเมนตัมรวม, E, P และประจุ boost บน lattice 1+1 และโมเมนตัมเชิงมุมบน lattice 2+1 ลู่เข้าอันดับ 2 (`C_NOETHER_COVERAGE`, L1; ตัวตรวจ `05_tests/physics/test_noether.py`) |
| ตัวพยายามทำให้พัง | `05_tests/physics/test_stability_attacks.py`, `test_portal_fifth_force.py`, `test_fidelity_static_vacuum.py` |
| โมดูลเสริม (vacuum, fifth force) | `03_lanes/scalar_tensor/uet_vacuum_structure.py`, `uet_portal_fifth_force.py` |
| เทียบข้อมูลจริง | ทุกไฟล์อยู่ใน `03_lanes/scalar_tensor/`: T001 pulsar คู่ (`t001_binary_pulsar_constraint.py`), T005 fifth force (`t005_fifth_force_constraint.py`), T016 ดาวเทียม MICROSCOPE (`t016_microscope_portal.py`), T019 ช่วงระยะ 1 ซม.–100 กม. (`t019_portal_gap_rotwash.py`), T020 เส้นทาง ข กับ LLR (`t020_route_b_llr.py`) |
| ภาค χ (สสาร) เทียบข้อมูลจริง | T015 ฮีเลียมเหลว (`03_lanes/open_system/t015_he_ii_tree_level.py`) **FAILED** |

### ชั้น 2: ระบบเปิด เผาพลังงานอิสระ เขียนร่องรอย

| อะไร | ไฟล์ |
|---|---|
| derive จาก action (2026-11-18) | `03_lanes/open_system/uet_layer2_from_action.py`: ถ้าให้ χ เป็นแหล่งความร้อน φ จะได้แรงเสียดทานและสัญญาณรบกวนที่เป็นไปตาม KMS เอง แรงเสียดทาน γ(q,T) = Nσ²n(√(q²/4+M_χ²))/(16πq) โดย σ = h√ε/(Z√k) จึงไม่ใช่พารามิเตอร์อิสระอีกต่อไป (`C_L2_FROM_ACTION`, L1; ตัวตรวจ `05_tests/physics/test_layer2_from_action.py`) |
| กฎข้อ 2 จาก action (2026-11-18) | `03_lanes/open_system/uet_layer2_second_law.py`: spectral function เป็นบวก ความร้อนไหลจากร้อนไปเย็น การผลิต entropy ≥ 0 และโหมดที่สั่นแบบ coherent เผา F ด้วย P = ΓE เขียน P/(T ln2) บิต (`C_L2_SECOND_LAW`, L1) |
| สมการและโมเดล | `03_lanes/open_system/uet_layer2_dissipation.py` (ระบบปิดให้ระบบเปิดเอง), `uet_r3_trace_decomposition.py` (ร่องรอย = บันทึก + ความต่างศักย์), `uet_r1_writing_channels.py`, `uet_portal_drag.py`, `uet_portal_drag_bound.py` (ขอบเขตของแรงลาก portal จากการที่วงโคจรอยู่รอด) |
| ตัวตรวจ | `05_tests/physics/test_layer2_dissipation.py`, `test_r3_trace_decomposition.py`, `test_r1_writing_channels.py`, `test_distinctness.py` |
| เทียบข้อมูลจริง | T006 ดวงอาทิตย์ (`t006_solar_mass_loss.py`) |
| ของเก่าที่ยังอยู่ | `02_equations/covariant/uet_covariant_open_system.py` (ระบบเปิดแบบเชิงเส้น ค่า `kms_residual` เป็น 0 เสมอโดยนิยาม จึงไม่ใช่ตัวตรวจจริง ดู FIDELITY_MATRIX) |

### ชั้น 3: การคัดสรรด้วยการบริหารทรัพยากร

| อะไร | ไฟล์ |
|---|---|
| derive จาก action (2026-11-19) | `03_lanes/persistence/uet_layer3_from_action.py`: อัตราการตาย 1/τ คืออัตราหน่วงของชั้น 2 อัตราการจับ a = −ρ_stream/(2w) มาจาก spectral function เดียวกัน แหล่ง χ ที่เท่ากันทุกทิศหน่วงได้อย่างเดียว กระแส χ ที่ไหลด้วย v ป้อนเฉพาะโหมดที่ w < vq (เงื่อนไข Cherenkov) และโหมดที่ R* ต่ำสุดชนะ (`C_L3_FROM_ACTION`, L1; ตัวตรวจ `05_tests/physics/test_layer3_from_action.py`) |
| อัตราเติมและรั่ว (2026-11-19) | `03_lanes/persistence/uet_layer3_supply.py`: แหล่งรั่วด้วย δ = n_sink⟨σv⟩ จาก quartic ของ χ (σ = 3λ²/(2πs)); S ไม่ได้มาจาก action; โครงสร้างอยู่ได้เมื่อ S > S* = δR*ₘᵢₙ (`C_L3_SUPPLY`, L1) |
| S ในระบบจริง (2026-11-19) | `03_lanes/persistence/uet_layer3_supply_chemostat.py`: ใน chemostat S = D·S0, δ = D และ 1/τ = D; เกณฑ์ S* = δR*ₘᵢₙ ใช้ได้กับการดูดซึมแบบอิ่มตัว (Monod) ไม่ใช่แค่แบบเส้นตรง; ไดอะตอมของ Tilman ที่ D = 0.25/วัน ต้องการ S* = 0.003–0.48 µM/วัน (`C_L3_SUPPLY_CHEMOSTAT`, L1) |
| สมการและโมเดล | `03_lanes/persistence/uet_persistence_selection.py`, `uet_layer2_to_3.py` (อายุจากกฎการเผา), `uet_path_a_models.py`, `uet_layer3_lv_map.py` (ลดรูปเป็น Lotka–Volterra ของ Saavedra et al. 2025 ทีละเทอม) |
| ตัวตรวจ | `05_tests/physics/test_persistence_selection.py`, `test_layer2_to_3.py`, `test_r2_laser_selection.py`, `test_path_a_models.py`, `test_layer3_lv_map.py` |
| เทียบข้อมูลจริง | T002 และ T014 กระจุกดาว, T007 สาหร่าย, T008 ดาวแคระขาว, T009 ยูเรเนียม-234, T017 ยีสต์, T018 อายุนกและสัตว์เลี้ยงลูกด้วยนม **FAILED**, T021 การเปลี่ยนเทคโนโลยีแสงสว่าง, T023 ค้างคาวเทียบนก (`t002_*`, `t007_*`, `t008_*`, `t009_*`, `t014_*`, `t017_*`, `t018_*`, `t021_*`, `t023_*` ใน `03_lanes/persistence/`) |

### ชั้นสังเกต (thought experiment v3)

| อะไร | ไฟล์ |
|---|---|
| คำอธิบายและหลักการ P1–P4 | [`THOUGHT_EXPERIMENT.md`](THOUGHT_EXPERIMENT.md) |
| โมเดล | `03_lanes/observation/uet_observation_layer.py` (เวลาหน่วง, ช่องว่าง), `uet_shared_record.py` (บันทึกร่วมต้องมีการสัมผัสเชิงเหตุผล), `uet_estimators.py` (Markov กับ history), `uet_field_causality.py` (สนาม ψ แพร่ใน light cone), `uet_pulsation_timing.py` (P2 กับดาวเต้นในระบบดาวคู่), `uet_two_signal_contact.py` (P4 เมื่อสัญญาณสองตัวมีความเร็วต่างกัน: t = d/(c_a + c_b)), `uet_lorentz_time.py` (P3: boost, ความพร้อมกันสัมพัทธ์ dt' = −γβdx, ค่า Ives–Stilwell), `uet_rms_light_speed.py` (ความเร็วแสงสองทางในกรอบ Robertson–Mansouri–Sexl) |
| ตัวตรวจ | `05_tests/physics/test_observation_delay.py`, `test_shared_record_cone.py`, `test_markov_vs_history.py`, `test_field_causality.py`, `test_pulsation_timing.py`, `test_two_signal_contact.py`, `test_lorentz_time.py`, `test_rms_light_speed.py` |
| เทียบข้อมูลจริง | T010 GW170817 (`t010_gw170817_carrier_speed.py`): คลื่นความโน้มถ่วงกับแสงวิ่งเร็วเท่ากัน ตามที่ c_T = 1 กำหนด (derive ใน `05_tests/physics/test_tensor_speed.py`); T011 ดาวเต้นในระบบดาวคู่ (`t011_pulsation_delay_vs_rv.py`): ช่องว่างเฟส = อัตรา × อายุบันทึก (P2); T012 หน้าคลื่นสหสัมพันธ์ใน Bose–Hubbard quench (`t012_correlation_front_bound.py`): บันทึกร่วมต้องผ่านอดีตร่วม (P4); T013 Ives–Stilwell (`t013_ives_stilwell_lorentz_time.py`): การแปลงเวลาเป็นแบบลอเรนซ์ (P3 ในฐานะส่วนหนึ่งของการแปลงลอเรนซ์); T022 Michelson–Morley และ Kennedy–Thorndike (`t022_michelson_morley_kennedy_thorndike.py`): ความยาวและความเร็วก็เป็นแบบลอเรนซ์ ทำให้การแปลงลอเรนซ์ครบเมื่อรวมกับ T013 |

## 3. ผลการทดสอบกับข้อมูลจริงทั้งหมด (`docs/standard/`)

**นับรวม (2026-11-18):** 22 การ์ด (ไม่มีเลข T003, T004) · ผ่าน 16 · ไม่ชี้ขาด 3 (T002, T014, T023) · **พัง 3 (T015, T018, T024)** · ข้ออ้างใน claims.json 52 ข้อ: L1 31, L2 18, FAILED 3 · ทุกตัวที่ผ่าน ฟิสิกส์มาตรฐานหรือ null ก็ผ่านด้วย จึง**ยังไม่มีการทดสอบไหนที่แยก UET ออกจากฟิสิกส์เดิมได้**

| Card | ชั้น | สรุป | ผล |
|---|---|---|---|
| T001 | 1 | pulsar คู่ตัด ξ_c ช่วง 2.0–2.4 | L2 constraint |
| T002 | 3 | สัดส่วนดาวในกระจุก | L2 INCONCLUSIVE (z = 2.05) |
| T005 | 1 | fifth force จำกัดการเชื่อม portal g_c | L2 constraint |
| T006 | 2 | การใช้พลังงานของดวงอาทิตย์เขียนลงแรงโน้มถ่วง | L2 PASS |
| T007 | 3 | สาหร่ายแข่งกันใน chemostat | L2 PASS |
| T008 | 3 | ความชัน luminosity function ของดาวแคระขาว | L2 PASS |
| T009 | 3 | ครึ่งชีวิต U-234 จากสมดุล เทียบกับวัดตรง | L2 PASS |
| T010 | สังเกต | บันทึกของเหตุการณ์เดียวผ่านคลื่นความโน้มถ่วงกับแสง (GW170817) วิ่งเร็วเท่ากัน | L2 PASS (ทฤษฎีใดที่มี c_T = 1 ก็ผ่าน) |
| T011 | สังเกต | เวลาหน่วงจากจังหวะการเต้นเท่ากับอายุบันทึกที่คำนวณจากวงโคจร RV อิสระ (P2) | L2 PASS (z = 0.04, 0.17; เวลาเดินทางของแสงมาตรฐานก็ผ่าน) |
| T012 | สังเกต | หน้าคลื่นสหสัมพันธ์หลัง quench ไม่เร็วกว่าขอบเขตอดีตร่วม c_a + c_b และเร็วกว่าขอบเขตสัมผัสตรง 3.9σ และ 6.0σ (P4) | L2 PASS (ฟิสิกส์ควาซิพาร์ติเคิลมาตรฐานก็ผ่าน) |
| T013 | สังเกต | ค่า Ives–Stilwell ของ ⁷Li⁺ ที่ β = 0.338 เป็น (1.47 ± 2.30)×10⁻⁹ ตรงกับศูนย์ที่การแปลงลอเรนซ์ต้องการ (P3) | L2 PASS (สัมพัทธภาพพิเศษมาตรฐานก็ผ่าน; ไม่แยกความพร้อมกันเดี่ยวๆ) |
| T014 | 3 | สัดส่วนดาวในกระจุก ด้วยข้อมูลที่ไม่ขึ้นกับ T002: ทำนาย R = 1.47 วัดได้ 1.31 ± 0.06 | L2 INCONCLUSIVE (z = 2.22) |
| T015 | 1 (ภาค χ) | เอา χ เป็นอะตอมฮีเลียม-4 แล้วทำนายความเร็วเสียงของฮีเลียมเหลว: ทำนาย 771–880 m/s วัดได้ 233 m/s | **FAILED** (ภาค χ แบบ tree level ใช้แทนฮีเลียมเหลวตรงๆ ไม่ได้) |
| T016 | 1 | ดาวเทียม MICROSCOPE จำกัด portal: g_c ≤ 1.16e-15 eV ที่ระยะ 1.9e8 m (แคบกว่า T005 ราว 12 เท่า) | L2 constraint |
| T017 | 3 | ยีสต์แบ่งตัวไม่สมมาตร: เวลาเพิ่มเป็นสองเท่าที่ทำนายตรงกับที่วัด 5 ระดับยา (z สูงสุด 1.81) | L2 PASS (ทฤษฎีประชากรมาตรฐานก็ผ่าน) |
| T018 | 3 | อายุยืนสูงสุดของนก 128 ชนิดและสัตว์เลี้ยงลูกด้วยนม 170 ชนิด เทียบกับ τ = F/P: พลังงานตลอดชีวิตต่อกรัมไม่คงที่ ความชัน −0.114 (95%: −0.140 ถึง −0.088) และนกใช้มากกว่า 2.47 เท่า | **FAILED** (กฎชั้น 3 ใช้กับอายุของสัตว์แต่ละตัวไม่ได้ในขอบเขตที่ผู้เขียนประกาศ) |
| T019 | 1 | การทดลอง Rot-Wash ปิดช่องว่างของ g_c ที่ระยะ 1 ซม.–100 กม.: g_c ≤ 1.3e-12 eV (ที่ 1 m ขึ้นไป) | L2 constraint |
| T020 | 1 (เส้นทาง ข) | ถ้าการเผาพลังงานเป็นประจุของ ψ โลกกับดวงจันทร์จะตกต่างกัน: LLR ให้ τ_β ≤ 4.61e15 s (1.46e8 ปี) | L2 constraint |
| T021 | 3 | เทคโนโลยีแสงสว่างที่เข้ามาแทนและอยู่รอด ไม่มีตัวไหนแย่กว่าตัวเดิมทั้งพลังงานและชั่วโมงทำงานต่อ lumen-hour (เวลานับเป็นทรัพยากร) | L2 PASS |
| T022 | สังเกต | Michelson–Morley และ Kennedy–Thorndike ในกรอบ RMS: z_MM 0.50, z_KT 1.30 (แก้การ์ดครั้งหนึ่งเรื่องความแม่นยำของตัวเลข ก่อนรันใหม่) | L2 PASS (สัมพัทธภาพพิเศษมาตรฐานก็ผ่าน) |
| T023 | 3 | ค้างคาวเทียบนก (ทุนพลังงานระดับสายพันธุ์): ค้างคาวสูงกว่าสัตว์เลี้ยงลูกด้วยนมอื่น 1.96 เท่า แต่ต่ำกว่านก (Δ −0.17) การบินอธิบายได้ราว 60% ของส่วนเกินของนก | L2 INCONCLUSIVE |
| T024 | 3 (หลายระบบ) | ช่วงห่างระหว่างนวัตกรรมแสงสว่างกับประชากรโลก: ความชัน −1.43 (95%: −2.14 ถึง −0.72) ไม่ตรงกับ −0.27 ของ Bettencourt แต่ตรงกับ −1 ของ Kremer | **FAILED** (UET ยืมหลักการของ Kremer แทน) |

การ์ดอยู่ที่ `docs/standard/tests/` ผลอยู่ที่ `docs/standard/results/` ระดับของทุกข้ออ้างอยู่ที่ `docs/standard/claims.json` · การ์ด T001–T013 บันทึกพาธสคริปต์เดิมเป็น `docs/core/...` ซึ่งตอนนี้คือ `core/...` (ย้ายโฟลเดอร์ 2026-11-14)

**งานวิเคราะห์ที่ยังไม่ใช่การทดสอบ** (ไม่เปลี่ยนระดับหลักฐาน): topic 0.23 `Doc/STRESS_02`–`STRESS_09` (ขอบเขตชั้น 3, เส้นทาง ข, งบสารสนเทศ, ψ คืออะไร, ψ กับสุญญากาศควอนตัม, สี่จุดที่ UET อาจต่าง, การอยู่รอดของสายพันธุ์) และ topic 0.3 `Doc/ANALYSIS_PARENT_ACTION_EMG_2026-11-17.md` (parent action มีแบบจำลอง Early Modified Gravity ของ Hubble tension อยู่ในตัว) ทะเบียนสิ่งที่ทำให้ UET พังอยู่ที่ [`topics/0.23_Unity_Scale_Link/FALSIFICATION_REGISTER.md`](../topics/0.23_Unity_Scale_Link/FALSIFICATION_REGISTER.md)

## 4. ของเก่า: ยังอยู่ ห้ามลบ อ่านเป็นประวัติ

| ของ | สถานะ | เหตุผลที่ยังเก็บ |
|---|---|---|
| `02_equations/matter_space/uet_master_equation.py` (Master Equation 7 เทอม) | **ไม่ใช่สมการหลักปัจจุบัน** AUTHOR_PROPOSITION §5 ระบุว่าเทอม Natural Will / Game ไม่ได้ implement ตรรกะของผู้เขียน | contract และ test เก่าอ้างถึง |
| `topics/For Work/` (30 ไฟล์ ย้ายจาก `docs/topics/For Work/` 2026-11-19) | แทนที่แล้วบางส่วนโดย `docs/STANDARD.md` ดู `SUPERSEDED_BY_STANDARD_V2.md` ในโฟลเดอร์นั้น: ไฟล์โครงสร้าง topic, README โค้ด, ข้อมูล, template **ยังใช้** (§15 ของ STANDARD); คำสถานะและลำดับขั้นงานเดิม**ถูกแทนที่** | contract 6 ฉบับล็อก hash ของไฟล์เหล่านี้ ถ้าแก้เนื้อหาจะพัง (การย้ายไม่กระทบ เพราะ hash คิดจากเนื้อหาและ audit แปล path เดิมให้) |
| `00_governance/` (ยกเว้น calculation contract), `07_artifacts/`, audit script จำนวนมาก | ผลิตภัณฑ์ของระบบ gate เดิม (`LEGACY_UNREVIEWED`) | ใช้เป็นเครื่องมือวินิจฉัยได้ ไม่ควบคุมสถานะ |
| `08_history/archived_tests/`, `topics/0.10_*/Archive/tests/`, `topics/0.13_*/Archive/tests/` | test ป้าย C ที่พังหลังย้ายโฟลเดอร์ 2026-11-14 เก็บเข้าคลังตามที่ผู้เขียนตัดสิน (2026-11-18) ไม่ถูกรัน | README ของแต่ละคลังบอกว่าแต่ละไฟล์พังเพราะอะไร |
| `08_history/research_notes/THOUGHT_EXPERIMENT_OBSERVATION_PAST_BEHAVIOR.md` | v2 ของ thought experiment ใช้คำว่า being ซึ่งผู้เขียนถอนแล้ว ใช้ [`THOUGHT_EXPERIMENT.md`](THOUGHT_EXPERIMENT.md) แทน | manifest และ inventory หลายไฟล์ล็อก hash ไว้ |
| `08_history/README_LEGACY_2026-11-14.md` | README เดิมของ core (engine Ω = C·I) มีถ้อยคำเก่า ไม่ใช่แหล่งควบคุมข้ออ้าง | ประวัติ (README ปัจจุบันเขียนใหม่ 2026-11-18) |

## 5. กฎการแก้ไฟล์

- **ห้ามแก้** `topics/For Work/` และ `docs/scripts/audit/audit_calculation_completeness.py` (มี contract ล็อก hash ไว้ ถ้าแก้ contract เหล่านั้นจะกลายเป็น STALE) ดู AGENTS.md §6.3
- ข้ออ้างใหม่ต้องมี Test Card ที่ผู้เขียนอนุมัติก่อนรัน และ agent เลื่อนระดับเป็น L2 ขึ้นไปเองไม่ได้ (`docs/STANDARD.md` §4)
- สมการใหม่ต้องมี physics test ที่ derive จริง (`@pytest.mark.physics`)

## 6. ช่องว่างที่ยังเปิดอยู่ (ซื่อตรง)

1. **ชั้น 3 derive จาก parent action ได้เพียงบางส่วน** (2026-11-19: อัตราการจับ a_i และอัตราการตาย 1/τ_i มาจาก spectral function เดียวกับชั้น 2 ดู `03_lanes/persistence/uet_layer3_from_action.py`, `C_L3_FROM_ACTION`, L1; การสูญ δ derive ได้ใน `uet_layer3_supply.py` (`C_L3_SUPPLY`, L1) แต่อัตราการเติม S เป็นค่าจากขอบเขต และชุดโหมดยังไม่ได้) ชั้น 2 derive ได้แล้วหนึ่งช่องทาง (χ เป็นแหล่งความร้อนให้ φ ที่ one loop) ส่วน entropy production และ F ในหน่วยจริงยังต้องทำต่อ
2. **ยังไม่มีข้อทำนายเชิงตัวเลขที่ UET ต่างจากฟิสิกส์มาตรฐาน** (`C_B4_DISTINCTNESS_AUDIT`) ทุกชั้นลดรูปเป็นทฤษฎีที่มีอยู่แล้ว ส่วนที่เป็นของ UET คือการรวมสามสาขาและแผนที่ขอบเขต
3. ข้อ 7 ในตรรกะของผู้เขียน (ร่องรอยบน space) ตรงบางส่วน: ช่องแรงโน้มถ่วงมีหลักฐาน L2 (T006) แต่ยังไม่ได้ระบุว่าส่วนไหนเป็นของ UET เอง
4. **ชั้นสังเกตเชื่อมกับสมการหลักแค่เชิงเส้น** (สนาม ψ แบน 1+1D, O4) P1–P4 ทดสอบกับข้อมูลจริงครบแล้ว (T010–T013) โดย P3 ผ่านในฐานะส่วนหนึ่งของการแปลงเวลาลอเรนซ์ ไม่ใช่ความพร้อมกันเดี่ยวๆ
5. ยังขาดการทดสอบกับข้อมูลจริงในเรื่อง "ทรัพยากรถูกตรึงที่ R*" (เลเซอร์, chemostat) และ negative control ที่คมพอ
6. **(2026-11-17) ψ ยังไม่มีหลักฐานว่ามีอยู่จริง** การ์ด T005, T016, T019, T020 ให้แค่ขอบเขตบน ทุกข้อมูลเข้ากับ g_c = 0 ซึ่งตรงกับที่ผู้เขียนอธิบายว่าโครงสร้างของ space เป็นบันทึกของสิ่งที่เกิดขึ้นแล้ว ไม่ใช่แรง
7. **(2026-11-17) กฎชั้น 3 มีขอบเขตที่พังแล้ว** T018 แสดงว่า τ = F/P ใช้กับอายุของสัตว์แต่ละตัวไม่ได้ ระดับสายพันธุ์ทดสอบแล้วใน T023 (ค้างคาวเทียบนก): การบินอธิบายได้ราว 60% ของส่วนเกินของนก ผลไม่ชี้ขาด
8. **(2026-11-18) ชั้น 3 ลดรูปเป็น Lotka–Volterra ของ Saavedra et al. (2025) ทีละเทอม** (`C_L3_LV_MAP`, L1) ต่างกันสองจุด: แหล่งทรัพยากรเดียวทำให้เหลือผู้ชนะคนเดียว และอัตราการตายมาจาก P/F
