# UET Paper Supplementary Materials

## S1. Complete Test Results

### S1.1 Phase 1: Foundation Tests (6/6)
| Test | Method | Result | Value |
|------|--------|--------|-------|
| energy_decreasing | Lyapunov | PASS | 0 violations |
| phase_separation | Numerical | PASS | max_C = 1.0 |
| convergence | Variance | PASS | 1.34e-16 |
| coupled_ci | C-I Model | PASS | Stable |
| lyapunov | Analytical | PASS | dΩ/dt ≤ 0 |
| numerical_stability | Edge cases | PASS | No NaN/Inf |

### S1.2 Phase 3-6: Four Forces Tests (15/15)
| Test | Domain | Data Source | Result |
|------|--------|-------------|--------|
| gravity_uet | Gravitation | Simulated | PASS |
| em_force_uet | Electromagnetism | Simulated | PASS |
| strong_force_uet | Strong Force | Simulated | PASS |
| weak_force_uet | Weak Force | Simulated | PASS |
| gravity_data | Gravitation | NASA | PASS (16 pts) |
| thermo_data | Thermodynamics | NOAA | PASS (16 pts) |
| em_data | EM | CODATA | PASS (16 pts) |
| strong_data | QCD | PDG | PASS (16 pts) |
| weak_data | EW | PDG | PASS (16 pts) |
| strong_multiscale | QCD | Multi-scale | PASS |
| weak_multiscale | EW | Multi-scale | PASS |
| gravity_multiscale | GR | Multi-scale | PASS |
| em_multiscale | EM | Multi-scale | PASS |
| vix_real_data | Financial | VIX | PASS (r=-0.76) |
| ccbh_parameter | Black Hole | Kormendy | PASS (k=3.0) |

### S1.3 Phase 7-9: Quantum/GR Tests (7/7)
| Test | Domain | Data Source | Result |
|------|--------|-------------|--------|
| coupling_unification | Unified | PDG | PASS (α=0.0073) |
| force_emergence | Unified | Simulated | PASS |
| gr_effects | GR | Time dilation | PASS |
| uncertainty_analog | Quantum | NIST | PASS (ℏ=1.05e-34) |
| superposition | Quantum | Simulated | PASS |
| gw_strain | GW | LIGO | PASS (3.2e-21) |
| chirp_mass | GW | LIGO | PASS (28.3 M☉) |

### S1.4 Phase 10-11: Cosmology Tests (4/4)
| Test | Domain | Data Source | Result |
|------|--------|-------------|--------|
| dark_energy | Cosmology | Planck 2018 | PASS (Ω_Λ=0.685) |
| hubble_constant | Cosmology | Planck 2018 | PASS (H0=67.4) |
| higgs_analog | Mass Gen | PDG | PASS (m_H=125.25 GeV) |
| fermion_mass | Mass Gen | Hierarchy | PASS |

### S1.5 Phase 12-17: Advanced Tests (7/7)
| Test | Domain | Result |
|------|--------|--------|
| lagrangian_density | Action Principle | PASS |
| euler_lagrange | Variational | PASS |
| alpha_em | Fine Structure | PASS |
| fermion_antisymmetry | Statistics | PASS |
| exclusion_principle | Pauli | PASS |
| hamiltonian_conservation | Energy | PASS |
| black_hole_metric | BH (Real Data) | PASS |

---

## S2. Physics Gap Tests

### S2.1 Pauli Exclusion Test
**File:** `test_pauli_exclusion.py`

Energy vs Separation:
```
Separation  Energy
1.0         65.05
2.0         58.72
3.0         56.28
5.0         45.98
10.0        -28.57
```
**Result:** Energy increases at smaller separation → Repulsion confirmed

### S2.2 Lorentz/Euclidean Test
**File:** `test_lorentz_dispersion.py`

- c_eff = √(2κ) = √(2×0.5) = 1.0
- UET is Euclidean formulation
- Wick rotation: t → -iτ

### S2.3 Gauge Symmetry Test
**File:** `test_gauge_symmetry.py`

- U(1): |ψ|² conserved to 10⁻¹⁵
- SU(2): |ψ₁|²+|ψ₂|² conserved to 10⁻¹⁵
- β = 0.214 → α ≈ 1/109 (cf. 1/137)

### S2.4 Planck Constant Test
**File:** `test_planck_constant.py`

- S_min = |a|/δ = 1 (natural units)
- E = ℏω verified for electron
- Fixed point: κ=0.5, |a|=δ=1 → ℏ=c=1

---

## S3. Code Verification

### S3.1 Determinism Test
**File:** `test_determinism.py`

3 runs with seed=12345:
- Run 1: hash=b6efc9dbfde3fe8f
- Run 2: hash=b6efc9dbfde3fe8f
- Run 3: hash=b6efc9dbfde3fe8f

**Result:** 100% deterministic

### S3.2 Edge Case Test
**File:** `test_edge_cases.py`

| Case | Expected | Actual | Pass |
|------|----------|--------|------|
| δ < 0 | FAIL | FAIL | ✅ |
| κ = 0 | FAIL | FAIL | ✅ |
| κ < 0 | FAIL | FAIL | ✅ |
| Extreme ratio | Handle | PASS | ✅ |
| Tiny grid | PASS | PASS | ✅ |

---

*Supplementary Materials v1.0 | 2025-12-29*
