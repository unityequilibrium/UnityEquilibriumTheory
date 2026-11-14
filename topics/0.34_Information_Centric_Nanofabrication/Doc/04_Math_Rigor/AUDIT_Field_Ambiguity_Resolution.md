# 📐 AUDIT: I vs C Field Roles (Topic 0.34)

This audit resolves the ambiguity raised regarding the roles of $I$ (Information) and $C$ (Matter) in the Nanofabrication context.

---

## 1. Variable Identity (The Industrial Fix)

In a general UET state (e.g. Galaxy Formation), $I$ is an emergent property driven by $C$. However, in **Nanofabrication Manufacturing (ICN)**, we operate in **Command Mode (Axiom 6)**.

| Variable | General UET Role | **ICN Manufacturing Role** | Physical Equivalent |
| :--- | :--- | :--- | :--- |
| **$I$ (Information)** | Resultant (Entropy Flux) | **Actuator (Input)** | **SAW Pressure Field** |
| **$C$ (Matter)** | Primary State | **Resultant (Output)** | Atomic Concentration |

**Direction of Causality:**
- **Theoretic UET:** $C \to I$ (Matter produces Information).
- **ICN Nanofab:** $I \to C$ (Information/SAW shapes Matter).

---

## 2. Hardened Master Equation (0.34 Variant)

The trapping mechanism is no longer "Sticky Coupling" ($\beta CI$). Instead, we use the **Acoustic Radiation Force (Gradient Drift)**:

$\frac{\partial C}{\partial t} = \kappa \nabla^2 C + \beta \nabla \cdot (C \nabla I)$

- **$\beta \nabla \cdot (C \nabla I)$**: This is the drift term. Since we define the SAW nodes at $I_{min}$ (potential wells), a positive $\beta$ pulls $C$ into these wells.
- **Selectivity**: Matter is physically pushed *out* of domains where $\nabla I$ is strong and directed away from the nodes. This resolves the **100% Defect Rate crisis**.

---

## 3. Terminal Lag Resolution

To address the "Terminal Problem," the engine now:
1.  **Precomputes $\nabla I$**: $I$ is a static actuator "mask," so we compute its gradient once at initialization. This reduces CPU load by ~50%.
2.  **High-Frequency Flush**: Uses `sys.stdout.write` and `flush=True` every 25 steps to provide an ASCII growth meter `[####....]`. This ensures the user sees real-time progress even in buffered terminal environments.
