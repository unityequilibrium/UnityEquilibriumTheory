# ⚖️ UET Core Axioms (4 Only) + Hypothesis

Reduced from 18 axioms to **4 essential axioms** + **1 testable hypothesis**.

---

## Axiom 1: Information is Physical
> **Every physical system contains and processes information.**
> **Information has a minimum energy cost (Landauer's Principle).**

**Testable:** Yes. Measure energy dissipation during computation.
**Falsifiable:** If information processing has zero energy cost, axiom fails.
**Source:** Landauer (1961), Bennett (2003).

**Math:**
$$ E_{bit} = k_B T \ln(2) $$

---

## Axiom 2: Boundaries Define Systems
> **A system is defined by its boundary.**
> **Information flows across boundaries at rate $C$.**

**Testable:** Yes. Define boundary, measure $C$.
**Falsifiable:** If boundaries cannot be defined, axiom fails.

**Math:**
$$ C = \frac{d(\text{bits crossing boundary})}{dt} $$

---

## Axiom 3: Flow Seeks Equilibrium
> **Information flow adjusts to minimize gradients.**
> **Equilibrium occurs when $C_{in} = C_{out}$.**

**Testable:** Yes. Perturb system, measure relaxation.
**Falsifiable:** If systems don't relax, axiom fails.

**Math:**
$$ \frac{dV}{dt} = C_{in} - C_{out} $$

---

## Axiom 4: Oscillation Indicates Dynamics
> **Systems oscillate around equilibrium.**
> **The frequency $\Omega$ indicates system responsiveness.**

**Testable:** Yes. Measure $\Omega$ via FFT.
**Falsifiable:** If systems don't oscillate, axiom fails.

**Math:**
$$ \Omega = 2\pi \sqrt{\frac{k_{eff}}{m_{eff}}} $$

---

# ⚠️ HYPOTHESIS (Not Axiom)

## Hypothesis H1: Value-Flow Coupling

> **The value (stored information) of a system depends on its flow rate.**

**This is NOT an axiom because:**
- It requires empirical verification
- The exact functional form is unknown
- The exponent $\alpha$ must be derived or measured

**Proposed Form:**
$$ V = V_{ref} \cdot \left( \frac{C}{C_{ref}} \right)^\alpha $$

**Status:** ⚠️ **UNPROVEN**
- $\alpha$ is currently empirical
- Must be derived from first principles or measured systematically

---

## Summary

| # | Type | Name | Status |
|:--|:-----|:-----|:-------|
| 1 | Axiom | Information is Physical | ✅ Established (Landauer) |
| 2 | Axiom | Boundaries Define Systems | ✅ Definition |
| 3 | Axiom | Flow Seeks Equilibrium | ✅ Conservation |
| 4 | Axiom | Oscillation Indicates Dynamics | ✅ Observable |
| H1 | **Hypothesis** | Value-Flow Coupling | ⚠️ **To be tested** |

---

*4 axioms (all established) + 1 hypothesis (to be tested).*
*Honest science requires separating assumptions from claims.*
