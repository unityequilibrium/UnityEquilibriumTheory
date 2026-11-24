/-
F9: time reparametrization and the energy constraint in a homogeneous (minisuperspace) universe
(claim C_NOETHER_COVERAGE, diffeomorphism part, homogeneous case only).

Setting: a lapse N(t) and n variables q_i(t) (for the parent action in a Bianchi I universe: the scale factors
a, b, c and the fields phi, chi1, chi2). The Lagrangian has the reparametrization-invariant form
    L = Q(q, qdot) / N - N U(q) + beta W(q),      Q = sum_ij G_ij(q) qdot_i qdot_j / 2,  G_ij = G_ji,
where beta W is a term not multiplied by N; it breaks time reparametrization unless beta = 0 (it is the negative
control of core/05_tests/physics/test_noether.py). G, U, W are any functions differentiable at the point.
Euler-Lagrange expressions:
    E_N = dL/dN = -Q/N^2 - U,
    E_k = dL/dq_k - d/dt (dL/dqdot_k),   dL/dqdot_k = sum_j G_kj qdot_j / N   (`mom`).

Theorems proved here (N(t) /= 0; q_i and qdot_i differentiable at t):
  * `reparam_identity`: N d/dt E_N = sum_k E_k qdot_k - beta sum_k dW/dq_k qdot_k, off shell.
  * `constraint_preserved`: with beta = 0 and all E_k = 0, d/dt E_N = 0, so the energy constraint E_N = 0,
    once imposed, is preserved by the other equations.
  * `constraint_broken`: with beta /= 0 and dW/dt /= 0 it is not preserved.
Scope: this is the homogeneous (Bianchi I type) case. Writing the parent action in this form needs an integration
by parts of the curvature term [AI derivation; the sympy test checks the action itself]. The full curved-metric
identity nabla^mu E_mu_nu = -kappa (E_phi d_nu phi + sum_A E_A d_nu chi_A) remains a numerical check.
Nearest known theory: Noether's second theorem; ADM Hamiltonian constraint. Not UET-distinct.
-/
import Mathlib
import UetFormal.EnergyMomentum

namespace UetFormal
namespace Mini

open Finset

variable {n : ℕ}

/-- The configuration point `(q_i t)_i`, velocities and accelerations. -/
def qAt (q : Fin n → ℝ → ℝ) (t : ℝ) : Fin n → ℝ := fun i => q i t
noncomputable def vel (q : Fin n → ℝ → ℝ) (i : Fin n) (t : ℝ) : ℝ := deriv (q i) t
noncomputable def acc (q : Fin n → ℝ → ℝ) (i : Fin n) (t : ℝ) : ℝ := deriv (vel q i) t

/-- Kinetic form `Q = sum_ij G_ij qdot_i qdot_j / 2`. -/
noncomputable def Qkin (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (q : Fin n → ℝ → ℝ) (t : ℝ) : ℝ :=
  ∑ i, ∑ j, G i j (qAt q t) * vel q i t * vel q j t / 2

/-- `E_N = dL/dN`. -/
noncomputable def EN (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (U : (Fin n → ℝ) → ℝ) (N : ℝ → ℝ)
    (q : Fin n → ℝ → ℝ) (t : ℝ) : ℝ :=
  -Qkin G q t / (N t * N t) - U (qAt q t)

/-- Canonical momentum `dL/dqdot_k`. -/
noncomputable def mom (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (N : ℝ → ℝ) (q : Fin n → ℝ → ℝ) (k : Fin n)
    (t : ℝ) : ℝ :=
  (∑ j, G k j (qAt q t) * vel q j t) / N t

/-- `E_k = dL/dq_k - d/dt dL/dqdot_k`. -/
noncomputable def Ek (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (U W : (Fin n → ℝ) → ℝ) (β : ℝ) (N : ℝ → ℝ)
    (q : Fin n → ℝ → ℝ) (k : Fin n) (t : ℝ) : ℝ :=
  (∑ i, ∑ j, dV (G i j) (qAt q t) k * vel q i t * vel q j t / 2) / N t
    - N t * dV U (qAt q t) k + β * dV W (qAt q t) k - deriv (mom G N q k) t

/-- Cubic and acceleration terms of `dQ/dt`. -/
noncomputable def Acub (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (q : Fin n → ℝ → ℝ) (t : ℝ) : ℝ :=
  ∑ i, ∑ j, ∑ l, dV (G i j) (qAt q t) l * vel q l t * vel q i t * vel q j t

noncomputable def Bacc (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (q : Fin n → ℝ → ℝ) (t : ℝ) : ℝ :=
  ∑ k, ∑ j, G k j (qAt q t) * acc q j t * vel q k t

/-- Chain rule along the path. -/
theorem hasDerivAt_along (F : (Fin n → ℝ) → ℝ) (q : Fin n → ℝ → ℝ) (t : ℝ)
    (hF : DifferentiableAt ℝ F (qAt q t)) (hq : ∀ i, DifferentiableAt ℝ (q i) t) :
    HasDerivAt (fun s => F (qAt q s)) (∑ l, dV F (qAt q t) l * vel q l t) t := by
  have hpath : HasDerivAt (fun s => qAt q s) (fun l => vel q l t) t := by
    rw [hasDerivAt_pi]
    intro l
    exact (hq l).hasDerivAt
  have h := hF.hasFDerivAt.comp_hasDerivAt t hpath
  rw [clm_apply_eq_sum] at h
  exact h

/-- Sum identities used below. -/
theorem quad_rate (D : Fin n → Fin n → Fin n → ℝ) (g : Fin n → Fin n → ℝ) (v a : Fin n → ℝ)
    (hsym : ∀ i j, g i j = g j i) :
    ∑ i, ∑ j, (((∑ l, D i j l * v l) * v i + g i j * a i) * v j + g i j * v i * a j) / 2
      = (∑ i, ∑ j, ∑ l, D i j l * v l * v i * v j) / 2 + ∑ k, ∑ j, g k j * a j * v k := by
  have e1 : ∀ i j, (((∑ l, D i j l * v l) * v i + g i j * a i) * v j + g i j * v i * a j) / 2
      = (∑ l, D i j l * v l) * v i * v j / 2 + (g i j * a i * v j / 2 + g i j * v i * a j / 2) := by
    intro i j; ring
  simp only [e1, Finset.sum_add_distrib]
  have e2 : ∑ i, ∑ j, (∑ l, D i j l * v l) * v i * v j / 2
      = (∑ i, ∑ j, ∑ l, D i j l * v l * v i * v j) / 2 := by
    simp only [Finset.sum_mul, Finset.sum_div]
  have e3 : ∑ i, ∑ j, g i j * a i * v j / 2 = (∑ k, ∑ j, g k j * a j * v k) / 2 := by
    rw [Finset.sum_div, Finset.sum_comm]
    refine Finset.sum_congr rfl (fun x _ => ?_)
    rw [Finset.sum_div]
    refine Finset.sum_congr rfl (fun y _ => ?_)
    rw [hsym y x]
  have e4 : ∑ i, ∑ j, g i j * v i * a j / 2 = (∑ k, ∑ j, g k j * a j * v k) / 2 := by
    rw [Finset.sum_div]
    refine Finset.sum_congr rfl (fun x _ => ?_)
    rw [Finset.sum_div]
    refine Finset.sum_congr rfl (fun y _ => ?_)
    ring
  rw [e2, e3, e4]; ring

theorem sum_P (D : Fin n → Fin n → Fin n → ℝ) (v : Fin n → ℝ) :
    ∑ k, (∑ i, ∑ j, D i j k * v i * v j / 2) * v k = (∑ i, ∑ j, ∑ l, D i j l * v l * v i * v j) / 2 := by
  simp only [Finset.sum_mul, Finset.sum_div]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun i _ => ?_)
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl (fun j _ => ?_)
  refine Finset.sum_congr rfl (fun l _ => ?_)
  ring

theorem sum_Sd (D : Fin n → Fin n → Fin n → ℝ) (g : Fin n → Fin n → ℝ) (v a : Fin n → ℝ) :
    ∑ k, (∑ j, ((∑ l, D k j l * v l) * v j + g k j * a j)) * v k
      = ∑ i, ∑ j, ∑ l, D i j l * v l * v i * v j + ∑ k, ∑ j, g k j * a j * v k := by
  simp only [Finset.sum_mul, add_mul, Finset.sum_add_distrib]
  congr 1
  refine Finset.sum_congr rfl (fun i _ => Finset.sum_congr rfl (fun j _ => Finset.sum_congr rfl (fun l _ => ?_)))
  ring

theorem sum_S (g : Fin n → Fin n → ℝ) (v : Fin n → ℝ) :
    ∑ k, (∑ j, g k j * v j) * v k = 2 * ∑ i, ∑ j, g i j * v i * v j / 2 := by
  simp only [Finset.sum_mul, Finset.mul_sum]
  refine Finset.sum_congr rfl (fun i _ => Finset.sum_congr rfl (fun j _ => ?_))
  ring

theorem split_sum (P u w Y Zs : Fin n → ℝ) (N Nd β : ℝ) :
    ∑ k, (P k / N - N * u k + β * w k - (Y k * N - Zs k * Nd) / N ^ 2)
      = (∑ k, P k) / N - N * ∑ k, u k + β * ∑ k, w k - ((∑ k, Y k) * N - (∑ k, Zs k) * Nd) / N ^ 2 := by
  simp only [sub_div, Finset.sum_sub_distrib, Finset.sum_add_distrib, Finset.sum_div, Finset.mul_sum,
    Finset.sum_mul]

theorem hasDerivAt_Qkin (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (q : Fin n → ℝ → ℝ) (t : ℝ)
    (hG : ∀ i j, DifferentiableAt ℝ (G i j) (qAt q t)) (hq : ∀ i, DifferentiableAt ℝ (q i) t)
    (hv : ∀ i, DifferentiableAt ℝ (vel q i) t) (hsym : ∀ i j, G i j = G j i) :
    HasDerivAt (fun s => Qkin G q s) (Acub G q t / 2 + Bacc G q t) t := by
  have h : HasDerivAt (fun s => Qkin G q s)
      (∑ i, ∑ j, (((∑ l, dV (G i j) (qAt q t) l * vel q l t) * vel q i t + G i j (qAt q t) * acc q i t)
          * vel q j t + G i j (qAt q t) * vel q i t * acc q j t) / 2) t := by
    refine HasDerivAt.fun_sum (fun i _ => ?_)
    refine HasDerivAt.fun_sum (fun j _ => ?_)
    exact (((hasDerivAt_along (G i j) q t (hG i j) hq).mul (hv i).hasDerivAt).mul (hv j).hasDerivAt).div_const 2
  have e := quad_rate (fun i j l => dV (G i j) (qAt q t) l) (fun i j => G i j (qAt q t))
    (fun i => vel q i t) (fun i => acc q i t) (fun i j => by simp only [hsym i j])
  beta_reduce at e
  rw [e] at h
  exact h

/-- The reparametrization identity, off shell. -/
theorem reparam_identity (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (U W : (Fin n → ℝ) → ℝ) (β : ℝ)
    (N : ℝ → ℝ) (q : Fin n → ℝ → ℝ) (t : ℝ)
    (hN : N t ≠ 0) (hNd : DifferentiableAt ℝ N t)
    (hG : ∀ i j, DifferentiableAt ℝ (G i j) (qAt q t)) (hU : DifferentiableAt ℝ U (qAt q t))
    (hq : ∀ i, DifferentiableAt ℝ (q i) t) (hv : ∀ i, DifferentiableAt ℝ (vel q i) t)
    (hsym : ∀ i j, G i j = G j i) :
    N t * deriv (fun s => EN G U N q s) t
      = ∑ k, Ek G U W β N q k t * vel q k t - β * ∑ k, dV W (qAt q t) k * vel q k t := by
  have hQ := hasDerivAt_Qkin G q t hG hq hv hsym
  have hNN : HasDerivAt (fun s => N s * N s) (deriv N t * N t + N t * deriv N t) t :=
    hNd.hasDerivAt.mul hNd.hasDerivAt
  have hEN := (hQ.neg.div hNN (mul_ne_zero hN hN)).sub (hasDerivAt_along U q t hU hq)
  have eEN : HasDerivAt (fun s => EN G U N q s) _ t := hEN
  have hmom : ∀ k, HasDerivAt (mom G N q k)
      (((∑ j, ((∑ l, dV (G k j) (qAt q t) l * vel q l t) * vel q j t + G k j (qAt q t) * acc q j t)) * N t
        - (∑ j, G k j (qAt q t) * vel q j t) * deriv N t) / N t ^ 2) t := by
    intro k
    have hS : HasDerivAt (fun s => ∑ j, G k j (qAt q s) * vel q j s)
        (∑ j, ((∑ l, dV (G k j) (qAt q t) l * vel q l t) * vel q j t + G k j (qAt q t) * acc q j t)) t :=
      HasDerivAt.fun_sum (fun j _ => (hasDerivAt_along (G k j) q t (hG k j) hq).mul (hv j).hasDerivAt)
    exact hS.div hNd.hasDerivAt hN
  have hk : ∀ k, Ek G U W β N q k t * vel q k t
      = (∑ i, ∑ j, dV (G i j) (qAt q t) k * vel q i t * vel q j t / 2) * vel q k t / N t
        - N t * (dV U (qAt q t) k * vel q k t) + β * (dV W (qAt q t) k * vel q k t)
        - ((∑ j, ((∑ l, dV (G k j) (qAt q t) l * vel q l t) * vel q j t + G k j (qAt q t) * acc q j t))
              * vel q k t * N t
            - (∑ j, G k j (qAt q t) * vel q j t) * vel q k t * deriv N t) / N t ^ 2 := by
    intro k
    unfold Ek
    rw [(hmom k).deriv]
    ring
  rw [eEN.deriv, Finset.sum_congr rfl (fun k _ => hk k), split_sum]
  have e1 := sum_P (fun i j k => dV (G i j) (qAt q t) k) (fun i => vel q i t)
  have e2 := sum_Sd (fun i j l => dV (G i j) (qAt q t) l) (fun i j => G i j (qAt q t))
    (fun i => vel q i t) (fun i => acc q i t)
  have e3 := sum_S (fun i j => G i j (qAt q t)) (fun i => vel q i t)
  beta_reduce at e1 e2 e3
  rw [e1, e2, e3]
  simp only [Pi.neg_apply]
  unfold Acub Bacc Qkin
  field_simp
  ring

/-- With `beta = 0`, on shell (`E_k = 0`) the energy constraint `E_N` does not change. -/
theorem constraint_preserved (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (U W : (Fin n → ℝ) → ℝ)
    (N : ℝ → ℝ) (q : Fin n → ℝ → ℝ) (t : ℝ)
    (hN : N t ≠ 0) (hNd : DifferentiableAt ℝ N t)
    (hG : ∀ i j, DifferentiableAt ℝ (G i j) (qAt q t)) (hU : DifferentiableAt ℝ U (qAt q t))
    (hq : ∀ i, DifferentiableAt ℝ (q i) t) (hv : ∀ i, DifferentiableAt ℝ (vel q i) t)
    (hsym : ∀ i j, G i j = G j i) (hshell : ∀ k, Ek G U W 0 N q k t = 0) :
    deriv (fun s => EN G U N q s) t = 0 := by
  have h := reparam_identity G U W 0 N q t hN hNd hG hU hq hv hsym
  simp only [hshell, zero_mul, Finset.sum_const_zero, sub_zero] at h
  exact (mul_eq_zero.mp h).resolve_left hN

/-- With `beta /= 0`, on shell the constraint changes at `-beta dW/dt / N`, so it is not preserved
wherever `dW/dt /= 0`. -/
theorem constraint_broken (G : Fin n → Fin n → (Fin n → ℝ) → ℝ) (U W : (Fin n → ℝ) → ℝ) (β : ℝ)
    (N : ℝ → ℝ) (q : Fin n → ℝ → ℝ) (t : ℝ)
    (hN : N t ≠ 0) (hNd : DifferentiableAt ℝ N t)
    (hG : ∀ i j, DifferentiableAt ℝ (G i j) (qAt q t)) (hU : DifferentiableAt ℝ U (qAt q t))
    (hq : ∀ i, DifferentiableAt ℝ (q i) t) (hv : ∀ i, DifferentiableAt ℝ (vel q i) t)
    (hsym : ∀ i j, G i j = G j i) (hshell : ∀ k, Ek G U W β N q k t = 0)
    (hβ : β ≠ 0) (hW : ∑ k, dV W (qAt q t) k * vel q k t ≠ 0) :
    deriv (fun s => EN G U N q s) t ≠ 0 := by
  have h := reparam_identity G U W β N q t hN hNd hG hU hq hv hsym
  simp only [hshell, zero_mul, Finset.sum_const_zero, zero_sub] at h
  intro h0
  rw [h0, mul_zero] at h
  exact mul_ne_zero hβ hW (neg_eq_zero.mp h.symm)

end Mini
end UetFormal
