/-
F2: layer 3 with trace feedback, the switch supply S_c (claim C_L3_TRACE_FEEDBACK).

Model (core/03_lanes/persistence/uet_layer3_trace_feedback.py): a shared trace E is written at w per unit
resource used and fades at kappa; capture of type i is a_i0 (1 + beta_i E). Type 1 has beta_1 = 0 and the
lower cost at E = 0 (r1 = d1/a10 < r20 = d2/a20); type 2 is helped by the trace (beta2 > 0).

With type 1 resident at steady state, R = r1 and kappa E1 = w (S - delta r1).
Type 2 entering that state grows at lambda = a20 (1 + beta2 E1) r1 - d2.

Theorems proved here:
  * `rstar2_lt_iff`: type 2 beats type 1 at trace level E  <->  E > E_c = (r20/r1 - 1)/beta2.
  * `invasion_rate_linear`: lambda = a20 r1 beta2 (w/kappa) (S - S_c), with
        S_c = delta r1 + kappa (r20/r1 - 1)/(w beta2).
  * `invasion_rate_zero_at_switch`: lambda = 0 at S = S_c.
  * `invades_iff_above_switch`: lambda > 0  <->  S > S_c  (the winner switches at S_c).
  * `switch_above_type1_threshold`: S_c > delta r1, so the switch lies above type 1's own persistence threshold.
-/
import Mathlib

namespace UetFormal

/-- Cost of type 2 at trace level `E`: `R*_2(E) = d2 / (a20 (1 + beta2 E))`. -/
noncomputable def rstar2 (a20 d2 beta2 E : ℝ) : ℝ := d2 / (a20 * (1 + beta2 * E))

/-- Critical trace level. -/
noncomputable def traceCrit (r1 r20 beta2 : ℝ) : ℝ := (r20 / r1 - 1) / beta2

/-- Switch supply. -/
noncomputable def switchSupply (delta r1 r20 beta2 w kappa : ℝ) : ℝ :=
  delta * r1 + kappa * (r20 / r1 - 1) / (w * beta2)

/-- Steady trace left by a type-1 resident: `kappa E1 = w (S - delta r1)`. -/
noncomputable def trace1 (S delta r1 w kappa : ℝ) : ℝ := w * (S - delta * r1) / kappa

/-- Invasion rate of type 2 into the type-1 steady state. -/
noncomputable def invasionRate (a20 d2 beta2 r1 S delta w kappa : ℝ) : ℝ :=
  a20 * (1 + beta2 * trace1 S delta r1 w kappa) * r1 - d2

theorem trace1_steady (S delta r1 w kappa : ℝ) (hk : 0 < kappa) :
    kappa * trace1 S delta r1 w kappa = w * (S - delta * r1) := by
  unfold trace1
  field_simp

/-- Type 2 is cheaper than type 1 exactly when the trace exceeds `E_c`. -/
theorem rstar2_lt_iff (a20 d2 beta2 r1 E : ℝ) (ha : 0 < a20) (hb : 0 < beta2)
    (hr1 : 0 < r1) (hE : 0 ≤ E) :
    rstar2 a20 d2 beta2 E < r1 ↔ traceCrit r1 (d2 / a20) beta2 < E := by
  unfold rstar2 traceCrit
  have h1 : 0 < 1 + beta2 * E := by nlinarith
  have hden : 0 < a20 * (1 + beta2 * E) := mul_pos ha h1
  rw [div_lt_iff₀ hden, div_lt_iff₀ hb, div_sub_one hr1.ne', div_lt_iff₀ hr1, sub_lt_iff_lt_add,
    div_lt_iff₀ ha]
  constructor
  · intro h; nlinarith
  · intro h; nlinarith

/-- The invasion rate is linear in the supply and vanishes at `S_c`. -/
theorem invasion_rate_linear (a20 beta2 r1 r20 S delta w kappa : ℝ)
    (hb : 0 < beta2) (hr1 : 0 < r1) (hw : 0 < w) (hk : 0 < kappa) :
    invasionRate a20 (a20 * r20) beta2 r1 S delta w kappa
      = a20 * r1 * beta2 * (w / kappa) * (S - switchSupply delta r1 r20 beta2 w kappa) := by
  unfold invasionRate trace1 switchSupply
  field_simp
  ring

theorem invasion_rate_zero_at_switch (a20 beta2 r1 r20 delta w kappa : ℝ)
    (hb : 0 < beta2) (hr1 : 0 < r1) (hw : 0 < w) (hk : 0 < kappa) :
    invasionRate a20 (a20 * r20) beta2 r1 (switchSupply delta r1 r20 beta2 w kappa) delta w kappa = 0 := by
  rw [invasion_rate_linear a20 beta2 r1 r20 _ delta w kappa hb hr1 hw hk]
  ring

/-- The winner switches at `S_c`: type 2 invades a type-1 resident exactly when `S > S_c`. -/
theorem invades_iff_above_switch (a20 beta2 r1 r20 S delta w kappa : ℝ)
    (ha : 0 < a20) (hb : 0 < beta2) (hr1 : 0 < r1) (hw : 0 < w) (hk : 0 < kappa) :
    0 < invasionRate a20 (a20 * r20) beta2 r1 S delta w kappa
      ↔ switchSupply delta r1 r20 beta2 w kappa < S := by
  rw [invasion_rate_linear a20 beta2 r1 r20 S delta w kappa hb hr1 hw hk]
  have hc : 0 < a20 * r1 * beta2 * (w / kappa) := by positivity
  constructor
  · intro h
    by_contra hle
    have hle' := not_lt.mp hle
    have : a20 * r1 * beta2 * (w / kappa) * (S - switchSupply delta r1 r20 beta2 w kappa) ≤ 0 :=
      mul_nonpos_of_nonneg_of_nonpos hc.le (by linarith [hle'])
    linarith
  · intro h
    exact mul_pos hc (by linarith)

/-- If type 1 is cheaper at `E = 0` (`r1 < r20`), the switch lies above type 1's persistence
threshold `delta r1`. -/
theorem switch_above_type1_threshold (delta r1 r20 beta2 w kappa : ℝ)
    (hr1 : 0 < r1) (hlt : r1 < r20) (hb : 0 < beta2) (hw : 0 < w) (hk : 0 < kappa) :
    delta * r1 < switchSupply delta r1 r20 beta2 w kappa := by
  unfold switchSupply
  have h1 : 0 < r20 / r1 - 1 := by
    rw [sub_pos, one_lt_div hr1]; exact hlt
  have : 0 < kappa * (r20 / r1 - 1) / (w * beta2) := by positivity
  linarith

end UetFormal
