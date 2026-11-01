# ฐาน Thermodynamic Information ของ UET: สังเคราะห์ก่อนเลือกแบบจำลองจุลภาค

รอบ L — วันตัดยอด 24 ตุลาคม 2026 (Asia/Bangkok)

เอกสารนี้เป็น literature synthesis และการตรวจสายเหตุผล ไม่ใช่ calculation path ใหม่ การพิสูจน์ UET หรือการเลือก microscopic realization ผู้เขียนเลือกรอบสังเคราะห์ฐานทฤษฎีก่อน จึงยังไม่สร้าง Hamiltonian, fast subsystem, constitutive law หรือข้อมูลทดลองใหม่

**อ่านสรุปก่อน:** ฐาน thermodynamic information ให้ทางพัฒนา UET ที่มีเงื่อนไขชัด ไม่ได้บอกว่าต้องทิ้งสมการเดิม แต่ก็ไม่ได้เลือกความหมายทางกายภาพให้จากรูปสมการเพียงอย่างเดียว สิ่งที่ต้องประกอบให้ครบคือ **สถานะที่เก็บไว้ → รายละเอียดที่รวมออก → วิธีนับสถานะ → การพึ่งอุณหภูมิ → บัญชีงานและความร้อน** ก่อนเลือกตัวอย่างจุลภาค ไม่ใช่เริ่มจากหาวัสดุหรือเพิ่มเทอม

รอบนี้ปิดคำถามระดับ synthesis ได้ว่า Ω อาจเป็น effective potential ของ reference หรือ candidate coarse free energy ภายใต้ dictionary ที่เพิ่ม แต่ยังไม่ทราบว่าเป็น internal energy/heat ของระบบจริงอย่างไร Phi, retained memory, sigma/R และ mutual information ไม่ใช่ชื่อแทนกันทั้งหมด และการเปรียบเทียบกับมาตรฐานที่เทียบเท่าไม่ได้ทำให้งานหมดความหมาย เพียงจำกัดสิ่งที่เรียกว่าข้อเสนอเฉพาะ UET

ทางอ่าน: [แผนที่ความหมาย](#foundations-map) → [เทียบเทอม UET](#uet-thermal-dictionary) → [สิ่งที่ต้องตัดสินใจก่อนรอบใหม่](#before-microscopic-design) โดย source cards และฐานตรวจอยู่ใน §§1–2 ส่วนผลตรวจและข้อจำกัดอยู่ §6

## 1. คำถาม ขอบเขต และฐานที่คงไว้

**คำถาม:** ผลจาก statistical mechanics และ thermodynamic information ที่มีอยู่ช่วยระบุว่า Ω ของเราคืออะไรได้ถึงขั้นใด ต้องมีเงื่อนไขอะไร และยังขาดอะไรจึงจะเชื่อมกับ internal energy และ heat โดยไม่สับสนความหมาย?

เป้าหมายไม่ใช่รวบรวมชื่อทฤษฎีให้มาก แต่ประกอบสาย **วัตถุที่นิยาม → ผลนำเข้า → เงื่อนไข → การใช้กับ UET → ข้อจำกัด** ให้ผู้อ่านตามตรวจได้ งานคณิตศาสตร์จำเป็นต่อทฤษฎี แต่รอบนี้ไม่ตั้งโจทย์คำนวณใหม่แทนการตรวจฐานที่รับมา

### 1.1 L0 — Baseline และการรักษาหลักฐาน

- Local HEAD `81ad20f12d398e32e62052588dadf61ea96ce353`, branch `codex/research/source-backaction-discrimination`; ไม่ใช่การยืนยันว่า public main อยู่ที่ SHA นี้
- เริ่มรอบพบงานค้างอื่น 463 รายการและ index ว่าง; Topic 13 UPDATE_LOG มี diff เดิม 578 additions / 79 deletions ซึ่งแยกออกจากงานรอบนี้ ไม่สลับ worktree หรือรวมงานเดิม
- ตรวจ canonical identities ของ [joint thermal contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/joint_thermodynamic_completion.json) 8 รายการ และ [cycle contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/energy_memory_cycle.json) 42 รายการ: ตรงกัน ไม่มี identity errors ทั้งสอง review ยังเป็น INCOMPLETE ตามช่องว่างเดิม ไม่รัน scientific verifier ซ้ำ
- เก็บ [Theory Argument §§14, 17–19, 30](UET_THEORY_ARGUMENT.md) และ artifact/contract เดิมโดยไม่แก้เนื้อหา/hash รายงานใหม่นี้เชื่อมกลับไปยังผลเหล่านั้น ไม่คัดลอก proof/ผลทั้งชุดมาสร้างทะเบียนซ้ำ
- Theory Argument, joint contract และ joint artifact ตรงกับ blob ใน `81ad20f12` หลัง canonical LF normalization; METHOD ที่ใช้ตรวจ drift เป็น **working-copy snapshot ซึ่งต่างจาก commit นั้น** ไม่อ้างว่าเป็น public main หรือรวมสองรุ่นเงียบ ๆ ดู identity ใน §6
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

- **Stage / claim:** ทบทวน proposition และ prerequisites ของลำดับ TD0–TD3 เชิง synthesis; ไม่ประกาศว่าผ่านทุก stage หรือเลือก model ใน TD1 แทนผู้เขียน
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

<a id="foundation-information-flow"></a>

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

<a id="foundations-map"></a>

## 3. L2 — เรื่องเดียวกัน แต่คนละระดับของคำอธิบาย

### 3.1 อธิบายโดยไม่ต้องเริ่มจากสมการ

เมื่อเราเก็บเพียง C และ Phi เราอาจกำลังเรียกหลายสภาพจุลภาคด้วยชื่อ coarse state เดียวกัน การรู้ว่าอยู่ที่ coarse state ใดจึงไม่จำเป็นต้องบอกว่ารายละเอียดภายในจัดเรียงอย่างไร นี่ต่างจากความไม่แน่นอนว่าในแต่ละครั้งระบบอยู่ที่ coarse state ใด และต่างอีกจากความสัมพันธ์ระหว่างระบบย่อยสองส่วน

ถ้ารายละเอียดภายในปรับสมดุลได้เร็วพอ การรวมมันออกอาจให้ free-energy landscape ที่ใช้กับพลวัตช้าได้ แต่ถ้ารายละเอียดนั้นเก็บประวัติที่ยังเปลี่ยนการตอบสนองครั้งต่อไป การเรียกมันว่า “รายละเอียดที่ไม่ต้องติดตาม” อาจทำให้คำอธิบายไม่ปิด เงื่อนไขการตัดออกจึงเป็นเรื่องกลไกและเวลา ไม่ใช่เพราะตัวแปรอ่านยากหรือสมการจะสั้นลง ดูเงื่อนไขใน §2.2–2.3

**ข้ออนุมานสำหรับ UET:** การเก็บ Phi/Pi ไว้ใน state และการรวม fast degrees of freedom อื่นออกไม่ขัดกัน แต่ต้องบอกว่ารายละเอียดชุดใดถูกเก็บ ชุดใดถูกตัด และเหตุใด การตั้งชื่อ Phi ว่า memory, space response หรือ information ไม่ได้ตอบคำถามนี้แทน microscopic correspondence

### 3.2 แผนที่ entropy และ information

| ปริมาณ | นิยาม/ระดับที่ต้องระบุ | ต้องไม่แทนด้วยอะไรเงียบ ๆ |
| --- | --- | --- |
| Microstate count / degeneracy | จำนวนสภาพที่สอดคล้องกับข้อจำกัด; ไม่ใช่ entropy จนระบุการนับและ weighting | จำนวนไฟล์ ขนาด trace หรือ amplitude ของ field |
| Shannon/Gibbs entropy | functional ของ probability distribution และ reference measure; การให้ความหมาย thermodynamic ต้องมี correspondence | “ความเปลี่ยนแปลงทั้งหมด” หรือ energy ที่ใช้ไป |
| Intrinsic entropy | entropy ของรายละเอียดภายในที่ coarse state ยังไม่ได้แยก; ต้องมี conditional distribution | entropy ของ distribution ระหว่าง coarse states |
| Joint/marginal entropy | entropy ของ joint state หรือของ state หลัง marginalize; ระดับ hidden entropy ต้องระบุแยก | ผลรวม entropy ย่อยโดยไม่ตรวจ dependence |
| Mutual information (MI) | dependence ของ joint distribution เทียบกับ product marginals | legacy I, Phi, total entropy หรือความจำเชิงกลไกทั้งหมด |
| Retained memory | state/โครงสร้าง/ความสัมพันธ์ที่ยังมีผลต่อการตอบสนอง ต้องตาม coupling จริง | histogram dependence เพียงอย่างเดียว หรือบันทึกของ detector |

แถว entropy ใช้ขอบเขต §2.2–2.3 ส่วน MI ใช้ §2.6 และ [ผล chain rule/zero-covariance ใน Argument §§30.8–30.9](UET_THEORY_ARGUMENT.md) ตารางเป็นการสังเคราะห์ศัพท์ ไม่ใช่การประกาศ ontology ใหม่: information ในเจตนาผู้เขียนยังอาจสัมพันธ์กับหลายแถว แต่การใช้คำเดียวไม่ทำให้วัตถุเหล่านี้เท่ากัน

ใน coarse-state entropy accounting ต้องรักษาทั้งความไม่แน่นอนระหว่าง state และค่าเฉลี่ย entropy ภายใน state ตาม construction นั้น การคำนวณ MI ระหว่าง retained variables จึงไม่ได้คืนรายละเอียดหรือ correlation ที่รวมออกทั้งหมดให้โดยอัตโนมัติ นี่คือเหตุผลที่ “วัด dependence ได้” กับ “รู้ entropy ที่ Ω รวมไว้ครบแล้ว” เป็นคนละคำถาม

หน่วยต้องแยก: Shannon entropy/MI ที่ใช้ natural logarithm เป็น nat และไร้มิติ; ถ้าใช้ log base 2 เป็น bit เมื่อมี physical correspondence จึงแปลง entropy เป็น S=k_B H_nats=k_B ln(2) H_bits หน่วย J/K ไม่ใช่คูณ k_B กับจำนวน bits แล้วละ ln(2) และไม่ใช่กลายเป็นพลังงานเอง Differential entropy ของ continuous density ต้องประกาศ measure/scale; ไม่เอาค่าตัวเลขไปเทียบกับ discrete-state entropy โดยไม่ระบุการ coarse-grain ดู conventions ของ [§30](UET_THEORY_ARGUMENT.md)

### 3.3 แผนที่ energy: landscape ไม่ใช่บัญชีทุกชนิด

| วัตถุ | ใช้ตอบคำถามใด | เงื่อนไขหรือข้อมูลที่ยังต้องมี |
| --- | --- | --- |
| Microscopic energy / Hamiltonian | พลังงานของ microstate ตามระบบที่นิยาม | state, interactions, units, boundary และสิ่งที่ควบคุม |
| Constrained/coarse free energy F(x,T) | thermal weighting เมื่อบังคับ retained state x | conditional ensemble, measure/degeneracy และ temperature dependence |
| Ensemble equilibrium free energy | thermodynamic potential หลังรวม distribution ของ retained states อีกระดับ | partition function และ normalization; ไม่ใช่เพียงค่าของ landscape ที่ state หนึ่ง |
| Internal energy U | พลังงานภายในตาม thermal/system partition ที่เลือก | ไม่ใช้ชื่อ energy ของ F แทน; ต้องมี intrinsic contribution หรือ HMF convention ที่เหมาะ |
| Hamiltonian of mean force H* | effective equilibrium object เมื่อรวม bath ออก | total/bare-bath reference และ coupling convention; ไม่ใช่ชื่อใหม่ของ polynomial ใด ๆ |
| Effective/Lyapunov ledger | ตรวจ balance หรือ dissipation ของ realization ที่ประกาศ | คำตอบเรื่อง normalized dynamics ไม่รับรอง SI calorimetry |

สูตรที่ต้องใช้ทำความเข้าใจในจุดนี้เป็น **นิยามจากฐานภายนอก ไม่ใช่สมการ UET ที่เพิ่มใหม่**: ภายใต้ constrained canonical construction ที่ microscopic energy กับ partition/measure ไม่พึ่ง T อย่างชัดแจ้ง และทำ derivative ที่ fixed x,λ,

\[
F_x(T)=-k_BT\ln Z_x(T),\qquad
S_{\mathrm{int},x}=-\left(\frac{\partial F_x}{\partial T}\right)_{x,\lambda},\qquad
U_x=F_x+T S_{\mathrm{int},x}.
\]

ใน construction นี้ U_x คือ conditional average ของ microscopic energy; effective F ยังพึ่ง T ผ่านการรวม state ได้ หากเริ่มจาก T-dependent effective Hamiltonian/measure ต้องพิจารณา derivative corrections และที่มาของมัน ไม่เรียก average ของ effective Hamiltonian ว่า U ด้วยสูตรเดิมเงียบ ๆ ไม่ใช้ derivative ของพารามิเตอร์ fit ที่ไม่ทราบแทนคำตอบต้นทาง สูตรนี้คืน k_B และ T หน่วย K ให้ชัด ต่างจาก convention k_B=1 ใน [Seifert §9.2](https://arxiv.org/html/1205.4176) สำหรับ HMF ต้องใช้ bath-reference construction ของ §2.4–2.5 ไม่อ้างว่าทุก U_x ในตารางเป็น bare-system energy

**สิ่งที่ผลเดิมตัดสินแล้ว:** การอ่าน REF-E ของ Ω เป็น normalized potential ใช้ต่อได้ใน reference ที่ประกาศ การอ่าน HIST-F ว่า Ω เป็น coarse free energy ต้องใช้ dictionary เพิ่ม [Argument §30.4](UET_THEORY_ARGUMENT.md) แสดงไว้แล้วว่า single-temperature family/drift ไม่เลือก intrinsic entropy และ heat ให้เอกลักษณ์ รอบ L ไม่สร้าง witness หรือรันผลนี้ซ้ำ

### 3.4 การรวมออกสองชนิด และความเห็นต่างที่ไม่ควรซ่อน

การรวมรายละเอียดภายในระบบออกกับการรวม bath ออกอาจใช้แนวคิด conditional averaging คล้ายกัน แต่ **ไม่ใช่ partition เดียวกันโดยอัตโนมัติ** ใน UET พจน์ coupling ระหว่าง C กับ Phi อยู่ภายใน joint realization ส่วน coupling ของ joint realization นี้กับ bath ยังต้องนิยาม การรู้ g จึงไม่บอกความแรงของ system–bath coupling และการนับ interaction energy ต้องนับครั้งเดียวตาม [Argument §§19, 30](UET_THEORY_ARGUMENT.md)

งาน strong coupling ทั้งสองยอมให้ใช้ HMF สร้าง equilibrium thermodynamics เมื่อมีข้อมูลตาม construction แต่ต่างกันที่ข้อกำหนดเพิ่มเพื่อเลือก fluctuating assignments และการกู้ข้อมูลจากการสังเกต: Seifert เสนอ assignment ภายใต้ conventions ของตน ขณะที่ Talkner–Hänggi ชี้ normalization/assignment freedom ที่ยังเหลือ ดู [Seifert discussion](https://arxiv.org/html/1512.03746) และ [Talkner–Hänggi §§II–V, Appendix A](https://arxiv.org/pdf/1605.07415)

**ข้อวินิจฉัยของรายงานนี้:** ต้องแยกสามระดับ คือความสอดคล้องของ equilibrium ensemble, การเลือก trajectory energy/heat และการที่เครื่องมือเข้าถึงปริมาณนั้นได้จริง ไม่ถือว่าการทำระดับแรกผ่านเป็นคำตอบครบอีกสองระดับ และไม่ใช้ข้อคัดค้านนี้สรุปว่าไม่มีทางนิยามหรือวัด heat ใน physical setup ที่ระบุครบแล้ว นี่คือข้อจำกัดของการอนุมาน ไม่ใช่ข้อห้ามทำทฤษฎีต่อ

เงื่อนไข preparation ก็ต้องแยก “bath อยู่ใน conditional equilibrium ตอนเริ่ม” ออกจาก “distribution จริงยังมีรูปนั้นตลอดการขับ” โดยเฉพาะการใช้ reference/test density ใน fluctuation-theorem construction ไม่เท่ากับการประกาศว่าเป็น evolved density จริง ข้อนี้เป็นคำถามส่งผู้เชี่ยวชาญหากใช้ strong-coupling lane ต่อ ไม่ได้เลือก lane นั้นในรอบ L

การใช้ system+bath Hamiltonian เป็นฐานนำเข้าของ framework เหล่านี้เป็น construction ของคำถามนั้น ไม่ใช่ข้อพิสูจน์ว่าจักรวาลต้องเป็นระบบปิด หรือว่าข้อเสนอจักรวาลเปิดของผู้เขียนถูกแทนด้วย bath model แล้ว การเชื่อมระดับดังกล่าวยังอยู่นอกผลรอบ L

### 3.5 Measure, degeneracy, N และ temperature: จุดที่ต้องล็อกพร้อมกัน

ข้อกำหนดต่อไปนี้เป็นการนำข้อจำกัดข้างต้นมาใช้กับช่องว่าง UET ไม่ใช่ข้อค้นพบ numerical ใหม่

1. **นับรายละเอียดครั้งเดียว:** ถ้า F รวม multiplicity แล้ว ห้ามใส่ degeneracy เดิมซ้ำใน retained-state measure โดยไม่แสดงการแปลง convention ถ้าเก็บมันใน measure ต้องบอกว่า F นิยามคนละแบบ ไม่สลับกลางการคำนวณ
2. **ไม่ละค่าคงที่โดยลืมเป้าหมาย:** additive term ที่ไม่ขึ้นกับ C/Phi อาจไม่เปลี่ยนแรงที่ T เดียว แต่ถ้าพึ่ง T ก็ยังเกี่ยวกับ thermal normalization/entropy ไม่สรุปว่าหา U/heat dictionary ได้จาก gradient เพียงอย่างเดียว ข้อกำหนดนี้ไม่เท่ากับว่าทุก constant เปลี่ยน isothermal trajectory heat
3. **N ไม่ใช่ factor ประดับ:** แยก F ทั้ง cell จาก f ต่อ site; θ_site จาก Θ ของ normalized joint reference; ระบุจำนวน state, cell volume และ C=s_C m เมื่อใช้ [§§14, 17](UET_THEORY_ARGUMENT.md) ความสัมพันธ์ Θ=θ_site/N ใน conditional C-only bridge เดิมไม่ใช่ derivation ของ noise ของ joint C/Phi/Pi
4. **Domain ต้องเดินมาด้วย:** binary m มีช่วงจำกัด ขณะที่ quartic reference บนทั้งเส้นจริงเป็นคนละ domain; local expansion ไม่ให้สิทธิ์ย้าย tails/measure/entropy ทั่ว domain แทนกัน
5. **Derivative ต้องรู้ว่าล็อกอะไร:** ที่ fixed physical control ไม่ใช่ fixed fitted coefficient เสมอ หาก coefficients หรือ coupling เป็น functions ของ T ต้องมีที่มาของ derivatives ไม่กำหนดเป็นศูนย์เพราะยังไม่มีข้อมูล
6. **Θ ยังไม่ใช่ T ใน K:** normalized bath-energy scale กับ SI temperature ต้องมี energy/time/field normalization ชัด β ที่เป็น inverse temperature ใน paper ก็ไม่ใช่ dimensionless UET coupling beta
7. **การ eliminate ไม่ได้จากคำว่า fast อย่างเดียว:** ต้องพิจารณา relaxation, driving และช่วงการตอบสนองที่สนใจ หาก hidden states ยังมีประวัติหรือ heat channels ที่ตัดสินผล อาจยังใช้ equilibrium closure ไม่ได้ อย่าตัด state เพิ่มเพื่อให้ดูเป็นแบบจำลองเล็ก

### 3.6 Work, heat, trace และผู้สังเกต

[ผลเดิม §§18–19 และ §30](UET_THEORY_ARGUMENT.md) แยก ledger source contribution ออกจาก physical force-port work ไว้แล้ว ขณะนี้จึงกล่าวได้ว่า source ถูกนับใน normalized balance ตามที่กำหนด แต่ยังกล่าวไม่ได้ว่าแต่ละ J คืออุปกรณ์ส่งงานจริงแบบหนึ่งโดยไม่ระบุพอร์ต/คู่แปร และยังไม่เอา friction loss ไปเรียกว่า heat กายภาพเมื่อ HIST-F dictionary ไม่ปิด

Convention เมื่ออ่าน thermal first law: งานเข้า = การเพิ่ม internal energy + heat ออกสู่ bath; heat ออกเป็นบวกใน Seifert 2012 Eq. (213) และ Seifert strong-coupling Eq. (1) ส่วน q ใน Talkner–Hänggi Eq. (34) และ Q ใน Horowitz–Esposito §II เป็น heat เข้าระบบ ความต่างของ sign นี้ไม่ใช่ข้อขัดแย้งทางฟิสิกส์ ต้องแปลง convention ก่อนเทียบ ไม่เปลี่ยน sign ของ ledger/โค้ดเดิมในรอบเอกสารนี้

sigma เป็น derived dissipation diagnostic; R เป็น retarded readout ของ sigma ไม่ใช่ physical state เพิ่มอีกก้อน ใน [§30.6](UET_THEORY_ARGUMENT.md) ค่าเฉลี่ย friction loss ที่ equilibrium ยังบวกได้ แต่ total entropy production ของ reference เป็นศูนย์ จึงไม่มีสิทธิ์เรียก sigma/R ว่า total entropy production จาก sign หรือชื่อเพียงอย่างเดียว ไม่ใช้คำว่า entropy production แทน uncertainty หรือ entropy ของ state ด้วย

source state, internal impact, carrier, receiver response, detector memory และ reported record ต้องแยกตาม boundary ที่ใช้ การที่ detector บันทึกได้ไม่ทำให้มันรู้ state ทั้งหมดหรือมี backaction สำคัญเสมอ และการที่ state ภายในย้อนเปลี่ยน response ได้ไม่บอกว่า detector เป็นที่เก็บความจำนั้น อ่านการแบ่งระบบร่วมกับ [มาตรฐาน 30](../topics/For%20Work/30_Calculation_and_Observation_Completeness_Standard.md) ไม่เพิ่ม detector model ในรอบนี้

### 3.7 Information-flow เป็นสะพานที่มีขอบเขต ไม่ใช่พจนานุกรมทั้งทฤษฎี

การแบ่ง C กับ Y=(Phi,Pi) ทำให้มีคำถามเรื่อง dependence และ information flow ที่ตรวจได้จาก generator แต่ MI คือปริมาณจาก joint distribution ไม่ใช่พลังงานที่สะสมเป็น “สารข้อมูล” และไม่บอกว่าร่องรอยทั้งหมดอยู่ที่ Phi ดู [§2.6](#foundation-information-flow) และ [ผล mixed generator ใน §30.8](UET_THEORY_ARGUMENT.md)

ผลเดิมแสดงทั้ง g=0 factorization ของ Gibbs reference และกรณี covariance เป็นศูนย์แต่ยัง dependence ได้ ไม่ใช้ correlation ตัวเดียวเป็น detector ของ information ทั้งหมด การเพิ่ม MI ไม่ใช่หลักฐาน learning, improvement หรือ persistence โดยลำพัง ส่วน Pi เป็น odd variable ภายใต้ time reversal จึงต้องเก็บ reversible current แยกจาก irreversible current ไม่ใช้ zero-current criterion ของ jump equilibrium ทับทั้ง phase space

การเก็บ signed state กับการอ่าน magnitude เป็นทางเลือกที่ยังคงไว้: การไม่แยกเครื่องหมายอาจเป็น readout หรือ coarse-graining เพิ่ม ไม่ใช่ invertible coordinate change ทั่วไป ต้องตรวจ state/preparation/observable ก่อนใช้สูตร entropy/MI ข้ามการอ่าน แต่รอบ L ยังไม่เลือกตัวอย่างหรือทำการตรวจเพิ่มเพื่อเลือกทางใด

**ผล L2:** ทางเชื่อมที่มีเหตุผลคือระบุ state/partition/measure และ thermal interpretation ก่อน ไม่ใช่เพิ่มพจน์เพื่อให้ชื่อ information ปรากฏในสมการ การรักษาความจำไว้กับการใช้ thermodynamics มาตรฐานทำร่วมกันได้ตามเงื่อนไข แต่ยังต้องแสดง joint correspondence ของ realization ที่เลือกจริง

<a id="uet-thermal-dictionary"></a>

## 4. L3 — เทียบกลับ C–Phi–Pi โดยไม่เปลี่ยนสมการ

### 4.1 สิ่งที่มีฐานแล้ว กับสิ่งที่ยังต้องกำหนด

ตารางนี้ใช้ [Argument §§14, 17–19, 30](UET_THEORY_ARGUMENT.md), [matter–space specification](../core/01_contracts/MATTER_SPACE_RESEARCH_SPEC.md), [ontology contract](../core/07_artifacts/correspondence/matter_space_ontology_contract.json) และ [joint thermal contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/joint_thermodynamic_completion.json) เป็นหลักฐานเดิม ไม่ใช่ข้อค้นพบจากการรันใหม่

| วัตถุใน realization | มีฐานถึงขั้นใด | เงื่อนไขเพิ่มก่อนอ่านแบบ physical thermodynamics | ช่องว่าง/ขอบเขตถ้อยคำ |
| --- | --- | --- | --- |
| C | normalized matter/structural state; มี C=s_C m comparator เฉพาะ §14 | ระบุ microstate partition, s_C, domain, N และ physical observable | ไม่ใช่ทุก C เป็น binary magnetization หรือ SI energy |
| Phi | independent signed effective response; retained-state influence ตาม coupling ที่ตรวจไว้ | ระบุสิ่งที่ Phi แทนและรายละเอียดภายในที่คงเหลือเมื่อบังคับ C/Phi | ไม่ใช่ legacy I ที่เปลี่ยนชื่อ, entropy, MI, metric หรือสารข้อมูลโดยอัตโนมัติ |
| Pi | state แทนอัตราการเปลี่ยน Phi; odd ใน thermal reference | เวลา/หน่วย/kinetic correspondence กับระบบที่เลือก; การเก็บ state ไม่ใช่ข้อพิสูจน์ microscopic momentum | ไม่ใช่ imaginary component หรือ antimatter จากเครื่องหมาย |
| Ω(C,Phi) | functional/landscape และ derivatives ของ realization; REF-E consistency แบบมีเงื่อนไข | สำหรับ HIST-F ต้องมี joint F/measure/T dictionary และขอบเขต approximation | เรียก normalized potential หรือ candidate coarse free energy ตาม lane; ยังไม่เรียก physical internal energy ทั้งระบบ |
| K_ref=τ Pi²/(2M_Phi) | positive normalized storage ใน ledger/thermal reference เดิม | physical scale, measure และ T-dependence ของ effective coefficients หากอ่านเป็น energy | รูป quadratic ไม่พิสูจน์ material kinetic energy หรือระบุมวลกายภาพให้เอง |
| μ_C, μ_Phi และ g | functional derivatives กับ internal coupling ที่กำหนดใน realization | แยก energetic/entropic origin ภายใต้ dictionary; physical units และ coefficient origins | ไม่ใช่ SI chemical potentials หรือ bath coupling เพียงเพราะใช้สัญลักษณ์คล้ายกัน |
| M_C, M_Phi, τ | coefficients ของ kinetics; noise–mobility relation ถูกประกาศเพิ่มใน REF-E | bath/process correspondence และ time-scale inputs ที่รองรับ | free energy และ FDT ไม่ derive ค่าหรือเลือก kinetics ให้เอกลักษณ์ |
| sigma | nonnegative deterministic dissipation diagnostic | ต้องแสดง entropy/heat correspondence แยก หากจะใช้คำทาง thermodynamics | finite-temperature friction loss ไม่ใช่ total entropy production; ใช้ข้อจำกัด equilibrium เดิม |
| R / I_trace | retarded diagnostic จาก sigma; ไม่มี feedback edge ใน ontology นี้ | readout/response kernel และ detector mapping ตาม protocol | ไม่เก็บผลอดีตทุกชนิด ไม่แทน state ทั้งหมด ไม่สร้างพลังงานหรือความจำก้อนใหม่ |
| Mutual information | derived functional ของ joint distribution C กับ (Phi,Pi) ใน reference | distribution/measure และการสังเกตพอรองรับค่าที่อ้าง; ใช้ flow decomposition ให้ตรง generator/parity | ไม่ใช่ I/Phi แบบ universal และไม่รับรอง causal learning/persistence |
| J และ observer record | ledger drive กับ output มีบทบาทประกาศไว้ตาม path | force-port work, physical preparation, measurement response/uncertainty และ backaction ที่เกี่ยวข้อง | การตรวจ symbol/record ไม่ใช่การวัด energy/heat จากธรรมชาติแล้ว |

**ข้อสรุปที่รับได้:** มี realization ที่ตรวจ balance และ comparator ได้จริง ไม่ใช่ไม่มีสิ่งใดใช้ต่อได้ แต่ความสอดคล้องของ normalized reference ไม่เติม microscopic meaning ให้ทุกแถว แผนที่นี้ทำให้เห็นว่าช่องว่างอยู่ที่ไหน แทนการให้ผู้เขียนป้องกันคำว่า information ทีละประโยค

**ข้อสรุปที่ยังรับไม่ได้:** joint Ω เป็น internal energy ของธรรมชาติแล้ว, MI เป็นเนื้อหาข้อมูลทั้งหมด, sigma เป็น entropy production, การมี retained response คือ learning หรือผล reference นี้ยืนยัน global open universe ทั้งหมด ข้อเสนอระดับจักรวาลยังอยู่ในภาพรวมและต้องมีการเชื่อมระดับเฉพาะของมัน ไม่ถูกยืนยันหรือปฏิเสธโดยการสัมผัส bath ของ subsystem

### 4.2 Documentation drift ที่พบ — บันทึก ไม่ซ่อมเงียบ ๆ

| ตำแหน่ง working-copy snapshot ที่ตรวจ | วินิจฉัยและข้อจำกัด | ทิศทางแก้หลังได้รับขอบเขตใหม่ |
| --- | --- | --- |
| [METHOD — Mechanism map](../topics/0.13_Thermodynamic_Bridge/METHOD.md), บรรทัด 84–89 ใน snapshot | ลูกศร Landauer lower bound → UET beta coupling → thermodynamic-gravity links อ่านเหมือน derivation ได้ แต่ [TRACE_RESEARCH_SPEC §5](../core/01_contracts/TRACE_RESEARCH_SPEC.md) จำกัดว่าเป็น external lower bound ไม่ derive dimensionless beta | กำกับชนิดลูกศรและ unresolved correspondence; ไม่ลบประวัติหรือแก้ coefficient |
| METHOD — Evidence matrix, บรรทัด 96 และ Assumptions บรรทัด 111 | “Landauer identity” กับ exact-constant calculation เป็น formula check ไม่ใช่ physical bridge proof; Assumptions ในไฟล์เดียวกันระบุ lower-bound consistency ไว้แล้ว จึงเป็นความเสี่ยงของ presentation ไม่ใช่หลักฐานว่า METHOD ทั้งฉบับอ้าง heat เท่ากับ bound | ทำให้ map/table สื่อขอบเขตเดียวกับ Assumptions และ controller ปัจจุบัน |
| METHOD — Joint G/r Reciprocal Dynamics และ Thermal Mass-Source Matching, บรรทัด 16–38 | มี material-specific entropy/free-energy dictionary ของ candidate lane อื่นอยู่จริง จึงไม่ควรกล่าวว่าโครงการไม่มีงานส่วนนี้เลย แต่ไม่ใช่ joint C/Phi/Pi correspondence ของ homogeneous reference โดยอัตโนมัติ | รักษา source/normalization/lane identity หากอนาคตเสนอ reuse; ตอนนี้ไม่ย้าย dictionary ข้าม lane |

ข้อควบคุมที่ **ยังสอดคล้อง** ต้องเก็บไว้ด้วย: ontology contract แยก Phi ออกจาก information และแยก R ออกจาก independent state อยู่แล้ว ส่วน joint contract ยังคง INCOMPLETE เพราะ physical dictionary เปิด ไม่ใช่เพราะผล FORMAL ใน §30 หายไป รอบ L ไม่แก้ METHOD, README, สมการ, contracts หรือ physics gates เพื่อทำให้ภาพดูปิด

### 4.3 ข้อวินิจฉัยที่ตัดสินได้ในรอบนี้

1. **สอดคล้องภายใต้เงื่อนไข:** การใช้ thermodynamic information เป็นฐานตรวจ realization มีเส้นทางตามวรรณกรรม ไม่ได้จำเป็นต้องสร้าง pure mathematics ใหม่หรือ invent energy-information identity ก่อน
2. **ต้องเพิ่มสมมติฐาน/ที่มา:** HIST-F ต้องมี conditional state/measure/T information; การเลือก bath และ conditional equilibration เป็นสิ่งเพิ่ม ไม่ใช่ผลที่ได้จาก polynomial Ω ลำพัง
3. **เทียบเท่าคู่เทียบในขอบเขตเดิม:** REF-E ยังเป็น standard mixed-Langevin equivalence ตาม §30.10 วรรณกรรมไม่ได้เพิ่ม UET-specific restriction ให้ ต้องยอมรับผลนี้แทนการเพิ่มเทอมหลบ comparator
4. **ยังตัดสินไม่ได้ทางกายภาพ:** จะเลือก reading ใดให้ C/Phi/Pi ของระบบจริง และข้อมูล/ความจำในเจตนาผู้เขียนสัมพันธ์กับ distribution/structure ใด; ไม่บังคับเลือก MI, signed หรือ magnitude ในรอบนี้
5. **ไม่ให้ขยายข้ออ้าง:** ผลแยก sigma/entropy และ underdetermination เดิมยังมีผล ไม่เรียก literature agreement ว่า physical validation หรือการยืนยัน novelty

ไม่มี contradiction ใหม่ของ Core ที่พิสูจน์ด้วยการคำนวณในรอบ L เพราะไม่ได้เปิด calculation path ใหม่ ข้อขัดข้องที่ชี้เป็นเรื่อง correspondence และความกำกวมของการนำเสนอ ไม่ใช่คำตัดสินว่าทุกสมการผิดหรือทุกหลักคิดผู้เขียนถูก

<a id="before-microscopic-design"></a>

## 5. ก่อนออกแบบตัวอย่างจุลภาค — ต้องตอบอะไร และใครรับผิดชอบ

### 5.1 การตัดสินใจขั้นต่ำ ไม่ใช่รายการให้ผู้เขียนคำนวณเอง

| ต้องระบุให้ได้ก่อน | เหตุใดเปลี่ยนข้อสรุปได้ | ผู้เขียนต้องช่วยตรงไหน / งานของผู้วิจัย |
| --- | --- | --- |
| โจทย์แกนและ reading ของ Ω ที่จะตรวจในตัวอย่างหนึ่ง | ทดสอบ reference consistency กับกู้ physical thermal dictionary เป็นคนละงาน | ผู้เขียนทบทวนว่าโจทย์แทนเจตนาหรือไม่; ผู้วิจัยแสดง alternatives/ขอบเขต ไม่เลือกแทนเงียบ ๆ |
| Retained state กับ eliminated degrees of freedom | ตัด state ที่เก็บประวัติอาจทำให้ response/closure หาย | ผู้วิจัยเสนอ partition พร้อมเหตุผล; ผู้เขียนตรวจความหมาย memory/information ไม่ต้องตรวจ algebra |
| State counting, measure, degeneracy, domain และ N | เปลี่ยน entropy/weighting และ normalization | เป็นหน้าที่ผู้วิจัย/ผู้เชี่ยวชาญ statistical mechanics ต้องให้ที่มา ไม่ผลักให้ผู้เขียนเดา |
| T-dependence ของ coefficients/coupling/storage และ physical scales | ต้องใช้แยก F, S_int, U; one-T fit ไม่พอ | ต้องมี derivation หรือ independent inputs; unknown ไม่ตั้งเป็นศูนย์ |
| Bath coupling, preparation และเวลาที่เกี่ยวข้อง | เลือกได้หรือไม่ได้ว่าจะใช้ conditional equilibrium/HMF | ผู้วิจัยระบุสมมติฐานและหลักฐาน ไม่ใช้ “ระบบเปิด” แทนข้อมูลทั้งหมด |
| Interaction accounting, source ports และ heat convention | ความสอดคล้องรวมไม่รับรองพลังงานย่อยหรือ heat ที่เครื่องวัดได้ | ผู้วิจัยให้ operational definition และเทียบ convention อย่างชัด |
| Preparation/readout: signed และ magnitude | readout ที่สูญเครื่องหมายอาจไม่แทน state เดียวกัน | ตามคำตอบเดิมตรวจทั้งสองแบบไว้ก่อน; ยังไม่กำหนด interpretation ทั้งทฤษฎี |
| Comparator กับข้ออ้างที่ผลอาจแยกได้ | กลไกที่มีจริงอาจเทียบเท่าทฤษฎีเดิม | ผู้วิจัยรายงาน equivalence ได้ ไม่ต้องบังคับให้ผลสนับสนุนฟิสิกส์ใหม่ |

ถ้ายังตอบขั้นต่ำไม่ได้ ผลที่ถูกต้องคือเขียน prerequisite เฉพาะจุด ไม่ใช่เปิดการคำนวณแล้วค่อยตั้งชื่อ state ภายหลัง หรือขอข้อมูลวัสดุเพิ่มโดยยังไม่รู้ว่าจะเติม dictionary ตรงไหน การทบทวนของผู้เขียนยืนยันเจตนา ไม่ใช่ proof ทางฟิสิกส์

### 5.2 คำถามเฉพาะสำหรับผู้เชี่ยวชาญ — เตรียมไว้ ยังไม่ติดต่อ

- **Statistical mechanics / coarse-graining:** จาก [§14 และ §30.4](UET_THEORY_ARGUMENT.md) กับ §3.5 ของรายงานนี้ joint constrained measure ที่ต้องเพิ่มต้องรักษาอะไร จึงไม่ซ้ำ degeneracy และไม่ย้าย finite binary approximation ไปเป็น full joint process? ผลตรวจอาจเป็น matching แบบมี limit, mismatch หรือ underdetermination ได้
- **Stochastic thermodynamics:** ด้วย REF-E/HIST-F alternatives และ source-port distinction ใน [§§18–19/30](UET_THEORY_ARGUMENT.md) เงื่อนไขใดพอให้ระบุ physical heat? ต้องรู้ T-dependence, preparation หรือ interaction-energy assignment อะไรเพิ่ม? ไม่ขอรับรองทั้ง UET
- **Strong-coupling thermodynamics:** หากภายหลังเลือก bath lane นี้ ข้อมูลใดแก้ normalization ambiguity ของ HMF ได้ และหลัก operational ใดเลือก trajectory assignment? โปรดแยก equilibrium construction, initial conditional state และ evolved density ไม่ถือว่า consistency เพียงอย่างเดียวตัดสินทุกข้อ
- **Information theory / measurement:** retained state, derived MI และ sigma/R ใน [§30.8](UET_THEORY_ARGUMENT.md) ตอบคนละคำถามอย่างไร และ readout แบบ signed/magnitude เข้าถึง joint distribution ได้แค่ไหน? การพบ dependence ไม่ใช่หลักฐาน learning อัตโนมัติ

ชุดส่งตรวจในอนาคตควรมีเฉพาะนิยาม state/measure/หน่วย, imported assumptions, ผลเดิมที่เกี่ยวข้อง และคำถามที่ตัดสินได้ การเห็นด้วยกับ narrative หรือจำนวน tests ไม่ใช้แทนคำตอบเหล่านี้ ไม่มีอีเมล นัดหมาย หรือการส่งข้อมูลออกในรอบ L

### 5.3 หนึ่งโจทย์ถัดไปที่เสนอ และจุดหยุดของรอบนี้

เสนอให้รอบถัดไปทำ **joint thermal-dictionary feasibility ของ realization เดิมหนึ่งขอบเขต** หลังผู้เขียนอ่านรายงานนี้: ให้ข้อเสนอ state–measure–temperature correspondence จาก comparator ที่มีที่มา พร้อมเหตุผลว่าจำเป็นต้องเก็บหรือรวมรายละเอียดใดออก แล้วค่อยเลือกว่าจะเปิด microscopic calculation หรือไม่

นี่เป็นข้อเสนอขั้นงาน ไม่ใช่การเลือก microscopic model หรือเพิ่ม subsystem แล้ว ผลรับได้คือ **มี dictionary ภายใต้เงื่อนไข / มีได้หลายแบบและต้องมี independent restriction / จับคู่ไม่ได้ในขอบเขตเดิม / เทียบเท่ามาตรฐาน** ต้องไม่กำหนดผลล่วงหน้าว่า UET ใหม่กว่า หากสองความพยายามไม่เพิ่มหลักฐานที่เปลี่ยนคำตัดสิน ให้จบด้วย prerequisite ไม่เพิ่ม state/term เพื่อรักษากิจกรรม

**รอบ L จบที่ synthesis นี้:** ไม่ต้องรอ correspondence ปิด แต่ยังไม่เริ่มโจทย์ถัดไป ไม่กลับไปทำ beam/He-4/graphite หรือข้อมูลจักรวาลอัตโนมัติ ไม่เปลี่ยน claim/gate และไม่ลดข้อเสนอผู้เขียนให้เหลือ thermal subsystem ตัวเดียว

## 6. ขอบเขตการตรวจ ความปลอดภัย และการส่งต่อ

ตรวจเฉพาะ corpus ใน §2 กับ controlling UET evidence ที่อ้าง ไม่กล่าวว่าเป็น systematic review ของ literature ทั้งสาขาหรือทุก revision และไม่รับรองว่ามี microscopic theory ที่ใช้ได้กับ UET รออยู่แล้ว ภาษาไทยและศัพท์อังกฤษใช้ช่วยแยกความหมาย ไม่ใช่การประกาศเอกลักษณ์ของสัญลักษณ์ข้าม paper

หลักฐาน R0–R3 และ hashes เดิมคงไว้ การเพิ่มรายงานแยกนี้ไม่เปลี่ยน scientific inputs/model/measurement operator จึงไม่สร้าง calculation contract หรือ regenerate artifact เดิม เอกสารอ้าง public primary sources และสรุปเจตนาที่บันทึกใน Argument แล้วโดยไม่คัด private conversation หรือต้นฉบับเฉพาะเครื่อง ไม่ถือว่า local commit เท่ากับ public main

METHOD snapshot ที่ใช้วินิจฉัยมี canonical-text SHA-256 `431d805567e44ab1e62a3cd7f53488abd5d9d9b9a8478c451e6af1066e658054` ต่างจาก blob ใน `81ad20f12` จึงเป็น working evidence ไม่กล่าวว่า drift ทุกจุดอยู่บน public main และไม่คัดเนื้อหาไฟล์ทั้งฉบับเข้ารายงาน ส่วน references ที่มีเพียง local checkout ยังต้องตรวจขอบเขตเผยแพร่ก่อน publish จริง

ผล read-only completeness ทั้ง `--check` และ `--changed 81ad20f12d398e32e62052588dadf61ea96ce353 --check` ออกสำเร็จ: 17 contracts / 122 routes / 0 errors มี legacy routes และ coverage gaps เดิมคงอยู่ ตัวเลขนี้เป็นผลตรวจโครงสร้าง ไม่ใช่คะแนนความถูกต้องของ UET และไม่ทำให้ INCOMPLETE contracts หรือ physics gates ผ่าน รายละเอียด document/preservation QA บันทึกตามที่รันจริงใน entry ปิดรอบ L ของ [Topic 13 UPDATE_LOG](../topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md) และ [WORK_LEDGER วันที่ 24 ตุลาคม 2026](../../WORK_LEDGER/2026/2026-10-24.md)

<a id="thermal-dictionary-followup"></a>

## 7. ภาคต่อ — รายละเอียดที่รวมออกอยู่ตรงไหนในงานที่มีแล้ว

24 ตุลาคม 2026 หลังผู้เขียนขอให้เจาะเงื่อนไข Seifert §9.2 ต่ออย่างละเอียด §§1–6 คงเป็นผลรอบ L เดิม ส่วนนี้เป็น feasibility/source audit เพิ่ม ไม่เลือก microscopic model ใหม่ ไม่เพิ่ม subsystem และไม่เริ่ม calculation path ใหม่

### 7.1 คำถาม ขอบเขต และหลักฐานที่ล็อก

**คำถามเดียว:** มีหลักฐานเดิมส่วนใดระบุ eliminated degrees of freedom และ temperature dependence ได้จริง และส่วนใดนำมาปิด joint C–Phi–Pi thermal dictionary ไม่ได้โดยปราศจากสมมติฐานเพิ่ม?

- **ฐาน:** local commit `8e38f78c2cb84f24c94aa1b4e2f76b693c2f62e5`, branch เดิม ไม่มี upstream; index ว่างและมีงานค้างอื่น 463 รายการ ส่วนเก่าของรายงาน/ล็อกไม่ถูกแก้ย้อนหลัง ไม่อ้างว่า SHA นี้เป็น public main
- **มีแล้ว:** C-side state counting ใน Argument §14, joint reference และ underdetermination ใน §30, Gaussian mass-source matching และ reciprocal thermal dynamics ในอีก lane
- **ยังขาด/ผู้ควบคุม:** `intrinsic-entropy-correspondence` ใน joint contract เดิม โดยเฉพาะ joint partition/measure, thermal coefficient family และ physical map ไม่สร้าง blocker registry หรือ status ใหม่
- **ทำอะไร/ทำไม:** ตามนิยามใน source/spec/code กับผลเก่า ก่อนบอกว่าต้องสร้างอะไรเพิ่ม เพื่อแยกช่องว่างจริงจากงานที่มีอยู่แล้วแต่คนละขอบเขต
- **ขอบเขตระบบ:** retained C/Phi/Pi ต่างจากรายละเอียดจุลภาคภายใน, bath และ detector; ไม่ตัด Phi/Pi เป็น fast state หรือเพิ่ม hidden state แทนผู้เขียน ทั้ง signed/magnitude alternatives ยังคงอยู่
- **ผลรับได้/หยุด:** reuse แบบมีเงื่อนไข, ไม่รองรับ direct substitution หรือยังไม่ระบุครบ; ไม่ฝืนให้ได้ dictionary ใหม่ ถ้าต้องเลือก joint microscopic ensemble หรือคำนวณใหม่ ให้หยุดที่ prerequisite ที่เฉพาะเจาะจง
- **คำถามผู้ตรวจ:** state/measure/thermal derivatives ที่สอง lane ใช้อยู่เป็นวัตถุเดียวกันจริงหรือเพียงใช้คำ/สัญลักษณ์คล้ายกัน? นี่คือการตรวจรอยต่อ ไม่ใช่ขอให้รับรอง UET ทั้งหมด

### 7.2 Seifert ต้องการ “รายละเอียด” แบบใด

ใน [Seifert §§9.2.1–9.2.4, Eqs. (206)–(222)](https://arxiv.org/html/1205.4176) ต้องมีการจัด microstates ลง coarse classes, conditional equilibrium ภายในแต่ละ class และความรู้ด้านอุณหภูมิของ constrained free energy เพื่อเชื่อมกับ intrinsic entropy/internal energy และ heat การรู้เพียง coarse trajectory ไม่ได้แสดงว่าทำ construction นี้แล้ว

ต้องระวังสัญลักษณ์: **Φ(ξ,λ) ใน paper คือ microscopic potential energy ไม่ใช่ Phi ของ UET** ส่วน x คือ retained mesoscopic coordinates จะจับคู่ x กับ (C,Phi) ได้ต้องมี mapping ไม่ใช่เพราะเขียนตัวอักษรเหมือนกัน และ ξ ไม่ใช่ข้อมูล detector ที่มองไม่เห็นเฉย ๆ แต่เป็น physical degrees of freedom ใน construction นั้น

นำมาใช้กับช่องว่างของเรา ต้องตอบเจ็ดข้อโดยไม่ประดิษฐ์รายละเอียดขึ้นเติม:

1. **อะไรคงไว้:** C/Phi/Pi แทน physical state ชนิดใด และ coarse class ถูกกำหนดอย่างไร
2. **อะไรรวมออก:** microstates ใดมี coarse label เดียวกัน; ไม่เรียกทุกสิ่งที่ไม่ได้เขียนว่า bath
3. **นับอย่างไร:** probability/measure, degeneracy, constraints, N และ volume ที่ใช้
4. **พลังงานต้นทางคืออะไร:** conditional weighting รับจาก Hamiltonian หรือ effective construction ใด รวม interactions ตรงไหน
5. **ทำไมใช้ equilibrium ภายในได้:** ต้องมี relaxation/preparation/driving scope ไม่ใช่สรุปจากค่า τ_Phi เป็นบวก
6. **อุณหภูมิเปลี่ยนแล้วอะไรเปลี่ยน:** ทั้ง Boltzmann weights, effective coefficients และ normalization โดยล็อก physical controls ให้ถูก
7. **heat/work หมายถึงอะไร:** thermal dictionary ต้องเข้ากับ source ports และ boundary ที่นิยาม ไม่ใช่อ่านจากการลด Ω อย่างเดียว

ไม่จำเป็นต้องให้ coarse variables ทั้งหมดอยู่ equilibrium: รายละเอียดภายในอาจ thermalize ขณะที่ retained distribution ยังไม่สมดุล แต่ต้องมีเหตุผลให้ใช้ separation นั้น ดู [Esposito §§III.1–III.2 และ IV.1](https://arxiv.org/html/1112.5410) fast stationary state ที่ถูกหลาย reservoir ขับไม่จำเป็นต้องเป็น thermal equilibrium และ τ_Phi ใน Core ไม่ใช่หลักฐานวัด relaxation ของรายละเอียดที่ยังไม่ระบุ

### 7.3 สี่ชุดงานเดิมตอบต่างส่วนกัน

| ชุดหลักฐานที่ตรวจ | อะไรถูกคงไว้/รวมออกจริงตามขอบเขตเดิม | ใช้ต่อได้อะไร | ยังไม่ตามมา |
| --- | --- | --- | --- |
| [Argument §14](UET_THEORY_ARGUMENT.md), §§14.2–14.4 | เก็บ m หรือ C=s_C m; นับ binary configurations ที่ให้ population contrast เดียวกันใน mean-field comparator; Phi ยังเป็น response coordinate ที่กำหนดเพิ่ม | มี mixing entropy และ local quartic correspondence ของ C พร้อม N/domain/approximation limits | ไม่ได้ derive microstates หรือ intrinsic entropy ของ Phi/Pi; f_Phi ยืมจาก prototype และ affine j(Phi) เป็น constitutive choice |
| [Core matter–space implementation](../core/02_equations/matter_space/uet_matter_space.py), MatterSpaceConfig และ matter_space_free_energy | โค้ดเก็บ C/Phi/Pi และ normalized coefficients ไม่ได้รวม fast microstates ใหม่ระหว่างรัน | บอก functional, derivatives, kinetics และ ledger ที่ใช้จริง; config ระบุ defaults เป็น benchmark controls และปฏิเสธ SI | ไม่มี physical T parameter หรือ microscopic conditional measure ใน interface นี้ ไม่ใช่ proof ว่า intrinsic entropy เป็นศูนย์ |
| [Joint reference producer](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Joint_Thermodynamic_Completion.py), reference()/coarse_free_energy_residuals() | ประกาศ one-bath stochastic reference เพิ่มเหนือ deterministic Core; ไม่มี explicit bath microstates ถูก derive ใน producer | REF-E consistency และ HIST-F witness เดิม; เห็นว่า Θ เป็น bath-energy scale แยกจาก symbolic coefficients | FDT choice ไม่ใช่ microscopic bath elimination หรือกฎ T-dependence ของ material coefficients |
| [Thermal mass-source matching specification](../core/03_lanes/topic13_support/T13_MATTER_STRAIN_SUSCEPTIBILITY_MATCH.md) และ [implementation](../core/03_lanes/thermal/uet_matter_strain_susceptibility.py), thermal_moments()/thermal_matching() | Gaussian thermal modes ของ canonical O(2) matter doublet บน normal branch; response displacement/strain เป็น sources ตามที่ประกาศ | มี F_th, thermal entropy/heat capacity และ direct Phi–entropy coefficient ใน conditional lane จริง | thermal increment ไม่ใช่ full joint Ω, χ ไม่ได้ระบุว่าเท่ากับ C และไม่ใช่ graphite phonon identity; ไม่มี vacuum/interaction/transport/physical-source closure |

**ผลที่แคบลงจากรอบ L:** ไม่ควรพูดว่าทั้งโครงการยังไม่มีที่มาของ entropy หรือไม่เคยเชื่อม Phi กับ thermal response แต่ก็ยังไม่พบเหตุให้ถือว่างานทั้งสี่เป็น thermal dictionary เดียวกัน การตรวจนี้ระบุว่า “มีชิ้นไหนแล้ว” และปฏิเสธการนำมาต่อกันด้วยชื่อเทอมอย่างเดียว ไม่ใช่ตัดสินว่าไม่มีทางเชื่อมในอนาคต

### 7.4 กรณีเดิมที่ช่วยอธิบาย: entropy เกี่ยวกับ Phi ได้โดย Phi ไม่ใช่ entropy

ใน mass-source lane เดิม การเปลี่ยน response displacement เปลี่ยน mass parameter ของ χ modes ตาม source ที่ประกาศ จึงเปลี่ยน thermal population และ entropy contribution ได้ นี่ไม่ใช่การประกาศว่า Phi เป็น temperature หรือเป็นจำนวน bits และยังไม่ใช่ derivation ว่า Phi เป็น information ทั้งทฤษฎี

ผลเดิมใน specification ให้ G และ r จาก free energy เดียวกัน โดย r เป็น coefficient ของการเปลี่ยน entropy ตาม Phi ใน local expansion ไม่ใช่ entropy ทั้งหมดของ Phi เอง ส่วน `thermal_moments()['entropy']` เป็น entropy ของ thermal modes ใน construction นั้น ไม่ใช่ S_int ของทุก degree of freedom ใน C/Phi/Pi

สัญลักษณ์อุณหภูมิก็ไม่ใช่ตัวเดียวกันทุกไฟล์: θ ใน C-side comparator เป็น normalized k_B T/E_* ส่วน Θ เป็น bath scale ของ joint reference และ theta ใน reciprocal material dynamics เป็น temperature perturbation รอบ reference T การเชื่อมต้องตามนิยาม/หน่วย ไม่ใช้ชื่อ theta เหมือนกันแทน conversion

[Reciprocal thermal dynamics specification](../core/03_lanes/topic13_support/T13_RECIPROCAL_THERMAL_DYNAMICS.md), “Positive availability and reciprocal cancellation” ยังแสดงว่า r cross term ยกเลิกออกจาก quadratic availability หลัง Legendre transform ทั้งที่ r ยังอยู่ใน entropy และ reciprocal equations ดังนั้น **ไม่เห็นเทอม entropy ชัดใน ledger ไม่ได้พิสูจน์ว่า entropy นั้นไม่มี** ต้องตามชนิด potential และ transformation ที่ใช้ ไม่เดาจากหน้าตาสมการ

ผลนี้เป็น local quadratic material candidate กับ linear entropy/quadratic availability budget ไม่ใช่ nonlinear total SI first law และไม่ถูกย้ายมาเปลี่ยน Ω ของ homogeneous pilot รอบนี้ ไม่รัน integration, quadrature, finite differences หรือ verifier เดิมซ้ำ

### 7.5 เงื่อนไขที่ยังห้ามนำคำตอบข้าม lane

- **χ กับ C:** ชื่อ matter และรูป coupling ที่คล้ายกันไม่ระบุ coordinate map, symmetry, phase/degeneracy หรือ measure ให้เอง สอง real χ components ไม่ใช่ binary +/- states ของ §14 และไม่ใช่จำนวนบิตสองบิต
- **ไม่มี fixed-C conditioning ใน interface นี้:** `thermal_moments(T,mass_squared)` กับ `deformed_free_energy(T,sources,delta_phi,strain)` ยังไม่รับ C หรือกฎจัด χ microstates ลง coarse classes ของ C จึงไม่ถือว่าฟังก์ชันนี้เป็น joint constrained F(C,Phi,T) แล้ว พารามิเตอร์ x=mass_squared ของ lane นี้ไม่ใช่ coarse x ใน Seifert และไม่ใช่ population contrast m ใน §14
- **หน่วย/ขนาดระบบ:** F_th ใน Gaussian lane เป็น natural-unit density มิติ E^4; entropy density มิติ E^3 ส่วน Ω ของ joint pilot เป็น normalized unit-cell object ต้องมี volume/energy/field normalization ก่อนเทียบ ไม่คูณ N หรือ degeneracy ซ้ำ
- **สิ่งที่ขาดจาก thermal increment:** normal branch χ=0, positive mass squared, fixed measure/kinetic normalization และ Gaussian approximation ไม่ครอบคลุม condensate, interaction loops, vacuum counterterms หรือ T-dependent resummation ที่ไม่ได้รวมไว้
- **สมดุลทางสถิติไม่ใช่หลักฐานเวลา:** การมี equilibrium F_th ยังไม่แสดงว่า χ modes thermalize เร็วกว่า retained C/Phi หรือ driving ในระบบจริง ต้องมี kinetic/time-scale correspondence หากจะใช้ conditional-equilibrium elimination กับ dynamics นั้น
- **thermal modes ไม่ใช่ bath-noise derivation แล้ว:** χ determinant ไม่ได้ derive Gaussian white bath ของ §30, HMF bath subtraction หรือ mobility/damping/kernel ของ Core; การเชื่อม fluctuation/transport ต้องมีที่มาเพิ่ม ไม่อนุมานจากการมี T ในสูตร
- **การนับซ้ำ:** ถ้า material coefficients รวม thermal modes นี้แล้ว จะบวก increments ซ้ำไม่ได้; การรวม C-side state-counting กับ χ determinant ก็ต้องมี joint state accounting ก่อน ไม่ถือว่าเป็น independent factors เพราะอยู่คนละไฟล์
- **พจน์ต้องมาด้วยกัน:** ห้ามดึง G เพียงตัวเดียวมาใช้แล้วละ r กับ companion Hessian terms หากอ้างผล matching ทั้งชุด และผลดังกล่าวยังไม่ derive mobilities/damping ของ Core

### 7.6 Identity และขอบเขตการใช้ผลเก่า

ตรวจ source/spec/artifact ที่เกี่ยวข้องเก้ารายการเทียบ local baseline `8e38f78c2cb84f24c94aa1b4e2f76b693c2f62e5`: canonical-text identities ตรงกับ commit นี้ ไม่เปลี่ยน source เหล่านั้น ส่วน [mass-source artifact](../core/07_artifacts/topic13/t13_matter_strain_susceptibility_matching_audit.json) กับ [reciprocal artifact](../core/07_artifacts/topic13/t13_reciprocal_thermal_dynamics_audit.json) เป็นผลที่บันทึกไว้เดิม ไม่ใช่ผลรันวันนี้

ตาม legacy paths ในสอง artifacts ผ่าน [core_paths.canonical_existing_path](../core/core_paths.py) แล้วพบครบทั้ง 18 identity entries: 8 raw hashes ตรง, อีก 8 ตรงเมื่อ normalize CRLF/CR เป็น LF เท่านั้น และ 2 producer hashes ไม่ตรงแม้ normalize แล้ว ไม่เรียกสองรายการหลังว่ามี current producer identity ครบ และไม่แก้ artifact ให้ดูสด รายการ 18 นี้มี source ซ้ำระหว่าง artifacts ไม่ใช่ 18 การทดลองหรือ 18 source ที่ต่างกัน

ค่า raw hash ของ generator เดิมไม่ใช่ policy text hash แบบใหม่ การตรงหลัง normalize เป็นหลักฐานเรื่องเนื้อหาข้อความ ไม่ใช่การอ้างว่า raw identity ตรง การอ่าน source/spec ที่ unchanged ใช้อธิบาย construction ได้ แต่ถ้าจะนำ numerical acceptance ของ legacy artifact มาเป็นผล current-run ใหม่ ต้องจัดการ provenance/producer review แยกก่อน; รอบนี้ไม่ต้องทำเช่นนั้นเพื่ออ่านความหมาย และไม่ใช้ปัญหา path/hash ตัดสินว่าผลวิทยาศาสตร์ผิด

Controlling blockers ของ legacy lanes ยังเป็น `physical_material_mass_source_and_vacuum_matching_missing` และ `physical_material_and_preparation_match_missing`; ไม่ทับ `intrinsic-entropy-correspondence` ของ joint reference และไม่เลื่อน physics gates จากการตรวจเอกสารนี้

<a id="temperature-dependency-audit"></a>

## 8. อุณหภูมิเข้ามาตรงไหน — ตรวจตามเทอม ไม่เดาจากชื่อฟังก์ชัน

### 8.1 “ค่าคงที่ตอนรัน” ไม่เท่ากับ “ไม่ขึ้นกับ T ทางกายภาพ”

MatterSpaceConfig เก็บตัวเลขสำหรับหนึ่ง realization และไม่มี physical-temperature argument ส่วน `reference()` แยก Θ ออกจาก a_C, b_C, a_Phi, b_Phi, g, M_C, M_Phi, τ อย่างชัดเจน นี่คือขอบเขตที่ implementation รองรับ ไม่ใช่หลักฐานว่า coefficients ของวัสดุไม่พึ่ง T หรือว่า entropy เป็นศูนย์

ถ้าใช้ REF-E เป็น T-independent reference potential ตามนิยาม การคง coefficients แล้วเปลี่ยน bath-energy scale เป็น family ของแบบจำลอง reference ที่ตั้งได้ แต่ถ้าอ้าง HIST-F ว่า Ω เป็น coarse free energy ของระบบเดิม ต้องมีเหตุผลว่าฟังก์ชัน coefficients, state normalization และ measure เปลี่ยนกับ physical T อย่างไร การเลือกสอง reading นี้ต้องไม่สลับกลางข้ออ้าง

### 8.2 Temperature-dependency sheet ของสิ่งที่มีอยู่

| เทอม/ข้อมูล | หลักฐานเดิมบอกอะไร | อะไรยังไม่กำหนด และทำไมสำคัญ |
| --- | --- | --- |
| a_C, b_C | §14.4 ให้ a_C=(θ−j_0)/s_C² และ b_C=θ/(3s_C⁴) ภายใต้ local mean-field matching | เป็น conditional correspondence ไม่ใช่ measured thermal family; ต้องระบุ E_*, s_C, j_0 และสิ่งที่ล็อกเมื่อเปลี่ยน T จึงตาม entropy contribution ได้ |
| g | §14 ใช้ g=γ/s_C² จาก affine j(Phi) ที่ผู้ตรวจเลือก | ต้องรู้ origin/T-dependence ของ γ และ normalization; constant g ใน fixture ไม่ตัดสินว่า physical coupling เป็น energetic หรือ entropic ทั้งหมด |
| a_Phi, b_Phi และ f_Phi | §14 ยืม response free-energy sector ของ prototype; Core เก็บ polynomial coefficients | ยังไม่มี full joint microstate counting ของ sector นี้; thermal mass-source increment อีก lane ไม่กำหนด total a_Phi(T), b_Phi(T) ของ realization นี้ให้เอง |
| κ_C, κ_Phi และ spatial measure | Core มี gradient terms แต่ joint pilot เป็น homogeneous unit cell | spatial thermal dictionary ไม่ได้ถูกตรวจใน pilot; ไม่ใช้การไม่ปรากฏของ gradient เป็นคำตอบเรื่อง entropy ของ spatial modes หรือ continuum cutoff |
| K_ref=τ Pi²/(2M_Phi) | positive storage ใน normalized reference; Pi เป็น rate coordinate | ต้องระบุ physical variable ที่ล็อกในการทำ T derivative และ normalization; fixed Pi กับ fixed physical canonical momentum ไม่ใช่เงื่อนไขเดียวกันโดยอัตโนมัติ |
| M_C, M_Phi, τ และ noise | positivity/drift/FDT relation ของ REF-E ถูกประกาศไว้ | ไม่ได้ derive mobilities หรือ temperature laws; M_Phi กับ τ ยังเข้าพจน์ storage จึงแยกทิ้งจาก thermal interpretation ทั้งหมดไม่ได้ |
| E_*, s_C, N, volume และ Θ | §§14/17 และ joint contract ให้ conditional scale conventions | หาก scale หรือ state/volume เปลี่ยนเมื่อเปลี่ยน T ต้องตามการแปลงนั้น ไม่เอา normalized derivative ไปเรียก SI entropy; ต้องล็อก ensemble/physical controls ก่อน |
| Additive reference ของ free energy | gradient/drift ที่ T เดียวไม่บอก normalization นี้ | T-dependent reference เกี่ยวกับ absolute entropy/U; แต่ term ที่ขึ้นกับ T อย่างเดียวและไม่ขึ้นกับ state ยกเลิกใน state differences ของ isothermal fixed-control process ได้ ไม่อ้างว่าความกำกวมทุกแบบทำให้ heat ทุกชนิดไม่ทราบเสมอ |

ตารางนี้อ่านจากนิยาม/ผลเดิม ไม่ได้ fit functions ของ T หรือคำนวณ derivatives ใหม่ การให้ numerical fixture คงที่เป็นวิธีล็อก benchmark ที่ถูกต้องได้ แต่ไม่ใช่ derivation ของ material T-dependence และการจับคู่ที่ T จุดเดียวไม่ใช่หลักฐานการจับคู่ตลอดช่วงอุณหภูมิ

### 8.3 เหตุใดต้องบอกว่า derivative ล็อกอะไร

เมื่อใช้ S_int=-∂F/∂T ต้องบอกว่า fixed physical retained state, external control, particle constraint/ensemble และ reference measure คืออะไร ไม่ใช่ถือว่าตัวเลข normalized ทุกตัวถูกล็อกแล้วเท่ากับ physical controls ถูกล็อก เช่น C=s_C m ต้องรู้ว่า scale s_C ถูกกำหนดอย่างไร; fixed-volume field density ไม่ใช่ total energy ของตัวอย่างที่ volume เปลี่ยน

ใน Gaussian implementation `thermal_moments(temperature,mass_squared)` ให้ thermal derivatives/entropy ที่ fixed mass_squared ตาม construction ของ source probe ถ้าใน realization อื่น mass parameter, kinetic normalization หรือ measure มี T-dependence เพิ่ม จะใช้ output entropy เดิมเป็น total thermal derivative โดยไม่ทบทวนไม่ได้ คำถามนี้ไม่แก้ด้วยการเปลี่ยนตัวเลข T หลายค่าอย่างเดียว

สำหรับ state ที่เก็บ Pi ต้องรู้ physical conjugate-variable/measure ก่อนทำ derivative ข้าม thermal family การเป็น odd variable บอก time-reversal parity แต่ไม่ใช่หลักฐานว่า Pi มีหน่วยและ normalization ของ physical canonical momentum แล้ว รอบนี้ไม่เปลี่ยน Pi ไม่ทำ coordinate reduction หรือคำนวณ Jacobian ใหม่

### 8.4 Intrinsic entropy เป็นศูนย์ได้เมื่อไร และไม่ได้แปลว่าอะไร

การกำหนด reference ที่ไม่มี relevant internal degeneracy เป็นสมมติฐานได้ ไม่จำเป็นต้องใส่ hidden entropy เพิ่มทุกครั้ง แต่ถ้า reading เป็น coarse free energy ต้องมีเหตุผลให้ entropy ที่รวมออกมีค่าตามที่อ้าง ไม่ตั้งเป็นศูนย์เพราะ source ยังไม่ให้มา

**ไม่มี intrinsic entropy ที่เพิ่มจากการรวมออก ไม่เท่ากับไม่มี entropy ของ distribution บน retained states** แม้ reference energy ไม่พึ่ง T, thermal probability distribution ยังขึ้นกับ bath scale ได้อยู่ และ entropy production ก็เป็นอีกปริมาณหนึ่ง ไม่แปลว่าค่า sigma หรือ R คือ entropy เหล่านั้นตามไปด้วย ดู [Argument §30.6–30.8](UET_THEORY_ARGUMENT.md)

### 8.5 F(T) หลายอุณหภูมิ กับการขับ T(t) เป็นคนละโจทย์

การรู้ thermal family ช่วยตรวจ derivative แต่การ ramp bath temperature ในเวลาจริงไม่ใช่โจทย์ isothermal เดิมของ §30 หรือ Seifert §9.2.2 โดยอัตโนมัติ ต้องทบทวน state/parameters, work/heat convention และ stochastic assumptions สำหรับ protocol ที่เปลี่ยน ไม่แทน Θ(t) ใน reference แล้วประกาศว่าได้ physical heating/cooling law ครบ

การวัด normalized equilibrium distributions หลาย T อาจให้ข้อมูลเพิ่มเกี่ยวกับ relative landscape แต่ไม่รับรอง absolute thermal normalization/HMF reconstruction ทั่วไป ดู [Talkner–Hänggi §II Eq. (17), Appendix A](https://arxiv.org/pdf/1605.07415) จึงต้องแยก “ข้อมูลมากขึ้นมีประโยชน์” ออกจาก “ข้อมูลชนิดนี้เพียงพอให้คำตอบเอกลักษณ์แล้ว” ไม่มีการขอหรือเก็บข้อมูลเพิ่มในรอบนี้

<a id="thermal-evidence-decision"></a>

## 9. ผล feasibility: จะปิดอะไรด้วยหลักฐานชนิดไหน

### 9.1 หลักฐานที่มีแต่ละชนิดตัดสินได้ไม่เท่ากัน

| หลักฐานหรือ input ที่มี | ตอบอะไรได้ตามขอบเขต | ยังไม่ตอบอะไร |
| --- | --- | --- |
| Ω/drift/trajectories ที่ bath จุดเดียว | ตรวจ normalized response กับ comparator ตาม protocol | ไม่เลือก intrinsic entropy หรือ physical energy/heat ให้เอกลักษณ์ ตาม witness เดิม §30.4 |
| C-side state counting และ mean-field construction | อธิบาย mixing entropy กับส่วน polynomial ของ C แบบมีเงื่อนไข | ไม่เติม full Phi/Pi sector หรือเปลี่ยน finite binary domain เป็นทั้งเส้นจริง |
| Gaussian F_th และ r ของ lane เดิม | มี thermal contribution และ reciprocal entropy coupling ที่ตามต้นทางได้ | ไม่ใช่ full joint dictionary, physical material identity หรือ total entropy จาก vacuum/interaction ทุกส่วน |
| Equilibrium distributions หลาย T ภายใต้ measure เดิม | จำกัด relative statistical landscape และบาง thermal dependence ได้เพิ่ม | normalized probabilities ไม่เลือก free-energy normalization/HMF ทั้งหมดทั่วไป และไม่ให้ kinetic/source calibration เอง |
| Joint microscopic construction พร้อม state/measure/temperature family และ justified conditional equilibration | เป็นฐานสำหรับตรวจ constrained F/S_int/U และ heat convention ต่อได้ | ไม่รับรองว่าได้สมการ UET เดิมใน limit ที่ควบคุม หรือแยก UET จาก comparator; ต้องแสดงการจับคู่จริง |
| Independent physical source/work/energy/measurement correspondence | ทำให้ตรวจ operational heat และ uncertainty ของระบบที่เลือกได้ | ไม่เปลี่ยน calibration เป็น blind test หรือทำให้กลไกที่ equivalent กลายเป็นฟิสิกส์ใหม่ |

ดังนั้นควรขอ input ให้ตรงกับช่องว่าง ไม่ใช่ขอข้อมูลเพิ่มแบบไม่รู้จุดประสงค์ และการมีข้อมูลอุณหภูมิหรือ entropy output บางตัวไม่ทำให้ joint correspondence ครบเอง

### 9.2 คำวินิจฉัยที่ได้เพิ่มจริง

1. **รับใช้ต่อได้แบบมีเงื่อนไข:** C-side state counting และ Gaussian thermal/Phi-entropy mechanism มีต้นทางจริง ไม่ต้องเริ่มใหม่จากศูนย์
2. **การแทนกันตรง ๆ ยังไม่รองรับ:** C binary population, O(2) χ modes, normalized Φ/Pi และ material response displacement ยังไม่ถูกแสดงว่าใช้ joint state/measure/units เดียวกัน จึงไม่ย้าย S_th หรือ r ไปเป็น full S_int(C,Phi) และไม่บวกสอง free energies เข้าด้วยกันอัตโนมัติ นี่ไม่ใช่ theorem ว่าไม่มี mapping ใดเป็นไปได้
3. **แยกช่องว่างแคบลง:** สิ่งที่ขาดใน joint pilot ไม่ใช่ “entropy ทุกชนิด” แต่คือ correspondence ของ retained C/Phi/Pi กับสิ่งที่ถูกนับรวมแล้ว พร้อม total coefficient/thermal family และ normalization
4. **ตรวจพบ representation trap ที่อธิบายได้:** function ชื่อ free_energy, coefficient ที่เป็นตัวเลขคงที่ และการไม่มี r ใน availability ไม่ตัดสิน physical internal energy หรือ zero intrinsic entropy ต้องตาม construction และชนิด potential
5. **ไม่เพิ่มข้ออ้าง:** REF-E consistency/equivalence และ HIST-F underdetermination เดิมยังอยู่ Physical dictionary, learning, persistence และ global openness ไม่ถูกตัดสินใหม่จาก audit นี้

นี่เป็นความก้าวหน้าด้าน correspondence feasibility และการคัดสิ่งที่จะใช้ต่อ ไม่ใช่ผลทำนายกายภาพใหม่หรือ microscopic closure ที่สำเร็จแล้ว และไม่อ้างว่า self-review ของ AI เป็น specialist approval

### 9.3 หนึ่งงานถัดไป และสิ่งที่ผู้เขียนยังไม่ต้องทำ

ไม่เริ่มตรวจจากศูนย์: [Argument §§13.2 และ 13.7](UET_THEORY_ARGUMENT.md) แยก amplitude squared, signed charge และ nonconserved order coordinate ไว้แล้ว รวมถึงข้อจำกัด conservation/EOS และ rejected double-well reduction ใน scope ของผลเดิม จึงไม่รัน EOS หรือถามซ้ำเพียงว่า C เปลี่ยนชื่อเป็น amplitude/charge ได้หรือไม่

**ข้อเสนอถัดไปที่เฉพาะขึ้น:** จัดทำข้อเสนอ joint conditioning/state–measure rule สำหรับการอ่าน Ω แบบ coarse free energy หนึ่งขอบเขต โดยต้องตอบว่า C เป็น coarse constraint ของ microstates ชุดใด และ Phi เป็น retained state หรือ parameter อย่างไร หากจะ reuse Gaussian entropy ให้ระบุว่า χ ถูกนับภายใต้ constraint ของ C หรือเป็นรายละเอียดอีกส่วนที่มี accounting ต่างกัน ไม่ใช้ unconstrained thermal trace มาแทน fixed-C partition โดยปริยาย

นี่ต้องเป็นข้อเสนอที่เปิดเผยสมมติฐานเพิ่ม ไม่ใช่กลับไปทำผลเก่าซ้ำหรือถือว่ารับอนุมัติจากการมีชื่อ C ใน code แล้ว ไม่เปิดวัสดุใหม่ ไม่หา heat dataset เพื่อเลี่ยงคำถาม และยังไม่ประกาศเลือก microscopic model ของทั้ง UET จาก audit นี้

ชิ้นงานที่ต้องได้คือข้อเสนอที่ประกาศ retained/eliminated variables, normalization/degeneracy และ conditional domain หรือคำตัดสินตรง ๆ ว่าเป็นคนละ model/ยังต้องมี input ใด พร้อม comparator และเหตุผลที่จะเปิด calculation path หากจำเป็น ไม่บังคับให้ผลลงท้ายว่ารวมกันได้ ไม่ทำ mapping ใหม่โดยอ้างว่าเป็นสิ่งที่ผู้เขียนเคยยืนยันแล้ว และเปิดต่อเฉพาะเมื่อมี premise/constraint ที่เปลี่ยนข้อวินิจฉัย ไม่เปลี่ยนสัญลักษณ์แล้วเปิด route ที่ถูกจำกัดไว้ใหม่

ผู้เขียนยังไม่ต้องคิด entropy formula, กำหนด coefficients หรือหาเครื่องมือทดลองให้ งานตามรอยและเสนอทางเลือกพร้อมหลักฐานเป็นหน้าที่ผู้วิจัย หากพบทางเลือกที่เปลี่ยนความหมายของ information/memory จริงจึงส่งให้ทบทวนเฉพาะข้อนั้น ไม่ขอให้เล่าทั้งทฤษฎีใหม่ และยังรักษาทางอ่าน signed/magnitude ทั้งสองแบบ

**จุดหยุดของภาคต่อนี้:** แผนที่ eliminated content กับ T-dependence และคำวินิจฉัยการนำของเดิมมาใช้เสร็จแล้ว ยังไม่เริ่ม correspondence calculation ข้างต้น หากต้องเพิ่ม microscopic ensemble, Hamiltonian, state หรือสมมติฐาน thermal family ต้องเสนอแยกพร้อมเหตุผลก่อน ไม่เพิ่มเพื่อให้การทำงานดูต่อเนื่อง

## 10. ขอบเขตและการตรวจภาคต่อ

source/spec/artifact ที่ตรวจเทียบ baseline เก้ารายการคือ matter–space specification, matter–space implementation, joint reference producer, mass-source specification/implementation, reciprocal dynamics specification, mass-source artifact, reciprocal artifact และ core_paths helper ตามลิงก์ใน §7 เป็น snapshot ของ local baseline ที่ระบุ ไม่กล่าวว่าได้ตรวจทุก Core family หรือ public main สด

เก็บ §§1–6 ของรายงานเดิมไว้ครบ ใช้ SHA-256 ของ canonical LF text ตรวจ preservation ไม่แก้รายงาน Argument, scientific code, calculation contracts, artifacts หรือ gates ไม่สร้าง contract ใหม่เพราะภาคต่อนี้เป็นการตรวจ source/นิยาม/รอยต่อของผลเดิม ยังไม่มีการประเมิน thermal derivatives ใหม่หรือรัน scientific calculation

การตรวจ legacy identity ใน §7.6 แยกจาก completeness schema check: การที่ completeness ไม่พบ structural error ไม่ได้ certify producer identity ของ legacy artifact ทุกไฟล์ การ refresh producer/provenance ถ้าจะทำภายหลังต้องเป็น scoped repair ตามมาตรฐาน ไม่เขียน hash ใหม่เพื่อให้ประวัติดูผ่าน

ผล read-only completeness ทั้งปกติและ changed-path จาก baseline `8e38f78c2cb84f24c94aa1b4e2f76b693c2f62e5` ออกสำเร็จ 17 contracts / 122 routes / 0 errors; existing joint/cycle identities 8+42 ยังตรงและ review ยังคง INCOMPLETE การตรวจ links/anchors/privacy/preservation กับ interface inspection ไม่ใช่ numerical tests หรือผลการรัน science ใหม่ รายละเอียดอยู่ใน log ปิดภาคต่อ ไม่มี push/PR/merge/เผยแพร่ หรือติดต่อผู้เชี่ยวชาญจากคำสั่งวิจัยต่อนี้
