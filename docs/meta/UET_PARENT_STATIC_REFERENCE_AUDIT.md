# รอบ Q — จุดสมดุลและฐานสถิติของ parent เดิม

> ตรวจถึง 25 ตุลาคม 2026 — งาน FORMAL และ certified numerics; ไม่ใช่ physical validation

## สรุปสำหรับผู้เขียน

**parent เดิมมีจุดสมดุลที่เป็น minimum เฉพาะที่ซึ่งรับรองได้ อย่างน้อยใน
สปินสลับ `-+-+`/`+-+-` แต่ยังไม่ได้ reference ทางกายภาพหรือช่วงอุณหภูมิที่รับรองแล้ว**
จุดนี้เกิดจากแรงในพลังงานเดิม ไม่ได้เติมแรงพยุงหรือปรับพารามิเตอร์ให้ผ่าน
ช่องว่างอะตอมประมาณ `(0.702596, 0.623649, 0.702596) d_ref` ต่างจากการตั้ง
ทุกช่องว่างเท่ากับ `d_ref` แล้วสมมติว่าตรงนั้นเป็นสมดุล

เมื่อใช้พิกัดเดิม จะได้ `Φ* ≈ 0.328983`, `u1* = 0` ตาม symmetry และ
`u2*/d_ref ≈ -0.0353060` นี่คือการระบุตำแหน่งใหม่อย่างเปิดเผย
ไม่ใช่เปลี่ยนชื่อ `d_ref` หรือเปลี่ยนค่าการเชื่อมเพื่อทำให้จุดใหม่กลายเป็นศูนย์
ยังนับพลังงานของทั้งสามโหมดได้เหมือนเดิม และแยกได้ว่าถ้าเก็บ Φ ไว้
รายละเอียดที่รวมออกมีเพียงสองโหมด ไม่ใช่เอา entropy ทั้งสามโหมดมาบวก Φ อีกครั้ง

อีกด้านหนึ่ง สปินเหมือนกันทั้งหมดให้ root ที่รับรองแล้วแต่มีทิศความโค้งลบ
จึงไม่ใช่ minimum ส่วนอีกสี่ symmetry groups ไม่พบ candidate ในงบที่ประกาศ
**ไม่ได้พิสูจน์ว่าไม่มี minimum ที่อื่น** ผลลบของ P ที่ตำแหน่ง/ball เดิม
และผลไม่มี global equilibrium ของ parent ยังคงอยู่ การพบ local minimum
ไม่แก้ปัญหาการชนหรือการแยกออกไปไกล และไม่บอกว่าระบบคงอยู่ได้นานเท่าไร

สิ่งที่แคบลงจริงคือมี stationary reference หนึ่งกลุ่มให้ศึกษาต่อได้โดยไม่เดา
สิ่งที่ยังขาดคือความหมายกายภาพ/สเกลจริง การเลือก error budgets และเงื่อนไข
classical–local ที่อยู่ร่วมกัน รวมถึงการเตรียมระบบจริงและการคงอยู่ซึ่งไม่ได้ตรวจรอบนี้

## 1. Q0 — ฐานหลักฐานและ bounded research card

ฐาน local commit `316797ea3590bdc5cc80a9ea387c7db147c67ddf`;
สาขารอบนี้ `codex/research/parent-static-reference` สืบต่อจาก P ใน worktree เดิม
มีงานค้างก่อนเริ่ม 463 รายการ index ว่าง; ไม่รวมงานเก่าเข้า scoped commit
remote-tracking `origin/main` ที่อ่านได้ในเครื่องคือ
`6da62c33f6e61311990f4588b44c7737f089710e` แต่ไม่ได้ fetch หรือยืนยัน public main สด
รายงาน/ผลใหม่จึงเป็น local working evidence ไม่ใช่ public release

| รายการ | ขอบเขต/ตัวควบคุม |
| --- | --- |
| Proposition | parent เดิมมี strict local minimum ที่รับรองได้หรือไม่ และรอบนั้นมี static harmonic dictionary ภายใต้เงื่อนไขใด |
| มีแล้ว | [O](UET_LATTICE_MECHANICAL_STATE_CONSTRUCTION.md): พิกัด/measure/inertia และ collision no-go; [P](UET_LATTICE_BATH_REDUCTION_AUDIT.md): reference เดิมไม่ผ่าน localization แต่ formal bath reduction ใช้ได้ตามสมมติฐาน |
| Identity ก่อนเริ่ม | P20/O14/N13/M11/thermal8 ตรงทั้งหมด โดยอ่าน helper เท่านั้น ไม่รัน scientific producers เก่า |
| ขาด/โต้แย้ง | reference ที่แรงทุก internal coordinate เป็นศูนย์จริง, local curvature/remainder และ static/classical preparation conditions |
| Controller | P contract component `physical-parent-preparation`; ผล Q ไม่แก้ contract/artifact ของ P ย้อนหลัง |
| Next action / why | ค้น candidate ใน gap coordinates แล้วพิสูจน์ root/curvature ด้วย rational enclosure เพื่อแยก stationary reference จากการย้ายศูนย์ตามใจ |
| Outcomes | certified minimum / certified nonminimum / unresolved / ไม่พบ candidate ในงบ; ทุกแบบเป็นผลได้ |
| Stop | หนึ่ง minimum witness ต่อ symmetry orbit หรือใช้งบ seeds/รับรองครบ; ไม่ขยาย box/seed/parameter อัตโนมัติ |
| Reviewer | numerical verification + statistical mechanics: ตรวจ inclusion, coordinate metric และขอบเขต local ensemble; ยังไม่ติดต่อภายนอก |
| Non-goals | ไม่มี lifetime/escape/trajectory, spin rates, material calibration, wall/cutoff, experiment, Core/README/gate change |

ผู้เขียนอนุมัติ numerical search ตามด้วย certificate และเลือกปิดสถิติก่อน
Hamiltonian เป็น comparator เดิมของ O/P; symmetry reduction, search policy,
local certificate และ conditional preparation เป็นการสร้างโดย AI ที่ต้องตรวจได้
ไม่ใช่คำพูดต้นฉบับหรือผลเฉพาะ UET จากการยอมรับร่วมกัน

System partition: frozen spin labels + สาม internal canonical pairs หลังตัด CM
ส่วน gaps, C, Φ, Π และ endpoint เป็น views ของ state เดียวกัน ไม่มี detector,
signal-transport หรือ physical backaction claim และไม่มี bath ใหม่เพิ่มในรอบนี้

<a id="parent-and-coordinates"></a>
## 2. Q1 — Parent เดิม พิกัด และแรงที่ต้องเป็นศูนย์

ใช้หน่วย `J_ref,d_ref` และ `ℓ_i = (x_{i+1}-x_i)/d_ref` ในสมการต่อไปนี้
โดยไม่เปลี่ยนค่าคงที่เมื่อเลื่อนจุดอ้างอิง:

\[
v_s(\ell)=\frac{V_s}{J_{\rm ref}}=
\sum_{i<j}\{8[1-e^{-L(r_{ij}-1)}]^2
-8[1-2^{-(j-i-1)}]^2\}
-\frac14\sum_{i=1}^3\frac{s_is_{i+1}}{\ell_i^2},
\quad r_{ij}=\sum_{a=i}^{j-1}\ell_a,\quad L=\ln2.
\tag{Q1}
\]

มี elastic pairs หกคู่และ magnetic bonds สามเส้น ไม่มี periodic closing bond
ตัวประกอบ `1/4` สืบจาก `S_i=s_i/2` ของต้นฉบับ
[Balcerzak–Szałowski–Jaščur v2, II.A–D, Eqs.1,3–5,18–20](https://arxiv.org/pdf/2003.12054)
ต้นฉบับหา minimum ของ Gibbs potential ที่รวม ensemble/vibrations/แรงภายนอก
ส่วนนี้เป็น finite frozen-spin comparator ของ O ไม่ใช่ EOS นั้นหรือ reproduction
ของ infinite chain และ control `δ=ln2` ก็ไม่ใช่การสอบเทียบวัสดุของบทความ

สำหรับ pair ที่ `η=s_i s_j` เมื่อเป็น NN และ `η=0` เมื่อไม่ใช่ NN ให้
`e=exp[-L(r-1)]`; อนุพันธ์จากพลังงานชุดเดียวกันคือ

\[
w'=16L(e-e^2)+\frac{\eta}{2r^3},\quad
w''=16L^2(2e^2-e)-\frac{3\eta}{2r^4},\quad
w'''=16L^3(e-4e^2)+\frac{6\eta}{r^5}.
\tag{Q2}
\]

gradient และ Hessian บน gaps เกิดจากบวก `w' t_ij` และ `w'' t_ij t_ij^T`
โดย `t_ij` มีค่า1บน bonds ที่คั่น pair นั้น การ differentiate Q1 อิสระ
ในตัวตรวจให้ผลตรงกับ Q2 ไม่อาศัย residual ของ producer เก่า

### พิกัดไม่ได้กำหนดมวลตามชื่อ

หลังตัด CM เขียน `x/d_ref=Tℓ` และ `D x/d_ref=ℓ`:

\[
T=\frac14\begin{pmatrix}-3&-2&-1\\1&-2&-1\\1&2&-1\\1&2&3\end{pmatrix},
\quad DT=I,\quad \mathbf1^TT=0,\quad
G=T^TT=(DD^T)^{-1},\quad\det G=\frac14.
\tag{Q3}
\]

เมื่อกลับไปใช้ dimensional gaps `l=d_ref ℓ`, canonical momentum คือ
`p_l=T^T p_x` และ kinetic energy เป็น `p_l^T G^{-1}p_l/(2μ)` ไม่ใช่
`p_l^Tp_l/(2μ)` position Jacobian `sqrt(det G)=1/2` ยกเลิกกับ momentum
Jacobian2 เมื่อใช้คู่ canonical ครบ ไม่เติม factorนั้นซ้ำใน partition
หากใช้ dimensionless ℓ ต้องใช้ conjugate momentum `p_ℓ=d_ref p_l` อีกชั้น

ในพิกัด length เดิม `q=(Q,u1,u2)` มี `x=d_ref a+Bq`,
`B=(-a/sqrt5,E)` และ `q/d_ref=B^T(Tℓ-a)` ดังนั้น

\[
\nabla_q V=\frac{J_{\rm ref}}{d_{\rm ref}}(DB)^T\nabla_\ell v,
\quad\det(DB)^2=4\ne0.
\tag{Q4}
\]

จึง `∇ℓv=0` เทียบเท่ากับแรง internal ทั้งสามเป็นศูนย์ และแรงอะตอมทั้งสี่
เป็นศูนย์ด้วย translation invariance ไม่ใช่ตรวจเพียงแรง conjugate ต่อ Φ
atomic Hessian มี translation zero mode ที่ต้องตัดก่อนตรวจความเป็นบวก

canonical measure ยังคง `d³q d³p/h³` เมื่อ condition CM pair ออก
ไม่มีการ integrate zero mode หรืออ้างว่า CM entropy เป็นศูนย์
สำหรับ Φ ไร้มิติ `λ=sqrt5 d_ref`, `p_Φ=λp_Q`,
`M_Φ^phys=μλ²=5μd_ref²` มีหน่วย kg·m² และ normalized inertia `5/4`
ภายใต้ `E*=J_ref,t*=d_ref sqrt(μ/J_ref)` ตาม O/P ไม่ derive mobility/damping

readout เดิมยังเป็น

\[
\Phi=1-\frac{a^Tx}{5d_{\rm ref}},\qquad
L_{\rm end}=3d_{\rm ref}(1-\Phi)-u_2/\sqrt5.
\tag{Q5}
\]

ระยะปลายถึงปลายไม่ใช่ Φ เพียงอย่างเดียว และ C ยังคง population contrast
ของ frozen spins ไม่กลายเป็นมวล entropy หรือ information ทุกความหมาย

<a id="root-certificates"></a>
## 3. นโยบายค้น และ certificate ที่ใช้ตัดสิน

### 3.1 Candidate search ไม่ใช่ proof

ค้น `ℓ∈[1/4,4]^3` ด้วย seeds `{1/2,1,2}³` เรียง lexicographic ไม่มี random
ใช้ mpmath1.3.0 ที่80digits, Newtonไม่เกิน100stepsและ20backtracks/step
ยอมรับ step เมื่ออยู่ใน box และ gradient infinity norm ลดด้วย factor
`1-α/10000`, `α=2^{-b}`, `b=0..19` เป้าหมาย residual `1e-40`
เป็น numerical stopping target เท่านั้น ไม่ใช่ physical accuracy threshold

แม้ตัวค้นรายงาน success ก็ยังไม่ได้พิสูจน์ root; ข้อจำกัดนี้สอดคล้องกับ
[mpmath1.3.0, optimization.py, findroot docstring](https://github.com/mpmath/mpmath/blob/1.3.0/mpmath/calculus/optimization.py)
ซึ่งแยก residual check ออกจาก root guarantee โดยเฉพาะ interval findroot
เราใช้ safeguarded Newton ของเส้นทางนี้ ไม่ได้เรียก `iv.findroot` เป็น certificate

global flip คงทุก `s_i s_{i+1}`; reflection กลับลำดับ bond products และ gaps
พร้อมกัน ชุด pair distancesทั้งหกคงเดิม จึงลด16configurationsเป็น6orbits
ได้ก่อนค้น ไม่ใช่รวมกลุ่มจากผลตัวเลข ส่วน root ของ reflected sector
มี gaps กลับลำดับ, Φและu2คงเดิม, u1กลับเครื่องหมาย และ inertiaคงเดิม

### 3.2 Rational enclosure และความหมายของ uniqueness

ใช้ `Fraction` endpoints และ arithmetic ปิด outward บน rational grid `10^{-170}`
ทุก operation: lowerปัดลง upperปัดขึ้น เพื่อลด denominator growth โดยไม่หด enclosure
serializeเป็น rational strings ไม่ใช่ decimalที่ปัดเข้าด้านใน
`ln2=2Σ_{n=0}^{m-1}1/[(2n+1)3^{2n+1}]+remainder` โดย

\[
0<r_m\le\frac{2}{(2m+1)3^{2m+1}(1-1/9)}.
\tag{Q6}
\]

primaryใช้m64; fallback96 ส่วน exponential ใช้positive Taylorของ`exp(|x|/32)`
ลำดับ48/64 พร้อม tailจากratio bound `y/(n+2)` เมื่อ`y=|x|/32<1`
แล้วยกกำลัง32 และใช้reciprocalสำหรับ xลบ ปลายของ intervalอาศัยmonotonicity
square rootsในcoordinate mapใช้integer-square-rootและoutward rational endpoints

ตั้ง rational center c จาก candidate; primary halfwidth `r=1e-12`
ถ้ายังรับรองไม่ได้ อนุญาต160digitsและr`1e-16`อีกครั้งเดียวต่อcandidate
ให้ `H(X)` ครอบ Hessian ใน `c+[-r,r]^3`, Rเป็นrational preconditioner
ที่ตรวจ nonsingularity แบบexact และ

\[
E=I-RH(X),\quad Z=-R\nabla v(c),\quad
\|E\|_\infty<1,\quad Z+E[-r,r]^3\subset\operatorname{int}[-r,r]^3.
\tag{Q7}
\]

การหดตัว/self-mapจึงให้rootที่uniqueในboxนั้น และrootอยู่ใน `c+Z+E[-r,r]^3`
ดู [Rump2010, corrected author copy, Theorem13.3/Eq.13.8, printed p89](https://www.tuhh.de/ti3/rump/intlab/ActaNumerica2010.pdf)
ไม่ใช่ uniquenessทั้งsearchboxหรือทั้งparent ความล้มเหลวของcertificate
ก็ไม่ใช่ nonexistence proof Hessianใช้interval LDL; ถ้า pivotคร่อมศูนย์
ยังตัดสินไม่ได้ ถ้ามีrational directionที่ quadratic form upper boundเป็นลบ
จึงใช้ตัดสินว่าrootนั้นไม่ใช่minimum

## 4. Q1 — ผลค้นครบทุก configuration

| Representative / members | สิ่งที่พบในงบเดิม | คำวินิจฉัย |
| --- | --- | --- |
| `----`, `++++` | 8seedsจบที่certified rootsซึ่งมีnegative-curvature witness; 19seedsใช้backtracksครบ | มีrootที่ไม่ใช่minimum; ยังไม่ใช่no-minimum theorem |
| `---+`, `+---`, `-+++`, `+++-` | ทั้ง27seedsใช้backtracksครบ ไม่ได้candidate | bounded inconclusive |
| `--+-`, `-+--`, `+-++`, `++-+` | ทั้ง27seedsใช้backtracksครบ ไม่ได้candidate | bounded inconclusive |
| `--++`, `++--` | ทั้ง27seedsใช้backtracksครบ ไม่ได้candidate | bounded inconclusive |
| `-+-+`, `+-+-` | seedแรก `(1/2,1/2,1/2)` ให้rootพร้อมinclusionและSPD | certified strict local minimum |
| `-++-`, `+--+` | ทั้ง27seedsใช้backtracksครบ ไม่ได้candidate | bounded inconclusive |

สรุปเป็น136candidate attemptsตามstop policy ไม่ได้ใช้fallbackเพื่อปรับผล
ไม่ค้นstationary pointsให้ครบ และไม่เปิดseedหรือboxใหม่ ผลรายconfiguration
และattemptsที่ตัดสินได้เก็บใน
[artifact](../topics/0.13_Thermodynamic_Bridge/Result/artifacts/t13_parent_static_reference_audit.json)
การนับนี้บอกcoverageของงาน ไม่ใช่คะแนนความถูกต้องของUET

ตัวอย่าง nonminimum witness ของ `----` อยู่ประมาณ
`(0.487400101733465,0.529227934195840,0.487400101733465)`
และทิศ gap `(-1,1,-1)` มี quadratic form ของ Hessian เป็นลบทั้ง enclosure
จึงปฏิเสธการใช้ **root นี้** เป็น stable reference ได้จริง ไม่ใช่แค่ solver ไม่ลู่เข้า
แปด seed outcomes ไม่ได้หมายถึง root ต่างกันแปดจุด

สำหรับminimumที่รับรอง ค่าทศนิยมต่อไปนี้เพื่ออ่านเท่านั้น;
หลักฐานเป็นrational endpoints/inclusionในartifact:

| ปริมาณ | ค่าอ่านง่ายและขอบเขต |
| --- | --- |
| gaps/d_ref | `(0.7025956690271465,0.6236490105233948,0.7025956690271465)` |
| Φ* | `≈0.3289829943743541` |
| u1*/d_ref | 0 จากreflectionและuniqueness; enclosureยังมีwidth |
| u2*/d_ref | `≈-0.03530601900217015` |
| endpoint/d_ref | `≈2.028840348577688` |
| V*/J_ref | `≈-2.5597570055589323` โดยรักษาพลังงานอ้างอิงเดิม |
| Krawczyk contraction upper | น้อยกว่า `1.201×10^-11` |
| root-position uncertainty ในq/d_ref | ไม่เกิน `3.003×10^-23` จากimage enclosure ไม่ตั้งเป็นศูนย์ |
| eigenvalue boundsของinternal stiffnessที่root | `18.189 < κ_min` และ `κ_max <82.375` แบบsufficient enclosure |
| det(internal stiffness dimensionless) | `≈70653.3480599961` มีintervalไม่ใช่ค่าคงที่exactจากdecimal |

full internal stiffness ในลำดับ `(Q,u1,u2)` อ่านโดยประมาณเป็น

\[
\bar A_*\approx
\begin{pmatrix}
18.84483308&0&-2.52739738\\
0&47.15541542&0\\
-2.52739738&0&79.84660746
\end{pmatrix}.
\tag{Q7a}
\]

off-diagonal Q–u2 ไม่เป็นศูนย์ การมี minimum จึงยังไม่ทำให้ Φ เป็น closed mode
และไม่ derive Core kinetics จาก inertia เพียงอย่างเดียว ตัวเลขศูนย์อาศัย
reflection symmetry; interval entries ใน artifact ยังครอบความคลาดเคลื่อน

จุดนี้มีcompressionจากระยะอ้างอิงเดิมประมาณ0.329 จึงไม่ยกคำว่าsmall strain
ของsourceมาใช้รับรองวัสดุเดิม การเลื่อนเป็นδΦ=Φ−Φ*เป็นcoordinate change
เท่านั้น หากตั้งd_refใหม่โดยไม่แปลงexchangeจะเปลี่ยนparent ไม่ใช่rewrite

## 5. Q2 — บริเวณlocalรอบrootจริง

ใช้ballในorthonormal internal length coordinatesรอบrootจริง
`||q−q*||≤d_ref R` ไม่ใช่ballของPรอบศูนย์เดิม
rootboxถูกส่งเข้าgap boundsก่อนเสมอ; pair distanceเปลี่ยนไม่เกิน
`sqrt2 R <3R/2` การใช้componentwise gap boxเป็นouter enclosureจึงอาจหยาบ
แต่ไม่ละroot uncertainty

ตรวจradiiที่ล็อก `R_j=1/(4·2^j)`, j0..8 ทุกค่า ใช้interval LDL
และinverse norm boundสำหรับuniform curvature ไม่ใช้float eigenvaluesเป็นproof
จาก `min eigen(DD^T)=2−sqrt2>1/2`, `max eigen(DD^T)<4`
จึงย้ายgap-curvature boundไปinternal qโดยไม่ใช้mass metricผิด
ให้ m≤min eigen(A_q) และ M≥max eigen(A_q) บนdomain
ส่วนthird-derivative tensorมีbound

\[
\|D^3v\|\le2\sqrt2\sum_{i<j}|w'''_{ij}|<3\sum_{i<j}|w'''_{ij}|=:M_3,
\quad |v-v_*-\tfrac12y^TA_*y|\le\Delta=\frac{M_3R^3}{6},
\quad v-v_*\ge\frac m2\|y\|^2.
\tag{Q8}
\]

| j / R | uniform certificate | m lower (อ่านโดยประมาณ) | Δ upper (อ่านโดยประมาณ) |
| --- | --- | --- | --- |
| 0 / 1/4 | ยังรับรองไม่ได้: interval curvature | — | — |
| 1 / 1/8 | ยังรับรองไม่ได้: interval curvature | — | — |
| 2 / 1/16 | ยังรับรองไม่ได้: interval curvature | — | — |
| 3 / 1/32 | รับรองได้ เป็นรัศมีใหญ่สุดในgridนี้ | 4.6361597 | 0.0046906873 |
| 4 / 1/64 | รับรองได้ | 7.3909436 | 0.0005108875 |
| 5 / 1/128 | รับรองได้ | 8.7958853 | 0.0000597777 |
| 6 / 1/256 | รับรองได้ | 9.5063442 | 0.0000072340 |
| 7 / 1/512 | รับรองได้ | 9.8637217 | 0.0000008899 |
| 8 / 1/1024 | รับรองได้ | 10.0429672 | 0.0000001104 |

ที่R1/32 boundที่ปัดออกอย่างปลอดภัยคือm>4.636, M<225.284,
M3<922.227 และระยะNNยัง>0.576774 d_ref พลังงานขึ้นถึงขอบอย่างน้อย
`0.0022637 J_ref` นี่เป็น**local energy rise บนsphereนี้** ไม่ใช่global escape
barrierหรือfull basin ระดับcertificateไม่ผ่านที่รัศมีใหญ่กว่าอาจเกิดจาก
outer enclosureหยาบ ไม่ได้พิสูจน์ว่าparentไม่เสถียรที่ทุกจุดในballนั้น

ถ้าใช้rational centerแทนrootจริง ต้องเก็บforce intervalที่centerและ
location uncertaintyไว้ Q8เขียนรอบrootที่มีอยู่จริง ไม่ได้ลบgradientที่center
เพื่อประกาศว่าเป็นศูนย์ Stiffness/covariance/determinantในartifactครอบrootbox
รวมแล้ว การเปลี่ยนพิกัดไม่เปลี่ยนbare inertiaของO/P

<a id="static-dictionary"></a>
## 6. Q3 — Static thermal dictionaryจากenergyและmeasureเดียวกัน

### 6.1 Jointสามโหมด

ให้ `Ā=(d_ref²/J_ref) Hessian_q V(q*)`, `v*=V*/J_ref`,
`θ=k_BT/J_ref`, `χ=ℏ/(J_ref t*)`, `h=2πℏ`
Hamiltonian quadraticมีสามcanonical pairsและCMถูกconditionออก:

\[
Z_{\rm H,3}=e^{-v_*/\theta}\frac{\theta^3}{\chi^3\sqrt{\det\bar A}},\quad
\frac{F_{\rm H,3}}{J_{\rm ref}}=v_*-\theta\ln\frac{\theta^3}{\chi^3\sqrt{\det\bar A}},
\quad\frac{U_{\rm H,3}}{J_{\rm ref}}=v_*+3\theta,
\quad\frac{S_{\rm H,3}}{k_B}=3+\ln\frac{\theta^3}{\chi^3\sqrt{\det\bar A}}.
\tag{Q9}
\]

covarianceบน`q/d_ref`คือ`θĀ^{-1}` และmomentumคือ`μk_BT I`
F=U−TSและthermal derivativesใช้coefficients/measureเดิมซึ่งคงต่อT
ไม่ได้เติมintrinsic entropyของΦจริงให้เป็นศูนย์
พลังงานV*ต่างsectorต้องเก็บไว้ แม้ไม่เปลี่ยนแรงก็ตาม
frozen labelsไม่มีdynamical lawมาบอกว่าจะให้น้ำหนักsectorอย่างไร
ถ้าจะใช้mixtureต้องประกาศpreparation weights ไม่เปลี่ยนเป็นannealed Gibbsโดยเงียบ

### 6.2 Fixed-Φรวมออกสองโหมด

แบ่งĀเป็น`(a,g^T;g,K)`; ตั้ง`z=δQ/d_ref`, `w=δu/d_ref`
ที่retained Q,pQคงที่:

\[
\bar u(z)=-K^{-1}gz,\quad k_{\rm stat}=a-g^TK^{-1}g>0,\quad
v_{\rm eff}(z)=v_*+\tfrac12 k_{\rm stat}z^2,
\quad Z_{\rm H,2}(z)=e^{-v_{\rm eff}/\theta}
\frac{\theta^2}{\chi^2\sqrt{\det K}}.
\tag{Q10}
\]

จึงUhidden/J_ref=`v_eff+2θ` และShidden/k_B=`2+ln[θ²/(χ²sqrt(detK))]`
ถ้ารวมretained kineticก็ใส่`pQ²/(2μ)`ครั้งเดียวในFและU
การintegrateคู่Q,pQเพิ่มจากQ10คืนQ9 เป็นpartition factorizationจากGaussian
completion ไม่ใช่spin/vibration factorizationหรือindependent Φ substance
การเปลี่ยน`Q,pQ`เป็น`Φ,pΦ`มีJacobianรวม1; ถ้าแทนpΦด้วยΠต้องใส่
`dpΦ=(MΦ^phys/t*) dΠ` ไม่เปลี่ยนเป็นflat measureชุดใหม่

Q10ตรงกับโครงสร้างconditional GaussianของOเมื่อใช้quadraticreferenceใหม่นี้
แต่ไม่เท่ากับK_s(Φ),shift,entropyหรือentropic forceทั้งหมดของparentในO
ที่มีhigher derivatives/arrangement dependence ถ้าใช้fixedΦ local domain
ต้องมี`z²+(||ubar(z)||+r_u)²≤R²`ก่อนใช้hidden ballradiusr_u
และใช้สองโหมดในtail/thermal bound ไม่เอาjoint entropyมานับซ้ำ

### 6.3 Local-parent integralไม่ใช่globalpartition

ให้`Z_loc`เป็นparent integralเฉพาะballรอบrootจริงและcanonical momentaเต็ม
นี่เป็นconditional static construction ไม่เติมกำแพงและไม่แก้energy law
หากquadratic GaussianมีprobabilityนอกballηและQ8ให้Δ จะได้

\[
e^{-\Delta/\theta}(1-\eta)Z_{\rm H,3}\le Z_{\rm loc}
\le e^{\Delta/\theta}(1-\eta)Z_{\rm H,3},\quad
\frac{|F_{\rm loc}-F_{\rm H,3}|}{J_{\rm ref}}
\le\Delta-\theta\ln(1-\eta_b),\quad\eta\le\eta_b<1.
\tag{Q11}
\]

แยกpotential errorΔออกจากtruncated probabilityη ไม่ถือว่าการมีGaussianที่
normalizeได้แปลว่าparent normalizeทั้งdomainได้ ตัวparentเมื่อทุกgap≥L≥1
มี`v≤79/2+3/(4L²)`ในoctantไม่จำกัดปริมาตร จึงglobalcanonicalpartition
divergeจากdissociationได้ทุกsectorด้วย ผลcollision no-goของOสำหรับ
attractive sectorยังอยู่ ไม่ใช้localminimumลบglobalข้อจำกัดทั้งสองชนิด

สำหรับUและS ห้ามderiveerrorจากFboundที่Tเดียวโดยไม่มีการควบคุมเพิ่ม
ในballใช้density ratioของparentต่อconditioned harmonicอยู่ใน
`[exp(-2Δ/θ),exp(2Δ/θ)]`, harmonic potential≤`MR²/2`
และGaussian potentialmoment `E[X]=3θ/2`, `E[X²]=15θ²/4`
ดังนั้น sufficientboundแยกได้เป็น

\[
\frac{|U_{\rm loc}-U_{\rm H,3}|}{J_{\rm ref}}
\le\Delta+(e^{2\Delta/\theta}-1)\frac{MR^2}{2}
+\frac{\theta(\sqrt{15}\sqrt{\eta_b}+3\eta_b)}{2(1-\eta_b)},
\quad |S_{\rm loc}-S_{\rm H,3}|/k_B\le (\delta_U+\delta_F)/\theta.
\tag{Q12}
\]

kinetic distributionเหมือนกันจึงหักล้างในdifferenceนี้ แต่entropyของmomentum
ยังอยู่ในQ9/10 ขอบเขตdomainคงต่อT; ถ้าเลื่อนdomain/coefficientsตามT
ต้องรวมderivativesเพิ่มเติม ไม่ใช้Q9อนุมานthermal dictionaryใหม่อัตโนมัติ

mechanicalminimumไม่ใช่finite-Tmean: harmonicmeanตรงrootเพราะGaussian
สมมาตร ส่วนparentanharmonicmeanอาจเลื่อน แม้conditionในballสมมาตร
ได้bound`||E_loc[q]−q*||/d_ref≤R(exp(2Δ/θ)−1)`
จึงยังไม่ได้thermal expansioncoefficientหรือequilibriumEOSของวัสดุจริง

### 6.4 เงื่อนไขlocalและclassicalต้องอยู่ร่วมกัน

ให้εloc,εval,εqเป็นerrorbudgetsที่ผู้ใช้ปลายทางต้องประกาศก่อน ไม่เลือกในรอบนี้
covariance≤`θ/m I` ทำให้`||y||²≤(θ/m)χ³²`ในcouplingของstandardnormal
ChernoffจากMGF `(1−2t)^(-3/2)` ให้สำหรับu>0

\[
P[\chi_3^2\ge B(u)]\le e^{-u},\quad
B(u)=3+2\sqrt{3u}+2u.
\tag{Q13}
\]

พิสูจน์ใช้`−ln(1−2t)−2t≤2t²/(1−2t)`สำหรับ0<t<1/2แล้วoptimize
จึงsufficientlocalizationconditionคือ`θ≤mR²/B(ln(1/εloc))`
และuniformvaluecondition`Δ/θ≤εval`ให้lowerbound`θ≥Δ/εval`
ลดTจึงไม่ได้ทำให้errorสองชนิดผ่านพร้อมกันอัตโนมัติ โดยเฉพาะuniformΔbound
ที่อาจหยาบเมื่อเทียบกับthermalwidth

สำหรับisolatedquadraticreferenceนี้มีเพียงสามnormalfrequencies
`ω_j t*=sqrt(κ_j)`; quantum/classicalcovarianceratioคือ`x_j coth x_j`
เมื่อ`x_j=χsqrt(κ_j)/(2θ)` ใช้boundเดิมในPว่า
`0≤x coth x−1≤x²/3` ได้

\[
\theta\ge\chi\sqrt{\frac{\kappa_{\max}}{12\epsilon_q}},\qquad
\max\!\left(\frac{\Delta}{\epsilon_{\rm val}},
\chi\sqrt{\frac{\kappa_{\max}}{12\epsilon_q}}\right)
\le\theta\le\frac{mR^2}{B(\ln(1/\epsilon_{\rm loc}))}.
\tag{Q14}
\]

Q14เป็นsufficientwindow ไม่ใช่necessaryconditionหรืออุณหภูมิที่fitไว้
มีnonemptywindowเฉพาะเมื่อlower≤upperสำหรับχและbudgetsที่ระบุ
ถ้าไม่ผ่านก็ยังไม่ใช่proofว่าไม่มีbetterharmonicapproximation
สำหรับfreeenergyquantumcorrectionของquadraticสามโหมดเอง
`Σ ln(sinh x_j/x_j)≤Σx_j²/6≤χ²·3κmax/(24θ²)`ตามintegralของcothbound
ต้องมีbudgetของobservableนั้นแยก ไม่ใช้covariancebudgetรับรองF,U,Sทุกอย่าง

รอบนี้ไม่มีbathใหม่ จึงไม่แทนDrudeเป็นhardcutoffหรือใช้finiteสามโหมด
รับรองbathhigh-frequencytail ถ้าจะต่อbathต้องใช้response-weightedtail/
preparationconditionsของPตามขอบเขตเดิมเพิ่มเติม Q14ยังไม่มีχจากวัสดุ,
errorpolicyหรือacceptedthermalwindowจริง; largestgeometricradiusไม่เท่ากับ
largestthermalaccuracydomain และไม่ได้เลือกTเพื่อสร้างผลผ่าน

### 6.5 Conditional preparationไม่ใช่สิ่งที่ทำสำเร็จในห้องทดลอง

ชุดที่นิยามได้ตอนนี้คือ frozenสปินสลับ, พิกัดรอบrootในenclosureที่ประกาศ,
canonicalmomentumlawและlocalconditioningบนball, oldΦ/u/endpointreadout
โดยระบุว่าจะใช้joint3หรือfixedΦhidden2ensemble
การconditionไม่ได้เพิ่มreflectivewall ไม่แปลว่าensembleนั้นinvariantตาม
parent/bathdynamics และไม่พิสูจน์spinfreezingหรือequilibrationจริง
ไม่คำนวณescapeprobability, relaxation, durationหรือlifetimeในรอบQ

## 7. Q4 — Verdict, ความสัมพันธ์กับUET และขอบเขตที่ยังเปิด

| สะพาน/ข้ออ้าง | ผลที่มีจริง | สิ่งที่ยังเปิด |
| --- | --- | --- |
| parentเดิม→stationaryreference | certifiedminimumของAFalternatingหนึ่งorbit; ferromagneticrootsที่พบไม่ใช่minimum | ไม่ได้ค้นminimumทั้งหมด; อีก4orbitsboundedinconclusive |
| gap→atomic/internalforce | exactcoordinate/chain-rulemapหลังตัดCM | ไม่มีrealapparatus/measurementmap |
| bareΠstorage | inertiaเดิมคงอยู่ที่rootใหม่ | ไม่กำหนดdamping,mobility,τหรือCorekinetics |
| parentlocal→quadratic | sufficientuniformcurvatureที่gridradii1/32ถึง1/1024และvalue/tailboundsแยกกัน | acceptedT/χ/budgets,quantum/materialvalidity |
| jointthermal→fixedΦhidden | GaussianSchur/dictionaryภายใต้measureเดียวกันและmodecount3/2 | ไม่แทนfullΦ-dependententropyของOหรือข้อมูลทุกความหมาย |
| local→globalequilibrium | ใช้แทนกันไม่ได้; collision/dissociationข้อจำกัดยังอยู่ | ไม่มีconfinement/physicalpreparation/lifetimeในขอบเขตรอบนี้ |
| standardcomparator→UETnovelty | constructionนี้ใช้Morse/exchangeและstandardlocalstatmech | ไม่มีpredictionที่แยกUETจากcomparator |

information/learning/persistenceหรือจักรวาลเปิดของผู้เขียนไม่ถูกยืนยันหรือปฏิเสธ
จากminimumของโซ่นี้ เครื่องหมายCเป็นreadoutของpopulation; globalspinflip
ทำให้Cกลับเครื่องหมายแต่energyคงเดิม ส่วนmagnitudefoldingสูญเสียรายละเอียด
ไม่ใช่invertiblecoordinatechangeและไม่เพิ่มsourcebackaction
ไม่โยงเครื่องหมายกับimaginaryหรือantimatterโดยไม่มีcorrespondenceเพิ่ม

### คำถามตรวจเฉพาะสำหรับผู้เชี่ยวชาญ

Ω ของ Core/M ยังไม่ได้กลายเป็น free energy ของ parent นี้แบบ exact:
รอบ Q ได้เพียง local quadratic dictionary ของ frozen sector หนึ่งชุด
ไม่ได้ derive even quartic, C–Φ coupling ของ Core หรือการรวม arrangements
ทุกแบบให้เหลือ C ตัวเดียว เมื่อ C เท่ากันแต่ bond products ต่างกัน Q1 ยังต่างกัน
ต้องรักษาผล squared-sum/NN mismatch ของ N และ Φ-dependent entropy ของ O
พลังงาน V* ที่ติดลบเป็นพลังงานเทียบ common reference เดิม ไม่ใช่มวลลบ
หรือ information energy ชนิดใหม่

1. Numericalverification: ตรวจQ6/exp remainder/outward grid, Q7และLDL,
   root-locationpropagation และแยก localuniquenessออกจากrootcensusได้ถูกต้องหรือไม่?
2. Statisticalmechanics/latticedynamics: measure/modecount/sectoroffsetsในQ9–12
   ถูกต้องหรือไม่ และเงื่อนไขlocal–classicalของQ14พอสำหรับobservableใดจริง?
3. Physicalcorrespondence: frozenalternatingreferenceนี้สามารถมีpreparationใด
   ที่ไม่เพิ่มenergytermและมีparameter/scalesที่รองรับหรือไม่? คำถามนี้ยังไม่มี
   materialinputหรือindependentreview และยังไม่ได้ติดต่อผู้เชี่ยวชาญ

**หนึ่งโจทย์ถัดไป:** ตรวจว่า certified alternating reference มี local–classical
window ที่ใช้กับ observable หนึ่งชนิดได้จริงหรือไม่ เมื่อมี physical dictionary,
parameter origins/χ และ error policy ที่กำหนดจากภายนอกการคำนวณนี้
prerequisite เหล่านี้ยังขาด จึงไม่ใส่ค่าเพื่อให้ Q14 ผ่านหรือค้น minimum เพิ่ม
เพียงเพื่อให้ coverage ดูดี ผู้เขียนเลือกขอบเขต observable/การนำไปใช้ได้โดยไม่
ต้องตรวจคณิตศาสตร์เอง ส่วนการเลือก material หรือ preparation ที่มี duration
ต้องอนุมัติแยก ไม่เปิด kinetics/lifetime/experiment หรือสองเลนอัตโนมัติ

รายงานจบที่certifiedstaticconstructionและboundedinconclusiveผลอื่น
ไม่เปลี่ยนP/Ocontracts, Coreequations, API/defaults/thresholds/READMEหรือphysicsgates
`physical-parent-preparation`ยังเปิด แต่จากเดิมไม่มีstationarywitness
ตอนนี้มีwitnessเฉพาะหนึ่งspinorbitให้ตรวจphysicalpreparationต่อได้

## 8. ชุดทำซ้ำและaudit trail

- [FORMAL contract](../topics/0.13_Thermodynamic_Bridge/calculation_contracts/parent_static_reference_audit.json)
  เป็นcontrollerของscopeใหม่นี้ reviewคงINCOMPLETE ไม่ยกphysicsgate
- [Producer](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/Research_T13_Parent_Static_Reference_Audit.py):
  `--check`อ่านอย่างเดียวเทียบartifact/identities; `--emit-report`เขียนเฉพาะartifactQ
- [Regression tests](../topics/0.13_Thermodynamic_Bridge/Code/03_Research/test_t13_parent_static_reference_audit.py)
  ครอบinterval/coordinate/source/negativecontrolsและclaimboundary
- [Topic log](../topics/0.13_Thermodynamic_Bridge/UPDATE_LOG.md) และ
  [daily ledger](../../WORK_LEDGER/2026/2026-10-25.md) บันทึกเฉพาะงานที่เสร็จจริง

หลักฐานsoftwareเป็นlocalreproduction ไม่ใช่independentreplication
sourcecommit/config/code/contracthashและfailedattemptsอยู่ในartifact
ไม่อัปโหลดrawfiles/บทสนทนา/privatepaths ไม่มีการเผยแพร่หรือขอให้CI
ทำphysicsgateให้เขียวเพื่อปิดงานเอกสาร

## 9. การตรวจรับและขอบเขตการปิดรอบ

- New-only regression suite ผ่าน28/28 รวม source derivatives, canonical metric,
  interval arithmetic/remainders, inclusion, negative curvature, Schur dictionary,
  root-location propagation และ claim boundary; มี14 deliberate negative controls
  และ19 exact identity checks ไม่ใช้จำนวนนี้เป็นคะแนนทฤษฎี
- Producer สร้าง artifact ด้วย `--emit-report` และตรวจ freshness ด้วย `--check`
  แยกชัด ผลยัง `physical_acceptance=false`, review `INCOMPLETE`
  source baseline/config/code/report/contract identities ผูกในแพ็กเกจใหม่
- Read-only completeness และ explicit seven-changed-path audit:22contracts,
  127discovered routes,0errors เป็น methodological coverage ไม่ใช่ physical PASS
  มี legacy unreviewed routes อยู่และไม่ถูกอ้างว่าปิดจากรอบนี้
- QA เอกสารตรวจ8local links,3primary-source links,3explicit anchors,
  15display equationsและ5tables; ไม่มีbroken local link หรือprivatepath/contact/token
  แหล่งสาธารณะตรวจเฉพาะsectionsที่ใช้ ไม่อ้างว่าอ่านทุกหน้า/ทุกบทสนทนา
- หลักฐานเก่า30 normalized hashes และงานค้างอื่น284 raw tracked hashes
  ไม่เปลี่ยน; original Topic-log body byte-preserved งานค้างเดิม463statuses
  ต้องคงอยู่หลังscopedcommit ไม่รัน scientific producers O/P/N/M/R
- ระหว่างพัฒนาแก้ syntax ของ producer และชื่อfieldของaudit wrapper;
  การตรวจwhitespaceทั้งworktreeพบปัญหาเดิมนอกscope จึงตรวจเฉพาะnewpaths/
  stageddiffโดยไม่แก้งานเก่า ไม่มีการเปลี่ยนพลังงาน physicalparametersหรือthreshold

Q0–Q4จบในความหมายของผลส่งมอบที่ตรวจย้อนกลับได้ ไม่ใช่ปิดphysical
correspondenceหรือcontrollerทั้งหมด คำถามต่อที่จำเป็นและข้อห้ามขยายงาน
อยู่ใน§7 งานนี้คอมมิตเฉพาะแพ็กเกจใหม่ในเครื่อง ไม่push/merge/เผยแพร่
