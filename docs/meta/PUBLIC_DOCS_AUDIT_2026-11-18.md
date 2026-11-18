# ตรวจเอกสาร public ก่อนอัปเดต (2026-11-18)

> ร่างโดย Claude เป็นงานรวบรวมข้อมูล ยังไม่ได้แก้ README หรือเอกสารใดเลย
> ตรวจบน `main` ที่ `cc1bfc578` (หลัง merge PR #61)

## 1. ปัญหาที่เจอ

### README.md (758 บรรทัด): ขัดกับ Standard v2 และเจตนาผู้เขียน

| จุด | สิ่งที่ README เขียน | ปัญหา |
|---|---|---|
| ชื่อเรื่อง | "UET v0.9.0: The Thermodynamics of Ethics Framework" และคำคม "moral negotiation" | ผู้เขียนบอกเมื่อ 2026-11-17 ว่า UET คือขั้นตอนคำนวณเดียวเพื่อปรับปรุงระบบใด ๆ ไม่ใช่ฟิสิกส์ใหม่ |
| badge | "Millennium_Problems-8_Mapped", "Topics-38_Master_Domains" | อ้างเกินหลักฐาน |
| "Big Picture Dashboard: 38 Solutions" | Millennium Problems, "Impossible" physics anomalies | ไม่มี claim ใดใน `claims.json` รองรับ |
| "Test Results (v0.9.0)" | ✅ Galaxy rotation "no dark matter needed", Muon g-2 "0.0σ (exact match!)", "816x faster than Navier-Stokes" | ใช้คำต้องห้าม (exact) ไม่มี Result record รองรับ มีแค่ป้ายบอกว่าเป็น historical |
| Topic index | 0.1 "Solved without Dark Matter", 0.10 "Turbulence Solved", 0.18 "P vs NP / Riemann Solved" | คำต้องห้าม "solved" และลิงก์ยังชี้ไป `docs/topics/` |
| "Questions Answered by UET (SEO)" | "Navier Stokes smoothness ... is proved" | คำต้องห้าม "proved" และเป็นเนื้อหาเพื่อ SEO |
| "Uet-Cash Mining System" | โครงสร้าง blockchain, mining, rewards | ไม่เกี่ยวกับงานวิจัย ควรออกจาก README |
| ภาคผนวก "ถ้อยคำที่ปรับในรอบนี้" | ตารางคำเก่าเทียบคำใหม่ | เป็นบันทึกภายใน ไม่ใช่ของผู้อ่าน |
| ลิงก์ | 99 จุดยังชี้ `docs/topics/` หรือ `docs/core/` | ลิงก์เสียตั้งแต่ย้ายโฟลเดอร์ใน PR #60 |

เนื้อหาที่ยังใช้ได้: หัวข้อ "อัปเดตงานวิจัยล่าสุด" (บรรทัด 70–149) และ "The Core Equation" (248–379) ซึ่งเขียนตามมาตรฐานใหม่แล้ว แต่ยาวและใช้ศัพท์ภายในมาก

### เอกสารอื่น

| ไฟล์ | ลิงก์เก่า | หมายเหตุ |
|---|---|---|
| `CONTRIBUTING.md` | 12 | คำ "exact"/"verified" ที่เจอเป็นภาษาขั้นตอนงาน ไม่ใช่ข้ออ้าง |
| `core/README.md` | 2 | "exact rewrite" ใช้ในความหมายทางคณิตศาสตร์ (เขียนรูปเทียบเท่า) ยอมรับได้ |
| `topics/README.md` | 1 | ใช้ "predicts" กับ T007 ซึ่งไม่ใช่ `BLIND_PREDICTION` ต้องเปลี่ยนคำ; มีสถานะแบบเก่า (`Draft`, เกรด `B`) 5 จุด |
| `docs/README.md` | 3 | — |
| `CONTEXT.md`, `CONTEXT-MAP.md` | 1, 3 | — |

### งาน README ของ Codex (branch `codex/repo/root-layout-repair`, ยังไม่ merge)

แก้แค่ path ส่วน "38 Solutions", Millennium, Test Results เก่า, SEO และ Uet-Cash ยังอยู่ครบ
branch เดียวกันมีการย้าย `For Work/` ที่ผู้เขียนไม่ได้อนุมัติ จึงไม่ควรต่อยอดจาก branch นี้

## 2. หลักฐานจริงที่ README ควรแสดง (จาก `docs/standard/`)

ใน `main` มี 19 claims: `L1_CONSISTENT` 12, `L2_CONFRONTED` 7 ไม่มี `L3` ไม่มี `FAILED`

| Test | ผล | เรื่อง |
|---|---|---|
| T001 | L2 PASS | binary pulsar ตัดช่วง coupling ของ UET ออก |
| T002 | L2 INCONCLUSIVE | สัดส่วนดาวตามช่วงชีวิต |
| T005 | L2 PASS | ขอบเขต fifth force จำกัด portal coupling |
| T006 | L2 PASS | มวลที่ดวงอาทิตย์เสียไปกับการใช้พลังงาน |
| T007 | L2 PASS | การแข่งขันทรัพยากรของ Tilman (chemostat) |
| T008 | L2 PASS | luminosity function ของดาวแคระขาว |
| T009 | L2 PASS | สมดุลของสาย U-238 → U-234 |

ยังไม่อยู่ใน `main`: T010–T013 และ T021 (L2) อยู่ใน PR #59

ข้อเท็จจริงที่ README ต้องพูดตรง ๆ (จาก R_B4 และงาน 2026-11-10): แต่ละชั้นของ UET ลดรูปเป็นทฤษฎีที่มีอยู่แล้ว
และยังไม่มีการทำนายที่เป็นของ UET โดยเฉพาะ

## 3. โครง README ใหม่ที่เสนอ

1. UET คืออะไร: ใช้คำของผู้เขียนจาก `core/AUTHOR_PROPOSITION.md` และข้อชี้แจง 2026-11-17 (ขั้นตอนคำนวณเดียว ระบบซ้อนกัน ทรัพยากรซ้อนทับ เวลานับเป็นทรัพยากร)
2. สถานะหลักฐานตอนนี้: ตารางจาก `claims.json` สร้างจากไฟล์โดยตรง ไม่พิมพ์มือ รวมผลไม่ผ่านและ INCONCLUSIVE
3. สมการแกนแบบสั้น และลิงก์ไปรายละเอียดใน `core/README.md`
4. วิธีวิจัย: สรุป Standard v2 ห้าบรรทัด และลิงก์
5. แผนที่ repo: `core/`, `topics/`, `docs/standard/`, `WORK_LEDGER/`
6. วิธีรันและทำซ้ำผล
7. ประวัติ: ข้ออ้างเก่าย้ายไปไฟล์เดียว (`docs/history/LEGACY_CLAIMS.md`) ระบุชัดว่าไม่ได้ทบทวน

## 4. การตัดสินของผู้เขียน

ตัดสินแล้ว (2026-11-18):
- Uet-Cash: เอาออกจาก README ทั้งหมด เพราะเป็นคนละโปรเจกต์แล้ว
- เวอร์ชัน: README ใหม่ใช้ v0.9.1

ข้อเสนอของ Claude ที่รอผู้เขียนตอบ:
1. ข้ออ้างเก่า (38 Solutions, Millennium, Test Results v0.9.0, SEO): ย้ายไป `docs/history/LEGACY_CLAIMS.md` ติดป้าย `LEGACY_UNREVIEWED` ไม่ลบ เพื่อให้คนตรวจย้อนได้ว่าเคยอ้างอะไร
2. ภาษา: `README.md` เป็นภาษาอังกฤษ ลิงก์ไป `README.th.md` ฉบับไทยเต็มที่บรรทัดแรก ไม่ผสมสองภาษาในย่อหน้าเดียวกัน
3. การย้าย `For Work/` ของ Codex ที่ไม่ได้อนุมัติ: ไม่ merge และให้ Claude แยกงานซ่อม path ที่ดีของมันออกมาทีหลัง
