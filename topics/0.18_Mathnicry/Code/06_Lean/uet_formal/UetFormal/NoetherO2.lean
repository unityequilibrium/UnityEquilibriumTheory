/-
F4: the O(2) charge identity of the parent action, off shell (claim C_NOETHER_COVERAGE, O(2) part).

Matter sector in flat 1+1 dimensions (core/03_lanes/symmetry/uet_noether.py), fields chi1, chi2:
    L = -Z/2 (d chi_A)^2 - V(chi1, chi2),   V = U(chi1^2 + chi2^2),
where U collects the matter potential W(|chi|^2) and the portal term -1/2 eps h delta |chi|^2 (both depend
on chi only through |chi|^2, which is the O(2) symmetry). The Euler-Lagrange expressions are
    E_A = Z (d_t^2 chi_A - d_x^2 chi_A) - dV/dchi_A,
and the Noether current of the O(2) rotation is
    N^t = chi1 d_t chi2 - chi2 d_t chi1,   N^x = -(chi1 d_x chi2 - chi2 d_x chi1).

Theorems proved here:
  * `deriv_wronskian`: d/ds (f g' - g f') = f g'' - g f''.
  * `o2_potential_torque`: chi1 dV/dchi2 - chi2 dV/dchi1 = 0 for any differentiable U (the potential exerts
    no O(2) torque; this includes the portal).
  * `o2_charge_identity`: Z (d_t N^t + d_x N^x) = chi1 E2 - chi2 E1 at every point, on or off shell.
    On shell (E1 = E2 = 0) the charge is conserved; the identity also says how much it changes when the
    field equations are not satisfied, which is what the numerical tests checked at 20 random points.
-/
import Mathlib

namespace UetFormal

/-- `d/ds (f g' - g f') = f g'' - g f''`, as a derivative statement. -/
theorem hasDerivAt_wronskian (f g : ℝ → ℝ) (s : ℝ) (hf : Differentiable ℝ f) (hg : Differentiable ℝ g)
    (hf' : Differentiable ℝ (deriv f)) (hg' : Differentiable ℝ (deriv g)) :
    HasDerivAt (fun t => f t * deriv g t - g t * deriv f t)
      (f s * deriv (deriv g) s - g s * deriv (deriv f) s) s := by
  have h := ((hf s).hasDerivAt.mul (hg' s).hasDerivAt).sub ((hg s).hasDerivAt.mul (hf' s).hasDerivAt)
  convert h using 1
  ring

/-- `d/ds (f g' - g f') = f g'' - g f''`. -/
theorem deriv_wronskian (f g : ℝ → ℝ) (s : ℝ) (hf : Differentiable ℝ f) (hg : Differentiable ℝ g)
    (hf' : Differentiable ℝ (deriv f)) (hg' : Differentiable ℝ (deriv g)) :
    deriv (fun t => f t * deriv g t - g t * deriv f t) s
      = f s * deriv (deriv g) s - g s * deriv (deriv f) s :=
  (hasDerivAt_wronskian f g s hf hg hf' hg').deriv

/-- The O(2)-invariant potential exerts no torque: `c1 ∂V/∂c2 - c2 ∂V/∂c1 = 0` for `V = U (c1^2 + c2^2)`. -/
theorem o2_potential_torque (U : ℝ → ℝ) (hU : Differentiable ℝ U) (c1 c2 : ℝ) :
    c1 * deriv (fun c => U (c1 ^ 2 + c ^ 2)) c2 - c2 * deriv (fun c => U (c ^ 2 + c2 ^ 2)) c1 = 0 := by
  have e2 : deriv (fun c => U (c1 ^ 2 + c ^ 2)) c2 = deriv U (c1 ^ 2 + c2 ^ 2) * (2 * c2) := by
    have h : HasDerivAt (fun c => c1 ^ 2 + c ^ 2) (2 * c2) c2 := by
      simpa using ((hasDerivAt_pow 2 c2).const_add (c1 ^ 2))
    exact ((hU _).hasDerivAt.comp c2 h).deriv
  have e1 : deriv (fun c => U (c ^ 2 + c2 ^ 2)) c1 = deriv U (c1 ^ 2 + c2 ^ 2) * (2 * c1) := by
    have h : HasDerivAt (fun c => c ^ 2 + c2 ^ 2) (2 * c1) c1 := by
      simpa using ((hasDerivAt_pow 2 c1).add_const (c2 ^ 2))
    exact ((hU _).hasDerivAt.comp c1 h).deriv
  rw [e1, e2]
  ring

/-- Time and space slices of a field `φ t x`. -/
noncomputable def dT (φ : ℝ → ℝ → ℝ) (t x : ℝ) : ℝ := deriv (fun s => φ s x) t
noncomputable def dX (φ : ℝ → ℝ → ℝ) (t x : ℝ) : ℝ := deriv (fun y => φ t y) x

/-- O(2) Noether current. -/
noncomputable def Nt (χ1 χ2 : ℝ → ℝ → ℝ) (t x : ℝ) : ℝ := χ1 t x * dT χ2 t x - χ2 t x * dT χ1 t x
noncomputable def Nx (χ1 χ2 : ℝ → ℝ → ℝ) (t x : ℝ) : ℝ := -(χ1 t x * dX χ2 t x - χ2 t x * dX χ1 t x)

/-- Euler-Lagrange expression of component `A`, with `dV` the partial derivative of the potential. -/
noncomputable def EL (Z : ℝ) (χ : ℝ → ℝ → ℝ) (dV : ℝ) (t x : ℝ) : ℝ :=
  Z * (dT (dT χ) t x - dX (dX χ) t x) - dV

/-- The O(2) charge identity, off shell: `Z (∂_t N^t + ∂_x N^x) = χ1 E2 - χ2 E1`. -/
theorem o2_charge_identity (Z : ℝ) (U : ℝ → ℝ) (hU : Differentiable ℝ U)
    (χ1 χ2 : ℝ → ℝ → ℝ) (t x : ℝ)
    (h1t : Differentiable ℝ (fun s => χ1 s x)) (h2t : Differentiable ℝ (fun s => χ2 s x))
    (h1t' : Differentiable ℝ (deriv (fun s => χ1 s x))) (h2t' : Differentiable ℝ (deriv (fun s => χ2 s x)))
    (h1x : Differentiable ℝ (fun y => χ1 t y)) (h2x : Differentiable ℝ (fun y => χ2 t y))
    (h1x' : Differentiable ℝ (deriv (fun y => χ1 t y))) (h2x' : Differentiable ℝ (deriv (fun y => χ2 t y))) :
    Z * (deriv (fun s => Nt χ1 χ2 s x) t + deriv (fun y => Nx χ1 χ2 t y) x)
      = χ1 t x * EL Z χ2 (deriv (fun c => U ((χ1 t x) ^ 2 + c ^ 2)) (χ2 t x)) t x
        - χ2 t x * EL Z χ1 (deriv (fun c => U (c ^ 2 + (χ2 t x) ^ 2)) (χ1 t x)) t x := by
  have ht : deriv (fun s => Nt χ1 χ2 s x) t
      = χ1 t x * deriv (deriv (fun s => χ2 s x)) t - χ2 t x * deriv (deriv (fun s => χ1 s x)) t :=
    deriv_wronskian (fun s => χ1 s x) (fun s => χ2 s x) t h1t h2t h1t' h2t'
  have hx : deriv (fun y => Nx χ1 χ2 t y) x
      = -(χ1 t x * deriv (deriv (fun y => χ2 t y)) x - χ2 t x * deriv (deriv (fun y => χ1 t y)) x) :=
    (hasDerivAt_wronskian (fun y => χ1 t y) (fun y => χ2 t y) x h1x h2x h1x' h2x').neg.deriv
  have htor := o2_potential_torque U hU (χ1 t x) (χ2 t x)
  have dTT1 : dT (dT χ1) t x = deriv (deriv (fun s => χ1 s x)) t := rfl
  have dTT2 : dT (dT χ2) t x = deriv (deriv (fun s => χ2 s x)) t := rfl
  have dXX1 : dX (dX χ1) t x = deriv (deriv (fun y => χ1 t y)) x := rfl
  have dXX2 : dX (dX χ2) t x = deriv (deriv (fun y => χ2 t y)) x := rfl
  rw [ht, hx]
  unfold EL
  rw [dTT1, dTT2, dXX1, dXX2]
  linear_combination htor

end UetFormal
