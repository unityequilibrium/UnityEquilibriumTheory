# UET Interpretation
> What do C, I, and Ω mean?

---

## 1. Overview

UET uses a **coupled field model** with two order parameters: **C** and **I**.

This is mathematically equivalent to Landau-Ginzburg theory, but with a specific interpretation.

---

## 2. The Fields

### 2.1 C (Communication / Openness)

| Aspect | Description |
|--------|-------------|
| **Symbol** | $C(\mathbf{x}, t)$ |
| **Meaning** | Degree of openness/communication at point x |
| **High C** | System is open, exchanging with environment |
| **Low C** | System is closed/isolated |

**Physical analogy:** Permeability, conductivity, coupling strength

### 2.2 I (Isolation / Closure)

| Aspect | Description |
|--------|-------------|
| **Symbol** | $I(\mathbf{x}, t)$ |
| **Meaning** | Degree of isolation/closure at point x |
| **High I** | System is isolated, self-contained |
| **Low I** | System is open |

**Physical analogy:** Resistance, friction, internal barriers

### 2.3 Relationship

$$C \uparrow \iff I \downarrow$$

C and I are **complementary** (but not necessarily C + I = const).

---

## 3. The Energy Functional Ω

### 3.1 Definition

$$\Omega[C,I] = \text{Total "stress" or "disequilibrium" of the system}$$

### 3.2 Interpretation

| Property | Meaning |
|----------|---------|
| **Ω high** | System far from equilibrium |
| **Ω low** | System near equilibrium |
| **Ω decreasing** | System improving/ordering |
| **Ω = 0** | Ideal state (may not exist) |

### 3.3 Components

| Component | Formula | Meaning |
|-----------|---------|---------|
| $\Omega_{pot}$ | $\int [V(C) + V(I)]$ | Local tendency toward minima |
| $\Omega_{coup}$ | $-\beta \int CI$ | Benefit of C-I alignment |
| $\Omega_{grad}$ | $\frac{\kappa}{2}\int |\nabla|^2$ | Cost of spatial variation |

---

## 4. The Value 𝒱

### 4.1 Definition

$$\mathcal{V} = -\frac{d\Omega}{dt} = \text{Rate of ordering}$$

### 4.2 Interpretation

| Property | Meaning |
|----------|---------|
| **𝒱 > 0** | System is improving |
| **𝒱 = 0** | System at equilibrium |
| **𝒱 < 0** | Impossible (Lyapunov) |

---

## 5. Coupling Term (-βCI)

### 5.1 What it means

$$-\beta C \cdot I$$

- **β > 0:** C and I "want" to be aligned (cooperative)
- **β < 0:** C and I "want" to be opposite (competitive)
- **β = 0:** C and I are independent

### 5.2 Physical interpretation

When β > 0:
- High C × High I → Lower energy (good)
- This seems contradictory! 

**Resolution:** In practice, the potential V(C) and V(I) usually push toward specific values, and the coupling modifies the equilibrium.

---

## 6. Units and Dimensions

### 6.1 Current status: UNDEFINED

⚠️ **C and I do not have specified physical units.**

They are dimensionless order parameters, normalized to [-1, 1] or similar.

### 6.2 Practical usage

| Context | C meaning | I meaning |
|---------|-----------|-----------|
| Thermodynamics | Exchange rate | Dissipation |
| Social systems | Communication | Barriers |
| Networks | Connectivity | Isolation |
| Economics | Trade | Transaction cost |

---

## 7. Key Insight

> **UET is NOT claiming new physics.**
>
> UET is a **mathematical framework** (Landau-Ginzburg) with a **particular naming convention** (C, I, Ω) that allows cross-domain analogies.

The value is in the **common language**, not new predictions.

---

*Version: 1.0 | Date: 2025-12-28*
