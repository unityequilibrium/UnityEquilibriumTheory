# Topic 13: ผลหลักสำหรับพอร์ตและแผนต่อยอด

วันที่ทบทวน: 3 ตุลาคม 2026 | ฉบับสรุปเพื่อเลือกงาน ไม่ใช่ controller ใหม่

Science handoff ล่าสุด: [thermal source target](Result/artifacts/T13_THERMAL_SOURCE_CURVATURE_2026-10-03.md) ได้ same-action pressure Hessian และพบ cut-only matching gap3.65%/66.4% ในสอง witnesses. งานถัดไปคือ actual dynamic source/contact/virtual completion ไม่ fit residual. Canonical `thermal_source_curvature_evidence_2026_10_03`; วัน/เกณฑ์/full Goal ยังเดิม. Handoffs และ pending statements ด้านล่างเป็นประวัติรอบก่อน ไม่ใช้เป็น current pointer.

Science handoff หลังรอบวางแผน: [Landau/source result](Result/artifacts/T13_ACOUSTIC_SOURCE_LANDAU_2026-10-03.md) รับ acoustic absorption/support window เข้า canonical evidence แล้วโดย science wave แยก. Current controller คือ `local_real_source_contact_and_complete_thermal_sunset_matching_open`; ไม่ใช่ full real/thermal/physical acceptance. Snapshot และข้อความ pending ด้านล่างคงสภาพของรอบ planning เดิม ไม่เขียนประวัติย้อนหลัง; วัน/เกณฑ์/โมเดลไม่เปลี่ยน.

อ่านรายละเอียดจาก [แผน 14 วัน](RESEARCH_PLAN_14D_FUNDING_2026-09-27.md),
[แผนระยะยาว](RESEARCH_ROADMAP_MODELS_12W_2026-09-27.md) และ
[canonical contract](Data/03_Research/funding_portfolio_14d_plan.json).
เอกสารนี้ไม่รับผล G0-G5/R1-R5 เพิ่ม ไม่เริ่มนับสองสัปดาห์ใหม่ และไม่ปิด Goal
ด้วยเอกสารหรือการครบกำหนด ผู้ใช้ยังไม่เลือกทุน สถาบัน/PI งบและ deadline จริงยังไม่ทราบ

## 1. จะปิดอะไรเป็นผลงานหลัก

เป้าหมายเดิมคือ `T13_HE4_PREDICTIVE_CONTENT_AND_MEASUREMENT_DESIGN`:
**เมื่อ equilibrium/calibration ถูกล็อก สมการกำหนด dynamic thermal response
ได้แค่ไหน และต้องเพิ่มข้อมูลอิสระอะไรจึงแยกคำตอบและทดสอบได้?**

ผลส่งมอบหนึ่งชิ้นต้องมีสามส่วนที่เชื่อมกัน ไม่ใช่สามรายการ PASS:

1. ผลสมการ: predictive content หรือ scoped structural proof ตาม G2/G3 เดิม
   พร้อม assumptions, units, invariant observable และวิธีตรวจอิสระ
2. ผลการออกแบบการวัด: source-to-state-to-detector map, unknown/nuisance inputs
   และเหตุผลว่าการวัดใหม่เพิ่ม information/rank อย่างไร ตาม G4
3. แพ็กวิจัย: derivation, evidence/hash map, reproducibility, related-work gap,
   uncertainty/claim map, report และ pitch ตาม G5

หากส่วนใดไม่ครบ ให้คง `UNRESOLVED` หรือ preliminary evidence ตามจริง
พอร์ตพร้อมทบทวนไม่เท่ากับผลวิทยาศาสตร์ปิดหรือพร้อมยื่นตามเกณฑ์ทุน
Full Topic 13 ยังต้อง EOS/normal/transport/KMS/entropy และ physical mapping
อีกหลายส่วน; ไม่เป็นเงื่อนไขสร้างพอร์ต preliminary และไม่อ้างว่าปิดจากผลนี้

## 2. สถานะที่ใช้ตัดสิน ณ รอบนี้

หลักฐานรับเข้า canonical ล่าสุดคือ [action-source/pair interface](Result/artifacts/T13_ACOUSTIC_SOURCE_PAIR_2026-10-03.md)
และ [artifact](Result/artifacts/t13_acoustic_source_pair.json):
SHA-256 `c151cc3d2b8342f3ab0b6569a68f40a58ce2d604d99a419e934556e605b4f025`.
ปิดเฉพาะ tree h-source/static/pole และ off-shell acoustic pair spectral kernel
ใน lane ที่ประกาศ ไม่ใช่ full retarded response หรือ detector calibration

ตัวควบคุมที่รับเข้าแล้ว:
`off_shell_Landau_local_real_source_contact_and_complete_thermal_sunset_open`.
งาน Landau ใหม่ที่ยังไม่ส่งมอบเป็น exploration ไม่รับเป็นหลักฐานด้วยแผนนี้
current pointer ใน contract เป็นผู้ควบคุมเมื่อมี science wave ใหม่; ข้อความนี้
เป็น snapshot วันที่ 3 ต.ค. ไม่เขียนสถานะย้อนหลังเมื่อ wave ถัดไปผ่าน

แยกปัญหาสองสายเพื่อไม่วน: **สมการ/source/real matching** ต้องคำนวณหรือพิสูจน์;
**material/readout/thermal scale** ต้องมีข้อมูลอิสระหรือออกแบบการวัดจริง
งาน chaos, fluid benchmark หรือการเพิ่มเวลารันไม่สร้าง alpha หรือข้อมูลทดลองแทน
Core-owner O(2)/He-4 composition เป็นผลอีกขอบเขต ไม่ใช้รับ branch นี้อัตโนมัติ

## 3. แผนก่อนพอร์ต 11 ตุลาคม

| ช่วง | งานตัดสินและเจ้าของ | เงื่อนไขส่งมอบ/ทางออก |
| --- | --- | --- |
| 3-4 ต.ค. | Derivation lead + verifier: ส่งมอบ Landau/source wave แยก แล้วตรวจส่วน real/contact/local ที่ยังไม่ถูกกำหนด | สมการ หน่วย assumptions และ independent checks; เก็บ fail baseline ไม่ใช้ cut แทน full response |
| ไม่เกิน 5 ต.ค. | Lead: เลือก predictive / structural / unresolved | Predictive ต้องมี matched operator และ non-target inputs; structural ต้องมี proof ที่ admissible และไม่เป็นเพียง coordinate redundancy; ขาดทั้งคู่คง unresolved |
| 3-6 ต.ค. คู่ขนาน | Measurement/source owner: เลือกหนึ่ง protocol และ information-gap card | ระบุ material/state, source/readout, sensitivity, nuisance, uncertainty/covariance และ permission; ถ้ายังไม่มีข้อมูลให้เป็น conditional feasibility ไม่ใช่ validation |
| 6-7 ต.ค. | Verifier + lead: independent check, related-work และ scientific decision | แยก numerical error จาก approximation/material uncertainty; novelty ต้องมีการเทียบ ไม่อ้างจากชื่อ UET; ตรึงเฉพาะผลที่ตรวจแล้ว |
| 8-11 ต.ค. | Writer + reviewer เมื่อมี: report/reproduction/pitch/aims | Review-ready bundle พร้อมรายการทุน/PI/งบที่ยังขาด; ไม่อ้าง submission-ready หรือ external replication ถ้าไม่มีผู้ตรวจอิสระจริง |

**7 ต.ค. scientific freeze / 11 ต.ค. portfolio review** เป็นวันเดิมที่ตั้งไว้
ไม่ใช่วันปิดรับทุน หากการคำนวณไม่จบให้ส่ง preliminary result กับ exact open
obligation และทำวิจัยต่อหลัง freeze; ไม่ย้ายเกณฑ์จบให้เพียงเอกสารครบ

งานก่อน freeze จึงมี decisive calculation ครั้งละหนึ่งเรื่อง และ source inventory
คู่ขนานเท่านั้น เกินสอง wave ที่ไม่มีข้อมูล/คำตอบใหม่ต้องทบทวน route อย่างชัดเจน
ไม่ rerun สมการเดิมเพียงเพื่อเพิ่ม log และไม่เปิด Gravity/Galaxy/chaos campaign
รายการไฟล์ส่งมอบและ G0-G5 ยังอ้าง contract เดิม ไม่เริ่มตาราง D01 ใหม่

## 4. ถ้ารออีก 2-3 เดือน เวลาต้องซื้ออะไร

| วันทบทวนเดิม | ผลหลักที่ต้องเพิ่ม | ประโยชน์ระยะยาว/หากยังไม่ได้ |
| --- | --- | --- |
| 25 ต.ค. / R1 | Source-complete response และ validity/approximation boundary จาก prescription เดียว | Core ได้ interface ที่ตรวจย้อนกลับได้; หากยังไม่ครบระบุ matching/consistency obligation ไม่ใช้ convergence แทน proof |
| 8 พ.ย. / R2-R3 | หนึ่ง material/state/source/detector/temperature map และ independent input/uncertainty | เปิดทางทดสอบเชิงปริมาณ; หากข้อมูลไม่ได้ให้ protocol feasibility ที่บอกว่าทุนต้องซื้อการวัดอะไร ไม่สร้าง source แทน |
| 22 พ.ย. / R4 | Preregistered comparison เมื่อ R1-R3 พร้อม หรือ verified scoped structural result + measurement design | ได้คำตอบตรง/ขัดข้อมูลโดยไม่ rematch; หาก proof ยังเปิดคง unresolved ไม่เรียก source absence ว่า no-go |
| 6 ธ.ค. | Independent reproduction/robustness; protocol ที่สองเฉพาะผลแรกพร้อม | แยกผลทนทานจาก artifact ของวิธี/parameter; แก้ผลแรกก่อนขยาย |
| 20 ธ.ค. / R5 | Research release, review trail และ proposal ที่ตรง call เมื่อทราบจริง | ส่งต่อ Core/transport ภายใต้ admission ของตัวเอง; ไม่มี automatic Gravity/Galaxy/global unlock |

รอบถัดไป **11 ธ.ค. 2026 หรือ 11 ม.ค. 2027 เป็น scenario ไม่ใช่ประกาศทุน**
หากพบทุนจริงให้ปรับ deadline เอกสารและผู้สมัครตามประกาศ ไม่เปลี่ยน thresholds
ถ้าพลาดรอบแรก เก็บ portfolio v1 และแยกเหตุ: eligibility/deadline, evidence,
novelty หรือ partner/resources แล้วทำเฉพาะงานแก้เหตุนั้น ไม่เริ่มทฤษฎีใหม่ทั้งชุด
ไม่มีหลักฐานให้รับประกันว่า Full Topic 13 จะปิดภายในสามเดือน

## 5. โมเดลและการใช้ทรัพยากร

| งาน | คำแนะนำสำหรับการทดลอง | ขอบเขต |
| --- | --- | --- |
| Derivation, identifiability, route decision | GPT-6 Astra / high | xhigh เฉพาะ proof obligation ที่มี input/output ชัด; ไม่ใช้ผลโมเดลแทนหลักฐาน |
| Implementation, independent numerical method, regression | GPT-6.1 Sol / high | ต้องตรวจ formula และ failure controls ไม่ทำเพียง packaging |
| Inventory/provenance checklist/link review | Luna ตามรุ่นที่ใช้ได้ | งานขอบเขตชัดเท่านั้น; ไม่เป็นผู้รับรอง physics/claim |
| ถ้าใช้ตัวเดียวหรือโควตาจำกัด | GPT-6.1 Sol / high | ส่งคำถามพิสูจน์ยากให้ Astra เมื่อทำได้ ไม่ลด acceptance |

การแบ่งบทบาทเป็นข้อเสนอจาก workload ไม่ใช่ benchmark UET ที่พิสูจน์แล้ว
[OpenAI model-selection guidance](https://developers.openai.com/api/docs/guides/model-selection)
แนะนำเปรียบเทียบโมเดลด้วย input เดียวและเลือกความสามารถ/effort ที่ผ่านเกณฑ์จริง
[Model catalog](https://developers.openai.com/api/docs/models) อธิบาย Astra สำหรับ
งาน reasoning ยากและ Sol 6.1 สำหรับสมดุลความสามารถกับต้นทุน การเข้าถึง/โควตา
ขึ้นกับบัญชี; แผนนี้ไม่คาดเดาราคา ค่าใช้จ่าย หรือเปลี่ยนการตั้งค่า

ทดลองเดิม: จำกัด **90 นาทีต่อ configuration** ใช้โจทย์และ frozen inputs เดียว
ประเมิน derivation/unit errors, unauthorized source/holdout access, independent
controls และเวลารวมแก้ข้อผิดพลาด; critical errors ต้องเป็นศูนย์
ไม่ใช้จำนวน token, ความยาวคำตอบ หรือสองโมเดลเห็นตรงกันเป็น scientific acceptance
สถานะ trial **NOT_RUN**; model configuration unchanged. คำนวณงบจากการใช้งาน
ที่วัดจริงก่อนจอง queue ใหญ่ ไม่ authorize ซื้อบริการ ติดต่อแล็บ หรือยื่นทุน

## 6. วิธีใช้กับ Goal

มี Goal วิจัยเดิม active อยู่ ไม่สร้างซ้ำหรือเปลี่ยน completion rule ด้วย brief นี้
แต่ละ wave ต้องเริ่มจาก current canonical evidence และเลือกคำถามเดียวที่เปลี่ยน
ข้อสรุปได้ ส่งสมการ/ข้อมูล/independent verification + artifact/hash ก่อนรับผล
รายงานผลจริงด้วย 11 fields เดิม: อะไรปิด เหลืออะไร และ dependency ใดยังไม่เปิด
งานเผยแพร่แยกจาก science: push ยังรอ authorization หลัง auto-review ปฏิเสธ
ไม่ retry/work around ไม่อ้าง CI ของ head ใหม่ผ่านจาก CI ของ commit เก่า

MAJOR_RESULT_CLOSURE: PLANNING_ONLY; no scientific result accepted.

WHAT_IS_ACTUALLY_CLOSED: Reading route and bounded delivery decisions are explicit; not the research question itself.

WHAT_REMAINS_OPEN: Full response/matching, independent physical input and measurement design, novelty/review, funder/PI/budget and all existing acceptance gates.

DEPENDENCY_UNLOCKED: None; owner Core and existing physical gates unchanged.

STATUS: PLAN_CLARIFIED_NOT_SCIENTIFIC_ACCEPTANCE.

WHAT_CHANGED: Compact two-horizon execution brief linked to existing canonical plan; model recommendations rechecked against official documentation.

EQUATION_OR_MAPPING: Planned same-action source response and independent readout/thermal mapping; no equation, alpha or transport coefficient added.

VERIFICATION: Accepted pair artifact is hash-identified; planning regression is recorded in UPDATE_LOG. No scientific rerun, model trial or funding-call eligibility verification by this brief.

CONTROLLING_BLOCKER: off_shell_Landau_local_real_source_contact_and_complete_thermal_sunset_open at the accepted snapshot; material/readout/scale input remains separately open.

NEXT_ACTION: Deliver the pending Landau science wave separately, then one real/contact matching decision and linked measurement information card before the existing freeze.

CLAIM_BOUNDARY: Planning and preliminary evidence only; not Full Topic13, Goal, physical prediction, external validation, funding eligibility or a guaranteed funding round. Holdout remains locked with prior-exposure REVIEW_REQUIRED; original conserved-C failure and ontology unchanged.
