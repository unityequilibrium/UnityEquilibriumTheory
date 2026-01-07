# 🧬 Biology Simulation Design: The UET Health Metric

**Goal:** Distinguish "Healthy" vs "Stressed" states using UET Entropy Metrics on Heart Rate Variability (HRV) data.

## 1. The Core Variables
UET maps Biological data to Information Dynamics (Complexity Theory):

| Physics/UET | Biology Mapping | Logic |
|---|---|---|
| **Activity (C)** | **HRV (Variance)** | High C = Flexibility/Adaptability (Youth/Health). |
| **Closure (I)** | **Rigidity (Stress)** | High I = Inability to adapt (Stress/Age). |
| **Balance (Ω)** | **Homeostasis** | The optimal state between Chaos and Stasis. |
| **Value (V)** | **Health Score** | $V = C \times (1 - I_{excess})$. |

## 2. The Hypothesis

**Hypothesis:** Health is a state of **"Organized Instability"** (Criticality).
- **Too much Order (Low HRV):** Death/Stasis (Stressed/Aging).
- **Too much Chaos (Arrhythmia):** System failure.
- **Healthy:** High Variability (C) within a stable range.

## 3. The UET Formula
We propose a "UET Vitality Index":
$$ V_{vitality} = \sigma_{RR} \times \frac{1}{\mu_{RR}} $$
(Standard Deviation of RR intervals / Mean R) -> Coefficient of Variation.
*In UET terms:* $V = \frac{C}{I}$ (Openness divided by Inertia).

## 4. The Experiment
1.  **Load:** `research_v3/01_data/hrv_stress.csv`.
2.  **Calculate:** $V_{vitality}$ for each subject.
3.  **Compare:** Healthy should have HIGH score. Stressed should have LOW score.
4.  **Visualize:** Bar chart comparisons.

## 5. Success Criteria
- The model must clearly separate Subject A (Healthy) from Subject B (Stressed).
- It should show Subject D (Athlete) as having the highest Vitality.
