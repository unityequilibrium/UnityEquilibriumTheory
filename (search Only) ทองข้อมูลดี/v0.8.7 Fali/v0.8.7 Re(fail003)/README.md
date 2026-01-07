# UET Landauer Research (Part 3)

## โครงสร้างใหม่ที่เป็นระเบียบ

**สร้าง:** 2025-12-30
**Version:** Part 3 (Landauer Foundation)

---

## 📚 Folder Structure

```
research_v3/
├── 00_foundation/          ← ทฤษฎีพื้นฐาน
│   ├── core_equations.md   ← 3 สมการหลัก
│   ├── physics_support.md  ← 6 หลักการที่สนับสนุน
│   └── vision.md           ← Original vision
│
├── 01_theory/              ← ทฤษฎีเต็ม
│   ├── landauer.md         ← E = kT ln 2
│   ├── thermodynamics.md   ← Laws 0-3
│   └── space_recorder.md   ← Space บันทึกข้อมูล
│
├── 02_implementation/      ← Code & Tests
│   ├── code_guide.md       ← How to use uet_landauer/
│   └── test_results.md     ← Test outputs
│
├── 03_validation/          ← การพิสูจน์
│   ├── physics_tests.md    ← เทียบกับ physics
│   └── predictions.md      ← What theory predicts
│
├── 04_papers/              ← Papers & Publications
│   ├── draft_v1.md         ← Main paper draft
│   └── figures/            ← Images for paper
│
├── 05_archive/             ← Link to old data
│   └── legacy_data.md      ← References to old folders
│
└── README.md               ← This file
```

---

## 🎯 Core Equations (Quick Reference)

### 1. Landauer Principle
```
E_bit = k_B × T × ln(2)
```

### 2. Value Function
```
V = M × (C/I)^α
```

### 3. Energy-Information Bridge
```
dE/dt = k_B T ln(2) × dI/dt
```

---

## 📦 Old Data Reference

ข้อมูลเก่าอยู่ที่:
- `research/00_core_paper/` → Part 2 archive
- `research/ปรับ/` → Legacy merged docs
- `research/01-core/` → Old core (CH-based)

**ไม่ใช้โดยตรง — ดึงข้อมูลที่ต้องการมาเท่านั้น**

---

## 🚀 Quick Start

```python
from uet_landauer import (
    energy_per_bit,
    value_function,
    FullSimulator
)

# Energy per bit at 300K
E = energy_per_bit(300)  # ~2.87e-21 J

# Value from C/I ratio
V = value_function(C=2, I=1)  # 2.0

# Run simulation
sim = FullSimulator()
sim.run()
sim.plot()
```

---

*Part 3 Research Structure - Clean and Organized*
