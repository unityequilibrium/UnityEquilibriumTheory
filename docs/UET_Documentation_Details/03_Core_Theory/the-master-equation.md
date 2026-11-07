---
title: "The Master Equation"
description: "Historical seven-term UET candidate template with current ontology and claim boundaries."
---

# The Master Equation

> **Current status:** this page preserves the historical seven-term candidate template. It is
> not a proven single source of truth and it does not give `C` a universal physical identity.
> For current ontology and mapping rules, read [C as a Relational Interaction Variable](./relational-C-and-physical-mapping.md).

**The Master Equation** is the historical UET functional template used to organize candidate relations across different systems. It is not, by itself, a completed equation that explains every scale or a replacement for the established equations of each domain.

เป้าหมายของหน้านี้คือการบันทึกโครงสร้างแบบจำลองและคำถามวิจัยเรื่องความสัมพันธ์ ต้นทุนของการเปลี่ยนแปลง และเงื่อนไขการคงอยู่ ไม่ใช่การประกาศทฤษฎีสากลที่พิสูจน์แล้ว

---

## แบบจำลองผู้สมัคร 7 เทอมในประวัติการพัฒนา

สถานะการตรวจของแต่ละ lane อยู่ใน [Foundation Status Aggregate](../../core/01_contracts/UET_FOUNDATION_STATUS_AGGREGATE.md).

สมการนี้เขียนอยู่ในรูปของ Functional (ฟังก์ชันนัล) $\Omega$ ที่ขึ้นอยู่กับตัวแปรหลัก 3 ตัว คือ $C$ (relational interaction coordinate), $I$ (lane-declared second-sector variable), และ $J$ (exchange/flux when dimensionally defined)

$$
\Omega[C,I,J] = \int d^3x \left[ V(C) + \frac{\kappa}{2}|\nabla C|^2 + \beta C \cdot I + \gamma_J (J_{in} - J_{out}) \cdot C + W_N |\nabla \Omega| + \beta_U V_{game} + \lambda \sum (C_i - C_j)^2 \right]
$$

---

## 📊 อธิบายความหมายทีละเทอม (Term-by-Term Breakdown)

สมการนี้ประกอบด้วย 7 เทอม (Terms) ซึ่งแต่ละเทอมเป็นตัวแทนของแนวคิดพื้นฐานทางฟิสิกส์และระบบ:

### 1. The Potential Term: $V(C)$
- **ความหมาย:** ต้นทุนหรือค่าความชอบของโครงสร้างปฏิสัมพันธ์ที่เบี่ยงจากสภาวะอ้างอิง (ยังไม่ใช่พลังงานกายภาพโดยอัตโนมัติ)
- **อธิบาย:** เป็นตัวกำหนด cost landscape ของ relational state คล้ายโครงสร้าง potential ในแบบจำลองพลังงาน แต่ยังไม่ใช่ physical energy หากยังไม่มี unit/ledger mapping

### 2. The Gradient Term: $\frac{\kappa}{2}|\nabla C|^2$
- **ความหมาย:** การลงโทษความแปรผันเชิงพื้นที่ของตัวแปรปฏิสัมพันธ์ (ไม่ใช่พลังงานจลน์หรือความหนืดโดยอัตโนมัติ)
- **อธิบาย:** เทอมนี้ลงโทษความไม่สม่ำเสมอของ relational state; การเรียกมันว่าแรงต้าน ความหนืด หรือ kinetic cost ต้องมี constitutive mapping แยกต่างหาก

### 3. The Coupling Term: $\beta C \cdot I$
- **ความหมาย:** เทอม coupling ระหว่างภาคส่วน `C` และ `I` ที่ประกาศความหมายแยกกัน (ไม่ใช่กฎการแปลง C เป็น I)
- **อธิบาย:** เทอมนี้ระบุเพียงการ coupling ใน functional การประมวลผลหรือการเปลี่ยนแปลงอาจต้องทำ energy bookkeeping ตาม lane แต่สมการนี้ยังไม่พิสูจน์ว่า `I` เป็นสสารหรือว่า `C` แปลงเป็น `I`

### 4. The Exchange Term: $\gamma_J (J_{in} - J_{out}) \cdot C$
- **ความหมาย:** ช่องทางแลกเปลี่ยนของระบบเปิด/กึ่งเปิด เมื่อ `J` ถูกนิยามเป็น flux พร้อมหน่วยและ boundary law
- **อธิบาย:** เมื่อระบบถูกศึกษาเป็น open/effective subsystem เทอมนี้บันทึก inflow และ outflow ของสิ่งที่ `J` นิยามไว้; มันไม่ใช่ proof ว่าทุกระบบต้องใช้ boundary law เดียวกัน

### 5. The Natural Will Term: $W_N |\nabla \Omega|$
- **ความหมาย:** เทอมเชิงแนวคิดเรื่อง persistence หรือแรงกดดันให้คงอยู่; ยังต้องมี derivation และ observable mapping
- **อธิบาย:** ภาษาประวัติศาสตร์ใช้เทอมนี้แทน persistence pressure; การ derive เป็น action หรือ survival law ยังเปิดอยู่

### 6. The Game Term: $\beta_U V_{game}$
- **ความหมาย:** การแข่งขันและความร่วมมือ (Dynamic Game / Nash Equilibrium)
- **อธิบาย:** ใน lane แบบหลายตัวแสดง เทอมนี้อาจแทน competition, coordination, หรือ cooperation เมื่อมี game/agent model รองรับ

### 7. The Coherence Term: $\lambda \sum (C_i - C_j)^2$
- **ความหมาย:** การซิงค์กันข้ามมิติ (Multi-layer Sync / Coherence)
- **อธิบาย:** เทอมนี้ลงโทษ mismatch ระหว่าง subsystem ที่ประกาศไว้; ผลต่อความกลมกลืนต้องตรวจจาก dynamics ของ lane นั้น ไม่ใช่ข้อสรุปสากล

---

## 🔑 ตัวแปรหลัก (Parameter Definitions)

| สัญลักษณ์ | ชื่อเรียก | ความหมายโดยย่อ |
|:------:|:-----|:----------------|
| **C** | Relational interaction coordinate | ตัวแปรนามธรรมสำหรับโครงสร้างปฏิสัมพันธ์/พฤติกรรม; physical realization ต้องประกาศเป็นราย lane |
| **I** | Lane-declared second-sector variable | อาจเป็น information, entropy, field, หรือ comparator ตาม lane; ห้ามเหมารวม |
| **J** | Flux / Flow | อัตราการแลกเปลี่ยนเข้า-ออกเมื่อมีนิยามเชิงมิติและ boundary law |
| **κ** (Kappa) | Gradient coefficient | coefficient ของ `|grad C|^2`; หน่วยต้องปิดตาม lane |
| **β** (Beta) | Coupling coefficient | coefficient ของ `C I`; ไม่ใช่กฎแปลงข้อมูลเป็นพลังงานโดยอัตโนมัติ |
| **λ** (Lambda) | Layer coherence | แรงยึดเหนี่ยวที่ทำให้ระบบไม่แตกสลาย |

การทำความเข้าใจสมการนี้คือการเข้าใจโครงสร้างของแบบจำลองเชิงระบบและคำถามวิจัยของ UET ไม่ใช่การพิสูจน์กลไกของทุกสรรพสิ่งโดยอัตโนมัติ
