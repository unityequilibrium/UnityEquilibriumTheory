# 000.00
## TL;DR

ต่อจากนี้ “แกนเอกสารสาธารณะ/การใช้งาน UET” ควรเริ่มที่ **เฟรมเวิร์ก 2 แกน** ที่มึงสรุปได้แล้ว:

- **แกนแนวนอน (Extrovert / ระบบเปิด):** สนาม → ระบบ → กลไก → แรง → ผลลัพธ์ → ผลกระทบ → feedback
    
- **แกนแนวตั้ง (Introvert / การดำรงอยู่ของสิ่งหนึ่ง):** เงื่อนไข/ข้อจำกัด → ความจำเป็น → คุณสมบัติ → ศักยภาพ → การไหล/การเป็น → ผลลัพธ์ → (คุณค่า/ความขัดแย้ง)
    

แล้วค่อย “map” ลง **สมการ/Ω ที่มีอยู่จริงในโค้ดตอนนี้** (Ω ของ C-only / C-I + dynamics แบบ gradient flow + accept/reject) เพื่อให้:

1. คนทั่วไปเข้าใจ “สิ่งหนึ่งคืออะไร / สมดุลคืออะไร” ก่อน
    
2. นักเทคนิคเอาไปสร้างโมเดลโดเมนใหม่ได้จริง (ผ่าน MI card + run + demo)
    

ด้านล่างคือ “แผ่นเขียนระยะยาว” + “ส่วนนี้ก่อน” ที่ทำให้แกนนี้ชัดและใช้งานได้จริง

---

## Insight

จุดที่ทำให้ทุกคนหลง (รวมถึงมึง) ไม่ใช่เพราะสมการไม่ดี แต่เพราะ **เรายังไม่มีภาษาเชื่อม** ระหว่าง:

- “โลกจริง/ระบบรวม/สิ่งหนึ่ง” (ที่คนคิดเป็นภาพแบบ YouTube)  
    กับ
    
- “ของในสมการ” (Ω + field + dynamics + metrics)
    

ดังนั้นเอกสาร/การคุยต่อจากนี้ต้อง “ล็อกภาษาเชื่อม” ให้แน่นก่อน แล้วค่อยขยายไป thermodynamics / information / quantum / game / Einstein

---

## Analysis

## ส่วนนี้ก่อน: “Dual-Equilibrium + Two-Axis Reading” (แกนกลางที่ต้องเขียนให้จบก่อนอย่างอื่น)

## 0) นิยามฐาน (ให้คนอ่านเริ่มถูก)

**ใน UET harness ปัจจุบัน** สิ่งที่มีจริง (และต้องเป็นฐานของ public doc) คือ:

- **State (ระบบที่กำลังเป็นอยู่):**
    
    - `C(x,y,t)` และ `I(x,y,t)` (หรือ `C_only`) บนกริด 2D (periodic)
        
- **Field/Landscape (สนามที่บอกว่ามันควรไหลไปไหน):**
    
    - **Energy functional Ω** ที่รวม:
        
        - local potential `V(C), V(I)` (quartic Landau)
            
        - coupling `- beta * C * I`
            
        - gradient penalty `~ kC |∇C|² + kI |∇I|²` (spectral grad energy)
            
- **Mechanism (กติกาการเปลี่ยนแปลง):**
    
    - dynamics แบบ dissipative / gradient-like พร้อม **accept–reject + dt backtracking** เพื่อบังคับให้ Ω ไม่เพิ่ม (Lyapunov/monotone gate)
        
- **Result labels (ผลสรุประดับเฟส):**
    
    - `BIAS_C`, `BIAS_I`, `SYM` (มาจาก validator/aggregation)
        

> แปลไทย: ตอนนี้เรามี “โลก 2D ที่มีภูมิประเทศ Ω” + “ลูกบอล/ระบบ (seed) ที่ไหล” + “กติกาให้ไหลลงหลุม” แล้วค่อย “ติดป้ายว่าไปจบฝั่งไหน”

---

## 1) เฟรมเวิร์ก 2 ชั้นของสมดุล (ที่มึงพูด)

### 1.1 Introvert equilibrium (ปัจเจก / input–process–output)

นี่คือ “การเป็นสิ่งหนึ่ง” แบบโมเดลคอมพิวเตอร์:

- **Input:** สภาพแวดล้อม/ข้อจำกัด/พารามิเตอร์ (สนาม) + initial condition (seed)
    
- **Process:** กลไกปรับตัว (dynamics)
    
- **Output:** สถานะปลายทาง + ผลกระทบ (value/conflict ในความหมายเฟรมเวิร์ก)
    

**สมดุลของสิ่งหนึ่ง** ใน UET = “มันเข้า attractor แล้วแกว่ง/เปลี่ยนยาก”  
ในเชิงโค้ดตอนนี้: Ω ลดลงจน “นิ่ง” และ state เข้ารูปแบบคงตัว

### 1.2 Extrovert equilibrium (ระบบเปิด / สนาม–ระบบ–แรง–feedback)

นี่คือ “ระบบรวม” ที่อ่านแบบระบบเปิด:

- **สนาม (Field):** Ω + constraints + boundary + resources
    
- **ระบบ (System):** state ทั้งหมดที่อยู่ในสนาม (ในอนาคตอาจหลาย subsystem)
    
- **แรง (Force):** แรงผลักจากความชันของสนาม (−δΩ/δstate) + แรงต้านจากข้อจำกัด
    
- **ผลลัพธ์:** รูปแบบเฟส/การจัดระเบียบของโลก
    
- **ผลกระทบ–feedback:** ผลจากระบบย้อนกลับไปเปลี่ยนสนาม/เงื่อนไข (นี่คือส่วนที่ทำให้ “โลกมีชีวิต/เรียนรู้” ในภาษาคน)
    

> จุดสำคัญ: ตอนนี้ harness ยังอยู่ในเฟส “สนามคงที่ + ระบบไหล” (feedback ยังเบา) แต่เฟรมเวิร์ก extrovert ทำให้เรารู้ว่าอนาคตต้องเติมอะไร

---

## 2) เฟรมเวิร์กแนวตั้ง “การดำรงอยู่” (ที่มึงย้ำว่าต้องเอามารวม)

จาก framework เดิมของมึง (และไฟล์ framework ที่มีอยู่) แกนแนวตั้งคือ:

- **เงื่อนไข/ข้อจำกัด (Constraints):** ขอบเขต, BC, stability gates
    
- **ความจำเป็น (Necessity):** ต้องไม่ระเบิด, Ω ต้องลง, ต้องผ่าน coercivity/acceptance
    
- **คุณสมบัติ (Properties):** symmetry/asym, coupling, mobilities, stiffness
    
- **ศักยภาพ (Potential):** สิ่งที่ “อยากให้เกิด”/แรงขับ (ในโค้ดคือ `V` และ `s` tilt)
    
- **ความขัดแย้ง/แรงต้าน (Conflict/Resistance):** ค่าใช้จ่าย/ความต้านทาน (ในโค้ดคือ gradient penalty + ความชันที่ทำให้ต้อง backtrack)
    
- **การไหล/การเป็น (Flow/Activity):** dynamics ที่แปลงศักยภาพเป็นการเปลี่ยนแปลงจริง
    
- **ผลลัพธ์:** attractor/phase
    
- **ผลกระทบ:** value/conflict ต่อระบบรวม
    

**ตรงนี้คือหัวใจที่ทำให้ “สิ่งหนึ่งคืออะไร” อธิบายได้**  
เพราะเราไม่ได้เริ่มที่ “สมดุลเลย” แต่เริ่มที่ “มันต้องผ่านอะไรถึงจะเป็นอยู่ได้”

---

## 3) ตาราง Map ที่ต้องมีเป็น “หน้าแรกของ public doc”

นี่คือ “ตารางแม่” ที่จะทำให้ทุกอย่างไม่หลงทิศ (และเป็นจุดเริ่มของอีกหลายร้อยแชท)

### 3.1 แนวนอน: ระบบเปิด (Extrovert)

|ระบบรวม|คำอธิบายคนทั่วไป|ของจริงใน UET ตอนนี้ (ต้องอ้างกับไฟล์/โค้ด)|
|---|---|---|
|สนาม|ภูมิประเทศ/กฎของโลก|Ω functional + params (`beta,kC,kI,potC,potI,L,N,dt`)|
|ระบบ|สิ่งที่กำลังเกิด|fields `C(x,y,t), I(x,y,t)`|
|กลไก|กติกาการเปลี่ยน|solver step + accept/reject + backtrack|
|แรง|ผลัก/ดึงให้เปลี่ยน|“ความชันของ Ω” (functional derivative) + diffusion-like term|
|ผลลัพธ์|ลงเอยแบบไหน|phase label (`BIAS_C/BIAS_I/SYM`) + pattern|
|ผลกระทบ|ทำให้โลกเปลี่ยนยังไง|metrics ที่ไปปรับสนาม/เงื่อนไข (ยังเป็น roadmap)|
|feedback|วงจรควบคุม|ยังต้องนิยามเชิงปฏิบัติ (v0.9 layer)|

### 3.2 แนวตั้ง: การดำรงอยู่ (Introvert)

|การเป็นสิ่งหนึ่ง|แปลไทยง่ายๆ|ของจริงใน UET ตอนนี้|
|---|---|---|
|Constraints|อยู่ในกรอบ|domain/grid/bc + coercivity + acceptance|
|Necessity|ต้องไม่พัง|Ω monotone, dt ladder, fail flags|
|Properties|ลักษณะนิสัย|asym, coupling strength, stiffness|
|Potential|แรงขับ|quartic potential params (`a, delta, s`) + coupling `beta`|
|Conflict|ต้าน/ราคา|grad energy (`kC,kI`) + backtracks density|
|Flow|กระบวนการ|update rule + mobilities/M|
|Outcome|สิ่งที่เป็น|final pattern + attractor|
|Impact|ต่อโลก|value/conflict metrics (ต้อง define operational)|

> นี่คือ “หน้าตาราง” ที่มึงบอกว่าอยากได้ก่อนถึงจะเข้าใจว่ากำลังทำอะไรอยู่

---

## 4) ประโยคที่ต้องเขียนให้คนทั่วไปเข้าใจ (ไม่ต้องเห็นสมการก่อน)

**สรุปที่ควรอยู่หน้าแรก (Public):**

- “UET เป็นเครื่องจำลองที่ใช้ **สนาม Ω** เป็นภาษาเดียวในการบอกว่า ‘ระบบควรไหลไปไหน’”
    
- “**สิ่งหนึ่ง** ใน UET คือรูปแบบของสถานะ (pattern) ที่สามารถดำรงอยู่ได้ภายใต้ข้อจำกัด”
    
- “**สมดุล** ไม่ใช่เลขเดียว แต่คือ ‘หลุม/attractor’ และ ‘ความทนทานต่อ seed’ (basin robustness)”
    
- “เราจึงใช้ seed หลายค่าเพื่ออ่าน ‘รูปร่างของสนาม’ ว่าโลกนี้ชอบลงเอยแบบไหน”
    

นี่จะปูพื้นให้คนดู YouTube ไม่หลุด

---

## แผ่นเขียนระยะยาว (Roadmap การเรียบเรียงเป็นระบบเดียว)

## Layer A: Public Narrative & Demo (คนทั่วไปต้องเข้าใจ)

**เป้าหมาย:** มี “เดโม 1 หน้า” ที่เห็นภาพเหมือน YouTube

- นิยาม: สิ่งหนึ่ง / สนาม / แรง / สมดุล
    
- Demo card: snapshot + animation + 3D surface (จาก state/Ω-density) + คำอธิบาย 5 บรรทัด
    
- Gallery: 3–5 demo ที่เป็น archetype (ไม่ใช่ร้อยกราฟ)
    

**เกณฑ์ผ่าน:** คนทั่วไปดูแล้วตอบได้ว่า BIAS_C/BIAS_I คือ “ภาพอะไร”

## Layer B: Modeling Interface (MI) สำหรับคนเอาไปใช้โดเมนใหม่

**เป้าหมาย:** ใครมีโจทย์ใหม่ “แปลงเป็น UET” ได้แบบขั้นตอนเดียว

- MI card template (2 แกน)
    
- วิธีเลือกตัวแปร/ข้อจำกัดที่เป็นจริง (ไม่ sweep หลุดโลก)
    
- วิธีอ่านผล: outcome + impact metrics
    

**เกณฑ์ผ่าน:** คนทำ matrix ได้โดยไม่ต้องถามกลับว่า “จะใส่อะไร”

## Layer C: Math Core (สำหรับวิชาการ)

- นิยาม Ω (C-only / C-I) + decomposition (potential/coupling/gradient)
    
- dynamics, monotonicity gate, Lyapunov proof, coercivity/ stability
    
- dimensional analysis + scaling + what is calibratable
    

**เกณฑ์ผ่าน:** ส่งเป็น paper section ได้

## Layer D: Implementation Spec (ทำให้ reproducible)

- repo structure, configs, matrices, validators, aggregators
    
- “what counts as PASS” และ “why”
    
- regression & CI (ค่อยกลับไปแตะ infra ทีหลังเมื่อ Layer A/B เสร็จ)
    

## Layer E: Bridge Program (สิ่งที่มึงตั้งโจทย์ v0.9)

(ทำได้ แต่ต้องอยู่ “หลัง” Layer A/B/C)

- Thermodynamics reinterpretation (สมดุล/เอนโทรปี/การไหล)
    
- Information theory mapping (นิยาม operational ของ information ในระบบ)
    
- Quantum analogy (ถ้ามีในไฟล์ UET)
    
- Game dynamics (potential game vs conflict regimes)
    
- Einstein/Lambda (วิธีเชื่อมเชิงสเกล/หน่วย/observable)
    

---

## Next Step (งานถัดไปในแชทนี้ โดยไม่กระโดด)

ถัดจากข้อความนี้ กูจะทำ “ชิ้นที่ 1” ให้จบก่อนตามที่มึงสั่ง:

✅ **เขียนเอกสารย่อย 1 ตอน**:  
**“Dual-Equilibrium + Two-Axis Reading (System × Existence) — Canonical Spec v0.9 Draft (Part 1)”**  
ประกอบด้วย:

1. นิยามคำ (สิ่งหนึ่ง/สนาม/แรง/สมดุล/ผลกระทบ)
    
2. ตาราง map 2 แกน (แบบที่ด้านบน) แต่ละเอียดขึ้นระดับ “เอาไปใช้งานได้”
    
3. ชี้ว่าใน harness ตอนนี้ “มีอะไรแล้ว/ขาดอะไร” เฉพาะส่วนที่เกี่ยวกับการสื่อสาร/เดโม (ไม่พาไหลไป infra)
    

ถ้ามึงโอเค เดี๋ยวข้อความถัดไปกูเริ่ม “Part 1” แบบเขียนเป็นเอกสารจริง (ทั้งเวอร์ชันวิชาการ + เวอร์ชันภาษาคน) แล้วเราค่อยไล่ Part 2, Part 3 ไปเรื่อย ๆ จนเป็นชุด public ได้จริง.

---
# 000.01
## TL;DR

ต่อจากนี้ “แกนเอกสารระยะยาว” ของ UET ต้องเริ่มจาก **ภาษากลาง 2 ชั้นของสมดุล** + **ตารางอ่านระบบ 2 แกน** แล้ว “ผูก” เข้ากับ **ของจริงที่รันอยู่ตอนนี้ (Ω + dynamics + labels)** ให้แน่นก่อน

- **Introvert (ระบบเล็ก/การเป็นสิ่งหนึ่ง):** input → processing → output
    
- **Extrovert (ระบบเปิด/ระบบรวม):** สนาม → ระบบ → กลไก → แรง → ผลลัพธ์ → ผลกระทบ → feedback
    
- แล้ว map ลง **UET Core ปัจจุบัน**: `C_only` และ `C_I` ที่มี Ω แบบ potential + coupling + gradient penalty และ solver แบบ **semi-implicit + accept/reject (บังคับ Ω ลด)**
    

จากนั้นค่อยทำ “เดโมแบบ YouTube” โดยระบุ **สัญญา output** ว่าต้อง export อะไร (state snapshots/terrain/animation) — ไม่ใช่เริ่มจาก heatmap 2D

---

## Insight

ตอนนี้สิ่งที่เรากำลัง “เขียนให้โลกเข้าใจ” ไม่ใช่สมการใหม่ แต่คือ “คู่มือแปลภาษา”:

> **สิ่งหนึ่งคืออะไร** (Introvert)  
> **ระบบรวมคืออะไร** (Extrovert)  
> **สมดุลคืออะไร** (ไม่ใช่เลขจุดเดียว แต่คือ attractor + basin robustness)  
> และทั้งหมดนี้ “เท่ากับ” อะไรใน Ω/solver/ผลลัพธ์ที่รันได้จริง

นี่คือฐานที่ทำให้ UET กลายเป็น public/open-source ได้แบบไม่งง

---

## Canonical Spec v0.9 Draft — Part 1

## Dual-Equilibrium + Two-Axis Reading (System × Existence)

## 1) เป้าหมายของ Part 1

Part 1 มีหน้าที่ “ล็อกนิยาม” ให้ทุกคนคิดตรงกันก่อน:

1. **สมดุลมี 2 ชั้น**: Introvert vs Extrovert
    
2. **สิ่งหนึ่ง (entity)** และ **สนาม (field/space)** คืออะไร
    
3. **Seed สำคัญยังไง** (และไม่ใช่พระเอกของเรื่อง)
    
4. Map ลงของจริงที่รันอยู่ตอนนี้: Ω, potential, coupling, gradient penalty, solver, labels
    
5. กำหนด “สิ่งที่ต้อง export” เพื่อทำเดโมแบบ YouTube (ภาพ/terrain/animation)
    

> Part 1 ยังไม่ไป thermodynamics/quantum/Einstein — เอา “แกนภาษา + ของจริงในโค้ด” ให้แน่นก่อน

---

## 2) นิยามแกนกลาง (คำที่ต้องใช้ซ้ำทั้งโปรเจกต์)

### 2.1 Entity / สิ่งหนึ่ง (Introvert view)

**นิยาม (เชิงระบบ):**  
สิ่งหนึ่ง = _(State, Constraints, Mechanism)_ ที่ทำ input→process→output ได้

- **State**: ตัวแปรที่บรรยาย “สิ่งนั้นกำลังเป็นอะไรอยู่”
    
- **Constraints**: ขอบเขต/ข้อจำกัดที่ทำให้การเป็นอยู่ไม่พัง
    
- **Mechanism**: กติกาการเปลี่ยน state
    

> ใน UET ปัจจุบัน “สิ่งหนึ่ง” สามารถตีความเป็น _รูปแบบของ field_ (pattern/state configuration) ที่ดำรงอยู่ได้ภายใต้ Ω และข้อจำกัด

### 2.2 Field / สนาม (Extrovert view)

**นิยาม (เชิงโลก):**  
สนาม = _(กฎ + ภูมิประเทศ + เงื่อนไขภายนอก)_ ที่บอกว่า state “ควรไหลไปทางไหน”

> ใน UET สนามถูกเขียนด้วย **energy functional Ω** + พารามิเตอร์ + boundary/geometry

### 2.3 Equilibrium / สมดุล (สองชั้น)

- **Introvert equilibrium:** ระบบเล็ก “เข้าที่/คงรูป” (เปลี่ยนยาก)
    
- **Extrovert equilibrium:** ระบบรวม “จัดระเบียบ/กระจาย/ไหลเวียน” แบบระบบเปิด โดยดูผลกระทบและ feedback
    

### 2.4 Seed

Seed = initial condition ของ state

- Seed ไม่ใช่ “ความจริงของระบบ”
    
- Seed คือ “การสุ่มจุดปล่อยลูกบอล” เพื่ออ่านว่า **สนามมีหลุมกี่แบบ** และ **หลุมไหนกินพื้นที่มาก** (basin robustness)
    

---

## 3) ตารางอ่านระบบ 2 แกน (Framework → ใช้งานจริง)

## 3.1 แกนแนวนอน: Extrovert / ระบบเปิด (Field→System→Mechanism→Force→Result→Impact→Feedback)

|โหนด|ภาษาเข้าใจง่าย|ใน UET ปัจจุบัน (ของจริง)|
|---|---|---|
|สนาม (Field)|ภูมิประเทศที่บอกว่าอะไร “ไหลลง”|**Ω functional** + params (`pot, beta, kC,kI,kappa, L,N,…`)|
|ระบบ (System)|สิ่งที่กำลังเกิดขึ้นในโลกนั้น|`C(x,y,t)` และ/หรือ `I(x,y,t)` บนกริด|
|กลไก (Mechanism)|กติกาการเปลี่ยนแปลง|solver: semi-implicit + backtracking|
|แรง (Force)|สิ่งที่ผลัก/ดึง|“ความชันของ Ω” (functional derivative)|
|ผลลัพธ์ (Result)|ระบบลงเอยแบบไหน|phase label: `BIAS_C / BIAS_I / SYM` + pattern|
|ผลกระทบ (Impact)|ต่อระบบรวม|metrics ที่แปลเป็น value/conflict (กำหนดเชิงปฏิบัติใน Part 2)|
|Feedback|ผลกระทบย้อนกลับไปเปลี่ยนสนาม|roadmap: Ω/params เปลี่ยนตามผล (ยังไม่ใช่แกนหลักของ harness ตอนนี้)|

## 3.2 แกนแนวตั้ง: Introvert / กระบวนการดำรงอยู่ (Constraints→Necessity→Properties→Potential/Conflict/Flow→Outcome→Impact)

|ชั้น|ภาษาเข้าใจง่าย|ใน UET ปัจจุบัน|
|---|---|---|
|Constraints|กรอบที่ห้ามพัง|domain/grid/BC + coercivity checks|
|Necessity|สิ่งที่ต้องเกิดเพื่ออยู่รอด|Ω ต้องลด (Lyapunov-like monotone gate), ไม่ NaN/Inf|
|Properties|บุคลิกของระบบ|asym/coupling/stiffness/mobility|
|Potential (P)|แรงขับ “อยากให้เกิด”|quartic potential + tilt `s`|
|Conflict/Resistance (R)|แรงต้าน/ราคาที่ต้องจ่าย|gradient penalty (`kC,kI,kappa`) + backtracks|
|Flow/Activity (J)|กระบวนการที่ทำให้เปลี่ยนจริง|time stepping + mobility (`M, MC, MI`)|
|Outcome|สิ่งที่ได้จริง|attractor/phase/pattern|
|Impact|ตีความเป็น “คุณค่า/ความขัดแย้ง”|ต้อง define operational metrics (Part 2)|

> “ศักยภาพ–ความขัดแย้ง–การไหล” (P/R/J) คือสะพานที่ทำให้เฟรมเวิร์กของมึงไม่ลอย และไปจับกับ Ω/dynamics ได้จริง

---

## 4) ผูกเข้าของจริง: UET Core ปัจจุบัน (Ω + dynamics)

### 4.1 แบบจำลองที่มีอยู่จริง (2 รุ่น)

1. **C_only model**
    
2. **C_I model** (C กับ I couple กัน)
    

### 4.2 Ω (Energy functional) — เวอร์ชันที่รันอยู่จริงในโค้ด

#### (A) C_only

**Discrete form (ในโค้ด):**  
[  
\Omega(C)=\sum_{grid} V(C),dx^2+\frac{1}{2}\kappa,G(C)  
]  
โดย (G(C)) คือ spectral gradient energy (สอดคล้อง periodic spectral operator)

#### (B) C_I

**Discrete form (ในโค้ด):**  
[  
\Omega(C,I)=\sum_{grid}\Big(V_C(C)+V_I(I)-\beta,C,I\Big),dx^2  
+\frac{1}{2}k_C,G(C)+\frac{1}{2}k_I,G(I)  
]

> นี่คือ “สนาม” ในความหมาย extrovert: ภูมิประเทศของระบบ

### 4.3 Potential ที่ใช้จริง: Quartic + tilt

ศักย์ (per-field) ที่ใช้จริง:  
[  
V(u)=\frac{1}{2}a u^2+\frac{1}{4}\delta u^4 - s,u  
]  
และอนุพันธ์:  
[  
V'(u)=a u+\delta u^3-s  
]

- (a,\delta): รูปทรงหลุม
    
- (s): tilt (เอนสนามให้ “เข้าข้าง”)
    
- (\beta): coupling C–I (แรงดึงดูด/ผลักเชิงปฏิสัมพันธ์)
    
- (k_C,k_I,\kappa): ความต้านการเปลี่ยนแปลงเชิงพื้นที่ (ความเรียบ/ความหนืดเชิงโครงสร้าง)
    

### 4.4 Dynamics ที่ใช้จริง: semi-implicit + monotone Ω gate

โค้ดใช้แนวคิด:

- **reaction/coupling explicit**
    
- **diffusion (gradient penalty) semi-implicit ใน spectral space**
    
- **accept/reject + dt backtracking** เพื่อบังคับให้ Ω ไม่เพิ่ม (ภายใน tolerance)
    

ตัวอย่างใน C_I (เชิงรูปแบบ):

- สร้าง RHS:  
    [  
    rhs_C = C - dt,MC,(V_C'(C) - \beta I)  
    ]  
    [  
    rhs_I = I - dt,MI,(V_I'(I) - \beta C)  
    ]
    
- แล้วแก้ส่วน diffusion แบบ semi-implicit (spectral solve) ด้วยพารามิเตอร์ (dt,MC,k_C), (dt,MI,k_I)
    

**กติกา “อยู่รอด” (Necessity):**  
[  
d\Omega=\Omega_{cand}-\Omega_{n}  
]  
รับ candidate ถ้า  
[  
d\Omega \le \text{tol_abs}+\text{tol_rel}\cdot\max(1,|\Omega_n|)  
]  
ไม่งั้น backtrack ลด dt แล้วลองใหม่

> นี่คือ “สิ่งที่มึงถามว่าลูกบอลไหลตามความชันได้ไหม” — ได้ และมันถูกบังคับให้ไหลลง Ω ด้วย gate นี้

---

## 5) สิ่งที่ Part 1 ต้อง “ล็อกความเข้าใจ” เรื่อง 2D/3D

### 5.1 อย่าสับสน 2D สองแบบ

- **2D parameter map** (เช่น beta×s) = เลือกหมุนปุ่ม 2 ตัวเพื่อดู phase map
    
- **2D spatial solver** (x,y) = implementation ปัจจุบันรันบนกริด 2D จริง
    

### 5.2 “ไม่ติดคุก 2D” แต่ต้องพูดความจริง

- ทฤษฎี/เฟรมเวิร์กไม่ได้ห้าม 3D
    
- แต่ _โค้ดตอนนี้_ เป็น 2D spatial (เพราะ operator เป็น spectral 2D)
    
- อย่างไรก็ตาม “ภาพ 3D แบบ YouTube” ทำได้ทันทีจาก 2D field โดย plot เป็น surface (x,y,z) หรือ plot Ω-density เป็น terrain
    

> ดังนั้น **เดโมแบบ terrain 3D** ไม่ต้องรอ 3D spatial solver  
> แต่ **ถ้าจะทำ 3D spatial จริง** ค่อยเป็น Part Implementation หลังจากภาษา+เดโมนิ่งแล้ว

---

## 6) สัญญา “Public Demo Output” (สิ่งที่ต้องมีเพื่อให้คนทั่วไปเข้าใจ)

นี่คือส่วนที่ทำให้ UET “ไม่กลายเป็นกราฟอ่านไม่ออก”:

### 6.1 Demo Card (ขั้นต่ำ 1 ใบต้องเล่าเรื่องได้)

**สำหรับ 1 case (1 parameter set)** ต้องมี:

1. `state_start` / `state_end` ของ C และ I
    
2. `evolution.gif` หรือ snapshots 10–20 เฟรม
    
3. `terrain_omega_density` หรือ surface ของ C/I (ภาพแบบมึงแนบ)
    
4. ตัวชี้วัด 2 เส้นพอ: Ω(t) และ bias(t)
    

> สำคัญ: **state snapshots** คือของที่ตอนนี้ยัง “ขาด” ในการสื่อสาร (แม้ระบบรันจะถูก)

### 6.2 บทบาทของ heatmap 2D

heatmap ใช้เป็น “แผนที่ชี้ทาง” หลังจากคนเห็น demo card แล้วเท่านั้น  
ไม่ใช่ของที่ใช้สอนคนให้เข้าใจ UET ตั้งแต่ศูนย์

---

## 7) Checklist: ตอนนี้มีแล้วอะไร / ขาดอะไร (เฉพาะในกรอบ Part 1)

### มีแล้ว (แข็งแรง)

- นิยาม Ω แบบ potential+coup+grad (รันจริง)
    
- solver ที่บังคับ Ω monotone (accept/reject+backtrack)
    
- summary/timeseries (Ω(t), mean_C, mean_I, bias_CI ฯลฯ)
    
- phase labels/validators (BIAS_C/BIAS_I/SYM) สำหรับการทำ phase map
    

### ขาด (เพื่อให้ “เข้าใจง่ายแบบ YouTube”)

- **การ dump field snapshots ต่อเวลา** (C/I เป็น array ต่อ step)
    
- script ทำ **terrain/animation** จาก snapshots
    
- “Demo Card” มาตรฐาน (หนึ่งหน้าจบ) + gallery index
    

> นี่คือ “แกนงาน public ที่แท้จริง” ก่อนจะไป thermodynamics/quantum/Einstein

---

## Plain-Language Interpretation (เวอร์ชันคนทั่วไป)

- ตอนนี้เรามี “โลก” ที่นิยามด้วยสนาม Ω
    
- เราปล่อย “สิ่งหนึ่ง” (seed) ลงไป แล้วมันจะไหลลงหลุม
    
- หลุมแต่ละแบบคือ “สมดุล/รูปแบบชีวิตของระบบ”
    
- เราสุ่มหลาย seed เพื่ออ่านว่าโลกนี้ “เอียงไปทางไหนโดยธรรมชาติ”
    
- แต่ถ้าไม่โชว์ภาพตอนมันไหล คนจะไม่เข้าใจ  
    ดังนั้นงานต่อไปคือทำให้ระบบ “ถ่ายวิดีโอการไหล” ได้
    

---

## Next Step (Part 2 ที่จะเขียนต่อทันที)

Part 2 จะทำ 2 อย่างแบบลงมือใช้งานได้:

1. **Operational definitions** ของ “คุณค่า vs ความขัดแย้ง” (Impact layer)
    - ต้องนิยามเป็น metric ที่คำนวณได้จาก state/Ω/timeseries (ไม่ใช่คำสวยๆ)
        
2. **MI Card (Modeling Interface)**: วิธีแปลงโจทย์โดเมนใหม่ให้เข้ากับ 2 แกนนี้
    - โดยยึด UET ปัจจุบันเป็นหลัก แล้วใช้ framework เก่าเป็น “ภาษาอธิบาย” ไม่ใช่บังคับสมการ

ถ้ามึงพิมพ์ “ต่อ” อีกครั้ง กูจะเริ่ม Part 2 แบบเป็นเอกสารจริง:

- นิยาม Value/Conflict เป็น metric เชิงปฏิบัติ
- แล้วผูกมันกับ output ที่ “ต้อง export” (เพื่อเดโม) และกับ validator ที่มีอยู่แล้ว

---
# 000.02
## TL;DR

Part 2 จะทำให้ “เฟรมเวิร์กของมึง” กลายเป็น **ของที่คำนวณได้จริง** ใน harness ปัจจุบัน โดยนิยาม 2 อย่างแบบ operational:

- **Value (คุณค่า)** = ระบบ “จัดระเบียบ/คงรูป/ใช้พลังงานต่ำ” ได้แค่ไหน
    
- **Conflict (ความขัดแย้ง)** = ระบบ “ต้านกันเอง/แตกเป็นรอยต่อ/แกว่ง/ต้อง backtrack เยอะ” แค่ไหน
    

แล้วผูกเข้ากับ output ที่เรามี/ต้องเพิ่ม (โดยเฉพาะ **state snapshots** เพื่อทำเดโมแบบ YouTube)

---

## Insight

ตอนนี้เราจะไม่พูด “คุณค่า/ความขัดแย้ง” แบบปรัชญาอีกแล้ว  
เราจะให้มันมี **สูตรวัดได้** จากสิ่งที่ UET รันอยู่จริง:

- จาก **Ω decomposition** (potential/coupling/gradient)
    
- จาก **พฤติกรรม dynamics** (Ω monotone, backtracking, relax)
    
- จาก **โครงสร้างเชิงพื้นที่** (ต้องมี snapshots)
    

นี่คือสะพานที่ทำให้ “ระบบรวม/สิ่งหนึ่ง” เข้าใจง่ายและใช้งานได้จริง

---

## Canonical Spec v0.9 Draft — Part 2

## Operational Semantics: Value vs Conflict + MI Card (Modeling Interface)

## 1) คำจำกัดความแบบคำนวณได้ (Operational Definitions)

### 1.1 สิ่งที่เรามีอยู่แล้วในผลรัน (ตอนนี้)

จาก summary/timeseries ปัจจุบัน เรามักมี (หรือทำให้มีได้ไม่ยาก):

- ( \Omega(t) ), ( \Omega_{\text{final}} )
    
- ตัวชี้วัด bias/phase (เช่น BIAS_C/BIAS_I/SYM)
    
- ( t_{\text{relax}} ) (แม้ตอนนี้บางเคสไม่ informative)
    
- จำนวนครั้ง backtrack / dt reductions (ถ้ายังไม่ log ให้เพิ่ม)
    

> แต่ “สิ่งที่ยังขาดเพื่อทำ YouTube-level” คือ **state snapshots** ของ C/I (และอาจ Ω-density) ต่อเวลา

---

## 2) นิยาม “Value” และ “Conflict” (วัดได้จริง)

### 2.1 Value — คุณค่า (จัดระเบียบ/เสถียร/ประหยัด)

ให้ยึดหลัก: **คุณค่า = การเข้าสู่รูปแบบที่เสถียรด้วยต้นทุนต่ำ**

เรานิยาม “Value score” ได้หลายระดับ (เลือกใช้ตามว่ามีข้อมูลแค่ไหน)

#### (V1) Energy-based Value (ใช้ได้ทันทีถ้ามี Ω)

- **ค่าเสถียรปลายทาง**:  
    [  
    V_E = -\Omega_{\text{final}}  
    ]
    
- หรือ **การพัฒนา**:  
    [  
    V_{\Delta E} = \Omega(0) - \Omega_{\text{final}}  
    ]  
    แปล: ยิ่งลด Ω ได้มาก → ยิ่ง “จัดระเบียบ” ตามสนามได้มาก
    

> ข้อดี: คำนวณง่าย ใช้ได้ทันที  
> ข้อควรระวัง: ต้อง normalize ถ้าจะเทียบข้ามสเกล/พารามิเตอร์

#### (V2) Robustness Value (ของระบบรวม: basin robustness)

สำหรับ sweep/หลาย seed:  
[  
V_R = \max{P(\text{BIAS}_C),,P(\text{BIAS}_I),,P(\text{SYM})}  
]  
แปล: ถ้าระบบ “ลงเอยแบบเดียวกันบ่อย” → ระบบมีคุณค่าด้านความแน่นอน/ทน seed

#### (V3) Order/Structure Value (ต้องมี snapshots)

กำหนด “order” แบบเข้าใจง่ายจากภาพ:

- ถ้า system เกิด pattern ชัด (domain/structure) และนิ่ง → value สูง
    
- วิธีคำนวณเชิงรูปธรรม (ตัวอย่าง):
    
    - spatial variance ของ field
        
    - spectral energy concentration
        
    - domain-size / correlation length
        

> อันนี้คือแกนที่ทำให้คนดูภาพแล้ว “เข้าใจทันที” ว่าเกิดอะไร

---

### 2.2 Conflict — ความขัดแย้ง (ต้านกันเอง/แกว่ง/รอยต่อเยอะ/ต้องจ่ายราคา)

หลัก: **conflict = ความยากในการ reconcile แรงผลักหลายทิศให้ลงหลุมเดียวกัน**

#### (C1) Gradient-cost Conflict (ต้องมี Ω decomposition หรือคำนวณเพิ่ม)

ให้แยก:  
[  
\Omega = \Omega_{\text{pot}} + \Omega_{\text{coup}} + \Omega_{\text{grad}}  
]  
แล้วนิยาม:  
[  
C_G = \Omega_{\text{grad, final}}  
]  
แปล: รอยต่อ/ความไม่เรียบ/ความตึงเครียดเชิงพื้นที่สูง → conflict สูง

นี่แมพตรงกับ “ความขัดแย้ง” ของเฟรมเวิร์กมึงแบบสวยมาก เพราะมันคือ “ราคาที่ต้องจ่ายเพื่ออยู่ร่วมกันในสนามเดียว”

#### (C2) Dynamic-friction Conflict (ใช้ได้ทันทีถ้า log backtracking)

[  
C_F = #(\text{reject/backtrack}) \quad \text{หรือ}\quad \sum \log\left(\frac{dt_{\text{prev}}}{dt_{\text{accepted}}}\right)  
]  
แปล: ถ้าระบบต้องลด dt บ่อยเพื่อไม่ให้ Ω เพิ่ม → dynamics “ฝืด/ต้าน/ไม่ลงรอย”

#### (C3) Non-settling Conflict (จาก timeseries)

วัด “ความแกว่ง”:  
[  
C_O = \text{Var}\big(\Omega(t)\ \text{ช่วงท้าย}\big) + \text{Var}\big(\text{bias}(t)\ \text{ช่วงท้าย}\big)  
]  
แปล: ช่วงท้ายยังไม่นิ่ง → conflict สูง

#### (C4) Multi-attractor Conflict (ของระบบรวม)

สำหรับ sweep:  
[  
C_M = 1 - V_R  
]  
แปล: seed เปลี่ยนแล้ว outcome เปลี่ยนง่าย → ระบบ “มีหลายหลุมแข่งกัน” → conflict ในเชิงระบบรวมสูง

---

## 3) “Value vs Conflict” ต้องสรุปเป็นอะไรให้ public เข้าใจง่าย

ต่อให้มีสูตร พอ public ต้องมี 2 อย่าง:

### 3.1 Value–Conflict Plane (แผนที่ 2 มิติที่คนอ่านออก)

แทนที่จะให้ดูกราฟมั่ว ๆ ให้สรุป 1 รูปแบบนี้:

- แกน X = Value (เช่น (V_{\Delta E}) หรือ (-\Omega_{\text{final}}))
    
- แกน Y = Conflict (เช่น (C_G) หรือ (C_F))
    

แล้วแบ่งเป็น 4 เขต:

1. **High Value, Low Conflict** = “จัดระเบียบดี” (sweet spot)
    
2. **High Value, High Conflict** = “ได้ผลแต่ต้องจ่ายแพง/รอยต่อเยอะ”
    
3. **Low Value, Low Conflict** = “นิ่งแต่ไร้พลัง/ไร้โครงสร้าง”
    
4. **Low Value, High Conflict** = “วุ่นวาย/แตกแยก/ไม่ลงหลุม”
    

นี่แหละที่เป็น “ภาษาคนทั่วไป” โดยไม่ทิ้งความเป็นวิชาการ

### 3.2 Demo Card ต้องโชว์ “ภาพ” รองรับจุดบนแผนที่

ทุกจุดใน plane ต้องคลิกไปดู:

- snapshot start/end
    
- evolution gif
    
- terrain Ω-density / surface C หรือ I
    

> ไม่งั้นมันกลับไปเป็นกราฟที่มึงด่าเหมือนเดิม

---

## 4) MI Card — วิธีทำให้คนสร้างโมเดลโดเมนใหม่ได้ (โดยไม่มั่ว)

MI Card คือ “แบบฟอร์ม” ที่บังคับให้คนไม่กระโดดข้ามเฟรมเวิร์ก

### MI Card (Canonical Template)

#### A) Entity (Introvert)

1. **สิ่งหนึ่งคืออะไร** ในโดเมนนี้?
    
2. state ของมันคืออะไร? (แนะนำ: เลือก 1–2 field ก่อน)
    
3. constraints ที่จริงในโลกคืออะไร? (ห้ามสวีปหลุดข้อจำกัด)
    

#### B) World (Extrovert)

4. สนาม/สิ่งแวดล้อมคืออะไร? (สิ่งที่ “บังคับ” ให้ระบบต้องจัดรูป)
    
5. มี “แรง” อะไรบ้าง? (ผลัก/ดึง/ต้าน)
    

#### C) Map เข้า UET (ของจริง)

6. **C กับ I แปลว่าอะไร** ในโดเมนนี้ (หรือใช้ C-only)
    
7. **Potential (P)** มาจากอะไร (อะไรคือ “แรงขับ”)?
    
8. **Conflict/Resistance (R)** มาจากอะไร (อะไรคือ “ต้นทุน/รอยต่อ/การต้าน”)?
    
9. **Flow (J)**: dynamics/เวลาในโดเมนนี้เทียบกับ dt ยังไง? (อย่างน้อยต้องกำหนดสเกล)
    

#### D) Observables

10. ผลลัพธ์ที่อยากได้คืออะไร? (phase? value? conflict? pattern?)
    
11. จะทำ demo ยังไงให้คนเห็นภาพ? (ต้อง export อะไร)
    

#### E) Sweep Plan (ไม่ให้มั่ว)

12. เลือก sweep แค่ 2 แกนก่อน + เหตุผล (เพราะต้องทำ phase map ไม่ใช่สุ่ม 10 มิติ)
    

---

## 5) ส่วนที่ต้อง “เพิ่ม” ใน harness เพื่อให้ MI Card ใช้งานจริง (สำคัญ)

เพื่อให้ “YouTube-level” เกิดจริง เราต้องเพิ่ม output 1 กลุ่ม:

### 5.1 State Snapshot Export (ขั้นต่ำ)

- บันทึก `C` และ `I` ทุก ๆ N steps (หรือเวลา logscale)
    
- เก็บเป็น `.npz` หรือ `.npy`
    
- export frame `.png` สำหรับทำ gif/mp4
    

### 5.2 Ω Decomposition Export (ถ้าจะทำ Value/Conflict ให้คม)

ถ้าตอนนี้ summary มีแค่ Ω รวม ให้เพิ่ม:

- ( \Omega_{\text{pot}} )
    
- ( \Omega_{\text{coup}} )
    
- ( \Omega_{\text{grad}} )
    

นี่จะทำให้ “Conflict = grad cost” อธิบายได้ทั้งคนทั่วไปและวิชาการ

### 5.3 Backtracking Stats (Conflict เชิง dynamics)

log:

- rejects count
    
- dt ladder events
    
- acceptance ratio
    

---

## Math/Physics Interpretation (แก่นเดียว)

- **Value** = “ลด Ω ได้ดี + outcome robust”
    
- **Conflict** = “gradient energy สูง + friction/backtracking สูง + multi-attractor สูง”  
    ทั้งหมดนี้เป็น **ตัวเลขจาก Ω และ dynamics** ไม่ใช่คำลอย ๆ
    

---

## Plain-Language Interpretation

- คุณค่า = โลกจัดระเบียบได้ โดยไม่ต้องปะทะกันแรง
    
- ความขัดแย้ง = โลกปะทะกันเยอะ ต้องฝืนเยอะ มีรอยต่อเยอะ หรือเปลี่ยน seed แล้วจบไม่เหมือนเดิม
    

---

## Next Step (Part 3 ที่จะทำต่อ)

Part 3 จะเป็น “Public Demo Blueprint” แบบที่มึงอยากได้จริง:

- รูปแบบหน้าเดียว (Demo Card) ที่ต้องมีภาพ/terrain/animation
    
- วิธีเลือก 3–5 archetype demos (ไม่ใช่ร้อยกราฟ)
    
- วิธีทำ gallery ให้คนคลิกแล้วเข้าใจ “สนาม/หลุม/แรง/สมดุล” ทันที
    

แต่ก่อนไป Part 3 กูขอ “ล็อก” การตัดสินใจ 1 อย่าง (ไม่ใช่โจทย์ใหม่ เป็นการเลือก metric):

> ใน Part 2 นี้ มึงอยากให้ **Conflict** ยึด “Gradient cost” เป็นแกนหลักไหม?  
> เพราะมันสอดคล้อง framework มึงที่สุดและอธิบายเป็นภาพได้ง่ายสุด

ถ้ามึงตอบ “เอา” กูจะเขียน Part 3 ต่อโดยสมมติว่าเราจะ export Ω_grad + snapshots เป็นมาตรฐานของเดโมทันที


---
# 000.03

## TL;DR

Part 3 = “**Blueprint เดโมแบบ YouTube**” ของ UET: ไม่เริ่มที่ matrix/heatmap แต่เริ่มที่ **การเล่าเรื่องด้วยภาพของ state** (C/I) + **terrain ของ Ω (หรือ Ω-density)** + **แผนที่ Value–Conflict** แล้วค่อยใช้ sweep เป็น “แผนที่นำทาง” ทีหลัง

เป้าหมายคือ: คนทั่วไปดู **เดโม 1 หน้า** แล้วตอบได้ว่า

- “สิ่งหนึ่งคืออะไร”
    
- “สนามคืออะไร”
    
- “สมดุลคืออะไร”
    
- “BIAS_C/BIAS_I/SYM คือภาพแบบไหน”  
    โดยไม่ต้องรู้คณิต
    

---

## Canonical Spec v0.9 Draft — Part 3

## Public Demo Blueprint: จากสมการ → ภาพที่มนุษย์เข้าใจ (YouTube-level)

## 1) หลักการออกแบบเดโม (ห้ามหลงกลับไปกราฟที่คนไม่เข้าใจ)

### 1.1 คนทั่วไป “เข้าใจจากภาพ” ก่อน “เข้าใจจากสถิติ”

ลำดับที่ถูกต้องคือ:

1. **เห็น state** (C/I) ว่ามันเป็นรูปอะไร
    
2. **เห็นการไหลตามเวลา** (evolution)
    
3. **เห็นสนาม/หลุม** (terrain ของ Ω หรือ Ω-density)
    
4. ค่อยสรุป **Value/Conflict/Phase label**
    
5. สุดท้ายค่อยใช้ heatmap/sweep เป็น “แผนที่รวม”
    

> ถ้าตัดข้อ 1–3 ออกแล้วไปข้อ 4–5 เลย = คนทั่วไปจะไม่เข้าใจเหมือนที่ผ่านมา

### 1.2 “3D ที่คนเห็นภาพ” ไม่เท่ากับ “3D spatial simulation”

- ตอนนี้ solver เป็น 2D spatial (x,y) จริง
    
- แต่เรา render เป็น **3D terrain/surface** ได้ทันที (x,y,z) โดยให้ z = C หรือ z = Ω-density  
    **ผลลัพธ์ที่คนเห็น** จะได้ฟีลแบบรูปที่มึงแปะ โดยไม่ต้องรอ 3D spatial solver
    

---

## 2) หน่วยพื้นฐานของการสื่อสาร: Demo Card (หนึ่งใบจบ)

### 2.1 Demo Card คืออะไร

**Demo Card = “การทดลองหนึ่งเรื่อง”** (1 parameter set + 1 seed หรือ seed ตัวแทน)  
แต่ใน 1 ใบมี “หลายมุม” ได้ตามจำเป็น เพื่อให้ครบวงจร:

- Introvert: input → process → output (สิ่งหนึ่ง)
    
- Extrovert: field → system → force → result → impact (ระบบรวม)
    

### 2.2 โครงสร้าง Demo Card (ขั้นต่ำที่ต้องมี)

**A) Setup (Input)**

- ชื่อเดโม + “สิ่งที่กำลังโชว์” (1 ประโยค)
    
- พารามิเตอร์หลัก 4–6 ตัว (beta, s_tilt, delta, k_ratio, asym …)
    
- seed + grid + T + dt
    

**B) State Snapshot (เห็นด้วยตา)**

- `C_start`, `C_end` (2 ภาพ)
    
- `I_start`, `I_end` (ถ้ามี I)
    
- (optional) overlay หรือ difference map (end-start)
    

**C) Evolution (กระบวนการ)**

- gif/mp4 สั้น 10–30 วินาที
    
    - อย่างน้อย 10–20 frames (ไม่ต้องละเอียดเป็นพัน)
        

**D) Terrain / Landscape (อธิบาย “หลุม–สัน–แรง”)**  
เลือกอย่างใดอย่างหนึ่ง (หรือทั้งคู่ถ้าทำได้):

1. **Ω-density terrain**: map ของพลังงานเชิงพื้นที่ (คนจะเข้าใจว่า “ตึง/รอยต่ออยู่ตรงไหน”)
    
2. **surface ของ C หรือ I**: x,y เป็นพื้น z เป็นค่า field (ภาพแบบภูเขา)
    

**E) Metrics (ยืนยัน ไม่ใช่เล่าเรื่องหลัก)**

- Ω(t) 1 เส้น
    
- bias(t) 1 เส้น
    
- Value score + Conflict score (เลขเดียวจบ) + Phase label
    

**F) Caption แบบ YouTube (3 บรรทัด)**

- “แรงขับ (Potential) คืออะไร”
    
- “แรงต้าน (Conflict/Resistance) อยู่ตรงไหน”
    
- “สุดท้ายระบบลงเอยแบบไหน และทำไม”
    

> ถ้ามีครบ A–F = คนทั่วไปเริ่ม “เข้าใจ” UET จริง

---

## 3) ภาษาเดียวกับ Part 1–2: สรุปเดโมด้วย Value–Conflict Plane

### 3.1 เลือกนิยามหลัก (ไม่ลังเล)

เพื่อให้ consistent และสื่อสารง่ายสุด:

- **Value** = ใช้ (V_{\Delta E}=\Omega(0)-\Omega_{final}) หรือ (-\Omega_{final})
    
- **Conflict (แกนหลัก)** = ใช้ **gradient cost** (C_G=\Omega_{grad,final})  
    (เพราะมันแปลเป็น “รอยต่อ/ความตึง” และโชว์เป็นภาพ Ω-density ได้ตรง ๆ)
    

ถ้ายังไม่มี Ω decomposition ตอนนี้ ก็ใช้สำรอง:

- Conflict สำรอง = backtrack count / dt friction (C_F)
    

### 3.2 เดโม 1 ใบต้อง “ปักจุด” บน plane นี้

ใน Demo Card ให้มีรูปเล็ก ๆ (หรือค่าพิกัด) ว่าเดโมนี้อยู่มุมไหน:

- High Value / Low Conflict = “จัดระเบียบดี”
    
- High Value / High Conflict = “ได้ผลแต่ต้องจ่ายแพง”
    
- Low Value / Low Conflict = “นิ่งแต่ไม่เกิดอะไร”
    
- Low Value / High Conflict = “วุ่นวาย/แตกแยก”
    

> นี่ทำให้คนทั่วไปเริ่มมี “แผนที่ความหมาย” โดยไม่ต้องอ่านสมการ

---

## 4) Archetype Demos: เลือก “น้อยแต่คม” (ไม่ต้องร้อย)

แทนที่จะโชว์ผลรันเป็นร้อยกราฟ ให้เลือก **เดโมต้นแบบ 3–5 แบบ** ที่ครอบคลุม “ทุกมุม” ของความหมาย:

### Archetype 1: SYM Stable (นิ่งและสมมาตร)

- ภาพ: C/I อยู่ร่วมกันแบบไม่เอนข้าง
    
- คำอธิบาย: สนามไม่เอน/แรงขับสมดุลกัน
    

### Archetype 2: BIAS_C (ล็อกฝั่ง C)

- ภาพ: domain ของ C เด่นชัด / I ถอย
    
- คำอธิบาย: coupling + tilt ทำให้หลุมฝั่ง C ลึกกว่า
    

### Archetype 3: BIAS_I (ล็อกฝั่ง I)

- mirror ของ archetype 2
    

### Archetype 4: High-Conflict Boundary (รอยต่อ/แพตเทิร์นแตก/ตึงมาก)

- ภาพ: interface เยอะ, Ω-density สูงตามขอบ
    
- คำอธิบาย: ศักยภาพดึงคนละทาง + gradient penalty สู้กัน → conflict สูง
    

### (ถ้าจะมี 5) Multi-attractor / Seed-sensitive

- เปลี่ยน seed แล้วลงเอยคนละแบบ
    
- สื่อสาร “ระบบรวมมีหลายหลุมแข่งกัน”
    

> 5 อันไม่ใช่กฎ—นี่คือ “ชุดขั้นต่ำที่ครอบคลุมความหมาย” ถ้าทำ 3 อันแล้วครอบคลุมจริงก็พอ

---

## 5) จาก “ระบบฟิสิกส์” → “ระบบเรียนรู้/เกม/NPC” แบบไม่มั่ว

มึงอยากให้มันเล่าเป็นเกม/learning ได้ใช่ไหม—ทำได้ในภาษาสื่อสารแบบนี้ โดยไม่เปลี่ยนแกนคณิต:

### 5.1 NPC View (Introvert)

- NPC = state (C/I pattern)
    
- policy/learning = dynamics ที่ปรับตัวตามแรง (−δΩ/δx)
    
- reward/penalty = Value/Conflict ที่เราวัดได้
    

### 5.2 World View (Extrovert)

- world rules = Ω + constraints
    
- resources/terrain = potential landscape + boundary/forcing
    
- conflict = gradient/interface cost + dt friction
    

> จุดสำคัญ: อย่าพูดว่า “มันคือ RL agent” ตรง ๆ  
> ให้พูดว่า “มันเป็น **world dynamics ที่มีพฤติกรรมเหมือนการเรียนรู้**” (เพราะมันปรับตัวลดความขัดแย้ง/เพิ่มความอยู่รอด)

---

## 6) สิ่งที่ต้องเพิ่ม (เชิง output) เพื่อให้ Blueprint นี้ทำได้จริง

เพื่อทำ Demo Card ตามสเปกนี้ เราต้อง “มีของให้วาด” 2 อย่าง:

### 6.1 State snapshots (บังคับ)

- dump `C(x,y,t)` และ `I(x,y,t)` เป็นช่วงเวลา
    
- เก็บแบบประหยัด: 10–20 frames ต่อ run ก็พอสำหรับเดโม
    

### 6.2 Ω decomposition (แนะนำมาก)

- log: Ω_pot, Ω_coup, Ω_grad ต่อเวลา หรืออย่างน้อยที่ปลายทาง  
    เพื่อให้ Conflict = Ω_grad พูดได้ทั้งในภาพและตัวเลข
    

> นี่ไม่ใช่ “ทำกราฟ 2D เพิ่ม” แต่มันคือ “ทำให้เรามีภาพเพื่อเล่าเรื่อง”

---

## 7) รูปแบบ “Gallery” สำหรับ Public (ให้คนคลิกแล้วเข้าใจทันที)

Gallery ไม่ต้องหรู แค่เป็นระบบ:

### 7.1 หน้า index แบ่งตาม Archetype

- SYM / BIAS_C / BIAS_I / High-Conflict / Multi-attractor  
    แต่ละอันแสดง thumbnail (C_end + Ω-density_end)
    

### 7.2 ในแต่ละ Demo Card ให้มี 3 ปุ่มความลึก

1. **ดูแบบคนทั่วไป** (ภาพ+คำอธิบาย 5 บรรทัด)
    
2. **ดูแบบนักเทคนิค** (พารามิเตอร์+กราฟ Ω/bias+Value/Conflict)
    
3. **ดูแบบวิชาการ** (นิยาม Ω term, scaling, stability notes)
    

> นี่คือ “เอกสารหลายชั้น” ที่มึงต้องการสำหรับการคุยยาว ๆ

---

## Roadmap การคุยระยะยาว (ให้เป็นระบบ ไม่รก ไม่หลง)

จากนี้เราจะเดินเป็น “ตอน/Part” ที่ชัดเจน:

- **Part 1:** ภาษาแกน (Dual equilibrium + 2-axis) ✅ ทำแล้ว
    
- **Part 2:** Value/Conflict + MI Card ✅ ทำแล้ว
    
- **Part 3:** Public Demo Blueprint ✅ (ตอนนี้)
    
- **Part 4:** “MI → สร้างเดโม” (ขั้นตอนจริง: จากโจทย์ → เลือกพารามิเตอร์ → เลือก observables → ได้ Demo Card)
    
- **Part 5:** “Open system / feedback” (ทำ extrovert ให้ครบ: forcing, resources, multi-process)
    
- **Part 6:** Bridge program v0.9 (thermo → info → quantum → game → Einstein) โดยยึดนิยามที่ล็อกแล้ว ไม่หลุด
    

---

## Next Step (Part 4)

Part 4 กูจะทำ “ขั้นตอนใช้งานจริง” แบบ recipe ที่สั้นแต่คม:

1. เลือก “สิ่งหนึ่ง” ในโดเมน → map เป็น C/I (หรือ C-only)
    
2. เลือก “ศักยภาพ/แรงขับ” → map เป็น (a,delta,s)
    
3. เลือก “ความขัดแย้ง/แรงต้าน” → map เป็น (kC,kI) และ/หรือ constraints
    
4. เลือก “การไหล” → map เป็น (M, dt, T)
    
5. ออกแบบเดโม 1 ใบ (ไม่ sweep ก่อน)
    
6. ค่อย sweep เพื่อทำแผนที่หลังจากเข้าใจแล้ว
    

ถ้ามึงพิมพ์ “ต่อ” อีก กูจะเริ่ม Part 4 แบบเป็น “สูตรใช้งาน” เลย และจะยึด framework ที่มึงพูด (introvert/extrovert) เป็นแกนตลอด ไม่กลับไปยัด heatmap เป็นพระเอกอีก


----
# 000.04/1

## TL;DR

**Part 4 = “สูตรใช้งานจริง”**: จาก “โจทย์/เฟรมเวิร์ก 2 ชั้น (Introvert–Extrovert)” → แปลงเป็น **UET model ที่รันได้** → แล้วผลิต **Demo Card แบบ YouTube** (ภาพ state + evolution + terrain + ค่า Value/Conflict) โดย **ไม่เริ่มจาก heatmap 2D**

แก่นคือ:

- **Seed = จุดปล่อย** (ใช้สำรวจ basin)
    
- **Space/Spec = ตัวกำหนดโลก** (Ω + กลไก + constraints)
    
- เรา “เรียนรู้สนาม” จากการดูว่า seed จำนวนมาก “ไหลลงไหน” + ภาพของการไหล
    

---

## Insight

สิ่งที่ทำให้ UET “ใช้งานได้จริง” ไม่ใช่จำนวน runs แต่คือ **การมี “สัญญา (contract)” ว่า 1 โมเดลต้องให้ Output อะไรบ้าง** เพื่อให้คน:

1. เห็นภาพ (YouTube-level)
    
2. เข้าใจความหมาย (Value/Conflict/Phase)
    
3. ทำซ้ำได้ (reproducible)
    

ดังนั้น Part 4 จะล็อก “ขั้นตอน + contract” เป็นมาตรฐานเดียว

---

## Canonical Spec v0.9 Draft — Part 4/1

## MI → Runnable Model → Demo Card (Recipe ที่ใช้ได้จริง)

## 0) โครงสร้างการทำงานที่ถูกลำดับ (ห้ามสลับ)

**ลำดับมาตรฐาน 6 ขั้น**

1. **นิยาม 2 ชั้น**: Introvert entity / Extrovert world
    
2. **MI Card**: Map ความหมายโดเมน → C/I + Potential/Conflict/Flow
    
3. **1 Case Demo ก่อน** (1 parameter set) → ให้ “เห็นภาพ”
    
4. **Extract Value/Conflict + Phase label** จาก case demo
    
5. **ค่อยทำ Sweep** (ใช้เป็นแผนที่นำทาง ไม่ใช่ตัวเล่าเรื่อง)
    
6. **เลือก archetype** จาก sweep มาทำ Demo Cards เพิ่ม (3–5 ใบ)
    

> ถ้าย้อนกลับไปทำข้อ 5 ก่อนข้อ 3 = กลับไปงงเหมือนเดิม

---

## 1) Step 1 — แยก “Introvert vs Extrovert” ให้ชัดก่อนแตะพารามิเตอร์

### 1.1 Introvert (สิ่งหนึ่ง = input → processing → output)

- **input**: สภาพแวดล้อมที่รับรู้ + ข้อจำกัด + seed (initial state)
    
- **processing**: dynamics ของ UET (ไหลตาม Ω + gates)
    
- **output**: state ปลายทาง + ตัวชี้วัด (Value/Conflict/Phase)
    

### 1.2 Extrovert (โลกเปิด = สนาม + หลายกระบวนการ + feedback)

- **สนาม**: Ω + constraints + forcing (ตอนนี้ harness ยังเน้น “สนามคงที่”)
    
- **หลายกระบวนการ**: ตีความได้ผ่าน C/I (สองแรงสองแนวโน้ม) หรือ multi-subsystem (อนาคต)
    
- **feedback**: เอาผลกระทบไปปรับสนาม/ข้อจำกัดในรอบถัดไป (roadmap)
    

> ใน v0.8.5+/ปัจจุบัน ให้ถือว่าเราอยู่ในโหมด “สนามคงที่ + ระบบไหล” ก่อน แล้วค่อยขยายเป็น feedback

---

## 2) Step 2 — MI Card (แบบฟอร์มแปลงโจทย์ → UET)

ให้กรอกแค่นี้ แล้วจะรันได้/เล่าเรื่องได้

### MI Card — Canonical (สั้นแต่ครบ)

**A) Entity (Introvert)**

1. สิ่งหนึ่งคืออะไร? (สิ่งที่ “กำลังเป็นอยู่”)
    
2. state ที่จะจำลองคืออะไร? (เริ่ม 1 field หรือ 2 fields)
    

**B) World (Extrovert)**  
3) สนาม/แรงขับมาจากอะไร? (อะไรทำให้ระบบ “อยาก” ไปทางหนึ่ง)  
4) ข้อจำกัด/แรงต้านคืออะไร? (อะไรทำให้การเปลี่ยนแปลง “มีราคา”)

**C) Map เข้า UET**  
5) ใช้ **C-only** หรือ **C–I**?  
6) Potential (P) → map เป็น `potC/potI` (quartic + tilt)  
7) Conflict/Resistance (R) → map เป็น `kC/kI` (+ gradient penalty)  
8) Flow (J) → map เป็น `M / dt / T` (+ gates)

**D) Observables**  
9) output ที่ต้องเห็นด้วยตา (demo): C/I snapshots + evolution + terrain  
10) output ที่ต้องได้เป็นตัวเลข: Ω, Ω_grad, Value, Conflict, Phase label

> MI Card คือ “สะพาน” ระหว่างเฟรมเวิร์กกับสมการที่พิสูจน์แล้ว ไม่ใช่สมการใหม่

---

## 3) Step 3 — เลือก “รุ่นของโมเดล” ให้ตรงคำถาม

### 3.1 ใช้ C-only เมื่อ:

- โจทย์เป็น “เอนเอียงไปทางเดียว” หรือ “สถานะเดียว”
    
- อยากได้เดโมเร็วสุด
    

### 3.2 ใช้ C–I เมื่อ:

- โจทย์มี “สองแรง/สองแนวโน้ม” แข่งกัน (ตรงกับสมดุลสองฝั่งที่มึงพูด)
    
- อยากอธิบาย “ความขัดแย้ง” แบบเป็นรูป (interface/รอยต่อ) ได้ชัด
    

**คำแปลสั้น ๆ**

- C = tendency/แรงขับชนิดหนึ่ง
    
- I = tendency/แรงขับอีกชนิดหนึ่ง
    
- β = ความผูก/การกระตุ้นกัน (coupling)
    
- kC,kI = ความต้านการแยกตัวเชิงพื้นที่ (ทำให้เกิด/ลดรอยต่อ)
    

---

## 4) Step 4 — ตั้ง “Space/Spec” (นี่คือพระเอก ไม่ใช่ seed)

นี่คือสิ่งที่มึงพูดว่า “สำคัญหมด” — ถูกต้อง

### 4.1 Potential knobs (ศักยภาพ)

- `delta` (ความคม/ความลึกของหลุม quartic)
    
- `s` หรือ `s_tilt` (เอนสนามให้เข้าข้าง)
    
- (และ `a` ถ้ามีใน pot)
    

### 4.2 Interaction knob

- `beta` (C–I ส่งผลกันแรงแค่ไหน)
    

### 4.3 Conflict/structure knobs

- `kC, kI` และ/หรือ `k_ratio` (ความหนืดเชิงพื้นที่ / รอยต่อ)
    

### 4.4 Flow knobs

- `M` (mobility) + `dt`, `T` (เวลาในซิม)
    

### 4.5 Geometry knobs

- `N, L` (ความละเอียดและขนาดโลก)
    

> **นี่คือ Space/Spec** ที่กำหนด “ภูมิประเทศ Ω” + “กติกาการไหล”  
> ส่วน seed คือการเลือกจุดปล่อยลูกบอลเพื่อสำรวจภูมิประเทศนั้น

---

## 5) Step 5 — “1 Case Demo” (ชุดเดียว = เรื่องเดียว แต่มีหลายภาพได้)

คำว่า “ชุดเดียว” ใน Part 3/4 = **1 parameter set**  
แต่ “ในชุด” มี output หลายชิ้นเพื่อเล่าเรื่อง (ไม่ใช่กราฟ 2D)

### Demo Contract (ต้องมี)

**(A) State visuals**

- `C_start`, `C_end`
    
- `I_start`, `I_end` (ถ้ามี)
    

**(B) Evolution**

- `evolution.gif` (10–20 frames ก็พอ)
    

**(C) Terrain**

- `surface_C_or_I.png` (plot 3D: x,y,z = C หรือ I)
    
- และ/หรือ `omega_density_terrain.png` (ภาพแบบภูเขาที่สื่อ “หลุม/สัน/รอยต่อ”)
    

**(D) Metrics (ยืนยัน)**

- Ω(t)
    
- bias(t)
    
- Value, Conflict, Phase label
    

> นี่คือเดโมแบบ YouTube ที่มึงต้องการ และมันไม่ใช่ “2D heatmap หลายอัน”

---

## 6) Step 6 — นิยาม Value/Conflict ให้ “อ่านเป็นภาพ”

ยึดแกนที่สื่อสารง่ายสุด (ตาม Part 2):

- **Value**: (V_{\Delta E}=\Omega(0)-\Omega_{final}) หรือ (-\Omega_{final})
    
- **Conflict (แกนหลัก)**: (C_G=\Omega_{grad,final}) (รอยต่อ/ความตึง)
    

สิ่งสำคัญคือ:

- **Conflict ต้องชี้บนภาพได้** (เช่น Ω-density สว่างตาม interface)
    
- ไม่งั้นมันจะกลายเป็นตัวเลขลอย ๆ
    

---

## 7) Step 7 — ค่อยทำ Sweep เพื่อ “หา archetype” ไม่ใช่เพื่อเล่าเรื่อง

หลังจากเดโม 1 ใบเข้าใจแล้ว ค่อยทำ sweep:

### Sweep rule (กันมั่ว)

- เริ่มแค่ **2 knobs** ก่อน (เช่น `beta × s_tilt` หรือ `beta × k_ratio`)
    
- แล้วสำหรับแต่ละจุด เก็บหลาย seed เพื่อวัด robustness (Strength)
    

### ผลลัพธ์ของ sweep ที่ “ถูกใช้”

- ใช้เป็น “แผนที่” เพื่อเลือกจุด 3–5 จุดมาเป็น archetype demos
    
- ไม่ใช่เอา heatmap ไปสอนคนจากศูนย์
    

---

## 8) Step 8 — สรุปเป็น “Gallery ที่คนคลิกแล้วเข้าใจ”

โครง Gallery:

- หน้าแรก: 3–5 archetype (SYM / BIAS_C / BIAS_I / High-conflict / Multi-attractor)
    
- แต่ละอันเป็น Demo Card (ภาพ+gif+terrain+caption)
    
- มีปุ่ม “ดูเชิงเทคนิค” สำหรับพารามิเตอร์/กราฟ/ไฟล์
    

---

## Math/Physics Interpretation

- Introvert = dynamics ของ state ภายใต้ Ω
    
- Extrovert = นิยามของสนาม Ω + constraints + (อนาคต) forcing/feedback
    
- Value/Conflict วัดได้จาก Ω และ decomposition (โดยเฉพาะ Ω_grad)
    

---

## Plain-Language Interpretation

- เราสร้าง “โลก” (สนาม) ก่อน แล้วปล่อย “สิ่งหนึ่ง” (seed) เข้าไป
    
- สิ่งหนึ่งจะไหลจนเข้าที่ (สมดุล)
    
- เราไม่เรียนรู้จาก seed แต่เรียนรู้จาก “โลก” ว่ามันชอบให้สิ่งต่าง ๆ ลงเอยแบบไหน
    
- ถ้าอยากให้คนเข้าใจ ต้อง “ถ่ายวิดีโอ” การไหล + ทำรูปภูเขา/หลุมของสนาม
    

---

## Next Step (Part 4.5 / Part 5 ที่ต้องทำต่อในแชท)

**ต่อไปกูจะทำ 2 อย่างให้เป็นมาตรฐาน public:**

1. “**MI Card ตัวอย่าง 1 ใบ**” แบบไม่ผูกโดเมน (เป็น template ที่กรอกได้จริง)
    
2. “**Demo Contract checklist**” ที่แปะไว้ใน repo/docs ได้เลย ว่า run ไหน “ถือว่าเป็น Demo-ready”
    

ถ้ามึงพิมพ์ “ต่อ” อีก กูจะเขียน MI Card template + checklist ให้แบบสั้น กระชับ และใช้ได้ทันที (ไม่แตะ infra/ไม่สร้างไฟล์เพิ่มก่อน).


----
# 000.04/2

ได้ ต่อเลย — คราวนี้เป็น “ของใช้งานจริง” 2 ชิ้นตาม Part 4/2:

1. **MI Card Template (แบบฟอร์มมาตรฐานแปลงโจทย์ → UET case/run ได้ทันที)**
2. **Demo Contract Checklist (นิยามว่า run ไหน “Demo-ready” สำหรับ public/YouTube-level)**
## 1) MI Card Template v0.9 (Canonical)

### 1.1 MI Card (แบบย่อ 1 หน้า)

> ใช้กรอกทุกครั้งก่อนสร้าง matrix / ก่อนรัน เพื่อไม่ให้หลุด framework

**A) Identity**

- `project_name:`
    
- `model_type:` `C_only` | `C_I`
    
- `intent:` (ต้องการ “สมดุลแบบไหน” introvert หรือ extrovert หรือทั้งคู่)
    

**B) Introvert (Entity = input→process→output)**

- `entity_definition:` “สิ่งหนึ่ง” คืออะไร (ในโดเมน)
    
- `state_variables:` C คืออะไร? I คืออะไร? (ถ้า C_only ก็แค่ C)
    
- `constraints:` ข้อจำกัดจริง (เช่น C,I อยู่ในช่วงไหน? conservation มีไหม? ฯลฯ)
    
- `process_story:` มัน “ปรับตัว/ไหล” อย่างไรในโดเมน (ภาษาคน)
    

**C) Extrovert (World = field→system→force→impact)**

- `world_field_story:` “สนาม/สิ่งแวดล้อม” ในโดเมนคืออะไร
    
- `forces_story:` อะไรผลัก/ดึง/ต้าน (แยก Potential vs Conflict)
    
- `impact_story:` output จะตีความเป็น “คุณค่า/ความขัดแย้ง” ยังไง
    

**D) Map เข้า UET (ของจริงที่รัน)**

- `potential_map:` (P)
    
    - `potC:` quartic(a, delta, s)
        
    - `potI:` quartic(a, delta, s) (ถ้ามี I)
        
- `interaction_map:`
    
    - `beta:` ความแรง coupling C–I
        
- `conflict_map:` (R)
    
    - `kC, kI:` gradient penalty (หรือ `k_ratio`)
        
- `flow_map:` (J)
    
    - `M / MC / MI:` mobility
        
    - `dt, T:` time discretization
        
- `geometry_map:`
    
    - `N, L, dim:` (ตอนนี้ code เป็น 2D spatial; 3D spatial เป็น roadmap)
        

**E) Observables (สิ่งที่ต้องได้จาก run)**

- `phase_label:` BIAS_C / BIAS_I / SYM
    
- `value_metric:` (เลือก 1) `V_deltaE` หรือ `-Omega_final`
    
- `conflict_metric:` (หลัก) `Omega_grad_final` (สำรอง: backtrack_count)
    
- `sanity:` Ω ต้อง monotone ผ่าน gate, ไม่ NaN/Inf
    

**F) Demo Plan (ต้อง “เห็นภาพ”)**

- `demo_case:` ระบุ 1 parameter set ที่จะทำ Demo Card ก่อน sweep
    
- `required_exports:` snapshots + gif + terrain + curves (ดู Demo Contract ด้านล่าง)
    

**G) Sweep Plan (หลังจาก demo เข้าใจแล้วค่อยทำ)**

- `primary_axes:` เลือก 2 knobs (เช่น beta×s_tilt)
    
- `secondary_axes:` (optional) fix หรือทำ slice
    
- `seeds:` จำนวน seed ต่อจุด (เพื่อ basin robustness)
    

---

### 1.2 MI Card (รูปแบบไฟล์ที่กรอกง่าย) — YAML Template

```yaml
project_name: "___"
model_type: "C_I"   # or "C_only"
intent:
  introvert: true
  extrovert: true

introvert:
  entity_definition: "___"
  state_variables:
    C: "___"
    I: "___"   # omit if C_only
  constraints:
    - "___"
  process_story: "input → processing → output ในโดเมนนี้คืออะไร (ภาษาคน)"

extrovert:
  world_field_story: "สนาม/สิ่งแวดล้อมคืออะไร"
  forces_story:
    potential: "อะไรคือแรงขับ (P)"
    conflict: "อะไรคือแรงต้าน/ราคาที่ต้องจ่าย (R)"
    flow: "อะไรทำให้เกิดการไหล/ปรับตัว (J)"
  impact_story:
    value: "นิยามคุณค่าในโดเมนนี้"
    conflict: "นิยามความขัดแย้งในโดเมนนี้"

uet_map:
  potentials:
    potC: {type: "quartic", a: ___, delta: ___, s: ___}
    potI: {type: "quartic", a: ___, delta: ___, s: ___}  # omit if C_only
  interaction:
    beta: ___
  conflict:
    kC: ___
    kI: ___
    k_ratio: ___  # optional alternative
  flow:
    MC: ___
    MI: ___
    dt: ___
    T: ___
  geometry:
    N: ___
    L: ___
    dim: 2

observables:
  phase_label: true
  value_metric: "V_deltaE"
  conflict_metric: "Omega_grad_final"
  sanity:
    omega_monotone: true
    no_nan_inf: true

demo_plan:
  demo_case_params:
    beta: ___
    s_tilt: ___
    delta: ___
    k_ratio: ___
    asym: ___
  required_exports:
    - "snapshots_CI"
    - "evolution_gif"
    - "omega_density_terrain"
    - "omega_bias_curves"

sweep_plan:
  primary_axes: ["beta", "s_tilt"]
  grid: {beta: [...], s_tilt: [...]}
  seeds: [0,1,2,3,4,5,6,7,8,9]
```

---

## 2) Demo Contract Checklist (Run ไหน “Demo-ready”)

> เป้าหมาย: คนทั่วไปดู “1 หน้า” แล้วเข้าใจ ไม่ใช่ดู heatmap เป็นร้อยอันแล้วงง

### 2.1 โครงสร้างไฟล์ขั้นต่ำ (ต้องมี)

ให้ถือว่า **1 demo = 1 run_dir** แล้วต้องมี:

**(A) Metadata**

- `demo_manifest.json` หรือ `meta.json`  
    ต้องมี: model_type, params, grid(N,L), dt,T, seed, git_commit (ถ้ามี), note
    

**(B) State snapshots (หัวใจ)**

- `snapshots/` หรือไฟล์รวม `.npz`
    
    - อย่างน้อย 10–20 เฟรม (log-scale ก็ได้)
        
    - ต้องมี C ทุกเฟรม และ I ถ้าเป็น C_I
        

**(C) Visual assets**

- `figs/state_start.png`
    
- `figs/state_end.png`
    
- `figs/evolution.gif` (หรือ mp4)
    
- `figs/terrain_C.png` (surface 3D: z=C) และ/หรือ `figs/terrain_omega_density.png`
    

**(D) Metrics assets**

- `timeseries.csv` (Ω(t), bias(t) อย่างน้อย)
    
- `summary.json` หรือ `UET_final_summary.csv` ที่มีค่า Omega_final/Value/Conflict/label
    

**(E) Caption (ภาษา YouTube)**

- `README_demo.md` (สั้นมากพอ)
    
    - 1 บรรทัด: “เดโมนี้กำลังแสดงอะไร”
        
    - 3 บรรทัด: Potential/Conflict/Flow ในภาษาคน
        
    - 1 บรรทัด: ผลลัพธ์ = phase + value/conflict
        

---

### 2.2 Acceptance Criteria (ผ่าน/ไม่ผ่าน)

**ต้องผ่านทั้งหมดนี้ถึงเรียก Demo-ready**

1. **Reproducible setup**
    

- มี seed + params ครบใน manifest
    
- run สามารถ rerun ได้โดยไม่เดา
    

2. **Visible story**
    

- มี start/end และ evolution gif (คนดูแล้วเห็น “มันเปลี่ยนจริง”)
    
- terrain อย่างน้อย 1 ภาพ (C หรือ Ω-density)
    

3. **Metric sanity**
    

- Ω ไม่ NaN/Inf
    
- ถ้ามี monotone gate: ต้อง PASS (หรือมีเหตุผลชัดใน README)
    

4. **Interpretability**
    

- README_demo อธิบายได้ว่า “ทำไมถึง BIAS_C/BIAS_I/SYM” แบบไม่อ้างสมการยาว
    

---

## 3) แผ่นสรุปการ map “เฟรมเวิร์ก → UET term” (ใช้แปะต้น docs)

เพื่อให้ไม่หลุดกรอบทุกครั้ง:

|Framework|ภาษาคน|UET term ที่จับต้องได้|
|---|---|---|
|Potential (P)|แรงขับ/ความอยากเกิด|quartic `V(C), V(I)` + tilt `s` + coupling drive ผ่าน `beta`|
|Conflict/Resistance (R)|ราคาที่ต้องจ่าย/แรงต้าน|gradient penalty `kC,kI` ⇒ Ω_grad + backtrack friction|
|Flow/Activity (J)|การปรับตัว/การไหล|mobility `M/MC/MI` + dt,T + solver update|
|Result|ลงเอยแบบไหน|phase label + final pattern|
|Impact|คุณค่า/ความขัดแย้งในระบบรวม|Value score + Conflict score + robustness across seeds|

---

## Next Step

ถัดไป (Part 4.6) กูจะทำ **“MI Card ตัวอย่าง 1 ใบ”** แบบ “เป็นกลาง” (ไม่ผูกโดเมน) + **ตัวอย่าง 1 ใบแบบ Physarum (ทาก/รา)** ในฐานะ _case study_ เพื่อให้เห็นว่า framework สองชั้น “กรอกแล้ววิ่งเข้าหา demo ได้ยังไง” โดยไม่ไปสร้างสมการใหม่

ถ้ามึงพิมพ์ “ต่อ” อีก กูจะเขียน 2 ใบนั้นให้ครบในรูปแบบที่เอาไปวาง docs ได้ทันที.


----
# 000.04/3

## TL;DR

ต่อไปนี้คือ “Part 4.6” ตามที่คุยกัน: **MI Card ตัวอย่าง 2 ใบ** (พร้อมวางลง docs ได้ทันที)

1. **MI Card ตัวอย่างกลาง (Neutral / Toy)** — ใช้เป็นต้นแบบกรอกทุกโดเมน
    
2. **MI Card กรณีศึกษา Physarum (slime mold)** — เพื่อโชว์ว่า “สิ่งหนึ่ง + ระบบเปิด + value/conflict” แปลงเข้า UET ได้ยังไง โดย **ไม่สร้างสมการใหม่**
    

ท้ายสุดกูแถม “แปลง MI Card → 1 demo case + sweep plan” แบบสูตรใช้งานจริง (ไม่ใช่รันมั่ว)

---

## Insight

- “เดโมแบบ YouTube” ไม่ได้มาจากทำ heatmap เยอะ ๆ
    
- มันมาจาก **MI Card ที่ map ความหมาย → Ω term → output ที่ต้อง export** แล้วทำ **Demo Card 1 ใบ** ให้คนเห็น state/evolution/terrain ก่อน
    

---

## Part 4.3 — MI Cards (Docs-ready)

## MI Card 0 — Neutral Canonical (Toy / Template ที่กรอกแล้วรันได้)

> อันนี้เป็น “ตัวอย่างกลาง” ไม่ผูกโดเมน ใช้เป็นมาตรฐานทุกโปรเจกต์

### เวอร์ชันวิชาการ (Formal)

**A) Identity**

- `project_name`: UET-Neutral-Canonical
    
- `model_type`: `C_I`
    
- `intent`: introvert+extrovert (แต่ extrovert ยัง “สนามคงที่” ใน harness ปัจจุบัน)
    

**B) Introvert (Entity)**

- `entity_definition`: “ระบบหนึ่งหน่วย” ที่มี 2 แนวโน้มแข่งขันกัน (C vs I)
    
- `state_variables`:
    
    - `C(x,y,t)`: tendency/drive ชนิดที่ 1
        
    - `I(x,y,t)`: tendency/drive ชนิดที่ 2
        
- `constraints`:
    
    - boundedness / numerical stability (ตาม gate)
        
    - optional: range clamp (ถ้ากำหนดใน implementation)
        
- `process_story`:
    
    - state evolves under dissipative dynamics that decreases Ω (Lyapunov-like monotone gate)
        

**C) Extrovert (World)**

- `world_field_story`: world is defined by Ω(C,I; θ) with fixed parameters θ
    
- `forces_story`:
    
    - Potential P: local quartic wells + tilt (s) for each field
        
    - Conflict R: gradient penalty (kC,kI) controlling interface/smoothness cost
        
    - Flow J: mobility (MC,MI) and timestep controls relaxation speed
        
- `impact_story`:
    
    - Value = energy decrease / stable organization
        
    - Conflict = gradient/interface cost + dynamic friction (backtracks)
        

**D) Map → UET parameters (ตัวจริงที่รัน)**

- `potC = quartic(aC, deltaC, sC)`
    
- `potI = quartic(aI, deltaI, sI)`
    
- `beta`: coupling strength
    
- `kC,kI` (หรือ k_ratio): gradient penalty
    
- `MC, MI, dt, T, N, L, dim=2`
    

**E) Observables**

- Phase label: BIAS_C / BIAS_I / SYM
    
- Value metric: (V_{\Delta E}=\Omega(0)-\Omega_{\text{final}})
    
- Conflict metric: (C_G=\Omega_{\text{grad,final}}) (สำรอง: backtrack_count)
    

**F) Demo Plan**

- ทำ “1 demo case” ก่อน sweep
    
- export: snapshots + gif + terrain (C หรือ Ω-density) + Ω(t), bias(t)
    

---

### เวอร์ชันคนทั่วไป (Intuitive)

เรามี “ตัวตนหนึ่งตัว” ที่มีแรงดึง 2 ฝั่ง (C กับ I) แล้วมันค่อย ๆ ปรับตัวลงไปหาความนิ่งใน “สนาม” (Ω)

- **แรงขับ** ทำให้มันอยากไปทางใดทางหนึ่ง
    
- **แรงต้าน** ทำให้มันต้องจ่ายราคาเวลาจะแยกตัว/เกิดรอยต่อ
    
- **การไหล** คือความเร็วการปรับตัว  
    สุดท้ายมันจะ “ล็อกฝั่ง C”, “ล็อกฝั่ง I” หรือ “สมดุล” และเราวัดเป็น Value/Conflict ได้จริง
    

---

## YAML (วางลง docs ได้เลย)

```yaml
project_name: "UET-Neutral-Canonical"
model_type: "C_I"
intent: {introvert: true, extrovert: true}

introvert:
  entity_definition: "A two-tendency entity (C vs I) evolving under a monotone-Ω dynamics."
  state_variables:
    C: "Drive/tendency type-1 field"
    I: "Drive/tendency type-2 field"
  constraints:
    - "numerical stability via monotone-Ω accept/reject"
    - "boundedness (optional clamp if used)"
  process_story: "Input→(relaxation under Ω)→Output attractor/pattern"

extrovert:
  world_field_story: "World is defined by Ω(C,I;θ) with fixed θ in current harness."
  forces_story:
    potential: "quartic wells + tilt (s) per field"
    conflict: "gradient/interface cost controlled by kC,kI"
    flow: "mobility + dt/T sets relaxation rate"
  impact_story:
    value: "energy decrease / stable organization"
    conflict: "interface cost + backtracking friction"

uet_map:
  potentials:
    potC: {type: "quartic", a: -1.0, delta: 3.0, s: 0.0}
    potI: {type: "quartic", a: -1.0, delta: 3.0, s: 0.0}
  interaction: {beta: 1.0}
  conflict: {kC: 1.0, kI: 1.0, k_ratio: 1.0}
  flow: {MC: 1.0, MI: 1.0, dt: 1e-3, T: 1.0}
  geometry: {N: 128, L: 1.0, dim: 2}

observables:
  phase_label: true
  value_metric: "V_deltaE"
  conflict_metric: "Omega_grad_final"
  sanity: {omega_monotone: true, no_nan_inf: true}

demo_plan:
  demo_case_params: {beta: 1.0, s_tilt: 0.0, delta: 3.0, k_ratio: 1.0, asym: 0.0}
  required_exports: ["snapshots_CI", "evolution_gif", "terrain_omega_density", "curves_omega_bias"]

sweep_plan:
  primary_axes: ["beta", "s_tilt"]
  seeds: [0,1,2,3,4,5,6,7,8,9]
```

---

## MI Card 1 — Case Study: Physarum (slime mold) แบบ “ไม่มั่วสมการใหม่”

> เป้าหมาย: ใช้ Physarum เป็น “เรื่องเล่า” ที่คนดูคลิปแล้วเข้าใจ: มันสร้าง network ดี ๆ ได้เพราะ trade-off **efficiency vs cost**  
> เรา map trade-off นี้เข้า UET ด้วย **Potential/Conflict/Flow** ที่เรามีอยู่แล้ว

### เวอร์ชันวิชาการ (Formal)

**A) Identity**

- `project_name`: UET-Physarum-Network (Conceptual)
    
- `model_type`: `C_I` (เพื่อมี “สองแรง” ชัด: reinforcement vs cost/decay)
    
- `intent`: introvert (ตัวสิ่ง) + extrovert (สิ่งแวดล้อม/แหล่งอาหารเป็นสนาม/forcing)
    

**B) Introvert (Entity)**

- `entity_definition`: network-forming adaptive medium (การกระจายความหนาท่อ/ความหนาแน่น)
    
- `state_variables`:
    
    - `C(x,y,t)`: “capacity/structure” (ความหนา/ความสามารถในการเชื่อมต่อ) — แนวโน้ม “สร้างท่อ/คงโครงสร้าง”
        
    - `I(x,y,t)`: “inhibition/maintenance pressure” หรือ “cost tendency” — แนวโน้ม “ลดท่อ/จำกัดต้นทุน”
        
- `constraints`:
    
    - boundedness + monotone-Ω gate
        
    - forcing/boundary: จุดอาหาร/เป้าหมายเป็น external condition (ใน harness ปัจจุบันทำได้ในรูป tilt/initialization/หรือ roadmap)
        

**C) Extrovert (World)**

- `world_field_story`:
    
    - environment provides “sources/sinks” (อาหาร) ทำหน้าที่เหมือน “tilt” ของสนาม
        
- `forces_story`:
    
    - Potential (P): ทำให้ C “อยากเพิ่ม” ใกล้แหล่งอาหาร/เส้นทางดี (ผ่าน tilt หรือ spatial bias ใน potential)
        
    - Conflict (R): gradient cost = “ราคาของรอยต่อ/ความซับซ้อนของ network” (ยิ่งแตกแขนง/คม ยิ่งจ่าย)
        
    - Flow (J): mobility คุมความเร็วการปรับ network
        
- `impact_story`:
    
    - Value = ได้โครงสร้างเสถียรที่ลด Ω ได้มาก (ตีความเป็น “efficiency/organization”)
        
    - Conflict = interface/roughness (Ω_grad) + friction/backtrack (ยิ่งฝืดแปลว่ากลไกปะทะกันหนัก)
        

**D) Map → UET**

- `potC`: quartic + tilt ให้ C ชอบเกิด/คงอยู่ (และ “เอน” ตามแหล่งอาหาร)
    
- `potI`: quartic ให้ I ทำหน้าที่ต้าน/จำกัด (หรือแสดง maintenance pressure)
    
- `beta`: coupling ระหว่าง reinforcement กับ cost (แรงปะทะ/แรงประสาน)
    
- `kC,kI`: คุม “ความเรียบของท่อ/รอยต่อ” (interface cost)
    
- open-system forcing:
    
    - v0.8.5 harness: ทำแบบ “สนามคงที่” ก่อน (tilt คงที่)
        
    - roadmap extrovert: ให้ tilt เป็น spatial field หรือ time-varying
        

**E) Observables**

- Pattern outcome:
    
    - network-like structure (ต้องเห็นจาก snapshots)
        
- Value/Conflict plane:
    
    - Value สูง = network เสถียรและ “ชนะ” ใน Ω
        
    - Conflict สูง = interface เยอะ/ซับซ้อน/ตึง
        

---

### เวอร์ชันคนทั่วไป (Intuitive)

คิดว่าโลกมี “อาหาร” อยู่บางจุด ทาก/ราเหมือนพยายามสร้าง “ถนน” ให้ไปถึงอาหารได้ดี

- แรงขับ = อยากเชื่อมเส้นทางให้ดี
    
- แรงต้าน = สร้างถนนเยอะก็แพง (ต้องดูแล)  
    มันเลยต้องหาจุดสมดุล: **ดีพอแต่ไม่ฟุ่มเฟือย**  
    ใน UET เราให้สิ่งนี้เกิดจากการไหลบน “ภูมิประเทศ Ω” แล้วดูภาพ evolution เหมือนคลิป YouTube ได้
    

---

## YAML (วางลง docs ได้)

```yaml
project_name: "UET-Physarum-Network (Conceptual)"
model_type: "C_I"
intent: {introvert: true, extrovert: true}

introvert:
  entity_definition: "Adaptive medium forming transport-like structure under competing drives."
  state_variables:
    C: "Structure/capacity field (network thickness/strength proxy)"
    I: "Cost/maintenance pressure field (inhibitory tendency proxy)"
  constraints:
    - "monotone-Ω gate for stability"
    - "environmental forcing via tilt / spatial bias (v0.9 roadmap for true open forcing)"
  process_story: "C grows where it is beneficial; I penalizes excessive structure; system relaxes to a stable pattern."

extrovert:
  world_field_story: "Environment provides resource locations that bias the landscape (tilt)."
  forces_story:
    potential: "resource-driven bias toward forming structure"
    conflict: "interface/complexity cost via gradient penalty"
    flow: "relaxation speed via mobility"
  impact_story:
    value: "organized, efficient stable pattern"
    conflict: "high interface/roughness and dynamic friction"

uet_map:
  potentials:
    potC: {type: "quartic", a: -1.0, delta: 3.0, s: +0.2}   # s is a stand-in for resource bias (conceptual)
    potI: {type: "quartic", a: -1.0, delta: 3.0, s: -0.2}
  interaction: {beta: 1.2}
  conflict: {kC: 1.0, kI: 1.0, k_ratio: 1.0}
  flow: {MC: 1.0, MI: 1.0, dt: 1e-3, T: 1.0}
  geometry: {N: 128, L: 1.0, dim: 2}

observables:
  phase_label: true
  value_metric: "V_deltaE"
  conflict_metric: "Omega_grad_final"
  sanity: {omega_monotone: true, no_nan_inf: true}

demo_plan:
  demo_case_params: {beta: 1.2, s_tilt: 0.2, delta: 3.0, k_ratio: 1.0, asym: 0.0}
  required_exports: ["snapshots_CI", "evolution_gif", "terrain_C", "terrain_omega_density", "curves_omega_bias"]

sweep_plan:
  primary_axes: ["beta", "k_ratio"]
  seeds: [0,1,2,3,4,5,6,7,8,9]
```

> หมายเหตุสำคัญ (กันมั่ว): ใน harness ปัจจุบัน “resource locations” ยังไม่ได้เป็น spatial forcing เต็มรูปแบบ  
> YAML นี้เลยใช้ `s` เป็นตัวแทนแนวคิด “เอนสนาม” ก่อน และบอกชัดว่า **open forcing เป็น roadmap (extrovert ขั้นถัดไป)**

---

## แปลง MI Card → “1 Demo Case” + “Sweep Plan” แบบไม่มั่ว (สูตรใช้งาน)

## 1) เลือก Demo Case 1 จุด (ก่อน sweep)

หลักเลือก:

- อยากให้คนเห็น “การแข่งขัน 2 ฝั่ง” → เลือก `C_I`
    
- อยากให้เห็น “หลุมชนะชัด” → เลือก `|s_tilt|` ไม่เล็กเกิน + `beta` กลาง ๆ
    
- อยากให้เห็น “ความขัดแย้งเป็นรูป” → เลือก `k_ratio` ให้เกิด interface พอดี (ไม่เรียบหมด/ไม่แตกละเอียดเกิน)
    

**Output ที่ต้องได้จาก case เดียวนี้**

- ภาพ start/end ของ C/I
    
- gif evolution
    
- terrain (C หรือ Ω-density)
    
- Value, Conflict, label
    

## 2) ค่อย sweep ทีหลัง (ใช้หาจุด archetype)

เลือก 2 แกน:

- ถ้าจะเล่า “แรงประสาน vs แรงต้าน” → `beta × k_ratio`
    
- ถ้าจะเล่า “เอนสนาม vs coupling” → `beta × s_tilt`  
    แล้วใช้หลาย seed เพื่อ robustness
    

---

## Next Step

ต่อไป (Part 4.7) กูจะ “ทำให้มันเป็นบทเอกสารพร้อม public” แบบอ่านสนุกแต่ไม่หลุดวิชาการ โดยเขียนเป็น:

1. **บทสั้น “UET as a World Simulator”** (อธิบาย NPC/learning/world rules อย่างถูกถ้อยคำ)
    
2. **Runbook 1 หน้า**: “เริ่มจาก MI Card → ทำ Demo Card → ค่อย sweep”
    
3. **Glossary**: คำว่า Field/Entity/Value/Conflict/Seed/Phase แปลเป็นไทย+เทคนิคตรงกัน
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูเขียน Part 4.7 ให้เลยแบบเป็นบทจริง (สองเวอร์ชัน: วิชาการ + คนทั่วไป)



----
# 000.04/4

## TL;DR

ต่อไปนี้คือ **Part 4.4 (พร้อมเอาไปวางเป็น docs/public ได้เลย) 3 ชิ้น:

1. บท “**UET as a World Simulator**” (อธิบายแบบเกม/NPC/learning แต่ไม่มั่ว)
2. “**Runbook 1 หน้า**” (MI Card → Demo Card → Sweep → Gallery)
3. “**Glossary**” (คำศัพท์ไทย–อังกฤษ–สัญลักษณ์ UET) ให้ทั้งคนทั่วไปและสายเทคนิคใช้คำตรงกัน

---
## Insight

สิ่งที่ทำให้ UET “คนอ่านเข้าใจ” ไม่ใช่กราฟมากขึ้น แต่คือ **เล่าโลก 1 โลกให้เห็น** ด้วย 3 สิ่ง:

- **World rules** = Ω + constraints + dynamics gate
- **Agents/NPC** = state (C/I pattern) ที่ถูกโลกบังคับให้ไหล
- **Meaning** = Value/Conflict/Phase ที่ “ผูกกับภาพ” ได้ (snapshots/terrain)

---
## Part 4.4 — UET as a World Simulator (Public Chapter + Runbook + Glossary)

## 1) บทอธิบายสำหรับคนทั่วไป (Story-teller / YouTube style)

### UET คืออะไร (ไม่ใช่สูตรตอบ แต่เป็น “โลกจำลอง”)

ให้คิดว่า UET เป็น “เครื่องจำลองโลก” ที่มี **ภูมิประเทศ** ชื่อว่า Ω

- Ω บอกว่า “ตำแหน่ง/รูปแบบไหนอยู่สบาย” (หลุม)
    
- “รูปแบบไหนอยู่ยาก” (สัน/ชัน)
    

เราไม่ได้บอกระบบว่า “ต้องไปตรงนี้”  
เราแค่สร้างโลก (Ω) แล้วปล่อยสิ่งหนึ่ง (seed) ลงไป  
มันจะ **ค่อย ๆ ปรับตัว** จนไปอยู่ในรูปแบบที่ “อยู่ได้” (สมดุล/attractor)

### สิ่งหนึ่งคืออะไร

“สิ่งหนึ่ง” ใน UET ไม่จำเป็นต้องเป็นสัตว์หรือวัตถุ  
มันคือ **รูปแบบของสถานะ** (pattern) ที่กำลังเปลี่ยนไปตามเวลา  
ในโค้ดตอนนี้ เราแทนมันด้วย field 1–2 ชนิด:

- `C(x,y,t)` และ/หรือ `I(x,y,t)`
    

### สมดุลคืออะไร

สมดุลไม่ใช่เลขเดียว แต่มักเป็น “หลุมหลายหลุม”

- seed ต่างกัน → อาจตกคนละหลุม
    
- เราใช้หลาย seed เพื่อดูว่า “โลกนี้ชอบหลุมไหน” (robustness/basin)
    

### ทำไมมันเหมือนเกม / learning / NPC ได้

- **World rules**: Ω + กติกาอัปเดต (dynamics)
    
- **NPC**: state ที่ถูกบีบให้ปรับตัวเพื่อ “อยู่รอดในโลกนั้น”
    
- **Learning (แบบไม่ต้องเรียก RL)**: เพราะมันปรับตัวลดความตึง/ลงหลุมเหมือน “เรียนรู้ทางออกที่เสถียร”
    

> สำคัญ: อย่าอ้างว่าเป็น RL agent ตรง ๆ  
> ให้พูดว่า “world dynamics ที่ให้พฤติกรรมคล้ายการเรียนรู้” เพราะมันเป็นกระบวนการปรับตัวภายใต้แรง/ข้อจำกัด

---

## 2) บทอธิบายเชิงวิชาการ (Formal / Mathematical)

### Core objects

- **State**: (X) (เช่น (C) หรือ ((C,I))) บนโดเมน 2D ใน implementation ปัจจุบัน
    
- **World/Landscape**: energy functional (\Omega[X;\theta]) ซึ่งแตกได้เป็น:
    
    - local potential (ศักยภาพ): ( \Omega_{\text{pot}} )
        
    - coupling (ปฏิสัมพันธ์): ( \Omega_{\text{coup}} )
        
    - gradient/interface cost (ความขัดแย้งเชิงโครงสร้าง): ( \Omega_{\text{grad}} )
        
- **Dynamics**: dissipative update ที่พยายามลด (\Omega) พร้อม **accept/reject + dt backtracking** เพื่อบังคับ monotonicity (Lyapunov-like gate)
    

### Dual-equilibrium

- **Introvert equilibrium**: การเข้าที่ของ entity (state เข้าสู่ attractor; Ω ลดแล้วนิ่ง)
    
- **Extrovert equilibrium**: การจัดระเบียบของระบบรวม (อ่านผ่าน Value/Conflict/phase robustness และ (roadmap) feedback)
    

### Operational semantics (ยึด Part 2)

- **Value**: (V_{\Delta E}=\Omega(0)-\Omega_{\text{final}}) (หรือ (-\Omega_{\text{final}}))
    
- **Conflict (หลัก)**: (C_G=\Omega_{\text{grad,final}}) (แปลเป็น “รอยต่อ/ความตึง” ได้ และทำภาพ Ω-density ได้)
    

---

## 3) Runbook 1 หน้า (MI → Demo → Sweep → Gallery)

### Step 0 — ห้ามข้าม

ก่อนทำ sweep ให้ทำ **Demo 1 case** ให้ “เห็นภาพ” ก่อนเสมอ

---

### Step 1 — ทำ MI Card (10 นาที)

กรอกให้ครบ 4 ช่องนี้อย่างน้อย:

1. ใช้ `C_only` หรือ `C_I`
    
2. Potential (P): quartic + tilt (`a, delta, s`)
    
3. Conflict (R): gradient penalty (`kC,kI` หรือ `k_ratio`)
    
4. Flow (J): mobility + `dt, T` + geometry `N,L`
    

ผลลัพธ์: ได้ “สัญญา” ว่าจะ export อะไรและวัด Value/Conflict ยังไง

---

### Step 2 — ทำ Demo Case 1 จุด (เรื่องเดียว แต่ครบทุกมุม)

เลือกพารามิเตอร์ 1 ชุด + seed 1 ค่า (หรือ seed ตัวแทน)

**Demo-ready ต้องมี**

- start/end ของ C (และ I ถ้ามี)
    
- evolution (gif/mp4 หรืออย่างน้อย snapshots 10–20 เฟรม)
    
- terrain อย่างน้อย 1 แบบ: surface(C/I) หรือ Ω-density terrain
    
- Ω(t), bias(t), Value, Conflict, Phase label
    
- caption 5 บรรทัด (Potential/Conflict/Flow/Result)
    

> ถ้ายังไม่มี snapshots ของ field: ให้ถือว่ายัง “Demo ไม่เกิด” ต่อให้ summary เยอะก็ไม่ช่วย public

---

### Step 3 — สรุป Value–Conflict ของเดโม

วางจุดเดโมลง “Value–Conflict plane” แล้วบอกว่าอยู่ quadrant ไหน  
(จัดระเบียบดี / จ่ายแพง / นิ่งแต่ไม่เกิด / วุ่นวาย)

---

### Step 4 — ค่อย Sweep (2 แกนพอ)

เลือกแกน 2 ตัว (เช่น `beta × s_tilt` หรือ `beta × k_ratio`)

- ต่อ 1 grid-point รันหลาย seed เพื่อ robustness
    
- ผล sweep ใช้เพื่อ “หา archetype” ไม่ใช่ใช้สอนคนจากศูนย์
    

---

### Step 5 — เลือก 3–5 archetype ทำเป็น Demo Cards

- SYM stable
    
- BIAS_C
    
- BIAS_I
    
- High-conflict boundary
    
- (optional) multi-attractor / seed-sensitive
    

---

### Step 6 — ทำ Gallery

หน้า index แสดง thumbnail + คำอธิบายสั้น  
คลิกเข้าไปเห็น Demo Card (ภาพ+gif+terrain+Value/Conflict+phase)

---

## 4) Glossary (Thai–English–UET mapping)

### แกนคำหลัก

- **สิ่งหนึ่ง / Entity**: ระบบย่อยที่มี state และกลไกการเปลี่ยนแปลง (Introvert view)
    
- **ระบบรวม / Open system**: สนามเดียวที่มีหลายกระบวนการ/แรงปะทะและ feedback (Extrovert view)
    
- **สนาม / Field (world rules)**: นิยามกฎและภูมิประเทศของการไหล = (\Omega) + constraints
    
- **สถานะ / State**: สิ่งที่เปลี่ยนตามเวลา เช่น (C(x,y,t), I(x,y,t))
    
- **สมดุล / Equilibrium**: attractor/phase + ความทนต่อ seed (ไม่ใช่เลขจุดเดียว)
    
- **หลุม / Basin**: บริเวณเริ่มต้นที่ไหลไป attractor เดียวกัน
    
- **seed / initial condition**: จุดเริ่ม state เพื่อสำรวจ basin
    

### UET terms ที่ต้องใช้ให้ตรง

- **Ω (Omega functional)**: พลังงาน/ภูมิประเทศของโลก (รวมทุกเทอม)
    
- **Potential (P)**: เทอม local ที่เป็นแรงขับ (quartic + tilt)
    
- **Coupling (β)**: ปฏิสัมพันธ์ C–I (แรงประสาน/แรงปะทะ)
    
- **Gradient penalty (kC,kI, κ)**: ต้นทุนรอยต่อ/ความตึงเชิงพื้นที่ (Conflict เชิงโครงสร้าง)
    
- **Flow / Mobility (M, MC, MI)**: ความเร็วการปรับตัว/การไหล
    
- **accept/reject + backtracking**: กลไกบังคับให้ Ω ไม่เพิ่ม (เสถียรภาพเชิงตัวเลข/เชิงไลยาพูนอฟในทางปฏิบัติ)
    
- **Phase labels**: `BIAS_C`, `BIAS_I`, `SYM` (ผลลงเอยเชิงเฟส)
    
- **Value**: (V_{\Delta E}) หรือ (-\Omega_{\text{final}}) (จัดระเบียบ/เสถียร)
    
- **Conflict**: (\Omega_{\text{grad,final}}) (หลัก) หรือ friction/backtracks (สำรอง)
    

---

## Next Step

Part ถัดไปที่เหมาะสุดตอนนี้มี 2 ทาง (ไม่ต้องเลือกนาน):

1. **Part 5: Open-system/feedback spec** (ทำ extrovert ให้ครบ: forcing/resources/multi-process)
    
2. **Part 4.8: Demo Card “canonical 1 ใบ” แบบเต็มหน้า** (เป็นแม่แบบหน้าเดียวสำหรับ public)
    

ถ้ามึงพิมพ์ “ต่อ” อีกรอบ กูจะทำ **Part 4.8** ก่อน (เพราะมันทำให้ “เห็นภาพแบบ YouTube” ได้เร็วสุด และจะเป็นหัวหอกของ public).


---

# 000.04/5

## TL;DR

นี่คือ **Part 4.5: Demo Card (canonical 1 ใบ แบบเต็มหน้า)** — แม่แบบหน้าเดียวสำหรับ public ที่ “เล่าเรื่องด้วยภาพ” ก่อน แล้วค่อยยืนยันด้วยตัวเลข (Value/Conflict/Phase) โดยยึด framework ของเรา 2 ชั้น (Introvert/Extrovert) และยึดของจริงที่รันได้ใน UET ปัจจุบัน

---

## Insight

Demo Card ใบเดียวต้องทำ 3 อย่างให้จบในหน้าเดียว:

1. **คนทั่วไปเห็นภาพ** ว่าระบบ “ไหล/ปรับตัว/ลงหลุม” ยังไง
    
2. **คนเทคนิค rerun ได้** (มี params/seed/grid/time ครบ)
    
3. **คนวิชาการอ่านได้** ว่ามันสอดคล้องกับ Ω / Potential–Conflict–Flow ยังไง
    

---

## Part 4.5 — UET Canonical Demo Card (One-page Template)

> แนะนำให้ใช้ไฟล์นี้เป็น `README_demo.md` ในโฟลเดอร์เดโมหนึ่งอัน (1 case / 1 parameter set)  
> ใส่รูป/gif ไว้ตามชื่อไฟล์มาตรฐานด้านล่าง

---

## 0) Title + One-liner (หัวเรื่องที่คนอ่านแล้วเข้าใจทันที)

**Demo ID:** `DEMO____`  
**ชื่อเดโม:** `_____`  
**One-liner:** “เดโมนี้แสดงว่าเมื่อ ___ (Potential) แข่งกับ ___ (Conflict) ภายใต้การไหลแบบ ___ (Flow) ระบบจะลงเอยเป็น ___ (Phase)”

**ผลลัพธ์สรุป (อ่านเร็ว 5 วินาที):**

- **Phase:** `BIAS_C / BIAS_I / SYM`
- **Value:** `_____` (นิยาม: (V_{\Delta E}=\Omega(0)-\Omega_{final}) หรือ (-\Omega_{final}))
- **Conflict:** `_____` (นิยามหลัก: (\Omega_{grad,final}) | สำรอง: backtrack/friction)
- **Robustness (optional):** `_____` (เช่น % seeds ที่ได้ phase เดียวกัน)

---

## 1) What you should see (คนทั่วไปควร “เห็นอะไร”)

**ภาพรวมแบบภาษาคน (3 bullet):**

- ตอนเริ่ม: `_____` (อธิบาย pattern/สภาพเริ่มต้นสั้นๆ)
- ระหว่างทาง: `_____` (เกิดการแยกตัว/เกิดโดเมน/เกิดรอยต่อ ฯลฯ)
- ตอนจบ: `_____` (ล็อกฝั่งไหน/สมมาตร/มีรอยต่อเยอะ)

**คำแปล framework (P/R/J):**

- **Potential (P):** `_____` (แรงขับ/สิ่งที่ “อยากให้เกิด”)
- **Conflict (R):** `_____` (แรงต้าน/ราคาที่ต้องจ่าย/รอยต่อ)
- **Flow (J):** `_____` (กระบวนการไหล/ความเร็วการปรับตัว)

---

## 2) Visual Story (นี่คือหัวใจของเดโม)

### 2.1 Start → End (ภาพก่อน/หลัง)

**C field**

- `figs/state_C_start.png`
- `figs/state_C_end.png`

**I field (ถ้ามี)**

- `figs/state_I_start.png`
- `figs/state_I_end.png`

> คำอธิบายใต้ภาพ (1–2 ประโยค):  
> “ภาพ C แสดง ___; ภาพ I แสดง ___; จุดที่สว่าง/เข้มหมายถึง ___”

### 2.2 Evolution (เห็นการ “ไหล/เรียนรู้”)

- `figs/evolution.gif` _(หรือ mp4 ก็ได้)_

> Caption 1 บรรทัด: “สังเกตว่าระบบเริ่ม ___ แล้วค่อย ๆ ___ ก่อนจะ ___”

### 2.3 Terrain (ภาพแบบ ‘ภูเขา-หลุม’ ให้คนเข้าใจสนาม)

เลือกอย่างน้อย 1 อย่าง (ยิ่งมีครบยิ่งดี)

**Option A: Ω-density terrain (แนะนำที่สุดสำหรับ Conflict)**

- `figs/terrain_omega_density.png`  
    คำอธิบาย: “บริเวณสว่าง/สูงคือความตึง/รอยต่อ (Conflict สูง)”

**Option B: 3D surface ของ C หรือ I**

- `figs/surface_C.png` (หรือ `surface_I.png`)  
    คำอธิบาย: “z=ค่าของ field ทำให้เห็นรูปทรง/pattern ชัดแบบ 3D”

---

## 3) Metrics (ยืนยันความเข้าใจด้วยตัวเลข ไม่ใช่ให้คนอ่านตัวเลขแล้วเดา)

### 3.1 Curves

- `figs/curve_omega.png` (Ω(t))
- `figs/curve_bias.png` (bias(t) หรือ metric ที่ validator ใช้)

**อ่านกราฟแบบคนทั่วไป (2 บรรทัด):**

- Ω(t): “ลดลงแล้วนิ่ง” แปลว่า “เข้าที่”
- bias(t): “หนีไปฝั่ง C/I” แปลว่า “ล็อกฝั่งนั้น”

### 3.2 Decomposition (ถ้ามี — ช่วยอธิบาย Value/Conflict ให้คมมาก)

- `figs/curve_omega_terms.png` (Ω_pot, Ω_coup, Ω_grad)

**ตีความ 1 บรรทัด:**  
“Conflict สูงเพราะ Ω_grad สูง → มีรอยต่อ/ความตึงเชิงพื้นที่มาก”

---
## 4) Result Interpretation (เอา framework มาปิดจบให้เข้าใจ)

### 4.1 Phase label แปลว่าอะไร “ในภาพ”

- **BIAS_C:** ภาพปลายทางแสดงว่า `_____` (อธิบายจาก state_end)
- **BIAS_I:** `_____`
- **SYM:** `_____`

### 4.2 Value vs Conflict (ปักหมุดบน plane)

**Value =** `_____` เพราะ `_____`  
**Conflict =** `_____` เพราะ `_____`

**Quadrant:**

- `High Value / Low Conflict` หรือ `High Value / High Conflict` ฯลฯ  
    **คำแปลคนทั่วไป 1 ประโยค:**  
    “เดโมนี้คือกรณี ___ (เช่น ‘จัดระเบียบดีแต่ต้องจ่ายแพง’)”

---

## 5) Reproducibility (ให้คนเทคนิค rerun ได้ทันที)

### 5.1 Minimal Setup

- **model_type:** `C_only / C_I`
- **seed:** `_____`
- **grid:** `N=___, L=___, dim=2`
- **time:** `dt=___, T=___`
- **params:** `beta=___, delta=___, s_tilt=___, kC=___, kI=___, asym=___, ...`

### 5.2 Run command (ใส่คำสั่งจริงของ repo)

```bash
python scripts/run_suite.py --matrix matrices/_____.csv --out runs/DEMO____
```

---
## 6) Files in this demo (โครงไฟล์มาตรฐาน)

```
DEMO____/
  demo_manifest.json
  timeseries.csv
  summary.json
  snapshots/                 # (ต้องมี) 10–20 frames อย่างน้อย
    C_t0000.npy (or .npz)
    I_t0000.npy (optional)
    ...
  figs/                      # (ต้องมี)
    state_C_start.png
    state_C_end.png
    state_I_start.png (optional)
    state_I_end.png   (optional)
    evolution.gif
    terrain_omega_density.png (recommended)
    surface_C.png (optional)
    curve_omega.png
    curve_bias.png
    curve_omega_terms.png (optional)
  README_demo.md             # เอกสารหน้านี้
```

---
## Appendix A — demo_manifest.json (สคีมาขั้นต่ำ)

> ใช้เพื่อให้ “ไม่ต้องเดา” ว่าเดโมนี้รันด้วยอะไร

```json
{
  "demo_id": "DEMO____",
  "title": "_____",
  "model_type": "C_I",
  "seed": 10,
  "geometry": {"dim": 2, "N": 128, "L": 1.0},
  "time": {"dt": 0.001, "T": 1.0, "steps_saved": 20},
  "params": {
    "beta": 1.0,
    "delta": 3.0,
    "s_tilt": 0.2,
    "kC": 1.0,
    "kI": 1.0,
    "asym": 0.0
  },
  "outputs": {
    "phase_label": "BIAS_C",
    "value_metric": {"name": "V_deltaE", "value": 0.0},
    "conflict_metric": {"name": "Omega_grad_final", "value": 0.0}
  },
  "notes": "Potential=___, Conflict=___, Flow=___"
}
```

---
## Appendix B — Demo-ready Acceptance Checklist (ต้องผ่านก่อนขึ้น public)

-  มี **state_start/end** ของ C (และ I ถ้าเป็น C_I)
-  มี **evolution.gif** หรือ snapshots ≥ 10 frames
-  มี **terrain** อย่างน้อย 1 รูป (Ω-density แนะนำที่สุด)
-  มี Ω(t) และ bias(t) curves
-  Value/Conflict/Phase ระบุชัด + อธิบายจาก “ภาพ” ได้
-  มี `demo_manifest.json` + params/seed/grid/time ครบ
-  (ถ้าพบ) backtracking/fail flags ต้องอธิบายใน README

---

## Plain-Language Interpretation (สรุปแบบคนทั่วไป)

เดโม 1 ใบที่ดีต้องเหมือนคลิป YouTube:  
เห็น “ก่อน–หลัง”, เห็น “การเปลี่ยนแปลง”, เห็น “ภูเขา-หลุมของสนาม”, แล้วค่อยมีตัวเลขมายืนยันว่า **มันจัดระเบียบได้มากแค่ไหน (Value)** และ **ต้องปะทะกันแค่ไหน (Conflict)**

---

## Next Step

ถัดไป (Part 4.9) กูจะทำ “**แม่แบบ Gallery**” ที่เอา Demo Cards หลายใบมาเรียงเป็นหน้าเดียว (แบ่ง archetype: SYM/BIAS_C/BIAS_I/High-conflict/Multi-attractor) พร้อมกติกาว่า “1 archetype ต้องมีอะไร” เพื่อให้ public อ่านแล้วไม่หลง

พิมพ์ “ต่อ” อีกที เดี๋ยวกูทำ Part 4.9 ให้เลย.

---
# 000.04/6

## TL;DR

**Part 4.6 = แม่แบบ “Public Gallery”** ที่เอา Demo Cards (Part 4.8) หลายใบมาเรียงให้คนคลิกแล้วเข้าใจทันที โดยไม่ต้องอ่าน matrix/heatmap ก่อน

- แบ่งเป็น **5 archetypes** (SYM / BIAS_C / BIAS_I / High-conflict / Multi-attractor)
- ใช้ **Demo Card เป็นหน่วยหลัก** (1 เรื่อง = 1 หน้า)
- หน้า Gallery ทำหน้าที่เป็น “สารบัญแบบภาพ” + “แผนที่ความหมาย (Value–Conflict)”
- Sweep/heatmap (ถ้ามี) เป็น “navigator” ทีหลัง ไม่ใช่หน้าแรก

---
## Insight

Public จะไม่อ่านงานเราแบบ “ตาราง/กราฟ” เขาอ่านแบบ “คลิกดูเรื่อง”  
ดังนั้น Gallery ต้องทำให้:

1. เข้าใจ “คำศัพท์” จากภาพ (สิ่งหนึ่ง/สนาม/สมดุล)
2. เห็น archetype ของพฤติกรรม (BIAS_C คือหน้าตาแบบไหน)
3. ค่อยเปิดทางให้คนเทคนิคไปดู sweep/regression ต่อ

---
## Part 4.9 — Public Gallery Template (Docs-ready)

## 1) เป้าหมายของ Gallery

Gallery ต้องตอบคำถาม 3 ข้อให้ได้ใน 30 วินาที:

1. UET ทำให้ “เกิดอะไร” บนหน้าจอ?
2. คำว่า BIAS_C / BIAS_I / SYM แปลเป็น “ภาพ” ยังไง?
3. Value/Conflict คืออะไร และมันไปอยู่ตรงไหนของผลลัพธ์?

---
## 2) หลักการออกแบบ (ห้ามหลุดกลับไปยุคกราฟอ่านไม่ออก)

- หน้าแรก = **ภาพ + เรื่องสั้น + ป้าย (Phase/Value/Conflict)**
- 1 คลิก = เข้า **Demo Card** (Part 4.8)
- ไม่โยน heatmap/sweep ใส่หน้าคนทันที
- ทุกเดโมต้องมี **terrain/animation** อย่างน้อย 1 อย่าง ไม่งั้น “ห้ามขึ้น Gallery”

---
## 3) โครงสร้าง Gallery (โฟลเดอร์/หน้าที่แนะนำ)

> อันนี้เป็น “โครงเอกสาร” ไม่บังคับโค้ด

```
docs/
  gallery/
    index.md
    archetypes/
      SYM.md
      BIAS_C.md
      BIAS_I.md
      HIGH_CONFLICT.md
      MULTI_ATTRACTOR.md
    demos/
      DEMO_0001/README_demo.md
      DEMO_0002/README_demo.md
      ...
    registry.json   (หรือ registry.yaml)
```

- `gallery/index.md` = หน้าแรก (สารบัญภาพ + แผนที่ Value–Conflict)
- `archetypes/*.md` = หน้าอธิบาย “แบบแผน” + ลิงก์เดโมที่เป็นตัวแทน
- `demos/DEMO_xxxx/README_demo.md` = หน้าเดโมจริง (ตาม Part 4.8)
- `registry.*` = รายการเดโมทั้งหมดพร้อม metadata (จะสร้างมือหรือ auto ก็ได้)

---

## 4) กติกา “Archetype” (5 หมวดที่ต้องมี)

แต่ละหมวดต้องมี:

- 1 ย่อหน้าอธิบาย “มันคืออะไร” แบบคนทั่วไป
- 1 ย่อหน้าอธิบาย “มันเกิดจาก P/R/J ยังไง” แบบเทคนิค
- รายการเดโมตัวแทน 2–6 ใบ (ไม่ต้องเยอะ)

### 4.1 SYM (สมมาตร/อยู่ร่วมกัน)

- **ภาพที่คาดหวัง:** C และ I ไม่ครอบงำกันชัด หรือ pattern สมมาตร
- **ความหมาย:** สนามไม่เอน/แรงขับสมดุลกัน
- **Value/Conflict:** มักอยู่ “Value กลาง–สูง / Conflict ต่ำ–กลาง”

### 4.2 BIAS_C (ล็อกฝั่ง C)

- **ภาพที่คาดหวัง:** C เด่นชัด (domain/structure ของ C)
- **ความหมาย:** หลุมฝั่ง C ลึกกว่า/มีแรงเอนให้ C ชนะ
- **Value/Conflict:** แล้วแต่ kC/kI (ถ้า interface เยอะ → conflict สูง)

### 4.3 BIAS_I (ล็อกฝั่ง I)

- mirror ของ BIAS_C

### 4.4 HIGH_CONFLICT (ชายแดน/รอยต่อ/ตึงมาก)

- **ภาพที่คาดหวัง:** interface เยอะ, Ω-density สว่างตามขอบ, pattern แตกละเอียด
- **ความหมาย:** potential ดึงคนละทาง + gradient penalty ทำให้ “ต้องจ่ายราคา”
- **Value/Conflict:** “Conflict สูง” ชัดเจน (นี่คือหมวดที่ช่วยอธิบาย Conflict ให้คนเข้าใจที่สุด)

### 4.5 MULTI_ATTRACTOR (seed-sensitive)

- **ภาพที่คาดหวัง:** พารามิเตอร์เหมือนกันแต่ seed ต่าง → ลงเอยคนละแบบ
- **ความหมาย:** โลกมีหลายหลุมแข่งกัน basin ใกล้ๆ กัน
- **Value/Conflict:** “Robustness ต่ำ” (แปลเป็นระบบรวมยังไม่แน่นอน)

---
## 5) Gallery Index (หน้าแรก) — Template (Markdown)

> นี่คือหน้าที่ public ต้องเห็นก่อนอย่างอื่น

### 5.1 ส่วนหัว

- 3 ประโยค: UET คือ world simulator + สมดุลคือ attractor + Value/Conflict คือแกนความหมาย

### 5.2 Archetype Tiles (คลิกแล้วเข้า)

แสดงเป็น 5 กล่อง:

- ชื่อหมวด
- thumbnail 1 รูปจากเดโมตัวแทน
- 1 บรรทัด “มันคืออะไร”

### 5.3 Value–Conflict Map (ภาพเดียวจบ)

- วางจุดของเดโมตัวแทน 10–30 จุด (พอ)
- สีตาม phase (SYM/BIAS_C/BIAS_I)
- คลิกจุดแล้วลิงก์ไป Demo Card

> จุดนี้คือ “แผนที่ความหมาย” ที่แทน heatmap 2D ได้สำหรับ public

**ตัวอย่างโครง index.md (ตัดให้สั้น)**

```md
# UET Gallery

UET is a world simulator defined by an energy landscape Ω.  
Seeds are starting points; outcomes reveal attractors (equilibria).  
We interpret outcomes using Phase + Value–Conflict.

## Archetypes
- SYM — coexistence / symmetric stability
- BIAS_C — C-dominant attractor
- BIAS_I — I-dominant attractor
- HIGH_CONFLICT — many interfaces / high Ω_grad
- MULTI_ATTRACTOR — seed-sensitive outcomes

## Value–Conflict Map
(figure: value_conflict_map.png)
Legend: color = phase, y = conflict (Ω_grad), x = value (ΔΩ)
```

---
## 6) Registry Spec (metadata ที่ต้องมี เพื่อให้ gallery ไม่มั่ว)

ไม่จำเป็นต้องซับซ้อน แค่มี field เหล่านี้พอ:

```json
[
  {
    "demo_id": "DEMO_0001",
    "title": "Beta tilt drives C dominance",
    "path": "docs/gallery/demos/DEMO_0001/README_demo.md",
    "phase": "BIAS_C",
    "value": 1.234,
    "conflict": 0.456,
    "robustness": 0.9,
    "params": {"beta": 1.0, "delta": 3.0, "s_tilt": 0.2, "k_ratio": 1.0},
    "assets": {
      "thumb": "docs/gallery/demos/DEMO_0001/figs/state_C_end.png",
      "gif": "docs/gallery/demos/DEMO_0001/figs/evolution.gif",
      "terrain": "docs/gallery/demos/DEMO_0001/figs/terrain_omega_density.png"
    },
    "tags": ["C_I", "terrain", "introvert", "extrovert"]
  }
]
```

**กติกา:** ถ้าไม่มี `thumb` + `gif` อย่างน้อย 1 → ไม่ให้ขึ้นหน้าแรก

---

## 7) “Navigator” สำหรับ Sweep/หลายมิติ (ไว้ชั้นถัดไป ไม่ใช่หน้าแรก)

เพื่อแก้ปัญหาที่มึงย้ำว่า “สมการไม่ควรถูกเล่าเป็น 2D”:

### 7.1 แนวคิดที่ถูกต้อง

- เราไม่สามารถ “โชว์ 4D” ให้คนเข้าใจในภาพเดียวได้
    
- วิธีที่ถูกคือ **slice navigator**
    
    - fix ตัวแปรบางตัว
        
    - โชว์ 2D map ทีละระนาบ
        
    - แต่ทุกจุดต้อง “ลิงก์กลับไป Demo Card” เพื่อเห็นของจริง
        

### 7.2 หน้า Navigator template

- เลือก sweep 1 ชุด (เช่น beta×k_ratio)
    
- แสดง heatmap 1 รูป (optional)
    
- มี “Representative demos” 6 จุด: มุมทั้งสี่ + boundary + center  
    (นี่คือจุดที่คนจะเข้าใจ)
    

---

## 8) Acceptance Rules (อะไรขึ้น public ได้)

**ขึ้น Gallery ได้** เมื่อ:

- ผ่าน Demo-ready checklist (Part 4.8 Appendix B)
- มีภาพที่ “อธิบาย conflict” ได้อย่างน้อย 1 (terrain Ω-density หรือ equivalent)
- มี caption ที่พูด P/R/J + ผลลัพธ์ 3–5 บรรทัด

**ยังไม่ขึ้น Gallery** เมื่อ:

- มีแค่ summary/CSV แต่ไม่มี snapshots/gif/terrain
- มีแค่ heatmap/sweep แต่ไม่มี demo story

---

## Plain-Language Interpretation

Gallery คือ “สารคดี” ไม่ใช่ “รายงานผลทดลองดิบ”  
เดโม 1 ใบคือ “ฉากหนึ่ง” ที่เห็นการเปลี่ยนแปลงจริง  
Archetype คือ “หมวดของฉาก” ที่ช่วยให้คนจำได้ว่า BIAS_C หน้าตาประมาณไหน  
Value–Conflict map คือ “แผนที่ความหมาย” ที่บอกว่าฉากไหนจัดระเบียบดี/ปะทะหนัก

---

## Next Step

Part ถัดไปมี 2 อันที่ “จำเป็นจริง” เพื่อให้ Gallery เกิดได้ในทางปฏิบัติ:

### **Part 4.10 — Canonical Export Contract**

กำหนดมาตรฐานการ export จาก run ให้ได้:

- snapshots (C/I)
- ω_density หรือ ω_terms
- gif + thumbs
- registry entry

### **Part 5 — Open-system/feedback spec**

ขยับจาก “สนามคงที่” → “สนามเปลี่ยนตาม environment/resources” (extrovert เต็ม)

มึงพิมพ์ “ต่อ” อีกที กูจะทำ **Part 4.10** ก่อน (เพราะมันทำให้จาก “แนวคิด” กลายเป็น “ของที่ generate ได้จริง” แล้วค่อยไป Part 5).

---
# 000.04/7

## TL;DR

**Part 4.7 = “Canonical Export Contract”** คือสัญญามาตรฐานว่า “1 run” ต้อง export อะไรบ้าง (ไฟล์/ชื่อ/โครงสร้าง/สคีมา) เพื่อให้:

- ทำ **Demo Card / Gallery** ได้แบบ YouTube-level
- ทำซ้ำ (reproducible) ได้
- ไม่รก ไม่กระจัดกระจาย ไม่ต้องเดาว่าไฟล์ไหนคืออะไร

แกนคือ: **Run Dir = หน่วยความจริง**, แล้วทุกอย่าง (plots/gif/registry/gallery) “ประกอบขึ้น” จากของใน run dir เท่านั้น

---
## Insight

ก่อนหน้านี้เรามี “เครื่องรัน + summary” แต่ขาด “สินทรัพย์ภาพ” (state snapshots / terrain / omega decomposition)  
ดังนั้น public มันไม่เข้าใจ

Export Contract จะ “ล็อก” ว่า:
- ต้องมี **state snapshots** (ขั้นต่ำ)
- ต้องมี **manifest** ที่บอก params/seed/grid/time
- ต้องมี **metrics** (Ω/bias/value/conflict/phase)
- และควรมี **energy decomposition** เพื่ออธิบาย Conflict เป็นภาพได้จริง

---

## Part 4.10 — Canonical Export Contract (v0.9 Draft)

## 0) หลักการ (Non-negotiable)

1. **Run directory เป็นหน่วยความจริง**: ทุก output ที่ใช้เล่าเรื่อง/ทำ gallery ต้องสร้างได้จากไฟล์ใน run_dir
2. **ชื่อไฟล์ต้องเสถียร**: public docs, scripts, และ CI ต้องอ้างชื่อเดียวกัน
3. **ไฟล์ “เล่าเรื่องด้วยภาพ” ต้องมาก่อน heatmap**: snapshot/gif/terrain คือ core asset
4. **No hidden meaning**: ทุกตัวเลข/ไฟล์ต้องมี metadata ระบุหน่วย/นิยาม/เวอร์ชัน

---

## 1) Run Directory Layout (มาตรฐาน)

โครงสร้างขั้นต่ำที่ “แนะนำให้ยึด”:

```
runs/<RUN_ID>/                      # หนึ่ง run = หนึ่ง case หนึ่ง seed
  manifest.json                     # MUST
  params.json                       # SHOULD (หรือฝังใน manifest)
  timeseries.csv                    # MUST (ขั้นต่ำ Ω(t), bias(t))
  summary.json                      # MUST (phase/value/conflict/final stats)
  snapshots/                        # MUST สำหรับ demo-ready
    state_t0000.npz                 # MUST (แนะนำ npz)
    state_t0001.npz
    ...
  energy/                           # SHOULD
    omega_terms_t0000.npz           # SHOULD (Ω_pot, Ω_coup, Ω_grad per-grid)
    ...
  figs/                             # SHOULD (generate ได้จาก snapshots)
    state_C_start.png
    state_C_end.png
    state_I_start.png (optional)
    state_I_end.png   (optional)
    evolution.gif
    terrain_omega_density.png
    surface_C.png (optional)
    curve_omega.png
    curve_bias.png
    curve_omega_terms.png (optional)
  README_demo.md                    # MAY (public-facing; Demo Card)
  logs/                             # MAY
    run.log
    backtracking.json
```

> **MUST** = ถ้าไม่มีถือว่า run ไม่สมบูรณ์  
> **SHOULD** = ไม่มีได้ แต่จะทำ demo/gallery ยากมาก  
> **MAY** = มีเพื่อความสะดวก/สื่อสาร

---

## 2) manifest.json (MUST) — สคีมาขั้นต่ำ

เป้าหมาย: ให้ rerun ได้โดย “ไม่ต้องเดา” และให้ trace ได้ว่า output มาจากอะไร

### Minimal schema

```json
{
  "run_id": "RUN_2025_..._seed10_case034",
  "created_at": "2025-12-20T00:00:00Z",
  "code_version": {
    "git_commit": "____",
    "uet_version": "0.8.5+",
    "harness_version": "____"
  },
  "model": {
    "model_type": "C_I",
    "dim": 2,
    "grid": {"N": 128, "L": 1.0, "dx": 0.0078125},
    "time": {"dt": 0.001, "T": 1.0, "steps": 1000}
  },
  "seed": 10,
  "params": {
    "beta": 1.0,
    "kC": 1.0,
    "kI": 1.0,
    "k_ratio": 1.0,
    "asym": 0.0,
    "potC": {"type": "quartic", "a": -1.0, "delta": 3.0, "s": 0.2},
    "potI": {"type": "quartic", "a": -1.0, "delta": 3.0, "s": -0.2}
  },
  "outputs": {
    "paths": {
      "timeseries": "timeseries.csv",
      "summary": "summary.json",
      "snapshots_dir": "snapshots/"
    }
  }
}
```

**Rules**

- `code_version` ต้องมีอย่างน้อย 1 ตัวระบุต้นทาง (git_commit หรือ uet_version)
    
- `grid/time/seed/params` ต้องครบ
    
- ห้ามเขียนค่าซ้ำซ้อนแบบไม่จำเป็น: manifest คือ “แหล่งเดียว”
    

---

## 3) snapshots (MUST สำหรับ demo-ready) — รูปแบบไฟล์

จุดประสงค์: ให้เราทำ gif/terrain/ภาพก่อน–หลัง ได้เสมอ
### 3.1 แนะนำฟอร์แมต

- `state_tXXXX.npz` (แนะนำ) ภายในมี keys:
    - `t` (float หรือ int step)
    - `C` (2D array)
    - `I` (2D array, optional)
    - `meta` (optional: dt, step, normalization)

### 3.2 Sampling policy (สำคัญ)

ไม่ต้อง save ทุก step ให้หนัก:

- **MUST:** อย่างน้อย 10 frames ต่อ run สำหรับ demo (เช่น 0%, 10%, …, 100%)
- **SHOULD:** log-scale frames (ต้นเยอะ ปลายห่าง) ถ้าระบบเร็วช่วงต้น
- **SHOULD:** เก็บ start/end เสมอ

> นี่คือ “กล้อง” ของเรา ถ้าไม่มี = ไม่มี YouTube-level

---
## 4) timeseries.csv (MUST) — คอลัมน์ขั้นต่ำ

เพื่อให้ยืนยันสมดุล/การไหลได้แบบไม่มั่ว

**MUST columns**

- `t`
- `Omega` (หรือ `Omega_total`) — ให้ตกลงชื่อเดียวในโปรเจกต์
- `bias` (หนึ่งคอลัมน์ที่ validator ใช้จริง; เช่น mean(C)-mean(I) หรือ metric ที่ทีมใช้)

**SHOULD columns**

- `mean_C`, `mean_I`
- `Omega_pot`, `Omega_coup`, `Omega_grad` (ถ้าคำนวณได้; จะช่วย Part 2/3/Value-Conflict มาก)

---
## 5) summary.json (MUST) — “สรุปเชิงความหมาย”

ให้สั้นแต่เป็นแหล่งจริงของ phase/value/conflict

**MUST fields**

- `status`: PASS/FAIL (หรือ accepted flag)
- `phase_label`: BIAS_C/BIAS_I/SYM
- `Omega_final`
- `Value`: (ระบุชื่อ metric ด้วย)
- `Conflict`: (ระบุชื่อ metric ด้วย)
- `t_relax` + `t_relax_flag` (ถ้ามี)

**SHOULD fields**

- `Omega_terms_final`: pot/coup/grad
- `backtracking_stats`: rejects, dt_min, accept_ratio

ตัวอย่าง:

```json
{
  "status": "PASS",
  "phase_label": "BIAS_C",
  "metrics": {
    "Omega_final": -12.34,
    "Value": {"name": "V_deltaE", "value": 3.21},
    "Conflict": {"name": "Omega_grad_final", "value": 0.45},
    "t_relax": 0.12,
    "t_relax_flag": "OK"
  },
  "notes": "Potential dominates; conflict localized at interfaces."
}
```

---

## 6) energy decomposition (SHOULD แต่แนะนำมาก)

เพื่อให้ “Conflict = interface cost” ไม่ใช่คำลอย และทำ terrain ได้

### 6.1 Ω decomposition ที่เราต้องการให้ export

- `Omega_pot` : local potential energy (per-grid หรือรวม)
    
- `Omega_coup`: coupling energy (per-grid หรือรวม)
    
- `Omega_grad`: gradient/interface energy (per-grid หรือรวม)
    

### 6.2 omega_density terrain (สำหรับรูปภูเขา)

กำหนด `omega_density(x,y)` = density ที่รวมเทอม (หรือเฉพาะ grad สำหรับ conflict terrain)

**Public-friendly**

- terrain ที่โชว์ “conflict” ใช้ `omega_grad_density` เป็นหลัก (เห็นรอยต่อชัดสุด)
    

---

## 7) figs/ (SHOULD) — ผลผลิตมาตรฐานจาก snapshots

ให้ถือว่า figs เป็น “derived assets” ที่ generate ซ้ำได้จาก snapshots + timeseries

**MUST for Gallery inclusion**

- `state_C_end.png` (thumbnail)
    
- `evolution.gif`
    
- `terrain_omega_density.png` (หรือ surface_C)
    

**SHOULD**

- start/end ครบทั้ง C/I
    
- curve_omega / curve_bias
    
- curve_omega_terms (ถ้ามี decomposition)
    

---

## 8) Demo-ready gate (ใช้เป็น CI rule ได้)

**Run จะขึ้น Public Gallery ได้เมื่อ**

- มี `manifest.json`
    
- มี `timeseries.csv` ที่มี Ω และ bias
    
- มี `summary.json` ที่มี phase/value/conflict
    
- มี `snapshots/` อย่างน้อย 10 frames (รวม start/end)
    
- มี assets ที่ทำให้คนดูเข้าใจ (gif + thumbnail + terrain อย่างน้อย 1)
    

ถ้าขาดอย่างใดอย่างหนึ่ง → อยู่ในหมวด “compute-only” (ยังไม่ใช่ public demo)

---

## 9) Generation pipeline (แนวทางที่ไม่รก)

นี่คือ “ขั้นตอน” ไม่บังคับชื่อสคริปต์ แต่บังคับผลลัพธ์

1. **run** → สร้าง run_dir + manifest/timeseries/summary (+snapshots)
    
2. **render** → อ่าน snapshots/timeseries → สร้าง figs/ + README_demo.md (ถ้าต้องการ)
    
3. **register** → สแกน run_dir ทั้งหมด → สร้าง `registry.json` สำหรับ gallery
    
4. **gallery build** → ใช้ registry + figs ทำ index/archetypes pages
    

> จุดชี้ขาด: ทุกขั้น “อ่านจาก run_dir” และไม่เขียนข้าม run_dir แบบมั่ว ๆ

---

## Plain-Language Interpretation

Export Contract คือกติกาว่า “การทดลองหนึ่งเรื่อง” ต้องมี **หลักฐาน** ครบ:

- มีบัตรประชาชน (manifest)
    
- มีไทม์ไลน์ (timeseries)
    
- มีบทสรุป (summary)
    
- มีวิดีโอ/ภาพประกอบ (snapshots → figs)  
    แล้วถึงจะเอาไปเล่าให้คนทั้งโลกดูได้
    

---

## Next Step

**Part 4.11** ต่อจากนี้จะเป็น “Canonical Registry + Gallery Build Rules” แบบละเอียดขึ้น:

- registry fields ที่ต้องมีจริง
    
- วิธีเลือก thumbnail/representative seed
    
- กติกาเลือก archetype points จาก sweep (ไม่เลือกมั่ว)
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูเขียน Part 4.11 ให้เลย (จะเป็นคู่มือทำ gallery จาก runs แบบเป็นระบบเดียว).

----
# 000.04/8

## TL;DR

**Part 4.11 = คู่มือ “Registry + Gallery Build Rules”** ที่ทำให้เราสร้าง Public Gallery ได้แบบ _ไม่มั่ว_ และ _ไม่รก_:

- `registry.json` คือ “บัญชีรายการเดโม” ที่ชี้จาก **run_dir** ไปหา assets/metrics
- กติกาเลือก “ตัวแทน” จาก sweep/หลาย seed ต้อง **deterministic** (เลือกซ้ำแล้วได้เหมือนเดิม)
- กติกาเลือก archetype (SYM/BIAS_C/BIAS_I/HIGH_CONFLICT/MULTI_ATTRACTOR) ต้อง **อธิบายได้** และ _ลิงก์กลับไป Demo Card_

---
## Insight

ถ้าไม่มี registry + กติกาคัดเลือกที่ชัด:

- เดโมจะถูกหยิบ “ตามอารมณ์” → คนตามไม่ทัน → repo เละ
- พอเปิด public จะตอบคำถามไม่ได้ว่า “ทำไมอันนี้เป็นตัวแทน”  
    Part 4.11 ทำให้ทุกอย่าง “เป็นระบบเดียว” และพร้อมทำ open-source จริง

---
## Part 4.11 — Canonical Registry + Gallery Build Rules (v0.9 Draft)

## 0) หลักการใหญ่ (จำไว้ 3 ข้อ)

1. **ความจริงอยู่ที่ run_dir** (manifest/timeseries/summary/snapshots)
2. **registry เป็นแค่ index** (ห้ามบรรจุ logic/ข้อมูลซ้ำซ้อนจนกลายเป็นแหล่งจริงใหม่)
3. **การคัดเลือกต้อง deterministic** (ใช้ rule เดียวกันเสมอ → rerun/regen แล้วเหมือนเดิม)

---

## 1) Registry คืออะไร และทำไมต้องมี

### 1.1 ความหมาย

`registry.json` = รายการ “Demo Candidates / Demo Published” ที่บอกว่า:

- เดโมนี้มาจาก run ไหน (`run_id`, `run_dir`)
    
- phase/value/conflict คืออะไร
    
- รูป/กิฟ/terrain อยู่ไฟล์ไหน
    
- ถูกจัดเป็น archetype ไหน (ถ้าขึ้น public)
    

### 1.2 ทำไมต้องแยก “candidate” กับ “published”

- **candidate**: run ที่ครบ export contract ระดับหนึ่ง (อาจยังไม่คัดเป็นตัวแทน)
    
- **published**: ถูกคัดแล้ว + ผ่าน Demo-ready gate + มี caption และ assets ครบ
    

---

## 2) Registry Schema (ขั้นต่ำที่ควรล็อก)

> ให้ถือว่า registry เป็น “สคีมาที่สคริปต์/เว็บ/เอกสารอ้างได้” ต้องเสถียร

### 2.1 `registry.json` (array of entries)

```json
[
  {
    "demo_id": "DEMO_0001",
    "run_id": "RUN_..._seed10_case034",
    "run_dir": "runs/RUN_..._seed10_case034",
    "model_type": "C_I",
    "phase": "BIAS_C",
    "metrics": {
      "value": {"name": "V_deltaE", "value": 3.21},
      "conflict": {"name": "Omega_grad_final", "value": 0.45},
      "omega_final": -12.34,
      "robustness": 0.9
    },
    "params": {
      "beta": 1.0, "delta": 3.0, "s_tilt": 0.2, "k_ratio": 1.0, "asym": 0.0
    },
    "assets": {
      "thumb": "runs/.../figs/state_C_end.png",
      "gif": "runs/.../figs/evolution.gif",
      "terrain": "runs/.../figs/terrain_omega_density.png",
      "demo_page": "docs/gallery/demos/DEMO_0001/README_demo.md"
    },
    "tags": ["introvert", "extrovert", "terrain", "C_I"],
    "archetype": "BIAS_C",
    "status": "published"
  }
]
```

### 2.2 Fields ที่ “ต้องมีเสมอ”

- `demo_id`, `run_id`, `run_dir`
    
- `model_type`, `phase`
    
- `metrics.value`, `metrics.conflict` (ต้องระบุชื่อ metric)
    
- `assets.thumb`, `assets.gif` (สำหรับ gallery)
    
- `status`: `candidate|published|rejected` (เพื่อ track)
    

---

## 3) Demo-ready Gate (กติกาขึ้น candidate)

Run จะเข้า registry เป็น `candidate` ได้เมื่อ:

- มี `manifest.json`, `timeseries.csv`, `summary.json`
    
- มี `snapshots/` อย่างน้อย 10 frames (รวม start/end)
    
- มี `figs/state_*_end.png` + `figs/evolution.gif` อย่างน้อย
    
- `summary.json.status == PASS` (หรือ accepted=1)
    

> ถ้าไม่มี snapshots/gif → ไม่เข้า candidate (เพราะ public ไม่เข้าใจ)

---

## 4) กติกาเลือก “Representative Demo” เมื่อมีหลาย seed ต่อพารามิเตอร์เดียว

นี่คือจุดที่มึงย้ำเรื่อง “seed ไม่ใช่พระเอก แต่ต้องใช้เพื่ออ่านสนาม” → ถูกต้อง  
ดังนั้นต้องมีวิธีเลือก “seed ตัวแทน” แบบไม่มั่ว

### 4.1 นิยาม “กลุ่มเดียวกัน”

กลุ่ม = parameter set เดียวกัน (case_id เดียวกัน) แต่ seed ต่างกัน  
(เช่นใน cross-sweep 1 จุดมี seed 10 ตัว)

### 4.2 Rule เลือก seed ตัวแทน (deterministic)

**Step A: เลือก phase หลักของกลุ่ม**

- phase_major = phase ที่พบมากที่สุดในกลุ่ม (mode)
    
- robustness = (count(phase_major) / n_seeds)
    

**Step B: เลือก seed ภายใน phase_major**  
เลือก seed ที่:

1. `conflict` ใกล้ “median conflict” ของ phase_major มากที่สุด
    
2. ถ้า tie → เลือก `value` ใกล้ median value มากที่สุด
    
3. ถ้า tie → เลือก seed เลขน้อยสุด (เพื่อ deterministic)
    

**เหตุผล:** median representative เล่า “เคสทั่วไป” ไม่ใช่ outlier

### 4.3 กรณี “multi-attractor”

ถ้า robustness < threshold (เช่น 0.6) → กลุ่มนี้จัดเป็น `MULTI_ATTRACTOR`  
แล้วเลือกตัวแทน 2–3 seed แทน (เพื่อโชว์ความแตกต่าง):

- เลือกตัวแทนของ phase ที่มีอันดับ 1 และ 2
    
- หรือเลือก seed ที่ให้ผลต่างสุดบน Value–Conflict (max distance)
    

> นี่คือเดโมที่ public จะเข้าใจว่า “โลกมีหลายหลุมแข่งกัน”

---

## 5) กติกาเลือก Archetype Demos จาก Sweep (ไม่หยิบมั่ว)

เป้าหมายคือ: จากผล sweep ใหญ่ เลือกเดโมน้อย ๆ ที่ “ครอบคลุมความหมาย”

### 5.1 นิยามชุดหมวด (เหมือน Part 4.9)

- `SYM`
    
- `BIAS_C`
    
- `BIAS_I`
    
- `HIGH_CONFLICT`
    
- `MULTI_ATTRACTOR`
    

### 5.2 Algorithm เลือกตัวแทนแต่ละหมวด (deterministic)

ให้ทำบน “representative per parameter point” ก่อน (ตามข้อ 4)

#### (A) SYM representative

- filter phase == SYM และ robustness ≥ 0.8
    
- เลือกจุดที่ conflict ต่ำสุด (หรือใกล้ 20th percentile conflict) และ value สูงพอ
    
- tie-breaker: value สูงกว่า → seed ต่ำกว่า
    

#### (B) BIAS_C representative

- filter phase == BIAS_C และ robustness ≥ 0.8
    
- เลือก “sweet spot” = maximize (value − λ·conflict) โดย λ เป็นค่าคงที่ใน docs (เช่น 1.0)
    
- tie-breaker ตาม deterministic order
    

#### (C) BIAS_I representative

- ทำเหมือน BIAS_C (mirror)
    

#### (D) HIGH_CONFLICT representative

- filter robustness ≥ 0.8 (หรือ ≥0.6 ก็ได้ตามนิยาม)
    
- เลือก conflict สูงสุด (top 5%) แล้วในกลุ่มนั้นเลือก value กลาง ๆ (ไม่เอา value ต่ำสุดสุดโต่ง)
    
- จุดประสงค์: ให้เห็น “รอยต่อ/ตึง” แบบชัดจาก terrain
    

#### (E) MULTI_ATTRACTOR representative

- filter robustness < 0.6
    
- เลือกจุดที่ “phase diversity” สูงสุด (เช่นมี 3 label) หรือความแปรปรวน Value–Conflict สูงสุด
    
- แล้วเลือก 2 seed ตัวแทนให้เห็นผลต่าง (ข้อ 4.3)
    

---

## 6) Registry Build Steps (pipeline แบบไม่รก)

> ให้ทำเป็นขั้นเป็นตอน เพื่อ regen ได้เสมอ

### Step 1: Scan runs

- อ่านทุก `runs/*/manifest.json`
    
- เช็ค Demo-ready gate (ข้อ 3)
    
- อ่าน `summary.json` และ `timeseries.csv` เพื่อดึง metrics
    
- สร้าง entry เป็น `candidate`
    

### Step 2: Group by parameter set

- group key = (matrix_case_id หรือ hash ของ params ที่สำคัญ)
    
- คำนวณ robustness/phase_major
    
- เลือก representative seed (ข้อ 4)
    

### Step 3: Assign archetype

- ใช้ rule ในข้อ 5
    
- mark `published` เฉพาะ entry ที่ถูกเลือกเป็นตัวแทน (ที่เหลือยังคง `candidate`)
    

### Step 4: Build gallery pages

- สร้าง `docs/gallery/index.md` (tiles + Value–Conflict map)
    
- สร้างหน้า archetype ทั้ง 5
    
- สร้าง link ไป `README_demo.md` ของเดโมแต่ละใบ (หรือ copy/alias)
    

> หลัก: Gallery “อ่าน registry” ไม่ใช่ไปไล่จับไฟล์มั่ว ๆ

---

## 7) กติกา Thumbnail / Preview (ให้ gallery สื่อสารได้จริง)

เพราะคนทั่วไปอ่านจากรูปก่อน

### 7.1 Thumbnail standard

- ใช้ `state_C_end.png` เป็น default
    
- ถ้าเป็น `C_I` และ I สำคัญมาก → ให้ใช้ composite thumbnail (C_end + I_end) แต่ต้องกำหนดชื่อเดียว (เช่น `thumb.png`)
    

### 7.2 Terrain preview

- ให้ terrain ที่โชว์ conflict ชัดสุดเป็น default:
    
    - `terrain_omega_density.png` หรือ `terrain_omega_grad_density.png` (ถ้ามี)
        
- ถ้าไม่มี terrain → ไม่ขึ้น published (อยู่ candidate อย่างเดียว)
    

---

## 8) Traceability Rules (กันหลงเมื่อ public)

ทุก `published demo` ต้อง trace กลับได้ว่า:

- params/seed/grid/time มาจาก manifest
    
- metrics มาจาก summary/timeseries
    
- assets สร้างจาก snapshots
    
- และ `demo_id → run_id` เป็น one-to-one ใน registry
    

> นี่คือสิ่งที่ทำให้ repo “เป็นวิชาการ” ไม่ใช่ “งานกราฟสวยแต่เช็คไม่ได้”

---

## Plain-Language Interpretation

- “Run” คือคลิปดิบ/ข้อมูลจริง
    
- “Registry” คือสารบัญว่าคลิปไหนอยู่ตรงไหนและมีความหมายอะไร
    
- “Gallery rules” คือกติกาว่าเราเลือกคลิปไหนมาโชว์เป็นตัวแทน และเลือกแบบยุติธรรม (เลือกซ้ำแล้วได้เหมือนเดิม)
    

---

## Next Step

**Part 5 (Open-system/feedback spec)** เป็นก้าวถัดไปของเนื้อหาเชิงทฤษฎีที่มึงตั้งโจทย์ไว้:  
ขยับจาก “สนามคงที่” → “สนามที่ถูกปรับโดยสิ่งแวดล้อม/ทรัพยากร/หลายกระบวนการ” ให้เข้ากับ extrovert เต็มรูปแบบ

พิมพ์ “ต่อ” อีกที เดี๋ยวกูเริ่ม **Part 5.1: Open System Minimal Extension** (แบบไม่สร้างสมการใหม่ลอย ๆ แต่เป็น “ชั้นต่อ” จาก Ω/dynamics ที่เรามีอยู่แล้ว และบอกชัดว่าใน harness ต้องเพิ่ม output/input อะไร).

----
# 000.05/1

## TL;DR

เริ่ม **Part 5.1: Open System Minimal Extension** — วิธีทำให้ UET จาก “สนามคงที่ (closed)” ไปเป็น “ระบบเปิด (open)” แบบ **ไม่มั่วสมการใหม่** และยัง **ต่อยอดจาก Ω/dynamics ที่พิสูจน์แล้ว** ได้ทันที

แกนเดียวที่เราจะเพิ่มคือ:

> ให้พารามิเตอร์ของสนาม ( \theta ) “เปลี่ยนตามเวลา/ผลกระทบ” ได้  
> โดยยังใช้ solver เดิมทั้งหมด (C/I + monotone gate) เป็นแกน

---

## Insight

สิ่งที่มึงต้องการใน extrovert/open system ไม่ใช่ “3D graph” ก่อน แต่คือ **ชั้นควบคุม (driver/feedback)** ที่นิยามว่า

- โลก (สนาม) เปลี่ยนได้ยังไง
    
- เปลี่ยนเพราะอะไร (impact/value/conflict)
    
- แล้วเราวัด “พลังงานที่โลกใส่เข้ามา/ดึงออกไป” ยังไง
    

นี่แหละคือสะพานไป **Thermodynamics / Information / Game / Einstein** ใน v0.9 แบบไม่หลุด

---

## Part 5.1 — Open System Minimal Extension (จาก Closed → Open แบบเป็นชั้นต่อ)

## 1) นิยามให้ชัดก่อน: Closed vs Open ในภาษา UET

### Closed system (ที่ harness ทำอยู่ตอนนี้)

- พารามิเตอร์โลก ( \theta ) **คงที่**:  
    (\theta = {\beta, k_C, k_I, \text{potC}, \text{potI}, M, ...})
    
- ระบบไหลด้วย dynamics เดิม:  
    [  
    \dot X = -\mathcal{M},\frac{\delta \Omega(X;\theta)}{\delta X}  
    ]
    
- และมี **accept/reject** เพื่อบังคับ ( \Omega ) ไม่เพิ่ม (ในเชิงปฏิบัติเป็น Lyapunov gate)
    

### Open system (ขั้นต่ำที่เราต้องเพิ่ม)

- ให้ ( \theta ) **เปลี่ยนตามเวลา/ตามผล**:  
    [  
    \theta = \theta(t)\quad \text{หรือ}\quad \theta=\theta(t,,\text{Impact}(X))  
    ]
    
- ระบบยังไหลแบบเดิม “ภายใต้สนามใหม่ที่เปลี่ยนได้”
    

> สรุป: **เราไม่เปลี่ยนแกน solver** เราแค่เพิ่ม “driver” ที่ขยับสนามได้

---

## 2) Open System แบบ “Minimal” มี 3 โหมด (เรียงจากง่ายสุด)

### โหมด A — Scheduled Open System (เปิดแบบตารางเวลา)

ให้ ( \theta(t) ) เปลี่ยนตามสคริปต์/ตารางที่เรากำหนดไว้ เช่น

- ช่วงแรก tilt = 0
    
- ช่วงหลัง tilt = +0.2
    
- หรือ beta เปลี่ยนเป็นเฟส ๆ
    

**ใช้ทำอะไร:** เดโม “โลกเปลี่ยนกติกา” แล้วดูระบบปรับตัว  
**ข้อดี:** ง่ายสุด ไม่ต้องนิยาม impact ก่อนก็ทำได้

---

### โหมด B — Feedback Open System (เปิดแบบ feedback จาก impact)

ให้โลกเปลี่ยนตามผลลัพธ์ที่ระบบสร้าง เช่น

- ถ้า conflict สูง → เพิ่ม k (ทำให้เรียบขึ้น) หรือปรับ tilt ให้ลดรอยต่อ
    
- ถ้าระบบ bias มากเกิน → ปรับ s_tilt กลับมาถ่วงดุล
    

รูปแบบทั่วไป:  
[  
\theta_{m+1} = \theta_m + \eta,G(\text{Impact}_m)  
]  
โดย Impact มาจาก metrics ที่เราล็อกไว้แล้ว (Value/Conflict/Phase/Robustness)

**ใช้ทำอะไร:** “ระบบเปิดจริง” ที่มีวงจรควบคุม  
**ข้อดี:** นี่แหละที่เอาไปเล่าเป็น “โลก+NPC+ผลกระทบ+การเรียนรู้” ได้ถูกต้อง

---

### โหมด C — Spatial Forcing Open System (เปิดแบบทรัพยากร/แหล่งกำเนิด)

ให้ “สภาพแวดล้อมเป็นฟิลด์” เช่นมี resource map (R(x)) แล้วทำให้ tilt เป็นฟังก์ชันของตำแหน่ง:  
[  
s(x) = s_0 + \lambda R(x)  
]  
หรือ external potential (U_{\text{ext}}(x)) เข้า Ω

**ใช้ทำอะไร:** เดโมแบบ Physarum/ระบบนิเวศ/เมือง/ทรัพยากร  
**ข้อดี:** คนเข้าใจง่ายมาก (มันเหมือนโลกจริง)

> หมายเหตุ: โหมด C อาจต้องเพิ่ม input ใหม่ใน harness (รับ spatial map) แต่ยัง “ไม่ต้องเปลี่ยนแกนสมการ” แค่เพิ่ม term/field ที่ feed เข้า tilt/potential

---

## 3) “บัญชีพลังงาน” ของระบบเปิด (สำคัญมาก + เป็นสะพานไป Thermodynamics)

พอโลกเปลี่ยนได้ เราต้องแยกให้ได้ว่า “พลังงานเปลี่ยนเพราะอะไร” ไม่งั้นมั่ว

ให้ดู discrete-time แบบแบ่งเป็น epoch:

- เราอัปเดต state ด้วย solver ภายใต้ ( \theta_m ) จนได้ (X_{m+1})
    
- แล้วโลกเปลี่ยนพารามิเตอร์เป็น ( \theta_{m+1})
    

แตกการเปลี่ยนของ Ω ได้แบบเป็นบัญชี:

 [  
\Omega(X_{m+1};\theta_{m+1})-\Omega(X_m;\theta_m)

\underbrace{\big[\Omega(X_{m+1};\theta_m)-\Omega(X_m;\theta_m)\big]}_{\text{Dissipation } \Delta\Omega_{\text{diss}}\le 0}  
+  
\underbrace{\big[\Omega(X_{m+1};\theta_{m+1})-\Omega(X_{m+1};\theta_m)\big]}_{\text{Work/Drive } \Delta\Omega_{\text{env}}}  
]

- เทอมแรก = การไหล/การผ่อนคลายของระบบ (ควร ≤ 0 ถ้า gate ทำงาน)
    
- เทอมสอง = “งานจากสิ่งแวดล้อม” (อาจ + หรือ −)
    

นี่คือ “ภาษากลาง” ที่จะไป thermodynamics ได้โดยไม่ต้องโม้:

- **dissipation** = การสูญเสีย/การคลายความตึงภายใน
    
- **work injection** = โลกใส่พลังงาน/ดึงพลังงานออกด้วยการเปลี่ยนสนาม
    

> จุดนี้คือโคตรสำคัญ เพราะมันแก้ปัญหาที่มึงด่า: นักวิทย์ชอบควบตัวแปรแบบไม่ผูกกัน  
> ที่นี่เราบังคับให้ “การเปลี่ยนกติกา” ถูกนับเป็นงานของโลกอย่างเป็นระบบ

---

## 4) นิยาม Impact สำหรับ feedback (ให้ “ระบบเปิด” ไม่เลื่อนลอย)

เราจะยึดของที่เราล็อกไว้แล้วจาก Part 2:

- **Value**: (V_{\Delta E}) หรือ (-\Omega_{\text{final}})
    
- **Conflict (หลัก)**: (\Omega_{\text{grad,final}})
    
- **Phase**: BIAS_C / BIAS_I / SYM
    
- **Robustness**: สัดส่วน seed ที่ได้ phase_major
    

ให้รวมเป็น impact vector:  
[  
\text{Impact} = (V,\ C,\ \text{phase},\ R)  
]

แล้วกำหนด policy ที่ “ชัด+ไม่มั่ว” เช่น:

### Policy ตัวอย่าง (โหมด B)

- ถ้า conflict สูงเกินเป้า (C>C^*) → เพิ่ม (k) (ทำให้รอยต่อลด)  
    [  
    k_{m+1}=k_m + \eta_k (C-C^*)  
    ]
    
- ถ้า bias เยอะเกิน (เช่น phase=BIA S_C ต่อเนื่อง) → ลด tilt หรือปรับ beta  
    [  
    s_{m+1}=s_m - \eta_s \cdot \text{sign}(\text{bias})  
    ]
    

> นี่คือ “feedback” ที่ทำให้ extrovert เป็นระบบจริง ไม่ใช่คำสวยๆ

---

## 5) เสถียรภาพของระบบเปิด (Two-timescale rule)

เพื่อไม่ให้ระบบเปิด “พังเพราะขยับโลกเร็วเกิน” ให้ใช้กติกาง่าย ๆ:

- ให้ state relax เร็วกว่าการเปลี่ยนสนาม  
    [  
    \tau_{\text{state}} \ll \tau_{\text{env}}  
    ]  
    ในภาษา implementation:
    
- รัน solver ภายใต้ (\theta_m) ให้ “เกือบนิ่ง” ก่อนค่อยอัปเดต (\theta)
    
- หรืออัปเดต (\theta) ทีละน้อย (small η)
    

**ผลดี:** ได้ quasi-equilibrium sequence  
**ผลเสีย:** ถ้าต้องการโลกผันผวนเร็ว ก็ทำได้ แต่ต้องยอมรับว่า Ω อาจไม่ monotone และต้องใช้บัญชีพลังงานด้านบนแทน “gate เดียว”

---

## 6) Implementation Plan ที่ “ต่อจาก harness เดิม” แบบไม่รก

ไม่ต้องรื้ออะไรใหญ่ แค่เพิ่ม “driver loop” ชั้นนอก

### 6.1 โครงรันแบบ epoch

- epoch m:
    
    1. fix (\theta_m)
        
    2. run solver T_inner steps (หรือจน relax)
        
    3. compute Impact_m
        
    4. update (\theta_{m+1}) ตาม schedule/policy
        
    5. log ledger: dissipation/work
        

### 6.2 Output contract สำหรับระบบเปิด (เพิ่มจาก Part 4.10)

ใน `summary.json` ของ open-run เพิ่ม:

- `omega_diss_total` (รวมเทอม dissipation)
    
- `omega_env_total` (รวม work injection)
    
- `policy_trace` (ค่าพารามิเตอร์ต่อ epoch: beta(t), s(t), k(t))
    

และใน `timeseries.csv` เพิ่ม (ถ้าทำได้):

- `Omega_state` (เปลี่ยนจากการไหล)
    
- `Omega_env` (เปลี่ยนจากการขยับสนาม)
    

> นี่จะเป็นรากฐานของ thermodynamics chapter แบบ “มีของจริง” ไม่ใช่ปรัชญา

---

## Plain-Language Interpretation (เวอร์ชันคนทั่วไป)

- ระบบปิด: โลกไม่เปลี่ยน กติกาคงที่ ลูกบอลไหลลงหลุมจนหยุด
    
- ระบบเปิด: โลกเปลี่ยนได้ เช่นมีทรัพยากรเพิ่ม/ลด มีแรงกดดันใหม่ ระบบต้องปรับตัวใหม่
    
- เราต้องแยกให้ได้ว่า “มันเปลี่ยนเพราะมันคลายเอง” กับ “โลกมาบังคับให้เปลี่ยน”
    

---

## Next Step

Part 5 ต่อไปจะเป็น 2 ตอนที่สำคัญมาก:

### **Part 5.2 — Open System: Resource/Forcing Field Spec**

ทำโหมด C ให้เป็นสเปกชัด ๆ (รับ (R(x)), map เข้า tilt/potential, export terrain)

### **Part 5.3 — Multi-process / Multi-entity Extension**

ทำให้ “มีหลายกระบวนการอยู่ในสนามเดียว” อย่างเป็นระบบ (โดยยังใช้แกน Ω เดิม)

มึงพิมพ์ “ต่อ” อีกที กูจะเริ่ม **Part 5.2** ทันที และจะเขียนให้มัน “เป็นสเปกที่เอาไปทำใน repo ได้” ไม่ใช่คุยลอย ๆ

----

# 000.05/2

## TL;DR

**Part 5.2 = สเปก “Resource/Forcing Field”** ที่ทำให้ UET กลายเป็น “ระบบเปิดที่มีสิ่งแวดล้อมจริง” แบบ _ทำได้ใน repo_ โดย **ไม่เปลี่ยนแกน Ω/dynamics**:

- เพิ่มอินพุต **แผนที่สิ่งแวดล้อม** (R(x,t)) (ทรัพยากร/แรงกดดัน/ข้อจำกัดเชิงพื้นที่)
    
- map มันเข้า **พารามิเตอร์เชิงพื้นที่** ของศักย์ (โดยเฉพาะ tilt) เช่น (s_C(x,t), s_I(x,t))
    
- solver เดิมยังเหมือนเดิม แค่คำนวณ (V'(u)) โดยใช้ (s(x,t)) แทนค่าคงที่
    
- export เพิ่ม: `resource_map`, `s_field`, และ “บัญชีงานจากสิ่งแวดล้อม” (ΔΩ_env)
    

---

## Insight

ถ้าอยากให้ UET “เหมือนคลิป YouTube/เหมือนโลกจริง” สิ่งที่ขาดไม่ใช่ 3D solver แต่คือ **โลกต้องมีภูมิประเทศที่ไม่สม่ำเสมอ** (มีอาหาร มีแหล่งกดดัน มีพื้นที่ต้องห้าม ฯลฯ)

ดังนั้น Part 5.2 จะล็อกว่า “สิ่งแวดล้อม” เข้ามาใน UET ผ่านช่องไหนบ้าง โดยเริ่มจากช่องที่ **ปลอดภัยที่สุดและสอดคล้องสมการเดิมที่สุด**:

> **tilt field** (s(x,t)) ใน quartic potential

---

## Part 5.2 — Open System: Resource/Forcing Field Spec (v0.9 Draft)

## 1) เป้าหมาย

ทำให้ UET รองรับ “ระบบเปิดเชิงพื้นที่” ที่:

- มี **resource / forcing map** บนกริดเดียวกับ state (2D ในปัจจุบัน)
    
- ทำเดโมแบบ Physarum/ระบบนิเวศ/เมือง ได้: “มีจุดอาหาร/จุดอันตราย/เส้นทาง”
    
- ยังคงใช้ **Ω + monotone gate** เป็นแกน (เสถียรและพิสูจน์ต่อได้)
    

---

## 2) นิยามตัวแปรใหม่ (เพิ่มแค่สิ่งจำเป็น)

### 2.1 Resource / Forcing field

ให้มีฟิลด์สิ่งแวดล้อม:  
[  
R(x,t)\quad \text{บนโดเมนเดียวกับ } C(x,t), I(x,t)  
]

- (R) อาจเป็น “อาหาร”, “แรงกดดัน”, “ข้อจำกัดพื้นที่”, “ภูมิประเทศ”, “ความเหมาะสมของถิ่นอาศัย”
    
- รูปแบบข้อมูล: array ขนาด (N,N) ต่อเวลา หรือคงที่
    

### 2.2 Parameter fields (พารามิเตอร์ที่กลายเป็นเชิงพื้นที่)

เริ่มจาก “ช่องที่เล็กที่สุด”:

- (s_C(x,t)), (s_I(x,t)) แทนค่าคงที่ (s_C, s_I)
    

> หมายเหตุ: ยัง **ไม่ต้อง** ทำให้ (\beta), (k) เป็น field ก่อน (ทำได้ใน Part 5.3/5.4 ถ้าจำเป็น)

---

## 3) การ map “สิ่งแวดล้อม → สนาม Ω” (Core mapping)

### 3.1 Mapping หลัก (แนะนำ): tilt field

ให้กำหนด:  
[  
s_C(x,t) = s_{C0} + \lambda_C,\hat R(x,t)  
]  
[  
s_I(x,t) = s_{I0} + \lambda_I,\hat R(x,t)  
]  
โดย (\hat R) คือ resource ที่ normalize แล้ว (เช่นให้อยู่ในช่วง [-1,1] หรือ [0,1])

**เหตุผลที่เลือก tilt field เป็นช่องหลัก**

- quartic potential ใน UET มีรูป (V(u)=\frac12 a u^2+\frac14 \delta u^4 - s u)
    
- การทำให้ (s) เป็นฟิลด์ คือการ “เอนสนามแบบพื้นที่ต่อพื้นที่”
    
- อธิบายง่ายมาก: “บริเวณที่มีทรัพยากรสูง จะดึงให้ C (หรือ I) ไปทางนั้น”
    

### 3.2 Mapping แบบข้อห้าม/อุปสรรค (optional): barrier via tilt หรือ additive mask

กรณี “พื้นที่ต้องห้าม/อันตราย” ให้ใช้ (R) เป็น penalty:

- ทำ (s) ผลักให้ state ลด/หนีพื้นที่นั้น (เลือกสัญญาณให้ถูก)  
    หรือในระดับถัดไป (ถ้าอยากคมกว่านี้ในอนาคต):
    
- เพิ่ม external penalty term ใน Ω แบบ “คูณ mask” (แต่ยังอยู่ในกรอบเดิมได้)
    

> ใน Part 5.2 เรายึด tilt field เป็นหลักเพื่อไม่แตกประเด็น

---

## 4) สมการ (Formal) หลังเพิ่ม forcing field

### 4.1 Potential term

เดิม:  
[  
V_C(C) = \tfrac12 a_C C^2 + \tfrac14 \delta_C C^4 - s_C C  
]  
ใหม่:  
[  
V_C(C;x,t) = \tfrac12 a_C C^2 + \tfrac14 \delta_C C^4 - s_C(x,t), C  
]  
ดังนั้นอนุพันธ์:  
[  
\frac{\partial V_C}{\partial C} = a_C C + \delta_C C^3 - s_C(x,t)  
]  
(เช่นเดียวกันสำหรับ I)

### 4.2 Ω functional (ยังโครงเดิม)

[  
\Omega(C,I;t)=\int \Big(V_C(C;x,t)+V_I(I;x,t)-\beta C I\Big),dx  
+\tfrac12 k_C \int |\nabla C|^2 dx + \tfrac12 k_I \int |\nabla I|^2 dx  
]

### 4.3 Dynamics (solver แกนเดิม)

ยังกึ่ง-implicit เหมือนเดิม แค่ RHS เปลี่ยนเพราะ (s(x,t)) เป็นฟิลด์:  
[  
rhs_C = C - dt,MC,\big(a_C C + \delta_C C^3 - s_C(x,t) - \beta I\big)  
]  
แล้วแก้ diffusion แบบเดิมใน spectral space

---

## 5) โหมดการเปิด (สอดคล้อง Part 5.1) — สำหรับ forcing field

### Mode C1: Static spatial forcing (เริ่มจากง่ายสุด)

- (R(x)) คงที่
    
- เหมาะกับเดโม “มีอาหารอยู่ตรงนี้” แบบ Physarum/ระบบนิเวศ
    

### Mode C2: Scheduled forcing (เวลาเปลี่ยนตามสคริปต์)

- (R(x,t)) เปลี่ยนตามตาราง (เช่นย้ายแหล่งอาหาร/เกิดภัยแล้ง)
    

### Mode C3: Feedback forcing (สิ่งแวดล้อมเปลี่ยนตาม impact)

- (R_{m+1}(x)=\mathcal{H}(R_m(x), \text{Impact}_m))
    
- อันนี้จะไปเชื่อม “นิเวศ–การใช้ทรัพยากร–การฟื้นตัว” ได้ตรงมาก
    

> ใน Part 5.2 เราล็อกสเปกข้อมูลให้รองรับทั้ง 3 แบบ แต่เริ่ม implement ที่ C1 ก่อน

---

## 6) Data Contract (อินพุต/ไฟล์) — ทำให้คนใช้งานได้จริง

### 6.1 รูปแบบไฟล์ resource map

แนะนำให้รองรับอย่างน้อย 2 แบบ:

- `resource.npy` หรือ `resource.npz` (N×N)
    
- หรือ `resource.png` (grayscale) แล้วแปลงเป็น float (0..1)
    

**สัญญา**

- `resource` ต้องอยู่ในกริดเดียวกับ simulation (N×N)
    
- ถ้าไม่ตรงให้มีขั้น resample (แต่ในสเปกนี้ให้ถือว่าต้องตรงก่อน)
    

### 6.2 config เพิ่มใน case

เพิ่ม field ใน params/manifest:

- `resource_path`
    
- `resource_norm` (วิธี normalize)
    
- `lambda_C`, `lambda_I`
    
- `sC0`, `sI0`
    

---

## 7) Output Contract เพิ่มเติม (ต่อยอดจาก Part 4.10)

เพื่อให้ demo/gallery “อธิบายโลก” ได้ ต้อง export เพิ่ม:

### 7.1 Store environment fields

- `env/resource.npy` (หรือ copy path)
    
- `env/sC_field.npy`, `env/sI_field.npy` (ถ้าใช้)
    
- `figs/resource_map.png`
    
- `figs/s_field_map.png` (optional)
    

### 7.2 Ledger (บัญชีงานจากสิ่งแวดล้อม)

เพราะตอนนี้ Ω เปลี่ยนได้จาก 2 สาเหตุ:

1. ระบบไหลเอง (dissipation)
    
2. โลกเปลี่ยนสนาม (work/drive)
    

เก็บใน `summary.json`:

- `omega_diss_total`
    
- `omega_env_total`  
    และใน `timeseries.csv` (ถ้าทำได้):
    
- `Omega_env_step` (ความเปลี่ยนจาก forcing)
    
- `Omega_diss_step` (ความเปลี่ยนจาก relaxation)
    

> นี่คือสะพานไป thermodynamics แบบ “มีเลขจริง”

---

## 8) Demo Blueprint เฉพาะ forcing field (ให้คนเข้าใจทันที)

**Demo Card (Part 4.8) สำหรับระบบเปิดเชิงพื้นที่** ต้องเพิ่ม “ภาพโลก” อีก 1 แผ่น:

- `figs/resource_map.png` (โลกให้รางวัล/ลงโทษตรงไหน)
    
- และ overlay: `resource_map + path/pattern` (optional)
    

**caption ที่คนทั่วไปเข้าใจ**

- “บริเวณสว่างคืออาหาร”
    
- “ระบบสร้างโครงสร้าง/ย้ายตัวเองไปหาอาหาร”
    
- “รอยต่อสว่างใน terrain คือ conflict ที่ต้องจ่าย”
    

---

## 9) ขอบเขตความจริง (กันหลงประเด็น)

- ตอนนี้ solver ยังเป็น 2D spatial: เพียงพอสำหรับ **ภาพแบบ 3D terrain** และ **เดโมแบบ YouTube**
    
- forcing field ทำให้ “โลก” มีโครงสร้างจริงขึ้นทันที
    
- 3D spatial solver เป็นงานถัดไป ไม่ใช่ prerequisite ของการสื่อสาร
    

---

## Math/Physics Interpretation

- Open forcing ทำให้ Ω เป็นฟังก์ชันของเวลา: (\Omega(\cdot;t))
    
- เราต้องแยกการเปลี่ยนพลังงานเป็น:
    
    - dissipation (จาก dynamics ภายใต้ θ คงที่)
        
    - work injection (จากการเปลี่ยน θ หรือ forcing field)
        
- นี่คือโครงสร้างมาตรฐานของระบบเปิดที่ต่อยอดไป thermo/info ได้โดยไม่หลุด
    

---

## Plain-Language Interpretation

ก่อนหน้านี้ UET คือโลกที่ “พื้นเรียบเหมือนกันหมด”  
พอเพิ่ม resource map โลกจะมี “อาหาร/อุปสรรค/แรงดึง” จริง ๆ  
ระบบจึงดูเหมือนสิ่งมีชีวิต/การเรียนรู้: มัน “ปรับตัวให้ไปอยู่ตรงที่อยู่ได้” และเราถ่ายออกมาเป็นภาพได้เลย

---

## Next Step

ถัดไปเราจะไป **Part 5.3: Multi-process / Multi-entity Extension** ซึ่งคือสิ่งที่มึงย้ำว่า “ระบบรวมมีหลายกระบวนการ”:

- ทำให้มีหลาย subsystem หรือหลาย “entity fields” อยู่ร่วมกัน
    
- และนิยาม coupling/impact ระหว่างกัน โดยยังยึด Ω + driver loop เดิม
    

พิมพ์ “ต่อ” อีกที กูเริ่ม Part 5.3 ทันที และจะเขียนเป็นสเปกที่ “ทำใน repo ได้” เช่นเดียวกับ Part 5.2 (ไม่คุยลอย).


---
# 000.05/3

## TL;DR

**Part 5.3 = Multi-process / Multi-entity Extension**: ทำให้ “ระบบรวมมีหลายกระบวนการ” ได้จริง โดย **ไม่ทิ้งแกนเดิม** (Ω + dynamics + monotone gate) และยัง implement ใน repo ได้เป็นขั้น ๆ

- **Multi-process (หลายแรง/หลายแนวโน้ม)** = จาก C/I → ขยายเป็น (X_1,\dots,X_n) (หลายฟิลด์)
    
- **Multi-entity (หลายสิ่งในโลกเดียว)** = “หลายแพตเทิร์น/หลายโดเมน” ที่เกิดจากฟิลด์เดียวกัน (โดยต้องมี snapshot เพื่อ extract entity)
    
- ทำสองอย่างนี้ด้วยสเปกเดียว: **Ω แบบ multi-field + interaction graph + environment field (จาก Part 5.2)**
    

---

## Insight

สิ่งที่มึงเรียกว่า “ระบบรวมมีหลายกระบวนการ” ใน UET **ไม่จำเป็นต้องเพิ่มแนวคิดใหม่** เลย  
มันคือการทำให้ “จำนวนแกนแนวโน้ม” เพิ่มขึ้น จาก 2 (C/I) เป็น n (X₁..Xₙ) และนิยามว่าใคร interact กับใครบ้าง (graph)

แล้ว “หลายสิ่ง” (multi-entity) จะโผล่เองในเชิงภาพเป็นหลายโดเมน/หลายก้อน—สิ่งที่ขาดอยู่มีแค่อย่างเดียว: **snapshots เพื่อมองเห็นและแยก entity**

---

## Part 5.3 — Multi-process / Multi-entity Extension Spec (v0.9 Draft)

## 1) นิยาม “Process” vs “Entity” ในภาษา UET (กันสับสน)

### 1.1 Process = แกนแนวโน้ม/แรงขับ (internal degrees)

- C กับ I ในโมเดลปัจจุบันคือ “2 processes”
    
- ขยายเป็น n processes = n ฟิลด์:  
    [  
    X(x,t) = (X_1(x,t),\dots,X_n(x,t))  
    ]  
    แต่ละ (X_i) มี:
    
- potential ของตัวเอง (Pᵢ)
    
- gradient penalty ของตัวเอง (Rᵢ)
    
- mobility ของตัวเอง (Jᵢ)
    
- และ interaction กับคนอื่น (coupling)
    

### 1.2 Entity = “สิ่งหนึ่ง” ที่เป็นแพตเทิร์น/ก้อน/โดเมน (emergent)

- ใน UET “entity” ไม่จำเป็นต้องเป็นตัวแปรเพิ่ม
    
- entity เกิดจาก **การจัดรูปของฟิลด์** (เช่น domain, cluster, filament)
    
- เราจะ “เห็น entity” ได้เมื่อมี snapshots แล้วทำ segmentation / component tracking
    

> สรุป: **Multi-process = เพิ่มมิติของ state**  
> **Multi-entity = เพิ่มความสามารถในการ “มองเห็น/นับ/ติดตาม” สิ่งที่เกิดจาก state**

---

## 2) Multi-process: Ω แบบ multi-field (ยังอยู่ในกรอบเดิม)

เริ่มจาก generalization ที่ตรงกับของเดิมสุด:

### 2.1 Ω functional (แบบ canonical)

[  
\Omega(X;t)=\int \Big(\sum_{i=1}^n V_i(X_i;x,t)\Big),dx  
;+;\int \Big(\sum_{i<j} W_{ij}(X_i,X_j)\Big),dx  
;+;\frac12\sum_{i=1}^n k_i\int |\nabla X_i|^2 dx  
]

- (V_i) = quartic + tilt field (รับจาก Part 5.2 ได้):  
    [  
    V_i(u;x,t)=\tfrac12 a_i u^2 + \tfrac14 \delta_i u^4 - s_i(x,t),u  
    ]
    
- interaction term (W_{ij}) ให้เริ่มจาก linear coupling แบบเดิมที่สุด:  
    [  
    W_{ij}(X_i,X_j)= -\beta_{ij},X_i X_j  
    ]  
    (นี่คือ C–I coupling แบบเดิมที่ถูกยกไปเป็นกรณี (n=2))
    

### 2.2 กติกา “ไม่มั่ว” ของ interaction graph

- ให้ (\beta_{ij}) เป็น **matrix สมมาตร** (เริ่มต้น) เพื่อความนิ่งของความหมาย
    
- ถ้าจะให้ไม่สมมาตร ให้ถือว่าเป็น “directed influence” (ค่อยทำหลัง v0.9)
    

> นี่คือ “หลายกระบวนการในสนามเดียว” แบบ minimal ที่ยังยึดโครงเดิม 100%

---

## 3) Dynamics: ใช้ solver เดิม (แค่ทำทีละฟิลด์)

ให้ dynamics ของแต่ละฟิลด์เป็น:  
[  
\dot X_i = -M_i;\frac{\delta \Omega}{\delta X_i}  
]

เมื่อคำนวณอนุพันธ์ จะได้:  
[  
\frac{\delta \Omega}{\delta X_i}  
= a_i X_i + \delta_i X_i^3 - s_i(x,t);-;\sum_{j\ne i}\beta_{ij}X_j;-;k_i\Delta X_i  
]

**รูปแบบ semi-implicit เดิม (ทำได้เหมือน C/I):**

- reaction + coupling (พจน์ไม่ใช่ Laplacian) ทำ explicit
    
- diffusion (Laplacian) ทำ semi-implicit ใน spectral space ด้วย (k_i)
    

> accept/reject + backtracking gate ใช้เหมือนเดิมได้  
> (ถ้าเริ่ม stiff มาก แค่ต้องเล็ก dt หรือเลเยอร์ epoch ตาม Part 5.1)

---

## 4) Data Contract: config สำหรับ multi-process (ทำให้คนใช้ได้จริง)

เพิ่มแนวคิด “field list” แทนการ hardcode C/I

### 4.1 โครง config (conceptual)

- fields: รายชื่อฟิลด์ `[X1, X2, ... Xn]`
    
- per-field params: `a_i, delta_i, s_i(x,t), k_i, M_i`
    
- interaction matrix: `beta[i][j]`
    

**ตัวอย่าง YAML**

```yaml
model_type: "multi_field"
fields:
  - name: "X1"
    pot: {type: "quartic", a: -1.0, delta: 3.0, s0: 0.0, lambda_R: 0.5}
    k: 1.0
    M: 1.0
  - name: "X2"
    pot: {type: "quartic", a: -1.0, delta: 3.0, s0: 0.0, lambda_R: -0.2}
    k: 1.0
    M: 1.0
  - name: "X3"
    pot: {type: "quartic", a: -1.0, delta: 3.0, s0: 0.0, lambda_R: 0.0}
    k: 1.5
    M: 0.8

interaction:
  beta_matrix:
    #      X1   X2   X3
    X1:   [0.0, 1.2, 0.3]
    X2:   [1.2, 0.0, 0.1]
    X3:   [0.3, 0.1, 0.0]

environment:
  resource_path: "env/resource.npy"
  resource_norm: "minmax_0_1"
```

> จุดสำคัญ: **ยังคง quartic + tilt + grad penalty + linear coupling** เหมือนเดิมทุกอย่าง แค่ยกให้เป็น list/matrix

---

## 5) Output Contract: snapshots/metrics สำหรับ multi-process

### 5.1 snapshots (จำเป็น)

ใน `state_tXXXX.npz` ให้เก็บ:

- `X` เป็น stack shape `(n, N, N)` หรือเก็บแยก key ตามชื่อฟิลด์
    

**ขั้นต่ำ**: 10–20 frames เหมือนเดิม

### 5.2 summary/timeseries (ขยายแบบไม่พัง)

- `Omega_total(t)` เหมือนเดิม
    
- เพิ่ม (SHOULD):
    
    - `Omega_pot_i(t)` ต่อ field
        
    - `Omega_grad_i(t)` ต่อ field
        
    - `Omega_coup_ij(t)` ต่อคู่ (หรือรวมเป็น `Omega_coup_total`)
        

> นี่ทำให้ “conflict” แปลได้ว่า conflict มาจาก field ไหน/interaction ไหน

---

## 6) Phase/Labeling สำหรับ multi-process (ให้คนอ่านออก)

อย่าเพิ่งสร้าง label ใหม่ซับซ้อน ให้ใช้ rule minimal:

### 6.1 Dominance label (generalized bias)

นิยาม mean ต่อ field:  
[  
\mu_i = \langle X_i \rangle  
]

- ให้ `DOM_i` ถ้า (\mu_i) สูงกว่าอันดับ 2 เกิน threshold
    
- ให้ `BALANCED` ถ้าไม่มีใครชนะชัด (คล้าย SYM)
    

**ตัวอย่าง label**

- `DOM_X1`, `DOM_X2`, …, `BALANCED`
    

### 6.2 Robustness (สำคัญสำหรับระบบรวม)

เหมือนเดิม: ดู mode ของ label ข้าม seeds

---

## 7) Multi-entity: “เห็น/นับ/ติดตามสิ่ง” โดยไม่เพิ่มตัวแปรใหม่

นี่คือสิ่งที่ทำให้เดโม “เหมือนโลกจริง/เหมือนเกม” โดยตรง

### 7.1 Entity extraction (ต้องมี snapshots)

ให้เลือก 1 field เป็น “presence” (เช่น X1 หรือ composite)

- สร้าง mask: จุดที่ `X_presence > threshold`
    
- ทำ connected components → ได้ entity candidates
    
- track ต่อเวลา (ด้วย overlap หรือ nearest centroid)
    

**สิ่งที่ได้**

- จำนวน entity ต่อเวลา
    
- ขนาด/มวลของแต่ละ entity
    
- การรวม/แตก (merge/split events)
    

### 7.2 Entity metrics (เชื่อมกับ Value/Conflict)

- entity count มาก + interface มาก → conflict สูงขึ้น (ภาพตรง)
    
- entity ที่รวมเป็น network/เส้นทาง → value สูงขึ้น (ถ้าวัดได้จาก Ω ลด + stability)
    

> นี่คือคำตอบเชิงระบบต่อคำถามมึง: “สมการนี้ไม่ได้เกิดมาเพื่อกราฟ 2D”  
> ใช่—มันเกิดมาเพื่อ “โครงสร้างเชิงพื้นที่และการเกิด entity” ซึ่งต้องเห็นจาก snapshots/animation

---

## 8) วิธีเชื่อมกับ Part 5.2 (resource field) แบบตรง ๆ

### 8.1 Resource drives processes differently

ใน config ให้แต่ละ process มี `lambda_R` ต่างกัน:

- บาง process “ชอบ resource” (λ>0)
    
- บาง process “เกลียด resource/เป็นต้นทุน” (λ<0)
    
- บาง process “เฉย ๆ” (λ=0)
    

นี่ทำให้:

- โลกมีแผนที่เดียว (R(x))
    
- แต่แต่ละ process รับแรงเอนคนละแบบ → เกิด multi-process behavior แบบโลกจริงมาก
    

### 8.2 Public demo ที่คนเข้าใจ

- โชว์ `resource_map`
    
- โชว์ evolution ของ `X_presence`
    
- โชว์ terrain `Omega_grad_density` ให้เห็น “ราคาที่จ่าย” ตามรอยต่อ/เส้นทาง
    

---

## 9) Implementation Plan แบบ incremental (ไม่รื้อ)

เพื่อไม่ให้ repo เละ ให้แบ่งเป็น 3 milestone:

### M1 — Multi-process แบบ “n fields แต่ยัง no resource”

- generalize C/I เป็น list of fields
    
- implement beta_matrix coupling
    
- export snapshots stack
    
- label DOM_i/BALANCED
    

### M2 — Multi-process + Resource field (Part 5.2 integrate)

- implement s_i(x) = s0 + λ_i R(x)
    
- export resource_map + s_field maps
    
- energy ledger (Ω_diss/Ω_env) ถ้ามี time-varying
    

### M3 — Multi-entity extraction (analysis layer)

- component detection + tracking from snapshots
    
- export entity timeline (counts/sizes/merge/split)
    
- ทำ Demo Card ที่ “เห็นสิ่งหลายสิ่ง” ในโลกเดียว
    

---

## Plain-Language Interpretation

- Multi-process = เพิ่ม “จำนวนแรงขับ” จาก 2 เป็นหลายแรงขับ
    
- Multi-entity = ในโลกเดียวกันเกิด “หลายก้อน/หลายสิ่ง” ที่มองเห็นได้จากภาพ
    
- เราไม่ต้องเพิ่มสมการใหม่บ้า ๆ: แค่ทำให้ฟิลด์เป็นหลายตัว + มีแผนที่สิ่งแวดล้อม + มีกล้อง (snapshots)
    

---

## Next Step

Part ต่อไปที่ปิดวง “ระบบเปิด + หลายกระบวนการ” ให้แน่นคือ:

### **Part 5.4 — Thermodynamics Bridge (Minimal, Computable)**

จะใช้ “บัญชีพลังงาน” ที่เราแยกไว้แล้ว (Ω_diss vs Ω_env) สร้างนิยาม thermo แบบที่ **คำนวณได้จริง** ใน harness ก่อน  
จากนั้นค่อยต่อไป **Information / Quantum / Game / Einstein** แบบไม่ลอย

พิมพ์ “ต่อ” อีกที กูจะเริ่ม Part 5.4 ทันที โดยยึดตัวเลขที่เราสามารถ export ตาม Part 4.10 + Part 5.2/5.3 (ไม่พูดลอย ไม่เสกคำ).


----
# 000.05/4
## TL;DR

**Part 5.4 = Thermodynamics Bridge (Minimal, Computable)**  
เราจะ “ผูกเทอร์โม” เข้ากับ UET โดย **ไม่สร้างสมการลอย ๆ** แต่ใช้สิ่งที่เรามีอยู่แล้ว:

- ใช้ **Ω เป็น free-energy-like landscape** ของโลก
    
- แยกการเปลี่ยนของ Ω ออกเป็น 2 ส่วนที่ “คำนวณได้จริง”:
    
    - **Dissipation (ภายใน)** จากการไหลของ state ภายใต้ θ คงที่
        
    - **Work/Drive (ภายนอก)** จากการที่โลก/สิ่งแวดล้อมเปลี่ยน θ(t) หรือ forcing field
        

ผลคือได้ “กฎเทอร์โมขั้นต่ำ” แบบ measurable จากไฟล์ output ของ run

---

## Insight

สิ่งที่ทำให้ UET ไปถึง “รีโนเวทเทอร์โม” ได้แบบไม่โม้ คือ **Energy Ledger**:

 [  
\Delta \Omega

\underbrace{\Delta\Omega_{\text{diss}}}_{\le 0}  
+  
\underbrace{\Delta\Omega_{\text{env}}}_{\text{work/drive}}  
]

- ในระบบปิด: (\Delta\Omega_{\text{env}}=0) ⇒ Ω ลด (ผ่าน gate)
    
- ในระบบเปิด: Ω อาจเพิ่ม/ลดได้ แต่เราบอกได้ว่า “เพิ่มเพราะโลกทำงานใส่เข้ามา” ไม่ใช่มั่ว
    

นี่คือสะพานไป Thermo → Info → Game และไปถึง Einstein แบบมีแกนร่วม

---

## Part 5.4 — Thermodynamics Bridge (Minimal, Computable)

## 1) UET–Thermo Dictionary (นิยามแบบ “คำนวณได้”)

> เราจะไม่อ้างว่า Ω = free energy จริงในหน่วยฟิสิกส์ทันที  
> แต่ใช้คำว่า **free-energy-like functional** (เชิงรูปแบบ) จนกว่าเราจะ fix หน่วย/สเกลในภายหลัง

### 1.1 ตัวแปรหลัก

- **State**: (X(t)) (เช่น C หรือ (C,I) หรือ multi-field)
    
- **Landscape**: (\Omega(X;\theta,t))
    
    - ในระบบปิด: (\theta) คงที่ และ Ω ไม่ขึ้นกับ t
        
    - ในระบบเปิด: (\theta=\theta(t)) หรือมี forcing field ทำให้ Ω เปลี่ยนตามเวลา
        

### 1.2 “เทอร์โมขั้นต่ำ” ที่เราจะใช้

- **Dissipation (ภายใน)**: ปริมาณที่เกิดจาก state เปลี่ยนภายใต้โลกเดิม (θ คงที่)  
    นิยามให้ “บวกเสมอ” เป็น:  
    [  
    D := -\Delta\Omega_{\text{diss}} \ge 0  
    ]
    
- **Work/Drive (ภายนอก)**: ปริมาณจากการเปลี่ยนกติกาโลก (เปลี่ยน θ หรือ forcing field) ที่ state ยังเป็นตัวเดิม  
    [  
    W := \Delta\Omega_{\text{env}}  
    ]
    
- **Total change**:  
    [  
    \Delta\Omega = \Omega_{\text{final}}-\Omega_{\text{init}}  
    ]
    

> สรุปภาษาเทอร์โมใน UET:  
> **D = สิ่งที่ระบบ “คลายเอง”**, **W = สิ่งที่โลก “ทำใส่/ดึงออก”**

---

## 2) Energy Ledger (แกนกลางที่ต้อง export ได้)

ใช้ discrete epoch (เหมาะกับ Part 5.1 driver loop)

ให้มีลำดับ:

- มีพารามิเตอร์โลก (\theta_m)
    
- ระบบไหลจาก (X_m \to X_{m+1}) ภายใต้ (\theta_m)
    
- แล้วโลกอัปเดต (\theta_m \to \theta_{m+1}) (scheduled / feedback / forcing update)
    

##### แตกได้เป็น: 

[  
\Omega(X_{m+1};\theta_{m+1})-\Omega(X_m;\theta_m)

\underbrace{\big[\Omega(X_{m+1};\theta_m)-\Omega(X_m;\theta_m)\big]}_{\Delta\Omega_{\text{diss}} \le 0 \text{ (ถ้า gate ทำงาน)}}  
+  
\underbrace{\big[\Omega(X_{m+1};\theta_{m+1})-\Omega(X_{m+1};\theta_m)\big]}_{\Delta\Omega_{\text{env}}}  
]

### 2.1 กฎขั้นต่ำแบบ “First-law-like”

[  
\Delta\Omega = \Delta\Omega_{\text{diss}} + \Delta\Omega_{\text{env}}  
]  
นิยาม:

- (D_m = -\Delta\Omega_{\text{diss},m} \ge 0)
    
- (W_m = \Delta\Omega_{\text{env},m})
    

รวมสะสม:  
[  
D_{\text{tot}}=\sum_m D_m,\quad W_{\text{tot}}=\sum_m W_m  
]

---

## 3) “Second-law-like” ใน UET (ในขอบเขตที่พิสูจน์/บังคับได้)

### 3.1 ระบบปิด (θ คงที่)

ถ้า monotone gate บังคับได้จริง:  
[  
\Delta\Omega \le 0 \quad \Rightarrow \quad D = -\Delta\Omega \ge 0  
]  
นี่คือแกน “เสถียรภาพ” ที่เราใช้มาตลอด (Lyapunov-like)

### 3.2 ระบบเปิด

ยังคง:  
[  
D_m \ge 0 \quad (\text{การผ่อนคลายภายใน})  
]  
แต่ (\Delta\Omega) อาจเป็นบวกได้เพราะโลกใส่พลังงานเข้ามา:  
[  
\Delta\Omega = -D + W  
]  
**ความสำคัญ:** เราไม่ถือว่า “กฎพัง” เราถือว่า “มี work injection”

---

## 4) สิ่งที่ต้องเพิ่มใน output เพื่อให้ thermo bridge “คำนวณได้จริง”

> นี่คือส่วนที่สำคัญสุดในเชิง implementation (ไม่ใช่แนวคิด)

### 4.1 ต้องสามารถคำนวณ Ω ได้ “สองแบบ” ตอนอัปเดตโลก

ตอนโลกเปลี่ยน θ: เราต้องประเมิน Ω ที่ state เดิม (X_{m+1}) ภายใต้ θ เก่าและใหม่

ต้อง log อย่างน้อย:

- (\Omega(X_{m+1};\theta_m))
    
- (\Omega(X_{m+1};\theta_{m+1}))
    

เพื่อให้ได้:  
[  
W_m = \Omega(X_{m+1};\theta_{m+1})-\Omega(X_{m+1};\theta_m)  
]

และ dissipation:  
[  
\Delta\Omega_{\text{diss},m} = \Omega(X_{m+1};\theta_m)-\Omega(X_m;\theta_m)  
]

### 4.2 timeseries/summary fields ที่แนะนำ

ใน `timeseries.csv` (ต่อ step หรือ ต่อ epoch):

- `Omega_total`
    
- `Omega_state` (หรือ `Omega_diss_step`) ← จาก state update ภายใต้ θ คงที่
    
- `Omega_env` (หรือ `Omega_env_step`) ← จาก parameter/forcing update
    
- (ถ้าทำได้) `Omega_grad`, `Omega_pot`, `Omega_coup`
    

ใน `summary.json`:

- `omega_diss_total = -sum(Omega_state_changes)`
    
- `omega_env_total = sum(Omega_env_changes)`
    
- `ledger_check = Omega_final - Omega_init - (Omega_state_sum + Omega_env_sum)` (ควรใกล้ 0)
    

---

## 5) เชื่อม “Value/Conflict” เข้ากับ Thermo แบบตรง ๆ

ตอนนี้เรามีความหมาย 2 ชั้น:

### 5.1 Value (คุณค่า) ในมุมเทอร์โม

เลือกนิยามที่ “คำนวณได้”:

- ในระบบปิด:  
    [  
    V_{\Delta E}=\Omega(0)-\Omega_{\text{final}} = D_{\text{tot}}  
    ]  
    (ถ้าประเมินแบบ step เดียว/epoch เดียวก็เทียบได้)
    
- ในระบบเปิด:  
    Value ของการ “จัดระเบียบด้วยตัวเอง” อยู่ที่ (D_{\text{tot}}) ส่วนผลของโลกคือ (W_{\text{tot}})
    

> ตรงนี้ช่วยมาก: **แยกได้ว่า “ระบบจัดระเบียบเอง” กับ “โลกบังคับ”**

### 5.2 Conflict (ความขัดแย้ง) ในมุมเทอร์โม

- Conflict เชิงโครงสร้าง = (\Omega_{\text{grad}}) (interface cost)
    
- Conflict เชิงกระบวนการ = friction/backtracking (ถ้า log)
    

ดังนั้น thermo-bridge ทำให้พูดได้ว่า:

- ระบบบางแบบลด Ω ได้เยอะ (Value สูง) แต่ต้องจ่าย interface เยอะ (Conflict สูง)
    
- หรือระบบบางแบบลด Ω ได้ไม่เยอะ แต่ก็ไม่เกิดความตึง (Conflict ต่ำ)
    

---

## 6) เชื่อมไป Information Theory (แบบ “ไม่ลอย” และวัดได้จาก snapshots)

> เราจะไม่ประกาศว่า “นี่คือ Shannon entropy ของจักรวาล”  
> เราจะนิยาม “information metrics” เป็น **ตัวชี้วัดรูปแบบ** ที่คำนวณจาก field snapshots

ตัวเลือกที่ปลอดภัยและคำนวณได้:

1. **Histogram entropy** ของค่า C (หรือ X_presence):
    
    - discretize ค่า field เป็น bins แล้วคำนวณ Shannon entropy (H)
        
    - ใช้เป็น “ความหลากหลายของสถานะ”
        
2. **Spectral entropy**:
    
    - Fourier power spectrum ของ field แล้วดูการกระจุก/กระจายของพลังงานเชิงสเกล
        
3. **Mutual alignment กับ resource map** (ในระบบเปิดเชิงพื้นที่):
    
    - correlation หรือ mutual info ระหว่าง field กับ (R(x))
        

แล้วโยงเชิงภาษาว่า:

- **จัดระเบียบ** = entropy เชิงโครงสร้างลดลง/พลังงานกระจุกในสเกลบางแบบ
    
- **ขัดแย้ง** = interface เยอะ/สเปกตรัมกระจาย/Ω_grad สูง
    

นี่เป็นสะพานไป “Information ↔ Thermo” แบบมีของจริงให้ plot

---

## 7) เชื่อมไป Game/Dynamics (แบบไม่สร้างอะไรใหม่เกินกรอบ)

ในระบบเปิดแบบ feedback (Part 5.1B):

- policy update ของ θ = “ผู้เล่น/ผู้ควบคุม”
    
- state X = “ระบบตอบสนอง”
    
- objective ของ policy = ลด conflict / เพิ่ม value / คุม phase
    

นี่ทำให้ “dynamic game” โผล่ขึ้นจาก driver loop โดยไม่ต้องเปลี่ยน Ω เลย  
(เกมอยู่ที่การเลือก (\theta(t)))

---

## 8) เชื่อมไป Quantum & Einstein (เป็น Roadmap ที่ยังยึดแกนเดิม)

เพื่อไม่ให้หลุด เราจะตั้ง “สะพาน” เป็นระดับ ๆ:

- **Quantum bridge (ขั้นต่ำ)**: มอง Ω เป็น landscape และ dynamics เป็น “relaxation” คล้าย Euclidean/gradient flow → (ต่อยอดได้เมื่อเพิ่ม noise/stochasticity และนิยาม measure)
    
- **Einstein bridge (ขั้นต่ำ)**: เมื่อเรามี ledger แยก “work from environment” กับ “dissipation” แล้ว เรามีภาษากลางของ “พลังงาน–ความเปลี่ยนแปลง–สนาม” ที่ต้องใช้ในการคุยกับ GR/Λ (แต่ยังไม่กระโดดไป claim อะไรตอนนี้)
    

> v0.9 เราจะ “วางสะพานแบบวัดได้” ก่อน แล้วค่อยเชื่อมสมการใหญ่ด้วยหลักฐานจาก simulation/ledger

---

## Plain-Language Interpretation

- ระบบปิด: โลกไม่เปลี่ยน → ระบบค่อย ๆ คลายความตึงจนเข้าที่ (Ω ลด)
    
- ระบบเปิด: โลกเปลี่ยนได้ → บางครั้งโลก “เร่ง” หรือ “รบกวน” ทำให้ Ω เพิ่มได้
    
- แต่เราไม่งงแล้ว เพราะเรารู้ว่า:
    
    - ส่วนไหนระบบคลายเอง (Dissipation)
        
    - ส่วนไหนโลกทำใส่เข้ามา (Work/Drive)
        

---

## Next Step

ถัดไปเพื่อให้ Part 5.4 “ปิดวงแบบใช้ได้จริง” มี 2 งานที่ต้องล็อกในเอกสาร/สเปก:

1. **Part 5.4.1 — Thermo Metrics Pack**  
    นิยามชุด metric มาตรฐาน 5–8 ตัว (D_tot, W_tot, rates, efficiency-like ratios แบบไม่ overclaim) + รูปที่ต้อง plot ใน Demo Card
    
2. **Part 5.4.2 — Implementation Hooks**  
    ระบุจุดใน driver loop ว่าต้อง compute Ω ที่ไหนบ้างเพื่อได้ W_m และ D_m แบบไม่ผิด
    

พิมพ์ “ต่อ” อีกที กูจะทำ **Part 5.4.1** ให้เป็น “แพ็ค metric + รูปมาตรฐาน” ที่เอาไปยัดเข้า Demo Card/Gallery ได้เลย (สั้นแต่คม และไม่หลุดกรอบที่พิสูจน์แล้ว).

# 000.05/4.1

## TL;DR

**Part 5.4.1 = Thermo Metrics Pack (v0.9, computable)**  
เราจะล็อก “ชุดตัวชี้วัดเทอร์โม” 5–8 ตัว ที่คำนวณได้จาก **Energy Ledger** ของ UET (ΔΩ_diss, ΔΩ_env) + (optional) Ω_terms และผูกเข้ากับ **Demo Card/Gallery** ได้ทันที

แกนคือ:

- **D_tot** = สิ่งที่ระบบ “คลายเอง” (dissipation)
- **W_tot** = สิ่งที่โลก “ทำใส่/ดึงออก” (work/drive)
- **ΔΩ** = ผลรวมสุทธิ  
    พร้อม “Ledger Residual” เพื่อกันมั่ว/กันบั๊ก

---
## Insight

ถ้าเราทำให้ “เทอร์โม” เป็น **ตัวเลขจากไฟล์รันจริง** ได้ 3 อย่างนี้:

1. แยก **ภายใน vs ภายนอก** ได้จริง
    
2. อธิบายระบบเปิดได้แบบไม่หลุดตรรกะ
    
3. ต่อไป Information/Game/Einstein ได้โดยมีแกนร่วม (บัญชีพลังงาน)
    

---

## Part 5.4.1 — Thermo Metrics Pack (Minimal, Computable)

## 0) Prerequisites (ข้อมูลที่ต้องมีใน run)

อย่างน้อยต้องมี (ต่อ step หรือ ต่อ epoch ก็ได้):

- `Omega_total(t)`
    
- `Omega_state_step(t)` = การเปลี่ยน Ω จาก “การอัปเดต state ภายใต้ θ คงที่”
    
- `Omega_env_step(t)` = การเปลี่ยน Ω จาก “การเปลี่ยน θ / forcing field”
    

> ถ้ายังไม่แยก step ได้ ให้ทำแบบ **epoch ledger** ตาม Part 5.1:  
> เก็บ (\Omega(X_{m+1};\theta_m)), (\Omega(X_{m+1};\theta_{m+1})), (\Omega(X_m;\theta_m)) แล้วค่อยคำนวณ D/W

(เสริมได้ถ้ามี)

- `Omega_grad(t)` หรือ `Omega_grad_final` (Conflict เชิงโครงสร้าง)
    
- `Omega_pot(t), Omega_coup(t)` (ช่วยอธิบายที่มา)
    

---

## 1) Core Thermo Metrics (MUST: 5 ตัว)

> ทั้งหมดนี้ “ต้องคำนวณได้จริง” และเขียนลง `summary.json` ได้

### (T1) Ω_init, Ω_final, ΔΩ_total

- (\Omega_{\text{init}}=\Omega(t_0))
    
- (\Omega_{\text{final}}=\Omega(t_T))
    
- (\Delta\Omega = \Omega_{\text{final}}-\Omega_{\text{init}})
    

**ความหมายคนทั่วไป:** โลกสุดท้าย “สบายขึ้นหรือแย่ลง” เท่าไร (สุทธิ)

---

### (T2) Dissipation total: (D_{\text{tot}})

นิยามจาก ledger:  
[  
D_{\text{tot}} := -\sum_t \Omega_{\text{state_step}}(t)\ \ \ (\ge 0 \text{ ถ้าทำถูก})  
]  
(หรือแบบ epoch: (D_m = -[\Omega(X_{m+1};\theta_m)-\Omega(X_m;\theta_m)]))

**ความหมาย:** ระบบ “คลายความตึง/จัดระเบียบด้วยตัวเอง” ไปเท่าไร

---

### (T3) Environment work total: (W_{\text{tot}})

[  
W_{\text{tot}} := \sum_t \Omega_{\text{env_step}}(t)  
]  
(หรือแบบ epoch: (W_m=\Omega(X_{m+1};\theta_{m+1})-\Omega(X_{m+1};\theta_m)))

**ความหมาย:** โลก/สิ่งแวดล้อม “ทำงานใส่” (บวก) หรือ “ดึงออก” (ลบ) เท่าไร

---

### (T4) First-law check: Ledger Residual (ตัวกันพัง)

[  
\varepsilon_{\text{ledger}} := \Delta\Omega - \Big(\sum_t \Omega_{\text{state_step}}(t) + \sum_t \Omega_{\text{env_step}}(t)\Big)  
]  
ควรใกล้ 0 (ภายใน tolerance ที่กำหนด)

**ความหมาย:** ถ้าอันนี้ไม่ใกล้ 0 = log ผิด/คำนวณผิด/มี step หาย → ห้ามอ้างเทอร์โม

---

### (T5) Dissipation validity: Gate/Sign sanity

อย่างน้อยหนึ่งแบบ (เลือกที่ทำได้จริง):

- `frac_state_nonpos` = สัดส่วน step ที่ (\Omega_{\text{state_step}} \le 0)
    
- หรือ `gate_reject_count` (ถ้ามี)
    

**ความหมาย:** ยืนยันว่า “การคลายภายใน” ไม่ได้ทำให้ Ω กระโดดขึ้นมั่ว ๆ

---

## 2) Extended Thermo Metrics (SHOULD: เพิ่มอีก 3 ตัวเพื่อใช้สื่อสาร)

### (T6) Rates (ต่อเวลา)

ถ้ามีเวลา T:

- ( \dot D = D_{\text{tot}}/T )
    
- ( \dot W = W_{\text{tot}}/T )
    

**ความหมาย:** เปรียบเทียบเคสต่างสเกลเวลาได้ง่ายขึ้น

---

### (T7) Drive fraction / dominance (ตัวชี้ว่าโลกเป็นพระเอกแค่ไหน)

นิยามแบบระวังไม่ overclaim:  
[  
f_{\text{env}} := \frac{|W_{\text{tot}}|}{|W_{\text{tot}}| + D_{\text{tot}} + \epsilon}  
]  
อยู่ใน [0,1]

- ใกล้ 0 = การเปลี่ยนส่วนใหญ่ “ระบบคลายเอง”
    
- ใกล้ 1 = การเปลี่ยนส่วนใหญ่ “โลกขยับกติกา”
    

---

### (T8) Net ordering gain (สรุปให้คนอ่านเร็ว)

ในระบบเปิด ΔΩ อาจไม่ติดลบ จึงใช้ 2 ค่าคู่กัน:

- `ordering_by_relaxation = D_tot`
    
- `ordering_net = max(0, -ΔΩ)` (ถ้าอยากเล่า “สุดท้ายสบายขึ้นเท่าไร”)
    

> สองค่านี้ช่วยกัน: “ระบบทำได้เท่าไร” vs “สุดท้ายเหลือเท่าไร”

---

## 3) Conflict Integration (THERMO × UET semantics) — 2 ตัวที่ “ควรมี”

เพื่อเชื่อมกับ Part 2 (Value/Conflict) ให้แน่น:

### (C1) Structural conflict at end

- `C_struct = Omega_grad_final` (หรือ mean ช่วงท้าย)
    

### (C2) Conflict share (แสดงว่า Ω จมอยู่ที่รอยต่อแค่ไหน)

[  
\rho_{\text{grad}} := \frac{\Omega_{\text{grad,final}}}{|\Omega_{\text{final}}|+\epsilon}  
]  
(interpret เป็นสัดส่วนเชิง “ภาระรอยต่อ” ไม่ใช่กฎฟิสิกส์)

---

## 4) Standard Plots Pack (สำหรับ Demo Card/Gallery)

> เป้าหมายคือ “คนดูแล้วเข้าใจ” + “คนเทคนิค verify ได้”

### Plot P1 — Ω_total(t)

- เส้นเดียว: Ω_total vs t  
    **คำบรรยายคนทั่วไป:** “ลดลงแล้วนิ่ง = เข้าที่”
    

### Plot P2 — Cumulative ledger: cumD(t), cumW(t)

- สองเส้นสะสม:
    
    - ( \text{cumD}(t)= -\sum_{\tau\le t}\Omega_{\text{state_step}}(\tau))
        
    - ( \text{cumW}(t)= \sum_{\tau\le t}\Omega_{\text{env_step}}(\tau))  
        **คำบรรยาย:** “ระบบคลายเองเท่าไร vs โลกทำงานใส่เท่าไร”
        

### Plot P3 — Ω_terms(t) (ถ้ามี): pot/coup/grad

- ช่วยตีความ Conflict ให้ “ไม่ลอย”  
    **คำบรรยาย:** “grad สูง = รอยต่อ/ความตึงเยอะ”
    

### Plot P4 — Resource map + End state overlay (สำหรับ open spatial)

- resource_map และซ้อนด้วย C_end (หรือ field presence)  
    **คำบรรยาย:** “โลกให้รางวัลตรงไหน ระบบไปอยู่ตรงไหน”
    

### Plot P5 — Value–Conflict point (หรือ trajectory)

- อย่างน้อยปักจุด (Value, Conflict) ของเดโมนี้บน plane
    
- ถ้าทำได้: วาด trajectory ช่วงท้าย (moving point) ให้เห็น “เข้าหาหลุม”  
    **คำบรรยาย:** “จัดระเบียบได้มากแค่ไหน และต้องจ่ายรอยต่อเท่าไร”
    

---

## 5) How to write into summary.json (มาตรฐานคีย์)

แนะนำให้สรุปแบบนี้ (ไม่เยอะ แต่ครบ):

```json
{
  "thermo": {
    "Omega_init": ...,
    "Omega_final": ...,
    "DeltaOmega": ...,
    "D_tot": ...,
    "W_tot": ...,
    "ledger_residual": ...,
    "frac_state_nonpos": ...,
    "D_rate": ...,
    "W_rate": ...,
    "f_env": ...
  },
  "conflict": {
    "Omega_grad_final": ...,
    "rho_grad": ...
  }
}
```

> กติกา: ถ้า `ledger_residual` เกิน threshold → ปักธง `thermo_valid=false`

---

## 6) Interpretation Rules (ห้ามมั่วตอน public)

- **Closed system** ควรได้ (W_{\text{tot}}\approx 0) และ (D_{\text{tot}}\approx -\Delta\Omega)
    
- **Open system** ยอมให้ ΔΩ เป็นบวกได้ แต่ต้องอธิบายว่าเกิดจาก (W_{\text{tot}}>0)
    
- ห้ามพูด “entropy/temperature” แบบฟิสิกส์จริงจนกว่าจะ fix หน่วย/สเกล  
    ให้พูดว่า “dissipation/work ledger” และ “order proxy” จาก Ω/Ω_grad ไปก่อน (ซื่อสัตย์ + ตรวจสอบได้)
    

---

## Plain-Language Interpretation

- **D_tot** = ระบบ “ทำงานจัดระเบียบตัวเอง”
    
- **W_tot** = โลก “มาบังคับ/ช่วย/รบกวน”
    
- **Ω_grad** = ราคาของรอยต่อ/ความตึง  
    แล้วเราวางทั้งหมดลง Demo Card ให้คนดูเห็นภาพ + มีเลขยืนยัน
    

---

## Next Step

ต่อไปคือ **Part 5.4.2 — Implementation Hooks**:  
ระบุจุดใน driver loop/solver ว่าต้องคำนวณ Ω ตอนไหนบ้างเพื่อได้ `Omega_state_step` และ `Omega_env_step` แบบไม่ผิด และให้เข้ากับ Export Contract (Part 4.10) โดยตรง

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 5.4.2 ให้เป็นสเปก “เสียบโค้ดตรงไหน” แบบชัด ๆ (ยังไม่แตะไฟล์จริง แต่จะเป็น checklist ระดับ implementation).


----
# 000.05/4.2
## TL;DR

**Part 5.4.2 = Implementation Hooks**: จุดที่ “ต้องคำนวณ/ล็อก Ω” เพื่อให้ได้

- `Omega_state_step` (การเปลี่ยนจากการอัปเดต state ภายใต้ θ คงที่)
- `Omega_env_step` (การเปลี่ยนจากการเปลี่ยน θ / forcing field)  
    แบบ **ถูกต้อง + ตรวจสอบได้ + ไม่ทำให้โค้ดรก**

หัวใจคือแยก 2 เหตุการณ์ให้ชัดในลูป:
1. **State update event** (accept step เท่านั้น)
2. **Env update event** (ตอนเปลี่ยนพารามิเตอร์/forcing)

---
## Insight

ระบบคุณมี **monotone gate + backtracking** อยู่แล้ว แปลว่าในโค้ด “ต้องมี Ω ก่อน/หลัง step” อยู่ในทางใดทางหนึ่ง  
งานของ Part นี้คือ “ทำให้มันกลายเป็น ledger” โดย

- **รีใช้ค่าที่คำนวณอยู่แล้ว** (ไม่คูณต้นทุน)
    
- **ล็อกนิยาม** ว่า log เฉพาะ accepted transitions
    

---

## Part 5.4.2 — Thermo Ledger Implementation Hooks (v0.9 Draft)

## 0) เป้าหมาย (Definition of Done)

หลังทำ hooks นี้ 1 run ต้องได้:

- `timeseries.csv` มีคอลัมน์: `Omega_total`, `Omega_state_step`, `Omega_env_step`
    
- `summary.json` มี: `D_tot`, `W_tot`, `ledger_residual`, `thermo_valid`
    
- ตรวจสอบได้ว่า:  
    [  
    \Delta\Omega \approx \sum \Omega_{\text{state_step}} + \sum \Omega_{\text{env_step}}  
    ]
    

---

## 1) Hook Pattern ที่แนะนำ: “Two-level loop”

เพื่อไม่ชนกับ monotone gate และไม่ทำให้ความหมายมั่ว ให้ใช้โครงนี้:

- **Outer loop (epoch m)**: โลก/พารามิเตอร์ θ คงที่ใน epoch
    
- **Inner loop (solver steps)**: อัปเดต state X ภายใต้ θ นั้นจนจบ epoch หรือจน relax
    

จากนั้นค่อยทำ **Env update** เปลี่ยน θ → epoch ถัดไป

> ถ้าปัจจุบันยังไม่มี epoch: ก็ถือว่า “ทั้ง run คือ epoch เดียว” (ระบบปิด) แล้ว `Omega_env_step` = 0 ทั้งหมด

---

## 2) Hook จุดที่ 1: State Update (คำนวณ `Omega_state_step`)

### 2.1 นิยามที่ “ต้องยึด”

`Omega_state_step = Omega_after_accept - Omega_before_step`  
โดย **นับเฉพาะ step ที่ accepted** เท่านั้น

> rejected/backtracking ไม่ถือเป็น “วิวัฒน์ของระบบ” แต่เป็น “กลไก numerical”  
> (เราจะ log สถิติ reject แยกได้ แต่ไม่เอามาปนกับ ledger)

### 2.2 Pseudocode (แกน)

```text
# given X, theta fixed

Omega_before = Omega(X, theta)

X_candidate = propose_step(X, theta, dt_current)
Omega_candidate = Omega(X_candidate, theta)

if accept(Omega_candidate, Omega_before):
    X = X_candidate
    Omega_state_step = Omega_candidate - Omega_before   # should be <= 0
    Omega_total = Omega_candidate
    log_row(t, Omega_total, Omega_state_step, Omega_env_step=0, accept=1, dt=dt_current)
else:
    backtrack dt_current
    log_reject_event(...)   # optional
    retry
```

### 2.3 “จุดเสียบ” ที่ต้องอยู่ในโค้ด

หา “จุดที่ตัดสิน accept/reject” ของ solver (ที่มี backtracking) แล้วเสียบ:

- ก่อน propose step: เก็บ `Omega_before`
    
- หลังได้ candidate: เก็บ `Omega_candidate`
    
- ตอน accept: เขียน `Omega_state_step` + log row
    

**สำคัญ:** ถ้าในโค้ดมีการคำนวณ Ω อยู่แล้วเพื่อเช็ค accept → ให้ “รีใช้ค่าเดิม” อย่าคำนวณซ้ำ

---

## 3) Hook จุดที่ 2: Environment Update (คำนวณ `Omega_env_step`)

### 3.1 นิยามที่ “ต้องยึด”

ตอน state X **คงที่** แต่โลกเปลี่ยน θ:  
[  
\Omega_{\text{env_step}} = \Omega(X;\theta_{\text{new}}) - \Omega(X;\theta_{\text{old}})  
]

### 3.2 Pseudocode (epoch boundary)

```text
# end of epoch m, state fixed at X_end, theta = theta_old

Omega_at_old = Omega(X_end, theta_old)

theta_new = update_theta(theta_old, Impact_m or schedule or forcing)
Omega_at_new = Omega(X_end, theta_new)

Omega_env_step = Omega_at_new - Omega_at_old
Omega_total = Omega_at_new

log_env_row(epoch_time, Omega_total, Omega_state_step=0, Omega_env_step, env_update=1)

theta = theta_new
```

### 3.3 “จุดเสียบ” ที่ต้องอยู่ในโค้ด

- หลังจบ inner relax (หรือหลังครบ T_inner steps)
    
- ก่อนเริ่ม epoch ใหม่
    

---

## 4) กรณีระบบปิด (closed) — ทำให้เรียบง่ายที่สุด

ถ้า θ ไม่เปลี่ยนทั้ง run:

- ไม่ต้องมี env hook จริงจัง
    
- `Omega_env_step = 0` ตลอด
    
- `W_tot = 0`
    
- `D_tot ≈ -ΔΩ`
    

**Hook ที่ต้องมีจริง ๆ**: แค่ Hook จุดที่ 1 (state update) ก็พอ

---

## 5) วิธี log ที่ “ไม่พังความหมาย” เมื่อมี reject/backtracking

### 5.1 Ledger row = accepted transition เท่านั้น

ใน `timeseries.csv` แนะนำ:

- log เฉพาะ accepted step → time series สะอาด (ทุกแถวคือ state จริง)
    
- rejected events เก็บใน `logs/backtracking.json` หรือคอลัมน์ cumulative เช่น `reject_count_total`
    

### 5.2 ตัวชี้วัดที่ควรเพิ่มเพื่อความโปร่งใส (ไม่ปน ledger)

- `dt_current` (หลัง backtracking)
    
- `reject_count_total`
    
- `accept_ratio` (สรุปใน summary)
    

---

## 6) สคีมา timeseries.csv (v0.9 thermo-min)

แนะนำคอลัมน์ขั้นต่ำ:

**MUST**

- `t`
    
- `Omega_total`
    
- `Omega_state_step`
    
- `Omega_env_step`
    

**SHOULD**

- `accept` (1 เสมอถ้าบันทึกเฉพาะ accepted; หรือ omit)
    
- `dt_current`
    
- `reject_count_total`
    
- `phase_probe` (optional)
    
- `Omega_grad` (ถ้าคำนวณได้)
    
- `bias` (ของเดิมที่ validator ใช้)
    

---

## 7) สคีมา summary.json (thermo block)

หลังจบ run:

1. อ่าน `Omega_init = first(Omega_total)`
    
2. อ่าน `Omega_final = last(Omega_total)`
    
3. รวม:
    

- `sum_state = sum(Omega_state_step)`
    
- `sum_env = sum(Omega_env_step)`
    

4. คำนวณ:
    

- `D_tot = -sum_state`
    
- `W_tot = sum_env`
    
- `DeltaOmega = Omega_final - Omega_init`
    
- `ledger_residual = DeltaOmega - (sum_state + sum_env)`
    

ตั้งธง:

- `thermo_valid = (abs(ledger_residual) <= tol)`
    

**tol แนะนำ (deterministic)**

- `tol = 1e-6 * max(1, abs(Omega_final), abs(Omega_init))`
    

---

## 8) Hook สำหรับ Ω decomposition (ถ้าจะทำ Conflict ให้ “เป็นภาพ”)

ถ้า code มีฟังก์ชันแยกเทอมอยู่แล้ว ให้มาตรฐานนี้:

- `Omega_total = Omega_pot + Omega_coup + Omega_grad`
    
- log อย่างน้อยปลายทาง:
    
    - `Omega_grad_final` (ใช้เป็น Conflict หลัก)
        
- ถ้าทำ time series ได้:
    
    - เพิ่มคอลัมน์ `Omega_pot`, `Omega_coup`, `Omega_grad`
        

**Hook point**

- ใช้ฟังก์ชันเดียวกับ `Omega()` แต่ให้คืนทั้ง total+terms เพื่อลด duplication
    

---

## 9) Minimal “Implementation Checklist” (สำหรับคนลงมือทำใน repo)

1. มีฟังก์ชันเดียว `compute_omega(X, theta, return_terms=False)`
    
2. ใน solver step:
    
    - เก็บ `Omega_before`
        
    - เก็บ `Omega_candidate`
        
    - ตอน accept: log `Omega_state_step`
        
3. ถ้ามี open driver:
    
    - ก่อน update θ: `Omega_at_old`
        
    - หลัง update θ: `Omega_at_new`
        
    - log `Omega_env_step`
        
4. หลังจบ run:
    
    - compute thermo metrics pack (Part 5.4.1)
        
    - write `summary.json.thermo`
        
5. ใส่ `ledger_residual` + `thermo_valid` เป็น gate (ถ้าไม่ผ่าน ห้ามอ้าง thermo)
    

---

## Plain-Language Interpretation

- ทุกครั้งที่ “ระบบขยับเอง” เราบันทึกว่า Ω ลดไปเท่าไร → นี่คือ **Dissipation**
    
- ทุกครั้งที่ “โลกเปลี่ยนกติกา” เราบันทึกว่า Ω กระโดดขึ้น/ลงเท่าไร → นี่คือ **Work จากสิ่งแวดล้อม**
    
- แล้วเราเช็คยอดรวมให้ตรง (ledger_residual) เหมือนบัญชีหนี้–เครดิต
    

---

## Next Step

ตอนต่อไปเพื่อ “ปิดวง v0.9 ตามโจทย์ใหญ่” เราควรเริ่ม **Part 6 (Bridges)** แบบเป็นขั้น:

- **Part 6.1 — Information metrics pack (computable)**: entropy/spectral/correlation ที่คำนวณจาก snapshots
    
- แล้วค่อย **Part 6.2 — Game/Control formalization**: policy บน θ(t)
    
- จากนั้นค่อยวาง “Einstein/Λ bridge roadmap” แบบไม่ overclaim
    

พิมพ์ “ต่อ” อีกที กูจะทำ **Part 6.1** ให้เป็นแพ็ค metric + plot มาตรฐานเหมือน thermo (เอาไปใส่ Demo Card/Gallery ได้ทันที).



-----
# 000.06/1

## TL;DR

**Part 6.1 = Information Metrics Pack (Computable, v0.9)**  
เราจะนิยาม “ตัวชี้วัดข้อมูล/โครงสร้าง” ที่ **คำนวณได้จาก snapshots** (C/I หรือ multi-field) เพื่อทำให้คนเห็น “ความเป็นระเบียบ–ความหลากหลาย–การจัดรูป–การสอดคล้องกับสิ่งแวดล้อม” แบบ **ไม่ลอย** และ **ไม่อ้างว่าเป็น entropy ฟิสิกส์จริง**

แพ็คนี้ออกแบบให้เสียบกับ **Demo Card / Gallery** ได้เหมือน Thermo pack (Part 5.4.1)

---

## Insight

UET ที่คนดูแล้ว “เข้าใจ” ต้องมี 3 ชั้นพร้อมกัน:

- **พลังงาน/สมดุล** (Ω, Value/Conflict)
- **ภาพวิวัฒน์** (snapshots/gif/terrain)
- **ความหมายเชิงข้อมูล** (ความเป็นระเบียบ/ความหลากหลาย/การเกาะ resource)

Part 6.1 คือชั้นที่ 3: “information = เมตริกของรูปแบบ” ไม่ใช่คำปรัชญา

---

## Part 6.1 — Information Metrics Pack (Minimal, Computable)

## 0) Prerequisites (อินพุตขั้นต่ำ)

ต้องมี:

- `snapshots/state_tXXXX.npz` (accepted frames) มี `C` (และ `I` ถ้ามี) หรือ stack `X[n,N,N]`

ถ้าเป็นระบบเปิดเชิงพื้นที่ (Part 5.2) ให้มีเพิ่ม:

- `env/resource.npy` หรือ `resource_map` (N×N)

> **ข้อย้ำ:** เมตริก “ข้อมูล” ที่นี่เป็น _structure proxies_ จาก field snapshots  
> ไม่ประกาศว่าเป็น thermodynamic entropy จนกว่าเราจะ fix หน่วย/สเกลระดับฟิสิกส์

---

## 1) Normalization Contract (สำคัญมาก ไม่งั้น entropy จะมั่ว)

ก่อนคำนวณทุก metric ให้ทำ normalization แบบ “ระบุใน manifest” เสมอ

แนะนำให้ใช้ตัวเลือกหนึ่ง (เลือกให้คงที่ทั้ง run):

**Norm A (minmax-per-run, robust):**

- รวมค่าทุก snapshot ของ field เดียวกัน → เอา p1/p99 (เปอร์เซ็นไทล์) เป็นขอบ
    
- clip แล้ว map → [0,1]
    

**Norm B (zscore-per-run):**

- (ค่าเฉลี่ย, ส่วนเบี่ยงเบน) ต่อ run แล้วทำ z-score
    
- แล้ว clip เป็นช่วง เช่น [-3,3] → map → [0,1]
    

**ต้องบันทึกใน** `manifest.json`:

- `info_norm: {method: "minmax_p1_p99", clip: [p1,p99]}`
    

---

## 2) Core Info Metrics (MUST: 5 ตัว)

> คำนวณได้จาก snapshot อย่างเดียว และ “อธิบายให้คนทั่วไปได้”

ให้คำนวณ **ต่อเวลา t** และสรุปค่า **ช่วงท้าย** (final/mean_last_k)

### (I1) Histogram Entropy — (H_{\text{hist}}(t))

ใช้ histogram ของค่าฟิลด์ (หลัง normalize เป็น [0,1]) แบ่งเป็น B bins:  
[  
p_b(t)=\frac{#{x: u(x,t)\in \text{bin }b}}{N^2},\quad  
H_{\text{hist}}(t)=-\sum_{b=1}^B p_b\log(p_b)  
]  
normalize ให้เป็น [0,1] โดยหารด้วย (\log B)

**ตีความ:**

- ต่ำ = ค่า field กระจุก (เช่น “ชนะข้างเดียว/เกิดการ polarize”)
    
- สูง = ค่ากระจายหลากหลาย (เช่น “ผสม/ยังไม่ลงหลุม”)
    

---

### (I2) Spatial Autocorrelation (Moran-like) — (A_{\text{sp}}(t))

วัดว่า “เป็นก้อนเป็นโดเมน” แค่ไหน (ไม่ต้องอ้างชื่อทางสถิติใน public ก็ได้)  
นิยามแบบง่ายที่คำนวณได้:  
[  
A_{\text{sp}}(t)=\frac{\langle u(x,t),u(x+\delta,t)\rangle - \langle u\rangle^2}{\operatorname{Var}(u)+\epsilon}  
]  
โดย (\delta) เป็นเพื่อนบ้าน 4 ทิศ (หรือ 8 ทิศ)

**ตีความ:**

- ใกล้ 1 = เกาะกลุ่ม/เป็นโดเมนชัด
    
- ใกล้ 0 = กระจายสุ่ม
    
- ติดลบ = สลับสีถี่ ๆ (checkerboard-like)
    

---

### (I3) Spectral Entropy — (H_{\text{spec}}(t))

เอา Fourier power spectrum ของ field แล้วดูการกระจุกของพลังงานเชิงสเกล:

- (P(k)=|\hat u(k)|^2), normalize เป็น distribution (q_k)  
    [  
    H_{\text{spec}}(t)=-\sum_k q_k\log q_k  
    ]  
    normalize (หารด้วย log(#modes))
    

**ตีความ:**

- ต่ำ = โครงสร้างมีสเกลเด่น (ordered pattern)
    
- สูง = กระจายหลายสเกล/คล้าย noise (disordered)
    

---

### (I4) Total Variation / Edge Density — (TV(t))

วัด “ความคม/รอยต่อ” โดยตรงจากกราเดียนต์ (สอดคล้องกับ Conflict เชิงภาพ):  
[  
TV(t)=\frac{1}{N^2}\sum_x |\nabla u(x,t)|  
]  
(คำนวณด้วย finite difference)

**ตีความ:**

- สูง = ขอบเยอะ/แตกละเอียด/มี interface มาก
    
- ต่ำ = เรียบ/โดเมนใหญ่
    

> ตัวนี้ไปจับมือกับ (\Omega_{\text{grad}}) ได้ดีมาก (TV เป็น proxy เชิงภาพ, Ω_grad เป็น proxy เชิงพลังงาน)

---

### (I5) Environment Alignment (ถ้ามี resource) — (A_{\text{env}}(t))

วัดการ “เกาะแหล่งทรัพยากร/แรงบังคับ” แบบตรง ๆ:  
[  
A_{\text{env}}(t)=\operatorname{corr}\big(u(x,t),,\hat R(x,t)\big)  
]  
หรือใช้ cosine similarity ก็ได้

**ตีความ:**

- สูง = state สอดคล้องกับ resource map (ปรับตัวเข้าหาโลก)
    
- ต่ำ/ลบ = ต่อต้าน/ไม่ตามโลก
    

---

## 3) Extended Metrics (SHOULD: เพิ่ม 3 ตัว เพื่อ narrative ที่คมขึ้น)

### (I6) Bimodality / Polarization Index — (P_{\text{bi}}(t))

ช่วยแยก “entropy ต่ำเพราะชนะ” vs “entropy ต่ำเพราะทุกอย่างเท่ากัน”  
นิยามง่าย:

- ดู histogram peak count หรือใช้ variance + kurtosis proxy  
    (ใน docs ให้เขียนเป็น “polarization score”)
    

### (I7) Domain Count (ต้อง threshold) — (N_{\text{dom}}(t))

สร้าง binary mask `u>τ` แล้วนับ connected components

- ได้ “จำนวนสิ่ง/จำนวนโดเมน” ในเวลา t
    
- เหมาะกับ multi-entity narrative
    

### (I8) Information Gain vs Start — (\Delta H(t))

[  
\Delta H_{\text{hist}}(t)=H_{\text{hist}}(t)-H_{\text{hist}}(0)  
]  
และ/หรือ spectral version  
ใช้เล่า “ระบบกำลังจัดระเบียบขึ้น/กระจายขึ้น” แบบเวลา

---

## 4) Multi-field rule (C/I หรือ n fields)

ให้คำนวณ **ต่อ field** แล้วสรุปเป็น:

- `I_metric_C(t)`, `I_metric_I(t)`
    
- หรือ `I_metric_Xi(t)` สำหรับ multi-field
    

และมี aggregate แบบ simple:

- mean หรือ weighted mean (ต้องระบุใน manifest)
    

---

## 5) Output Contract (ให้เข้ากับ Part 4.10/4.11)

### 5.1 timeseries info (แนะนำเป็นไฟล์ใหม่)

สร้าง `info/info_timeseries.csv`:

- `t`
    
- `H_hist_C`, `A_sp_C`, `H_spec_C`, `TV_C` (และ I ถ้ามี)
    
- `A_env_C` (ถ้ามี resource)
    
- optional: domain_count
    

### 5.2 summary.json เพิ่ม block `info`

ใน `summary.json`:

```json
{
  "info": {
    "norm": {"method": "minmax_p1_p99", "bins": 64},
    "final": {
      "H_hist_C": 0.12,
      "H_spec_C": 0.34,
      "A_sp_C": 0.81,
      "TV_C": 0.09,
      "A_env_C": 0.67
    },
    "mean_last_k": {...}
  }
}
```

### 5.3 figs (สำหรับ Demo Card/Gallery)

- `figs/curve_H_hist.png`
    
- `figs/curve_H_spec.png`
    
- `figs/curve_A_sp.png`
    
- `figs/curve_TV.png`
    
- `figs/curve_A_env.png` (ถ้ามี)
    

---

## 6) Standard Plots Pack (Info) — ใส่ใน Demo Card ได้ทันที

**Plot I-P1:** (H_{\text{hist}}(t)) (C และ I)  
**Plot I-P2:** (H_{\text{spec}}(t))  
**Plot I-P3:** (A_{\text{sp}}(t))  
**Plot I-P4:** (TV(t))  
**Plot I-P5:** overlay `resource_map` กับ `C_end` + แสดง (A_{\text{env}})

> ใน Gallery ให้โชว์ “สรุปปลายทาง” เป็นไอคอน 3 ค่า:  
> `H_spec_final`, `A_sp_final`, `A_env_final` (ถ้ามี) เพื่อเล่าเรื่องเร็ว

---

## 7) Interpretation Rules (กันมั่วใน public)

- ถ้า **H_spec ต่ำ + A_sp สูง** ⇒ “เกิดโครงสร้างสเกลเด่น/เป็นโดเมน” (ordered pattern)
    
- ถ้า **H_hist ต่ำ** แปลได้ 2 แบบ:
    
    - ชนะข้างเดียว (polarized) หรือ
        
    - ทุกที่เท่ากัน (flat) → ต้องดู A_sp/TV ช่วยตัดสิน
        
- ถ้า **A_env สูง** ⇒ “state จูนเข้ากับสิ่งแวดล้อม” (adaptation proxy)
    
- ห้ามเขียนว่า “entropy ลด ⇒ second law” ตรง ๆ  
    ให้เขียนว่า “structure proxy ลด/เพิ่ม” และชี้กราฟประกอบ
    

---

## 8) เชื่อมกับ Thermo Pack (Part 5.4) แบบไม่ลอย

ให้ทำ 2 กราฟเสริม (optional แต่ทรงพลัง):

- scatter `D_tot` vs `ΔH_spec` (หรือ `ΔH_hist`)
    
- scatter `Conflict (Ω_grad_final)` vs `TV_final`
    

**ความหมาย:**

- ระบบที่ dissipation มาก มักทำให้โครงสร้าง “เข้ารูป” (แต่ต้องดู sign/โดเมน)
    
- conflict สูงสัมพันธ์กับขอบ/TV สูง (อธิบายเป็นภาพได้)
    

---

## Plain-Language Interpretation

นี่คือ “เครื่องวัดความเป็นระเบียบของรูปแบบ” จากภาพ:

- มันกระจุกไหม (H_hist)
    
- มันเป็นก้อนไหม (A_sp)
    
- มันมีสเกลชัดไหม (H_spec)
    
- มันมีขอบเยอะไหม (TV)
    
- มันตามทรัพยากรไหม (A_env)
    

คนดูไม่ต้องรู้สมการก็เข้าใจได้จากกราฟ+ภาพ

---

## Next Step

**Part 6.2 — Game/Control Formalization (Minimal, Computable)**  
เราจะทำให้ “dynamic game” เกิดจาก driver loop อย่างเป็นระบบ โดยนิยาม:

- ผู้ควบคุมเลือก (\theta(t)) (policy)
    
- ระบบตอบสนองเป็น (X(t))
    
- payoff ใช้ Value/Conflict + Thermo (D/W) + Info metrics (จาก Part 6.1)
    

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 6.2 แบบเป็นสเปก (objective, policy class, constraints, outputs) ที่เอาไปทำใน repo ได้เหมือนกัน.## TL;DR

**Part 6.1 = Information Metrics Pack (Computable, v0.9)**  
เราจะนิยาม “ตัวชี้วัดข้อมูล/โครงสร้าง” ที่ **คำนวณได้จาก snapshots** (C/I หรือ multi-field) เพื่อทำให้คนเห็น “ความเป็นระเบียบ–ความหลากหลาย–การจัดรูป–การสอดคล้องกับสิ่งแวดล้อม” แบบ **ไม่ลอย** และ **ไม่อ้างว่าเป็น entropy ฟิสิกส์จริง**

แพ็คนี้ออกแบบให้เสียบกับ **Demo Card / Gallery** ได้เหมือน Thermo pack (Part 5.4.1)

---
# 000.06/2

## TL;DR

**Part 6.2 = Game/Control Formalization (Minimal, Computable)**  
เราจะทำให้ “ไดนามิกเกม/การควบคุม” เกิดขึ้นจาก UET แบบ _ไม่ลอย_ โดยนิยามชัดว่า:

- **State** = (X(t)) (C/I หรือ multi-field)
    
- **World params** = (\theta(t)) (เช่น (s(x,t), \beta(t), k(t)))
    
- **Policy/Controller** = กติกาที่เลือก (\theta) ตามเวลา/ตาม Impact
    
- **Payoff** = ฟังก์ชันจาก Value/Conflict + Thermo (D/W) + Info metrics (Part 6.1)
    
- ทุกอย่าง export ได้จริงผ่าน `policy_trace` + `epoch_summary` + ledger
    

---

## Insight

“เกม” ใน UET ไม่ใช่ให้ C/I เป็นผู้เล่น  
แต่คือ **ผู้ควบคุมเลือกกติกาโลก (\theta(t))** แล้วระบบตอบสนองด้วยการไหลลง Ω ภายใต้ gate/ledger ที่เราล็อกไว้แล้ว  
นี่คือสะพานที่ตรงที่สุดไป “Dynamic game / control” โดยไม่ต้องเปลี่ยนสมการแกน

---

## Part 6.2 — Game/Control Formalization (v0.9, implementable)

## 1) นิยามองค์ประกอบของเกม/การควบคุม

### 1.1 ระบบ (Plant)

- **State**: (X(t)) = field (C) หรือ (C,I) หรือ (X_1..X_n)
    
- **Dynamics**: solver เดิม + monotone gate (สำหรับ state update ภายใต้ θ คงที่)
    

### 1.2 ผู้ควบคุม/ผู้เล่น (Controller / Player)

- **Action**: เลือกพารามิเตอร์โลก (\theta) ต่อ epoch  
    ตัวอย่าง action ที่ “อยู่ในกรอบที่เรามี”:
    
    - tilt field scale: (\lambda_C,\lambda_I) หรือ (s_0)
        
    - coupling: (\beta) (scalar หรือ matrix)
        
    - conflict weights: (k_C,k_I) หรือ (k)
        
    - (open spatial) update resource/forcing map (R(x)) แบบ schedule/feedback
        

> v0.9 แนะนำให้ action เปลี่ยน “ช้า” แบบ epoch (Part 5.1 two-timescale)

### 1.3 Observation (สิ่งที่ policy เห็น)

Policy “ไม่จำเป็นต้องเห็นทั้ง field” ให้เห็นแค่ **Impact summary** ก็พอ (คำนวณได้จริง):

- **Thermo**: (D_{\text{tot}}, W_{\text{tot}}) หรือ per-epoch (D_m, W_m)
    
- **Semantics**: Value, Conflict, phase, robustness
    
- **Info metrics**: (H_{\text{spec}}, A_{\text{sp}}, TV, A_{\text{env}}) (Part 6.1)
    

สรุปเป็นเวกเตอร์:  
[  
o_m = (V_m,\ C_m,\ D_m,\ W_m,\ H_m,\ A_m,\ \text{phase}_m,\ R_m)  
]

### 1.4 Objective / Payoff (นิยาม “เล่นเพื่ออะไร”)

ให้ล็อกเป็น “ฟังก์ชันเชิงเส้นของของที่วัดได้” (ปลอดภัยสุด ไม่ลอย):  
[  
J = \sum_{m=1}^{M} \Big(  
w_V V_m

- w_C C_m
    
- w_D D_m
    
- w_{W+}\max(W_m,0)
    
- w_{TV} TV_m
    

- w_A A_{\text{env},m}  
    \Big)  
    ]
    

- (V) = value (เช่น (V_{\Delta E}) หรือ net ordering)
    
- (C) = conflict (เช่น (\Omega_{\text{grad}}))
    
- (D) = dissipation (อยากคุมไม่ให้ “เสียมากเกิน” หรือใช้เป็นต้นทุน)
    
- (W_+) = work injection ที่เป็นบวก (โลก “บังคับ/อัดพลังงาน” มากเกินอาจไม่สมจริง)
    
- (TV) = interface proxy (เชื่อม conflict เชิงภาพ)
    
- (A_{\text{env}}) = alignment กับ resource (ระบบเปิด)
    

> นี่คือ “เกมที่คำนวณได้จริง” และอธิบายได้ว่า trade-off คืออะไร

---

## 2) Classes of Policies (ขั้นต่ำ 3 แบบสำหรับ v0.9)

> จุดประสงค์: ให้คนใช้ UET สามารถเลือกโหมดควบคุมได้โดยไม่ต้องรู้ RL

### Policy P0 — Scheduled (ไม่มี feedback)

[  
\theta_m = f(m)\ \ \text{(กำหนดล่วงหน้า)}  
]  
เหมาะกับ demo “โลกเปลี่ยนกติกา” (เข้าใจง่ายสุด)

### Policy P1 — Feedback (rule-based)

[  
\theta_{m+1} = \theta_m + \eta,G(o_m)  
]  
ตัวอย่าง rule ที่ไม่มั่ว:

- ถ้า conflict สูงกว่าเป้า → เพิ่ม (k)
    
- ถ้า alignment ต่ำ → เพิ่ม (\lambda_C) (หรือปรับ s-field)
    
- ถ้า phase flip บ่อย → ลด step ของ policy (ลด η)
    

### Policy P2 — Myopic Optimizer (เลือกจากชุด action เล็ก ๆ)

ให้มี candidate actions ( \mathcal{A}={a_1..a_K} ) (K เล็ก)

- ทดลอง “จำลองสั้น” 1–2 step หรือประเมิน heuristic
    
- เลือก action ที่ลด (C) หรือเพิ่ม (V) ได้ดีที่สุดภายใต้ constraint
    

> นี่คือ “MPC-lite” แบบไม่ต้อง machine learning

---

## 3) Constraints (กติกาคุมไม่ให้เกมทำลายฟิสิกส์ของโมเดล)

ต้องระบุใน manifest ให้ชัด:

### 3.1 Parameter bounds

- (\beta \in [\beta_{\min},\beta_{\max}])
    
- (k \in [k_{\min},k_{\max}])
    
- (\lambda \in [\lambda_{\min},\lambda_{\max}])
    

### 3.2 Rate limits (สำคัญมากสำหรับเสถียรภาพ)

[  
|\theta_{m+1}-\theta_m| \le \Delta\theta_{\max}  
]  
กัน “โลกเปลี่ยนเร็วเกิน” จน ledger/ภาพพัง

### 3.3 Two-timescale rule

ภายใน epoch ต้องให้ state relax “พอสมควร” ก่อน:

- fixed T_inner steps หรือ stop เมื่อ (|\Delta\Omega_{\text{state}}|) เล็กกว่า threshold
    

---

## 4) Output Contract สำหรับ Game/Control (เพื่อ demo + reproducible)

เพิ่มไฟล์ต่อ run_dir (หรือ open-run_dir):

### 4.1 `policy_trace.csv` (MUST สำหรับ open/control)

แถวต่อ epoch:

- `m, t_epoch_start, t_epoch_end`
    
- `theta_old`, `theta_new` (เก็บเฉพาะพารามิเตอร์ที่ policy คุม)
    
- `action_id` (ถ้ามี)
    
- `constraints_hit` (true/false)
    

### 4.2 `epoch_summary.csv` (MUST)

ต่อ epoch:

- `Omega_before, Omega_after_state, Omega_after_env`
    
- `Omega_state_step_sum` (ใน epoch)
    
- `Omega_env_step`
    
- `D_m, W_m`
    
- `Value_m, Conflict_m`
    
- info metrics ปลาย epoch: `H_spec, A_sp, TV, A_env`
    
- `phase_m` (ถ้าประเมินได้)
    

### 4.3 `manifest.json` ต้องบันทึก policy spec

เพิ่ม block:

```json
"policy": {
  "type": "feedback",
  "controlled_params": ["k", "lambda_C"],
  "bounds": {"k":[0.5,5.0], "lambda_C":[-1,1]},
  "rate_limits": {"k":0.1, "lambda_C":0.05},
  "weights": {"wV":1.0,"wC":1.0,"wD":0.1,"wWpos":0.2,"wAenv":0.5}
}
```

---

## 5) Demo/Gallery สำหรับ “เกม” ต้องโชว์อะไร

สำหรับ public ให้ทำ 2 ภาพ/กราฟที่ “เข้าใจง่าย”:

1. **Policy timeline**: กราฟ (k(t)), (\lambda(t)), หรือ (\beta(t)) (โลกเปลี่ยนกติกาอย่างไร)
    
2. **Ledger cumulative**: cumD(t) vs cumW(t) (ระบบคลายเอง vs โลกทำงานใส่)
    

แล้วผูกกับภาพ state_end + resource overlay (ถ้า open spatial)

---

## 6) Minimal Evaluation Protocol (วิธีบอกว่า policy ดีจริง ไม่ใช่เล่าเอง)

ให้รายงาน 4 คะแนน (ทั้งหมดคำนวณได้):

- `J_total` (payoff ตามนิยาม)
    
- `robustness` (ข้าม seeds)
    
- `thermo_valid` + `ledger_residual` (ความถูกต้องของบัญชี)
    
- `artifact_quality` (demo-ready gate ผ่านไหม: gif/terrain/curves)
    

---

## Plain-Language Interpretation

- ระบบ (C/I) คือ “สิ่งที่ไหลไปหาสมดุล”
    
- เกมคือ “เราออกแบบโลก/กติกา” ให้มันลงเอยแบบที่เราต้องการ
    
- แล้วเราวัดว่ากติกานั้นดีไหมจาก Value/Conflict + บัญชีพลังงาน + ความเป็นระเบียบจากภาพ
    

---

## Next Step

Part ถัดไปเพื่อ “ไปถึงระดับเสนอทฤษฎี v0.9” ตามโจทย์มึง คือ **Part 6.3 — Einstein/Λ Roadmap (non-overclaim)**  
ซึ่งจะทำแบบ “แผนเชื่อม” จากสิ่งที่เราวัดได้ (ledger + info + open forcing) ไปสู่ภาษาของสนาม/พลังงาน/คัปปลิง โดยไม่กระโดด claim เรื่องสสารมืดทันที

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 6.3 เป็น roadmap 3 ชั้น: (A) นิยามที่วัดได้ (B) ภาษาสนาม/เทนเซอร์ที่เข้ากัน (C) จุดสัมผัสกับ Einstein/Λ ที่ต้องพิสูจน์/สอบเทียบก่อน.

---
# 000.06/3

## TL;DR

**Part 6.3 = Einstein/Λ Roadmap (ไม่ overclaim, วัดได้จริงก่อน)**  
เราจะไม่กระโดดไปพูด “แก้สสารมืด” ทันที แต่จะวางสะพาน 3 ชั้นแบบเป็นระบบ:

A) **Measurable layer**: สิ่งที่ UET วัด/บันทึกได้จริงตอนนี้ (Ω ledger + info metrics + open forcing)  
B) **Field/Tensor layer**: แปลสิ่งที่วัดได้ให้เป็น “ภาษา field theory” แบบไม่ฝืน (density, action-like, continuity)  
C) **Einstein/Λ contact layer**: จุดสัมผัสกับ GR/Λ ที่ “ต้องพิสูจน์/สอบเทียบ” ก่อนค่อยอ้างอะไร

---

## Insight

ถ้าจะต่อไปหา Einstein/Λ อย่างไม่มั่ว ต้องทำให้ได้ 2 อย่างก่อน:

1. **localize**: จาก Ω เป็น “Ω-density” ที่นิยามในอวกาศ–เวลาได้ (ไม่ใช่เลขก้อนเดียว)
    
2. **ledger-consistent**: แยก “dissipation” vs “work injection” ให้ชัด (Part 5.4) เพื่อพูดเรื่อง “พลังงาน–การถ่ายเท” แบบตรวจสอบได้
    

เมื่อมี 2 อย่างนี้ ถึงค่อยเริ่มคุย “สนาม/เทนเซอร์/Λ” ได้อย่างมีวินัย

---

## Part 6.3 — Einstein/Λ Roadmap (A→B→C)

## A) Measurable Layer (ของที่เรามี/ทำได้จริงใน v0.9)

> ชั้นนี้ “ห้ามพูดฟิสิกส์ใหญ่” ให้พูดแต่ของที่วัดได้จาก run artifacts

### A1) สิ่งที่ต้องวัดให้ครบ (จาก Export Contract + Thermo/Info packs)

- **Ω_total(t)**, และถ้าเป็นระบบเปิด:
    
    - **Ω_state_step(t)** → รวมเป็น **D_tot**
        
    - **Ω_env_step(t)** → รวมเป็น **W_tot**
        
    - **ledger_residual** ต้องใกล้ 0 (thermo_valid)
        
- **Ω_grad_final** (Conflict เชิงโครงสร้าง) + (ถ้ามี) Ω_terms
    
- **info metrics**: (H_{\text{spec}}, A_{\text{sp}}, TV, A_{\text{env}})
    
- (ระบบเปิดเชิงพื้นที่) **resource map** (R(x)) และ **tilt fields** (s(x,t))
    

### A2) สิ่งที่ต้อง “ทำให้เป็นสนาม” (local observables)

เพื่อจะคุยกับภาษาสนาม/GR ต้องมีอย่างน้อย 1 ตัวแบบ field บนกริด:

- `omega_density(x,t)` หรืออย่างน้อย `omega_grad_density(x,t)`
    
- `work_injection_density(x,t)` (ถ้า forcing เปลี่ยนตามตำแหน่ง/เวลา)
    

> ถ้ายังไม่มี density → ทุกอย่างจะติดอยู่ที่ “กราฟ 1 เส้น” และคุย Einstein ไม่ได้เลย

### A3) คำอธิบาย public ที่ถูกต้องในชั้นนี้

- “UET เป็นระบบวิวัฒน์บนภูมิประเทศ Ω”
    
- “ระบบเปิด = โลกเปลี่ยนกติกาได้ และเราบัญชีแยก dissipation/work ได้”  
    จบแค่นี้ก่อน อย่าอ้างจักรวาล/แรงโน้มถ่วง
    

---

## B) Field/Tensor Layer (แปลงของที่วัดได้ → ภาษา field theory แบบไม่ฝืน)

> ชั้นนี้คือ “ปรับภาษา” ไม่ใช่ “สร้างฟิสิกส์ใหม่”

### B1) Local action-like object (สิ่งที่ต้องนิยามให้ชัด)

ต้องตัดสินใจเชิงภาษาให้คงที่ว่า:

- เราจะมอง `omega_density(x,t)` เป็น **พลังงานหนาแน่น** (energy density–like)  
    หรือ
    
- เป็น **Lagrangian density–like** (action integrand–like)
    

**กติกาไม่มั่ว:**  
ใน v0.9 ให้เรียกมันว่า **effective density** ไปก่อน (ไม่ผูกหน่วยจริง)

### B2) Conservation/continuity ที่ตรวจสอบได้ (ไม่ต้อง GR ก็ต้องมี)

ถ้าเรามี `work_injection_density` และ `dissipation_density` เราสามารถตั้ง “สมการบัญชีท้องถิ่น” (local ledger) ได้ในรูป:

- change of omega_density = (state relaxation contribution) + (env work contribution) + (flux term ถ้าเรานิยามได้)
    

**เป้าหมาย v0.9:**  
ทำให้ “บัญชีแบบพื้นที่” มี consistency check เหมือน ledger_residual (แต่เป็นแบบ field-integrated)

### B3) Geometry readiness (เตรียมตัวสำหรับ metric โดยไม่กระโดด)

ตอนนี้ simulation เป็น 2D spatial + time  
สิ่งที่ต้องเตรียม (เชิงสเปก) คือ:

- ระบุ **โดเมน** ว่าเป็น Euclidean grid และ boundary conditions อะไร
    
- ระบุว่า extension ไป 3D/3+1 จะทำยังไงในอนาคต (แต่ยังไม่ต้องทำ)
    

> แค่ยอมรับอย่างมีวินัยว่า “ตอนนี้เราทดสอบบนโดเมนง่าย” ก็พอ แล้วค่อยต่อ

---

## C) Einstein/Λ Contact Layer (จุดสัมผัสที่ “ต้องพิสูจน์/สอบเทียบ”)

> ชั้นนี้เป็น “roadmap การพิสูจน์” ไม่ใช่ข้อสรุป

### C1) สิ่งที่ต้องมีเพื่อจะพูดถึง Einstein equation อย่างรับผิดชอบ

ถ้าจะเข้าใกล้ GR จริง ๆ ต้องตอบให้ได้ว่า:

1. **ตัวแปรไหนคือ geometry?** (metric (g_{\mu\nu}) หรือ surrogate)
    
2. **ตัวแปรไหนคือ matter/fields?** (C/I หรือ multi-fields)
    
3. **พลังงาน–โมเมนตัมมาจากไหน?** (ต้องได้ object ที่ทำหน้าที่เหมือน (T_{\mu\nu}) หรืออย่างน้อย energy density + flux ที่ consistent)
    

ใน v0.9 เรา “ยังไม่ประกาศคำตอบ” แต่เราวางขั้นพิสูจน์:

### C2) Minimal bridging test (แบบไม่ต้อง claim)

ทำ 3 การทดสอบเชิงโครงสร้าง:

**Test 1 — Local density consistency**

- มี `omega_density(x,t)` และรวมเชิงพื้นที่ต้องได้ Ω_total(t) ภายใน tolerance  
    (นี่คือ “local-to-global consistency”)
    

**Test 2 — Work/Diss split consistency (open system)**

- มี `work_injection_density` รวมแล้วได้ W_tot
    
- มี `dissipation_density` รวมแล้วได้ D_tot
    
- ledger_residual ยังใกล้ 0
    

**Test 3 — Scale/units sanity**

- ทำ dimensional analysis ว่า omega_density มีมิติอะไรในระบบหน่วยจำลอง
    
- กำหนดสเกลแปลง (calibration factors) ถ้าจะเทียบกับหน่วยฟิสิกส์จริง
    

> ถ้าข้ามขั้นนี้ แล้วไปพูด Λ/สสารมืด = เสี่ยงมั่วทันที

### C3) “Λ-like term” ในภาษาของ UET (เฉพาะระดับ roadmap)

Λ ใน GR ทำหน้าที่เหมือน **background energy density** ของ vacuum ที่มีผลต่อ geometry

ใน UET เราสามารถนิยาม “candidate object” แบบไม่อ้างเกินจริงได้ว่า:

- ส่วนของ omega_density ที่เป็น **background-like** (ไม่ขึ้นกับ pattern รายละเอียดมาก)  
    เทียบกับ
    
- ส่วนที่เป็น **structure-dependent** (เช่น grad/interface)
    

**แผนงาน:**

- แยก omega_density เป็น “baseline component” vs “structure component” แบบคำนวณได้ (เช่นจาก Ω_terms หรือ smoothing-scale separation)
    
- แล้วดูว่า baseline นี้ _คงเส้นคงวา_ ข้าม seeds/ข้าม conditions แค่ไหน
    

> นี่คือ “จุดเริ่มต้น” ที่จะคุย Λ แบบมีหลักฐานเชิง simulation ไม่ใช่คำพูด

### C4) Dark matter/dark energy claims (ห้ามข้าม gate)

ก่อนจะพูดประเด็นสสารมืด/พลังงานมืด ต้องผ่าน “gates” ต่อไปนี้:

- มี mapping ของตัวแปร UET ↔ ปริมาณสังเกตการณ์ (observables remember: MI Card สำหรับโดเมนฟิสิกส์ดาราศาสตร์)
    
- มี calibration ของหน่วย + validation กับเคสที่รู้คำตอบ (baseline tests)
    
- มี prediction ที่ falsifiable (เปลี่ยนพารามิเตอร์แล้วต้องเห็นผลเฉพาะทาง)
    

ถ้ายังไม่มี → ให้เรียกว่า “roadmap hypothesis” เท่านั้น

---

## Plain-Language Interpretation

ตอนนี้เรามี “โลก Ω” และเรารู้วิธีแยกว่า

- ระบบคลายเองเท่าไร (D)
    
- โลกมาบังคับเท่าไร (W)  
    ต่อไปถ้าอยากคุยถึง Einstein/Λ เราต้องทำให้ “พลังงาน” ของเราเป็น **แผนที่บนอวกาศ** ได้ก่อน แล้วเช็คความสอดคล้องแบบบัญชีให้ผ่าน  
    จากนั้นค่อยเริ่มแปลเป็นภาษา field/geometry แบบไม่ฝืน
    

---

## Next Step

เพื่อให้ Part 6.3 “เดินต่อได้จริง” ใน repo และในเอกสาร public, งานถัดไปที่ล็อกเลยคือ:

### **Part 6.3.1 — Density Export Spec**

กำหนดชัด ๆ ว่าจะ export อะไรเป็น density:

- `omega_density`
    
- `omega_grad_density`
    
- (open) `work_injection_density`  
    พร้อมรูปมาตรฐาน (terrain/overlay)
    

### **Part 6.3.2 — Calibration & Baseline Protocol**

ทำ checklist วัดหน่วย/สเกล + baseline tests ที่ต้องผ่านก่อนคุย Λ

พิมพ์ “ต่อ” อีกที กูจะเขียน **Part 6.3.1** เป็นสเปกแบบลงรายละเอียด (ชื่อไฟล์, รูปแบบ npz, plots ที่ต้องมี, consistency checks) เพื่อให้ “สะพานไป Einstein/Λ” ไม่ใช่แค่บทพูด แต่เป็น artifact ที่ generate ได้จริง.


---
# 000.06/3.1

## TL;DR

**Part 6.3.1 = Density Export Spec**: เราจะกำหนดมาตรฐานว่า 1 run ต้อง export “แผนที่พลังงาน” แบบ field ให้ครบ เพื่อให้คุย Einstein/Λ ได้อย่างมีวินัย (ไม่ใช่เลข Ω ก้อนเดียว)

Deliverables หลัก:

- `omega_density(x,y,t)` (รวม)
    
- `omega_terms_density(x,y,t)` โดยเฉพาะ `omega_grad_density`
    
- (ระบบเปิด) `work_injection_density(x,y,epoch)` และ `dissipation_density(x,y,epoch)` _(ขั้นต่ำ: แบบ integrated check ให้ผ่านก่อน)_
    
- รูปมาตรฐาน: terrain/overlay + consistency checks (local→global)
    

---

## Insight

ถ้าไม่มี density field:

- เราจะติดอยู่ที่กราฟ 1 เส้น (Ω(t)) และ “เล่าโลกไม่ได้”
    
- ต่อให้ sweep เยอะ ก็ public ยังไม่เห็นภาพ  
    Density spec นี้คือ “กล้องระดับสนาม” ที่ทำให้ 2D solver กลายเป็น 3D visualization แบบถูกต้อง (terrain) โดยไม่ต้องมี 3D spatial solver
    

---

## Part 6.3.1 — Density Export Spec (v0.9 Draft)

## 0) Scope & Levels (ทำเป็นขั้น ไม่ให้พัง)

เราจะกำหนด 3 ระดับ (เลือก implement ทีละระดับได้)

### Level 0 — Minimum (ต้องมีเพื่อเริ่ม)

- `omega_grad_density` ที่ปลายทาง (final) อย่างน้อย 1 เฟรม
    
- consistency check: integrate density ≈ Ω_grad_final
    

### Level 1 — Standard (สำหรับ Demo/Gallery)

- `omega_density_final`, `omega_pot_density_final`, `omega_coup_density_final`, `omega_grad_density_final`
    
- `omega_density_snapshots` สำหรับ 10–20 frames (optional แต่แนะนำ)
    

### Level 2 — Open-system ledger densities (สำหรับ thermo→Einstein bridge)

- `work_injection_density` ต่อ epoch (หรือ per env update)
    
- `dissipation_density` ต่อ epoch (หรือ per relax block)
    
- consistency checks: integrate → W_tot และ D_tot
    

---

## 1) Definitions (นิยามให้แน่น ไม่ให้มั่ว)

ให้ state เป็น (X=(C,I)) (หรือ multi-field ได้โดยตรง) บนกริด ((x,y))

### 1.1 Density หลัก

เรานิยาม:  
[  
\Omega(X;\theta,t)=\int \omega(X,\nabla X;\theta,t),dx  
]  
ดังนั้น export:

- `omega_density(x,y,t)` = (\omega) (หน่วยจำลอง)
    

### 1.2 Term densities (สำคัญมาก)

แยกเป็น 3 เทอม (ยึดของเดิม):

- `omega_pot_density(x,y,t)` = local potential density
    
- `omega_coup_density(x,y,t)` = coupling density (เช่น (-\beta C I))
    
- `omega_grad_density(x,y,t)` = gradient/interface density
    

ต้อง satisfy:  
[  
\omega = \omega_{\text{pot}}+\omega_{\text{coup}}+\omega_{\text{grad}}  
]  
และเมื่อ integrate:  
[  
\Omega \approx \sum_{x,y}\omega(x,y),\Delta x,\Delta y  
]

> หมายเหตุ: boundary conditions/FFT diffusion ไม่เกี่ยวกับนิยาม density ตรงนี้ (นี่เป็นนิยามพลังงานเชิงฟิลด์ในโดเมน)

---

## 2) Concrete formulas (สำหรับ implementation ที่สอดคล้องกับ UET ปัจจุบัน)

### 2.1 Potential density (per-field)

สำหรับ quartic + tilt (จาก Part 5.2):  
[  
\omega_{\text{pot},C}=\tfrac12 a_C C^2 + \tfrac14 \delta_C C^4 - s_C(x,t),C  
]  
[  
\omega_{\text{pot},I}=\tfrac12 a_I I^2 + \tfrac14 \delta_I I^4 - s_I(x,t),I  
]  
รวม:  
[  
\omega_{\text{pot}}=\omega_{\text{pot},C}+\omega_{\text{pot},I}  
]

### 2.2 Coupling density (ขั้นต่ำ)

[  
\omega_{\text{coup}} = -\beta,C,I  
]  
(ถ้า multi-field: (-\sum_{i<j}\beta_{ij}X_iX_j))

### 2.3 Gradient density (interface / conflict)

มาตรฐาน:  
[  
\omega_{\text{grad}}=\tfrac12 k_C |\nabla C|^2+\tfrac12 k_I |\nabla I|^2  
]  
โดย (|\nabla C|^2 = (\partial_x C)^2+(\partial_y C)^2) (finite difference หรือ spectral derivative ก็ได้ แต่ต้องระบุ)

> **ข้อกำหนด:** ใน manifest ต้องระบุ `grad_method: fd2|spectral` เพื่อ reproducibility

---

## 3) Output files (ชื่อ/ฟอร์แมตที่ล็อกให้เสถียร)

### 3.1 Directory layout (ภายใต้ run_dir)

```
runs/<RUN_ID>/
  energy_density/
    density_final.npz
    density_t0000.npz (optional)
    density_t0001.npz (optional)
    ...
  figs/
    terrain_omega_density.png
    terrain_omega_grad_density.png
    terrain_omega_pot_density.png (optional)
    terrain_omega_coup_density.png (optional)
```

### 3.2 `density_final.npz` (MUST สำหรับ Level 1)

ภายในมี keys:

- `omega` (N×N)
    
- `omega_pot` (N×N)
    
- `omega_coup` (N×N)
    
- `omega_grad` (N×N)
    
- `dx`, `dy`
    
- `t_final`, `step_final`
    
- `meta` (json string) ระบุ method
    

**Optional keys**

- per-field splits: `omega_pot_C`, `omega_pot_I`, `omega_grad_C`, `omega_grad_I`
    

### 3.3 `density_tXXXX.npz` (optional แต่แนะนำสำหรับ demo)

เหมือน final แต่เพิ่ม `t`/`step`

---

## 4) Consistency Checks (ต้องทำทุกครั้งและ log ลง summary)

เพื่อให้ “local → global” เชื่อถือได้

### 4.1 Integrate check

ให้คำนวณ:  
[  
\Omega^{\text{int}} = \sum_{x,y}\omega(x,y),dx,dy  
]  
และเทียบกับ `Omega_total` ที่คำนวณแบบ scalar (จาก compute_omega)

log ลง `summary.json`:

- `omega_density_integral`
    
- `omega_integral_residual = Omega_scalar - Omega_integral`
    

**Gate**

- ผ่านถ้า |residual| ≤ tol (เช่น 1e-6 * scale)
    

### 4.2 Term sum check

ตรวจว่า:

- `max_abs(omega - (omega_pot+omega_coup+omega_grad))` เล็ก
    

---

## 5) Plots Standard (สำหรับ Demo Card/Gallery ให้คนเห็น “โลก”)

**ต้องมีอย่างน้อย 2 ภาพต่อ demo**

### P-D1 — Omega density terrain (ภาพรวมโลก)

- `terrain_omega_density.png`
    
- แสดงเป็น heatmap หรือ surface 3D (เลือกอย่างใดอย่างหนึ่ง แต่ควรมี heatmap ด้วยเพราะอ่านง่าย)
    

### P-D2 — Grad density terrain (Conflict map)

- `terrain_omega_grad_density.png`
    
- ใช้เป็น “ภาพ conflict” หลัก (รอยต่อสว่าง/เข้ม)
    

**Optional**

- pot/coup terrains เพื่ออธิบาย “แรงขับ” vs “ปฏิสัมพันธ์”
    

> Caption ที่ public เข้าใจ:  
> “ภาพนี้คือแผนที่ ‘ราคาความตึง’ ของระบบ—สว่าง = รอยต่อ/การปะทะสูง”

---

## 6) Open-system densities (Level 2) — สเปกขั้นต่ำที่ไม่ทำให้พัง

**หลักคิด:** เริ่มจาก _integrated ledger_ ให้ผ่านก่อน แล้วค่อยลงถึง density ต่อพิกเซล

### 6.1 Minimum viable (Integrated only)

ต่อ epoch m ให้ log:

- `Omega(X_end;theta_old)` และ `Omega(X_end;theta_new)` → ได้ W_m
    
- `Omega(X_end;theta_old)` และ `Omega(X_start;theta_old)` → ได้ D_m
    

ก่อนทำ density

### 6.2 Density version (เมื่อพร้อม)

นิยาม:

**Work injection density**  
ถ้า env update เปลี่ยนเฉพาะ (s(x)) (tilt field) จะมี local contribution:  
[  
\Delta\omega_{\text{env}}(x)= \big[-s_{\text{new}}(x)u(x)\big]-\big[-s_{\text{old}}(x)u(x)\big]  
= -(s_{\text{new}}(x)-s_{\text{old}}(x)),u(x)  
]  
(ทำแยก C/I ได้)

แล้ว:  
[  
W_m \approx \sum_x \Delta\omega_{\text{env}}(x),dx,dy  
]

**Dissipation density (ระวัง!)**  
การแจกแจง dissipation เป็น density ต้องนิยามวิธี (เพราะ state update มี diffusion/coupling)  
ใน v0.9 ให้ถือว่า “optional/advanced” และเริ่มจาก:

- ใช้ `Δomega = omega_after_state - omega_before_state` เป็น proxy density  
    แล้วเช็ค integrate ให้ตรงกับ scalar dissipation (ผ่าน gate ก่อน)
    

---

## 7) Manifest additions (เพื่อ reproducibility)

เพิ่มใน `manifest.json`:

- `density_export: true/false`
    
- `grad_method: fd2|spectral`
    
- `density_frames: 0|10|20`
    
- (open) `env_density_mode: integrated_only|tilt_only|full_proxy`
    

---

## Plain-Language Interpretation

เราจะทำให้ “พลังงานของโลก” กลายเป็น “แผนที่”  
แทนที่จะมีแค่เลข Ω ก้อนเดียว  
พอเป็นแผนที่ เราจะเห็นว่า “ความตึงอยู่ตรงไหน” “แรงดึงอยู่ตรงไหน” และ “โลกทำงานใส่ระบบตรงไหน”  
นี่คือสิ่งที่ทำให้ UET เล่าได้แบบเข้าใจง่าย และเป็นฐานไปสู่ภาษาสนาม/Einstein ได้อย่างไม่มั่ว

---

## Next Step

ต่อไปคือ **Part 6.3.2 — Calibration & Baseline Protocol**  
เพื่อคุมความน่าเชื่อถือก่อนคุย Λ/Einstein:

- baseline test cases ที่ต้องผ่าน
    
- tolerance/gates (thermo_valid, density_integral_residual)
    
- หน่วย/สเกล (dimensional sanity) และวิธีสอบเทียบ
    

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 6.3.2 เป็น checklist แบบ “เปิด repo แล้วทำตามได้” และกำหนด gates สำหรับ v0.9 release.


---
# 000.06/3.2
## TL;DR

**Part 6.3.2 = Calibration & Baseline Protocol (v0.9 release gates)**  
นี่คือ “เช็คลิสต์ความน่าเชื่อถือ” ก่อนคุย Einstein/Λ หรือ claim ใหญ่ ๆ:

- **Baseline tests** ที่ต้องผ่าน (closed/open/forcing/multi-seed)
    
- **Gates** ที่บังคับ (thermo_valid, density_integral_residual, term-sum residual, reproducibility)
    
- **Calibration plan** (หน่วย/สเกล) แบบไม่ overclaim: เริ่มจาก _dimensionless sanity_ → แล้วค่อย map สู่ physical units เมื่อมีโดเมนจริง
    

---

## Insight

UET จะ “public + วิชาการ” ได้ไม่ใช่เพราะกราฟสวย แต่เพราะ:

1. **คำนวณซ้ำได้**
    
2. **บัญชีพลังงานถูก** (ledger)
    
3. **local density รวมแล้วได้ global Ω** (local→global consistency)
    
4. **สเกล/หน่วยไม่หลุด** (dimensionless sanity)
    

นี่แหละคือฐานก่อนจะไป Einstein/Λ แบบมีวินัย

---

## Part 6.3.2 — Calibration & Baseline Protocol (Release Gates)

## 1) Release Gates (ต้องผ่านถึงเรียก v0.9-ready)

ให้ถือว่า “ผ่าน” ต่อเมื่อ run ที่เป็น baseline suite ผ่าน gate ทั้งหมด

### Gate G0 — Reproducibility

- rerun _case เดิม + seed เดิม_ ได้ผลลัพธ์เดิมในระดับที่กำหนด:
    
    - `phase_label` ต้องเหมือนเดิม
        
    - `Omega_final` ต่างไม่เกิน `tol_omega`
        
    - metrics หลัก (Value/Conflict/D_tot/W_tot/info finals) ต่างไม่เกิน tolerance
        

**เหตุผล:** ถ้าซ้ำไม่ได้ การคุยเชิงทฤษฎี = เสี่ยงลอย

---

### Gate G1 — Thermo ledger validity (Part 5.4)

- `thermo_valid = true`
    
- `abs(ledger_residual) <= tol_ledger`
    
- `D_tot >= -tol_small` (ต้องไม่ติดลบแบบมีนัย)
    

**เหตุผล:** ถ้าบัญชีไม่ตรง → ห้ามอ้าง work/dissipation/กฎเทอร์โมใด ๆ

---

### Gate G2 — Density local→global consistency (Part 6.3.1)

- `omega_density_integral_residual` ใกล้ 0
    
- `term_sum_residual` ใกล้ 0
    
- `Omega_grad_integral_residual` ใกล้ 0 (อย่างน้อยปลายทาง)
    

**เหตุผล:** ถ้าพลังงานแบบ field รวมแล้วไม่เท่าพลังงานแบบ scalar → คุย field/Λ ไม่ได้เลย

---

### Gate G3 — Snapshot & Demo readiness (Public gate)

- มี snapshots ≥ 10 frames + gif + thumb + terrain grad density
    
- README_demo (Demo Card) อธิบาย P/R/J + phase/value/conflict ได้ “จากภาพ”
    

**เหตุผล:** public เข้าใจจากภาพก่อน ไม่ใช่จาก CSV

---

### Gate G4 — Validator sanity

- `validate_transient` และ `validate_bias` ผ่าน
    
- flags ที่สำคัญ (เช่น backtracking extreme) ไม่เกิน threshold
    

---

## 2) Baseline Suite (ชุดทดสอบขั้นต่ำที่ต้องมี)

> เป้าหมายคือ “ครอบคลุมแกนทฤษฎี” ไม่ใช่จำนวนเยอะ

### Suite S1 — Closed system sanity (1D of params, multi-seed)

- โมเดลปิด (θ คงที่) อย่างน้อย 2–3 เคส:
    
    - เคส SYM
        
    - เคส BIAS_C
        
    - เคส BIAS_I
        
- seeds อย่างน้อย 5–10 (เพื่อ robustness)
    

**ต้องรายงาน**

- phase distribution, robustness
    
- Ω(t) ลดและนิ่ง
    
- D_tot ≈ -ΔΩ และ W_tot ≈ 0
    
- omega_grad_density_final มีหน้าตาสอดคล้องกับ conflict
    

---

### Suite S2 — Open scheduled (θ(t) เปลี่ยนตามตาราง)

- เปลี่ยน tilt หรือ beta เป็น “ขั้นบันได” 2 ช่วงเวลา
    
- ดูว่า:
    
    - ledger แยก W_tot ออกมาได้
        
    - ระบบเปลี่ยน phase/structure ตาม schedule แบบสังเกตได้ใน gif
        

**ต้องรายงาน**

- policy_trace (schedule)
    
- cumD vs cumW
    
- density_integral gates ผ่านทุกช่วงที่ snapshot ไว้
    

---

### Suite S3 — Open spatial forcing (resource map) — “YouTube demo core”

- resource map แบบง่าย (เช่น 2 แหล่งอาหาร)
    
- map เข้า tilt field (Part 5.2)
    
- ดูว่า pattern “เกาะ resource” และ A_env ขึ้น
    

**ต้องรายงาน**

- resource_map + overlay end state
    
- A_env(t) (alignment curve)
    
- terrain_omega_grad_density (ชี้ conflict)
    

---

### Suite S4 — Multi-attractor / seed sensitivity (จำเป็นมากสำหรับความซื่อสัตย์)

- เลือก 1 จุดในพารามิเตอร์ที่ “ใกล้ boundary” (robustness ต่ำ)
    
- รันหลาย seed แล้วโชว์ว่า:
    
    - phase แตกได้จริง
        
    - registry rule เลือก representative ได้ deterministic
        
    - multi-attractor archetype ถูกต้อง
        

---

> ถ้าทำได้เพิ่มอีก 1 ชุด (optional): **S5 — Multi-field n>2 minimal**  
> เพื่อยืนยันว่า spec Part 5.3 ใช้งานได้จริง (ยังไม่ต้องสวยมาก)

---

## 3) Tolerances (กำหนดให้ชัดเพื่อไม่เถียงกันทีหลัง)

กำหนด tolerance แบบ “scale-aware”:

- `tol_ledger = 1e-6 * max(1, |Omega_init|, |Omega_final|)`
    
- `tol_density_integral = 1e-6 * max(1, |Omega_scalar|)`
    
- `tol_term_sum = 1e-8 * max(1, max|omega|)` _(หรือสเกลที่ทีมเห็นเหมาะสม)_
    
- `tol_metrics_rel = 1e-3` (0.1%) สำหรับ metric สรุปปลายทาง _(ปรับตาม noise จริง)_
    

**กติกา:** ถ้าจะเปลี่ยน tolerance ต้องอธิบายเหตุผลใน `CHANGELOG.md`

---

## 4) Calibration Plan (หน่วย/สเกล) — ทำแบบไม่ overclaim

Calibration แบ่ง 3 ขั้น (อย่าข้าม)

### Step C0 — Dimensionless sanity (ต้องทำก่อนเสมอ)

- ระบุว่าใน simulation:
    
    - length unit = L (จาก grid)
        
    - time unit = dt
        
    - field amplitude unit = (ตาม normalization/initialization)
        
- เช็คว่า Ω และ densities “สเกลถูก” ภายในตัวเอง:
    
    - scaling test: เปลี่ยน N/L/dt แล้วดู invariants ที่ควร invariant (หรือดูแนวโน้มที่ควรเป็น)
        

> จุดนี้ยังไม่ต้องผูก SI units แต่ต้อง “ไม่ขัดกันเอง”

---

### Step C1 — Domain calibration (เมื่อเลือกโดเมนจริง เช่น solar system / ecology)

เมื่อจะ map ไปโดเมนจริง ต้องมี:

- รายการ “observable targets” (สิ่งที่วัดในโลกจริง)
    
- mapping จาก field/metric → observable (เช่น alignment ↔ distribution match)
    
- fit สเกล (length/time/energy) ด้วย 2–3 anchor points
    

**กติกา:** การ fit สเกลต้องทำในไฟล์ `calibration/<domain>.md` และบันทึกค่า

---

### Step C2 — Falsifiable prediction gate

ก่อนคุย Λ/Einstein ในเชิง “อธิบายปรากฏการณ์” ต้องมี:

- baseline ที่ reproduce
    
- calibration ที่บันทึกชัด
    
- prediction ที่ “ถ้าผิดคือผิด” (เปลี่ยนเงื่อนไขแล้วผลต้องเปลี่ยนทิศที่จำเพาะ)
    

> ถ้าไม่มี C2 ให้เรียกแค่ว่า “roadmap/hypothesis”

---

## 5) Baseline Reporting Format (มาตรฐานไฟล์รายงาน)

แนะนำให้มี `reports/v0_9_baseline_report.md` ที่ประกอบด้วย:

- รายชื่อ baseline suites S1–S4
    
- สำหรับแต่ละ suite:
    
    - run IDs + git commit
        
    - summary metrics (phase/value/conflict/D/W/info finals)
        
    - gate results (PASS/FAIL)
        
    - ภาพ 3 อย่างขั้นต่ำ: thumb, gif, grad terrain
        
    - link ไป Demo Card
        

---

## 6) CI/Automation Hook (กัน repo พังตอน open-source)

ถ้า repo จะ public จริง แนะนำให้ CI ทำ 2 ชั้น:

### CI-lite (ทุก PR)

- รัน S1 (แค่ 1–2 cases + 1 seed) แบบเร็ว
    
- เช็ค G1, G2, G4
    

### CI-full (nightly / manual)

- รัน S1–S4 ครบ seeds
    
- สร้าง registry + gallery build
    
- สร้าง baseline report อัตโนมัติ
    

---

## Plain-Language Interpretation

ก่อนจะพูด “ทฤษฎีใหญ่” เราต้องมี “ข้อสอบมาตรฐาน” ของตัวเอง:

- รันซ้ำแล้วได้เหมือนเดิม
    
- บัญชีพลังงานตรง
    
- แผนที่พลังงานรวมแล้วเท่ากับพลังงานรวมจริง
    
- และมีภาพที่คนเห็นแล้วเข้าใจว่ามันเกิดอะไร
    

ผ่านชุดนี้ก่อน แล้วค่อยไปคุย Einstein/Λ แบบไม่มั่ว

---

## Next Step

ถัดไป (เพื่อปิดวงเอกสาร v0.9 ให้เป็น “Public-ready”) มี 2 ชิ้นที่ควรทำทันที:

1. **Part 7 — Public Narrative Layers (Einstein-style explanation)**  
    ทำ “ชั้นคำอธิบาย” แบบ E=mc² ของเรา: นิยามคำพื้นฐาน → Ω → Value/Conflict → Open ledger → Densities
    
2. **Part 8 — Contributor Workflow (Open-source)**  
    กติกาการเพิ่ม model/sweep/demo โดยไม่ทำให้ repo รก (registry/gates/CI)
    

พิมพ์ “ต่อ” อีกที กูจะเริ่ม **Part 7.1 — Public Narrative Layer 0 (คำศัพท์+ภาพ 1 หน้า)** ให้เป็นโครงแบบที่คนอ่านครั้งแรก “เข้าใจ UET ได้จริง” ก่อนค่อยไล่ลงชั้นลึก.


# 000.07/1

## TL;DR

**Part 7.1 = “หน้าคู่มือ 1 หน้า” สำหรับคนเปิดมาอ่านครั้งแรกแล้วต้องเข้าใจ UET ได้ทันที**  
เล่าแบบ _Einstein-style_: มีคำจำกัดความสั้น ๆ + ภาพที่ต้องดู 3 อย่าง + สูตรแกนเดียวที่ไม่ทำให้หลง

---

## Insight

Public ไม่เริ่มจาก matrix/กราฟยิบย่อย  
Public เริ่มจากคำถามนี้:

> “โลกนี้มีอะไรอยู่บ้าง และทำไมมันถึง ‘เข้าที่’ ได้?”

UET ตอบด้วยภาษาง่ายสุดว่า  
**“ระบบคือสิ่งที่ไหลบนภูมิประเทศ Ω แล้วไปจบที่หลุม (สมดุล)”**  
และเราวัดความหมายด้วย 2 แกน: **Value** กับ **Conflict**

---

## Part 7.1 — Public Narrative Layer 0

## UET in One Page (คำศัพท์ + ภาพ + แกนสมการ)

### 1) UET คืออะไร (ประโยคเดียว)

**UET คือเครื่องจำลอง “สมดุลของระบบ” โดยนิยามภูมิประเทศพลังงาน ( \Omega ) แล้วปล่อยให้ระบบไหลลงไปหา “หลุม” (equilibrium/attractor).**

---

### 2) ของ 4 อย่างที่ต้องรู้ก่อน (ไม่เกิน 60 วินาที)

#### (A) State — “สภาพของระบบ”

- คือภาพ/ฟิลด์บนพื้นที่ เช่น `C(x,y)` และ `I(x,y)`
    
- คิดง่าย ๆ: **แผนที่ว่า ‘อะไรอยู่ตรงไหน’**
    

#### (B) Space / Field — “สนาม/สภาพแวดล้อม”

- คือสิ่งที่กำหนดว่าระบบ “ชอบไปทางไหน” (เช่น tilt, resource map, coupling)
    
- คิดง่าย ๆ: **กติกาของโลก**
    

#### (C) Seed — “จุดเริ่ม”

- seed คือการสุ่ม/ตั้งค่าเริ่มต้นต่างกัน
    
- จุดประสงค์ของ seed ไม่ใช่โชว์ความมั่ว แต่ใช้วัดว่า “สนามนี้ robust แค่ไหน” (หลาย seed ลงหลุมเดียวกันไหม)
    

#### (D) Ω (Omega) — “ภูมิประเทศ”

- ( \Omega ) เป็นฟังก์ชันที่ให้ “คะแนนความเข้าที่” ของสภาพระบบ
    
- **ต่ำกว่า = เข้าที่กว่า** (โดยเฉพาะในระบบปิดที่กติกาไม่เปลี่ยน)
    

---

### 3) แกนสมการเดียวที่พอ (Minimal Formal)

เราไม่ต้องให้คนจำสูตรเยอะ แค่เข้าใจโครง:

[  
\text{ระบบเปลี่ยนเพื่อทำให้ }\Omega \text{ ลดลง (ภายใต้กติกาโลกที่กำหนด)}  
]

ในเชิงภาพ: **ลูกบอลกลิ้งลงหาหลุม**

- หลุม = สมดุล (equilibrium/attractor)
    
- หลุมหลายอัน = multi-attractor (seed-sensitive)
    

> สำคัญ: “สมดุล” ใน UET ไม่ได้แปลว่า “หยุดนิ่งตลอดกาล” เสมอไป  
> แต่แปลว่า “ระบบเข้ารูป/เข้าหลุม” ตามกติกาที่กำหนด

---

### 4) 2 คำที่ทำให้ UET อ่านออก (Value & Conflict)

#### Value (V) — “จัดระเบียบได้แค่ไหน”

- วัดว่า **ระบบลด Ω ได้มากเท่าไร / เข้าที่ได้ดีแค่ไหน**
    
- สำหรับ public: “ได้ความเป็นระเบียบ/เสถียรภาพเพิ่มเท่าไร”
    

#### Conflict (C) — “ราคาที่ต้องจ่าย”

- วัดว่า **รอยต่อ/ความตึง/การปะทะของโครงสร้างมากแค่ไหน**
    
- ในระบบฟิลด์ มักเห็นชัดใน **gradient/interface** (ภาพรอยต่อสว่าง ๆ)
    

> สรุป:  
> **Value = ผลลัพธ์ที่อยากได้**  
> **Conflict = ต้นทุน/แรงเสียดทานของการไปถึงผลลัพธ์นั้น**

---

### 5) “ภาพ 3 อย่าง” ที่ต้องดูเสมอ (แทนการดูกราฟ 2D งง ๆ)

Public-friendly = ดู 3 อย่างนี้ก่อน แล้วค่อยดูตาราง

1. **Evolution GIF** — ระบบ “เปลี่ยนรูป” ยังไงจนเข้าที่
    
2. **End State Map** — สุดท้ายเหลืออะไร/โดเมนไหนชนะ
    
3. **Conflict Terrain (Ω_grad density)** — จุดไหน “ตึง/ปะทะ/รอยต่อ” มากที่สุด
    

ถ้าเดโมไหนไม่มี 3 อย่างนี้ → **ยังไม่ควรขึ้น Gallery**

---

### 6) ระบบปิด vs ระบบเปิด (ให้เข้าใจง่ายแบบสุด)

#### Closed system (ระบบปิด)

- กติกาโลก **คงที่** ตลอด
    
- Ω ควรลดลงจนเข้าที่ (ผ่าน gate)
    

#### Open system (ระบบเปิด)

- กติกาโลก **เปลี่ยนได้** (เช่น resource map เปลี่ยน, tilt เปลี่ยน, policy ปรับค่า)
    
- Ω อาจขึ้นได้ แต่เราต้อง “แยกบัญชี” ว่า:
    
    - ระบบคลายเองเท่าไร (**Dissipation**)
        
    - โลกทำงานใส่เท่าไร (**Work injection**)
        

นี่คือเหตุผลที่ v0.9 เราบังคับ **Energy Ledger** (D/W)

---

### 7) Framework เดิมของมึง (ระบบรวม vs กระบวนการเป็นสิ่งหนึ่ง) — map ให้ public เห็นภาพ

ให้คิด 2 เลเยอร์:

#### (Layer อินโทรเวิร์ด) “การเป็นสิ่งหนึ่ง” = Input → Process → Output

- **Constraints/Conditions** = กติกา/ข้อจำกัดใน Ω (potential/grad/coupling)
    
- **Necessity** = สิ่งที่ระบบ “จำเป็นต้องทำ” เพื่ออยู่รอดในสนามนั้น (ไหลลงหาหลุม)
    
- **Capability/Potential** = ความสามารถในการจัดรูป (ขึ้นกับพารามิเตอร์และสภาพแวดล้อม)
    
- **Outputs** = Value และ Conflict (ผลลัพธ์ + ราคาที่จ่าย)
    

#### (Layer เอ็กซ์โทรเวิร์ด) “ระบบรวม” = หลายกระบวนการอยู่ร่วมในสนามเดียว

- เห็นเป็น **หลายโดเมน/หลาย entity**
    
- วัดด้วย robustness (seed), interaction, resource alignment, conflict map
    

---

## Plain-Language Interpretation (สรุปแบบคนทั่วไป)

UET คือ “เกมฟิสิกส์ของสมดุล”

- เราวางโลก (กติกา)
    
- ปล่อยสิ่งต่าง ๆ เรียนรู้/ปรับตัวบนโลกนั้น
    
- แล้วดูว่าเข้าที่แบบไหน (หลุมไหน)
    
- ได้ประโยชน์อะไร (Value)
    
- และต้องจ่ายความตึงแค่ไหน (Conflict)
    

---

## Next Step

ถัดไปจะทำ **Part 7.2 — Public Narrative Layer 1: “อ่าน Demo Card ให้เป็น”**

- 1 เดโมต้องตอบ 5 คำถามอะไรบ้าง (What/Why/How/So what/Checks)
    
- วิธีอ่านภาพ 3 อย่าง + กราฟ Ω/ledger แบบไม่ต้องเป็นนักคณิต
    
- แล้วค่อยเชื่อมไป Gallery archetypes (SYM/BIAS/HIGH_CONFLICT/MULTI_ATTRACTOR)
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูเขียน Part 7.2 ให้เป็นแม่แบบ Demo Card ที่ “คนทั่วไปอ่านแล้วเข้าใจจริง” แต่ยัง “นักวิชาการตรวจสอบได้”.

----
# 000.07/2

## TL;DR

**Part 7.2 = วิธี “อ่าน Demo Card ให้เป็น” + แม่แบบ Demo Card มาตรฐาน**  
เป้าหมายคือให้ _คนทั่วไปอ่านรู้เรื่องใน 60 วินาที_ แต่ _นักวิชาการตรวจสอบย้อนกลับได้ 100%_ (run_id/commit/ledger/gates)

---

## Insight

Demo Card ต้องทำหน้าที่เหมือน “คลิป YouTube + ใบสรุปเชิงวิทย์” ในหน้าเดียว:

- ส่วนบน: **เล่าเรื่องด้วยภาพ** (GIF + End state + Conflict terrain)
    
- ส่วนกลาง: **ความหมาย** (Value/Conflict + phase + robustness)
    
- ส่วนล่าง: **ตรวจสอบได้** (Ω/ledger + gates + reproduce info)
    

> ถ้าขาด “ภาพ 3 อย่าง” → ยังไม่ใช่ demo  
> ถ้าขาด “ตรวจสอบได้” → ยังไม่ใช่วิชาการ

---

## Part 7.2 — Public Narrative Layer 1

## How to Read a Demo Card (and a Standard Template)

## 1) 60-Second Reading Rule (คนทั่วไปควรอ่านได้)

อ่านตามลำดับนี้เท่านั้น:

1. **GIF**: “มันเปลี่ยนรูปยังไง?”
    
2. **End State**: “สุดท้ายเป็นอะไร/ใครเด่น?”
    
3. **Conflict Terrain (Ω_grad density)**: “จุดไหนตึง/รอยต่อเยอะ?”
    
4. **Value–Conflict**: “ได้ประโยชน์เท่าไร จ่ายราคาเท่าไร?”
    
5. **Ω / Ledger**: “เชื่อได้ไหม? (ลดจริง/บัญชีตรงจริง?)”
    

---

## 2) 5 Questions Every Demo Must Answer (ใช้เป็นโครงเล่าเรื่อง)

1. **What**: โลกนี้คืออะไร (กติกา/สนาม/พารามิเตอร์)?
    
2. **How**: ระบบเคลื่อนยังไง (pattern/phase/attractor)?
    
3. **So what**: Value/Conflict คือเท่าไร และหมายความว่าอะไร?
    
4. **Why**: เพราะเทอมไหนใน Ω เป็นตัวนำ (pot/coup/grad + P/R/J)?
    
5. **Can we trust it**: gates ผ่านไหม (ledger/density/validator/repro)?
    

---

## 3) Demo Card Minimum Assets (บังคับเพื่อ “YouTube-level”)

**MUST**

- `figs/evolution.gif`
    
- `figs/state_C_end.png` (หรือ `thumb.png`)
    
- `figs/terrain_omega_grad_density.png` _(Conflict map หลัก)_
    
- `curve_omega.png` _(Ω_total vs t)_
    
- (open system) `policy_trace.png` หรือกราฟพารามิเตอร์ตามเวลา
    

**SHOULD**

- `resource_map.png` + overlay (ถ้าเป็น forcing)
    
- `curve_cumD_cumW.png` (ledger cumulative)
    
- `terrain_omega_density.png` (ภาพรวมโลก)
    

---

## 4) Demo Card Template (Markdown พร้อมใช้งาน)

เอาไปวางได้เลยใน `runs/<RUN_ID>/README_demo.md` หรือ `docs/gallery/demos/DEMO_xxxx/README_demo.md`

````md
# DEMO: <Short title that describes the phenomenon>
**Archetype:** <SYM | BIAS_C | BIAS_I | HIGH_CONFLICT | MULTI_ATTRACTOR>  
**Phase label:** <...>  | **Robustness:** <0..1>  | **Model:** <C_I | multi_field>  
**Run:** <RUN_ID>  | **Commit:** <git_commit>  | **UET version:** <0.8.5+>

---

## 0) One-sentence takeaway (public)
<พูดประโยคเดียวว่า “เกิดอะไร” เช่น “Resource forcing makes the system form a path while conflict concentrates at interfaces.”>

---

## 1) What is the world? (Inputs / Field)
**Parameters (key ones):**
- beta = ...
- kC/kI (or k) = ...
- delta = ...
- s_tilt / lambda_R = ...
- (open) resource map = <static | scheduled | feedback>

**Plain-language:**  
<อธิบาย 2-3 บรรทัดว่า “โลกให้รางวัล/ลงโทษตรงไหน” และ “แรงดึงหลักคืออะไร”>

---

## 2) What happens? (Evolution)
### A) Evolution (GIF)
![evolution](figs/evolution.gif)

### B) End state (what remains)
![end state](figs/state_C_end.png)

**Interpretation (public):**
- <ระบบรวมตัว/แยกโดเมน/ชนะข้างใดข้างหนึ่ง/เกิดหลายก้อน ฯลฯ>

---

## 3) Where is the cost? (Conflict map)
![conflict](figs/terrain_omega_grad_density.png)

**Interpretation:**
- Bright/large regions = high interface cost (conflict)
- <ชี้ให้เห็นว่าความตึงอยู่ที่ขอบ/รอยต่อ/เส้นทาง>

---

## 4) Meaning: Value & Conflict (numbers + words)
**Value:** <value_name> = <number>  
**Conflict:** <conflict_name> = <number>  
**Omega_final:** <number>

**So what (public):**
- Value tells how much ordering/stability is achieved.
- Conflict tells how much interface tension is paid.

---

## 5) Trust checks (scientific)
### A) Omega curve
![omega](figs/curve_omega.png)

### B) Thermo ledger (open system)
![ledger](figs/curve_cumD_cumW.png)   <!-- if open -->

**Gates:**
- thermo_valid = <true/false>, ledger_residual = ...
- density_integral_residual = ...
- validators: transient=<PASS/FAIL>, bias=<PASS/FAIL>

---

## 6) Why it happens (P/R/J explanation)
**P (Potential / drives):** <pot term dominates? tilt? resource?>  
**R (Resistance / conflict):** <grad term → interfaces?>  
**J (Flow / mobility):** <mobility/backtracking/relax speed?>

**One paragraph (public):**
<เล่าให้เข้าใจง่าย: โลกเอนให้ไปทางไหน, ทำไมเกิดขอบ, ทำไมถึงนิ่ง>

---

## 7) Reproduce (for collaborators)
Command:
```bash
python scripts/run_suite.py --matrix <...> --out <...>
````

Artifacts:

- manifest.json / summary.json / timeseries.csv
    
- snapshots/ (>=10 frames)
    
- energy_density/density_final.npz (if enabled)
    

```

---

## 5) “How to interpret” Cheatsheet (คนอ่านไม่ต้องเดา)
ใช้กติกาอ่านแบบนี้ทุกเดโม:

### 5.1 Ω(t) บอกอะไร
- Ω ลดลงแล้วแบน = “เข้าหลุม/เข้าที่”
- Ω ลดลงเร็วต้นแล้วแบนไว = “relax เร็ว” (แต่ต้องดูว่า informative ไหม)

### 5.2 Conflict terrain (Ω_grad density) บอกอะไร
- สว่างตามขอบโดเมน = “รอยต่อคือราคาหลัก”
- สว่างกระจายละเอียดทั่ว = “ตึงทั่วระบบ/แตกสเกลเล็กเยอะ”
- สว่างเฉพาะเป็นเส้นทาง = “เกิดโครงข่าย/route” (เหมาะกับเดโม Physarum)

### 5.3 Value–Conflict อ่านยังไง
- Value สูง + Conflict ต่ำ = “ดีและคุ้ม”
- Value สูง + Conflict สูง = “ได้เยอะ แต่ต้องจ่ายราคา”
- Value ต่ำ + Conflict สูง = “แพ้ทั้งคู่/ระบบตึงแต่ไม่เข้าที่”

### 5.4 Open system ledger (D/W) อ่านยังไง
- cumD เพิ่ม = ระบบ “คลายเอง”
- cumW เพิ่ม = โลก “อัดงานใส่”
- ถ้า ΔΩ เป็นบวก แต่ cumW บวกเยอะ → “โลกทำให้ยากขึ้น” (ยังไม่ใช่บั๊ก ถ้า ledger_valid)

---

## 6) Special Rules per Archetype (กันเล่าเพี้ยน)

### SYM
- ต้องโชว์ “ความสมมาตร/การอยู่ร่วม” ใน end state
- conflict map ไม่ควรเด่นเป็นเส้นแบ่งชัดเกิน (ยกเว้นเป็น SYM แบบ domain)

### BIAS_C / BIAS_I
- end state ต้องเห็น dominance ชัด
- อธิบายว่ามาจาก “tilt / asym / coupling” ตัวไหน (เลือก 1–2 ตัว)

### HIGH_CONFLICT
- conflict terrain ต้องเป็นพระเอก (สว่าง/เด่น)
- ต้องอธิบายว่า conflict มาจาก grad/interface ไม่ใช่ “random noise”

### MULTI_ATTRACTOR
- ต้องโชว์อย่างน้อย 2 seeds “พารามิเตอร์เดียวกัน” แต่ลงเอยต่างกัน
- รายงาน robustness ต่ำ และชี้ว่าอยู่ใกล้ boundary

---

## 7) Math/Physics Interpretation (เวอร์ชันนักวิชาการ — สั้นแต่ตรง)
- Demo เป็น trajectory ของ gradient-flow-like dynamics บน \(\Omega(X;\theta,t)\)  
- Closed: คาดหวัง \(\Delta\Omega\le 0\) (ผ่าน monotone gate)  
- Open: ใช้ ledger แยก \(\Delta\Omega = \Delta\Omega_{\text{diss}}+\Delta\Omega_{\text{env}}\)  
- Conflict map ใช้ \(\omega_{\text{grad}}\) เป็น local proxy ของ interface cost

---

## 8) Plain-Language Interpretation (เวอร์ชันคนทั่วไป — ใช้ได้ในหน้าเดียว)
- GIF บอก “มันกำลังเรียนรู้/ปรับตัว”  
- End state บอก “สุดท้ายมันเป็นอะไร”  
- Conflict map บอก “มันต้องฝืน/ตึงตรงไหน”  
- Value/Conflict บอก “คุ้มไหม”  
- Ω/ledger บอก “เชื่อได้ไหม”

---

## Next Step
ถัดไปคือ **Part 7.3 — Public Narrative Layer 2: Gallery Archetypes & Navigation**  
- ทำให้คนอ่าน “หลายเดโม” แล้วเริ่มเห็นภาพรวม: จากเดโมเดี่ยว → แผนที่ Value–Conflict → archetypes  
- และวางกติกาว่า “จาก sweep ใหญ่ เลือกเดโมตัวแทนยังไง” ให้ตรงกับ Part 4.11 (deterministic)

พิมพ์ “ต่อ” อีกที เดี๋ยวกูเขียน Part 7.3 ให้เป็นโครงหน้า Gallery + วิธีเล่า archetypes แบบคนทั่วไปเข้าใจ แต่ยังคุมความถูกต้องได้.
```


# 000.07/3
## TL;DR

**Part 7.3 = โครง “Gallery Public” + วิธีเล่า archetypes ให้คนทั่วไปเข้าใจ** โดยยังยึดกติกาเดิมแบบ deterministic (Part 4.11):

- หน้าแรกมี 3 อย่าง: **(1) Archetype tiles (5 หมวด)** + **(2) Value–Conflict map** + **(3) How to read (ลิงก์ Part 7.2)**
    
- แต่ละ archetype page มี: **เดโมตัวแทน 3–6 ใบ** (เลือกด้วย rule เดียวกันเสมอ) + “สิ่งที่ต้องดูในภาพ 3 อย่าง”
    
- ทุกเดโมต้อง trace กลับได้ด้วย `registry.json → run_dir → manifest/summary/ledger/density`
    

---

## Insight

Public ต้อง “เดินทาง” จาก **เดโมเดี่ยว** → **รูปแบบรวม** → **กติกาเลือกเดโม**  
ถ้าทำ Gallery เป็นระบบนี้ คนทั่วไปจะไม่จมกับ matrix/กราฟ และนักวิชาการยังตรวจสอบย้อนกลับได้

---

## Part 7.3 — Public Narrative Layer 2

## Gallery Archetypes & Navigation (v0.9)

## 1) เป้าหมายของ Gallery (Public-first แต่ Verify ได้)

Gallery ต้องทำ 3 หน้าที่พร้อมกัน:

1. **สื่อสาร**: เห็นภาพและเข้าใจความหมายใน 1–2 นาที
    
2. **จัดระบบ**: เดโมเยอะก็ไม่รก เพราะมี archetypes + map
    
3. **ตรวจสอบได้**: ทุกใบมี run_id/commit/gates/ledger
    

---

## 2) โครงหน้า Gallery (Pages ที่ต้องมี)

### 2.1 `Gallery Index` (หน้าแรก)

ต้องมี 4 บล็อกหลักเรียงจาก “ง่าย → ลึก”:

**Block A — Archetype Tiles (5 หมวด)**

- SYM
    
- BIAS_C
    
- BIAS_I
    
- HIGH_CONFLICT
    
- MULTI_ATTRACTOR  
    แต่ละ tile: thumbnail 1 รูป + 1 ประโยค takeaway + ปุ่ม “ดูเดโมตัวแทน”
    

**Block B — Value–Conflict Map**

- จุดแต่ละจุด = 1 demo representative (ไม่ใช่ทุก seed)
    
- สี/สัญลักษณ์ = phase (SYM/BIAS_C/BIAS_I)
    
- วงกลมขอบ/สัญลักษณ์พิเศษ = MULTI_ATTRACTOR หรือ HIGH_CONFLICT
    

**Block C — “How to read”**

- ลิงก์ไป Part 7.2 + checklist “ภาพ 3 อย่าง” + ความหมาย Value/Conflict
    

**Block D — “Run it / Verify it”**

- สั้น ๆ 3 บรรทัด: run → validate → aggregate → build gallery
    
- ลิงก์ไป runbook/commands (ไม่ยาว)
    

---

### 2.2 `Archetype Pages` (หน้าแยกของแต่ละหมวด)

แต่ละหน้า archetype มีโครงเหมือนกัน:

1. นิยามหมวด (2–3 บรรทัด)
    
2. “ดูอะไรในภาพ 3 อย่าง” เฉพาะหมวดนั้น
    
3. เดโมตัวแทน 3–6 ใบ (cards)
    
4. “Parameter intuition” สั้น ๆ: พารามิเตอร์ไหนมักดันให้เกิดหมวดนี้ (ไม่ต้องอ้างมาก)
    
5. ลิงก์ไป Value–Conflict map (เน้นจุดที่คัดมา)
    

---

### 2.3 `Demo Pages` (หน้าเดโมรายใบ)

ใช้แม่แบบ Part 7.2 เป็นมาตรฐาน  
ให้เน้นว่า “หน้าเดโมคือความจริง” และ Gallery เป็นสารบัญ

---

## 3) Navigation Rules (วิธีพาคนอ่านแบบไม่หลง)

ให้มีเส้นทาง 2 โหมด (เหมือน YouTube playlist):

### Mode P — Public path (คนทั่วไป)

Index → Archetype ที่สนใจ → เปิดเดโม 1–2 ใบ → ดู map → จบ

### Mode R — Research path (นักวิชาการ/ผู้ร่วมพัฒนา)

Index → map → คลิกจุด → ดู gates/ledger/density checks → เปิด run_dir → reproduce

> กติกา: ทุกหน้าต้องมี breadcrumb “กลับไป archetype / กลับไป map” เสมอ

---

## 4) Archetype Narratives (เล่าแต่ละหมวดยังไงให้เข้าใจง่าย)

> ใช้ “ภาพ 3 อย่าง” เป็นแกนเสมอ

### 4.1 SYM (อยู่ร่วม/สมมาตร)

- **GIF**: ไหลแล้ว “นิ่งแบบไม่เอียงข้าง”
    
- **End state**: ไม่ dominate ชัด (หรือโดเมนสมดุล)
    
- **Conflict map**: ไม่เด่นเป็นเส้นแบ่งรุนแรง (ยกเว้นเป็น SYM แบบ domain)
    

**ประโยคเล่าคงที่**: “ระบบเข้าที่โดยไม่ต้องมีผู้ชนะชัดเจน”

---

### 4.2 BIAS_C / BIAS_I (ชนะข้าง)

- **GIF**: มีแนวโน้มไหลไปทางข้างหนึ่ง
    
- **End state**: dominance ชัด
    
- **Conflict map**: มักเด่นที่ขอบช่วงเปลี่ยนผ่าน (ถ้ามี)
    

**ประโยคเล่าคงที่**: “สนามเอียง ทำให้ระบบลงหลุมที่ favor ฝั่งหนึ่ง”

---

### 4.3 HIGH_CONFLICT (ตึง/รอยต่อคือพระเอก)

- **GIF**: อาจนิ่ง แต่รูปแบบ “ขอบเยอะ/แตกละเอียด/เส้นทาง”
    
- **Conflict map**: ต้องเด่นมาก (นี่คือหลักฐาน)
    
- **Value–Conflict**: Conflict สูง (top percentile)
    

**ประโยคเล่าคงที่**: “ได้โครงสร้างบางอย่าง แต่ต้องจ่ายราคาที่รอยต่อสูง”

---

### 4.4 MULTI_ATTRACTOR (หลายหลุม/seed-sensitive)

- **ต้องโชว์ 2 seeds** อย่างน้อย
    
- **End state**: ลงเอยต่างกันภายใต้พารามิเตอร์เดียว
    
- **Robustness**: ต่ำกว่า threshold ที่กำหนด
    

**ประโยคเล่าคงที่**: “โลกนี้มีมากกว่าหนึ่งคำตอบ—จุดเริ่มทำให้ลงหลุมต่างกัน”

---

## 5) Selection Rules (ดึงเดโมจาก sweep ยังไงให้ deterministic)

**นี่คือจุดที่ต้อง “เชื่อม” Part 4.11 เข้ากับ Gallery**

### 5.1 หน่วยคัดเลือกที่ถูกต้อง

- ใน sweep หนึ่งจุดพารามิเตอร์มีหลาย seed
    
- ให้ “ยุบ” เป็น **representative per parameter point** ก่อน (ข้อ 4.2 ใน Part 4.11)
    
- แล้วค่อยเลือกตัวแทนของ archetype
    

### 5.2 จำนวนเดโมต่อหมวด

แนะนำ:

- archetype ละ 3 ใบเป็น “ขั้นต่ำ”
    
- สูงสุด 6 ใบ เพื่อไม่ให้หน้าแน่น
    

### 5.3 Rule เลือกเดโมตามหมวด (สรุปแบบสั้น)

- **SYM**: robust สูง + conflict ต่ำ
    
- **BIAS_C/BIAS_I**: robust สูง + maximize (value − λ·conflict)
    
- **HIGH_CONFLICT**: conflict สูงสุด (top 5%) แล้วคุมไม่ให้เป็น outlier ที่อ่านไม่รู้เรื่อง
    
- **MULTI_ATTRACTOR**: robustness ต่ำสุด + phase diversity สูง → โชว์ 2 seeds
    

> ทุก rule ต้องเขียนไว้ใน docs และอยู่ในสคริปต์เดียวกัน เพื่อให้ regen ได้เหมือนเดิม

---

## 6) Gallery Data Plumbing (ไฟล์ไหนเป็นศูนย์กลาง)

### 6.1 แหล่งข้อมูลจริง

- `runs/<RUN_ID>/manifest.json`
    
- `runs/<RUN_ID>/summary.json`
    
- `runs/<RUN_ID>/timeseries.csv`
    
- `runs/<RUN_ID>/energy_density/density_final.npz` (ถ้า enable)
    
- `runs/<RUN_ID>/figs/*` (derived assets)
    

### 6.2 ตัวกลาง (Index)

- `registry.json` (candidate/published + assets paths + metrics + archetype)
    

### 6.3 สิ่งที่ Gallery generator ทำ

- อ่าน `registry.json` แล้วสร้าง:
    
    - `docs/gallery/index.md`
        
    - `docs/gallery/archetypes/<name>.md`
        
    - `docs/gallery/demos/<DEMO_ID>/README_demo.md` (หรือ symlink/copy)
        

> กติกา: Gallery ห้ามไป scan ไฟล์มั่ว ๆ เอง นอกจากผ่าน registry

---

## 7) “Map view” ที่คนอ่านแล้วได้อะไร (ไม่ใช่กราฟสวยเฉย ๆ)

Value–Conflict map ต้องมีคำอธิบายสั้น ๆ บนหน้าเดียว:

- แกน X = Conflict (ต้นทุน/รอยต่อ)
    
- แกน Y = Value (การจัดระเบียบ/ประโยชน์)
    
- สี = phase
    
- สัญลักษณ์พิเศษ = multi-attractor / high-conflict
    

**การอ่านแบบคนทั่วไป**

- มุมบนซ้าย = “คุ้ม” (ได้เยอะ จ่ายน้อย)
    
- มุมบนขวา = “ได้เยอะ แต่แพง”
    
- มุมล่างขวา = “ตึงและไม่ได้อะไร”  
    แล้วให้คลิกจุดเพื่อดู “ภาพ 3 อย่าง” ของเดโมนั้น
    

---

## 8) Math/Physics Interpretation (เวอร์ชันนักวิชาการ)

- Gallery คือ empirical atlas ของ attractors ของ dynamics บน (\Omega(X;\theta))
    
- Archetype = partition ของผลลัพธ์ตาม label/metrics ที่ตรวจสอบได้
    
- Deterministic selection ลด selection bias และทำให้ทำซ้ำ/peer review ได้
    
- การแสดง density/ledger ทำให้การตีความ “พลังงาน/ความขัดแย้ง” มีหลักฐาน local-to-global
    

---

## Plain-Language Interpretation

Gallery คือ “พิพิธภัณฑ์เดโม”:

- ห้องนี้คือ “สมมาตร”
    
- ห้องนี้คือ “ชนะข้าง”
    
- ห้องนี้คือ “ตึงมาก”
    
- ห้องนี้คือ “มีหลายคำตอบ”  
    และทุกชิ้นมีวิดีโอ+ภาพ+ตัวเลขยืนยันว่ามันจริง ไม่ใช่เลือกมาโชว์สวย ๆ
    

---

## Next Step

ถัดไปคือ **Part 8 — Contributor Workflow (Open-source)**  
จะล็อกกติกา “ใครจะเพิ่มเดโม/เพิ่มโมเดล/เพิ่มสคริปต์ ต้องทำอะไรบ้าง” เพื่อกัน repo รก:

- naming, export contract, gates, registry update, docs update, CI hooks
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูเริ่ม **Part 8.1 — Contribution Rules (Minimal & Strict)** ให้เป็นข้อกำหนดที่ใช้รับ PR ได้จริง.



# 000.08/1

## TL;DR

**Part 8.1 = กติกา contribution แบบ “สั้นแต่เข้ม”** เพื่อทำให้ repo public แล้ว **ไม่รก/ไม่หลงทิศ**:

- ทุกอย่างต้องผ่าน **Export Contract + Gates + Registry**
    
- เพิ่มของได้ แต่ต้อง “เข้ารูป” (ชื่อไฟล์/โฟลเดอร์/รายงาน/เดโม) และ **regen ได้**
    

---

## Insight

Open-source ที่ดีไม่ใช่มีไฟล์เยอะ แต่คือ:

- คนใหม่เข้ามา “รันได้ → เห็นภาพ → ตรวจสอบได้” ภายใน 10 นาที
    
- PR ทุกอันต้องไม่ทำให้ **registry/gates/CI** พัง
    

---

## Part 8.1 — Contribution Rules (Minimal & Strict)

## 1) Golden Rules (ห้ามละเมิด)

1. **Run truth lives in `run_dir`**: `manifest.json`, `summary.json`, `timeseries.csv`, `snapshots/` คือความจริง
    
2. **Gallery/Docs อ่านจาก `registry.json` เท่านั้น** (ห้ามสคริปต์ไป scan เดาเอง)
    
3. **ทุก demo ที่ publish ต้องมี “ภาพ 3 อย่าง”**: GIF + end-state + conflict terrain
    
4. **ทุก claim เชิง thermo/field ต้องผ่าน gate**: `thermo_valid` + density consistency
    
5. **ทุกอย่างต้อง reproduce**: ระบุ commit + command + seed + matrix
    

---

## 2) Repo Layout (ล็อกโครงให้คงที่)

- `scripts/` : runnable scripts เท่านั้น (ไม่มีไฟล์ผลลัพธ์)
    
- `matrices/` : input matrices (CSV) + ชื่อสื่อความหมาย
    
- `runs/` : output เท่านั้น (ห้าม commit runs ยกเว้น “release pack”/demo pack ที่คัดแล้ว)
    
- `docs/` : เอกสาร + gallery (อ่านจาก registry)
    
- `configs/` (ถ้ามี): preset configs
    
- `reports/` : baseline reports / release reports (generated หรือ curated)
    

**ห้าม**: วางไฟล์สุ่มใน root

---

## 3) Naming Conventions (เพื่อกันรก)

### 3.1 Runs

`runs/<RUN_ID>/` ต้องมี RUN_ID ที่ deterministic และ traceable เช่น:

- รวม: model + sweep + case_id + seed + timestamp/shorthash
    
- ห้ามชื่อ “test1”, “new”, “final_final”
    

### 3.2 Matrices

`matrices/UET_<Suite>_<SweepDims>_seed<k>.csv`  
ตัวอย่าง:

- `UET_Cross_CI_beta_k_ratio_seed10.csv`
    

### 3.3 Demos

`DEMO_XXXX` เพิ่มเลขรัน (ไม่ reuse)

- `docs/gallery/demos/DEMO_XXXX/README_demo.md`
    

---

## 4) Export Contract (สิ่งที่ PR ต้องทำให้ครบ)

### 4.1 Minimum Run Artifact (ต้องมีเพื่อให้ validator/aggregate ทำงาน)

ในทุก `run_dir`:

- `manifest.json`
    
- `summary.json`
    
- `timeseries.csv`
    
- `snapshots/` (>=10 frames สำหรับ demo-ready; สำหรับ non-demo อาจต่ำกว่าได้ แต่ต้องระบุ)
    
- `figs/` (อย่างน้อย end-state + omega curve)
    

### 4.2 Demo-ready (publish candidate)

เพิ่ม:

- `figs/evolution.gif`
    
- `figs/terrain_omega_grad_density.png`
    
- `README_demo.md` (ตาม Part 7.2 template)
    

### 4.3 Thermo-ready (ถ้าจะอ้าง open-system/thermo)

- `Omega_state_step`, `Omega_env_step` ใน timeseries หรือ epoch ledger
    
- `summary.json.thermo` มี: `D_tot`, `W_tot`, `ledger_residual`, `thermo_valid`
    

### 4.4 Field-ready (ถ้าจะอ้าง density/Λ bridge)

- `energy_density/density_final.npz`
    
- `summary.json` มี residual checks: density integral / term-sum
    

---

## 5) Gates (PR ต้องผ่านอะไรบ้าง)

### Gate A — Validators

- `validate_transient` PASS
    
- `validate_bias` PASS  
    (หรือถ้ามี FAIL ต้องอธิบายว่า “expected” และใส่ label/exception ที่เป็นมาตรฐาน)
    

### Gate B — Thermo (ถ้าเปิดระบบ)

- `thermo_valid=true`
    
- `abs(ledger_residual) <= tol`
    

### Gate C — Density (ถ้า export density)

- `omega_density_integral_residual <= tol`
    
- `term_sum_residual <= tol`
    

### Gate D — Repro (ขั้นต่ำ)

- รันซ้ำ 1 เคส 1 seed แล้ว phase/metrics ไม่กระโดดผิดปกติ
    

---

## 6) What you may add (อนุญาตให้เพิ่มอะไรได้บ้าง)

### 6.1 เพิ่ม “Suite/Sweep ใหม่”

ต้องมีครบ:

- matrix csv ใน `matrices/`
    
- runbook snippet (command) ใน `docs/runbook/`
    
- update `registry` rule ถ้าหมวด archetype ใหม่หรือ criteria ใหม่ (ปกติไม่ควรเพิ่มหมวดใหม่ถ้าไม่จำเป็น)
    

### 6.2 เพิ่ม “Model variant”

ต้องมี:

- นิยาม model_type ที่ชัด + params schema
    
- export contract ไม่แตก (ยังมี manifest/summary/timeseries)
    
- demo-ready assets ถ้าจะขึ้น gallery
    

### 6.3 เพิ่ม “Plot script”

ต้อง:

- รับ `--runs <dir>` หรือ `--run <dir>`
    
- ไม่ hardcode path
    
- output ลง `run_dir/figs/` เสมอ
    
- เขียนให้ deterministic (rerun แล้วรูปเหมือนเดิมถ้า input เหมือน)
    

---

## 7) What you may NOT do (ของต้องห้าม)

- ห้าม commit `runs/` จำนวนมหาศาลลง repo public (ยกเว้น release pack ที่คัดแล้ว)
    
- ห้ามแก้ความหมาย core metrics โดยไม่ bump version/CHANGELOG
    
- ห้ามเพิ่ม “วิธีเลือก demo” แบบเลือกมือ (manual cherry-pick) โดยไม่ผ่าน registry rule
    
- ห้ามทำสคริปต์ที่ทำให้ regenerate ไม่ได้ (ใช้ไฟล์กลาง/สเตทลอย)
    

---

## 8) PR Checklist (สั้น ๆ แต่ครบ)

ทุก PR ต้องมีหัวข้อเช็ค:

1. ทำอะไร / ทำไปเพื่ออะไร (1–3 บรรทัด)
    
2. กระทบไฟล์อะไร (scripts/matrices/docs)
    
3. รันคำสั่งไหนเพื่อ reproduce
    
4. Gates ผ่านอะไรบ้าง (แนบ output/สรุป)
    
5. ถ้าเพิ่ม demo: แนบ 3 ภาพ (gif/end/conflict terrain) + demo_id
    

---

## 9) Release Discipline (กันหลงทิศ)

- ทุก milestone ใหญ่: ทำ `reports/v0_9_baseline_report.md` ตาม Part 6.3.2
    
- `CHANGELOG.md` ต้องบอก:
    
    - อะไรเปลี่ยน (metrics/schema/rules)
        
    - ทำไมเปลี่ยน
        
    - compatibility: “ต้อง rerun ไหม”
        

---

## Plain-Language Interpretation

ใครจะมาช่วยทำโปรเจกต์นี้ ต้อง “เล่นตามกติกาเดียวกัน”:

- รันแล้วได้ไฟล์มาตรฐาน
    
- มีภาพที่คนเข้าใจ
    
- มีตัวเลขที่ตรวจสอบได้
    
- และทุกอย่างย้อนกลับไปหา run จริงได้
    

---

## Next Step

ต่อไปจะเป็น **Part 8.2 — Workflow Recipes (Contributor Playbooks)**:

- “เพิ่ม sweep ใหม่” ต้องทำ 7 ขั้นอะไรบ้าง
    
- “เพิ่ม demo ใหม่” ต้องทำ 5 ขั้นอะไรบ้าง
    
- “เพิ่ม metric ใหม่” ต้องทำ 6 ขั้นอะไรบ้าง (พร้อม gate + backward compatibility)
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูทำ Part 8.2 เป็น playbook แบบทำตามได้ทีละข้อเลย (เหมือนคู่มือทำอาหาร).


---
# 000.08/2

## TL;DR

**Part 8.2 = Contributor Playbooks (ทำตามได้ทีละขั้นเหมือนคู่มือทำอาหาร)**  
มี 6 สูตรหลักที่คนร่วมโปรเจกต์ต้องใช้บ่อยสุด:

1. เพิ่ม **Sweep/Suite ใหม่**
    
2. เพิ่ม **Demo ใหม่ (ขึ้น Gallery ได้)**
    
3. เพิ่ม **Metric ใหม่** (ไม่ทำลาย compatibility)
    
4. เพิ่ม **Model variant** (ยังอยู่ในกรอบ Ω/dynamics)
    
5. เพิ่ม/ปรับ **Plot script**
    
6. ทำ **Bugfix/Refactor แบบไม่ทำให้ repo เละ**
    

ทุกสูตรจบด้วย “**Gates ที่ต้องผ่าน**” + “**ไฟล์ที่ต้องแก้**” + “**คำสั่งรัน**”

---

## Insight

สิ่งที่ทำให้ open-source ไม่รกคือ “ทุกคนทำตามขั้นตอนเดียวกัน”  
ดังนั้น playbook ต้องบังคับ 3 อย่างเสมอ:

- output เข้าสัญญา (export contract)
    
- ผ่าน gates (ledger/density/validators)
    
- trace ได้ (registry + commit + commands)
    

---

## Part 8.2 — Workflow Recipes (Contributor Playbooks)

## Playbook 1) เพิ่ม Sweep / Suite ใหม่

### เป้าหมาย

เพิ่มชุดทดลองใหม่ที่ “รันได้–validate ได้–aggregate ได้–เข้ากับ gallery/registry ได้”

### ขั้นตอน

1. **นิยามชื่อ suite ให้ชัด**
    
    - ตั้งชื่อแบบสื่อความหมาย: `UET_<Suite>_<Dims>_seed<k>.csv`
        
    - ตัวอย่าง: `UET_Cross_CI_beta_delta_seed10.csv`
        
2. **สร้าง matrix CSV ใน `matrices/`**
    
    - ต้องมีคอลัมน์ขั้นต่ำที่ `run_suite.py` รับได้ (ตาม schema ปัจจุบัน)
        
    - ใส่ `case_id` ที่ deterministic (เช่น hash ของพารามิเตอร์หรือ incremental)
        
3. **เพิ่ม runbook snippet ใน `docs/runbook/`**
    
    - ไฟล์: `docs/runbook/<suite_name>.md`
        
    - ใส่ 3 คำสั่งมาตรฐาน:
        
        ```bash
        python scripts/run_suite.py --matrix matrices/<...>.csv --out runs_<suite>
        python scripts/validate_transient_v3.py --runs runs_<suite> --out runs_<suite>/validation_transient_v3.json
        python scripts/validate_bias_v2.py --runs runs_<suite> --out runs_<suite>/validation_bias_v2.json
        python scripts/aggregate_final_summary.py --runs runs_<suite> --out runs_<suite>/UET_final_summary.csv
        ```
        
4. **รันจริง 1 รอบแบบ “smoke” ก่อน**
    
    - ลดขนาด matrix ให้เหลือ 2–5 cases + 1 seed เพื่อเช็ค pipeline
        
5. **รันเต็ม แล้วตรวจ gates**
    
    - validators PASS
        
    - ถ้าเป็น open system ต้องมี thermo_valid
        
    - ถ้า export density ต้องผ่าน density residual
        
6. **อัปเดต registry (ถ้าจะ publish เดโมจาก suite นี้)**
    
    - เพิ่ม entries เป็น “candidate” ก่อน (ยังไม่ต้องขึ้น index)
        

### Gates ที่ต้องผ่าน

- Gate A validators (transient/bias) ผ่าน
    
- ถ้า suite เป็น open: Gate B thermo ผ่าน
    
- ถ้า suite export density: Gate C density ผ่าน
    

---

## Playbook 2) เพิ่ม Demo ใหม่ (ขึ้น Gallery ได้)

### เป้าหมาย

ได้ “Demo Card” ที่คนทั่วไปดูเข้าใจ + นักวิชาการ trace ได้

### ขั้นตอน

1. **เลือก run candidate จากผล aggregate**
    
    - เลือกด้วย rule deterministic (Part 4.11) ห้ามเลือกมือแบบตามใจ
        
    - ถ้าเป็น MULTI_ATTRACTOR ต้องเลือกอย่างน้อย 2 seeds
        
2. **ตรวจว่า run_dir มีของครบ**
    
    - MUST: `manifest.json`, `summary.json`, `timeseries.csv`, `snapshots/`
        
    - Demo-ready: `figs/evolution.gif`, `figs/state_end.png`, `figs/terrain_omega_grad_density.png`
        
3. **สร้าง/เติมรูปให้ครบ**
    
    - ถ้ายังไม่มี: รัน plot scripts ให้ generate ลง `run_dir/figs/`
        
    - (open system) ต้องมี `curve_cumD_cumW.png` หรือเทียบเท่า
        
4. **เขียน `README_demo.md` ตามแม่แบบ Part 7.2**
    
    - ห้ามยาวเกินจำเป็น แต่ต้องมี:
        
        - One-sentence takeaway
            
        - ภาพ 3 อย่าง (GIF/end/conflict)
            
        - Value/Conflict + Ω_final
            
        - Gates (thermo_valid/density residual/validators)
            
        - reproduce command
            
5. **เพิ่ม entry ลง `registry.json`**
    
    - status: `candidate` → `published` เมื่อผ่าน review
        
    - ระบุ paths ของ assets ที่ gallery จะลิงก์
        
6. **build gallery locally (regen)**
    
    - ให้แน่ใจว่า gallery generator อ่าน registry แล้ว “ประกอบหน้าได้”
        

### Gates ที่ต้องผ่าน

- Gate G3 (ภาพ 3 อย่าง + demo ready)
    
- Gate A validators
    
- ถ้า open: thermo_valid
    
- ถ้า density: density checks
    

---

## Playbook 3) เพิ่ม Metric ใหม่ (ไม่พัง backward compatibility)

### เป้าหมาย

เพิ่มตัวชี้วัด (thermo/info/phase/quality) โดยไม่ทำให้สรุปเก่าอ่านไม่ได้

### ขั้นตอน

1. **กำหนด: metric นี้อยู่ชั้นไหน**
    
    - `summary.json` (final metrics)
        
    - `timeseries.csv` (time-dependent)
        
    - `epoch_summary.csv` (open/control)
        
2. **เพิ่ม metric แบบ “optional-first”**
    
    - aggregator/plot ต้อง “ไม่ fail” ถ้า metric ยังไม่มีใน run เก่า
        
    - ใช้ค่า `NaN` หรือ omit อย่างมีวินัย
        
3. **ระบุชื่อคีย์มาตรฐาน**
    
    - ใส่ใน docs: `docs/metrics/<metric_pack>.md`
        
    - อธิบาย: นิยาม, ช่วงค่า, การตีความ, prerequisites
        
4. **เพิ่มลง scripts ที่เกี่ยวข้อง**
    
    - `aggregate_final_summary.py` ต้องเพิ่มคอลัมน์ใหม่แบบ backward compatible
        
    - ถ้าเป็น info metrics: สร้างไฟล์ `info_timeseries.csv` แยก (แนะนำ) เพื่อลดการพัง schema
        
5. **เพิ่ม “sanity check”**
    
    - เช่น ค่าอยู่ในช่วง [0,1] หรือไม่
        
    - หรือ monotonicity expectation
        
6. **อัปเดต CHANGELOG**
    
    - ระบุว่าเป็น additive (ไม่ breaking)
        
    - ระบุว่า run เก่าไม่ต้อง rerun แต่ metric ใหม่จะว่าง
        

### Gates ที่ต้องผ่าน

- run เก่าต้องยัง aggregate ได้ไม่ error
    
- baseline suite ต้องยังผ่าน validators
    
- ถ้า metric กระทบ thermo/density: ต้องไม่ทำให้ residual gate fail
    

---

## Playbook 4) เพิ่ม Model Variant (ยังอยู่ในกรอบ UET)

### เป้าหมาย

เพิ่ม model_type ใหม่ เช่น multi-field หรือ forcing mode โดยไม่หลุดกรอบ Ω/dynamics

### ขั้นตอน

1. **นิยาม schema ของ params**
    
    - ระบุ `model_type`
        
    - ระบุพารามิเตอร์ใหม่ใน manifest อย่างชัด
        
2. **ยืนยันว่าแกนยังเดิม**
    
    - ต้องยังคำนวณ `Omega_total` ได้
        
    - ต้องยัง export `summary.json` + `timeseries.csv`
        
    - ต้องยังผ่าน monotone gate หรือ ledger (ตาม closed/open)
        
3. **เพิ่ม minimal tests**
    
    - 1–2 cases ที่รู้พฤติกรรมโดย intuition (sanity)
        
    - ต้อง produce phase label หรืออย่างน้อย metrics ที่เทียบได้
        
4. **เพิ่ม plot support**
    
    - อย่างน้อย end-state + omega curve
        
    - ถ้า public: gif + conflict terrain
        
5. **เอกสาร**
    
    - `docs/models/<model_type>.md` (นิยาม + parameters + ตัวอย่าง matrix row)
        

### Gates ที่ต้องผ่าน

- baseline S1 (closed) ต้องไม่พัง
    
- ถ้าเป็น open: thermo ledger ต้อง valid
    
- ถ้า export density: density residual ต้องผ่าน
    

---

## Playbook 5) เพิ่ม/ปรับ Plot Script (ให้เป็นของสาธารณะได้จริง)

### เป้าหมาย

plot script ต้อง “รันที่ไหนก็ได้” ไม่ hardcode และ output คงที่

### ขั้นตอน

1. **อินเตอร์เฟซมาตรฐาน**
    
    - รับ `--run <run_dir>` หรือ `--runs <runs_dir>`
        
    - ไม่ scan มั่วนอก path ที่รับมา
        
2. **อ่าน input จาก artifacts เท่านั้น**
    
    - summary/manifest/timeseries/snapshots/density
        
3. **เขียน output ลง `run_dir/figs/`**
    
    - ตั้งชื่อรูปให้คงที่ เช่น `curve_omega.png`, `terrain_omega_grad_density.png`
        
4. **ถ้าทำ gallery**
    
    - ต้องสร้าง `thumb.png` (ภาพเดียว) เพื่อใช้ tile
        
5. **ทดสอบกับ run เก่า**
    
    - ถ้า field ใหม่ไม่มี ให้ degrade gracefully
        

### Gates ที่ต้องผ่าน

- rerun แล้วรูปไม่เปลี่ยนถ้า input ไม่เปลี่ยน
    
- ไม่ทำให้ pipeline ช้าหรือพัง
    

---

## Playbook 6) Bugfix / Refactor แบบไม่เละ

### เป้าหมาย

แก้บั๊ก/ปรับโครงสร้าง โดยไม่ทำให้ “ความจริงของ run” สับสน

### ขั้นตอน

1. **ล็อกสาเหตุ + ผลกระทบ**
    
    - บั๊กเกี่ยวกับ export? metrics? stability?
        
    - กระทบ schema ไหม?
        
2. **เพิ่ม regression test case**
    
    - อย่างน้อย 1 case ที่ก่อนแก้ fail หลังแก้ pass
        
    - ถ้าเกี่ยวกับ aggregator ให้มี CSV ตัวอย่าง
        
3. **คุม breaking changes**
    
    - ถ้าเปลี่ยนชื่อคอลัมน์/คีย์ → ต้อง bump version + migration note
        
    - ถ้า additive → ระบุชัดว่า run เก่าใช้ได้
        
4. **อัปเดต docs + CHANGELOG**
    
    - อธิบาย patch สั้น ๆ
        

### Gates ที่ต้องผ่าน

- baseline suite ผ่าน
    
- run เก่า aggregate ได้
    
- registry build ไม่พัง
    

---

## “Fast Tracks” ที่คนทำงานจริงจะใช้บ่อย

## Fast Track A — เพิ่ม demo จาก suite ที่มีอยู่แล้ว

1. run suite → validate → aggregate
    
2. เลือก representative → plot pack → เขียน README_demo
    
3. registry candidate → build gallery → publish
    

## Fast Track B — เพิ่ม metric info ใหม่

1. นิยาม + doc
    
2. ทำ extractor จาก snapshots → info_timeseries.csv
    
3. summary final metrics → plots
    
4. ensure backward compatible → baseline pass
    

---

## Next Step

Part ต่อไป (8.3) จะเป็น “**PR Templates & Review Rubric**”:

- เทมเพลต PR ที่บังคับกรอก (commands, gates, artifacts)
    
- rubric สำหรับ reviewer ว่าต้องเช็คอะไรบ้าง (public + scientific)
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูทำ Part 8.3 ให้เป็นไฟล์ template พร้อมใช้ (ในรูป markdown) สำหรับเอาไปวางใน repo ได้ทันที.

# 000.08/3

## TL;DR

**Part 8.3 = PR Templates + Review Rubric (พร้อมเอาไปวางใน repo ได้เลย)**  
ให้ 2 ไฟล์หลัก:

1. `.github/PULL_REQUEST_TEMPLATE.md` (บังคับกรอกเพื่อกัน PR มั่ว)
    
2. `docs/review_rubric.md` (รูบริกสำหรับ reviewer ว่าต้องเช็คอะไร)
    

---

## Insight

ถ้า repo จะ public แล้วไม่รก ต้องทำให้ “ทุก PR ตอบคำถามเดียวกัน”:

- ทำอะไร / ทำเพื่ออะไร
    
- รันซ้ำได้ไหม (คำสั่ง + seed + matrix)
    
- ผ่าน gates ไหม (validators / thermo / density)
    
- กระทบ schema/backward compatibility ไหม
    
- จะขึ้น gallery/registry ไหม
    

---

## Part 8.3 — PR Templates & Review Rubric

## 1) `.github/PULL_REQUEST_TEMPLATE.md`

วางไฟล์นี้ที่ `.github/PULL_REQUEST_TEMPLATE.md`

````md
# Summary (1–3 lines)
<!-- What changed and why? Keep it short and concrete. -->

## Type of change
- [ ] Bugfix
- [ ] Refactor (no behavior change)
- [ ] New sweep/suite (matrix + runbook)
- [ ] New demo (gallery candidate/publish)
- [ ] New metric (thermo/info/phase/quality)
- [ ] New model variant (within UET Ω/dynamics)
- [ ] Plot/visualization script
- [ ] Docs only

## Motivation / Context
<!-- What problem does this solve? What user story or research need? -->
- Problem:
- Expected outcome:

## Scope (files/areas touched)
<!-- List key files or directories changed -->
- scripts/:
- matrices/:
- docs/:
- (other):

## Reproducibility (MUST)
<!-- Provide the exact command(s) to reproduce the result. -->
### Command(s)
```bash
# 1) run
python scripts/run_suite.py --matrix matrices/<...>.csv --out runs_<...>

# 2) validate
python scripts/validate_transient_v3.py --runs runs_<...> --out runs_<...>/validation_transient_v3.json
python scripts/validate_bias_v2.py --runs runs_<...> --out runs_<...>/validation_bias_v2.json

# 3) aggregate
python scripts/aggregate_final_summary.py --runs runs_<...> --out runs_<...>/UET_final_summary.csv

# 4) plots (if applicable)
python scripts/<plot_script>.py --runs runs_<...>
````

### Environment

- OS:
    
- Python version:
    
- Package install method: (pip/conda)
    
- Commit hash: `<git rev-parse --short HEAD>`
    

## Artifacts (MUST for non-doc PRs)

- Example run_dir: `runs/<RUN_ID>/`
    
- Contains:
    
    -  manifest.json
        
    -  summary.json
        
    -  timeseries.csv
        
    -  snapshots/ (>=10 frames if demo-ready)
        
    -  figs/ (end-state + omega curve at minimum)
        

## Gates checklist (MUST)

### Validators

-  transient validator PASS (`validation_transient_v3.json`)
    
-  bias validator PASS (`validation_bias_v2.json`)
    
- Notes (if any warnings/flags):
    

### Thermo ledger (ONLY if open system / claims about D/W)

-  summary.json has `thermo.thermo_valid=true`
    
-  |ledger_residual| <= tol
    
- D_tot, W_tot reported:
    
    - D_tot =
        
    - W_tot =
        
    - ledger_residual =
        

### Density export (ONLY if claims about density / conflict terrain source)

-  `energy_density/density_final.npz` present
    
-  density_integral_residual <= tol
    
-  term_sum_residual <= tol
    

## Demo / Gallery (ONLY if adding a demo)

- Demo ID: `DEMO_XXXX`
    
- Archetype: (SYM / BIAS_C / BIAS_I / HIGH_CONFLICT / MULTI_ATTRACTOR)
    
-  Has the “3 required visuals”:
    
    -  evolution.gif
        
    -  end-state image
        
    -  terrain_omega_grad_density.png
        
-  README_demo.md added/updated (Part 7.2 format)
    
- Registry update:
    
    -  `registry.json` entry added/updated
        
    - status: [ ] candidate [ ] published
        

## Backward compatibility / Schema

- Does this change schema/keys/columns?
    
    -  No (additive-only)
        
    -  Yes (BREAKING) → must bump version + add migration note
        
- If adding new metric:
    
    -  aggregator does NOT fail on older runs (missing fields handled)
        

## Documentation

-  Docs updated (runbook/model/metrics) if behavior changed
    
-  CHANGELOG updated if user-facing change
    

## Evidence (screenshots/links)

- Key figure(s):
    
- Notes:
    

## Checklist before request review

-  I ran at least one smoke test locally
    
-  I did not commit bulk `runs/` outputs (unless release/demo pack policy allows)
    
-  I followed naming conventions (runs/matrices/demos)
    

````

---

## 2) `docs/review_rubric.md`
วางไฟล์นี้ที่ `docs/review_rubric.md`

```md
# Review Rubric (v0.9)

This rubric defines how we review PRs to keep UET public repo reproducible, non-rigid, and not messy.

---

## A) Fast triage (30–60 seconds)
**Reject immediately if:**
- Missing reproducibility commands (exact CLI steps)
- No example run_dir artifacts for non-doc PRs
- Manual cherry-pick demo selection without deterministic rule/registry update
- Commits large `runs/` bulk outputs without release/demo policy
- Breaks schema without version bump + migration note

**Proceed if:**
- PR has clear summary + commands + gates evidence + bounded scope

---

## B) Core checks (Must pass)
### B1) Reproducibility
- [ ] Commands run without hidden dependencies or hardcoded paths
- [ ] Seed/matrix/out path are explicit
- [ ] Commit hash provided and consistent

### B2) Export Contract
For at least one example run_dir:
- [ ] manifest.json present and complete
- [ ] summary.json present
- [ ] timeseries.csv present
- [ ] figures present (end-state + omega curve minimum)
- [ ] snapshots exist if demo-ready claim

### B3) Gates
- Validators:
  - [ ] transient PASS
  - [ ] bias PASS
- Thermo (only if open/claims):
  - [ ] thermo_valid true
  - [ ] ledger_residual within tolerance
- Density (only if density/field claims):
  - [ ] density_final.npz present
  - [ ] integral residual within tolerance
  - [ ] term sum residual within tolerance

### B4) Backward compatibility
- [ ] New metrics are additive and do not break aggregators on older runs
- [ ] Missing fields handled gracefully (NaN/optional)
- If BREAKING:
  - [ ] version bump
  - [ ] migration note
  - [ ] CHANGELOG updated

---

## C) PR-type specific checks
### C1) New sweep/suite
- [ ] Matrix file naming is standard
- [ ] runbook doc added with run/validate/aggregate commands
- [ ] Smoke test (small subset) evidence included
- [ ] Full suite results do not violate gates (or clearly marked as WIP)

### C2) New demo (gallery)
- [ ] 3 visuals present (gif/end/conflict terrain)
- [ ] README_demo.md follows demo template
- [ ] Archetype assignment justified by metrics/labels
- [ ] Registry entry added/updated (candidate or published)
- [ ] No manual “looks nice” selection without deterministic rule

### C3) New metric
- [ ] Metric definition documented (formula, range, prerequisites)
- [ ] Stored location is consistent (summary vs timeseries vs info_timeseries)
- [ ] Sanity checks exist (range, NaN handling, etc.)
- [ ] Does not create “silent meaning shift” in existing metrics

### C4) Model variant
- [ ] Still computes Omega_total
- [ ] Still exports manifest/summary/timeseries
- [ ] Minimal tests included
- [ ] Plot support added (at least end-state + omega curve)

### C5) Plot script
- [ ] Accepts --run or --runs (no hardcoded paths)
- [ ] Outputs only to run_dir/figs
- [ ] Deterministic output (same inputs → same files)
- [ ] Graceful degradation when optional files are missing

### C6) Refactor/bugfix
- [ ] Regression test added (before fail → after pass)
- [ ] Baseline suite does not regress (or explicitly explained)

---

## D) Quality bar for merging
**Approve when:**
- All applicable gates pass
- Reproducibility commands are complete
- Export contract is intact
- Docs/CHANGELOG updated when needed
- No uncontrolled repo growth

**Request changes when:**
- Evidence missing (gates, artifacts, commands)
- Ambiguous behavior change without docs
- Non-deterministic selection/registry misuse
- Hardcoded paths / non-portable scripts

---

## E) Reviewer notes (best practices)
- Prefer “small PRs” that isolate one concern
- If PR includes demo + metric changes, ask to split unless tightly coupled
- Keep public narrative honest: no overclaim beyond measurable artifacts
````

---

## Next Step

ถัดไป (Part 8.4) คือ “**Repo Starter Pack for Public Release**” แบบเป็นรายการไฟล์ที่ควรมีใน root:

- `README.md` (quickstart)
    
- `CONTRIBUTING.md`
    
- `CODE_OF_CONDUCT.md`
    
- `SECURITY.md` (ถ้าต้องการ)
    
- `LICENSE`
    
- `CITATION.cff`
    
- `docs/` โครงขั้นต่ำ + gallery index skeleton
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูจัด Part 8.4 เป็น “รายการ + โครงไฟล์ตัวอย่าง” ให้เอาไปวางได้เลย.


# 000.08/4
## TL;DR

**Part 8.4 = Repo Starter Pack for Public Release**  
นี่คือ “ชุดไฟล์ขั้นต่ำ” ที่ทำให้ repo UET เปิดสาธารณะแล้วคนใหม่ **เข้าได้-รันได้-เชื่อได้** ภายในเร็ว ๆ พร้อมโครงไฟล์ตัวอย่าง (copy ไปวางได้เลย)

---

## Insight

Public-ready = 3 อย่างพร้อมกัน:

1. **Quickstart ชัด** (รัน 1 คำสั่งแล้วเห็นผล)
    
2. **กติกา contribution ชัด** (PR template + gates)
    
3. **เอกสาร/เดโมนำทางได้** (Gallery + Demo Card)
    

---

## Part 8.4 — Public Repo Starter Pack (Files + Skeletons)

## 1) โครงไฟล์ (แนะนำ)

```text
/README.md
/CHANGELOG.md
/LICENSE
/CITATION.cff
/CONTRIBUTING.md
/CODE_OF_CONDUCT.md
/SECURITY.md                (optional)
/requirements.txt           (หรือ pyproject.toml)
/docs/
  /index.md
  /quickstart.md
  /runbook/
    cross_sweeps.md
  /models/
  /metrics/
  /review_rubric.md
  /gallery/
    /index.md
    /archetypes/
      SYM.md
      BIAS_C.md
      BIAS_I.md
      HIGH_CONFLICT.md
      MULTI_ATTRACTOR.md
    /demos/
      (generated)
/.github/
  /PULL_REQUEST_TEMPLATE.md
```

---

## 2) README.md (หน้าแรกที่คนต้อง “รันได้ใน 3 นาที”)

**เป้าหมาย**: คนใหม่อ่านจบแล้วรู้ว่าโปรเจกต์ทำอะไร + วิธีรันขั้นต่ำ + จะไปดู Gallery ตรงไหน

````md
# UET (Equilibrium ... Theory) — Public Research Harness

UET is a simulation + validation harness for studying equilibrium/attractor behavior on an energy-like landscape Ω.
It supports closed/open systems, reproducible sweeps, validators, aggregation, and a public-facing demo gallery.

## What you get
- Run sweeps from CSV matrices
- Validate transient & bias behavior
- Aggregate results into a final summary
- Produce demo-ready artifacts (GIF + end state + conflict terrain)
- Build a deterministic gallery from registry.json

## Quickstart (smoke test)
```bash
pip install -r requirements.txt
python scripts/run_suite.py --matrix matrices/<SMOKE_MATRIX>.csv --out runs_smoke
python scripts/validate_transient_v3.py --runs runs_smoke --out runs_smoke/validation_transient_v3.json
python scripts/validate_bias_v2.py --runs runs_smoke --out runs_smoke/validation_bias_v2.json
python scripts/aggregate_final_summary.py --runs runs_smoke --out runs_smoke/UET_final_summary.csv
````

## Documentation

- Quickstart: docs/quickstart.md
    
- Runbooks: docs/runbook/
    
- Gallery: docs/gallery/index.md
    

## Scientific integrity

All thermo/field claims require gates:

- thermo_valid + ledger_residual
    
- density integral residual (if density exported)
    

## Contributing

See CONTRIBUTING.md and the PR template.

````

> หมายเหตุ: `<SMOKE_MATRIX>` ให้ทำไฟล์ matrix เล็ก ๆ 2–5 เคสไว้จริง (เพื่อให้ repo “รันได้ทันที”)

---

## 3) docs/index.md (สารบัญเอกสาร)
```md
# Docs Index
- Quickstart: quickstart.md
- Runbook: runbook/
- Models: models/
- Metrics: metrics/
- Review rubric: review_rubric.md
- Gallery: gallery/index.md
````

---

## 4) docs/quickstart.md (เวอร์ชันละเอียดนิดเดียว แต่ไม่เยิ่นเย้อ)

````md
# Quickstart
## Install
```bash
pip install -r requirements.txt
````

## Run a small suite

```bash
python scripts/run_suite.py --matrix matrices/<SMOKE_MATRIX>.csv --out runs_smoke
```

## Validate

```bash
python scripts/validate_transient_v3.py --runs runs_smoke --out runs_smoke/validation_transient_v3.json
python scripts/validate_bias_v2.py --runs runs_smoke --out runs_smoke/validation_bias_v2.json
```

## Aggregate

```bash
python scripts/aggregate_final_summary.py --runs runs_smoke --out runs_smoke/UET_final_summary.csv
```

## Where results live

- runs_smoke/<RUN_ID>/manifest.json
    
- runs_smoke/<RUN_ID>/summary.json
    
- runs_smoke/<RUN_ID>/timeseries.csv
    
- runs_smoke/<RUN_ID>/snapshots/
    
- runs_smoke/<RUN_ID>/figs/
    

````

---

## 5) CONTRIBUTING.md (กติกาแบบสั้น + ลิงก์ไป rubric)
```md
# Contributing
## Golden rules
1) Truth lives in run_dir artifacts (manifest/summary/timeseries/snapshots).
2) Gallery reads from registry.json only.
3) Demos must include GIF + end state + conflict terrain.
4) Thermo/field claims require gates (thermo_valid, density residual).
5) Provide exact reproduce commands in PR.

## Workflow
- For PR requirements, see .github/PULL_REQUEST_TEMPLATE.md
- Review rubric: docs/review_rubric.md

## Do not commit bulk runs
Large run outputs must be shared as release/demo packs, not raw runs.
````

---

## 6) CHANGELOG.md (กัน “meaning shift” แบบเงียบ ๆ)

```md
# Changelog

## Unreleased
- ...

## v0.9.0 (YYYY-MM-DD)
### Added
- Thermo ledger metrics (D/W) with thermo_valid gate
- Density export spec (omega_density terms) with integral residual gate
- Info metrics pack (hist/spectral/spatial/TV/alignment)
### Changed
- ...
### Fixed
- ...
### Breaking changes
- (none)
```

---

## 7) LICENSE (เลือกแบบชัด ๆ)

- ถ้าอยากให้คนใช้กว้าง: **MIT** หรือ **Apache-2.0**
    
- ถ้าอยากบังคับ share-alike: **GPLv3** (จะทำให้บางองค์กรใช้ยากขึ้น)
    

> เลือกอันเดียวแล้วใส่ไฟล์ LICENSE ตามมาตรฐาน (ไม่ต้องเขียนเอง)

---

## 8) CITATION.cff (ให้คน cite ได้ถูก)

```yaml
cff-version: 1.2.0
title: "UET: Equilibrium Simulation & Validation Harness"
message: "If you use this software, please cite it."
type: software
authors:
  - family-names: "..."
    given-names: "..."
version: 0.9.0
date-released: YYYY-MM-DD
repository-code: "https://github.com/<org>/<repo>"
license: "MIT"
```

---

## 9) CODE_OF_CONDUCT.md (ใช้เทมเพลตมาตรฐาน)

แนะนำใช้ Contributor Covenant เวอร์ชันล่าสุด (วางไฟล์ตาม template)

---

## 10) SECURITY.md (optional แต่ดี ถ้าจะ public จริง)

```md
# Security Policy
## Reporting a Vulnerability
Please open a private report or contact: <email or issue process>
We will respond within a reasonable timeframe.
```

---

## 11) requirements.txt (หรือ pyproject.toml)

ถ้าใช้ requirements:

- ล็อกเวอร์ชันหลัก (ขั้นต่ำ) ที่รันได้จริง
    
- อย่าใส่ของฟุ่มเฟือย
    

(ถ้าอยากสะอาดระยะยาว ใช้ `pyproject.toml` + `pip-tools/poetry` ก็ได้ แต่ไม่จำเป็นตอนนี้)

---

## 12) docs/gallery/index.md (โครงหน้า gallery)

```md
# UET Gallery
This gallery is built from registry.json (deterministic selection).

## How to read
See: docs/gallery/how_to_read.md (or link to Part 7.2)

## Archetypes
- SYM
- BIAS_C
- BIAS_I
- HIGH_CONFLICT
- MULTI_ATTRACTOR

## Value–Conflict Map
(autogenerated figure + links)
```

แล้วสร้างไฟล์หมวด archetype skeleton:  
`docs/gallery/archetypes/SYM.md` ฯลฯ เป็นหน้า placeholder ที่ generator จะเติม cards

---

## 13) docs/metrics/ (ให้มี “แพ็ค” ชัด)

ขั้นต่ำควรมี:

- `docs/metrics/thermo_pack.md` (Part 5.4.1)
    
- `docs/metrics/info_pack.md` (Part 6.1)
    
- `docs/metrics/value_conflict.md` (ความหมาย Value/Conflict + mapping กับ Ω_terms)
    

---

## 14) .github/PULL_REQUEST_TEMPLATE.md + docs/review_rubric.md

อันนี้เราเขียนไว้แล้วใน Part 8.3 — เอาไปวางได้เลย

---

## Next Step

**Part 8.4.1 — Release Checklist (v0.9 Public)**  
จะเป็น checklist สั้น ๆ ว่า “ก่อนกดปล่อย public” ต้องเช็คอะไรบ้าง: baseline suites (S1–S4), gates, gallery build, license/citation, และแพ็ค release artifacts

พิมพ์ “ต่อ” อีกที เดี๋ยวกูจัด Part 8.4.1 ให้เป็น checklist แบบติ๊กได้เลย.

---
# 000.08/4.1
## TL;DR

**Part 8.4.1 = Release Checklist (v0.9 Public)**  
เช็คลิสต์แบบ “ติ๊กได้” ก่อนกดปล่อย public:

- Baselines ผ่าน (S1–S4)
    
- Gates ผ่าน (validator/thermo/density)
    
- Gallery build ได้จาก registry
    
- Docs/License/Citation พร้อม
    
- Release pack จัดเป็นชุดเดียว (ไม่ commit runs ดิบ)
    

---

## Insight

“ปล่อย public” ไม่ใช่แค่ push โค้ดขึ้น GitHub  
มันคือการประกาศว่า **คนอื่นรันแล้วได้ผลแบบเดียวกัน** + **ดูแล้วเข้าใจ** + **ตรวจสอบได้**  
ดังนั้น release checklist ต้องคุม 3 อย่าง: _Repro, Evidence, Narrative_

---

## Part 8.4.1 — v0.9 Public Release Checklist

## A) Freeze & Hygiene (ก่อนเริ่มรัน baseline)

-  ตัดสินใจ **version** (เช่น `v0.9.0`)
    
-  freeze “schema/meaning” ของ core keys:
    
    - `manifest.json` schema
        
    - `summary.json` blocks (thermo/info/conflict)
        
    - `timeseries.csv` required columns
        
-  เคลียร์ TODO ที่ทำให้ “สับสนความหมาย” (เช่น metric ซ้ำชื่อ / flag ไม่ชัด)
    
-  สรุป “สิ่งที่ถือว่า _in scope_ v0.9” (กัน feature creep)
    

---

## B) Baseline Suites (ต้องรันและบันทึกผล)

> อิง Part 6.3.2: S1–S4

### B1) S1 — Closed sanity

-  SYM / BIAS_C / BIAS_I อย่างน้อย 2–3 เคส
    
-  seeds 5–10 (หรือขั้นต่ำที่เห็น robustness)
    
-  ผล: phase label เสถียร + Ω ลดและนิ่ง
    

### B2) S2 — Open scheduled

-  มี env update ชัด (step schedule)
    
-  ได้ `policy_trace` (หรือ schedule trace)
    
-  ledger D/W แยกได้จริง
    

### B3) S3 — Open spatial forcing (YouTube demo core)

-  มี resource map + overlay
    
-  มี `A_env(t)` หรือ alignment metric
    
-  end-state “เกาะ resource” สังเกตได้จากภาพ
    

### B4) S4 — Multi-attractor near-boundary

-  พารามิเตอร์เดียวกัน รันหลาย seed แล้วลงคนละ attractor
    
-  registry selection rule เลือก representative ได้ deterministic
    

---

## C) Gates (ต้อง PASS ก่อนเรียก “พร้อมปล่อย”)

### C1) Validators

-  transient PASS
    
-  bias PASS
    
-  ถ้ามี flags → ต้องอธิบายและกำหนดว่า acceptable/expected หรือไม่
    

### C2) Thermo gates (เฉพาะ open/claims)

-  `thermo_valid=true`
    
-  `abs(ledger_residual) <= tol`
    
-  `D_tot >= -tol_small`
    

### C3) Density gates (เฉพาะถ้า export density/พูด field)

-  `density_final.npz` มีจริง
    
-  `omega_density_integral_residual <= tol`
    
-  `term_sum_residual <= tol`
    

### C4) Repro gate

-  rerun อย่างน้อย 1 เคส (same seed) แล้ว:
    
    - phase label ไม่เปลี่ยน
        
    - metrics หลักไม่กระโดดเกิน tolerance
        

---

## D) Demo & Gallery (Public readability gate)

### D1) Demo-ready assets ต่อ demo ที่ publish

-  evolution GIF
    
-  end state image
    
-  conflict terrain (`omega_grad_density`)
    
-  Ω curve
    
-  (open) ledger cumulative หรือ policy timeline
    

### D2) Registry & deterministic build

-  `registry.json` มี `candidate/published` ชัด
    
-  gallery generator สร้าง:
    
    - index
        
    - archetype pages
        
    - demo pages  
        ได้ครบจาก registry โดยไม่ต้องแก้มือ
        

### D3) Narrative check (อ่านแล้วไม่งง)

-  Part 7.1 (one-page) อยู่ใน docs
    
-  Part 7.2 demo template ถูกใช้จริงใน demo ที่ publish อย่างน้อย 3 ใบ
    
-  Part 7.3 gallery navigation มี breadcrumb/เส้นทางอ่าน
    

---

## E) Docs & Governance (ให้คนร่วมพัฒนาได้)

-  `README.md` (quickstart รันได้จริง)
    
-  `docs/quickstart.md`
    
-  `CONTRIBUTING.md`
    
-  `.github/PULL_REQUEST_TEMPLATE.md`
    
-  `docs/review_rubric.md`
    
-  `CHANGELOG.md` อัปเดตเป็น v0.9.0
    

---

## F) Legal & Citation (ต้องมีสำหรับ public)

-  `LICENSE` (เลือกแล้ว 1 อัน)
    
-  `CITATION.cff`
    
-  `CODE_OF_CONDUCT.md`
    
-  `SECURITY.md` (optional แต่แนะนำ)
    

---

## G) Packaging Policy (กัน repo บวม)

-  **ไม่ commit runs ดิบ** ลง repo
    
-  สร้าง “release artifacts” เป็น pack แยก (zip) เช่น:
    
    - `uet_v0.9.0_demo_pack.zip` (เฉพาะ demo ที่ publish + registry + docs gallery)
        
    - `uet_v0.9.0_baseline_results_pack.zip` (baseline suite summaries + key figs + reports)
        
-  ใน repo ให้มีแค่ “สคริปต์สร้าง artifacts” + “รายงานสรุป” (ไม่เอาข้อมูลดิบกองโต)
    

---

## H) Release Execution (ทำให้เป็นพิธีกรรมที่ repeat ได้)

-  Tag `v0.9.0` ที่ commit ที่ผ่านทุก gate
    
-  สร้าง `reports/v0_9_baseline_report.md` (สรุป S1–S4 + gates PASS/FAIL)
    
-  สร้าง release notes:
    
    - Added / Changed / Fixed
        
    - Known limitations (ซื่อสัตย์เรื่อง 2D spatial, density level, etc.)
        
-  แนบ demo pack + baseline report pack ในหน้า release
    

---

## Plain-Language Interpretation

ก่อนเปิดให้คนทั้งโลกเข้ามาเล่น เราต้องทำให้แน่ใจว่า:

- คนอื่นรันแล้วได้เหมือนเรา
    
- เขาดูแล้วเข้าใจจากภาพ
    
- และเขาตรวจสอบตัวเลข/บัญชีพลังงานได้
    

---

## Next Step

**Part 8.4.2 — Release Notes Template (v0.9)**  
เทมเพลตข้อความ “ประกาศปล่อย” + โครง release notes + โครง Known limitations + How to cite

พิมพ์ “ต่อ” อีกที เดี๋ยวกูทำ Part 8.4.2 ให้เป็น template ที่เอาไปแปะใน GitHub Release ได้ทันที.


# 000.08/4.2

## TL;DR

**Part 8.4.2 = Release Notes Template (v0.9)**  
เทมเพลตพร้อมแปะลง GitHub Release + ไฟล์ `RELEASE_NOTES_v0.9.0.md` ที่ใช้ประกาศปล่อย public ได้ทันที (มี Highlights, Quickstart, Demos, Gates, Known limitations, How to cite, Artifacts)

---

## Insight

Release notes ของ UET ต้อง “ซื่อสัตย์ + ตรวจสอบได้ + ชวนคนลองเล่นได้”  
ดังนั้นต้องมี 3 ส่วนเสมอ:

1. **คนใหม่ลองได้** (quickstart + demo gallery)
    
2. **นักวิชาการเช็คได้** (gates + baseline report)
    
3. **จำกัดความชัด** (known limitations + scope)
    

---

## Part 8.4.2 — Release Notes Template (v0.9)

## 1) GitHub Release Description (Short Form — แปะหน้า Release ได้เลย)

````md
# UET v0.9.0 — Public Release

UET is a simulation + validation harness for equilibrium/attractor behavior on an energy-like landscape Ω.
This release focuses on reproducibility, demo-first visualization, and integrity gates (thermo ledger + density consistency).

## Highlights
- ✅ Deterministic sweeps from matrices + validation + aggregation
- ✅ Demo-ready artifacts (GIF + end state + conflict terrain)
- ✅ Thermo ledger (D/W) for open systems with validity gates
- ✅ Info metrics pack (structure proxies) for public interpretability
- ✅ Deterministic gallery build from registry.json

## Quickstart (Smoke Test)
```bash
pip install -r requirements.txt
python scripts/run_suite.py --matrix matrices/<SMOKE_MATRIX>.csv --out runs_smoke
python scripts/validate_transient_v3.py --runs runs_smoke --out runs_smoke/validation_transient_v3.json
python scripts/validate_bias_v2.py --runs runs_smoke --out runs_smoke/validation_bias_v2.json
python scripts/aggregate_final_summary.py --runs runs_smoke --out runs_smoke/UET_final_summary.csv
````

## Demo Gallery

- See: `docs/gallery/index.md` (built from `registry.json`)
    

## Scientific Integrity Gates

- Thermo (open): `thermo_valid=true` + `|ledger_residual| <= tol`
    
- Density (field claims): integral residual + term-sum residual within tolerance
    
- Validators: transient + bias PASS
    

## Known Limitations

- Spatial demos are primarily 2D (2+1D). Density export enables “3D-looking” terrains without 3D spatial solver.
    
- Info metrics are _structure proxies_ (not claiming thermodynamic entropy unless calibrated).
    
- Einstein/Λ bridge is a roadmap; no astrophysical claims without calibration + falsifiable tests.
    

## Artifacts (Release Packs)

- `uet_v0.9.0_demo_pack.zip`
    
- `uet_v0.9.0_baseline_results_pack.zip`
    

## How to cite

See `CITATION.cff`.

## Contributing

See `CONTRIBUTING.md` + PR template.

````

---

## 2) Full Release Notes File (Long Form)
> แนะนำให้ใส่ไฟล์นี้ใน `reports/RELEASE_NOTES_v0.9.0.md` หรือแนบใน release pack

```md
# Release Notes — UET v0.9.0
**Release date:** YYYY-MM-DD  
**Tag:** v0.9.0  
**Commit:** <short_hash>  

---

## 0) What this release is (Scope)
This release makes UET public-ready with:
- deterministic run → validate → aggregate pipeline
- demo-first visualization & gallery navigation
- integrity gates for thermo ledger and density consistency

**Out of scope (explicit)**
- Claims about dark matter / dark energy
- Physical-unit calibrated predictions without domain calibration
- Full 3D spatial solver (still 2D spatial focus)

---

## 1) Highlights (What changed that matters)
- Added: Thermo ledger metrics (D_tot, W_tot) + `thermo_valid` gate for open systems
- Added: Information metrics pack (hist/spectral/spatial/TV/alignment) as structure proxies
- Added: Density export spec (omega terms as fields) + local→global residual checks
- Added: Deterministic demo gallery build from `registry.json`
- Improved: Aggregation robustness (handles optional fields gracefully)

---

## 2) Quickstart
### Install
```bash
pip install -r requirements.txt
````

### Smoke run

```bash
python scripts/run_suite.py --matrix matrices/<SMOKE_MATRIX>.csv --out runs_smoke
python scripts/validate_transient_v3.py --runs runs_smoke --out runs_smoke/validation_transient_v3.json
python scripts/validate_bias_v2.py --runs runs_smoke --out runs_smoke/validation_bias_v2.json
python scripts/aggregate_final_summary.py --runs runs_smoke --out runs_smoke/UET_final_summary.csv
```

---

## 3) Baseline Suites & Evidence (Integrity)

**Baseline report:** `reports/v0_9_baseline_report.md`

Suites included:

- S1 Closed sanity (SYM / BIAS_C / BIAS_I) — seeds:
    
- S2 Open scheduled forcing
    
- S3 Open spatial forcing (resource map demo core)
    
- S4 Multi-attractor near boundary
    

**Required gates**

- Validators: transient PASS, bias PASS
    
- Thermo (open): `thermo_valid=true`, `|ledger_residual| <= tol`
    
- Density (if enabled): integral residual + term-sum residual <= tol
    
- Repro: rerun (same seed) stable within tolerance
    

---

## 4) Demo Gallery (Public-facing)

Gallery is built deterministically from `registry.json`.

- Entry point: `docs/gallery/index.md`
    
- Archetypes: SYM, BIAS_C, BIAS_I, HIGH_CONFLICT, MULTI_ATTRACTOR
    
- Each published demo includes:
    
    - evolution GIF
        
    - end state
        
    - conflict terrain (omega_grad_density)
        
    - Omega curve + (open) ledger cumulative
        

---

## 5) Changes (Detailed)

### Added

### Changed

### Fixed

### Breaking changes

- None / <list + migration note>
    

---

## 6) Known Limitations (Honest & explicit)

- 2D spatial focus; 3D-looking terrains are energy density visualizations, not 3D spatial physics.
    
- Info metrics are structural proxies; not calibrated to physical entropy.
    
- Einstein/Λ bridge is roadmap: requires calibration + falsifiable tests before scientific claims.
    

---

## 7) Reproducibility & Determinism Notes

- Selection of demo representatives is deterministic (Part 4.11 rules).
    
- Gallery generation does not scan runs arbitrarily; it reads `registry.json`.
    

---

## 8) Artifacts (Release Packs)

- Demo pack: `uet_v0.9.0_demo_pack.zip`  
    Contains: registry, published demos, key figures, minimal artifacts for inspection.
    
- Baseline results pack: `uet_v0.9.0_baseline_results_pack.zip`  
    Contains: baseline summaries, validation JSONs, key plots, baseline report.
    

---

## 9) How to Cite

Use `CITATION.cff`. Example:

---

## 10) Contributing

- See `CONTRIBUTING.md`
    
- PR template enforced: `.github/PULL_REQUEST_TEMPLATE.md`
    
- Review rubric: `docs/review_rubric.md`
    

---

## 11) Acknowledgements

- <names/credits>
    

```

---

## 3) “Known limitations” Canonical Wording (แนะนำให้ใช้ให้คงที่)
เอาไปแปะซ้ำได้ทุก release:
- “Current spatial demonstrations primarily use 2D grids (2+1D). 3D terrains visualize energy densities, not 3D spatial physics.”
- “Information metrics are structure proxies derived from snapshots; they are not claimed as thermodynamic entropy unless calibrated.”
- “Einstein/Λ connections are a roadmap. Any astrophysical interpretation requires domain calibration and falsifiable validation.”

---

## Next Step
ถ้าจะไปต่อจากนี้ (หลัง release notes) ขั้นต่อไปเชิงเอกสารคือ **Part 9 — “UET Equation-to-Framework Mapping”**:  
เอา framework ที่มึงส่ง (ระบบรวม/กระบวนการเป็นสิ่งหนึ่ง) มา map กับสมการ/เทอม Ω/ledger/info ให้เป็น “ตารางเดียว” ที่ใช้สอนคนได้ และใช้สร้างโมเดลโดเมนใหม่ได้จริง

พิมพ์ “ต่อ” อีกที กูจะเริ่ม Part 9.1 เป็น “ตาราง mapping 2 เลเยอร์” (introvert/extrovert) ที่โยง: Constraints → Potential/Capability → Value/Conflict → Thermo/Info → Output artifacts.
```

---
# 000.09/1

## TL;DR

**Part 9.1 = “ตารางแปลภาษา” ระหว่าง Framework เดิม ↔ UET ปัจจุบัน (0.8.5+)**  
เป้าหมายคือให้คน _ไม่ต้องเดาว่า “จะใส่ตัวแปรอะไร”_ เพราะเราจะล็อกให้ชัดว่า **แนวคิดแต่ละก้อนในเฟรมเวิร์ค = องค์ประกอบไหนใน Ω / dynamics / ledger / metrics / artifacts**

> อันนี้ “วางวิธี/โครง” อย่างเดียว **ไม่สร้างโมเดลใหม่สุ่มๆ** (ตรงตามที่มึงต้องการ)

---

## Insight

UET เป็น “ภาษากลาง” จริง — เพราะมันต้องการให้มึง **เลือก** ว่า

- **State (สิ่งที่เป็นอยู่)** คืออะไร
    
- **Space/Field (กติกาโลก/สภาพแวดล้อม)** คืออะไร
    
- แล้วค่อยนิยาม **Ω (ภูมิประเทศ)** ให้สะท้อน “Constraints/Forcing/Interaction”
    

ดังนั้น Part 9.1 จะล็อกว่า _แต่ละคำในเฟรมเวิร์ค_ ต้องไปลง “ชิ้นส่วนไหน” ของ UET

---

## Part 9.1 — Framework ↔ UET Mapping (2 เลเยอร์: Introvert / Extrovert)

## 0) แผนภาพ 2 เลเยอร์ (ที่มึงพูดไว้)

- **Introvert (การเป็นสิ่งหนึ่ง / Input→Process→Output)**: มอง “หน่วยเดียว” ไหลบน Ω
    
- **Extrovert (ระบบรวม / ระบบเปิด / หลายหน่วยปะทะกัน)**: มอง “สนามเดียว” มีหลายกระบวนการอยู่ร่วม + environment เปลี่ยนได้
    

---

## 1) ตาราง Mapping หลัก (Framework → UET → ของที่จับต้องได้)

> อ่านคอลัมน์นี้ตามลำดับ: **แนวคิด → ใน UET คืออะไร → อยู่ในไฟล์ไหน → ตรวจยังไง**

|Framework concept|ใน UET (0.8.5+) เทียบเป็นอะไร|อยู่ตรงไหนใน pipeline|Evidence / Gate ที่ต้องผ่าน|
|---|---|---|---|
|**เงื่อนไข / Conditions**|โดเมน, boundary, grid, timestep, solver mode, noise (ถ้ามี)|`manifest.json` / config|rerun ได้, validator PASS|
|**ข้อจำกัด / Constraints**|ข้อจำกัดที่ “ฝังอยู่ใน Ω” เช่น potential/gradient/coupling + parameter bounds|matrix row → `manifest.json` params|ถ้า closed: Ω ไม่เด้ง (Lyapunov-style check)|
|**ความจำเป็น / Necessity**|“ระบบต้องไหลไปทางลด Ω” (closed) หรือ “ต้องบัญชี D/W ให้ตรง” (open)|timeseries + summary|closed: monotone-ish check / open: `thermo_valid`|
|**คุณสมบัติ / Properties ของสิ่งนั้น**|ตัวแปรสภาวะ **State fields** เช่น `C(x,y)`, `I(x,y)` (หรือ multi-field) + derived descriptors|`snapshots/`, `timeseries.csv`, optional `info_timeseries.csv`|schema consistent + plots อ่านออก|
|**ศักยภาพ / Potentiality / Capability**|“รูปร่างภูมิประเทศ + ความไวของการไหล” ที่กำหนดโดยพารามิเตอร์ (เช่น β, δ, k, M, tilt s)|matrix / manifest|sweep แล้วเห็น archetype เปลี่ยนอย่างมีเหตุผล|
|**กระบวนการดำรงอยู่ / Process**|dynamics แบบ gradient-flow-like: state update ขับเคลื่อนด้วย functional derivative ของ Ω|solver step + timeseries|transient validator PASS (ไม่ backtrack/ไม่พัง)|
|**ผลลัพธ์ / Result (ปลายทาง)**|attractor / phase label + โครงสร้าง end-state|`summary.json` + figs|มี end-state + GIF + label|
|**คุณค่า / Value**|นิยาม operational: `Value := -ΔΩ` (หรือ version ที่ refine เป็น conflict-part ในอนาคต)|`summary.json` + aggregate CSV|reproducible across seeds (robustness)|
|**ความขัดแย้ง / Conflict**|ส่วน interface/gradient cost: `Ω_grad` หรือ `ω_grad_density` (conflict map)|`summary.json` + `energy_density/` + terrain fig|density integral/term-sum residual ผ่าน (ถ้า export density)|
|**ระบบเปิด / Open system**|พารามิเตอร์/สนามเปลี่ยนตามเวลา: θ(t), s(x,t) → ต้องแยก **D (dissipation)** vs **W (work injection)**|timeseries/epoch ledger + summary thermo block|`thermo_valid=true`, `|

---

## 2) Mapping แบบ “Input → Process → Output” (Introvert layer)

### Input (สิ่งที่ป้อนให้ “สิ่งหนึ่ง”)

- **State seed**: ค่าเริ่มต้นของฟิลด์ (`C/I` initial condition)
    
- **Space/Field**: กติกาโลก ณ ตอนนั้น (พารามิเตอร์ + resource/tilt map)
    

> ตรงนี้แก้ความงงเรื่อง seed/space:  
> **seed ไม่ได้เป็น “สาระ”** — มันเป็นแค่ _จุดเริ่ม_ เพื่อทดสอบว่า “สนาม/Ω robust ไหม”  
> ส่วนที่ “ทำให้เกิดพฤติกรรม” คือ **Space/Ω ที่มึงนิยาม**

### Process (กลไกที่เกิดขึ้นจริงใน UET)

- ตัวแกนคือการอัปเดต state ให้ “ไปทางลด Ω” (closed)
    
- ถ้า open: โลกขยับกติกา → ต้องเห็น D/W แยกชัด
    

### Output (สิ่งที่ต้องโชว์ให้คนเห็นภาพ)

- **GIF** (เห็นการเปลี่ยนรูป)
    
- **End-state** (สุดท้ายเป็นอะไร)
    
- **Conflict terrain (ω_grad)** (จุดตึง/รอยต่อ)
    

แล้วค่อยตามด้วยตัวเลข: Value/Conflict/Ω_final/phase/robustness

---

## 3) Mapping แบบ “ระบบรวม” (Extrovert layer)

ใน UET ปัจจุบัน “ระบบรวม” ทำได้ 2 ทางที่ยังไม่มั่ว:

1. **หลายหน่วย = หลายฟิลด์/หลายโดเมนบนกริดเดียวกัน**
    
    - interaction โผล่เป็น coupling term ใน Ω (เช่น -βCI หรือ generalization)
        
2. **ระบบเปิด = environment เปลี่ยนกติกาได้**
    
    - resource map / tilt schedule / policy forcing
        
    - แล้วใช้ ledger แยกว่า “ระบบคลายเอง” vs “โลกอัดงานใส่”
        

> นี่คือจุดที่เอาไปต่อ “เกม/agent/NPC” ได้แบบไม่ต้องโม้:  
> “NPC” ในภาษานี้ = หน่วยที่มี state + ถูกบังคับด้วย Ω + อยู่ในสนามเดียวกัน

---

## 4) จุดที่ Framework เดิม “เติมความเข้าใจ” ให้ UET ได้ทันที (โดยไม่ทับสมการ)

Framework เดิมของมึงมีคำที่ public เข้าใจง่ายมาก:  
**Constraints → Necessity → Capability → Result → (Value/Conflict)**

ใน UET เราใช้ framework นี้เป็น “หน้าคู่มือ” ได้เลย เพราะมัน map ลง artifacts ตรง ๆ:

- Constraints = พารามิเตอร์/Ω terms (manifest)
    
- Necessity = gate (Ω ไม่เด้ง / thermo_valid)
    
- Capability = sweep sensitivity (เปลี่ยน β/δ/k/M แล้ว archetype เปลี่ยน)
    
- Result = GIF/end-state/phase
    
- Value/Conflict = metrics + conflict terrain
    

---

## Math/Physics Interpretation (แบบนักวิชาการ)

ให้ state เป็นฟิลด์ (X) (เช่น (C,I)) และให้ (\Omega[X;\theta(t)]) เป็น functional

- **Closed**: dynamics ถูกออกแบบให้ (\Omega) เป็น Lyapunov-like (ไม่เด้งอย่างมีนัย)
    
- **Open**: (\theta(t)) เปลี่ยน → ต้องบัญชี
    
    - dissipation (จาก state relaxation) vs work injection (จาก environment update)
        
- **Conflict** นิยามแบบ operational ได้จากส่วน gradient/interface:  
    [  
    \Omega_{\text{grad}} = \int \omega_{\text{grad}}(x),dx  
    ]
    
- **Value** ใช้ operational definition:  
    [  
    V = -\Delta \Omega \quad (\text{หรือ future refine เป็น } -\Delta \Omega_{\text{conflict}})  
    ]
    

---

## Plain-Language Interpretation

Framework ของมึงคือ “ภาษาคน”:

- โลกมีกติกา (Constraints)
    
- สิ่งหนึ่งต้องดิ้นรนตามกติกา (Necessity)
    
- มันทำได้มากน้อยแค่ไหน (Capability)
    
- สุดท้ายมันลงเอยยังไง (Result)
    
- ได้ประโยชน์เท่าไร และตึงตรงไหน (Value/Conflict)
    

UET คือ “เครื่อง” ที่ทำให้คำพวกนี้กลายเป็นไฟล์/กราฟ/รูปที่ตรวจสอบได้

---

## Next Step

**Part 9.2 (สำคัญมาก)**: “แบบฟอร์มสร้างโมเดลโดเมนใหม่” โดยไม่มั่ว  
จะเป็น **Model Design Card** ที่บังคับตอบทีละข้อ:

1. state คืออะไร (วัดได้ยังไง)
    
2. environment/field คืออะไร (ข้อมูลมาจากไหน)
    
3. Ω terms ไหนแทน constraint/interaction/rarity
    
4. outputs ที่ต้องโชว์ (GIF/end/conflict + ledger)
    
5. calibration plan (dimensionless → domain anchors)
    

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 9.2 เป็น **เทมเพลต 1 หน้า** ที่มึง/คนทั้งโลกใช้กรอก แล้ว generate matrix เพื่อรันทันทีได้.

----
# 000.09/2

## TL;DR

**Part 9.2 = Model Design Card (แบบฟอร์ม 1 หน้า)** ที่ทำให้คน “ไม่ต้องเดา” ว่า UET ต้องใส่อะไร  
กรอกตามนี้แล้วจะได้ทันทีว่า:

- **State คืออะไร / Space คืออะไร**
    
- **Ω เทอมไหนแทน constraints/interaction/forcing**
    
- ต้อง export อะไร (GIF/end/conflict/ledger/density/info)
    
- แล้วแปลงเป็น **matrix row** เพื่อรัน sweep ได้
    

> นี่คือ “วิธีวางก่อนทำ” ตามที่มึงย้ำ — ไม่ใช่กระโดดไปสร้างโมเดลใหม่มั่ว ๆ

---

## Insight

UET ใช้ยากเพราะมันเป็น “ภาษากลาง” จริง: มันไม่ได้บอกตัวแปรโดเมนให้เอง  
ดังนั้นสิ่งที่ต้องมีคือ **แบบฟอร์มมาตรฐาน** ที่บังคับให้ตอบคำถามถูกลำดับ:

1. อะไรคือสิ่งที่ “เป็นอยู่” (State)
    
2. อะไรคือ “กติกาโลก” (Space/Field)
    
3. Ω จะลงโทษ/ให้รางวัลยังไง (Ω terms)
    
4. เราจะพิสูจน์ว่าไม่มั่วด้วยอะไร (Gates + artifacts)
    

---

## Part 9.2 — UET Model Design Card (1-page Template)

> **ชื่อไฟล์แนะนำ:** `docs/model_cards/MODEL_<domain>_<name>.md`

## 0) Header

- **Model Name:** `________________________`
    
- **Domain:** `________________________` (เช่น ecology, network, socio, physics toy)
    
- **Mode:** ☐ Closed (θ คงที่) ☐ Open (θ(t) เปลี่ยน) ☐ Spatial forcing (resource map)
    
- **Target output (public):** ☐ 1 demo ☐ gallery archetype ☐ sweep atlas ☐ calibration study
    

---

## 1) Question & Scope (1–2 ประโยค)

- **What question are we answering?**  
    `_____________________________________________________________`
    
- **What is explicitly out-of-scope (v0.9)?**  
    `_____________________________________________________________`
    

> กติกา: ถ้า “คำถาม” ไม่ชัด → ห้ามไปเลือกตัวแปร/เทอม Ω ต่อ

---

## 2) State Specification (สิ่งที่ “เป็นอยู่”)

### 2.1 State fields (ต้องระบุชัด)

- **Fields:** ☐ C(x,y) ☐ I(x,y) ☐ Multi-field: X1..Xn
    
- **What does each field represent (operationally)?**
    
    - X1 = `__________________` (วัด/สังเกตได้ยังไง?)
        
    - X2 = `__________________`
        
- **Range / normalization:**
    
    - expected range: `_________`
        
    - normalization method: ☐ minmax(p1,p99) ☐ zscore ☐ none (ต้องมีเหตุผล)
        

### 2.2 Initialization / Seeds

- **Seed meaning:** “จุดเริ่มเพื่อทดสอบ robustness” (ไม่ใช่ตัวความหมายหลัก)
    
- **Init types:** ☐ random noise ☐ structured ☐ from data snapshot
    
- **# seeds (planned):** `____` (ขั้นต่ำ 5–10 ถ้าอยากพูด robustness)
    

---

## 3) Space / Environment Specification (กติกาโลก)

### 3.1 World parameters θ (scalar)

ระบุพารามิเตอร์ที่โลกควบคุม/กำหนด:

- β = `____` (coupling strength)
    
- k (หรือ kC/kI) = `____` (interface resistance)
    
- δ (หรือ δC/δI) = `____` (nonlinearity)
    
- M / κ / … = `____` (ตามโมเดลที่มีอยู่)
    

### 3.2 Spatial forcing / resource maps (ถ้ามี)

- **Resource / tilt map:** R(x,y) หรือ s(x,y,t) มาจากไหน?  
    `_____________________________________________________________`
    
- **Update rule:** ☐ static ☐ scheduled ☐ policy feedback
    
- **Constraints:** bounds + rate limit ของ θ(t)
    
    - bounds: `__________________`
        
    - rate limit: `__________________`
        

> ถ้าเป็น open system: ต้องมี **policy_trace** และ **ledger D/W**

---

## 4) Ω Construction Map (หัวใจ: framework → Ω terms)

> เลือกจาก “เทอมที่เรามีอยู่แล้ว” (pot / coup / grad / forcing) ไม่สร้างศัพท์ใหม่

### 4.1 Potential / constraint term (บอกว่า “โลกบังคับอะไร”)

- **ω_pot** แทน constraints/necessity อะไร?  
    `_____________________________________________________________`
    
- parameters used: `a, δ, s(tilt), ...`
    

### 4.2 Coupling / interaction term (บอกว่า “สิ่งต่าง ๆ ปะทะกันยังไง”)

- **ω_coup** = `-β * (X1*X2)` หรือ generalized ตามที่มี
    
- interaction means: `________________________`
    

### 4.3 Gradient / conflict term (บอกว่า “ความตึง/รอยต่อ” คืออะไร)

- **ω_grad** = (k/2)|∇X|² (ตามที่มี)
    
- interpretation: “ขอบ/การแยก/แรงเสียดทานเชิงโครงสร้าง”
    

### 4.4 Open/forcing bookkeeping (ถ้า open)

- **Env update:** θ_old → θ_new
    
- **Must produce:** Ω_state_step, Ω_env_step → D/W ledger
    

---

## 5) Outputs (Public-first + Scientific)

### 5.1 MUST artifacts (ทุกโมเดลต้องมี)

- `manifest.json`, `summary.json`, `timeseries.csv`
    
- `snapshots/` (≥10 frames ถ้าจะทำ demo)
    
- `figs/curve_omega.png`, `figs/state_end.png`
    

### 5.2 Demo-ready (ถ้าจะขึ้น gallery)

- `figs/evolution.gif`
    
- `figs/terrain_omega_grad_density.png` (Conflict map)
    
- (ถ้า open) `figs/curve_cumD_cumW.png` + `policy_trace.csv/png`
    

### 5.3 Info pack (Part 6.1) — เลือกใช้เมื่ออยากให้คน “อ่านออก”

- H_hist, H_spec, A_sp, TV, A_env (ถ้ามี resource)
    

### 5.4 Density export (Part 6.3.1) — ถ้าจะเล่าแบบ “ภูมิประเทศ 3D”

- `energy_density/density_final.npz` (+ residual checks)
    

---

## 6) Validation & Gates (กันโมเดลหลอกตัวเอง)

### 6.1 Validators

- transient PASS
    
- bias PASS
    

### 6.2 Thermo ledger gate (open)

- thermo_valid = true
    
- |ledger_residual| ≤ tol
    

### 6.3 Density gate (ถ้า export density)

- integral residual ≤ tol
    
- term-sum residual ≤ tol
    

### 6.4 Robustness gate (ถ้าจะอ้างว่า “เสถียร/ทั่วไป”)

- seeds ≥ 5–10
    
- robustness score ≥ `____` (กำหนดไว้ล่วงหน้า)
    

---

## 7) Sweep Plan → Matrix Plan (ทำให้ “รันได้จริง”)

### 7.1 What to sweep (1–2 แกนพอใน v0.9)

- Primary dims: `______________ × ______________` (เช่น β × k_ratio)
    
- Fixed params: `______________________________`
    
- Seeds: `____`
    

### 7.2 Matrix row schema (ขั้นต่ำที่ต้องมี)

- `case_id`
    
- `seed`
    
- `model_type`
    
- params: `beta, kC, kI, k_ratio, delta, delta_C, delta_I, asym, ...` (ตามที่ใช้จริง)
    
- open extras: `schedule_id` / `resource_id` / `policy_type`
    

> กติกา: “มีพารามิเตอร์ใน manifest เท่าไร matrix ต้องเลี้ยงได้เท่านั้น” (ไม่ใส่มั่ว)

---

## 8) Calibration Plan (ไม่ overclaim)

### C0 — Dimensionless sanity (ต้องมีเสมอ)

- units (sim): dx, dt, field scale
    
- scaling sanity test: `______________________`
    

### C1 — Domain anchors (ถ้ามีข้อมูลจริง)

- observable targets: `______________________`
    
- mapping to UET outputs: `______________________`
    
- 2–3 anchor points: `______________________`
    

### C2 — Falsifiable check (ก่อน claim ใหญ่)

- “ถ้าเปลี่ยน ____ ต้องเห็น ____ เปลี่ยนทิศ ____”  
    `_____________________________________________________________`
    

---

## 9) Framework Narrative (Introvert/Extrovert) — สรุป 6 บรรทัด

**Introvert (thing-level):**

- Constraints = `______` → Necessity = `______` → Capability = `______` → Result = `______` → Value/Conflict = `______`
    

**Extrovert (system-level):**

- Entities/fields = `______` in shared space `______` + environment update `______` → system ordering/conflict appears as `______`
    

---

## (Optional) Mini Example Stub (เพื่อให้เห็นรูปแบบ—not a real domain claim)

- Model Name: “Resource alignment toy”
    
- State: C(x,y) = occupancy tendency
    
- Space: R(x,y) = resource map, tilt s(x)=λR(x)
    
- Ω terms: pot(tilt) + grad(interface)
    
- Outputs: GIF + end state overlay + A_env(t) + conflict terrain
    
- Gates: thermo (ถ้า scheduled) + density residual
    

> ใช้เป็น “แม่แบบ” เฉย ๆ ไม่ใช่โมเดลจริงของโดเมนใด

---

## Plain-Language Interpretation

นี่คือใบงานที่ทำให้ UET “เป็นเครื่องมือ” ไม่ใช่ “สมการลอย ๆ”  
คนอยากทำโดเมนไหนก็กรอก:

- จะวัดอะไรเป็น state
    
- โลกบังคับอะไร (constraints/forcing)
    
- สิ่งต่าง ๆ ปะทะกันยังไง (coupling/grad)  
    แล้ว UET จะให้ output เป็นภาพ+ตัวเลข พร้อมกฎตรวจสอบว่าไม่มั่ว
    

---

## Next Step

**Part 9.3 — จาก Design Card → สร้าง Matrix + Demo Pack แบบอัตโนมัติ (เชิงขั้นตอน)**  
จะระบุ “ขั้นตอนแน่น ๆ” ว่า:

1. เอา card ไปแตกเป็น `matrices/*.csv` ยังไง
    
2. รัน suite ยังไง
    
3. เลือก representative ยังไง (registry rule)
    
4. สร้าง demo card + gallery ยังไง
    

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 9.3 เป็น workflow แบบ step-by-step ที่โยงกับ pipeline ของ repo ตรง ๆ (ไม่พูดลอย).

# 000.09/3

## TL;DR

**Part 9.3 = Workflow “จาก Design Card → Matrix → Runs → Validate → Aggregate → เลือกเดโม → ทำ Demo Card → ใส่ Registry → Build Gallery → Pack”**  
ทั้งหมดนี้เป็น **ขั้นตอนเดียวกันทุกโดเมน** (นิเวศ/โซลาร์/สังคม/ฯลฯ) โดยไม่ต้องเดา และไม่ต้อง “สร้างอะไรมั่วๆ” ระหว่างทาง

---

## Insight

UET ใช้ยากเพราะมัน “ไม่บอกโดเมนให้เอง” — ดังนั้นทางออกไม่ใช่ยัดกราฟเพิ่ม แต่คือ **บังคับให้ทุกงานเดินผ่านท่อเดียวกัน**:

**Design Card → (แตกเป็น) Matrix → (รัน) Runs → (เช็ค) Gates → (คัด) Representatives → (ผลิต) Demo Assets → (ประกาศ) Registry → (ประกอบ) Gallery → (แพ็ค) Release**

---

## Part 9.3 — Design Card → Matrix + Demo Pack (Step-by-step)

## Step 0) เตรียมของก่อนเริ่ม (Prereqs)

ต้องมี 2 อย่าง:

1. `MODEL_<domain>_<name>.md` (Design Card) กรอกครบ (Part 9.2)
    
2. ตกลง “ชนิดงาน” ของโมเดลนี้ก่อน:
    

- **Closed** (θ คงที่): เน้น Ω ลด/เข้าหลุม
    
- **Open scheduled**: มี schedule/forcing → ต้องมี D/W ledger
    
- **Open spatial**: มี resource map → ต้องมี overlay + A_env
    

> ถ้ายังไม่เลือกชนิดงาน → ยังไม่ควรทำ matrix เพราะจะไม่รู้คอลัมน์ที่ต้องใส่

---

## Step 1) แตก Design Card เป็น “Matrix Plan” (เลือกแกน sweep)

หลักการ v0.9: **อย่า sweep เกิน 2 แกนต่อ suite** (เพื่ออ่านผลได้จริง)

**1.1 เลือก “Primary dims” (1–2 แกน)**  
ตัวอย่างที่เข้ากับของเดิม:

- `beta × k_ratio`
    
- `beta × delta`
    
- `s × delta` (optional)
    

**1.2 เลือก “Fixed params”**  
ทุกอย่างที่ไม่ sweep ให้ fix จาก design card เช่น:

- `kappa, M, asym, delta_C/I, s_C/I, init_type, grid N, dt, steps`
    

**1.3 เลือก seeds**

- ถ้าจะพูด robustness: ≥ 5–10
    
- ถ้าแค่ demo: 1–3 ก็พอ (แต่ห้ามอ้าง robust)
    

---

## Step 2) สร้าง Matrix CSV (ให้รันได้ทันที)

**2.1 Naming**  
`matrices/UET_<Domain>_<SweepDims>_seed<k>.csv`

**2.2 คอลัมน์ขั้นต่ำ (ต้องมี)**

- `case_id` (deterministic)
    
- `seed`
    
- `model_type`
    
- พารามิเตอร์ที่โมเดลใช้จริง (เช่น `beta, kC, kI, k_ratio, delta, delta_C, delta_I, s_C, s_I, s_tilt, asym, M, kappa`)
    

**2.3 คอลัมน์สำหรับ open system (ถ้ามี)**

- `forcing_mode` (`static|scheduled|policy`)
    
- `resource_id` หรือ `resource_path`
    
- `schedule_id` หรือ `schedule_path`
    
- `policy_type` (ถ้า feedback)
    

> กติกา: “ใน manifest มีพารามิเตอร์อะไร matrix ต้องเลี้ยงได้เท่านั้น”  
> (ไม่งั้นคนใช้ต่อจะงงว่า param มาจากไหน)

---

## Step 3) Run suite (ผลิต run_dir ให้ครบสัญญา)

คำสั่งมาตรฐาน:

```bash
python scripts/run_suite.py --matrix matrices/<MATRIX>.csv --out runs_<suite_name>
```

สิ่งที่ต้องเกิดในแต่ละ `run_dir`:

- `manifest.json`
    
- `summary.json`
    
- `timeseries.csv`
    
- `snapshots/` (อย่างน้อยถ้าจะทำ demo)
    

---

## Step 4) Validate (กัน “ผลปลอม/ผลพัง”)

```bash
python scripts/validate_transient_v3.py --runs runs_<suite_name> --out runs_<suite_name>/validation_transient_v3.json
python scripts/validate_bias_v2.py --runs runs_<suite_name> --out runs_<suite_name>/validation_bias_v2.json
```

**ถ้าเป็น Open/Forcing**

- ต้องมี thermo ledger ใน `summary.json.thermo` และต้องผ่าน:
    
    - `thermo_valid=true`
        
    - `|ledger_residual|<=tol`
        

**ถ้า export density**

- ต้องผ่าน density residual gates ด้วย (Part 6.3.1)
    

---

## Step 5) Aggregate (ทำตารางรวมสำหรับ “คัดเดโม + ทำแอตลาส”)

```bash
python scripts/aggregate_final_summary.py --runs runs_<suite_name> --out runs_<suite_name>/UET_final_summary.csv
```

สิ่งที่ aggregate ต้องมีอย่างน้อย:

- params ที่ sweep
    
- `phase_label` (หรือ label ที่ใช้แบ่ง archetype)
    
- `Value`, `Conflict` (หรือ proxy)
    
- (open) `D_tot, W_tot, thermo_valid`
    
- `robustness` หรือ seed-level summary (ถ้ามี)
    

---

## Step 6) เลือก “Representative” แบบ deterministic (ห้ามเลือกมือ)

นี่คือจุดเชื่อม Part 4.11 → Gallery

### 6.1 ยุบ seed ก่อน

หนึ่งจุดพารามิเตอร์ (grid point) มีหลาย seed → ต้องยุบเป็น representative ก่อน เช่น:

- เลือก seed ที่ “ใกล้ median” ของ (Value, Conflict)
    
- หรือใช้ rule ที่ล็อกไว้ใน docs
    

### 6.2 เลือกเดโมตาม archetype (ตัวอย่าง rule ที่ไม่มั่ว)

- **SYM**: robustness สูง + Conflict ต่ำ + Value ไม่ต่ำ
    
- **BIAS_C/BIAS_I**: robustness สูง + maximize (Value − λ·Conflict)
    
- **HIGH_CONFLICT**: Conflict สูงสุด (top 5%) แต่ต้องผ่าน validators
    
- **MULTI_ATTRACTOR**: robustness ต่ำสุด + ต้องโชว์อย่างน้อย 2 seeds (same params)
    

> ทำให้เป็นสคริปต์เดียว (เช่น `scripts/select_representatives.py`) แล้ว “ทุกคนใช้เหมือนกัน”

---

## Step 7) ผลิต Demo Assets (ภาพ 3 อย่าง + กราฟที่อ่านออก)

สำหรับ run ที่ถูกเลือกเป็น representative ให้ generate:

**MUST (ภาพ 3 อย่าง)**

1. `figs/evolution.gif`
    
2. `figs/state_end.png` (หรือ `thumb.png`)
    
3. `figs/terrain_omega_grad_density.png` _(Conflict map)_
    

**MUST (เช็คความจริง)**

- `figs/curve_omega.png`
    

**ถ้า Open**

- `figs/curve_cumD_cumW.png`
    
- `policy_trace.csv/png` (ถ้ามี)
    

> จุดนี้คือคำตอบเรื่อง “อย่าเอาแต่กราฟ 2D”:  
> ภาพ terrain ของ `omega_grad_density` = วิธีทำให้เห็น “ระบบทั้งภาพ” แบบที่คนทั่วไปอ่านได้ (YouTube-style) โดยไม่ต้องมี 3D spatial solver จริง

---

## Step 8) สร้าง Demo Card (README_demo.md) แบบเติมอัตโนมัติได้

ใช้ template Part 7.2 แล้วเติมจาก `summary.json` + `UET_final_summary.csv`

ขั้นต่ำใน Demo Card ต้องมี:

- 1 ประโยค takeaway
    
- ภาพ 3 อย่าง
    
- Value/Conflict/phase/robustness
    
- Gates: validator/thermo/density
    
- reproduce command (matrix + seed + out)
    

---

## Step 9) Update `registry.json` (นี่คือ “ศูนย์กลางของ Gallery”)

เพิ่ม entry ต่อ demo (ตัวอย่างโครงขั้นต่ำ):

```json
{
  "demo_id": "DEMO_0123",
  "status": "candidate",
  "archetype": "HIGH_CONFLICT",
  "run_id": "<RUN_ID>",
  "run_dir": "runs_<suite_name>/<RUN_ID>",
  "assets": {
    "gif": "figs/evolution.gif",
    "end_state": "figs/state_end.png",
    "conflict": "figs/terrain_omega_grad_density.png",
    "omega_curve": "figs/curve_omega.png"
  },
  "metrics": {
    "value": 0.0,
    "conflict": 0.0,
    "omega_final": 0.0,
    "robustness": 0.0
  },
  "gates": {
    "transient_pass": true,
    "bias_pass": true,
    "thermo_valid": true,
    "density_ok": true
  }
}
```

> กติกา: Gallery generator **อ่านจาก registry เท่านั้น** ไม่ไปเดาไฟล์เอง

---

## Step 10) Build Gallery (ประกอบหน้าเว็บ/หน้าเอกสารจาก registry)

รันสคริปต์ build (ชื่อจริงแล้วแต่ repo แต่หลักคือ):

- อ่าน `registry.json`
    
- สร้าง:
    
    - `docs/gallery/index.md`
        
    - `docs/gallery/archetypes/*.md`
        
    - `docs/gallery/demos/DEMO_xxxx/...`
        

**ผลลัพธ์ที่ถูกต้อง**: ลบแล้ว build ใหม่ได้เหมือนเดิม (deterministic)

---

## Step 11) Pack (ทำ zip สำหรับแชร์/ปล่อย release โดยไม่ทำ repo บวม)

หลักการ: **ไม่ pack ทั้ง runs ดิบ** ให้ pack แค่ “สิ่งที่ตรวจสอบ+เล่าเรื่องได้”

### Demo pack (แนะนำ)

- `registry.json`
    
- `docs/gallery/` (generated)
    
- demo run_dir เฉพาะที่ publish:
    
    - `manifest.json, summary.json, timeseries.csv`
        
    - `figs/` ที่จำเป็น
        
    - `energy_density/density_final.npz` (ถ้าใช้ terrain)
        
    - snapshots อาจเอาแค่ subset ถ้าหนัก (แต่ต้องมี GIF แล้ว)
        

### Baseline pack

- `reports/v0_9_baseline_report.md`
    
- validation JSON
    
- aggregate CSV
    
- key figs
    

---

## Plain-Language Interpretation

นี่คือ “สูตรทำอาหาร” ของ UET:

- กรอกใบงาน (Design Card)
    
- แตกเป็นรายการทดลอง (Matrix)
    
- รันให้ได้ไฟล์มาตรฐาน (Runs)
    
- เช็คว่าไม่มั่ว (Validators + Gates)
    
- คัดตัวแทนแบบมีกติกา (Representative)
    
- ทำรูปให้คนดูออก (GIF + end + conflict terrain)
    
- ใส่ทะเบียน (Registry)
    
- สร้างนิทรรศการ (Gallery)
    
- แพ็คไปปล่อย (Release pack)
    

---

## Next Step

**Part 9.4 — Domain Adapter Spec (Data → State/Field → UET)**  
อันนี้คือจุดที่ตอบโจทย์ “คนอยากเอาไปใช้จริงกับโดเมนใหม่ทำยังไง” แบบไม่หลุด:

- วิธีเอา “ข้อมูลจริง” มาเป็น `C/I` (หรือ multi-field)
    
- วิธีสร้าง `resource/tilt map` จากข้อมูลจริง
    
- และวิธีตั้ง calibration anchors แบบไม่ overclaim
    

พิมพ์ “ต่อ” อีกที กูจะทำ Part 9.4 เป็นสเปก + checklist ที่ใช้กับโดเมนไหนก็ได้ (รวมถึงตัวอย่าง _โครง_ สำหรับนิเวศไทย/ระบบสุริยะ โดยไม่กระโดดไปสร้างโมเดลจริงทันที).


---
# 000.09/4

## TL;DR

**Part 9.4 = Domain Adapter Spec (Data → State/Field → UET)**  
นี่คือสเปก/เช็คลิสต์ที่ทำให้ “คนอยากเอา UET ไปใช้กับโดเมนใหม่” ทำได้แบบ **ไม่เดา ไม่มั่ว ไม่กระโดด**:

- แยกให้ชัดว่า **State (สิ่งที่เป็นอยู่)** คืออะไร
    
- **Environment/Space (กติกาโลก)** มาจากข้อมูลไหน
    
- แปลงข้อมูลเป็น **field บนกริด** + **tilt/resource map** + (ถ้า open) **schedule/policy**
    
- ใส่ทั้งหมดลง `manifest`/`matrix` แบบ trace ได้
    
- แล้วล็อก **gates**: validators + thermo ledger + density residual
    

---

## Insight

UET ไม่ได้เกิดมาเพื่อ “รับข้อมูลแล้วตอบคำถามทันที” แบบโมเดลสำเร็จรูป  
แต่มันเป็น **เครื่องมาตรฐาน** ที่บังคับให้โดเมนไหน ๆ ต้องตอบคำถามเดียวกัน 5 ข้อก่อน:

1. State คืออะไร (วัดได้/นิยามได้จริง)
    
2. Space/Environment คืออะไร (กติกาที่มากจากข้อมูล)
    
3. Ω ลงโทษ/ให้รางวัลยังไง (เลือกเทอมที่มีอยู่แล้ว: pot/coup/grad/tilt)
    
4. Output ที่คนอ่านออกคืออะไร (GIF/end/conflict/ledger)
    
5. จะพิสูจน์ว่าไม่มั่วยังไง (gates + reproducibility)
    

---

## Part 9.4 — Domain Adapter Spec (General, Public-Ready)

## 9.4.0 นิยาม “Domain Adapter”

**Domain Adapter** = ชุดกติกาแปลง “ข้อมูลดิบของโดเมน” → “อินพุตมาตรฐานของ UET”

**Input**

- dataset(s): raster/time series/network tables/point observations
    
- metadata: spatial ref, time ref, units, missingness
    

**Output (ต้องได้อย่างน้อย)**

- `X_init` (state fields เริ่มต้น) บนกริด
    
- `R(x,y)` หรือ `s(x,y,t)` (resource/tilt field)
    
- `theta` (พารามิเตอร์โลก: β, k, δ, …) + bounds/rate-limit ถ้า open
    
- `matrix.csv` สำหรับ run_suite
    
- `manifest.json` บันทึก provenance (dataset version/hash + transform config)
    

> หลัก: **Adapter ห้ามไป “พิสูจน์สมการ”** — หน้าที่มันคือ “แปลงโดเมนให้เข้าภาษา UET” เท่านั้น

---

## 9.4.1 เลือก “Resolution & Representation” ก่อนเสมอ

### A) Spatial domain

- เลือก grid: `N×N`, ขนาด cell = dx
    
- เลือก boundary: periodic / reflective / fixed
    

### B) Time domain

- เลือก dt ของ simulation (ไม่จำเป็นต้องเท่ากับ dt ของข้อมูลจริง)
    
- ทำ mapping: 1 epoch = กี่วัน/เดือน/ปี (ถ้าอยากเทียบโดเมน)
    

### C) Representation type (สำคัญมาก)

UET รุ่นนี้เหมาะกับ 3 representation หลัก:

1. **Density field**: สิ่งต่าง ๆ เป็น “ความหนาแน่น” (ต่อพื้นที่)
    
2. **Potential/pressure field**: สภาพแวดล้อมเป็นแผนที่แรงดึง/แรงผลัก
    
3. **Interface cost**: ความตึงเกิดที่รอยต่อ (ω_grad)
    

ถ้าโดเมนเป็น “agent/ตัวบุคคล/ดาวเคราะห์” ให้คิดแบบนี้ก่อน:

- ถ้ายังไม่ทำ discrete agents → แปลงเป็น **density field** ของ “การมีอยู่/การไหล” (toy แต่ public เข้าใจง่ายและรันได้)
    

---

## 9.4.2 Data → Field (กติกาแปลงข้อมูลเป็นแผนที่)

### A) Raster data (ภาพ/แผนที่)

- จัดให้อยู่บนกริดเดียวกับ UET (resample)
    
- normalize (ดู 9.4.3)
    

### B) Point observations (จุดพิกัด)

- rasterize ด้วย kernel:
    
    - Gaussian kernel / inverse distance / binning
        
- ได้ field เช่น “ความหนาแน่นการพบเห็น”
    

### C) Time series (รายเวลา)

- ถ้าไม่ spatial: ทำเป็น “global schedule” ของ θ(t)
    
- ถ้า spatial + time: ทำเป็น `R(x,y,t)` หรือ `s(x,y,t)` แบบ epoch update
    

### D) Network tables (โหนด-เส้นเชื่อม)

- ทางที่รันได้ใน v0.9: **embed เป็น grid field**
    
    - สร้าง heatmap ของ node importance / edge density แล้วให้เป็น resource field
        
- (อนาคต) ทำ graph-native variant ได้ แต่ตอน v0.9 ให้ยึด grid เพื่อไม่แตกสาย
    

---

## 9.4.3 Normalization & Missing Data (ต้องล็อกให้ deterministic)

### A) Normalization options (ต้องเลือก 1 และบันทึกใน manifest)

- `minmax(p1,p99)` (แนะนำสำหรับ public stability)
    
- `zscore` (เสี่ยงโดน outliers)
    
- `log1p + minmax` (ถ้าค่า skew มาก)
    

### B) Missingness policy

- fill = median / nearest / mask-to-zero (ต้องระบุ)
    
- ถ้ามี mask: ให้ export mask ด้วยเพื่อ reproducibility
    

### C) Provenance required in manifest

- dataset name + version/date
    
- hash ของไฟล์ (หรือ fingerprint)
    
- transform config (yaml/json)
    

> จุดนี้คือ “กันงานวิชาการพัง” เพราะคนอื่นจะรันซ้ำได้จริง

---

## 9.4.4 Mapping เข้าช่อง State (C/I หรือ X1..Xn)

เพื่อกันการ “ยัดความหมายมั่ว” ให้ใช้กฎนี้:

### Rule: State ต้องเป็น “สิ่งที่วัดได้/นิยาม operational ได้”

ตัวอย่างรูปแบบที่ไม่ลอย:

- X1 = “density ของสิ่ง A” (เช่น biomass density / traffic density / population density)
    
- X2 = “density ของสิ่ง B” หรือ “stress/pressure field” ที่วัดได้
    
- ถ้าจะใช้ C/I: ให้ระบุใน Design Card ว่า **C และ I ในโดเมนนี้หมายถึงอะไรเชิง operational** ไม่ใช่คำปรัชญา
    

**สำคัญ:**

- seed = ความไม่แน่นอนของ initial condition (ใช้ทดสอบ robustness)
    
- ความหมายหลักอยู่ที่ **Space/Ω/forcing** ไม่ใช่ seed
    

---

## 9.4.5 Mapping เข้าช่อง Space/Environment (tilt/resource/schedule)

นี่คือหัวใจที่ทำให้ UET “เล่าแบบ YouTube” ได้:

### A) Resource / tilt map

- แปลง feature map → `R(x,y)` แล้วทำ tilt:
    
    - `s(x,y) = λ * R(x,y)` (รูปแบบพื้นฐานสุด)
        

### B) Scheduled environment (open system)

- มีช่วงเวลา t: เปลี่ยน `λ(t)` หรือเปลี่ยน `R(x,y,t)`
    
- บังคับให้มี `policy_trace` แม้จะเป็น schedule ธรรมดา
    

### C) Feedback policy (optional)

- ใช้ observation vector จาก summary/epoch_summary
    
- เปลี่ยน θ ด้วย bounds + rate-limit (Part 6.2)
    

> แก่น: ถ้าโลกเปลี่ยนได้ ต้องผ่าน **thermo ledger (D/W)** เสมอ

---

## 9.4.6 Calibration & Validation (แบบไม่ overclaim)

### Level C0: Dimensionless sanity (ต้องทำ)

- dx, dt, scale ของ field
    
- scaling sanity: เปลี่ยน N/dt แล้ว behavior ไม่ “พังความหมาย” แบบไร้เหตุผล
    

### Level C1: Domain anchors (ถ้าจะเทียบโลกจริง)

- เลือก 2–3 anchor points เท่านั้นก่อน
    
    - เช่น “ตำแหน่ง resource peaks”
        
    - หรือ “distribution match” แบบ coarse
        
- ห้ามอ้าง SI units ถ้ายังไม่ทำ anchors
    

### Level C2: Falsifiable check (ก่อน claim ใหญ่)

กำหนดไว้ล่วงหน้า:

- “ถ้าปรับ feature A ขึ้น → ต้องเห็น alignment เพิ่ม”
    
- “ถ้าเพิ่ม coupling → ต้องเห็น conflict map เปลี่ยนรูปแบบเฉพาะ”  
    แล้วทดสอบจริง
    

---

## 9.4.7 Output Contract (สำหรับโดเมนใด ๆ)

ทุกโดเมนต้องผลิต “อย่างน้อย”:

- GIF evolution
    
- end-state
    
- conflict terrain (ω_grad density)
    
- Ω curve  
    และถ้า open:
    
- cumD/cumW (ledger) + thermo_valid
    

นี่คือสิ่งที่ทำให้คนทั่วไป “อ่านออก” โดยไม่ต้องอ่านตาราง

---

## 9.4.8 Example Adapter Stubs (เป็น “โครง” ไม่ใช่โมเดลจริง)

## Stub A: Thailand Ecology (โครงเท่านั้น)

**Data → Field**

- X1 (state): biomass/abundance density map (จากสำรวจ/remote sensing)
    
- X2 (state): stress/pressure proxy (เช่น human footprint / drought index)
    
- R(x,y): habitat suitability / water availability map
    

**UET mapping**

- tilt: `s(x)=λR(x)` (โลกเอียงไปหาแหล่ง resource)
    
- grad: แปล “boundary tension” ของ niche/region
    
- coupling: interaction ระหว่าง X1–X2 (ถ้าตีความได้ operational)
    

**Outputs**

- GIF: การรวมตัว/การย้ายตาม resource
    
- conflict terrain: จุดที่ “ชนกัน” ของ niche/pressure
    

> ไม่ได้บอกว่า “นี่คือระบบนิเวศจริง” — เป็นแค่ blueprint ว่าจะ map ยังไงให้รันได้ก่อน

---

## Stub B: “Solar-system style” (ต้องย้ำว่าเป็น toy ใน v0.9)

ถ้าอยากเล่า “สมดุลวงโคจร” แบบ public:

- ทำเป็น **potential landscape toy** ไม่ใช่ N-body orbital solver
    
- X = density/probability ของการอยู่ในบาง radius/region (grid embed)
    
- R(x) = effective potential proxy (สร้างจากสูตรหรือข้อมูลที่เลือก)
    
- UET จะเล่า “การกระจายตัว/โครงสร้างสมดุล” ได้ แต่ **ไม่ใช่คำนวณวงโคจรจริง** จนกว่าจะมี dynamics แบบนั้น
    

---

## Stub C: Physarum / network routing (เข้าทาง UET มาก)

- State: field ของ “ความหนาแน่นเส้นทาง/การไหล”
    
- Resource map: จุดอาหารหลายจุด
    
- Expected public demo: เกิดเส้นทางเชื่อมจุด → conflict terrain เป็น “เส้น” (เห็นชัดมาก)
    

นี่เป็นตัวอย่างที่ให้ภาพแบบ YouTube ได้ดี โดยไม่ต้องเพิ่มฟิสิกส์ใหม่

---

## Plain-Language Interpretation

ถ้ามีคนอยากใช้ UET กับโดเมนใหม่:

- ไม่ต้องเริ่มจากสมการยาก ๆ
    
- ให้เริ่มจาก “ทำแผนที่” ของสิ่งที่มีอยู่ (state) และแผนที่ของแรงดึง/กติกาโลก (resource/tilt)
    
- แล้ว UET จะค่อย ๆ แสดงว่าเมื่อโลกให้รางวัล/ลงโทษแบบนี้ ระบบจะ “เข้าที่” ยังไง และ “ตึงตรงไหน”
    

---

## Next Step

**Part 9.5 — Domain Model Bootstrapping Pack (Minimal viable public demo)**  
กูจะทำ “สูตรทำเดโมโดเมนใหม่ให้สำเร็จภายใน 1 suite”:

- เลือก 1 archetype ที่อยากโชว์ (เช่น HIGH_CONFLICT หรือ SYM)
    
- ทำ matrix เล็ก 3×3×(seeds 3)
    
- สร้าง demo 1 ใบ + registry + gallery entry ให้ครบวงจร
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูเขียน Part 9.5 เป็นแพลนแบบจบในชุดเดียว (เพื่อให้เห็นภาพว่าจากโดเมนใหม่ → public demo ทำยังไงแบบไม่งง).

---
# 000.09/5

## TL;DR

**Part 9.5 = สูตร “ทำโดเมนใหม่ให้เป็น Public Demo ได้ภายใน 1 suite”**  
ไม่ต้องเริ่มจาก sweep ใหญ่/กราฟ 2D เยอะ ๆ — ให้ทำ **Mini-suite 3×3×seeds(3)** เพื่อให้ได้:

- เดโม 1 ใบที่คนดูแล้ว “เห็นภาพ” (GIF + end-state + conflict terrain)
- ผ่าน gates (validators + ถ้า open: thermo ledger + ถ้า density: residual)
- มี registry entry → build gallery ได้

---

## Insight

เวลา “เอา UET ไปใช้กับโดเมนใหม่” สิ่งที่ต้องชนะก่อนคือ **การสื่อสาร + ความถูกต้องขั้นต่ำ** ไม่ใช่ความละเอียดสูง

ดังนั้น MVP ต้องตอบให้ได้ 3 อย่าง:

1. โลกให้ “แรงดึง” แบบไหน (resource/tilt)
    
2. ระบบ “เข้าที่” ยังไง (GIF/end-state)
    
3. “ตึงตรงไหน” (conflict terrain = ω_grad)
    

พอครบ 3 อย่างนี้แล้วค่อยขยายไป sweep ใหญ่/คาลิเบรต

---

## Part 9.5 — Domain Model Bootstrapping Pack (Minimal Viable Public Demo)

## 9.5.1 เลือก “เดโมเป้าหมาย” ก่อน (1 archetype พอ)

ให้เลือก **1 archetype** ที่อยากโชว์ให้คนเข้าใจง่ายที่สุด (แนะนำตามนี้):

- **HIGH_CONFLICT (แนะนำสุด)**: เห็น conflict terrain ชัดมาก → คนดูร้องอ๋อได้ง่าย
    
- **SYM**: เห็นการเข้าที่แบบสมมาตร → สื่อสารง่าย
    
- **BIAS_C/BIAS_I**: เห็น “ชนะข้าง” ชัด
    
- **MULTI_ATTRACTOR**: ใช้ตอนที่อยากเล่า “หลายคำตอบ” (ต้องโชว์ ≥2 seeds)
    

> v0.9 แนะนำเริ่มที่ HIGH_CONFLICT หรือ SYM ก่อน เพราะ “ภาพ” จะเล่าเรื่องแทนเราได้

---

## 9.5.2 MVP Model Choice (ยึดของที่มีอยู่แล้ว)

เพื่อไม่สร้างของใหม่มั่ว ให้ใช้ **โมเดล C/I เดิม + spatial forcing (resource→tilt)**

**แกนหลัก**

- State: `C(x,y), I(x,y)`
    
- Space: `R(x,y)` → tilt `s(x,y) = λ * R(x,y)`
    
- Ω terms ที่ใช้:
    
    - pot (รวม tilt)
        
    - coupling `-βCI`
        
    - grad (conflict) `~ k|∇|²`
        

**ทำไมวิธีนี้เหมาะกับ “เดโม public”**

- GIF จะโชว์ “ไหลเข้าหา resource”
    
- conflict terrain จะโชว์ “รอยต่อ/เส้นทาง/ขอบ” แบบเห็นภาพทันที
    

---

## 9.5.3 Mini-suite 3×3×seeds(3) (ชุดเดียวจบ)

ให้ทำ **3×3 grid** แค่ 2 แกน + seeds 3

### ตัวเลือกแกน sweep (เลือกอย่างใดอย่างหนึ่ง)

**Option A (แนะนำ)**: `λ_resource × k_ratio`

- λ_resource คุม “แรงดึงของ resource” (แรงขับจาก environment)
    
- k_ratio คุม “ความตึง/ราคาของรอยต่อ” (ทำให้ conflict map เด่น)
    

**Option B**: `β × k_ratio`

- β คุม interaction C–I (ระบบชนะข้าง/ปะทะ)
    
- k_ratio คุม interface cost
    

### ค่าตัวอย่าง (แนวทาง ไม่ล็อกตัวเลข)

- λ_resource: [low, mid, high]
    
- k_ratio: [soft, mid, hard]
    
- seeds: [0, 1, 2] (อย่างน้อย 3)
    

รวมเคส = 9 × 3 = 27 runs (เบามาก แต่พอให้เห็น pattern)

---

## 9.5.4 Resource Map (ต้องทำให้ “เห็นภาพ”)

ทำ resource map แบบง่าย 2 แบบ (เลือก 1 หรือทำทั้งคู่)

### Map M1: “สองแหล่งอาหาร”

- R(x,y) มี peak 2 จุด (ซ้าย–ขวา)
    
- เดโมคาดหวัง: การรวมตัว/เส้นทางเชื่อม/เกิด boundary
    

### Map M2: “ไล่ระดับ (slope)”

- R(x,y) เป็น gradient จากล่าง→บน
    
- เดโมคาดหวัง: ไหลไปทิศเดียว + โครงสร้าง end-state อ่านง่าย
    

> จุดสำคัญ: **resource map ต้องถูกบันทึก** (resource_id/path) เพื่อ reproducibility

---

## 9.5.5 Matrix ที่ต้องสร้าง (ตัวอย่าง schema)

ตั้งชื่อ:  
`matrices/UET_<Domain>_MVP_lambda_k_ratio_seed3.csv`

คอลัมน์ขั้นต่ำ (แนวเดียวกับของเดิม):

- `case_id`
    
- `seed`
    
- `model_type` (เช่น `CI`)
    
- `beta`
    
- `kC`, `kI`, `k_ratio`
    
- `delta` (หรือ `delta_C`, `delta_I`)
    
- `s_C`, `s_I` (ถ้ามีแยก) + `s_tilt` หรือ `lambda_R`
    
- `resource_id` หรือ `resource_path`
    
- ค่าคุม simulation (ถ้าระบบต้องการ): `N`, `dt`, `steps` (หรืออยู่ config ก็ได้)
    

> กติกา MVP: ใส่ **เท่าที่จำเป็น** และให้ manifest เก็บ provenance ให้ครบ

---

## 9.5.6 Pipeline (คำสั่งชุดเดียว)

### Run

```bash
python scripts/run_suite.py --matrix matrices/<MVP_MATRIX>.csv --out runs_<domain>_mvp
```

### Validate

```bash
python scripts/validate_transient_v3.py --runs runs_<domain>_mvp --out runs_<domain>_mvp/validation_transient_v3.json
python scripts/validate_bias_v2.py --runs runs_<domain>_mvp --out runs_<domain>_mvp/validation_bias_v2.json
```

### Aggregate

```bash
python scripts/aggregate_final_summary.py --runs runs_<domain>_mvp --out runs_<domain>_mvp/UET_final_summary.csv
```

### Plot pack (ทำให้เป็น “ภาพ 3 อย่าง”)

รันสคริปต์ plot ที่มีอยู่ (หรือ pack ที่เตรียมไว้) ให้ generate:

- `figs/evolution.gif`
    
- `figs/state_end.png` (หรือ thumb)
    
- `figs/terrain_omega_grad_density.png`
    
- `figs/curve_omega.png`
    

---

## 9.5.7 กติกาเลือก “Demo ตัวแทน 1 ใบ” (ห้ามเลือกมือ)

ใน mini-suite ให้เลือกเดโมด้วย rule ง่าย ๆ ที่ deterministic:

### ถ้าจะทำ HIGH_CONFLICT demo

- เลือกเคสที่ `Conflict` สูงสุด **แต่ validators ต้อง PASS**
    
- ถ้ามีหลายเคสเท่ากัน → เลือกที่ Value ไม่ต่ำ (tie-break)
    

### ถ้าจะทำ SYM demo

- เลือกที่ `robustness` สูงสุด + conflict ต่ำสุด (ถ้ามี seeds)
    

> สำหรับ MVP เอา 1 demo ก่อน (อย่าเพิ่งทำทั้ง gallery ใหญ่)

---

## 9.5.8 ทำ Demo Card 1 ใบ (public-ready)

สร้าง `README_demo.md` (ตาม Part 7.2) โดยบังคับให้มี:

- One-sentence takeaway (ภาษาคน)
    
- ภาพ 3 อย่าง (GIF/end/conflict terrain)
    
- Value/Conflict/phase label
    
- Gates summary (validators PASS, ถ้ามี density ก็ใส่ residual)
    
- reproduce command (matrix + seed)
    

**นี่คือจุดที่ “คนทั่วไปต้องเข้าใจได้” โดยไม่อ่าน CSV**

---

## 9.5.9 Update Registry → Build Gallery (แบบ minimal)

เพิ่ม entry เดโมเดียวลง `registry.json` เป็น `candidate` ก่อน  
แล้ว build gallery (generator อ่าน registry)

ผลลัพธ์ขั้นต่ำที่ต้องได้:

- `docs/gallery/index.md` มี tile ของ demo นี้
    
- ลิงก์ไป demo page ได้
    
- breadcrumb กลับได้
    

---

## 9.5.10 Pack (แชร์ให้คนอื่นลองได้ โดยไม่ทำ repo บวม)

ทำ zip ชุดเดียวที่ “คนโหลดไปดูแล้วเข้าใจ”:

- demo run_dir (เฉพาะใบเดียว)
    
- registry.json
    
- docs/gallery generated
    
- reports สั้น ๆ (optional)
    

> จุดนี้คือ “MVP Public Demo” ที่แท้จริง — ไม่ต้องมี runs 300 ชุด

---

## สิ่งที่ MVP ต้อง “พูดได้” (เพื่อให้มันมีค่า)

หลังทำครบ เราต้องตอบได้เป็นประโยคเดียวว่า:

- “ถ้าโลกมี resource แบบนี้ และแรงดึง λ มากขึ้น ระบบจะ ___”
    
- “แต่ราคาที่จ่ายคือ conflict ที่เกิดตรง ___ (ดูจาก terrain)”
    
- “และนี่ไม่มั่ว เพราะ validators ผ่าน + Ω curve/ledger/density checks ผ่าน”
    

---

## Plain-Language Interpretation

นี่คือสูตร “ทำโดเมนใหม่ให้คนดูแล้วเข้าใจ”:

1. ทำแผนที่ resource ง่าย ๆ
    
2. ปล่อยระบบไหล → ทำ GIF
    
3. เอา conflict terrain มาชี้ว่า “ตึงตรงไหน”
    
4. ใส่เดโมลง registry → gallery  
    เสร็จในชุดเดียว ไม่ต้องหลงไปทำ sweep ใหญ่ก่อน
    

---

## Next Step

**Part 9.6 — “From MVP to Research-Grade” Roadmap**  
หลังมี MVP demo แล้ว ค่อยขยายอย่างมีลำดับ:

- เพิ่ม seeds เพื่อ robustness
    
- ขยาย 3×3 → 7×7 cross-sweep
    
- เพิ่ม scheduled open system + thermo ledger
    
- เพิ่ม density export เต็ม (local→global)
    
- เริ่ม calibration C0→C1→C2
    

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 9.6 เป็นแผนขยายงานแบบเป็นขั้นบันได (ไม่แตกประเด็น) ว่าจากเดโมเดียวไปสู่งานวิชาการเต็มรูปแบบต้องทำอะไรทีละอย่าง.

# 000.09/6

## TL;DR

**Part 9.6 = แผน “จาก MVP Demo → Research-grade → Einstein/Λ Roadmap” แบบขั้นบันได**  
ไม่กระโดด ไม่แตกประเด็น แบ่งเป็น 5 ระดับชัด ๆ:  
**MVP → Robust → Atlas → Open/Thermo → Field/Density → Contact (Einstein/Λ)**  
แต่ละระดับมี “ของที่ต้องมี” + “gates” + “สิ่งที่ยังห้ามอ้าง”

---

## Insight

ปัญหาที่มึงเจอ (กราฟ 2D งง / คนทั่วไปไม่เข้าใจ / กลัวทฤษฎีไม่จบ)  
แก้ได้ด้วย “บันไดความรับผิดชอบ”:

- ชั้นล่าง: **เล่าเรื่องให้เห็นภาพ** (GIF/end/conflict)
    
- ชั้นกลาง: **พิสูจน์เชิงระบบ** (robustness + validators)
    
- ชั้นบน: **บัญชีเทอร์โม** (D/W) + **สนามแบบ density** (local→global)
    
- ชั้นสุด: **เริ่มแตะ Einstein/Λ แบบไม่ overclaim**
    

---

## Part 9.6 — From MVP to Research-Grade Roadmap (Step Ladder)

## Level 0 — MVP Public Demo (ทำได้ใน 1 suite) ✅

**เป้าหมาย:** คนทั่วไปดูแล้วเข้าใจ “มันเกิดอะไร” + ไม่มั่ว (validator PASS)

**Must have**

- 1 demo card (Part 7.2)
    
- ภาพ 3 อย่าง: GIF + end-state + conflict terrain
    
- Ω curve
    
- reproduce command ชัด
    

**Gates**

- validators PASS (transient/bias)
    

**Do NOT claim**

- ความทั่วไป/เสถียรภาพ (ยัง seed น้อย)
    
- thermodynamics / entropy (ถ้ายังไม่ทำ ledger/info)
    
- Einstein/Λ
    

---

## Level 1 — Robust Demo (เพิ่ม seeds เพื่อพูด “เสถียร/ทั่วไป”) ✅

**เป้าหมาย:** เดโมเดิม “ไม่ใช่ฟลุคของ seed”

**Do**

- เพิ่ม seeds เป็น 10 (หรือขั้นต่ำ 5 ถ้า compute จำกัด)
    
- เพิ่ม `robustness` metric/report (phase stability, metric dispersion)
    
- ทำ “representative selection” per parameter point (Part 4.11)
    

**Must have**

- “seed spread plot” หรือ summary: median/IQR ของ Value/Conflict
    
- demo card เพิ่มหัวข้อ “Robustness evidence”
    

**Gates**

- Repro gate: rerun same seed stable
    
- Robustness threshold (กำหนดไว้ชัดใน docs)
    

**Do NOT claim**

- ข้อสรุปเชิงโดเมนลึก ๆ (ยัง sweep น้อย)
    

---

## Level 2 — Atlas (Cross-sweep + Gallery Archetypes) ✅

**เป้าหมาย:** จาก “เดโมเดียว” → เห็นภูมิประเทศพารามิเตอร์ (atlas)

**Do**

- ทำ cross-sweep 1 ชุด (เช่น 7×7 หรือ 9×9) + seeds 5
    
- aggregate summary
    
- เลือก representative แบบ deterministic
    
- สร้าง Gallery (Part 7.3)
    

**Must have**

- Value–Conflict map (ของ representative)
    
- archetype pages (SYM/BIAS/HIGH_CONFLICT/MULTI_ATTRACTOR)
    
- baseline report ของ suite นี้ (สั้น ๆ)
    

**Gates**

- validators PASS ทุก run หรืออย่างน้อยทุก representative
    
- selection deterministic (regen แล้วเหมือนเดิม)
    

**Do NOT claim**

- thermo/open work/dissipation ถ้ายังไม่เปิดระบบ
    
- density/field claims ถ้ายังไม่มี density residual checks
    

---

## Level 3 — Open System + Thermo Ledger (D/W) ✅

**เป้าหมาย:** เริ่มพูด “ระบบเปิด” แบบมีบัญชี ไม่มั่ว

**Do**

- เพิ่ม scheduled forcing หรือ spatial forcing แบบเปลี่ยนตามเวลา
    
- ทำ ledger: `Ω_state_step` / `Ω_env_step` → `D_tot`, `W_tot`
    
- ทำกราฟ cumD/cumW + policy_trace
    

**Must have**

- thermo block ใน summary.json
    
- demo card แสดง D/W + policy timeline
    

**Gates**

- `thermo_valid=true`
    
- `|ledger_residual|<=tol`
    
- validators PASS
    

**Do NOT claim**

- entropy/thermo law ใหม่แบบเต็ม ๆ หากยังไม่แยก local densities หรือยังไม่มี calibration ที่ดี  
    (พูดได้แค่ “operational ledger”)
    

---

## Level 4 — Field/Density Export (local→global) ✅

**เป้าหมาย:** เปลี่ยนจาก “กราฟเส้น” เป็น “แผนที่สนาม” ที่ตรวจสอบได้  
นี่คือชั้นที่ทำให้ภาพแบบ YouTube เกิดจริง (terrain 3D/heatmap) แบบมีหลักฐาน

**Do**

- export `density_final.npz` อย่างน้อย: omega, pot, coup, grad
    
- ทำ residual checks: integrate density ≈ Ω_scalar
    
- สร้าง terrain plots จาก omega_grad_density เป็นหลัก
    

**Must have**

- density_final.npz + meta (grad method)
    
- term sum residual logs
    
- terrain_omega_grad_density + terrain_omega_density (optional)
    

**Gates**

- density_integral_residual <= tol
    
- term_sum_residual <= tol
    

**Do NOT claim**

- geometry/Einstein/Λ หากยังไม่มีการนิยาม object เทียบกับ energy-momentum หรือ calibration
    

---

## Level 5 — Einstein/Λ Contact (Roadmap gate, not claim) 🧭

**เป้าหมาย:** เริ่ม “แตะ” GR/Λ อย่างรับผิดชอบ โดยยึด 3 tests ใน Part 6.3

**Do**

- ทำ “baseline vs structure separation” ของ omega_density (baseline vs structure component)
    
- ทดสอบความคงเส้นคงวา (across seeds/conditions)
    
- ทำ contact tests 1–3:
    
    - local→global consistency (ผ่านแล้วใน Level 4)
        
    - open ledger consistency (ผ่านแล้วใน Level 3)
        
    - scale sanity (C0 dimensionless + anchors ถ้าจะเทียบโลกจริง)
        

**Must have**

- เอกสาร “Einstein/Λ is a roadmap” พร้อม gate list
    
- รายงานผล contact tests (PASS/FAIL)
    

**Do NOT claim**

- dark matter/energy explanation
    
- cosmology claims  
    จนกว่าจะมี C1–C2 calibration + falsifiable predictions
    

---

## “ลำดับงาน” ที่แนะนำจริง (เพื่อไม่หลง)

ถ้ามึงจะไปให้จบไวและไม่รก ให้ทำตามนี้:

1. ทำ MVP 1 ใบให้สวยและถูก (Level 0)
    
2. เพิ่ม seeds → robustness (Level 1)
    
3. ทำ cross-sweep 1 ชุด → gallery (Level 2)
    
4. เติม open schedule + ledger (Level 3)
    
5. เติม density export + terrain residual checks (Level 4)
    
6. เขียน Einstein/Λ contact report แบบ gate-based (Level 5)
    

---

## Plain-Language Interpretation

- เริ่มจากทำ “คลิปสั้นที่คนดูแล้วเข้าใจ”
    
- แล้วค่อยทำให้มัน “ไม่ฟลุค” ด้วยหลาย seed
    
- แล้วค่อยทำ “แผนที่” ของพารามิเตอร์
    
- แล้วค่อยเปิดระบบและทำบัญชี D/W
    
- แล้วค่อยทำแผนที่พลังงานเป็นสนาม (terrain)
    
- สุดท้ายค่อยแตะ Einstein/Λ แบบไม่โม้
    

---

## Next Step

เพื่อไม่ให้ลอย: ขั้นต่อไปของเอกสารคือ **Part 9.7 — “Minimal Domain Adapter Implementation Checklist”**  
เป็นรายการงานแบบ “ทำจริงใน repo” ว่าต้องสร้างไฟล์/สคริปต์อะไรบ้างเพื่อให้ adapter ของโดเมนใหม่ทำงานได้ (โดยไม่แก้ core เยอะ)

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 9.7 เป็น checklist เชิง implementation (ไฟล์, CLI, outputs, tests) ที่ตรงกับ pipeline ของ repo.

---
# 000.09/7

## TL;DR

**Part 9.7 = Minimal Domain Adapter Implementation Checklist (ทำจริงใน repo แบบไม่แก้ core เละ)**  
เป้าหมาย: คนเอา “ข้อมูลโดเมน” มาแปลงเป็น **state fields + resource/tilt maps + schedule** แล้ว **รันผ่าน pipeline เดิม** ได้เลย (run → validate → aggregate → demo → registry → gallery)

---

## Insight

Adapter ที่ดี **ไม่ใช่โมเดลใหม่** และไม่ไปแตะสมการหลัก  
Adapter คือ “ชั้นแปลงข้อมูล” ให้เข้าภาษา UET แบบ **deterministic + traceable + reproduce ได้**  
ดังนั้นสิ่งที่ต้องล็อกคือ:

- schema ของ input/output
    
- provenance (hash/version/config)
    
- path convention
    
- tests ขั้นต่ำ (determinism + range checks)
    

---

## Part 9.7 — Minimal Domain Adapter Implementation Checklist

## 9.7.0 หลักการก่อนเริ่ม (ไม่งั้นจะรก)

- ✅ Adapter อยู่ในโฟลเดอร์เฉพาะ (เช่น `domain_adapters/` หรือ `scripts/domain/`)
    
- ✅ ห้าม embed logic แปลงข้อมูลไว้ใน solver โดยตรง
    
- ✅ solver อ่าน “field files” ได้แบบ generic (`.npz`) ผ่าน path ใน matrix/manifest
    
- ✅ ทุกการแปลงต้องมี **config** และ **fingerprint** (dataset + transform)
    

---

## 9.7.1 โครงไฟล์ขั้นต่ำที่ต้องเพิ่ม

### A) โฟลเดอร์แนะนำ

```
domain_adapters/
  __init__.py
  common/
    io.py
    normalize.py
    fingerprint.py
    grid.py
  <domain_name>/
    adapter.py
    config_schema.md
    examples/
      adapter_config_example.yaml
```

### B) สคริปต์ CLI อย่างน้อย 2 ตัว

1. `scripts/build_domain_fields.py`
    
    - input: adapter_config.yaml + raw data path
        
    - output: `data/processed/<domain>/<dataset_fingerprint>/fields_*.npz` + `provenance.json`
        
2. `scripts/make_matrix_from_fields.py`
    
    - input: processed fields path + sweep plan (yaml)
        
    - output: `matrices/UET_<Domain>_<Sweep>.csv`
        

> ถ้าจะ minimal สุดจริง ๆ: ทำแค่ `build_domain_fields.py` ก่อน แล้ว matrix เขียนมือได้ แต่พอ public แนะนำให้มีทั้งคู่

---

## 9.7.2 Output Contract ของ Adapter (สิ่งที่ต้อง export ให้ solver)

### A) Field bundle file (`fields_bundle.npz`)

ต้องมี keys อย่างน้อย:

**State init**

- `C0` (N×N) _(หรือ X1_0)_
    
- `I0` (N×N) _(หรือ X2_0)_
    

**Environment**

- `R` (N×N) _(resource map)_ หรือ
    
- `s` (N×N) _(tilt map)_
    
- ถ้ามีเวลา: `R_t` (T×N×N) หรือ `s_t` (T×N×N) + `t_grid`
    

**Grid metadata**

- `dx`, `dy`
    
- `N`
    
- `grid_bounds` (optional)
    

**Mask (optional but recommended)**

- `mask` (N×N) (1=valid, 0=missing)
    

### B) Provenance file (`provenance.json`)

ต้องบันทึก:

- `domain_name`
    
- raw dataset identifiers (name/version/date)
    
- raw file fingerprints (sha256 หรือขนาด+mtime+hash)
    
- transform config snapshot (normalize method, fill policy, kernel params, resample method)
    
- output fingerprint (hash ของ npz + provenance)
    

> กติกา: ถ้าไม่มี provenance → ห้ามใช้ทำ claim/เผยแพร่ demo

---

## 9.7.3 Adapter Config (YAML) — schema ขั้นต่ำ

ไฟล์: `configs/adapters/<domain>_adapter.yaml` (หรือใน `domain_adapters/<domain>/examples/`)

ตัวอย่างโครง:

```yaml
domain: thailand_ecology
raw_inputs:
  biomass_raster: data/raw/<...>.tif
  pressure_raster: data/raw/<...>.tif
  resource_raster: data/raw/<...>.tif

grid:
  N: 128
  bounds: [xmin, xmax, ymin, ymax]
  boundary: periodic

preprocess:
  resample: bilinear
  fill_missing: median
  normalize: minmax_p1_p99
  clip: [0.0, 1.0]

mapping:
  state:
    C0_from: biomass_raster
    I0_from: pressure_raster
  environment:
    R_from: resource_raster
    s_from_R:
      enabled: true
      lambda_R: 2.0

time:
  mode: static   # static | scheduled
  schedule: null # or path to schedule file
```

---

## 9.7.4 วิธีให้ solver “รับ fields” โดยไม่พังระบบเดิม

### A) เพิ่มคอลัมน์ใน matrix (สำหรับโดเมนที่ใช้ adapter)

- `fields_path` = path ไป `fields_bundle.npz`
    
- (optional) `provenance_path`
    
- `resource_id`/`schedule_id` ถ้าจะใช้ระบบอ้างอิงแทน path
    

### B) ใน run pipeline

หลักคือ:

- `run_suite.py` อ่าน matrix row → ใส่ path ลง manifest
    
- solver โหลด `C0/I0/R/s` จาก npz แล้ว initialize state/environment
    
- แล้ว export manifest/summary/timeseries เหมือนเดิม
    

> กติกา compatibility: ถ้า matrix ไม่มี `fields_path` ให้ fallback ไป init แบบเดิม (random/structured)

---

## 9.7.5 Minimal Tests (ต้องมีเพื่อกัน “มั่วแล้วไม่รู้ตัว”)

สร้าง `tests/` (ถ้ามีอยู่แล้วก็เพิ่มเคส)

### Test T1 — Determinism

- ใช้ raw input เดิม + config เดิม
    
- ต้องได้ `fields_bundle.npz` เหมือนเดิม (hash เท่ากัน)
    

### Test T2 — Range & NaN

- หลัง normalize ต้องไม่มี NaN/Inf ใน `C0/I0/R/s`
    
- อยู่ใน range ที่ประกาศ (เช่น [0,1])
    

### Test T3 — Mask consistency (ถ้ามี mask)

- mask=0 ตำแหน่งนั้นค่า field ต้องเป็น 0 หรือค่าที่นิยามไว้ (บังคับให้ชัด)
    

### Test T4 — Regrid shape

- output shape ต้อง N×N ถูกต้อง และ metadata dx/dy ตรงตาม config
    

> แนะนำเพิ่ม T5 (ถ้าจะ public จริง): provenance contains all required keys

---

## 9.7.6 “Smoke Demo” สำหรับโดเมนใหม่ (บังคับทำ 1 ชุด)

หลัง adapter ทำงาน ให้ทำ MVP ตาม Part 9.5 ทันที:

- matrix 3×3×seeds(3)
    
- รัน → validate → aggregate
    
- สร้างรูป 3 อย่าง + demo card
    
- ใส่ registry เป็น `candidate`
    

**นี่คือ proof ว่า adapter ไม่ใช่ไฟล์ค้างในลิ้นชัก**

---

## 9.7.7 Documentation ที่ต้องเพิ่ม (สั้นแต่ครบ)

1. `docs/domain_adapters.md`
    
    - อธิบาย concept: data→fields→matrix→runs
        
2. `domain_adapters/<domain>/config_schema.md`
    
    - อธิบาย config keys + ตัวอย่าง
        
3. `docs/runbook/<domain>_mvp.md`
    
    - คำสั่ง build fields + make matrix + run + validate + aggregate + plot
        

---

## 9.7.8 Gates ที่ผูกกับ adapter โดยตรง

- **Adapter gate (ใหม่ระดับ tooling ไม่ใช่ทฤษฎี):**
    
    - `fields_hash` ต้องถูกบันทึกใน manifest
        
    - `adapter_config_hash` ต้องถูกบันทึกใน manifest
        
- **Main gates (เดิม):**
    
    - validators PASS
        
    - ถ้า open: thermo_valid
        
    - ถ้า density: residual PASS
        

---

## 9.7.9 “No-regret” conventions (กัน repo รกตั้งแต่แรก)

- raw data ไม่ commit (เก็บนอก repo หรือใช้ git-lfs ถ้าจำเป็น)
    
- processed fields เก็บใน `data/processed/...` และไม่ commit (ยกเว้น demo pack/release pack)
    
- registry แยก `candidate` กับ `published` ชัด
    

---

## Plain-Language Interpretation

นี่คือคู่มือ “ทำตัวแปลงโดเมน” แบบที่คนอื่นเอาไปใช้ต่อได้:

- เอาข้อมูลจริงมาแปลงเป็นแผนที่ (state + resource)
    
- ใส่ metadata ว่ามาจากไฟล์ไหน แปลงยังไง
    
- แล้ว UET ก็ทำหน้าที่เดิม: รัน → ตรวจ → สรุป → ทำภาพ → สร้าง gallery
    

---

## Next Step

**Part 9.8 — “Einstein/Λ Bridge: What we can say (and what we must not say) in v0.9”**  
จะเป็นกรอบคำพูด/กรอบทดสอบแบบ “ไม่โม้”:

- นิยาม object ที่เรามีจริงตอนนี้ (Ω density, ledger, scale sanity)
    
- สิ่งที่ยังขาดเพื่อเชื่อม GR (ต้องมีอะไรเพิ่มบ้าง)
    
- รูปแบบรายงาน contact tests ที่ publish ได้โดยไม่โดนตบ
    

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 9.8 ให้เป็น policy + test list แบบใช้ขึ้น public ได้จริง.

---
# 000.09/8

## TL;DR

**Part 9.8 = “Einstein/Λ Bridge Policy” สำหรับ v0.9**  
บอกให้ชัดว่า **ตอนนี้เรามีอะไรที่พูดได้จริง** (Ω/ledger/density/residuals) และ **อะไรที่ห้ามอ้าง** จนกว่าจะผ่าน calibration + falsifiable tests  
พร้อม “รายการทดสอบ” ที่ต้องผ่านก่อนจะเริ่มแตะ GR/Λ แบบเป็นวิชาการ

---

## Insight

ถ้าเราจะ “เชื่อม Einstein/Λ” แบบไม่โดนตบ สิ่งสำคัญไม่ใช่ไอเดีย แต่คือ **กรอบความรับผิดชอบ**:

- **พูดได้** เฉพาะสิ่งที่ “ตรวจซ้ำได้ + มี gate ยืนยัน”
    
- **พูดไม่ได้** ถ้ายังไม่มี mapping object-to-object (เช่น เทียบกับ stress-energy, curvature) และยังไม่มี calibration ที่ผูกกับ observable
    

ดังนั้น Part 9.8 จะเป็น “policy + test list” สำหรับ public

---

## Part 9.8 — Einstein/Λ Bridge Policy (v0.9)

## 9.8.1 สิ่งที่ “มีอยู่จริง” ใน v0.9 (พูดได้)

### A) เรามี “scalar landscape” จริง

- ( \Omega[X;\theta(t)] ) เป็นค่าที่คำนวณได้
    
- closed: ใช้เป็น Lyapunov-like indicator (ผ่าน validator/gate)
    
- open: แยก ledger ได้ (D/W)
    

**Allowed statement (public-safe)**

- “ระบบมีภูมิประเทศ Ω และ dynamics ที่พา state เข้าหา attractor”
    
- “ระบบเปิดสามารถแยกผลของการคลายตัวเอง vs งานจากสิ่งแวดล้อมได้ (D/W ledger)”
    

---

### B) เรามี “field densities” แบบ operational จริง (ถ้าเปิด density export)

- (\omega(x)), (\omega_{\text{pot}}(x)), (\omega_{\text{coup}}(x)), (\omega_{\text{grad}}(x))
    
- มี residual checks: integral(density) ≈ Ω_scalar
    

**Allowed statement**

- “เรามีแผนที่ต้นทุน/ความตึงในเชิงพื้นที่ (เช่น ω_grad_density) ที่รวมแล้วสอดคล้องกับ Ω”
    

---

### C) เรามี “โครงสร้างการเปลี่ยนแปลง” ที่ตรวจสอบได้

- phase labels / archetypes
    
- robustness ผ่าน multi-seed
    
- gallery selection deterministic
    

**Allowed statement**

- “atlas ของ attractors ภายใต้พารามิเตอร์ต่าง ๆ สร้างได้แบบทำซ้ำได้”
    

---

## 9.8.2 สิ่งที่ “ห้ามอ้าง” ใน v0.9 (ต้องล็อกไว้ชัด)

### Forbidden claims (ห้ามพูดว่าเป็นข้อสรุป)

- “อธิบาย dark matter/dark energy ได้แล้ว”
    
- “Ω density = curvature/metric ของ GR โดยตรง”
    
- “Value/Conflict = entropy/temperature ในความหมายฟิสิกส์จริง”
    
- “ได้สมการ Einstein field equations จาก UET แล้ว” (ถ้ายังไม่มี derivation + object mapping + calibration)
    

**เหตุผลเดียวกันหมด**

- ตอนนี้ยังไม่มี:
    
    1. mapping object-to-object กับ GR (metric/curvature/stress-energy)
        
    2. หน่วย/สเกลจริง (C1–C2)
        
    3. falsifiable predictions เทียบข้อมูลจริง
        

---

## 9.8.3 นิยาม “Bridge” ที่อนุญาต (Roadmap-only) ใน v0.9

ใน v0.9 ให้ใช้คำว่า:

> **“Contact / Bridge Candidate”**  
> หมายถึง: “เรามี object ใน UET ที่มีพฤติกรรมคล้าย” แต่ยังไม่ใช่ “เทียบเท่า”

### Bridge Candidate Objects (พูดได้แบบ cautious)

1. **Baseline vs structure decomposition** ของ (\omega(x))
    
    - โครงสร้างที่คงรูป vs โครงสร้างที่เป็น interface cost
        
2. **Open-system ledger D/W**
    
    - แยก “การคลาย” กับ “งานจากภายนอก”
        
3. **Scale sanity (dimensionless)**
    
    - เปลี่ยน dx/dt/N แล้ว invariants ยังอยู่ในแนวที่สมเหตุผล
        

**Allowed wording**

- “This is a candidate structural analogy”
    
- “This provides a testable contact point”
    
- “No astrophysical claim without calibration”
    

---

## 9.8.4 Contact Tests (รายการทดสอบขั้นต่ำก่อนพูดถึง GR/Λ ต่อหน้า public)

> ถ้าไม่ผ่านข้อใดข้อหนึ่ง → ห้ามใช้คำว่า bridge/contact ใน release notes

### Test T1 — Local→Global Consistency (Density)

- ผ่านแล้วใน Part 6.3.1 framework
    
- ต้องรายงาน:
    
    - `omega_density_integral_residual`
        
    - `term_sum_residual`
        

**Pass criteria**: residual ≤ tol

---

### Test T2 — Open Ledger Consistency (Thermo)

- `thermo_valid=true`
    
- `|ledger_residual| <= tol`
    

**Pass criteria**: ผ่านทุก representative demo ที่จะเอาไปอ้าง

---

### Test T3 — Robustness under seeds

- same parameter point, seeds ≥ 5–10
    
- phase label/metrics dispersion อยู่ในกรอบ
    

**Pass criteria**: robustness ≥ threshold ที่ประกาศไว้

---

### Test T4 — Scale sanity (dimensionless)

ทำ 2 การทดลอง (ขั้นต่ำ):

- เปลี่ยน grid resolution N (เช่น 64→128) แล้ว normalize แบบเดิม
    
- เปลี่ยน dt (เช่น dt/2) แล้วดู qualitative attractor/archetype
    

**Pass criteria**

- archetype ไม่พลิกมั่ว ๆ เมื่อ refine resolution
    
- residuals ไม่พัง และ pattern “เหมือนเดิมในภาพรวม”
    

---

### Test T5 — Baseline/Structure separation stability (ถ้าจะพูดถึง “Λ-like baseline”)

- นิยาม baseline component ของ (\omega(x)) แบบ operational (เช่น spatial mean / low-pass component)
    
- ตรวจว่า baseline ไม่ขึ้นกับ seed มากเกินไป และไม่เป็น artifact ของ normalization
    

**Pass criteria**

- baseline metric (mean/lowfreq energy) stable across seeds within tolerance
    

> ยังไม่เรียก “Λ” ได้ แค่เรียก “baseline component candidate”

---

## 9.8.5 Report Format (ไฟล์รายงานที่ publish ได้)

แนะนำไฟล์: `reports/v0_9_contact_report_GR_lambda.md`

โครง:

1. What we tested (T1–T5)
    
2. Results table (PASS/FAIL + values)
    
3. Visual evidence (1 รูปต่อ test)
    
4. “What this means” (คำอธิบายแบบ cautious)
    
5. “What this does NOT mean” (ข้อห้าม)
    

---

## 9.8.6 Public-facing wording (คำที่ใช้ได้ / คำที่ห้ามใช้)

### Allowed phrases

- “candidate contact point”
    
- “structural analogy”
    
- “operational baseline component”
    
- “requires calibration before physical interpretation”
    

### Disallowed phrases

- “explains dark matter”
    
- “derives Einstein equation”
    
- “this is curvature/metric”
    
- “entropy law of the universe” (ถ้ายังไม่ calibrate)
    

---

## Math/Physics Interpretation (แบบนักวิชาการ—ซื่อตรง)

- v0.9 มี (\Omega) และ (\omega(x)) เป็น objects ภายในระบบจำลอง
    
- การจะเชื่อม GR ต้องมี mapping:
    
    - object (UET) → tensor/geometry object (GR)
        
    - และต้องระบุหน่วย/สเกล + observational anchors
        
- ดังนั้น v0.9 ทำได้แค่ “contact tests” เพื่อคัดว่าแนวทางไม่ขัดกับตัวเอง (consistency + scaling)
    

---

## Plain-Language Interpretation

ตอนนี้เราพูดได้ว่า:

- เรามี “ภูมิประเทศ” ที่ระบบไหลลงไปหา “หลุม”
    
- เรามี “แผนที่” ว่าตึงตรงไหน
    
- และเรามีบัญชีว่า “โลกอัดงานใส่” กับ “ระบบคลายเอง” แยกกันได้
    

แต่เรายัง **ห้ามพูด** ว่า “นี่คือจักรวาล/แรงโน้มถ่วง/สสารมืด”  
จนกว่าจะทำการเทียบกับข้อมูลจริงและทดสอบแบบหักล้างได้

---

## Next Step

ถัดไปเพื่อให้ “bridge roadmap” มีเนื้อจริง คือ **Part 9.9 — Baseline/Structure Decomposition Spec**

- นิยาม baseline component ของ ω(x) แบบ operational
    
- วิธี low-pass/high-pass (เชิงคณิต) ที่ไม่สร้างของใหม่เกินกรอบ
    
- แล้วเช็คความเสถียรของ baseline ข้าม seeds/params
    

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 9.9 เป็นสเปกที่เอาไปทำในสคริปต์ได้จริง (ไม่ใช่คำพูดลอย ๆ).

---
# 000.09/9

## TL;DR

**Part 9.9 = สเปก “แยก Baseline vs Structure” บนสนาม (\omega(x))** (ที่เรา export อยู่แล้ว)  
เพื่อให้เราพูดถึง “พื้นหลัง/ค่าฐาน” ได้แบบ **operational + ตรวจสอบได้** โดย **ไม่อ้างว่าเป็น Λ จริง**  
และทำเป็น pipeline ได้เลย: **density_final.npz → baseline_map → structure_map → stability tests (across seeds/params)**

---

## Insight

ถ้าจะไปต่อเรื่อง Einstein/Λ แบบไม่โม้ เราต้องมีสิ่งนี้ก่อน:

> “บนแผนที่พลังงาน (\omega(x)) มีส่วนที่เป็น ‘พื้นหลัง’ (smooth/low-frequency) และส่วนที่เป็น ‘โครงสร้าง’ (interfaces/high-frequency) จริงไหม และมันเสถียรข้าม seed ไหม?”

Part 9.9 คือการ “ทำให้คำว่า baseline” มีนิยามและการทดสอบที่ repeat ได้

---

## Part 9.9 — Baseline/Structure Decomposition Spec (Implementable)

## 9.9.1 Inputs (ยึดของที่มีอยู่แล้ว)

ต้องมีอย่างน้อย:

- `energy_density/density_final.npz` ที่มีแผนที่:
    
    - `omega` หรือ `omega_density`
        
    - `omega_pot_density`, `omega_coup_density`, `omega_grad_density` (ถ้ามี)
        
- `summary.json` ที่มี Ω scalar (เพื่อเช็ค local→global)
    
- grid meta (N, dx) ถ้าอยู่ใน npz หรือ manifest
    

> หลัก: เรา “แยกภาพ” บน (\omega(x)) ไม่แก้สมการ ไม่แตะ solver

---

## 9.9.2 เป้าหมายของการแยก (นิยามเชิงงาน ไม่ใช่เชิงจักรวาล)

ให้แยก (\omega(x)) เป็น 2 ส่วน:  
[  
\omega(x) = \omega_{\text{base}}(x) + \omega_{\text{str}}(x)  
]

โดยบังคับคุณสมบัติขั้นต่ำ:

### (P1) Additive exactness (เชิงตัวเลข)

- ต้องได้ (\omega_{\text{base}} + \omega_{\text{str}}) ใกล้ (\omega) ภายใน tol
    

### (P2) Baseline = smooth (low-frequency)

- (\omega_{\text{base}}) ต้อง “เรียบ” (ควบคุมด้วย scale parameter (\ell))
    

### (P3) Structure = localized (interfaces / high-frequency)

- (\omega_{\text{str}}) ควรเด่นบริเวณขอบ/รอยต่อ/เส้นทาง
    
- โดยเฉพาะควร correlate กับ `omega_grad_density` (ถ้ามี)
    

> ตรงนี้คือหัวใจ: เราไม่ได้บอกว่า baseline คือ Λ  
> เราบอกแค่ว่า “มีองค์ประกอบพื้นหลังแบบเรียบ” เป็น candidate object

---

## 9.9.3 ตัวเลือกวิธีแยก (เลือก 1 เป็นมาตรฐาน v0.9)

เพื่อไม่แตกสาย ให้รองรับ 2 วิธีหลักพอ:

### Method A (แนะนำ): Spatial Low-pass Filter (Gaussian Blur / FFT low-pass)

นิยาม:

- (\omega_{\text{base}} = \mathcal{L}_{\ell}[\omega]) (ตัวกรองความถี่ต่ำที่ scale (\ell))
    
- (\omega_{\text{str}} = \omega - \omega_{\text{base}})
    

**ตัวกรองที่ใช้ได้**

- Gaussian blur ด้วย (\sigma=\ell/dx)
    
- หรือ FFT low-pass ด้วย cutoff (k_c \sim 1/\ell)
    

**ข้อดี**

- ตรงไปตรงมา, implement ง่าย, deterministic
    
- อธิบาย public ได้: “เฉลี่ยให้เรียบ แล้วดูส่วนที่เหลือเป็นรายละเอียด”
    

---

### Method B: Baseline = Spatial Mean / Polynomial Trend (ultra-minimal)

นิยาม:

- (\omega_{\text{base}}(x) = \bar{\omega}) (ค่าคงที่) หรือ fit โพลิโนเมียล low-degree
    
- (\omega_{\text{str}} = \omega - \omega_{\text{base}})
    

**ข้อดี**

- ง่ายสุด, ไม่มี hyperparameter เยอะ  
    **ข้อเสีย**
    
- baseline แบนเกินไป อาจพลาด gradient ของโลกที่เป็นจริงของ simulation
    

> v0.9 แนะนำให้มาตรฐานเป็น Method A แล้วเก็บ Method B เป็น sanity check

---

## 9.9.4 Choosing the scale (\ell) (สำคัญมาก)

(\ell) คือ “ขนาดที่เราถือว่าเป็นพื้นหลัง”

### Rule-of-thumb (operational, ไม่อ้างฟิสิกส์จริง)

- ถ้ากริด N×N: เลือก (\ell) เป็นสัดส่วนของ domain size เช่น
    
    - (\ell \in {L/8, L/6, L/4}) (ทำ 2–3 ค่าเพื่อดู sensitivity)
        
- หรือเลือกจาก “ขนาดโครงสร้าง” ที่ต้องการให้เป็น structure:
    
    - ถ้า interface หนา ~ 2–5 cells → (\ell) ต้องใหญ่กว่านั้นพอสมควรเพื่อไม่ดูดรายละเอียดเข้าพื้นหลัง
        

### Gate: Scale sensitivity must be bounded

- ถ้าเปลี่ยน (\ell) เล็กน้อย baseline/structure ไม่ควร “กลับความหมาย” ทั้งหมด
    

---

## 9.9.5 Metrics ที่ต้องรายงาน (เพื่อไม่ให้พูดลอย)

ให้คำนวณจาก (\omega), (\omega_{\text{base}}), (\omega_{\text{str}})

### Scalar summaries

- ( \Omega = \int \omega(x),dx )
    
- ( \Omega_{\text{base}} = \int \omega_{\text{base}}(x),dx )
    
- ( \Omega_{\text{str}} = \int \omega_{\text{str}}(x),dx )
    

> หมายเหตุ: (\omega_{\text{str}}) อาจมีค่าลบ/บวกได้ (เป็น residual)  
> ดังนั้นอย่าฝืนตีความ “พลังงานบวกเท่านั้น” ถ้าเรายังไม่ได้ constrain

### Ratio / dominance

- `baseline_fraction = Ω_base / Ω`
    
- `structure_fraction = Ω_str / Ω` (รายงานเพื่อ monitoring ไม่ใช่ตีความฟิสิกส์ทันที)
    

### Correlation with conflict

ถ้ามี `omega_grad_density`:

- `corr_str_grad = corr( |ω_str| , ω_grad_density )`  
    คาดหวังว่า structure จะสัมพันธ์กับ gradient/conflict สูงขึ้น
    

---

## 9.9.6 Residual & Consistency Gates (สิ่งที่ต้องผ่าน)

### Gate D1 — Reconstruction residual

[  
r_{\text{rec}} = \frac{|\omega - (\omega_{\text{base}}+\omega_{\text{str}})|_1}{|\omega|_1}  
]

- ต้อง ≤ tol (เช่น 1e-6 ถึง 1e-3 แล้วแต่ numerical)
    

### Gate D2 — Local→Global (ต่อยอดจาก density export)

- (\int \omega \approx \Omega_{\text{scalar}}) ต้องยัง PASS
    
- และ (\int \omega_{\text{base}} + \int \omega_{\text{str}} \approx \Omega_{\text{scalar}})
    

### Gate D3 — Smoothness check ของ baseline

วัดด้วย total variation หรือ energy ของ high-frequency:

- `TV(base)` ต้องต่ำกว่า `TV(omega)` ชัดเจน
    
- หรือ FFT energy ใน high k ของ baseline ต้องต่ำ
    

---

## 9.9.7 Stability Tests (ข้าม seed/params) — นี่คือ “เนื้อจริง”

### Test S1 — Seed stability at fixed params

เลือก parameter point เดียว รัน seeds ≥ 5–10:

- ดูการกระจายของ `Ω_base`, `baseline_fraction`
    
- ดู similarity ของ baseline map:
    
    - `sim_base = corr( ω_base(seed_i), ω_base(seed_j) )` หรือ SSIM  
        คาดหวัง: baseline เสถียรกว่า structure
        

### Test S2 — Near-boundary sensitivity

เลือกจุดที่ใกล้ phase boundary:

- คาดหวังว่า structure จะเปลี่ยนเยอะ แต่ baseline เปลี่ยนน้อยกว่า
    

### Test S3 — Scale sanity

เปลี่ยน grid resolution (ถ้าทำได้) หรือเปลี่ยน (\ell):

- baseline component ไม่ควร “หายไป” หรือ “กลับขั้ว” แบบไร้เหตุผล
    

---

## 9.9.8 Artifacts ที่ต้อง export (เพื่อเอาไปใส่ Demo/Gallery)

สำหรับแต่ละ run (หรือ representative) ให้สร้าง:

- `figs/terrain_omega_density.png`
    
- `figs/terrain_omega_base_density.png`
    
- `figs/terrain_omega_str_density.png`
    
- `figs/terrain_omega_grad_density.png` (มีอยู่แล้ว)
    
- `figs/curve_base_structure_scalars.png` (สรุป Ω_base/Ω_str vs t ถ้าทำ timeseries ได้)
    

และไฟล์ data:

- `energy_density/baseline_decomp.npz` ที่มี:
    
    - `omega_base`, `omega_str`, `ell`, `method`, `rec_residual`, metrics scalars
        

> สำคัญ: demo จะ “อ่านออก” ทันที เพราะเห็น 3 ชั้น: omega / base / structure

---

## 9.9.9 How to talk about it in public (คำพูดมาตรฐาน)

### อนุญาต

- “เราแยกสนาม (\omega(x)) เป็นส่วนเรียบ (baseline) กับส่วนรายละเอียด (structure) แบบทำซ้ำได้”
    
- “baseline มีเสถียรภาพข้าม seed มากกว่า structure”
    
- “structure สัมพันธ์กับ conflict terrain (ω_grad) สูง”
    

### ห้าม

- “baseline = Λ ของจักรวาล”
    
- “นี่คือ curvature/metric”
    

---

## Math/Physics Interpretation (Formal)

ให้ (\mathcal{L}_{\ell}) เป็น low-pass operator:  
[  
\omega_{\text{base}} = \mathcal{L}_{\ell}\omega,\quad  
\omega_{\text{str}} = (I-\mathcal{L}_{\ell})\omega  
]  
แล้วตรวจ:

- reconstruction (trivial)
    
- smoothness: (|\nabla \omega_{\text{base}}|) ต่ำ
    
- structure localization: (\omega_{\text{str}}) correlate กับ (\omega_{\text{grad}})
    

ทั้งหมดเป็น “signal decomposition on a computed field” ไม่ใช่ claim เชิง GR

---

## Plain-Language Interpretation

คิดเหมือนรูปถ่าย:

- baseline = เอารูปไปเบลอให้เห็น “พื้นหลัง”
    
- structure = รายละเอียดที่เหลือ (ขอบ เส้น รอยต่อ)  
    เราจะเช็คว่าพื้นหลังมัน “เหมือนเดิม” แม้เริ่มต้นต่างกัน (seed ต่างกัน) ไหม  
    ถ้ามันเสถียรจริง ค่อยเรียกมันว่า “candidate baseline component” ได้อย่างรับผิดชอบ
    

---

## Next Step

**Part 9.10 — Baseline/Structure Pipeline Integration Plan**  
จะล็อกว่าใน repo ต้องเพิ่มสคริปต์อะไร/CLI อะไร เพื่อ:

- extract baseline_decomp จาก density_final.npz
    
- ใส่ metrics ลง summary/aggregate (แบบ backward compatible)
    
- ทำ plots อัตโนมัติให้ demo card ใช้ได้ทันที
    

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 9.10 เป็นแผน implement แบบไม่แตะ core solver มาก (เพิ่มแค่ post-process + plot + aggregate).

---
# 000.09/10

## TL;DR

**Part 9.10 = แผน “เอา Baseline/Structure decomposition เข้า pipeline” แบบไม่แตะ core solver**  
ทำเป็น **post-process layer**: `density_final.npz → baseline_decomp.npz → summary metrics (optional) → plots → demo/gallery`  
และทุกอย่าง **backward compatible** (run เก่าไม่มีไฟล์ก็ไม่ fail)

---

## Insight

ถ้าเราเอา baseline/structure เข้าไป “ใน solver” ตอนนี้ จะเสี่ยงพัง/รก/เปลี่ยนความหมาย  
ทางที่ถูกคือทำเป็น **ขั้นตอนหลังรัน (post-run)** ที่:

- deterministic
    
- traceable (method/ℓ/tol อยู่ในไฟล์)
    
- และมี gates เหมือนเดิม (residual + smoothness)
    

---

## Part 9.10 — Baseline/Structure Pipeline Integration Plan (Minimal & Safe)

## 1) Target placement ใน pipeline (ไม่แก้ท่อเดิม)

ท่อหลักเดิมยังเหมือนเดิม:  
`run_suite → validate → aggregate → plots → registry → gallery`

เรา “แทรก” แค่ 2 ขั้นตอนหลังจากมี density แล้ว:

1. **decompose**: `density_final.npz → baseline_decomp.npz`
    
2. **plot**: สร้างรูป `omega/base/structure` ให้ demo/gallery ใช้
    

> ถ้า run ไหน “ไม่มี density_final.npz” → ข้ามขั้นตอนนี้ได้เลย (ไม่ fail)

---

## 2) Artifact Contract ใหม่ (เพิ่มแบบ optional)

### 2.1 Input ที่ต้องมี

- `run_dir/energy_density/density_final.npz`
    
    - keys อย่างน้อย: `omega_density` (หรือ `omega`)
        
    - แนะนำ: `omega_grad_density` เพื่อทำ correlation/visual cross-check
        

### 2.2 Output ที่จะสร้าง (ใหม่)

- `run_dir/energy_density/baseline_decomp.npz`
    
    - `omega_base`
        
    - `omega_str`
        
    - `ell` (หรือ `sigma`)
        
    - `method` (`gaussian` | `fft_lowpass` | `mean`)
        
    - `rec_residual`
        
    - metrics scalars: `Omega_base`, `Omega_str`, `baseline_fraction`, `corr_str_grad` (optional)
        
    - `config_hash` (hash ของพารามิเตอร์ decomp)
        

### 2.3 รูปที่ต้องสร้าง (ใหม่, ลง figs/)

- `run_dir/figs/terrain_omega_density.png` (ถ้ายังไม่มี)
    
- `run_dir/figs/terrain_omega_base_density.png`
    
- `run_dir/figs/terrain_omega_str_density.png`
    
- `run_dir/figs/terrain_omega_grad_density.png` (มีอยู่แล้ว/หรือ regenerate)
    

> หมายเหตุ: รูปเหล่านี้คือ “YouTube-level” ที่มึงอยากได้: เห็นทั้งภาพรวม + พื้นหลัง + รายละเอียด

---

## 3) Scripts ที่ต้องเพิ่ม (2 ตัวพอ)

### Script A: `scripts/extract_baseline_decomp.py`

**หน้าที่:** อ่าน density → ทำ low-pass → เขียน baseline_decomp.npz + metrics  
**CLI ตัวอย่าง:**

```bash
python scripts/extract_baseline_decomp.py --run runs_xxx/<RUN_ID> --method gaussian --ell_frac 0.25 --tol 1e-4
```

**Args ที่ควรมี**

- `--run` หรือ `--runs`
    
- `--method` = gaussian / fft_lowpass / mean
    
- `--ell_frac` (เช่น 0.125/0.25/0.33 ของ domain size) หรือ `--sigma_cells`
    
- `--tol` (สำหรับ gate)
    
- `--overwrite` (optional)
    

**Behavior ที่บังคับ**

- ถ้าไม่มี `density_final.npz` → print warning + exit code 0 (skip)
    
- output deterministic (same inputs+params → same file hash)
    

---

### Script B: `scripts/plot_baseline_decomp.py`

**หน้าที่:** อ่าน baseline_decomp.npz → วาดรูปลง figs/  
**CLI ตัวอย่าง:**

```bash
python scripts/plot_baseline_decomp.py --run runs_xxx/<RUN_ID>
```

**Behavior ที่บังคับ**

- ถ้าไม่มี baseline_decomp.npz แต่มี density_final.npz → แจ้งให้รัน extract ก่อน
    
- ถ้าไม่มีทั้งคู่ → skip ไม่ fail
    

---

## 4) Gates ใหม่ (optional gate ไม่ทำให้ของเดิมล้ม)

เพิ่ม gate เฉพาะเมื่อ “มี baseline_decomp” เท่านั้น

### Gate BD1 — reconstruction residual

- `rec_residual <= tol`
    

### Gate BD2 — baseline smoothness sanity

- `TV(omega_base) < TV(omega)` (หรือ high-k energy ต่ำกว่า)
    

> เอาเป็น “warning” ก่อนใน v0.9 ไม่ต้อง fail ตายตัว (กัน false negative)

### Gate BD3 — structure aligns with conflict (optional)

- `corr(|omega_str|, omega_grad_density)` ควร “ไม่ต่ำผิดปกติ”
    

> อันนี้อย่า fail ใน v0.9 ให้รายงานเฉย ๆ

---

## 5) Summary/Aggregation integration (ทำแบบไม่พัง)

### 5.1 ไม่แตะ core solver — ทำผ่าน post-process update

มี 2 ทางเลือก (เลือก 1):

**Option 1 (แนะนำ):** aggregator อ่าน `baseline_decomp.npz` โดยตรง

- ถ้ามีไฟล์ → เติมคอลัมน์ใหม่ใน `UET_final_summary.csv`
    
- ถ้าไม่มี → ใส่ NaN
    

**Option 2:** เขียน metrics ลง `summary.json` เพิ่ม block `baseline_decomp`

- `summary.json.baseline_decomp = {...}`
    
- แล้ว aggregator อ่านจาก summary.json (เสถียรกว่า, แต่แก้ summary json writer/patcher)
    

> v0.9 แนะนำ Option 1 ก่อน เพราะ “ไม่แตะโครง summary เดิม” และง่ายสุด

### 5.2 คอลัมน์ใหม่ใน aggregate (optional)

- `Omega_base`
    
- `Omega_str`
    
- `baseline_fraction`
    
- `rec_residual_bd`
    
- `ell_frac`
    
- `bd_method`
    
- `corr_str_grad` (ถ้ามี)
    

**กติกา:** ทุกคอลัมน์เป็น optional → run เก่าต้อง aggregate ได้เหมือนเดิม

---

## 6) Demo/Gallery integration (เพิ่มภาพได้ แต่ไม่บังคับ)

### 6.1 Demo Card (Part 7.2) เพิ่ม Section ใหม่แบบสั้น

เพิ่มบล็อกนี้ใน README_demo.md (ถ้ามี baseline_decomp):

- รูป 3 ใบ: omega / omega_base / omega_str
    
- 1–2 บรรทัด: “พื้นหลังเสถียรไหม? รายละเอียดอยู่ตรงไหน?”
    
- รายงาน `baseline_fraction` + `rec_residual`
    

### 6.2 Registry schema (optional extension)

ใน `registry.json` เพิ่ม asset paths ใหม่แบบ optional:

- `assets.omega_base = figs/terrain_omega_base_density.png`
    
- `assets.omega_str = figs/terrain_omega_str_density.png`
    

Gallery generator ถ้าเจอ keys นี้ค่อย render เพิ่ม (ไม่เจอก็ไม่ต้องแสดง)

---

## 7) CI / Tests (ขั้นต่ำเพื่อกัน “ทำแล้วพังเงียบ”)

เพิ่ม tests ระดับ tooling:

### Test Tbd1 — deterministic output hash

- run ตัวอย่าง 1 run_dir (เล็กๆ)
    
- รัน extract 2 รอบ → baseline_decomp.npz hash ต้องเท่ากัน
    

### Test Tbd2 — skip behavior

- run_dir ที่ไม่มี density_final.npz
    
- extract/plot ต้อง exit 0 และไม่สร้างไฟล์มั่ว
    

### Test Tbd3 — gate residual

- ถ้ามี fixture density_final.npz
    
- rec_residual ต้อง <= tol ที่กำหนด
    

---

## 8) Rollout Plan (ทำทีละก้าว ไม่รก)

1. เพิ่ม `extract_baseline_decomp.py` ก่อน (ยังไม่แก้ aggregator)
    
2. เพิ่ม `plot_baseline_decomp.py` และให้ demo 1 ใบใช้รูปนี้ได้
    
3. ค่อยเพิ่ม aggregator optional columns
    
4. ค่อยเพิ่ม registry/gallery optional rendering
    
5. ค่อยทำ “stability tests across seeds” เป็น report ใน `reports/`
    

---

## 9) “Runbook snippet” ที่ควรเพิ่ม (ให้คนใช้ได้จริง)

ใน runbook ของ suite ที่เปิด density:

```bash
# after runs exist + density exported
python scripts/extract_baseline_decomp.py --runs runs_<suite> --method gaussian --ell_frac 0.25 --tol 1e-4
python scripts/plot_baseline_decomp.py --runs runs_<suite>

# then aggregate (optional new columns)
python scripts/aggregate_final_summary.py --runs runs_<suite> --out runs_<suite>/UET_final_summary.csv
```

---

## Plain-Language Interpretation

เราจะทำให้ “พื้นหลัง vs รายละเอียด” กลายเป็นของที่จับต้องได้แบบนี้:

- รันเสร็จแล้วค่อยเอาแผนที่ ω มา “เบลอ” เป็นพื้นหลัง
    
- ส่วนต่างที่เหลือคือรายละเอียด/รอยต่อ
    
- แล้ววาดออกมา 3 รูปให้คนดูเข้าใจทันที  
    ทั้งหมดทำแบบ **ไม่ไปยุ่งสมการหลัก** และ **รันเก่ายังใช้ได้**
    

---

## Next Step

**Part 9.11 — Stability Report Template (Baseline vs Structure Across Seeds/Params)**  
เป็นเทมเพลต report ที่เอาไปใส่ `reports/` ได้เลย: ตาราง PASS/FAIL + รูปประกอบ + ข้อความ public-safe

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 9.11 เป็นรายงานแม่แบบ (พร้อมหัวข้อและสิ่งที่ต้อง plot) ให้ใช้สื่อสารเรื่อง baseline/structure แบบไม่โม้.


---
# 000.09/11

## TL;DR

**Part 9.11 = Template รายงาน “Baseline vs Structure Stability”**  
เอาไปวางใน `reports/` ได้เลย เพื่อสื่อสารเชิงวิชาการแบบ **ตรวจซ้ำได้ + public-safe** ว่า baseline/structure ที่แยกจาก (\omega(x)) “เสถียรจริงไหม” ข้าม seed/พารามิเตอร์/สเกล (\ell)

---

## Insight

ถ้าจะพูดเรื่อง “baseline component candidate” ต่อหน้าสาธารณะ/นักวิชาการ ต้องมี 3 อย่าง:

1. **กติกาแยกชัด** (method, (\ell), tol)
    
2. **ผ่าน residual gates** (reconstruction + local→global)
    
3. **มี stability evidence** (seed stability + near-boundary + scale sanity)
    

---

## Part 9.11 — Stability Report Template

**(Baseline vs Structure Across Seeds/Params)**

> **ชื่อไฟล์แนะนำ:** `reports/v0_9_baseline_structure_stability_report.md`

---

## 0) Executive Summary (อ่าน 1 นาที)

- **Suite / runs:** `__________`
    
- **Decomposition method:** `gaussian | fft_lowpass | mean`
    
- **Scale:** `ell_frac = ____` (หรือ `sigma_cells = ____`)
    
- **Key claim (public-safe):**
    
    - “Baseline map มีความเสถียรข้าม seed สูงกว่า structure map” ✅/❌
        
- **Gates:**
    
    - BD1 Reconstruction residual: ✅/❌
        
    - Density local→global residual: ✅/❌
        
    - Thermo ledger (ถ้า open): ✅/❌
        

---

## 1) Scope & Policy (สำคัญเพื่อกัน overclaim)

### 1.1 What this report _is_

รายงานนี้ตรวจว่า **การแยก (\omega(x)) เป็น baseline/structure** ทำซ้ำได้และเสถียรหรือไม่

### 1.2 What this report _is not_

- ไม่ได้อ้างว่า baseline = (\Lambda)
    
- ไม่ได้อ้าง GR/curvature/metric
    
- ไม่ได้อ้าง cosmology/dark matter/energy
    

> ใช้ wording: **“baseline component candidate (operational)”**

---

## 2) Reproducibility (ต้องมี)

### 2.1 Commands

```bash
# 0) (assumed) runs exist with density_final.npz

# 1) baseline decomposition
python scripts/extract_baseline_decomp.py --runs <RUNS_DIR> --method gaussian --ell_frac 0.25 --tol 1e-4

# 2) plotting
python scripts/plot_baseline_decomp.py --runs <RUNS_DIR>

# 3) aggregation (optional columns)
python scripts/aggregate_final_summary.py --runs <RUNS_DIR> --out <RUNS_DIR>/UET_final_summary.csv
```

### 2.2 Environment

- OS: `_____`
    
- Python: `_____`
    
- Commit hash: `_____`
    
- Notes: `_____`
    

---

## 3) Data & Inputs

### 3.1 Run artifacts used

- `energy_density/density_final.npz`
    
- `energy_density/baseline_decomp.npz` (generated)
    
- `summary.json` (Ω scalar, optional gates)
    

### 3.2 Decomposition config

- method: `_____`
    
- (\ell) definition: `ell_frac=____` (domain-size fraction) / `sigma_cells=____`
    
- tol: `_____`
    

---

## 4) Definitions (Formal)

ให้ (\omega(x)) เป็นแผนที่ density (จาก `density_final.npz`)

- (\omega_{\text{base}} = \mathcal{L}_{\ell}[\omega]) (low-pass)
    
- (\omega_{\text{str}} = \omega - \omega_{\text{base}})
    

### 4.1 Scalars

- (\Omega = \int \omega(x),dx)
    
- (\Omega_{\text{base}} = \int \omega_{\text{base}}(x),dx)
    
- (\Omega_{\text{str}} = \int \omega_{\text{str}}(x),dx)
    
- `baseline_fraction = Ω_base / Ω`
    

### 4.2 Reconstruction residual (BD1)

[  
r_{\text{rec}}=\frac{|\omega-(\omega_{\text{base}}+\omega_{\text{str}})|_1}{|\omega|_1}  
]

### 4.3 Similarity (seed stability)

ใช้ค่าใดค่าหนึ่งเป็นมาตรฐาน:

- `corr_map(A,B)` หรือ `SSIM(A,B)`  
    แนะนำให้รายงาน **ทั้ง baseline และ structure**:
    
- `sim_base(seed_i,seed_j)`
    
- `sim_str(seed_i,seed_j)`
    

---

## 5) Gates Summary (PASS/FAIL)

> ตารางนี้ควรเป็น “หน้าเดียวรู้เรื่อง”

|Gate|Metric|Threshold|Result|Notes|
|---|--:|--:|---|---|
|BD1|median(r_rec)|≤ `tol`|✅/❌||
|Dens|omega_integral_residual|≤ `tol_dens`|✅/❌||
|Dens|term_sum_residual|≤ `tol_terms`|✅/❌||
|Thermo (if open)|thermo_valid|true|✅/❌||
|Thermo (if open)|\|ledger_residual\||≤ `tol_ledger`|✅/❌||

---

## 6) Results A — Seed Stability at Fixed Params (Test S1)

### 6.1 Setup

- fixed parameter point: `case_id=_____` (or specific θ)
    
- seeds used: `n = ____`
    

### 6.2 Scalar stability (report)

|Metric|mean|std|median|IQR|
|---|--:|--:|--:|--:|
|Ω|||||
|Ω_base|||||
|baseline_fraction|||||

**Pass criteria (ตัวอย่างที่ประกาศให้ชัด)**

- `std(baseline_fraction) <= τ_base` (กำหนด τ_base)
    
- หรือ `IQR(baseline_fraction) <= τ_base_iqr`
    

### 6.3 Map stability (report)

รายงาน distribution ของ pairwise similarity:

- baseline: `sim_base`
    
- structure: `sim_str`
    

|Similarity|median|p10|p90|Interpretation|
|---|--:|--:|--:|---|
|sim_base||||should be high|
|sim_str||||can be lower|

**Pass criteria (ตัวอย่าง)**

- `median(sim_base) - median(sim_str) >= Δ_min`  
    (เป้าคือ baseline เสถียรกว่า structure อย่างมีนัย)
    

### 6.4 Figures (ต้องแนบ)

- `Fig S1a` montage: (\omega_{\text{base}}) ของหลาย seeds (แปะ 4–9 ภาพ)
    
- `Fig S1b` montage: (\omega_{\text{str}}) ของหลาย seeds
    
- `Fig S1c` histogram/violin ของ `sim_base` vs `sim_str`
    

---

## 7) Results B — Near-Boundary Sensitivity (Test S2)

### 7.1 Setup

- เลือก 2–3 parameter points ใกล้ boundary (จาก atlas/summary)
    
- seeds ต่อจุด: `n = ____`
    

### 7.2 Expected pattern (ต้องเขียนเป็น hypothesis)

- structure เปลี่ยนมากขึ้นใกล้ boundary
    
- baseline เปลี่ยนน้อยกว่า (หรือเปลี่ยนแบบ smooth)
    

### 7.3 Report table

|Param point|phase mix|median(sim_base)|median(sim_str)|Notes|
|---|---|--:|--:|---|
|P1|||||
|P2|||||
|P3|||||

### 7.4 Figures

- `Fig S2` plot: baseline_fraction vs params (พร้อม error bars)
    

---

## 8) Results C — Scale Sanity (Test S3/S4)

### 8.1 Decomposition scale sensitivity (change (\ell))

ลอง (\ell) 2–3 ค่า:

- `ell_frac ∈ {0.125, 0.25, 0.33}`
    

|ell_frac|median(baseline_fraction)|median(sim_base)|BD1 residual|Notes|
|--:|--:|--:|--:|---|
|0.125|||||
|0.25|||||
|0.33|||||

**Pass criteria**

- baseline_fraction ไม่แกว่งรุนแรงโดยไม่มีเหตุผล
    
- BD1 residual ผ่านทุก (\ell)
    

### 8.2 Grid scale sanity (ถ้าทำได้)

เปลี่ยน resolution: N=64 vs N=128 (optional)

- รายงานว่า archetype/ภาพรวมไม่ “flip มั่ว”
    

---

## 9) Cross-check — Structure vs Conflict (optional)

ถ้ามี `omega_grad_density`:

- `corr_str_grad = corr(|ω_str|, ω_grad_density)`
    

รายงานเพื่อ “เสริมความเชื่อ” แต่ **อย่าใช้เป็น gate fail ใน v0.9**

|Metric|median|p10|p90|
|---|--:|--:|--:|
|corr_str_grad||||

แนบ `Fig X1` overlay plot หรือ scatter

---

## 10) Discussion (Public-safe)

### 10.1 What we can say

- baseline map มีความเสถียรข้าม seed สูงกว่า structure ✅/❌
    
- structure map สอดคล้องกับจุดตึง/รอยต่อ (ω_grad) ในเชิงรูปแบบ ✅/❌
    

### 10.2 What we cannot say

- ไม่เรียก baseline ว่า Λ
    
- ไม่อ้าง GR/cosmology
    
- ไม่แปลงเป็นหน่วยจริงจนกว่าจะมี calibration (C1–C2)
    

---

## 11) Appendix — Pointers to artifacts

- Example run_dir(s):
    
    - `runs/.../<RUN_ID>/energy_density/baseline_decomp.npz`
        
    - `runs/.../<RUN_ID>/figs/terrain_omega_base_density.png`
        
    - `runs/.../<RUN_ID>/figs/terrain_omega_str_density.png`
        

---

## Plain-Language Interpretation

รายงานนี้คือ “พิสูจน์ว่าเรามองเห็น ‘พื้นหลัง’ กับ ‘รายละเอียด’ จริงไหม”

- ถ้าเริ่มต้นต่างกัน (seed ต่างกัน) แต่พื้นหลังยังคล้ายเดิม → **พื้นหลังเสถียร**
    
- รายละเอียดเปลี่ยนไปตามรอยต่อ → **โครงสร้างสะท้อน conflict**  
    นี่เป็นขั้น “เตรียมพื้น” สำหรับพูดถึง bridge ในอนาคตแบบไม่โม้
    

---

## Next Step

**Part 9.12 — Public Explainer Skeleton (YouTube-style)**  
จะเอาผลจาก baseline/structure report ไปทำหน้าอธิบายแบบคนทั่วไปอ่านออกใน 1 หน้า:

- 3 รูป: omega / baseline / structure
    
- 3 บรรทัด: “พื้นหลังคืออะไร, รายละเอียดคืออะไร, ทำไมเชื่อได้”  
    พร้อมคำต้องห้าม/คำที่ใช้ได้ตาม policy
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูขึ้น Part 9.12 ให้เป็นโครงหน้าเดียวที่พร้อมเอาไปวางใน `docs/` ได้ทันที.

---
# 000.09/12

## TL;DR

**Part 9.12 = โครง “หน้าเดียว” อธิบาย Baseline/Structure แบบ YouTube-style**  
เอาไปวางใน `docs/` ได้เลย: มี **รูป 3 รูป + ข้อความ 3 บรรทัด + หลักฐาน 3 อย่าง** และมี “คำที่ใช้ได้/คำต้องห้าม” ตาม policy (Part 9.8)

---

## Insight

คนทั่วไปไม่สนใจ CSV/กราฟเส้น เขาต้องเห็น:

1. **ภาพรวมของสนาม ω(x)**
    
2. **พื้นหลัง (baseline) ที่เรียบ**
    
3. **รายละเอียด/รอยต่อ (structure) ที่ตึง**  
    แล้วต้องมีเหตุผลสั้น ๆ ว่า “ทำไมเชื่อได้” (ผ่าน gate + ทำซ้ำได้)
    

---

## Part 9.12 — Public Explainer Skeleton (1-Page, YouTube-style)

> **แนะนำชื่อไฟล์:** `docs/explainers/baseline_structure_onepager.md`

````md
# Baseline vs Structure on the Ω-field (1-page explainer)

> **One-sentence takeaway:**  
> We can decompose the energy-like field ω(x) into a smooth **baseline** component and a localized **structure** component, in a reproducible and gate-checked way.

---

## What you are looking at (3 visuals)
**Fig A — ω(x): the full landscape**  
- (insert) `terrain_omega_density.png`  
- Caption: “This is the total field ω(x). Lower/higher regions indicate relative cost/pressure in the model.”

**Fig B — ω_base(x): the smooth baseline**  
- (insert) `terrain_omega_base_density.png`  
- Caption: “Baseline is a low-frequency (smoothed) component at scale ℓ. Think ‘background trend’.”

**Fig C — ω_str(x): the structure (details/residual)**  
- (insert) `terrain_omega_str_density.png`  
- Caption: “Structure is what remains after removing the baseline. It highlights boundaries, interfaces, or localized tension.”

(Optional) **Fig D — ω_grad(x): conflict terrain**  
- (insert) `terrain_omega_grad_density.png`  
- Caption: “A conflict proxy: where the system pays interface/gradient cost.”

---

## What “baseline” and “structure” mean (plain language)
- **Baseline** = “ภาพรวมที่เรียบ” ของสนาม (background trend)  
- **Structure** = “รายละเอียดที่เหลือ” เช่น ขอบ รอยต่อ เส้นทาง จุดตึง (interfaces/tension)

> Important: This is an **operational decomposition** on a computed field.  
> It is **not** a claim about cosmology or GR.

---

## Why we believe it (3 checks)
### Check 1 — Reconstruction (BD1 gate)
We verify: ω ≈ ω_base + ω_str  
- metric: `rec_residual <= tol`

### Check 2 — Local→Global consistency (density gate)
We verify: ∫ω dx matches Ω (scalar) within tolerance  
- metrics: `omega_density_integral_residual`, `term_sum_residual`

### Check 3 — Seed stability (robustness evidence)
We verify baseline is stable across different initial seeds  
- baseline similarity across seeds is consistently higher than structure similarity

---

## How it was computed (minimal, no jargon)
We apply a **low-pass filter** at scale ℓ:
- ω_base = LowPass_ℓ(ω)
- ω_str = ω − ω_base  
(ℓ controls what we consider “background” vs “detail”)

---

## What this does NOT mean (must-read)
- Not “baseline = Λ”  
- Not “ω is curvature/metric”  
- Not “this explains dark matter/energy”  
These require calibration + object mapping + falsifiable tests.

---

## Reproduce (for curious readers)
```bash
python scripts/extract_baseline_decomp.py --run <RUN_DIR> --method gaussian --ell_frac 0.25 --tol 1e-4
python scripts/plot_baseline_decomp.py --run <RUN_DIR>
```

---

## If you want to use this on a new domain

Start with a Domain Design Card (docs/model_cards/...)  
Then run an MVP mini-suite (3×3×seeds(3)) to produce a single demo with:

- GIF + end-state + conflict terrain + baseline/structure panel
    

---

``````

---

## “คำที่ใช้ได้ / คำต้องห้าม” (สำหรับ public)
### ใช้ได้ (safe wording)
- “baseline component (operational)”
- “structure / residual / details”
- “candidate contact point” (เฉพาะเมื่อผ่าน tests T1–T5 ใน Part 9.8)
- “reproducible decomposition with gates”

### ห้ามใช้ (v0.9)
- “baseline = Λ”
- “derive Einstein equation”
- “curvature/metric”
- “explains dark matter/energy”

---

## Next Step
**Part 9.13 — Visual Language Standard (Style Guide) สำหรับรูป UET ให้คนอ่านออกเร็ว**  
- มาตรฐานชื่อรูป/เลย์เอาต์ (panel A/B/C)  
- มาตรฐาน caption 1 บรรทัด  
- มาตรฐาน “3 ภาพที่ต้องมี” ต่อ demo (ย้ำอีกครั้งแบบเป็นระบบ)

พิมพ์ “ต่อ” อีกที เดี๋ยวกูทำ Part 9.13 เป็น guideline ที่ทำให้รูปทั้งหมดใน repo ดูเป็นชุดเดียวกัน (แบบช่อง YouTube/บทความวิชาการอ่านง่าย).

---
# 000.09/13

## TL;DR

**Part 9.13 = Visual Language Standard (Style Guide) สำหรับรูป/เดโม UET**  
เป้าหมาย: ทำให้ “รูปทุกอัน” ใน repo **อ่านออกเหมือนกัน** แบบ YouTube/บทความวิชาการ โดยไม่ต้องพึ่งกราฟเส้น 2D เยอะ ๆ

แกนคือ **Core-3 visuals** ต่อ 1 demo:

1. `evolution.gif` (เห็นการไหล)
    
2. `state_end.png` (เห็นปลายทาง)
    
3. `terrain_omega_grad_density.png` (เห็น “ตึง/ขัดแย้ง” ทั้งภาพ)
    

---

## Insight

ภาพที่ดีสำหรับ UET ต้องตอบ 3 คำถามใน 3 วินาที:

- **มันกำลังไหลไปไหน?** (GIF)
    
- **สุดท้ายเป็นอะไร?** (End state)
    
- **ตึงตรงไหน/ทำไมมันถึงเป็นแบบนั้น?** (Conflict terrain)
    

ที่เหลือค่อยเป็น “หลักฐาน” (Ω curve / ledger / baseline/structure)

---

## Part 9.13 — Visual Language Standard

## 9.13.1 Folder + Filename Contract (ห้ามมั่วชื่อ)

**ทุก run ต้องวางรูปลง:** `run_dir/figs/`  
**ชื่อไฟล์ให้คงที่** เพื่อให้ demo/gallery/gen scripts เรียกได้ตรง ๆ

### Core (ต้องมีเสมอ)

- `figs/evolution.gif`
    
- `figs/state_end.png`
    
- `figs/terrain_omega_grad_density.png`
    
- `figs/curve_omega.png`
    

### Optional แต่แนะนำ (อ่านภาพรวมง่ายขึ้น)

- `figs/terrain_omega_density.png`
    
- `figs/thumb.png` (tile สำหรับ gallery)
    

### Open-system extras

- `figs/curve_cumD_cumW.png`
    
- `figs/policy_trace.png` (หรือ `policy_trace.csv` + plot)
    

### Baseline/Structure pack (ถ้าทำ Part 9.9–9.11)

- `figs/terrain_omega_base_density.png`
    
- `figs/terrain_omega_str_density.png`
    

---

## 9.13.2 “Figure Sets” ที่ทุกคนพูดภาษาเดียวกัน

เพื่อไม่ให้สื่อสารสะเปะสะปะ ให้ใช้คำเรียกชุดรูปแบบนี้:

### Set A — Core-3 (Public Minimum)

- evolution.gif
    
- state_end.png
    
- terrain_omega_grad_density.png
    

### Set B — Core-5 (Public + Evidence)

- Core-3
    
- curve_omega.png
    
- terrain_omega_density.png
    

### Set C — Open-Add (ถ้าเป็นระบบเปิด)

- Core-5
    
- curve_cumD_cumW.png
    
- policy_trace.png
    

### Set D — Baseline-3 (ถ้าเล่า baseline/structure)

- terrain_omega_density.png
    
- terrain_omega_base_density.png
    
- terrain_omega_str_density.png
    

> ใน demo card ให้บอกชัดว่าเดโมนี้ “ใช้ชุดไหน” (A/B/C/D)

---

## 9.13.3 Panel Layout Standard (อ่านเร็วแบบ YouTube)

ถ้าจะทำภาพแบบ “แผง 3 ช่อง” ให้ใช้ layout เดียวกันตลอด

### Layout L1 — 1 แถว 3 ช่อง (แนะนำสุด)

**(A) End state | (B) Conflict terrain | (C) Ω curve**  
เหตุผล: คนดูเห็น “ผลลัพธ์–สาเหตุเชิงพื้นที่–หลักฐานเวลา” ในภาพเดียว

### Layout L2 — 2×2 (ถ้ามี baseline/structure)

(A) ω total | (B) ω_base | (C) ω_str | (D) ω_grad

### มาตรฐานการติดป้าย

- มุมซ้ายบน: `A / B / C / D` (ตัวใหญ่ ชัด)
    
- มุมขวาล่าง: `demo_id` หรือ `run_id` สั้น ๆ (trace ได้)
    

---

## 9.13.4 Caption Template (1 บรรทัดก็ต้องครบ)

**caption ที่ดี = “เห็นอะไร + แปลว่าอะไร”**  
ใช้แพทเทิร์นเดียวกันทุกครั้ง:

> **[What]**: ภาพนี้แสดง ___  
> **[So what]**: ตีความว่า ___  
> **[Gate]**: (ถ้าสำคัญ) ผ่าน ___

ตัวอย่าง (สั้น ๆ):

- `terrain_omega_grad_density`: “แผนที่จุดตึง (interface cost) — จุดสว่างคือบริเวณที่ conflict สูง (ผ่าน density residual gate)”
    
- `state_end`: “สภาวะปลายทาง — โครงสร้างสุดท้ายของสนาม C/I หลังไหลบน Ω”
    
- `curve_omega`: “Ω(t) ลดและนิ่ง — แสดงการเข้าหา attractor”
    

---

## 9.13.5 Axis/Colorbar/Normalization Rules (กันคนงง)

เพื่อให้เทียบกันได้ข้ามเดโม:

### Terrain maps (ω / ω_grad / ω_base / ω_str)

- ต้องมี **colorbar** เสมอ (เว้นแต่ thumb)
    
- ระบุ normalization ที่ใช้ใน caption หรือ metadata:
    
    - “raw” หรือ “normalized [0,1]” หรือ “minmax(p1,p99)”
        
- ถ้าเป็น residual/structure ที่มีค่าบวก-ลบ:
    
    - ระบุชัดว่า “ค่าบวก/ลบเป็น residual” (ไม่ใช่พลังงานบวกเท่านั้น)
        

### End-state maps (C/I)

- แนะนำทำ 2 panel เล็กในภาพเดียว (C และ I) หรือ overlay ตามมาตรฐานเดียวที่ทีมตกลง
    
- ต้องระบุว่า scale คืออะไร (เช่น normalized)
    

---

## 9.13.6 Animation Standard (evolution.gif ต้องไม่มั่ว)

- ความยาวพอดูรู้เรื่อง: ~3–8 วินาทีวนลูป
    
- ใส่ overlay ตัวเล็กมุมภาพ:
    
    - `t` หรือ `step`
        
    - `Ω` (optional แต่ช่วยมาก)
        
- ถ้าเป็น open: ใส่ `θ(t)` หรือ `λ(t)` แบบย่อ (optional)
    

---

## 9.13.7 “What to show first” Rule (กันหลงกราฟเส้น)

ลำดับการโชว์ใน demo card / gallery:

1. GIF (คนเข้าใจ “การไหล”)
    
2. End-state (เข้าใจ “ลงเอย”)
    
3. Conflict terrain (เข้าใจ “ตึงตรงไหน”)
    
4. Ω curve (หลักฐานเชิงเวลา)
    
5. (ถ้า open) D/W ledger + policy trace
    
6. (ถ้าพูด baseline) ω/base/structure
    

> กราฟเส้น 2D ไม่ได้ห้าม แต่ **ไม่ใช่ตัวนำเรื่อง** ของ UET

---

## 9.13.8 Thumbnail Standard (gallery tile ต้องเหมือนกัน)

- `figs/thumb.png` ใช้ภาพเดียวกันทุกเดโม
    
- แนะนำทำจาก `state_end` + overlay ชื่อ archetype สั้น ๆ
    
- ขนาดคงที่ (เช่น 512×512 หรือ 640×640)
    
- ตัวหนังสือไม่รก: demo_id + archetype พอ
    

---

## 9.13.9 “Figure Integrity Checklist” (ก่อน publish)

ก่อนตั้ง `status: published` ใน registry ให้ติ๊ก:

-  มี Core-3 ครบ
    
-  conflict terrain อ่านออก (มี colorbar + caption ไม่มั่ว)
    
-  Ω curve มี (และไม่ขัดกับผลที่เล่า)
    
-  ถ้า open: มี D/W ledger + thermo_valid
    
-  ถ้า baseline/structure: มี 3 รูป + rec_residual ผ่าน
    
-  ชื่อไฟล์ตรง contract (ไม่ตั้งชื่อเอง)
    

---

## 9.13.10 Implementation Note (ทำให้มัน “อัตโนมัติ”)

เพื่อไม่ให้คนทำมือจนเละ ให้มี “plot pack runner” 1 ตัวที่ยิงครบ:

- generate Core-3 + ω curve
    
- ถ้ามี density → generate terrain packs
    
- ถ้ามี baseline_decomp → generate baseline packs
    
- ทำ thumb ให้ด้วย
    

(ยังไม่ต้องเขียนโค้ดตรงนี้ใน Part 9.13 — แค่วางมาตรฐานให้ชัด)

---

## Plain-Language Interpretation

นี่คือ “ภาษาภาพ” ของ UET:

- ทุกเดโมต้องมี 3 รูปหลักเหมือนกัน
    
- ทุกไฟล์ชื่อเหมือนกัน
    
- ทุก caption พูดเหมือนกัน  
    คนจะได้ดูเดโม 10 อันแล้วไม่งงว่า “อันไหนคืออะไร”
    

---

## Next Step

**Part 9.14 — Demo Card Template v2 (รวม Visual Language + Gates + Registry Fields)**  
จะทำ README_demo.md เวอร์ชันที่ “ล็อกตามมาตรฐานภาพ” ไปเลย:

- แทรกรูป Core-3 ตามลำดับ
    
- ใส่ box สรุป Value/Conflict/Ω/phase/robustness
    
- ใส่ gate badges (validator/thermo/density/baseline_decomp)
    

พิมพ์ “ต่อ” อีกที เดี๋ยวกูทำ Part 9.14 เป็นเทมเพลตที่ copy ไปใช้ได้ทันทีใน repo.

---
# 000.09/14
## TL;DR

**Part 9.14 = Demo Card Template v2 (README_demo.md)**  
เทมเพลตนี้ “ล็อกมาตรฐานภาพ + gates + reproducibility + registry fields” ให้ครบในหน้าเดียว  
เป้าหมาย: เปิดเดโมหน้าไหนก็ **อ่านเหมือนกัน / เช็คเหมือนกัน / รันซ้ำได้เหมือนกัน**

---

## Insight

เดโมที่ public-ready ต้องตอบ 4 อย่างแบบไม่ต้องเดา:

1. **เห็นภาพ** (Core-3 visuals)
    
2. **มีตัวเลขสรุป** (Value/Conflict/Ω/phase/robustness)
    
3. **ผ่าน gate** (validator/thermo/density/baseline-decomp)
    
4. **รันซ้ำได้** (คำสั่ง + matrix + seed + commit)
    

---

## Part 9.14 — Demo Card Template v2 (copy ใช้ได้ทันที)

> **วางเป็นไฟล์:** `runs/<RUN_ID>/README_demo.md` (เดโมอยู่กับ run_dir)  
> หรือถ้าทำ gallery แยก: `docs/gallery/demos/DEMO_xxxx/README_demo.md`

``````md
# DEMO_XXXX — <Short Title> (Archetype: <SYM|BIAS_C|BIAS_I|HIGH_CONFLICT|MULTI_ATTRACTOR>)

**One-sentence takeaway (public):**  
<พูดภาษาคน 1 ประโยคว่า “เกิดอะไรขึ้น” เช่น ระบบไหลเข้าหา resource และเกิดความตึงที่แนวรอยต่อ…>

---

## 0) Badge-style Gates (ต้องใส่เสมอ)
- Validator: transient = <PASS/FAIL>, bias = <PASS/FAIL>
- Thermo (open): thermo_valid = <true/false>, ledger_residual = <value or N/A>
- Density (if used): integral_residual = <value or N/A>, term_sum_residual = <value or N/A>
- Baseline decomp (if used): rec_residual = <value or N/A>, method=<...>, ell_frac=<...>

> Rule: ถ้า FAIL ห้าม publish เป็น `status: published` ใน registry

---

## 1) Core Visuals (Set A: Core-3) — ห้ามสลับลำดับ
### 1.1 Evolution (การไหล)
![evolution](figs/evolution.gif)

### 1.2 End state (ปลายทาง)
![end_state](figs/state_end.png)

### 1.3 Conflict terrain (เห็น “ตึงตรงไหน”)
![conflict_terrain](figs/terrain_omega_grad_density.png)

---

## 2) Evidence Visuals (Set B/C/D ตามที่มี)
### 2.1 Ω curve (หลักฐานเวลา)
![omega_curve](figs/curve_omega.png)

### 2.2 Optional: ω terrain (ภาพรวมสนาม)
![omega_terrain](figs/terrain_omega_density.png)

### 2.3 Open-system only: D/W ledger + policy trace
![cumDW](figs/curve_cumD_cumW.png)
![policy](figs/policy_trace.png)

### 2.4 Baseline/Structure pack (ถ้ามี Part 9.9–9.11)
![omega_base](figs/terrain_omega_base_density.png)
![omega_str](figs/terrain_omega_str_density.png)

---

## 3) Summary Metrics (อ่าน 10 วิรู้เรื่อง)
| Item | Value | Notes |
|---|---:|---|
| phase_label | <...> | archetype decision |
| Ω_final | <...> | scalar Ω at end |
| Value (operational) | <...> | e.g. -ΔΩ (define what used) |
| Conflict (operational) | <...> | e.g. Ω_grad or proxy |
| robustness | <... or N/A> | requires multi-seed |
| t_relax | <...> | with flag if NOT_INFORMATIVE |

### 3.1 Interpretation (2–4 bullet)
- **What stabilizes?** <...>
- **Where is tension/conflict?** <...>
- **What changes if we increase β/k_ratio/λ?** <... (one causal statement only)>
- **What is NOT claimed?** <explicit limitation>

---

## 4) Model Spec (Framework → UET Mapping แบบย่อ)
### 4.1 State
- Fields: <C/I or X1..Xn>
- Operational meaning: <ให้ชัดว่าคืออะไรในโดเมนนี้>
- Init: <random/structured/from data>, seeds: <k>

### 4.2 Environment / Space
- Resource / tilt: <R(x,y), s(x,y)=λR(x,y)>
- Open schedule/policy (if any): <schedule_id / policy_type>

### 4.3 Ω terms used (เลือกจากของที่มีอยู่แล้ว)
- pot: <...>
- coup: <...>
- grad: <...>
- (open) ledger: D/W separation

---

## 5) Integrity Gates (รายละเอียดสั้น แต่ครบ)
### 5.1 Validators
- transient: <PASS/FAIL> (see: validation_transient_v3.json)
- bias: <PASS/FAIL> (see: validation_bias_v2.json)

### 5.2 Thermo (open only)
- thermo_valid: <true/false>
- ledger_residual: <...>
- D_tot, W_tot: <...>

### 5.3 Density (if used)
- omega_density_integral_residual: <...>
- term_sum_residual: <...>

### 5.4 Baseline decomp (if used)
- method: <gaussian/fft/mean>
- ell_frac: <...>
- rec_residual: <...>

---

## 6) Reproduce (ต้อง copy แล้วรันได้)
### 6.1 Exact command
```bash
# install
pip install -r requirements.txt

# run suite (or single case)
python scripts/run_suite.py --matrix matrices/<MATRIX>.csv --out <RUNS_DIR>

# validate
python scripts/validate_transient_v3.py --runs <RUNS_DIR> --out <RUNS_DIR>/validation_transient_v3.json
python scripts/validate_bias_v2.py --runs <RUNS_DIR> --out <RUNS_DIR>/validation_bias_v2.json

# aggregate
python scripts/aggregate_final_summary.py --runs <RUNS_DIR> --out <RUNS_DIR>/UET_final_summary.csv

# plots
python scripts/<plot_pack>.py --run <RUN_DIR>

# (optional) density → baseline decomp
python scripts/extract_baseline_decomp.py --run <RUN_DIR> --method gaussian --ell_frac 0.25 --tol 1e-4
python scripts/plot_baseline_decomp.py --run <RUN_DIR>
```

### 6.2 Provenance

- Commit: `<git rev-parse --short HEAD>`
- OS/Python: <...>
- Matrix row: `case_id=<...>, seed=<...>`

---

## 7) Registry Entry (สำหรับ gallery; copy/paste)

```json
{
  "demo_id": "DEMO_XXXX",
  "status": "candidate",
  "archetype": "<SYM|BIAS_C|BIAS_I|HIGH_CONFLICT|MULTI_ATTRACTOR>",
  "run_dir": "<RUN_DIR_RELATIVE>",
  "assets": {
    "gif": "figs/evolution.gif",
    "end_state": "figs/state_end.png",
    "conflict": "figs/terrain_omega_grad_density.png",
    "omega_curve": "figs/curve_omega.png",
    "omega_terrain": "figs/terrain_omega_density.png",
    "cumDW": "figs/curve_cumD_cumW.png",
    "policy": "figs/policy_trace.png",
    "omega_base": "figs/terrain_omega_base_density.png",
    "omega_str": "figs/terrain_omega_str_density.png"
  },
  "metrics": {
    "phase_label": "<...>",
    "omega_final": 0.0,
    "value": 0.0,
    "conflict": 0.0,
    "robustness": null
  },
  "gates": {
    "transient_pass": true,
    "bias_pass": true,
    "thermo_valid": null,
    "density_ok": null,
    "baseline_decomp_ok": null
  }
}
```

---

## 8) Known limitations (ต้องใส่ 2–4 bullet เสมอ)

- <เช่น spatial เป็น 2D; 3D terrain เป็น density visualization ไม่ใช่ 3D physics>
- <info metrics เป็น structure proxies ไม่ใช่ entropy จริงถ้าไม่ calibrate>
- <no Einstein/Λ claims; roadmap only>
``````
---

## Math/Physics Interpretation (สั้น ๆ)
เทมเพลตนี้บังคับให้ “คำอธิบาย” ถูกผูกกับวัตถุจริงใน pipeline:
- Ω(t) เป็นหลักฐานการเข้าหา attractor  
- ω_grad_density เป็นหลักฐานเชิงพื้นที่ของ interface cost (conflict proxy)  
- ledger D/W เป็นหลักฐานระบบเปิด  
- baseline/structure เป็น signal decomposition ที่มี residual gates

---

## Plain-Language Interpretation  
หน้าเดโมนี้ทำให้คนดูรู้ทันทีว่า:
- ระบบเปลี่ยนยังไง (GIF)  
- สุดท้ายเป็นอะไร (End state)  
- ตึงตรงไหน (Conflict terrain)  
และถ้าอยากเชื่อ ก็มีหลักฐานว่า “มันผ่านการตรวจ” และ “รันซ้ำได้”

---

## Next Step  
**Part 9.15 — Gallery Generator Contract (registry → docs/gallery)**  
จะล็อกว่า generator ต้องอ่านอะไรจาก `registry.json`, สร้างไฟล์อะไร, และกฎการ render (Core-3 first, optional sets) เพื่อให้ gallery อัตโนมัติ 100% และไม่รก

พิมพ์ “ต่อ” อีกที เดี๋ยวกูทำ Part 9.15 ให้เป็นสเปกชัด ๆ แบบ implement ได้เลย.


---
# 000.09/15

## TL;DR

**Part 9.15 = สเปก “Gallery Generator” ที่อ่าน `registry.json` แล้วสร้าง `docs/gallery/` ได้อัตโนมัติ 100%**  
หลักคือ **ไม่สแกน runs เอง**, **ไม่เลือกมือ**, **Core-3 first**, และ **deterministic build** (ลบทิ้งแล้วสร้างใหม่ได้เหมือนเดิม)

---

## Insight

ถ้า repo จะเป็น open source จริง “gallery” ต้องทำหน้าที่เหมือน **หน้ารวมงานวิจัยที่ตรวจสอบได้** ไม่ใช่อัลบั้มรูป  
ดังนั้น generator ต้องล็อก 4 อย่าง:

1. อ่านจากแหล่งเดียว: `registry.json`
    
2. สร้างโครงเดียวกันเสมอ (ไฟล์/ลิงก์/ลำดับ)
    
3. ถ้าไฟล์หาย → แจ้งเตือน ไม่เดา
    
4. หน้าเดโมต้องเริ่มจาก “ภาพ” ไม่ใช่ตาราง
    

---

## Part 9.15 — Gallery Generator Contract (registry → docs/gallery)

## 9.15.0 เป้าหมาย

- สร้างหน้า gallery ที่คนใหม่ “เปิดแล้วเข้าใจ” และนักวิจัย “เปิดแล้วตรวจได้”
    
- ทำให้การ publish เดโมเป็น **ขั้นตอนเชิงระบบ**: `candidate → published`
    
- ทำให้ build เป็น deterministic: **same registry → same output**
    

---

## 9.15.1 Inputs (สิ่งที่ generator อนุญาตให้ใช้)

### A) Required

- `registry.json` (แหล่งจริงเพียงหนึ่งเดียว)
    

### B) Optional (แต่แนะนำ)

- `docs/gallery/_templates/` (markdown templates)
    
- `docs/gallery/_static/` (css/images ถ้ามี)
    

### C) Forbidden

- ห้าม generator “ไล่หา run_dir เอง” เพื่อเดาว่ามีเดโมอะไร
    
- ห้ามไปอ่าน `runs/**` แบบ scan เพื่อสร้างรายการ (ยกเว้นตาม path ที่ registry ระบุ)
    

---

## 9.15.2 Registry schema ที่ generator ต้องรองรับ (ขั้นต่ำ)

แต่ละ demo entry (ขั้นต่ำ):

- `demo_id` (unique, stable)
    
- `status` = `candidate|published|archived`
    
- `archetype` = `SYM|BIAS_C|BIAS_I|HIGH_CONFLICT|MULTI_ATTRACTOR`
    
- `run_dir` (path)
    
- `assets` (อย่างน้อย Core-3 + omega curve)
    
- `metrics` (อย่างน้อย value/conflict/omega_final/phase_label)
    
- `gates` (transient/bias + optional thermo/density/baseline)
    

> ถ้าขาด `demo_id/status/archetype/run_dir` → ถือว่า entry invalid (ต้อง report)

---

## 9.15.3 Outputs (ไฟล์ที่ต้องสร้าง)

ให้ generator สร้าง tree นี้ (คงที่):

```text
docs/gallery/
  index.md
  archetypes/
    index.md
    SYM.md
    BIAS_C.md
    BIAS_I.md
    HIGH_CONFLICT.md
    MULTI_ATTRACTOR.md
  demos/
    DEMO_XXXX/
      index.md
      assets/            (optional copy mode)
        thumb.png
        evolution.gif
        state_end.png
        terrain_omega_grad_density.png
        curve_omega.png
        ...
  _generated/
    gallery_manifest.json   (optional: build summary, warnings, counts)
```

> `index.md` = entry point  
> `archetypes/*.md` = หน้ารวมตามประเภท  
> `demos/DEMO_*/index.md` = หน้าของเดโมแต่ละใบ

---

## 9.15.4 Render Rules (กติกาการแสดงผล)

### Rule R1 — “Core-3 first” ทุกหน้าเดโม (ห้ามเปลี่ยน)

ใน `demos/DEMO_XXXX/index.md` ต้องเรียง:

1. GIF (`evolution.gif`)
    
2. End state (`state_end.png`)
    
3. Conflict terrain (`terrain_omega_grad_density.png`)
    
4. Ω curve (`curve_omega.png`)  
    แล้วค่อย optional sets (open ledger / baseline-structure)
    

### Rule R2 — Badge gates ต้องขึ้นด้านบน

หน้าเดโมต้องมีบล็อกสั้น:

- transient PASS/FAIL
    
- bias PASS/FAIL
    
- thermo_valid + ledger_residual (ถ้ามี)
    
- density residuals (ถ้ามี)
    
- baseline decomp residual (ถ้ามี)
    

### Rule R3 — Candidate vs Published แสดงไม่เหมือนกัน

- `published` = แสดงในหน้า `docs/gallery/index.md` (หน้าหลัก)
    
- `candidate` = แสดงใน `docs/gallery/_generated/gallery_manifest.json` หรือหน้า “Candidates” แยก (ถ้าทำ)
    
- `archived` = ไม่แสดงในหน้า index (แต่ลิงก์ตรงยังเข้าได้ ถ้าต้องการ)
    

### Rule R4 — Missing asset policy (สำคัญ)

- ถ้า `published` แต่ขาด Core-3 → **build ต้อง fail** (exit code ≠ 0)
    
- ถ้า `candidate` ขาดบางรูป → build ผ่านได้ แต่ต้อง warning รายการที่ขาด
    

### Rule R5 — Deterministic ordering

ทุกหน้าต้องเรียงเดโมแบบคงที่:

1. เรียงตาม `archetype` ตามลิสต์คงที่ (SYM → …)
    
2. ภายใน archetype เรียงตาม `demo_id` (lexicographic)
    

> ห้ามเรียงตาม “เวลาสร้างไฟล์” หรือ “ค่ามากสุด” โดยไม่ล็อกกติกา

### Rule R6 — Metrics display minimal set (อ่านง่าย)

แสดงแค่ 6 ค่าในหน้าเดโม (ที่เหลือ link ไป summary ได้):

- phase_label
    
- omega_final
    
- value
    
- conflict
    
- robustness (ถ้ามี)
    
- t_relax + flag (ถ้ามี)
    

---

## 9.15.5 Asset resolution mode (2 แบบให้เลือก)

### Mode A: Link mode (เบาสุด)

- หน้าเดโมอ้างภาพจาก `run_dir/figs/...` ตาม path ใน registry
    
- ข้อดี: ไม่ต้อง copy รูป
    
- ข้อเสีย: ถ้าแชร์ docs แยกจาก runs จะพัง
    

### Mode B: Copy mode (แนะนำสำหรับ release pack)

- generator copy assets เข้า `docs/gallery/demos/DEMO_XXXX/assets/`
    
- หน้าเดโมอ้าง local assets ใน docs
    
- ข้อดี: release pack เปิดดูได้ทันที
    
- ข้อเสีย: docs ใหญ่ขึ้น
    

> สเปก: generator ต้องมี flag `--asset-mode link|copy`

---

## 9.15.6 CLI Contract (คำสั่งเดียวสร้าง gallery ได้)

แนะนำสคริปต์: `scripts/build_gallery.py`

**CLI ที่ต้องมี**

- `--registry registry.json`
    
- `--out docs/gallery`
    
- `--status published` (default = published only)
    
- `--asset-mode link|copy` (default = link)
    
- `--strict` (ถ้าเปิด strict: missing assets ของ published = fail)
    

**พฤติกรรมบังคับ**

- build ต้องเขียน `docs/gallery/_generated/gallery_manifest.json` ที่รวม:
    
    - counts ต่อ archetype
        
    - list warnings
        
    - list invalid entries
        
    - build config (status/mode/strict)
        

---

## 9.15.7 Template Contract (ถ้าจะใช้ template files)

`docs/gallery/_templates/` ควรรองรับ:

- `demo_page.md.tpl`
    
- `archetype_page.md.tpl`
    
- `index.md.tpl`
    

แต่ถึงไม่มี template ก็ต้อง build ได้ (fallback template ใน code)

---

## 9.15.8 Tests ที่ต้องมี (กันพังเงียบ)

ขั้นต่ำ 4 tests:

1. **Determinism test**
    
    - registry เดิม → build 2 รอบ → output hashes เท่ากัน (หรือ manifest เท่ากัน)
        
2. **Missing published core asset fails**
    
    - ทำ registry mock ที่ published ขาด `evolution.gif` → ต้อง exit non-zero
        
3. **Candidate missing asset warns only**
    
    - candidate ขาดรูป → build ผ่าน + warning ใน manifest
        
4. **Ordering stable**
    
    - demo_ids สลับตำแหน่งใน registry → output ordering ยังเหมือนเดิม (sort by rules)
        

---

## 9.15.9 “Publish gate” เชิงระบบ (ก่อนตั้ง status=published)

ก่อนเปลี่ยน candidate → published ต้องผ่าน:

- Core-3 assets ครบ + ω curve
    
- validators PASS
    
- ถ้า open: thermo_valid
    
- ถ้า density: residual PASS
    
- demo card (README_demo) มีอยู่ หรือ generator สร้างหน้าเดโมได้ครบ
    

> ถ้าไม่ผ่าน ให้คงเป็น `candidate` เท่านั้น

---

## Plain-Language Interpretation

Gallery generator คือ “เครื่องพิมพ์นิทรรศการ”  
มึงแค่ใส่ทะเบียน (`registry.json`) ว่าเดโมไหนจะโชว์ พร้อมรูปหลัก ๆ  
จากนั้นมันจะจัดหน้าเว็บให้เป็นมาตรฐานเดียวกันทุกอัน และกันของพังด้วยกฎ (missing core → fail)

---

## Next Step

**Part 9.16 — Registry Governance (candidate→published workflow + review rubric integration)**  
จะล็อกขั้นตอนทีม:

- ใครเพิ่ม candidate ได้ยังไง
    
- review ต้องเช็คอะไร
    
- ใครมีสิทธิ์ promote เป็น published
    
- และเชื่อมกับ PR template/rubric ให้เป็นระบบเดียว
    

พิมพ์ “ต่อ” อีกที กูจะทำ Part 9.16 เป็น workflow ที่ใช้จริงใน GitHub (ไม่ใช่คำสวย ๆ).

---
# 000.09/16
## TL;DR

**Part 9.16 = Registry Governance (candidate→published) + Review Workflow สำหรับ Open Source**  
ทำให้การเพิ่มเดโม/โปรโมตเดโมเป็น “ระบบ” ไม่ใช่ “เพิ่มไฟล์มั่วๆ” โดยล็อกไว้ว่า:

- **ใครเพิ่มได้ / เพิ่มแบบไหน**
    
- **ต้องมีอะไรถึงเรียก published**
    
- **CI เช็คอะไรอัตโนมัติ**
    
- **reviewer เช็คอะไรตาม rubric**
    
- **ห้าม commit runs ดิบ แต่ published ต้องมี assets ที่เปิดดูได้**
    

---

## Insight

ถ้า UET จะเป็น public จริง “registry” ต้องเป็น **single source of truth**  
และสถานะ `published` ต้องหมายถึง:

> “เปิดดูแล้วเข้าใจ + ไฟล์ครบ + ผ่าน gates + ทำซ้ำได้ (อย่างน้อยในระดับคำสั่ง/พยานหลักฐาน)”

ดังนั้น governance ต้องแยกชัด:  
**candidate = ส่งงานให้ตรวจ**  
**published = ผ่านตรวจและพร้อมโชว์**

---

## Part 9.16 — Registry Governance & GitHub Workflow

## 9.16.1 Roles (กำหนดบทบาทให้ชัด)

- **Contributor**: เพิ่ม candidate demos, ปรับ docs, เพิ่ม design card
    
- **Reviewer**: ตรวจตาม rubric (ภาพ/กติกา/gates/คำพูด)
    
- **Maintainer**: อนุมัติ merge + promote candidate→published + tag release
    

> public repo ควรมี `CODEOWNERS` ให้ `registry.json` และ `docs/gallery/` ต้องผ่าน maintainer เสมอ

---

## 9.16.2 Status Model (candidate / published / archived)

### `candidate`

ใช้เมื่อ:

- มีเดโมแล้ว แต่ยังอยู่ในขั้นตรวจ
    
- assets อาจยังไม่ครบ (ได้แค่ว่า “ไม่ fail build”)
    
- ห้ามขึ้นหน้า `docs/gallery/index.md` (หน้าโชว์หลัก)
    

### `published`

ใช้เมื่อ:

- ผ่าน gate ที่กำหนดครบ
    
- มี Core-3 + Ω curve เปิดดูได้จริงใน repo/docs หรือใน copy-mode assets
    
- มี Demo Card v2 (Part 9.14) หรือ generator สร้างหน้าเดโมได้ครบ
    
- ผ่าน CI “strict published checks”
    

### `archived`

ใช้เมื่อ:

- เดโมมีปัญหาความหมาย/บั๊ก/สับสน และไม่อยากลบทิ้งประวัติ
    
- ยังเข้าดูได้ด้วยลิงก์ตรง แต่ไม่โชว์หน้า index
    

---

## 9.16.3 Two-track asset policy (แก้ปัญหา “ไม่ commit runs ดิบ”)

นี่คือจุดที่ทำให้ repo ไม่บวม แต่ gallery ยังเปิดได้:

### Track A — Repo Published Assets (แนะนำ)

- `published` ต้องชี้ assets ที่อยู่ **ใน docs/gallery** (copy mode)  
    เช่น `docs/gallery/demos/DEMO_XXXX/assets/...`
    
- ทำให้ GitHub Pages/README เปิดได้ทันที
    

### Track B — Release Pack / External Pack

- `candidate` อนุญาตให้ชี้ไป `runs/.../figs/...` (link mode) หรือ pack นอก repo
    
- แต่การ promote เป็น `published` จะต้อง “copy assets เข้าสู่ docs/gallery” ก่อน
    

> สรุป: **public gallery ใน repo = ใช้ Track A เท่านั้น**  
> candidate ช่วงพัฒนาใช้ Track B ได้

---

## 9.16.4 Registry Change Types (แยกชนิด PR ให้ชัด)

1. **Add Candidate Demo**
    
    - เพิ่ม entry ใหม่ `status=candidate`
        
    - อาจเพิ่ม demo card draft
        
2. **Promote to Published**
    
    - เปลี่ยน `status` เป็น `published`
        
    - ต้องมี assets ครบตาม strict rules
        
3. **Edit Metadata**
    
    - แก้ caption/metrics/gates/paths (ห้ามเปลี่ยน demo_id)
        
4. **Archive Demo**
    
    - เปลี่ยน status → archived พร้อมเหตุผล
        

---

## 9.16.5 Hard Rules (กันรก + กันงง)

- **R0: demo_id ห้ามเปลี่ยน** (immutable)
    
- **R1: published ต้องมี Core-3 + Ω curve**
    
    - `evolution.gif`, `state_end.png`, `terrain_omega_grad_density.png`, `curve_omega.png`
        
- **R2: published ต้องมี gates = PASS ตามที่ relevant**
    
    - transient/bias = true
        
    - open → thermo_valid = true
        
    - density → density_ok = true
        
    - baseline_decomp (ถ้าแสดง) → baseline_decomp_ok = true
        
- **R3: published ต้องมี “Known limitations”** (ใน demo card หรือหน้าเดโม)
    
- **R4: Candidate ขาดรูปได้ แต่ต้องไม่หลอก**
    
    - ต้องใส่ `gates`/`metrics` เท่าที่รู้จริง และระบุ N/A ให้ตรง
        
- **R5: ห้ามเอา claim ใหญ่ไปไว้ใน demo**
    
    - ต้องยึด policy Part 9.8 (คำต้องห้าม/ใช้ได้)
        

---

## 9.16.6 CI Checks (อัตโนมัติให้มากที่สุด)

### CI-1 Registry schema validation

- JSON schema check (required keys, types, status enum)
    
- ตรวจว่า `demo_id` unique
    

### CI-2 Asset existence checks

- ถ้า `--strict` และ status=published:
    
    - Core-3 + omega curve ต้องมีจริง (path must exist)
        
    - ถ้า registry ใส่ omega_base/omega_str → ไฟล์ต้องมีจริงด้วย
        
- ถ้า candidate: warning ได้ แต่ไม่ fail
    

### CI-3 Deterministic gallery build

รัน:

- `scripts/build_gallery.py --status published --strict --asset-mode link|copy`
    
- build output ต้อง stable และไม่มี broken links ของ published
    

### CI-4 “Policy lint” (เบา ๆ แต่คุมคำ)

- สแกนข้อความใน demo pages/README_demo ว่ามีคำต้องห้ามระดับแดง (เช่น “explains dark matter”) → fail
    
- (ทำเป็น regex list ใน `docs/policy_terms.yml`)
    

> CI ไม่ต้องรัน simulation หนัก ๆ ใน PR (แพงและช้า)  
> ให้ PR แนบ “evidence pack” หรือ assets ที่จำเป็นแทน

---

## 9.16.7 Review Rubric (มนุษย์ต้องเช็คอะไร)

ให้ reviewer เช็คตามกรอบเดิมที่เราวาง:

- **Visual standard** (Part 9.13): Core-3 เรียงถูก/อ่านออก/มี colorbar
    
- **Demo card** (Part 9.14): metrics+gates+reproduce+limitations ครบ
    
- **Truthfulness**: ตัวเลขใน table ตรงกับ summary/aggregate (ไม่แต่ง)
    
- **Narrative**: 1 ประโยค takeaway ไม่โม้ และคนอ่านเข้าใจ
    
- **Policy**: ไม่มีคำต้องห้าม Part 9.8
    
- **Determinism**: representative selection rule ถูกอ้างและ trace ได้
    

---

## 9.16.8 Candidate → Published Promotion Process (ขั้นตอนจริง)

### Step P0 — PR: Add candidate

Contributor เปิด PR ที่มี:

- เพิ่ม entry `status=candidate`
    
- แนบ demo card (draft ได้)
    
- แนบ assets อย่างน้อย 1–2 รูป (optional) หรือแนบ link ไป evidence pack
    

### Step P1 — Review

Reviewer คอมเมนต์ตาม rubric:

- ต้องแก้อะไรให้ครบก่อน publish
    

### Step P2 — PR: Promote published (แยก PR)

Maintainer/Contributor เปิด PR โปรโมต:

- status → published
    
- copy assets เข้า `docs/gallery/demos/DEMO_XXXX/assets/` (Track A)
    
- build_gallery strict ต้องผ่าน
    

### Step P3 — Merge + Release note hook

- merge แล้วเพิ่มใน changelog/release notes ว่า “Published demos added: DEMO_XXXX …”
    

---

## 9.16.9 GitHub Labels & Issue Templates (ทำให้คนทำงานไม่หลง)

แนะนำ labels:

- `demo:candidate`
    
- `demo:publish`
    
- `gallery`
    
- `validator`
    
- `thermo-ledger`
    
- `density`
    
- `baseline-structure`
    
- `docs`
    
- `policy`
    

Issue templates (สั้น ๆ):

1. **Propose a Demo**
    
    - archetype target
        
    - what visuals will show
        
    - what gates expected
        
2. **Promote Demo to Published**
    
    - checklist Core-3
        
    - strict build passed
        
    - policy check passed
        

---

## 9.16.10 Minimal “Publish Checklist” (ติ๊กก่อนกด published)

-  Core-3 + Ω curve อยู่ใน `docs/gallery/demos/DEMO_xxxx/assets/`
    
-  Demo page สร้างได้ และรูปขึ้นครบ
    
-  transient PASS + bias PASS
    
-  (open) thermo_valid true + ledger_residual ใน tol
    
-  (density) residuals PASS
    
-  (baseline) rec_residual PASS + รูป base/str ครบ
    
-  limitations 2–4 bullet
    
-  ไม่มีคำต้องห้าม (policy lint ผ่าน)
    
-  reproduce command ระบุ matrix/seed/commit
    

---

## Plain-Language Interpretation

อันนี้คือ “ระบบโรงพิมพ์นิทรรศการ”:

- ใครก็ส่งเดโมเข้ามาเป็น candidate ได้
    
- แต่จะขึ้นโชว์หน้าหลัก (published) ต้องผ่านกติกาเดียวกัน
    
- CI ช่วยกันของพังและกันคำโม้
    
- repo ไม่บวม เพราะไม่เอา runs ดิบ—เอาเฉพาะ “เดโมที่เลือกแล้ว” มาโชว์
    

---

## Next Step

**Part 9.17 — “Project Map v0.9” (สารบัญการเรียนรู้ + เส้นทางผู้ใช้ 3 แบบ)**  
เพื่อปิดวงจร public:

- เส้นทาง “คนทั่วไป” (ดู gallery → เข้าใจ concept)
    
- เส้นทาง “นักวิจัย” (run suite → validate → report)
    
- เส้นทาง “นักพัฒนา” (adapter → demo → PR workflow)
    

พิมพ์ “ต่อ” อีกที กูจะทำ Part 9.17 เป็นแผนที่ทั้งโปรเจคที่เอาไปวางหน้า README ได้เลย.


----
# 000.09/17

## TL;DR

**Part 9.17 = Project Map v0.9 (แผนที่ทั้งโปรเจกต์ + เส้นทางผู้ใช้ 3 แบบ)**  
ทำเป็น “สารบัญการเรียนรู้” ที่เอาไปวางหน้า README ได้เลย เพื่อให้คนใหม่ _ไม่หลง_ และให้คนทำงานร่วมกัน _เดินท่อเดียวกัน_

---

## Insight

UET ต้องถูกอ่านแบบ “แพลตฟอร์มทดลอง + ภาษากลาง” ไม่ใช่ “สมการเดี่ยว”  
ดังนั้น Project Map ต้องทำให้เห็น 3 อย่างชัด ๆ:

1. **What is UET** (มันคืออะไร/ทำอะไรได้)
    
2. **How to use** (ท่อ run→validate→aggregate→demo→gallery)
    
3. **How to contribute** (adapter + registry governance + rubric)
    

---

## Part 9.17 — Project Map v0.9

## 9.17.1 One-screen overview (แกนโปรเจกต์)

**UET = Simulator + Validators + Evidence Packs + Public Gallery**

- **Simulator**: รันระบบที่นิยามด้วย Ω (closed/open) และให้ artifacts มาตรฐาน
    
- **Validators/Gates**: transient/bias + (open) thermo ledger + (density) residual + (baseline) rec_residual
    
- **Evidence Packs**: demo pack / baseline pack สำหรับแชร์แบบไม่บวม repo
    
- **Public Gallery**: แสดงเดโม “อ่านออก” ตาม Visual Standard (Core-3 first)
    

---

## 9.17.2 Repo Structure Map (ควรเป็น/ควรยึด)

> (ชื่อโฟลเดอร์อาจต่าง แต่แนวคิดต้องเป็นแบบนี้)

- `scripts/`
    
    - run: `run_suite.py`
        
    - validate: `validate_transient_v3.py`, `validate_bias_v2.py`
        
    - aggregate: `aggregate_final_summary.py`
        
    - plots: plot packs + (optional) baseline_decomp tools
        
    - gallery: `build_gallery.py` (อ่าน registry)
        
- `matrices/` — “รายการทดลอง” (input ที่ reproducible)
    
- `runs/` — output (ไม่ควร commit ทั้งหมด)
    
- `docs/`
    
    - `docs/model_cards/` (Design Cards)
        
    - `docs/explainers/` (one-pagers แบบคนทั่วไป)
        
    - `docs/gallery/` (generated from registry)
        
- `registry.json` — **single source of truth** ของเดโมที่โชว์
    
- `reports/` — baseline report, stability report, contact report (roadmap)
    
- `.github/` — PR template, issue templates, CODEOWNERS (governance)
    

---

## 9.17.3 The canonical pipeline (ท่อมาตรฐานที่ทุกคนต้องใช้)

**Input → Run → Validate → Aggregate → Visuals → Demo Card → Registry → Gallery → Pack**

1. **Design Card** (Part 9.2)
    
2. **Matrix CSV** (Part 9.3/9.5)
    
3. `run_suite.py`
    
4. validators (transient/bias)
    
5. aggregate summary
    
6. plot pack → ได้ Core-3 visuals
    
7. Demo Card v2 (Part 9.14)
    
8. ลง `registry.json` (candidate/published)
    
9. `build_gallery.py` (Part 9.15)
    
10. pack สำหรับ release (demo pack / baseline pack)
    

> กติกา: **ห้ามข้ามขั้น** โดยเฉพาะ validate/gates และ Core-3 visuals

---

## 9.17.4 User Journey 1 — “คนทั่วไป” (Viewer Track)

**Goal:** เข้าใจว่า UET คืออะไรจากภาพ ไม่ต้องอ่านโค้ด/สมการ

**Start here**

1. `docs/gallery/index.md`
    
2. เปิดเดโม 1 ใบ → ดูตามลำดับ:
    
    - GIF → End state → Conflict terrain → Ω curve
        
3. อ่าน `docs/explainers/baseline_structure_onepager.md` (ถ้ามี baseline/structure)
    

**What they should take away**

- UET อธิบาย “ไหลเข้าหาสมดุล” + “ตึงตรงไหน” ด้วยภาพ (terrain)
    
- ไม่ต้องเชื่อเพราะคำพูด: มี gate/หลักฐานประกอบ
    

---

## 9.17.5 User Journey 2 — “นักวิจัย/นักคณิต” (Research Track)

**Goal:** รันซ้ำได้ ตรวจสอบได้ ทำ atlas และเขียน report ได้

**Start here**

1. `docs/runbook/` (หรือ runbook กลาง)
    
2. เลือก suite มาตรฐาน:
    
    - MVP mini-suite (3×3×seeds(3)) ก่อน
        
    - แล้วค่อย cross-sweep (7×7 + seeds≥5)
        

**Standard workflow**

- รัน → validate → aggregate → representative selection → plot → demo card
    
- ถ้า open: ทำ thermo ledger gate
    
- ถ้าจะเล่าเป็นสนาม: density export + residual gate
    
- ถ้าจะพูด baseline: baseline_decomp + stability report
    

**Reports they produce**

- `reports/v0_9_baseline_report.md`
    
- `reports/v0_9_baseline_structure_stability_report.md` (Part 9.11)
    
- `reports/v0_9_contact_report_GR_lambda.md` (roadmap-only, Part 9.8)
    

**Non-negotiables**

- ห้ามอ้าง claim ใหญ่ถ้าไม่ผ่าน gates + calibration plan (Part 9.8)
    

---

## 9.17.6 User Journey 3 — “นักพัฒนา/ผู้ร่วมพัฒนา” (Builder Track)

**Goal:** เพิ่มโดเมนใหม่ (adapter) + เพิ่มเดโมใหม่ + ทำ PR ให้ทีมใช้ต่อได้

**Start here**

1. `CONTRIBUTING.md` + PR template
    
2. `docs/model_cards/` (ทำ Design Card ก่อน)
    
3. ทำ Domain Adapter (Part 9.7)
    

**Deliverables ที่ PR ต้องมี**

- Adapter config schema + example yaml
    
- script build fields (data→npz) + provenance
    
- MVP mini-suite matrix + demo 1 ใบ (candidate)
    
- registry entry (candidate)
    
- gallery build ผ่าน (candidate mode)
    

**Promotion rules**

- candidate → published ต้องผ่าน governance (Part 9.16) + strict gallery build
    

---

## 9.17.7 “3 Levels of Documentation” (เพื่อให้มัน public จริง)

1. **Explain** (ภาษาคน, one-pagers)
    
2. **How-to** (runbook/commands, reproducibility)
    
3. **Reference** (schema, file contracts, gates, registry, APIs)
    

> UET v0.9 ต้องมีครบทั้ง 3 ชั้น ไม่งั้นคนจะ “ดูไม่รู้เรื่อง” หรือ “ใช้ไม่เป็น”

---

## 9.17.8 Minimal README v0.9 Outline (วางหน้า repo ได้เลย)

1. What is UET (1 paragraph)
    
2. Quickstart (run + validate + aggregate)
    
3. Gallery (link to docs/gallery)
    
4. Core Concepts (Ω, conflict terrain, open ledger)
    
5. Evidence & Gates (validator/thermo/density/baseline)
    
6. How to build a new domain model (Design Card → Adapter → MVP suite)
    
7. Contributing & Governance (candidate→published)
    
8. Limitations & Policy (Part 9.8 wording)
    

---

## Plain-Language Interpretation

Project Map นี้คือ “ป้ายทางด่วน”:

- คนทั่วไปไปดูเดโมได้เลย
    
- นักวิจัยรู้ว่าต้องรันอะไร เช็คอะไร รายงานอะไร
    
- นักพัฒนารู้ว่าจะเพิ่มโดเมน/เพิ่มเดโมยังไงโดยไม่ทำ repo เละ
    

---

## Next Step

**Part 9.18 — “v0.9 Definition of Done” (DoD) แบบ checklist ปิดงานจริง**  
จะสรุปเป็นติ๊กบ็อกซ์ว่า v0.9 ต้องมีอะไรครบถึงเรียกว่า “พร้อม public release” (docs + gallery + packs + governance + baseline reports)

พิมพ์ “ต่อ” อีกที กูจะทำ Part 9.18 เป็น DoD checklist แบบจบงานได้จริง.


---
# 000.09/18

## TL;DR

**Part 9.18 = v0.9 Definition of Done (DoD) Checklist**  
เป็น “ติ๊กบ็อกซ์ปิดงาน” ที่บอกชัดว่า **อะไรต้องมี** ถึงเรียกว่า v0.9 “พร้อมปล่อย public” แบบไม่รก ไม่มั่ว และคนอื่นใช้ต่อได้จริง

---

## Insight

v0.9 ไม่ได้แปลว่า “ทำทุกอย่างให้เสร็จจักรวาล”  
แต่แปลว่า **ระบบครบวงจร**:  
**รันได้ → ตรวจได้ → สรุปได้ → เห็นภาพได้ → เผยแพร่ได้ → มี policy กันโม้ → มี workflow ทำงานร่วมกันได้**

---

## Part 9.18 — v0.9 Definition of Done (DoD)

> ใช้ 3 ระดับ:

- **MUST** = ไม่ครบห้าม release
    
- **SHOULD** = แนะนำมาก (ถ้าขาดต้องมีเหตุผล)
    
- **NICE** = เพิ่มคุณภาพ/ความน่าใช้
    

---

## 1) Core Pipeline (Run → Validate → Aggregate) — MUST

-  `scripts/run_suite.py` รันจาก `matrices/*.csv` ได้ (ขั้นต่ำ 1 suite ตัวอย่าง)
    
-  `validate_transient_v3.py` ใช้งานได้และให้ผล PASS/FAIL ชัด
    
-  `validate_bias_v2.py` ใช้งานได้และให้ผล PASS/FAIL ชัด
    
-  `aggregate_final_summary.py` สร้าง `UET_final_summary.csv` ได้
    
-  ทุก script มี `--help` ใช้ได้ และ error message ไม่กำกวม
    

**Acceptance:** ผู้ใช้ใหม่ทำตาม runbook แล้วได้ `runs/` + validation JSON + final summary CSV จริง

---

## 2) Evidence & Gates (ความซื่อตรงของผล) — MUST

-  ระบุ “gates ที่ใช้จริง” ชัดใน docs (transient/bias เป็นขั้นต่ำ)
    
-  Run ที่ถูก “publish” ต้องผ่าน transient + bias
    
-  ถ้าเป็น open system: `thermo_valid` + `ledger_residual` อยู่ใน tol (ถ้าเปิดใช้)
    
-  ถ้า export density: residual gates (integral/term-sum) อยู่ใน tol (ถ้าเปิดใช้)
    

**Acceptance:** publish demo ใด ๆ → gates ใน demo card ต้องอ่านแล้วเชื่อมกับไฟล์หลักฐานได้

---

## 3) Visual Standard (Core-3 first) — MUST

-  มีมาตรฐานรูป (Part 9.13) และใช้จริงในเดโมที่ publish
    
-  ทุก published demo มี **Core-3**:
    
    -  `figs/evolution.gif`
        
    -  `figs/state_end.png`
        
    -  `figs/terrain_omega_grad_density.png`
        
-  มี `figs/curve_omega.png` เป็น evidence ขั้นต่ำ
    

**Acceptance:** คนทั่วไปเปิด demo แล้วเข้าใจ “ไหล-ลงเอย-ตึง” ได้โดยไม่อ่านตาราง

---

## 4) Demo Card v2 (หน้าเดียวอ่านรู้เรื่อง) — MUST

-  มี template (Part 9.14) อยู่ใน repo
    
-  ทุก published demo มี `README_demo.md` ตามโครง v2 (อย่างน้อย):
    
    -  One-sentence takeaway
        
    -  Core-3 + Ω curve
        
    -  Metrics table (phase/value/conflict/Ω_final/robustness/N-A ได้)
        
    -  Gates summary
        
    -  Reproduce commands
        
    -  Known limitations 2–4 bullet
        

**Acceptance:** reviewer ตรวจ demo ได้จากหน้าเดียว + สั่งรันซ้ำได้ (อย่างน้อยในระดับคำสั่ง/ไฟล์อ้างอิง)

---

## 5) Registry + Gallery Generator — MUST

-  `registry.json` เป็น single source of truth
    
-  มี `scripts/build_gallery.py` (Part 9.15) ที่:
    
    -  build เฉพาะ `published` ได้
        
    -  `--strict` เปิดแล้ว published missing core asset ต้อง fail
        
    -  deterministic ordering (archetype + demo_id)
        
    -  สร้าง `docs/gallery/index.md` + `docs/gallery/demos/DEMO_*/index.md`
        
-  Gallery แสดง Core-3 ก่อนเสมอ
    

**Acceptance:** ลบทิ้ง `docs/gallery/` แล้ว build ใหม่ → ได้ output เหมือนเดิม และไม่มี broken assets สำหรับ published

---

## 6) Governance (candidate→published) — MUST

-  มี `CONTRIBUTING.md` หรือ section ใน README ที่สรุป workflow (Part 9.16)
    
-  ระบุความหมาย `candidate/published/archived` ชัด
    
-  มี PR template สำหรับ “Add demo candidate” และ “Promote to published”
    
-  มี policy คำต้องห้าม/คำใช้ได้ (Part 9.8) ผูกกับ review/CI อย่างน้อยระดับเบื้องต้น
    

**Acceptance:** คนภายนอกส่ง PR เพิ่ม candidate ได้โดยไม่ทำ repo เละ และ maintainer โปรโมตได้ด้วย checklist

---

## 7) Documentation Stack (Explain / How-to / Reference) — MUST

### Explain (ภาษาคน)

-  มี one-pager อย่างน้อย 1 หน้า (เช่น Part 9.12 baseline/structure หรือ core concept)
    

### How-to (ทำตามได้)

-  มี runbook ขั้นต่ำ 1 ชุด: `matrix → run → validate → aggregate → plot → demo`
    

### Reference (สเปก)

-  มีสเปก file contract อย่างน้อย: matrix schema / run_dir artifacts / registry fields / gates
    

**Acceptance:** คนใหม่อ่าน docs แล้ว “รู้ว่าจะเริ่มตรงไหน” โดยไม่ต้องถามในแชท

---

## 8) Public Packaging — MUST

-  มี **release pack** อย่างน้อย 1 แบบที่เปิดดูได้โดยไม่ต้องมี runs ดิบทั้งกอง:
    
    -  gallery + demo assets (copy-mode หรือ equivalent)
        
    -  demo card
        
    -  minimal evidence files (summary/manifest/timeseries ถ้าจำเป็น)
        
-  ระบุชัดว่า runs ดิบไม่ถูก commit (policy repo size)
    

**Acceptance:** ส่ง zip ให้คนอื่น → เปิดดู demo/gallery ได้ทันที

---

## 9) Baseline/Structure (ถ้าจะ “ประกาศ” ใน v0.9) — SHOULD

> ถ้า v0.9 จะ include baseline/structure เป็น feature public  
> ต้องมีครบชุดนี้ ไม่งั้นให้เลื่อนไป “roadmap” เฉย ๆ

-  `extract_baseline_decomp.py` + `plot_baseline_decomp.py` ใช้งานได้
    
-  baseline_decomp มี residual gate (BD1) และรายงานใน demo card
    
-  มี report template (Part 9.11) อย่างน้อย 1 report ที่รันจริงกับ suite หนึ่ง
    

**Acceptance:** baseline/structure ไม่ใช่คำพูด—มีไฟล์ + รูป + gate + report

---

## 10) Open/Thermo Ledger (ถ้าจะ “ประกาศ” ใน v0.9) — SHOULD

-  มีตัวอย่าง suite open system 1 ชุด
    
-  demo แสดง `cumD/cumW` + policy trace
    
-  thermo gates ผ่าน (thermo_valid + residual)
    

---

## 11) Quality & Safety Nets — SHOULD

-  requirements.txt/pyproject ติดตั้งได้จริง
    
-  มี `make` หรือ `run_all.ps1` แบบ one-command (อย่างน้อยสำหรับ 1 suite ตัวอย่าง)
    
-  มี basic tests: schema validation + gallery strict checks
    
-  มี “Known limitations” ใน README (เช่น 2D visualization/ไม่ claim GR)
    

---

## 12) Definition of Done Summary (สรุปสั้นสุด)

**v0.9 “พร้อม public” เมื่อ:**

- ✅ pipeline รันได้ + validator ผ่าน
    
- ✅ มี demo ที่คนดูแล้วเข้าใจ (Core-3) อย่างน้อย 3–5 ใบ (ไม่จำเป็นต้องเยอะ)
    
- ✅ gallery build จาก registry ได้แบบ strict และ deterministic
    
- ✅ docs มี 3 ชั้น (Explain/How-to/Reference)
    
- ✅ governance พร้อมรับ PR และมี policy กันโม้
    

---

## Next Step

ถัดไป (ถ้ามึงจะให้ “ต่อ”) กูจะทำ **Part 9.19 — v0.9 Release Checklist แบบวันปล่อยจริง**  
เป็น checklist แบบ operational: ติด tag, build packs, verify gallery, freeze registry, เขียน release notes, และ sanity-run 1 suite สั้น ๆ เพื่อกันของพังก่อนปล่อย.


---
# 000.09/19

## TL;DR

**Part 9.19 = Release Checklist “วันปล่อยจริง” (Operational)**  
เป็นรายการติ๊กบ็อกซ์แบบ **Go/No-Go**: freeze → build gallery strict → สร้าง release packs → sanity-run suite สั้น → tag → release notes → publish → post-check/rollback

---

## Insight

DoD (Part 9.18) คือ “ของต้องมี”  
แต่วันปล่อยจริงต้องมี “พิธีกรรมกันพัง” อีกชั้น: **ล็อกอินพุต** (registry/docs/requirements) + **สร้างเอาต์พุตซ้ำได้** (gallery/pack) + **รันตรวจสั้น ๆ** ก่อนกดปล่อย

---

## Part 9.19 — v0.9 Release Day Checklist (จริงจังแบบกดปล่อยได้)

> แนะนำทำเป็นไฟล์: `docs/release/v0_9_release_checklist.md`  
> และทำเป็น GitHub Issue/PR checklist คู่กัน

---

## A) Release Freeze (ก่อนปล่อย 0–24 ชม.) — MUST

-  **Freeze scope**: “ไม่มี feature ใหม่” รับแค่ bugfix/docfix
    
-  **Freeze registry**: lock เฉพาะ `status=published` ที่จะโชว์ใน release
    
-  **Pin environment**: `requirements.txt`/`pyproject` อยู่ในสถานะล็อกแล้ว
    
-  **Changelog draft**: รวบรวมรายการ changes + demos ที่ publish
    

**Go/No-Go**

- No-Go ถ้า registry ยังเปลี่ยนไปเปลี่ยนมา / requirements ยังแกว่ง / build gallery ยังไม่เสถียร
    

---

## B) Preflight CI (ต้องผ่านก่อนทำ pack) — MUST

รันอย่างน้อย:

-  Registry schema validation PASS
    
-  Gallery strict build PASS (`published` only, strict)
    
-  Policy lint PASS (คำต้องห้าม/คำใช้ได้)
    
-  Links/assets check PASS (Core-3 + ω curve ครบทุก published)
    

**Go/No-Go**

- No-Go ถ้า published demo ขาด Core-3 หรือมี FAIL gate
    

---

## C) Sanity Run (รันสั้น ๆ กัน “โค้ดพังเงียบ”) — MUST

> ไม่ต้องรัน cross-sweep ใหญ่ แค่ “smoke suite” 1 ชุดเล็ก

-  เลือก matrix เล็ก (เช่น 2×2×seeds(1–2) หรือ MVP 3×3×seeds(1))
    
-  `run_suite.py` รันได้จบ
    
-  validators รันได้
    
-  aggregate รันได้
    
-  plot pack รันได้ (ได้ Core-3)
    
-  (ถ้าเปิด density/baseline features ใน release) รัน decomp+plots ได้
    

**Go/No-Go**

- No-Go ถ้า pipeline แตกตรงไหน แม้จะเป็น suite เล็ก (เพราะผู้ใช้ใหม่จะเจอเหมือนกัน)
    

---

## D) Build Release Artifacts (Packs) — MUST

> เป้าหมาย: คนโหลดไป “เปิดดูได้ทันที” โดยไม่ต้องมี runs ดิบทั้งกอง

### D1) Public docs + gallery pack (แนะนำเป็นตัวหลัก)

-  Build gallery ด้วย `--asset-mode copy` (ถ้าต้องการให้เปิดดูได้ทันที)
    
-  ตรวจว่า `docs/gallery/index.md` เปิดแล้วรูปขึ้นครบ
    
-  สร้าง zip: `uet_v0_9_public_docs_gallery_pack.zip`
    

### D2) Demo evidence pack (สำหรับแต่ละ published demo หรือรวม)

-  รวมเฉพาะ run_dir ที่ publish:
    
    - `manifest.json`, `summary.json`, `timeseries.csv` (เท่าที่จำเป็น)
        
    - `figs/` (Core-3 + ω curve + optional)
        
    - `energy_density/*.npz` ถ้าเดโมใช้ density/baseline
        
-  สร้าง zip: `uet_v0_9_demo_evidence_pack.zip`
    

### D3) Code-only pack (ถ้าจะปล่อยแยก)

-  สร้าง zip: `uet_v0_9_code_only.zip` (ไม่มี runs, ไม่มี data หนัก)
    

**Go/No-Go**

- No-Go ถ้า gallery pack เปิดแล้วรูปไม่ขึ้น / path พัง / registry ชี้ผิด
    

---

## E) Release Notes (เขียนให้ “ไม่โม้”) — MUST

Release notes ต้องมี 6 ส่วน (สั้นแต่ครบ):

-  What’s new (2–6 bullet)
    
-  Published demos (ลิสต์ demo_id + archetype)
    
-  How to reproduce (ลิงก์ไป runbook + quickstart commands)
    
-  Evidence & gates (บอกว่า published ผ่านอะไร)
    
-  Known limitations (2–5 bullet)
    
-  Policy statement (ย้ำ Part 9.8: ไม่มี GR/Λ claims)
    

**Go/No-Go**

- No-Go ถ้า release notes มีคำต้องห้าม/claim เกิน policy
    

---

## F) Tag & Publish (จังหวะกดปล่อย) — MUST

-  สร้าง tag: `v0.9.0` (หรือที่ตกลง)
    
-  แนบ assets: gallery pack + evidence pack + code-only pack
    
-  Verify download & open:
    
    - gallery เปิดได้
        
    - demo page อย่างน้อย 2–3 ใบเปิดแล้วรูปขึ้น
        
-  ปักหมุด link: README → docs/gallery → quickstart
    

**Go/No-Go**

- No-Go ถ้าแนบไฟล์ผิดรุ่น / เปิด zip แล้วขาดไฟล์
    

---

## G) Post-release Verification (หลังปล่อย 30–60 นาที) — SHOULD

-  เครื่องสะอาด (fresh env) ติดตั้งตาม README ได้
    
-  รัน quickstart suite ได้จริง
    
-  Gallery บน GitHub Pages (ถ้ามี) แสดงผลถูก
    
-  เปิด issue “Post-release tracking” รวม bug/feedback
    

---

## H) Rollback Plan (กันสถานการณ์ฉุกเฉิน) — MUST

-  ถ้าพบ bug critical:
    
    - ทำ hotfix branch
        
    - แก้เฉพาะจุด
        
    - tag ใหม่ `v0.9.1`
        
-  ถ้า assets pack พัง:
    
    - re-upload pack ที่ถูกต้อง
        
    - แก้ release notes ระบุ checksum/version ของ pack
        
-  ถ้า policy/claim พลาด:
    
    - แก้ docs/release notes ทันที + เพิ่ม lint rule
        

---

## Plain-Language Interpretation

วันปล่อยจริงคือ “ทำให้ทุกอย่างนิ่ง” แล้วกดพิมพ์:

- ล็อก registry + ของที่โชว์
    
- สร้าง gallery แบบ strict
    
- ทำ zip ที่คนเปิดแล้วดูได้ทันที
    
- รันทดสอบสั้น ๆ กันพัง
    
- ปล่อยแบบไม่โม้ และมีแผน rollback
    

---

## Next Step

**Part 9.20 — “Quickstart v0.9 (5 นาที)”**  
จะทำหน้า quickstart ที่คนใหม่ทำตามแล้วได้เดโม 1 ใบทันที (matrix เล็ก + run + validate + plot + เปิด gallery) แบบไม่ต้องอ่านเอกสารยาวก่อน

พิมพ์ “ต่อ” อีกที กูจะเขียน Part 9.20 เป็น quickstart ที่พร้อมวางหน้า README ได้เลย.

----
