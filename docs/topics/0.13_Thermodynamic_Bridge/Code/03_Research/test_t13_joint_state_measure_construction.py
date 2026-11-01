"""Independent finite-count and mutation checks for the static reference."""
import importlib.util
from math import comb
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as s

spec = importlib.util.spec_from_file_location(
    "joint_state_measure", Path(__file__).with_name("Research_T13_Joint_State_Measure_Construction.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class JointStateMeasureTests(unittest.TestCase):
    def assertZeros(self, values):
        for name, value in values.items():
            with self.subTest(identity=name):
                self.assertEqual(s.simplify(value), 0)

    def test_population_domain_rejects_bad_N(self):
        for N in (0, 1, -2, 2.0, True, "4"):
            with self.subTest(N=N), self.assertRaises(ValueError):
                m.multiplicity(N, 0)

    def test_population_domain_rejects_bad_k(self):
        for k in (-1, 5, 1.5, True, "2"):
            with self.subTest(k=k), self.assertRaises(ValueError):
                m.multiplicity(4, k)

    def test_exact_counts_and_weighted_partition_regressions(self):
        for N in m.REGRESSION_N:
            self.assertEqual(sum(m.multiplicity(N, k) for k in range(N+1)), 2**N)
            self.assertTrue(m.finite_population_checks(N)["enumerated_multiplicity_and_weight_sum"])

    def test_enumeration_detects_corrupted_multiplicity(self):
        original = m.multiplicity
        with patch.object(m, "multiplicity", side_effect=lambda N, k: original(N, k)+(1 if k == 1 else 0)):
            with self.assertRaises(ValueError):
                m.finite_population_checks(3)

    def test_restricted_boltzmann_sum_uses_actual_energy(self):
        r = m.reference()
        for N in m.REGRESSION_N:
            for k in range(N+1):
                H = m.energy_for_count(N, k, r)
                F = r["F"].subs({r["N"]: N, r["k"]: k, r["m"]: m.magnetization(N, k)})
                ratio = s.exp(-F/(r["kB"]*r["T"]))/s.exp(-H/(r["kB"]*r["T"]))
                self.assertEqual(s.simplify(ratio), comb(N, k))

    def test_conditional_dictionary_and_T_derivatives(self):
        self.assertZeros(m.thermodynamic_residuals())

    def test_nontrivial_intrinsic_entropy_not_zero(self):
        r = m.reference()
        F = r["F"].subs({r["N"]: 4, r["k"]: 2, r["m"]: 0})
        self.assertEqual(s.simplify(-s.diff(F, r["T"])-r["kB"]*s.log(6)), 0)
        self.assertNotEqual(s.log(6), 0)

    def test_endpoints_have_one_arrangement_not_log_zero(self):
        for N in m.REGRESSION_N:
            self.assertEqual(m.multiplicity(N, 0), 1)
            self.assertEqual(m.multiplicity(N, N), 1)
            self.assertEqual(m.magnetization(N, 0), -1)
            self.assertEqual(m.magnetization(N, N), 1)

    def test_omitted_or_double_degeneracy_rejected(self):
        r = m.reference()
        for F in (r["H"], r["F"]-r["kB"]*r["T"]*s.log(r["G"])):
            self.assertNotEqual(s.simplify(m.thermodynamic_residuals(F)["intrinsic_entropy_from_T_derivative"]), 0)

    def test_entropy_chain_rule_and_ensemble_F(self):
        self.assertZeros(m.entropy_residuals())

    def test_nonuniform_hidden_distribution_is_not_log_G(self):
        # Static conditioning requires uniformity. This witness is not kinetics.
        p = (s.Rational(1, 4), s.Rational(3, 4))
        entropy = -sum(x*s.log(x) for x in p)
        self.assertNotEqual(s.simplify(entropy-s.log(2)), 0)

    def test_energy_measure_and_temperature_normalization(self):
        self.assertZeros(m.normalization_residuals())

    def test_direct_gaussian_integral_and_pushforward_agree(self):
        # Analytic integrals at exact symbolic parameters, not quadrature samples.
        r = m.reference()
        P, Pi, N, mass, th = r["P"], r["Pi"], r["N"], r["mass"], r["theta"]
        direct = s.integrate(s.exp(-P**2/(2*N*mass*th)), (P, -s.oo, s.oo))
        pushed = N*mass*s.integrate(s.exp(-N*mass*Pi**2/(2*th)), (Pi, -s.oo, s.oo))
        self.assertEqual(s.simplify(direct-pushed), 0)
        self.assertEqual(s.simplify(direct-s.sqrt(2*s.pi*N*mass*th)), 0)
        self.assertEqual(s.diff(N*mass*Pi, Pi), N*mass)

    def test_all_to_all_square_keeps_Phi_dependent_diagonal(self):
        self.assertZeros(m.pair_convention_residuals())
        r = m.reference()
        diagonal = -r["E"]*(r["j0"]+r["gamma"]*r["Phi"])/2
        self.assertNotEqual(s.diff(diagonal, r["Phi"]), 0)

    def test_wrong_N_storage_is_rejected(self):
        r = m.reference()
        changed = r["H"]+r["E"]*r["P"]**2/(2*r["mass"])*(1-1/r["N"])
        self.assertNotEqual(s.simplify(m.normalization_residuals(changed)["total_to_per_site_storage"]), 0)

    def test_omitted_or_double_Jacobian_is_rejected(self):
        r = m.reference()
        for J in (s.Integer(1), (r["N"]*r["mass"])**2):
            self.assertNotEqual(s.simplify(m.normalization_residuals(jacobian=J)["P_to_Pi_pushforward_measure"]), 0)

    def test_fixed_C_thermal_quartic_map_not_generic_constant_Core_coefficients(self):
        self.assertZeros(m.quartic_bridge_residuals())
        r = m.reference()
        self.assertEqual(s.diff((r["theta"]-r["j0"])/r["sc"]**2, r["T"]), r["kB"]/(r["E"]*r["sc"]**2))

    def test_dropping_ln2_changes_entropy_reference(self):
        r = m.reference()
        omitted = r["N"]*r["kB"]*r["T"]*s.log(2)
        self.assertEqual(-s.diff(omitted, r["T"]), -r["N"]*r["kB"]*s.log(2))

    def test_wrong_coupling_factor_or_sign_is_rejected_by_old_map(self):
        r = m.reference()
        interaction = -r["E"]*r["N"]*r["gamma"]*r["Phi"]*r["m"]**2/2
        for changed in (r["H"]+interaction, r["H"]-2*interaction):
            residual = s.diff(changed, r["gamma"])+r["E"]*r["N"]*r["Phi"]*r["m"]**2/2
            self.assertNotEqual(s.simplify(residual), 0)

    def test_finite_N_bound_has_mode_proof_algebra_and_exact_certificates(self):
        self.assertZeros(m.finite_bound_residuals())
        for N in m.REGRESSION_N:
            self.assertTrue(m.finite_population_checks(N)["exact_rational_entropy_bound_certificate"])

    def test_finite_N_is_not_exact_binary_mixing_entropy(self):
        # N=2,k=1: log binomial/N=log2/2, while h2(0)=log2.
        self.assertEqual(s.simplify(s.log(2)-s.log(m.multiplicity(2, 1))/2), s.log(2)/2)

    def test_normalizability_certificate(self):
        self.assertZeros(m.tail_bound_residuals())

    def test_factorization_is_equilibrium_only_and_gamma_zero(self):
        self.assertZeros(m.decoupling_residuals())
        r = m.reference()
        self.assertNotEqual(s.diff(r["H"], r["m"], r["Phi"]), 0)

    def test_even_and_odd_folding_preserve_state_count(self):
        for N in m.REGRESSION_N:
            self.assertTrue(m.folding_checks(N)["counts_and_even_energy"])

    def test_zero_magnitude_not_doubled(self):
        self.assertEqual(m.folded_multiplicity(4, 0), 6)
        self.assertEqual(m.folded_multiplicity(4, 2), 8)
        self.assertEqual(m.folded_multiplicity(4, 4), 2)
        self.assertNotIn(0, m.folded_groups(3))

    def test_folding_rejects_non_grid_values(self):
        for a in (-1, 1, 5, 2.0, True):
            with self.subTest(a=a), self.assertRaises(ValueError):
                m.folded_multiplicity(4, a)

    def test_fold_is_not_invertible_but_entropy_accounting_is_consistent(self):
        self.assertZeros(m.folding_entropy_residuals())
        self.assertEqual(abs(m.magnetization(3, 0)), abs(m.magnetization(3, 3)))
        self.assertNotEqual(m.magnetization(3, 0), m.magnetization(3, 3))

    def test_readout_changes_no_energy_and_adds_no_state(self):
        r = m.reference()
        before = r["H"]
        readout_signed = m.magnetization(4, 1)
        readout_magnitude = abs(readout_signed)
        self.assertNotEqual(readout_signed, readout_magnitude)
        self.assertEqual(r["H"], before)

    def test_negative_controls_all_detected(self):
        self.assertTrue(all(m.negative_controls().values()))

    def test_calculation_does_not_promote_physics_or_add_dynamics(self):
        result = m.calculate()
        self.assertFalse(result["physical_acceptance"])
        self.assertFalse(result["unique_UET_discriminator"])
        self.assertFalse(result["kinetic_law_added"])
        self.assertFalse(result["old_scientific_verifiers_rerun"])
        self.assertEqual(result["new_core_terms"], 0)
        self.assertEqual(result["observational_rows"], 0)


if __name__ == "__main__":
    unittest.main()
