# คำสั่งสำหรับเริ่ม Goal: Topic 13 research portfolio

สถานะ: เตรียมไว้สำหรับผู้ใช้เริ่ม Goal mode; การสร้างไฟล์นี้ยังไม่เริ่ม Goal หรือ automation

## Objective

ดำเนินงานตาม `docs/topics/0.13_Thermodynamic_Bridge/RESEARCH_PLAN_14D_FUNDING_2026-09-27.md` และ planning contract `docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/funding_portfolio_14d_plan.json` ให้ได้ผลหลัก `T13_HE4_PREDICTIVE_CONTENT_AND_MEASUREMENT_DESIGN` พร้อมพอร์ตยื่นทุนที่ตรวจซ้ำได้ ภายใน 11 ตุลาคม 2026 ตามกรอบสองสัปดาห์ของผู้ใช้

ปิดคำถามว่า He-4/O(2) bridge ที่แช่แข็ง calibration แล้วกำหนด independent dynamic response ได้หรือไม่ และต้องวัดอะไรเพิ่มจึงแยกคำตอบได้ ผลสำเร็จต้องมี predictive-content derivation หรือ scoped nonidentifiability proof ที่เพิ่มจาก matching identity เดิม พร้อม measurement design และชุดหลักฐาน ไม่ใช้จำนวน artifacts/PASS เป็นเกณฑ์สำเร็จ

## Start and continue

โมเดลแนะนำสำหรับ Goal owner คือ GPT-6 Astra / high; ใช้ xhigh เฉพาะ derivation/no-go review ที่ต้องเพิ่ม effort และใช้ GPT-6.1 Sol / high กับ implementation เมื่อมีการแบ่งงานที่รองรับจริง หากใช้ได้ตัวเดียวและโควตาจำกัด ให้ใช้ Sol 6.1 / high โดยไม่ลดเกณฑ์ตรวจ อ่าน `RESEARCH_ROADMAP_MODELS_12W_2026-09-27.md` โดยเฉพาะ revision 1 ตุลาคม สำหรับสถานะปัจจุบัน แพ็ก A–E และแผน W3–W12 คำแนะนำนี้ไม่ได้สั่งเปลี่ยนโมเดลหรือเปิดห้องอื่นอัตโนมัติ

1. อ่าน AGENTS, topic standards และแผน ตรวจ current goal ก่อนสร้างเป้าหมายซ้ำ เริ่ม D01 จากข้อมูลปัจจุบัน; วันในตารางคือวันครบกำหนด สามารถทำล่วงหน้าเมื่อ prerequisites พร้อม
2. ยืนยัน hashes ใน baseline กับไฟล์จริง หากเปลี่ยน ให้บันทึกเหตุและเลือก snapshot อย่างตรวจสอบได้ ไม่ยึดสถานะจากข้อความแชท ย้ายเฉพาะ committed source/protocol J02 ที่ต้องใช้จาก `c42385d07e390b338096122275fe809737b8477a` หลังตรวจ dependency; อย่าเขียนทับอีกห้อง
3. ใช้ `py` หรือ runtime ที่ตรวจพบจริงเพื่อรัน tests; ไม่สรุปว่า pytest ไม่มีเพราะ `python` ชี้ Microsoft Store alias บันทึก environment ที่ใช้ ไม่ติดตั้ง dependency ที่โจทย์หลักไม่ใช้
4. ทำ G0/G1 และ preregister ก่อนคำนวณเปรียบเทียบ Freeze theta_T, Z_Phi, e0, alpha, eta, source roles และ protocol parameters ด้วย provenance ทุกตัว
5. ทำ source pass คู่ขนานกับ derivation ได้ จำกัดค้น 6 ชั่วโมงงานเข้มข้นและตัดสิน D03; การขาด source ไม่ใช่ proof of no-go
6. ตัดสิน predictive/structural/unresolved ภายใน D05 ตาม operator และหลักฐานจริง ไม่เพิ่ม complete two-fluid state/transport theory เพียงเพื่อทำ comparison ให้ได้ทัน
7. Structural route ต้องมี analytic/constructive proof, admissibility, invariance และ independent check; แยก local rank จาก global identifiability และพิสูจน์ lower bound + sufficiency ก่อนใช้คำว่า minimum measurements
8. Predictive route ต้องมี matched protocol/operator และพารามิเตอร์ครบจาก non-target sources ก่อนเปรียบเทียบ; รายงานได้ทั้งผลตรงและผลขัดกับข้อมูล ไม่ rematch หลังเห็น residual
9. ทุก wave บันทึกสิ่งที่ปิดจริง ข้อที่ยังเปิด artifact/hash และ next action ด้วย 11 fields ใน contract ทำ scoped commits เมื่อหน่วยงานนิ่ง ห้าม stage dirty Core/ledger ของคนอื่นทั้งไฟล์
10. ล็อก scientific decision D10 แล้วทำ report, figures, reproducibility bundle, claim map, executive brief, pitch, budget rationale และ call-fit checklist ให้ครบ D14

## Constraints

The latest `Result/artifacts/T13_POLAR_DYNAMIC_COMPOSITE_2026-10-01.md`
derives conditional pair/scattering spectra, the retarded time kernel and
Gaussian current-contact matching. Do not replace this continuum with a fitted
single relaxation time, call absorption collision damping, or promote Gaussian
FDT to microscopic SK/KMS. Next close renormalized background and full-action
dynamic matching/remainder; the all-momentum linear phase extension is not
material-admitted and does not repair the original conserved-C leakage gate.

The subsequent `Result/artifacts/T13_POLAR_STATIC_IR_OBSERVABLE_2026-10-01.md`
closes same-field/source/measure identities and conditional leading static IR
matching. Its source-complete offshell Gaussian recovers the original tadpole;
do not call a zero polar angle mass a stationary state or a completed
microscopic resummation. Continue interacting/background and dynamic observable
matching before physical predictive admission.

Earlier full-action response evidence: `Result/artifacts/T13_FINITE_MOMENTUM_THERMAL_1PI_2026-10-01.md`
and its JSON compute the finite-q thermal one-loop matrix and static-current
limit. Do not repeat kernel generation without a new question. Next derive
the amplitude-direction IR/current matching and real-axis limit; the computed
upper-half-plane inverse is not a resummed state or a physical prediction.

- C เป็น collective coordinate, Phi เป็น effective response, R_gen เป็น derived trace และ R_obs แยกจาก physical dynamics; อ้าง ontology/F0–F8 ก่อนเพิ่มสมการที่ใช้ตีความทางฟิสิกส์
- He-4 recorded Core-ready กับ graphite aggregate เป็นคนละขอบเขต ใช้ evidence ที่ตรวจจริงโดยไม่เลื่อนทั้ง Core หรือแก้ status เดิมจากการทำ planning milestone สำเร็จ
- Xie 2026 อยู่ review-required หลัง context exposure; ไม่เปิด ไม่ใช้ fit/tuning/comparison และไม่อ้าง blind eligibility ใหม่ ไม่มีการส่งข้อความหาผู้เขียนหรือหน่วยงานทุนจาก prompt นี้
- He-4 second-sound candidate เคยเห็นแล้ว ใช้เป็น nonblind comparison เมื่อ source contract ผ่าน; ไม่แปลง calibration constants หรือ source-level uncertainty เป็นข้อมูลทดลองใหม่
- Named causal branch ต้องรักษา leakage threshold 1e-6 และ ledger/convergence/no-clipping/no-padding ที่ล็อกไว้
- คง source missing, uncertainty missing และ operator missing ตามจริง ข้อมูล synthetic ต้องติดป้ายและใช้เฉพาะบทบาทที่อนุญาต
- หากสองรอบไม่เกิดหลักฐานใหม่ ให้ตัดสินแผนวิจัยด้วยเหตุผลก่อนรันต่อ ไม่เพิ่มหัวข้อเพราะหัวข้อเดิมยาก
- การเผยแพร่ ส่งทุน การติดต่อภายนอก และซื้อทรัพยากรต้องมี authorization ของ action นั้น เตรียมชิ้นงานให้ review ได้ก่อน ขอข้อมูลชื่อทุน/PI เมื่อจำเป็นโดยทำวิจัยที่ไม่ขึ้นต่อคำตอบต่อไปได้

## Completion

Goal complete ได้เมื่อ G0–G5 ผ่านตามความหมายจริง และ SCIENTIFIC_DECISION เป็น `PREDICTIVE_CONTENT_ESTABLISHED` หรือ `SCOPED_NONIDENTIFIABILITY_ESTABLISHED` พร้อม evidence manifest และ reviewable portfolio

ถ้าได้ `UNRESOLVED` ให้ส่ง dossier พร้อม exact blocker และ remaining goal; ห้าม mark complete เพียงเพราะครบวัน มีเอกสารครบ หรือใกล้หมด budget ทำตามข้อกำหนดของ Goal mode เรื่องสถานะ blocked/paused/complete ที่ระบบกำหนด

คำว่า portfolio-ready หมายถึงแพ็กงานวิจัยพร้อมทบทวน การยื่นทุนจริงยังต้องเลือก call ตรวจคุณสมบัติ สังกัด ผู้ร่วม งบ และเอกสารตามประกาศ เป้าหมายนี้ไม่รับประกันทุนหรือ peer review acceptance

เมื่อพลาดรอบแรกให้เก็บ portfolio v1 และ scientific decision แล้วใช้ roadmap W3–W12 เลือก Goal ถัดไปตามหลักฐาน เตรียมจุดส่งมอบ W8 (22 พ.ย.) และ W12 (20 ธ.ค.) เป็นปฏิทินภายใน; ตรวจวันเปิดทุนจริงก่อนกำหนดวันยื่น การขยายแผนระยะยาวไม่เปลี่ยน completion rule ของ Goal แรก และไม่อนุญาตให้ mark complete ถ้างานวิจัยยัง unresolved
