# CORE_MAP: สมการหลักของ UET อยู่ไหน อะไรคือของจริง อะไรคือของเก่า

> เขียนเมื่อ 2026-11-10 ตามที่ผู้เขียนสั่ง ทุกพาธในไฟล์นี้ตรวจแล้วว่ามีอยู่จริงในรีโพ ณ วันที่เขียน
> ไฟล์นี้เป็น**แผนที่** ไม่ใช่หลักฐาน ระดับหลักฐานของแต่ละข้ออ้างดูที่ [`docs/standard/claims.json`](../standard/claims.json) เท่านั้น
> ถ้าไฟล์นี้ขัดกับ `docs/STANDARD.md` ให้ถือ `docs/STANDARD.md`

## 1. อ่านตามลำดับนี้

| ลำดับ | ไฟล์ | บอกอะไร |
|---|---|---|
| 1 | [`AUTHOR_PROPOSITION.md`](AUTHOR_PROPOSITION.md) | เจตนาและตรรกะ 10 ข้อของผู้เขียน (แหล่งเดียวของเจตนา) |
| 1b | [`THOUGHT_EXPERIMENT.md`](THOUGHT_EXPERIMENT.md) | thought experiment "สิ่งที่เห็นคือบันทึกของอดีต" เวอร์ชัน 3 (ฉบับเดิมอยู่ `08_history/research_notes/` เก็บเป็นประวัติ) |
| 2 | [`THEORY_CARD.md`](THEORY_CARD.md) | **สมการหลักของชั้น 1** (parent action) พร้อมสถานะและพารามิเตอร์ที่ซ้ำซ้อน |
| 3 | [`FIDELITY_MATRIX.md`](FIDELITY_MATRIX.md) | ตรรกะแต่ละข้อของผู้เขียนตรงกับสมการไหม (ตรง 8 ข้อ) |
| 4 | [`SYNTHESIS_AUDIT.md`](SYNTHESIS_AUDIT.md) | หลักการที่ยืมจากทฤษฎีอื่นใช้ถูกเงื่อนไขไหม และขอบเขตของกฎรวม |
| 5 | [`../STANDARD.md`](../STANDARD.md) | มาตรฐานวิจัย (ระดับหลักฐาน, Test Card) |

## 2. สมการหลักอยู่ที่ไหน (แยกตามชั้น)

**สำคัญ: สมการหลักยังไม่ใช่สมการเดียว** ชั้น 1 เป็น action ที่ derive แล้ว ส่วนชั้น 2 และ 3 เขียนเป็นโมดูลแยก **ยังไม่ได้ derive จาก action ของชั้น 1**

### ชั้น 1: สสารแลกเปลี่ยนกับโครงสร้างของ space (parent action)

| อะไร | ไฟล์ |
|---|---|
| สมการ (action + สมการเคลื่อนที่ 3 ชุด) | [`THEORY_CARD.md`](THEORY_CARD.md) |
| โค้ดสมการ | `02_equations/covariant/uet_covariant_matter.py`, `uet_covariant_response.py`, `uet_covariant_parent.py`, `uet_covariant_balance.py` |
| แปลงเป็นทฤษฎี scalar-tensor (DEF) | `02_equations/covariant/uet_scalar_tensor_mapping.py` |
| ตัวตรวจว่าสมการถูก (sympy) | `05_tests/physics/test_parent_derivation.py`, `test_parent_offdiagonal.py`, `test_exchange_identity.py`, `test_def_mapping.py` |
| ตัวพยายามทำให้พัง | `05_tests/physics/test_stability_attacks.py`, `test_portal_fifth_force.py`, `test_fidelity_static_vacuum.py` |
| โมดูลเสริม (vacuum, fifth force) | `03_lanes/scalar_tensor/uet_vacuum_structure.py`, `uet_portal_fifth_force.py` |
| เทียบข้อมูลจริง | T001 pulsar คู่ (`t001_binary_pulsar_constraint.py`), T005 fifth force (`t005_fifth_force_constraint.py`) |

### ชั้น 2: ระบบเปิด เผาพลังงานอิสระ เขียนร่องรอย

| อะไร | ไฟล์ |
|---|---|
| สมการและโมเดล | `03_lanes/open_system/uet_layer2_dissipation.py` (ระบบปิดให้ระบบเปิดเอง), `uet_r3_trace_decomposition.py` (ร่องรอย = บันทึก + ความต่างศักย์), `uet_r1_writing_channels.py`, `uet_portal_drag.py` |
| ตัวตรวจ | `05_tests/physics/test_layer2_dissipation.py`, `test_r3_trace_decomposition.py`, `test_r1_writing_channels.py`, `test_distinctness.py` |
| เทียบข้อมูลจริง | T006 ดวงอาทิตย์ (`t006_solar_mass_loss.py`) |
| ของเก่าที่ยังอยู่ | `02_equations/covariant/uet_covariant_open_system.py` (ระบบเปิดแบบเชิงเส้น ค่า `kms_residual` เป็น 0 เสมอโดยนิยาม จึงไม่ใช่ตัวตรวจจริง ดู FIDELITY_MATRIX) |

### ชั้น 3: การคัดสรรด้วยการบริหารทรัพยากร

| อะไร | ไฟล์ |
|---|---|
| สมการและโมเดล | `03_lanes/persistence/uet_persistence_selection.py`, `uet_layer2_to_3.py` (อายุจากกฎการเผา), `uet_path_a_models.py` |
| ตัวตรวจ | `05_tests/physics/test_persistence_selection.py`, `test_layer2_to_3.py`, `test_r2_laser_selection.py`, `test_path_a_models.py` |
| เทียบข้อมูลจริง | T002 กระจุกดาว, T007 สาหร่าย, T008 ดาวแคระขาว, T009 ยูเรเนียม-234 (`t002_*`, `t007_*`, `t008_*`, `t009_*` ในโฟลเดอร์เดียวกัน) |

## 3. ผลการทดสอบกับข้อมูลจริงทั้งหมด (`docs/standard/`)

| Card | สรุป | ผล |
|---|---|---|
| T001 | pulsar คู่ตัด ξ_c ช่วง 2.0–2.4 | L2 constraint |
| T002 | สัดส่วนดาวในกระจุก | L2 INCONCLUSIVE (z = 2.05) |
| T005 | fifth force จำกัดการเชื่อม portal g_c | L2 constraint |
| T006 | การใช้พลังงานของดวงอาทิตย์เขียนลงแรงโน้มถ่วง | L2 PASS |
| T007 | สาหร่ายแข่งกันใน chemostat | L2 PASS |
| T008 | ความชัน luminosity function ของดาวแคระขาว | L2 PASS |
| T009 | ครึ่งชีวิต U-234 จากสมดุล เทียบกับวัดตรง | L2 PASS |

การ์ดอยู่ที่ `docs/standard/tests/` ผลอยู่ที่ `docs/standard/results/` ระดับของทุกข้ออ้างอยู่ที่ `docs/standard/claims.json`

## 4. ของเก่า: ยังอยู่ ห้ามลบ อ่านเป็นประวัติ

| ของ | สถานะ | เหตุผลที่ยังเก็บ |
|---|---|---|
| `02_equations/matter_space/uet_master_equation.py` (Master Equation 7 เทอม) | **ไม่ใช่สมการหลักปัจจุบัน** AUTHOR_PROPOSITION §5 ระบุว่าเทอม Natural Will / Game ไม่ได้ implement ตรรกะของผู้เขียน | contract และ test เก่าอ้างถึง |
| `docs/topics/For Work/` (30 ไฟล์) | แทนที่แล้วบางส่วนโดย `docs/STANDARD.md` ดู `SUPERSEDED_BY_STANDARD_V2.md` ในโฟลเดอร์นั้น: ไฟล์โครงสร้าง topic, README โค้ด, ข้อมูล, template **ยังใช้** (§15 ของ STANDARD); คำสถานะและลำดับขั้นงานเดิม**ถูกแทนที่** | contract 6 ฉบับล็อก hash ของไฟล์เหล่านี้ ถ้าย้ายหรือแก้จะพัง |
| `docs/core/00_governance/`, `07_artifacts/`, audit script จำนวนมาก | ผลิตภัณฑ์ของระบบ gate เดิม (`LEGACY_UNREVIEWED`) | ใช้เป็นเครื่องมือวินิจฉัยได้ ไม่ควบคุมสถานะ |
| `08_history/research_notes/THOUGHT_EXPERIMENT_OBSERVATION_PAST_BEHAVIOR.md` | v2 ของ thought experiment ใช้คำว่า being ซึ่งผู้เขียนถอนแล้ว ใช้ [`THOUGHT_EXPERIMENT.md`](THOUGHT_EXPERIMENT.md) แทน | manifest และ inventory หลายไฟล์ล็อก hash ไว้ |
| `docs/core/README.md` | มีถ้อยคำเก่า ไม่ใช่แหล่งควบคุมข้ออ้าง | ประวัติ |

## 5. กฎการแก้ไฟล์

- **ห้ามแก้** `docs/topics/For Work/` และ `docs/scripts/audit/audit_calculation_completeness.py` (มี contract ล็อก hash ไว้ ถ้าแก้ contract เหล่านั้นจะกลายเป็น STALE) ดู AGENTS.md §6.2
- ข้ออ้างใหม่ต้องมี Test Card ที่ผู้เขียนอนุมัติก่อนรัน และ agent เลื่อนระดับเป็น L2 ขึ้นไปเองไม่ได้ (`docs/STANDARD.md` §4)
- สมการใหม่ต้องมี physics test ที่ derive จริง (`@pytest.mark.physics`)

## 6. ช่องว่างที่ยังเปิดอยู่ (ซื่อตรง)

1. **ชั้น 2 และ 3 ยังไม่ได้ derive จาก parent action ของชั้น 1** ตอนนี้ต่อกันด้วยตรรกะและตัวเลข ไม่ได้ต่อกันด้วยสมการเดียว
2. **ยังไม่มีข้อทำนายเชิงตัวเลขที่ UET ต่างจากฟิสิกส์มาตรฐาน** (`C_B4_DISTINCTNESS_AUDIT`) ทุกชั้นลดรูปเป็นทฤษฎีที่มีอยู่แล้ว ส่วนที่เป็นของ UET คือการรวมสามสาขาและแผนที่ขอบเขต
3. ข้อ 7 ในตรรกะของผู้เขียน (ร่องรอยบน space) ตรงบางส่วน: ช่องแรงโน้มถ่วงมีหลักฐาน L2 (T006) แต่ยังไม่ได้ระบุว่าส่วนไหนเป็นของ UET เอง
4. ยังขาดการทดสอบกับข้อมูลจริงในเรื่อง "ทรัพยากรถูกตรึงที่ R*" (เลเซอร์, chemostat) และ negative control ที่คมพอ
