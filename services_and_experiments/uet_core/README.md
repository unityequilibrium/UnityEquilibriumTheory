# ⚛️ UET Core Engine (`uet_core`)

![Status](https://img.shields.io/badge/Status-ACTIVE-brightgreen)
![Language](https://img.shields.io/badge/Language-Rust-orange)
![Performance](https://img.shields.io/badge/Performance-High_Precision-blue)

> **"The Physics Engine of UET"** - คำนวณสมการแม่บท (Master Equation) ด้วยความเร็วและตรรกะที่ถูกต้องแม่นยำที่สุด (High-Performance Computing).

---

## 🏛️ Architecture Pillars

| Component | Description |
| :--- | :--- |
| **Dynamics** | คำนวณค่า $\Omega$ (Omega), $\kappa$ (Kappa), $\beta$ (Beta) ตามทฤษฎี. |
| **Fields** | จัดการโครงสร้าง Tensor Field (C, I) สำหรับการคำนวณ. |
| **Safety** | ใช้ระบบ Type System ของ Rust ป้องกัน Logical Error 100%. |

---

## 🔗 Theory Connection

```mermaid
graph LR
    Input[("Raw Input (C, I)")] --> Engine{"🦀 uet_core"}
    Engine -->|Compute| Omega["Ω (Optimization)"]
    Engine -->|Compute| Kappa["κ (Boundary)"]
    Engine -->|Compute| Beta["β (Coupling)"]

    style Engine fill:#ffab91,stroke:#e64a19
```

---

## 🚀 Key Functions

- **`compute_omega(c, i)`**: หัวใจหลักของการหาค่าความสมดุล (Balance).
- **`Field::new(data)`**: สร้างสนามพลังงานสำหรับการทดสอบ.

---

## 🛠️ Usage

ใช้เป็น Library สำหรับ `uet_kb` หรือ Python Binding:

```rust
use uet_core::dynamics;
let omega = dynamics::compute_omega(&config, &field_c, &field_i);
```
