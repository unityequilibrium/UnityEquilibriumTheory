/-
F5: layer-3 selection on one resource, the lowest R* wins (claim C_L3_SELECTION_FORMAL).

Model (linear uptake, core/03_lanes/persistence/uet_layer3_from_action.py):
    dn_i/dt = (a_i R - d_i) n_i,        dR/dt = S - delta R - R sum_i a_i F_i n_i,
with cost R*_i = d_i / a_i.

Theorems proved here:
  * `resident_steady`: type j alone has the steady state R = R*_j, n_j = (S - delta R*_j)/(a_j F_j R*_j)
    (both right-hand sides vanish), and n_j > 0 exactly when S > delta R*_j.
  * `resident_stable`: at that state the Jacobian of (n_j, R) has negative trace and positive determinant,
    so the resident state is locally stable.
  * `invasion_iff`: a rare type i grows in type j's state exactly when R*_i < R*_j.
  * `lowest_rstar_wins`: if type k has the strictly lowest cost, then k invades every other resident and no
    other type invades k.
  * `no_coexistence`: two types with different costs cannot both be at rest with positive densities at the
    same resource level.
-/
import Mathlib

namespace UetFormal

/-- Cost of a type. -/
noncomputable def rstar (a d : ℝ) : ℝ := d / a

/-- Resident density at its steady state. -/
noncomputable def residentDensity (a d F S delta : ℝ) : ℝ :=
  (S - delta * rstar a d) / (a * F * rstar a d)

theorem resident_steady (a d F S delta : ℝ) (ha : 0 < a) (hd : 0 < d) (hF : 0 < F) :
    (a * rstar a d - d) * residentDensity a d F S delta = 0 ∧
    S - delta * rstar a d - rstar a d * (a * F * residentDensity a d F S delta) = 0 := by
  have hr : 0 < rstar a d := div_pos hd ha
  have hgrow : a * rstar a d - d = 0 := by unfold rstar; field_simp; ring
  refine ⟨by rw [hgrow, zero_mul], ?_⟩
  unfold residentDensity
  have : a * F * rstar a d ≠ 0 := by positivity
  field_simp
  ring

theorem resident_positive_iff (a d F S delta : ℝ) (ha : 0 < a) (hd : 0 < d) (hF : 0 < F) :
    0 < residentDensity a d F S delta ↔ delta * rstar a d < S := by
  have hr : 0 < rstar a d := div_pos hd ha
  have hden : 0 < a * F * rstar a d := by positivity
  unfold residentDensity
  rw [div_pos_iff_of_pos_right hden, sub_pos]

/-- Local stability of the resident state: trace < 0 and determinant > 0 of the (n, R) Jacobian
`[[a R* - d, a n], [-a F R*, -delta - a F n]]` with `a R* - d = 0`. -/
theorem resident_stable (a d F delta n : ℝ) (ha : 0 < a) (hd : 0 < d) (hF : 0 < F) (hdelta : 0 ≤ delta)
    (hn : 0 < n) :
    let J11 := a * rstar a d - d
    let J12 := a * n
    let J21 := -(a * F * rstar a d)
    let J22 := -delta - a * F * n
    J11 + J22 < 0 ∧ 0 < J11 * J22 - J12 * J21 := by
  intro J11 J12 J21 J22
  have hr : 0 < rstar a d := div_pos hd ha
  have h11 : J11 = 0 := by
    show a * rstar a d - d = 0
    unfold rstar; field_simp; ring
  have hpos : 0 < a * F * n := by positivity
  constructor
  · show J11 + J22 < 0
    rw [h11]; show 0 + (-delta - a * F * n) < 0; linarith
  · rw [h11]
    show 0 < 0 * (-delta - a * F * n) - a * n * -(a * F * rstar a d)
    have : 0 < a * n * (a * F * rstar a d) := by positivity
    linarith

/-- A rare type `i` grows in type `j`'s steady state exactly when its cost is lower. -/
theorem invasion_iff (ai di aj dj : ℝ) (hai : 0 < ai) :
    0 < ai * rstar aj dj - di ↔ rstar ai di < rstar aj dj := by
  unfold rstar
  rw [sub_pos, div_lt_iff₀ hai]
  constructor <;> intro h <;> linarith [mul_comm ai (dj / aj)]

/-- The strictly cheapest type wins: it invades every other resident, and no other type invades it. -/
theorem lowest_rstar_wins {ι : Type*} (a d : ι → ℝ) (ha : ∀ i, 0 < a i) (hd : ∀ i, 0 < d i) (k : ι)
    (hk : ∀ j, j ≠ k → rstar (a k) (d k) < rstar (a j) (d j)) :
    ∀ j, j ≠ k → 0 < a k * rstar (a j) (d j) - d k ∧ ¬ 0 < a j * rstar (a k) (d k) - d j := by
  intro j hj
  have hlt := hk j hj
  refine ⟨(invasion_iff (a k) (d k) (a j) (d j) (ha k)).mpr hlt, ?_⟩
  rw [invasion_iff (a j) (d j) (a k) (d k) (ha j)]
  exact not_lt.mpr hlt.le

/-- Two types with different costs cannot both be at rest with positive densities at the same `R`. -/
theorem no_coexistence (ai di aj dj R ni nj : ℝ) (hai : 0 < ai) (haj : 0 < aj)
    (hni : 0 < ni) (hnj : 0 < nj) (hne : rstar ai di ≠ rstar aj dj)
    (hi : (ai * R - di) * ni = 0) (hj : (aj * R - dj) * nj = 0) : False := by
  have hRi : R = rstar ai di := by
    have : ai * R - di = 0 := by
      rcases mul_eq_zero.mp hi with h | h
      · exact h
      · exact absurd h hni.ne'
    unfold rstar; field_simp; linarith
  have hRj : R = rstar aj dj := by
    have : aj * R - dj = 0 := by
      rcases mul_eq_zero.mp hj with h | h
      · exact h
      · exact absurd h hnj.ne'
    unfold rstar; field_simp; linarith
  exact hne (hRi ▸ hRj)

end UetFormal
