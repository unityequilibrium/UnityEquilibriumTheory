# รอบ O — สถานะ พลังงาน และ entropy ของโซ่ที่ยืดหดเอง

วันตัดยอด: 24 ตุลาคม 2026 • research-core • FORMAL / classical local reference

## สรุปสำหรับผู้เขียน

**การยืด–หดหนึ่งแบบของโซ่ให้ kinetic storage ที่แทน Π ได้อย่างมีเงื่อนไข และรายละเอียดการสั่นที่เหลือให้ intrinsic entropy ได้จาก energy law เดียวกัน** แต่ผลนี้ไม่ทำให้ได้ Core kinetics หรือแบบจำลองวัสดุจริงครบชุดโดยอัตโนมัติ

ภาพที่ตรวจคืออะตอมสี่ตัว เราแยกการเคลื่อนที่รวมของทั้งโซ่ออก เก็บการเปลี่ยนรูปแบบประสานกันเป็น Φ และยังเหลือการเคลื่อนที่ภายในอีกสองพิกัด การรวมสองพิกัดหลังออกจาก conditional equilibrium ทำให้ได้ free energy ไม่ต้องเพิ่มพลังงาน information หรือ entropy ของ Φ เป็นสารอีกก้อน

ผลสำคัญที่ต้องอ่านร่วมกัน:

1. **ที่มาของ Π storage ชัดขึ้น:** มาจากพลังงานจลน์ของอะตอมตามรูปร่างการเคลื่อนที่ที่เลือก ไม่ใช่เพียงตั้งชื่อ coefficient ว่า mass มวลเชิงพิกัดนี้มีหน่วย kg·m² เพราะ Φ ไม่มีหน่วย
2. **Entropy ของรายละเอียดการสั่นไม่เท่ากันทุก arrangement:** มีทั้งน้ำหนักจากพลังงานหลังเลื่อนจุดสมดุล และจาก stiffness determinant จึงไม่อาจใช้ log จำนวน configurations อย่างเดียว
3. **การอ่านระยะปลายโซ่ไม่ใช่การอ่าน Φ ล้วน:** โหมดภายในหนึ่งตัวเปลี่ยนระยะปลายด้วย เป็นข้อจำกัด observation map ไม่ใช่ detector backaction ที่ถูกตั้งศูนย์
4. **พบข้อจำกัดของการขยาย parent law ไปไกลเกิน domain:** ถ้าปล่อยให้ระยะอะตอมเข้าใกล้ศูนย์ตาม power law นี้ พลังงานดึงดูดของบาง spin states ทำให้ unconfined partition ไม่อยู่ ไม่ใช่การหักล้างต้นฉบับที่ใช้ small strain
5. **Quadratic reference ยังตรวจได้โดยไม่ซ่อม parent เงียบ ๆ:** มี conditional Gaussian dictionary ที่ exact ใน reference ของมัน แต่ความแม่นยำต่อ parent ต้องมี local Taylor และ tail bounds เพิ่ม และยังไม่รับรอง regime ของวัสดุจริง
6. **Φ ยัง coupling กับรายละเอียดภายใน:** การมีมวลและ free energy ไม่ได้ derive damping, noise, spin-flip rates, Markov closure หรือการเรียนรู้ให้เรา

ดังนั้นความก้าวหน้ารอบนี้คือเปลี่ยนคำว่า “พลังงาน Π/entropy ของโครงสร้าง” ให้มีตัวอย่างสถานะ–พลังงาน–measure ที่ตามตรวจได้ พร้อมจุดที่ใช้ต่อไม่ได้ ไม่ใช่เพิ่มคะแนนหรือรับรองทั้ง UET

## 1. O0 — ฐาน หลักการนำเข้า และขอบเขต

### 1.1 Baseline ที่รักษา

ฐาน local HEAD `91d9a3455b1019a3aafdd5553a662ee594d87a83` ตรงแผน เริ่มบน `codex/research/spin-strain-correspondence` ไม่มี staged changes และมี dirty/untracked statuses เดิม 463 รายการ งานรอบนี้อยู่บน `codex/research/lattice-mechanical-state` ไม่กล่าวว่า local results อยู่บน public main แล้ว

ตรวจ metadata ของ N 13, M 11 และ joint thermal 8 identities โดยไม่รัน science producers เก่า; reviews ยัง INCOMPLETE ตาม physical gaps เดิม เก็บ protected hashes 21 ไฟล์กับ original log/ledger และ unrelated tracked-diff digest ก่อนแก้

หลักฐานเดิม: [รอบ N](UET_SPIN_STRAIN_CORRESPONDENCE_AUDIT.md), [รอบ M](UET_JOINT_STATE_MEASURE_CONSTRUCTION.md), [foundations review](UET_THERMODYNAMIC_FOUNDATIONS_REVIEW.md), [Argument](UET_THEORY_ARGUMENT.md) และ [Core matter-space spec](../core/01_contracts/MATTER_SPACE_RESEARCH_SPEC.md) ไม่ย้ายผล graphite/He-4 หรือ thermal-noise lane มาแทนรอบนี้

### 1.2 Provenance และ primary sources

- **ผู้เขียนยืนยัน scope:** รวมกลศาสตร์ และใช้โซ่ยืดหดเอง ไม่ใช้มวล piston การเลือก scope ไม่ใช่ physical validation
- **Imported physics:** half-spin exchange และ Morse form จาก [Balcerzak–Szałowski–Jaščur, arXiv:2003.12054v2, 7 Apr 2020](https://arxiv.org/pdf/2003.12054), §§II.A–D Eqs. (1), (3)–(11), (18)–(19)
- **Imported framework:** canonical phase-space measure จาก [Tong, Statistical Physics §2.1, Eq. (2.49)](https://www.damtp.cam.ac.uk/user/tong/statphys/statmechhtml/S2.html); phonon mode count และ classical/quantum distinction จาก [§§3.3–3.4](https://www.damtp.cam.ac.uk/user/tong/statphys/statmechhtml/S3.html)
- **AI/model choices ที่เปิดเผย:** finite open chain สี่อะตอม, affine coordinate, equal masses, classical local expansion และหนึ่ง locked algebra control ไม่อ้างว่า paper derive สิ่งเหล่านี้ทั้งหมดให้ UET
- **ผลอนุมานรอบนี้:** canonical map, Gaussian mixture, collision witness และ local error conditions ด้านล่าง แยกจาก actual material correspondence

อ่าน main text ที่ระบุ ไม่ใช้ abstract หรือ material plots เป็นหลักฐาน ไม่เก็บ raw paper/contact/data ใหม่ รอบ N เคยยืนยัน rendered PDF header ว่า v2 แต่ยังไม่มี versioned-byte hash; locator นี้ไม่อ้างความครบถ้วนเกินนั้น

### 1.3 Bounded research card

| รายการ | คำตอบ |
| --- | --- |
| Proposition | ตัวอย่างโซ่หนึ่งชุดให้ที่มาของ kinetic Φ/Π storage และ intrinsic vibrational entropy โดยไม่ซ้ำ state ได้ถึงไหน? |
| มีแล้ว | M counting ตาม declared energy; N nonuniform spin entropy/force และ exact-non-equivalence witness |
| ขาดก่อนรอบ | Mechanical geometry, canonical momentum/measure และ vibrations ที่นับจาก atomic coordinates เดียวกัน |
| Boundary | Independent spins กับ atomic canonical pairs; Φ/u เป็นพิกัดแทน atomic coordinates, k/C เป็น views; ไม่มี detector หรือ bath dynamics |
| Stage/controller | TD1–TD3 / [FORMAL contract ใหม่](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/lattice_mechanical_state_construction.json); ไม่แทน Topic 13 physics gates |
| Action/why | Derive kinetic map และ conditional partition จาก one parent law; ตัดสิน double counting/closure ได้โดยไม่หา material dataset |
| Outcomes | Exact conditional result / bounded approximation / difference / no global extension / unresolved correspondence |
| Stop/reopen | หยุดเมื่อมี witness/derivation เพียงพอ; การรับรองวัสดุต้องมี admissible parent regime และ parameter/preparation evidence ใหม่ |
| Reviewer | Statistical mechanics กับ lattice dynamics: canonical conditioning, local approximation และ coarse kinetic closure ถูกแยกหรือไม่? ยังไม่ติดต่อ |

## 2. ระบบที่เลือก และสิ่งที่ไม่เหมือน N/ต้นฉบับ

<a id="mechanical-parent"></a>

ใช้ N=4, ordered x_1<x_2<x_3<x_4, μ>0 และ free ends พลังงานเป็น

\[
H=\sum_i\frac{p_i^2}{2\mu}+V_s(x),\quad
v_M(r)=D[1-e^{-\delta(r/r_0-1)}]^2,
\tag{O1}
\]
\[
V_s=\sum_{i<j}[v_M(x_j-x_i)-v_M((j-i)d_{\rm ref})]
-\frac{J_{\rm ref}}4\sum_{i=1}^3
\left(\frac{x_{i+1}-x_i}{d_{\rm ref}}\right)^{-\nu}s_is_{i+1}.
\tag{O2}
\]

Elastic pairs มีหกคู่; magnetic bonds มีสามคู่ ไม่เพิ่ม periodic closing bond มี zero external magnetic field/force ทุก coefficient และ scales คงที่เมื่อ differentiate T สปินไม่มี transition law ในรอบนี้

| ปริมาณ | ที่มา/หน่วย | ข้อจำกัด |
| --- | --- | --- |
| μ | Assumed common atomic mass, kg | ยังไม่เลือก atom/material หรือ independent measurement |
| D,J_ref,E_* | Energy, J | D,J_ref เป็น constitutive parameters ไม่ใช่ค่าคำนวณใหม่จาก UET |
| r_0,d_ref,x,u | Length, m | r_0 คือ isolated Morse-pair minimum; d_ref เป็น chosen reference ไม่ใช่ ground state ของ coupled finite chain |
| δ,ν,ε_*,Φ,C/s_C | Dimensionless | ε_* เป็น coordinate scale, ν เป็น exchange exponent ไม่ใช่ oscillator count |
| h | Planck action scale, J·s; classical measure convention | ไม่ได้ทำให้ classical model ใช้ได้ถึง T=0 หรือเป็น quantum phonon calculation |
| p_Φ | Conjugate to dimensionless Φ, J·s | ไม่ใช่ linear momentum kg·m/s |
| M_Φ^phys | Generalized inertia, kg·m² | ต่างจาก mobility ของ Core และจาก μ |

ถ้าจะเทียบ J_ref กับ J_0 ของ source ต้องมี `J_ref=J_0(d_ref/d_0)^(-nu)` ภายใต้ law เดียวกัน ไม่ตั้ง d_ref=d_0 เพียงเพราะใช้สัญลักษณ์คล้ายกัน ค่าคงที่อ้างอิงที่ลบใน O2 ไม่เปลี่ยนแรงและไม่ลบ Φ-dependent terms

N periodic ring กับ O open chain **ไม่ใช่ energy law เดียวกัน** การเปลี่ยน boundary เกิดจาก scope กลศาสตร์ที่เลือก ไม่ยกเลิก N's counterexample และไม่เปลี่ยน old contracts/artifacts ผลต่อ source Debye model อยู่ใน §6

## 3. O1 — พิกัด มวล momentum และ measure

<a id="canonical-mechanical-map"></a>

ให้ a=(-3/2,-1/2,1/2,3/2), E มีคอลัมน์ตามแผน และ

\[
x=d_{\rm ref}(1-\epsilon_*\Phi)a+Eu,
\quad c=\partial_\Phi x=-\epsilon_*d_{\rm ref}a,
\quad E^TE=I,\quad E^Ta=E^T\mathbf1=0.
\tag{O3}
\]

แยก normalized center-of-mass coordinate $Q_0=\mathbf{1}^Tx/2$ และ conjugate p_0 ออก โดยวิเคราะห์ internal system ใน rest frame ไม่อ้างว่า translational entropy ของ physical whole object เป็นศูนย์ หลังตัดคู่นี้เหลือสาม canonical pairs: (Φ,p_Φ) กับ (u_1,p_{u1}),(u_2,p_{u2})

สำหรับ B=[c,E] momentum map มาจาก one-form `p^T dx=p_Phi dPhi+p_u^T du`:

\[
p_\Phi=c^Tp,\quad p_u=E^Tp,\qquad
p=c\,p_\Phi/(c^Tc)+Ep_u,
\]
\[
K=\frac{p_\Phi^2}{2M_\Phi^{\rm phys}}+\frac{p_u^Tp_u}{2\mu},\quad
M_\Phi^{\rm phys}=\mu c^Tc
=5\mu\epsilon_*^2d_{\rm ref}^2.
\tag{O4}
\]

General N identity คือ Σ_i[i−(N+1)/2]²=N(N²−1)/12; N=4 จึง factor5 ไม่เอา mass ของ atom ตัวเดียวมาแทน generalized inertia

Position Jacobian ไม่ใช่1 แต่ inverse-transpose momentum map หักล้างมันใน phase space จึง internal measure คือ

\[
d\Gamma_{\rm int}/h^3
=d\Phi\,dp_\Phi\,d^2u\,d^2p_u/h^3.
\tag{O5}
\]

ใช้ labeled localized sites และ ordered local reference ไม่ใส่ N! หรือ exchange-particle entropy เพิ่มโดยไม่เปลี่ยน construction การตัด center-of-mass เป็น declared conditioning ไม่ใช่การ integrate zero mode แล้วทิ้ง divergence

### 3.1 เทียบ normalized Π/P เดิม

เลือก E_*=J_ref, t_*=d_ref√(μ/J_ref), t_phys=t_*t_norm และ Π=dΦ/dt_norm:

\[
p_\Phi=M_\Phi^{\rm phys}\Pi/t_*,\quad
m_\Phi=\frac{M_\Phi^{\rm phys}}{NE_*t_*^2}
=\frac54\epsilon_*^2,
\quad P=Nm_\Phi\Pi,
\quad p_\Phi=E_*t_*P.
\tag{O6}
\]

ดังนั้น K_Phi/(NE_*)=m_Phi Π²/2 ตรง kinetic-storage form เดิม **เมื่อ**ใช้ normalization/geometry นี้ ใน velocity coordinates measure มี `dp_Phi=(M_Phi^phys/t_*)dPi`; ใน normalized P มี `dp_Phi=E_*t_*dP` ต้องเก็บ action-scale/h และ N m_Phi ไม่เลือก flat dPhi dPi แล้วอ้าง entropy ชุดเดิม

การระบุ `tau/M_Phi_mobility=m_Phi` เป็น matching condition ของหนึ่งตัวอย่าง ไม่ derive tau กับ mobility แยกกัน หรือบังคับ current Core defaults ห้าม fit ε_* เพื่อ match ค่าเก่าแล้วเรียกเป็น independent prediction

### 3.2 Φ ไม่ใช่ readout ปลายโซ่ทั้งหมด

\[
\Phi=\frac{1-a^Tx/(5d_{\rm ref})}{\epsilon_*},\qquad
x_4-x_1=3d_{\rm ref}(1-\epsilon_*\Phi)-u_2/\sqrt5.
\tag{O7}
\]

การวัด end length เพียงช่องเดียวจึงไม่ identify Φ เมื่อ u_2 ยังเปลี่ยนได้ การใช้ source external-force potential f_s L กับ L=N d_0(1+ε) ของ uniform infinite chain ไม่ใช่ port เดียวกับ O7 โดยอัตโนมัติ รอบนี้ f_s=0 และไม่สร้าง detector/backaction model ขึ้นแทนข้อมูลที่ไม่มี

### 3.3 กลศาสตร์ที่ได้และสิ่งที่ยังไม่ปิด

ที่ frozen spins มี Hamilton equations `Phi_dot=p_Phi/Mphys`, `u_dot=p_u/mu`, `p_Phi_dot=-partial_Phi V`, `p_u_dot=-partial_u V` ซึ่งให้ dH/dt=0 ของระบบปิด เมื่อ mixed stiffness ∂_Φ b_s ไม่เป็นศูนย์ การตอบสนอง Φ ขึ้นกับ u ด้วย affine coordinate จึงไม่ใช่ autonomous normal mode โดยชื่อของมัน

การแทน u ด้วย conditional average ให้ mean force ได้ แต่ไม่ได้ prove real-time equilibration/Markov closure หรือสร้าง friction/noise อัตโนมัติ การมี Π เป็น velocity ไม่เท่ากับพิสูจน์ memory lifetime, adaptation หรือ C dynamics

## 4. O2 — รวม vibrations ออกจากพลังงานชุดเดียวกัน

<a id="conditional-vibrational-dictionary"></a>

ที่ fixed Φ และ spin arrangement ให้ Taylor ใน u เท่านั้น:

\[
V_s^{(2)}=V_{s0}+b_s^Tu+\tfrac12u^TK_su,
\quad b_s=E^T\nabla_xV_s|_{u=0},
\quad K_s=E^T(\nabla_x^2V_s)E|_{u=0}.
\tag{O8}
\]

ทุก V0,b,K มาจาก pair law O2 จริง ที่ locked control มี hidden Hessian positive definite แต่ b และ mixed affine-hidden stiffness โดยทั่วไปไม่เป็นศูนย์ ต้องเก็บการเลื่อน u_* =−K_s^{-1}b_s:

\[
V_{s,\rm eff}=V_{s0}-\tfrac12b_s^TK_s^{-1}b_s.
\tag{O9}
\]

ให้ r=N−2=2 และ K_s>0 Gaussian integration บน quadratic reference ทั้ง R² ให้ dimensionless factor

\[
A_s(\Phi,T)=\left(\frac{2\pi k_BT}{h}\right)^r
\sqrt{\frac{\mu^r}{\det K_s}},\qquad
Z_s=e^{-\beta V_{s,\rm eff}}A_s.
\tag{O10}
\]

Equivalent conditional frequencies คือ eigenvalues ของ K_s/μ; product ω_1ω_2=√detK_s/μ ทำให้ mode-product และ direct Gaussian ใช้ measure เดียวกัน ไม่จำเป็นต้องเพิ่ม state ของ phonon ซ้ำอีกชุด

ที่ fixed k,Φ,p_Φ:

\[
Z_k=\sum_{s:k(s)=k}Z_s,\quad p_s=Z_s/Z_k,
\quad F_k=K_\Phi-k_BT\ln Z_k,
\]
\[
U_k=K_\Phi+\sum_s p_s V_{s,\rm eff}+r k_BT,
\]
\[
S_{{\rm int},k}=-k_B\sum_sp_s\ln p_s
+\sum_s p_s k_B[\ln A_s+r].
\tag{O11}
\]

Thermal derivatives ล็อก k,Φ,p_Φ, coefficients, scales และ measure จึง F=U−TS และ S=−∂_TF ใน quadratic reference พจน์ r k_BT มีทั้ง potential และ kinetic ของ hidden oscillators ไม่รวม retained kinetic อีกครั้ง

Entropy แถวแรกของ O11 เป็น uncertainty ระหว่าง arrangements แถวหลังเป็น conditional continuous entropy ของ vibrations ตาม h measure ไม่ใช่ entropy ของ distribution บน retained Φ/Π ทั้งหมด หากภายหลังมี retained density q ให้รวมเป็น `S_full=S_ret[q]+<S_int>_q` ตาม chain rule ด้วย measure เดียวกัน ไม่เรียก information ทุกความหมายว่า S_int

### 4.1 Mean force และ entropy consistency

เมื่อ generalized inertia ไม่พึ่ง Φ ตาม linear coordinate map นี้:

\[
f_\Phi=-\partial_\Phi F_k
=\sum_s p_s\left[-\partial_\Phi V_{s,\rm eff}
-\frac{k_BT}{2}\operatorname{tr}(K_s^{-1}\partial_\Phi K_s)\right],
\quad \partial_Tf_\Phi=\partial_\Phi S_{{\rm int},k}.
\tag{O12}
\]

ตรวจคู่กับ microscopic force average โดยใช้ mean u_* และ covariance k_BT K_s^{-1}; ต้องมีทั้ง b' mean และ K' second moment ที่ถูกต้อง การละ shift หรือ determinant เป็นคนละ model ไม่ใช่ cosmetic normalization

**ผลต่อ M/N:** แม้มี k/C เท่ากัน weights ใน O ยังขึ้นกับ arrangement ผ่าน V_eff และ detK จึงไม่สมมติ spin/vibration factorization ส่วน zero-exchange limit ที่ตรึง elastic D ไว้ทำให้ mechanical factors ไม่ขึ้นกับ s และได้ binomial multiplicity กลับมา แต่ vibrational entropy ยังไม่หายไป ข้อความ D=8J ของ unit control ไม่ใช่ parameter law ที่ใช้เมื่อทำ decoupling limit

Global spin flip ให้ V0,b,K เหมือนเดิม จึงการอ่าน |C| โดยยังเก็บ signed state ไม่เปลี่ยน interaction ส่วนการ fold state เป็น magnitude ต้องรวม weights ของ k กับ N−k และนับ k=N/2 ครั้งเดียว แต่ |Φ| ไม่ใช่พิกัด compression ที่ย้อนกลับได้: Morse/exchange ไม่บังคับ compression และ extension ให้เหมือนกัน และ reference force ใน control ไม่เป็นศูนย์ การลืมเครื่องหมายจึงต้องถือเป็น readout loss ไม่ใช่ symmetry ใหม่หรือการระบุปฏิสสาร/imaginary

## 5. O3 — Positive local reference ไม่เท่ากับ global parent equilibrium

<a id="parent-local-validity"></a>

### 5.1 Locked control และ positivity

ใช้ Φ=0, d_ref=r_0, δ=ln2, D=8J_ref, ν=2, ε_*=1 เท่านั้นเป็น algebra regression ไม่ใช้ material numbers ค่า d_ref=r_0 ไม่ใช่ผล EOS ของ source หรือของ coupled finite chain

ใน J_ref/d_ref² units NN elastic curvature คือ16(ln2)²; magnetic curvature คือ−3s_is_(i+1)/2; next-nearest elastic curvature0; end-to-end curvature−2(ln2)² สำหรับ displacement ที่ไม่มี translation:

\[
v^T(\nabla_x^2V_s)v
\ge [10(\ln2)^2-3/2]\sum_{i=1}^3(v_{i+1}-v_i)^2>0.
\tag{O13}
\]

ใช้ `(v_4−v_1)^2≤3Σ(diff v)^2` และ ln2>1/2 เพื่อรับรอง all16 spin arrangements ไม่ใช่ floating tolerance การฉายบน E จึงให้ K_s>0 และ continuity ให้ local neighborhood บางช่วง ไม่รับรอง strain ทุกค่า/ทุก parameter

### 5.2 Collision witness: global continuation ใช้ไม่ได้

ที่ fixed Φ=0 เลือก nearest gaps ใน d_ref units เป็น `(t,7/4−3t/4,1)`, t→0+ แล้วเลื่อน center of mass กลับศูนย์ จะยังได้ a^Tx=5 และ gaps อื่นเป็นบวก ที่ all-plus spins:

\[
V_s(t)=-\frac{J_{\rm ref}}4(t/d_{\rm ref})^{-\nu}+O(1),
\quad \int_0^\eta e^{c/t^\nu}dt=\infty\quad(c,\nu>0).
\tag{O14}
\]

Morse potential finite เมื่อคู่หนึ่งชน แต่ negative exchange term นี้ไม่ finite พิจารณา tube ของ transverse coordinate ช่วงบวกคงที่รอบ path ที่ยังมี gaps อื่นห่างศูนย์ จึงไม่ใช่เพียง singularity บน zero-measure line การ integral over hidden u ของ parent ที่ไม่มี local restriction จึงไม่อยู่สำหรับ class ที่มี witness นี้

นี่จำกัด **การขยาย power law ออกนอก small-strain domain** ไม่หักล้าง source หรือบอกว่า material จริงยุบแบบนี้ ไม่เพิ่ม hard-core repulsion, cutoff หรือ counterterm เพื่อหลบผล การเลื่อน H ด้วยค่าคงที่ก็แก้ divergence ไม่ได้

### 5.3 Local value error และ Gaussian tails

สำหรับ |ε_*Φ|≤ρ<1 กำหนด local ball ||u||≤R=d_ref(1−ρ)/4 ซึ่งทำให้ระยะทุกคู่ยังบวก เพราะ |(E_j−E_i)u|≤√2 R ค่า bound ต่อ third derivative ของ pair potential หาได้บน interval

`r_ij ∈ [(j−i)d_ref(1−rho)−sqrt(2)R, (j−i)d_ref(1+rho)+sqrt(2)R]`.

สำหรับ Morse ใช้ `|v'''|≤2D(delta/r0)^3(y_max+4y_max²)`, y_max=exp[−δ(r_min/r0−1)]; สำหรับ magnetic NN ใช้ `J_ref nu(nu+1)(nu+2)d_ref^nu/(4 r_min^(nu+3))` แล้วคูณ norm ของ pair direction กำลังสามและรวมทุกคู่ จะได้ M_3 ที่มีหน่วย energy/length³ และ

\[
|V_s-V_s^{(2)}|\le\varepsilon_V=M_3R^3/6.
\tag{O15}
\]

ภายใต้ Gaussian ของแต่ละ arrangement ให้

\[
\eta_s=\frac{\|u_{*,s}\|^2+k_BT\operatorname{tr}K_s^{-1}}{R^2},
\quad P_s(\|u\|>R)\le\eta_s.
\]

เมื่อทุก K_s>0 และ η=max_sη_s<1 จึงได้ conservative value comparison ของ **parent ที่ condition อยู่ใน local ball** กับ full quadratic reference:

\[
|F_{k,\rm parent;ball}-F_{k,\rm quadratic;full}|
\le\varepsilon_V-k_BT\ln(1-\eta).
\tag{O16}
\]

ball เป็น comparison/preparation condition ไม่ใช่ physical stabilizing interaction ใหม่ ถ้า η≥1 bound นี้ให้ log certificate ไม่ได้ ต้องรายงานว่าไม่รับรอง ไม่เปลี่ยน R หรือ parameters เพื่อผ่าน และ O16 ไม่ให้ force/lifetime/global-parent error bound

### 5.4 Classical กับ localized regime ต้องมีช่วงทับกันจริง

Actual vibrational interpretation ต้องมี k_BT มากกว่า quantum spacing ที่เกี่ยวข้อง ขณะที่ local expansion/tail ต้องไม่กระจายออกนอก ball ทั้งสองข้ออาจไม่มี useful common window เมื่อยังไม่ทราบ material constants และ reference shift จึงไม่อ้างว่ามีอยู่แล้ว ไม่ใช้ classical entropy ที่ T→0 เป็นคำทำนาย third law

Conditional eigenfrequencies ที่ fixed Φ ไม่ใช่ complete free-chain spectrum ถ้า retained/hidden modes ยัง coupled; quantum treatment และ actual preparation ยังเป็น prerequisite ต่างหาก ไม่บวก three-polarization Debye entropy มาปิดช่องว่างนี้

## 6. O4 — คำวินิจฉัยและขอบเขตการใช้ต่อ

| สะพาน | Verdict | สิ่งที่ยังห้ามอ้าง |
| --- | --- | --- |
| Atomic coordinates ↔ Φ/u | EXACT หลัง CM conditioning | ไม่ใช่ detector calibration หรือ full observability จาก end length |
| Atomic kinetic ↔ Π storage | CONDITIONAL EXACT scale map | ไม่เลือก tau/mobility แยกกัน ไม่รับรอง universal Φ mass |
| Quadratic hidden modes ↔ F/U/S | EXACT เมื่อ K_s>0 ตาม measure | ไม่ใช่ global parent equilibrium หรือ entropy ของทุก UET information |
| Parent ↔ local quadratic | CONDITIONAL bound O15–O16; global extension NOT ADMITTED | ไม่ให้ omission/tail effects เป็นศูนย์หรืออ้าง material accuracy |
| Open chain ↔ N periodic/source continuum | DIFFERENT declared geometry/mode scope | ไม่ใช้ N's old partition หรือ source unconstrained G เป็น fixed-k O partition |
| O free energy ↔ even-quartic Ω | PARTIAL/DIFFERENT | Reference linear force, shift/determinant และ arrangement corrections ไม่หายเอง |
| Conservative microscopic ↔ Core dissipative kinetics | NOT CLOSED | ไม่ได้ C rates, friction, noise, heat trajectory หรือ Markov reduction |
| Physical material/learning/cosmology | UNRESOLVED / NO PROMOTION | Formal completion ไม่ยืนยันหรือปฏิเสธข้อเสนอรวมทั้งทฤษฎี |

ไม่ตัด linear/cubic terms เพื่อให้ดูเป็น Ω เก่า ไม่มีการนำ coefficient ของ local normal modes ไปสวมเป็น metric, Π มวล SI สากล หรือ physical temperature anchor ของ Topic 13 อื่น

**คำถามผู้เชี่ยวชาญ:** (1) ตรวจ canonical map/CM-conditioned measure และ generalized inertia O3–O7; (2) ตรวจ shifted Gaussian mixture และ fixed-coordinate F/U/S/force O8–O12; (3) ตรวจ collision tube กับ local-tail certificate O14–O16; (4) ต้องมีหลักฐานใดจึงเลือก physical classical/local window และ coarse kinetic reduction ได้ ขอเฉพาะชุดนี้ ไม่ส่งทั้ง archive และยังไม่ติดต่อภายนอก

**หนึ่ง prerequisite ถัดไป:** admissible parent/regime และ reduction evidence ที่ทำให้ local mechanical reference แทน physical preparation ได้จริง ไม่ใช่เพิ่ม detector dataset หรือ kinetics โดยอัตโนมัติ ถ้าคง parent law เดิมแบบ global ผล collision no-go ต้องคงอยู่ ไม่ rerun เพื่อหา acceptance เดิมอีก

## 7. Verification และ local checkpoint

[Producer ใหม่](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Lattice_Mechanical_State_Construction.py), [tests](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_lattice_mechanical_state_construction.py), [contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/lattice_mechanical_state_construction.json) และ [artifact](../topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_lattice_mechanical_state_construction.json) เป็นเส้นทางใหม่แยกจาก M/N

ใช้ exact symbolic residuals, all16 spin labels ของหนึ่ง locked N=4 control, independent direct derivatives ของ parent energy และ analytic proofs ไม่ใช้จำนวน tests เป็นคะแนนทฤษฎี `--check` อ่านอย่างเดียว; `--emit-report` สร้างเฉพาะ artifact ใหม่พร้อม source/contract identities ไม่มี random sampling/sweep/trajectory หรือ old science rerun

ผลตรวจที่รันจริงและส่วนที่ยังเปิดบันทึกใน [Topic UPDATE_LOG](../topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md) และ [daily ledger](../../WORK_LEDGER/2026/2026-10-24.md) Construction/adversarial self-review ไม่ใช่ independent specialist approval ไม่เปลี่ยน public API/Core/defaults/thresholds/README/gates และไม่ push/merge/เผยแพร่หรือเริ่มรอบถัดไปอัตโนมัติ
