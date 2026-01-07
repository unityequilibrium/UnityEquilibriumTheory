# Thermodynamics in UET

## กฎเทอร์โมไดนามิกส์ 0-1-2-3

---

## กฎข้อ 0: สมดุลพลังงาน

> สมดุลพลังงานจะเกิดขึ้นได้ ถ้ามีการเปลี่ยนแปลง/พฤติกรรมในระบบ

**Implementation:**
```python
from uet_landauer import law_0_equilibrium
```

---

## กฎข้อ 1: พลังงานไม่สูญหาย

> พลังงานไม่หาย แต่เปลี่ยนรูป → เป็น "ข้อมูลของพฤติกรรม"

**สมการ:**
```
ΔE = k_B T ln(2) × ΔI
```

**Implementation:**
```python
from uet_landauer import law_1_conservation
```

---

## กฎข้อ 2: Entropy เพิ่มขึ้นเสมอ

> พฤติกรรม = เสื่อมพลังงาน = เพิ่ม entropy = ทิ้งร่องรอย

**สมการ:**
```
dS/dt ≥ 0
```

**ความหมาย:**
- ทุกพฤติกรรมทิ้งร่องรอย
- ร่องรอย = ข้อมูลใน Space

**Implementation:**
```python
from uet_landauer import law_2_entropy_increase
```

---

## กฎข้อ 3: Space เป็นระเบียบสูงสุด

> Space จัดการความไร้ระเบียบ → พาระบบหาสมดุล

**ความหมาย:**
- Space คือ "ระบบบันทึก/จัดระเบียบ"
- ข้อมูลไม่ใช่มโน มันเกิดจากความจริง

---

## สรุป: Vision + Thermo

```
พฤติกรรม (Law 0)
    ↓
ใช้พลังงาน (Law 1)
    ↓
เพิ่ม entropy (Law 2)
    ↓
บันทึกใน Space (Law 3)
```

---

*Thermodynamics - Part 3*
