# ขอบเขตสเกลและความคลาดเคลื่อนของการแกว่ง Φ

> ตรวจถึง 25 ตุลาคม 2026 — FORMAL observable-specific analysis; ไม่ใช่ physical validation

## 1. ฐานหลักฐานและ bounded research card

ฐาน local commit `62f8efe0558e2c7f40aac1785c2b7cc780727953` จากรอบ Q;
สาขาใหม่ `codex/research/phi-variance-admissibility` ใน worktree เดิม
ก่อนเริ่มมีงานค้าง463รายการ indexว่าง และ Topic-log working diff578/79เดิม
ต้องไม่รวมงานเหล่านั้นใน scoped commit นี้ daily ledger ของวันที่25มี Q อยู่แล้ว
เพิ่มเฉพาะงานใหม่ ไม่เขียนประวัติ Q ทับ

อ่าน remote-tracking `origin/main` ในเครื่องได้
`6da62c33f6e61311990f4588b44c7737f089710e` แต่ไม่ได้ fetch/ยืนยัน public main สด
งานและหลักฐานใหม่นี้จึงเป็น local evidence ไม่ใช่ release

| รายการ | คำถามและขอบเขต |
| --- | --- |
| Proposition | variance ของ Φ จาก harmonic reference ใกล้ classical parent ที่ normalize ภายใน local ball ได้ภายใต้ error bound ใด และ harmonic classicality จำกัดสเกลอย่างไร |
| มีแล้ว | [Q](UET_PARENT_STATIC_REFERENCE_AUDIT.md): stationary AF reference, full stiffness/root uncertainty และหกรัศมีที่รับรอง curvature; [P](UET_LATTICE_BATH_REDUCTION_AUDIT.md) กับ [O](UET_LATTICE_MECHANICAL_STATE_CONSTRUCTION.md) ใช้ตามขอบเขตเดิม |
| Identity | Q14/P20/O14/N13/M11/thermal8 identities ตรงก่อนเริ่ม;38 protected normalized hashes เก็บไว้ ไม่รัน producers เก่า |
| ขาด/โต้แย้ง | bound ของ variance โดยตรง, mean shift/surface terms และ observable-specific quantum correction; ยังไม่มี material scales/error policy |
| Controller | Q contract component `physical-parent-preparation`; quantum parent correspondence ยังเป็นช่องว่างแยก ไม่ย้ายขอบเขตเงียบ ๆ |
| Action / why | สร้าง moment bounds ของ observable เดียวจาก measure/energy เดิม เพื่อแยกขอบเขตประมาณที่หยาบจากข้อจำกัดทางกายภาพ |
| Outcomes | derived bound / conditional scale set / counterexample / unresolved prerequisite; ไม่จำเป็นต้องได้วัสดุจริงหรือผลสนับสนุน UET |
| Stop | ตรวจเพียงวิธี A และ B ตามแผน ไม่ค้น roots/radii/material หรือเพิ่ม model term; สองความพยายามไม่เพิ่มหลักฐานให้หยุดเส้นทางนั้น |
| Reviewer | numerical verification/statistical mechanics: ตรวจ variance centering, finite-boundary moments และการแยก classical/quantum comparator |
| Non-goals | ไม่มี trajectories, lifetime, spin flips, bath/damping, datasets, detector, physical acceptance หรือ Core/API/defaults/README/gate changes |

ผู้เขียนเลือกคง parent เดิมและใช้ variance ของ Φ เป็นหลัก โดยยังไม่เลือกวัสดุ
Imported physics คือ canonical statistics และ quantum harmonic oscillator
การเลือกสองวิธีสร้าง bounds กับการจัด error ledger เป็นงานของ AI ที่ต้องตรวจได้
ไม่ใช่ข้อเสนอพื้นฐานใหม่หรือหลักฐานการยอมรับทางฟิสิกส์จากผู้เขียน

System partition: frozen alternating labels + สาม internal canonical pairs เดิม
Φ, Π, gaps, population C และ endpoint เป็น views; variance เป็น functional
ของ distribution ไม่ใช่ state/trace/สารข้อมูลอิสระ ไม่มี detector หรือ source port ใหม่

## 2. สรุปสำหรับผู้เขียน

รอบนี้ปิดคำถามได้ในระดับ **ขอบเขตที่เพียงพอของ observable หนึ่งตัว**:
การแกว่งของ Φ รอบค่าเฉลี่ยของตัวมันเอง ไม่ใช่ตำแหน่งจุดสมดุล
และไม่ใช่ค่าเฉลี่ยกำลังสองรอบจุดสมดุลโดยไม่หัก mean shift

1. Harmonic reference ให้ `Var(Φ)=θ c_h` โดย `c_h` ขึ้นกับ stiffness
   ของสามโหมดร่วมกัน ไม่ใช่ stiffness ของ Φ โดด ๆ การรวมโหมดภายในออก
   ไม่ได้ลบผลของ coupling หรือทำให้เหลือ variance ของ fixed-Φ ensemble
2. สร้างขอบเขต classical-parent variance ได้สองวิธีตามแผน
   วิธี A ใช้พลังงานคลาดเคลื่อนสูงสุดและ Gaussian tail ซึ่งอาจหยาบมาก
   วิธี B ใช้โมเมนต์พร้อมเทอมขอบบริเวณและ mean shift; ที่รัศมีเดิมคงที่
   ขอบเขตวิธี B ลดสู่ศูนย์เมื่อ θ ลดสู่ศูนย์ใน **classical restricted model**
3. แต่ quantum correction ของ harmonic comparator มีขอบเขตแปรตาม `χ²/θ²`
   ในระบบกายภาพเดิม χ คงที่ จึงไม่อนุมานว่าทำให้เย็นลงอย่างเดียวแล้ว
   ทั้ง approximation และ classicality จะผ่านพร้อมกันเสมอ
4. ได้ frontier แบบมีเงื่อนไขบน `μ d_ref² J_ref` และ θ แล้ว
   ยังไม่ได้ค่า μ, ระยะ, พลังงาน หรือ T ของวัสดุจริง และยังไม่ได้เลือก
   error budgets หรือยอมรับ physical window ใด

นี่เป็นความก้าวหน้าจาก free-energy/localization bounds ของ Q มาสู่
variance-specific bounds ไม่ใช่การค้นพบกลไกใหม่ หรือการแก้ global-parent no-go
ผลยังไม่ยืนยัน learning, persistence หรือจักรวาลเปิด และไม่เปลี่ยน physics gates

<a id="observable-and-covariance"></a>
## 3. Observable, measure และ joint covariance

### 3.1 สถานะและการเปรียบเทียบที่ไม่ปะปนกัน

ใช้ stationary point จริง `q_*` ที่ Q รับรองสำหรับ `-+-+` และ `+-+-`
ซึ่งสมมูลกันภายใต้ global flip เท่านั้น กำหนด

\[
y=(q-q_*)/d_{\rm ref},\quad
X=\Phi-\Phi_*=h^Ty,\quad h=(1/\sqrt5,0,0)^T,
\quad v(y)=V(q_*+d_{\rm ref}y)/J_{\rm ref}.
\]

ให้ `S_R={||y||≤R}` โดย R คือ dimensionless radius
`1/32,1/64,1/128,1/256,1/512,1/1024` จาก Q เท่านั้น
เขียน `v_*=v(0)`, `A=bar A=∇²v(0)` แล้วใช้สอง measure:

\[
p_{\rm loc}(y)=\frac{\mathbf1_{S_R}e^{-[v(y)-v_*]/\theta}}{Z_{\rm loc}},
\qquad p_H(y)\propto e^{-y^TAy/(2\theta)}\quad(y\in\mathbb R^3).
\]

Restricted parent นี้เป็นการ **นิยาม static measure บนบริเวณจำกัดโดยตรง**
ไม่ใช่ condition จาก normalized global parent Gibbs ที่ยังไม่มี
และไม่ใช่การเติมกำแพงหรือรับรองว่า distribution นี้ invariant ตามเวลา
Φ ยังผันผวนได้ใน joint ensemble; fixed-Φ ensemble ของ O ตอบคนละคำถาม

Canonical measure ก่อน integrate momenta คือ `d³q d³p/h_P³`
โดย `h_P=2πℏ` ไม่ใช่ readout vector h ใช้สาม canonical pairs หลังตัด CM
และมวล `μI` ในพิกัดความยาว q ตาม O/Q อินทิกรัล momenta และค่าคงที่
จากเปลี่ยน q เป็น y หักล้างใน normalized positional expectations
ไม่ได้ถูกตั้งให้ไม่มีผลต่อ absolute entropy และไม่ได้เพิ่ม hidden modes ซ้ำ
ฐาน canonical phase-space นี้รับจาก [Tong §2.1, Eq. (2.49)](https://www.damtp.cam.ac.uk/user/tong/statphys/statmechhtml/S2.html)

คู่เปรียบเทียบที่หนึ่งคือ `p_loc` กับ full classical `p_H`
คู่ที่สองคือ isolated quantum harmonic reference กับ classical `p_H`
**ไม่มีการเปรียบเทียบ actual quantum anharmonic parent ในรอบนี้**

### 3.2 Covariance และ Schur complement

Joint Gaussian ให้ `E_H y=0`, `Cov_H(y)=θ A⁻¹` ดังนั้น

\[
c_h=h^TA^{-1}h>0,\qquad V_H=\operatorname{Var}_H(\Phi)=\theta c_h.
\]

แบ่ง `A=[[a,gᵀ],[g,K]]`; K เป็น SPD และ
`s=a−gᵀK⁻¹g>0` การ complete square ใน u ให้

\[
\frac12 y^TAy
=\frac12(u+K^{-1}g y_Q)^TK(u+K^{-1}g y_Q)
+\frac12s y_Q^2,\qquad
V_H=\frac{\theta}{5s}.
\]

Hidden determinant เป็นส่วน normalization ของ marginal ไม่ใช่โหมดใหม่
`θ/(5a)` จะใช้ได้เมื่อ g=0 หรือมีเหตุผลอื่นให้ correction นั้นเป็นศูนย์
ไม่ใช่สูตรของ reference นี้ ไม่ใช้ `Θ=θ/4` แทน θ ใน total-energy stiffness

อ่าน interval stiffness ของ Q โดยตรง แล้ว invert ด้วย outward rational arithmetic
ได้ decimal enclosures ที่ปัดออกเพื่ออ่านง่ายดังนี้; rational endpoints เต็มอยู่ใน artifact:

| ปริมาณ | Enclosure / บทบาท |
|---|---|
| `c_h` | `[0.0106582350256, 0.0106582350260]`; dimensionless variance ต่อ θ |
| `s=κ_obs` สำหรับ h นี้ | `[18.7648329685, 18.7648329690]`; ไม่ใช่ coupling ใหม่ |
| ค่าที่ละ g: `1/(5a)` | ประมาณ0.0106129886715; ไม่ใช้เป็นคำตอบ |
| `ν_h=||A⁻¹h||` | ประมาณ0.0238444742267; artifact เก็บ interval ไม่ใช้เลขปัดรับรอง |
| `||h||` | `1/√5`; exact coordinate normalization |
| Root uncertainty | คง upper bound ประมาณ`3.0021×10⁻²³ d_ref` ของ Q ไม่ตั้งเป็นศูนย์ |

การขยายนี้อ้างอิง **root จริงใน certified box**; Q สร้าง curvature/third-derivative
enclosures ครอบคลุม root box แล้ว A จึงเป็น interval ของ stiffness ที่ root จริง
ไม่ใช่นำ Hessian midpoint มาใช้แบบ exact เพิ่มเติม ความไม่แน่นอนของตำแหน่ง root
เข้าสู่ stiffness/bounds เดิมและ enclosure ของ Φ_*; การเลื่อน origin คงที่
ไม่เปลี่ยน central variance จึงไม่บวก root-location error ซ้ำเป็น random variance
แต่ห้ามลบทิ้งจาก stiffness certificates

### 3.3 Endpoint ไม่ใช่ Φ เพียงตัวเดียว

จาก observation map เดิม

\[
L_{\rm end}=3d_{\rm ref}(1-\Phi)-u_2/\sqrt5,
\quad \delta L_{\rm end}/d_{\rm ref}=(-3/\sqrt5,0,-1/\sqrt5)^Ty.
\]

จึงมีทั้ง variance ของ u₂ และ covariance กับ Φ เมื่อเปลี่ยน readout
ไม่แทนด้วย `9 d_ref² Var(Φ)` โดยทั่วไป ไม่เปิด endpoint เป็น observable
หลักตัวที่สอง และไม่แปลเครื่องหมายพิกัดเป็น imaginary/ปฏิสสาร

<a id="classical-variance-bounds"></a>
## 4. ขอบเขต classical-parent variance โดยตรง

### 4.1 Inputs ที่สืบทอดและสถานะของขอบเขต

Q รับรองบนแต่ละ ball ว่า `0<mI≼∇²v≼MI` และ
`||∇³v||≤K₃` ระยะอะตอมยังเป็นบวก ดังนั้นสำหรับ root จริง

\[
v-v_*=\tfrac12 y^TAy+r(y),\quad
|r(y)|\le\Delta=K_3R^3/6,\quad
\|\nabla r(y)\|\le K_3\|y\|^2/2.
\]

ใช้ Δ_upper ของ Q ซึ่งปัดออกแล้ว ไม่สร้าง radius หรือควบคุม parent ใหม่
ตัวเลขตารางนี้เป็น **display approximations ของ bounds** ไม่ใช่ inputs ที่ตัดความแม่นยำ:

| R | m_lower ประมาณ | M_upper ประมาณ | K₃_upper ประมาณ | Δ_upper ประมาณ |
|---|---:|---:|---:|---:|
|1/32|4.63616|225.284|922.227|0.00469069|
|1/64|7.39094|191.832|803.557|0.000510887|
|1/128|8.79589|176.066|752.177|0.0000597777|
|1/256|9.50634|168.399|728.202|0.00000723404|
|1/512|9.86372|164.617|716.613|0.000000889864|
|1/1024|10.0430|162.738|710.915|0.000000110349|

สิ่งที่ต้องรับรองคือ relative error ของ **central variance**

\[
\frac{|\operatorname{Var}_{\rm loc}(X)-V_H|}{V_H}
\le E_{\rm cl}(\theta,R),
\quad \operatorname{Var}_{\rm loc}(X)
=\langle X^2\rangle_{\rm loc}-\langle X\rangle_{\rm loc}^2.
\]

แม้ `Φ_*` เป็น mechanical minimum ก็ไม่ได้ทำให้ local parent mean อยู่ที่ Φ_*
เช่น distribution ที่ X=1,3 โอกาสเท่ากัน มี raw moment5 แต่ variance1

### 4.2 วิธี A — Uniform remainder และ Gaussian tail

กำหนด `η=P_H(S_R^c)` และ `H_R=H|S_R` ซึ่ง symmetric จึง `E_HR X=0`
เพราะ `|r|≤Δ` normalized density ratio ของ parent ต่อ H_R อยู่ระหว่าง
`exp(−2Δ/θ)` กับ `exp(2Δ/θ)` ให้ `d=exp(2Δ/θ)−1` ได้

\[
|\langle X^2\rangle_{\rm loc}-\langle X^2\rangle_{H_R}|
\le d\langle X^2\rangle_{H_R},\qquad
|\langle X\rangle_{\rm loc}|^2\le d^2\langle X^2\rangle_{H_R}.
\]

Gaussian fourth moment เป็น `3 V_H²`; Cauchy–Schwarz ให้

\[
\frac{|\langle X^2\rangle_{H_R}-V_H|}{V_H}
\le\frac{\eta+\sqrt{3\eta}}{1-\eta},\quad
\frac{\langle X^2\rangle_{H_R}}{V_H}\le\frac1{1-\eta}.
\]

จึงเป็น variance-specific bound ไม่ใช่ free-energy error เปลี่ยนชื่อ:

\[
\boxed{E_A=\frac{d+d^2+\eta_0+\sqrt{3\eta_0}}{1-\eta_0}}
\quad(\eta\le\eta_0<1).
\]

ใช้ Gaussian tail จาก covariance และ m เดิม: `b=mR²/θ`,
`||y||²≤(θ/m)||Z₃||²` ใน Gaussian representation
Chernoff/MGF `E exp(t||Z₃||²)=(1−2t)^(−3/2)` ให้

\[
\eta_0=\begin{cases}
e^{-(b-3)/2}(b/3)^{3/2},&b>3,\\
1,&b\le3.
\end{cases}
\]

กรณี η₀=1 วิธีนี้ยังให้ finite relative certificate ไม่ได้
และเมื่อ Δ>0 คงที่ θ→0 ทำให้ d โตไม่จำกัด นี่เป็นความหยาบของ uniform bound
**ไม่ใช่ข้อพิสูจน์ว่า harmonic approximation แย่ลงจริงหรือ parent ผิด**
Producer หยุดประเมิน exp ที่ใหญ่มากเมื่อ `2Δ/θ≥1` เพราะ `E_A≥d≥1`
จึงรับรอง budget ใน(0,1)ด้วย bound นี้ไม่ได้อยู่แล้ว ไม่ใช่ physical threshold ใหม่

### 4.3 วิธี B — Moments และ surface terms บน ball เดิม

เขียน `w=exp[−(v−v_*)/θ]`, `Z=∫_S w`, outward unit normal n แล้วนิยาม

\[
b_0=Z^{-1}\oint_{\partial S}n w\,dS,\quad
S_b=Z^{-1}\oint_{\partial S}y n^T w\,dS.
\]

Integration by parts **เก็บ surface terms** ให้ identities

\[
A\langle y\rangle+\langle\nabla r\rangle=-\theta b_0,
\qquad
\langle yy^T\rangle A+\langle y(\nabla r)^T\rangle
=\theta I-\theta S_b.
\]

ไม่มีเหตุผลให้ surface term เป็นศูนย์เพียงเพราะ weight เป็น Gibbs
บน ball ที่จำกัด และ parent ไม่จำเป็นต้อง symmetric รอบ root

จาก curvature ที่ Q รับรอง `m||y||²/2≤v−v_*≤M||y||²/2`
เลือกรัศมีอินทิกรัลภายใน `ρ=min(R,√(θ/M))` ได้

\[
Z\ge Z_-:=\frac{4\pi}{3}\rho^3e^{-M\rho^2/(2\theta)},
\quad
G_n:=\frac{2\pi(2\theta/m)^{(n+3)/2}\Gamma((n+3)/2)}{Z_-},
\quad \langle\|y\|^n\rangle\le G_n\quad(n=2,3),
\]

\[
B_\partial:=\frac{4\pi R^2e^{-mR^2/(2\theta)}}{Z_-},
\qquad \|b_0\|\le B_\partial,\quad \|S_b\|\le R B_\partial.
\]

ρ ไม่ใช่ radius ของ parent/การค้น/physical reference ใหม่ แต่เป็น sub-ball
สำหรับ lower bound ของ normalization บน S_R เดิม ส่วน upper moments
ขยาย integral ไปทั้ง ℝ³ ภายใต้ lower curvature; ไม่สลับ m กับ M

ให้ `ν=||A⁻¹h||`, `ℓ=||h||` จาก identities ข้างต้น:

\[
|\langle X\rangle|\le B_\mu:=\nu(K_3G_2/2+\theta B_\partial),
\]

\[
|\langle X^2\rangle-\theta c_h|
\le B_2:=\nu\ell(K_3G_3/2+\theta R B_\partial).
\]

จึงได้ขอบเขตที่ต้องการ:

\[
\boxed{E_B(\theta,R)=\frac{B_2+B_\mu^2}{\theta c_h}.}
\]

ใช้ ν,ℓ upper enclosures และ c_h lower>0 เพื่อรับรองแบบ worst-case
`B_mu²` คือ upper error contribution หลังหัก mean จริง ไม่ใช่เอา bound ของ
mean ไปอ้างว่า parent มี mean shift ขนาดนั้นจริง หรือใช้แทน intrinsic entropy

ในการประเมิน rational ปลอดภัย producer ใช้ `√π<2` ทำให้

\[
G_2\le\frac94(2\theta/m)^{5/2}\frac{e^{M\rho^2/(2\theta)}}{\rho^3},
\quad G_3=3(2\theta/m)^3\frac{e^{M\rho^2/(2\theta)}}{\rho^3},
\quad B_\partial=3R^2\frac{e^{(M\rho^2-mR^2)/(2\theta)}}{\rho^3}.
\]

ทุก exponential/square root ที่ใช้ตัวเลขเป็น outward rational enclosure
อาศัย pure arithmetic helper ของ Q เท่านั้น ที่ exponent ≤−32 ใช้
`0<e^(−t)≤16!/t^16` แทนการ underflow เป็นศูนย์จาก positive exponential series
นี่เป็น bound เชิงคำนวณแบบอนุรักษ์ ไม่ใช่วิธีที่สามหรือกฎฟิสิกส์เพิ่ม

### 4.4 ทำไมวิธี B ปิดคำถามได้มากกว่า uniform bound

เมื่อ `θ≤MR²`, `ρ=√(θ/M)`, ให้

\[
C_2=\tfrac94(2/m)^{5/2}M^{3/2}e^{1/2},\quad
C_3=3(2/m)^3M^{3/2}e^{1/2},\quad
B_\partial\le3R^2(M/\theta)^{3/2}e^{1/2-mR^2/(2\theta)}.
\]

ได้ `G₂≤C₂θ`, `G₃≤C₃θ^(3/2)` และ

\[
E_B\le\frac{\nu\ell K_3 C_3}{2c_h}\sqrt\theta
+\frac{\nu\ell R}{c_h}B_\partial
+\frac{\nu^2\theta}{c_h}(K_3C_2/2+B_\partial)^2\longrightarrow0.
\]

Artifact เก็บ upper coefficients ของส่วน √θ และส่วน θ ที่ไม่มี boundary
**ห้ามละ boundary/cross terms จากสูตรเต็ม** การมี limit0 เป็นผลสำหรับ
classical restricted parent และ fixed certified R ไม่ใช่เลือก T ใหม่ของวัสดุ
หรือรับรอง physical small-quantum window สำหรับระบบใดก็ได้

### 4.5 Negative witness: quadratic บน ball ก็ยังต่างจาก full Gaussian

แม้ `K₃=0`, isotropic `A=I` และ mean=0 ให้ `b=R²/(2θ)`:

\[
\operatorname{Var}_{H_R}(y_i)
=\frac{2\theta}{3}\frac{\gamma(5/2,b)}{\gamma(3/2,b)}
=\theta\left[1-\frac{2b^{3/2}e^{-b}}{3\gamma(3/2,b)}\right]<\theta.
\]

ใช้ lower incomplete gamma recurrence; term ที่ขาดจาก θ เป็น surface/truncation
contribution จริง การตั้ง surface=0 จะอ้างผิดว่า variance ตรงกันทุก R
control แบบ exact นี้แยกการเลื่อน mean จาก finite-domain effect
ไม่ได้ทดสอบ parent ด้วย trajectory/Monte Carlo/parameter sweep

<a id="quantum-and-scales"></a>
## 5. Harmonic quantum correction และ frontier ของสเกล

### 5.1 Normal-mode weights สำหรับ Φ โดยเฉพาะ

ให้ `Ae_j=κ_j e_j`, `w_j=hᵀe_j`, ทั้งสามโหมดมี mass metric μI
และ frequency จริง `ω_j=√κ_j/t_*` ฐาน oscillator จาก
[Tong §3.4](https://www.damtp.cam.ac.uk/user/tong/statphys/statmechhtml/S3.html)
ให้ `Z_j=[2sinh(χω_j t_*/(2θ))]⁻¹` และ quantum virial relation
ใน quadratic Hamiltonian ให้

\[
V_{QH}=\sum_j w_j^2\frac{\chi}{2\sqrt{\kappa_j}}
\coth\!\left(\frac{\chi\sqrt{\kappa_j}}{2\theta}\right),
\quad V_H=\theta\sum_j\frac{w_j^2}{\kappa_j}.
\]

ไม่ต้องอ้างว่า eigenvectors ของ midpoint เป็น exact
spectral identity `Σw_j²=||h||²`, `Σw_j²/κ_j=c_h`
ทำให้ใช้ coefficient enclosures จาก stiffness certificate ได้โดยตรง

สำหรับ x>0, `0≤x coth x−1≤x²/3`:
lower bound ตามจาก derivative ของ `x cosh x−sinh x` เป็น `x sinh x≥0`
upper boundตามจาก `(1+x²/3)sinh x−x cosh x`
ซึ่งสัมประสิทธิ์ของ `x^(2n+1)` เป็น `4n(n−1)/[3(2n+1)!]≥0`
ดังนั้น

\[
\boxed{0\le\frac{V_{QH}-V_H}{V_H}
\le\frac{\chi^2\kappa_{\rm obs}}{12\theta^2},\qquad
\kappa_{\rm obs}=\frac{h^Th}{h^TA^{-1}h}.}
\]

Rayleigh bounds ให้ `κ_min≤κ_obs≤κ_max`; ใน reference นี้ κ_obs ประมาณ18.765
เทียบกับ certified upper κ_max ของ Q ประมาณ82.374 จึงไม่ต้องให้โหมดที่
observable อ่านออกน้อยมาคุมขอบเขตแบบเหมารวมทั้งหมด
κ_obs เป็น derived combination ของ state/readout เดิม ไม่ใช่ parameter ใหม่

ขอบเขตนี้ใช้กับ **isolated quadratic comparator** ไม่ครอบคลุม quantum
anharmonic parent, quantum local restriction/preparation, bath spectral tails
หรือ measurement uncertainty ไม่เอา error คู่แรกกับคู่ที่สองบวกแล้วเรียกว่า
full quantum-parent error แม้มี classical E_B→0 และ harmonic quantum bound

### 5.2 Admissible set แบบพารามิเตอร์ ไม่ใช่ physical PASS

สำหรับแต่ละหกรัศมี ให้ `E_cl=min(E_A ที่ใช้ได้,E_B)` เพราะทั้งสอง bound
คู่เปรียบเทียบเดียวกัน หาก A ใช้ไม่ได้ใช้ B เพียงตัวเดียว
ให้ `ε_cl,ε_q∈(0,1)` เป็น error budgets ที่ยังไม่เลือก:

\[
\mathcal A_R=\{(\theta,\chi):\theta,\chi>0,
E_{\rm cl}(\theta,R)\le\epsilon_{\rm cl},
\chi\le\theta\sqrt{12\epsilon_q/\kappa_{\rm obs}^{+}}\}.
\]

การมี E_B→0 บอกว่าเมื่อกำหนด budget>0 สามารถมี θ ที่เล็กพอใน classical model
และเลือกลำดับ family ของ χ ที่เล็กพอให้สอง comparator bounds ผ่านร่วมกันได้
**ไม่ได้บอกว่าทุก fixed χ มีช่วง θ เช่นนั้น** และไม่ได้ค้น global optimum
หรือทำ parameter sweep เพื่อเลือกจุดสนับสนุน UET

Dictionary เดิมและผลบนสเกลกายภาพคือ

\[
\theta=\frac{k_BT}{J_{\rm ref}},\quad
\chi=\frac{\hbar}{d_{\rm ref}\sqrt{\mu J_{\rm ref}}},\quad
\boxed{\mu d_{\rm ref}^2J_{\rm ref}
\ge\frac{\hbar^2\kappa_{\rm obs}^{+}}{12\epsilon_q\theta^2}},
\quad T=J_{\rm ref}\theta/k_B.
\]

เมื่อตรึง T จริง เขียนเงื่อนไขเดียวกันเป็น
`μ d_ref² ≥ ℏ² κ_obs^+ J_ref/[12 ε_q(k_BT)²]`
ยังต้องนำ E_cl( k_BT/J_ref,R ) มาตรวจแยกด้วย ไม่ใช้ quantum inequality
เพียงตัวเดียวตัดสินว่า parent harmonic approximation ใช้ได้

| ปริมาณ | หน่วย / ที่มา | สิ่งที่ไม่ตามมา |
|---|---|---|
| Φ,X,y | ไร้มิติ; coordinate/readout ของ O/Q | ไม่ใช่ entropy/information ทุกความหมาย |
| A,m,M,K₃,c_h,κ_obs | ไร้มิติ; derivatives/certificates/derived combinations | ไม่ได้เลือก constitutive constants ใหม่ |
| μ | kg; มวลอะตอมใน reference | ยังไม่รู้วัสดุจริง |
| d_ref | m; ระยะอ้างอิงเดิม | ไม่แทนด้วย gap equilibrium แล้วเปลี่ยน coupling เงียบ ๆ |
| J_ref | J; energy scale เดิม | ไม่อนุมานจาก dimensionless variance ตัวเดียว |
| `5 μ d_ref²` | kg·m²; generalized inertia ของ Φ | ไม่ใช่มวล kg หรือ mobility/damping |
| θ,χ | ไร้มิติ; scale definitions เดิม | χ ไม่ใช่ตัวปรับตาม T ของระบบเดิม |
| `μ d_ref² J_ref` | kg²·m⁴·s⁻² เท่าหน่วย ℏ² | จำกัดผลคูณ ไม่แยกสามพารามิเตอร์ได้ |
| ε_cl,ε_q | ไร้มิติ; future error policy | ไม่ใช่ thresholds ที่เลือกให้ผ่านแล้ว |

ตัวอย่าง non-identifiability: `μ→λμ,d_ref→d_ref/√λ` โดย J_ref,T คงเดิม
ทำให้ θ,χ เท่าเดิม; หรือ `J_ref,T→α(J_ref,T),μ→μ/α` โดยระยะคงเดิม
ก็ให้ θ,χ เท่าเดิม ดังนั้น variance อย่างเดียวไม่ระบุมวล/ระยะ/พลังงานแยกกัน
ยิ่งกว่านั้น classical static variance ไม่มี μ โดยตรงเมื่อ θ/shape คงเดิม

เมื่อทำให้ **ระบบหนึ่ง** เย็นลง χ ต้องคงเดิม; การลด χ คือเปลี่ยน family
ของ scales ไม่ใช่ลด T ไปด้วยเพื่อรักษาผลผ่าน Bound ไม่ผ่านหมายถึงวิธีนี้
ยังรับรองไม่ได้ ไม่ใช่หลักฐานหักล้าง parent

## 6. คำวินิจฉัย ข้อโต้แย้ง และ input ที่ยังขาด

| รอยต่อ | คำวินิจฉัย / หลักฐาน | สิ่งที่ไม่ปิด |
|---|---|---|
| Joint reference→Var(Φ) | exact Gaussian/Schur identity; mixed stiffness คงอยู่ | ไม่ได้เลือก quantum/parent/material state |
| Local classical parent→H variance | sufficient bounds A/B; B รวม mean/surface และมี limit0 ที่ fixed R | constants อาจหยาบ; ไม่รับรองทุก θ หรือทุก physical χ |
| Quantum H→classical H | observable-weighted coth bound, ใช้ rational coefficient enclosures | ไม่ใช่ quantum anharmonic parent |
| Dimensionless→scales | conditional frontier ของผลคูณ พร้อม units/identifiability | ไม่มี material scales/error policy/measurement จริง |
| Static restriction→preparation | specification ของ measure เท่านั้น | ไม่มี duration/escape/stationarity/วิธีเตรียมจริง |
| Result→UET | จำกัดความใช้ได้ของ reference เดิมด้วยฟิสิกส์มาตรฐาน | ไม่ได้สร้าง discriminator หรือพิสูจน์ learning/จักรวาลเปิด |

ข้อคัดค้านสำคัญที่ยังเปิด:

- Constants m,M,K₃ จาก Q เป็น sufficient enclosures ที่หยาบ ไม่ใช่ exact
  local spectral valuesทุกจุด: ไม่เปลี่ยนให้แคบลงโดยไม่มีหลักฐาน
- Gaussian มี support ทั้ง R³ ส่วน parent ใช้ ball: boundary error ยังอยู่
  แม้ K₃=0 ไม่ซ่อนด้วยการเรียกทั้งสองว่า equilibrium เหมือนกัน
- Local root certificate ไม่แก้ collision/dissociation ของ global parent
  และไม่แทนผล P ที่ reference center เดิมไม่ผ่าน localization
- Classical/local window ของวัสดุจริงต้องมี dictionary อิสระและ error policy
  การเลือก χ พร้อม θ เพื่อแสดง family ทางคณิตศาสตร์ไม่ใช่การทดสอบวัสดุ
- ไม่มีการประเมิน thermalization/preparation/lifetime และไม่มีเครื่องตรวจจริง
  effects เหล่านี้ยังไม่ทราบ ไม่ใช่มีค่าเป็นศูนย์

**Controller หลังรอบนี้:** `physical-parent-preparation` ยังเปิด แต่แคบลง
จาก “ต้องมี variance-specific error relation” เป็น “ต้องมี physical scales
และ observable-specific error/preparation policy ที่อ้างอิงอิสระได้”
ส่วน `quantum-parent-correspondence` เป็นช่องว่างแยกหากจะอ้างถึง quantum parent
ไม่บังคับให้ผู้เขียนตรวจคณิตศาสตร์เองหรือเลือกระหว่างสอง error methods

หนึ่งโจทย์ถัดไปที่เสนอ (ยังไม่เริ่ม): จัด physical dictionary และ error/preparation
policy สำหรับ Φ หนึ่งชุดที่มีหลักฐานอิสระ แล้วตรวจ admissible set ที่ได้โดยไม่ fit
scales จาก variance ที่จะใช้ตรวจเอง หากยังไม่มี input นี้ ให้หยุด physical admission
ที่ conditional frontier ไม่เปิด lifetime/material/experiment หลายเลนแทน

คำถามเฉพาะสำหรับผู้ตรวจ numerical verification/statistical mechanics:

1. Q bounds ครอบคลุม ball รอบ root จริงและ interval A ตามที่ใช้หรือไม่;
   numerical denominator/inverse enclosures และ root uncertainty ส่งต่อครบหรือไม่?
2. finite-ball IBP orientation, normalization lower bound, moment/surface
   upper bounds และ squared-mean contribution ให้ E_B ที่ถูกต้องหรือไม่?
3. oscillator state/readout และ coth weighting ใช้ isolate quantum harmonic
   comparator ถูกต้องหรือไม่; ข้อมูลใดต้องเพิ่มก่อนกล่าวถึง quantum parent?

การขอรีวิวนี้เป็นชุดคำถาม ไม่ได้ติดต่อผู้ตรวจหรืออ้างว่าได้รับ independent review

## 7. หลักฐานและการทำซ้ำ

- [Q report](UET_PARENT_STATIC_REFERENCE_AUDIT.md),
  [Q artifact](../topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_parent_static_reference_audit.json),
  [Q contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/parent_static_reference_audit.json)
  เป็น imported certified construction ไม่เรียก solver/producer เก่า
- [FORMAL contract ใหม่](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/phi_variance_static_admissibility.json),
  [producer ใหม่](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Phi_Variance_Static_Admissibility.py),
  [regression tests](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_phi_variance_static_admissibility.py),
  [artifact](../topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_phi_variance_static_admissibility.json)
  ผูก source/report/code/config/contract identities และเก็บ rational endpoints
- producer `--check` อ่านอย่างเดียว; `--emit-report` เขียนเฉพาะ artifact ใหม่นี้
  ไม่มี timestamp/randomness, roots, sweep หรือ trajectories ในทางคำนวณใหม่
- ศึกษา Tong §2.1 และ §3.4 จากเนื้อหาหลักออนไลน์เข้าถึง25ตุลาคม2026
  (หน้า HTML ระบุ generated18ตุลาคม2021); ใช้เป็นฐาน measure/oscillator
  ไม่ใช้ abstract หรือสูตรของระบบอื่นมาแทน stiffness จาก Q
- Review contract คง `INCOMPLETE`: construction/adversarial self-review
  ไม่ใช่ independent specialist review, completeness ไม่ใช่ physical validation

ผล checks ที่รันจริงและการคงหลักฐานเก่าบันทึกใน
[Topic UPDATE_LOG](../topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md) และ
[WORK_LEDGER ประจำวัน](../../WORK_LEDGER/2026/2026-10-25.md)
ไม่ให้รายงานหรือจำนวน tests เปลี่ยน physics gates/public main โดยอัตโนมัติ
