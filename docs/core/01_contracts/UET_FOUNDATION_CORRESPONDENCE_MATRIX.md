# UET Foundation Correspondence Matrix

เอกสารนี้เป็นชั้นคัดเลือกจาก F0 inventory สำหรับตอบคำถามเชิงทฤษฎีโดยตรง
ไม่ใช่การแทนที่ inventory ทั้ง 260 rows

ผล machine-readable อยู่ที่
[`uet_foundation_correspondence_matrix.json`](artifacts/uet_foundation_correspondence_matrix.json)
และสร้างซ้ำได้จาก
[`build_uet_foundation_correspondence_matrix.py`](../scripts/audit/build_uet_foundation_correspondence_matrix.py)

## กติกาการอ่านผล

แต่ละ row แยกสถานะออกเป็นสามแกน:

1. `compatibility_status` — relation ตรงกับ counterpart หรือมี conflict/blocked หรือไม่
2. `uet_derivation_status` — UET derive relation นั้นจริงหรือเป็น standard/baseline/heuristic
3. `special_case_status` — ทฤษฎีเดิมเป็น limit ของ UET ที่ตรวจแล้วหรือเป็นเพียง comparator

การผ่านแกนแรกไม่ทำให้แกนที่สองหรือสามผ่านอัตโนมัติ

## ผลรวมรอบนี้

มี critical rows `19` รายการ และ matrix status เป็น `BLOCKED` เพราะ inventory และ core
compatibility gate ยัง blocked

### สิ่งที่เข้ากันได้ในฐานะ baseline มาตรฐาน

- Landauer lower bound
- Newtonian weak-field acceleration
- Rydberg hydrogen spectrum
- singlet-state quantum correlation
- Cahn–Hilliard formในฐานะ standard constitutive comparator

สิ่งเหล่านี้แปลว่า “สูตรมาตรฐานไม่ขัดกับตัวมันเองใน lane ที่ประกาศ” ไม่ได้แปลว่า UET
derive สูตรนั้นจากสมการหลัก

### สิ่งที่เป็น UET bridge แต่ยัง derive ไม่เสร็จ

- electroweak weak-angle correction
- PMNS geometric angle bridge
- Koide/mass hierarchy inference
- QCD correction, scale-running points
- cosmic dynamic-frame velocity combination
- vacuum/dark-energy anchor

แต่ละรายการยังต้องมี action/functional หรือ physical correspondence ที่แสดงว่าพารามิเตอร์
มาจากไหน ไม่ใช่เพียงให้ค่าตัวเลขใกล้ benchmark

### สิ่งที่เป็น blocker จริง

- `uet.legacy.master_potential`: potential กับ derivative ขัดกันเชิงคณิตศาสตร์
- `T01-001`: 0.1 ยังเป็น formula scaffold จึงทดสอบ special case ไม่ได้
- `T05-QCD-010`: formula audit รายงาน implementation/data-shape issue และ origin ของ correction ยังเปิด
- `uet.matter_space.candidate`: derivative/ledger ผ่านภายใน แต่ causal leakage ยังทำให้ physical promotion blocked

## คำตอบเชิงทฤษฎีจาก matrix

ตอนนี้ยังสรุปไม่ได้ว่า “สมการใหม่ครอบคลุมทฤษฎีเก่าทั้งหมด” เพราะมีเพียงบาง relation
ที่เป็น standard baseline หรือ conditional limit ใน lane เฉพาะ ตัวอย่างที่แข็งแรงที่สุดคือ
covariant GR null contract และ O(2) finite-density EOS แต่ทั้งคู่ยังไม่ใช่ proof ของ
legacy master equation หรือของจักรวาลทั้งระบบ

หลักที่ปิดได้ในระดับ methodological foundation คือ:

\[
\text{baseline compatibility}
\neq
\text{UET derivation}
\neq
\text{special-case proof}
\neq
\text{empirical validation}.
\]

นี่คือเส้นแบ่งที่ต้องใช้กับทุก topic ต่อจากนี้

