# แผนต่อยอด 12 สัปดาห์และการเลือกโมเดลสำหรับงานวิจัย UET

วันที่: 27 กันยายน 2026 | ต่อจาก [แผน 14 วัน](RESEARCH_PLAN_14D_FUNDING_2026-09-27.md)

เอกสารนี้เพิ่มภาพระยะยาวและแผนรองรับรอบทุนถัดไปตามคำขอผู้ใช้ โดยคงผลงาน 14 วันเป็น milestone แรก ข้อมูลวันเปิด/ปิดรับทุนจริงยังไม่ทราบ ช่วงสัปดาห์ 8 และ 12 เป็นวันเตรียมพอร์ตที่เสนอ ไม่ใช่การยืนยันว่าหน่วยงานจะเปิดรอบในวันนั้น

## 0. Revision 1 ตุลาคม: ผลที่ต้องซื้อด้วยเวลาที่เพิ่ม

คงวันส่งมอบพอร์ตภายใน 11 ตุลาคมตามแผนเดิม ไม่เริ่มนับ 14 วันใหม่จาก revision นี้ วันดังกล่าวยังเป็น planning target ไม่ใช่ deadline ของทุนที่ยืนยันแล้ว หากผู้ยื่นต้องการเปลี่ยนวัน ให้บันทึก calendar revision แยกจากการเปลี่ยน scientific acceptance

**คำถามหลัก:** หลังแช่แข็ง equilibrium matching แล้ว สมการ O(2)/He-4 กำหนด thermal response อิสระได้แค่ไหน และการวัดใดตัดความกำกวมที่เหลือ? ไม่ตั้ง Goal ว่าเพิ่ม artifacts ให้มากที่สุด หรือปิดทุกระบบในสองสัปดาห์

สถานะต้องอ่านแบบแยก lane: Core matrix บันทึก O(2)/He-4 composition เป็น bounded `CLOSED_FOR_CORE` แล้ว แต่การรับ interface และ imported shear channel ไม่ได้ปิด independent second-sound prediction, complete finite-temperature transport หรือ graphite TTG validation งานใหม่นี้ไม่ถอนสถานะเดิมและไม่ขยายสถานะเดิมไปครอบคลุมโจทย์ใหม่ ใช้ Core snapshot ปัจจุบันกับ hash/lineage review ก่อน handoff; ห้ามใช้ `full_core_unlock=false` ของ diagnostic ใหม่ไปเขียนทับ gate ของ composition เดิม

หลักฐาน 1 ตุลาคมแยกคำถามย่อยได้ชัด: [thermal phase-gradient curvature](Result/artifacts/T13_THERMAL_GRADIENT_CURVATURE_STATIONARITY_2026-10-01.md) คำนวณได้และตรวจสองวิธีแล้ว แต่ `f_path=f_held-2Z*Omega_x/lambda` มี nonstationary amplitude-path term ที่ยังต้องจัดการ จึงยังไม่เป็น physical current หรือ He-II mode prediction ผลนี้ไม่พิสูจน์ว่า consistent perturbative completion เป็นไปไม่ได้

ผลต่อมาในวันเดียวกัน: [one-loop thermal Ward/current](Result/artifacts/T13_THERMAL_ONE_LOOP_WARD_CURRENT_2026-10-01.md) คำนวณ tadpole กับ bubble และปิด zero-momentum Ward/static-current matching ที่ fixed Phi ในลำดับ one-loop แล้ว แพ็ก A จึงไม่ต้องเริ่มจากการเดาค่า zero-momentum correction อีก แต่ต้อง derive finite-q/frequency kernel และแก้ infrared/nonuniform-expansion boundary ก่อนรับ stationary retarded operator ผลนี้ไม่ทำให้ W4 หรือ physical gate ผ่านโดยอัตโนมัติ

### ผลส่งมอบสองสัปดาห์ที่ต้องมี

อัปเดตผลถัดมา 1 ต.ค.: [finite-q thermal 1PI และ infrared boundary](Result/artifacts/T13_FINITE_MOMENTUM_THERMAL_1PI_2026-10-01.md) คำนวณ bubble/kernel ที่ขึ้นกับ momentum และความถี่เชิงซ้อน พร้อมตรวจ static-current matching แล้ว เทอม radial โตแบบ `1/q` และมีสเกล diagnostic `q_IR=0.0275` ในผู้สมัครเดิม จึงไม่ต้องเริ่มแพ็ก A ด้วยการสร้าง kernel ใหม่ แต่ต้องเชื่อม amplitude-direction/IR treatment, current vertices และ real-axis limit อย่างสอดคล้องก่อน physical admission ผลนี้ไม่ใช่ damping หรือการปิด full Topic13; ตัวเลือก D5 และวันพอร์ตเดิมไม่เปลี่ยน

| วันที่ภายใน | ผลที่รับงาน | ไม่ให้นับเป็นความสำเร็จแทน |
| --- | --- | --- |
| 2 ต.ค. / D5 | decision card เลือก predictive, structural หรือ unresolved; มีสมการ/สมมติฐาน/หลักฐานที่ใช้ตัดสิน | เรียก missing operator ว่า no-go หรือเลือกผู้สมัครเพราะความเร็วดูดี |
| 7 ต.ค. / D10 | หนึ่ง scientific result ที่พิสูจน์/ตรวจซ้ำได้ พร้อม measurement design; หาก unresolved ต้องระบุ proof obligation ที่ยังไม่เสร็จ | เปลี่ยน diagnostic `PASS` เป็น physical closure หรือลดเกณฑ์เพื่อทันวัน |
| 11 ต.ค. / D14 | portfolio v1: report, claim map, evidence hashes, rerun/review, pitch และคำอธิบายว่าเงินทุนจะซื้อหลักฐานอะไร | เอกสารสวยแต่ไม่มีผลใหม่ หรือรับรอง submission-ready ทั้งที่ยังไม่รู้ call/PI |

### แพ็กวิจัยต่อที่มีปลายทาง

| แพ็ก / เจ้าของ | คำถามและ acceptance | ทางออกเมื่อยังไม่ผ่าน |
| --- | --- | --- |
| A / Topic 13, W3–W4 | เลือกหนึ่ง loop-ordering/resummation prescription; derive tadpole, stationary amplitude, zero-momentum Ward/self-energy และ current จาก approximation เดียว; ตรวจ derivative protocol, low-T limit, stability และ error-control assumptions | ส่ง consistency-boundary proof เฉพาะ class ที่ทดสอบ หรือคง unresolved พร้อม missing calculation; ห้ามอ้าง no-go ของทุก completion |
| B / Topic 13 + Core admission, หลัง A พร้อม | ปิด source-to-state และ detector-to-observable map พร้อม units, independent parameter origins, normal-component definition และ uncertainty; เลือก observable หลักหนึ่งชนิดก่อนขยาย | ถ้ายังไม่ admitted ให้ใช้ operator-completion/identifiability result; งด physical prediction score |
| C / Source owner, คู่ขนาน A–B ถึง W6 | primary measurement record ที่ state/frequency/protocol/permission/uncertainty ตรง; ล็อก calibration/comparison overlap และ competitor ก่อนเทียบ | measurement-feasibility package พร้อม precision/geometry/readout และรายการที่ต้องขอ; ไม่สร้าง empirical rows แทน |
| D / Topic 10 numerical support, หลัง operator lock | คำนวณอีกวิธีด้วย fixed parameters; ตรวจ analytic limits, convergence และ conservation/ledger ที่เกี่ยวข้อง | ซ่อมเฉพาะ discrepancy ที่เปลี่ยนข้อสรุป ไม่เปิด turbulence/chaos wave ใหม่ |
| E / Research lead + human reviewer, W7–W12 | comparison แบบไม่ rematch หรือ scoped structural result พร้อม sufficient-measurement argument; ตรวจอีก state/protocol เฉพาะเมื่อ preregistration พร้อม | เผย failed comparison/remaining identifiability; conditional result ต้องติดป้าย ไม่เลื่อนเป็น external validation |

การได้เวลาสองเดือนควรเพิ่มอย่างน้อย **consistent response prescription + independent input หรือ feasibility specification** การได้เดือนที่สามควรเพิ่ม **comparison/independent reproduction หรือ measurement-design proof ที่แรงขึ้น** ไม่สัญญาว่ารันนานพอแล้ว Full Topic 13 จะปิดเอง

### วิธีตัดสินทุกสองสัปดาห์

รับงานด้วยหนึ่ง result card: คำถาม, version/สมมติฐาน, สิ่งที่ปิดจริง, equation/observable, units, source/hash, วิธีตรวจอีกแบบ, blocker ที่เหลือ และ next decision ทุก card ใช้ 11 report fields เดิม และแยก `research_result_ready`, `portfolio_review_ready`, `submission_ready` ออกจากกัน

หากสอง wave ไม่เพิ่ม source, proof, operator หรือ independent check ที่เปลี่ยนข้อสรุป ให้หยุด rerun เดิมและตัดสินเลือก measurement request, scoped model revision หรือยุติ branch ด้วยเหตุผล การตัดสินเชิงวิจัยนี้ไม่ใช่การเปลี่ยนสถานะ Goal ของระบบโดยอัตโนมัติ ห้ามยุติ scope ด้วยการตั้ง complete เมื่อยัง unresolved

จัดสรร effort เริ่มต้นประมาณ 60% สมการ/identifiability, 20% verification, 20% source/portfolio/call-fit แล้วปรับตาม controller จริง ช่วง 8–11 ตุลาคมเน้น verification และ portfolio หลัง scientific freeze การค้น/รันแต่ละงานต้องระบุว่า input ใหม่ใดจะทำให้ข้อสรุปเปลี่ยน ไม่เปิดทุก topic แข่งกัน

ความใหม่ยังต้องมี related-work/claim comparison ที่แยก imported two-fluid EFT ออกจาก contribution ของ UET; การคำนวณ method มาตรฐานซ้ำไม่รับประกัน novelty และโมเดล AI สองตัวเห็นตรงกันไม่แทนผู้เชี่ยวชาญหรือ external replication

## 1. สิ่งที่งานสองสัปดาห์จะซื้อให้ระยะยาว

เป้าหมายระยะยาวคือทำให้สะพานความร้อนของ UET มีสมการและ observable ที่เชื่อมกับการวัดในสภาวะระบุชัด โดยรู้ว่าความสามารถทำนายใดมาจาก derivation และค่าใดต้องอาศัยการวัดภายนอก งานสองสัปดาห์แรกตัดสินว่าทุนควรซื้อการวัดอะไรหรือควรแก้ model class ตรงไหน

| ผลที่ได้จาก sprint แรก | สิ่งที่จะทำต่อได้ | สิ่งที่หลีกเลี่ยงได้ |
| --- | --- | --- |
| calibration และ derivative protocol ถูกแยกชัด | เลือก perturbation ที่วัดได้จริงและไม่ใช้ปรับเทียบซ้ำ | การใช้ matching identity เป็นหลักฐานทำนาย |
| parameter combinations/nullspace ที่พิสูจน์ได้ | เลือก measurement ที่เพิ่มข้อมูลและออกแบบ precision budget | เก็บข้อมูลจำนวนมากแต่ยังตอบพารามิเตอร์เดิมไม่ได้ |
| มี admitted response operator หรือ proof ว่ายังขาด closure | สร้าง prediction pipeline หรือ minimal candidate extension อย่างมีเหตุผล | เพิ่ม field/coefficients โดยไม่รู้ว่าช่วย observable อย่างไร |
| clean reproduction bundle และ evidence manifest | ให้ผู้ร่วมวิจัยตรวจ และใช้เป็น preliminary result ในทุน | ต้องสร้างความเชื่อถือจากเรื่องเล่าอย่างเดียว |
| comparison/uncertainty contract | รับข้อมูลใหม่เข้าระบบแล้วตัดสินตามกติกาที่ล็อกไว้ | เลือก threshold หลังเห็นผล |

ผล no-go ที่จำกัดขอบเขตอาจเป็นงานสำเร็จทางวิจัยได้ แต่ความน่าสนใจสำหรับทุนยังต้องอธิบายความใหม่และงานที่ทุนจะทำต่อ การสรุปว่าไม่มีข้อมูลอย่างเดียวไม่พอ

## 2. ใช้โมเดลไหน

ตรวจ official OpenAI documentation อีกครั้งวันที่ 1 ตุลาคม 2026: [model selection](https://developers.openai.com/api/docs/guides/model-selection), [GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) และ [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) จัด Astra สำหรับงานยากที่สุด และเสนอให้เปรียบเทียบ Sol 6.1 กับ Astra บนงานจริงเมื่อคำนึงถึงต้นทุน การแบ่งงานด้านล่างเป็นข้อเสนอสำหรับ UET ไม่ใช่ benchmark ที่พิสูจน์แล้วใน repo นี้

| งาน | โมเดล/effort เริ่มต้นที่เสนอ | ส่งมอบที่ตรวจได้ |
| --- | --- | --- |
| เจ้าของ Goal และการตัดสินวิจัย | **GPT-6 Astra / high** | อธิบายว่าอะไรปิดจริง next controller และหลักฐานที่เปลี่ยนข้อสรุป |
| derivation, identifiability, no-go, units/protocol conflict | Astra / xhigh เฉพาะโจทย์ที่นิยามแล้ว | proof/assumptions/counterexample พร้อมวิธีหักล้าง |
| implementation, tests, numerical controls, artifact production | **GPT-6.1 Sol / high**; medium สำหรับงานตรงไปตรงมา | executable result และ log; ให้ Astra ตรวจสมการที่กระทบ interpretation |
| inventory, hash/link checks, metadata extraction ที่ schema ชัด | GPT-6 Luna / medium | structured rows พร้อม locator; ส่ง uncertainty/ambiguity กลับผู้วิเคราะห์ |
| ตรวจข้อสรุปก่อน D10/W8/W12 | Astra / high หรือ xhigh ในบริบทสะอาดและวิธีคำนวณอีกแบบ | adversarial review และ independent reimplementation; ไม่ถือเป็น external validation |
| เขียนเอกสาร/สไลด์จาก claim map ที่ล็อกแล้ว | Sol 6.1 / medium; Astra ตรวจ claim รอบสุดท้าย | แต่ละข้อความสำคัญย้อนถึงหลักฐานได้ |

**ถ้าเลือกโมเดลเดียวสำหรับ Goal นี้ ให้เลือก GPT-6 Astra / high.** เมื่อผล reasoning รอบแรกยังขาด proof obligation ที่ระบุได้ ให้ใช้ xhigh กับคำถามนั้น ส่วน max ให้ใช้เฉพาะข้อยากที่ระบุช่องว่างได้และต้องวัดผลว่าช่วยจริง ห้ามตีความว่า effort สูงขึ้นจะสร้างข้อมูลการทดลองที่ขาดอยู่

**ถ้าต้องควบคุมค่าใช้จ่าย ให้ Sol 6.1 / high ทำ execution เป็นส่วนใหญ่ แล้วใช้ Astra ที่จุดตัดสิน D5, D10, W4/W6 และก่อนส่งพอร์ต.** หากใช้ได้ตัวเดียวและ Astra ใช้เวลาหรือโควตามากเกินไป ให้ใช้ Sol 6.1 / high โดยรักษา analytic checks และ review ไม่ลดเกณฑ์วิจัยเพื่อประหยัด Luna เป็นตัวเลือกเสริม ไม่จำเป็นต้องเปิดสามโมเดลตลอดเวลา เวลารันและค่าใช้จ่ายจริงต้องวัดจากงานที่เสร็จผ่านเกณฑ์ รวมรอบแก้ ไม่เทียบเพียงราคาต่อ token

รายชื่อโมเดล/effort เหล่านี้มีในเครื่องมือของ session ปัจจุบัน แต่สิทธิ์ใช้งานและโควตาขึ้นกับบัญชี/การตั้งค่าจริง แผนนี้ไม่ได้เปลี่ยนโมเดลให้แชท ไม่ตั้งค่า routing อัตโนมัติ ไม่เริ่มห้องใหม่หรือซื้อ API การใช้ Codex ผ่านบัญชีกับราคา API เป็นคนละเรื่อง; ไม่ประมาณค่าใช้จ่ายบัญชีจากตาราง API

### ทดลองแบ่งงานใน D1 แบบสั้น

ให้ Astra และ Sol 6.1 ทำโจทย์เดียวกันจาก source packet ที่ตรึงไว้ จำกัดการประเมินรวมประมาณ 60–90 นาทีถ้าทั้งคู่ใช้ได้ ใช้เมื่อเริ่มแบ่งงานหรือเปลี่ยนรุ่น ไม่ restart D1 เพราะเปลี่ยนโมเดล ไม่ปล่อยให้การเลือกโมเดลกิน sprint หากใช้ได้ตัวเดียวให้ใช้ตัวนั้นและตรวจด้วยเครื่องมือ

โจทย์ตรวจหกข้อ: (1) matching identity ไม่ใช่ validation, (2) chain-rule Phi Jacobian, (3) source uncertainty ไม่ใช่ sigma เมื่อไม่มีนิยาม, (4) initial rate ทำให้ dip time เปลี่ยน, (5) source missing ไม่ใช่ no-go, (6) historical no-access ไม่รับรอง blinding หลัง exposure ให้ reference answers จาก artifacts/derivations และทดสอบโค้ดจริง

บันทึก critical errors, traceable citations, correctness, reviewer correction time, wall time และ usage ที่ระบบเปิดเผย ผู้รับงานวิจัยวิกฤตต้องไม่มี critical false claim ในชุดนี้ ผู้ทำ inventory ต้องเก็บ units/locator/data-role ได้ครบ อัปเกรดบทบาทเมื่อมีหลักฐานคุณภาพ ไม่ใช้คะแนน self-review ของโมเดลอย่างเดียว การเปลี่ยนโมเดลไม่ทำให้ข้อมูลหรือการตรวจทางฟิสิกส์เป็นอิสระโดยตัวมันเอง

## 3. เส้นทางหลัง D14 ตามผลจริง

| ผลวันที่ 11 ต.ค. | งานหลักรอบต่อไป | เงื่อนไขจบที่ตรวจได้ |
| --- | --- | --- |
| มี prediction operator ที่กำหนดครบ | ทดสอบกับ primary response ที่ matched protocol และไม่ได้ใช้ matching; ตรวจ failure modes | comparison + uncertainty + competitor ที่ reproducible; ขัดข้อมูลต้องรายงาน |
| พิสูจน์ nonidentifiability/no-go ของ class ปัจจุบัน | เลือก measurement หนึ่งชุดหรือ minimal extension หนึ่งแบบที่แก้ ambiguity ที่พิสูจน์แล้ว | rank/structural gap ปิดด้วย independent evidence หรือ explicit new assumption |
| พิสูจน์ยังไม่เสร็จ | ใช้ไม่เกินหนึ่งสัปดาห์ทำข้อพิสูจน์ย่อยที่ตัดสินได้ หรือ scope down อย่างมีเหตุผล | ไม่เปลี่ยน unresolved เป็น no-go; มี finite question และ stop rule ใหม่ |
| วิจัยเสร็จแต่ส่งทุนไม่ได้ด้วยคุณสมบัติ/เอกสาร/เวลา | คง research scope แล้วทำ partner/call-fit และ reviewer feedback | พร้อมรอบใหม่โดยไม่เพิ่มทฤษฎีเพื่อชดเชยปัญหาธุรการ |
| ผลไม่สนับสนุน physical mapping เดิม | เผยข้อจำกัดใน manuscript; เตรียม candidate ใหม่คนละ version หากมีเหตุผล | baseline เดิมถูกเก็บ; ไม่มี post-hoc retuning ที่เรียกว่า prediction |

จัดเป้าหมายวิจัยหนึ่งเรื่องต่อช่วงสองสัปดาห์ และ scientific release ทุกสี่สัปดาห์ วันครบกำหนดไม่ทำให้ scientific gate เปลี่ยนเป็นผ่านเอง

## 4. แผนสัปดาห์ 3–12

นับจาก D1 = 28 ก.ย. 2026: W8 จบ 22 พ.ย.; W12 จบ 20 ธ.ค. หากรอบทุนถัดไปอยู่ 2–3 เดือน **หลัง** รอบแรก ให้ใช้วันประกาศจริงจัด submission buffer ใหม่ โดยเก็บ milestone วิจัยเดิม ไม่เดาวันเปิดทุน

สองถึงสามเดือนหลัง 11 ตุลาคมจะอยู่ราว 11 ธันวาคม–11 มกราคม จึงไม่เท่ากับ W8/W12 จากวันเริ่ม sprint หาก call จริงอยู่เดือนมกราคม ให้ใช้ช่วงหลัง 20 ธันวาคมกับ reviewer response, missing institutional documents และ rerun ของ release ที่ตรึงแล้ว ไม่ขยายทฤษฎีใหม่จนกิน submission buffer รอบทุนดังกล่าวยังไม่ได้รับการยืนยัน

| ช่วง | งานที่เน้น | สิ่งที่ต้องปิดก่อนขยับ |
| --- | --- | --- |
| W1–2 / 28 ก.ย.–11 ต.ค. | sprint ตามแผนหลัก | predictive-content/identifiability decision + measurement design + portfolio v1 |
| W3–4 / 12–25 ต.ค. | review ข้อสรุปและ admit response protocol หรือ minimal model extension ที่จำเป็นเพียงหนึ่งแบบ | `RESPONSE_PROTOCOL_AND_MODEL_CLASS_READY`: state, equations, observables, parameters, units, source/assumption origin และ valid regime ครบ; external-ready ยังแยก |
| W5–6 / 26 ต.ค.–8 พ.ย. | ปิด primary data/permission/uncertainty หรือ lab feasibility; ล็อก independent comparison | `INDEPENDENT_RESPONSE_INPUT_READY` หรือ `MEASUREMENT_FEASIBILITY_PACKAGE_READY` พร้อมเหตุที่ยังไม่มีข้อมูล; แยกสองระดับนี้ |
| W7–8 / 9–22 พ.ย. | รัน comparison ที่ล็อกไว้ หรือจบ conditional prediction/design ถ้าข้อมูลยังไม่ได้; independent reproduction | portfolio v2: ผลใหม่ที่เพิ่มจาก v1 + manuscript + reviewer response + call-specific proposal หากรู้ทุน |
| W9–10 / 23 พ.ย.–6 ธ.ค. | ขยายอีก state/frequency เพื่อทดสอบ generalization โดยตรึงพารามิเตอร์; ถ้าไม่มีข้อมูลให้ทำ identifiability/design และ protocol readiness ต่อ | `CROSS_PROTOCOL_ROBUSTNESS_RESULT` แบบ empirical หรือ conditional ต้องบอกประเภท; ถ้าต้อง refit ให้เปลี่ยน evidence class ตามจริง |
| W11–12 / 7–20 ธ.ค. | ตรวจอิสระครั้งสุดท้าย รับ feedback และเชื่อมผลกลับ Core แบบจำกัดขอบเขต | portfolio v3 + reproducible release + full evidence/uncertainty trail + proposal/budget/partner evidence ที่มีจริง |

รายการชื่อผลในตารางเป็น planned deliverables ไม่ใช่สถานะผลที่ปิดแล้ว ไม่ใช้ field `CLOSED_FOR_CORE` เพียงเพราะ week complete

### เกณฑ์ข้อมูลที่ต้องได้ภายใน W6

Primary source หรือ experiment record ต้องให้ material/state, temperature scale/path, driving frequency, amplitude, geometry, preprocessing, uncertainty และสิทธิ์ใช้ข้อมูลที่ตรงกับการเทียบ ต้องระบุว่าข้อมูลเดียวกันเคยสร้าง calibration หรือ recommended inputs ที่เราใช้อยู่หรือไม่ ข้อมูลจากคนละหน้าใน review เดียวกันยังอาจมี provenance/covariance ร่วมกัน

อัปเดต 28 ก.ย.: [J02 source-ancestry audit](Result/artifacts/T13_HE4_J02_CALIBRATION_SOURCE_ANCESTRY_2026-09-28.md) พบความทับซ้อนระดับวิธีวัดระหว่าง calibration ของ `alpha_Phi_K` กับ second-sound reference ในช่วงอุณหภูมิเดียวกัน จึงใช้ J02 เป็น comparator สำหรับออกแบบ protocol เท่านั้น ไม่ใช่ independent validation. งาน W5-W6 ต้องหาแหล่งวัดที่ไม่สืบจาก sound calibration หรือออกแบบการวัดตอบสนองอิสระ และตรวจ covariance ก่อนใช้คำว่า independent comparison; หากทำไม่ได้ ให้เลือกพอร์ตแบบ methods/measurement feasibility ตามกติกาด้านล่าง

เส้นทางที่ลงชื่อแล้วอยู่ใน [measurement-route screen](Result/artifacts/T13_HE4_INDEPENDENT_MEASUREMENT_ROUTE_SCREEN_2026-09-28.md): ตรวจ primary Wang key 5 และ calibration ทางเลือก Dash-Taylor ก่อนขยายรายการแหล่งอื่น หาก primary rows/permission/uncertainty หรือ temperature-scale conversion ไม่ครบใน W6 ให้คง `NOT_ADMITTED` และทำพอร์ต feasibility แทนการเปลี่ยนแหล่งจากชื่อบทความอย่างเดียว

ถ้าทำแล็บ: ต้องมี feasibility assessment ของ cryogenic access, thermometry, excitation/readout, safety/operator requirements, duration และ quotation จากผู้ให้บริการจริง ไม่มีคำมั่นว่าจะได้ lab slot หรือข้อมูลในสองเดือนโดยยังไม่คุยกับแล็บ การติดต่อแล็บเป็น action ที่ต้องได้รับอนุญาตจริง; แผนสามารถเตรียม request packet ล่วงหน้าได้

ถ้า W6 ยังหา input ไม่ได้ ให้ส่ง portfolio v2 เป็น **theory/methods + experimental design pilot** พร้อม measurement specification และเหตุผลขอทุนสร้างข้อมูล ไม่เติมข้อมูล synthetic เป็น external evidence เป้าหมาย empirical ยังคงเปิด

## 5. ถ้าพลาดรอบทุนแรกต้องเปลี่ยนอะไร

ผล [thermal gradient/tadpole decomposition](Result/artifacts/T13_THERMAL_GRADIENT_CURVATURE_STATIONARITY_2026-10-01.md) ระบุงาน W3–W4 ให้ละเอียดขึ้น: สร้าง matched stationary amplitude, Ward self-energy และ current response ใน prescription เดียว ค่า static thermal curvature คำนวณได้แล้ว แต่มี amplitude-path contribution ที่ต้องตีความด้วย loop ordering/resummation ที่สอดคล้องกัน งานระยะยาวจึงมีทั้ง consistency target เชิงตัวเลขและการตรวจ low-temperature limit ก่อนใช้ source/detector และข้อมูลวัสดุ; ยังไม่รับประกันว่า complete prescription จะสำเร็จตามกำหนด

อัปเดต 1 ต.ค.: [conditional operator/domain decision](Result/artifacts/T13_CONDITIONAL_TWOFLUID_OPERATOR_2026-10-01.md) ทำให้โจทย์ W3–W4 ชัดขึ้น: derive finite-T relative-flow current และ normal component จาก prescription เดียวที่ jointly stationary แล้วตรวจ stiffness กับช่วงเชิงสมการ ก่อนเพิ่ม source/detector map การแทน tree stiffness กับ thermal EOS ตรง ๆ ถูกปฏิเสธที่หนึ่งในสองผู้สมัคร จึงไม่เลือกผู้สมัครที่ผ่านเพียงเพราะให้ความเร็วเหมาะสม ทั้งคู่ยังไม่มี material admission งานนี้นำไปใช้ต่อเป็น consistency test สำหรับ completion ใหม่และ measurement design; การทดลองอิสระยังเป็นงาน W5–W6 ตามสิทธิ์/protocol ที่ได้รับจริง

ก่อนตัดสินใจเลื่อนให้แยกสาเหตุ: (A) พลาด deadline, (B) คุณสมบัติ/สังกัดไม่ตรง, (C) หลักฐาน preliminary ยังไม่พอ, (D) panel ไม่เห็น novelty/impact, (E) ขาด partner/budget support แต่ละสาเหตุใช้วิธีแก้ต่างกัน

- D14 เก็บ portfolio v1 และ scientific decision เป็น snapshot แม้ไม่ได้ยื่น ไม่เขียนทับด้วยเวอร์ชันถัดไป
- ภายใน W3 ตรวจ call calendar และ eligibility จากประกาศจริง รวมทุนทางเลือกที่รับ methods/feasibility scope ถ้ามีคำวิจารณ์จากผู้ประเมิน ให้ทำ response matrix ตามข้อความจริง; ถ้ายังไม่มีอย่าแต่งเหตุผลถูกปฏิเสธ
- W4 เลือก target call หลักหนึ่งและสำรองหนึ่งเมื่อได้ข้อมูลจริง ระบุ PI/สังกัด เอกสาร partner งบ เพดาน overhead และเวลารออนุมัติ
- W6 ตัดสินว่ารอบถัดไปจะยื่น empirical comparison หรือ feasibility proposal ตาม evidence ที่ได้ แล้วคง scope ให้สอดคล้องทั้ง title, aims, methods และ budget
- ก่อน deadline จริง 14 วัน ล็อก scientific scope; ก่อน 7 วัน ปิดเอกสารหน่วยงาน/งบ; ก่อน 3 วันตรวจแบบฟอร์ม ลิงก์และไฟล์แนบ การส่งจริงต้องผ่าน author/institution approval ตาม call
- เวลาที่เพิ่มต้องซื้อหลักฐานอย่างน้อยหนึ่งอย่างจาก independent input, stronger derivation, reproducibility หรือ measurement feasibility ไม่ใช้แค่ขยายจำนวนหัวข้อ/หน้า/graphs

ทุนแต่ละหน่วยงานอาจไม่มีรอบทุก 2–3 เดือน ตารางนี้ทำให้เราเตรียมตัวได้หลายจุด แต่ต้องปรับตามประกาศ ไม่รับประกันโอกาสหรือกำหนดทุนจากปฏิทินภายใน

## 6. ภาพระยะ 6–12 เดือนแบบมีเงื่อนไข

ถ้าสะพานความร้อนมี response/state map ที่ตรวจได้และ independent evidence ตามเกณฑ์ เป้าหมายถัดไปคือส่ง parameter/uncertainty/entropy/transport contract เดียวกันให้ Core และ Topic 10 พัฒนา constitutive transport ในขอบเขตที่ระบุ ข้อมูลที่ใช้ calibrate ต้องแยกจากข้อมูลที่จะทดสอบ generalization

Curved 3+1 และ Gravity เดินตาม dependency gate ของตนเอง รวม conserved-matter evolution, boundaries, observable map และ constraint tests ความสำเร็จของ He-4 ไม่ทำให้ Gravity หรือ graphite ผ่านอัตโนมัติ Galaxy อยู่หลัง metric-to-observable mapping และข้อมูล density ที่เหมาะสม

ถ้าผลวิจัยแสดงว่าตัวแบบเดิมยังไม่รองรับการวัดที่ตั้งใจไว้ ผลระยะยาวที่ได้คือรู้ว่า assumption ไหนต้องเปลี่ยน และมี regression suite ป้องกันไม่ให้กลับไปอ้าง identity เดิมเป็น prediction เส้นทางใหม่ต้องมี version/registry ของตนเอง ไม่ลบผลขัดแย้งของ baseline

ตัวชี้วัดระยะยาวคือจำนวน **คำถามวิจัยที่มีคำตอบรองรับ**, observable ที่ทำนายโดยไม่ rematch ได้, independent measurement constraints และการทำซ้ำจากผู้ร่วมวิจัย หลีกเลี่ยงเปอร์เซ็นต์ปิดทั้งทฤษฎีที่ไม่มีนิยาม

## 7. การแบ่งกำลังและการใช้ Goal ต่อเนื่อง

ใช้กำลังหลักกับหนึ่ง thermal question; ให้ source/review กับ numerical verification เป็นสายสนับสนุน ไม่เปิดทุก topic พร้อมกัน ทบทวนทุกสองสัปดาห์ว่าตัวควบคุมเปลี่ยนจากหลักฐานใด ประเมิน compute/runtime จาก smoke run ก่อน queue ใหญ่; การจ่ายเงินหรือเช่าเครื่องต้องมีงบที่ผู้ใช้อนุญาต

Goal แรกจบตาม G0–G5 ของ sprint 14 วัน จากนั้นตั้ง Goal ถัดไปจาก scientific decision ที่ได้จริง ไม่ตั้ง Goal เดียวว่า “ปิด UET” ยาวสามเดือนโดยไม่มีจุดรับงาน ใช้ planned checkpoint W4/W6/W8/W10/W12 ใน JSON เป็น handoff; การเริ่ม Goal หรือ recurring automation ยังเป็นการกระทำแยกจากเอกสารนี้

ภายในโควตาจำกัด ให้รักษา Astra ที่ derivation/decision review และ Sol ที่ execution ก่อนลดการตรวจเพื่อประหยัด ถ้าโมเดลเปลี่ยนรุ่นกลางงาน ให้ rerun ชุดประเมินหกข้อและบันทึก version/effort; ไม่อ้างว่ารุ่นใหม่ทำให้งานเดิมถูกต้องย้อนหลัง

## 8. สิ่งที่ยังต้องได้รับข้อมูลจากผู้ยื่น

ชื่อทุน/ประเทศ/หน่วยงาน, รอบ deadline จริง, สังกัดและคุณสมบัติ PI, งบที่จะขอและเวลาที่ทำได้จริง, การเข้าถึงผู้เชี่ยวชาญ/แล็บ และรูปแบบพอร์ตที่หน่วยงานต้องการ ยังเป็น OPEN ข้อมูลเหล่านี้ไม่ขวางการเริ่ม research sprint แต่ขวางการเรียกชุดเอกสารว่า submission-ready

CLAIM_BOUNDARY: แผนระยะยาวและการเลือกโมเดลเป็นข้อเสนอการจัดงาน ไม่มีการเริ่ม Goal, เปลี่ยนโมเดล, รับรองทุน, ติดต่อ partner หรือ promote ผลทางฟิสิกส์จากการออกแผนนี้
