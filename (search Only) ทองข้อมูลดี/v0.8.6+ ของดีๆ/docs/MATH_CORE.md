# UET Mathematical Core Specification

**Version:** 0.9  
**Status:** Paper-ready  
**Last Updated:** 2024-12

---

## Abstract

This document provides a complete mathematical specification of the Universal Evolution Thermodynamics (UET) framework. The framework models coupled field systems undergoing phase transitions and symmetry breaking through gradient flow dynamics on a Landau-Ginzburg free energy functional.

---

## 1. Energy Functional

### 1.1 Single Field (C-only Model)

For a single order parameter field $C(\mathbf{x}, t)$ on a periodic domain $\Omega = [0, L]^d$:

$$\Omega[C] = \int_\Omega \left[ V(C) + \frac{\kappa}{2}|\nabla C|^2 \right] d\mathbf{x}$$

where:
- $V(C)$ is the Landau potential (local bulk energy)
- $\frac{\kappa}{2}|\nabla C|^2$ is the gradient energy (surface tension)

### 1.2 Quartic Landau Potential

The quartic (double-well) potential:

$$V(u) = \frac{a}{2}u^2 + \frac{\delta}{4}u^4 - su$$

Parameters:
| Parameter | Physical Meaning | Typical Range |
|-----------|-----------------|---------------|
| $a$ | Quadratic coefficient | $a < 0$ for double-well |
| $\delta$ | Quartic coefficient | $\delta > 0$ for boundedness |
| $s$ | External field / tilt | Controls symmetry breaking |

**Critical Points:** For $s = 0$, the minima are at $u^* = \pm\sqrt{-a/\delta}$ when $a < 0$.

### 1.3 Coupled Fields (C-I Model)

For two coupled fields $C(\mathbf{x}, t)$ and $I(\mathbf{x}, t)$:

$$\Omega[C, I] = \int_\Omega \left[ V_C(C) + V_I(I) - \beta C \cdot I + \frac{\kappa_C}{2}|\nabla C|^2 + \frac{\kappa_I}{2}|\nabla I|^2 \right] d\mathbf{x}$$

where:
- $V_C(C)$, $V_I(I)$ are individual Landau potentials
- $-\beta C \cdot I$ is the coupling energy (negative = cooperative)
- $\beta > 0$ promotes alignment of fields

### 1.4 Energy Decomposition

The total energy decomposes as:

$$\Omega = \Omega_{\text{pot}} + \Omega_{\text{coup}} + \Omega_{\text{grad}}$$

| Component | Definition | Physical Meaning |
|-----------|------------|------------------|
| $\Omega_{\text{pot}}$ | $\int [V_C(C) + V_I(I)] d\mathbf{x}$ | Bulk potential energy |
| $\Omega_{\text{coup}}$ | $\int [-\beta C \cdot I] d\mathbf{x}$ | Coupling energy |
| $\Omega_{\text{grad}}$ | $\int \frac{1}{2}[\kappa_C|\nabla C|^2 + \kappa_I|\nabla I|^2] d\mathbf{x}$ | Gradient (surface) energy |

---

## 2. Dynamics

### 2.1 Gradient Flow (Model A / Allen-Cahn)

The dynamics follow $L^2$ gradient descent:

$$\frac{\partial C}{\partial t} = -M_C \frac{\delta\Omega}{\delta C} = -M_C \mu_C$$

$$\frac{\partial I}{\partial t} = -M_I \frac{\delta\Omega}{\delta I} = -M_I \mu_I$$

where the chemical potentials are:

$$\mu_C = V'_C(C) - \beta I - \kappa_C \nabla^2 C$$
$$\mu_I = V'_I(I) - \beta C - \kappa_I \nabla^2 I$$

### 2.2 Energy Dissipation (Lyapunov Property)

**Theorem 1 (Energy Monotonicity):** Along solutions of the gradient flow:

$$\frac{d\Omega}{dt} = -\int_\Omega \left[ M_C |\mu_C|^2 + M_I |\mu_I|^2 \right] d\mathbf{x} \leq 0$$

**Proof:** Direct computation using the chain rule and integration by parts with periodic boundary conditions. □

**Corollary:** $\Omega$ is a Lyapunov functional; stationary points are characterized by $\mu_C = \mu_I = 0$.

---

## 3. Discretization

### 3.1 Spatial Discretization

We use a uniform grid with $N$ points per dimension:
- Grid spacing: $\Delta x = L/N$
- Points: $x_j = j \cdot \Delta x$ for $j = 0, 1, \ldots, N-1$

**Spectral Laplacian (Periodic BC):**

$$(\nabla^2 u)_j = \mathcal{F}^{-1}[-|k|^2 \hat{u}_k]$$

where $k$ are the discrete wavenumbers: $k_j = \frac{2\pi}{L} \cdot \begin{cases} j & j < N/2 \\ j - N & j \geq N/2 \end{cases}$

**Spectral Gradient Energy:**

$$E_{\text{grad}} = \frac{\kappa}{2} \sum_k |k|^2 |\hat{u}_k|^2$$

### 3.2 Temporal Discretization (Semi-Implicit)

**Stiff Linear + Explicit Nonlinear:**

$$(1 - \alpha \Delta t \nabla^2) C^{n+1} = C^n + \Delta t \cdot R^n$$

where:
- Linear diffusion handled implicitly (Fourier space division)
- Nonlinear reaction term $R^n = -M[V'(C^n) - \beta I^n]$ explicit

**In Fourier Space:**

$$\hat{C}^{n+1}_k = \frac{\hat{C}^n_k + \Delta t \cdot \hat{R}^n_k}{1 + \alpha \Delta t |k|^2}$$

where $\alpha = M \kappa$.

---

## 4. Stability and Coercivity

### 4.1 Coercivity Condition

**Definition:** The energy functional is coercive if $\Omega[u] \to +\infty$ as $\|u\|_{H^1} \to \infty$.

**Theorem 2 (Coercivity):** For the quartic potential, $\Omega$ is coercive if and only if:
1. $\delta > 0$ (quartic term positive)
2. $\kappa > 0$ (gradient penalty positive)

**Coupled System Additional Condition:**
3. $|\beta| < \sqrt{\delta_C \delta_I}$ (coupling not too strong)

### 4.2 Numerical Stability

**CFL-type Condition:** For explicit treatment of reaction term:

$$\Delta t \leq \frac{C_{\text{CFL}}}{M \cdot L_V}$$

where $L_V = \sup_{u}|V''(u)| = |a| + 3\delta u_{\max}^2$ is the Lipschitz constant.

### 4.3 Energy Monitoring (Backtracking)

To preserve discrete energy monotonicity:

**Algorithm 1: Adaptive Backtracking**
```
1. Propose step: C_cand = step(C, dt)
2. Check: dΩ = Ω(C_cand) - Ω(C)
3. If dΩ > tol:
     dt ← dt × factor
     goto 1
4. Accept C_cand
```

Parameters:
- `tol`: tolerance for energy increase (default: $10^{-10}$)
- `factor`: backtrack factor (default: 0.5)
- `max_backtracks`: limit (default: 20)

---

## 5. Phase Classification

### 5.1 Order Parameter

Define the mean-field order parameter:

$$\langle C \rangle = \frac{1}{|\Omega|} \int_\Omega C(\mathbf{x}) d\mathbf{x}$$

### 5.2 Bias Metric

For coupled fields:

$$\text{bias}_{CI} = \langle C \rangle - \langle I \rangle$$

### 5.3 Phase Labels

| Phase | Condition | Physical Meaning |
|-------|-----------|------------------|
| **BIAS_C** | $\langle C \rangle > \theta$ and $\langle C \rangle > \langle I \rangle$ | C-dominant |
| **BIAS_I** | $\langle I \rangle > \theta$ and $\langle I \rangle > \langle C \rangle$ | I-dominant |
| **SYM** | Otherwise | Symmetric/disordered |

Default threshold: $\theta = 0.1$

---

## 6. Dimensional Analysis

### 6.1 Characteristic Scales

| Quantity | Scale | Expression |
|----------|-------|------------|
| Length | $\xi$ | $\xi = \sqrt{\kappa/|a|}$ (correlation length) |
| Energy | $\epsilon$ | $\epsilon = a^2/\delta$ (barrier height) |
| Time | $\tau$ | $\tau = 1/(M|a|)$ (relaxation time) |

### 6.2 Dimensionless Parameters

Rescaling $x \to x/\xi$, $t \to t/\tau$, $u \to u/u^*$:

$$\tilde{\Omega} = \int \left[ -\frac{1}{2}\tilde{u}^2 + \frac{1}{4}\tilde{u}^4 - \tilde{s}\tilde{u} + \frac{1}{2}|\tilde{\nabla}\tilde{u}|^2 \right] d\tilde{\mathbf{x}}$$

**Dimensionless tilt:** $\tilde{s} = s/(a u^*) = s \sqrt{\delta/|a|^3}$

### 6.3 Calibration

**Calibratable Parameters:**
- $s$: External field (maps to external bias/incentive)
- $\beta$: Coupling strength (maps to interaction intensity)
- $M$: Mobility (maps to timescale)

**Fixed Parameters (theory):**
- $a = -1$ (normalized)
- $\delta = 1$ (normalized)
- $\kappa = \xi^2$ (set by desired correlation length)

---

## 7. Implementation Reference

### 7.1 Core Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `omega_C()` | `energy.py` | Total energy (C-only) |
| `omega_CI()` | `energy.py` | Total energy (coupled) |
| `omega_CI_decomposed()` | `energy.py` | Decomposed energy |
| `mu_CI()` | `variational.py` | Chemical potentials |
| `run_case()` | `solver.py` | Main simulation loop |

### 7.2 Validation

**Coercivity Check:** `check_C_only()`, `check_CI()` in `coercivity.py`

**Energy Monotonicity:** Tracked via `dt_backtracks_total` and `acceptance_ratio`

---

## 8. References

1. Landau, L.D. (1937). "On the theory of phase transitions."
2. Ginzburg, V.L. & Landau, L.D. (1950). "On the theory of superconductivity."
3. Allen, S.M. & Cahn, J.W. (1979). "A microscopic theory for antiphase boundary motion."
4. Chen, L.Q. (2002). "Phase-field models for microstructure evolution." *Annu. Rev. Mater. Res.*

---

## Appendix A: Full Energy Formula

**C-I Model (Discrete):**

$$\Omega = \Delta x^2 \sum_{i,j} \left[ V_C(C_{ij}) + V_I(I_{ij}) - \beta C_{ij} I_{ij} \right] + \frac{\kappa_C}{2} E_{\text{grad}}[C] + \frac{\kappa_I}{2} E_{\text{grad}}[I]$$

where $E_{\text{grad}}[u] = \sum_k |k|^2 |\hat{u}_k|^2$ (Parseval).

---

## Appendix B: Proof of Lyapunov Property

**Claim:** $\frac{d\Omega}{dt} \leq 0$ along gradient flow dynamics.

**Proof:**

$$\frac{d\Omega}{dt} = \int \frac{\delta\Omega}{\delta C} \frac{\partial C}{\partial t} + \frac{\delta\Omega}{\delta I} \frac{\partial I}{\partial t} d\mathbf{x}$$

Substituting $\partial_t C = -M_C \mu_C$ and $\partial_t I = -M_I \mu_I$:

$$= \int \mu_C (-M_C \mu_C) + \mu_I (-M_I \mu_I) d\mathbf{x}$$

$$= -\int M_C |\mu_C|^2 + M_I |\mu_I|^2 d\mathbf{x} \leq 0$$

Equality holds iff $\mu_C = \mu_I = 0$ (stationary point). □
