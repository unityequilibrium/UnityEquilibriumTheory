/-
F8: the rotation (angular momentum) charge of the parent action in flat 2+1 dimensions
(claim C_NOETHER_COVERAGE, rotation part).

Setting: n real fields chi_A(t, x, y), each with kinetic coefficient Z_A and squared speeds a_A along x and
b_A along y (a spatially isotropic field has a_A = b_A = c_A), and one potential V of all fields:
    L = sum_A Z_A/2 (d_t chi_A^2 - a_A d_x chi_A^2 - b_A d_y chi_A^2) - V(chi).
Euler-Lagrange residuals:  E_A = Z_A (d_t^2 chi_A - a_A d_x^2 chi_A - b_A d_y^2 chi_A) + dV/dchi_A.
Momentum densities (sign as in `EnergyMomentum`): Px = sum Z d_t chi d_x chi, Py = sum Z d_t chi d_y chi.
Their fluxes (Pab = flux of Pa in direction b):
    Pxx = sum Z/2 (b d_y chi^2 - d_t chi^2 - a d_x chi^2) + V,   Pxy = -sum Z b d_x chi d_y chi,
    Pyy = sum Z/2 (a d_x chi^2 - d_t chi^2 - b d_y chi^2) + V,   Pyx = -sum Z a d_x chi d_y chi.
Rotation charge density and fluxes:  J^t = x Py - y Px,  J^x = x Pyx - y Pxx,  J^y = x Pyy - y Pxy.

Theorems proved here (fields with the slice derivatives named in `Regular` and equal mixed partials):
  * `rotation_identity`: d_t J^t + d_x J^x + d_y J^y = x sum_A d_y chi_A E_A - y sum_A d_x chi_A E_A
        + sum_A Z_A (b_A - a_A) d_x chi_A d_y chi_A,  at every point, on or off shell.
  * `rotation_conserved_isotropic`: if every field is isotropic (a_A = b_A), the rotation charge is
    conserved on shell, whatever the speeds of the different fields.
  * `rotation_fails_anisotropic`: one field with a /= b breaks it wherever Z d_x chi d_y chi /= 0.
Contrast with F7 (`Boost`): the boost charge needs all fields to share one speed; rotation needs only
that each field is isotropic in space.
-/
import Mathlib
import UetFormal.EnergyMomentum

namespace UetFormal
namespace Plane

open Finset

variable {n : ℕ}

/-- Partial derivatives of a field `φ t x y` along t, x and y. -/
noncomputable def d0 (φ : ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ := deriv (fun s => φ s x y) t
noncomputable def d1 (φ : ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ := deriv (fun u => φ t u y) x
noncomputable def d2 (φ : ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ := deriv (fun v => φ t x v) y

/-- The field point `(chi_A t x y)_A`. -/
def pt (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : Fin n → ℝ := fun A => χ A t x y

/-- Euler-Lagrange residual of field `A`. -/
noncomputable def ELres (Z a b : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (A : Fin n)
    (t x y : ℝ) : ℝ :=
  Z A * (d0 (d0 (χ A)) t x y - a A * d1 (d1 (χ A)) t x y - b A * d2 (d2 (χ A)) t x y)
    + dV V (pt χ t x y) A

noncomputable def Px (Z : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ :=
  ∑ A, Z A * d0 (χ A) t x y * d1 (χ A) t x y

noncomputable def Py (Z : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ :=
  ∑ A, Z A * d0 (χ A) t x y * d2 (χ A) t x y

noncomputable def Pxx (Z a b : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ :=
  ∑ A, Z A * b A / 2 * d2 (χ A) t x y * d2 (χ A) t x y
    - ∑ A, Z A / 2 * d0 (χ A) t x y * d0 (χ A) t x y
    - ∑ A, Z A * a A / 2 * d1 (χ A) t x y * d1 (χ A) t x y
    + V (pt χ t x y)

noncomputable def Pyy (Z a b : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ :=
  ∑ A, Z A * a A / 2 * d1 (χ A) t x y * d1 (χ A) t x y
    - ∑ A, Z A / 2 * d0 (χ A) t x y * d0 (χ A) t x y
    - ∑ A, Z A * b A / 2 * d2 (χ A) t x y * d2 (χ A) t x y
    + V (pt χ t x y)

noncomputable def Pxy (Z b : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ :=
  -∑ A, Z A * b A * d1 (χ A) t x y * d2 (χ A) t x y

noncomputable def Pyx (Z a : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ :=
  -∑ A, Z A * a A * d1 (χ A) t x y * d2 (χ A) t x y

/-- Rotation charge density and fluxes. -/
noncomputable def Jt (Z : Fin n → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ :=
  x * Py Z χ t x y - y * Px Z χ t x y

noncomputable def Jx (Z a b : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ :=
  x * Pyx Z a χ t x y - y * Pxx Z a b V χ t x y

noncomputable def Jy (Z a b : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : ℝ :=
  x * Pyy Z a b V χ t x y - y * Pxy Z b χ t x y

/-- Smoothness assumed at `(t, x, y)`: the slice derivatives used below exist and mixed partials agree. -/
structure Regular (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) : Prop where
  x0 : ∀ A, DifferentiableAt ℝ (fun u => χ A t u y) x
  y0 : ∀ A, DifferentiableAt ℝ (fun v => χ A t x v) y
  t0 : ∀ A, DifferentiableAt ℝ (fun s => d0 (χ A) s x y) t
  t1 : ∀ A, DifferentiableAt ℝ (fun s => d1 (χ A) s x y) t
  t2 : ∀ A, DifferentiableAt ℝ (fun s => d2 (χ A) s x y) t
  x0' : ∀ A, DifferentiableAt ℝ (fun u => d0 (χ A) t u y) x
  x1 : ∀ A, DifferentiableAt ℝ (fun u => d1 (χ A) t u y) x
  x2 : ∀ A, DifferentiableAt ℝ (fun u => d2 (χ A) t u y) x
  y0' : ∀ A, DifferentiableAt ℝ (fun v => d0 (χ A) t x v) y
  y1 : ∀ A, DifferentiableAt ℝ (fun v => d1 (χ A) t x v) y
  y2 : ∀ A, DifferentiableAt ℝ (fun v => d2 (χ A) t x v) y
  m01 : ∀ A, d1 (d0 (χ A)) t x y = d0 (d1 (χ A)) t x y
  m02 : ∀ A, d2 (d0 (χ A)) t x y = d0 (d2 (χ A)) t x y
  m12 : ∀ A, d2 (d1 (χ A)) t x y = d1 (d2 (χ A)) t x y

/-- Product rule for a weighted sum of products. -/
theorem hasDerivAt_sum_mul (k : Fin n → ℝ) (f g : Fin n → ℝ → ℝ) (f' g' : Fin n → ℝ) (z : ℝ)
    (hf : ∀ A, HasDerivAt (f A) (f' A) z) (hg : ∀ A, HasDerivAt (g A) (g' A) z) :
    HasDerivAt (fun w => ∑ A, k A * f A w * g A w) (∑ A, k A * (f' A * g A z + f A z * g' A)) z := by
  refine HasDerivAt.fun_sum (fun A _ => ?_)
  have h := ((hf A).mul (hg A)).const_mul (k A)
  convert h using 1
  funext w
  simp only [Pi.mul_apply]
  ring

theorem hasDerivAt_potential_x (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ)
    (hV : DifferentiableAt ℝ V (pt χ t x y)) (hx : ∀ A, DifferentiableAt ℝ (fun u => χ A t u y) x) :
    HasDerivAt (fun u => V (pt χ t u y)) (∑ A, dV V (pt χ t x y) A * d1 (χ A) t x y) x := by
  have hpath : HasDerivAt (fun u => pt χ t u y) (fun A => d1 (χ A) t x y) x := by
    rw [hasDerivAt_pi]
    intro A
    exact (hx A).hasDerivAt
  have h := hV.hasFDerivAt.comp_hasDerivAt x hpath
  rw [clm_apply_eq_sum] at h
  exact h

theorem hasDerivAt_potential_y (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ)
    (hV : DifferentiableAt ℝ V (pt χ t x y)) (hy : ∀ A, DifferentiableAt ℝ (fun v => χ A t x v) y) :
    HasDerivAt (fun v => V (pt χ t x v)) (∑ A, dV V (pt χ t x y) A * d2 (χ A) t x y) y := by
  have hpath : HasDerivAt (fun v => pt χ t x v) (fun A => d2 (χ A) t x y) y := by
    rw [hasDerivAt_pi]
    intro A
    exact (hy A).hasDerivAt
  have h := hV.hasFDerivAt.comp_hasDerivAt y hpath
  rw [clm_apply_eq_sum] at h
  exact h

/-- The rotation identity, off shell, for any speeds. -/
theorem rotation_identity (Z a b : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ) (χ : Fin n → ℝ → ℝ → ℝ → ℝ)
    (t x y : ℝ) (hV : DifferentiableAt ℝ V (pt χ t x y)) (hr : Regular χ t x y) :
    deriv (fun s => Jt Z χ s x y) t + deriv (fun u => Jx Z a b V χ t u y) x
        + deriv (fun v => Jy Z a b V χ t x v) y
      = x * ∑ A, d2 (χ A) t x y * ELres Z a b V χ A t x y
        - y * ∑ A, d1 (χ A) t x y * ELres Z a b V χ A t x y
        + ∑ A, Z A * (b A - a A) * d1 (χ A) t x y * d2 (χ A) t x y := by
  -- time derivatives of the momentum densities
  have hPy := hasDerivAt_sum_mul Z (fun A s => d0 (χ A) s x y) (fun A s => d2 (χ A) s x y)
    (fun A => d0 (d0 (χ A)) t x y) (fun A => d0 (d2 (χ A)) t x y) t
    (fun A => (hr.t0 A).hasDerivAt) (fun A => (hr.t2 A).hasDerivAt)
  have hPx := hasDerivAt_sum_mul Z (fun A s => d0 (χ A) s x y) (fun A s => d1 (χ A) s x y)
    (fun A => d0 (d0 (χ A)) t x y) (fun A => d0 (d1 (χ A)) t x y) t
    (fun A => (hr.t0 A).hasDerivAt) (fun A => (hr.t1 A).hasDerivAt)
  have hJt := (hPy.const_mul x).sub (hPx.const_mul y)
  -- x derivatives
  have hx22 := hasDerivAt_sum_mul (fun A => Z A * b A / 2) (fun A u => d2 (χ A) t u y)
    (fun A u => d2 (χ A) t u y) (fun A => d1 (d2 (χ A)) t x y) (fun A => d1 (d2 (χ A)) t x y) x
    (fun A => (hr.x2 A).hasDerivAt) (fun A => (hr.x2 A).hasDerivAt)
  have hx00 := hasDerivAt_sum_mul (fun A => Z A / 2) (fun A u => d0 (χ A) t u y)
    (fun A u => d0 (χ A) t u y) (fun A => d1 (d0 (χ A)) t x y) (fun A => d1 (d0 (χ A)) t x y) x
    (fun A => (hr.x0' A).hasDerivAt) (fun A => (hr.x0' A).hasDerivAt)
  have hx11 := hasDerivAt_sum_mul (fun A => Z A * a A / 2) (fun A u => d1 (χ A) t u y)
    (fun A u => d1 (χ A) t u y) (fun A => d1 (d1 (χ A)) t x y) (fun A => d1 (d1 (χ A)) t x y) x
    (fun A => (hr.x1 A).hasDerivAt) (fun A => (hr.x1 A).hasDerivAt)
  have hxV := hasDerivAt_potential_x V χ t x y hV hr.x0
  have hPxx := ((hx22.sub hx00).sub hx11).add hxV
  have hx12 := hasDerivAt_sum_mul (fun A => Z A * a A) (fun A u => d1 (χ A) t u y)
    (fun A u => d2 (χ A) t u y) (fun A => d1 (d1 (χ A)) t x y) (fun A => d1 (d2 (χ A)) t x y) x
    (fun A => (hr.x1 A).hasDerivAt) (fun A => (hr.x2 A).hasDerivAt)
  have hJx := ((hasDerivAt_id x).mul hx12.neg).sub (hPxx.const_mul y)
  -- y derivatives
  have hy11 := hasDerivAt_sum_mul (fun A => Z A * a A / 2) (fun A v => d1 (χ A) t x v)
    (fun A v => d1 (χ A) t x v) (fun A => d2 (d1 (χ A)) t x y) (fun A => d2 (d1 (χ A)) t x y) y
    (fun A => (hr.y1 A).hasDerivAt) (fun A => (hr.y1 A).hasDerivAt)
  have hy00 := hasDerivAt_sum_mul (fun A => Z A / 2) (fun A v => d0 (χ A) t x v)
    (fun A v => d0 (χ A) t x v) (fun A => d2 (d0 (χ A)) t x y) (fun A => d2 (d0 (χ A)) t x y) y
    (fun A => (hr.y0' A).hasDerivAt) (fun A => (hr.y0' A).hasDerivAt)
  have hy22 := hasDerivAt_sum_mul (fun A => Z A * b A / 2) (fun A v => d2 (χ A) t x v)
    (fun A v => d2 (χ A) t x v) (fun A => d2 (d2 (χ A)) t x y) (fun A => d2 (d2 (χ A)) t x y) y
    (fun A => (hr.y2 A).hasDerivAt) (fun A => (hr.y2 A).hasDerivAt)
  have hyV := hasDerivAt_potential_y V χ t x y hV hr.y0
  have hPyy := ((hy11.sub hy00).sub hy22).add hyV
  have hy12 := hasDerivAt_sum_mul (fun A => Z A * b A) (fun A v => d1 (χ A) t x v)
    (fun A v => d2 (χ A) t x v) (fun A => d2 (d1 (χ A)) t x y) (fun A => d2 (d2 (χ A)) t x y) y
    (fun A => (hr.y1 A).hasDerivAt) (fun A => (hr.y2 A).hasDerivAt)
  have hJy := (hPyy.const_mul x).sub ((hasDerivAt_id y).mul hy12.neg)
  have eT : HasDerivAt (fun s => Jt Z χ s x y) _ t := hJt
  have eX : HasDerivAt (fun u => Jx Z a b V χ t u y) _ x := hJx
  have eY : HasDerivAt (fun v => Jy Z a b V χ t x v) _ y := hJy
  rw [eT.deriv, eX.deriv, eY.deriv]
  simp only [id, one_mul, Pi.neg_apply, Finset.mul_sum, ← Finset.sum_neg_distrib, ← Finset.sum_add_distrib,
    ← Finset.sum_sub_distrib]
  refine Finset.sum_congr rfl (fun A _ => ?_)
  unfold ELres
  rw [hr.m01 A, hr.m02 A, hr.m12 A]
  ring

/-- Every field isotropic in space (`a A = b A`): the rotation charge is conserved on shell, for any speeds. -/
theorem rotation_conserved_isotropic (Z a b : Fin n → ℝ) (V : (Fin n → ℝ) → ℝ)
    (χ : Fin n → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) (hV : DifferentiableAt ℝ V (pt χ t x y))
    (hr : Regular χ t x y) (hab : ∀ A, a A = b A) (hshell : ∀ A, ELres Z a b V χ A t x y = 0) :
    deriv (fun s => Jt Z χ s x y) t + deriv (fun u => Jx Z a b V χ t u y) x
        + deriv (fun v => Jy Z a b V χ t x v) y = 0 := by
  rw [rotation_identity Z a b V χ t x y hV hr]
  simp [hshell, hab]

/-- One field with different speeds along x and y: on shell the rotation charge changes at
`Z (b - a) d_x chi d_y chi`, so it is not conserved wherever that product is nonzero. -/
theorem rotation_fails_anisotropic (Z a b : Fin 1 → ℝ) (V : (Fin 1 → ℝ) → ℝ)
    (χ : Fin 1 → ℝ → ℝ → ℝ → ℝ) (t x y : ℝ) (hV : DifferentiableAt ℝ V (pt χ t x y))
    (hr : Regular χ t x y) (hshell : ∀ A, ELres Z a b V χ A t x y = 0)
    (hZ : Z 0 ≠ 0) (hne : b 0 ≠ a 0) (hx : d1 (χ 0) t x y ≠ 0) (hy : d2 (χ 0) t x y ≠ 0) :
    deriv (fun s => Jt Z χ s x y) t + deriv (fun u => Jx Z a b V χ t u y) x
        + deriv (fun v => Jy Z a b V χ t x v) y ≠ 0 := by
  rw [rotation_identity Z a b V χ t x y hV hr]
  simp only [hshell, mul_zero, Finset.sum_const_zero, sub_zero, zero_add, Fin.sum_univ_one]
  exact mul_ne_zero (mul_ne_zero (mul_ne_zero hZ (sub_ne_zero.mpr hne)) hx) hy

end Plane
end UetFormal
