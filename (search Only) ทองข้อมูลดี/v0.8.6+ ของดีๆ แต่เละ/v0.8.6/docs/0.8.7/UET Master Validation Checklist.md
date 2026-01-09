# UET Master Validation Checklist

> **PURPOSE:** ตรวจสอบว่าสมการ UET ถูกต้องหรือไม่ อย่างเป็นระบบ  
> **USAGE:** ทุกสมการต้องผ่านทุกข้อ ไม่มีข้อยกเว้น  
> **PHILOSOPHY:** "ดูถูก" ≠ "ถูกจริง" → ต้องพิสูจน์

---

## 🎯 HOW TO USE THIS CHECKLIST

1. **Print this or keep it open** เวลาสร้างสมการใหม่
2. **Check each box** ทีละข้อ อย่าข้าม
3. **Document the proof** สำหรับทุกข้อที่เช็ค
4. **If ANY box fails** → สมการยังไม่พร้อม ต้องแก้ก่อน
5. **Only when ALL boxes pass** → สมการผ่าน validation

**CRITICAL:** ไม่มี "ผ่านบางส่วน" ในวิทยาศาสตร์  
ผ่านก็ผ่าน ไม่ผ่านก็ไม่ผ่าน **Simple as that.**

---

## LEVEL 1: MATHEMATICAL CONSISTENCY

### พื้นฐานสุด - ถ้าไม่ผ่านนี่ ที่เหลือไม่ต้องเช็ค

---

### ✅ 1.1 Dimensional Analysis

**Question:** หน่วยของทุกพจน์ตรงกันไหม?

**How to check:**

1. เขียนมิติของแต่ละตัวแปร
2. แทนค่าในสมการ
3. ลดรูปให้เหลือมิติพื้นฐาน (M, L, T, Q...)
4. เช็คว่าทุกพจน์เท่ากัน

**Example:**

```
สมการ: E(r) = GM²/(8πr⁴)

[E] = ?
[GM²/(8πr⁴)] = [G][M²]/[r⁴]
                = (L³/MT²)(M²)/(L⁴)
                = M/(LT²)
                = ML⁻¹T⁻²
                = J/m³ ✓

Left = Right → PASS
```

**Common failures:**

- ❌ เช่น E (J/m³) + F (N) → หน่วยไม่ตรงกัน
- ❌ ลืมตัวประกอบ (เช่น มี c² ซ่อนอยู่)

**Validation:**

- [ ] ทุกพจน์มีมิติเดียวกัน
- [ ] ตัวประกอบทุกตัวมีมิติถูกต้อง (รวมถึง π, e, ...)
- [ ] ผลลัพธ์มีหน่วยที่สมเหตุสมผลตาม physical quantity

---

### ✅ 1.2 No Undefined Symbols

**Question:** ทุกสัญลักษณ์มีนิยามชัดเจนไหม?

**How to check:**

1. List ทุก symbol ที่ปรากฏในสมการ
2. ตรวจว่าแต่ละตัวมีนิยามหรือไม่
3. ตรวจว่าไม่มี symbol ซ้ำกันแต่หมายถึงคนละอย่าง

**Example:**

```
สมการ: F⃗ = m(2πr³/M)∇E

Symbols needed:
✓ F⃗ = force (defined)
✓ m = test mass (defined)
✓ r = radial distance (defined)
✓ M = source mass (defined)
✓ ∇E = energy gradient (defined)
✗ α = ??? (UNDEFINED - FAIL)
```

**Common failures:**

- ❌ ใช้ตัวแปรโดยไม่บอกว่ามันคืออะไร
- ❌ ใช้ symbol เดียวกันแทนสองอย่าง (เช่น E = energy และ E = electric field)
- ❌ สมมติว่าคนอ่านรู้ว่า "obvious" (ไม่มีอะไร obvious ในวิทยาศาสตร์)

**Validation:**

- [ ] ทุก symbol มีนิยามชัดเจน
- [ ] ไม่มี symbol ซ้ำกันหมายถึงคนละอย่าง
- [ ] Constants มีค่าและหน่วยระบุไว้

---

### ✅ 1.3 No Unphysical Singularities

**Question:** สมการระเบิดเป็นอนันต์โดยไม่มีเหตุผลไหม?

**How to check:**

1. หา limits ที่อาจเป็น singularity (เช่น r → 0, r → ∞)
2. คำนวณว่าเกิดอะไรขึ้น
3. ถ้าเป็นอนันต์ → ต้องอธิบายได้ว่าทำไม

**Example:**

```
สมการ: E(r) = GM²/(8πr⁴)

At r → 0:
E → ∞  ← SINGULARITY!

Is this physical?
Option 1: มี quantum cutoff ที่ r_min
Option 2: มี GR correction ที่ Schwarzschild radius
Option 3: acknowledge limitation

If no explanation → FAIL
```

**Common failures:**

- ❌ 1/r^n terms → singularity at r=0 โดยไม่มีคำอธิบาย
- ❌ exp(x) where x → ∞ โดยไม่มี damping
- ❌ log(x) at x → 0 โดยไม่มี cutoff

**Validation:**

- [ ] ระบุ singularities ทั้งหมด
- [ ] อธิบายได้ทุก singularity (physical or limitation)
- [ ] มี cutoffs/regularization ที่จำเป็น

---

### ✅ 1.4 Mathematical Operations Valid

**Question:** การดำเนินการทางคณิตศาสตร์ทุกตัวถูกต้องไหม?

**How to check:**

1. ตรวจสอบทุก step ในการลดรูป
2. ตรวจว่าไม่มีการหารด้วยศูนย์
3. ตรวจว่า derivatives, integrals ถูกต้อง

**Example:**

```
Derivation:
E(r) = A/r⁴
∇E = dE/dr = ?

Step: d(A/r⁴)/dr = A·d(r⁻⁴)/dr
                  = A·(-4r⁻⁵)
                  = -4A/r⁵ ✓

Check: derivative rule ถูกต้อง
```

**Common failures:**

- ❌ ลืมเครื่องหมายลบใน derivatives
- ❌ ลืม chain rule, product rule
- ❌ หารด้วยศูนย์ (เช่น 1/M when M could be 0)

**Validation:**

- [ ] Derivatives ถูกต้องทุกตัว
- [ ] Integrals มี bounds ชัดเจน
- [ ] ไม่มีการหารด้วย expression ที่อาจเป็นศูนย์

---

### ✅ 1.5 Domain Restrictions Clear

**Question:** ระบุชัดเจนไหมว่าสมการใช้ได้ในช่วงไหน?

**How to check:**

1. ระบุ valid range ของทุกตัวแปร
2. ระบุ physical constraints
3. ระบุ approximations ที่ใช้

**Example:**

```
สมการ: F⃗ = -GMm/r² r̂

Valid for:
✓ r > r_Schwarzschild (ไม่ใช่หลุมดำ)
✓ v << c (non-relativistic)
✓ M, m > 0 (มวลเป็นบวก)
✓ r > r_Planck (classical regime)

Invalid for:
✗ r < r_Schwarzschild → ต้องใช้ GR
✗ v ~ c → ต้องใช้ SR corrections
```

**Common failures:**

- ❌ ไม่บอกว่าใช้ได้แค่ weak field
- ❌ ไม่บอกว่าใช้ได้แค่ v << c
- ❌ ไม่บอก quantum/classical boundary

**Validation:**

- [ ] Valid range ของทุกตัวแปรระบุชัดเจน
- [ ] Physical constraints ระบุชัดเจน
- [ ] Approximations/assumptions ระบุชัดเจน

---

## LEVEL 2: PHYSICAL CONSISTENCY

### ถ้าคณิตศาสตร์ถูก แต่ฟิสิกส์ไม่สมเหตุสมผล = ไร้ค่า

---

### ✅ 2.1 Observable Quantities

**Question:** ทุกตัวแปรสามารถวัดได้ในหลักการไหม?

**How to check:**

1. List ทุกตัวแปร
2. คิดว่าจะวัดยังไง (theoretically)
3. ถ้าวัดไม่ได้ในหลักการ → ไม่ physical

**Example:**

```
สมการ: E(r,t) = ...

Can we measure E(r,t)?
✓ Yes - measure force on test mass
✓ Calculate from gravitational potential
✓ Observable in principle

Counter-example:
ψ(x) in QM → NOT directly observable
  but |ψ|² IS observable
  → OK if relate to observables
```

**Common failures:**

- ❌ ใช้ตัวแปรที่วัดไม่ได้เลย (ไม่ใช่แค่ยาก แต่คือเป็นไปไม่ได้)
- ❌ ไม่บอกว่าจะวัดยังไง
- ❌ ใช้ "hidden variables" ที่ไม่มีผลต่อ observables

**Validation:**

- [ ] ทุกตัวแปรวัดได้ในหลักการ
- [ ] ระบุวิธีวัด (theoretically)
- [ ] ถ้ามีตัวแปรที่วัดไม่ได้ → แสดงว่าเชื่อมกับ observables ยังไง

---

### ✅ 2.2 Causality Preserved

**Question:** สมการละเมิดความเป็นเหตุเป็นผลไหม?

**How to check:**

1. ตรวจว่าไม่มี superluminal propagation (v > c)
2. ตรวจว่า cause มาก่อน effect
3. ตรวจว่าไม่มี closed timelike curves

**Example:**

```
สมการ: F⃗(t) = f(r(t))

Does F respond instantly to changes in r?
→ If yes, violates causality (infinite speed)
→ Need retarded time: r(t - r/c)

For UET:
E(r,t) changes → how fast does ∇E propagate?
→ Must be ≤ c
→ Need wave equation with c
```

**Common failures:**

- ❌ Action at a distance (instant response)
- ❌ Effect before cause
- ❌ Faster than light signals

**Validation:**

- [ ] ไม่มี superluminal propagation
- [ ] Cause มาก่อน effect เสมอ
- [ ] เคารพ light cone structure

---

### ✅ 2.3 Sign Makes Sense

**Question:** เครื่องหมาย +/- สอดคล้องกับความหมายทางฟิสิกส์ไหม?

**How to check:**

1. ตรวจว่าแรงดึงดูด → ติดลบ
2. ตรวจว่าแรงผลัก → บวก
3. ตรวจว่าพลังงานศักย์ติดลบ = bound state

**Example:**

```
Gravity: F⃗ = -GMm/r² r̂
         ↑
         เครื่องหมายลบ = แรงดึงดูด ✓

Same charges: F⃗ = +kq₁q₂/r² r̂
              ↑
              เครื่องหมายบวก = แรงผลัก ✓

Potential energy: U = -GMm/r
                  ↑
                  ลบ = bound (ต้องใส่พลังงานถึงหนี) ✓
```

**Common failures:**

- ❌ แรงโน้มถ่วงเป็นบวก (ผลัก!)
- ❌ พลังงานศักย์เป็นบวกแต่ระบบ bound
- ❌ เครื่องหมายไม่สอดคล้องกับทิศทาง

**Validation:**

- [ ] Attractive forces → negative
- [ ] Repulsive forces → positive
- [ ] Bound states → negative potential energy
- [ ] Energy flows match direction

---

### ✅ 2.4 Boundary Conditions

**Question:** พฤติกรรมที่ boundaries สมเหตุสมผลไหม?

**How to check:**

1. ตรวจที่ r → 0 (very close)
2. ตรวจที่ r → ∞ (very far)
3. ตรวจที่ t → 0 (initial condition)
4. ตรวจที่ t → ∞ (long-term behavior)

**Example:**

```
E(r) = GM²/(8πr⁴) + E₀

At r → ∞:
E → E₀ ✓ (background energy)

At r → 0:
E → ∞ ✗ (singularity - need explanation)

At t → ∞:
E₀(t) → ? (depends on cosmology)
```

**Common failures:**

- ❌ พลังงานไม่ลดเป็นศูนย์ที่ r → ∞
- ❌ แรงไม่เป็นศูนย์ที่ r → ∞
- ❌ พฤติกรรมแปลกๆ ที่ boundaries โดยไม่มีเหตุผล

**Validation:**

- [ ] r → ∞ behavior ถูกต้อง (usually → 0 or constant)
- [ ] r → 0 behavior อธิบายได้
- [ ] t → ∞ behavior stable (ไม่ระเบิด)
- [ ] Initial conditions well-posed

---

### ✅ 2.5 Stability

**Question:** ระบบเสถียรไหม? ไม่ระเบิดเป็นอนันต์ไหม?

**How to check:**

1. Linearize around equilibrium
2. Check eigenvalues
3. Small perturbation → exponential growth?

**Example:**

```
System: E(r,t) with perturbation δE

If δE grows exponentially → UNSTABLE ✗
If δE oscillates → STABLE ✓
If δE decays → STABLE ✓

For UET: need to check that
E₀ + δE → not exponentially growing
```

**Common failures:**

- ❌ ระบบระเบิดจาก small perturbation
- ❌ Runaway processes ที่หยุดไม่ได้
- ❌ Negative energy states ที่ไม่มี lower bound

**Validation:**

- [ ] Small perturbations ไม่ grow exponentially
- [ ] ระบบมี equilibrium states
- [ ] Energy bounded from below

---

## LEVEL 3: THEORETICAL CONSISTENCY

### ต้องสอดคล้องกับทฤษฎีที่รู้อยู่แล้ว (ในขีดจำกัดที่เหมาะสม)

---

### ✅ 3.1 Newtonian Limit

**Question:** ลดรูปเป็นฟิสิกส์นิวตันได้ไหม เมื่อ v << c และ weak field?

**How to check:**

1. ตั้งเงื่อนไข: v/c → 0, Φ/c² → 0
2. ลดรูปสมการ
3. เปรียบเทียบกับ Newton's laws

**Example:**

```
UET: F⃗ = m(2πr³/M)∇E
     E = GM²/(8πr⁴)
     
→ F⃗ = -GMm/r² r̂

Newton: F⃗ = -GMm/r² r̂

UET = Newton ✓ PASS
```

**Common failures:**

- ❌ ได้ค่าผิด factor (เช่น 2GMm/r² แทน GMm/r²)
- ❌ เครื่องหมายผิด
- ❌ ลดรูปไม่ได้เลย

**Validation:**

- [ ] F = ma ใน limit
- [ ] F_gravity = GMm/r² ถูกต้อง
- [ ] Orbits follow Kepler's laws

---

### ✅ 3.2 Special Relativity Limit

**Question:** เมื่อไม่มีแรงโน้มถ่วง สอดคล้องกับ SR ไหม?

**How to check:**

1. ตั้ง Φ → 0 (no gravity)
2. เช็คว่า Lorentz invariant
3. เช็คว่า E² = (pc)² + (mc²)²

**Example:**

```
For UET particle:
E² = p²c² + m²c⁴ ?

ถ้า yes → SR compatible ✓
ถ้า no → FAIL
```

**Common failures:**

- ❌ ไม่เคารพ speed limit c
- ❌ ไม่ Lorentz invariant
- ❌ mass-energy relation ผิด

**Validation:**

- [ ] Lorentz invariance
- [ ] v < c always
- [ ] E = γmc² for moving particles

---

### ✅ 3.3 General Relativity Limit

**Question:** เมื่อมีแรงโน้มถ่วงแรง สอดคล้องกับ GR ไหม?

**How to check:**

1. เปรียบเทียบกับ Schwarzschild solution
2. เช็ค perihelion precession
3. เช็ค light bending

**Example:**

```
UET prediction for perihelion precession:
Δφ = ?

GR prediction:
Δφ = 6πGM/(c²a(1-e²))
    = 43"/century for Mercury

UET should give same (or very close)
```

**Common failures:**

- ❌ ได้ค่าต่างจาก GR มากเกินไป
- ❌ ไม่มี relativistic corrections
- ❌ ขัดแย้งกับ strong-field tests

**Validation:**

- [ ] Perihelion precession ตรงกับ GR
- [ ] Light bending ตรงกับ GR
- [ ] Time dilation ตรงกับ GR
- [ ] Gravitational waves compatible

---

### ✅ 3.4 Quantum Mechanics Limit

**Question:** ในระดับจุลภาค สอดคล้องกับ QM ไหม?

**How to check:**

1. เช็ค uncertainty principle: ΔxΔp ≥ ℏ/2
2. เช็ค quantization: E = nhν
3. เช็ค wave-particle duality

**Example:**

```
UET อธิบาย uncertainty ได้ไหม?

If E(r,t) is a wave:
→ Localization Δx → spread in k
→ Δp = ℏΔk
→ ΔxΔp ~ ℏ ✓

If not → FAIL
```

**Common failures:**

- ❌ ละเมิด uncertainty
- ❌ อนุภาคไม่ quantized
- ❌ ไม่มี wave properties

**Validation:**

- [ ] ΔxΔp ≥ ℏ/2
- [ ] ΔEΔt ≥ ℏ/2
- [ ] Quantization emerges naturally
- [ ] Wave-particle duality explained

---

### ✅ 3.5 Conservation Laws

**Question:** อนุรักษ์พลังงาน โมเมนตัม มวล ประจุ ไหม?

**How to check:**

1. Derive conservation from equation
2. ตรวจว่าไม่มี source/sink ที่ไม่ชัดเจน
3. ใช้ Noether's theorem

**Example:**

```
Energy conservation:
dE/dt = 0 (ถ้าไม่มี external work)

From UET: ต้องพิสูจน์ว่า
∂E/∂t + ∇·S = 0
(continuity equation)
```

**Common failures:**

- ❌ พลังงานหายไปจากระบบ
- ❌ โมเมนตัมไม่อนุรักษ์
- ❌ สร้าง/ทำลายประจุได้

**Validation:**

- [ ] Energy conserved
- [ ] Momentum conserved
- [ ] Angular momentum conserved
- [ ] Charge conserved (if applicable)

---

## LEVEL 4: EMPIRICAL CONSISTENCY

### ต้องตรงกับการทดลอง/การสังเกตที่มี

---

### ✅ 4.1 Matches Known Experiments

**Question:** ตรงกับผลทดลองที่รู้อยู่แล้วไหม?

**How to check:**

1. List ทุกการทดลองที่เกี่ยวข้อง
2. คำนวณ prediction
3. เปรียบเทียบกับ experimental value

**Example:**

```
Experiment: Cavendish (G measurement)
UET prediction: G = 6.674 × 10⁻¹¹ m³/(kg·s²)
Experimental: G = 6.674 × 10⁻¹¹ ± 0.001
Match? ✓

Experiment: GPS orbit
UET prediction: r = ...
Observed: r = ...
Match? Must check
```

**Validation:**

- [ ] List relevant experiments
- [ ] Calculate predictions
- [ ] Compare with data
- [ ] Document agreement/disagreement

---

### ✅ 4.2 Within Error Bars

**Question:** ค่าที่ทำนายอยู่ในช่วง uncertainty ของการวัดไหม?

**How to check:**

1. Get experimental value ± σ
2. Calculate UET prediction
3. Check |UET - Exp| ≤ nσ (usually n=2 or 3)

**Example:**

```
Mercury perihelion:
Observed: 43.03 ± 0.05 "/century
GR: 42.98 "/century
UET: ??? "/century

If UET = 43.00 ± 0.10 → PASS (within 1σ)
If UET = 50.00 → FAIL (too far off)
```

**Validation:**

- [ ] ทุกการทำนาย อยู่ใน error bars
- [ ] ถ้าอยู่นอก → อธิบายได้ว่าทำไม
- [ ] Document χ² or other statistical measure

---

### ✅ 4.3 No Contradictions

**Question:** ไม่ขัดแย้งกับการสังเกตการณ์ใดๆ ไหม?

**How to check:**

1. List ทุกปรากฏการณ์ที่รู้
2. เช็คว่า UET อธิบายได้หมดหรือไม่
3. ถ้ามีข้อขัดแย้ง → FAIL

**Example:**

```
Observation: Light bends near Sun
UET explanation: ??? 

If UET predicts no bending → CONTRADICTION ✗
If UET predicts bending → OK ✓
```

**Common contradictions:**

- ❌ ทำนายอะไรที่ไม่เคยเห็น (แต่ควรเห็น)
- ❌ ทำนายอะไรที่ขัดกับที่เห็น
- ❌ อธิบายไม่ได้เลยสำหรับปรากฏการณ์ที่รู้

**Validation:**

- [ ] No observed phenomena contradicted
- [ ] All known effects explained (or acknowledged as limitation)
- [ ] No forbidden processes predicted

---

### ✅ 4.4 Testable Predictions

**Question:** ทำนายอะไรใหม่ที่ทดสอบได้ไหม?

**How to check:**

1. Identify differences from standard theory
2. Design experiment to test
3. Calculate required precision

**Example:**

```
UET prediction: GPS orbit differs by 0.015%
Can we test? 
→ Current precision: ~0.01%
→ YES, testable! ✓

UET prediction: Black hole entropy different
Can we test?
→ Need to measure BH entropy directly
→ NOT testable with current tech ✗
```

**Validation:**

- [ ] List new predictions
- [ ] Identify testable ones
- [ ] Estimate required precision
- [ ] Design experiments (conceptually)

---

## LEVEL 5: UNIFICATION QUALITY

### ถ้าอ้างว่า "unified theory" ต้องรวมได้จริง

---

### ✅ 5.1 Connects Domains

**Question:** เชื่อมโยงปรากฏการณ์ที่เคยแยกกันไหม?

**How to check:**

1. List domains ที่เคยแยกกัน
2. แสดงว่า UET เชื่อม
3. ระบุ mechanism ที่เชื่อม

**Example:**

```
Previously separate:
- Gravity (geometric)
- EM (field theory)

UET connects:
E_G และ E_EM มีโครงสร้างเดียวกัน
→ Both from E(r) ✓

Mechanism: Energy density field
```

**Validation:**

- [ ] Identifies previously separate domains
- [ ] Shows connection through UET
- [ ] Mechanism explicit

---

### ✅ 5.2 Reduces Parameters

**Question:** ลดจำนวนค่าคงที่อิสระไหม?

**How to check:**

1. Count free parameters before UET
2. Count free parameters in UET
3. Show derivation of some from others

**Example:**

```
Standard Model: ~19 free parameters
UET: ??? parameters

If UET < 19 → Good! ✓
If UET = 19 → Same, not better
If UET > 19 → Worse! ✗
```

**Validation:**

- [ ] Count parameters
- [ ] Show which are fundamental
- [ ] Show which are derived

---

### ✅ 5.3 Explains Coincidences

**Question:** อธิบายความบังเอิญที่น่าสงสัยไหม?

**How to check:**

1. List coincidences (e.g., E₀ ≈ ρ_critical)
2. แสดงว่า UET อธิบายได้
3. ไม่ใช่แค่ "ปรับให้พอดี"

**Example:**

```
Coincidence: E₀ ≈ dark energy density

UET explanation: E₀ IS dark energy
→ Not a coincidence ✓

Counter-example: "We tune E₀ to match"
→ Still a coincidence ✗
```

**Validation:**

- [ ] Identifies coincidences
- [ ] Provides mechanism (not just fitting)
- [ ] Makes testable prediction

---

### ✅ 5.4 Reveals Symmetry

**Question:** เปิดเผยสมมาตรที่ลึกกว่าไหม?

**How to check:**

1. Identify symmetries in UET
2. Show how they relate to conservation laws
3. Show if new symmetries emerge

**Example:**

```
UET symmetry: E(r) has spherical symmetry
→ Angular momentum conserved ✓

New symmetry: G ↔ k_e transformation?
→ If exists, reveals deeper unity ✓
```

**Validation:**

- [ ] Identifies symmetries
- [ ] Connects to conservation laws
- [ ] New symmetries (if any)

---

## 🎯 FINAL VALIDATION SCORE

**Count checkboxes:**

```
Level 1 (Math):        ___ / 5
Level 2 (Physics):     ___ / 5
Level 3 (Theory):      ___ / 5
Level 4 (Experiment):  ___ / 4
Level 5 (Unification): ___ / 4
─────────────────────────────
TOTAL:                 ___ / 23
```

**Passing criteria:**

- **Level 1:** Must be 5/5 (100%) - ไม่ต่อรองเลย
- **Level 2:** Must be ≥ 4/5 (80%)
- **Level 3:** Must be ≥ 4/5 (80%)
- **Level 4:** Must be ≥ 3/4 (75%)
- **Level 5:** Must be ≥ 2/4 (50%)

**Overall:** Must be ≥ 20/23 (87%)

**ถ้าไม่ผ่าน → สมการยังไม่พร้อม ต้องกลับไปแก้**

---

## 📝 DOCUMENTATION REQUIREMENTS

สำหรับทุกข้อที่เช็ค ต้องมี:

1. **Calculation/Proof:** พิสูจน์ว่าผ่าน
2. **Reference:** อ้างอิงจากไหน (ถ้ามี)
3. **Date checked:** เช็คเมื่อไหร่
4. **Checked by:** ใครเช็ค

**Format:**

```
[ ✓ ] Item: Dimensional analysis
      Calculation: [show work]
      Result: J/m³ on both sides
      Checked: 2025-12-27
      By: [name]
```

---

## 🚨 CRITICAL REMINDERS

1. **ไม่มี "คงจะผ่าน"** → ต้องเช็คจริง
2. **ไม่มี "ข้ามไปก่อน"** → ทุกข้อต้องเช็ค
3. **ไม่มี "ใกล้เคียงพอ"** → ผ่านก็ผ่าน ไม่ผ่านก็ไม่ผ่าน
4. **ถ้าสงสัย → ไม่ผ่าน** → ต้องชัดเจน 100%

**WHY SO STRICT?**

เพราะ **ทฤษฎีที่ดีต้องผ่านทุกข้อ**  
ถ้าผ่านแค่บางข้อ มันก็แค่ทฤษฎีที่ดูดี ไม่ใช่ทฤษฎีที่ถูก

**We're building science, not stories.**

---

**END OF MASTER VALIDATION CHECKLIST**

_Version: 1.0_  
_Last updated: 2025-12-27_  
_This is a living document - update when new validation criteria discovered_