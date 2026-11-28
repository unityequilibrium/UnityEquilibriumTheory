# แผนเก็บกวาด repo (ร่าง รอผู้เขียนอนุมัติ)

> **สถานะ: DRAFT ข้อเสนอของ AI (Claude) 2026-11-27** ยังไม่ได้ลบหรือย้ายอะไร
> ที่มา: `docs/meta/CONTENT_VALUE_AUDIT_2026-11-27.md` ซึ่งพบว่าราว 85% ของเนื้อหาที่เขียนขึ้นไม่ได้เพิ่มหลักฐาน
> ต้องได้รับอนุมัติเป็นข้อยกเว้นของ STANDARD §8 ("legacy ห้ามแก้ไขหรือลบ") ก่อนเริ่มเฟสที่ 2

## 0. หลักการ

1. **ไม่มีอะไรหายจริง** ก่อนลบ ให้ติด tag `archive/legacy-2026-11` บน `main` และ push ขึ้น GitHub
   ไฟล์ทุกไฟล์ในทุกเวอร์ชันยังดึงกลับได้ด้วย `git show archive/legacy-2026-11:<path>` หรือ `git checkout <tag> -- <path>`
   (ไม่ทำสำเนาในเครื่อง เพราะพื้นที่ดิสก์จำกัด และไม่สร้าง worktree เพิ่ม)
2. **ลบออกจาก working tree ไม่ใช่ย้ายไปโฟลเดอร์ legacy** ถ้าย้าย ขนาดก็เท่าเดิม และ agent ยังอ่านแล้วหลงเหมือนเดิม
3. **ทำเป็นเฟส** แต่ละเฟสเป็นหนึ่ง PR ต้องผ่าน CI และลง ledger ไม่รวบทำครั้งเดียว
4. **ตรวจการอ้างอิงก่อนลบทุกเฟส** ถ้าไฟล์ที่เก็บไว้ยังอ้างถึงไฟล์ที่จะลบ ให้หยุดและรายงาน ห้ามลบไปก่อนแล้วค่อยซ่อม
5. **เริ่มหลัง PR #90 และ #95 merge แล้ว** และหลังถามว่ามี session อื่นทำงานใน topic ไหนอยู่ ตอนนี้มี topic 0.18 (Lean)

## 1. สิ่งที่พบตอนตรวจการพึ่งพา

| เรื่อง | สิ่งที่พบ | ผลต่อแผน |
|---|---|---|
| Record ของ v2 (claims, การ์ด, result) | อ้าง topic แค่ 4 ตัว: 0.3 (proposal ของ T040/T041), 0.23, 0.25, 0.13 | เก็บเฉพาะไฟล์ที่ถูกอ้างใน topic เหล่านี้ |
| Calculation contract | 102 ฉบับ แบ่งเป็น FORMAL 63 ฉบับและ data comparison ~40 ฉบับ ไม่มีฉบับไหนอ้าง `topics/` และ lock hash ของ `audit_calculation_completeness.py` | เก็บทั้งหมด ห้ามแตะ script ที่ถูก lock |
| CI | `topics/run_all_tests.py` รันใน PR, main และ nightly; `compileall` ครอบ `topics` และ `services_and_experiments`; Pages copy ทั้ง `docs/`, `core/` และ `topics/`; มี `cargo check` ของ `services_and_experiments/uet_core` | ต้องแก้ workflow ในเฟสเดียวกับที่ลบ |
| `docs/scripts/audit` | 880 script ส่วนใหญ่เป็น sync, gate และ migration ยุค Codex CI ใช้แค่ `audit_calculation_completeness.py` | เก็บตัวที่ CI และ contract ใช้ พร้อมไฟล์ที่ import กัน ที่เหลือลบ |
| `core/05_tests` | physics 74 ไฟล์ (v2), regression 453 ไฟล์ และอื่นๆ ~70 ไฟล์ (legacy) | เก็บ physics ส่วน regression ต้องตรวจก่อนว่ายังมีอะไรเรียกใช้ |
| Superapp | อ่าน Harness ในฐานะ downstream; AI ห้ามเข้าไปดู (AGENTS §2) | **ผู้เขียนต้องเช็กเอง**ว่า Superapp อ่าน path ไหนบ้าง ก่อนเฟส 3 และ 5 |
| `topics/For Work/` | STANDARD §15 ยังบังคับใช้และห้ามแก้ | เก็บไว้ จนกว่าจะเขียนส่วนที่ยังใช้เข้า STANDARD |

## 2. รายการตัดสิน (เก็บ / ลบโดยเก็บใน tag / ถามผู้เขียน)

| พื้นที่ | ไฟล์ | ตัดสิน |
|---|---|---|
| `core/` theory card, author proposition, `02_equations`, `03_lanes`, `05_tests/physics`, `06_data`, contract ทั้งหมด, CORE_MAP | ~600 | **เก็บ** |
| `docs/standard`, `docs/STANDARD.md`, `docs/data/external` (เฉพาะที่ลงทะเบียน), `docs/scripts/standard`, `docs/scripts/maintenance` | ~880 | **เก็บ** |
| `WORK_LEDGER`, `AGENTS.md`, `.claude`, `.github` (หลังตัด step ที่ไม่ใช้) | ~140 | **เก็บ** |
| `docs/meta` ฉบับยุค v2 (retrospective, distinctness screen, ข้อเสนอ, audit, แผนนี้) | ~15 | **เก็บ** |
| topic ที่ record ของ v2 อ้าง (0.3, 0.13, 0.23, 0.25 เฉพาะ Doc ที่ถูกอ้าง) และ 0.18 ที่มีคนทำอยู่ | ~200 | **เก็บ** |
| `topics/For Work/` | 30 | **เก็บ** (§15) |
| `core/07_artifacts`, `topics/*/Result`, `_Logs` (output ที่ generate) | ~1,800 | **ลบ เก็บใน tag** |
| `core/08_history` | 319 | **ลบ เก็บใน tag** |
| topic engine, prose และข้อมูลของ topic ที่ไม่มี record อ้าง | ~3,800 | **ลบ เก็บใน tag** |
| `docs/scripts/audit` (ยกเว้นตัวที่ใช้), `Legacy`, `Data`, `Runners`, `Reporting`, `debug`, script SEO | ~950 | **ลบ เก็บใน tag** |
| `core/00_governance` ที่ไม่ใช่ contract (รายงาน migration, gate) | ~190 | **ลบ เก็บใน tag** |
| `core/05_tests/regression` และ test legacy อื่นๆ | ~520 | ลบ ถ้าการตรวจพบว่าไม่มีอะไรพึ่งพา |
| `docs/meta` ฉบับก่อน v2 | ~130 | **ลบ เก็บใน tag** |
| `docs/UET_Documentation_Details` (เอกสารสาธารณะ 524 ไฟล์) | 524 | **ถามผู้เขียน** ข้อเสนอ: ลบ แล้วเขียนหน้าเดียวที่บอกสถานะจริง |
| `services_and_experiments/uet_core` (Rust มี cargo check ใน CI) | 128 | **ถามผู้เขียน** AI ไม่รู้ว่าใช้ทำอะไร |
| `docs/knowledge_base` (pilot ค้นเอกสาร มี cost log และ API client) | 28 | **ถามผู้เขียน** |
| `docs/media`, ไฟล์ที่ root (`HISTORY_RECOVERY_LOG.md`, `verify_manuscript_gate.js` ฯลฯ) | ~120 | **ถามผู้เขียน** |

**คาดว่าจะลดจาก 9,760 ไฟล์ เหลือราว 1,900–2,700 ไฟล์** (ขึ้นกับคำตอบในหมวด "ถามผู้เขียน")
ข้อมูลภายนอกที่ลงทะเบียนไว้ไม่ถูกแตะ

## 3. เฟส

| เฟส | งาน | ความเสี่ยง | ต้องอนุมัติ |
|---|---|---|---|
| 1 หน้าแรกบอกความจริง | เขียน `README.md` และ `README.th.md` ใหม่ ให้บอกตรงๆ ว่า UET ยังไม่มีตัวเลขที่ทายต่างจากฟิสิกส์มาตรฐาน (`C_B4_DISTINCTNESS_AUDIT`) สิ่งที่มีคือการสังเคราะห์ ขอบเขต parameter และผลที่ตก | ต่ำ ไม่ลบอะไร | ตรวจข้อความ |
| 2 tag และแก้มาตรฐาน | ติด tag `archive/legacy-2026-11` แล้ว push; แก้ STANDARD §8 เป็น "legacy เก็บใน tag ไม่ใช่ใน tree"; ทำสคริปต์ตรวจการอ้างอิงแบบใช้ครั้งเดียว (ไม่ใช่ gate ใหม่) | ต่ำ | **ใช่** (แก้ §8, push tag) |
| 3 ลบ output และ history | `core/07_artifacts`, `Result`, `_Logs`, `core/08_history` | ต่ำ | ใช่ |
| 4 ลบ topic legacy | topic ที่ไม่มี record อ้าง; ตัด `run_all_tests.py` ออกจาก CI หรือย่อให้รันแค่ topic ที่เหลือ; แก้ `compileall` และ Pages | กลาง (CI, Superapp) | ใช่ |
| 5 ลบระบบราชการ | audit script ที่ไม่ใช้, governance ที่ไม่ใช่ contract, test regression, `docs/meta` ก่อน v2 | กลาง (contract อาจ STALE ถ้าพลาด) | ใช่ |
| 6 ส่วนที่ต้องถาม | เอกสารสาธารณะ, Rust core, knowledge base, media ตามที่ผู้เขียนตัดสิน | ขึ้นกับคำตอบ | ใช่ |
| 7 ย่อ claim | แยก claim ที่เป็นแค่ "ฟิสิกส์มาตรฐานเขียนด้วยคำของ UET" (~50 ข้อ) ออกจากตัวเลขที่รายงานบนหน้าแรก ไม่ลบหรือเปลี่ยนระดับ เพราะ §1 ห้ามลบ FAILED และการเปลี่ยนระดับต้องมีเหตุผลทางหลักฐาน | ต่ำ | ใช่ |

แต่ละเฟสใช้เวลาราวหนึ่ง session รวมทั้งหมดราว 5–7 PR

## 4. สิ่งที่ผู้เขียนต้องตอบก่อนเริ่ม

1. อนุมัติหลักการ "ลบจาก tree เก็บใน git tag" และการแก้ §8 ไหม
2. `docs/UET_Documentation_Details`, `services_and_experiments/uet_core`, `docs/knowledge_base` และ `docs/media` จะเก็บหรือลบ
3. Superapp อ่าน path ไหนของ Harness บ้าง (AI เข้าไปดูเองไม่ได้)
4. ตอนนี้มี session ไหนทำงานใน topic ไหนอยู่บ้าง นอกจาก 0.18
