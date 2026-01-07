# How Established Physics Connects
## Newton ↔ Einstein ↔ Thermodynamics

**Created:** 2025-12-30

---

## 🎯 Goal

ดูว่า physics ที่พิสูจน์แล้ว เชื่อมกันยังไง ก่อนจะเอา UET มาต่อ

---

## 📐 1. Newton ↔ Einstein

### Connection: Low-velocity limit

```
Einstein (Special Relativity):
E = γmc²  where γ = 1/√(1 - v²/c²)

When v << c:
γ ≈ 1 + ½(v/c)² + ...

E ≈ mc² + ½mv²
    ↑      ↑
  rest   kinetic (Newton!)
  energy
```

### Key Equations:

| Einstein | → | Newton (v << c) |
|----------|---|-----------------|
| E = γmc² | → | E ≈ mc² + ½mv² |
| p = γmv | → | p ≈ mv |
| F = dp/dt | → | F = ma |

### Diagram:

```
EINSTEIN (c = finite)
       │
       │ v << c
       ▼
NEWTON (c → ∞)
```

---

## 📐 2. Newton ↔ Thermodynamics

### Connection: Statistical mechanics

```
Newton: Single particle
F = ma

Many particles → Statistical average:
<E> = Σ ½mv² → ³⁄₂ kT per particle (equipartition)
```

### Key Equations:

| Newton (micro) | → | Thermo (macro) |
|----------------|---|----------------|
| E = ½mv² | → | <E> = ³⁄₂ kT |
| F = ma | → | P = NkT/V (ideal gas) |
| Work = ∫F·dx | → | W = ∫PdV |

### Diagram:

```
NEWTON (1 particle)
       │
       │ N → ∞ (many particles)
       ▼
THERMODYNAMICS (macro)
```

---

## 📐 3. Einstein ↔ Thermodynamics

### Connection: Relativistic thermodynamics

```
Einstein tells us: E = mc²

This means: mass IS energy

Thermodynamics says: energy is conserved

Together: mass-energy is conserved!
```

### Key Equations:

| Einstein | + | Thermo |
|----------|---|--------|
| E = mc² | + | dS/dt ≥ 0 |
| = | | |
| Relativistic thermodynamics | | |

### Black Hole Connection (Bekenstein-Hawking):

```
S_BH = (kc³/4Għ) × A

Combines:
- c (Einstein)
- k (Thermo)
- G (Newton)
- ħ (Quantum)
```

---

## 📐 4. All Three Together: Energy is Central

### Diagram:

```
                    ENERGY
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
    NEWTON        EINSTEIN       THERMO
    
   E = ½mv²       E = mc²       E = TS - PV
   (kinetic)      (rest)        (internal)
```

### The Common Thread:

> **ENERGY เป็นตัวเชื่อม!**
>
> - Newton: Energy จาก motion
> - Einstein: Energy จาก mass
> - Thermo: Energy distribution

---

## 📐 5. Summary: Known Connections

```
                EINSTEIN
                   │
                   │ v << c
                   ▼
    ┌──────────NEWTON───────────┐
    │              │            │
    │ macro avg    │  micro     │
    ▼              ▼            ▼
THERMO         Statistical    Landauer
dS ≥ 0         Mechanics      E = kT ln(2)
                                   │
                                   │ Info ↔ Energy
                                   ▼
                              INFORMATION
```

### Key Limits:

| From | To | Condition |
|------|-----|-----------|
| Einstein | Newton | v << c |
| Newton | Thermo | N → ∞ (many particles) |
| Thermo | Landauer | Info processing |

---

## 🔑 Core Insight for UET

> **ถ้า UET จะ unify ได้ ต้องเข้าใจว่า:**
>
> 1. Newton ↔ Einstein เชื่อมผ่าน **velocity limit**
> 2. Newton ↔ Thermo เชื่อมผ่าน **particle statistics**  
> 3. Thermo ↔ Info เชื่อมผ่าน **Landauer principle**
>
> **UET อยู่ตรงไหน?**

---

## 📊 Visual Summary:

```
                    ┌─────────────────────┐
                    │      EINSTEIN       │
                    │      E = mc²        │
                    └─────────┬───────────┘
                              │ v << c
                    ┌─────────▼───────────┐
                    │       NEWTON        │
                    │      E = ½mv²       │
                    └─────────┬───────────┘
                              │ N → ∞
              ┌───────────────┴───────────────┐
              │                               │
    ┌─────────▼─────────┐         ┌───────────▼──────────┐
    │   THERMODYNAMICS  │         │    STAT MECHANICS    │
    │     dS ≥ 0        │         │     <E> = kT         │
    └─────────┬─────────┘         └──────────────────────┘
              │ info
    ┌─────────▼─────────┐
    │     LANDAUER      │
    │   E = kT ln(2)    │
    └───────────────────┘
              │
              ▼
            UET?
```

---

*Established Physics Connections - 2025-12-30*
