# 👥 Sociology Simulation Design: Polarization as Phase Separation

**Goal:** Model Political Polarization as a Thermodynamic "Phase Separation" (like Oil and Water).

## 1. The Core Variables
UET maps Social dynamics to Cahn-Hilliard Phase Separation physics:

| Physics/UET | Sociology Mapping | Logic |
|---|---|---|
| **Connectivity ($C$)** | **Media/Internet** | High C forces interaction. If $C$ is too high, system breaks. |
| **Temperature ($T$)** | **Social Tension** | The "Heat" in the system. |
| **Phase A / B** | **Left / Right Tribe** | Two distinct stable states. |
| **Interface Energy** | **Conflict** | The tension at the boundary between tribes. |

## 2. The Hypothesis

**Hypothesis:** Society is a **Spin Glass System**.
- **Low C (1950s):** Local interactions dominates. Mixtures are possible (bi-partisanship).
- **High C (2020s):** Global pressure forces alignment. The "Middle Ground" becomes energetically unstable.
- **Result:** Society **Phase Separates** into two pure, opposing poles to minimize stress.

## 3. The UET Formula
We check the correlation between **Connectivity** and **Polarization**:
$$ P(t) \propto \log(C(t)) $$
(Polarization scales with the magnitude of Information Pressure).

## 4. The Experiment
1.  **Load:** `research_v3/01_data/social_polarization.csv`.
2.  **Calculate:** The "Separation Force" driven by Connectivity.
3.  **Detect:** The "Tipping Point" (Year 2000+) where the middle ground disappears.
4.  **Visualize:** Connectivity vs Polarization.

## 5. Success Criteria
- The model must show that as `Connectivity_Index` rises, `Cross_Party_Voting` collapses.
- It validates that **"Hyper-connection leads to Tribalism"** (Counter-intuitive but thermodynamically true).
