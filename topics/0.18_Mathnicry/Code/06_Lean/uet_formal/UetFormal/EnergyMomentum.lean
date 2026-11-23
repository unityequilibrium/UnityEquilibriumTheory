/-
F6: energy and momentum identities of the parent action in flat space, off shell
(claim C_NOETHER_COVERAGE, translation part).

Setting (core/03_lanes/symmetry/uet_noether.py, flat 1+1 dimensions, gravity decoupled): n real fields
chi_A (for the action n = 3: phi, chi1, chi2), each with its own kinetic coefficient Z_A and squared speed c_A,
and one potential V of all fields together (for the action: eps U(phi) + W(|chi|^2) + the portal):
    L = sum_A Z_A/2 (d_t chi_A^2 - c_A d_x chi_A^2) - V(chi).
Euler-Lagrange residuals:  E_A = Z_A (d_t^2 chi_A - c_A d_x^2 chi_A) + dV/dchi_A.
Energy density and flux:   H = sum_A Z_A/2 (d_t chi_A^2 + c_A d_x chi_A^2) + V,   S = -sum_A Z_A c_A d_t chi_A d_x chi_A.
Momentum density and flux: P = sum_A Z_A d_t chi_A d_x chi_A,                     Pi = -sum_A Z_A/2 (d_t chi_A^2 + c_A d_x chi_A^2) + V.

Theorems proved here (V any function differentiable at the field point; fields with the slice derivatives
named in the hypotheses and equal mixed partials d_x d_t chi_A = d_t d_x chi_A, which holds for C^2 fields):
  * `hasDerivAt_potential_t`, `hasDerivAt_potential_x`: chain rule, d_mu V(chi) = sum_A dV/dchi_A d_mu chi_A.
  * `energy_identity`:   d_t H + d_x S  = sum_A d_t chi_A E_A   at every point, on or off shell.
  * `momentum_identity`: d_t P + d_x Pi = sum_A d_x chi_A E_A   at every point, on or off shell.
On shell (all E_A = 0) energy and momentum are conserved for any speeds c_A and any potential, the portal
included. The boost charge needs equal speeds; that part is not proved here.
-/
import Mathlib

namespace UetFormal

open Finset

variable {n : ℕ}

/-- Time and space slices of a field `φ t x` (as in `NoetherO2`). -/
noncomputable def dT' (φ : ℝ → ℝ → ℝ) (t x : ℝ) : ℝ := deriv (fun s => φ s x) t
noncomputable def dX' (φ : ℝ → ℝ → ℝ) (t x : ℝ) : ℝ := deriv (fun y => φ t y) x

/-- The field point `(chi_A t x)_A`. -/
def fieldAt (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) : Fin n → ℝ := fun A => χ A t x

/-- Partial derivative of the potential along field `A`. -/
noncomputable def dV (V : (Fin n → ℝ) → ℝ) (p : Fin n → ℝ) (A : Fin n) : ℝ :=
  fderiv ℝ V p (Pi.single A 1)

/-- Euler-Lagrange residual of field `A`. -/
noncomputable def ELres (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (A : Fin n)
    (t x : ℝ) : ℝ :=
  Z A * (dT' (dT' (χ A)) t x - c A * dX' (dX' (χ A)) t x) + dV V (fieldAt χ t x) A

/-- Kinetic-gradient part shared by `H` and `Pi`. -/
noncomputable def kin (Z c : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) : ℝ :=
  ∑ A, Z A / 2 * ((dT' (χ A) t x) ^ 2 + c A * (dX' (χ A) t x) ^ 2)

noncomputable def Hden (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) : ℝ :=
  kin Z c χ t x + V (fieldAt χ t x)

noncomputable def Sflux (Z c : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) : ℝ :=
  -∑ A, Z A * c A * dT' (χ A) t x * dX' (χ A) t x

noncomputable def Pden (Z : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) : ℝ :=
  ∑ A, Z A * dT' (χ A) t x * dX' (χ A) t x

noncomputable def Piflux (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) : ℝ :=
  -kin Z c χ t x + V (fieldAt χ t x)

/-- A linear map on `Fin n → ℝ` is the sum of its values on the basis vectors. -/
theorem clm_apply_eq_sum (L : (Fin n → ℝ) →L[ℝ] ℝ) (v : Fin n → ℝ) :
    L v = ∑ A, L (Pi.single A 1) * v A := by
  conv_lhs => rw [← Finset.univ_sum_single v]
  rw [map_sum]
  refine Finset.sum_congr rfl (fun A _ => ?_)
  have : Pi.single A (v A) = v A • (Pi.single A (1 : ℝ) : Fin n → ℝ) := by
    rw [← Pi.single_smul, smul_eq_mul, mul_one]
  rw [this, map_smul, smul_eq_mul, mul_comm]

/-- Chain rule in time. -/
theorem hasDerivAt_potential_t (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ)
    (hV : DifferentiableAt ℝ V (fieldAt χ t x))
    (ht : ∀ A, DifferentiableAt ℝ (fun s => χ A s x) t) :
    HasDerivAt (fun s => V (fieldAt χ s x))
      (∑ A, dV V (fieldAt χ t x) A * dT' (χ A) t x) t := by
  have hpath : HasDerivAt (fun s => fieldAt χ s x) (fun A => dT' (χ A) t x) t := by
    rw [hasDerivAt_pi]
    intro A
    exact (ht A).hasDerivAt
  have h := hV.hasFDerivAt.comp_hasDerivAt t hpath
  rw [clm_apply_eq_sum] at h
  exact h

/-- Chain rule in space. -/
theorem hasDerivAt_potential_x (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ)
    (hV : DifferentiableAt ℝ V (fieldAt χ t x))
    (hx : ∀ A, DifferentiableAt ℝ (fun y => χ A t y) x) :
    HasDerivAt (fun y => V (fieldAt χ t y))
      (∑ A, dV V (fieldAt χ t x) A * dX' (χ A) t x) x := by
  have hpath : HasDerivAt (fun y => fieldAt χ t y) (fun A => dX' (χ A) t x) x := by
    rw [hasDerivAt_pi]
    intro A
    exact (hx A).hasDerivAt
  have h := hV.hasFDerivAt.comp_hasDerivAt x hpath
  rw [clm_apply_eq_sum] at h
  exact h

/-- Smoothness assumed at the point `(t, x)`: the slice derivatives used below exist, and the mixed partials
agree. -/
structure Regular (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) : Prop where
  t0 : ∀ A, DifferentiableAt ℝ (fun s => χ A s x) t
  x0 : ∀ A, DifferentiableAt ℝ (fun y => χ A t y) x
  tt : ∀ A, DifferentiableAt ℝ (fun s => dT' (χ A) s x) t
  tx : ∀ A, DifferentiableAt ℝ (fun s => dX' (χ A) s x) t
  xt : ∀ A, DifferentiableAt ℝ (fun y => dT' (χ A) t y) x
  xx : ∀ A, DifferentiableAt ℝ (fun y => dX' (χ A) t y) x
  mixed : ∀ A, dX' (dT' (χ A)) t x = dT' (dX' (χ A)) t x

theorem hasDerivAt_kin_t (Z c : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) (hr : Regular χ t x) :
    HasDerivAt (fun s => kin Z c χ s x)
      (∑ A, Z A * (dT' (χ A) t x * dT' (dT' (χ A)) t x + c A * (dX' (χ A) t x * dT' (dX' (χ A)) t x))) t := by
  refine HasDerivAt.fun_sum (fun A _ => ?_)
  have h1 := ((hr.tt A).hasDerivAt).pow 2
  have h2 := ((hr.tx A).hasDerivAt).pow 2
  have h := ((h1.add (h2.const_mul (c A))).const_mul (Z A / 2))
  convert h using 1
  simp only [dT']
  push_cast
  ring

theorem hasDerivAt_kin_x (Z c : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ) (hr : Regular χ t x) :
    HasDerivAt (fun y => kin Z c χ t y)
      (∑ A, Z A * (dT' (χ A) t x * dX' (dT' (χ A)) t x + c A * (dX' (χ A) t x * dX' (dX' (χ A)) t x))) x := by
  refine HasDerivAt.fun_sum (fun A _ => ?_)
  have h1 := ((hr.xt A).hasDerivAt).pow 2
  have h2 := ((hr.xx A).hasDerivAt).pow 2
  have h := ((h1.add (h2.const_mul (c A))).const_mul (Z A / 2))
  convert h using 1
  simp only [dX']
  push_cast
  ring

/-- Energy identity, off shell: `d_t H + d_x S = sum_A d_t chi_A E_A`. -/
theorem energy_identity (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ)
    (hV : DifferentiableAt ℝ V (fieldAt χ t x)) (hr : Regular χ t x) :
    deriv (fun s => Hden Z c V χ s x) t + deriv (fun y => Sflux Z c χ t y) x
      = ∑ A, dT' (χ A) t x * ELres Z c V χ A t x := by
  have hH : HasDerivAt (fun s => Hden Z c V χ s x)
      ((∑ A, Z A * (dT' (χ A) t x * dT' (dT' (χ A)) t x + c A * (dX' (χ A) t x * dT' (dX' (χ A)) t x)))
        + ∑ A, dV V (fieldAt χ t x) A * dT' (χ A) t x) t :=
    (hasDerivAt_kin_t Z c χ t x hr).add (hasDerivAt_potential_t V χ t x hV hr.t0)
  have hS : HasDerivAt (fun y => Sflux Z c χ t y)
      (-∑ A, Z A * c A * (dX' (dT' (χ A)) t x * dX' (χ A) t x + dT' (χ A) t x * dX' (dX' (χ A)) t x)) x := by
    have hsum : HasDerivAt (fun y => ∑ A, Z A * c A * dT' (χ A) t y * dX' (χ A) t y)
        (∑ A, Z A * c A * (dX' (dT' (χ A)) t x * dX' (χ A) t x + dT' (χ A) t x * dX' (dX' (χ A)) t x)) x := by
      refine HasDerivAt.fun_sum (fun A _ => ?_)
      have h := (((hr.xt A).hasDerivAt).mul ((hr.xx A).hasDerivAt)).const_mul (Z A * c A)
      convert h using 1
      · funext y; simp only [Pi.mul_apply]; ring
      · simp only [dX']
    exact hsum.neg
  rw [hH.deriv, hS.deriv]
  unfold ELres
  simp only [← Finset.sum_add_distrib, ← Finset.sum_neg_distrib]
  refine Finset.sum_congr rfl (fun A _ => ?_)
  rw [hr.mixed A]
  ring

/-- Momentum identity, off shell: `d_t P + d_x Pi = sum_A d_x chi_A E_A`. -/
theorem momentum_identity (Z c : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ) (t x : ℝ)
    (hV : DifferentiableAt ℝ V (fieldAt χ t x)) (hr : Regular χ t x) :
    deriv (fun s => Pden Z χ s x) t + deriv (fun y => Piflux Z c V χ t y) x
      = ∑ A, dX' (χ A) t x * ELres Z c V χ A t x := by
  have hP : HasDerivAt (fun s => Pden Z χ s x)
      (∑ A, Z A * (dT' (dT' (χ A)) t x * dX' (χ A) t x + dT' (χ A) t x * dT' (dX' (χ A)) t x)) t := by
    refine HasDerivAt.fun_sum (fun A _ => ?_)
    have h := (((hr.tt A).hasDerivAt).mul ((hr.tx A).hasDerivAt)).const_mul (Z A)
    convert h using 1
    · funext s; simp only [Pi.mul_apply]; ring
    · simp only [dT']
  have hPi : HasDerivAt (fun y => Piflux Z c V χ t y)
      (-(∑ A, Z A * (dT' (χ A) t x * dX' (dT' (χ A)) t x + c A * (dX' (χ A) t x * dX' (dX' (χ A)) t x)))
        + ∑ A, dV V (fieldAt χ t x) A * dX' (χ A) t x) x :=
    (hasDerivAt_kin_x Z c χ t x hr).neg.add (hasDerivAt_potential_x V χ t x hV hr.x0)
  rw [hP.deriv, hPi.deriv]
  unfold ELres
  simp only [← Finset.sum_add_distrib, ← Finset.sum_neg_distrib]
  refine Finset.sum_congr rfl (fun A _ => ?_)
  rw [hr.mixed A]
  ring

end UetFormal
