# รอบ P — ช่วงใช้งานและการลดรายละเอียดของโซ่–อ่างความร้อนสู่ Φ/Π

> ตรวจถึง 24 ตุลาคม 2026 — FORMAL result; ไม่ใช่การรับรองวัสดุจริงหรือ Core kinetics

## สรุปสำหรับผู้เขียน

รอบนี้ได้คำตอบสองชั้นที่ต้องเก็บร่วมกัน: **สมการ bath/memory ของ reference
ตรวจได้ แต่ reference นี้ยังรับรองโซ่อะตอมเดิมในช่วงเล็กที่ล็อกไม่ได้**
ทั้ง 16 แบบมีความแข็งเป็นบวก แต่ตำแหน่งเฉลี่ยอยู่นอกช่วงนั้น จึงไม่แก้ปัญหา
ด้วยการเพิ่ม bath ลดอุณหภูมิ หรือทำผลคำนวณให้ละเอียดขึ้นใน reference เดิม

ภายใน quadratic reference พลังงานของ Φ แลกกับอีกสองโหมดและ bath;
เมื่อตัดรายละเอียดออก อิทธิพลที่ย้อนกลับมาปรากฏเป็น memory และ noise
ที่ต้องสอดคล้องกับการเตรียมระบบ White bath ไม่ลบ internal memory และ
มวลจาก low-frequency response ไม่ใช่ bare kinetic storage โดยอัตโนมัติ
จึงได้ **สะพานแบบมีเงื่อนไข ไม่ได้ derive full C–Φ–Π หรือพบกลศาสตร์ใหม่**

งานเก่าไม่ถูกทิ้ง: canonical inertia/conditional thermodynamics ของ O
ยังใช้ตามขอบเขตเดิม ผลใหม่นี้บอกว่าควรหยุดใช้ reference นี้รับรอง physical
equilibrium-local window และต้องตรวจ admissible reference/preparation ก่อน
ขยายไปวัสดุจริง Core kinetics หรือการทดลอง

## 1. P0 — ฐานหลักฐานและ bounded research card

ฐาน local commit `e3bc64812a5ea7e6d40ba65da429dd65e89750ed` บนสาขาเดิม
`codex/research/lattice-mechanical-state`; งานรอบนี้บน
`codex/research/lattice-bath-reduction` ไม่มี upstream/publication มีงานค้างเดิม 463
รายการและ index ว่างก่อนเริ่ม แยก local working evidence ออกจาก public main
ซึ่งไม่ได้ fetch หรือตรวจ SHA สดในรอบนี้ ห้ามตีความ local checkpoint เป็น public release

| คำถาม/รายการ | ขอบเขตและตัวควบคุม |
| --- | --- |
| Proposition | bath และ hidden mechanical modes ให้ memory/แรงกลับสู่ Φ อย่างไร และลดเป็น constant damping/inertia ได้เมื่อไร |
| มีแล้ว | [O](UET_LATTICE_MECHANICAL_STATE_CONSTRUCTION.md): canonical map/inertia, conditional hidden F/U/S, global collision no-go และ local value bound; M/N และ thermal reference ใช้ในขอบเขตเดิม |
| Identity check | O 14/N 13/M 11/joint thermal 8 identities ตรงก่อนเริ่ม ไม่รัน producers เก่า |
| ขาด/โต้แย้ง | full internal localization, preparation, bath law, hidden reduction และ correspondence กับ Core; ดู O contract component `physical-regime-and-kinetic-closure` |
| การตรวจถัดไป | full joint quadratic/local certificate ก่อน; จากนั้น oscillator-bath/GLE และ exact hidden elimination ของ reference ที่ประกาศ |
| ผลที่รับได้ | conditional result, approximation, equivalence, contradiction หรือ prerequisite ที่ระบุตำแหน่งได้ |
| จุดหยุด | หยุด physical parent lane เมื่อไม่มี admissible certificate; independent formal quadratic lane ทำต่อได้ ไม่เพิ่มแรงหรือย้ายศูนย์เพื่อช่วยผล |
| Reviewer | statistical mechanics/lattice dynamics: ตรวจ preparation, localization, memory reduction และสิ่งที่จำเป็นก่อน physical use; ยังไม่ติดต่อ |
| Non-goals | ไม่มีวัสดุจริง การทดลอง spin rates fit/sweep/trajectory หรือ Core/API/defaults/thresholds/gate change |

### Provenance และ system partition

- ผู้เขียนเลือกตรวจโซ่ที่เคลื่อนไหวเอง รวม bath ทั้งสาม internal coordinates และยังไม่เลือกวัสดุ
- Imported physics: harmonic oscillator bath, conditional Gibbs, FDT และ linear response
- AI/reference choices: joint quadratic expansion, identical independent Drude bath channels และการตรวจ spectral band; ไม่ใช่ข้อเสนอพื้นฐาน UET ที่พิสูจน์แล้ว
- spins เป็น frozen labels; mechanical/bath states แลกพลังงานจริงภายใน reference
  ส่วน C, Φ, Π, endpoint readout และ auxiliary force เป็นพิกัด/การอ่าน/representation
  ที่ต้องแจกแจง ไม่ใช่สำเนาพลังงานหรือสถานะอิสระเพิ่มทุกชื่อ
- bath ไม่ใช่ detector; ไม่มี apparatus, signal transport, measurement uncertainty
  หรือ negligible physical backaction claim Mathematical infinitesimal force ใช้ตรวจ response
  เท่านั้น ไม่ใช่การออกแบบเครื่องมือทดลอง

<a id="joint-local-regime"></a>
## 2. P1 — Full internal reference และผลลบของ local window

ใช้ \(B=(-a/\sqrt5,E)\), \(\lambda=\sqrt5\epsilon_*d_{\rm ref}\):

\[
x=d_{\rm ref}a+Bq,\quad q=(Q,u_1,u_2),\quad Q=\lambda\Phi,
\quad B^TB=I,\quad B^T\mathbf1=0.
\tag{P1}
\]

จึง \(p_\Phi=\lambda p_Q\), kinetic energy \(p^Tp/(2\mu)\), phase-space
measure คงเดิม (position Jacobian ยกเลิก momentum inverse Jacobian) และ

\[
f_\Phi=\lambda f_Q,\quad D_\Phi=\lambda^2D_Q,\quad
M_{\Phi,\rm bare}=\mu\lambda^2.
\tag{P2}
\]

Φ เป็น compression projection ไม่ใช่ endpoint เพียงตัวเดียว:

\[
L_{\rm end}=3d_{\rm ref}(1-\epsilon_*\Phi)-u_2/\sqrt5.
\tag{P3}
\]

| วัตถุ | หน่วย/บทบาท | ที่มาและข้อจำกัด |
| --- | --- | --- |
| Q,u,p | m, kg·m/s; internal canonical state | coordinate transformation จากอะตอมเดิม ไม่บวกสถานะซ้ำ |
| Φ,Π | Φ ไร้มิติ, Π=dΦ/dt_norm | coordinate/velocity views ไม่ใช่ entropy หรือข้อมูลทุกความหมาย |
| f_s,A_s,g_s,K_s | force N และ stiffness N/m | derivatives ของ parent/control ที่เลือก ไม่ใช่ constants สากล |
| γ_b,ω_D | s⁻¹; bath rates | positive constitutive choices ไม่ได้ derive/fit จากวัสดุ |
| Γ,Γhat,r | kg/s², kg/s, N | bath memory/force representation; ไม่ใช่พลังงานก้อนใหม่ |
| D_s,m_dyn,ζ_eff | N/m, kg, kg/s | inverse response และ coefficients ของ expansion ไม่ใช่ bare Hamiltonian parameters เสมอ |
| Ω_ref | normalized constrained free energy | reference-specific; ไม่ใช่ exact mapping กับ full Ω ของ M/Core |
| sigma/R, detector record | ไม่ได้สร้างในรอบ P | friction loss ไม่ถูกเรียก total entropy production และไม่มี measurement claim |

### Joint expansion ไม่ใช่การแทน conditional dictionary เดิม

สร้าง \(V_{s,\rm lin}=V_{s0}+f_s^Tq+q^TA_sq/2\) จากอนุพันธ์ potential
เดียวกับ O ที่ q=0 โดยใช้ control เดิม: D/Jref=8, δ=ln2, ν=2,
dref/r0=1, ε*=1 ไม่ลบ linear force ไม่หา reference equilibrium ใหม่

O ขยายเฉพาะ u ที่ fixed Φ และเก็บ \(b_s(\Phi),K_s(\Phi)\) แต่รอบนี้ขยายทุก
coordinate ร่วมถึง order 2 ดังนั้น term \(Q u_i u_j\) และอนุพันธ์ K ต่อ Φ
ระดับถัดไปไม่ได้อยู่ใน joint quadratic reference ผลนี้ไม่ทำให้ entropic force
จาก stiffness determinant ใน O หายไปทางกายภาพ และไม่ derive full Ω ของ UET

### ข้อค้นพบที่ตัดสินได้จริง

ทั้ง 16 spin configurations มี A_s>0, f_s≠0 และ mixed Q/u stiffness ไม่เป็นศูนย์
แต่ mean และ covariance ของ formal joint Gibbs reference คือ

\[
q_s^*=-A_s^{-1}f_s,\qquad \Sigma_s=k_BT A_s^{-1},\qquad
\|q_s^*\|^2>(d_{\rm ref}/4)^2\quad\text{ทุก s}.
\tag{P4}
\]

นี่เป็น **exact inequality certificate ไม่ใช่ผลจากการเลือก tolerance**:
producer ตรวจ Sylvester minors และ numerator/denominator ของ rational
inequality ด้วย Bernstein polynomial coefficients บน ln2∈(69/100,7/10)
ขอบนี้ได้จาก positive series
ln2=2Σ[n≥0]1/((2n+1)3^(2n+1)): lower 842/1215 และ remainder <1/6804
อยู่ระหว่าง rational endpoints ดังกล่าว รายการผลทุก configuration อยู่ใน artifact

ให้ R=dref/4 และ e=q*/||q*|| สำหรับ T>0:

\[
\Pr(\|q\|\le R)\le
\Pr(e^Tq\le R)=\mathcal N_{\rm CDF}
\!\left(\frac{R-\|q^*\|}{\sqrt{k_BT e^TA^{-1}e}}\right)<\frac12.
\tag{P5}
\]

จึง **ไม่มี equilibrium-localization window ที่ให้ probability ≥1−ε_local
เมื่อ ε_local<1/2** สำหรับ reference/center/ball ที่ล็อกนี้ ไม่ใช่แค่ Markov
tail bound หยาบไม่ผ่าน การลด T ทำให้ spread แคบลงรอบ mean ที่อยู่นอก ball
และการเปลี่ยน damping/cutoff ไม่ย้าย classical stationary mean นี้

คำวินิจฉัยจำกัดเฉพาะ reference นี้ ไม่แปลว่าโซ่อะตอมไม่มี metastable preparation
ไม่หักล้างวัสดุจริง ไม่ตัดสินทุกศูนย์ขยาย และไม่ตัดสิน UET ทั้งทฤษฎี
**หยุด physical-parent acceptance lane ตรงนี้**; ส่วนต่อไปเป็น independent
formal quadratic/bath result ไม่ใช่การช่วย parent ให้ผ่านด้วยการเปลี่ยนสมการ

### Error domain และ classical limit ที่ยังแยกตรวจ

เมื่อ ||q||≤R ระยะคู่มี lower bound
r_ij≥(j−i)dref−√2R>0 กำหนด M3 เป็นผลรวม supremum ของ absolute third
pair derivative คูณ ||B_j−B_i||³ จะได้ |V−V_lin|≤M3R³/6 บน ball
เท่านั้น ความคลาดเคลื่อน potential กับ probability นอก ball เป็นคนละส่วน
ไม่มี bound ของ force, lifetime หรือ probability การออกจาก domain ตามเวลา

ใช้ θ=kBT/Jref, χ=ℏ/(Jref t*) และ frequencies จาก A/μ ไม่ใช้ hidden
frequencies ที่ fixed Φ แทน full internal spectrum สำหรับ undamped harmonic
mode x=ℏω/(2kBT) มี relative variance correction
0≤x coth x−1≤x²/3: lower ตาม derivative ของ x cosh x−sinh x; upper ตาม
coefficients 4n(n−1)/(3(2n+1)!) ของ (1+x²/3)sinh x−x cosh x ซึ่งไม่ติดลบ
นี่ไม่พอรับรอง bath ที่มี spectral tail ต่อไปถึง infinity

สำหรับ **linear Drude reference เท่านั้น** ให้ G(ω)=[A−μω²I−iωΓhat(−iω)]⁻¹
และเลือก analysis splitting frequency Bω ที่
Bω²≥2(tr A/μ+γ_bω_D) จะได้ ||G||≤2/(μω²) เมื่อ ω≥Bω
จาก FDT และ 0≤x coth x−1≤min(x²/3,x) จึงมี sufficient covariance bounds

\[
\Delta\langle Q^2\rangle\le r_B k_BT(A^{-1})_{00}
+\frac{\hbar\gamma_b\omega_D^2}{\pi\mu B_\omega^4},\quad
\Delta\langle\dot Q^2\rangle\le r_B\frac{k_BT}{\mu}
+\frac{2\hbar\gamma_b\omega_D^2}{\pi\mu B_\omega^2},\quad
r_B=\frac{\hbar^2B_\omega^2}{12(k_BT)^2}.
\tag{P6}
\]

ใช้ two-sided PSD convention ∫dω/(2π); Δ คือ quantum minus classical
symmetrized variance สำหรับ linear equilibrium bath ไม่ใช่ quantum entropy
ของ parent ไม่อ้าง quantum white-noise limit หรือรับรองทุก T จาก formula นี้
Drude cutoff ไม่ใช่ hard cutoff; tail ใน P6 ไม่ถูกตั้งเป็นศูนย์
เลือก budgets ε_q, ε_v แล้วตรวจ RHS/variance≤budget ได้ในอนาคต แต่ไม่มี
material constants หรือ budgets เชิงทดลองในรอบนี้ และ P5 ปิด local-parent
route ที่ล็อกไว้แล้ว ไม่ทำ scan หา T เพื่อหลบผลนั้น

<a id="bath-gle-dictionary"></a>
## 3. P2 — Bath Hamiltonian, preparation และ GLE

ใช้ independent channels a=1,2,3 ที่มี spectrum เดียวกัน เชื่อมกับ q ไม่ใช่ CM:

\[
H_{\rm tot}=\frac{p^Tp}{2\mu}+V(q)+
\sum_{a,j}\left[\frac{(p^b_{aj})^2}{2m_j}
+\frac{m_j\omega_j^2}{2}\left(z_{aj}-\frac{c_jq_a}{m_j\omega_j^2}\right)^2\right].
\tag{P7}
\]

Finite bath มี positive m_j,ω_j และ fixed coefficients ใช้ classical canonical
measure เดียวกันใน numerator กับ bare bath partition Z_b^0 เมื่อ shift
y_aj=z_aj−c_jq_a/(m_jω_j²) ที่ fixed q, Jacobian=1 จึง
Z_b(q)/Z_b^0=1 mechanical marginal ไม่เปลี่ยน V(q) และ mean P4 ไม่ย้าย
เมื่อขยาย square ต้องเก็บ counterterm q_a²Σ c_j²/(2m_jω_j²) หากละจะได้
V_eff=V−q_a²Σ c_j²/(2m_jω_j²) ซึ่งเป็นคนละแบบจำลอง
ไม่ได้ใช้ counterterm นี้อุด collision no-go ของ O: bath ที่หาร reference แล้ว
ยังให้ reduced parent integral เดิมที่ diverge

Hamilton equations ให้ bath oscillator driven by c_jq_a(t) แก้แล้ว integrate
by parts ใน convolution จะได้ **ก่อนออกจาก parent ordered/local domain**

\[
\mu\ddot q+\nabla V(q)+\int_0^t\Gamma(t-s)\dot q(s)\,ds=\xi(t)+F(t),\quad
\Gamma_{ab}(t)=\delta_{ab}\sum_j\frac{c_j^2}{m_j\omega_j^2}\cos\omega_jt,
\tag{P8}
\]

\[
\xi_a(t)=\sum_j c_j\left[
\left(z_{aj}(0)-\frac{c_jq_a(0)}{m_j\omega_j^2}\right)\cos\omega_jt
+\frac{p^b_{aj}(0)}{m_j\omega_j}\sin\omega_jt\right].
\tag{P9}
\]

Default preparation เป็น conditional Gibbs ของ shifted bath ที่ q(0)
จึง ξ mean zero Gaussian และ
E[ξ_a(t)ξ_b(s)]=kBT Γ_ab(t−s) หากใช้ bare/unshifted Gibbs แทน
จะมี deterministic initial slip −Γ(t)q(0) ห้ามตัดหรือเอาไปเรียก memory
ที่ระบบเรียนรู้เพิ่ม ไม่มีการสมมติ spin equilibration ในขั้นนี้

P8 เป็น exact finite-bath elimination (โดยมี local existence ของ trajectory)
ไม่ต้องสมมติ V quadratic แต่ global stationary statements ต่อไปใช้เฉพาะ
confining joint quadratic V_lin ส่วน finite Hamiltonian รักษา H_tot เมื่อ F=0
และ spins frozen ไม่ได้ทำให้ reduced mechanical energy คงที่เอง

### Drude continuum และ units

ประกาศ convention
J_b(ω)=(π/2)Σ c_j²/(m_jω_j)δ(ω−ω_j) สำหรับหนึ่ง channel และเลือก

\[
J_b(\omega)=\mu\gamma_b\omega\frac{\omega_D^2}{\omega^2+\omega_D^2},\quad
\Gamma(t)=\frac2\pi\int_0^\infty\frac{J_b(\omega)}{\omega}\cos\omega t\,d\omega
=\mu\gamma_b\omega_De^{-\omega_D|t|}I,
\quad \widehat\Gamma(z)=\frac{\mu\gamma_b\omega_D}{z+\omega_D}I.
\tag{P10}
\]

Finite bath ไม่เกิด irreversible decay แบบ continuum นี้โดยอัตโนมัติ
การแทน spectral sum ด้วย continuous measure เป็น assumption ที่ประกาศ
μ [kg], q [m], γ_b,ω_D [s⁻¹], Γ [kg s⁻²], Γhat [kg s⁻¹], ξ,F [N]
J_b [kg s⁻²] และ covariance kBTΓ [N²] ส่วน coordinate Φ ไร้มิติต้องใช้
λ²Γ, λξ, λF และ inertia μλ² ไม่ย้าย kg เป็น kg m² ด้วยชื่อ Π

### Equivalent auxiliary representation ของ quadratic reference

\[
dq=p\,dt/\mu,\qquad dp=(-A(q-q^*)+r+F)\,dt,
\quad dr=(-\omega_Dr-\gamma_b\omega_Dp)\,dt
+\sqrt{2\mu\gamma_b\omega_D^2k_BT}\,dW.
\tag{P11}
\]

กำหนด r(0)∼N(0,μγ_bω_DkBT I) กับ conditional preparation ที่กล่าวมา
เมื่อลด r จะได้ P8/P10 พร้อม noise Gaussian law เดียวกัน ไม่ใช่แค่ response
ตรงกัน ตัว r แทน projected bath force; ไม่รวมเป็น substance ใหม่และไม่เอา
energy ของ finite bath มาบวกกับ auxiliary bookkeeping ซ้ำ

สำหรับ centered state (q−q*,p,r) covariance ของ invariant Gaussian คือ

\[
\Sigma=\operatorname{diag}(k_BT A^{-1},\mu k_BT I,
\mu\gamma_b\omega_D k_BT I).
\tag{P12}
\]

ตรวจ F_OUΣ+ΣF_OU^T+GG^T=0 และ reversible parity: q,r even, p และ Π odd
หมุน A ไป eigenbasis (bath isotropic จึงไม่เปลี่ยน law) แต่ละ eigenvalue κ>0
ให้ pole polynomial z³+ω_Dz²+(κ/μ+γ_bω_D)z+ω_Dκ/μ; Routh–Hurwitz
margin γ_bω_D²>0 จึง stable สำหรับ reference นี้ ไม่อ้าง theorem นี้กับ parent
ที่ไม่ confining หรือ spin sectors ที่ไม่ได้เปลี่ยนสถานะ

### White limit และบัญชีพลังงาน

ตรึง γ_b แล้ว ω_D→∞: causal Γhat→μγ_b ขณะที่ two-sided covariance
kBT μγ_bω_D exp(−ω_D|t|)→2μγ_bkBTδ(t) จึง white force amplitude
√(2μγ_bkBT) และ friction μγ_b ไม่หายไปครึ่งหนึ่งที่ causal endpoint
เป็น classical fixed-band/kernel/noise limit; ไม่อ้าง uniform quantum หรือ
ทุก initial preparation ใช้ได้โดยละ boundary layer

ใน colored representation dH_mech/dt=v^T(r+F) ส่วน extended function
H_mech+r²/(2μγ_bω_D) มี deterministic loss r²/(μγ_b) และ Itô injection
3ω_DkBT ที่ equilibrium สองส่วนเท่ากันเฉลี่ย; white limit มี loss
μγ_b E|v|²=3γ_bkBT เท่ากับ noise injection
friction loss บวกไม่ได้หมายถึง equilibrium มี total entropy production บวก
และไม่ย้าย deterministic sigma/R เดิมมาเป็น entropy โดยเปลี่ยนชื่อ
นี่คือบัญชีของ declared reference ไม่ใช่คำตอบ unique physical heat ภายใต้
strong coupling ของวัสดุจริง; ใช้บทเรียน Argument §30 โดยไม่รันซ้ำ

<a id="hidden-reduction-and-core"></a>
## 4. P3 — Internal memory, exact reduction และขอบเขต Core correspondence

P13–P19 ใช้ centered fluctuations q−q* ภายใน **formal quadratic reference**
เพื่อเขียน response ให้กระชับ การเปลี่ยนพิกัดนี้ไม่ได้ขยาย parent ใหม่รอบ q*
ไม่ได้ลบ f_s หรือย้าย physical reference เพื่อแก้ P5; ข้อห้าม local regime ยังอยู่

เขียน A_s เป็น block (a,g^T;g,K) และ h(z)=μz²+zΓhat(z) ที่ Re z>0
สำหรับ centered initial response:

\[
D_s(z)=a+h(z)-g^T[K+h(z)I]^{-1}g,\qquad
\widetilde Q=D_s^{-1}\widetilde F_Q\quad\text{สำหรับ zero-mean prepared response}.
\tag{P13}
\]

ตัวตรวจใช้ full block equation และ determinant identity
det(A+hI)=det(K+hI)D ไม่ลบ hidden poles เพียงเพราะเห็น scalar denominator
นี่คือ exact linear response ของ joint quadratic reference ไม่ใช่สมการหลัก
สากล UET และไม่ใช่ equivalence ของ stochastic process หากยังไม่ตรวจ noise

### Initial forcing และ effective FDT

ให้ ℓ(z)=μz+Γhat(z), η_Q=ℓQ_0+μv_Q0+ξ_Q และ
η_u=ℓu_0+μv_u0+ξ_u จะได้

\[
D_s\widetilde Q=\widetilde F_Q+\eta_Q-g^T(K+hI)^{-1}\eta_u.
\tag{P14}
\]

หาก hidden coordinates เตรียมแบบ conditional equilibrium ที่ Q_0:
u_0=−K⁻¹gQ_0+δu_0, covariance δu_0=kBT K⁻¹ และ p_u covariance μkBT I
จึงมี exact reduced GLE ที่ bare mass μ, static stiffness k0 และ kernel

\[
k_0=a-g^TK^{-1}g>0,\qquad
\widehat\Gamma_{\rm eff}(z)=\widehat\Gamma(z)
+[\mu z+\widehat\Gamma(z)]g^T(K+hI)^{-1}K^{-1}g,\quad
D_s=\mu z^2+z\widehat\Gamma_{\rm eff}+k_0.
\tag{P15}
\]

เพื่อพิสูจน์ preparation ไม่ใช่ตรวจ spectrum อย่างเดียว ใช้ hidden OU state
y=(u+K⁻¹gQ,p_u,r_Q,r_u) ซึ่ง obey dy=F_hy dt+B_h v_Q dt+G_h dW
และ force=c_h y โดย B_h=(K⁻¹g,0,−μγ_bω_D,0), c_h=(−g^T,0,1,0)
conditional covariance Σ_h=diag(kBT K⁻¹,μkBT I,μγ_bω_DkBT,
μγ_bω_DkBT I) ให้ exact identities

\[
F_h\Sigma_h+\Sigma_hF_h^T+G_hG_h^T=0,\quad
\Sigma_hc_h^T=-k_BT B_h,\quad
\Gamma_{\rm eff}(t)=-c_he^{F_ht}B_h.
\tag{P16}
\]

ดังนั้น free hidden force มี covariance kBT Γ_eff(|t−s|) และ mean zero
จาก Gaussian initial law ที่ระบุ หาก mean หรือ covariance ของ hidden state
ต่างไป ต้องเก็บ prepared forcing c_h exp(F_ht)E[y_0] และ transient covariance
ไม่ใช่เรียก forcing ส่วนนี้ว่า equilibrium noise หรือ learning

ใน Fourier convention q(t)∝exp(−iωt), R=(K−μω²I−iωΓhat(−iω)I)⁻¹:

\[
S_{\xi,\rm eff}(\omega)=2k_BT\Re\widehat\Gamma(-i\omega)
[1+g^TRR^\dagger g]
=2k_BT\Re\widehat\Gamma_{\rm eff}(-i\omega).
\tag{P17}
\]

ได้ทั้ง noise positivity, response และ initial-law consistency ใน linear
Gaussian reference อนุพันธ์ memory นี้มีสองต้นทาง: bath และ internal modes
Markovian state (q,p,r) ไม่ได้ทำให้ (Φ,Π) เพียงสองตัว Markovian

### Low-frequency reduction ไม่ได้คืน bare inertia เสมอ

นิยาม r1=g^TK⁻²g, r2=g^TK⁻³g:

\[
D_s(z)=k_0+\zeta_{\rm eff}z+m_{\rm dyn}z^2+O(z^3),\quad
\zeta_{\rm eff}=\mu\gamma_b(1+r_1),\quad
m_{\rm dyn}=\mu(1-\gamma_b/\omega_D)(1+r_1)
-(\mu\gamma_b)^2r_2.
\tag{P18}
\]

m_dyn เป็น coefficient ของ low-frequency inverse response ไม่ใช่มวลอะตอม
หรือ bare kinetic storage จึงไม่ต้องเท่ากับ μ และอาจติดลบแม้ full reference
stable ตัวอย่างพีชคณิตมาตรฐาน a=2,K=diag(1,1),g=(1,0),μ=1,γ_b=2
ใน white-bath limit ให้ k0=1,ζ_eff=4,m_dyn=−2 แต่ A ยัง SPD และ full
damped dynamics stable ตัวอย่างนี้ **ไม่ใช่การปรับ control ของโซ่ O**
และไม่ใช่ negative physical mass: มันปฏิเสธการใช้ truncated second-order
polynomial เป็น stable positive-inertia Core model โดยไม่มีเงื่อนไขเพิ่ม

### Finite-band error certificate ก่อนอนุญาตใช้รูปง่าย

สำหรับ complex disk |z|≤B<ω_D และ κ≤λ_min(K), กำหนด
H=μB²+μγ_bω_DB/(ω_D−B)<κ,
R_h=μγ_bB³/[ω_D(ω_D−B)] และ G²=||g||² จะได้

\[
|D_s-D_2|\le\Delta_D=(1+r_1)R_h
+r_2[\mu|1-\gamma_b/\omega_D|B^2+R_h](H+\mu\gamma_bB)
+\frac{G^2H^3}{\kappa^3(\kappa-H)}.
\tag{P19}
\]

จาก exact identities h−μγ_bz−μ(1−γ_b/ω_D)z²
=μγ_bz³/[ω_D(ω_D+z)] และ hidden resolvent remainder
h³g^TK⁻³(K+hI)⁻¹g ไม่ได้นำ errors กลุ่มเดียวกันมาบวกซ้ำ
เมื่อ |D2|≥d_min>Δ_D บน band จึง
|D_s⁻¹−D2⁻¹|≤Δ_D/[d_min(d_min−Δ_D)] ใน response units
ไม่มีการหาร relative error ที่ resonance โดยไม่มี lower bound
ไม่มี bandwidth/threshold ที่ fit เพื่อให้ผ่าน: P19 เป็นเงื่อนไขเพียงพอให้ผู้ใช้
ประกาศ target band/error ก่อนประยุกต์จริง; ไม่ครอบ stochastic covariance
ของ approximate model โดยอัตโนมัติ ต้องตรวจ FDT/noise policy ของ surrogate ด้วย
หากเลือก surrogate white-force PSD \(S_{\xi,2}=2k_BT\zeta_{\rm eff}\) ตาม FDT
จะได้ pointwise noise bound
\[
|S_{\xi,\rm eff}(\omega)-S_{\xi,2}|
\le 2k_BT\,\Delta_D(|\omega|)/|\omega|,\qquad 0<|\omega|\le B.
\tag{P19a}
\]

เพราะ Re Γeff=−Im D(−iω)/ω และ Δ_D(b)=O(b³), RHS จึงต่อเนื่องเป็นศูนย์ที่
ω=0 ไม่เกิด singularity เทียม ใช้ร่วมกับ compliance bound ข้างบนและ
|χ|≤1/(d_min−Δ_D), |χ2|≤1/d_min เพื่อ bound output PSD ได้บน band
แต่ไม่มีการควบคุม frequencies นอก band จึงยังไม่รับรอง full-time covariance,
escape/lifetime หรือ physical Markov law จาก low-band agreement เพียงอย่างเดียว

### White-bath กับ fast-internal limit: ผลที่ตรวจ ไม่ใช่สมมติว่าไม่ commute

white limit เพียงอย่างเดียวทำให้ h=μz²+μγ_bz แต่ยังเหลือ (K+hI)⁻¹
จึงไม่ลบ internal memory ส่วน explicit fast scaling K→K/ε²,g→g/ε
โดยตรึง static coupling g^TK⁻¹g ให้
D_ε=a+h−g^T(K+ε²hI)⁻¹g→k0+h
สำหรับ bounded z ที่แยกจาก poles ใน reference นี้ limits ε→0 และ
ω_D→∞ **commute** ไม่กล่าวอ้าง noncommutation โดยไม่มีหลักฐาน
แต่แทน hidden dynamics ด้วย static force ตั้งแต่แรกในระบบที่ไม่มี scaling
เช่นนี้ จะพลาด r1/r2 และ friction/mass corrections ใน P18
นี่เป็นการพิสูจน์เงื่อนไขของ limit ไม่ได้ scale/retune locked atomic control

### Normalization กลับสู่ Φ/Π และขอบเขต C

เมื่อ admissible reduction มี m_dyn>0,ζ_eff>0 และผ่าน band/noise criteria:

\[
m_n=\frac{\lambda^2m_{\rm dyn}}{NE_*t_*^2},\quad
\zeta_n=\frac{\lambda^2\zeta_{\rm eff}}{NE_*t_*},\quad
M_\Phi^{\rm mobility}=1/\zeta_n,\quad \tau=m_n/\zeta_n,
\quad \tau\dot\Pi+\Pi=-M_\Phi^{\rm mobility}\partial_\Phi\Omega_{\rm ref}
+\text{matched source/noise}.
\tag{P20}
\]

ใช้ Ω_ref=F_ref/(NE*) ที่ประกาศเท่านั้น ไม่ใช่ identity กับ full Ω ของ M/Core
τ/M=m_n ไม่เลือก τ,M จาก first principles เพราะ γ_b,ω_D และ reduction
assumptions ยังเป็น constitutive inputs ไม่มีการอัปเดต Core defaults

mechanical bath ไม่ทำให้ spins เปลี่ยน: w_s เป็น preparation ที่คงที่
χ_frozen=Σ_s w_s χ_s ไม่เท่ากับ inverse ของ averaged impedance โดยทั่วไป
และไม่ใช่ annealed force จาก −kBT lnΣ_s Z_s(q) โดยอัตโนมัติ
แม้เตรียม weights ให้ตรง canonical ณ T_0 ก็ยังไม่มีหลักฐานให้มัน re-equilibrate
เมื่อ T หรือ drive เปลี่ยน จึงไม่ derive C drift หรือ full C–Φ–Π closure
global spin flip ยังคงสมมาตร; signed/magnitude ทางเลือกเดิมไม่ถูกเลือกแทน
และไม่มีการโยงเครื่องหมายไป antimatter/imaginary การตรวจ parity ของ q,p,r
ไม่ได้ยืนยัน parity หรือ physical meaning ของ C ใน Core เพราะสปินในรอบนี้
ยังเป็น frozen labels และไม่มี C transition law

## 5. P4 — คำวินิจฉัย ข้อคัดค้าน และงานถัดไป

| สะพาน | ผลที่ตัดสินได้ | สิ่งที่ไม่ตามมา |
| --- | --- | --- |
| Atomic internal coordinates → Q/Φ/u | EXACT coordinate/force-port/inertia map ตาม geometry O | endpoint เดียวอ่าน Φ ครบหรือได้ CM damping |
| Parent → joint quadratic reference | local Taylor formula มีได้ แต่ equilibrium localization ของ control นี้ NOT ADMITTED ตาม P5 | ปฏิเสธทุก preparation/ทุกวัสดุ หรือรับรอง parent ทั่ว domain |
| Harmonic bath → GLE | EXACT finite elimination; Drude continuum เป็น declared choice | bath spectrum/γ_b/ω_D ถูก derive จาก UET หรือวัสดุ |
| Drude GLE → auxiliary representation | EQUIVALENT Gaussian law เมื่อ initial preparation ตรง | Φ/Π สองตัวเป็น Markovian หรือ r เป็น substance ใหม่ |
| Full internal modes → scalar response/noise | EXACT memory/FDT ตาม P13–P17 | memory หายเพียงเพราะ bath white |
| Scalar memory → simple Core form | CONDITIONAL band/positive-mass/noise reduction เท่านั้น; counterexample จำกัด blanket identification | bare inertia=dynamic mass เสมอ หรือ closure ของ C |
| Comparator novelty | STANDARD_COMPARATOR_EQUIVALENCE ใน reference ที่เลือก | prediction ใหม่หรือการยืนยันหลักคิด UET ทั้งหมด |

**หนึ่งโจทย์ถัดไปที่เสนอ:** ตรวจการมีอยู่ของ stationary/metastable mechanical
reference และ local preparation ที่ admissible ของ parent เดิม พร้อม basin/
classical-domain evidence ก่อนผูก Core kinetics กับระบบจริง ไม่เริ่มค้น stationary
point ย้ายศูนย์ เติม repulsion/cutoff เลือกวัสดุ หรือรัน dynamics ในรอบ P

คำถามผู้เชี่ยวชาญที่เตรียม: (1) ตรวจ no-local-equilibrium certificate P4–P5
และขอบเขตที่ไม่ตัด metastable/transient preparation; (2) ตรวจ bath initial
preparation/conditional hidden FDT P9/P16; (3) ตรวจการแยก dynamic mass
และ bare inertia รวม sufficient band certificate P18–P20; (4) input ใด
จำเป็นก่อน admissible physical parent reduction ยังไม่มีการติดต่อภายนอก

### แหล่งหลักและขอบเขตที่อ่าน

| แหล่ง/รุ่น | ตำแหน่งที่ใช้ | รับมา/ไม่รับมา |
| --- | --- | --- |
| [Hänggi–Ingold, quant-ph/0412052v1, 7 Dec 2004](https://arxiv.org/html/quant-ph/0412052) | II Eq5; III.1 Eq9/III.2 Eqs12–14; IV.1 Eqs20–29 | FDT, response, oscillator bath และ preparation; ใช้ classical reduction ที่ derive เอง ไม่ย้าย quantum initial-correlation subtleties เป็น classical theorem |
| [Ottobre–Pavliotis, 1003.4203v1, 22 Mar 2010](https://arxiv.org/html/1003.4203) | Eqs5–10, Assumption2.1, Theorem2.6/Eqs17–22 และ §6 | Markov embedding/white-limit framework; theorem2.6 มี periodic-potential/initial-moment conditions ไม่ใช่การรับรอง parent O |
| [O report](UET_LATTICE_MECHANICAL_STATE_CONSTRUCTION.md) และ [N report](UET_SPIN_STRAIN_CORRESPONDENCE_AUDIT.md) | O1–O4/N microscopic-topology verdict | source-linked parent, geometry, units และ negative evidence; ไม่รัน science เก่าซ้ำ |
| [Argument](UET_THEORY_ARGUMENT.md) | §30 conditional bath/energy/parity lessons | deterministic loss≠total EP; ยังไม่เป็น microscopic bath law |

Derivations P1–P20 และ exact certificates เป็นงานตรวจภายใน ไม่ใช่ independent
specialist review หรือ external replication ข้อจำกัด openness/learning/persistence
และจักรวาลของผู้เขียนยังอยู่ในภาพรวม ไม่ถูกยืนยันหรือปฏิเสธด้วย reference นี้

## 6. ชุดตรวจ การทำซ้ำ และข้อจำกัดการเผยแพร่

ชุดใหม่ประกอบด้วย [FORMAL contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/lattice_bath_reduction_audit.json),
[producer](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Lattice_Bath_Reduction_Audit.py),
[regression tests](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_lattice_bath_reduction_audit.py)
และ [artifact](../topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_lattice_bath_reduction_audit.json)
ใช้ identity helper เดิม ไม่มี schema/status system ใหม่

คำสั่งจาก repo root (ใช้ Python environment ที่มี SymPy 1.14.0):

```text
python docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Lattice_Bath_Reduction_Audit.py --check
python -m unittest discover -s docs/topics/0.13_Thermodynamic_Bridge/Code/03_Research -p test_t13_lattice_bath_reduction_audit.py -v
python docs/scripts/audit/audit_calculation_completeness.py --check
```

`--check` อ่านอย่างเดียวและปฏิเสธ artifact ที่ไม่ตรง input/contract ปัจจุบัน;
`--emit-report` เขียนเฉพาะ artifact ใหม่อย่างชัดเจน ไม่รัน producer M/N/O/R
producer นำ definitions ของ O มาใช้เป็น dependency โดยไม่เรียก calculate/main
ของ O ผลใหม่ผูก identities 20 รายการและ canonical contract hash

ผลตรวจภายใน: 12 symbolic groups, 16 locked spin configurations,
14 negative controls และ regression 37/37 ผ่าน Completeness แบบอ่านอย่างเดียว
และ explicit seven-path precommit check ผ่าน (21 contracts/126 routes/0 errors)
ตัวเลขเหล่านี้บอกขอบเขตการตรวจ ไม่ใช่คะแนนความถูกต้องของทฤษฎี;
analytic inequality/limit proofs ในเนื้อหาไม่ได้กลายเป็น machine theorem proof
จากการที่ residuals ผ่าน

ระหว่าง QA พบและแก้ cache ที่ยอมให้ float/bool tuple เท่ากับ integer tuple
ข้าม validation โดยย้าย domain validation ออกนอก cache พบ metadata unit
string ไม่ตรงกันและแก้ให้ใช้ unit declaration เดียวกัน Initial pre-package
test ยังไม่มี contract/artifact จึงไม่ผ่าน; หลังสร้าง package และแก้เหตุจริง
จึงรัน regression ใหม่ผ่าน ไม่ลด threshold หรือแก้ physics เพื่อให้ผ่าน

review คง INCOMPLETE: `physical-parent-preparation` และ
`Core-surrogate-admission` ยัง UNKNOWN การแก้เอกสาร/metadata และ self-review
ไม่ใช่ independent statistical-mechanics/lattice-dynamics approval
เก็บ old identities/hashes และงานค้างเดิม ไม่ regenerate หลักฐานวิทยาศาสตร์เก่า

เอกสาร/โค้ด/ผลนี้เตรียมเป็น public-safe local work แต่ยังไม่ push/merge/เผยแพร่
source commit เป็น local evidence ไม่เท่ากับ public main ไม่มี raw private
conversation, credentials หรือเอกสารต้นฉบับเฉพาะเครื่องรวมในชุดส่งมอบ
