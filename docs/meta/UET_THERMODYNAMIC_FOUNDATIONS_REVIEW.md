# ฐาน Thermodynamic Information ของ UET: สังเคราะห์ก่อนเลือกแบบจำลองจุลภาค

รอบ L — วันตัดยอด 24 ตุลาคม 2026 (Asia/Bangkok)

เอกสารนี้เป็น literature synthesis และการตรวจสายเหตุผล ไม่ใช่ calculation path ใหม่ การพิสูจน์ UET หรือการเลือก microscopic realization ผู้เขียนเลือกรอบสังเคราะห์ฐานทฤษฎีก่อน จึงยังไม่สร้าง Hamiltonian, fast subsystem, constitutive law หรือข้อมูลทดลองใหม่

## 1. คำถาม ขอบเขต และฐานที่คงไว้

**คำถาม:** ผลจาก statistical mechanics และ thermodynamic information ที่มีอยู่ช่วยระบุว่า Ω ของเราคืออะไรได้ถึงขั้นใด ต้องมีเงื่อนไขอะไร และยังขาดอะไรจึงจะเชื่อมกับ internal energy และ heat โดยไม่สับสนความหมาย?

เป้าหมายไม่ใช่รวบรวมชื่อทฤษฎีให้มาก แต่ประกอบสาย **วัตถุที่นิยาม → ผลนำเข้า → เงื่อนไข → การใช้กับ UET → ข้อจำกัด** ให้ผู้อ่านตามตรวจได้ งานคณิตศาสตร์จำเป็นต่อทฤษฎี แต่รอบนี้ไม่ตั้งโจทย์คำนวณใหม่แทนการตรวจฐานที่รับมา

### 1.1 L0 — Baseline และการรักษาหลักฐาน

- Local HEAD `81ad20f12d398e32e62052588dadf61ea96ce353`, branch `codex/research/source-backaction-discrimination`; ไม่ใช่การยืนยันว่า public main อยู่ที่ SHA นี้
- เริ่มรอบพบงานค้างอื่น 463 รายการและ index ว่าง; Topic 13 UPDATE_LOG มี diff เดิม 578 additions / 79 deletions ซึ่งแยกออกจากงานรอบนี้ ไม่สลับ worktree หรือรวมงานเดิม
- ตรวจ canonical identities ของ [joint thermal contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/joint_thermodynamic_completion.json) 8 รายการ และ [cycle contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/energy_memory_cycle.json) 42 รายการ: ตรงกัน ไม่มี identity errors ทั้งสอง review ยังเป็น INCOMPLETE ตามช่องว่างเดิม ไม่รัน scientific verifier ซ้ำ
- เก็บ [Theory Argument §§14, 17–19, 30](UET_THEORY_ARGUMENT.md) และ artifact/contract เดิมโดยไม่แก้เนื้อหา/hash รายงานใหม่นี้เชื่อมกลับไปยังผลเหล่านั้น ไม่คัดลอก proof/ผลทั้งชุดมาสร้างทะเบียนซ้ำ
- ไม่มี contract, gate, schema, numerical test หรือ scientific artifact ใหม่ เพราะผลส่งมอบเป็นการสังเคราะห์เอกสาร ไม่ได้เปิดเส้นทางคำนวณใหม่

### 1.2 สิ่งที่มีแล้ว และสิ่งที่รอบนี้ไม่ถือว่าได้เพิ่ม

| หลักฐานเดิม | ใช้ต่อในขอบเขตใด | ไม่ใช้แทนอะไร |
| --- | --- | --- |
| Argument §14 | C=s_C m, state counting/mean-field และ local quartic correspondence มีขอบเขต/ข้อโต้แย้งเดิม | ไม่ใช่ microscopic derivation ของ Phi หรือ global equality ของ full entropy กับ quartic |
| §§17–19 | C-only conditional reaction closure, source-port distinction และ hidden-channel limitations | ไม่ใช่ joint thermodynamics ที่ derive จาก microstates ของ C/Phi/Pi แล้ว |
| §30 REF-E | one-bath reference มี conditional first law, Gibbs, odd-Pi entropy balance และ standard equivalence | ไม่ใช่ material internal energy/heat, unique kinetics หรือ UET-specific prediction |
| §30 HIST-F | single-temperature free energy/drift ไม่เลือก intrinsic entropy/heat dictionary ให้เอง | ไม่ใช่เหตุให้ตั้ง entropy ที่ไม่รู้เป็นศูนย์หรือสรุปว่าทั้งทฤษฎีผิด |

### 1.3 ที่มาของข้อเสนอและ bounded work card

เจตนาผู้เขียนที่ใช้ต่อคือระบบซ้อนระบบมีปฏิสัมพันธ์ ผลอดีตอาจคงอยู่ในสภาพ/ความสัมพันธ์และเปลี่ยนการตอบสนอง Information ในความหมายนี้ยังไม่ถูกกำหนดให้เท่ากับ C, Phi, entropy, mutual information หรือ trace ผู้เขียนยังเสนอจักรวาลเปิดเป็นเป้าหมายระดับภาพรวม ไม่เปลี่ยนให้เหลือเพียง subsystem ที่เปิดต่อ bath

การเลือก C-side comparator, affine coupling, thermal reference และการแบ่ง proof ในงานเดิมเป็น model/reference choices ของผู้ตรวจตามขอบเขตที่บันทึกไว้ ผลจากแหล่งภายนอกเป็น imported theory ส่วนการจัดความสัมพันธ์ในรายงานนี้เป็นการสังเคราะห์ของ AI ไม่ใช่การยืนยันเจตนาหรือการตรวจทางฟิสิกส์จากผู้เชี่ยวชาญอิสระ

- **Stage / claim:** TD0–TD3 เชิง synthesis; ตรวจความหมาย เงื่อนไข และข้อจำกัดของฐานที่รับมา ไม่เลือก model ใน TD1 แทนผู้เขียน
- **Boundary:** แยก slow joint state, รายละเอียดภายในที่ถูกรวมออก, environment, carrier/detector และ record; บทบาทเปลี่ยนตามคำถาม ไม่สันนิษฐาน full observability หรือ significant backaction จากการมี interaction
- **Controller:** ช่องว่าง `intrinsic-entropy-correspondence` ใน joint contract เดิมและ scope ใน Argument §30; วรรณกรรมช่วยกำหนดเงื่อนไข ไม่ทำให้ช่องว่างนี้ปิดเอง
- **Have / missing:** conditional reference ปิดได้แล้ว; ยังขาด joint state/measure/thermal dictionary และ independent physical mapping
- **Action / why:** อ่าน source statements ที่รองรับหรือจำกัดความหมายเหล่านี้ แล้วเทียบของเดิม เพื่อไม่เลือกตัวอย่าง/สมการจากสัญลักษณ์หรือความสะดวกในการคำนวณ
- **Outcomes:** รับผลได้ภายใต้เงื่อนไข / ใช้ข้ามขอบเขตไม่ได้ / มีหลาย convention / ยังต้องมี input หรือ author choice ชัดเจน
- **Stop:** จบเมื่อมี synthesis และคำถามตัดสินใจขั้นต่ำ ไม่รอ physical closure หากต้องคำนวณหรือสร้าง model ให้เสนอรอบใหม่ ไม่เริ่มเอง
- **Reviewer question:** นิยามและสมมติฐานที่ยืมมาถูกใช้กับวัตถุระดับเดียวกันหรือไม่ โดยเฉพาะ coarse free energy, intrinsic entropy และ heat; ยังไม่ติดต่อผู้เชี่ยวชาญ

**ผล L0:** ยืนยันฐานและขอบเขตสำเร็จ การตั้งเอกสารและการตรวจ identities ไม่ใช่หลักฐานว่าช่องว่างทางฟิสิกส์ปิดแล้ว

## 2. L1 — ฐานที่อ่านจริง และเงื่อนไขที่รับมา

ตรวจเนื้อหาหลักตามตำแหน่งต่อไปนี้ ไม่ใช้ abstract เป็นหลักฐานแทน derivation เอกสารทั้งหมดเข้าถึงเมื่อ 24 ตุลาคม 2026 รุ่นที่ระบุเป็นรุ่นที่หน้าแหล่งข้อมูลแสดง ไม่ใช่การรับรองว่าได้ตรวจทุก revision หรือ byte identity ของเว็บไซต์ ไม่มีการเก็บสำเนา paper ดิบใน repository

### 2.1 Tong — จากการนับสถานะไปสู่ effective free energy

แหล่ง: David Tong, [Statistical Field Theory, Chapter 1](https://www.damtp.cam.ac.uk/user/tong/sft/sfthtml/S1.html), §§1.1.1–1.2 โดยเฉพาะ Eqs. (1.7)–(1.13) และ (1.17); official Cambridge HTML ไม่แสดง revision identifier ที่ยืนยันได้ในการตรวจครั้งนี้

- **ผลที่รับมา:** constrained free energy ของ magnetization และ mean-field polynomial มีสายจาก canonical state counting
- **วัตถุ:** magnetization ของ configuration, จำนวน configuration, free energy เมื่อบังคับค่า m และ ensemble free energy เป็นคนละวัตถุ; Ω ในบทนี้หมายถึง multiplicity ไม่ใช่ Ω ของ UET
- **เงื่อนไข:** binary spins, |m|≤1, finite-N grid; mean-field, large-N/Stirling และ small-m expansion เป็นคนละ approximation
- **สิ่งที่ไม่ตามมา:** quartic ไม่เท่ากับ full entropy ทั่ว domain; การนับ C-side ไม่กำหนด microstates ของ Phi
- **ตำแหน่ง UET:** ใช้ตรวจขอบเขต [Argument §14](UET_THEORY_ARGUMENT.md) ที่มีอยู่ ไม่ทำ matching หรือคำนวณ remainder เดิมซ้ำ

### 2.2 Seifert 2012 — intrinsic entropy และความหมายของ heat

แหล่ง: Udo Seifert, [Stochastic thermodynamics, fluctuation theorems, and molecular machines](https://arxiv.org/html/1205.4176), arXiv:1205.4176v1, 18 May 2012; §§9.2.1–9.2.4, Eqs. (206)–(222)

- **ผลที่รับมา:** F ของ coarse state รวม intrinsic entropy; constrained internal energy ไม่ใช่ F โดยอัตโนมัติ การระบุ heat ต้องรักษาส่วนนี้
- **วัตถุ:** distribution ภายใน coarse state, F(x,T), S_int(x,T), U(x,T), stochastic entropy ของ distribution ระหว่าง coarse states
- **เงื่อนไข:** conditional thermal equilibration ภายใน state เร็วกว่าพลวัตที่เก็บไว้ และ thermal/reference convention ที่ระบุ; ต้นฉบับใช้ k_B=1
- **สิ่งที่ไม่ตามมา:** รู้ drift หรือ F ที่อุณหภูมิเดียวแล้วรู้ S_int/heat ครบ หรือทุกตัวแปรที่เรียก information เป็น entropy
- **ตำแหน่ง UET:** รองรับเหตุผลที่ §30 แยก REF-E จาก HIST-F; ไม่เลือก thermal dictionary ของ C/Phi/Pi ให้เอง

### 2.3 Esposito 2012 — การรวมรายละเอียดออกไม่ใช่การลบต้นทุนทิ้ง

แหล่ง: Massimiliano Esposito, [Stochastic thermodynamics under coarse-graining](https://arxiv.org/html/1112.5410), arXiv:1112.5410v1, 22 Dec 2011; §§III–IV, Eqs. (28)–(49), (50)–(77)

- **ผลที่รับมา:** coarse rate ยังขึ้นกับ conditional microstate distribution; equilibrium closure ต้องมีเงื่อนไขเพิ่ม และ coarse entropy มีทั้งส่วนระหว่างและภายใน macrostates
- **วัตถุ:** classical Markov jump process, macrostate partition และ reservoir-resolved transitions; Ω ของบทความเป็น grand potential
- **เงื่อนไข:** time-scale separation; การใช้ conditional equilibrium ต้องมี reservoir/local detailed balance ที่เหมาะ และ driving ไม่เร็วเกิน fast relaxation
- **สิ่งที่ไม่ตามมา:** fast stationary เท่ากับ thermal equilibrium เสมอ หรือ hidden entropy production เป็นศูนย์; zero-current statement ของ jump sector ใช้กับ odd-Pi ทั้ง phase space ไม่ได้
- **ตำแหน่ง UET:** ตรวจ prerequisite ของ future joint closure และข้อจำกัด hidden channels ใน §§17–19/30 ไม่ใช่ derivation ใหม่ของ joint process

หมายเหตุรุ่น: HTML แสดง dateline “August 24, 2026” แต่ header ระบุ v1 ปี 2011 จึงไม่ใช้ dateline ที่ render เป็นวันเกิดผลวิจัยหรือหลักฐานว่ามีผลใหม่ในปี 2026

### 2.4 Seifert 2016 — strong system–bath coupling

แหล่ง: Udo Seifert, [First and Second Law of Thermodynamics at strong coupling](https://arxiv.org/html/1512.03746), arXiv:1512.03746v1, 11 Dec 2015; Eqs. (3)–(14), (20)–(27) และ discussion หลัง Eq. (27)

- **ผลที่รับมา:** Hamiltonian of mean force (HMF) และ temperature derivative ให้ thermodynamic assignment หนึ่งที่สอดคล้อง; internal energy ต่างจาก HMF เมื่อมี temperature dependence
- **วัตถุ:** classical Hamiltonian ของ system+bath+interaction และ reduced equilibrium description
- **เงื่อนไข:** control กระทำที่ system; second-law construction ใช้ conditional-equilibrium bath ใน initial preparation และ conventions ที่ประกาศ
- **สิ่งที่ไม่ตามมา:** arbitrary bath preparation ใช้ได้หมด หรือ consistency ทำให้ trajectory heat มีความหมายเดียวโดยไม่มีข้อกำหนดเพิ่ม; C–Phi coupling ไม่ใช่ system–bath coupling โดยนิยาม
- **ตำแหน่ง UET:** เป็นทางเลือกเชิงกรอบหากอนาคตแสดง bath correspondence ได้ ยังไม่เปลี่ยน Ω เป็น HMF หรืออ้างว่าระบบ UET อยู่ใน strong-coupling regime

### 2.5 Talkner–Hänggi 2016 — ข้อคัดค้านเรื่อง reconstruction และ uniqueness

แหล่ง: Peter Talkner และ Peter Hänggi, [Open system trajectories specify fluctuating work but not heat](https://arxiv.org/pdf/1605.07415), arXiv:1605.07415v4, 26 Aug 2016; §II Eqs. (5)–(18), §III Eqs. (19)–(22), §§IV–V และ Appendix A Eq. (A1)

- **ผลที่รับมา:** normalized reduced distribution ไม่กำหนด HMF และ free-energy normalization แยกกันทั่วไป; matching equilibrium averages ยังเหลือเสรีภาพของ fluctuating quantities
- **วัตถุ:** classical open-system equilibrium thermodynamics และการขยายเป็น trajectory assignments ไม่ใช่ theorem ว่าความร้อนทุกระบบวัดไม่ได้
- **เงื่อนไข:** ต้องแยกกรณีรู้ full HMF/temperature dependence แล้ว จากกรณีมีเพียง trajectory statistics; heat convention และ preparation สำคัญ
- **สิ่งที่ไม่ตามมา:** equilibrium HMF framework ใช้ไม่ได้ทั้งหมด หรือข้อเสนอ Seifert ผิดทุกเงื่อนไข
- **ตำแหน่ง UET:** ห้ามประกาศว่า readout/drift ที่ตรงกันเลือก internal energy/heat ให้เอง ต้องมี independent dictionary และ operational definition

หมายเหตุรุ่น: หน้า abstract ยืนยัน v4 ลงวันที่ 26 Aug 2016; PDF ที่ให้บริการแสดง dateline “July 5, 2021” ด้วย จึงใช้ version header กับ section/equation เป็น locator ไม่สมมติว่าเป็น revision ปี 2021 ที่ตรวจแยกแล้ว

### 2.6 Horowitz–Esposito 2014 — information flow ระหว่างระบบย่อย

แหล่ง: Jordan M. Horowitz และ Massimiliano Esposito, [Thermodynamics with continuous information flow](https://arxiv.org/html/1402.3276), arXiv:1402.3276v3, 30 Jun 2014; §III Eqs. (8)–(12), §VII Discussion

- **ผลที่รับมา:** mutual information ของ joint distribution และ current-resolved information flows เข้าไปใน subsystem entropy balances ได้
- **วัตถุ:** bipartite classical jump dynamics; partial entropy production ไม่ใช่ entropy ของ subsystem เพียงอย่างเดียว
- **เงื่อนไข:** bipartite transition structure และ thermodynamic reservoir identification; สูตร jump ไม่ใช่สูตรสำเร็จสำหรับ mixed overdamped–underdamped dynamics
- **สิ่งที่ไม่ตามมา:** MI เท่ากับ information ทุกความหมาย, งานแบ่งระหว่าง subsystem มีนิยามเอกลักษณ์ หรือความสัมพันธ์คงที่พิสูจน์ learning
- **ตำแหน่ง UET:** เป็นฐาน comparator ของ partition C กับ (Phi,Pi); ใช้ mixed-generator result ที่ตรวจไว้แล้วใน §30.8 ไม่ย้าย jump formula มารันใหม่หรือเลือก MI เป็น ontology แทนผู้เขียน

### 2.7 ฐาน Shannon–Landauer–Bennett ที่ใช้ต่อโดยไม่เปิด audit ใหม่

ใช้ขอบเขตที่บันทึกใน [Argument §3.3](UET_THEORY_ARGUMENT.md) และ [Trace research specification §5](../core/01_contracts/TRACE_RESEARCH_SPEC.md): ปริมาณจาก distribution, เงื่อนไขต้นทุน erasure และการแยก reversible measurement/computation ออกจาก erasure เป็นคนละบทบาท ไม่ยกชื่อ Landauer เป็น derivation ของ dimensionless beta ไม่อนุมาน universal rest mass ต่อบิต หรือ heat เท่ากันทุก interaction

รอบ L ไม่อ้างว่าได้อ่านต้นฉบับ Shannon/Landauer/Bennett ใหม่ทั้งหมด หรือยกระดับ old audit เป็น independent replication ถ้าข้อเสนออนาคตต้องพึ่ง theorem เฉพาะนอกขอบเขตนี้ ต้องตรวจต้นฉบับตรงจุดนั้นก่อนใช้

**ผล L1:** corpus ที่เลือกให้ทั้งเส้นทางเชื่อมและข้อจำกัด ไม่ได้เสนอ dictionary สำเร็จรูปของ UET ความเห็นต่างที่ต้องรักษาคือ reconstruction จาก observation กับ uniqueness ของ trajectory assignment ไม่ใช่เลือกเชื่อผู้เขียน paper คนใดเพื่อปิดช่องว่าง
