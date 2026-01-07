# 📐 00-foundation Index

> พื้นฐานทางทฤษฎีสำหรับ Unity Equilibrium Theory

---

## Structure

```
00-foundation/
├── 01-thermodynamics/     ← กฎเทอร์โมไดนามิกส์ 0-1-2-3
├── 02-free-energy/        ← แนวคิด Free Energy
├── 03-gradient-flow/      ← คณิตศาสตร์ Gradient Flow
└── 04-cahn-hilliard/      ← สมการ Cahn-Hilliard / Landau-Ginzburg
```

---

## Progress

| Section | Status | Priority |
|---------|--------|----------|
| [01-thermodynamics](./01-thermodynamics/) | 🔄 In Progress | 🔴 High |
| [02-free-energy](./02-free-energy/) | ⬜ TODO | 🔴 High |
| [03-gradient-flow](./03-gradient-flow/) | ⬜ TODO | 🔴 High |
| [04-cahn-hilliard](./04-cahn-hilliard/) | ⬜ TODO | 🟡 Medium |

---

## Why Foundation First?

```
┌─────────────────────────────────────────────────────────────────┐
│  ❌ WRONG: Jump straight to applications                        │
│     01-gravity → 02-em-force → ... (ไม่มีฐาน!)                  │
│                                                                 │
│  ✅ CORRECT: Build foundation first                             │
│     Thermo → Free Energy → Gradient Flow → UET → Applications  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Equations to Derive

| Equation | From | To |
|----------|------|-----|
| `dF ≤ 0` | 2nd Law | UET basis |
| `∂u/∂t = -∇Ω` | Gradient flow | UET dynamics |
| `Ω = ∫[V + κ|∇u|²]dx` | Landau-Ginzburg | UET energy |
| `dΩ/dt ≤ 0` | All above | UET guarantee |

---

*Version: 0.9*
*Date: 2025-12-29*
