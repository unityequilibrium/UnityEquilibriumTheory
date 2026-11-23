/-
F3: an isotropic matter pool cannot feed the response field (claim C_L3_FROM_ACTION, point 2).

At one loop the spectral weight of a spacelike phi mode (w, q) in a chi medium with occupation f is
    rho_f  ∝  ∫_{E1 >= a} [ f(E1) - f(E1 + w) ] dE1
(core/03_lanes/persistence/uet_layer3_from_action.py). For an isotropic pool f depends on energy only.
Positive rho means the mode is damped; a mode can only grow (be fed) if rho < 0.

Theorems proved here:
  * `isotropic_telescopes`: ∫_{x > a} [f x - f (x + w)] dx = ∫_a^{a+w} f  (the integral telescopes).
  * `isotropic_cannot_feed`: if f >= 0 (any occupation, thermal or not, inverted or not) and w >= 0,
    the spectral weight is >= 0, so an isotropic pool can only damp phi.
-/
import Mathlib

namespace UetFormal

open MeasureTheory Set

/-- Translating the integrand by `w` shifts the half-line `(a, oo)` to `(a + w, oo)`. -/
theorem integral_Ioi_comp_add (f : ℝ → ℝ) (a w : ℝ) :
    ∫ x in Ioi a, f (x + w) = ∫ x in Ioi (a + w), f x := by
  have hmp : MeasurePreserving (fun x : ℝ => x + w) volume volume := measurePreserving_add_right volume w
  have he : MeasurableEmbedding (fun x : ℝ => x + w) := (MeasurableEquiv.addRight w).measurableEmbedding
  rw [← hmp.setIntegral_preimage_emb he f (Ioi (a + w)), preimage_add_const_Ioi, add_sub_cancel_right]

/-- Integrability of the translated occupation on `(a, oo)`. -/
theorem integrableOn_Ioi_comp_add (f : ℝ → ℝ) (a w : ℝ) (hw : 0 ≤ w) (hf : IntegrableOn f (Ioi a)) :
    IntegrableOn (fun x => f (x + w)) (Ioi a) := by
  have hmp : MeasurePreserving (fun x : ℝ => x + w) volume volume := measurePreserving_add_right volume w
  have he : MeasurableEmbedding (fun x : ℝ => x + w) := (MeasurableEquiv.addRight w).measurableEmbedding
  have h1 : IntegrableOn f (Ioi (a + w)) := hf.mono_set (Ioi_subset_Ioi (by linarith))
  have h2 := (hmp.integrableOn_comp_preimage he).mpr h1
  rwa [preimage_add_const_Ioi, add_sub_cancel_right] at h2

/-- The scattering integral telescopes to the occupation integrated over one window of width `w`. -/
theorem isotropic_telescopes (f : ℝ → ℝ) (a w : ℝ) (hw : 0 ≤ w) (hf : IntegrableOn f (Ioi a)) :
    ∫ x in Ioi a, (f x - f (x + w)) = ∫ x in a..a + w, f x := by
  rw [integral_sub hf (integrableOn_Ioi_comp_add f a w hw hf), integral_Ioi_comp_add,
    intervalIntegral.integral_Ioi_sub_Ioi hf (by linarith)]

/-- An isotropic pool, with any non-negative occupation, gives non-negative spectral weight:
it can only damp the response field, never feed it. -/
theorem isotropic_cannot_feed (f : ℝ → ℝ) (a w : ℝ) (hw : 0 ≤ w) (hf : IntegrableOn f (Ioi a))
    (hpos : ∀ x, 0 ≤ f x) :
    0 ≤ ∫ x in Ioi a, (f x - f (x + w)) := by
  rw [isotropic_telescopes f a w hw hf]
  exact intervalIntegral.integral_nonneg (by linarith) (fun x _ => hpos x)

end UetFormal
