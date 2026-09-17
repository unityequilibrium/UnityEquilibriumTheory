# Core File and Research Organization Standard

สถานะ: `ACTIVE`

มาตรฐานนี้ควบคุมการจัดไฟล์และการทำงานภายใน `docs/core/` โดยเฉพาะ ไม่ใช่สมการใหม่
และไม่ยกระดับสถานะทางฟิสิกส์ของงานใด

## 1. เหตุผลที่ต้องมีมาตรฐานนี้

`docs/core/` มี production modules, proof code, tests, specifications, research
notes, update logs และ generated artifacts อยู่ร่วม namespace เดียวกัน จำนวนไฟล์จึง
ไม่เท่ากับจำนวนสมการ และไฟล์ชื่อคล้ายกันอาจมีบทบาทกับหลักฐานคนละระดับ

ผลตรวจล่าสุดที่ใช้เป็นขอบเขตการจัดระบบ (ตัวเลขละเอียดให้ยึด generated artifacts):

- core-file manifest: 1,545 ไฟล์; Wave 1 จัด disposition ให้ review records เดิม 133 รายการครบแล้ว โดยยังมี scientific-link follow-up 133 รายการ
- code-surface และ equation inventory: ให้ยึด summary/records ใน `uet_code_surface_inventory.json` และ `uet_foundation_equation_inventory.json` ตามลำดับ ไม่คัดลอกตัวเลขเก่ามาเป็นสถานะถาวรใน prose
- `artifacts/` มี generated records จำนวนมากและยังเป็น flat namespace; การนับปัจจุบันให้ยึด `uet_core_file_manifest.json`
- core มีโฟลเดอร์ `02_Proof`, `artifacts`, `data`, `test` แต่ research/spec จำนวนมากยังอยู่ที่ root

ตัวเลขนี้เป็นขอบเขตการจัดระบบ ไม่ใช่คะแนนความถูกต้องของทฤษฎี

## 2. Source-of-truth hierarchy

เมื่อข้อมูลขัดกัน ให้ใช้ลำดับนี้:

1. `docs/core/07_artifacts/gates/uet_foundation_dependency_gate.json`
2. `docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json`
3. `docs/core/07_artifacts/gates/uet_foundation_equation_inventory.json`
4. `docs/core/07_artifacts/archive/uet_code_surface_inventory.json`
5. `docs/core/07_artifacts/archive/uet_core_equation_family_contract.json`
6. specification และ formula-audit ที่ถูก link จาก artifact
7. `README.md`, research report และ update log

Prose ที่มีจำนวนหรือสถานะเก่ากว่า artifact ต้องถูกติดเป็น drift แล้วซิงก์ภายหลัง
ห้ามแก้ generated JSON ด้วยมือเพื่อให้ตรงกับ prose

## 3. Logical file areas

ทุกไฟล์ใน core ต้องมีบทบาทหลักเพียงหนึ่งบทบาท:

| Logical area | บทบาท | ขอบเขตปัจจุบัน |
| :-- | :-- | :-- |
| `00_governance` | กติกาและ navigation | `AGENTS.md`, `README.md` |
| `01_contracts` | ontology, specification, formula/claim contract | `*_SPEC.md`, `*_CONTRACT.md` |
| `02_equations` | equation family หรือ production operator | family-owned Python modules |
| `03_lanes` | lane-specific comparator, source bridge, diagnostic | O(2), thermal, Topic 13 support |
| `04_proofs` | proof/derivation runners | `02_Proof/` และ proof modules |
| `05_tests` | unit, regression, artifact-boundary tests | `test/` |
| `06_data` | declared input data/source package | `data/` |
| `07_artifacts` | generated JSON, NPZ และ gates | `artifacts/` |
| `08_history` | update logs และ dated research notes | `*_UPDATE_LOG.md`, wave notes |
| `99_review` | ยังจัด owner/สถานะไม่ได้ | unlinked/ambiguous files |

นี่เป็น logical layout ก่อน physical layout เสมอ เพื่อไม่ทำให้ import และ link เดิมพัง

## 4. Machine-readable manifest

ไฟล์ควบคุมคือ:

- generator: `docs/scripts/audit/build_uet_core_file_manifest.py`
- manifest: `docs/core/07_artifacts/provenance/uet_core_file_manifest.json`
- human index: `docs/core/CORE_FILE_INDEX.md`
- organization policy: `docs/core/00_governance/uet_research_organization_policy.json`
- organization registry generator: `docs/scripts/audit/build_uet_research_organization_registry_v2.py`
- organization registry: `docs/core/07_artifacts/gates/uet_research_organization_registry.json`
- migration map: `docs/core/07_artifacts/archive/uet_core_file_migration_map.json`
- organization audit: `docs/core/07_artifacts/gates/uet_core_organization_audit.json`
- scientific-link audit: `docs/core/07_artifacts/verification/uet_core_scientific_link_audit.json`
- equation-family contract: `docs/core/07_artifacts/archive/uet_core_equation_family_contract.json`
- central formula correspondence registry:
  `docs/core/07_artifacts/correspondence/uet_equation_correspondence_registry.json`

ทุก record ต้องมีอย่างน้อย:

```text
path
file_kind
logical_area
owner_family_or_lane
registry_link_status
status_source
generated_or_source
sha256
review_action
```

สำหรับ equation-bearing code ให้เพิ่ม family, formula registry, verifier/test paths,
unit lane และ claim ceiling

ถ้า family ถูกระบุว่า `organization_review_required` จะต้องผ่าน bounded scientific-link
review ก่อน แม้ source path จะถูกประกาศใน family contract แล้วก็ตาม โดยต้อง materialize
formula IDs, unit lane, verifier paths, artifact paths และ claim ceiling จาก contract หรือ
registry ที่ตรวจสอบย้อนกลับได้

การ assign ครบทุก path ไม่ได้แปลว่าสมการถูกพิสูจน์แล้ว แต่แปลว่าไม่มีไฟล์หลุดจากการ
ตรวจสอบโดยไม่รู้ตัว

## 5. กฎการเพิ่มและแก้ไฟล์

ก่อนเพิ่มหรือแก้ไฟล์ใน core:

1. อ่าน `AGENTS.md` และ source-of-truth artifacts
2. สร้างหรือ refresh core-file manifest
3. refresh organization registry และ migration map
4. ระบุ owner family/lane และ logical area
5. รัน scientific-link audit เพื่อแยก organization assignment ออกจาก scientific linkage
6. แยก equation, support, comparator, verifier, artifact และ history
7. ผูก formula → implementation → verifier → artifact → source
8. อัปเดต manifest, registry, link audit และ update log ใน wave เดียวกัน

สำหรับ family ใหม่ให้แยกให้ชัดระหว่าง “มี family contract” กับ “ผ่าน physics gate”:
การมี formula/verifier/artifact chain หมายถึง traceability ครบขึ้นเท่านั้น ไม่ได้เลื่อน
`evidence_status`, foundation gate หรือ claim boundary โดยอัตโนมัติ

ห้ามเพิ่มไฟล์ใหม่ที่ root ของ `docs/core/` หากอยู่ใน logical area เดิมได้
หากต้องรักษา legacy path ให้ใช้ adapter/index และบันทึกเหตุผล

## 6. Artifact, reference และ log rules

- JSON/NPZ ใน `artifacts/` ต้องสร้างจาก generator ไม่เขียนผลด้วยมือ
- test ต้องตรวจ schema, input identity, hash, threshold และ claim boundary
- log บอกว่าอะไรเปลี่ยนและอะไรเป็น blocker; log ไม่แทน artifact
- research note ที่ยังไม่ผ่าน gate ต้องติด `DRAFT`, `CANDIDATE`, `INTERNAL`,
  `SIMULATION_ONLY`, `WARN` หรือ `BLOCKED`
- `Result/` ของ topic ไม่ถูกคัดลอกมาเป็น core evidence โดยไม่มี provenance link
+ การอ้างหนึ่งผลต้องย้อนกลับได้อย่างน้อย `source → formula/spec → code → verifier → artifact`
+  และ formula ID ต้องอยู่ใน central correspondence registry
+- named normalized branches เช่น `core.matter_space_flux` ต้องระบุว่าเป็น branch/comparator
+  เฉพาะ lane; ห้ามใช้ branch นั้นแทนสมการ matter-space อื่นหรือแปลง normalized quantity
+  เป็น SI โดยไม่มี observable/unit contract

## 7. Physical migration policy

wave แรกทำ logical registration เท่านั้น ยังไม่ย้ายไฟล์จำนวนมาก
การย้ายจริงต้องผ่าน:

1. manifest ระบุ owner และ target path ครบ
2. import/link scan ไม่พบ broken path และมี compatibility adapter เมื่อจำเป็น
3. targeted tests, artifact parse และ generator rerun ผ่าน

ไฟล์ legacy ไม่ถูกลบ ให้ติด `LEGACY` หรือ `QUARANTINED` และคง historical path ไว้จนกว่า
reviewer จะอนุมัติ migration

## 8. Definition of done

organization wave ถือว่าเสร็จเมื่อ reviewer ตอบได้ทันทีว่า:

- ไฟล์นี้เป็นอะไรและใครเป็นเจ้าของ
- สถานะมาจาก artifact ไหน
- สมการผูกกับ verifier และ output ใด
- ไฟล์นี้เป็น source หรือ generated output
- ถ้าแก้ไฟล์นี้ต้องรันอะไร
- blocker ปัจจุบันคืออะไร

การจัดโฟลเดอร์ให้สวยขึ้นแต่ตอบคำถามเหล่านี้ไม่ได้ ถือว่ายังไม่เสร็จ
