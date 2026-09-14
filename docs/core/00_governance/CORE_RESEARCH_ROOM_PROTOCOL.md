# Core Research Room Protocol

สถานะ: `ACTIVE`

เอกสารนี้กำหนดวิธีแบ่งงานระหว่างห้องวิจัยที่แตะ `docs/core/` โดยเน้นลดการอ่านซ้ำ
และทำให้ทุกผลส่งมอบย้อนกลับไปยังสมการ, code, verifier และ artifact ได้

## 1. บทบาทของห้อง

### Control tower

ดูเฉพาะ dependency graph, foundation gate, file manifest และ handoff ล่าสุด
ทำหน้าที่เลือก blocker ถัดไปและรับผลจากห้องเจ้าของ lane ไม่ทำการทดลองเดียวกันซ้ำ

### Core foundation room

ดูแล ontology, equation registry, family contract, units, derivation และ core gates
มีสิทธิ์แก้ shared contract แต่ไม่แก้ผลหรือ interpretation ของ topic โดยไม่มี handoff

### Lane room

แต่ละห้องดูแล lane เดียว เช่น thermal, phase, O(2), gravity หรือ carrier
ต้องใช้ core contract เป็น dependency และส่ง artifact/metric กลับ ไม่ส่ง prose ทฤษฎีซ้ำ

### Review/organization room

ดูแลเฉพาะการ assign file owner, path, status, generator และ link chain
ห้ามแก้สมการเพื่อแก้ปัญหา organization

## 2. กฎหนึ่งห้องหนึ่งงาน

หนึ่งรอบของห้องต้องมี:

- หนึ่ง controlling blocker
- หนึ่งชุดไฟล์ที่อยู่ใน scope
- หนึ่ง verifier หรือ audit ที่เกี่ยวข้อง
- หนึ่ง artifact/index/log ที่อัปเดต
- หนึ่ง handoff ที่มี next action เดียว

ถ้าพบ blocker คนละประเภท ให้แยกเป็นรอบใหม่ เช่น provenance, formula, units และ claim
ไม่รวมเป็นงานเดียวเพียงเพื่อให้ดูคืบหน้าเร็ว

## 3. Token-saving reading protocol

ก่อนอ่านไฟล์ลึก ให้ทำตามลำดับ:

1. `docs/core/CORE_FILE_INDEX.md`
2. `docs/core/artifacts/uet_core_file_manifest.json` เฉพาะ record ที่อยู่ใน scope
3. foundation gate หรือ topic gate ล่าสุด
4. specification/FORMULA_AUDIT ที่ artifact ชี้เท่านั้น
5. code และ test ที่เกี่ยวข้องกับ blocker เดียว

ห้ามอ่าน `docs/core/` ทั้งโฟลเดอร์เพื่อเริ่มงานหนึ่งชิ้น และห้ามคัดลอก report เก่าทั้งฉบับ
เข้าห้องใหม่

## 4. Handoff format

ทุกห้องต้องส่งกลับด้วยหัวข้อนี้:

```text
STATUS: PASS | PARTIAL | BLOCKED | WARN
SCOPE: file paths หรือ family/lane เดียว
CONTROLLING_BLOCKER: ตัวควบคุมหนึ่งรายการ
WHAT_CHANGED: ไฟล์/artifact ที่เปลี่ยนจริง
VERIFICATION: คำสั่งหรือ audit ที่รันจริง
RESULT: metric/threshold/hash ที่สำคัญ
CLAIM_BOUNDARY: สิ่งที่ผลนี้ยังอ้างไม่ได้
NEXT_ACTION: งานถัดไปหนึ่งงาน
```

ถ้ายังไม่มี artifact หรือ verifier ใหม่ ให้ระบุ `NO_EVIDENCE_CHANGE` และไม่เลื่อนสถานะ

## 5. Parallel schedule

ทำพร้อมกันได้ไม่เกินสามห้องในช่วง foundation:

| ห้อง | งานที่อนุญาต | ไม่ควรทำ |
| :-- | :-- | :-- |
| core organization | manifest, owner, link, metadata | เปลี่ยน physical equation |
| Topic 0.13 | thermal source/units/observable blocker | ใช้ holdout ปรับ parameter |
| Topic 0.11 | replicate/estimator/uncertainty blocker | อ้าง universality จาก pilot |

ห้อง O(2), gravity, galaxy, particle และ cosmology รอ dependency ที่เกี่ยวข้อง
เว้นแต่ทำเฉพาะ audit หรือ no-go ที่ไม่เลื่อน claim

## 6. Core file change protocol

ก่อนแก้ไฟล์:

1. ตรวจ owner ใน core-file manifest
2. ตรวจ equation family contract และ current gate
3. ระบุว่าเป็น source, generated output, test, support หรือ history
4. แก้ source/generator ก่อน generated artifact
5. rerun เฉพาะ verifier ที่ evidence-producing state เปลี่ยน
6. refresh manifest/index
7. เขียน update log และส่ง handoff

การเปลี่ยนชื่อหรือย้ายไฟล์ต้องเป็น migration wave แยกต่างหาก มี import/link scan,
compatibility shim และ targeted tests ครบก่อนลบ path เดิม

## 7. Current organization queue

ลำดับ review ของ core ตอนนี้:

1. `unassigned_python_surface` — assign เข้า equation family หรือ support/quarantine
2. `lane_specific_module` — ระบุ lane, formula registry และ evidence class
3. specification/research notes — ผูกกับ owner และ current artifact
4. generated artifacts — ตรวจ generator, status และ provenance link; ไม่ย้ายมือ
5. physical migration — ทำหลัง queue ข้างต้นเป็นศูนย์หรือมีเหตุผลคง legacy path

การลดจำนวนไฟล์ไม่ใช่เป้าหมายหลัก เป้าหมายคือทำให้ทุกไฟล์มี owner, role, source/status
และ next action ที่ตรวจได้

