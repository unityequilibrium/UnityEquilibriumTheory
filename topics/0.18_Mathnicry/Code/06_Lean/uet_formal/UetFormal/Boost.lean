/-
F7: the boost charge of the parent action in flat space, and why it needs one light cone
(claim C_NOETHER_COVERAGE, boost part).

Setting and notation as in `EnergyMomentum` (F6): n fields with kinetic coefficients Z_A and squared speeds c_A,
any differentiable potential V; H, S are the energy density and flux, P, Pi the momentum density and flux,
E_A the Euler-Lagrange residuals. For a boost with squared speed c the charge density and flux are
    K^t = x H + c t P,      K^x = x S + c t Pi
(the integral of K^t is the boost charge K = int x H dx - t p_phys with p_phys = -P, written for speed c).

Theorems proved here:
  * `boost_identity`: d_t K^t + d_x K^x = x sum_A d_t chi_A E_A + c t sum_A d_x chi_A E_A
        + sum_A Z_A (c - c_A) d_t chi_A d_x chi_A,  at every point, on or off shell.
  * `boost_identity_one_light_cone`: if every field has speed c (c_A = c), the last sum vanishes, so on shell
    the boost charge is conserved.
  * `boost_fails_without_one_light_cone`: if some field has c_A /= c, then on shell d_t K^t + d_x K^x equals
    Z_A (c - c_A) d_t chi_A d_x chi_A (for one field), which is nonzero wherever Z_A, d_t chi_A and d_x chi_A are.
So the boost charge is conserved exactly when the fields share one light cone, as the numerical tests found.
-/
import Mathlib
import UetFormal.EnergyMomentum

namespace UetFormal

open Finset

variable {n : ℕ}

theorem hasDerivAt_Hden_t (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ)
    (hV : DifferentiableAt ℝ V (fieldAt χ t x)) (hr : Regular χ t x) :
    HasDerivAt (fun s => Hden Z c V χ s x)
      ((∑ A, Z A * (dT' (χ A) t x * dT' (dT' (χ A)) t x + c A * (dX' (χ A) t x * dT' (dX' (χ A)) t x)))
        + ∑ A, dV V (fieldAt χ t x) A * dT' (χ A) t x) t :=
  (hasDerivAt_kin_t Z c χ t x hr).add (hasDerivAt_potential_t V χ t x hV hr.t0)

theorem hasDerivAt_Piflux_x (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ)
    (hV : DifferentiableAt ℝ V (fieldAt χ t x)) (hr : Regular χ t x) :
    HasDerivAt (fun y => Piflux Z c V χ t y)
      (-(∑ A, Z A * (dT' (χ A) t x * dX' (dT' (χ A)) t x + c A * (dX' (χ A) t x * dX' (dX' (χ A)) t x)))
        + ∑ A, dV V (fieldAt χ t x) A * dX' (χ A) t x) x :=
  (hasDerivAt_kin_x Z c χ t x hr).neg.add (hasDerivAt_potential_x V χ t x hV hr.x0)

theorem hasDerivAt_Sflux_x (Z c : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) (hr : Regular χ t x) :
    HasDerivAt (fun y => Sflux Z c χ t y)
      (-∑ A, Z A * c A * (dX' (dT' (χ A)) t x * dX' (χ A) t x + dT' (χ A) t x * dX' (dX' (χ A)) t x)) x := by
  have hsum : HasDerivAt (fun y => ∑ A, Z A * c A * dT' (χ A) t y * dX' (χ A) t y)
      (∑ A, Z A * c A * (dX' (dT' (χ A)) t x * dX' (χ A) t x + dT' (χ A) t x * dX' (dX' (χ A)) t x)) x := by
    refine HasDerivAt.fun_sum (fun A _ => ?_)
    have h := (((hr.xt A).hasDerivAt).mul ((hr.xx A).hasDerivAt)).const_mul (Z A * c A)
    convert h using 1
    · funext y; simp only [Pi.mul_apply]; ring
    · simp only [dX']
  exact hsum.neg

theorem hasDerivAt_Pden_t (Z : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) (hr : Regular χ t x) :
    HasDerivAt (fun s => Pden Z χ s x)
      (∑ A, Z A * (dT' (dT' (χ A)) t x * dX' (χ A) t x + dT' (χ A) t x * dT' (dX' (χ A)) t x)) t := by
  refine HasDerivAt.fun_sum (fun A _ => ?_)
  have h := (((hr.tt A).hasDerivAt).mul ((hr.tx A).hasDerivAt)).const_mul (Z A)
  convert h using 1
  · funext s; simp only [Pi.mul_apply]; ring
  · simp only [dT']

/-- Boost charge density for a boost with squared speed `cb`. -/
noncomputable def Kt (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (cb t x : ℝ) : ℝ :=
  x * Hden Z c V χ t x + cb * t * Pden Z χ t x

/-- Boost charge flux. -/
noncomputable def Kx (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (cb t x : ℝ) : ℝ :=
  x * Sflux Z c χ t x + cb * t * Piflux Z c V χ t x

/-- The boost identity, off shell, for any speeds. -/
theorem boost_identity (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (cb t x : ℝ)
    (hV : DifferentiableAt ℝ V (fieldAt χ t x)) (hr : Regular χ t x) :
    deriv (fun s => Kt Z c V χ cb s x) t + deriv (fun y => Kx Z c V χ cb t y) x
      = x * ∑ A, dT' (χ A) t x * ELres Z c V χ A t x
        + cb * t * ∑ A, dX' (χ A) t x * ELres Z c V χ A t x
        + ∑ A, Z A * (cb - c A) * dT' (χ A) t x * dX' (χ A) t x := by
  have hKt : HasDerivAt (fun s => Kt Z c V χ cb s x)
      (x * ((∑ A, Z A * (dT' (χ A) t x * dT' (dT' (χ A)) t x + c A * (dX' (χ A) t x * dT' (dX' (χ A)) t x)))
          + ∑ A, dV V (fieldAt χ t x) A * dT' (χ A) t x)
        + (cb * 1 * Pden Z χ t x
          + cb * t * ∑ A, Z A * (dT' (dT' (χ A)) t x * dX' (χ A) t x + dT' (χ A) t x * dT' (dX' (χ A)) t x))) t := by
    have h1 := (hasDerivAt_Hden_t Z c V χ t x hV hr).const_mul x
    have h2 := ((hasDerivAt_id t).const_mul cb).mul (hasDerivAt_Pden_t Z χ t x hr)
    have h := h1.add h2
    convert h using 1
    all_goals (try funext _)
    all_goals simp only [Kt, Pi.add_apply, Pi.mul_apply, id]
  have hKx : HasDerivAt (fun y => Kx Z c V χ cb t y)
      ((1 * Sflux Z c χ t x
          + x * -∑ A, Z A * c A * (dX' (dT' (χ A)) t x * dX' (χ A) t x + dT' (χ A) t x * dX' (dX' (χ A)) t x))
        + cb * t * (-(∑ A, Z A * (dT' (χ A) t x * dX' (dT' (χ A)) t x
              + c A * (dX' (χ A) t x * dX' (dX' (χ A)) t x)))
          + ∑ A, dV V (fieldAt χ t x) A * dX' (χ A) t x)) x := by
    have h1 := (hasDerivAt_id x).mul (hasDerivAt_Sflux_x Z c χ t x hr)
    have h2 := (hasDerivAt_Piflux_x Z c V χ t x hV hr).const_mul (cb * t)
    have h := h1.add h2
    convert h using 1
    all_goals (try funext _)
    all_goals simp only [Kx, Pi.add_apply, Pi.mul_apply, id]
  rw [hKt.deriv, hKx.deriv]
  unfold ELres Sflux Pden
  simp only [Finset.mul_sum, ← Finset.sum_add_distrib, ← Finset.sum_neg_distrib, mul_neg]
  refine Finset.sum_congr rfl (fun A _ => ?_)
  rw [hr.mixed A]
  ring

/-- With one light cone (`c A = cb` for every field) the boost charge is conserved on shell. -/
theorem boost_identity_one_light_cone (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ)
    (cb t x : ℝ) (hV : DifferentiableAt ℝ V (fieldAt χ t x)) (hr : Regular χ t x) (hc : ∀ A, c A = cb)
    (hshell : ∀ A, ELres Z c V χ A t x = 0) :
    deriv (fun s => Kt Z c V χ cb s x) t + deriv (fun y => Kx Z c V χ cb t y) x = 0 := by
  rw [boost_identity Z c V χ cb t x hV hr]
  simp [hshell, hc]

/-- One field whose speed differs from the boost speed: on shell the boost charge changes at
`Z (cb - c) d_t chi d_x chi`, so it is not conserved wherever that product is nonzero. -/
theorem boost_fails_without_one_light_cone (Z c : Fin 1 → ℝ) (V : (Fin 1 → ℝ) → ℝ) (χ : Fin 1 → ℝ → ℝ → ℝ)
    (cb t x : ℝ) (hV : DifferentiableAt ℝ V (fieldAt χ t x)) (hr : Regular χ t x)
    (hshell : ∀ A, ELres Z c V χ A t x = 0)
    (hZ : Z 0 ≠ 0) (hne : cb ≠ c 0) (ht : dT' (χ 0) t x ≠ 0) (hx : dX' (χ 0) t x ≠ 0) :
    deriv (fun s => Kt Z c V χ cb s x) t + deriv (fun y => Kx Z c V χ cb t y) x ≠ 0 := by
  rw [boost_identity Z c V χ cb t x hV hr]
  simp only [hshell, mul_zero, Finset.sum_const_zero, zero_add, Fin.sum_univ_one]
  have : cb - c 0 ≠ 0 := sub_ne_zero.mpr hne
  exact mul_ne_zero (mul_ne_zero (mul_ne_zero hZ this) ht) hx

end UetFormal
