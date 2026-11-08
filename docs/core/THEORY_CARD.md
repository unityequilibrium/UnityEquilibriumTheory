# UET Theory Card — `UET_PARENT` v1

> **สถานะ: APPROVED — อนุมัติโดยผู้เขียน (santxkoz) 2026-11-08** (ร่างโดย Claude ใน W3)
> Machine-readable: [`theory_card.json`](theory_card.json) · Standard: [`docs/STANDARD.md`](../STANDARD.md) §3
> ระดับของสมการแกนทุกบรรทัด: `L1_CONSISTENT` (W4 derivation check ผ่าน 2026-11-08; ส่วนประกอบ off-diagonal ของ metric equation ยังไม่ได้ตรวจ — ดู `docs/standard/results/R_W4_PARENT_EOM.json`)

## 1. สมการแกน (conservative parent action)

ใช้หน่วย natural (ħ = c = 1) และ signature (−,+,+,+) ส่วน δ ≡ φ − φ\* และ |χ|² ≡ χ₁² + χ₂²

```
S = ∫ d⁴x √−g [ F(φ)(R − 2Λ)/(2κ)
               − ε( ½ k (∇φ)² + U(φ) )
               − ½ Z (∇χ_A)² − W(|χ|²)
               + ½ ε h δ |χ|² ]

F(φ) = 1 + ε ξ δ²
U(φ) = ρ* + ½ μ² δ² + ¼ λ_φ δ⁴
W    = ½ m² |χ|² + ¼ λ_χ |χ|⁴
```

| formula_id | สมการ | โค้ด |
|---|---|---|
| UET-PARENT-ACTION-001 | action ข้างบน | `02_equations/covariant/uet_covariant_matter.py::coupled_conservative_action_density` |
| UET-PARENT-METRIC-EOM | F(G+Λg) + ε(g□f − ∇∇f) = κ(T_χ + T_int + εT_φ), โดย f = ξδ² | `uet_covariant_response.py::uet_metric_residual` |
| UET-PARENT-SCALAR-EOM | ε[k□φ − U′ + f′(R−2Λ)/(2κ)] + ½εh\|χ\|² = 0 | `uet_covariant_matter.py::coupled_response_scalar_equation_residual` |
| UET-PARENT-MATTER-EOM | Z□χ_A − (m² + λ_χ\|χ\|² − εhδ)χ_A = 0 | `uet_covariant_matter.py::matter_eom_residual` |

W4: sympy derivation check ผ่านแล้ว (`05_tests/physics/test_parent_derivation.py`, 28 test, tolerance 1e-10) สมการทั้งสี่บรรทัดจึงเป็น L1

## 2. ตาราง field และ parameter

| สัญลักษณ์ | ความหมาย | mass dim | อิสระ? |
|---|---|---|---|
| g_μν | metric | 0 | ใช่ |
| φ | response scalar (UET Φ) | 1 | field |
| χ_A (A=1,2) | O(2) matter doublet (UET C ในบาง lane) | 1 | field |
| κ | 8πG | −2 | ใช่ |
| Λ | cosmological constant | 2 | ถูกรวมเข้า Λ_eff |
| ε | "non-closure" nesting parameter | 0 | **ไม่อิสระ** (§5) |
| k | kinetic normalization ของ φ | 0 | **ไม่อิสระ** |
| ξ | curvature coupling | −2 | ถูกรวมเข้า ξ_c |
| φ\* | ตำแหน่งสมดุล | 1 | **ไม่อิสระ** (shift) |
| ρ\* | ความหนาแน่นพลังงานสมดุล | 4 | ถูกรวมเข้า Λ_eff |
| μ², λ_φ | mass และ quartic ของ φ | 2, 0 | ถูกรวมเข้า m_ψ², λ_ψ |
| Z | kinetic normalization ของ χ | 0 | **ไม่อิสระ** |
| m², λ_χ | mass และ quartic ของ χ | 2, 0 | ถูกรวมเข้า m_χ², λ_χ̃ |
| h | portal coupling | 1 | ถูกรวมเข้า g_c |

## 3. คลาสทฤษฎีที่รู้จักแล้วที่ใกล้ที่สุด

**Scalar-tensor gravity ที่มี non-minimal coupling แบบกำลังสอง (`ξψ²R`) บวก O(2)/complex scalar ที่ต่อกันผ่าน trilinear portal**

เมื่อเปลี่ยนเป็น canonical field ψ = √(εk) δ และ χ̃ = √Z χ action จะกลายเป็น (ตรวจด้วย sympy แล้ว residual = 0):

```
L = (1 + κ ξ_c ψ²)(R − 2Λ)/(2κ) − ½(∇ψ)² − ½ m_ψ² ψ² − ¼ λ_ψ ψ⁴
    − ½(∇χ̃)² − ½ m_χ² |χ̃|² − ¼ λ_χ̃ |χ̃|⁴ + ½ g_c ψ |χ̃|² − ε ρ*

ξ_c = ξ/(κk)   m_ψ² = μ²/k   λ_ψ = λ_φ/(εk²)   g_c = h √(ε/k) / Z
m_χ² = m²/Z    λ_χ̃ = λ_χ/Z²  Λ_eff = Λ + κ ε ρ*
```

ทฤษฎีนี้อยู่ในคลาสเดียวกับ:
- **Damour–Esposito-Farèse (DEF)** spontaneous scalarization (F ∝ 1 + ξψ²) ซึ่งศึกษาไว้ตั้งแต่ปี 1993
- non-minimal scalar แบบ Higgs-inflation (ξψ²R)
- scalar portal ไปยัง complex scalar sector

## 4. สิ่งที่ต่างจากคลาสนั้น

**ยังไม่มี (none yet)** ที่ระดับ action
- ส่วน UET ที่เพิ่มเข้ามาอีก ได้แก่ R_gen, R_obs, trace และ observer record ถูกประกาศไว้ว่า **ไม่มี feedback** เข้า dynamics จึงไม่เปลี่ยน prediction ใด ๆ ของ action นี้
- Dissipative sector (SK/KMS) ยังไม่ได้อยู่ใน action
- ความต่างจากคลาสมาตรฐาน ถ้ามีจริง ต้องมาจาก (ก) dissipative/open-system sector หรือ (ข) lane mapping ที่ให้ observable ใหม่ ทั้งสองอย่างยังเป็น L0

## 5. Parameter ที่ซ้ำซ้อน และผลต่อ "GR limit"

- **k, Z, φ\*** ถูกดูดซับด้วยการ normalize และ shift field ทั้งหมด
- **ε ไม่ใช่ coupling ทางกายภาพที่แยกออกมาได้** มันปรากฏเฉพาะในชุด λ_ψ, g_c และ Λ_eff
- **ข้อค้นพบสำคัญ:** ที่ค่า parameter เดิมคงที่ เมื่อ ε → 0⁺:
  - ξ_c และ m_ψ² **ไม่เปลี่ยน**
  - g_c → 0
  - λ_ψ → ∞ (strong coupling)
- ดังนั้นเมื่อ ε เป็นค่าบวกใด ๆ ยังคงมี scalar ที่แพร่กระจายได้ มี mass m_ψ และ non-minimal coupling ξ_c ที่ไม่ขึ้นกับ ε
- จุด ε = 0 เป็น**จุดเสื่อม (degenerate point)** เพราะ kinetic term ของ φ หายไป ไม่ใช่ limit ที่ต่อเนื่องไปถึง GR
- ผล "exact GR null at ε = 0" ในโค้ดเดิมจึงเป็นจริงแบบ tautology (§6 ของ standard) และ**ไม่ได้แสดงว่าทฤษฎีลดรูปเป็น GR อย่างต่อเนื่อง**
- Limit ที่มีความหมายในตัวแปร canonical คือ ξ_c → 0 และ g_c → 0 (decoupling) ซึ่งจะเหลือ GR + scalar ที่ไม่ได้ต่อกับอะไร

## 6. Prediction ที่วัดได้ (ผู้สมัคร ยังไม่ได้คำนวณ)

| observable | ระบบ | หมายเหตุ |
|---|---|---|
| PPN γ − 1 | ระบบสุริยะ (Cassini) | รอบ vacuum ที่ ψ = 0 จะได้ F′ = 0 scalar จึงไม่ต่อกับ T ในอันดับเชิงเส้น ดังนั้น **γ = 1 ในอันดับแรก** การทดสอบนี้จึงน่าจะผ่านแบบไม่ได้แยกแยะอะไร (ต้องยืนยันใน W5) |
| Spontaneous scalarization ของดาวนิวตรอน, dipole radiation ใน binary pulsar | PSR J1738+0333 และระบบอื่น | **ช่องทดสอบที่คมที่สุดของคลาส DEF** ข้อมูลจริงจำกัด ξ_c (ผ่าน β ของ DEF) ร่วมกับ m_ψ ต้องหาแหล่งอ้างอิงและสูตร map ใน W5 |
| Fifth force ระยะสั้น (Eöt-Wash) | ห้องปฏิบัติการ | ไวเฉพาะเมื่อ background ψ ≠ 0 หรือ matter ปกติต่อกับ ψ ซึ่ง action นี้ไม่มี จึงคาดว่าไม่ได้ข้อจำกัด |
| ความหนาแน่นพลังงานมืด / w(z) | cosmology | ψ ที่เลื่อนจาก 0 ทำให้ G_eff ขึ้นกับเวลา ต้องใช้ background FRW (Topic 0.3) |

**ผู้เขียนตัดสินใจ (2026-11-08):** pilot หลักของ W5–W6 คือ **binary-pulsar scalarization bounds** ส่วน Cassini ใช้เป็น sanity check เท่านั้น เหตุผลคือในการทดสอบนี้ทฤษฎีมีโอกาสตกจริง

## 7. Lane mapping (ตามสัญญาเดิม ไม่เพิ่มใหม่)

| lane | สัญลักษณ์ UET | ปริมาณมาตรฐาน | สถานะ |
|---|---|---|---|
| phase | C | amplitude ของ order parameter \|χ\| | conditional |
| charge | C | Noether charge density N⁰ ของ global O(2) | conditional |
| response | Φ | φ (หรือ ψ canonical) | candidate |
| response | Π | ∂_t φ | นิยาม |
| He-4 (Topic 13) | O(2) sector | superfluid order parameter | **ยังไม่ได้รับการยอมรับ** (charge-to-atom identity ยังเปิดอยู่) |

C ไม่ใช่มวลโดยทั่วไป และ Φ ไม่ใช่ metric

## 8. อนุมัติ

อนุมัติโดยผู้เขียน (santxkoz) เมื่อ 2026-11-08 บันทึกไว้ใน `theory_card.json` ฟิลด์ `approval`
การอนุมัติหมายถึงยอมรับ**ว่าการ์ดบรรยายทฤษฎีปัจจุบันถูกต้อง** ไม่ได้หมายความว่าทฤษฎีถูก
