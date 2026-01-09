# UET Usage Patterns Guide

## วิธีใช้ UET กับสถานการณ์ต่างๆ

---

## 1. Overview: 3 Patterns หลัก

```
Pattern A: Single System, Multiple N
  → ระบบเดียว มีหลายตัวแปร
  → ตัวอย่าง: สังคมที่มีหลายคน

Pattern B: Single N, Multiple Systems  
  → ตัวแปรเดียว อยู่ในหลายระบบ
  → ตัวอย่าง: คนหนึ่งคนในหลายบทบาท

Pattern C: Competition (Game Theory)
  → หลาย N, หลาย System, หลาย Strategy
  → ตัวอย่าง: ใครจะ normalize ได้มากที่สุด?
```

---

## 2. Pattern A: Single System, Multiple N

### 2.1 โครงสร้าง

```
┌────────────────────────────────────────┐
│              SYSTEM                    │
│                                        │
│   N₁    N₂    N₃    ...    Nₘ         │
│    ↓     ↓     ↓           ↓          │
│   ┌─────────────────────────┐          │
│   │     Interactions (β)    │          │
│   └─────────────────────────┘          │
│                ↓                       │
│              Ω_system                  │
└────────────────────────────────────────┘
```

### 2.2 สูตร

```
Ω_system = Σ Ω(Nᵢ) + Σ β_ij × interaction(Nᵢ, Nⱼ)

Where:
  Ω(Nᵢ) = พลังงานของตัวแปร i
  β_ij = coupling ระหว่าง i กับ j
```

### 2.3 คำถามที่ใช้

```
1. N แต่ละตัวมี Ω เท่าไหร่?
2. N ตัวไหนสร้างปัญหา (Ω สูง)?
3. Coupling ระหว่าง N แต่ละคู่เป็นยังไง?
4. ลด Ω_system ได้ยังไง?
```

### 2.4 ตัวอย่าง: สังคม

```
System = สังคม
N = คนแต่ละคน

Ω(คน A) = ความเครียด/ความขัดแย้งภายใน
β_AB = ความสัมพันธ์ระหว่าง A กับ B

Ω_สังคม = Σ Ω(คน) + Σ β × ความขัดแย้งระหว่างคน
```

---

## 3. Pattern B: Single N, Multiple Systems

### 3.1 โครงสร้าง

```
     System 1          System 2          System 3
  ┌────────────┐    ┌────────────┐    ┌────────────┐
  │            │    │            │    │            │
  │     N      │    │     N      │    │     N      │
  │   (role 1) │    │   (role 2) │    │   (role 3) │
  │            │    │            │    │            │
  └────────────┘    └────────────┘    └────────────┘
        ↓                 ↓                 ↓
      Ω₁(N)            Ω₂(N)             Ω₃(N)
        └────────────────┬────────────────┘
                         ↓
                    Ω_total(N)
```

### 3.2 สูตร

```
Ω_total(N) = Σ wᵢ × Ωᵢ(N) + conflict_cost

Where:
  Ωᵢ(N) = Ω ของ N ในระบบ i
  wᵢ = weight/ความสำคัญของระบบ i
  conflict_cost = ต้นทุนจากการอยู่หลายระบบพร้อมกัน
```

### 3.3 คำถามที่ใช้

```
1. N อยู่ในกี่ระบบ?
2. ระบบไหนเรียกร้อง Ω มากที่สุด?
3. ขัดแย้งระหว่างระบบไหม?
4. จะ balance ได้ยังไง?
```

### 3.4 ตัวอย่าง: คนหนึ่งคน หลายบทบาท

```
N = คุณ

System 1 = ครอบครัว (ลูก/พ่อ/แม่)
System 2 = ที่ทำงาน (พนักงาน)
System 3 = สังคม (พลเมือง)
System 4 = ตัวเอง (ความต้องการส่วนตัว)

Ω_total = wครอบครัว × Ωครอบครัว + wงาน × Ωงาน + ...

Conflict: ถ้างานเรียกร้องเวลา ≠ ครอบครัวเรียกร้องเวลา
```

---

## 4. Pattern C: Competition (Game Theory)

### 4.1 โครงสร้าง

```
┌─────────────────────────────────────────────────┐
│                  ARENA                          │
│                                                 │
│   N₁ (Strategy A)     N₂ (Strategy B)          │
│        ↓                    ↓                   │
│   ┌─────────┐          ┌─────────┐              │
│   │ Formal₁ │← compete →│ Formal₂ │             │
│   └────┬────┘          └────┬────┘              │
│        ↓                    ↓                   │
│   Normalize?            Normalize?              │
│        ↓                    ↓                   │
│   ┌─────────┐          ┌─────────┐              │
│   │ New F₁  │          │ New F₂  │              │
│   └─────────┘          └─────────┘              │
│        └────────────┬───────────┘               │
│                     ↓                           │
│              ใครชนะ?                            │
│        (ใคร normalize ได้มากกว่า)               │
└─────────────────────────────────────────────────┘
```

### 4.2 กฎ

```
Rule 1: ทุก N มี Formal state ของตัวเอง
Rule 2: ทุก N พยายาม Normalize
Rule 3: ใคร Normalize ได้มากที่สุด = ชนะ
Rule 4: Formal ใหม่ = Formal เก่า + Normalization

Winner = N ที่มี Δ(Formalization) สูงสุด
       = N ที่ normalize ได้มากที่สุด
```

### 4.3 4 Strategies (จาก Power Dynamics)

```
        มิติ 1: ศักยภาพ
        ┌───────────────┬───────────────┐
        │   ธรรมดา      │  ไม่ธรรมดา    │
   ┌────┼───────────────┼───────────────┤
มิ │ปกติ│  A: Conserve  │  B: Maintain  │
ติ │    │  Low risk     │  Stable power │
2: ├────┼───────────────┼───────────────┤
การ│ไม่ │  C: Disrupt   │  D: Dominate  │
ตัด│ปกติ│  ★ Sacrifice  │  High risk    │
สิน└────┴───────────────┴───────────────┘
ใจ

Normalization potential:
  A: Low (no change, no normalize)
  B: Medium (has power but doesn't use)
  C: High ★ (no self-interest, can normalize others)
  D: Variable (can normalize or destroy)
```

### 4.4 ทำไม C ชนะ?

```
C = ธรรมดา + ไม่ปกติ

สามารถ normalize ได้มากที่สุดเพราะ:
1. ธรรมดา = ไม่มี Formal ตัวเองที่ต้องปกป้อง
2. ไม่ปกติ = กล้าเปลี่ยนแปลง

→ ไม่มีอะไรจะเสีย + กล้าทำ
→ Normalize potential สูงสุด
→ ชนะในระยะยาว!
```

---

## 5. Normalize Competition Cycle

### 5.1 The Infinite Loop

```
Formal₁ (initial state)
    ↓
[Normalize attempt]
    ↓
Formal₂ (new state)
    ↓
[Normalize attempt]
    ↓
Formal₃ ...
    ↓
    ∞ (never ends)
```

### 5.2 Competition Rules

```
Round N:
  - ทุก participant มี Formal state
  - แต่ละคนพยายาม Normalize
  - วัดผล: ใคร Normalize ได้มากกว่า?

ชนะ = ได้เป็น Formal ใหม่ของ round ถัดไป
แพ้ = ต้อง adapt ตาม Formal ของผู้ชนะ

แต่! Formal ใหม่ก็ต้องถูก Normalize อีก...
→ ไม่มีใครชนะถาวร
→ มีแต่ "ชนะ round นี้"
```

### 5.3 เหมือน Nature จริงๆ

```
ธรรมชาติ:
  Species A dominates → Environment changes
  Species B adapts better → B dominates
  Environment changes again → C emerges
  ...forever

UET:
  Formal A wins → Must normalize to stay
  Formal B normalizes better → B becomes new Formal
  B must normalize → C emerges
  ...forever

= Becoming, not Being
= Process, not State
= ไม่มีผู้ชนะถาวร
```

---

## 6. Decision Guide: เลือก Pattern ไหน?

```
คำถาม: "ฉันอยากวิเคราะห์อะไร?"

┌─────────────────────────────────────────────────┐
│ ถ้ามี 1 ระบบ + หลายตัวแปร:                      │
│   → Pattern A (Single System, Multiple N)       │
│   → ตัวอย่าง: สังคม, องค์กร, ecosystem         │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ ถ้ามี 1 ตัวแปร + หลายระบบ:                      │
│   → Pattern B (Single N, Multiple Systems)      │
│   → ตัวอย่าง: คนหนึ่งคน, บริษัทหนึ่ง, ประเทศ   │
└─────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────┐
│ ถ้าอยากรู้ว่า "ใครจะชนะ?" หรือ "อะไรจะเกิด?":   │
│   → Pattern C (Competition)                     │
│   → ตัวอย่าง: เลือกตั้ง, market, evolution     │
└─────────────────────────────────────────────────┘
```

---

## 7. Quick Reference Table

| Pattern | Input | Output | Use Case |
|---------|-------|--------|----------|
| A: Multi-N | 1 System, N variables | Ω_system | วิเคราะห์ระบบ |
| B: Multi-System | 1 Variable, M systems | Ω_total(N) | วิเคราะห์บทบาท |
| C: Competition | N players, 4 strategies | Winner | ทำนายผล |

---

## 8. สรุป

```
1. Pattern A: หลาย N ในระบบเดียว
   → Ω = Σ Ω(N) + interactions

2. Pattern B: หนึ่ง N ในหลายระบบ
   → Ω = Σ wᵢ × Ωᵢ(N) + conflicts

3. Pattern C: Competition (Game Theory)
   → ใคร Normalize ได้มากที่สุด = ชนะ
   → แต่ชนะไม่ถาวร (ต้อง normalize ต่อ)

4. Infinite Loop: Formal → Normalize → New Formal → ...
   → ไม่มี Being, มีแต่ Becoming
```

---

*"ผู้ชนะไม่ใช่คนที่ถึง Formal สุดท้าย แต่คือคนที่ Normalize ได้ดีที่สุดตอนนี้"*
