# UET Foundation Equation Inventory

นี่คือผลของ Gate F0: ตรวจว่าสมการที่ repository ประกาศไว้มีอะไรบ้าง ก่อนตัดสินว่า
สมการใดขัดกับคณิตศาสตร์/ฟิสิกส์มาตรฐาน หรือเป็นกรณีพิเศษของทฤษฎีเดิม

ผลเชิงเครื่องอยู่ที่
[`uet_foundation_equation_inventory.json`](artifacts/uet_foundation_equation_inventory.json)
และสร้างซ้ำได้จาก
[`build_uet_equation_inventory.py`](../scripts/audit/build_uet_equation_inventory.py)

## ผลการสแกน

- พบ `FORMULA_AUDIT.md` จำนวน `27` ไฟล์
- อ่านได้ `260` formula rows
- ไม่พบ formula ID ซ้ำหลังตัดตารางที่ไม่ใช่ formula registry ออก
- topic `0.1` ยังเป็น scaffold ทั้งหมด `10` rows จึงถูก `BLOCKED`
- inventory gate: `BLOCKED` เพราะยังไม่ครอบคลุมสมการที่อยู่เฉพาะใน Python code/README และยังไม่มี correspondence/observable map ครบทุก row

การที่ inventory audit ทำงานสำเร็จ (`PASS_WITH_DISCLOSED_GAPS`) ไม่ได้หมายความว่า
สมการ 260 รายการถูกตรวจว่าถูกต้องแล้ว แต่หมายความว่าเรารู้แล้วว่าสิ่งที่ต้องตรวจมีอะไร
และยังขาดอะไรอยู่

## การแบ่งสถานะจากหลักฐานเดิม

| ชั้น | จำนวน | ความหมาย |
|---|---:|---|
| `STANDARD_OR_BENCHMARK` | 60 | สูตรมาตรฐานหรือ benchmark ที่ใช้เป็น counterpart; ยังไม่ใช่ UET derivation |
| `INTERNAL_CHECKED` | 17 | ตรวจความสัมพันธ์ใน implementation/benchmark ภายในแล้ว แต่ยังไม่ใช่ physical validation |
| `OPEN_OR_HEURISTIC` | 88 | มี bridge/สมมติฐานหรือหน่วย/ที่มาที่ยังเปิด |
| `REVIEW_REQUIRED` | 85 | registry มีสูตร แต่ metadata ยังไม่พอให้จัดสถานะเชิงฟิสิกส์ |
| `SCAFFOLD_BLOCKED` | 10 | ยังไม่มีสูตร explicit และหน่วย/ที่มาเปิดอยู่ |

สถานะเหล่านี้เป็น evidence labels ไม่ใช่คะแนนรวมของทฤษฎี

## Correspondence ที่อ่านได้ชัดจาก inventory

### Standard counterpart ที่ยังไม่ใช่ UET proof

- `PT-CH-EVOLUTION`: Cahn–Hilliard form ใน topic 0.11 เป็น standard constitutive comparator ที่
  ตรวจ implementation ภายในได้ แต่ยังต้องกำหนดว่า UET coupling เพิ่มอะไรและ observable คืออะไร
- `T13-004`: \(E_{\min}=k_BT\ln2\) เป็น Landauer lower-bound relation ที่มีหน่วย SI ถูกต้อง
  ใช้เป็น thermodynamic constraint ได้ แต่ไม่ใช่ derivation ของ `beta`
- `GR19-NEWTON-ACCELERATION`: \(g=GM/r^2\) เป็น Newtonian baseline ไม่ใช่หลักฐานว่า UET derive gravity
- Rydberg, SEMF, PMNS และสูตรมาตรฐานอื่น ๆ ต้องถูกเก็บเป็น baseline/benchmark จนกว่าจะมี UET derivation

### UET bridge ที่ยังเปิด

- `EW-01`: weak-angle correction มี `bridge_factor` แบบ heuristic
- `NUPMNS-ANGLE-GEOM`: มุม neutrino เป็น benchmark-gated heuristic bridge
- `T17-PLANCKEXP-005`: mass ansatz แบบ exponential ยังไม่มี derivation หรือ parameter provenance ครบ
- `T26-002` ถึง `T26-009`: cosmic-fluid/viscosity/dynamic-frame relations เป็น heuristic หรือ analogy
- `PT-UET-LEGACY-INFO` และ spatial information candidate: เป็น legacy/candidate comparator ไม่ใช่ physical derivation

### Foundation ที่ยังต้องตรวจเพิ่ม

- `0.1` ยังไม่มี explicit formula registry ที่แทน calculation path ได้ จึงห้ามใช้เป็นหลักฐาน
  รองรับ galaxy-level claim
- `0.11` มี Cahn–Hilliard structure และ diagnostics แต่ยังต้องเชื่อมกับ matter–space functional
  ด้วย derivative/unit/observable map เดียวกัน
- `0.13` แยก Landauer identity, Bekenstein/Hawking/Unruh identities, synthetic Cattaneo และ
  vacuum-sink hypothesis ออกจากกันได้แล้ว แต่แต่ละ lane มี evidence class ต่างกัน
- `0.19` มี Newton/GR standard formulas และ constant checkpoint แต่ยังไม่ใช่ UET field-equation derivation
- `0.23` ใช้ normalized cross-domain functional; ยังพิสูจน์ unity of scale ไม่ได้เพราะ dimensionalization
  และ parameter running ยังเปิด
- `0.26` reuse galaxy/flow/drag formulas หลายตระกูล; จึงยังรวมเป็น “cosmic dynamic equation” เดียวไม่ได้

## คำตอบต่อคำถามเรื่องความขัดแย้ง

จาก inventory เพียงอย่างเดียว ยังสรุปไม่ได้ว่าสมการทั้งหมดขัดหรือไม่ขัดกับฟิสิกส์สากล
เพราะหลาย row ยังไม่มีหน่วยหรือ derivation ที่ปิด แต่ inventory ทำให้แยกได้ว่า:

1. สูตรมาตรฐานที่ใช้เป็น baseline ไม่ได้ขัดในตัวมันเอง
2. UET bridge ที่ยังไม่มี counterpart/derivation ต้องใช้คำว่า `OPEN_OR_HEURISTIC`
3. สมการ core ที่ implementation ขัดกับสมการประกาศถูกส่งต่อไปยัง
   [compatibility audit](../08_history/research_notes/UET_FOUNDATION_COMPATIBILITY_AUDIT.md) เป็น `CONTRADICTION` หรือ `CONFLICT`
4. การที่ benchmark ผ่านไม่สามารถยกระดับ bridge ให้เป็นทฤษฎีที่ derive แล้ว

ดังนั้นคำตอบปัจจุบันที่แม่นยำคือ:

> ยังไม่มีหลักฐานว่าทฤษฎี UET ทั้งระบบขัดกับคณิตศาสตร์สากล แต่ก็ยังไม่มีหลักฐานว่ามันสอดคล้องและครอบคลุมฟิสิกส์สากลทั้งหมด เพราะหลายสมการยังเป็น bridge, comparator หรือ scaffold และบาง implementation ขัดกับสมการที่ประกาศเอง

## กติกาเลื่อนจาก inventory ไปสู่การพิสูจน์

แต่ละ row จะผ่านลำดับเดียวกัน:

```text
inventory
→ variable ontology
→ standard counterpart
→ units
→ derivation class
→ mathematical residual
→ numerical convergence
→ observable map
→ real-data holdout
→ claim
```

หาก row ใดไม่มี standard counterpart, unit closure, derivation status หรือ observable map
จะคงไว้ที่ `OPEN`, `HEURISTIC`, `DIAGNOSTIC` หรือ `BLOCKED` ไม่เลื่อนด้วยผลตัวเลขเพียงอย่างเดียว

