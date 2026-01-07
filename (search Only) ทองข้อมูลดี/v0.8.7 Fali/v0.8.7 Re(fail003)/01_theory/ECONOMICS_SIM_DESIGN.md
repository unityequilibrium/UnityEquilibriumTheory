# 📉 Economics Simulation Design: The UET Value Metric

**Goal:** Detect the "Dot Com Bubble" (2000) using UET variables instead of traditional technical indicators.

## 1. The Core Variables
UET maps Economic data to Energy Dynamics:

| Physics/UET | Economics Mapping | Logic |
|---|---|---|
| **Energy (E)** | **Money / Capital** | The capacity to do work (hire/build). |
| **Activity (C)** | **Trading Volume** | High C = High Hype/Flow (Openness). |
| **Organization (I)** | **Earnings / Profit** | Realized structure (Closure/Result). |
| **Value (V)** | **UET Intrinsic Value** | The "True Worth" of the system. |

## 2. The Hypothesis

**Hypothesis:** A "Bubble" occurs when **Price (Hype) decouples from Value (Reality).**
- In UET: Price is driven by $C$ (Activity).
- In UET: Value is driven by $I$ (Earnings).
- **Bubble Condition:** $\text{Price} \gg V(I, C)$.

## 3. The UET Formula
We propose a "Universal Value Equation":
$$ V_{uet} = \text{Earnings} \times \left( \frac{\text{Earnings}}{\text{Volume}} \right)^\alpha $$
*Interpretation:* Value increases with Earnings, but is *penalized* if Volume (C) is too high relative to Earnings (Hype ratio).

## 4. The Experiment
1.  **Load:** `research_v3/01_data/sp500_bubble.csv`.
2.  **Calculate:** $V_{uet}$ for each year.
3.  **Compare:** Plot `SP500_Price` (Red) vs `V_uet` (Green).
4.  **Prediction:** The Red line should skyrocket above Green in 1999-2000, predicting the crash.

## 5. Success Criteria
- The model must identify the **Year 2000** as the peak divergence.
- It must clearly warn of "Negative Value Pressure" ($\Omega$) before the crash.
