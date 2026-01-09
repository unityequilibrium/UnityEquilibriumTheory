# UET Writing Standards & Conventions

> **MANDATORY:** ทุกสมการ UET ต้องเขียนตามมาตรฐานนี้  
> **NO EXCEPTIONS:** ไม่มีข้อยกเว้น ไม่มีการประนีประนอม  
> **WHY:** เพราะถ้าไม่มีมาตรฐาน เราจะสร้างแค่ความสับสน ไม่ใช่วิทยาศาสตร์

---

## 🎯 CORE PRINCIPLE

**"One symbol, one meaning. Always."**

ถ้าวันนี้มึงใช้ **E** แทนพลังงาน พรุ่งนี้มึงก็ต้องใช้ **E** แทนพลังงาน  
ห้ามเปลี่ยนใจกลางคัน ห้ามใช้ตัวเดียวกันแทนคนละอย่าง  
**Simple as that.**

---

## 1️⃣ VECTOR NOTATION (การเขียน Vector)

### Standard: Arrow notation for vectors

**CORRECT:**

```
F⃗       (force vector)
r⃗       (position vector)
v⃗       (velocity vector)
∇⃗       (del operator)
```

**WRONG:**

```
F       (ambiguous - scalar or vector?)
𝐅       (bold - ยากต่อการพิมพ์)
[F]     (แปลก)
```

### Unit vectors: hat notation

**CORRECT:**

```
r̂       (radial unit vector)
θ̂       (angular unit vector)
x̂, ŷ, ẑ  (Cartesian unit vectors)
```

**WRONG:**

```
e_r     (ยาวเกินไป)
u_r     (สับสนกับ velocity)
```

### WHY Arrow?

1. **ชัดเจน** - เห็นทีเดียวว่าเป็น vector
2. **Universal** - ทุกที่ในโลกใช้
3. **Typable** - พิมพ์ได้ใน LaTeX, markdown, แม้แต่ plain text

---

## 2️⃣ ENERGY FIELD NOTATION

### Standard: E(r,t) for energy density field

**CORRECT:**

```
E(r,t)          (time-dependent energy density)
E(r)            (static energy density)
E₀              (background energy density)
```

**WRONG:**

```
ρ_E(r,t)        (สับสนกับ mass density ρ)
𝓔(r,t)          (พิมพ์ยาก ดูแฟนซีเกินไป)
Energy(r,t)     (ยาวเกินไป)
```

### Subscripts for different fields

**CORRECT:**

```
E_G(r)          (gravitational energy density)
E_EM(r)         (electromagnetic energy density)
E_strong(r)     (strong nuclear energy density)
E_weak(r)       (weak nuclear energy density)
```

**Shorthand allowed:**

```
E_g, E_e, E_s, E_w    (ในบริบทที่ชัดเจน)
```

### WHY E(r,t)?

1. **E = Energy** - obvious ไม่ต้องคิด
2. **(r,t) = function of space and time** - ชัดเจนว่ามันเปลี่ยนตามตำแหน่งและเวลา
3. **ไม่ซ้ำกับ E = mc²** - พลังงานทั้งหมดใช้ E แต่ E(r,t) คือ field

---

## 3️⃣ CONSTANTS (ค่าคงที่)

### Standard: Use standard physics symbols

|Symbol|Meaning|Value|Unit|
|---|---|---|---|
|**G**|Gravitational constant|6.674 × 10⁻¹¹|m³/(kg·s²)|
|**c**|Speed of light|2.998 × 10⁸|m/s|
|**ℏ**|Reduced Planck constant|1.055 × 10⁻³⁴|J·s|
|**k_e**|Coulomb constant|8.988 × 10⁹|N·m²/C²|
|**ε₀**|Vacuum permittivity|8.854 × 10⁻¹²|F/m|
|**μ₀**|Vacuum permeability|1.257 × 10⁻⁶|H/m|

### UET-specific constants

|Symbol|Meaning|Value|Derivation|
|---|---|---|---|
|**E₀**|Background energy density|8.47 × 10⁻¹⁰ J/m³|From cosmology|
|**α_UET**|UET coupling constant|TBD|To be determined|

### WHY Standard symbols?

**เพราะถ้ามึงใช้สัญลักษณ์แปลกๆ ไม่มีใครรู้จักว่ามึงพูดถึงอะไร**

ถ้ามึงเขียน κ = 8πG/c⁴ (GR style) แทน G  
→ คนที่ไม่ได้เรียน GR จะงง "ไอ้ κ มันคืออะไรวะ?"

**ใช้สัญลักษณ์ที่ทุกคนรู้จัก ไม่ต้องสร้างภาษาใหม่**

---

## 4️⃣ GRADIENT & DIFFERENTIAL OPERATORS

### Standard: ∇ for gradient, d/dr for derivatives

**CORRECT:**

```
∇E              (gradient of E - vector)
∇·F⃗             (divergence of F)
∇×F⃗             (curl of F)
dE/dr           (derivative w.r.t. r - scalar)
∂E/∂t           (partial derivative w.r.t. time)
```

**WRONG:**

```
grad(E)         (ยาวเกินไป)
E'              (สับสน - derivative ทิศไหน?)
DE/Dr           (capital D สงวนไว้ให้ covariant derivative)
```

### WHY ∇?

1. **Compact** - สั้น กระชับ
2. **Universal** - ทุกที่ใช้
3. **Vector-aware** - บอกทิศทางโดยตัวมันเอง

---

## 5️⃣ FORCE NOTATION

### Standard: F⃗ with subscript for type

**CORRECT:**

```
F⃗_G            (gravitational force)
F⃗_EM           (electromagnetic force)
F⃗_strong       (strong nuclear force)
F⃗_weak         (weak nuclear force)
F⃗_net          (net force)
```

**Shorthand allowed in context:**

```
F⃗_g, F⃗_e, F⃗_s, F⃗_w
```

### Components notation

**CORRECT:**

```
F_r             (radial component - scalar)
F_θ             (angular component - scalar)
F_x, F_y, F_z   (Cartesian components - scalars)
```

**Note:** ไม่มี arrow = scalar component

---

## 6️⃣ EQUATION LABELING

### Standard: Descriptive names + numbers

**CORRECT:**

```
[E_density_G]   E_G(r) = GM²/(8πr⁴) + E₀
[F_gradient]    F⃗ = -m∇E
[F_Newton]      F⃗ = -GMm/r² r̂
```

**WRONG:**

```
[Eq.1]          (ไม่บอกว่ามันคืออะไร)
[Formula]       (generic เกินไป)
```

### In-text references

**CORRECT:**

```
"From the gravitational energy density equation [E_density_G]..."
"Substituting into the gradient force formula [F_gradient]..."
```

---

## 7️⃣ DIMENSIONAL ANALYSIS FORMAT

### Standard: Square brackets for dimensions

**CORRECT:**

```
[E] = J/m³ = kg/(m·s²)
[F] = N = kg·m/s²
[G] = m³/(kg·s²)
```

**Check format:**

```
Left side: [quantity]
Right side: dimensions

Example:
[E(r)] = [GM²/(8πr⁴)]
       = [G][M²]/[r⁴]
       = (m³/kg·s²)(kg²)/(m⁴)
       = kg/(m·s²)
       = J/m³ ✓
```

---

## 8️⃣ APPROXIMATIONS & LIMITS

### Standard: Clear notation for approximations

**CORRECT:**

```
F ≈ ma              (approximately equal)
F → ma as v → 0     (approaches in limit)
F ∼ 1/r²            (scales as / proportional to)
F ≪ ma              (much less than)
F ≫ ma              (much greater than)
```

**WRONG:**

```
F ~ ma              (ambiguous - approx or scales?)
F = ma (approx)     (ใช้คำแทนสัญลักษณ์)
```

---

## 9️⃣ SPECIAL CASES & CONDITIONAL EQUATIONS

### Standard: Use "where" or "for" with conditions

**CORRECT:**

```
F⃗ = -GMm/r² r̂,    where r > r_Schwarzschild

E(r) = {
  GM²/(8πr⁴),     for r > r_min
  ∞,              for r = 0
}
```

---

## 🔟 TYPOGRAPHY RULES

### Numbers

**CORRECT:**

```
1.23 × 10⁻¹⁰        (scientific notation with ×)
3.14159...          (ellipsis for continuing decimals)
~10⁻¹⁵ m            (~ for "approximately")
```

**WRONG:**

```
1.23e-10            (programming style - ใช้ใน code อย่างเดียว)
1.23*10^-10         (ugly)
```

### Greek letters

**Uppercase vs lowercase matters:**

```
Δ (Delta) ≠ δ (delta)
Σ (Sigma) ≠ σ (sigma)
Ω (Omega) ≠ ω (omega)
```

**Use lowercase for:**

- α (alpha) - coupling constants, angles
- θ (theta) - angles
- λ (lambda) - wavelength
- ρ (rho) - density
- σ (sigma) - cross-section

**Use uppercase for:**

- Δ (delta) - change in quantity
- Σ (sigma) - summation
- Ω (omega) - solid angle

---

## 1️⃣1️⃣ COMMON PITFALLS TO AVOID

### ❌ DON'T: Mix notations in same document

**WRONG:**

```
Section 1: F⃗ = ...
Section 2: 𝐅 = ...    ← ใช้คนละแบบ!
```

### ❌ DON'T: Reuse symbols for different meanings

**WRONG:**

```
Let E = energy
...later...
Let E = electric field  ← ใช้ E ซ้ำ!
```

### ❌ DON'T: Use ambiguous notation

**WRONG:**

```
F = GMm/r²    ← scalar or vector? ไม่ชัดเจน
```

**CORRECT:**

```
F = GMm/r²    (magnitude of force)
or
F⃗ = -GMm/r² r̂  (vector force)
```

### ❌ DON'T: Omit units

**WRONG:**

```
G = 6.674 × 10⁻¹¹   ← units หายไปไหน?
```

**CORRECT:**

```
G = 6.674 × 10⁻¹¹ m³/(kg·s²)
```

---

## 1️⃣2️⃣ EQUATION FORMATTING IN MARKDOWN/LATEX

### Standard block equations

```latex
$$
F⃗ = -\frac{GMm}{r^2}\hat{r}
$$
```

### Inline equations

```latex
The force $F⃗$ acts radially inward with magnitude $F = GMm/r^2$.
```

### Multi-line derivations

```latex
\begin{align}
F⃗ &= m \cdot \frac{2πr³}{M} \nabla E \\
  &= m \cdot \frac{2πr³}{M} \cdot \left(-\frac{GM²}{2πr⁵}\right)\hat{r} \\
  &= -\frac{GMm}{r²}\hat{r}
\end{align}
```

---

## 1️⃣3️⃣ COMMENTING & EXPLANATION STYLE

### Standard: Inline comments with parentheses

**CORRECT:**

```
E_G(r) = GM²/(8πr⁴)    (gravitational energy density)
where:
  G = gravitational constant
  M = source mass
  r = radial distance
```

### Explaining steps

**CORRECT:**

```
Step 1: Start with E_G(r) = GM²/(8πr⁴)
Step 2: Take gradient: ∇E_G = -4GM²/(8πr⁵) r̂ = -GM²/(2πr⁵) r̂
Step 3: Apply force formula: F⃗ = m·(2πr³/M)·∇E_G
Step 4: Simplify: F⃗ = -GMm/r² r̂  ✓
```

---

## 1️⃣4️⃣ VALIDATION MARKERS

### Standard: Checkmarks and crosses

**CORRECT:**

```
✓ Dimensional analysis passed
✗ Reduces to Newton (FAILED - needs correction)
⚠ Assumption: weak field limit
```

---

## 1️⃣5️⃣ STYLE CONSISTENCY CHECKLIST

ก่อนเผยแพร่สมการใดๆ ต้องเช็คว่า:

- [ ] Vectors มี arrow (F⃗ ไม่ใช่ F)
- [ ] Constants ใช้สัญลักษณ์มาตรฐาน (G ไม่ใช่ g_const)
- [ ] Units ระบุครบทุกค่า
- [ ] Subscripts สอดคล้องกัน (E_G ไม่ใช่ E_grav)
- [ ] Equations มี labels ที่มีความหมาย
- [ ] ไม่มีสัญลักษณ์ซ้ำความหมายต่างกัน
- [ ] Format ตาม LaTeX/Markdown standards
- [ ] Comments อธิบายชัดเจน

---

## 📚 QUICK REFERENCE TABLE

|Element|Standard|Example|Notes|
|---|---|---|---|
|**Vector**|Arrow|F⃗, r⃗, v⃗|Always|
|**Unit vector**|Hat|r̂, θ̂, x̂|Normalized|
|**Energy field**|E(r,t)|E_G(r), E_EM(r)|Subscript for type|
|**Gradient**|∇|∇E, ∇·F⃗|Del operator|
|**Derivative**|d/dr, ∂/∂t|dE/dr, ∂E/∂t|Partial if multi-var|
|**Approximation**|≈, ∼|F ≈ ma, F ∼ 1/r²|≈ for value, ∼ for scaling|
|**Scientific notation**|×|1.23 × 10⁻¹⁰|Not * or e|
|**Equation label**|[name_desc]|[F_Newton], [E_density_G]|Descriptive|

---

## 🎯 ENFORCEMENT

**These standards are MANDATORY.**

ทุกสมการที่ไม่ตามมาตรฐาน = **ไม่ผ่าน validation**

ไม่มีข้อแม้ ไม่มีพิเศษเฉพาะตัว  
ถ้ามึงอยากเขียนสมการ UET **มึงต้องเขียนตามกติกา**

WHY SO STRICT?

เพราะ **consistency = credibility**

ถ้าทฤษฎีเขียนไม่สอดคล้องกันเอง ใครจะเชื่อว่ามันถูก?

---

**END OF STANDARDS DOCUMENT**

_Last updated: 2025-12-27_  
_Next review: เมื่อมีสมการใหม่ที่ต้องการสัญลักษณ์ที่ไม่มีในนี้_