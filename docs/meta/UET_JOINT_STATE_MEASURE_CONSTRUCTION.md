# รอบ M — ฐานร่วม C–Phi–Pi: การนับสถานะ พลังงาน และ entropy

วันตัดยอด: 24 ตุลาคม 2026 • พื้นที่งาน: `research-core` • ขอบเขต: FORMAL static reference

## สรุปสำหรับผู้เขียน

**ตัวอย่างที่กำหนดในรอบนี้ให้บัญชี free energy, intrinsic entropy และ internal energy ร่วมกันได้แบบมีเงื่อนไข** ไม่ต้องเรียก C หรือ Φ ว่า entropy และไม่ต้องเพิ่มพลังงานของ information อีกก้อน

ภาพที่ได้คือ: เราเก็บค่า C ซึ่งบอกสัดส่วนสถานะสองแบบ แต่ไม่ได้เก็บว่าองค์ประกอบตัวไหนอยู่แบบไหน การจัดเรียงหลายแบบที่ให้ C เดียวกันคือรายละเอียดที่ถูกซ่อน การนับรายละเอียดนั้นให้ intrinsic entropy ส่วนพลังงานมาจาก energy law ที่ประกาศแยกต่างหาก เมื่อรวมรายละเอียดออกจึงได้ free energy ซึ่งไม่ใช่ internal energy

ผลสำคัญมีห้าข้อ:

1. ที่สถานะรวมหนึ่งค่า **พลังงานภายในยังเป็นค่า H ของ energy law** แต่ free energy มีส่วนลบ `T × entropy ของการจัดเรียง` จึงไม่ใช่พลังงานอีกชื่อหนึ่ง
2. Φ และ Π ถูกเก็บโดยตรงในตัวอย่างนี้ จึงไม่ได้เพิ่ม hidden entropy ของ Φ แต่ distribution บน Φ/Π ยังมี entropy ได้ และ entropy ของ Φ ทางกายภาพของ UET ยังไม่ทราบ
3. Ω แบบ quartic เดิมเชื่อมกับตัวอย่างนี้ได้ผ่าน large-N/small-C approximation และสัมประสิทธิ์ที่มี thermal dependence ตามที่แสดง ไม่ใช่ exact microscopic identity ของ Core ทุกชุด
4. การอ่านแค่ขนาด C ไม่เหมือนการลบเครื่องหมายออกจาก state: อย่างแรกเปลี่ยนคำตอบที่อ่าน อย่างหลังเปลี่ยนการจัดกลุ่มและ entropy accounting
5. นี่เป็นตัวอย่างมาตรฐานทาง statistical mechanics ที่ทำให้รอยต่อชัดขึ้น **ยังไม่มีผลเฉพาะที่แยก UET จาก comparator และยังไม่ให้กฎ heat ในเวลาจริง**

สิ่งที่ผู้เขียนยังไม่ต้องทำ: ไม่ต้องตรวจคณิตศาสตร์เอง ไม่ต้องเลือกข้อมูลทดลองหรือคิด coefficients เพิ่ม คำถามเชิงเจตนาที่ยังเปิดคือสถานะในตัวอย่างนี้แทนความหมาย information/ผลคงอยู่ที่ต้องการได้มากน้อยเพียงใด ไม่ใช่บังคับให้ information ทั้งทฤษฎีเท่ากับ entropy นี้

## 1. M0 — ฐานหลักฐานและขอบเขต

### 1.1 Lineage และสิ่งที่รักษา

- Working directory คือ checkout หลัก `uet_harness`; branch `codex/research/source-backaction-discrimination` ไม่มี upstream
- HEAD เริ่มรอบตรงกับแผน: `6a971bd0c24684738842ae8ae6a9b48477c433f6` เป็น **local commit** ไม่ใช่การยืนยัน public main ล่าสุด
- เริ่มรอบด้วย index ว่างและ 463 dirty/untracked status entries ที่มีมาก่อน รวม Topic 13 UPDATE_LOG ซึ่งมี diff เก่า 578 เพิ่ม/79 ลบ รักษางานเหล่านั้น ไม่รวมเข้า commit รอบนี้
- ไม่ fetch/push หรือเทียบ GitHub สด ไม่อ้างว่าหลักฐาน working copy/local commit เผยแพร่แล้ว แหล่งภายนอกด้านล่างเป็น public primary texts; ไม่มี private/raw source ถูกคัดเข้ารายงาน
- ใช้ [Foundations Review §§7–10](UET_THERMODYNAMIC_FOUNDATIONS_REVIEW.md#thermal-dictionary-followup), [Argument §14 และ §§17–19](UET_THEORY_ARGUMENT.md), [§30](UET_THEORY_ARGUMENT.md#joint-thermal-reference) และ [spec เดิม](../core/01_contracts/MATTER_SPACE_RESEARCH_SPEC.md) ไม่รันงานเก่าเหล่านั้นใหม่
- ช่องว่าง `intrinsic-entropy-correspondence` ใน [joint contract เก่า](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/joint_thermodynamic_completion.json) ยังควบคุม physical HIST-F เหมือนเดิม ไม่มีการแก้ contract/artifact/gate เก่า

### 1.2 Bounded work card

| รายการ | ข้อกำหนดของรอบนี้ |
| --- | --- |
| คำถาม | ตัวอย่างร่วมหนึ่งชุดให้ constrained F/U/S และเชื่อม Ω เดิมได้จริงถึงไหน? |
| มีแล้ว | C binary bridge, bounded quartic expansion, conditional REF-E และ comparator equivalence; ใช้ผลเดิมตาม domain |
| ขาดก่อนรอบ | joint conditioning, fixed measure, finite-N counting และ thermal family สำหรับตัวอย่างหนึ่งชุด |
| Action / เหตุผล | ประกาศ energy/state/measure หนึ่งชุด แล้ว derive restricted sum และ identities; สิ่งนี้ตัดสินรอยต่อได้โดยไม่หาวัสดุใหม่ |
| Boundary | Binary configurations กับ retained Φ/P อยู่ใน reference; ไม่มี bath microstates, detector, spatial signal หรือ time evolution |
| Stage / controller | TD1–TD3 เฉพาะ reference นี้; [FORMAL contract ใหม่](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/joint_state_measure_construction.json) และ artifact ใหม่ ไม่แทน controller กายภาพเดิม |
| ผลที่รับได้ | สอดคล้องตามเงื่อนไข / ขัดแย้ง / approximation เท่านั้น / เทียบเท่าคู่เทียบ / premise ไม่พอ |
| จุดหยุด | จบที่ static dictionary และคำวินิจฉัย; ไม่เปิด kinetics หรือ microscopic sector ใหม่ หากสองความพยายามไม่เปลี่ยนคำตัดสินให้ระบุ prerequisite |
| คำถามผู้ตรวจ | class/measure/thermal derivatives และ finite-N/limit ที่อ้างตรงกันหรือไม่? ขอ statistical-mechanics specialist ตรวจเฉพาะรอยต่อนี้; ยังไม่ติดต่อ |

### 1.3 Provenance ของความคิด

| ชนิด | สิ่งที่ใช้ในรอบนี้ | สิ่งที่ไม่อนุมาน |
| --- | --- | --- |
| เจตนา/การตัดสินใจผู้เขียน | อนุมัติตัวอย่างร่วมหนึ่งชุด ปิดฐานเทอร์โมก่อน เก็บ Φ/Π โดยตรง และตรวจทั้ง signed/magnitude | ไม่ถือว่าอนุมัติ physical microscopic ontology ของ UET หรือกำหนด information เท่ากับ entropy |
| Imported physics | Canonical conditioning, state counting, entropy chain rule และ controlled mean-field expansion | การอ้างชื่อทฤษฎีไม่ทำให้ microscopic correspondence สำเร็จ |
| AI constitutive choice | Energy law ด้านล่าง, affine Φ coupling, flat dimensionless measure, coefficients คงที่ต่อ T | ไม่ปลอมเป็น derivation จากหลักคิดผู้เขียนหรือค่าที่ได้จากการทดลอง |
| Derivation รอบนี้ | Restricted F/U/S, finite-N value bound, normalization, folding accounting และ joint comparison | ไม่ใช่ empirical validation หรือ proof ของ learning/cosmology |

หลักการ constrained F/S/U ใช้ [Seifert 2012, arXiv:1205.4176v1, §9.2.1 Eqs. (206)–(209)](https://arxiv.org/html/1205.4176) โดยแยกจาก time-scale/dynamic assumptions ใน §§9.2.2–9.2.4; ต้นฉบับใช้ k_B=1 และสัญลักษณ์ Φ ของ paper ไม่ใช่ Φ ของ UET

การเปรียบ state counting/mean-field ใช้ [Tong, Statistical Field Theory Ch. 1, §§1.1.1–1.2, Eqs. (1.7)–(1.13)](https://www.damtp.cam.ac.uk/user/tong/sft/sfthtml/S1.html) official HTML ไม่มี revision ID ที่ยืนยันได้ ตรวจ main text เมื่อ 24 ตุลาคม 2026 ไม่ใช้ nearest-neighbor approximation เป็น exact energy law ของตัวอย่างนี้

## 2. ตัวอย่างและสิ่งที่นับจริง

### 2.1 Microstate, retained state และ domain

ให้ configuration `s=(s_1,...,s_N)` มี s_i=±1 และ N≥2 เป็นจำนวนเต็ม ที่ fixed k จำนวนสถานะบวก:

\[
m_k=\frac{2k-N}{N},\quad C=s_Cm_k,\quad k\in\{0,\ldots,N\},\quad s_C>0.
\]

microstate ของ reference คือ (s,Φ,P) ส่วน retained state คือ (k,Φ,P) หรือเทียบเท่า (C,Φ,Π) บนกริด C ที่กำหนด ไม่ใช่สามตัวแปรอิสระบน R³ กำหนด

\[
m_\Phi=\tau/M_\Phi>0,\qquad P=Nm_\Phi\Pi.
\]

P เป็น normalized integration coordinate และเป็นฟังก์ชันของ Π ไม่เพิ่ม independent state การใช้คำว่า kinetic storage ไม่ได้ derive ว่า Π=dot Φ หรือเลือก symplectic/kinetic law แล้ว ทั้งหมดใช้ normalization ไร้มิติของ state; E_* เป็น energy scale ที่ยังไม่ผูกกับวัตถุจริง

เลือก fixed reference measure: counting measure บน configurations หรือ k และ `dΦ dP` บน retained continuous coordinates ไม่มี degeneracy แอบเพิ่มใน measure นี้ ใน Π coordinates ใช้ `N m_Φ dΦ dΠ` ซึ่งเป็น pushforward เดียวกัน

<a id="reference-energy"></a>

### 2.2 Energy law ที่เลือก ไม่ใช่ผลบังคับจาก UET

\[
v_\Phi=\frac{a_\Phi}{2}\Phi^2+\frac{b_\Phi}{4}\Phi^4,
\qquad
\frac{H_N}{E_*}=N\left[-\frac{j_0+\gamma\Phi}{2}m_k^2+v_\Phi\right]
+\frac{P^2}{2Nm_\Phi}.
\tag{M1}
\]

E_*,j_0,s_C,τ,M_Φ,b_Φ,T,k_B>0; γ,a_Φ≥0; Φ,P∈R และไม่มี bias h ล็อกทุก coefficient, N, scale และ measure ไม่ให้พึ่ง T ใน reference นี้ เงื่อนไขนี้ **ไม่ได้ตามจาก runtime constants ของ Core หรือ material calibration**

พลังงาน binary เท่ากับ `-E_*(j_0+γΦ)(Σ_i s_i)²/(2N)` ตามนิยาม เป็น fully connected mean-field energy ที่ขึ้นกับ configuration ผ่าน k เท่านั้น ไม่ใช่ nearest-neighbor Ising ที่พลังงานขึ้นกับรูปการจัดเรียงด้วย

**Finite-N convention ที่ห้ามซ่อน:** รูป square-of-sum นี้รวม diagonal i=j เมื่อเขียนเป็น pair sum จึงมี term `-E_*(j_0+γΦ)/2` ด้วย มันขึ้นกับ Φ; จะตัดออกเหมือนเป็นค่าคงที่ที่ไม่สำคัญไม่ได้ การใช้ off-diagonal-only Hamiltonian เป็นอีก energy law ไม่ใช่ exact rewrite ของ M1 เว้นแต่รักษา term นี้ไว้ รอบนี้ไม่เปลี่ยน convention เพื่อให้ mapping ดูง่าย

Interaction `-N E_* γ Φ m²/2` อยู่ใน H ร่วมเพียงครั้งเดียว ไม่บวกเป็นพลังงานของแต่ละระบบซ้ำ ความสามารถแยก state เป็น subsystem ไม่ได้ให้ interaction-energy allocation เอกลักษณ์

## 3. M1 — Restricted counting และ thermodynamic dictionary

<a id="restricted-dictionary"></a>

### 3.1 Derivation ที่ fixed retained state

มี \(G_N(k)=\binom Nk\) configurations ใน class ที่ k คงที่ ทุก configuration ใน class มี H เท่ากันตาม M1 จึงได้

\[
Z_{k,\Phi,P}=G_N(k)e^{-H_N/(k_BT)},\qquad
p(s\mid k,\Phi,P)=G_N(k)^{-1}.
\]

นิยาม constrained free energy จาก restricted sum โดยตรง:

\[
F_N=-k_BT\ln Z_{k,\Phi,P}=H_N-k_BT\ln G_N(k).
\tag{M2}
\]

Derivative ล็อก k (หรือ C เมื่อ N,s_C คงที่), Φ,P, coefficients, scales และ measure แล้วจึงให้

\[
S_{\rm int}=-\partial_TF_N=k_B\ln G_N(k),\qquad
U_{\rm cond}=F_N+TS_{\rm int}=H_N.
\tag{M3}
\]

เท่ากันกับ conditional average Σ_s p(s|k)H_N เพราะ H คงที่ใน class และกับ ∂_β(βF_N), β=1/(k_BT) ห้ามตรึงสัมประสิทธิ์ effective ที่มี T-dependence หลัง derive แล้วค่อยเรียก derivative นั้นว่า thermal derivative เดียวกัน

ตัวอย่าง exact: N=4,k=2 มี 6 arrangements, S_int=k_B ln6; endpoint k=0,N มีหนึ่ง arrangement และ S_int=0 ไม่ใช่การแทน log0 ส่วน N k_B h_2(m) เป็น approximation อีกขั้น ไม่ใช่ exact finite-N entropy

ความเป็น uniform ที่นี่เป็น canonical equilibrium ของ energy law ที่เลือก ไม่มี spin-flip rates หรือหลักฐานว่า configurations สลับเร็วจริง จึงยังไม่อ้าง local equilibration ในเวลาจริง, Markov closure หรือ retention lifetime

### 3.2 Partition sum และ entropy ทั้งระบบ

\[
Z_N=\sum_s\int d\Phi\,dP\ e^{-H_N/(k_BT)}
=\sum_{k=0}^N\int d\Phi\,dP\ e^{-F_N/(k_BT)}.
\tag{M4}
\]

ขวามือ **ไม่คูณ G_N อีก** เพราะนับไปแล้วใน F_N การพิสูจน์คือแยก disjoint configuration classes และใช้ M2 ก่อนอินทิเกรต จึงไม่จำเป็นต้องแก้ quartic Φ integral เป็น closed form

ให้ q(k,Φ,P) เป็น normalized retained density ตาม measure เดิม และ conditional distribution uniform จะได้ p_micro=q/G_N จากการแทนใน Gibbs entropy:

\[
S_{\rm full}=S_{\rm ret}[q]+\langle S_{\rm int}\rangle_q,
\quad S_{\rm ret}[q]=-k_B\sum_k\int q\ln q\ d\Phi dP.
\tag{M5}
\]

ทั้งสองเป็นคนละระดับของ distribution ไม่ใช่พลังงานหรือ independent information substance หาก hidden conditional distribution ไม่ uniform ต้องใช้ conditional Shannon entropy จริง ไม่แทนด้วย ln G_N โดยไม่มีเงื่อนไข

ที่ equilibrium q_eq=Z_N^(-1)exp(-F_N/k_BT) จะได้

\[
\mathcal F_{\rm ens}=-k_BT\ln Z_N
=\langle F_N\rangle-k_BT[-\langle\ln q_{\rm eq}\rangle]
=\langle H_N\rangle-TS_{\rm full}.
\tag{M6}
\]

F_N เป็น **constrained landscape**; 𝓕_ens เป็น ensemble free energy หลังรวม retained states อีกชั้น; U_cond=H_N ไม่ใช่คำกล่าวว่า ensemble internal energy ไม่เปลี่ยนกับ T เพราะ ⟨H_N⟩ ยังขึ้นกับ thermal distribution

แม้ไม่มี hidden Φ states เพิ่มในนิยาม Φ/P distribution ยังมี entropy ได้ Gaussian P factor เป็น \(\sqrt{2\pi N m_\Phi\theta}\) เมื่อ θ=k_BT/E_* การไม่รวม P ออกเป็นการเลือกเก็บสถานะไว้ ไม่ใช่การอ้างว่า thermal distribution ของ P ไม่มีผล

## 4. M2 — Measure, N และการเทียบ Ω

### 4.1 การแปลง Π ไม่ใช่การเปลี่ยน state counting

จาก P=N m_Φ Π ได้ J=N m_Φ และ

\[
Z_N=\sum_k\int N m_\Phi\,d\Phi d\Pi
\exp\left[-\frac{F_N(k,\Phi,Nm_\Phi\Pi;T)}{k_BT}\right].
\tag{M7}
\]

ใช้ fixed pushforward measure นี้ entropy accounting ไม่เปลี่ยน หากเลือก flat `dΦ dΠ` แทนจริง ๆ ต้องย้าย J เข้า density หรือ potential **อย่างใดอย่างหนึ่ง** เช่น F_flat=F∘P−k_BT lnJ สำหรับ M4; จะใส่ทั้งสองซ้ำไม่ได้ การย้าย reference นี้ไม่ใช่ hidden binary entropy เพิ่มหรือการพิสูจน์ physical canonical momentum

Derivative ข้าม T ใช้ได้ดัง M3 เพราะ J,m_Φ คงที่ตามสมมติฐาน หากภายหลัง τ,M_Φ หรือ normalization พึ่ง T ต้องทบทวน fixed physical coordinate และ measure ใหม่ ไม่ใช้ผลนี้ต่อโดยอัตโนมัติ

### 4.2 Exact finite-N landscape

\[
\frac{F_N(k,\Phi,Nm_\Phi\Pi;T)}{NE_*}
=f_N(m_k,\Phi;\theta)+\frac{m_\Phi}{2}\Pi^2,
\]
\[
f_N=-\frac{j_0+\gamma\Phi}{2}m_k^2+v_\Phi
-\frac{\theta}{N}\ln\binom Nk.
\tag{M8}
\]

ดังนั้น exponent ที่ถูกต้องคือ `(f_N+storage)/(θ/N)` ไม่ใช่หารด้วย θ โดยลืม N และไม่แทน θ/N ว่าเป็น SI temperature ที่สอบเทียบแล้ว ใช้ C=s_Cm_k ได้เฉพาะกริด [-s_C,s_C] ใน reference นี้

<a id="finite-n-bound"></a>

### 4.3 Finite-N entropy bound — ผลใหม่ที่พิสูจน์ได้

ให้ q=k/N, h_2(m_k)=−q lnq−(1−q)ln(1−q) โดย 0ln0=0 และ

\[
B_k=\binom Nk q^k(1-q)^{N-k}=\exp[\ln G_N-Nh_2].
\]

สำหรับ 0<k<N สมาชิกนี้เป็น mode ของ Binomial(N,q): อัตราส่วน B_(ell+1)/B_ell เทียบ 1 มี numerator difference `N(k−ell−1)+k` เป็นบวกเมื่อ ell≤k−1 และเป็นลบเมื่อ ell≥k ส่วน endpoints มี B_k=1 โดยตรง สมาชิก N+1 ตัวรวมกันได้ 1 จึง 1/(N+1)≤B_k≤1 แล้ว take log ได้

\[
\boxed{0\le h_2(m_k)-\frac{\ln\binom Nk}{N}\le\frac{\ln(N+1)}{N}.}
\tag{M9}
\]

นี่เป็น proof สำหรับทุก N≥2 และ k ที่ยอมรับ ไม่ใช่การสรุปจาก regression สี่ค่า ผลต่อ free energy ต่อ site คือ 0≤f_N−f_∞≤θ ln(N+1)/N โดย f_∞=−(j_0+γΦ)m²/2+v_Φ−θh_2(m)

<a id="omega-correspondence"></a>

### 4.4 Controlled quartic bridge และสิ่งที่ไม่ตรงแบบ exact

รับ coefficient map และ Taylor remainder จาก [Argument §14.4](UET_THEORY_ARGUMENT.md) มาใช้ ไม่รัน scans/minima/fixtures เก่าซ้ำ:

\[
a_C(T)=\frac{\theta-j_0}{s_C^2},\quad
b_C(T)=\frac{\theta}{3s_C^4},\quad g=\frac{\gamma}{s_C^2}.
\]

\[
f_\infty=\Omega_4(C,\Phi;T)-\theta\ln2+R_f,
\quad
\Omega_4=\frac{a_C}{2}C^2+\frac{b_C}{4}C^4+v_\Phi-\frac{g}{2}C^2\Phi.
\tag{M10}
\]

ที่ |m_k|≤ρ<1:

\[
0\le f_N-[\Omega_4-\theta\ln2]
\le\frac{\theta\ln(N+1)}{N}
+\frac{\theta|m_k|^6}{30(1-\rho^2)}.
\tag{M11}
\]

เป็น conservative sum ของ value bounds ไม่มีสมมติ error independence ไม่ได้รวม nearest-neighbor correlation, material mapping, measurement หรือ spatial error และ **ไม่ได้ให้ finite-N force bound** เพราะ exact finite-N C เป็นกริด การหา derivative ของ value bound อย่างเดียวทำไม่ได้

การแทน finite grid ด้วย integral ต้องมี grid density: formal Riemann replacement Σ_k≈(N/2)∫dm=(N/(2s_C))∫dC ซึ่งไม่ใช้เป็น exact finite-N equality หรือพร้อมทิ้ง normalization ทุกกรณี รอบนี้ไม่ certify saddle-point/global partition error จาก M11 และไม่ยก bounded binary domain เป็น all-R diffusion

ส่วนที่ derive เพิ่มจาก thermal family นี้: เมื่อใช้ F_4=NE_*[Ω_4−θln2+m_ΦΠ²/2] จะได้

\[
S_{{\rm int},4}=Nk_B[\ln2-m^2/2-m^4/12],\quad
F_4+TS_{{\rm int},4}=H_N.
\tag{M12}
\]

M12 เป็น conditional thermal split ของ polynomial approximation ไม่ใช่ entropy exact finite-N การทิ้ง −θln2 ไม่เปลี่ยน state gradient แต่ทำให้ entropy reference ลดลง Nk_Bln2 ส่วนการตรึง a_C,b_C ที่ T จุดเดียวก่อน differentiate ไม่ใช่ thermal family นี้แล้ว

**ข้อจำกัดสำคัญ:** Core มี coefficients อิสระ; ตัวอย่างนี้ให้ subset ที่ต้องมี b_C s_C⁴=θ/3 และ a_C s_C²=θ−j_0 ไม่ได้ derive ค่าทุกชุดของ Core, spatial gradients, kinetics หรือ entropy ของ physical Φ การจับคู่ที่ T เดียวอาจทำได้เมื่อเลือก scales แต่การจับคู่ข้าม T ต้องเคารพเงื่อนไขเพิ่มดังกล่าว

### 4.5 Partition integrability ไม่ต้องอาศัย numerical sweep

สำหรับ |m|≤1 ตั้ง A=(γ/b_Φ)^(1/3)≥0 จะมี exact certificate

\[
t^4-4A^3t+3A^4=(t-A)^2(t^2+2At+3A^2)\ge0,\quad t=|\Phi|.
\]

จึงได้ H_N/E_*≥N[b_ΦΦ⁴/8−j_0/2−3γ^(4/3)/(8b_Φ^(1/3))]+P²/(2Nm_Φ) มี quartic/Gaussian tails และจำนวน binary configurations จำกัด จึง Z_N จำกัดสำหรับ domain ที่ล็อก ไม่ใช้ผลนี้อ้าง uniqueness, mixing, finite-time dynamics หรือหลักฐานของวัสดุ

## 5. M3 — Signed/magnitude, comparator และคำวินิจฉัย

### 5.1 สองการกระทำที่ต้องแยก

**Readout-only:** เก็บ signed k/C เดิมแล้วรายงาน |C| ค่า H,F และ microstates ไม่เปลี่ยนเพราะเราเปลี่ยนเพียงฟังก์ชันที่ถาม ไม่ได้เพิ่ม detector/coupling หรือ source backaction จริง

**State folding:** เปลี่ยน retained classes ให้เป็น magnitude a=|2k−N| รวม k กับ N−k ที่ a>0 ส่วน a=0 (เฉพาะ N คู่) มี class เดียว:

\[
G_N^{\rm fold}(a)=\sum_{k:|2k-N|=a}\binom Nk.
\tag{M13}
\]

พลังงานสองเครื่องหมายเท่ากันใน M1 จึง G_fold=2G_k เมื่อ a>0 และ G_fold=G_(N/2) เมื่อ a=0 ได้ F_fold=H−k_BT lnG_fold: intrinsic entropy เพิ่ม k_Bln2 สำหรับ nonzero magnitude ใน conditional equilibrium ขณะที่ retained sign entropy ที่ย้ายออกลดลงชดเชยกัน full entropy/partition sum เดิมไม่เปลี่ยน

ตัวอย่าง N=4 มี folded multiplicities สำหรับ a=0,2,4 คือ 6,8,2 รวม16 ไม่ใช่ 12,8,2 สำหรับ distribution นอก equilibrium ต้องใช้ sign-conditional entropy จริง ไม่สรุปว่าต้องเป็น ln2 เสมอ การพับนี้ไม่ผกผันและไม่ได้ระบุว่าเครื่องหมายคือ charge, antimatter หรือ imaginary

### 5.2 Comparator และ information

ที่ γ=0 energy แยก spin กับ Φ/P และ canonical measure เป็น product จึง equilibrium distribution factorize ไม่อนุมาน initial correlations ของ distribution ใด ๆ ให้หายทันที ที่ γ≠0 dependence อาจเกิดผ่าน m² แต่เป็น static coupling ไม่ใช่หลักฐานการเรียนรู้หรือ causal information-flow law

Entropy ใน M3/M5 กับ mutual information ระหว่างระบบย่อยเป็นคนละ functional ไม่ใช้ covariance แทน information หรืออ้างว่า C,Φ,Π,σ/R เป็น entropy ทั้งหมด ผลเดิมเรื่อง odd Π, equilibrium currents, sigma และ information flow ใน §30 คงเดิม ไม่รันหรือย้ายสูตรมาใช้กับ dynamics ที่รอบนี้ยังไม่ได้กำหนด

### 5.3 แยกผลตามฐานหลักฐาน

| ประเด็น | ผลที่รองรับ | ขอบเขตที่ยังไม่รองรับ |
| --- | --- | --- |
| Counting และ F/U/S | Exact conditional result จาก M1 กับ fixed measure; M2–M6 | ไม่เป็น microscopic derivation ของวัสดุ/ทุก Core family |
| Ω correspondence | Exact finite-grid f_N; controlled large-N/small-m value bridge M9–M11 | ไม่ใช่ exact quartic บน R หรือ force/kinetic closure |
| Φ entropy | ไม่เพิ่ม hidden Φ sector ใน reference นี้; retained entropy แยกชัด | Physical intrinsic entropy ของ UET Φ ยัง UNKNOWN ไม่ถูกตั้งศูนย์ |
| พลังงาน/heat | U_cond ชัดและไม่เท่ากับ F; ensemble energy คือ ⟨H⟩ | ไม่มี trajectory heat, source work หรือ bath-elimination law ใหม่ |
| Signed/magnitude | Exact relabel/readout distinction และ lossy fold พร้อม accounting | ไม่เลือกแทนเจตนา information ทั้งทฤษฎีหรือ full observability |
| Novelty | Standard equilibrium construction; named comparator correspondence ตามเงื่อนไข | ไม่มี unique UET discriminator หรือ empirical validation |
| Author intent | รักษาระบบซ้อนระบบ/interaction/ผลคงอยู่เป็นเป้าหมายรวม | Static canonical reference ไม่พิสูจน์หรือปฏิเสธ cosmic openness, learning, persistence |

## 6. ชุดตรวจ การตรวจรับ และการส่งต่อ

### 6.1 ผลิตหลักฐานอย่างไร

ใช้ [producer ใหม่](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Joint_State_Measure_Construction.py) และ [regression tests](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_joint_state_measure_construction.py) สร้าง [artifact ย่อ](../topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_joint_state_measure_construction.json) ผ่าน contract/identity helper เดิม ไม่มี schema หรือระบบสถานะใหม่

ตัวตรวจใช้ exact symbolic residuals, finite enumeration ของ N=2,3,4,8 และ rational binomial certificates ไม่มี Monte Carlo, parameter sweep, quadrature หรือ fitted tolerance การพิสูจน์ทุก N/domain/integrability อยู่ในข้อความ M4/M9/M11 และ §4.5 ไม่ใช่ claim จากจำนวน tests

Negative controls ต้องตรวจพบ omitted/double multiplicity, wrong N in storage, missing/double Jacobian, wrong/double interaction, zero-class double counting และ noninvertible magnitude fold แต่ละกรณีคือการไม่ตรงกับ reference ที่ประกาศ ไม่ได้อ้างว่า energy law อื่นทุกแบบละเมิด thermodynamics

ความสดของ artifact ตรวจด้วย `--check` แบบอ่านอย่างเดียว การสร้างไฟล์ใช้ `--emit-report` อย่างชัดเจน มี contract hash และ source/code/config identities ไม่ใช้ artifact ใหม่ไป refresh ผลเก่า Generated payload ไม่ฝังรายงานหรือ manifest เก่าทั้งก้อน

### 6.2 ขอบเขต review และคำถามผู้เชี่ยวชาญ

การสร้างและ adversarial self-review ของ AI ไม่ใช่ independent specialist review และไม่ใช่ physical validation สถานะ review ของ contract ใหม่ไม่เปลี่ยน physics gates หรือสถานะ contract เก่า การตรวจรับรอบ M คือมี conditional derivation/counterexample ที่ตามตรวจได้ ไม่ต้องรอทั้งทฤษฎีถูกหรือผิด

ผู้ตรวจ statistical mechanics/mathematical physics ควรตรวจเฉพาะ: fixed-measure entropy derivative, counting/diagonal convention, finite-N bound และ validity ของ Ω correspondence โดยแยก static ensemble จาก assumed fast equilibration ส่วนผู้เขียนตรวจเพียงว่าภาพ retained/eliminated information นี้ยังอยู่ในเจตนาที่ต้องการหรือไม่ การเห็นด้วยยืนยันเจตนา ไม่ยืนยันฟิสิกส์

### 6.3 สิ่งที่ปิดได้และหนึ่ง prerequisite ถัดไป

**ปิดได้ในรอบนี้:** ตัวอย่างร่วมที่นิยามชัดให้ static F/U/S dictionary และ normalization; finite-N value error มี bound; Ω เดิมเป็น approximation ของ subset ของ comparator ไม่ใช่ identity ของทุกสัมประสิทธิ์

**ยังเปิด:** physical retained-state/energy/measure map, physical Φ entropy, thermal dependence ของวัสดุ, time-scale separation และ kinetics ไม่มีการแก้ช่องว่าง `intrinsic-entropy-correspondence` ใน physical HIST-F ให้เสร็จด้วยการตั้ง reference นี้

**หนึ่งโจทย์ถัดไปที่เสนอแต่ยังไม่เริ่ม:** มี correspondence ของ retained state/energy/measure ที่มีหลักฐานอิสระเพียงพอให้ reference นี้แทนระบบกายภาพใดจริงหรือไม่? หากยังไม่มี ให้ระบุ exact missing premise ก่อนเลือก dynamics ไม่เปิดวัสดุ/hidden sector/heat dataset เพียงเพื่อให้มีงานต่อ หากต้องการพลวัตต้องล็อกแผนใหม่เรื่อง rates/conditional equilibration และ comparator แยกต่างหาก

รอบนี้หยุดที่คำวินิจฉัยนี้ ไม่ติดต่อผู้เชี่ยวชาญ ไม่เปลี่ยน README/METHOD/Core/API/defaults/thresholds/physics gates ไม่ push/PR/merge/เผยแพร่ และไม่เปิดรอบถัดไปโดยอัตโนมัติ บันทึกการตรวจที่รันจริงและ scoped local commit ไว้ใน [Topic 13 UPDATE_LOG](../topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md) กับ [WORK_LEDGER](../../WORK_LEDGER/2026/2026-10-24.md)
