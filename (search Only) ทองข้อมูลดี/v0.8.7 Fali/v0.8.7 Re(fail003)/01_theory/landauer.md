# Landauer Theory

## E = k_B T ln(2)

---

## พื้นฐาน

Landauer's principle (1961) กล่าวว่า:

> **การลบข้อมูล 1 bit ต้องใช้พลังงานอย่างน้อย k_B T ln(2)**

---

## สมการ

```
E_bit = k_B × T × ln(2)
```

### ที่ 300K (อุณหภูมิห้อง):
```
E_bit = 1.38×10⁻²³ × 300 × 0.693
      = 2.87×10⁻²¹ J
```

---

## ความหมายทางฟิสิกส์

1. **ข้อมูลคือ physical quantity** — ไม่ใช่ abstract
2. **ลบข้อมูล = ปล่อยความร้อน** — thermodynamic cost
3. **Information ↔ Energy** — แปลงกันได้

---

## เชื่อมกับ Maxwell's Demon

Landauer แก้ปัญหา Maxwell's Demon:
- Demon ต้อง "จำ" ว่า molecule ไปทางไหน
- จำ = เก็บข้อมูล
- ลบข้อมูล = ใช้พลังงาน ≥ kT ln 2
- → 2nd Law ไม่ถูกละเมิด

---

## Implementation

```python
from uet_landauer import energy_per_bit

# Energy to erase 1 bit at 300K
E = energy_per_bit(300)
print(f"E = {E:.2e} J")  # 2.87e-21 J

# Energy for 1 trillion bits
E_tera = energy_per_bit(300) * 1e12
print(f"E = {E_tera:.2e} J")  # 2.87e-09 J
```

---

*Landauer Theory - Part 3*
