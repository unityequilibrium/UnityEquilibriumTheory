# Core alignment register

> แผน: [`docs/meta/CORE_ALIGNMENT_PLAN_2026-11-18.md`](../docs/meta/CORE_ALIGNMENT_PLAN_2026-11-18.md)
> บัญชีไฟล์รายตัว: [`CORE_ALIGNMENT_REGISTER.tsv`](CORE_ALIGNMENT_REGISTER.tsv) (ไฟล์ละหนึ่งแถว)
> สร้าง 2026-11-18 จาก branch `claude/research/core-alignment` ด้วยการสแกนแบบอ่านอย่างเดียว ป้ายในบัญชีนี้เป็น**ป้ายเบื้องต้น** ป้ายจริงตัดสินทีละรอบ (W1–W10)

## ป้าย

| ป้าย | ความหมาย | ตัดสินจาก |
|---|---|---|
| `A` | ใช้ต่อ: ส่วนของสมการใหม่ | ถูกอ้างใน `docs/standard/` หรือ `theory_card.json` หรืออยู่ใน `05_tests/physics` |
| `A_DEP` | ใช้ต่อ: โค้ดที่ไฟล์ป้าย A เรียกใช้ | ชื่อหรือ path ของไฟล์ปรากฏในโค้ด Python ป้าย A (ไล่ต่อเป็นทอด) |
| `D` | โครงสร้าง | contract, redirect, shim, `__init__.py`, governance |
| `REVIEW` | ยังไม่ตัดสิน | ที่เหลือทั้งหมด จะได้ป้าย B (พัฒนาต่อ) หรือ C (เก็บ) ในรอบตรวจ |

คอลัมน์ในไฟล์ TSV:
- `pinned_by` คือจำนวน calculation contract ที่ล็อก hash ไฟล์นั้น
- `ref_*` คือจำนวนไฟล์ที่อ้างถึงไฟล์นั้น แยกตามที่มา: standard, physics test, core, core test, topic, contract, อื่น ๆ

## สรุปตามโฟลเดอร์

| โฟลเดอร์ | ไฟล์ | A | A_DEP | D | REVIEW | ล็อก hash | topic เรียกใช้ |
|---|---|---|---|---|---|---|---|
| `(ราก core)` | 14 | 2 | 6 | 1 | 5 | 0 | 9 |
| `00_governance` | 239 | 17 | 0 | 222 | 0 | 1 | 83 |
| `01_contracts` | 34 | 0 | 4 | 2 | 28 | 8 | 8 |
| `02_equations` | 131 | 3 | 13 | 5 | 110 | 13 | 88 |
| `03_lanes` | 193 | 21 | 34 | 10 | 128 | 50 | 96 |
| `04_proofs` | 2 | 0 | 1 | 0 | 1 | 0 | 0 |
| `05_tests` | 572 | 38 | 0 | 0 | 534 | 30 | 102 |
| `06_data` | 20 | 0 | 1 | 0 | 19 | 0 | 16 |
| `07_artifacts` | 617 | 0 | 6 | 0 | 611 | 13 | 318 |
| `08_history` | 305 | 2 | 1 | 271 | 31 | 1 | 127 |
| `99_review` | 5 | 0 | 1 | 0 | 4 | 0 | 1 |
| `engine` | 10 | 1 | 5 | 1 | 3 | 5 | 1 |
| **รวม** | **2,142** | **84** | **72** | **512** | **1,474** | **121** | **849** |

## สิ่งที่บัญชีนี้บอก

- ส่วนของสมการใหม่ (A กับ A_DEP) มี 156 ไฟล์ จาก 2,142 ไฟล์
- ไฟล์ที่ยังต้องตัดสินมี 1,474 ไฟล์ ส่วนใหญ่อยู่ใน `05_tests` (regression เก่า 534 ไฟล์) และ `07_artifacts` (611 ไฟล์)
- ไฟล์ที่ถูกล็อก hash มี 121 ไฟล์ ไฟล์กลุ่มนี้ห้ามย้ายหรือแก้เนื้อหาโดยไม่ได้อนุมัติแยก
- ไฟล์ core ที่ topic อ้างถึงมี 849 ไฟล์ ถ้าเก็บไฟล์กลุ่มนี้ต้องดูผลต่อ topic ก่อน

## ข้อจำกัดของการสแกน

- นับการอ้างถึงจากชื่อไฟล์และ path ที่ปรากฏในข้อความ ไม่ใช่จากการรันโค้ด ไฟล์ที่ถูกเอ่ยชื่อในเอกสารจึงนับว่าถูกอ้างด้วย
  ดังนั้น A_DEP อาจกว้างเกินจริง ส่วนไฟล์ที่ถูกโหลดผ่านชื่อที่ประกอบขึ้นตอนรันอาจหลุดไป
- ป้ายจริงของทุกไฟล์ตัดสินในรอบตรวจ โดยอ่านไฟล์นั้นจริง

## ผลการตรวจแต่ละรอบ

| รอบ | โฟลเดอร์ | สถานะ |
|---|---|---|
| W1 | `02_equations/covariant`, `lorentz_noether` | เสร็จ 2026-11-18 (ดูด้านล่าง) |
| W2 | `03_lanes` ที่ใช้อยู่, `engine` | เสร็จ 2026-11-18 (ดูด้านล่าง) |
| W3 | `02_equations/matter_space` | เสร็จ 2026-11-18 (ดูด้านล่าง) |
| W4 | `02_equations/o2` | เสร็จ 2026-11-18 (ดูด้านล่าง) |
| W5 | `03_lanes/thermal`, `topic13_support` | เสร็จ 2026-11-18 (ดูด้านล่าง) |
| W6 | `01_contracts`, `04_proofs`, `99_review` | เสร็จ 2026-11-18 (ดูด้านล่าง) |
| W7 | `05_tests` | เสร็จ 2026-11-18; ซ่อม hash แล้ว (ดูด้านล่าง) |
| W8 | `07_artifacts` และเก็บ test ที่พัง | เสร็จ 2026-11-18 (ดูด้านล่าง) |
| W9 | `00_governance`, `06_data`, `08_history` | ยังไม่เริ่ม |
| W10 | เอกสารหน้า core | ยังไม่เริ่ม |

ป้ายสุดท้ายอยู่ในคอลัมน์ `decision` ของ TSV: `A` ใช้ต่อ, `B` พัฒนาต่อ, `C` เก็บ, `C?` น่าจะเก็บแต่รอรอบอื่น, `D` โครงสร้าง

### W1: `02_equations/covariant` และ `lorentz_noether` (24 ไฟล์)

| ป้าย | ไฟล์ | เหตุผล |
|---|---|---|
| A (6) | `uet_covariant_response.py`, `uet_covariant_matter.py`, `uet_covariant_balance.py`, `uet_covariant_parent.py`, `uet_scalar_tensor_mapping.py`, `covariant/README.md` | คือ action แม่, บัญชีแลกเปลี่ยน และการแปลงเป็น DEF; physics test 85 ข้อที่ครอบไฟล์เหล่านี้ผ่าน |
| B (1) | `uet_covariant_nonclosed.py` | kernel แบบ retarded อาจใช้เป็น memory kernel ของชั้น 2 ถ้าต้องการ ยังไม่ได้ derive จาก action |
| C (12) | `uet_covariant_open_system.py`, `uet_covariant_superfluid_transport.py`, `uet_covariant_theory_spine.py`, `uet_curved_3p1_*.py` (6 ไฟล์), `uet_lorentz.py`, `uet_noether.py`, `lorentz_noether/README.md` | ไม่มี claim ไหนใช้: ระบบเปิดเชิงเส้นที่ตัวตรวจเป็นศูนย์โดยนิยาม, สายฮีเลียมที่ T015 ตก, เครื่องมือ GR เชิงตัวเลขมาตรฐาน, และ diagnostics ลอเรนซ์/Noether ของชุดสมการเก่าซึ่ง `03_lanes/observation/uet_lorentz_time.py` แทนแล้ว |
| C? (3) | `uet_covariant_diffusion.py`, `uet_covariant_reduction.py`, `uet_noether_phase_field_map.py` | เป็นสะพานไปหา prototype C, Φ, Π ของ `matter_space` ตัดสินพร้อม W3 |
| D (2) | `__init__.py` ทั้งสองโฟลเดอร์ | |

สิ่งที่พบเพิ่ม:
- ไฟล์ป้าย A ยัง import ผ่านชื่อเก่า `docs.core.*` ซึ่งยังทำงานได้ผ่าน `docs/core/__init__.py`
  แต่ `uet_covariant_matter.py` ถูกล็อก hash โดย contract 5 ฉบับ และ `uet_covariant_response.py` 2 ฉบับ
  แก้บรรทัด import จะทำให้ contract STALE จึงต้องรอรอบที่ผู้เขียนอนุมัติแยก
- ไฟล์ป้าย C ทุกตัวยังถูก regression test, `core/__init__.py` หรือ audit script เรียกใช้ จึงยังไม่ย้ายในรอบนี้ ติดป้ายไว้ก่อน แล้วย้ายพร้อม test ใน W7

### W2: `03_lanes` ที่ใช้อยู่ และ `engine` (84 ไฟล์)

| ป้าย | กลุ่ม | เหตุผล |
|---|---|---|
| A (56) | `observation`, `open_system`, `scalar_tensor`, `persistence` (โมเดลชั้น 3 และ producer ของ T001–T021), `engine` ทั้งหมดรวม lane card | เป็นโมเดลของสมการใหม่ หรือสคริปต์ที่สร้างผลใน `docs/standard/results/` |
| C (19) | `carrier_observer` (comparator ฟิสิกส์มาตรฐานของ foundation lane เก่า), `mass_density` (แปลง C แบบ normalized เป็นความหนาแน่น), `review` (observable เก่าที่ไม่ได้ derive จาก action), และ 4 ไฟล์ใน `persistence` ที่เป็น comparator รุ่นก่อน `uet_persistence_selection.py` | ไม่มี claim ใดใช้ สมการใหม่ไม่ใช้ตัวแปร C |
| D (9) | `__init__.py` | |

สิ่งที่พบเพิ่ม:
- physics test ทั้งชุดผ่าน 358 ข้อ ข้าม 1 ข้อ
- `persistence/uet_resource_selection.py` ป้าย C แต่ topic ยัง import อยู่ 3 ที่ ต้องแก้ topic ก่อนย้าย
- lane card ของ topic 0.19 และ 0.22 ใน `engine/lane_cards` จะตรวจซ้ำในแผน topics

### W3: `02_equations/matter_space` (15 ไฟล์) และสามไฟล์ C? จาก W1

- **C ทั้งโฟลเดอร์ (14 ไฟล์ + README):** ทั้งหมดคือชุดสมการรุ่นก่อนที่ใช้ตัวแปร C แบบ normalized ได้แก่ engine Ω = C·I (`uet_master_equation.py`), prototype C, Φ, Π (`uet_matter_space*.py`) และเครื่องมือประกอบ
  action แม่และ lane ที่ใช้อยู่ไม่ได้เรียกไฟล์ใดในโฟลเดอร์นี้เลย ร่องรอยของชั้น 2 ตอนนี้อยู่ที่ `03_lanes/open_system/uet_r3_trace_decomposition.py`
- **ไฟล์ C? จาก W1 เป็น C ทั้งสาม:** `uet_covariant_diffusion.py`, `uet_covariant_reduction.py`, `uet_noether_phase_field_map.py` เป็นสะพานไปหา prototype นี้

สิ่งที่พบเพิ่ม (สำคัญต่อแผน topics):
- ไฟล์ Python ใน topics 112 ไฟล์ จาก 28 topic ยัง import engine เก่า `uet_master_equation.py` (มากสุดคือ 0.11, 0.14, 0.23, 0.10)
  แปลว่าผลของ topic เหล่านี้คำนวณด้วยสมการเก่า ไม่ใช่ action แม่ จึงต้องตรวจทีละ topic ในแผน topics ว่าจะย้ายมาใช้ `core/engine` หรือเก็บ
- `uet_matter_space.py` ถูก contract ล็อก hash 9 ฉบับ จึงคงไว้ที่เดิม

### W4: `02_equations/o2` (90 ไฟล์)

โฟลเดอร์นี้คือ QFT ที่อุณหภูมิจำกัดของสนามสสาร O(2) (χ ใน action แม่) ที่สร้างไว้สำหรับสายฮีเลียมของ Topic 13
ไม่มีไฟล์ใดที่ lane ปัจจุบัน, engine หรือ claim ใช้ แต่ topic อ้างถึงหลายไฟล์ (มากสุด 46 ไฟล์ที่อ้าง `action_thermal_observable_bridge`)

| ป้าย | จำนวน | เหตุผล |
|---|---|---|
| B | 15 | derive จาก action ของ χ โดยตรงและเกี่ยวกับการสลายพลังงาน: SK contour, KMS, sunset cut, entropy production, no-go สองข้อ (one loop ไม่ให้ dissipation; action แบบอนุรักษ์อย่างเดียวไม่ให้ dissipation ในสถานะควบแน่น), EOS ที่ระดับ tree |
| C | 74 | เครื่องมือเฉพาะสายฮีเลียมของ Topic 13: สะพานไป β, two-fluid, การจับคู่ transport และขอบเขตเชิงตัวเลข; สายนี้ตกที่ระดับ tree ใน T015 |
| D | 1 | `__init__.py` |

ไฟล์ป้าย B คือวัตถุดิบของงานที่ AUTHOR_PROPOSITION ระบุว่ายังขาด: derive ชั้น 2 (ระบบเปิดและ entropy production) จาก action ผ่าน SK/KMS
จะทำในขั้น 3 เป็นรอบวิจัย โดยใช้ no-go สองข้อเป็นขอบเขตตั้งต้น

### W5: `03_lanes/thermal` และ `topic13_support` (119 ไฟล์)

- **C 117 ไฟล์:** `thermal` (29 ไฟล์ Python) คือสะพานความร้อนของ Topic 13 ไปหา lane C, Φ แบบ normalized และ lane วัสดุฮีเลียม/graphite
  `topic13_support` (85 บันทึกงานและ helper 4 ไฟล์) คือบันทึกการทำงานของโปรแกรมสะพานเดียวกัน ไม่มีไฟล์ใดที่ derive จาก action แม่ หรือที่ claim ใช้
- **D 2 ไฟล์:** `__init__.py`
- ไฟล์ 3 ไฟล์ถูก contract ล็อก hash และ 90 ไฟล์ถูก topic อ้างถึง (ส่วนใหญ่คือ Topic 13) จึงคงไว้ที่เดิม
- ตัวตรวจ entropy และ SK/KMS ที่นี่ (`thermal_sk_kms_entropy_contract.py`) เป็น interface แบบประกาศเอา ไม่ใช่ derivation ส่วนที่ derive จริงอยู่ในไฟล์ป้าย B ของ W4

### W6: `01_contracts`, `04_proofs`, `99_review` (41 ไฟล์)

| ป้าย | จำนวน | ไฟล์และเหตุผล |
|---|---|---|
| A | 4 | `BINARY_PULSAR_PILOT_SOURCES.md` และ `JOURNAL_CROSSCHECK_2026-11-10.md` (แหล่งตัวเลขของ T001, T002, T005, T006), README ของ `01_contracts` (เขียนใหม่ใน W10) และ README ของ `99_review` (กติกาว่าไฟล์ที่กักไว้ใช้เป็นหลักฐานไม่ได้ยังใช้ได้) |
| B | 3 | `UET_GR_NONCLOSED_RESEARCH_SPEC.md` (spec ของสนาม response ใน action แม่ แต่ยังใช้คำสถานะแบบเก่า), `O2_SUPERFLUID_EOS_TRANSPORT_SPEC.md` (spec ของ EOS และ SK ของ χ ที่ W4 ให้ B) และ `RESOURCE_PERSISTENCE_PRINCIPLE_SPEC.md` (หลักการว่าการดำรงอยู่คัดเลือกวิธีจัดสรรทรัพยากรโดยไม่มีเจตนา ตรงกับชั้น 3 ของผู้เขียน แต่รูปคำนวณยังเขียนบนเส้นทาง C ต้องเขียนใหม่ด้วยตัวแปรของชั้น 3) |
| C | 32 | spec ของ lane C และ comparator รุ่นก่อน 14 ฉบับ, สรุป gate เก่า 6 ฉบับ (F0 inventory, correspondence matrix, compatibility decision, status aggregate, code surface, equation family) ซึ่งทะเบียนนี้และ SYNTHESIS_AUDIT แทนแล้ว, spec จักรวาลเปิดที่ AUTHOR_PROPOSITION แทน, `uet_parameters.py` (ตาราง κ/β ของ engine Ω = C·I), `uet_gr_correspondence.py`, `uet_coarse_graining.py`, `Proof_00_Master_Balance.py`, README ของสามโฟลเดอร์ที่ถือแต่ไฟล์ C และของใน `99_review/unresolved_assets` 4 ไฟล์ |
| D | 2 | `__init__.py` |

- **`Proof_00_Master_Balance.py`** อ้างว่าแก้ปัญหา Millennium ทั้ง 7 ข้อได้ด้วย Ω → 0 ซึ่งไม่มี derivation และใช้คำที่ห้ามใช้ จึงเก็บพร้อมป้าย LEGACY_UNREVIEWED และห้ามอ้างเป็นหลักฐาน
- **`uet_parameters.py`** ถูก topic import 93 ไฟล์ และ `uet_master_equation.py` ก็ใช้ จึงคงไว้ที่เดิมจนถึงแผน topics
- **ไฟล์ที่ contract ล็อก hash คงไว้ที่เดิม:** `MATTER_SPACE_RESEARCH_SPEC.md` (10 ฉบับ), `RESOURCE_SELECTION_DYNAMIC_GAME_SPEC.md`, `UET_MAIN_THEORY_AXIOMS_SPEC.md` และ `UET_CORE_EQUATION_FAMILY_CONTRACT.md`
- **สิ่งที่ต้องทำต่อจากรอบนี้:** เขียน spec ป้าย B ใหม่ด้วยคำศัพท์ v2 ในขั้น 3 โดยเฉพาะหลักการของชั้น 3 ที่ควรอ้างถึงโมเดล consumer-resource และผล T018, T023

### W7: `05_tests` (572 ไฟล์)

ตัดสินจากโมดูลที่ test import: ถ้า import โมดูลป้าย B ให้ B, ถ้า import โมดูลป้าย C ให้ C (โมดูล A ที่ import ด้วยเป็นแค่ input), ถ้า import แต่โมดูล A ให้ A
test ที่ไม่ import โมดูลใน core เลยตัดสินจากสิ่งที่มันอ่าน (artifact, audit script, ไฟล์ migration)

| ป้าย | จำนวน | อะไรบ้าง |
|---|---|---|
| A | 46 | physics test ทั้ง 36 ไฟล์ (ที่ `check_physics_tests` นับ), mutation run ของ action แม่, ตัวตรวจ lane card ของ engine, regression ของ response, matter, balance, parent และ closed limit และ README ของโฟลเดอร์ที่ยังมี A |
| B | 32 | regression ของโมดูล O(2) ป้าย B (SK/KMS, sunset cut, entropy balance, no-go สองข้อ) และ `uet_covariant_nonclosed` เก็บไว้คู่กับโมดูลสำหรับขั้น 3 |
| C | 491 | test ของ Topic 13 ที่อ่าน artifact หรือ audit script 256 ไฟล์, test ของโมดูลป้าย C 148 ไฟล์, test ของ gate, migration และ artifact เก่า 83 ไฟล์ และ fixture 4 ไฟล์ |
| D | 3 | `__init__.py` และ test การหา path แบบ canonical |

- **test ที่เป็นหลักฐานจริงมีแค่ 36 ไฟล์ใน `physics/`:** อีก 536 ไฟล์เป็น bookkeeping หรือ regression ของ lane เก่า
- **ยังไม่ได้ย้ายไฟล์:** test ป้าย C จะย้ายไปพร้อมโมดูลของมันในขั้นย้ายไฟล์

**สาเหตุที่ CI แดง (Research contract validation):**
contract 20 ฉบับ (19 ฉบับใน Topic 0.13 และ `audit_matter_space_core`) ล็อก sha256 ของสคริปต์ 26 ไฟล์ไว้ STALE ทั้งหมด 43 จุด
สคริปต์ทั้ง 26 ไฟล์ถูกแก้ตอนย้าย core และ topics ไปไว้ที่ root (commit 4aaffa11a, 1153050a9, bd02cb921 วันที่ 14–15 พ.ย.)
สิ่งที่แก้คือ `parents[5]` เป็น `parents[4]`, ข้อความ path จาก `docs/core` และ `docs/topics` และการครอบด้วย `canonical_existing_path` ไม่ได้แตะสูตร
ผลคำนวณที่เทียบกับ artifact ที่ commit ไว้ได้ 8 ตัวเหมือนเดิมทุกค่า (ต่างแค่ข้อความ path ใน 1 key) ที่เหลือเทียบไม่ได้ เพราะ artifact ไม่ได้ commit ไว้ หรือติด STALE ต่อกันเป็นสาย
manifest ของ BaTiO3 publication ก็ล็อก hash ของสคริปต์เดียวกันไว้ จึงทำให้ `calculation-audit-tests` ล้มด้วย
การซ่อมคือคำนวณ hash ใหม่ใน contract (และใน manifest) โดยไม่แก้ path และ physics ซึ่งตาม AGENTS §6.3 ต้องให้เจ้าของอนุมัติก่อน

**ผลการซ่อม (เจ้าของอนุมัติ 2026-11-18):** คำนวณ hash ใหม่ใน contract 20 ฉบับและ manifest ของ BaTiO3 และสร้าง artifact ใหม่ 29 ไฟล์ ที่เปลี่ยนมีแค่ hash, เวลาที่สร้าง และ path ที่ producer เขียนเอง
completeness audit จึงเหลือ 0 error (เดิม 43) ส่วน test ที่ยังล้มหลังซ่อมนั้นเก็บเข้าคลังใน W8

### W8: `07_artifacts` (617 ไฟล์) และเก็บ test ที่พัง

- **ป้าย A 7 ไฟล์:** artifact ที่ regression test ป้าย A ของ action แม่อ่าน (covariant parent, GR closed limit, registry สมการ) และ README
- **ป้าย C 610 ไฟล์:** ผลลัพธ์ของ Topic 13 (350), gate และ correspondence ของ lane C และ foundation เก่า, archive และ provenance ของ migration
- **ไม่มี record วิจัยปัจจุบันไหนอ้าง `07_artifacts` เลย:** ผลของ T001–T023 อยู่ใน `docs/standard/results/`

**เก็บ test ที่พัง (เจ้าของตัดสินใจ 2026-11-18):** test ป้าย C 56 ไฟล์ที่ยังล้มหลังซ่อม hash (รวม test ที่เช็กว่าไฟล์ test Noether มีอยู่) ถูกย้ายเข้าคลังแบบไม่แก้เนื้อหา
- core 12 ไฟล์ไปที่ `core/08_history/archived_tests/`
- Topic 0.13 44 ไฟล์ไปที่ `topics/0.13_Thermodynamic_Bridge/Archive/tests/`
- ชื่อไฟล์ขึ้นต้นด้วย `archived_` เพื่อไม่ให้ pytest และขั้นตรวจ test ที่เปลี่ยนใน CI เก็บไปรัน
- สาเหตุที่ล้มเขียนไว้ใน README ของแต่ละคลัง: สคริปต์ยัง import `docs.core` หรือคาดหวัง path และ hash จากก่อนย้ายโฟลเดอร์, ต้องใช้ข้อมูล raw ส่วนตัว, หรือขัดกับ pin ของ BaTiO3
- ไฟล์ Topic 0.13 ทั้ง 44 ไฟล์มี test รวม 844 ข้อ ล้มอยู่ 53 ข้อ ข้อที่ผ่านอีก 791 ข้อจึงถูกเก็บไปด้วย เพราะเก็บทั้งไฟล์โดยไม่แก้เนื้อหา
