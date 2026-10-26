"""Regression controls for the conditional reference, not empirical UET tests."""
import importlib.util
from pathlib import Path
import unittest

import sympy as s

spec = importlib.util.spec_from_file_location(
    "joint_thermodynamic_completion", Path(__file__).with_name("Research_T13_Joint_Thermodynamic_Completion.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class JointThermodynamicCompletionTests(unittest.TestCase):
    def assertZeros(self, values):
        for name, value in values.items():
            with self.subTest(identity=name):
                self.assertEqual(s.simplify(value), 0)

    def test_actual_core_homogeneous_expressions_match(self):
        self.assertZeros(m.core_projection_residuals())

    def test_core_source_mutation_is_detected(self):
        text = (m.ROOT/m.CORE).read_text(encoding="utf-8-sig")
        changed = text.replace("dPhi = state.space_rate.copy()", "dPhi = 2 * state.space_rate.copy()")
        self.assertNotEqual(changed, text)
        self.assertNotEqual(m.core_projection_residuals(changed)["dPhi"], 0)

    def test_actual_core_returns_are_bound_not_only_local_formulas(self):
        text = (m.ROOT/m.CORE).read_text(encoding="utf-8-sig")
        changed = text.replace("return float(matter_space_free_energy(state, dx, config) + kinetic)",
                               "return float(2 * matter_space_free_energy(state, dx, config) + kinetic)")
        self.assertNotEqual(changed, text)
        self.assertNotEqual(m.core_projection_residuals(changed)["energy"], 0)
        changed = text.replace("return dC, dPhi, dPi, mu_matter, mu_space",
                               "return dC, dPi, dPhi, mu_matter, mu_space")
        self.assertNotEqual(m.core_projection_residuals(changed)["dPhi"], 0)

    def test_first_law_ito_and_stratonovich_agree(self):
        self.assertZeros(m.first_law_residuals())

    def test_wrong_heat_sign_fails_in_drift_and_noise(self):
        result = m.first_law_residuals(heat_sign=-1)
        self.assertNotEqual(s.simplify(result["work_minus_heat_dt"]), 0)
        self.assertNotEqual(s.simplify(result["work_minus_heat_C_noise"]), 0)
        self.assertNotEqual(s.simplify(result["work_minus_heat_Pi_noise"]), 0)

    def test_no_independent_phi_noise_and_no_spurious_sde_drift(self):
        r = m.reference()
        for i, _ in enumerate(r["state"]):
            conversion = sum(r["noise"][k, j]*s.diff(r["noise"][i, j], x)
                             for k, x in enumerate(r["state"]) for j in range(2))/2
            self.assertEqual(conversion, 0)
        self.assertEqual(r["noise"][1, :], s.zeros(1, 2))

    def test_deterministic_limit_holds_coefficients_fixed(self):
        r = m.reference()
        eps = s.Symbol("epsilon", nonnegative=True)
        self.assertEqual((eps*r["noise"]).subs(eps, 0), s.zeros(3, 2))
        for x, drift in zip(r["state"], r["drift"]):
            self.assertEqual(s.simplify(m.generator(x, r)-drift), 0)

    def test_same_free_energy_at_one_bath_does_not_fix_heat(self):
        self.assertZeros(m.coarse_free_energy_residuals())
        r = m.reference()
        kappa = s.Symbol("kappa", positive=True)
        correction = 2*r["theta"]*kappa*r["Phi"]*r["Pi"]
        self.assertNotEqual(correction, 0)

    def test_source_ledger_is_not_force_port_work(self):
        r = m.reference()
        ledger = r["muC"]*r["JC"]+r["Pi"]*r["JP"]/r["MP"]
        port = r["JC"]/r["MC"]*r["drift"][0]+r["JP"]/r["MP"]*r["Pi"]
        self.assertEqual(s.simplify(ledger-port-(2*r["muC"]*r["JC"]-r["JC"]**2/r["MC"])), 0)
        self.assertNotEqual(s.simplify(ledger-port), 0)

    def test_gibbs_stationarity_exact_and_sources_off(self):
        self.assertEqual(m.stationary_residual(), 0)

    def test_each_wrong_noise_coefficient_fails_locked_gibbs(self):
        self.assertNotEqual(m.stationary_residual(c_noise_scale=2), 0)
        self.assertNotEqual(m.stationary_residual(pi_noise_scale=2), 0)
        self.assertNotEqual(m.stationary_residual(c_noise_scale=0), 0)
        self.assertNotEqual(m.stationary_residual(pi_noise_scale=0), 0)

    def test_odd_pi_parity_and_reversible_volume_flow(self):
        self.assertZeros(m.parity_residuals())
        self.assertZeros(m.equilibrium_current_residuals())
        r = m.reference()
        rev, _ = m.parity_split(r)
        self.assertEqual(rev[1], r["Pi"])
        self.assertNotEqual(rev[1], 0)  # Gibbs can have reversible phase-space current.

    def test_even_pi_parity_wrongly_makes_undiffused_phi_irreversible(self):
        r = m.reference()
        _, irr = m.parity_split(r, pi_parity=1)
        self.assertEqual(irr[1], r["Pi"])
        self.assertNotEqual(m.parity_residuals(pi_parity=1)["irreversible_1"], 0)
        with self.assertRaises(ValueError):
            m.parity_split(r, pi_parity=0)

    def test_coercive_quartic_bound_is_exact(self):
        self.assertZeros(m.coercivity_residuals())

    def test_entropy_and_heat_current_accounts_match(self):
        self.assertZeros(m.entropy_residuals())

    def test_gibbs_friction_positive_while_irreversible_currents_zero(self):
        r = m.reference()
        variance = m.gaussian_pi_variance()
        self.assertEqual(s.simplify(variance-r["MP"]*r["theta"]/r["tau"]), 0)
        self.assertTrue((variance/r["MP"]).is_positive)
        self.assertZeros(m.equilibrium_current_residuals())

    def test_generator_splits_without_mixed_quadratic_variation(self):
        self.assertZeros(m.generator_partition_residuals())

    def test_continuous_entropy_chain_rule_and_partial_balances(self):
        self.assertZeros(m.information_residuals())

    def test_zero_coupling_gibbs_factorizes(self):
        r = m.reference()
        self.assertZeros(m.gibbs_dependence_residuals())
        self.assertEqual(s.diff(-r["energy"]/r["theta"], r["C"], r["Phi"]).subs(r["g"], 0), 0)

    def test_zero_covariance_does_not_imply_gibbs_independence(self):
        r = m.reference()
        self.assertEqual(s.simplify(r["energy"].subs(r["C"], -r["C"])-r["energy"]), 0)
        witness = s.diff(-r["energy"]/r["theta"], r["C"], r["Phi"])
        self.assertNotEqual(witness, 0)  # A symbolic nonzero function for g != 0.
        self.assertEqual(s.simplify(witness-r["g"]*r["C"]/r["theta"]), 0)

    def test_underdamped_standard_comparator_is_exact(self):
        self.assertZeros(m.comparator_residuals())

    def test_per_site_temperature_scale_contains_N(self):
        self.assertZeros(m.normalization_residuals())

    def test_information_is_not_an_added_state_or_observation(self):
        result = m.calculate()
        self.assertEqual(result["completed_rounds"], ["R0", "R1", "R2", "R3"])
        self.assertEqual(len(m.reference()["state"]), 3)
        self.assertEqual(result["method"]["samples"], 0)
        self.assertFalse(result["unique_UET_discriminator"])

    def test_no_physics_promotion_from_symbolic_checks(self):
        result = m.calculate()
        self.assertFalse(result["physical_acceptance"])
        self.assertFalse(result["unique_UET_discriminator"])
        self.assertEqual(result["new_core_terms"], 0)
        self.assertEqual(result["observational_rows"], 0)


if __name__ == "__main__":
    unittest.main()
