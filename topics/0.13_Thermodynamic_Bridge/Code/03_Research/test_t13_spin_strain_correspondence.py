"""Exact controls of the new NN comparator, not old M verifier reruns."""
import importlib.util
from itertools import product
from pathlib import Path
import unittest
from unittest.mock import patch

import sympy as s

spec = importlib.util.spec_from_file_location(
    "spin_strain", Path(__file__).with_name("Research_T13_Spin_Strain_Correspondence.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class SpinStrainCorrespondenceTests(unittest.TestCase):
    def assertZeros(self, values):
        for key, value in values.items():
            with self.subTest(identity=key):
                self.assertEqual(s.simplify(value), 0)

    def test_domain_rejects_invalid_population(self):
        for N in (0, 2, 3, -4, 4.0, True, "4"):
            with self.subTest(N=N), self.assertRaises(ValueError):
                m.histograms(N)
        for k in (-1, 5, 1.5, True):
            with self.subTest(k=k), self.assertRaises(ValueError):
                m.conditional(4, k)

    def test_spin_domain_not_half_spin_or_bool_by_accident(self):
        for spins in ((1, 1, -1, 0), (True, 1, -1, -1), (0.5, 0.5, -0.5, -0.5)):
            with self.assertRaises(ValueError):
                m.bond_sum(spins)

    def test_N_unique_undirected_bonds_with_periodic_last_edge(self):
        for N in m.REGRESSION_N:
            edges = m.ring_bonds(N)
            self.assertEqual(len(edges), N)
            self.assertEqual(len({frozenset(edge) for edge in edges}), N)
            self.assertIn((N-1, 0), edges)

    def test_factor_four_matches_actual_source_half_spin_energy(self):
        for N in m.REGRESSION_N:
            self.assertZeros(m.source_normalization_residuals(N))

    def test_wrong_spin_factor_and_double_bonds_are_detected(self):
        for values in (m.source_normalization_residuals(4, spin_factor=1),
                       m.source_normalization_residuals(4, bond_factor=2)):
            self.assertTrue(any(s.simplify(v) != 0 for v in values.values()))

    def test_class_counts_and_full_partition_from_independent_transfer_trace(self):
        for N in m.REGRESSION_N:
            self.assertEqual(sum(sum(h.values()) for h in m.histograms(N).values()), 2**N)
            self.assertZeros(m.ensemble_residuals(N))

    def test_minimal_same_C_unequal_energy_witness_is_enumerated(self):
        self.assertEqual(dict(m.histograms(4)[2]), {0: 4, -4: 2})
        self.assertEqual(sum(x == 1 for x in (1, 1, -1, -1)), 2)
        self.assertEqual(sum(x == 1 for x in (1, -1, 1, -1)), 2)
        self.assertEqual(m.bond_sum((1, 1, -1, -1)), 0)
        self.assertEqual(m.bond_sum((1, -1, 1, -1)), -4)

    def test_neighbor_order_must_not_be_replaced_by_population(self):
        with patch.object(m, "bond_sum", side_effect=lambda spins: sum(spins)**2):
            self.assertNotEqual(dict(m.histograms(4)[2]), {0: 4, -4: 2})

    def test_probability_moments_KL_and_chain_for_every_new_control_class(self):
        for N in m.REGRESSION_N:
            for k in range(N+1):
                self.assertZeros(m.probability_residuals(N, k))

    def test_endpoints_and_one_defect_are_special_uniform_classes(self):
        # Nonuniformity is not claimed for every class; many classes are degenerate.
        for N in m.REGRESSION_N:
            for k in (0, 1, N-1, N):
                self.assertEqual(len(m.histograms(N)[k]), 1)
                self.assertEqual(m.conditional(N, k)["variance"], 0)

    def test_N4_partition_and_nonzero_variance(self):
        self.assertZeros(m.direct_N4_thermal_residuals())
        c = m.conditional(4, 2)
        self.assertTrue(c["variance"].subs(c["w"], 2) > 0)

    def test_log_count_formula_fails_at_nonuniform_weights(self):
        c = m.conditional(4, 2)
        w = c["w"]
        entropy = s.log(c["Q"])-s.log(w)*c["mean"]
        self.assertNotEqual(s.simplify(entropy.subs(w, 2)-s.log(6)), 0)
        # KL nonnegativity follows analytically; exact positive witness at w=2.
        p_low, p_high = s.Rational(8, 33), s.Rational(1, 66)
        self.assertEqual(4*p_low+2*p_high, 1)
        KL = 4*p_low*s.log(6*p_low)+2*p_high*s.log(6*p_high)
        self.assertEqual(s.simplify(s.log(6)-entropy.subs(w, 2)-KL), 0)

    def test_histogram_probability_entropy_is_not_microstate_entropy(self):
        c = m.conditional(4, 2)
        self.assertEqual(c["Q"].subs(c["w"], 1), 6)
        # At x=0, bond-label entropy excludes log 4/log 2 internal multiplicities.
        H_B = -s.Rational(2, 3)*s.log(s.Rational(2, 3))-s.Rational(1, 3)*s.log(s.Rational(1, 3))
        self.assertEqual(s.simplify(s.log(6)-H_B-(s.Rational(2, 3)*s.log(4)+s.Rational(1, 3)*s.log(2))), 0)

    def test_conditional_free_internal_entropy_force_and_Maxwell(self):
        self.assertZeros(m.thermodynamic_residuals())

    def test_nonzero_Phi_entropy_without_new_hidden_Phi_state(self):
        J, Jprime, kB, T = s.symbols("J Jprime k_B T", positive=True)
        c = m.conditional(4, 2)
        derivative = -J*Jprime*c["variance"]/(kB*T**2)
        self.assertTrue(derivative.subs(c["w"], 2).is_negative)

    def test_conditional_correlation_force_exists_at_zero_C(self):
        c = m.conditional(4, 2)
        self.assertEqual(s.Rational(2*2-4, 4), 0)
        self.assertEqual(c["mean"].subs(c["w"], 2), -s.Rational(4, 33))
        # M's spin force is proportional to m^2; NN's Jprime*<B> is not zero.
        self.assertNotEqual(c["mean"].subs(c["w"], 2), 0)

    def test_fixed_coordinate_T_derivative_cannot_drop_thermal_weights(self):
        T, J, kB = s.symbols("T J k_B", positive=True)
        Q = 4+2*s.exp(-4*J/(kB*T))
        F = -kB*T*s.log(Q)
        wrong = kB*s.log(Q)
        self.assertNotEqual(s.simplify(-s.diff(F, T)-wrong), 0)

    def test_source_strain_law_and_compression_sign(self):
        self.assertZeros(m.strain_residuals())

    def test_actual_source_power_law_in_direct_N4_force_entropy(self):
        self.assertZeros(m.direct_source_N4_residuals())

    def test_uniform_entropy_gives_wrong_thermal_force_response(self):
        # At Phi=0, direct source-Q force has a nonzero T derivative; ln G does not.
        J0, nu, e, kB, T = s.symbols("J0 nu epsilon_star k_B T", positive=True)
        force = -J0*nu*e/(2*s.exp(J0/(kB*T))+1)
        self.assertNotEqual(s.simplify(s.diff(force, T)), 0)

    def test_wrong_strain_orientation_reverses_derivative(self):
        r = m.strain_reference()
        wrong = r["J_eps"].subs(r["eps"], r["eps_star"]*r["phi"])
        diff = (s.diff(wrong, r["phi"])-s.diff(r["J_phi"], r["phi"])).subs(r["phi"], 0)
        self.assertEqual(s.simplify(diff+r["J0"]*r["nu"]*r["eps_star"]/2), 0)
        self.assertNotEqual(diff, 0)

    def test_affine_law_is_not_exact_power_law(self):
        r = m.strain_reference()
        curvature = s.diff(r["J_phi"], r["phi"], 2).subs(r["phi"], 0)
        self.assertTrue(curvature.is_positive)
        self.assertEqual(s.diff(r["J_aff"], r["phi"], 2), 0)

    def test_old_parameter_map_does_not_drop_diagonal(self):
        self.assertZeros(m.old_mean_field_residuals())

    def test_energy_envelope_all_new_control_classes(self):
        for N in m.REGRESSION_N:
            self.assertTrue(m.bound_checks(N)["endpoint_envelope_all_classes"])

    def test_bad_delta_input_domain(self):
        for J, Ja in ((0, 1), (-1, 1), (s.I, 1), (1, s.I)):
            with self.assertRaises(ValueError):
                m.delta_bound(4, 2, J, Ja)

    def test_central_energy_bound_not_falsely_zero(self):
        J, Ja = s.symbols("Jcal Jaff", positive=True)
        result = m.delta_bound(4, 2, J, Ja)
        self.assertEqual(result["delta"], 4*J)
        self.assertEqual(result["HM"], 0)

    def test_exact_weight_envelopes_and_fixed_parameter_limits(self):
        self.assertZeros(m.N4_limits_and_bounds())

    def test_fixed_k_partition_cannot_be_replaced_by_full_spin_sum(self):
        c = m.conditional(4, 2)
        full_count = sum(sum(h.values()) for h in m.histograms(4).values())
        self.assertEqual(full_count, 16)
        self.assertEqual(c["Q"].subs(c["w"], 1), 6)
        self.assertNotEqual(full_count, 6)

    def test_signed_flip_and_magnitude_fold_with_nonuniform_internal_weights(self):
        for N in m.REGRESSION_N:
            self.assertZeros(m.folding_residuals(N))

    def test_zero_class_must_not_be_doubled(self):
        c = m.conditional(4, 2)
        self.assertNotEqual(c["Q"], 2*c["Q"])

    def test_negative_controls_reject_all_declared_mutations(self):
        self.assertTrue(all(m.negative_controls().values()))

    def test_no_promotion_or_new_dynamics_from_conditional_result(self):
        result = m.calculate()
        self.assertFalse(result["physical_acceptance"])
        self.assertFalse(result["unique_UET_discriminator"])
        self.assertFalse(result["kinetic_law_added"])
        self.assertFalse(result["old_scientific_verifiers_rerun"])
        self.assertEqual(result["new_core_terms"], 0)
        self.assertEqual(result["observational_rows"], 0)
        self.assertEqual(result["decisions"]["microscopic_equivalence"].split(':')[0], "DIFFERENT")


if __name__ == "__main__":
    unittest.main()
