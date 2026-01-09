# 📋 Restructure Plan — Step-by-Step Migration

> **วันที่**: 2026-01-04
> **หลักการ**: ไม่ลบ แค่จัดระเบียบทีละส่วน

---

## 🎯 เป้าหมาย

ทำให้ `data/`, `lab/`, `theory/` มีโครงสร้างเหมือนกัน:

```
XX_category/
├── __init__.py      ← Python package
├── README.md        ← Documentation  
└── {files}          ← Actual content
```

---

## 📊 หมายเลขมาตรฐาน (Final)

| # | Category | New Name | Old Names |
|:-:|:---------|:---------|:----------|
| 00 | Foundation | `00_foundation` | `00_thermodynamic_bridge` |
| 01 | Particle | `01_particle` | `01_particle_physics` |
| 02 | Astro | `02_astro` | `02_astrophysics` |
| 03 | Condensed | `03_condensed` | `03_condensed_matter`, `03_universal` |
| 04 | Quantum | `04_quantum` | `04_quantum` ✓ |
| 05 | Unity | `05_unity` | `05_unity_theory` |
| 06 | Complex | `06_complex` | `06_complex_systems` |
| 07 | Motion | `07_motion` | `06_motion_dynamics` (เลขซ้ำ!) |
| 08 | Utilities | `08_utilities` | `07_utilities` |
| 09 | Cosmo | `09_cosmo` | `cosmo` (orphan) |
| 10 | Fluid | `10_fluid` | `fluid_dynamics` (orphan) |
| 98 | References | `98_references` | `references` (orphan) |
| 99 | Archive | `_archive` | `_archive`, `_legacy`, etc. |

---

## 🔧 ขั้นตอนดำเนินการ

### Phase 1: ✅ เตรียมโครงสร้าง (ไม่ย้ายไฟล์)

- [x] สร้าง NAMING_CONVENTION.md
- [x] สร้าง README.md ในทุกโฟลเดอร์
- [x] วิเคราะห์ปัญหาครบถ้วน

### Phase 2: 🔄 สร้าง Compatibility Layer

สร้างไฟล์ `__init__.py` ที่ทำ import redirect:

```python
# data/01_particle/__init__.py
# This provides backward compatibility
from research_uet.data.old_01_particle_physics import *
```

### Phase 3: 🔄 Rename Incrementally

1. `06_motion_dynamics` → `07_motion` (แก้เลขซ้ำ)
2. `07_utilities` → `08_utilities`
3. Rename orphans: `cosmo` → `09_cosmo`

### Phase 4: 🧹 Consolidate Archives

รวมทุก archive folders → `_archive/`

---

## ⚠️ สิ่งที่ต้องระวัง

1. **Import paths** — ต้องอัพเดทถ้าเปลี่ยนชื่อ
2. **Relative imports** — อาจพัง
3. **Scripts hardcoded paths** — ต้อง grep หา

---

## 🚀 คำสั่งสำหรับ Clean __pycache__

```powershell
# ลบ __pycache__ ทั้งหมด (regenerated เมื่อ run)
Get-ChildItem -Path "research_uet" -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

---

*Plan v1.0 — Incremental Migration*
