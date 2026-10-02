# แผนตัดสินใจวิจัย: พอร์ตสองสัปดาห์และการต่อยอดอีก 2–3 เดือน

วันที่ทบทวน: 2 ตุลาคม 2026 (Asia/Bangkok)

Science successor: [Low-T phase EFT](Result/artifacts/T13_LOW_T_PHASE_EFT_2026-10-02.md) และ [conditional measurement card](Result/artifacts/T13_LOW_T_PHASE_EFT_MEASUREMENT_CARD_2026-10-02.md) ทำแพ็ก A บางส่วนได้จริงแล้วใน branch ใหม่: tree/phase thermal difference และ source/entropy สอดคล้องกัน แต่ vacuum/interaction control และ physical readout ยังเปิด companion JSON ด้านล่างเป็น historical planning snapshot ไม่ใช่ current scientific artifact; current evidence อยู่ใน canonical funding contract วันและเกณฑ์รับผลเดิมไม่เปลี่ยน.

เอกสารนี้เป็นฉบับอ่านเพื่อเลือกงาน ไม่ใช่การเพิ่มเกณฑ์ปิดทฤษฎีหรือเริ่มนับเวลาใหม่ อ่านคู่กับ [แผน 14 วัน](RESEARCH_PLAN_14D_FUNDING_2026-09-27.md), [แผน 12 สัปดาห์](RESEARCH_ROADMAP_MODELS_12W_2026-09-27.md) และ [contract เดิม](Data/03_Research/funding_portfolio_14d_plan.json) ซึ่งยังควบคุม G0–G5 และการรับผลหลัก เอกสารตัดสินใจที่เครื่องอ่านได้อยู่ที่ [funding_decision_roadmap_2026_10_02.json](Data/03_Research/funding_decision_roadmap_2026_10_02.json)

## ข้อสรุปสำหรับเลือกโมเดลและวางแผนสองรอบ

ผู้ใช้ยืนยันว่ายังไม่เลือกทุนหรือหน่วยงาน จึงตั้งเป้า **พอร์ตพร้อมทบทวน 11 ต.ค.** ไม่ใช่พร้อมยื่นตามข้อกำหนดทุนที่ยังไม่ทราบ เราไม่ทราบว่าจะพลาดรอบแรกหรือไม่ และไม่ยืนยันว่ารอบถัดไปเปิดในอีกสองหรือสามเดือน

**เลือกโมเดล:** ถ้าใช้ตัวเดียวและโควตาไม่ใช่ข้อจำกัด เลือก **GPT-6 Astra / high** สำหรับ Goal วิจัยนี้ ถ้าต้องคุมโควตาให้ใช้ **GPT-6.1 Sol / high** เป็นตัวทำงานหลัก แล้วใช้ Astra ตรวจเฉพาะจุดอนุมานสำคัญ ไม่จำเป็นต้องเปิดสามโมเดลพร้อมกัน Astra / xhigh ใช้เฉพาะโจทย์พิสูจน์ที่มี inputs และเงื่อนไขจบชัด ส่วน Luna / medium เหมาะกับรายการแหล่งข้อมูล/ลิงก์ที่มี checklist ไม่รับรองฟิสิกส์แทน lead คำแนะนำเป็นการจัดบทบาทตาม [OpenAI Docs](https://developers.openai.com/api/docs/guides/model-selection) ไม่ใช่ผลทดลองว่าโมเดลใดปิด UET ได้เร็วกว่า

**สถานะต้องแยก lane:** Core-owner checkout ที่อ่านวันที่ 2 ต.ค. บันทึก O(2)/He-4 composition เป็น `CLOSED_FOR_CORE` ใน `docs/core/07_artifacts/topic13/t13_topic13_closure_matrix.json` แต่ไม่ครอบคลุม graphite TTG และ predictive-response branch ใหม่ การอ่านบันทึกนี้ไม่ใช่ rerun หรือการรับรอง Core ใหม่ โดย incident `docs/core/08_history/update_logs/T13_HOLDOUT_EXPOSURE_REVIEW_REQUIRED_2026-09-24.md` ยังบังคับ `REVIEW_REQUIRED`; ห้ามใช้ PASS เก่าอ้างว่าไม่เคยเห็น Xie ทั้งสองรายการเป็น read-only snapshot จาก checkout เจ้าของ Core มี hash ใน addendum ไม่ใช่ไฟล์ที่รับเข้า release ของแผนนี้ โดยเฉพาะ incident ยังไม่อยู่ใน execution checkout งานวางแผนไม่แก้ gate ของเจ้าของ Core และไม่ใช้ผลใหม่ล้าง FAIL ของ conserved-C เดิม

### ผลที่จะปิดก่อนสำหรับพอร์ต

เลือกแพ็กผลหลักหนึ่งเรื่อง: **แบบจำลอง low-T บอก response อะไรได้ และต้องวัดอะไรอิสระเพิ่มจึงทดสอบได้** ประกอบด้วยสามชิ้นที่ต้องเชื่อมกัน ไม่ใช่สามจำนวน PASS:

1. **ผลทางสมการที่มีขอบเขต:** มีแล้วคือ tree-matched thermal differences และ derived leading zero-T decay ใน candidate lane; ต้องระบุส่วนที่ยังต้อง matching และตรวจอีกวิธี ไม่เรียก full quantum EOS
2. **ผลเรื่องข้อมูลที่จำเป็น:** [measurement card](Result/artifacts/T13_LOW_T_PHASE_EFT_MEASUREMENT_CARD_2026-10-02.md) แสดงว่า static/leading thermal input ยังไม่กำหนด invariant kinetic response แต่ dispersion เพิ่มข้อมูลได้ในชั้นแบบจำลองจำกัด งานต่อคือ nuisance inputs, uncertainty และ readout ไม่ใช่สรุปว่าทดลองได้จริงแล้ว
3. **แพ็กที่คนอื่นตรวจได้:** derivation, artifact/hash, failed baseline, reproduction และ related-work map ต้องแยกวิธีมาตรฐานที่นำเข้ากับสิ่งที่คำนวณเพิ่มสำหรับ candidate นี้ การประยุกต์ Beliaev/EFT ไม่ใช่หลักฐานว่าค้นพบกลไกใหม่

แพ็กนี้รับได้ตาม evidence/measurement/claim acceptance เดิมเท่านั้น หากยังไม่ครบให้ส่ง preliminary portfolio พร้อมข้อค้าง ไม่ mark scientific Goal สำเร็จเพราะเอกสารครบ ส่วนไฟล์ vacuum-cut exploration ที่ยังไม่ commit และไม่ครบ focused review ยังไม่ถูกนับเป็นผลสำเร็จรอบนี้

| ส่งมอบภายใน | ผลที่ต้องได้ ไม่ใช่จำนวนรัน | หากยังปิดไม่ได้ |
| --- | --- | --- |
| 3 ต.ค. | ล็อก action/branch/coefficient origins และเลือกหนึ่งคำถามคำนวณที่เปลี่ยนข้อสรุป | บอก missing input หรือสมมติฐาน ไม่กระจายไปหัวข้อใหม่ |
| 5 ต.ค. | ตรวจ cut/real response และ local matching obligation อีกวิธี; ระบุส่วนของ thermal remainder ที่ยังไม่คำนวณ | ใช้ผล interactions ที่ตรวจแล้ว ไม่กำหนด width หรือค่าชดเชยให้ผ่านเอง |
| 7 ต.ค. | scientific freeze: bounded result + measurement card + novelty/claim/evidence map | ตรึงผลเบื้องต้นและ exact unresolved obligation ไม่เปลี่ยน uncertainty เป็นศูนย์ |
| 8–11 ต.ค. | report, figures, short pitch, reproduction bundle, three aims, resource/risk และ call-fit checklist | พร้อมให้คนอ่านได้ตามจริง แต่ eligibility/PI/งบยังไม่ทราบ |

### เวลาเพิ่มอีกสองหรือสามเดือนต้องช่วยอะไร

| รอบทบทวน | ต้องได้ความรู้เพิ่มอะไร | ช่วยระยะยาวอย่างไร |
| --- | --- | --- |
| 25 ต.ค. / R1 | ตัดสิน source/response prescription และ validity domain รวม vacuum/Wilson กับ interaction obligations | รู้ว่าสมการส่วนใดส่งเป็น response interface ได้ และส่วนใดห้ามใช้เป็น prediction |
| 8 พ.ย. / R2–R3 | เลือกหนึ่ง material/state/protocol; มี input/normalization/readout อิสระ หรือ feasibility ที่ระบุการวัดจริงที่ยังต้องหา | เปลี่ยนคำว่า “ขาดข้อมูล” เป็นคำขอข้อมูล/การวัดที่หาทุนรองรับได้ |
| 22 พ.ย. / R4 | เปรียบเทียบหนึ่ง observable เมื่อ prerequisites ผ่าน หรือปิดผล structural ที่พิสูจน์และตรวจอิสระได้ | ได้คำตัดสินที่อาจสนับสนุนหรือขัดกับ candidate ไม่ใช่แค่กราฟ fit |
| 6 ธ.ค. / extension | ตรวจ state/protocol ที่สองเมื่อผลแรกพร้อม หรือแก้ uncertainty ของผลแรก | แยกผลเฉพาะจุดจากผลที่ทนต่อการเปลี่ยนเงื่อนไข |
| 20 ธ.ค. / R5 | clean reproduction, reviewer disposition และพอร์ตฉบับปรับตามทุนที่เลือกเมื่อทราบ | ทำให้ทุนสนับสนุนงานถัดไปจากหลักฐานที่ตรวจได้ ไม่ใช่ความมั่นใจของ AI |

แต่ละวันเป็น **วันตัดสินผล ไม่ใช่วันรับประกันผ่าน** R1–R5 ยังไม่ถูก accept จากการปรับแผน หาก 8 พ.ย. ยังไม่มี numeric input ให้เลือก theory/methods + measurement-design route และเปิด empirical gate ไว้ ไม่รอ source เดิมแบบไม่จำกัดเวลา ไม่สร้างข้อมูลแทน และไม่เรียกการหาไม่พบว่า no-go

ถ้าต้องรอทุนอีกสองเดือนนับจาก 11 ต.ค. ให้ใช้ **11 ธ.ค. เป็น scenario** และ freeze ผล 27 พ.ย.; อีกสามเดือนใช้ **11 ม.ค. 2027 เป็น scenario** และ freeze 28 ธ.ค. เผื่อเอกสารสถาบันอย่างน้อย 7 วันและ attachments 3 วันก่อน deadline จริง ปรับเพิ่มตามข้อกำหนดหน่วยงาน ไม่รอ release 20 ธ.ค. ถ้าทุนปิดก่อน เก็บ v1 แล้ววิเคราะห์เหตุที่ไม่ยื่น: deadline, eligibility, evidence, novelty หรือ partner/resources ก่อนเลือกงานต่อ

### คุมเวลาและตรวจว่าโมเดลไหนคุ้มจริง

ก่อน freeze ใช้สัดส่วนตั้งต้น 60% derivation, 20% independent verification, 20% source/portfolio; หลัง freeze ใช้ 80% packaging/call-fit และ 20% reproduction/claim check เป็นการจัดเวลา ไม่ใช่ usage ที่วัดแล้ว จำกัด decisive calculation หนึ่งเรื่อง พร้อม source inventory คู่ขนานได้ หากสอง wave ไม่มีหลักฐานใหม่ให้ตัดสิน route ก่อนรันต่อ แยก numerical convergence จาก physical approximation error เสมอ

ทดลอง Astra กับ Sol ด้วย frozen input เดียวกันและ acceptance เดียวกัน จำกัด **90 นาทีต่อ configuration** ตรวจ derivation/units, independent control และ claim/source leakage ต้องไม่มี critical error วัดเวลารวมแก้ข้อผิดพลาดและ usage/cost เมื่อมีข้อมูล เลือกค่าที่เบาสุดที่ผ่านจริง Trial ยัง `NOT_RUN` จึงไม่มีการรับรองเวลาหรือค่าใช้จ่าย และการเห็นตรงกันของสองโมเดลไม่ใช่ external replication

**ปลายทางระยะยาว:** ส่ง response ที่รู้ units/domain/uncertainty และ independent-input contract กลับ Core เพื่อรองรับ thermal/constitutive research ตาม dependency จริง ไม่ปลด Gravity/Galaxy อัตโนมัติ งาน finite-T normal component, heat/Kubo, SK/KMS และ entropy transport ยังต้องปิดเฉพาะ scope ของมันเอง ไม่รับประกัน Full Topic13 ในสามเดือน

## Current Interaction Result (2026-10-02)

[The interaction successor](Result/artifacts/T13_LOW_T_INTERACTIONS_2026-10-02.md)
derives the first leading T=0 attenuation kernel from the same tree pressure,
with actual phase-space/energy/Bose checks. The tree T8 pressure extension
and one subtracted quartic term do not establish total approximation error.
Current controller: renormalized cubic-sunset/vacuum Wilson matching, plus
independent physical inputs and finite-T normal/heat transport. Earlier
Hartree/controller snapshots below retain historical scope, not current
scientific status. Dates/models/Goal acceptance are unchanged.

## 1. ข้อเสนอที่เลือก

**รอบแรกให้ส่งผล methods/structural ที่มีหลักฐาน พร้อมการออกแบบการวัดหนึ่งชุด ไม่สัญญาปิด Full Topic 13 ในสองสัปดาห์** เป้าหมายพอร์ตยังเป็น 11 ตุลาคม; freeze วิทยาศาสตร์ 7 ตุลาคม ไม่ใช่สองสัปดาห์ใหม่จากวันนี้ หากทำผลหลักไม่ครบ ให้ส่ง preliminary portfolio ตามจริง ไม่เรียก Goal สำเร็จ

ชื่อโครงการทำงานที่เสนอ: **ความสอดคล้องและข้อมูลที่จำเป็นสำหรับสะพาน thermodynamic response ของ UET** ชื่อและ novelty ต้องให้ผู้วิจัยทบทวน ไม่ใช่ข้ออ้างว่าค้นพบฟิสิกส์ใหม่แล้ว

คำถามปลายทาง: ภายใต้ action และ approximation ที่ประกาศ การตอบสนองกับ thermodynamics สอดคล้องกันเพียงใด และการวัดอิสระใดจำเป็นต่อการระบุ response ในหน่วยจริง?

ข้อเสนอขณะนี้คือเส้น methods/measurement design เพราะ material map, input อิสระและ physical transport ยังไม่รับเข้า เปลี่ยนเป็น prediction route ได้ต่อเมื่อ prerequisites เดิมผ่านจริงเท่านั้น ไม่ใช้วันครบกำหนดหรือความมั่นใจของโมเดลแทนหลักฐาน

## 2. สิ่งที่มีแล้วและสิ่งที่ยังขาด

หลักฐานปัจจุบันคือ [interaction result](Result/artifacts/T13_LOW_T_INTERACTIONS_2026-10-02.md) และ artifact `t13_low_T_interactions.json` SHA-256 `f1679543e0a644c5104d001ea7ed84adbaf1298f8d8315c9c5108cdcfb53fd0c` ที่ published Topic13 head `17a0e603a702c43a2abcd9489d21864e600192a0` ส่วน [Hartree low-T boundary](Result/artifacts/T13_HARTREE_LOW_T_VALIDITY_2026-10-02.md) เป็นหลักฐาน predecessor ใน branch ของมัน ไม่ใช่ current EFT controller companion JSON ของ decision roadmap คงเป็น historical snapshot; canonical funding contract และ addendum เป็นตัวชี้สถานะล่าสุด

| สิ่งที่มีหลักฐานแล้ว | สิ่งที่ผลนั้นยังไม่ให้ |
| --- | --- |
| Joint stationary และ retarded response ใน named classical-Phi/Hartree lane พร้อม independent checks | ไม่ใช่สมดุลหรือ response ของ He-II ที่รับเข้าแล้ว; ไม่รับรองทุกความถี่หรือทุก state |
| Conditional low-T boundary: entropy envelope ถูกต้อง แต่ internal gap ทำให้ asymptotic entropy ต่างจาก external gapless-mode interpretation | ไม่ใช่ global UET no-go; ไม่ได้สร้าง EOS ใหม่; ไม่รับรอง Hartree physical validity window |
| Source/calibration limitations และ provenance chain ที่บันทึกไว้ | ไม่ได้ให้ independent `alpha_Phi_K`, permissioned TTG rows หรือ physical Kubo coefficient |
| Core มีผลย่อยใน curved 3+1 แต่ parent ยัง PARTIAL ใน checkout ของเจ้าของ Core ที่อ่าน | ไม่ปลดล็อก Gravity และไม่เป็นงานที่ Topic13 ต้องแก้แทนเพื่อทำพอร์ต |

**ตัวตัดสินงานต่อใน EFT:** `renormalized_cubic_sunset_and_vacuum_Wilson_matching_open` ส่วน `gapless_equilibrium_thermal_prescription_not_derived` ยังคุม Hartree predecessor ไม่ได้ถูกซ่อมด้วย branch ใหม่ ความสอดคล้องเชิงสมการ, physical input และการยื่นทุนเป็นคนละปัญหา ต้องส่งมอบแยกกัน

## 3. งานก่อน freeze: หนึ่งโจทย์หลักและหนึ่งสายข้อมูล

| แพ็ก / เจ้าของ | งานที่ต้องทำจริง | เกณฑ์รับผล / ทางออก |
| --- | --- | --- |
| A / Topic13 derivation lead | ทดลอง same-action low-T phase EFT แบบ loop-ordered เป็น named branch ใหม่: stationary elimination ของ amplitude และ classical Phi, source/current และ thermal determinant จาก prescription เดียว | ต้องแสดง units, stable domain, static/Ward limits, entropy/current derivatives, independent mode/integral checks และ approximation obligations; ถ้า error control ยังขาด ให้คง conditional ไม่เรียก controlled physical EOS |
| B / Source/measurement owner, คู่ขนาน A | เลือก material/protocol เดียวตามคำถาม; ทำ source identity, permission, units, state/frequency/readout, uncertainty และ ancestry/covariance card | ตัวเลขจริงที่รับเข้าได้ หรือ feasibility card ที่ระบุว่าต้องวัดอะไรและแก้ degeneracy ใด; การหา source ไม่พบไม่ใช่ no-go |
| C / Numerical verifier | ตรวจ A ด้วยวิธีที่ไม่ใช้สูตรคำตอบเดียวกัน: derivative เทียบ source response, mode expansion เทียบ full parent, thermal integral เทียบ asymptotics ตามงานที่ derive ได้ | numerical residual/convergence ไม่แทน approximation error; เก็บ failed baseline และ uncertainties ที่ยังไม่ทราบไว้ |
| D / Lead + human reviewer เมื่อมี | รวม bounded result, related-work comparison และ measurement design | ต้องระบุ imported method กับ contribution ของเรา; AI สองตัวเห็นตรงกันไม่เป็น external replication |

แนวทาง A มีฐานวิธีจาก [Son: low-energy action จาก EOS](https://arxiv.org/abs/hep-ph/0204199) และ [Kourkoulou–Nicolis–Parmentier: low-T phonon thermodynamics/currents](https://arxiv.org/abs/2212.12555) แต่ยังต้อง derive และตรวจสำหรับ action ของเราเอง งานอ้างอิงไม่ให้ material calibration หรือ transport ของ UET โดยอัตโนมัติ

ห้ามแก้ internal mass เดิมให้ gapless ห้ามเติม phonon gas ลงใน Hartree potential เดิมแล้วเรียกสมการผ่าน และห้ามใช้ nonlocal filtering แทน causal proof หาก A ไม่ผ่าน ให้รายงาน exact failed obligation; ใช้ restricted Hartree validity หรือ constrained resummation เป็นงานภายหลังได้เมื่อมีสมการและเหตุผลใหม่ ไม่เปิดสาม approximation แข่งกันก่อน freeze

| วันภายในกรอบเดิม | ผลส่งมอบ | การตัดสิน |
| --- | --- | --- |
| 2 ต.ค. | ยืนยัน methods/measurement-design route และรายการ proof obligations | เป็น planning decision ไม่รับ D5 scientific milestone จากการเลือกเส้นทาง |
| 3–4 ต.ค. | Bounded derivation/new-branch feasibility พร้อม independent check หรือ verified failure boundary | ถ้าไม่มีการคำนวณที่เปลี่ยนข้อสรุป ให้เปลี่ยนคำถาม ไม่ rerun unchanged candidate |
| 5–6 ต.ค. | Uncertainty/validity table และ measurement card หนึ่งใบ | ระบุ identifiable parameter combinations, source/readout, state, units และข้อมูลใหม่ที่ต้องการ; อ้าง minimum measurements เฉพาะเมื่อมี necessity + sufficiency proof |
| 7 ต.ค. | Scientific decision และ evidence/claim freeze | predictive / scoped structural / unresolved ตาม G0–G5 เดิม; preliminary methods อย่างเดียวไม่ทำให้ Goal สำเร็จ |
| 8–11 ต.ค. | Report, figures, reproducibility bundle, portfolio index, pitch, aims, resource/call-fit gaps | portfolio review-ready แยกจาก scientific result accepted และ submission-ready |

Measurement card ต้องมี question, parameter combination, material/state, observable/operator, detector/protocol, source role/permission, independence statement, uncertainty/covariance, precision rationale, nuisance parameters, information/rank gain และทรัพยากรที่ต้องขอ หาก operator ยังไม่รับเข้า precision target ต้องติดป้าย conditional ไม่ใส่ตัวเลขความแม่นยำจากการคาดเดา

## 4. ถ้าไม่ทันรอบแรก: เวลาเพิ่มต้องได้ผลอะไร

รักษา portfolio v1 และคำตอบที่ตรวจแล้วไว้ ไม่เริ่มแผนใหม่หรือเปลี่ยนเกณฑ์ย้อนหลัง วันด้านล่างเป็น **วัน review ผล** ไม่ใช่สัญญาว่าจะผ่านทุกข้อ

| Review / ผลหลักเดิม | สิ่งที่เวลาเพิ่มต้องซื้อ | ไปต่อได้เมื่อ / หากยังไม่ได้ |
| --- | --- | --- |
| 25 ต.ค. / R1 | Prescription ที่สอดคล้องสำหรับ stationary/source/thermal response พร้อม numerical และ approximation boundaries | รับเฉพาะขอบเขตที่ตรวจได้; ถ้า control ยังเปิด ให้ตัดสินเลือก approximation หรือ validity question ที่มีปลายทาง ไม่ยก local poles เป็น full response |
| 8 พ.ย. / R2–R3 | Material/state/dimensional observable map และ input อิสระ หรือ feasibility package ที่ส่งให้แล็บตรวจได้ | Empirical admission ต้องมี numeric provenance/protocol/uncertainty จริง; feasibility ไม่แทนข้อมูลและไม่ปลด physical prediction |
| 22 พ.ย. / R4 | ผลเปรียบเทียบที่ล็อกก่อนเห็น target และไม่ retune หรือ scoped structural proof พร้อม measurement design | Comparison ต้องมี R1/R2/R3 numeric-input admission; ผลไม่ตรงข้อมูลก็เป็นคำตอบ ถ้า proof ยังขาดคง unresolved |
| 6 ธ.ค. / R4 extension | ทดสอบอีก state/protocol เพื่อแยก parameter degeneracy หรือจำกัด domain ให้ชัด | ทำหลังผลแรกและ preregistration เท่านั้น; หากรอบทุนมาก่อน ให้พัก extension แล้วเตรียมยื่น |
| 20 ธ.ค. / R5 | Reproducible release, claim/novelty/uncertainty map และ actual review disposition | ผู้เชี่ยวชาญ/ผู้รันอิสระเมื่อหาได้; ถ้าไม่มีให้เปิดเผย ไม่ใช้ model agreement แทน |

**เดือนแรก:** ทำให้สมการที่มีบอก response/thermodynamics ได้ภายใต้สมมติฐานที่ตรวจสอบได้

**เดือนที่สอง:** ทำให้สิ่งนั้นทดสอบได้ด้วย input อิสระหรือคำขอการวัดที่ชัด และได้คำตัดสินจาก comparison/structural result

**เดือนที่สาม:** เพิ่มความน่าเชื่อถือด้วยการตรวจซ้ำ ผู้เชี่ยวชาญ และข้อเสนอที่ตรงทุน ไม่เพิ่มหัวข้อเพื่อให้พอร์ตดูใหญ่

เส้นทางสู่ Full Topic13 หลังจากนั้นยังต้องมี independent scale/source/uncertainty, finite-T EOS และ normal component, physical constitutive/transport coefficient, SK/KMS, entropy current/positivity, dissipative balance และ heat-flux observable mapping รวมถึง causal branch ที่รับเข้าได้ ผล low-T equilibrium EFT ไม่แทน collision/heat/Kubo หรือ causal closure งาน curved 3+1 เป็น Core result แยก ไม่สร้าง dependency cycle ใน Topic13

## 5. แผนรองรับวันทุนจริง

ยังไม่ทราบชื่อทุน deadline สังกัด PI หรือข้อจำกัดงบ จึงยังตอบไม่ได้ว่าเข้า/ไม่เข้ารอบแรกจากความพร้อมวิทยาศาสตร์เพียงอย่างเดียว และไม่คาดเดาว่ารอบถัดไปจะเปิดแน่นอนในอีก 2–3 เดือน

| Scenario ที่นับจากพอร์ต 11 ต.ค. | Freeze ผลที่ใช้ยื่น | เอกสารหน่วยงาน | ตรวจ forms/attachments |
| --- | --- | --- | --- |
| ปิดรับสมมติ 11 ธ.ค. (อีกสองเดือน) | 27 พ.ย. | 4 ธ.ค. | 8 ธ.ค. |
| ปิดรับสมมติ 11 ม.ค. 2027 (อีกสามเดือน) | 28 ธ.ค. | 4 ม.ค. | 8 ม.ค. |

ปรับตามประกาศจริง โดยเผื่อ 14 วันสำหรับ scientific freeze, 7 วันสำหรับ institutional documents และ 3 วันสำหรับ attachments; ถ้าหน่วยงานต้องเวลามากกว่าให้เผื่อเพิ่ม กำหนดยื่นจริงมาก่อน W12 release ได้ ห้ามรอ 20 ธ.ค. หาก deadline จริงคือ 11 ธ.ค.

Call-fit packet ต้องมี eligibility/PI/host, aims และประโยชน์, preliminary result ที่มีจริง, project duration, requested measurement/compute, budget rationale, data rights และ risk/alternative route การค้น call ทำได้; การติดต่อ ยื่น ซื้อ หรือจองเครื่องต้องมี authorization แยก

## 6. ควรใช้โมเดลไหน

คำแนะนำตั้งต้น ไม่ใช่ผล benchmark UET: [OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection) แยก Astra สำหรับ deep/ambiguous analysis, Sol สำหรับงานซับซ้อนที่ต้องคุมเวลา/ทรัพยากร และ Luna สำหรับ scoped tasks พร้อมแนะนำให้เทียบด้วย input เดียวกัน รายละเอียดรุ่นและ effort ตรวจจาก [official GPT-6 guide](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra) วันที่ 2 ต.ค. 2026

| งาน | แนะนำ | ขอบเขต |
| --- | --- | --- |
| Lead ของโจทย์วิจัยและ Goal | GPT-6 Astra / high | เลือกคำถาม, derive, ตรวจ circularity/units/claim, ตัดสิน branch; ไม่รับผลจากความมั่นใจตัวเอง |
| Proof/no-go ที่ยากและขอบเขตชัด | Astra / xhigh เฉพาะงานนั้น | ส่ง obligation, inputs และ exit condition ก่อนเพิ่ม effort; ไม่เปิด xhigh/max ยาวโดยไม่มีคำถามที่ตัดสินได้ |
| Implementation, regression, artifact และ reproducibility | GPT-6.1 Sol / high | สูตรและ acceptance ต้องล็อก; source hash และ independent controls ยังเหมือนเดิม |
| Source inventory/metadata | GPT-6 Luna / medium เป็นทางเลือก | ไม่เป็นผู้รับรอง formula/provenance/claim สุดท้าย; สิ่งที่สกัดต้องตรวจเทียบต้นฉบับ |

ถ้าใช้ตัวเดียวและไม่ติดโควตา เลือก Astra/high; หากต้องคุมทรัพยากร เลือก Sol/high แล้วจัด proof/claim review ที่จุดสำคัญ ไม่จำเป็นต้องใช้สามโมเดลพร้อมกัน ไม่มีการเปลี่ยน model configuration, เปิดห้อง หรือเรียกงานโมเดลอื่นจากเอกสารนี้

**ทดลองก่อนตัดสินว่าอะไรเร็วกว่า:** คง trial เดิม `NOT_RUN` จำกัด 90 นาทีต่อ configuration และใช้ hash input/acceptance เดียวกัน งานเทียบคือ (1) ตรวจ derivation/units (2) ทำ independent control (3) audit claim/source leakage บันทึก accepted task, critical errors, wall time รวมเวลาคนแก้, usage/cost เมื่อทราบจริง ใช้ configuration เบาสุดที่ไม่มี critical error และผ่านทุกเกณฑ์ ข้อมูลนี้ยังไม่ได้วัด; ค่าใช้จ่ายที่ไม่ทราบเป็น unknown ไม่ใช่ศูนย์

โมเดลที่เก่งขึ้นอาจลดเวลาตรวจเหตุผลและข้อผิดพลาด แต่สร้าง independent calibration, source permission, experimental rows หรือ lab access ที่ไม่มีไม่ได้ การเปลี่ยนโมเดลไม่ใช่เหตุผลให้ลด threshold หรือเรียกสองคำตอบ AI ว่า independent physical validation

## 7. กติกาทำงานให้จบเป็นเรื่อง

หนึ่ง decisive research question ต่อครั้ง; source/measurement inventory ทำคู่ขนานได้โดยไม่แก้ไฟล์ชุดเดียวกัน จัด effort ตั้งต้นก่อน freeze 60% derivation/identifiability, 20% independent verification, 20% source/portfolio แล้วปรับตาม blocker จริง ช่วง 8–11 ต.ค. เน้นตรวจซ้ำและจัดพอร์ต ไม่เปิดฟิสิกส์ใหม่

เมื่อสอง wave ไม่เพิ่ม proof/operator/source/independent check ที่เปลี่ยนข้อสรุป ให้ทำ explicit decision: เปลี่ยน approximation ที่มีเหตุผล, ขอ measurement input ที่ระบุได้, จำกัด/ยุติ branch ด้วยหลักฐาน หรือคง exact unresolved obligation ไม่เพิ่ม resolution/รันซ้ำโดยไม่มี hypothesis ใหม่ การตัดสิน branch ไม่เปลี่ยนสถานะ Goal โดยอัตโนมัติ

ห้ามเปิด Gravity/Galaxy/chaos ใหม่เพื่อแก้ปัญหาพอร์ต; Topic10 สนับสนุน numerical method ได้เมื่อ operator ล็อก แต่ comparator PASS ไม่รับรอง fluid physics ห้ามแก้ Core ของเจ้าของอื่นหรือใช้ผล lane ใหม่ล้าง FAIL branch เดิม

ทุก result card ใช้ 11 fields เดิม พร้อม artifact/hash, what is closed/open, next decisive input/calculation และ claim boundary รับงานตาม **คำถามที่มีคำตอบและหลักฐาน** ไม่ตามจำนวน test/ไฟล์/เวลารัน

## 8. ประโยชน์ระยะยาวและรายงานรอบนี้

ผลนี้จะส่งให้ Core เป็น response equation ที่รู้ units/validity/uncertainty และรู้ว่าต้องวัดอะไร จึงลด circular fitting และทำให้ thermal transport/entropy research เลือก input ได้ตรงจุด การขอทุนจะอธิบายได้ว่าเงินซื้อการวัดหรือการคำนวณใดที่เปลี่ยนข้อสรุป ไม่ใช่ขอรัน UET ไปเรื่อย ๆ ทั้งสองอย่างนี้ไม่เท่ากับ global UET closure หรือรับประกันได้ทุน

MAJOR_RESULT_CLOSURE: Planning/decision clarification only; no new scientific closure.

WHAT_IS_ACTUALLY_CLOSED: แยกเป้าพอร์ตสองสัปดาห์, ผลวิทยาศาสตร์, submission readiness และผลที่จะซื้อด้วยเวลาอีก 2–3 เดือน; model recommendation มี official sources แต่ trial ยัง NOT_RUN.

WHAT_REMAINS_OPEN: Matched vacuum/Wilson and thermal interaction remainder, independent source/scale/material/readout, physical transport, instrument feasibility/novelty, G0–G5/R1–R5 and broader Topic13 acceptance; owner Core composition is separately recorded, not reverified here. ผู้ใช้ยังไม่เลือกทุน/PI/งบ.

DEPENDENCY_UNLOCKED: None; งานวางแผนไม่ปลด physical/Core/Gravity gate.

STATUS: PLAN_REVIEW_READY_NOT_SCIENTIFIC_ACCEPTANCE.

WHAT_CHANGED: เพิ่ม executive model/delivery/next-round detail และ backward-compatible canonical planning addendum; แก้ current evidence/controller ให้แยกจาก historical snapshot ไม่เริ่ม sprint ใหม่หรือเปลี่ยน completion rule.

EQUATION_OR_MAPPING: Proposed research path only: same-action stationary response -> declared low-T thermal prescription -> independent dimensional/source/readout map -> locked comparison or scoped structural proof. Natural-unit Phi ไม่ใช่ Kelvin alpha โดยอัตโนมัติ.

VERIFICATION: อ่าน latest Topic13 artifact/notes, แผนและ Core owner README; ตรวจ machine-readable companion/links/hashes/date invariants และ planning regressions แยกจาก scientific revalidation โดยบันทึกผลจริงใน UPDATE_LOG.

CONTROLLING_BLOCKER: renormalized_cubic_sunset_and_vacuum_Wilson_matching_open in the new EFT; empirical calibration/source/material และ actual funding call ยังเปิดแยก. Hartree predecessor retains its own low-T blocker.

NEXT_ACTION: ทำแพ็ก A ใหม่ที่มี independent controls และแพ็ก B measurement card ก่อน 7 ต.ค.; เตรียม portfolio review 11 ต.ค.; 25 ต.ค. review R1 ตามหลักฐาน ไม่ใช่วันผ่านอัตโนมัติ.

CLAIM_BOUNDARY: Plan only. ไม่สร้าง EOS/calibration/data, ไม่ fit holdout, ไม่เปลี่ยน 1e-6/ontology/Core composition, ไม่อ้าง pristine blind เพราะ prior Xie exposure ยัง REVIEW_REQUIRED. Existing active Goal ไม่ถูกแทนที่/รับสำเร็จ; ไม่มี model trial/configuration change, contact/purchase/submission หรือ public API ใหม่.
