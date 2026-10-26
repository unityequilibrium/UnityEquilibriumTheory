# สภาพคงตัว ความไว และการเขียนของ C–Φ–Π เดิม

ตรวจวันที่ 25 ตุลาคม 2026 • source baseline `d6ddc910313028f63828a8bf02897480822c10e3`
• `FORMAL_RESULT` • review `INCOMPLETE` (การสร้างและทบทวนตนเอง ไม่ใช่ผู้เชี่ยวชาญอิสระ)

## สรุปสำหรับผู้เขียน

**สมการเดิมทำได้มากกว่าการจำเครื่องหมายบวก–ลบใน unit fixture ของรอบ U:**
ภายในช่วงพารามิเตอร์ที่โค้ดอนุญาตอยู่แล้ว มีกรณีที่สถานะศูนย์กับสถานะไม่เป็นศูนย์
เป็นจุดพักที่เสถียรร่วมกัน เมื่อเขียนจากจุดเริ่มเดียวกันไปคนละจุดพัก แล้วใช้
input เล็กแบบเดียวกันอ่าน C หลังหักค่าพื้นฐาน จะได้ความไวที่มีขนาดต่างกันจริง
ไม่ต้องเพิ่มเทอม เปลี่ยนกฎ หรือเปลี่ยนพารามิเตอร์ระหว่างสองประวัติ

ภาพง่าย ๆ คือระบบมีทั้ง “พักแบบศูนย์” และ “พักอีกแบบที่ C กับ Φ ไม่เป็นศูนย์”
การเขียนพาไปเลือก operating point หนึ่ง จากนั้นกฎเดิมตอบสนองต่างกันเพราะความโค้ง
และ coupling ที่จุดนั้นต่างกัน นี่คือ **state/phase memory และ state-dependent
sensitivity** ในแบบจำลอง ไม่ใช่หลักฐานว่าระบบเรียนรู้ topology หรือสร้างกฎใหม่เอง

ผล U เดิมยังถูกในขอบเขตเดิม: คู่ ±C ที่มี Φ เดียวกันให้ขนาด transfer เท่ากัน
สำหรับแต่ละช่องอ่านและทีละ port ส่วนผลใหม่เปรียบเทียบ **ศูนย์กับ nonzero branch**
จึงไม่ใช่การแก้ผล U ย้อนหลัง และไม่ควรยกข้อจำกัดของ unit fixture เป็นข้อห้ามทั้ง family

มีข้อแลกเปลี่ยนที่ต้องแสดงตรง ๆ: ใน exact control ที่กำหนดก่อนตรวจ สภาพ nonzero
มีพลังงานสูงกว่าศูนย์ และการเขียนใช้ normalized work มากกว่าประวัติที่ไม่เขียน
เราพิสูจน์เส้นทางเขียนได้ด้วย inputs ของสมการเดิม แต่ยังไม่มี apparatus, SI energy,
noise lifetime, physical C/Φ mapping หรือผลว่าพฤติกรรม “ดีขึ้น”
กลไกนี้ตรงกับกรอบ nonlinear multistability มาตรฐาน จึงยังไม่แยก UET ออกจากคู่เทียบ

ทางอ่าน: [ฐานและขอบเขต](#regime-baseline) → [ตารางจำแนก](#regime-classification)
→ [ความไว](#regime-response) → [การเขียนและพลังงาน](#regime-write)
→ [คำวินิจฉัยและทางต่อ](#regime-verdict)

<a id="regime-baseline"></a>
## 1. ฐานหลักฐาน ขอบเขต และ bounded research card

### 1.1 Source identity และการรักษาหลักฐาน

เริ่มจาก HEAD ข้างต้น บนสาขา `codex/research/retained-response-regimes` ใน worktree
เดิม ไม่มี upstream ของสาขานี้ ตรวจพบงานค้างเดิม 463 รายการและ index ว่างก่อนทำงาน
Topic UPDATE_LOG มี diff เดิม 578 เพิ่ม/79 ลบ ซึ่ง **ไม่รวมใน commit รอบนี้**
วันที่กับชื่อรายงานไม่ถูกใช้แทนการตรวจ identity

ตรวจ metadata/identities ของสิบ contract เดิมโดยไม่เรียก scientific producers:
energy-memory cycle (42), joint thermodynamic completion (8), joint state measure (11),
spin–strain (13), lattice mechanical (14), lattice bath (20), parent static (14),
Φ variance (11), physical-platform screen (15) และ retained-response U (22)
ไม่พบ identity errors ณ ฐานนี้ เก็บ 101 normalized source/contract/artifact hashes
และ raw hashes ของงาน tracked อื่น 284 ไฟล์เพื่อเทียบตอนส่งงาน
ตัวเลขเหล่านี้เป็นขอบเขตการรักษาไฟล์ ไม่ใช่คะแนนความถูกต้องทางฟิสิกส์

ฐานวิทยาศาสตร์ที่ใช้จริง:

- [Core law](../core/02_equations/matter_space/uet_matter_space.py):
  `MatterSpaceConfig.__post_init__`, `matter_space_free_energy`,
  `matter_space_chemical_potentials`, `matter_space_rhs`, `matter_space_extended_energy`
- [Matter–space specification](../core/01_contracts/MATTER_SPACE_RESEARCH_SPEC.md)
  และ [Argument §11](UET_THEORY_ARGUMENT.md): state, source ports และ normalized ledger
- [รายงาน U §§8–13](UET_CORE_PROPOSITION_PREMISE_REVIEW.md#retained-response-question)
  และ [artifact U](../topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_retained_response_requirement_audit.json):
  อ่านผล transfer ที่บันทึกไว้ ไม่เรียก `calculate`, `algebra` หรือ `main` ของ U
- [Physical-platform screen](UET_PHYSICAL_PLATFORM_CORRESPONDENCE_SCREEN.md):
  `physical-parent-preparation` ยังเป็น controller ทางกายภาพ;
  `quantum-parent-correspondence` เป็นช่องว่างแยก ไม่ปิดด้วยผล formal นี้

นี่คือ working evidence และ local commits ไม่ใช่การยืนยันว่าชุดนี้อยู่บน public main
ไม่ได้ fetch/push/merge หรือเผยแพร่ และไม่คัดข้อมูล private/raw มาเป็นหลักฐานสาธารณะ
artifact ใหม่ผูก normalized hashes ของ report/code/spec/U input/schema/helper/standards
อย่างชัดเจน ไม่ refresh hashes ของ contract เก่า

### 1.2 ใครเสนออะไร และตรวจอะไร

| ประเภท | สิ่งที่ใช้ในรอบนี้ | สถานะ/สิ่งที่ไม่ตามมา |
| --- | --- | --- |
| เจตนาผู้เขียน | ตรวจทั้งการเก็บผลอดีตและการเปลี่ยนความไว; คง signed/magnitude ทางเลือก | ไม่บังคับว่า information เท่ากับ C, Φ หรือ entropy และไม่ตัดข้อเสนอจักรวาลเปิดออก |
| สมการเดิม | state C/Φ/Π, potential และ source ports ที่โค้ดมี | ไม่ออกกฎใหม่ ไม่เปลี่ยน defaults หรือเลือก realization สากล |
| ข้อเลือกวิจัยที่ผู้เขียนอนุมัติ | homogeneous nonconserved restriction, primary readout C, สอง exact controls, quintic write | เป็น protocol ของการตรวจ ไม่ใช่ค่าของวัสดุหรือการเลือกความหมายทางกายภาพ |
| ฐานมาตรฐานที่นำเข้า | energy landscape, Hessian, susceptibility, resolvent และ Lyapunov/LaSalle argument | เป็นเครื่องมือคณิตศาสตร์ ไม่ใช่หลักฐานความใหม่หรือ physical validation |
| ผลใหม่ของรอบนี้ | domain-wide classification, zero/nonzero gain contrast, exact finite-write ledger | จำกัดตาม domain/protocol ที่ประกาศ ไม่พิสูจน์ topology learning, improvement หรือ lifetime |

ใช้ Tong, *Statistical Field Theory*, official HTML chapter 1,
§§1.2.1–1.2.2, Eqs. (1.13)–(1.20) เป็นฐานแนวคิดเรื่อง minima และ susceptibility;
§1.2.2 แยก local กับ global minimum และ Eq. (1.19) นิยาม susceptibility เป็น derivative
ไม่ใช่ความต่างของ baseline เรา derive สองพิกัดของเราต่างหาก ไม่อ้างว่า Tong มี
Hamiltonian ชุดนี้หรือพิสูจน์ UET ไว้แล้ว และไม่ยก bifurcation ของ ODE ไปเป็น
thermodynamic phase transition ของวัสดุ ([ต้นฉบับ](https://www.damtp.cam.ac.uk/user/tong/sft/sfthtml/S1.html))
รุ่นที่ตรวจคือ official HTML ที่เข้าถึงวันที่ข้างต้น; ไม่อ้างว่าได้ archive upstream bytes

### 1.3 Bounded work card

| ช่อง | ข้อกำหนดของรอบนี้ |
| --- | --- |
| Question / intended claim | สมการเดิมมีสภาพคงตัวที่เขียนถึงจาก common state แล้วให้ขนาด response ต่างกันหรือไม่ ภายใต้ domain ใด |
| Boundary | C กับ (Φ,Π) มี internal coupling จาก Ω เดียว; ports เป็น mathematical inputs; readouts เป็น views ไม่มี detector/carrier ใหม่และไม่อนุมาน backaction จริงเป็นศูนย์ |
| Stage | TD2–TD3: consistency และ comparator ของ family เดิม ไม่ใช่ physical realization/test |
| Have | U จำกัดคู่ ± ใน unit fixture; source ให้ coefficient domain และ ledger; M–S ให้ข้อจำกัด physical correspondence ที่ยังต้องรักษา |
| Missing/disputed | U ยังไม่ตัดสิน zero/nonzero coexistence ทั้ง family; physical state/preparation/readout และข้อจำกัดที่แยก comparator ยังไม่ admitted |
| Controller | การคำนวณนี้ใช้ contract ใหม่ด้านล่าง; physical controller เดิมยังเป็น `physical-parent-preparation` ไม่ถูกแทนที่ด้วย formal pass |
| Next action / why | จำแนก force pair และ Hessian ก่อน แล้วตรวจ transfer กับ finite write: แยกข้อจำกัด fixture ออกจาก family โดยไม่เพิ่มสมมติฐานพลวัต |
| Acceptable outcomes | construction, no-go ภายใน domain, equivalence หรือ prerequisite ที่เจาะจง; ไม่ต้องได้ฟิสิกส์ใหม่ |
| Acceptance | proof/counterexample พร้อม exact algebraic controls, full-state response, independent work/loss integration และ negative controls |
| Stop / reopen | หยุดเมื่อคำถามนี้ตัดสินได้; เปิดต่อเมื่อมี sourced requirement หรือ independent restriction/state/preparation/readout ที่เปลี่ยนคำตัดสิน ไม่ rerun เดิมเพื่อเพิ่มกิจกรรม |
| Reviewer question | ผู้เชี่ยวชาญ dynamical systems ตรวจ branch admissibility/degenerate minima และดูว่า exact reachability ภายใต้สองพอร์ตต่างจาก constrained physical writing อย่างไร |
| Non-goals | ไม่ noise/lifetime, trajectories, fitted parameters, material search, physical detector, redesign, Core/README/gates หรือ publication |

<a id="regime-law"></a>
## 2. สมการ ขอบเขตตัวแปร และบัญชีเดียวกัน

เพื่ออ่านพีชคณิตสั้นลง เขียน $a=a_C,\ b=b_C,\ \alpha=a_\Phi,\ \beta=b_\Phi$
และ $M_C,M_\Phi,\tau$ ตามเดิม:

\[
\Omega=\frac a2 C^2+\frac b4 C^4+
\frac\alpha2\Phi^2+\frac\beta4\Phi^4-\frac g2C^2\Phi,
\quad b,\beta,M_C,M_\Phi,\tau>0,\quad\alpha,g\ge0,\quad a\in\mathbb R.
\]

\[
\mu_C=C(a+bC^2-g\Phi),\qquad
\mu_\Phi=\alpha\Phi+\beta\Phi^3-\frac g2C^2,
\]
\[
\dot C=-M_C\mu_C+J_C,\quad \dot\Phi=\Pi,\quad
\tau\dot\Pi=-\Pi-M_\Phi\mu_\Phi+J_\Phi.
\]

การลดนี้ให้ spatial derivatives เป็นศูนย์เท่านั้น κ ทั้งสองยังเป็นบวก
`a_space<0` และ `coupling_g<0` ถูก source ปฏิเสธ จึงไม่เปิด negative-α lane เพื่อสร้างผล
หลังเขียนใช้ $J_C=J_\Phi=0$ ไม่มี background drive
Ω ในเอกสารนี้เป็น homogeneous density/หนึ่งหน่วย normalized measure;
ไม่ยกปัจจัย N=4 จากงานโซ่เก่ามาคูณ หรือเรียกค่าหนึ่งหน่วยนี้ว่า joule

| วัตถุ | หน้าที่ | หน่วย/ที่มาและขอบเขต |
| --- | --- | --- |
| C, Φ, Π | independent state; Π คืออัตรา Φ | normalized coordinates/clock เดิม ไม่ระบุสารหรือวัสดุ |
| a,b,α,β,g | potential coefficients | allowed source configuration; ไม่ fit และไม่เปลี่ยนระหว่าง histories |
| M_C,M_Φ,τ | kinetics/relaxation coefficients | positive source configuration; energy อย่างเดียวไม่ได้ derive ค่าเหล่านี้ |
| μ_C,μ_Φ | derivatives ของ Ω | ไม่ใช่ state ใหม่หรือ physical force SI โดยอัตโนมัติ |
| J_C,J_Φ | additive source ports | อยู่คนละ normalization กับ conjugate force; steady bias ที่เทียบได้คือ J_C/M_C และ J_Φ/M_Φ |
| E | Ω+τΠ²/(2M_Φ) | one normalized ledger, interaction นับครั้งเดียว |
| C²,Φ,Π,abs(C) | readout views | ไม่มีอุปกรณ์ที่สอบเทียบ; abs(C) ไม่ differentiable ที่ศูนย์ |
| A,B,Δ,k,h,v | derived combinations | สัญลักษณ์ย่อ ไม่ใช่ coefficients หรือ state เพิ่ม |

Ω coercive เพราะ quartic coefficients ทั้งสองเป็นบวกและ dominate cubic coupling
ที่ระยะ state ใหญ่ จึงมี global minimum ทางคณิตศาสตร์ แต่ยังไม่ใช่ physical Gibbs ensemble
หรือ entropy/temperature dictionary ของวัสดุ

<a id="regime-classification"></a>
## 3. จำแนก stationary states ครบ domain ที่ประกาศ

### 3.1 เก็บ branch ศูนย์ก่อน

stationary ต้องมี Π=0 และ μ ทั้งสองเป็นศูนย์ ถ้า C=0 จะได้

\[
\Phi(\alpha+\beta\Phi^2)=0\quad\Rightarrow\quad\Phi=0.
\]

ดังนั้น $x_0=(0,0,0)$ มีเสมอ ห้ามหารด้วย C แล้วทำ branch นี้หาย
Hessian ที่ศูนย์คือ diag(a,α); ค่า eigenvalue ศูนย์ต้องตรวจเทอมถัดไป ไม่ใช่ตัดสิน unstable

ถ้า g=0 สมการแยกกัน: Φ=0 เสมอ; C=0 และเมื่อ a<0 มี

\[
C=\pm\sqrt{-a/b}.
\]

สำหรับ g>0 และ C≠0, μ_Φ=0 บังคับ Φ>0 เพราะ β>0 และ

\[
C^2=\frac{g\Phi-a}{b}=\frac{2\Phi(\alpha+\beta\Phi^2)}g>0.
\]

เหลือ cubic แต่ **ต้องตรวจ admissibility**:

\[
p(\Phi)=\beta\Phi^3-A\Phi+B=0,
\quad A=\frac{g^2}{2b}-\alpha,\quad B=\frac{ga}{2b},
\quad\Delta=4A^3-27\beta B^2.
\]

discriminant จริงของ polynomial p คือ βΔ; β>0 ทำให้ใช้ sign ของ Δ ได้
รากลบไม่ให้ real nonzero C ที่ stationary ใน domain นี้ และราก Φ=0 ที่ a=0
กลับไป branch ศูนย์ ไม่ใช่ state ใหม่

### 3.2 Hessian ของ full Ω ไม่ใช่ curvature ของ cubic อย่างเดียว

\[
H=\begin{pmatrix}a+3bC^2-g\Phi&-gC\\-gC&\alpha+3\beta\Phi^2\end{pmatrix}.
\]

บน nonzero branch:

\[
H_{CC}=2bC^2>0,\qquad \det H=2bC^2p'(\Phi).
\]

ดังนั้น p′>0 ให้ SPD/strict minimum; p′<0 ให้ saddle ส่วน p′=0 ต้องดู leading terms
การ eliminate $C^2=(g\Phi-a)/b$ ใช้เฉพาะ stationary geometry:

\[
\Omega_{\rm valley}(\Phi)=
\frac\alpha2\Phi^2+\frac\beta4\Phi^4-\frac{(g\Phi-a)^2}{4b},
\qquad \Omega'_{\rm valley}=p(\Phi),
\]

ไม่ใช่การตั้งให้ C equilibrate ทันทีระหว่าง response หรือเขียนกฎ Φ ใหม่

### 3.3 ตารางผลทั่วไปและขอบเขต degenerate

| เงื่อนไข | Stationary states ที่ admissible | Minima และ stability |
| --- | --- | --- |
| g=0,a>0 | ศูนย์เท่านั้น | strict global minimum; SPD ถ้า α>0; α=0 ยัง strict แต่ nonhyperbolic |
| g=0,a=0 | ศูนย์เท่านั้น | strict global minimum จาก bC⁴/4 และ αΦ²/2+βΦ⁴/4; nonhyperbolic |
| g=0,a<0 | ศูนย์และคู่ ±sqrt(−a/b),Φ=0 | ศูนย์ unstable/saddle; คู่ nonzero เป็น global minima; α=0 ให้ strict nonhyperbolic minima |
| g>0,a<0 | ศูนย์และหนึ่ง positive-Φ root ให้คู่ ±C | คู่ nonzero เป็น SPD global minima; ศูนย์ unstable |
| g>0,a=0,A≤0 | ศูนย์เท่านั้น | strict global minimum แต่ nonhyperbolic; A=0 ไม่ใช่ unstable โดยอัตโนมัติ |
| g>0,a=0,A>0 | ศูนย์และ Φ=sqrt(A/β),C²=gΦ/b | คู่ nonzero เป็น SPD global minima; ศูนย์ไม่เป็น minimum |
| g>0,a>0,A≤0 หรือ A>0,Δ<0 | ศูนย์เท่านั้น | strict global minimum; α=0 ไม่ใช้ linear Hurwitz/DC-inverse conclusion |
| g>0,a>0,A>0,Δ=0 | ศูนย์และ positive double-root Φ_d=sqrt(A/(3β)) ให้คู่ ±C | ศูนย์ minimum; nonzero points degenerate แต่ไม่เป็น minima |
| g>0,a>0,A>0,Δ>0 | ศูนย์; สอง positive roots ให้สองคู่ ±C | ศูนย์ minimum; root เล็กเป็น saddle pair; root ใหญ่เป็น SPD minimum pair |

เหตุผล root count ไม่อาศัย discriminant เพียงอย่างเดียว:

- ถ้า a<0, B<0: p(0)<0; ถ้า A≤0 p เพิ่มบนแกนบวก ถ้า A>0 p ลดถึงจุดต่ำสุดก่อน
  แล้วเพิ่มสู่ +∞ จึงมี positive root เพียงหนึ่งและ p′>0 ที่ root นั้น
- ถ้า a=0: $p=\Phi(\beta\Phi^2-A)$ แล้วคัด Φ>0 จึงได้ผลในตาราง
- ถ้า a>0, B>0: ถ้า A≤0 ไม่มี positive root; ถ้า A>0 จุดต่ำสุดฝั่งบวกอยู่ที่
  $d=\sqrt{A/(3\beta)}$, $p(d)=B-2A^{3/2}/(3\sqrt{3\beta})$
  sign นี้กับ B>0 ให้สอง/หนึ่ง double/ศูนย์ positive roots ตาม Δ>0/=0/<0
  รากที่สามกรณี Δ>0 เป็นลบ ต้องทิ้ง ไม่ใช่ “มีสาม real roots จึงมีสาม stable branches”

การตรวจ leading energy ที่ boundaries:

1. a=0 ใช้ identity exact
   \[
   \Omega=\frac b4(C^2-g\Phi/b)^2-\frac A2\Phi^2+\frac\beta4\Phi^4.
   \]
   A≤0 จึงมีศูนย์เป็นจุดต่ำสุดเดียว; ที่ A=0 square กับ βΦ⁴ ยังบวกนอกศูนย์
   บน valley $\Phi=bC^2/g$ เทอมแรกหายแต่เหลือเทอมบวกอันดับ C⁸
   ถ้า A>0 ทาง valley ฝั่ง Φ>0 ให้พลังงานต่ำกว่าศูนย์ใกล้จุดเดิม จึงไม่ใช่ minimum
2. a>0,α=0: เลือก neighborhood $|\Phi|<a/(2g)$ เมื่อ g>0 จะได้
   \[
   \Omega\ge aC^2/4+bC^4/4+\beta\Phi^4/4,
   \]
   จึงยัง strict minimum แม้ Hessian มี eigenvalue ศูนย์ (g=0 เห็นได้ตรง ๆ)
3. ที่ positive double root p=p′=0 และ $\Omega'''_{\rm valley}/6=\beta\Phi_d>0$
   leading change เป็นลูกบาศก์ที่กลับเครื่องหมาย จึงไม่ใช่ minimum แม้ curvature ศูนย์

Strict minima ที่ degenerate อาจเสถียรแบบ nonlinear ภายใต้กฎเดิมได้: E เป็น local
positive energy และ loss=0 ที่เป็น invariant ต้องมี μ_C=μ_Φ=Π=0 ด้วย
ใน neighborhood ของ isolated minimum จึงใช้ LaSalle ได้ แต่ไม่อนุมาน exponential rate,
Hurwitz Jacobian หรือ finite linear susceptibility จากข้อสรุปนี้

### 3.4 Local กับ global และสิ่งที่ยังไม่ใช่ lifetime

ใน coexistence ให้ Φ_h เป็นรากบวกใหญ่และใช้ค่าพลังงานเดิม ไม่ตัด well offsets ออก:

\[
E_h=\frac\alpha2\Phi_h^2+\frac\beta4\Phi_h^4-
\frac{(g\Phi_h-a)^2}{4b},\qquad E_0=0.
\]

E_h<0: คู่ nonzero เป็น global minima; E_h>0: ศูนย์เป็น global minimum;
E_h=0: ทั้งสาม minima มีพลังงานเท่ากัน quartic coercivity และรายการ minima ที่ครบ
ทำให้กฎเลือกด้วย sign นี้เพียงพอ ไม่ต้องกำหนด thermal ensemble เพิ่ม
การเป็น higher-energy local minimum **ไม่ให้** thermal escape probability หรือ lifetime
เพราะรอบนี้ไม่มี noise/bath/preparation model และไม่ได้คำนวณ basin ทั้งหมด

<a id="regime-response"></a>
## 4. ความไวจาก full C–Φ–Π และสอง source ports

ที่ nondegenerate minimum ตั้ง $k=H_{CC},h=H_{\Phi\Phi},v=gC_*,d_H=kh-v^2>0$
ใช้ zero perturbation initial state รอบ operating point เดียวกัน และ same normalized clock:

\[
L=\begin{pmatrix}-M_Ck&M_Cv&0\\0&0&1\\
M_\Phi v/\tau&-M_\Phi h/\tau&-1/\tau\end{pmatrix},\quad
B_{\rm port}=\begin{pmatrix}1&0\\0&0\\0&1/\tau\end{pmatrix},
\quad K=\begin{pmatrix}1&0&0\\2C_*&0&0\\0&1&0\\0&0&1\end{pmatrix}.
\]

K ให้แถว baseline-subtracted C,C²,Φ,Π ตามลำดับ derivative ของ C² คือ 2C_*
ไม่ใช่การเอา perturbation มายกกำลังสอง และที่ C_*=0 แถวนั้นเป็นศูนย์อันดับหนึ่ง

\[
D(z)=(z+M_Ck)(\tau z^2+z+M_\Phi h)-M_CM_\Phi v^2,
\qquad \det(zI-L)=D(z)/\tau.
\]

\[
T(z)=K(zI-L)^{-1}B_{\rm port}
=\frac1{D(z)}\begin{pmatrix}
\tau z^2+z+M_\Phi h&M_Cv\\
2C_*(\tau z^2+z+M_\Phi h)&2C_*M_Cv\\
M_\Phi v&z+M_Ck\\
zM_\Phi v&z(z+M_Ck)
\end{pmatrix}.
\]

ไม่มีการทิ้ง Π หรือ τ; stationary elimination ใช้แทน frequency-dependent response นี้ไม่ได้
DC ของสองแถว C,Φ คือ

\[
G(0)=H^{-1}\operatorname{diag}(M_C^{-1},M_\Phi^{-1})
=\frac1{d_H}\begin{pmatrix}h/M_C&v/M_\Phi\\v/M_C&k/M_\Phi\end{pmatrix}.
\]

ดังนั้น H⁻¹ เฉย ๆ ตรงกับ conjugate biases ไม่ใช่ ports ดิบทุกกรณี
ที่ origin a,α>0: C/J_C=1/(M_Ca), C/J_Φ=0,
Φ/J_C=0 และ Φ/J_Φ=1/(M_Φα) ส่วน Π DC เป็นศูนย์
ไม่ใช้ relative error หารช่องศูนย์ และไม่ใช้สูตร H⁻¹ ที่ singular boundary

สำหรับ coexistence ที่ a,α>0 ทั้ง origin และ nonzero minimum เป็น SPD จึงเทียบกันได้:
ช่อง C/J_Φ DC ต่างขนาดแน่นอน เพราะศูนย์เทียบกับ v/(M_Φ d_H)≠0
ส่วนช่อง C/J_C DC ต่างก็ต่อเมื่อ \(a h_h\ne d_{H,h}\)
ไม่กำหนด ordering เดียวทั่ว regime; inequality G_h>G_0 ใน §5 เป็นผลเฉพาะ control ที่ล็อก
หาก DC ช่องนี้บังเอิญเท่ากัน ก็ยังไม่ทำให้ transfer functions ทั้งเส้นเท่ากัน:

\[
T_{h,CJ_C}(z)-\frac1{z+M_Ca}
=\frac{M_C[(a-k_h)(\tau z^2+z+M_\Phi h_h)+M_\Phi v_h^2]}
{D_h(z)(z+M_Ca)}.
\]

numerator จะเป็นศูนย์ทุก z ต้องมี k_h=a และ v_h=0 ซึ่งขัดกับ nonzero branch ที่ g>0
ข้อสรุปนี้ไม่บอกว่าขนาดต่างกันที่ทุกความถี่ หรือให้ mixed-port protocol โดยอัตโนมัติ
กรณี α=0 เก็บ nonlinear origin minimum ไว้ในตาราง แต่ไม่อ้าง SPD/full linear DC result ที่ origin

### 4.1 Stability โดยไม่ใช้ floating eigenvalues

\[
P=\begin{pmatrix}k&-v&0\\-v&h&0\\0&0&\tau/M_\Phi\end{pmatrix}>0,
\quad w=(k,-v,0),\ e_\Pi=(0,0,1),
\]
\[
L^TP+PL=-2M_Cw^Tw-2e_\Pi^Te_\Pi/M_\Phi.
\]

ถ้ามี eigenmode ที่ Re(z)=0 มันต้องมี wδx=0 และ δΠ=0 ด้วย
แต่ matrix ที่มีแถว e_Π, L แถวสาม, w มี determinant $M_\Phi d_H/\tau>0$
จึงไม่มี nonzero zero-loss eigenmode ⇒ ทุก pole อยู่ซีกซ้าย
เป็นข้อพิสูจน์เฉพาะ SPD branches ไม่ย้ายไปใช้ที่ flat boundaries

บน nonzero saddle ที่ det H<0 มี D(0)=M_CM_Φ det H<0 แต่ D(z)→+∞ บนแกน z>0
จึงมี positive real pole: instability ไม่ได้อนุมานจากคำว่า saddle อย่างเดียว
ที่ origin a<0 ก็มี eigenvalue −M_Ca>0 โดยตรง ส่วน degenerate saddle-node
ตัดสินว่าไม่เป็น minimum จาก cubic leading term ไม่ใช้สูตร SPD ฝืนเข้าไป

### 4.2 ผล U เดิมกลับมา และสิ่งที่การอ่าน magnitude ไม่ได้แก้

ให้ R=diag(−1,1,1), S_in=diag(−1,1), S_out=diag(−1,1,1,1)
reflection เปลี่ยน C และ J_C พร้อมกัน; v กับ C_* เปลี่ยนเครื่องหมาย
แล้ว (T_-=S_{out}T_+S_{in}) จึงมีขนาดเท่ากันทีละ entry สำหรับคู่ ± ที่มี Φ เดียวกัน
แทน unit coefficients ของ U แล้วได้ transfer ที่บันทึกไว้ทุก entry โดยไม่ได้รัน U ใหม่

เมื่ออ่าน |C| ใกล้ nonzero branch ใช้ derivative sign(C_*) ได้ แต่ที่ศูนย์
left/right derivatives ต่างกัน จึงไม่มี ordinary linear transfer ของ |C| ตรงนั้น
ยังเทียบ magnitude ของ transfer C ได้ เพราะเป็นคนละ operation กับ readout |C|
ส่วน C² มี zero linear response ที่ศูนย์; ไม่ได้แปลว่า finite response ทุกอันดับเป็นศูนย์

ผลนี้ไม่ครอบคลุม simultaneous mixed inputs, mixed readouts, finite-amplitude switching,
เวลารอที่ยังมี transients หรือ physical detector ที่ไม่ได้ประกาศ

<a id="regime-controls"></a>
## 5. สอง exact controls ที่ล็อกไว้ก่อนตรวจ

ทั้งสองใช้ $M_C=M_\Phi=\tau=\kappa_C=\kappa_\Phi=1$ เฉพาะ regression
ไม่ใช่ defaults ของโครงการ และไม่ใช้ numerical root search

### 5.1 Coexistence control

\[
a=3/8,\quad \alpha=b=\beta=1,\quad g=2,
\quad A=1,\ B=3/8,\ \Delta=13/64>0,
\]
\[
p(\Phi)=\Phi^3-\Phi+3/8
=\frac{(2\Phi-1)(4\Phi^2+2\Phi-3)}8.
\]

| Φ root / state | C² | Hessian / admissibility | คำวินิจฉัย |
| --- | --- | --- | --- |
| origin Φ=C=0 | 0 | H=diag(3/8,1)>0 | strict minimum |
| −(sqrt(13)+1)/4 | −(4sqrt(13)+7)/8 | C²<0 และ Φ<0 | ทิ้ง ไม่ใช่ real state |
| 1/2 | 5/8 | det H=−5/16 | saddle pair ไม่ใช่จุดเก็บที่เสถียร |
| (sqrt(13)−1)/4 | (4sqrt(13)−7)/8 | det H=(73sqrt(13)−247)/32>0 | strict minimum pair |

positivity สุดท้ายตรวจด้วย $73^2\,13>247^2$, H_CC>0 และ exact stationary residual
ไม่ใช้ floating eigenvalues

สำหรับ C/J_C DC:

\[
G_0=8/3,\qquad
G_h=\frac{4(29-3\sqrt{13})}{73\sqrt{13}-247},\qquad
G_h-G_0=\frac{1376\sqrt{13}-1196}{2067}>0.
\]

จึงต่างทั้งขนาด ไม่ใช่เพียง sign/baseline; inequality ใช้ exact square comparison
ส่วน C/J_Φ: origin เป็นศูนย์ แต่ branch ±h ให้

\[
G_{h,CJ_\Phi}=\frac{2C_h}{\det H_h}\ne0.
\]

ไม่หารผลด้วย zero-gain reference แสดง zero-versus-nonzero ตรง ๆ
ทั้งสอง probes ใช้ **ทีละ port** ที่พารามิเตอร์/clock/readout เดียวกัน

\[
E_h-E_0=\frac{-83+26\sqrt{13}}{256}>0
\quad(26^2\,13>83^2).
\]

ดังนั้น origin เป็น global minimum ใน control นี้ ส่วน nonzero pair เป็น local minima
ที่สูงกว่า ไม่ใช่ equal-energy memory และไม่ได้ให้ noise lifetime

### 5.2 Non-coexistence control

\[
a=\alpha=b=\beta=g=1,\qquad A=-1/2,\ B=1/2.
\]

$p=\Phi^3+\Phi/2+1/2$ เพิ่มและเป็นบวกบน Φ>0
จึงไม่มี admissible nonzero stationary state; origin เป็น minimum เดียว
การที่ exact control นี้ไม่มี coexistence เป็นผลที่คงไว้ ไม่ retune เพื่อให้ผ่าน

<a id="regime-write"></a>
## 6. เขียนจาก common state และตรวจ normalized ledger

### 6.1 Construction ที่ไม่ใช่การตั้งสอง initial conditions ต่างกัน

ใน coexistence control เริ่มทั้ง histories จาก ((0,0,0)) และใช้ coefficients ชุดเดียวกัน
history H0 อยู่ศูนย์โดย sources เป็นศูนย์; history Hh ใช้ finite write ไปหา

\[
(C_h,\Phi_h,0),\qquad
\Phi_h=(\sqrt{13}-1)/4,\quad C_h=\sqrt{(4\sqrt{13}-7)/8}.
\]

เลือกปลายทางลบได้ด้วย reflection โดยค่าพลังงานเท่าเดิม ไม่จำเป็นต้องเพิ่ม control ใหม่
สำหรับ $0\le t\le T_w$, ให้ u=t/T_w และ

\[
S=10u^3-15u^4+6u^5,\quad
C=C_iS,\quad\Phi=\Phi_iS,\quad\Pi=\Phi_iS'/T_w,
\]
\[
J_C=\dot C+M_C\mu_C,\qquad
J_\Phi=\tau\dot\Pi+\Pi+M_\Phi\mu_\Phi.
\]

แทนกลับ RHS ได้ trajectory นี้แบบ exact (prescribed polynomial ไม่ใช่ numerical integration)
S(0)=0,S(1)=1 และ S′=S″=0 ที่ปลายทั้งสอง จึงมี state/velocity ที่ตรงตามกำหนด
และ sources ต่อเนื่องเป็นศูนย์ที่ stationary endpoints
เมื่อปล่อย inputs หลัง T_w state เป็น equilibrium ของสมการเดิม จึงคงอยู่แบบ deterministic

ไม่อ้าง controls เรียบทุกอันดับ: S‴(0)=S‴(1)=60; โดยทั่วไป derivative ของ J_Φ กระโดด
เมื่อขยาย inputs ให้เป็นศูนย์ภายนอกช่วงเขียน sources ยัง continuous/bounded สำหรับ T_w>0
construction ไม่กำหนด actuator limit, disturbance tolerance หรือ switching threshold
จึงเป็น mathematical reachability ไม่ใช่หลักฐานการเตรียม apparatus หรือ finite-wait reset

### 6.2 Pointwise กับ integrated balance ที่คำนวณแยก

\[
E=\Omega+\frac\tau{2M_\Phi}\Pi^2,\qquad
\dot E=-M_C\mu_C^2-\Pi^2/M_\Phi+
\mu_CJ_C+\Pi J_\Phi/M_\Phi.
\]

ให้ $\mathcal D=\int_0^{T_w}(M_C\mu_C^2+\Pi^2/M_\Phi)dt$
และ $W=\int_0^{T_w}(\mu_CJ_C+\Pi J_\Phi/M_\Phi)dt$
producer ขยายแต่ละ integrand เป็น polynomial แล้ว integrate แยกกัน ไม่กำหนด W จาก ΔE+D
แล้วอ้างว่าได้ตรวจ identity จากนั้นตรวจทั้ง pointwise residual และ

\[
W-\mathcal D=E(T_w)-E(0).
\]

เขียน $X=C_i^2,Y=\Phi_i$ จะมี

\[
\mu_C/C_i=aS+bXS^3-gYS^2,\quad
\mu_\Phi=\alpha YS+\beta Y^3S^3-gXS^2/2.
\]

นี่เป็นการ factor สัญลักษณ์สำหรับ polynomial arithmetic ไม่ใช่หาร C_i=0 ใน source จริง
ประวัติศูนย์แทน X=Y=0 แล้วได้ W=D=ΔE=0
ประวัติ nonzero มี loss อย่างน้อยจาก Π:

\[
\int_0^{T_w}\Pi^2/M_\Phi\,dt=10Y^2/(7M_\Phi T_w)>0.
\]

สำหรับ exact regression T_w=1 (ไม่ใช่หนึ่งวินาที):

\[
\mathcal D_h=
\frac{229790000785-30488096005\sqrt{13}}{197474944128},
\]
\[
W_h=\mathcal D_h+\frac{-83+26\sqrt{13}}{256}.
\]

artifact เก็บ W จาก integration ของ power โดยตรงด้วยรูปพีชคณิตที่เทียบเท่ากัน
ทั้ง D_h>0 และ ΔE_h>0 ตาม proof ข้างต้น จึง W_h>0 ต่างจาก H0 ตรง ๆ
ไม่เติม compensation เพื่ออ้าง equal work/equal energy และไม่ใช้ normalized work/loss
แทน SI heat, entropy หรือ total entropy production

<a id="regime-verdict"></a>
## 7. คำวินิจฉัยและสิ่งที่แคบลงจริง

| คำถาม | ผลใน scope | สิ่งที่ไม่ตามมา |
| --- | --- | --- |
| คู่ ± ของ U มีขนาด gain ต่างหรือไม่ | ไม่ต่างใน eight separate single-port channels เดิม; recover ผล U ครบ | ไม่ใช่ family-wide no-go และไม่ครอบคลุม mixed protocols |
| family เดิมมี stable states ที่ gain ต่างจริงหรือไม่ | มีใน coexistence regime A>0,Δ>0,a>0; ต้องมี α>0 หากเปรียบเทียบทั้งสองด้วย SPD linear response; exact control แสดง zero/nonzero contrast | ไม่ใช่ทุก coefficient set/ความถี่ และไม่ใช่ physical detector response |
| เขียนถึงจาก common state ได้หรือไม่ | ได้ภายใต้สอง source ports เดิมด้วย finite polynomial construction | ไม่ได้ให้ actuator feasibility, same work/energy หรือ robust/lifetime guarantee |
| เป็น memory แบบใด | เก็บ operating point/phase ใน state แล้วเปลี่ยน small-signal sensitivity | ไม่จำเป็นต้องเปลี่ยน fundamental law และไม่เท่ากับ internal topology learning |
| ได้ improvement/generalization หรือไม่ | ยังไม่มี objective/task/transfer criterion อิสระ | gain มากกว่าไม่เท่ากับทำงานดีกว่า |
| comparator | EQUIVALENT เมื่อใช้ generator, state, kinetics, ports และ readout เดียวกัน | ชื่อ UET ไม่ทำให้ prediction ต่างจาก standard multistability |
| physical C–Φ–Π | ยัง unresolved | formal pass ไม่ปิดวัสดุ/observer/quantum/cosmology/learning gates |

สิ่งที่เปลี่ยนคือ “unit fixture ยังไม่ให้ gain-magnitude contrast” ถูกจำกัดให้เป็นผลเฉพาะ
fixture/protocol; family มี conditional construction ที่ทำได้ โดยไม่มี term หรือ freedom ใหม่
แต่ **ความสามารถนี้ยังไม่เป็นข้อจำกัดเฉพาะ UET** และไม่ได้อนุญาตให้ยืมสเกลวัสดุจาก
platform ที่ correspondence ไม่ตรงมาใช้ ผล M–S, parent no-go และ physical controllers เดิมคงอยู่

### หนึ่งโจทย์ถัดไป และ prerequisite

**ตรวจข้อจำกัดอิสระหนึ่งข้อของการเขียน/อ่านที่ข้อเสนอผู้เขียนต้องการจริง เทียบกับ
multistable comparator ชุดเดียวกัน** ไม่ใช่เพิ่ม state, topology law หรือหา material ใหม่ทันที
ก่อนเปิดงานต้องมีต้นทางของ requirement (เช่น port ที่มีจริงและสิ่งที่ควบคุมได้,
readout/task ที่ต้องแยก หรือ parameter restriction ที่มีเหตุผลอิสระ)
พร้อม preparation และเกณฑ์ตัดสินตาม scope ไม่ให้ผู้เขียนคิดสมการใหม่แทน

ถ้า requirement นั้นยังได้สมการ/observable เดียวกับ comparator ให้สรุป equivalence แล้วหยุด
ถ้าเป็น mathematical restriction ให้ตัดสินเฉพาะ restriction; ถ้าเป็น physical claim ต้องกลับไป
`physical-parent-preparation` และปิด state/source/measurement dictionary ก่อน
ไม่มี input ที่เปลี่ยนคำตัดสินไม่ควร rerun หรือเปิด parameter sweep
รอบนี้จบที่ classification/response/write ledger นี้ ไม่เริ่มโจทย์ถัดไปอัตโนมัติ

คำถามผู้ตรวจเฉพาะทางที่เตรียมไว้โดยยังไม่ติดต่อ:

- Dynamical systems: admissible-root classification, degenerate leading terms และ LaSalle scope
  ครบหรือไม่; full resolvent กับ static Hessian ใช้ตรง operating point/ports หรือไม่
- Control theory: exact two-port write ต้องมี constraints/preparation uncertainty อะไรเพิ่ม
  ก่อนจะอ้าง reachability ของ physical apparatus; ไม่ขอให้ตรวจทั้งทฤษฎี UET
- Statistical mechanics: มีเหตุผลอิสระใดให้ Ω/normalized sources เป็น physical energy/work
  ใน realization ที่ระบุ; mathematical minimum อย่างเดียวตอบเรื่อง noise lifetime ไม่ได้

<a id="regime-reproduce"></a>
## 8. หลักฐาน การทำซ้ำ และขอบเขตการตรวจรับ

FORMAL package เดียว:

- [Contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/retained_response_regime_classification.json)
- [Producer](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Retained_Response_Regime_Classification.py)
- [Regression/adversarial tests](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_retained_response_regime_classification.py)
- [Compact artifact](../topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_retained_response_regime_classification.json)

ใช้ Python กับ SymPy 1.14.0 ที่มีอยู่แล้ว ไม่มี installation:

```text
python docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Retained_Response_Regime_Classification.py --check
python -m unittest discover -s docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research -p test_t13_retained_response_regime_classification.py
python docs/scripts/audit/audit_calculation_completeness.py --check
```

`--check` เปรียบเทียบกับ artifact โดยไม่เขียนไฟล์; `--emit-report` เป็นโหมดเขียน
artifact ใหม่นี้โดย explicit เท่านั้น identity mismatch ต้องหยุดก่อน calculate
ไม่มี network, old `calculate/main`, numerical roots, Monte Carlo, sweep หรือ trajectory
ในเครื่องรอบนี้ใช้ bundled Python3.12 และ pure-Python packages ที่มีใน repo venv ผ่าน
PYTHONPATH ไม่ได้เพิ่ม runtime หรือทำให้สภาพแวดล้อมนั้นกลายเป็นหลักฐานทางฟิสิกส์

การตรวจครอบคลุม source domain/RHS, origin/admissible roots, Hessian/degeneracy,
full/static response, U recovery, finite-write endpoints/source continuity,
pointwise/integrated ledger, comparator และขอบเขตข้ออ้าง
negative controls ตรวจ alpha ที่ห้ามใช้, missing mobility/τ, baseline แทน gain,
abs(C) derivative ที่ศูนย์, C² derivative, static-as-dynamic substitution,
retuning histories, mixed protocol, local/global/lifetime และ physical promotion
การผ่าน tests เป็น implementation evidence ไม่ใช่การพิสูจน์จาก sampling แทนบทอนุมาน §§3–6

ผลตรวจการทำซ้ำจริง จำนวน checks และ preservation ก่อน commit บันทึกใน
[Topic UPDATE_LOG](../topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md)
และ [WORK_LEDGER](../../WORK_LEDGER/2026/2026-10-25.md)
โดยไม่ย้ายผลตรวจเอกสารไปเป็น physics gate และไม่คัดรายงาน U/M–S มาซ้ำทั้งชุด
