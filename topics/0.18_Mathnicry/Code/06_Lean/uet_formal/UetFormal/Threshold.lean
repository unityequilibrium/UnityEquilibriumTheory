/-
F1: layer-3 persistence threshold in a chemostat (claim C_L3_SUPPLY_CHEMOSTAT).

Setting (core/03_lanes/persistence/uet_layer3_supply_chemostat.py):
  dR/dt = D S0 - D R - mu(R) n / Y,   dn/dt = (mu(R) - D) n.
An empty vessel holds R = S0, so a rare consumer grows at mu(S0) - D.
In layer-3 units S = D S0 (supply) and delta = D (loss).

Theorems proved here:
  * `rstar_exists`: a continuous uptake with mu 0 = 0 that exceeds D somewhere has a level R* with mu R* = D.
  * `invades_iff`: for strictly increasing uptake, mu(S0) - D > 0  <->  S0 > R*.
  * `invades_iff_supply`: the same in layer-3 units: rare-consumer growth > 0  <->  S > delta * R*.
  * `monod_rstar`: for Monod uptake mu R = mumax R / (K + R) with D < mumax, R* = K D / (mumax - D).
  * `monod_strictMonoOn`: Monod uptake is strictly increasing on [0, oo).
  * `invades_iff_monod`: the threshold for Monod uptake, combining the above.
-/
import Mathlib

namespace UetFormal

open Set

/-- A continuous uptake with `mu 0 = 0 < D < mu M` reaches the level `D` somewhere in `[0, M]`. -/
theorem rstar_exists (mu : ℝ → ℝ) (D M : ℝ) (hM : 0 ≤ M) (hcont : ContinuousOn mu (Icc 0 M))
    (h0 : mu 0 = 0) (hD : 0 < D) (hDM : D < mu M) :
    ∃ r ∈ Icc 0 M, mu r = D := by
  have hmem : D ∈ Icc (mu 0) (mu M) := ⟨by rw [h0]; exact hD.le, hDM.le⟩
  exact intermediate_value_Icc hM hcont hmem

/-- Invasion of an empty vessel: with strictly increasing uptake on `[0, oo)`,
the rare-consumer growth rate `mu S0 - D` is positive exactly when `S0 > R*`. -/
theorem invades_iff (mu : ℝ → ℝ) (D r S0 : ℝ) (hmono : StrictMonoOn mu (Ici 0))
    (hr : 0 ≤ r) (hS0 : 0 ≤ S0) (hrD : mu r = D) :
    0 < mu S0 - D ↔ r < S0 := by
  rw [sub_pos, ← hrD]
  exact hmono.lt_iff_lt hr hS0

/-- The same threshold in layer-3 units: supply `S = D * S0`, loss `delta = D`,
so the consumer persists exactly when `S > delta * R*` (the threshold `S* = delta R*_min`). -/
theorem invades_iff_supply (mu : ℝ → ℝ) (D r S0 : ℝ) (hmono : StrictMonoOn mu (Ici 0))
    (hr : 0 ≤ r) (hS0 : 0 ≤ S0) (hrD : mu r = D) (hD : 0 < D) :
    0 < mu S0 - D ↔ D * r < D * S0 := by
  rw [invades_iff mu D r S0 hmono hr hS0 hrD]
  constructor
  · intro h; nlinarith
  · intro h; nlinarith

/-- Monod uptake. -/
noncomputable def monod (mumax K : ℝ) (R : ℝ) : ℝ := mumax * R / (K + R)

/-- Tilman's closed form: Monod uptake reaches `D` at `R* = K D / (mumax - D)`. -/
theorem monod_rstar (mumax K D : ℝ) (hK : 0 < K) (hD : 0 < D) (hDm : D < mumax) :
    monod mumax K (K * D / (mumax - D)) = D := by
  unfold monod
  have hm : mumax ≠ 0 := by linarith
  have h1 : mumax - D ≠ 0 := by linarith
  have h2 : K + K * D / (mumax - D) = K * mumax / (mumax - D) := by
    field_simp
    ring
  rw [h2]
  have hK0 : K ≠ 0 := hK.ne'
  field_simp

/-- Monod uptake is strictly increasing on `[0, oo)` when `mumax > 0` and `K > 0`. -/
theorem monod_strictMonoOn (mumax K : ℝ) (hm : 0 < mumax) (hK : 0 < K) :
    StrictMonoOn (monod mumax K) (Ici 0) := by
  intro a ha b hb hab
  simp only [mem_Ici] at ha hb
  unfold monod
  have hKa : 0 < K + a := by linarith
  have hKb : 0 < K + b := by linarith
  rw [div_lt_div_iff₀ hKa hKb]
  nlinarith [mul_pos hm hK]

/-- The persistence threshold for Monod uptake: a rare consumer invades the empty chemostat
exactly when the supply concentration exceeds Tilman's `R* = K D / (mumax - D)`. -/
theorem invades_iff_monod (mumax K D S0 : ℝ) (hK : 0 < K) (hD : 0 < D) (hDm : D < mumax)
    (hS0 : 0 ≤ S0) :
    0 < monod mumax K S0 - D ↔ K * D / (mumax - D) < S0 := by
  have hm : 0 < mumax := by linarith
  have hr : 0 ≤ K * D / (mumax - D) := by
    have : 0 < mumax - D := by linarith
    positivity
  exact invades_iff (monod mumax K) D _ S0 (monod_strictMonoOn mumax K hm hK) hr hS0
    (monod_rstar mumax K D hK hD hDm)

end UetFormal
