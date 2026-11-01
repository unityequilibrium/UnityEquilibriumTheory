# BaTiO₃: สะพานจากผลึกก้อน–สนามไฟฟ้าสู่ C–Φ–Π

26 ตุลาคม 2026 • baseline 3d42f606ea27af1ae0d2215b183c537073d09bd1
• PHYSICAL_COMPARISON / DIAGNOSTIC • review INCOMPLETE

## สรุปสำหรับผู้เขียน

**ยังใช้ BaTiO₃ เป็น physical realization ของสมการเดิมทั้งชุดไม่ได้ แต่ระบุรอยต่อที่ติดได้ชัดขึ้นแล้ว**
ปัญหาไม่ได้อยู่ที่หาเลขมาแทนไม่ครบอย่างเดียว: พลังงานที่ฟิตหลังวัสดุผ่อนการเปลี่ยนรูปแล้ว
ไม่ใช่พลังงานร่วมก่อนรวมรายละเอียดออก และเครื่องมือวัดความไวทางไฟฟ้าไม่ได้อ่าน C/Φ/Π ครบ

ผลที่ตัดสินได้ใหม่คือ ภายใต้ dictionary แบบเชิงเส้น C↔polarization และเงื่อนไข static
ที่ประกาศใน §4 เมื่อปล่อย Φ ของสมการเดิมให้สมดุลใกล้ศูนย์ จะไม่มีเทอม C⁶ ใน potential ที่เหลือ
แต่ source-fitted polynomial ของกรณีหลักมีเทอม P⁶ ไม่เป็นศูนย์
จึง **ไม่เท่ากันแบบ exact ระหว่าง polynomial คู่นี้ภายใต้เงื่อนไขนั้น**
ไม่ใช่การพิสูจน์ว่าวัสดุขัดกับ UET ทั้งหมด: uncertainty ของ fit, joint ensemble และการลดโหมด
ยังไม่ admitted จึงไม่เปลี่ยน conditional mismatch ให้เป็น certified physical rejection

สิ่งที่อ่านจริงคือ dielectric response จาก LCR ที่มีความถี่และ bias กำกับ
ไม่ใช่ signed P กับ strain ที่วัดอิสระพร้อมกัน และไม่ใช่หลักฐานว่าคง nonzero state ได้หลังปิดสนาม
ข้อมูลชุดนี้จึงยังไม่รับรองการเขียน–เก็บ–อ่านแบบรอบ regime, ไม่กำหนด Π/inertia/damping
และไม่ทำให้ normalized injection work กลายเป็น electrical work หรือ heat ของอุปกรณ์

ทางอ่าน: [ฐาน](#bto-baseline) → [dictionary](#bto-dictionary) → [ผลตรวจ potential](#bto-potential)
→ [พอร์ตและการอ่าน](#bto-observation) → [คำวินิจฉัย](#bto-verdict)

<a id="bto-baseline"></a>
## 1. ฐาน ขอบเขต และ bounded research card

เริ่มจาก HEAD ข้างต้นบน codex/research/batio3-static-correspondence ใน worktree เดิม
index ว่าง งานค้างเดิม463รายการ และ Topic-log diff578เพิ่ม/79ลบแยกไว้ ไม่ fetch หรืออ้างว่า
working evidence เท่ากับ public main ตรวจ11 contracts เดิมด้วย metadata/identity เท่านั้น
พบ identity errors เป็นศูนย์:42/8/11/13/14/20/14/11/15/22/18รายการตามลำดับสาย cycle,
joint thermal, M,N,O,P,Q,variance,platform screen,U และ regime
รักษา106 normalized hashes และ284 unrelated tracked raw hashes ไม่รัน producers เก่า

| Work card | ขอบเขตที่ล็อก |
|---|---|
| Question | กรณี bulk BaTiO₃ ที่เลือกให้ physical state/energy/ports/readout ตรงสมการเดิมได้หรือไม่ ไม่ใช่หาค่าสเกลให้ fit |
| Have | [Argument §§18,21–29](UET_THEORY_ARGUMENT.md), [regime](UET_RETAINED_RESPONSE_REGIME_CLASSIFICATION.md), [premise T/U](UET_CORE_PROPOSITION_PREMISE_REVIEW.md); dictionary/force-work/Schur/omitted-mode limits มีแล้ว ไม่ derive ซ้ำ |
| Boundary | Sample, electrodes, circuit/LCR, thermal/mounting environment และ record แยกกัน; C/Φ เป็น candidate view ของ sample ไม่ใช่ state ที่เพิ่มจากชื่อ |
| Missing | Same-specimen joint/bare potential, mechanical boundary/mode, internal field, calibrated strain/signed-P readout, DC band และ uncertainty |
| Controller | physical-parent-preparation เดิมยังเปิด; quantum-parent-correspondence แยก ไม่ปิดด้วยการอ่าน source หรือ symbolic pass |
| One action / why | ตรวจ native model/ensemble ก่อน แล้วใช้ conditional sextic witness และ observation chain เพื่อแยกความต่างจริงจากการเทียบผิดระดับ |
| Outcomes | EQUIVALENT / APPROXIMATE / DIFFERENT / UNRESOLVED รายรอยต่อ ไม่ต้องมี realization ผ่าน |
| Stop / reopen | หยุด exact claim เมื่อ witness เพียงพอ; หากสองความพยายามไม่เปลี่ยน verdict ให้ระบุ prerequisite ไม่เพิ่มวัสดุหรือเทอม |
| Reviewer | ผู้เชี่ยวชาญ ferroelectric thermodynamics/measurement ตรวจว่า joint ensemble และ source-calibrated observable ตรงหรือไม่ ไม่ขอให้รับรองทั้ง UET |
| Non-goals | No fit/digitization/sweep/trajectory, new material/experiment, one-port write, Core/README/gates หรือ publication |

เจตนาผู้เขียนคือปิดสะพานกายภาพก่อนและเลือก bulk–electric-field case
ส่วน C=P/P₀, mechanical projection และการอ่าน Ω เป็น effective free energy
เป็น candidate dictionary ที่ AI เคยเสนอใน Argument §21 ไม่ใช่ author ontology หรือผลบังคับของ information
ผลโซ่ N4 และความต่าง Mn/Fe/Pt เดิมไม่ถูกลบหรือโอนมวล/geometry มาใช้กับ BaTiO₃

### Source identity และสิ่งที่ใช้จริง

| Source | ตำแหน่งที่ตรวจ / หน้าที่ |
|---|---|
| [Wang2006 v1](https://arxiv.org/pdf/cond-mat/0603688v1) | pp.3–6,Eqs.(1)–(7), specimen/LCR และ Fig.2/Table I/footnote; กรณีหลัก |
| [Li2005 author copy](https://personal.ems.psu.edu/~chen/publications/YL2005JAP.pdf) | §II Eq.(1),Table I; §III Eq.(2),Eqs.(3)–(4); potential/normalization lineage ไม่ใช่ specimen calibration |
| [Wang2007 v1](https://arxiv.org/html/0706.3261v1) | §§II.A,III,IV,Eqs.(1)–(3),(21)–(22),Table II; follow-up/ensemble/temperature limitations ไม่ใช่ independent replication |
| [Jiang2016 v4](https://arxiv.org/html/1512.05456v4) | §§I–II,III.A/D; fixed-D,zero-stress,zero-temperature calculation และ Q definition ไม่ใช่ค่าของ specimen |

Publisher DOI ของ Li/Wang2007 เปิดไม่ได้ แต่สำเนาผู้เขียนของ Li และ arXiv ของ Wang2007 อ่านได้
ไม่ใช้ abstract เป็นหลักฐานของสมการ Access copy PDF สองไฟล์อยู่ชั่วคราวนอก repository
ตรวจภาพ Table I ของ Wang2006 และ Li2005 จริงด้วย Poppler; ไม่รวมบทความ/ภาพเข้า commit
hash ของ access copies และ read scope อยู่ใน source-input ไม่อ้างว่า offline producer ดึงต้นฉบับใหม่
ใช้ arXiv version/บรรณานุกรมเป็นวันที่ source ไม่ใช้ regenerated date ใน HTML/PDF เป็นวันเผยแพร่
Wang2007 HTML Eqs.(8)–(9) มี gamma factors ตกเมื่อเทียบ Eq.(2)–(3); ไม่ใช้สองสมการนั้นคำนวณ

## 2. Native case และ provenance ที่ห้ามผสม

กรณีหลักคือ undoped [001] plate เคลือบ Pt ทั้งสองหน้าหลัก มี nominal geometry
2×2×0.3mm³; DC-bias dielectric response ที่135°C อ่านด้วย LCR10kHz
จาก specimen paragraph/Fig.2 ของ Wang2006 ไม่ digitize จุดบนกราฟ
Table I แถว eighth-order/Both ให้ source-model fit:

| วัตถุ | Printed value / convention | ใช้อย่างไร |
|---|---|---|
| −β_N | 8.6×10⁸ V m⁵ C⁻³ | β_N เป็นลบ ไม่ใช่บวกจากชื่อคอลัมน์ |
| γ_N | 0.8×10¹⁰ V m⁹ C⁻⁵ | fit coefficient ไม่ใช่ direct measured constant |
| δ_N | 3.4×10¹¹ V m¹³ C⁻⁷ | fit coefficient ไม่มี covariance/error interval ให้ใช้ |

Geometry/conditions ก็ไม่มี hard uncertainty ใน source subset ไม่ใช่ค่าที่แน่นอนทางกายภาพ
α_N ยังไม่มีค่าที่ใช้ได้ใน packet นี้ ไม่เติมจาก paper อื่น
sixth-order paraelectric γ ใช้ข้อมูล critical field เพิ่มตาม footnote ไม่ใช่ identifiable จาก branch เดียว
รอบนี้จึงไม่ผสมสามแถว fit ไม่ fit ใหม่ และไม่สร้าง predicted curve ของ Core

Li Eq.(1) ระบุ **mechanically stress-free potential** และ fit origins ของ coefficients;
Table I ใช้ convention α₁₁P⁴+α₁₁₁P⁶+α₁₁₁₁P⁸ ต่างจาก fractions ของ Wang
การแปลงฐานให้ β=4α₁₁,γ=6α₁₁₁,δ=8α₁₁₁₁ ได้ point values
−8.388×10⁸,7.764×10⁹,3.0904×10¹¹ ตามลำดับ แต่เป็นคนละ potential/context
ไม่แทนค่าของ Wang ด้วยตัวเลขเหล่านี้หรือถือว่าความต่างเป็น measurement error
ค่าที่อ้างว่าเป็น Li ในคำอธิบาย/ตารางของงานต่อเนื่องมีการปัด/ความต่าง จึงเก็บรุ่นต้นทางแยก

Wang2007 เชื่อมกับงาน2006โดยตรง จึงไม่นับเป็น external replication หรือฟิตหลายชุดแล้วอ้างเป็น
holdout; ความสัมพันธ์ระหว่าง specimens ไม่เพียงพอให้ยืนยันเหมือนกันทุกสภาพ
การพบ temperature dependence ในหลาย T ไม่หักล้างการตรึง coefficients ณ T เดียวโดยตัวมันเอง
Jiang fixed-D/zero-stress calculation ต่างจาก voltage-driven finite-T plate;
ไม่ยืม Q,elastic constants หรือ lattice scales มาคาลิเบรตผลึกนี้

<a id="bto-dictionary"></a>
## 3. Native potential, joint energy และ physical dictionary

เขียน intrinsic polarization potential density ของ source เป็น

\[
G_0(P)=\frac{\alpha_N}{2}P^2+\frac{\beta_N}{4}P^4+
\frac{\gamma_N}{6}P^6+\frac{\delta_N}{8}P^8.
\]

Bias-controlled potential ใช้ \(G_0-EP\); Wang2006 Eq.(1) แสดง intrinsic part
ส่วน Wang2007 Eq.(1) รวม −EP แล้ว ต้องใช้ convention ให้ตรงก่อน differentiate
\[
E=\partial_PG_0,\qquad K_N(P)=\partial_P^2G_0
=\alpha_N+3\beta_NP^2+5\gamma_NP^4+7\delta_NP^6.
\]

นี่ไม่ใช่ full joint F(P,strain) ที่เพียงเอา elastic energy/coupling มาเติมต่อได้
เมื่อ strain ถูก relax ออกแล้ว ผล coupling อยู่ใน effective coefficients บางส่วน
การ recover bare coefficients ต้องมี joint constitutive/ensemble information เพิ่ม
สำหรับ specimen หลัก mounting, external traction และ clamping ยังไม่ครบใน protocol ที่อ่าน
ไม่เอาคำว่า bulk ไปแทน stress-free boundary ที่สอบเทียบแล้ว

| Quantity | Candidate role / unit | สิ่งที่ยังไม่ admitted |
|---|---|---|
| P | signed polarization, C_charge/m²; C=P/P₀ | order-parameter/background split, uniformity และ independent signed readout |
| strain tensor ε_ij | dimensionless deformation | tensor component, reference lattice, lateral constraints และ compatible mode |
| x / Φ | modal displacement m / normalized view | projection/shape/calibration ไม่ใช่ terminal displacement โดยชื่อ |
| Π | normalized rate ของ Φ | static packet ไม่ให้ rate, mass, damping หรือ Markov closure |
| G₀,f / F | J/m³ / total J=∫f dV | ensemble และ eliminated degrees of freedom |
| E_int / f_P | V/m / generalized electrical force | actual field/circuit map; uniform case จึงมี f_P=V_sample E_int |
| Q / energy coupling λ | m⁴/C_charge² / J m⁻³ per P² | ไม่ใช่ g เดียวกันและไม่ใช่ cubic stiffness โดยอัตโนมัติ |
| C_cap / C | capacitance F / normalized state | ห้ามสับสนชื่อ C หรือ coulomb unit กับ state C |
| ε_abs,ε_r,χ_P | F/m,dimensionless,F/m | background/frequency/field definitions ต้องตรง |

ตัวอย่างพีชคณิต **หนึ่ง strain component ที่มี constitutive law รองรับแล้วเท่านั้น**:
\[
f_{\rm mech}=\tfrac12k_\epsilon\epsilon^2-\tfrac12\lambda P^2\epsilon+\cdots,
\quad
\epsilon=\frac{\lambda}{2k_\epsilon}P^2+\cdots,\quad
Q=\frac{\lambda}{2k_\epsilon}.
\]
จึงต้องมี stiffness และ tensor/boundary reduction ก่อนแปล Q เป็น energy coupling
ใน leading harmonic relaxation จะได้
\[
B_{\rm relaxed}=B_{\rm bare}-\lambda^2/(2k_\epsilon)
=B_{\rm bare}-2k_\epsilon Q^2.
\]
นี่เป็น origin/normalization check ไม่ใช่การตั้ง b_Φ=0 ใน Core
negative relaxed quartic จึง **ไม่** พิสูจน์ว่า bare b_C>0 ผิด
แต่ positive bare coefficient ก็ยังหาไม่ได้จาก B_relaxed ตัวเดียว

การ shift \(\Phi=\Phi_0+y\) ใน quartic Φ เดิมให้ cubic coefficient \(b_\Phi\Phi_0y^3\)
รวม linear/quadratic terms ที่เปลี่ยนด้วย จะไม่ตัดสิ่งเหล่านี้ทิ้งแล้วอ้างว่าเป็น old zero-reference law
เช่นเดียวกับการเปลี่ยนเป็น fixed-D ต้องรักษา field-energy/Legendre terms ไม่ใช่เพียงเปลี่ยนชื่อ E

<a id="bto-potential"></a>
## 4. ผลตรวจใหม่: conditional sextic obstruction

ใช้ Ω เดิมเท่านั้น เขียน a=a_C,b=b_C,α=a_Φ,β=b_Φ และ g ตามเดิม
ในส่วนนี้ **α>0, zero mechanical source, reference Φ=0, linear P=P₀C
และ matched static ensemble** เป็นเงื่อนไข ไม่ใช่ข้อเท็จจริงของ specimen ที่รู้แล้ว
\[
\alpha\Phi+\beta\Phi^3=\tfrac g2C^2.
\]
Implicit-function theorem ที่ ∂_Φ lhs=α>0 ให้ analytic branch ใกล้ศูนย์
ตั้ง q=C² แล้ว Φ(q) เป็น odd function เพราะสมการเปลี่ยนเครื่องหมายพร้อม q,Φ
จึงได้
\[
\Phi(C)=\frac{g}{2\alpha}C^2-\frac{\beta g^3}{8\alpha^4}C^6
+\frac{3\beta^2g^5}{32\alpha^7}C^{10}+O(C^{14}).
\]
แทนกลับ generator เดียวกัน:
\[
\Omega_{\rm red}(C)=\frac a2C^2+
\left(\frac b4-\frac{g^2}{8\alpha}\right)C^4+
\frac{\beta g^4}{64\alpha^4}C^8+O(C^{12}).
\]
ไม่มี C⁶ หรือ C¹⁰; force ไม่มี C⁵ และ curvature ไม่มี C⁴ term
นี่คือ local series coefficient identity ไม่ใช่ finite-amplitude approximation certificate
การลด static ไม่ให้สิทธิ์ทิ้ง Φ/Π ใน prepared-state dynamics ตามข้อจำกัดเดิม

ถ้า f_*=E_*/V_* และ P=P₀C โดยสเกลบวก จะได้ native normalized sextic coefficient
\(\bar\gamma_N=\gamma_NP_0^6/f_*\) การ rescale เชิงเส้นไม่เปลี่ยน nonzero ให้เป็นศูนย์
ดังนั้น polynomial ที่ใช้ printed γ_N≠0 ไม่อาจเท่ากับ Ω_red นี้แบบ exact รอบศูนย์
ภายใต้ premises ข้างต้น นี่ตัด **exact polynomial identification แบบหนึ่ง** ได้

แต่ไม่ใช่ certified physical rejection เพราะ (1) γ_N เป็น fit point ไม่มี interval/covariance
(2) same-specimen mechanical ensemble และ bare joint mapping ยังไม่ปิด
(3) physical reference/prestress และ omitted degrees ไม่ได้พิสูจน์ให้ตรง premises
จึงแยก verdict “DIFFERENT: conditional polynomials” จาก “UNRESOLVED: full physical bridge”
ไม่แก้ด้วย P⁶ term ใหม่, nonlinear coordinate fit, shift ที่ละ cubic หรือ retuning source

### Error scope ที่ไม่แอบรับรอง approximation

ถ้าสมมติให้ coefficients อื่นตรงและพิจารณาเฉพาะส่วน sextic ที่หายไป จะมี contributions
\[
\Delta E_{\rm sextic}=\gamma_NP^5,\qquad
\Delta K_{\rm sextic}=5\gamma_NP^4.
\]
นี่ไม่ใช่ total error bound: full Ω_red มี higher terms และ physical coefficient/range uncertainties
ยังไม่มี admitted physical P interval หรือ error allocation ให้ใช้
ไม่แทน free-energy error เป็น susceptibility error และไม่หาร relative error ใกล้ K=0
ไม่มีเปอร์เซ็นต์ผ่าน, fit หรือ material admissibility claim จากสูตรนี้
ถ้า α=0 การอ่าน analytic branch นี้ใช้ไม่ได้ ไม่ลด α หรือเปลี่ยน Core domain เพื่อรักษาผล

<a id="bto-observation"></a>
## 5. Input–observation chain และบัญชี work

### 5.1 สิ่งที่เครื่องมืออ่าน

Native chain คือ voltage source/temperature chamber → electroded sample →
terminal small-signal charge/current → LCR-derived dielectric product
ไม่ใช่ P,ε_ij,Π ที่ถูกอ่านอิสระครบทุกตัว
Pt/electrodes,circuit และ mounting/thermal surroundings เป็นคนละส่วนกับ sample
“ผู้สังเกตอยู่นอกระบบ” ไม่ได้ทำให้ loading,field redistribution หรือ heating เป็นศูนย์

สำหรับ ideal parallel plate, uniform field และ equivalent circuit/background ที่ยืนยันแล้ว:
\[
D=\epsilon_0\epsilon_b E_{\rm int}+P,\quad
C_{\rm cap}=\frac{A_s}{d_s}(\epsilon_0\epsilon_b+\chi_P),\quad
\chi_P=\epsilon_0(\epsilon_r-\epsilon_b).
\]
ใช้ ε_b=1 ได้เมื่อ P หมายถึง total material polarization ตาม convention นั้นจริง
หาก P คือ soft-mode order parameter จะมี background ที่ต้องระบุ
หน่วย Eq.(3) เป็น inverse susceptibility (m/F) ขณะที่เลข dielectric constant ที่นำเสนอ
มักเป็น relative convention; Wang2007 Eq.(21) ระบุ ε_r และ ε₀ แยกชัด
การแก้ notation ไม่เท่ากับได้ raw capacitance/circuit calibration ของ specimen แล้ว

การแปลง nominal geometry/conditions ให้ A_s=4×10⁻⁶m²,V_s=1.2×10⁻⁹m³,
T=408.15K,f=10000Hz และ ω=20000πrad/s เป็น point conversions เท่านั้น
ไม่สร้าง C_cap ที่ source ไม่ได้สกัด ไม่ตั้ง E_int=V_command/d โดยละ screening/interface
และไม่ตั้ง measurement uncertainty เป็นศูนย์เพราะการแปลงหน่วย exact

10kHz ยังเป็น finite-frequency observable แม้ source ใช้ quasistatic polynomial ตีความข้อมูล
คำกล่าวเรื่อง within-phase hysteresis ใน source ไม่ใช่ bound ว่า χ(10kHz)=χ(0)
band,AC amplitude,loss/background และ instrument correction ยังไม่มีใน packet ที่ admitted
จึงยังใช้เปรียบเทียบ full DC gain หรือหา M_C,M_Φ,τ ของ Core ไม่ได้

### 5.2 Readout และ retained-state limitations

Native K_N(P) เป็น even function ของ P; electrostrictive QP² ก็ even
ดังนั้น **readout map สองชนิดนี้เพียงลำพัง** ไม่แยก ±P
นี่ไม่ใช่ no-go ต่อทุก protocol: known bias/history หรือ signed-charge measurement อาจเพิ่มข้อมูล
แต่ต้องประกาศ ไม่ถือว่ามีอยู่แล้ว หรือใช้ native scalar response เป็น full C–Φ–Π observation

Native field-induced branch ที่ bias ยังคงอยู่ไม่ใช่การเตรียม nonzero state แล้วปิด inputs
จากนั้น hold/read ตามรอบ regime ชุดนี้ไม่มี write–release–hold–probe certificate นั้น
ไม่มี same-specimen calibrated strain/mode/time readout จึงยังไม่มี Φ/Π admission
ไม่อนุมาน mechanical lifetime จาก dielectric hysteresis หรือ atomic mass

### 5.3 Work convention ที่ต้องรักษา

ใช้ force-port reading ของ Argument §18/§21 เมื่อ field/geometry mapping รองรับ:
\[
P_{\rm force}=(J_C/M_C)\dot C+(J_\Phi/M_\Phi)\Pi,\quad
D_{\rm force}=\dot C^2/M_C+\Pi^2/M_\Phi.
\]
old injection ledger ยังเป็น
\[
P_{\rm old}=\mu_CJ_C+\Pi J_\Phi/M_\Phi,\quad
D_{\rm old}=M_C\mu_C^2+\Pi^2/M_\Phi.
\]
สอง split ให้ energy balance เดียวกัน แต่ไม่ให้ work/heat ความหมายเดียวกันโดยอัตโนมัติ
จาก \(\dot C=-M_C\mu_C+J_C\) ผลต่าง C-sector ของทั้ง P และ D เท่ากับ
\(J_C^2/M_C-2\mu_CJ_C\) จึงหักล้างใน net balance ได้ โดยยังไม่เลือก physical split
แรงไฟฟ้ารวมของ uniform P คือ f_P=V_s E_int ไม่ใช่ raw voltage
terminal VI ยังรวม circuit/field/background storage และ losses ที่ต้องแยก
จึงไม่แปลงตัวเลข write-work ในรายงาน regime เป็น joule/heat ของ BaTiO₃

<a id="bto-verdict"></a>
## 6. คำวินิจฉัยและหนึ่งโจทย์ถัดไป

| รอยต่อ | Verdict และขอบเขต |
|---|---|
| C↔P | UNRESOLVED ทางกายภาพ; candidate normalization มีความหมาย แต่ full state/independent readout ไม่ admitted |
| Conditional reduced polynomial | DIFFERENT ภายใต้ exact premises §4 และ source point polynomial ไม่ใช่ certified material falsification |
| Full joint potential/ensemble | UNRESOLVED; ต้องมี bare/clamped-versus-relaxed,mechanical boundary และ error/covariance |
| Source voltage↔J_C | UNRESOLVED; nominal field ไม่ให้ internal-field/kinetic normalization หรือ work calibration |
| Dielectric channel↔full state | DIFFERENT ถ้าอ้าง invertible signed-state reading จาก channel นี้เพียงลำพัง |
| LCR10kHz↔DC gain | UNRESOLVED; finite-frequency/circuit/background certificate ยังขาด |
| Φ/Π | UNRESOLVED; mode/strain readout,inertia/rates ยังไม่มี |
| Regime memory/improvement | UNRESOLVED สำหรับ specimen; biased phases ไม่เป็น write-release memory หรือ task improvement |

ไม่มี verdict “APPROXIMATE” ที่แอบหมายถึง numerical accuracy ที่ยังไม่ได้ bound
พลังงานสองระดับที่ต่างกันไม่ทำให้ทุก correspondence เป็นเท็จ
และการมี standard electrostriction ไม่ใช่ UET discriminator
ข้อเสนอจักรวาลเปิด,learning,persistence และ physics gates สายอื่นไม่ถูกยืนยันหรือปฏิเสธแทน

**หนึ่งโจทย์ถัดไป:** ขอให้มี same-specimen mechanical-ensemble/joint-potential/readout packet
ก่อน instantiate scales หรือ kinetics ประกอบด้วย boundary/mounting, source-to-internal-field,
bare-versus-relaxed constitutive origin, calibrated dielectric convention/band,
และ independent strain/signed-state observation ที่เกี่ยวกับ claim
สิ่งที่ไม่มีให้คง UNKNOWN; ไม่ให้ผู้เขียนคิดสมการหรือสร้างเครื่องมือแทนช่องข้อมูลนี้

ผู้ตรวจ ferroelectric thermodynamics ควรตอบว่า source potential ที่ใช้ถูก relax ใต้อะไร
และ sextic witness ใช้กับ dictionary นี้ได้จริงหรือไม่
ผู้ตรวจ impedance/measurement ควรตอบว่า LCR product แยก background,circuit และ finite frequency ได้แค่ไหน
หาก packet ยืนยัน mismatch ให้ปิด exact bridge ใน scope นั้น; หากพอ bound approximation
ค่อยเสนอการตรวจ error โดยเฉพาะ หากยังไม่มี input ที่เปลี่ยน verdict ให้หยุด ไม่เปิดวัสดุ/model/experiment ใหม่
รอบนี้ยังไม่ติดต่อผู้ตรวจหรือเริ่มงานนั้น

<a id="bto-reproduce"></a>
## 7. การทำซ้ำและขอบเขตการตรวจ

- [Source-input/manifest-equivalent](../topics/0.13_Thermodynamic_Bridge/Data/03_Research/batio3_static_correspondence_audit_sources.json)
- [Contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/batio3_static_correspondence_audit.json)
- [Producer](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_BaTiO3_Static_Correspondence_Audit.py)
- [Tests](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_batio3_static_correspondence_audit.py)
- [Artifact](../topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_batio3_static_correspondence_audit.json)

Producer อ่านเฉพาะ source subset และ identity-matched local evidence ไม่มี network ระหว่างทำซ้ำ
ใช้ --check แบบ read-only; --emit-report เขียน artifact ใหม่นี้โดย explicit เท่านั้น
symbolic/source/negative-control checks เป็น implementation evidence ไม่ใช่ independent physical validation
ค่าของ source, transformations และ curator verdicts แยกจาก symbolic identities ใน artifact
ไม่มี Monte Carlo,fit,graph digitization,sweep,trajectory,numerical roots หรือ old scientific producer
helper AST เดิมใช้เพียงตรวจ source generator ไม่เรียก old calculate/algebra/main

ชุดตรวจใหม่ครอบคลุม fractions/sign/unit/context,conditional reduction/degeneracy/prestress,
bare-versus-relaxed accounting,dielectric background/frequency/readout,
work convention,unknown uncertainty และการป้องกัน claim promotion
completeness/changed-path,links,source identity,privacy และการรักษาผลเดิมตรวจแยก
ผลที่รันจริงอยู่ใน Topic UPDATE_LOG และ WORK_LEDGER ไม่ทำให้ physical gates เป็นสีเขียว
