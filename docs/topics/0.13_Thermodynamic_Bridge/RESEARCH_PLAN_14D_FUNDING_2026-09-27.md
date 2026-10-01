# แผนวิจัย 14 วัน: ผลทำนายอิสระของ Topic 13 และพอร์ตขอทุน

วันที่ออกแผน: 27 กันยายน 2026 | D1: 28 กันยายน | D14: 11 ตุลาคม 2026 (Asia/Bangkok)

สถานะ: แผนเสนอเพื่อรันใน Goal mode; Goal พอร์ต 14 วันและ gate G0-G5 ยังไม่เริ่ม แต่มีผลย่อยก่อน sprint ห้าชิ้นที่ต้องนำเข้ารอบ baseline โดยไม่เลื่อน readiness วันส่งมอบตีความจากคำตอบผู้ใช้ว่า “2 สัปดาห์”; ยังไม่ทราบวันปิดรับของทุนจริง ชื่อทุน สังกัดผู้ยื่น และงบที่ขอ

ตัวควบคุมงาน: [funding_portfolio_14d_plan.json](Data/03_Research/funding_portfolio_14d_plan.json) | คำสั่งเริ่มงาน: [GOAL_BRIEF_FUNDING_14D.md](GOAL_BRIEF_FUNDING_14D.md)

แผนต่อยอดและการเลือกโมเดล: [Roadmap 12 สัปดาห์](RESEARCH_ROADMAP_MODELS_12W_2026-09-27.md) ครอบคลุม Astra/Sol/Luna, portfolio v2–v3 และการเตรียมรอบทุนใหม่หากพลาดรอบแรก

## 1. ผลลัพธ์หลักที่จะปิดก่อน

ผลล่าสุด: [collisionless soft collective kernel](Result/artifacts/T13_HARTREE_SOFT_COLLECTIVE_2026-10-01.md) derive thermal ray limit และตรวจกับ full finite-q response แล้ว ทั้งสองผู้สมัครมี absorption ที่ reactive zero จึงไม่ใช้ static susceptibility/stiffness ratio เป็น sound prediction หรือเรียกส่วน real เป็นศูนย์ว่า undamped pole งานต่อคือ controlled complex-pole และ validity-domain analysis จาก kernel ที่คำนวณนี้ แล้วปิด approximation/regulator/action และ joint-Phi/material/heat-current งานพอร์ตใช้ผล methods ที่ตรวจได้ แต่ R1–R5, G1/G2, Full Topic13 และวันเดิมยังไม่เปลี่ยน

ผลถัดมา 1 ต.ค.: [actual Hartree external field response](Result/artifacts/T13_HARTREE_EXTERNAL_RESPONSE_2026-10-01.md) คำนวณ vacuum/thermal bubble สามช่องและ source-responsive covariance ที่ q/frequency ไม่เป็นศูนย์แล้ว คืน static potential/Ward โดยไม่แก้ internal mass และตรงกับ direct subtraction/4D vacuum reference งานต่อจึงไม่ต้องสร้าง field bubble เดิมซ้ำ แต่ต้อง derive gauge-current contacts, real-axis/error และ regulator/RG/joint-Phi/material match ผลนี้ปิดเฉพาะ named candidate prescription; R1–R5, physical G1/G2 และวัน D5/D10/D14 ยังไม่รับงานจาก field response อย่างเดียว

ผลถัดมา 1 ต.ค.: [finite Hartree background](Result/artifacts/T13_RENORMALIZED_HARTREE_BACKGROUND_2026-10-01.md) พบ stationary candidate ที่ fixed Phi โดยรวม vacuum/thermal ใน potential เดียว และ [counterterm/potential matching](Result/artifacts/T13_HARTREE_COUNTERTERM_MATCHING_2026-10-01.md) ปิด homogeneous invariant-channel cancellation กับ potential บน gap equations ที่ต่างเพียง normalization คงที่ใน lane นี้แล้ว ไม่ต้องเดา stationary shift หรือใช้ countercoupling เดียวต่อ งานถัดไปคือ regulator/RG input และ actual external finite-q/frequency vertices รวม joint Phi/material mapping; conditional vertex algebra ไม่ใช่ physical response และ normalization ที่ขึ้นกับ m(Phi) ห้ามทิ้งเมื่อขยาย joint Phi ค่า trial renormalized inputs ยังไม่ใช่ original calibration ที่รับวัสดุแล้ว G1/G2 และวัน D5/D10/D14 ไม่เปลี่ยน

ผลล่าสุดถัดมา 1 ต.ค.: [conditional dynamic composite/current](Result/artifacts/T13_POLAR_DYNAMIC_COMPOSITE_2026-10-01.md) ปิด leading phase-lane spectrum, time kernel และ current-contact identity พร้อมคืน static IR coefficient เดิมแล้ว แต่ยังไม่เป็น physical response หรือ microscopic equilibrium ต้องใช้ผลนี้ออกแบบ frequency/source protocol โดยไม่ fit relaxation pole เดียว และทำ renormalized background/full-action remainder ต่อ G1/G2 และวัน D5/D10/D14 ไม่เปลี่ยน

ผลล่าสุด 1 ต.ค.: [polar static observable/source matching](Result/artifacts/T13_POLAR_STATIC_IR_OBSERVABLE_2026-10-01.md) ปิดพิกัด/source/measure และ static IR coefficient แบบมีเงื่อนไข แต่ Gaussian stationarity obstruction ยังอยู่เมื่อคืน source ให้ครบ งานวิจัยหลักต้องแยกผลนี้จาก microscopic resummation, independent predictive content และการทำนายวัสดุ G1/G2 ยังไม่เปิดจากการเพิ่ม artifact นี้

หลักฐานต่อเนื่อง 1 ต.ค.: [finite-momentum thermal 1PI](Result/artifacts/T13_FINITE_MOMENTUM_THERMAL_1PI_2026-10-01.md) ปิด kernel แบบ fixed-Phi thermal one-loop และตรวจ static current เพิ่มจาก zero-momentum result แต่ bare radial expansion ไม่ uniform เมื่อ q ต่ำ จึงยังไม่ผ่าน physical G1/G2 หรือผลหลักของพอร์ต ต้องตัดสิน D5 จาก scope ที่ตรวจจริงและ obligations เรื่อง IR/current/material/measurement ที่ยังเหลือ ไม่เรียก divergence นี้ว่า no-go ของ UET ทุก completion

ชื่อผลงานเสนอ: **ขอบเขตการทำนายและการออกแบบการวัดเพื่อทดสอบสะพานความร้อนที่ปรับเทียบแล้ว: กรณี He-4/O(2)**

คำถามหลัก: เมื่อแช่แข็ง calibration, สเกล และสมการที่มีอยู่ แบบจำลองกำหนดการตอบสนองความร้อนที่ยังไม่ได้ใช้ปรับเทียบได้เป็นเอกลักษณ์หรือไม่? หากยังไม่ได้ ต้องเพิ่มการวัดชนิดใดจึงระบุพารามิเตอร์หรือแยกแบบจำลองคู่แข่งได้?

ผลหลักที่ตั้งเป้า: `T13_HE4_PREDICTIVE_CONTENT_AND_MEASUREMENT_DESIGN` เป็น ID ของงานที่วางแผน ยังไม่เพิ่มเป็นผลสำเร็จใน Core registry เป้าหมายคือคำตอบเชิงวิจัยพร้อมหลักฐานตรวจซ้ำได้หนึ่งชุด ภายใน D10 แล้วจัดพอร์ตเสร็จ D14

ผลที่นับว่าปิดคำถามนี้ได้มีสองทาง:

1. `PREDICTIVE_CONTENT_ESTABLISHED`: มี observable operator และ protocol ตรงกัน ทุกพารามิเตอร์ที่กระทบผลถูกกำหนดจากหลักฐานอื่นก่อนเทียบเป้าหมาย มีการคำนวณอิสระและ uncertainty ที่เหมาะสม ผลเทียบต้องรายงานได้ทั้งสอดคล้องและไม่สอดคล้องกับข้อมูล การไม่สอดคล้องไม่ใช่เหตุให้ย้อนปรับ calibration
2. `SCOPED_NONIDENTIFIABILITY_ESTABLISHED`: พิสูจน์ภายใต้สมมติฐานที่ประกาศว่า calibration ปัจจุบันยอมให้การตอบสนองต่างกันได้ พร้อมตระกูลตัวอย่าง/การพิสูจน์ที่ผ่าน conservation, stability และเงื่อนไขที่ใช้จริง แล้วออกแบบการวัดที่แก้ degeneracy นั้นได้

การหา source ไม่พบ การรันไม่ผ่าน หรือการเขียน blocker เพิ่ม ให้สถานะ `UNRESOLVED` และยังไม่นับว่าปิดผลหลัก พอร์ตอาจจัดเอกสารเสร็จได้ในกรณีนั้น แต่ต้องระบุว่าเป้าหมายวิจัยยังไม่สำเร็จ

## 2. หลักฐานตั้งต้นและสิ่งที่ต้องแก้ความเข้าใจ

ตรวจ checkout `codex/research/core-physical-migration` ที่ HEAD `a62efba425f1b219241cf149bc4bab50cce4c379` พร้อมไฟล์ที่ยังไม่ commit; hash หลักฐานอยู่ใน JSON แผน ต้องตรึงทั้ง commit และไฟล์ที่ต่างจาก commit ใน D1

| สิ่งที่มีแล้ว | สิ่งที่ใช้ต่อได้ | ขอบเขต/ผลต่อแผน |
| --- | --- | --- |
| [He-4 composition](../../core/07_artifacts/topic13/t13_he4_core_thermodynamic_bridge_composition_audit.json) บันทึก `CLOSED_FOR_CORE` | bounded interface ที่มี external inputs | ยังไม่เป็น independent action-to-material validation |
| [Matching independence](../../core/07_artifacts/topic13/t13_he4_matching_independence_audit.json) | พิสูจน์ว่า alpha ที่ match กลับเป็นค่าเดิมตามนิยาม | ห้ามนับการคืนค่า calibration เป็นผลใหม่; ต้องขยายถึง response/protocol และการวัด |
| [SI normalization](../../core/07_artifacts/topic13/t13_si_phi_normalization_jacobian_audit.json) | chain rule และพิกัดของอนุพันธ์ชัดขึ้น | generic base-Phi map ยังเปิด; ห้ามนำ scale ระหว่าง lane มาใช้เงียบ ๆ |
| [Normalized dip time](Result/artifacts/t13_normalized_dip_time_identifiability.json) | alpha คงที่ตัดออกจาก normalized trace; initial rate เปลี่ยน dip time | งาน shape ยังต้องมี initialization, dimensional dynamics และ detector map |
| [NIMS diagnostic](../../core/07_artifacts/topic13/t13_nims_mp990448_aa_stack_shear_instability.json) | จบคำถาม source route MP-990448 แบบจำกัดโครงสร้าง | ใช้เป็นภาคผนวก; ไม่เปิดรอบซ่อม NIMS ใหม่ในเส้นวิกฤตนี้ |
| [Source priority](../../core/07_artifacts/topic13/t13_csrc_source_route_priority_audit.json) | มีการคัดเส้นทางข้อมูลแล้ว | ไม่มี Ding-compatible route ที่ผ่าน acceptance; จึงไม่วางเส้นตายหลักบนการรอ Ding |
| [Core handoff](Result/artifacts/core_handoff_revalidation.json) | บันทึก revalidation เป็น `BLOCKED_HANDOFF_REVALIDATION` | ผลวันที่ 24 ก.ย. ระบุ provenance drift; ไม่อ้างว่าทั้ง Core ผ่านใหม่ |
| [Holdout incident](../../core/08_history/update_logs/T13_HOLDOUT_EXPOSURE_REVIEW_REQUIRED_2026-09-24.md) | มีการบันทึก article/context exposure | Xie อยู่ `REVIEW_REQUIRED`; งดใช้และงดอ้าง pristine blinding |
| [Thermal-pole design control](Result/artifacts/T13_THERMAL_POLE_MEASUREMENT_DESIGN_CONTROL_2026-09-27.md) | ตัวเทียบ Cattaneo แสดงว่าความถี่อย่างเดียวแยก transport pair ไม่ได้ แต่อัตราลดทอนช่วยแยก | เป็นเพียง standard comparator ไม่ใช่ UET second sound หรือข้อมูล He-II |
| [Frozen-state branch boundary](Result/artifacts/T13_HE4_FROZEN_BRANCH_COMPATIBILITY_2026-09-27.md) | สถานะ natural bridge เดิมเป็น normal O(2), ไม่ใช่ condensed He-II background | ก่อนคำนวณ second sound ต้องมี condensed state และ transfer map ที่เลือกอย่างอิสระ; ห้ามย้าย calibration เดิมข้าม branch |
| [Condensed-state selection boundary](Result/artifacts/T13_HE4_CONDENSED_STATE_SELECTION_BOUNDARY_2026-09-27.md) | ผู้สมัคร condensed สองจุดที่ผ่านเกณฑ์ภายในให้ response ต่างกัน แต่ข้อมูล density/fraction/e0/gain ปัจจุบันยังไม่เลือกจุดใด | ต้อง derive หรือ calibrate แมป absolute charge/phase-stiffness สู่ density ของ He-II อย่างอิสระ; candidate ไม่ใช่ physical fit |
| [Conditional charge-map circularity](Result/artifacts/T13_HE4_CONDITIONAL_CHARGE_MAP_CIRCULARITY_2026-09-27.md) | หากสมมติแมป pressure/mu/charge แบบง่าย การ match density จะวน เพราะ density ค่าเดียวกันถูกใช้สร้าง `e0` | ต้องมี observable อิสระที่ไม่ได้ใช้ calibration และหลักฐานยอมรับ charge identity; ค่า `mu` ที่ได้แบบมีเงื่อนไขไม่ใช่ผลทำนาย |

มีงาน J02 ที่ commit `c42385d07e390b338096122275fe809737b8477a` ใน branch `codex/research/fluid-thermal-joint-plan` แล้ว: `HE4_SECOND_SOUND_PROTOCOL_CARD.md`, source package และ protocol audit ระบุ `PASS_SOURCE_PROTOCOL_CANDIDATE_ONLY` โดยยังขาด UET two-fluid operator และ primary frequency/uncertainty match ต้องนำเฉพาะแพ็กที่เกี่ยวข้องมาทบทวนใน D1; การอ่านจากอีก worktree ไม่เท่ากับ merge แล้ว

ตรวจจริงในรอบวางแผน: `py -m pytest -q docs/core/05_tests/regression/root/test_topic13_he4_matching_independence.py docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_normalized_dip_time_identifiability.py` ได้ **5 passed** เฉพาะสองขอบเขตนี้ พบว่า Python 3.14 ผ่าน `py` มี numpy/scipy/pytest แต่ไม่มี phonopy; งานหลักที่เลือกไม่ต้องใช้ phonopy

## 3. ทำไมเลือกผลนี้ก่อน

| ตัวเลือก | งานที่ต้องเพิ่มก่อนเกิดผล | คำตัดสินสำหรับ 14 วัน |
| --- | --- | --- |
| He-4 predictive-content และ measurement design | ตรวจ protocol, พิสูจน์ identifiability, คำนวณ sensitivity และออกแบบการวัด | **งานหลัก**: ใช้ข้อมูล/สมการที่มีอยู่ และมีทางตัดสินเชิงโครงสร้าง |
| Graphite TTG validation | authorized rows, uncertainty, material map, independent Phi scale | สายข้อมูลสำรอง มีเวลาเพดาน; ไม่เป็นเงื่อนไขจบพอร์ต |
| Curved 3+1/Gravity | boundaries, conserved matter, provenance และ observable acceptance | เป็นงานระยะถัดไป; ไม่ตั้งสัญญาว่าปิดภายในสองสัปดาห์ |
| Topic 10 benchmark/chaos | มีประโยชน์เป็นวิธีตรวจ | ให้บริการเฉพาะ numerical controls ที่งานหลักต้องใช้ |
| NIMS source result อย่างเดียว | มีผลเชิง comparator แล้ว | เป็นหลักฐานความสามารถเสริม; ความใหม่ของงานนี้ต้องประเมินเพิ่ม |

การประเมินความเป็นไปได้นี้เป็นข้อเสนอการจัดงาน ไม่ใช่ความน่าจะเป็นเชิงสถิติหรือการรับประกันได้ทุน ผลลบที่พิสูจน์ได้มีคุณค่าเมื่อเพิ่มข้อสรุปจากเดิมอย่างชัดเจน; การทวน matching identity ที่มีอยู่แล้วอย่างเดียวไม่ถึงเกณฑ์ผลงานหลัก

## 4. สมมติฐานและแผนพิสูจน์

### Q1: Calibration กำหนดอะไรจริง

ใช้สัญลักษณ์ calibration เดิม:

```text
T_K = theta_T T_nat
Delta_Phi_norm = Z_Phi Delta_Phi_nat
Z_Phi = theta_T alpha_nat / alpha_external
alpha_reconstructed = theta_T alpha_nat / Z_Phi = alpha_external
```

แช่แข็งค่า theta_T, Z_Phi, e0, alpha และ external shear eta ด้วย hash ของ record; บันทึก units, uncertainty class และ covariance ที่ยังไม่ทราบ แยก calibration-independent-from-Xie ออกจาก independent physical prediction ตรวจอนุพันธ์ตาม SVP กับ fixed-(T,mu) และ normal component กับ whole He-II เป็นคนละเงื่อนไข

ทำ parameter-to-observable map ของสมการที่มีจริง รวมแหล่งกระตุ้น initial state detector และ boundary กำหนด null hypothesis ว่า calibrated interface ยังไม่กำหนด dynamic response เป้าหมาย โดยให้โอกาสหักล้างด้วย derivation ที่ไม่ใช้ target

### Q2: มี observable ทดสอบอิสระได้หรือยัง

ใช้ second-sound protocol J02 เป็นคำถามทดสอบลำดับแรก แต่ต้องผ่าน **branch/state admission ก่อน**: จุด natural bridge ที่ตรึงไว้เป็น normal O(2) (`q=-0.8715`) ส่วน He-II anchor มี superfluid fraction ไม่เป็นศูนย์ ต้องมีแมป absolute ระหว่าง O(2) charge หรือ phase stiffness กับจำนวนอะตอมหรือ superfluid density ของ He-II ที่ derive/calibrate โดยไม่ใช้ target จึงจะเลือก condensed background และแมปสภาวะ/หน่วยได้ ไม่เลือก `mu` หรือ `Phi` จากความเร็วเสียงเป้าหมาย หลังจากนั้นจึงตรวจ state vector, mass/entropy balance, relative motion, energy และ source coupling ก่อนเขียน eigenmode solver เปรียบเทียบกับ standard two-fluid comparator ที่ state/units ตรงกัน

**ห้ามนับข้อมูลซ้ำ:** `e0=n_He4 k_B T0` ใช้ความหนาแน่นที่ 1.7 K ไปแล้ว ดังนั้นหากสมมติ `n_He4=(e0/(k_B theta_T))n_O2` และเลือก `mu` จากความหนาแน่นแถวเดียวกัน การ match แถวนั้นเป็น identity ไม่ใช่ validation ต้องกันข้อมูลหรือการวัดอีกชนิดหนึ่งที่ไม่ถูกใช้เลือกสเกล/พารามิเตอร์ไว้เป็น comparison จริง

หากยังไม่มี independent condensed-state transfer **หรือ** admitted dynamic operator ให้บันทึกช่องว่างนั้นและไปเส้นทาง structural identifiability ภายใน D5 การเติม tau, conductivity หรือ velocity state เพื่อให้ได้กราฟ ต้องถูกระบุเป็นสมมติฐานใหม่ พร้อม F0–F8 ก่อนตีความทางฟิสิกส์ ใน sprint นี้ไม่ตั้งเป้าสร้าง complete two-fluid theory ใหม่

Fourier/Cattaneo เป็น analytic numerical controls; normal shear viscosity เพียงตัวเดียวไม่ใช้แทน heat transport หรือ attenuation ทั้งระบบ Second-sound source เคยถูกดูขณะออกแบบ protocol แล้ว จึงเป็น source-backed comparison candidate ไม่ใช่ blind holdout

### Q3: ถ้ายังระบุผลไม่ได้ ต้องพิสูจน์ให้ถึงไหน

สร้าง map `g(p)` ของ calibration และ `h(p; protocol)` ของ dynamic observable จาก model class ที่ประกาศ จากนั้นหา `p_a != p_b` ซึ่ง `g(p_a)=g(p_b)` แต่ `h(p_a)!=h(p_b)` ทั้งสองต้องผ่านเงื่อนไขของ class จริง ไม่ใช่แค่เลือกพารามิเตอร์ arbitrary ที่ผิด conservation หรือ stability

แยกการเปลี่ยนพิกัด Phi ซึ่งไม่เปลี่ยน observable ออกจากความไม่แน่นอนเชิงกายภาพ ตัด coordinate/gauge redundancy ก่อนใช้ rank เป็นข้อสรุป ถ้า operator ยังนิยามไม่ได้ ผลที่พิสูจน์ได้อาจเป็น operator-completion boundary; ห้ามรายงานความเร็วที่แต่งขึ้นเป็น UET prediction

ใช้ analytic symmetry/nullspace หรือ constructive proof เป็นแกน เสริมด้วย Jacobian/sensitivity และ independent implementation ผล rank ต่ำ ณ จุดเดียวให้ได้เพียง local statement; ห้ามขยายเป็น global no-go จาก SVD หรือ finite sweep

### Q4: ต้องวัดเพิ่มอะไรจึงตอบได้

ทำตาราง observable ที่ยังไม่ได้ใช้ matching เช่น phase velocity หลาย state, attenuation หลาย frequency, amplitude/phase ของ driven response หรือ response ต่อ perturbation อีกชนิดหนึ่ง แต่ละรายการต้องระบุ unknown combination, units, protocol, sensitivity และ nuisance parameters

คำว่า “ชุดวัดขั้นต่ำ” ใช้ได้เมื่อพิสูจน์ทั้ง lower bound และ sufficiency ภายใน model class หลังตัด redundancy หากทำได้เพียงเพิ่ม rank ให้เรียกว่า “ชุดวัดที่เพียงพอแบบ local/conditional” การมีข้อมูลเพิ่มหลายแถวจาก compilation เดียวไม่ทำให้เป็น independent measurements โดยอัตโนมัติ

## 5. เกณฑ์ปิดที่ตรวจได้

| Gate | สิ่งที่ต้องส่งและเกณฑ์ | ผลเมื่อไม่ผ่าน |
| --- | --- | --- |
| G0 baseline | snapshot แหล่งข้อมูล/สมการ/เวอร์ชัน/dirty diff, hashes, rerun logs และ lineage ของ J02 | แยกผลเก่าที่ยังตรวจซ้ำไม่ได้ออกจากหลักฐานพอร์ต |
| G1 protocol | variables held fixed, material state, excitation, observable, units และ parameter origin ครบ; freeze ก่อนคำนวณเทียบ | เปิด structural route; ไม่สร้าง physical score |
| G2 science | พิสูจน์ PREDICTIVE_CONTENT หรือ SCOPED_NONIDENTIFIABILITY ตามข้อ 1 พร้อม assumption table และ evidence beyond existing matching identity | UNRESOLVED; เป้าหมายวิจัยยังไม่จบ |
| G3 verification | analytic limit, independent solver/derivation, sensitivity/rank robustness, conservation/energy ที่เกี่ยวข้อง และ uncertainty semantics ถูกต้อง | ซ่อมเฉพาะ failure ที่เปลี่ยนข้อสรุป |
| G4 measurement design | observable ที่เพิ่มข้อมูลจริง + sensitivity + nuisance/covariance treatment + state/frequency/precision requirement | ระบุว่างานออกแบบการวัดยังค้าง |
| G5 portfolio | report, evidence manifest, reproducibility instructions, figures, claim map, proposal/budget rationale และ review record | ส่ง draft พร้อมรายการค้าง; ไม่เรียก submission-ready |

เกณฑ์ตัวเลขต่อไปนี้เป็น **ข้อเสนอสำหรับ diagnostic ใหม่** ต้อง preregister D2 และติด provenance; ถ้าของเดิมเข้มกว่าหรือใช้ scale ต่างกันให้ใช้เกณฑ์เดิม ไม่เปลี่ยนเกณฑ์เดิมเพื่อให้ผ่าน:

- Algebraic matching/chain-rule witness: normalized residual <= 1e-10 โดยนิยาม denominator และ near-zero handling ล่วงหน้า
- Jacobian: central differences ที่ relative steps 1e-4, 1e-5, 1e-6 เทียบ analytic/independent derivative; scaled norm difference <= 1e-5 ใน valid domain ถ้า singular ให้แสดง singular case โดยตรง
- Rank: nondimensionalize ก่อน; รายงาน spectrum และทดสอบ relative SVD cutoffs 1e-6, 1e-8, 1e-10 หาก rank เปลี่ยนให้เป็น unresolved numerical rank และใช้ analytic argument ตัดสิน
- Dynamic diagnostic ถ้าจำเป็น: dt, dt/2, dt/4; ใช้ dx, dx/2, dx/4 เฉพาะ PDE; finest observable difference <= 1% และ numerical error <= 10% ของ physical uncertainty/discrimination margin ที่มีเหตุผล หาก uncertainty ไม่มี ห้ามผ่าน empirical score
- หากใช้ causal branch ต้องรักษา threshold leakage <= 1e-6 และ arrival/ledger/no-clipping/no-padding เดิม ตรวจ PDE principal structure แยกจาก finite-grid leakage; ไม่อ้าง continuum causality จากกริดอย่างเดียว
- ไม่มี pointwise uncertainties/covariance ให้ใช้ source-described bounds หรือ sensitivity envelope; ห้ามแปลง range เป็น Gaussian sigma สุ่มเอง ผล residual ที่ไม่มี uncertainty แสดงได้แต่ยังไม่ใช่ acceptance score
- Empirical threshold และหลักตัดสิน superiority ต่อ baseline ให้กำหนดจาก measurement/error model ก่อน comparison การเห็นค่าตารางแล้วต้องเปิดเผยว่าเป็น preregistered analysis of already-seen data, ไม่ใช่ blind prediction

## 6. ไทม์ไลน์และสิ่งที่ต้องจบรายวัน

กำหนดใช้ 14 วันปฏิทิน เริ่ม 28 ก.ย. หากเริ่มช้ากว่านี้ให้บันทึกผลต่อกำหนดส่ง ไม่เลื่อนเงียบ ๆ ประมาณ effort 50–70 ชั่วโมงงานเข้มข้นรวมวิจัย/ตรวจ/เขียน เป็นสมมติฐานวางแผน ไม่รวมเวลารอแล็บหรือ reviewer

| วัน / วันที่ | งานหลัก | ผลส่งมอบและเงื่อนไขจบ |
| --- | --- | --- |
| D1 / 28 ก.ย. | ตรึง baseline และรับ J02 จาก commit ที่ระบุ; ตรวจ runtime/links/hashes | BASELINE_MANIFEST.json + test log; แยก recorded status กับ reverified evidence |
| D2 / 29 ก.ย. | ล็อก model class, parameter provenance, data roles และ acceptance | PREREGISTRATION.md + parameter_origin.json + data_access_policy.json; G1 ระบุชัด |
| D3 / 30 ก.ย. | ตรวจ primary source/protocol และ perturbation correspondence | SOURCE_PROTOCOL_DECISION.md; จบ source search ที่ยังไม่พบคำตอบตามเพดาน |
| D4 / 1 ต.ค. | สร้าง observable map และ identifiable combinations | DERIVATION.md ฉบับแรก + sensitivity/nullspace witness |
| D5 / 2 ต.ค. | ตัดสินเส้นทางหลักจากหลักฐาน | SCIENCE_ROUTE_DECISION.json: predictive / structural / unresolved พร้อมเหตุผล; หยุดขยาย operator ที่ยังเปิด |
| D6 / 3 ต.ค. | ทำ derivation/constructive family ให้ครบ | assumption table + counterexample family หรือ fully specified prediction operator |
| D7 / 4 ต.ค. | ตรวจสมการด้วย implementation อิสระและ control | verification.json + analytic/solver comparison; ไม่มี physical claim จาก synthetic witness |
| D8 / 5 ต.ค. | ประเมิน robustness, uncertainty และคู่แข่ง | uncertainty_budget.json + competitor comparison หรือ bounded nonidentifiability result |
| D9 / 6 ต.ค. | ออกแบบการวัดเพิ่มและทดสอบ rank gain | MEASUREMENT_DESIGN.md + precision/frequency/state requirements และข้อจำกัด minimality |
| D10 / 7 ต.ค. | ล็อกข้อสรุปหลัก ตรวจ G2–G4 | SCIENTIFIC_DECISION.json + figures; ผ่าน/หักล้าง/ไม่ระบุได้/ยังไม่จบแยกชัด |
| D11 / 8 ต.ค. | เขียน technical report และที่มาความใหม่ | REPORT.md ราว 8–12 หน้าเมื่อจัดหน้า + claim/evidence table |
| D12 / 9 ต.ค. | clean rerun และ review แบบอิสระจาก derivation แรก | REPRODUCIBILITY.md + rerun log + REVIEW.md; internal replication ไม่อ้าง external validation |
| D13 / 10 ต.ค. | เตรียมเรื่องเล่าขอทุน สไลด์และงบตามช่องว่าง | EXECUTIVE_BRIEF.md 2 หน้า, PITCH.md 6–8 สไลด์, BUDGET_SCOPE.md, CALL_FIT.md |
| D14 / 11 ต.ค. | ตรวจรับพอร์ตและ scoped Git release handoff | PORTFOLIO_INDEX.md + EVIDENCE_MANIFEST.json + decision summary; human author review ค้างต้องมองเห็น |

เส้นวิกฤต: G0 -> G1 -> G2 -> G3 -> G4 -> G5 สายค้นเอกสารกับสายสมการทำคู่ขนานได้; ห้ามให้หลายห้องเขียน Core registry เดียวกันพร้อมกัน

## 7. ขอบเขตงานและการแบ่งเจ้าของ

| เจ้าของเชิงหน้าที่ | รับผิดชอบ | เวลา/เงื่อนไข |
| --- | --- | --- |
| Topic 13 research lead | derivation, response protocol, identifiability และข้อสรุปหลัก | งานหลัก D1–D10 |
| Source/provenance pass | primary measurement, permissions, uncertainty, overlap และ holdout incident | ไม่เกิน 6 ชั่วโมงงานค้นเข้มข้นถึง D3; source ไม่ครบให้ปิด inventory |
| Topic 10 method support | independent solver, rank/norm controls, convergence เฉพาะโจทย์นี้ | ไม่เปิด turbulence/chaos research wave ใหม่ |
| Core integration owner | ontology/units/F0–F8 review ของ equation ที่ใช้ และรับผลหลังผ่าน | ไม่ไล่ปิด whole Core, curved 3+1 หรือ Gravity เพื่อทำพอร์ตนี้ |
| Author/PI | วิจารณ์ความใหม่ เลือกทุน ทบทวนข้ออ้างและอนุมัติเผยแพร่ | นัด D5/D10/D13 หากไม่มี reviewer ให้ระบุช่องว่าง |

เป็นบทบาทในแผน ไม่ได้สร้างห้อง ส่งข้อความ หรือยืนยันว่ามีบุคคล/แล็บรับงานแล้ว จำกัดงานวิจัยหลักครั้งละหนึ่งคำถามและหนึ่ง independent verification path

## 8. เงื่อนไขหยุดวนและทางสำรอง

- D3: ถ้า source ใหม่ยังขาด primary protocol หรือ uncertainty ยุติการค้นแบบกว้าง บันทึกสิ่งที่ต้องขอจากผู้ทดลอง แล้วเดิน structural route ต่อ ส่งอีเมลขอข้อมูลได้เมื่อผู้ใช้อนุญาตการติดต่อจริงเท่านั้น
- D5: หาก second-sound operator ต้องเพิ่ม state/constitutive law ที่ไม่ระบุได้ ให้หยุดสัญญาว่าจะทำนายความเร็วภายใน sprint แล้วพิสูจน์ข้อจำกัดของ class ปัจจุบันอย่างชัดเจน
- หากซ่อมตัวควบคุมเดิมสองรอบโดยไม่มี source/derivation/input ใหม่ ให้ทำ decision record ว่าความพยายามต่อไปเปลี่ยนข้อสรุปอย่างไร ห้ามนับ rerun เดิมเป็นความคืบหน้า
- D10: หยุดเพิ่มขอบเขตวิจัย ใช้เวลาที่เหลือกับความถูกต้องและการส่งมอบ หาก G2 ไม่ผ่าน ให้ scientific goal คง unresolved แม้เอกสารครบ
- ไม่เอา graphite data มายืนยัน He-4 mapping, ไม่ใช้ source uncertainty ของคนละสภาวะร่วมกัน, ไม่เติม model discrepancy term แล้วเรียก uncertainty จากแหล่งข้อมูล
- ไม่ใช้ Xie 2026 ใน sprint นี้ รวมถึงค้น/เปิดบทความเพื่อเลือกตัวแบบ เหตุ exposure ที่มีอยู่ต้องอยู่ในแผนการ validation ภายหลัง
- ถ้า core revalidation กว้างยังไม่ผ่าน ให้แนบ scoped evidence ที่ตรวจใหม่เอง; ไม่เลื่อนระดับ whole Core เพื่อให้พอร์ตดูพร้อม

## 9. พอร์ตต้องทำให้ผู้ประเมินเห็นอะไร

โฟลเดอร์ส่งมอบที่วางแผน: `Result/funding_portfolio_2026-10-11/` ยังไม่สร้างผลวิจัยในโฟลเดอร์นี้จากการวางแผน

| ชิ้นงาน | เนื้อหาต้องมี | เหตุผลสำหรับขอทุน |
| --- | --- | --- |
| Technical report | คำถามเดียว, related work/ความใหม่, สมมติฐาน, derivation, methods, result, limitations | แสดงว่าตอบโจทย์หนึ่งเรื่องจนจบได้ |
| Evidence/reproducibility bundle | source IDs/rights/hashes, pinned environment, commands, synthetic-vs-measured labels, clean rerun | ให้ผู้ประเมินตรวจความน่าเชื่อถือ |
| Figures 3–4 ภาพ | correspondence diagram; response/counterexample; sensitivity/rank; uncertainty/measurement design | ทุกภาพระบุว่า measured, derived หรือ simulation |
| Claim map | แต่ละข้ออ้างเชื่อมสมการ/source/result และ allowed wording | แสดงขอบเขตของหลักฐาน |
| Proposal 2 หน้า | ปัญหา, preliminary result, งานที่จะซื้อด้วยทุน, deliverables, risk/fallback | ผูกเงินกับสิ่งที่ยังวัด/ตรวจไม่ได้ |
| Budget scope | compute, cryogenic facility access ถ้าจำเป็น, sensor/lock-in/resonance measurements, data stewardship, researcher/reviewer time | ใส่จำนวน/อัตราจาก quotation หรือ call; ไม่แต่งราคาขึ้น |
| Call-fit checklist | หน่วยงาน สังกัด PI/ผู้ร่วม คุณสมบัติ deadline เอกสาร งบ/overhead และ IP/data terms | ยังเป็น OPEN จนเลือกทุน; generic portfolio ไม่เท่ากับใบสมัครพร้อมยื่น |

การทบทวนความใหม่ต้องแยก “สิ่งที่ฟิสิกส์มาตรฐานรู้อยู่แล้ว” จาก “สิ่งที่ตรวจเพิ่มเฉพาะ UET” ประเมิน contribution อย่างน้อยสามด้าน: ข้อจำกัดเชิงสมการที่พิสูจน์ใหม่, ชุดคำนวณ/หลักฐานที่ตรวจซ้ำได้, การวัดที่เพิ่มข้อมูลจริง หากไม่มีความใหม่ทางทฤษฎี ให้เสนอเป็น feasibility/methodology pilot ตามหลักฐาน

แผนทุนต่อยอดหลัง D14 เป็นร่าง milestone: เดือน 1 ล็อก partner/protocol/precision; เดือน 2–3 รับข้อมูลหรือทำการวัดตาม state ที่ระบุ; เดือน 4 วิเคราะห์ตาม protocol ที่ตรึงไว้และทดสอบกับ comparator งบและระยะเวลาจริงขึ้นกับ call/แล็บ ยังไม่ถือว่าจัดหาได้แล้ว

## 10. การรันใน Goal mode และการรายงาน

ไฟล์ JSON นี้เป็น planning contract แยกจาก scientific acceptance gate ไม่แก้ค่า `CLOSED_FOR_CORE` หรือ dependency เดิมเมื่อเพียงทำงานในแผนครบ

ทุกช่วงเริ่มจากอ่าน current goal state + baseline manifest + milestone ล่าสุด ดำเนินงานต่อทันทีเมื่อ prerequisites พร้อม ไม่ต้องรอให้วันปฏิทินนั้นมาถึง วันในแผนเป็น deadline ไม่ใช่คำสั่ง sleep ห้ามสร้าง automation เอง

แต่ละรอบส่งกลับหัวข้อ:

```text
MAJOR_RESULT_CLOSURE:
WHAT_IS_ACTUALLY_CLOSED:
WHAT_REMAINS_OPEN:
DEPENDENCY_UNLOCKED:
STATUS:
WHAT_CHANGED:
EQUATION_OR_MAPPING:
VERIFICATION:
CONTROLLING_BLOCKER:
NEXT_ACTION:
CLAIM_BOUNDARY:
```

ต้องอธิบายเป็นภาษาคนก่อนว่าคำถามใดตอบได้เพิ่ม แล้วอ้าง artifact/hash ไม่ใช้จำนวน PASS เป็นผลหลัก Goal completion ต้อง G2–G5 ครบและแสดง scientific disposition จริง ถ้าถึงเส้นตายแล้วยัง unresolved ให้ส่ง dossier และระบุเป้าหมายที่ค้าง; ไม่ mark complete เพราะใช้เวลา/งบหมด

งานภายใน repo ที่เป็น scoped reversible research ให้ทำต่อได้ตามแผน การซื้อ/จ่ายเงิน ติดต่อผู้ทดลอง ส่งใบสมัคร และเผยแพร่ข้ออ้างในนามผู้ยื่นเป็น action แยกที่ต้องมี authorization ตามจริง งานเอกสารและชุดหลักฐานต้องเตรียมให้ review ได้ก่อนถึงขั้นนั้น

Git: เก็บของเดิมใน dirty worktree; D1 สร้าง frozen input manifest ก่อนแยก execution checkout ใช้ short-lived scoped branch และ commit งานที่ตรวจแล้วทีละส่วน ห้ามรวม ledger หรือ Core migration ที่คนอื่นกำลังทำใน commit นี้ การตรวจทั้งหมดควรจบใน clean reproduction checkout ก่อน final release; ไม่ใช้ working directory dirty เป็นหลักฐานว่าบุคคลอื่น rerun ได้แล้ว

การตรวจเผยแพร่ 27 ก.ย.: ผลย่อยก่อน sprint ทั้งสี่ถูก regenerate บน branch แยกจาก `origin/main` แล้ว โดยข้อสรุปและสถานะทางวิทยาศาสตร์ไม่เปลี่ยน; hash ของไฟล์อ้างอิงบางชิ้นเปลี่ยนเพราะฐาน Core ต่างจาก dirty worktree เดิม จึงเก็บ hash ชุดเดิมใน `baseline` เป็นประวัติเท่านั้น และใช้ `pre_sprint_evidence` เป็น hash ของผลที่ตรวจซ้ำใน checkout นี้ มี test ตรวจทั้ง JSON ที่บันทึกและ hash ของ input จริง การตรวจนี้ยัง **ไม่** revalidate Core baseline ทั้งชุด ไม่ปิด G0 และไม่ปลดล็อก Full Topic 13

ผลย่อยที่ห้าเป็น [conditional compressibility design](Result/artifacts/T13_HE4_CONDITIONAL_COMPRESSIBILITY_DESIGN_2026-09-27.md): density ที่ใช้สร้าง `e0` ไม่ใช่ test ซ้ำอีกครั้ง; อนุพันธ์ isothermal ที่ตรึง `Phi` เป็น candidate observable คนละตัว แต่จะใช้เทียบข้อมูล He-II ได้ต่อเมื่อมี physical charge map, `E_mu` และโปรโตคอลตรึง `Phi` หรือกฎตอบสนองเมื่อ `Phi` ผ่อนคลาย ถ้าใช้ response นี้เลือก `Phi` ต้องเก็บ observable ที่สามไว้ทดสอบจริง ไม่ยกระดับ G0-G5 จากผลนี้

[Source-route screen สำหรับ compressibility](Result/artifacts/T13_HE4_COMPRESSIBILITY_SOURCE_ROUTE_2026-09-27.md) ยังเป็น `PARTIAL` แยกจากผลย่อยที่ปิดได้ห้าชิ้น: แหล่ง SVP เดิมไม่มี row นี้ในแพ็กเกจ, Brooks-Donnelly เป็น EOS-derived comparator, และ Elwell-Meyer เป็น primary pressure-volume route ที่ยังต้องได้ absolute baseline/การย้าย state/uncertainty ก่อนรับ numeric row ห้ามใช้ first-sound, density ตามเส้น SVP หรือค่าการเปลี่ยนของ compressibility แทน absolute isothermal row โดยอัตโนมัติ

[G0 clean-baseline lineage screen](Result/artifacts/T13_FUNDING_BASELINE_LINEAGE_SCREEN_2026-09-27.md) รุ่นแรกระบุว่า 5 ผลย่อยใหม่ hash ตรง checkout นี้ แต่ baseline 8 ชิ้นจาก dirty branch เดิมเป็น `DRIFT` 4 และ `MISSING` 4; ไม่มีชิ้นใด `MATCH` และตอนนั้น J02 protocol ยังไม่อยู่ใน checkout จึงคง G0 = `BLOCKED_LINEAGE_RECONCILIATION` การเลือก clean equivalent ต้องตรวจเนื้อหา/บทบาทข้อมูลและ rerun Core ที่เกี่ยวข้อง ไม่บังคับให้ hash เก่าเท่ากันหรือเรียกการตรวจผลย่อยว่า G0 ผ่าน

อัปเดต G0 วันที่ 27 ก.ย.: นำเข้า [J02 protocol card](HE4_SECOND_SOUND_PROTOCOL_CARD.md) กับ [source package](Data/03_Research/he4_svp_second_sound_response_source_package.json) จาก commit ที่แผนระบุแบบทบทวนขอบเขตแล้ว ไม่ได้นำเข้า Topic 10 หรือเปลี่ยน Core การตรวจค่าที่ตรึงไว้กับ Core ปัจจุบันผ่าน และ source role เป็น nonblind candidate ที่ยังไม่มี uncertainty รายแถวหรือ two-fluid operator ดังนั้น subblocker เรื่องไฟล์ J02 ไม่อยู่ใน checkout ถูกลบออก แต่ G0 ยัง `BLOCKED_LINEAGE_RECONCILIATION` เพราะ clean Core baseline 8 ชิ้นยังไม่ได้ยอมรับเทียบเท่าหรือ rerun ทั้งชุด ข้อความก่อนหน้านี้เป็น snapshot ก่อนนำเข้า ไม่ใช่สถานะล่าสุด

[He-4 composition reference-lineage screen](Result/artifacts/T13_HE4_COMPOSITION_REFERENCE_LINEAGE_2026-09-27.md) แยกการย้ายที่ของหลักฐานออกจากการตรวจเนื้อหา: reference 12 ชิ้นใน Core composition มีคู่ชื่อเดียวกันในตำแหน่งใหม่ทั้งหมดและ status ตรงกัน แต่ hash เปลี่ยนทั้ง 12 ชิ้น เทียบกับ commit ฐานที่บันทึกไว้แล้ว 9 ชิ้น byte-identical และ 3 ชิ้นเปลี่ยน field โดยหนึ่งรายการเปลี่ยน `closure_level` ใน summary ด้วย การเทียบนี้ไม่กู้สภาพ dirty-worktree เดิม จึงยังไม่ยอมรับว่าเทียบเท่าหรือว่า Core baseline ถูก reproduce แล้ว ผล Core test ที่ผ่านตรวจสถานะที่บันทึกไว้ ไม่ได้ตรวจห่วงโซ่ source/hash ทั้งชุด

[Historical snapshot recovery](Result/artifacts/T13_FUNDING_HISTORICAL_SNAPSHOT_RECOVERY_2026-09-27.md) ตรวจแบบอ่านอย่างเดียวเพิ่มเติมและพบไฟล์ทั้ง 8 ชิ้นที่ byte/hash ตรงแผนใน worktree หลักที่ยัง dirty (tracked-clean 2, modified 2, untracked 4) จึงไม่ต้องถือว่า historical bytes สูญหาย แต่การพบไฟล์ไม่ใช่การรับเข้า clean checkout หรือการตรวจ Core ใหม่; G0 ยังคงถูกบล็อกโดย owner handoff, nested provenance และ clean revalidation ผล `0/4/4` ของ lineage screen ยังถูกต้องเฉพาะ checkout สะอาดนี้

[Clean-admission triage](Result/artifacts/T13_FUNDING_CLEAN_ADMISSION_TRIAGE_2026-09-27.md) แยกงานส่งต่อเป็น 2 รายการ JSON เท่ากันแต่ reference ภายในยังต้องตรวจ, 2 รายการ Core เปลี่ยน field ที่มีผลต่อ source/decision gate, และ 4 รายการไม่มีชื่อเดียวกันใน checkout สะอาด เส้น source ที่มี harmonic payload ยังถูกปฏิเสธว่าไม่ใช่ Ding/PBTE จึงไม่เปิด TTG calibration; curved gate ยังคง `PARTIAL` และไม่ปลดล็อก Gravity การเทียบนี้ไม่เปลี่ยน G0 หรือ readiness ของพอร์ต

[Nested composition-reference recovery](Result/artifacts/T13_FUNDING_NESTED_REFERENCE_RECOVERY_2026-09-27.md) ตรวจ reference ภายใน composition เพิ่ม: path เก่า 12 ชิ้นไม่มีในทั้งสอง worktree แต่ relocated source candidate 8 ชิ้น hash ตรงที่บันทึก, 4 ชิ้นไม่ตรง; เทียบ source กับ clean แล้ว 9 ชิ้น JSON เท่ากัน, 3 ชิ้นต่าง field โดย causal summary มี `closure_level` เพิ่มใน clean ตำแหน่งหนึ่ง ทั้ง 12 status ยังตรง แต่ไม่ได้พิสูจน์ semantic equivalence หรือปิด G0 ต้องให้ Core ตรวจ nested claim/source chain และ rerun ก่อน

อัปเดต 28 ก.ย.: [J02 source-ancestry audit](Result/artifacts/T13_HE4_J02_CALIBRATION_SOURCE_ANCESTRY_2026-09-28.md) ลดบทบาท J02 จาก response candidate ที่อาจตีความว่าอิสระ ให้เป็น source-overlap comparator: calibration superfluid-density reference บางส่วนได้จาก sound measurements ในช่วงอุณหภูมิเดียวกัน แม้ไม่ได้ fit Table 4.3 โดยตรง ความทับซ้อนระดับ row/covariance ยังไม่ทราบ D4-D10 จึงห้ามใช้ J02 เป็น independent He-II test; เป้าหมาย 14 วันยังเป็นผล identifiability/measurement design หรือผลทำนายที่มี input อิสระจริงเท่านั้น G0 และ Full Topic 13 ไม่เปลี่ยน

[Independent-measurement route screen](Result/artifacts/T13_HE4_INDEPENDENT_MEASUREMENT_ROUTE_SCREEN_2026-09-28.md) ระบุงานค้นต่อแบบมีปลายทาง: Wang-Wagner-Donnelly Table 4.1 key 5 เป็น response study คนละชื่อจาก calibration keys 2/3 แต่ยังขาด primary protocol/uncertainty/covariance; Dash-Taylor oscillating-disk เป็นเส้น calibration ไม่ใช้เสียงแต่ยังไม่มี numeric package และต้องแปลง temperature scale ก่อน ใช้เวลาค้น/คัดเข้าแบบมีเพดานใน D3; ถ้าไม่ผ่านให้ใช้ผล identifiability/measurement design ไม่เรียก J02 หรือ key 5 ว่า independent validation โดยอัตโนมัติ

[Frozen He-II operator-domain decision](Result/artifacts/T13_FUNDING_HEII_OPERATOR_DOMAIN_DECISION_2026-09-28.md) รวมผล branch/state ที่มีจริง: reference ที่ตรึงเป็น normal (`q=-0.8715`), tree-condensed witnesses ไม่ใช่ He-II ที่รับเข้า, thermal-only Gaussian Phi root มี scoped amplitude no-go และ formal auxiliary root ใช้ `Z` คนละ prescription ดังนั้น D2–D5 ห้ามสร้าง physical second-sound score จาก frozen bundle หรือรายงาน SVD ของ `h` ที่ยังไม่มี operator เป็น proof of nonidentifiability สายงานที่เปิดคือเลือก completion และ material map ที่ประกาศชัด แล้วพิสูจน์ `h` หรือ same-calibration/different-response family ใน class นั้น G1 physical และ G2 ยังไม่ผ่าน

[Finite-T condensed scheme route decision](Result/artifacts/T13_FUNDING_CONDENSED_SCHEME_SELECTION_2026-09-28.md) คัดเส้นทาง Core และวรรณกรรมที่อาจใช้เติม operator: formal auxiliary เป็น internal Ward/stationarity witness, renormalized vertex ยังอยู่ที่ `mu=0`, Gaussian stationarity ยังขึ้นกับ scheme, SI-2PI มีข้อโต้แย้งเรื่อง linear response, และ two-chemical-potential HFB เปลี่ยน prescription ของ ensemble จึงเป็น comparator ก่อน ไม่เลือกวิธีใดเป็น physical UET operator ด้วยชื่อหรือ Goldstone gap อย่างเดียว D2–D5 ให้ทดลอง derive single-charge source-coupled longitudinal response ภายใต้ fixed prescription หนึ่งชุด; หากยังไม่รับเข้า ให้ G1/G2 เปิดและเสนอ feasibility portfolio ตามจริง

[Rest-EOS/dynamic-response constructive witness](Result/artifacts/T13_FUNDING_REST_EOS_DYNAMIC_DEGENERACY_2026-09-28.md) ปิดคำถามย่อยใน standard nondissipative two-fluid EFT: rest pressure/charge/entropy/energy เหมือนกันทุกสภาวะที่อยู่นิ่งได้ แต่ relative-flow curvature ต่างกันทำให้ low-mode sound ต่างกันโดย quadratic energy ยังเป็นบวกและ linear speed ต่ำกว่าแสงใน anchor ที่ทดสอบ Core มี `f_s_tree=Z*q/lambda` อยู่แล้ว และเทียบกับ `-2 F_X` ได้ **เฉพาะแบบ tree และเมื่อ normalization ของ phase/หน่วยตรงกัน**; frozen normal state ให้ stiffness ศูนย์ ส่วน tree-condensed candidates ยังไม่ใช่ He-II ที่รับเข้า งานต่อจึงเป็นการ lift ค่านี้ไปยัง finite-T stationary current/operator และ physical material map ไม่ใช่หาเลข stiffness ใหม่จาก rest-EOS row ผลนี้ไม่ใช่สอง UET completion และไม่ปิด G2

[Local relaxed-`Phi` response boundary](Result/artifacts/T13_HE4_RELAXED_PHI_RESPONSE_BOUNDARY_2026-09-27.md) ปิดคำถามย่อยที่สำคัญต่อ D4–D5: EOS ที่ตรึง `Phi` ไม่กำหนด ordinary isothermal response เอง แม้คง pressure/density/response แบบตรึงไว้ที่ anchor เดิม ศักย์ตอบสนองท้องถิ่นที่เสถียรสองแบบยังให้ relaxed susceptibility ต่างกัน อีกทั้ง root conditional เดิมไม่ stationary สำหรับ flat partial combination ของ action ที่ประกาศ (`Omega_Phi=-0.04130585` ในหน่วย natural) ผลนี้ไม่ใช่ helium prediction หรือ no-go ของ full UET; ก่อนเทียบ source ต้องปิด stationary background/กฎ `Phi` และ effective curvature `K` อย่างอิสระ

[Conditional flat partial-action stationary root](Result/artifacts/T13_HE4_FLAT_PARTIAL_STATIONARY_ROOT_2026-09-27.md) แสดงว่าการไม่ stationary ของ root เดิมไม่ใช่จุดจบเชิงตัวเลข: เมื่อแก้ `Phi` และ `mu` ใน approximation เดิมร่วมกับเป้าความหนาแน่นที่เคยใช้สร้าง `e0` พบจุด stationary เฉพาะทิศ `Phi` บน tree-condensed branch ที่ลู่เข้าและ curvature `Phi` เป็นบวก แต่ **ไม่ได้** แก้สมดุล amplitude ของ condensate ที่ finite temperature หรือ Ward/Goldstone identity การ match density ยังคง circular ขั้น D4–D5 จึงใช้เป็น conditional internal witness เท่านั้น และต้องตรวจ microscopic Ward-consistent completion กับ observable อิสระก่อนอ้าง predictive content

[Phi/amplitude compatibility result](Result/artifacts/T13_HE4_PHI_AMPLITUDE_COMPATIBILITY_2026-09-27.md) ใช้ no-go ของ Core กับ root conditional ใหม่นี้โดยตรง: ที่ `T>0`, `q>0`, `x=q/lambda` ระบบอยู่ใน stable thermal-only Gaussian domain ที่ `partial_x Omega>0` จึง **ไม่** stationary พร้อมกันในทิศ amplitude ในคลาสนั้น การค้น root เพิ่มในคลาสเดิมไม่ใช่ทางปิดผลหลัก ต้องเลือก renormalized/interacting Ward-preserving branch ที่ประกาศชัดก่อน ไม่เอาผล formal Ward lane มาแทน microscopic completion

[Formal auxiliary joint root](Result/artifacts/T13_HE4_FORMAL_AUXILIARY_PHI_JOINT_ROOT_2026-09-27.md) แสดงว่าใน **formal** auxiliary-field branch ของ Core ที่กำหนด `Z=1.2` มีจุดสมดุลร่วมของ `Phi`, condensate amplitude, auxiliary gap และ Ward gap โดยไม่ใช้ target density แต่สมการ `Phi` ของ approximation นี้ไม่ขึ้นกับ `T` โดยตรงเมื่อ fix `mu` และ branch เดิม `Z=1` อยู่นอก domain ของมัน ผลนี้เป็น feasibility ของคนละพารามิเตอร์และยังไม่ใช่ microscopic/He-II bridge; D4–D5 ต้องตรวจ scheme จริงก่อนเทียบข้อมูล

## 11. แหล่งอ้างอิงที่ใช้วางแผน

อัปเดต D4 ล่าสุด 1 ต.ค.: [scoped real-axis response](Result/artifacts/T13_HARTREE_REAL_AXIS_2026-10-01.md) ปิด exact angular principal value และ pair/scattering cuts โดยไม่กำหนด damping width ตรวจด้วย forward on-shell delta roots และ radial phase space อีกวิธี พร้อม vacuum, Ward, refinement, reality และหน่วยบนสิบจุดที่ประกาศไว้แล้ว รับเป็น preliminary methods evidence ของ named fixed-Phi candidate ได้ แต่ numerical convergence ไม่เป็น global pole stability หรือ controlled Hartree remainder งานต่อคือ global collective/IR และ approximation/regulator/action control ก่อน joint Phi/material/heat-current admission; R1 เต็ม, physical G1/G2 และวันพอร์ตยังไม่เปลี่ยน

อัปเดต D4 วันที่ 1 ต.ค.: [rest-frame Hartree current](Result/artifacts/T13_HARTREE_GAUGE_CURRENT_2026-10-01.md) ปิด source/current consistency ที่ fixed Phi ด้วย actual mixed/current loops, covariance/mean-field reoptimization และ contacts ที่ derive แล้ว Ward ไม่ได้ถูกบังคับด้วย projector และ density susceptibility ตรงกับ stationary potential อีกวิธี ผลนี้นับเป็น preliminary methods evidence สำหรับการตัดสิน D5 ได้ แต่ finite source contact ยังเป็น subtraction convention, real-axis/error และ joint-Phi/material/heat-current ยังไม่รับเข้า จึงไม่เปลี่ยน physical G1/G2, source policy หรือวันพอร์ต

ผล D4 ถัดมา 1 ต.ค.: [thermal one-loop Ward/current matching](Result/artifacts/T13_THERMAL_ONE_LOOP_WARD_CURRENT_2026-10-01.md) คำนวณ tadpole และ bubble จริงแล้ว ไม่ใช่แทนค่าตาม identity และปิด static current แบบ fixed-Phi ในลำดับ one-loop ได้ แต่ amplitude Hessian แบบ bare มี infrared divergence จึงยังไม่ปิด exact finite-T background หรือ retarded response งาน D5 ต้องแยกผลนี้เป็น preliminary derivation จาก physical G1/G2 ที่ยังไม่ผ่าน แล้วตัดสินว่าจะใช้ scoped structural/methods result ในพอร์ตหรือยังขาด proof obligation ใด ไม่รัน shifted Gaussian นอก stable domain เพื่อสร้างคะแนน second sound

อัปเดต D4 เพิ่มเติม 1 ต.ค.: [moving-background thermal curvature และ stationarity boundary](Result/artifacts/T13_THERMAL_GRADIENT_CURVATURE_STATIONARITY_2026-10-01.md) คำนวณเทอม thermal จากสเปกตรัมของ action ได้โดยไม่ fit และทำให้ผู้สมัครทั้งสองผ่าน local mode screen ใน approximation แต่แยกพบ amplitude-path term เพราะ background ยังไม่ stationary งานต่อที่ต้องตรวจจริงจึงเป็น matched tadpole/Ward/self-energy และ current prescription ไม่ใช้การผ่าน mode screen แทน physical G1/G2 มีค่าเทอมที่ต้องชดเชยและวิธีตรวจอิสระสำหรับงานต่อแล้ว; scientific disposition ของพอร์ตยังขึ้นกับ admission/derivation ที่เหลือ

อัปเดต D4 วันที่ 1 ต.ค.: [conditional pressure-Hessian operator](Result/artifacts/T13_CONDITIONAL_TWOFLUID_OPERATOR_2026-10-01.md) ให้สมการเสียงสองโหมดจาก rest-pressure derivatives กับ relative-flow stiffness ใน imported EFT แล้ว แต่การแทน stiffness แบบ tree ตรง ๆ ไม่ผ่านที่ `mu=1.05` (โหมดเร็ว `c^2=1.8219`) และผ่านเฉพาะแบบมีเงื่อนไขที่ `mu=1.20` มีช่วง stiffness ที่ยอมรับได้จากสมการโดยไม่ fit ผู้สมัครเดิมทั้งสองไม่ใช่ He-II ที่รับเข้า ดังนั้น D5 ต้องตัดสินจาก finite-T current/normal-component derivation กับ material admission ที่มีจริง; หากยังขาด ให้ G1/G2 คงเปิด ผลนี้เป็น preliminary methods result สำหรับพอร์ตและกำหนดงาน derive relative-flow response ต่อใน W3–W4 ไม่ใช่ผลทำนาย He-II

- [Donnelly–Barenghi 1998, NIST-hosted reference paper](https://srd.nist.gov/jpcrdreprint/1.556028.pdf), DOI 10.1063/1.556028: แหล่งข้อมูลสมบัติ He-4 ตาม SVP รวม second sound; ต้องย้อนจาก compilation ไป primary experiment สำหรับ protocol/uncertainty ที่ใช้ตัดสิน
- [Lane, Fairbank & Fairbank 1947](https://journals.aps.org/pr/abstract/10.1103/PhysRev.71.600), DOI 10.1103/PhysRev.71.600: primary resonance route สำหรับการตรวจ protocol; การเปิด abstract ยังไม่ปิด state/frequency/uncertainty contract
- [NSF merit review](https://www.nsf.gov/funding/merit-review): ใช้เป็นตัวอย่างให้ proposal มีคำถาม ความสำคัญ แผน วิธีประเมินผล ทีมและทรัพยากรที่ชัดเจน ไม่ใช่ข้อกำหนดของทุนไทยหรือหลักฐานว่าเราเข้าเกณฑ์ทุนใด

อ่านแหล่งออนไลน์วันที่ 27 กันยายน 2026 หลักฐาน UET ใช้ไฟล์และ hash ใน planning JSON; ผล source/holdout ที่มีข้อจำกัดยังคงข้อจำกัดเดิม
