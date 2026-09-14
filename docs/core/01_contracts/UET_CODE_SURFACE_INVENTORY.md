# UET Code-Surface Inventory

F0 ยังไม่จบเพียงการอ่าน `FORMULA_AUDIT.md` เพราะ implementation อาจมีสมการที่ยังไม่ถูก
เขียนลง registry ดังนั้นจึงมี static scan ของ core Python modules แยกออกมา

ผลเครื่องอยู่ที่
[`uet_code_surface_inventory.json`](artifacts/uet_code_surface_inventory.json)
และสร้างซ้ำได้จาก
[`build_uet_code_surface_inventory.py`](../scripts/audit/build_uet_code_surface_inventory.py)

## ผลปัจจุบัน

- core implementation/proof modules ที่สแกน: `32` ไฟล์
- candidate equation-like surfaces: `1450` จุด
- ไฟล์ที่ยังไม่มี path link ใน formula inventory/registry: `25` ไฟล์
- gate: `BLOCKED`

นี่ไม่ใช่การบอกว่า 1450 จุดเป็นสมการฟิสิกส์ 1450 สมการ แต่เป็นรายการที่อาจมี
mathematical/physical behavior และยังไม่มี ontology, units, derivation หรือ observable link
จึงต้องตรวจต่อหรือ quarantine เป็น implementation support

## หลักการไม่ให้ static scan overclaim

ทุก candidate ถูกตั้งค่าเริ่มต้นเป็น:

```text
registry_link_status = REVIEW_REQUIRED
ontology_status       = OPEN
unit_status           = OPEN
derivation_status     = OPEN
claim_status          = NOT_EVIDENCE
```

candidate จะกลายเป็นสมการของทฤษฎีได้ก็ต่อเมื่อผ่าน F1–F8 และมีการเชื่อมกับ formula registry
อย่าง explicit การมีชื่อ `energy`, `mass`, `beta`, `kappa`, `potential` หรือ `np.sqrt` ในโค้ด
ไม่ใช่หลักฐานว่าความหมายนั้นปิดทางฟิสิกส์แล้ว

## ผลต่อเป้าหมายวิจัย

ตอนนี้เรารู้เพิ่มอย่างเป็นระบบว่า “ยังตอบว่าไม่ขัดทั้งหมดไม่ได้” ไม่ใช่เพราะพบว่า
คณิตศาสตร์ของ UET ผิดทั้งหมด แต่เพราะมี code surface จำนวนมากที่ยังไม่ได้ผ่าน
correspondence/units/derivation gate

ดังนั้นการปิดคำถามระดับทฤษฎีต้องเริ่มจากการจัดประเภท candidate เหล่านี้เป็น:

1. ส่วนหนึ่งของสมการ core ที่ต้องเพิ่มเข้า registry
2. constitutive/application equation ที่ต้องมี lane ของตัวเอง
3. standard baseline/comparator
4. numerical implementation detail
5. dead/legacy code ที่ต้อง quarantine

จนกว่าการจัดประเภทนี้จะเสร็จ foundation status ต้องคง `BLOCKED`

