# UET Core Equations
> Mathematical Specification v1.0

---

## 1. Energy Functional (Core Equation)

### 1.1 Single Field Model

For a scalar field $C(\mathbf{x}, t)$ on domain $\Omega$:

$$\Omega[C] = \int \left[ V(C) + \frac{\kappa}{2}|\nabla C|^2 \right] d\mathbf{x}$$

### 1.2 Coupled Field Model (C-I Model)

For two coupled fields $C$ and $I$:

$$\boxed{\Omega[C,I] = \int \left[ V_C(C) + V_I(I) - \beta C \cdot I + \frac{\kappa_C}{2}|\nabla C|^2 + \frac{\kappa_I}{2}|\nabla I|^2 \right] d\mathbf{x}}$$

---

## 2. Potential Function

### 2.1 Quartic (Double-Well) Potential

$$V(u) = \frac{a}{2}u^2 + \frac{\delta}{4}u^4 - su$$

**Parameters:**

| Parameter | Symbol | Meaning | Range |
|-----------|--------|---------|-------|
| Quadratic | $a$ | Curvature at origin | $a < 0$ for double-well |
| Quartic | $\delta$ | Boundedness | $\delta > 0$ required |
| Tilt | $s$ | External bias | Any |

**Critical Points:** For $s = 0$, minima at $u^* = \pm\sqrt{-a/\delta}$

---

## 3. Dynamics (Gradient Flow)

### 3.1 Evolution Equations

$$\frac{\partial C}{\partial t} = -M_C \frac{\delta\Omega}{\delta C}$$

$$\frac{\partial I}{\partial t} = -M_I \frac{\delta\Omega}{\delta I}$$

### 3.2 Chemical Potentials

$$\mu_C = V'_C(C) - \beta I - \kappa_C \nabla^2 C$$

$$\mu_I = V'_I(I) - \beta C - \kappa_I \nabla^2 I$$

---

## 4. Mathematical Properties

### 4.1 Energy Dissipation (Lyapunov)

**Theorem:** Along gradient flow solutions:

$$\frac{d\Omega}{dt} = -\int \left[ M_C |\mu_C|^2 + M_I |\mu_I|^2 \right] d\mathbf{x} \leq 0$$

**Implication:** Energy always decreases. Ω is a Lyapunov functional.

### 4.2 Stationary Points

At equilibrium: $\mu_C = \mu_I = 0$

---

## 5. Simplified Form

For quick reference:

$$\boxed{\Omega = \Omega_{pot} + \Omega_{coup} + \Omega_{grad}}$$

Where:
- $\Omega_{pot}$ = Potential energy (bulk)
- $\Omega_{coup}$ = Coupling energy ($-\beta CI$)
- $\Omega_{grad}$ = Gradient energy (surface)

---

## 6. Relation to Standard Physics

| UET Term | Physics Analog |
|----------|----------------|
| $\Omega$ | Free energy / Hamiltonian |
| $\partial_t C = -M\mu$ | Gradient descent / Relaxation |
| $\kappa|\nabla C|^2$ | Surface tension / Elastic energy |
| $V(C)$ | Landau potential |

---

*This is Landau-Ginzburg field theory with coupled order parameters.*

*Version: 1.0 | Date: 2025-12-28*
