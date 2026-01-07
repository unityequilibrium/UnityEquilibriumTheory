# 📐 UET Core Variables

All variables have **clear definitions**, **units**, and **measurement methods**.

---

## 1. C — Communication Rate

| Property | Value |
|:---------|:------|
| **Name** | Communication Rate |
| **Symbol** | $C$ |
| **Definition** | Rate of information exchange across a system boundary |
| **Units** | bits per second (bits/s) |
| **Range** | $[0, \infty)$ |
| **Measurement** | Count state changes per unit time at system boundary |
| **Dimensionless** | $\tilde{C} = C / C_{max}$ where $C_{max}$ = max observed rate |

**Physical Interpretation:**
- In Galaxies: Rate of gravitational information exchange
- In Markets: Rate of price discovery (trades per second × information per trade)

---

## 2. I — Insulation (Resistance to Flow)

| Property | Value |
|:---------|:------|
| **Name** | Insulation |
| **Symbol** | $I$ |
| **Definition** | Resistance to information flow across boundary |
| **Units** | seconds per bit (s/bit) |
| **Range** | $[0, \infty)$ |
| **Measurement** | $I = 1/C$ when system is in equilibrium |
| **Dimensionless** | $\tilde{I} = I / I_{ref}$ |

**Physical Interpretation:**
- High $I$ = Slow information flow = "Insulated" system
- Low $I$ = Fast information flow = "Conductive" system

---

## 3. V — Value (Stored Information)

| Property | Value |
|:---------|:------|
| **Name** | Value (Information Content) |
| **Symbol** | $V$ |
| **Definition** | Total information stored within system boundary |
| **Units** | bits or Joules (via Landauer: $E = k_B T \ln(2) \times V$) |
| **Range** | $[0, \infty)$ |
| **Measurement** | $V = \int_{t_0}^{t} C \cdot dt$ (accumulated information) |
| **Dimensionless** | $\tilde{V} = V / V_{ref}$ |

**Physical Interpretation:**
- In Galaxies: Total gravitational binding energy (in bits)
- In Markets: Total market capitalization (in bits of confidence)

---

## 4. Ω — Oscillation Frequency

| Property | Value |
|:---------|:------|
| **Name** | Oscillation Frequency |
| **Symbol** | $\Omega$ |
| **Definition** | Rate of value fluctuation around equilibrium |
| **Units** | Hertz (Hz) or $s^{-1}$ |
| **Range** | $[0, \infty)$ |
| **Measurement** | FFT peak frequency of $V(t)$ time series |
| **Dimensionless** | $\tilde{\Omega} = \Omega / \Omega_{ref}$ |

**Physical Interpretation:**
- High $\Omega$ = Volatile system (fast oscillations)
- Low $\Omega$ = Stable system (slow drift)

---

## Summary Table

| Variable | Units | How to Measure |
|:---------|:------|:---------------|
| $C$ | bits/s | Count state changes at boundary |
| $I$ | s/bit | Inverse of $C$ at equilibrium |
| $V$ | bits | Integrate $C$ over time |
| $\Omega$ | Hz | FFT of $V(t)$ |

---

*All variables are now rigorously defined.*
*Ready for equations.*
