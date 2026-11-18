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
| W6 | `01_contracts`, `04_proofs`, `99_review` | ยังไม่เริ่ม |
| W7 | `05_tests` | ยังไม่เริ่ม |
| W8 | `07_artifacts` | ยังไม่เริ่ม |
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
